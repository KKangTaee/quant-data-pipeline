from __future__ import annotations

import importlib
import json
from copy import deepcopy
from datetime import date
from types import SimpleNamespace

import pandas as pd
import pytest


def _workspace_module():
    return importlib.import_module("app.services.backtest_portfolio_mix_workspace")


def _runtime_options() -> dict[str, object]:
    return {
        "presets": {
            "Equal Weight": {"Dividend ETFs": ["VIG", "SCHD", "DGRO", "GLD"]},
            "GTAA": {
                "GTAA Universe": [
                    "SPY",
                    "IWD",
                    "IWM",
                    "IWN",
                    "MTUM",
                    "EFA",
                    "TLT",
                    "IEF",
                    "LQD",
                    "PDBC",
                    "VNQ",
                    "GLD",
                ]
            },
            "Global Relative Strength": {"GRS Universe": ["SPY", "EFA", "TLT"]},
            "Risk Parity Trend": {"Risk Parity Universe": ["SPY", "TLT", "GLD"]},
            "Dual Momentum": {"Dual Momentum Universe": ["SPY", "EFA", "AGG"]},
        },
        "presets_by_strategy_key": {
            "quality_value_snapshot_strict_annual": {
                "US Base Universe 100": ["AAPL", "MSFT", "NVDA"]
            },
            "quality_value_snapshot_strict_quarterly_prototype": {
                "US Base Universe 100": ["AAPL", "MSFT", "NVDA"]
            },
        },
        "preset_target_sizes": {"US Base Universe 100": 100},
        "tickers": [
            "AAPL",
            "MSFT",
            "NVDA",
            "SPY",
            "IWD",
            "IWM",
            "IWN",
            "MTUM",
            "EFA",
            "TLT",
            "IEF",
            "LQD",
            "PDBC",
            "VNQ",
            "GLD",
            "VIG",
            "SCHD",
            "DGRO",
            "AGG",
        ],
        "benchmarks": ["SPY", "ACWI", "QQQ"],
        "score_horizons": [1, 3, 6, 12],
        "market_regime_benchmarks": ["SPY", "ACWI"],
        "quality_factor_options": [
            "roe",
            "roa",
            "net_margin",
            "asset_turnover",
            "current_ratio",
        ],
        "value_factor_options": [
            "book_to_market",
            "earnings_yield",
            "sales_yield",
            "ocf_yield",
            "operating_income_yield",
        ],
    }


def _valid_draft() -> dict[str, object]:
    return {
        "draft_id": "draft-test",
        "source_saved_portfolio_id": None,
        "shared": {
            "start": "2016-01-01",
            "end": "2026-07-19",
            "timeframe": "1d",
            "option": "month_end",
            "date_policy": "intersection",
        },
        "components": [
            {
                "component_id": "component-gtaa",
                "strategy_choice": "GTAA",
                "variant": None,
                "settings_values": {"preset_name": "GTAA Universe", "top": 3},
                "role": "core",
                "weight_percent": 50,
            },
            {
                "component_id": "component-equal",
                "strategy_choice": "Equal Weight",
                "variant": None,
                "settings_values": {
                    "preset_name": "Dividend ETFs",
                    "rebalance_interval": 12,
                },
                "role": "defense",
                "weight_percent": 50,
            },
        ],
    }


def _weighted_result_evidence_fixture() -> dict[str, object]:
    dates = pd.to_datetime(["2026-01-31", "2026-02-28", "2026-04-30"])
    return {
        "strategy_name": "Weighted Portfolio",
        "summary_df": pd.DataFrame(
            [
                {
                    "CAGR": 0.096,
                    "Maximum Drawdown": -0.17,
                    "Sharpe Ratio": 0.91234,
                    "End Balance": 10200.0,
                }
            ]
        ),
        "result_df": pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [10000.0, 10500.0, 10200.0],
                "Total Return": [float("nan"), 0.05, -0.0285714286],
            }
        ),
        "component_contribution_amount_df": pd.DataFrame(
            {
                "GTAA": [5000.0, 5355.0, 5304.0],
                "Equal Weight": [5000.0, 5145.0, 4896.0],
            },
            index=dates,
        ),
        "component_contribution_share_df": pd.DataFrame(
            {
                "GTAA": [0.5, 0.51, 0.52],
                "Equal Weight": [0.5, 0.49, 0.48],
            },
            index=dates,
        ),
        "component_strategy_names": ["GTAA", "Equal Weight"],
        "component_roles": ["core", "defense"],
        "component_input_weights": [50.0, 50.0],
        "component_data_trust_rows": [
            {
                "Strategy": "GTAA",
                "Requested End": "2026-04-30",
                "Actual Result End": "2026-04-30",
                "Result Rows": 3,
                "Price Freshness": "OK",
                "Interpretation": "눈에 띄는 데이터 이슈 없음",
            }
        ],
        "date_policy": "intersection",
        "meta": {
            "run_id": "mix-run-evidence",
            "start": "2026-01-01",
            "end": "2026-04-30",
            "actual_result_end": "2026-04-30",
        },
    }


