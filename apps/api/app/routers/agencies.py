"""Agency routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_session
from app.repositories.agencies import AgencyRepository
from app.schemas.agency import AgencyOut, AgencyProfile
from app.schemas.common import Page, PageMeta
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/agencies", tags=["agencies"])


@router.get("", response_model=Page[AgencyOut])
def list_agencies(
    q: str | None = None,
    state: str | None = None,
    sphere: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session),
) -> Page[AgencyOut]:
    repo = AgencyRepository(session)
    offset = (page - 1) * page_size
    items, total = repo.list(q=q, state=state, sphere=sphere, limit=page_size, offset=offset)
    return Page[AgencyOut](
        items=[AgencyOut.model_validate(a) for a in items],
        meta=PageMeta.build(page=page, page_size=page_size, total=total),
    )


@router.get("/{agency_id}", response_model=AgencyProfile)
def agency_detail(agency_id: int, session: Session = Depends(get_session)) -> AgencyProfile:
    repo = AgencyRepository(session)
    agency = repo.get(agency_id)
    if agency is None:
        raise HTTPException(404, "Agency not found")
    profile = AnalyticsService(session).agency_profile(agency_id)
    out = AgencyProfile.model_validate({**agency.model_dump(), **profile})
    return out
