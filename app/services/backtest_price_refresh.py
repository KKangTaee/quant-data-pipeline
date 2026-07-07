from __future__ import annotations

from collections.abc import Callable, Iterable, Mapping
from datetime import date, datetime, time, timedelta
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd

from app.jobs.ingestion_jobs import JobResult, run_collect_ohlcv
from finance.loaders.symbol_resolver import load_active_symbol_resolutions


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


_PROVIDER_GAP_REASON_MARKERS = (
    "persistent_source_gap",
    "provider_source_gap",
    "provider_no_data",
    "likely_delisted",
    "symbol_changed",
    "asset_profile_error",
    "unavailable_from_provider",
)


def _provider_gap_symbols_from_price_freshness(freshness_details: Mapping[str, Any]) -> list[str]:
    rows = freshness_details.get("classification_rows") or []
    provider_gap_symbols: list[Any] = []
    for row in rows:
        if not isinstance(row, Mapping):
            continue
        reason = str(row.get("reason") or "").strip().lower()
        if not reason:
            continue
        if any(marker in reason for marker in _PROVIDER_GAP_REASON_MARKERS):
            provider_gap_symbols.append(row.get("symbol"))
    return _normalize_symbols(provider_gap_symbols)


def _raw_refresh_symbols_from_price_freshness(freshness_details: Mapping[str, Any]) -> list[str]:
    return _normalize_symbols(
        freshness_details.get("refresh_symbols_all")
        or list(freshness_details.get("stale_symbols_all") or [])
        + list(freshness_details.get("missing_symbols_all") or [])
        or list(freshness_details.get("stale_symbols") or [])
        + list(freshness_details.get("missing_symbols") or [])
    )


def _normalize_active_symbol_resolutions(
    resolutions: Mapping[str, Mapping[str, Any]] | None,
) -> dict[str, dict[str, Any]]:
    normalized: dict[str, dict[str, Any]] = {}
    for key, value in dict(resolutions or {}).items():
        if not isinstance(value, Mapping):
            continue
        source_candidates = _normalize_symbols([value.get("source_symbol") or value.get("symbol") or key])
        resolved_candidates = _normalize_symbols([value.get("resolved_symbol") or value.get("related_symbol")])
        if not source_candidates or not resolved_candidates:
            continue
        source_symbol = source_candidates[0]
        resolved_symbol = resolved_candidates[0]
        if source_symbol == resolved_symbol:
            continue
        item = dict(value)
        item["source_symbol"] = source_symbol
        item["resolved_symbol"] = resolved_symbol
        normalized[source_symbol] = item
    return normalized


def _load_active_symbol_resolutions_safely(symbols: Iterable[Any] | None) -> dict[str, dict[str, Any]]:
    try:
        return _normalize_active_symbol_resolutions(load_active_symbol_resolutions(symbols))
    except Exception:
        return {}


def _refresh_symbols_from_price_freshness(
    meta: Mapping[str, Any],
    coverage_tickers: list[str],
) -> tuple[list[str], str, bool, list[str]]:
    price_freshness = meta.get("price_freshness") or {}
    freshness_details = price_freshness.get("details") or {}
    refresh_symbols = _raw_refresh_symbols_from_price_freshness(freshness_details)
    if refresh_symbols:
        refresh_symbol_set = set(refresh_symbols)
        provider_gap_symbols = [
            symbol
            for symbol in _provider_gap_symbols_from_price_freshness(freshness_details)
            if symbol in refresh_symbol_set
        ]
        provider_gap_symbol_set = set(provider_gap_symbols)
        refreshable_symbols = [
            symbol for symbol in refresh_symbols if symbol not in provider_gap_symbol_set
        ]
        missing_symbols = set(
            _normalize_symbols(
                freshness_details.get("missing_symbols_all")
                or freshness_details.get("missing_symbols")
                or []
            )
        )
        has_missing = any(symbol in missing_symbols for symbol in refreshable_symbols)
        return refreshable_symbols, "stale_or_missing_symbols", has_missing, provider_gap_symbols
    return coverage_tickers, "full_current_backtest_universe", False, []


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


