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


if __name__ == "__main__":
    unittest.main()
