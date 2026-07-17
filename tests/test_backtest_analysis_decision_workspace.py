from __future__ import annotations

import json
from datetime import date
from unittest.mock import patch

import pandas as pd

from app.services.backtest_analysis_decision_workspace import (
    _deduplicate_reasons,
    build_backtest_analysis_decision_workspace,
    build_level1_configuration_fingerprint,
    build_level1_readiness_projection,
    build_level1_strategy_catalog,
    level1_strategy_maturity,
)


def test_level1_catalog_groups_each_strategy_once() -> None:
    groups = build_level1_strategy_catalog()
    options = [item["strategy_choice"] for group in groups for item in group["items"]]

    assert options == [
        "Quality + Value",
        "Quality",
        "Value",
        "GTAA",
        "Global Relative Strength",
        "Dual Momentum",
        "Risk Parity Trend",
        "Equal Weight",
        "Risk-On Momentum 5D",
    ]
    assert len(options) == len(set(options))


def test_risk_on_is_development_not_research() -> None:
    assert level1_strategy_maturity("Risk-On Momentum 5D") == "development"
    assert level1_strategy_maturity("GTAA") == "production"


def test_configuration_fingerprint_is_order_independent_and_sensitive() -> None:
    left = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"top": 3, "tickers": ["SPY", "TLT"]},
    )
    reordered = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"tickers": ["SPY", "TLT"], "top": 3},
    )
    changed = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"top": 2, "tickers": ["SPY", "TLT"]},
    )

    assert left == reordered
    assert left != changed


def test_stale_result_is_preserved_and_handoff_blocked() -> None:
    projection = build_level1_readiness_projection(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle={"meta": {"strategy_key": "gtaa"}},
        current_configuration_fingerprint="current",
        result_configuration_fingerprint="previous",
        action_handlers={"save_and_move": lambda: None},
    )

    assert projection["result_freshness"] == "stale"
    assert projection["handoff_state"] == "blocked"
    assert projection["result_available"] is True


def test_development_or_missing_handler_has_no_cta() -> None:
    development = build_level1_readiness_projection(
        workspace_kind="single_strategy",
        strategy_choice="Risk-On Momentum 5D",
        result_bundle={"meta": {"strategy_key": "risk_on_momentum_5d"}},
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        action_handlers={"save_and_move": lambda: None},
    )
    missing = build_level1_readiness_projection(
        workspace_kind="single_strategy",
        strategy_choice="GTAA",
        result_bundle={"meta": {"strategy_key": "gtaa"}},
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        action_handlers={"save_and_move": None},
    )

    assert "save_and_move" not in development["actions"]
    assert "save_and_move" not in missing["actions"]


def test_duplicate_root_reason_is_counted_once() -> None:
    rows = _deduplicate_reasons(
        [
            {"root_issue_id": "price", "message": "가격 확인"},
            {"root_issue_id": "price", "message": "가격 확인"},
        ]
    )

    assert rows == [{"root_issue_id": "price", "message": "가격 확인"}]


def _successful_bundle() -> dict:
    return {
        "strategy_name": "GTAA",
        "summary_df": pd.DataFrame(
            [
                {
                    "CAGR": 0.12,
                    "Maximum Drawdown": -0.18,
                    "Sharpe Ratio": 0.8,
                    "Standard Deviation": 0.14,
                }
            ]
        ),
        "result_df": pd.DataFrame(
            {"Date": ["2026-06-30"], "Total Balance": [11200.0]}
        ),
        "chart_df": pd.DataFrame(
            {"Date": ["2026-06-30"], "Total Balance": [11200.0]}
        ),
        "meta": {
            "strategy_key": "gtaa",
            "promotion_decision": "pass",
            "price_freshness": {"status": "ok"},
            "transaction_cost_bps": 10.0,
        },
    }


def test_workspace_orders_decision_metrics_and_technical_evidence() -> None:
    selection = {"strategy_choice": "GTAA"}
    configuration = {"top": 3}
    fingerprint = build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection=selection,
        configuration=configuration,
    )

    with patch(
        "app.services.backtest_analysis_decision_workspace."
        "build_next_step_readiness_evaluation",
        return_value={"can_enter_practical_validation": True},
    ):
        workspace = build_backtest_analysis_decision_workspace(
            workspace_kind="single_strategy",
            selection=selection,
            configuration=configuration,
            result_bundle=_successful_bundle(),
            result_configuration_fingerprint=fingerprint,
            saved_mixes=[],
            last_error=None,
            last_error_kind=None,
            action_handlers={"save_and_move": lambda: None},
        )

    assert workspace["workspace_phase"] == "result"
    assert workspace["decision"]["headline"] == "Level2 검증 후보로 보낼 수 있습니다"
    assert [row["metric_id"] for row in workspace["decision"]["metrics"]] == [
        "cagr",
        "maximum_drawdown",
        "sharpe_ratio",
        "volatility",
    ]
    assert workspace["details"]["technical_evidence"]["meta"]["strategy_key"] == "gtaa"


def test_first_read_hides_raw_path_and_error_preserves_result() -> None:
    bundle = _successful_bundle()
    bundle["meta"]["warnings"] = [
        "app.runtime.backtest._apply_transaction_cost_postprocess"
    ]

    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={},
        result_bundle=bundle,
        result_configuration_fingerprint="old",
        saved_mixes=[],
        last_error="Backtest data issue: missing SPY",
        last_error_kind="data",
        action_handlers={"save_and_move": lambda: None},
    )

    assert workspace["workspace_phase"] == "error"
    assert workspace["error"]["kind"] == "data_required"
    assert workspace["decision"]["result_available"] is True
    assert "app.runtime" not in str(workspace["decision"])


def test_workspace_projection_is_json_serializable() -> None:
    bundle = _successful_bundle()
    bundle["meta"]["effective_end"] = date(2026, 6, 30)
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration={"start": date(2020, 1, 1)},
        result_bundle=bundle,
        result_configuration_fingerprint="old",
        saved_mixes=[{"saved_at": date(2026, 7, 18)}],
        last_error=None,
        last_error_kind=None,
        action_handlers={},
    )

    json.dumps(workspace, ensure_ascii=False)
