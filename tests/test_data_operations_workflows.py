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

    def test_history_filters_out_non_data_operations_and_compatibility_runs(self) -> None:
        from app.web.ingestion.views.history import filter_data_operations_history

        records = [
            {"job_name": "daily_market_update"},
            {"job_name": "weekly_fundamental_refresh"},
            {"job_name": "portfolio_monitoring_price_refresh"},
            {"job_name": "collect_market_sentiment"},
        ]

        filtered = filter_data_operations_history(records)

        self.assertEqual(
            [record["job_name"] for record in filtered],
            ["daily_market_update", "collect_market_sentiment"],
        )

    def test_history_row_is_compact_and_does_not_expose_raw_paths(self) -> None:
        from app.web.ingestion.views.history import build_data_activity_row

        row = build_data_activity_row(
            {
                "job_name": "collect_futures_ohlcv",
                "status": "success",
                "finished_at": "2026-07-23 07:27:19",
                "rows_written": 42486,
                "symbols_requested": 17,
                "artifact_path": "/private/tmp/raw-result.json",
                "failure_csv": "/private/tmp/failures.csv",
                "details": {"log_path": "/private/tmp/collector.log"},
            }
        )

        self.assertEqual(
            set(row),
            {"실행 시각", "작업", "목적", "상태", "범위", "결과", "다음 행동"},
        )
        self.assertNotIn("/private/", repr(row))
        self.assertEqual(row["범위"], "17개 대상")
        self.assertEqual(row["결과"], "42,486 rows 저장")

    def test_partial_history_row_explains_next_action(self) -> None:
        from app.web.ingestion.views.history import build_data_activity_row

        row = build_data_activity_row(
            {
                "job_name": "daily_market_update",
                "status": "partial_success",
                "rows_written": 980,
                "symbols_requested": 1000,
                "failed_symbols": ["AAA", "BBB"],
            }
        )

        self.assertEqual(row["상태"], "부분 성공")
        self.assertIn("Price Stale Diagnosis", row["다음 행동"])
        self.assertIn("2개 누락/실패", row["결과"])


if __name__ == "__main__":
    unittest.main()
