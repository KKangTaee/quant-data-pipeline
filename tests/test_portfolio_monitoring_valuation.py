from __future__ import annotations

import importlib
import unittest
from datetime import date
from decimal import Decimal

import pandas as pd

from app.services.portfolio_monitoring.persistence import MonitoringItemRecord
from app.services.portfolio_monitoring.persistence import PositionEventRecord


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
        effective_start_date=date(2026, 7, 1),
        instrument_kind="stock",
        source_ref="AAPL",
    ):
        return MonitoringItemRecord(
            monitoring_item_id="item-aapl",
            portfolio_group_id="group-core",
            source_type="direct_security",
            source_ref=source_ref,
            instrument_kind=instrument_kind,
            requested_start_date=effective_start_date,
            effective_start_date=effective_start_date,
            funding_mode=funding_mode,
            input_notional=input_notional,
            input_shares=input_shares,
            entry_close=entry_close,
            initial_capital=initial_capital,
        )

    def _event(
        self,
        *,
        event_id,
        root_id,
        order,
        effect,
        day,
        quantity,
        price=None,
        fee="0",
        requested_start_date=None,
        effective_start_date=None,
        reference_close=None,
    ):
        return PositionEventRecord(
            position_event_id=event_id,
            root_event_id=root_id,
            supersedes_event_id=None,
            monitoring_item_id="item-aapl",
            event_order=order,
            event_action="create",
            position_effect=effect,
            trade_date=date.fromisoformat(day),
            quantity=quantity,
            execution_price=Decimal(price) if price is not None else None,
            reference_close=(
                Decimal(reference_close)
                if reference_close is not None
                else (Decimal(price) if price is not None else None)
            ),
            execution_price_source=(
                "db_close_default" if price is not None else None
            ),
            fee_usd=Decimal(fee),
            note="",
            command_id=f"command-{event_id}",
            requested_start_date=requested_start_date,
            effective_start_date=effective_start_date,
        )

    def test_no_event_lane_is_identical_for_implicit_and_explicit_empty_ledger(self) -> None:
        valuation = _load_valuation()
        item = self._item(
            input_shares=30,
            entry_close=Decimal("100"),
            initial_capital=Decimal("3000"),
        )
        frame = _history(
            [
                {"date": "2026-07-01", "close": 100, "adj_close": 100},
                {"date": "2026-07-02", "close": 110, "adj_close": 110},
            ]
        )

        implicit = valuation.build_direct_security_value_lane(item, frame)
        explicit = valuation.build_direct_security_value_lane(
            item, frame, position_events=[]
        )

        pd.testing.assert_frame_equal(implicit.curve, explicit.curve)
        self.assertEqual(implicit.initial_capital, explicit.initial_capital)

    def test_initial_quantity_correction_recomputes_from_original_entry_close(self) -> None:
        valuation = _load_valuation()
        item = self._item(
            input_shares=30,
            entry_close=Decimal("100"),
            initial_capital=Decimal("3000"),
        )
        frame = _history(
            [
                {"date": "2026-07-01", "close": 100, "adj_close": 100},
                {"date": "2026-07-02", "close": 110, "adj_close": 110},
            ]
        )

        lane = valuation.build_direct_security_value_lane(
            item,
            frame,
            position_events=[
                self._event(
                    event_id="correct-v1",
                    root_id="correct-root",
                    order=1,
                    effect="initial_quantity_correction",
                    day="2026-07-01",
                    quantity=20,
                )
            ],
        )

        self.assertEqual(lane.initial_capital, Decimal("2000"))
        self.assertEqual(lane.position.current_shares, Decimal("20"))
        self.assertEqual(
            Decimal(str(lane.curve.iloc[-1]["total_value"])),
            Decimal("2200.0"),
        )

    def test_initial_setting_correction_restarts_lane_from_resolved_contract(self) -> None:
        valuation = _load_valuation()
        item = self._item(
            input_shares=30,
            entry_close=Decimal("100"),
            initial_capital=Decimal("3000"),
            effective_start_date=date(2026, 7, 1),
        )
        frame = _history(
            [
                {"date": "2026-06-29", "close": 95, "adj_close": 95},
                {"date": "2026-06-30", "close": 97, "adj_close": 97},
                {"date": "2026-07-01", "close": 100, "adj_close": 100},
            ]
        )

        lane = valuation.build_direct_security_value_lane(
            item,
            frame,
            position_events=[
                self._event(
                    event_id="correct-v1",
                    root_id="correct-root",
                    order=1,
                    effect="initial_quantity_correction",
                    day="2026-06-29",
                    quantity=40,
                    requested_start_date=date(2026, 6, 28),
                    effective_start_date=date(2026, 6, 29),
                    reference_close="95",
                )
            ],
        )

        self.assertEqual(lane.effective_start_date, date(2026, 6, 29))
        self.assertEqual(lane.initial_capital, Decimal("3800"))
        self.assertEqual(lane.curve.iloc[0]["date"].date(), date(2026, 6, 29))
        self.assertEqual(lane.position.requested_start_date, date(2026, 6, 28))
        self.assertEqual(lane.position.effective_start_date, date(2026, 6, 29))
        self.assertEqual(lane.position.entry_close, Decimal("95"))
        self.assertEqual(lane.position.initial_capital, Decimal("3800"))

    def test_buy_and_partial_sell_adjust_cashflow_without_counting_flows_as_profit(self) -> None:
        valuation = _load_valuation()
        item = self._item()
        frame = _history(
            [
                {"date": "2026-07-01", "close": 100, "adj_close": 100},
                {"date": "2026-07-02", "close": 100, "adj_close": 100},
                {"date": "2026-07-03", "close": 100, "adj_close": 100},
            ]
        )

        lane = valuation.build_direct_security_value_lane(
            item,
            frame,
            position_events=[
                self._event(
                    event_id="buy-v1", root_id="buy-root", order=1,
                    effect="buy", day="2026-07-02", quantity=5,
                    price="100", fee="1",
                ),
                self._event(
                    event_id="sell-v1", root_id="sell-root", order=2,
                    effect="sell", day="2026-07-03", quantity=3,
                    price="100", fee="1",
                ),
            ],
        )

        self.assertEqual(lane.position.current_shares, Decimal("12"))
        self.assertEqual(
            lane.position.cumulative_contributions, Decimal("1501")
        )
        self.assertEqual(
            lane.position.cumulative_withdrawals, Decimal("299")
        )
        self.assertEqual(lane.position.pnl, Decimal("-2"))
        self.assertLess(
            Decimal(str(lane.curve.iloc[-1]["flow_adjusted_index"])),
            Decimal("1"),
        )

    def test_daily_modified_dietz_uses_half_day_flow_weight(self) -> None:
        valuation = _load_valuation()

        result = valuation.modified_dietz_return(
            begin_value=Decimal("3000"),
            end_value=Decimal("4100"),
            net_external_flow=Decimal("1000"),
        )

        self.assertEqual(
            result.quantize(Decimal("0.000001")), Decimal("0.028571")
        )

    def test_split_precedes_same_day_trade_and_dividend_uses_post_trade_units(self) -> None:
        valuation = _load_valuation()
        item = self._item(
            input_shares=30,
            entry_close=Decimal("50"),
            initial_capital=Decimal("1500"),
            effective_start_date=date(2026, 7, 14),
        )
        frame = _history(
            [
                {
                    "date": "2026-07-14", "close": 50, "adj_close": 25,
                    "stock_splits": 0, "dividends": 0,
                },
                {
                    "date": "2026-07-15", "close": 25, "adj_close": 25,
                    "stock_splits": 2, "dividends": 1,
                },
            ]
        )

        lane = valuation.build_direct_security_value_lane(
            item,
            frame,
            position_events=[
                self._event(
                    event_id="sell-v1", root_id="sell-root", order=1,
                    effect="sell", day="2026-07-15", quantity=50,
                    price="25",
                )
            ],
        )

        self.assertEqual(lane.position.current_shares, Decimal("10"))
        self.assertEqual(
            Decimal(str(lane.curve.iloc[-1]["dividend_cash"])),
            Decimal("10.0"),
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

    def test_etf_fixed_shares_supports_split_dividend_buy_and_sell(self) -> None:
        valuation = _load_valuation()
        item = self._item(
            instrument_kind="etf",
            source_ref="QQQ",
            input_shares=4,
            entry_close=Decimal("100"),
            initial_capital=Decimal("400"),
        )
        history = _history(
            [
                {
                    "date": "2026-07-01",
                    "close": 100,
                    "adj_close": 50,
                    "stock_splits": 0,
                    "dividends": 0,
                },
                {
                    "date": "2026-07-02",
                    "close": 50,
                    "adj_close": 50,
                    "stock_splits": 2,
                    "dividends": 0,
                },
                {
                    "date": "2026-07-03",
                    "close": 51,
                    "adj_close": 51,
                    "stock_splits": 0,
                    "dividends": 1,
                },
            ]
        )

        lane = valuation.build_direct_security_value_lane(
            item,
            history,
            position_events=[
                self._event(
                    event_id="buy-v1",
                    root_id="buy-root",
                    order=1,
                    effect="buy",
                    day="2026-07-02",
                    quantity=1,
                    price="50",
                    fee="1",
                ),
                self._event(
                    event_id="sell-v1",
                    root_id="sell-root",
                    order=2,
                    effect="sell",
                    day="2026-07-03",
                    quantity=2,
                    price="51",
                    fee="1",
                ),
            ],
        )

        self.assertIsNotNone(lane.position)
        assert lane.position is not None
        self.assertEqual(lane.position.effective_initial_shares, Decimal("4"))
        self.assertEqual(lane.position.current_shares, Decimal("7"))
        self.assertEqual(lane.position.cumulative_contributions, Decimal("451"))
        self.assertEqual(lane.position.cumulative_withdrawals, Decimal("101"))
        self.assertEqual(
            Decimal(str(lane.curve.iloc[-1]["dividend_cash"])), Decimal("7.0")
        )

        fixed_notional = self._item(
            instrument_kind="etf",
            source_ref="QQQ",
            funding_mode="fixed_notional",
            input_notional=Decimal("400"),
            input_shares=None,
            initial_capital=Decimal("400"),
        )
        self.assertIsNone(
            valuation.build_direct_security_value_lane(
                fixed_notional, history
            ).position
        )

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
