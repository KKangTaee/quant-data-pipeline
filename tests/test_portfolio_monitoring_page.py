from __future__ import annotations

import unittest
from datetime import date
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from app.services.portfolio_monitoring.commands import CommandResult
from app.services.portfolio_monitoring.schemas import CommandStatus


class PortfolioMonitoringPageTests(unittest.TestCase):
    def _services(self, *, component_value=None):
        calls = []
        state = {}

        def build_workspace(
            *,
            active_group_id,
            catalog_query,
            selected_item_id=None,
            include_selected_item_market_chart=False,
        ):
            calls.append((
                "build",
                active_group_id,
                catalog_query,
                selected_item_id,
                include_selected_item_market_chart,
            ))
            return {
                "schema_version": "portfolio_monitoring_workspace_v2",
                "generated_at": "2026-07-19T12:00:00",
                "groups": [],
                "active_group": None,
                "selected_position": {
                    "monitoring_item_id": None,
                    "eligible": False,
                    "reason": None,
                    "effective_initial_shares": None,
                    "current_shares": None,
                    "gross_contributions": 0,
                    "gross_withdrawals": 0,
                    "pnl": None,
                    "total_return": None,
                    "event_rows": [],
                },
                "catalog": {"query": catalog_query, "items": []},
                "commands": [],
                "diagnosis": {"policy_version": "portfolio_monitoring_policy_v1", "top_three": [], "strengths": [], "weaknesses": [], "data_gaps": [], "all_rows": []},
                "macro_observation": {"state": "low", "rows": [], "top_rows": []},
                "now_to_review": [],
                "source_health": {"status": "LIMITED", "coverage": 0.0},
                "method": {},
                "boundaries": {},
            }

        def render(payload):
            calls.append(("render", payload["schema_version"]))
            return component_value

        def create_group(event):
            calls.append(("create_group", event["name"]))
            return CommandResult(
                status=CommandStatus.SUCCEEDED,
                command_id=event["command_id"],
                target_id="group-new",
                replayed=False,
                message="created",
            )

        return SimpleNamespace(
            calls=calls,
            session_state=state,
            build_workspace=build_workspace,
            render_workbench=render,
            render_fallback=lambda workspace, error=None: calls.append(("fallback", error)),
            rerun=lambda: calls.append(("rerun",)),
            create_group=create_group,
            rename_group=lambda event: calls.append(("rename_group", event)) or None,
            add_item=lambda event: calls.append(("add_item", event)) or None,
            end_item=lambda event: calls.append(("end_item", event)) or None,
            reopen_item=lambda event: calls.append(("reopen_item", event)) or None,
            correct_initial_quantity=lambda event: calls.append(
                ("correct_initial_quantity", event)
            ) or None,
            record_position_trade=lambda event: calls.append(
                ("record_position_trade", event)
            ) or None,
            replace_position_trade=lambda event: calls.append(
                ("replace_position_trade", event)
            ) or None,
            void_position_trade=lambda event: calls.append(
                ("void_position_trade", event)
            ) or None,
        )

    def test_route_builds_once_mounts_once_dispatches_once_and_reruns_after_success(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services(
            component_value={
                "event": {
                    "id": "create_group",
                    "command_id": "command-1",
                    "name": "Core",
                }
            }
        )

        page.render_final_selected_portfolio_dashboard_page(services=services)

        self.assertEqual(sum(call[0] == "build" for call in services.calls), 1)
        self.assertEqual(sum(call[0] == "render" for call in services.calls), 1)
        self.assertEqual(sum(call[0] == "create_group" for call in services.calls), 1)
        self.assertEqual(sum(call[0] == "rerun" for call in services.calls), 1)
        self.assertEqual(services.session_state["portfolio_monitoring_last_command"]["command_id"], "command-1")

    def test_route_requests_market_chart_for_the_session_selected_item(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services(component_value={"event": None})
        services.session_state["portfolio_monitoring_selected_item_id"] = "item-a"

        page.render_final_selected_portfolio_dashboard_page(services=services)

        build_call = next(call for call in services.calls if call[0] == "build")
        self.assertEqual(build_call[3], "item-a")
        self.assertTrue(build_call[4])

    def test_operations_workspace_explicitly_skips_selected_item_market_chart(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        with patch.object(page, "_default_portfolio_monitoring_services", return_value=services):
            page.load_portfolio_monitoring_workspace_for_operations()

        build_call = next(call for call in services.calls if call[0] == "build")
        self.assertIsNone(build_call[3])
        self.assertFalse(build_call[4])

    def test_missing_component_uses_read_only_fallback_not_legacy_dashboard(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services(component_value=None)
        with patch.object(page, "_render_dashboard_portfolio_workspace", side_effect=AssertionError("legacy renderer called")):
            page.render_final_selected_portfolio_dashboard_page(services=services)

        self.assertEqual(sum(call[0] == "fallback" for call in services.calls), 1)
        self.assertEqual(sum(call[0] == "rerun" for call in services.calls), 0)

    def test_dispatch_updates_view_state_without_mutating_command(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        result = page._dispatch_portfolio_monitoring_event(
            {"id": "search_catalog", "query": "aapl", "source_type": "direct_security"},
            services,
        )

        self.assertIsNone(result)
        self.assertEqual(services.session_state["portfolio_monitoring_catalog_query"], "aapl")
        self.assertEqual(services.session_state["portfolio_monitoring_catalog_source_type"], "direct_security")
        self.assertFalse(any(call[0] in {"create_group", "rename_group", "add_item", "end_item", "reopen_item"} for call in services.calls))

    def test_dispatches_reopen_item_command(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        event = {
            "id": "reopen_item",
            "command_id": "command-reopen",
            "monitoring_item_id": "item-ended",
        }

        page._dispatch_portfolio_monitoring_event(event, services)

        self.assertIn(("reopen_item", event), services.calls)

    def test_catalog_search_whitelists_item_builder_recovery_state(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        page._dispatch_portfolio_monitoring_event(
            {
                "id": "search_catalog",
                "query": "aapl",
                "source_type": "direct_security",
                "item_builder_state": {
                    "drawer_open": True,
                    "drawer_step": 2,
                    "catalog_query": "aapl",
                    "draft": {
                        "command_id": "command-search",
                        "source_type": "direct_security",
                        "selected_source_ref": "AAPL",
                        "selected_label": "Apple Inc.",
                        "selected_kind": "stock",
                        "requested_start_date": "2026-07-01",
                        "funding_mode": "fixed_shares",
                        "notional": "10000",
                        "shares": "5",
                        "unexpected": "drop-me",
                    },
                    "unexpected": "drop-me",
                },
            },
            services,
        )

        self.assertEqual(
            services.session_state["portfolio_monitoring_item_builder_state"],
            {
                "drawer_open": True,
                "drawer_step": 2,
                "catalog_query": "aapl",
                "draft": {
                    "command_id": "command-search",
                    "source_type": "direct_security",
                    "selected_source_ref": "AAPL",
                    "selected_label": "Apple Inc.",
                    "selected_kind": "stock",
                    "requested_start_date": "2026-07-01",
                    "funding_mode": "fixed_shares",
                    "notional": "10000",
                    "shares": "5",
                },
            },
        )

    def test_new_catalog_search_clears_a_stale_requested_start_date(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        services.session_state["portfolio_monitoring_catalog_requested_start_date"] = "2026-06-01"

        page._dispatch_portfolio_monitoring_event(
            {"id": "search_catalog", "query": "aapl", "source_type": "direct_security"},
            services,
        )

        self.assertNotIn(
            "portfolio_monitoring_catalog_requested_start_date",
            services.session_state,
        )

    def test_trade_date_lookup_preserves_editor_and_requests_exact_close(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        event = {
            "id": "lookup_position_trade_close",
            "monitoring_item_id": "item-amd",
            "trade_date": "2026-07-17",
            "position_editor_state": {
                "open": True,
                "mode": "record",
                "position_effect": "buy",
                "quantity": "5",
                "execution_price": "",
                "price_mode": "awaiting_close",
                "fee_usd": "0",
                "note": "",
                "unexpected": "drop",
            },
        }

        page._dispatch_portfolio_monitoring_event(event, services)

        self.assertEqual(
            services.session_state["portfolio_monitoring_trade_date"],
            "2026-07-17",
        )
        self.assertEqual(
            services.session_state[
                "portfolio_monitoring_position_editor_state"
            ]["quantity"],
            "5",
        )
        self.assertNotIn(
            "unexpected",
            services.session_state["portfolio_monitoring_position_editor_state"],
        )
        self.assertEqual(
            services.session_state[
                "portfolio_monitoring_position_editor_state"
            ]["price_mode"],
            "awaiting_close",
        )

    def test_exact_close_projection_never_shifts_to_next_market_day(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        frame = pd.DataFrame([{"date": "2026-07-18", "close": 160}])
        item = SimpleNamespace(source_ref="AMD")
        with patch.object(page, "load_price_history", return_value=frame):
            with self.assertRaisesRegex(ValueError, "해당 거래일"):
                page._load_exact_position_trade_close(
                    item, date(2026, 7, 17)
                )

    def test_dispatches_all_position_commands_once(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        for event_id, call_name in (
            ("correct_initial_quantity", "correct_initial_quantity"),
            ("record_position_trade", "record_position_trade"),
            ("replace_position_trade", "replace_position_trade"),
            ("void_position_trade", "void_position_trade"),
        ):
            event = {
                "id": event_id,
                "command_id": f"command-{event_id}",
                "monitoring_item_id": "item-amd",
            }
            page._dispatch_portfolio_monitoring_event(event, services)
            self.assertIn((call_name, event), services.calls)

        self.assertEqual(
            services.session_state["portfolio_monitoring_selected_item_id"],
            "item-amd",
        )

if __name__ == "__main__":
    unittest.main()
