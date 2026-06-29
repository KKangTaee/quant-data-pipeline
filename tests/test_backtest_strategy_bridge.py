from __future__ import annotations

import sys
import unittest


class BacktestStrategyBridgeContractTests(unittest.TestCase):
    def test_bridge_is_streamlit_free_and_contains_only_first_mature_group(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_strategy_bridge import build_strict_annual_etf_bridge

        bridge = build_strict_annual_etf_bridge()
        rows = bridge["rows"]
        row_keys = {row["strategy_key"] for row in rows}

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(
            row_keys,
            {
                "equal_weight",
                "gtaa",
                "quality_snapshot_strict_annual",
                "value_snapshot_strict_annual",
                "quality_value_snapshot_strict_annual",
            },
        )
        self.assertEqual(set(bridge["bridge_group_keys"]), row_keys)

        excluded = set(bridge["deferred_exclusions"])
        self.assertIn("risk_on_momentum_5d", excluded)
        self.assertIn("quality_snapshot_strict_quarterly_prototype", excluded)
        self.assertIn("global_relative_strength", excluded)
        self.assertTrue(row_keys.isdisjoint(excluded))

    def test_bridge_rows_explain_role_target_validation_and_next_workflow(self) -> None:
        from app.services.backtest_strategy_bridge import build_strict_annual_etf_bridge

        bridge = build_strict_annual_etf_bridge()

        self.assertEqual(bridge["status"], "Read-only bridge")
        self.assertIn("Practical Validation", bridge["candidate_intent"])
        self.assertIn("does not write", bridge["storage_boundary"])
        self.assertIn("Final Review", bridge["route_boundary"])
        self.assertGreaterEqual(len(bridge["validation_checklist"]), 5)

        for row in bridge["rows"]:
            for field in (
                "display_name",
                "bridge_role",
                "target_use",
                "current_anchor",
                "known_weakness",
                "recommended_next_workflow",
                "route_boundary",
            ):
                self.assertTrue(row[field], f"{row['strategy_key']} missing {field}")
            required = row["required_practical_validation_evidence"]
            self.assertIsInstance(required, list)
            self.assertGreaterEqual(len(required), 3)
            self.assertIn("Practical Validation", row["recommended_next_workflow"])
            self.assertIn("Final Review", row["route_boundary"])

    def test_bridge_has_specific_core_and_sleeve_roles(self) -> None:
        from app.services.backtest_strategy_bridge import build_strict_annual_etf_bridge

        rows_by_key = {row["strategy_key"]: row for row in build_strict_annual_etf_bridge()["rows"]}

        self.assertIn("core", rows_by_key["quality_value_snapshot_strict_annual"]["bridge_role"].lower())
        self.assertIn("return engine", rows_by_key["value_snapshot_strict_annual"]["bridge_role"].lower())
        self.assertIn("stabilizer", rows_by_key["quality_snapshot_strict_annual"]["bridge_role"].lower())
        self.assertIn("tactical sleeve", rows_by_key["gtaa"]["bridge_role"].lower())
        self.assertIn("baseline sleeve", rows_by_key["equal_weight"]["bridge_role"].lower())

    def test_bridge_rows_are_returned_as_copies(self) -> None:
        from app.services.backtest_strategy_bridge import build_strict_annual_etf_bridge

        first = build_strict_annual_etf_bridge()
        first["rows"][0]["bridge_role"] = "mutated"
        first["validation_checklist"].append("mutated")

        fresh = build_strict_annual_etf_bridge()

        self.assertNotEqual(fresh["rows"][0]["bridge_role"], "mutated")
        self.assertNotIn("mutated", fresh["validation_checklist"])


if __name__ == "__main__":
    unittest.main()
