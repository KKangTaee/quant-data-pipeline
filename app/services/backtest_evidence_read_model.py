from __future__ import annotations

from typing import Any

from app.services.backtest_component_role_weight_audit import build_component_role_weight_audit
from app.services.backtest_construction_risk_audit import build_construction_risk_audit
from app.services.backtest_data_coverage_audit import build_data_coverage_audit
from app.services.backtest_realism_audit import build_backtest_realism_audit
from app.services.backtest_risk_contribution_audit import build_risk_contribution_audit
from app.services.backtest_validation_efficacy import build_validation_efficacy_audit


SELECT_FOR_PRACTICAL_PORTFOLIO = "SELECT_FOR_PRACTICAL_PORTFOLIO"
DECISION_DOSSIER_SCHEMA_VERSION = "decision_dossier_v1"
DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION = "selected_decision_source_consistency_v1"
CANDIDATE_BOARD_SCHEMA_VERSION = "final_review_candidate_board_v1"
DECISION_RECORD_GUIDE_SCHEMA_VERSION = "final_review_decision_record_guide_v1"
SAVED_DECISION_REVIEW_SCHEMA_VERSION = "final_review_saved_decision_review_v1"

FINAL_REVIEW_DECISION_LABELS = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "실전 검토 통과 후보",
    "HOLD_FOR_MORE_PAPER_TRACKING": "내용 부족 / 관찰 필요",
    "REJECT_FOR_PRACTICAL_USE": "투자하면 안 됨",
    "RE_REVIEW_REQUIRED": "재검토 필요",
}
FINAL_REVIEW_STATUS_DISPLAY = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: {
        "route": "FINAL_REVIEW_DECISION_COMPLETE",
        "verdict": "최종 판단 완료: 실전 검토 통과 후보로 선정됨",
        "next_action": "이 기록은 투자 후보 선정 판단입니다. 실제 투자 금액, 리밸런싱, 주문 승인 여부는 별도 운영 / 승인 단계에서 사용자가 결정합니다.",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "route": "FINAL_REVIEW_HOLD_FOR_MORE_OBSERVATION",
        "verdict": "최종 판단 보류: 내용 부족 / 추가 관찰 필요",
        "next_action": "추가 paper observation이나 근거 보강 후 Final Review에서 다시 판단합니다.",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "route": "FINAL_REVIEW_REJECTED",
        "verdict": "최종 판단 완료: 실전 후보에서 제외됨",
        "next_action": "필요하면 후보 탐색, Compare, Portfolio Proposal 단계로 되돌아갑니다.",
    },
    "RE_REVIEW_REQUIRED": {
        "route": "FINAL_REVIEW_REVIEW_REQUIRED",
        "verdict": "최종 판단 재검토 필요: 구성 / 비중 / 검증 근거를 다시 확인",
        "next_action": "구성, 비중, validation, robustness, paper observation 근거를 보강한 뒤 Final Review에서 다시 판단합니다.",
    },
}
FINAL_REVIEW_DECISION_RECORD_TEMPLATES = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: {
        "reason": "Decision Cockpit과 investability gate가 선정 가능 상태이며, 남은 blocker 없이 실전 검토 통과 후보로 기록한다.",
        "constraints": "실제 투자 전 투입 금액, 리밸런싱 규칙, 중단 / 재검토 기준, 세금 / 계좌 조건은 별도로 확인한다.",
        "next_action": "Selected Portfolio Dashboard에서 read-only monitoring / recheck 기준을 확인한다.",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "reason": "critical blocker는 아니지만 review-required evidence나 관찰 공백이 남아 있어 선정 전 추가 paper tracking이 필요하다.",
        "constraints": "관찰 기간, benchmark, review trigger, 보강할 evidence row를 명시하고 선정 판단은 보류한다.",
        "next_action": "추가 관찰 또는 evidence 보강 후 Final Review에서 다시 판단한다.",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "reason": "현재 검증 근거와 gate evidence로는 실전 후보로 사용하기 어렵다고 판단한다.",
        "constraints": "동일 source를 다시 검토하려면 blocker 해소나 후보 재구성이 먼저 필요하다.",
        "next_action": "필요하면 Backtest Analysis, Practical Validation, Portfolio Mix 단계로 돌아가 새 후보를 만든다.",
    },
    "RE_REVIEW_REQUIRED": {
        "reason": "구성, 비중, 검증 근거, 데이터 상태 중 최종 판단 전에 다시 검토해야 할 항목이 남아 있다.",
        "constraints": "재검토 대상 evidence row와 보강 책임 범위를 남기고 선정 route로 저장하지 않는다.",
        "next_action": "구성 / 비중 / validation / provider / robustness evidence를 보강한 뒤 Final Review에서 재검토한다.",
    },
}
FINAL_REVIEW_SAVED_DECISION_FILTER_OPTIONS = (
    "All",
    "Selected",
    "Hold",
    "Reject",
    "Re-review",
    "Unknown",
)
GATE_POLICY_SCHEMA_VERSION = "investability_gate_policy_v1"
SELECTION_GATE_POLICY_SCHEMA_VERSION = "final_review_selection_gate_policy_v1"
DEPLOYMENT_READINESS_GATE_POLICY_SCHEMA_VERSION = "deployment_readiness_gate_policy_v1"
GATE_POLICY_MODE_SELECTION = "selection_readiness"
GATE_POLICY_MODE_DEPLOYMENT = "deployment_readiness"
GATE_POLICY_GROUP_LABELS = {
    "data_trust": "Data Trust / Source Contract",
    "benchmark": "Benchmark / Comparator Parity",
    "provider_coverage": "Provider / Look-through",
    "stress_robustness": "Stress / Robustness",
    "leveraged_inverse": "Leveraged / Inverse Suitability",
    "paper_observation": "Paper Observation",
    "final_review_evidence": "Final Review Evidence",
    "validation_efficacy": "Validation Efficacy",
    "data_coverage": "Data Coverage",
    "construction_risk": "Construction Risk",
    "risk_contribution": "Risk Contribution",
    "component_role_weight": "Component Role / Weight",
    "backtest_realism": "Backtest Realism",
}
GATE_POLICY_GROUP_ACTIONS = {
    "data_trust": "원본 source, 가격, 비중, Data Trust blocker를 먼저 해소합니다.",
    "benchmark": "같은 기간 / frequency / coverage의 benchmark parity를 보강합니다.",
    "provider_coverage": "ETF 운용성 / holdings / exposure / macro coverage를 actual evidence로 보강합니다.",
    "stress_robustness": "stress, rolling, sensitivity, overfit evidence를 실행 가능한 근거로 보강합니다.",
    "leveraged_inverse": "leveraged / inverse 노출 목적, 보유 기간, 위험 한계를 명시합니다.",
    "paper_observation": "관찰 benchmark, active component, review trigger를 보강합니다.",
    "final_review_evidence": "Final Review evidence route가 ready가 되도록 validation / robustness / observation blocker를 해소합니다.",
    "validation_efficacy": "runtime replay, benchmark parity, walk-forward / OOS / regime, provider freshness, robustness, PIT / survivorship evidence gap을 보강합니다.",
    "data_coverage": "DB price window, provider freshness, PIT replay, universe / survivorship evidence gap을 보강합니다.",
    "construction_risk": "component weight, provider look-through coverage, top holding / overlap, asset exposure evidence gap을 보강합니다.",
    "risk_contribution": "component return matrix, correlation, risk contribution, drop-one dependency evidence gap을 보강합니다.",
    "component_role_weight": "component role source, profile intent, target weight, weight rationale evidence gap을 보강합니다.",
    "backtest_realism": "거래비용, turnover, liquidity, net performance, tax/account scope 같은 실전성 근거를 보강합니다.",
}
GATE_POLICY_DOMAIN_GROUPS = {
    "input_evidence_layer": "data_trust",
    "asset_allocation_fit": "provider_coverage",
    "concentration_overlap_exposure": "construction_risk",
    "correlation_diversification_risk_contribution": "risk_contribution",
    "regime_macro_suitability": "provider_coverage",
    "sentiment_risk_on_off_overlay": "provider_coverage",
    "stress_scenario_diagnostics": "stress_robustness",
    "alternative_portfolio_challenge": "benchmark",
    "leveraged_inverse_etf_suitability": "leveraged_inverse",
    "operability_cost_liquidity": "provider_coverage",
    "robustness_sensitivity_overfit": "stress_robustness",
    "monitoring_baseline_seed": "paper_observation",
}
GATE_POLICY_SECTION_GROUPS = {
    "source chain": "data_trust",
    "backtest contract / data trust": "data_trust",
    "runtime replay": "stress_robustness",
    "provider / look-through": "provider_coverage",
    "benchmark parity": "benchmark",
    "robustness / stress": "stress_robustness",
    "paper observation": "paper_observation",
    "critical gaps": "final_review_evidence",
    "validation efficacy audit": "validation_efficacy",
    "data coverage audit": "data_coverage",
    "construction risk audit": "construction_risk",
    "risk contribution audit": "risk_contribution",
    "component role / weight audit": "component_role_weight",
    "backtest realism audit": "backtest_realism",
}
GATE_POLICY_CRITICAL_GROUPS_BY_PROFILE = {
    "conservative_defensive": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "paper_observation",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "balanced_core": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "paper_observation",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "growth_aggressive": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "hedged_tactical": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "custom": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "paper_observation",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
}
GATE_POLICY_REVIEW_GROUPS_BY_PROFILE = {
    "growth_aggressive": {"paper_observation"},
    "hedged_tactical": {"paper_observation"},
}
_POLICY_SEVERITY_RANK = {
    "PASS": 0,
    "WATCH": 1,
    "REVIEW_REQUIRED": 2,
    "BLOCK": 3,
}
_SELECTION_STATUS_BLOCKING_GROUPS = {
    "data_trust",
    "benchmark",
    "stress_robustness",
    "paper_observation",
    "final_review_evidence",
    "leveraged_inverse",
}
_SELECTION_VALIDATION_EFFICACY_BLOCKING_TERMS = {
    "runtime replay",
    "runtime period",
    "period coverage",
    "benchmark parity",
    "pit",
    "look-ahead",
    "lookahead",
    "survivorship",
}
_SELECTION_DATA_COVERAGE_BLOCKING_TERMS = {
    "price db window",
    "price coverage",
    "window coverage",
    "pit",
    "survivorship",
    "delisting",
}
_SELECTION_BACKTEST_REALISM_BLOCKING_TERMS = {
    "transaction cost",
    "net cost curve",
    "net performance",
    "execution boundary",
    "cost input",
    "gross",
}
_SELECTION_COMPONENT_ROLE_BLOCKING_TERMS = {
    "component role source",
    "weight rationale",
    "profile intent",
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


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _ready_from_check(check: dict[str, Any]) -> bool:
    if "Ready" in check:
        return bool(check.get("Ready"))
    return bool(check.get("ready"))


def _find_check(checks: list[dict[str, Any]], criteria: str) -> dict[str, Any]:
    criteria_key = criteria.lower()
    for check in checks:
        check_row = dict(check or {})
        label = _safe_text(check_row.get("Criteria") or check_row.get("criteria"), "").lower()
        if label == criteria_key:
            return check_row
    return {}


def _status_counts(validation: dict[str, Any]) -> dict[str, int]:
    summary = dict(validation.get("diagnostic_summary") or {})
    return dict(summary.get("status_counts") or {})


def _provider_status_summary(validation: dict[str, Any]) -> str:
    provider_context = dict(validation.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    statuses = sorted(
        {
            _safe_text(dict(item or {}).get("diagnostic_status"), "")
            for item in coverage.values()
            if isinstance(item, dict)
        }
    )
    return ", ".join([status for status in statuses if status]) or "-"


def _profile_gate_policy_sets(validation: dict[str, Any]) -> tuple[str, str, set[str], set[str]]:
    profile = dict(validation.get("validation_profile") or {})
    summary = dict(validation.get("diagnostic_summary") or {})
    profile_id = _safe_text(profile.get("profile_id") or summary.get("profile_id"), "balanced_core")
    if profile_id not in GATE_POLICY_CRITICAL_GROUPS_BY_PROFILE:
        profile_id = "balanced_core"
    profile_label = _safe_text(profile.get("profile_label") or summary.get("profile_label"), "균형형")
    critical_groups = set(GATE_POLICY_CRITICAL_GROUPS_BY_PROFILE.get(profile_id) or set())
    review_groups = set(GATE_POLICY_REVIEW_GROUPS_BY_PROFILE.get(profile_id) or set())
    return profile_id, profile_label, critical_groups, review_groups


def _policy_status_from_current(*, ready: bool, current: Any) -> str:
    text = str(current or "").strip().upper()
    if not ready:
        if not text or text == "-" or any(token in text for token in ("BLOCK", "ERROR", "MISSING", "NEEDS_INPUT", "NOT_RUN")):
            return "NOT_RUN"
        return "REVIEW"
    if any(token in text for token in ("BLOCK", "ERROR", "MISSING", "NEEDS_INPUT", "NOT_RUN")):
        return "NOT_RUN"
    if any(token in text for token in ("REVIEW", "PROXY", "BRIDGE", "STALE", "PARTIAL", "WATCH", "NEEDS_REVIEW")):
        return "REVIEW"
    return "PASS"


def _policy_severity(
    *,
    group: str,
    status: str,
    critical_groups: set[str],
    review_groups: set[str],
    policy_mode: str = GATE_POLICY_MODE_DEPLOYMENT,
    criteria: str = "",
    current: Any = "",
    evidence: Any = "",
) -> str:
    normalized = str(status or "").upper()
    if policy_mode == GATE_POLICY_MODE_SELECTION:
        return _selection_policy_severity(
            group=group,
            status=normalized,
            criteria=criteria,
            current=current,
            evidence=evidence,
        )
    if normalized in {"BLOCKED", "BLOCK", "NOT_RUN", "NEEDS_INPUT", "MISSING"}:
        return "BLOCK" if group in critical_groups else "REVIEW_REQUIRED"
    if normalized == "REVIEW":
        if group in critical_groups:
            return "REVIEW_REQUIRED"
        if group in review_groups:
            return "REVIEW_REQUIRED"
        return "WATCH"
    return "PASS"


def _text_has_any(value: str, terms: set[str]) -> bool:
    text = value.lower()
    return any(term in text for term in terms)


def _selection_policy_severity(
    *,
    group: str,
    status: str,
    criteria: str,
    current: Any,
    evidence: Any,
) -> str:
    if status in {"", "PASS", "OK", "READY"}:
        return "PASS"
    joined = " ".join(
        [
            str(criteria or ""),
            str(current or ""),
            str(evidence or ""),
        ]
    ).lower()
    if status in {"BLOCKED", "BLOCK"}:
        return "BLOCK"
    if status in {"NOT_RUN", "NEEDS_INPUT", "MISSING"}:
        if group in _SELECTION_STATUS_BLOCKING_GROUPS:
            return "BLOCK"
        if group == "validation_efficacy" and _text_has_any(joined, _SELECTION_VALIDATION_EFFICACY_BLOCKING_TERMS):
            return "BLOCK"
        if group == "data_coverage" and _text_has_any(joined, _SELECTION_DATA_COVERAGE_BLOCKING_TERMS):
            return "BLOCK"
        if group == "backtest_realism" and _text_has_any(joined, _SELECTION_BACKTEST_REALISM_BLOCKING_TERMS):
            return "BLOCK"
        if group == "component_role_weight" and _text_has_any(joined, _SELECTION_COMPONENT_ROLE_BLOCKING_TERMS):
            return "BLOCK"
        return "WATCH"
    if status == "REVIEW":
        if group == "benchmark":
            return "REVIEW_REQUIRED"
        specific_joined = " ".join([str(criteria or ""), str(current or "")]).lower()
        if group == "backtest_realism" and _text_has_any(
            specific_joined,
            {"transaction cost", "net cost curve", "net performance", "gross"},
        ):
            return "REVIEW_REQUIRED"
        return "WATCH"
    return "PASS"


def _selection_source_is_weighted_mix(validation: dict[str, Any]) -> bool:
    traits = dict(validation.get("source_traits") or {})
    if "is_weighted_mix" in traits:
        return bool(traits.get("is_weighted_mix"))
    source = dict(validation.get("selection_source_snapshot") or validation.get("source_snapshot") or {})
    construction = dict(source.get("construction") or {})
    source_kind = str(source.get("source_kind") or validation.get("source_kind") or "").lower()
    construction_source = str(construction.get("source") or "").lower()
    if "weighted" in source_kind or "mix" in construction_source:
        return True
    components = list(
        source.get("components")
        or validation.get("component_rows")
        or validation.get("selected_components")
        or []
    )
    active = [
        component
        for component in components
        if (_float_or_none(dict(component or {}).get("target_weight") or dict(component or {}).get("Weight")) or 0.0)
        > 0.0
    ]
    return len(active) > 1


def _selection_not_applicable_groups(validation: dict[str, Any]) -> set[str]:
    if _selection_source_is_weighted_mix(validation):
        return set()
    return {"risk_contribution", "component_role_weight"}


def _gate_group_from_gap(gap: dict[str, Any]) -> str:
    area = _safe_text(gap.get("Area"), "").lower()
    text = f"{area} {_safe_text(gap.get('Gap'), '').lower()}"
    if "paper" in text or "observation" in text:
        return "paper_observation"
    if "benchmark" in text:
        return "benchmark"
    if any(token in text for token in ("provider", "holding", "exposure", "operability", "macro", "liquidity")):
        return "provider_coverage"
    if any(token in text for token in ("cost", "turnover", "slippage", "execution", "tax", "account", "rebalance")):
        return "backtest_realism"
    if any(token in text for token in ("stress", "scenario", "robust", "sensitivity", "overfit", "correlation")):
        return "stress_robustness"
    if "leverag" in text or "inverse" in text:
        return "leveraged_inverse"
    if "decision evidence" in text:
        return "final_review_evidence"
    return "data_trust"


def _finding_label(group: str) -> str:
    return GATE_POLICY_GROUP_LABELS.get(group, group.replace("_", " ").title())


def _merge_policy_state(
    states: dict[str, dict[str, Any]],
    *,
    group: str,
    severity: str,
    current: Any,
    evidence: Any,
    required_action: str | None = None,
) -> None:
    if not group:
        return
    state = states.setdefault(
        group,
        {
            "group": group,
            "severity": "PASS",
            "current": [],
            "evidence": [],
            "required_action": GATE_POLICY_GROUP_ACTIONS.get(group, "근거를 보강합니다."),
        },
    )
    if _POLICY_SEVERITY_RANK.get(severity, 0) > _POLICY_SEVERITY_RANK.get(str(state.get("severity") or "PASS"), 0):
        state["severity"] = severity
        state["current"] = [item for item in state.get("current", []) if item != "PASS"]
        state["evidence"] = [item for item in state.get("evidence", []) if item != "No policy finding"]
    current_text = _safe_text(current)
    if current_text not in state["current"]:
        state["current"].append(current_text)
    evidence_text = _safe_text(evidence)
    if evidence_text not in state["evidence"]:
        state["evidence"].append(evidence_text)
    if required_action:
        state["required_action"] = required_action


def _merge_audit_rows_into_policy(
    states: dict[str, dict[str, Any]],
    *,
    audit: dict[str, Any],
    group: str,
    critical_groups: set[str],
    review_groups: set[str],
    policy_mode: str = GATE_POLICY_MODE_DEPLOYMENT,
    skipped_groups: set[str] | None = None,
) -> None:
    if group in set(skipped_groups or set()):
        return
    for raw_row in _as_list(dict(audit or {}).get("rows")):
        if not isinstance(raw_row, dict):
            continue
        row = dict(raw_row or {})
        raw_status = row.get("Status") or row.get("status")
        status = str(raw_status or "").strip().upper()
        if not status and not _ready_from_check(row):
            status = _policy_status_from_current(
                ready=False,
                current=row.get("Current") or row.get("current") or "-",
            )
        if status in {"", "PASS", "OK", "READY"}:
            continue
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=policy_mode,
            criteria=_safe_text(row.get("Criteria") or row.get("criteria"), "Audit row"),
            current=row.get("Current") or row.get("current") or status,
            evidence=row.get("Meaning") or row.get("Evidence") or row.get("evidence"),
        )
        criteria = _safe_text(row.get("Criteria") or row.get("criteria"), "Audit row")
        evidence = _safe_text(
            row.get("Meaning")
            or row.get("Evidence")
            or row.get("evidence")
            or row.get("Current")
            or row.get("current"),
            "audit evidence gap",
        )
        current = _safe_text(row.get("Current") or row.get("current") or status)
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=f"{criteria}: {status} / {current}",
            evidence=f"{criteria}: {evidence}",
            required_action=row.get("Next Action") or row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )


