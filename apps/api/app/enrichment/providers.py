"""Provider abstraction: offline heuristics by default, optional LLM hook.

The `Provider` interface returns ``(summary, bullet_points)``. Offline
generation is deterministic so demos are reproducible. A real LLM can be
plugged in by implementing ``summarize`` against any HTTP API.
"""

from __future__ import annotations

import logging
from typing import Protocol

from app.core.config import get_settings
from app.utils.text import top_keywords

logger = logging.getLogger(__name__)


class Provider(Protocol):
    name: str

    def summarize(self, *, title: str, body: str) -> tuple[str, list[str]]:  # pragma: no cover
        ...


class OfflineProvider:
    """Deterministic provider that doesn't require network access."""

    name = "offline"
    model = "heuristic/v1"

    def summarize(self, *, title: str, body: str) -> tuple[str, list[str]]:
        # Extract the first two sentences as a summary scaffolding.
        sentences = [s.strip() for s in body.replace("\n", " ").split(".") if len(s.strip()) > 20]
        lede = (sentences[0] + ".") if sentences else title
        second = (sentences[1] + ".") if len(sentences) > 1 else ""
        summary = f"{lede} {second}".strip()

        # Bullets: top keywords + key signals
        kws = top_keywords(f"{title}. {body}", k=6)
        bullets: list[str] = []
        if kws:
            bullets.append("Palavras-chave: " + ", ".join(kws))
        if "pregão" in body.lower() or "pregao" in body.lower():
            bullets.append("Modalidade identificada: pregão.")
        if "urgente" in body.lower() or "emergencial" in body.lower():
            bullets.append("Sinal de urgência detectado no texto.")
        if "lote" in body.lower():
            bullets.append("Processo estruturado em lotes.")
        if not bullets:
            bullets.append("Sem sinais adicionais extraídos pelo modo offline.")
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
