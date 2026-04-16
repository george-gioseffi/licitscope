"""AI / heuristic enrichment package."""

from app.enrichment.pipeline import EnrichmentPipeline
from app.enrichment.providers import OfflineProvider, get_provider
from app.enrichment.similarity import SimilarityIndex

__all__ = ["EnrichmentPipeline", "OfflineProvider", "SimilarityIndex", "get_provider"]
