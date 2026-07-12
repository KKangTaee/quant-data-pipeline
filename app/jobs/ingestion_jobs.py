from __future__ import annotations

from time import perf_counter
from app.jobs.ingestion.common import (
    JobResult,
    _build_result,
    _emit_stage_progress,
    _failed_item_ids,
    _merge_step_failures,
    _now_str,
    _pipeline_status,
    _resolve_ohlcv_execution_profile,
    _status_from_provider_summary,
    parse_symbols,
    split_valid_invalid_symbols,
)
from typing import Any, Callable, Iterable

from finance.data.data import store_ohlcv_to_mysql
from finance.data.factors import upsert_factors, upsert_statement_factors_shadow
from finance.data.financial_statements import upsert_financial_statements
from finance.data.fundamentals import upsert_fundamentals, upsert_statement_fundamentals_shadow
from finance.data.asset_profile import collect_and_store_asset_profiles
from finance.data.computed_lifecycle import collect_and_store_computed_snapshot_lifecycle
from finance.data.etf_provider import (
    aggregate_and_store_etf_exposures,
    collect_and_store_etf_holdings,
    collect_and_store_etf_operability,
    discover_and_store_etf_provider_source_map,
)
from finance.data.futures_market import (
    DEFAULT_CORE_FUTURES_SYMBOLS,
    collect_and_store_futures_ohlcv,
    normalize_futures_symbols,
)
from finance.data.macro import DEFAULT_MACRO_SERIES, collect_and_store_macro_series
from finance.data.sentiment import collect_and_store_market_sentiment
from finance.data.sp500_valuation import (
    collect_and_store_fomc_sep,
    collect_and_store_shiller_monthly_valuation,
    ensure_sp500_valuation_schemas,
    import_and_store_sp500_index_earnings,
)
from finance.data.market_intelligence import (
    collect_and_store_bls_macro_calendar_ics,
    collect_and_store_earnings_calendar,
    collect_and_store_fomc_calendar,
    collect_and_store_macro_calendar,
    collect_and_store_market_structure_calendar,
    collect_and_store_market_intraday_snapshot,
    collect_and_store_sp500_universe,
    diagnose_market_quote_gaps,
    persist_quote_gap_diagnostics,
)
from finance.data.sec_company_tickers import collect_and_store_sec_company_ticker_crosscheck
from finance.data.sec_delisting import collect_and_store_sec_form25_delistings
from finance.data.symbol_directory import collect_and_store_symbol_directory_snapshots


def run_collect_ohlcv(
    symbols: str | Iterable[str] | None,
    *,
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
    interval: str = "1d",
    execution_profile: str = "managed_safe",
    excluded_symbols: Iterable[str] | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_ohlcv"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
        )

    normalized_profile, writer_kwargs = _resolve_ohlcv_execution_profile(execution_profile)
    excluded_symbols_list = parse_symbols(excluded_symbols)

    try:
        write_stats = store_ohlcv_to_mysql(
            parsed,
            start=start,
            end=end,
            period=period,
            interval=interval,
            return_stats=True,
            progress_callback=progress_callback,
            **writer_kwargs,
        )
        rows_written = int(write_stats["rows_written"])
        missing_symbols = list(write_stats.get("missing_symbols") or [])
        symbols_with_data = int(write_stats.get("symbols_with_data") or 0)
        provider_no_data_symbols = list(write_stats.get("provider_no_data_symbols") or [])
        rate_limited_symbols = list(write_stats.get("rate_limited_symbols") or [])
        cooldown_events = list(write_stats.get("cooldown_events") or [])
        timing_breakdown = dict(write_stats.get("timing_breakdown") or {})
        all_failed_symbols = invalid_symbols + [sym for sym in missing_symbols if sym not in invalid_symbols]
        finished_at = _now_str()
        if rows_written > 0:
            status = "success" if not all_failed_symbols else "partial_success"
            msg = "OHLCV collection completed."
        else:
            status = "failed"
            msg = (
                "OHLCV collection finished with no rows written. "
                "The symbols may be invalid, delisted, or unavailable from the provider."
            )
        if missing_symbols:
            msg += f" Missing provider data for: {', '.join(missing_symbols[:10])}."
        if invalid_symbols:
            msg += f" Invalid symbols ignored: {', '.join(invalid_symbols[:10])}."
        if rate_limited_symbols:
            msg += f" Rate limit detected for: {', '.join(rate_limited_symbols[:10])}."
        if excluded_symbols_list:
            msg += f" Filtered non-plain symbols: {', '.join(excluded_symbols_list[:10])}."

        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=len(parsed),
            symbols_processed=symbols_with_data,
            failed_symbols=all_failed_symbols if all_failed_symbols else parsed if rows_written == 0 else [],
            message=msg,
            details={
                "start": start,
                "end": end,
                "period": period,
                "interval": interval,
                "execution_profile": normalized_profile,
                "write_settings": writer_kwargs,
                "symbols_with_data": symbols_with_data,
                "missing_symbols": missing_symbols,
                "provider_no_data_symbols": provider_no_data_symbols,
                "rate_limited_symbols": rate_limited_symbols,
                "excluded_symbols": excluded_symbols_list,
                "cooldown_events": cooldown_events,
                "timing_breakdown": timing_breakdown,
                "batch_errors": write_stats.get("batch_errors") or [],
                "provider_message_batches": write_stats.get("provider_message_batches") or [],
                "rerun_missing_payload": ",".join(missing_symbols),
                "rerun_rate_limited_payload": ",".join(rate_limited_symbols),
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            message=f"OHLCV collection failed: {exc}",
            details={
                "start": start,
                "end": end,
                "period": period,
                "interval": interval,
                "execution_profile": normalized_profile,
                "write_settings": writer_kwargs,
                "excluded_symbols": excluded_symbols_list,
                "timing_breakdown": {},
            },
        )


def run_collect_sp500_valuation_context(
    *,
    index_earnings_path: str | None = None,
    source_release_date: str | None = None,
) -> JobResult:
    """Refresh the DB inputs used by the S&P 500 valuation read model."""
    job_name = "collect_sp500_valuation_context"
    started_at = _now_str()
    t0 = perf_counter()
    steps: list[dict[str, Any]] = []

    try:
        ensure_sp500_valuation_schemas()
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=2,
            symbols_processed=0,
            message=f"S&P 500 valuation schema bootstrap failed: {exc}",
            details={"pipeline_type": "sp500_valuation_context", "steps": []},
        )

    def collect_step(label: str, collector: Callable[[], dict[str, Any]]) -> None:
        try:
            payload = dict(collector() or {})
            steps.append(
                {
                    "label": label,
                    "status": "success",
                    "rows_written": int(payload.get("rows_written") or 0),
                    "details": payload,
                }
            )
        except Exception as exc:
            steps.append(
                {
                    "label": label,
                    "status": "failed",
                    "rows_written": 0,
                    "message": str(exc),
                }
            )

    collect_step("Shiller monthly valuation", collect_and_store_shiller_monthly_valuation)
    collect_step("Federal Reserve SEP", collect_and_store_fomc_sep)
    if index_earnings_path and source_release_date:
        collect_step(
            "S&P Index Earnings",
            lambda: import_and_store_sp500_index_earnings(
                index_earnings_path,
                source_release_date=source_release_date,
            ),
        )
    else:
        steps.append(
            {
                "label": "S&P Index Earnings",
                "status": "skipped",
                "rows_written": 0,
                "message": "명시적 workbook path와 release date가 없어 기존 actual EPS를 유지합니다.",
            }
        )

    price_result = run_collect_ohlcv(
        ["^GSPC", "SPY"],
        period="1mo",
        interval="1d",
        execution_profile="managed_safe",
    )
    steps.append(
        {
            "label": "SPX/SPY EOD",
            "status": str(price_result.get("status") or "failed"),
            "rows_written": int(price_result.get("rows_written") or 0),
            "message": price_result.get("message"),
            "details": price_result.get("details") or {},
        }
    )

    failed = [step for step in steps if step["status"] == "failed"]
    succeeded = [step for step in steps if step["status"] in {"success", "partial_success"}]
    rows_written = sum(int(step.get("rows_written") or 0) for step in steps)
    if failed and succeeded:
        status = "partial_success"
    elif failed:
        status = "failed"
    else:
        status = "success"
    finished_at = _now_str()
    return _build_result(
        job_name=job_name,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=perf_counter() - t0,
        rows_written=rows_written,
        symbols_requested=2,
        symbols_processed=2 if price_result.get("status") == "success" else 0,
        message=(
            "S&P 500 valuation context refresh completed."
            if status == "success"
            else "S&P 500 valuation context refresh completed with source failures."
        ),
        details={
            "pipeline_type": "sp500_valuation_context",
            "target_tables": [
                "finance_meta.sp500_monthly_valuation",
                "finance_meta.sp500_index_earnings",
                "finance_meta.fomc_sep_projection",
                "finance_price.nyse_price_history",
            ],
            "steps": steps,
        },
    )


