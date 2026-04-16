"""Watchlists — saved filter expressions + their alerts."""

from __future__ import annotations

from datetime import UTC, datetime

from fastapi import APIRouter, Depends, HTTPException
from pydantic import BaseModel
from sqlmodel import Session, select

from app.db.session import get_session
from app.models.watchlist import Alert, Watchlist
from app.repositories.opportunities import OpportunityRepository
from app.schemas.opportunity import OpportunityFilters, OpportunitySummary

router = APIRouter(prefix="/watchlists", tags=["watchlists"])


class WatchlistCreate(BaseModel):
    name: str
    description: str | None = None
    filters: OpportunityFilters
    notify_email: str | None = None
    notify_webhook_url: str | None = None


class WatchlistOut(BaseModel):
    id: int
    name: str
    description: str | None
    filters: dict
    notify_email: str | None
    notify_webhook_url: str | None
    active: bool
    created_at: datetime
    last_run_at: datetime | None
    match_count: int = 0


@router.get("", response_model=list[WatchlistOut])
def list_watchlists(session: Session = Depends(get_session)) -> list[WatchlistOut]:
    rows = list(session.exec(select(Watchlist).order_by(Watchlist.created_at.desc())).all())  # type: ignore[attr-defined]
    return [
        WatchlistOut(
            id=w.id,
            name=w.name,
            description=w.description,
            filters=w.filters,
            notify_email=w.notify_email,
            notify_webhook_url=w.notify_webhook_url,
            active=w.active,
            created_at=w.created_at,
            last_run_at=w.last_run_at,
            match_count=len(w.alerts or []),
        )
        for w in rows
    ]


@router.post("", response_model=WatchlistOut, status_code=201)
def create_watchlist(
    payload: WatchlistCreate, session: Session = Depends(get_session)
) -> WatchlistOut:
    entity = Watchlist(
        name=payload.name,
        description=payload.description,
        filters=payload.filters.model_dump(),
        notify_email=payload.notify_email,
        notify_webhook_url=payload.notify_webhook_url,
    )
    session.add(entity)
    session.commit()
    session.refresh(entity)
    return WatchlistOut(
        id=entity.id,
        name=entity.name,
        description=entity.description,
        filters=entity.filters,
        notify_email=entity.notify_email,
        notify_webhook_url=entity.notify_webhook_url,
        active=entity.active,
        created_at=entity.created_at,
        last_run_at=entity.last_run_at,
        match_count=0,
    )


@router.delete("/{watchlist_id}", status_code=204)
def delete_watchlist(watchlist_id: int, session: Session = Depends(get_session)) -> None:
    entity = session.get(Watchlist, watchlist_id)
    if not entity:
        raise HTTPException(404, "Watchlist not found")
    session.delete(entity)
    session.commit()


@router.post("/{watchlist_id}/run", response_model=list[OpportunitySummary])
def run_watchlist(
    watchlist_id: int, session: Session = Depends(get_session)
) -> list[OpportunitySummary]:
    watchlist = session.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(404, "Watchlist not found")
    filters = OpportunityFilters.model_validate(watchlist.filters)
    repo = OpportunityRepository(session)
    items, _ = repo.search(filters, limit=50, offset=0)

    # Record alerts for any notices not previously seen by this watchlist.
    known = {a.opportunity_id for a in watchlist.alerts}
    for opp in items:
        if opp.id in known:
            continue
        session.add(
            Alert(
                watchlist_id=watchlist.id,
                opportunity_id=opp.id,
                headline=opp.title[:512],
                payload={"estimated_value": opp.estimated_value, "state": opp.state},
            )
        )
    watchlist.last_run_at = datetime.now(UTC)
    session.add(watchlist)
    session.commit()

    return [OpportunitySummary.model_validate(o) for o in items]


@router.get("/{watchlist_id}/alerts")
def list_alerts(watchlist_id: int, session: Session = Depends(get_session)) -> list[dict]:
    watchlist = session.get(Watchlist, watchlist_id)
    if not watchlist:
        raise HTTPException(404, "Watchlist not found")
    return [
        {
            "id": a.id,
            "headline": a.headline,
            "opportunity_id": a.opportunity_id,
            "fired_at": a.fired_at.isoformat(),
            "read": a.read,
            "payload": a.payload,
        }
        for a in sorted(watchlist.alerts, key=lambda x: x.fired_at, reverse=True)
    ]
