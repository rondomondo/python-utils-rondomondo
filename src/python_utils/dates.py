import calendar
import re
from datetime import datetime, timedelta, timezone

_UNIT_MAP: dict[str, str] = {
    unit: param
    for param, units in {
        "weeks":   ["w", "wk", "wks", "week", "weeks"],
        "days":    ["d", "day", "days"],
        "hours":   ["h", "hr", "hrs", "hour", "hours"],
        "minutes": ["m", "min", "mins", "minute", "minutes"],
        "seconds": ["s", "sec", "secs", "second", "seconds"],
    }.items()
    for unit in units
}


def now_utc(microsecond: bool = False) -> datetime:
    """Return the current UTC datetime, always timezone-aware."""
    dt = datetime.now(timezone.utc)
    return dt if microsecond else dt.replace(microsecond=0)


def to_iso(dt: datetime, timespec: str = "seconds") -> str:
    """Format a datetime as an ISO 8601 string."""
    return dt.isoformat(sep=" ", timespec=timespec)


def from_iso(s: str) -> datetime:
    """Parse an ISO 8601 string to a datetime."""
    return datetime.fromisoformat(s)


def parse_duration(duration: str) -> timedelta:
    """Parse a human duration string like '7days', '3hrs', '90secs' to timedelta."""
    duration = re.sub(r"\s+", "", duration.lower())
    m_int = re.search(r"\d+", duration)
    m_unit = re.search(r"[a-z]+", duration)
    if not m_int or not m_unit:
        raise ValueError(f"Cannot parse duration: {duration!r}")
    unit = m_unit.group()
    param = _UNIT_MAP.get(unit)
    if param is None:
        raise ValueError(f"Unknown unit {unit!r} in {duration!r}")
    return timedelta(**{param: int(m_int.group())})


def midnight_before(dt: datetime) -> datetime:
    """Return midnight at the start of the day before dt."""
    day_start = datetime.combine(dt.date(), datetime.min.time(), tzinfo=dt.tzinfo)
    return day_start - timedelta(days=1)


def date_windows(start: datetime, end: datetime, window: timedelta) -> list[tuple[datetime, datetime]]:
    """Split [start, end] into non-overlapping windows of the given size."""
    windows = []
    cursor = start
    while cursor < end:
        win_end = min(cursor + window, end)
        windows.append((cursor, win_end))
        cursor = win_end
    return windows


def is_leap(year: int) -> bool:
    """Return True if the given year is a leap year."""
    return calendar.isleap(year)


def same_day_next_year(dt: datetime) -> datetime:
    """Advance by one calendar year, clamping Feb 29 to Feb 28 in non-leap years."""
    target_year = dt.year + 1
    target_day = min(dt.day, calendar.monthrange(target_year, dt.month)[1])
    return dt.replace(year=target_year, day=target_day)
