"""Ingestion run + raw payload repository."""

from __future__ import annotations

import hashlib
import json
from datetime import UTC, datetime

from sqlmodel import Session, select

from app.models.ingestion import IngestionRun, RawPayload


def _hash_payload(payload: dict) -> str:
    blob = json.dumps(payload, sort_keys=True, default=str).encode("utf-8")
    return hashlib.sha256(blob).hexdigest()


class IngestionRepository:
    def __init__(self, session: Session) -> None:
        self.session = session

    # --- runs ----------------------------------------------------------------
    def start_run(self, *, source: str, scope: str, params: dict | None = None) -> IngestionRun:
        run = IngestionRun(source=source, scope=scope, params=params or {}, status="running")
        self.session.add(run)
        self.session.flush()
        return run

    def finish_run(self, run: IngestionRun, *, status: str, notes: str | None = None) -> None:
        run.finished_at = datetime.now(UTC)
        run.status = status
        if notes:
            run.notes = notes
        self.session.add(run)
        self.session.flush()

    def list_runs(self, *, limit: int = 50) -> list[IngestionRun]:
        stmt = select(IngestionRun).order_by(IngestionRun.started_at.desc()).limit(limit)  # type: ignore[attr-defined]
        return list(self.session.exec(stmt).all())

    def last_run(self, *, source: str) -> IngestionRun | None:
        stmt = (
            select(IngestionRun)
            .where(IngestionRun.source == source)
            .order_by(IngestionRun.started_at.desc())  # type: ignore[attr-defined]
        )
        return self.session.exec(stmt).first()

    # --- raw payloads --------------------------------------------------------
    def save_payload(
        self,
        *,
        source: str,
        kind: str,
        source_id: str,
        payload: dict,
        run: IngestionRun | None = None,
    ) -> RawPayload:
        content_hash = _hash_payload(payload)
        existing = self.session.exec(
            select(RawPayload).where(
                RawPayload.source == source,
                RawPayload.kind == kind,
                RawPayload.source_id == source_id,
                RawPayload.content_hash == content_hash,
            )
        ).first()
        if existing:
            return existing

        entry = RawPayload(
            source=source,
            kind=kind,
            source_id=source_id,
            content_hash=content_hash,
            payload=payload,
            ingestion_run_id=run.id if run else None,
        )
        self.session.add(entry)
        self.session.flush()
        return entry
