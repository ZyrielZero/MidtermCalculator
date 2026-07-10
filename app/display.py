"""Color-coded terminal output via colorama.

One module owns every ANSI decision so the REPL never touches color
codes directly. colorama's autoreset keeps each print self-contained,
and init() translates codes on Windows terminals.
"""

from __future__ import annotations

from colorama import Fore, Style, init

init(autoreset=True)


def style_banner(text: str) -> str:
    """Cyan for the startup banner and prompts."""
    return f"{Fore.CYAN}{text}{Style.RESET_ALL}"


def style_result(text: str) -> str:
    """Green for successful calculation output."""
    return f"{Fore.GREEN}{text}{Style.RESET_ALL}"


def style_error(text: str) -> str:
    """Red for anything that begins with an error marker."""
    return f"{Fore.RED}{text}{Style.RESET_ALL}"


def style_info(text: str) -> str:
    """Yellow for neutral status messages."""
    return f"{Fore.YELLOW}{text}{Style.RESET_ALL}"


def style_output(text: str) -> str:
    """Route one REPL output block to the right color."""
    if text.startswith("Error:"):
        return style_error(text)
    if "=" in text.splitlines()[0]:
        return style_result(text)
    return style_info(text)