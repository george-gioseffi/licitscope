"""Smoke-test the REST API end-to-end with seeded fixtures."""

from __future__ import annotations

import json
from pathlib import Path

import pytest

from app.enrichment.pipeline import EnrichmentPipeline
from app.models.enums import SourceName
from app.repositories.agencies import AgencyRepository
from app.repositories.opportunities import OpportunityRepository
from app.repositories.suppliers import SupplierRepository
from app.utils.dates import parse_date

DATE_FIELDS = {
    "published_at",
    "proposals_open_at",
    "proposals_close_at",
    "session_at",
    "awarded_at",
    "signed_at",
    "start_at",
    "end_at",
}


def _coerce(payload: dict) -> dict:
    for k in list(payload.keys()):
        if k in DATE_FIELDS and isinstance(payload[k], str):
            payload[k] = parse_date(payload[k])
    return payload


@pytest.fixture()
def seeded(session, repo_root: Path):
    base = repo_root / "data-demo"
    agencies = json.loads((base / "agencies.json").read_text(encoding="utf-8"))
    suppliers = json.loads((base / "suppliers.json").read_text(encoding="utf-8"))
    opportunities = json.loads((base / "opportunities.json").read_text(encoding="utf-8"))

    a_repo = AgencyRepository(session)
    s_repo = SupplierRepository(session)
    o_repo = OpportunityRepository(session)

    for p in agencies:
        a_repo.upsert(p)
    for p in suppliers:
        s_repo.upsert(p)
    for p in opportunities[:20]:  # trim for fast tests
        p = dict(p)
        cnpj = p.pop("agency_cnpj", None)
        items = p.pop("items", [])
        if cnpj:
            ag = a_repo.get_by_cnpj(cnpj)
            if ag:
                p["agency_id"] = ag.id
        p.setdefault("source", SourceName.FIXTURE.value)
        _coerce(p)
        o_repo.upsert(p, items=items)
    session.commit()

    EnrichmentPipeline(session).enrich_all()
    session.commit()
    return True


def test_health_live(client):
    r = client.get("/health/live")
    assert r.status_code == 200
    assert r.json() == {"status": "ok"}


def test_health_ready(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    body = r.json()
    assert body["status"] in {"ok", "degraded"}
    assert body["app"] == "LicitScope"


def test_opportunities_feed(client, seeded):
    r = client.get("/opportunities?page_size=5")
    assert r.status_code == 200
    body = r.json()
    assert body["meta"]["total"] >= 1
    assert len(body["items"]) <= 5
    first = body["items"][0]
    for field in ("id", "title", "modality", "status", "agency"):
        assert field in first


def test_opportunity_detail_and_similar(client, seeded):
    r = client.get("/opportunities?page_size=1")
    oid = r.json()["items"][0]["id"]

    detail = client.get(f"/opportunities/{oid}")
    assert detail.status_code == 200
    payload = detail.json()
    assert payload["id"] == oid
    assert "items" in payload
    assert "enrichment" in payload

    similar = client.get(f"/opportunities/{oid}/similar?k=3")
    assert similar.status_code == 200
    assert isinstance(similar.json(), list)


def test_opportunity_filter_by_state(client, seeded):
    r = client.get("/opportunities?state=SP&page_size=100")
    assert r.status_code == 200
    for item in r.json()["items"]:
        assert item.get("state") == "SP"


def test_facets_contain_expected_dimensions(client, seeded):
    r = client.get("/opportunities/facets")
    assert r.status_code == 200
    body = r.json()
    for key in ("modalities", "statuses", "categories", "states", "sources"):
        assert key in body
        assert isinstance(body[key], list)


def test_analytics_overview(client, seeded):
    r = client.get("/analytics/overview")
    assert r.status_code == 200
    body = r.json()
    assert "kpis" in body and len(body["kpis"]) > 0
    assert isinstance(body["by_state"], list)
    assert isinstance(body["by_category"], list)


def test_semantic_search(client, seeded):
    r = client.get("/search?q=medicamentos&k=5")
    assert r.status_code == 200
    hits = r.json()
    assert isinstance(hits, list)
    # at least one hit should mention "saúde" or "medicamento" in title
    if hits:
        kws = " ".join(h["opportunity"]["title"].lower() for h in hits)
        assert any(word in kws for word in ["medicamento", "saude", "hemodial", "unidade básica"])


def test_meta_endpoints(client):
    for path in ("/meta/modalities", "/meta/statuses", "/meta/sources"):
        r = client.get(path)
        assert r.status_code == 200
        assert len(r.json()) > 0


def test_root(client):
    r = client.get("/")
    assert r.status_code == 200
    assert r.json()["name"] == "LicitScope"
