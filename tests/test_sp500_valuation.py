from __future__ import annotations

import unittest
from unittest.mock import Mock

import pandas as pd


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


if __name__ == "__main__":
    unittest.main()
