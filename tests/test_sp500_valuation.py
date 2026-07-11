from __future__ import annotations

import unittest
from unittest.mock import Mock

import pandas as pd


def monthly_pe_frame(months: int, start: str = "2020-01-01") -> pd.DataFrame:
    dates = pd.date_range(start, periods=months, freq="MS")
    return pd.DataFrame(
        {
            "observation_month": dates,
            "trailing_pe": [18.0 + (index * 0.15) for index in range(months)],
            "spx_level": [3600.0 + (index * 45.0) for index in range(months)],
            "trailing_eps": [200.0 + index for index in range(months)],
        }
    )


def sep_projection_frame() -> pd.DataFrame:
    values = {
        "real_gdp": {"median": 2.2, "central_tendency_lower": 2.0, "central_tendency_upper": 2.3},
        "pce_inflation": {"median": 3.6, "central_tendency_lower": 3.5, "central_tendency_upper": 3.7},
    }
    return pd.DataFrame(
        [
            {
                "release_date": "2026-06-17",
                "target_year": 2026,
                "variable_name": variable,
                "statistic_name": statistic,
                "value_pct": value,
                "source_ref": "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
            }
            for variable, statistics in values.items()
            for statistic, value in statistics.items()
        ]
    )


SEP_HTML_FIXTURE = """
<html>
  <head><title>June 17, 2026: FOMC Projections materials</title></head>
  <body>
    <p>For release at 2:00 p.m., EDT, June 17, 2026</p>
    <table>
      <thead>
        <tr><th>Variable</th><th>Statistic</th><th>2026</th><th>2027</th></tr>
      </thead>
      <tbody>
        <tr><td>Change in real GDP</td><td>Median</td><td>2.2</td><td>2.3</td></tr>
        <tr><td>Change in real GDP</td><td>Central Tendency</td><td>2.0–2.3</td><td>2.0–2.4</td></tr>
        <tr><td>PCE inflation</td><td>Median</td><td>3.6</td><td>2.3</td></tr>
        <tr><td>PCE inflation</td><td>Central Tendency</td><td>3.5–3.7</td><td>2.2–2.5</td></tr>
      </tbody>
    </table>
  </body>
</html>
"""


