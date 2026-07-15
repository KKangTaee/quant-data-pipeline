from __future__ import annotations

from collections import Counter
from datetime import date, datetime, timedelta
from math import isfinite
from typing import Any, Callable, Iterable

from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
from finance.data.market_intelligence import (
    build_price_history_limit_issue_rows,
    collect_and_store_market_liquidity_universe,
    load_market_data_issues,
    load_market_cap_universe_members,
    load_market_liquidity_universe_members,
    load_market_liquidity_universe_candidate_symbols,
    load_market_universe_members,
    load_nasdaq_symbol_directory_universe_members,
    upsert_market_data_issue_rows,
    upsert_market_symbol_aliases,
)
from finance.loaders.price import load_latest_prices, load_price_freshness_summary
from finance.loaders.us_stock_valuation import build_us_stock_valuation_collection_plan
from finance.loaders.us_stock_turnaround import build_us_stock_turnaround_collection_plan

from app.jobs.ingestion_jobs import (
    JobResult,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_futures_ohlcv,
    run_collect_macro_calendar,
    run_collect_market_structure_calendar,
    run_collect_market_sentiment,
    run_collect_market_intraday_snapshot,
    run_repair_nasdaq100_valuation_coverage,
    run_collect_ohlcv,
    run_collect_sec_company_ticker_crosscheck,
    run_collect_sp500_universe,
    run_collect_symbol_directory_snapshots,
    run_collect_us_stock_valuation_inputs,
    run_collect_us_stock_turnaround_inputs,
    run_diagnose_market_quote_gaps,
    run_extended_statement_refresh,
)
from app.jobs.overview_automation import run_overview_automation
from app.jobs.run_history import append_run_history

MARKET_MOVERS_EOD_COLLECTION_PERIODS = {
    "weekly": "3mo",
    "monthly": "1y",
    "yearly": "3y",
}
MARKET_MOVERS_EOD_MIN_PRICE_ROWS = {
    "weekly": 10,
    "monthly": 45,
    "yearly": 180,
}


def _market_movers_today() -> date:
    return datetime.now().date()


def record_overview_action_result(result: JobResult) -> None:
    """Persist an explicit Overview action result to the shared ingestion run history."""
    append_run_history(result)


def run_overview_browser_auto_refresh(
    *,
    profile: str,
    job_id: str,
    universe_code: str = "SP500",
    checked_at: str | None = None,
) -> dict[str, Any]:
    checked_at_text = checked_at or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    normalized_universe = str(universe_code or "SP500").strip().upper()
    try:
        summary = run_overview_automation(
            profile=profile,
            job_ids=[job_id],
            execution_mode="browser_auto",
        )
    except RuntimeError as exc:
        summary = {
            "job_name": "overview_automation",
            "status": "locked",
            "profile": profile,
            "execution_mode": "browser_auto",
            "started_at": checked_at_text,
            "finished_at": checked_at_text,
            "jobs_due": 1,
            "jobs_run": 0,
            "plan": [],
            "results": [],
            "message": str(exc),
        }
    except Exception as exc:  # pragma: no cover - UI resilience only
        summary = {
            "job_name": "overview_automation",
            "status": "failed",
            "profile": profile,
            "execution_mode": "browser_auto",
            "started_at": checked_at_text,
            "finished_at": checked_at_text,
            "jobs_due": None,
            "jobs_run": 0,
            "plan": [],
            "results": [],
            "message": str(exc),
        }
    summary["selected_universe_code"] = normalized_universe
    return summary


def run_overview_market_intraday_snapshot(
    *,
    universe_code: str,
    universe_limit: int,
) -> JobResult:
    normalized_universe = str(universe_code or "SP500").strip().upper()
    return run_collect_market_intraday_snapshot(
        universe_code=normalized_universe,
        universe_limit=universe_limit,
        interval="5m",
        chunk_size=100,
        quote_batch_size=200,
        method="quote_fast",
        fallback_to_yfinance=normalized_universe == "SP500",
    )


def run_overview_futures_ohlcv(
    *,
    symbols: Iterable[str],
    cadence_mode: str,
) -> JobResult:
    selected_symbols = list(symbols)
    return run_collect_futures_ohlcv(
        symbols=selected_symbols,
        period="1d",
        interval="1m",
        cadence_mode=cadence_mode,
        max_symbols=max(1, min(24, len(selected_symbols))),
        batch_size=6,
        sleep_sec=0.1,
    )


def run_overview_futures_daily_ohlcv() -> JobResult:
    return run_collect_futures_ohlcv(
        symbols=list(DEFAULT_CORE_FUTURES_SYMBOLS),
        period="5y",
        interval="1d",
        cadence_mode="manual_macro_daily",
        max_symbols=len(DEFAULT_CORE_FUTURES_SYMBOLS),
        batch_size=6,
        sleep_sec=0.1,
    )


def run_overview_fomc_calendar(*, years: Iterable[int]) -> JobResult:
    return run_collect_fomc_calendar(years=years)


def run_overview_earnings_calendar() -> JobResult:
    return run_collect_earnings_calendar(
        symbol_source="latest_movers",
        universe_code="SP500",
        top_movers_limit=20,
        lookahead_days=120,
        max_symbols=50,
        validate_with_nasdaq=True,
    )


def run_overview_macro_calendar(*, years: Iterable[int]) -> JobResult:
    return run_collect_macro_calendar(years=years)


def run_overview_market_structure_calendar(*, years: Iterable[int]) -> JobResult:
    return run_collect_market_structure_calendar(years=years)


def run_overview_event_calendars_refresh_all(*, years: Iterable[int] | None = None) -> JobResult:
    """Run the bounded Events calendar collectors as one manual, sequential refresh bundle."""
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    target_years = tuple(years or (current_year, current_year + 1))
    steps: list[tuple[str, Callable[[], JobResult]]] = [
        ("FOMC Calendar", lambda: run_overview_fomc_calendar(years=target_years)),
        ("Macro Calendar", lambda: run_overview_macro_calendar(years=target_years)),
        ("Market Structure Calendar", lambda: run_overview_market_structure_calendar(years=target_years)),
        ("Earnings Calendar", run_overview_earnings_calendar),
    ]
    result = _run_overview_market_context_refresh_steps(
        job_name="overview_event_calendars_refresh_all",
        execution_mode="manual_events_bundle",
        steps=steps,
        started_at=started_at,
    )
    completed_count = int(result.get("jobs_run") or 0) - int(result.get("jobs_failed") or 0)
    result["message"] = (
        f"Events 일정 갱신: {completed_count}/{len(steps)} jobs completed."
        if result.get("status") != "failed"
        else "Events 일정 갱신이 실패했습니다."
    )
    return result


def run_overview_sp500_universe() -> JobResult:
    return run_collect_sp500_universe()


