"""Tests for colorama-based output styling."""

from colorama import Fore

from app.display import (
    style_banner,
    style_error,
    style_info,
    style_output,
    style_result,
)


def test_banner_is_cyan():
    assert style_banner("hello").startswith(Fore.CYAN)


def test_result_is_green():
    assert style_result("add(1, 2) = 3").startswith(Fore.GREEN)


def test_error_is_red():
    assert style_error("Error: nope").startswith(Fore.RED)


def test_info_is_yellow():
    assert style_info("History cleared.").startswith(Fore.YELLOW)


def test_router_sends_errors_to_red():
    assert style_output("Error: divide by zero").startswith(Fore.RED)


def test_router_sends_equations_to_green():
    assert style_output("power(2, 10) = 1024").startswith(Fore.GREEN)


def test_router_sends_status_lines_to_yellow():
    assert style_output("History is empty.").startswith(Fore.YELLOW)


def test_original_text_survives_styling():
    styled = style_output("modulus(22, 6) = 4")
    assert "modulus(22, 6) = 4" in styled