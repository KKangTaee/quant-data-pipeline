"""Dispatch Streamlit ingestion actions to job wrappers or read-only diagnostics."""

from __future__ import annotations

from datetime import datetime
from typing import Any

from app.jobs.ingestion_jobs import (
    run_collect_computed_snapshot_lifecycle,
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_futures_ohlcv,
    run_collect_macro_calendar,
    run_collect_market_structure_calendar,
    run_collect_market_sentiment,
    run_collect_sec_company_ticker_crosscheck,
    run_import_bls_macro_calendar_ics,
    run_collect_etf_holdings_exposure,
    run_collect_etf_operability_provider,
    run_collect_sec_form25_delistings,
    run_collect_symbol_directory_snapshots,
    run_discover_etf_provider_source_map,
    run_collect_macro_market_context,
    run_daily_market_update,
    run_extended_statement_refresh,
    run_rebuild_statement_shadow,
    run_metadata_refresh,
    run_collect_asset_profiles,
    run_collect_financial_statements,
    run_calculate_factors,
    run_collect_fundamentals,
    run_collect_ohlcv,
    run_pipeline_core_market_data,
    run_weekly_fundamental_refresh,
)
from app.services.ingestion_diagnostics import (
    run_price_stale_diagnosis,
    run_statement_coverage_diagnosis,
    run_statement_pit_inspection,
    run_statement_universe_coverage_qa,
)
from app.web.ingestion.guides import _job_title


JobResult = dict[str, Any]


def _parse_csv_items(value: str) -> list[str]:
    return [item.strip().upper() for item in str(value or "").replace("\n", ",").split(",") if item.strip()]


def _diagnostic_state_key(action: str) -> str | None:
    return {
        "diagnose_price_stale": "price_stale_diagnosis_result",
        "diagnose_statement_universe_coverage": "statement_universe_coverage_qa_result",
        "diagnose_statement_coverage": "statement_coverage_diagnosis_result",
        "inspect_statement_pit": "statement_pit_inspection_result",
    }.get(action)


def _diagnostic_status_to_job_status(status: Any) -> str:
    normalized = str(status or "").strip().lower()
    if normalized in {"ok", "success", "passed", "pass"}:
        return "success"
    if normalized in {"warning", "partial_success", "review", "needs_review"}:
        return "partial_success"
    return "failed"


def _count_diagnostic_symbols(params: dict[str, Any]) -> int:
    symbols = params.get("symbols")
    if isinstance(symbols, str):
        return len(_parse_csv_items(symbols))
    if isinstance(symbols, (list, tuple, set)):
        return len([symbol for symbol in symbols if str(symbol).strip()])
    return 0


def _build_diagnostic_job_result(
    *,
    action: str,
    params: dict[str, Any],
    diagnostic_result: dict[str, Any],
    started_at: datetime,
    finished_at: datetime,
) -> JobResult:
    status = _diagnostic_status_to_job_status(diagnostic_result.get("status"))
    symbols_requested = _count_diagnostic_symbols(params)
    return {
        "job_name": action,
        "status": status,
        "started_at": started_at.isoformat(timespec="seconds"),
        "finished_at": finished_at.isoformat(timespec="seconds"),
        "duration_sec": round((finished_at - started_at).total_seconds(), 3),
        "rows_written": 0,
        "symbols_requested": symbols_requested,
        "symbols_processed": symbols_requested if status in {"success", "partial_success"} else 0,
        "failed_symbols": [],
        "message": diagnostic_result.get("message") or f"{_job_title(action)} completed.",
        "details": {
            "action": action,
            "diagnostic_result": diagnostic_result,
            "write_behavior": "read_only",
        },
    }


def _dispatch_diagnostic_job(
    action: str,
    params: dict[str, Any],
    *,
    progress_callback: Any = None,
) -> JobResult:
    started_at = datetime.now()
    if progress_callback:
        progress_callback({"type": "stage_start", "stage": action, "stage_index": 1, "total_stages": 1})

    if action == "diagnose_price_stale":
        diagnostic_result = run_price_stale_diagnosis(
            params.get("symbols") or [],
            end=params.get("end"),
            timeframe=params.get("timeframe", "1d"),
        )
    elif action == "diagnose_statement_universe_coverage":
        diagnostic_result = run_statement_universe_coverage_qa(
            universe_code=params.get("universe_code", "TOP1000"),
            universe_limit=params.get("universe_limit"),
            freq=params.get("freq", "annual"),
            as_of_date=params.get("as_of_date"),
        )
    elif action == "diagnose_statement_coverage":
        diagnostic_result = run_statement_coverage_diagnosis(
            params.get("symbols") or [],
            freq=params.get("freq", "quarterly"),
            sample_size=int(params.get("sample_size", 2) or 2),
        )
    elif action == "inspect_statement_pit":
        diagnostic_result = run_statement_pit_inspection(
            symbols=params.get("symbols") or [],
            inspect_freq=params.get("inspect_freq", "quarterly"),
            audit_symbol_limit=int(params.get("audit_symbol_limit", 3) or 3),
            audit_limit_per_symbol=int(params.get("audit_limit_per_symbol", 5) or 5),
            source_symbol=params.get("source_symbol"),
            source_sample_size=int(params.get("source_sample_size", 2) or 2),
        )
    else:
        raise ValueError(f"Unsupported diagnostic action: {action}")

    finished_at = datetime.now()
    if progress_callback:
        progress_callback({"type": "stage_complete", "stage": action, "stage_index": 1, "total_stages": 1})
    return _build_diagnostic_job_result(
        action=action,
        params=params,
        diagnostic_result=diagnostic_result,
        started_at=started_at,
        finished_at=finished_at,
    )


