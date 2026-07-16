"""Normalize Practical Validation evidence into root-level closure issues.

This service is Streamlit-free and read-only. Audit/module rows remain available
as derived checks, while Final Review consumes one issue per root cause.
"""

from __future__ import annotations

from typing import Any

import pandas as pd


EVIDENCE_CLOSURE_SCHEMA_VERSION = "backtest_evidence_closure_v1"

ACTION_HANDLER_CONTRACTS = {
    "run_practical_validation_replay": {
        "owner_stage": "practical_validation",
        "handler": (
            "app.web.backtest_practical_validation.page:"
            "_execute_practical_validation_replay"
        ),
    },
    "run_practical_validation_provider_gap_collection": {
        "owner_stage": "practical_validation",
        "handler": (
            "app.web.backtest_practical_validation.page:"
            "_execute_practical_validation_provider_gap_collection"
        ),
    },
}

_RESOLUTION_ACTION_LABELS = {
    "validated_caution": "Level2에서 검증 완료",
    "resolve_now": "지금 해결",
    "engineering_required": "개발 후 재검토",
    "accepted_limit": "Final Review에서 한계 인수",
    "final_decision": "Final Review에서 판단",
    "monitoring_transfer": "Monitoring 조건으로 이관",
}

_TERMINAL_STATE_LABELS = {
    "open": "미정",
    "resolved": "해결됨",
    "accepted": "한계 인수",
    "monitoring_transferred": "Monitoring 이관",
    "deferred": "개발 후 재검토",
    "blocked": "차단됨",
}

_PASS_STATUSES = {"PASS", "READY", "OK", "NOT_APPLICABLE"}
_KNOWN_MODULE_ROOTS = {
    "source_integrity": "source_integrity",
    "benchmark_parity": "benchmark_comparator_parity",
    "validation_efficacy": "validation_method_strength",
    "construction_risk": "construction_risk",
    "backtest_realism": "backtest_realism",
    "stress_robustness": "stress_robustness",
    "provider_investability": "provider_investability",
    "leverage_inverse": "leverage_inverse_suitability",
    "risk_contribution": "risk_contribution",
    "component_role_weight": "component_role_weight",
    "macro_regime": "macro_regime_fit",
    "monitoring_baseline": "monitoring_baseline",
    "tax_account_scope": "tax_account_scope",
    "selected_route_preflight": "selected_route_preflight",
    "pre_final_data_enrichment": "pre_final_data_enrichment",
    "pre_final_data_contract": "pre_final_data_contract",
}


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _optional_int(value: Any) -> int | None:
    if value is None:
        return None
    try:
        return int(value)
    except (TypeError, ValueError):
        return None


def _status(value: Any) -> str:
    return str(value or "").strip().upper()


def _is_non_pass(value: Any) -> bool:
    status = _status(value)
    return bool(status) and status not in _PASS_STATUSES


def has_action_handler(action_id: Any) -> bool:
    """Return whether an action is backed by a registered Python handler."""

    return str(action_id or "").strip() in ACTION_HANDLER_CONTRACTS


def normalize_evidence_issue(issue: dict[str, Any]) -> dict[str, Any]:
    """Normalize actionability without turning an unimplemented intent into a CTA."""

    normalized = dict(issue or {})
    resolution_class = str(normalized.get("resolution_class") or "engineering_required").strip()
    terminal_state = str(normalized.get("terminal_state") or "open").strip()
    action_id = str(normalized.get("action_id") or "").strip() or None
    if resolution_class == "resolve_now" and not has_action_handler(action_id):
        resolution_class = "engineering_required"
        action_id = None
        normalized["gate_effect"] = "block_final_review"
        normalized["owner_stage"] = "development"
        if terminal_state == "open":
            terminal_state = "deferred"

    normalized.update(
        {
            "resolution_class": resolution_class,
            "terminal_state": terminal_state,
            "action_id": action_id,
            "actionable_now": (
                resolution_class == "resolve_now"
                and terminal_state == "open"
                and has_action_handler(action_id)
            ),
            "action_label": _RESOLUTION_ACTION_LABELS.get(
                resolution_class,
                "개발 후 재검토",
            ),
            "terminal_state_label": _TERMINAL_STATE_LABELS.get(terminal_state, terminal_state),
        }
    )
    return normalized


