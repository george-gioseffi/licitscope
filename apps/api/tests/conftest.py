"""Shared pytest fixtures for the LicitScope backend tests.

Each test runs against a fresh in-memory SQLite database to keep tests
hermetic. We inject the engine through the SQLModel metadata so no real
database is touched.
"""

from __future__ import annotations

import json
import os
from collections.abc import Iterator
from pathlib import Path

import pytest
from fastapi.testclient import TestClient
from sqlalchemy.pool import StaticPool
from sqlmodel import Session, SQLModel, create_engine

os.environ.setdefault("DATABASE_URL", "sqlite:///:memory:")
os.environ.setdefault("INGESTION_USE_FIXTURES", "true")

from app.core.config import get_settings
from app.db import session as db_session_module
from app.enrichment.pipeline import EnrichmentPipeline
from app.main import app as fastapi_app
from app.models import Agency, Opportunity, Supplier  # noqa: F401 ensures metadata loaded
from app.models.enums import SourceName
from app.repositories.agencies import AgencyRepository
from app.repositories.opportunities import OpportunityRepository
from app.repositories.suppliers import SupplierRepository
from app.utils.dates import parse_date

_DATE_FIELDS = {
    "published_at",
    "proposals_open_at",
    "proposals_close_at",
    "session_at",
    "awarded_at",
    "signed_at",
    "start_at",
    "end_at",
}


def _coerce_dates(payload: dict) -> dict:
    for key in list(payload.keys()):
        if key in _DATE_FIELDS and isinstance(payload[key], str):
            payload[key] = parse_date(payload[key])
    return payload


@pytest.fixture()
def engine():
    engine = create_engine(
        "sqlite://",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    SQLModel.metadata.create_all(engine)
    # Override the app-level engine so get_session picks this one up.
    db_session_module._engine = engine
    try:
        yield engine
    finally:
        db_session_module._engine = None
        SQLModel.metadata.drop_all(engine)


@pytest.fixture()
def session(engine) -> Iterator[Session]:
    with Session(engine) as session:
        yield session


@pytest.fixture()
def client(engine) -> Iterator[TestClient]:
    with TestClient(fastapi_app) as c:
        yield c


@pytest.fixture()
def settings():
    get_settings.cache_clear()
    return get_settings()


@pytest.fixture()
def repo_root() -> Path:
    return Path(__file__).resolve().parents[3]


@pytest.fixture()
def seeded(session, repo_root: Path):
    """Seed the in-memory DB with a slice of the bundled fixtures + enrichment.

    Loads a small but representative subset so API tests can exercise the
    real filter / facet / similarity pipeline without waiting on the full
    85-opportunity seed.
    """
    base = repo_root / "data-demo"
    agencies = json.loads((base / "agencies.json").read_text(encoding="utf-8"))
    suppliers = json.loads((base / "suppliers.json").read_text(encoding="utf-8"))
    opportunities = json.loads((base / "opportunities.json").read_text(encoding="utf-8"))

    a_repo = AgencyRepository(session)
    s_repo = SupplierRepository(session)
    o_repo = OpportunityRepository(session)

    for p in agencies:
        a_repo.upsert(p)
    for p in suppliers:
        s_repo.upsert(p)
    for p in opportunities[:30]:  # 30 is enough to test facets + search
        p = dict(p)
        cnpj = p.pop("agency_cnpj", None)
        items = p.pop("items", [])
        if cnpj:
            ag = a_repo.get_by_cnpj(cnpj)
            if ag:
                p["agency_id"] = ag.id
        p.setdefault("source", SourceName.FIXTURE.value)
        _coerce_dates(p)
        o_repo.upsert(p, items=items)
    session.commit()

    EnrichmentPipeline(session).enrich_all()
    session.commit()
    return True
