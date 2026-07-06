from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from app.jobs.ingestion_jobs import JobResult, run_collect_ohlcv


US_EASTERN_TZ = ZoneInfo("America/New_York")
US_MARKET_CLOSE_TIME = time(16, 0)
US_MARKET_EARLY_CLOSE_TIME = time(13, 0)


def _normalize_symbols(symbols: Iterable[Any] | None) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for symbol in symbols or []:
        value = str(symbol or "").strip().upper()
        if not value or value in seen:
            continue
        seen.add(value)
        out.append(value)
    return out


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
    return {value for value in candidates if value.weekday() < 5 and value not in holidays}


def _is_nyse_trading_day(value: date) -> bool:
    return value.weekday() < 5 and value not in _nyse_holidays(value.year)


def _previous_nyse_trading_day(value: date) -> date:
    current = value
    for _ in range(15):
        if _is_nyse_trading_day(current):
            return current
        current -= timedelta(days=1)
    return value


def _latest_completed_nyse_session(now: datetime | None = None) -> date:
    now_et = (now or datetime.now(tz=US_EASTERN_TZ)).astimezone(US_EASTERN_TZ)
    session_date = now_et.date()
    if not _is_nyse_trading_day(session_date):
        return _previous_nyse_trading_day(session_date - timedelta(days=1))
    close_time = US_MARKET_EARLY_CLOSE_TIME if session_date in _nyse_early_close_dates(session_date.year) else US_MARKET_CLOSE_TIME
    if now_et.time() <= close_time:
        return _previous_nyse_trading_day(session_date - timedelta(days=1))
    return session_date


def _coerce_date(value: Any) -> date | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.date()


def _target_end_date(meta: Mapping[str, Any], *, now: datetime | None = None) -> date:
    latest_completed = _latest_completed_nyse_session(now)
    requested = _coerce_date(meta.get("end"))
    if requested is None:
        return latest_completed
    bounded = min(requested, latest_completed)
    return _previous_nyse_trading_day(bounded)


def _current_common_latest_date(meta: Mapping[str, Any]) -> date | None:
    price_freshness = meta.get("price_freshness") or {}
    freshness_details = price_freshness.get("details") or {}
    for value in [
        freshness_details.get("common_latest_date"),
        freshness_details.get("effective_end_date"),
        meta.get("actual_result_end"),
    ]:
        parsed = _coerce_date(value)
        if parsed is not None:
            return parsed
    return None


def build_backtest_price_refresh_plan(meta: Mapping[str, Any], *, now: datetime | None = None) -> dict[str, Any]:
    """Return the Backtest Data Trust price-refresh action model without running ingestion."""
    tickers = _normalize_symbols(meta.get("tickers") or meta.get("symbols"))
    target_end = _target_end_date(meta, now=now)
    current_latest = _current_common_latest_date(meta)
    current_latest_text = current_latest.isoformat() if current_latest else "-"
    target_end_text = target_end.isoformat()

    base = {
        "tickers": tickers,
        "ticker_count": len(tickers),
        "current_common_latest": current_latest_text,
        "target_end": target_end_text,
        "collection_end": target_end_text,
        "button_label": "가격 데이터 업데이트",
        "interval": "1d",
        "target_table": "finance_price.nyse_price_history",
    }

    if not tickers:
        return {
            **base,
            "eligible": False,
            "status": "unavailable",
            "collection_start": None,
            "summary": "업데이트할 ticker가 없습니다.",
            "detail": "백테스트 meta에 구성 종목이 없어 가격 갱신 대상을 만들 수 없습니다.",
        }

    if current_latest is not None and current_latest >= target_end:
        return {
            **base,
            "eligible": False,
            "status": "up_to_date",
            "collection_start": None,
            "summary": f"이미 최신 가격 기준입니다. 기준일 {target_end_text}",
            "detail": "주말/휴장일 제외 기준으로 추가 수집할 일봉 OHLCV가 없습니다.",
        }

    collection_start = None
    if current_latest is not None:
        collection_start = (current_latest + timedelta(days=1)).isoformat()
    else:
        requested_start = _coerce_date(meta.get("start"))
        collection_start = requested_start.isoformat() if requested_start else None

    return {
        **base,
        "eligible": True,
        "status": "refresh_available",
        "collection_start": collection_start,
        "summary": f"{len(tickers)}개 종목의 가격 데이터를 {target_end_text}까지 업데이트할 수 있습니다.",
        "detail": f"주말/휴장일 제외 최신 기준일은 {target_end_text}이며, 현재 공통 기준일은 {current_latest_text}입니다.",
    }


def run_backtest_price_refresh(
    meta: Mapping[str, Any],
    *,
    now: datetime | None = None,
    runner: Callable[..., JobResult] | None = None,
) -> JobResult:
    """Refresh the current Backtest ticker set through the existing OHLCV ingestion job."""
    plan = build_backtest_price_refresh_plan(meta, now=now)
    if not plan.get("eligible"):
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "job_name": "backtest_data_trust_ohlcv_refresh",
            "status": "skipped",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": plan.get("ticker_count") or 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": str(plan.get("summary") or "가격 데이터 업데이트 대상이 없습니다."),
            "details": {
                "plan": plan,
                "target_tables": ["finance_price.nyse_price_history"],
                "source": "yfinance OHLCV",
                "purpose": "Backtest Data Trust price freshness repair",
            },
        }

    selected_runner = runner or run_collect_ohlcv
    result = dict(
        selected_runner(
            list(plan["tickers"]),
            start=plan.get("collection_start"),
            end=plan.get("collection_end"),
            period="1y",
            interval="1d",
            execution_profile="managed_safe",
        )
    )
    result["job_name"] = "backtest_data_trust_ohlcv_refresh"
    details = dict(result.get("details") or {})
    details.update(
        {
            "plan": plan,
            "symbols": list(plan["tickers"]),
            "collection_start": plan.get("collection_start"),
            "collection_end": plan.get("collection_end"),
            "interval": "1d",
            "target_tables": ["finance_price.nyse_price_history"],
            "source": "yfinance OHLCV",
            "purpose": "Backtest Data Trust price freshness repair",
        }
    )
    result["details"] = details
    base_message = str(result.get("message") or "").strip()
    result["message"] = (
        f"Backtest 가격 데이터 업데이트: {base_message}"
        if base_message
        else "Backtest 가격 데이터 업데이트를 실행했습니다."
    )
    return result


def price_refresh_result_requires_backtest_rerun(result: Mapping[str, Any] | None) -> bool:
    """Return whether a price refresh changed stored OHLCV enough to stale the current result."""
    if not result:
        return False
    status = str(result.get("status") or "").strip().lower()
    if status not in {"success", "partial_success"}:
        return False
    try:
        rows_written = int(result.get("rows_written") or 0)
    except (TypeError, ValueError):
        rows_written = 0
    return rows_written > 0