def build_investability_gate_policy(
    *,
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    packet_checks: list[dict[str, Any]] | None = None,
    critical_gaps: list[dict[str, Any]] | None = None,
    policy_mode: str = GATE_POLICY_MODE_DEPLOYMENT,
) -> dict[str, Any]:
    """Summarize profile-aware gate policy without persisting raw validation data."""

    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    profile_id, profile_label, critical_groups, review_groups = _profile_gate_policy_sets(validation)
    mode = policy_mode if policy_mode in {GATE_POLICY_MODE_SELECTION, GATE_POLICY_MODE_DEPLOYMENT} else GATE_POLICY_MODE_DEPLOYMENT
    skipped_groups = _selection_not_applicable_groups(validation) if mode == GATE_POLICY_MODE_SELECTION else set()
    states: dict[str, dict[str, Any]] = {}
    for group in sorted(critical_groups | review_groups):
        if group in skipped_groups:
            _merge_policy_state(
                states,
                group=group,
                severity="PASS",
                current="NOT_APPLICABLE",
                evidence="Current source traits mark this audit as not applicable for Final Review selection.",
                required_action="추가 조치 없음",
            )
            continue
        _merge_policy_state(
            states,
            group=group,
            severity="PASS",
            current="PASS",
            evidence="No policy finding",
            required_action=GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    for check in list(packet_checks or []):
        check_row = dict(check or {})
        section = _safe_text(check_row.get("Section") or check_row.get("Criteria"), "").lower()
        group = GATE_POLICY_SECTION_GROUPS.get(section)
        if not group:
            continue
        if group in skipped_groups:
            continue
        current = check_row.get("Current") or "-"
        status = _policy_status_from_current(ready=_ready_from_check(check_row), current=current)
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=mode,
            criteria=section,
            current=current,
            evidence=check_row.get("Meaning") or section,
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=current,
            evidence=check_row.get("Meaning") or section,
            required_action=GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    for diagnostic in _as_list(validation.get("diagnostic_results")):
        if not isinstance(diagnostic, dict):
            continue
        diagnostic_row = dict(diagnostic or {})
        domain = str(diagnostic_row.get("domain") or "")
        group = GATE_POLICY_DOMAIN_GROUPS.get(domain)
        if not group:
            continue
        if group in skipped_groups:
            continue
        status = str(diagnostic_row.get("status") or "NOT_RUN").upper()
        if status not in {"BLOCKED", "NOT_RUN", "REVIEW"}:
            continue
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=mode,
            criteria=diagnostic_row.get("title") or domain,
            current=status,
            evidence=diagnostic_row.get("summary") or diagnostic_row.get("title") or domain,
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=status,
            evidence=diagnostic_row.get("title") or domain,
            required_action=diagnostic_row.get("next_action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    for gap in list(critical_gaps or []):
        if not isinstance(gap, dict):
            continue
        gap_row = dict(gap or {})
        group = _gate_group_from_gap(gap_row)
        if group in skipped_groups:
            continue
        status = "BLOCKED" if str(gap_row.get("Severity") or "").upper() == "BLOCK" else "REVIEW"
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=mode,
            criteria=gap_row.get("Area"),
            current=status,
            evidence=gap_row.get("Gap"),
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=status,
            evidence=gap_row.get("Gap") or gap_row.get("Area"),
            required_action=gap_row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("validation_efficacy_audit") or {}),
        group="validation_efficacy",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("construction_risk_audit") or {}),
        group="construction_risk",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("risk_contribution_audit") or {}),
        group="risk_contribution",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("component_role_weight_audit") or {}),
        group="component_role_weight",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("backtest_realism_audit") or {}),
        group="backtest_realism",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    if decision_evidence.get("route") not in {"READY_FOR_FINAL_DECISION", None, ""}:
        _merge_policy_state(
            states,
            group="final_review_evidence",
            severity="BLOCK" if mode == GATE_POLICY_MODE_SELECTION else "REVIEW_REQUIRED",
            current=decision_evidence.get("route") or "-",
            evidence=decision_evidence.get("verdict") or "Final Review evidence is not ready",
            required_action=decision_evidence.get("next_action") or GATE_POLICY_GROUP_ACTIONS["final_review_evidence"],
        )
    if paper_observation.get("blockers"):
        _merge_policy_state(
            states,
            group="paper_observation",
            severity="BLOCK" if "paper_observation" in critical_groups else "REVIEW_REQUIRED",
            current=paper_observation.get("route") or "-",
            evidence=", ".join(str(item) for item in _as_list(paper_observation.get("blockers"))),
            required_action=GATE_POLICY_GROUP_ACTIONS["paper_observation"],
        )
    policy_rows = []
    for group, state in sorted(states.items()):
        severity = str(state.get("severity") or "PASS")
        ready = severity in {"PASS", "WATCH"}
        current_values = list(state.get("current") or ["-"])
        evidence_values = list(state.get("evidence") or ["-"])
        if severity != "PASS":
            current_values = [item for item in current_values if item != "PASS"] or ["-"]
            evidence_values = [item for item in evidence_values if item != "No policy finding"] or ["-"]
        policy_rows.append(
            {
                "Criteria": _finding_label(group),
                "Group": group,
                "Policy": (
                    "not-applicable"
                    if group in skipped_groups
                    else "selection"
                    if mode == GATE_POLICY_MODE_SELECTION
                    else "critical"
                    if group in critical_groups
                    else "review-required"
                ),
                "Ready": ready,
                "Severity": severity,
                "Current": "; ".join(current_values),
                "Evidence": "; ".join(evidence_values),
                "Required Action": state.get("required_action") or GATE_POLICY_GROUP_ACTIONS.get(group, "-"),
                "Selected Route": "Allowed" if ready else "Blocked",
            }
        )
    blockers = [
        f"{row['Criteria']}: {row['Evidence']}"
        for row in policy_rows
        if row.get("Severity") == "BLOCK"
    ]
    review_required = [
        f"{row['Criteria']}: {row['Evidence']}"
        for row in policy_rows
        if row.get("Severity") == "REVIEW_REQUIRED"
    ]
    if blockers:
        outcome = "blocked"
        suggested_decision_route = "RE_REVIEW_REQUIRED"
        next_action = "critical blocker를 해소한 뒤 Final Review에서 최종 후보 선정 가능 여부를 다시 확인합니다."
    elif review_required:
        outcome = "hold_or_re_review"
        suggested_decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
        next_action = "부족한 evidence를 보강한 뒤 Final Review에서 최종 후보 선정 가능 여부를 다시 확인합니다."
    else:
        outcome = "select_ready"
        suggested_decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO
        next_action = "Final Review에서 최종 후보 선정 저장을 진행합니다."
    return {
        "schema_version": (
            SELECTION_GATE_POLICY_SCHEMA_VERSION
            if mode == GATE_POLICY_MODE_SELECTION
            else DEPLOYMENT_READINESS_GATE_POLICY_SCHEMA_VERSION
        ),
        "legacy_schema_version": GATE_POLICY_SCHEMA_VERSION,
        "policy_mode": mode,
        "profile_id": profile_id,
        "profile_label": profile_label,
        "critical_groups": sorted(critical_groups),
        "review_required_groups": sorted(review_groups),
        "not_applicable_groups": sorted(skipped_groups),
        "outcome": outcome,
        "select_allowed": outcome == "select_ready",
        "suggested_decision_route": suggested_decision_route,
        "next_action": next_action,
        "waiver_supported": False,
        "waiver_required_for_select": bool(blockers or review_required),
        "policy_rows": policy_rows,
        "blockers": blockers,
        "review_required": review_required,
    }


