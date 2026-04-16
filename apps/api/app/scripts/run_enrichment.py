"""Re-run enrichment over all opportunities (or only missing ones)."""

from __future__ import annotations

import argparse
import logging
import sys

from app.core.logging import configure_logging
from app.db.session import init_db, session_scope
from app.enrichment.pipeline import EnrichmentPipeline

logger = logging.getLogger("enrich")


def main(argv: list[str] | None = None) -> int:
    configure_logging()
    init_db()
    parser = argparse.ArgumentParser(description="Run enrichment over the opportunities table.")
    parser.add_argument("--only-missing", action="store_true")
    args = parser.parse_args(argv)
    with session_scope() as session:
        processed = EnrichmentPipeline(session).enrich_all(only_missing=args.only_missing)
        logger.info("enriched %d opportunities", processed)
    return 0


if __name__ == "__main__":
    sys.exit(main())
