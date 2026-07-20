from __future__ import annotations

import sys
import unittest
from pathlib import Path


REQUIRED_JOURNEY_IDS = {
    "journey.market_understanding",
    "journey.institutional_portfolios",
    "journey.data_preparation",
    "journey.candidate_creation",
    "journey.validation_decision",
    "journey.monitoring",
}

REQUIRED_REFERENCE_ITEM_IDS = {
    "feature.market_context",
    "feature.market_movers",
    "feature.futures_macro",
    "feature.sentiment",
    "feature.events",
    "feature.economic_cycle",
    "status.not_run",
    "status.review",
    "status.blocked",
    "concept.data_trust",
    "concept.provider_coverage",
    "concept.selected_route_gate",
    "concept.saved_portfolio",
    "concept.monitoring_scenario",
    "playbook.ingestion_data_missing",
    "playbook.practical_validation_not_run",
    "playbook.final_review_candidate_missing",
    "playbook.monitoring_scenario_stale",
}

REQUIRED_SURFACES = {
    "Overview",
    "Institutional Portfolios",
    "Ingestion",
    "Backtest Analysis",
    "Practical Validation",
    "Final Review",
    "Portfolio Monitoring",
}

FORBIDDEN_USER_LABELS = {
    "futures monitor",
    "macro thermometer",
    "candidate review",
    "portfolio proposal",
    "selected portfolio dashboard",
    "main worktree",
    "sub worktree",
    "fixture",
}


class ReferenceCenterCatalogContractTests(unittest.TestCase):
    def test_catalog_service_is_streamlit_free_and_builds_v1_payload(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.reference_center import build_reference_center_payload

        payload = build_reference_center_payload()

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(payload["schema_version"], "reference_center_v1")
        self.assertEqual(payload["component"], "ReferenceCenterWorkbench")
        self.assertEqual(set(payload["journeys"]), REQUIRED_JOURNEY_IDS)
        self.assertIsNone(payload["initial_item_id"])
        self.assertFalse(payload["invalid_initial_item"])

    def test_catalog_has_current_journeys_concepts_and_playbooks(self) -> None:
        from app.services.reference_center import get_reference_center_items

        items = get_reference_center_items()
        item_ids = {str(item["id"]) for item in items}
        journey_ids = {str(item["id"]) for item in items if item["kind"] == "journey"}

        self.assertEqual(journey_ids, REQUIRED_JOURNEY_IDS)
        self.assertGreaterEqual(item_ids, REQUIRED_REFERENCE_ITEM_IDS)
        self.assertEqual(
            {surface for item in items for surface in item["related_surfaces"]},
            REQUIRED_SURFACES,
        )

    def test_every_item_has_valid_schema_unique_id_and_search_projection(self) -> None:
        from app.services.reference_center import REFERENCE_DESTINATIONS, get_reference_center_items

        items = get_reference_center_items()
        ids = [str(item["id"]) for item in items]
        self.assertEqual(len(ids), len(set(ids)))

        for item in items:
            with self.subTest(item_id=item.get("id")):
                self.assertIn(item["kind"], {"journey", "concept", "playbook"})
                for field in ("id", "category", "title", "summary", "meaning", "impact", "next_action"):
                    self.assertTrue(str(item.get(field) or "").strip(), field)
                for field in ("aliases", "keywords", "related_surfaces", "related_item_ids"):
                    self.assertIsInstance(item.get(field), list, field)
                self.assertTrue(str(item.get("search_text") or "").strip())
                self.assertEqual(str(item["search_text"]), str(item["search_text"]).lower())
                if item["destination"] is not None:
                    self.assertIn(item["destination"], REFERENCE_DESTINATIONS)

    def test_related_item_ids_resolve_and_user_copy_excludes_legacy_labels(self) -> None:
        from app.services.reference_center import get_reference_center_items

        items = get_reference_center_items()
        item_ids = {str(item["id"]) for item in items}

        for item in items:
            with self.subTest(item_id=item["id"]):
                self.assertEqual(set(item["related_item_ids"]) - item_ids, set())
                user_copy = " ".join(
                    str(value)
                    for key, value in item.items()
                    if key != "id"
                ).lower()
                self.assertEqual(
                    {label for label in FORBIDDEN_USER_LABELS if label in user_copy},
                    set(),
                )

    def test_reference_item_lookup_is_defensive_and_validates_initial_item(self) -> None:
        from app.services.reference_center import get_reference_item, validate_initial_reference_item

        item = get_reference_item("status.not_run")
        self.assertIsNotNone(item)
        assert item is not None
        item["title"] = "mutated"

        fresh_item = get_reference_item("status.not_run")
        assert fresh_item is not None
        self.assertEqual(fresh_item["title"], "NOT_RUN")
        self.assertEqual(validate_initial_reference_item(" status.not_run "), "status.not_run")
        self.assertIsNone(validate_initial_reference_item("unknown"))

        valid_payload = __import__(
            "app.services.reference_center",
            fromlist=["build_reference_center_payload"],
        ).build_reference_center_payload("status.not_run")
        invalid_payload = __import__(
            "app.services.reference_center",
            fromlist=["build_reference_center_payload"],
        ).build_reference_center_payload("unknown")
        self.assertEqual(valid_payload["initial_item_id"], "status.not_run")
        self.assertFalse(valid_payload["invalid_initial_item"])
        self.assertIsNone(invalid_payload["initial_item_id"])
        self.assertTrue(invalid_payload["invalid_initial_item"])

    def test_destination_validation_accepts_only_current_user_surfaces(self) -> None:
        from app.services.reference_center import REFERENCE_DESTINATIONS, validate_reference_destination

        for destination in REFERENCE_DESTINATIONS:
            self.assertEqual(validate_reference_destination(f" {destination} "), destination)
        for destination in (None, "", "raw_registry", "run_history", "/guides"):
            self.assertIsNone(validate_reference_destination(destination))

    def test_drift_report_passes_all_current_surface_and_integrity_checks(self) -> None:
        from app.services.reference_center import build_reference_center_drift_report

        report = build_reference_center_drift_report()

        self.assertEqual(report["status"], "PASS")
        for issue_key in (
            "missing_current_surfaces",
            "forbidden_user_labels",
            "duplicate_ids",
            "invalid_related_item_ids",
            "invalid_destinations",
            "invalid_items",
        ):
            self.assertEqual(report[issue_key], [], issue_key)
        self.assertEqual(report["metrics"]["journey_count"], 6)

    def test_streamlit_shell_migration_contract_is_deferred_until_task_6(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
        self.assertIn('title="Guides"', source)
        self.assertIn('title="Glossary"', source)


if __name__ == "__main__":
    unittest.main()
