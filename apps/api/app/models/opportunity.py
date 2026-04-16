"""Opportunity — a procurement notice (licitação / edital / dispensa)."""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import JSON, Column, Text, UniqueConstraint
from sqlmodel import Field, Relationship, SQLModel


class Opportunity(SQLModel, table=True):
    __tablename__ = "opportunities"
    __table_args__ = (UniqueConstraint("source", "source_id", name="uq_opportunity_source"),)

    id: int | None = Field(default=None, primary_key=True)

    # Source identity — (source, source_id) is the canonical key across systems.
    source: str = Field(index=True, max_length=64)
    source_id: str = Field(index=True, max_length=128)
    source_url: str | None = Field(default=None, max_length=1024)

    # Public identifiers
    pncp_control_number: str | None = Field(default=None, max_length=64, index=True)
    notice_number: str | None = Field(default=None, max_length=64)

    # Core descriptive fields
    title: str = Field(max_length=1024)
    object_description: str = Field(
        default="",
        sa_column=Column("object_description", Text, nullable=False, server_default=""),
    )

    # Classification
    modality: str = Field(default="outros", max_length=64, index=True)
    status: str = Field(default="published", max_length=64, index=True)
    category: str | None = Field(default=None, max_length=128, index=True)
    subcategory: str | None = Field(default=None, max_length=128)

    # Money
    estimated_value: float | None = Field(default=None, index=True)
    currency: str = Field(default="BRL", max_length=8)

    # Dates
    published_at: datetime | None = Field(default=None, index=True)
    proposals_open_at: datetime | None = Field(default=None)
    proposals_close_at: datetime | None = Field(default=None, index=True)
    session_at: datetime | None = Field(default=None)
    awarded_at: datetime | None = Field(default=None)

    # Geography (denormalized for quick filters)
    state: str | None = Field(default=None, max_length=2, index=True)
    city: str | None = Field(default=None, max_length=128, index=True)

    # Foreign key to agency
    agency_id: int | None = Field(default=None, foreign_key="agencies.id", index=True)
    agency: Optional["Agency"] = Relationship(back_populates="opportunities")  # noqa: F821

    # Full raw metadata as JSON for future-proofing
    raw_metadata: dict | None = Field(default=None, sa_column=Column("raw_metadata", JSON))

    # Audit
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Associations
    items: list["OpportunityItem"] = Relationship(
        back_populates="opportunity",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )
    enrichment: Optional["Enrichment"] = Relationship(  # noqa: F821
        back_populates="opportunity",
        sa_relationship_kwargs={"uselist": False, "cascade": "all, delete-orphan"},
    )
    contracts: list["Contract"] = Relationship(back_populates="opportunity")  # noqa: F821


class OpportunityItem(SQLModel, table=True):
    __tablename__ = "opportunity_items"

    id: int | None = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True)

    lot_number: int | None = Field(default=None)
    item_number: int | None = Field(default=None)
    description: str = Field(max_length=4000)
    unit: str | None = Field(default=None, max_length=64)
    quantity: float | None = Field(default=None)
    unit_reference_price: float | None = Field(default=None)
    total_reference_price: float | None = Field(default=None)

    # Classification (CATMAT / CATSER when available)
    catmat_code: str | None = Field(default=None, max_length=32, index=True)
    catser_code: str | None = Field(default=None, max_length=32, index=True)

    opportunity: Optional["Opportunity"] = Relationship(back_populates="items")

    # Enrichment metadata per item
    enrichment_tags: dict | None = Field(default=None, sa_column=Column("enrichment_tags", JSON))
