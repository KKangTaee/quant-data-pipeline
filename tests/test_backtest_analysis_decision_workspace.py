from __future__ import annotations

import json
from datetime import date
from types import SimpleNamespace
from unittest.mock import MagicMock, patch

import pandas as pd

from app.services.backtest_analysis_decision_workspace import (
    _deduplicate_reasons,
    build_backtest_analysis_decision_workspace,
    build_level1_configuration_fingerprint,
    build_level1_readiness_projection,
    build_level1_strategy_catalog,
    level1_strategy_maturity,
)
from app.web.backtest_single_settings_workspace import (
    build_compact_ticker_summary,
    build_single_strategy_settings_summary,
)


class _SessionState(dict):
    __getattr__ = dict.__getitem__
    __setattr__ = dict.__setitem__


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


def test_single_settings_summary_projects_purpose_variant_and_maturity() -> None:
    summary = build_single_strategy_settings_summary(
        "Quality + Value",
        "Strict Annual",
    )

    assert summary == {
        "strategy_choice": "Quality + Value",
        "display_name": "Quality + Value Snapshot (Strict Annual)",
        "variant": "Strict Annual",
        "purpose": "팩터 기반 종목 선정",
        "maturity": "production",
        "maturity_label": "운영 전략",
        "description": "기업의 품질과 가치평가를 함께 비교해 보유 후보를 고릅니다.",
    }


def test_compact_ticker_summary_keeps_complete_evidence() -> None:
    summary = build_compact_ticker_summary(
        ["AAPL", "MSFT", "GOOG", "AMZN", "META"],
        preview_count=3,
    )

    assert summary == {
        "count": 5,
        "headline": "선택 종목 5개 · 대표 AAPL, MSFT, GOOG",
        "full_text": "AAPL, MSFT, GOOG, AMZN, META",
    }


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


def test_record_single_strategy_draft_stores_normalized_fingerprint() -> None:
    from app.web import backtest_analysis_workspace

    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {"backtest_strategy_choice": "GTAA"}
    )
    with patch.object(backtest_analysis_workspace, "st", fake_streamlit):
        fingerprint = backtest_analysis_workspace.record_single_strategy_draft(
            {"strategy_key": "gtaa", "tickers": ("SPY", "TLT")},
            strategy_name="GTAA",
        )

    assert fake_streamlit.session_state.backtest_current_draft_payload["tickers"] == [
        "SPY",
        "TLT",
    ]
    assert (
        fake_streamlit.session_state.backtest_current_configuration_fingerprint
        == fingerprint
    )
    assert fingerprint == build_level1_configuration_fingerprint(
        workspace_kind="single_strategy",
        selection={"strategy_choice": "GTAA"},
        configuration=fake_streamlit.session_state.backtest_current_draft_payload,
    )


def test_successful_runner_stamps_fingerprint_without_candidate_handoff() -> None:
    from app.web import backtest_single_runner

    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState()
    result = SimpleNamespace(
        ok=True,
        bundle={"strategy_name": "GTAA", "meta": {"strategy_key": "gtaa"}},
        elapsed_seconds=0.01,
    )
    with (
        patch.object(backtest_single_runner, "st", fake_streamlit),
        patch.object(
            backtest_single_runner,
            "execute_single_backtest",
            return_value=result,
        ),
        patch.object(
            backtest_single_runner,
            "record_single_strategy_draft",
            return_value="fingerprint-1",
        ),
        patch.object(backtest_single_runner, "append_backtest_run_history") as history,
    ):
        assert backtest_single_runner._handle_backtest_run(
            {"strategy_key": "gtaa"}, strategy_name="GTAA"
        )

    bundle = fake_streamlit.session_state.backtest_last_bundle
    assert bundle["meta"]["level1_configuration_fingerprint"] == "fingerprint-1"
    history.assert_called_once_with(
        bundle=bundle,
        run_kind="single_strategy",
        context={"level1_configuration_fingerprint": "fingerprint-1"},
    )
    assert "_queue_candidate_review_draft" not in (
        __import__("pathlib").Path("app/web/backtest_single_runner.py").read_text()
    )


