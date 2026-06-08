from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.backtest_data_coverage_audit import build_data_coverage_audit


DATA_PROVENANCE_SCHEMA_VERSION = "data_provenance_contract_v1"

DATA_PROVENANCE_READY = "DATA_PROVENANCE_READY"
DATA_PROVENANCE_REVIEW = "DATA_PROVENANCE_REVIEW"
DATA_PROVENANCE_NEEDS_INPUT = "DATA_PROVENANCE_NEEDS_INPUT"
DATA_PROVENANCE_BLOCKED = "DATA_PROVENANCE_BLOCKED"

DATA_PROVENANCE_ROUTE_LABELS = {
    DATA_PROVENANCE_READY: "Ready",
    DATA_PROVENANCE_REVIEW: "Review Required",
    DATA_PROVENANCE_NEEDS_INPUT: "Evidence Input Needed",
    DATA_PROVENANCE_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}

_PROVIDER_AREA_LABELS = {
    "operability": "ETF Operability",
    "holdings": "ETF Holdings",
    "exposure": "ETF Exposure",
    "macro": "Macro Context",
}

_PROVIDER_STORAGE = {
    "operability": "MySQL finance_meta.etf_operability_snapshot; compact validation summary",
    "holdings": "MySQL finance_meta.etf_holdings_snapshot; compact validation summary",
    "exposure": "MySQL finance_meta.etf_exposure_snapshot; compact validation summary",
    "macro": "MySQL finance_meta.macro_series_observation; compact validation summary",
}


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _date_range(values: list[Any]) -> str | None:
    dates = [_date_text(value) for value in values]
    dates = sorted({date for date in dates if date})
    if not dates:
        return None
    if dates[0] == dates[-1]:
        return dates[0]
    return f"{dates[0]}..{dates[-1]}"


def _status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "NONE", "NULL", "N/A", "UNKNOWN"}:
        return default
    if text in {"BLOCKED", "BLOCK", "ERROR", "FAILED", "FAIL"} or "ERROR" in text:
        return "BLOCKED"
    if text in {"NOT_RUN", "MISSING", "NO_DATA", "UNAVAILABLE"}:
        return "NEEDS_INPUT"
    if text in {"PASS", "OK", "READY", "SUCCESS", "FRESH", "COMPLETE", "COMPLETED"}:
        return "PASS"
    if text.startswith("READY_"):
        return "PASS"
    if text in {"REVIEW", "STALE", "PARTIAL", "WARNING", "WARN", "WATCH"} or "REVIEW" in text:
        return "REVIEW"
    return default


def _best_weighted_label(weights: dict[str, Any], *, fallback: str = "unknown") -> str:
    clean: list[tuple[str, float]] = []
    for key, value in dict(weights or {}).items():
        numeric = _optional_float(value)
        if numeric is None:
            continue
        clean.append((str(key or "").strip(), numeric))
    if not clean:
        return fallback
    clean.sort(key=lambda item: (-item[1], item[0]))
    return clean[0][0] or fallback


def _source_type_from_provenance(provenance: dict[str, Any], *, macro: bool = False) -> str:
    if provenance.get("source_type_weights"):
        return _best_weighted_label(dict(provenance.get("source_type_weights") or {}))
    row_key = "series_rows" if macro else "symbol_rows"
    source_types = [
        _safe_text(dict(row or {}).get("Source Type"), "")
        for row in _as_list(provenance.get(row_key))
        if isinstance(row, dict)
    ]
    source_types = [item for item in source_types if item]
    return source_types[0] if source_types else "unknown"


def _coverage_from_provenance(area: dict[str, Any], provenance: dict[str, Any]) -> str:
    if provenance.get("coverage_status_weights"):
        return _best_weighted_label(dict(provenance.get("coverage_status_weights") or {}), fallback="unknown")
    return _safe_text(area.get("status") or area.get("coverage_status"), "unknown")


