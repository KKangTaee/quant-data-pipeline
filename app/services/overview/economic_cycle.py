"""Compact DB-only read model for the Overview economic-cycle surface."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping, Sequence
from datetime import date
from typing import Any

import pandas as pd

from finance.economic_cycle_interpretation import (
    build_market_implications,
    evidence_direction,
    evidence_group,
    translate_reason_code,
)
from finance.economic_cycle_model import PHASES
from finance.loaders.economic_cycle import load_cycle_history, load_cycle_snapshot
from finance.loaders.economic_cycle_assets import load_economic_cycle_asset_prices

SCHEMA_VERSION = "economic_cycle_v1"
HORIZON_LABELS = {0: "현재", 1: "1개월 후", 2: "2개월 후"}
PHASE_LABELS = {
    "recovery": "회복",
    "expansion": "확장",
    "slowdown": "둔화",
    "recession": "침체",
}
ESTIMATE_LABELS = {
    "VERIFIED": "검증된 모델 추정",
    "PROVISIONAL": "잠정 모델 추정",
    "UNAVAILABLE": "판단 불가",
}


def _json_value(value: object, fallback: object) -> object:
    if value is None:
        return fallback
    if isinstance(value, (dict, list, tuple)):
        return value
    try:
        return json.loads(str(value))
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def _probabilities(value: object) -> dict[str, float] | None:
    raw = _json_value(value, {})
    if not isinstance(raw, Mapping) or set(raw) != set(PHASES):
        return None
    try:
        values = {phase: float(raw[phase]) for phase in PHASES}
    except (TypeError, ValueError):
        return None
    if any(not math.isfinite(item) or item < 0 for item in values.values()):
        return None
    total = sum(values.values())
    if total <= 0 or not math.isclose(total, 1.0, abs_tol=1e-6):
        return None
    return values


def _empty_model(
    *,
    status: str,
    reason_code: str,
    as_of_date: object = None,
) -> dict[str, object]:
    reason = translate_reason_code(reason_code)
    economic_as_of_date = str(as_of_date or "") or None
    horizons = [
        {
            "horizon_months": horizon,
            "label": HORIZON_LABELS[horizon],
            "probabilities": None,
            "dominant_phase": None,
            "confidence": None,
            "publication_status": "LIMITED",
            "estimate_status": "UNAVAILABLE",
            "estimate_label": ESTIMATE_LABELS["UNAVAILABLE"],
            "reason_code": reason_code,
            "reason": reason,
        }
        for horizon in (0, 1, 2)
    ]
    market_implications = build_market_implications(horizons, [])
    for item in market_implications:
        item["economic_as_of_date"] = economic_as_of_date
    return {
        "schema_version": SCHEMA_VERSION,
        "status": status,
        "as_of_date": str(as_of_date or "") or None,
        "model_version": None,
        "headline": {
            "phase": None,
            "phase_label": "판단 제한",
            "summary": reason,
            "reason_code": reason_code,
        },
        "horizons": horizons,
        "cycle_clock": {
            "phase_order": list(PHASES),
            "recent_path": [],
            "forecast_markers": [],
            "expected_transition": None,
        },
        "evidence": [],
        "market_implications": market_implications,
        "history": [],
        "sources": [],
        "limitations": [reason, "NBER 공식 판정이나 투자 지시가 아닙니다."],
    }


def _horizons(snapshot: Mapping[str, object]) -> list[dict[str, object]]:
    raw_path = _json_value(snapshot.get("forecast_path_json"), [])
    indexed = {
        int(item.get("horizon_months") or 0): dict(item)
        for item in raw_path
        if isinstance(item, Mapping)
    }
    output: list[dict[str, object]] = []
    for horizon in (0, 1, 2):
        raw = indexed.get(horizon, {})
        status = str(raw.get("publication_status") or "LIMITED").upper()
        reason_code = str(raw.get("reason") or "VALIDATION_FAILED").upper()
        probabilities = _probabilities(raw.get("probabilities"))
        status = "READY" if status == "READY" and probabilities is not None else "LIMITED"
        dominant = str(raw.get("dominant_phase") or "")
        if probabilities is not None and dominant not in PHASES:
            dominant = max(PHASES, key=probabilities.__getitem__)
        if probabilities is None:
            dominant = None
        confidence = probabilities.get(dominant) if probabilities and dominant else None
        estimate_status = (
            "VERIFIED"
            if status == "READY"
            else "PROVISIONAL"
            if probabilities is not None
            else "UNAVAILABLE"
        )
        output.append(
            {
                "horizon_months": horizon,
                "label": HORIZON_LABELS[horizon],
                "probabilities": probabilities,
                "dominant_phase": dominant,
                "dominant_phase_label": PHASE_LABELS.get(dominant),
                "confidence": confidence,
                "publication_status": status,
                "estimate_status": estimate_status,
                "estimate_label": ESTIMATE_LABELS[estimate_status],
                "reason_code": reason_code if status == "LIMITED" else None,
                "reason": (
                    translate_reason_code(reason_code) if status == "LIMITED" else None
                ),
            }
        )
    return output


def _history(rows: Sequence[Mapping[str, object]]) -> list[dict[str, object]]:
    normalized: list[dict[str, object]] = []
    for raw in rows:
        phase = str(raw.get("current_phase") or "")
        status = str(raw.get("status") or "LIMITED").upper()
        probabilities = _probabilities(raw.get("probabilities_json"))
        if probabilities is not None and phase not in PHASES:
            phase = max(PHASES, key=probabilities.__getitem__)
        estimate_status = (
            "VERIFIED"
            if status == "READY" and probabilities is not None
            else "PROVISIONAL"
            if probabilities is not None
            else "UNAVAILABLE"
        )
        normalized.append(
            {
                "date": str(raw.get("as_of_date") or "")[:10],
                "phase": phase if phase in PHASES else None,
                "probabilities": probabilities,
                "status": "READY" if status == "READY" else "LIMITED",
                "estimate_status": estimate_status,
                "nber_recession": bool(raw.get("nber_recession")),
            }
        )
    ordered = sorted(normalized, key=lambda item: item["date"])
    return ordered[-60:]


def _evidence(snapshot: Mapping[str, object]) -> list[dict[str, object]]:
    raw_rows = _json_value(snapshot.get("top_evidence_json"), [])
    rows = [dict(item) for item in raw_rows if isinstance(item, Mapping)]
    normalized = []
    for item in rows:
        factor = str(item.get("factor") or item.get("series_id") or "unknown")
        normalized.append(
            {
                "factor": factor,
                "series_id": str(item.get("series_id") or "") or None,
                "group": evidence_group(factor),
                "direction": evidence_direction(item.get("value")),
                "value": (
                    float(item["value"])
                    if isinstance(item.get("value"), (int, float))
                    else None
                ),
                "source_date": str(
                    item.get("source_date")
                    or snapshot.get("data_cutoff_date")
                    or snapshot.get("as_of_date")
                    or ""
                )[:10]
                or None,
                "source_basis": "FRED/ALFRED point-in-time",
            }
        )
    normalized.sort(key=lambda item: 0 if item["group"] == "real_economy" else 1)
    return normalized[:10]


def _sources(
    snapshot: Mapping[str, object], evidence: Sequence[Mapping[str, object]]
) -> list[dict[str, object]]:
    dates = list(
        dict.fromkeys(
            str(item.get("source_date") or "")
            for item in evidence
            if item.get("source_date")
        )
    )
    if not dates:
        dates = [
            str(snapshot.get("data_cutoff_date") or snapshot.get("as_of_date") or "")[
                :10
            ]
        ]
    return [
        {
            "name": "FRED/ALFRED 빈티지",
            "source_date": source_date,
            "basis": "forecast-origin eligible observations",
        }
        for source_date in dates
        if source_date
    ]


def build_economic_cycle_read_model(
    *,
    as_of_date: str | date | None = None,
    snapshot_loader: Callable[..., Mapping[str, object] | None] | None = None,
    history_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None,
    asset_price_loader: Callable[[], Sequence[Mapping[str, object]]] | None = None,
    price_reference_date: str | date | None = None,
) -> dict[str, object]:
    """Adapt persisted compact rows; never fetch, fit, write, or mutate UI state."""

    load_snapshot = snapshot_loader or load_cycle_snapshot
    load_history = history_loader or load_cycle_history
    try:
        snapshot = load_snapshot(as_of_date=as_of_date)
    except Exception:
        return _empty_model(
            status="ERROR", reason_code="READ_ERROR", as_of_date=as_of_date
        )
    if not snapshot:
        return _empty_model(
            status="LIMITED",
            reason_code="NOT_MATERIALIZED",
            as_of_date=as_of_date,
        )

    resolved_snapshot = dict(snapshot)
    snapshot_date = str(resolved_snapshot.get("as_of_date") or as_of_date or "")[:10]
    try:
        end = pd.Timestamp(snapshot_date).date()
        start = (pd.Timestamp(end) - pd.DateOffset(months=59)).date()
        history_rows = load_history(start_date=start, end_date=end)
    except Exception:
        return _empty_model(
            status="ERROR", reason_code="READ_ERROR", as_of_date=snapshot_date
        )

    horizons = _horizons(resolved_snapshot)
    history = _history(history_rows)
    evidence = _evidence(resolved_snapshot)
    load_asset_prices = asset_price_loader or load_economic_cycle_asset_prices
    try:
        asset_price_rows = list(load_asset_prices())
    except Exception:
        asset_price_rows = []
    market_implications = build_market_implications(
        horizons,
        evidence,
        asset_price_rows,
        price_reference_date=price_reference_date,
    )
    for item in market_implications:
        item["economic_as_of_date"] = snapshot_date or None
    current = horizons[0]
    current_phase = current.get("dominant_phase")
    status = str(resolved_snapshot.get("status") or "LIMITED").upper()
    if current.get("publication_status") != "READY":
        status = "LIMITED"
    limitations = [
        "이 결과는 데이터 기반 국면 추정이며 NBER의 공식 경기판정이 아닙니다.",
        "시장 맥락은 조건부 해석이며 수익률 예측이나 매매 지시가 아닙니다.",
    ]
    warnings = _json_value(resolved_snapshot.get("warnings_json"), [])
    limitations.extend(str(item) for item in warnings if item)
    forecast_markers = [
        {
            "horizon_months": item["horizon_months"],
            "phase": item["dominant_phase"],
            "status": item["publication_status"],
            "estimate_status": item["estimate_status"],
        }
        for item in horizons[1:]
    ]
    headline_summary = (
        f"현재는 {PHASE_LABELS.get(str(current_phase), '판단 제한')} 국면 가능성이 가장 높습니다."
        if current_phase
        else str(current.get("reason") or "현재 국면 판단이 제한적입니다.")
    )
    return {
        "schema_version": SCHEMA_VERSION,
        "status": "READY" if status == "READY" else "LIMITED",
        "as_of_date": snapshot_date or None,
        "model_version": str(resolved_snapshot.get("model_version") or "") or None,
        "headline": {
            "phase": current_phase,
            "phase_label": PHASE_LABELS.get(str(current_phase), "판단 제한"),
            "summary": headline_summary,
            "reason_code": current.get("reason_code"),
        },
        "horizons": horizons,
        "cycle_clock": {
            "phase_order": list(PHASES),
            "recent_path": [
                {"date": item["date"], "phase": item["phase"], "status": item["status"]}
                for item in history[-12:]
            ],
            "forecast_markers": forecast_markers,
            "expected_transition": resolved_snapshot.get("expected_transition"),
        },
        "evidence": evidence,
        "market_implications": market_implications,
        "history": history,
        "sources": _sources(resolved_snapshot, evidence),
        "limitations": limitations,
    }
