from __future__ import annotations

import pandas as pd

from app.services.backtest_analysis_result_workspace import (
    build_level1_technical_handoff_readiness,
    build_level2_validation_questions,
    build_result_lifecycle,
)


def result_bundle(*, run_id: str = "run-current") -> dict:
    return {
        "strategy_name": "GTAA",
        "summary_df": pd.DataFrame([{"CAGR": 0.12}]),
        "chart_df": pd.DataFrame(
            [{"Date": "2026-06-30", "Total Balance": 100.0}]
        ),
        "result_df": pd.DataFrame(
            [{"Date": "2026-06-30", "Total Balance": 100.0}]
        ),
        "meta": {
            "run_id": run_id,
            "strategy_key": "gtaa",
            "benchmark_available": False,
            "rolling_review_status": "review",
            "etf_operability_status": "unavailable",
            "liquidity_policy_status": "caution",
        },
    }


def test_no_run_is_hidden_and_previous_error_result_is_reference() -> None:
    hidden = build_result_lifecycle(
        result_bundle=None,
        current_configuration_fingerprint="a",
        result_configuration_fingerprint=None,
        result_requires_rerun=False,
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    failed_rerun = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="new",
        result_configuration_fingerprint="old",
        result_requires_rerun=True,
        is_running=False,
        last_error="provider timeout",
        last_error_kind="data",
    )

    assert hidden["state"] == "hidden"
    assert hidden["show_workspace"] is False
    assert failed_rerun["state"] == "error_with_reference"
    assert failed_rerun["show_workspace"] is True
    assert failed_rerun["reference_only"] is True


def test_level1_gate_ignores_practical_validation_signals() -> None:
    lifecycle = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        result_requires_rerun=False,
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    readiness = build_level1_technical_handoff_readiness(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle=result_bundle(),
        lifecycle=lifecycle,
        action_handlers={"save_and_move": lambda payload: None},
    )

    assert readiness["state"] == "ready"
    assert readiness["can_handoff"] is True
    assert readiness["reasons"] == []


def test_practical_validation_gaps_become_level2_questions_once() -> None:
    questions = build_level2_validation_questions(
        meta=result_bundle()["meta"],
        workspace_kind="single_strategy",
        component_bundles=(),
    )

    assert {row["question_id"] for row in questions} >= {
        "benchmark_comparison",
        "rolling_oos_validation",
        "etf_operability",
        "liquidity_realism",
    }
    assert len({row["root_issue_id"] for row in questions}) == len(questions)
