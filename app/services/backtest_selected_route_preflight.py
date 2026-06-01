from __future__ import annotations

from typing import Any

from app.services.backtest_evidence_read_model import build_investability_evidence_packet


PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION = (
    "practical_validation_selected_route_preflight_v1"
)


def build_practical_validation_selected_route_preflight(
    validation: dict[str, Any] | None,
    *,
    source: dict[str, Any] | None = None,
    paper_observation: dict[str, Any] | None = None,
    decision_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Run the Final Review selected-route policy before exposing a validation row."""

    validation_row = dict(validation or {})
    source_row = dict(source or {})
    if not source_row:
        source_row = {
            "source_type": "practical_validation_result",
            "source_id": validation_row.get("validation_id")
            or validation_row.get("selection_source_id"),
        }
    paper_row = dict(paper_observation or validation_row.get("paper_observation") or {})
    paper_row.setdefault("mode", "inline_paper_observation")
    paper_row.setdefault("blockers", [])
    decision_row = dict(decision_evidence or {})
    if not decision_row:
        decision_row = {
            "route": "READY_FOR_FINAL_DECISION",
            "blockers": [],
            "verdict": "Practical Validation selected-route preflight checks selection-critical evidence before Final Review.",
            "next_action": "Final Review에서 최종 후보 선정 저장을 진행합니다.",
        }
    packet = build_investability_evidence_packet(
        source=source_row,
        validation=validation_row,
        paper_observation=paper_row,
        decision_evidence=decision_row,
    )
    policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    select_allowed = bool(policy.get("select_allowed"))
    return {
        "schema_version": PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION,
        "route": (
            "SELECTED_ROUTE_PREFLIGHT_READY"
            if select_allowed
            else "SELECTED_ROUTE_PREFLIGHT_NEEDS_INPUT"
        ),
        "select_allowed": select_allowed,
        "policy_outcome": policy.get("outcome") or "-",
        "suggested_decision_route": policy.get("suggested_decision_route") or "-",
        "next_action": policy.get("next_action") or packet.get("next_action") or "-",
        "blockers": list(policy.get("blockers") or []),
        "review_required": list(policy.get("review_required") or []),
        "policy_rows": list(policy.get("policy_rows") or []),
        "packet_route": packet.get("route"),
        "packet_select_ready": bool(packet.get("select_ready")),
        "open_review_items": len(packet.get("open_review_items") or []),
    }


__all__ = [
    "PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION",
    "build_practical_validation_selected_route_preflight",
]
