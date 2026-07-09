"""Tests for logging setup."""

import logging

from app.calculator_config import CalculatorConfig
from app.logger import LOGGER_NAME, configure_logging, get_logger


def _config(tmp_path):
    return CalculatorConfig(
        log_dir=tmp_path / "logs", history_dir=tmp_path / "history"
    )


def test_configure_creates_dir_and_writes(tmp_path):
    config = _config(tmp_path)
    logger = configure_logging(config)
    logger.info("probe entry %d", 7)
    for handler in logger.handlers:
        handler.flush()
    assert config.log_file.exists()
    assert "probe entry 7" in config.log_file.read_text()


def test_configure_is_idempotent(tmp_path):
    config = _config(tmp_path)
    configure_logging(config)
    before = len(logging.getLogger(LOGGER_NAME).handlers)
    configure_logging(config)
    assert len(logging.getLogger(LOGGER_NAME).handlers) == before


def test_get_logger_returns_the_named_logger():
    assert get_logger().name == LOGGER_NAME