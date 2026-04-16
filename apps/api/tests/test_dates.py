from datetime import UTC

from app.utils.dates import extract_dates, parse_date


def test_parse_iso_naive_gets_utc():
    dt = parse_date("2026-04-16T14:00:00")
    assert dt is not None
    assert dt.tzinfo is UTC


def test_parse_br_format():
    dt = parse_date("16/04/2026")
    assert dt.year == 2026 and dt.month == 4 and dt.day == 16


def test_parse_invalid():
    assert parse_date("") is None
    assert parse_date(None) is None
    assert parse_date("not-a-date") is None


def test_extract_dates_iso_and_br():
    text = "Publicada em 2026-04-15 e abertura em 20/04/2026."
    found = extract_dates(text)
    assert "2026-04-15" in found
    assert "2026-04-20" in found


def test_extract_dates_invalid_ignored():
    assert extract_dates("99/99/9999") == []
