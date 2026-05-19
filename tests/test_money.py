"""Tests for python_utils.money."""

import pytest
from decimal import Decimal, InvalidOperation

from python_utils.money import (
    CENT,
    allocate,
    fmt_accounting,
    format_currency,
    parse_currency,
    round_bankers,
    round_half_up,
    to_decimal,
    to_money,
    truncate,
)


class TestToDecimal:
    def test_int(self) -> None:
        assert to_decimal(5) == Decimal("5")

    def test_float(self) -> None:
        assert to_decimal(1.5) == Decimal("1.5")

    def test_float_precision(self) -> None:
        # Via str conversion, float precision artefacts are avoided
        result = to_decimal(0.1)
        assert result == Decimal("0.1")

    def test_string(self) -> None:
        assert to_decimal("3.14") == Decimal("3.14")

    def test_decimal_passthrough(self) -> None:
        d = Decimal("9.99")
        assert to_decimal(d) == d

    def test_negative(self) -> None:
        assert to_decimal(-7) == Decimal("-7")

    def test_zero(self) -> None:
        assert to_decimal(0) == Decimal("0")

    def test_invalid_string(self) -> None:
        with pytest.raises(InvalidOperation):
            to_decimal("not-a-number")


class TestRoundHalfUp:
    def test_rounds_half_up(self) -> None:
        assert round_half_up(Decimal("2.225")) == Decimal("2.23")

    def test_rounds_down_below_half(self) -> None:
        assert round_half_up(Decimal("2.224")) == Decimal("2.22")

    def test_negative_half(self) -> None:
        # ROUND_HALF_UP rounds away from zero for negatives, so -2.225 -> -2.23
        assert round_half_up(Decimal("-2.225")) == Decimal("-2.23")

    def test_custom_places(self) -> None:
        assert round_half_up(Decimal("1.5555"), places=3) == Decimal("1.556")

    def test_already_rounded(self) -> None:
        assert round_half_up(Decimal("1.00")) == Decimal("1.00")

    def test_zero(self) -> None:
        assert round_half_up(Decimal("0")) == Decimal("0.00")


class TestRoundBankers:
    def test_half_rounds_to_even_up(self) -> None:
        # 2.225 -> nearest even is 2.22 (even) or 2.23 -- last retained digit 2 is even -> 2.22
        assert round_bankers(Decimal("2.235")) == Decimal("2.24")

    def test_half_rounds_to_even_down(self) -> None:
        assert round_bankers(Decimal("2.225")) == Decimal("2.22")

    def test_differs_from_half_up(self) -> None:
        # Banker's rounds 0.5 to 0 (even), half-up rounds to 1
        assert round_bankers(Decimal("0.5"), places=0) == Decimal("0")
        assert round_half_up(Decimal("0.5"), places=0) == Decimal("1")

    def test_custom_places(self) -> None:
        assert round_bankers(Decimal("1.2345"), places=3) == Decimal("1.234")

    def test_zero(self) -> None:
        assert round_bankers(Decimal("0")) == Decimal("0.00")


class TestTruncate:
    def test_truncates_toward_zero(self) -> None:
        assert truncate(Decimal("1.999")) == Decimal("1.99")

    def test_negative_truncates_toward_zero(self) -> None:
        assert truncate(Decimal("-1.999")) == Decimal("-1.99")

    def test_exact_value_unchanged(self) -> None:
        assert truncate(Decimal("1.23")) == Decimal("1.23")

    def test_custom_places(self) -> None:
        assert truncate(Decimal("3.14159"), places=3) == Decimal("3.141")

    def test_zero_places(self) -> None:
        assert truncate(Decimal("9.99"), places=0) == Decimal("9")

    def test_zero(self) -> None:
        assert truncate(Decimal("0.009")) == Decimal("0.00")


class TestFormatCurrency:
    def test_basic(self) -> None:
        assert format_currency(Decimal("1234.56")) == "$1,234.56"

    def test_no_thousands(self) -> None:
        assert format_currency(Decimal("1234.56"), thousands=False) == "$1234.56"

    def test_custom_symbol(self) -> None:
        assert format_currency(Decimal("99.00"), symbol="£") == "£99.00"

    def test_negative(self) -> None:
        assert format_currency(Decimal("-50.00")) == "-$50.00"

    def test_zero(self) -> None:
        assert format_currency(Decimal("0")) == "$0.00"

    def test_rounds_before_formatting(self) -> None:
        assert format_currency(Decimal("1.005")) == "$1.01"

    def test_large_number(self) -> None:
        assert format_currency(Decimal("1000000.00")) == "$1,000,000.00"

    def test_small_fraction(self) -> None:
        assert format_currency(Decimal("0.999")) == "$1.00"

    def test_euro_symbol(self) -> None:
        assert format_currency(Decimal("500.00"), symbol="€") == "€500.00"


