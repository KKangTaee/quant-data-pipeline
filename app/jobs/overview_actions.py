from __future__ import annotations

from datetime import datetime
from typing import Any, Iterable

from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS

from app.jobs.ingestion_jobs import (
    JobResult,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_futures_ohlcv,
    run_collect_macro_calendar,
    run_collect_market_sentiment,
    run_collect_market_intraday_snapshot,
    run_collect_sp500_universe,
    run_diagnose_market_quote_gaps,
)
from app.jobs.overview_automation import run_overview_automation
from app.jobs.run_history import append_run_history


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
