from pathlib import Path
import unittest


class IngestionModuleSplitContractsTest(unittest.TestCase):
    def test_ingestion_console_legacy_entrypoint_reexports_package_page(self) -> None:
        from app.web.ingestion import render_ingestion_page as package_entrypoint
        from app.web.ingestion_console import render_ingestion_page as legacy_entrypoint

        self.assertTrue(callable(package_entrypoint))
        self.assertIs(legacy_entrypoint, package_entrypoint)

    def test_ingestion_package_keeps_legacy_console_as_thin_facade(self) -> None:
        source = Path("app/web/ingestion_console.py").read_text(encoding="utf-8")

        self.assertIn("app.web.ingestion.page", source)
        self.assertLess(source.count("\n"), 220)

    def test_ingestion_action_registry_lives_in_registry_module(self) -> None:
        from app.web.ingestion import page
        from app.web.ingestion import registry
        from app.web.ingestion_console import INGESTION_ACTION_REGISTRY

        self.assertIs(page.INGESTION_ACTION_REGISTRY, registry.INGESTION_ACTION_REGISTRY)
        self.assertIs(INGESTION_ACTION_REGISTRY, registry.INGESTION_ACTION_REGISTRY)
        self.assertEqual(
            registry.INGESTION_ACTION_REGISTRY["daily_market_update"]["section"],
            registry.INGESTION_COLLECTION_OPERATIONAL,
        )
        self.assertIn("weekly_fundamental_refresh", registry.compatibility_ingestion_actions())
        self.assertNotIn("weekly_fundamental_refresh", registry.active_ingestion_actions())

    def test_ingestion_styles_and_result_summaries_live_in_dedicated_modules(self) -> None:
        from app.web.ingestion import page
        from app.web.ingestion import results
        from app.web.ingestion import styles

        self.assertIs(page._install_ingestion_responsive_styles, styles.install_ingestion_responsive_styles)
        self.assertIs(page._build_common_last_result_summary, results.build_common_last_result_summary)
        self.assertIs(page._build_statement_refresh_action_summary, results.build_statement_refresh_action_summary)

        summary = results.build_common_last_result_summary(
            {
                "job_name": "daily_market_update",
                "status": "partial_success",
                "rows_written": 12,
                "symbols_requested": 3,
                "failed_symbols": ["BAD"],
                "duration_sec": 1.25,
                "message": "partial",
            }
        )
        self.assertEqual(summary["title"], "일별 가격 업데이트")
        self.assertIn("coverage gap", summary["attention"])


if __name__ == "__main__":
    unittest.main()
