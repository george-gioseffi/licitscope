"""Contract repository."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.contract import Contract, ContractItem


class ContractRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, contract_id: int) -> Contract | None:
        stmt = (
            select(Contract)
            .where(Contract.id == contract_id)
            .options(
                selectinload(Contract.items),
                selectinload(Contract.agency),
                selectinload(Contract.supplier),
            )
        )
        return self.session.exec(stmt).first()

    def get_by_source(self, source: str, source_id: str) -> Contract | None:
        stmt = select(Contract).where(Contract.source == source, Contract.source_id == source_id)
        return self.session.exec(stmt).first()

    def list(
        self,
        *,
        q: str | None = None,
        agency_id: int | None = None,
        supplier_id: int | None = None,
        min_value: float | None = None,
        max_value: float | None = None,
        status: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Contract], int]:
        stmt = select(Contract).options(
            selectinload(Contract.agency),
            selectinload(Contract.supplier),
        )
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(
                or_(
                    Contract.object_description.ilike(like),  # type: ignore[attr-defined]
                    Contract.contract_number.ilike(like),  # type: ignore[attr-defined]
                )
            )
        if agency_id:
            stmt = stmt.where(Contract.agency_id == agency_id)
        if supplier_id:
            stmt = stmt.where(Contract.supplier_id == supplier_id)
        if min_value is not None:
            stmt = stmt.where(Contract.total_value >= min_value)
        if max_value is not None:
            stmt = stmt.where(Contract.total_value <= max_value)
        if status:
            stmt = stmt.where(Contract.status == status)

        count_stmt = select(func.count()).select_from(stmt.subquery())
        total = int(self.session.exec(count_stmt).one())

        stmt = stmt.order_by(Contract.signed_at.desc().nullslast()).limit(limit).offset(offset)  # type: ignore[attr-defined]
        return list(self.session.exec(stmt).all()), total

    def upsert(self, payload: dict, items: list[dict] | None = None) -> Contract:
        existing = self.get_by_source(payload["source"], payload["source_id"])
        if existing is None:
            entity = Contract(**payload)
            self.session.add(entity)
            self.session.flush()
        else:
            for key, value in payload.items():
                if value is not None and hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(UTC)
            entity = existing

        if items is not None:
            for old in list(entity.items):
                self.session.delete(old)
            self.session.flush()
            for item in items:
                self.session.add(ContractItem(contract_id=entity.id, **item))
            self.session.flush()
        return entity

    def price_observations(self, *, catmat_or_catser: str) -> list[ContractItem]:
        """Return item-level price observations for a given classification code."""
        stmt = select(ContractItem).where(
            or_(
                ContractItem.catmat_code == catmat_or_catser,
                ContractItem.catser_code == catmat_or_catser,
            )
        )
        return list(self.session.exec(stmt).all())
