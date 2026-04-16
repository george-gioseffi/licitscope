"""Enrichment repository."""

from __future__ import annotations

from sqlmodel import Session, select

from app.models.enrichment import Enrichment


class EnrichmentRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    def get_for_opportunity(self, opportunity_id: int) -> Enrichment | None:
        stmt = select(Enrichment).where(Enrichment.opportunity_id == opportunity_id)
        return self.session.exec(stmt).first()

    def upsert(self, opportunity_id: int, payload: dict) -> Enrichment:
        existing = self.get_for_opportunity(opportunity_id)
        if existing is None:
            entity = Enrichment(opportunity_id=opportunity_id, **payload)
            self.session.add(entity)
            self.session.flush()
            return entity
        for key, value in payload.items():
            if hasattr(existing, key):
                setattr(existing, key, value)
        self.session.add(existing)
        self.session.flush()
        return existing

    def list_fingerprints(self) -> list[Enrichment]:
        stmt = select(Enrichment).where(Enrichment.fingerprint.isnot(None))  # type: ignore[attr-defined]
        return list(self.session.exec(stmt).all())
