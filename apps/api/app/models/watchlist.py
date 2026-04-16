"""Saved-search watchlists + alert events.

In the MVP these are persisted locally and are per-device; authentication
and user accounts are deliberately out of scope (see ROADMAP.md).
"""

from datetime import UTC, datetime
from typing import Optional

from sqlalchemy import JSON, Column
from sqlmodel import Field, Relationship, SQLModel


class Watchlist(SQLModel, table=True):
    __tablename__ = "watchlists"

    id: int | None = Field(default=None, primary_key=True)
    name: str = Field(index=True, max_length=256)
    description: str | None = Field(default=None, max_length=1024)

    # Stored filter expression, matching the /opportunities query params.
    filters: dict = Field(sa_column=Column("filters", JSON, nullable=False))

    # Notification settings
    notify_email: str | None = Field(default=None, max_length=256)
    notify_webhook_url: str | None = Field(default=None, max_length=1024)
    active: bool = Field(default=True)

    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    updated_at: datetime = Field(default_factory=lambda: datetime.now(UTC))
    last_run_at: datetime | None = Field(default=None)

    alerts: list["Alert"] = Relationship(
        back_populates="watchlist",
        sa_relationship_kwargs={"cascade": "all, delete-orphan"},
    )


class Alert(SQLModel, table=True):
    __tablename__ = "alerts"

    id: int | None = Field(default=None, primary_key=True)
    watchlist_id: int = Field(foreign_key="watchlists.id", index=True)
    opportunity_id: int | None = Field(default=None, foreign_key="opportunities.id", index=True)

    headline: str = Field(max_length=512)
    payload: dict | None = Field(default=None, sa_column=Column("payload", JSON))

    fired_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    read: bool = Field(default=False)

    watchlist: Optional["Watchlist"] = Relationship(back_populates="alerts")
