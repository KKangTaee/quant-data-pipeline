"""Shared helpers for ingestion job wrappers."""

from __future__ import annotations

import re
from datetime import datetime
from typing import Any, Callable, Iterable

JobResult = dict[str, Any]
SYMBOL_PATTERN = re.compile(r"^[A-Z0-9.\-_=^]+$")
OHLCV_EXECUTION_PROFILES: dict[str, dict[str, Any]] = {
    "managed_refresh_short": {
        "chunk_size": 70,
        "sleep": 0.01,
        "max_workers": 2,
        "max_retry": 2,
        "retry_backoff": 1.0,
        "sleep_jitter_ratio": 0.15,
        "rate_limit_cooldown_sec": 10.0,
        "rate_limit_circuit_break_threshold": 1,
        "cooldown_chunk_size": 40,
        "degrade_to_single_worker_on_rate_limit": True,
    },
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


def build_result(
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


def _emit_stage_progress(
    progress_callback: Callable[[dict[str, Any]], None] | None,
    *,
    event: str,
    stage: str,
    stage_index: int = 1,
    total_stages: int = 1,
) -> None:
    if progress_callback is None:
        return
    progress_callback(
        {
            "event": event,
            "stage": stage,
            "stage_index": stage_index,
            "total_stages": total_stages,
        }
    )


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


def _failed_item_ids(failed_items: Iterable[Any], *, id_keys: tuple[str, ...] = ("symbol", "series_id")) -> list[str]:
    ids: list[str] = []
    for item in failed_items or []:
        if isinstance(item, dict):
            for key in id_keys:
                value = item.get(key)
                if value:
                    ids.append(str(value).upper())
                    break
        elif item:
            ids.append(str(item).upper())
    return ids


def _status_from_provider_summary(
    *,
    rows_written: int,
    failed_items: list[str],
    missing_items: list[str],
) -> str:
    if rows_written <= 0:
        return "failed"
    if failed_items or missing_items:
        return "partial_success"
    return "success"


def _pipeline_status(steps: list[JobResult]) -> str:
    statuses = [step["status"] for step in steps]
    if any(status == "failed" for status in statuses):
        return "failed"
    if any(status == "partial_success" for status in statuses):
        return "partial_success"
    return "success"


_build_result = build_result
