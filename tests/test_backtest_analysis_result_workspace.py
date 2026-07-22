from __future__ import annotations

from inspect import signature
from unittest.mock import MagicMock, patch

import pandas as pd

from app.services.backtest_analysis_result_workspace import (
    build_backtest_analysis_result_workspace,
    build_level1_technical_handoff_readiness,
    build_level2_validation_questions,
    build_result_lifecycle,
)
from app.web.backtest_analysis_result_workspace import (
    validate_result_workspace_intent,
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


def test_lifecycle_accepts_python_owned_reference_reason() -> None:
    assert "reference_reason" in signature(build_result_lifecycle).parameters


def test_reference_only_lifecycle_explains_settings_price_and_failure_reasons() -> None:
    settings = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="new",
        result_configuration_fingerprint="old",
        result_requires_rerun=True,
        is_running=False,
        last_error=None,
        last_error_kind=None,
    )
    price = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        result_requires_rerun=True,
        is_running=False,
        last_error=None,
        last_error_kind=None,
        reference_reason="price_refresh",
    )
    failed = build_result_lifecycle(
        result_bundle=result_bundle(),
        current_configuration_fingerprint="new",
        result_configuration_fingerprint="old",
        result_requires_rerun=True,
        is_running=False,
        last_error="provider timeout",
        last_error_kind="data",
    )

    assert settings.get("reference_reason") == "settings_changed"
    assert settings.get("reference_message") == (
        "현재 설정으로 다시 실행하면 Level2 인계를 다시 확인할 수 있습니다."
    )
    assert price["display_label"] == "가격 갱신 전 결과 · 참고용"
    assert price.get("reference_reason") == "price_refresh"
    assert failed.get("reference_reason") == "rerun_failed"
    assert failed.get("reference_message") == (
        "재실행에 실패해 마지막 성공 결과를 참고용으로 유지합니다."
    )


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


def _build_workspace(
    bundle: dict,
    *,
    workspace_kind: str = "single_strategy",
    strategy_choice: str | None = "GTAA",
    component_bundles: tuple[dict, ...] = (),
) -> dict:
    return build_backtest_analysis_result_workspace(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=bundle,
        current_configuration_fingerprint="same",
        result_configuration_fingerprint="same",
        result_requires_rerun=False,
        is_running=False,
        last_error=None,
        last_error_kind=None,
        action_handlers={"save_and_move": lambda payload: None},
        component_bundles=component_bundles,
    )


def test_holdings_projects_current_and_last_valid_signal_without_future_guess() -> None:
    bundle = result_bundle()
    bundle["result_df"] = pd.DataFrame(
        [
            {
                "Date": "2026-05-31",
                "Rebalancing": True,
                "End Ticker": ["SPY"],
                "End Balance": [100.0],
                "Next Ticker": ["SPY", "TLT"],
                "Next Weight": [0.6, 0.4],
                "Added Ticker": ["TLT"],
                "Removed Ticker": [],
                "Cash": 0.0,
                "Total Balance": 100.0,
            },
            {
                "Date": "2026-06-30",
                "Rebalancing": False,
                "End Ticker": ["SPY", "TLT"],
                "End Balance": [63.0, 39.0],
                "Next Ticker": ["SPY", "TLT"],
                "Next Balance": [63.0, 39.0],
                "Cash": 0.0,
                "Total Balance": 102.0,
            },
        ]
    )

    model = _build_workspace(bundle)

    assert model["holdings"]["current_allocation"] == [
        {"ticker": "SPY", "weight": 0.617647, "weight_label": "61.8%"},
        {"ticker": "TLT", "weight": 0.382353, "weight_label": "38.2%"},
    ]
    assert model["holdings"]["target_allocation"] == [
        {"ticker": "SPY", "weight": 0.6, "weight_label": "60.0%"},
        {"ticker": "TLT", "weight": 0.4, "weight_label": "40.0%"},
    ]
    assert model["holdings"]["status"] == "hold_current_until_rebalance"


