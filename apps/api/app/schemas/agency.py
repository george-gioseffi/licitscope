"""Agency DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict


class AgencyOut(BaseModel):
    id: int
    cnpj: str
    name: str
    short_name: str | None = None
    sphere: str | None = None
    branch: str | None = None
    state: str | None = None
    city: str | None = None
    ibge_code: str | None = None
    website: str | None = None
    source: str
    created_at: datetime
    updated_at: datetime

    model_config = ConfigDict(from_attributes=True)


class AgencyProfile(AgencyOut):
    opportunity_count: int = 0
    contract_count: int = 0
    total_contracted_value: float = 0.0
    active_opportunities: int = 0
    top_categories: list[dict] = []