def run_collect_fundamentals(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "annual",
) -> JobResult:
    job_name = "collect_fundamentals"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
        )

    try:
        rows_written = upsert_fundamentals(parsed, freq=freq)
        finished_at = _now_str()
        if rows_written > 0:
            status = "success" if not invalid_symbols else "partial_success"
            msg = "Fundamentals ingestion completed."
        else:
            status = "failed"
            msg = (
                "Fundamentals ingestion finished with no rows written. "
                "Check symbol validity and provider coverage for the selected frequency."
            )
        if invalid_symbols:
            msg += f" Invalid symbols ignored: {', '.join(invalid_symbols[:10])}."
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if rows_written > 0 else 0,
            failed_symbols=invalid_symbols if invalid_symbols else parsed if rows_written == 0 else [],
            message=msg,
            details={"freq": freq},
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            message=f"Fundamentals ingestion failed: {exc}",
            details={"freq": freq},
        )


def run_calculate_factors(
    symbols: str | Iterable[str] | None = None,
    *,
    freq: str | None = None,
    start: str | None = None,
    end: str | None = None,
) -> JobResult:
    job_name = "calculate_factors"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)
    requested = len(parsed) if parsed else None

    if symbols is not None and not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
            details={
                "freq": freq,
                "start": start,
                "end": end,
            },
        )

    try:
        rows_written = upsert_factors(
            symbols=parsed or None,
            freq=freq,
            start=start,
            end=end,
        )
        finished_at = _now_str()
        if rows_written > 0:
            status = "success" if not invalid_symbols else "partial_success"
            msg = "Factor calculation completed."
        else:
            status = "failed"
            msg = (
                "Factor calculation finished with no rows written. "
                "Matching OHLCV or fundamentals data may be missing in MySQL."
            )
        if invalid_symbols:
            msg += f" Invalid symbols ignored: {', '.join(invalid_symbols[:10])}."
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=requested,
            symbols_processed=requested if rows_written > 0 else 0,
            failed_symbols=invalid_symbols if invalid_symbols else parsed if rows_written == 0 and parsed else [],
            message=msg,
            details={
                "freq": freq,
                "start": start,
                "end": end,
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=requested,
            symbols_processed=0,
            message=f"Factor calculation failed: {exc}",
            details={
                "freq": freq,
                "start": start,
                "end": end,
            },
        )


def run_pipeline_core_market_data(
    symbols: str | Iterable[str] | None,
    *,
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
    interval: str = "1d",
    freq: str = "annual",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "pipeline_core_market_data"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
            details={"steps": []},
        )

    steps: list[JobResult] = []

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_start",
                "stage": "ohlcv",
                "stage_index": 1,
                "total_stages": 3,
            }
        )

    ohlcv_result = run_collect_ohlcv(
        parsed,
        start=start,
        end=end,
        period=period,
        interval=interval,
        progress_callback=progress_callback,
    )
    steps.append(ohlcv_result)

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_complete",
                "stage": "ohlcv",
                "stage_index": 1,
                "total_stages": 3,
            }
        )

    if ohlcv_result["status"] == "failed":
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=ohlcv_result.get("rows_written") or 0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=invalid_symbols + (ohlcv_result.get("failed_symbols") or []),
            message="Pipeline stopped because OHLCV collection failed.",
            details={"steps": steps},
        )

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_start",
                "stage": "fundamentals",
                "stage_index": 2,
                "total_stages": 3,
            }
        )

    fundamentals_result = run_collect_fundamentals(parsed, freq=freq)
    steps.append(fundamentals_result)

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_complete",
                "stage": "fundamentals",
                "stage_index": 2,
                "total_stages": 3,
            }
        )

    if fundamentals_result["status"] == "failed":
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=(ohlcv_result.get("rows_written") or 0) + (fundamentals_result.get("rows_written") or 0),
            symbols_requested=len(parsed),
            symbols_processed=len(parsed),
            failed_symbols=invalid_symbols + (fundamentals_result.get("failed_symbols") or []),
            message="Pipeline stopped because fundamentals ingestion failed.",
            details={"steps": steps},
        )

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_start",
                "stage": "factors",
                "stage_index": 3,
                "total_stages": 3,
            }
        )

    factors_result = run_calculate_factors(
        parsed,
        freq=freq,
        start=start,
        end=end,
    )
    steps.append(factors_result)

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_complete",
                "stage": "factors",
                "stage_index": 3,
                "total_stages": 3,
            }
        )

    statuses = [step["status"] for step in steps]
    if any(status == "failed" for status in statuses):
        status = "failed"
    elif any(status == "partial_success" for status in statuses):
        status = "partial_success"
    else:
        status = "success"

    finished_at = _now_str()
    total_rows = sum((step.get("rows_written") or 0) for step in steps)

    return _build_result(
        job_name=job_name,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=perf_counter() - t0,
        rows_written=total_rows,
        symbols_requested=len(parsed),
        symbols_processed=len(parsed) if total_rows > 0 else 0,
        failed_symbols=invalid_symbols + [sym for step in steps for sym in step.get("failed_symbols", [])],
        message="Core market-data pipeline completed." if total_rows > 0 else "Core market-data pipeline finished with no rows written.",
        details={
            "steps": steps,
            "period": period,
            "interval": interval,
            "freq": freq,
            "start": start,
            "end": end,
        },
    )


def run_daily_market_update(
    symbols: str | Iterable[str] | None,
    *,
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
    interval: str = "1d",
    execution_profile: str = "managed_safe",
    excluded_symbols: Iterable[str] | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    result = run_collect_ohlcv(
        symbols,
        start=start,
        end=end,
        period=period,
        interval=interval,
        execution_profile=execution_profile,
        excluded_symbols=excluded_symbols,
        progress_callback=progress_callback,
    )
    result["job_name"] = "daily_market_update"
    if result["status"] == "success":
        result["message"] = "Daily market update completed."
    elif result["status"] == "partial_success":
        result["message"] = "Daily market update completed with partial success."
    else:
        result["message"] = "Daily market update failed."
    result.setdefault("details", {})
    result["details"]["pipeline_type"] = "daily_market_update"
    return result


def run_collect_sp500_universe() -> JobResult:
    job_name = "collect_sp500_universe"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        result = collect_and_store_sp500_universe()
        rows_written = int(result.get("rows_written") or 0)
        symbols = list(result.get("symbols") or [])
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="success" if rows_written else "failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=len(symbols),
            symbols_processed=rows_written,
            failed_symbols=[] if rows_written else symbols,
            message="S&P 500 universe collection completed." if rows_written else "S&P 500 universe collection wrote no rows.",
            details=result,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            message=f"S&P 500 universe collection failed: {exc}",
        )


MARKET_INTRADAY_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
    "NASDAQ": "Nasdaq-listed",
}