def run_overview_nasdaq100_valuation_repair(
    *,
    months: int = 60,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Run the approved Nasdaq valuation repair through the ingestion boundary."""
    result = dict(
        run_repair_nasdaq100_valuation_coverage(
            months=months,
            progress_callback=progress_callback,
        )
    )
    result["job_name"] = "overview_nasdaq100_valuation_repair"
    details = dict(result.get("details") or {})
    details.update(
        {
            "source_job_name": "repair_nasdaq100_valuation_coverage",
            "purpose": (
                f"Market Context Nasdaq-100 {int(months)}-month "
                "valuation/history repair"
            ),
            "requested_months": int(months),
        }
    )
    result["details"] = details
    return result


def run_overview_us_stock_valuation_collection(
    symbol: str,
    *,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
    plan_builder: Callable[..., dict[str, Any]] = build_us_stock_valuation_collection_plan,
    identity_runner: Callable[..., JobResult] = run_collect_sec_company_ticker_crosscheck,
    collection_runner: Callable[..., JobResult] = run_collect_us_stock_valuation_inputs,
) -> JobResult:
    """Preflight, synchronously collect, and recheck one selected stock."""
    normalized = str(symbol or "").strip().upper()
    before = dict(plan_builder(normalized))
    if before.get("status") == "READY":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "job_name": "overview_us_stock_valuation_collection",
            "status": "success",
            "started_at": now,
            "finished_at": now,
            "duration_sec": 0.0,
            "rows_written": 0,
            "symbols_requested": 1,
            "symbols_processed": 1,
            "failed_symbols": [],
            "message": f"{normalized} valuation inputs are already complete.",
            "details": {"before": before, "after": before},
        }
    if before.get("status") != "COLLECTABLE":
        now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "job_name": "overview_us_stock_valuation_collection",
            "status": "failed",
            "started_at": now,
            "finished_at": now,
            "duration_sec": 0.0,
            "rows_written": 0,
            "symbols_requested": 1,
            "symbols_processed": 0,
            "failed_symbols": [normalized],
            "message": str(before.get("reason") or "Selected stock is not collectable."),
            "details": {"before": before, "after": before},
        }

    active_plan = before
    identity_result: dict[str, Any] | None = None
    if "sec_identity" in set(before.get("scopes") or []):
        if progress_callback is not None:
            progress_callback(
                {"event": "stage", "stage": "identity", "symbol": normalized}
            )
        identity_result = dict(
            identity_runner([normalized], progress_callback=None)
        )
        active_plan = dict(plan_builder(normalized))
        active_identity = dict(active_plan.get("identity") or {})
        if not str(active_identity.get("cik") or "").strip():
            return {
                **identity_result,
                "job_name": "overview_us_stock_valuation_collection",
                "status": "failed",
                "failed_symbols": [normalized],
                "message": f"{normalized} SEC CIK identity could not be linked.",
                "details": {
                    "identity_step": identity_result,
                    "before": before,
                    "after": active_plan,
                },
            }
        if active_plan.get("status") == "READY":
            return {
                **identity_result,
                "job_name": "overview_us_stock_valuation_collection",
                "status": "success",
                "message": f"{normalized} valuation inputs are ready.",
                "details": {
                    "identity_step": identity_result,
                    "before": before,
                    "after": active_plan,
                },
            }
        if active_plan.get("status") != "COLLECTABLE":
            return {
                **identity_result,
                "job_name": "overview_us_stock_valuation_collection",
                "status": "failed",
                "failed_symbols": [normalized],
                "message": str(
                    active_plan.get("reason")
                    or f"{normalized} is not collectable after SEC identity refresh."
                ),
                "details": {
                    "identity_step": identity_result,
                    "before": before,
                    "after": active_plan,
                },
            }

    identity = dict(active_plan.get("identity") or {})
    scopes = set(active_plan.get("scopes") or [])
    ranges = dict(active_plan.get("missing_ranges") or {})
    price_range = dict(ranges.get("prices") or {})
    collected = dict(
        collection_runner(
            normalized,
            cik=str(identity.get("cik") or ""),
            identity_cik=str(identity.get("cik") or ""),
            price_start=price_range.get("start"),
            price_end=price_range.get("end"),
            collect_prices="prices" in scopes,
            collect_statements="sec_statements" in scopes,
            progress_callback=progress_callback,
        )
    )
    after = dict(plan_builder(normalized))
    if after.get("status") == "READY":
        status = "success"
    elif after.get("status") == "COLLECTABLE" and collected.get("status") != "failed":
        status = "partial_success"
    else:
        status = str(collected.get("status") or "failed")
    details = dict(collected.get("details") or {})
    details.update(
        {
            "source_job_name": collected.get("job_name"),
            "before": before,
            "after": after,
        }
    )
    if identity_result is not None:
        details["identity_step"] = identity_result
    return {
        **collected,
        "job_name": "overview_us_stock_valuation_collection",
        "status": status,
        "rows_written": int(collected.get("rows_written") or 0)
        + int((identity_result or {}).get("rows_written") or 0),
        "message": (
            f"{normalized} valuation inputs are ready."
            if status == "success"
            else f"{normalized} collection finished; remaining ranges are shown."
        ),
        "details": details,
    }


def run_overview_us_stock_turnaround_collection(
    symbol: str,
    *,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
    plan_builder: Callable[..., dict[str, Any]] = build_us_stock_turnaround_collection_plan,
    collection_runner: Callable[..., JobResult] = run_collect_us_stock_turnaround_inputs,
) -> JobResult:
    """Preflight, collect, and recheck exact selected-stock turnaround scopes."""
    normalized = str(symbol or "").strip().upper()
    before = dict(plan_builder(normalized))
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if before.get("status") == "READY":
        return {
            "job_name": "overview_us_stock_turnaround_collection",
            "status": "success",
            "started_at": now,
            "finished_at": now,
            "duration_sec": 0.0,
            "rows_written": 0,
            "symbols_requested": 1,
            "symbols_processed": 1,
            "failed_symbols": [],
            "message": f"{normalized} turnaround inputs are already complete.",
            "details": {"before": before, "after": before},
        }
    if before.get("status") != "COLLECTABLE":
        return {
            "job_name": "overview_us_stock_turnaround_collection",
            "status": "failed",
            "started_at": now,
            "finished_at": now,
            "duration_sec": 0.0,
            "rows_written": 0,
            "symbols_requested": 1,
            "symbols_processed": 0,
            "failed_symbols": [normalized],
            "message": str(before.get("reason") or "Selected stock is not collectable."),
            "details": {"before": before, "after": before},
        }

    identity = dict(before.get("identity") or {})
    scopes = set(before.get("scopes") or [])
    ranges = dict(before.get("missing_ranges") or {})
    price_range = dict(ranges.get("prices") or {})
    collected = dict(
        collection_runner(
            normalized,
            cik=str(identity.get("cik") or ""),
            identity_cik=str(identity.get("cik") or ""),
            price_start=price_range.get("start"),
            price_end=price_range.get("end"),
            collect_profile="asset_profile" in scopes,
            collect_prices="prices" in scopes,
            collect_statements="sec_statements" in scopes,
            progress_callback=progress_callback,
        )
    )
    after = dict(plan_builder(normalized))
    if after.get("status") == "READY":
        status = "success"
    elif after.get("status") == "COLLECTABLE" and collected.get("status") != "failed":
        status = "partial_success"
    else:
        status = str(collected.get("status") or "failed")
    details = dict(collected.get("details") or {})
    details.update(
        {
            "source_job_name": collected.get("job_name"),
            "before": before,
            "after": after,
        }
    )
    return {
        **collected,
        "job_name": "overview_us_stock_turnaround_collection",
        "status": status,
        "message": (
            f"{normalized} turnaround inputs are ready."
            if status == "success"
            else f"{normalized} collection finished; remaining scopes are shown."
        ),
        "details": details,
    }


def run_overview_nasdaq_symbol_directory() -> JobResult:
    return run_collect_symbol_directory_snapshots(sources=("nasdaqlisted",))


def run_overview_market_sentiment() -> JobResult:
    return run_collect_market_sentiment()


def market_movers_eod_collection_period(period: str) -> str:
    normalized_period = str(period or "").strip().lower()
    try:
        return MARKET_MOVERS_EOD_COLLECTION_PERIODS[normalized_period]
    except KeyError as exc:
        raise ValueError(f"Unsupported Market Movers EOD refresh period: {period!r}") from exc


def _normalize_action_symbols(symbols: Iterable[str]) -> list[str]:
    normalized: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        value = str(symbol or "").strip().upper()
        if not value or value in seen:
            continue
        seen.add(value)
        normalized.append(value)
    return normalized


def _normalize_symbol_alias_candidates(candidates: Iterable[dict[str, Any]]) -> list[dict[str, Any]]:
    normalized: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for row in candidates:
        source_symbol = str(row.get("source_symbol") or row.get("symbol") or "").strip().upper()
        alias_symbol = str(row.get("alias_symbol") or "").strip().upper()
        if not source_symbol or not alias_symbol or source_symbol == alias_symbol:
            continue
        key = (source_symbol, alias_symbol)
        if key in seen:
            continue
        seen.add(key)
        normalized.append(
            {
                **dict(row),
                "source_symbol": source_symbol,
                "symbol": source_symbol,
                "alias_symbol": alias_symbol,
                "alias_type": str(row.get("alias_type") or "ticker_change"),
                "status": "active",
            }
        )
    return normalized


def run_overview_market_symbol_alias_repair(
    *,
    universe_code: str,
    candidates: Iterable[dict[str, Any]],
) -> JobResult:
    """Apply reviewed ticker-change aliases for Market Movers quote repair."""
    normalized_universe = str(universe_code or "SP500").strip().upper()
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    rows = _normalize_symbol_alias_candidates(candidates)
    if not rows:
        return {
            "job_name": "overview_market_symbol_alias_repair",
            "status": "failed",
            "started_at": started_at,
            "finished_at": started_at,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": "적용할 티커 변경 후보가 없습니다.",
            "details": {
                "universe_code": normalized_universe,
                "target_table": "finance_meta.market_symbol_alias",
                "next_action": "후보를 다시 확인한 뒤 일중 스냅샷을 갱신하세요.",
            },
        }
    rows_written = upsert_market_symbol_aliases(rows, status="active", applied_at=started_at)
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    source_symbols = [row["source_symbol"] for row in rows]
    alias_pairs = [f"{row['source_symbol']}->{row['alias_symbol']}" for row in rows]
    return {
        "job_name": "overview_market_symbol_alias_repair",
        "status": "success" if rows_written else "failed",
        "started_at": started_at,
        "finished_at": finished_at,
        "rows_written": rows_written,
        "symbols_requested": len(rows),
        "symbols_processed": rows_written,
        "failed_symbols": [] if rows_written else source_symbols,
        "message": f"티커 변경 복구 {rows_written}건을 적용했습니다. 이제 일중 스냅샷을 다시 갱신하세요.",
        "details": {
            "universe_code": normalized_universe,
            "alias_pairs": alias_pairs,
            "target_table": "finance_meta.market_symbol_alias",
            "next_action": "일중 스냅샷 갱신",
            "purpose": "Market Movers quote lookup should use active replacement ticker while keeping universe symbols stable.",
        },
    }


def _load_market_movers_eod_universe_symbols(*, universe_code: str, universe_limit: int) -> tuple[list[str], str]:
    normalized_universe = str(universe_code or "SP500").strip().upper()
    if normalized_universe == "SP500":
        rows = load_market_universe_members("SP500")
        coverage_basis = "Current S&P 500 constituents"
    elif normalized_universe == "NASDAQ":
        rows = load_nasdaq_symbol_directory_universe_members()
        coverage_basis = "Nasdaq-listed current snapshot"
    elif normalized_universe in {"TOP1000", "TOP2000"}:
        rows = load_market_liquidity_universe_members(normalized_universe, universe_limit=universe_limit)
        coverage_basis = "20D avg dollar volume materialized universe"
    else:
        rows = load_market_cap_universe_members(normalized_universe, universe_limit=universe_limit)
        coverage_basis = "Latest asset_profile.market_cap snapshot"
    return _normalize_action_symbols(row.get("symbol") for row in rows), coverage_basis


def _coerce_market_movers_date(value: Any) -> date | None:
    if value is None:
        return None
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    if hasattr(value, "date") and callable(value.date):
        try:
            parsed = value.date()
            if isinstance(parsed, date):
                return parsed
        except Exception:
            return None
    parsed_ts = _market_movers_to_datetime(value)
    if parsed_ts is None:
        return None
    return parsed_ts.date()


def _market_movers_to_datetime(value: Any) -> datetime | None:
    try:
        from pandas import isna, to_datetime

        parsed = to_datetime(value, errors="coerce")
    except Exception:
        return None
    if parsed is None or bool(isna(parsed)):
        return None
    if hasattr(parsed, "to_pydatetime"):
        return parsed.to_pydatetime()
    if isinstance(parsed, datetime):
        return parsed
    return None


def _load_market_movers_eod_freshness(symbols: list[str]) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    frame = load_price_freshness_summary(symbols=symbols, timeframe="1d")
    rows: dict[str, dict[str, Any]] = {}
    if not frame.empty:
        for row in frame.to_dict("records"):
            symbol = str(row.get("symbol") or "").strip().upper()
            if not symbol:
                continue
            latest_date = _coerce_market_movers_date(row.get("latest_date"))
            rows[symbol] = {
                "first_date": _coerce_market_movers_date(row.get("first_date")),
                "latest_date": latest_date,
                "row_count": int(row.get("row_count") or 0),
            }
    latest_frame = load_latest_prices(symbols=symbols, timeframe="1d", field="close")
    if not latest_frame.empty:
        for row in latest_frame.to_dict("records"):
            symbol = str(row.get("symbol") or "").strip().upper()
            if not symbol:
                continue
            target = rows.setdefault(symbol, {})
            target["latest_date"] = _coerce_market_movers_date(row.get("latest_date")) or target.get("latest_date")
            for field in ("price", "close", "adj_close", "volume"):
                if field in row:
                    target[field] = row.get(field)
    return rows


def _load_market_movers_limited_history_symbols(*, universe_code: str, symbols: list[str]) -> set[str]:
    if not symbols:
        return set()
    issues = load_market_data_issues(
        universe_code=universe_code,
        symbols=symbols,
        issue_type="limited_price_history",
        limit=max(len(symbols), 1),
    )
    return {
        str(row.get("symbol") or "").strip().upper()
        for row in issues
        if str(row.get("latest_status") or "active").strip().lower() == "active"
    }


def _market_movers_positive_number(value: Any) -> bool:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return False
    return isfinite(numeric) and numeric > 0


def _market_movers_quality_reasons(row: dict[str, Any], *, period: str) -> list[str]:
    reasons: list[str] = []
    latest_date = _coerce_market_movers_date(row.get("latest_date"))
    if latest_date is not None and "close" in row and not _market_movers_positive_number(row.get("close")):
        reasons.append("bad_latest_price")
    if latest_date is not None and "volume" in row and not _market_movers_positive_number(row.get("volume")):
        reasons.append("zero_latest_volume")
    min_rows = MARKET_MOVERS_EOD_MIN_PRICE_ROWS.get(period, 0)
    try:
        row_count = int(row.get("row_count") or 0)
    except (TypeError, ValueError):
        row_count = 0
    if latest_date is not None and min_rows > 0 and row_count < min_rows:
        reasons.append("insufficient_window_rows")
    return reasons


def _market_movers_format_date(value: date | None) -> str | None:
    return value.strftime("%Y-%m-%d") if value else None


def _market_movers_eod_symbol_batches(
    symbols: list[str],
    starts_by_symbol: dict[str, date],
    *,
    end_date: date,
    reason: str,
) -> list[dict[str, Any]]:
    grouped: dict[date, list[str]] = {}
    for symbol in symbols:
        start_date = starts_by_symbol.get(symbol)
        if start_date is None:
            continue
        grouped.setdefault(start_date, []).append(symbol)
    return [
        {
            "reason": reason,
            "start_date": start_date,
            "end_date": end_date,
            "symbols": grouped[start_date],
            "symbols_count": len(grouped[start_date]),
            "driver_symbols": grouped[start_date][:5],
        }
        for start_date in sorted(grouped)
    ]


def _market_movers_eod_range_reason(
    *,
    earliest_batch: dict[str, Any] | None,
    missing_symbols: list[str],
) -> str:
    if earliest_batch:
        driver_symbols = ", ".join(str(symbol) for symbol in list(earliest_batch.get("driver_symbols") or [])[:3])
        start_date = _market_movers_format_date(earliest_batch.get("start_date"))
        if earliest_batch.get("reason") == "quality_repair":
            return (
                f"품질 보강 대상 중 가장 오래된 종목 {driver_symbols or '-'}의 최신 가격일 {start_date}부터 "
                "다시 확인합니다. 같은 시작일끼리 나눠 수집합니다."
            )
        return (
            f"가장 오래된 stale 종목 {driver_symbols or '-'}의 다음 거래일 {start_date}부터 보강합니다. "
            "같은 시작일끼리 나눠 최신 stale 종목은 더 짧게 수집합니다."
        )
    if missing_symbols:
        sample = ", ".join(missing_symbols[:3])
        return f"가격 이력이 없는 종목 {sample or '-'}은 provider 기간 window 전체로 수집합니다."
    return "선택한 기준일 기준으로 추가 수집할 가격 이력이 없습니다."


def _market_movers_eod_refresh_plan(
    symbols: list[str],
    freshness: dict[str, dict[str, Any]],
    *,
    as_of_date: date,
    period: str,
    known_limited_symbols: set[str] | None = None,
) -> dict[str, Any]:
    current_symbols: list[str] = []
    stale_symbols: list[str] = []
    repair_symbols: list[str] = []
    missing_symbols: list[str] = []
    stale_starts: list[date] = []
    repair_starts: list[date] = []
    stale_starts_by_symbol: dict[str, date] = {}
    repair_starts_by_symbol: dict[str, date] = {}
    quality_reasons_by_symbol: dict[str, list[str]] = {}
    limited_history_symbols: list[str] = []
    known_limited = known_limited_symbols or set()

    for symbol in symbols:
        row = freshness.get(symbol) or {}
        latest_date = _coerce_market_movers_date(row.get("latest_date"))
        quality_reasons = _market_movers_quality_reasons(row, period=period)
        if latest_date is None:
            missing_symbols.append(symbol)
        elif "insufficient_window_rows" in quality_reasons:
            quality_reasons_by_symbol[symbol] = quality_reasons
            if symbol in known_limited:
                limited_history_symbols.append(symbol)
            else:
                missing_symbols.append(symbol)
        elif quality_reasons:
            repair_symbols.append(symbol)
            repair_starts.append(latest_date)
            repair_starts_by_symbol[symbol] = latest_date
            quality_reasons_by_symbol[symbol] = quality_reasons
        elif latest_date >= as_of_date:
            current_symbols.append(symbol)
        else:
            stale_symbols.append(symbol)
            stale_start = latest_date + timedelta(days=1)
            stale_starts.append(stale_start)
            stale_starts_by_symbol[symbol] = stale_start

    delta_start = min(stale_starts) if stale_starts else None
    repair_start = min(repair_starts) if repair_starts else None
    delta_end = as_of_date + timedelta(days=1)
    delta_batches = _market_movers_eod_symbol_batches(
        stale_symbols,
        stale_starts_by_symbol,
        end_date=delta_end,
        reason="stale_delta",
    )
    repair_batches = _market_movers_eod_symbol_batches(
        repair_symbols,
        repair_starts_by_symbol,
        end_date=delta_end,
        reason="quality_repair",
    )
    scoped_batches = sorted([*delta_batches, *repair_batches], key=lambda batch: batch["start_date"])
    earliest_batch = scoped_batches[0] if scoped_batches else None
    range_start = earliest_batch.get("start_date") if earliest_batch else None
    range_end = max((batch["end_date"] for batch in scoped_batches), default=None)
    reason_counts = Counter(reason for reasons in quality_reasons_by_symbol.values() for reason in reasons)
    return {
        "current_symbols": current_symbols,
        "stale_symbols": stale_symbols,
        "repair_symbols": repair_symbols,
        "missing_symbols": missing_symbols,
        "limited_history_symbols": limited_history_symbols,
        "delta_start": delta_start,
        "repair_start": repair_start,
        "delta_end": delta_end if stale_symbols else None,
        "repair_end": delta_end if repair_symbols else None,
        "delta_batches": delta_batches,
        "repair_batches": repair_batches,
        "range_start": range_start,
        "range_end": range_end,
        "range_reason": _market_movers_eod_range_reason(
            earliest_batch=earliest_batch,
            missing_symbols=missing_symbols,
        ),
        "range_driver_symbols": list(earliest_batch.get("driver_symbols") or []) if earliest_batch else missing_symbols[:5],
        "quality_reasons_by_symbol": quality_reasons_by_symbol,
        "quality_reason_counts": dict(reason_counts),
    }


def _market_movers_serialize_eod_batch(batch: dict[str, Any]) -> dict[str, Any]:
    return {
        "reason": str(batch.get("reason") or ""),
        "start_date": _market_movers_format_date(batch.get("start_date")),
        "end_date": _market_movers_format_date(batch.get("end_date")),
        "symbols_count": int(batch.get("symbols_count") or 0),
        "driver_symbols": list(batch.get("driver_symbols") or []),
    }


def _market_movers_eod_preflight_payload(
    *,
    normalized_universe: str,
    universe_limit: int,
    normalized_period: str,
    collection_period: str,
    coverage_basis: str,
    symbols: list[str],
    plan: dict[str, Any],
    as_of_date: date,
    force_full_refresh: bool,
    freshness_error: str = "",
) -> dict[str, Any]:
    missing_symbols = symbols if force_full_refresh else list(plan["missing_symbols"])
    limited_history_symbols = [] if force_full_refresh else list(plan.get("limited_history_symbols") or [])
    current_symbols = [] if force_full_refresh else list(plan["current_symbols"])
    selected_symbols = list(dict.fromkeys([*plan["stale_symbols"], *plan["repair_symbols"], *missing_symbols]))
    status = "current" if not selected_symbols and not freshness_error else "due"
    if limited_history_symbols and not selected_symbols and not freshness_error:
        status = "limited"
    range_start = plan.get("range_start")
    range_end = plan.get("range_end")
    if force_full_refresh:
        status_label = "전체 가격 이력 갱신"
        range_reason = "사용자가 전체 갱신을 요청해 선택 universe 전체를 provider 기간 window로 다시 수집합니다."
    elif freshness_error:
        status_label = "가격 이력 확인 필요"
        range_reason = "저장 가격의 최신 상태 확인에 실패해 안전하게 provider 기간 window 수집으로 전환합니다."
    elif selected_symbols:
        status_label = "가격 이력 보강 필요"
        range_reason = str(plan.get("range_reason") or "")
    elif limited_history_symbols:
        status_label = "짧은 가격 이력 제외"
        sample = ", ".join(limited_history_symbols[:3])
        range_reason = (
            f"{sample or '-'}는 provider에서 사용할 수 있는 가격 이력이 짧아 현재 랭킹에서 제외되며 "
            "추가 수집 대상이 아닙니다."
        )
    else:
        status_label = "가격 이력 최신"
        range_reason = str(plan.get("range_reason") or "")
    return {
        "schema_version": "market_movers_eod_refresh_preflight_v1",
        "status": status,
        "status_label": status_label,
        "tone": "positive" if status == "current" else "warning",
        "universe_code": normalized_universe,
        "universe_limit": universe_limit,
        "coverage_basis": coverage_basis,
        "market_mover_period": normalized_period,
        "collection_period": collection_period,
        "as_of_date": _market_movers_format_date(as_of_date),
        "symbols_requested_count": len(symbols),
        "selected_symbols_count": len(selected_symbols),
        "skipped_current_count": len(current_symbols),
        "delta_symbols_count": len(plan["stale_symbols"]),
        "repair_symbols_count": len(plan["repair_symbols"]),
        "missing_symbols_count": len(missing_symbols),
        "limited_history_symbols_count": len(limited_history_symbols),
        "limited_history_symbols": limited_history_symbols,
        "quality_symbols_count": len(plan["quality_reasons_by_symbol"]),
        "delta_batch_count": len(plan.get("delta_batches") or []),
        "repair_batch_count": len(plan.get("repair_batches") or []),
        "range_start": _market_movers_format_date(range_start),
        "range_end": _market_movers_format_date(range_end),
        "range_reason": range_reason,
        "range_driver_symbols": list(plan.get("range_driver_symbols") or []),
        "selected_symbols_sample": selected_symbols[:10],
        "delta_batches": [_market_movers_serialize_eod_batch(batch) for batch in list(plan.get("delta_batches") or [])],
        "repair_batches": [
            _market_movers_serialize_eod_batch(batch) for batch in list(plan.get("repair_batches") or [])
        ],
        "freshness_error": freshness_error,
    }


def build_market_movers_eod_refresh_preflight(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
    as_of_date: str | date | datetime | None = None,
    force_full_refresh: bool = False,
) -> dict[str, Any]:
    """Return the Market Movers EOD refresh scope without calling the provider."""
    normalized_universe = str(universe_code or "SP500").strip().upper()
    normalized_period = str(period or "").strip().lower()
    collection_period = market_movers_eod_collection_period(normalized_period)
    symbols, coverage_basis = _load_market_movers_eod_universe_symbols(
        universe_code=normalized_universe,
        universe_limit=universe_limit,
    )
    resolved_as_of_date = _coerce_market_movers_date(as_of_date) or _market_movers_today()
    freshness_error = ""
    freshness: dict[str, dict[str, Any]] = {}
    known_limited_symbols: set[str] = set()
    if not force_full_refresh:
        try:
            freshness = _load_market_movers_eod_freshness(symbols)
        except Exception as exc:
            freshness_error = str(exc)
            freshness = {}
        try:
            known_limited_symbols = _load_market_movers_limited_history_symbols(
                universe_code=normalized_universe,
                symbols=symbols,
            )
        except Exception:
            known_limited_symbols = set()
    plan = _market_movers_eod_refresh_plan(
        symbols,
        freshness,
        as_of_date=resolved_as_of_date,
        period=normalized_period,
        known_limited_symbols=known_limited_symbols,
    )
    return _market_movers_eod_preflight_payload(
        normalized_universe=normalized_universe,
        universe_limit=universe_limit,
        normalized_period=normalized_period,
        collection_period=collection_period,
        coverage_basis=coverage_basis,
        symbols=symbols,
        plan=plan,
        as_of_date=resolved_as_of_date,
        force_full_refresh=force_full_refresh,
        freshness_error=freshness_error,
    )


def _market_movers_result_int(result: dict[str, Any], key: str) -> int:
    try:
        return int(result.get(key) or 0)
    except (TypeError, ValueError):
        return 0


def _merge_market_movers_eod_results(results: list[dict[str, Any]], *, now_text: str) -> dict[str, Any]:
    if not results:
        return {
            "job_name": "collect_ohlcv",
            "status": "success",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": "",
            "details": {},
        }
    if len(results) == 1:
        return dict(results[0])

    statuses = [str(result.get("status") or "").lower() for result in results]
    if any(status in {"failed", "error"} for status in statuses):
        status = "failed"
    elif any(status in {"partial", "warning"} for status in statuses):
        status = "partial"
    else:
        status = "success"

    failed_symbols: list[str] = []
    messages: list[str] = []
    for result in results:
        failed_symbols.extend(str(symbol) for symbol in result.get("failed_symbols") or [])
        message = str(result.get("message") or "").strip()
        if message:
            messages.append(message)

    details = {
        "collect_parts": [
            {
                "status": result.get("status"),
                "rows_written": result.get("rows_written"),
                "symbols_requested": result.get("symbols_requested"),
                "symbols_processed": result.get("symbols_processed"),
            }
            for result in results
        ]
    }
    return {
        "job_name": "collect_ohlcv",
        "status": status,
        "started_at": results[0].get("started_at") or now_text,
        "finished_at": results[-1].get("finished_at") or now_text,
        "rows_written": sum(_market_movers_result_int(result, "rows_written") for result in results),
        "symbols_requested": sum(_market_movers_result_int(result, "symbols_requested") for result in results),
        "symbols_processed": sum(_market_movers_result_int(result, "symbols_processed") for result in results),
        "failed_symbols": failed_symbols,
        "message": " / ".join(messages),
        "details": details,
    }


def _persist_market_movers_limited_history_issues(
    *,
    universe_code: str,
    period: str,
    symbols: list[str],
    as_of_date: date,
) -> dict[str, Any]:
    """Persist symbols that remain short only after a full provider-window refresh."""
    if not symbols:
        return {"symbols": [], "rows_written": 0}
    freshness = _load_market_movers_eod_freshness(symbols)
    min_rows = MARKET_MOVERS_EOD_MIN_PRICE_ROWS.get(period, 0)
    evidence: list[dict[str, Any]] = []
    for symbol in symbols:
        row = freshness.get(symbol) or {}
        latest_date = _coerce_market_movers_date(row.get("latest_date"))
        reasons = _market_movers_quality_reasons(row, period=period)
        if "insufficient_window_rows" not in reasons or latest_date is None or latest_date < as_of_date:
            continue
        evidence.append(
            {
                "symbol": symbol,
                "period": period,
                "first_date": _market_movers_format_date(_coerce_market_movers_date(row.get("first_date"))),
                "latest_date": _market_movers_format_date(latest_date),
                "row_count": int(row.get("row_count") or 0),
                "min_rows": min_rows,
            }
        )
    issue_rows = build_price_history_limit_issue_rows(evidence, universe_code=universe_code)
    rows_written = upsert_market_data_issue_rows(issue_rows) if issue_rows else 0
    return {
        "symbols": [str(row.get("symbol") or "") for row in evidence],
        "rows_written": rows_written,
    }


def run_overview_market_movers_eod_history(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
    force_full_refresh: bool = False,
    as_of_date: str | date | datetime | None = None,
) -> JobResult:
    """Refresh EOD price history for non-daily Market Movers through the existing OHLCV job."""
    normalized_universe = str(universe_code or "SP500").strip().upper()
    normalized_period = str(period or "").strip().lower()
    collection_period = market_movers_eod_collection_period(normalized_period)
    symbols, coverage_basis = _load_market_movers_eod_universe_symbols(
        universe_code=normalized_universe,
        universe_limit=universe_limit,
    )
    resolved_as_of_date = _coerce_market_movers_date(as_of_date) or _market_movers_today()
    now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    if not symbols:
        return {
            "job_name": "overview_market_movers_eod_history",
            "status": "failed",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": "Market Movers 가격 이력 갱신 대상 universe symbol이 없습니다.",
            "details": {
                "universe_code": normalized_universe,
                "universe_limit": universe_limit,
                "coverage_basis": coverage_basis,
                "market_mover_period": normalized_period,
                "collection_period": collection_period,
                "interval": "1d",
                "as_of_date": _market_movers_format_date(resolved_as_of_date),
                "target_tables": ["finance_price.nyse_price_history"],
                "source": "yfinance OHLCV",
                "purpose": "Overview Market Movers non-daily EOD price history refresh",
            },
        }

    freshness_error = ""
    freshness: dict[str, dict[str, Any]] = {}
    known_limited_symbols: set[str] = set()
    if not force_full_refresh:
        try:
            freshness = _load_market_movers_eod_freshness(symbols)
        except Exception as exc:
            freshness_error = str(exc)
            freshness = {}
        try:
            known_limited_symbols = _load_market_movers_limited_history_symbols(
                universe_code=normalized_universe,
                symbols=symbols,
            )
        except Exception:
            known_limited_symbols = set()
    plan = _market_movers_eod_refresh_plan(
        symbols,
        freshness,
        as_of_date=resolved_as_of_date,
        period=normalized_period,
        known_limited_symbols=known_limited_symbols,
    )
    stale_symbols = plan["stale_symbols"]
    repair_symbols = plan["repair_symbols"]
    missing_symbols = symbols if force_full_refresh else plan["missing_symbols"]
    current_symbols = [] if force_full_refresh else plan["current_symbols"]
    selected_symbols = list(dict.fromkeys([*stale_symbols, *repair_symbols, *missing_symbols]))

    if not selected_symbols:
        result = {
            "job_name": "overview_market_movers_eod_history",
            "status": "success",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": f"{normalized_period.title()} Market Movers 가격 이력은 이미 최신입니다.",
            "details": {},
        }
    else:
        collect_results: list[dict[str, Any]] = []
        for batch in list(plan.get("delta_batches") or []):
            collect_results.append(
                dict(
                    run_collect_ohlcv(
                        list(batch.get("symbols") or []),
                        start=batch["start_date"].strftime("%Y-%m-%d"),
                        end=batch["end_date"].strftime("%Y-%m-%d"),
                        period=collection_period,
                        interval="1d",
                        execution_profile="managed_safe",
                    )
                )
            )
        for batch in list(plan.get("repair_batches") or []):
            collect_results.append(
                dict(
                    run_collect_ohlcv(
                        list(batch.get("symbols") or []),
                        start=batch["start_date"].strftime("%Y-%m-%d"),
                        end=batch["end_date"].strftime("%Y-%m-%d"),
                        period=collection_period,
                        interval="1d",
                        execution_profile="managed_safe",
                    )
                )
            )
        if missing_symbols:
            collect_results.append(
                dict(
                    run_collect_ohlcv(
                        missing_symbols,
                        period=collection_period,
                        interval="1d",
                        execution_profile="managed_safe",
                    )
                )
            )
        result = _merge_market_movers_eod_results(collect_results, now_text=now_text)

    limited_history_result = _persist_market_movers_limited_history_issues(
        universe_code=normalized_universe,
        period=normalized_period,
        symbols=selected_symbols,
        as_of_date=resolved_as_of_date,
    )

    result["job_name"] = "overview_market_movers_eod_history"
    details = dict(result.get("details") or {})
    refresh_strategy = "full_window_forced" if force_full_refresh else "smart_delta"
    preflight_payload = _market_movers_eod_preflight_payload(
        normalized_universe=normalized_universe,
        universe_limit=universe_limit,
        normalized_period=normalized_period,
        collection_period=collection_period,
        coverage_basis=coverage_basis,
        symbols=symbols,
        plan=plan,
        as_of_date=resolved_as_of_date,
        force_full_refresh=force_full_refresh,
        freshness_error=freshness_error,
    )
    details.update(
        {
            "universe_code": normalized_universe,
            "universe_limit": universe_limit,
            "coverage_basis": coverage_basis,
            "market_mover_period": normalized_period,
            "collection_period": collection_period,
            "interval": "1d",
            "refresh_strategy": refresh_strategy,
            "as_of_date": _market_movers_format_date(resolved_as_of_date),
            "symbols_requested": len(symbols),
            "symbols_selected": len(selected_symbols),
            "symbols_skipped_current": len(current_symbols),
            "delta_symbols_count": len(stale_symbols),
            "repair_symbols_count": len(repair_symbols),
            "missing_symbols_count": len(missing_symbols),
            "known_limited_history_symbols_count": len(plan.get("limited_history_symbols") or []),
            "limited_history_symbols_count": len(limited_history_result["symbols"]),
            "limited_history_symbols": limited_history_result["symbols"],
            "limited_history_issue_rows_written": limited_history_result["rows_written"],
            "quality_symbols_count": len(plan["quality_reasons_by_symbol"]),
            "delta_batch_count": len(plan.get("delta_batches") or []),
            "repair_batch_count": len(plan.get("repair_batches") or []),
            "bad_latest_symbols_count": sum(
                1
                for reasons in plan["quality_reasons_by_symbol"].values()
                if "bad_latest_price" in reasons or "zero_latest_volume" in reasons
            ),
            "insufficient_window_symbols_count": sum(
                1
                for reasons in plan["quality_reasons_by_symbol"].values()
                if "insufficient_window_rows" in reasons
            ),
            "quality_reason_counts": plan["quality_reason_counts"],
            "delta_start": plan["delta_start"].strftime("%Y-%m-%d") if plan["delta_start"] else None,
            "delta_end": plan["delta_end"].strftime("%Y-%m-%d") if plan["delta_end"] else None,
            "repair_start": plan["repair_start"].strftime("%Y-%m-%d") if plan["repair_start"] else None,
            "repair_end": plan["repair_end"].strftime("%Y-%m-%d") if plan["repair_end"] else None,
            "range_start": preflight_payload["range_start"],
            "range_end": preflight_payload["range_end"],
            "range_reason": preflight_payload["range_reason"],
            "range_driver_symbols": preflight_payload["range_driver_symbols"],
            "delta_batches": preflight_payload["delta_batches"],
            "repair_batches": preflight_payload["repair_batches"],
            "preflight": preflight_payload,
            "symbols_sample": symbols[:10],
            "selected_symbols_sample": selected_symbols[:10],
            "target_tables": ["finance_price.nyse_price_history"],
            "source": "yfinance OHLCV",
            "purpose": "Overview Market Movers non-daily EOD price history refresh",
        }
    )
    if freshness_error:
        details["refresh_preflight_error"] = freshness_error
        details["refresh_fallback_reason"] = "freshness preflight failed; full-window refresh selected"
    result["details"] = details
    base_message = str(result.get("message") or "").strip()
    prefix = f"{normalized_period.title()} Market Movers 가격 이력 갱신"
    if selected_symbols and len(current_symbols) > 0:
        prefix = f"{prefix} ({len(selected_symbols)}개 갱신, {len(current_symbols)}개 최신 스킵)"
    result["message"] = f"{prefix}: {base_message}" if base_message else f"{prefix}을 실행했습니다."
    return result


def run_overview_market_liquidity_universe_refresh(
    *,
    universe_code: str,
    universe_limit: int,
    price_history_period: str = "1mo",
) -> JobResult:
    """Refresh EOD history, then materialize Top universe membership by 20D dollar volume."""
    normalized_universe = str(universe_code or "TOP1000").strip().upper()
    if normalized_universe not in {"TOP1000", "TOP2000"}:
        raise ValueError(f"Unsupported liquidity universe refresh target: {universe_code!r}")

    candidate_rows = load_market_liquidity_universe_candidate_symbols(normalized_universe)
    symbols = _normalize_action_symbols(row.get("symbol") for row in candidate_rows)
    if not symbols:
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "job_name": "overview_market_liquidity_universe_refresh",
            "status": "failed",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": "Top universe 기준 갱신 후보가 없습니다. listing source를 먼저 갱신해야 합니다.",
            "details": {
                "universe_code": normalized_universe,
                "universe_limit": universe_limit,
                "coverage_basis": "20D avg dollar volume from nyse_price_history",
                "candidate_source": "nyse_symbol_lifecycle current listing snapshots",
                "fallback_policy": "no legacy profile fallback",
                "target_tables": [
                    "finance_price.nyse_price_history",
                    "finance_meta.market_liquidity_universe_member",
                ],
            },
        }

    eod_result = dict(
        run_collect_ohlcv(
            symbols,
            period=price_history_period,
            interval="1d",
            execution_profile="managed_safe",
        )
    )
    materialized = collect_and_store_market_liquidity_universe(
        universe_code=normalized_universe,
        universe_limit=universe_limit,
        candidate_rows=candidate_rows,
    )

    details = dict(eod_result.get("details") or {})
    details.update(
        {
            "universe_code": normalized_universe,
            "universe_limit": universe_limit,
            "coverage_basis": "20D avg dollar volume from nyse_price_history",
            "candidate_source": "nyse_symbol_lifecycle current listing snapshots",
            "fallback_policy": "no legacy profile fallback",
            "price_history_period": price_history_period,
            "interval": "1d",
            "symbols_requested": len(symbols),
            "symbols_sample": symbols[:10],
            "materialized": materialized,
            "target_tables": [
                "finance_price.nyse_price_history",
                "finance_meta.market_liquidity_universe_member",
            ],
            "source": "listing lifecycle + yfinance OHLCV + nyse_price_history 20D dollar volume",
            "purpose": "Overview Market Movers Top universe basis refresh",
        }
    )
    status = "success" if str(eod_result.get("status") or "success").lower() == "success" and materialized["rows_written"] else "failed"
    return {
        **eod_result,
        "job_name": "overview_market_liquidity_universe_refresh",
        "status": status,
        "rows_written": materialized["rows_written"],
        "symbols_requested": len(symbols),
        "symbols_processed": eod_result.get("symbols_processed", len(symbols)),
        "failed_symbols": eod_result.get("failed_symbols", []),
        "message": (
            f"{normalized_universe} 유니버스 기준 갱신: "
            f"{materialized['rows_written']}개를 20D 평균 거래대금 기준으로 저장했습니다."
        ),
        "details": details,
    }


def run_overview_market_mover_statement_refresh(
    *,
    symbol: str,
    freq: str = "quarterly",
    periods: int = 0,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Refresh EDGAR statement data for one Market Movers selected symbol through Ingestion."""

    symbols = _normalize_action_symbols([symbol])
    normalized_freq = str(freq or "quarterly").strip().lower()
    if normalized_freq not in {"annual", "quarterly"}:
        raise ValueError(f"Unsupported statement refresh frequency: {freq!r}")
    normalized_periods = max(0, int(periods or 0))
    if not symbols:
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "job_name": "overview_market_mover_statement_refresh",
            "status": "failed",
            "started_at": now_text,
            "finished_at": now_text,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "message": "Market Movers 재무제표 수집 대상 symbol이 없습니다.",
            "details": {
                "symbols": [],
                "freq": normalized_freq,
                "period": normalized_freq,
                "periods": normalized_periods,
                "target_tables": [
                    "finance_fundamental.nyse_financial_statement_filings",
                    "finance_fundamental.nyse_financial_statement_values",
                    "finance_fundamental.nyse_fundamentals_statement",
                    "finance_fundamental.nyse_factors_statement",
                ],
                "source": "SEC EDGAR statement ingestion",
                "purpose": "Overview Market Movers selected-symbol financial statement refresh",
            },
        }

    result = dict(
        run_extended_statement_refresh(
            symbols=symbols,
            freq=normalized_freq,
            period=normalized_freq,
            periods=normalized_periods,
            progress_callback=progress_callback,
        )
    )
    source_job_name = str(result.get("job_name") or "extended_statement_refresh")
    result["job_name"] = "overview_market_mover_statement_refresh"
    details = dict(result.get("details") or {})
    details.update(
        {
            "source_job_name": source_job_name,
            "symbol": symbols[0],
            "symbols": symbols,
            "freq": normalized_freq,
            "period": normalized_freq,
            "periods": normalized_periods,
            "target_tables": [
                "finance_fundamental.nyse_financial_statement_filings",
                "finance_fundamental.nyse_financial_statement_values",
                "finance_fundamental.nyse_fundamentals_statement",
                "finance_fundamental.nyse_factors_statement",
            ],
            "source": "SEC EDGAR statement ingestion",
            "purpose": "Overview Market Movers selected-symbol financial statement refresh",
        }
    )
    result["details"] = details
    base_message = str(result.get("message") or "").strip()
    prefix = f"{symbols[0]} {normalized_freq} 재무제표 수집"
    result["message"] = f"{prefix}: {base_message}" if base_message else f"{prefix}을 실행했습니다."
    return result


