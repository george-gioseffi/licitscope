"""Agency (órgão público) — the contracting entity."""

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class Agency(SQLModel, table=True):
    __tablename__ = "agencies"

    id: int | None = Field(default=None, primary_key=True)

    # Brazilian unique ids
    cnpj: str = Field(index=True, unique=True, max_length=32)
    name: str = Field(index=True, max_length=512)
    short_name: str | None = Field(default=None, max_length=128)

    # Administrative hierarchy
    sphere: str | None = Field(default=None, max_length=32)  # federal / estadual / municipal
    branch: str | None = Field(default=None, max_length=64)  # executivo / legislativo / judiciario
    parent_cnpj: str | None = Field(default=None, max_length=32, index=True)

    # Location
    state: str | None = Field(default=None, max_length=2, index=True)
    city: str | None = Field(default=None, max_length=128, index=True)
    ibge_code: str | None = Field(default=None, max_length=16)

    # Contact / external
    website: str | None = Field(default=None, max_length=512)

    # Audit
    source: str = Field(default="pncp", max_length=64)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    # Relationships
    opportunities: list["Opportunity"] = Relationship(back_populates="agency")  # noqa: F821
    contracts: list["Contract"] = Relationship(back_populates="agency")  # noqa: F821
