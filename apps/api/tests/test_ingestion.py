"""Ingestion service + client smoke tests.

The live PNCP API is deliberately not hit — we exercise the fixtures path
(which is what the demo runs on) plus a respx-mocked live fetch path.
"""

from __future__ import annotations

import json
from pathlib import Path

import respx
from httpx import Response

from app.services.ingestion import IngestionService


def test_ingest_from_fixtures(session, repo_root: Path, monkeypatch):
    monkeypatch.setenv("INGESTION_USE_FIXTURES", "true")
    # ensure config picks up the repo fixtures
    svc = IngestionService(session)
    run = svc.ingest_pncp_window(days_back=1, use_fixtures=True)
    assert run.status in {"success", "partial"}
    assert run.fetched > 0
    # created or updated should be > 0
    assert (run.created + run.updated) > 0


@respx.mock
def test_ingest_from_live_api_with_mock(session, monkeypatch):
    """Hit a mocked PNCP endpoint; confirm parsing + upsert works."""
    sample = json.loads(
        (Path(__file__).resolve().parents[3] / "data-demo" / "pncp" / "opportunities.json").read_text(
            encoding="utf-8"
        )
    )[:3]

    respx.get("https://pncp.gov.br/api/consulta/v1/contratacoes/publicacao").mock(
        return_value=Response(200, json={"data": sample, "totalPaginas": 1})
    )

    # Force live path (use_fixtures=False)
    svc = IngestionService(session)
    run = svc.ingest_pncp_window(days_back=1, modalities=[1], use_fixtures=False)
    # Because we only mocked modality=1, we expect some records were collected
    assert run.fetched > 0
