from __future__ import annotations

import inspect
import unittest

import pandas as pd


QUARTERLY_KEYS = {
    "quality_snapshot_strict_quarterly_prototype",
    "value_snapshot_strict_quarterly_prototype",
    "quality_value_snapshot_strict_quarterly_prototype",
}


class BacktestQuarterlyProductionizationTests(unittest.TestCase):
    def test_post_run_readiness_reads_quarterly_statement_shadow_gaps(self) -> None:
        from app.web.backtest_common import build_post_run_factor_readiness_panel_model

        model = build_post_run_factor_readiness_panel_model(
            {
                "strategy_name": "Quality Snapshot (Strict Quarterly)",
                "meta": {
                    "strategy_key": "quality_snapshot_strict_quarterly_prototype",
                    "factor_freq": "quarterly",
                    "statement_shadow_coverage": {
                        "requested_count": 3,
                        "covered_count": 2,
                        "missing_count": 1,
                        "missing_symbols": ["MRSH"],
                        "raw_present_missing_symbols": [],
                        "no_raw_missing_symbols": ["MRSH"],
                        "min_period_end": "2021-03-31",
                        "max_period_end": "2026-03-31",
                        "row_count": 42,
                    },
                },
                "result_df": pd.DataFrame({"Date": ["2026-06-30"], "Selected Count": [2]}),
            }
        )

        check_ids = [check["id"] for check in model["checks"]]
        self.assertIn("statement_shadow", check_ids)
        statement_check = next(check for check in model["checks"] if check["id"] == "statement_shadow")
        self.assertEqual(statement_check["symbols"], ["MRSH"])
        self.assertEqual(statement_check["action"]["id"], "refresh_statement_shadow")
        self.assertTrue(statement_check["action"]["enabled"])
        self.assertFalse(model["run_recommended"])

    def test_quarterly_runners_accept_annual_like_contract_inputs(self) -> None:
        from app.runtime.backtest.runners.strict_factor import (
            run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
            run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
            run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
        )

        required = {
            "min_price_filter",
            "min_history_months_filter",
            "min_avg_dollar_volume_20d_m_filter",
            "transaction_cost_bps",
            "benchmark_contract",
            "benchmark_ticker",
            "guardrail_reference_ticker",
            "promotion_min_benchmark_coverage",
            "promotion_min_net_cagr_spread",
            "promotion_min_liquidity_clean_coverage",
            "promotion_max_underperformance_share",
            "promotion_min_worst_rolling_excess_return",
            "promotion_max_strategy_drawdown",
            "promotion_max_drawdown_gap_vs_benchmark",
            "underperformance_guardrail_enabled",
            "underperformance_guardrail_window_months",
            "underperformance_guardrail_threshold",
            "drawdown_guardrail_enabled",
            "drawdown_guardrail_window_months",
            "drawdown_guardrail_strategy_threshold",
            "drawdown_guardrail_gap_threshold",
        }

        for runner in (
            run_quality_snapshot_strict_quarterly_prototype_backtest_from_db,
            run_value_snapshot_strict_quarterly_prototype_backtest_from_db,
            run_quality_value_snapshot_strict_quarterly_prototype_backtest_from_db,
        ):
            params = set(inspect.signature(runner).parameters)
            self.assertTrue(required.issubset(params), runner.__name__)

    def test_quarterly_catalog_and_evidence_are_formal_not_prototype(self) -> None:
        from app.runtime.backtest.runner_catalog import get_runner_definition
        from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME
        from app.services.backtest_strategy_evidence_inventory import build_strategy_evidence_inventory

        rows = {row["strategy_key"]: row for row in build_strategy_evidence_inventory()}
        for strategy_key in QUARTERLY_KEYS:
            display_name = STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key]
            self.assertNotIn("Prototype", display_name)
            self.assertNotIn("Prototype", get_runner_definition(strategy_key).display_name)

            row = rows[strategy_key]
            self.assertEqual(row["maturity_group"], "Evidence mature")
            self.assertNotIn("prototype", row["maturity_label"].lower())
            self.assertIn("Practical Validation", row["validation_readiness"])


if __name__ == "__main__":
    unittest.main()
