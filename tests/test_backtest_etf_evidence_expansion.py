from __future__ import annotations

import sys
import unittest


class BacktestEtfEvidenceExpansionContractTests(unittest.TestCase):
    def test_etf_evidence_expansion_is_streamlit_free_and_targets_non_mature_etf_strategies(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_etf_evidence_expansion import build_etf_evidence_expansion

        expansion = build_etf_evidence_expansion()
        row_keys = {row["strategy_key"] for row in expansion["rows"]}

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(expansion["status"], "Read-only evidence expansion")
        self.assertEqual(
            row_keys,
            {
                "global_relative_strength",
                "risk_parity_trend",
                "dual_momentum",
            },
        )
        self.assertEqual(set(expansion["target_strategy_keys"]), row_keys)
        self.assertEqual(expansion["baseline_reference_keys"], ["gtaa", "equal_weight"])
        self.assertNotIn("gtaa", row_keys)
        self.assertNotIn("equal_weight", row_keys)
        self.assertIn("does not write", expansion["storage_boundary"])

    def test_each_target_strategy_has_anchor_near_miss_gap_and_next_workflow(self) -> None:
        from app.services.backtest_etf_evidence_expansion import build_etf_evidence_expansion

        expansion = build_etf_evidence_expansion()
        rows_by_key = {row["strategy_key"]: row for row in expansion["rows"]}

        self.assertEqual(rows_by_key["global_relative_strength"]["priority"], "First ETF expansion target")
        self.assertIn("runtime", rows_by_key["global_relative_strength"]["current_anchor"].lower())
        self.assertIn("current candidate", rows_by_key["global_relative_strength"]["not_ready_reason"].lower())

        self.assertIn("low-vol", rows_by_key["risk_parity_trend"]["near_miss"].lower())
        self.assertIn("volatility window", " ".join(rows_by_key["risk_parity_trend"]["required_evidence"]).lower())

        self.assertIn("top-1", rows_by_key["dual_momentum"]["not_ready_reason"].lower())
        self.assertIn("guardrail", " ".join(rows_by_key["dual_momentum"]["required_evidence"]).lower())

        for row in expansion["rows"]:
            for field in (
                "display_name",
                "family",
                "current_anchor",
                "near_miss",
                "not_ready_reason",
                "evidence_gap",
                "next_workflow",
                "route_boundary",
            ):
                self.assertTrue(row[field], f"{row['strategy_key']} missing {field}")
            self.assertIsInstance(row["required_evidence"], list)
            self.assertGreaterEqual(len(row["required_evidence"]), 3)
            self.assertIn("Practical Validation", row["next_workflow"])

    def test_expansion_keeps_candidate_creation_and_reruns_deferred(self) -> None:
        from app.services.backtest_etf_evidence_expansion import build_etf_evidence_expansion

        expansion = build_etf_evidence_expansion()

        self.assertFalse(expansion["creates_current_candidate"])
        self.assertFalse(expansion["runs_backtests"])
        self.assertFalse(expansion["writes_validation_results"])
        self.assertIn("Current candidate registry", expansion["storage_boundary"])
        self.assertIn("Backtest Analysis", expansion["route_boundary"])
        self.assertGreaterEqual(len(expansion["next_workflow_steps"]), 3)

    def test_etf_evidence_rows_are_returned_as_copies(self) -> None:
        from app.services.backtest_etf_evidence_expansion import build_etf_evidence_expansion

        first = build_etf_evidence_expansion()
        first["rows"][0]["priority"] = "mutated"
        first["next_workflow_steps"].append("mutated")

        fresh = build_etf_evidence_expansion()

        self.assertNotEqual(fresh["rows"][0]["priority"], "mutated")
        self.assertNotIn("mutated", fresh["next_workflow_steps"])


if __name__ == "__main__":
    unittest.main()
