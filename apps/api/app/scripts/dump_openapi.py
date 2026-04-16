"""Dump the current OpenAPI schema to docs/openapi.json.

The committed snapshot under ``docs/openapi.json`` doubles as:

* an easy way for reviewers to see the full API surface without booting
  the server;
* a CI artefact that would catch accidental schema changes in review.

Run:
    python -m app.scripts.dump_openapi
"""

from __future__ import annotations

import json
import logging
import sys
from pathlib import Path

from app.core.logging import configure_logging
from app.main import app

logger = logging.getLogger("openapi-dump")


def main() -> int:
    configure_logging()
    schema = app.openapi()
    # The repo-root path, reached via app/scripts/dump_openapi.py -> 4 up
    root = Path(__file__).resolve().parents[4]
    target = root / "docs" / "openapi.json"
    target.parent.mkdir(parents=True, exist_ok=True)
    target.write_text(json.dumps(schema, indent=2, ensure_ascii=False) + "\n", encoding="utf-8")
    logger.info(
        "Wrote OpenAPI schema to %s (%d paths)",
        target,
        len(schema.get("paths", {})),
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
