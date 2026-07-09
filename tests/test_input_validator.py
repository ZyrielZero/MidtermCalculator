"""Tests for input validation and Decimal normalization."""

from decimal import Decimal

import pytest

from app.exceptions import ValidationError
from app.input_validators import InputValidator

LIMIT = Decimal("1e6")


@pytest.mark.parametrize(
    "raw, expected",
    [
        ("42", Decimal("42")),
        ("-17.25", Decimal("-17.25")),
        ("  8.5  ", Decimal("8.5")),
        ("0", Decimal("0")),
        ("3e2", Decimal("300")),
        ("+6", Decimal("6")),
    ],
)
def test_parse_number_accepts_valid_tokens(raw, expected):
    assert InputValidator.parse_number(raw, LIMIT) == expected


@pytest.mark.parametrize(
    "raw",
    ["", "   ", "seven", "4..2", "12abc", None, "nan", "inf", "-inf"],
)
def test_parse_number_rejects_unusable_tokens(raw):
    with pytest.raises(ValidationError):
        InputValidator.parse_number(raw, LIMIT)


@pytest.mark.parametrize("raw", ["1000001", "-1000000.01", "9e9"])
def test_parse_number_rejects_values_over_limit(raw):
    with pytest.raises(ValidationError):
        InputValidator.parse_number(raw, LIMIT)


def test_parse_number_allows_value_exactly_at_limit():
    assert InputValidator.parse_number("1000000", LIMIT) == LIMIT


def test_parse_pair_returns_both_decimals():
    a, b = InputValidator.parse_pair("2.5", "-4", LIMIT)
    assert a == Decimal("2.5")
    assert b == Decimal("-4")


def test_parse_pair_reports_first_bad_operand():
    with pytest.raises(ValidationError) as excinfo:
        InputValidator.parse_pair("oops", "3", LIMIT)
    assert "oops" in str(excinfo.value)