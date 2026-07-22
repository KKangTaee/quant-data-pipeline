from __future__ import annotations

import importlib
import importlib.util
import tempfile
import unittest
from datetime import datetime, timezone
from decimal import Decimal
from pathlib import Path
from unittest.mock import MagicMock, patch


class TodayHomeReadModelTests(unittest.TestCase):
    def _builder(self):
        spec = importlib.util.find_spec("app.services.today")
        self.assertIsNotNone(spec, "Today read-model service should exist")
        module = importlib.import_module("app.services.today")
        builder = getattr(module, "build_today_read_model", None)
        self.assertTrue(callable(builder), "build_today_read_model should be callable")
        return builder

    @staticmethod
    def _complete_inputs() -> dict[str, object]:
        return {
            "economic_cycle": {
                "status": "READY",
                "as_of_date": "2026-06-30",
                "headline": {
                    "phase": "recovery",
                    "phase_label": "회복",
                    "summary": "현재는 회복 국면 가능성이 가장 높습니다.",
                },
            },
            "sp500": {
                "status": "READY",
                "multiple_regime": {
                    "status": "READY",
                    "bucket": "HIGH",
                    "current_pe": 28.8,
                    "mean_multiple": 25.1,
                    "current_basis_date": "2026-07-16",
                    "current_is_provisional": False,
                },
                "earnings_scenario": {"status": "READY"},
            },
            "futures_macro": {
                "status": "READY",
                "metadata": {"as_of_date": "2026-07-21"},
                "macro": {
                    "status": "OK",
                    "summary": {
                        "scenario": "달러 강세 · 금리 혼재",
                        "summary": "단기 재가격화 신호가 엇갈립니다.",
                    },
                },
            },
            "sentiment": {
                "status": "OK",
                "coverage": {"source_count": 2, "stale_count": 0, "missing_count": 0},
                "analysis": {
                    "phase_label": "행동 공포 · 설문 낙관",
                    "headline": "시장 행동과 개인투자자 설문이 엇갈립니다.",
                    "tone": "warning",
                    "axes": {
                        "market_behavior": {"latest_date": "2026-07-21"},
                        "investor_survey": {"latest_date": "2026-07-16"},
                    },
                },
            },
            "events": {
                "status": "OK",
                "coverage": {"event_count": 1, "next_event_date": "2026-07-29"},
                "rows": [
                    {
                        "Date": "2026-07-29",
                        "Type": "FOMC_MEETING",
                        "Title": "FOMC Meeting",
                        "Importance": "High",
                        "Days Until": 7,
                    }
                ],
            },
            "portfolio": {
                "generated_at": "2026-07-22T08:00:00",
                "groups": [
                    {
                        "portfolio_group_id": "core",
                        "name": "Core",
                        "is_default": True,
                        "selected": True,
                        "active_item_count": 2,
                    }
                ],
                "active_group": {
                    "status": "READY",
                    "basis_date": "2026-07-21",
                    "active_item_count": 2,
                    "failures": {},
                    "curve": [
                        {"date": "2026-07-18", "unit_value": 1.00},
                        {"date": "2026-07-21", "unit_value": 1.02},
                    ],
                    "metrics": {
                        "current_value": Decimal("1200"),
                        "total_return": Decimal("0.20"),
                        "contribution_by_item": {
                            "nvda": Decimal("240"),
                            "tlt": Decimal("-40"),
                        },
                    },
                    "item_rows": [
                        {
                            "monitoring_item_id": "nvda",
                            "source_ref": "NVDA",
                            "total_return": Decimal("0.42"),
                        },
                        {
                            "monitoring_item_id": "tlt",
                            "source_ref": "TLT",
                            "total_return": Decimal("-0.08"),
                        },
                    ],
                },
                "now_to_review": [
                    {
                        "severity": "HIGH",
                        "meaning": "Technology 노출이 집중 기준을 넘었습니다.",
                    }
                ],
            },
        }

    def test_complete_inputs_build_market_and_representative_portfolio(self) -> None:
        model = self._builder()(
            **self._complete_inputs(),
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(model["schema_version"], "today_home_v3")
        self.assertEqual(model["header"]["source_ready_count"], 5)
        self.assertEqual(
            model["header"]["as_of_date"],
            "2026-07-21",
            "future event dates must not become the saved-data basis date",
        )
        self.assertEqual(model["market"]["status"], "READY")
        self.assertEqual(
            [row["key"] for row in model["market"]["evidence"]],
            ["economic_cycle", "sp500", "futures_macro", "sentiment"],
        )
        self.assertEqual(model["market"]["next_event"]["title"], "FOMC Meeting")
        self.assertEqual(model["portfolio"]["status"], "READY")
        self.assertEqual(model["portfolio"]["name"], "Core")
        self.assertEqual(model["portfolio"]["metrics"]["current_value"], 1200.0)
        self.assertAlmostEqual(
            model["portfolio"]["metrics"]["latest_observation_return"],
            0.02,
        )
        self.assertEqual(
            model["portfolio"]["metrics"]["return_from_date"],
            "2026-07-18",
        )
        self.assertEqual(
            model["portfolio"]["metrics"]["return_to_date"],
            "2026-07-21",
        )
        self.assertAlmostEqual(model["portfolio"]["metrics"]["total_return"], 0.20)
        self.assertEqual(
            model["portfolio"]["contributors"][0],
            {
                "symbol": "NVDA",
                "contribution_value": 240.0,
                "value": 240.0,
                "total_return": 0.42,
                "tone": "positive",
            },
        )
        self.assertEqual(
            model["portfolio"]["contributors"][-1],
            {
                "symbol": "TLT",
                "contribution_value": -40.0,
                "value": -40.0,
                "total_return": -0.08,
                "tone": "negative",
            },
        )

    def test_contributor_keeps_contribution_when_item_return_is_missing(self) -> None:
        inputs = self._complete_inputs()
        inputs["portfolio"]["active_group"]["item_rows"][0]["total_return"] = None

        model = self._builder()(**inputs)

        contributor = model["portfolio"]["contributors"][0]
        self.assertEqual(contributor["symbol"], "NVDA")
        self.assertEqual(contributor["contribution_value"], 240.0)
        self.assertIsNone(contributor["total_return"])

    def test_insufficient_market_sources_hold_the_combined_judgment(self) -> None:
        inputs = self._complete_inputs()
        inputs["economic_cycle"] = {"status": "MISSING"}
        inputs["sp500"] = {"status": "MISSING"}
        inputs["futures_macro"] = {"status": "MISSING", "reason": "저장 자료 없음"}
        inputs["sentiment"] = {"status": "MISSING"}

        model = self._builder()(
            **inputs,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(model["market"]["status"], "UNAVAILABLE")
        self.assertIn("종합 판단 보류", model["market"]["headline"])
        self.assertGreaterEqual(len(model["market"]["watch_items"]), 1)

    def test_degraded_market_evidence_never_becomes_ready_from_event_availability(self) -> None:
        inputs = self._complete_inputs()
        inputs["economic_cycle"]["status"] = "LIMITED"
        inputs["sp500"]["multiple_regime"]["current_is_provisional"] = True
        inputs["futures_macro"]["macro"]["status"] = "LIMITED"
        inputs["sentiment"]["coverage"]["stale_count"] = 1

        model = self._builder()(
            **inputs,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(model["market"]["status"], "PARTIAL")
        self.assertLess(model["header"]["source_ready_count"], model["header"]["source_count"])
        self.assertNotIn("종합 판단 보류", model["market"]["headline"])

    def test_two_market_evidence_plus_ready_event_still_holds_headline(self) -> None:
        inputs = self._complete_inputs()
        inputs["economic_cycle"] = {"status": "MISSING"}
        inputs["futures_macro"] = {"status": "MISSING"}

        model = self._builder()(
            **inputs,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(model["market"]["status"], "UNAVAILABLE")
        self.assertIn("종합 판단 보류", model["market"]["headline"])

    def test_sp500_insufficient_history_without_usable_values_is_unavailable(self) -> None:
        inputs = self._complete_inputs()
        inputs["sp500"] = {
            "status": "INSUFFICIENT_HISTORY",
            "multiple_regime": {"status": "INSUFFICIENT_HISTORY"},
        }

        model = self._builder()(
            **inputs,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        sp500 = next(row for row in model["market"]["evidence"] if row["key"] == "sp500")
        self.assertEqual(sp500["status"], "UNAVAILABLE")
        self.assertEqual(model["market"]["status"], "PARTIAL")
        self.assertEqual(model["header"]["source_ready_count"], 4)

    def test_empty_default_group_does_not_fabricate_zero_returns(self) -> None:
        inputs = self._complete_inputs()
        inputs["portfolio"] = {
            "groups": [
                {
                    "portfolio_group_id": "core",
                    "name": "Core",
                    "is_default": True,
                    "selected": True,
                    "active_item_count": 0,
                }
            ],
            "active_group": {
                "status": "EMPTY",
                "active_item_count": 0,
                "curve": [],
                "metrics": {},
                "item_rows": [],
                "failures": {},
            },
            "now_to_review": [],
        }

        model = self._builder()(
            **inputs,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(model["portfolio"]["status"], "EMPTY")
        self.assertIsNone(model["portfolio"]["metrics"]["current_value"])
        self.assertIsNone(
            model["portfolio"]["metrics"]["latest_observation_return"]
        )
        self.assertIsNone(model["portfolio"]["metrics"]["total_return"])

    def test_portfolio_storage_failure_is_unavailable_not_empty(self) -> None:
        inputs = self._complete_inputs()
        inputs["portfolio"] = {
            "status": "ERROR",
            "groups": [],
            "active_group": None,
            "boundaries": {
                "storage_ready": False,
                "storage_error": "connection failed",
            },
        }

        model = self._builder()(
            **inputs,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(model["portfolio"]["status"], "UNAVAILABLE")
        self.assertIn("확인할 수 없습니다", model["portfolio"]["summary"])

    def test_market_evidence_projects_explicit_signal_risk_and_quality_labels(self) -> None:
        inputs = self._complete_inputs()
        inputs["futures_macro"]["macro"]["summary"]["tone"] = "mixed"
        inputs["sentiment"]["coverage"]["stale_count"] = 1

        model = self._builder()(**inputs)

        rows = {row["key"]: row for row in model["market"]["evidence"]}
        self.assertEqual(rows["economic_cycle"]["signal_level"], "support")
        self.assertEqual(rows["economic_cycle"]["risk_label"], "위험도 낮음")
        self.assertEqual(rows["sp500"]["signal_level"], "watch")
        self.assertEqual(rows["sp500"]["risk_label"], "위험도 높음")
        self.assertEqual(rows["futures_macro"]["signal_level"], "neutral")
        self.assertEqual(rows["sentiment"]["data_quality_label"], "자료 제한")

    def test_unavailable_evidence_never_fabricates_low_or_high_risk(self) -> None:
        inputs = self._complete_inputs()
        inputs["economic_cycle"] = {"status": "UNAVAILABLE"}

        model = self._builder()(**inputs)

        row = next(
            item
            for item in model["market"]["evidence"]
            if item["key"] == "economic_cycle"
        )
        self.assertEqual(row["signal_level"], "limited")
        self.assertEqual(row["risk_label"], "판단 제한")
        self.assertNotIn(row["risk_label"], {"위험도 낮음", "위험도 높음"})

    def test_portfolio_curve_identifies_daily_stored_close_and_exact_return_dates(self) -> None:
        inputs = self._complete_inputs()
        inputs["portfolio"]["active_group"]["curve"] = [
            {"date": "2026-07-17", "unit_value": 1.00, "total_value": 10000},
            {"date": "2026-07-18", "unit_value": 1.02, "total_value": 10200},
            {"date": "2026-07-21", "unit_value": 1.0812, "total_value": 10812},
        ]

        model = self._builder()(**inputs)

        portfolio = model["portfolio"]
        self.assertEqual(model["schema_version"], "today_home_v3")
        self.assertAlmostEqual(
            portfolio["metrics"]["latest_observation_return"],
            0.06,
            places=10,
        )
        self.assertEqual(portfolio["metrics"]["return_from_date"], "2026-07-18")
        self.assertEqual(portfolio["metrics"]["return_to_date"], "2026-07-21")
        self.assertEqual(portfolio["curve"][0]["cumulative_return"], 0.0)
        self.assertEqual(portfolio["curve"][-1]["total_value"], 10812.0)
        self.assertEqual(
            portfolio["curve_metadata"],
            {
                "interval": "daily",
                "price_basis": "stored_close",
                "aggregation": "none",
                "intraday": False,
                "observation_count": 3,
                "start_date": "2026-07-17",
                "end_date": "2026-07-21",
            },
        )

    def test_today_contract_is_read_only_and_context_only(self) -> None:
        model = self._builder()(
            **self._complete_inputs(),
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        self.assertEqual(
            model["boundaries"],
            {
                "db_only": True,
                "provider_fetch": False,
                "ingestion_job": False,
                "registry_write": False,
                "monitoring_log_write": False,
                "trading_signal": False,
                "live_orders": False,
                "auto_rebalance": False,
            },
        )

    def test_market_session_does_not_change_evidence_readiness(self) -> None:
        inputs = self._complete_inputs()

        model = self._builder()(
            **inputs,
            market_calendar={"holiday_rows": [], "early_close_rows": []},
            generated_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(model["schema_version"], "today_home_v3")
        self.assertEqual(model["header"]["source_count"], 5)
        self.assertEqual(model["header"]["source_ready_count"], 5)
        self.assertEqual(
            model["market_session"]["schema_version"],
            "market_session_v1",
        )
        self.assertFalse(model["boundaries"]["provider_fetch"])

    def test_market_calendar_loader_status_reaches_session_quality(self) -> None:
        model = self._builder()(
            **self._complete_inputs(),
            market_calendar={
                "holiday_rows": [
                    {"Date": "2026-07-03", "Title": "Independence Day"}
                ],
                "early_close_rows": [],
                "statuses": {"holiday": "OK", "early_close": "ERROR"},
            },
            generated_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
        )

        self.assertEqual(model["market_session"]["calendar_quality"], "LIMITED")
        self.assertIn(
            "공식 조기폐장 일정 자료 부족",
            model["market_session"]["warnings"],
        )


class TodayMarketSessionTests(unittest.TestCase):
    def _builder(self):
        module = importlib.import_module("app.services.today_market_session")
        return module.build_us_market_session_model

    def test_regular_day_uses_new_york_wall_clock_and_utc_boundaries(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {"Date": "2026-07-03", "Title": "Independence Day"}
            ],
            early_close_rows=[
                {
                    "Date": "2026-11-27",
                    "Event Time": "Early close 13:00 ET",
                }
            ],
        )

        today = next(
            row
            for row in model["schedule"]
            if row["trade_date"] == "2026-07-22"
        )
        self.assertEqual(today["day_kind"], "TRADING_DAY")
        self.assertEqual(today["open_at_utc"], "2026-07-22T13:30:00+00:00")
        self.assertEqual(today["close_at_utc"], "2026-07-22T20:00:00+00:00")
        self.assertFalse(today["is_early_close"])
        self.assertEqual(
            model["timezones"],
            {"market": "America/New_York", "viewer": "Asia/Seoul"},
        )

    def test_winter_and_summer_keep_0930_et_but_shift_utc_boundary(self) -> None:
        summer = self._builder()(
            generated_at=datetime(2026, 7, 22, 0, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {"Date": "2026-07-03", "Title": "Independence Day"}
            ],
            early_close_rows=[],
        )["schedule"][0]
        winter = self._builder()(
            generated_at=datetime(2026, 12, 2, 0, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {"Date": "2026-12-25", "Title": "Christmas Day"}
            ],
            early_close_rows=[],
        )["schedule"][0]

        self.assertEqual(summer["open_at_utc"][11:16], "13:30")
        self.assertEqual(winter["open_at_utc"][11:16], "14:30")

    def test_holiday_and_weekend_rows_have_no_session_boundaries(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 7, 3, 12, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {
                    "Date": "2026-07-03",
                    "Title": "US Market Holiday: Independence Day",
                }
            ],
            early_close_rows=[],
        )

        holiday, weekend = model["schedule"][:2]
        self.assertEqual(
            (holiday["day_kind"], holiday["open_at_utc"]),
            ("HOLIDAY", None),
        )
        self.assertIn("Independence Day", holiday["holiday_label"])
        self.assertEqual(
            (weekend["day_kind"], weekend["open_at_utc"]),
            ("WEEKEND", None),
        )

    def test_official_early_close_uses_1300_et(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {"Date": "2026-11-26", "Title": "Thanksgiving Day"}
            ],
            early_close_rows=[
                {
                    "Date": "2026-11-27",
                    "Event Time": "Early close 13:00 ET",
                }
            ],
        )

        self.assertEqual(
            model["schedule"][0]["close_at_utc"],
            "2026-11-27T18:00:00+00:00",
        )
        self.assertTrue(model["schedule"][0]["is_early_close"])

    def test_malformed_early_close_time_keeps_regular_close_and_warns(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 11, 27, 12, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {"Date": "2026-11-26", "Title": "Thanksgiving Day"}
            ],
            early_close_rows=[
                {"Date": "2026-11-27", "Event Time": "Early close"}
            ],
        )

        self.assertEqual(
            model["schedule"][0]["close_at_utc"],
            "2026-11-27T21:00:00+00:00",
        )
        self.assertFalse(model["schedule"][0]["is_early_close"])
        self.assertEqual(model["calendar_quality"], "LIMITED")
        self.assertIn("2026-11-27", model["warnings"][0])

    def test_failed_calendar_source_marks_schedule_limited(self) -> None:
        model = self._builder()(
            generated_at=datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc),
            holiday_rows=[
                {"Date": "2026-07-03", "Title": "Independence Day"}
            ],
            early_close_rows=[],
            calendar_statuses={"holiday": "OK", "early_close": "ERROR"},
        )

        self.assertEqual(model["calendar_quality"], "LIMITED")


class TodayHomePageContractTests(unittest.TestCase):
    def test_today_market_calendar_loads_holidays_and_early_closes_separately(
        self,
    ) -> None:
        page = importlib.import_module("app.web.today_page")
        fake = MagicMock(
            side_effect=[
                {"status": "OK", "rows": []},
                {"status": "OK", "rows": []},
            ]
        )
        generated_at = datetime(2026, 7, 22, 13, 0, tzinfo=timezone.utc)

        with patch.object(page, "build_market_events_snapshot", fake):
            result = page.load_today_market_calendar(
                generated_at=generated_at,
            )

        self.assertEqual(
            set(result),
            {"holiday_rows", "early_close_rows", "statuses"},
        )
        self.assertEqual(
            [call.kwargs["event_type"] for call in fake.call_args_list],
            ["MARKET_HOLIDAY", "EARLY_CLOSE"],
        )
        self.assertEqual(
            fake.call_args_list[0].kwargs["start_date"],
            "2026-01-01",
        )
        self.assertEqual(
            fake.call_args_list[0].kwargs["end_date"],
            "2027-12-31",
        )

    def test_today_react_renders_regular_market_status_without_extended_hours(
        self,
    ) -> None:
        root = Path("app/web/streamlit_components/today_workbench/src")
        source = (root / "TodayWorkbench.tsx").read_text(encoding="utf-8")
        styles = (root / "style.css").read_text(encoding="utf-8")

        self.assertIn("미국 정규장", source)
        self.assertIn("뉴욕", source)
        self.assertIn("한국", source)
        self.assertIn("resolveMarketSession", source)
        self.assertIn("setInterval", source)
        self.assertIn(".today-market-session", styles)
        self.assertNotIn("프리마켓", source)
        self.assertNotIn("애프터마켓", source)

    def test_today_react_source_uses_explicit_risk_labels_and_chart_semantics(self) -> None:
        root = Path("app/web/streamlit_components/today_workbench/src")
        workbench = (root / "TodayWorkbench.tsx").read_text(encoding="utf-8")
        chart = (root / "TodayPortfolioChart.tsx").read_text(encoding="utf-8")
        styles = (root / "style.css").read_text(encoding="utf-8")

        self.assertIn("signal_label", workbench)
        self.assertIn("risk_label", workbench)
        self.assertNotIn("border-left", styles)
        self.assertIn("일별 종가 기반 누적 수익률", chart)
        self.assertIn("장중 아님", chart)
        self.assertIn("Y축 · 누적 수익률 (%)", chart)
        self.assertIn("X축 · 저장 관측일", chart)
        self.assertIn("total_value", chart)
        self.assertIn("font-size: 26px", styles)

    def test_today_component_availability_requires_built_index(self) -> None:
        component = importlib.import_module("app.web.today_react_component")
        with tempfile.TemporaryDirectory() as directory:
            build = Path(directory)
            self.assertFalse(component.today_react_component_available(build))
            (build / "index.html").write_text("<html></html>", encoding="utf-8")
            self.assertTrue(component.today_react_component_available(build))

    def test_today_component_returns_event_envelope(self) -> None:
        component = importlib.import_module("app.web.today_react_component")
        fake_component = MagicMock(
            return_value={"event": {"id": "open_market_research"}}
        )
        with patch.object(
            component,
            "_declare_today_component",
            return_value=fake_component,
        ):
            result = component.render_today_workbench(
                {"schema_version": "today_home_v2"}
            )

        self.assertEqual(result, {"event": {"id": "open_market_research"}})
        fake_component.assert_called_once_with(
            payload={"schema_version": "today_home_v2"},
            key="today_workbench",
            default={"event": None},
        )

    def test_today_page_uses_react_primary_and_routes_market_event(self) -> None:
        page = importlib.import_module("app.web.today_page")
        fake_st = MagicMock()
        page.configure_today_page_targets(
            {
                "market_research": "market-page",
                "stock_research": "stock-page",
                "portfolio_monitoring": "monitoring-page",
            }
        )
        with (
            patch.object(page, "st", fake_st),
            patch.object(page, "load_today_read_model", return_value={"schema_version": "today_home_v2"}),
            patch.object(page, "today_react_component_available", return_value=True),
            patch.object(
                page,
                "render_today_workbench",
                return_value={"event": {"id": "open_market_research"}},
            ) as render_component,
        ):
            page.render_today_page()

        render_component.assert_called_once_with({"schema_version": "today_home_v2"})
        fake_st.markdown.assert_not_called()
        fake_st.switch_page.assert_called_once_with(
            "market-page",
            query_params={"overview_tab": "market-context"},
        )

    def test_today_page_routes_stock_and_portfolio_events(self) -> None:
        page = importlib.import_module("app.web.today_page")
        routes = (
            (
                "open_stock_research",
                "stock-page",
                {"overview_tab": "market-movers"},
            ),
            ("open_portfolio_monitoring", "monitoring-page", None),
        )
        for event_id, target, query_params in routes:
            with self.subTest(event_id=event_id):
                fake_st = MagicMock()
                page.configure_today_page_targets(
                    {
                        "market_research": "market-page",
                        "stock_research": "stock-page",
                        "portfolio_monitoring": "monitoring-page",
                    }
                )
                with (
                    patch.object(page, "st", fake_st),
                    patch.object(page, "load_today_read_model", return_value={"schema_version": "today_home_v2"}),
                    patch.object(page, "today_react_component_available", return_value=True),
                    patch.object(
                        page,
                        "render_today_workbench",
                        return_value={"event": {"id": event_id}},
                    ),
                ):
                    page.render_today_page()
                if query_params is None:
                    fake_st.switch_page.assert_called_once_with(target)
                else:
                    fake_st.switch_page.assert_called_once_with(
                        target,
                        query_params=query_params,
                    )

    def test_today_page_rejects_unknown_react_event(self) -> None:
        page = importlib.import_module("app.web.today_page")
        fake_st = MagicMock()
        with (
            patch.object(page, "st", fake_st),
            patch.object(page, "load_today_read_model", return_value={"schema_version": "today_home_v2"}),
            patch.object(page, "today_react_component_available", return_value=True),
            patch.object(
                page,
                "render_today_workbench",
                return_value={"event": {"id": "delete_everything"}},
            ),
        ):
            page.render_today_page()

        fake_st.warning.assert_called_once()
        fake_st.switch_page.assert_not_called()

    def test_today_page_falls_back_only_when_react_build_is_unavailable(self) -> None:
        page = importlib.import_module("app.web.today_page")
        fake_st = MagicMock()
        model = {
            "header": {},
            "market": {"evidence": [], "watch_items": []},
            "portfolio": {"metrics": {}, "curve": []},
        }
        with (
            patch.object(page, "st", fake_st),
            patch.object(page, "load_today_read_model", return_value=model),
            patch.object(page, "today_react_component_available", return_value=False),
        ):
            page.render_today_page()

        fake_st.markdown.assert_called_once()
        fake_st.error.assert_called_once()

    def test_today_page_reuses_overview_visual_tokens_and_read_only_loaders(self) -> None:
        path = Path("app/web/today_page.py")
        self.assertTrue(path.exists(), "Today page renderer should exist")
        source = path.read_text(encoding="utf-8")
        react_source = Path(
            "app/web/streamlit_components/today_workbench/src/TodayWorkbench.tsx"
        ).read_text(encoding="utf-8")
        css_source = Path(
            "app/web/streamlit_components/today_workbench/src/style.css"
        ).read_text(encoding="utf-8")
        types_source = Path(
            "app/web/streamlit_components/today_workbench/src/types.ts"
        ).read_text(encoding="utf-8")

        self.assertIn("overview_ui_css", source)
        self.assertIn("load_economic_cycle_model", source)
        self.assertIn("load_sp500_valuation_model", source)
        self.assertIn("load_overview_futures_macro_materialized_snapshot", source)
        self.assertIn("load_overview_market_sentiment_snapshot", source)
        self.assertIn("load_overview_market_events_snapshot", source)
        self.assertIn("load_default_portfolio_monitoring_workspace_for_today", source)
        self.assertNotIn("run_overview_", source)
        self.assertNotIn("requests.", source)
        self.assertIn("종목별 성과 기여", react_source)
        self.assertIn("기여 상위 2 · 하위 2", react_source)
        self.assertIn("수익률 자료 부족", react_source)
        self.assertIn("signedMoneyText(row.contribution_value)", react_source)
        self.assertIn("contribution_value", types_source)
        self.assertIn("total_return", types_source)
        self.assertIn(".today-contributor-grid", css_source)
        self.assertIn(
            "grid-template-columns: repeat(2, minmax(0, 1fr))",
            css_source,
        )

    def test_today_html_preserves_b_layout_order_and_escapes_market_copy(self) -> None:
        spec = importlib.util.find_spec("app.web.today_page")
        self.assertIsNotNone(spec, "Today page renderer should be importable")
        module = importlib.import_module("app.web.today_page")
        renderer = getattr(module, "build_today_html", None)
        self.assertTrue(callable(renderer), "build_today_html should be callable")
        model = {
            "header": {
                "as_of_date": "2026-07-22",
                "source_count": 5,
                "source_ready_count": 4,
                "status": "PARTIAL",
                "status_label": "일부 자료 제한",
            },
            "market": {
                "status": "PARTIAL",
                "tone": "warning",
                "headline": "회복 가능성 <script>alert(1)</script>",
                "summary": "저장 근거 요약",
                "evidence": [
                    {
                        "key": "economic_cycle",
                        "label": "경제 사이클",
                        "status": "PARTIAL",
                        "title": "회복",
                        "detail": "근거 제한",
                        "as_of_date": "2026-06-30",
                        "tone": "warning",
                    }
                ],
                "next_event": {
                    "date": "2026-07-29",
                    "days_until": 7,
                    "type": "FOMC_MEETING",
                    "title": "FOMC Meeting",
                    "importance": "High",
                },
                "watch_items": ["선물 매크로 자료를 확인할 수 없습니다."],
            },
            "portfolio": {
                "status": "READY",
                "name": "Core",
                "basis_date": "2026-07-21",
                "summary": "저장 가격 기준",
                "metrics": {
                    "current_value": 1200.0,
                    "day_return": 0.02,
                    "total_return": 0.20,
                },
                "curve": [
                    {"date": "2026-07-18", "value": 1.0},
                    {"date": "2026-07-21", "value": 1.02},
                ],
                "contributors": [
                    {
                        "symbol": "NVDA",
                        "contribution_value": 240.0,
                        "value": 240.0,
                        "total_return": 0.42,
                        "tone": "positive",
                    }
                ],
                "review_items": [{"severity": "HIGH", "meaning": "집중도 확인"}],
                "active_item_count": 2,
            },
        }

        html = renderer(model)

        self.assertNotIn("<script>alert(1)</script>", html)
        self.assertIn("&lt;script&gt;alert(1)&lt;/script&gt;", html)
        self.assertLess(html.index("today-market-brief"), html.index("today-portfolio"))
        self.assertIn("today-evidence-grid", html)
        self.assertIn("대표 포트폴리오", html)
        self.assertIn("종목별 성과 기여", html)
        self.assertIn("기여 상위 2 · 하위 2", html)
        self.assertIn("종목 누적 수익률", html)
        self.assertIn("+42.00%", html)
        self.assertIn("포트폴리오 누적 기여", html)
        self.assertIn("$240", html)
        self.assertIn("입출금 영향을 조정한 누적 성과", html)

    def test_today_fallback_labels_missing_item_return_without_hiding_contribution(self) -> None:
        module = importlib.import_module("app.web.today_page")
        model = {
            "header": {},
            "market": {"evidence": [], "watch_items": []},
            "portfolio": {
                "status": "READY",
                "basis_date": "2026-07-21",
                "metrics": {},
                "curve": [],
                "contributors": [
                    {
                        "symbol": "AMD",
                        "contribution_value": 11915.0,
                        "value": 11915.0,
                        "total_return": None,
                        "tone": "positive",
                    },
                    {
                        "symbol": "TEM",
                        "contribution_value": -401.0,
                        "value": -401.0,
                        "total_return": None,
                        "tone": "negative",
                    },
                ],
                "review_items": [],
            },
        }

        html = module.build_today_html(model)

        self.assertIn("수익률 자료 부족", html)
        self.assertIn("+$11,915", html)
        self.assertIn("-$401", html)

    def test_today_fallback_keeps_chart_above_one_to_one_contributor_review_grid(self) -> None:
        module = importlib.import_module("app.web.today_page")
        model = {
            "header": {},
            "market": {"evidence": [], "watch_items": []},
            "portfolio": {
                "status": "READY",
                "metrics": {},
                "curve": [],
                "contributors": [],
                "review_items": [],
            },
        }

        html = module.build_today_html(model)
        css = module._today_css()

        visual_index = html.index('<div class="today-portfolio-visual">')
        detail_index = html.index('<div class="today-portfolio-detail-grid">')
        contributor_index = html.index("종목별 성과 기여", detail_index)
        review_index = html.index("우선 확인", detail_index)
        self.assertLess(visual_index, detail_index)
        self.assertLess(detail_index, contributor_index)
        self.assertLess(contributor_index, review_index)

        portfolio_rule = css.split(".today-portfolio {", 1)[1].split("}", 1)[0]
        detail_rule = css.split(".today-portfolio-detail-grid {", 1)[1].split("}", 1)[0]
        tablet_rule = css.split("@media (max-width: 760px) {", 1)[1].split(
            "@media (max-width: 460px) {", 1
        )[0]
        phone_rule = css.split("@media (max-width: 460px) {", 1)[1]
        self.assertIn("grid-template-columns: 1fr", portfolio_rule)
        self.assertIn("grid-template-columns: 1fr 1fr", detail_rule)
        self.assertIn(".today-portfolio-detail-grid", tablet_rule)
        self.assertNotIn(".today-contributor-grid", tablet_rule)
        self.assertIn(".today-contributor-grid", phone_rule)

    def test_unframed_today_header_inherits_streamlit_theme_text_color(self) -> None:
        module = importlib.import_module("app.web.today_page")
        css = module._today_css()
        shell_rule = css.split(".today-shell {", 1)[1].split("}", 1)[0]
        title_rule = css.split(".today-title {", 1)[1].split("}", 1)[0]
        subtitle_rule = css.split(".today-subtitle {", 1)[1].split("}", 1)[0]

        self.assertIn("color: inherit", shell_rule)
        self.assertIn("color: inherit", title_rule)
        self.assertIn("color: inherit", subtitle_rule)

    def test_white_panel_titles_use_overview_card_text_color(self) -> None:
        module = importlib.import_module("app.web.today_page")
        css = module._today_css()
        panel_title_rule = css.split(".today-panel-title {", 1)[1].split("}", 1)[0]

        self.assertIn("var(--ov-mi-color-text)", panel_title_rule)

    def test_today_default_portfolio_loader_is_read_only_and_ignores_active_session_group(self) -> None:
        dashboard = importlib.import_module("app.web.final_selected_portfolio_dashboard")
        persistence = importlib.import_module("app.services.portfolio_monitoring.persistence")
        builder = getattr(dashboard, "_build_default_portfolio_monitoring_workspace", None)
        self.assertTrue(callable(builder), "Today needs a dedicated read-only default-group builder")

        class ReadOnlyRepository:
            def __init__(self) -> None:
                self.write_calls: list[str] = []
                self.groups = [
                    persistence.PortfolioGroupRecord("session-group", "Session", False),
                    persistence.PortfolioGroupRecord("default-group", "Default", True),
                ]

            def list_groups(self, *, include_deleted: bool = False):
                return list(self.groups)

            def list_items(self, portfolio_group_id: str, *, statuses=None):
                return []

            def insert_group(self, record):
                self.write_calls.append("insert_group")
                raise AssertionError("Today render must not write")

            def get_or_create_default_group(self):
                self.write_calls.append("get_or_create_default_group")
                raise AssertionError("Today render must not create a default group")

        repository = ReadOnlyRepository()
        workspace = builder(
            repository,
            generated_at=datetime(2026, 7, 22, 9, 0),
        )

        selected = [row for row in workspace["groups"] if row["selected"]]
        self.assertEqual([row["portfolio_group_id"] for row in selected], ["default-group"])
        self.assertEqual(repository.write_calls, [])


class TodayNavigationContractTests(unittest.TestCase):
    def test_today_is_default_and_legacy_paths_are_preserved(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")

        self.assertIn("from app.web.today_page import", source)
        today_statement = source.split("today_page = st.Page(", 1)[1].split(")", 1)[0]
        self.assertIn('title="Today"', today_statement)
        self.assertIn('url_path="today"', today_statement)
        self.assertIn("default=True", today_statement)
        for legacy_path in (
            "overview",
            "institutional-portfolios",
            "ingestion",
            "backtest",
            "selected-portfolio-dashboard",
            "reference",
        ):
            self.assertIn(f'url_path="{legacy_path}"', source)

    def test_navigation_uses_approved_purpose_groups_and_titles(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")

        for group in ("Research", "Portfolio", "Data", "Help"):
            self.assertIn(f'"{group}": [', source)
        for legacy_group in ("Workspace", "Operations", "Reference"):
            self.assertNotIn(f'"{legacy_group}": [', source)
        for title in (
            "Market Research",
            "Institutional Holdings",
            "Portfolio Lab",
            "Portfolio Monitoring",
            "Data Operations",
            "Reference Center",
        ):
            self.assertIn(f'title="{title}"', source)
        research = source.split('"Research": [', 1)[1].split("],", 1)[0]
        portfolio = source.split('"Portfolio": [', 1)[1].split("],", 1)[0]
        self.assertLess(research.index("today_page"), research.index("overview_page"))
        self.assertLess(
            research.index("overview_page"),
            research.index("institutional_portfolios_page"),
        )
        self.assertLess(portfolio.index("backtest_page"), portfolio.index("selected_portfolio_dashboard_page"))

    def test_today_page_targets_existing_owner_pages(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")

        self.assertIn("configure_today_page_targets(", source)
        self.assertIn('"market_research": overview_page', source)
        self.assertIn('"stock_research": overview_page', source)
        self.assertIn('"portfolio_monitoring": selected_portfolio_dashboard_page', source)


if __name__ == "__main__":
    unittest.main()