def test_cash_only_is_not_an_empty_holding_state() -> None:
    bundle = result_bundle()
    bundle["result_df"] = pd.DataFrame(
        [
            {
                "Date": "2026-06-30",
                "Rebalancing": True,
                "End Ticker": [],
                "End Balance": [],
                "Next Ticker": [],
                "Next Balance": [],
                "Cash": 100.0,
                "Total Balance": 100.0,
            }
        ]
    )

    model = _build_workspace(bundle)

    assert model["holdings"]["current_allocation"] == [
        {"ticker": "현금", "weight": 1.0, "weight_label": "100.0%"}
    ]
    assert model["holdings"]["status"] == "cash_only"


def test_user_tables_and_chart_use_stable_labels_not_raw_columns() -> None:
    bundle = result_bundle()
    bundle["summary_df"] = pd.DataFrame(
        [
            {
                "Start Date": "2026-05-31",
                "End Date": "2026-06-30",
                "Start Balance": 100.0,
                "End Balance": 102.0,
                "CAGR": 0.24,
                "Maximum Drawdown": -0.05,
                "Sharpe Ratio": 1.2,
                "Standard Deviation": 0.15,
            }
        ]
    )
    bundle["chart_df"] = pd.DataFrame(
        [
            {"Date": "2026-05-31", "Total Balance": 100.0},
            {"Date": "2026-06-30", "Total Balance": 102.0},
        ]
    )
    bundle["result_df"] = pd.DataFrame(
        [
            {
                "Date": "2026-05-31",
                "Total Balance": 100.0,
                "Total Return": 0.0,
                "End Ticker": [],
                "End Balance": [],
                "Next Ticker": ["SPY"],
                "Next Balance": [100.0],
                "Rebalancing": True,
                "Cash": 0.0,
            },
            {
                "Date": "2026-06-30",
                "Total Balance": 102.0,
                "Total Return": 0.02,
                "End Ticker": ["SPY"],
                "End Balance": [102.0],
                "Next Ticker": ["SPY"],
                "Next Balance": [102.0],
                "Rebalancing": False,
                "Cash": 0.0,
            },
        ]
    )

    model = _build_workspace(bundle)

    assert [item["metric_id"] for item in model["performance_summary"]] == [
        "period",
        "cumulative_return",
        "cagr",
        "maximum_drawdown",
        "sharpe",
        "volatility",
    ]
    assert model["chart"]["strategy_series"][0]["value"] == 100.0
    assert list(model["performance_rows"][0]) == [
        "date",
        "balance",
        "period_return",
        "drawdown",
        "holding_count",
        "turnover",
        "cost",
    ]
    assert "Total Balance" not in model["performance_rows"][0]
    assert [group["group_id"] for group in model["evidence_groups"]] == [
        "performance_risk",
        "selection_holdings",
        "execution_realism",
        "data_trust",
    ]


def test_chart_publishes_real_date_ticks_returns_and_benchmark_identity() -> None:
    bundle = result_bundle()
    dates = pd.date_range("2026-01-31", periods=7, freq="ME")
    bundle["chart_df"] = pd.DataFrame(
        {"Date": dates, "Total Balance": [100, 101, 99, 104, 108, 110, 124.9]}
    )
    bundle["benchmark_chart_df"] = pd.DataFrame(
        {
            "Date": dates,
            "Benchmark Total Balance": [100, 100, 101, 103, 104, 106, 112],
        }
    )
    bundle["meta"].update(
        {
            "benchmark_ticker": "SPY",
            "benchmark_label": "S&P 500 (SPY)",
            "benchmark_contract": "ticker",
        }
    )

    chart = _build_workspace(bundle)["chart"]

    assert chart["normalized_base"] == 100.0
    assert "124.9" in chart["normalized_explanation"]
    assert chart["benchmark"]["label"] == "S&P 500 (SPY)"
    assert chart["benchmark"]["contract_label"] == "대표 ETF 비교"
    assert chart["timeline_dates"] == [date.date().isoformat() for date in dates]
    assert len(chart["desktop_x_ticks"]) == 6
    assert len(chart["compact_x_ticks"]) == 3
    assert chart["desktop_x_ticks"][0]["date"] == "2026-01-31"
    assert chart["desktop_x_ticks"][-1]["date"] == "2026-07-31"
    assert chart["hover_rows"][-1]["strategy_return_label"] == "+24.9%"
    assert chart["hover_rows"][-1]["benchmark_return_label"] == "+12.0%"


