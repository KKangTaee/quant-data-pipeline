from __future__ import annotations

import unittest
from datetime import date
from decimal import Decimal
from types import SimpleNamespace
from unittest.mock import patch

import pandas as pd

from app.services.portfolio_monitoring.commands import CommandResult
from app.services.portfolio_monitoring.persistence import (
    MonitoringItemRecord,
    PositionEventRecord,
)
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
            review_latest_decision=lambda event: calls.append(
                ("review_latest_decision", event)
            )
            or None,
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
            refresh_group_prices=lambda event: calls.append(
                ("refresh_group_prices", event)
            )
            or {
                "command_id": event.get("command_id"),
                "status": "success",
                "message": "prices refreshed",
                "target_id": event.get("portfolio_group_id"),
            },
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
        self.assertEqual(
            services.session_state["portfolio_monitoring_selected_item_id"],
            "item-ended",
        )

    def test_dispatches_latest_decision_review_navigation(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        event = {
            "id": "review_latest_decision",
            "monitoring_item_id": "item-strategy",
        }

        result = page._dispatch_portfolio_monitoring_event(event, services)

        self.assertIsNone(result)
        self.assertIn(("review_latest_decision", event), services.calls)

    def test_default_latest_decision_review_routes_to_final_review_server_side(
        self,
    ) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        state = {}
        switch_calls = []
        item = SimpleNamespace(
            monitoring_item_id="item-strategy",
            source_type="selected_strategy",
            source_ref="old-selected",
            instrument_kind="strategy",
        )
        repository = SimpleNamespace(
            get_item=lambda item_id: item if item_id == "item-strategy" else None
        )
        contract = SimpleNamespace(
            decision_row={
                "decision_id": "latest-hold",
                "source_id": "validation-latest-hold",
                "selection_source_id": "selection-a",
            },
            readiness=SimpleNamespace(
                decision_lifecycle={
                    "state": "TRACKING_ELIGIBILITY_CHANGED",
                    "locked": True,
                    "latest_source_id": "validation-latest-hold",
                }
            ),
        )
        adapter = SimpleNamespace(load_candidate_contract=lambda decision_id: contract)
        fake_st = SimpleNamespace(
            session_state=state,
            rerun=lambda: None,
            switch_page=lambda target: switch_calls.append(target),
        )
        target = object()
        page.configure_portfolio_monitoring_page_targets({"backtest": target})
        try:
            with (
                patch.object(page, "st", fake_st),
                patch.object(
                    page,
                    "MySQLMonitoringRepository",
                    return_value=repository,
                ),
                patch.object(
                    page,
                    "MySQLMonitoringHistoryRepository",
                    return_value=SimpleNamespace(),
                ),
                patch.object(
                    page,
                    "SelectedStrategyReplayAdapter",
                    return_value=adapter,
                ),
            ):
                services = page._default_portfolio_monitoring_services()
                result = services.review_latest_decision(
                    {
                        "id": "review_latest_decision",
                        "monitoring_item_id": "item-strategy",
                        "latest_source_id": "untrusted-client-value",
                    }
                )
        finally:
            page.configure_portfolio_monitoring_page_targets({})

        self.assertIsNone(result)
        self.assertEqual(state["backtest_requested_panel"], "Final Review")
        self.assertEqual(
            state["final_review_active_decision_brief_source_id"],
            "practical_validation_result:validation-latest-hold",
        )
        self.assertEqual(switch_calls, [target])

    def test_default_tracking_end_uses_original_selected_decision_replay_path(
        self,
    ) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        calls = []
        item = SimpleNamespace(source_type="selected_strategy")
        lane = object()
        resolution = object()
        adapter = SimpleNamespace(
            build_tracking_end_lane=lambda value, end_date: calls.append(
                ("tracking_end", value, end_date)
            )
            or lane,
            build_value_lane=lambda *args, **kwargs: self.fail(
                "tracking end must not use the lifecycle-locked value lane"
            ),
        )

        def execute_end(repository, command, *, resolve_end):
            self.assertIs(resolve_end(item), resolution)
            return CommandResult(
                status=CommandStatus.SUCCEEDED,
                command_id=command.command_id,
                target_id=command.target_id,
                replayed=False,
                message="ended",
            )

        fake_st = SimpleNamespace(session_state={}, rerun=lambda: None)
        with (
            patch.object(page, "st", fake_st),
            patch.object(
                page,
                "MySQLMonitoringRepository",
                return_value=SimpleNamespace(),
            ),
            patch.object(
                page,
                "MySQLMonitoringHistoryRepository",
                return_value=SimpleNamespace(),
            ),
            patch.object(
                page,
                "SelectedStrategyReplayAdapter",
                return_value=adapter,
            ),
            patch.object(page, "execute_end_item", side_effect=execute_end),
            patch.object(
                page,
                "resolve_tracking_end",
                side_effect=lambda value, requested: (
                    self.assertIs(value, lane),
                    self.assertEqual(requested, date(2026, 7, 23)),
                    resolution,
                )[-1],
            ),
        ):
            services = page._default_portfolio_monitoring_services()
            result = services.end_item(
                {
                    "command_id": "command-end",
                    "monitoring_item_id": "item-strategy",
                    "requested_end_date": "2026-07-23",
                }
            )

        self.assertEqual(result.status, CommandStatus.SUCCEEDED)
        self.assertEqual(
            calls,
            [("tracking_end", item, date(2026, 8, 2))],
        )

    def test_dispatches_group_price_refresh_once(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        event = {
            "id": "refresh_group_prices",
            "command_id": "command-refresh",
            "portfolio_group_id": "group-core",
        }

        result = page._dispatch_portfolio_monitoring_event(event, services)

        self.assertIn(("refresh_group_prices", event), services.calls)
        self.assertEqual(result["status"], "success")

    def test_route_preserves_partial_refresh_as_warning_feedback(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services(
            component_value={
                "event": {
                    "id": "refresh_group_prices",
                    "command_id": "command-refresh-warning",
                    "portfolio_group_id": "group-core",
                }
            }
        )
        services.refresh_group_prices = lambda event: {
            "command_id": event["command_id"],
            "status": "warning",
            "message": "QQQ 종목이 아직 이전 날짜입니다.",
            "target_id": event["portfolio_group_id"],
        }

        page.render_final_selected_portfolio_dashboard_page(services=services)

        self.assertEqual(
            services.session_state["portfolio_monitoring_last_command"]["status"],
            "warning",
        )
        self.assertEqual(sum(call[0] == "rerun" for call in services.calls), 1)

    def test_refresh_bridge_runs_selected_group_and_appends_ingestion_history(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        items = [SimpleNamespace(source_ref="AMD")]
        repository = SimpleNamespace(
            get_group=lambda group_id: SimpleNamespace(portfolio_group_id=group_id),
            list_items=lambda group_id: items,
        )
        calls = []

        result = page._execute_portfolio_price_refresh(
            {
                "command_id": "command-refresh",
                "portfolio_group_id": "group-core",
            },
            repository=repository,
            refresh_runner=lambda received: calls.append(("run", received))
            or {
                "status": "partial_success",
                "rows_written": 2,
                "failed_symbols": ["QQQ"],
                "message": "QQQ remains stale",
            },
            history_writer=lambda job_result: calls.append(("history", job_result)),
        )

        self.assertEqual(calls[0], ("run", items))
        self.assertEqual(calls[1][0], "history")
        self.assertEqual(result["command_id"], "command-refresh")
        self.assertEqual(result["status"], "warning")
        self.assertEqual(result["target_id"], "group-core")

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

    def test_initial_entry_lookup_resolves_requested_to_effective_market_date(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        frame = pd.DataFrame(
            [
                {"date": "2026-06-29", "close": 95},
                {"date": "2026-06-30", "close": 97},
            ]
        )
        item = SimpleNamespace(source_ref="AMD")
        with patch.object(page, "load_price_history", return_value=frame):
            result = page._resolve_initial_position_entry(
                item,
                date(2026, 6, 28),
                40,
            )

        self.assertEqual(result.effective_start_date, date(2026, 6, 29))
        self.assertEqual(result.entry_close, Decimal("95"))
        self.assertEqual(result.initial_capital, Decimal("3800"))

    def test_initial_entry_lookup_preserves_correction_editor_state(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        services = self._services()
        page._dispatch_portfolio_monitoring_event(
            {
                "id": "lookup_initial_position_entry",
                "monitoring_item_id": "item-amd",
                "requested_start_date": "2026-06-28",
                "quantity": 40,
                "position_editor_state": {
                    "open": True,
                    "mode": "correction",
                    "position_effect": "buy",
                    "trade_date": "2026-06-28",
                    "quantity": "40",
                    "execution_price": "",
                    "price_mode": "awaiting_close",
                    "fee_usd": "0",
                    "note": "최초 설정 수정",
                    "root_event_id": "",
                    "expected_event_id": "",
                    "unexpected": "drop",
                },
            },
            services,
        )

        self.assertEqual(
            services.session_state[
                "portfolio_monitoring_initial_requested_start_date"
            ],
            "2026-06-28",
        )
        self.assertEqual(
            services.session_state["portfolio_monitoring_initial_quantity"],
            40,
        )
        recovered = services.session_state[
            "portfolio_monitoring_position_editor_state"
        ]
        self.assertEqual(recovered["mode"], "correction")
        self.assertEqual(recovered["trade_date"], "2026-06-28")
        self.assertNotIn("unexpected", recovered)

    def test_corrected_contract_controls_position_history_start(self) -> None:
        from app.web import final_selected_portfolio_dashboard as page

        item = MonitoringItemRecord(
            monitoring_item_id="item-amd",
            portfolio_group_id="group-core",
            source_type="direct_security",
            source_ref="AMD",
            instrument_kind="stock",
            requested_start_date=date(2026, 7, 1),
            effective_start_date=date(2026, 7, 1),
            funding_mode="fixed_shares",
            input_notional=None,
            input_shares=30,
            entry_close=Decimal("100"),
            initial_capital=Decimal("3000"),
        )
        correction = PositionEventRecord(
            position_event_id="correct-v1",
            root_event_id="correct-root",
            supersedes_event_id=None,
            monitoring_item_id=item.monitoring_item_id,
            event_order=1,
            event_action="create",
            position_effect="initial_quantity_correction",
            trade_date=date(2026, 6, 29),
            quantity=40,
            execution_price=None,
            reference_close=Decimal("95"),
            execution_price_source=None,
            fee_usd=Decimal("0"),
            note="",
            command_id="correct-command",
            requested_start_date=date(2026, 6, 28),
            effective_start_date=date(2026, 6, 29),
        )

        self.assertEqual(
            page._effective_position_history_start(item, [correction]),
            date(2026, 6, 29),
        )
        self.assertEqual(
            page._effective_position_history_start(item, []),
            date(2026, 7, 1),
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
