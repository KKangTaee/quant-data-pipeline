from __future__ import annotations

from typing import Any

from app.services.backtest_evidence_read_model import build_investability_evidence_packet
from app.services.backtest_final_review_policy import (
    PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION,
    build_selected_route_preflight_from_packet,
)


def build_practical_validation_selected_route_preflight(
    validation: dict[str, Any] | None,
    *,
    source: dict[str, Any] | None = None,
    paper_observation: dict[str, Any] | None = None,
    decision_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Preview Final Review readiness before exposing a validation row."""

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
            "verdict": "Practical Validation previews Final Review readiness evidence before handoff.",
            "next_action": "Final Review에서 Portfolio Monitoring 후보 선정 저장을 진행합니다.",
        }
    packet = build_investability_evidence_packet(
        source=source_row,
        validation=validation_row,
        paper_observation=paper_row,
        decision_evidence=decision_row,
    )
    return build_selected_route_preflight_from_packet(packet)


__all__ = [
    "PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION",
    "build_practical_validation_selected_route_preflight",
]