def _dispatch_job(job: dict[str, Any], *, progress_callback: Any = None) -> JobResult:
    action = job["action"]
    params = dict(job["params"])

    if _diagnostic_state_key(action):
        return _dispatch_diagnostic_job(action, params, progress_callback=progress_callback)
    if action == "pipeline_core_market_data":
        params["progress_callback"] = progress_callback
        return run_pipeline_core_market_data(**params)
    if action == "daily_market_update":
        params["progress_callback"] = progress_callback
        return run_daily_market_update(**params)
    if action == "weekly_fundamental_refresh":
        params["progress_callback"] = progress_callback
        return run_weekly_fundamental_refresh(**params)
    if action == "extended_statement_refresh":
        params["progress_callback"] = progress_callback
        return run_extended_statement_refresh(**params)
    if action == "rebuild_statement_shadow":
        params["progress_callback"] = progress_callback
        return run_rebuild_statement_shadow(**params)
    if action == "metadata_refresh":
        params["progress_callback"] = progress_callback
        return run_metadata_refresh(**params)
    if action == "discover_etf_provider_source_map":
        params["progress_callback"] = progress_callback
        return run_discover_etf_provider_source_map(**params)
    if action == "collect_etf_operability_provider":
        params["progress_callback"] = progress_callback
        return run_collect_etf_operability_provider(**params)
    if action == "collect_etf_holdings_exposure":
        params["progress_callback"] = progress_callback
        return run_collect_etf_holdings_exposure(**params)
    if action == "collect_macro_market_context":
        params["progress_callback"] = progress_callback
        return run_collect_macro_market_context(**params)
    if action == "collect_market_sentiment":
        params["progress_callback"] = progress_callback
        return run_collect_market_sentiment(**params)
    if action == "collect_sec_form25_delistings":
        params["progress_callback"] = progress_callback
        return run_collect_sec_form25_delistings(**params)
    if action == "collect_symbol_directory_snapshots":
        params["progress_callback"] = progress_callback
        return run_collect_symbol_directory_snapshots(**params)
    if action == "collect_sec_company_ticker_crosscheck":
        params["progress_callback"] = progress_callback
        return run_collect_sec_company_ticker_crosscheck(**params)
    if action == "collect_computed_snapshot_lifecycle":
        params["progress_callback"] = progress_callback
        return run_collect_computed_snapshot_lifecycle(**params)
    if action == "collect_fomc_calendar":
        params["progress_callback"] = progress_callback
        return run_collect_fomc_calendar(**params)
    if action == "collect_earnings_calendar":
        params["progress_callback"] = progress_callback
        return run_collect_earnings_calendar(**params)
    if action == "collect_futures_ohlcv":
        params["progress_callback"] = progress_callback
        return run_collect_futures_ohlcv(**params)
    if action == "collect_macro_calendar":
        params["progress_callback"] = progress_callback
        return run_collect_macro_calendar(**params)
    if action == "collect_market_structure_calendar":
        params["progress_callback"] = progress_callback
        return run_collect_market_structure_calendar(**params)
    if action == "import_bls_macro_calendar_ics":
        params["progress_callback"] = progress_callback
        return run_import_bls_macro_calendar_ics(**params)
    if action == "collect_ohlcv":
        params["progress_callback"] = progress_callback
        return run_collect_ohlcv(**params)
    if action == "collect_fundamentals":
        return run_collect_fundamentals(**params)
    if action == "calculate_factors":
        return run_calculate_factors(**params)
    if action == "collect_asset_profiles":
        params["progress_callback"] = progress_callback
        return run_collect_asset_profiles(**params)
    if action == "collect_financial_statements":
        params["progress_callback"] = progress_callback
        return run_collect_financial_statements(**params)
    raise ValueError(f"Unsupported job action: {action}")


diagnostic_state_key = _diagnostic_state_key
dispatch_job = _dispatch_job
