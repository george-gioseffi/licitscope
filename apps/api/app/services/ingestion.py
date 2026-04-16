"""Ingestion orchestrator.

Given a source (default: PNCP) and a date range, this service:

  * starts an ``IngestionRun`` record;
  * streams payloads from the source client (or bundled fixtures);
  * persists the raw payload first, keyed by content hash (replayable);
  * upserts Agencies + Opportunities via their repositories;
  * finalizes the run with ``success`` / ``partial`` / ``failed``.

The run is the single source of truth for observability — counters on the
row (``fetched`` / ``created`` / ``updated`` / ``skipped`` / ``failed``)
make each execution inspectable after the fact.
"""

from __future__ import annotations

import json
import logging
from datetime import UTC, datetime, timedelta
from pathlib import Path
from typing import Any

import httpx
from sqlmodel import Session

from app.clients.pncp import PNCPClient
from app.clients.pncp_parser import parse_full
from app.core.config import get_settings
from app.models.enums import IngestionStatus, SourceName
from app.models.ingestion import IngestionRun
from app.repositories.agencies import AgencyRepository
from app.repositories.ingestion import IngestionRepository
from app.repositories.opportunities import OpportunityRepository

logger = logging.getLogger(__name__)

# Default PNCP modality sweep — pregão eletrônico + dispensa cover most
# practical volume for a daily demo ingestion.
_DEFAULT_MODALITIES: tuple[int, ...] = (1, 9)


class IngestionService:
    def __init__(self, session: Session) -> None:
        self.session = session
        self.agencies = AgencyRepository(session)
        self.opportunities = OpportunityRepository(session)
        self.runs = IngestionRepository(session)

    # ---- public entrypoint --------------------------------------------------
    def ingest_pncp_window(
        self,
        *,
        days_back: int = 3,
        modalities: list[int] | None = None,
        use_fixtures: bool | None = None,
    ) -> IngestionRun:
        settings = get_settings()
        if use_fixtures is None:
            use_fixtures = settings.ingestion_use_fixtures

        params: dict[str, Any] = {
            "days_back": days_back,
            "modalities": list(modalities or _DEFAULT_MODALITIES),
            "use_fixtures": use_fixtures,
        }
        run = self.runs.start_run(
            source=SourceName.PNCP.value, scope="opportunities", params=params
        )
        try:
            payloads = (
                self._load_fixtures()
                if use_fixtures
                else list(self._fetch_from_pncp(days_back=days_back, modalities=modalities))
            )
            self._process_payloads(run, payloads)
            self.runs.finish_run(run, status=IngestionStatus.SUCCESS.value)
        except httpx.HTTPError as exc:
            # Live source failed. Fall back to fixtures so the demo stays up;
            # mark the run partial and record the reason for audit.
            logger.warning("PNCP ingestion HTTP failure (%s); falling back to fixtures", exc)
            try:
                self._process_payloads(run, self._load_fixtures())
                self.runs.finish_run(
                    run,
                    status=IngestionStatus.PARTIAL.value,
                    notes=f"fallback to fixtures after HTTP failure: {exc}",
                )
            except Exception as inner:  # pragma: no cover - defensive
                logger.exception("Fixture fallback also failed")
                self.runs.finish_run(
                    run,
                    status=IngestionStatus.FAILED.value,
                    notes=f"fixture fallback failed: {inner}",
                )
                raise
        except Exception as exc:
            logger.exception("Ingestion failed (unexpected)")
            self.runs.finish_run(run, status=IngestionStatus.FAILED.value, notes=str(exc))
            raise

        self.session.commit()
        return run

    # ---- fetch paths --------------------------------------------------------
    def _fetch_from_pncp(
        self,
        *,
        days_back: int,
        modalities: list[int] | None,
    ) -> list[dict]:
        end = datetime.now(UTC).date()
        start = end - timedelta(days=max(1, days_back))
        d_i, d_f = start.strftime("%Y%m%d"), end.strftime("%Y%m%d")
        settings = get_settings()

        mod_codes = list(modalities or _DEFAULT_MODALITIES)
        collected: list[dict] = []
        with PNCPClient() as client:
            for code in mod_codes:
                before = len(collected)
                for rec in client.list_published_notices(
                    data_inicial=d_i,
                    data_final=d_f,
                    codigo_modalidade=code,
                    page_size=settings.ingestion_page_size,
                    max_pages=settings.ingestion_max_pages,
                ):
                    collected.append(rec)
                logger.info(
                    "PNCP modality=%s window=%s..%s returned %d records",
                    code,
                    d_i,
                    d_f,
                    len(collected) - before,
                )
        logger.info("PNCP fetch returned %d total records", len(collected))
        return collected

    def _load_fixtures(self) -> list[dict]:
        settings = get_settings()
        candidates = [
            settings.data_demo_dir / "pncp" / "opportunities.json",
            Path(__file__).resolve().parents[3] / "data-demo" / "pncp" / "opportunities.json",
        ]
        for path in candidates:
            if path.exists():
                logger.info("Loading PNCP fixtures from %s", path)
                with path.open("r", encoding="utf-8") as f:
                    data = json.load(f)
                return data if isinstance(data, list) else data.get("records", [])
        logger.warning("No PNCP fixtures found; searched %s", [str(p) for p in candidates])
        return []

    # ---- processing ---------------------------------------------------------
    def _process_payloads(self, run: IngestionRun, payloads: list[dict]) -> None:
        """Persist a batch of payloads. Each record is independent — a single
        malformed payload does not abort the run; it bumps ``failed`` and is
        recorded in the raw payload log for later inspection."""
        for raw in payloads:
            run.fetched += 1
            try:
                agency_p, opp_p, items_p = parse_full(raw)
            except Exception as exc:
                logger.exception("Parser failure on payload: %s", exc)
                run.failed += 1
                continue

            source_id = (opp_p.get("source_id") or "").strip()
            if not source_id:
                logger.warning("Payload without source_id skipped")
                run.skipped += 1
                # Still save the raw payload so operators can inspect why.
                self.runs.save_payload(
                    source=SourceName.PNCP.value,
                    kind="opportunity-unparsed",
                    source_id="unknown",
                    payload=raw,
                    run=run,
                )
                continue

            # Persist raw payload first — traceability even if upsert fails.
            self.runs.save_payload(
                source=SourceName.PNCP.value,
                kind="opportunity",
                source_id=source_id,
                payload=raw,
                run=run,
            )

            try:
                agency = (
                    self.agencies.upsert(agency_p)
                    if agency_p.get("cnpj") and agency_p["cnpj"] != "UNKNOWN"
                    else None
                )
                if agency is not None:
                    opp_p["agency_id"] = agency.id

                existed = self.opportunities.get_by_source(opp_p["source"], source_id) is not None
                self.opportunities.upsert(opp_p, items=items_p)
                if existed:
                    run.updated += 1
                else:
                    run.created += 1
            except Exception as exc:
                logger.exception("Upsert failure for %s: %s", source_id, exc)
                run.failed += 1

        self.session.add(run)
        self.session.flush()

    # ---- read helpers -------------------------------------------------------
    def recent_runs(self, limit: int = 25) -> list[dict[str, Any]]:
        runs = self.runs.list_runs(limit=limit)
        return [
            {
                "id": r.id,
                "source": r.source,
                "scope": r.scope,
                "status": r.status,
                "started_at": r.started_at,
                "finished_at": r.finished_at,
                "fetched": r.fetched,
                "created": r.created,
                "updated": r.updated,
                "skipped": r.skipped,
                "failed": r.failed,
                "notes": r.notes,
            }
            for r in runs
        ]
