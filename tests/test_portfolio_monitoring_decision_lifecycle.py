from __future__ import annotations

from app.services.portfolio_monitoring.decision_lifecycle import (
    decision_subject_key,
    latest_final_decision_rows,
    resolve_monitoring_decision,
)


def _row(
    decision_id: str,
    *,
    updated_at: str,
    route: str,
    selected: bool,
    selection_source_id: str = "selection-a",
    created_at: str = "",
) -> dict[str, object]:
    return {
        "decision_id": decision_id,
        "updated_at": updated_at,
        "created_at": created_at,
        "decision_route": route,
        "monitoring_candidate": selected,
        "source_type": "practical_validation_result",
        "source_id": f"validation-{decision_id}",
        "selection_source_id": selection_source_id,
    }


def test_latest_non_select_supersedes_old_selected_without_deleting_history() -> None:
    rows = [
        _row(
            "old-selected",
            updated_at="2026-07-22T10:00:00",
            route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            selected=True,
        ),
        _row(
            "new-hold",
            updated_at="2026-07-23T10:00:00",
            route="HOLD_FOR_MORE_PAPER_TRACKING",
            selected=False,
        ),
    ]

    lifecycle = resolve_monitoring_decision(rows, "old-selected")

    assert lifecycle.state == "TRACKING_ELIGIBILITY_CHANGED"
    assert lifecycle.locked is True
    assert lifecycle.effective_decision_id == "new-hold"
    assert lifecycle.requested_row is not None
    assert lifecycle.requested_row["decision_id"] == "old-selected"
    assert lifecycle.effective_row is not None
    assert lifecycle.effective_row["decision_id"] == "new-hold"
    assert lifecycle.to_projection()["latest_route_label"] == "관찰 후 재검토"


def test_new_selected_decision_reactivates_existing_subject() -> None:
    rows = [
        _row(
            "old-selected",
            updated_at="2026-07-21T10:00:00",
            route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            selected=True,
        ),
        _row(
            "hold",
            updated_at="2026-07-22T10:00:00",
            route="HOLD_FOR_MORE_PAPER_TRACKING",
            selected=False,
        ),
        _row(
            "new-selected",
            updated_at="2026-07-23T10:00:00",
            route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            selected=True,
        ),
    ]

    lifecycle = resolve_monitoring_decision(rows, "old-selected")

    assert lifecycle.state == "SUPERSEDED_SELECTED"
    assert lifecycle.locked is False
    assert lifecycle.effective_decision_id == "new-selected"


def test_identity_falls_back_without_collapsing_unrelated_legacy_rows() -> None:
    assert decision_subject_key(
        {"decision_id": "a", "source_type": "validation", "source_id": "same"}
    ) == "source:validation:same"
    assert decision_subject_key({"decision_id": "b"}) == "decision:b"


def test_latest_rows_use_updated_created_and_decision_id_as_stable_order() -> None:
    rows = [
        _row(
            "decision-a",
            updated_at="2026-07-23T10:00:00",
            created_at="2026-07-23T09:00:00",
            route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            selected=True,
        ),
        _row(
            "decision-b",
            updated_at="2026-07-23T10:00:00",
            created_at="2026-07-23T09:00:00",
            route="HOLD_FOR_MORE_PAPER_TRACKING",
            selected=False,
        ),
        _row(
            "other-subject",
            updated_at="2026-07-22T10:00:00",
            route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            selected=True,
            selection_source_id="selection-b",
        ),
    ]

    latest = latest_final_decision_rows(rows)

    assert [row["decision_id"] for row in latest] == [
        "decision-b",
        "other-subject",
    ]


def test_missing_decision_is_locked_without_fabricating_effective_row() -> None:
    lifecycle = resolve_monitoring_decision([], "missing-decision")

    assert lifecycle.state == "DECISION_NOT_FOUND"
    assert lifecycle.locked is True
    assert lifecycle.effective_decision_id is None
    assert lifecycle.requested_row is None
    assert lifecycle.effective_row is None
