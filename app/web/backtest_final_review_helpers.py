from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from app.services.backtest_evidence_read_model import (
    FINAL_REVIEW_DECISION_LABELS,
    SELECT_FOR_PRACTICAL_PORTFOLIO,
    build_investability_evidence_packet,
    build_final_review_decision_display_rows,
    build_final_review_status_display,
    build_selected_route_gate,
)
from app.services.backtest_selected_route_preflight import (
    build_practical_validation_selected_route_preflight,
)
from app.runtime import FINAL_SELECTION_DECISION_CURRENT_SCHEMA_VERSION


FINAL_REVIEW_ROUTE_OPTIONS = [
    SELECT_FOR_PRACTICAL_PORTFOLIO,
    "HOLD_FOR_MORE_PAPER_TRACKING",
    "REJECT_FOR_PRACTICAL_USE",
    "RE_REVIEW_REQUIRED",
]
FINAL_REVIEW_ROUTE_DESCRIPTIONS = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "Portfolio Monitoring 후보로 선정합니다. 승인/주문은 아니며 Final Review에서 선정 판단이 완료됩니다.",
    "HOLD_FOR_MORE_PAPER_TRACKING": "근거는 남기되 실제 선정 전 더 관찰합니다.",
    "REJECT_FOR_PRACTICAL_USE": "현재 근거로는 모니터링 후보에서 제외합니다.",
    "RE_REVIEW_REQUIRED": "구성, 비중, 검증 근거, 데이터 상태를 다시 검토합니다.",
}


def _final_review_slug(value: Any) -> str:
    raw = str(value or "").strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw)
    return "_".join(part for part in cleaned.split("_") if part) or "source"


def _final_review_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _final_review_target_components(validation: dict[str, Any]) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    for row in list(validation.get("component_rows") or []):
        row = dict(row or {})
        components.append(
            {
                "registry_id": row.get("Registry ID") or row.get("registry_id") or row.get("component_id"),
                "title": row.get("Title") or row.get("title") or row.get("strategy_name"),
                "proposal_role": row.get("Role") or row.get("proposal_role") or row.get("role"),
                "target_weight": _final_review_optional_float(row.get("Weight") or row.get("target_weight")) or 0.0,
                "strategy_family": row.get("Family") or row.get("strategy_family"),
                "benchmark": row.get("Benchmark") or row.get("benchmark"),
                "universe": row.get("Universe") or row.get("universe"),
                "factors": row.get("Factors") or row.get("factors"),
                "pre_live_status": row.get("Pre-Live") or row.get("pre_live_status"),
                "data_trust_status": row.get("Data Trust") or row.get("data_trust_status"),
                "promotion": row.get("Promotion") or row.get("promotion"),
                "deployment": row.get("Deployment") or row.get("deployment"),
                "baseline_cagr": row.get("CAGR") or row.get("baseline_cagr"),
                "baseline_mdd": row.get("MDD") or row.get("baseline_mdd"),
            }
        )
    return components


