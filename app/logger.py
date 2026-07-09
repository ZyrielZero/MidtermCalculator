"""Logging setup for the calculator.

One named logger, one file handler pointed at the configured log
directory. configure_logging is idempotent so repeated calls (tests,
REPL restarts) never stack duplicate handlers.
"""

from __future__ import annotations

import logging

from app.calculator_config import CalculatorConfig

LOGGER_NAME = "calculator"


def configure_logging(config: CalculatorConfig) -> logging.Logger:
    """Point the calculator logger at the configured log file."""
    config.log_dir.mkdir(parents=True, exist_ok=True)
    logger = logging.getLogger(LOGGER_NAME)
    logger.setLevel(logging.INFO)

    target = str(config.log_file)
    already_attached = any(
        isinstance(h, logging.FileHandler) and h.baseFilename.endswith(target)
        for h in logger.handlers
    )
    if not already_attached:
        handler = logging.FileHandler(
            config.log_file, encoding=config.default_encoding
        )
        handler.setFormatter(
            logging.Formatter("%(asctime)s %(levelname)s %(message)s")
        )
        logger.addHandler(handler)
    return logger


def get_logger() -> logging.Logger:
    """The shared calculator logger."""
    return logging.getLogger(LOGGER_NAME)