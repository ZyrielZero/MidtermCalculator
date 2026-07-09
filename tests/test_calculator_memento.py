"""Tests for history snapshots."""

from decimal import Decimal

from app.calculation import Calculation
from app.calculator_memento import CalculatorMemento


def _calc(n: int) -> Calculation:
    return Calculation(
        operation="add",
        operand_a=Decimal(n),
        operand_b=Decimal(n),
        result=Decimal(2 * n),
    )


def test_capture_then_restore_round_trips():
    history = [_calc(1), _calc(2)]
    memento = CalculatorMemento.capture(history)
    assert memento.restore() == history


def test_snapshot_is_detached_from_the_live_list():
    first = _calc(1)
    history = [first]
    memento = CalculatorMemento.capture(history)
    history.append(_calc(2))
    assert memento.restore() == [first]


def test_restore_returns_a_fresh_list_each_time():
    kept = _calc(3)
    memento = CalculatorMemento.capture([kept])
    restored = memento.restore()
    restored.clear()
    assert memento.restore() == [kept]


def test_empty_history_snapshots_cleanly():
    assert CalculatorMemento.capture([]).restore() == []