def _final_review_baseline_snapshot(validation: dict[str, Any]) -> dict[str, Any]:
    components = _final_review_target_components(validation)
    active_components = [
        component
        for component in components
        if (_final_review_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    weighted_cagr = 0.0
    weighted_mdd = 0.0
    total_weight = 0.0
    cagr_complete = True
    mdd_complete = True
    for component in active_components:
        weight = _final_review_optional_float(component.get("target_weight")) or 0.0
        cagr = _final_review_optional_float(component.get("baseline_cagr"))
        mdd = _final_review_optional_float(component.get("baseline_mdd"))
        if cagr is None:
            cagr_complete = False
        else:
            weighted_cagr += cagr * weight
        if mdd is None:
            mdd_complete = False
        else:
            weighted_mdd += mdd * weight
        total_weight += weight
    return {
        "component_count": len(components),
        "active_component_count": len(active_components),
        "target_weight_total": round(total_weight, 4),
        "weighted_cagr": round(weighted_cagr / total_weight, 6) if total_weight > 0 and cagr_complete else None,
        "weighted_mdd": round(weighted_mdd / total_weight, 6) if total_weight > 0 and mdd_complete else None,
    }


def _build_final_review_phase35_handoff(row: dict[str, Any]) -> dict[str, Any]:
    """Summarize Final Review completion while preserving the persisted handoff field name."""

    decision_route = str(row.get("decision_route") or "")
    evidence = dict(row.get("decision_evidence_snapshot") or {})
    if decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO:
        handoff_route = "FINAL_REVIEW_DECISION_COMPLETE"
        verdict = "최종 판단 완료: Portfolio Monitoring 후보로 선정됨"
        next_action = "Operations > Portfolio Monitoring에서 read-only 사후 점검을 이어갑니다."
    elif decision_route == "HOLD_FOR_MORE_PAPER_TRACKING":
        handoff_route = "WAIT_FOR_MORE_PAPER_TRACKING"
        verdict = "최종 판단 보류: 관찰 근거를 더 쌓아야 함"
        next_action = "추가 관찰 기간 또는 trigger 충족 후 Final Review에서 다시 판단합니다."
    elif decision_route == "REJECT_FOR_PRACTICAL_USE":
        handoff_route = "FINAL_REVIEW_REJECTED"
        verdict = "최종 판단 완료: 모니터링 후보에서 제외됨"
        next_action = "필요하면 Backtest Analysis 또는 Practical Validation으로 되돌아갑니다."
    else:
        handoff_route = "FINAL_REVIEW_REVIEW_REQUIRED"
        verdict = "최종 판단 재검토 필요: 구성 / 비중 / 근거를 다시 확인"
        next_action = "Practical Validation evidence를 보강한 뒤 Final Review 판단을 다시 봅니다."
    return {
        "handoff_route": handoff_route,
        "verdict": verdict,
        "next_action": next_action,
        "requirements": [
            {
                "Requirement": "Final decision route",
                "Status": "READY" if decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO else "NOT_READY",
                "Current": decision_route or "-",
                "Why It Matters": "Final Review에서 Portfolio Monitoring 후보 선정 여부를 명확히 남긴다.",
            },
            {
                "Requirement": "Evidence pack",
                "Status": "READY" if evidence.get("route") == "READY_FOR_FINAL_DECISION" else "REVIEW",
                "Current": evidence.get("route") or "-",
                "Why It Matters": "선정 근거가 Practical Validation evidence와 연결되어야 한다.",
            },
            {
                "Requirement": "Execution boundary",
                "Status": "READY",
                "Current": "live approval disabled / order instruction disabled",
                "Why It Matters": "선정 기록은 주문 실행이 아니라 최종 검토 판단이다.",
            },
        ],
    }


def _build_final_review_selected_component_rows(row: dict[str, Any]) -> pd.DataFrame:
    """Flatten final decision selected components for operator review."""

    display_rows: list[dict[str, Any]] = []
    for component in list(row.get("selected_components") or []):
        component = dict(component or {})
        display_rows.append(
            {
                "Registry ID": component.get("registry_id"),
                "Title": component.get("title"),
                "Role": component.get("proposal_role"),
                "Weight": component.get("target_weight"),
                "Family": component.get("strategy_family"),
                "Benchmark": component.get("benchmark"),
                "Data Trust": component.get("data_trust_status"),
                "Promotion": component.get("promotion"),
                "Deployment": component.get("deployment"),
                "Baseline CAGR": component.get("baseline_cagr"),
                "Baseline MDD": component.get("baseline_mdd"),
            }
        )
    return pd.DataFrame(display_rows)


def _build_final_review_status_display(row: dict[str, Any]) -> dict[str, str]:
    return build_final_review_status_display(row)


def _final_review_practical_validation_label(row: dict[str, Any]) -> str:
    validation_id = str(row.get("validation_id") or "").strip()
    source_title = str(row.get("source_title") or row.get("selection_source_id") or "-")
    route = str(row.get("validation_route") or "-")
    return f"current 검증 결과 | {route} | {source_title} | id={validation_id}"


def _is_final_review_eligible_validation_result(row: dict[str, Any]) -> bool:
    """Return whether a saved Practical Validation result may appear in Final Review."""

    validation = dict(row or {})
    gate = dict(validation.get("final_review_gate") or {})
    base_eligible = False
    if "can_save_and_move" in gate:
        base_eligible = bool(gate.get("can_save_and_move"))
    else:
        handoff = dict(validation.get("final_review_handoff") or {})
        if "allowed" in handoff:
            base_eligible = bool(handoff.get("allowed"))
        else:
            base_eligible = (
                str(validation.get("validation_route") or "").strip().upper() == "READY_FOR_FINAL_REVIEW"
                and not list(validation.get("hard_blockers") or [])
            )
    if not base_eligible:
        return False
    preflight = dict(validation.get("selected_route_preflight") or {})
    if "select_allowed" not in preflight:
        try:
            preflight = build_practical_validation_selected_route_preflight(validation)
        except Exception:
            return False
    return bool(preflight.get("select_allowed"))


def _build_final_review_source_options(
    current_rows: list[dict[str, Any]],
    proposal_rows: list[dict[str, Any]],
    practical_validation_rows: list[dict[str, Any]] | None = None,
    session_practical_source: dict[str, Any] | None = None,
    include_legacy_sources: bool = True,
) -> list[dict[str, Any]]:
    """Build selectable Final Review sources from current Practical Validation results."""
    del current_rows, proposal_rows, include_legacy_sources
    options: list[dict[str, Any]] = []
    session_practical_source = dict(session_practical_source or {})
    session_validation = dict(session_practical_source.get("validation_result") or {})
    if session_validation and _is_final_review_eligible_validation_result(session_validation):
        options.append(
            {
                "label": "현재 Practical Validation source | "
                + _final_review_practical_validation_label(session_validation),
                "source_type": "practical_validation_result",
                "source_id": session_validation.get("validation_id") or session_validation.get("selection_source_id"),
                "source_title": session_validation.get("source_title") or session_validation.get("selection_source_id"),
                "row": session_validation,
            }
        )
    seen_validation_ids = {
        str(session_validation.get("validation_id") or "").strip()
    } if session_validation else set()
    for row in list(practical_validation_rows or []):
        validation_id = str(row.get("validation_id") or "").strip()
        if validation_id and validation_id in seen_validation_ids:
            continue
        if not validation_id:
            continue
        if not _is_final_review_eligible_validation_result(row):
            continue
        options.append(
            {
                "label": _final_review_practical_validation_label(row),
                "source_type": "practical_validation_result",
                "source_id": validation_id,
                "source_title": row.get("source_title") or row.get("selection_source_id") or validation_id,
                "row": dict(row),
            }
        )
    return options


def _build_final_review_validation(
    source: dict[str, Any],
    *,
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Read a selected Practical Validation result through the Final Review contract."""
    del current_rows, pre_live_rows
    source_type = str(source.get("source_type") or "")
    source_row = dict(source.get("row") or {})
    if source_type == "practical_validation_result":
        validation = dict(source_row)
        validation.setdefault("source_type", "practical_validation_result")
        validation.setdefault("validation_route", source_row.get("validation_route") or "NEEDS_REVIEW")
        validation.setdefault("validation_score", source_row.get("validation_score") or 0.0)
        validation.setdefault("hard_blockers", list(source_row.get("hard_blockers") or []))
        validation.setdefault("paper_tracking_gaps", list(source_row.get("paper_tracking_gaps") or []))
        validation.setdefault("review_gaps", list(source_row.get("review_gaps") or []))
        validation.setdefault("component_rows", list(source_row.get("component_rows") or []))
        return validation
    return {
        "source_type": source_type or "unsupported_source",
        "source_id": source.get("source_id"),
        "source_label": source.get("label") or source.get("source_id"),
        "validation_route": "BLOCKED",
        "validation_score": 0.0,
        "hard_blockers": ["Final Review accepts Practical Validation results only."],
        "paper_tracking_gaps": [],
        "review_gaps": [],
        "checks": [],
        "component_rows": [],
    }


def _build_final_review_paper_observation_snapshot(validation: dict[str, Any]) -> dict[str, Any]:
    """Convert validation output into paper-observation criteria without saving a separate ledger."""
    existing = dict(validation.get("paper_observation") or {})
    if existing:
        existing.setdefault("mode", "inline_paper_observation")
        existing.setdefault("route", "PAPER_OBSERVATION_READY")
        existing.setdefault("checks", [])
        existing.setdefault("blockers", [])
        return existing
    baseline = _final_review_baseline_snapshot(validation)
    components = _final_review_target_components(validation)
    active_components = [
        component
        for component in components
        if (_final_review_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    benchmarks = sorted(
        {
            str(component.get("benchmark") or "").strip()
            for component in active_components
            if str(component.get("benchmark") or "").strip() not in {"", "-"}
        }
    )
    default_triggers = [
        "CAGR deterioration review",
        "MDD deterioration review",
        "Pre-Live status drift review",
        "Benchmark-relative underperformance review",
    ]
    target_weight_total = float(baseline.get("target_weight_total") or 0.0)
    checks = [
        {
            "Criteria": "Active components",
            "Ready": bool(active_components),
            "Current": str(len(active_components)),
            "Meaning": "최종 판단에 들어갈 active component가 있는지 봅니다.",
        },
        {
            "Criteria": "Target weight total",
            "Ready": bool(active_components) and abs(target_weight_total - 100.0) <= 0.01,
            "Current": f"{target_weight_total:.1f}%",
            "Meaning": "모니터링 후보 검토 기준 비중이 100%인지 봅니다.",
        },
        {
            "Criteria": "Observation benchmark",
            "Ready": bool(benchmarks),
            "Current": ", ".join(benchmarks) or "-",
            "Meaning": "관찰 성과를 무엇과 비교할지 봅니다.",
        },
        {
            "Criteria": "Review triggers",
            "Ready": True,
            "Current": str(len(default_triggers)),
            "Meaning": "최종 판단 이후에도 다시 볼 조건을 남깁니다.",
        },
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    route = "PAPER_OBSERVATION_READY" if not blockers else "PAPER_OBSERVATION_NEEDS_INPUT"
    return {
        "mode": "inline_paper_observation",
        "route": route,
        "blockers": blockers,
        "baseline_snapshot": baseline,
        "target_components": components,
        "active_components": active_components,
        "tracking_benchmark": benchmarks[0] if benchmarks else None,
        "review_cadence": "monthly_or_rebalance_review",
        "review_triggers": default_triggers,
        "checks": checks,
        "notes": "Paper observation criteria are kept inside the final review record; no separate paper ledger save is required.",
    }


def _build_final_review_decision_evidence_pack(
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
) -> dict[str, Any]:
    """Summarize validation, robustness, and paper observation into one final-review route."""
    robustness = dict(validation.get("robustness_validation") or {})
    validation_route = str(validation.get("validation_route") or "")
    robustness_route = str(robustness.get("robustness_route") or "")
    paper_route = str(paper_observation.get("route") or "")
    validation_ready_routes = {"READY_FOR_ROBUSTNESS_REVIEW", "READY_FOR_FINAL_REVIEW"}
    validation_blocked = validation_route in {"BLOCKED_FOR_LIVE_READINESS", "BLOCKED"}
    robustness_blocked = robustness_route == "BLOCKED_FOR_ROBUSTNESS"
    paper_blocked = bool(paper_observation.get("blockers"))
    checks = [
        {
            "Criteria": "Portfolio validation",
            "Ready": not validation_blocked,
            "Current": validation_route or "-",
            "Meaning": "구성 / 비중 / 후보 상태가 최종 검토 전에 차단 상태인지 봅니다.",
            "Score": 2.4,
        },
        {
            "Criteria": "Robustness preview",
            "Ready": not robustness_blocked,
            "Current": robustness_route or "-",
            "Meaning": "기간 / 설정 / benchmark / 성과 snapshot blocker가 있는지 봅니다.",
            "Score": 2.2,
        },
        {
            "Criteria": "Paper observation criteria",
            "Ready": not paper_blocked,
            "Current": paper_route or "-",
            "Meaning": "별도 ledger 저장 없이 모니터링 후보 선정 저장에 남길 관찰 기준이 충분한지 봅니다.",
            "Score": 2.0,
        },
        {
            "Criteria": "Execution boundary",
            "Ready": True,
            "Current": "live approval disabled / order instruction disabled",
            "Meaning": "최종 검토 기록이 주문이나 자동매매가 아님을 고정합니다.",
            "Score": 0.8,
        },
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    score = round(sum(float(row["Score"]) for row in checks if row["Ready"]), 1)
    if blockers:
        route = "FINAL_DECISION_BLOCKED"
        verdict = "최종 판단 전 보강 필요: validation / robustness / paper observation blocker가 남아 있음"
        next_action = "blocker를 해결한 뒤 Final Review에서 모니터링 후보 선정 가능 여부를 다시 확인합니다."
        suggested_decision_route = "RE_REVIEW_REQUIRED"
    elif validation_route not in validation_ready_routes or robustness_route != "READY_FOR_STRESS_SWEEP":
        route = "FINAL_DECISION_NEEDS_REVIEW"
        verdict = "모니터링 후보 선정 전 추가 검토 필요: hard blocker는 없지만 검증 보강 항목이 남아 있음"
        next_action = "더 관찰하거나 보강 후 선정 판단을 다시 봅니다."
        suggested_decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
    else:
        route = "READY_FOR_FINAL_DECISION"
        verdict = "최종 검토 가능: 검증 근거와 관찰 기준이 하나의 판단 기록으로 묶임"
        next_action = "모니터링 후보 선정과 사유를 저장하면 Final Review에서 Dashboard 추적 후보 판단이 완료됩니다."
        suggested_decision_route = "SELECT_FOR_PRACTICAL_PORTFOLIO"
    return {
        "route": route,
        "score": min(score, 10.0),
        "verdict": verdict,
        "next_action": next_action,
        "suggested_decision_route": suggested_decision_route,
        "checks": checks,
        "blockers": blockers,
        "metrics": {
            "validation_route": validation_route,
            "validation_score": validation.get("validation_score"),
            "robustness_route": robustness_route,
            "robustness_score": robustness.get("robustness_score"),
            "paper_observation_route": paper_route,
            "active_components": len(paper_observation.get("active_components") or []),
            "target_weight_total": dict(paper_observation.get("baseline_snapshot") or {}).get("target_weight_total"),
        },
    }


def _build_investability_evidence_packet(
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    evidence: dict[str, Any],
) -> dict[str, Any]:
    return build_investability_evidence_packet(
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        decision_evidence=evidence,
    )


def _build_final_review_save_evaluation(
    *,
    evidence: dict[str, Any],
    investability_packet: dict[str, Any] | None = None,
    decision_id: str,
    decision_route: str,
    operator_reason: str,
    existing_decision_ids: set[str],
) -> dict[str, Any]:
    """Check whether the final review can be recorded as one durable decision row."""
    decision_id_clean = str(decision_id or "").strip()
    decision_route_clean = str(decision_route or "").strip()
    packet_gate = build_selected_route_gate(
        decision_route=decision_route_clean,
        investability_packet=investability_packet,
    )
    checks = [
        {
            "Criteria": "Decision identity",
            "Ready": bool(decision_id_clean) and decision_id_clean not in existing_decision_ids,
            "Current": decision_id_clean or "-",
            "Meaning": "중복되지 않는 최종 검토 기록 id가 필요합니다.",
        },
        {
            "Criteria": "Official selection route",
            "Ready": decision_route_clean == SELECT_FOR_PRACTICAL_PORTFOLIO,
            "Current": decision_route_clean or "-",
            "Meaning": "Final Review의 정식 저장은 모니터링 후보 선정 route만 허용합니다. 보류 / 거절 / 재검토는 저장하지 않는 상태 안내입니다.",
        },
        {
            "Criteria": "Operator reason",
            "Ready": bool(str(operator_reason or "").strip()),
            "Current": "attached" if str(operator_reason or "").strip() else "-",
            "Meaning": "왜 이 판단을 했는지 남깁니다.",
        },
        {
            "Criteria": "Select readiness",
            "Ready": evidence.get("route") == "READY_FOR_FINAL_DECISION",
            "Current": evidence.get("route") or "-",
            "Meaning": "모니터링 후보 선정은 blocker가 없을 때만 저장합니다.",
        },
        packet_gate,
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    if not blockers:
        route = "FINAL_SELECTION_SAVE_READY"
        verdict = "모니터링 후보 선정 저장 가능"
        next_action = "`모니터링 후보로 선정`을 눌러 선정 근거를 남깁니다."
    else:
        route = "FINAL_SELECTION_SAVE_BLOCKED"
        verdict = "모니터링 후보 선정 저장 전 확인 필요"
        next_action = "decision id, 선정 사유, selection gate, investability packet을 확인합니다."
    return {
        "route": route,
        "score": round((len(checks) - len(blockers)) / len(checks) * 10.0, 1),
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "blockers": blockers,
        "can_save": not blockers,
    }


def _build_final_review_decision_row(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    evidence: dict[str, Any],
    investability_packet: dict[str, Any] | None = None,
    decision_id: str,
    decision_route: str,
    operator_reason: str,
    operator_constraints: str,
    operator_next_action: str,
) -> dict[str, Any]:
    """Create one final review record that includes validation, observation, and decision evidence."""
    now = datetime.now().isoformat(timespec="seconds")
    source_id = str(source.get("source_id") or "").strip()
    gate_policy_snapshot = dict(dict(investability_packet or {}).get("gate_policy_snapshot") or {})
    selection_gate_policy_snapshot = dict(
        dict(investability_packet or {}).get("selection_gate_policy_snapshot") or gate_policy_snapshot
    )
    deployment_readiness_policy_snapshot = dict(
        dict(investability_packet or {}).get("deployment_readiness_policy_snapshot") or {}
    )
    open_review_items = list(dict(investability_packet or {}).get("open_review_items") or [])
    row = {
        "schema_version": FINAL_SELECTION_DECISION_CURRENT_SCHEMA_VERSION,
        "decision_id": str(decision_id or "").strip(),
        "created_at": now,
        "updated_at": now,
        "decision_status": "recorded",
        "decision_route": str(decision_route or "").strip(),
        "selected_practical_portfolio": decision_route == "SELECT_FOR_PRACTICAL_PORTFOLIO",
        "source_paper_ledger_id": None,
        "source_observation_id": f"paper_observation_{_final_review_slug(source_id)}",
        "source_type": source.get("source_type"),
        "source_id": source_id,
        "source_title": source.get("source_title") or source_id,
        "selection_source_id": validation.get("selection_source_id"),
        "validation_id": validation.get("validation_id"),
        "selected_components": list(paper_observation.get("active_components") or []),
        "decision_evidence_snapshot": evidence,
        "investability_evidence_packet": dict(investability_packet or {}),
        "gate_policy_snapshot": selection_gate_policy_snapshot,
        "selection_gate_policy_snapshot": selection_gate_policy_snapshot,
        "deployment_readiness_policy_snapshot": deployment_readiness_policy_snapshot,
        "open_review_items": open_review_items,
        "risk_and_validation_snapshot": {
            "validation_route": validation.get("validation_route"),
            "validation_score": validation.get("validation_score"),
            "validation_checks": list(validation.get("checks") or []),
            "validation_profile": dict(validation.get("validation_profile") or {}),
            "diagnostic_summary": dict(validation.get("diagnostic_summary") or {}),
            "diagnostic_display_rows": list(validation.get("diagnostic_display_rows") or []),
            "diagnostic_results": list(validation.get("diagnostic_results") or []),
            "provider_coverage": dict(validation.get("provider_coverage") or {}),
            "provider_coverage_display_rows": list(validation.get("provider_coverage_display_rows") or []),
            "validation_efficacy_audit": dict(validation.get("validation_efficacy_audit") or {}),
            "validation_efficacy_display_rows": list(validation.get("validation_efficacy_display_rows") or []),
            "data_coverage_audit": dict(validation.get("data_coverage_audit") or {}),
            "data_coverage_display_rows": list(validation.get("data_coverage_display_rows") or []),
            "construction_risk_audit": dict(validation.get("construction_risk_audit") or {}),
            "construction_risk_display_rows": list(validation.get("construction_risk_display_rows") or []),
            "risk_contribution_audit": dict(validation.get("risk_contribution_audit") or {}),
            "risk_contribution_display_rows": list(validation.get("risk_contribution_display_rows") or []),
            "component_role_weight_audit": dict(validation.get("component_role_weight_audit") or {}),
            "component_role_weight_display_rows": list(validation.get("component_role_weight_display_rows") or []),
            "backtest_realism_audit": dict(validation.get("backtest_realism_audit") or {}),
            "backtest_realism_display_rows": list(validation.get("backtest_realism_display_rows") or []),
            "robustness_run_set": dict(validation.get("robustness_run_set") or {}),
            "profile_score_rows": list(validation.get("profile_score_rows") or []),
            "curve_evidence": dict(validation.get("curve_evidence") or {}),
            "rolling_validation": dict(validation.get("rolling_validation") or {}),
            "not_run_domains": list(validation.get("not_run_domains") or []),
            "not_run_critical_domains": list(validation.get("not_run_critical_domains") or []),
            "intent_mismatch_warnings": list(validation.get("intent_mismatch_warnings") or []),
            "robustness_validation": dict(validation.get("robustness_validation") or {}),
        },
        "paper_tracking_snapshot": paper_observation,
        "operator_decision": {
            "reason": str(operator_reason or "").strip(),
            "constraints": str(operator_constraints or "").strip(),
            "next_action": str(operator_next_action or "").strip(),
        },
        "live_approval": False,
        "order_instruction": False,
        "notes": (
            "Created from Backtest > Final Review. This record combines validation, robustness, "
            "paper observation criteria, operator judgment, and open review items. "
            "It is not live approval, deployment approval, or an order instruction."
        ),
    }
    row["phase35_handoff"] = _build_final_review_phase35_handoff(row)
    return row


def _build_final_review_decision_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten final decision records for the Final Review saved-record table."""
    return pd.DataFrame(build_final_review_decision_display_rows(rows))
