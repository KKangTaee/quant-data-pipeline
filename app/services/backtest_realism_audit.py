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


def _turnover_row(validation: dict[str, Any], source: dict[str, Any]) -> dict[str, Any]:
    avg_turnover = _first_non_none(_first_float(source, "avg_turnover"), _first_float(validation, "avg_turnover"))
    max_turnover = _first_non_none(_first_float(source, "max_turnover"), _first_float(validation, "max_turnover"))
    rebalance = (
        _first_value(source, "rebalance_interval")
        or _first_value(source, "rebalance_freq")
        or _first_value(source, "factor_freq")
        or dict(dict(validation.get("selection_source_snapshot") or {}).get("construction") or {}).get("rebalance_cadence")
    )
    if avg_turnover is not None or max_turnover is not None:
        status = "PASS"
        current = f"avg={avg_turnover if avg_turnover is not None else '-'} / max={max_turnover if max_turnover is not None else '-'}"
        evidence = "turnover metadata attached"
        next_action = "turnover가 높으면 비용 민감도 sweep을 후속으로 확인합니다."
    elif rebalance:
        status = "REVIEW"
        current = f"rebalance={rebalance}"
        evidence = "rebalance cadence exists but turnover estimate missing"
        next_action = "rebalance별 turnover 추정치를 result metadata에 보강합니다."
    else:
        status = "NEEDS_INPUT"
        current = "missing"
        evidence = "turnover / rebalance metadata missing"
        next_action = "turnover 또는 rebalance cadence evidence를 보강합니다."
    return _row(
        criteria="Turnover evidence",
        status=status,
        current=current,
        evidence=evidence,
        next_action=next_action,
        meaning="리밸런싱과 포지션 교체 빈도가 비용과 체결 가능성에 미치는 영향을 확인합니다.",
    )


def _liquidity_row(validation: dict[str, Any]) -> dict[str, Any]:
    diagnostic = _find_diagnostic(validation, "operability_cost_liquidity")
    provider = _provider_operability(validation)
    provider_status = provider.get("diagnostic_status") or diagnostic.get("status")
    status = _status(provider_status)
    if status == "PASS":
        evidence = provider.get("summary") or diagnostic.get("summary") or "provider operability PASS"
        next_action = "추가 조치 없음"
    elif status == "REVIEW":
        evidence = provider.get("summary") or diagnostic.get("summary") or "operability review"
        next_action = "expense / AUM / ADV / spread / premium-discount gap을 확인합니다."
    elif status == "BLOCKED":
        evidence = provider.get("summary") or diagnostic.get("summary") or "operability blocked"
        next_action = "가격 / provider blocker를 먼저 해소합니다."
    else:
        evidence = provider.get("summary") or diagnostic.get("summary") or "provider operability missing"
        next_action = "ETF operability / liquidity provider snapshot을 보강합니다."
    coverage_weight = provider.get("coverage_weight")
    return _row(
        criteria="Liquidity / operability evidence",
        status=status,
        current=f"{provider_status or 'NOT_RUN'} / coverage={coverage_weight if coverage_weight is not None else '-'}",
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
    rows = [
        _transaction_cost_row(validation, evidence_root, cost_model_contract),
        _turnover_row(validation, evidence_root),
        _liquidity_row(validation),
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
    "build_backtest_realism_audit",
]