def test_sparse_benchmark_keeps_timeline_positions_without_fake_values() -> None:
    bundle = result_bundle()
    bundle["chart_df"] = pd.DataFrame(
        [
            {"Date": "2026-01-31", "Total Balance": 100.0},
            {"Date": "2026-02-28", "Total Balance": 105.0},
            {"Date": "2026-03-31", "Total Balance": 110.0},
        ]
    )
    bundle["benchmark_chart_df"] = pd.DataFrame(
        [
            {"Date": "2026-01-31", "Benchmark Total Balance": 100.0},
            {"Date": "2026-03-31", "Benchmark Total Balance": 104.0},
        ]
    )
    bundle["meta"]["benchmark_ticker"] = "SPY"

    chart = _build_workspace(bundle)["chart"]

    assert chart["timeline_dates"] == [
        "2026-01-31",
        "2026-02-28",
        "2026-03-31",
    ]
    assert chart["hover_rows"][1]["benchmark_value"] is None
    assert [row["date"] for row in chart["benchmark_series"]] == [
        "2026-01-31",
        "2026-03-31",
    ]


def test_holdings_schedule_separates_signal_rebalance_and_next_window() -> None:
    bundle = result_bundle()
    bundle["meta"]["rebalance_interval"] = 3
    bundle["result_df"] = pd.DataFrame(
        [
            {
                "Date": "2026-03-31",
                "Rebalancing": True,
                "End Ticker": ["SPY"],
                "End Balance": [100.0],
                "Next Ticker": ["SPY", "TLT"],
                "Next Weight": [0.6, 0.4],
                "Total Balance": 100.0,
                "Cash": 0.0,
            },
            {
                "Date": "2026-04-30",
                "Rebalancing": False,
                "End Ticker": ["SPY", "TLT"],
                "End Balance": [61.0, 41.0],
                "Next Ticker": ["SPY", "TLT"],
                "Next Balance": [61.0, 41.0],
                "Total Balance": 102.0,
                "Cash": 0.0,
            },
        ]
    )

    schedule = _build_workspace(bundle)["holdings"]["schedule"]

    assert schedule["valuation_as_of"] == "2026-04-30"
    assert schedule["latest_signal_as_of"] == "2026-03-31"
    assert schedule["last_rebalance_as_of"] == "2026-03-31"
    assert schedule["cadence_label"] == "3개월마다"
    assert schedule["next_window_label"] == "2026-06 월말 예상"
    assert schedule["next_window_status"] == "estimated_window"


def test_missing_cadence_never_invents_next_rebalance_date() -> None:
    bundle = result_bundle()
    bundle["result_df"]["Rebalancing"] = True

    schedule = _build_workspace(bundle)["holdings"]["schedule"]

    assert schedule["last_rebalance_as_of"] == "2026-06-30"
    assert schedule["cadence_label"] == "주기 근거 없음"
    assert schedule["next_window_label"] == "다음 일정 확인 필요"
    assert schedule["next_window_status"] == "unknown"


def test_calculation_and_data_basis_hides_raw_keys_from_first_layer() -> None:
    bundle = result_bundle()
    bundle["meta"].update(
        {
            "execution_mode": "db",
            "transaction_cost_bps": 10.0,
            "universe_name": "GTAA Universe",
            "benchmark_ticker": "SPY",
            "unknown_provider_payload": {"raw": True},
        }
    )

    appendix = _build_workspace(bundle)["technical_appendix"]

    assert [section["section_id"] for section in appendix["sections"]] == [
        "calculation_basis",
        "data_basis",
        "result_trace",
    ]
    visible_labels = [
        row["label"]
        for section in appendix["sections"]
        for row in section["rows"]
    ]
    assert "실행 방식" in visible_labels
    assert "기준지수" in visible_labels
    assert "unknown_provider_payload" not in visible_labels
    assert "unknown_provider_payload" in appendix["raw"]["meta"]


