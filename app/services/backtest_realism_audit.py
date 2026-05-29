from __future__ import annotations

from typing import Any


BACKTEST_REALISM_AUDIT_SCHEMA_VERSION = "backtest_realism_audit_v1"

BACKTEST_REALISM_READY = "BACKTEST_REALISM_READY"
BACKTEST_REALISM_REVIEW = "BACKTEST_REALISM_REVIEW"
BACKTEST_REALISM_NEEDS_INPUT = "BACKTEST_REALISM_NEEDS_INPUT"
BACKTEST_REALISM_BLOCKED = "BACKTEST_REALISM_BLOCKED"

BACKTEST_REALISM_ROUTE_LABELS = {
    BACKTEST_REALISM_READY: "Ready",
    BACKTEST_REALISM_REVIEW: "Review Required",
    BACKTEST_REALISM_NEEDS_INPUT: "Realism Input Needed",
    BACKTEST_REALISM_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "pass", "ready", "enabled"}


def _status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "NONE", "NULL", "N/A", "UNKNOWN"}:
        return default
    if text in {"BLOCKED", "BLOCK", "ERROR", "FAILED", "FAIL"} or "ERROR" in text:
        return "BLOCKED"
    if text in {"NOT_RUN", "MISSING", "NO_DATA", "UNAVAILABLE"}:
        return "NEEDS_INPUT"
    if text in {"PASS", "OK", "READY", "SUCCESS", "COMPLETE", "COMPLETED"}:
        return "PASS"
    if text.startswith("READY_"):
        return "PASS"
    if text in {"REVIEW", "STALE", "PARTIAL", "WARNING", "WARN", "WATCH"} or "REVIEW" in text:
        return "REVIEW"
    return default


def _row(
    *,
    criteria: str,
    status: str,
    current: Any,
    evidence: Any,
    next_action: str,
    meaning: str,
) -> dict[str, Any]:
    normalized = status if status in _STATUS_RANK else _status(status, default="REVIEW")
    return {
        "Criteria": criteria,
        "Status": normalized,
        "Ready": normalized == "PASS",
        "Current": _safe_text(current),
        "Evidence": _safe_text(evidence),
        "Next Action": next_action,
        "Meaning": meaning,
    }


def _nested_values_for_key(value: Any, key: str, *, limit: int = 20) -> list[Any]:
    found: list[Any] = []
    key_lower = key.lower()

    def _walk(node: Any) -> None:
        if len(found) >= limit:
            return
        if isinstance(node, dict):
            for item_key, child in node.items():
                if str(item_key or "").strip().lower() == key_lower:
                    found.append(child)
                    if len(found) >= limit:
                        return
                if isinstance(child, (dict, list)):
                    _walk(child)
                    if len(found) >= limit:
                        return
        elif isinstance(node, list):
            for item in node:
                if isinstance(item, (dict, list)):
                    _walk(item)
                    if len(found) >= limit:
                        return

    _walk(value)
    return found


def _first_value(root: dict[str, Any], *keys: str) -> Any:
    for key in keys:
        for value in _nested_values_for_key(root, key):
            if value not in (None, ""):
                return value
    return None


def _first_float(root: dict[str, Any], *keys: str) -> float | None:
    for key in keys:
        for value in _nested_values_for_key(root, key):
            numeric = _optional_float(value)
            if numeric is not None:
                return numeric
    return None


def _first_non_none(*values: Any) -> Any:
    for value in values:
        if value is not None:
            return value
    return None


def _find_diagnostic(validation: dict[str, Any], domain: str) -> dict[str, Any]:
    for diagnostic in _as_list(validation.get("diagnostic_results")):
        row = dict(diagnostic or {})
        if str(row.get("domain") or "") == domain:
            return row
    return {}