def test_mix_result_evidence_projects_user_labels_charts_and_contribution():
    module = _workspace_module()

    evidence = module.build_portfolio_mix_result_evidence(
        _weighted_result_evidence_fixture()
    )

    assert evidence["kpis"][0] == {
        "id": "annualized_return",
        "label": "연환산 수익률",
        "value": 0.096,
        "value_label": "9.60%",
    }
    assert evidence["equity_chart"]["rows"][0]["index_value"] == 100.0
    assert evidence["monthly_returns"]["chart_rows"][0]["month_label"] == (
        "2026.02"
    )
    assert evidence["contribution"]["summary_rows"][0][
        "target_weight_label"
    ] == "50.00%"
    assert evidence["contribution"]["summary_rows"][0]["role_label"] == "핵심"
    assert evidence["data_trust_rows"][0]["strategy_label"] == "GTAA"
    json.dumps(evidence, allow_nan=False)


def test_mix_result_evidence_preserves_sparse_and_unavailable_months():
    module = _workspace_module()

    evidence = module.build_portfolio_mix_result_evidence(
        _weighted_result_evidence_fixture()
    )

    assert len(evidence["equity_chart"]["desktop_ticks"]) <= 6
    assert len(evidence["equity_chart"]["compact_ticks"]) <= 3
    assert [row["date"] for row in evidence["equity_chart"]["rows"]] == [
        "2026-01-31",
        "2026-02-28",
        "2026-04-30",
    ]
    assert evidence["monthly_returns"]["table_rows"][0]["return_label"] == (
        "계산값 없음"
    )
    assert evidence["monthly_returns"]["table_rows"][0]["available"] is False
    assert all(
        row["available"]
        for row in evidence["monthly_returns"]["chart_rows"]
    )


def test_normalization_keeps_stable_component_ids_and_requires_two_to_four_components():
    module = _workspace_module()
    draft = _valid_draft()
    draft["components"][0].pop("component_id")

    normalized = module.normalize_portfolio_mix_draft(
        draft,
        runtime_options=_runtime_options(),
    )

    assert normalized["components"][0]["component_id"] == "component-1"
    assert normalized["components"][1]["component_id"] == "component-equal"
    assert module.validate_portfolio_mix_draft(normalized) == {}

    one_component = deepcopy(normalized)
    one_component["components"] = one_component["components"][:1]
    assert module.validate_portfolio_mix_draft(one_component)["components"] == (
        "구성 전략은 2개 이상 4개 이하로 선택해 주세요."
    )

    five_components = deepcopy(normalized)
    five_components["components"] = five_components["components"] * 3
    assert module.validate_portfolio_mix_draft(five_components)["components"] == (
        "구성 전략은 2개 이상 4개 이하로 선택해 주세요."
    )


def test_duplicate_concrete_strategy_is_rejected_once():
    module = _workspace_module()
    draft = _valid_draft()
    duplicate = deepcopy(draft["components"][0])
    duplicate["component_id"] = "component-gtaa-copy"
    duplicate["weight_percent"] = 10
    draft["components"][0]["weight_percent"] = 40
    draft["components"].append(duplicate)

    workspace = module.build_portfolio_mix_workspace(
        draft=draft,
        runtime_options=_runtime_options(),
    )

    assert workspace["validation"]["valid"] is False
    duplicate_issues = [
        issue
        for issue in workspace["validation"]["issues"]
        if issue["root_issue_id"] == "duplicate:gtaa"
    ]
    assert len(duplicate_issues) == 1
    assert workspace["validation"]["issue_count"] == len(
        workspace["validation"]["issues"]
    )


