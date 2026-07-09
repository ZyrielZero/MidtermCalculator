"""Configuration loaded from the environment.

Settings arrive through a .env file (via python-dotenv) or real
environment variables, with sensible defaults for anything unset.
Validation happens once at construction so the rest of the code can
trust every field.
"""

from __future__ import annotations

import os
from dataclasses import dataclass
from decimal import Decimal, InvalidOperation
from pathlib import Path

from dotenv import load_dotenv

from app.exceptions import ConfigurationError

_TRUTHY = {"true", "1", "yes", "on"}
_FALSY = {"false", "0", "no", "off"}


def _parse_bool(raw: str, setting: str) -> bool:
    lowered = raw.strip().lower()
    if lowered in _TRUTHY:
        return True
    if lowered in _FALSY:
        return False
    raise ConfigurationError(
        f"{setting} must be a boolean-like value, not {raw!r}."
    )


def _parse_positive_int(raw: str, setting: str) -> int:
    try:
        value = int(raw)
    except ValueError as exc:
        raise ConfigurationError(
            f"{setting} must be an integer, not {raw!r}."
        ) from exc
    if value <= 0:
        raise ConfigurationError(f"{setting} must be positive, got {value}.")
    return value


@dataclass(frozen=True)
class CalculatorConfig:
    """Validated application settings."""

    log_dir: Path = Path("logs")
    history_dir: Path = Path("history")
    max_history_size: int = 1000
    auto_save: bool = True
    precision: int = 10
    max_input_value: Decimal = Decimal("1e100")
    default_encoding: str = "utf-8"

    def __post_init__(self) -> None:
        if self.precision <= 0:
            raise ConfigurationError(
                f"Precision must be positive, got {self.precision}."
            )
        if self.max_history_size <= 0:
            raise ConfigurationError(
                f"History size must be positive, got {self.max_history_size}."
            )
        if not self.max_input_value.is_finite() or self.max_input_value <= 0:
            raise ConfigurationError(
                "Maximum input value must be a positive finite number."
            )
        try:
            "probe".encode(self.default_encoding)
        except LookupError as exc:
            raise ConfigurationError(
                f"Unknown encoding {self.default_encoding!r}."
            ) from exc

    @property
    def log_file(self) -> Path:
        return self.log_dir / "calculator.log"

    @property
    def history_file(self) -> Path:
        return self.history_dir / "calculator_history.csv"

    @classmethod
    def from_env(cls) -> "CalculatorConfig":
        """Build a config from .env plus process environment."""
        load_dotenv()
        try:
            max_input = Decimal(
                os.getenv("CALCULATOR_MAX_INPUT_VALUE", "1e100")
            )
        except InvalidOperation as exc:
            raise ConfigurationError(
                "CALCULATOR_MAX_INPUT_VALUE is not a readable number."
            ) from exc

        return cls(
            log_dir=Path(os.getenv("CALCULATOR_LOG_DIR", "logs")),
            history_dir=Path(os.getenv("CALCULATOR_HISTORY_DIR", "history")),
            max_history_size=_parse_positive_int(
                os.getenv("CALCULATOR_MAX_HISTORY_SIZE", "1000"),
                "CALCULATOR_MAX_HISTORY_SIZE",
            ),
            auto_save=_parse_bool(
                os.getenv("CALCULATOR_AUTO_SAVE", "true"),
                "CALCULATOR_AUTO_SAVE",
            ),
            precision=_parse_positive_int(
                os.getenv("CALCULATOR_PRECISION", "10"),
                "CALCULATOR_PRECISION",
            ),
            max_input_value=max_input,
            default_encoding=os.getenv(
                "CALCULATOR_DEFAULT_ENCODING", "utf-8"
            ),
        )