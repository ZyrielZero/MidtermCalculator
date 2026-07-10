# Advanced Calculator

A command-line calculator built around four design patterns: a Factory
creates arithmetic operations, Mementos back the undo and redo stack,
Observers log and auto-save every calculation, and Command objects
drive the REPL dispatch. All math runs on `Decimal`, so precision
rounding is exact and history survives a CSV round trip without
floating-point drift.

## Features

Ten operations (`add`, `subtract`, `multiply`, `divide`, `power`,
`root`, `modulus`, `int_divide`, `percent`, `abs_diff`), undo/redo,
persistent history through pandas CSV files, environment-driven
configuration, file logging, a decorator-generated help menu that
updates itself when operations are added, and color-coded output via
colorama.

## Installation

```bash
git clone https://github.com/ZyrielZero/MidtermCalculator.git
cd MidtermCalculator
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

## Configuration

Settings load from a `.env` file in the project root through
python-dotenv. Copy the template and adjust:

```bash
cp .env.example .env
```

| Variable | Purpose | Default |
| --- | --- | --- |
| `CALCULATOR_LOG_DIR` | Directory for the log file | `logs` |
| `CALCULATOR_HISTORY_DIR` | Directory for the history CSV | `history` |
| `CALCULATOR_MAX_HISTORY_SIZE` | Most entries kept in memory | `1000` |
| `CALCULATOR_AUTO_SAVE` | Save history after every calculation | `true` |
| `CALCULATOR_PRECISION` | Decimal places in results | `10` |
| `CALCULATOR_MAX_INPUT_VALUE` | Largest accepted operand magnitude | `1e100` |
| `CALCULATOR_DEFAULT_ENCODING` | Encoding for log and CSV files | `utf-8` |

Every value is validated at startup; a bad setting stops the
application with a `ConfigurationError` naming the variable.

## Usage

```bash
python -m app.calculator
```

Arithmetic commands take exactly two operands:

```
calc> power 2 10
power(2, 10) = 1024
calc> percent 30 120
percent(30, 120) = 25
```

Utility commands: `history` lists the session's calculations, `clear`
erases them, `undo` and `redo` walk the history stack, `save` and
`load` move history to and from the configured CSV file, `help` shows
the generated command list, and `exit` leaves the program. Errors
never crash the loop; they come back as a red `Error:` line.

## Testing

```bash
pytest --cov=app --cov-fail-under=90
```

The suite reaches 100% coverage with parameterized tests for
operation results, rejection cases, configuration parsing, CSV round
trips, and the REPL handler. Only the interactive input loop is
excluded with `# pragma: no cover`.

## Continuous Integration

GitHub Actions (`.github/workflows/python-app.yml`) runs the full
suite on every push and pull request to `main`, and fails the build
if coverage drops below 90%. The local test command above is the exact
command CI runs.

## Project layout

```
app/
  calculator.py         Engine, REPL loop, command dispatch
  calculation.py        Immutable calculation record and CSV mapping
  calculator_config.py  Environment-driven settings
  calculator_memento.py History snapshots for undo/redo
  commands.py           Command pattern: one object per REPL verb
  display.py            Colorama output styling
  exceptions.py         CalculatorError hierarchy
  help_menu.py          Decorator-built help text
  history.py            Observers and pandas persistence
  input_validators.py   Decimal parsing and bounds checks
  logger.py             File logging setup
  operations.py         Ten operations and the factory registry
tests/                  One test module per app module
```