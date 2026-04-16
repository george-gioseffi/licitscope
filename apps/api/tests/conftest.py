"""Shared pytest fixtures for the LicitScope backend tests.

Each test runs against a fresh in-memory SQLite database to keep tests
hermetic. We inject the engine through the SQLModel metadata so no real
database is touched.
"""

from __future__ import annotations

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
from app.main import app as fastapi_app
from app.models import Agency, Opportunity, Supplier  # noqa: F401 ensures metadata loaded


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
