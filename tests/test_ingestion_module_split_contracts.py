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


if __name__ == "__main__":
    unittest.main()