def test_failed_runner_preserves_previous_successful_bundle() -> None:
    from app.web import backtest_single_runner

    previous = {"strategy_name": "GTAA", "meta": {"strategy_key": "gtaa"}}
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState({"backtest_last_bundle": previous})
    result = SimpleNamespace(
        ok=False,
        bundle=None,
        error_kind="data",
        error_message="missing SPY",
        elapsed_seconds=0.01,
    )
    with (
        patch.object(backtest_single_runner, "st", fake_streamlit),
        patch.object(
            backtest_single_runner,
            "execute_single_backtest",
            return_value=result,
        ),
        patch.object(
            backtest_single_runner,
            "record_single_strategy_draft",
            return_value="fingerprint-1",
            create=True,
        ),
    ):
        assert not backtest_single_runner._handle_backtest_run(
            {"strategy_key": "gtaa"}, strategy_name="GTAA"
        )

    assert fake_streamlit.session_state.backtest_last_bundle is previous
    assert fake_streamlit.session_state.backtest_last_error_kind == "data"


def test_explicit_save_and_move_intent_queues_current_bundle_once() -> None:
    from app.web import backtest_analysis_workspace

    bundle = _successful_bundle()
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            "backtest_last_bundle": bundle,
            "backtest_analysis_consumed_nonce": None,
        }
    )
    workspace = {
        "workspace_kind": "single_strategy",
        "actions": {
            "save_and_move": {
                "id": "save_and_move",
                "enabled": True,
            }
        },
    }
    with (
        patch.object(backtest_analysis_workspace, "st", fake_streamlit),
        patch.object(
            backtest_analysis_workspace,
            "build_current_backtest_analysis_workspace",
            return_value=workspace,
        ),
        patch.object(
            backtest_analysis_workspace,
            "_candidate_review_draft_from_bundle",
            return_value={"draft_id": "draft-1"},
        ) as draft_from_bundle,
        patch.object(
            backtest_analysis_workspace,
            "_queue_candidate_review_draft",
        ) as queue_draft,
    ):
        intent = {
            "action": "save_and_move",
            "payload": {},
            "nonce": "handoff-1",
        }
        backtest_analysis_workspace.consume_backtest_analysis_intent(
            intent,
            allowed_actions={"save_and_move"},
        )
        backtest_analysis_workspace.consume_backtest_analysis_intent(
            intent,
            allowed_actions={"save_and_move"},
        )

    draft_from_bundle.assert_called_once_with(bundle)
    queue_draft.assert_called_once_with({"draft_id": "draft-1"})
    assert (
        fake_streamlit.session_state.backtest_analysis_consumed_nonce
        == "handoff-1"
    )


def test_save_and_move_intent_rejects_disabled_or_missing_result() -> None:
    from app.web import backtest_analysis_workspace

    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {"backtest_analysis_consumed_nonce": None}
    )
    workspace = {
        "workspace_kind": "single_strategy",
        "actions": {},
    }
    with (
        patch.object(backtest_analysis_workspace, "st", fake_streamlit),
        patch.object(
            backtest_analysis_workspace,
            "build_current_backtest_analysis_workspace",
            return_value=workspace,
        ),
        patch.object(
            backtest_analysis_workspace,
            "_queue_candidate_review_draft",
        ) as queue_draft,
    ):
        backtest_analysis_workspace.consume_backtest_analysis_intent(
            {
                "action": "save_and_move",
                "payload": {},
                "nonce": "handoff-disabled",
            },
            allowed_actions={"save_and_move"},
        )

    queue_draft.assert_not_called()