def build_backtest_price_refresh_plan(
    meta: Mapping[str, Any],
    *,
    now: datetime | None = None,
    active_symbol_resolutions: Mapping[str, Mapping[str, Any]] | None = None,
) -> dict[str, Any]:
    """Return the Backtest coverage-refresh action model without running ingestion."""
    coverage_tickers = _normalize_symbols(meta.get("tickers") or meta.get("symbols"))
    freshness_details = dict((meta.get("price_freshness") or {}).get("details") or {})
    raw_refresh_symbols = _raw_refresh_symbols_from_price_freshness(freshness_details)
    tickers, refresh_scope, has_missing_symbols, provider_gap_symbols = _refresh_symbols_from_price_freshness(
        meta,
        coverage_tickers,
    )
    lookup_symbols = raw_refresh_symbols or coverage_tickers
    if active_symbol_resolutions is None:
        active_resolution_map = _load_active_symbol_resolutions_safely(lookup_symbols)
    else:
        active_resolution_map = _normalize_active_symbol_resolutions(active_symbol_resolutions)
    source_tickers = list(tickers)
    symbol_resolutions: list[dict[str, Any]] = []
    if active_resolution_map:
        source_candidates = raw_refresh_symbols or tickers or coverage_tickers
        refreshable_symbol_set = set(tickers)
        resolved_sources: set[str] = set()
        collection_tickers: list[str] = []
        collection_sources: list[str] = []
        for source_symbol in source_candidates:
            resolution = active_resolution_map.get(source_symbol)
            if resolution:
                resolved_symbol = str(resolution.get("resolved_symbol") or "").strip().upper()
                if resolved_symbol:
                    collection_tickers.append(resolved_symbol)
                    collection_sources.append(source_symbol)
                    resolved_sources.add(source_symbol)
                    symbol_resolutions.append(
                        {
                            "source_symbol": source_symbol,
                            "resolved_symbol": resolved_symbol,
                            "alias_type": resolution.get("alias_type") or "ticker_change",
                            "effective_date": resolution.get("effective_date"),
                            "confidence": resolution.get("confidence"),
                            "resolution_status": resolution.get("resolution_status") or "active",
                            "source": resolution.get("source"),
                            "source_ref": resolution.get("source_ref"),
                        }
                    )
                    continue
            if not refreshable_symbol_set or source_symbol in refreshable_symbol_set:
                collection_tickers.append(source_symbol)
                collection_sources.append(source_symbol)
        if symbol_resolutions:
            tickers = _normalize_symbols(collection_tickers)
            source_tickers = _normalize_symbols(collection_sources)
            provider_gap_symbols = [symbol for symbol in provider_gap_symbols if symbol not in resolved_sources]
            missing_symbols = set(
                _normalize_symbols(
                    freshness_details.get("missing_symbols_all")
                    or freshness_details.get("missing_symbols")
                    or []
                )
            )
            if any(symbol in missing_symbols for symbol in resolved_sources):
                has_missing_symbols = True
    else:
        source_tickers = list(tickers)
    target_end = _target_end_date(meta, now=now)
    current_latest = _current_common_latest_date(meta)
    current_latest_text = current_latest.isoformat() if current_latest else "-"
    target_end_text = target_end.isoformat()

    base = {
        "tickers": tickers,
        "ticker_count": len(tickers),
        "source_tickers": source_tickers,
        "source_ticker_count": len(source_tickers),
        "symbol_resolutions": symbol_resolutions,
        "resolved_ticker_count": len(symbol_resolutions),
        "coverage_tickers": coverage_tickers,
        "coverage_ticker_count": len(coverage_tickers),
        "provider_gap_symbols": provider_gap_symbols,
        "provider_gap_count": len(provider_gap_symbols),
        "refresh_scope": refresh_scope,
        "current_common_latest": current_latest_text,
        "target_end": target_end_text,
        "collection_end": target_end_text,
        "button_label": "Coverage 최신화",
        "interval": "1d",
        "target_table": "finance_price.nyse_price_history",
    }

    if not coverage_tickers:
        return {
            **base,
            "eligible": False,
            "status": "unavailable",
            "collection_start": None,
            "summary": "업데이트할 ticker가 없습니다.",
            "detail": "백테스트 meta에 구성 종목이 없어 가격 갱신 대상을 만들 수 없습니다.",
        }

    if not tickers:
        if provider_gap_symbols:
            sample = ", ".join(provider_gap_symbols[:8])
            if len(provider_gap_symbols) > 8:
                sample = f"{sample} (+{len(provider_gap_symbols) - 8} more)"
            return {
                **base,
                "eligible": False,
                "status": "provider_gap_only",
                "collection_start": None,
                "summary": (
                    "가격 업데이트로 해결하기 어려운 "
                    f"provider/source gap {len(provider_gap_symbols)}개가 남았습니다: {sample}"
                ),
                "detail": (
                    "provider가 최신 OHLCV row를 주지 않거나 symbol lifecycle 확인이 필요한 대상입니다. "
                    "Coverage 최신화를 반복하기보다 Data Trust에서 provider/source 상태를 확인하거나 universe를 조정하세요."
                ),
            }
        return {
            **base,
            "eligible": False,
            "status": "up_to_date",
            "collection_start": None,
            "summary": "Coverage 최신화 대상이 없습니다.",
            "detail": "가격 최신성 점검에서 stale/missing 대상이 확인되지 않았습니다.",
        }

    if current_latest is not None and current_latest >= target_end and refresh_scope != "stale_or_missing_symbols":
        return {
            **base,
            "eligible": False,
            "status": "up_to_date",
            "collection_start": None,
            "summary": f"이미 최신 coverage 가격 기준입니다. 기준일 {target_end_text}",
            "detail": "주말/휴장일 제외 기준으로 추가 수집할 일봉 OHLCV가 없습니다.",
        }

    collection_start = None
    if has_missing_symbols:
        requested_start = _coerce_date(meta.get("start"))
        collection_start = requested_start.isoformat() if requested_start else None
    elif current_latest is not None:
        collection_start = (current_latest + timedelta(days=1)).isoformat()
    else:
        requested_start = _coerce_date(meta.get("start"))
        collection_start = requested_start.isoformat() if requested_start else None

    scope_label = "stale/missing 가격 대상" if refresh_scope == "stale_or_missing_symbols" else "현재 백테스트 전체 종목"
    provider_gap_note = ""
    if provider_gap_symbols:
        sample = ", ".join(provider_gap_symbols[:8])
        if len(provider_gap_symbols) > 8:
            sample = f"{sample} (+{len(provider_gap_symbols) - 8} more)"
        provider_gap_note = (
            f" provider/source gap {len(provider_gap_symbols)}개는 refresh 대상에서 제외했습니다: {sample}."
        )
    resolution_note = ""
    if symbol_resolutions:
        sample = ", ".join(
            f"{item['source_symbol']} -> {item['resolved_symbol']}"
            for item in symbol_resolutions[:8]
        )
        if len(symbol_resolutions) > 8:
            sample = f"{sample} (+{len(symbol_resolutions) - 8} more)"
        resolution_note = f" Active ticker repair: {sample}."
    return {
        **base,
        "eligible": True,
        "status": "refresh_available",
        "collection_start": collection_start,
        "summary": f"{len(tickers)}개 {scope_label}의 가격 데이터를 {target_end_text}까지 최신화할 수 있습니다.",
        "detail": (
            f"Base Universe {len(coverage_tickers)}개 중 refresh 대상은 {len(tickers)}개입니다. "
            f"주말/휴장일 제외 최신 기준일은 {target_end_text}이며, 현재 공통 기준일은 {current_latest_text}입니다."
            f"{provider_gap_note}{resolution_note}"
        ),
    }


