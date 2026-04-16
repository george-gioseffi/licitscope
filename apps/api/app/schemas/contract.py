"""Contract DTOs."""

from __future__ import annotations

from datetime import datetime

from pydantic import BaseModel, ConfigDict

from app.schemas.agency import AgencyOut
from app.schemas.supplier import SupplierOut


class ContractItemOut(BaseModel):
    id: int
    item_number: int | None = None
    description: str
    unit: str | None = None
    quantity: float | None = None
    unit_price: float | None = None
    total_price: float | None = None
    catmat_code: str | None = None
    catser_code: str | None = None

    model_config = ConfigDict(from_attributes=True)


class ContractOut(BaseModel):
    id: int
    source: str
    source_id: str
    pncp_control_number: str | None = None
    contract_number: str | None = None
    object_description: str
    signed_at: datetime | None = None
    start_at: datetime | None = None
    end_at: datetime | None = None
    total_value: float | None = None
    currency: str = "BRL"
    status: str

    agency: AgencyOut | None = None
    supplier: SupplierOut | None = None

    model_config = ConfigDict(from_attributes=True)


class ContractDetail(ContractOut):
    items: list[ContractItemOut] = []


class PricingIntelligence(BaseModel):
    catmat_or_catser: str
    description_sample: str
    observations: int
    median_unit_price: float
    p25_unit_price: float
    p75_unit_price: float
    min_unit_price: float
    max_unit_price: float
    anomaly_flag: bool = False
