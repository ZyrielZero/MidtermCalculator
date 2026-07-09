"""Dynamic help menu built with the Decorator pattern.

BasicHelp renders the bare header. Each decorator wraps a component
and appends its own section, so the final text is assembled by
stacking decorators. The operations section reads the live factory
registry, which means a newly registered operation appears in help
with zero changes here.
"""

from __future__ import annotations

from abc import ABC, abstractmethod

from app.operations import OperationFactory


class HelpComponent(ABC):
    """Anything that can render a block of help text."""

    @abstractmethod
    def render(self) -> str:
        """Produce this component's help text."""


class BasicHelp(HelpComponent):
    """The undecorated core: just the banner line."""

    def render(self) -> str:
        return "Advanced Calculator commands"


class HelpDecorator(HelpComponent):
    """Base decorator: wraps a component and extends its output."""

    def __init__(self, inner: HelpComponent) -> None:
        self._inner = inner

    def render(self) -> str:
        return self._inner.render()


class OperationsSection(HelpDecorator):
    """Appends every registered operation, straight from the factory."""

    def render(self) -> str:
        lines = [self._inner.render(), "", "Operations (usage: <name> <a> <b>):"]
        for op_cls in OperationFactory.available():
            lines.append(f"  {op_cls.name:<12}{op_cls.description}")
        return "\n".join(lines)


class UtilitiesSection(HelpDecorator):
    """Appends the non-arithmetic REPL commands."""

    def __init__(
        self, inner: HelpComponent, utilities: dict[str, str]
    ) -> None:
        super().__init__(inner)
        self._utilities = utilities

    def render(self) -> str:
        lines = [self._inner.render(), "", "Other commands:"]
        for name, blurb in self._utilities.items():
            lines.append(f"  {name:<12}{blurb}")
        return "\n".join(lines)


def build_help(utilities: dict[str, str]) -> str:
    """Stack the decorators and render the full help text."""
    menu: HelpComponent = BasicHelp()
    menu = OperationsSection(menu)
    menu = UtilitiesSection(menu, utilities)
    return menu.render()