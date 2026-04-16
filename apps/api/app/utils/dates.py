"""Date helpers for Brazilian procurement text."""

from __future__ import annotations

import re
from datetime import UTC, date, datetime

from dateutil import parser as du_parser

ISO_RE = re.compile(r"\b(\d{4})-(\d{2})-(\d{2})(?:[T ](\d{2}):(\d{2})(?::(\d{2}))?)?")
BR_RE = re.compile(r"\b(\d{2})/(\d{2})/(\d{4})(?:\s+(\d{2}):(\d{2})(?::(\d{2}))?)?")


def parse_date(value: str | None) -> datetime | None:
    """Best-effort parse of an ISO or BR-style date string into aware UTC."""
    if not value:
        return None
    try:
        dt = du_parser.parse(str(value), dayfirst=True)
        if dt.tzinfo is None:
            dt = dt.replace(tzinfo=UTC)
        return dt
    except (ValueError, OverflowError, du_parser.ParserError):
        return None


def extract_dates(text: str) -> list[str]:
    """Return ISO date strings mentioned in free text (ISO + BR format)."""
    if not text:
        return []
    out: set[str] = set()
    for m in ISO_RE.finditer(text):
        y, mo, d = m.group(1), m.group(2), m.group(3)
        out.add(f"{y}-{mo}-{d}")
    for m in BR_RE.finditer(text):
        d, mo, y = m.group(1), m.group(2), m.group(3)
        try:
            iso = date(int(y), int(mo), int(d)).isoformat()
            out.add(iso)
        except ValueError:
            pass
    return sorted(out)


def now_utc() -> datetime:
    return datetime.now(UTC)