def test_missing_holdings_stays_unavailable_instead_of_guessing_equal_weights() -> None:
    bundle = result_bundle()
    bundle["result_df"] = pd.DataFrame(
        [{"Date": "2026-06-30", "Total Balance": 100.0, "Ticker": ["SPY", "TLT"]}]
    )

    model = _build_workspace(bundle)

    assert model["holdings"]["status"] == "unavailable"
    assert model["holdings"]["current_allocation"] == []
    assert model["holdings"]["unavailable_reason"]


def test_result_column_boundary_matrix_keeps_each_family_visible_and_deduplicated() -> None:
    base_rows = {
        "equal_weight": {
            "Date": "2026-06-30",
            "Ticker": ["SPY", "TLT"],
            "End Balance": [55.0, 45.0],
            "Next Balance": [50.0, 50.0],
            "Total Balance": 100.0,
            "Rebalancing": True,
            "Cash": 0.0,
        },
        "gtaa": {
            "Date": "2026-06-30",
            "End Ticker": ["SPY", "TLT"],
            "End Balance": [60.0, 40.0],
            "Next Ticker": ["SPY", "TLT"],
            "Next Weight": [0.6, 0.4],
            "Total Balance": 100.0,
            "Rebalancing": True,
            "Cash": 0.0,
        },
        "global_relative_strength": {
            "Date": "2026-06-30",
            "End Ticker": ["SPY"],
            "End Balance": [100.0],
            "Next Ticker": ["SPY"],
            "Next Balance": [100.0],
            "Total Balance": 100.0,
            "Rebalancing": False,
            "Cash": 0.0,
        },
        "risk_parity_trend": {
            "Date": "2026-06-30",
            "End Ticker": ["SPY", "IEF"],
            "End Balance": [70.0, 30.0],
            "Next Ticker": ["SPY", "IEF"],
            "Next Weight": [0.7, 0.3],
            "Total Balance": 100.0,
            "Rebalancing": True,
            "Cash": 0.0,
        },
        "dual_momentum": {
            "Date": "2026-06-30",
            "End Ticker": ["SPY"],
            "End Balance": [100.0],
            "Next Ticker": ["SPY"],
            "Next Balance": [100.0],
            "Total Balance": 100.0,
            "Rebalancing": True,
            "Cash": 0.0,
        },
        "quality_snapshot_strict_annual": {
            "Date": "2026-06-30",
            "End Ticker": ["AAPL", "MSFT"],
            "End Balance": [50.0, 50.0],
            "Next Ticker": ["AAPL", "MSFT"],
            "Next Balance": [50.0, 50.0],
            "Total Balance": 100.0,
            "Rebalancing": True,
            "Cash": 0.0,
        },
    }
    for index, (strategy_key, row) in enumerate(base_rows.items()):
        bundle = result_bundle(run_id=f"run-{index}")
        bundle["meta"].update({"strategy_key": strategy_key})
        bundle["result_df"] = pd.DataFrame([row])
        model = _build_workspace(
            bundle,
            strategy_choice="Equal Weight" if strategy_key == "equal_weight" else "GTAA",
        )

        assert model["visible"] is True
        assert model["identity"]["run_result_id"] == f"run-{index}"
        assert model["holdings"]["status"] in {
            "available",
            "cash_only",
            "hold_current_until_rebalance",
            "partial",
            "unavailable",
        }
        questions = model["level2_validation_questions"]
        assert len({row["root_issue_id"] for row in questions}) == len(questions)


