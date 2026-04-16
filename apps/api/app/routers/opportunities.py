"""Opportunity routes — feed, detail, facets, similarity."""

from __future__ import annotations

from datetime import datetime

from fastapi import APIRouter, Depends, HTTPException, Query
from pydantic import ValidationError
from sqlmodel import Session

from app.db.session import get_session
from app.models.enums import MODALITY_LABELS
from app.repositories.opportunities import OpportunityRepository
from app.schemas.common import Page, PageMeta
from app.schemas.opportunity import (
    Facet,
    OpportunityDetail,
    OpportunityFacets,
    OpportunityFilters,
    OpportunitySummary,
    SimilarOpportunity,
)
from app.services.search import SearchService

router = APIRouter(prefix="/opportunities", tags=["opportunities"])


def _filters_dep(
    q: str | None = Query(None, description="Free-text query across title and object"),
    state: str | None = Query(None, description="UF (2 letters)"),
    city: str | None = None,
    agency_id: int | None = None,
    modality: str | None = None,
    status: str | None = None,
    category: str | None = None,
    source: str | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    published_from: datetime | None = None,
    published_to: datetime | None = None,
    closes_from: datetime | None = None,
    closes_to: datetime | None = None,
    sort: str = Query("published_at_desc"),
) -> OpportunityFilters:
    try:
        return OpportunityFilters(
            q=q,
            state=state,
            city=city,
            agency_id=agency_id,
            modality=modality,
            status=status,
            category=category,
            source=source,
            min_value=min_value,
            max_value=max_value,
            published_from=published_from,
            published_to=published_to,
            closes_from=closes_from,
            closes_to=closes_to,
            sort=sort,
        )
    except ValidationError as exc:
        # Surface schema-level validation as a proper 422 rather than a 500.
        # pydantic.errors() may embed un-serializable Exception objects in
        # `ctx`; keep just the fields FastAPI can encode.
        detail = [
            {"loc": list(err["loc"]), "msg": err["msg"], "type": err["type"]}
            for err in exc.errors()
        ]
        raise HTTPException(status_code=422, detail=detail) from exc


@router.get("", response_model=Page[OpportunitySummary], summary="Feed of opportunities")
def list_opportunities(
    filters: OpportunityFilters = Depends(_filters_dep),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    session: Session = Depends(get_session),
) -> Page[OpportunitySummary]:
    if (
        filters.min_value is not None
        and filters.max_value is not None
        and filters.min_value > filters.max_value
    ):
        raise HTTPException(status_code=422, detail="min_value must be <= max_value")

    repo = OpportunityRepository(session)
    offset = (page - 1) * page_size
    items, total = repo.search(filters, limit=page_size, offset=offset)

    return Page[OpportunitySummary](
        items=[OpportunitySummary.from_model(o) for o in items],
        meta=PageMeta.build(page=page, page_size=page_size, total=total),
    )


@router.get("/facets", response_model=OpportunityFacets, summary="Facet counts for the current filter context")
def opportunity_facets(
    filters: OpportunityFilters = Depends(_filters_dep),
    session: Session = Depends(get_session),
) -> OpportunityFacets:
    repo = OpportunityRepository(session)
    raw = repo.facets(filters)

    def _facets(pairs: list[tuple[str, int]], labels: dict[str, str] | None = None) -> list[Facet]:
        rows = [
            Facet(value=v, label=(labels or {}).get(v, v), count=c)
            for v, c in pairs
        ]
        rows.sort(key=lambda f: (-f.count, f.label))
        return rows

    return OpportunityFacets(
        modalities=_facets(raw["modality"], MODALITY_LABELS),
        statuses=_facets(raw["status"]),
        categories=_facets(raw["category"]),
        states=_facets(raw["state"]),
        sources=_facets(raw["source"]),
    )


@router.get("/{opportunity_id}", response_model=OpportunityDetail, summary="Opportunity detail")
def get_opportunity(opportunity_id: int, session: Session = Depends(get_session)) -> OpportunityDetail:
    repo = OpportunityRepository(session)
    opp = repo.get(opportunity_id)
    if opp is None:
        raise HTTPException(status_code=404, detail="Opportunity not found")
    detail = OpportunityDetail.model_validate(opp)
    if opp.enrichment is not None:
        detail.complexity_score = opp.enrichment.complexity_score
        detail.risk_score = opp.enrichment.risk_score
    return detail


@router.get(
    "/{opportunity_id}/similar",
    response_model=list[SimilarOpportunity],
    summary="Top-K semantically similar opportunities (offline TF-IDF)",
)
def similar_opportunities(
    opportunity_id: int,
    k: int = Query(5, ge=1, le=20),
    session: Session = Depends(get_session),
) -> list[SimilarOpportunity]:
    return SearchService(session).similar_to(opportunity_id, k=k)
