from __future__ import annotations

import unittest
from unittest.mock import patch
from pathlib import Path

import pandas as pd


def _sep_rows() -> pd.DataFrame:
    rows = []
    values = {
        "central_tendency_lower": (1.5, 2.0),
        "median": (2.0, 2.2),
        "central_tendency_upper": (2.5, 2.4),
    }
    for statistic, (gdp, pce) in values.items():
        rows.extend(
            [
                {"target_year": 2027, "variable_name": "real_gdp", "statistic_name": statistic, "value_pct": gdp, "release_date": "2026-06-15"},
                {"target_year": 2027, "variable_name": "pce_inflation", "statistic_name": statistic, "value_pct": pce, "release_date": "2026-06-15"},
            ]
        )
    return pd.DataFrame(rows)


class MarketContextValuationTests(unittest.TestCase):
    def test_nasdaq_model_preserves_coverage_block_evidence(self) -> None:
        from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model

        model = build_nasdaq100_valuation_read_model(
            monthly_rows=[{"observation_month": "2026-07-01", "qqq_price": 709.43, "trailing_pe": None,
                           "reconstructed_ttm_eps": None, "coverage_weight_pct": 94.47,
                           "unmapped_weight_pct": 5.53, "data_quality": "blocked",
                           "error_msg": "INSUFFICIENT_EARNINGS_COVERAGE"}],
            ttm_evidence={"status": "BLOCKED", "coverage_weight_pct": 94.47,
                          "unmapped_weight_pct": 5.53, "error_code": "INSUFFICIENT_EARNINGS_COVERAGE"},
            sep_rows=_sep_rows(), sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 709.43}],
        )

        self.assertEqual(model["status"], "BLOCKED")
        self.assertEqual(model["coverage"]["coverage_weight_pct"], 94.47)
        self.assertEqual(model["instrument"]["proxy_symbol"], "QQQ")
        self.assertEqual(model["earnings_scenario"]["status"], "BLOCKED")

    def test_nasdaq_model_ready_contract_uses_sixty_complete_months(self) -> None:
        from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model

        rows = [
            {"observation_month": date, "qqq_price": 500.0 + index,
             "reconstructed_ttm_eps": 20.0, "trailing_pe": 20.0 + index / 20,
             "coverage_weight_pct": 97.0, "unmapped_weight_pct": 3.0,
             "data_quality": "reconstructed_actual"}
            for index, date in enumerate(pd.date_range("2021-08-01", periods=60, freq="MS"))
        ]
        model = build_nasdaq100_valuation_read_model(
            monthly_rows=rows,
            ttm_evidence={"status": "READY", "current_ttm_eps": 20.0,
                          "coverage_weight_pct": 97.0, "unmapped_weight_pct": 3.0,
                          "eps_source_quality": "reconstructed_actual"},
            sep_rows=_sep_rows(), sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 700.0}],
        )

        self.assertEqual(model["multiple_regime"]["status"], "READY")
        self.assertEqual(model["multiple_regime"]["observation_count"], 60)
        self.assertIn("price_scenarios", model["index_scenario"])

    def test_combined_model_isolates_one_instrument_failure(self) -> None:
        from app.services.overview.market_context_valuation import build_market_context_valuation_read_model

        with patch("app.services.overview.market_context_valuation.build_sp500_valuation_read_model", return_value={"status": "READY"}), \
             patch("app.services.overview.market_context_valuation.build_nasdaq100_valuation_read_model", side_effect=RuntimeError("db unavailable")):
            model = build_market_context_valuation_read_model()

        self.assertEqual(model["instruments"]["sp500"]["status"], "READY")
        self.assertEqual(model["instruments"]["nasdaq100"]["status"], "ERROR")

    def test_react_surface_has_instrument_selector_and_coverage_block(self) -> None:
        component = Path("app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx").read_text()
        helper = Path("app/web/overview/market_context_helpers.py").read_text()

        for token in ("instrument-selector", "Nasdaq-100", "coverage-block", "minimum_required_pct"):
            self.assertIn(token, component)
        self.assertIn("build_market_context_valuation_read_model", helper)


if __name__ == "__main__":
    unittest.main()
