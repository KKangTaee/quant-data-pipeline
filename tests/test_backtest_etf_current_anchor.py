from __future__ import annotations

import sys
import unittest


class BacktestEtfCurrentAnchorWorkbenchTests(unittest.TestCase):
    def test_workbench_is_streamlit_free_read_only_and_targets_etf_expansion_strategies(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_etf_current_anchor import build_etf_current_anchor_workbench

        workbench = build_etf_current_anchor_workbench(run_history_rows=[], selection_source_rows=[])
        row_keys = {row["strategy_key"] for row in workbench["rows"]}

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(workbench["status"], "Read-only current-anchor workbench")
        self.assertEqual(
            row_keys,
            {
                "global_relative_strength",
                "risk_parity_trend",
                "dual_momentum",
            },
        )
        self.assertFalse(workbench["creates_current_candidate"])
        self.assertFalse(workbench["runs_backtests"])
        self.assertFalse(workbench["writes_validation_results"])
        self.assertIn("does not write", workbench["storage_boundary"])

    def test_latest_run_and_selection_source_are_matched_by_strategy(self) -> None:
        from app.services.backtest_etf_current_anchor import build_etf_current_anchor_workbench

        run_history_rows = [
            {
                "strategy_key": "global_relative_strength",
                "recorded_at": "2026-06-07T09:00:00",
                "actual_result_end": "2026-05-30",
                "result_rows": 200,
                "summary": {"cagr": 0.08, "maximum_drawdown": -0.19, "sharpe_ratio": 0.91},
                "price_freshness": {"status": "ok"},
                "gate_snapshot": {"price_freshness_status": "ok", "promotion_decision": "review_required"},
                "cost_application_status": "applied_to_result_curve",
                "net_cost_curve_status": "measurable",
                "benchmark_policy_status": "PASS",
                "liquidity_policy_status": "PASS",
                "etf_operability_status": "PASS",
            },
            {
                "strategy_key": "global_relative_strength",
                "recorded_at": "2026-06-08T10:00:00",
                "actual_result_end": "2026-06-05",
                "result_rows": 240,
                "summary": {"cagr": 0.12, "maximum_drawdown": -0.17, "sharpe_ratio": 1.05},
                "price_freshness": {"status": "ok"},
                "gate_snapshot": {"price_freshness_status": "ok", "promotion_decision": "review_required"},
                "cost_application_status": "applied_to_result_curve",
                "net_cost_curve_status": "measurable",
                "benchmark_policy_status": "PASS",
                "liquidity_policy_status": "PASS",
                "etf_operability_status": "PASS",
            },
        ]
        selection_source_rows = [
            {
                "selection_source_id": "selection-grs-latest",
                "created_at": "2026-06-08T10:05:00",
                "updated_at": "2026-06-08T10:05:00",
                "source_kind": "latest_backtest_run",
                "components": [{"strategy_key": "global_relative_strength"}],
            }
        ]

        workbench = build_etf_current_anchor_workbench(
            run_history_rows=run_history_rows,
            selection_source_rows=selection_source_rows,
        )
        grs = {row["strategy_key"]: row for row in workbench["rows"]}["global_relative_strength"]

        self.assertEqual(grs["anchor_status"], "ANCHOR_READY_FOR_REVIEW")
        self.assertEqual(grs["latest_run"]["recorded_at"], "2026-06-08T10:00:00")
        self.assertEqual(grs["latest_run"]["actual_result_end"], "2026-06-05")
        self.assertEqual(grs["latest_source"]["selection_source_id"], "selection-grs-latest")
        self.assertEqual(grs["missing_evidence"], [])
        self.assertIn("current anchor review input", grs["recommended_next_action"])

    def test_missing_run_source_and_evidence_are_explicit_gaps(self) -> None:
        from app.services.backtest_etf_current_anchor import build_etf_current_anchor_workbench

        run_history_rows = [
            {
                "strategy_key": "risk_parity_trend",
                "recorded_at": "2026-06-08T11:00:00",
                "actual_result_end": "2026-06-05",
                "result_rows": 180,
                "summary": {"cagr": 0.05, "maximum_drawdown": -0.11, "sharpe_ratio": 0.7},
                "price_freshness": {"status": "ok"},
            }
        ]

        workbench = build_etf_current_anchor_workbench(
            run_history_rows=run_history_rows,
            selection_source_rows=[],
        )
        rows_by_key = {row["strategy_key"]: row for row in workbench["rows"]}

        risk_parity = rows_by_key["risk_parity_trend"]
        self.assertEqual(risk_parity["anchor_status"], "SOURCE_HANDOFF_REQUIRED")
        self.assertIn("selection source", " ".join(risk_parity["missing_evidence"]).lower())
        self.assertIn("provider", " ".join(risk_parity["missing_evidence"]).lower())
        self.assertIn("cost", " ".join(risk_parity["missing_evidence"]).lower())
        self.assertIn("benchmark", " ".join(risk_parity["missing_evidence"]).lower())

        dual = rows_by_key["dual_momentum"]
        self.assertEqual(dual["anchor_status"], "RERUN_REQUIRED")
        self.assertIn("latest DB-backed backtest run", dual["missing_evidence"])
        self.assertIn("Run latest DB-backed Dual Momentum backtest", dual["recommended_next_action"])

    def test_workbench_rows_are_returned_as_copies(self) -> None:
        from app.services.backtest_etf_current_anchor import build_etf_current_anchor_workbench

        first = build_etf_current_anchor_workbench(run_history_rows=[], selection_source_rows=[])
        first["rows"][0]["anchor_status"] = "mutated"
        first["rows"][0]["missing_evidence"].append("mutated")

        fresh = build_etf_current_anchor_workbench(run_history_rows=[], selection_source_rows=[])

        self.assertNotEqual(fresh["rows"][0]["anchor_status"], "mutated")
        self.assertNotIn("mutated", fresh["rows"][0]["missing_evidence"])


if __name__ == "__main__":
    unittest.main()
