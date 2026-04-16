"""Watchlist CRUD + validation tests."""

from __future__ import annotations


def test_watchlist_crud_happy_path(client):
    body = {
        "name": "TI SP",
        "description": "Tecnologia em São Paulo",
        "filters": {"q": "software", "state": "SP", "sort": "published_at_desc"},
    }
    r = client.post("/watchlists", json=body)
    assert r.status_code == 201, r.text
    created = r.json()
    assert created["name"] == "TI SP"
    wid = created["id"]

    r = client.get("/watchlists")
    assert r.status_code == 200
    assert any(w["id"] == wid for w in r.json())

    r = client.post(f"/watchlists/{wid}/run")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.get(f"/watchlists/{wid}/alerts")
    assert r.status_code == 200
    assert isinstance(r.json(), list)

    r = client.delete(f"/watchlists/{wid}")
    assert r.status_code == 204


def test_watchlist_rejects_empty_name(client):
    r = client.post(
        "/watchlists",
        json={"name": "   ", "filters": {"q": "software"}},
    )
    assert r.status_code == 422


def test_watchlist_rejects_non_discriminating_filters(client):
    """A filter that would match every notice is rejected — otherwise the
    watchlist would fire an alert on every ingestion run."""
    r = client.post(
        "/watchlists",
        json={"name": "Everything", "filters": {"sort": "published_at_desc"}},
    )
    assert r.status_code == 422
    body = r.json()
    assert body["type"] == "validation_error"


def test_watchlist_run_404_has_envelope(client):
    r = client.post("/watchlists/99999/run")
    assert r.status_code == 404
    body = r.json()
    assert body["type"] == "http_404"
    assert body["request_id"]


def test_watchlist_trims_whitespace_in_name(client):
    r = client.post(
        "/watchlists",
        json={"name": "  Saúde MG  ", "filters": {"state": "MG"}},
    )
    assert r.status_code == 201
    assert r.json()["name"] == "Saúde MG"