def _module_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    rows = validation.get("validation_modules") or validation.get("validation_module_display_rows") or []
    return [dict(row) for row in list(rows) if isinstance(row, dict)]


def _module_id(row: dict[str, Any]) -> str:
    return str(row.get("module_id") or row.get("Module") or "").strip()


def _audit_rows(validation: dict[str, Any], key: str) -> list[dict[str, Any]]:
    payload = dict(validation.get(key) or {})
    return [dict(row) for row in list(payload.get("rows") or []) if isinstance(row, dict)]


def _audit_row(validation: dict[str, Any], criteria: str) -> dict[str, Any]:
    return next(
        (
            row
            for row in _audit_rows(validation, "data_coverage_audit")
            if str(row.get("Criteria") or "").strip() == criteria
        ),
        {},
    )


def build_latest_replay_evidence(validation: dict[str, Any]) -> dict[str, Any]:
    """Read stored replay provenance without inventing a new threshold."""

    curve = dict(validation.get("curve_evidence") or {})
    provenance = dict(curve.get("curve_provenance") or {})
    period = dict(curve.get("period_coverage") or provenance.get("period_coverage") or {})
    market_date_contract = dict(
        provenance.get("market_date_contract")
        or period.get("market_date_contract")
        or {}
    )
    requested_period = dict(period.get("requested_period") or {})
    actual_period = dict(period.get("actual_period") or {})
    return {
        "requested_market_date": _date_text(
            period.get("requested_market_date")
            or market_date_contract.get("requested_market_date")
            or provenance.get("requested_market_date")
            or requested_period.get("end")
        ),
        "latest_common_price_date": _date_text(
            period.get("latest_common_price_date")
            or market_date_contract.get("latest_common_price_date")
            or provenance.get("latest_common_price_date")
        ),
        "last_complete_rebalance_date": _date_text(
            period.get("last_complete_rebalance_date")
            or market_date_contract.get("last_complete_rebalance_date")
            or provenance.get("last_complete_rebalance_date")
        ),
        "latest_valuation_date": _date_text(
            period.get("latest_valuation_date")
            or market_date_contract.get("latest_valuation_date")
            or provenance.get("latest_valuation_date")
        ),
        "actual_result_date": _date_text(
            period.get("actual_result_date") or actual_period.get("end")
        ),
        "end_gap_days": _optional_int(period.get("end_gap_days")),
        "runtime_status": _status(
            provenance.get("runtime_recheck_status")
            or dict(curve.get("replay_attempt") or {}).get("status")
        ),
        "period_status": _status(
            provenance.get("period_coverage_status") or period.get("status")
        ),
        "source": str(
            curve.get("portfolio_curve_source")
            or provenance.get("portfolio_curve_source")
            or "stored_curve_provenance"
        ),
        "limiting_symbols": list(
            period.get("limiting_symbols")
            or market_date_contract.get("limiting_symbols")
            or provenance.get("limiting_symbols")
            or []
        ),
    }


