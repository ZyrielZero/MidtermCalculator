"""Input validation utilities.

All user-supplied text enters the application through this module.
Values are converted to Decimal at the boundary so downstream code
never handles raw strings or binary floats, which keeps precision
rounding exact once configuration wires in CALCULATOR_PRECISION.
"""

from decimal import Decimal, InvalidOperation

from app.exceptions import ValidationError


class InputValidator:
    """Validates and normalizes raw operand input."""

    @staticmethod
    def parse_number(raw: str, max_value: Decimal) -> Decimal:
        """Convert one raw token into a bounded Decimal.

        Args:
            raw: The text the user typed for a single operand.
            max_value: Largest permitted magnitude, from configuration.

        Returns:
            The parsed value as a Decimal.

        Raises:
            ValidationError: If the token is empty, not numeric, or
                its magnitude exceeds max_value.
        """
        cleaned = raw.strip() if isinstance(raw, str) else raw
        if cleaned is None or cleaned == "":
            raise ValidationError("An operand was left empty; enter a number.")

        try:
            value = Decimal(str(cleaned))
        except (InvalidOperation, ValueError, TypeError) as exc:
            raise ValidationError(
                f"Could not read {cleaned!r} as a number."
            ) from exc

        if value.is_nan() or value.is_infinite():
            raise ValidationError(
                f"{cleaned!r} is not a finite number."
            )

        if abs(value) > max_value:
            raise ValidationError(
                f"Magnitude of {value} exceeds the allowed maximum of {max_value}."
            )

        return value

    @staticmethod
    def parse_pair(
        raw_a: str, raw_b: str, max_value: Decimal
    ) -> tuple[Decimal, Decimal]:
        """Validate both operands of a binary operation at once."""
        return (
            InputValidator.parse_number(raw_a, max_value),
            InputValidator.parse_number(raw_b, max_value),
        )