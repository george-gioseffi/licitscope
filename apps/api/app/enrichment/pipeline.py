"""Enrichment pipeline — runs over Opportunity records and writes Enrichment rows.

End-to-end steps:
    1. Normalize text + extract keywords and dates.
    2. Classify against the editable taxonomy.
    3. Compute heuristic complexity/effort/risk scores.
    4. Compute a price-anomaly signal from item reference prices.
    5. Generate a human-readable summary via the configured provider.
    6. Compute a TF-IDF fingerprint used for similarity search.
"""

from __future__ import annotations

import logging
from collections import Counter

from sqlmodel import Session, select

from app.enrichment.providers import Provider, get_provider
from app.enrichment.scoring import price_anomaly_score, score_notice
from app.enrichment.taxonomy import classify
from app.models.opportunity import Opportunity
from app.repositories.enrichment import EnrichmentRepository
from app.utils.dates import extract_dates
from app.utils.text import tfidf_fingerprint, top_keywords

logger = logging.getLogger(__name__)


class EnrichmentPipeline:
    def __init__(self, session: Session, provider: Provider | None = None) -> None:
        self.session = session
        self.provider = provider or get_provider()
        self.repo = EnrichmentRepository(session)

    # ---- public API ---------------------------------------------------------
    def enrich_one(self, opportunity: Opportunity, *, df: dict[str, int] | None = None, n_docs: int = 1) -> None:
        text = f"{opportunity.title}\n{opportunity.object_description or ''}"
        keywords = top_keywords(text, k=10)
        categories = classify(text, top_k=3)
        dates = extract_dates(text)
        summary, bullets = self.provider.summarize(title=opportunity.title, body=opportunity.object_description or "")
        scores = score_notice(opportunity)

        unit_prices = [i.unit_reference_price for i in (opportunity.items or []) if i.unit_reference_price]
        anomaly = price_anomaly_score(unit_prices) if unit_prices else None

        fingerprint = tfidf_fingerprint(text, corpus_df=df, n_docs=n_docs)

        self.repo.upsert(
            opportunity.id,
            {
                "summary": summary,
                "bullet_points": bullets,
                "keywords": keywords,
                "categories": categories,
                "entities": {"dates": dates},
                "important_dates": {"mentioned": dates},
                "complexity_score": scores.complexity,
                "effort_score": scores.effort,
                "risk_score": scores.risk,
                "price_anomaly_score": anomaly,
                "fingerprint": fingerprint,
                "provider": getattr(self.provider, "name", "offline"),
                "model": getattr(self.provider, "model", None),
            },
        )

    def enrich_all(self, *, only_missing: bool = False) -> int:
        stmt = select(Opportunity)
        opportunities: list[Opportunity] = list(self.session.exec(stmt).all())
        if only_missing:
            opportunities = [o for o in opportunities if o.enrichment is None]

        # Build a small corpus-level DF map for TF-IDF weighting.
        df_counter: Counter[str] = Counter()
        for opp in opportunities:
            text = f"{opp.title} {opp.object_description or ''}"
            for tok in set(top_keywords(text, k=50)):
                df_counter[tok] += 1

        n_docs = len(opportunities) or 1
        processed = 0
        for opp in opportunities:
            try:
                self.enrich_one(opp, df=dict(df_counter), n_docs=n_docs)
                processed += 1
            except Exception:  # pragma: no cover - safety net
                logger.exception("enrichment failed for opportunity %s", opp.id)
        self.session.commit()
        return processed
