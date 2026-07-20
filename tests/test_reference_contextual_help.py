from __future__ import annotations

import sys
import unittest
from pathlib import Path


REQUIRED_CONTEXTUAL_SURFACES = {
    "overview",
    "institutional_portfolios",
    "ingestion",
    "backtest_analysis",
    "practical_validation",
    "final_review",
    "portfolio_monitoring",
}

OWNER_CALL_SITES = {
    "overview": Path("app/web/overview/page.py"),
    "institutional_portfolios": Path("app/web/institutional_portfolios.py"),
    "ingestion": Path("app/web/ingestion/page.py"),
    "backtest_analysis": Path("app/web/backtest_analysis.py"),
    "practical_validation": Path("app/web/backtest_practical_validation/page.py"),
    "final_review": Path("app/web/backtest_final_review/page.py"),
    "portfolio_monitoring": Path("app/web/final_selected_portfolio_dashboard.py"),
}


class ReferenceContextualHelpContractTests(unittest.TestCase):
    def test_contextual_help_catalog_is_streamlit_free_and_covers_current_surfaces(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.reference_contextual_help import get_reference_contextual_help_catalog

        catalog = get_reference_contextual_help_catalog()

        self.assertNotIn("streamlit", sys.modules)
        surface_keys = {row["surface_key"] for row in catalog}
        self.assertGreaterEqual(surface_keys, REQUIRED_CONTEXTUAL_SURFACES)
        self.assertNotIn("operations_console", surface_keys)

        final_review = next(row for row in catalog if row["surface_key"] == "final_review")
        self.assertIn("concept.selected_route_gate", final_review["reference_item_ids"])
        self.assertIn("Practical Validation", " ".join(final_review["next_checks"]))
        self.assertIn("broker order", " ".join(final_review["boundaries"]))

    def test_contextual_links_use_single_reference_target_and_existing_item_ids(self) -> None:
        from app.services.reference_center import get_reference_center_items
        from app.services.reference_contextual_help import get_reference_contextual_help_catalog

        item_ids = {item["id"] for item in get_reference_center_items()}
        for help_item in get_reference_contextual_help_catalog():
            with self.subTest(surface_key=help_item["surface_key"]):
                self.assertGreaterEqual(len(help_item["links"]), 1)
                self.assertEqual(
                    {link["target"] for link in help_item["links"]},
                    {"/reference"},
                )
                self.assertEqual(
                    {link["item_id"] for link in help_item["links"]} - item_ids,
                    set(),
                )
                self.assertEqual(set(help_item["reference_item_ids"]) - item_ids, set())

    def test_contextual_help_lookup_returns_defensive_copy(self) -> None:
        from app.services.reference_contextual_help import get_reference_contextual_help

        help_item = get_reference_contextual_help("portfolio_monitoring")
        self.assertIsNotNone(help_item)
        assert help_item is not None
        self.assertEqual(help_item["surface"], "Portfolio Monitoring")
        self.assertIn("concept.monitoring_scenario", help_item["reference_item_ids"])

        help_item["reference_item_ids"].append("mutated")
        fresh_item = get_reference_contextual_help("portfolio_monitoring")
        assert fresh_item is not None
        self.assertNotIn("mutated", fresh_item["reference_item_ids"])

    def test_unknown_contextual_help_key_returns_none(self) -> None:
        from app.services.reference_contextual_help import get_reference_contextual_help

        self.assertIsNone(get_reference_contextual_help("unknown_surface"))

    def test_contextual_help_drift_report_matches_reference_items_and_links(self) -> None:
        from app.services.reference_contextual_help import build_reference_contextual_help_drift_report

        report = build_reference_contextual_help_drift_report()

        self.assertEqual(report["status"], "PASS")
        self.assertEqual(report["missing_reference_item_ids"], [])
        self.assertEqual(report["invalid_links"], [])
        self.assertEqual(report["duplicate_surface_keys"], [])
        self.assertGreaterEqual(report["metrics"]["surface_count"], 7)
        self.assertGreaterEqual(report["metrics"]["reference_item_count"], 7)

    def test_contextual_help_renderer_uses_one_page_target_and_item_query_param(self) -> None:
        source = Path("app/web/reference_contextual_help.py").read_text(encoding="utf-8")

        self.assertIn('"/reference": "reference"', source)
        self.assertIn("st.page_link", source)
        self.assertIn('query_params={"item": item_id}', source)
        self.assertNotIn('"/guides"', source)
        self.assertNotIn('"/glossary"', source)

    def test_all_current_owner_surfaces_render_contextual_help(self) -> None:
        for surface_key, path in OWNER_CALL_SITES.items():
            with self.subTest(surface_key=surface_key):
                source = path.read_text(encoding="utf-8")
                self.assertIn(f'render_reference_contextual_help("{surface_key}"', source)

    def test_streamlit_shell_keeps_contextual_config_behind_module_boundary(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")

        self.assertNotIn(
            "from app.web.reference_contextual_help import configure_reference_contextual_help_page_targets",
            source,
        )
        self.assertIn("from app.web import reference_contextual_help as reference_contextual_help_module", source)
        self.assertIn(
            'getattr(reference_contextual_help_module, "configure_reference_contextual_help_page_targets"',
            source,
        )
        self.assertIn('"reference": reference_page', source)


if __name__ == "__main__":
    unittest.main()
