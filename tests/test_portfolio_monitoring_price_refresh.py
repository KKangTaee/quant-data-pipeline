from __future__ import annotations

import unittest
from datetime import date, datetime
from types import SimpleNamespace
from zoneinfo import ZoneInfo

import pandas as pd


def _item(
    symbol: str,
    *,
    source_type: str = "direct_security",
    instrument_kind: str = "stock",
    status: str = "active",
    effective_start_date: date = date(2026, 6, 1),
):
    return SimpleNamespace(
        source_ref=symbol,
        source_type=source_type,
        instrument_kind=instrument_kind,
        status=status,
        effective_start_date=effective_start_date,
    )


class PortfolioMonitoringPriceRefreshPlanTests(unittest.TestCase):
    def test_plan_targets_only_deduplicated_active_direct_stocks_and_etfs(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            build_portfolio_price_refresh_plan,
        )

        calls = []

        def freshness_loader(symbols, *, end, timeframe):
            calls.append((symbols, end, timeframe))
            return pd.DataFrame(
                [
                    {"symbol": "AMD", "latest_date": "2026-07-20"},
                    {"symbol": "QQQ", "latest_date": "2026-07-17"},
                ]
            )

        plan = build_portfolio_price_refresh_plan(
            [
                _item("amd"),
                _item("AMD"),
                _item("qqq", instrument_kind="etf", status="data_review"),
                _item("SOXX", status="ended"),
                _item(
                    "strategy-1",
                    source_type="selected_strategy",
                    instrument_kind="strategy",
                ),
            ],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=freshness_loader,
        )

        self.assertEqual(calls, [(["AMD", "QQQ"], "2026-07-21", "1d")])
        self.assertTrue(plan["eligible"])
        self.assertEqual(plan["status"], "refresh_available")
        self.assertEqual(plan["symbols"], ["AMD", "QQQ"])
        self.assertEqual(plan["target_date"], "2026-07-21")
        self.assertEqual(plan["current_common_latest"], "2026-07-17")
        self.assertEqual(plan["stale_symbols"], ["AMD", "QQQ"])
        self.assertEqual(plan["missing_symbols"], [])
        self.assertEqual(plan["collection_start"], "2026-07-10")
        self.assertEqual(plan["collection_end"], "2026-07-21")
        self.assertEqual(plan["excluded_strategy_count"], 1)


