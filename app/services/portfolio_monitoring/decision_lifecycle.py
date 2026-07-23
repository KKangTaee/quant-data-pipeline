"""Resolve the latest Final Review decision for Portfolio Monitoring."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any, Iterable, Mapping


ROUTE_LABELS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "계속 추적",
    "HOLD_FOR_MORE_PAPER_TRACKING": "관찰 후 재검토",
    "REJECT_FOR_PRACTICAL_USE": "추적 대상에서 제외",
    "RE_REVIEW_REQUIRED": "Level2로 돌려보내기",
}


@dataclass(frozen=True)
class MonitoringDecisionLifecycle:
    """Current monitoring eligibility derived from an append-only decision history."""

    state: str
    locked: bool
    subject_key: str
    requested_decision_id: str
    effective_decision_id: str | None
    latest_route: str | None
    latest_route_label: str
    latest_source_id: str | None
    message: str
    requested_row: dict[str, Any] | None
    effective_row: dict[str, Any] | None

    def to_projection(self) -> dict[str, Any]:
        """Return the JSON-safe state shared with read models and the web UI."""

        return {
            "state": self.state,
            "locked": self.locked,
            "subject_key": self.subject_key,
            "requested_decision_id": self.requested_decision_id,
            "effective_decision_id": self.effective_decision_id,
            "latest_route": self.latest_route,
            "latest_route_label": self.latest_route_label,
            "latest_source_id": self.latest_source_id,
            "message": self.message,
        }


def decision_subject_key(row: Mapping[str, Any]) -> str:
    """Build the most stable available identity for one reviewed candidate."""

    selection_source_id = str(row.get("selection_source_id") or "").strip()
    if selection_source_id:
        return f"selection:{selection_source_id}"
    source_type = str(row.get("source_type") or "").strip()
    source_id = str(row.get("source_id") or "").strip()
    if source_type and source_id:
        return f"source:{source_type}:{source_id}"
    return f"decision:{str(row.get('decision_id') or '').strip()}"


def _decision_order(row: Mapping[str, Any]) -> tuple[str, str, str]:
    return (
        str(row.get("updated_at") or ""),
        str(row.get("created_at") or ""),
        str(row.get("decision_id") or ""),
    )


def latest_final_decision_rows(
    rows: Iterable[Mapping[str, Any]],
) -> list[dict[str, Any]]:
    """Collapse decision history to one deterministic latest row per subject."""

    latest: dict[str, dict[str, Any]] = {}
    for source in rows:
        row = dict(source or {})
        key = decision_subject_key(row)
        if key not in latest or _decision_order(row) > _decision_order(latest[key]):
            latest[key] = row
    return sorted(latest.values(), key=_decision_order, reverse=True)


def resolve_monitoring_decision(
    rows: Iterable[Mapping[str, Any]],
    requested_decision_id: str,
) -> MonitoringDecisionLifecycle:
    """Resolve an item's historical decision reference against current eligibility."""

    normalized = [dict(row or {}) for row in rows]
    clean_id = str(requested_decision_id or "").strip()
    requested = next(
        (
            row
            for row in normalized
            if str(row.get("decision_id") or "").strip() == clean_id
        ),
        None,
    )
    if requested is None:
        return MonitoringDecisionLifecycle(
            state="DECISION_NOT_FOUND",
            locked=True,
            subject_key=f"decision:{clean_id}",
            requested_decision_id=clean_id,
            effective_decision_id=None,
            latest_route=None,
            latest_route_label="판단 기록 없음",
            latest_source_id=None,
            message="Final Review 판단 기록을 찾을 수 없습니다.",
            requested_row=None,
            effective_row=None,
        )

    subject_key = decision_subject_key(requested)
    subject_rows = [
        row for row in normalized if decision_subject_key(row) == subject_key
    ]
    effective = max(subject_rows, key=_decision_order)
    effective_id = str(effective.get("decision_id") or "").strip()
    route = str(effective.get("decision_route") or "").strip()
    selected = effective.get("monitoring_candidate") is True

    if not selected:
        state = "TRACKING_ELIGIBILITY_CHANGED"
        message = (
            "최신 Final Review 판단이 "
            f"{ROUTE_LABELS.get(route, route or '선택 해제')}로 변경되어 "
            "새 계산을 잠갔습니다."
        )
    elif effective_id == clean_id:
        state = "CURRENT_SELECTED"
        message = "현재 Final Review 계속 추적 판단과 일치합니다."
    else:
        state = "SUPERSEDED_SELECTED"
        message = "더 최신의 계속 추적 판단을 적용합니다."

    return MonitoringDecisionLifecycle(
        state=state,
        locked=not selected,
        subject_key=subject_key,
        requested_decision_id=clean_id,
        effective_decision_id=effective_id,
        latest_route=route or None,
        latest_route_label=ROUTE_LABELS.get(route, route or "판단 미지정"),
        latest_source_id=str(effective.get("source_id") or "").strip() or None,
        message=message,
        requested_row=requested,
        effective_row=effective,
    )