def test_portfolio_mix_keeps_component_evidence_partial_without_guessing() -> None:
    mix = result_bundle(run_id="mix-run")
    mix["strategy_name"] = "Portfolio Mix"
    first = result_bundle(run_id="component-a")
    first["strategy_name"] = "GTAA"
    first["meta"].update({"component_id": "a", "component_weight": 0.6})
    first["result_df"] = pd.DataFrame(
        [
            {
                "Date": "2026-06-30",
                "End Ticker": ["SPY"],
                "End Balance": [100.0],
                "Next Ticker": ["SPY"],
                "Next Weight": [1.0],
                "Total Balance": 100.0,
                "Rebalancing": True,
                "Cash": 0.0,
            }
        ]
    )
    second = result_bundle(run_id="component-b")
    second["strategy_name"] = "Risk Parity Trend"
    second["meta"].update({"component_id": "b", "component_weight": 0.4})

    model = _build_workspace(
        mix,
        workspace_kind="portfolio_mix",
        strategy_choice=None,
        component_bundles=(first, second),
    )

    assert model["holdings"]["status"] == "partial"
    assert model["holdings"]["evidence_status"] == "partial"
    assert [row["component_id"] for row in model["holdings"]["components"]] == [
        "a",
        "b",
    ]
    assert model["holdings"]["target_allocation"] == []


def test_result_intent_requires_exact_current_run_and_enabled_action() -> None:
    workspace = {
        "configuration_fingerprint": "fingerprint-current",
        "identity": {"run_result_id": "run-current"},
        "actions": {"save_and_move": {"enabled": True}},
    }

    accepted = validate_result_workspace_intent(
        {
            "action": "save_and_move",
            "payload": {
                "run_result_id": "run-current",
                "current_configuration_fingerprint": "fingerprint-current",
            },
            "nonce": "n-1",
        },
        workspace=workspace,
    )
    stale = validate_result_workspace_intent(
        {
            "action": "save_and_move",
            "payload": {
                "run_result_id": "run-old",
                "current_configuration_fingerprint": "fingerprint-current",
            },
            "nonce": "n-2",
        },
        workspace=workspace,
    )
    disabled = validate_result_workspace_intent(
        {
            "action": "save_and_move",
            "payload": {
                "run_result_id": "run-current",
                "current_configuration_fingerprint": "fingerprint-current",
            },
            "nonce": "n-3",
        },
        workspace={**workspace, "actions": {}},
    )

    assert accepted["ok"] is True
    assert stale == {"ok": False, "reason": "run_identity_mismatch"}
    assert disabled == {"ok": False, "reason": "action_unavailable"}


def test_result_component_defers_intent_consumption_to_fragment_body() -> None:
    from app.web import backtest_analysis_result_workspace as result_workspace

    workspace = {
        "visible": True,
        "configuration_fingerprint": "fingerprint-current",
        "identity": {"run_result_id": "run-current"},
        "actions": {"save_and_move": {"enabled": True}},
    }
    intent = {
        "action": "save_and_move",
        "payload": {
            "run_result_id": "run-current",
            "current_configuration_fingerprint": "fingerprint-current",
        },
        "nonce": "handoff-fragment-1",
    }
    fake_streamlit = MagicMock()

    with (
        patch.object(result_workspace, "st", fake_streamlit),
        patch.object(
            result_workspace,
            "build_current_backtest_analysis_result_workspace",
            return_value=workspace,
        ),
        patch.object(
            result_workspace,
            "is_backtest_analysis_result_workspace_available",
            return_value=True,
        ),
        patch.object(
            result_workspace,
            "render_backtest_analysis_result_workspace_component",
            return_value=intent,
        ) as render_component,
        patch.object(
            result_workspace,
            "consume_result_workspace_intent",
            return_value={"ok": True},
        ) as consume_intent,
    ):
        result_workspace.render_backtest_analysis_result_workspace()

    assert "on_change" not in render_component.call_args.kwargs
    consume_intent.assert_called_once_with(intent, workspace=workspace)
    fake_streamlit.rerun.assert_called_once_with(scope="app")
