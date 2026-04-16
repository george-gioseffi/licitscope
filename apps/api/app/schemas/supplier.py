"""Supplier DTOs."""

from __future__ import annotations

from pydantic import BaseModel, ConfigDict


class SupplierOut(BaseModel):
    id: int
    tax_id: str
    tax_id_type: str
    name: str
    trade_name: str | None = None
    state: str | None = None
    city: str | None = None
    size: str | None = None
    main_cnae: str | None = None

    model_config = ConfigDict(from_attributes=True)


class SupplierProfile(SupplierOut):
    contract_count: int = 0
    total_contracted_value: float = 0.0
    top_agencies: list[dict] = []
    top_categories: list[dict] = []
