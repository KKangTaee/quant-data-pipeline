from __future__ import annotations

from datetime import date, datetime, time, timedelta
from zoneinfo import ZoneInfo


US_EASTERN_TZ = ZoneInfo("America/New_York")
US_MARKET_CLOSE_TIME = time(16, 0)
US_MARKET_EARLY_CLOSE_TIME = time(13, 0)


def _nth_weekday(year: int, month: int, weekday: int, occurrence: int) -> date:
    current = date(year, month, 1)
    days_until_weekday = (weekday - current.weekday()) % 7
    return current + timedelta(days=days_until_weekday + 7 * (occurrence - 1))


def _last_weekday(year: int, month: int, weekday: int) -> date:
    if month == 12:
        current = date(year + 1, 1, 1) - timedelta(days=1)
    else:
        current = date(year, month + 1, 1) - timedelta(days=1)
    return current - timedelta(days=(current.weekday() - weekday) % 7)


def _observed_fixed_holiday(year: int, month: int, day: int) -> date:
    holiday = date(year, month, day)
    if holiday.weekday() == 5:
        return holiday - timedelta(days=1)
    if holiday.weekday() == 6:
        return holiday + timedelta(days=1)
    return holiday


def _easter_date(year: int) -> date:
    a = year % 19
    b = year // 100
    c = year % 100
    d = b // 4
    e = b % 4
    f = (b + 8) // 25
    g = (b - f + 1) // 3
    h = (19 * a + b - d - g + 15) % 30
    i = c // 4
    k = c % 4
    l = (32 + 2 * e + 2 * i - h - k) % 7
    m = (a + 11 * h + 22 * l) // 451
    month = (h + l - 7 * m + 114) // 31
    day = ((h + l - 7 * m + 114) % 31) + 1
    return date(year, month, day)


def _nyse_holidays(year: int) -> set[date]:
    holidays: set[date] = {
        _nth_weekday(year, 1, 0, 3),
        _nth_weekday(year, 2, 0, 3),
        _easter_date(year) - timedelta(days=2),
        _last_weekday(year, 5, 0),
        _nth_weekday(year, 9, 0, 1),
        _nth_weekday(year, 11, 3, 4),
    }
    for holiday_year, month, day in [
        (year, 1, 1),
        (year + 1, 1, 1),
        (year, 6, 19),
        (year, 7, 4),
        (year, 12, 25),
    ]:
        observed = _observed_fixed_holiday(holiday_year, month, day)
        if observed.year == year:
            holidays.add(observed)
    return holidays


def _nyse_early_close_dates(year: int) -> set[date]:
    holidays = _nyse_holidays(year)
    thanksgiving = _nth_weekday(year, 11, 3, 4)
    candidates = {
        thanksgiving + timedelta(days=1),
        date(year, 7, 3),
        date(year, 12, 24),
    }
    return {
        value
        for value in candidates
        if value.weekday() < 5 and value not in holidays
    }


def _is_nyse_trading_day(value: date) -> bool:
    return value.weekday() < 5 and value not in _nyse_holidays(value.year)


def previous_nyse_trading_day(value: date) -> date:
    """Return the nearest NYSE session on or before ``value``."""
    current = value
    for _ in range(15):
        if _is_nyse_trading_day(current):
            return current
        current -= timedelta(days=1)
    return value


def latest_completed_nyse_session(now: datetime | None = None) -> date:
    """Return the last fully completed NYSE session in U.S. Eastern time."""
    now_et = (now or datetime.now(tz=US_EASTERN_TZ)).astimezone(US_EASTERN_TZ)
    session_date = now_et.date()
    if not _is_nyse_trading_day(session_date):
        return previous_nyse_trading_day(session_date - timedelta(days=1))
    close_time = (
        US_MARKET_EARLY_CLOSE_TIME
        if session_date in _nyse_early_close_dates(session_date.year)
        else US_MARKET_CLOSE_TIME
    )
    if now_et.time() <= close_time:
        return previous_nyse_trading_day(session_date - timedelta(days=1))
    return session_date
