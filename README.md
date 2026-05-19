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
from python_utils.money import format_currency, allocate, round_half_up
```

### Dates

```python
from python_utils.dates import now_utc, parse_duration, to_iso

now = now_utc()
delta = parse_duration("7days")
print(to_iso(now))
```

### Money

```python
from decimal import Decimal
from python_utils.money import format_currency, allocate

print(format_currency(Decimal("1234.5")))   # $1,234.50
shares = allocate(Decimal("100.00"), [1, 2, 3])
```

## Requirements

Python 3.11+

## License

MIT