def _provider_operability(validation: dict[str, Any]) -> dict[str, Any]:
    provider_context = dict(validation.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    if coverage:
        return dict(coverage.get("operability") or {})
    input_context = dict(dict(validation.get("input_evidence") or {}).get("provider_coverage") or {})
    return dict(dict(input_context.get("coverage") or {}).get("operability") or {})


def _weight_from_mapping(mapping: dict[str, Any], *keys: str) -> float:
    total = 0.0
    lowered = {str(key).lower() for key in keys}
    for raw_key, raw_value in dict(mapping or {}).items():
        if str(raw_key or "").strip().lower() in lowered:
            total += _optional_float(raw_value) or 0.0
    return float(total)


def _cost_model_contract_from_root(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    diagnostic = _find_diagnostic(validation, "operability_cost_liquidity")
    metrics = dict(diagnostic.get("metrics") or {})
    cost_bps = _first_non_none(
        _optional_float(metrics.get("one_way_cost_bps")),
        _first_float(source, "transaction_cost_bps", "one_way_cost_bps"),
        _first_float(validation, "transaction_cost_bps"),
    )
    hardening = _truthy(_first_value(source, "real_money_hardening") or _first_value(validation, "real_money_hardening"))
    raw_application_status = _safe_text(
        _first_value(source, "cost_application_status")
        or _first_value(source, "cost_applied_status")
        or _first_value(validation, "cost_application_status"),
        fallback="",
    ).lower()
    cost_source = _safe_text(
        _first_value(source, "cost_model_source")
        or _first_value(validation, "cost_model_source"),
        fallback="",
    )
    estimated_cost_total = _first_non_none(
        _first_float(source, "estimated_cost_total"),
        _first_float(validation, "estimated_cost_total"),
    )
    avg_turnover = _first_non_none(_first_float(source, "avg_turnover"), _first_float(validation, "avg_turnover"))
    gross_end_balance = _first_non_none(
        _first_float(source, "gross_end_balance"),
        _first_float(validation, "gross_end_balance"),
    )
    net_end_balance = _first_non_none(
        _first_float(source, "net_end_balance"),
        _first_float(validation, "net_end_balance"),
    )

    applied_statuses = {
        "applied_to_result_curve",
        "applied_to_net_curve",
        "net_curve_applied",
        "result_curve_net_of_cost",
    }
    if cost_bps is None:
        application_status = "missing_cost_input"
        evidence = "transaction_cost_bps not attached"
    elif cost_bps <= 0:
        application_status = "zero_or_non_positive_cost"
        evidence = "zero or non-positive cost assumption"
    elif raw_application_status in applied_statuses:
        application_status = "applied_to_result_curve"
        evidence = cost_source or "explicit cost_application_status attached"
    elif hardening and cost_source and estimated_cost_total is not None and avg_turnover is not None:
        application_status = "applied_to_result_curve_legacy_inferred"
        evidence = "real_money_hardening plus cost source / estimated cost / turnover metadata"
    elif hardening and estimated_cost_total is not None and gross_end_balance is not None:
        application_status = "applied_to_result_curve_legacy_inferred"
        evidence = "real_money_hardening plus gross/net cost metadata"
    elif hardening:
        application_status = "legacy_hardening_flag_only"
        evidence = "real_money_hardening=True but cost application contract is incomplete"
    else:
        application_status = "assumption_only"
        evidence = "cost assumption exists but result-curve application is not proven"

    return {
        "schema_version": "cost_model_source_contract_v1",
        "transaction_cost_bps": cost_bps,
        "application_status": application_status,
        "cost_model_source": cost_source or None,
        "cost_application_target": _first_value(source, "cost_application_target")
        or _first_value(validation, "cost_application_target"),
        "cost_turnover_source": _first_value(source, "cost_turnover_source")
        or _first_value(validation, "cost_turnover_source"),
        "estimated_cost_total": estimated_cost_total,
        "avg_turnover": avg_turnover,
        "gross_end_balance": gross_end_balance,
        "net_end_balance": net_end_balance,
        "real_money_hardening": hardening,
        "evidence": evidence,
    }


def build_cost_model_source_contract(validation: dict[str, Any]) -> dict[str, Any]:
    """Extract the compact cost source contract used by Backtest Realism Audit."""

    validation = dict(validation or {})
    source = dict(validation.get("selection_source_snapshot") or {})
    source_snapshot = dict(source.get("source_snapshot") or {})
    evidence_root = {
        "validation": validation,
        "selection_source_snapshot": source,
        "source_snapshot": source_snapshot,
    }
    return _cost_model_contract_from_root(validation, evidence_root)


def _net_cost_curve_contract_from_root(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    cost_bps = _first_non_none(
        _first_float(source, "transaction_cost_bps", "one_way_cost_bps"),
        _first_float(validation, "transaction_cost_bps"),
    )
    cost_application_status = _safe_text(
        _first_value(source, "cost_application_status")
        or _first_value(validation, "cost_application_status"),
        fallback="",
    ).lower()
    net_curve_status = _safe_text(
        _first_value(source, "net_cost_curve_status")
        or _first_value(validation, "net_cost_curve_status"),
        fallback="",
    ).lower()
    estimated_cost_total = _first_non_none(
        _first_float(source, "estimated_cost_total"),
        _first_float(validation, "estimated_cost_total"),
    )
    estimated_cost_positive_rows = _first_non_none(
        _first_float(source, "estimated_cost_positive_rows"),
        _first_float(validation, "estimated_cost_positive_rows"),
    )
    gross_end_balance = _first_non_none(
        _first_float(source, "gross_end_balance"),
        _first_float(validation, "gross_end_balance"),
    )
    net_end_balance = _first_non_none(
        _first_float(source, "net_end_balance"),
        _first_float(validation, "net_end_balance"),
    )
    gross_net_delta = _first_non_none(
        _first_float(source, "gross_net_end_balance_delta"),
        _first_float(validation, "gross_net_end_balance_delta"),
    )
    if gross_net_delta is None and gross_end_balance is not None and net_end_balance is not None:
        gross_net_delta = float(gross_end_balance - net_end_balance)
    rows = _first_non_none(
        _first_float(source, "net_cost_curve_rows"),
        _first_float(validation, "net_cost_curve_rows"),
    )
    turnover_status = _safe_text(
        _first_value(source, "turnover_estimation_status")
        or _first_value(validation, "turnover_estimation_status"),
        fallback="",
    ).lower()
    total_balance_is_net = _truthy(
        _first_value(source, "total_balance_is_net_of_cost")
        or _first_value(validation, "total_balance_is_net_of_cost")
    )

    if net_curve_status:
        proof_status = net_curve_status
    elif cost_bps is None:
        proof_status = "missing_cost_input"
    elif cost_bps <= 0:
        proof_status = "applied_zero_cost_bps" if cost_application_status else "zero_cost_assumption"
    elif estimated_cost_total and estimated_cost_total > 0 and gross_net_delta and gross_net_delta > 0:
        proof_status = "applied_with_measurable_cost_legacy_inferred"
    elif cost_application_status == "applied_to_result_curve":
        proof_status = "legacy_application_flag_only"
    else:
        proof_status = "missing_net_cost_curve_proof"

    return {
        "schema_version": "net_cost_curve_contract_v1",
        "proof_status": proof_status,
        "cost_application_status": cost_application_status or None,
        "transaction_cost_bps": cost_bps,
        "estimated_cost_total": estimated_cost_total,
        "estimated_cost_positive_rows": int(estimated_cost_positive_rows) if estimated_cost_positive_rows is not None else None,
        "gross_end_balance": gross_end_balance,
        "net_end_balance": net_end_balance,
        "gross_net_end_balance_delta": gross_net_delta,
        "net_cost_curve_rows": int(rows) if rows is not None else None,
        "total_balance_is_net_of_cost": total_balance_is_net,
        "turnover_estimation_status": turnover_status or None,
        "evidence": _first_value(source, "net_cost_curve_application_target")
        or _first_value(validation, "net_cost_curve_application_target")
        or "net cost curve proof metadata",
    }


def build_net_cost_curve_contract(validation: dict[str, Any]) -> dict[str, Any]:
    """Extract the compact net cost curve proof used by Backtest Realism Audit."""

    validation = dict(validation or {})
    source = dict(validation.get("selection_source_snapshot") or {})
    source_snapshot = dict(source.get("source_snapshot") or {})
    evidence_root = {
        "validation": validation,
        "selection_source_snapshot": source,
        "source_snapshot": source_snapshot,
    }
    return _net_cost_curve_contract_from_root(validation, evidence_root)


def _transaction_cost_row(
    validation: dict[str, Any],
    source: dict[str, Any],
    cost_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = dict(cost_contract or _cost_model_contract_from_root(validation, source))
    cost_bps = _optional_float(contract.get("transaction_cost_bps"))
    application_status = str(contract.get("application_status") or "").strip()
    if cost_bps is None:
        status = "NEEDS_INPUT"
        current = "missing"
        evidence = contract.get("evidence") or "transaction_cost_bps not attached"
        next_action = "거래비용 bps와 적용 여부를 runtime metadata에 보강합니다."
    elif cost_bps <= 0:
        status = "REVIEW"
        current = f"{cost_bps:g} bps"
        evidence = contract.get("evidence") or "zero or non-positive cost assumption"
        next_action = "zero-cost backtest인지 의도적으로 확인하고 최종 판단 근거에 남깁니다."
    elif application_status.startswith("applied_to_result_curve"):
        status = "PASS"
        current = f"{cost_bps:g} bps / {application_status}"
        evidence = contract.get("evidence") or "cost application contract attached"
        next_action = "추가 조치 없음"
    else:
        status = "REVIEW"
        current = f"{cost_bps:g} bps / {application_status or 'assumption_only'}"
        evidence = contract.get("evidence") or "cost assumption exists but net-curve application is not proven"
        next_action = "비용이 result curve에 실제 반영됐는지 runtime metadata를 확인합니다."
    return _row(
        criteria="Transaction cost model",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="성과가 거래비용 / spread / slippage 영향을 반영했는지 확인합니다.",
    )


def _net_cost_curve_row(
    validation: dict[str, Any],
    source: dict[str, Any],
    curve_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = dict(curve_contract or _net_cost_curve_contract_from_root(validation, source))
    proof_status = str(contract.get("proof_status") or "").strip()
    estimated_cost_total = _optional_float(contract.get("estimated_cost_total"))
    gross_net_delta = _optional_float(contract.get("gross_net_end_balance_delta"))
    positive_rows = contract.get("estimated_cost_positive_rows")
    if proof_status.startswith("applied_with_measurable_cost"):
        status = "PASS"
        current = f"cost={estimated_cost_total if estimated_cost_total is not None else '-'} / gross-net={gross_net_delta if gross_net_delta is not None else '-'}"
        evidence = contract.get("evidence") or "net cost curve proof attached"
        next_action = "추가 조치 없음"
    elif proof_status in {"applied_without_turnover_estimate", "legacy_application_flag_only", "applied_no_cost_impact"}:
        status = "REVIEW"
        current = f"{proof_status} / positive_rows={positive_rows if positive_rows is not None else '-'}"
        evidence = contract.get("evidence") or "net curve application proof is incomplete"
        next_action = "gross / net / estimated cost proof와 turnover estimate를 함께 확인합니다."
    elif proof_status in {"applied_zero_cost_bps", "zero_cost_assumption"}:
        status = "REVIEW"
        current = proof_status
        evidence = "zero or non-positive cost impact"
        next_action = "zero-cost run인지 의도적으로 확인하고 최종 판단 사유에 남깁니다."
    elif proof_status == "missing_cost_input":
        status = "NEEDS_INPUT"
        current = "missing cost input"
        evidence = "transaction_cost_bps missing"
        next_action = "거래비용 입력과 net curve proof를 보강합니다."
    else:
        status = "NEEDS_INPUT"
        current = proof_status or "missing"
        evidence = contract.get("evidence") or "net cost curve proof missing"
        next_action = "gross / net / estimated cost curve metadata를 보강합니다."
    return _row(
        criteria="Net cost curve proof",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="거래비용이 단순 가정이 아니라 결과 곡선의 net 성과에 실제 반영됐는지 확인합니다.",
    )


def _turnover_evidence_contract_from_root(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    avg_turnover = _first_non_none(_first_float(source, "avg_turnover"), _first_float(validation, "avg_turnover"))
    max_turnover = _first_non_none(_first_float(source, "max_turnover"), _first_float(validation, "max_turnover"))
    avg_rebalance_turnover = _first_non_none(
        _first_float(source, "avg_rebalance_turnover"),
        _first_float(validation, "avg_rebalance_turnover"),
    )
    observation_count = _first_non_none(
        _first_float(source, "turnover_observation_count"),
        _first_float(validation, "turnover_observation_count"),
    )
    rebalance_rows = _first_non_none(
        _first_float(source, "turnover_rebalance_rows"),
        _first_float(validation, "turnover_rebalance_rows"),
    )
    nonzero_count = _first_non_none(
        _first_float(source, "turnover_nonzero_count"),
        _first_float(validation, "turnover_nonzero_count"),
    )
    estimation_status = _safe_text(
        _first_value(source, "turnover_estimation_status")
        or _first_value(validation, "turnover_estimation_status"),
        fallback="",
    ).lower()
    turnover_source = _safe_text(
        _first_value(source, "turnover_source")
        or _first_value(source, "cost_turnover_source")
        or _first_value(validation, "turnover_source"),
        fallback="",
    )
    missing_columns = _first_value(source, "turnover_input_missing_columns") or _first_value(
        validation,
        "turnover_input_missing_columns",
    )
    rebalance = (
        _first_value(source, "rebalance_interval")
        or _first_value(source, "rebalance_freq")
        or _first_value(source, "factor_freq")
        or dict(dict(validation.get("selection_source_snapshot") or {}).get("construction") or {}).get("rebalance_cadence")
    )

    if estimation_status == "estimated_from_holdings":
        evidence_strength = "actual_estimate"
        evidence = turnover_source or "turnover estimated from holdings delta"
    elif estimation_status.startswith("not_estimated"):
        evidence_strength = "missing_estimate"
        evidence = estimation_status
    elif avg_turnover is not None or max_turnover is not None:
        evidence_strength = "legacy_estimate"
        evidence = "legacy turnover metadata attached without explicit source contract"
    elif rebalance:
        evidence_strength = "cadence_only"
        evidence = "rebalance cadence exists but turnover estimate missing"
    else:
        evidence_strength = "missing"
        evidence = "turnover / rebalance metadata missing"

    return {
        "schema_version": "turnover_evidence_contract_v1",
        "evidence_strength": evidence_strength,
        "turnover_estimation_status": estimation_status or None,
        "turnover_source": turnover_source or None,
        "avg_turnover": avg_turnover,
        "max_turnover": max_turnover,
        "avg_rebalance_turnover": avg_rebalance_turnover,
        "turnover_observation_count": int(observation_count) if observation_count is not None else None,
        "turnover_rebalance_rows": int(rebalance_rows) if rebalance_rows is not None else None,
        "turnover_nonzero_count": int(nonzero_count) if nonzero_count is not None else None,
        "turnover_input_missing_columns": missing_columns,
        "rebalance_cadence": rebalance,
        "evidence": evidence,
    }


def build_turnover_evidence_contract(validation: dict[str, Any]) -> dict[str, Any]:
    """Extract the compact turnover evidence contract used by Backtest Realism Audit."""

    validation = dict(validation or {})
    source = dict(validation.get("selection_source_snapshot") or {})
    source_snapshot = dict(source.get("source_snapshot") or {})
    evidence_root = {
        "validation": validation,
        "selection_source_snapshot": source,
        "source_snapshot": source_snapshot,
    }
    return _turnover_evidence_contract_from_root(validation, evidence_root)


def _liquidity_capacity_contract_from_validation(validation: dict[str, Any]) -> dict[str, Any]:
    diagnostic = _find_diagnostic(validation, "operability_cost_liquidity")
    provider = _provider_operability(validation)
    provider_status = provider.get("diagnostic_status") or diagnostic.get("status")
    normalized_status = _status(provider_status)
    coverage_weight = _optional_float(provider.get("coverage_weight"))
    metrics = dict(provider.get("metrics") or {})
    provenance = dict(provider.get("provenance") or {})
    source_type_weights = dict(provenance.get("source_type_weights") or {})
    coverage_status_weights = dict(provenance.get("coverage_status_weights") or {})
    freshness_status = str(provenance.get("freshness_status") or "").strip().lower()
    stale_weight = _optional_float(provenance.get("stale_weight")) or 0.0
    unknown_freshness_weight = _optional_float(provenance.get("unknown_freshness_weight")) or 0.0
    official_weight = _weight_from_mapping(source_type_weights, "official")
    actual_weight = _weight_from_mapping(coverage_status_weights, "actual")
    supported_weight = sum((_optional_float(value) or 0.0) for value in coverage_status_weights.values())
    weak_source_weight = _weight_from_mapping(
        source_type_weights,
        "bridge",
        "database_bridge",
        "computed_proxy",
        "proxy",
        "unknown",
    )
    weak_coverage_weight = _weight_from_mapping(
        coverage_status_weights,
        "bridge",
        "proxy",
        "missing",
        "error",
        "not_run",
    )
    missing_symbols = _as_list(provider.get("missing_symbols"))
    review_symbols = _as_list(metrics.get("review_symbols"))
    review_count = int(_optional_float(metrics.get("review_count")) or len(review_symbols or []))
    has_provider_context = bool(provider)
    has_provenance = bool(provenance)

    if normalized_status == "BLOCKED":
        proof_status = "blocked_provider_operability"
    elif not has_provider_context and not diagnostic:
        proof_status = "missing_provider_operability"
    elif normalized_status == "NEEDS_INPUT" or coverage_weight is None or coverage_weight <= 0.0:
        proof_status = "missing_provider_operability"
    elif not has_provenance:
        proof_status = "legacy_provider_pass_without_capacity_contract"
    elif freshness_status in {"stale", "unknown"} or stale_weight > 0.0 or unknown_freshness_weight > 0.0:
        proof_status = "stale_or_unknown_provider_snapshot"
    elif coverage_weight < 80.0:
        proof_status = "partial_liquidity_coverage"
    elif official_weight < 80.0 or actual_weight < 80.0 or weak_source_weight > 0.0 or weak_coverage_weight > 0.0:
        proof_status = "weak_source_or_proxy_liquidity_evidence"
    elif normalized_status == "PASS" and review_count <= 0:
        proof_status = "official_fresh_capacity_evidence"
    elif normalized_status == "REVIEW" or review_count > 0:
        proof_status = "provider_operability_review"
    else:
        proof_status = "incomplete_liquidity_capacity_evidence"

    return {
        "schema_version": "liquidity_capacity_contract_v1",
        "proof_status": proof_status,
        "provider_status": provider_status,
        "diagnostic_status": normalized_status,
        "coverage_weight": coverage_weight,
        "freshness_status": freshness_status or None,
        "source_type_weights": source_type_weights,
        "coverage_status_weights": coverage_status_weights,
        "official_source_weight": round(official_weight, 4),
        "actual_coverage_weight": round(actual_weight, 4),
        "supported_coverage_weight": round(supported_weight, 4),
        "weak_source_weight": round(weak_source_weight, 4),
        "weak_coverage_weight": round(weak_coverage_weight, 4),
        "stale_weight": round(stale_weight, 4),
        "unknown_freshness_weight": round(unknown_freshness_weight, 4),
        "missing_symbols": missing_symbols,
        "review_symbols": review_symbols,
        "review_count": review_count,
        "min_net_assets": _optional_float(metrics.get("min_net_assets")),
        "min_avg_daily_dollar_volume": _optional_float(metrics.get("min_avg_daily_dollar_volume")),
        "max_bid_ask_spread_pct": _optional_float(metrics.get("max_bid_ask_spread_pct")),
        "max_expense_ratio": _optional_float(metrics.get("max_expense_ratio")),
        "max_abs_premium_discount_pct": _optional_float(metrics.get("max_abs_premium_discount_pct")),
        "as_of_range": provenance.get("as_of_range"),
        "source_mix": provenance.get("source_mix"),
        "evidence": provider.get("summary")
        or diagnostic.get("summary")
        or provenance.get("source_mix")
        or "provider operability evidence",
    }


def build_liquidity_capacity_contract(validation: dict[str, Any]) -> dict[str, Any]:
    """Extract compact liquidity / capacity evidence used by Backtest Realism Audit."""

    return _liquidity_capacity_contract_from_validation(dict(validation or {}))


def _turnover_row(
    validation: dict[str, Any],
    source: dict[str, Any],
    turnover_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = dict(turnover_contract or _turnover_evidence_contract_from_root(validation, source))
    avg_turnover = _optional_float(contract.get("avg_turnover"))
    max_turnover = _optional_float(contract.get("max_turnover"))
    avg_rebalance_turnover = _optional_float(contract.get("avg_rebalance_turnover"))
    evidence_strength = str(contract.get("evidence_strength") or "").strip()
    rebalance = contract.get("rebalance_cadence")
    if evidence_strength == "actual_estimate":
        status = "PASS"
        current = (
            f"avg={avg_turnover if avg_turnover is not None else '-'} / "
            f"max={max_turnover if max_turnover is not None else '-'} / "
            f"rebalance_avg={avg_rebalance_turnover if avg_rebalance_turnover is not None else '-'}"
        )
        evidence = contract.get("evidence") or "turnover estimate contract attached"
        next_action = "turnover가 높으면 비용 민감도 sweep을 후속으로 확인합니다."
    elif evidence_strength == "legacy_estimate":
        status = "REVIEW"
        current = f"avg={avg_turnover if avg_turnover is not None else '-'} / max={max_turnover if max_turnover is not None else '-'}"
        evidence = contract.get("evidence") or "legacy turnover metadata attached"
        next_action = "turnover source contract를 확인한 뒤 비용 민감도와 연결합니다."
    elif rebalance:
        status = "REVIEW"
        current = f"rebalance={rebalance}"
        evidence = contract.get("evidence") or "rebalance cadence exists but turnover estimate missing"
        next_action = "rebalance별 turnover 추정치를 result metadata에 보강합니다."
    else:
        status = "NEEDS_INPUT"
        current = "missing"
        evidence = contract.get("evidence") or "turnover / rebalance metadata missing"
        next_action = "turnover 또는 rebalance cadence evidence를 보강합니다."
    return _row(
        criteria="Turnover evidence",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="리밸런싱과 포지션 교체 빈도가 비용과 체결 가능성에 미치는 영향을 확인합니다.",
    )


def _liquidity_row(
    validation: dict[str, Any],
    liquidity_contract: dict[str, Any] | None = None,
) -> dict[str, Any]:
    contract = dict(liquidity_contract or _liquidity_capacity_contract_from_validation(validation))
    proof_status = str(contract.get("proof_status") or "").strip()
    coverage_weight = contract.get("coverage_weight")
    if proof_status == "official_fresh_capacity_evidence":
        status = "PASS"
        evidence = contract.get("evidence") or "fresh official provider capacity evidence"
        next_action = "추가 조치 없음"
    elif proof_status == "blocked_provider_operability":
        status = "BLOCKED"
        evidence = contract.get("evidence") or "provider operability blocked"
        next_action = "가격 / provider blocker를 먼저 해소합니다."
    elif proof_status == "missing_provider_operability":
        status = "NEEDS_INPUT"
        evidence = contract.get("evidence") or "provider operability missing"
        next_action = "ETF operability / liquidity provider snapshot을 보강합니다."
    else:
        status = "REVIEW"
        evidence = contract.get("evidence") or "operability evidence requires review"
        next_action = "fresh official coverage, AUM, ADV, spread, premium-discount gap을 확인합니다."
    current = (
        f"{proof_status or 'missing'} / coverage={coverage_weight if coverage_weight is not None else '-'} / "
        f"freshness={contract.get('freshness_status') or '-'}"
    )
    return _row(
        criteria="Liquidity / operability evidence",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="ETF AUM, spread, 거래대금, price/volume proxy가 실전 운용성에 충분한지 확인합니다.",
    )


def _net_policy_row(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    net_spread = _first_non_none(_first_float(source, "net_cagr_spread"), _first_float(validation, "net_cagr_spread"))
    min_spread = _first_non_none(
        _first_float(source, "promotion_min_net_cagr_spread"),
        _first_float(validation, "promotion_min_net_cagr_spread"),
    )
    real_money = dict(validation.get("real_money_signal") or {})
    if not real_money:
        real_money = dict(dict(validation.get("selection_source_snapshot") or {}).get("real_money_signal") or {})
    if net_spread is not None and min_spread is not None:
        status = "PASS" if net_spread >= min_spread else "REVIEW"
        current = f"net spread={net_spread:.4f} / min={min_spread:.4f}"
        evidence = "net_cagr_spread policy metadata attached"
        next_action = "policy 미달이면 benchmark-relative net performance를 재검토합니다." if status == "REVIEW" else "추가 조치 없음"
    elif real_money:
        status = "REVIEW"
        current = real_money.get("promotion") or real_money.get("deployment") or "real_money_signal attached"
        evidence = "real_money signal exists but net spread policy is incomplete"
        next_action = "net CAGR spread와 promotion threshold를 함께 보강합니다."
    else:
        status = "NEEDS_INPUT"
        current = "missing"
        evidence = "net performance policy missing"
        next_action = "benchmark-relative net performance threshold를 보강합니다."
    return _row(
        criteria="Net performance policy",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="비용 반영 후 benchmark 대비 성과 기준이 있는지 확인합니다.",
    )


def _rebalance_row(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    construction = dict(dict(validation.get("selection_source_snapshot") or {}).get("construction") or {})
    cadence = (
        construction.get("rebalance_cadence")
        or _first_value(source, "rebalance_interval")
        or _first_value(source, "rebalance_freq")
        or _first_value(source, "factor_freq")
        or _first_value(validation, "review_cadence")
    )
    if cadence:
        status = "PASS"
        current = cadence
        evidence = "cadence metadata attached"
        next_action = "turnover / 비용 민감도와 함께 해석합니다."
    else:
        status = "REVIEW"
        current = "missing"
        evidence = "rebalance cadence not explicit"
        next_action = "리밸런싱 주기와 trade timing 가정을 명시합니다."
    return _row(
        criteria="Rebalance / trade timing",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="전략의 매매 주기와 체결 시점 가정이 명확한지 확인합니다.",
    )


def _tax_account_row(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    scope = (
        _first_value(source, "tax_account_scope")
        or _first_value(source, "tax_treatment")
        or _first_value(source, "account_constraints")
        or _first_value(validation, "tax_account_scope")
    )
    acknowledged = _truthy(
        _first_value(source, "operator_tax_scope_acknowledged")
        or _first_value(source, "tax_scope_acknowledged")
        or _first_value(validation, "operator_tax_scope_acknowledged")
    )
    if scope or acknowledged:
        status = "PASS"
        current = scope or "operator acknowledged"
        evidence = "tax/account scope attached"
        next_action = "계좌별 세금 / 매매 제한은 실제 운용 단계에서 별도 확인합니다."
    else:
        status = "REVIEW"
        current = "not modeled"
        evidence = "tax/account-specific constraints absent"
        next_action = "세금, 계좌 제약, 최소 주문 단위는 최종 판단 사유에 남깁니다."
    return _row(
        criteria="Tax / account scope",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="백테스트가 세금, 계좌 유형, 주문 단위 같은 실제 계좌 제약을 반영했는지 확인합니다.",
    )


def _execution_boundary_row(validation: dict[str, Any]) -> dict[str, Any]:
    prohibited = {
        "live_approval": validation.get("live_approval"),
        "order_instruction": validation.get("order_instruction"),
        "auto_rebalance": validation.get("auto_rebalance"),
    }
    active = [name for name, value in prohibited.items() if _truthy(value)]
    status = "BLOCKED" if active else "PASS"
    return _row(
        criteria="Execution boundary",
        status=status,
        current=" / ".join(active) if active else "read-only realism audit / writes disabled",
        evidence="db_write=False / registry_write=False / memo_persistence=False",
        next_action="주문 / 승인 / 자동 리밸런싱 경계를 제거합니다." if active else "추가 조치 없음",
        meaning="Backtest Realism Audit은 실거래 지시나 자동 저장 기능이 아니라 판단 보조 근거입니다.",
    )


def _route_from_rows(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row.get("Status") or "") for row in rows}
    if "BLOCKED" in statuses:
        return BACKTEST_REALISM_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return BACKTEST_REALISM_NEEDS_INPUT
    if "REVIEW" in statuses:
        return BACKTEST_REALISM_REVIEW
    return BACKTEST_REALISM_READY


def build_backtest_realism_audit(validation: dict[str, Any]) -> dict[str, Any]:
    """Summarize whether backtest results include practical cost and execution assumptions."""

    validation = dict(validation or {})
    source = dict(validation.get("selection_source_snapshot") or {})
    source_snapshot = dict(source.get("source_snapshot") or {})
    evidence_root = {
        "validation": validation,
        "selection_source_snapshot": source,
        "source_snapshot": source_snapshot,
    }
    cost_model_contract = _cost_model_contract_from_root(validation, evidence_root)
    net_cost_curve_contract = _net_cost_curve_contract_from_root(validation, evidence_root)
    turnover_evidence_contract = _turnover_evidence_contract_from_root(validation, evidence_root)
    liquidity_capacity_contract = _liquidity_capacity_contract_from_validation(validation)
    rows = [
        _transaction_cost_row(validation, evidence_root, cost_model_contract),
        _net_cost_curve_row(validation, evidence_root, net_cost_curve_contract),
        _turnover_row(validation, evidence_root, turnover_evidence_contract),
        _liquidity_row(validation, liquidity_capacity_contract),
        _net_policy_row(validation, evidence_root),
        _rebalance_row(validation, evidence_root),
        _tax_account_row(validation, evidence_root),
        _execution_boundary_row(validation),
    ]
    route = _route_from_rows(rows)
    status_counts = {
        status: sum(1 for row in rows if row.get("Status") == status)
        for status in _STATUS_RANK
    }
    if route == BACKTEST_REALISM_READY:
        conclusion = "Backtest realism audit 기준으로 즉시 보강이 필요한 공백이 없습니다."
        next_action = "Final Review에서 validation gate와 operator 판단을 함께 확인합니다."
    elif route == BACKTEST_REALISM_BLOCKED:
        conclusion = "Backtest realism audit에서 차단 항목이 발견됐습니다."
        next_action = "BLOCKED 항목을 먼저 해소한 뒤 최종 선택 판단을 진행합니다."
    elif route == BACKTEST_REALISM_NEEDS_INPUT:
        conclusion = "실전성 판단을 위해 비용 / turnover / liquidity / net policy evidence가 더 필요합니다."
        next_action = "runtime metadata 또는 provider operability evidence를 보강합니다."
    else:
        conclusion = "실전성 근거는 일부 확인됐지만 REVIEW 항목이 남아 있습니다."
        next_action = "REVIEW 항목을 최종 판단 사유에 명시하거나 evidence를 보강합니다."
    return {
        "schema_version": BACKTEST_REALISM_AUDIT_SCHEMA_VERSION,
        "route": route,
        "route_label": BACKTEST_REALISM_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("BACKTEST_REALISM_", ""),
        "conclusion": conclusion,
        "next_action": next_action,
        "cost_model_contract": cost_model_contract,
        "net_cost_curve_contract": net_cost_curve_contract,
        "turnover_evidence_contract": turnover_evidence_contract,
        "liquidity_capacity_contract": liquidity_capacity_contract,
        "rows": rows,
        "metrics": {
            "ready_rows": status_counts["PASS"],
            "total_rows": len(rows),
            "pass": status_counts["PASS"],
            "review": status_counts["REVIEW"],
            "needs_input": status_counts["NEEDS_INPUT"],
            "blocked": status_counts["BLOCKED"],
        },
        "execution_boundary": {
            "write_policy": "read_only_backtest_realism_audit",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "BACKTEST_REALISM_AUDIT_SCHEMA_VERSION",
    "BACKTEST_REALISM_READY",
    "BACKTEST_REALISM_REVIEW",
    "BACKTEST_REALISM_NEEDS_INPUT",
    "BACKTEST_REALISM_BLOCKED",
    "build_cost_model_source_contract",
    "build_net_cost_curve_contract",
    "build_turnover_evidence_contract",
    "build_liquidity_capacity_contract",
    "build_backtest_realism_audit",
]
