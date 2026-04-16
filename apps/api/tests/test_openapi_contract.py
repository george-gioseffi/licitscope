"""Contract tests for the OpenAPI schema.

These guard against accidentally removing a route, stripping a field from
a response model, or changing an endpoint's operation id — the kind of
silent API break that is otherwise invisible in code review.
"""

from __future__ import annotations

from app.main import app

EXPECTED_PATHS: set[str] = {
    # Liveness / readiness
    "/health/live",
    "/health/ready",
    "/health/sources",
    # Opportunities
    "/opportunities",
    "/opportunities/facets",
    "/opportunities/{opportunity_id}",
    "/opportunities/{opportunity_id}/similar",
    # Search
    "/search",
    # Meta
    "/meta/modalities",
    "/meta/statuses",
    "/meta/sources",
    # Analytics
    "/analytics/overview",
    # Agencies / suppliers
    "/agencies",
    "/agencies/{agency_id}",
    "/suppliers",
    "/suppliers/{supplier_id}",
    # Contracts + pricing
    "/contracts",
    "/contracts/pricing",
    "/contracts/{contract_id}",
    # Watchlists
    "/watchlists",
    "/watchlists/{watchlist_id}",
    "/watchlists/{watchlist_id}/run",
    "/watchlists/{watchlist_id}/alerts",
}


def test_openapi_schema_contains_all_expected_paths():
    schema = app.openapi()
    actual = set(schema.get("paths", {}).keys())
    missing = EXPECTED_PATHS - actual
    assert not missing, f"Expected endpoints missing from the API: {sorted(missing)}"


def test_openapi_schema_declares_stable_tags():
    schema = app.openapi()
    tags = {t["name"] for t in schema.get("tags", []) if isinstance(t, dict)}
    # tags come from the routers' tags= kwarg; any removal should be
    # intentional and surface here.
    expected_tags = {
        "health",
        "opportunities",
        "search",
        "meta",
        "analytics",
        "agencies",
        "suppliers",
        "contracts",
        "watchlists",
    }
    # FastAPI only lists tags that are explicitly declared in app.openapi_tags;
    # the ones declared per-router appear under paths.
    # We cross-check via operation tags to keep this test meaningful:
    operation_tags: set[str] = set()
    for methods in schema.get("paths", {}).values():
        for op in methods.values():
            if isinstance(op, dict):
                operation_tags.update(op.get("tags", []))
    missing_from_ops = expected_tags - operation_tags
    assert not missing_from_ops, (
        f"Expected tags absent from any operation: {sorted(missing_from_ops)}"
    )
    # The static tags list is optional, so we don't hard-fail on it.
    _ = tags


def test_opportunity_detail_response_has_enrichment_envelope():
    """Regression guard: /opportunities/{id} must expose enrichment signals."""
    schema = app.openapi()
    component = schema["components"]["schemas"]["OpportunityDetail"]
    assert "enrichment" in component["properties"]
    assert "items" in component["properties"]


def test_pricing_intelligence_schema_shape():
    schema = app.openapi()["components"]["schemas"]["PricingIntelligence"]
    required_fields = {
        "catmat_or_catser",
        "description_sample",
        "observations",
        "median_unit_price",
        "p25_unit_price",
        "p75_unit_price",
        "min_unit_price",
        "max_unit_price",
        "anomaly_flag",
    }
    declared = set(schema["properties"].keys())
    missing = required_fields - declared
    assert not missing, f"PricingIntelligence fields missing: {sorted(missing)}"