class Sp500ValuationDataTests(unittest.TestCase):
    def test_valuation_schema_preserves_monthly_earnings_and_sep_vintages(self) -> None:
        from finance.data.db.schema import VALUATION_SCHEMAS

        monthly = VALUATION_SCHEMAS["sp500_monthly_valuation"]
        earnings = VALUATION_SCHEMAS["sp500_index_earnings"]
        sep = VALUATION_SCHEMAS["fomc_sep_projection"]

        self.assertIn("UNIQUE KEY uk_sp500_month_source", monthly)
        self.assertIn("value_status ENUM('actual','estimate','mixed')", earnings)
        self.assertIn("UNIQUE KEY uk_sep_release_year_variable_stat", sep)

    def test_shiller_normalizer_emits_positive_monthly_per(self) -> None:
        from finance.data.sp500_valuation import normalize_shiller_monthly_frame

        frame = pd.DataFrame(
            {"Date": [2026.03], "P": [6654.4191], "E": [261.723], "CAPE": [37.03]}
        )

        rows = normalize_shiller_monthly_frame(
            frame,
            collected_at="2026-07-12 00:00:00",
        )

        self.assertEqual(rows[0]["observation_month"], "2026-03-01")
        self.assertAlmostEqual(rows[0]["trailing_pe"], 25.4254, places=4)
        self.assertEqual(rows[0]["data_quality"], "interpolated")

    def test_index_earnings_normalizer_keeps_actual_as_reported_quarters(self) -> None:
        from finance.data.sp500_valuation import normalize_index_earnings_frame

        frame = pd.DataFrame(
            {
                "period_end": ["2026-03-31"],
                "as_reported_eps": [70.0],
                "status": ["actual"],
            }
        )

        rows = normalize_index_earnings_frame(
            frame,
            source_release_date="2026-05-15",
        )

        self.assertEqual(rows[0]["earnings_basis"], "as_reported")
        self.assertEqual(rows[0]["value_status"], "actual")
        self.assertEqual(rows[0]["period_type"], "quarterly")

    def test_fomc_calendar_discovery_uses_latest_accessible_projection(self) -> None:
        from finance.data.sp500_valuation import discover_latest_fomc_sep_url

        calendar_html = """
        <a href="/monetarypolicy/fomcprojtabl20260318.htm">March projections</a>
        <a href="/monetarypolicy/fomcprojtabl20260617.htm">June projections</a>
        """

        self.assertEqual(
            discover_latest_fomc_sep_url(calendar_html),
            "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
        )

    def test_sep_parser_preserves_release_vintage_and_central_tendency(self) -> None:
        from finance.data.sp500_valuation import parse_fomc_sep_html

        rows = parse_fomc_sep_html(
            SEP_HTML_FIXTURE,
            source_url="https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
        )
        keyed = {
            (row["variable_name"], row["statistic_name"]): row["value_pct"]
            for row in rows
            if row["target_year"] == 2026
        }

        self.assertEqual(keyed[("real_gdp", "median")], 2.2)
        self.assertEqual(keyed[("pce_inflation", "central_tendency_upper")], 3.7)
        self.assertTrue(all(row["release_date"] == "2026-06-17" for row in rows))

    def test_shiller_collector_upserts_normalized_rows(self) -> None:
        from finance.data.sp500_valuation import collect_and_store_shiller_monthly_valuation

        db = Mock()
        db.query.return_value = [{"cnt": 0}]
        reader = Mock(
            return_value=[
                {
                    "observation_month": "2026-03-01",
                    "spx_level": 6654.4,
                    "trailing_eps": 261.7,
                    "trailing_pe": 25.42,
                    "cape": 37.03,
                    "data_quality": "interpolated",
                    "source": "robert_shiller_irrational_exuberance",
                    "source_ref": "fixture.xls",
                    "source_version": None,
                    "collected_at": "2026-07-12 00:00:00",
                    "error_msg": None,
                }
            ]
        )

        result = collect_and_store_shiller_monthly_valuation(
            workbook_reader=reader,
            db_factory=lambda *_args, **_kwargs: db,
        )

        self.assertEqual(result["rows_written"], 1)
        self.assertIn("ON DUPLICATE KEY UPDATE", db.executemany.call_args.args[0])
        db.close.assert_called_once()

    def test_index_earnings_import_requires_release_vintage(self) -> None:
        from finance.data.sp500_valuation import import_and_store_sp500_index_earnings

        db = Mock()
        db.query.return_value = [{"cnt": 0}]
        reader = Mock(
            return_value=[
                {
                    "period_end": "2026-03-31",
                    "period_type": "quarterly",
                    "earnings_basis": "as_reported",
                    "value_status": "actual",
                    "eps": 70.0,
                    "source": "sp_dow_jones_index_earnings",
                    "source_ref": "fixture.xlsx",
                    "source_release_date": "2026-05-15",
                    "collected_at": None,
                    "error_msg": None,
                }
            ]
        )

        result = import_and_store_sp500_index_earnings(
            "fixture.xlsx",
            source_release_date="2026-05-15",
            workbook_reader=reader,
            db_factory=lambda *_args, **_kwargs: db,
        )

        self.assertEqual(result["release_date"], "2026-05-15")
        self.assertEqual(db.executemany.call_args.args[1][0]["value_status"], "actual")

    def test_sep_collector_discovers_latest_release_and_preserves_vintage(self) -> None:
        from finance.data.sp500_valuation import collect_and_store_fomc_sep

        db = Mock()
        db.query.return_value = [{"cnt": 0}]
        calendar = '<a href="/monetarypolicy/fomcprojtabl20260617.htm">HTML</a>'

        result = collect_and_store_fomc_sep(
            calendar_fetcher=Mock(return_value=calendar),
            sep_fetcher=Mock(return_value=SEP_HTML_FIXTURE),
            db_factory=lambda *_args, **_kwargs: db,
        )

        self.assertEqual(result["release_date"], "2026-06-17")
        self.assertEqual(result["rows_written"], 12)
        self.assertIn("release_date = VALUES(release_date)", db.executemany.call_args.args[0])

    def test_multiple_regime_uses_60_months_and_36_month_sensitivity(self) -> None:
        from app.services.overview.sp500_valuation import calculate_multiple_regime

        result = calculate_multiple_regime(
            monthly_pe_frame(72),
            current_spx=7200.0,
            current_ttm_eps=280.0,
        )

        self.assertEqual(result["window_months"], 60)
        self.assertEqual(result["sensitivity"]["window_months"], 36)
        self.assertAlmostEqual(result["current_pe"], 25.7142857)
        self.assertIn(result["bucket"], {"LOW", "NEUTRAL", "HIGH", "EXTREME_HIGH"})
        self.assertEqual(len(result["series"]), 60)

    def test_ttm_loader_sums_latest_four_completed_actual_quarters(self) -> None:
        from finance.loaders.sp500_valuation import load_latest_sp500_ttm_actual_eps

        rows = [
            {"period_end": "2026-03-31", "eps": 72.0, "source_release_date": "2026-05-15"},
            {"period_end": "2025-12-31", "eps": 70.0, "source_release_date": "2026-02-15"},
            {"period_end": "2025-09-30", "eps": 66.0, "source_release_date": "2025-11-15"},
            {"period_end": "2025-06-30", "eps": 62.0, "source_release_date": "2025-08-15"},
            {"period_end": "2025-03-31", "eps": 58.0, "source_release_date": "2025-05-15"},
        ]

        result = load_latest_sp500_ttm_actual_eps(query_fn=lambda _sql, _params: rows)

        self.assertEqual(result["quarter_count"], 4)
        self.assertEqual(result["ttm_eps"], 270.0)
        self.assertEqual(result["value_status"], "actual")
        self.assertEqual(result["basis"], "as_reported")

    def test_fomc_eps_scenario_compounds_real_gdp_and_pce(self) -> None:
        from app.services.overview.sp500_valuation import calculate_fomc_eps_scenarios

        result = calculate_fomc_eps_scenarios(270.0, sep_projection_frame())

        self.assertAlmostEqual(result["baseline"]["growth_pct"], 5.8792, places=4)
        self.assertAlmostEqual(result["baseline"]["projected_eps"], 285.87384, places=5)
        self.assertEqual(result["target_year"], 2026)

    def test_index_scenario_blocks_spy_conversion_when_dates_differ(self) -> None:
        from app.services.overview.sp500_valuation import (
            calculate_fomc_eps_scenarios,
            calculate_index_scenario,
            calculate_multiple_regime,
        )

        result = calculate_index_scenario(
            multiple_regime=calculate_multiple_regime(
                monthly_pe_frame(60), current_spx=7200.0, current_ttm_eps=270.0
            ),
            eps_scenarios=calculate_fomc_eps_scenarios(270.0, sep_projection_frame()),
            current_spx={"date": "2026-07-10", "price": 7200.0},
            current_spy={"date": "2026-07-09", "price": 720.0},
        )

        self.assertIsNone(result["spy_equivalent"])
        self.assertEqual(result["spy_status"], "DATE_MISMATCH")

    def test_read_model_blocks_actual_scenario_for_mixed_eps(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        model = build_sp500_valuation_read_model(
            monthly_rows=monthly_pe_frame(60),
            ttm_evidence={"value_status": "mixed", "ttm_eps": 280.0},
            sep_rows=sep_projection_frame(),
            current_prices=pd.DataFrame(
                [
                    {"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7200.0},
                    {"symbol": "SPY", "latest_date": "2026-07-10", "price": 720.0},
                ]
            ),
        )

        self.assertEqual(model["earnings_scenario"]["status"], "BLOCKED")
        self.assertIn("실제 EPS", model["earnings_scenario"]["reason"])

    def test_read_model_marks_sep_stale_against_spx_date(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        stale_sep = sep_projection_frame().assign(release_date="2025-12-01")
        model = build_sp500_valuation_read_model(
            monthly_rows=monthly_pe_frame(60),
            ttm_evidence={"status": "READY", "value_status": "actual", "ttm_eps": 280.0},
            sep_rows=stale_sep,
            current_prices=pd.DataFrame(
                [
                    {"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7200.0},
                    {"symbol": "SPY", "latest_date": "2026-07-10", "price": 720.0},
                ]
            ),
        )

        self.assertEqual(model["earnings_scenario"]["status"], "STALE_SEP")
        self.assertEqual(model["index_scenario"]["status"], "BLOCKED")


if __name__ == "__main__":
    unittest.main()
