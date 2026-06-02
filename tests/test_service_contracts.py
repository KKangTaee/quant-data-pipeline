from __future__ import annotations

import importlib.util
import json
import subprocess
import sys
import tempfile
import unittest
from datetime import date, datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import patch

import pandas as pd


def _macro_regime_rows(
    dates: pd.DatetimeIndex,
    *,
    source_type: str = "official",
    coverage_status: str = "actual",
) -> pd.DataFrame:
    rows: list[dict[str, object]] = []
    for idx, date in enumerate(dates):
        if idx < 24:
            vix, curve, credit = 15.0, 1.2, 2.0
        elif idx < 42:
            vix, curve, credit = 22.0, 0.4, 2.6
        else:
            vix, curve, credit = 35.0, -0.2, 3.2
        for series_id, value in (("VIXCLS", vix), ("T10Y3M", curve), ("BAA10Y", credit)):
            rows.append(
                {
                    "series_id": series_id,
                    "observation_date": date,
                    "source": "fred",
                    "source_type": source_type,
                    "source_mode": "csv_download",
                    "category": "market_context",
                    "coverage_status": coverage_status,
                    "value": value,
                }
            )
    return pd.DataFrame(rows)


class PracticalValidationServiceContractTests(unittest.TestCase):
    def test_source_handoff_without_persistence_is_ui_neutral(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {
            "selection_source_id": "source-1",
            "source_title": "Quality portfolio",
            "source_type": "saved_mix",
        }

        with patch.object(service, "append_portfolio_selection_source") as append_source:
            handoff = service.prepare_practical_validation_source_handoff(source, persist=False)

        append_source.assert_not_called()
        self.assertEqual(handoff.source_payload, source)
        self.assertIsNot(handoff.source_payload, source)
        self.assertEqual(handoff.mode, "Selected Source")
        self.assertEqual(handoff.requested_panel, "Practical Validation")
        self.assertFalse(handoff.persisted)
        self.assertIn("Quality portfolio", handoff.notice)
        self.assertIn("live approval", handoff.notice)

    def test_source_handoff_with_persistence_reports_persisted(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {"selection_source_id": "source-2"}

        with patch.object(service, "append_portfolio_selection_source") as append_source:
            handoff = service.prepare_practical_validation_source_handoff(source, persist=True)

        append_source.assert_called_once_with(source)
        self.assertTrue(handoff.persisted)
        self.assertEqual(handoff.source_payload, source)
        self.assertIn("source-2", handoff.notice)

    def test_final_review_handoff_without_persistence_preserves_payloads(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {"selection_source_id": "source-3", "source_type": "single_strategy"}
        validation_result = {
            "selection_source_id": "source-3",
            "source_title": "Dual momentum candidate",
            "overall_status": "REVIEW",
        }

        with patch.object(service, "save_practical_validation_result") as save_result:
            handoff = service.prepare_final_review_handoff_from_validation(
                source=source,
                validation_result=validation_result,
                persist_validation=False,
            )

        save_result.assert_not_called()
        self.assertEqual(handoff.requested_panel, "Final Review")
        self.assertFalse(handoff.persisted)
        self.assertEqual(handoff.session_payload["source"], source)
        self.assertIsNot(handoff.session_payload["source"], source)
        self.assertEqual(handoff.session_payload["validation_result"], validation_result)
        self.assertIsNot(handoff.session_payload["validation_result"], validation_result)
        self.assertIn("Dual momentum candidate", handoff.notice)

    def test_final_review_handoff_with_persistence_saves_validation_result(self) -> None:
        from app.services import backtest_practical_validation as service

        source = {"selection_source_id": "source-4"}
        validation_result = {"selection_source_id": "source-4"}

        with patch.object(service, "save_practical_validation_result") as save_result:
            handoff = service.prepare_final_review_handoff_from_validation(
                source=source,
                validation_result=validation_result,
                persist_validation=True,
            )

        save_result.assert_called_once_with(validation_result)
        self.assertTrue(handoff.persisted)
        self.assertEqual(handoff.requested_panel, "Final Review")

    def test_final_review_source_options_hide_blocked_practical_validation_results(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_source_options

        blocked = {
            "validation_id": "validation-blocked",
            "selection_source_id": "source-blocked",
            "source_title": "Blocked source",
            "final_review_gate": {"can_save_and_move": False},
        }
        ready = {
            "validation_id": "validation-ready",
            "selection_source_id": "source-ready",
            "source_title": "Ready source",
            "final_review_gate": {"can_save_and_move": True},
            "selected_route_preflight": {"select_allowed": True},
        }

        options = _build_final_review_source_options(
            [{"registry_id": "legacy-candidate", "title": "Legacy candidate"}],
            [{"proposal_id": "legacy-proposal"}],
            practical_validation_rows=[blocked, ready],
            session_practical_source={"validation_result": blocked},
            include_legacy_sources=False,
        )

        self.assertEqual(len(options), 1)
        self.assertEqual(options[0]["source_type"], "practical_validation_result")
        self.assertEqual(options[0]["source_id"], "validation-ready")

    def test_practical_validation_registry_serializes_db_scalar_payloads(self) -> None:
        from app.runtime import portfolio_selection_v2

        with tempfile.TemporaryDirectory() as tmp_dir:
            result_file = Path(tmp_dir) / "PRACTICAL_VALIDATION_RESULTS.jsonl"
            with patch.object(portfolio_selection_v2, "PRACTICAL_VALIDATION_RESULT_FILE", result_file):
                portfolio_selection_v2.append_practical_validation_result(
                    {
                        "selection_source_id": "source-json-safe",
                        "input_evidence": {
                            "data_coverage_context": {
                                "price_window_rows": [
                                    {
                                        "symbol": "SPY",
                                        "window_row_count": Decimal("2558"),
                                        "first_date": date(2020, 1, 31),
                                        "latest_seen": pd.Timestamp("2026-05-29"),
                                    }
                                ]
                            }
                        },
                    }
                )
            loaded = json.loads(result_file.read_text(encoding="utf-8").strip())

        row = loaded["input_evidence"]["data_coverage_context"]["price_window_rows"][0]
        self.assertEqual(row["window_row_count"], 2558)
        self.assertEqual(row["first_date"], "2020-01-31")
        self.assertEqual(row["latest_seen"], "2026-05-29T00:00:00")

    def test_selection_source_preserves_cost_and_turnover_snapshots_without_new_registry(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_candidate_draft

        source = build_selection_source_from_candidate_draft(
            {
                "source_kind": "latest_backtest_run",
                "strategy_key": "equal_weight",
                "strategy_name": "Equal Weight",
                "result_snapshot": {
                    "start_date": "2020-01-31",
                    "end_date": "2024-12-31",
                    "cagr": 0.1,
                    "maximum_drawdown": -0.2,
                    "sharpe_ratio": 1.0,
                    "end_balance": 1500.0,
                },
                "settings_snapshot": {
                    "tickers": ["SPY", "TLT"],
                    "rebalance_interval": 1,
                    "transaction_cost_bps": 10.0,
                },
                "cost_model_snapshot": {
                    "cost_model_contract_version": "cost_model_source_contract_v1",
                    "cost_application_status": "applied_to_result_curve",
                    "transaction_cost_bps": 10.0,
                    "estimated_cost_total": 42.0,
                },
                "turnover_evidence_snapshot": {
                    "turnover_model_contract_version": "turnover_evidence_contract_v1",
                    "turnover_estimation_status": "estimated_from_holdings",
                    "turnover_source": "end_next_holdings_weight_delta",
                    "turnover_observation_count": 12,
                    "turnover_rebalance_rows": 12,
                    "avg_turnover": 0.2,
                },
                "net_cost_curve_snapshot": {
                    "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                    "net_cost_curve_status": "applied_with_measurable_cost",
                    "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                    "total_balance_is_net_of_cost": True,
                    "net_cost_curve_rows": 12,
                    "estimated_cost_total": 42.0,
                    "estimated_cost_positive_rows": 12,
                    "gross_end_balance": 1542.0,
                    "net_end_balance": 1500.0,
                    "gross_net_end_balance_delta": 42.0,
                },
            }
        )

        self.assertEqual(
            source["cost_model_snapshot"]["cost_application_status"],
            "applied_to_result_curve",
        )
        self.assertEqual(
            source["components"][0]["replay_contract"]["cost_model_snapshot"]["estimated_cost_total"],
            42.0,
        )
        self.assertEqual(
            source["turnover_evidence_snapshot"]["turnover_estimation_status"],
            "estimated_from_holdings",
        )
        self.assertEqual(
            source["components"][0]["replay_contract"]["turnover_evidence_snapshot"]["avg_turnover"],
            0.2,
        )
        self.assertEqual(
            source["net_cost_curve_snapshot"]["net_cost_curve_status"],
            "applied_with_measurable_cost",
        )
        self.assertEqual(
            source["components"][0]["replay_contract"]["net_cost_curve_snapshot"][
                "gross_net_end_balance_delta"
            ],
            42.0,
        )
        self.assertEqual(source["construction"]["rebalance_cadence"], 1)

    def test_compact_selection_history_extracts_monthly_holdings(self) -> None:
        from app.services.backtest_practical_validation_source import compact_selection_history_from_result_df

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Rebalancing": True,
                    "Next Ticker": ["SPY", "TLT"],
                    "Next Balance": [600.0, 400.0],
                    "Raw Selected Ticker": ["SPY", "TLT", "GLD"],
                    "Overlay Rejected Ticker": ["GLD"],
                    "Cash": 0.0,
                    "Total Balance": 1000.0,
                    "Total Return": 0.0,
                },
                {
                    "Date": "2020-02-29",
                    "Rebalancing": False,
                    "Next Ticker": ["SPY", "TLT"],
                    "Next Balance": [610.0, 410.0],
                    "Cash": 0.0,
                    "Total Balance": 1020.0,
                    "Total Return": 0.02,
                },
            ]
        )

        rows = compact_selection_history_from_result_df(result_df, component_title="GTAA", component_weight=100.0)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["date"], "2020-01-31")
        self.assertEqual(rows[0]["component"], "GTAA")
        self.assertEqual(rows[0]["selected_tickers"], ["SPY", "TLT"])
        self.assertEqual(rows[0]["target_weights"], [0.6, 0.4])
        self.assertEqual(rows[0]["raw_selected_tickers"], ["SPY", "TLT", "GLD"])
        self.assertEqual(rows[0]["overlay_rejected_tickers"], ["GLD"])
        self.assertIn("Selected SPY 60.0%, TLT 40.0%", rows[0]["interpretation"])

    def test_selection_source_preserves_selection_history_snapshot(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_candidate_draft

        selection_history = [
            {
                "date": "2020-01-31",
                "component": "Quality Snapshot",
                "selected_tickers": ["AAPL", "MSFT"],
                "target_weights": [0.5, 0.5],
            }
        ]

        source = build_selection_source_from_candidate_draft(
            {
                "source_kind": "latest_backtest_run",
                "strategy_key": "quality_snapshot_strict_annual",
                "strategy_name": "Quality Snapshot (Strict Annual)",
                "result_snapshot": {"start_date": "2020-01-31", "end_date": "2020-12-31"},
                "settings_snapshot": {"tickers": ["AAPL", "MSFT"], "rebalance_interval": 1},
                "selection_history_snapshot": selection_history,
            }
        )

        self.assertEqual(source["selection_history"], selection_history)
        self.assertEqual(source["components"][0]["selection_history"], selection_history)

    def test_saved_mix_source_preserves_component_selection_history(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_saved_mix_prefill

        source = build_selection_source_from_saved_mix_prefill(
            {
                "source_kind": "weighted_portfolio_mix",
                "weighted_portfolio_id": "mix-1",
                "weighted_portfolio_name": "Two Sleeve Mix",
                "weighted_summary": {"cagr": 0.1, "mdd": -0.2},
                "weighted_period": {"start": "2020-01-31", "end": "2020-12-31"},
                "components": [
                    {
                        "registry_id": "component-1",
                        "strategy_name": "Quality Snapshot (Strict Annual)",
                        "target_weight": 60.0,
                        "selection_history": [{"date": "2020-01-31", "selected_tickers": ["AAPL"]}],
                    }
                ],
            }
        )

        self.assertEqual(source["construction"]["target_weight_total"], 60.0)
        self.assertEqual(source["components"][0]["selection_history"][0]["selected_tickers"], ["AAPL"])

    def test_saved_mix_source_preserves_weight_rationale_and_cost_snapshots(self) -> None:
        from app.services.backtest_practical_validation_source import build_selection_source_from_saved_mix_prefill

        source = build_selection_source_from_saved_mix_prefill(
            {
                "source_kind": "weighted_portfolio_mix",
                "weighted_portfolio_id": "mix-2",
                "weighted_portfolio_name": "Role Aware Mix",
                "weighted_summary": {"cagr": 0.1, "mdd": -0.2},
                "weighted_period": {"start": "2020-01-31", "end": "2020-12-31"},
                "weighted_curve_snapshot": [{"date": "2020-01-31", "value": 1000.0}],
                "components": [
                    {
                        "registry_id": "component-core",
                        "strategy_name": "Equal Weight",
                        "candidate_role": "weighted_mix_component",
                        "proposal_role": "core_anchor",
                        "target_weight": 60.0,
                        "weight_reason": "Core exposure",
                        "selection_history": [{"date": "2020-01-31", "selected_tickers": ["SPY"]}],
                        "contract": {"transaction_cost_bps": 10.0},
                    },
                    {
                        "registry_id": "component-defense",
                        "strategy_name": "Risk Parity",
                        "candidate_role": "weighted_mix_component",
                        "proposal_role": "defensive_sleeve",
                        "target_weight": 40.0,
                        "weight_reason": "Drawdown dampener",
                        "selection_history": [{"date": "2020-01-31", "selected_tickers": ["TLT"]}],
                        "contract": {"transaction_cost_bps": 10.0},
                    },
                ],
            }
        )

        self.assertEqual(source["components"][0]["weight_reason"], "Core exposure")
        self.assertEqual(source["components"][1]["role_source"], "weighted_mix_component")
        self.assertEqual(source["cost_model_snapshot"]["transaction_cost_bps"], 10.0)
        self.assertEqual(source["turnover_evidence_snapshot"]["turnover_source"], "component_selection_history")
        self.assertEqual(source["net_cost_curve_snapshot"]["net_cost_curve_rows"], 1)
        self.assertEqual(
            source["components"][0]["replay_contract"]["cost_model_snapshot"]["cost_model_source"],
            "component_contracts",
        )

    def test_validation_source_traits_classify_single_etf_tactical_candidate(self) -> None:
        from app.services.backtest_practical_validation_modules import infer_validation_source_traits

        traits = infer_validation_source_traits(
            {
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [
                    {
                        "strategy_key": "gtaa",
                        "target_weight": 100.0,
                        "universe": ["SPY", "QQQ", "GLD", "IEF"],
                        "replay_contract": {
                            "settings_snapshot": {
                                "tickers": ["SPY", "QQQ", "GLD", "IEF"],
                                "interval": 2,
                            }
                        },
                    }
                ],
            }
        )

        self.assertTrue(traits["is_single_component"])
        self.assertFalse(traits["is_weighted_mix"])
        self.assertTrue(traits["is_etf_like"])
        self.assertTrue(traits["is_tactical"])
        self.assertTrue(traits["is_high_turnover"])
        self.assertEqual(traits["symbol_count"], 4)

    def test_validation_module_gate_blocks_missing_required_runtime_replay(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": False, "Current": "NOT_RUN"},
            {"Criteria": "Runtime period coverage", "Ready": False, "Current": "NOT_RUN"},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
            {"domain": "regime_macro_suitability", "status": "REVIEW"},
            {"domain": "sentiment_risk_on_off_overlay", "status": "REVIEW"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [{"strategy_key": "gtaa", "target_weight": 100.0, "universe": ["SPY", "TLT"]}],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=pass_row,
            risk_contribution_rows=[{"Criteria": "Pairwise correlation", "Status": "NEEDS_INPUT"}],
            component_role_weight_rows=[{"Criteria": "Component role source coverage", "Status": "REVIEW"}],
            backtest_realism_rows=pass_row,
        )

        gate = plan["final_review_gate"]
        self.assertFalse(gate["can_save_and_move"])
        self.assertEqual(gate["route"], "BLOCKED_FOR_FINAL_REVIEW")
        self.assertEqual([row["module_id"] for row in gate["blocking_modules"]], ["latest_replay"])
        self.assertEqual(gate["blocking_modules"][0]["gate_effect"], "Blocks Final Review")
        self.assertIn("전략 재검증", gate["blocking_modules"][0]["gate_reason"])
        self.assertEqual(
            gate["blocking_modules"][0]["resolution_surface"],
            "3. 최신 데이터 기준 전략 재검증",
        )
        self.assertIn("전략 재검증 실행", gate["blocking_modules"][0]["resolution_action"])
        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertFalse(modules["risk_contribution"]["applies"])
        self.assertEqual(modules["risk_contribution"]["status"], "NOT_APPLICABLE")
        self.assertEqual(modules["risk_contribution"]["gate_effect"], "Not applicable")
        display_rows = {row["Module"]: row for row in plan["module_display_rows"]}
        self.assertEqual(
            display_rows["Latest Runtime Replay"]["Fix Location"],
            "3. 최신 데이터 기준 전략 재검증",
        )

    def test_validation_board_map_marks_single_gtaa_conditional_boards(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": True},
            {"Criteria": "Runtime period coverage", "Ready": True},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
            {"domain": "regime_macro_suitability", "status": "REVIEW"},
            {"domain": "sentiment_risk_on_off_overlay", "status": "REVIEW"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [
                    {
                        "strategy_key": "gtaa",
                        "target_weight": 100.0,
                        "universe": ["SPY", "QQQ", "GLD", "IEF"],
                        "replay_contract": {
                            "settings_snapshot": {
                                "tickers": ["SPY", "QQQ", "GLD", "IEF"],
                                "interval": 2,
                            }
                        },
                    }
                ],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=pass_row,
            risk_contribution_rows=[{"Criteria": "Pairwise correlation", "Status": "NEEDS_INPUT"}],
            component_role_weight_rows=[{"Criteria": "Component role source coverage", "Status": "REVIEW"}],
            backtest_realism_rows=pass_row,
        )

        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertTrue(modules["provider_investability"]["applies"])
        self.assertFalse(modules["leverage_inverse"]["applies"])
        self.assertTrue(modules["macro_regime"]["applies"])
        self.assertFalse(modules["risk_contribution"]["applies"])
        self.assertFalse(modules["component_role_weight"]["applies"])

        display_rows = {row["Module"]: row for row in plan["module_display_rows"]}
        self.assertEqual(display_rows["Risk Contribution"]["Module Type"], "Conditional")
        self.assertEqual(display_rows["Risk Contribution"]["Applies"], "No")
        self.assertIn("Risk Contribution Audit", display_rows["Risk Contribution"]["Evidence Boards"])
        self.assertEqual(display_rows["Risk Contribution"]["Fix Location"], "Risk Contribution Audit")

        board_rows = {row["Board"]: row for row in plan["board_display_rows"]}
        self.assertEqual(board_rows["Provider Coverage"]["Applies"], "Yes")
        self.assertEqual(board_rows["Look-through Exposure Board"]["Applies"], "Yes")
        self.assertEqual(board_rows["Risk Contribution Audit"]["Applies"], "No")
        self.assertEqual(board_rows["Component Role / Weight Audit"]["Applies"], "No")
        self.assertIn("single component", board_rows["Risk Contribution Audit"]["Applicability"])

    def test_validation_module_gate_allows_ready_with_review_modules(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": True},
            {"Criteria": "Runtime period coverage", "Ready": True},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [{"strategy_key": "equal_weight", "target_weight": 100.0, "universe": ["SPY", "TLT"]}],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=[{"Criteria": "Component weight concentration", "Status": "REVIEW"}],
            risk_contribution_rows=[],
            component_role_weight_rows=[],
            backtest_realism_rows=[{"Criteria": "Cost / slippage sensitivity evidence", "Status": "REVIEW"}],
        )

        gate = plan["final_review_gate"]
        self.assertTrue(gate["can_save_and_move"])
        self.assertEqual(gate["route"], "READY_WITH_REVIEW")
        self.assertEqual(gate["blocking_modules"], [])
        self.assertTrue(
            {row["module_id"] for row in gate["review_modules"]}
            >= {"construction_risk", "backtest_realism"}
        )
        self.assertTrue(
            all(row["gate_effect"] == "Final Review review" for row in gate["review_modules"])
        )
        display_rows = {row["Module"]: row for row in plan["module_display_rows"]}
        self.assertIn("Benchmark / Comparator Parity", display_rows)
        self.assertEqual(display_rows["Benchmark / Comparator Parity"]["Gate Effect"], "Ready")

    def test_validation_module_gate_blocks_selected_route_preflight_gaps(self) -> None:
        from app.services.backtest_practical_validation_modules import build_validation_module_plan

        checks = [
            {"Criteria": "Selection source", "Ready": True},
            {"Criteria": "Active components", "Ready": True},
            {"Criteria": "Target weight total", "Ready": True},
            {"Criteria": "Data Trust", "Ready": True},
            {"Criteria": "Execution boundary", "Ready": True},
            {"Criteria": "Curve evidence", "Ready": True},
            {"Criteria": "Runtime recheck", "Ready": True},
            {"Criteria": "Runtime period coverage", "Ready": True},
            {"Criteria": "Benchmark parity", "Ready": True},
            {"Criteria": "Provider coverage", "Ready": True},
        ]
        diagnostics = [
            {"domain": "stress_scenario_diagnostics", "status": "PASS"},
            {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
            {"domain": "leveraged_inverse_etf_suitability", "status": "PASS"},
            {"domain": "asset_allocation_fit", "status": "PASS"},
            {"domain": "concentration_overlap_exposure", "status": "PASS"},
            {"domain": "operability_cost_liquidity", "status": "PASS"},
        ]
        pass_row = [{"Criteria": "row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [{"strategy_key": "equal_weight", "target_weight": 100.0, "universe": ["SPY", "TLT"]}],
            },
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            checks=checks,
            diagnostics=diagnostics,
            validation_efficacy_rows=pass_row,
            data_coverage_rows=pass_row,
            construction_risk_rows=pass_row,
            risk_contribution_rows=[],
            component_role_weight_rows=[],
            backtest_realism_rows=[{"Criteria": "Net performance policy", "Status": "REVIEW"}],
            selected_route_preflight={
                "select_allowed": False,
                "policy_outcome": "hold_or_re_review",
                "review_required": ["Backtest Realism: Net performance policy: gross-only evidence"],
                "next_action": "net performance evidence를 보강합니다.",
            },
        )

        gate = plan["final_review_gate"]
        self.assertFalse(gate["can_save_and_move"])
        self.assertEqual(gate["route"], "BLOCKED_FOR_FINAL_REVIEW")
        self.assertIn("selected-route", gate["verdict"])
        self.assertEqual(gate["blocking_modules"][0]["module_id"], "selected_route_preflight")
        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertEqual(modules["selected_route_preflight"]["status"], "NEEDS_INPUT")
        self.assertEqual(modules["selected_route_preflight"]["gate_effect"], "Blocks Final Review")
        self.assertIn("gross-only", modules["selected_route_preflight"]["resolution_action"])

    def test_service_imports_do_not_load_streamlit(self) -> None:
        script = """
import sys
import app.runtime
import app.runtime.backtest
import app.runtime.candidate_library
import app.runtime.backtest_result_bundle
import app.services.backtest_component_role_weight_audit
import app.services.backtest_construction_risk_audit
import app.services.backtest_data_coverage_audit
import app.services.backtest_realism_audit
import app.services.backtest_evidence_read_model
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_diagnostics
import app.services.backtest_practical_validation_board_registry
import app.services.backtest_practical_validation_modules
import app.services.backtest_practical_validation
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_replay
import app.services.backtest_practical_validation_source
import app.services.backtest_risk_contribution_audit
import app.services.backtest_selected_route_preflight
import app.services.backtest_validation_efficacy
import app.services.overview_market_intelligence
print("streamlit" in sys.modules)
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.strip(), "False")

    def test_runtime_package_import_does_not_load_streamlit(self) -> None:
        script = """
import sys
import importlib.util
import app.runtime
import app.runtime.candidate_library
print("streamlit" in sys.modules)
print(importlib.util.find_spec("app.web.runtime") is None)
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.splitlines(), ["False", "True"])

    def test_practical_validation_helpers_are_not_web_modules(self) -> None:
        script = """
import importlib.util
import sys
import app.services.backtest_component_role_weight_audit
import app.services.backtest_data_coverage_audit
import app.services.backtest_realism_audit
import app.services.backtest_construction_risk_audit
import app.services.backtest_practical_validation_curve
import app.services.backtest_practical_validation_curve_context
import app.services.backtest_practical_validation_provider_context
import app.services.backtest_practical_validation_stress_sensitivity
import app.services.backtest_practical_validation_source
import app.services.backtest_risk_contribution_audit
import app.services.backtest_temporal_validation
import app.services.backtest_validation_efficacy
print("streamlit" in sys.modules)
print(importlib.util.find_spec("app.web.backtest_practical_validation_curve") is None)
print(importlib.util.find_spec("app.web.backtest_practical_validation_connectors") is None)
"""
        result = subprocess.run(
            [sys.executable, "-c", script],
            check=True,
            capture_output=True,
            text=True,
        )

        self.assertEqual(result.stdout.splitlines(), ["False", "True", "True"])


class ConstructionRiskAuditContractTests(unittest.TestCase):
    def _validation_with_board(self, board: dict) -> dict:
        return {
            "validation_profile": {
                "profile_id": "balanced_core",
                "thresholds": {"max_weight_review": 75.0},
            },
            "metrics": {
                "active_components": 2,
                "weight_total": 100.0,
                "max_weight": 60.0,
            },
            "diagnostic_results": [
                {
                    "domain": "concentration_overlap_exposure",
                    "status": "PASS",
                    "summary": "component concentration and provider look-through available",
                }
            ],
            "provider_coverage": {
                "look_through_board": board,
            },
        }

    def test_ready_audit_uses_provider_look_through_without_writes(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            CONSTRUCTION_RISK_READY,
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            self._validation_with_board(
                {
                    "schema_version": "look_through_board_v1",
                    "status": "PASS",
                    "summary": "Provider look-through board status PASS.",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "top_holding_weight": 3.5,
                    "top_overlap_weight": 2.0,
                    "dominant_asset_bucket": "equity",
                    "dominant_asset_weight": 60.0,
                    "unknown_exposure_weight": 0.0,
                }
            )
        )

        self.assertEqual(audit["route"], CONSTRUCTION_RISK_READY)
        self.assertEqual(audit["source_strength"], "provider_backed")
        self.assertEqual(audit["metrics"]["pass"], 6)
        self.assertEqual(audit["metrics"]["holdings_coverage_weight"], 100.0)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def test_missing_provider_coverage_is_not_ready_even_with_proxy_diagnostic(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            CONSTRUCTION_RISK_NEEDS_INPUT,
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            {
                "metrics": {
                    "active_components": 2,
                    "weight_total": 100.0,
                    "max_weight": 50.0,
                },
                "diagnostic_results": [
                    {
                        "domain": "concentration_overlap_exposure",
                        "status": "PASS",
                        "summary": "proxy concentration did not exceed threshold",
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], CONSTRUCTION_RISK_NEEDS_INPUT)
        self.assertEqual(audit["source_strength"], "proxy_only")
        self.assertEqual(rows_by_criteria["Provider look-through coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Top holding concentration"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Asset bucket exposure"]["Status"], "NEEDS_INPUT")

    def test_top_holding_overlap_and_unknown_exposure_trigger_review(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            CONSTRUCTION_RISK_REVIEW,
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            self._validation_with_board(
                {
                    "schema_version": "look_through_board_v1",
                    "status": "PASS",
                    "summary": "Provider look-through board status PASS.",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "top_holding_weight": 30.0,
                    "top_overlap_weight": 22.0,
                    "dominant_asset_bucket": "equity",
                    "dominant_asset_weight": 70.0,
                    "unknown_exposure_weight": 4.0,
                }
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], CONSTRUCTION_RISK_REVIEW)
        self.assertEqual(rows_by_criteria["Top holding concentration"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Holdings overlap"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Asset bucket exposure"]["Status"], "REVIEW")


class RiskContributionAuditContractTests(unittest.TestCase):
    def _validation(
        self,
        *,
        diagnostic_status: str = "PASS",
        average_correlation: float | None = 0.25,
        max_correlation: float | None = 0.45,
        max_risk_contribution: float | None = 0.55,
        monthly_return_rows: int = 48,
        curve_source: str = "actual_runtime_replay",
        curve_rows: int = 120,
        dependency_status: str = "PASS",
    ) -> dict:
        diagnostic_metrics: dict[str, object] = {"monthly_return_rows": monthly_return_rows}
        if average_correlation is not None:
            diagnostic_metrics["average_correlation"] = average_correlation
        if max_correlation is not None:
            diagnostic_metrics["max_correlation"] = max_correlation
        if max_risk_contribution is not None:
            diagnostic_metrics["max_risk_contribution"] = max_risk_contribution
        return {
            "metrics": {"active_components": 2},
            "curve_evidence": {
                "component_curve_rows": [
                    {
                        "Component": "Core",
                        "Weight": 60.0,
                        "Curve Source": curve_source,
                        "Rows": curve_rows,
                    },
                    {
                        "Component": "Defense",
                        "Weight": 40.0,
                        "Curve Source": curve_source,
                        "Rows": curve_rows,
                    },
                ]
            },
            "diagnostic_results": [
                {
                    "domain": "correlation_diversification_risk_contribution",
                    "status": diagnostic_status,
                    "summary": "Correlation and risk contribution evidence available.",
                    "metrics": diagnostic_metrics,
                    "evidence_rows": [
                        {
                            "Component": "Core",
                            "Weight": 60.0,
                            "Risk Contribution Proxy": 0.55,
                        },
                        {
                            "Component": "Defense",
                            "Weight": 40.0,
                            "Risk Contribution Proxy": 0.45,
                        },
                    ],
                }
            ],
            "sensitivity_interpretation": {
                "rows": [
                    {
                        "Check": "Component dependency",
                        "Status": dependency_status,
                        "Finding": "Drop-one dependency is contained.",
                        "Why It Matters": "No single component explains the portfolio.",
                    }
                ]
            },
        }

    def test_ready_audit_uses_runtime_component_curves_without_writes(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_READY,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(self._validation())

        self.assertEqual(audit["route"], RISK_CONTRIBUTION_READY)
        self.assertEqual(audit["source_strength"], "runtime_component_curves")
        self.assertEqual(audit["metrics"]["pass"], 5)
        self.assertEqual(audit["metrics"]["monthly_return_rows"], 48)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["raw_matrix_persistence"])

    def test_missing_component_matrix_needs_input(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_NEEDS_INPUT,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(
            {
                "metrics": {"active_components": 2},
                "diagnostic_results": [
                    {
                        "domain": "correlation_diversification_risk_contribution",
                        "status": "NOT_RUN",
                        "summary": "component return matrix missing",
                        "metrics": {"monthly_return_rows": 0},
                    }
                ],
                "sensitivity_interpretation": {
                    "rows": [{"Check": "Component dependency", "Status": "NOT_RUN"}]
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], RISK_CONTRIBUTION_NEEDS_INPUT)
        self.assertEqual(audit["source_strength"], "missing_component_matrix")
        self.assertEqual(rows_by_criteria["Component return matrix coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Pairwise correlation"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Risk contribution concentration"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Drop-one component dependency"]["Status"], "NEEDS_INPUT")

    def test_high_correlation_and_risk_contribution_trigger_review(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_REVIEW,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(
            self._validation(
                average_correlation=0.76,
                max_correlation=0.92,
                max_risk_contribution=0.85,
                curve_source="embedded_result_curve",
                dependency_status="REVIEW",
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], RISK_CONTRIBUTION_REVIEW)
        self.assertEqual(audit["source_strength"], "embedded_component_curves")
        self.assertEqual(rows_by_criteria["Pairwise correlation"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Risk contribution concentration"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Drop-one component dependency"]["Status"], "REVIEW")

    def test_db_price_proxy_source_triggers_review(self) -> None:
        from app.services.backtest_risk_contribution_audit import (
            RISK_CONTRIBUTION_REVIEW,
            build_risk_contribution_audit,
        )

        audit = build_risk_contribution_audit(self._validation(curve_source="db_price_proxy"))

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], RISK_CONTRIBUTION_REVIEW)
        self.assertEqual(audit["source_strength"], "db_price_proxy")
        self.assertEqual(rows_by_criteria["Component return matrix coverage"]["Status"], "REVIEW")


class ComponentRoleWeightAuditContractTests(unittest.TestCase):
    def _validation(
        self,
        *,
        profile_id: str = "balanced_core",
        primary_goal: str = "balanced",
        max_weight_review: float = 75.0,
        components: list[dict] | None = None,
    ) -> dict:
        components = list(
            components
            or [
                {
                    "title": "Core Trend",
                    "strategy_name": "GTAA",
                    "proposal_role": "core_anchor",
                    "target_weight": 50.0,
                    "weight_reason": "Core allocation",
                },
                {
                    "title": "Defense",
                    "strategy_name": "Risk Parity",
                    "proposal_role": "defensive_sleeve",
                    "target_weight": 30.0,
                    "weight_reason": "Drawdown dampener",
                },
                {
                    "title": "Diversifier",
                    "strategy_name": "Equal Weight",
                    "proposal_role": "diversifier",
                    "target_weight": 20.0,
                    "weight_reason": "Diversification sleeve",
                },
            ]
        )
        return {
            "validation_profile": {
                "profile_id": profile_id,
                "profile_label": "균형형",
                "answers": {"primary_goal": primary_goal},
                "thresholds": {"max_weight_review": max_weight_review},
            },
            "metrics": {
                "active_components": len(components),
                "weight_total": sum(float(component.get("target_weight") or 0.0) for component in components),
                "max_weight": max([float(component.get("target_weight") or 0.0) for component in components], default=0.0),
            },
            "selection_source_snapshot": {
                "source_kind": "weighted_portfolio_mix",
                "components": components,
            },
        }

    def test_ready_audit_uses_explicit_roles_without_writes(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_READY,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(self._validation())

        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_READY)
        self.assertEqual(audit["source_strength"], "explicit_role_metadata")
        self.assertEqual(audit["metrics"]["pass"], 6)
        self.assertEqual(audit["metrics"]["explicit_role_weight"], 100.0)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])
        self.assertFalse(audit["execution_boundary"]["role_preset_persistence"])

    def test_missing_multi_component_roles_need_input(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_NEEDS_INPUT,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(
            self._validation(
                components=[
                    {"title": "A", "strategy_name": "GTAA", "target_weight": 60.0},
                    {"title": "B", "strategy_name": "Equal Weight", "target_weight": 40.0},
                ]
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_NEEDS_INPUT)
        self.assertEqual(audit["source_strength"], "missing_role_metadata")
        self.assertEqual(rows_by_criteria["Component role source coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Role concentration discipline"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Weight rationale coverage"]["Status"], "NEEDS_INPUT")

    def test_profile_weight_and_role_concentration_trigger_review(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_REVIEW,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(
            self._validation(
                components=[
                    {
                        "title": "Core",
                        "strategy_name": "GTAA",
                        "proposal_role": "core_anchor",
                        "target_weight": 90.0,
                        "weight_reason": "High conviction core",
                    },
                    {
                        "title": "Diversifier",
                        "strategy_name": "Equal Weight",
                        "proposal_role": "diversifier",
                        "target_weight": 10.0,
                        "weight_reason": "Small diversifier",
                    },
                ]
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_REVIEW)
        self.assertEqual(rows_by_criteria["Profile-aware weight discipline"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Role concentration discipline"]["Status"], "REVIEW")

    def test_hedged_profile_without_matching_role_triggers_review(self) -> None:
        from app.services.backtest_component_role_weight_audit import (
            COMPONENT_ROLE_WEIGHT_REVIEW,
            build_component_role_weight_audit,
        )

        audit = build_component_role_weight_audit(
            self._validation(
                profile_id="hedged_tactical",
                primary_goal="hedged_tactical",
                max_weight_review=70.0,
                components=[
                    {
                        "title": "Core",
                        "strategy_name": "Equal Weight",
                        "proposal_role": "core_anchor",
                        "target_weight": 60.0,
                        "weight_reason": "Core exposure",
                    },
                    {
                        "title": "Growth",
                        "strategy_name": "Quality Growth",
                        "proposal_role": "growth_sleeve",
                        "target_weight": 40.0,
                        "weight_reason": "Growth exposure",
                    },
                ],
            )
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], COMPONENT_ROLE_WEIGHT_REVIEW)
        self.assertEqual(rows_by_criteria["Profile intent role fit"]["Status"], "REVIEW")


class ValidationEfficacyAuditContractTests(unittest.TestCase):
    def test_ready_audit_uses_compact_evidence_without_writes(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_READY,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "selection_source_id": "source-ready",
                "checks": [
                    {"Criteria": "Selection source", "Ready": True, "Current": "source-ready"},
                    {"Criteria": "Active components", "Ready": True, "Current": "3"},
                    {"Criteria": "Target weight total", "Ready": True, "Current": "100.00%"},
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "portfolio_curve_rows": 120,
                    "curve_provenance": {
                        "portfolio_curve_source": "actual_runtime_replay",
                        "portfolio_curve_rows": 120,
                        "runtime_recheck_status": "PASS",
                        "runtime_recheck_id": "replay-1",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                        "actual_period": {"start": "2020-01-31", "end": "2026-05-20"},
                        "requested_period": {"start": "2020-01-31", "end": "2026-05-20"},
                    },
                    "period_coverage": {
                        "status": "PASS",
                        "actual_period": {"start": "2020-01-31", "end": "2026-05-20"},
                        "requested_period": {"start": "2020-01-31", "end": "2026-05-20"},
                    },
                    "benchmark_parity": {
                        "status": "PASS",
                        "metrics": {"coverage_ratio": 1.0, "same_period": True, "same_frequency": True},
                    },
                },
                "temporal_validation": {
                    "status": "PASS",
                    "summary": "36M walk-forward 12 windows: worst excess 2.00%.",
                    "metrics": {
                        "window_count": 12,
                        "worst_rolling_excess_return": 0.02,
                        "negative_excess_window_share": 0.0,
                        "worst_drawdown_gap": 0.0,
                        "portfolio_curve_source": "actual_runtime_replay",
                    },
                },
                "oos_holdout_validation": {
                    "status": "PASS",
                    "summary": "OOS holdout: out excess 3.00%, drawdown gap 0.00%.",
                    "metrics": {
                        "in_sample_months": 30,
                        "out_sample_months": 30,
                        "out_sample_excess_return": 0.03,
                        "excess_change": 0.0,
                        "out_sample_drawdown_gap": 0.0,
                    },
                },
                "regime_split_validation": {
                    "status": "PASS",
                    "summary": "Regime split 3 buckets / 59 months: worst excess 1.00%.",
                    "metrics": {
                        "regime_bucket_count": 3,
                        "common_months": 59,
                        "stress_regime_months": 36,
                        "worst_regime_excess_return": 0.01,
                        "worst_regime_drawdown_gap": 0.0,
                        "macro_source": "finance.loaders.macro.load_macro_series_observations",
                    },
                },
                "provider_coverage_display_rows": [
                    {"Area": "ETF Operability", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "ETF Holdings", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "ETF Exposure", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "Macro Context", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "robustness_validation": {
                    "robustness_route": "READY_FOR_STRESS_SWEEP",
                    "robustness_lab_board": {"status": "PASS", "summary": "stress / rolling / sensitivity attached"},
                },
                "survivorship_control": {"status": "controlled"},
                "diagnostic_summary": {"status_counts": {"NOT_RUN": 0}},
            }
        )

        self.assertEqual(audit["route"], VALIDATION_EFFICACY_READY)
        self.assertEqual(audit["metrics"]["pass"], 13)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def test_walkforward_temporal_validation_uses_benchmark_aligned_windows(self) -> None:
        from app.services.backtest_temporal_validation import build_walkforward_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        portfolio["Total Return"] = portfolio["Total Balance"].pct_change().fillna(0.0)
        benchmark["Total Return"] = benchmark["Total Balance"].pct_change().fillna(0.0)

        evidence = build_walkforward_validation(
            portfolio,
            benchmark,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
            window_months=12,
        )

        self.assertEqual(evidence["schema_version"], "walkforward_validation_contract_v1")
        self.assertEqual(evidence["status"], "PASS")
        self.assertGreater(evidence["metrics"]["window_count"], 3)
        self.assertGreaterEqual(evidence["metrics"]["worst_rolling_excess_return"], 0.0)
        self.assertFalse(evidence["registry_write"])
        self.assertFalse(evidence["memo_persistence"])

    def test_walkforward_temporal_validation_does_not_pass_short_or_proxy_only_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_walkforward_validation

        short_dates = pd.date_range("2023-01-31", periods=10, freq="ME")
        short_curve = pd.DataFrame(
            {
                "Date": short_dates,
                "Total Balance": [100.0 + idx for idx in range(len(short_dates))],
                "Total Return": [0.0] + [0.01] * (len(short_dates) - 1),
            }
        )
        short_evidence = build_walkforward_validation(
            short_curve,
            short_curve,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
            window_months=12,
        )

        self.assertEqual(short_evidence["status"], "NEEDS_INPUT")

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        proxy_portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_evidence = build_walkforward_validation(
            proxy_portfolio,
            proxy_benchmark,
            portfolio_curve_source="component_curve_weighted_proxy",
            benchmark_curve_source="db_price_proxy",
            benchmark_parity={"status": "PASS"},
            window_months=12,
        )

        self.assertEqual(proxy_evidence["status"], "REVIEW")
        self.assertTrue(proxy_evidence["metrics"]["proxy_evidence"])

    def test_oos_holdout_validation_uses_out_sample_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_oos_holdout_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )

        evidence = build_oos_holdout_validation(
            portfolio,
            benchmark,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(evidence["schema_version"], "oos_holdout_validation_contract_v1")
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["metrics"]["in_sample_months"], 30)
        self.assertEqual(evidence["metrics"]["out_sample_months"], 30)
        self.assertGreaterEqual(evidence["metrics"]["out_sample_excess_return"], 0.0)
        self.assertFalse(evidence["registry_write"])
        self.assertFalse(evidence["memo_persistence"])

    def test_oos_holdout_validation_does_not_pass_short_or_proxy_only_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_oos_holdout_validation

        short_dates = pd.date_range("2023-01-31", periods=10, freq="ME")
        short_curve = pd.DataFrame(
            {
                "Date": short_dates,
                "Total Balance": [100.0 + idx for idx in range(len(short_dates))],
            }
        )
        short_evidence = build_oos_holdout_validation(
            short_curve,
            short_curve,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(short_evidence["status"], "NEEDS_INPUT")

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        proxy_portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        proxy_evidence = build_oos_holdout_validation(
            proxy_portfolio,
            proxy_benchmark,
            portfolio_curve_source="component_curve_weighted_proxy",
            benchmark_curve_source="db_price_proxy",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(proxy_evidence["status"], "REVIEW")
        self.assertTrue(proxy_evidence["metrics"]["proxy_evidence"])

    def test_regime_split_validation_uses_macro_bucket_evidence(self) -> None:
        from app.services.backtest_temporal_validation import build_regime_split_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        macro = _macro_regime_rows(dates)

        evidence = build_regime_split_validation(
            portfolio,
            benchmark,
            macro,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            macro_source="finance.loaders.macro.load_macro_series_observations",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(evidence["schema_version"], "regime_split_validation_contract_v1")
        self.assertEqual(evidence["status"], "PASS")
        self.assertEqual(evidence["metrics"]["regime_bucket_count"], 3)
        self.assertGreaterEqual(evidence["metrics"]["stress_regime_months"], 3)
        self.assertGreaterEqual(evidence["metrics"]["worst_regime_excess_return"], 0.0)
        self.assertFalse(evidence["registry_write"])
        self.assertFalse(evidence["memo_persistence"])

    def test_regime_split_validation_does_not_pass_missing_or_proxy_macro(self) -> None:
        from app.services.backtest_temporal_validation import build_regime_split_validation

        dates = pd.date_range("2020-01-31", periods=60, freq="ME")
        portfolio = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.012 ** idx) for idx in range(len(dates))],
            }
        )
        benchmark = pd.DataFrame(
            {
                "Date": dates,
                "Total Balance": [100.0 * (1.006 ** idx) for idx in range(len(dates))],
            }
        )
        missing_evidence = build_regime_split_validation(
            portfolio,
            benchmark,
            pd.DataFrame(),
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            macro_source="missing",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(missing_evidence["status"], "NEEDS_INPUT")

        proxy_macro = _macro_regime_rows(dates, source_type="computed_proxy", coverage_status="proxy")
        proxy_evidence = build_regime_split_validation(
            portfolio,
            benchmark,
            proxy_macro,
            portfolio_curve_source="actual_runtime_replay",
            benchmark_curve_source="actual_runtime_replay",
            macro_source="computed_proxy_macro",
            benchmark_parity={"status": "PASS"},
        )

        self.assertEqual(proxy_evidence["status"], "REVIEW")
        self.assertTrue(proxy_evidence["metrics"]["proxy_evidence"])

    def test_missing_runtime_and_provider_evidence_are_not_passed(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_NEEDS_INPUT,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "selection_source_id": "source-gap",
                "checks": [
                    {"Criteria": "Selection source", "Ready": True, "Current": "source-gap"},
                    {"Criteria": "Active components", "Ready": True, "Current": "2"},
                    {"Criteria": "Target weight total", "Ready": True, "Current": "100.00%"},
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": False, "Current": "NOT_RUN"},
                    {"Criteria": "Runtime period coverage", "Ready": False, "Current": "NOT_RUN"},
                    {"Criteria": "Provider coverage", "Ready": False, "Current": "NOT_RUN"},
                    {"Criteria": "Benchmark parity", "Ready": False, "Current": "NOT_RUN"},
                ],
                "provider_coverage_display_rows": [
                    {"Area": "ETF Operability", "Diagnostic Status": "NOT_RUN", "Freshness": "not_run"},
                    {"Area": "ETF Holdings", "Diagnostic Status": "NOT_RUN", "Freshness": "not_run"},
                ],
                "diagnostic_summary": {"status_counts": {"NOT_RUN": 4}},
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], VALIDATION_EFFICACY_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Runtime replay evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Provider / freshness evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Survivorship / universe guard"]["Status"], "REVIEW")

    def test_survivorship_guard_uses_data_coverage_lifecycle_evidence(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_READY,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "selection_source_id": "source-lifecycle",
                "checks": [
                    {"Criteria": "Selection source", "Ready": True, "Current": "source-lifecycle"},
                    {"Criteria": "Active components", "Ready": True, "Current": "2"},
                    {"Criteria": "Target weight total", "Ready": True, "Current": "100.00%"},
                    {"Criteria": "Data Trust", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "portfolio_curve_rows": 120,
                    "curve_provenance": {
                        "portfolio_curve_source": "actual_runtime_replay",
                        "portfolio_curve_rows": 120,
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                    "benchmark_parity": {
                        "status": "PASS",
                        "metrics": {"coverage_ratio": 1.0, "same_period": True, "same_frequency": True},
                    },
                },
                "provider_coverage_display_rows": [
                    {"Area": "ETF Operability", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Area": "ETF Holdings", "Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "robustness_validation": {
                    "robustness_route": "READY_FOR_STRESS_SWEEP",
                    "robustness_lab_board": {"status": "PASS", "summary": "stress / rolling / sensitivity attached"},
                },
                "data_coverage_audit": {
                    "rows": [
                        {
                            "Criteria": "Survivorship / delisting control",
                            "Status": "PASS",
                            "Evidence": "historical lifecycle rows cover requested period",
                        }
                    ]
                },
                "diagnostic_summary": {"status_counts": {"NOT_RUN": 0}},
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], VALIDATION_EFFICACY_READY)
        self.assertEqual(rows_by_criteria["Survivorship / universe guard"]["Status"], "PASS")


class BacktestRealismAuditContractTests(unittest.TestCase):
    def test_turnover_postprocess_marks_missing_holding_columns(self) -> None:
        from app.runtime.backtest import _apply_transaction_cost_postprocess

        result_df = pd.DataFrame(
            [
                {"Date": "2020-01-31", "Total Balance": 1000.0, "Total Return": None},
                {"Date": "2020-02-29", "Total Balance": 1010.0, "Total Return": 0.01},
            ]
        )

        hardened, diagnostics = _apply_transaction_cost_postprocess(
            result_df,
            transaction_cost_bps=10.0,
        )

        self.assertEqual(diagnostics["turnover_estimation_status"], "not_estimated_missing_holdings")
        self.assertIn("End Ticker", diagnostics["turnover_input_missing_columns"])
        self.assertTrue(hardened["Turnover"].isna().all())
        self.assertEqual(diagnostics["estimated_cost_total"], 0.0)
        self.assertEqual(diagnostics["net_cost_curve_status"], "applied_without_turnover_estimate")
        self.assertTrue(diagnostics["total_balance_is_net_of_cost"])
        self.assertEqual(diagnostics["estimated_cost_positive_rows"], 0)

    def test_turnover_postprocess_estimates_from_holdings(self) -> None:
        from app.runtime.backtest import _apply_transaction_cost_postprocess

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Total Balance": 1000.0,
                    "Total Return": None,
                    "End Ticker": [],
                    "End Balance": [],
                    "Next Ticker": ["SPY"],
                    "Next Balance": [1000.0],
                    "Cash": 0.0,
                    "Rebalancing": True,
                },
                {
                    "Date": "2020-02-29",
                    "Total Balance": 1010.0,
                    "Total Return": 0.01,
                    "End Ticker": ["SPY"],
                    "End Balance": [1010.0],
                    "Next Ticker": ["TLT"],
                    "Next Balance": [1010.0],
                    "Cash": 0.0,
                    "Rebalancing": True,
                },
            ]
        )

        hardened, diagnostics = _apply_transaction_cost_postprocess(
            result_df,
            transaction_cost_bps=10.0,
        )

        self.assertEqual(diagnostics["turnover_estimation_status"], "estimated_from_holdings")
        self.assertEqual(diagnostics["turnover_observation_count"], 2)
        self.assertEqual(diagnostics["turnover_rebalance_rows"], 2)
        self.assertEqual(diagnostics["max_turnover"], 1.0)
        self.assertGreater(diagnostics["estimated_cost_total"], 0.0)
        self.assertEqual(diagnostics["net_cost_curve_status"], "applied_with_measurable_cost")
        self.assertGreater(diagnostics["estimated_cost_positive_rows"], 0)
        self.assertGreater(diagnostics["gross_net_end_balance_delta"], 0.0)
        self.assertIn("Turnover", hardened.columns)

    def test_ready_audit_uses_cost_turnover_and_liquidity_metadata_without_writes(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_READY,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "cost_model_snapshot": {
                        "cost_model_contract_version": "cost_model_source_contract_v1",
                        "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                        "cost_application_status": "applied_to_result_curve",
                        "cost_application_target": "result_df.Total Balance/Total Return",
                        "cost_turnover_source": "end_next_holdings_weight_delta",
                        "transaction_cost_bps": 10.0,
                        "avg_turnover": 0.15,
                        "estimated_cost_total": 125.0,
                    },
                    "turnover_evidence_snapshot": {
                        "turnover_model_contract_version": "turnover_evidence_contract_v1",
                        "turnover_estimation_status": "estimated_from_holdings",
                        "turnover_source": "end_next_holdings_weight_delta",
                        "turnover_observation_count": 24,
                        "turnover_rebalance_rows": 24,
                        "turnover_nonzero_count": 12,
                        "avg_turnover": 0.15,
                        "max_turnover": 0.4,
                        "avg_rebalance_turnover": 0.15,
                    },
                    "net_cost_curve_snapshot": {
                        "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                        "net_cost_curve_status": "applied_with_measurable_cost",
                        "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                        "total_balance_is_net_of_cost": True,
                        "net_cost_curve_rows": 24,
                        "estimated_cost_total": 125.0,
                        "estimated_cost_positive_rows": 12,
                        "gross_end_balance": 1200.0,
                        "net_end_balance": 1075.0,
                        "gross_net_end_balance_delta": 125.0,
                        "turnover_estimation_status": "estimated_from_holdings",
                    },
                    "cost_slippage_sensitivity": {
                        "schema_version": "cost_slippage_sensitivity_contract_v1",
                        "status": "PASS",
                        "computed_count": 3,
                        "review_count": 0,
                        "not_run_count": 0,
                        "runtime_followup_count": 0,
                        "summary": "Cost bps 5/10/25 and slippage spread shock passed.",
                        "rows": [
                            {
                                "Scenario": "Transaction cost bps sweep",
                                "Scope": "cost / slippage",
                                "Result Status": "PASS",
                            }
                        ],
                    },
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "real_money_hardening": True,
                            "avg_turnover": 0.15,
                            "max_turnover": 0.4,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "official operability coverage",
                            "provenance": {
                                "freshness_status": "fresh",
                                "source_mix": "official 100.0%",
                                "source_type_weights": {"official": 100.0},
                                "coverage_status_weights": {"actual": 100.0},
                                "as_of_range": "2026-05-20",
                                "stale_weight": 0.0,
                                "unknown_freshness_weight": 0.0,
                            },
                            "metrics": {
                                "review_count": 0,
                                "review_symbols": [],
                                "min_net_assets": 50_000_000_000,
                                "min_avg_daily_dollar_volume": 500_000_000,
                                "max_bid_ask_spread_pct": 0.0002,
                            },
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        self.assertEqual(audit["route"], BACKTEST_REALISM_READY)
        self.assertEqual(audit["cost_model_contract"]["application_status"], "applied_to_result_curve")
        self.assertEqual(audit["net_cost_curve_contract"]["proof_status"], "applied_with_measurable_cost")
        self.assertEqual(audit["turnover_evidence_contract"]["evidence_strength"], "actual_estimate")
        self.assertEqual(
            audit["cost_slippage_sensitivity_contract"]["evidence_strength"],
            "explicit_cost_slippage_sensitivity",
        )
        self.assertEqual(audit["liquidity_capacity_contract"]["proof_status"], "official_fresh_capacity_evidence")
        self.assertEqual(audit["metrics"]["pass"], 9)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def _ready_realism_validation_without_sensitivity(self):
        return {
            "selection_source_snapshot": {
                "construction": {"rebalance_cadence": "monthly"},
                "cost_model_snapshot": {
                    "cost_model_contract_version": "cost_model_source_contract_v1",
                    "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                    "cost_application_status": "applied_to_result_curve",
                    "cost_application_target": "result_df.Total Balance/Total Return",
                    "cost_turnover_source": "end_next_holdings_weight_delta",
                    "transaction_cost_bps": 10.0,
                    "avg_turnover": 0.15,
                    "estimated_cost_total": 125.0,
                },
                "turnover_evidence_snapshot": {
                    "turnover_model_contract_version": "turnover_evidence_contract_v1",
                    "turnover_estimation_status": "estimated_from_holdings",
                    "turnover_source": "end_next_holdings_weight_delta",
                    "turnover_observation_count": 24,
                    "turnover_rebalance_rows": 24,
                    "turnover_nonzero_count": 12,
                    "avg_turnover": 0.15,
                    "max_turnover": 0.4,
                    "avg_rebalance_turnover": 0.15,
                },
                "net_cost_curve_snapshot": {
                    "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                    "net_cost_curve_status": "applied_with_measurable_cost",
                    "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                    "total_balance_is_net_of_cost": True,
                    "net_cost_curve_rows": 24,
                    "estimated_cost_total": 125.0,
                    "estimated_cost_positive_rows": 12,
                    "gross_end_balance": 1200.0,
                    "net_end_balance": 1075.0,
                    "gross_net_end_balance_delta": 125.0,
                    "turnover_estimation_status": "estimated_from_holdings",
                },
                "source_snapshot": {
                    "settings_snapshot": {
                        "transaction_cost_bps": 10.0,
                        "rebalance_interval": 1,
                        "operator_tax_scope_acknowledged": True,
                    },
                    "meta": {
                        "real_money_hardening": True,
                        "avg_turnover": 0.15,
                        "max_turnover": 0.4,
                        "net_cagr_spread": 0.03,
                        "promotion_min_net_cagr_spread": -0.02,
                    },
                },
            },
            "provider_coverage": {
                "coverage": {
                    "operability": {
                        "diagnostic_status": "PASS",
                        "coverage_weight": 100.0,
                        "summary": "official operability coverage",
                        "provenance": {
                            "freshness_status": "fresh",
                            "source_mix": "official 100.0%",
                            "source_type_weights": {"official": 100.0},
                            "coverage_status_weights": {"actual": 100.0},
                            "as_of_range": "2026-05-20",
                            "stale_weight": 0.0,
                            "unknown_freshness_weight": 0.0,
                        },
                        "metrics": {
                            "review_count": 0,
                            "review_symbols": [],
                            "min_net_assets": 50_000_000_000,
                            "min_avg_daily_dollar_volume": 500_000_000,
                            "max_bid_ask_spread_pct": 0.0002,
                        },
                    }
                }
            },
            "diagnostic_results": [
                {
                    "domain": "operability_cost_liquidity",
                    "status": "PASS",
                    "metrics": {"one_way_cost_bps": 10.0},
                    "evidence_rows": [
                        {
                            "Check": "One-way cost bps assumption",
                            "Status": "PASS",
                            "Evidence": "cost bps exists but this is not sensitivity evidence",
                        }
                    ],
                }
            ],
        }

    def test_missing_cost_slippage_sensitivity_requires_review_despite_ready_costs(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(self._ready_realism_validation_without_sensitivity())

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Cost / slippage sensitivity evidence"]["Status"], "REVIEW")
        self.assertEqual(
            audit["cost_slippage_sensitivity_contract"]["evidence_strength"],
            "missing_sensitivity_evidence",
        )

    def test_generic_robustness_sensitivity_without_cost_axis_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        validation = self._ready_realism_validation_without_sensitivity()
        validation["sensitivity_interpretation"] = {
            "status": "PASS",
            "summary": "2 curve sensitivity checks computed.",
            "computed_count": 2,
            "review_count": 0,
            "runtime_followup_count": 0,
            "rows": [
                {
                    "Check": "Weight tilt sensitivity",
                    "Status": "PASS",
                    "Finding": "component weights stable",
                }
            ],
        }
        validation["robustness_validation"] = {
            "robustness_lab_board": {
                "status": "PASS",
                "metrics": {
                    "computed_sensitivity_checks": 2,
                    "sensitivity_review_count": 0,
                    "runtime_followup_count": 0,
                },
                "summary_rows": [
                    {
                        "Check": "Sensitivity coverage",
                        "Status": "PASS",
                        "Current": "computed 2",
                        "Evidence": "weight and drop-one checks",
                    }
                ],
            }
        }

        audit = build_backtest_realism_audit(validation)

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Cost / slippage sensitivity evidence"]["Status"], "REVIEW")
        self.assertEqual(
            audit["cost_slippage_sensitivity_contract"]["evidence_strength"],
            "generic_sensitivity_only",
        )

    def test_legacy_provider_pass_without_capacity_contract_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "cost_model_snapshot": {
                        "cost_model_contract_version": "cost_model_source_contract_v1",
                        "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                        "cost_application_status": "applied_to_result_curve",
                        "transaction_cost_bps": 10.0,
                        "estimated_cost_total": 125.0,
                    },
                    "turnover_evidence_snapshot": {
                        "turnover_model_contract_version": "turnover_evidence_contract_v1",
                        "turnover_estimation_status": "estimated_from_holdings",
                        "turnover_source": "end_next_holdings_weight_delta",
                        "turnover_observation_count": 24,
                        "turnover_rebalance_rows": 24,
                        "avg_turnover": 0.15,
                    },
                    "net_cost_curve_snapshot": {
                        "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                        "net_cost_curve_status": "applied_with_measurable_cost",
                        "total_balance_is_net_of_cost": True,
                        "net_cost_curve_rows": 24,
                        "estimated_cost_total": 125.0,
                        "estimated_cost_positive_rows": 12,
                        "gross_end_balance": 1200.0,
                        "net_end_balance": 1075.0,
                        "gross_net_end_balance_delta": 125.0,
                    },
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "real_money_hardening": True,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "legacy pass without provenance",
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Liquidity / operability evidence"]["Status"], "REVIEW")
        self.assertEqual(
            audit["liquidity_capacity_contract"]["proof_status"],
            "legacy_provider_pass_without_capacity_contract",
        )

    def test_cost_assumption_without_application_proof_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_NEEDS_INPUT,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "avg_turnover": 0.15,
                            "max_turnover": 0.4,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "official operability coverage",
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Transaction cost model"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Net cost curve proof"]["Status"], "NEEDS_INPUT")
        self.assertEqual(audit["cost_model_contract"]["application_status"], "assumption_only")

    def test_rebalance_cadence_without_turnover_estimate_requires_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_REVIEW,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {
                    "construction": {"rebalance_cadence": "monthly"},
                    "cost_model_snapshot": {
                        "cost_model_contract_version": "cost_model_source_contract_v1",
                        "cost_model_source": "app.runtime.backtest._apply_transaction_cost_postprocess",
                        "cost_application_status": "applied_to_result_curve",
                        "transaction_cost_bps": 10.0,
                        "estimated_cost_total": 0.0,
                    },
                    "turnover_evidence_snapshot": {
                        "turnover_model_contract_version": "turnover_evidence_contract_v1",
                        "turnover_estimation_status": "not_estimated_missing_holdings",
                        "turnover_source": "missing_result_holding_columns",
                        "turnover_input_missing_columns": ["End Ticker", "Next Ticker"],
                    },
                    "net_cost_curve_snapshot": {
                        "net_cost_curve_contract_version": "net_cost_curve_contract_v1",
                        "net_cost_curve_status": "applied_without_turnover_estimate",
                        "net_cost_curve_application_target": "result_df.Total Balance/Total Return",
                        "total_balance_is_net_of_cost": True,
                        "net_cost_curve_rows": 24,
                        "estimated_cost_total": 0.0,
                        "estimated_cost_positive_rows": 0,
                        "gross_net_end_balance_delta": 0.0,
                        "turnover_estimation_status": "not_estimated_missing_holdings",
                    },
                    "source_snapshot": {
                        "settings_snapshot": {
                            "transaction_cost_bps": 10.0,
                            "rebalance_interval": 1,
                            "operator_tax_scope_acknowledged": True,
                        },
                        "meta": {
                            "real_money_hardening": True,
                            "net_cagr_spread": 0.03,
                            "promotion_min_net_cagr_spread": -0.02,
                        },
                    },
                },
                "provider_coverage": {
                    "coverage": {
                        "operability": {
                            "diagnostic_status": "PASS",
                            "coverage_weight": 100.0,
                            "summary": "official operability coverage",
                        }
                    }
                },
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "PASS",
                        "metrics": {"one_way_cost_bps": 10.0},
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_REVIEW)
        self.assertEqual(rows_by_criteria["Net cost curve proof"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Turnover evidence"]["Status"], "REVIEW")
        self.assertEqual(audit["net_cost_curve_contract"]["proof_status"], "applied_without_turnover_estimate")
        self.assertEqual(audit["turnover_evidence_contract"]["evidence_strength"], "missing_estimate")

    def test_missing_cost_and_liquidity_evidence_are_not_passed(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_NEEDS_INPUT,
            build_backtest_realism_audit,
        )

        audit = build_backtest_realism_audit(
            {
                "selection_source_snapshot": {"construction": {}},
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "status": "NOT_RUN",
                    }
                ],
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], BACKTEST_REALISM_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Transaction cost model"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Liquidity / operability evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Tax / account scope"]["Status"], "REVIEW")


class DataCoverageAuditContractTests(unittest.TestCase):
    def test_ready_audit_uses_db_price_provider_and_survivorship_evidence_without_writes(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_READY,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY", "TLT"],
                    "symbol_weights": {"SPY": 60.0, "TLT": 40.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "TLT",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                    ],
                    "asset_profile_rows": [
                        {"symbol": "SPY", "status": "active"},
                        {"symbol": "TLT", "status": "active"},
                    ],
                },
                "provider_coverage_display_rows": [
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
                "survivorship_control": {"status": "controlled"},
            }
        )

        self.assertEqual(audit["route"], DATA_COVERAGE_READY)
        self.assertEqual(audit["metrics"]["pass"], 6)
        self.assertEqual(audit["metrics"]["price_covered_weight"], 100.0)
        self.assertFalse(audit["execution_boundary"]["db_write"])
        self.assertFalse(audit["execution_boundary"]["registry_write"])
        self.assertFalse(audit["execution_boundary"]["memo_persistence"])

    def test_lifecycle_rows_control_survivorship_without_explicit_flag(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_READY,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY", "TLT"],
                    "symbol_weights": {"SPY": 60.0, "TLT": 40.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "TLT",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                    ],
                    "asset_profile_rows": [
                        {"symbol": "SPY", "status": "active"},
                        {"symbol": "TLT", "status": "active"},
                    ],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "historical_feed",
                            "source_type": "historical_listing",
                            "coverage_status": "actual",
                            "first_seen_date": "1993-01-29",
                            "last_seen_date": None,
                        },
                        {
                            "symbol": "TLT",
                            "listing_status": "active",
                            "source": "historical_feed",
                            "source_type": "historical_listing",
                            "coverage_status": "actual",
                            "first_seen_date": "2002-07-26",
                            "last_seen_date": None,
                        },
                    ],
                },
                "provider_coverage_display_rows": [
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                    {"Diagnostic Status": "PASS", "Freshness": "fresh"},
                ],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_READY)
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "PASS")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "PASS")
        self.assertEqual(audit["metrics"]["lifecycle_covered_symbols"], ["SPY", "TLT"])

    def test_current_listing_snapshot_does_not_control_historical_survivorship(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_REVIEW,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY"],
                    "symbol_weights": {"SPY": 100.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        }
                    ],
                    "asset_profile_rows": [{"symbol": "SPY", "status": "active"}],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "nyse_listings_directory",
                            "source_type": "current_listing_snapshot",
                            "coverage_status": "partial",
                            "first_seen_date": "2026-05-28",
                            "last_seen_date": "2026-05-28",
                        }
                    ],
                },
                "provider_coverage_display_rows": [{"Diagnostic Status": "PASS", "Freshness": "fresh"}],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_REVIEW)
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "REVIEW")
        self.assertIn("SPY", audit["metrics"]["lifecycle_partial_symbols"])
        self.assertEqual(audit["metrics"]["lifecycle_current_snapshot_symbols"], ["SPY"])

    def test_missing_db_price_and_universe_evidence_are_not_passed(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_NEEDS_INPUT,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY"],
                    "symbol_weights": {"SPY": 100.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [],
                    "asset_profile_rows": [],
                },
                "provider_coverage_display_rows": [],
                "curve_evidence": {},
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_NEEDS_INPUT)
        self.assertEqual(rows_by_criteria["Price DB window coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "NEEDS_INPUT")

    def test_lifecycle_audit_scoring_separates_partial_identity_computed_and_actual_evidence(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_REVIEW,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY", "AAPL", "ABC"],
                    "symbol_weights": {"SPY": 40.0, "AAPL": 40.0, "ABC": 20.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "AAPL",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                        {
                            "symbol": "ABC",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        },
                    ],
                    "asset_profile_rows": [
                        {"symbol": "SPY", "status": "active"},
                        {"symbol": "AAPL", "status": "active"},
                        {"symbol": "ABC", "status": "active"},
                    ],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "historical_feed",
                            "source_type": "historical_listing",
                            "coverage_status": "actual",
                            "first_seen_date": "1993-01-29",
                            "last_seen_date": None,
                        },
                        {
                            "symbol": "AAPL",
                            "listing_status": "active",
                            "source": "nasdaq_symdir_nasdaqlisted",
                            "source_type": "current_listing_snapshot",
                            "coverage_status": "partial",
                            "first_seen_date": "2026-05-28",
                            "last_seen_date": "2026-05-28",
                            "event_type": "listing_observed",
                        },
                        {
                            "symbol": "AAPL",
                            "listing_status": "active",
                            "source": "sec_company_tickers_exchange",
                            "source_type": "current_listing_snapshot",
                            "coverage_status": "partial",
                            "first_seen_date": "2026-05-28",
                            "last_seen_date": "2026-05-28",
                            "event_type": "listing_observed",
                            "related_cik": 320193,
                        },
                        {
                            "symbol": "AAPL",
                            "listing_status": "active",
                            "source": "computed_snapshot_lifecycle",
                            "source_type": "computed_from_snapshots",
                            "coverage_status": "partial",
                            "first_seen_date": "2019-01-01",
                            "last_seen_date": "2021-12-31",
                            "event_type": "historical_membership",
                        },
                        {
                            "symbol": "ABC",
                            "listing_status": "delisted",
                            "source": "sec_form25_abc",
                            "source_type": "delisting_feed",
                            "coverage_status": "actual",
                            "first_seen_date": None,
                            "last_seen_date": "2020-06-01",
                            "event_type": "delisting",
                            "event_date": "2020-06-01",
                        },
                    ],
                },
                "provider_coverage_display_rows": [{"Diagnostic Status": "PASS", "Freshness": "fresh"}],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_REVIEW)
        self.assertEqual(audit["metrics"]["lifecycle_covered_symbols"], ["SPY"])
        self.assertEqual(audit["metrics"]["lifecycle_partial_symbols"], ["AAPL", "ABC"])
        self.assertEqual(audit["metrics"]["lifecycle_actual_symbols"], ["ABC", "SPY"])
        self.assertEqual(audit["metrics"]["lifecycle_actual_noncovering_symbols"], ["ABC"])
        self.assertEqual(audit["metrics"]["lifecycle_current_snapshot_symbols"], ["AAPL"])
        self.assertEqual(audit["metrics"]["lifecycle_identity_crosscheck_symbols"], ["AAPL"])
        self.assertEqual(audit["metrics"]["lifecycle_computed_partial_symbols"], ["AAPL"])
        self.assertEqual(audit["metrics"]["lifecycle_delisting_actual_symbols"], ["ABC"])
        self.assertEqual(
            audit["metrics"]["lifecycle_row_counts_by_category"],
            {
                "computed_partial": 1,
                "current_snapshot": 1,
                "delisting_actual": 1,
                "historical_actual": 1,
                "identity_crosscheck": 1,
            },
        )
        self.assertIn("current_snapshot=AAPL", rows_by_criteria["Universe / listing evidence"]["Evidence"])
        self.assertIn("sec_identity=AAPL", rows_by_criteria["Universe / listing evidence"]["Evidence"])
        self.assertIn("computed_partial=AAPL", rows_by_criteria["Survivorship / delisting control"]["Evidence"])
        self.assertIn("delisting_actual=ABC", rows_by_criteria["Survivorship / delisting control"]["Evidence"])


class SecForm25DelistingCollectorContractTests(unittest.TestCase):
    def test_form25_payload_maps_to_lifecycle_row_without_claiming_full_membership(self) -> None:
        from finance.data.sec_delisting import (
            build_sec_form25_lifecycle_rows,
            extract_sec_form25_filings,
            normalize_sec_ticker_map,
        )

        ticker_map = normalize_sec_ticker_map(
            {
                "0": {"cik_str": 123456, "ticker": "ABC", "title": "ABC Corp"},
            }
        )
        filings = extract_sec_form25_filings(
            {
                "filings": {
                    "recent": {
                        "form": ["10-K", "25-NSE"],
                        "accessionNumber": ["0000123456-26-000001", "0000123456-26-000002"],
                        "filingDate": ["2026-02-01", "2026-03-15"],
                        "reportDate": ["2026-01-01", ""],
                        "primaryDocument": ["abc-10k.htm", "primary_doc.xml"],
                    }
                }
            }
        )
        rows = build_sec_form25_lifecycle_rows(
            "abc",
            "stock",
            ticker_map["ABC"],
            filings,
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["symbol"], "ABC")
        self.assertEqual(row["listing_status"], "delisted")
        self.assertEqual(row["source_type"], "delisting_feed")
        self.assertEqual(row["coverage_status"], "actual")
        self.assertIsNone(row["first_seen_date"])
        self.assertEqual(row["last_seen_date"], "2026-03-15")
        self.assertEqual(row["event_type"], "delisting")
        self.assertEqual(row["event_date"], "2026-03-15")
        self.assertEqual(row["related_cik"], 123456)
        self.assertIn("sec_form25_000012345626000002", row["source"])
        self.assertIn("primary_doc.xml", row["source_ref"])
        self.assertIn('"event_type": "delisting"', row["evidence_json"])
        self.assertIn("absence of Form 25 is not active-listing proof", row["evidence_json"])

    def test_current_listing_snapshot_maps_to_partial_listing_observed_event(self) -> None:
        from finance.data import nyse_db

        class FakeDB:
            def __init__(self) -> None:
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

        fake_db = FakeDB()
        frame = pd.DataFrame(
            [
                {
                    "symbol": "spy",
                    "name": "SPDR S&P 500 ETF Trust",
                    "url": "https://www.nyse.com/quote/ARCX:SPY",
                }
            ]
        )
        with patch.object(nyse_db, "sync_table_schema"):
            count = nyse_db._upsert_symbol_lifecycle_rows(  # noqa: SLF001 - contract locks DB row semantics.
                fake_db,
                kind="etf",
                frame=frame,
                snapshot_date="2026-05-28",
            )

        self.assertEqual(count, 1)
        written_row = fake_db.executemany_calls[0][1][0]
        self.assertEqual(written_row["symbol"], "SPY")
        self.assertEqual(written_row["source_type"], "current_listing_snapshot")
        self.assertEqual(written_row["coverage_status"], "partial")
        self.assertEqual(written_row["event_type"], "listing_observed")
        self.assertEqual(written_row["event_date"], "2026-05-28")
        self.assertIsNone(written_row["related_symbol"])
        self.assertIsNone(written_row["related_cik"])
        self.assertIn("not sufficient alone for historical survivorship PASS", written_row["evidence_json"])

    def test_collector_writes_db_lifecycle_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import sec_delisting

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                if "nyse_etf" in sql:
                    return []
                if "nyse_stock" in sql:
                    return [{"symbol": "ABC"}]
                return []

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        def fake_fetch(url: str, user_agent: str, timeout: float):
            if url == sec_delisting.SEC_COMPANY_TICKERS_URL:
                return {"0": {"cik_str": 123456, "ticker": "ABC", "title": "ABC Corp"}}
            return {
                "filings": {
                    "recent": {
                        "form": ["25-NSE"],
                        "accessionNumber": ["0000123456-26-000002"],
                        "filingDate": ["2026-03-15"],
                        "reportDate": [""],
                        "primaryDocument": ["primary_doc.xml"],
                    },
                    "files": [],
                }
            }

        fake_db = FakeDB()
        with patch.object(sec_delisting, "MySQLClient", return_value=fake_db), patch.object(
            sec_delisting,
            "sync_table_schema",
        ):
            summary = sec_delisting.collect_and_store_sec_form25_delistings(
                ["ABC"],
                user_agent="Unit Test unit@example.com",
                fetch_json=fake_fetch,
                request_sleep=0,
            )

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 1)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        self.assertEqual(len(fake_db.executemany_calls), 1)
        written_row = fake_db.executemany_calls[0][1][0]
        self.assertEqual(written_row["kind"], "stock")
        self.assertEqual(written_row["source_type"], "delisting_feed")
        self.assertEqual(written_row["event_type"], "delisting")
        self.assertEqual(written_row["event_date"], "2026-03-15")

    def test_ingestion_job_surfaces_form25_coverage_gaps(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_sec_form25_delistings",
            return_value={
                "rows_written": 1,
                "unmapped_symbols": ["MISS"],
                "symbols_without_form25": [],
                "errors": [],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_sec_form25_delistings("ABC,MISS", user_agent="Unit Test unit@example.com")

        self.assertEqual(result["job_name"], "collect_sec_form25_delistings")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 1)
        self.assertIn("MISS", result["failed_symbols"])


class SymbolDirectorySnapshotCollectorContractTests(unittest.TestCase):
    def test_nasdaq_listed_snapshot_maps_to_partial_listing_observed_rows(self) -> None:
        from finance.data.symbol_directory import build_symbol_directory_lifecycle_rows

        text = "\n".join(
            [
                "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares",
                "AAPL|Apple Inc. Common Stock|Q|N|N|100|N|N",
                "QQQ|Invesco QQQ Trust, Series 1|G|N|N|100|Y|N",
                "TEST|Test Issue|Q|Y|N|100|N|N",
                "File Creation Time: 0528202613:04|||||",
            ]
        )

        rows, metadata = build_symbol_directory_lifecycle_rows(
            "nasdaqlisted",
            text,
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(metadata["event_date"], "2026-05-28")
        self.assertEqual(metadata["rows_built"], 2)
        self.assertEqual(metadata["skipped_test_issues"], 1)
        rows_by_symbol = {row["symbol"]: row for row in rows}
        self.assertEqual(rows_by_symbol["AAPL"]["kind"], "stock")
        self.assertEqual(rows_by_symbol["QQQ"]["kind"], "etf")
        self.assertEqual(rows_by_symbol["AAPL"]["source"], "nasdaq_symdir_nasdaqlisted")
        self.assertEqual(rows_by_symbol["AAPL"]["source_type"], "current_listing_snapshot")
        self.assertEqual(rows_by_symbol["AAPL"]["coverage_status"], "partial")
        self.assertEqual(rows_by_symbol["AAPL"]["event_type"], "listing_observed")
        self.assertEqual(rows_by_symbol["AAPL"]["event_date"], "2026-05-28")
        self.assertIn("not historical membership or delisting proof", rows_by_symbol["AAPL"]["evidence_json"])

    def test_otherlisted_snapshot_maps_exchange_context_without_claiming_history(self) -> None:
        from finance.data.symbol_directory import build_symbol_directory_lifecycle_rows

        text = "\n".join(
            [
                "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
                "SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY",
                "GE|GE Aerospace Common Stock|N|GE|N|100|N|GE",
                "File Creation Time: 0528202613:04|||||||",
            ]
        )

        rows, metadata = build_symbol_directory_lifecycle_rows(
            "otherlisted",
            text,
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(metadata["rows_built"], 2)
        rows_by_symbol = {row["symbol"]: row for row in rows}
        self.assertEqual(rows_by_symbol["SPY"]["kind"], "etf")
        self.assertEqual(rows_by_symbol["SPY"]["source"], "nasdaq_symdir_otherlisted")
        self.assertIn('"exchange": "P"', rows_by_symbol["SPY"]["evidence_json"])
        self.assertIn('"nasdaq_symbol": "SPY"', rows_by_symbol["SPY"]["evidence_json"])
        self.assertEqual(rows_by_symbol["GE"]["event_type"], "listing_observed")

    def test_collector_writes_symbol_directory_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import symbol_directory

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                return []

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        def fake_fetch(url: str, user_agent: str, timeout: float) -> str:
            if url == symbol_directory.NASDAQ_LISTED_URL:
                return "\n".join(
                    [
                        "Symbol|Security Name|Market Category|Test Issue|Financial Status|Round Lot Size|ETF|NextShares",
                        "AAPL|Apple Inc. Common Stock|Q|N|N|100|N|N",
                        "File Creation Time: 0528202613:04|||||",
                    ]
                )
            return "\n".join(
                [
                    "ACT Symbol|Security Name|Exchange|CQS Symbol|ETF|Round Lot Size|Test Issue|NASDAQ Symbol",
                    "SPY|SPDR S&P 500 ETF Trust|P|SPY|Y|100|N|SPY",
                    "File Creation Time: 0528202613:04|||||||",
                ]
            )

        fake_db = FakeDB()
        with patch.object(symbol_directory, "MySQLClient", return_value=fake_db), patch.object(
            symbol_directory,
            "sync_table_schema",
        ):
            summary = symbol_directory.collect_and_store_symbol_directory_snapshots(
                user_agent="Unit Test unit@example.com",
                fetch_text=fake_fetch,
            )

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 2)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        written_rows = fake_db.executemany_calls[0][1]
        self.assertEqual({row["source"] for row in written_rows}, {"nasdaq_symdir_nasdaqlisted", "nasdaq_symdir_otherlisted"})
        self.assertEqual({row["event_type"] for row in written_rows}, {"listing_observed"})
        self.assertEqual({row["coverage_status"] for row in written_rows}, {"partial"})

    def test_ingestion_job_wraps_symbol_directory_snapshot_summary(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_symbol_directory_snapshots",
            return_value={
                "rows_written": 2,
                "rows_found": 2,
                "errors": [],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_symbol_directory_snapshots(user_agent="Unit Test unit@example.com")

        self.assertEqual(result["job_name"], "collect_symbol_directory_snapshots")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(result["symbols_processed"], 2)


class SecCompanyTickerCrosscheckContractTests(unittest.TestCase):
    def test_sec_exchange_payload_maps_to_partial_listing_observed_rows(self) -> None:
        from finance.data.sec_company_tickers import (
            build_sec_company_ticker_lifecycle_rows,
            normalize_sec_company_tickers_exchange,
        )

        records = normalize_sec_company_tickers_exchange(
            {
                "fields": ["cik", "name", "ticker", "exchange"],
                "data": [
                    [320193, "Apple Inc.", "AAPL", "Nasdaq"],
                    [1067983, "BERKSHIRE HATHAWAY INC", "BRK-B", "NYSE"],
                    ["bad", "Bad CIK", "BAD", "NYSE"],
                ],
            }
        )
        rows, metadata = build_sec_company_ticker_lifecycle_rows(
            records,
            kind_by_symbol={"AAPL": "stock", "BRK-B": "stock"},
            symbols=["AAPL"],
            collected_at="2026-05-28 00:00:00",
            snapshot_date="2026-05-28",
        )

        self.assertEqual(len(records), 2)
        self.assertEqual(len(rows), 1)
        self.assertEqual(metadata["skipped_not_requested"], 1)
        row = rows[0]
        self.assertEqual(row["symbol"], "AAPL")
        self.assertEqual(row["kind"], "stock")
        self.assertEqual(row["source"], "sec_company_tickers_exchange")
        self.assertEqual(row["source_type"], "current_listing_snapshot")
        self.assertEqual(row["coverage_status"], "partial")
        self.assertEqual(row["event_type"], "listing_observed")
        self.assertEqual(row["event_date"], "2026-05-28")
        self.assertEqual(row["related_cik"], 320193)
        self.assertIn('"exchange": "Nasdaq"', row["evidence_json"])
        self.assertIn("not historical membership proof", row["evidence_json"])

    def test_collector_writes_sec_crosscheck_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import sec_company_tickers

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                if "nyse_etf" in sql:
                    return [{"symbol": "QQQ"}]
                if "nyse_stock" in sql:
                    return [{"symbol": "AAPL"}]
                return []

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        def fake_fetch(url: str, user_agent: str, timeout: float):
            self.assertEqual(url, sec_company_tickers.SEC_COMPANY_TICKERS_EXCHANGE_URL)
            return {
                "fields": ["cik", "name", "ticker", "exchange"],
                "data": [
                    [320193, "Apple Inc.", "AAPL", "Nasdaq"],
                    [111111, "Invesco QQQ Trust", "QQQ", "Nasdaq"],
                ],
            }

        fake_db = FakeDB()
        with patch.object(sec_company_tickers, "MySQLClient", return_value=fake_db), patch.object(
            sec_company_tickers,
            "sync_table_schema",
        ):
            summary = sec_company_tickers.collect_and_store_sec_company_ticker_crosscheck(
                symbols=["AAPL", "QQQ"],
                user_agent="Unit Test unit@example.com",
                fetch_json=fake_fetch,
                snapshot_date="2026-05-28",
            )

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 2)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        rows_by_symbol = {row["symbol"]: row for row in fake_db.executemany_calls[0][1]}
        self.assertEqual(rows_by_symbol["AAPL"]["kind"], "stock")
        self.assertEqual(rows_by_symbol["QQQ"]["kind"], "etf")
        self.assertEqual({row["coverage_status"] for row in rows_by_symbol.values()}, {"partial"})
        self.assertEqual({row["event_type"] for row in rows_by_symbol.values()}, {"listing_observed"})

    def test_ingestion_job_wraps_sec_crosscheck_summary(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_sec_company_ticker_crosscheck",
            return_value={
                "requested": 2,
                "rows_written": 1,
                "requested_missing_symbols": ["MISS"],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_sec_company_ticker_crosscheck("AAPL,MISS", user_agent="Unit Test unit@example.com")

        self.assertEqual(result["job_name"], "collect_sec_company_ticker_crosscheck")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 1)
        self.assertIn("MISS", result["failed_symbols"])


class ComputedSnapshotLifecycleContractTests(unittest.TestCase):
    def test_repeated_current_snapshots_build_partial_computed_row(self) -> None:
        from finance.data.computed_lifecycle import build_computed_snapshot_lifecycle_rows

        rows, metadata = build_computed_snapshot_lifecycle_rows(
            [
                {
                    "symbol": "spy",
                    "kind": "etf",
                    "listing_status": "active",
                    "source": "nasdaq_symdir_otherlisted",
                    "source_type": "current_listing_snapshot",
                    "coverage_status": "partial",
                    "first_seen_date": "2026-05-01",
                    "last_seen_date": "2026-05-28",
                    "event_type": "listing_observed",
                    "event_date": "2026-05-28",
                    "name": "SPDR S&P 500 ETF Trust",
                },
                {
                    "symbol": "ONE",
                    "kind": "stock",
                    "listing_status": "active",
                    "source": "sec_company_tickers_exchange",
                    "source_type": "current_listing_snapshot",
                    "coverage_status": "partial",
                    "first_seen_date": "2026-05-28",
                    "last_seen_date": "2026-05-28",
                    "event_type": "listing_observed",
                    "event_date": "2026-05-28",
                },
            ],
            collected_at="2026-05-28 00:00:00",
        )

        self.assertEqual(metadata["rows_built"], 1)
        self.assertEqual(metadata["skipped_insufficient_observation_dates"], 1)
        row = rows[0]
        self.assertEqual(row["symbol"], "SPY")
        self.assertEqual(row["kind"], "etf")
        self.assertEqual(row["listing_status"], "active")
        self.assertEqual(row["source"], "computed_snapshot_lifecycle")
        self.assertEqual(row["source_type"], "computed_from_snapshots")
        self.assertEqual(row["coverage_status"], "partial")
        self.assertEqual(row["first_seen_date"], "2026-05-01")
        self.assertEqual(row["last_seen_date"], "2026-05-28")
        self.assertEqual(row["event_type"], "historical_membership")
        self.assertEqual(row["event_date"], "2026-05-28")
        self.assertIn('"pass_eligible": false', row["evidence_json"])
        self.assertIn("absence from current snapshots is not delisting proof", row["evidence_json"])

    def test_collector_writes_computed_rows_without_jsonl_side_effects(self) -> None:
        from finance.data import computed_lifecycle

        class FakeDB:
            def __init__(self) -> None:
                self.used_db: str | None = None
                self.executemany_calls: list[tuple[str, list[dict]]] = []

            def use_db(self, db_name: str) -> None:
                self.used_db = db_name

            def query(self, sql: str, params=None) -> list[dict]:
                return [
                    {
                        "symbol": "SPY",
                        "kind": "etf",
                        "listing_status": "active",
                        "source": "nasdaq_symdir_otherlisted",
                        "source_type": "current_listing_snapshot",
                        "coverage_status": "partial",
                        "first_seen_date": "2026-05-01",
                        "last_seen_date": "2026-05-28",
                        "event_type": "listing_observed",
                        "event_date": "2026-05-28",
                        "name": "SPDR S&P 500 ETF Trust",
                    }
                ]

            def execute(self, sql: str, params=None) -> None:
                return None

            def executemany(self, sql: str, params: list[dict]) -> None:
                self.executemany_calls.append((sql, params))

            def close(self) -> None:
                return None

        fake_db = FakeDB()
        with patch.object(computed_lifecycle, "MySQLClient", return_value=fake_db), patch.object(
            computed_lifecycle,
            "sync_table_schema",
        ):
            summary = computed_lifecycle.collect_and_store_computed_snapshot_lifecycle(symbols=["SPY"])

        self.assertEqual(fake_db.used_db, "finance_meta")
        self.assertEqual(summary["rows_written"], 1)
        self.assertEqual(summary["target_table"], "finance_meta.nyse_symbol_lifecycle")
        self.assertFalse(summary["execution_boundary"]["registry_write"])
        self.assertFalse(summary["execution_boundary"]["memo_persistence"])
        self.assertFalse(summary["execution_boundary"]["preset_persistence"])
        self.assertFalse(summary["execution_boundary"]["live_approval"])
        written_row = fake_db.executemany_calls[0][1][0]
        self.assertEqual(written_row["source_type"], "computed_from_snapshots")
        self.assertEqual(written_row["coverage_status"], "partial")
        self.assertIsNone(written_row["inactive_detected_at"])

    def test_ingestion_job_wraps_computed_snapshot_summary(self) -> None:
        import app.jobs.ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_computed_snapshot_lifecycle",
            return_value={
                "requested": 2,
                "rows_written": 1,
                "requested_missing_symbols": ["MISS"],
                "target_table": "finance_meta.nyse_symbol_lifecycle",
                "execution_boundary": {"registry_write": False},
            },
        ):
            result = jobs.run_collect_computed_snapshot_lifecycle("SPY,MISS")

        self.assertEqual(result["job_name"], "collect_computed_snapshot_lifecycle")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 1)
        self.assertIn("MISS", result["failed_symbols"])

    def test_partial_computed_snapshot_row_does_not_pass_survivorship(self) -> None:
        from app.services.backtest_data_coverage_audit import (
            DATA_COVERAGE_REVIEW,
            build_data_coverage_audit,
        )

        audit = build_data_coverage_audit(
            {
                "data_coverage_context": {
                    "symbols": ["SPY"],
                    "symbol_weights": {"SPY": 100.0},
                    "requested_start": "2020-01-01",
                    "requested_end": "2020-12-31",
                    "price_window_rows": [
                        {
                            "symbol": "SPY",
                            "first_window_date": "2020-01-01",
                            "latest_window_date": "2020-12-31",
                            "window_row_count": 252,
                        }
                    ],
                    "asset_profile_rows": [{"symbol": "SPY", "status": "active"}],
                    "symbol_lifecycle_rows": [
                        {
                            "symbol": "SPY",
                            "listing_status": "active",
                            "source": "computed_snapshot_lifecycle",
                            "source_type": "computed_from_snapshots",
                            "coverage_status": "partial",
                            "first_seen_date": "2019-01-01",
                            "last_seen_date": "2021-12-31",
                            "event_type": "historical_membership",
                            "event_date": "2021-12-31",
                        }
                    ],
                },
                "provider_coverage_display_rows": [{"Diagnostic Status": "PASS", "Freshness": "fresh"}],
                "curve_evidence": {
                    "portfolio_curve_source": "actual_runtime_replay",
                    "curve_provenance": {
                        "runtime_recheck_status": "PASS",
                        "period_coverage_status": "PASS",
                        "runtime_recheck_mode": "latest_market_replay",
                    },
                    "period_coverage": {"status": "PASS"},
                },
            }
        )

        rows_by_criteria = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], DATA_COVERAGE_REVIEW)
        self.assertEqual(rows_by_criteria["Universe / listing evidence"]["Status"], "REVIEW")
        self.assertEqual(rows_by_criteria["Survivorship / delisting control"]["Status"], "REVIEW")
        self.assertIn("SPY", audit["metrics"]["lifecycle_partial_symbols"])
        self.assertEqual(audit["metrics"]["lifecycle_computed_partial_symbols"], ["SPY"])


class PracticalValidationDiagnosticsServiceContractTests(unittest.TestCase):
    def test_diagnostics_public_compatibility_contract_is_explicit(self) -> None:
        from app.services import backtest_practical_validation_curve_context as curve_context
        from app.services import backtest_practical_validation_diagnostics as diagnostics
        from app.services import backtest_practical_validation_source as source_builders

        self.assertEqual(
            diagnostics.__all__,
            [
                "VALIDATION_PROFILE_OPTIONS",
                "VALIDATION_PROFILE_QUESTIONS",
                "build_practical_validation_result",
                "build_selection_source_from_candidate_draft",
                "build_selection_source_from_saved_mix_prefill",
                "build_selection_source_from_weighted_mix_prefill",
                "build_validation_profile",
                "compact_benchmark_curve_snapshot_from_bundle",
                "compact_curve_snapshot_from_bundle",
                "source_components_dataframe",
            ],
        )
        self.assertIs(diagnostics.build_validation_profile, source_builders.build_validation_profile)
        self.assertIs(diagnostics.source_components_dataframe, source_builders.source_components_dataframe)
        self.assertIs(diagnostics.compact_curve_snapshot_from_bundle, curve_context.compact_curve_snapshot_from_bundle)

    def test_profile_builder_and_curve_snapshot_are_ui_neutral(self) -> None:
        from app.services import backtest_practical_validation_curve_context as curve_context
        from app.services import backtest_practical_validation_source as source_builders

        profile = source_builders.build_validation_profile(
            "custom",
            {
                "primary_goal": "defensive",
                "drawdown_tolerance": "dd_10",
                "holding_period": "6_to_12m",
                "complexity_allowance": "broad_etf_only",
                "alternative_success_metric": "lower_mdd",
            },
        )
        curve = curve_context.compact_curve_snapshot_from_bundle(
            {
                "result_df": pd.DataFrame(
                    [
                        {"Date": "2020-01-31", "Total Balance": 100.0},
                        {"Date": "2020-02-28", "Total Balance": 98.0},
                    ]
                )
            }
        )

        self.assertEqual(profile["profile_id"], "custom")
        self.assertEqual(profile["profile_label"], "사용자 지정")
        self.assertEqual(profile["answers"]["primary_goal"], "defensive")
        self.assertEqual(profile["answer_labels"]["drawdown_tolerance"], "-10% 내외")
        self.assertEqual(profile["thresholds"]["mdd_review_line"], -10.0)
        self.assertGreaterEqual(profile["domain_weights"]["stress_scenario_diagnostics"], 1.35)
        self.assertEqual([row["Date"] for row in curve], ["2020-01-31", "2020-02-28"])
        self.assertEqual([row["Total Balance"] for row in curve], [100.0, 98.0])
        self.assertAlmostEqual(curve[0]["Total Return"], 0.0)
        self.assertAlmostEqual(curve[1]["Total Return"], -0.02)

    def test_robustness_lab_board_keeps_compact_evidence_contract(self) -> None:
        from app.services.backtest_practical_validation_stress_sensitivity import build_robustness_lab_board

        board = build_robustness_lab_board(
            stress_interpretation={
                "status": "REVIEW",
                "summary": "1/2개 covered stress window만 계산됐습니다.",
                "covered_count": 2,
                "computed_count": 1,
                "uncomputed_count": 1,
                "worst_mdd": -0.25,
                "worst_mdd_scenario": "COVID crash",
                "worst_benchmark_spread": -0.04,
                "rows": [
                    {
                        "Check": "Stress coverage",
                        "Status": "REVIEW",
                        "Finding": "1/2 covered windows computed",
                        "Why It Matters": "stress coverage compact summary",
                        "Next Check": "daily replay",
                    }
                ],
            },
            sensitivity_interpretation={
                "status": "PASS",
                "summary": "2개 sensitivity 계산됨",
                "computed_count": 2,
                "review_count": 0,
                "runtime_followup_count": 1,
                "worst_scenario": "Mix weight +5%p: Core",
                "worst_cagr_delta": -0.01,
                "worst_mdd_delta": -0.02,
            },
            stress_rows=[
                {
                    "Scenario": "COVID crash",
                    "Result Status": "REVIEW",
                    "Window": "2020-02-19 -> 2020-03-23",
                    "Portfolio Return": -0.18,
                    "Portfolio MDD": -0.25,
                    "Benchmark Spread": -0.04,
                    "Expected Check": "return / MDD / benchmark spread",
                }
            ],
            sensitivity_rows=[
                {
                    "Scenario": "GTAA parameter perturbation",
                    "Scope": "interval / MA window",
                    "Result Status": "NOT_RUN",
                    "Expected Check": "cadence 민감도",
                }
            ],
            overfit_audit={"status": "PASS", "trial_count": 4, "interpretation": "trial count ok"},
            rolling_evidence={
                "status": "PASS",
                "summary": "12개월 rolling 계산됨",
                "metrics": {"window_count": 8, "worst_rolling_cagr": 0.01, "worst_rolling_mdd": -0.08},
            },
        )

        self.assertEqual(board["schema_version"], "robustness_lab_board_v1")
        self.assertEqual(board["status"], "REVIEW")
        self.assertEqual(board["metrics"]["computed_stress_windows"], 1)
        self.assertEqual(board["metrics"]["runtime_followup_count"], 1)
        self.assertEqual(len(board["summary_rows"]), 6)
        self.assertTrue(any(row["Check"] == "Local overfit audit" for row in board["summary_rows"]))
        self.assertTrue(any(row["Status"] == "NOT_RUN" for row in board["follow_up_rows"]))


class BoundaryContractHardeningTests(unittest.TestCase):
    def _load_boundary_checker(self):
        script_path = (
            Path(__file__).resolve().parents[1]
            / ".aiworkspace/plugins/quant-finance-workflow/scripts/check_ui_engine_boundary.py"
        )
        spec = importlib.util.spec_from_file_location("check_ui_engine_boundary", script_path)
        self.assertIsNotNone(spec)
        self.assertIsNotNone(spec.loader)
        module = importlib.util.module_from_spec(spec)
        spec.loader.exec_module(module)
        return module

    def test_app_web_import_is_hard_boundary_violation(self) -> None:
        checker = self._load_boundary_checker()

        with tempfile.TemporaryDirectory() as tmp_dir:
            candidate = Path(tmp_dir) / "bad_runtime.py"
            candidate.write_text(
                "from app.web.backtest_common import format_percent\n",
                encoding="utf-8",
            )

            with (
                patch.object(checker, "_boundary_files", return_value=[candidate]),
                patch.object(checker, "_relative", return_value="app/runtime/bad_runtime.py"),
            ):
                violations, advisories = checker._scan_boundary_files()

        self.assertEqual(advisories, [])
        self.assertEqual(len(violations), 1)
        self.assertEqual(violations[0]["kind"], "app_web_import")
        self.assertEqual(violations[0]["path"], "app/runtime/bad_runtime.py")


class FinanceWorkspacePathContractTests(unittest.TestCase):
    def test_runtime_and_job_paths_use_canonical_aiworkspace_note_root(self) -> None:
        from app.jobs.result_artifacts import RUN_ARTIFACT_DIR
        from app.jobs.run_history import HISTORY_FILE
        from app.runtime import (
            BACKTEST_HISTORY_FILE,
            CURRENT_CANDIDATE_REGISTRY_FILE,
            FINAL_SELECTION_DECISION_REGISTRY_FILE,
            PORTFOLIO_PROPOSAL_REGISTRY_FILE,
            SAVED_PORTFOLIO_FILE,
        )
        from app.workspace_paths import FINANCE_NOTE_DIR, PROJECT_ROOT, REGISTRIES_DIR, SAVED_DIR

        expected_note_dir = PROJECT_ROOT / ".aiworkspace" / "note" / "finance"
        self.assertEqual(FINANCE_NOTE_DIR, expected_note_dir)
        self.assertEqual(REGISTRIES_DIR, expected_note_dir / "registries")
        self.assertEqual(SAVED_DIR, expected_note_dir / "saved")

        runtime_paths = [
            CURRENT_CANDIDATE_REGISTRY_FILE,
            FINAL_SELECTION_DECISION_REGISTRY_FILE,
            PORTFOLIO_PROPOSAL_REGISTRY_FILE,
            SAVED_PORTFOLIO_FILE,
            BACKTEST_HISTORY_FILE,
            HISTORY_FILE,
            RUN_ARTIFACT_DIR,
        ]
        for path in runtime_paths:
            path_text = str(path)
            self.assertIn("/.aiworkspace/note/finance/", path_text)
            self.assertNotIn("/.note/finance/", path_text)


class JobResultArtifactContractTests(unittest.TestCase):
    def test_earnings_symbol_diagnostics_become_failure_rows(self) -> None:
        from app.jobs.result_artifacts import _extract_failure_rows

        rows = _extract_failure_rows(
            {
                "job_name": "collect_earnings_calendar",
                "status": "partial_success",
                "started_at": "2026-05-28 10:00:00",
                "finished_at": "2026-05-28 10:00:01",
                "failed_symbols": ["AAA", "BBB"],
                "message": "Earnings calendar completed with issues.",
                "details": {
                    "missing_symbols": ["AAA"],
                    "symbol_diagnostics": [
                        {
                            "symbol": "AAA",
                            "status": "missing",
                            "reason": "outside_window",
                            "detail": "Provider date was outside the selected window.",
                        },
                        {
                            "symbol": "BBB",
                            "status": "failed",
                            "reason": "provider_error",
                            "detail": "provider unavailable",
                        },
                    ]
                },
            }
        )

        self.assertEqual(
            [(row["symbol"], row["kind"], row["detail"]) for row in rows],
            [
                ("AAA", "earnings_missing", "outside_window"),
                ("BBB", "earnings_failed", "provider_error"),
            ],
        )


class OverviewAutomationContractTests(unittest.TestCase):
    def test_market_session_banner_reports_open_day_times(self) -> None:
        from app.web.overview_dashboard import US_EASTERN_TZ, _market_session_banner_model

        model = _market_session_banner_model(now=datetime(2026, 5, 29, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["status"], "장중")
        self.assertIn("2026-05-29 ET", model["title"])
        self.assertEqual(model["items"][0]["value"], "05-29 22:30 KST")
        self.assertEqual(model["items"][0]["detail"], "09:30 ET")
        self.assertEqual(model["items"][1]["value"], "05-30 05:00 KST")
        self.assertEqual(model["items"][1]["detail"], "16:00 ET")

    def test_market_session_banner_reports_weekend_closure(self) -> None:
        from app.web.overview_dashboard import US_EASTERN_TZ, _market_session_banner_model

        model = _market_session_banner_model(now=datetime(2026, 5, 30, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["status"], "휴장")
        self.assertIn("주말", model["detail"])
        self.assertEqual(model["items"][1]["value"], "06-01 22:30 KST")
        self.assertEqual(model["items"][1]["detail"], "09:30 ET")

    def test_market_session_banner_reports_observed_holiday_closure(self) -> None:
        from app.web.overview_dashboard import US_EASTERN_TZ, _market_session_banner_model

        model = _market_session_banner_model(now=datetime(2026, 7, 3, 10, 0, tzinfo=US_EASTERN_TZ))

        self.assertEqual(model["status"], "휴장")
        self.assertIn("Independence Day", model["detail"])

    def test_snapshot_status_labels_intraday_quote_time(self) -> None:
        from app.web.overview_dashboard import _snapshot_status_items

        items = _snapshot_status_items(
            {
                "status": "OK",
                "coverage": {
                    "price_mode": "Intraday Snapshot",
                    "snapshot_time_utc": "2026-05-29 21:32",
                    "returnable_count": 503,
                    "universe_count": 503,
                },
            }
        )

        self.assertEqual(items[0]["title"], "Effective Quote Time")
        self.assertEqual(items[0]["value"], "2026-05-29 21:32")
        self.assertIn("previous close", items[0]["detail"])

    def test_snapshot_status_labels_sparse_eod_date(self) -> None:
        from app.web.overview_dashboard import _snapshot_status_items

        items = _snapshot_status_items(
            {
                "status": "OK",
                "coverage": {
                    "price_mode": "EOD DB",
                    "latest_raw_date": "2026-05-28",
                    "effective_end_date": "2026-05-27",
                    "returnable_count": 500,
                    "universe_count": 503,
                },
            }
        )

        self.assertEqual(items[0]["title"], "Effective EOD Date")
        self.assertEqual(items[0]["value"], "2026-05-27")
        self.assertIn("latest raw 2026-05-28 is sparse", items[0]["detail"])

    def test_browser_auto_refresh_timing_shows_remaining_cadence(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_timing

        timing = _browser_auto_refresh_timing(
            {
                "status": "skipped",
                "plan": [
                    {
                        "label": "S&P 500 Daily Snapshot",
                        "reason": "cadence not due",
                        "cadence_minutes": 5,
                        "last_finished_at": "2026-05-29 10:00:00",
                        "next_due_at": "2026-05-29 10:05:00",
                    }
                ],
            },
            now=datetime(2026, 5, 29, 10, 2, 30),
        )

        self.assertEqual(timing["title"], "다음 갱신까지 2분 30초")
        self.assertEqual(timing["progress_pct"], 50)
        self.assertEqual(timing["next_due_at"], "2026-05-29 10:05:00")

    def test_browser_auto_refresh_timing_waits_outside_market_hours(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_timing

        timing = _browser_auto_refresh_timing(
            {
                "status": "skipped",
                "plan": [
                    {
                        "label": "S&P 500 Daily Snapshot",
                        "reason": "outside US market hours",
                        "cadence_minutes": 5,
                        "last_finished_at": "2026-05-29 10:00:00",
                        "next_due_at": "2026-05-29 10:05:00",
                    }
                ],
            },
            now=datetime(2026, 5, 29, 10, 2, 30),
        )

        self.assertEqual(timing["title"], "미국 정규장 대기")
        self.assertEqual(timing["progress_pct"], 0)

    def test_browser_auto_refresh_timing_rebases_success_to_next_cadence(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_timing

        timing = _browser_auto_refresh_timing(
            {
                "status": "success",
                "finished_at": "2026-05-29 10:03:00",
                "plan": [
                    {
                        "label": "S&P 500 Daily Snapshot",
                        "reason": "due",
                        "should_run": True,
                        "cadence_minutes": 5,
                        "last_finished_at": "2026-05-29 09:58:00",
                        "next_due_at": "2026-05-29 10:03:00",
                    }
                ],
            },
            now=datetime(2026, 5, 29, 10, 4, 0),
        )

        self.assertEqual(timing["title"], "방금 갱신됨. 다음 갱신까지 4분")
        self.assertEqual(timing["next_due_at"], "2026-05-29 10:08:00")
        self.assertEqual(timing["progress_pct"], 20)

    def test_browser_auto_refresh_check_due_uses_next_due(self) -> None:
        from app.web.overview_dashboard import _should_run_browser_auto_refresh_check

        summary = {
            "status": "skipped",
            "plan": [
                {
                    "label": "S&P 500 Daily Snapshot",
                    "reason": "cadence not due",
                    "cadence_minutes": 5,
                    "last_finished_at": "2026-05-29 10:00:00",
                    "next_due_at": "2026-05-29 10:05:00",
                }
            ],
        }

        self.assertFalse(
            _should_run_browser_auto_refresh_check(summary, now=datetime(2026, 5, 29, 10, 4, 59))
        )
        self.assertTrue(
            _should_run_browser_auto_refresh_check(summary, now=datetime(2026, 5, 29, 10, 5, 0))
        )

    def test_browser_auto_refresh_completion_label_uses_actionable_status(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_completion_label

        self.assertEqual(
            _browser_auto_refresh_completion_label({"status": "success"}),
            "S&P 500 스냅샷 갱신이 완료되었습니다.",
        )
        self.assertEqual(
            _browser_auto_refresh_completion_label(
                {
                    "status": "skipped",
                    "plan": [{"label": "S&P 500 Daily Snapshot", "reason": "outside US market hours"}],
                }
            ),
            "S&P 500 일중 스냅샷: 미국 정규장 시간이 아니라 수집하지 않았습니다.",
        )
        self.assertEqual(
            _browser_auto_refresh_completion_label({"status": "locked"}),
            "다른 Overview 갱신 작업이 이미 실행 중입니다.",
        )

    def test_browser_auto_refresh_job_config_tracks_selected_coverage(self) -> None:
        from app.web.overview_dashboard import _browser_auto_refresh_job_config

        self.assertEqual(
            _browser_auto_refresh_job_config("SP500"),
            {"profile": "browser_safe", "job_id": "sp500_intraday"},
        )
        self.assertEqual(
            _browser_auto_refresh_job_config("TOP1000"),
            {"profile": "intraday", "job_id": "top1000_intraday"},
        )
        self.assertEqual(
            _browser_auto_refresh_job_config("TOP2000"),
            {"profile": "intraday", "job_id": "top2000_intraday"},
        )

    def test_group_trend_heatmap_expands_for_many_selected_groups(self) -> None:
        from app.web.overview_dashboard import (
            GROUP_TREND_HEATMAP_ROW_HEIGHT,
            _build_group_leadership_trend_heatmap,
        )

        rows = pd.DataFrame(
            [
                {
                    "Date": "2026-05-27",
                    "Group": f"Sector {index}",
                    "Market Cap Weighted Return %": float(index),
                    "Symbols": 10,
                    "Top Symbol": "AAA",
                }
                for index in range(11)
            ]
        )

        chart_spec = _build_group_leadership_trend_heatmap(rows).to_dict()

        self.assertGreaterEqual(chart_spec["height"], GROUP_TREND_HEATMAP_ROW_HEIGHT * 11)

    def test_run_history_append_serializes_provider_date_payload(self) -> None:
        from app.jobs import run_history

        with tempfile.TemporaryDirectory() as tmp_dir:
            history_file = Path(tmp_dir) / "WEB_APP_RUN_HISTORY.jsonl"
            with patch.object(run_history, "HISTORY_FILE", history_file):
                run_history.append_run_history(
                    {
                        "job_name": "collect_earnings_calendar",
                        "status": "success",
                        "started_at": "2026-05-29 10:00:00",
                        "finished_at": "2026-05-29 10:00:02",
                        "duration_sec": 2.0,
                        "rows_written": 1,
                        "symbols_requested": 1,
                        "symbols_processed": 1,
                        "failed_symbols": [],
                        "message": "earnings calendar completed",
                        "details": {
                            "symbol_diagnostics": [
                                {
                                    "symbol": "AAA",
                                    "provider_dates": [date(2026, 7, 30)],
                                }
                            ]
                        },
                    }
                )
                loaded = run_history.load_run_history(limit=1)

        self.assertEqual(
            loaded[0]["details"]["symbol_diagnostics"][0]["provider_dates"],
            ["2026-07-30"],
        )

    def test_browser_safe_profile_only_selects_sp500_intraday_snapshot(self) -> None:
        from app.jobs.overview_automation import VALID_PROFILES, build_overview_automation_plan

        self.assertIn("browser_safe", VALID_PROFILES)

        plan = build_overview_automation_plan(
            profile="browser_safe",
            history_rows=[],
            now=datetime(2026, 5, 29, 15, 0, tzinfo=timezone.utc),
        )

        self.assertEqual([row["job_id"] for row in plan], ["sp500_intraday"])
        self.assertTrue(plan[0]["should_run"])
        self.assertEqual(plan[0]["cadence_minutes"], 5)
        self.assertTrue(plan[0]["market_hours_only"])

    def test_intraday_plan_skips_outside_market_hours_unless_allowed(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, build_overview_automation_plan

        spec = ScheduledJobSpec(
            job_id="fake_intraday",
            job_name="fake_intraday_job",
            label="Fake Intraday",
            cadence_minutes=5,
            profiles=("test",),
            market_hours_only=True,
            runner=lambda _: {},
            description="fake provider run",
        )
        outside_market_hours = datetime(2026, 5, 29, 23, 0, tzinfo=timezone.utc)

        plan = build_overview_automation_plan(
            profile="test",
            history_rows=[],
            now=outside_market_hours,
            specs=(spec,),
        )
        self.assertFalse(plan[0]["should_run"])
        self.assertEqual(plan[0]["reason"], "outside US market hours")

        allowed_plan = build_overview_automation_plan(
            profile="test",
            history_rows=[],
            now=outside_market_hours,
            allow_outside_market_hours=True,
            specs=(spec,),
        )
        self.assertTrue(allowed_plan[0]["should_run"])
        self.assertEqual(allowed_plan[0]["reason"], "due")

    def test_plan_uses_cadence_from_latest_accepted_history(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, build_overview_automation_plan

        spec = ScheduledJobSpec(
            job_id="fake_calendar",
            job_name="fake_calendar_job",
            label="Fake Calendar",
            cadence_minutes=60,
            profiles=("test",),
            market_hours_only=False,
            runner=lambda _: {},
            description="fake calendar run",
        )
        history_rows = [
            {
                "job_name": "fake_calendar_job",
                "status": "success",
                "finished_at": "2026-05-29 10:00:00",
            }
        ]

        early_plan = build_overview_automation_plan(
            profile="test",
            history_rows=history_rows,
            now=datetime(2026, 5, 29, 10, 30),
            specs=(spec,),
        )
        self.assertFalse(early_plan[0]["should_run"])
        self.assertEqual(early_plan[0]["reason"], "cadence not due")

        due_plan = build_overview_automation_plan(
            profile="test",
            history_rows=history_rows,
            now=datetime(2026, 5, 29, 11, 1),
            specs=(spec,),
        )
        self.assertTrue(due_plan[0]["should_run"])
        self.assertEqual(due_plan[0]["reason"], "due")

    def test_run_appends_scheduled_metadata_and_releases_lock(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, run_overview_automation

        calls: list[datetime] = []

        def fake_runner(value: datetime) -> dict:
            calls.append(value)
            return {
                "job_name": "fake_calendar_job",
                "status": "success",
                "started_at": "2026-05-29 10:00:00",
                "finished_at": "2026-05-29 10:00:01",
                "duration_sec": 1.0,
                "rows_written": 3,
                "symbols_requested": None,
                "symbols_processed": None,
                "failed_symbols": [],
                "message": "fake completed",
                "details": {"source": "fake"},
            }

        spec = ScheduledJobSpec(
            job_id="fake_calendar",
            job_name="fake_calendar_job",
            label="Fake Calendar",
            cadence_minutes=60,
            profiles=("test",),
            market_hours_only=False,
            runner=fake_runner,
            description="fake calendar run",
        )
        appended: list[dict] = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            lock_path = Path(tmp_dir) / "overview.lock"
            summary = run_overview_automation(
                profile="test",
                history_rows=[],
                history_appender=appended.append,
                lock_path=lock_path,
                now=datetime(2026, 5, 29, 10, 0),
                specs=(spec,),
            )
            self.assertFalse(lock_path.exists())

        self.assertEqual(summary["status"], "success")
        self.assertEqual(summary["jobs_run"], 1)
        self.assertEqual(len(calls), 1)
        self.assertEqual(len(appended), 1)
        metadata = appended[0]["run_metadata"]
        self.assertEqual(metadata["execution_mode"], "scheduled")
        self.assertEqual(metadata["automation_profile"], "test")
        self.assertEqual(metadata["automation_job_id"], "fake_calendar")
        self.assertEqual(appended[0]["details"]["automation"]["profile"], "test")
        self.assertEqual(appended[0]["details"]["automation"]["execution_mode"], "scheduled")

    def test_run_can_append_browser_auto_metadata(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, run_overview_automation

        def fake_runner(_: datetime) -> dict:
            return {
                "job_name": "fake_intraday_job",
                "status": "success",
                "started_at": "2026-05-29 10:00:00",
                "finished_at": "2026-05-29 10:00:02",
                "duration_sec": 2.0,
                "rows_written": 503,
                "symbols_requested": 503,
                "symbols_processed": 503,
                "failed_symbols": [],
                "message": "fake intraday completed",
                "details": {},
            }

        spec = ScheduledJobSpec(
            job_id="fake_intraday",
            job_name="fake_intraday_job",
            label="Fake Intraday",
            cadence_minutes=5,
            profiles=("browser_safe",),
            market_hours_only=False,
            runner=fake_runner,
            description="fake browser auto run",
        )
        appended: list[dict] = []

        with tempfile.TemporaryDirectory() as tmp_dir:
            summary = run_overview_automation(
                profile="browser_safe",
                execution_mode="browser_auto",
                history_rows=[],
                history_appender=appended.append,
                lock_path=Path(tmp_dir) / "overview.lock",
                now=datetime(2026, 5, 29, 10, 0),
                specs=(spec,),
            )

        self.assertEqual(summary["execution_mode"], "browser_auto")
        self.assertEqual(appended[0]["run_metadata"]["execution_mode"], "browser_auto")
        self.assertIn("Browser-session Overview automation", appended[0]["run_metadata"]["execution_context"])
        self.assertEqual(appended[0]["details"]["automation"]["execution_mode"], "browser_auto")

    def test_dry_run_does_not_call_runner_or_append_history(self) -> None:
        from app.jobs.overview_automation import ScheduledJobSpec, run_overview_automation

        def fake_runner(_: datetime) -> dict:
            raise AssertionError("dry-run should not execute the runner")

        spec = ScheduledJobSpec(
            job_id="fake_calendar",
            job_name="fake_calendar_job",
            label="Fake Calendar",
            cadence_minutes=60,
            profiles=("test",),
            market_hours_only=False,
            runner=fake_runner,
            description="fake calendar run",
        )
        appended: list[dict] = []

        summary = run_overview_automation(
            profile="test",
            dry_run=True,
            history_rows=[],
            history_appender=appended.append,
            now=datetime(2026, 5, 29, 10, 0),
            specs=(spec,),
        )

        self.assertEqual(summary["status"], "dry_run")
        self.assertEqual(summary["jobs_due"], 1)
        self.assertEqual(summary["jobs_run"], 0)
        self.assertEqual(appended, [])


class BacktestRuntimeContractTests(unittest.TestCase):
    def test_execution_preview_ignores_later_stage_probation_monitoring_fields(self) -> None:
        from app.runtime.backtest import _build_deployment_readiness_contract

        preview = _build_deployment_readiness_contract(
            {
                "benchmark_available": True,
                "benchmark_contract": "spy",
                "benchmark_label": "SPY Benchmark",
                "universe_contract": "historical_dynamic_pit",
                "price_freshness": {"status": "ok"},
                "benchmark_policy_status": "normal",
                "liquidity_policy_status": "normal",
                "validation_policy_status": "normal",
                "guardrail_policy_status": "normal",
                "etf_operability_status": "normal",
                "rolling_review_status": "normal",
                "out_of_sample_review_status": "normal",
                # Legacy later-stage fields can remain in metadata, but Execution Preview must not score them.
                "shortlist_status": "hold",
                "probation_status": "not_ready",
                "monitoring_status": "blocked",
            }
        )

        check_names = {row["Check"] for row in preview["deployment_checklist_rows"]}
        self.assertNotIn("Shortlist", check_names)
        self.assertNotIn("Probation", check_names)
        self.assertNotIn("Monitoring", check_names)
        self.assertEqual(preview["deployment_readiness_status"], "small_capital_ready")
        self.assertEqual(preview["deployment_check_fail_count"], 0)

    def test_candidate_readiness_scores_source_checks_not_legacy_deployment_status(self) -> None:
        from app.web.backtest_result_display import _build_next_step_readiness_evaluation

        evaluation = _build_next_step_readiness_evaluation(
            {
                "promotion_decision": "real_money_candidate",
                "deployment_readiness_status": "blocked",
                "benchmark_available": True,
                "validation_status": "normal",
                "benchmark_policy_status": "normal",
                "liquidity_policy_status": "normal",
                "validation_policy_status": "normal",
                "guardrail_policy_status": "normal",
                "etf_operability_status": "normal",
                "price_freshness": {"status": "ok"},
                "rolling_review_status": "caution",
                "out_of_sample_review_status": "caution",
                "transaction_cost_bps": 10.0,
                "turnover_estimation_status": "not_estimated_missing_holdings",
                "net_cost_curve_status": "applied_without_turnover_estimate",
            }
        )

        self.assertTrue(evaluation["can_move_to_compare"])
        self.assertEqual(evaluation["blocking_reasons"], [])
        self.assertEqual(evaluation["score"], 8.0)
        self.assertIn("Rolling Review: caution", evaluation["review_reasons"])
        self.assertIn("Split-Period Check: caution", evaluation["review_reasons"])
        self.assertIn("Turnover Estimate: not_estimated_missing_holdings", evaluation["review_reasons"])
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Execution Source Checks"]["현재 값"], "block 0 / review 2")
        self.assertEqual(criteria["Validation Source Checks"]["현재 값"], "block 0 / review 2")

    def test_practical_validation_handoff_gate_blocks_hold_candidates(self) -> None:
        from app.web.backtest_result_display import _build_practical_validation_handoff_state

        state = _build_practical_validation_handoff_state(
            {
                "meta": {
                    "promotion_decision": "hold",
                    "benchmark_available": True,
                    "validation_status": "normal",
                    "benchmark_policy_status": "normal",
                    "liquidity_policy_status": "normal",
                    "validation_policy_status": "normal",
                    "guardrail_policy_status": "normal",
                    "etf_operability_status": "normal",
                    "price_freshness": {"status": "ok"},
                }
            }
        )

        self.assertFalse(state["can_submit"])
        self.assertEqual(state["status_label"], "진입 보류")
        self.assertIn("Promotion Decision이 hold이거나 비어 있음", state["display_reasons"])
        criteria = {row["label"]: row for row in state["criteria"]}
        self.assertEqual(criteria["Promotion"]["value"], "보류")

    def test_practical_validation_handoff_gate_allows_ready_candidates(self) -> None:
        from app.web.backtest_result_display import _build_practical_validation_handoff_state

        state = _build_practical_validation_handoff_state(
            {
                "meta": {
                    "promotion_decision": "real_money_candidate",
                    "benchmark_available": True,
                    "validation_status": "normal",
                    "benchmark_policy_status": "normal",
                    "liquidity_policy_status": "normal",
                    "validation_policy_status": "normal",
                    "guardrail_policy_status": "normal",
                    "etf_operability_status": "normal",
                    "price_freshness": {"status": "ok"},
                }
            }
        )

        self.assertTrue(state["can_submit"])
        self.assertEqual(state["status_label"], "진입 가능")
        self.assertEqual(state["display_reasons"], ["막는 항목 없음"])
        criteria = {row["label"]: row for row in state["criteria"]}
        self.assertEqual(criteria["실행 원천"]["value"], "통과")
        self.assertEqual(criteria["검증 원천"]["value"], "통과")

    def test_portfolio_mix_candidate_gate_allows_ready_mix(self) -> None:
        from app.web.backtest_compare import _build_weighted_mix_candidate_readiness_evaluation

        def _bundle(strategy_name: str) -> dict:
            return {
                "strategy_name": strategy_name,
                "summary_df": pd.DataFrame([{"End Balance": 110.0}]),
                "result_df": pd.DataFrame(
                    [
                        {"Date": "2024-12-31", "Total Balance": 100.0},
                        {"Date": "2025-12-31", "Total Balance": 110.0},
                    ]
                ),
                "meta": {
                    "strategy_name": strategy_name,
                    "end": "2025-12-31",
                    "promotion_decision": "real_money_candidate",
                    "benchmark_available": True,
                    "validation_status": "normal",
                    "benchmark_policy_status": "normal",
                    "liquidity_policy_status": "normal",
                    "validation_policy_status": "normal",
                    "guardrail_policy_status": "normal",
                    "etf_operability_status": "normal",
                    "price_freshness": {"status": "ok"},
                },
            }

        weighted_bundle = {
            "summary_df": pd.DataFrame([{"End Balance": 112.0}]),
            "result_df": pd.DataFrame(
                [
                    {"Date": "2024-12-31", "Total Balance": 100.0},
                    {"Date": "2025-12-31", "Total Balance": 112.0},
                ]
            ),
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [70.0, 30.0],
            "component_data_trust_rows": [
                {"Strategy": "GTAA", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
                {"Strategy": "Equal Weight", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
            ],
            "date_policy": "intersection",
        }

        evaluation = _build_weighted_mix_candidate_readiness_evaluation(
            weighted_bundle,
            [_bundle("GTAA"), _bundle("Equal Weight")],
        )

        self.assertTrue(evaluation["can_send_to_practical_validation"])
        self.assertEqual(evaluation["stage_status"], "PASS")
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Weight Discipline"]["상태"], "PASS")
        self.assertEqual(criteria["Component 1차 후보 판단"]["상태"], "PASS")

    def test_portfolio_mix_candidate_gate_blocks_hold_component(self) -> None:
        from app.web.backtest_compare import _build_weighted_mix_candidate_readiness_evaluation

        ready_meta = {
            "end": "2025-12-31",
            "promotion_decision": "real_money_candidate",
            "benchmark_available": True,
            "validation_status": "normal",
            "benchmark_policy_status": "normal",
            "liquidity_policy_status": "normal",
            "validation_policy_status": "normal",
            "guardrail_policy_status": "normal",
            "etf_operability_status": "normal",
            "price_freshness": {"status": "ok"},
        }
        result_df = pd.DataFrame(
            [
                {"Date": "2024-12-31", "Total Balance": 100.0},
                {"Date": "2025-12-31", "Total Balance": 110.0},
            ]
        )
        bundles = [
            {"strategy_name": "GTAA", "summary_df": pd.DataFrame([{"End Balance": 110.0}]), "result_df": result_df, "meta": dict(ready_meta)},
            {
                "strategy_name": "Equal Weight",
                "summary_df": pd.DataFrame([{"End Balance": 108.0}]),
                "result_df": result_df,
                "meta": {**ready_meta, "promotion_decision": "hold"},
            },
        ]
        weighted_bundle = {
            "summary_df": pd.DataFrame([{"End Balance": 112.0}]),
            "result_df": result_df,
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [50.0, 50.0],
            "component_data_trust_rows": [
                {"Strategy": "GTAA", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
                {"Strategy": "Equal Weight", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
            ],
            "date_policy": "intersection",
        }

        evaluation = _build_weighted_mix_candidate_readiness_evaluation(weighted_bundle, bundles)

        self.assertFalse(evaluation["can_send_to_practical_validation"])
        self.assertEqual(evaluation["stage_status"], "HOLD")
        self.assertTrue(any("Promotion Decision" in reason for reason in evaluation["blocking_reasons"]))
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Component 1차 후보 판단"]["상태"], "FAIL")

    def test_portfolio_mix_candidate_gate_blocks_non_100_weight_total(self) -> None:
        from app.web.backtest_compare import _build_weighted_mix_candidate_readiness_evaluation

        meta = {
            "end": "2025-12-31",
            "promotion_decision": "real_money_candidate",
            "benchmark_available": True,
            "validation_status": "normal",
            "benchmark_policy_status": "normal",
            "liquidity_policy_status": "normal",
            "validation_policy_status": "normal",
            "guardrail_policy_status": "normal",
            "etf_operability_status": "normal",
            "price_freshness": {"status": "ok"},
        }
        result_df = pd.DataFrame(
            [
                {"Date": "2024-12-31", "Total Balance": 100.0},
                {"Date": "2025-12-31", "Total Balance": 110.0},
            ]
        )
        bundles = [
            {"strategy_name": "GTAA", "summary_df": pd.DataFrame([{"End Balance": 110.0}]), "result_df": result_df, "meta": meta},
            {"strategy_name": "Equal Weight", "summary_df": pd.DataFrame([{"End Balance": 108.0}]), "result_df": result_df, "meta": meta},
        ]
        weighted_bundle = {
            "summary_df": pd.DataFrame([{"End Balance": 112.0}]),
            "result_df": result_df,
            "component_strategy_names": ["GTAA", "Equal Weight"],
            "component_input_weights": [70.0, 20.0],
            "component_data_trust_rows": [
                {"Strategy": "GTAA", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
                {"Strategy": "Equal Weight", "Price Freshness": "ok", "Interpretation": "눈에 띄는 데이터 이슈 없음"},
            ],
            "date_policy": "intersection",
        }

        evaluation = _build_weighted_mix_candidate_readiness_evaluation(weighted_bundle, bundles)

        self.assertFalse(evaluation["can_send_to_practical_validation"])
        criteria = {row["기준"]: row for row in evaluation["criteria_rows"]}
        self.assertEqual(criteria["Weight Discipline"]["상태"], "FAIL")
        self.assertIn("target weight 합계가 100%가 아님", criteria["Weight Discipline"]["판단"])

    def test_result_bundle_public_compatibility_contract_is_preserved(self) -> None:
        import app.runtime
        from app.runtime import backtest as runtime_backtest
        from app.runtime import backtest_result_bundle

        self.assertIs(
            runtime_backtest.build_backtest_result_bundle,
            backtest_result_bundle.build_backtest_result_bundle,
        )
        self.assertIs(
            app.runtime.build_backtest_result_bundle,
            backtest_result_bundle.build_backtest_result_bundle,
        )

    def test_result_bundle_contract_sorts_dates_and_keeps_metadata(self) -> None:
        from app.runtime.backtest_result_bundle import build_backtest_result_bundle

        bundle = build_backtest_result_bundle(
            pd.DataFrame(
                [
                    {"Date": "2020-02-29", "Total Balance": 102.0, "Total Return": 0.02},
                    {"Date": "2020-01-31", "Total Balance": 100.0, "Total Return": 0.0},
                ]
            ),
            strategy_name="Global Relative Strength",
            strategy_key="global_relative_strength",
            input_params={
                "tickers": ["SPY", "TLT"],
                "start": "2020-01-01",
                "end": "2020-02-29",
                "timeframe": "1d",
                "option": "month_end",
                "rebalance_interval": 1,
                "score_lookback_months": [3, 6, 12],
            },
            warnings=["price freshness warning"],
        )

        self.assertEqual(bundle["strategy_name"], "Global Relative Strength")
        self.assertEqual(
            [date.strftime("%Y-%m-%d") for date in bundle["result_df"]["Date"]],
            ["2020-01-31", "2020-02-29"],
        )
        self.assertEqual(
            [date.strftime("%Y-%m-%d") for date in bundle["chart_df"]["Date"]],
            ["2020-01-31", "2020-02-29"],
        )
        self.assertEqual(bundle["meta"]["strategy_family"], "Global Relative Strength")
        self.assertEqual(bundle["meta"]["result_rows"], 2)
        self.assertEqual(bundle["meta"]["actual_result_start"], "2020-01-31")
        self.assertEqual(bundle["meta"]["actual_result_end"], "2020-02-29")
        self.assertEqual(bundle["meta"]["tickers"], ["SPY", "TLT"])
        self.assertEqual(bundle["meta"]["warnings"], ["price freshness warning"])
        self.assertEqual(bundle["meta"]["score_lookback_months"], [3, 6, 12])
        self.assertFalse(bundle["summary_df"].empty)

    def test_dynamic_etf_execution_dispatch_adds_promotion_policy_defaults(self) -> None:
        from app.runtime.backtest import (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )
        from app.services.backtest_execution import execute_single_backtest

        payload = {
            "strategy_key": "global_relative_strength",
            "tickers": ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"],
            "cash_ticker": "BIL",
            "start": "2016-01-29",
            "end": "2026-05-29",
            "timeframe": "1d",
            "option": "month_end",
            "top": 2,
            "interval": 1,
            "universe_mode": "manual_tickers",
            "preset_name": "GRS Liquid Macro Top2",
        }

        with patch(
            "app.services.backtest_execution.run_global_relative_strength_backtest_from_db",
            return_value={"strategy_name": "Global Relative Strength", "meta": {}},
        ) as runner:
            result = execute_single_backtest(payload, strategy_name="Global Relative Strength")

        self.assertTrue(result.ok, result.error_message)
        kwargs = runner.call_args.kwargs
        self.assertEqual(kwargs["promotion_min_benchmark_coverage"], STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE)
        self.assertEqual(kwargs["promotion_min_net_cagr_spread"], STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD)
        self.assertEqual(
            kwargs["promotion_min_liquidity_clean_coverage"],
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        )
        self.assertEqual(
            kwargs["promotion_max_underperformance_share"],
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        )
        self.assertEqual(
            kwargs["promotion_min_worst_rolling_excess_return"],
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )
        self.assertEqual(kwargs["promotion_max_strategy_drawdown"], STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN)
        self.assertEqual(
            kwargs["promotion_max_drawdown_gap_vs_benchmark"],
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        )

    def test_global_relative_strength_source_contract_includes_promotion_policy_defaults(self) -> None:
        from app.runtime import backtest as runtime_backtest
        from app.runtime.backtest import (
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
            STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN,
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
            STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )

        result_df = pd.DataFrame(
            [
                {"Date": "2020-01-31", "Total Balance": 100.0, "Total Return": 0.0},
                {"Date": "2020-02-29", "Total Balance": 103.0, "Total Return": 0.03},
                {"Date": "2020-03-31", "Total Balance": 107.0, "Total Return": 0.07},
            ]
        )
        result_df.attrs["effective_tickers"] = ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"]
        result_df.attrs["requested_tickers"] = ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"]
        captured_hardening_kwargs: dict[str, object] = {}

        def _capture_hardening(bundle: dict[str, object], **kwargs: object) -> dict[str, object]:
            captured_hardening_kwargs.update(kwargs)
            return bundle

        with (
            patch.object(
                runtime_backtest,
                "inspect_strict_annual_price_freshness",
                return_value={"status": "ok", "message": "", "details": {}},
            ),
            patch.object(runtime_backtest, "_preflight_price_strategy_data"),
            patch.object(runtime_backtest, "get_global_relative_strength_from_db", return_value=result_df),
            patch.object(runtime_backtest, "_apply_real_money_hardening", side_effect=_capture_hardening),
        ):
            bundle = runtime_backtest.run_global_relative_strength_backtest_from_db(
                tickers=["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"],
                cash_ticker="BIL",
                start="2020-01-31",
                end="2020-03-31",
                timeframe="1d",
                option="month_end",
                top=2,
                interval=1,
                benchmark_ticker="AOR",
                universe_mode="manual_tickers",
                preset_name="GRS Liquid Macro Top2",
            )

        meta = bundle["meta"]
        self.assertEqual(meta["promotion_min_benchmark_coverage"], STRICT_PROMOTION_DEFAULT_MIN_BENCHMARK_COVERAGE)
        self.assertEqual(meta["promotion_min_net_cagr_spread"], STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD)
        self.assertEqual(
            meta["promotion_min_liquidity_clean_coverage"],
            STRICT_PROMOTION_DEFAULT_MIN_LIQUIDITY_CLEAN_COVERAGE,
        )
        self.assertEqual(
            meta["promotion_max_underperformance_share"],
            STRICT_PROMOTION_DEFAULT_MAX_UNDERPERFORMANCE_SHARE,
        )
        self.assertEqual(
            meta["promotion_min_worst_rolling_excess_return"],
            STRICT_PROMOTION_DEFAULT_MIN_WORST_ROLLING_EXCESS_RETURN,
        )
        self.assertEqual(meta["promotion_max_strategy_drawdown"], STRICT_PROMOTION_DEFAULT_MAX_STRATEGY_DRAWDOWN)
        self.assertEqual(
            meta["promotion_max_drawdown_gap_vs_benchmark"],
            STRICT_PROMOTION_DEFAULT_MAX_DRAWDOWN_GAP_VS_BENCHMARK,
        )
        self.assertEqual(
            captured_hardening_kwargs["promotion_min_net_cagr_spread"],
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        )

    def test_dynamic_etf_compare_override_preserves_promotion_policy_defaults(self) -> None:
        from app.runtime.backtest import STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD
        from app.web.backtest_compare import _bundle_to_saved_strategy_override

        override = _bundle_to_saved_strategy_override(
            {
                "strategy_name": "Global Relative Strength",
                "meta": {
                    "tickers": ["SPY", "QQQ", "GLD", "IEF", "TLT", "BIL"],
                    "cash_ticker": "BIL",
                    "top": 2,
                    "rebalance_interval": 1,
                    "benchmark_ticker": "AOR",
                },
            }
        )

        self.assertEqual(
            override["promotion_min_net_cagr_spread"],
            STRICT_PROMOTION_DEFAULT_MIN_NET_CAGR_SPREAD,
        )
        self.assertIn("promotion_min_benchmark_coverage", override)
        self.assertIn("promotion_min_liquidity_clean_coverage", override)
        self.assertIn("promotion_max_drawdown_gap_vs_benchmark", override)

    def test_result_bundle_rejects_missing_required_columns(self) -> None:
        from app.runtime.backtest_result_bundle import build_backtest_result_bundle

        with self.assertRaisesRegex(ValueError, "missing required columns"):
            build_backtest_result_bundle(
                pd.DataFrame([{"Date": "2020-01-31", "Total Balance": 100.0}]),
                strategy_name="Equal Weight",
                strategy_key="equal_weight",
                input_params={},
            )


class OverviewMarketIntelligenceServiceContractTests(unittest.TestCase):
    def _query_fn(self, db_name: str, sql: str, params=None) -> list[dict[str, object]]:
        del db_name
        if "FROM market_event_calendar" in sql:
            rows = [
                {
                    "event_date": "2026-06-17",
                    "event_type": "FOMC_MEETING",
                    "symbol": None,
                    "title": "FOMC Meeting: June 16-17*, 2026",
                    "source": "federal_reserve_fomc_calendar",
                    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                    "confidence": 1.0,
                    "collected_at": "2026-05-28 02:00:00",
                },
                {
                    "event_date": "2026-07-29",
                    "event_type": "FOMC_MEETING",
                    "symbol": None,
                    "title": "FOMC Meeting: July 28-29, 2026",
                    "source": "federal_reserve_fomc_calendar",
                    "source_url": "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
                    "confidence": 1.0,
                    "collected_at": "2026-05-28 02:00:00",
                },
                {
                    "event_date": "2026-07-30",
                    "event_type": "EARNINGS",
                    "symbol": "MSFT",
                    "title": "MSFT Earnings Release",
                    "source": "yfinance_calendar",
                    "source_url": "https://finance.yahoo.com/quote/MSFT/analysis",
                    "confidence": 0.65,
                    "collected_at": "2026-05-28 03:00:00",
                },
            ]
            event_filter = None
            for value in params or []:
                if value in {"FOMC_MEETING", "EARNINGS"}:
                    event_filter = value
                    break
            if event_filter:
                return [row for row in rows if row["event_type"] == event_filter]
            return rows
        if "FROM market_universe_member" in sql:
            return [
                {
                    "symbol": "AAA",
                    "long_name": "AAA Corp",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 100,
                    "status": "active",
                    "error_msg": None,
                    "last_collected_at": "2026-05-18 10:00:00",
                    "universe_as_of_date": "2026-05-28",
                    "universe_collected_at": "2026-05-28 11:00:00",
                    "universe_source": "wikipedia_sp500_constituents",
                    "universe_source_url": "https://example.test/sp500",
                },
                {
                    "symbol": "BBB",
                    "long_name": "BBB Corp",
                    "sector": "Healthcare",
                    "industry": "Medical Devices",
                    "market_cap": 200,
                    "status": "active",
                    "error_msg": None,
                    "last_collected_at": "2026-05-18 10:00:00",
                    "universe_as_of_date": "2026-05-28",
                    "universe_collected_at": "2026-05-28 11:00:00",
                    "universe_source": "wikipedia_sp500_constituents",
                    "universe_source_url": "https://example.test/sp500",
                },
            ]
        if "MAX(snapshot_time_utc) AS snapshot_time_utc" in sql:
            return [{"snapshot_time_utc": "2026-05-18 15:35:00"}]
        if "FROM market_intraday_snapshot s" in sql:
            return [
                {
                    "symbol": "AAA",
                    "interval_code": "5m",
                    "snapshot_time_utc": "2026-05-18 15:35:00",
                    "quote_time_utc": "2026-05-18 15:30:00",
                    "previous_close": 100.0,
                    "latest_price": 112.0,
                    "return_pct": 12.0,
                    "volume": 1000,
                    "provider_status": "ok",
                    "error_msg": None,
                    "source": "yfinance",
                    "source_ref": "test",
                },
                {
                    "symbol": "BBB",
                    "interval_code": "5m",
                    "snapshot_time_utc": "2026-05-18 15:35:00",
                    "quote_time_utc": None,
                    "previous_close": None,
                    "latest_price": None,
                    "return_pct": None,
                    "volume": None,
                    "provider_status": "missing",
                    "error_msg": "missing latest price",
                    "source": "yfinance",
                    "source_ref": "test",
                },
            ]
        if "MAX(`date`) AS latest_raw_date" in sql:
            return [{"latest_raw_date": "2026-05-19"}]
        if "MAX(`date`) AS latest_price_date" in sql:
            return [
                {"symbol": "AAA", "latest_price_date": "2026-05-18"},
                {"symbol": "BBB", "latest_price_date": "2026-05-18"},
                {"symbol": "CCC", "latest_price_date": "2026-05-18"},
                {"symbol": "DDD", "latest_price_date": "2026-05-18"},
            ]
        if "GROUP BY `date`" in sql:
            dates = [
                "2026-05-18",
                "2026-05-15",
                "2026-05-14",
                "2026-05-13",
                "2026-05-12",
                "2026-05-11",
                "2026-05-08",
                "2026-05-07",
                "2026-05-06",
                "2026-05-05",
                "2026-05-04",
                "2026-05-01",
                "2026-04-30",
                "2026-04-29",
                "2026-04-28",
                "2026-04-27",
                "2026-04-24",
                "2026-04-23",
                "2026-04-22",
                "2026-04-21",
                "2026-04-20",
                "2026-04-17",
            ]
            return [{"date": item, "usable_rows": 1200} for item in dates]
        if "SUM(CASE WHEN volume IS NOT NULL THEN volume ELSE 0 END) AS total_volume" in sql:
            return [
                {
                    "symbol": "AAA",
                    "total_volume": 5_000,
                    "avg_daily_volume": 1_000,
                    "total_dollar_volume": 650_000.0,
                    "avg_daily_dollar_volume": 130_000.0,
                    "volume_days": 5,
                },
                {
                    "symbol": "BBB",
                    "total_volume": 7_500,
                    "avg_daily_volume": 1_500,
                    "total_dollar_volume": 900_000.0,
                    "avg_daily_dollar_volume": 180_000.0,
                    "volume_days": 5,
                },
                {
                    "symbol": "CCC",
                    "total_volume": 12_500,
                    "avg_daily_volume": 2_500,
                    "total_dollar_volume": 2_500_000.0,
                    "avg_daily_dollar_volume": 500_000.0,
                    "volume_days": 5,
                },
            ]
        if "FROM nyse_asset_profile" in sql:
            return [
                {
                    "symbol": "AAA",
                    "long_name": "AAA Corp",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 100,
                },
                {
                    "symbol": "BBB",
                    "long_name": "BBB Corp",
                    "sector": "Technology",
                    "industry": "Software",
                    "market_cap": 300,
                },
                {
                    "symbol": "CCC",
                    "long_name": "CCC Corp",
                    "sector": "Healthcare",
                    "industry": "Medical Devices",
                    "market_cap": 200,
                },
                {
                    "symbol": "DDD",
                    "long_name": "DDD Corp",
                    "sector": "Energy",
                    "industry": "Oil & Gas",
                    "market_cap": 100,
                },
            ]
        if "COALESCE(adj_close, close) AS price" in sql:
            return [
                {"symbol": "AAA", "date": "2026-05-11", "price": 100.0, "volume": 700},
                {"symbol": "AAA", "date": "2026-05-14", "price": 95.0, "volume": 900},
                {"symbol": "AAA", "date": "2026-05-15", "price": 100.0, "volume": 1000},
                {"symbol": "AAA", "date": "2026-05-18", "price": 110.0, "volume": 1500},
                {"symbol": "AAA", "date": "2026-04-17", "price": 100.0, "volume": 800},
                {"symbol": "BBB", "date": "2026-05-11", "price": 100.0, "volume": 1800},
                {"symbol": "BBB", "date": "2026-05-14", "price": 90.0, "volume": 1800},
                {"symbol": "BBB", "date": "2026-05-15", "price": 100.0, "volume": 2000},
                {"symbol": "BBB", "date": "2026-05-18", "price": 130.0, "volume": 2500},
                {"symbol": "BBB", "date": "2026-04-17", "price": 100.0, "volume": 1900},
                {"symbol": "CCC", "date": "2026-05-11", "price": 100.0, "volume": 1200},
                {"symbol": "CCC", "date": "2026-05-14", "price": 100.0, "volume": 1200},
                {"symbol": "CCC", "date": "2026-05-15", "price": 100.0, "volume": 1000},
                {"symbol": "CCC", "date": "2026-05-18", "price": 120.0, "volume": 1700},
                {"symbol": "CCC", "date": "2026-04-17", "price": 100.0, "volume": 1100},
                {"symbol": "DDD", "date": "2026-05-18", "price": 140.0, "volume": 900},
            ]
        return []

    def test_effective_market_date_skips_sparse_latest_raw_date(self) -> None:
        from app.services.overview_market_intelligence import resolve_effective_market_dates

        window = resolve_effective_market_dates(
            period="daily",
            min_price_rows=1000,
            today=date(2026, 5, 28),
            query_fn=self._query_fn,
        )

        self.assertEqual(window["status"], "OK")
        self.assertEqual(window["latest_raw_date"], "2026-05-19")
        self.assertEqual(window["effective_end_date"], "2026-05-18")
        self.assertEqual(window["start_date"], "2026-05-15")
        self.assertEqual(window["stale_days"], 10)

    def test_group_trend_window_contract_uses_compact_horizons(self) -> None:
        from app.services.overview_market_intelligence import resolve_group_trend_market_dates

        market_dates = [
            item.strftime("%Y-%m-%d")
            for item in reversed(pd.bdate_range(end="2026-05-29", periods=320).tolist())
        ]

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "MAX(`date`) AS latest_raw_date" in sql:
                return [{"latest_raw_date": market_dates[0]}]
            if "GROUP BY `date`" in sql:
                return [{"date": item, "usable_rows": 1200} for item in market_dates]
            return []

        daily = resolve_group_trend_market_dates(period="daily", query_fn=query_fn)
        weekly = resolve_group_trend_market_dates(period="weekly", query_fn=query_fn)
        monthly = resolve_group_trend_market_dates(period="monthly", query_fn=query_fn)

        self.assertEqual(daily["trend_window_label"], "Last 1M")
        self.assertEqual(len(daily["windows"]), 21)
        self.assertEqual(weekly["trend_window_label"], "Last 3M")
        self.assertEqual(len(weekly["windows"]), 13)
        self.assertEqual(monthly["trend_window_label"], "Last 12M")
        self.assertEqual(len(monthly["windows"]), 12)

    def test_market_movers_snapshot_ranks_returnable_symbols_and_reports_gaps(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_limit=100,
            period="daily",
            top_n=5,
            today=date(2026, 5, 28),
            prefer_intraday=False,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["universe_count"], 4)
        self.assertEqual(snapshot["coverage"]["returnable_count"], 3)
        self.assertEqual(snapshot["coverage"]["missing_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 30.0)
        self.assertIn("Latest raw price date is sparse", snapshot["warnings"][0])
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "DDD")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing start price")
        self.assertEqual(snapshot["rows"].iloc[0]["Volume"], 2500)
        self.assertEqual(snapshot["rows"].iloc[0]["Dollar Volume"], 325000.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Previous Return %"], 11.11)
        self.assertEqual(snapshot["rows"].iloc[0]["Momentum Delta pp"], 18.89)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Basis"], "Daily dollar volume")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume"], 2500)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Dollar Volume"], 325000.0)
        self.assertEqual(
            snapshot["missing_rows"].iloc[0]["Recommended Action"],
            "Refresh daily OHLCV history or inspect previous-close coverage.",
        )

    def test_market_movers_snapshot_uses_sp500_intraday_previous_close_returns(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_code="SP500",
            period="daily",
            top_n=5,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "SP500")
        self.assertEqual(snapshot["coverage"]["price_mode"], "Intraday Snapshot")
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Current S&P 500 constituents")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 1)
        self.assertEqual(snapshot["coverage"]["failed_count"], 1)
        self.assertEqual(snapshot["coverage"]["returnable_pct"], 50.0)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["status"], "stale")
        self.assertTrue(snapshot["coverage"]["refresh_state"]["refresh_due"])
        self.assertEqual(snapshot["coverage"]["refresh_state"]["check_interval_minutes"], 5)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["stale_after_minutes"], 15)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["next_due_in_minutes"], 0)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 12.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Volume"], 1000)
        self.assertEqual(snapshot["rows"].iloc[0]["Dollar Volume"], 112000.0)
        self.assertEqual(snapshot["rows"].iloc[0]["Previous Return %"], 5.26)
        self.assertEqual(snapshot["rows"].iloc[0]["Momentum Delta pp"], 6.74)
        self.assertEqual(snapshot["rows"].iloc[0]["Start Date"], "Previous Close")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Basis"], "Daily dollar volume")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Metric"], 112000.0)
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing latest price")
        self.assertEqual(
            snapshot["missing_rows"].iloc[0]["Recommended Action"],
            "Refresh the daily snapshot; if it persists, inspect provider quote coverage.",
        )

    def test_market_movers_snapshot_uses_top1000_intraday_returns(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            period="daily",
            top_n=5,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "TOP1000")
        self.assertEqual(snapshot["coverage"]["price_mode"], "Intraday Snapshot")
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Latest asset_profile.market_cap snapshot")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 1)
        self.assertEqual(snapshot["coverage"]["returnable_pct"], 25.0)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["universe_count"], 4)
        self.assertEqual(snapshot["coverage"]["refresh_state"]["returnable_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 12.0)
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["missing_rows"].iloc[0]["Reason"], "missing latest price")

    def test_market_movers_weekly_volume_rows_use_average_and_total_volume(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            period="weekly",
            top_n=5,
            today=date(2026, 5, 28),
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["rows"].iloc[0]["Return %"], 30.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Symbol"], "CCC")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Basis"], "Avg daily dollar volume")
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Metric"], 500000.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Avg Daily Volume"], 2500)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Total Volume"], 12500)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Avg Daily Dollar Volume"], 500000.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Total Dollar Volume"], 2500000.0)
        self.assertEqual(snapshot["volume_rows"].iloc[0]["Volume Days"], 5)

    def test_market_movers_snapshot_falls_back_to_listing_names(self) -> None:
        from app.services.overview_market_intelligence import build_market_movers_snapshot

        observed_sql: dict[str, str] = {}

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            if "FROM nyse_asset_profile p" in sql:
                observed_sql["universe"] = sql
                return [
                    {
                        "symbol": "AAA",
                        "long_name": "AAA LISTING INC",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 100,
                    },
                    {
                        "symbol": "BBB",
                        "long_name": "BBB LISTING INC",
                        "sector": "Technology",
                        "industry": "Software",
                        "market_cap": 300,
                    },
                ]
            return self._query_fn(db_name, sql, params)

        snapshot = build_market_movers_snapshot(
            universe_code="TOP1000",
            period="daily",
            top_n=5,
            today=date(2026, 5, 28),
            prefer_intraday=False,
            query_fn=query_fn,
        )

        self.assertIn("LEFT JOIN nyse_stock", observed_sql["universe"])
        self.assertIn("COALESCE(NULLIF(p.long_name, ''), s.name)", observed_sql["universe"])
        self.assertEqual(snapshot["rows"].iloc[0]["Symbol"], "BBB")
        self.assertEqual(snapshot["rows"].iloc[0]["Name"], "BBB LISTING INC")

    def test_group_leadership_snapshot_uses_monthly_weighted_and_equal_returns(self) -> None:
        from app.services.overview_market_intelligence import build_group_leadership_snapshot

        snapshot = build_group_leadership_snapshot(
            universe_limit=100,
            group_by="sector",
            top_n=5,
            min_group_size=1,
            today=date(2026, 5, 28),
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["date_window"]["period"], "monthly")
        self.assertEqual(snapshot["period"], "monthly")
        self.assertEqual(snapshot["trend_window_label"], "Last 12M")
        self.assertFalse(snapshot["trend_rows"].empty)
        self.assertFalse(snapshot["ticker_leader_rows"].empty)
        self.assertEqual(snapshot["coverage"]["returnable_count"], 3)
        first_row = snapshot["rows"].iloc[0]
        self.assertEqual(first_row["Group"], "Technology")
        self.assertEqual(first_row["Symbols"], 2)
        self.assertEqual(first_row["Positive Symbols"], 2)
        self.assertEqual(first_row["Positive Symbol Share %"], 100.0)
        self.assertEqual(first_row["Equal Weight Return %"], 20.0)
        self.assertEqual(first_row["Market Cap Weighted Return %"], 25.0)
        self.assertEqual(first_row["Cap vs Equal Gap pp"], 5.0)
        self.assertEqual(first_row["Top 3 Positive Share %"], 100.0)
        self.assertEqual(first_row["Top Symbol"], "BBB")
        technology_leaders = snapshot["ticker_leader_rows"][
            snapshot["ticker_leader_rows"]["Group"] == "Technology"
        ].sort_values("Rank")
        self.assertEqual(technology_leaders["Symbol"].tolist(), ["BBB", "AAA"])
        self.assertEqual(technology_leaders.iloc[0]["Positive Return Share %"], 75.0)
        self.assertIn("Previous Return %", technology_leaders.columns)
        self.assertIn("Momentum Delta pp", technology_leaders.columns)

    def test_group_leadership_snapshot_supports_sp500_daily_trend(self) -> None:
        from app.services.overview_market_intelligence import build_group_leadership_snapshot

        snapshot = build_group_leadership_snapshot(
            universe_code="SP500",
            universe_limit=500,
            group_by="sector",
            period="daily",
            top_n=5,
            min_group_size=1,
            today=date(2026, 5, 28),
            trend_groups=("Healthcare",),
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["universe_code"], "SP500")
        self.assertEqual(snapshot["period"], "daily")
        self.assertEqual(snapshot["trend_window_label"], "Last 1M")
        self.assertEqual(snapshot["coverage"]["price_mode"], "Intraday Snapshot")
        self.assertEqual(snapshot["coverage"]["snapshot_time_utc"], "2026-05-18 15:35")
        self.assertEqual(snapshot["date_window"]["start_date"], "Previous Close")
        self.assertEqual(snapshot["rows"].iloc[0]["Top Symbol"], "AAA")
        self.assertEqual(snapshot["rows"].iloc[0]["Top Symbol Return %"], 12.0)
        self.assertEqual(snapshot["ticker_leader_rows"].iloc[0]["End Date"], "2026-05-18 15:30")
        self.assertEqual(snapshot["ticker_leader_rows"].iloc[0]["Previous Return %"], 5.26)
        self.assertEqual(snapshot["ticker_leader_rows"].iloc[0]["Momentum Delta pp"], 6.74)
        self.assertEqual(snapshot["coverage"]["coverage_basis"], "Current S&P 500 constituents")
        self.assertFalse(snapshot["rows"].empty)
        self.assertFalse(snapshot["trend_rows"].empty)
        self.assertIn("Healthcare", set(snapshot["trend_rows"]["Group"]))

    def test_market_events_snapshot_reads_fomc_rows_from_db(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        snapshot = build_market_events_snapshot(
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["event_count"], 2)
        self.assertEqual(snapshot["coverage"]["next_event_date"], "2026-06-17")
        self.assertEqual(snapshot["coverage"]["latest_collected_at"], "2026-05-28 02:00")
        self.assertEqual(snapshot["coverage"]["official_count"], 2)
        self.assertEqual(snapshot["coverage"]["estimate_count"], 0)
        self.assertEqual(snapshot["rows"].iloc[0]["Type"], "FOMC_MEETING")
        self.assertEqual(snapshot["rows"].iloc[0]["Date"], "2026-06-17")
        self.assertEqual(snapshot["rows"].iloc[0]["Days Until"], 20)
        self.assertEqual(snapshot["rows"].iloc[0]["Importance"], "High")
        self.assertEqual(snapshot["rows"].iloc[0]["Focus"], "Next 30D")
        self.assertEqual(snapshot["rows"].iloc[0]["Source Type"], "Official")
        self.assertEqual(snapshot["rows"].iloc[0]["Freshness"], "Official")

    def test_market_events_snapshot_can_read_all_event_types(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        snapshot = build_market_events_snapshot(
            event_type=None,
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=self._query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["event_type"], "All")
        self.assertEqual(snapshot["coverage"]["event_count"], 3)
        self.assertEqual(snapshot["coverage"]["official_count"], 2)
        self.assertEqual(snapshot["coverage"]["estimate_count"], 1)
        self.assertEqual(snapshot["coverage"]["estimate_only_count"], 1)
        self.assertEqual(snapshot["coverage"]["action_required_count"], 1)
        self.assertEqual(snapshot["coverage"]["high_importance_count"], 2)
        self.assertEqual(snapshot["coverage"]["needs_review_count"], 1)
        self.assertEqual(snapshot["coverage"]["this_week_count"], 0)
        self.assertEqual(snapshot["coverage"]["next_30d_count"], 1)
        self.assertEqual(snapshot["coverage"]["stale_estimate_count"], 0)
        self.assertEqual(set(snapshot["rows"]["Type"]), {"FOMC_MEETING", "EARNINGS"})
        earnings_row = snapshot["rows"][snapshot["rows"]["Type"] == "EARNINGS"].iloc[0]
        self.assertEqual(earnings_row["Importance"], "Medium")
        self.assertEqual(earnings_row["Focus"], "Needs Review")
        self.assertEqual(earnings_row["Source Type"], "Provider Estimate")
        self.assertEqual(earnings_row["Freshness"], "Current estimate")
        self.assertEqual(earnings_row["Quality Action"], "Enable cross-check or refresh closer to date")

    def test_market_events_snapshot_macro_filter_reads_macro_prefix_rows(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name
            self.assertIn("event_type LIKE %s", sql)
            self.assertIn("MACRO_%", params or [])
            return [
                {
                    "event_date": "2026-06-10",
                    "event_type": "MACRO_CPI",
                    "symbol": None,
                    "title": "CPI: Consumer Price Index for May 2026",
                    "source": "bureau_labor_statistics_release_schedule",
                    "source_type": "official",
                    "validation_status": "official",
                    "event_status": "active",
                    "source_url": "https://www.bls.gov/schedule/2026/",
                    "confidence": 0.95,
                    "collected_at": "2026-05-28 04:00:00",
                },
                {
                    "event_date": "2026-06-25",
                    "event_type": "MACRO_GDP",
                    "symbol": None,
                    "title": "GDP: Gross Domestic Product, 1st Quarter 2026",
                    "source": "bureau_economic_analysis_release_schedule",
                    "source_type": "official",
                    "validation_status": "official",
                    "event_status": "active",
                    "source_url": "https://www.bea.gov/index.php/news/schedule/full",
                    "confidence": 0.95,
                    "collected_at": "2026-05-28 04:00:00",
                },
            ]

        snapshot = build_market_events_snapshot(
            event_type="MACRO",
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["event_type"], "MACRO")
        self.assertEqual(snapshot["coverage"]["event_count"], 2)
        self.assertEqual(snapshot["coverage"]["official_count"], 2)
        self.assertEqual(set(snapshot["rows"]["Type"]), {"MACRO_CPI", "MACRO_GDP"})

    def test_market_events_snapshot_warns_on_stale_earnings_estimates(self) -> None:
        from app.services.overview_market_intelligence import build_market_events_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, sql, params
            return [
                {
                    "event_date": "2026-07-30",
                    "event_type": "EARNINGS",
                    "symbol": "MSFT",
                    "title": "MSFT Earnings Release",
                    "source": "yfinance_calendar",
                    "source_url": "https://finance.yahoo.com/quote/MSFT/analysis",
                    "confidence": 0.65,
                    "collected_at": "2026-05-01 03:00:00",
                }
            ]

        snapshot = build_market_events_snapshot(
            event_type="EARNINGS",
            today=date(2026, 5, 28),
            horizon_days=180,
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["estimate_count"], 1)
        self.assertEqual(snapshot["coverage"]["stale_estimate_count"], 1)
        self.assertEqual(snapshot["rows"].iloc[0]["Freshness"], "Stale estimate")
        self.assertEqual(snapshot["rows"].iloc[0]["Age Days"], 27)
        self.assertIn("Refresh Earnings Calendar", snapshot["warnings"][0])

    def test_collection_ops_snapshot_combines_db_freshness_and_run_history(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return [
                    {"universe_code": "SP500", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                    {"universe_code": "TOP1000", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                ]
            if "FROM futures_ohlcv" in sql:
                return [
                    {
                        "latest_candle_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        "active_symbols": 4,
                        "candle_rows": 240,
                    }
                ]
            if "FROM market_universe_member" in sql:
                return [
                    {
                        "universe_code": "SP500",
                        "active_symbols": 503,
                        "latest_collected_at": "2026-05-28 01:00:00",
                        "latest_as_of_date": "2026-05-28",
                    }
                ]
            if "FROM market_event_calendar" in sql:
                return [
                    {
                        "event_type": "FOMC_MEETING",
                        "active_events": 12,
                        "future_events": 12,
                        "next_event_date": "2026-06-17",
                        "latest_collected_at": "2026-05-28 02:00:00",
                    },
                    {
                        "event_type": "EARNINGS",
                        "active_events": 3,
                        "future_events": 3,
                        "next_event_date": "2026-07-30",
                        "latest_collected_at": "2026-05-28 03:00:00",
                    },
                ]
            return []

        snapshot = build_collection_ops_snapshot(
            today=date(2026, 5, 28),
            query_fn=query_fn,
            history_rows=[
                {
                    "job_name": "collect_sp500_universe",
                    "status": "success",
                    "finished_at": "2026-05-28 01:01:00",
                    "rows_written": 503,
                    "symbols_processed": 503,
                    "failed_symbols": [],
                    "duration_sec": 1.2,
                    "message": "S&P 500 universe collection completed.",
                },
                {
                    "job_name": "collect_sp500_universe",
                    "status": "success",
                    "finished_at": "2026-05-28 01:05:00",
                    "rows_written": 503,
                    "symbols_processed": 503,
                    "failed_symbols": [],
                    "duration_sec": 1.1,
                    "message": "S&P 500 universe scheduled collection completed.",
                    "run_metadata": {"execution_mode": "scheduled"},
                },
                {
                    "job_name": "collect_sp500_intraday_snapshot",
                    "status": "success",
                    "finished_at": "2026-05-28 04:05:00",
                    "rows_written": 503,
                    "symbols_processed": 503,
                    "failed_symbols": [],
                    "duration_sec": 5.1,
                    "message": "S&P 500 browser auto snapshot completed.",
                    "run_metadata": {
                        "execution_mode": "browser_auto",
                        "automation_profile": "browser_safe",
                    },
                },
                {
                    "job_name": "collect_earnings_calendar",
                    "status": "partial_success",
                    "finished_at": "2026-05-28 03:01:00",
                    "rows_written": 2,
                    "symbols_processed": 2,
                    "failed_symbols": ["AAA"],
                    "duration_sec": 2.5,
                    "message": "Earnings calendar completed with missing symbols.",
                },
            ],
        )

        rows = snapshot["rows"]
        self.assertEqual(snapshot["status"], "REVIEW")
        self.assertEqual(snapshot["coverage"]["partial_count"], 1)
        universe_row = rows[rows["Area"] == "S&P 500 Universe"].iloc[0]
        self.assertEqual(universe_row["Status"], "OK")
        self.assertEqual(universe_row["Rows"], 503)
        self.assertEqual(universe_row["Last Auto Run"], "2026-05-28 01:05")
        self.assertEqual(universe_row["Auto Source"], "Scheduled")
        self.assertEqual(universe_row["Last Manual Run"], "2026-05-28 01:01")
        self.assertEqual(universe_row["Next Auto Due"], "2026-05-29 01:05")
        sp500_intraday_row = rows[rows["Area"] == "S&P 500 Daily Snapshot"].iloc[0]
        self.assertEqual(sp500_intraday_row["Last Auto Run"], "2026-05-28 04:05")
        self.assertEqual(sp500_intraday_row["Auto Source"], "Browser Auto")
        self.assertEqual(sp500_intraday_row["Next Auto Due"], "2026-05-28 04:10")
        futures_row = rows[rows["Area"] == "Futures Monitor 1m OHLCV"].iloc[0]
        self.assertEqual(futures_row["Status"], "OK")
        self.assertIn("4 symbols", futures_row["Data Freshness"])
        self.assertEqual(snapshot["coverage"]["latest_auto_at"], "2026-05-28 04:05")
        earnings_row = rows[rows["Area"] == "Earnings Calendar"].iloc[0]
        self.assertEqual(earnings_row["Status"], "Partial")
        self.assertEqual(earnings_row["Failed"], 1)
        self.assertEqual(earnings_row["Failure Streak"], 1)
        self.assertIn("Inspect failed symbols", earnings_row["Next Action"])

    def test_collection_ops_snapshot_supports_legacy_event_calendar_schema(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        event_query_count = 0

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            nonlocal event_query_count
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return [
                    {"universe_code": "SP500", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                    {"universe_code": "TOP1000", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                    {"universe_code": "TOP2000", "interval_code": "5m", "latest_snapshot_time": "2026-05-28 00:00:00"},
                ]
            if "FROM futures_ohlcv" in sql:
                return [
                    {
                        "latest_candle_time": datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S"),
                        "active_symbols": 4,
                        "candle_rows": 240,
                    }
                ]
            if "FROM market_universe_member" in sql:
                return [
                    {
                        "universe_code": "SP500",
                        "active_symbols": 503,
                        "latest_collected_at": "2026-05-28 01:00:00",
                        "latest_as_of_date": "2026-05-28",
                    }
                ]
            if "FROM market_event_calendar" in sql:
                event_query_count += 1
                if "event_status" in sql:
                    raise RuntimeError("Unknown column 'event_status'")
                return [
                    {
                        "event_type": "FOMC_MEETING",
                        "active_events": 12,
                        "future_events": 12,
                        "next_event_date": "2026-06-17",
                        "latest_collected_at": "2026-05-28 02:00:00",
                    }
                ]
            return []

        snapshot = build_collection_ops_snapshot(today=date(2026, 5, 28), query_fn=query_fn)

        self.assertEqual(event_query_count, 2)
        fomc_row = snapshot["rows"][snapshot["rows"]["Area"] == "FOMC Calendar"].iloc[0]
        self.assertEqual(fomc_row["Status"], "OK")
        self.assertIn("next 2026-06-17", fomc_row["Data Freshness"])

    def test_collection_ops_snapshot_marks_macro_calendar_due_when_some_macro_types_missing(self) -> None:
        from app.services.overview_market_intelligence import build_collection_ops_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM market_intraday_snapshot" in sql:
                return []
            if "FROM futures_ohlcv" in sql:
                return []
            if "FROM market_universe_member" in sql:
                return []
            if "FROM market_event_calendar" in sql:
                return [
                    {
                        "event_type": "MACRO_GDP",
                        "active_events": 2,
                        "future_events": 2,
                        "next_event_date": "2026-06-25",
                        "latest_collected_at": "2026-05-28 04:00:00",
                    }
                ]
            return []

        snapshot = build_collection_ops_snapshot(today=date(2026, 5, 28), query_fn=query_fn)

        macro_row = snapshot["rows"][snapshot["rows"]["Area"] == "Macro Calendar"].iloc[0]
        self.assertEqual(macro_row["Status"], "Due")
        self.assertIn("covered 1/4", macro_row["Data Freshness"])


class FuturesMarketMonitoringContractTests(unittest.TestCase):
    def test_futures_monitor_snapshot_scores_moves_and_stale_state(self) -> None:
        from app.services.futures_market_monitoring import build_futures_monitor_snapshot

        base = pd.Timestamp("2026-06-02 00:00:00", tz=timezone.utc)
        candle_rows: list[dict[str, object]] = []
        for idx in range(0, 61):
            ts = base - pd.Timedelta(minutes=60 - idx)
            es_close = 100.0 + idx * 0.01
            nq_close = 100.0 + idx * 0.025
            for symbol, close in (("ES=F", es_close), ("NQ=F", nq_close)):
                candle_rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1m",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": close - 0.05,
                        "high": close + 0.1,
                        "low": close - 0.1,
                        "close": close,
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_instrument" in sql:
                return [
                    {"provider_symbol": "ES=F", "display_name": "E-mini S&P 500", "futures_group": "Equity Index", "source": "yfinance", "sort_order": 10},
                    {"provider_symbol": "NQ=F", "display_name": "E-mini Nasdaq 100", "futures_group": "Equity Index", "source": "yfinance", "sort_order": 20},
                ]
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            if "FROM futures_market_monitor_run" in sql:
                return [
                    {
                        "run_id": "run-1",
                        "status": "success",
                        "symbols_requested": 2,
                        "symbols_processed": 2,
                        "rows_written": len(candle_rows),
                        "latest_candle_time_utc": "2026-06-02 00:00:00",
                        "finished_at": "2026-06-02 00:00:01",
                    }
                ]
            return []

        snapshot = build_futures_monitor_snapshot(
            group="Equity Index",
            symbols=["ES=F", "NQ=F"],
            selected_symbol="NQ=F",
            now=datetime(2026, 6, 2, 0, 1, tzinfo=timezone.utc),
            query_fn=query_fn,
        )

        self.assertEqual(snapshot["status"], "OK")
        self.assertEqual(snapshot["coverage"]["returnable_count"], 2)
        self.assertEqual(snapshot["selected_symbol"], "NQ=F")
        self.assertFalse(snapshot["candles"].empty)
        self.assertFalse(snapshot["all_candles"].empty)
        self.assertEqual(set(snapshot["all_candles"]["Symbol"]), {"ES=F", "NQ=F"})
        self.assertEqual(snapshot["top_move"]["Symbol"], "NQ=F")
        nq_row = snapshot["rows"][snapshot["rows"]["Symbol"] == "NQ=F"].iloc[0]
        self.assertEqual(nq_row["State"], "Sharp")
        self.assertGreater(nq_row["60m %"], 1.0)

    def test_futures_monitor_preopen_core_uses_cross_asset_symbols(self) -> None:
        from app.services.futures_market_monitoring import build_futures_monitor_snapshot

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_instrument" in sql:
                return [
                    {"provider_symbol": "NQ=F", "display_name": "E-mini Nasdaq 100", "futures_group": "Equity Index", "source": "yfinance", "sort_order": 20},
                    {"provider_symbol": "ZN=F", "display_name": "10Y Treasury Note", "futures_group": "Rates", "source": "yfinance", "sort_order": 110},
                    {"provider_symbol": "CL=F", "display_name": "WTI Crude Oil", "futures_group": "Commodities", "source": "yfinance", "sort_order": 210},
                    {"provider_symbol": "6E=F", "display_name": "Euro FX", "futures_group": "FX Futures", "source": "yfinance", "sort_order": 310},
                ]
            return []

        snapshot = build_futures_monitor_snapshot(group="Pre-open Core", query_fn=query_fn)

        self.assertEqual(snapshot["symbols"], ["NQ=F", "ZN=F", "CL=F", "6E=F"])
        self.assertEqual(snapshot["selected_symbol"], "NQ=F")
        self.assertIn("Pre-open Core", snapshot["groups"])

    def test_futures_collector_normalizes_yfinance_frame_and_records_run(self) -> None:
        from finance.data import futures_market as fm

        idx = pd.date_range("2026-06-02 00:00:00", periods=2, freq="min", tz=timezone.utc)
        frame = pd.DataFrame(
            {
                ("Open", "ES=F"): [100.0, 101.0],
                ("High", "ES=F"): [101.0, 102.0],
                ("Low", "ES=F"): [99.0, 100.0],
                ("Close", "ES=F"): [100.5, 101.5],
                ("Adj Close", "ES=F"): [100.5, 101.5],
                ("Volume", "ES=F"): [1000, 1100],
            },
            index=idx,
        )

        written_rows: list[dict[str, object]] = []
        run_rows: list[dict[str, object]] = []

        def downloader(symbols, *, period, interval):
            self.assertEqual(symbols, ["ES=F"])
            self.assertEqual(period, "1d")
            self.assertEqual(interval, "1m")
            return frame

        def capture_ohlcv(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        def capture_run(row, **kwargs):
            del kwargs
            run_rows.append(row)
            return 1

        with (
            patch.object(fm, "sync_futures_market_tables", return_value=None),
            patch.object(fm, "upsert_futures_instruments", return_value=1),
            patch.object(fm, "upsert_futures_ohlcv_rows", side_effect=capture_ohlcv),
            patch.object(fm, "upsert_futures_monitor_run", side_effect=capture_run),
        ):
            result = fm.collect_and_store_futures_ohlcv(
                ["ES=F"],
                period="1d",
                interval="1m",
                downloader=downloader,
                sleep_sec=0,
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(result["symbols_processed"], 1)
        self.assertEqual(written_rows[0]["provider_symbol"], "ES=F")
        self.assertEqual(written_rows[0]["interval_code"], "1m")
        self.assertEqual(written_rows[0]["provider_status"], "ok")
        self.assertEqual(run_rows[0]["status"], "success")
        self.assertEqual(run_rows[0]["latest_candle_time_utc"], "2026-06-02 00:01:00")

    def test_ingestion_job_wraps_futures_collection_summary(self) -> None:
        from app.jobs import ingestion_jobs as jobs

        with patch.object(
            jobs,
            "collect_and_store_futures_ohlcv",
            return_value={
                "run_id": "run-job",
                "source": "yfinance",
                "period": "1d",
                "interval": "1m",
                "cadence_mode": "manual",
                "status": "partial_success",
                "rows_written": 10,
                "symbols_requested": 2,
                "symbols_processed": 1,
                "failed_symbols": ["NQ=F"],
                "latest_candle_time_utc": "2026-06-02 00:01:00",
                "diagnostics": {"batches": []},
            },
        ):
            result = jobs.run_collect_futures_ohlcv(["ES=F", "NQ=F"], max_symbols=2)

        self.assertEqual(result["job_name"], "collect_futures_ohlcv")
        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 10)
        self.assertEqual(result["failed_symbols"], ["NQ=F"])
        self.assertEqual(result["details"]["target_tables"][0], "finance_price.futures_ohlcv")


class FuturesMacroThermometerContractTests(unittest.TestCase):
    def _daily_rows(self, final_moves: dict[str, float], *, days: int = 260) -> list[dict[str, object]]:
        base = pd.Timestamp("2026-06-02 00:00:00", tz=timezone.utc) - pd.Timedelta(days=days - 1)
        rows: list[dict[str, object]] = []
        for symbol_index, (symbol, final_move) in enumerate(final_moves.items()):
            price = 100.0 + symbol_index * 7.0
            for idx in range(days):
                daily_move = 0.0003 + 0.003 * ((idx % 9) - 4) / 4
                if idx == days - 1:
                    daily_move = final_move
                price *= 1.0 + daily_move
                ts = base + pd.Timedelta(days=idx)
                rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1d",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": price * 0.995,
                        "high": price * 1.005,
                        "low": price * 0.99,
                        "close": price,
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )
        return rows

    def _risk_on_validation_rows(self, *, days: int = 150) -> tuple[list[str], list[dict[str, object]]]:
        symbols = [
            "ES=F",
            "NQ=F",
            "YM=F",
            "RTY=F",
            "ZN=F",
            "ZB=F",
            "CL=F",
            "GC=F",
            "SI=F",
            "HG=F",
            "NG=F",
            "6E=F",
            "6J=F",
            "6B=F",
            "6A=F",
            "6C=F",
        ]
        risk_growth = {"ES=F", "NQ=F", "YM=F", "RTY=F", "HG=F", "CL=F", "6A=F"}
        event_indices = {80, 105}
        base = pd.Timestamp("2026-01-01 00:00:00", tz=timezone.utc)
        rows: list[dict[str, object]] = []
        prices = {symbol: 100.0 + idx * 5.0 for idx, symbol in enumerate(symbols)}
        for idx in range(days):
            for symbol in symbols:
                daily_move = 0.0004 + 0.002 * ((idx % 7) - 3) / 3
                if idx in event_indices and symbol in risk_growth:
                    daily_move = 0.02
                elif any(event_idx < idx <= event_idx + 5 for event_idx in event_indices) and symbol in risk_growth:
                    daily_move = 0.006
                elif idx in event_indices and symbol in {"ZN=F", "ZB=F", "6E=F", "6J=F", "6B=F", "6C=F"}:
                    daily_move = 0.001
                prices[symbol] *= 1.0 + daily_move
                ts = base + pd.Timedelta(days=idx)
                rows.append(
                    {
                        "provider_symbol": symbol,
                        "interval_code": "1d",
                        "candle_time_utc": ts.strftime("%Y-%m-%d %H:%M:%S"),
                        "open": prices[symbol] * 0.995,
                        "high": prices[symbol] * 1.005,
                        "low": prices[symbol] * 0.99,
                        "close": prices[symbol],
                        "volume": 1000 + idx,
                        "source": "yfinance",
                        "provider_status": "ok",
                    }
                )
        return symbols, rows

    def test_macro_thermometer_inverts_rates_and_fx_pressure(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        symbols = [
            "ES=F",
            "NQ=F",
            "YM=F",
            "RTY=F",
            "ZN=F",
            "ZB=F",
            "CL=F",
            "GC=F",
            "SI=F",
            "HG=F",
            "NG=F",
            "6E=F",
            "6J=F",
            "6B=F",
            "6A=F",
            "6C=F",
        ]
        final_moves = {symbol: 0.001 for symbol in symbols}
        final_moves.update(
            {
                "ES=F": 0.018,
                "NQ=F": 0.024,
                "YM=F": 0.014,
                "RTY=F": 0.02,
                "ZN=F": -0.012,
                "ZB=F": -0.014,
                "6E=F": -0.01,
                "6J=F": -0.008,
                "6B=F": -0.011,
                "6A=F": -0.009,
                "6C=F": -0.008,
            }
        )
        candle_rows = self._daily_rows(final_moves)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=symbols, query_fn=query_fn)
        scores = snapshot["scores"].set_index("Score")

        self.assertEqual(snapshot["status"], "OK")
        self.assertGreater(scores.loc["Risk-On Score", "Value"], 20)
        self.assertGreater(scores.loc["Rate Pressure Score", "Value"], 20)
        self.assertGreater(scores.loc["Dollar Pressure Score", "Value"], 20)
        rate_components = snapshot["score_components"]
        zn_component = rate_components[
            (rate_components["Score"] == "Rate Pressure Score") & (rate_components["Symbol"] == "ZN=F")
        ].iloc[0]
        self.assertLess(zn_component["Raw Std Move"], 0)
        self.assertGreater(zn_component["Score Move"], 0)

    def test_macro_thermometer_detects_rate_pressure_scenario(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        symbols = ["ES=F", "NQ=F", "RTY=F", "ZN=F", "ZB=F", "GC=F", "HG=F", "CL=F", "6A=F"]
        final_moves = {symbol: 0.001 for symbol in symbols}
        final_moves.update({"NQ=F": -0.025, "ZN=F": -0.015, "ZB=F": -0.017, "GC=F": -0.018})
        candle_rows = self._daily_rows(final_moves)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=symbols, query_fn=query_fn)

        self.assertEqual(snapshot["summary"]["scenario"], "금리 상승 부담")
        self.assertIn("금리 상승 압력", snapshot["summary"]["summary"])
        self.assertGreater(snapshot["scores"].set_index("Score").loc["Rate Pressure Score", "Value"], 20)

    def test_macro_thermometer_warns_when_daily_history_is_short(self) -> None:
        from app.services.futures_macro_thermometer import build_futures_macro_thermometer_snapshot

        candle_rows = self._daily_rows({"ES=F": 0.02, "NQ=F": 0.02}, days=20)

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            return []

        snapshot = build_futures_macro_thermometer_snapshot(symbols=["ES=F", "NQ=F"], query_fn=query_fn)

        self.assertEqual(snapshot["status"], "REVIEW")
        self.assertIn("less than 6 months", " ".join(snapshot["warnings"]))
        self.assertEqual(snapshot["coverage"]["standardized_count"], 0)

    def test_macro_validation_recomputes_point_in_time_scenario_hits(self) -> None:
        from app.services.futures_macro_validation import build_futures_macro_validation_snapshot

        symbols, candle_rows = self._risk_on_validation_rows()

        def query_fn(db_name: str, sql: str, params=None) -> list[dict[str, object]]:
            del db_name, params
            if "FROM futures_ohlcv" in sql:
                return candle_rows
            if "FROM nyse_price_history" in sql:
                return []
            return []

        validation = build_futures_macro_validation_snapshot(
            symbols=symbols,
            query_fn=query_fn,
            current_snapshot={"summary": {"scenario": "좋은 risk-on"}},
            min_standardized_symbols=8,
        )
        summary = validation["scenario_summary"]

        self.assertIn(validation["status"], {"OK", "REVIEW"})
        self.assertFalse(validation["records"].empty)
        self.assertIn("좋은 risk-on", set(summary["Scenario"]))
        risk_on_row = summary[summary["Scenario"] == "좋은 risk-on"].iloc[0]
        self.assertGreaterEqual(risk_on_row["Sample 5D"], 1)
        self.assertIsNotNone(risk_on_row["Hit Rate 5D %"])
        self.assertGreaterEqual(risk_on_row["Hit Rate 5D %"], 50)

    def test_interpretation_confidence_uses_current_coverage_and_validation_sample(self) -> None:
        from app.services.futures_macro_validation import build_interpretation_confidence

        current_snapshot = {
            "coverage": {
                "symbol_count": 16,
                "standardized_count": 16,
                "min_data_days": 260,
                "latest_daily_date": date.today().isoformat(),
            },
            "evidence_groups": {
                "counts": {
                    "strong": 4,
                    "weak": 1,
                    "missing": 0,
                    "conflicting": 0,
                }
            },
        }
        validation_snapshot = {
            "coverage": {
                "validation_dates": 100,
                "history_span_years": 4.0,
            },
            "current_scenario_metrics": {
                "Scenario": "좋은 risk-on",
                "Sample 5D": 80,
                "Hit Rate 5D %": 61.0,
            },
        }

        confidence = build_interpretation_confidence(current_snapshot, validation_snapshot)

        self.assertIn(confidence["label"], {"High Confidence", "Medium Confidence"})
        self.assertEqual(confidence["sample_size"], 80)
        self.assertEqual(confidence["hit_rate_5d"], 61.0)

        low_snapshot = {
            "coverage": {
                "symbol_count": 16,
                "standardized_count": 0,
                "min_data_days": 20,
                "latest_daily_date": date.today().isoformat(),
            },
            "evidence_groups": {"counts": {}},
        }
        low_confidence = build_interpretation_confidence(low_snapshot, validation_snapshot)

        self.assertEqual(low_confidence["label"], "Not Enough History")


class MarketIntelligenceIngestionContractTests(unittest.TestCase):
    def test_sp500_snapshot_uses_fast_quote_rows_without_yfinance_download(self) -> None:
        from finance.data import market_intelligence as mi

        members = [
            {"symbol": "AAA"},
            {"symbol": "BBB"},
        ]

        def quote_fetcher(symbols):
            self.assertEqual(symbols, ["AAA", "BBB"])
            return [
                {
                    "symbol": "AAA",
                    "regularMarketPrice": 112.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912000,
                    "regularMarketVolume": 1000,
                    "marketState": "REGULAR",
                },
                {
                    "symbol": "BBB",
                    "regularMarketPrice": 96.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912001,
                    "regularMarketVolume": 2000,
                    "marketState": "REGULAR",
                },
            ]

        written_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        with (
            patch.object(mi, "sync_market_intelligence_tables", return_value=None),
            patch.object(mi, "_load_db_previous_close_map", return_value={}),
            patch.object(mi, "upsert_intraday_snapshot_rows", side_effect=capture_rows),
        ):
            result = mi.collect_and_store_sp500_intraday_snapshot(
                universe_loader=lambda: members,
                quote_fetcher=quote_fetcher,
                quote_batch_size=200,
                method="quote_fast",
                fallback_to_yfinance=False,
            )

        self.assertEqual(result["source"], "yahoo_quote")
        self.assertEqual(result["method"], "quote_fast")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(result["symbols_processed"], 2)
        self.assertEqual(written_rows[0]["source"], "yahoo_quote")
        self.assertAlmostEqual(float(written_rows[0]["return_pct"]), 12.0)
        self.assertAlmostEqual(float(written_rows[1]["return_pct"]), -4.0)

    def test_top_universe_snapshot_writes_top1000_rows(self) -> None:
        from finance.data import market_intelligence as mi

        members = [{"symbol": "AAA"}, {"symbol": "BBB"}]

        def quote_fetcher(symbols):
            self.assertEqual(symbols, ["AAA", "BBB"])
            return [
                {
                    "symbol": "AAA",
                    "regularMarketPrice": 112.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912000,
                    "regularMarketVolume": 1000,
                },
                {
                    "symbol": "BBB",
                    "regularMarketPrice": 96.0,
                    "regularMarketPreviousClose": 100.0,
                    "regularMarketTime": 1779912001,
                    "regularMarketVolume": 2000,
                },
            ]

        written_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            written_rows.extend(rows)
            return len(rows)

        with (
            patch.object(mi, "sync_market_intelligence_tables", return_value=None),
            patch.object(mi, "_load_db_previous_close_map", return_value={}),
            patch.object(mi, "upsert_intraday_snapshot_rows", side_effect=capture_rows),
        ):
            result = mi.collect_and_store_market_intraday_snapshot(
                universe_code="TOP1000",
                universe_limit=1000,
                universe_loader=lambda: members,
                quote_fetcher=quote_fetcher,
                quote_batch_size=200,
                method="quote_fast",
                fallback_to_yfinance=False,
            )

        self.assertEqual(result["universe_code"], "TOP1000")
        self.assertEqual(result["universe_limit"], 1000)
        self.assertEqual(result["source"], "yahoo_quote")
        self.assertEqual(result["rows_written"], 2)
        self.assertEqual(written_rows[0]["universe_code"], "TOP1000")
        self.assertAlmostEqual(float(written_rows[0]["return_pct"]), 12.0)

    def test_quote_gap_diagnostics_explain_batch_only_gap(self) -> None:
        from finance.data import market_intelligence as mi

        class EmptyTicker:
            fast_info = {}

            def __init__(self, symbol: str) -> None:
                self.symbol = symbol

        def quote_fetcher(symbols):
            self.assertEqual(symbols, ["AAA"])
            return [
                {
                    "symbol": "AAA",
                    "regularMarketPrice": 112.0,
                    "regularMarketPreviousClose": 100.0,
                }
            ]

        result = mi.diagnose_market_quote_gaps(
            ["AAA"],
            quote_fetcher=quote_fetcher,
            ticker_factory=EmptyTicker,
            history_downloader=lambda *args, **kwargs: pd.DataFrame(),
            db_previous_close_map={},
            profile_map={"AAA": {"status": "active"}},
        )

        self.assertEqual(result["diagnosis_counts"], {"batch_only_gap": 1})
        row = result["diagnostics"][0]
        self.assertEqual(row["Diagnosis"], "batch_only_gap")
        self.assertEqual(row["Quote Single Status"], "ok")
        self.assertIn("Single-symbol", row["Evidence Summary"])

    def test_quote_gap_diagnostics_explain_provider_quote_gap(self) -> None:
        from finance.data import market_intelligence as mi

        class EmptyTicker:
            fast_info = {}

            def __init__(self, symbol: str) -> None:
                self.symbol = symbol

        def history_downloader(symbols, **kwargs):
            self.assertEqual(symbols, ["BBB"])
            del kwargs
            return pd.DataFrame(
                {"Close": [100.0, 105.0], "Volume": [1000, 1200]},
                index=pd.to_datetime(["2026-05-27", "2026-05-28"]),
            )

        result = mi.diagnose_market_quote_gaps(
            ["BBB"],
            quote_fetcher=lambda symbols: [],
            ticker_factory=EmptyTicker,
            history_downloader=history_downloader,
            db_previous_close_map={"BBB": {"previous_close": 105.0, "previous_close_date": "2026-05-28"}},
            profile_map={"BBB": {"status": "active"}},
        )

        self.assertEqual(result["diagnosis_counts"], {"provider_quote_gap": 1})
        row = result["diagnostics"][0]
        self.assertEqual(row["Diagnosis"], "provider_quote_gap")
        self.assertEqual(row["History Status"], "ok")
        self.assertEqual(row["DB Price Status"], "ok")

    def test_quote_gap_diagnostics_build_persistent_issue_rows(self) -> None:
        from finance.data import market_intelligence as mi

        rows = mi.build_quote_gap_issue_rows(
            [
                {
                    "Symbol": "bbb",
                    "Diagnosis": "provider_quote_gap",
                    "Confidence": 0.82,
                    "Evidence Summary": "Alternate price evidence exists.",
                    "Recommended Action": "Rerun later.",
                }
            ],
            universe_code="top1000",
            interval_code="5m",
            snapshot_time_utc="2026-05-29 13:30:00",
            seen_at="2026-05-29 13:31:00",
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["issue_type"], "quote_gap")
        self.assertEqual(row["universe_code"], "TOP1000")
        self.assertEqual(row["symbol"], "BBB")
        self.assertEqual(row["diagnosis"], "provider_quote_gap")
        self.assertEqual(row["last_snapshot_time_utc"], "2026-05-29 13:30:00")
        self.assertIn("provider_quote_gap", row["raw_payload_json"])

    def test_quote_gap_job_persists_issue_history(self) -> None:
        from app.jobs import ingestion_jobs

        diagnosis = {
            "universe_code": "TOP1000",
            "interval_code": "5m",
            "snapshot_time_utc": "2026-05-29 13:30:00",
            "symbols_requested": 1,
            "symbols_processed": 1,
            "diagnosis_counts": {"provider_quote_gap": 1},
            "diagnostics": [{"Symbol": "BBB", "Diagnosis": "provider_quote_gap"}],
        }
        issue_history = [
            {
                "universe_code": "TOP1000",
                "symbol": "BBB",
                "diagnosis": "provider_quote_gap",
                "occurrence_count": 3,
            }
        ]

        with (
            patch.object(ingestion_jobs, "diagnose_market_quote_gaps", return_value=diagnosis),
            patch.object(
                ingestion_jobs,
                "persist_quote_gap_diagnostics",
                return_value={"rows_written": 1, "issues": issue_history},
            ) as persist,
        ):
            result = ingestion_jobs.run_diagnose_market_quote_gaps(
                symbols=["BBB"],
                universe_code="TOP1000",
                snapshot_time_utc="2026-05-29 13:30:00",
            )

        persist.assert_called_once()
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["details"]["issue_rows_written"], 1)
        self.assertEqual(result["details"]["issue_history"][0]["occurrence_count"], 3)
        self.assertIn("Persisted 1 issue row", result["message"])


class MarketIntelligenceEventCalendarContractTests(unittest.TestCase):
    def test_market_event_schema_contains_required_columns(self) -> None:
        from finance.data.db.schema import MARKET_INTELLIGENCE_SCHEMAS

        schema_sql = MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"]

        for column in [
            "event_date",
            "event_type",
            "symbol",
            "title",
            "source",
            "source_type",
            "validation_status",
            "event_status",
            "superseded_by_event_key",
            "superseded_at",
            "source_url",
            "confidence",
            "collected_at",
            "raw_payload_json",
        ]:
            self.assertIn(column, schema_sql)
        self.assertIn("UNIQUE KEY uk_market_event_key", schema_sql)

    def test_market_data_issue_schema_tracks_repeated_quote_gaps(self) -> None:
        from finance.data.db.schema import MARKET_INTELLIGENCE_SCHEMAS

        schema_sql = MARKET_INTELLIGENCE_SCHEMAS["market_data_issue"]

        for column in [
            "issue_key",
            "issue_type",
            "universe_code",
            "symbol",
            "diagnosis",
            "occurrence_count",
            "first_seen_at",
            "last_seen_at",
            "latest_confidence",
            "latest_recommended_action",
            "raw_payload_json",
        ]:
            self.assertIn(column, schema_sql)
        self.assertIn("UNIQUE KEY uk_market_data_issue_key", schema_sql)

    def test_fomc_calendar_parser_uses_final_meeting_day_and_official_links(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <div class="panel panel-default">
          <div class="panel-heading"><h4><a id="42828">2026 FOMC Meetings</a></h4></div>
          <div class="row fomc-meeting">
            <div class="fomc-meeting__month"><strong>June</strong></div>
            <div class="fomc-meeting__date">16-17*</div>
            <a href="/newsevents/pressreleases/monetary20260617a.htm">HTML</a>
          </div>
          <div class="row fomc-meeting">
            <div class="fomc-meeting__month"><strong>Apr/May</strong></div>
            <div class="fomc-meeting__date">30-1</div>
          </div>
        </div>
        """

        rows = mi._parse_fomc_calendar_events_from_html(  # noqa: SLF001
            html,
            source_url="https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm",
            years=[2026],
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["event_date"], "2026-06-17")
        self.assertEqual(rows[0]["event_type"], "FOMC_MEETING")
        self.assertTrue(rows[0]["raw_payload"]["has_summary_of_economic_projections"])
        self.assertEqual(
            rows[0]["raw_payload"]["links"][0]["url"],
            "https://www.federalreserve.gov/newsevents/pressreleases/monetary20260617a.htm",
        )
        self.assertEqual(rows[1]["event_date"], "2026-05-01")

    def test_collect_fomc_calendar_writes_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        with (
            patch.object(
                mi,
                "fetch_fomc_calendar_events",
                return_value=[
                    {
                        "event_date": "2026-06-17",
                        "event_type": "FOMC_MEETING",
                        "symbol": None,
                        "title": "FOMC Meeting: June 16-17*, 2026",
                        "source": mi.FOMC_CALENDAR_SOURCE,
                        "source_url": mi.FOMC_CALENDAR_SOURCE_URL,
                        "confidence": 1.0,
                        "raw_payload": {"meeting_range": "June 16-17*"},
                    }
                ],
            ),
            patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows),
        ):
            result = mi.collect_and_store_fomc_calendar(years=[2026])

        self.assertEqual(result["source"], mi.FOMC_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "FOMC_MEETING")
        self.assertEqual(result["events_found"], 1)
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(result["event_dates"], ["2026-06-17"])
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_bls_macro_calendar_parser_builds_official_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <table>
          <thead><tr><th>Date Time</th><th>Release</th></tr></thead>
          <tbody>
            <tr><td>Wednesday, June 10, 2026 08:30 AM</td><td>Consumer Price Index for May 2026</td></tr>
            <tr><td>Thursday, June 11, 2026 08:30 AM</td><td>Producer Price Index for May 2026</td></tr>
            <tr><td>Friday, June 5, 2026 08:30 AM</td><td>Employment Situation for May 2026</td></tr>
            <tr><td>Friday, June 5, 2026 10:00 AM</td><td>Other Release for May 2026</td></tr>
          </tbody>
        </table>
        """

        rows = mi.parse_bls_macro_calendar_events_from_html(
            html,
            source_url="https://www.bls.gov/schedule/2026/",
            year=2026,
        )

        self.assertEqual([row["event_type"] for row in rows], ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT"])
        self.assertEqual(rows[0]["event_date"], "2026-06-10")
        self.assertEqual(rows[0]["source_type"], "official")
        self.assertEqual(rows[0]["validation_status"], "official")
        self.assertEqual(rows[0]["raw_payload"]["reference_period"], "May 2026")
        self.assertEqual(rows[0]["raw_payload"]["release_time_et"], "08:30")

    def test_bls_macro_calendar_ics_parser_builds_official_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        ics_text = """
BEGIN:VCALENDAR
BEGIN:VEVENT
UID:cpi-20260610@bls.gov
DTSTART:20260610T123000Z
SUMMARY:Consumer Price Index for May 2026
END:VEVENT
BEGIN:VEVENT
UID:ppi-20260611@bls.gov
DTSTART;TZID=America/New_York:20260611T083000
SUMMARY:Producer Price Index for May 2026
END:VEVENT
BEGIN:VEVENT
UID:jobs-20260605@bls.gov
DTSTART;VALUE=DATE:20260605
SUMMARY:Employment Situation for May
  2026
END:VEVENT
BEGIN:VEVENT
UID:other-20260605@bls.gov
DTSTART:20260605T140000Z
SUMMARY:Other Release for May 2026
END:VEVENT
END:VCALENDAR
        """

        rows = mi.parse_bls_macro_calendar_events_from_ics(
            ics_text,
            years=[2026],
            source_name="bls.ics",
        )

        self.assertEqual([row["event_type"] for row in rows], ["MACRO_CPI", "MACRO_PPI", "MACRO_EMPLOYMENT"])
        self.assertEqual([row["event_date"] for row in rows], ["2026-06-10", "2026-06-11", "2026-06-05"])
        self.assertEqual(rows[0]["raw_payload"]["release_time_et"], "08:30")
        self.assertEqual(rows[0]["raw_payload"]["import_method"], "official_ics_file")
        self.assertEqual(rows[0]["raw_payload"]["source_file_name"], "bls.ics")
        self.assertEqual(rows[2]["raw_payload"]["reference_period"], "May 2026")

    def test_collect_bls_macro_calendar_ics_writes_events(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        ics_text = """
BEGIN:VCALENDAR
BEGIN:VEVENT
UID:cpi-20260610@bls.gov
DTSTART:20260610T123000Z
SUMMARY:Consumer Price Index for May 2026
END:VEVENT
END:VCALENDAR
        """

        with patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows):
            result = mi.collect_and_store_bls_macro_calendar_ics(
                ics_text,
                years=[2026],
                source_name="bls.ics",
            )

        self.assertEqual(result["source"], mi.BLS_MACRO_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "MACRO")
        self.assertEqual(result["method"], "official_ics_file")
        self.assertEqual(result["event_types"], ["MACRO_CPI"])
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_bea_gdp_calendar_parser_excludes_state_and_county_gdp(self) -> None:
        from finance.data import market_intelligence as mi

        html = """
        <table>
          <thead><tr><th>Year 2026</th><th>Type</th><th>Release</th><th></th></tr></thead>
          <tbody>
            <tr><td>June 25 8:30 AM</td><td>News</td><td>Gross Domestic Product, 1st Quarter 2026 (Third Estimate)</td><td></td></tr>
            <tr><td>June 30 8:30 AM</td><td>News</td><td>Gross Domestic Product by State, 1st Quarter 2026</td><td>View</td></tr>
            <tr><td>July 30 8:30 AM</td><td>News</td><td>GDP (Advance Estimate), 2nd Quarter 2026</td><td>View</td></tr>
          </tbody>
        </table>
        """

        rows = mi.parse_bea_gdp_calendar_events_from_html(
            html,
            source_url="https://www.bea.gov/index.php/news/schedule/full",
            years=[2026],
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual([row["event_date"] for row in rows], ["2026-06-25", "2026-07-30"])
        self.assertTrue(all(row["event_type"] == "MACRO_GDP" for row in rows))
        self.assertEqual(rows[0]["raw_payload"]["release_time_et"], "08:30")
        self.assertIsNone(rows[0]["raw_payload"]["source_row"]["Unnamed: 3"])

    def test_collect_macro_calendar_writes_events_and_reports_failed_sources(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        def fake_fetcher(**kwargs):
            self.assertEqual(kwargs["years"], [2026])
            return {
                "source": mi.MACRO_CALENDAR_SOURCE,
                "source_url": "https://example.test/macro",
                "event_type": "MACRO",
                "method": "official_html",
                "events": [
                    {
                        "event_date": "2026-06-10",
                        "event_type": "MACRO_CPI",
                        "title": "CPI: Consumer Price Index for May 2026",
                        "source": mi.BLS_MACRO_CALENDAR_SOURCE,
                        "source_type": "official",
                        "validation_status": "official",
                        "source_url": "https://www.bls.gov/schedule/2026/",
                        "confidence": 0.95,
                    }
                ],
                "events_found": 1,
                "failed_sources": ["BEA: temporary failure"],
            }

        with patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows):
            result = mi.collect_and_store_macro_calendar(years=[2026], macro_fetcher=fake_fetcher)

        self.assertEqual(result["source"], mi.MACRO_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "MACRO")
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(result["event_types"], ["MACRO_CPI"])
        self.assertEqual(result["failed_sources"], ["BEA: temporary failure"])
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_yfinance_earnings_calendar_builds_event_rows_for_window(self) -> None:
        from finance.data import market_intelligence as mi

        calendars = {
            "AAA": {
                "Earnings Date": [date(2026, 7, 30)],
                "Earnings Average": 1.23,
                "Revenue Average": 1000000,
            },
            "BBB": {},
        }

        class FakeTicker:
            def __init__(self, symbol: str) -> None:
                self.calendar = calendars[symbol]

        result = mi.fetch_yfinance_earnings_calendar_events(
            ["AAA", "BBB"],
            start_date="2026-05-28",
            lookahead_days=120,
            ticker_factory=FakeTicker,
        )

        self.assertEqual(result["source"], mi.EARNINGS_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "EARNINGS")
        self.assertEqual(result["events_found"], 1)
        self.assertEqual(result["missing_symbols"], ["BBB"])
        row = result["events"][0]
        self.assertEqual(row["event_date"], "2026-07-30")
        self.assertEqual(row["symbol"], "AAA")
        self.assertEqual(row["event_type"], "EARNINGS")
        self.assertEqual(row["confidence"], 0.65)
        self.assertEqual(row["source_type"], "provider_estimate")
        self.assertEqual(row["validation_status"], "estimate_only")
        self.assertEqual(row["raw_payload"]["provider_calendar"]["Earnings Average"], 1.23)
        self.assertEqual(result["symbols_with_events"], 1)
        self.assertEqual(result["missing_reason_counts"], {"no_provider_earnings_date": 1})
        self.assertEqual(result["symbol_diagnostics"][0]["status"], "event_found")
        self.assertEqual(result["symbol_diagnostics"][1]["reason"], "no_provider_earnings_date")
        self.assertEqual(row["raw_payload"]["collection_quality"]["in_window_date_count"], 1)

    def test_yfinance_earnings_calendar_diagnostics_explain_outside_window_and_errors(self) -> None:
        from finance.data import market_intelligence as mi

        calendars = {
            "AAA": {"Earnings Date": [date(2026, 12, 30)]},
            "BBB": RuntimeError("provider unavailable"),
        }

        class FakeTicker:
            def __init__(self, symbol: str) -> None:
                value = calendars[symbol]
                if isinstance(value, Exception):
                    raise value
                self.calendar = value

        result = mi.fetch_yfinance_earnings_calendar_events(
            ["AAA", "BBB"],
            start_date="2026-05-28",
            lookahead_days=30,
            ticker_factory=FakeTicker,
        )

        self.assertEqual(result["events_found"], 0)
        self.assertEqual(result["missing_symbols"], ["AAA"])
        self.assertEqual(result["failed_symbols"], ["BBB"])
        self.assertEqual(result["missing_reason_counts"], {"outside_window": 1})
        self.assertEqual(result["failed_reason_counts"], {"provider_error": 1})
        self.assertEqual(result["symbol_diagnostics"][0]["provider_dates"], ["2026-12-30"])
        self.assertEqual(result["symbol_diagnostics"][1]["detail"], "provider unavailable")

    def test_yfinance_earnings_calendar_can_cross_check_nasdaq_source(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeTicker:
            def __init__(self, symbol: str) -> None:
                self.calendar = {"Earnings Date": [date(2026, 7, 30)]}

        def fake_nasdaq_fetcher(dates, **kwargs):
            del kwargs
            self.assertEqual(dates, ["2026-07-30"])
            return {
                "2026-07-30": {
                    "symbols": ["AAA", "MSFT"],
                    "source": mi.NASDAQ_EARNINGS_CALENDAR_SOURCE,
                    "source_url": "https://api.nasdaq.test/calendar?date=2026-07-30",
                    "status": "ok",
                }
            }

        result = mi.fetch_yfinance_earnings_calendar_events(
            ["AAA"],
            start_date="2026-05-28",
            lookahead_days=120,
            validate_with_nasdaq=True,
            nasdaq_fetcher=fake_nasdaq_fetcher,
            ticker_factory=FakeTicker,
        )

        row = result["events"][0]
        self.assertEqual(result["validation_source"], mi.NASDAQ_EARNINGS_CALENDAR_SOURCE)
        self.assertEqual(row["validation_status"], "cross_checked")
        self.assertEqual(row["confidence"], 0.75)
        self.assertTrue(row["raw_payload"]["source_validation"]["fallback_order"][1]["matched"])

    def test_collect_earnings_calendar_writes_event_rows(self) -> None:
        from finance.data import market_intelligence as mi

        captured_rows: list[dict[str, object]] = []

        def capture_rows(rows, **kwargs):
            del kwargs
            captured_rows.extend(rows)
            return len(rows)

        def fake_fetcher(symbols, **kwargs):
            self.assertEqual(symbols, ["AAA", "BBB"])
            self.assertEqual(kwargs["lookahead_days"], 90)
            return {
                "source": mi.EARNINGS_CALENDAR_SOURCE,
                "source_url": mi.EARNINGS_CALENDAR_SOURCE_URL,
                "event_type": "EARNINGS",
                "method": "yfinance_ticker_calendar",
                "start_date": "2026-05-28",
                "end_date": "2026-08-26",
                "symbols_requested": 2,
                "symbols_processed": 2,
                "events": [
                    {
                        "event_date": "2026-07-30",
                        "event_type": "EARNINGS",
                        "symbol": "AAA",
                        "title": "AAA Earnings Release",
                        "source": mi.EARNINGS_CALENDAR_SOURCE,
                        "source_type": "provider_estimate",
                        "validation_status": "estimate_only",
                        "source_url": "https://finance.yahoo.com/quote/AAA/analysis",
                        "confidence": 0.65,
                        "raw_payload": {"provider": mi.EARNINGS_CALENDAR_SOURCE},
                    }
                ],
                "events_found": 1,
                "missing_symbols": ["BBB"],
                "failed_symbols": [],
            }

        with (
            patch.object(mi, "upsert_market_event_rows", side_effect=capture_rows),
            patch.object(mi, "mark_superseded_earnings_events", return_value=0),
            patch.object(mi, "mark_stale_earnings_estimates", return_value=0),
        ):
            result = mi.collect_and_store_earnings_calendar(
                symbols=["AAA", "BBB"],
                lookahead_days=90,
                earnings_fetcher=fake_fetcher,
            )

        self.assertEqual(result["source"], mi.EARNINGS_CALENDAR_SOURCE)
        self.assertEqual(result["event_type"], "EARNINGS")
        self.assertEqual(result["symbol_source"], "manual")
        self.assertEqual(result["events_found"], 1)
        self.assertEqual(result["rows_written"], 1)
        self.assertEqual(result["event_dates"], ["2026-07-30"])
        self.assertEqual(result["missing_symbols"], ["BBB"])
        self.assertEqual(result["superseded_rows_marked"], 0)
        self.assertEqual(result["stale_rows_marked"], 0)
        self.assertEqual(captured_rows[0]["collected_at"], result["collected_at"])

    def test_resolve_earnings_collection_symbols_supports_universe_batches(self) -> None:
        from finance.data import market_intelligence as mi

        symbols, source = mi.resolve_earnings_collection_symbols(
            symbol_source="top1000",
            max_symbols=2,
            batch_offset=1,
            source_symbols_loader=lambda: ["AAA", "BBB", "CCC", "DDD"],
        )

        self.assertEqual(source, "top1000")
        self.assertEqual(symbols, ["BBB", "CCC"])

    def test_mark_superseded_earnings_events_marks_prior_active_rows(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeDb:
            def __init__(self) -> None:
                self.used_dbs: list[str] = []
                self.queries: list[tuple[str, list[object]]] = []
                self.executes: list[tuple[str, list[object]]] = []
                self.closed = False

            def use_db(self, db_name: str) -> None:
                self.used_dbs.append(db_name)

            def query(self, sql: str, params=None):
                self.queries.append((sql, list(params or [])))
                return [{"event_key": "old-key"}]

            def execute(self, sql: str, params=None) -> None:
                self.executes.append((sql, list(params or [])))

            def close(self) -> None:
                self.closed = True

        fake_db = FakeDb()
        with (
            patch.object(mi, "_db", return_value=fake_db),
            patch.object(mi, "sync_table_schema") as sync_schema,
        ):
            marked = mi.mark_superseded_earnings_events(
                [
                    {
                        "event_date": "2026-07-30",
                        "event_type": "EARNINGS",
                        "symbol": "AAA",
                        "title": "AAA Earnings Release",
                        "source": mi.EARNINGS_CALENDAR_SOURCE,
                    }
                ],
                superseded_at="2026-05-28 04:00:00",
            )

        self.assertEqual(marked, 1)
        self.assertEqual(fake_db.used_dbs, ["finance_meta"])
        sync_schema.assert_called_once()
        self.assertEqual(fake_db.executes[0][1][0], "superseded")
        self.assertEqual(fake_db.executes[0][1][-1], "old-key")
        self.assertTrue(fake_db.closed)

    def test_market_event_upsert_normalizes_payload_and_business_key(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeDb:
            def __init__(self) -> None:
                self.used_dbs: list[str] = []
                self.executemany_calls: list[tuple[str, list[dict[str, object]]]] = []
                self.closed = False

            def use_db(self, db_name: str) -> None:
                self.used_dbs.append(db_name)

            def executemany(self, sql: str, rows: list[dict[str, object]]) -> None:
                self.executemany_calls.append((sql, rows))

            def close(self) -> None:
                self.closed = True

        fake_db = FakeDb()
        with (
            patch.object(mi, "_db", return_value=fake_db),
            patch.object(mi, "sync_table_schema") as sync_schema,
        ):
            rows_written = mi.upsert_market_event_rows(
                [
                    {
                        "event_date": "2026-06-17",
                        "event_type": "fomc meeting",
                        "symbol": "",
                        "title": "FOMC Meeting",
                        "source": "federal_reserve",
                        "source_url": "https://example.test/fomc",
                        "confidence": "0.95",
                        "raw_payload": {"meeting": "June"},
                    }
                ]
            )

        self.assertEqual(rows_written, 1)
        self.assertEqual(fake_db.used_dbs, ["finance_meta"])
        sync_schema.assert_called_once()
        _, captured_rows = fake_db.executemany_calls[0]
        captured = captured_rows[0]
        self.assertEqual(captured["event_date"], "2026-06-17")
        self.assertEqual(captured["event_type"], "FOMC_MEETING")
        self.assertIsNone(captured["symbol"])
        self.assertEqual(captured["source_type"], "unknown")
        self.assertEqual(captured["validation_status"], "unknown")
        self.assertEqual(captured["event_status"], "active")
        self.assertEqual(captured["confidence"], 0.95)
        self.assertEqual(captured["raw_payload_json"], '{"meeting":"June"}')
        self.assertEqual(len(str(captured["event_key"])), 64)
        self.assertTrue(fake_db.closed)

    def test_market_intelligence_sync_includes_event_calendar_table(self) -> None:
        from finance.data import market_intelligence as mi

        class FakeDb:
            def __init__(self) -> None:
                self.used_dbs: list[str] = []

            def use_db(self, db_name: str) -> None:
                self.used_dbs.append(db_name)

            def close(self) -> None:
                pass

        dbs = [FakeDb(), FakeDb()]

        def fake_db(*args, **kwargs):
            del args, kwargs
            return dbs.pop(0)

        with (
            patch.object(mi, "_db", side_effect=fake_db),
            patch.object(mi, "sync_table_schema") as sync_schema,
        ):
            mi.sync_market_intelligence_tables()

        synced_tables = [call.args[1] for call in sync_schema.call_args_list]
        self.assertIn("market_universe_member", synced_tables)
        self.assertIn("market_event_calendar", synced_tables)
        self.assertIn("market_data_issue", synced_tables)
        self.assertIn("market_intraday_snapshot", synced_tables)


class PracticalValidationReplayServiceContractTests(unittest.TestCase):
    def test_recheck_plan_extends_to_latest_market_date(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        source = {
            "selection_source_id": "source-replay",
            "period": {"actual_start": "2020-01-31", "actual_end": "2020-12-31"},
        }

        with patch.object(replay_service, "load_latest_market_date", return_value="2021-01-08"):
            plan = replay_service.build_practical_validation_recheck_plan(source)

        self.assertEqual(plan["mode"], replay_service.RECHECK_MODE_EXTEND_TO_LATEST)
        self.assertEqual(plan["status"], "EXTENDED")
        self.assertEqual(plan["stored_period"], {"start": "2020-01-31", "end": "2020-12-31"})
        self.assertEqual(plan["requested_period"], {"start": "2020-01-31", "end": "2021-01-08"})
        self.assertEqual(plan["latest_market_date"], "2021-01-08")
        self.assertEqual(plan["extension_days"], 8)
        self.assertEqual(plan["curve_source"], "actual_runtime_latest_recheck")

    def test_recheck_plan_stored_period_does_not_query_latest_market_date(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        source = {
            "selection_source_id": "source-replay",
            "period": {"start": "2020-01-31", "end": "2020-12-31"},
        }

        with patch.object(replay_service, "load_latest_market_date") as load_latest:
            plan = replay_service.build_practical_validation_recheck_plan(
                source,
                mode=replay_service.RECHECK_MODE_STORED_PERIOD,
            )

        load_latest.assert_not_called()
        self.assertEqual(plan["mode"], replay_service.RECHECK_MODE_STORED_PERIOD)
        self.assertEqual(plan["status"], "STORED_PERIOD")
        self.assertEqual(plan["requested_period"], {"start": "2020-01-31", "end": "2020-12-31"})
        self.assertFalse(plan["uses_latest_db_date"])
        self.assertEqual(plan["curve_source"], "actual_runtime_replay")

    def test_actual_replay_returns_blocked_contract_when_source_period_is_missing(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        result = replay_service.run_practical_validation_actual_replay(
            {"selection_source_id": "source-missing-period", "components": []}
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertEqual(result["source_id"], "source-missing-period")
        self.assertEqual(result["recheck_plan"]["status"], "BLOCKED")
        self.assertEqual(result["period_coverage"]["status"], "BLOCKED")
        self.assertEqual(result["portfolio_curve"], [])
        self.assertEqual(result["benchmark_curve"], [])


class ProviderGapCollectionServiceContractTests(unittest.TestCase):
    def _validation_result(self) -> dict[str, object]:
        return {
            "selection_source_id": "source-provider-gap",
            "provider_coverage": {
                "symbols": ["SPY", "TLT", "XYZ"],
                "symbol_weights": {"SPY": 0.6, "TLT": 0.3, "XYZ": 0.1},
                "coverage": {
                    "operability": {"missing_symbols": ["SPY", "XYZ"]},
                    "holdings": {"missing_symbols": ["SPY", "XYZ"]},
                    "exposure": {"missing_symbols": ["SPY", "XYZ"]},
                    "macro": {
                        "diagnostic_status": "REVIEW",
                        "series_count": 2,
                        "stale_count": 1,
                    },
                },
            },
        }

    def test_provider_gap_rows_and_plan_are_built_without_ui_runtime(self) -> None:
        from app.services import backtest_practical_validation as service

        verified_rows = [
            {"symbol": "SPY", "data_kind": "operability", "provider": "ishares", "parser": "factsheet"},
            {"symbol": "SPY", "data_kind": "holdings", "provider": "ishares", "parser": "holdings_csv"},
            {"symbol": "SPY", "data_kind": "exposure", "provider": "ishares", "parser": "provider_aggregate"},
        ]

        with patch.object(service, "load_etf_provider_source_map", return_value=verified_rows):
            rows = service.build_provider_gap_rows(self._validation_result())
            plan = service.build_provider_gap_collection_plan(self._validation_result())

        rows_by_symbol = {row["ETF"]: row for row in rows}
        self.assertEqual(rows_by_symbol["SPY"]["Action"], "운용성 보강, holdings/exposure 수집")
        self.assertEqual(rows_by_symbol["TLT"]["Action"], "조치 없음")
        self.assertEqual(rows_by_symbol["XYZ"]["Action"], "운용성 보강, source map 자동 탐색")
        self.assertEqual(plan["source_map_discovery"], ["XYZ"])
        self.assertEqual(plan["operability_official"], ["SPY"])
        self.assertEqual(plan["operability_bridge"], ["SPY", "XYZ"])
        self.assertEqual(plan["holdings_exposure"], ["SPY"])
        self.assertTrue(plan["macro"])
        self.assertEqual(
            service.provider_gap_state_key(self._validation_result()),
            "practical_validation_provider_gap_results_source-provider-gap",
        )

    def test_provider_gap_collection_runs_planned_jobs_and_records_history(self) -> None:
        from app.services import backtest_practical_validation as service

        first_plan = {
            "source_map_discovery": ["XYZ"],
            "source_symbols": ["SPY", "XYZ"],
            "operability_official": [],
            "operability_bridge": [],
            "holdings_exposure": [],
            "mapping_needed": [],
            "macro": False,
        }
        second_plan = {
            "source_map_discovery": [],
            "source_symbols": ["SPY", "XYZ"],
            "operability_official": ["SPY"],
            "operability_bridge": ["SPY", "XYZ"],
            "holdings_exposure": ["SPY"],
            "mapping_needed": [],
            "macro": True,
        }

        def result(job_name: str, symbols_requested: int | None = 1) -> dict[str, object]:
            return {
                "job_name": job_name,
                "status": "success",
                "rows_written": 1,
                "symbols_requested": symbols_requested,
                "failed_symbols": [],
                "message": "ok",
            }

        with (
            patch.object(
                service,
                "build_provider_gap_collection_plan",
                side_effect=[first_plan, second_plan],
            ) as build_plan,
            patch.object(
                service,
                "run_discover_etf_provider_source_map",
                return_value=result("discover"),
            ) as discover,
            patch.object(
                service,
                "run_collect_etf_operability_provider",
                side_effect=[result("operability_official"), result("operability_bridge", 2)],
            ) as operability,
            patch.object(
                service,
                "run_collect_etf_holdings_exposure",
                return_value=result("holdings_exposure"),
            ) as holdings,
            patch.object(
                service,
                "run_collect_macro_market_context",
                return_value=result("macro", None),
            ) as macro,
            patch.object(service, "append_run_history") as append_history,
        ):
            results = service.run_provider_gap_collection(self._validation_result())

        self.assertEqual(build_plan.call_count, 2)
        discover.assert_called_once_with(["SPY", "XYZ"], verify=True)
        operability.assert_any_call(
            ["SPY"],
            provider="official",
            as_of_date=None,
            lookback_days=60,
            timeframe="1d",
        )
        operability.assert_any_call(
            ["SPY", "XYZ"],
            provider="db_bridge",
            as_of_date=None,
            lookback_days=60,
            timeframe="1d",
        )
        holdings.assert_called_once_with(
            ["SPY"],
            provider="official",
            as_of_date=None,
            include_provider_aggregates=True,
            refresh_mode="canonical_refresh",
        )
        macro.assert_called_once_with()
        self.assertEqual(len(results), 5)
        self.assertEqual(append_history.call_count, 5)
        provider_areas = [
            result["run_metadata"]["input_params"]["provider_area"]
            for result in results
        ]
        self.assertEqual(
            provider_areas,
            [
                "etf_provider_source_map",
                "etf_operability_official",
                "etf_operability_db_bridge",
                "etf_holdings_exposure",
                "macro_context",
            ],
        )
        self.assertTrue(
            all(
                result["run_metadata"]["pipeline_type"]
                == "practical_validation_provider_gap_collection"
                for result in results
            )
        )


class ProviderContextProvenanceContractTests(unittest.TestCase):
    def test_provider_context_exposes_compact_provenance_and_downgrades_stale_pass(self) -> None:
        from app.services import backtest_practical_validation_provider_context as provider_context

        operability = pd.DataFrame(
            [
                {
                    "symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "expense_ratio": 0.0009,
                    "net_assets": 500_000_000_000,
                    "avg_daily_dollar_volume": 3_000_000_000,
                    "bid_ask_spread_pct": 0.0001,
                    "premium_discount_pct": 0.0002,
                },
                {
                    "symbol": "TLT",
                    "as_of_date": "2026-03-01",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-03-02",
                    "expense_ratio": 0.0015,
                    "net_assets": 50_000_000_000,
                    "avg_daily_dollar_volume": 500_000_000,
                    "bid_ask_spread_pct": 0.0002,
                    "premium_discount_pct": 0.0001,
                },
            ]
        )
        holdings = pd.DataFrame(
            [
                {
                    "fund_symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "holding_id": "AAPL",
                    "holding_symbol": "AAPL",
                    "holding_name": "Apple Inc",
                    "weight_pct": 5.0,
                },
                {
                    "fund_symbol": "TLT",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "holding_id": "UST",
                    "holding_symbol": "UST",
                    "holding_name": "US Treasury",
                    "weight_pct": 5.0,
                },
            ]
        )
        exposure = pd.DataFrame(
            [
                {
                    "fund_symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "exposure_type": "asset_class",
                    "exposure_name": "Equity",
                    "weight_pct": 100.0,
                },
                {
                    "fund_symbol": "TLT",
                    "as_of_date": "2026-05-20",
                    "source": "ishares",
                    "source_type": "official",
                    "coverage_status": "actual",
                    "collected_at": "2026-05-21",
                    "exposure_type": "asset_class",
                    "exposure_name": "Treasury Bond",
                    "weight_pct": 100.0,
                },
            ]
        )
        macro = pd.DataFrame(
            [
                {
                    "series_id": "VIXCLS",
                    "observation_date": "2026-05-27",
                    "source": "fred",
                    "source_type": "official",
                    "source_mode": "csv",
                    "coverage_status": "actual",
                    "value": 18.0,
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                    "collected_at": "2026-05-28",
                },
                {
                    "series_id": "T10Y3M",
                    "observation_date": "2026-05-27",
                    "source": "fred",
                    "source_type": "official",
                    "source_mode": "csv",
                    "coverage_status": "actual",
                    "value": 0.7,
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                    "collected_at": "2026-05-28",
                },
                {
                    "series_id": "BAA10Y",
                    "observation_date": "2026-05-27",
                    "source": "fred",
                    "source_type": "official",
                    "source_mode": "csv",
                    "coverage_status": "actual",
                    "value": 2.0,
                    "staleness_days": 1,
                    "snapshot_status": "actual",
                    "collected_at": "2026-05-28",
                },
            ]
        )

        with (
            patch.object(provider_context, "load_etf_operability_snapshot", return_value=operability),
            patch.object(provider_context, "load_etf_holdings_snapshot", return_value=holdings),
            patch.object(provider_context, "load_etf_exposure_snapshot", return_value=exposure),
            patch.object(provider_context, "load_macro_snapshot", return_value=macro),
        ):
            context = provider_context.build_provider_context(
                {"SPY": 70.0, "TLT": 30.0},
                as_of_date="2026-05-28",
                max_provider_staleness_days=45,
                max_macro_staleness_days=10,
            )

        self.assertEqual(context["schema_version"], 2)
        operability_context = context["coverage"]["operability"]
        provenance = operability_context["provenance"]
        self.assertEqual(operability_context["status"], "actual")
        self.assertEqual(operability_context["diagnostic_status"], "REVIEW")
        self.assertEqual(operability_context["metrics"]["review_count"], 0)
        self.assertEqual(operability_context["metrics"]["min_net_assets"], 50_000_000_000)
        self.assertEqual(operability_context["metrics"]["min_avg_daily_dollar_volume"], 500_000_000)
        self.assertEqual(operability_context["metrics"]["max_bid_ask_spread_pct"], 0.0002)
        self.assertEqual(provenance["freshness_status"], "stale")
        self.assertEqual(provenance["stale_symbols"], ["TLT"])
        self.assertEqual(provenance["stale_weight"], 30.0)
        self.assertEqual(provenance["source_type_weights"], {"official": 100.0})
        self.assertEqual(provenance["coverage_status_weights"], {"actual": 100.0})
        self.assertEqual(provenance["as_of_range"], "2026-03-01..2026-05-20")

        board = context["look_through_board"]
        self.assertEqual(board["schema_version"], "look_through_board_v1")
        self.assertEqual(board["status"], "PASS")
        self.assertEqual(board["holdings_coverage_weight"], 100.0)
        self.assertEqual(board["exposure_coverage_weight"], 100.0)
        self.assertEqual(board["top_holding_weight"], 3.5)
        self.assertEqual(board["dominant_asset_bucket"], "equity")
        self.assertEqual(board["dominant_asset_weight"], 70.0)
        asset_rows_by_bucket = {row["Asset Bucket"]: row for row in board["asset_bucket_rows"]}
        self.assertEqual(asset_rows_by_bucket["equity"]["Portfolio Weight"], 70.0)
        self.assertEqual(asset_rows_by_bucket["bond"]["Portfolio Weight"], 30.0)
        fund_rows_by_symbol = {row["Symbol"]: row for row in board["fund_coverage_rows"]}
        self.assertEqual(fund_rows_by_symbol["SPY"]["Holdings Freshness"], "fresh")
        self.assertEqual(fund_rows_by_symbol["TLT"]["Exposure Coverage"], "actual")

        rows_by_area = {row["Area"]: row for row in context["display_rows"]}
        self.assertEqual(rows_by_area["ETF Operability"]["Freshness"], "stale")
        self.assertEqual(rows_by_area["ETF Operability"]["Source Mix"], "official 100.0%")
        self.assertEqual(rows_by_area["Macro Context"]["Freshness"], "fresh")
        self.assertIn("fred/csv", rows_by_area["Macro Context"]["Source Mix"])

    def test_provider_context_keeps_bridge_liquidity_evidence_in_review(self) -> None:
        from app.services import backtest_practical_validation_provider_context as provider_context

        operability = pd.DataFrame(
            [
                {
                    "symbol": "SPY",
                    "as_of_date": "2026-05-20",
                    "source": "local_db_bridge",
                    "source_type": "database_bridge",
                    "coverage_status": "bridge",
                    "collected_at": "2026-05-21",
                    "expense_ratio": 0.0009,
                    "net_assets": 500_000_000_000,
                    "avg_daily_dollar_volume": 3_000_000_000,
                    "bid_ask_spread_pct": 0.0001,
                    "premium_discount_pct": 0.0002,
                }
            ]
        )

        with (
            patch.object(provider_context, "load_etf_operability_snapshot", return_value=operability),
            patch.object(provider_context, "load_etf_holdings_snapshot", return_value=pd.DataFrame()),
            patch.object(provider_context, "load_etf_exposure_snapshot", return_value=pd.DataFrame()),
            patch.object(provider_context, "load_macro_snapshot", return_value=pd.DataFrame()),
        ):
            context = provider_context.build_provider_context(
                {"SPY": 100.0},
                as_of_date="2026-05-28",
                max_provider_staleness_days=45,
                max_macro_staleness_days=10,
            )

        operability_context = context["coverage"]["operability"]
        self.assertEqual(operability_context["status"], "bridge")
        self.assertEqual(operability_context["diagnostic_status"], "REVIEW")
        self.assertEqual(operability_context["provenance"]["source_type_weights"], {"database_bridge": 100.0})
        self.assertEqual(operability_context["metrics"]["review_count"], 0)


class FinalReviewEvidenceReadModelContractTests(unittest.TestCase):
    def _integrated_gate_ready_validation(self) -> dict:
        return {
            "selection_source_id": "source-integrated-ready",
            "validation_id": "validation-integrated-ready",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
            "source_traits": {"is_weighted_mix": True},
            "diagnostic_summary": {
                "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
            },
            "checks": [
                {"Criteria": "Data Trust", "Ready": True, "Current": "PASS"},
                {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
            ],
            "provider_coverage": {
                "coverage": {
                    "holdings": {"diagnostic_status": "PASS"},
                    "operability": {"diagnostic_status": "PASS"},
                    "exposure": {"diagnostic_status": "PASS"},
                }
            },
            "diagnostic_results": [],
            "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
            "validation_efficacy_audit": self._gate_audit(
                route="VALIDATION_EFFICACY_READY",
                label="Ready",
                criteria="Runtime replay evidence",
                status="PASS",
                ready=True,
                current="PASS",
                meaning="runtime replay attached",
            ),
            "data_coverage_audit": self._gate_audit(
                route="DATA_COVERAGE_READY",
                label="Ready",
                criteria="Price DB window coverage",
                status="PASS",
                ready=True,
                current="100.0% / symbols=2",
                meaning="data coverage attached",
            ),
            "construction_risk_audit": self._gate_audit(
                route="CONSTRUCTION_RISK_READY",
                label="Ready",
                criteria="Provider look-through coverage",
                status="PASS",
                ready=True,
                current="holdings 100.0% / exposure 100.0%",
                meaning="construction risk evidence attached",
            ),
            "risk_contribution_audit": self._gate_audit(
                route="RISK_CONTRIBUTION_READY",
                label="Ready",
                criteria="Risk contribution concentration",
                status="PASS",
                ready=True,
                current="max 35.0%",
                meaning="risk contribution evidence attached",
            ),
            "component_role_weight_audit": self._gate_audit(
                route="COMPONENT_ROLE_WEIGHT_READY",
                label="Ready",
                criteria="Component role source coverage",
                status="PASS",
                ready=True,
                current="explicit role weight 100.0%",
                meaning="component role and weight evidence attached",
            ),
            "backtest_realism_audit": self._gate_audit(
                route="BACKTEST_REALISM_READY",
                label="Ready",
                criteria="Transaction cost model",
                status="PASS",
                ready=True,
                current="10 bps / net curve applied",
                meaning="realism evidence attached",
            ),
        }

    def _gate_audit(
        self,
        *,
        route: str,
        label: str,
        criteria: str,
        status: str,
        ready: bool,
        current: str,
        meaning: str,
    ) -> dict:
        return {
            "route": route,
            "route_label": label,
            "rows": [
                {
                    "Criteria": criteria,
                    "Status": status,
                    "Ready": ready,
                    "Current": current,
                    "Meaning": meaning,
                }
            ],
        }

    def _construction_gate_ready_audits(self) -> dict:
        return {
            "construction_risk_audit": self._gate_audit(
                route="CONSTRUCTION_RISK_READY",
                label="Ready",
                criteria="Provider look-through coverage",
                status="PASS",
                ready=True,
                current="holdings 100.0% / exposure 100.0%",
                meaning="construction risk evidence attached",
            ),
            "risk_contribution_audit": self._gate_audit(
                route="RISK_CONTRIBUTION_READY",
                label="Ready",
                criteria="Risk contribution concentration",
                status="PASS",
                ready=True,
                current="max 35.0%",
                meaning="risk contribution evidence attached",
            ),
            "component_role_weight_audit": self._gate_audit(
                route="COMPONENT_ROLE_WEIGHT_READY",
                label="Ready",
                criteria="Component role source coverage",
                status="PASS",
                ready=True,
                current="explicit role weight 100.0%",
                meaning="component role and weight evidence attached",
            ),
        }

    def _gate_policy_severities(self, packet: dict) -> dict:
        gate_policy = dict(packet.get("gate_policy_snapshot") or {})
        return {
            row.get("Group"): row.get("Severity")
            for row in list(gate_policy.get("policy_rows") or [])
        }

    def test_status_display_uses_current_decision_routes(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_status_display

        selected = build_final_review_status_display(
            {"decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO"}
        )
        rejected = build_final_review_status_display({"decision_route": "REJECT_FOR_PRACTICAL_USE"})

        self.assertEqual(selected["route"], "FINAL_REVIEW_DECISION_COMPLETE")
        self.assertIn("next_action", selected)
        self.assertEqual(rejected["route"], "FINAL_REVIEW_REJECTED")

    def test_status_display_keeps_legacy_handoff_route_as_fallback(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_status_display

        status = build_final_review_status_display(
            {"phase35_handoff": {"handoff_route": "LEGACY_COMPLETE"}}
        )

        self.assertEqual(status["route"], "LEGACY_COMPLETE")
        self.assertIn("next_action", status)

    def test_decision_display_rows_keep_table_contract(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_decision_display_rows,
        )

        rows = build_final_review_decision_display_rows(
            [
                {
                    "updated_at": "2026-05-20T10:00:00",
                    "decision_id": "decision-1",
                    "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "source_type": "proposal",
                    "source_id": "proposal-1",
                    "selected_components": [{"ticker": "SPY"}, {"ticker": "TLT"}],
                    "decision_evidence_snapshot": {"route": "READY", "score": 92},
                }
            ]
        )

        self.assertEqual(len(rows), 1)
        row = rows[0]
        self.assertEqual(row["Updated At"], "2026-05-20T10:00:00")
        self.assertEqual(row["Decision ID"], "decision-1")
        self.assertEqual(row["Source"], "proposal / proposal-1")
        self.assertEqual(row["Components"], 2)
        self.assertEqual(row["Evidence Route"], "READY")
        self.assertEqual(row["Evidence Score"], 92)
        self.assertEqual(row["판단 라벨"], "모니터링 후보 선정")
        self.assertEqual(row["Final Status"], "FINAL_REVIEW_DECISION_COMPLETE")
        self.assertEqual(row["Live Approval"], "Disabled")

    def test_saved_final_review_decision_review_summarizes_and_sorts_records(self) -> None:
        from app.services.backtest_evidence_read_model import build_saved_final_review_decision_review

        rows = [
            {
                "decision_id": "decision-hold",
                "updated_at": "2026-05-20T10:00:00",
                "decision_route": "HOLD_FOR_MORE_PAPER_TRACKING",
                "source_type": "practical_validation_result",
                "source_id": "validation-hold",
                "selected_components": [],
                "decision_evidence_snapshot": {"route": "READY_FOR_FINAL_DECISION", "score": 7.2},
                "operator_decision": {"reason": "more observation", "next_action": "paper tracking"},
                "investability_evidence_packet": {
                    "route": "INVESTABILITY_PACKET_REVIEW",
                    "gate_policy_snapshot": {
                        "outcome": "hold_or_re_review",
                        "select_allowed": False,
                        "review_required": ["Backtest realism review"],
                    },
                },
            },
            {
                "decision_id": "decision-selected",
                "updated_at": "2026-05-22T10:00:00",
                "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                "source_type": "practical_validation_result",
                "source_id": "validation-selected",
                "selected_components": [{"ticker": "SPY"}, {"ticker": "TLT"}],
                "decision_evidence_snapshot": {"route": "READY_FOR_FINAL_DECISION", "score": 8.8},
                "operator_decision": {"reason": "ready", "next_action": "dashboard recheck"},
                "investability_evidence_packet": {
                    "route": "INVESTABILITY_PACKET_READY",
                    "gate_policy_snapshot": {
                        "outcome": "select_ready",
                        "select_allowed": True,
                        "blockers": [],
                        "review_required": [],
                    },
                },
            },
            {
                "decision_id": "decision-reject",
                "updated_at": "2026-05-21T10:00:00",
                "decision_route": "REJECT_FOR_PRACTICAL_USE",
                "source_type": "practical_validation_result",
                "source_id": "validation-reject",
                "decision_evidence_snapshot": {"route": "REVIEW_REQUIRED", "score": 4.1, "blockers": ["missing data"]},
                "operator_decision": {"reason": "reject"},
            },
        ]

        review = build_saved_final_review_decision_review(rows)

        self.assertEqual(review["schema_version"], "final_review_saved_decision_review_v1")
        self.assertEqual(review["summary"]["total_records"], 3)
        self.assertEqual(review["summary"]["selected"], 1)
        self.assertEqual(review["summary"]["hold"], 1)
        self.assertEqual(review["summary"]["reject"], 1)
        self.assertEqual(review["summary"]["dashboard_eligible"], 1)
        self.assertEqual(review["summary"]["latest_decision_id"], "decision-selected")
        self.assertFalse(review["summary"]["live_approval"])
        self.assertIn("All", review["filter_options"])
        self.assertEqual(review["rows"][0]["Decision ID"], "decision-selected")
        self.assertEqual(review["rows"][0]["Route Family"], "Selected")
        self.assertEqual(review["rows"][0]["Dashboard Eligible"], "Yes")
        self.assertEqual(review["rows"][1]["Decision ID"], "decision-reject")
        self.assertEqual(review["rows"][2]["Evidence Issues"], 1)

    def test_final_review_decision_cockpit_summarizes_selected_route_state(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_candidate_board_rows,
            build_final_review_decision_cockpit,
            build_investability_evidence_packet,
        )

        validation = self._integrated_gate_ready_validation()
        source = {
            "source_type": "practical_validation_result",
            "source_id": validation["validation_id"],
            "source_title": "Ready candidate",
        }
        paper = {
            "route": "PAPER_OBSERVATION_READY",
            "blockers": [],
            "review_cadence": "monthly_or_rebalance_review",
            "tracking_benchmark": "SPY",
            "review_triggers": ["CAGR deterioration review"],
            "active_components": [{"title": "Ready component", "target_weight": 100.0}],
            "baseline_snapshot": {"target_weight_total": 100.0},
        }
        evidence = {"route": "READY_FOR_FINAL_DECISION", "blockers": []}
        packet = build_investability_evidence_packet(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
        )

        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
            investability_packet=packet,
        )
        board_rows = build_final_review_candidate_board_rows(
            [
                {
                    "source": source,
                    "validation": validation,
                    "paper_observation": paper,
                    "decision_evidence": evidence,
                    "investability_packet": packet,
                }
            ]
        )

        self.assertEqual(cockpit["schema_version"], "final_review_decision_cockpit_v1")
        self.assertEqual(cockpit["state"], "SELECT_READY")
        self.assertTrue(cockpit["select_allowed"])
        self.assertEqual(cockpit["suggested_decision_route"], "SELECT_FOR_PRACTICAL_PORTFOLIO")
        self.assertEqual(cockpit["monitoring_handoff"]["tracking_benchmark"], "SPY")
        self.assertEqual(board_rows[0]["Decision State"], "모니터링 후보 가능")
        self.assertEqual(board_rows[0]["Select Allowed"], "Yes")
        self.assertEqual(board_rows[0]["Open Review"], 0)
        self.assertEqual(board_rows[0]["Candidate"], "Ready candidate")

    def test_final_review_decision_cockpit_surfaces_blocked_candidate_board_row(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_candidate_board_rows,
            build_final_review_decision_cockpit,
            build_investability_evidence_packet,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_id"] = "validation-blocked"
        validation["not_run_critical_domains"] = [
            {
                "domain": "stress_scenario_diagnostics",
                "title": "Stress scenario diagnostics",
                "next_action": "Run stress diagnostics before selection.",
            }
        ]
        validation["diagnostic_summary"]["status_counts"]["NOT_RUN"] = 1
        source = {
            "source_type": "practical_validation_result",
            "source_id": "validation-blocked",
            "source_title": "Blocked candidate",
        }
        paper = {"route": "PAPER_OBSERVATION_READY", "blockers": []}
        evidence = {"route": "READY_FOR_FINAL_DECISION", "blockers": []}
        packet = build_investability_evidence_packet(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
        )

        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper,
            decision_evidence=evidence,
            investability_packet=packet,
        )
        board_rows = build_final_review_candidate_board_rows(
            [
                {
                    "source": source,
                    "validation": validation,
                    "paper_observation": paper,
                    "decision_evidence": evidence,
                    "investability_packet": packet,
                }
            ]
        )

        self.assertEqual(cockpit["state"], "SELECT_BLOCKED")
        self.assertFalse(cockpit["select_allowed"])
        self.assertGreaterEqual(len(cockpit["must_fix_rows"]), 1)
        self.assertEqual(board_rows[0]["Decision State"], "선정 차단")
        self.assertEqual(board_rows[0]["Select Allowed"], "No")
        self.assertGreaterEqual(board_rows[0]["Blockers"], 1)
        self.assertEqual(board_rows[0]["NOT_RUN"], 1)

    def test_final_review_candidate_board_prioritizes_ready_candidates(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_candidate_board

        def candidate(label: str, outcome: str, score: float, *, blockers: int = 0, reviews: int = 0) -> dict:
            policy_rows = []
            policy_blockers = [
                "Risk Contribution: drop-one dependency missing",
            ][:blockers]
            policy_reviews = [
                "Backtest Realism: tax/account scope review",
            ][:reviews]
            if blockers:
                policy_rows.append(
                    {
                        "Criteria": "Risk Contribution",
                        "Severity": "BLOCK",
                        "Required Action": "drop-one dependency evidence를 보강합니다.",
                    }
                )
            if reviews:
                policy_rows.append(
                    {
                        "Criteria": "Backtest Realism",
                        "Severity": "REVIEW_REQUIRED",
                        "Required Action": "세금 / 계좌 scope를 최종 판단 전에 확인합니다.",
                    }
                )
            suggested = (
                "SELECT_FOR_PRACTICAL_PORTFOLIO"
                if outcome == "select_ready"
                else "RE_REVIEW_REQUIRED"
                if outcome == "blocked"
                else "HOLD_FOR_MORE_PAPER_TRACKING"
            )
            return {
                "source": {"source_title": label, "source_type": "practical_validation_result"},
                "validation": {"validation_id": f"validation-{label.lower()}"},
                "paper_observation": {"route": "PAPER_OBSERVATION_READY", "blockers": []},
                "decision_evidence": {"route": "READY_FOR_FINAL_DECISION", "blockers": []},
                "investability_packet": {
                    "route": "INVESTABILITY_PACKET_READY" if outcome == "select_ready" else "INVESTABILITY_PACKET_REVIEW",
                    "score": score,
                    "summary": {"not_run": 0, "review": reviews, "blocked": blockers},
                    "source_chain": {"validation_id": f"validation-{label.lower()}", "selection_source_id": f"source-{label.lower()}"},
                    "gate_policy_snapshot": {
                        "outcome": outcome,
                        "select_allowed": outcome == "select_ready",
                        "suggested_decision_route": suggested,
                        "blockers": policy_blockers,
                        "review_required": policy_reviews,
                        "policy_rows": policy_rows,
                    },
                },
            }

        board = build_final_review_candidate_board(
            [
                candidate("Blocked", "blocked", 6.1, blockers=1),
                candidate("Hold", "hold_or_re_review", 7.2, reviews=1),
                candidate("Ready", "select_ready", 8.8),
            ]
        )

        rows = board["rows"]
        self.assertEqual(board["schema_version"], "final_review_candidate_board_v1")
        self.assertEqual(board["summary"]["total_candidates"], 3)
        self.assertEqual(board["summary"]["select_ready"], 1)
        self.assertEqual(board["summary"]["hold_or_re_review"], 1)
        self.assertEqual(board["summary"]["blocked"], 1)
        self.assertEqual(rows[0]["Candidate"], "Ready")
        self.assertEqual(rows[0]["Review Priority"], "P1")
        self.assertEqual(rows[0]["Board Action"], "모니터링 후보 선정")
        self.assertEqual(rows[1]["Candidate"], "Hold")
        self.assertEqual(rows[2]["Candidate"], "Blocked")
        self.assertEqual(board["review_queue_rows"][0]["Action"], "모니터링 후보 선정")

    def test_final_review_decision_record_guide_blocks_selected_route_when_gate_blocks(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_final_review_decision_record_guide,
        )

        packet = {
            "route": "INVESTABILITY_PACKET_BLOCKED",
            "select_ready": False,
            "gate_policy_snapshot": {
                "outcome": "blocked",
                "select_allowed": False,
                "suggested_decision_route": "RE_REVIEW_REQUIRED",
                "blockers": ["Risk Contribution: missing drop-one dependency"],
                "review_required": [],
                "policy_rows": [
                    {
                        "Criteria": "Risk Contribution",
                        "Severity": "BLOCK",
                        "Required Action": "drop-one dependency evidence를 보강합니다.",
                    }
                ],
            },
        }

        guide = build_final_review_decision_record_guide(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            decision_evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=packet,
        )

        self.assertEqual(guide["schema_version"], "final_review_decision_record_guide_v1")
        self.assertEqual(guide["route_state"], "SELECT_ROUTE_BLOCKED")
        self.assertFalse(guide["recordable_route"])
        self.assertFalse(guide["selected_route_gate"]["Ready"])
        self.assertEqual(guide["suggested_decision_route"], "RE_REVIEW_REQUIRED")
        self.assertIn("Investability evidence packet", guide["blockers"])
        self.assertFalse(guide["record_boundary"]["live_approval"])

    def test_final_review_decision_record_guide_treats_non_select_route_as_status_only(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_decision_record_guide

        packet = {
            "route": "INVESTABILITY_PACKET_BLOCKED",
            "select_ready": False,
            "gate_policy_snapshot": {
                "outcome": "blocked",
                "select_allowed": False,
                "suggested_decision_route": "RE_REVIEW_REQUIRED",
                "blockers": ["Data Coverage: survivorship evidence missing"],
                "review_required": [],
            },
        }

        guide = build_final_review_decision_record_guide(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            decision_evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=packet,
        )

        self.assertEqual(guide["route_state"], "NON_SELECT_NOT_STORED")
        self.assertFalse(guide["recordable_route"])
        self.assertTrue(guide["selected_route_gate"]["Ready"])
        self.assertIn("Official selection route", guide["blockers"])
        self.assertIn("paper tracking", guide["route_templates"]["reason"])
        self.assertFalse(guide["record_boundary"]["non_select_persistence"])
        self.assertFalse(guide["record_boundary"]["waiver_persistence"])

    def test_evidence_rows_expand_current_and_wrapped_decision_shapes(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_decision_evidence_rows

        decision = {
            "decision_evidence_snapshot": {
                "checks": [
                    {
                        "criteria": "Evidence route",
                        "ready": True,
                        "current": "READY",
                        "meaning": "Reusable final review evidence",
                        "score": 1,
                    }
                ]
            },
            "risk_and_validation_snapshot": {
                "validation_checks": [
                    {
                        "Criteria": "Validation status",
                        "Ready": False,
                        "Current": "REVIEW",
                    }
                ],
                "validation_efficacy_audit": {
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "NOT_RUN",
                            "Meaning": "runtime replay gap",
                        }
                    ]
                },
                "data_coverage_audit": {
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "80.0% / symbols=2",
                            "Meaning": "price coverage gap",
                        }
                    ]
                },
                "backtest_realism_audit": {
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "10 bps / assumption only",
                            "Meaning": "cost model gap",
                        }
                    ]
                },
                "provider_look_through_board": {
                    "summary_rows": [
                        {
                            "Check": "Holdings Coverage",
                            "Status": "PASS",
                            "Current": "100.0%",
                            "Evidence": "fresh / official 100.0% / 2026-05-20",
                            "Meaning": "holdings coverage compact summary",
                        }
                    ]
                },
                "robustness_validation": {
                    "robustness_lab_board": {
                        "summary_rows": [
                            {
                                "Check": "Sensitivity coverage",
                                "Status": "REVIEW",
                                "Current": "computed 3 / review 1 / runtime follow-up 1",
                                "Evidence": "compact robustness lab summary",
                                "Meaning": "sensitivity coverage compact summary",
                            }
                        ]
                    },
                    "checks": [{"criteria": "Robustness status", "current_value": "WATCH"}]
                },
            },
            "paper_tracking_snapshot": {
                "checks": [{"criteria": "Paper status", "current": "OPTIONAL"}]
            },
        }

        rows = build_final_decision_evidence_rows({"raw_decision": decision})

        self.assertEqual(
            [row["Area"] for row in rows],
            [
                "Final Review Evidence",
                "Validation",
                "Validation Efficacy",
                "Data Coverage",
                "Backtest Realism",
                "Look-through Exposure",
                "Robustness Lab",
                "Robustness",
                "Paper Observation",
            ],
        )
        self.assertEqual(rows[0]["Criteria"], "Evidence route")
        self.assertTrue(rows[0]["Ready"])
        self.assertEqual(rows[1]["Current"], "REVIEW")
        self.assertEqual(rows[2]["Criteria"], "Runtime replay evidence")
        self.assertFalse(rows[2]["Ready"])
        self.assertEqual(rows[3]["Criteria"], "Price DB window coverage")
        self.assertFalse(rows[3]["Ready"])
        self.assertEqual(rows[4]["Criteria"], "Transaction cost model")
        self.assertFalse(rows[4]["Ready"])
        self.assertEqual(rows[5]["Criteria"], "Holdings Coverage")
        self.assertTrue(rows[5]["Ready"])
        self.assertEqual(rows[6]["Criteria"], "Sensitivity coverage")
        self.assertFalse(rows[6]["Ready"])
        self.assertEqual(rows[7]["Current"], "WATCH")
        self.assertEqual(rows[8]["Current"], "OPTIONAL")

    def test_investability_packet_ready_contract_is_ui_neutral(self) -> None:
        from app.services.backtest_evidence_read_model import build_investability_evidence_packet

        validation = {
            "selection_source_id": "source-ready",
            "validation_id": "validation-ready",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "diagnostic_summary": {"status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}},
            "checks": [
                {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
            ],
            "provider_coverage": {
                "coverage": {
                    "holdings": {"diagnostic_status": "PASS"},
                    "operability": {"diagnostic_status": "PASS"},
                }
            },
            "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
            "validation_efficacy_audit": {
                "route": "VALIDATION_EFFICACY_READY",
                "route_label": "Ready",
                "rows": [
                    {
                        "Criteria": "Runtime replay evidence",
                        "Status": "PASS",
                        "Ready": True,
                        "Current": "PASS",
                        "Meaning": "runtime replay attached",
                    }
                ],
            },
            "data_coverage_audit": {
                "route": "DATA_COVERAGE_READY",
                "route_label": "Ready",
                "rows": [
                    {
                        "Criteria": "Price DB window coverage",
                        "Status": "PASS",
                        "Ready": True,
                        "Current": "100.0% / symbols=2",
                        "Meaning": "price coverage attached",
                    }
                ],
            },
            "backtest_realism_audit": {
                "route": "BACKTEST_REALISM_READY",
                "route_label": "Ready",
                "rows": [
                    {
                        "Criteria": "Transaction cost model",
                        "Status": "PASS",
                        "Ready": True,
                        "Current": "10 bps / net curve applied",
                        "Meaning": "cost model attached",
                    }
                ],
            },
        }
        validation.update(self._construction_gate_ready_audits())

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-ready"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["source_chain"]["selection_source_id"], "source-ready")
        self.assertEqual(packet["summary"]["not_run"], 0)
        self.assertEqual(packet["critical_gaps"], [])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(packet["gate_policy_snapshot"]["select_allowed"])
        sections = [row["Section"] for row in packet["checks"]]
        self.assertIn("Validation Efficacy Audit", sections)
        self.assertIn("Data Coverage Audit", sections)
        self.assertIn("Construction Risk Audit", sections)
        self.assertIn("Risk Contribution Audit", sections)
        self.assertIn("Component Role / Weight Audit", sections)
        self.assertIn("Backtest Realism Audit", sections)
        self.assertEqual(packet["summary"]["validation_efficacy_route"], "VALIDATION_EFFICACY_READY")
        self.assertEqual(packet["summary"]["data_coverage_route"], "DATA_COVERAGE_READY")
        self.assertEqual(packet["summary"]["construction_risk_route"], "CONSTRUCTION_RISK_READY")
        self.assertEqual(packet["summary"]["risk_contribution_route"], "RISK_CONTRIBUTION_READY")
        self.assertEqual(packet["summary"]["component_role_weight_route"], "COMPONENT_ROLE_WEIGHT_READY")
        self.assertEqual(packet["summary"]["backtest_realism_route"], "BACKTEST_REALISM_READY")
        assumptions = [row["Assumption"] for row in packet["assumptions_and_limits"]]
        self.assertIn("Hypothetical backtest", assumptions)
        self.assertIn("No live approval / order", assumptions)

    def test_integrated_investability_gate_all_ready_allows_selected_route(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-integrated-ready"},
            validation=self._integrated_gate_ready_validation(),
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(packet["gate_policy_snapshot"]["select_allowed"])
        self.assertFalse(packet["gate_policy_snapshot"]["waiver_supported"])
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["validation_efficacy"], "PASS")
        self.assertEqual(severities["data_coverage"], "PASS")
        self.assertEqual(severities["construction_risk"], "PASS")
        self.assertEqual(severities["risk_contribution"], "PASS")
        self.assertEqual(severities["component_role_weight"], "PASS")
        self.assertEqual(severities["backtest_realism"], "PASS")
        execution_boundary = next(row for row in packet["checks"] if row["Section"] == "Execution Boundary")
        self.assertEqual(execution_boundary["Current"], "live approval disabled / order disabled")

    def test_integrated_investability_gate_multiple_review_gaps_hold_selected_route(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["checks"][3] = {"Criteria": "Provider coverage", "Ready": True, "Current": "REVIEW"}
        validation["diagnostic_summary"] = {
            "status_counts": {"PASS": 8, "REVIEW": 4, "BLOCKED": 0, "NOT_RUN": 0}
        }
        validation["diagnostic_results"] = [
            {
                "domain": "operability_cost_liquidity",
                "title": "10. Operability / Cost / Liquidity",
                "status": "REVIEW",
                "next_action": "provider actual evidence 보강",
            }
        ]
        validation["validation_efficacy_audit"] = self._gate_audit(
            route="VALIDATION_EFFICACY_REVIEW",
            label="Review Required",
            criteria="PIT / look-ahead boundary",
            status="REVIEW",
            ready=False,
            current="needs review",
            meaning="PIT boundary needs review",
        )
        validation["data_coverage_audit"] = self._gate_audit(
            route="DATA_COVERAGE_REVIEW",
            label="Review Required",
            criteria="Survivorship / delisting control",
            status="REVIEW",
            ready=False,
            current="not proven",
            meaning="current listing is not survivorship control",
        )
        validation["backtest_realism_audit"] = self._gate_audit(
            route="BACKTEST_REALISM_REVIEW",
            label="Review Required",
            criteria="Tax / account scope",
            status="REVIEW",
            ready=False,
            current="not modeled",
            meaning="tax/account scope review",
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-integrated-review"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(packet["gate_policy_snapshot"]["blockers"], [])
        self.assertFalse(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 4)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["provider_coverage"], "WATCH")
        self.assertEqual(severities["validation_efficacy"], "WATCH")
        self.assertEqual(severities["data_coverage"], "WATCH")
        self.assertEqual(severities["backtest_realism"], "WATCH")
        self.assertTrue(
            all(
                row["Selected Route"] == "Allowed with watch"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
                if row["Severity"] == "WATCH"
            )
        )

    def test_integrated_investability_gate_multiple_blockers_block_selected_route(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_efficacy_audit"] = self._gate_audit(
            route="VALIDATION_EFFICACY_NEEDS_INPUT",
            label="Evidence Input Needed",
            criteria="Runtime replay evidence",
            status="NEEDS_INPUT",
            ready=False,
            current="NOT_RUN",
            meaning="runtime replay missing",
        )
        validation["data_coverage_audit"] = self._gate_audit(
            route="DATA_COVERAGE_NEEDS_INPUT",
            label="Coverage Input Needed",
            criteria="Price DB window coverage",
            status="NEEDS_INPUT",
            ready=False,
            current="0.0% / symbols=2",
            meaning="price coverage missing",
        )
        validation["backtest_realism_audit"] = self._gate_audit(
            route="BACKTEST_REALISM_BLOCKED",
            label="Blocked",
            criteria="Execution boundary",
            status="BLOCKED",
            ready=False,
            current="execution model invalid",
            meaning="execution assumption blocks selection",
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-integrated-blocked"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertFalse(packet["select_ready"])
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertTrue(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        severities = self._gate_policy_severities(packet)
        self.assertEqual(severities["validation_efficacy"], "BLOCK")
        self.assertEqual(severities["data_coverage"], "BLOCK")
        self.assertEqual(severities["backtest_realism"], "BLOCK")
        self.assertGreaterEqual(len(packet["gate_policy_snapshot"]["blockers"]), 3)

    def test_gate_policy_blocks_selected_route_on_construction_risk_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["construction_risk_audit"] = {
            "route": "CONSTRUCTION_RISK_NEEDS_INPUT",
            "route_label": "Evidence Input Needed",
            "rows": [
                {
                    "Criteria": "Provider look-through coverage",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "holdings 0.0% / exposure 0.0%",
                    "Meaning": "provider holdings / exposure evidence missing",
                    "Next Action": "ETF holdings / exposure provider snapshot을 먼저 보강합니다.",
                }
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "construction-risk-gap"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "construction_risk"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertIn("Provider look-through coverage", policy_row["Evidence"])
        self.assertIn("NEEDS_INPUT", policy_row["Current"])

    def test_gate_policy_requires_review_on_risk_contribution_review(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["risk_contribution_audit"] = {
            "route": "RISK_CONTRIBUTION_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Pairwise correlation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "avg 0.72 / max 0.91",
                    "Meaning": "component correlation is high",
                },
                {
                    "Criteria": "Risk contribution concentration",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "max 86.0%",
                    "Meaning": "one component dominates volatility contribution",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "risk-contribution-review"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "risk_contribution"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertIn("Pairwise correlation", policy_row["Evidence"])
        self.assertIn("Risk contribution concentration", policy_row["Evidence"])

    def test_gate_policy_blocks_selected_route_on_component_role_weight_blocked(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["component_role_weight_audit"] = {
            "route": "COMPONENT_ROLE_WEIGHT_BLOCKED",
            "route_label": "Blocked",
            "rows": [
                {
                    "Criteria": "Component role source coverage",
                    "Status": "BLOCKED",
                    "Ready": False,
                    "Current": "components 0 / explicit role weight 0.0%",
                    "Meaning": "active component role contract is unavailable",
                    "Next Action": "active component가 있는 source를 다시 선택합니다.",
                }
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "component-role-blocked"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "component_role_weight"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "BLOCK")
        self.assertIn("Component role source coverage", policy_row["Evidence"])

    def test_investability_packet_blocks_selected_route_on_critical_not_run(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-gap"},
            validation={
                "selection_source_id": "source-gap",
                "validation_id": "validation-gap",
                "diagnostic_summary": {"status_counts": {"PASS": 10, "REVIEW": 1, "BLOCKED": 0, "NOT_RUN": 1}},
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "REVIEW"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "not_run_critical_domains": [
                    {
                        "domain": "stress_scenario_diagnostics",
                        "title": "7. Stress / Scenario Diagnostics",
                        "next_action": "daily replay evidence 필요",
                    }
                ],
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )

        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertFalse(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertTrue(packet["gate_policy_snapshot"]["waiver_required_for_select"])
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])

    def test_gate_policy_blocks_selected_route_on_validation_efficacy_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-efficacy-gap"},
            validation={
                "selection_source_id": "source-efficacy-gap",
                "validation_id": "validation-efficacy-gap",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "provider_coverage": {
                    "coverage": {
                        "holdings": {"diagnostic_status": "PASS"},
                        "operability": {"diagnostic_status": "PASS"},
                    }
                },
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_NEEDS_INPUT",
                    "route_label": "Evidence Input Needed",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "NOT_RUN",
                            "Meaning": "runtime replay missing",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertFalse(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "validation_efficacy" and row["Severity"] == "BLOCK"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_surfaces_temporal_oos_and_regime_review_rows(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_efficacy_audit"] = {
            "route": "VALIDATION_EFFICACY_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Walk-forward temporal validation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "windows=6 / negative share=0.33",
                    "Meaning": "rolling excess return is unstable",
                },
                {
                    "Criteria": "OOS holdout validation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "out=12 / excess change=-0.08",
                    "Meaning": "holdout performance deteriorated",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "risk_off bucket short history",
                    "Meaning": "regime evidence needs review",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-temporal-review"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "validation_efficacy"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertIn("Walk-forward temporal validation", policy_row["Evidence"])
        self.assertIn("OOS holdout validation", policy_row["Evidence"])
        self.assertIn("Regime split validation", policy_row["Evidence"])
        self.assertIn("REVIEW", policy_row["Current"])

    def test_gate_policy_blocks_selected_route_on_temporal_oos_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["validation_efficacy_audit"] = {
            "route": "VALIDATION_EFFICACY_NEEDS_INPUT",
            "route_label": "Evidence Input Needed",
            "rows": [
                {
                    "Criteria": "OOS holdout validation",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "out_sample_months=0",
                    "Meaning": "holdout period is missing",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "macro history missing",
                    "Meaning": "regime macro evidence is missing",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-temporal-gap"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "validation_efficacy"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "BLOCK")
        self.assertIn("OOS holdout validation", policy_row["Evidence"])
        self.assertIn("Regime split validation", policy_row["Evidence"])
        self.assertIn("NEEDS_INPUT", policy_row["Current"])

    def test_gate_policy_blocks_selected_route_on_backtest_realism_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-gap"},
            validation={
                "selection_source_id": "source-realism-gap",
                "validation_id": "validation-realism-gap",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "provider_coverage": {
                    "coverage": {
                        "holdings": {"diagnostic_status": "PASS"},
                        "operability": {"diagnostic_status": "PASS"},
                    }
                },
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_NEEDS_INPUT",
                    "route_label": "Realism Input Needed",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "missing",
                            "Meaning": "cost model missing",
                        }
                    ],
                },
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertFalse(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "backtest_realism" and row["Severity"] == "BLOCK"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_blocks_selected_route_on_data_coverage_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "data-coverage-gap"},
            validation={
                "selection_source_id": "source-data-gap",
                "validation_id": "validation-data-gap",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "provider_coverage": {
                    "coverage": {
                        "holdings": {"diagnostic_status": "PASS"},
                        "operability": {"diagnostic_status": "PASS"},
                    }
                },
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_NEEDS_INPUT",
                    "route_label": "Coverage Input Needed",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "NEEDS_INPUT",
                            "Ready": False,
                            "Current": "0.0% / symbols=2",
                            "Meaning": "price coverage missing",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertFalse(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertTrue(
            any(
                row["Group"] == "data_coverage" and row["Severity"] == "BLOCK"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_requires_review_on_data_coverage_review(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "data-coverage-review"},
            validation={
                "selection_source_id": "source-data-review",
                "validation_id": "validation-data-review",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "provider_coverage": {
                    "coverage": {
                        "holdings": {"diagnostic_status": "PASS"},
                        "operability": {"diagnostic_status": "PASS"},
                    }
                },
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_REVIEW",
                    "route_label": "Review Required",
                    "rows": [
                        {
                            "Criteria": "Survivorship / delisting control",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "not proven",
                            "Meaning": "current listing is not survivorship control",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertTrue(
            any(
                row["Group"] == "data_coverage" and row["Severity"] == "WATCH"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_requires_review_on_backtest_realism_review(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-review"},
            validation={
                "selection_source_id": "source-realism-review",
                "validation_id": "validation-realism-review",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 12, "REVIEW": 0, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "provider_coverage": {
                    "coverage": {
                        "holdings": {"diagnostic_status": "PASS"},
                        "operability": {"diagnostic_status": "PASS"},
                    }
                },
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Runtime replay evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_REVIEW",
                    "route_label": "Review Required",
                    "rows": [
                        {
                            "Criteria": "Tax / account scope",
                            "Status": "REVIEW",
                            "Ready": False,
                            "Current": "not modeled",
                            "Meaning": "tax/account scope review",
                        }
                    ],
                },
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertTrue(
            any(
                row["Group"] == "backtest_realism" and row["Severity"] == "WATCH"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_gate_policy_surfaces_cost_slippage_and_liquidity_review_rows(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Cost / slippage sensitivity evidence",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "generic robustness only",
                    "Meaning": "cost / slippage axis is missing",
                    "Next Action": "비용 bps / spread / slippage 축의 sensitivity evidence를 확인합니다.",
                },
                {
                    "Criteria": "Liquidity / operability evidence",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "weak_source_or_proxy_liquidity_evidence",
                    "Meaning": "fresh official capacity evidence missing",
                },
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-sensitivity-review"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "backtest_realism"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertTrue(selected_gate["Ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(policy_row["Severity"], "WATCH")
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertIn("Cost / slippage sensitivity evidence", policy_row["Evidence"])
        self.assertIn("Liquidity / operability evidence", policy_row["Evidence"])

    def test_gate_policy_blocks_selected_route_on_cost_slippage_sensitivity_needs_input(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        validation = self._integrated_gate_ready_validation()
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_NEEDS_INPUT",
            "route_label": "Realism Input Needed",
            "rows": [
                {
                    "Criteria": "Cost / slippage sensitivity evidence",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "cost=- / net=missing_net_cost_curve_proof",
                    "Meaning": "cost input or net cost curve proof missing",
                    "Next Action": "거래비용 입력과 net cost curve proof를 먼저 보강합니다.",
                }
            ],
        }

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "backtest-realism-sensitivity-gap"},
            validation=validation,
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )
        hold_gate = build_selected_route_gate(
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            investability_packet=packet,
        )
        policy_row = next(
            row
            for row in packet["gate_policy_snapshot"]["policy_rows"]
            if row["Group"] == "backtest_realism"
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_BLOCKED")
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "blocked")
        self.assertFalse(selected_gate["Ready"])
        self.assertTrue(hold_gate["Ready"])
        self.assertEqual(policy_row["Severity"], "BLOCK")
        self.assertIn("Cost / slippage sensitivity evidence", policy_row["Evidence"])
        self.assertIn("NEEDS_INPUT", policy_row["Current"])

    def test_practical_validation_selected_route_preflight_blocks_gross_only_review(self) -> None:
        from app.services.backtest_selected_route_preflight import (
            build_practical_validation_selected_route_preflight,
        )

        validation = self._integrated_gate_ready_validation()
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Net performance policy",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "gross-only / net cost curve proof missing",
                    "Meaning": "net performance proof is required before selected-route storage",
                }
            ],
        }

        preflight = build_practical_validation_selected_route_preflight(validation)

        self.assertFalse(preflight["select_allowed"])
        self.assertEqual(preflight["policy_outcome"], "hold_or_re_review")
        self.assertEqual(preflight["route"], "SELECTED_ROUTE_PREFLIGHT_NEEDS_INPUT")
        self.assertTrue(
            any("Backtest Realism" in item for item in preflight["review_required"])
        )

    def test_selected_route_preflight_blocks_equal_weight_missing_net_cost_proof(self) -> None:
        from app.services.backtest_selected_route_preflight import (
            build_practical_validation_selected_route_preflight,
        )

        validation = self._integrated_gate_ready_validation()
        validation["source_title"] = "Equal Weight proof-deficient regression"
        validation["backtest_realism_audit"] = {
            "route": "BACKTEST_REALISM_REVIEW",
            "route_label": "Review Required",
            "rows": [
                {
                    "Criteria": "Net cost curve proof",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "not_proven / equal weight net curve missing",
                    "Meaning": "net cost curve proof is required before selected-route storage",
                },
                {
                    "Criteria": "Turnover evidence",
                    "Status": "REVIEW",
                    "Ready": False,
                    "Current": "not_estimated_missing_holdings",
                    "Meaning": "turnover proof is still missing",
                },
            ],
        }

        preflight = build_practical_validation_selected_route_preflight(validation)

        self.assertFalse(preflight["select_allowed"])
        self.assertEqual(preflight["policy_outcome"], "hold_or_re_review")
        self.assertEqual(preflight["route"], "SELECTED_ROUTE_PREFLIGHT_NEEDS_INPUT")
        self.assertTrue(any("Backtest Realism" in item for item in preflight["review_required"]))

    def test_gate_policy_blocks_selected_route_on_provider_review_for_balanced_profile(self) -> None:
        from app.services.backtest_evidence_read_model import (
            SELECT_FOR_PRACTICAL_PORTFOLIO,
            build_investability_evidence_packet,
            build_selected_route_gate,
        )

        packet = build_investability_evidence_packet(
            source={"source_type": "practical_validation_result", "source_id": "validation-provider-review"},
            validation={
                "selection_source_id": "source-provider-review",
                "validation_id": "validation-provider-review",
                "validation_profile": {"profile_id": "balanced_core", "profile_label": "균형형"},
                "diagnostic_summary": {
                    "status_counts": {"PASS": 11, "REVIEW": 1, "BLOCKED": 0, "NOT_RUN": 0}
                },
                "checks": [
                    {"Criteria": "Data Trust", "Ready": True, "Current": "ok"},
                    {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Runtime period coverage", "Ready": True, "Current": "PASS"},
                    {"Criteria": "Provider coverage", "Ready": True, "Current": "REVIEW"},
                    {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
                ],
                "diagnostic_results": [
                    {
                        "domain": "operability_cost_liquidity",
                        "title": "10. Operability / Cost / Liquidity",
                        "status": "REVIEW",
                        "next_action": "provider actual evidence 보강",
                    }
                ],
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP"},
                "validation_efficacy_audit": {
                    "route": "VALIDATION_EFFICACY_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Provider / freshness evidence",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "PASS",
                            "Meaning": "validation efficacy ready",
                        }
                    ],
                },
                "data_coverage_audit": {
                    "route": "DATA_COVERAGE_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Price DB window coverage",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "100.0% / symbols=2",
                            "Meaning": "data coverage ready",
                        }
                    ],
                },
                "backtest_realism_audit": {
                    "route": "BACKTEST_REALISM_READY",
                    "route_label": "Ready",
                    "rows": [
                        {
                            "Criteria": "Transaction cost model",
                            "Status": "PASS",
                            "Ready": True,
                            "Current": "10 bps / net curve applied",
                            "Meaning": "backtest realism ready",
                        }
                    ],
                },
                **self._construction_gate_ready_audits(),
            },
            paper_observation={"route": "PAPER_OBSERVATION_READY", "blockers": []},
            decision_evidence={"route": "READY_FOR_FINAL_DECISION", "blockers": []},
        )
        selected_gate = build_selected_route_gate(
            decision_route=SELECT_FOR_PRACTICAL_PORTFOLIO,
            investability_packet=packet,
        )

        self.assertEqual(packet["route"], "INVESTABILITY_PACKET_READY")
        self.assertTrue(packet["select_ready"])
        self.assertEqual(packet["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertTrue(selected_gate["Ready"])
        self.assertGreaterEqual(len(packet["open_review_items"]), 1)
        self.assertEqual(
            packet["deployment_readiness_policy_snapshot"]["outcome"],
            "hold_or_re_review",
        )
        self.assertTrue(
            any(
                row["Group"] == "provider_coverage" and row["Severity"] == "WATCH"
                for row in packet["gate_policy_snapshot"]["policy_rows"]
            )
        )

    def test_final_review_save_evaluation_uses_investability_packet_gate(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_save_evaluation

        blocked_packet = {
            "route": "INVESTABILITY_PACKET_BLOCKED",
            "select_ready": False,
        }
        selected = _build_final_review_save_evaluation(
            evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=blocked_packet,
            decision_id="decision-packet-blocked",
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="reason attached",
            existing_decision_ids=set(),
        )
        hold = _build_final_review_save_evaluation(
            evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=blocked_packet,
            decision_id="decision-packet-hold",
            decision_route="HOLD_FOR_MORE_PAPER_TRACKING",
            operator_reason="reason attached",
            existing_decision_ids=set(),
        )

        self.assertFalse(selected["can_save"])
        self.assertIn("Investability evidence packet", selected["blockers"])
        self.assertFalse(hold["can_save"])
        self.assertIn("Official selection route", hold["blockers"])

    def test_final_review_decision_row_stores_compact_gate_policy_snapshot(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_decision_row

        selection_policy = {
            "schema_version": "final_review_selection_gate_policy_v1",
            "outcome": "select_ready",
            "select_allowed": True,
            "policy_rows": [
                {
                    "Criteria": "Benchmark Parity",
                    "Group": "benchmark",
                    "Ready": True,
                    "Severity": "PASS",
                }
            ],
        }
        deployment_policy = {
            "schema_version": "deployment_readiness_gate_policy_v1",
            "outcome": "hold_or_re_review",
            "select_allowed": False,
            "policy_rows": [],
        }
        packet = {
            "route": "INVESTABILITY_PACKET_READY",
            "select_ready": True,
            "gate_policy_snapshot": selection_policy,
            "selection_gate_policy_snapshot": selection_policy,
            "deployment_readiness_policy_snapshot": deployment_policy,
            "open_review_items": [{"Group": "provider_coverage", "Criteria": "Provider / Look-through"}],
        }

        row = _build_final_review_decision_row(
            source={"source_id": "source-row", "source_type": "practical_validation_result"},
            validation={"selection_source_id": "source-row", "validation_id": "validation-row"},
            paper_observation={"active_components": [], "checks": []},
            evidence={"route": "READY_FOR_FINAL_DECISION", "checks": [], "blockers": []},
            investability_packet=packet,
            decision_id="decision-row",
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="reason",
            operator_constraints="constraints",
            operator_next_action="next",
        )

        self.assertEqual(row["gate_policy_snapshot"]["outcome"], "select_ready")
        self.assertEqual(row["gate_policy_snapshot"]["policy_rows"][0]["Group"], "benchmark")
        self.assertEqual(row["selection_gate_policy_snapshot"]["schema_version"], "final_review_selection_gate_policy_v1")
        self.assertEqual(row["deployment_readiness_policy_snapshot"]["schema_version"], "deployment_readiness_gate_policy_v1")
        self.assertEqual(row["open_review_items"][0]["Group"], "provider_coverage")


class SelectedPortfolioMonitoringTimelineContractTests(unittest.TestCase):
    def _selected_row(self) -> dict:
        return {
            "decision_id": "decision-selected",
            "updated_at": "2026-05-28T10:00:00",
            "operation_status": "normal",
            "operation_status_label": "모니터링 기준 통과",
            "status_reason": "selected row is operational",
            "evidence_route": "READY_FOR_FINAL_DECISION",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "robustness_route": "READY_FOR_STRESS_SWEEP",
            "paper_observation_route": "PAPER_OBSERVATION_READY",
            "review_cadence": "monthly_or_rebalance_review",
            "review_triggers": ["CAGR deterioration review"],
            "blockers": [],
            "raw_decision": {
                "decision_id": "decision-selected",
                "updated_at": "2026-05-28T10:00:00",
                "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                "selected_practical_portfolio": True,
                "source_type": "practical_validation_result",
                "source_id": "source-selected",
                "source_title": "Selected portfolio source",
                "selection_source_id": "source-selected",
                "validation_id": "validation-selected",
                "selected_components": [
                    {
                        "title": "Selected Component",
                        "registry_id": "candidate-selected",
                        "target_weight": 100.0,
                        "benchmark": "SPY",
                        "period_start": "2020-01-01",
                        "period_end": "2024-12-31",
                    }
                ],
                "decision_evidence_snapshot": {"route": "READY_FOR_FINAL_DECISION", "checks": [], "blockers": []},
                "investability_evidence_packet": {
                    "route": "INVESTABILITY_PACKET_READY",
                    "gate_policy_snapshot": {
                        "outcome": "select_ready",
                        "select_allowed": True,
                    },
                },
                "paper_tracking_snapshot": {
                    "route": "PAPER_OBSERVATION_READY",
                    "review_cadence": "monthly_or_rebalance_review",
                    "review_triggers": ["CAGR deterioration review"],
                },
            },
        }

    def _candidate_rows_by_id(self) -> dict:
        return {
            "candidate-selected": {
                "registry_id": "candidate-selected",
                "title": "Selected Component",
                "strategy_family": "equal_weight",
                "contract": {
                    "tickers": ["SPY", "QQQ"],
                    "benchmark_ticker": "SPY",
                    "start": "2020-01-01",
                    "end": "2024-12-31",
                    "rebalance_interval": 12,
                },
                "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
            }
        }

    def _ready_recheck_preflight(self) -> dict:
        return {
            "schema_version": "selected_recheck_operations_preflight_v1",
            "route": "RECHECK_PREFLIGHT_READY",
            "route_label": "재검증 preflight 준비 완료",
            "conclusion": "ready",
            "metrics": {
                "missing_symbol_count": 0,
                "stale_symbol_count": 0,
                "watch_symbol_count": 0,
            },
        }

    def _needs_data_recheck_preflight(self) -> dict:
        return {
            "schema_version": "selected_recheck_operations_preflight_v1",
            "route": "RECHECK_PREFLIGHT_NEEDS_DATA",
            "route_label": "재검증 preflight 데이터 확인 필요",
            "conclusion": "needs data",
            "metrics": {
                "missing_symbol_count": 1,
                "stale_symbol_count": 0,
                "watch_symbol_count": 0,
            },
        }

    def _selected_row_with_open_issue(self) -> dict:
        row = self._selected_row()
        raw = dict(row["raw_decision"])
        raw["open_review_items"] = [
            {
                "Group": "provider_coverage",
                "Criteria": "Provider / Look-through",
                "Severity": "OPEN_REVIEW",
                "Current": "partial provider coverage",
                "Evidence": "Holdings coverage is partial.",
                "Required Action": "Provider holdings / exposure evidence를 보강합니다.",
                "Selection Gate Effect": "Open review item",
                "Deployment Gate Effect": "REVIEW_REQUIRED",
            }
        ]
        raw["deployment_readiness_policy_snapshot"] = {
            "schema_version": "deployment_readiness_gate_policy_v1",
            "outcome": "hold_or_re_review",
            "select_allowed": False,
            "policy_rows": [
                {
                    "Criteria": "Provider / Look-through",
                    "Group": "provider_coverage",
                    "Ready": False,
                    "Severity": "REVIEW_REQUIRED",
                    "Current": "partial provider coverage",
                    "Evidence": "Holdings coverage is partial.",
                    "Required Action": "Provider holdings / exposure evidence를 보강합니다.",
                }
            ],
        }
        row["raw_decision"] = raw
        return row

    def test_selected_dashboard_monitoring_portfolio_saved_state_crud_is_soft_delete(self) -> None:
        from app.runtime.final_selected_portfolios import (
            add_selected_dashboard_portfolio_strategy,
            delete_selected_dashboard_portfolio,
            load_selected_dashboard_portfolios,
            remove_selected_dashboard_portfolio_strategy,
            save_selected_dashboard_portfolio,
            update_selected_dashboard_portfolio_strategy_slot,
        )

        with tempfile.TemporaryDirectory() as tmpdir:
            path = Path(tmpdir) / "SELECTED_DASHBOARD_PORTFOLIOS.jsonl"
            record = save_selected_dashboard_portfolio(
                name="Core Monitor",
                description="selected candidates",
                now="2026-06-01T10:00:00",
                path=path,
            )

            self.assertEqual(record["schema_version"], 1)
            self.assertEqual(record["name"], "Core Monitor")
            self.assertEqual(record["selected_decision_ids"], [])
            self.assertEqual(record["strategy_slots"], [])
            self.assertFalse(record["storage_boundary"]["final_decision_registry_write"])
            self.assertFalse(record["storage_boundary"]["monitoring_log_auto_write"])

            add_result = add_selected_dashboard_portfolio_strategy(
                record["portfolio_id"],
                "decision-selected",
                start="2024-01-01",
                use_latest_end=True,
                initial_capital=10000.0,
                memo="core sleeve",
                now="2026-06-01T10:01:00",
                path=path,
            )
            duplicate_result = add_selected_dashboard_portfolio_strategy(
                record["portfolio_id"],
                "decision-selected",
                now="2026-06-01T10:02:00",
                path=path,
            )

            self.assertEqual(add_result["status"], "added")
            self.assertEqual(duplicate_result["status"], "duplicate")
            portfolios = load_selected_dashboard_portfolios(path=path)
            self.assertEqual(portfolios[0]["selected_decision_ids"], ["decision-selected"])
            self.assertEqual(portfolios[0]["strategy_slots"][0]["start"], "2024-01-01")
            self.assertEqual(portfolios[0]["strategy_slots"][0]["initial_capital"], 10000.0)

            update_result = update_selected_dashboard_portfolio_strategy_slot(
                record["portfolio_id"],
                "decision-selected",
                start="2024-02-01",
                end="2026-05-29",
                use_latest_end=False,
                initial_capital=12000.0,
                memo="updated sleeve",
                now="2026-06-01T10:02:30",
                path=path,
            )
            self.assertEqual(update_result["status"], "updated")
            updated_slot = load_selected_dashboard_portfolios(path=path)[0]["strategy_slots"][0]
            self.assertEqual(updated_slot["start"], "2024-02-01")
            self.assertEqual(updated_slot["end"], "2026-05-29")
            self.assertFalse(updated_slot["use_latest_end"])
            self.assertEqual(updated_slot["initial_capital"], 12000.0)

            remove_result = remove_selected_dashboard_portfolio_strategy(
                record["portfolio_id"],
                "decision-selected",
                now="2026-06-01T10:03:00",
                path=path,
            )
            self.assertEqual(remove_result["status"], "removed")
            self.assertEqual(load_selected_dashboard_portfolios(path=path)[0]["selected_decision_ids"], [])

            self.assertTrue(
                delete_selected_dashboard_portfolio(
                    record["portfolio_id"],
                    now="2026-06-01T10:04:00",
                    path=path,
                )
            )
            self.assertEqual(load_selected_dashboard_portfolios(path=path), [])
            deleted_rows = load_selected_dashboard_portfolios(include_deleted=True, path=path)
            self.assertEqual(deleted_rows[0]["deleted_at"], "2026-06-01T10:04:00")

    def test_selected_dashboard_portfolio_state_joins_selected_strategy_pool(self) -> None:
        from app.runtime.final_selected_portfolios import (
            build_final_selected_portfolio_dashboard_row,
            build_selected_dashboard_portfolio_state,
        )

        dashboard_row = build_final_selected_portfolio_dashboard_row(self._selected_row()["raw_decision"])
        state = build_selected_dashboard_portfolio_state(
            portfolios=[
                {
                    "portfolio_id": "p1",
                    "name": "Core Monitor",
                    "selected_decision_ids": ["decision-selected", "decision-selected", "missing-decision"],
                    "updated_at": "2026-06-01T10:00:00",
                }
            ],
            dashboard_rows=[dashboard_row],
        )

        self.assertEqual(state["schema_version"], "selected_dashboard_monitoring_portfolio_state_v1")
        self.assertEqual(state["metrics"]["portfolio_count"], 1)
        self.assertEqual(state["metrics"]["selected_strategy_pool_count"], 1)
        self.assertEqual(state["metrics"]["duplicate_reference_count"], 1)
        self.assertEqual(state["metrics"]["missing_reference_count"], 1)
        portfolio = state["portfolios"][0]
        self.assertEqual(portfolio["strategy_count"], 1)
        self.assertEqual(portfolio["missing_strategy_count"], 1)
        self.assertEqual(portfolio["strategy_rows"][0]["decision_id"], "decision-selected")
        self.assertEqual(portfolio["complete_strategy_slot_count"], 1)
        self.assertEqual(portfolio["incomplete_strategy_slot_count"], 1)
        self.assertTrue(portfolio["strategy_rows"][0]["slot_input_complete"])
        self.assertFalse(state["execution_boundary"]["final_decision_registry_write"])
        self.assertFalse(state["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_dashboard_portfolio_state_marks_complete_strategy_slots_ready(self) -> None:
        from app.runtime.final_selected_portfolios import (
            build_final_selected_portfolio_dashboard_row,
            build_selected_dashboard_portfolio_state,
        )

        dashboard_row = build_final_selected_portfolio_dashboard_row(self._selected_row()["raw_decision"])
        state = build_selected_dashboard_portfolio_state(
            portfolios=[
                {
                    "portfolio_id": "p1",
                    "name": "Core Monitor",
                    "strategy_slots": [
                        {
                            "decision_id": "decision-selected",
                            "start": "2024-01-01",
                            "end": "",
                            "use_latest_end": True,
                            "initial_capital": 30000.0,
                            "memo": "monitoring row",
                        }
                    ],
                    "updated_at": "2026-06-01T10:00:00",
                }
            ],
            dashboard_rows=[dashboard_row],
        )

        portfolio = state["portfolios"][0]
        self.assertEqual(portfolio["dashboard_status"], "Ready")
        self.assertEqual(portfolio["complete_strategy_slot_count"], 1)
        self.assertEqual(portfolio["incomplete_strategy_slot_count"], 0)
        self.assertEqual(portfolio["virtual_capital_total"], 30000.0)
        self.assertTrue(portfolio["strategy_rows"][0]["slot_input_complete"])

    def _ready_provider_evidence(self) -> dict:
        return {
            "schema_version": "selected_provider_evidence_v1",
            "route": "SELECTED_PROVIDER_READY",
            "route_label": "Provider 근거 준비 완료",
            "conclusion": "ready",
            "metrics": {
                "stale_count": 0,
                "partial_coverage_count": 0,
                "needs_input_count": 0,
            },
        }

    def _needs_data_provider_evidence(self) -> dict:
        return {
            "schema_version": "selected_provider_evidence_v1",
            "route": "SELECTED_PROVIDER_NEEDS_DATA",
            "route_label": "Provider DB 확인 필요",
            "conclusion": "needs data",
            "metrics": {
                "stale_count": 1,
                "partial_coverage_count": 1,
                "needs_input_count": 2,
            },
        }

    def test_selected_dashboard_handoff_review_links_selected_final_review_rows(self) -> None:
        from app.runtime.final_selected_portfolios import (
            SELECTED_DASHBOARD_HANDOFF_SCHEMA_VERSION,
            build_selected_dashboard_handoff_review,
        )

        handoff = build_selected_dashboard_handoff_review([self._selected_row()])

        self.assertEqual(handoff["schema_version"], SELECTED_DASHBOARD_HANDOFF_SCHEMA_VERSION)
        self.assertEqual(handoff["route"], "HANDOFF_READY")
        self.assertEqual(handoff["destination"], "Operations > Selected Portfolio Dashboard")
        self.assertEqual(handoff["summary"]["final_decision_count"], 1)
        self.assertEqual(handoff["summary"]["selected_decision_count"], 1)
        self.assertEqual(handoff["summary"]["dashboard_row_count"], 1)
        self.assertEqual(handoff["summary"]["monitorable_count"], 1)
        self.assertEqual(handoff["rows"][0]["Decision ID"], "decision-selected")
        self.assertEqual(handoff["rows"][0]["Handoff Destination"], "Operations > Selected Portfolio Dashboard")
        self.assertEqual(handoff["rows"][0]["Live Approval"], "Disabled")
        checks = {row["Check"]: row for row in handoff["checklist"]}
        self.assertEqual(checks["Selected route record"]["Status"], "PASS")
        self.assertEqual(checks["Monitorable row"]["Status"], "PASS")
        self.assertFalse(handoff["execution_boundary"]["registry_write"])
        self.assertFalse(handoff["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(handoff["execution_boundary"]["live_approval"])
        self.assertFalse(handoff["execution_boundary"]["order_instruction"])
        self.assertFalse(handoff["execution_boundary"]["auto_rebalance"])

    def test_selected_dashboard_handoff_review_blocks_without_selected_route(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_dashboard_handoff_review

        row = dict(self._selected_row()["raw_decision"])
        row["decision_route"] = "HOLD_FOR_MORE_PAPER_TRACKING"
        row["selected_practical_portfolio"] = False

        handoff = build_selected_dashboard_handoff_review([row])

        self.assertEqual(handoff["route"], "HANDOFF_NO_SELECTED_DECISION")
        self.assertEqual(handoff["summary"]["final_decision_count"], 1)
        self.assertEqual(handoff["summary"]["selected_decision_count"], 0)
        self.assertEqual(handoff["summary"]["dashboard_row_count"], 0)
        self.assertEqual(handoff["rows"], [])
        checks = {item["Check"]: item for item in handoff["checklist"]}
        self.assertEqual(checks["Final Review decision record"]["Status"], "PASS")
        self.assertEqual(checks["Selected route record"]["Status"], "NEEDS_INPUT")
        self.assertFalse(handoff["execution_boundary"]["auto_rebalance"])

    def test_selected_dashboard_handoff_review_surfaces_blocked_dashboard_contract(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_dashboard_handoff_review

        row = dict(self._selected_row()["raw_decision"])
        row["selected_components"] = [
            {
                "title": "Incomplete Component",
                "registry_id": "candidate-incomplete",
                "target_weight": 80.0,
                "benchmark": "SPY",
            }
        ]

        handoff = build_selected_dashboard_handoff_review([row])

        self.assertEqual(handoff["route"], "HANDOFF_BLOCKED")
        self.assertEqual(handoff["summary"]["selected_decision_count"], 1)
        self.assertEqual(handoff["summary"]["monitorable_count"], 0)
        self.assertEqual(handoff["summary"]["blocked_count"], 1)
        self.assertEqual(handoff["rows"][0]["Dashboard Status"], "운영 대상 차단")
        self.assertIn("target weight", handoff["rows"][0]["Handoff Action"])
        checks = {item["Check"]: item for item in handoff["checklist"]}
        self.assertEqual(checks["Dashboard row build"]["Status"], "PASS")
        self.assertEqual(checks["Monitorable row"]["Status"], "BLOCKED")
        self.assertFalse(handoff["execution_boundary"]["order_instruction"])

    def _ready_recheck_result(self) -> dict:
        return {
            "status": "ok",
            "verdict_route": "SELECTION_THESIS_HOLDS",
            "verdict": "선택한 재검증 기간에서 기존 선정 근거가 유지됩니다.",
            "period": {
                "start": "2024-01-01",
                "end": "2026-05-28",
                "baseline_start": "2020-01-01",
                "baseline_end": "2024-12-31",
                "added_days_vs_baseline": 513,
            },
            "portfolio_summary": {"cagr": 0.12, "mdd": -0.12},
            "baseline_summary": {"cagr": 0.10, "mdd": -0.14, "start": "2020-01-01", "end": "2024-12-31"},
            "benchmark_summary": {"cagr": 0.08},
            "change_summary": {
                "cagr_delta_vs_baseline": 0.02,
                "mdd_delta_vs_baseline": 0.02,
                "benchmark_cagr": 0.08,
                "net_cagr_spread": 0.04,
            },
            "component_rows": [{"Component": "Selected Component", "Registry ID": "candidate-selected"}],
            "blockers": [],
        }

    def test_monitoring_timeline_is_read_only_and_requires_recheck_input(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_monitoring_timeline

        timeline = build_selected_portfolio_monitoring_timeline(self._selected_row())

        self.assertEqual(timeline["schema_version"], "selected_monitoring_timeline_v1")
        self.assertEqual(timeline["timeline_status"], "NEEDS_INPUT")
        self.assertEqual([row["event"] for row in timeline["rows"]], [
            "Final Review selection",
            "Evidence gate snapshot",
            "Performance Recheck",
            "Actual Allocation drift",
            "Review trigger preview",
        ])
        self.assertFalse(timeline["execution_boundary"]["monitoring_log_auto_write"])
        self.assertEqual(timeline["execution_boundary"]["write_policy"], "read_only_timeline")
        self.assertEqual(timeline["source_contract"]["schema_version"], "selected_decision_source_consistency_v1")
        self.assertEqual(timeline["source_contract"]["decision_id"], "decision-selected")
        self.assertEqual(timeline["source_contract"]["source_identity"], "practical_validation_result:source-selected")
        self.assertEqual(timeline["source_contract"]["durable_source"], "FINAL_PORTFOLIO_SELECTION_DECISIONS")
        self.assertFalse(timeline["source_contract"]["execution_boundary"]["registry_write"])
        self.assertFalse(timeline["source_contract"]["execution_boundary"]["monitoring_log_auto_write"])

    def test_monitoring_timeline_surfaces_recheck_breach_and_drift_watch(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_monitoring_timeline

        timeline = build_selected_portfolio_monitoring_timeline(
            self._selected_row(),
            recheck_result={
                "status": "ok",
                "verdict_route": "PERFORMANCE_WEAKENED",
                "verdict": "원래 검증 대비 CAGR이 의미 있게 낮아졌습니다.",
                "period": {"start": "2024-01-01", "end": "2026-05-28"},
                "change_summary": {
                    "cagr_delta_vs_baseline": -0.05,
                    "mdd_delta_vs_baseline": -0.02,
                },
            },
            drift_check={
                "route": "DRIFT_WATCH",
                "route_label": "비중 관찰 필요",
                "verdict": "일부 drift가 watch 기준을 넘었습니다.",
                "next_action": "다음 점검일에 drift 확대 여부를 확인합니다.",
                "metrics": {"max_abs_drift": 2.5, "current_weight_total": 100.0},
            },
            alert_preview={
                "alert_route": "WATCH_ALERT",
                "alert_route_label": "관찰 경고",
                "verdict": "watch component를 다음 관찰 주기에 확인합니다.",
                "next_action": "watch component의 drift 확대 여부를 봅니다.",
                "metrics": {"alert_row_count": 2, "review_trigger_count": 1},
            },
        )

        self.assertEqual(timeline["timeline_status"], "BREACHED")
        by_event = {row["event"]: row for row in timeline["rows"]}
        self.assertEqual(by_event["Performance Recheck"]["status"], "BREACHED")
        self.assertEqual(by_event["Actual Allocation drift"]["status"], "WATCH")
        self.assertEqual(by_event["Review trigger preview"]["status"], "WATCH")
        self.assertFalse(timeline["execution_boundary"]["auto_rebalance"])

    def test_allocation_drift_boundary_is_read_only_and_session_only(self) -> None:
        from app.runtime.final_selected_portfolios import (
            SELECTED_ALLOCATION_DRIFT_BOUNDARY_SCHEMA_VERSION,
            build_selected_portfolio_allocation_drift_boundary,
            build_selected_portfolio_current_weight_inputs,
            build_selected_portfolio_drift_alert_preview,
            build_selected_portfolio_drift_check,
        )

        weight_inputs = build_selected_portfolio_current_weight_inputs(
            self._selected_row(),
            component_inputs={"candidate-selected": {"current_value": 10_000.0}},
            cash_value=0.0,
            input_mode="current_value",
        )
        drift_check = build_selected_portfolio_drift_check(
            self._selected_row(),
            current_weights=weight_inputs["current_weights"],
        )
        alert_preview = build_selected_portfolio_drift_alert_preview(
            self._selected_row(),
            drift_check=drift_check,
        )
        boundary = build_selected_portfolio_allocation_drift_boundary(
            self._selected_row(),
            weight_inputs=weight_inputs,
            drift_check=drift_check,
            alert_preview=alert_preview,
            input_mode="current_value",
        )

        self.assertEqual(boundary["schema_version"], SELECTED_ALLOCATION_DRIFT_BOUNDARY_SCHEMA_VERSION)
        self.assertEqual(boundary["route"], "ALLOCATION_DRIFT_BOUNDARY_READY")
        self.assertEqual(boundary["metrics"]["boundary_violation_count"], 0)
        rows = {row["Check"]: row for row in boundary["rows"]}
        self.assertEqual(rows["Current weight input source"]["Status"], "PASS")
        self.assertEqual(rows["Drift evidence"]["Status"], "PASS")
        self.assertEqual(rows["Alert preview evidence"]["Status"], "PASS")
        for contract in (weight_inputs, drift_check, alert_preview, boundary):
            execution_boundary = dict(contract.get("execution_boundary") or {})
            self.assertFalse(execution_boundary["db_write"])
            self.assertFalse(execution_boundary["registry_write"])
            self.assertFalse(execution_boundary["monitoring_log_auto_write"])
            self.assertFalse(execution_boundary["input_persistence"])
            self.assertFalse(execution_boundary["alert_persistence"])
            self.assertFalse(execution_boundary["account_connection"])
            self.assertFalse(execution_boundary["broker_sync"])
            self.assertFalse(execution_boundary["live_approval"])
            self.assertFalse(execution_boundary["order_instruction"])
            self.assertFalse(execution_boundary["auto_rebalance"])

    def test_allocation_drift_boundary_surfaces_breach_without_rebalance_action(self) -> None:
        from app.runtime.final_selected_portfolios import (
            build_selected_portfolio_allocation_drift_boundary,
            build_selected_portfolio_drift_alert_preview,
            build_selected_portfolio_drift_check,
        )

        row = self._selected_row()
        row["raw_decision"]["selected_components"] = [
            {
                "title": "Selected Component A",
                "registry_id": "candidate-a",
                "target_weight": 50.0,
                "benchmark": "SPY",
                "period_start": "2020-01-01",
                "period_end": "2024-12-31",
            },
            {
                "title": "Selected Component B",
                "registry_id": "candidate-b",
                "target_weight": 50.0,
                "benchmark": "QQQ",
                "period_start": "2020-01-01",
                "period_end": "2024-12-31",
            },
        ]
        drift_check = build_selected_portfolio_drift_check(
            row,
            current_weights={"candidate-a": 60.0, "candidate-b": 40.0},
        )
        alert_preview = build_selected_portfolio_drift_alert_preview(row, drift_check=drift_check)
        boundary = build_selected_portfolio_allocation_drift_boundary(
            row,
            drift_check=drift_check,
            alert_preview=alert_preview,
            input_mode="current_weight",
        )

        self.assertEqual(drift_check["route"], "REBALANCE_NEEDED")
        self.assertEqual(boundary["route"], "ALLOCATION_DRIFT_BOUNDARY_BREACHED")
        rows = {row["Check"]: row for row in boundary["rows"]}
        self.assertEqual(rows["Drift evidence"]["Status"], "BREACHED")
        self.assertEqual(rows["Alert preview evidence"]["Status"], "BREACHED")
        self.assertFalse(boundary["execution_boundary"]["order_instruction"])
        self.assertFalse(boundary["execution_boundary"]["auto_rebalance"])
        self.assertFalse(boundary["execution_boundary"]["account_connection"])
        self.assertFalse(boundary["execution_boundary"]["broker_sync"])

    def test_selected_continuity_check_requires_recheck_input_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_continuity_check

        continuity = build_selected_portfolio_continuity_check(self._selected_row())

        self.assertEqual(continuity["schema_version"], "selected_continuity_check_v1")
        self.assertEqual(continuity["route"], "CONTINUITY_NEEDS_INPUT")
        checks = {row["Check"]: row for row in continuity["checks"]}
        self.assertEqual(checks["Selected Final Review row"]["Status"], "PASS")
        self.assertEqual(checks["Decision source consistency"]["Status"], "PASS")
        self.assertEqual(checks["Component target contract"]["Status"], "PASS")
        self.assertEqual(checks["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertTrue(continuity["metrics"]["source_contract_consistent"])
        self.assertEqual(continuity["source_contract"]["decision_id"], "decision-selected")
        self.assertFalse(continuity["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(continuity["execution_boundary"]["registry_write"])
        self.assertFalse(continuity["execution_boundary"]["live_approval"])

    def test_selected_continuity_check_blocks_mismatched_timeline_source_contract(self) -> None:
        from app.runtime.final_selected_portfolios import (
            build_selected_portfolio_continuity_check,
            build_selected_portfolio_monitoring_timeline,
        )

        timeline = build_selected_portfolio_monitoring_timeline(self._selected_row())
        timeline["source_contract"]["decision_id"] = "different-decision"

        continuity = build_selected_portfolio_continuity_check(
            self._selected_row(),
            monitoring_timeline=timeline,
        )

        self.assertEqual(continuity["route"], "CONTINUITY_BLOCKED")
        checks = {row["Check"]: row for row in continuity["checks"]}
        self.assertEqual(checks["Decision source consistency"]["Status"], "BLOCKED")
        self.assertFalse(continuity["metrics"]["source_contract_consistent"])
        self.assertFalse(continuity["execution_boundary"]["registry_write"])

    def test_selected_continuity_check_blocks_non_selected_or_invalid_component_contract(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_continuity_check

        row = self._selected_row()
        row["raw_decision"]["decision_route"] = "HOLD_FOR_MORE_PAPER_TRACKING"
        row["raw_decision"]["selected_practical_portfolio"] = False
        row["raw_decision"]["selected_components"][0]["target_weight"] = 80.0

        continuity = build_selected_portfolio_continuity_check(row)

        self.assertEqual(continuity["route"], "CONTINUITY_BLOCKED")
        checks = {item["Check"]: item for item in continuity["checks"]}
        self.assertEqual(checks["Selected Final Review row"]["Status"], "BLOCKED")
        self.assertEqual(checks["Component target contract"]["Status"], "BLOCKED")
        self.assertFalse(continuity["execution_boundary"]["order_instruction"])

    def test_recheck_comparison_requires_recheck_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_comparison

        comparison = build_selected_portfolio_recheck_comparison(self._selected_row())

        self.assertEqual(comparison["schema_version"], "selected_recheck_comparison_v1")
        self.assertEqual(comparison["route"], "RECHECK_COMPARISON_NOT_RUN")
        self.assertEqual(comparison["overall_status"], "NEEDS_INPUT")
        rows = {row["Check"]: row for row in comparison["rows"]}
        self.assertEqual(rows["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "NEEDS_INPUT")
        self.assertFalse(comparison["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(comparison["execution_boundary"]["live_approval"])
        self.assertFalse(comparison["execution_boundary"]["auto_rebalance"])

    def test_recheck_comparison_surfaces_breach_from_recheck_delta(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_comparison

        comparison = build_selected_portfolio_recheck_comparison(
            self._selected_row(),
            recheck_result={
                "status": "ok",
                "verdict_route": "PERFORMANCE_WEAKENED",
                "verdict": "원래 검증 대비 CAGR이 의미 있게 낮아졌습니다.",
                "period": {
                    "start": "2024-01-01",
                    "end": "2026-05-28",
                    "baseline_start": "2020-01-01",
                    "baseline_end": "2024-12-31",
                    "added_days_vs_baseline": 513,
                },
                "portfolio_summary": {"cagr": 0.04, "mdd": -0.22},
                "baseline_summary": {"cagr": 0.10, "mdd": -0.14, "start": "2020-01-01", "end": "2024-12-31"},
                "benchmark_summary": {"cagr": 0.06},
                "change_summary": {
                    "cagr_delta_vs_baseline": -0.06,
                    "mdd_delta_vs_baseline": -0.08,
                    "benchmark_cagr": 0.06,
                    "net_cagr_spread": -0.02,
                },
                "component_rows": [{"Component": "Selected Component", "Registry ID": "candidate-selected"}],
                "blockers": [],
            },
        )

        self.assertEqual(comparison["route"], "RECHECK_COMPARISON_BREACHED")
        self.assertEqual(comparison["overall_status"], "BREACHED")
        rows = {row["Check"]: row for row in comparison["rows"]}
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "BREACHED")
        self.assertEqual(rows["MDD vs selected baseline"]["Status"], "BREACHED")
        self.assertEqual(rows["Benchmark spread"]["Status"], "BREACHED")
        self.assertFalse(comparison["execution_boundary"]["order_instruction"])
        self.assertFalse(comparison["execution_boundary"]["auto_rebalance"])

    def test_recheck_comparison_ready_when_thesis_holds(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_comparison

        comparison = build_selected_portfolio_recheck_comparison(
            self._selected_row(),
            recheck_result={
                "status": "ok",
                "verdict_route": "SELECTION_THESIS_HOLDS",
                "verdict": "선택한 재검증 기간에서 기존 선정 근거가 유지됩니다.",
                "period": {
                    "start": "2024-01-01",
                    "end": "2026-05-28",
                    "baseline_start": "2020-01-01",
                    "baseline_end": "2024-12-31",
                    "added_days_vs_baseline": 513,
                },
                "portfolio_summary": {"cagr": 0.12, "mdd": -0.12},
                "baseline_summary": {"cagr": 0.10, "mdd": -0.14, "start": "2020-01-01", "end": "2024-12-31"},
                "benchmark_summary": {"cagr": 0.08},
                "change_summary": {
                    "cagr_delta_vs_baseline": 0.02,
                    "mdd_delta_vs_baseline": 0.02,
                    "benchmark_cagr": 0.08,
                    "net_cagr_spread": 0.04,
                },
                "component_rows": [{"Component": "Selected Component", "Registry ID": "candidate-selected"}],
                "blockers": [],
            },
        )

        self.assertEqual(comparison["route"], "RECHECK_COMPARISON_READY")
        self.assertEqual(comparison["overall_status"], "CLEAR")
        self.assertEqual(comparison["metrics"]["breached_count"], 0)
        self.assertEqual(comparison["metrics"]["watch_count"], 0)
        self.assertEqual(comparison["metrics"]["needs_input_count"], 0)

    def test_review_signal_policy_ready_uses_recheck_comparison_rows(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_review_signal_policy

        policy = build_selected_portfolio_review_signal_policy(
            self._selected_row(),
            recheck_result=self._ready_recheck_result(),
            recheck_preflight=self._ready_recheck_preflight(),
            provider_evidence=self._ready_provider_evidence(),
        )

        self.assertEqual(policy["schema_version"], "selected_review_signal_policy_v1")
        self.assertEqual(policy["route"], "REVIEW_SIGNAL_CLEAR")
        self.assertEqual(policy["overall_status"], "CLEAR")
        rows = {row["Trigger"]: row for row in policy["rows"]}
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "CLEAR")
        self.assertEqual(rows["CAGR vs selected baseline"]["Policy Owner"], "Recheck Comparison")
        self.assertEqual(rows["MDD vs selected baseline"]["Policy Owner"], "Recheck Comparison")
        self.assertEqual(rows["Benchmark spread"]["Policy Owner"], "Recheck Comparison")
        self.assertFalse(policy["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(policy["execution_boundary"]["report_auto_write"])
        self.assertFalse(policy["execution_boundary"]["order_instruction"])
        self.assertEqual(policy["source_contract"]["decision_id"], "decision-selected")
        self.assertEqual(
            policy["source_contract"]["session_evidence_sources"],
            ["session_state.performance_recheck"],
        )

    def test_review_signal_policy_keeps_missing_recheck_and_data_gaps_out_of_clear(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_review_signal_policy

        policy = build_selected_portfolio_review_signal_policy(
            self._selected_row(),
            recheck_preflight=self._needs_data_recheck_preflight(),
            provider_evidence=self._needs_data_provider_evidence(),
        )

        self.assertEqual(policy["route"], "REVIEW_SIGNAL_NEEDS_INPUT")
        self.assertEqual(policy["overall_status"], "NEEDS_INPUT")
        rows = {row["Trigger"]: row for row in policy["rows"]}
        self.assertEqual(rows["Recheck operations preflight"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["Provider evidence freshness / coverage"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["Performance Recheck input"]["Status"], "NEEDS_INPUT")
        self.assertGreaterEqual(policy["metrics"]["needs_input_count"], 3)
        self.assertFalse(policy["execution_boundary"]["registry_write"])

    def test_review_signal_policy_surfaces_comparison_breach(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_review_signal_policy

        breached_result = self._ready_recheck_result()
        breached_result["verdict_route"] = "PERFORMANCE_WEAKENED"
        breached_result["portfolio_summary"] = {"cagr": 0.04, "mdd": -0.22}
        breached_result["benchmark_summary"] = {"cagr": 0.06}
        breached_result["change_summary"] = {
            "cagr_delta_vs_baseline": -0.06,
            "mdd_delta_vs_baseline": -0.08,
            "benchmark_cagr": 0.06,
            "net_cagr_spread": -0.02,
        }

        policy = build_selected_portfolio_review_signal_policy(
            self._selected_row(),
            recheck_result=breached_result,
            recheck_preflight=self._ready_recheck_preflight(),
            provider_evidence=self._ready_provider_evidence(),
        )

        self.assertEqual(policy["route"], "REVIEW_SIGNAL_BREACHED")
        self.assertEqual(policy["overall_status"], "BREACHED")
        self.assertEqual(policy["recheck_comparison"]["route"], "RECHECK_COMPARISON_BREACHED")
        rows = {row["Trigger"]: row for row in policy["rows"]}
        self.assertEqual(rows["CAGR vs selected baseline"]["Status"], "BREACHED")
        self.assertEqual(rows["Benchmark spread"]["Policy Owner"], "Recheck Comparison")
        self.assertFalse(policy["execution_boundary"]["auto_rebalance"])

    def test_recheck_readiness_blocks_missing_replay_contract_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        readiness = build_selected_portfolio_recheck_readiness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
        )

        self.assertEqual(readiness["schema_version"], "selected_recheck_readiness_v1")
        self.assertEqual(readiness["route"], "RECHECK_READINESS_BLOCKED")
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["Selected component contract"]["Status"], "PASS")
        self.assertEqual(rows["Selected replay contract"]["Status"], "BLOCKED")
        self.assertFalse(readiness["execution_boundary"]["db_write"])
        self.assertFalse(readiness["execution_boundary"]["registry_write"])
        self.assertFalse(readiness["execution_boundary"]["monitoring_log_auto_write"])

    def test_recheck_readiness_ready_when_db_latest_and_replay_contract_exist(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        readiness = build_selected_portfolio_recheck_readiness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={
                "candidate-selected": {
                    "registry_id": "candidate-selected",
                    "title": "Selected Component",
                    "strategy_family": "equal_weight",
                    "contract": {
                        "tickers": ["SPY", "QQQ"],
                        "benchmark_ticker": "SPY",
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "rebalance_interval": 12,
                    },
                    "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
                }
            },
        )

        self.assertEqual(readiness["route"], "RECHECK_READINESS_READY")
        self.assertEqual(readiness["metrics"]["blocked_count"], 0)
        self.assertEqual(readiness["metrics"]["needs_input_count"], 0)
        self.assertEqual(readiness["metrics"]["replay_contract_count"], 1)
        self.assertEqual(readiness["metrics"]["symbol_count"], 2)
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["DB latest market date"]["Status"], "PASS")
        self.assertEqual(rows["Default recheck period"]["Status"], "PASS")

    def test_recheck_readiness_uses_embedded_final_decision_contract_without_registry(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_readiness

        row = self._selected_row()
        row["raw_decision"]["selected_components"][0]["strategy_key"] = "equal_weight"
        row["raw_decision"]["selected_components"][0]["replay_contract"] = {
            "settings_snapshot": {
                "tickers": ["SPY", "QQQ"],
                "benchmark_ticker": "SPY",
                "start": "2020-01-01",
                "end": "2024-12-31",
                "rebalance_interval": 12,
            }
        }

        readiness = build_selected_portfolio_recheck_readiness(
            row,
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
        )

        self.assertEqual(readiness["route"], "RECHECK_READINESS_READY")
        self.assertEqual(readiness["metrics"]["embedded_replay_contract_count"], 1)
        self.assertEqual(readiness["metrics"]["candidate_registry_fallback_count"], 0)
        rows = {row["Check"]: row for row in readiness["rows"]}
        self.assertEqual(rows["Selected replay contract"]["Status"], "PASS")

    def test_recheck_symbol_freshness_detects_missing_and_stale_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_symbol_freshness

        freshness = build_selected_portfolio_recheck_symbol_freshness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={
                "candidate-selected": {
                    "registry_id": "candidate-selected",
                    "title": "Selected Component",
                    "strategy_family": "equal_weight",
                    "contract": {
                        "tickers": ["SPY", "QQQ"],
                        "benchmark_ticker": "DIA",
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "rebalance_interval": 12,
                    },
                    "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
                }
            },
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                    {"symbol": "QQQ", "latest_date": "2026-05-10", "row_count": 980},
                ]
            ),
        )

        self.assertEqual(freshness["schema_version"], "selected_recheck_symbol_freshness_v1")
        self.assertEqual(freshness["route"], "SYMBOL_FRESHNESS_MISSING")
        self.assertEqual(freshness["metrics"]["symbol_count"], 3)
        self.assertEqual(freshness["metrics"]["stale_count"], 1)
        self.assertEqual(freshness["metrics"]["missing_count"], 1)
        rows = {row["Symbol"]: row for row in freshness["rows"]}
        self.assertEqual(rows["QQQ"]["Status"], "STALE")
        self.assertEqual(rows["DIA"]["Status"], "MISSING")
        self.assertFalse(freshness["execution_boundary"]["db_write"])
        self.assertFalse(freshness["execution_boundary"]["registry_write"])
        self.assertFalse(freshness["execution_boundary"]["monitoring_log_auto_write"])

    def test_recheck_symbol_freshness_ready_when_all_symbols_recent(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_symbol_freshness

        freshness = build_selected_portfolio_recheck_symbol_freshness(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={
                "candidate-selected": {
                    "registry_id": "candidate-selected",
                    "title": "Selected Component",
                    "strategy_family": "equal_weight",
                    "contract": {
                        "tickers": ["SPY", "QQQ"],
                        "benchmark_ticker": "SPY",
                        "start": "2020-01-01",
                        "end": "2024-12-31",
                        "rebalance_interval": 12,
                    },
                    "execution_context": {"start": "2020-01-01", "end": "2024-12-31"},
                }
            },
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                    {"symbol": "QQQ", "latest_date": "2026-05-27", "row_count": 999},
                ]
            ),
        )

        self.assertEqual(freshness["route"], "SYMBOL_FRESHNESS_READY")
        self.assertEqual(freshness["metrics"]["pass_count"], 2)
        self.assertEqual(freshness["metrics"]["missing_count"], 0)
        self.assertEqual(freshness["metrics"]["stale_count"], 0)
        rows = {row["Symbol"]: row for row in freshness["rows"]}
        self.assertIn("benchmark", rows["SPY"]["Role"])
        self.assertFalse(freshness["execution_boundary"]["order_instruction"])

    def test_recheck_operations_preflight_ready_when_readiness_and_freshness_are_ready(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_operations_preflight

        preflight = build_selected_portfolio_recheck_operations_preflight(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id=self._candidate_rows_by_id(),
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                    {"symbol": "QQQ", "latest_date": "2026-05-27", "row_count": 999},
                ]
            ),
        )

        self.assertEqual(preflight["schema_version"], "selected_recheck_operations_preflight_v1")
        self.assertEqual(preflight["route"], "RECHECK_PREFLIGHT_READY")
        self.assertEqual(preflight["metrics"]["replay_contract_count"], 1)
        self.assertEqual(preflight["metrics"]["missing_symbol_count"], 0)
        self.assertEqual(preflight["metrics"]["stale_symbol_count"], 0)
        self.assertEqual(preflight["readiness"]["route"], "RECHECK_READINESS_READY")
        self.assertEqual(preflight["symbol_freshness"]["route"], "SYMBOL_FRESHNESS_READY")
        self.assertFalse(preflight["execution_boundary"]["db_write"])
        self.assertFalse(preflight["execution_boundary"]["registry_write"])
        self.assertFalse(preflight["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(preflight["execution_boundary"]["order_instruction"])
        self.assertFalse(preflight["execution_boundary"]["auto_rebalance"])

    def test_recheck_operations_preflight_routes_missing_price_to_needs_data(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_operations_preflight

        preflight = build_selected_portfolio_recheck_operations_preflight(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id=self._candidate_rows_by_id(),
            freshness_df=pd.DataFrame(
                [
                    {"symbol": "SPY", "latest_date": "2026-05-28", "row_count": 1000},
                ]
            ),
        )

        self.assertEqual(preflight["route"], "RECHECK_PREFLIGHT_NEEDS_DATA")
        self.assertEqual(preflight["symbol_freshness"]["route"], "SYMBOL_FRESHNESS_MISSING")
        self.assertEqual(preflight["metrics"]["missing_symbol_count"], 1)
        rows = {row["Area"]: row for row in preflight["rows"]}
        self.assertEqual(rows["Symbol Freshness"]["Status"], "NEEDS_INPUT")

    def test_recheck_operations_preflight_blocks_missing_replay_contract(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_recheck_operations_preflight

        preflight = build_selected_portfolio_recheck_operations_preflight(
            self._selected_row(),
            latest_market_result={"status": "ok", "latest_market_date": "2026-05-28", "error": None},
            candidate_rows_by_id={},
            freshness_df=pd.DataFrame(),
        )

        self.assertEqual(preflight["route"], "RECHECK_PREFLIGHT_BLOCKED")
        self.assertEqual(preflight["readiness"]["route"], "RECHECK_READINESS_BLOCKED")
        self.assertEqual(preflight["symbol_freshness"]["route"], "SYMBOL_FRESHNESS_BLOCKED")
        rows = {row["Area"]: row for row in preflight["rows"]}
        self.assertEqual(rows["Recheck Readiness"]["Status"], "BLOCKED")
        self.assertEqual(rows["Symbol Freshness"]["Status"], "BLOCKED")

    def test_open_issue_followup_surfaces_final_review_open_items(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_open_issue_followup

        followup = build_selected_portfolio_open_issue_followup(self._selected_row_with_open_issue())

        self.assertEqual(followup["schema_version"], "selected_open_issue_followup_v1")
        self.assertEqual(followup["route"], "OPEN_ISSUES_PRESENT")
        self.assertEqual(followup["metrics"]["open_review_item_count"], 1)
        self.assertEqual(followup["metrics"]["review_trigger_count"], 1)
        rows = {row["Area"]: row for row in followup["rows"]}
        self.assertEqual(rows["Provider / Look-through"]["Status"], "REVIEW")
        self.assertIn("Provider holdings", rows["Provider / Look-through"]["Next Action"])
        self.assertFalse(followup["execution_boundary"]["monitoring_log_auto_write"])
        self.assertFalse(followup["execution_boundary"]["live_approval"])

    def test_deployment_readiness_preflight_is_read_only_and_keeps_review_open(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_deployment_readiness_preflight

        preflight = build_selected_portfolio_deployment_readiness_preflight(
            self._selected_row_with_open_issue(),
            recheck_preflight=self._ready_recheck_preflight(),
            provider_evidence={
                "schema_version": "selected_provider_evidence_v1",
                "route": "SELECTED_PROVIDER_READY",
                "route_label": "Provider 근거 준비 완료",
                "conclusion": "provider ready",
            },
            continuity_check={
                "schema_version": "selected_continuity_check_v1",
                "route": "CONTINUITY_READY",
                "route_label": "사후 점검 준비 완료",
                "next_action": "continue monitoring",
            },
            review_signal_policy={
                "schema_version": "selected_review_signal_policy_v1",
                "route": "REVIEW_SIGNAL_CLEAR",
                "route_label": "운영 신호 정상",
                "conclusion": "signals clear",
            },
            allocation_boundary={
                "schema_version": "selected_allocation_drift_evidence_boundary_v1",
                "route": "ALLOCATION_DRIFT_BOUNDARY_OPTIONAL",
                "route_label": "비중 근거 선택 점검",
                "conclusion": "allocation optional",
            },
        )

        self.assertEqual(preflight["schema_version"], "selected_deployment_readiness_preflight_v1")
        self.assertEqual(preflight["route"], "DEPLOYMENT_READINESS_REVIEW")
        self.assertEqual(preflight["metrics"]["review_count"], 3)
        rows = {row["Area"]: row for row in preflight["rows"]}
        self.assertEqual(rows["Deployment Gate Policy"]["Status"], "REVIEW")
        self.assertEqual(rows["Policy: Provider / Look-through"]["Status"], "REVIEW")
        self.assertEqual(rows["Open Issues / Follow-up"]["Status"], "REVIEW")
        self.assertFalse(preflight["execution_boundary"]["live_approval"])
        self.assertFalse(preflight["execution_boundary"]["order_instruction"])
        self.assertFalse(preflight["execution_boundary"]["auto_rebalance"])

    def test_selected_provider_evidence_ready_from_injected_provider_context(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF holdings snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF exposure snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "Macro Context",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": None,
                        "Source Mix": "fred: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "Macro context is available.",
                    },
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                    "summary_rows": [{"Check": "Holdings coverage", "Status": "PASS"}],
                },
            },
        )

        self.assertEqual(evidence["schema_version"], "selected_provider_evidence_v1")
        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_READY")
        self.assertEqual(
            evidence["staleness_contract"]["schema_version"],
            "selected_provider_evidence_staleness_contract_v1",
        )
        self.assertEqual(evidence["metrics"]["provider_symbol_count"], 2)
        self.assertEqual(evidence["metrics"]["needs_input_count"], 0)
        self.assertEqual(evidence["metrics"]["stale_count"], 0)
        self.assertEqual(evidence["metrics"]["partial_coverage_count"], 0)
        self.assertEqual(evidence["symbol_weights"], {"QQQ": 50.0, "SPY": 50.0})
        self.assertFalse(evidence["execution_boundary"]["db_write"])
        self.assertFalse(evidence["execution_boundary"]["provider_collection"])
        self.assertFalse(evidence["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_provider_evidence_surfaces_not_run_without_writing(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "not_run",
                        "Diagnostic Status": "NOT_RUN",
                        "Coverage Weight": 0.0,
                        "Source Mix": "-",
                        "Freshness": "missing",
                        "As Of Range": "-",
                        "Summary": "ETF holdings snapshot coverage is unavailable.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "partial",
                        "Diagnostic Status": "REVIEW",
                        "Coverage Weight": 50.0,
                        "Source Mix": "official: 50.0%",
                        "Freshness": "stale",
                        "As Of Range": "2026-04-01 -> 2026-04-01",
                        "Summary": "ETF exposure snapshot covers 50.0% of target weight.",
                    },
                ],
                "look_through_board": {
                    "status": "REVIEW",
                    "holdings_coverage_weight": 0.0,
                    "exposure_coverage_weight": 50.0,
                    "unknown_exposure_weight": 50.0,
                    "top_holding_weight": 0.0,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_NEEDS_DATA")
        self.assertEqual(evidence["metrics"]["needs_input_count"], 2)
        self.assertEqual(evidence["metrics"]["review_count"], 1)
        self.assertEqual(evidence["metrics"]["stale_count"], 1)
        self.assertEqual(evidence["metrics"]["partial_coverage_count"], 1)
        self.assertGreaterEqual(evidence["metrics"]["missing_coverage_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["ETF Exposure"]["Status"], "REVIEW")
        self.assertEqual(rows["Look-through Coverage"]["Status"], "NEEDS_INPUT")
        self.assertFalse(evidence["execution_boundary"]["registry_write"])
        self.assertFalse(evidence["execution_boundary"]["order_instruction"])

    def test_selected_provider_evidence_marks_component_fallback_as_review(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        row = self._selected_row()
        row["raw_decision"]["selected_components"][0]["universe"] = "SPY QQQ"

        evidence = build_selected_portfolio_provider_evidence(
            row,
            candidate_rows_by_id={},
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF holdings snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF exposure snapshot covers 100.0% of target weight.",
                    }
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertEqual(evidence["symbol_weights"], {"QQQ": 50.0, "SPY": 50.0})
        self.assertEqual(evidence["metrics"]["fallback_contract_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["Selected Symbol Contract"]["Status"], "REVIEW")
        self.assertFalse(evidence["execution_boundary"]["monitoring_log_auto_write"])

    def test_selected_provider_evidence_downgrades_stale_actual_pass_to_review(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "stale",
                        "As Of Range": "2026-03-01 -> 2026-03-01",
                        "Summary": "ETF holdings snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF exposure snapshot covers 100.0% of target weight.",
                    },
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertEqual(evidence["metrics"]["stale_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "REVIEW")
        self.assertIn("freshness=stale", rows["ETF Holdings"]["Policy Reason"])

    def test_selected_provider_evidence_downgrades_partial_pass_to_review(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    },
                    {
                        "Area": "ETF Holdings",
                        "Coverage": "partial",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 75.0,
                        "Source Mix": "official: 75.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF holdings snapshot covers 75.0% of target weight.",
                    },
                    {
                        "Area": "ETF Exposure",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF exposure snapshot covers 100.0% of target weight.",
                    },
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 75.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_REVIEW")
        self.assertGreaterEqual(evidence["metrics"]["partial_coverage_count"], 1)
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "REVIEW")
        self.assertEqual(rows["Look-through Coverage"]["Status"], "REVIEW")

    def test_selected_provider_evidence_requires_core_provider_areas(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_provider_evidence

        evidence = build_selected_portfolio_provider_evidence(
            self._selected_row(),
            candidate_rows_by_id=self._candidate_rows_by_id(),
            provider_context={
                "display_rows": [
                    {
                        "Area": "ETF Operability",
                        "Coverage": "actual",
                        "Diagnostic Status": "PASS",
                        "Coverage Weight": 100.0,
                        "Source Mix": "official: 100.0%",
                        "Freshness": "fresh",
                        "As Of Range": "2026-05-28 -> 2026-05-28",
                        "Summary": "ETF operability snapshot covers 100.0% of target weight.",
                    }
                ],
                "look_through_board": {
                    "status": "PASS",
                    "holdings_coverage_weight": 100.0,
                    "exposure_coverage_weight": 100.0,
                    "unknown_exposure_weight": 0.0,
                    "top_holding_weight": 9.5,
                },
            },
        )

        self.assertEqual(evidence["route"], "SELECTED_PROVIDER_NEEDS_DATA")
        rows = {row["Area"]: row for row in evidence["rows"]}
        self.assertEqual(rows["ETF Holdings"]["Status"], "NEEDS_INPUT")
        self.assertEqual(rows["ETF Exposure"]["Status"], "NEEDS_INPUT")
        self.assertIn("required_provider_area_missing", rows["ETF Holdings"]["Policy Reason"])


class DecisionDossierContractTests(unittest.TestCase):
    def _final_decision_row(self) -> dict:
        return {
            "decision_id": "decision-dossier",
            "created_at": "2026-05-28T09:00:00",
            "updated_at": "2026-05-28T10:00:00",
            "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
            "selected_practical_portfolio": True,
            "source_type": "practical_validation_result",
            "source_id": "source-dossier",
            "source_title": "GTAA selected portfolio",
            "selection_source_id": "source-dossier",
            "validation_id": "validation-dossier",
            "selected_components": [
                {
                    "title": "GTAA component",
                    "registry_id": "candidate-gtaa",
                    "target_weight": 100.0,
                    "benchmark": "SPY",
                }
            ],
            "decision_evidence_snapshot": {
                "route": "READY_FOR_FINAL_DECISION",
                "score": 8.2,
                "checks": [
                    {
                        "Criteria": "Portfolio validation",
                        "Ready": True,
                        "Current": "READY_FOR_FINAL_REVIEW",
                        "Meaning": "validation evidence attached",
                        "Score": 2.4,
                    }
                ],
                "blockers": [],
            },
            "investability_evidence_packet": {
                "route": "INVESTABILITY_PACKET_READY",
                "checks": [
                    {
                        "Section": "Execution Boundary",
                        "Ready": True,
                        "Current": "live approval disabled / order disabled",
                        "Meaning": "not an order",
                    }
                ],
                "gate_policy_snapshot": {
                    "schema_version": "investability_gate_policy_v1",
                    "outcome": "select_ready",
                    "select_allowed": True,
                    "blockers": [],
                    "review_required": [],
                    "policy_rows": [
                        {
                            "Group": "benchmark",
                            "Status": "PASS",
                            "Severity": "PASS",
                            "Current": "PASS",
                            "Evidence": "benchmark parity attached",
                            "Required Action": "none",
                        }
                    ],
                },
            },
            "risk_and_validation_snapshot": {
                "validation_route": "READY_FOR_FINAL_REVIEW",
                "validation_score": 8.5,
                "diagnostic_summary": {"status_counts": {"PASS": 10, "REVIEW": 1, "NOT_RUN": 1}},
                "robustness_validation": {"robustness_route": "READY_FOR_STRESS_SWEEP", "robustness_score": 7.8},
            },
            "paper_tracking_snapshot": {
                "route": "PAPER_OBSERVATION_READY",
                "review_cadence": "monthly_or_rebalance_review",
                "review_triggers": ["CAGR deterioration review"],
                "checks": [
                    {
                        "Criteria": "Review triggers",
                        "Ready": True,
                        "Current": "1",
                        "Meaning": "trigger attached",
                    }
                ],
            },
            "operator_decision": {
                "reason": "검증 근거가 충분합니다.",
                "constraints": "실제 투자 전 금액과 중단 기준 확인",
                "next_action": "Selected Dashboard에서 사후 점검",
            },
        }

    def test_decision_dossier_is_read_only_markdown_export(self) -> None:
        from app.services.backtest_evidence_read_model import build_decision_dossier

        dossier = build_decision_dossier(self._final_decision_row())

        self.assertEqual(dossier["schema_version"], "decision_dossier_v1")
        self.assertEqual(dossier["decision"]["decision_id"], "decision-dossier")
        self.assertEqual(dossier["metrics"]["component_count"], 1)
        self.assertGreaterEqual(dossier["metrics"]["evidence_check_count"], 1)
        self.assertEqual(dossier["execution_boundary"]["write_policy"], "read_only_dossier")
        self.assertFalse(dossier["execution_boundary"]["db_write"])
        self.assertFalse(dossier["execution_boundary"]["registry_write"])
        self.assertFalse(dossier["execution_boundary"]["report_auto_write"])
        self.assertFalse(dossier["execution_boundary"]["live_approval"])
        self.assertEqual(dossier["source_contract"]["schema_version"], "selected_decision_source_consistency_v1")
        self.assertEqual(dossier["source_contract"]["source_identity"], "practical_validation_result:source-dossier")
        self.assertTrue(dossier["metrics"]["source_contract_consistent"])
        self.assertIn("# Final Decision Dossier", dossier["markdown"])
        self.assertIn("## Source Contract", dossier["markdown"])
        self.assertIn("decision-dossier", dossier["filename"])
        self.assertIn("not live approval", dossier["markdown"])

    def test_decision_dossier_can_include_selected_monitoring_timeline(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_monitoring_timeline
        from app.services.backtest_evidence_read_model import build_decision_dossier

        selected_row = {"raw_decision": self._final_decision_row()}
        timeline = build_selected_portfolio_monitoring_timeline(
            selected_row,
            recheck_result={
                "status": "ok",
                "verdict_route": "SELECTION_THESIS_HOLDS",
                "verdict": "선정 근거가 유지됩니다.",
                "period": {"start": "2026-01-01", "end": "2026-05-28"},
                "change_summary": {"cagr_delta_vs_baseline": 0.01},
            },
        )

        dossier = build_decision_dossier(
            selected_row,
            monitoring_timeline=timeline,
        )

        self.assertTrue(dossier["monitoring_timeline"]["present"])
        self.assertTrue(dossier["metrics"]["monitoring_timeline_present"])
        self.assertTrue(dossier["source_contract"]["timeline_contract_present"])
        self.assertTrue(dossier["source_contract"]["timeline_contract_consistent"])
        self.assertEqual(
            dossier["source_contract"]["session_evidence_sources"],
            ["session_state.performance_recheck"],
        )
        self.assertIn("Performance Recheck", dossier["markdown"])
        self.assertFalse(dossier["execution_boundary"]["monitoring_log_auto_write"])

    def test_decision_dossier_surfaces_mismatched_timeline_source_contract(self) -> None:
        from app.runtime.final_selected_portfolios import build_selected_portfolio_monitoring_timeline
        from app.services.backtest_evidence_read_model import build_decision_dossier

        selected_row = {"raw_decision": self._final_decision_row()}
        timeline = build_selected_portfolio_monitoring_timeline(selected_row)
        timeline["source_contract"]["source_id"] = "different-source"

        dossier = build_decision_dossier(
            selected_row,
            monitoring_timeline=timeline,
        )

        self.assertTrue(dossier["source_contract"]["timeline_contract_present"])
        self.assertFalse(dossier["source_contract"]["timeline_contract_consistent"])
        self.assertFalse(dossier["metrics"]["source_contract_consistent"])
        self.assertIn("Timeline Contract Consistent: `False`", dossier["markdown"])


if __name__ == "__main__":
    unittest.main()