def run_overview_historical_analog_ohlcv(
    *,
    symbols: Iterable[str],
    period: str = "10y",
    interval: str = "1d",
) -> JobResult:
    """Collect missing sector-proxy price history through the existing OHLCV pipeline."""
    selected_symbols = _normalize_action_symbols(symbols)
    result = dict(
        run_collect_ohlcv(
            selected_symbols,
            period=period,
            interval=interval,
            execution_profile="managed_safe",
        )
    )
    result["job_name"] = "overview_historical_analog_ohlcv"
    details = dict(result.get("details") or {})
    details.update(
        {
            "symbols": selected_symbols,
            "period": period,
            "interval": interval,
            "target_tables": ["finance_price.nyse_price_history"],
            "source": "yfinance OHLCV",
            "purpose": "Overview Market Context historical analog coverage repair",
        }
    )
    result["details"] = details
    if result.get("message"):
        result["message"] = f"과거 유사 맥락 가격 이력 보강: {result['message']}"
    else:
        result["message"] = "과거 유사 맥락 가격 이력 보강을 실행했습니다."
    return result


def _overview_bundle_result(label: str, result: JobResult) -> JobResult:
    row = dict(result or {})
    row["label"] = label
    row.setdefault("job_name", label)
    row.setdefault("status", "success")
    row.setdefault("message", f"{label} completed.")
    return row


