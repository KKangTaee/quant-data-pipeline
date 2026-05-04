from __future__ import annotations

from typing import Any

import pandas as pd


POST_SELECTION_REBALANCE_CADENCE_OPTIONS = [
    "monthly_review",
    "quarterly_review",
    "strategy_rebalance_date",
    "threshold_only",
]

POST_SELECTION_CAPITAL_MODE_OPTIONS = [
    "paper_to_small_capital_review",
    "operator_defined_capital",
    "paper_only_until_next_review",
]

POST_SELECTION_READY_HANDOFF_ROUTES = {
    "READY_FOR_FINAL_INVESTMENT_GUIDE",
    "READY_FOR_POST_SELECTION_OPERATING_GUIDE",
}

FINAL_INVESTMENT_VERDICT_LABELS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": {
        "label": "투자 가능 후보",
        "detail": "검증 근거와 관찰 기준이 준비되어 최종 실전 후보로 읽을 수 있습니다.",
        "tone": "positive",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "label": "내용 부족 / 관찰 필요",
        "detail": "바로 투자 후보로 확정하기보다 추가 관찰 근거가 필요합니다.",
        "tone": "warning",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "label": "투자하면 안 됨",
        "detail": "현재 근거로는 실전 후보에서 제외하는 판단입니다.",
        "tone": "danger",
    },
    "RE_REVIEW_REQUIRED": {
        "label": "재검토 필요",
        "detail": "구성, 비중, 검증 근거, 데이터 상태를 다시 확인해야 합니다.",
        "tone": "warning",
    },
}


def _optional_float(value: Any) -> float | None:
    try:
        if value is None or value == "":
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _component_weight_total(components: list[dict[str, Any]]) -> float:
    return round(
        sum(_optional_float(component.get("target_weight")) or 0.0 for component in components),
        4,
    )


def _selected_final_decision_is_eligible(row: dict[str, Any]) -> bool:
    handoff = dict(row.get("phase35_handoff") or {})
    return (
        str(row.get("decision_route") or "") == "SELECT_FOR_PRACTICAL_PORTFOLIO"
        and str(handoff.get("handoff_route") or "") in POST_SELECTION_READY_HANDOFF_ROUTES
    )


def build_final_investment_decision_summary(row: dict[str, Any]) -> dict[str, Any]:
    """Translate final decision routes into plain investment-readiness language."""
    decision_route = str(row.get("decision_route") or "")
    handoff = dict(row.get("phase35_handoff") or {})
    verdict = dict(
        FINAL_INVESTMENT_VERDICT_LABELS.get(
            decision_route,
            {
                "label": "내용 부족 / 재검토 필요",
                "detail": "최종 판단 route가 명확하지 않아 다시 확인해야 합니다.",
                "tone": "warning",
            },
        )
    )
    return {
        "decision_route": decision_route,
        "verdict_label": verdict["label"],
        "verdict_detail": verdict["detail"],
        "tone": verdict["tone"],
        "phase35_handoff": handoff.get("handoff_route") or "-",
        "phase35_next_action": handoff.get("next_action") or "-",
        "eligible_for_final_guide": _selected_final_decision_is_eligible(row),
    }


def build_post_selection_source_options(final_decision_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Build selectable Phase35 sources from final decisions that were explicitly selected."""
    options: list[dict[str, Any]] = []
    for row in final_decision_rows:
        decision_id = str(row.get("decision_id") or "").strip()
        if not decision_id or not _selected_final_decision_is_eligible(row):
            continue
        source_title = str(row.get("source_title") or row.get("source_id") or decision_id)
        updated_at = str(row.get("updated_at") or row.get("created_at") or "-")
        components = list(row.get("selected_components") or [])
        options.append(
            {
                "label": f"{updated_at} | {source_title} | id={decision_id}",
                "decision_id": decision_id,
                "source_title": source_title,
                "row": dict(row),
                "weight_total": _component_weight_total([dict(component or {}) for component in components]),
            }
        )
    return options


def build_post_selection_source_review_rows(final_decision_rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten final decisions so selected and excluded Phase35 sources are easy to distinguish."""
    display_rows: list[dict[str, Any]] = []
    for row in final_decision_rows:
        handoff = dict(row.get("phase35_handoff") or {})
        summary = build_final_investment_decision_summary(row)
        components = [dict(component or {}) for component in list(row.get("selected_components") or [])]
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "투자 가능성": summary["verdict_label"],
                "Phase35 Handoff": handoff.get("handoff_route"),
                "Final Guide Eligible": "Yes" if _selected_final_decision_is_eligible(row) else "No",
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Components": len(components),
                "Weight Total": _component_weight_total(components),
                "Live Approval": "Disabled",
            }
        )
    return pd.DataFrame(display_rows)


