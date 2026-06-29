from __future__ import annotations

import sys
import unittest


class ReferenceGuidesCatalogContractTests(unittest.TestCase):
    def test_reference_center_catalog_is_streamlit_free_and_task_first(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.reference_guides_catalog import get_reference_center_catalog

        catalog = get_reference_center_catalog()

        self.assertNotIn("streamlit", sys.modules)
        self.assertIn("task_cards", catalog)
        task_keys = {row["key"] for row in catalog["task_cards"]}
        expected_task_keys = {
            "market_context",
            "data_freshness",
            "candidate_creation",
            "evidence_review",
            "portfolio_monitoring",
            "troubleshooting",
        }
        self.assertGreaterEqual(task_keys, expected_task_keys)

        data_freshness = next(row for row in catalog["task_cards"] if row["key"] == "data_freshness")
        self.assertIn("Workspace > Ingestion", data_freshness["owner_screen"])
        self.assertIn("System / Data Health", data_freshness["owner_screen"])
        self.assertIn("provider fetch", data_freshness["does_not_do"])

    def test_reference_center_has_current_journeys_and_boundaries(self) -> None:
        from app.services.reference_guides_catalog import get_reference_center_catalog

        catalog = get_reference_center_catalog()
        journeys = {row["key"]: row for row in catalog["journeys"]}

        self.assertIn("portfolio_selection", journeys)
        self.assertIn("daily_market_context", journeys)
        self.assertIn("data_freshness_repair", journeys)
        self.assertIn("monitoring_after_selection", journeys)

        portfolio_selection = journeys["portfolio_selection"]
        self.assertEqual(
            portfolio_selection["screens"],
            "Backtest Analysis -> Practical Validation -> Final Review -> Operations > Portfolio Monitoring",
        )
        self.assertIn("broker order", portfolio_selection["boundary"])
        self.assertIn("auto rebalance", portfolio_selection["boundary"])

    def test_reference_center_explains_statuses_records_and_playbooks(self) -> None:
        from app.services.reference_guides_catalog import get_reference_center_catalog

        catalog = get_reference_center_catalog()

        concepts = {row["term"]: row for row in catalog["concepts"]}
        self.assertEqual(concepts["NOT_RUN"]["progress_implication"], "pass가 아니라 evidence missing / not executed")
        self.assertIn("where_to_fix", concepts["BLOCKED"])

        records = {row["record"]: row for row in catalog["records"]}
        self.assertEqual(records["SELECTED_DASHBOARD_PORTFOLIOS.jsonl"]["kind"], "saved setup")
        self.assertIn("보통 커밋하지 않음", records["BACKTEST_RUN_HISTORY.jsonl"]["commit_policy"])

        playbooks = {row["key"]: row for row in catalog["playbooks"]}
        self.assertIn("overview_futures_stale", playbooks)
        self.assertIn("Workspace > Overview", playbooks["overview_futures_stale"]["owner_screen"])
        self.assertIn("latest stored", playbooks["overview_futures_stale"]["first_check"])
        self.assertIn("NOT_RUN", playbooks)
        self.assertIn("Final Review", playbooks["final_review_source_missing"]["owner_screen"])

    def test_journey_details_include_ordered_steps_and_failure_states(self) -> None:
        from app.services.reference_guides_catalog import get_reference_center_catalog

        catalog = get_reference_center_catalog()
        journeys = {row["key"]: row for row in catalog["journeys"]}

        market_context = journeys["daily_market_context"]
        market_steps = market_context["steps"]
        self.assertGreaterEqual(len(market_steps), 3)
        self.assertEqual(market_steps[0]["owner_screen"], "Workspace > Overview")
        self.assertIn("Futures Monitor", market_steps[0]["check"])
        self.assertIn("downstream", market_steps[0])

        data_repair = journeys["data_freshness_repair"]
        data_failures = {row["state"]: row for row in data_repair["failure_states"]}
        self.assertIn("UI가 최신 수집 결과를 못 읽음", data_failures)
        self.assertIn("System / Data Health", data_failures["UI가 최신 수집 결과를 못 읽음"]["owner_screen"])
        self.assertIn("Reference", data_failures["UI가 최신 수집 결과를 못 읽음"]["stop_condition"])

    def test_playbooks_include_check_steps_and_evidence_locations(self) -> None:
        from app.services.reference_guides_catalog import get_reference_center_catalog

        catalog = get_reference_center_catalog()
        playbooks = {row["key"]: row for row in catalog["playbooks"]}

        provider_gap = playbooks["provider_snapshot_missing"]
        self.assertGreaterEqual(len(provider_gap["check_steps"]), 3)
        self.assertEqual(provider_gap["check_steps"][0]["order"], "1")
        self.assertIn("Provider Data Gaps", provider_gap["check_steps"][0]["check"])
        self.assertIn("evidence_locations", provider_gap)
        self.assertIn("ETF provider snapshot DB tables", provider_gap["evidence_locations"])

        archive_recovery = playbooks["archive_recovery"]
        self.assertIn("Operations > Archive: Backtest Runs", archive_recovery["owner_screen"])
        self.assertIn("BACKTEST_RUN_HISTORY.jsonl", archive_recovery["evidence_locations"])


if __name__ == "__main__":
    unittest.main()
