from __future__ import annotations

from datetime import date, datetime, time, timedelta, timezone
import re
from typing import Any, Mapping, Sequence
from zoneinfo import ZoneInfo


MARKET_TIMEZONE = ZoneInfo("America/New_York")
VIEWER_TIMEZONE = ZoneInfo("Asia/Seoul")
REGULAR_OPEN = time(9, 30)
REGULAR_CLOSE = time(16, 0)


def _records(value: Any) -> list[dict[str, Any]]:
    if value is None:
        return []
    if hasattr(value, "to_dict"):
        rows = value.to_dict(orient="records")
        return [dict(row) for row in rows]
    if isinstance(value, Sequence) and not isinstance(
        value,
        (str, bytes, bytearray),
    ):
        return [dict(row) for row in value if isinstance(row, Mapping)]
    return []


def _iso_date(value: Any) -> str | None:
    text = str(value or "").strip()[:10]
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError:
        return None


def _utc_iso(local_date: date, local_time: time) -> str:
    return (
        datetime.combine(local_date, local_time, MARKET_TIMEZONE)
        .astimezone(timezone.utc)
        .isoformat(timespec="seconds")
    )


def _early_close_time(row: Mapping[str, Any]) -> time | None:
    label = str(
        row.get("Event Time")
        or row.get("event_time_label")
        or ""
    ).strip()
    match = re.search(r"(?<!\d)(\d{1,2}):(\d{2})(?!\d)", label)
    if match is None:
        return None
    hour, minute = int(match.group(1)), int(match.group(2))
    if not (0 <= hour <= 23 and 0 <= minute <= 59):
        return None
    return time(hour, minute)


def build_us_market_session_model(
    *,
    generated_at: datetime,
    holiday_rows: Any = None,
    early_close_rows: Any = None,
    horizon_days: int = 15,
) -> dict[str, Any]:
    """Build a bounded regular-session schedule without provider access."""

    now_utc = (
        generated_at.replace(tzinfo=timezone.utc)
        if generated_at.tzinfo is None
        else generated_at.astimezone(timezone.utc)
    )
    start_date = now_utc.astimezone(MARKET_TIMEZONE).date()
    holidays = {
        on_date: str(row.get("Title") or "미국 증시 휴장")
        for row in _records(holiday_rows)
        if (on_date := _iso_date(row.get("Date")))
    }
    early_close_rows_by_date = {
        on_date: row
        for row in _records(early_close_rows)
        if (on_date := _iso_date(row.get("Date")))
    }
    early_close_times = {
        on_date: parsed
        for on_date, row in early_close_rows_by_date.items()
        if (parsed := _early_close_time(row)) is not None
    }
    warnings = [
        f"조기폐장 시간 확인 필요: {on_date}"
        for on_date in early_close_rows_by_date
        if on_date not in early_close_times
    ]
    schedule: list[dict[str, Any]] = []
    for offset in range(max(8, min(int(horizon_days), 31))):
        local_date = start_date + timedelta(days=offset)
        trade_date = local_date.isoformat()
        if local_date.weekday() >= 5:
            schedule.append(
                {
                    "trade_date": trade_date,
                    "day_kind": "WEEKEND",
                    "holiday_label": "주말",
                    "open_at_utc": None,
                    "close_at_utc": None,
                    "is_early_close": False,
                }
            )
            continue
        if trade_date in holidays:
            schedule.append(
                {
                    "trade_date": trade_date,
                    "day_kind": "HOLIDAY",
                    "holiday_label": holidays[trade_date],
                    "open_at_utc": None,
                    "close_at_utc": None,
                    "is_early_close": False,
                }
            )
            continue
        schedule.append(
            {
                "trade_date": trade_date,
                "day_kind": "TRADING_DAY",
                "holiday_label": None,
                "open_at_utc": _utc_iso(local_date, REGULAR_OPEN),
                "close_at_utc": _utc_iso(
                    local_date,
                    early_close_times.get(trade_date, REGULAR_CLOSE),
                ),
                "is_early_close": trade_date in early_close_times,
            }
        )
    covered_years = sorted({int(day[:4]) for day in holidays})
    required_years = sorted({int(row["trade_date"][:4]) for row in schedule})
    return {
        "schema_version": "market_session_v1",
        "generated_at_utc": now_utc.isoformat(timespec="seconds"),
        "timezones": {
            "market": str(MARKET_TIMEZONE),
            "viewer": str(VIEWER_TIMEZONE),
        },
        "calendar_quality": (
            "CONFIRMED"
            if set(required_years).issubset(covered_years) and not warnings
            else "LIMITED"
        ),
        "warnings": warnings,
        "schedule": schedule,
    }


__all__ = ["build_us_market_session_model"]
