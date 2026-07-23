"""Materialize and read the compact Overview Futures Macro snapshot."""

from __future__ import annotations

import json
import hashlib
from datetime import date, datetime, timezone
from math import isfinite
from time import perf_counter
from typing import Any, Callable

import pandas as pd

from app.services.futures_macro_pattern_validation import (
    PATTERN_ALGORITHM_VERSION,
    build_overview_futures_macro_pattern_outlook_from_inputs,
    load_overview_futures_macro_pattern_outlook,
    prepare_overview_futures_macro_pattern_inputs,
)
from app.services.futures_macro_pattern import PATTERN_STATE_SCHEMA_VERSION
from app.services.futures_macro_thermometer import (
    _default_query,
    _latest_daily_cache_marker,
    load_overview_futures_macro_snapshot,
)
from finance.data.futures_macro_snapshot import persist_futures_macro_snapshot_bundle
from finance.data.futures_market import (
    DEFAULT_CORE_FUTURES_SYMBOLS,
    FUTURES_MACRO_HISTORY_YEARS,
)
from finance.loaders.futures_macro_snapshot import (
    load_latest_futures_macro_snapshot,
)


FUTURES_MACRO_SNAPSHOT_KEY = "overview_current"
FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION = "futures_macro_snapshot_v2"
COMPACT_MACRO_KEYS = (
    "status",
    "coverage",
    "warnings",
    "summary",
    "summary_sentences",
    "evidence",
    "evidence_groups",
    "evidence_reading",
    "weekly_context",
    "flow_context",
    "pattern",
    "cautions",
    "source_note",
    "as_of_date",
)
COMPACT_TABLE_KEYS = ("scores", "score_components", "symbols")


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        return [_json_safe(row) for row in value.to_dict(orient="records")]
    if isinstance(value, dict):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, (pd.Timestamp, datetime)):
        return value.isoformat(sep=" ")
    if isinstance(value, date):
        return value.isoformat()
    if hasattr(value, "item") and callable(value.item):
        try:
            return _json_safe(value.item())
        except (TypeError, ValueError):
            pass
    if isinstance(value, float):
        return value if isfinite(value) else None
    if value is None or isinstance(value, (str, int, bool)):
        return value
    try:
        return None if bool(pd.isna(value)) else value
    except (TypeError, ValueError):
        return str(value)


def _canonical_fingerprint_value(value: Any) -> Any:
    safe = _json_safe(value)
    if isinstance(safe, dict):
        return {
            str(key): _canonical_fingerprint_value(item)
            for key, item in sorted(safe.items(), key=lambda pair: str(pair[0]))
        }
    if isinstance(safe, list):
        normalized = [_canonical_fingerprint_value(item) for item in safe]
        return sorted(
            normalized,
            key=lambda item: json.dumps(
                item,
                ensure_ascii=False,
                sort_keys=True,
                separators=(",", ":"),
            ),
        )
    return safe


def compute_futures_macro_input_fingerprint(evidence: dict[str, Any]) -> str:
    """Hash canonical final-input evidence without run timestamps or row ordering."""

    canonical = _canonical_fingerprint_value(evidence)
    encoded = json.dumps(
        canonical,
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        allow_nan=False,
    ).encode("utf-8")
    return hashlib.sha256(encoded).hexdigest()


def build_futures_macro_forecast_identity(
    *,
    as_of_date: object,
    input_fingerprint: str,
) -> str:
    identity = "|".join(
        (
            str(as_of_date),
            str(input_fingerprint),
            FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION,
            PATTERN_ALGORITHM_VERSION,
        )
    )
    return hashlib.sha256(identity.encode("utf-8")).hexdigest()


