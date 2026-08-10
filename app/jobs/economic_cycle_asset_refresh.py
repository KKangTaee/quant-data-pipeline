"""Refresh only the DB inputs used by Economic Cycle asset pathways."""

from __future__ import annotations

from datetime import datetime
from time import perf_counter
from typing import Callable

from app.jobs.ingestion_jobs import (
    JobResult,
    run_collect_futures_ohlcv,
    run_collect_macro_market_context,
    run_collect_ohlcv,
)
from finance.loaders.economic_cycle_assets import (
    DEFAULT_ASSET_SYMBOLS,
    DEFAULT_EQUITY_SYMBOLS,
    DEFAULT_PATHWAY_SERIES,
)


def _failed_step(scope: str, exc: Exception) -> JobResult:
    return {
        "scope": scope,
        "job_name": f"economic_cycle_asset_{scope}",
        "status": "failed",
        "rows_written": 0,
        "failed_symbols": [],
        "message": f"{type(exc).__name__}: {exc}",
    }


def run_economic_cycle_asset_pathway_refresh(
    *,
    macro_runner: Callable[..., JobResult] = run_collect_macro_market_context,
    futures_runner: Callable[..., JobResult] = run_collect_futures_ohlcv,
    equity_runner: Callable[..., JobResult] = run_collect_ohlcv,
) -> JobResult:
    """Run the three bounded ingestion groups without multiplying concurrency."""

    started_at = datetime.now()
    started = perf_counter()
    calls = (
        (
            "macro",
            lambda: macro_runner(series_ids=DEFAULT_PATHWAY_SERIES),
        ),
        (
            "futures",
            lambda: futures_runner(
                symbols=list(DEFAULT_ASSET_SYMBOLS),
                period="1y",
                interval="1d",
                cadence_mode="economic_cycle_asset_daily",
                max_symbols=4,
                batch_size=4,
                sleep_sec=0.1,
                materialize_snapshot=False,
            ),
        ),
        (
            "equity",
            lambda: equity_runner(
                list(DEFAULT_EQUITY_SYMBOLS),
                period="1mo",
                interval="1d",
                execution_profile="managed_safe",
            ),
        ),
    )
    steps: list[JobResult] = []
    for scope, call in calls:
        try:
            row = dict(call())
            row["scope"] = scope
        except Exception as exc:
            row = _failed_step(scope, exc)
        steps.append(row)

    statuses = {str(row.get("status") or "failed") for row in steps}
    rows_written = sum(int(row.get("rows_written") or 0) for row in steps)
    failed_symbols = sorted(
        {
            str(symbol)
            for row in steps
            for symbol in row.get("failed_symbols") or []
        }
    )
    status = (
        "failed"
        if statuses <= {"failed", "error"}
        else "partial_success"
        if statuses - {"success"}
        else "success"
    )
    finished_at = datetime.now()
    return {
        "job_name": "refresh_economic_cycle_asset_pathways",
        "status": status,
        "started_at": started_at.strftime("%Y-%m-%d %H:%M:%S"),
        "finished_at": finished_at.strftime("%Y-%m-%d %H:%M:%S"),
        "duration_sec": round(perf_counter() - started, 3),
        "rows_written": rows_written,
        "symbols_requested": 15,
        "symbols_processed": 15 - len(failed_symbols),
        "failed_symbols": failed_symbols,
        "message": "Economic-cycle asset pathway refresh completed.",
        "details": {"steps": steps},
    }
