"""Tests for the Command pattern layer."""

from decimal import Decimal

import pytest

from app.calculator import UTILITY_COMMANDS, Calculator
from app.calculator_config import CalculatorConfig
from app.commands import (
    Command,
    ExitCommand,
    HelpCommand,
    OperationCommand,
    build_registry,
)
from app.exceptions import ValidationError
from app.operations import OperationFactory


@pytest.fixture
def calculator(tmp_path):
    return Calculator(
        CalculatorConfig(
            log_dir=tmp_path / "logs",
            history_dir=tmp_path / "history",
            auto_save=False,
        )
    )


def test_command_base_is_abstract():
    with pytest.raises(TypeError):
        Command()


def test_operation_command_delegates_to_the_factory(calculator):
    out = OperationCommand("abs_diff").execute(calculator, ["3", "11"])
    assert out == "abs_diff(3, 11) = 8"
    assert calculator.history[0].result == Decimal("8")


def test_operation_command_enforces_two_operands(calculator):
    with pytest.raises(ValidationError):
        OperationCommand("add").execute(calculator, ["1"])


def test_exit_command_signals_shutdown(calculator):
    command = ExitCommand()
    assert command.keeps_running is False
    assert command.execute(calculator, []) == "Goodbye."


def test_help_command_renders_the_decorated_menu(calculator):
    out = HelpCommand(UTILITY_COMMANDS).execute(calculator, [])
    assert "Operations" in out and "exit" in out


def test_registry_covers_every_verb():
    names = [op.name for op in OperationFactory.available()]
    registry = build_registry(names, UTILITY_COMMANDS)
    for verb in names + list(UTILITY_COMMANDS):
        assert verb in registry
    assert len(registry) == len(names) + len(UTILITY_COMMANDS)