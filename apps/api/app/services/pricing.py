"""Pricing intelligence — aggregate contract-item observations per CATMAT/CATSER.

The summary is what powers the "Inteligência de preços" dashboard: for each
classification code we compute a robust price distribution (median, IQR,
extremes) and flag anomalous dispersion using the same IQR-based heuristic
that lives in :mod:`app.enrichment.scoring`.
"""

from __future__ import annotations

import statistics

from sqlalchemy import func
from sqlmodel import Session, select

from app.models.contract import ContractItem
from app.schemas.contract import PricingIntelligence

MIN_OBSERVATIONS = 3
ANOMALY_IQR_RATIO = 0.75  # IQR >= 75% of median -> dispersão alta


class PricingService:
    def __init__(self, session: Session) -> None:
        self.session = session

    def summary(self, *, limit: int = 25) -> list[PricingIntelligence]:
        # Group by a single stable code (prefer CATMAT, fall back to CATSER).
        code_col = func.coalesce(ContractItem.catmat_code, ContractItem.catser_code)
        rows = self.session.exec(
            select(code_col, func.count(ContractItem.id))
            .where(ContractItem.unit_price.isnot(None))  # type: ignore[attr-defined]
            .where(ContractItem.unit_price > 0)  # type: ignore[operator]
            .group_by(code_col)
            .having(func.count(ContractItem.id) >= MIN_OBSERVATIONS)
            .order_by(func.count(ContractItem.id).desc())
            .limit(limit)
        ).all()

        out: list[PricingIntelligence] = []
        for code, _count in rows:
            if not code:
                continue
            items = list(
                self.session.exec(
                    select(ContractItem).where(
                        (ContractItem.catmat_code == code) | (ContractItem.catser_code == code)
                    )
                ).all()
            )
            prices = sorted(
                float(i.unit_price)
                for i in items
                if i.unit_price is not None and i.unit_price > 0
            )
            if len(prices) < MIN_OBSERVATIONS:
                continue

            median = statistics.median(prices)
            if len(prices) >= 4:
                q1, _m, q3 = statistics.quantiles(prices, n=4)
            else:
                q1, q3 = prices[0], prices[-1]
            lo, hi = prices[0], prices[-1]
            iqr = q3 - q1
            dispersion = iqr / median if median else 0.0

            # Pick the most representative description sample: the one closest
            # to the median, not just the first row (which is random order).
            sample_item = min(
                items,
                key=lambda i: abs((i.unit_price or 0) - median),
            )

            out.append(
                PricingIntelligence(
                    catmat_or_catser=str(code),
                    description_sample=(sample_item.description or "")[:160],
                    observations=len(prices),
                    median_unit_price=round(median, 2),
                    p25_unit_price=round(q1, 2),
                    p75_unit_price=round(q3, 2),
                    min_unit_price=round(lo, 2),
                    max_unit_price=round(hi, 2),
                    anomaly_flag=dispersion >= ANOMALY_IQR_RATIO,
                )
            )
        return out