def test_shared_role_and_weight_validation_blocks_invalid_draft():
    module = _workspace_module()
    draft = _valid_draft()
    draft["shared"]["start"] = "2026-07-20"
    draft["components"][0]["role"] = "unknown"
    draft["components"][0]["weight_percent"] = 0
    draft["components"][1]["weight_percent"] = 75

    errors = module.validate_portfolio_mix_draft(
        module.normalize_portfolio_mix_draft(
            draft,
            runtime_options=_runtime_options(),
        )
    )

    assert errors["shared.period"] == "시작일은 종료일보다 빨라야 합니다."
    assert errors["components.component-gtaa.role"] == "허용되지 않은 역할입니다."
    assert errors["components.component-gtaa.weight_percent"] == (
        "목표 비중은 0보다 커야 합니다."
    )
    assert errors["allocation.total"] == "목표 비중 합계는 100%여야 합니다."


def test_component_projection_reuses_single_settings_schema_and_payload():
    module = _workspace_module()
    draft = _valid_draft()
    draft["components"].append(
        {
            "component_id": "component-quality-value",
            "strategy_choice": "Quality + Value",
            "variant": "Strict Annual",
            "settings_values": {
                "preset_name": "US Base Universe 100",
                "top": 10,
            },
            "role": "growth",
            "weight_percent": 20,
        }
    )
    draft["components"][0]["weight_percent"] = 40
    draft["components"][1]["weight_percent"] = 40

    projections = module.project_portfolio_mix_component_payloads(
        draft,
        runtime_options=_runtime_options(),
    )

    assert [item["strategy_name"] for item in projections] == [
        "GTAA",
        "Equal Weight",
        "Quality + Value Snapshot (Strict Annual)",
    ]
    assert projections[0]["concrete_strategy_key"] == "gtaa"
    assert projections[0]["overrides"]["top"] == 3
    assert projections[0]["overrides"]["tickers"][0] == "SPY"
    assert projections[1]["overrides"]["rebalance_interval"] == 12
    assert projections[2]["concrete_strategy_key"] == (
        "quality_value_snapshot_strict_annual"
    )
    assert projections[2]["overrides"]["dynamic_target_size"] == 100
    assert all(
        key not in projections[0]["overrides"]
        for key in ("start", "end", "timeframe", "option", "strategy_key")
    )
    assert all(
        section["section_id"] != "execution"
        for section in projections[0]["settings_workspace"]["sections"]
    )


def test_fingerprint_ignores_draft_identity_but_tracks_effective_configuration():
    module = _workspace_module()
    first = _valid_draft()
    same = deepcopy(first)
    same["draft_id"] = "another-draft"
    same["source_saved_portfolio_id"] = "saved-row-1"
    same["components"][0]["component_id"] = "restored-component-1"
    same["components"][1]["component_id"] = "restored-component-2"
    first["components"][0]["settings_values"].pop("top")
    same["components"][0]["settings_values"]["top"] = 3

    assert module.build_portfolio_mix_fingerprint(
        first,
        runtime_options=_runtime_options(),
    ) == module.build_portfolio_mix_fingerprint(
        same,
        runtime_options=_runtime_options(),
    )

    same["components"][0]["settings_values"]["top"] = 2
    assert module.build_portfolio_mix_fingerprint(
        first,
        runtime_options=_runtime_options(),
    ) != module.build_portfolio_mix_fingerprint(
        same,
        runtime_options=_runtime_options(),
    )


def test_pre_run_workspace_has_no_result_verdict_or_final_action_board():
    module = _workspace_module()

    workspace = module.build_portfolio_mix_workspace(
        draft=_valid_draft(),
        runtime_options=_runtime_options(),
        action_capabilities={"run_mix": True, "save_mix": True, "handoff_level2": True},
    )

    assert workspace["result"]["status"] == "not_run"
    assert workspace["result"]["current"] is None
    assert workspace["result"]["reference"] is None
    assert workspace["actions"] == []
    assert workspace["execution_action"] == {
        "id": "run_mix",
        "label": "이 구성으로 Mix 실행",
        "enabled": True,
    }


