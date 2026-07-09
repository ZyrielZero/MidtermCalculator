"""Tests for the exception hierarchy."""

import pytest

from app.exceptions import (
    CalculatorError,
    ConfigurationError,
    HistoryError,
    OperationError,
    ValidationError,
)


@pytest.mark.parametrize(
    "exc_type",
    [ValidationError, OperationError, ConfigurationError, HistoryError],
)
def test_specific_errors_derive_from_calculator_error(exc_type):
    assert issubclass(exc_type, CalculatorError)


@pytest.mark.parametrize(
    "exc_type",
    [ValidationError, OperationError, ConfigurationError, HistoryError],
)
def test_specific_errors_are_catchable_as_calculator_error(exc_type):
    with pytest.raises(CalculatorError):
        raise exc_type("triggered for the hierarchy test")


def test_error_message_round_trips():
    err = OperationError("sixth root of a negative operand")
    assert str(err) == "sixth root of a negative operand"