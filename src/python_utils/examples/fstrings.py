"""F-string formatting reference - using an invoice as the running example.

Run directly to see all output:
    python src/python_utils/examples/fstrings.py
"""

from decimal import Decimal

from python_utils.money import fmt_accounting, format_currency, to_money


def section(title: str) -> None:
    print(f"\n{title}")
    print("-" * len(title))


def main() -> None:

    # Basic numbers
    section("Basic number formatting")
    amount = 1234567.891
    print(f"  plain:              {amount}")
    print(f"  2dp:                {amount:.2f}")
    print(f"  thousands + 2dp:    {amount:,.2f}")
    print(f"  right-align 15chr:  {amount:>15,.2f}")
    print(f"  dollar:             ${amount:,.2f}")
    print(f"  pound:              £{amount:,.2f}")
    print(f"  euro:               €{amount:,.2f}")

    # Alignment and padding
    section("Alignment and padding")
    label = "Total Due"
    value = 9876.50
    print(f"  left-align:   {label:<20} |")
    print(f"  right-align:  {label:>20} |")
    print(f"  centre:       {label:^20} |")
    print(f"  zero-padded:  {value:015,.2f}")
    print(f"  fill char:    {label:*^20}")

    # Sign formatting
    section("Sign formatting")
    credit = Decimal("500.00")
    debit = Decimal("-120.00")
    print(f"  explicit sign (credit): {credit:+,.2f}")
    print(f"  explicit sign (debit):  {debit:+,.2f}")
    print(f"  space for positive:     {credit: ,.2f}")
    print(f"  space for negative:     {debit: ,.2f}")

    # Accounting convention (negatives in parentheses)
    section("Accounting convention (fmt_accounting)")
    print(f"  credit: {fmt_accounting(credit)}")
    print(f"  debit:  {fmt_accounting(debit)}")
    print(f"  zero:   {fmt_accounting(Decimal('0.00'))}")

    # Integer formatting
    section("Integer formatting")
    n = 1_000_000
    print(f"  plain:         {n}")
    print(f"  thousands:     {n:,}")
    print(f"  hex:           {n:#x}")
    print(f"  octal:         {n:#o}")
    print(f"  binary:        {n:#b}")
    print(f"  scientific:    {n:e}")
    print(f"  percent:       {0.1275:.2%}")

    # String width and truncation
    section("String width and truncation")
    long_str = "Consulting services (3 days)"
    print(f"  truncate to 20:  {long_str:.20}")
    print(f"  pad to 30:       {long_str:<30}|")
    print(f"  truncate + pad:  {long_str:<30.20}|")

    # Nested expressions and conditionals
    section("Expressions inside f-strings")
    qty = 3
    unit_price = Decimal("850.00")
    line_total = qty * unit_price
    print(f"  expression:    {qty} x {unit_price} = {line_total:,.2f}")
    print(f"  conditional:   {'credit' if credit > 0 else 'debit'}")
    print(f"  method call:   {'hello world'.title()}")
    print(f"  ternary sign:  {'positive' if line_total >= 0 else 'negative'}")

    # Multiline / repr / !r !s !a conversion
    section("Conversion flags")
    sample = "cafe\u0301"  # 'cafe' + combining accent
    print(f"  !s (str):   {sample!s}")
    print(f"  !r (repr):  {sample!r}")
    print(f"  !a (ascii): {sample!a}")

    # Invoice table - pulling it all together
    section("Invoice table")
    items = [
        ("Consulting (3 days)",  3,  Decimal("850.00")),
        ("Travel expenses",      1,  Decimal("127.50")),
        ("Software licence",    12,  Decimal("29.99")),
    ]

    col_w = (30, 4, 10, 12)
    header = f"{'Description':<{col_w[0]}} {'Qty':>{col_w[1]}} {'Unit':>{col_w[2]}} {'Total':>{col_w[3]}}"
    rule = "-" * len(header)

    print(f"  {header}")
    print(f"  {rule}")

    subtotal = Decimal("0")
    for desc, qty, unit in items:
        total = to_money(qty * unit)
        subtotal += total
        print(f"  {desc:<{col_w[0]}} {qty:>{col_w[1]}} {unit:>{col_w[2]},.2f} {total:>{col_w[3]},.2f}")

    tax = to_money(subtotal * Decimal("0.20"))
    due = subtotal + tax

    print(f"  {rule}")
    print(f"  {'Subtotal':>{sum(col_w) + 3}} {subtotal:>{col_w[3]},.2f}")
    print(f"  {'VAT (20%)':>{sum(col_w) + 3}} {tax:>{col_w[3]},.2f}")
    print(f"  {'Total Due':>{sum(col_w) + 3}} {due:>{col_w[3]},.2f}")

    print(f"\n  Formatted:  {format_currency(due, symbol='EUR')}")
    print(f"  Accounting: {fmt_accounting(due)}")


if __name__ == "__main__":
    main()
