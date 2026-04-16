"""Opportunity repository — filtering, search, facets, upsert."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import func, or_
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.opportunity import Opportunity, OpportunityItem
from app.schemas.opportunity import OpportunityFilters

# For each facet dimension, the filter fields that would collapse its counts.
# When computing that dimension's facet list, we skip those filters so the
# user can see alternatives rather than a single selected value.
_FACET_EXCLUSIONS: dict[str, frozenset[str]] = {
    "modality": frozenset({"modality"}),
    "status": frozenset({"status"}),
    "category": frozenset({"category"}),
    "state": frozenset({"state"}),
    "source": frozenset({"source"}),
}


class OpportunityRepository:
    SORT_MAP: dict[str, tuple] = {
        "published_at_desc": (Opportunity.published_at, "desc"),
        "published_at_asc": (Opportunity.published_at, "asc"),
        "value_desc": (Opportunity.estimated_value, "desc"),
        "value_asc": (Opportunity.estimated_value, "asc"),
        "closes_at_asc": (Opportunity.proposals_close_at, "asc"),
        "closes_at_desc": (Opportunity.proposals_close_at, "desc"),
    }

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

    def _apply_filters(
        self,
        stmt,
        filters: OpportunityFilters,
        *,
        skip: frozenset[str] = frozenset(),
    ):
        """Attach WHERE clauses. ``skip`` names filter fields to ignore — used
        by facet queries so each facet shows alternative counts instead of
        collapsing to the user's already-selected value.
        """
        if filters.q and "q" not in skip:
            like = f"%{filters.q}%"
            stmt = stmt.where(
                or_(
                    Opportunity.title.ilike(like),  # type: ignore[attr-defined]
                    Opportunity.object_description.ilike(like),  # type: ignore[attr-defined]
                )
            )
        if filters.state and "state" not in skip:
            stmt = stmt.where(Opportunity.state == filters.state)
        if filters.city and "city" not in skip:
            stmt = stmt.where(Opportunity.city == filters.city)
        if filters.agency_id and "agency_id" not in skip:
            stmt = stmt.where(Opportunity.agency_id == filters.agency_id)
        if filters.modality and "modality" not in skip:
            stmt = stmt.where(Opportunity.modality == filters.modality)
        if filters.status and "status" not in skip:
            stmt = stmt.where(Opportunity.status == filters.status)
        if filters.category and "category" not in skip:
            stmt = stmt.where(Opportunity.category == filters.category)
        if filters.source and "source" not in skip:
            stmt = stmt.where(Opportunity.source == filters.source)
        if filters.min_value is not None and "min_value" not in skip:
            stmt = stmt.where(Opportunity.estimated_value >= filters.min_value)
        if filters.max_value is not None and "max_value" not in skip:
            stmt = stmt.where(Opportunity.estimated_value <= filters.max_value)
        if filters.published_from and "published_from" not in skip:
            stmt = stmt.where(Opportunity.published_at >= filters.published_from)
        if filters.published_to and "published_to" not in skip:
            stmt = stmt.where(Opportunity.published_at <= filters.published_to)
        if filters.closes_from and "closes_from" not in skip:
            stmt = stmt.where(Opportunity.proposals_close_at >= filters.closes_from)
        if filters.closes_to and "closes_to" not in skip:
            stmt = stmt.where(Opportunity.proposals_close_at <= filters.closes_to)
        return stmt

    def search(
        self,
        filters: OpportunityFilters,
        *,
        limit: int = 20,
        offset: int = 0,
    ) -> tuple[list[Opportunity], int]:
        count_stmt = select(func.count()).select_from(
            self._apply_filters(select(Opportunity.id), filters).subquery()
        )
        total = int(self.session.exec(count_stmt).one())

        base = select(Opportunity).options(
            selectinload(Opportunity.agency),
            selectinload(Opportunity.enrichment),
        )
        base = self._apply_filters(base, filters)

        col, direction = self.SORT_MAP.get(filters.sort, self.SORT_MAP["published_at_desc"])
        order = col.desc().nullslast() if direction == "desc" else col.asc().nullslast()  # type: ignore[attr-defined]
        base = base.order_by(order, Opportunity.id.desc()).limit(limit).offset(offset)  # type: ignore[attr-defined]
        items = list(self.session.exec(base).all())
        return items, total

    def facets(self, filters: OpportunityFilters) -> dict[str, list[tuple[str, int]]]:
        """Return facet counts for each supported dimension.

        For each dimension, the filter on that same dimension is removed
        from the WHERE clause — which is the standard faceted-search pattern,
        giving the user alternatives to their current selection rather than
        a tautological single-row answer.
        """

        def _count_by(dimension: str, column):
            skip = _FACET_EXCLUSIONS.get(dimension, frozenset())
            stmt = select(column, func.count(Opportunity.id)).group_by(column)
            stmt = self._apply_filters(stmt, filters, skip=skip)
            rows = self.session.exec(stmt).all()
            return [(r[0], int(r[1])) for r in rows if r[0] is not None]

        return {
            "modality": _count_by("modality", Opportunity.modality),
            "status": _count_by("status", Opportunity.status),
            "category": _count_by("category", Opportunity.category),
            "state": _count_by("state", Opportunity.state),
            "source": _count_by("source", Opportunity.source),
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
            # replace the item set atomically; volumes per notice are small
            for old in list(entity.items):
                self.session.delete(old)
            self.session.flush()
            for item in items:
                self.session.add(OpportunityItem(opportunity_id=entity.id, **item))
            self.session.flush()

        return entity