def _base_issue(
    *,
    root_issue_id: str,
    title: str,
    observed: str,
    expected: str,
    cause: str,
    derived_checks: list[str],
    resolution_class: str,
    owner_stage: str,
    actionable_now: bool,
    action_id: str | None,
    completion_criteria: str,
    applicability: str,
    criticality: str,
    gate_effect: str,
    terminal_state: str = "open",
    period: dict[str, Any] | None = None,
    measurement: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "root_issue_id": root_issue_id,
        "title": title,
        "observed": observed,
        "expected": expected,
        "cause": cause,
        "derived_checks": list(derived_checks),
        "resolution_class": resolution_class,
        "owner_stage": owner_stage,
        "actionable_now": actionable_now,
        "action_id": action_id,
        "completion_criteria": completion_criteria,
        "applicability": applicability,
        "criticality": criticality,
        "gate_effect": gate_effect,
        "accepted_reason": None,
        "monitoring_condition": None,
        "terminal_state": terminal_state,
        "period": dict(period or {}),
        "measurement": dict(measurement or {}),
        "score_impact": 0,
    }


def _replay_issue(validation: dict[str, Any], modules: dict[str, dict[str, Any]]) -> dict[str, Any] | None:
    replay_module = modules.get("latest_replay") or {}
    pit_row = _audit_row(validation, "PIT price window coverage")
    if not _is_non_pass(replay_module.get("status") or replay_module.get("Status")) and not _is_non_pass(
        pit_row.get("Status")
    ):
        return None
    period = build_latest_replay_evidence(validation)
    requested = period.get("requested_market_date") or "-"
    actual = period.get("actual_result_date") or "-"
    gap = period.get("end_gap_days")
    gap_text = f"{gap}일 gap" if gap is not None else "gap 미확인"
    requested_date = pd.to_datetime(
        period.get("requested_market_date"),
        errors="coerce",
    )
    latest_common_date = pd.to_datetime(
        period.get("latest_common_price_date"),
        errors="coerce",
    )
    last_complete_date = pd.to_datetime(
        period.get("last_complete_rebalance_date"),
        errors="coerce",
    )
    latest_valuation_date = pd.to_datetime(
        period.get("latest_valuation_date"),
        errors="coerce",
    )
    actual_result_date = pd.to_datetime(
        period.get("actual_result_date"),
        errors="coerce",
    )
    requested_month = (
        requested_date.to_period("M")
        if not pd.isna(requested_date)
        else None
    )
    last_complete_month = (
        last_complete_date.to_period("M")
        if not pd.isna(last_complete_date)
        else None
    )
    latest_common_month = (
        latest_common_date.to_period("M")
        if not pd.isna(latest_common_date)
        else None
    )
    latest_valuation_month = (
        latest_valuation_date.to_period("M")
        if not pd.isna(latest_valuation_date)
        else None
    )
    actual_result_month = (
        actual_result_date.to_period("M")
        if not pd.isna(actual_result_date)
        else None
    )
    partial_month_proven = (
        not pd.isna(requested_date)
        and not pd.isna(latest_common_date)
        and not pd.isna(last_complete_date)
        and not pd.isna(latest_valuation_date)
        and not pd.isna(actual_result_date)
        and gap is not None
        and 0 <= gap <= 31
        and last_complete_month == requested_month - 1
        and latest_common_month in {last_complete_month, requested_month}
        and latest_valuation_month == requested_month
        and actual_result_month == last_complete_month
        and actual_result_date == last_complete_date
        and latest_common_date >= last_complete_date - pd.Timedelta(days=7)
        and latest_common_date <= latest_valuation_date
        and last_complete_date < latest_valuation_date <= requested_date
        and last_complete_date < requested_date
    )
    derived = []
    if replay_module:
        derived.append("latest_replay")
    if pit_row:
        derived.append("pit_price_window_coverage")
    if partial_month_proven:
        latest_valuation = period.get("latest_valuation_date") or "-"
        last_complete = period.get("last_complete_rebalance_date") or "-"
        return _base_issue(
            root_issue_id="replay_period_coverage",
            title="월중 최신 평가와 완결 리밸런싱 구분",
            observed=(
                f"요청 {requested} / 완결 리밸런싱 {last_complete} / "
                f"최신 평가 {latest_valuation}"
            ),
            expected="완결 리밸런싱과 월중 valuation 근거를 분리해 저장",
            cause="partial-month valuation after the last complete rebalance",
            derived_checks=derived,
            resolution_class="monitoring_transfer",
            owner_stage="final_review",
            actionable_now=False,
            action_id=None,
            completion_criteria=(
                "Final Review에서 최신 평가일과 다음 완결 리밸런싱 확인 조건을 "
                "Monitoring handoff로 기록합니다."
            ),
            applicability="partial_month_monitoring",
            criticality="noncritical",
            gate_effect="final_review_closure",
            period=period,
        )
    return _base_issue(
        root_issue_id="replay_period_coverage",
        title="최신 재검증 기간 충족 여부",
        observed=f"요청 {requested} / 실제 {actual} / {gap_text}",
        expected="latest common price date까지 설명 가능한 runtime period contract 확보",
        cause="completed replay still has an unexplained period gap",
        derived_checks=derived,
        resolution_class="engineering_required",
        owner_stage="development",
        actionable_now=False,
        action_id=None,
        completion_criteria=(
            "같은 replay 재실행으로 해결되지 않는 기간 gap 원인을 보강하고 "
            "새 validation에서 period coverage PASS를 저장합니다."
        ),
        applicability="required",
        criticality="critical",
        gate_effect="block_final_review",
        terminal_state="deferred",
        period=period,
    )


