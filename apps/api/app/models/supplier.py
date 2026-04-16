"""Supplier (fornecedor) — awarded vendor."""

from datetime import UTC, datetime

from sqlmodel import Field, Relationship, SQLModel


class Supplier(SQLModel, table=True):
    __tablename__ = "suppliers"

    id: int | None = Field(default=None, primary_key=True)

    # Brazilian unique ids
    tax_id: str = Field(index=True, unique=True, max_length=32)  # CNPJ or CPF
    tax_id_type: str = Field(default="CNPJ", max_length=8)
    name: str = Field(index=True, max_length=512)
    trade_name: str | None = Field(default=None, max_length=512)

    # Location
    state: str | None = Field(default=None, max_length=2, index=True)
    city: str | None = Field(default=None, max_length=128, index=True)

    # Classification
    size: str | None = Field(default=None, max_length=32)  # ME / EPP / grande porte
    main_cnae: str | None = Field(default=None, max_length=16, index=True)

    source: str = Field(default="pncp", max_length=64)
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    contracts: list["Contract"] = Relationship(back_populates="supplier")  # noqa: F821
