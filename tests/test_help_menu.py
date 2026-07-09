"""Tests for the decorator-built help menu."""

from app.calculator import UTILITY_COMMANDS
from app.help_menu import (
    BasicHelp,
    HelpDecorator,
    OperationsSection,
    UtilitiesSection,
    build_help,
)
from app.operations import OperationFactory


def test_basic_help_is_just_the_banner():
    assert BasicHelp().render() == "Advanced Calculator commands"


def test_plain_decorator_passes_text_through():
    assert HelpDecorator(BasicHelp()).render() == BasicHelp().render()


def test_operations_section_lists_every_registered_op():
    text = OperationsSection(BasicHelp()).render()
    for op_cls in OperationFactory.available():
        assert op_cls.name in text
        assert op_cls.description in text


def test_utilities_section_lists_repl_commands():
    text = UtilitiesSection(BasicHelp(), UTILITY_COMMANDS).render()
    for name in UTILITY_COMMANDS:
        assert name in text


def test_build_help_stacks_both_sections():
    text = build_help(UTILITY_COMMANDS)
    assert text.startswith("Advanced Calculator commands")
    assert "Operations" in text
    assert "Other commands:" in text


def test_new_registration_appears_without_edits():
    from decimal import Decimal

    from app.operations import Operation

    @OperationFactory.register
    class Doubling(Operation):
        name = "double_check"
        description = "Temporary op proving the menu is dynamic."

        def execute(self, a: Decimal, b: Decimal) -> Decimal:
            return a * 2  # pragma: no cover

    try:
        assert "double_check" in build_help(UTILITY_COMMANDS)
    finally:
        OperationFactory._registry.pop("double_check")