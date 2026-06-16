from __future__ import annotations

from datetime import datetime
from typing import Any, Callable, Iterable

from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
from finance.data.market_intelligence import load_market_cap_universe_members, load_market_universe_members

from app.jobs.ingestion_jobs import (
    JobResult,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_futures_ohlcv,
    run_collect_macro_calendar,
    run_collect_market_sentiment,
    run_collect_market_intraday_snapshot,
    run_collect_ohlcv,
    run_collect_sp500_universe,
    run_diagnose_market_quote_gaps,
)
from app.jobs.overview_automation import run_overview_automation
from app.jobs.run_history import append_run_history

MARKET_MOVERS_EOD_COLLECTION_PERIODS = {
    "weekly": "3mo",
    "monthly": "1y",
    "yearly": "3y",
}


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


def run_overview_sp500_universe() -> JobResult:
    return run_collect_sp500_universe()


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


def _load_market_movers_eod_universe_symbols(*, universe_code: str, universe_limit: int) -> tuple[list[str], str]:
    normalized_universe = str(universe_code or "SP500").strip().upper()
    if normalized_universe == "SP500":
        rows = load_market_universe_members("SP500")
        coverage_basis = "Current S&P 500 constituents"
    else:
        rows = load_market_cap_universe_members(normalized_universe, universe_limit=universe_limit)
        coverage_basis = "Latest asset_profile.market_cap snapshot"
    return _normalize_action_symbols(row.get("symbol") for row in rows), coverage_basis


def run_overview_market_movers_eod_history(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> JobResult:
    """Refresh EOD price history for non-daily Market Movers through the existing OHLCV job."""
    normalized_universe = str(universe_code or "SP500").strip().upper()
    normalized_period = str(period or "").strip().lower()
    collection_period = market_movers_eod_collection_period(normalized_period)
    symbols, coverage_basis = _load_market_movers_eod_universe_symbols(
        universe_code=normalized_universe,
        universe_limit=universe_limit,
    )
    if not symbols:
        now_text = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
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
                "target_tables": ["finance_price.nyse_price_history"],
                "source": "yfinance OHLCV",
                "purpose": "Overview Market Movers non-daily EOD price history refresh",
            },
        }

    result = dict(
        run_collect_ohlcv(
            symbols,
            period=collection_period,
            interval="1d",
            execution_profile="managed_safe",
        )
    )
    result["job_name"] = "overview_market_movers_eod_history"
    details = dict(result.get("details") or {})
    details.update(
        {
            "universe_code": normalized_universe,
            "universe_limit": universe_limit,
            "coverage_basis": coverage_basis,
            "market_mover_period": normalized_period,
            "collection_period": collection_period,
            "interval": "1d",
            "symbols_requested": len(symbols),
            "symbols_sample": symbols[:10],
            "target_tables": ["finance_price.nyse_price_history"],
            "source": "yfinance OHLCV",
            "purpose": "Overview Market Movers non-daily EOD price history refresh",
        }
    )
    result["details"] = details
    base_message = str(result.get("message") or "").strip()
    prefix = f"{normalized_period.title()} Market Movers 가격 이력 갱신"
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


def run_overview_market_context_refresh_all(
    *,
    years: Iterable[int] | None = None,
    futures_symbols: Iterable[str] | None = None,
) -> JobResult:
    """Run the existing bounded Overview market-context refresh actions as one manual bundle."""
    started_at = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    current_year = datetime.now().year
    target_years = tuple(years or (current_year, current_year + 1))
    selected_futures = list(futures_symbols or DEFAULT_CORE_FUTURES_SYMBOLS)
    steps: list[tuple[str, Callable[[], JobResult]]] = [
        (
            "S&P 500 Market Movers",
            lambda: run_overview_market_intraday_snapshot(universe_code="SP500", universe_limit=500),
        ),
        (
            "Futures Monitor 1m OHLCV",
            lambda: run_overview_futures_ohlcv(symbols=selected_futures, cadence_mode="manual_bundle"),
        ),
        ("Futures Macro Daily OHLCV", run_overview_futures_daily_ohlcv),
        ("Market Sentiment", run_overview_market_sentiment),
        ("FOMC Calendar", lambda: run_overview_fomc_calendar(years=target_years)),
        ("Earnings Calendar", run_overview_earnings_calendar),
        ("Macro Calendar", lambda: run_overview_macro_calendar(years=target_years)),
    ]

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
        "job_name": "overview_market_context_refresh_all",
        "status": status,
        "execution_mode": "manual_bundle",
        "started_at": started_at,
        "finished_at": finished_at,
        "jobs_due": len(steps),
        "jobs_run": len(results),
        "jobs_failed": failed_count,
        "results": results,
        "message": (
            f"Overview market context 일괄 갱신: {len(results) - failed_count}/{len(steps)} jobs completed."
            if status != "failed"
            else "Overview market context 일괄 갱신이 실패했습니다."
        ),
    }


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
