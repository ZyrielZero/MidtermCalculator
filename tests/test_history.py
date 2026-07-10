"""Tests for observers and pandas CSV persistence."""

from decimal import Decimal
from pathlib import Path

import pytest

from app.calculation import Calculation
from app.calculator import Calculator
from app.calculator_config import CalculatorConfig
from app.exceptions import HistoryError
from app.history import (
    AutoSaveObserver,
    HistoryObserver,
    LoggingObserver,
    load_history,
    save_history,
)
from app.logger import configure_logging


def _config(tmp_path, **overrides):
    settings = dict(
        log_dir=tmp_path / "logs", history_dir=tmp_path / "history"
    )
    settings.update(overrides)
    return CalculatorConfig(**settings)


def _calc(n: int) -> Calculation:
    return Calculation(
        operation="multiply",
        operand_a=Decimal(n),
        operand_b=Decimal("3"),
        result=Decimal(3 * n),
    )


def test_save_then_load_round_trips(tmp_path):
    target = tmp_path / "nested" / "hist.csv"
    original = [_calc(1), _calc(5)]
    save_history(original, target, "utf-8")
    assert load_history(target, "utf-8") == original


def test_save_writes_header_even_for_empty_history(tmp_path):
    target = tmp_path / "empty.csv"
    save_history([], target, "utf-8")
    assert load_history(target, "utf-8") == []
    assert "operation" in target.read_text().splitlines()[0]


def test_load_missing_file_raises(tmp_path):
    with pytest.raises(HistoryError):
        load_history(tmp_path / "absent.csv", "utf-8")


def test_load_rejects_file_without_required_columns(tmp_path):
    target = tmp_path / "wrong.csv"
    target.write_text("alpha,beta\n1,2\n")
    with pytest.raises(HistoryError):
        load_history(target, "utf-8")


def test_load_rejects_malformed_row(tmp_path):
    target = tmp_path / "bad.csv"
    target.write_text(
        "operation,operand_a,operand_b,result,timestamp\n"
        "add,one,2,3,2026-07-04T09:30:00\n"
    )
    with pytest.raises(HistoryError):
        load_history(target, "utf-8")


def test_logging_observer_records_the_calculation(tmp_path):
    config = _config(tmp_path)
    configure_logging(config)
    calculator = Calculator(config)
    LoggingObserver().on_calculation(calculator, _calc(4))
    import logging

    for handler in logging.getLogger("calculator").handlers:
        handler.flush()
    assert "result=12" in config.log_file.read_text()


def test_auto_save_observer_writes_when_enabled(tmp_path):
    config = _config(tmp_path, auto_save=True)
    calculator = Calculator(config)
    calculator.history.append(_calc(2))
    AutoSaveObserver().on_calculation(calculator, _calc(2))
    assert config.history_file.exists()


def test_auto_save_observer_stays_quiet_when_disabled(tmp_path):
    config = _config(tmp_path, auto_save=False)
    calculator = Calculator(config)
    calculator.history.append(_calc(2))
    AutoSaveObserver().on_calculation(calculator, _calc(2))
    assert not config.history_file.exists()


def test_observer_base_class_is_abstract():
    with pytest.raises(TypeError):
        HistoryObserver()
        
        
def test_save_translates_os_failures(tmp_path):
    blocker = tmp_path / "blocker"
    blocker.write_text("a file, not a directory")
    with pytest.raises(HistoryError):
        save_history([], blocker / "hist.csv", "utf-8")


def test_load_translates_unparseable_files(tmp_path):
    target = tmp_path / "hollow.csv"
    target.write_text("")
    with pytest.raises(HistoryError):
        load_history(target, "utf-8")