def test_stale_result_is_preserved_as_reference_and_disables_save_and_handoff():
    module = _workspace_module()
    draft = module.normalize_portfolio_mix_draft(
        _valid_draft(),
        runtime_options=_runtime_options(),
    )
    result = {
        "run_result_id": "mix-run-1",
        "configuration_fingerprint": module.build_portfolio_mix_fingerprint(
            draft,
            runtime_options=_runtime_options(),
        ),
        "summary": {"annualized_return": 0.12},
    }
    changed = deepcopy(draft)
    changed["components"][0]["weight_percent"] = 45
    changed["components"][1]["weight_percent"] = 55

    workspace = module.build_portfolio_mix_workspace(
        draft=changed,
        current_result=result,
        action_capabilities={"run_mix": True, "save_mix": True, "handoff_level2": True},
        runtime_options=_runtime_options(),
    )

    assert workspace["result"]["status"] == "stale"
    assert workspace["result"]["current"] is None
    assert workspace["result"]["reference"]["run_result_id"] == "mix-run-1"
    assert {action["id"] for action in workspace["actions"]} == set()
    assert workspace["execution_action"]["enabled"] is True


def test_saved_shelf_accepts_only_new_schema_without_raw_details():
    module = _workspace_module()
    saved_records = [
        {
            "schema_version": module.PORTFOLIO_MIX_SAVED_SCHEMA_VERSION,
            "id": "saved-new",
            "name": "균형형 Mix",
            "saved_at": "2026-07-19T12:00:00+09:00",
            "mix_draft": _valid_draft(),
            "absolute_path": "/tmp/should-not-appear.jsonl",
            "raw": {"secret": True},
        },
        {
            "id": "legacy-row",
            "name": "Legacy Mix",
            "portfolio_context": {"strategy_names": ["GTAA", "Equal Weight"]},
        },
    ]

    workspace = module.build_portfolio_mix_workspace(
        draft=_valid_draft(),
        saved_records=saved_records,
        runtime_options=_runtime_options(),
    )

    assert workspace["saved_mix"]["empty"] is False
    assert workspace["saved_mix"]["rows"] == [
        {
            "id": "saved-new",
            "name": "균형형 Mix",
            "saved_at": "2026-07-19T12:00:00+09:00",
            "component_count": 2,
            "component_summary": "GTAA 50% · Equal Weight 50%",
        }
    ]
    assert "/tmp" not in repr(workspace["saved_mix"])
    assert "secret" not in repr(workspace["saved_mix"])


def test_current_result_exposes_distinct_callable_save_and_handoff_actions():
    module = _workspace_module()
    draft = module.normalize_portfolio_mix_draft(
        _valid_draft(),
        runtime_options=_runtime_options(),
    )
    result = {
        "run_result_id": "mix-run-current",
        "configuration_fingerprint": module.build_portfolio_mix_fingerprint(
            draft,
            runtime_options=_runtime_options(),
        ),
    }

    workspace = module.build_portfolio_mix_workspace(
        draft=draft,
        current_result=result,
        action_capabilities={"run_mix": True, "save_mix": True, "handoff_level2": True},
        runtime_options=_runtime_options(),
    )

    assert workspace["result"]["status"] == "current"
    assert [action["id"] for action in workspace["actions"]] == [
        "save_mix",
        "handoff_level2",
    ]
    assert all(action["enabled"] is True for action in workspace["actions"])


def _intent(action: str, intent_id: str, **payload: object) -> dict[str, object]:
    return {
        "event": {
            "id": action,
            "intent_id": intent_id,
            "payload": payload,
        }
    }


def test_mix_adapter_builds_two_component_valid_initial_draft():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")

    draft = adapter.build_initial_portfolio_mix_session_draft(
        today=date(2026, 7, 19),
    )

    assert [component["strategy_choice"] for component in draft["components"]] == [
        "GTAA",
        "Equal Weight",
    ]
    assert [component["weight_percent"] for component in draft["components"]] == [
        50.0,
        50.0,
    ]
    assert draft["shared"]["end"] == "2026-07-19"


