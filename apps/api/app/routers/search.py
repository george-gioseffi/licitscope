"""Free-form semantic search."""

from __future__ import annotations

from fastapi import APIRouter, Depends, Query
from sqlmodel import Session

from app.db.session import get_session
from app.schemas.opportunity import SimilarOpportunity
from app.services.search import SearchService

router = APIRouter(prefix="/search", tags=["search"])


@router.get("", response_model=list[SimilarOpportunity], summary="Semantic search via TF-IDF similarity")
def search(
    q: str = Query(..., min_length=2),
    k: int = Query(20, ge=1, le=50),
    session: Session = Depends(get_session),
) -> list[SimilarOpportunity]:
    return SearchService(session).semantic_search(q, k=k)
