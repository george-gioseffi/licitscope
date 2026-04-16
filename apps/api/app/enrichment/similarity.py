"""In-process similarity index using hashed TF-IDF fingerprints."""

from __future__ import annotations

from dataclasses import dataclass

from app.utils.text import cosine


@dataclass
class SimilarityHit:
    opportunity_id: int
    score: float


class SimilarityIndex:
    """Micro-ranker. We store fingerprints in-process for the lifetime of a
    single API call or script run; persistence happens via the Enrichment
    table (``fingerprint`` column)."""

    def __init__(self) -> None:
        self._by_id: dict[int, dict[str, float]] = {}

    def add(self, opportunity_id: int, fingerprint: dict[str, float] | None) -> None:
        if fingerprint:
            self._by_id[opportunity_id] = fingerprint

    def top_k(self, query: dict[str, float], *, k: int = 5, exclude: int | None = None) -> list[SimilarityHit]:
        results: list[SimilarityHit] = []
        for oid, vec in self._by_id.items():
            if exclude is not None and oid == exclude:
                continue
            score = cosine(query, vec)
            if score > 0:
                results.append(SimilarityHit(opportunity_id=oid, score=round(score, 4)))
        results.sort(key=lambda r: r.score, reverse=True)
        return results[:k]

    @property
    def size(self) -> int:
        return len(self._by_id)
