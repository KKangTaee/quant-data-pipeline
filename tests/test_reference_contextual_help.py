from __future__ import annotations

import sys
import unittest


class ReferenceContextualHelpContractTests(unittest.TestCase):
    def test_contextual_help_catalog_is_streamlit_free_and_covers_primary_surfaces(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.reference_contextual_help import get_reference_contextual_help_catalog

        catalog = get_reference_contextual_help_catalog()

        self.assertNotIn("streamlit", sys.modules)
        surface_keys = {row["surface_key"] for row in catalog}
        self.assertGreaterEqual(
            surface_keys,
            {
                "backtest_analysis",
                "practical_validation",
                "final_review",
                "operations_console",
                "portfolio_monitoring",
            },
        )

        final_review = next(row for row in catalog if row["surface_key"] == "final_review")
        self.assertIn("Selected-route Gate", final_review["glossary_terms"])
        self.assertIn("Practical Validation", " ".join(final_review["next_checks"]))
        self.assertIn("broker order", " ".join(final_review["boundaries"]))

    def test_contextual_help_lookup_returns_copy_and_reference_only_links(self) -> None:
        from app.services.reference_contextual_help import get_reference_contextual_help

        help_item = get_reference_contextual_help("portfolio_monitoring")
        self.assertIsNotNone(help_item)
        assert help_item is not None
        self.assertEqual(help_item["surface"], "Operations > Portfolio Monitoring")

        links = help_item["links"]
        self.assertGreaterEqual(len(links), 2)
        self.assertEqual({link["target"] for link in links}, {"/guides", "/glossary"})
        self.assertIn("Portfolio Monitoring Scenario", help_item["glossary_terms"])

        help_item["glossary_terms"].append("mutated")
        fresh_item = get_reference_contextual_help("portfolio_monitoring")
        assert fresh_item is not None
        self.assertNotIn("mutated", fresh_item["glossary_terms"])

    def test_unknown_contextual_help_key_returns_none(self) -> None:
        from app.services.reference_contextual_help import get_reference_contextual_help

        self.assertIsNone(get_reference_contextual_help("unknown_surface"))


if __name__ == "__main__":
    unittest.main()
