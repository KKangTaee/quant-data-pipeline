from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo


US_EASTERN_TZ = ZoneInfo("America/New_York")
KOREA_TZ = ZoneInfo("Asia/Seoul")
US_MARKET_OPEN_TIME = time(9, 30)
US_MARKET_CLOSE_TIME = time(16, 0)
US_MARKET_EARLY_CLOSE_TIME = time(13, 0)


@dataclass(frozen=True)
class MarketSessionInfo:
    session_date: date
    is_trading_day: bool
    phase: str
    reason: str
    open_at: datetime | None
    close_at: datetime | None
    next_open_at: datetime | None = None
    next_close_at: datetime | None = None
    early_close_reason: str | None = None


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


def _nyse_holidays(year: int) -> dict[date, str]:
    holidays: dict[date, str] = {
        _nth_weekday(year, 1, 0, 3): "Martin Luther King Jr. Day",
        _nth_weekday(year, 2, 0, 3): "Washington's Birthday",
        _easter_date(year) - timedelta(days=2): "Good Friday",
        _last_weekday(year, 5, 0): "Memorial Day",
        _nth_weekday(year, 9, 0, 1): "Labor Day",
        _nth_weekday(year, 11, 3, 4): "Thanksgiving Day",
    }
    for holiday_year, label, month, day in [
        (year, "New Year's Day", 1, 1),
        (year + 1, "New Year's Day", 1, 1),
        (year, "Juneteenth National Independence Day", 6, 19),
        (year, "Independence Day", 7, 4),
        (year, "Christmas Day", 12, 25),
    ]:
        observed = _observed_fixed_holiday(holiday_year, month, day)
        if observed.year == year:
            suffix = " (observed)" if observed != date(holiday_year, month, day) else ""
            holidays[observed] = f"{label}{suffix}"
    return holidays


def _nyse_early_closes(year: int) -> dict[date, str]:
    holidays = _nyse_holidays(year)
    thanksgiving = _nth_weekday(year, 11, 3, 4)
    candidates = {
        thanksgiving + timedelta(days=1): "Day after Thanksgiving",
        date(year, 7, 3): "Independence Day early close",
        date(year, 12, 24): "Christmas Eve",
    }
    return {
        value: reason
        for value, reason in candidates.items()
        if value.weekday() < 5 and value not in holidays
    }


def _market_datetime(session_date: date, session_time: time) -> datetime:
    return datetime.combine(session_date, session_time, tzinfo=US_EASTERN_TZ)


def _market_session_for_date(session_date: date) -> MarketSessionInfo:
    if session_date.weekday() >= 5:
        return MarketSessionInfo(
            session_date=session_date,
            is_trading_day=False,
            phase="휴장",
            reason="주말",
            open_at=None,
            close_at=None,
        )
    holidays = _nyse_holidays(session_date.year)
    if session_date in holidays:
        return MarketSessionInfo(
            session_date=session_date,
            is_trading_day=False,
            phase="휴장",
            reason=holidays[session_date],
            open_at=None,
            close_at=None,
        )
    early_close_reason = _nyse_early_closes(session_date.year).get(session_date)
    close_time = US_MARKET_EARLY_CLOSE_TIME if early_close_reason else US_MARKET_CLOSE_TIME
    return MarketSessionInfo(
        session_date=session_date,
        is_trading_day=True,
        phase="거래일",
        reason="조기 종료" if early_close_reason else "정규장",
        open_at=_market_datetime(session_date, US_MARKET_OPEN_TIME),
        close_at=_market_datetime(session_date, close_time),
        early_close_reason=early_close_reason,
    )


def _next_market_session(start_date: date) -> MarketSessionInfo:
    for offset in range(1, 15):
        candidate = _market_session_for_date(start_date + timedelta(days=offset))
        if candidate.is_trading_day:
            return candidate
    return _market_session_for_date(start_date)


def _previous_market_session(start_date: date) -> MarketSessionInfo:
    for offset in range(1, 15):
        candidate = _market_session_for_date(start_date - timedelta(days=offset))
        if candidate.is_trading_day:
            return candidate
    return _market_session_for_date(start_date)


def _current_market_session_info(now: datetime | None = None) -> MarketSessionInfo:
    now_et = (now or datetime.now(tz=US_EASTERN_TZ)).astimezone(US_EASTERN_TZ)
    session = _market_session_for_date(now_et.date())
    if not session.is_trading_day:
        next_session = _next_market_session(session.session_date)
        return MarketSessionInfo(
            session_date=session.session_date,
            is_trading_day=False,
            phase="휴장",
            reason=session.reason,
            open_at=None,
            close_at=None,
            next_open_at=next_session.open_at,
            next_close_at=next_session.close_at,
        )
    if session.open_at and now_et < session.open_at:
        phase = "장 시작 전"
    elif session.close_at and now_et <= session.close_at:
        phase = "장중"
    else:
        phase = "장 종료"
    return MarketSessionInfo(
        session_date=session.session_date,
        is_trading_day=True,
        phase=phase,
        reason=session.reason,
        open_at=session.open_at,
        close_at=session.close_at,
        early_close_reason=session.early_close_reason,
    )


def _format_et_time(value: datetime | None) -> str:
    return value.strftime("%H:%M ET") if value else "-"


