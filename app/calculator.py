"""The Calculator engine and its command-line REPL.

Calculator ties every other module together: validated Decimal input,
factory-created operations, precision rounding, memento-backed undo
and redo, observer notification, and pandas persistence. The REPL is
a thin loop over handle_command, which stays a pure function so tests
can drive it without faking stdin.
"""

from __future__ import annotations

from decimal import Decimal, InvalidOperation

from app import history as history_io
from app.calculation import Calculation
from app.calculator_config import CalculatorConfig
from app.calculator_memento import CalculatorMemento
from app.exceptions import CalculatorError, HistoryError, ValidationError
from app.history import AutoSaveObserver, HistoryObserver, LoggingObserver
from app.input_validators import InputValidator
from app.logger import configure_logging, get_logger
from app.operations import OperationFactory

UTILITY_COMMANDS = {
    "history": "Show every calculation this session.",
    "clear": "Erase history along with undo and redo state.",
    "undo": "Revert the most recent calculation.",
    "redo": "Reapply the most recently undone calculation.",
    "save": "Write history to the configured CSV file.",
    "load": "Replace history with the saved CSV file.",
    "help": "Show this command list.",
    "exit": "Leave the calculator.",
}


class Calculator:
    """Originator, subject, and owner of calculation history."""

    def __init__(self, config: CalculatorConfig | None = None) -> None:
        self.config = config or CalculatorConfig.from_env()
        self.history: list[Calculation] = []
        self._undo_stack: list[CalculatorMemento] = []
        self._redo_stack: list[CalculatorMemento] = []
        self._observers: list[HistoryObserver] = []

    # -- observer wiring -------------------------------------------------

    def add_observer(self, observer: HistoryObserver) -> None:
        if observer not in self._observers:
            self._observers.append(observer)

    def remove_observer(self, observer: HistoryObserver) -> None:
        if observer in self._observers:
            self._observers.remove(observer)

    def _notify(self, calculation: Calculation) -> None:
        for observer in self._observers:
            observer.on_calculation(self, calculation)

    # -- core calculation ------------------------------------------------

    def _round(self, value: Decimal) -> Decimal:
        """Quantize to the configured decimal places, then tidy zeros."""
        exponent = Decimal(1).scaleb(-self.config.precision)
        try:
            rounded = value.quantize(exponent)
        except InvalidOperation:
            return value
        tidy = rounded.normalize()
        if tidy.as_tuple().exponent > 0:
            return tidy.quantize(Decimal(1))
        return tidy

    def perform(self, op_name: str, raw_a: str, raw_b: str) -> Calculation:
        """Validate, execute, record, and broadcast one calculation."""
        a, b = InputValidator.parse_pair(
            raw_a, raw_b, self.config.max_input_value
        )
        operation = OperationFactory.create(op_name)
        result = self._round(operation.execute(a, b))

        self._undo_stack.append(CalculatorMemento.capture(self.history))
        self._redo_stack.clear()

        calculation = Calculation(
            operation=operation.name, operand_a=a, operand_b=b, result=result
        )
        self.history.append(calculation)
        while len(self.history) > self.config.max_history_size:
            self.history.pop(0)

        self._notify(calculation)
        return calculation

    # -- undo / redo -----------------------------------------------------

    def undo(self) -> None:
        if not self._undo_stack:
            raise HistoryError("Nothing to undo.")
        self._redo_stack.append(CalculatorMemento.capture(self.history))
        self.history = self._undo_stack.pop().restore()

    def redo(self) -> None:
        if not self._redo_stack:
            raise HistoryError("Nothing to redo.")
        self._undo_stack.append(CalculatorMemento.capture(self.history))
        self.history = self._redo_stack.pop().restore()

    def clear_history(self) -> None:
        self.history.clear()
        self._undo_stack.clear()
        self._redo_stack.clear()

    # -- persistence -----------------------------------------------------

    def save_history(self) -> None:
        history_io.save_history(
            self.history, self.config.history_file, self.config.default_encoding
        )

    def load_history(self) -> None:
        self.history = history_io.load_history(
            self.config.history_file, self.config.default_encoding
        )
        self._undo_stack.clear()
        self._redo_stack.clear()


# -- REPL ------------------------------------------------------------------


def help_text() -> str:
    """Static command listing for the help command.

    Hand-maintained for now; a later branch will generate this from
    the operation registry so new operations appear automatically.
    """
    lines = [
        "Operations (usage: <name> <a> <b>):",
        "  add, subtract, multiply, divide, power, root,",
        "  modulus, int_divide, percent, abs_diff",
        "Other commands:",
    ]
    for name, blurb in UTILITY_COMMANDS.items():
        lines.append(f"  {name:<12}{blurb}")
    return "\n".join(lines)


def handle_command(calculator: Calculator, line: str) -> tuple[bool, str]:
    """Process one REPL line.

    Returns:
        A (keep_running, output) pair. keep_running is False only for
        the exit command.
    """
    tokens = line.strip().split()
    if not tokens:
        return True, ""
    command, args = tokens[0].lower(), tokens[1:]

    try:
        if command == "exit":
            return False, "Goodbye."
        if command == "help":
            return True, help_text()
        if command == "history":
            if not calculator.history:
                return True, "History is empty."
            rows = [
                f"{i}. {calc}" for i, calc in enumerate(calculator.history, 1)
            ]
            return True, "\n".join(rows)
        if command == "clear":
            calculator.clear_history()
            return True, "History cleared."
        if command == "undo":
            calculator.undo()
            return True, "Undid the last calculation."
        if command == "redo":
            calculator.redo()
            return True, "Redid the last undone calculation."
        if command == "save":
            calculator.save_history()
            return True, f"History saved to {calculator.config.history_file}."
        if command == "load":
            calculator.load_history()
            return True, f"Loaded {len(calculator.history)} calculations."

        if len(args) != 2:
            raise ValidationError(
                f"Usage: {command} <a> <b> with exactly two operands."
            )
        calculation = calculator.perform(command, args[0], args[1])
        return True, str(calculation)
    except CalculatorError as exc:
        get_logger().warning("command %r failed: %s", line.strip(), exc)
        return True, f"Error: {exc}"


def run_repl() -> None:  # pragma: no cover
    """Interactive Read-Eval-Print Loop."""
    config = CalculatorConfig.from_env()
    configure_logging(config)
    calculator = Calculator(config)
    calculator.add_observer(LoggingObserver())
    calculator.add_observer(AutoSaveObserver())

    print("Advanced Calculator. Type help for commands.")
    while True:
        try:
            line = input("calc> ")
        except (EOFError, KeyboardInterrupt):
            print()
            break
        keep_running, output = handle_command(calculator, line)
        if output:
            print(output)
        if not keep_running:
            break


if __name__ == "__main__":  # pragma: no cover
    run_repl()