def build_post_selection_component_rows(row: dict[str, Any]) -> pd.DataFrame:
    """Flatten selected components from a final decision or saved operating guide."""
    components = list(row.get("target_components") or row.get("selected_components") or [])
    display_rows: list[dict[str, Any]] = []
    for component in components:
        component = dict(component or {})
        display_rows.append(
            {
                "Registry ID": component.get("registry_id"),
                "Title": component.get("title"),
                "Role": component.get("proposal_role"),
                "Target Weight": component.get("target_weight"),
                "Family": component.get("strategy_family"),
                "Benchmark": component.get("benchmark"),
                "Pre-Live": component.get("pre_live_status"),
                "Data Trust": component.get("data_trust_status"),
                "Baseline CAGR": component.get("baseline_cagr"),
                "Baseline MDD": component.get("baseline_mdd"),
            }
        )
    return pd.DataFrame(display_rows)


def default_post_selection_policy_inputs(final_decision_row: dict[str, Any]) -> dict[str, Any]:
    """Derive practical default guide fields from the saved final review observation snapshot."""
    paper = dict(final_decision_row.get("paper_tracking_snapshot") or {})
    review_triggers = list(paper.get("review_triggers") or [])
    benchmark = str(paper.get("tracking_benchmark") or "").strip() or "AOR or selected benchmark"
    cadence = str(paper.get("review_cadence") or "").strip() or "monthly_or_rebalance_review"
    triggers_text = "\n".join(str(trigger) for trigger in review_triggers if str(trigger).strip())
    if not triggers_text:
        triggers_text = (
            "CAGR deterioration review\n"
            "MDD deterioration review\n"
            "Benchmark-relative underperformance review"
        )
    return {
        "capital_mode": "paper_to_small_capital_review",
        "capital_boundary_note": (
            "이 가이드는 투입 기준을 정리하지만 live approval이나 주문 지시가 아니다. "
            "실제 투입 금액은 별도 사용자 판단으로 확정한다."
        ),
        "rebalancing_cadence": "monthly_review" if "monthly" in cadence else "quarterly_review",
        "rebalance_trigger": f"정기 검토일에 target weight를 확인하고, benchmark `{benchmark}` 대비 이탈과 component drift를 같이 본다.",
        "reduce_trigger": "MDD가 baseline보다 의미 있게 악화되거나 핵심 component의 Data Trust가 blocked로 바뀌면 비중 축소를 검토한다.",
        "stop_trigger": "live approval 전 hard blocker, data trust blocked, 또는 전략 전제 훼손이 확인되면 신규 투입을 중단한다.",
        "re_review_trigger": triggers_text,
        "operator_review_note": "Final Review 근거를 운영 기준으로 옮겨 사용자가 직접 확인한다.",
    }