def _critical_gap_rows(
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for blocker in _as_list(validation.get("hard_blockers")):
        gaps.append(
            {
                "Area": "Hard blocker",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "Backtest Analysis 또는 Practical Validation에서 blocker를 먼저 해소합니다.",
            }
        )
    for item in _as_list(validation.get("not_run_critical_domains")):
        item_row = dict(item or {})
        gaps.append(
            {
                "Area": _safe_text(item_row.get("title") or item_row.get("domain"), "Critical NOT_RUN"),
                "Gap": "중요 진단이 실행되지 않았습니다.",
                "Severity": "BLOCK",
                "Required Action": _safe_text(item_row.get("next_action"), "데이터 / replay / benchmark 근거를 보강합니다."),
            }
        )
    for gap in _as_list(validation.get("paper_tracking_gaps")):
        gaps.append(
            {
                "Area": "Observation gap",
                "Gap": _safe_text(gap),
                "Severity": "REVIEW",
                "Required Action": "Final Review에서 보류 / 재검토 사유로 확인합니다.",
            }
        )
    for blocker in _as_list(paper_observation.get("blockers")):
        gaps.append(
            {
                "Area": "Paper observation",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "관찰 benchmark / component / weight 기준을 보강합니다.",
            }
        )
    for blocker in _as_list(decision_evidence.get("blockers")):
        gaps.append(
            {
                "Area": "Decision evidence",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "Final Review evidence route를 먼저 통과 가능한 상태로 만듭니다.",
            }
        )
    return gaps


def _assumption_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    status_counts = _status_counts(validation)
    rows = [
        {
            "Assumption": "Hypothetical backtest",
            "Current": "applies",
            "Meaning": "백테스트와 재검증 결과는 미래 수익을 보장하지 않습니다.",
        },
        {
            "Assumption": "No live approval / order",
            "Current": "disabled",
            "Meaning": "Final Review는 투자 승인, 주문 지시, 자동 리밸런싱이 아닙니다.",
        },
        {
            "Assumption": "Compact evidence only",
            "Current": "JSONL stores summary evidence",
            "Meaning": "full holdings / macro / provider raw row는 DB 영역에 두고 판단 row에는 compact 근거만 남깁니다.",
        },
        {
            "Assumption": "Current provider snapshots",
            "Current": _provider_status_summary(validation),
            "Meaning": "ETF provider snapshot은 validation 기준 current evidence이며 과거 특정 시점의 완전한 PIT truth가 아닐 수 있습니다.",
        },
        {
            "Assumption": "Macro vintage",
            "Current": "ALFRED vintage not implemented",
            "Meaning": "macro context는 observation 기준이며 revision vintage까지 보장하지 않습니다.",
        },
        {
            "Assumption": "Cost / slippage limits",
            "Current": curve_evidence.get("portfolio_curve_source") or "source dependent",
            "Meaning": "비용, slippage, 세금, 계좌 제약은 제한적으로만 반영됐을 수 있습니다.",
        },
    ]
    if int(status_counts.get("NOT_RUN", 0) or 0) > 0:
        rows.append(
            {
                "Assumption": "Missing diagnostics",
                "Current": f"{status_counts.get('NOT_RUN', 0)} NOT_RUN",
                "Meaning": "실행되지 않은 진단은 통과가 아니라 판단 전 확인해야 하는 공백입니다.",
            }
        )
    return rows


def _open_review_items_from_policies(
    *,
    selection_policy: dict[str, Any],
    deployment_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    selection_rows = {
        str(row.get("Group") or ""): dict(row or {})
        for row in list(selection_policy.get("policy_rows") or [])
        if isinstance(row, dict)
    }
    for raw_row in list(deployment_policy.get("policy_rows") or []):
        row = dict(raw_row or {})
        group = str(row.get("Group") or "")
        severity = str(row.get("Severity") or "")
        if severity not in {"WATCH", "REVIEW_REQUIRED"}:
            continue
        selection_row = selection_rows.get(group, {})
        if str(selection_row.get("Severity") or "") == "BLOCK":
            continue
        key = (group, str(row.get("Criteria") or ""))
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "Group": group,
                "Criteria": row.get("Criteria") or _finding_label(group),
                "Severity": "OPEN_REVIEW",
                "Current": row.get("Current") or "-",
                "Evidence": row.get("Evidence") or "-",
                "Required Action": row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group, "-"),
                "Selection Gate Effect": "Open review item",
                "Deployment Gate Effect": severity,
            }
        )
    for raw_row in list(selection_policy.get("policy_rows") or []):
        row = dict(raw_row or {})
        if str(row.get("Severity") or "") != "WATCH":
            continue
        group = str(row.get("Group") or "")
        key = (group, str(row.get("Criteria") or ""))
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "Group": group,
                "Criteria": row.get("Criteria") or _finding_label(group),
                "Severity": "OPEN_REVIEW",
                "Current": row.get("Current") or "-",
                "Evidence": row.get("Evidence") or "-",
                "Required Action": row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group, "-"),
                "Selection Gate Effect": "Open review item",
                "Deployment Gate Effect": "-",
            }
        )
    return items


