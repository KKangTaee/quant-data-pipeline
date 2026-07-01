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

    def test_ingestion_dispatcher_lives_in_dedicated_module(self) -> None:
        from unittest.mock import patch

        from app.web.ingestion import dispatcher
        from app.web.ingestion import page

        self.assertIs(page._dispatch_job, dispatcher.dispatch_job)
        self.assertEqual(dispatcher.diagnostic_state_key("diagnose_price_stale"), "price_stale_diagnosis_result")

        with patch(
            "app.web.ingestion.dispatcher.run_price_stale_diagnosis",
            return_value={"status": "ok", "message": "diagnosis ok", "details": {"rows": []}},
        ) as diagnose:
            result = dispatcher.dispatch_job(
                {
                    "action": "diagnose_price_stale",
                    "job_name": "diagnose_price_stale",
                    "params": {"symbols": ["AAPL"], "end": "2026-07-01", "timeframe": "1d"},
                }
            )

        diagnose.assert_called_once_with(["AAPL"], end="2026-07-01", timeframe="1d")
        self.assertEqual(result["job_name"], "diagnose_price_stale")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 0)

    def test_ingestion_collection_sections_live_in_dedicated_module(self) -> None:
        from app.web.ingestion import page
        from app.web.ingestion import sections

        self.assertIs(page._render_ingestion_operational_section, sections.render_operational_section)
        self.assertIs(page._render_ingestion_manual_section, sections.render_manual_section)
        self.assertIs(page._render_selected_ingestion_collection_section, sections.render_selected_section)


if __name__ == "__main__":
    unittest.main()