def run_backtest_price_refresh(
    meta: Mapping[str, Any],
    *,
    now: datetime | None = None,
    active_symbol_resolutions: Mapping[str, Mapping[str, Any]] | None = None,
    runner: Callable[..., JobResult] | None = None,
    freshness_inspector: Callable[..., Mapping[str, Any]] | None = None,
) -> JobResult:
    """Refresh stale or missing Backtest coverage prices through the existing OHLCV ingestion job."""
    plan = build_backtest_price_refresh_plan(
        meta,
        now=now,
        active_symbol_resolutions=active_symbol_resolutions,
    )
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
                "message": str(plan.get("summary") or "Coverage 최신화 대상이 없습니다."),
            "details": {
                "plan": plan,
                "source_symbols": list(plan.get("source_tickers") or []),
                "symbol_resolutions": list(plan.get("symbol_resolutions") or []),
                "target_tables": ["finance_price.nyse_price_history"],
                "source": "yfinance OHLCV",
                "purpose": "Backtest Coverage price freshness repair",
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
            "source_symbols": list(plan.get("source_tickers") or []),
            "symbol_resolutions": list(plan.get("symbol_resolutions") or []),
            "collection_start": plan.get("collection_start"),
            "collection_end": plan.get("collection_end"),
            "interval": "1d",
            "target_tables": ["finance_price.nyse_price_history"],
            "source": "yfinance OHLCV",
            "purpose": "Backtest Coverage price freshness repair",
        }
    )
    selected_inspector = freshness_inspector
    if selected_inspector is None:
        try:
            from app.runtime.backtest.runners.strict_factor import inspect_strict_annual_price_freshness

            selected_inspector = inspect_strict_annual_price_freshness
        except Exception:
            selected_inspector = None
    if selected_inspector is not None:
        try:
            post_refresh = dict(
                selected_inspector(
                    tickers=list(plan["tickers"]),
                    end=plan.get("collection_end"),
                    timeframe=plan.get("interval") or "1d",
                    context_label="coverage refresh targets",
                )
            )
            details["post_refresh_price_freshness"] = post_refresh
            post_details = dict(post_refresh.get("details") or {})
            unresolved = _normalize_symbols(post_details.get("refresh_symbols_all") or [])
            details["post_refresh_unresolved_symbols"] = unresolved
            details["post_refresh_unresolved_count"] = len(unresolved)
        except Exception as exc:
            details["post_refresh_price_freshness_error"] = str(exc)
    result["details"] = details
    base_message = str(result.get("message") or "").strip()
    unresolved_count = int(details.get("post_refresh_unresolved_count") or 0)
    unresolved_note = f" 미해결 가격 대상 {unresolved_count}개는 Data Trust에서 계속 확인하세요." if unresolved_count else ""
    result["message"] = (
        f"Backtest Coverage 최신화: {base_message}{unresolved_note}"
        if base_message
        else f"Backtest Coverage 최신화를 실행했습니다.{unresolved_note}"
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
