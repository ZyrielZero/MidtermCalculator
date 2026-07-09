"""Tests for environment-driven configuration."""

from decimal import Decimal
from pathlib import Path

import pytest

from app.calculator_config import CalculatorConfig
from app.exceptions import ConfigurationError

ENV_KEYS = [
    "CALCULATOR_LOG_DIR",
    "CALCULATOR_HISTORY_DIR",
    "CALCULATOR_MAX_HISTORY_SIZE",
    "CALCULATOR_AUTO_SAVE",
    "CALCULATOR_PRECISION",
    "CALCULATOR_MAX_INPUT_VALUE",
    "CALCULATOR_DEFAULT_ENCODING",
]


@pytest.fixture(autouse=True)
def clean_env(monkeypatch):
    for key in ENV_KEYS:
        monkeypatch.delenv(key, raising=False)


def test_defaults_apply_when_env_is_empty():
    config = CalculatorConfig.from_env()
    assert config.precision == 10
    assert config.max_history_size == 1000
    assert config.auto_save is True
    assert config.default_encoding == "utf-8"


def test_env_overrides_are_honored(monkeypatch):
    monkeypatch.setenv("CALCULATOR_PRECISION", "4")
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", "off")
    monkeypatch.setenv("CALCULATOR_LOG_DIR", "run/logs")
    monkeypatch.setenv("CALCULATOR_MAX_INPUT_VALUE", "5e6")
    config = CalculatorConfig.from_env()
    assert config.precision == 4
    assert config.auto_save is False
    assert config.log_dir == Path("run/logs")
    assert config.max_input_value == Decimal("5e6")


def test_derived_file_paths_sit_inside_their_dirs():
    config = CalculatorConfig(log_dir=Path("a"), history_dir=Path("b"))
    assert config.log_file == Path("a/calculator.log")
    assert config.history_file == Path("b/calculator_history.csv")


@pytest.mark.parametrize("raw", ["true", "1", "YES", "on"])
def test_truthy_auto_save_spellings(monkeypatch, raw):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", raw)
    assert CalculatorConfig.from_env().auto_save is True


@pytest.mark.parametrize("raw", ["false", "0", "No", "OFF"])
def test_falsy_auto_save_spellings(monkeypatch, raw):
    monkeypatch.setenv("CALCULATOR_AUTO_SAVE", raw)
    assert CalculatorConfig.from_env().auto_save is False


@pytest.mark.parametrize(
    "key, raw",
    [
        ("CALCULATOR_PRECISION", "0"),
        ("CALCULATOR_PRECISION", "-3"),
        ("CALCULATOR_PRECISION", "ten"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "0"),
        ("CALCULATOR_MAX_HISTORY_SIZE", "lots"),
        ("CALCULATOR_AUTO_SAVE", "maybe"),
        ("CALCULATOR_MAX_INPUT_VALUE", "huge"),
        ("CALCULATOR_DEFAULT_ENCODING", "utf-999"),
    ],
)
def test_bad_env_values_raise_configuration_error(monkeypatch, key, raw):
    monkeypatch.setenv(key, raw)
    with pytest.raises(ConfigurationError):
        CalculatorConfig.from_env()


def test_direct_construction_validates_too():
    with pytest.raises(ConfigurationError):
        CalculatorConfig(max_input_value=Decimal("-5"))

        
def test_direct_construction_rejects_bad_precision():
    with pytest.raises(ConfigurationError):
        CalculatorConfig(precision=0)


def test_direct_construction_rejects_bad_history_size():
    with pytest.raises(ConfigurationError):
        CalculatorConfig(max_history_size=-1)