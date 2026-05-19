# python-utils-rondomondo

Reusable Python utilities for dates and money.

## Install

```bash
pip install python-utils-rondomondo
```

Or with `uv`:

```bash
uv add python-utils-rondomondo
```

## Usage

```python
from python_utils.dates import now_utc, parse_duration, date_windows
from python_utils.money import to_money, fmt_accounting, format_currency, allocate
```

### Dates

| Function | Description |
|---|---|
| `now_utc(microsecond=False)` | Current UTC datetime, always timezone-aware |
| `to_iso(dt, timespec="seconds")` | Format datetime as ISO 8601 string (space separator) |
| `from_iso(s)` | Parse ISO 8601 string to datetime |
| `parse_duration(s)` | Parse human duration like `"7days"`, `"3hrs"`, `"90secs"` to `timedelta` |
| `midnight_before(dt)` | Midnight at the start of the day before `dt` |
| `date_windows(start, end, window)` | Split a range into non-overlapping `timedelta` windows |
| `is_leap(year)` | True if the given year is a leap year |
| `same_day_next_year(dt)` | Advance by one calendar year, clamping Feb 29 to Feb 28 |

```python
from python_utils.dates import now_utc, parse_duration, date_windows, to_iso
from datetime import timedelta

now = now_utc()
end = now + parse_duration("7days")
windows = date_windows(now, end, timedelta(days=2))
print(to_iso(now))  # '2026-05-19 14:30:00+00:00'
```

### Money

| Function | Description |
|---|---|
| `to_money(value)` | Convert `str`, `int`, or `Decimal` to a cent-quantised `Decimal` (half-up) |
| `to_decimal(value)` | Convert `int`, `float`, `str`, or `Decimal` to `Decimal` without rounding |
| `round_half_up(amount, places=2)` | Round using half-up convention |
| `round_bankers(amount, places=2)` | Round using banker's rounding (half to even) |
| `truncate(amount, places=2)` | Truncate toward zero |
| `format_currency(amount, symbol="$", thousands=True)` | Format `Decimal` as a currency string |
| `parse_currency(s)` | Parse a currency string like `"$1,234.56"` or `"-£99.00"` to `Decimal` |
| `fmt_accounting(value)` | Accounting convention: negatives as `(120.00)`, positives as `500.00 ` |
| `allocate(amount, ratios)` | Distribute amount across ratios with no penny lost or gained |

```python
from decimal import Decimal
from python_utils.money import to_money, format_currency, fmt_accounting, allocate

price = to_money("19.99")
tax   = to_money(price * Decimal("0.1"))  # 2.00
total = price + tax                       # 21.99

print(format_currency(total))             # '$21.99'
print(fmt_accounting(Decimal("-120.00"))) # '(120.00)'
print(fmt_accounting(Decimal("500.00"))) # '500.00 '

shares = allocate(Decimal("100.00"), [1, 2, 3])  # [33.33, 33.33, 33.34] (sums exactly)
```

## Examples

### F-string formatting reference

[`src/python_utils/examples/fstrings.py`](src/python_utils/examples/fstrings.py) is a runnable reference script covering the full range of Python f-string format specs, using an invoice as the running example:

- Number formatting: decimal places, thousands separators, alignment, currency symbols
- Sign formatting: explicit `+`, space padding, accounting parentheses
- Integer bases: hex, octal, binary, scientific notation, percent
- String alignment, padding, fill characters, truncation
- Expressions, conditionals, and method calls inside f-strings
- Conversion flags: `!s`, `!r`, `!a`
- A complete invoice table tying all patterns together

```bash
python src/python_utils/examples/fstrings.py
```

## Requirements

Python 3.12+

## License

MIT
