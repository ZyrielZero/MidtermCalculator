"""The Calculation record.

One immutable object per performed calculation. The record knows how
to flatten itself into a plain dict (one CSV row) and rebuild itself
from one, which is the only serialization contract the rest of the
application relies on. Operands travel as strings in CSV form so
Decimal exactness survives the round trip.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal, InvalidOperation

from app.exceptions import HistoryError

CSV_COLUMNS = ("operation", "operand_a", "operand_b", "result", "timestamp")


@dataclass(frozen=True)
class Calculation:
    """A single completed calculation."""

    operation: str
    operand_a: Decimal
    operand_b: Decimal
    result: Decimal
    timestamp: datetime = field(default_factory=datetime.now)

    def to_row(self) -> dict[str, str]:
        """Flatten into a dict of strings, ready for one CSV row."""
        return {
            "operation": self.operation,
            "operand_a": str(self.operand_a),
            "operand_b": str(self.operand_b),
            "result": str(self.result),
            "timestamp": self.timestamp.isoformat(),
        }

    @classmethod
    def from_row(cls, row: dict[str, str]) -> "Calculation":
        """Rebuild a Calculation from one CSV row.

        Raises:
            HistoryError: If the row is missing columns or holds
                values that cannot be parsed back.
        """
        try:
            return cls(
                operation=str(row["operation"]),
                operand_a=Decimal(str(row["operand_a"])),
                operand_b=Decimal(str(row["operand_b"])),
                result=Decimal(str(row["result"])),
                timestamp=datetime.fromisoformat(str(row["timestamp"])),
            )
        except KeyError as exc:
            raise HistoryError(
                f"History row is missing the {exc.args[0]!r} column."
            ) from exc
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise HistoryError(
                f"History row holds an unreadable value: {row!r}"
            ) from exc

    def __str__(self) -> str:
        return f"{self.operation}({self.operand_a}, {self.operand_b}) = {self.result}"