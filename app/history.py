"""History observers and CSV persistence.

The observer half implements the Observer pattern: the Calculator
notifies every registered HistoryObserver after each successful
calculation. The persistence half serializes history to CSV through
pandas. Reading uses dtype=str so operands come back as exact strings
for Decimal, never as lossy floats.
"""

from __future__ import annotations

from abc import ABC, abstractmethod
from pathlib import Path
from typing import TYPE_CHECKING

import pandas as pd

from app.calculation import CSV_COLUMNS, Calculation
from app.exceptions import HistoryError
from app.logger import get_logger

if TYPE_CHECKING:  # pragma: no cover
    from app.calculator import Calculator


class HistoryObserver(ABC):
    """Reacts whenever the calculator completes a calculation."""

    @abstractmethod
    def on_calculation(
        self, calculator: "Calculator", calculation: Calculation
    ) -> None:
        """Handle one newly completed calculation."""


class LoggingObserver(HistoryObserver):
    """Writes every calculation to the application log."""

    def on_calculation(
        self, calculator: "Calculator", calculation: Calculation
    ) -> None:
        get_logger().info(
            "operation=%s operands=(%s, %s) result=%s",
            calculation.operation,
            calculation.operand_a,
            calculation.operand_b,
            calculation.result,
        )


class AutoSaveObserver(HistoryObserver):
    """Persists history after each calculation when auto-save is on."""

    def on_calculation(
        self, calculator: "Calculator", calculation: Calculation
    ) -> None:
        if calculator.config.auto_save:
            calculator.save_history()


def save_history(
    history: list[Calculation], path: Path, encoding: str
) -> None:
    """Write the history list to a CSV file via pandas.

    Raises:
        HistoryError: If the file cannot be written.
    """
    frame = pd.DataFrame(
        [calc.to_row() for calc in history], columns=list(CSV_COLUMNS)
    )
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        frame.to_csv(path, index=False, encoding=encoding)
    except OSError as exc:
        raise HistoryError(f"Could not write history to {path}.") from exc


def load_history(path: Path, encoding: str) -> list[Calculation]:
    """Read a CSV file back into a list of Calculations via pandas.

    Raises:
        HistoryError: If the file is absent, unreadable, or malformed.
    """
    if not path.exists():
        raise HistoryError(f"No history file at {path}; save one first.")
    try:
        frame = pd.read_csv(path, dtype=str, encoding=encoding)
    except (OSError, ValueError, pd.errors.ParserError) as exc:
        raise HistoryError(f"Could not read history from {path}.") from exc

    missing = set(CSV_COLUMNS) - set(frame.columns)
    if missing:
        raise HistoryError(
            f"History file lacks columns: {', '.join(sorted(missing))}."
        )
    return [Calculation.from_row(row) for row in frame.to_dict("records")]