class PortfolioMonitoringPriceRefreshExecutionTests(unittest.TestCase):
    def test_refresh_runs_existing_ohlcv_job_and_verifies_success(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            run_portfolio_price_refresh,
        )

        freshness_frames = iter(
            [
                pd.DataFrame([{"symbol": "AMD", "latest_date": "2026-07-17"}]),
                pd.DataFrame([{"symbol": "AMD", "latest_date": "2026-07-21"}]),
            ]
        )
        runner_calls = []

        def runner(symbols, **kwargs):
            runner_calls.append((symbols, kwargs))
            return {
                "job_name": "collect_ohlcv",
                "status": "success",
                "rows_written": 3,
                "symbols_requested": 1,
                "symbols_processed": 1,
                "failed_symbols": [],
                "message": "collected",
                "details": {},
            }

        result = run_portfolio_price_refresh(
            [_item("AMD")],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: next(freshness_frames),
            runner=runner,
        )

        self.assertEqual(
            runner_calls,
            [
                (
                    ["AMD"],
                    {
                        "start": "2026-07-10",
                        "end": "2026-07-21",
                        "period": "1mo",
                        "interval": "1d",
                        "execution_profile": "managed_safe",
                    },
                )
            ],
        )
        self.assertEqual(result["job_name"], "portfolio_monitoring_price_refresh")
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["details"]["post_refresh_unresolved_symbols"], [])
        self.assertEqual(
            result["run_metadata"]["pipeline_type"],
            "portfolio_monitoring_price_refresh",
        )

    def test_refresh_reports_partial_success_when_one_symbol_remains_stale(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            run_portfolio_price_refresh,
        )

        freshness_frames = iter(
            [
                pd.DataFrame(
                    [
                        {"symbol": "AMD", "latest_date": "2026-07-17"},
                        {"symbol": "QQQ", "latest_date": "2026-07-16"},
                    ]
                ),
                pd.DataFrame(
                    [
                        {"symbol": "AMD", "latest_date": "2026-07-21"},
                        {"symbol": "QQQ", "latest_date": "2026-07-17"},
                    ]
                ),
            ]
        )
        result = run_portfolio_price_refresh(
            [_item("AMD"), _item("QQQ", instrument_kind="etf")],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: next(freshness_frames),
            runner=lambda *args, **kwargs: {
                "status": "success",
                "rows_written": 4,
                "failed_symbols": [],
                "message": "collected",
                "details": {},
            },
        )

        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["failed_symbols"], ["QQQ"])
        self.assertEqual(
            result["details"]["post_refresh_unresolved_symbols"], ["QQQ"]
        )
        self.assertIn("QQQ", result["message"])

    def test_refresh_with_no_rows_and_unresolved_symbol_is_failed(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            run_portfolio_price_refresh,
        )

        stale = pd.DataFrame([{"symbol": "SOXX", "latest_date": "2026-07-16"}])
        result = run_portfolio_price_refresh(
            [_item("SOXX", instrument_kind="etf")],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: stale,
            runner=lambda *args, **kwargs: {
                "status": "failed",
                "rows_written": 0,
                "failed_symbols": ["SOXX"],
                "message": "no rows",
                "details": {},
            },
        )

        self.assertEqual(result["status"], "failed")
        self.assertEqual(result["failed_symbols"], ["SOXX"])
        self.assertIn("최신화하지 못했습니다", result["message"])

    def test_current_group_skips_without_running_ingestion(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            run_portfolio_price_refresh,
        )

        result = run_portfolio_price_refresh(
            [_item("AMD")],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: pd.DataFrame(
                [{"symbol": "AMD", "latest_date": "2026-07-21"}]
            ),
            runner=lambda *args, **kwargs: self.fail("runner must not be called"),
        )

        self.assertEqual(result["status"], "skipped")
        self.assertEqual(result["rows_written"], 0)
        self.assertIn("최신", result["message"])

    def test_missing_symbol_uses_its_effective_tracking_start(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            build_portfolio_price_refresh_plan,
        )

        plan = build_portfolio_price_refresh_plan(
            [_item("TEM", effective_start_date=date(2026, 7, 3))],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: pd.DataFrame(),
        )

        self.assertTrue(plan["eligible"])
        self.assertEqual(plan["missing_symbols"], ["TEM"])
        self.assertEqual(plan["current_common_latest"], None)
        self.assertEqual(plan["collection_start"], "2026-07-03")

    def test_current_group_hides_refresh_action(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            build_portfolio_price_refresh_plan,
        )

        plan = build_portfolio_price_refresh_plan(
            [_item("AMD")],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: pd.DataFrame(
                [{"symbol": "AMD", "latest_date": "2026-07-21"}]
            ),
        )

        self.assertFalse(plan["eligible"])
        self.assertEqual(plan["status"], "up_to_date")
        self.assertEqual(plan["stale_symbols"], [])
        self.assertEqual(plan["collection_start"], None)

    def test_group_without_active_direct_security_is_unavailable(self) -> None:
        from app.services.portfolio_monitoring.price_refresh import (
            build_portfolio_price_refresh_plan,
        )

        plan = build_portfolio_price_refresh_plan(
            [
                _item(
                    "strategy-1",
                    source_type="selected_strategy",
                    instrument_kind="strategy",
                )
            ],
            now=datetime(2026, 7, 21, 18, tzinfo=ZoneInfo("America/New_York")),
            freshness_loader=lambda *args, **kwargs: self.fail(
                "freshness loader must not run without eligible symbols"
            ),
        )

        self.assertFalse(plan["eligible"])
        self.assertEqual(plan["status"], "unavailable")
        self.assertEqual(plan["symbols"], [])
        self.assertEqual(plan["excluded_strategy_count"], 1)


if __name__ == "__main__":
    unittest.main()
