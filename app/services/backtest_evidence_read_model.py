from __future__ import annotations

from typing import Any

from app.services.backtest_realism_audit import build_backtest_realism_audit
from app.services.backtest_validation_efficacy import build_validation_efficacy_audit


SELECT_FOR_PRACTICAL_PORTFOLIO = "SELECT_FOR_PRACTICAL_PORTFOLIO"
DECISION_DOSSIER_SCHEMA_VERSION = "decision_dossier_v1"

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
GATE_POLICY_SCHEMA_VERSION = "investability_gate_policy_v1"
GATE_POLICY_GROUP_LABELS = {
    "data_trust": "Data Trust / Source Contract",
    "benchmark": "Benchmark Parity",
    "provider_coverage": "Provider / Look-through",
    "stress_robustness": "Stress / Robustness",
    "leveraged_inverse": "Leveraged / Inverse Suitability",
    "paper_observation": "Paper Observation",
    "final_review_evidence": "Final Review Evidence",
    "validation_efficacy": "Validation Efficacy",
}
GATE_POLICY_GROUP_ACTIONS = {
    "data_trust": "원본 source, 가격, 비중, Data Trust blocker를 먼저 해소합니다.",
    "benchmark": "같은 기간 / frequency / coverage의 benchmark parity를 보강합니다.",
    "provider_coverage": "ETF 운용성 / holdings / exposure / macro coverage를 actual evidence로 보강합니다.",
    "stress_robustness": "stress, rolling, sensitivity, overfit evidence를 실행 가능한 근거로 보강합니다.",
    "leveraged_inverse": "leveraged / inverse 노출 목적, 보유 기간, 위험 한계를 명시합니다.",
    "paper_observation": "관찰 benchmark, active component, review trigger를 보강합니다.",
    "final_review_evidence": "Final Review evidence route가 ready가 되도록 validation / robustness / observation blocker를 해소합니다.",
    "validation_efficacy": "runtime replay, benchmark parity, provider freshness, robustness, PIT / survivorship evidence gap을 보강합니다.",
}
GATE_POLICY_DOMAIN_GROUPS = {
    "input_evidence_layer": "data_trust",
    "asset_allocation_fit": "provider_coverage",
    "concentration_overlap_exposure": "provider_coverage",
    "correlation_diversification_risk_contribution": "stress_robustness",
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
    },
    "growth_aggressive": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "final_review_evidence",
        "validation_efficacy",
    },
    "hedged_tactical": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "final_review_evidence",
        "validation_efficacy",
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


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


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
) -> str:
    normalized = str(status or "").upper()
    if normalized in {"BLOCKED", "BLOCK", "NOT_RUN"}:
        return "BLOCK" if group in critical_groups else "REVIEW_REQUIRED"
    if normalized == "REVIEW":
        if group in critical_groups:
            return "REVIEW_REQUIRED"
        if group in review_groups:
            return "REVIEW_REQUIRED"
        return "WATCH"
    return "PASS"


def _gate_group_from_gap(gap: dict[str, Any]) -> str:
    area = _safe_text(gap.get("Area"), "").lower()
    text = f"{area} {_safe_text(gap.get('Gap'), '').lower()}"
    if "paper" in text or "observation" in text:
        return "paper_observation"
    if "benchmark" in text:
        return "benchmark"
    if any(token in text for token in ("provider", "holding", "exposure", "operability", "macro", "liquidity")):
        return "provider_coverage"
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