def _overview_bundle_failed_result(label: str, exc: Exception, *, started_at: str, finished_at: str) -> JobResult:
    return {
        "label": label,
        "job_name": label,
        "status": "failed",
        "started_at": started_at,
        "finished_at": finished_at,
        "message": str(exc),
    }


def _overview_bundle_status(results: list[JobResult]) -> str:
    statuses = {str(result.get("status") or "").lower() for result in results}
    failed_statuses = {"failed", "error"}
    partial_statuses = {"partial_success", "skipped", "locked"}
    if results and statuses <= failed_statuses:
        return "failed"
    if statuses & failed_statuses or statuses & partial_statuses:
        return "partial_success"
    return "success"


def _overview_market_context_refresh_steps(
    *,
    action_ids: Iterable[str],
    years: Iterable[int],
    futures_symbols: Iterable[str],
    futures_cadence_mode: str,
) -> list[tuple[str, Callable[[], JobResult]]]:
    del futures_symbols, futures_cadence_mode
    actions: dict[str, tuple[str, Callable[[], JobResult]]] = {
        "sp500_intraday_snapshot": (
            "S&P 500 Market Movers",
            lambda: run_overview_market_intraday_snapshot(universe_code="SP500", universe_limit=500),
        ),
        "market_sentiment": ("Market Sentiment", run_overview_market_sentiment),
        "fomc_calendar": ("FOMC Calendar", lambda: run_overview_fomc_calendar(years=years)),
        "earnings_calendar": ("Earnings Calendar", run_overview_earnings_calendar),
        "macro_calendar": ("Macro Calendar", lambda: run_overview_macro_calendar(years=years)),
        "sp500_universe": ("S&P 500 Universe", run_overview_sp500_universe),
    }
    steps: list[tuple[str, Callable[[], JobResult]]] = []
    seen: set[str] = set()
    for action_id in action_ids:
        normalized = str(action_id or "").strip()
        if not normalized or normalized in seen or normalized not in actions:
            continue
        seen.add(normalized)
        steps.append(actions[normalized])
    return steps