def run_collect_market_intraday_snapshot(
    *,
    universe_code: str = "SP500",
    universe_limit: int | None = None,
    interval: str = "5m",
    chunk_size: int = 100,
    quote_batch_size: int = 200,
    method: str = "quote_fast",
    fallback_to_yfinance: bool = True,
) -> JobResult:
    normalized_universe = str(universe_code or "SP500").strip().upper()
    universe_label = MARKET_INTRADAY_LABELS.get(normalized_universe, normalized_universe)
    job_name = f"collect_{normalized_universe.lower()}_intraday_snapshot"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        result = collect_and_store_market_intraday_snapshot(
            universe_code=normalized_universe,
            universe_limit=universe_limit,
            interval=interval,
            chunk_size=chunk_size,
            quote_batch_size=quote_batch_size,
            method=method,
            fallback_to_yfinance=fallback_to_yfinance,
        )
        rows_written = int(result.get("rows_written") or 0)
        failed_symbols = list(result.get("failed_symbols") or [])
        requested = int(result.get("symbols_requested") or 0)
        processed = int(result.get("symbols_processed") or 0)
        finished_at = _now_str()
        if rows_written <= 0:
            status = "failed"
            message = f"{universe_label} intraday snapshot wrote no rows."
        elif failed_symbols:
            status = "partial_success"
            message = f"{universe_label} intraday snapshot completed with missing symbols."
        else:
            status = "success"
            message = f"{universe_label} intraday snapshot completed."
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=requested,
            symbols_processed=processed,
            failed_symbols=failed_symbols,
            message=message,
            details=result,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            message=f"{universe_label} intraday snapshot failed: {exc}",
            details={
                "universe_code": normalized_universe,
                "universe_limit": universe_limit,
                "interval": interval,
                "chunk_size": chunk_size,
                "quote_batch_size": quote_batch_size,
                "method": method,
                "fallback_to_yfinance": fallback_to_yfinance,
            },
        )


def run_collect_sp500_intraday_snapshot(
    *,
    interval: str = "5m",
    chunk_size: int = 100,
    quote_batch_size: int = 200,
    method: str = "quote_fast",
    fallback_to_yfinance: bool = True,
) -> JobResult:
    return run_collect_market_intraday_snapshot(
        universe_code="SP500",
        universe_limit=500,
        interval=interval,
        chunk_size=chunk_size,
        quote_batch_size=quote_batch_size,
        method=method,
        fallback_to_yfinance=fallback_to_yfinance,
    )


def run_collect_futures_ohlcv(
    symbols: str | Iterable[str] | None = None,
    *,
    period: str = "1d",
    interval: str = "1m",
    cadence_mode: str = "manual",
    max_symbols: int = 24,
    batch_size: int = 8,
    sleep_sec: float = 0.15,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_futures_ohlcv"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        requested_symbols = normalize_futures_symbols(
            symbols if symbols is not None else DEFAULT_CORE_FUTURES_SYMBOLS,
            max_symbols=max_symbols,
        )
        _emit_stage_progress(progress_callback, event="stage_start", stage="futures_ohlcv")
        result = collect_and_store_futures_ohlcv(
            requested_symbols,
            period=period,
            interval=interval,
            cadence_mode=cadence_mode,
            max_symbols=max_symbols,
            batch_size=batch_size,
            sleep_sec=sleep_sec,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="futures_ohlcv")
        rows_written = int(result.get("rows_written") or 0)
        failed_symbols = list(result.get("failed_symbols") or [])
        requested = int(result.get("symbols_requested") or len(requested_symbols))
        processed = int(result.get("symbols_processed") or 0)
        finished_at = _now_str()
        if rows_written <= 0:
            status = "failed"
            message = "Futures OHLCV collection wrote no rows."
        elif failed_symbols:
            status = "partial_success"
            message = "Futures OHLCV collection completed with missing symbols."
        else:
            status = "success"
            message = "Futures OHLCV collection completed."
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=requested,
            symbols_processed=processed,
            failed_symbols=failed_symbols,
            message=message,
            details={
                "source": result.get("source") or "yfinance",
                "method": "yfinance_ohlcv",
                "period": result.get("period") or period,
                "interval": result.get("interval") or interval,
                "cadence_mode": result.get("cadence_mode") or cadence_mode,
                "latest_candle_time_utc": result.get("latest_candle_time_utc"),
                "run_id": result.get("run_id"),
                "target_tables": [
                    "finance_price.futures_ohlcv",
                    "finance_meta.futures_instrument",
                    "finance_meta.futures_market_monitor_run",
                ],
                "diagnostics": result.get("diagnostics") or {},
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            message=f"Futures OHLCV collection failed: {exc}",
            details={
                "source": "yfinance",
                "method": "yfinance_ohlcv",
                "period": period,
                "interval": interval,
                "cadence_mode": cadence_mode,
            },
        )


def run_collect_fomc_calendar(
    *,
    years: Iterable[int] | None = None,
    source_url: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_fomc_calendar"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        normalized_years = tuple(int(year) for year in years) if years else None
        _emit_stage_progress(progress_callback, event="stage_start", stage="fomc_calendar")
        result = collect_and_store_fomc_calendar(
            years=normalized_years,
            **({"source_url": source_url} if source_url else {}),
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="fomc_calendar")
        rows_written = int(result.get("rows_written") or 0)
        events_found = int(result.get("events_found") or 0)
        finished_at = _now_str()
        status = "success" if rows_written > 0 else "failed"
        message = (
            f"FOMC calendar collected {events_found} events from the official Fed page."
            if rows_written > 0
            else "FOMC calendar collection wrote no rows."
        )
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            message=message,
            details=result,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            message=f"FOMC calendar collection failed: {exc}",
            details={"years": list(years or []), "source_url": source_url},
        )


def run_collect_earnings_calendar(
    *,
    symbols: str | Iterable[str] | None = None,
    symbol_source: str = "latest_movers",
    universe_code: str = "SP500",
    universe_limit: int | None = None,
    interval: str = "5m",
    top_movers_limit: int = 20,
    lookahead_days: int = 120,
    max_symbols: int = 100,
    batch_offset: int = 0,
    validate_with_nasdaq: bool = False,
    request_sleep_sec: float = 0.0,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_earnings_calendar"
    started_at = _now_str()
    t0 = perf_counter()
    parsed_symbols: list[str] | None = None
    invalid_symbols: list[str] = []
    if symbols is not None:
        parsed_symbols, invalid_symbols = split_valid_invalid_symbols(symbols)
        if not parsed_symbols:
            finished_at = _now_str()
            return _build_result(
                job_name=job_name,
                status="failed",
                started_at=started_at,
                finished_at=finished_at,
                duration_sec=perf_counter() - t0,
                rows_written=0,
                symbols_requested=0,
                symbols_processed=0,
                failed_symbols=invalid_symbols,
                message="Earnings calendar collection needs at least one valid symbol.",
                details={"symbol_source": "manual", "invalid_symbols": invalid_symbols},
            )
    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="earnings_calendar")
        result = collect_and_store_earnings_calendar(
            symbols=parsed_symbols,
            symbol_source=symbol_source,
            universe_code=universe_code,
            universe_limit=universe_limit,
            interval=interval,
            top_movers_limit=top_movers_limit,
            lookahead_days=lookahead_days,
            max_symbols=max_symbols,
            batch_offset=batch_offset,
            validate_with_nasdaq=validate_with_nasdaq,
            request_sleep_sec=request_sleep_sec,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="earnings_calendar")
        rows_written = int(result.get("rows_written") or 0)
        symbols_requested = int(result.get("symbols_requested") or 0)
        symbols_processed = int(result.get("symbols_processed") or 0)
        missing_symbols = [str(item) for item in result.get("missing_symbols") or []]
        failed_symbols = invalid_symbols + [str(item) for item in result.get("failed_symbols") or []]
        surfaced_symbols = failed_symbols + [item for item in missing_symbols if item not in failed_symbols]
        finished_at = _now_str()
        if rows_written > 0 and not surfaced_symbols:
            status = "success"
        elif rows_written > 0:
            status = "partial_success"
        else:
            status = "failed"
        events_found = int(result.get("events_found") or 0)
        issue_suffix = ""
        if surfaced_symbols:
            issue_suffix = f" Missing/failed symbols: {len(surfaced_symbols)}."
        message = (
            f"Earnings calendar collected {events_found} events for {symbols_processed} / {symbols_requested} symbols."
            if rows_written > 0
            else "Earnings calendar collection wrote no rows."
        ) + issue_suffix
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=symbols_requested,
            symbols_processed=symbols_processed,
            failed_symbols=surfaced_symbols,
            message=message,
            details={**result, "invalid_symbols": invalid_symbols},
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed_symbols or []),
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message=f"Earnings calendar collection failed: {exc}",
            details={
                "symbol_source": symbol_source,
                "universe_code": universe_code,
                "batch_offset": batch_offset,
                "top_movers_limit": top_movers_limit,
                "lookahead_days": lookahead_days,
                "validate_with_nasdaq": validate_with_nasdaq,
                "request_sleep_sec": request_sleep_sec,
                "invalid_symbols": invalid_symbols,
            },
        )


