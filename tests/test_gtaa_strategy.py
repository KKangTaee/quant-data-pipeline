from __future__ import annotations

import sys
import unittest
from typing import Any

import pandas as pd


def _gtaa_price_df(
    *,
    dates: pd.DatetimeIndex,
    closes: list[float],
    scores: list[float],
    ma_values: list[float] | None = None,
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": dates,
            "Close": closes,
            "Avg Score": scores,
            "MA200": ma_values or [1.0] * len(dates),
        }
    )


class _FakeDisplayFrame:
    def __init__(self, result: pd.DataFrame) -> None:
        self.result = result

    def round_columns(self, *args: Any, **kwargs: Any) -> "_FakeDisplayFrame":
        return self


class _FakeGtaaEngine:
    def __init__(self) -> None:
        dates = pd.date_range("2020-01-31", periods=7, freq="ME")
        self.dfs = {
            "SPY": pd.DataFrame({"Date": dates, "Close": range(100, 107)}),
            "TLT": pd.DataFrame({"Date": dates, "Close": range(80, 87)}),
        }
        self.calls: list[tuple[str, Any]] = []

    def add_ma(self, window: int) -> "_FakeGtaaEngine":
        self.calls.append(("add_ma", window))
        for df in self.dfs.values():
            df[f"MA{window}"] = 1.0
        return self

    def filter_by_period(self) -> "_FakeGtaaEngine":
        self.calls.append(("filter_by_period", None))
        return self

    def add_interval_returns(self, intervals: list[int]) -> "_FakeGtaaEngine":
        self.calls.append(("add_interval_returns", list(intervals)))
        for months in intervals:
            for df in self.dfs.values():
                df[f"{months}MReturn"] = 0.01
        return self

    def align_dates(self) -> "_FakeGtaaEngine":
        self.calls.append(("align_dates", None))
        return self

    def slice(self, start: str | None = None, end: str | None = None) -> "_FakeGtaaEngine":
        self.calls.append(("slice", (start, end)))
        return self

    def add_avg_score(self, return_cols: tuple[str, ...], weights: dict[str, float]) -> "_FakeGtaaEngine":
        self.calls.append(("add_avg_score", (tuple(return_cols), dict(weights))))
        for df in self.dfs.values():
            df["Avg Score"] = 1.0
        return self

    def drop_columns(self, cols: list[str]) -> "_FakeGtaaEngine":
        self.calls.append(("drop_columns", list(cols)))
        return self

    def interval(self, interval: int) -> "_FakeGtaaEngine":
        self.calls.append(("interval", interval))
        return self

    def run(self, strategy: Any) -> _FakeDisplayFrame:
        self.calls.append(("run_rebalance_interval", strategy.rebalance_interval))
        return _FakeDisplayFrame(
            pd.DataFrame(
                [
                    {"Date": "2020-01-31", "Total Balance": 10000.0, "Total Return": 0.0},
                    {"Date": "2020-02-29", "Total Balance": 10100.0, "Total Return": 0.01},
                ]
            )
        )


