"""Pricing intelligence — aggregate contract-item observations per CATMAT/CATSER."""

from __future__ import annotations

import statistics

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.contract import ContractItem
from app.schemas.contract import PricingIntelligence


class PricingService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(self, *, limit: int = 25) -> list[PricingIntelligence]:
        # Group by catmat (prefer) else catser
        rows = self.session.exec(
            select(
                func.coalesce(ContractItem.catmat_code, ContractItem.catser_code),
                func.count(ContractItem.id),
            )
            .where(ContractItem.unit_price.isnot(None))  # type: ignore[attr-defined]
            .group_by(func.coalesce(ContractItem.catmat_code, ContractItem.catser_code))
            .order_by(func.count(ContractItem.id).desc())
            .limit(limit)
        ).all()

        out: list[PricingIntelligence] = []
        for code, _count in rows:
            if not code:
                continue
            items = self.session.exec(
                select(ContractItem).where(
                    (ContractItem.catmat_code == code) | (ContractItem.catser_code == code)
                )
            ).all()
            prices = sorted([i.unit_price for i in items if i.unit_price and i.unit_price > 0])
            if len(prices) < 3:
                continue
            sample_desc = items[0].description
            median = statistics.median(prices)
            p25 = prices[len(prices) // 4] if len(prices) >= 4 else prices[0]
            p75 = prices[3 * len(prices) // 4] if len(prices) >= 4 else prices[-1]
            lo, hi = prices[0], prices[-1]
            dispersion = (hi - lo) / median if median else 0.0
            out.append(
                PricingIntelligence(
                    catmat_or_catser=str(code),
                    description_sample=sample_desc[:160],
                    observations=len(prices),
                    median_unit_price=round(float(median), 2),
                    p25_unit_price=round(float(p25), 2),
                    p75_unit_price=round(float(p75), 2),
                    min_unit_price=round(float(lo), 2),
                    max_unit_price=round(float(hi), 2),
                    anomaly_flag=dispersion > 2.5,
                )
            )
        return out
