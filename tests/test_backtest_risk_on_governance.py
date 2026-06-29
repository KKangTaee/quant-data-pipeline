from __future__ import annotations

import sys
import unittest


class BacktestRiskOnGovernanceContractTests(unittest.TestCase):
    def test_governance_read_model_is_streamlit_free_and_deferred(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance

        governance = build_risk_on_momentum_governance()

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(governance["strategy_key"], "risk_on_momentum_5d")
        self.assertEqual(governance["status"], "Governance deferred")
        self.assertEqual(governance["lane"], "Backtest Analysis research lane")
        self.assertFalse(governance["promoted_to_practical_validation"])
        self.assertFalse(governance["promoted_to_final_review"])
        self.assertFalse(governance["monitoring_signal_enabled"])
        self.assertIn("does not write", governance["storage_boundary"])
        self.assertIn("not a Portfolio Monitoring signal", governance["route_boundary"])

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
        for module_key in module_keys - {"research_evidence_review"}:
            row = rows_by_key[module_key]
            self.assertIn(row["readiness"], {"Deferred", "Needs design"})
            self.assertTrue(row["blocker"], f"{module_key} missing blocker")
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
