from __future__ import annotations

from datetime import date


def test_2026_deadlines_roll_weekend_and_federal_holiday() -> None:
    from app.services.institutional_13f_refresh import form_13f_due_date

    assert form_13f_due_date("2026-03-31") == date(2026, 5, 15)
    assert form_13f_due_date("2026-06-30") == date(2026, 8, 14)
    assert form_13f_due_date("2026-09-30") == date(2026, 11, 16)
    assert form_13f_due_date("2026-12-31") == date(2027, 2, 16)


def test_refresh_action_targets_latest_due_quarter_from_local_manager_periods() -> None:
    from app.services.institutional_13f_refresh import build_institutional_refresh_action

    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-03-31", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )

    assert action == {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "partial",
        "target_report_period": "2026-06-30",
        "target_quarter_label": "2026년 2분기",
        "label": "2026년 2분기 업데이트 확인 및 갱신",
        "description": "버튼을 누르면 SEC 공개 자료를 확인한 뒤 가능한 기관을 갱신합니다.",
        "completed_managers": 1,
        "expected_managers": 2,
        "pending_ciks": ["0001067983"],
        "next_due_date": "2026-11-16",
    }


def test_refresh_action_hides_when_every_expected_manager_is_current() -> None:
    from app.services.institutional_13f_refresh import build_institutional_refresh_action

    action = build_institutional_refresh_action(
        as_of_date="2026-08-17",
        manager_periods={"0001067983": "2026-06-30", "0001350694": "2026-06-30"},
        expected_ciks=["0001067983", "0001350694"],
    )

    assert action["status"] == "current"
    assert action["visible"] is False
    assert action["pending_ciks"] == []
    assert action["next_due_date"] == "2026-11-16"


def test_workbench_payload_preserves_injected_local_refresh_action() -> None:
    from app.services.institutional_portfolios import build_institutional_workbench_payload

    refresh_action = {
        "action_id": "refresh_institutional_13f",
        "visible": True,
        "status": "due",
        "target_report_period": "2026-06-30",
    }

    payload = build_institutional_workbench_payload(
        model={"summary": {}, "holdings": [], "changes": [], "sector_exposure": []},
        managers=[],
        selected_cik=None,
        interest_model=None,
        refresh_action=refresh_action,
    )

    assert payload["refresh_action"] == refresh_action
