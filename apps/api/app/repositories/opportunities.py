"""Opportunity repository — filtering, search, facets, upsert."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.opportunity import Opportunity, OpportunityItem
from app.schemas.opportunity import OpportunityFilters


class OpportunityRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ---- read ---------------------------------------------------------------
    def get(self, opportunity_id: int) -> Opportunity | None:
        stmt = (
            select(Opportunity)
            .where(Opportunity.id == opportunity_id)
            .options(
                selectinload(Opportunity.items),
                selectinload(Opportunity.enrichment),
                selectinload(Opportunity.agency),
            )
        )
        return self.session.exec(stmt).first()

    def get_by_source(self, source: str, source_id: str) -> Opportunity | None:
        stmt = select(Opportunity).where(
            Opportunity.source == source, Opportunity.source_id == source_id
        )
        return self.session.exec(stmt).first()

    def _apply_filters(self, stmt, filters: OpportunityFilters):
        if filters.q:
            like = f"%{filters.q.lower()}%"
            stmt = stmt.where(
                or_(
                    Opportunity.title.ilike(like),  # type: ignore[attr-defined]
                    Opportunity.object_description.ilike(like),  # type: ignore[attr-defined]
                )
            )
        if filters.state:
            stmt = stmt.where(Opportunity.state == filters.state)
        if filters.city:
            stmt = stmt.where(Opportunity.city == filters.city)
        if filters.agency_id:
            stmt = stmt.where(Opportunity.agency_id == filters.agency_id)
        if filters.modality:
            stmt = stmt.where(Opportunity.modality == filters.modality)
        if filters.status:
            stmt = stmt.where(Opportunity.status == filters.status)
        if filters.category:
            stmt = stmt.where(Opportunity.category == filters.category)
        if filters.source:
            stmt = stmt.where(Opportunity.source == filters.source)
        if filters.min_value is not None:
            stmt = stmt.where(Opportunity.estimated_value >= filters.min_value)
        if filters.max_value is not None:
            stmt = stmt.where(Opportunity.estimated_value <= filters.max_value)
        if filters.published_from:
            stmt = stmt.where(Opportunity.published_at >= filters.published_from)
        if filters.published_to:
            stmt = stmt.where(Opportunity.published_at <= filters.published_to)
        if filters.closes_from:
            stmt = stmt.where(Opportunity.proposals_close_at >= filters.closes_from)
        if filters.closes_to:
            stmt = stmt.where(Opportunity.proposals_close_at <= filters.closes_to)
        return stmt

    SORT_MAP: dict[str, tuple] = {
        "published_at_desc": (Opportunity.published_at, "desc"),
        "published_at_asc": (Opportunity.published_at, "asc"),
        "value_desc": (Opportunity.estimated_value, "desc"),
        "value_asc": (Opportunity.estimated_value, "asc"),
        "closes_at_asc": (Opportunity.proposals_close_at, "asc"),
        "closes_at_desc": (Opportunity.proposals_close_at, "desc"),
    }

    def search(
        self,
        filters: OpportunityFilters,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Opportunity], int]:
        base = select(Opportunity).options(
            selectinload(Opportunity.agency),
            selectinload(Opportunity.enrichment),
        )
        base = self._apply_filters(base, filters)

        count_stmt = select(func.count()).select_from(self._apply_filters(select(Opportunity.id), filters).subquery())
        total = int(self.session.exec(count_stmt).one())

        col, direction = self.SORT_MAP.get(filters.sort, self.SORT_MAP["published_at_desc"])
        base = base.order_by(col.desc() if direction == "desc" else col.asc())
        base = base.limit(limit).offset(offset)
        items = list(self.session.exec(base).all())
        return items, total

    def facets(self, filters: OpportunityFilters) -> dict[str, list[tuple[str, int]]]:
        """Return facet counts for the given filter context."""

        def _count_by(column):
            stmt = select(column, func.count(Opportunity.id)).group_by(column)
            stmt = self._apply_filters(stmt, filters)
            rows = self.session.exec(stmt).all()
            return [(r[0] or "unknown", int(r[1])) for r in rows if r[0] is not None]

        return {
            "modality": _count_by(Opportunity.modality),
            "status": _count_by(Opportunity.status),
            "category": _count_by(Opportunity.category),
            "state": _count_by(Opportunity.state),
            "source": _count_by(Opportunity.source),
        }

    # ---- write --------------------------------------------------------------
    def upsert(self, payload: dict, items: list[dict] | None = None) -> Opportunity:
        existing = self.get_by_source(payload["source"], payload["source_id"])
        if existing is None:
            entity = Opportunity(**payload)
            self.session.add(entity)
            self.session.flush()
        else:
            for key, value in payload.items():
                if value is not None and hasattr(existing, key):
                    setattr(existing, key, value)
            existing.updated_at = datetime.now(UTC)
            entity = existing

        if items is not None:
            # simplest correct approach: wipe + reinsert items (volumes are small)
            for old in list(entity.items):
                self.session.delete(old)
            self.session.flush()
            for item in items:
                self.session.add(OpportunityItem(opportunity_id=entity.id, **item))
            self.session.flush()

        return entity
