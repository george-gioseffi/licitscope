"""Contract — an awarded procurement contract and its line items."""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import JSON, Column, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Contract(SQLModel, table=True):
    __tablename__ = "contracts"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_contract_source"),)

    id: int | None = Field(default=None, primary_key=True)

    source: str = Field(index=True, max_length=64)
    source_id: str = Field(index=True, max_length=128)
    source_url: str | None = Field(default=None, max_length=1024)
    pncp_control_number: str | None = Field(default=None, max_length=64, index=True)

    # Links to parent opportunity + counterparties
    opportunity_id: int | None = Field(default=None, foreign_key="opportunities.id", index=True)
    agency_id: int | None = Field(default=None, foreign_key="agencies.id", index=True)
    supplier_id: int | None = Field(default=None, foreign_key="suppliers.id", index=True)

    opportunity: Optional["Opportunity"] = Relationship(back_populates="contracts")  # noqa: F821
    agency: Optional["Agency"] = Relationship(back_populates="contracts")  # noqa: F821
    supplier: Optional["Supplier"] = Relationship(back_populates="contracts")  # noqa: F821

    # Contract metadata
    contract_number: str | None = Field(default=None, max_length=64, index=True)
    object_description: str = Field(default="", max_length=8000)

    signed_at: datetime | None = Field(default=None, index=True)
    start_at: datetime | None = Field(default=None)
    end_at: datetime | None = Field(default=None)

    total_value: float | None = Field(default=None, index=True)
    currency: str = Field(default="BRL", max_length=8)

    status: str = Field(default="active", max_length=32, index=True)

    raw_metadata: dict | None = Field(default=None, sa_column=Column("raw_metadata", JSON))

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    items: list["ContractItem"] = Relationship(
        back_populates="contract",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class ContractItem(SQLModel, table=True):
    __tablename__ = "contract_items"

    id: int | None = Field(default=None, primary_key=True)
    contract_id: int = Field(foreign_key="contracts.id", index=True)

    item_number: int | None = Field(default=None)
    description: str = Field(max_length=4000)
    unit: str | None = Field(default=None, max_length=64)
    quantity: float | None = Field(default=None)
    unit_price: float | None = Field(default=None)
    total_price: float | None = Field(default=None)

    catmat_code: str | None = Field(default=None, max_length=32, index=True)
    catser_code: str | None = Field(default=None, max_length=32, index=True)

    contract: Optional["Contract"] = Relationship(back_populates="items")
