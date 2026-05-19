"""Tests for python_utils.dates."""

import pytest
from datetime import datetime, timedelta, timezone

from python_utils.dates import (
    date_windows,
    from_iso,
    is_leap,
    midnight_before,
    now_utc,
    parse_duration,
    same_day_next_year,
    to_iso,
)

UTC = timezone.utc


class TestNowUtc:
    def test_returns_utc(self) -> None:
        dt = now_utc()
        assert dt.tzinfo == UTC

    def test_no_microseconds_by_default(self) -> None:
        dt = now_utc()
        assert dt.microsecond == 0

    def test_microseconds_when_requested(self) -> None:
        # We can only assert the function runs without raising; microseconds may be 0 by chance
        dt = now_utc(microsecond=True)
        assert dt.tzinfo == UTC

    def test_is_recent(self) -> None:
        dt = now_utc()
        delta = datetime.now(UTC) - dt
        assert abs(delta.total_seconds()) < 2


class TestToIso:
    def test_default_seconds(self) -> None:
        dt = datetime(2026, 5, 19, 14, 30, 45, tzinfo=UTC)
        assert to_iso(dt) == "2026-05-19 14:30:45+00:00"

    def test_uses_space_separator(self) -> None:
        dt = datetime(2026, 1, 1, 0, 0, 0, tzinfo=UTC)
        result = to_iso(dt)
        assert "T" not in result
        assert " " in result

    def test_milliseconds_timespec(self) -> None:
        dt = datetime(2026, 5, 19, 14, 30, 45, 123000, tzinfo=UTC)
        result = to_iso(dt, timespec="milliseconds")
        assert "123" in result

    def test_minutes_timespec(self) -> None:
        dt = datetime(2026, 5, 19, 14, 30, tzinfo=UTC)
        assert to_iso(dt, timespec="minutes") == "2026-05-19 14:30+00:00"

    def test_naive_datetime(self) -> None:
        dt = datetime(2026, 5, 19, 12, 0, 0)
        result = to_iso(dt)
        assert result == "2026-05-19 12:00:00"


class TestFromIso:
    def test_parses_space_separator(self) -> None:
        dt = from_iso("2026-05-19 14:30:45+00:00")
        assert dt == datetime(2026, 5, 19, 14, 30, 45, tzinfo=UTC)

    def test_parses_t_separator(self) -> None:
        dt = from_iso("2026-05-19T14:30:45+00:00")
        assert dt == datetime(2026, 5, 19, 14, 30, 45, tzinfo=UTC)

    def test_naive_string(self) -> None:
        dt = from_iso("2026-05-19 12:00:00")
        assert dt.year == 2026
        assert dt.tzinfo is None

    def test_roundtrip(self) -> None:
        original = datetime(2026, 5, 19, 14, 30, 45, tzinfo=UTC)
        assert from_iso(to_iso(original)) == original

    def test_invalid_raises(self) -> None:
        with pytest.raises(ValueError):
            from_iso("not-a-date")


class TestParseDuration:
    @pytest.mark.parametrize("s,expected", [
        ("7days", timedelta(days=7)),
        ("7 days", timedelta(days=7)),
        ("7d", timedelta(days=7)),
        ("7day", timedelta(days=7)),
        ("3hrs", timedelta(hours=3)),
        ("3hr", timedelta(hours=3)),
        ("3h", timedelta(hours=3)),
        ("3hours", timedelta(hours=3)),
        ("3hour", timedelta(hours=3)),
        ("90secs", timedelta(seconds=90)),
        ("90sec", timedelta(seconds=90)),
        ("90s", timedelta(seconds=90)),
        ("90seconds", timedelta(seconds=90)),
        ("90second", timedelta(seconds=90)),
        ("2weeks", timedelta(weeks=2)),
        ("2week", timedelta(weeks=2)),
        ("2wk", timedelta(weeks=2)),
        ("2wks", timedelta(weeks=2)),
        ("2w", timedelta(weeks=2)),
        ("5minutes", timedelta(minutes=5)),
        ("5minute", timedelta(minutes=5)),
        ("5min", timedelta(minutes=5)),
        ("5mins", timedelta(minutes=5)),
        ("5m", timedelta(minutes=5)),
    ])
    def test_valid_durations(self, s: str, expected: timedelta) -> None:
        assert parse_duration(s) == expected

    def test_case_insensitive(self) -> None:
        assert parse_duration("7DAYS") == timedelta(days=7)
        assert parse_duration("3HRS") == timedelta(hours=3)

    def test_whitespace_ignored(self) -> None:
        assert parse_duration("  7  days  ") == timedelta(days=7)

    def test_unknown_unit_raises(self) -> None:
        with pytest.raises(ValueError, match="Unknown unit"):
            parse_duration("5fortnights")

    def test_no_number_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot parse duration"):
            parse_duration("days")

    def test_no_unit_raises(self) -> None:
        with pytest.raises(ValueError, match="Cannot parse duration"):
            parse_duration("42")

    def test_zero_duration(self) -> None:
        assert parse_duration("0days") == timedelta(0)


