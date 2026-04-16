"""Liveness, readiness, and source-health endpoints."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends
from sqlalchemy import text
from sqlmodel import Session

from app import __version__
from app.core.config import get_settings
from app.db.session import get_session
from app.schemas.common import HealthStatus
from app.services.ingestion import IngestionService

router = APIRouter(prefix="/health", tags=["health"])


@router.get("/live", summary="Liveness probe")
def live() -> dict:
    return {"status": "ok"}


@router.get("/ready", response_model=HealthStatus, summary="Readiness probe")
def ready(session: Session = Depends(get_session)) -> HealthStatus:
    settings = get_settings()
    db_status = "ok"
    try:
        session.exec(text("SELECT 1"))  # type: ignore[arg-type]
    except Exception as exc:  # pragma: no cover
        db_status = f"error: {exc}"
    return HealthStatus(
        status="ok" if db_status == "ok" else "degraded",
        app=settings.app_name,
        version=__version__,
        env=settings.app_env,
        database=db_status,
        now=datetime.now(UTC).isoformat(),
    )


@router.get("/sources", summary="Source freshness + recent ingestion runs")
def sources(session: Session = Depends(get_session)) -> dict:
    svc = IngestionService(session)
    runs = svc.recent_runs(limit=25)
    by_source: dict[str, dict] = {}
    for r in runs:
        src = r["source"]
        if src not in by_source:
            by_source[src] = {"source": src, "runs": [], "last_success": None}
        by_source[src]["runs"].append(r)
        if r["status"] == "success" and by_source[src]["last_success"] is None:
            by_source[src]["last_success"] = r["finished_at"] or r["started_at"]
    return {"sources": list(by_source.values())}
