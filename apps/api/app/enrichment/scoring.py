"""Heuristic scoring — complexity, effort, risk, price anomaly.

Each score is a float in [0, 1] with 0.5 being the neutral baseline. The
heuristics below encode explainable rules that a procurement analyst can
critique and improve — we deliberately avoid opaque numeric black boxes.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass

from app.models.opportunity import Opportunity


@dataclass
class NoticeScores:
    complexity: float
    effort: float
    risk: float


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def score_notice(opportunity: Opportunity) -> NoticeScores:
    title = opportunity.title or ""
    body = opportunity.object_description or ""
    text = f"{title} {body}".lower()
    length = len(body)

    # Complexity: long notices with many technical terms get higher.
    tech_terms = ("engenharia", "projeto", "arquitetura", "especificação", "catmat", "catser", "bim")
    tech_hits = sum(1 for t in tech_terms if t in text)
    complexity = 0.30 + 0.10 * min(4, tech_hits) + 0.08 * min(4, length // 1500)

    # Effort: number of items + estimated value + number of references.
    item_count = len(opportunity.items or [])
    value = opportunity.estimated_value or 0.0
    value_pressure = math.log10(value + 1) / 9.0  # ~R$ 1B -> 1.0
    effort = 0.25 + 0.05 * min(8, item_count) + 0.5 * _clip01(value_pressure)

    # Risk: short deadlines or dispensa/inexigibilidade modes are riskier.
    risk = 0.30
    if opportunity.modality in {"dispensa", "inexigibilidade"}:
        risk += 0.25
    if opportunity.proposals_close_at and opportunity.published_at:
        delta = (opportunity.proposals_close_at - opportunity.published_at).days
        if delta <= 8:
            risk += 0.25
        elif delta <= 15:
            risk += 0.10
    if "urgente" in text or "emergencial" in text:
        risk += 0.15

    return NoticeScores(
        complexity=_clip01(complexity),
        effort=_clip01(effort),
        risk=_clip01(risk),
    )


def price_anomaly_score(unit_prices: list[float]) -> float:
    """Return a 0..1 anomaly heuristic for a basket of unit prices.

    We compute how dispersed prices are around the median: near-zero dispersion
    is 0.0 (healthy), unusually wide dispersion saturates at 1.0.
    """
    clean = [p for p in unit_prices if p is not None and p > 0]
    if len(clean) < 3:
        return 0.0
    median = statistics.median(clean)
    if median <= 0:
        return 0.0
    stdev = statistics.pstdev(clean)
    cv = stdev / median  # coefficient of variation
    # Map cv=0.2 (healthy) to 0.2, cv=1.5 (wild) to ~0.95
    return _clip01(0.1 + 0.6 * math.log1p(cv))
