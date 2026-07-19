from __future__ import annotations

import unittest
from datetime import date, timedelta
from decimal import Decimal

import pandas as pd

from app.services.portfolio_monitoring.market_chart import build_selected_item_market_chart
from app.services.portfolio_monitoring.persistence import MonitoringItemRecord


def _item(
    item_id: str,
    *,
    source_type: str = "direct_security",
    instrument_kind: str = "stock",
    status: str = "active",
) -> MonitoringItemRecord:
    return MonitoringItemRecord(
        monitoring_item_id=item_id,
        portfolio_group_id="group-core",
        source_type=source_type,
        source_ref=item_id.upper(),
        instrument_kind=instrument_kind,
        requested_start_date=date(2025, 1, 1),
        effective_start_date=date(2025, 1, 2),
        funding_mode="fixed_notional",
        input_notional=Decimal("10000"),
        input_shares=None,
        entry_close=Decimal("100"),
        initial_capital=Decimal("10000"),
        status=status,
    )


class PortfolioMonitoringMarketChartTests(unittest.TestCase):
    def test_direct_security_compacts_valid_rows_to_latest_120_sessions(self) -> None:
        calls = []
        basis_date = date(2026, 7, 18)
        dates = pd.date_range("2026-01-01", periods=130, freq="D")
        frame = pd.DataFrame(
            {
                "date": dates,
                "open": range(100, 230),
                "high": range(102, 232),
                "low": range(99, 229),
                "close": range(101, 231),
                "volume": [1000] * 129 + [pd.NA],
            }
        )

        def loader(item, start, end):
            calls.append((item.monitoring_item_id, start, end))
            return frame

        result = build_selected_item_market_chart(
            [_item("aapl")],
            selected_item_id="aapl",
            basis_date=basis_date,
            loader=loader,
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(len(result["rows"]), 120)
        self.assertEqual(result["rows"][0]["date"], "2026-01-11")
        self.assertIsNone(result["rows"][-1]["volume"])
        self.assertEqual(calls, [("aapl", basis_date - timedelta(days=240), basis_date)])

    def test_selected_strategy_is_unsupported_without_calling_loader(self) -> None:
        calls = []
        result = build_selected_item_market_chart(
            [_item("strategy", source_type="selected_strategy", instrument_kind="strategy")],
            selected_item_id="strategy",
            basis_date=date(2026, 7, 18),
            loader=lambda *_: calls.append(True),
        )

        self.assertEqual(result["status"], "UNSUPPORTED")
        self.assertEqual(calls, [])
        self.assertIn("OHLCV", result["reason"])

    def test_missing_or_ended_selection_falls_back_to_first_active_item(self) -> None:
        selected = []
        rows = pd.DataFrame(
            [{"date": "2026-07-18", "open": 10, "high": 11, "low": 9, "close": 10.5, "volume": 100}]
        )

        result = build_selected_item_market_chart(
            [_item("ended", status="ended"), _item("active")],
            selected_item_id="missing",
            basis_date=date(2026, 7, 18),
            loader=lambda item, *_: selected.append(item.monitoring_item_id) or rows,
        )

        self.assertEqual(result["monitoring_item_id"], "active")
        self.assertEqual(selected, ["active"])

    def test_invalid_ohlc_rows_are_missing_without_blocking_volume_null(self) -> None:
        invalid = pd.DataFrame(
            [
                {"date": "2026-07-17", "open": 10, "high": 9, "low": 8, "close": 10, "volume": 100},
                {"date": "bad-date", "open": 10, "high": 11, "low": 9, "close": 10, "volume": 100},
            ]
        )

        result = build_selected_item_market_chart(
            [_item("aapl")],
            selected_item_id="aapl",
            basis_date=date(2026, 7, 18),
            loader=lambda *_: invalid,
        )

        self.assertEqual(result["status"], "MISSING")
        self.assertEqual(result["rows"], [])

    def test_loader_error_is_isolated_in_error_projection(self) -> None:
        def broken_loader(*_):
            raise RuntimeError("database unavailable")

        result = build_selected_item_market_chart(
            [_item("aapl")],
            selected_item_id="aapl",
            basis_date=date(2026, 7, 18),
            loader=broken_loader,
        )

        self.assertEqual(result["status"], "ERROR")
        self.assertIn("database unavailable", result["reason"])


if __name__ == "__main__":
    unittest.main()