def test_mix_adapter_updates_only_addressed_draft_regions():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: adapter.build_initial_portfolio_mix_session_draft(
            today=date(2026, 7, 19)
        )
    }
    first_id = session[adapter.MIX_SESSION_KEYS["draft"]]["components"][0][
        "component_id"
    ]
    second_before = deepcopy(
        session[adapter.MIX_SESSION_KEYS["draft"]]["components"][1]
    )

    assert adapter.apply_portfolio_mix_intent(
        _intent("set_shared_field", "intent-shared", field_id="start", value="2018-01-01"),
        session_state=session,
        runtime_options=_runtime_options(),
    )["accepted"] is True
    assert adapter.apply_portfolio_mix_intent(
        _intent("set_role", "intent-role", component_id=first_id, value="growth"),
        session_state=session,
        runtime_options=_runtime_options(),
    )["accepted"] is True
    assert adapter.apply_portfolio_mix_intent(
        _intent("set_weight", "intent-weight", component_id=first_id, value=45),
        session_state=session,
        runtime_options=_runtime_options(),
    )["accepted"] is True
    assert adapter.apply_portfolio_mix_intent(
        _intent("set_component_field", "intent-field", component_id=first_id, field_id="top", value=2),
        session_state=session,
        runtime_options=_runtime_options(),
    )["accepted"] is True

    updated = session[adapter.MIX_SESSION_KEYS["draft"]]
    assert updated["shared"]["start"] == "2018-01-01"
    assert updated["components"][0]["role"] == "growth"
    assert updated["components"][0]["weight_percent"] == 45.0
    assert updated["components"][0]["settings_values"]["top"] == 2
    assert updated["components"][1] == second_before


def test_mix_adapter_adds_and_removes_components_without_replacing_other_drafts():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: adapter.build_initial_portfolio_mix_session_draft(
            today=date(2026, 7, 19)
        )
    }
    original = deepcopy(session[adapter.MIX_SESSION_KEYS["draft"]]["components"])

    added = adapter.apply_portfolio_mix_intent(
        _intent(
            "add_component",
            "intent-add",
            strategy_choice="Quality + Value",
            variant="Annual",
        ),
        session_state=session,
        runtime_options=_runtime_options(),
    )
    added_id = added["component_id"]

    assert added["accepted"] is True
    assert session[adapter.MIX_SESSION_KEYS["draft"]]["components"][:2] == original
    assert len(session[adapter.MIX_SESSION_KEYS["draft"]]["components"]) == 3

    removed = adapter.apply_portfolio_mix_intent(
        _intent("remove_component", "intent-remove", component_id=added_id),
        session_state=session,
        runtime_options=_runtime_options(),
    )

    assert removed["accepted"] is True
    assert session[adapter.MIX_SESSION_KEYS["draft"]]["components"] == original


def test_mix_adapter_applies_python_owned_preset_profile():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: adapter.build_initial_portfolio_mix_session_draft(
            today=date(2026, 7, 19)
        )
    }
    component_id = session[adapter.MIX_SESSION_KEYS["draft"]]["components"][0][
        "component_id"
    ]

    result = adapter.apply_portfolio_mix_intent(
        _intent(
            "apply_preset",
            "intent-preset",
            component_id=component_id,
            preset_name="GTAA Universe",
        ),
        session_state=session,
        runtime_options=_runtime_options(),
    )

    values = session[adapter.MIX_SESSION_KEYS["draft"]]["components"][0][
        "settings_values"
    ]
    assert result["accepted"] is True
    assert values["preset_name"] == "GTAA Universe"
    assert values["universe_mode"] == "preset"
    assert values["top"] == 3


def test_mix_adapter_rejects_unknown_and_duplicate_intents_without_mutation():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: adapter.build_initial_portfolio_mix_session_draft(
            today=date(2026, 7, 19)
        )
    }
    before = deepcopy(session)
    unknown = adapter.apply_portfolio_mix_intent(
        _intent("execute_runner_in_react", "intent-unknown"),
        session_state=session,
        runtime_options=_runtime_options(),
    )
    accepted = adapter.apply_portfolio_mix_intent(
        _intent("set_shared_field", "intent-once", field_id="start", value="2017-01-01"),
        session_state=session,
        runtime_options=_runtime_options(),
    )
    once = deepcopy(session)
    duplicate = adapter.apply_portfolio_mix_intent(
        _intent("set_shared_field", "intent-once", field_id="start", value="2019-01-01"),
        session_state=session,
        runtime_options=_runtime_options(),
    )

    assert unknown == {"accepted": False, "reason": "unknown_action"}
    assert before[adapter.MIX_SESSION_KEYS["draft"]] != once[
        adapter.MIX_SESSION_KEYS["draft"]
    ]
    assert accepted["accepted"] is True
    assert duplicate == {"accepted": False, "reason": "duplicate_intent"}
    assert session == once