def test_component_change_consumes_selection_without_nested_rerun() -> None:
    from app.web import backtest_analysis_workspace

    component_key = "backtest-analysis-decision-workspace-context"
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            component_key: {
                "action": "select_strategy",
                "payload": {"strategy_choice": "GTAA"},
                "nonce": "strategy-gtaa-1",
            },
            "backtest_analysis_consumed_nonce": None,
        }
    )

    with patch.object(backtest_analysis_workspace, "st", fake_streamlit):
        backtest_analysis_workspace.consume_backtest_analysis_component_change(
            component_key=component_key,
            allowed_actions={"select_strategy"},
        )

    assert fake_streamlit.session_state.backtest_strategy_choice == "GTAA"
    assert (
        fake_streamlit.session_state.backtest_analysis_consumed_nonce
        == "strategy-gtaa-1"
    )
    fake_streamlit.rerun.assert_not_called()


def test_mix_roles_and_weights_are_python_owned() -> None:
    from app.services.backtest_portfolio_mix_readiness import (
        build_mix_role_weight_rows,
    )

    rows = build_mix_role_weight_rows(
        strategy_names=[
            "GTAA",
            "Global Relative Strength",
            "Risk Parity Trend",
        ],
        weights_percent=[45.0, 35.0, 20.0],
        component_roles=["core", "growth", "defense"],
    )

    assert [row["role"] for row in rows] == ["core", "growth", "defense"]
    assert sum(row["weight_percent"] for row in rows) == 100.0
    assert all(row["valid"] for row in rows)


def test_legacy_saved_mix_without_roles_uses_inferred_roles() -> None:
    from app.services.backtest_saved_portfolio_replay import (
        resolve_saved_mix_component_roles,
    )

    roles = resolve_saved_mix_component_roles(
        {"portfolio_context": {}},
        strategy_names=["GTAA", "Risk Parity Trend"],
    )

    assert roles == ["core", "defense"]


def test_mix_workspace_uses_role_weight_projection() -> None:
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="portfolio_mix",
        selection={"mix_mode": "new"},
        configuration={
            "strategy_names": ["GTAA", "Risk Parity Trend"],
            "weights_percent": [50.0, 50.0],
            "component_roles": ["core", "defense"],
        },
        result_bundle=None,
        result_configuration_fingerprint=None,
        saved_mixes=[],
        last_error=None,
        last_error_kind=None,
        action_handlers={},
        component_bundles=(),
    )

    assert workspace["mix"]["role_weight_rows"][0]["role_label"] == "Core"
    assert workspace["mix"]["total_weight_percent"] == 100.0


def test_mix_save_and_candidate_handoff_use_different_handlers() -> None:
    from app.web.backtest_analysis_workspace import (
        build_backtest_analysis_action_handlers,
    )

    handlers = build_backtest_analysis_action_handlers(
        workspace_kind="portfolio_mix"
    )

    assert callable(handlers["save_mix"])
    assert callable(handlers["save_and_move"])
    assert handlers["save_mix"] is not handlers["save_and_move"]


def test_zero_actions_do_not_render_empty_action_board() -> None:
    workspace = build_backtest_analysis_decision_workspace(
        workspace_kind="portfolio_mix",
        selection={"mix_mode": "new"},
        configuration={
            "strategy_names": [],
            "weights_percent": [],
            "component_roles": [],
        },
        result_bundle=None,
        result_configuration_fingerprint=None,
        saved_mixes=[],
        last_error=None,
        last_error_kind=None,
        action_handlers={},
        component_bundles=(),
    )

    assert workspace["actions"] == {}