def _run_overview_market_context_refresh_steps(
    *,
    job_name: str,
    execution_mode: str,
    steps: list[tuple[str, Callable[[], JobResult]]],
    started_at: str,
) -> JobResult:
    if not steps:
        finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return {
            "job_name": job_name,
            "status": "skipped",
            "execution_mode": execution_mode,
            "started_at": started_at,
            "finished_at": finished_at,
            "jobs_due": 0,
            "jobs_run": 0,
            "jobs_failed": 0,
            "results": [],
            "message": "현재 Market Context에서 실행할 보강 작업이 없습니다.",
        }

    results: list[JobResult] = []
    for label, action in steps:
        step_started = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            results.append(_overview_bundle_result(label, action()))
        except Exception as exc:  # pragma: no cover - UI resilience and provider volatility
            results.append(
                _overview_bundle_failed_result(
                    label,
                    exc,
                    started_at=step_started,
                    finished_at=datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                )
            )

    failed_count = sum(1 for result in results if str(result.get("status") or "").lower() in {"failed", "error"})
    status = _overview_bundle_status(results)
    finished_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    return {
        "job_name": job_name,
        "status": status,
        "execution_mode": execution_mode,
        "started_at": started_at,
        "finished_at": finished_at,
        "jobs_due": len(steps),
        "jobs_run": len(results),
        "jobs_failed": failed_count,
        "results": results,
        "message": (
            f"Overview market context 보강: {len(results) - failed_count}/{len(steps)} jobs completed."
            if status != "failed"
            else "Overview market context 보강이 실패했습니다."
        ),
    }


