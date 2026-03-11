from __future__ import annotations

import re
from datetime import datetime
from time import perf_counter
from typing import Any, Callable, Iterable

from finance.data.data import store_ohlcv_to_mysql
from finance.data.factors import upsert_factors
from finance.data.financial_statements import upsert_financial_statements
from finance.data.fundamentals import upsert_fundamentals
from finance.data.asset_profile import collect_and_store_asset_profiles


JobResult = dict[str, Any]
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-_=^]+$")


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


def run_collect_ohlcv(
    symbols: str | Iterable[str] | None,
    *,
    start: str | None = None,
    end: str | None = None,
    period: str = "1y",
    interval: str = "1d",
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

    try:
        rows_written = store_ohlcv_to_mysql(
            parsed,
            start=start,
            end=end,
            period=period,
            interval=interval,
            progress_callback=progress_callback,
        )
        finished_at = _now_str()
        if rows_written > 0:
            status = "success" if not invalid_symbols else "partial_success"
            msg = "OHLCV collection completed."
        else:
            status = "failed"
            msg = (
                "OHLCV collection finished with no rows written. "
                "The symbols may be invalid, delisted, or unavailable from the provider."
            )
        if end is not None:
            msg += " Note: current low-level date-range handling may be start-oriented."
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
            details={
                "start": start,
                "end": end,
                "period": period,
                "interval": interval,
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
    periods: int = 4,
    period: str = "annual",
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
        )
        inserted_values = int(result.get("inserted_values", 0) or 0)
        upserted_labels = int(result.get("upserted_labels", 0) or 0)
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