def run_collect_macro_calendar(
    *,
    years: Iterable[int] | None = None,
    include_bls: bool = True,
    include_bea: bool = True,
    include_census: bool = True,
    include_ism: bool = True,
    include_treasury: bool = True,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_macro_calendar"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        normalized_years = tuple(int(year) for year in years) if years else None
        _emit_stage_progress(progress_callback, event="stage_start", stage="macro_calendar")
        result = collect_and_store_macro_calendar(
            years=normalized_years,
            include_bls=include_bls,
            include_bea=include_bea,
            include_census=include_census,
            include_ism=include_ism,
            include_treasury=include_treasury,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="macro_calendar")
        rows_written = int(result.get("rows_written") or 0)
        events_found = int(result.get("events_found") or 0)
        failed_sources = [str(item) for item in result.get("failed_sources") or []]
        finished_at = _now_str()
        if rows_written > 0 and not failed_sources:
            status = "success"
        elif rows_written > 0:
            status = "partial_success"
        else:
            status = "failed"
        message = (
            f"Macro calendar collected {events_found} official release events."
            if rows_written > 0
            else "Macro calendar collection wrote no rows."
        )
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            failed_symbols=failed_sources,
            message=message,
            details=result,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            message=f"Macro calendar collection failed: {exc}",
            details={
                "years": list(years or []),
                "include_bls": include_bls,
                "include_bea": include_bea,
            },
        )


def run_collect_market_structure_calendar(
    *,
    years: Iterable[int] | None = None,
    include_holidays: bool = True,
    include_options_expiration: bool = True,
    include_russell: bool = True,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_market_structure_calendar"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        normalized_years = tuple(int(year) for year in years) if years else None
        _emit_stage_progress(progress_callback, event="stage_start", stage="market_structure_calendar")
        result = collect_and_store_market_structure_calendar(
            years=normalized_years,
            include_holidays=include_holidays,
            include_options_expiration=include_options_expiration,
            include_russell=include_russell,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="market_structure_calendar")
        rows_written = int(result.get("rows_written") or 0)
        events_found = int(result.get("events_found") or 0)
        failed_sources = [str(item) for item in result.get("failed_sources") or []]
        finished_at = _now_str()
        if rows_written > 0 and not failed_sources:
            status = "success"
        elif rows_written > 0:
            status = "partial_success"
        else:
            status = "failed"
        message = (
            f"Market-structure calendar collected {events_found} event dates."
            if rows_written > 0
            else "Market-structure calendar collection wrote no rows."
        )
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            failed_symbols=failed_sources,
            message=message,
            details=result,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            message=f"Market-structure calendar collection failed: {exc}",
            details={
                "years": list(years or []),
                "include_holidays": include_holidays,
                "include_options_expiration": include_options_expiration,
                "include_russell": include_russell,
            },
        )


def run_diagnose_market_quote_gaps(
    *,
    symbols: str | Iterable[str] | None = None,
    universe_code: str = "SP500",
    interval_code: str = "5m",
    snapshot_time_utc: str | None = None,
    max_symbols: int = 50,
) -> JobResult:
    job_name = "diagnose_market_quote_gaps"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)
    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="Quote gap diagnosis needs at least one valid missing symbol.",
            details={"invalid_symbols": invalid_symbols, "universe_code": universe_code},
        )
    try:
        result = diagnose_market_quote_gaps(
            parsed,
            universe_code=universe_code,
            interval_code=interval_code,
            snapshot_time_utc=snapshot_time_utc,
            max_symbols=max_symbols,
        )
        diagnostics = list(result.get("diagnostics") or [])
        counts = dict(result.get("diagnosis_counts") or {})
        issue_persistence: dict[str, Any] = {"rows_written": 0, "issues": []}
        if diagnostics:
            issue_persistence = persist_quote_gap_diagnostics(
                diagnostics,
                universe_code=universe_code,
                interval_code=interval_code,
                snapshot_time_utc=snapshot_time_utc,
            )
        finished_at = _now_str()
        status = "success" if diagnostics else "failed"
        message = (
            f"Quote gap diagnosis completed for {len(diagnostics)} / {len(parsed)} symbols."
            if diagnostics
            else "Quote gap diagnosis produced no rows."
        )
        if counts:
            message += " " + ", ".join(f"{key}: {value}" for key, value in counts.items()) + "."
        if issue_persistence.get("rows_written"):
            message += f" Persisted {issue_persistence['rows_written']} issue row(s)."
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=len(diagnostics),
            failed_symbols=invalid_symbols,
            message=message,
            details={
                **result,
                "invalid_symbols": invalid_symbols,
                "issue_rows_written": issue_persistence.get("rows_written") or 0,
                "issue_history": issue_persistence.get("issues") or [],
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=invalid_symbols + parsed,
            message=f"Quote gap diagnosis failed: {exc}",
            details={
                "invalid_symbols": invalid_symbols,
                "universe_code": universe_code,
                "interval_code": interval_code,
                "snapshot_time_utc": snapshot_time_utc,
            },
        )


def run_import_bls_macro_calendar_ics(
    *,
    ics_text: str,
    years: Iterable[int] | None = None,
    source_name: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "import_bls_macro_calendar_ics"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        normalized_years = tuple(int(year) for year in years) if years else None
        _emit_stage_progress(progress_callback, event="stage_start", stage="bls_macro_calendar_ics")
        result = collect_and_store_bls_macro_calendar_ics(
            ics_text,
            years=normalized_years,
            source_name=source_name,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="bls_macro_calendar_ics")
        rows_written = int(result.get("rows_written") or 0)
        events_found = int(result.get("events_found") or 0)
        finished_at = _now_str()
        status = "success" if rows_written > 0 else "failed"
        message = (
            f"BLS macro calendar imported {events_found} official release events from ICS."
            if rows_written > 0
            else "BLS macro calendar ICS import wrote no rows."
        )
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            message=message,
            details=result,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            message=f"BLS macro calendar ICS import failed: {exc}",
            details={
                "years": list(years or []),
                "source_name": source_name,
            },
        )


def run_weekly_fundamental_refresh(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "annual",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "weekly_fundamental_refresh"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
            details={"steps": [], "freq": freq},
        )

    steps: list[JobResult] = []

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_start",
                "stage": "fundamentals",
                "stage_index": 1,
                "total_stages": 2,
            }
        )

    fundamentals_result = run_collect_fundamentals(parsed, freq=freq)
    steps.append(fundamentals_result)

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_complete",
                "stage": "fundamentals",
                "stage_index": 1,
                "total_stages": 2,
            }
        )
    if fundamentals_result["status"] == "failed":
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=fundamentals_result.get("rows_written") or 0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=_merge_step_failures(steps, invalid_symbols),
            message="Weekly fundamental refresh stopped because fundamentals ingestion failed.",
            details={"steps": steps, "freq": freq},
        )

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_start",
                "stage": "factors",
                "stage_index": 2,
                "total_stages": 2,
            }
        )

    factors_result = run_calculate_factors(parsed, freq=freq)
    steps.append(factors_result)

    if progress_callback is not None:
        progress_callback(
            {
                "event": "stage_complete",
                "stage": "factors",
                "stage_index": 2,
                "total_stages": 2,
            }
        )

    finished_at = _now_str()
    total_rows = sum((step.get("rows_written") or 0) for step in steps)
    status = _pipeline_status(steps)
    return _build_result(
        job_name=job_name,
        status=status,
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=perf_counter() - t0,
        rows_written=total_rows,
        symbols_requested=len(parsed),
        symbols_processed=len(parsed) if total_rows > 0 else 0,
        failed_symbols=_merge_step_failures(steps, invalid_symbols),
        message="Weekly fundamental refresh completed." if total_rows > 0 else "Weekly fundamental refresh finished with no rows written.",
        details={"steps": steps, "freq": freq},
    )