def test_mix_save_and_handoff_adapters_keep_persistence_separate() -> None:
    from app.web.backtest_compare import page

    weighted_bundle = {
        "strategy_name": "Weighted Portfolio",
        "component_strategy_names": ["GTAA", "Risk Parity Trend"],
        "component_input_weights": [60.0, 40.0],
        "component_roles": ["core", "defense"],
        "date_policy": "intersection",
        "meta": {},
    }
    bundles = [
        {"strategy_name": "GTAA", "meta": {}},
        {"strategy_name": "Risk Parity Trend", "meta": {}},
    ]
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            "backtest_compare_bundles": bundles,
            "backtest_weighted_bundle": weighted_bundle,
            "backtest_compare_source_context": {"source_kind": "manual_compare"},
        }
    )
    with (
        patch.object(page, "st", fake_streamlit),
        patch.object(
            page,
            "_build_saved_portfolio_compare_context",
            return_value={"selected_strategies": ["GTAA", "Risk Parity Trend"]},
        ),
        patch.object(
            page,
            "_build_saved_portfolio_context",
            return_value={"component_roles": ["core", "defense"]},
        ),
        patch.object(
            page,
            "save_saved_portfolio",
            return_value={"name": "Core Defense"},
        ) as save_mix,
        patch.object(
            page,
            "_build_weighted_mix_practical_validation_prefill_payload",
            return_value={"source_kind": "weighted_portfolio_mix"},
        ),
        patch.object(
            page,
            "build_selection_source_from_weighted_mix_prefill",
            return_value={"selection_source_id": "mix-source-1"},
        ),
        patch.object(
            page,
            "_apply_practical_validation_source_handoff",
        ) as handoff_mix,
    ):
        page._save_current_weighted_mix(
            {"name": "Core Defense", "description": "reusable setup"}
        )
        save_mix.assert_called_once()
        handoff_mix.assert_not_called()

        page._handoff_current_weighted_mix({})

    save_mix.assert_called_once()
    handoff_mix.assert_called_once_with({"selection_source_id": "mix-source-1"})


def _equal_weight_settings_runtime() -> dict:
    return {
        "presets": {
            "Equal Weight": {
                "Dividend ETFs": ["VIG", "SCHD", "DGRO", "GLD"],
            }
        },
        "tickers": ["VIG", "SCHD", "DGRO", "GLD", "SPY"],
        "benchmarks": ["SPY"],
    }


def _visible_settings_values(workspace: dict) -> dict:
    fields = [
        field
        for section in workspace["sections"]
        for field in section["fields"]
    ]
    all_values = {field["field_id"]: field["value"] for field in fields}
    return {
        field["field_id"]: field["value"]
        for field in fields
        if not field.get("visible_when")
        or all(
            all_values.get(dependency) == expected
            for dependency, expected in field["visible_when"].items()
        )
    }


def test_single_settings_schema_uses_current_strategy_catalog_names() -> None:
    from app.services.backtest_single_settings_workspace import (
        SINGLE_SETTINGS_CONCRETE_KEYS,
    )

    assert "Risk Parity Trend" in SINGLE_SETTINGS_CONCRETE_KEYS
    assert "Risk Parity" not in SINGLE_SETTINGS_CONCRETE_KEYS


def test_single_settings_run_intent_validates_then_calls_handler_once() -> None:
    from app.services.backtest_single_settings_workspace import (
        build_single_settings_workspace,
    )
    from app.web import backtest_single_settings_workspace as settings_workspace

    runtime = _equal_weight_settings_runtime()
    workspace = build_single_settings_workspace(
        "Equal Weight",
        None,
        {},
        runtime,
    )
    calls = []
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            "backtest_strategy_choice": "Equal Weight",
            "backtest_single_settings_consumed_intent_ids": [],
        }
    )
    intent = {
        "action": "run_single_strategy",
        "intent_id": "run-equal-1",
        "strategy_choice": "Equal Weight",
        "variant": None,
        "values": _visible_settings_values(workspace),
    }

    with patch.object(settings_workspace, "st", fake_streamlit):
        first = settings_workspace.consume_single_settings_intent(
            intent,
            run_handler=lambda payload, strategy_name: calls.append(
                (payload, strategy_name)
            ),
            runtime_options=runtime,
        )
        second = settings_workspace.consume_single_settings_intent(
            intent,
            run_handler=lambda payload, strategy_name: calls.append(
                (payload, strategy_name)
            ),
            runtime_options=runtime,
        )

    assert first["ok"] is True
    assert second["duplicate"] is True
    assert len(calls) == 1
    assert calls[0][0]["strategy_key"] == "equal_weight"
    assert calls[0][1] == "Equal Weight"


