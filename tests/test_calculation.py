"""Tests for the Calculation record and its CSV row contract."""

from datetime import datetime
from decimal import Decimal

import pytest

from app.calculation import CSV_COLUMNS, Calculation
from app.exceptions import HistoryError


def _sample() -> Calculation:
    return Calculation(
        operation="modulus",
        operand_a=Decimal("22"),
        operand_b=Decimal("6"),
        result=Decimal("4"),
        timestamp=datetime(2026, 7, 4, 9, 30, 0),
    )


def test_str_reads_like_an_equation():
    assert str(_sample()) == "modulus(22, 6) = 4"


def test_to_row_covers_every_csv_column():
    row = _sample().to_row()
    assert set(row) == set(CSV_COLUMNS)
    assert row["result"] == "4"
    assert row["timestamp"] == "2026-07-04T09:30:00"


def test_row_round_trip_preserves_everything():
    original = _sample()
    rebuilt = Calculation.from_row(original.to_row())
    assert rebuilt == original


def test_round_trip_keeps_decimal_exactness():
    calc = Calculation(
        operation="divide",
        operand_a=Decimal("1"),
        operand_b=Decimal("3"),
        result=Decimal("0.3333333333"),
    )
    rebuilt = Calculation.from_row(calc.to_row())
    assert rebuilt.result == Decimal("0.3333333333")


def test_from_row_rejects_missing_column():
    row = _sample().to_row()
    del row["operand_b"]
    with pytest.raises(HistoryError):
        Calculation.from_row(row)


@pytest.mark.parametrize(
    "column, bad_value",
    [
        ("operand_a", "twelve"),
        ("result", ""),
        ("timestamp", "yesterday morning"),
    ],
)
def test_from_row_rejects_unreadable_values(column, bad_value):
    row = _sample().to_row()
    row[column] = bad_value
    with pytest.raises(HistoryError):
        Calculation.from_row(row)


def test_calculation_is_immutable():
    with pytest.raises(AttributeError):
        _sample().result = Decimal("99")