def _format_kst_time(value: datetime | None) -> str:
    return value.astimezone(KOREA_TZ).strftime("%m-%d %H:%M KST") if value else "-"


def _format_session_time_item(label: str, value: datetime | None) -> dict[str, str]:
    return {
        "label": label,
        "value": _format_kst_time(value),
        "detail": _format_et_time(value),
    }


def _market_session_banner_model(now: datetime | None = None) -> dict[str, Any]:
    session = _current_market_session_info(now)
    if session.is_trading_day:
        detail = session.reason
        if session.early_close_reason:
            detail = f"{detail}: {session.early_close_reason}"
        return {
            "tone": "positive" if session.phase == "장중" else "neutral",
            "status": session.phase,
            "title": f"미국장 세션 · {session.session_date.isoformat()} ET",
            "detail": detail,
            "items": [
                _format_session_time_item("Open", session.open_at),
                _format_session_time_item("Close", session.close_at),
                {"label": "Timezone", "value": "KST", "detail": "ET shown below"},
            ],
        }
    return {
        "tone": "warning",
        "status": "휴장",
        "title": f"미국장 휴장 · {session.session_date.isoformat()} ET",
        "detail": f"사유: {session.reason}",
        "items": [
            {"label": "Reason", "value": session.reason, "detail": "NYSE closed"},
            _format_session_time_item("Next Open", session.next_open_at),
            _format_session_time_item("Next Close", session.next_close_at),
        ],
    }


def _market_context_session_payload(now: datetime | None = None) -> dict[str, Any]:
    session = _current_market_session_info(now)
    basis_session = (
        session
        if session.is_trading_day and session.phase in {"장중", "장 종료"}
        else _previous_market_session(session.session_date)
    )
    return {
        "phase": session.phase,
        "is_trading_day": session.is_trading_day,
        "is_market_open_now": session.is_trading_day and session.phase == "장중",
        "session_date": session.session_date.isoformat(),
        "basis_date": basis_session.session_date.isoformat(),
        "reason": session.reason,
    }


def _snapshot_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def _price_basis_status_item(snapshot: dict[str, Any]) -> dict[str, Any]:
    coverage = dict(snapshot.get("coverage") or {})
    price_mode = str(coverage.get("price_mode") or "")
    latest_raw = coverage.get("latest_raw_date")
    effective_end = coverage.get("effective_end_date")
    snapshot_time = coverage.get("snapshot_time_utc")

    if snapshot_time or price_mode == "Intraday Snapshot":
        title = "Effective Quote Time"
        value = snapshot_time or effective_end
        detail = f"{price_mode or 'Intraday Snapshot'} · previous close basis"
    else:
        title = "Effective EOD Date"
        value = effective_end
        if latest_raw and effective_end and str(latest_raw) != str(effective_end):
            detail = f"latest raw {latest_raw} is sparse; using {effective_end}"
        elif latest_raw:
            detail = f"latest raw {latest_raw}"
        else:
            detail = price_mode or "EOD DB"

    return {
        "title": title,
        "value": _snapshot_value(value),
        "detail": detail,
        "tone": "positive" if value else "warning",
    }


def _snapshot_status_items(snapshot: dict[str, Any]) -> list[dict[str, Any]]:
    coverage = dict(snapshot.get("coverage") or {})
    refresh_state = dict(coverage.get("refresh_state") or {})
    stale_days = coverage.get("stale_days")
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is not None:
        age_value = f"{int(stale_minutes)}m"
        age_detail = "from intraday snapshot"
        age_tone = refresh_state.get("tone") or ("positive" if int(stale_minutes) <= 10 else "warning")
    else:
        age_value = _snapshot_value(stale_days)
        age_detail = "calendar days from effective date"
        age_tone = "positive" if stale_days is not None and int(stale_days) <= 3 else "warning"
    returnable = coverage.get("returnable_count") or 0
    universe_count = coverage.get("universe_count") or 0
    coverage_text = f"{returnable} / {universe_count}" if universe_count else "-"
    returnable_pct = coverage.get("returnable_pct")
    coverage_detail = f"{float(returnable_pct):.2f}% returnable" if returnable_pct is not None else None
    missing_count = coverage.get("missing_count") or 0
    failed_count = coverage.get("failed_count") or missing_count
    status_title = "Refresh State" if refresh_state else "Snapshot Status"
    status_value = refresh_state.get("label") or snapshot.get("status") or "-"
    status_detail = refresh_state.get("detail") or coverage.get("coverage_basis") or snapshot.get("universe_label") or "-"
    status_tone = refresh_state.get("tone") or ("positive" if snapshot.get("status") == "OK" else "warning")
    return [
        _price_basis_status_item(snapshot),
        {
            "title": "Returnable Coverage",
            "value": coverage_text,
            "detail": coverage_detail or f"missing: {missing_count}, failed: {failed_count}",
            "tone": "positive" if returnable else "warning",
        },
        {
            "title": "Snapshot Age",
            "value": age_value,
            "detail": age_detail,
            "tone": age_tone,
        },
        {
            "title": status_title,
            "value": status_value,
            "detail": status_detail,
            "tone": status_tone,
        },
    ]