def run_extended_statement_refresh(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "annual",
    periods: int = 0,
    period: str = "annual",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "extended_statement_refresh"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
            details={"pipeline_type": "extended_statement_refresh", "freq": freq, "periods": periods, "period": period, "steps": []},
        )

    steps: list[JobResult] = []

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "collect_financial_statements", "stage_index": 1, "total_stages": 3})
    refresh_result = run_collect_financial_statements(
        parsed,
        freq=freq,
        periods=periods,
        period=period,
        progress_callback=progress_callback,
    )
    steps.append(refresh_result)
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "collect_financial_statements", "stage_index": 1, "total_stages": 3})

    if refresh_result["status"] == "failed":
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=refresh_result.get("rows_written") or 0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=_merge_step_failures(steps, invalid_symbols),
            message="Extended statement refresh stopped because raw statement collection failed.",
            details={
                "pipeline_type": "extended_statement_refresh",
                "freq": freq,
                "periods": periods,
                "period": period,
                "steps": steps,
            },
        )

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "statement_fundamentals_shadow", "stage_index": 2, "total_stages": 3})
    fundamentals_rows = upsert_statement_fundamentals_shadow(parsed, freq=freq)
    steps.append(
        _build_result(
            job_name="statement_fundamentals_shadow",
            status="success" if fundamentals_rows > 0 else "failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=0.0,
            rows_written=fundamentals_rows,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if fundamentals_rows > 0 else 0,
            message=(
                "Statement fundamentals shadow rebuild completed."
                if fundamentals_rows > 0
                else "Statement fundamentals shadow rebuild wrote no rows."
            ),
            details={"freq": freq},
        )
    )
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "statement_fundamentals_shadow", "stage_index": 2, "total_stages": 3})

    if fundamentals_rows == 0:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=sum((step.get("rows_written") or 0) for step in steps),
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=_merge_step_failures(steps, invalid_symbols),
            message="Extended statement refresh stopped because statement shadow rebuild wrote no rows.",
            details={
                "pipeline_type": "extended_statement_refresh",
                "freq": freq,
                "periods": periods,
                "period": period,
                "steps": steps,
            },
        )

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "statement_factors_shadow", "stage_index": 3, "total_stages": 3})
    factor_rows = upsert_statement_factors_shadow(parsed, freq=freq)
    steps.append(
        _build_result(
            job_name="statement_factors_shadow",
            status="success" if factor_rows > 0 else "failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=0.0,
            rows_written=factor_rows,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if factor_rows > 0 else 0,
            message=(
                "Statement factors shadow rebuild completed."
                if factor_rows > 0
                else "Statement factors shadow rebuild wrote no rows."
            ),
            details={"freq": freq},
        )
    )
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "statement_factors_shadow", "stage_index": 3, "total_stages": 3})

    finished_at = _now_str()
    return _build_result(
        job_name=job_name,
        status=_pipeline_status(steps),
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=perf_counter() - t0,
        rows_written=sum((step.get("rows_written") or 0) for step in steps),
        symbols_requested=len(parsed),
        symbols_processed=len(parsed) if factor_rows > 0 else 0,
        failed_symbols=_merge_step_failures(steps, invalid_symbols),
        message=(
            "Extended statement refresh completed."
            if factor_rows > 0
            else "Extended statement refresh finished with issues."
        ),
        details={
            "pipeline_type": "extended_statement_refresh",
            "freq": freq,
            "periods": periods,
            "period": period,
            "steps": steps,
        },
    )


def run_rebuild_statement_shadow(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "quarterly",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "rebuild_statement_shadow"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
            details={"pipeline_type": "statement_shadow_rebuild", "freq": freq, "steps": []},
        )

    steps: list[JobResult] = []

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "statement_fundamentals_shadow", "stage_index": 1, "total_stages": 2})
    fundamentals_rows = upsert_statement_fundamentals_shadow(parsed, freq=freq)
    steps.append(
        _build_result(
            job_name="statement_fundamentals_shadow",
            status="success" if fundamentals_rows > 0 else "failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=0.0,
            rows_written=fundamentals_rows,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if fundamentals_rows > 0 else 0,
            message=(
                "Statement fundamentals shadow rebuild completed."
                if fundamentals_rows > 0
                else "Statement fundamentals shadow rebuild wrote no rows."
            ),
            details={"freq": freq},
        )
    )
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "statement_fundamentals_shadow", "stage_index": 1, "total_stages": 2})

    if fundamentals_rows == 0:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=_merge_step_failures(steps, invalid_symbols),
            message="Statement shadow rebuild stopped because fundamentals shadow rebuild wrote no rows.",
            details={"pipeline_type": "statement_shadow_rebuild", "freq": freq, "steps": steps},
        )

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "statement_factors_shadow", "stage_index": 2, "total_stages": 2})
    factor_rows = upsert_statement_factors_shadow(parsed, freq=freq)
    steps.append(
        _build_result(
            job_name="statement_factors_shadow",
            status="success" if factor_rows > 0 else "failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=0.0,
            rows_written=factor_rows,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if factor_rows > 0 else 0,
            message=(
                "Statement factors shadow rebuild completed."
                if factor_rows > 0
                else "Statement factors shadow rebuild wrote no rows."
            ),
            details={"freq": freq},
        )
    )
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "statement_factors_shadow", "stage_index": 2, "total_stages": 2})

    finished_at = _now_str()
    return _build_result(
        job_name=job_name,
        status=_pipeline_status(steps),
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=perf_counter() - t0,
        rows_written=sum((step.get("rows_written") or 0) for step in steps),
        symbols_requested=len(parsed),
        symbols_processed=len(parsed) if factor_rows > 0 else 0,
        failed_symbols=_merge_step_failures(steps, invalid_symbols),
        message=(
            "Statement shadow rebuild completed."
            if factor_rows > 0
            else "Statement shadow rebuild finished with issues."
        ),
        details={"pipeline_type": "statement_shadow_rebuild", "freq": freq, "steps": steps},
    )


def run_metadata_refresh(
    *,
    kinds: tuple[str, ...] = ("stock", "etf"),
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    result = run_collect_asset_profiles(kinds=kinds, progress_callback=progress_callback)
    result["job_name"] = "metadata_refresh"
    if result["status"] == "success":
        result["message"] = "Metadata refresh completed."
    elif result["status"] == "partial_success":
        result["message"] = "Metadata refresh completed with partial success."
    else:
        result["message"] = "Metadata refresh failed."
    result.setdefault("details", {})
    result["details"]["pipeline_type"] = "metadata_refresh"
    return result


def run_collect_asset_profiles(
    *,
    kinds: tuple[str, ...] = ("stock", "etf"),
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_asset_profiles"
    started_at = _now_str()
    t0 = perf_counter()

    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="asset_profiles")
        failed_rows = collect_and_store_asset_profiles(kinds=kinds)
        _emit_stage_progress(progress_callback, event="stage_complete", stage="asset_profiles")
        finished_at = _now_str()
        failure_count = len(failed_rows)
        status = "partial_success" if failure_count > 0 else "success"
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=None,
            symbols_requested=None,
            symbols_processed=None,
            failed_symbols=[row["symbol"] for row in failed_rows[:20] if row.get("symbol")],
            message="Asset profile collection completed." if failure_count == 0 else "Asset profile collection completed with failures.",
            details={
                "kinds": list(kinds),
                "failure_count": failure_count,
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=None,
            symbols_processed=0,
            message=f"Asset profile collection failed: {exc}",
            details={"kinds": list(kinds)},
        )


def run_collect_etf_operability_provider(
    symbols: str | Iterable[str] | None,
    *,
    as_of_date: str | None = None,
    provider: str = "official",
    lookback_days: int = 60,
    timeframe: str = "1d",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Run the ETF operability connector and return a web-console job result."""
    job_name = "collect_etf_operability_provider"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid ETF symbols provided.",
            details={
                "provider": provider,
                "as_of_date": as_of_date,
                "lookback_days": lookback_days,
                "timeframe": timeframe,
            },
        )

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "etf_operability", "stage_index": 1, "total_stages": 1})

    try:
        summary = collect_and_store_etf_operability(
            parsed,
            as_of_date=as_of_date or None,
            provider=provider,
            lookback_days=int(lookback_days),
            timeframe=timeframe,
        )
        if progress_callback is not None:
            progress_callback({"event": "stage_complete", "stage": "etf_operability", "stage_index": 1, "total_stages": 1})
        rows_written = int(summary.get("stored") or 0)
        missing_symbols = list(summary.get("missing") or [])
        failed_symbols = _failed_item_ids(summary.get("failed") or [])
        all_failed = invalid_symbols + failed_symbols + [sym for sym in missing_symbols if sym not in failed_symbols]
        status = _status_from_provider_summary(
            rows_written=rows_written,
            failed_items=failed_symbols + invalid_symbols,
            missing_items=missing_symbols,
        )
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=len(parsed),
            symbols_processed=max(len(parsed) - len(set(missing_symbols + failed_symbols)), 0) if rows_written > 0 else 0,
            failed_symbols=all_failed[:50],
            message=(
                "ETF operability provider snapshot completed."
                if status == "success"
                else "ETF operability provider snapshot completed with coverage gaps."
                if status == "partial_success"
                else "ETF operability provider snapshot wrote no rows."
            ),
            details={
                "provider": summary.get("source") or provider,
                "as_of_date": as_of_date,
                "lookback_days": summary.get("lookback_days") or lookback_days,
                "timeframe": timeframe,
                "coverage": summary.get("coverage") or {},
                "missing": missing_symbols,
                "failed": summary.get("failed") or [],
                "target_table": "finance_meta.etf_operability_snapshot",
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=(invalid_symbols + parsed)[:50],
            message=f"ETF operability provider snapshot failed: {exc}",
            details={
                "provider": provider,
                "as_of_date": as_of_date,
                "lookback_days": lookback_days,
                "timeframe": timeframe,
                "target_table": "finance_meta.etf_operability_snapshot",
            },
        )


def run_discover_etf_provider_source_map(
    symbols: str | Iterable[str] | None = None,
    *,
    limit: int | None = None,
    verify: bool = True,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Discover ETF provider source endpoints from NYSE ETF/profile rows and cache them in DB."""
    job_name = "discover_etf_provider_source_map"
    started_at = _now_str()
    t0 = perf_counter()
    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="etf_provider_source_map")
        summary = discover_and_store_etf_provider_source_map(
            symbols=symbols,
            limit=limit,
            verify=bool(verify),
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="etf_provider_source_map")
        failed_items = _failed_item_ids(summary.get("failed") or [], id_keys=("symbol",))
        rows_written = int(summary.get("stored") or 0)
        verified = int(summary.get("verified") or 0)
        status = "success" if rows_written > 0 and not failed_items else "partial_success" if rows_written > 0 else "failed"
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=int(summary.get("requested") or 0),
            symbols_processed=verified,
            failed_symbols=failed_items[:50],
            message=(
                "ETF provider source map discovery completed."
                if status == "success"
                else "ETF provider source map discovery completed with gaps."
                if status == "partial_success"
                else "ETF provider source map discovery wrote no rows."
            ),
            details=summary,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=[],
            message=f"ETF provider source map discovery failed: {exc}",
            details={"limit": limit, "verify": bool(verify)},
        )


