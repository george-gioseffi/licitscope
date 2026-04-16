"""Supplier repository."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models.supplier import Supplier


class SupplierRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, supplier_id: int) -> Supplier | None:
        return self.session.get(Supplier, supplier_id)

    def get_by_tax_id(self, tax_id: str) -> Supplier | None:
        stmt = select(Supplier).where(Supplier.tax_id == tax_id)
        return self.session.exec(stmt).first()

    def list(
        self,
        *,
        q: str | None = None,
        state: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Supplier], int]:
        stmt = select(Supplier)
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(Supplier.name.ilike(like))  # type: ignore[attr-defined]
        if state:
            stmt = stmt.where(Supplier.state == state)
        total = len(self.session.exec(stmt).all())
        stmt = stmt.order_by(Supplier.name).limit(limit).offset(offset)  # type: ignore[attr-defined]
        return list(self.session.exec(stmt).all()), total

    def upsert(self, payload: dict) -> Supplier:
        existing = self.get_by_tax_id(payload["tax_id"])
        if existing is None:
            entity = Supplier(**payload)
            self.session.add(entity)
            self.session.flush()
            return entity
        for key, value in payload.items():
            if value is not None and hasattr(existing, key):
                setattr(existing, key, value)
        existing.updated_at = datetime.now(UTC)
        self.session.add(existing)
        self.session.flush()
        return existing