def test_mix_fallback_model_uses_same_four_step_read_model():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    module = _workspace_module()
    workspace = module.build_portfolio_mix_workspace(
        draft=_valid_draft(),
        runtime_options=_runtime_options(),
        action_capabilities={"run_mix": True},
    )

    fallback = adapter.build_portfolio_mix_fallback_model(workspace)

    assert [step["id"] for step in fallback["steps"]] == [
        "configuration",
        "allocation",
        "execution",
        "handoff",
    ]
    assert fallback["component_cards"] == workspace["component_cards"]
    assert fallback["execution_action"] == workspace["execution_action"]
    assert fallback["actions"] == workspace["actions"]


def test_mix_mode_survives_rerun_through_python_session_read_model():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: adapter.build_initial_portfolio_mix_session_draft(
            today=date(2026, 7, 19)
        ),
        adapter.MIX_SESSION_KEYS["mode"]: "new",
    }

    accepted = adapter.apply_portfolio_mix_intent(
        _intent("set_mode", "intent-mode", value="saved"),
        session_state=session,
        runtime_options=_runtime_options(),
    )
    workspace = adapter.build_portfolio_mix_workspace_from_session(
        session_state=session,
        runtime_options=_runtime_options(),
    )

    assert accepted["accepted"] is True
    assert workspace["mode"] == "saved"
    assert adapter.build_portfolio_mix_fallback_model(workspace)["mode"] == "saved"


def test_mix_runtime_rejects_invalid_draft_before_any_component_runner_call():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    draft = _valid_draft()
    draft["components"][0]["weight_percent"] = 40
    calls: list[str] = []

    result = adapter.execute_portfolio_mix_draft(
        draft,
        runtime_options=_runtime_options(),
        run_component=lambda **kwargs: calls.append(kwargs["strategy_name"]),
        weighted_builder=lambda **kwargs: {"meta": {"run_id": "should-not-run"}},
    )

    assert result["ok"] is False
    assert result["error_kind"] == "validation"
    assert calls == []


def test_mix_runtime_runs_each_component_then_builds_one_weighted_result():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    runner_calls: list[dict[str, object]] = []
    weighted_calls: list[dict[str, object]] = []

    def run_component(**kwargs: object) -> dict[str, object]:
        runner_calls.append(dict(kwargs))
        return {
            "strategy_name": kwargs["strategy_name"],
            "meta": {
                "run_id": f"run-{kwargs['strategy_name']}",
                "start": kwargs["start"],
                "end": kwargs["end"],
                "timeframe": kwargs["timeframe"],
                "option": kwargs["option"],
            },
        }

    def weighted_builder(**kwargs: object) -> dict[str, object]:
        weighted_calls.append(dict(kwargs))
        return {
            "strategy_name": "Weighted Portfolio",
            "meta": {"run_id": "mix-run-current"},
        }

    result = adapter.execute_portfolio_mix_draft(
        _valid_draft(),
        runtime_options=_runtime_options(),
        run_component=run_component,
        weighted_builder=weighted_builder,
    )

    assert result["ok"] is True
    assert [call["strategy_name"] for call in runner_calls] == ["GTAA", "Equal Weight"]
    assert weighted_calls[0]["weights_percent"] == [50.0, 50.0]
    assert weighted_calls[0]["component_roles"] == ["core", "defense"]
    assert result["current_result"]["run_result_id"] == "mix-run-current"
    assert result["current_result"]["configuration_fingerprint"]
    assert result["current_result"]["summary"] == {}
    assert result["current_result"]["period"] == {"start": None, "end": None}
    assert result["current_result"]["evidence"]["identity"]["title"] == (
        "현재 설정으로 계산한 Mix 결과"
    )
    assert result["current_result"]["evidence"]["equity_chart"]["rows"] == []
    assert all(
        state["status"] == "completed"
        for state in result["component_states"].values()
    )


