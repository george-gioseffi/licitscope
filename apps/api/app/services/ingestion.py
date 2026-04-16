"""Ingestion orchestrator.

Given a source (default: PNCP) and a date range, this service:
  * starts an ``IngestionRun`` record
  * streams payloads from the source client (or fixtures)
  * saves raw payloads idempotently
  * upserts Agencies + Opportunities via their repositories
  * marks the run with success / partial / failed status
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from sqlmodel import Session

from app.clients.pncp import PNCPClient
from app.clients.pncp_parser import parse_full
from app.core.config import get_settings
from app.models.enums import IngestionStatus, SourceName
from app.models.ingestion import IngestionRun
from app.repositories.agencies import AgencyRepository
from app.repositories.ingestion import IngestionRepository
from app.repositories.opportunities import OpportunityRepository

logger = logging.getLogger(__name__)


class IngestionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.agencies = AgencyRepository(session)
        self.opportunities = OpportunityRepository(session)
        self.runs = IngestionRepository(session)

    # ---- public entrypoints -------------------------------------------------
    def ingest_pncp_window(
        self,
        *,
        days_back: int = 3,
        modalities: list[int] | None = None,
        use_fixtures: bool | None = None,
    ) -> IngestionRun:
        settings = get_settings()
        if use_fixtures is None:
            use_fixtures = settings.ingestion_use_fixtures

        params = {
            "days_back": days_back,
            "modalities": modalities,
            "use_fixtures": use_fixtures,
        }
        run = self.runs.start_run(source=SourceName.PNCP.value, scope="opportunities", params=params)
        try:
            if use_fixtures:
                payloads = self._load_fixtures()
            else:
                payloads = list(self._fetch_from_pncp(days_back=days_back, modalities=modalities))
            self._process_payloads(run, payloads)
            self.runs.finish_run(run, status=IngestionStatus.SUCCESS.value)
        except httpx.HTTPError as exc:
            logger.exception("PNCP ingestion HTTP failure, falling back to fixtures")
            try:
                fallback = self._load_fixtures()
                self._process_payloads(run, fallback)
                self.runs.finish_run(
                    run,
                    status=IngestionStatus.PARTIAL.value,
                    notes=f"fallback to fixtures: {exc}",
                )
            except Exception as inner:  # pragma: no cover
                self.runs.finish_run(run, status=IngestionStatus.FAILED.value, notes=str(inner))
                raise
        except Exception as exc:
            self.runs.finish_run(run, status=IngestionStatus.FAILED.value, notes=str(exc))
            raise
        self.session.commit()
        return run

    # ---- fetch paths --------------------------------------------------------
    def _fetch_from_pncp(
        self,
        *,
        days_back: int,
        modalities: list[int] | None,
    ) -> list[dict]:
        end = datetime.now(UTC).date()
        start = end - timedelta(days=max(1, days_back))
        d_i, d_f = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
        settings = get_settings()

        collected: list[dict] = []
        modalities = modalities or [1, 9]  # pregão eletrônico + dispensa by default
        with PNCPClient() as client:
            for code in modalities:
                for rec in client.list_published_notices(
                    data_inicial=d_i,
                    data_final=d_f,
                    codigo_modalidade=code,
                    page_size=settings.ingestion_page_size,
                    max_pages=settings.ingestion_max_pages,
                ):
                    collected.append(rec)
        logger.info("PNCP fetch returned %d records", len(collected))
        return collected

    def _load_fixtures(self) -> list[dict]:
        settings = get_settings()
        fixtures_dir = settings.data_demo_dir
        candidates = [
            fixtures_dir / "pncp" / "opportunities.json",
            Path(__file__).resolve().parents[3] / "data-demo" / "pncp" / "opportunities.json",
        ]
        for path in candidates:
            if path.exists():
                logger.info("Loading PNCP fixtures from %s", path)
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, list) else data.get("records", [])
        logger.warning("No PNCP fixtures found in %s", candidates)
        return []

    # ---- processing ---------------------------------------------------------
    def _process_payloads(self, run: IngestionRun, payloads: list[dict]) -> None:
        for raw in payloads:
            run.fetched += 1
            try:
                agency_p, opp_p, items_p = parse_full(raw)

                # Ensure we have an agency first.
                agency = self.agencies.upsert(agency_p) if agency_p.get("cnpj") != "UNKNOWN" else None
                if agency:
                    opp_p["agency_id"] = agency.id

                existing = self.opportunities.get_by_source(opp_p["source"], opp_p["source_id"])
                self.opportunities.upsert(opp_p, items=items_p)
                if existing:
                    run.updated += 1
                else:
                    run.created += 1

                # Save raw payload
                self.runs.save_payload(
                    source=SourceName.PNCP.value,
                    kind="opportunity",
                    source_id=opp_p["source_id"],
                    payload=raw,
                    run=run,
                )
            except Exception as exc:  # pragma: no cover
                logger.exception("Failed to process payload: %s", exc)
                run.failed += 1

        self.session.add(run)
        self.session.flush()

    # ---- helpers ------------------------------------------------------------
    def recent_runs(self, limit: int = 25) -> list[dict[str, Any]]:
        runs = self.runs.list_runs(limit=limit)
        return [
            {
                "id": r.id,
                "source": r.source,
                "scope": r.scope,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "fetched": r.fetched,
                "created": r.created,
                "updated": r.updated,
                "failed": r.failed,
                "notes": r.notes,
            }
            for r in runs
        ]