class GtaaStrategyCadenceTests(unittest.TestCase):
    def test_latest_common_row_can_extend_month_end_rows_to_current_available_trade_date(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance.transform import append_latest_common_row

        month_end_dates = pd.to_datetime(["2020-01-31", "2020-02-28"])
        full_dates_a = pd.to_datetime(["2020-01-31", "2020-02-28", "2020-03-16", "2020-03-20"])
        full_dates_b = pd.to_datetime(["2020-01-31", "2020-02-28", "2020-03-16"])
        period_dfs = {
            "AAA": pd.DataFrame({"Date": month_end_dates, "Close": [100.0, 110.0], "MA200": [90.0, 95.0]}),
            "BBB": pd.DataFrame({"Date": month_end_dates, "Close": [80.0, 84.0], "MA200": [70.0, 72.0]}),
        }
        full_dfs = {
            "AAA": pd.DataFrame({"Date": full_dates_a, "Close": [100.0, 110.0, 115.0, 117.0], "MA200": [90.0, 95.0, 97.0, 98.0]}),
            "BBB": pd.DataFrame({"Date": full_dates_b, "Close": [80.0, 84.0, 87.0], "MA200": [70.0, 72.0, 73.0]}),
        }

        result = append_latest_common_row(period_dfs, full_dfs, end="2020-03-31")

        self.assertEqual(result["AAA"]["Date"].dt.strftime("%Y-%m-%d").tolist(), [
            "2020-01-31",
            "2020-02-28",
            "2020-03-16",
        ])
        self.assertEqual(result["BBB"]["Date"].dt.strftime("%Y-%m-%d").tolist(), [
            "2020-01-31",
            "2020-02-28",
            "2020-03-16",
        ])
        self.assertNotIn("streamlit", sys.modules)

    def test_get_gtaa_from_db_keeps_monthly_rows_for_strategy_owned_rebalance_cadence(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance import sample

        engine = _FakeGtaaEngine()
        original_builder = sample._build_price_only_engine
        try:
            sample._build_price_only_engine = lambda *args, **kwargs: engine  # type: ignore[method-assign]
            sample.get_gtaa3_from_db(
                tickers=["SPY", "TLT"],
                start="2020-01-31",
                end="2020-07-31",
                interval=4,
                score_lookback_months=[1],
                trend_filter_window=200,
            )
        finally:
            sample._build_price_only_engine = original_builder  # type: ignore[method-assign]

        self.assertNotIn(("interval", 4), engine.calls)
        self.assertIn(("run_rebalance_interval", 4), engine.calls)
        self.assertNotIn("streamlit", sys.modules)

    def test_gtaa_rebalance_interval_keeps_monthly_signal_rows_but_holds_positions_between_rebalances(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance.strategy import gtaa3

        dates = pd.date_range("2020-01-31", periods=5, freq="ME")
        dfs = {
            "AAA": _gtaa_price_df(
                dates=dates,
                closes=[100.0, 110.0, 120.0, 130.0, 140.0],
                scores=[0.90, 0.10, 0.10, 0.10, 0.10],
            ),
            "BBB": _gtaa_price_df(
                dates=dates,
                closes=[100.0, 90.0, 100.0, 110.0, 120.0],
                scores=[0.20, 0.95, 0.95, 0.95, 0.20],
            ),
            "CCC": _gtaa_price_df(
                dates=dates,
                closes=[100.0, 100.0, 100.0, 100.0, 200.0],
                scores=[0.10, 0.20, 0.20, 0.20, 0.99],
            ),
        }

        result = gtaa3(
            dfs,
            start_balance=1000,
            top=1,
            filter_ma="MA200",
            score_col="Avg Score",
            rebalance_interval=3,
        )

        self.assertEqual([date.strftime("%Y-%m-%d") for date in result["Date"]], [
            "2020-01-31",
            "2020-02-29",
            "2020-03-31",
            "2020-04-30",
            "2020-05-31",
        ])
        self.assertEqual(result["Rebalancing"].tolist(), [True, False, False, True, False])
        self.assertEqual(result["Raw Selected Ticker"].tolist(), [["AAA"], ["BBB"], ["BBB"], ["BBB"], ["CCC"]])
        self.assertEqual(result["Signal Investable Ticker"].tolist(), [["AAA"], ["BBB"], ["BBB"], ["BBB"], ["CCC"]])
        self.assertEqual(result["Next Ticker"].tolist(), [["AAA"], ["AAA"], ["AAA"], ["BBB"], ["BBB"]])
        self.assertAlmostEqual(float(result.iloc[-1]["Total Balance"]), 1418.1818181818182)
        self.assertNotIn("streamlit", sys.modules)


if __name__ == "__main__":
    unittest.main()
