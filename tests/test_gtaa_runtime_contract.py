from __future__ import annotations

import sys
import unittest
from typing import Any
from unittest.mock import patch

import pandas as pd


class GtaaRuntimeContractTests(unittest.TestCase):
    def test_runtime_attaches_price_freshness_for_effective_trading_end(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.runtime import backtest as runtime_backtest
        from app.web.backtest_result_display import _build_data_trust_brief

        tickers = ["SPY", "EFA", "EEM", "AGG", "TLT", "LQD", "VNQ", "DBC", "GLD", "IEF", "QQQ", "SHY"]
        result_df = pd.DataFrame(
            [
                {"Date": "2026-06-30", "Total Balance": 10000.0, "Total Return": 0.0},
                {"Date": "2026-07-06", "Total Balance": 10100.0, "Total Return": 0.01},
            ]
        )
        freshness = {
            "status": "ok",
            "message": "All GTAA universe symbols are current through the effective trading end.",
            "details": {
                "requested_end": "2026-07-07",
                "effective_end_date": "2026-07-06",
                "requested_count": 12,
                "covered_count": 12,
                "common_latest_date": "2026-07-06",
                "max_latest_date": "2026-07-06",
                "spread_days": 0,
            },
        }
        captured_hardening_meta: dict[str, Any] = {}

        def _no_hardening(bundle: dict[str, Any], **kwargs: Any) -> dict[str, Any]:
            captured_hardening_meta["price_freshness_status"] = (
                bundle["meta"].get("price_freshness") or {}
            ).get("status")
            return bundle

        with (
            patch.object(runtime_backtest, "inspect_strict_annual_price_freshness", return_value=freshness),
            patch.object(runtime_backtest, "_preflight_price_strategy_data"),
            patch.object(runtime_backtest, "get_gtaa3_from_db", return_value=result_df),
            patch.object(runtime_backtest, "_apply_real_money_hardening", side_effect=_no_hardening),
        ):
            bundle = runtime_backtest.run_gtaa_backtest_from_db(
                tickers=tickers,
                start="2026-01-01",
                end="2026-07-07",
                timeframe="1d",
                option="month_end",
                top=3,
                interval=1,
                benchmark_ticker="SPY",
                underperformance_guardrail_enabled=False,
                drawdown_guardrail_enabled=False,
            )

        meta = bundle["meta"]
        brief = _build_data_trust_brief(meta)
        price_item = next(item for item in brief["summary_items"] if item["label"] == "가격 기준")
        next_check_item = next(item for item in brief["summary_items"] if item["label"] == "1차 데이터 확인")

        self.assertIn("price_freshness", meta)
        self.assertEqual(meta["price_freshness"], freshness)
        self.assertEqual(captured_hardening_meta["price_freshness_status"], "ok")
        self.assertEqual(meta["actual_result_end"], "2026-07-06")
        self.assertEqual(brief["status_label"], "자료 정상")
        self.assertEqual(price_item["value"], "최신성 정상")
        self.assertIn("2026-07-07", brief["subtitle"])
        self.assertIn("2026-07-06", brief["subtitle"])
        self.assertEqual(next_check_item["value"], "바로 성과 확인")


if __name__ == "__main__":
    unittest.main()