def test_failed_mix_run_preserves_previous_current_result_and_bundles():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    previous_result = {
        "run_result_id": "mix-run-previous",
        "configuration_fingerprint": "previous-fingerprint",
    }
    previous_bundles = [{"strategy_name": "Previous"}]
    previous_weighted = {"meta": {"run_id": "mix-run-previous"}}
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: _valid_draft(),
        adapter.MIX_SESSION_KEYS["current_result"]: deepcopy(previous_result),
        adapter.MIX_SESSION_KEYS["component_bundles"]: deepcopy(previous_bundles),
        adapter.MIX_SESSION_KEYS["weighted_bundle"]: deepcopy(previous_weighted),
    }

    def fail_equal_weight(**kwargs: object) -> dict[str, object]:
        if kwargs["strategy_name"] == "Equal Weight":
            raise RuntimeError("provider unavailable")
        return {"strategy_name": kwargs["strategy_name"], "meta": {}}

    response = adapter.run_current_portfolio_mix(
        session_state=session,
        runtime_options=_runtime_options(),
        run_component=fail_equal_weight,
        weighted_builder=lambda **kwargs: pytest.fail("weighted builder must not run"),
        history_appender=lambda **kwargs: pytest.fail("history must not be written"),
    )

    assert response["accepted"] is False
    assert response["reason"] == "component_execution_failed"
    assert session[adapter.MIX_SESSION_KEYS["current_result"]] == previous_result
    assert session[adapter.MIX_SESSION_KEYS["component_bundles"]] == previous_bundles
    assert session[adapter.MIX_SESSION_KEYS["weighted_bundle"]] == previous_weighted
    assert session[adapter.MIX_SESSION_KEYS["component_states"]]["component-gtaa"][
        "status"
    ] == "completed"
    assert session[adapter.MIX_SESSION_KEYS["component_states"]]["component-equal"][
        "status"
    ] == "error"


def test_runtime_intents_require_and_call_distinct_python_handlers_once():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    calls: list[tuple[str, dict[str, object]]] = []
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: _valid_draft(),
    }
    handlers = {
        "run_mix": lambda payload: calls.append(("run", dict(payload)))
        or {"accepted": True},
        "save_mix": lambda payload: calls.append(("save", dict(payload)))
        or {"accepted": True},
    }

    run = adapter.apply_portfolio_mix_intent(
        _intent("run_mix", "runtime-run"),
        session_state=session,
        runtime_options=_runtime_options(),
        action_handlers=handlers,
    )
    save = adapter.apply_portfolio_mix_intent(
        _intent("save_mix", "runtime-save", name="균형형 Mix"),
        session_state=session,
        runtime_options=_runtime_options(),
        action_handlers=handlers,
    )
    missing = adapter.apply_portfolio_mix_intent(
        _intent("handoff_level2", "runtime-handoff"),
        session_state=session,
        runtime_options=_runtime_options(),
        action_handlers=handlers,
    )

    assert run["accepted"] is True
    assert save["accepted"] is True
    assert calls == [("run", {}), ("save", {"name": "균형형 Mix"})]
    assert missing == {"accepted": False, "reason": "handler_unavailable"}