def run_collect_sec_form25_delistings(
    symbols: str | Iterable[str] | None,
    *,
    user_agent: str | None = None,
    include_archive_files: bool = True,
    max_archive_files: int = 5,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Collect SEC Form 25 delisting evidence into the lifecycle evidence table."""
    job_name = "collect_sec_form25_delistings"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided for SEC Form 25 delisting collection.",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "include_archive_files": bool(include_archive_files),
                "max_archive_files": int(max_archive_files),
            },
        )

    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="sec_form25_delistings")
        summary = collect_and_store_sec_form25_delistings(
            parsed,
            user_agent=user_agent,
            include_archive_files=bool(include_archive_files),
            max_archive_files=int(max_archive_files),
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="sec_form25_delistings")
        rows_written = int(summary.get("rows_written") or 0)
        unmapped_symbols = list(summary.get("unmapped_symbols") or [])
        symbols_without_form25 = list(summary.get("symbols_without_form25") or [])
        error_symbols = _failed_item_ids(summary.get("errors") or [], id_keys=("symbol",))
        all_failed = invalid_symbols + error_symbols + unmapped_symbols + symbols_without_form25
        if rows_written <= 0:
            status = "failed"
            message = "SEC Form 25 delisting collection wrote no lifecycle rows."
        elif error_symbols or unmapped_symbols or symbols_without_form25 or invalid_symbols:
            status = "partial_success"
            message = "SEC Form 25 delisting collection completed with coverage gaps."
        else:
            status = "success"
            message = "SEC Form 25 delisting collection completed."

        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=len(parsed),
            symbols_processed=max(len(parsed) - len(set(all_failed)), 0) if rows_written > 0 else 0,
            failed_symbols=all_failed[:50],
            message=message,
            details=summary,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=(invalid_symbols + parsed)[:50],
            message=f"SEC Form 25 delisting collection failed: {exc}",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "include_archive_files": bool(include_archive_files),
                "max_archive_files": int(max_archive_files),
            },
        )


def run_collect_symbol_directory_snapshots(
    sources: str | Iterable[str] | None = None,
    *,
    user_agent: str | None = None,
    include_test_issues: bool = False,
    snapshot_date: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Collect Nasdaq public Symbol Directory current snapshots into lifecycle evidence."""
    job_name = "collect_symbol_directory_snapshots"
    started_at = _now_str()
    t0 = perf_counter()

    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="symbol_directory_snapshots")
        summary = collect_and_store_symbol_directory_snapshots(
            sources=sources,
            user_agent=user_agent,
            include_test_issues=bool(include_test_issues),
            snapshot_date=snapshot_date,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="symbol_directory_snapshots")
        rows_written = int(summary.get("rows_written") or 0)
        errors = list(summary.get("errors") or [])
        failed_sources = _failed_item_ids(errors, id_keys=("source",))
        if rows_written <= 0:
            status = "failed"
            message = "Nasdaq Symbol Directory snapshot collection wrote no lifecycle rows."
        elif errors:
            status = "partial_success"
            message = "Nasdaq Symbol Directory snapshot collection completed with source gaps."
        else:
            status = "success"
            message = "Nasdaq Symbol Directory snapshot collection completed."

        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=int(summary.get("rows_found") or 0),
            symbols_processed=rows_written,
            failed_symbols=failed_sources[:50],
            message=message,
            details=summary,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=[],
            message=f"Nasdaq Symbol Directory snapshot collection failed: {exc}",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "sources": sources,
                "include_test_issues": bool(include_test_issues),
            },
        )


def run_collect_sec_company_ticker_crosscheck(
    symbols: str | Iterable[str] | None = None,
    *,
    user_agent: str | None = None,
    snapshot_date: str | None = None,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Collect SEC current CIK / ticker / exchange associations into lifecycle evidence."""
    job_name = "collect_sec_company_ticker_crosscheck"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if symbols is not None and not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided for SEC CIK / ticker / exchange crosscheck.",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "symbols": parsed,
            },
        )

    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="sec_company_ticker_crosscheck")
        summary = collect_and_store_sec_company_ticker_crosscheck(
            symbols=parsed,
            user_agent=user_agent,
            snapshot_date=snapshot_date,
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="sec_company_ticker_crosscheck")
        rows_written = int(summary.get("rows_written") or 0)
        missing_symbols = list(summary.get("requested_missing_symbols") or [])
        failed_symbols = invalid_symbols + missing_symbols
        if rows_written <= 0:
            status = "failed"
            message = "SEC CIK / ticker / exchange crosscheck wrote no lifecycle rows."
        elif failed_symbols:
            status = "partial_success"
            message = "SEC CIK / ticker / exchange crosscheck completed with coverage gaps."
        else:
            status = "success"
            message = "SEC CIK / ticker / exchange crosscheck completed."

        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=int(summary.get("requested") or len(parsed)),
            symbols_processed=rows_written,
            failed_symbols=failed_symbols[:50],
            message=message,
            details=summary,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=(invalid_symbols + parsed)[:50],
            message=f"SEC CIK / ticker / exchange crosscheck failed: {exc}",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "symbols": parsed,
            },
        )


def run_collect_computed_snapshot_lifecycle(
    symbols: str | Iterable[str] | None = None,
    *,
    min_observation_dates: int = 2,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Compute conservative lifecycle evidence from existing current snapshot rows."""
    job_name = "collect_computed_snapshot_lifecycle"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if symbols is not None and not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided for computed snapshot lifecycle evidence.",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "symbols": parsed,
                "min_observation_dates": int(min_observation_dates),
            },
        )

    try:
        _emit_stage_progress(progress_callback, event="stage_start", stage="computed_snapshot_lifecycle")
        summary = collect_and_store_computed_snapshot_lifecycle(
            symbols=parsed,
            min_observation_dates=int(min_observation_dates),
        )
        _emit_stage_progress(progress_callback, event="stage_complete", stage="computed_snapshot_lifecycle")
        rows_written = int(summary.get("rows_written") or 0)
        missing_symbols = list(summary.get("requested_missing_symbols") or [])
        failed_symbols = invalid_symbols + missing_symbols
        if rows_written <= 0:
            status = "failed"
            message = "Computed snapshot lifecycle wrote no lifecycle rows."
        elif failed_symbols:
            status = "partial_success"
            message = "Computed snapshot lifecycle completed with coverage gaps."
        else:
            status = "success"
            message = "Computed snapshot lifecycle completed."

        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=int(summary.get("requested") or len(parsed)),
            symbols_processed=rows_written,
            failed_symbols=failed_symbols[:50],
            message=message,
            details=summary,
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=(invalid_symbols + parsed)[:50],
            message=f"Computed snapshot lifecycle failed: {exc}",
            details={
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "symbols": parsed,
                "min_observation_dates": int(min_observation_dates),
            },
        )


