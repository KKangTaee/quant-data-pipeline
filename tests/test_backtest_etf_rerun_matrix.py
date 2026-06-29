from __future__ import annotations

import sys
import unittest

import pandas as pd


def _fake_bundle(
    *,
    strategy_key: str,
    result_rows: int = 120,
    cagr: float = 0.11,
    mdd: float = -0.18,
    sharpe: float = 0.92,
    warning_count: int = 1,
) -> dict[str, object]:
    return {
        "meta": {
            "strategy_key": strategy_key,
            "actual_result_start": "2020-01-31",
            "actual_result_end": "2026-05-31",
            "result_rows": result_rows,
            "price_freshness": {"status": "ok"},
            "promotion_decision": "review_required",
            "warnings": ["review stale ETF data"] * warning_count,
        },
        "summary_df": pd.DataFrame(
            [
                {
                    "CAGR": cagr,
                    "Maximum Drawdown": mdd,
                    "Sharpe Ratio": sharpe,
                }
            ]
        ),
    }


class BacktestEtfRerunMatrixTests(unittest.TestCase):
    def test_plan_is_streamlit_free_read_only_and_targets_etf_expansion_strategies(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_etf_rerun_matrix import build_etf_rerun_matrix_plan

        plan = build_etf_rerun_matrix_plan()
        row_keys = {row["strategy_key"] for row in plan["rows"]}

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(plan["status"], "Session-only ETF rerun matrix plan")
        self.assertEqual(
            row_keys,
            {
                "global_relative_strength",
                "risk_parity_trend",
                "dual_momentum",
            },
        )
        self.assertGreaterEqual(plan["scenario_count"], 6)
        self.assertFalse(plan["runs_backtests_on_render"])
        self.assertFalse(plan["writes_run_history"])
        self.assertFalse(plan["writes_validation_results"])
        self.assertFalse(plan["creates_current_candidate"])
        self.assertIn("session state only", plan["storage_boundary"])

    def test_run_matrix_executes_only_selected_strategy_with_injected_runner(self) -> None:
        from app.services.backtest_etf_rerun_matrix import run_etf_rerun_matrix

        calls: list[dict[str, object]] = []

        def fake_runner(**kwargs: object) -> dict[str, object]:
            calls.append(dict(kwargs))
            return _fake_bundle(strategy_key="global_relative_strength")

        result = run_etf_rerun_matrix(
            "global_relative_strength",
            runner_map={"global_relative_strength": fake_runner},
        )

        self.assertEqual(result["strategy_key"], "global_relative_strength")
        self.assertEqual(result["status"], "COMPLETED")
        self.assertEqual(result["scenario_count"], len(calls))
        self.assertEqual(result["pass_count"], len(calls))
        self.assertEqual(result["error_count"], 0)
        self.assertFalse(result["writes_run_history"])
        self.assertGreaterEqual(len(calls), 2)
        self.assertTrue(all(call["universe_mode"] == "preset" for call in calls))
        self.assertTrue(all(row["status"] == "PASS" for row in result["rows"]))
        self.assertEqual(result["rows"][0]["cagr"], 0.11)
        self.assertEqual(result["rows"][0]["maximum_drawdown"], -0.18)
        self.assertEqual(result["rows"][0]["sharpe_ratio"], 0.92)
        self.assertEqual(result["rows"][0]["price_freshness_status"], "ok")
        self.assertEqual(result["rows"][0]["promotion_decision"], "review_required")
        self.assertEqual(result["rows"][0]["warning_count"], 1)

    def test_run_matrix_captures_scenario_errors_without_stopping_remaining_rows(self) -> None:
        from app.services.backtest_etf_rerun_matrix import run_etf_rerun_matrix

        calls: list[dict[str, object]] = []

        def fake_runner(**kwargs: object) -> dict[str, object]:
            calls.append(dict(kwargs))
            if len(calls) == 2:
                raise RuntimeError("missing DB prices")
            return _fake_bundle(strategy_key="risk_parity_trend", result_rows=90)

        result = run_etf_rerun_matrix(
            "risk_parity_trend",
            runner_map={"risk_parity_trend": fake_runner},
        )
        statuses = [row["status"] for row in result["rows"]]

        self.assertEqual(result["status"], "COMPLETED_WITH_ERRORS")
        self.assertIn("PASS", statuses)
        self.assertIn("ERROR", statuses)
        self.assertEqual(result["error_count"], 1)
        self.assertEqual(result["pass_count"], len(calls) - 1)
        error_row = next(row for row in result["rows"] if row["status"] == "ERROR")
        self.assertIn("missing DB prices", error_row["error"])

    def test_unsupported_strategy_key_is_rejected(self) -> None:
        from app.services.backtest_etf_rerun_matrix import run_etf_rerun_matrix

        with self.assertRaisesRegex(ValueError, "Unsupported ETF rerun matrix strategy"):
            run_etf_rerun_matrix("gtaa", runner_map={})

    def test_plan_and_results_are_returned_as_copies(self) -> None:
        from app.services.backtest_etf_rerun_matrix import (
            build_etf_rerun_matrix_plan,
            run_etf_rerun_matrix,
        )

        plan = build_etf_rerun_matrix_plan()
        plan["rows"][0]["scenarios"][0]["params"]["top"] = 999

        fresh_plan = build_etf_rerun_matrix_plan()
        self.assertNotEqual(fresh_plan["rows"][0]["scenarios"][0]["params"].get("top"), 999)

        def fake_runner(**kwargs: object) -> dict[str, object]:
            return _fake_bundle(strategy_key="dual_momentum")

        first = run_etf_rerun_matrix("dual_momentum", runner_map={"dual_momentum": fake_runner})
        first["rows"][0]["params"]["top"] = 999

        fresh = run_etf_rerun_matrix("dual_momentum", runner_map={"dual_momentum": fake_runner})
        self.assertNotEqual(fresh["rows"][0]["params"].get("top"), 999)


if __name__ == "__main__":
    unittest.main()