def _historical_universe_issue(validation: dict[str, Any]) -> dict[str, Any] | None:
    audit = dict(validation.get("data_coverage_audit") or {})
    universe_contract = dict(audit.get("universe_contract") or {})
    listing = _audit_row(validation, "Universe / listing evidence")
    survivorship = _audit_row(validation, "Survivorship / delisting control")
    if not _is_non_pass(listing.get("Status")) and not _is_non_pass(survivorship.get("Status")):
        return None
    derived = []
    if listing:
        derived.append("universe_listing_evidence")
    if survivorship:
        derived.append("survivorship_delisting_control")
    evidence = " / ".join(
        str(row.get("Current") or row.get("Evidence") or "-")
        for row in (listing, survivorship)
        if row
    )
    dynamic_historical = (
        universe_contract.get("mode") == "dynamic_historical"
        or bool(universe_contract.get("requires_pit_membership"))
    )
    return _base_issue(
        root_issue_id="historical_universe_coverage",
        title="과거 universe와 상장폐지 반영 범위",
        observed=evidence or "historical universe evidence missing",
        expected="universe 적용 방식에 맞는 lifecycle / survivorship evidence",
        cause="historical lifecycle coverage",
        derived_checks=derived,
        resolution_class="engineering_required" if dynamic_historical else "accepted_limit",
        owner_stage="development" if dynamic_historical else "final_review",
        actionable_now=False,
        action_id=None,
        completion_criteria="static/dynamic universe applicability에 맞는 종결 상태 저장",
        applicability=str(universe_contract.get("mode") or "pending_universe_contract"),
        criticality="critical" if dynamic_historical else "noncritical",
        gate_effect="block_final_review" if dynamic_historical else "final_review_closure",
        terminal_state="deferred" if dynamic_historical else "open",
    )