def _max_staleness_days(provenance: dict[str, Any]) -> int | None:
    values: list[float] = []
    for row_key in ("symbol_rows", "series_rows"):
        for raw_row in _as_list(provenance.get(row_key)):
            if not isinstance(raw_row, dict):
                continue
            numeric = _optional_float(dict(raw_row).get("Staleness Days"))
            if numeric is not None:
                values.append(numeric)
    return int(max(values)) if values else None


def _proxy_status(*, source_type: str, coverage_status: str) -> str:
    text = f"{source_type} {coverage_status}".lower()
    if "proxy" in text:
        return "proxy"
    if "bridge" in text:
        return "bridge"
    if "partial" in text:
        return "partial"
    if "actual" in text or "official" in text or "historical" in text or "delisting" in text:
        return "actual"
    if "not_run" in text or "missing" in text:
        return "not_run"
    return "unknown"


def _decision_effect(
    *,
    base_status: Any,
    freshness_status: str,
    proxy_status: str,
    pit_safe: bool,
    reason: str,
) -> dict[str, Any]:
    status = _status(base_status, default="NEEDS_INPUT")
    if status == "PASS" and freshness_status in {"stale", "unknown", "not_run"}:
        status = "REVIEW" if freshness_status != "not_run" else "NEEDS_INPUT"
    if status == "PASS" and proxy_status in {"proxy", "bridge", "partial", "mixed"}:
        status = "REVIEW"
    if status == "PASS" and not pit_safe:
        status = "REVIEW"
    return {
        "status": status,
        "treat_as_pass": status == "PASS",
        "reason": reason if status == "PASS" else f"{reason}; provenance risk remains visible",
    }


def _row(
    *,
    evidence_area: str,
    source_name: Any,
    source_type: Any,
    source_date: Any,
    collected_at: Any,
    as_of_date: Any,
    available_at_assumption: str,
    snapshot_kind: str,
    coverage_status: Any,
    freshness_status: str,
    staleness_days: int | None,
    is_point_in_time_safe: bool,
    pit_risk: str,
    lookahead_risk: str,
    survivorship_risk: str,
    proxy_status: str,
    decision_effect: dict[str, Any],
    evidence_owner: str,
    storage_location: str,
) -> dict[str, Any]:
    return {
        "schema_version": DATA_PROVENANCE_SCHEMA_VERSION,
        "evidence_area": evidence_area,
        "source_name": _safe_text(source_name),
        "source_type": _safe_text(source_type),
        "source_date": _safe_text(source_date),
        "collected_at": _safe_text(collected_at),
        "as_of_date": _safe_text(as_of_date),
        "available_at_assumption": available_at_assumption,
        "snapshot_kind": snapshot_kind,
        "coverage_status": _safe_text(coverage_status),
        "freshness_status": freshness_status,
        "staleness_days": staleness_days,
        "is_point_in_time_safe": bool(is_point_in_time_safe),
        "pit_risk": pit_risk,
        "lookahead_risk": lookahead_risk,
        "survivorship_risk": survivorship_risk,
        "proxy_status": proxy_status,
        "decision_effect": decision_effect,
        "evidence_owner": evidence_owner,
        "storage_location": storage_location,
    }


