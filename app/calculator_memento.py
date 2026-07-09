"""Memento support for undo and redo.

A memento is a frozen snapshot of the history list at one moment. The
Calculator (originator) captures one before every state change and
restores from one on undo or redo. Snapshots copy the list, not the
Calculation objects, which is safe because Calculation is immutable.
"""

from __future__ import annotations

from dataclasses import dataclass, field

from app.calculation import Calculation


@dataclass(frozen=True)
class CalculatorMemento:
    """An opaque snapshot of calculation history."""

    _snapshot: tuple[Calculation, ...] = field(default_factory=tuple)

    @classmethod
    def capture(cls, history: list[Calculation]) -> "CalculatorMemento":
        """Freeze the current history into a snapshot."""
        return cls(tuple(history))

    def restore(self) -> list[Calculation]:
        """Return a fresh mutable copy of the captured history."""
        return list(self._snapshot)