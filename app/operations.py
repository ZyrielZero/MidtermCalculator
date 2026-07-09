"""Arithmetic operations and the factory that creates them.

Each operation is a small class registered with OperationFactory via a
decorator. The factory owns the only name-to-class mapping in the
application, so adding an operation is a single class definition and
the registry, REPL dispatch, and help menu all pick it up.
"""

from abc import ABC, abstractmethod
from decimal import Decimal, DivisionByZero, InvalidOperation, Overflow

from app.exceptions import OperationError


class Operation(ABC):
    """Base class for all binary calculator operations."""

    name: str = ""
    description: str = ""

    @abstractmethod
    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        """Apply the operation to two validated operands."""

    def __str__(self) -> str:
        return self.name


class OperationFactory:
    """Creates operation instances from their registered names."""

    _registry: dict[str, type[Operation]] = {}

    @classmethod
    def register(cls, op_cls: type[Operation]) -> type[Operation]:
        """Class decorator that adds an operation to the registry."""
        key = op_cls.name.lower()
        if key in cls._registry:
            raise OperationError(
                f"Operation name {key!r} is registered twice."
            )
        cls._registry[key] = op_cls
        return op_cls

    @classmethod
    def create(cls, name: str) -> Operation:
        """Instantiate the operation registered under name.

        Raises:
            OperationError: If no operation uses that name.
        """
        try:
            return cls._registry[name.strip().lower()]()
        except KeyError:
            raise OperationError(
                f"Unknown operation {name!r}; run help for the full list."
            ) from None

    @classmethod
    def available(cls) -> list[type[Operation]]:
        """All registered operation classes, sorted by name."""
        return [cls._registry[key] for key in sorted(cls._registry)]


@OperationFactory.register
class Addition(Operation):
    name = "add"
    description = "Sum of the two operands."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a + b


@OperationFactory.register
class Subtraction(Operation):
    name = "subtract"
    description = "First operand minus the second."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a - b


@OperationFactory.register
class Multiplication(Operation):
    name = "multiply"
    description = "Product of the two operands."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return a * b


@OperationFactory.register
class Division(Operation):
    name = "divide"
    description = "First operand divided by the second."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            raise OperationError("Cannot divide by zero.")
        return a / b


@OperationFactory.register
class Power(Operation):
    name = "power"
    description = "First operand raised to the second."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        try:
            result = a ** b
        except (InvalidOperation, DivisionByZero, Overflow) as exc:
            raise OperationError(
                f"Power is undefined for base {a} and exponent {b}."
            ) from exc
        if not result.is_finite():
            raise OperationError(
                f"Power of base {a} and exponent {b} is not finite."
            )
        return result


@OperationFactory.register
class Root(Operation):
    name = "root"
    description = "The b-th root of the first operand."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            raise OperationError("A root of degree zero is undefined.")
        if a < 0:
            if b != b.to_integral_value() or int(b) % 2 == 0:
                raise OperationError(
                    "A negative radicand needs an odd integer degree."
                )
            return -((-a) ** (Decimal(1) / b))
        try:
            result = a ** (Decimal(1) / b)
        except (InvalidOperation, Overflow) as exc:
            raise OperationError(
                f"Root of degree {b} is undefined for {a}."
            ) from exc
        if not result.is_finite():
            raise OperationError(
                f"Root of degree {b} is not finite for {a}."
            )
        return result


@OperationFactory.register
class Modulus(Operation):
    name = "modulus"
    description = "Remainder after dividing the first operand by the second."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            raise OperationError("Cannot take a remainder with divisor zero.")
        return a % b


@OperationFactory.register
class IntegerDivision(Operation):
    name = "int_divide"
    description = "Quotient with the fractional part discarded."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            raise OperationError("Cannot integer-divide by zero.")
        return a // b


@OperationFactory.register
class Percentage(Operation):
    name = "percent"
    description = "First operand as a percentage of the second."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        if b == 0:
            raise OperationError(
                "Percentage needs a nonzero second operand as the base."
            )
        return (a / b) * Decimal(100)


@OperationFactory.register
class AbsoluteDifference(Operation):
    name = "abs_diff"
    description = "Distance between the two operands."

    def execute(self, a: Decimal, b: Decimal) -> Decimal:
        return abs(a - b)