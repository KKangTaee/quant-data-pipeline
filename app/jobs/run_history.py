from __future__ import annotations

import json
from pathlib import Path
from typing import Any


PROJECT_ROOT = Path(__file__).resolve().parents[2]
FINANCE_NOTE_DIR = PROJECT_ROOT / ".note" / "finance"
RUN_HISTORY_DIR = FINANCE_NOTE_DIR / "run_history"
HISTORY_FILE = RUN_HISTORY_DIR / "WEB_APP_RUN_HISTORY.jsonl"
RUN_HISTORY_SCHEMA_VERSION = 2


def _infer_pipeline_type(record: dict[str, Any]) -> str | None:
    job_name = record.get("job_name")
    mapping = {
        "daily_market_update": "daily_market_update",
        "weekly_fundamental_refresh": "weekly_fundamental_refresh",
        "extended_statement_refresh": "extended_statement_refresh",
        "rebuild_statement_shadow": "statement_shadow_rebuild",
        "metadata_refresh": "metadata_refresh",
        "pipeline_core_market_data": "core_market_data_pipeline",
        "collect_ohlcv": "manual_ohlcv_collection",
        "collect_fundamentals": "manual_fundamentals_ingestion",
        "calculate_factors": "manual_factor_calculation",
        "collect_financial_statements": "manual_financial_statement_ingestion",
        "collect_asset_profiles": "manual_asset_profile_collection",
    }
    return mapping.get(job_name)


def _infer_execution_mode(record: dict[str, Any]) -> str | None:
    pipeline_type = _infer_pipeline_type(record)
    if pipeline_type in {
        "daily_market_update",
        "weekly_fundamental_refresh",
        "extended_statement_refresh",
        "metadata_refresh",
    }:
        return "operational"
    if pipeline_type is not None:
        return "manual"
    return None


def _infer_execution_context(record: dict[str, Any]) -> str | None:
    pipeline_type = _infer_pipeline_type(record)
    mapping = {
        "daily_market_update": "Routine daily price-history refresh for the selected operating universe.",
        "weekly_fundamental_refresh": "Routine weekly refresh of normalized fundamentals and derived factors.",
        "extended_statement_refresh": "Extended refresh of detailed financial statement ledgers for long-horizon analysis.",
        "metadata_refresh": "Routine metadata refresh for tracked stock and ETF asset profiles.",
        "core_market_data_pipeline": "Manual composite run of OHLCV, fundamentals, and factor calculation in sequence.",
        "manual_ohlcv_collection": "Manual OHLCV ingestion for the selected symbols or universe source.",
        "manual_fundamentals_ingestion": "Manual normalized fundamentals ingestion for the selected symbols or universe source.",
        "manual_factor_calculation": "Manual factor calculation using already stored prices and fundamentals.",
        "manual_financial_statement_ingestion": "Manual detailed financial statement ingestion for the selected symbols or universe source.",
        "statement_shadow_rebuild": "Manual rebuild of statement shadow tables using already stored raw statement ledgers.",
        "manual_asset_profile_collection": "Manual asset-profile refresh for the tracked stock and ETF universes.",
    }
    return mapping.get(pipeline_type)


def _normalize_history_record(record: dict[str, Any]) -> dict[str, Any]:
    normalized = dict(record)
    normalized.setdefault("schema_version", RUN_HISTORY_SCHEMA_VERSION)

    run_metadata = dict(normalized.get("run_metadata") or {})
    run_metadata.setdefault("pipeline_type", _infer_pipeline_type(normalized))
    run_metadata.setdefault("execution_mode", _infer_execution_mode(normalized))
    run_metadata.setdefault("symbol_source", None)
    run_metadata.setdefault("symbol_count", normalized.get("symbols_requested"))
    run_metadata.setdefault("input_params", {})
    run_metadata.setdefault("execution_context", _infer_execution_context(normalized))

    normalized["run_metadata"] = run_metadata
    return normalized


def append_run_history(result: dict[str, Any]) -> None:
    record = _normalize_history_record(result)
    HISTORY_FILE.parent.mkdir(parents=True, exist_ok=True)
    with HISTORY_FILE.open("a", encoding="utf-8") as f:
        f.write(json.dumps(record, ensure_ascii=False) + "\n")


def load_run_history(limit: int = 50) -> list[dict[str, Any]]:
    if not HISTORY_FILE.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in HISTORY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            rows.append(_normalize_history_record(json.loads(line)))
        except json.JSONDecodeError:
            continue

    return rows[-limit:][::-1]


def estimate_duration_from_history(job_name: str, symbol_count: int) -> dict[str, Any]:
    history = load_run_history(limit=200)
    relevant = [
        item for item in history
        if item.get("job_name") == job_name
        and (item.get("symbols_requested") or 0) > 0
        and (item.get("duration_sec") or 0) > 0
    ]

    if not relevant or symbol_count <= 0:
        return {
            "available": False,
            "message": "No estimate available yet.",
        }

    per_symbol = [
        float(item["duration_sec"]) / float(item["symbols_requested"])
        for item in relevant
        if item.get("symbols_requested")
    ]
    if not per_symbol:
        return {
            "available": False,
            "message": "No estimate available yet.",
        }

    avg = sum(per_symbol) / len(per_symbol)
    estimate_sec = avg * symbol_count
    low = max(1, int(estimate_sec * 0.7))
    high = max(low, int(estimate_sec * 1.3))

    return {
        "available": True,
        "seconds_low": low,
        "seconds_high": high,
        "message": f"Estimated runtime: {low // 60}m {low % 60}s - {high // 60}m {high % 60}s",
    }