def test_new_mix_save_restore_and_level2_handoff_use_explicit_contracts():
    adapter = importlib.import_module("app.web.backtest_portfolio_mix_workspace")
    module = _workspace_module()
    draft = _valid_draft()
    fingerprint = module.build_portfolio_mix_fingerprint(
        draft,
        runtime_options=_runtime_options(),
    )
    stored: list[dict[str, object]] = []
    session: dict[str, object] = {
        adapter.MIX_SESSION_KEYS["draft"]: deepcopy(draft),
        adapter.MIX_SESSION_KEYS["current_result"]: {
            "run_result_id": "mix-run-current",
            "configuration_fingerprint": fingerprint,
        },
        adapter.MIX_SESSION_KEYS["component_bundles"]: [
            {"strategy_name": "GTAA", "meta": {}},
            {"strategy_name": "Equal Weight", "meta": {}},
        ],
        adapter.MIX_SESSION_KEYS["weighted_bundle"]: {
            "strategy_name": "Weighted Portfolio",
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [50.0, 50.0],
            "component_roles": ["core", "defense"],
            "date_policy": "intersection",
            "meta": {"run_id": "mix-run-current"},
        },
    }

    def save_handler(**kwargs: object) -> dict[str, object]:
        stored.append(dict(kwargs))
        return {
            "portfolio_id": "saved-new",
            "name": kwargs["name"],
            "saved_at": "2026-07-19T12:00:00+09:00",
            "source_context": kwargs["source_context"],
        }

    saved = adapter.save_current_portfolio_mix(
        {"name": "균형형 Mix"},
        session_state=session,
        runtime_options=_runtime_options(),
        save_handler=save_handler,
    )

    assert saved["accepted"] is True
    assert stored[0]["source_context"]["mix_schema_version"] == (
        module.PORTFOLIO_MIX_SAVED_SCHEMA_VERSION
    )
    assert stored[0]["source_context"]["mix_draft"] == module.normalize_portfolio_mix_draft(
        draft,
        runtime_options=_runtime_options(),
    )
    assert "component_bundles" not in stored[0]["source_context"]

    record = {
        "schema_version": 1,
        "portfolio_id": "saved-new",
        "name": "균형형 Mix",
        "saved_at": "2026-07-19T12:00:00+09:00",
        "source_context": stored[0]["source_context"],
    }
    restored = adapter.restore_saved_portfolio_mix(
        {"saved_mix_id": "saved-new"},
        session_state=session,
        saved_records=[record],
        runtime_options=_runtime_options(),
    )
    assert restored["accepted"] is True
    assert session[adapter.MIX_SESSION_KEYS["current_result"]] is None
    assert session[adapter.MIX_SESSION_KEYS["weighted_bundle"]] is None
    assert session[adapter.MIX_SESSION_KEYS["draft"]]["source_saved_portfolio_id"] == (
        "saved-new"
    )

    session[adapter.MIX_SESSION_KEYS["current_result"]] = {
        "run_result_id": "mix-run-current",
        "configuration_fingerprint": module.build_portfolio_mix_fingerprint(
            session[adapter.MIX_SESSION_KEYS["draft"]],
            runtime_options=_runtime_options(),
        ),
    }
    session[adapter.MIX_SESSION_KEYS["component_bundles"]] = [
        {"strategy_name": "GTAA", "meta": {}},
        {"strategy_name": "Equal Weight", "meta": {}},
    ]
    session[adapter.MIX_SESSION_KEYS["weighted_bundle"]] = {
        "meta": {"run_id": "mix-run-current"}
    }
    handed_off: list[dict[str, object]] = []
    handoff = adapter.handoff_current_portfolio_mix(
        {},
        session_state=session,
        runtime_options=_runtime_options(),
        source_builder=lambda prefill: {"source_title": prefill["weighted_portfolio_name"]},
        handoff_handler=lambda source, persist=True: handed_off.append(
            {"source": source, "persist": persist}
        )
        or SimpleNamespace(
            source_payload=source,
            notice="Level2 전달 완료",
            mode="Selected Source",
            requested_panel="Practical Validation",
        ),
    )

    assert handoff["accepted"] is True
    assert handed_off[0]["persist"] is True
    assert session["backtest_requested_panel"] == "Practical Validation"
    assert session["backtest_practical_validation_notice"] == "Level2 전달 완료"


def test_primary_mix_route_mounts_only_the_new_workspace():
    source = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "app/web/backtest_analysis.py"
    ).read_text()
    fragment = source.split("def _render_backtest_analysis_work_fragment", 1)[1].split(
        "\ndef ", 1
    )[0]

    assert "render_backtest_portfolio_mix_workspace()" in fragment
    assert "render_compare_portfolio_workspace()" not in fragment
    assert "render_backtest_analysis_decision_surface()" not in fragment


def test_mix_react_styles_keep_readable_text_inside_streamlit_dark_theme():
    styles = (
        __import__("pathlib").Path(__file__).resolve().parents[1]
        / "app/web/components/backtest_portfolio_mix_workspace/frontend/src/styles.css"
    ).read_text()

    assert ".mix-workspace h1, .mix-workspace h2" in styles
    assert ".mix-workspace button:not(.mix-primary)" in styles
    assert ".mix-primary {" in styles
    assert "color: #fff !important" in styles
