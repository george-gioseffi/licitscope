"""Agency repository — persistence for public-sector contracting entities."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models.agency import Agency


class AgencyRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get(self, agency_id: int) -> Agency | None:
        return self.session.get(Agency, agency_id)

    def get_by_cnpj(self, cnpj: str) -> Agency | None:
        stmt = select(Agency).where(Agency.cnpj == cnpj)
        return self.session.exec(stmt).first()

    def list(
        self,
        *,
        q: str | None = None,
        state: str | None = None,
        sphere: str | None = None,
        limit: int = 50,
        offset: int = 0,
    ) -> tuple[list[Agency], int]:
        stmt = select(Agency)
        if q:
            like = f"%{q.lower()}%"
            stmt = stmt.where(Agency.name.ilike(like))  # type: ignore[attr-defined]
        if state:
            stmt = stmt.where(Agency.state == state)
        if sphere:
            stmt = stmt.where(Agency.sphere == sphere)
        total = len(self.session.exec(stmt).all())
        stmt = stmt.order_by(Agency.name).limit(limit).offset(offset)  # type: ignore[attr-defined]
        return list(self.session.exec(stmt).all()), total

    def upsert(self, payload: dict) -> Agency:
        existing = self.get_by_cnpj(payload["cnpj"])
        if existing is None:
            entity = Agency(**payload)
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
