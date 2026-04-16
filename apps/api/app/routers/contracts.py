"""Contract routes + pricing intelligence."""

from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException, Query
from sqlmodel import Session

from app.db.session import get_session
from app.repositories.contracts import ContractRepository
from app.schemas.common import Page, PageMeta
from app.schemas.contract import ContractDetail, ContractOut, PricingIntelligence
from app.services.pricing import PricingService

router = APIRouter(prefix="/contracts", tags=["contracts"])


@router.get("", response_model=Page[ContractOut])
def list_contracts(
    q: str | None = None,
    agency_id: int | None = None,
    supplier_id: int | None = None,
    min_value: float | None = None,
    max_value: float | None = None,
    status: str | None = None,
    page: int = Query(1, ge=1),
    page_size: int = Query(25, ge=1, le=100),
    session: Session = Depends(get_session),
) -> Page[ContractOut]:
    repo = ContractRepository(session)
    offset = (page - 1) * page_size
    items, total = repo.list(
        q=q,
        agency_id=agency_id,
        supplier_id=supplier_id,
        min_value=min_value,
        max_value=max_value,
        status=status,
        limit=page_size,
        offset=offset,
    )
    return Page[ContractOut](
        items=[ContractOut.model_validate(c) for c in items],
        meta=PageMeta.build(page=page, page_size=page_size, total=total),
    )


@router.get("/pricing", response_model=list[PricingIntelligence])
def pricing_intelligence(
    limit: int = Query(25, ge=1, le=100),
    session: Session = Depends(get_session),
) -> list[PricingIntelligence]:
    return PricingService(session).summary(limit=limit)


@router.get("/{contract_id}", response_model=ContractDetail)
def contract_detail(contract_id: int, session: Session = Depends(get_session)) -> ContractDetail:
    repo = ContractRepository(session)
    contract = repo.get(contract_id)
    if contract is None:
        raise HTTPException(404, "Contract not found")
    return ContractDetail.model_validate(contract)