def build_compact_futures_macro_payload(
    macro: dict[str, Any],
    pattern_outlook: dict[str, Any],
    *,
    source_marker: str,
    materialized_at: str,
    input_fingerprint: str | None = None,
) -> dict[str, Any]:
    """Drop calculation frames and retain only UI-facing compact evidence."""

    compact_macro = {
        key: _json_safe(macro.get(key))
        for key in COMPACT_MACRO_KEYS
        if key in macro
    }
    compact_macro.update(
        {
            key: _json_safe(macro.get(key))
            for key in COMPACT_TABLE_KEYS
            if key in macro
        }
    )
    payload = {
        "schema_version": FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION,
        "algorithm_version": PATTERN_ALGORITHM_VERSION,
        "source_marker": str(source_marker),
        "input_fingerprint": str(
            input_fingerprint or pattern_outlook.get("input_fingerprint") or ""
        ),
        "materialized_at": str(materialized_at),
        "macro": compact_macro,
        "pattern_outlook": _json_safe(pattern_outlook),
    }
    json.dumps(payload, ensure_ascii=False, sort_keys=True, allow_nan=False)
    return payload


def _compatible_row(
    row: dict[str, Any] | None,
    *,
    input_fingerprint: str | None = None,
) -> bool:
    if not isinstance(row, dict):
        return False
    if str(row.get("schema_version") or "") != FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION:
        return False
    if str(row.get("algorithm_version") or "") != PATTERN_ALGORITHM_VERSION:
        return False
    return input_fingerprint is None or str(row.get("input_fingerprint") or "") == str(
        input_fingerprint
    )


def _stored_session_evidence_matches(
    row: dict[str, Any] | None,
    session: dict[str, Any],
) -> bool:
    """Check whether latest-good current already discloses this pending session."""

    if not isinstance(row, dict):
        return False
    try:
        payload = json.loads(str(row.get("snapshot_json") or ""))
        stored = dict(dict(payload.get("pattern_outlook") or {}).get("session") or {})
    except (TypeError, ValueError, json.JSONDecodeError):
        return False
    return all(
        str(stored.get(key) or "") == str(session.get(key) or "")
        for key in ("status", "latest_final_session", "pending_session")
    )


def _current_source_marker() -> str | None:
    return _latest_daily_cache_marker(_default_query, DEFAULT_CORE_FUTURES_SYMBOLS)


