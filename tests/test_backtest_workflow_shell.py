from __future__ import annotations

from app.services.backtest_workflow_shell import (
    build_backtest_workflow_shell,
    resolve_backtest_workflow_shell_intent,
)
from app.web.backtest_workflow_routes import (
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


def test_workflow_shell_projects_three_stages_once_in_route_order() -> None:
    shell = build_backtest_workflow_shell(BACKTEST_STAGE_PRACTICAL_VALIDATION)

    assert [row["stage_key"] for row in shell["stages"]] == [
        BACKTEST_STAGE_ANALYSIS,
        BACKTEST_STAGE_PRACTICAL_VALIDATION,
        BACKTEST_STAGE_FINAL_REVIEW,
    ]
    assert sum(bool(row["is_active"]) for row in shell["stages"]) == 1
    assert shell["active_stage_index"] == 1
    assert shell["active_stage_context"]["title"] == "실전 검증"
    assert "최신 데이터" in shell["active_stage_context"]["responsibility"]


def test_workflow_shell_normalizes_unknown_stage_to_level1() -> None:
    shell = build_backtest_workflow_shell("unknown")

    assert shell["active_stage"] == BACKTEST_STAGE_ANALYSIS
    assert shell["active_stage_context"]["level_label"] == "LEVEL 1"


def test_workflow_shell_accepts_only_new_allowed_noncurrent_intent() -> None:
    accepted = resolve_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
            "nonce": "intent-1",
        },
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce=None,
    )
    duplicate = resolve_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
            "nonce": "intent-1",
        },
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce="intent-1",
    )
    invalid = resolve_backtest_workflow_shell_intent(
        {"type": "select_stage", "stage_key": "unknown", "nonce": "intent-2"},
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce=None,
    )
    current = resolve_backtest_workflow_shell_intent(
        {
            "type": "select_stage",
            "stage_key": BACKTEST_STAGE_ANALYSIS,
            "nonce": "intent-3",
        },
        active_stage=BACKTEST_STAGE_ANALYSIS,
        consumed_nonce=None,
    )

    assert accepted == {
        "accepted": True,
        "stage_key": BACKTEST_STAGE_FINAL_REVIEW,
        "nonce": "intent-1",
    }
    assert duplicate == {"accepted": False}
    assert invalid == {"accepted": False}
    assert current == {"accepted": False}