def run_overview_market_context_refresh_all(
    *,
    years: Iterable[int] | None = None,
    futures_symbols: Iterable[str] | None = None,
) -> JobResult:
    """Run the existing bounded Overview market-context refresh actions as one manual bundle."""
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    target_years = tuple(years or (current_year, current_year + 1))
    all_action_ids = (
        "sp500_intraday_snapshot",
        "market_sentiment",
        "fomc_calendar",
        "earnings_calendar",
        "macro_calendar",
    )
    steps = _overview_market_context_refresh_steps(
        action_ids=all_action_ids,
        years=target_years,
        futures_symbols=futures_symbols or DEFAULT_CORE_FUTURES_SYMBOLS,
        futures_cadence_mode="manual_bundle",
    )
    return _run_overview_market_context_refresh_steps(
        job_name="overview_market_context_refresh_all",
        execution_mode="manual_bundle",
        steps=steps,
        started_at=started_at,
    )


def run_overview_market_context_refresh_smart(
    *,
    action_ids: Iterable[str],
    years: Iterable[int] | None = None,
    futures_symbols: Iterable[str] | None = None,
) -> JobResult:
    """Run only the current Market Context refresh actions selected by the read model."""
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    target_years = tuple(years or (current_year, current_year + 1))
    steps = _overview_market_context_refresh_steps(
        action_ids=action_ids,
        years=target_years,
        futures_symbols=futures_symbols or DEFAULT_CORE_FUTURES_SYMBOLS,
        futures_cadence_mode="smart_refresh",
    )
    return _run_overview_market_context_refresh_steps(
        job_name="overview_market_context_refresh_smart",
        execution_mode="smart_refresh",
        steps=steps,
        started_at=started_at,
    )


def run_overview_quote_gap_diagnostics(
    *,
    symbols: Iterable[str],
    universe_code: str,
    interval_code: str,
    snapshot_time_utc: Any,
    max_symbols: int = 50,
) -> JobResult:
    return run_diagnose_market_quote_gaps(
        symbols=list(symbols),
        universe_code=universe_code,
        interval_code=interval_code,
        snapshot_time_utc=snapshot_time_utc,
        max_symbols=max_symbols,
    )
