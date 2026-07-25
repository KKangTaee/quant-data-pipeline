import unittest


class DataOperationsWorkflowContractTest(unittest.TestCase):
    def test_active_actions_are_owned_without_promoting_compatibility_actions(self) -> None:
        from app.web.ingestion.registry import (
            active_ingestion_actions,
            compatibility_ingestion_actions,
        )
        from app.web.ingestion.workflows import (
            ACTION_WORKFLOW_OWNERSHIP,
            validate_workflow_inventory,
        )

        result = validate_workflow_inventory()

        self.assertEqual(
            set(ACTION_WORKFLOW_OWNERSHIP),
            set(active_ingestion_actions()),
        )
        self.assertEqual(result["active_action_count"], 30)
        self.assertEqual(result["unowned_actions"], ())
        self.assertEqual(result["unknown_actions"], ())
        self.assertTrue(
            set(compatibility_ingestion_actions()).isdisjoint(
                ACTION_WORKFLOW_OWNERSHIP,
            )
        )

    def test_shared_actions_keep_one_registry_identity(self) -> None:
        from app.web.ingestion.workflows import ACTION_WORKFLOW_OWNERSHIP

        self.assertEqual(
            ACTION_WORKFLOW_OWNERSHIP["daily_market_update"],
            ("market_research", "portfolio_lab"),
        )
        self.assertEqual(
            ACTION_WORKFLOW_OWNERSHIP["metadata_refresh"],
            ("market_research", "portfolio_lab"),
        )

    def test_action_focus_moves_to_advanced_without_losing_action(self) -> None:
        from app.web.ingestion.navigation import apply_action_focus
        from app.web.ingestion.workflows import DATA_OPERATIONS_SECTION_ADVANCED

        state: dict[str, object] = {}

        apply_action_focus(state, "collect_sec_13f_dataset")

        self.assertEqual(
            state["data_operations_section_choice"],
            DATA_OPERATIONS_SECTION_ADVANCED,
        )
        self.assertEqual(
            state["data_operations_focused_action"],
            "collect_sec_13f_dataset",
        )

    def test_action_focus_rejects_unknown_action_without_mutating_state(self) -> None:
        from app.web.ingestion.navigation import apply_action_focus

        state: dict[str, object] = {"existing": "preserved"}

        with self.assertRaises(KeyError):
            apply_action_focus(state, "unknown_action")

        self.assertEqual(state, {"existing": "preserved"})

    def test_official_import_and_recovery_actions_route_to_legacy_form_sections(self) -> None:
        from app.web.ingestion.registry import (
            INGESTION_COLLECTION_MANUAL,
            INGESTION_COLLECTION_OPERATIONAL,
        )
        from app.web.ingestion.views.advanced import section_for_action

        self.assertEqual(
            section_for_action("import_sp500_index_earnings_xlsx"),
            INGESTION_COLLECTION_OPERATIONAL,
        )
        self.assertEqual(
            section_for_action("diagnose_price_stale"),
            INGESTION_COLLECTION_MANUAL,
        )

    def test_advanced_routing_rejects_inactive_compatibility_action(self) -> None:
        from app.web.ingestion.views.advanced import section_for_action

        with self.assertRaises(KeyError):
            section_for_action("weekly_fundamental_refresh")


if __name__ == "__main__":
    unittest.main()