def _forecast_history_row(
    pattern_outlook: dict[str, Any],
    *,
    as_of_date: object,
    source_marker: str,
    input_fingerprint: str,
    materialized_at: str,
) -> dict[str, object]:
    return {
        "forecast_identity": build_futures_macro_forecast_identity(
            as_of_date=as_of_date,
            input_fingerprint=input_fingerprint,
        ),
        "as_of_date": as_of_date,
        "source_marker": source_marker,
        "input_fingerprint": input_fingerprint,
        "schema_version": FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION,
        "feature_schema_version": PATTERN_STATE_SCHEMA_VERSION,
        "algorithm_version": PATTERN_ALGORITHM_VERSION,
        "selected_models_json": json.dumps(
            dict(pattern_outlook.get("method") or {}).get("selected_candidates") or {},
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        "status_json": json.dumps(
            {
                str(item.get("horizon")): {
                    "probability_status": item.get("probability_status"),
                    "coordinate_status": item.get("coordinate_status"),
                    "vector_status": item.get("vector_status"),
                }
                for item in list(pattern_outlook.get("horizons") or [])
                if isinstance(item, dict)
            },
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
        ),
        "forecast_json": json.dumps(
            _json_safe(pattern_outlook),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
        "known_at": materialized_at,
        "materialized_at": materialized_at,
    }


def _refresh_pending_session_evidence(
    existing: dict[str, Any] | None,
    session: dict[str, Any],
    *,
    source_marker: str,
    input_fingerprint: str,
    materialized_at: str,
    write_fn: Callable[[dict[str, object], dict[str, object]], object],
) -> dict[str, Any] | None:
    """Patch pending-session disclosure without rerunning the nested outlook model."""

    if not isinstance(existing, dict):
        return None
    try:
        payload = json.loads(str(existing.get("snapshot_json") or ""))
    except (TypeError, ValueError, json.JSONDecodeError):
        return None
    if not isinstance(payload, dict):
        return None
    pattern_outlook = dict(payload.get("pattern_outlook") or {})
    pattern_outlook["session"] = _json_safe(session)
    pattern_outlook["input_fingerprint"] = input_fingerprint
    payload["pattern_outlook"] = pattern_outlook
    payload["source_marker"] = source_marker
    payload["input_fingerprint"] = input_fingerprint
    payload["materialized_at"] = materialized_at
    as_of_date = existing.get("as_of_date") or pattern_outlook.get("as_of_date")
    current_row: dict[str, object] = {
        "snapshot_key": FUTURES_MACRO_SNAPSHOT_KEY,
        "source_marker": source_marker,
        "as_of_date": as_of_date,
        "input_fingerprint": input_fingerprint,
        "schema_version": FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION,
        "algorithm_version": PATTERN_ALGORITHM_VERSION,
        "session_status": "FINAL",
        "status": str(existing.get("status") or pattern_outlook.get("status") or "LIMITED"),
        "snapshot_json": json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
        "materialized_at": materialized_at,
    }
    history_row = _forecast_history_row(
        pattern_outlook,
        as_of_date=as_of_date,
        source_marker=source_marker,
        input_fingerprint=input_fingerprint,
        materialized_at=materialized_at,
    )
    write_fn(current_row, history_row)
    return {
        "status": "materialized_pending_evidence",
        "source_marker": source_marker,
        "as_of_date": as_of_date,
        "pending_session": session.get("pending_session"),
        "materialized_at": materialized_at,
        "input_fingerprint": input_fingerprint,
        "forecast_identity": history_row["forecast_identity"],
    }


def materialize_overview_futures_macro_snapshot(
    *,
    force: bool = False,
    marker_fn: Callable[[], str | None] | None = None,
    load_fn: Callable[[], dict[str, Any] | None] | None = None,
    input_probe_fn: Callable[[], dict[str, Any]] | None = None,
    macro_builder: Callable[[], dict[str, Any]] | None = None,
    outlook_builder: Callable[[], dict[str, Any]] | None = None,
    write_fn: Callable[[dict[str, object], dict[str, object]], object] | None = None,
    now_fn: Callable[[], str] | None = None,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Calculate once per compatible daily marker and persist the compact result."""

    marker = (marker_fn or _current_source_marker)()
    if not marker:
        raise RuntimeError("Core futures daily source marker is unavailable.")
    read = load_fn or (
        lambda: load_latest_futures_macro_snapshot(
            snapshot_key=FUTURES_MACRO_SNAPSHOT_KEY
        )
    )
    existing = read()
    evaluated_at = evaluation_time or datetime.now(timezone.utc)
    prepared: dict[str, Any] | None = None
    input_compare_duration_sec = 0.0
    use_input_probe = input_probe_fn is not None or (
        macro_builder is None and outlook_builder is None
    )
    if use_input_probe:
        compare_started = perf_counter()
        prepared = (input_probe_fn or (
            lambda: prepare_overview_futures_macro_pattern_inputs(
                years=FUTURES_MACRO_HISTORY_YEARS,
                evaluation_time=evaluated_at,
            )
        ))()
        input_compare_duration_sec = perf_counter() - compare_started
        session = dict(prepared.get("session") or {})
        input_fingerprint = str(prepared.get("input_fingerprint") or "")
        pending_session = (
            str(session.get("status") or "")
            == "PENDING_SESSION_FINALIZATION"
        )
        compatible_input = len(input_fingerprint) == 64 and _compatible_row(
            existing,
            input_fingerprint=input_fingerprint,
        )
        if (
            pending_session
            and compatible_input
            and _stored_session_evidence_matches(existing, session)
        ):
            return {
                "status": "reused_pending",
                "source_marker": str(marker),
                "as_of_date": existing.get("as_of_date"),
                "pending_session": session.get("pending_session"),
                "materialized_at": existing.get("materialized_at"),
                "input_fingerprint": input_fingerprint,
                "input_compare_duration_sec": round(
                    input_compare_duration_sec, 6
                ),
                "materialization_duration_sec": 0.0,
            }
        if pending_session and compatible_input:
            materialized_at = (
                now_fn
                or (
                    lambda: datetime.now(timezone.utc).strftime(
                        "%Y-%m-%d %H:%M:%S"
                    )
                )
            )()
            pending_result = _refresh_pending_session_evidence(
                existing,
                session,
                source_marker=str(marker),
                input_fingerprint=input_fingerprint,
                materialized_at=materialized_at,
                write_fn=write_fn or persist_futures_macro_snapshot_bundle,
            )
            if pending_result is not None:
                pending_result["input_compare_duration_sec"] = round(
                    input_compare_duration_sec, 6
                )
                pending_result["materialization_duration_sec"] = 0.0
                return pending_result
        if not pending_session and not force and compatible_input:
            return {
                "status": "reused",
                "source_marker": str(marker),
                "as_of_date": existing.get("as_of_date"),
                "materialized_at": existing.get("materialized_at"),
                "input_fingerprint": input_fingerprint,
                "input_compare_duration_sec": round(
                    input_compare_duration_sec, 6
                ),
                "materialization_duration_sec": 0.0,
            }

    build_macro = macro_builder or (
        lambda: load_overview_futures_macro_snapshot(
            include_validation=False,
            force_refresh=True,
            cache_ttl_seconds=0,
            evaluation_time=evaluated_at,
        )
    )
    if outlook_builder is not None:
        build_outlook = outlook_builder
    elif prepared is not None:
        build_outlook = lambda: build_overview_futures_macro_pattern_outlook_from_inputs(
            prepared
        )
    else:
        build_outlook = lambda: load_overview_futures_macro_pattern_outlook(
            years=FUTURES_MACRO_HISTORY_YEARS,
            force_refresh=True,
            cache_ttl_seconds=0,
            evaluation_time=evaluated_at,
        )
    materialized_at = (
        now_fn
        or (lambda: datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"))
    )()
    materialization_started = perf_counter()
    macro = build_macro()
    pattern_outlook = build_outlook()
    session = dict(pattern_outlook.get("session") or {})
    pending_session = str(session.get("status") or "") == "PENDING_SESSION_FINALIZATION"
    input_fingerprint = str(
        (prepared or {}).get("input_fingerprint")
        or pattern_outlook.get("input_fingerprint")
        or ""
    )
    if len(input_fingerprint) != 64:
        input_fingerprint = compute_futures_macro_input_fingerprint(
            {
                "resolver_version": session.get("resolver_version"),
                "as_of_date": pattern_outlook.get("as_of_date"),
                "macro_coverage": dict(macro.get("coverage") or {}),
                "pattern_outlook": pattern_outlook,
            }
        )
    compatible_input = _compatible_row(
        existing,
        input_fingerprint=input_fingerprint,
    )
    if not use_input_probe and (
        pending_session
        and compatible_input
        and _stored_session_evidence_matches(existing, session)
    ):
        return {
            "status": "reused_pending",
            "source_marker": str(marker),
            "as_of_date": (
                existing.get("as_of_date")
                if isinstance(existing, dict)
                else session.get("latest_final_session")
            ),
            "pending_session": session.get("pending_session"),
            "materialized_at": (
                existing.get("materialized_at") if isinstance(existing, dict) else None
            ),
            "input_fingerprint": input_fingerprint,
        }
    if not use_input_probe and not pending_session and not force and compatible_input:
        return {
            "status": "reused",
            "source_marker": str(marker),
            "as_of_date": existing.get("as_of_date"),
            "materialized_at": existing.get("materialized_at"),
            "input_fingerprint": input_fingerprint,
        }
    payload = build_compact_futures_macro_payload(
        macro,
        pattern_outlook,
        source_marker=str(marker),
        materialized_at=materialized_at,
        input_fingerprint=input_fingerprint,
    )
    snapshot_status = str(pattern_outlook.get("status") or "LIMITED")
    if snapshot_status not in {"READY", "LIMITED", "ERROR"}:
        snapshot_status = "LIMITED"
    as_of_date = pattern_outlook.get("as_of_date") or dict(macro.get("coverage") or {}).get(
        "latest_daily_date"
    )
    row: dict[str, object] = {
        "snapshot_key": FUTURES_MACRO_SNAPSHOT_KEY,
        "source_marker": str(marker),
        "as_of_date": as_of_date,
        "input_fingerprint": input_fingerprint,
        "schema_version": FUTURES_MACRO_SNAPSHOT_SCHEMA_VERSION,
        "algorithm_version": PATTERN_ALGORITHM_VERSION,
        "session_status": "FINAL",
        "status": snapshot_status,
        "snapshot_json": json.dumps(
            payload,
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            allow_nan=False,
        ),
        "materialized_at": materialized_at,
    }
    history_row = _forecast_history_row(
        pattern_outlook,
        as_of_date=as_of_date,
        source_marker=str(marker),
        input_fingerprint=input_fingerprint,
        materialized_at=materialized_at,
    )
    forecast_identity = str(history_row["forecast_identity"])
    (write_fn or persist_futures_macro_snapshot_bundle)(row, history_row)
    materialization_status = "materialized"
    if pending_session:
        materialization_status = (
            "materialized_pending_evidence"
            if compatible_input
            else "materialized_pending_base"
        )
    return {
        "status": materialization_status,
        "source_marker": str(marker),
        "as_of_date": as_of_date,
        "materialized_at": materialized_at,
        "snapshot_status": snapshot_status,
        "input_fingerprint": input_fingerprint,
        "forecast_identity": forecast_identity,
        "input_compare_duration_sec": round(input_compare_duration_sec, 6),
        "materialization_duration_sec": round(
            perf_counter() - materialization_started, 6
        ),
    }


def load_overview_futures_macro_materialized_snapshot(
    *,
    load_fn: Callable[[], dict[str, Any] | None] | None = None,
) -> dict[str, Any]:
    """Read one compatible persisted snapshot without invoking calculation builders."""

    read = load_fn or (
        lambda: load_latest_futures_macro_snapshot(
            snapshot_key=FUTURES_MACRO_SNAPSHOT_KEY
        )
    )
    row = read()
    if not _compatible_row(row):
        return {
            "status": "MISSING",
            "reason": "저장된 선물 매크로 snapshot이 없거나 계산 버전이 달라 일봉 갱신이 필요합니다.",
        }
    try:
        payload = json.loads(str(row.get("snapshot_json") or ""))
    except (TypeError, ValueError, json.JSONDecodeError):
        return {
            "status": "MISSING",
            "reason": "저장된 선물 매크로 snapshot을 읽을 수 없어 일봉 갱신이 필요합니다.",
        }
    if not isinstance(payload, dict):
        return {
            "status": "MISSING",
            "reason": "저장된 선물 매크로 snapshot 형식이 올바르지 않아 일봉 갱신이 필요합니다.",
        }
    return {
        "status": "READY",
        "macro": dict(payload.get("macro") or {}),
        "pattern_outlook": dict(payload.get("pattern_outlook") or {}),
        "metadata": {
            "source_marker": str(row.get("source_marker") or payload.get("source_marker") or ""),
            "as_of_date": str(row.get("as_of_date") or ""),
            "materialized_at": str(
                row.get("materialized_at") or payload.get("materialized_at") or ""
            ),
            "snapshot_status": str(row.get("status") or ""),
            "schema_version": str(row.get("schema_version") or ""),
            "algorithm_version": str(row.get("algorithm_version") or ""),
            "input_fingerprint": str(row.get("input_fingerprint") or ""),
            "session_status": str(row.get("session_status") or ""),
        },
    }
