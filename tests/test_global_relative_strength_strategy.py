from __future__ import annotations

import sys
import unittest
from typing import Any
from unittest.mock import patch

import pandas as pd


def _grs_price_df(
    *,
    dates: pd.DatetimeIndex,
    closes: list[float],
    scores: list[float],
    ma_values: list[float],
) -> pd.DataFrame:
    return pd.DataFrame(
        {
            "Date": dates,
            "Close": closes,
            "Avg Score": scores,
            "MA200": ma_values,
        }
    )


class _FakeDisplayFrame:
    def __init__(self, result: pd.DataFrame) -> None:
        self.result = result

    def round_columns(self, *args: Any, **kwargs: Any) -> "_FakeDisplayFrame":
        return self


class _FakeGrsEngine:
    def __init__(self) -> None:
        dates = pd.date_range("2020-01-31", periods=7, freq="ME")
        self.dfs = {
            "SPY": pd.DataFrame({"Date": dates, "Close": range(100, 107)}),
            "BIL": pd.DataFrame({"Date": dates, "Close": range(50, 57)}),
        }
        self.calls: list[tuple[str, Any]] = []

    def add_ma(self, windows: int) -> "_FakeGrsEngine":
        self.calls.append(("add_ma", windows))
        for df in self.dfs.values():
            df[f"MA{windows}"] = 1.0
        return self

    def filter_by_period(self) -> "_FakeGrsEngine":
        self.calls.append(("filter_by_period", None))
        return self

    def add_interval_returns(self, intervals: list[int]) -> "_FakeGrsEngine":
        self.calls.append(("add_interval_returns", list(intervals)))
        for months in intervals:
            for df in self.dfs.values():
                df[f"{months}MReturn"] = 0.01
        return self

    def align_dates(self) -> "_FakeGrsEngine":
        self.calls.append(("align_dates", None))
        return self

    def slice(self, start: str | None = None, end: str | None = None) -> "_FakeGrsEngine":
        self.calls.append(("slice", (start, end)))
        return self

    def add_avg_score(self, return_cols: tuple[str, ...], weights: dict[str, float]) -> "_FakeGrsEngine":
        self.calls.append(("add_avg_score", (tuple(return_cols), dict(weights))))
        for df in self.dfs.values():
            df["Avg Score"] = 1.0
        return self

    def drop_columns(self, cols: list[str]) -> "_FakeGrsEngine":
        self.calls.append(("drop_columns", list(cols)))
        return self

    def interval(self, interval: int) -> "_FakeGrsEngine":
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