def build_post_selection_readiness(
    *,
    final_decision_row: dict[str, Any],
    capital_mode: str,
    capital_boundary_note: str,
    rebalancing_cadence: str,
    rebalance_trigger: str,
    reduce_trigger: str,
    stop_trigger: str,
    re_review_trigger: str,
) -> dict[str, Any]:
    """Check whether the selected final decision can be read as a usable final guide."""
    components = [dict(component or {}) for component in list(final_decision_row.get("selected_components") or [])]
    weight_total = _component_weight_total(components)
    handoff = dict(final_decision_row.get("phase35_handoff") or {})
    decision_ready = _selected_final_decision_is_eligible(final_decision_row)
    summary = build_final_investment_decision_summary(final_decision_row)
    evidence = dict(final_decision_row.get("decision_evidence_snapshot") or {})
    checks = [
        {
            "Criteria": "Selected final decision",
            "Ready": decision_ready,
            "Current": handoff.get("handoff_route") or "-",
            "Meaning": "Phase35는 최종 선정된 record만 마지막 투자 가능성 확인 대상으로 읽는다.",
            "Score": 2.0,
        },
        {
            "Criteria": "Final investment verdict",
            "Ready": summary["verdict_label"] == "투자 가능 후보",
            "Current": summary["verdict_label"],
            "Meaning": "최종 판단이 투자 가능 후보 / 투자하면 안 됨 / 내용 부족 / 재검토 필요 중 무엇인지 확인한다.",
            "Score": 1.2,
        },
        {
            "Criteria": "Target components",
            "Ready": bool(components) and abs(weight_total - 100.0) <= 0.01,
            "Current": f"components={len(components)}, weight_total={weight_total:.1f}%",
            "Meaning": "투자 후보로 볼 component와 target weight 합계가 명확해야 한다.",
            "Score": 1.4,
        },
        {
            "Criteria": "Evidence package",
            "Ready": evidence.get("route") == "READY_FOR_FINAL_DECISION",
            "Current": evidence.get("route") or "-",
            "Meaning": "검증 / robustness / 관찰 기준이 최종 판단 근거로 묶였는지 본다.",
            "Score": 1.2,
        },
        {
            "Criteria": "Capital boundary",
            "Ready": capital_mode in POST_SELECTION_CAPITAL_MODE_OPTIONS and bool(str(capital_boundary_note).strip()),
            "Current": capital_mode or "-",
            "Meaning": "실제 투입 금액과 승인 경계는 사용자가 별도 판단해야 함을 확인한다.",
            "Score": 1.0,
        },
        {
            "Criteria": "Rebalancing policy",
            "Ready": rebalancing_cadence in POST_SELECTION_REBALANCE_CADENCE_OPTIONS and bool(str(rebalance_trigger).strip()),
            "Current": rebalancing_cadence or "-",
            "Meaning": "언제 비중을 다시 맞출지 기준이 필요하다.",
            "Score": 1.1,
        },
        {
            "Criteria": "Reduce / stop policy",
            "Ready": bool(str(reduce_trigger).strip()) and bool(str(stop_trigger).strip()),
            "Current": "attached" if str(reduce_trigger).strip() and str(stop_trigger).strip() else "-",
            "Meaning": "언제 줄이고 멈출지 기준이 필요하다.",
            "Score": 1.1,
        },
        {
            "Criteria": "Re-review policy",
            "Ready": bool(str(re_review_trigger).strip()),
            "Current": "attached" if str(re_review_trigger).strip() else "-",
            "Meaning": "어떤 조건에서 Final Review나 Candidate Review로 되돌아갈지 남긴다.",
            "Score": 1.2,
        },
        {
            "Criteria": "Execution boundary",
            "Ready": True,
            "Current": "live approval disabled / order instruction disabled",
            "Meaning": "최종 지침 preview는 주문 실행 지시가 아니다.",
            "Score": 0.8,
        },
    ]
    blockers = [str(row["Criteria"]) for row in checks if not row["Ready"]]
    score = round(sum(float(row["Score"]) for row in checks if row["Ready"]), 1)
    if not decision_ready:
        route = "FINAL_INVESTMENT_GUIDE_BLOCKED"
        verdict = "최종 투자 지침 확인 차단: 최종 선정 record가 아님"
        next_action = "Final Review에서 `투자 가능 후보`로 볼 수 있는 최종 판단을 먼저 기록합니다."
    elif blockers:
        route = "FINAL_INVESTMENT_GUIDE_NEEDS_INPUT"
        verdict = "최종 투자 지침 확인 전 보강 필요"
        next_action = "비중 합계, 리밸런싱, 축소 / 중단 / 재검토 기준을 확인합니다."
    else:
        route = "FINAL_INVESTMENT_GUIDE_READY"
        verdict = "기본 투자 후보 확인 가능"
        next_action = "이 화면의 지침을 기준으로 실제 투자 전 사용자가 마지막 판단을 진행합니다."
    return {
        "route": route,
        "score": min(score, 10.0),
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "blockers": blockers,
        "can_use": not blockers,
        "metrics": {
            "component_count": len(components),
            "target_weight_total": weight_total,
            "source_decision_route": final_decision_row.get("decision_route"),
            "source_handoff_route": handoff.get("handoff_route"),
        },
    }


