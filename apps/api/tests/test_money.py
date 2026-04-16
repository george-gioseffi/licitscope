import pytest

from app.utils.money import parse_brl


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("R$ 1.234,56", 1234.56),
        ("1.234,56", 1234.56),
        ("1234.56", 1234.56),
        ("1234,56", 1234.56),
        ("R$ 2.500.000,00", 2_500_000.00),
        ("100", 100.0),
        ("", None),
        (None, None),
        (1234.5, 1234.5),
        (42, 42.0),
    ],
)
def test_parse_brl(raw, expected):
    assert parse_brl(raw) == expected


def test_parse_brl_garbage_returns_none():
    assert parse_brl("abc") is None