class GlobalRelativeStrengthRuntimeContractTests(unittest.TestCase):
    def test_grs_latest_common_row_is_valuation_without_fake_rebalance(self) -> None:
        from finance.strategy import global_relative_strength_allocation
        from finance.transform import append_latest_common_row

        signal_date = pd.Timestamp("2026-05-29")
        latest_common = pd.Timestamp("2026-06-26")
        period_dfs = {
            "SPY": _grs_price_df(
                dates=pd.DatetimeIndex([signal_date, pd.Timestamp("2026-06-30")]),
                closes=[100.0, 110.0],
                scores=[0.5, 0.6],
                ma_values=[90.0, 90.0],
            ),
            "BIL": _grs_price_df(
                dates=pd.DatetimeIndex([signal_date, latest_common]),
                closes=[50.0, 51.0],
                scores=[0.0, 0.0],
                ma_values=[40.0, 40.0],
            ),
        }
        full_dfs = {
            "SPY": pd.concat(
                [
                    period_dfs["SPY"],
                    _grs_price_df(
                        dates=pd.DatetimeIndex([latest_common]),
                        closes=[108.0],
                        scores=[0.55],
                        ma_values=[90.0],
                    ),
                ],
                ignore_index=True,
            ),
            "BIL": period_dfs["BIL"].copy(),
        }

        enriched = append_latest_common_row(
            period_dfs,
            full_dfs,
            end="2026-07-10",
            row_kind_col="Row Kind",
        )
        common_dates = set(enriched["SPY"]["Date"]).intersection(enriched["BIL"]["Date"])
        aligned = {
            ticker: frame[frame["Date"].isin(common_dates)].sort_values("Date").reset_index(drop=True)
            for ticker, frame in enriched.items()
        }
        result = global_relative_strength_allocation(
            aligned,
            start_balance=10000.0,
            top=1,
            cash_ticker="BIL",
        )

        last = result.iloc[-1]
        self.assertEqual(pd.Timestamp(last["Date"]), latest_common)
        self.assertEqual(last["Row Kind"], "valuation")
        self.assertFalse(last["Rebalancing"])
        self.assertEqual(last["Next Ticker"], result.iloc[-2]["Next Ticker"])
        self.assertEqual(last["Raw Selected Ticker"], [])

    def test_get_global_relative_strength_keeps_raw_monthly_rows_for_strategy_cadence(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance import sample

        engine = _FakeGrsEngine()

        original_builder = sample._build_price_only_engine
        try:
            sample._build_price_only_engine = lambda *args, **kwargs: engine  # type: ignore[method-assign]
            sample.get_global_relative_strength_from_db(
                tickers=["SPY"],
                cash_ticker="BIL",
                start="2020-01-31",
                end="2020-07-31",
                interval=3,
                score_lookback_months=[1],
                trend_filter_window=200,
            )
        finally:
            sample._build_price_only_engine = original_builder  # type: ignore[method-assign]

        self.assertNotIn(("interval", 3), engine.calls)
        self.assertIn(("run_rebalance_interval", 3), engine.calls)
        self.assertNotIn("streamlit", sys.modules)

    def test_allocation_exposes_cash_proxy_and_top_n_concentration_contract(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance.strategy import global_relative_strength_allocation

        dates = pd.date_range("2020-01-31", periods=2, freq="ME")
        dfs = {
            "SPY": _grs_price_df(dates=dates, closes=[100.0, 110.0], scores=[0.50, 0.50], ma_values=[90.0, 90.0]),
            "GLD": _grs_price_df(dates=dates, closes=[90.0, 95.0], scores=[0.40, 0.40], ma_values=[100.0, 100.0]),
            "EFA": _grs_price_df(dates=dates, closes=[80.0, 84.0], scores=[0.30, 0.30], ma_values=[70.0, 70.0]),
            "TLT": _grs_price_df(dates=dates, closes=[70.0, 71.0], scores=[0.20, 0.20], ma_values=[60.0, 60.0]),
            "BIL": _grs_price_df(dates=dates, closes=[50.0, 51.0], scores=[0.0, 0.0], ma_values=[40.0, 40.0]),
        }

        result = global_relative_strength_allocation(
            dfs,
            start_balance=9000.0,
            top=3,
            score_col="Avg Score",
            filter_ma="MA200",
            rebalance_interval=3,
            cash_ticker="BIL",
        )

        first = result.iloc[0]
        second = result.iloc[1]

        self.assertEqual(first["Raw Selected Ticker"], ["SPY", "GLD", "EFA"])
        self.assertEqual(first["Raw Selected Count"], 3)
        self.assertEqual(first["Next Ticker"], ["SPY", "EFA"])
        self.assertEqual(first["Overlay Rejected Ticker"], ["GLD"])
        self.assertEqual(first["Overlay Rejected Count"], 1)
        self.assertTrue(first["Trend Filter Enabled"])
        self.assertEqual(first["Weighting Mode"], "equal_weight")
        self.assertEqual(first["Risk-Off Mode"], "cash_only")
        self.assertTrue(first["Partial Cash Retention Enabled"])
        self.assertTrue(first["Partial Cash Retention Active"])
        self.assertEqual(first["Selected Count"], 2)
        self.assertEqual(first["Target Slot Count"], 3)
        self.assertEqual(first["Trend Rejected Count"], 1)
        self.assertEqual(first["Unfilled Slot Count"], 1)
        self.assertAlmostEqual(first["Cash Share"], 1.0 / 3.0)
        self.assertAlmostEqual(first["Max Position Weight"], 1.0 / 3.0)
        self.assertEqual(first["Concentration Status"], "balanced_top_n")
        self.assertEqual(first["Cash Proxy Ticker"], "BIL")
        self.assertIn("trend_rejected_slot_retained_as_cash", first["Cash Reason"])
        self.assertAlmostEqual(second["Cash Proxy Return"], 0.02)
        self.assertNotIn("streamlit", sys.modules)

    def test_runtime_bundle_preserves_grs_strategy_contract_metadata(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.runtime import backtest as runtime_backtest
        from app.runtime.backtest.real_money import STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Total Balance": 10000.0,
                    "Total Return": 0.0,
                    "Selected Count": 1,
                    "Target Slot Count": 2,
                    "Unfilled Slot Count": 1,
                    "Cash Share": 0.5,
                    "Max Position Weight": 0.5,
                    "Concentration Status": "concentrated_top_n",
                },
                {
                    "Date": "2020-02-29",
                    "Total Balance": 10100.0,
                    "Total Return": 0.01,
                    "Selected Count": 2,
                    "Target Slot Count": 2,
                    "Unfilled Slot Count": 0,
                    "Cash Share": 0.0,
                    "Max Position Weight": 0.5,
                    "Concentration Status": "concentrated_top_n",
                },
            ]
        )
        result_df.attrs["effective_tickers"] = ["SPY", "GLD"]
        result_df.attrs["requested_tickers"] = ["SPY", "GLD", "DBC"]
        result_df.attrs["excluded_tickers"] = ["DBC"]
        result_df.attrs["malformed_price_rows"] = [{"ticker": "DBC", "count": 2}]

        def _no_hardening(bundle: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
            bundle["meta"]["captured_hardening_benchmark_contract"] = kwargs["benchmark_contract"]
            return bundle

        with (
            patch.object(
                runtime_backtest,
                "inspect_strict_annual_price_freshness",
                return_value={"status": "ok", "message": "", "details": {}},
            ),
            patch.object(runtime_backtest, "_preflight_price_strategy_data"),
            patch.object(runtime_backtest, "get_global_relative_strength_from_db", return_value=result_df),
            patch.object(runtime_backtest, "_apply_real_money_hardening", side_effect=_no_hardening),
        ):
            bundle = runtime_backtest.run_global_relative_strength_backtest_from_db(
                tickers=["SPY", "GLD", "DBC"],
                cash_ticker="BIL",
                start="2020-01-31",
                end="2020-02-29",
                timeframe="1d",
                option="month_end",
                top=2,
                interval=3,
                benchmark_ticker="AOR",
                benchmark_contract=STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
                score_lookback_months=[3, 6],
                score_return_columns=["3MReturn", "6MReturn"],
                score_weights={"3MReturn": 0.70, "6MReturn": 0.30},
                trend_filter_window=150,
                universe_mode="manual_tickers",
                preset_name="GRS test",
            )

        meta = bundle["meta"]
        self.assertIn("grs_period_contract", meta)
        self.assertEqual(meta["benchmark_contract"], STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT)
        self.assertEqual(meta["captured_hardening_benchmark_contract"], STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT)
        self.assertEqual(
            meta["grs_strategy_contract"],
            {
                "contract_version": "grs_strategy_contract_v1",
                "cash_proxy_ticker": "BIL",
                "benchmark_contract": STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT,
                "benchmark_ticker": "AOR",
                "top_n": 2,
                "rebalance_interval_months": 3,
                "trend_filter_window": 150,
                "score_lookback_months": [3, 6],
                "score_return_columns": ["3MReturn", "6MReturn"],
                "score_weights": {"3MReturn": 0.70, "6MReturn": 0.30},
                "cash_handling": "trend_rejected_slots_retained_in_cash_proxy",
            },
        )
        self.assertEqual(meta["grs_top_n_concentration"]["max_selected_count"], 2)
        self.assertEqual(meta["grs_top_n_concentration"]["max_cash_share"], 0.5)
        self.assertEqual(meta["excluded_tickers"], ["DBC"])
        self.assertNotIn("streamlit", sys.modules)

    def test_runtime_preflight_keeps_risky_exclusion_path_open(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.runtime import backtest as runtime_backtest

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Total Balance": 10000.0,
                    "Total Return": 0.0,
                    "Selected Count": 1,
                    "Target Slot Count": 2,
                    "Unfilled Slot Count": 1,
                    "Cash Share": 0.5,
                    "Max Position Weight": 0.5,
                    "Concentration Status": "concentrated_top_n",
                },
                {
                    "Date": "2020-02-29",
                    "Total Balance": 10100.0,
                    "Total Return": 0.01,
                    "Selected Count": 1,
                    "Target Slot Count": 2,
                    "Unfilled Slot Count": 1,
                    "Cash Share": 0.5,
                    "Max Position Weight": 0.5,
                    "Concentration Status": "concentrated_top_n",
                },
            ]
        )
        result_df.attrs["effective_tickers"] = ["SPY"]
        result_df.attrs["requested_tickers"] = ["SPY", "DBC"]
        result_df.attrs["excluded_tickers"] = ["DBC"]

        preflight_calls: list[list[str]] = []

        def _preflight_without_missing_risky(*, tickers: list[str], **kwargs: Any) -> None:
            preflight_calls.append(list(tickers))
            if "DBC" in tickers:
                raise runtime_backtest.BacktestDataError("DBC should be handled by the GRS exclusion path")

        with (
            patch.object(
                runtime_backtest,
                "inspect_strict_annual_price_freshness",
                return_value={
                    "status": "warning",
                    "message": "1 Global Relative Strength universe symbols have no DB price rows.",
                    "details": {"missing_symbols": ["DBC"]},
                },
            ),
            patch.object(runtime_backtest, "_preflight_price_strategy_data", side_effect=_preflight_without_missing_risky),
            patch.object(runtime_backtest, "get_global_relative_strength_from_db", return_value=result_df),
            patch.object(runtime_backtest, "_apply_real_money_hardening", side_effect=lambda bundle, **kwargs: bundle),
        ):
            bundle = runtime_backtest.run_global_relative_strength_backtest_from_db(
                tickers=["SPY", "DBC"],
                cash_ticker="BIL",
                start="2020-01-31",
                end="2020-02-29",
                timeframe="1d",
                option="month_end",
                top=2,
                interval=1,
                benchmark_ticker="AOR",
            )

        self.assertNotIn(["SPY", "DBC", "BIL"], preflight_calls)
        self.assertIn(["BIL"], preflight_calls)
        self.assertIn(["AOR"], preflight_calls)
        self.assertEqual(bundle["meta"]["excluded_tickers"], ["DBC"])
        self.assertIn("가격 최신성 점검", " ".join(bundle["meta"]["warnings"]))
        self.assertNotIn("streamlit", sys.modules)


if __name__ == "__main__":
    unittest.main()
