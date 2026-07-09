"""Tests for arithmetic operations and the operation factory."""

from decimal import Decimal

import pytest

from app.exceptions import OperationError
from app.operations import Operation, OperationFactory

D = Decimal


@pytest.mark.parametrize(
    "op_name, a, b, expected",
    [
        ("add", D("11"), D("31"), D("42")),
        ("add", D("-2.5"), D("2.5"), D("0")),
        ("subtract", D("10"), D("14"), D("-4")),
        ("multiply", D("1.5"), D("4"), D("6")),
        ("multiply", D("7"), D("0"), D("0")),
        ("divide", D("9"), D("4"), D("2.25")),
        ("divide", D("-12"), D("3"), D("-4")),
        ("power", D("2"), D("10"), D("1024")),
        ("power", D("9"), D("0.5"), D("3")),
        ("power", D("5"), D("0"), D("1")),
        ("root", D("27"), D("3"), D("3")),
        ("root", D("16"), D("4"), D("2")),
        ("modulus", D("17"), D("5"), D("2")),
        ("int_divide", D("17"), D("5"), D("3")),
        ("percent", D("30"), D("120"), D("25")),
        ("percent", D("150"), D("60"), D("250")),
        ("abs_diff", D("3"), D("11"), D("8")),
        ("abs_diff", D("-4"), D("-9"), D("5")),
    ],
)
def test_operations_produce_expected_results(op_name, a, b, expected):
    op = OperationFactory.create(op_name)
    assert op.execute(a, b) == expected


def test_root_of_negative_with_odd_degree():
    op = OperationFactory.create("root")
    assert op.execute(D("-8"), D("3")) == D("-2")


def test_int_divide_truncates_toward_zero():
    # Decimal floor-division truncates, matching the spec's
    # "discard the fractional part" wording; -7 // 2 is -3, not -4.
    op = OperationFactory.create("int_divide")
    assert op.execute(D("-7"), D("2")) == D("-3")


@pytest.mark.parametrize(
    "op_name, a, b",
    [
        ("divide", D("5"), D("0")),
        ("modulus", D("5"), D("0")),
        ("int_divide", D("5"), D("0")),
        ("percent", D("5"), D("0")),
        ("root", D("5"), D("0")),
        ("root", D("-16"), D("2")),
        ("root", D("-5"), D("2.5")),
        ("power", D("0"), D("-1")),
        ("power", D("-4"), D("0.5")),
    ],
)
def test_operations_reject_undefined_inputs(op_name, a, b):
    op = OperationFactory.create(op_name)
    with pytest.raises(OperationError):
        op.execute(a, b)


def test_factory_rejects_unknown_name():
    with pytest.raises(OperationError):
        OperationFactory.create("cube")


def test_factory_is_case_and_whitespace_tolerant():
    op = OperationFactory.create("  ADD ")
    assert op.execute(D("1"), D("2")) == D("3")


def test_factory_rejects_duplicate_registration():
    with pytest.raises(OperationError):

        @OperationFactory.register
        class DuplicateAdd(Operation):
            name = "add"
            description = "collides with the real add"

            def execute(self, a, b):  # pragma: no cover
                return a + b


def test_available_lists_all_ten_operations():
    names = [op.name for op in OperationFactory.available()]
    assert len(names) == 10
    assert names == sorted(names)
    assert "abs_diff" in names and "power" in names