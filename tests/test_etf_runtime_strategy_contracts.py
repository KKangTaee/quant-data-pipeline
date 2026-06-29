from __future__ import annotations

import sys
import unittest
from typing import Any
from unittest.mock import patch

import pandas as pd


def _price_df(
    dates: pd.DatetimeIndex,
    closes: list[float],
    *,
    ma_values: list[float] | None = None,
    lookback_scores: list[float] | None = None,
) -> pd.DataFrame:
    data: dict[str, Any] = {
        "Date": dates,
        "Close": closes,
        "MA200": ma_values or [1.0] * len(dates),
    }
    if lookback_scores is not None:
        data["12MReturn"] = lookback_scores
    return pd.DataFrame(data)


class EtfRuntimeStrategyContractTests(unittest.TestCase):
    def test_risk_parity_exposes_inverse_vol_and_cash_only_contract(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance.strategy import risk_parity_trend

        dates = pd.date_range("2020-01-31", periods=4, freq="ME")
        dfs = {
            "LOW": _price_df(dates, [100.0, 101.0, 102.0, 103.0]),
            "HIGH": _price_df(dates, [100.0, 120.0, 96.0, 130.0]),
            "REJECT": _price_df(dates, [100.0, 100.0, 100.0, 100.0], ma_values=[150.0] * 4),
        }

        result = risk_parity_trend(
            dfs,
            start_balance=9000.0,
            rebalance_interval=1,
            vol_window=2,
            filter_ma="MA200",
        )

        first_invested = result[result["Selected Count"] > 0].iloc[0]
        self.assertEqual(first_invested["Eligible Ticker"], ["LOW", "HIGH"])
        self.assertEqual(first_invested["Eligible Count"], 2)
        self.assertEqual(first_invested["Volatility Window"], 2)
        self.assertEqual(first_invested["Weighting Mode"], "inverse_vol")
        self.assertEqual(first_invested["Low Vol Overweight Ticker"], "LOW")
        self.assertGreater(first_invested["Next Weight"][0], first_invested["Next Weight"][1])
        self.assertAlmostEqual(sum(first_invested["Next Weight"]), 1.0)

        warmup = result.iloc[0]
        self.assertTrue(warmup["Cash Only State"])
        self.assertIn("insufficient_volatility_window", warmup["Cash Only Reason"])
        self.assertAlmostEqual(warmup["Cash Share"], 1.0)
        self.assertNotIn("streamlit", sys.modules)

    def test_dual_momentum_exposes_top_n_cash_proxy_and_whipsaw_contract(self) -> None:
        sys.modules.pop("streamlit", None)

        from finance.strategy import dual_momentum

        dates = pd.date_range("2020-01-31", periods=3, freq="ME")
        dfs = {
            "AAA": _price_df(
                dates,
                [100.0, 110.0, 120.0],
                ma_values=[90.0, 90.0, 90.0],
                lookback_scores=[0.30, 0.10, 0.50],
            ),
            "BBB": _price_df(
                dates,
                [100.0, 95.0, 90.0],
                ma_values=[120.0, 120.0, 120.0],
                lookback_scores=[0.20, 0.80, 0.40],
            ),
            "CCC": _price_df(
                dates,
                [100.0, 105.0, 107.0],
                ma_values=[80.0, 80.0, 80.0],
                lookback_scores=[0.10, 0.70, 0.30],
            ),
            "BIL": _price_df(
                dates,
                [50.0, 51.0, 52.0],
                ma_values=[40.0, 40.0, 40.0],
                lookback_scores=[0.0, 0.0, 0.0],
            ),
        }

        result = dual_momentum(
            dfs,
            start_balance=9000.0,
            top=2,
            lookback_col="12MReturn",
            filter_ma="MA200",
            rebalance_interval=1,
            cash_ticker="BIL",
        )

        second = result.iloc[1]
        self.assertEqual(second["Raw Selected Ticker"], ["BBB", "CCC"])
        self.assertEqual(second["Trend Rejected Ticker"], ["BBB"])
        self.assertEqual(second["Selected Count"], 1)
        self.assertEqual(second["Target Slot Count"], 2)
        self.assertEqual(second["Unfilled Slot Count"], 1)
        self.assertEqual(second["Cash Proxy Ticker"], "BIL")
        self.assertIn("trend_rejected_slot_retained_as_cash", second["Cash Reason"])
        self.assertGreater(second["Cash Proxy Return"], 0.0)
        self.assertEqual(second["Concentration Status"], "concentrated_top_n")

        third = result.iloc[2]
        self.assertTrue(third["Selection Changed"])
        self.assertIn("AAA", third["Added Ticker"])
        self.assertIn("CCC", third["Removed Ticker"])
        self.assertEqual(third["Whipsaw Status"], "selection_changed")
        self.assertNotIn("streamlit", sys.modules)

    def test_runtime_bundles_preserve_etf_strategy_contract_metadata(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.runtime import backtest as runtime_backtest

        risk_result = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Total Balance": 10000.0,
                    "Total Return": 0.0,
                    "Selected Count": 0,
                    "Eligible Count": 0,
                    "Cash Share": 1.0,
                    "Cash Only State": True,
                    "Cash Only Reason": ["insufficient_volatility_window"],
                    "Max Position Weight": 0.0,
                    "Low Vol Overweight Ticker": "",
                    "Guardrail Cash Only State": False,
                },
                {
                    "Date": "2020-02-29",
                    "Total Balance": 10100.0,
                    "Total Return": 0.01,
                    "Selected Count": 2,
                    "Eligible Count": 2,
                    "Cash Share": 0.0,
                    "Cash Only State": False,
                    "Cash Only Reason": [],
                    "Max Position Weight": 0.70,
                    "Low Vol Overweight Ticker": "LOW",
                    "Guardrail Cash Only State": False,
                },
            ]
        )
        dual_result = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Total Balance": 10000.0,
                    "Total Return": 0.0,
                    "Selected Count": 1,
                    "Target Slot Count": 2,
                    "Trend Rejected Count": 1,
                    "Unfilled Slot Count": 1,
                    "Cash Share": 0.5,
                    "Max Position Weight": 0.5,
                    "Concentration Status": "concentrated_top_n",
                    "Selection Changed": False,
                    "Whipsaw Status": "initial_selection",
                },
                {
                    "Date": "2020-02-29",
                    "Total Balance": 10100.0,
                    "Total Return": 0.01,
                    "Selected Count": 1,
                    "Target Slot Count": 2,
                    "Trend Rejected Count": 0,
                    "Unfilled Slot Count": 1,
                    "Cash Share": 0.5,
                    "Max Position Weight": 0.5,
                    "Concentration Status": "concentrated_top_n",
                    "Selection Changed": True,
                    "Whipsaw Status": "selection_changed",
                },
            ]
        )

        with (
            patch.object(runtime_backtest, "_preflight_price_strategy_data"),
            patch.object(runtime_backtest, "get_risk_parity_trend_from_db", return_value=risk_result),
            patch.object(runtime_backtest, "get_dual_momentum_from_db", return_value=dual_result),
            patch.object(runtime_backtest, "_apply_real_money_hardening", side_effect=lambda bundle, **kwargs: bundle),
        ):
            risk_bundle = runtime_backtest.run_risk_parity_trend_backtest_from_db(
                tickers=["LOW", "HIGH"],
                start="2020-01-31",
                end="2020-02-29",
                vol_window=6,
                benchmark_ticker="AOR",
            )
            dual_bundle = runtime_backtest.run_dual_momentum_backtest_from_db(
                tickers=["AAA", "BBB", "BIL"],
                start="2020-01-31",
                end="2020-02-29",
                top=2,
                benchmark_ticker="AOR",
            )

        self.assertEqual(risk_bundle["meta"]["risk_parity_trend_contract"]["volatility_window_months"], 6)
        self.assertEqual(risk_bundle["meta"]["risk_parity_inverse_vol_summary"]["max_eligible_count"], 2)
        self.assertEqual(risk_bundle["meta"]["risk_parity_inverse_vol_summary"]["cash_only_rebalances"], 1)
        self.assertEqual(risk_bundle["meta"]["risk_parity_inverse_vol_summary"]["low_vol_overweight_tickers"], ["LOW"])

        self.assertEqual(dual_bundle["meta"]["dual_momentum_contract"]["top_n"], 2)
        self.assertEqual(dual_bundle["meta"]["dual_momentum_contract"]["cash_proxy_ticker"], "BIL")
        self.assertEqual(dual_bundle["meta"]["dual_momentum_concentration_turnover"]["max_trend_rejected_count"], 1)
        self.assertEqual(dual_bundle["meta"]["dual_momentum_concentration_turnover"]["selection_change_events"], 1)
        self.assertEqual(dual_bundle["meta"]["dual_momentum_concentration_turnover"]["max_cash_share"], 0.5)
        self.assertNotIn("streamlit", sys.modules)

    def test_existing_selection_history_builder_accepts_etf_runtime_diagnostics(self) -> None:
        from app.web.backtest_common import SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS
        from app.web.backtest_result_display import _build_snapshot_selection_history

        self.assertIn("risk_parity_trend", SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS)
        self.assertIn("dual_momentum", SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS)

        result_df = pd.DataFrame(
            [
                {
                    "Date": "2020-01-31",
                    "Rebalancing": True,
                    "Selected Count": 0,
                    "Raw Selected Count": 0,
                    "Cash Only State": True,
                    "Cash Only Reason": ["insufficient_volatility_window"],
                    "Cash": 10000.0,
                    "Total Balance": 10000.0,
                    "Total Return": 0.0,
                    "Weighting Mode": "inverse_vol",
                    "Risk-Off Mode": "cash_only",
                    "Risk-Off Reason": [],
                },
                {
                    "Date": "2020-02-29",
                    "Rebalancing": True,
                    "Raw Selected Ticker": ["LOW", "HIGH"],
                    "Raw Selected Count": 2,
                    "Eligible Ticker": ["LOW", "HIGH"],
                    "Eligible Count": 2,
                    "Next Ticker": ["LOW", "HIGH"],
                    "Next Weight": [0.7, 0.3],
                    "Selected Count": 2,
                    "Cash": 0.0,
                    "Total Balance": 10100.0,
                    "Total Return": 0.01,
                    "Weighting Mode": "inverse_vol",
                    "Risk-Off Mode": "cash_only",
                    "Risk-Off Reason": [],
                    "Low Vol Overweight Ticker": "LOW",
                    "Whipsaw Status": "selection_unchanged",
                },
            ]
        )

        selection_df = _build_snapshot_selection_history(result_df)

        self.assertEqual(len(selection_df), 2)
        self.assertIn("Cash Only Reasons", selection_df.columns)
        self.assertIn("Eligible Tickers", selection_df.columns)
        self.assertIn("Low Vol Overweight Ticker", selection_df.columns)
        self.assertEqual(selection_df.iloc[0]["Weighting Contract"], "Inverse Volatility")
        self.assertIn("현금", selection_df.iloc[0]["Interpretation"])


if __name__ == "__main__":
    unittest.main()
