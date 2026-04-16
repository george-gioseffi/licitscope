"""Ingestion-run bookkeeping + raw payload snapshots."""

from __future__ import annotations

from datetime import UTC, datetime

from sqlalchemy import JSON, Column, Text
from sqlmodel import Field, SQLModel


class IngestionRun(SQLModel, table=True):
    __tablename__ = "ingestion_runs"

    id: int | None = Field(default=None, primary_key=True)
    source: str = Field(index=True, max_length=64)
    scope: str = Field(default="opportunities", max_length=64)  # opportunities / contracts / ...
    status: str = Field(default="running", max_length=32, index=True)

    started_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    finished_at: datetime | None = Field(default=None)

    fetched: int = Field(default=0)
    created: int = Field(default=0)
    updated: int = Field(default=0)
    skipped: int = Field(default=0)
    failed: int = Field(default=0)

    notes: str | None = Field(default=None, sa_column=Column("notes", Text, nullable=True))
    params: dict | None = Field(default=None, sa_column=Column("params", JSON))


class RawPayload(SQLModel, table=True):
    """Raw, unmodified JSON payload as received from a source.

    We keep the original record so any downstream normalization bug can be
    re-run without hitting the external API again. ``content_hash`` is used
    for idempotent dedup.
    """

    __tablename__ = "raw_payloads"

    id: int | None = Field(default=None, primary_key=True)
    source: str = Field(index=True, max_length=64)
    kind: str = Field(index=True, max_length=64)  # opportunity / contract / agency / ...
    source_id: str = Field(index=True, max_length=256)
    content_hash: str = Field(index=True, max_length=64)
    payload: dict = Field(sa_column=Column("payload", JSON, nullable=False))
    fetched_at: datetime = Field(default_factory=lambda: datetime.now(UTC), index=True)
    ingestion_run_id: int | None = Field(default=None, foreign_key="ingestion_runs.id", index=True)
