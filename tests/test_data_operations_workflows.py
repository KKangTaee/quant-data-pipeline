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


if __name__ == "__main__":
    unittest.main()