def test_single_settings_invalid_or_mismatched_intent_never_runs() -> None:
    from app.web import backtest_single_settings_workspace as settings_workspace

    calls = []
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            "backtest_strategy_choice": "Equal Weight",
            "backtest_single_settings_consumed_intent_ids": [],
        }
    )
    with patch.object(settings_workspace, "st", fake_streamlit):
        mismatch = settings_workspace.consume_single_settings_intent(
            {
                "action": "run_single_strategy",
                "intent_id": "mismatch-1",
                "strategy_choice": "GTAA",
                "variant": None,
                "values": {},
            },
            run_handler=lambda payload, strategy_name: calls.append(payload),
            runtime_options=_equal_weight_settings_runtime(),
        )
        invalid = settings_workspace.consume_single_settings_intent(
            {
                "action": "run_single_strategy",
                "intent_id": "invalid-1",
                "strategy_choice": "Equal Weight",
                "variant": None,
                "values": {"unknown": "injected"},
            },
            run_handler=lambda payload, strategy_name: calls.append(payload),
            runtime_options=_equal_weight_settings_runtime(),
        )
        missing_handler = settings_workspace.consume_single_settings_intent(
            {
                "action": "run_single_strategy",
                "intent_id": "handler-1",
                "strategy_choice": "Equal Weight",
                "variant": None,
                "values": {},
            },
            run_handler=None,
            runtime_options=_equal_weight_settings_runtime(),
        )

    assert mismatch["ok"] is False
    assert invalid["errors"]["unknown"] == "허용되지 않은 설정입니다."
    assert missing_handler["ok"] is False
    assert calls == []


def test_single_settings_variant_intent_updates_only_allowed_family_variant() -> None:
    from app.web import backtest_single_settings_workspace as settings_workspace

    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            "backtest_strategy_choice": "Quality + Value",
            "backtest_quality_value_variant": "Strict Annual",
            "backtest_single_settings_consumed_intent_ids": [],
        }
    )
    with (
        patch.object(settings_workspace, "st", fake_streamlit),
        patch.object(
            settings_workspace,
            "_variant_session_key",
            return_value="backtest_quality_value_variant",
        ),
    ):
        result = settings_workspace.consume_single_settings_intent(
            {
                "action": "select_strategy_variant",
                "intent_id": "variant-1",
                "strategy_choice": "Quality + Value",
                "variant": "Quarterly",
                "values": {},
            },
            run_handler=None,
            runtime_options={},
        )

    assert result["ok"] is True
    assert (
        fake_streamlit.session_state["backtest_quality_value_variant"]
        == "Strict Quarterly"
    )


def test_current_single_settings_workspace_projects_prefill_back_to_editor_values() -> None:
    from app.web import backtest_single_settings_workspace as settings_workspace

    runtime = _equal_weight_settings_runtime()
    fake_streamlit = MagicMock()
    fake_streamlit.session_state = _SessionState(
        {
            "backtest_strategy_choice": "Equal Weight",
            "backtest_prefill_payload": {
                "strategy_key": "equal_weight",
                "start": "2020-01-01",
                "end": "2024-12-31",
                "rebalance_interval": 6,
                "universe_mode": "preset",
                "preset_name": "Dividend ETFs",
                "transaction_cost_bps": 12.0,
            },
        }
    )

    with patch.object(settings_workspace, "st", fake_streamlit):
        workspace = settings_workspace.build_current_single_settings_workspace(
            selected_variant=None,
            runtime_options=runtime,
        )

    values = {
        field["field_id"]: field["value"]
        for section in workspace["sections"]
        for field in section["fields"]
    }
    assert values["start"] == "2020-01-01"
    assert values["end"] == "2024-12-31"
    assert values["rebalance_interval"] == 6
    assert values["transaction_cost_bps"] == 12.0
