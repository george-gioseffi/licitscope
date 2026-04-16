"""Dashboard analytics endpoints."""

from __future__ import annotations

from fastapi import APIRouter, Depends
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.opportunity import DashboardOverview
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/analytics", tags=["analytics"])


@router.get("/overview", response_model=DashboardOverview)
def overview(session: Session = Depends(get_session)) -> DashboardOverview:
    return AnalyticsService(session).dashboard_overview()