class TestParseCurrency:
    def test_dollars(self) -> None:
        assert parse_currency("$1,234.56") == Decimal("1234.56")

    def test_negative(self) -> None:
        assert parse_currency("-£99.00") == Decimal("-99.00")

    def test_no_cents(self) -> None:
        assert parse_currency("€500") == Decimal("500")

    def test_whitespace_stripped(self) -> None:
        assert parse_currency("  $10.00  ") == Decimal("10.00")

    def test_positive_sign_stripped(self) -> None:
        assert parse_currency("+$5.00") == Decimal("5.00")

    def test_plain_number(self) -> None:
        assert parse_currency("42.50") == Decimal("42.50")

    def test_zero(self) -> None:
        assert parse_currency("$0.00") == Decimal("0.00")

    def test_roundtrip(self) -> None:
        original = Decimal("1234.56")
        assert parse_currency(format_currency(original)) == original


class TestAllocate:
    def test_even_split(self) -> None:
        result = allocate(Decimal("10.00"), [1, 1])
        assert result == [Decimal("5.00"), Decimal("5.00")]

    def test_ratio_split(self) -> None:
        result = allocate(Decimal("10.00"), [1, 2, 3])
        assert sum(result) == Decimal("10.00")
        assert result[0] < result[1] < result[2]

    def test_sums_to_original(self) -> None:
        amount = Decimal("10.01")
        result = allocate(amount, [1, 2, 3])
        assert sum(result) == amount

    def test_indivisible_penny(self) -> None:
        # $0.01 split 1:1 -- one side gets the penny
        result = allocate(Decimal("0.01"), [1, 1])
        assert sum(result) == Decimal("0.01")
        assert sorted(result) == [Decimal("0.00"), Decimal("0.01")]

    def test_single_ratio(self) -> None:
        result = allocate(Decimal("9.99"), [1])
        assert result == [Decimal("9.99")]

    def test_zero_ratios_raises(self) -> None:
        with pytest.raises(ValueError, match="Ratios must sum to a positive number"):
            allocate(Decimal("10.00"), [0, 0])

    def test_zero_amount(self) -> None:
        result = allocate(Decimal("0.00"), [1, 2, 3])
        assert all(r == Decimal("0.00") for r in result)
        assert sum(result) == Decimal("0.00")

    def test_large_amount(self) -> None:
        amount = Decimal("1000000.00")
        result = allocate(amount, [1, 1])
        assert sum(result) == amount
        assert result[0] == Decimal("500000.00")

    def test_unequal_ratios(self) -> None:
        result = allocate(Decimal("100.00"), [3, 7])
        assert sum(result) == Decimal("100.00")
        assert result[0] == Decimal("30.00")
        assert result[1] == Decimal("70.00")

    def test_cent_constant(self) -> None:
        assert CENT == Decimal("0.01")


class TestToMoney:
    def test_string(self) -> None:
        assert to_money("19.99") == Decimal("19.99")

    def test_int(self) -> None:
        assert to_money(5) == Decimal("5.00")

    def test_decimal_passthrough(self) -> None:
        assert to_money(Decimal("3.14")) == Decimal("3.14")

    def test_rounds_half_up(self) -> None:
        # 0.1 * 19.99 = 1.999 -> rounds to 2.00
        assert to_money(Decimal("1.999")) == Decimal("2.00")

    def test_rounds_down_below_half(self) -> None:
        assert to_money(Decimal("1.994")) == Decimal("1.99")

    def test_zero(self) -> None:
        assert to_money(0) == Decimal("0.00")

    def test_negative(self) -> None:
        assert to_money("-9.995") == Decimal("-10.00")


class TestFmtAccounting:
    def test_positive(self) -> None:
        assert fmt_accounting(Decimal("500.00")) == "500.00 "

    def test_negative_parentheses(self) -> None:
        assert fmt_accounting(Decimal("-120.00")) == "(120.00)"

    def test_zero_is_positive(self) -> None:
        assert fmt_accounting(Decimal("0.00")) == "0.00 "

    def test_thousands_separator(self) -> None:
        assert fmt_accounting(Decimal("1234567.89")) == "1,234,567.89 "

    def test_negative_thousands(self) -> None:
        assert fmt_accounting(Decimal("-1234.56")) == "(1,234.56)"

    def test_trailing_space_pads_positive(self) -> None:
        # Trailing space on positives reserves room for a closing paren on the right
        assert fmt_accounting(Decimal("100.00")).endswith(" ")
