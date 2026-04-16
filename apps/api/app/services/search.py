"""Search + similarity service."""

from __future__ import annotations

from sqlmodel import Session

from app.enrichment.similarity import SimilarityIndex
from app.repositories.enrichment import EnrichmentRepository
from app.repositories.opportunities import OpportunityRepository
from app.schemas.opportunity import OpportunitySummary, SimilarOpportunity
from app.utils.text import tfidf_fingerprint


class SearchService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.opps = OpportunityRepository(session)
        self.enrichments = EnrichmentRepository(session)

    def _build_index(self) -> SimilarityIndex:
        index = SimilarityIndex()
        for enr in self.enrichments.list_fingerprints():
            index.add(enr.opportunity_id, enr.fingerprint or {})
        return index

    def similar_to(self, opportunity_id: int, *, k: int = 5) -> list[SimilarOpportunity]:
        target = self.opps.get(opportunity_id)
        if not target or not target.enrichment or not target.enrichment.fingerprint:
            return []
        index = self._build_index()
        hits = index.top_k(target.enrichment.fingerprint, k=k, exclude=opportunity_id)
        out: list[SimilarOpportunity] = []
        target_kws = set(target.enrichment.keywords or [])
        for hit in hits:
            other = self.opps.get(hit.opportunity_id)
            if not other:
                continue
            other_kws = set((other.enrichment.keywords if other.enrichment else []) or [])
            out.append(
                SimilarOpportunity(
                    opportunity=OpportunitySummary.model_validate(other),
                    score=hit.score,
                    shared_keywords=sorted(target_kws & other_kws)[:8],
                )
            )
        return out

    def semantic_search(self, query: str, *, k: int = 20) -> list[SimilarOpportunity]:
        """Rank opportunities by TF-IDF cosine against the query string."""
        if not query.strip():
            return []
        fp = tfidf_fingerprint(query)
        if not fp:
            return []
        index = self._build_index()
        hits = index.top_k(fp, k=k)
        out: list[SimilarOpportunity] = []
        for hit in hits:
            opp = self.opps.get(hit.opportunity_id)
            if not opp:
                continue
            kws = (opp.enrichment.keywords if opp.enrichment else []) or []
            out.append(
                SimilarOpportunity(
                    opportunity=OpportunitySummary.model_validate(opp),
                    score=hit.score,
                    shared_keywords=kws[:6],
                )
            )
        return out
