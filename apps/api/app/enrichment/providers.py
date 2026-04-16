"""Provider abstraction: offline heuristics by default, optional LLM hook.

The ``Provider`` interface returns ``(summary, bullet_points)``. The
offline provider is deterministic — the same input always yields the same
output — so CI, tests and demos are reproducible without network access.
A real LLM can be plugged in by implementing ``summarize`` against any
HTTP API (see LLMProvider below).
"""

from __future__ import annotations

import logging
import re
from typing import Protocol

from app.core.config import get_settings
from app.utils.text import top_keywords

logger = logging.getLogger(__name__)


class Provider(Protocol):
    name: str

    def summarize(self, *, title: str, body: str) -> tuple[str, list[str]]:  # pragma: no cover
        ...


# Split on sentence-ending punctuation keeping the delimiter so we don't
# truncate at every period mid-abbreviation (e.g. "S.A.", "art. 5º").
_SENTENCE_SPLIT = re.compile(r"(?<=[.!?])\s+(?=[A-ZÁÉÍÓÚÂÊÔÃÕÇ])")


class OfflineProvider:
    """Deterministic provider that doesn't require network access."""

    name = "offline"
    model = "heuristic/v1"

    def summarize(self, *, title: str, body: str) -> tuple[str, list[str]]:
        cleaned_body = " ".join((body or "").split())
        # Extract the two most informative sentences (first two meaningful ones
        # — procurement notices front-load the core object).
        sentences = [s.strip() for s in _SENTENCE_SPLIT.split(cleaned_body) if len(s.strip()) > 20]
        lede = sentences[0] if sentences else title
        support = sentences[1] if len(sentences) > 1 else ""
        summary = " ".join(p for p in (lede, support) if p).strip()
        if not summary:
            summary = title or "Sem descrição disponível."

        text_lower = (title + " " + cleaned_body).lower()

        bullets: list[str] = []
        kws = top_keywords(f"{title}. {cleaned_body}", k=6)
        if kws:
            bullets.append("Palavras-chave: " + ", ".join(kws))

        if "pregão" in text_lower or "pregao" in text_lower:
            bullets.append("Modalidade identificada: pregão eletrônico ou presencial.")
        if "credenciamento" in text_lower:
            bullets.append("Processo estruturado como credenciamento — múltiplos fornecedores.")
        if "dispensa" in text_lower:
            bullets.append("Dispensa de licitação — atenção aos critérios legais.")
        if any(
            term in text_lower for term in ("urgente", "emergencial", "emergência", "emergencia")
        ):
            bullets.append("Linguagem de urgência detectada — prazos potencialmente curtos.")
        if "lote" in text_lower:
            bullets.append("Processo estruturado em lotes.")
        if "registro de preços" in text_lower or "registro de precos" in text_lower:
            bullets.append("Sistema de registro de preços — contratação parcelada.")
        if "menor preço" in text_lower or "menor preco" in text_lower:
            bullets.append("Critério de julgamento: menor preço.")
        if not bullets:
            bullets.append("Nenhum sinal adicional detectado pelo resumo offline.")

        # Cap length so UI stays predictable.
        return summary[:800], bullets[:5]


class LLMProvider:
    """Skeleton for an LLM-backed provider.

    This intentionally only *declares* the integration surface. A concrete
    implementation can call Anthropic, OpenAI, or any other HTTP LLM; we keep
    that behind a provider name so the CI/demo path never needs network.
    """

    def __init__(self, provider: str, api_key: str, model: str) -> None:
        self.name = f"llm/{provider}"
        self.model = model
        self._api_key = api_key

    def summarize(self, *, title: str, body: str) -> tuple[str, list[str]]:
        raise NotImplementedError(
            "LLMProvider is a placeholder. Set ENRICHMENT_MODE=offline or implement "
            "the .summarize() method with your preferred provider SDK."
        )


def get_provider() -> Provider:
    """Return the currently configured enrichment provider."""
    settings = get_settings()
    if settings.enrichment_mode == "llm" and settings.llm_provider and settings.llm_api_key:
        logger.info("Using LLM provider: %s", settings.llm_provider)
        return LLMProvider(
            provider=settings.llm_provider,
            api_key=settings.llm_api_key,
            model=settings.llm_model or "default",
        )
    return OfflineProvider()
