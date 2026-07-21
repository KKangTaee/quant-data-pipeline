from __future__ import annotations

import sys
import unittest
from pathlib import Path
from unittest.mock import MagicMock, patch


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
        loaded_streamlit = sys.modules.pop("streamlit", None)
        try:
            from app.services.reference_center import build_reference_center_payload

            payload = build_reference_center_payload()

            self.assertNotIn("streamlit", sys.modules)
            self.assertEqual(payload["schema_version"], "reference_center_v1")
            self.assertEqual(payload["component"], "ReferenceCenterWorkbench")
            self.assertEqual(set(payload["journeys"]), REQUIRED_JOURNEY_IDS)
            self.assertIsNone(payload["initial_item_id"])
            self.assertFalse(payload["invalid_initial_item"])
        finally:
            if loaded_streamlit is not None:
                sys.modules["streamlit"] = loaded_streamlit

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

    def test_streamlit_shell_has_one_reference_page_and_no_split_navigation(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")
        reference_page_source = Path("app/web/reference_center.py").read_text(encoding="utf-8")

        self.assertIn('title="Reference"', source)
        self.assertIn('url_path="reference"', source)
        self.assertNotIn('title="Guides"', source)
        self.assertNotIn('url_path="guides"', source)
        self.assertNotIn('title="Glossary"', source)
        self.assertNotIn('url_path="glossary"', source)
        self.assertNotIn("render_reference_guides_page", source)
        self.assertNotIn("load_glossary_sections_from_markdown", source)
        self.assertNotIn("_render_runtime_build_indicator", reference_page_source)
        for page_target_key in (
            '"overview": overview_page',
            '"institutional_portfolios": institutional_portfolios_page',
            '"ingestion": ingestion_page',
            '"backtest": backtest_page',
            '"portfolio_monitoring": selected_portfolio_dashboard_page',
        ):
            self.assertIn(page_target_key, source)

    def test_active_python_tree_has_no_legacy_reference_symbols(self) -> None:
        legacy_symbols = {
            "reference_guides",
            "reference_guides_catalog",
            "reference_glossary_catalog",
            "render_reference_guides_page",
            "load_glossary_sections_from_markdown",
            "search_glossary_sections",
        }
        matches: list[str] = []
        for path in Path("app").rglob("*.py"):
            if "__pycache__" in path.parts:
                continue
            source = path.read_text(encoding="utf-8")
            for symbol in legacy_symbols:
                if symbol in source:
                    matches.append(f"{path}:{symbol}")

        self.assertEqual(matches, [])


class ReferenceCenterNavigationContractTests(unittest.TestCase):
    def test_navigation_event_accepts_only_known_item_and_destination(self) -> None:
        from app.web.reference_center import normalize_reference_event

        self.assertIsNone(normalize_reference_event(None))
        self.assertIsNone(
            normalize_reference_event(
                {"event": {"id": "search", "destination": "overview", "item_id": "feature.market_context"}}
            )
        )
        self.assertIsNone(
            normalize_reference_event(
                {
                    "event": {
                        "id": "navigate_to_surface",
                        "destination": "raw_registry",
                        "item_id": "feature.market_context",
                    }
                }
            )
        )
        self.assertIsNone(
            normalize_reference_event(
                {
                    "event": {
                        "id": "navigate_to_surface",
                        "destination": "overview",
                        "item_id": "unknown",
                    }
                }
            )
        )

        self.assertEqual(
            normalize_reference_event(
                {
                    "event": {
                        "id": "navigate_to_surface",
                        "destination": "final_review",
                        "item_id": "journey.validation_decision",
                        "nonce": "n-1",
                    }
                }
            ),
            {
                "id": "navigate_to_surface",
                "destination": "final_review",
                "item_id": "journey.validation_decision",
                "nonce": "n-1",
            },
        )

    def test_navigation_resolution_maps_backtest_panels_and_top_level_pages(self) -> None:
        from app.web.reference_center import resolve_reference_navigation

        self.assertEqual(
            resolve_reference_navigation("backtest_analysis"),
            {"page_target_key": "backtest", "panel": "Backtest Analysis"},
        )
        self.assertEqual(
            resolve_reference_navigation("practical_validation"),
            {"page_target_key": "backtest", "panel": "Practical Validation"},
        )
        self.assertEqual(
            resolve_reference_navigation("final_review"),
            {"page_target_key": "backtest", "panel": "Final Review"},
        )
        self.assertEqual(
            resolve_reference_navigation("portfolio_monitoring"),
            {"page_target_key": "portfolio_monitoring", "panel": ""},
        )
        self.assertEqual(
            resolve_reference_navigation("institutional_portfolios"),
            {"page_target_key": "institutional_portfolios", "panel": ""},
        )
        self.assertIsNone(resolve_reference_navigation("raw_registry"))

    def test_page_target_configuration_keeps_only_allowed_keys(self) -> None:
        from app.web import reference_center

        reference_center.configure_reference_center_page_targets(
            {
                "overview": "overview-page",
                "backtest": "backtest-page",
                "raw_registry": "unsafe-page",
                "portfolio_monitoring": None,
            }
        )

        self.assertEqual(
            reference_center._REFERENCE_PAGE_TARGETS,
            {"overview": "overview-page", "backtest": "backtest-page"},
        )

    def test_missing_react_build_renders_compact_error_without_legacy_fallback(self) -> None:
        from app.web import reference_center

        fake_st = MagicMock()
        fake_st.query_params.get.return_value = None
        with (
            patch.object(reference_center, "st", fake_st),
            patch.object(reference_center, "reference_center_react_component_available", return_value=False),
            patch.object(reference_center, "render_reference_center_workbench") as render_workbench,
        ):
            reference_center.render_reference_center_page()

        fake_st.error.assert_called_once_with(
            "Reference 화면을 불러오지 못했습니다. 배포된 React build를 확인해 주세요."
        )
        fake_st.caption.assert_called_once()
        render_workbench.assert_not_called()

    def test_page_shell_builds_deep_link_payload_and_routes_backtest_intent(self) -> None:
        from app.web import reference_center

        fake_st = MagicMock()
        fake_st.query_params.get.return_value = "status.not_run"
        reference_center.configure_reference_center_page_targets({"backtest": "backtest-page"})
        event_value = {
            "event": {
                "id": "navigate_to_surface",
                "destination": "practical_validation",
                "item_id": "status.not_run",
                "nonce": "n-2",
            }
        }

        with (
            patch.object(reference_center, "st", fake_st),
            patch.object(reference_center, "reference_center_react_component_available", return_value=True),
            patch.object(reference_center, "render_reference_center_workbench", return_value=event_value) as render_workbench,
            patch.object(reference_center, "request_backtest_panel") as request_panel,
        ):
            reference_center.render_reference_center_page()

        payload = render_workbench.call_args.args[0]
        self.assertEqual(payload["initial_item_id"], "status.not_run")
        request_panel.assert_called_once_with("Practical Validation")
        fake_st.switch_page.assert_called_once_with("backtest-page")

    def test_invalid_deep_link_and_destination_stay_on_reference(self) -> None:
        from app.web import reference_center

        fake_st = MagicMock()
        fake_st.query_params.get.return_value = "removed-item"
        reference_center.configure_reference_center_page_targets({"overview": "overview-page"})
        invalid_event = {
            "event": {
                "id": "navigate_to_surface",
                "destination": "raw_registry",
                "item_id": "feature.market_context",
                "nonce": "n-3",
            }
        }

        with (
            patch.object(reference_center, "st", fake_st),
            patch.object(reference_center, "reference_center_react_component_available", return_value=True),
            patch.object(reference_center, "render_reference_center_workbench", return_value=invalid_event),
        ):
            reference_center.render_reference_center_page()

        warning_copy = " ".join(str(call.args[0]) for call in fake_st.warning.call_args_list)
        self.assertIn("변경되었거나 삭제", warning_copy)
        self.assertIn("이동 요청", warning_copy)
        fake_st.switch_page.assert_not_called()


if __name__ == "__main__":
    unittest.main()
