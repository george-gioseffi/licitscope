"""Aggregate analytics for the dashboard."""

from __future__ import annotations

from datetime import UTC, datetime, timedelta
from typing import Any

from sqlalchemy import func
from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.agency import Agency
from app.models.contract import Contract
from app.models.enrichment import Enrichment
from app.models.enums import MODALITY_LABELS
from app.models.ingestion import IngestionRun
from app.models.opportunity import Opportunity
from app.schemas.opportunity import (
    AnalyticsKPI,
    CategoryBreakdown,
    DashboardOverview,
    GeoBreakdown,
    OpportunitySummary,
    TimeSeriesPoint,
)


class AnalyticsService:
    def __init__(self, session: Session) -> None:
        self.session = session

    # ---- dashboard overview -------------------------------------------------
    def dashboard_overview(self) -> DashboardOverview:
        now = datetime.now(UTC)
        week_ago = now - timedelta(days=7)
        prev_week = now - timedelta(days=14)

        total_now = int(
            self.session.exec(
                select(func.count(Opportunity.id)).where(Opportunity.published_at >= week_ago)
            ).one()
        )
        total_prev = int(
            self.session.exec(
                select(func.count(Opportunity.id))
                .where(Opportunity.published_at >= prev_week)
                .where(Opportunity.published_at < week_ago)
            ).one()
        )
        total_value = float(
            self.session.exec(
                select(func.coalesce(func.sum(Opportunity.estimated_value), 0.0)).where(
                    Opportunity.published_at >= week_ago
                )
            ).one()
            or 0.0
        )
        open_now = int(
            self.session.exec(
                select(func.count(Opportunity.id)).where(
                    Opportunity.proposals_close_at >= now,
                )
            ).one()
        )
        avg_risk = self.session.exec(
            select(func.coalesce(func.avg(Enrichment.risk_score), 0.0))
        ).one()

        kpis = [
            AnalyticsKPI(
                label="Publicações (7d)",
                value=float(total_now),
                trend=float(total_now - total_prev),
                description="Licitações publicadas na última semana",
            ),
            AnalyticsKPI(
                label="Valor estimado (7d)",
                value=float(total_value),
                suffix="BRL",
                description="Soma dos valores estimados na última semana",
            ),
            AnalyticsKPI(
                label="Abertas para propostas",
                value=float(open_now),
                description="Licitações aceitando propostas agora",
            ),
            AnalyticsKPI(
                label="Risco médio",
                value=round(float(avg_risk or 0.0), 3),
                description="Score médio de risco heurístico",
            ),
        ]

        recent_stmt = (
            select(Opportunity)
            .options(selectinload(Opportunity.agency), selectinload(Opportunity.enrichment))
            .order_by(Opportunity.published_at.desc().nullslast())  # type: ignore[attr-defined]
            .limit(8)
        )
        recent = [OpportunitySummary.from_model(o) for o in self.session.exec(recent_stmt).all()]

        per_day_rows = self.session.exec(
            select(
                func.date(Opportunity.published_at),
                func.count(Opportunity.id),
                func.coalesce(func.sum(Opportunity.estimated_value), 0.0),
            )
            .where(Opportunity.published_at >= now - timedelta(days=30))
            .group_by(func.date(Opportunity.published_at))
            .order_by(func.date(Opportunity.published_at))
        ).all()
        per_day = [
            TimeSeriesPoint(date=str(r[0]), count=int(r[1]), value=float(r[2] or 0.0))
            for r in per_day_rows
            if r[0] is not None
        ]

        by_cat_rows = self.session.exec(
            select(
                Opportunity.category,
                func.count(Opportunity.id),
                func.coalesce(func.sum(Opportunity.estimated_value), 0.0),
            )
            .group_by(Opportunity.category)
            .order_by(func.count(Opportunity.id).desc())
            .limit(12)
        ).all()
        by_category = [
            CategoryBreakdown(
                category=(r[0] or "Não classificado"),
                count=int(r[1]),
                total_value=float(r[2] or 0.0),
            )
            for r in by_cat_rows
        ]

        by_state_rows = self.session.exec(
            select(
                Opportunity.state,
                func.count(Opportunity.id),
                func.coalesce(func.sum(Opportunity.estimated_value), 0.0),
            )
            .group_by(Opportunity.state)
            .order_by(func.count(Opportunity.id).desc())
            .limit(27)
        ).all()
        by_state = [
            GeoBreakdown(state=(r[0] or "—"), count=int(r[1]), total_value=float(r[2] or 0.0))
            for r in by_state_rows
        ]

        by_mod_rows = self.session.exec(
            select(
                Opportunity.modality,
                func.count(Opportunity.id),
                func.coalesce(func.sum(Opportunity.estimated_value), 0.0),
            )
            .group_by(Opportunity.modality)
            .order_by(func.count(Opportunity.id).desc())
        ).all()
        by_modality = [
            CategoryBreakdown(
                category=MODALITY_LABELS.get(r[0] or "", r[0] or "—"),
                count=int(r[1]),
                total_value=float(r[2] or 0.0),
            )
            for r in by_mod_rows
        ]

        # Top agencies in a single joined query (no N+1 agency fetches).
        top_agencies_rows = self.session.exec(
            select(
                Agency.id,
                Agency.name,
                Agency.state,
                func.count(Opportunity.id),
                func.coalesce(func.sum(Opportunity.estimated_value), 0.0),
            )
            .join(Opportunity, Opportunity.agency_id == Agency.id)
            .group_by(Agency.id, Agency.name, Agency.state)
            .order_by(func.count(Opportunity.id).desc())
            .limit(10)
        ).all()
        top_agencies: list[dict[str, Any]] = [
            {
                "agency_id": row[0],
                "name": row[1] or "—",
                "state": row[2],
                "count": int(row[3]),
                "total_value": float(row[4] or 0.0),
            }
            for row in top_agencies_rows
        ]

        source_health_rows = self.session.exec(
            select(IngestionRun)
            .order_by(IngestionRun.started_at.desc())  # type: ignore[attr-defined]
            .limit(10)
        ).all()
        source_health = [
            {
                "id": r.id,
                "source": r.source,
                "status": r.status,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
                "fetched": r.fetched,
                "created": r.created,
                "updated": r.updated,
            }
            for r in source_health_rows
        ]

        return DashboardOverview(
            kpis=kpis,
            recent=recent,
            published_per_day=per_day,
            by_category=by_category,
            by_state=by_state,
            by_modality=by_modality,
            top_agencies=top_agencies,
            source_health=source_health,
        )

    # ---- agency profile -----------------------------------------------------
    def agency_profile(self, agency_id: int) -> dict[str, Any]:
        opp_count = int(
            self.session.exec(
                select(func.count(Opportunity.id)).where(Opportunity.agency_id == agency_id)
            ).one()
        )
        active_count = int(
            self.session.exec(
                select(func.count(Opportunity.id)).where(
                    Opportunity.agency_id == agency_id,
                    Opportunity.proposals_close_at >= datetime.now(UTC),
                )
            ).one()
        )
        ctr_count = int(
            self.session.exec(
                select(func.count(Contract.id)).where(Contract.agency_id == agency_id)
            ).one()
        )
        total_value = float(
            self.session.exec(
                select(func.coalesce(func.sum(Contract.total_value), 0.0)).where(
                    Contract.agency_id == agency_id
                )
            ).one()
            or 0.0
        )
        cat_rows = self.session.exec(
            select(Opportunity.category, func.count(Opportunity.id))
            .where(Opportunity.agency_id == agency_id)
            .group_by(Opportunity.category)
            .order_by(func.count(Opportunity.id).desc())
            .limit(6)
        ).all()
        return {
            "opportunity_count": opp_count,
            "active_opportunities": active_count,
            "contract_count": ctr_count,
            "total_contracted_value": total_value,
            "top_categories": [
                {"category": r[0] or "Não classificado", "count": int(r[1])} for r in cat_rows
            ],
        }

    # ---- supplier profile ---------------------------------------------------
    def supplier_profile(self, supplier_id: int) -> dict[str, Any]:
        count = int(
            self.session.exec(
                select(func.count(Contract.id)).where(Contract.supplier_id == supplier_id)
            ).one()
        )
        total = float(
            self.session.exec(
                select(func.coalesce(func.sum(Contract.total_value), 0.0)).where(
                    Contract.supplier_id == supplier_id
                )
            ).one()
            or 0.0
        )
        agency_rows = self.session.exec(
            select(Agency.id, Agency.name, Agency.state, func.count(Contract.id))
            .join(Contract, Contract.agency_id == Agency.id)
            .where(Contract.supplier_id == supplier_id)
            .group_by(Agency.id, Agency.name, Agency.state)
            .order_by(func.count(Contract.id).desc())
            .limit(5)
        ).all()
        return {
            "contract_count": count,
            "total_contracted_value": total,
            "top_agencies": [
                {
                    "agency_id": row[0],
                    "name": row[1] or "—",
                    "state": row[2],
                    "count": int(row[3]),
                }
                for row in agency_rows
                if row[0]
            ],
            "top_categories": [],
        }
