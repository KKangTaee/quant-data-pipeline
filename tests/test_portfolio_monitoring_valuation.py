from __future__ import annotations

import importlib
import unittest
from datetime import date
from decimal import Decimal

import pandas as pd

from app.services.portfolio_monitoring.persistence import MonitoringItemRecord


def _load_valuation():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.valuation")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring valuation module is required") from exc


def _history(rows):
    return pd.DataFrame(rows)


class PortfolioMonitoringDirectValuationTests(unittest.TestCase):
    def _item(
        self,
        *,
        funding_mode="fixed_shares",
        input_notional=None,
        input_shares=10,
        entry_close=Decimal("100"),
        initial_capital=Decimal("1000"),
    ):
        return MonitoringItemRecord(
            monitoring_item_id="item-aapl",
            portfolio_group_id="group-core",
            source_type="direct_security",
            source_ref="AAPL",
            instrument_kind="stock",
            requested_start_date=date(2026, 7, 1),
            effective_start_date=date(2026, 7, 1),
            funding_mode=funding_mode,
            input_notional=input_notional,
            input_shares=input_shares,
            entry_close=entry_close,
            initial_capital=initial_capital,
        )

    def test_weekend_start_resolves_to_later_first_usable_session(self) -> None:
        valuation = _load_valuation()
        history = _history(
            [
                {"date": "2026-07-03", "close": 99.0, "adj_close": 99.0},
                {"date": "2026-07-06", "close": 100.0, "adj_close": 100.0},
                {"date": "2026-07-07", "close": 101.0, "adj_close": 101.0},
            ]
        )

        entry = valuation.resolve_direct_security_entry(
            history,
            date(2026, 7, 4),
            "fixed_notional",
            Decimal("10000"),
        )

        self.assertEqual(entry.effective_start_date, date(2026, 7, 6))
        self.assertEqual(entry.entry_close, Decimal("100.0"))
        self.assertEqual(entry.initial_capital, Decimal("10000"))
        self.assertEqual(entry.metadata["virtual_units"], "1.0E+2")

    def test_entry_resolution_blocks_missing_or_zero_later_price(self) -> None:
        valuation = _load_valuation()
        history = _history(
            [
                {"date": "2026-07-03", "close": 99.0, "adj_close": 99.0},
                {"date": "2026-07-06", "close": 0.0, "adj_close": 0.0},
            ]
        )

        with self.assertRaisesRegex(valuation.EntryPriceUnavailableError, "No usable close"):
            valuation.resolve_direct_security_entry(
                history,
                date(2026, 7, 4),
                "fixed_notional",
                Decimal("10000"),
            )

    def test_fixed_notional_uses_fractional_units_and_fixed_shares_use_integer_count(self) -> None:
        valuation = _load_valuation()
        history = _history(
            [{"date": "2026-07-01", "close": 333.0, "adj_close": 333.0}]
        )

        notional = valuation.resolve_direct_security_entry(
            history,
            date(2026, 7, 1),
            "fixed_notional",
            Decimal("10000"),
        )
        shares = valuation.resolve_direct_security_entry(
            history,
            date(2026, 7, 1),
            "fixed_shares",
            7,
        )

        self.assertEqual(
            Decimal(notional.metadata["virtual_units"]),
            Decimal("10000") / Decimal("333.0"),
        )
        self.assertEqual(shares.metadata["virtual_units"], "7")
        self.assertEqual(shares.initial_capital, Decimal("2331.0"))

    def test_split_adjusts_units_and_dividend_accumulates_as_cash_without_reinvestment(self) -> None:
        valuation = _load_valuation()
        history = _history(
            [
                {
                    "date": "2026-07-01",
                    "close": 100.0,
                    "adj_close": 50.0,
                    "dividends": 0.0,
                    "stock_splits": 0.0,
                },
                {
                    "date": "2026-07-02",
                    "close": 52.0,
                    "adj_close": 52.0,
                    "dividends": 0.0,
                    "stock_splits": 2.0,
                },
                {
                    "date": "2026-07-03",
                    "close": 53.0,
                    "adj_close": 54.0,
                    "dividends": 1.0,
                    "stock_splits": 0.0,
                },
            ]
        )

        lane = valuation.build_direct_security_value_lane(self._item(), history)
        curve = lane.curve.set_index("date")

        self.assertEqual(curve.loc[pd.Timestamp("2026-07-01"), "effective_units"], 10.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-02"), "effective_units"], 20.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-02"), "total_value"], 1040.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-03"), "dividend_cash"], 20.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-03"), "market_value"], 1060.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-03"), "total_value"], 1080.0)
        self.assertEqual(curve.loc[pd.Timestamp("2026-07-03"), "effective_units"], 20.0)

    def test_adjusted_close_cross_check_uses_strict_review_tolerances(self) -> None:
        valuation = _load_valuation()
        at_end_threshold = valuation.assess_corporate_action_consistency(
            [1.0, 1.005],
            [1.0, 1.0],
        )
        above_end_threshold = valuation.assess_corporate_action_consistency(
            [1.0, 1.0051],
            [1.0, 1.0],
        )
        at_session_threshold = valuation.assess_corporate_action_consistency(
            [1.0, 1.01, 1.0],
            [1.0, 1.0, 1.0],
        )
        above_session_threshold = valuation.assess_corporate_action_consistency(
            [1.0, 1.0101, 1.0],
            [1.0, 1.0, 1.0],
        )

        self.assertEqual(at_end_threshold.status, "READY")
        self.assertEqual(at_session_threshold.status, "READY")
        self.assertEqual(above_end_threshold.status, "DATA_REVIEW")
        self.assertEqual(above_session_threshold.status, "DATA_REVIEW")

    def test_lane_marks_data_review_without_replacing_raw_ledger_value(self) -> None:
        valuation = _load_valuation()
        history = _history(
            [
                {"date": "2026-07-01", "close": 100.0, "adj_close": 100.0, "dividends": 0.0, "stock_splits": 0.0},
                {"date": "2026-07-02", "close": 105.0, "adj_close": 120.0, "dividends": 0.0, "stock_splits": 0.0},
            ]
        )

        lane = valuation.build_direct_security_value_lane(self._item(), history)

        self.assertEqual(lane.status, "data_review")
        self.assertEqual(lane.curve.iloc[-1]["total_value"], 1050.0)
        self.assertEqual(lane.curve.iloc[-1]["adjusted_value"], 1200.0)
        self.assertTrue(lane.review.reasons)

    def test_tracking_end_uses_latest_value_available_on_or_before_weekend_request(self) -> None:
        valuation = _load_valuation()
        lane = valuation.ItemValueLane(
            monitoring_item_id="item-aapl",
            source_ref="AAPL",
            effective_start_date=date(2026, 7, 1),
            latest_usable_date=date(2026, 7, 17),
            initial_capital=Decimal("1000"),
            status="active",
            curve=pd.DataFrame(
                [
                    {"date": "2026-07-16", "total_value": 1020.0},
                    {"date": "2026-07-17", "total_value": 1030.0},
                ]
            ),
            review=valuation.CorporateActionReview(
                "READY", Decimal("0"), Decimal("0"), ()
            ),
        )

        resolution = valuation.resolve_tracking_end(lane, date(2026, 7, 19))

        self.assertEqual(resolution.requested_end_date, date(2026, 7, 19))
        self.assertEqual(resolution.effective_end_date, date(2026, 7, 17))
        self.assertEqual(resolution.exit_value, Decimal("1030.0"))

    def test_tracking_end_rejects_lane_without_value_on_or_before_request(self) -> None:
        valuation = _load_valuation()
        lane = valuation.ItemValueLane(
            monitoring_item_id="item-aapl",
            source_ref="AAPL",
            effective_start_date=date(2026, 7, 6),
            latest_usable_date=date(2026, 7, 6),
            initial_capital=Decimal("1000"),
            status="active",
            curve=pd.DataFrame(
                [{"date": "2026-07-06", "total_value": 1000.0}]
            ),
            review=valuation.CorporateActionReview(
                "READY", Decimal("0"), Decimal("0"), ()
            ),
        )

        with self.assertRaisesRegex(
            valuation.TrackingEndValueUnavailableError,
            "종료일 이전",
        ):
            valuation.resolve_tracking_end(lane, date(2026, 7, 5))


if __name__ == "__main__":
    unittest.main()
