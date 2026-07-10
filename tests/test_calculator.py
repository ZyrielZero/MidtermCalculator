"""Tests for the Calculator engine and the REPL command handler."""

from decimal import Decimal

import pytest

from app.calculation import Calculation
from app.calculator import Calculator, handle_command
from app.calculator_config import CalculatorConfig
from app.exceptions import HistoryError
from app.history import HistoryObserver


@pytest.fixture
def config(tmp_path):
    return CalculatorConfig(
        log_dir=tmp_path / "logs",
        history_dir=tmp_path / "history",
        precision=4,
        max_history_size=5,
        auto_save=False,
        max_input_value=Decimal("1e6"),
    )


@pytest.fixture
def calculator(config):
    return Calculator(config)


class RecordingObserver(HistoryObserver):
    def __init__(self):
        self.seen: list[Calculation] = []

    def on_calculation(self, calculator, calculation):
        self.seen.append(calculation)


# -- engine ---------------------------------------------------------------


def test_perform_runs_and_records(calculator):
    calc = calculator.perform("add", "19", "23")
    assert calc.result == Decimal("42")
    assert calculator.history == [calc]


def test_perform_applies_precision(calculator):
    calc = calculator.perform("divide", "2", "3")
    assert calc.result == Decimal("0.6667")


def test_perform_keeps_whole_numbers_plain(calculator):
    calc = calculator.perform("power", "2", "10")
    assert str(calc.result) == "1024"


def test_history_is_capped_at_configured_size(calculator):
    for n in range(8):
        calculator.perform("add", str(n), "1")
    assert len(calculator.history) == 5
    assert calculator.history[0].operand_a == Decimal("3")


def test_undo_then_redo_walks_history(calculator):
    calculator.perform("add", "1", "1")
    calculator.perform("add", "2", "2")
    calculator.undo()
    assert len(calculator.history) == 1
    calculator.redo()
    assert len(calculator.history) == 2


def test_new_calculation_clears_the_redo_stack(calculator):
    calculator.perform("add", "1", "1")
    calculator.undo()
    calculator.perform("add", "3", "3")
    with pytest.raises(HistoryError):
        calculator.redo()


def test_undo_with_no_history_raises(calculator):
    with pytest.raises(HistoryError):
        calculator.undo()


def test_redo_with_nothing_undone_raises(calculator):
    with pytest.raises(HistoryError):
        calculator.redo()


def test_clear_history_resets_everything(calculator):
    calculator.perform("add", "1", "1")
    calculator.clear_history()
    assert calculator.history == []
    with pytest.raises(HistoryError):
        calculator.undo()


def test_observers_hear_about_new_calculations(calculator):
    observer = RecordingObserver()
    calculator.add_observer(observer)
    calculator.add_observer(observer)  # duplicate ignored
    calculator.perform("subtract", "9", "4")
    assert len(observer.seen) == 1
    calculator.remove_observer(observer)
    calculator.perform("add", "1", "1")
    assert len(observer.seen) == 1


def test_save_and_load_round_trip_through_calculator(calculator):
    calculator.perform("modulus", "22", "6")
    calculator.save_history()
    calculator.clear_history()
    calculator.load_history()
    assert len(calculator.history) == 1
    assert calculator.history[0].result == Decimal("4")


# -- REPL handler -----------------------------------------------------------


def test_blank_line_is_a_quiet_no_op(calculator):
    assert handle_command(calculator, "   ") == (True, "")


def test_operation_line_prints_the_equation(calculator):
    keep, out = handle_command(calculator, "percent 30 120")
    assert keep is True
    assert out == "percent(30, 120) = 25"


def test_exit_stops_the_loop(calculator):
    keep, out = handle_command(calculator, "exit")
    assert keep is False
    assert "Goodbye" in out


def test_help_lists_operations_and_utilities(calculator):
    _, out = handle_command(calculator, "help")
    assert "abs_diff" in out
    assert "undo" in out


def test_history_command_lists_numbered_entries(calculator):
    handle_command(calculator, "add 1 2")
    handle_command(calculator, "multiply 3 4")
    _, out = handle_command(calculator, "history")
    assert out.splitlines()[0].startswith("1. add")
    assert out.splitlines()[1].startswith("2. multiply")


def test_history_command_reports_empty_state(calculator):
    _, out = handle_command(calculator, "history")
    assert out == "History is empty."


def test_clear_undo_redo_commands_respond(calculator):
    handle_command(calculator, "add 5 5")
    assert handle_command(calculator, "undo")[1].startswith("Undid")
    assert handle_command(calculator, "redo")[1].startswith("Redid")
    assert handle_command(calculator, "clear")[1] == "History cleared."


def test_save_and_load_commands_respond(calculator):
    handle_command(calculator, "add 5 5")
    _, save_out = handle_command(calculator, "save")
    assert "saved" in save_out
    handle_command(calculator, "clear")
    _, load_out = handle_command(calculator, "load")
    assert "Loaded 1" in load_out


@pytest.mark.parametrize(
    "line, fragment",
    [
        ("divide 5 0", "zero"),
        ("cube 2 3", "Unknown operation"),
        ("add 1", "exactly two"),
        ("add 1 2 3", "exactly two"),
        ("add one 2", "Could not read"),
        ("undo", "Nothing to undo"),
        ("load", "No history file"),
    ],
)
def test_failures_come_back_as_error_lines(calculator, line, fragment):
    keep, out = handle_command(calculator, line)
    assert keep is True
    assert out.startswith("Error:")
    assert fragment in out