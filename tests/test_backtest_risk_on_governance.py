from __future__ import annotations

import json
import sys
import tempfile
import unittest
from pathlib import Path
from unittest.mock import patch

import pandas as pd


class BacktestRiskOnGovernanceContractTests(unittest.TestCase):
    def test_compact_daily_swing_evidence_is_json_safe_and_flags_current_universe_bias(self) -> None:
        from app.runtime.backtest.runners.risk_on_momentum_evidence import (
            build_daily_swing_evidence_packet,
        )
        from finance.swing import RiskOnMomentumConfig

        packet = build_daily_swing_evidence_packet(
            config=RiskOnMomentumConfig(
                start="2024-07-26",
                end="2026-07-24",
                transaction_cost_bps=5.0,
                slippage_bps=5.0,
                macro_filter_mode="hard_filter",
            ),
            meta={
                "universe_mode": "top1000",
                "universe_source": "market_cap_universe_members:TOP1000",
                "universe_symbol_count": 1000,
                "analysis_intensity": "standard",
                "simulation_executed_count": 16,
            },
            metrics={
                "total_trades": 120,
                "avg_holding_days": 3.4,
                "cagr": 0.12,
                "mdd": -0.18,
                "total_fees": 42.0,
            },
            result_df=pd.DataFrame(
                [
                    {"Date": "2024-07-26", "Total Balance": 10_000.0},
                    {"Date": "2026-07-24", "Total Balance": 12_500.0},
                ]
            ),
            trade_log_df=pd.DataFrame(
                [
                    {
                        "entry_notional": 3_000.0,
                        "gross_proceeds": 3_300.0,
                        "exit_reason": "TAKE_PROFIT",
                        "net_return_pct": 0.10,
                    }
                ]
            ),
            random_summary_df=pd.DataFrame([{"cagr": 0.04}, {"cagr": 0.05}]),
            benchmark_comparison_df=pd.DataFrame(
                [{"label": "SPY Buy & Hold", "cagr": 0.08}]
            ),
            quality_warning_df=pd.DataFrame(
                [{"status": "REVIEW", "warning": "Ticker dependency"}]
            ),
            artifact={"run_json": "/tmp/run.json", "trade_row_count": 1, "scanner_row_count": 10},
        )

        json.dumps(packet)
        self.assertEqual(packet["status"], "REVIEW")
        self.assertEqual(packet["performance"]["trade_count"], 120)
        self.assertEqual(packet["execution"]["average_holding_days"], 3.4)
        self.assertGreater(packet["execution"]["annualized_turnover"], 0.0)
        self.assertFalse(packet["universe"]["pit_membership_verified"])
        self.assertFalse(packet["universe"]["delisting_coverage_verified"])
        self.assertTrue(packet["review_blockers"])
        self.assertNotIn("trade_log", packet)
        self.assertNotIn("scanner", packet)
        self.assertFalse(packet["boundaries"]["registry_write"])
        self.assertFalse(packet["boundaries"]["auto_order"])

    def test_candidate_source_preserves_daily_swing_evidence_for_replay(self) -> None:
        from app.services.backtest_practical_validation_source import (
            build_selection_source_from_candidate_draft,
        )

        evidence = {
            "schema_version": "daily_swing_evidence_v1",
            "strategy_key": "risk_on_momentum_5d",
            "status": "REVIEW",
            "review_blockers": ["PIT membership not verified"],
        }
        source = build_selection_source_from_candidate_draft(
            {
                "source_kind": "latest_backtest_run",
                "strategy_key": "risk_on_momentum_5d",
                "strategy_name": "Risk-On Momentum 5D",
                "result_snapshot": {"start_date": "2024-01-01", "end_date": "2025-01-01"},
                "settings_snapshot": {
                    "universe_mode": "top1000",
                    "analysis_intensity": "standard",
                },
                "daily_swing_evidence_snapshot": evidence,
            }
        )

        self.assertEqual(source["daily_swing_evidence_snapshot"], evidence)
        self.assertEqual(
            source["components"][0]["replay_contract"]["daily_swing_evidence_snapshot"],
            evidence,
        )

    def test_daily_swing_replay_uses_quick_runtime_with_preserved_strategy_rules(self) -> None:
        from app.services.backtest_practical_validation_replay import (
            build_risk_on_momentum_replay_kwargs,
        )

        kwargs = build_risk_on_momentum_replay_kwargs(
            {
                "tickers": [],
                "start": "2024-01-01",
                "end": "2025-01-01",
                "universe_mode": "top1000",
                "preset_name": "Top1000",
                "universe_limit": 1000,
                "start_balance": 25_000.0,
                "execution_mode": "close_based",
                "exit_mode": "atr_based",
                "max_holding_days": 5,
                "atr_period": 14,
                "stop_atr_multiple": 1.0,
                "take_profit_atr_multiple": 2.0,
                "macro_filter_mode": "ranking_penalty",
                "transaction_cost_bps": 5.0,
                "slippage_bps": 3.0,
                "option": "month_end",
            }
        )

        self.assertEqual(kwargs["analysis_intensity"], "quick")
        self.assertEqual(kwargs["option"], "close_based")
        self.assertEqual(kwargs["universe_mode"], "top1000")
        self.assertEqual(kwargs["exit_mode"], "atr_based")
        self.assertEqual(kwargs["macro_filter_mode"], "ranking_penalty")
        self.assertEqual(kwargs["start_balance"], 25_000.0)
        self.assertEqual(kwargs["transaction_cost_bps"], 5.0)
        self.assertEqual(kwargs["slippage_bps"], 3.0)

    def test_daily_swing_component_title_routes_to_risk_on_replay_runtime(self) -> None:
        from app.services import backtest_practical_validation_replay as replay_service

        payload = replay_service._component_payload(
            {"period": {"start": "2024-01-01", "end": "2025-01-01"}},
            {
                "title": "Risk-On Momentum 5D",
                "target_weight": 100.0,
                "contract": {"tickers": ["AAPL", "MSFT"]},
            },
        )

        self.assertEqual(payload["strategy_key"], "risk_on_momentum_5d")
        expected = {"result_df": pd.DataFrame()}
        with patch.object(
            replay_service,
            "run_risk_on_momentum_5d_backtest_from_db",
            return_value=expected,
        ) as run_risk_on:
            result = replay_service._run_payload(payload)

        self.assertIs(result, expected)
        run_risk_on.assert_called_once()
        self.assertEqual(run_risk_on.call_args.kwargs["analysis_intensity"], "quick")

    def test_run_history_preserves_compact_daily_swing_replay_contract(self) -> None:
        from app.runtime.backtest.stores.run_history import append_backtest_run_history

        evidence = {
            "schema_version": "daily_swing_evidence_v1",
            "strategy_key": "risk_on_momentum_5d",
            "status": "REVIEW",
            "review_blockers": ["PIT membership not verified"],
        }
        bundle = {
            "summary_df": pd.DataFrame(
                [
                    {
                        "Name": "Risk-On Momentum 5D",
                        "Start Date": "2024-07-26",
                        "End Date": "2026-07-24",
                        "Start Balance": 10_000.0,
                        "End Balance": 12_000.0,
                        "CAGR": 0.095,
                        "Standard Deviation": 0.2,
                        "Sharpe Ratio": 0.5,
                        "Maximum Drawdown": -0.18,
                    }
                ]
            ),
            "meta": {
                "strategy_key": "risk_on_momentum_5d",
                "start": "2024-07-26",
                "end": "2026-07-24",
                "analysis_intensity": "standard",
                "daily_swing_evidence": evidence,
            },
        }

        with tempfile.TemporaryDirectory() as directory:
            history_path = Path(directory) / "history.jsonl"
            with patch(
                "app.runtime.backtest.stores.run_history.BACKTEST_HISTORY_FILE",
                history_path,
            ):
                append_backtest_run_history(bundle=bundle, run_kind="single")
            record = json.loads(history_path.read_text(encoding="utf-8"))

        self.assertEqual(record["analysis_intensity"], "standard")
        self.assertEqual(record["daily_swing_evidence"], evidence)

    def test_daily_swing_validation_is_required_and_fail_closed_without_evidence(self) -> None:
        from app.services.backtest_daily_swing_validation import (
            build_daily_swing_validation,
        )
        from app.services.backtest_practical_validation_modules import (
            infer_validation_source_traits,
        )

        source = {
            "components": [
                {
                    "strategy_key": "risk_on_momentum_5d",
                    "target_weight": 100.0,
                    "replay_contract": {"settings_snapshot": {"analysis_intensity": "standard"}},
                }
            ]
        }
        traits = infer_validation_source_traits(source)
        missing = build_daily_swing_validation(source)

        self.assertTrue(traits["is_daily_swing"])
        self.assertFalse(traits["is_etf_like"])
        self.assertTrue(traits["is_high_turnover"])
        self.assertEqual(missing["status"], "NEEDS_INPUT")
        self.assertEqual(missing["evidence_state"], "missing")
        self.assertTrue(missing["blockers"])

    def test_daily_swing_validation_keeps_current_membership_as_review_limitation(self) -> None:
        from app.services.backtest_daily_swing_validation import (
            build_daily_swing_validation,
        )

        source = {
            "daily_swing_evidence_snapshot": {
                "schema_version": "daily_swing_evidence_v1",
                "strategy_key": "risk_on_momentum_5d",
                "status": "REVIEW",
                "performance": {"trade_count": 120},
                "execution": {
                    "average_holding_days": 3.4,
                    "annualized_turnover": 8.2,
                    "transaction_cost_bps": 5.0,
                    "slippage_bps": 3.0,
                },
                "robustness": {
                    "analysis_intensity": "standard",
                    "best_benchmark": {"label": "SPY Buy & Hold", "cagr": 0.08},
                    "random_median_cagr": 0.04,
                },
                "universe": {
                    "pit_membership_verified": False,
                    "delisting_coverage_verified": False,
                },
                "artifact": {"raw_rows_embedded": False, "trade_row_count": 120},
                "review_blockers": [
                    "Historical PIT universe membership is not verified.",
                ],
            },
            "components": [
                {"strategy_key": "risk_on_momentum_5d", "target_weight": 100.0}
            ],
        }

        validation = build_daily_swing_validation(source)

        self.assertEqual(validation["status"], "REVIEW")
        self.assertEqual(validation["evidence_state"], "computed")
        self.assertFalse(validation["blockers"])
        self.assertTrue(validation["review_required"])
        self.assertEqual(
            {row["Criteria"]: row["Status"] for row in validation["rows"]}[
                "Universe survivorship / PIT"
            ],
            "REVIEW",
        )

    def test_daily_swing_selected_route_policy_is_manual_daily_and_stale_after_one_day(self) -> None:
        from app.services.backtest_daily_swing_policy import build_daily_swing_policy

        blocked = build_daily_swing_policy(
            {
                "daily_swing_validation": {
                    "applies": True,
                    "status": "NEEDS_INPUT",
                    "blockers": ["Compact evidence"],
                }
            }
        )
        review = build_daily_swing_policy(
            {
                "daily_swing_validation": {
                    "applies": True,
                    "status": "REVIEW",
                    "review_required": ["Universe survivorship / PIT"],
                }
            }
        )

        self.assertFalse(blocked["selected_route_allowed"])
        self.assertTrue(blocked["blockers"])
        self.assertTrue(review["selected_route_allowed"])
        self.assertEqual(review["review_cadence"], "daily_after_market_close")
        self.assertEqual(review["stale_after_market_days"], 1)
        self.assertTrue(review["manual_recheck_required"])
        self.assertFalse(review["auto_order"])
        self.assertFalse(review["auto_rebalance"])
        self.assertTrue(review["monitoring_conditions"])

    def test_governance_read_model_is_streamlit_free_and_implemented(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance

        governance = build_risk_on_momentum_governance()

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(governance["strategy_key"], "risk_on_momentum_5d")
        self.assertEqual(governance["status"], "Governance implemented")
        self.assertEqual(governance["lane"], "Daily Swing validation and monitoring lane")
        self.assertTrue(governance["promoted_to_practical_validation"])
        self.assertTrue(governance["promoted_to_final_review"])
        self.assertFalse(governance["monitoring_signal_enabled"])
        self.assertIn("does not write", governance["storage_boundary"])
        self.assertIn("manual-review", governance["route_boundary"])

    def test_required_modules_separate_research_evidence_from_missing_governance(self) -> None:
        from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance

        governance = build_risk_on_momentum_governance()
        module_keys = {row["module_key"] for row in governance["required_modules"]}

        self.assertEqual(
            module_keys,
            {
                "research_evidence_review",
                "daily_swing_practical_validation",
                "final_review_selected_route_rule",
                "portfolio_monitoring_daily_policy",
                "artifact_trade_log_storage_boundary",
                "universe_survivorship_review",
            },
        )

        rows_by_key = {row["module_key"]: row for row in governance["required_modules"]}
        self.assertEqual(rows_by_key["research_evidence_review"]["readiness"], "Available for review")
        for module_key in module_keys:
            row = rows_by_key[module_key]
            self.assertIn(row["readiness"], {"Available for review", "Implemented"})
            self.assertFalse(row["blocker"], f"{module_key} retained blocker")
            self.assertTrue(row["next_action"], f"{module_key} missing next_action")

    def test_governance_rules_start_as_review_evidence_not_monitoring_signal(self) -> None:
        from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance

        governance = build_risk_on_momentum_governance()

        self.assertGreaterEqual(len(governance["research_evidence"]), 5)
        evidence_labels = " ".join(row["evidence"] for row in governance["research_evidence"])
        self.assertIn("Swing Detail", evidence_labels)
        self.assertIn("trade log", evidence_labels)
        self.assertIn("scanner", evidence_labels)

        rule_text = " ".join(governance["governance_rules"])
        self.assertIn("review evidence", rule_text)
        self.assertIn("not an automatic monitoring signal", rule_text)
        self.assertIn("Daily Swing", rule_text)

    def test_risk_on_catalog_is_production_and_no_longer_in_development_group(self) -> None:
        from app.services.backtest_strategy_catalog import (
            LEVEL1_STRATEGY_MATURITY,
            LEVEL1_STRATEGY_PURPOSE_GROUPS,
        )

        self.assertEqual(LEVEL1_STRATEGY_MATURITY["Risk-On Momentum 5D"], "production")
        self.assertNotIn("development", LEVEL1_STRATEGY_PURPOSE_GROUPS)
        self.assertIn(
            "Risk-On Momentum 5D",
            LEVEL1_STRATEGY_PURPOSE_GROUPS["tactical_allocation"]["items"],
        )

    def test_governance_rows_are_returned_as_copies(self) -> None:
        from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance

        first = build_risk_on_momentum_governance()
        first["required_modules"][0]["readiness"] = "mutated"
        first["governance_rules"].append("mutated")

        fresh = build_risk_on_momentum_governance()

        self.assertNotEqual(fresh["required_modules"][0]["readiness"], "mutated")
        self.assertNotIn("mutated", fresh["governance_rules"])


if __name__ == "__main__":
    unittest.main()
