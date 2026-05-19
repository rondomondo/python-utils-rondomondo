from decimal import Decimal, ROUND_HALF_UP, ROUND_HALF_EVEN, ROUND_DOWN
from typing import Sequence

CENT = Decimal("0.01")


def to_money(value: str | int | Decimal) -> Decimal:
    """Convert a value to a Decimal rounded to the nearest cent (half-up).

    Args:
        value: a string, integer, or Decimal monetary amount.

    Returns:
        Decimal quantized to two decimal places.
    """
    return Decimal(str(value)).quantize(CENT, rounding=ROUND_HALF_UP)


def fmt_accounting(value: Decimal) -> str:
    """Format a Decimal using accounting convention: negatives in parentheses.

    Args:
        value: the amount to format.

    Returns:
        A string like '1,234.56 ' for positives or '(1,234.56)' for negatives.
        Positive values are padded with a trailing space so columns align.
    """
    if value < 0:
        return f"({abs(value):,.2f})"
    return f"{value:,.2f} "


def to_decimal(value: int | float | str | Decimal) -> Decimal:
    """Convert a numeric value to Decimal."""
    return Decimal(str(value))

def round_half_up(amount: Decimal, places: int = 2) -> Decimal:
    """Round using half-up convention."""
    quantize_str = Decimal(10) ** -places
    return amount.quantize(quantize_str, rounding=ROUND_HALF_UP)

def round_bankers(amount: Decimal, places: int = 2) -> Decimal:
    """Round using banker's rounding (round half to even)."""
    quantize_str = Decimal(10) ** -places
    return amount.quantize(quantize_str, rounding=ROUND_HALF_EVEN)

def truncate(amount: Decimal, places: int = 2) -> Decimal:
    """Truncate toward zero."""
    quantize_str = Decimal(10) ** -places
    return amount.quantize(quantize_str, rounding=ROUND_DOWN)

def format_currency(amount: Decimal, symbol: str = "$", thousands: bool = True) -> str:
    """Format a Decimal as a currency string."""
    rounded = round_half_up(amount)
    negative = rounded < 0
    abs_val = abs(rounded)
    integer_part, _, frac_part = f"{abs_val:.2f}".partition(".")
    if thousands:
        integer_part = f"{int(integer_part):,}"
    sign = "-" if negative else ""
    return f"{sign}{symbol}{integer_part}.{frac_part}"

def parse_currency(s: str) -> Decimal:
    """Parse a currency string like '$1,234.56' or '-£99.00' to Decimal."""
    cleaned = s.strip().lstrip("+-")
    sign = -1 if s.strip().startswith("-") else 1
    cleaned = "".join(c for c in cleaned if c.isdigit() or c == ".")
    return Decimal(cleaned) * sign

def allocate(amount: Decimal, ratios: Sequence[int]) -> list[Decimal]:
    """Distribute amount across ratios with no penny lost or gained."""
    total = sum(ratios)
    if total == 0:
        raise ValueError("Ratios must sum to a positive number")
    share = [amount * Decimal(r) / Decimal(total) for r in ratios]
    floored = [truncate(s) for s in share]
    remainders = [(share[i] - floored[i], i) for i in range(len(share))]
    leftover = amount - sum(floored)
    remainders.sort(key=lambda x: x[0], reverse=True)
    cents = int(round(leftover / CENT))
    for i in range(cents):
        floored[remainders[i][1]] += CENT
    return floored