def build_investability_gate_policy(
    *,
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    packet_checks: list[dict[str, Any]] | None = None,
    critical_gaps: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Summarize profile-aware gate policy without persisting raw validation data."""

    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    profile_id, profile_label, critical_groups, review_groups = _profile_gate_policy_sets(validation)
    states: dict[str, dict[str, Any]] = {}
    for group in sorted(critical_groups | review_groups):
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
        current = check_row.get("Current") or "-"
        status = _policy_status_from_current(ready=_ready_from_check(check_row), current=current)
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
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
        status = str(diagnostic_row.get("status") or "NOT_RUN").upper()
        if status not in {"BLOCKED", "NOT_RUN", "REVIEW"}:
            continue
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
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
        status = "BLOCKED" if str(gap_row.get("Severity") or "").upper() == "BLOCK" else "REVIEW"
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=status,
            evidence=gap_row.get("Gap") or gap_row.get("Area"),
            required_action=gap_row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    if decision_evidence.get("route") not in {"READY_FOR_FINAL_DECISION", None, ""}:
        _merge_policy_state(
            states,
            group="final_review_evidence",
            severity="REVIEW_REQUIRED",
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
                "Policy": "critical" if group in critical_groups else "review-required",
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
        next_action = "critical blocker를 해소하거나 실전 검토 후보 선정 대신 재검토 / 거절로 기록합니다."
    elif review_required:
        outcome = "hold_or_re_review"
        suggested_decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
        next_action = "선정 대신 보류 / 재검토로 기록하고 부족한 evidence를 보강합니다."
    else:
        outcome = "select_ready"
        suggested_decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO
        next_action = "Final Review에서 선정 / 보류 / 거절 / 재검토 판단을 기록합니다."
    return {
        "schema_version": GATE_POLICY_SCHEMA_VERSION,
        "profile_id": profile_id,
        "profile_label": profile_label,
        "critical_groups": sorted(critical_groups),
        "review_required_groups": sorted(review_groups),
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
    validation_efficacy_audit = dict(
        validation.get("validation_efficacy_audit") or build_validation_efficacy_audit(validation)
    )
    validation_efficacy_route = str(validation_efficacy_audit.get("route") or "")
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
            "Section": "Benchmark Parity",
            "Ready": _ready_from_check(benchmark_check) if benchmark_check else False,
            "Current": benchmark_check.get("Current") or "-",
            "Meaning": "후보와 benchmark가 같은 기간 / coverage / frequency로 비교되는지 봅니다.",
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
            "Meaning": "PIT / replay / benchmark / provider / robustness evidence gap을 최종 선택 전에 분리해서 봅니다.",
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
    gate_policy = build_investability_gate_policy(
        validation=validation,
        paper_observation=paper_observation,
        decision_evidence=decision_evidence,
        packet_checks=checks,
        critical_gaps=critical_gaps,
    )
    checks.append(
        {
            "Section": "Validation Gate Policy",
            "Ready": bool(gate_policy.get("select_allowed")),
            "Current": gate_policy.get("outcome") or "-",
            "Meaning": "profile-aware gate matrix가 실전 검토 통과 후보 선정 가능 여부를 판정합니다.",
        }
    )
    score = round(
        sum(1 for check in checks if bool(check.get("Ready"))) / len(checks) * 10.0,
        1,
    ) if checks else 0.0
    policy_blockers = list(gate_policy.get("blockers") or [])
    policy_review_required = list(gate_policy.get("review_required") or [])
    if policy_blockers:
        route = "INVESTABILITY_PACKET_BLOCKED"
        verdict = "실전 후보 선정 차단: validation gate policy blocker가 남아 있습니다."
        next_action = "선택 대신 보류 / 재검토로 기록하거나 validation evidence를 보강합니다."
    elif policy_review_required:
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "실전 후보 선정 전 추가 검토가 필요합니다."
        next_action = "selected route 대신 보류 / 재검토로 기록하고 부족한 evidence를 보강합니다."
    elif decision_evidence.get("route") == "READY_FOR_FINAL_DECISION":
        route = "INVESTABILITY_PACKET_READY"
        verdict = "실전 검토 통과 후보로 기록 가능한 evidence packet입니다."
        next_action = "Final Review에서 선정 / 보류 / 거절 / 재검토 판단을 기록합니다."
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
        "gate_policy_snapshot": gate_policy,
        "assumptions_and_limits": assumptions,
        "validation_efficacy_audit": validation_efficacy_audit,
        "backtest_realism_audit": backtest_realism_audit,
        "summary": {
            "pass": int(status_counts.get("PASS", 0) or 0),
            "review": int(status_counts.get("REVIEW", 0) or 0),
            "blocked": int(status_counts.get("BLOCKED", 0) or 0),
            "not_run": int(status_counts.get("NOT_RUN", 0) or 0),
            "provider_status": _provider_status_summary(validation),
            "decision_evidence_route": decision_evidence.get("route"),
            "robustness_route": robustness.get("robustness_route"),
            "gate_policy_outcome": gate_policy.get("outcome"),
            "validation_efficacy_route": validation_efficacy_audit.get("route"),
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
    gate_policy = dict(packet.get("gate_policy_snapshot") or {})
    selected = route == SELECT_FOR_PRACTICAL_PORTFOLIO
    select_allowed = bool(gate_policy.get("select_allowed")) if gate_policy else bool(packet.get("select_ready"))
    ready = (not selected) or select_allowed
    current = gate_policy.get("outcome") or packet.get("route") or "packet_not_attached"
    return {
        "Criteria": "Investability evidence packet",
        "Ready": ready,
        "Current": current,
        "Meaning": (
            "실전 검토 통과 후보 선정은 validation gate policy가 허용할 때만 저장합니다."
            if selected
            else "보류 / 거절 / 재검토 판단은 evidence gap이 있어도 기록할 수 있습니다."
        ),
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
        gate_policy = dict(row.get("gate_policy_snapshot") or {})
        if not gate_policy:
            gate_policy = dict(dict(row.get("investability_evidence_packet") or {}).get("gate_policy_snapshot") or {})
        status_display = build_final_review_status_display(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "투자 가능성": FINAL_REVIEW_DECISION_LABELS.get(str(row.get("decision_route") or ""), "재검토 필요"),
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
    gate_policy = dict(raw_decision.get("gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    look_through = dict(risk_snapshot.get("provider_look_through_board") or {})
    if not look_through:
        provider_context = dict(risk_snapshot.get("provider_coverage") or {})
        look_through = dict(provider_context.get("look_through_board") or {})
    robustness_lab = dict(robustness.get("robustness_lab_board") or risk_snapshot.get("robustness_lab_board") or {})
    validation_efficacy = dict(
        risk_snapshot.get("validation_efficacy_audit") or packet.get("validation_efficacy_audit") or {}
    )
    backtest_realism = dict(risk_snapshot.get("backtest_realism_audit") or packet.get("backtest_realism_audit") or {})
    _append_check_rows(display_rows, area="Final Review Evidence", checks=list(evidence.get("checks") or []))
    _append_check_rows(display_rows, area="Investability Packet", checks=list(packet.get("checks") or []))
    _append_check_rows(display_rows, area="Gate Policy", checks=list(gate_policy.get("policy_rows") or []))
    _append_check_rows(display_rows, area="Validation", checks=list(risk_snapshot.get("validation_checks") or []))
    _append_check_rows(display_rows, area="Validation Efficacy", checks=list(validation_efficacy.get("rows") or []))
    _append_check_rows(display_rows, area="Backtest Realism", checks=list(backtest_realism.get("rows") or []))
    _append_check_rows(display_rows, area="Look-through Exposure", checks=list(look_through.get("summary_rows") or []))
    _append_check_rows(display_rows, area="Robustness Lab", checks=list(robustness_lab.get("summary_rows") or []))
    _append_check_rows(display_rows, area="Robustness", checks=list(robustness.get("checks") or []))
    _append_check_rows(display_rows, area="Paper Observation", checks=list(paper_snapshot.get("checks") or []))
    return display_rows


def _markdown_value(value: Any, default: str = "-") -> str:
    text = _safe_text(value, default)
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
    gate_policy = dict(raw_decision.get("gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    operator_decision = dict(raw_decision.get("operator_decision") or {})
    status_display = build_final_review_status_display(raw_decision)
    decision_route = _safe_text(raw_decision.get("decision_route"))
    evidence_checks = build_final_decision_evidence_rows(raw_decision)
    not_ready_count = sum(1 for check in evidence_checks if not bool(check.get("Ready")))
    timeline = dict(monitoring_timeline or {})
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
        "metrics": {
            "component_count": len(raw_decision.get("selected_components") or []),
            "evidence_check_count": len(evidence_checks),
            "not_ready_evidence_check_count": not_ready_count,
            "gate_policy_row_count": len(gate_policy.get("policy_rows") or []),
            "monitoring_timeline_present": bool(timeline),
        },
        "execution_boundary": {
            "write_policy": "read_only_dossier",
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
    "FINAL_REVIEW_DECISION_LABELS",
    "FINAL_REVIEW_STATUS_DISPLAY",
    "SELECT_FOR_PRACTICAL_PORTFOLIO",
    "build_decision_dossier",
    "build_investability_gate_policy",
    "build_investability_evidence_packet",
    "build_final_decision_evidence_rows",
    "build_final_review_decision_display_rows",
    "build_final_review_status_display",
    "build_selected_route_gate",
]