def _provider_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    provider_context = dict(validation.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    as_of_date = provider_context.get("as_of_date") or validation.get("as_of_date")
    rows: list[dict[str, Any]] = []
    for area_key in ("operability", "holdings", "exposure", "macro"):
        area = dict(coverage.get(area_key) or {})
        if not area:
            continue
        provenance = dict(area.get("provenance") or {})
        if not provenance:
            continue
        macro = area_key == "macro"
        source_type = _source_type_from_provenance(provenance, macro=macro)
        coverage_status = _coverage_from_provenance(area, provenance)
        freshness_status = _safe_text(provenance.get("freshness_status"), "not_run").lower()
        proxy_status = _proxy_status(source_type=source_type, coverage_status=coverage_status)
        if macro:
            source_date = provenance.get("observation_range")
            snapshot_kind = "macro_observation_snapshot"
            available_at = "Macro rows are assumed available after observation/release timing, but revision vintage is not controlled."
            pit_risk = "macro revision vintage risk: ALFRED-style point-in-time vintage is not implemented"
            lookahead_risk = "review: observation date is bounded, but revised values may differ from decision-time values"
            storage = _PROVIDER_STORAGE["macro"]
        else:
            source_date = provenance.get("as_of_range")
            snapshot_kind = "current_provider_snapshot"
            available_at = "Provider snapshot is assumed available after collected_at; issuer publication lag is not independently verified."
            pit_risk = "current snapshot risk: provider row may not represent historical truth for the full validation period"
            lookahead_risk = "review: latest snapshot must not be treated as if it was known during older backtest dates"
            storage = _PROVIDER_STORAGE[area_key]
        pit_safe = False
        effect = _decision_effect(
            base_status=area.get("diagnostic_status") or area.get("status"),
            freshness_status=freshness_status,
            proxy_status=proxy_status,
            pit_safe=pit_safe,
            reason="provider/macro evidence is compact read-only metadata",
        )
        rows.append(
            _row(
                evidence_area=_PROVIDER_AREA_LABELS[area_key],
                source_name=provenance.get("source_mix"),
                source_type=source_type,
                source_date=source_date,
                collected_at=provenance.get("collected_range"),
                as_of_date=as_of_date,
                available_at_assumption=available_at,
                snapshot_kind=snapshot_kind,
                coverage_status=coverage_status,
                freshness_status=freshness_status,
                staleness_days=_max_staleness_days(provenance),
                is_point_in_time_safe=pit_safe,
                pit_risk=pit_risk,
                lookahead_risk=lookahead_risk,
                survivorship_risk="not applicable to provider/macro context",
                proxy_status=proxy_status,
                decision_effect=effect,
                evidence_owner=(
                    "finance/loaders/macro.py -> app/services/backtest_practical_validation_provider_context.py"
                    if macro
                    else "finance/loaders/provider.py -> app/services/backtest_practical_validation_provider_context.py"
                ),
                storage_location=storage,
            )
        )
    return rows


def _audit_row(audit: dict[str, Any], criteria: str) -> dict[str, Any]:
    expected = criteria.strip().lower()
    for raw_row in _as_list(dict(audit or {}).get("rows")):
        if not isinstance(raw_row, dict):
            continue
        row = dict(raw_row)
        if _safe_text(row.get("Criteria"), "").lower() == expected:
            return row
    return {}


def _data_coverage(validation: dict[str, Any]) -> dict[str, Any]:
    audit = dict(validation.get("data_coverage_audit") or {})
    if audit:
        return audit
    return build_data_coverage_audit(validation)


def _has_audit_row(audit: dict[str, Any], criteria: str) -> bool:
    return bool(_audit_row(audit, criteria))


def _has_price_runtime_inputs(validation: dict[str, Any], audit: dict[str, Any]) -> bool:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    return bool(
        validation.get("data_coverage_context")
        or curve_evidence.get("curve_provenance")
        or (_has_audit_row(audit, "Price DB window coverage") and _has_audit_row(audit, "PIT price window coverage"))
    )


def _has_lifecycle_inputs(validation: dict[str, Any], audit: dict[str, Any]) -> bool:
    context = dict(validation.get("data_coverage_context") or {})
    return bool(context.get("symbol_lifecycle_rows") or _has_audit_row(audit, "Survivorship / delisting control"))


def _price_runtime_row(validation: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    context = dict(validation.get("data_coverage_context") or {})
    curve_evidence = dict(validation.get("curve_evidence") or {})
    provenance = dict(curve_evidence.get("curve_provenance") or {})
    price = _audit_row(audit, "Price DB window coverage")
    pit = _audit_row(audit, "PIT price window coverage")
    price_status = _status(price.get("Status"), default="NEEDS_INPUT")
    pit_status = _status(pit.get("Status"), default="NEEDS_INPUT")
    runtime_source = _safe_text(curve_evidence.get("portfolio_curve_source") or provenance.get("portfolio_curve_source"), "")
    pit_safe = price_status == "PASS" and pit_status == "PASS" and "runtime" in runtime_source.lower()
    base_status = "PASS" if pit_safe else "NEEDS_INPUT" if "NEEDS_INPUT" in {price_status, pit_status} else "REVIEW"
    requested_start = _date_text(context.get("requested_start") or dict(provenance.get("requested_period") or {}).get("start"))
    requested_end = _date_text(context.get("requested_end") or dict(provenance.get("requested_period") or {}).get("end"))
    source_date = f"{requested_start or '-'}..{requested_end or '-'}"
    effect = _decision_effect(
        base_status=base_status,
        freshness_status="fresh" if pit_safe else "unknown",
        proxy_status="actual" if pit_safe else "unknown",
        pit_safe=pit_safe,
        reason="DB price window and runtime replay are aligned" if pit_safe else "price/runtime PIT evidence is incomplete",
    )
    return _row(
        evidence_area="Price window / runtime replay",
        source_name="finance_price.nyse_price_history + runtime replay",
        source_type="database_runtime",
        source_date=source_date,
        collected_at="-",
        as_of_date=requested_end,
        available_at_assumption="OHLCV rows are assumed available by market date; same-window runtime replay must bound the comparison period.",
        snapshot_kind="historical_price_window",
        coverage_status=price_status,
        freshness_status="fresh" if pit_safe else "unknown",
        staleness_days=None,
        is_point_in_time_safe=pit_safe,
        pit_risk="low when DB price window and runtime period coverage both pass" if pit_safe else "PIT review: price window or runtime replay is incomplete",
        lookahead_risk="low when runtime replay period is bounded to requested end" if pit_safe else "review: period coverage must be proven before treating the curve as PIT-safe",
        survivorship_risk="handled separately by lifecycle evidence",
        proxy_status="actual" if pit_safe else "unknown",
        decision_effect=effect,
        evidence_owner="finance/loaders/price.py -> app/services/backtest_data_coverage_audit.py",
        storage_location="MySQL finance_price.nyse_price_history; compact Data Coverage Audit row",
    )


def _lifecycle_row(validation: dict[str, Any], audit: dict[str, Any]) -> dict[str, Any]:
    context = dict(validation.get("data_coverage_context") or {})
    lifecycle_rows = [
        dict(row or {})
        for row in _as_list(context.get("symbol_lifecycle_rows"))
        if isinstance(row, dict)
    ]
    survivorship = _audit_row(audit, "Survivorship / delisting control")
    status = _status(survivorship.get("Status"), default="NEEDS_INPUT")
    source_types = sorted({_safe_text(row.get("source_type"), "") for row in lifecycle_rows if row.get("source_type")})
    coverage_statuses = sorted({_safe_text(row.get("coverage_status"), "") for row in lifecycle_rows if row.get("coverage_status")})
    source_names = sorted({_safe_text(row.get("source"), "") for row in lifecycle_rows if row.get("source")})
    if len(source_types) == 1:
        source_type = source_types[0]
    elif source_types:
        source_type = "mixed:" + ",".join(source_types[:4])
    else:
        source_type = "missing"
    if source_type == "current_listing_snapshot":
        snapshot_kind = "current_listing_snapshot"
    elif "historical_listing" in source_type or "delisting_feed" in source_type:
        snapshot_kind = "historical_lifecycle_evidence"
    elif "computed_from_snapshots" in source_type:
        snapshot_kind = "computed_partial_lifecycle"
    else:
        snapshot_kind = "lifecycle_evidence_missing"
    source_date = _date_range(
        [
            row.get("event_date")
            or row.get("last_seen_date")
            or row.get("first_seen_date")
            for row in lifecycle_rows
        ]
    )
    collected_at = _date_range([row.get("collected_at") for row in lifecycle_rows])
    pit_safe = status == "PASS" and snapshot_kind == "historical_lifecycle_evidence"
    proxy = _proxy_status(
        source_type=source_type,
        coverage_status="mixed:" + ",".join(coverage_statuses[:4]) if len(coverage_statuses) > 1 else (coverage_statuses[0] if coverage_statuses else "missing"),
    )
    if not pit_safe and proxy == "actual" and "current_listing_snapshot" in source_type:
        proxy = "partial"
    effect = _decision_effect(
        base_status=status,
        freshness_status="fresh" if lifecycle_rows else "not_run",
        proxy_status=proxy,
        pit_safe=pit_safe,
        reason="lifecycle evidence controls survivorship" if pit_safe else "lifecycle evidence is current/partial or non-covering",
    )
    return _row(
        evidence_area="Universe / lifecycle",
        source_name=", ".join(source_names[:4]) if source_names else "-",
        source_type=source_type,
        source_date=source_date,
        collected_at=collected_at,
        as_of_date=context.get("requested_end"),
        available_at_assumption="Historical membership / delisting rows are usable only when they cover the requested period; current snapshots are decision-time identity context only.",
        snapshot_kind=snapshot_kind,
        coverage_status=", ".join(coverage_statuses[:4]) if coverage_statuses else "missing",
        freshness_status="fresh" if lifecycle_rows else "not_run",
        staleness_days=None,
        is_point_in_time_safe=pit_safe,
        pit_risk="low when historical/delisting actual evidence covers the requested period" if pit_safe else "current/partial lifecycle risk: current listing evidence is not historical truth",
        lookahead_risk="low when event dates bound the requested period" if pit_safe else "review: listing observation after the backtest period cannot be treated as known historically",
        survivorship_risk="controlled by historical/delisting actual evidence" if pit_safe else "survivorship review: current or partial lifecycle evidence is not enough",
        proxy_status=proxy,
        decision_effect=effect,
        evidence_owner="finance/loaders/universe.py -> app/services/backtest_data_coverage_audit.py",
        storage_location="MySQL finance_meta.nyse_symbol_lifecycle; compact Data Coverage Audit row",
    )


def _robustness_row(validation: dict[str, Any]) -> dict[str, Any] | None:
    robustness_validation = dict(validation.get("robustness_validation") or {})
    run_set = dict(validation.get("robustness_run_set") or robustness_validation.get("robustness_run_set") or {})
    if not run_set:
        return None
    effect_source = dict(run_set.get("decision_effect") or {})
    status = _status(effect_source.get("final_review") or run_set.get("overall_status"), default="NEEDS_INPUT")
    pit_safe = status == "PASS"
    effect = {
        "status": status,
        "treat_as_pass": status == "PASS" and bool(effect_source.get("treat_as_pass", status == "PASS")),
        "reason": effect_source.get("reason") or "run-set compact evidence status",
    }
    if status != "PASS":
        effect["treat_as_pass"] = False
    return _row(
        evidence_area="Robustness run-set",
        source_name=run_set.get("robustness_run_set_id"),
        source_type="derived_compact_validation_evidence",
        source_date="-",
        collected_at="-",
        as_of_date=validation.get("validation_id") or run_set.get("selection_source_id"),
        available_at_assumption="Run-set is derived from already attached Practical Validation compact evidence; generated artifacts remain references only.",
        snapshot_kind="derived_validation_evidence",
        coverage_status=status,
        freshness_status="derived",
        staleness_days=None,
        is_point_in_time_safe=pit_safe,
        pit_risk="inherits underlying robustness / temporal / OOS evidence limitations",
        lookahead_risk="inherits underlying experiment period and artifact assumptions",
        survivorship_risk="inherits underlying data coverage audit",
        proxy_status="derived",
        decision_effect=effect,
        evidence_owner="app/services/backtest_robustness_run_set.py",
        storage_location="Existing Practical Validation / Final Review compact evidence; no full artifacts or raw rows",
    )


def _route_from_rows(rows: list[dict[str, Any]]) -> str:
    statuses = {
        _status(dict(row.get("decision_effect") or {}).get("status"), default="NEEDS_INPUT")
        for row in rows
    }
    if "BLOCKED" in statuses:
        return DATA_PROVENANCE_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return DATA_PROVENANCE_NEEDS_INPUT
    if "REVIEW" in statuses:
        return DATA_PROVENANCE_REVIEW
    return DATA_PROVENANCE_READY


def build_evidence_provenance_summary(validation: dict[str, Any]) -> dict[str, Any]:
    """Build a compact provenance contract from existing validation evidence."""

    validation = dict(validation or {})
    audit = _data_coverage(validation)
    rows: list[dict[str, Any]] = []
    rows.extend(_provider_rows(validation))
    if _has_price_runtime_inputs(validation, audit):
        rows.append(_price_runtime_row(validation, audit))
    if _has_lifecycle_inputs(validation, audit):
        rows.append(_lifecycle_row(validation, audit))
    robustness = _robustness_row(validation)
    if robustness is not None:
        rows.append(robustness)

    route = _route_from_rows(rows) if rows else DATA_PROVENANCE_NEEDS_INPUT
    status_counts = {
        status: sum(1 for row in rows if dict(row.get("decision_effect") or {}).get("status") == status)
        for status in _STATUS_RANK
    }
    current_snapshot_rows = [
        row for row in rows if "current" in str(row.get("snapshot_kind") or "").lower()
    ]
    proxy_rows = [
        row for row in rows if str(row.get("proxy_status") or "").lower() in {"proxy", "bridge", "partial"}
    ]
    stale_rows = [
        row for row in rows if str(row.get("freshness_status") or "").lower() in {"stale", "unknown", "not_run"}
    ]
    pit_safe_rows = [row for row in rows if bool(row.get("is_point_in_time_safe"))]
    return {
        "schema_version": DATA_PROVENANCE_SCHEMA_VERSION,
        "route": route,
        "route_label": DATA_PROVENANCE_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("DATA_PROVENANCE_", ""),
        "conclusion": (
            "Provenance contract 기준으로 pass-like 숨김 위험이 없습니다."
            if route == DATA_PROVENANCE_READY
            else "Provenance contract에서 current / stale / proxy / PIT review evidence가 남아 있습니다."
        ),
        "next_action": (
            "Final Review 판단과 monitoring handoff에서 provenance row를 그대로 인용합니다."
            if route == DATA_PROVENANCE_READY
            else "stale / proxy / current-only / non-PIT-safe row를 보강하거나 최종 판단의 open review item으로 남깁니다."
        ),
        "rows": rows,
        "metrics": {
            "pass": status_counts["PASS"],
            "review": status_counts["REVIEW"],
            "needs_input": status_counts["NEEDS_INPUT"],
            "blocked": status_counts["BLOCKED"],
            "total_rows": len(rows),
            "current_snapshot_rows": len(current_snapshot_rows),
            "proxy_rows": len(proxy_rows),
            "stale_or_unknown_rows": len(stale_rows),
            "pit_safe_rows": len(pit_safe_rows),
        },
        "execution_boundary": {
            "write_policy": "read_only_data_provenance_contract",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "full_holdings_persistence": False,
            "full_macro_series_persistence": False,
            "raw_provider_response_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "DATA_PROVENANCE_SCHEMA_VERSION",
    "DATA_PROVENANCE_READY",
    "DATA_PROVENANCE_REVIEW",
    "DATA_PROVENANCE_NEEDS_INPUT",
    "DATA_PROVENANCE_BLOCKED",
    "build_evidence_provenance_summary",
]
