from __future__ import annotations

import sys
import unittest


class BacktestStrategyEvidenceInventoryContractTests(unittest.TestCase):
    def test_inventory_is_streamlit_free_and_covers_every_catalog_strategy_key(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_strategy_evidence_inventory import build_strategy_evidence_inventory
        from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME

        rows = build_strategy_evidence_inventory()
        rows_by_key = {row["strategy_key"]: row for row in rows}

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(set(rows_by_key), set(STRATEGY_KEY_TO_DISPLAY_NAME))
        self.assertEqual(len(rows), len(rows_by_key))

        for strategy_key, display_name in STRATEGY_KEY_TO_DISPLAY_NAME.items():
            row = rows_by_key[strategy_key]
            self.assertEqual(row["display_name"], display_name)
            for required_field in (
                "family",
                "intended_role",
                "maturity_label",
                "runtime_support",
                "compare_support",
                "replay_support",
                "validation_readiness",
                "monitoring_readiness",
                "current_anchor",
                "main_weakness",
                "next_action",
            ):
                self.assertTrue(row[required_field], f"{strategy_key} missing {required_field}")

    def test_research_lane_and_prototype_labels_are_explicit(self) -> None:
        from app.services.backtest_strategy_evidence_inventory import build_strategy_evidence_inventory

        rows_by_key = {row["strategy_key"]: row for row in build_strategy_evidence_inventory()}

        risk_on = rows_by_key["risk_on_momentum_5d"]
        self.assertEqual(risk_on["product_lane"], "Backtest Analysis research lane")
        self.assertEqual(risk_on["governance_status"], "Deferred")
        self.assertIn("governance deferred", risk_on["governance_note"].lower())

        quarterly_keys = {
            "quality_snapshot_strict_quarterly_prototype",
            "value_snapshot_strict_quarterly_prototype",
            "quality_value_snapshot_strict_quarterly_prototype",
        }
        for strategy_key in quarterly_keys:
            row = rows_by_key[strategy_key]
            self.assertEqual(row["maturity_label"], "Prototype / contract-smoke")
            self.assertIn("prototype", row["validation_readiness"].lower())
            self.assertIn("quarterly maturation", row["next_action"].lower())

    def test_first_evidence_mature_candidate_group_is_fixed(self) -> None:
        from app.services.backtest_strategy_evidence_inventory import build_strategy_evidence_inventory

        expected_group = {
            "equal_weight",
            "gtaa",
            "quality_snapshot_strict_annual",
            "value_snapshot_strict_annual",
            "quality_value_snapshot_strict_annual",
        }
        rows = build_strategy_evidence_inventory()
        actual_group = {
            row["strategy_key"]
            for row in rows
            if row["candidate_group"] == "First evidence-mature candidate group"
        }

        self.assertEqual(actual_group, expected_group)
        rows_by_key = {row["strategy_key"]: row for row in rows}
        for strategy_key in expected_group:
            row = rows_by_key[strategy_key]
            self.assertEqual(row["maturity_group"], "Evidence mature")
            self.assertIn("Practical Validation", row["next_action"])

    def test_inventory_rows_are_returned_as_copies(self) -> None:
        from app.services.backtest_strategy_evidence_inventory import build_strategy_evidence_inventory

        first = build_strategy_evidence_inventory()
        first[0]["next_action"] = "mutated"

        fresh = build_strategy_evidence_inventory()

        self.assertNotEqual(fresh[0]["next_action"], "mutated")

    def test_web_strategy_catalog_wrapper_matches_service_catalog(self) -> None:
        from app.services import backtest_strategy_catalog as service_catalog
        from app.web import backtest_strategy_catalog as web_catalog

        self.assertEqual(web_catalog.STRATEGY_KEY_TO_DISPLAY_NAME, service_catalog.STRATEGY_KEY_TO_DISPLAY_NAME)
        self.assertEqual(web_catalog.SINGLE_STRATEGY_OPTIONS, service_catalog.SINGLE_STRATEGY_OPTIONS)
        self.assertEqual(web_catalog.STRATEGY_FAMILY_VARIANTS, service_catalog.STRATEGY_FAMILY_VARIANTS)


if __name__ == "__main__":
    unittest.main()