def _generic_module_issue(module: dict[str, Any]) -> dict[str, Any] | None:
    module_id = _module_id(module)
    if not module_id or module_id in {"latest_replay", "data_coverage"}:
        return None
    status = module.get("status") or module.get("Status") or module.get("Current")
    if not _is_non_pass(status):
        return None
    requirement = str(module.get("requirement") or module.get("Requirement") or "").upper()
    role = str(module.get("review_role") or "")
    evidence_state = str(module.get("evidence_state") or "missing").strip().lower()
    explicit_resolution_class = str(
        module.get("resolution_class") or ""
    ).strip()
    known_root = _KNOWN_MODULE_ROOTS.get(module_id)
    if not known_root and requirement == "REQUIRED":
        return _base_issue(
            root_issue_id=f"missing_contract:{module_id}",
            title=str(module.get("label") or module.get("Module") or module_id),
            observed=f"{_status(status) or 'REVIEW'} / required trace adapter missing",
            expected="required module evidence adapter",
            cause="product contract missing",
            derived_checks=[module_id],
            resolution_class="engineering_required",
            owner_stage="development",
            actionable_now=False,
            action_id=None,
            completion_criteria="adapter 구현 후 새 validation 저장",
            applicability="required",
            criticality="critical",
            gate_effect="block_final_review",
            terminal_state="deferred",
        )
    if not known_root:
        return None
    action_id = str(module.get("action_id") or "").strip() or None
    if (
        explicit_resolution_class == "accepted_limit"
        and evidence_state in {"computed", "observed", "verified"}
    ):
        resolution_class = "accepted_limit"
        owner_stage = "final_review"
        criticality = "noncritical"
        gate_effect = "final_review_closure"
        terminal_state = "open"
    elif role == "final_readiness_blocker":
        if has_action_handler(action_id):
            resolution_class = "resolve_now"
            owner_stage = "practical_validation"
            criticality = "critical"
            gate_effect = "block_final_review"
        else:
            resolution_class = "engineering_required"
            owner_stage = "development"
            criticality = "critical"
            gate_effect = "block_final_review"
            action_id = None
        terminal_state = (
            "open"
            if resolution_class == "resolve_now"
            else "deferred"
        )
    elif role == "monitoring_followup":
        resolution_class = "monitoring_transfer"
        owner_stage = "final_review"
        criticality = "noncritical"
        gate_effect = "final_review_closure"
        terminal_state = "open"
    elif role == "final_decision_input":
        resolution_class = "final_decision"
        owner_stage = "final_review"
        criticality = "noncritical"
        gate_effect = "final_review_closure"
        terminal_state = "open"
    elif role in {"pv_data_caution", "pv_practical_caution"}:
        if evidence_state in {"computed", "observed", "verified"}:
            resolution_class = "validated_caution"
            owner_stage = "practical_validation"
            criticality = "noncritical"
            gate_effect = "level2_resolved"
            terminal_state = "resolved"
        else:
            resolution_class = "engineering_required"
            owner_stage = "development"
            criticality = "critical"
            gate_effect = "block_final_review"
            action_id = None
            terminal_state = "deferred"
    else:
        resolution_class = "engineering_required"
        owner_stage = "development"
        criticality = "critical"
        gate_effect = "block_final_review"
        action_id = None
        terminal_state = "deferred"
    return _base_issue(
        root_issue_id=known_root,
        title=str(module.get("label") or module.get("Module") or module_id),
        observed=str(module.get("reason") or module.get("Reason") or status),
        expected=str(module.get("resolution_action") or module.get("Next Action") or "explicit closure"),
        cause=f"validation module {module_id}",
        derived_checks=[module_id],
        resolution_class=resolution_class,
        owner_stage=owner_stage,
        actionable_now=resolution_class == "resolve_now",
        action_id=action_id,
        completion_criteria=str(module.get("completion_criteria") or "").strip()
        or (
            "Level2 계산 / 관측 근거와 주의 판정을 저장함"
            if resolution_class == "validated_caution"
            else (
                "required validator 또는 evidence adapter 구현 후 새 validation 저장"
                if resolution_class == "engineering_required"
                else "Final Review route/reason or Monitoring condition records terminal state"
            )
        ),
        applicability=str(module.get("applicability") or "module_applies"),
        criticality=criticality,
        gate_effect=gate_effect,
        terminal_state=terminal_state,
        measurement=dict(module.get("measurement") or {}),
    )


