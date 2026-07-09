"""Custom exception hierarchy for the calculator application.

Every error the application raises intentionally derives from
CalculatorError, so the REPL can catch one type at its top level and
report a readable message while genuine bugs propagate normally.
"""


class CalculatorError(Exception):
    """Root of the calculator's exception hierarchy."""


class ValidationError(CalculatorError):
    """Raised when user input fails validation before any math runs.

    Examples: non-numeric text, values beyond the configured maximum,
    or a missing operand.
    """


class OperationError(CalculatorError):
    """Raised when an arithmetic operation cannot produce a result.

    Examples: an unknown operation name requested from the factory,
    dividing by zero, or an even root of a negative number.
    """


class ConfigurationError(CalculatorError):
    """Raised when application settings are missing or unusable.

    Examples: a precision value that is not a positive integer, or a
    directory path that cannot be created.
    """


class HistoryError(CalculatorError):
    """Raised when persisting or restoring calculation history fails.

    Examples: a malformed CSV row, or a history file that cannot be
    read with the configured encoding.
    """