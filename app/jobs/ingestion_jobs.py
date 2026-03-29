from __future__ import annotations

import re
from datetime import datetime
from time import perf_counter
from typing import Any, Callable, Iterable

from finance.data.data import store_ohlcv_to_mysql
from finance.data.factors import upsert_factors, upsert_statement_factors_shadow
from finance.data.financial_statements import upsert_financial_statements
from finance.data.fundamentals import upsert_fundamentals, upsert_statement_fundamentals_shadow
from finance.data.asset_profile import collect_and_store_asset_profiles


JobResult = dict[str, Any]
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-_=^]+$")
OHLCV_EXECUTION_PROFILES: dict[str, dict[str, Any]] = {
    "managed_fast": {
        "chunk_size": 60,
        "sleep": 0.05,
        "max_workers": 1,
        "max_retry": 2,
        "retry_backoff": 1.0,
        "sleep_jitter_ratio": 0.2,
        "rate_limit_cooldown_sec": 12.0,
        "rate_limit_circuit_break_threshold": 1,
        "cooldown_chunk_size": 30,
        "degrade_to_single_worker_on_rate_limit": True,
    },
    "managed_safe": {
        "chunk_size": 40,
        "sleep": 0.15,
        "max_workers": 1,
        "max_retry": 3,
        "retry_backoff": 1.5,
        "sleep_jitter_ratio": 0.3,
        "rate_limit_cooldown_sec": 20.0,
        "rate_limit_circuit_break_threshold": 1,
        "cooldown_chunk_size": 20,
        "degrade_to_single_worker_on_rate_limit": True,
    },
    "raw_heavy": {
        "chunk_size": 25,
        "sleep": 0.35,
        "max_workers": 1,
        "max_retry": 4,
        "retry_backoff": 2.5,
        "sleep_jitter_ratio": 0.35,
        "rate_limit_cooldown_sec": 30.0,
        "rate_limit_circuit_break_threshold": 1,
        "cooldown_chunk_size": 10,
        "degrade_to_single_worker_on_rate_limit": True,
    },
}


def _now_str() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def parse_symbols(symbols: str | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []

    if isinstance(symbols, str):
        raw = symbols.replace("\n", ",").split(",")
    else:
        raw = list(symbols)

    out: list[str] = []
    seen: set[str] = set()

    for item in raw:
        sym = str(item).strip().upper()
        if not sym or sym in seen:
            continue
        seen.add(sym)
        out.append(sym)

    return out


def split_valid_invalid_symbols(symbols: str | Iterable[str] | None) -> tuple[list[str], list[str]]:
    parsed = parse_symbols(symbols)
    valid: list[str] = []
    invalid: list[str] = []

    for sym in parsed:
        if SYMBOL_PATTERN.fullmatch(sym):
            valid.append(sym)
        else:
            invalid.append(sym)

    return valid, invalid


def _build_result(
    *,
    job_name: str,
    status: str,
    started_at: str,
    finished_at: str,
    duration_sec: float,
    rows_written: int | None = None,
    symbols_requested: int | None = None,
    symbols_processed: int | None = None,
    failed_symbols: list[str] | None = None,
    message: str = "",
    details: dict[str, Any] | None = None,
) -> JobResult:
    return {
        "job_name": job_name,
        "status": status,
        "started_at": started_at,
        "finished_at": finished_at,
        "duration_sec": round(duration_sec, 3),
        "rows_written": rows_written,
        "symbols_requested": symbols_requested,
        "symbols_processed": symbols_processed,
        "failed_symbols": failed_symbols or [],
        "message": message,
        "details": details or {},
    }


def _resolve_ohlcv_execution_profile(execution_profile: str) -> tuple[str, dict[str, Any]]:
    normalized = str(execution_profile or "managed_safe").strip().lower()
    if normalized not in OHLCV_EXECUTION_PROFILES:
        normalized = "managed_safe"
    return normalized, dict(OHLCV_EXECUTION_PROFILES[normalized])


def _merge_step_failures(steps: list[JobResult], invalid_symbols: list[str] | None = None) -> list[str]:
    failures: list[str] = list(invalid_symbols or [])
    for step in steps:
        failures.extend(step.get("failed_symbols") or [])
    return failures


def _pipeline_status(steps: list[JobResult]) -> str:
    statuses = [step["status"] for step in steps]
    if any(status == "failed" for status in statuses):
        return "failed"
    if any(status == "partial_success" for status in statuses):
        return "partial_success"
    return "success"


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
) -> JobResult:
    result = run_collect_asset_profiles(kinds=kinds)
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
) -> JobResult:
    job_name = "collect_asset_profiles"
    started_at = _now_str()
    t0 = perf_counter()

    try:
        failed_rows = collect_and_store_asset_profiles(kinds=kinds)
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
