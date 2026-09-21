"""Persist current daily observations without running forecast research."""

from __future__ import annotations

import json
from datetime import datetime, timezone
from time import perf_counter
from typing import Any, Callable

from app.services.futures_macro_daily_loader import load_futures_macro_daily_rows
from app.services.futures_macro_sessions import select_completed_futures_daily_rows
from app.services.futures_macro_snapshot import (
    COMPACT_MACRO_KEYS, COMPACT_TABLE_KEYS, _json_safe,
    compute_futures_macro_input_fingerprint,
)
from app.services.futures_macro_thermometer import (
    _default_query, _instrument_rows, build_macro_thermometer_read_model,
    normalize_futures_macro_daily_candles,
)
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS
from finance.data.futures_macro_snapshot import upsert_futures_macro_snapshot
from finance.loaders.futures_macro_snapshot import load_latest_futures_macro_snapshot

OBSERVATION_KEY = "overview_futures_macro_observation_v1"
OBSERVATION_SCHEMA = "futures_macro_observation_v1"
OBSERVATION_ALGORITHM = "daily_current_no_research_v1"


def observation_row_compatible(row: dict | None) -> bool:
    return bool(row and row.get("schema_version") == OBSERVATION_SCHEMA
                and row.get("algorithm_version") == OBSERVATION_ALGORITHM)


def build_observation_payload(*, macro: dict, current_pattern: dict,
                              as_of_date: str, materialized_at: str) -> dict:
    """Keep consumer-facing current fields and explicitly omit uncomputed forecasts."""
    compact = {key: _json_safe(macro[key]) for key in (*COMPACT_MACRO_KEYS, *COMPACT_TABLE_KEYS) if key in macro}
    compact["as_of_date"] = as_of_date
    return {
        "schema_version": OBSERVATION_SCHEMA,
        "algorithm_version": OBSERVATION_ALGORITHM,
        "macro": compact,
        "pattern_outlook": {
            "status": current_pattern.get("status", "UNAVAILABLE"),
            "as_of_date": as_of_date,
            "current_pattern": _json_safe(current_pattern),
            "session": dict(macro.get("session") or {}),
            "horizons": [], "research_status": "NOT_COMPUTED",
        },
        "as_of_date": as_of_date, "materialized_at": materialized_at,
    }


def materialize_futures_macro_observation_snapshot(
    *, evaluation_time: datetime | None = None, force: bool = False,
    query_fn: Callable | None = None, load_fn: Callable | None = None,
    write_fn: Callable | None = None,
) -> dict[str, Any]:
    """Reuse bounded daily inputs and advance only the separate current snapshot."""
    started = perf_counter()
    evaluated = evaluation_time or datetime.now(timezone.utc)
    if evaluated.tzinfo is None:
        evaluated = evaluated.replace(tzinfo=timezone.utc)
    query = query_fn or _default_query
    rows = load_futures_macro_daily_rows(query, symbols=DEFAULT_CORE_FUTURES_SYMBOLS, lookback_days=420)
    completed = select_completed_futures_daily_rows(rows, evaluation_time=evaluated)
    if not completed.rows or not completed.latest_final_session:
        return {"status": "unavailable", "reason": "no_completed_daily_rows"}
    as_of = str(completed.latest_final_session)
    materialized_at = evaluated.astimezone(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    existing = (load_fn or (lambda: load_latest_futures_macro_snapshot(snapshot_key=OBSERVATION_KEY)))()
    if existing and (str(existing.get("as_of_date") or ""), str(existing.get("materialized_at") or "")) > (as_of, materialized_at):
        return {"status": "kept_newer", "as_of_date": str(existing.get("as_of_date"))}
    # Collection timestamps alone do not change an observation; corrected prices do.
    fields = ("provider_symbol", "candle_time_utc", "open", "high", "low", "close", "adj_close", "volume", "source")
    fingerprint = compute_futures_macro_input_fingerprint({
        "algorithm": OBSERVATION_ALGORITHM,
        "rows": [{key: row.get(key) for key in fields} for row in completed.rows],
        "pending_session": completed.pending_session,
    })
    if not force and observation_row_compatible(existing) and existing.get("input_fingerprint") == fingerprint:
        return {"status": "reused", "as_of_date": as_of, "input_fingerprint": fingerprint,
                "materialization_duration_sec": round(perf_counter() - started, 6)}
    candles = normalize_futures_macro_daily_candles(completed.rows)
    macro = build_macro_thermometer_read_model(
        candles=candles, instruments=_instrument_rows(query),
        selected_symbols=DEFAULT_CORE_FUTURES_SYMBOLS, daily_rows=completed.rows, as_of_date=as_of,
    )
    macro["session"] = {"status": "PENDING_SESSION_FINALIZATION" if completed.pending_session else "OBSERVED",
                        "latest_final_session": as_of, "pending_session": completed.pending_session}
    pattern = dict(macro.get("pattern") or {})
    payload = build_observation_payload(macro=macro, current_pattern=pattern, as_of_date=as_of,
                                        materialized_at=materialized_at)
    row = {"snapshot_key": OBSERVATION_KEY, "source_marker": as_of, "as_of_date": as_of,
           "input_fingerprint": fingerprint, "schema_version": OBSERVATION_SCHEMA,
           "algorithm_version": OBSERVATION_ALGORITHM, "session_status": "FINAL",
           "status": "READY" if macro.get("status") == "OK" else "LIMITED",
           "snapshot_json": json.dumps(payload, ensure_ascii=False, allow_nan=False),
           "materialized_at": materialized_at}
    (write_fn or (lambda value: upsert_futures_macro_snapshot(value, monotonic=True)))(row)
    return {"status": "materialized", "as_of_date": as_of, "input_fingerprint": fingerprint,
            "materialization_duration_sec": round(perf_counter() - started, 6)}
