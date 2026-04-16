"""Tests for request-id middleware and uniform error envelope."""

from __future__ import annotations

import re

UUID_HEX = re.compile(r"^[0-9a-f]{32}$")


def test_request_id_is_generated_when_client_omits_it(client):
    r = client.get("/health/ready")
    assert r.status_code == 200
    rid = r.headers.get("x-request-id")
    assert rid and UUID_HEX.match(rid), f"expected uuid hex, got {rid!r}"


def test_request_id_is_echoed_back_when_client_provides_it(client):
    provided = "abc123-client-supplied"
    r = client.get("/health/ready", headers={"X-Request-ID": provided})
    assert r.status_code == 200
    assert r.headers.get("x-request-id") == provided


def test_404_returns_uniform_error_envelope(client):
    r = client.get("/opportunities/99999999")
    assert r.status_code == 404
    body = r.json()
    assert body["type"] == "http_404"
    assert body["error"] == "Opportunity not found"
    assert body["request_id"]


def test_validation_error_returns_uniform_envelope(client):
    # q must be min_length=2 in the search router
    r = client.get("/search?q=a")
    assert r.status_code == 422
    body = r.json()
    assert body["type"] == "validation_error"
    assert isinstance(body["details"], list)
    assert body["request_id"]
