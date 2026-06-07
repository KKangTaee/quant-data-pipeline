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
        self.assertGreaterEqual(
            {
                "market_context",
                "data_freshness",
                "candidate_creation",
                "evidence_review",
                "portfolio_monitoring",
                "troubleshooting",
            },
            task_keys,
        )

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


if __name__ == "__main__":
    unittest.main()
