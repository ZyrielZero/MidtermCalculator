"""REPL commands encapsulated as objects (Command pattern).

Every REPL verb becomes a Command with one execute method, and the
registry maps verb names to instances. The REPL's dispatch collapses
to a dictionary lookup, and arithmetic falls through to a single
OperationCommand that defers to the operation factory.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from typing import TYPE_CHECKING

from app.exceptions import ValidationError
from app.help_menu import build_help

if TYPE_CHECKING:  # pragma: no cover
    from app.calculator import Calculator


class Command(ABC):
    """One REPL verb, executable against a calculator."""

    #: Set False by commands that end the session.
    keeps_running: bool = True

    @abstractmethod
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        """Run the command and return the text to print."""


class OperationCommand(Command):
    """Adapter that routes an arithmetic verb through the factory."""

    def __init__(self, op_name: str) -> None:
        self._op_name = op_name

    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        if len(args) != 2:
            raise ValidationError(
                f"Usage: {self._op_name} <a> <b> with exactly two operands."
            )
        return str(calculator.perform(self._op_name, args[0], args[1]))


class HistoryCommand(Command):
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        if not calculator.history:
            return "History is empty."
        return "\n".join(
            f"{i}. {calc}" for i, calc in enumerate(calculator.history, 1)
        )


class ClearCommand(Command):
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        calculator.clear_history()
        return "History cleared."


class UndoCommand(Command):
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        calculator.undo()
        return "Undid the last calculation."


class RedoCommand(Command):
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        calculator.redo()
        return "Redid the last undone calculation."


class SaveCommand(Command):
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        calculator.save_history()
        return f"History saved to {calculator.config.history_file}."


class LoadCommand(Command):
    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        calculator.load_history()
        return f"Loaded {len(calculator.history)} calculations."


class HelpCommand(Command):
    def __init__(self, utilities: dict[str, str]) -> None:
        self._utilities = utilities

    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        return build_help(self._utilities)


class ExitCommand(Command):
    keeps_running = False

    def execute(self, calculator: "Calculator", args: list[str]) -> str:
        return "Goodbye."


def build_registry(
    operation_names: list[str], utilities: dict[str, str]
) -> dict[str, Command]:
    """Assemble the full verb-to-command mapping."""
    registry: dict[str, Command] = {
        name: OperationCommand(name) for name in operation_names
    }
    registry.update(
        {
            "history": HistoryCommand(),
            "clear": ClearCommand(),
            "undo": UndoCommand(),
            "redo": RedoCommand(),
            "save": SaveCommand(),
            "load": LoadCommand(),
            "help": HelpCommand(utilities),
            "exit": ExitCommand(),
        }
    )
    return registry