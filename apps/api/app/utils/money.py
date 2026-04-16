"""Money parsing helpers for Brazilian Real."""

from __future__ import annotations

import re

_RE_MONEY = re.compile(r"[-+]?\d{1,3}(?:\.\d{3})*(?:,\d+)?|\d+(?:\.\d+)?")


def parse_brl(value: str | float | int | None) -> float | None:
    """Parse Brazilian Real strings: '1.234,56' -> 1234.56. Accepts numerics."""
    if value is None or value == "":
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value).strip()
    if not text:
        return None
    text = text.replace("R$", "").replace("BRL", "").replace(" ", "")
    # If both separators present, "." is thousands, "," is decimals.
    if "," in text and "." in text:
        text = text.replace(".", "").replace(",", ".")
    elif "," in text:
        text = text.replace(",", ".")
    try:
        return float(text)
    except ValueError:
        m = _RE_MONEY.search(text)
        if m:
            try:
                return float(m.group(0).replace(".", "").replace(",", "."))
            except ValueError:
                return None
    return None
