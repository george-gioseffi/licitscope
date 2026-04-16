"""Opportunity-related DTOs."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from pydantic import BaseModel, ConfigDict, Field


class AgencyRef(BaseModel):
    id: int
    cnpj: str
    name: str
    short_name: str | None = None
    state: str | None = None
    city: str | None = None
    sphere: str | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityItemOut(BaseModel):
    id: int
    lot_number: int | None = None
    item_number: int | None = None
    description: str
    unit: str | None = None
    quantity: float | None = None
    unit_reference_price: float | None = None
    total_reference_price: float | None = None
    catmat_code: str | None = None
    catser_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class EnrichmentOut(BaseModel):
    summary: str | None = None
    bullet_points: list[str] | None = None
    keywords: list[str] | None = None
    categories: list[str] | None = None
    entities: dict | None = None
    important_dates: dict | None = None
    complexity_score: float | None = None
    effort_score: float | None = None
    risk_score: float | None = None
    price_anomaly_score: float | None = None
    provider: str = "offline"
    model: str | None = None
    generated_at: datetime | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunitySummary(BaseModel):
    """Lightweight entry for list views."""

    id: int
    source: str
    source_id: str
    pncp_control_number: str | None = None
    title: str
    modality: str
    status: str
    category: str | None = None
    estimated_value: float | None = None
    currency: str = "BRL"
    state: str | None = None
    city: str | None = None
    published_at: datetime | None = None
    proposals_close_at: datetime | None = None
    agency: AgencyRef | None = None
    complexity_score: float | None = None
    risk_score: float | None = None

    model_config = ConfigDict(from_attributes=True)


class OpportunityOut(OpportunitySummary):
    object_description: str
    subcategory: str | None = None
    notice_number: str | None = None
    source_url: str | None = None
    proposals_open_at: datetime | None = None
    session_at: datetime | None = None
    awarded_at: datetime | None = None


class OpportunityDetail(OpportunityOut):
    items: list[OpportunityItemOut] = Field(default_factory=list)
    enrichment: EnrichmentOut | None = None
    raw_metadata: dict | None = None


class OpportunityFilters(BaseModel):
    q: str | None = None
    state: str | None = None
    city: str | None = None
    agency_id: int | None = None
    modality: str | None = None
    status: str | None = None
    category: str | None = None
    source: str | None = None
    min_value: float | None = None
    max_value: float | None = None
    published_from: datetime | None = None
    published_to: datetime | None = None
    closes_from: datetime | None = None
    closes_to: datetime | None = None
    sort: str = "published_at_desc"


class SimilarOpportunity(BaseModel):
    opportunity: OpportunitySummary
    score: float
    shared_keywords: list[str] = Field(default_factory=list)


class Facet(BaseModel):
    value: str
    label: str
    count: int


class OpportunityFacets(BaseModel):
    modalities: list[Facet] = Field(default_factory=list)
    statuses: list[Facet] = Field(default_factory=list)
    categories: list[Facet] = Field(default_factory=list)
    states: list[Facet] = Field(default_factory=list)
    sources: list[Facet] = Field(default_factory=list)


class AnalyticsKPI(BaseModel):
    label: str
    value: float
    trend: float | None = None
    suffix: str | None = None
    description: str | None = None


class TimeSeriesPoint(BaseModel):
    date: str
    count: int
    value: float = 0.0


class CategoryBreakdown(BaseModel):
    category: str
    count: int
    total_value: float = 0.0


class GeoBreakdown(BaseModel):
    state: str
    count: int
    total_value: float = 0.0


class DashboardOverview(BaseModel):
    kpis: list[AnalyticsKPI]
    recent: list[OpportunitySummary]
    published_per_day: list[TimeSeriesPoint]
    by_category: list[CategoryBreakdown]
    by_state: list[GeoBreakdown]
    by_modality: list[CategoryBreakdown]
    top_agencies: list[dict[str, Any]]
    source_health: list[dict[str, Any]]