def build_post_selection_guide_preview(
    *,
    final_decision_row: dict[str, Any],
    readiness: dict[str, Any],
    capital_mode: str,
    capital_boundary_note: str,
    rebalancing_cadence: str,
    rebalance_trigger: str,
    reduce_trigger: str,
    stop_trigger: str,
    re_review_trigger: str,
    operator_review_note: str,
) -> dict[str, Any]:
    """Build a non-persistent guide preview from the saved final decision."""
    components = [dict(component or {}) for component in list(final_decision_row.get("selected_components") or [])]
    paper = dict(final_decision_row.get("paper_tracking_snapshot") or {})
    evidence = dict(final_decision_row.get("decision_evidence_snapshot") or {})
    handoff = dict(final_decision_row.get("phase35_handoff") or {})
    summary = build_final_investment_decision_summary(final_decision_row)
    row = {
        "preview_only": True,
        "guide_route": readiness.get("route"),
        "final_investment_verdict": summary["verdict_label"],
        "final_investment_detail": summary["verdict_detail"],
        "source_decision_id": final_decision_row.get("decision_id"),
        "source_decision_route": final_decision_row.get("decision_route"),
        "source_type": final_decision_row.get("source_type"),
        "source_id": final_decision_row.get("source_id"),
        "source_title": final_decision_row.get("source_title") or final_decision_row.get("source_id"),
        "source_phase35_handoff": handoff,
        "target_components": components,
        "target_weight_total": _component_weight_total(components),
        "operating_policy": {
            "capital_mode": capital_mode,
            "capital_boundary_note": str(capital_boundary_note or "").strip(),
            "rebalancing_cadence": rebalancing_cadence,
            "rebalance_trigger": str(rebalance_trigger or "").strip(),
            "reduce_trigger": str(reduce_trigger or "").strip(),
            "stop_trigger": str(stop_trigger or "").strip(),
            "re_review_trigger": str(re_review_trigger or "").strip(),
            "operator_review_note": str(operator_review_note or "").strip(),
        },
        "observation_reference": {
            "tracking_benchmark": paper.get("tracking_benchmark"),
            "review_cadence": paper.get("review_cadence"),
            "baseline_snapshot": paper.get("baseline_snapshot") or {},
            "review_triggers": list(paper.get("review_triggers") or []),
        },
        "source_evidence_snapshot": evidence,
        "guide_readiness_snapshot": readiness,
        "post_selection_handoff": {
            "handoff_route": "FINAL_INVESTMENT_GUIDE_READY" if readiness.get("can_use") else readiness.get("route"),
            "verdict": "기본 실전 후보 포트폴리오 흐름 완료: 최종 판단과 운영 전 기준이 연결됨",
            "next_action": "실제 주문 / live approval은 별도 의사결정으로 유지하고, 이 화면을 기준으로 운영 전 최종 확인을 진행합니다.",
        },
        "live_approval": False,
        "order_instruction": False,
        "notes": (
            "Preview from Backtest > Post-Selection Guide. Final Review remains the durable record. "
            "This preview is not live approval, broker order, or auto-trading."
        ),
    }
    return row
