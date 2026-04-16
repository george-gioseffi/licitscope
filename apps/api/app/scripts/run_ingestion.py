"""One-shot ingestion cycle. Reads config from env."""

from __future__ import annotations

import logging
import sys

from app.core.logging import configure_logging
from app.db.session import init_db, session_scope
from app.services.ingestion import IngestionService

logger = logging.getLogger("ingest")


def main() -> int:
    configure_logging()
    init_db()
    with session_scope() as session:
        svc = IngestionService(session)
        run = svc.ingest_pncp_window(days_back=3)
        logger.info(
            "ingestion run %s finished status=%s fetched=%d created=%d updated=%d failed=%d",
            run.id, run.status, run.fetched, run.created, run.updated, run.failed,
        )
    return 0


if __name__ == "__main__":
    sys.exit(main())
