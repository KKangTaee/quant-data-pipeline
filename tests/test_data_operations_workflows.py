from pathlib import Path
import unittest


class DataOperationsPageContractTest(unittest.TestCase):
    def test_data_operations_page_does_not_render_contextual_reference_help(
        self,
    ) -> None:
        page_source = Path("app/web/ingestion/page.py").read_text(encoding="utf-8")

        self.assertNotIn(
            "from app.web.reference_contextual_help import "
            "render_reference_contextual_help",
            page_source,
        )
        self.assertNotIn(
            'render_reference_contextual_help("ingestion"',
            page_source,
        )

    def test_secondary_views_do_not_repeat_selected_section_title(
        self,
    ) -> None:
        repeated_subheaders = {
            "app/web/ingestion/views/imports.py": 'st.subheader("공식 파일 가져오기")',
            "app/web/ingestion/views/recovery.py": 'st.subheader("문제 복구")',
            "app/web/ingestion/views/history.py": 'st.subheader("실행 이력")',
            "app/web/ingestion/views/advanced.py": 'st.subheader("고급 도구")',
        }

        for path, repeated_subheader in repeated_subheaders.items():
            with self.subTest(path=path):
                source = Path(path).read_text(encoding="utf-8")
                self.assertNotIn(repeated_subheader, source)


class DataOperationsWorkflowContractTest(unittest.TestCase):
    def test_advanced_tools_are_closed_without_action_focus(self) -> None:
        from app.web.ingestion import sections

        self.assertTrue(hasattr(sections, "should_expand_action"))
        self.assertFalse(
            sections.should_expand_action(None, "daily_market_update")
        )

    def test_advanced_tools_open_only_matching_action_focus(self) -> None:
        from app.web.ingestion import sections

        self.assertTrue(hasattr(sections, "should_expand_action"))
        self.assertTrue(
            sections.should_expand_action(
                "daily_market_update",
                "daily_market_update",
            )
        )
        self.assertFalse(
            sections.should_expand_action(
                "metadata_refresh",
                "daily_market_update",
            )
        )

    def test_advanced_sections_share_focus_only_expansion_rule(self) -> None:
        source = Path("app/web/ingestion/sections.py").read_text(
            encoding="utf-8"
        )

        self.assertNotIn("default=True", source)
        self.assertNotIn("def expand_for(", source)
        self.assertGreaterEqual(
            source.count("expanded=should_expand_action("),
            2,
        )

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

    def test_leaving_advanced_clears_sticky_action_focus(self) -> None:
        from app.web.ingestion import navigation

        state: dict[str, object] = {
            navigation.FOCUSED_ACTION_STATE_KEY: "daily_market_update",
        }

        self.assertTrue(
            hasattr(navigation, "clear_action_focus_outside_advanced")
        )
        navigation.clear_action_focus_outside_advanced(
            state,
            "문제 복구",
        )

        self.assertNotIn(navigation.FOCUSED_ACTION_STATE_KEY, state)

    def test_advanced_rerun_preserves_current_action_focus(self) -> None:
        from app.web.ingestion import navigation
        from app.web.ingestion.workflows import (
            DATA_OPERATIONS_SECTION_ADVANCED,
        )

        state: dict[str, object] = {
            navigation.FOCUSED_ACTION_STATE_KEY: "daily_market_update",
        }

        self.assertTrue(
            hasattr(navigation, "clear_action_focus_outside_advanced")
        )
        navigation.clear_action_focus_outside_advanced(
            state,
            DATA_OPERATIONS_SECTION_ADVANCED,
        )

        self.assertEqual(
            state[navigation.FOCUSED_ACTION_STATE_KEY],
            "daily_market_update",
        )

    def test_widget_callback_queues_section_change_for_next_rerun(self) -> None:
        from app.web.ingestion.navigation import (
            FOCUSED_ACTION_STATE_KEY,
            PENDING_SECTION_STATE_KEY,
            SECTION_STATE_KEY,
            queue_action_focus,
        )
        from app.web.ingestion.workflows import DATA_OPERATIONS_SECTION_ADVANCED

        state: dict[str, object] = {
            SECTION_STATE_KEY: "데이터 준비",
        }

        queue_action_focus(state, "collect_market_sentiment")

        self.assertEqual(state[SECTION_STATE_KEY], "데이터 준비")
        self.assertEqual(
            state[PENDING_SECTION_STATE_KEY],
            DATA_OPERATIONS_SECTION_ADVANCED,
        )
        self.assertEqual(
            state[FOCUSED_ACTION_STATE_KEY],
            "collect_market_sentiment",
        )

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