def run_collect_etf_holdings_exposure(
    symbols: str | Iterable[str] | None,
    *,
    as_of_date: str | None = None,
    provider: str = "official",
    include_provider_aggregates: bool = True,
    refresh_mode: str = "canonical_refresh",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Collect ETF holdings and rebuild the matching exposure snapshot for the same symbol set."""
    job_name = "collect_etf_holdings_exposure"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid ETF symbols provided.",
            details={"steps": [], "provider": provider, "as_of_date": as_of_date},
        )

    steps: list[JobResult] = []
    try:
        if progress_callback is not None:
            progress_callback({"event": "stage_start", "stage": "etf_holdings", "stage_index": 1, "total_stages": 2})
        holdings_summary = collect_and_store_etf_holdings(
            parsed,
            as_of_date=as_of_date or None,
            provider=provider,
            refresh_mode=refresh_mode,
        )
        holdings_missing = list(holdings_summary.get("missing") or [])
        holdings_failed = _failed_item_ids(holdings_summary.get("failed") or [])
        holdings_rows = int(holdings_summary.get("stored") or 0)
        holdings_status = _status_from_provider_summary(
            rows_written=holdings_rows,
            failed_items=holdings_failed,
            missing_items=holdings_missing,
        )
        steps.append(
            _build_result(
                job_name="collect_etf_holdings",
                status=holdings_status,
                started_at=started_at,
                finished_at=_now_str(),
                duration_sec=0.0,
                rows_written=holdings_rows,
                symbols_requested=len(parsed),
                symbols_processed=max(len(parsed) - len(set(holdings_missing + holdings_failed)), 0) if holdings_rows > 0 else 0,
                failed_symbols=(holdings_failed + holdings_missing)[:50],
                message="ETF holdings snapshot step completed." if holdings_rows > 0 else "ETF holdings snapshot step wrote no rows.",
                details=holdings_summary,
            )
        )
        if progress_callback is not None:
            progress_callback({"event": "stage_complete", "stage": "etf_holdings", "stage_index": 1, "total_stages": 2})
            progress_callback({"event": "stage_start", "stage": "etf_exposure", "stage_index": 2, "total_stages": 2})

        exposure_source = provider if str(provider or "").lower() in {"ishares", "ssga", "invesco"} else None
        exposure_summary = aggregate_and_store_etf_exposures(
            parsed,
            as_of_date=as_of_date or None,
            source=exposure_source,
            latest=True,
            include_provider_aggregates=bool(include_provider_aggregates),
            refresh_mode=refresh_mode,
        )
        exposure_missing = list(exposure_summary.get("missing") or [])
        exposure_failed = _failed_item_ids(exposure_summary.get("failed") or [])
        exposure_rows = int(exposure_summary.get("stored") or 0)
        exposure_status = _status_from_provider_summary(
            rows_written=exposure_rows,
            failed_items=exposure_failed,
            missing_items=exposure_missing,
        )
        steps.append(
            _build_result(
                job_name="aggregate_etf_exposures",
                status=exposure_status,
                started_at=started_at,
                finished_at=_now_str(),
                duration_sec=0.0,
                rows_written=exposure_rows,
                symbols_requested=len(parsed),
                symbols_processed=max(len(parsed) - len(set(exposure_missing + exposure_failed)), 0) if exposure_rows > 0 else 0,
                failed_symbols=(exposure_failed + exposure_missing)[:50],
                message="ETF exposure aggregation step completed." if exposure_rows > 0 else "ETF exposure aggregation step wrote no rows.",
                details=exposure_summary,
            )
        )
        if progress_callback is not None:
            progress_callback({"event": "stage_complete", "stage": "etf_exposure", "stage_index": 2, "total_stages": 2})

        total_rows = holdings_rows + exposure_rows
        failed_symbols = _merge_step_failures(steps, invalid_symbols)
        status = _pipeline_status(steps)
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status if total_rows > 0 else "failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=total_rows,
            symbols_requested=len(parsed),
            symbols_processed=max(len(parsed) - len(set(failed_symbols)), 0) if total_rows > 0 else 0,
            failed_symbols=failed_symbols[:50],
            message=(
                "ETF holdings and exposure snapshots completed."
                if status == "success" and total_rows > 0
                else "ETF holdings and exposure snapshots completed with coverage gaps."
                if total_rows > 0
                else "ETF holdings and exposure snapshots wrote no rows."
            ),
            details={
                "steps": steps,
                "provider": provider,
                "as_of_date": as_of_date,
                "include_provider_aggregates": bool(include_provider_aggregates),
                "refresh_mode": refresh_mode,
                "target_tables": [
                    "finance_meta.etf_holdings_snapshot",
                    "finance_meta.etf_exposure_snapshot",
                ],
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=sum((step.get("rows_written") or 0) for step in steps),
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=(_merge_step_failures(steps, invalid_symbols) + parsed)[:50],
            message=f"ETF holdings / exposure collection failed: {exc}",
            details={
                "steps": steps,
                "provider": provider,
                "as_of_date": as_of_date,
                "include_provider_aggregates": bool(include_provider_aggregates),
                "refresh_mode": refresh_mode,
            },
        )


def run_collect_macro_market_context(
    series_ids: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    source_mode: str = "auto",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Run the FRED market-context connector for Practical Validation macro diagnostics."""
    job_name = "collect_macro_market_context"
    started_at = _now_str()
    t0 = perf_counter()
    effective_series = DEFAULT_MACRO_SERIES if series_ids is None or (isinstance(series_ids, str) and not series_ids.strip()) else series_ids
    parsed, invalid_symbols = split_valid_invalid_symbols(effective_series)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid macro series IDs provided.",
            details={"start": start, "end": end, "source_mode": source_mode},
        )


    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "macro_market_context", "stage_index": 1, "total_stages": 1})

    try:
        summary = collect_and_store_macro_series(
            parsed,
            start=start or None,
            end=end or None,
            provider="fred",
            source_mode=source_mode,
        )
        if progress_callback is not None:
            progress_callback({"event": "stage_complete", "stage": "macro_market_context", "stage_index": 1, "total_stages": 1})
        rows_written = int(summary.get("stored") or 0)
        missing_series = list(summary.get("missing") or [])
        failed_series = _failed_item_ids(summary.get("failed") or [], id_keys=("series_id", "symbol"))
        all_failed = invalid_symbols + failed_series + [series_id for series_id in missing_series if series_id not in failed_series]
        status = _status_from_provider_summary(
            rows_written=rows_written,
            failed_items=failed_series + invalid_symbols,
            missing_items=missing_series,
        )
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=len(parsed),
            symbols_processed=max(len(parsed) - len(set(missing_series + failed_series)), 0) if rows_written > 0 else 0,
            failed_symbols=all_failed[:50],
            message=(
                "Macro market-context snapshot completed."
                if status == "success"
                else "Macro market-context snapshot completed with coverage gaps."
                if status == "partial_success"
                else "Macro market-context snapshot wrote no rows."
            ),
            details={
                "series_ids": parsed,
                "start": summary.get("start") or start,
                "end": summary.get("end") or end,
                "source": summary.get("source") or "fred",
                "source_mode": summary.get("source_mode") or source_mode,
                "coverage": summary.get("coverage") or {},
                "missing": missing_series,
                "failed": summary.get("failed") or [],
                "target_table": "finance_meta.macro_series_observation",
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=(invalid_symbols + parsed)[:50],
            message=f"Macro market-context snapshot failed: {exc}",
            details={
                "series_ids": parsed,
                "start": start,
                "end": end,
                "source": "fred",
                "source_mode": source_mode,
                "target_table": "finance_meta.macro_series_observation",
            },
        )


