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

    def test_nasdaq_repair_action_is_exposed_only_while_blocked(self) -> None:
        from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model

        blocked = build_nasdaq100_valuation_read_model(
            monthly_rows=[
                {
                    "observation_month": "2026-07-01",
                    "qqq_price": 709.43,
                    "coverage_weight_pct": 94.47,
                    "unmapped_weight_pct": 5.53,
                    "data_quality": "blocked",
                    "error_msg": "INSUFFICIENT_EARNINGS_COVERAGE",
                }
            ],
            ttm_evidence={
                "status": "BLOCKED",
                "coverage_weight_pct": 94.47,
                "unmapped_weight_pct": 5.53,
                "error_code": "INSUFFICIENT_EARNINGS_COVERAGE",
            },
            sep_rows=_sep_rows(),
            sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 709.43}],
        )
        ready_rows = [
            {
                "observation_month": date,
                "qqq_price": 500.0 + index,
                "reconstructed_ttm_eps": 20.0,
                "trailing_pe": 20.0 + index / 20,
                "coverage_weight_pct": 97.0,
                "unmapped_weight_pct": 3.0,
                "data_quality": "reconstructed_actual",
            }
            for index, date in enumerate(pd.date_range("2021-08-01", periods=60, freq="MS"))
        ]
        ready = build_nasdaq100_valuation_read_model(
            monthly_rows=ready_rows,
            ttm_evidence={
                "status": "READY",
                "current_ttm_eps": 20.0,
                "coverage_weight_pct": 97.0,
                "unmapped_weight_pct": 3.0,
                "eps_source_quality": "reconstructed_actual",
            },
            sep_rows=_sep_rows(),
            sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 700.0}],
        )

        self.assertEqual(
            blocked["coverage"]["repair_action"],
            {
                "id": "repair_nasdaq100_60m",
                "label": "60개월 가치평가 자료 보강",
                "detail": "누락된 구성 종목 EPS와 가격 이력을 보강한 뒤 다시 계산합니다.",
                "enabled": True,
            },
        )
        self.assertNotIn("repair_action", ready["coverage"])

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

    def test_nasdaq_collection_job_reports_holdings_and_monthly_steps(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_nasdaq100_valuation_context

        with patch("app.jobs.ingestion_jobs.ensure_nasdaq100_valuation_schemas"), \
             patch("app.jobs.ingestion_jobs.collect_and_store_qqq_sec_holdings", return_value={"rows_written": 505}), \
             patch("app.jobs.ingestion_jobs.materialize_and_store_nasdaq100_monthly", return_value={"rows_written": 17, "blocked_rows": 17}), \
             patch("app.jobs.ingestion_jobs.run_collect_ohlcv", return_value={"status": "success", "rows_written": 5, "message": "ok"}):
            result = run_collect_nasdaq100_valuation_context()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 527)
        self.assertEqual(result["details"]["pipeline_type"], "nasdaq100_valuation_context")

    def test_automation_includes_daily_nasdaq_valuation_job(self) -> None:
        from app.jobs.overview_automation import OVERVIEW_AUTOMATION_JOB_SPECS

        spec = next(item for item in OVERVIEW_AUTOMATION_JOB_SPECS if item.job_id == "nasdaq100_valuation")
        self.assertEqual(spec.cadence_minutes, 24 * 60)
        self.assertFalse(spec.market_hours_only)


if __name__ == "__main__":
    unittest.main()
