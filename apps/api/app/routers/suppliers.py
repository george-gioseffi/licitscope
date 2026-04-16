"""Supplier routes."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_session
from app.repositories.suppliers import SupplierRepository
from app.schemas.common import Page, PageMeta
from app.schemas.supplier import SupplierOut, SupplierProfile
from app.services.analytics import AnalyticsService

router = APIRouter(prefix="/suppliers", tags=["suppliers"])


@router.get("", response_model=Page[SupplierOut])
def list_suppliers(
    q: str | None = None,
    state: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    session: Session = Depends(get_session),
) -> Page[SupplierOut]:
    repo = SupplierRepository(session)
    offset = (page - 1) * page_size
    items, total = repo.list(q=q, state=state, limit=page_size, offset=offset)
    return Page[SupplierOut](
        items=[SupplierOut.model_validate(s) for s in items],
        meta=PageMeta.build(page=page, page_size=page_size, total=total),
    )


@router.get("/{supplier_id}", response_model=SupplierProfile)
def supplier_detail(supplier_id: int, session: Session = Depends(get_session)) -> SupplierProfile:
    repo = SupplierRepository(session)
    supplier = repo.get(supplier_id)
    if supplier is None:
        raise HTTPException(404, "Supplier not found")
    profile = AnalyticsService(session).supplier_profile(supplier_id)
    out = SupplierProfile.model_validate({**supplier.model_dump(), **profile})
    return out