class TestMidnightBefore:
    def test_basic(self) -> None:
        dt = datetime(2026, 5, 19, 14, 30, tzinfo=UTC)
        result = midnight_before(dt)
        assert result == datetime(2026, 5, 18, 0, 0, 0, tzinfo=UTC)

    def test_at_midnight(self) -> None:
        dt = datetime(2026, 5, 19, 0, 0, 0, tzinfo=UTC)
        result = midnight_before(dt)
        assert result == datetime(2026, 5, 18, 0, 0, 0, tzinfo=UTC)

    def test_first_of_month(self) -> None:
        dt = datetime(2026, 6, 1, 10, 0, tzinfo=UTC)
        result = midnight_before(dt)
        assert result == datetime(2026, 5, 31, 0, 0, 0, tzinfo=UTC)

    def test_new_years_day(self) -> None:
        dt = datetime(2026, 1, 1, 8, 0, tzinfo=UTC)
        result = midnight_before(dt)
        assert result == datetime(2025, 12, 31, 0, 0, 0, tzinfo=UTC)

    def test_preserves_timezone(self) -> None:
        dt = datetime(2026, 5, 19, 12, 0, tzinfo=UTC)
        result = midnight_before(dt)
        assert result.tzinfo == UTC

    def test_naive_datetime(self) -> None:
        dt = datetime(2026, 5, 19, 12, 0)
        result = midnight_before(dt)
        assert result == datetime(2026, 5, 18, 0, 0, 0)
        assert result.tzinfo is None


class TestDateWindows:
    def test_even_split(self) -> None:
        start = datetime(2026, 5, 1, tzinfo=UTC)
        end = datetime(2026, 5, 7, tzinfo=UTC)
        windows = date_windows(start, end, timedelta(days=2))
        assert len(windows) == 3
        assert windows[0] == (datetime(2026, 5, 1, tzinfo=UTC), datetime(2026, 5, 3, tzinfo=UTC))
        assert windows[-1] == (datetime(2026, 5, 5, tzinfo=UTC), datetime(2026, 5, 7, tzinfo=UTC))

    def test_last_window_truncated(self) -> None:
        start = datetime(2026, 5, 1, tzinfo=UTC)
        end = datetime(2026, 5, 8, tzinfo=UTC)
        windows = date_windows(start, end, timedelta(days=3))
        assert len(windows) == 3
        # Last window is only 1 day
        last_start, last_end = windows[-1]
        assert (last_end - last_start) == timedelta(days=1)

    def test_start_equals_end_empty(self) -> None:
        dt = datetime(2026, 5, 1, tzinfo=UTC)
        assert date_windows(dt, dt, timedelta(days=1)) == []

    def test_start_after_end_empty(self) -> None:
        start = datetime(2026, 5, 2, tzinfo=UTC)
        end = datetime(2026, 5, 1, tzinfo=UTC)
        assert date_windows(start, end, timedelta(days=1)) == []

    def test_windows_are_contiguous(self) -> None:
        start = datetime(2026, 1, 1, tzinfo=UTC)
        end = datetime(2026, 2, 1, tzinfo=UTC)
        windows = date_windows(start, end, timedelta(days=7))
        for i in range(len(windows) - 1):
            assert windows[i][1] == windows[i + 1][0]

    def test_single_window(self) -> None:
        start = datetime(2026, 5, 1, tzinfo=UTC)
        end = datetime(2026, 5, 3, tzinfo=UTC)
        windows = date_windows(start, end, timedelta(days=7))
        assert windows == [(start, end)]

    def test_covers_full_range(self) -> None:
        start = datetime(2026, 5, 1, tzinfo=UTC)
        end = datetime(2026, 5, 31, tzinfo=UTC)
        windows = date_windows(start, end, timedelta(days=5))
        assert windows[0][0] == start
        assert windows[-1][1] == end


class TestIsLeap:
    @pytest.mark.parametrize("year", [2000, 2004, 2008, 2024, 2400])
    def test_leap_years(self, year: int) -> None:
        assert is_leap(year) is True

    @pytest.mark.parametrize("year", [1900, 2001, 2100, 2025, 2026])
    def test_non_leap_years(self, year: int) -> None:
        assert is_leap(year) is False

    def test_century_not_divisible_by_400(self) -> None:
        assert is_leap(1900) is False

    def test_century_divisible_by_400(self) -> None:
        assert is_leap(2000) is True


class TestSameDayNextYear:
    def test_regular_date(self) -> None:
        dt = datetime(2026, 5, 19, 14, 30, tzinfo=UTC)
        result = same_day_next_year(dt)
        assert result == datetime(2027, 5, 19, 14, 30, tzinfo=UTC)

    def test_feb_29_to_non_leap_year(self) -> None:
        dt = datetime(2024, 2, 29, tzinfo=UTC)
        result = same_day_next_year(dt)
        assert result == datetime(2025, 2, 28, tzinfo=UTC)

    def test_feb_29_to_leap_year(self) -> None:
        dt = datetime(2024, 2, 29, tzinfo=UTC)
        # 2024 -> 2025 (non-leap), but test 2028 -> 2029 path differently
        # Instead test that Feb 28 in non-leap is not clamped
        dt2 = datetime(2023, 2, 28, tzinfo=UTC)
        result = same_day_next_year(dt2)
        assert result == datetime(2024, 2, 28, tzinfo=UTC)

    def test_preserves_time_and_timezone(self) -> None:
        dt = datetime(2026, 7, 4, 9, 15, 30, tzinfo=UTC)
        result = same_day_next_year(dt)
        assert result.hour == 9
        assert result.minute == 15
        assert result.second == 30
        assert result.tzinfo == UTC

    def test_dec_31(self) -> None:
        dt = datetime(2025, 12, 31, tzinfo=UTC)
        result = same_day_next_year(dt)
        assert result == datetime(2026, 12, 31, tzinfo=UTC)

    def test_jan_1(self) -> None:
        dt = datetime(2026, 1, 1, tzinfo=UTC)
        result = same_day_next_year(dt)
        assert result == datetime(2027, 1, 1, tzinfo=UTC)

    def test_naive_datetime(self) -> None:
        dt = datetime(2026, 6, 15, 12, 0)
        result = same_day_next_year(dt)
        assert result == datetime(2027, 6, 15, 12, 0)
        assert result.tzinfo is None
