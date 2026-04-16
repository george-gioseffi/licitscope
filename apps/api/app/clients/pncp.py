"""PNCP (Portal Nacional de Contratações Públicas) HTTP client.

Documentation reference: https://pncp.gov.br/api/consulta/swagger-ui/index.html

Public, no-key endpoints we care about:
  - /v1/contratacoes/publicacao                 (notices by publication date)
  - /v1/contratos                               (signed contracts)
  - /v1/contratacoes/{cnpj}/{ano}/{seq}         (single notice)
  - /v1/orgaos/{cnpj}                           (agency lookup)

We implement a small subset focused on what the rest of the system needs,
with retries, pagination, and idempotent upsert-friendly parsing. If the
real endpoints are unavailable or rate-limited, callers can fall back to
the fixtures under ``data-demo/`` (see :mod:`app.services.ingestion`).
"""

from __future__ import annotations

import logging
from collections.abc import Iterator
from typing import Any

import httpx
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from app.core.config import get_settings

logger = logging.getLogger(__name__)


class PNCPClient:
    """Thin HTTP client over the PNCP consulta API."""

    def __init__(self, base_url: str | None = None, timeout: int | None = None) -> None:
        settings = get_settings()
        self.base_url = (base_url or settings.pncp_base_url).rstrip("/")
        self.timeout = timeout or settings.ingestion_request_timeout
        self._client = httpx.Client(
            base_url=self.base_url,
            timeout=self.timeout,
            headers={
                "Accept": "application/json",
                "User-Agent": "LicitScope/0.1 (+https://github.com/licitscope)",
            },
        )

    # ---- lifecycle ----------------------------------------------------------
    def close(self) -> None:
        self._client.close()

    def __enter__(self) -> PNCPClient:
        return self

    def __exit__(self, *exc: Any) -> None:
        self.close()

    # ---- low-level request with retry --------------------------------------
    @retry(
        reraise=True,
        stop=stop_after_attempt(3),
        wait=wait_exponential(multiplier=1, min=1, max=8),
        retry=retry_if_exception_type((httpx.TimeoutException, httpx.TransportError)),
    )
    def _get(self, path: str, params: dict | None = None) -> dict:
        logger.debug("GET %s params=%s", path, params)
        resp = self._client.get(path, params=params)
        resp.raise_for_status()
        return resp.json() if resp.content else {}

    # ---- public endpoints ---------------------------------------------------
    def list_published_notices(
        self,
        *,
        data_inicial: str,
        data_final: str,
        codigo_modalidade: int | None = None,
        uf: str | None = None,
        page_size: int = 50,
        max_pages: int = 5,
    ) -> Iterator[dict]:
        """Yield notices published within ``[data_inicial, data_final]`` (YYYYMMDD).

        This paginates transparently up to ``max_pages``. PNCP returns 400 if
        the range is too wide or modalidade missing — callers should batch.
        """
        page = 1
        while page <= max_pages:
            params: dict[str, Any] = {
                "dataInicial": data_inicial,
                "dataFinal": data_final,
                "pagina": page,
                "tamanhoPagina": page_size,
            }
            if codigo_modalidade is not None:
                params["codigoModalidadeContratacao"] = codigo_modalidade
            if uf:
                params["uf"] = uf

            data = self._get("/v1/contratacoes/publicacao", params=params)

            records = data.get("data") or data.get("content") or []
            if not records:
                return
            yield from records

            total_pages = int(
                data.get("totalPaginas") or data.get("totalPages") or 1
            )
            if page >= total_pages:
                return
            page += 1

    def get_notice(self, cnpj: str, ano: int, sequencial: int) -> dict:
        path = f"/v1/orgaos/{cnpj}/compras/{ano}/{sequencial}"
        return self._get(path)

    def list_contracts(
        self,
        *,
        data_inicial: str,
        data_final: str,
        page_size: int = 50,
        max_pages: int = 5,
    ) -> Iterator[dict]:
        page = 1
        while page <= max_pages:
            params = {
                "dataInicial": data_inicial,
                "dataFinal": data_final,
                "pagina": page,
                "tamanhoPagina": page_size,
            }
            data = self._get("/v1/contratos/publicacao", params=params)
            records = data.get("data") or data.get("content") or []
            if not records:
                return
            yield from records
            total_pages = int(
                data.get("totalPaginas") or data.get("totalPages") or 1
            )
            if page >= total_pages:
                return
            page += 1
