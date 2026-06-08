from __future__ import annotations

import sys
import tempfile
import unittest
from pathlib import Path


class ReferenceGlossaryCatalogContractTests(unittest.TestCase):
    def test_glossary_catalog_is_streamlit_free_and_contains_operational_concepts(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.reference_glossary_catalog import get_reference_concept_dictionary

        concepts = get_reference_concept_dictionary()

        self.assertNotIn("streamlit", sys.modules)
        concept_by_term = {row["term"]: row for row in concepts}
        for term in ["NOT_RUN", "REVIEW", "BLOCKED", "Data Trust", "Provider Coverage"]:
            self.assertIn(term, concept_by_term)

        not_run = concept_by_term["NOT_RUN"]
        self.assertEqual(not_run["category"], "Status / Gate")
        self.assertIn("pass", not_run["progress_implication"])
        self.assertIn("Practical Validation", not_run["owner_screen"])
        self.assertIn("keywords", not_run)

    def test_concept_search_matches_terms_keywords_and_body(self) -> None:
        from app.services.reference_glossary_catalog import (
            get_reference_concept_dictionary,
            search_reference_concepts,
        )

        concepts = get_reference_concept_dictionary()

        provider_results = search_reference_concepts(concepts, "look-through")
        provider_terms = [row["term"] for row in provider_results]
        self.assertIn("Provider Coverage", provider_terms)

        monitoring_results = search_reference_concepts(concepts, "scenario stale")
        self.assertEqual(monitoring_results[0]["term"], "Portfolio Monitoring Scenario")

        no_query = search_reference_concepts(concepts, "")
        self.assertEqual(len(no_query), len(concepts))

    def test_markdown_glossary_sections_parse_and_search_without_streamlit(self) -> None:
        from app.services.reference_glossary_catalog import (
            load_glossary_sections_from_markdown,
            search_glossary_sections,
        )

        with tempfile.TemporaryDirectory() as tmp_dir:
            glossary_path = Path(tmp_dir) / "GLOSSARY.md"
            glossary_path.write_text(
                """# Glossary

## 목적

meta body

## Promotion Policy Signal

candidate handoff policy body

## Portfolio Monitoring

read-only selected decision scenario body
""",
                encoding="utf-8",
            )

            meta_sections, term_sections = load_glossary_sections_from_markdown(glossary_path)

        self.assertEqual([row["title"] for row in meta_sections], ["목적"])
        self.assertEqual(
            [row["title"] for row in term_sections],
            ["Promotion Policy Signal", "Portfolio Monitoring"],
        )

        title_only = search_glossary_sections(term_sections, "scenario", search_body=False)
        self.assertEqual(title_only, [])

        body_search = search_glossary_sections(term_sections, "scenario", search_body=True)
        self.assertEqual(body_search[0]["title"], "Portfolio Monitoring")


if __name__ == "__main__":
    unittest.main()