def run_collect_market_sentiment(
    *,
    include_cnn: bool = True,
    include_aaii: bool = True,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    """Run CNN Fear & Greed and AAII sentiment collection for Overview market context."""
    job_name = "collect_market_sentiment"
    started_at = _now_str()
    t0 = perf_counter()

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "market_sentiment", "stage_index": 1, "total_stages": 1})

    try:
        summary = collect_and_store_market_sentiment(include_cnn=include_cnn, include_aaii=include_aaii)
        if progress_callback is not None:
            progress_callback({"event": "stage_complete", "stage": "market_sentiment", "stage_index": 1, "total_stages": 1})

        rows_written = int(summary.get("stored") or 0)
        failed_sources = _failed_item_ids(summary.get("failed") or [], id_keys=("source", "series_id", "symbol"))
        missing_sources = [str(item) for item in summary.get("missing") or []]
        all_failed = failed_sources + [source for source in missing_sources if source not in failed_sources]
        status = _status_from_provider_summary(
            rows_written=rows_written,
            failed_items=failed_sources,
            missing_items=missing_sources,
        )
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=rows_written,
            symbols_requested=int(summary.get("requested") or 0),
            symbols_processed=max(int(summary.get("requested") or 0) - len(set(missing_sources + failed_sources)), 0)
            if rows_written > 0
            else 0,
            failed_symbols=all_failed[:50],
            message=(
                "Market sentiment collection completed."
                if status == "success"
                else "Market sentiment collection completed with coverage gaps."
                if status == "partial_success"
                else "Market sentiment collection wrote no rows."
            ),
            details={
                "sources": summary.get("sources") or [],
                "source_row_counts": summary.get("source_row_counts") or {},
                "coverage": summary.get("coverage") or {},
                "failed": summary.get("failed") or [],
                "missing": missing_sources,
                "target_tables": ["finance_meta.macro_series_observation"],
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=2,
            symbols_processed=0,
            failed_symbols=["market_sentiment"],
            message=f"Market sentiment collection failed: {exc}",
            details={"include_cnn": bool(include_cnn), "include_aaii": bool(include_aaii)},
        )


def run_collect_financial_statements(
    symbols: str | Iterable[str] | None,
    *,
    freq: str = "annual",
    periods: int = 0,
    period: str = "annual",
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "collect_financial_statements"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
        )

    try:
        result = upsert_financial_statements(
            parsed,
            freq=freq,
            periods=periods,
            period=period,
            progress_callback=progress_callback,
        )
        inserted_values = int(result.get("inserted_values", 0) or 0)
        upserted_labels = int(result.get("upserted_labels", 0) or 0)
        upserted_filings = int(result.get("upserted_filings", 0) or 0)
        failed_symbols = list(result.get("failed_symbols", []) or [])
        finished_at = _now_str()
        if inserted_values > 0:
            status = "partial_success" if (failed_symbols or invalid_symbols) else "success"
            msg = "Financial statement ingestion completed." if not failed_symbols else "Financial statement ingestion completed with failures."
        else:
            status = "failed"
            msg = (
                "Financial statement ingestion finished with no rows written. "
                "Check symbol validity, EDGAR availability, or filing coverage."
            )
        if invalid_symbols:
            msg += f" Invalid symbols ignored: {', '.join(invalid_symbols[:10])}."
        return _build_result(
            job_name=job_name,
            status=status,
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=inserted_values,
            symbols_requested=len(parsed),
            symbols_processed=(len(parsed) - len(failed_symbols)) if inserted_values > 0 else 0,
            failed_symbols=(invalid_symbols + failed_symbols)[:50],
            message=msg,
            details={
                "freq": freq,
                "periods": periods,
                "period": period,
                "inserted_values": inserted_values,
                "upserted_labels": upserted_labels,
                "upserted_filings": upserted_filings,
                "failed_count": len(failed_symbols),
            },
        )
    except Exception as exc:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            message=f"Financial statement ingestion failed: {exc}",
            details={
                "freq": freq,
                "periods": periods,
                "period": period,
            },
        )


def run_strict_annual_shadow_refresh(
    symbols: str | Iterable[str] | None,
    *,
    periods: int = 12,
    progress_callback: Callable[[dict[str, Any]], None] | None = None,
) -> JobResult:
    job_name = "strict_annual_shadow_refresh"
    started_at = _now_str()
    t0 = perf_counter()
    parsed, invalid_symbols = split_valid_invalid_symbols(symbols)

    if not parsed:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=0,
            symbols_requested=0,
            symbols_processed=0,
            failed_symbols=invalid_symbols,
            message="No valid symbols provided.",
            details={"steps": [], "periods": periods},
        )

    steps: list[JobResult] = []

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "extended_statement_refresh", "stage_index": 1, "total_stages": 3})
    refresh_result = run_extended_statement_refresh(
        parsed,
        freq="annual",
        periods=periods,
        period="annual",
    )
    steps.append(refresh_result)
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "extended_statement_refresh", "stage_index": 1, "total_stages": 3})

    if refresh_result["status"] == "failed":
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=refresh_result.get("rows_written") or 0,
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=_merge_step_failures(steps, invalid_symbols),
            message="Strict annual shadow refresh stopped because statement refresh failed.",
            details={"steps": steps, "periods": periods},
        )

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "fundamentals_shadow", "stage_index": 2, "total_stages": 3})
    fundamentals_rows = upsert_statement_fundamentals_shadow(parsed, freq="annual")
    steps.append(
        _build_result(
            job_name="statement_fundamentals_shadow",
            status="success" if fundamentals_rows > 0 else "failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=0.0,
            rows_written=fundamentals_rows,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if fundamentals_rows > 0 else 0,
            message="Statement fundamentals shadow rebuild completed." if fundamentals_rows > 0 else "Statement fundamentals shadow rebuild wrote no rows.",
            details={"freq": "annual"},
        )
    )
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "fundamentals_shadow", "stage_index": 2, "total_stages": 3})

    if fundamentals_rows == 0:
        finished_at = _now_str()
        return _build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=finished_at,
            duration_sec=perf_counter() - t0,
            rows_written=sum((step.get("rows_written") or 0) for step in steps),
            symbols_requested=len(parsed),
            symbols_processed=0,
            failed_symbols=_merge_step_failures(steps, invalid_symbols),
            message="Strict annual shadow refresh stopped because fundamentals shadow rebuild wrote no rows.",
            details={"steps": steps, "periods": periods},
        )

    if progress_callback is not None:
        progress_callback({"event": "stage_start", "stage": "factors_shadow", "stage_index": 3, "total_stages": 3})
    factor_rows = upsert_statement_factors_shadow(parsed, freq="annual")
    steps.append(
        _build_result(
            job_name="statement_factors_shadow",
            status="success" if factor_rows > 0 else "failed",
            started_at=started_at,
            finished_at=_now_str(),
            duration_sec=0.0,
            rows_written=factor_rows,
            symbols_requested=len(parsed),
            symbols_processed=len(parsed) if factor_rows > 0 else 0,
            message="Statement factors shadow rebuild completed." if factor_rows > 0 else "Statement factors shadow rebuild wrote no rows.",
            details={"freq": "annual"},
        )
    )
    if progress_callback is not None:
        progress_callback({"event": "stage_complete", "stage": "factors_shadow", "stage_index": 3, "total_stages": 3})

    finished_at = _now_str()
    return _build_result(
        job_name=job_name,
        status=_pipeline_status(steps),
        started_at=started_at,
        finished_at=finished_at,
        duration_sec=perf_counter() - t0,
        rows_written=sum((step.get("rows_written") or 0) for step in steps),
        symbols_requested=len(parsed),
        symbols_processed=len(parsed) if factor_rows > 0 else 0,
        failed_symbols=_merge_step_failures(steps, invalid_symbols),
        message="Strict annual shadow refresh completed." if factor_rows > 0 else "Strict annual shadow refresh finished with issues.",
        details={"steps": steps, "periods": periods},
    )
