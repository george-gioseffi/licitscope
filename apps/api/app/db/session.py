"""Database engine + session management.

Supports both SQLite (local dev / tests) and PostgreSQL (Docker / prod).
We use SQLModel's metadata so the same models can be reflected either way.
"""

from __future__ import annotations

from collections.abc import Iterator
from contextlib import contextmanager

from sqlalchemy.engine import Engine
from sqlmodel import Session, SQLModel, create_engine

from app.core.config import get_settings

_engine: Engine | None = None


def get_engine() -> Engine:
    global _engine
    if _engine is not None:
        return _engine

    settings = get_settings()
    connect_args: dict = {}
    if settings.is_sqlite:
        connect_args["check_same_thread"] = False

    _engine = create_engine(
        settings.database_url,
        echo=False,
        pool_pre_ping=True,
        connect_args=connect_args,
    )
    return _engine


def init_db() -> None:
    """Create all tables. Safe to call at app startup; idempotent."""
    # Ensure all models are imported so metadata is complete before create_all.
    from app import models  # noqa: F401

    engine = get_engine()
    SQLModel.metadata.create_all(engine)


@contextmanager
def session_scope() -> Iterator[Session]:
    """Context-managed session for scripts/workers."""
    engine = get_engine()
    with Session(engine) as session:
        try:
            yield session
            session.commit()
        except Exception:
            session.rollback()
            raise


def get_session() -> Iterator[Session]:
    """FastAPI dependency: yields a request-scoped session."""
    engine = get_engine()
    with Session(engine) as session:
        yield session
