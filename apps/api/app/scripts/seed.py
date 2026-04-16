"""Load bundled demo fixtures into the configured database.

Usage:
    python -m app.scripts.seed [--if-empty]

``--if-empty`` makes the seeder a no-op when the opportunities table already
has rows. This is what the Docker entrypoint uses so a restart never wipes
or re-imports the demo.
"""

from __future__ import annotations

import argparse
import json
import logging
import sys
from pathlib import Path

from sqlmodel import select

from app.core.config import get_settings
from app.core.logging import configure_logging
from app.db.session import init_db, session_scope
from app.enrichment.pipeline import EnrichmentPipeline
from app.models.enums import SourceName
from app.models.opportunity import Opportunity
from app.repositories.agencies import AgencyRepository
from app.repositories.contracts import ContractRepository
from app.repositories.opportunities import OpportunityRepository
from app.repositories.suppliers import SupplierRepository
from app.utils.dates import parse_date

logger = logging.getLogger("seed")

_DATE_FIELDS = {
    "published_at", "proposals_open_at", "proposals_close_at",
    "session_at", "awarded_at", "signed_at", "start_at", "end_at",
}


def _coerce_dates(payload: dict) -> dict:
    """Convert any ISO-string date fields in a fixture payload into datetimes."""
    for key in list(payload.keys()):
        if key in _DATE_FIELDS and isinstance(payload[key], str):
            payload[key] = parse_date(payload[key])
    return payload


def _load_json(path: Path) -> list[dict]:
    if not path.exists():
        logger.warning("fixture file missing: %s", path)
        return []
    with path.open("r", encoding="utf-8") as f:
        data = json.load(f)
    return data if isinstance(data, list) else data.get("records", [])


def _seed(if_empty: bool) -> None:
    settings = get_settings()
    init_db()

    with session_scope() as session:
        if if_empty:
            count = session.exec(select(Opportunity).limit(1)).first()
            if count is not None:
                logger.info("seed skipped: opportunities table already populated")
                return

        base = settings.data_demo_dir
        agencies_data = _load_json(base / "agencies.json")
        suppliers_data = _load_json(base / "suppliers.json")
        opps_data = _load_json(base / "opportunities.json")
        contracts_data = _load_json(base / "contracts.json")

        agency_repo = AgencyRepository(session)
        supplier_repo = SupplierRepository(session)
        opp_repo = OpportunityRepository(session)
        contract_repo = ContractRepository(session)

        for payload in agencies_data:
            agency_repo.upsert(payload)
        logger.info("seeded %d agencies", len(agencies_data))

        for payload in suppliers_data:
            supplier_repo.upsert(payload)
        logger.info("seeded %d suppliers", len(suppliers_data))

        for payload in opps_data:
            agency_cnpj = payload.pop("agency_cnpj", None)
            items = payload.pop("items", [])
            if agency_cnpj:
                agency = agency_repo.get_by_cnpj(agency_cnpj)
                if agency:
                    payload["agency_id"] = agency.id
            payload.setdefault("source", SourceName.FIXTURE.value)
            _coerce_dates(payload)
            opp_repo.upsert(payload, items=items)
        logger.info("seeded %d opportunities", len(opps_data))

        for payload in contracts_data:
            agency_cnpj = payload.pop("agency_cnpj", None)
            supplier_tax = payload.pop("supplier_tax_id", None)
            opp_source_id = payload.pop("opportunity_source_id", None)
            items = payload.pop("items", [])
            if agency_cnpj and (a := agency_repo.get_by_cnpj(agency_cnpj)):
                payload["agency_id"] = a.id
            if supplier_tax and (s := supplier_repo.get_by_tax_id(supplier_tax)):
                payload["supplier_id"] = s.id
            if opp_source_id and (o := opp_repo.get_by_source(payload.get("source", "fixture"), opp_source_id)):
                payload["opportunity_id"] = o.id
            _coerce_dates(payload)
            contract_repo.upsert(payload, items=items)
        logger.info("seeded %d contracts", len(contracts_data))

        session.commit()

        # Run enrichment over the freshly seeded data.
        with session_scope() as enrich_session:
            pipeline = EnrichmentPipeline(enrich_session)
            n = pipeline.enrich_all()
            logger.info("enriched %d opportunities", n)


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    parser = argparse.ArgumentParser(description="Seed LicitScope with demo fixtures.")
    parser.add_argument("--if-empty", action="store_true", help="Skip if DB already has data")
    args = parser.parse_args(argv)
    _seed(if_empty=args.if_empty)
    return 0


if __name__ == "__main__":
    sys.exit(main())