def _merge_root_issues(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    merged: dict[str, dict[str, Any]] = {}
    order: list[str] = []
    for candidate in candidates:
        root_issue_id = str(candidate.get("root_issue_id") or "").strip()
        if not root_issue_id:
            continue
        if root_issue_id not in merged:
            merged[root_issue_id] = dict(candidate)
            order.append(root_issue_id)
            continue
        current = merged[root_issue_id]
        current["derived_checks"] = list(
            dict.fromkeys(
                [*list(current.get("derived_checks") or []), *list(candidate.get("derived_checks") or [])]
            )
        )
    return [normalize_evidence_issue(merged[root_issue_id]) for root_issue_id in order]


def _closure_summary(issues: list[dict[str, Any]]) -> dict[str, int]:
    resolution_counts = {
        resolution_class: sum(
            1
            for issue in issues
            if issue.get("resolution_class") == resolution_class
        )
        for resolution_class in (
            "validated_caution",
            "resolve_now",
            "engineering_required",
            "accepted_limit",
            "final_decision",
            "monitoring_transfer",
        )
    }
    unresolved_actionable_count = sum(
        1
        for issue in issues
        if issue.get("actionable_now") and issue.get("terminal_state") == "open"
    )
    critical_engineering_count = sum(
        1
        for issue in issues
        if issue.get("resolution_class") == "engineering_required"
        and issue.get("criticality") == "critical"
        and issue.get("terminal_state") not in {"resolved", "accepted", "monitoring_transferred"}
    )
    missing_contract_count = sum(
        1 for issue in issues if str(issue.get("root_issue_id") or "").startswith("missing_contract:")
    )
    return {
        "total": len(issues),
        "unresolved_actionable_count": unresolved_actionable_count,
        "critical_engineering_count": critical_engineering_count,
        "missing_contract_count": missing_contract_count,
        "validated_caution_count": resolution_counts["validated_caution"],
        "resolve_now_count": resolution_counts["resolve_now"],
        "engineering_required_count": resolution_counts["engineering_required"],
        "accepted_limit_count": resolution_counts["accepted_limit"],
        "final_decision_count": resolution_counts["final_decision"],
        "monitoring_transfer_count": resolution_counts["monitoring_transfer"],
    }


def is_current_final_review_eligible(contract: dict[str, Any]) -> bool:
    """Require every Level 2 actionable or engineering state to be terminal."""

    summary = dict(contract.get("summary") or {})
    return (
        int(summary.get("unresolved_actionable_count") or 0) == 0
        and int(summary.get("critical_engineering_count") or 0) == 0
        and int(summary.get("missing_contract_count") or 0) == 0
    )


def finalize_evidence_closure(
    contract: dict[str, Any],
    *,
    decision_route: str,
    operator_reason: str,
) -> dict[str, Any]:
    """Project Final Review judgment into terminal root-issue states."""

    snapshot = dict(contract or {})
    route = str(decision_route or "").strip()
    reason = str(operator_reason or "").strip()
    selected = route == "SELECT_FOR_PRACTICAL_PORTFOLIO"
    hold_routes = {"HOLD_FOR_MORE_PAPER_TRACKING", "RE_REVIEW_REQUIRED"}
    reject = route == "REJECT_FOR_PRACTICAL_USE"
    issues: list[dict[str, Any]] = []
    for raw_issue in list(snapshot.get("issues") or []):
        issue = normalize_evidence_issue(dict(raw_issue or {}))
        terminal_state = str(issue.get("terminal_state") or "open")
        if terminal_state in {"resolved", "accepted", "monitoring_transferred", "blocked"}:
            issues.append(issue)
            continue
        resolution_class = str(issue.get("resolution_class") or "")
        if selected and resolution_class in {"accepted_limit", "final_decision"}:
            issue["terminal_state"] = "accepted"
            issue["terminal_state_label"] = _TERMINAL_STATE_LABELS["accepted"]
            issue["accepted_reason"] = reason
        elif selected and resolution_class == "monitoring_transfer":
            issue["terminal_state"] = "monitoring_transferred"
            issue["terminal_state_label"] = _TERMINAL_STATE_LABELS["monitoring_transferred"]
            issue["monitoring_condition"] = str(
                issue.get("monitoring_condition")
                or issue.get("completion_criteria")
                or reason
            ).strip()
        elif route in hold_routes:
            issue["terminal_state"] = "deferred"
            issue["terminal_state_label"] = _TERMINAL_STATE_LABELS["deferred"]
            issue["accepted_reason"] = reason
        elif reject:
            issue["terminal_state"] = "blocked"
            issue["terminal_state_label"] = _TERMINAL_STATE_LABELS["blocked"]
            issue["accepted_reason"] = reason
        issues.append(issue)

    terminal_state_counts = {
        state: sum(1 for issue in issues if issue.get("terminal_state") == state)
        for state in _TERMINAL_STATE_LABELS
    }
    open_count = sum(
        1
        for issue in issues
        if issue.get("terminal_state") == "open"
        and issue.get("resolution_class") in {"resolve_now", "engineering_required", "accepted_limit", "final_decision", "monitoring_transfer"}
    )
    selection_blocker_count = sum(
        1
        for issue in issues
        if issue.get("resolution_class") in {"resolve_now", "engineering_required"}
        and issue.get("terminal_state") not in {"resolved", "accepted", "monitoring_transferred"}
    )
    snapshot.update(
        {
            "issues": issues,
            "decision_route": route,
            "terminal_state_counts": terminal_state_counts,
            "accepted_limit_summary": [
                str(issue.get("title") or issue.get("root_issue_id") or "")
                for issue in issues
                if issue.get("terminal_state") == "accepted"
            ],
            "monitoring_conditions": [
                str(issue.get("monitoring_condition") or "")
                for issue in issues
                if issue.get("terminal_state") == "monitoring_transferred"
                and str(issue.get("monitoring_condition") or "").strip()
            ],
            "decision_reason_summary": reason,
            "open_count": open_count,
            "selection_blocker_count": selection_blocker_count,
            "boundary": {
                **dict(snapshot.get("boundary") or {}),
                "provider_fetch": False,
                "validation_rerun": False,
                "registry_write": False,
            },
        }
    )
    return snapshot


def build_evidence_closure_contract(validation: dict[str, Any]) -> dict[str, Any]:
    """Build one closure issue per root cause from stored validation evidence."""

    validation_row = dict(validation or {})
    module_list = _module_rows(validation_row)
    modules = {_module_id(row): row for row in module_list if _module_id(row)}
    candidates: list[dict[str, Any]] = []
    replay_issue = _replay_issue(validation_row, modules)
    if replay_issue:
        candidates.append(replay_issue)
    universe_issue = _historical_universe_issue(validation_row)
    if universe_issue:
        candidates.append(universe_issue)
    candidates.extend(
        issue
        for issue in (_generic_module_issue(module) for module in module_list)
        if issue is not None
    )
    issues = _merge_root_issues(candidates)
    summary = _closure_summary(issues)
    contract = {
        "schema_version": EVIDENCE_CLOSURE_SCHEMA_VERSION,
        "validation_id": validation_row.get("validation_id"),
        "selection_source_id": validation_row.get("selection_source_id"),
        "issues": issues,
        "summary": summary,
        "current_final_review_eligible": False,
        "boundary": {
            "validation_rerun": False,
            "provider_fetch": False,
            "db_write": False,
            "registry_write": False,
        },
    }
    contract["current_final_review_eligible"] = is_current_final_review_eligible(contract)
    return contract


__all__ = [
    "ACTION_HANDLER_CONTRACTS",
    "EVIDENCE_CLOSURE_SCHEMA_VERSION",
    "build_evidence_closure_contract",
    "build_latest_replay_evidence",
    "finalize_evidence_closure",
    "has_action_handler",
    "is_current_final_review_eligible",
    "normalize_evidence_issue",
]
