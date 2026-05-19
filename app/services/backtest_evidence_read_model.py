from __future__ import annotations

from typing import Any


FINAL_REVIEW_DECISION_LABELS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "투자 가능 후보",
    "HOLD_FOR_MORE_PAPER_TRACKING": "내용 부족 / 관찰 필요",
    "REJECT_FOR_PRACTICAL_USE": "투자하면 안 됨",
    "RE_REVIEW_REQUIRED": "재검토 필요",
}
FINAL_REVIEW_STATUS_DISPLAY = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": {
        "route": "FINAL_REVIEW_DECISION_COMPLETE",
        "verdict": "최종 판단 완료: 실전 후보로 선정됨",
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
                "Criteria": check_row.get("Criteria") or check_row.get("criteria") or "-",
                "Ready": check_row.get("Ready") if "Ready" in check_row else check_row.get("ready"),
                "Current": check_row.get("Current")
                or check_row.get("current")
                or check_row.get("current_value")
                or "-",
                "Meaning": check_row.get("Meaning") or check_row.get("meaning") or "-",
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
    _append_check_rows(display_rows, area="Final Review Evidence", checks=list(evidence.get("checks") or []))
    _append_check_rows(display_rows, area="Validation", checks=list(risk_snapshot.get("validation_checks") or []))
    _append_check_rows(display_rows, area="Robustness", checks=list(robustness.get("checks") or []))
    _append_check_rows(display_rows, area="Paper Observation", checks=list(paper_snapshot.get("checks") or []))
    return display_rows


__all__ = [
    "FINAL_REVIEW_DECISION_LABELS",
    "FINAL_REVIEW_STATUS_DISPLAY",
    "build_final_decision_evidence_rows",
    "build_final_review_decision_display_rows",
    "build_final_review_status_display",
]
