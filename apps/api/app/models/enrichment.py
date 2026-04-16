"""Enrichment — AI/heuristic derived attributes for an opportunity."""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, Relationship, SQLModel


class Enrichment(SQLModel, table=True):
    __tablename__ = "enrichments"

    id: int | None = Field(default=None, primary_key=True)
    opportunity_id: int = Field(foreign_key="opportunities.id", index=True, unique=True)

    # Human-facing fields
    summary: str | None = Field(
        default=None,
        sa_column=Column("summary", Text, nullable=True),
    )
    bullet_points: list[str] | None = Field(default=None, sa_column=Column("bullet_points", JSON))

    # Extracted structured data
    keywords: list[str] | None = Field(default=None, sa_column=Column("keywords", JSON))
    categories: list[str] | None = Field(default=None, sa_column=Column("categories", JSON))
    entities: dict | None = Field(default=None, sa_column=Column("entities", JSON))
    important_dates: dict | None = Field(default=None, sa_column=Column("important_dates", JSON))

    # Heuristic scoring (0..1). Higher = more effort/complexity/risk.
    complexity_score: float | None = Field(default=None)
    effort_score: float | None = Field(default=None)
    risk_score: float | None = Field(default=None)
    price_anomaly_score: float | None = Field(default=None)

    # Similarity vector fingerprint (TF-IDF hashed vector). Opaque to clients.
    fingerprint: dict | None = Field(default=None, sa_column=Column("fingerprint", JSON))

    # Provenance
    provider: str = Field(default="offline", max_length=32)
    model: str | None = Field(default=None, max_length=128)
    generated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))

    opportunity: Optional["Opportunity"] = Relationship(back_populates="enrichment")  # noqa: F821