def build_investability_evidence_packet(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact Final Review decision packet without adding persistence."""

    source = dict(source or {})
    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    validation_checks = [dict(row or {}) for row in _as_list(validation.get("checks")) if isinstance(row, dict)]
    benchmark_check = _find_check(validation_checks, "Benchmark parity")
    provider_check = _find_check(validation_checks, "Provider coverage")
    period_check = _find_check(validation_checks, "Runtime period coverage")
    runtime_check = _find_check(validation_checks, "Runtime recheck")
    status_counts = _status_counts(validation)
    robustness = dict(validation.get("robustness_validation") or {})
    critical_gaps = _critical_gap_rows(validation, paper_observation, decision_evidence)
    blocking_gaps = [gap for gap in critical_gaps if str(gap.get("Severity") or "") == "BLOCK"]
    assumptions = _assumption_rows(validation)
    data_coverage_audit = dict(validation.get("data_coverage_audit") or build_data_coverage_audit(validation))
    data_coverage_route = str(data_coverage_audit.get("route") or "")
    validation_for_efficacy = dict(validation)
    validation_for_efficacy.setdefault("data_coverage_audit", data_coverage_audit)
    validation_efficacy_audit = dict(
        validation.get("validation_efficacy_audit") or build_validation_efficacy_audit(validation_for_efficacy)
    )
    validation_efficacy_route = str(validation_efficacy_audit.get("route") or "")
    construction_risk_audit = dict(
        validation.get("construction_risk_audit") or build_construction_risk_audit(validation)
    )
    construction_risk_route = str(construction_risk_audit.get("route") or "")
    risk_contribution_audit = dict(
        validation.get("risk_contribution_audit") or build_risk_contribution_audit(validation)
    )
    risk_contribution_route = str(risk_contribution_audit.get("route") or "")
    component_role_weight_audit = dict(
        validation.get("component_role_weight_audit") or build_component_role_weight_audit(validation)
    )
    component_role_weight_route = str(component_role_weight_audit.get("route") or "")
    backtest_realism_audit = dict(validation.get("backtest_realism_audit") or build_backtest_realism_audit(validation))
    backtest_realism_route = str(backtest_realism_audit.get("route") or "")
    source_chain = {
        "source_type": source.get("source_type") or validation.get("source_type"),
        "source_id": source.get("source_id") or validation.get("selection_source_id"),
        "selection_source_id": validation.get("selection_source_id"),
        "validation_id": validation.get("validation_id"),
        "decision_id": None,
        "monitoring_snapshot_id": None,
    }
    checks = [
        {
            "Section": "Source Chain",
            "Ready": bool(source_chain.get("source_id") or source_chain.get("selection_source_id")),
            "Current": source_chain.get("validation_id") or source_chain.get("selection_source_id") or "-",
            "Meaning": "Backtest source와 Practical Validation result가 이어지는지 확인합니다.",
        },
        {
            "Section": "Backtest Contract / Data Trust",
            "Ready": _ready_from_check(_find_check(validation_checks, "Data Trust")) if validation_checks else True,
            "Current": dict(_find_check(validation_checks, "Data Trust")).get("Current") or validation.get("validation_route") or "-",
            "Meaning": "원본 실행 결과의 데이터 품질과 차단 상태를 확인합니다.",
        },
        {
            "Section": "Runtime Replay",
            "Ready": _ready_from_check(runtime_check) and _ready_from_check(period_check) if runtime_check or period_check else False,
            "Current": f"{runtime_check.get('Current') or '-'} / {period_check.get('Current') or '-'}",
            "Meaning": "저장 snapshot이 아니라 runtime 재검증과 기간 coverage가 충분한지 봅니다.",
        },
        {
            "Section": "Provider / Look-through",
            "Ready": _ready_from_check(provider_check) if provider_check else False,
            "Current": provider_check.get("Current") or _provider_status_summary(validation),
            "Meaning": "ETF 운용성 / holdings / exposure / macro coverage가 검증에 연결됐는지 봅니다.",
        },
        {
            "Section": "Benchmark / Comparator Parity",
            "Ready": _ready_from_check(benchmark_check) if benchmark_check else False,
            "Current": benchmark_check.get("Current") or "-",
            "Meaning": "후보와 benchmark / comparator가 같은 기간 / coverage / frequency로 비교되는지 봅니다.",
        },
        {
            "Section": "Robustness / Stress",
            "Ready": str(robustness.get("robustness_route") or "") == "READY_FOR_STRESS_SWEEP"
            or decision_evidence.get("route") == "READY_FOR_FINAL_DECISION",
            "Current": robustness.get("robustness_route") or decision_evidence.get("route") or "-",
            "Meaning": "stress / sensitivity / robustness 근거가 최종 선택에 충분한지 봅니다.",
        },
        {
            "Section": "Paper Observation",
            "Ready": not bool(paper_observation.get("blockers")),
            "Current": paper_observation.get("route") or "-",
            "Meaning": "선정 이후 관찰 benchmark와 trigger seed가 있는지 봅니다.",
        },
        {
            "Section": "Critical Gaps",
            "Ready": not blocking_gaps,
            "Current": str(len(blocking_gaps)),
            "Meaning": "critical NOT_RUN, hard blocker, evidence blocker가 선택을 막는지 봅니다.",
        },
        {
            "Section": "Validation Efficacy Audit",
            "Ready": validation_efficacy_route == "VALIDATION_EFFICACY_READY",
            "Current": (
                f"{validation_efficacy_audit.get('route_label')} / {validation_efficacy_route}"
                if validation_efficacy_audit.get("route_label") and validation_efficacy_route
                else validation_efficacy_route or validation_efficacy_audit.get("route_label") or "-"
            ),
            "Meaning": "walk-forward / OOS / regime / PIT / replay / benchmark / provider / robustness evidence gap을 최종 선택 전에 분리해서 봅니다.",
        },
        {
            "Section": "Data Coverage Audit",
            "Ready": data_coverage_route == "DATA_COVERAGE_READY",
            "Current": (
                f"{data_coverage_audit.get('route_label')} / {data_coverage_route}"
                if data_coverage_audit.get("route_label") and data_coverage_route
                else data_coverage_route or data_coverage_audit.get("route_label") or "-"
            ),
            "Meaning": "DB price window, provider freshness, PIT replay, universe / survivorship evidence를 분리해서 봅니다.",
        },
        {
            "Section": "Construction Risk Audit",
            "Ready": construction_risk_route == "CONSTRUCTION_RISK_READY",
            "Current": (
                f"{construction_risk_audit.get('route_label')} / {construction_risk_route}"
                if construction_risk_audit.get("route_label") and construction_risk_route
                else construction_risk_route or construction_risk_audit.get("route_label") or "-"
            ),
            "Meaning": "component weight concentration, provider look-through, top holding / overlap, asset exposure risk를 분리해서 봅니다.",
        },
        {
            "Section": "Risk Contribution Audit",
            "Ready": risk_contribution_route == "RISK_CONTRIBUTION_READY",
            "Current": (
                f"{risk_contribution_audit.get('route_label')} / {risk_contribution_route}"
                if risk_contribution_audit.get("route_label") and risk_contribution_route
                else risk_contribution_route or risk_contribution_audit.get("route_label") or "-"
            ),
            "Meaning": "component return matrix, correlation, risk contribution proxy, drop-one dependency risk를 분리해서 봅니다.",
        },
        {
            "Section": "Component Role / Weight Audit",
            "Ready": component_role_weight_route == "COMPONENT_ROLE_WEIGHT_READY",
            "Current": (
                f"{component_role_weight_audit.get('route_label')} / {component_role_weight_route}"
                if component_role_weight_audit.get("route_label") and component_role_weight_route
                else component_role_weight_route or component_role_weight_audit.get("route_label") or "-"
            ),
            "Meaning": "component role source, profile intent, target weight, weight rationale discipline을 분리해서 봅니다.",
        },
        {
            "Section": "Backtest Realism Audit",
            "Ready": backtest_realism_route == "BACKTEST_REALISM_READY",
            "Current": (
                f"{backtest_realism_audit.get('route_label')} / {backtest_realism_route}"
                if backtest_realism_audit.get("route_label") and backtest_realism_route
                else backtest_realism_route or backtest_realism_audit.get("route_label") or "-"
            ),
            "Meaning": "거래비용, turnover, liquidity, net performance, tax/account scope 같은 실전성 가정을 분리해서 봅니다.",
        },
        {
            "Section": "Execution Boundary",
            "Ready": True,
            "Current": "live approval disabled / order disabled",
            "Meaning": "이 packet은 투자 판단 보조 근거이며 주문이나 자동매매가 아닙니다.",
        },
    ]
    validation_for_gate_policy = dict(validation)
    validation_for_gate_policy.setdefault("validation_efficacy_audit", validation_efficacy_audit)
    validation_for_gate_policy.setdefault("construction_risk_audit", construction_risk_audit)
    validation_for_gate_policy.setdefault("risk_contribution_audit", risk_contribution_audit)
    validation_for_gate_policy.setdefault("component_role_weight_audit", component_role_weight_audit)
    selection_gate_policy = build_investability_gate_policy(
        validation=validation_for_gate_policy,
        paper_observation=paper_observation,
        decision_evidence=decision_evidence,
        packet_checks=checks,
        critical_gaps=critical_gaps,
        policy_mode=GATE_POLICY_MODE_SELECTION,
    )
    deployment_gate_policy = build_investability_gate_policy(
        validation=validation_for_gate_policy,
        paper_observation=paper_observation,
        decision_evidence=decision_evidence,
        packet_checks=checks,
        critical_gaps=critical_gaps,
        policy_mode=GATE_POLICY_MODE_DEPLOYMENT,
    )
    open_review_items = _open_review_items_from_policies(
        selection_policy=selection_gate_policy,
        deployment_policy=deployment_gate_policy,
    )
    checks.append(
        {
            "Section": "Selection Gate Policy",
            "Ready": bool(selection_gate_policy.get("select_allowed")),
            "Current": selection_gate_policy.get("outcome") or "-",
            "Meaning": "Final Review selection gate가 Dashboard 추적 후보 선정 가능 여부를 판정합니다.",
        }
    )
    checks.append(
        {
            "Section": "Deployment Readiness Policy",
            "Ready": bool(deployment_gate_policy.get("select_allowed")),
            "Current": deployment_gate_policy.get("outcome") or "-",
            "Meaning": "향후 Live / Deployment Readiness에서 이어서 볼 엄격한 감사 상태입니다.",
        }
    )
    score = round(
        sum(1 for check in checks if bool(check.get("Ready"))) / len(checks) * 10.0,
        1,
    ) if checks else 0.0
    policy_blockers = list(selection_gate_policy.get("blockers") or [])
    policy_review_required = list(selection_gate_policy.get("review_required") or [])
    if policy_blockers:
        route = "INVESTABILITY_PACKET_BLOCKED"
        verdict = "실전 후보 선정 차단: selection gate blocker가 남아 있습니다."
        next_action = "validation evidence를 보강한 뒤 Final Review에서 선정 가능 여부를 다시 확인합니다."
    elif policy_review_required:
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "실전 후보 선정 전 반드시 해소해야 할 review가 남아 있습니다."
        next_action = "부족한 evidence를 보강한 뒤 selected-route gate를 다시 확인합니다."
    elif decision_evidence.get("route") == "READY_FOR_FINAL_DECISION":
        route = "INVESTABILITY_PACKET_READY"
        verdict = "Selected Dashboard에서 추적할 최종 후보로 기록 가능한 evidence packet입니다."
        next_action = "Final Review에서 최종 후보 선정 저장을 진행하고 open review item은 Dashboard / Live Readiness에서 이어서 확인합니다."
    else:
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "hard blocker는 없지만 Final Review evidence가 아직 완전하지 않습니다."
        next_action = "부족한 validation / robustness / observation 근거를 보강합니다."
    return {
        "schema_version": "investability_evidence_packet_v1",
        "route": route,
        "score": score,
        "select_ready": route == "INVESTABILITY_PACKET_READY",
        "verdict": verdict,
        "next_action": next_action,
        "source_chain": source_chain,
        "checks": checks,
        "critical_gaps": critical_gaps,
        "gate_policy_snapshot": selection_gate_policy,
        "selection_gate_policy_snapshot": selection_gate_policy,
        "deployment_readiness_policy_snapshot": deployment_gate_policy,
        "open_review_items": open_review_items,
        "assumptions_and_limits": assumptions,
        "validation_efficacy_audit": validation_efficacy_audit,
        "data_coverage_audit": data_coverage_audit,
        "construction_risk_audit": construction_risk_audit,
        "risk_contribution_audit": risk_contribution_audit,
        "component_role_weight_audit": component_role_weight_audit,
        "backtest_realism_audit": backtest_realism_audit,
        "summary": {
            "pass": int(status_counts.get("PASS", 0) or 0),
            "review": int(status_counts.get("REVIEW", 0) or 0),
            "blocked": int(status_counts.get("BLOCKED", 0) or 0),
            "not_run": int(status_counts.get("NOT_RUN", 0) or 0),
            "provider_status": _provider_status_summary(validation),
            "decision_evidence_route": decision_evidence.get("route"),
            "robustness_route": robustness.get("robustness_route"),
            "gate_policy_outcome": selection_gate_policy.get("outcome"),
            "selection_gate_policy_outcome": selection_gate_policy.get("outcome"),
            "deployment_readiness_policy_outcome": deployment_gate_policy.get("outcome"),
            "open_review_items": len(open_review_items),
            "validation_efficacy_route": validation_efficacy_audit.get("route"),
            "data_coverage_route": data_coverage_audit.get("route"),
            "construction_risk_route": construction_risk_audit.get("route"),
            "risk_contribution_route": risk_contribution_audit.get("route"),
            "component_role_weight_route": component_role_weight_audit.get("route"),
            "backtest_realism_route": backtest_realism_audit.get("route"),
        },
    }


def build_selected_route_gate(
    *,
    decision_route: str,
    investability_packet: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return whether the selected route is allowed by the investability packet."""

    route = str(decision_route or "").strip()
    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    selected = route == SELECT_FOR_PRACTICAL_PORTFOLIO
    select_allowed = bool(gate_policy.get("select_allowed")) if gate_policy else bool(packet.get("select_ready"))
    ready = (not selected) or select_allowed
    current = gate_policy.get("outcome") or packet.get("route") or "packet_not_attached"
    return {
        "Criteria": "Investability evidence packet",
        "Ready": ready,
        "Current": current,
        "Meaning": (
            "실전 후보 선정 저장은 Final Review selection gate가 허용할 때만 가능합니다. live 투입 판단은 별도 단계입니다."
            if selected
            else "보류 / 거절 / 재검토는 정식 저장하지 않는 상태 안내입니다."
        ),
    }


def build_final_review_decision_record_guide(
    *,
    decision_route: str,
    decision_evidence: dict[str, Any] | None,
    investability_packet: dict[str, Any] | None,
) -> dict[str, Any]:
    """Explain how the selected final route should be recorded without revalidating evidence."""

    route = str(decision_route or "").strip()
    evidence = dict(decision_evidence or {})
    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    suggested_route = (
        gate_policy.get("suggested_decision_route")
        or evidence.get("suggested_decision_route")
        or SELECT_FOR_PRACTICAL_PORTFOLIO
    )
    selected_gate = build_selected_route_gate(
        decision_route=route,
        investability_packet=packet,
    )
    selected = route == SELECT_FOR_PRACTICAL_PORTFOLIO
    valid_route = route in FINAL_REVIEW_DECISION_LABELS
    route_templates = dict(
        FINAL_REVIEW_DECISION_RECORD_TEMPLATES.get(
            route,
            FINAL_REVIEW_DECISION_RECORD_TEMPLATES["RE_REVIEW_REQUIRED"],
        )
    )
    if selected and not bool(selected_gate.get("Ready")):
        route_state = "SELECT_ROUTE_BLOCKED"
        route_state_label = "선정 저장 차단"
        notice_level = "warning"
        notice = "최종 후보 선정 저장은 Final Review selection gate가 허용할 때만 활성화됩니다. 보류 / 재검토 / 거절은 저장하지 않는 상태 안내로만 표시합니다."
    elif selected:
        route_state = "SELECT_ROUTE_READY"
        route_state_label = "선정 기록 가능"
        notice_level = "success"
        notice = "현재 selection gate가 선정 기록을 허용합니다. 판단 사유를 남기면 최종 검토 기록으로 저장할 수 있습니다."
    else:
        route_state = "NON_SELECT_NOT_STORED"
        route_state_label = "상태 안내만 표시"
        notice_level = "info"
        notice = "보류 / 거절 / 재검토는 정식 저장 대상이 아닙니다. Final Review의 저장 버튼은 최종 후보 선정이 가능할 때만 활성화됩니다."
    checklist_rows = [
        {
            "Criteria": "Suggested decision",
            "Ready": True,
            "Current": "matches suggestion" if route == suggested_route else "manual override",
            "Meaning": f"권장 route는 {_decision_route_label(suggested_route)}입니다.",
        },
        {
            "Criteria": "Selected route",
            "Ready": valid_route,
            "Current": _decision_route_label(route) if valid_route else route or "-",
            "Meaning": "최종 판단으로 저장될 route입니다.",
        },
        {
            "Criteria": "Official selection route",
            "Ready": selected,
            "Current": "selection save" if selected else "status only",
            "Meaning": "Final Review의 정식 저장은 최종 선정 route만 허용합니다.",
        },
        selected_gate,
        {
            "Criteria": "Operator reason",
            "Ready": True,
            "Current": "required at save",
            "Meaning": "저장 가능 여부는 실제 판단 사유 입력 후 최종 save gate에서 다시 확인합니다.",
        },
        {
            "Criteria": "Live approval / order",
            "Ready": True,
            "Current": "disabled",
            "Meaning": "Final Review는 승인, 주문, 계좌 연동, 자동 리밸런싱을 만들지 않습니다.",
        },
    ]
    blockers = [str(row.get("Criteria")) for row in checklist_rows if not bool(row.get("Ready"))]
    return {
        "schema_version": DECISION_RECORD_GUIDE_SCHEMA_VERSION,
        "decision_route": route,
        "decision_label": _decision_route_label(route),
        "suggested_decision_route": suggested_route,
        "suggested_decision_label": _decision_route_label(suggested_route),
        "route_state": route_state,
        "route_state_label": route_state_label,
        "notice_level": notice_level,
        "notice": notice,
        "selected_route_gate": selected_gate,
        "recordable_route": valid_route and selected and bool(selected_gate.get("Ready")),
        "checklist_rows": checklist_rows,
        "blockers": blockers,
        "route_templates": route_templates,
        "record_boundary": {
            "write_policy": "append_final_selection_decision_only",
            "validation_rerun": False,
            "provider_fetch": False,
            "waiver_persistence": False,
            "non_select_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "account_sync": False,
            "auto_rebalance": False,
        },
    }


def _decision_route_label(route: Any) -> str:
    return FINAL_REVIEW_DECISION_LABELS.get(_safe_text(route, ""), "재검토 필요")


def _policy_rows_by_severity(gate_policy: dict[str, Any], severity: str) -> list[dict[str, Any]]:
    target = str(severity or "").upper()
    return [
        dict(row or {})
        for row in list(dict(gate_policy or {}).get("policy_rows") or [])
        if str(dict(row or {}).get("Severity") or "").upper() == target
    ]


def _decision_cockpit_state(gate_policy: dict[str, Any], packet: dict[str, Any]) -> tuple[str, str, str]:
    outcome = str(dict(gate_policy or {}).get("outcome") or "").strip()
    route = str(dict(packet or {}).get("route") or "").strip()
    if outcome == "select_ready" or route == "INVESTABILITY_PACKET_READY":
        return (
            "SELECT_READY",
            "선정 가능",
            "현재 gate policy상 실전 검토 통과 후보로 저장할 수 있습니다.",
        )
    if outcome == "blocked" or route == "INVESTABILITY_PACKET_BLOCKED":
        return (
            "SELECT_BLOCKED",
            "선정 차단",
            "critical blocker가 남아 있어 최종 후보 선정 저장이 차단됩니다.",
        )
    return (
        "HOLD_OR_RE_REVIEW",
        "보류 / 재검토 권장",
        "hard blocker는 아니지만 선정 전 확인해야 할 review-required 근거가 남아 있습니다.",
    )


def _candidate_board_state_priority(state: Any) -> int:
    state_text = str(state or "").upper()
    if state_text == "SELECT_READY":
        return 1
    if state_text == "HOLD_OR_RE_REVIEW":
        return 2
    return 3


def _candidate_board_policy_reason(rows: list[dict[str, Any]], fallback: str) -> str:
    if not rows:
        return fallback
    row = dict(rows[0] or {})
    label = _safe_text(row.get("Criteria") or row.get("Group"), "Evidence")
    evidence = _safe_text(row.get("Required Action") or row.get("Evidence") or row.get("Current"), fallback)
    return f"{label}: {evidence}"


def _candidate_board_action(cockpit: dict[str, Any]) -> tuple[str, str, str]:
    state = str(dict(cockpit or {}).get("state") or "").upper()
    if state == "SELECT_READY":
        return (
            "최종 후보 선정",
            "선정 가능 후보입니다. Decision Cockpit을 확인한 뒤 최종 후보 선정 저장으로 진행합니다.",
            "선정 가능",
        )
    if state == "SELECT_BLOCKED":
        return (
            "차단 원인 해소",
            _candidate_board_policy_reason(
                list(dict(cockpit or {}).get("must_fix_rows") or []),
                "critical blocker를 먼저 해소한 뒤 다시 확인합니다.",
            ),
            "선정 차단",
        )
    return (
        "보강 후 재확인",
        _candidate_board_policy_reason(
            list(dict(cockpit or {}).get("must_review_rows") or []),
            "review-required 근거를 확인하고 evidence를 보강합니다.",
        ),
        "보류 필요",
    )


def build_final_review_decision_cockpit(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    investability_packet: dict[str, Any],
) -> dict[str, Any]:
    """Build the summary that Final Review should show before detailed evidence tables."""

    source = dict(source or {})
    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    source_chain = dict(packet.get("source_chain") or {})
    summary = dict(packet.get("summary") or {})
    state, state_label, verdict = _decision_cockpit_state(gate_policy, packet)
    suggested_route = (
        gate_policy.get("suggested_decision_route")
        or decision_evidence.get("suggested_decision_route")
        or SELECT_FOR_PRACTICAL_PORTFOLIO
    )
    must_fix = _policy_rows_by_severity(gate_policy, "BLOCK")
    must_review = _policy_rows_by_severity(gate_policy, "REVIEW_REQUIRED")
    watch_rows = _policy_rows_by_severity(gate_policy, "WATCH")
    ready_rows = _policy_rows_by_severity(gate_policy, "PASS")
    baseline = dict(paper_observation.get("baseline_snapshot") or {})
    return {
        "schema_version": "final_review_decision_cockpit_v1",
        "state": state,
        "state_label": state_label,
        "verdict": verdict,
        "next_action": gate_policy.get("next_action") or packet.get("next_action") or decision_evidence.get("next_action") or "-",
        "suggested_decision_route": suggested_route,
        "suggested_decision_label": _decision_route_label(suggested_route),
        "select_allowed": bool(gate_policy.get("select_allowed")),
        "packet_route": packet.get("route"),
        "packet_score": packet.get("score"),
        "gate_outcome": gate_policy.get("outcome"),
        "source_chain": source_chain,
        "source_title": source.get("source_title") or validation.get("source_title") or source_chain.get("source_id") or "-",
        "source_type": source.get("source_type") or validation.get("source_type") or source_chain.get("source_type") or "-",
        "blockers": list(gate_policy.get("blockers") or []),
        "review_required": list(gate_policy.get("review_required") or []),
        "critical_gaps": list(packet.get("critical_gaps") or []),
        "must_fix_rows": must_fix,
        "must_review_rows": must_review,
        "watch_rows": watch_rows,
        "open_review_items": list(packet.get("open_review_items") or []),
        "ready_rows": ready_rows,
        "monitoring_handoff": {
            "route": paper_observation.get("route"),
            "review_cadence": paper_observation.get("review_cadence"),
            "tracking_benchmark": paper_observation.get("tracking_benchmark"),
            "review_triggers": list(paper_observation.get("review_triggers") or []),
            "active_components": len(paper_observation.get("active_components") or []),
            "target_weight_total": baseline.get("target_weight_total"),
        },
        "metrics": {
            "not_run": summary.get("not_run", 0),
            "review": summary.get("review", 0),
            "blocked": summary.get("blocked", 0),
            "policy_blockers": len(gate_policy.get("blockers") or []),
            "policy_review_required": len(gate_policy.get("review_required") or []),
            "critical_gaps": len(packet.get("critical_gaps") or []),
            "open_review_items": len(packet.get("open_review_items") or []),
            "provider_status": summary.get("provider_status") or "-",
            "validation_efficacy_route": summary.get("validation_efficacy_route") or "-",
            "data_coverage_route": summary.get("data_coverage_route") or "-",
            "backtest_realism_route": summary.get("backtest_realism_route") or "-",
        },
    }


def build_final_review_candidate_board_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten Final Review eligible candidates into a comparison board."""

    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(list(candidates or []), start=1):
        source = dict(candidate.get("source") or {})
        validation = dict(candidate.get("validation") or {})
        paper_observation = dict(candidate.get("paper_observation") or {})
        decision_evidence = dict(candidate.get("decision_evidence") or {})
        packet = dict(candidate.get("investability_packet") or {})
        if not packet:
            packet = build_investability_evidence_packet(
                source=source,
                validation=validation,
                paper_observation=paper_observation,
                decision_evidence=decision_evidence,
            )
        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper_observation,
            decision_evidence=decision_evidence,
            investability_packet=packet,
        )
        source_chain = dict(packet.get("source_chain") or {})
        summary = dict(packet.get("summary") or {})
        action_label, primary_reason, priority_label = _candidate_board_action(cockpit)
        metrics = dict(cockpit.get("metrics") or {})
        packet_score = packet.get("score")
        try:
            sortable_score = float(packet_score or 0.0)
        except (TypeError, ValueError):
            sortable_score = 0.0
        state_priority = _candidate_board_state_priority(cockpit.get("state"))
        rows.append(
            {
                "Rank": index,
                "Review Priority": f"P{index}",
                "Priority Label": priority_label,
                "Candidate": cockpit.get("source_title") or candidate.get("label") or "-",
                "Decision State": cockpit.get("state_label"),
                "Suggested Decision": cockpit.get("suggested_decision_label"),
                "Board Action": action_label,
                "Primary Reason": primary_reason,
                "Next Review Focus": cockpit.get("next_action") or "-",
                "Gate Outcome": cockpit.get("gate_outcome") or "-",
                "Select Allowed": "Yes" if cockpit.get("select_allowed") else "No",
                "Blockers": metrics.get("policy_blockers", 0),
                "Review Required": metrics.get("policy_review_required", 0),
                "Open Review": metrics.get("open_review_items", 0),
                "Critical Gaps": metrics.get("critical_gaps", 0),
                "NOT_RUN": summary.get("not_run", 0),
                "Provider": summary.get("provider_status") or "-",
                "Validation Efficacy": summary.get("validation_efficacy_route") or "-",
                "Data Coverage": summary.get("data_coverage_route") or "-",
                "Backtest Realism": summary.get("backtest_realism_route") or "-",
                "Packet Score": packet.get("score"),
                "Validation ID": source_chain.get("validation_id") or validation.get("validation_id") or "-",
                "Source ID": source_chain.get("selection_source_id")
                or source_chain.get("source_id")
                or source.get("source_id")
                or "-",
                "_sort_key": (
                    state_priority,
                    int(metrics.get("policy_blockers", 0) or 0),
                    int(metrics.get("policy_review_required", 0) or 0),
                    int(metrics.get("open_review_items", 0) or 0),
                    int(metrics.get("critical_gaps", 0) or 0),
                    int(summary.get("not_run", 0) or 0),
                    -sortable_score,
                    index,
                ),
            }
        )
    rows.sort(key=lambda row: tuple(row.get("_sort_key") or (99, 99, 99, 99, 99, 99, 0, 9999)))
    for rank, row in enumerate(rows, start=1):
        row["Rank"] = rank
        row["Review Priority"] = f"P{rank}"
        row.pop("_sort_key", None)
    return rows


def build_final_review_candidate_board(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the Final Review candidate comparison board and review queue."""

    rows = build_final_review_candidate_board_rows(candidates)
    total = len(rows)
    select_ready = sum(1 for row in rows if row.get("Decision State") == "선정 가능")
    blocked = sum(1 for row in rows if row.get("Decision State") == "선정 차단")
    hold_or_re_review = max(0, total - select_ready - blocked)
    first_row = dict(rows[0] or {}) if rows else {}
    queue_rows = [
        {
            "Priority": row.get("Review Priority"),
            "Candidate": row.get("Candidate"),
            "Action": row.get("Board Action"),
            "Reason": row.get("Primary Reason"),
            "Suggested Decision": row.get("Suggested Decision"),
            "Packet Score": row.get("Packet Score"),
        }
        for row in rows[:5]
    ]
    return {
        "schema_version": CANDIDATE_BOARD_SCHEMA_VERSION,
        "summary": {
            "total_candidates": total,
            "select_ready": select_ready,
            "hold_or_re_review": hold_or_re_review,
            "blocked": blocked,
            "first_review_candidate": first_row.get("Candidate") or "-",
            "first_review_action": first_row.get("Board Action") or "-",
            "first_review_reason": first_row.get("Primary Reason") or "-",
        },
        "review_queue_rows": queue_rows,
        "rows": rows,
    }


def build_final_review_status_display(row: dict[str, Any]) -> dict[str, str]:
    """Translate a saved final decision row into the current Final Review status copy."""

    decision_route = str(row.get("decision_route") or "").strip()
    status = dict(FINAL_REVIEW_STATUS_DISPLAY.get(decision_route) or {})
    if status:
        return status
    legacy_handoff = dict(row.get("phase35_handoff") or {})
    return {
        "route": str(legacy_handoff.get("handoff_route") or "FINAL_REVIEW_STATUS_UNKNOWN"),
        "verdict": "최종 판단 상태 확인 필요",
        "next_action": "decision route와 evidence를 확인한 뒤 Final Review에서 다시 판단합니다.",
    }


def build_final_review_decision_display_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten saved final decision records for a UI table without depending on Streamlit."""

    display_rows: list[dict[str, Any]] = []
    for row in rows:
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        gate_policy = dict(row.get("selection_gate_policy_snapshot") or row.get("gate_policy_snapshot") or {})
        if not gate_policy:
            packet = dict(row.get("investability_evidence_packet") or {})
            gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
        status_display = build_final_review_status_display(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "판단 라벨": FINAL_REVIEW_DECISION_LABELS.get(str(row.get("decision_route") or ""), "재검토 필요"),
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Observation": row.get("source_observation_id") or row.get("source_paper_ledger_id") or "-",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route"),
                "Evidence Score": evidence.get("score"),
                "Gate Outcome": gate_policy.get("outcome") or "-",
                "Final Status": status_display.get("route"),
                "Live Approval": "Disabled",
            }
        )
    return display_rows


def _saved_decision_route_family(route: Any) -> str:
    route_text = str(route or "").strip()
    if route_text == SELECT_FOR_PRACTICAL_PORTFOLIO:
        return "Selected"
    if route_text == "HOLD_FOR_MORE_PAPER_TRACKING":
        return "Hold"
    if route_text == "REJECT_FOR_PRACTICAL_USE":
        return "Reject"
    if route_text == "RE_REVIEW_REQUIRED":
        return "Re-review"
    return "Unknown"


def _decision_gate_policy(row: dict[str, Any]) -> dict[str, Any]:
    gate_policy = dict(row.get("selection_gate_policy_snapshot") or row.get("gate_policy_snapshot") or {})
    if gate_policy:
        return gate_policy
    packet = dict(row.get("investability_evidence_packet") or {})
    return dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})


def build_saved_final_review_decision_review(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize saved Final Review decisions for review without adding persistence."""

    indexed_rows = [
        (index, dict(row or {}))
        for index, row in enumerate(list(rows or []))
    ]
    indexed_rows.sort(
        key=lambda item: _safe_text(item[1].get("updated_at") or item[1].get("created_at"), ""),
        reverse=True,
    )
    review_rows: list[dict[str, Any]] = []
    family_counts = {key: 0 for key in FINAL_REVIEW_SAVED_DECISION_FILTER_OPTIONS if key != "All"}
    dashboard_eligible = 0
    for display_index, (raw_index, row) in enumerate(indexed_rows, start=1):
        route = str(row.get("decision_route") or "").strip()
        family = _saved_decision_route_family(route)
        family_counts[family] = int(family_counts.get(family, 0) or 0) + 1
        if route == SELECT_FOR_PRACTICAL_PORTFOLIO:
            dashboard_eligible += 1
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        packet = dict(row.get("investability_evidence_packet") or {})
        gate_policy = _decision_gate_policy(row)
        operator = dict(row.get("operator_decision") or {})
        status_display = build_final_review_status_display(row)
        issue_count = (
            len(evidence.get("blockers") or [])
            + len(packet.get("critical_gaps") or [])
            + len(gate_policy.get("blockers") or [])
            + len(gate_policy.get("review_required") or [])
        )
        review_rows.append(
            {
                "Rank": display_index,
                "Updated At": row.get("updated_at") or row.get("created_at") or "-",
                "Decision ID": row.get("decision_id") or "-",
                "Decision": FINAL_REVIEW_DECISION_LABELS.get(route, "재검토 필요"),
                "Route Family": family,
                "Decision Route": route or "-",
                "Final Status": status_display.get("route") or "-",
                "Source": f"{row.get('source_type') or '-'} / {row.get('source_id') or '-'}",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route") or "-",
                "Evidence Score": evidence.get("score") if evidence.get("score") is not None else "-",
                "Packet Route": packet.get("route") or "-",
                "Gate Outcome": gate_policy.get("outcome") or "-",
                "Select Allowed": "Yes" if bool(gate_policy.get("select_allowed")) else "No",
                "Evidence Issues": issue_count,
                "Dashboard Eligible": "Yes" if route == SELECT_FOR_PRACTICAL_PORTFOLIO else "No",
                "Operator Reason": _safe_text(operator.get("reason"), "-"),
                "Next Action": _safe_text(operator.get("next_action") or status_display.get("next_action"), "-"),
                "Live Approval": "Disabled",
                "_row_index": raw_index,
            }
        )
    latest = dict(review_rows[0]) if review_rows else {}
    return {
        "schema_version": SAVED_DECISION_REVIEW_SCHEMA_VERSION,
        "summary": {
            "total_records": len(review_rows),
            "selected": int(family_counts.get("Selected", 0) or 0),
            "hold": int(family_counts.get("Hold", 0) or 0),
            "reject": int(family_counts.get("Reject", 0) or 0),
            "re_review": int(family_counts.get("Re-review", 0) or 0),
            "unknown": int(family_counts.get("Unknown", 0) or 0),
            "dashboard_eligible": dashboard_eligible,
            "latest_decision_id": latest.get("Decision ID") or "-",
            "latest_decision": latest.get("Decision") or "-",
            "latest_updated_at": latest.get("Updated At") or "-",
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
        "filter_options": list(FINAL_REVIEW_SAVED_DECISION_FILTER_OPTIONS),
        "rows": review_rows,
    }


def _append_check_rows(
    display_rows: list[dict[str, Any]],
    *,
    area: str,
    checks: list[dict[str, Any]],
) -> None:
    for check in checks:
        check_row = dict(check or {})
        display_rows.append(
            {
                "Area": area,
                "Criteria": check_row.get("Criteria")
                or check_row.get("criteria")
                or check_row.get("Section")
                or check_row.get("Group")
                or check_row.get("Check")
                or "-",
                "Ready": check_row.get("Ready")
                if "Ready" in check_row
                else check_row.get("ready")
                if "ready" in check_row
                else str(check_row.get("Status") or "").upper() == "PASS",
                "Current": check_row.get("Current")
                or check_row.get("current")
                or check_row.get("current_value")
                or check_row.get("Status")
                or "-",
                "Meaning": check_row.get("Meaning")
                or check_row.get("meaning")
                or check_row.get("Required Action")
                or check_row.get("Evidence")
                or "-",
                "Score": check_row.get("Score") or check_row.get("score") or "-",
            }
        )


def build_final_decision_evidence_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand a final decision row into evidence check rows shared by review and dashboard views."""

    raw_decision = dict(row.get("raw_decision") or row)
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    display_rows: list[dict[str, Any]] = []
    packet = dict(raw_decision.get("investability_evidence_packet") or {})
    gate_policy = dict(
        raw_decision.get("selection_gate_policy_snapshot")
        or raw_decision.get("gate_policy_snapshot")
        or packet.get("selection_gate_policy_snapshot")
        or packet.get("gate_policy_snapshot")
        or {}
    )
    look_through = dict(risk_snapshot.get("provider_look_through_board") or {})
    if not look_through:
        provider_context = dict(risk_snapshot.get("provider_coverage") or {})
        look_through = dict(provider_context.get("look_through_board") or {})
    robustness_lab = dict(robustness.get("robustness_lab_board") or risk_snapshot.get("robustness_lab_board") or {})
    validation_efficacy = dict(
        risk_snapshot.get("validation_efficacy_audit") or packet.get("validation_efficacy_audit") or {}
    )
    data_coverage = dict(risk_snapshot.get("data_coverage_audit") or packet.get("data_coverage_audit") or {})
    construction_risk = dict(
        risk_snapshot.get("construction_risk_audit") or packet.get("construction_risk_audit") or {}
    )
    risk_contribution = dict(
        risk_snapshot.get("risk_contribution_audit") or packet.get("risk_contribution_audit") or {}
    )
    component_role_weight = dict(
        risk_snapshot.get("component_role_weight_audit") or packet.get("component_role_weight_audit") or {}
    )
    backtest_realism = dict(risk_snapshot.get("backtest_realism_audit") or packet.get("backtest_realism_audit") or {})
    _append_check_rows(display_rows, area="Final Review Evidence", checks=list(evidence.get("checks") or []))
    _append_check_rows(display_rows, area="Investability Packet", checks=list(packet.get("checks") or []))
    _append_check_rows(display_rows, area="Gate Policy", checks=list(gate_policy.get("policy_rows") or []))
    _append_check_rows(display_rows, area="Validation", checks=list(risk_snapshot.get("validation_checks") or []))
    _append_check_rows(display_rows, area="Validation Efficacy", checks=list(validation_efficacy.get("rows") or []))
    _append_check_rows(display_rows, area="Data Coverage", checks=list(data_coverage.get("rows") or []))
    _append_check_rows(display_rows, area="Construction Risk", checks=list(construction_risk.get("rows") or []))
    _append_check_rows(display_rows, area="Risk Contribution", checks=list(risk_contribution.get("rows") or []))
    _append_check_rows(display_rows, area="Component Role / Weight", checks=list(component_role_weight.get("rows") or []))
    _append_check_rows(display_rows, area="Backtest Realism", checks=list(backtest_realism.get("rows") or []))
    _append_check_rows(display_rows, area="Look-through Exposure", checks=list(look_through.get("summary_rows") or []))
    _append_check_rows(display_rows, area="Robustness Lab", checks=list(robustness_lab.get("summary_rows") or []))
    _append_check_rows(display_rows, area="Robustness", checks=list(robustness.get("checks") or []))
    _append_check_rows(display_rows, area="Paper Observation", checks=list(paper_snapshot.get("checks") or []))
    return display_rows


def _markdown_value(value: Any, default: str = "-") -> str:
    if value is None:
        text = default
    elif isinstance(value, str):
        text = value.strip() or default
    else:
        text = str(value).strip() or default
    return text.replace("|", "\\|").replace("\n", "<br>")


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["- 표시할 row가 없습니다."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_value(row.get(column)) for column in columns) + " |")
    return lines


def _decision_dossier_filename(decision_id: Any) -> str:
    safe_id = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_"
        for char in _safe_text(decision_id, "final_decision")
    )
    return f"{safe_id}_decision_dossier.md"


def _decision_source_contract(
    raw_decision: dict[str, Any],
    *,
    surface: str,
    monitoring_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    timeline_contract = dict(dict(monitoring_timeline or {}).get("source_contract") or {})
    session_sources = [
        str(source).strip()
        for source in list(timeline_contract.get("session_evidence_sources") or [])
        if str(source or "").strip()
    ]
    decision_id = _safe_text(raw_decision.get("decision_id"), "")
    source_type = _safe_text(raw_decision.get("source_type"), "")
    source_id = _safe_text(raw_decision.get("source_id"), "")
    return {
        "schema_version": DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION,
        "surface": _safe_text(surface, "decision_dossier"),
        "decision_id": decision_id,
        "decision_route": _safe_text(raw_decision.get("decision_route"), ""),
        "selected_practical_portfolio": bool(raw_decision.get("selected_practical_portfolio")),
        "source_type": source_type,
        "source_id": source_id,
        "source_title": _safe_text(raw_decision.get("source_title"), ""),
        "selection_source_id": _safe_text(raw_decision.get("selection_source_id"), ""),
        "validation_id": _safe_text(raw_decision.get("validation_id"), ""),
        "source_identity": f"{source_type}:{source_id}" if source_type or source_id else "",
        "durable_source": "FINAL_PORTFOLIO_SELECTION_DECISIONS",
        "registry_file": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        "timeline_contract_present": bool(timeline_contract),
        "timeline_contract_consistent": _timeline_contract_matches_decision(raw_decision, timeline_contract)
        if timeline_contract
        else None,
        "session_evidence_sources": session_sources,
        "evidence_scope": "final_decision_plus_optional_session_timeline",
        "execution_boundary": {
            "write_policy": "read_only_decision_source_contract",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Decision Dossier reads the saved Final Decision row and optional Selected Dashboard session timeline only.",
        },
    }


def _timeline_contract_matches_decision(raw_decision: dict[str, Any], timeline_contract: dict[str, Any]) -> bool:
    if not timeline_contract:
        return False
    fields = ("decision_id", "decision_route", "source_type", "source_id", "selection_source_id", "validation_id")
    return all(
        _safe_text(raw_decision.get(field), "") == _safe_text(timeline_contract.get(field), "")
        for field in fields
    )


def _decision_dossier_component_rows(raw_decision: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, component in enumerate(list(raw_decision.get("selected_components") or []), start=1):
        component_row = dict(component or {})
        rows.append(
            {
                "Order": index,
                "Title": component_row.get("title")
                or component_row.get("strategy_name")
                or component_row.get("registry_id")
                or f"component_{index}",
                "Registry ID": component_row.get("registry_id") or "-",
                "Target Weight": component_row.get("target_weight") or component_row.get("weight") or "-",
                "Benchmark": component_row.get("benchmark") or "-",
            }
        )
    return rows


def _decision_dossier_markdown(dossier: dict[str, Any]) -> str:
    decision = dict(dossier.get("decision") or {})
    operator = dict(dossier.get("operator") or {})
    validation = dict(dossier.get("validation_summary") or {})
    gate_policy = dict(dossier.get("gate_policy") or {})
    monitoring = dict(dossier.get("monitoring_timeline") or {})
    source_contract = dict(dossier.get("source_contract") or {})
    boundary = dict(dossier.get("execution_boundary") or {})
    metrics = dict(dossier.get("metrics") or {})
    lines = [
        "# Final Decision Dossier",
        "",
        "## Summary",
        f"- Decision ID: `{_markdown_value(decision.get('decision_id'))}`",
        f"- Source: `{_markdown_value(decision.get('source_type'))}` / `{_markdown_value(decision.get('source_id'))}`",
        f"- Title: {_markdown_value(decision.get('source_title'))}",
        f"- Decision: {_markdown_value(decision.get('decision_label'))} (`{_markdown_value(decision.get('decision_route'))}`)",
        f"- Final Status: `{_markdown_value(decision.get('status_route'))}`",
        f"- Evidence Route: `{_markdown_value(decision.get('evidence_route'))}`",
        f"- Gate Outcome: `{_markdown_value(gate_policy.get('outcome'))}`",
        f"- Selected Practical Portfolio: `{_markdown_value(decision.get('selected_practical_portfolio'))}`",
        "",
        "## Source Contract",
        f"- Durable Source: `{_markdown_value(source_contract.get('durable_source'))}`",
        f"- Source Identity: `{_markdown_value(source_contract.get('source_identity'))}`",
        f"- Timeline Contract Present: `{_markdown_value(source_contract.get('timeline_contract_present'))}`",
        f"- Timeline Contract Consistent: `{_markdown_value(source_contract.get('timeline_contract_consistent'))}`",
        f"- Session Evidence Sources: {_markdown_value(', '.join(source_contract.get('session_evidence_sources') or []))}",
        "",
        "## Operator Decision",
        f"- Reason: {_markdown_value(operator.get('reason'))}",
        f"- Constraints: {_markdown_value(operator.get('constraints'))}",
        f"- Next Action: {_markdown_value(operator.get('next_action'))}",
        f"- Review Cadence: `{_markdown_value(operator.get('review_cadence'))}`",
        f"- Review Triggers: {_markdown_value(', '.join(operator.get('review_triggers') or []))}",
        "",
        "## Validation Snapshot",
        f"- Validation Route: `{_markdown_value(validation.get('validation_route'))}`",
        f"- Validation Score: `{_markdown_value(validation.get('validation_score'))}`",
        f"- Robustness Route: `{_markdown_value(validation.get('robustness_route'))}`",
        f"- Paper Observation Route: `{_markdown_value(validation.get('paper_observation_route'))}`",
        f"- Diagnostic Counts: `{_markdown_value(validation.get('status_counts'))}`",
        "",
        "## Selected Components",
        *_markdown_table(
            list(dossier.get("components") or []),
            ["Order", "Title", "Registry ID", "Target Weight", "Benchmark"],
        ),
        "",
        "## Evidence Checks",
        *_markdown_table(
            list(dossier.get("evidence_checks") or []),
            ["Area", "Criteria", "Ready", "Current", "Meaning", "Score"],
        ),
        "",
        "## Gate Policy",
        *_markdown_table(
            list(gate_policy.get("policy_rows") or []),
            ["Group", "Status", "Severity", "Current", "Evidence", "Required Action"],
        ),
        "",
        "## Monitoring Timeline",
    ]
    if monitoring.get("present"):
        lines.extend(
            _markdown_table(
                list(monitoring.get("rows") or []),
                ["order", "event", "timestamp", "status_label", "signal", "next_action", "source"],
            )
        )
    else:
        lines.append("- 현재 dossier에는 Selected Dashboard session timeline이 포함되지 않았습니다.")
    lines.extend(
        [
            "",
            "## Execution Boundary",
            *_markdown_table(
                [
                    {"Boundary": "Write Policy", "Value": boundary.get("write_policy")},
                    {"Boundary": "DB Write", "Value": boundary.get("db_write")},
                    {"Boundary": "Registry Write", "Value": boundary.get("registry_write")},
                    {"Boundary": "Report Auto Write", "Value": boundary.get("report_auto_write")},
                    {"Boundary": "Monitoring Log Auto Write", "Value": boundary.get("monitoring_log_auto_write")},
                    {"Boundary": "Live Approval", "Value": boundary.get("live_approval")},
                    {"Boundary": "Order Instruction", "Value": boundary.get("order_instruction")},
                    {"Boundary": "Auto Rebalance", "Value": boundary.get("auto_rebalance")},
                ],
                ["Boundary", "Value"],
            ),
            "",
            "## Metrics",
            f"- Components: `{_markdown_value(metrics.get('component_count'))}`",
            f"- Evidence Checks: `{_markdown_value(metrics.get('evidence_check_count'))}`",
            f"- Not Ready Evidence Checks: `{_markdown_value(metrics.get('not_ready_evidence_check_count'))}`",
            "",
            "> This dossier is a decision-support export. It is not live approval, broker order instruction, or automated rebalance authorization.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_decision_dossier(
    row: dict[str, Any],
    *,
    monitoring_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only human-readable dossier for a saved final decision row."""

    raw_decision = dict(row.get("raw_decision") or row or {})
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    packet = dict(raw_decision.get("investability_evidence_packet") or {})
    gate_policy = dict(
        raw_decision.get("selection_gate_policy_snapshot")
        or raw_decision.get("gate_policy_snapshot")
        or packet.get("selection_gate_policy_snapshot")
        or packet.get("gate_policy_snapshot")
        or {}
    )
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    operator_decision = dict(raw_decision.get("operator_decision") or {})
    status_display = build_final_review_status_display(raw_decision)
    decision_route = _safe_text(raw_decision.get("decision_route"))
    evidence_checks = build_final_decision_evidence_rows(raw_decision)
    not_ready_count = sum(1 for check in evidence_checks if not bool(check.get("Ready")))
    timeline = dict(monitoring_timeline or {})
    source_contract = _decision_source_contract(
        raw_decision,
        surface="decision_dossier",
        monitoring_timeline=timeline,
    )
    monitoring_payload = {
        "present": bool(timeline),
        "schema_version": timeline.get("schema_version"),
        "timeline_status": timeline.get("timeline_status"),
        "timeline_label": timeline.get("timeline_label"),
        "conclusion": timeline.get("conclusion"),
        "rows": list(timeline.get("rows") or []),
        "metrics": dict(timeline.get("metrics") or {}),
    }
    dossier: dict[str, Any] = {
        "schema_version": DECISION_DOSSIER_SCHEMA_VERSION,
        "decision": {
            "decision_id": raw_decision.get("decision_id"),
            "created_at": raw_decision.get("created_at"),
            "updated_at": raw_decision.get("updated_at"),
            "decision_route": decision_route,
            "decision_label": FINAL_REVIEW_DECISION_LABELS.get(decision_route, "재검토 필요"),
            "selected_practical_portfolio": bool(raw_decision.get("selected_practical_portfolio")),
            "source_type": raw_decision.get("source_type"),
            "source_id": raw_decision.get("source_id"),
            "source_title": raw_decision.get("source_title"),
            "selection_source_id": raw_decision.get("selection_source_id"),
            "validation_id": raw_decision.get("validation_id"),
            "evidence_route": evidence.get("route"),
            "packet_route": packet.get("route"),
            "status_route": status_display.get("route"),
            "status_verdict": status_display.get("verdict"),
            "status_next_action": status_display.get("next_action"),
        },
        "operator": {
            "reason": operator_decision.get("reason"),
            "constraints": operator_decision.get("constraints"),
            "next_action": operator_decision.get("next_action"),
            "review_cadence": paper_snapshot.get("review_cadence"),
            "review_triggers": list(paper_snapshot.get("review_triggers") or []),
        },
        "validation_summary": {
            "validation_route": risk_snapshot.get("validation_route"),
            "validation_score": risk_snapshot.get("validation_score"),
            "status_counts": dict(dict(risk_snapshot.get("diagnostic_summary") or {}).get("status_counts") or {}),
            "provider_status": _provider_status_summary(risk_snapshot),
            "robustness_route": robustness.get("robustness_route"),
            "robustness_score": robustness.get("robustness_score"),
            "paper_observation_route": paper_snapshot.get("route"),
            "not_run_domains": list(risk_snapshot.get("not_run_domains") or []),
            "not_run_critical_domains": list(risk_snapshot.get("not_run_critical_domains") or []),
        },
        "components": _decision_dossier_component_rows(raw_decision),
        "evidence_checks": evidence_checks,
        "gate_policy": {
            "schema_version": gate_policy.get("schema_version"),
            "outcome": gate_policy.get("outcome"),
            "select_allowed": bool(gate_policy.get("select_allowed")),
            "blockers": list(gate_policy.get("blockers") or []),
            "review_required": list(gate_policy.get("review_required") or []),
            "policy_rows": list(gate_policy.get("policy_rows") or []),
        },
        "monitoring_timeline": monitoring_payload,
        "source_contract": source_contract,
        "metrics": {
            "component_count": len(raw_decision.get("selected_components") or []),
            "evidence_check_count": len(evidence_checks),
            "not_ready_evidence_check_count": not_ready_count,
            "gate_policy_row_count": len(gate_policy.get("policy_rows") or []),
            "monitoring_timeline_present": bool(timeline),
            "source_contract_present": True,
            "timeline_source_contract_present": source_contract.get("timeline_contract_present"),
            "source_contract_consistent": source_contract.get("timeline_contract_consistent")
            if source_contract.get("timeline_contract_present")
            else True,
        },
        "execution_boundary": {
            "write_policy": "read_only_dossier",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Dossier is generated from existing final decision evidence and optional session timeline only.",
        },
    }
    dossier["filename"] = _decision_dossier_filename(raw_decision.get("decision_id"))
    dossier["markdown"] = _decision_dossier_markdown(dossier)
    return dossier


__all__ = [
    "DECISION_DOSSIER_SCHEMA_VERSION",
    "DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION",
    "CANDIDATE_BOARD_SCHEMA_VERSION",
    "DECISION_RECORD_GUIDE_SCHEMA_VERSION",
    "SAVED_DECISION_REVIEW_SCHEMA_VERSION",
    "FINAL_REVIEW_DECISION_LABELS",
    "FINAL_REVIEW_STATUS_DISPLAY",
    "SELECT_FOR_PRACTICAL_PORTFOLIO",
    "build_decision_dossier",
    "build_final_review_candidate_board",
    "build_final_review_candidate_board_rows",
    "build_final_review_decision_cockpit",
    "build_final_review_decision_record_guide",
    "build_saved_final_review_decision_review",
    "build_investability_gate_policy",
    "build_investability_evidence_packet",
    "build_final_decision_evidence_rows",
    "build_final_review_decision_display_rows",
    "build_final_review_status_display",
    "build_selected_route_gate",
]
