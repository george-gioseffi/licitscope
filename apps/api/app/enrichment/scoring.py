"""Heuristic scoring for procurement notices.

Scores are floats in ``[0, 1]`` produced by hand-written, explainable rules.
Every rule that fires adds both a weight to the score and a short
human-readable reason — both are surfaced to the API so users can see
*why* a notice scored the way it did. We deliberately avoid opaque black
boxes here because risk signals in public procurement must be auditable.
"""

from __future__ import annotations

import math
import statistics
from dataclasses import dataclass, field

from app.models.opportunity import Opportunity

# ---------------------------------------------------------------------------
# Rule lexicons (editable — this file is the source of truth)
# ---------------------------------------------------------------------------

TECH_TERMS: tuple[str, ...] = (
    "engenharia",
    "projeto",
    "arquitetura",
    "especificação",
    "especificacao",
    "catmat",
    "catser",
    "bim",
    "integração",
    "interoperabilidade",
    "homologação",
    "homologacao",
    "ndr",
    "sla",
    "arquitetura tecnológica",
    "alta disponibilidade",
    "auditoria",
)
URGENCY_TERMS: tuple[str, ...] = (
    "urgente",
    "emergencial",
    "emergência",
    "emergencia",
    "calamidade",
)
HIGH_RISK_MODALITIES = frozenset({"dispensa", "inexigibilidade"})


# ---------------------------------------------------------------------------
# Public types
# ---------------------------------------------------------------------------


@dataclass
class NoticeScores:
    complexity: float
    effort: float
    risk: float
    rationale: dict[str, list[str]] = field(default_factory=dict)


def _clip01(x: float) -> float:
    return max(0.0, min(1.0, x))


def _contains_any(text: str, terms) -> list[str]:
    return [t for t in terms if t in text]


# ---------------------------------------------------------------------------
# Scoring
# ---------------------------------------------------------------------------


def score_notice(opportunity: Opportunity) -> NoticeScores:
    title = opportunity.title or ""
    body = opportunity.object_description or ""
    text = f"{title} {body}".lower()
    length = len(body)
    reasons: dict[str, list[str]] = {"complexity": [], "effort": [], "risk": []}

    # -- complexity --------------------------------------------------------
    # "how much reading and how much technical depth does this notice carry?"
    complexity = 0.30
    tech_hits = _contains_any(text, TECH_TERMS)
    if tech_hits:
        bonus = 0.10 * min(4, len(tech_hits))
        complexity += bonus
        reasons["complexity"].append(
            f"{len(tech_hits)} termo(s) técnico(s) detectado(s) (+{bonus:.2f})"
        )
    length_buckets = min(4, length // 1500)
    if length_buckets:
        bonus = 0.08 * length_buckets
        complexity += bonus
        reasons["complexity"].append(f"objeto longo (+{bonus:.2f})")
    if opportunity.items and len(opportunity.items) >= 5:
        complexity += 0.10
        reasons["complexity"].append(f"{len(opportunity.items)} itens na licitação (+0.10)")

    # -- effort ------------------------------------------------------------
    # "how expensive / how many things does the fornecedor have to handle?"
    item_count = len(opportunity.items or [])
    value = opportunity.estimated_value or 0.0
    effort = 0.25
    if item_count:
        bonus = 0.05 * min(8, item_count)
        effort += bonus
        reasons["effort"].append(f"{item_count} item(ns) (+{bonus:.2f})")
    if value > 0:
        value_pressure = math.log10(value + 1) / 9.0  # ~R$ 1B saturates at 1.0
        bonus = 0.5 * _clip01(value_pressure)
        effort += bonus
        reasons["effort"].append(f"valor estimado alto (+{bonus:.2f})")

    # -- risk --------------------------------------------------------------
    # "how likely is this notice to be badly specified, rushed, or irregular?"
    risk = 0.30
    if opportunity.modality in HIGH_RISK_MODALITIES:
        risk += 0.25
        reasons["risk"].append(f"modalidade {opportunity.modality} (+0.25)")

    if opportunity.proposals_close_at and opportunity.published_at:
        delta_days = (opportunity.proposals_close_at - opportunity.published_at).days
        if delta_days <= 5:
            risk += 0.30
            reasons["risk"].append(f"prazo muito curto ({delta_days}d) (+0.30)")
        elif delta_days <= 8:
            risk += 0.20
            reasons["risk"].append(f"prazo curto ({delta_days}d) (+0.20)")
        elif delta_days <= 15:
            risk += 0.10
            reasons["risk"].append(f"prazo apertado ({delta_days}d) (+0.10)")

    urgency_hits = _contains_any(text, URGENCY_TERMS)
    if urgency_hits:
        risk += 0.15
        reasons["risk"].append(f"linguagem de urgência: {urgency_hits[0]} (+0.15)")

    # Under-specified notices are risky: items but no reference prices
    if item_count and all((i.unit_reference_price or 0) == 0 for i in (opportunity.items or [])):
        risk += 0.10
        reasons["risk"].append("itens sem preço de referência (+0.10)")

    return NoticeScores(
        complexity=_clip01(complexity),
        effort=_clip01(effort),
        risk=_clip01(risk),
        rationale={k: v for k, v in reasons.items() if v},
    )


# ---------------------------------------------------------------------------
# Pricing anomaly — robust to outliers
# ---------------------------------------------------------------------------


def price_anomaly_score(unit_prices: list[float]) -> float:
    """Return a 0..1 anomaly heuristic for a basket of unit prices.

    Uses an IQR-based coefficient of dispersion (robust to outliers) instead
    of standard deviation, because procurement data routinely contains a
    handful of extreme values that would dominate ``stdev``.
    """
    clean = sorted(p for p in unit_prices if p is not None and p > 0)
    if len(clean) < 3:
        return 0.0
    median = statistics.median(clean)
    if median <= 0:
        return 0.0

    # IQR / median is a robust dispersion measure.
    if len(clean) >= 4:
        q1 = statistics.quantiles(clean, n=4)[0]
        q3 = statistics.quantiles(clean, n=4)[2]
        iqr = q3 - q1
        dispersion = iqr / median
    else:
        dispersion = statistics.pstdev(clean) / median

    # dispersion ~0.1 (healthy) -> low; ~1.5+ (wild) -> saturates near 0.95
    return _clip01(0.1 + 0.6 * math.log1p(dispersion))
