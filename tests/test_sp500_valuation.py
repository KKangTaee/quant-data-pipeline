from __future__ import annotations

from io import BytesIO
import unittest
from unittest.mock import Mock
from unittest.mock import patch

import pandas as pd


def xlsx_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=sheet_name, index=False)
    return buffer.getvalue()


def raw_xlsx_bytes(sheets: dict[str, pd.DataFrame]) -> bytes:
    buffer = BytesIO()
    with pd.ExcelWriter(buffer, engine="openpyxl") as writer:
        for sheet_name, frame in sheets.items():
            frame.to_excel(writer, sheet_name=sheet_name, index=False, header=False)
    return buffer.getvalue()


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


def sep_history_frame() -> pd.DataFrame:
    inputs = [
        ("2025-06-18", 2025, 2.0, 2.5),
        ("2025-09-17", 2025, 2.1, 2.6),
        ("2025-12-10", 2025, 2.2, 2.7),
        ("2025-12-10", 2026, 2.2, 2.8),
        ("2026-03-18", 2026, 2.3, 3.0),
        ("2026-06-17", 2026, 2.4, 3.2),
    ]
    return pd.DataFrame(
        [
            {
                "release_date": release_date,
                "target_year": target_year,
                "variable_name": variable_name,
                "statistic_name": "median",
                "value_pct": value,
                "source_ref": f"https://www.federalreserve.gov/monetarypolicy/fomcprojtabl{release_date.replace('-', '')}.htm",
            }
            for release_date, target_year, real_gdp, pce in inputs
            for variable_name, value in (("real_gdp", real_gdp), ("pce_inflation", pce))
        ]
    )


def five_year_sep_history_frame() -> pd.DataFrame:
    releases = [
        "2021-03-17", "2021-06-16", "2021-09-22", "2021-12-15",
        "2022-06-15", "2022-09-21", "2022-12-14",
        "2023-03-22", "2023-06-14", "2023-09-20", "2023-12-13",
        "2024-03-20", "2024-06-12", "2024-09-18", "2024-12-18",
        "2025-03-19", "2025-06-18", "2025-09-17", "2025-12-10",
        "2026-03-18", "2026-06-17",
    ]
    inputs: list[tuple[str, int, float, float]] = []
    for release_date in releases:
        release = pd.Timestamp(release_date)
        inputs.append((release_date, release.year, 2.0, 2.5))
        if release.month == 12:
            inputs.append((release_date, release.year + 1, 2.1, 2.4))
    return pd.DataFrame(
        [
            {
                "release_date": release_date,
                "target_year": target_year,
                "variable_name": variable_name,
                "statistic_name": "median",
                "value_pct": value,
                "source_ref": f"https://www.federalreserve.gov/monetarypolicy/fomcprojtabl{release_date.replace('-', '')}.htm",
            }
            for release_date, target_year, real_gdp, pce in inputs
            for variable_name, value in (("real_gdp", real_gdp), ("pce_inflation", pce))
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
    def test_monthly_valuation_loader_keeps_five_year_window_and_rolling_warmup(self) -> None:
        from finance.loaders.sp500_valuation import load_sp500_monthly_valuation

        query_fn = Mock(return_value=[])

        load_sp500_monthly_valuation(query_fn=query_fn)

        self.assertEqual(query_fn.call_args.args[1], (120,))

    def test_valuation_schema_preserves_monthly_earnings_and_sep_vintages(self) -> None:
        from finance.data.db.schema import VALUATION_SCHEMAS

        monthly = VALUATION_SCHEMAS["sp500_monthly_valuation"]
        earnings = VALUATION_SCHEMAS["sp500_index_earnings"]
        sep = VALUATION_SCHEMAS["fomc_sep_projection"]

        self.assertIn("UNIQUE KEY uk_sp500_month_source", monthly)
        self.assertIn("value_status ENUM('actual','estimate','mixed')", earnings)
        self.assertIn("UNIQUE KEY uk_sep_release_year_variable_stat", sep)

    def test_schema_bootstrap_creates_all_valuation_tables(self) -> None:
        from finance.data.sp500_valuation import ensure_sp500_valuation_schemas

        db = Mock()
        db.query.return_value = [{"cnt": 0}]

        ensure_sp500_valuation_schemas(db_factory=lambda *_args, **_kwargs: db)

        executed = "\n".join(call.args[0] for call in db.execute.call_args_list)
        self.assertIn("sp500_monthly_valuation", executed)
        self.assertIn("sp500_index_earnings", executed)
        self.assertIn("fomc_sep_projection", executed)
        db.close.assert_called_once()

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

    def test_shiller_normalizer_preserves_price_before_eps_is_published(self) -> None:
        from finance.data.sp500_valuation import normalize_shiller_monthly_frame

        frame = pd.DataFrame(
            {"Date": [2026.07], "P": [7575.2], "E": [None], "CAPE": [None]}
        )

        rows = normalize_shiller_monthly_frame(frame)

        self.assertEqual(rows[0]["observation_month"], "2026-07-01")
        self.assertEqual(rows[0]["spx_level"], 7575.2)
        self.assertIsNone(rows[0]["trailing_eps"])
        self.assertIsNone(rows[0]["trailing_pe"])
        self.assertEqual(rows[0]["data_quality"], "missing")

    def test_shiller_page_discovery_uses_current_xls_download(self) -> None:
        from finance.data.sp500_valuation import discover_shiller_workbook_url

        page = '<a href="https://cdn.example/downloads/ie_data.xls?ver=20260708">Download</a>'

        self.assertEqual(
            discover_shiller_workbook_url(page),
            "https://cdn.example/downloads/ie_data.xls?ver=20260708",
        )

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

    def test_index_earnings_reader_accepts_explicit_official_quarterly_sheet(self) -> None:
        from finance.data.sp500_valuation import (
            SP500_INDEX_EARNINGS_URL,
            read_sp500_index_earnings_workbook,
        )

        workbook = xlsx_bytes(
            {
                "README": pd.DataFrame({"Notes": ["S&P 500 Index Earnings"]}),
                "QUARTERLY DATA": pd.DataFrame(
                    {
                        "Quarter End": ["2025-12-31", "2026-03-31", "2026-06-30"],
                        "Status": ["Actual", "Actual", "Estimate"],
                        "As Reported EPS": [70.0, 72.0, 74.0],
                        "Operating EPS": [71.0, 73.0, 75.0],
                    }
                ),
            }
        )

        rows = read_sp500_index_earnings_workbook(
            workbook,
            source_release_date="2026-05-15",
            source_ref=SP500_INDEX_EARNINGS_URL,
        )

        self.assertEqual(len(rows), 6)
        self.assertEqual(
            {(row["earnings_basis"], row["value_status"]) for row in rows},
            {
                ("as_reported", "actual"),
                ("as_reported", "estimate"),
                ("operating", "actual"),
                ("operating", "estimate"),
            },
        )
        self.assertTrue(
            all(row["source_ref"] == SP500_INDEX_EARNINGS_URL for row in rows)
        )

    def test_index_earnings_reader_parses_official_quarterly_data_layout(self) -> None:
        from finance.data.sp500_valuation import read_sp500_index_earnings_workbook

        workbook = raw_xlsx_bytes(
            {
                "QUARTERLY DATA": pd.DataFrame(
                    [
                        ["S&P Dow Jones Indices", None, None],
                        ["S&P 500 QUARTERLY DATA", None, None],
                        [None, None, None],
                        [None, "OPERATING", "AS REPORTED"],
                        ["QUARTER", "EARNINGS", "EARNINGS"],
                        ["END", "PER SHR", "PER SHR"],
                        [pd.Timestamp("2026-03-31"), None, None],
                        [pd.Timestamp("2025-12-31"), 70.0, 63.0],
                        [pd.Timestamp("2025-09-30"), 68.0, 61.0],
                    ]
                )
            }
        )

        rows = read_sp500_index_earnings_workbook(
            workbook,
            source_release_date="2026-05-15",
        )

        self.assertEqual(len(rows), 4)
        self.assertEqual(
            {(row["period_end"], row["earnings_basis"], row["value_status"]) for row in rows},
            {
                ("2025-12-31", "operating", "actual"),
                ("2025-12-31", "as_reported", "actual"),
                ("2025-09-30", "operating", "actual"),
                ("2025-09-30", "as_reported", "actual"),
            },
        )

    def test_index_earnings_reader_keeps_normalized_first_sheet_compatibility(self) -> None:
        from finance.data.sp500_valuation import read_sp500_index_earnings_workbook

        workbook = xlsx_bytes(
            {
                "Sheet1": pd.DataFrame(
                    {
                        "period_end": ["2026-03-31"],
                        "period_type": ["quarterly"],
                        "status": ["actual"],
                        "as_reported_eps": [72.0],
                    }
                )
            }
        )

        rows = read_sp500_index_earnings_workbook(
            workbook,
            source_release_date="2026-05-15",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["value_status"], "actual")
        self.assertEqual(rows[0]["earnings_basis"], "as_reported")

    def test_index_earnings_reader_rejects_workbook_without_explicit_status(self) -> None:
        from finance.data.sp500_valuation import read_sp500_index_earnings_workbook

        workbook = xlsx_bytes(
            {
                "QUARTERLY DATA": pd.DataFrame(
                    {
                        "Quarter End": ["2026-03-31"],
                        "As Reported EPS": [72.0],
                    }
                )
            }
        )

        with self.assertRaisesRegex(ValueError, "actual/estimate 상태"):
            read_sp500_index_earnings_workbook(
                workbook,
                source_release_date="2026-05-15",
            )

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

    def test_fomc_calendar_discovery_returns_ordered_unique_vintages(self) -> None:
        from finance.data.sp500_valuation import discover_fomc_sep_urls

        calendar_html = """
        <a href="/monetarypolicy/fomcprojtabl20250917.htm">September</a>
        <a href="/monetarypolicy/fomcprojtabl20250618.htm">June</a>
        <a href="/monetarypolicy/fomcprojtabl20250917.htm?duplicate=1">Duplicate</a>
        """

        self.assertEqual(
            discover_fomc_sep_urls(calendar_html),
            [
                "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20250618.htm",
                "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20250917.htm",
            ],
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
            source_ref="fixture.xls",
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

    def test_index_earnings_import_reports_actual_coverage_and_commits(self) -> None:
        from finance.data.sp500_valuation import (
            SP500_INDEX_EARNINGS_URL,
            import_and_store_sp500_index_earnings,
        )

        db = Mock()
        db.query.side_effect = [
            [{"cnt": 0}],
            [
                {
                    "actual_quarter_count": 6,
                    "latest_actual_period_end": "2026-03-31",
                }
            ],
        ]
        reader = Mock(
            return_value=[
                {
                    "period_end": "2026-03-31",
                    "period_type": "quarterly",
                    "earnings_basis": "as_reported",
                    "value_status": "actual",
                    "eps": 72.0,
                    "source": "sp_dow_jones_index_earnings",
                    "source_ref": "uploaded-file.xlsx",
                    "source_release_date": "2026-05-15",
                    "collected_at": None,
                    "error_msg": None,
                }
            ]
        )

        result = import_and_store_sp500_index_earnings(
            b"xlsx",
            source_release_date="2026-05-15",
            workbook_reader=reader,
            db_factory=lambda *_args, **_kwargs: db,
        )

        self.assertEqual(result["actual_quarter_count"], 6)
        self.assertEqual(result["latest_actual_period_end"], "2026-03-31")
        self.assertEqual(result["remaining_quarters"], 2)
        self.assertEqual(result["source_ref"], SP500_INDEX_EARNINGS_URL)
        self.assertEqual(
            db.executemany.call_args.args[1][0]["source_ref"],
            SP500_INDEX_EARNINGS_URL,
        )
        reader.assert_called_once_with(
            b"xlsx",
            source_release_date="2026-05-15",
            source_ref=SP500_INDEX_EARNINGS_URL,
        )
        db.begin.assert_called_once()
        db.commit.assert_called_once()
        db.rollback.assert_not_called()

    def test_index_earnings_import_rolls_back_failed_batch(self) -> None:
        from finance.data.sp500_valuation import import_and_store_sp500_index_earnings

        db = Mock()
        db.query.return_value = [{"cnt": 0}]
        db.executemany.side_effect = RuntimeError("write failed")
        reader = Mock(
            return_value=[
                {
                    "period_end": "2026-03-31",
                    "period_type": "quarterly",
                    "earnings_basis": "as_reported",
                    "value_status": "actual",
                    "eps": 72.0,
                    "source": "sp_dow_jones_index_earnings",
                    "source_ref": None,
                    "source_release_date": "2026-05-15",
                    "collected_at": None,
                    "error_msg": None,
                }
            ]
        )

        with self.assertRaisesRegex(RuntimeError, "write failed"):
            import_and_store_sp500_index_earnings(
                b"xlsx",
                source_release_date="2026-05-15",
                workbook_reader=reader,
                db_factory=lambda *_args, **_kwargs: db,
            )

        db.begin.assert_called_once()
        db.rollback.assert_called_once()
        db.commit.assert_not_called()
        db.close.assert_called_once()

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

    def test_sep_history_collector_fetches_only_missing_official_vintages(self) -> None:
        from finance.data.sp500_valuation import collect_and_store_fomc_sep_history

        db = Mock()
        db.query.side_effect = [
            [{"cnt": 0}],
            [{"release_date": "2026-06-17"}],
        ]
        source_refs = [
            "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260318.htm",
            "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
        ]
        fetcher = Mock(return_value=SEP_HTML_FIXTURE)

        result = collect_and_store_fomc_sep_history(
            source_refs=source_refs,
            sep_fetcher=fetcher,
            db_factory=lambda *_args, **_kwargs: db,
        )

        self.assertEqual(fetcher.call_count, 1)
        self.assertEqual(
            fetcher.call_args.args[0],
            "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260318.htm",
        )
        self.assertEqual(result["release_dates"], ["2026-03-18"])
        self.assertEqual(result["rows_written"], 12)
        self.assertTrue(all(row["release_date"] == "2026-03-18" for row in db.executemany.call_args.args[1]))

    def test_sep_history_collector_discovers_calendar_and_fetches_only_missing_vintages(self) -> None:
        from finance.data.sp500_valuation import collect_and_store_fomc_sep_history

        db = Mock()
        db.query.side_effect = [
            [{"cnt": 0}],
            [{"release_date": "2026-03-18"}],
        ]
        calendar = """
            <a href="/monetarypolicy/fomcprojtabl20251210.htm">2025</a>
            <a href="/monetarypolicy/fomcprojtabl20260318.htm">March</a>
            <a href="/monetarypolicy/fomcprojtabl20260617.htm">June</a>
        """
        calendar_fetcher = Mock(return_value=calendar)
        sep_fetcher = Mock(return_value=SEP_HTML_FIXTURE)

        result = collect_and_store_fomc_sep_history(
            calendar_fetcher=calendar_fetcher,
            sep_fetcher=sep_fetcher,
            db_factory=lambda *_args, **_kwargs: db,
        )

        calendar_fetcher.assert_called_once()
        self.assertEqual(
            [call.args[0] for call in sep_fetcher.call_args_list],
            [
                "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20251210.htm",
                "https://www.federalreserve.gov/monetarypolicy/fomcprojtabl20260617.htm",
            ],
        )
        self.assertEqual(result["release_dates"], ["2025-12-10", "2026-06-17"])
        self.assertEqual(result["rows_written"], 24)

    def test_multiple_regime_uses_latest_shiller_per_as_current_marker(self) -> None:
        from app.services.overview.sp500_valuation import calculate_multiple_regime

        result = calculate_multiple_regime(monthly_pe_frame(72))

        self.assertEqual(result["window_months"], 60)
        self.assertEqual(result["sensitivity"]["window_months"], 36)
        self.assertAlmostEqual(result["current_pe"], 28.65)
        self.assertIn(result["bucket"], {"LOW", "NEUTRAL", "HIGH", "EXTREME_HIGH"})
        self.assertEqual(len(result["series"]), 60)
        self.assertEqual(result["current_basis_date"], "2025-12-01")

    def test_multiple_regime_returns_symmetric_minus_two_sigma_anchor(self) -> None:
        from app.services.overview.sp500_valuation import calculate_multiple_regime

        result = calculate_multiple_regime(monthly_pe_frame(72))

        self.assertIn("minus_2sigma", result)
        self.assertLess(result["minus_2sigma"], result["minus_1sigma"])
        self.assertAlmostEqual(
            result["mean_multiple"] ** 2,
            result["minus_1sigma"] * result["plus_1sigma"],
            places=8,
        )

    def test_multiple_regime_extends_price_only_months_as_provisional(self) -> None:
        from app.services.overview.sp500_valuation import calculate_multiple_regime

        complete = monthly_pe_frame(64, start="2020-12-01")
        latest_eps = float(complete.iloc[-1]["trailing_eps"])
        price_only = pd.DataFrame(
            {
                "observation_month": pd.date_range("2026-04-01", periods=4, freq="MS"),
                "spx_level": [6957.0, 7412.55, 7450.03, 7503.85],
                "trailing_eps": [None, None, None, None],
                "trailing_pe": [None, None, None, None],
            }
        )
        rows = pd.concat([complete, price_only], ignore_index=True)
        complete_only = calculate_multiple_regime(complete)

        result = calculate_multiple_regime(
            rows,
            current_spx={"date": "2026-07-10", "price": 7575.39},
        )

        self.assertEqual(len(result["series"]), 60)
        self.assertEqual(result["series"][-2]["month"], "2026-06-01")
        self.assertEqual(result["series"][-2]["quality"], "provisional")
        self.assertEqual(result["series"][-1]["month"], "2026-07-01")
        self.assertEqual(result["series"][-1]["quality"], "provisional")
        self.assertEqual(result["series"][-1]["price_basis_date"], "2026-07-10")
        self.assertEqual(result["current_price_basis_date"], "2026-07-10")
        self.assertEqual(result["current_eps_basis_date"], "2026-03-01")
        self.assertTrue(result["current_is_provisional"])
        self.assertAlmostEqual(result["current_pe"], 7575.39 / latest_eps)
        self.assertEqual(result["latest_complete_basis_date"], "2026-03-01")
        self.assertAlmostEqual(result["latest_complete_pe"], float(complete.iloc[-1]["trailing_pe"]))
        for key in ("minus_2sigma", "minus_1sigma", "mean_multiple", "plus_1sigma", "plus_2sigma"):
            self.assertAlmostEqual(result[key], complete_only[key])

    def test_read_model_passes_latest_spx_to_graph_one_provisional_marker(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        complete = monthly_pe_frame(64, start="2020-12-01")
        rows = pd.concat(
            [
                complete,
                pd.DataFrame(
                    {
                        "observation_month": pd.date_range("2026-04-01", periods=4, freq="MS"),
                        "spx_level": [6957.0, 7412.55, 7450.03, 7503.85],
                        "trailing_eps": [None, None, None, None],
                        "trailing_pe": [None, None, None, None],
                    }
                ),
            ],
            ignore_index=True,
        )

        model = build_sp500_valuation_read_model(
            monthly_rows=rows,
            ttm_evidence={
                "status": "READY",
                "current_ttm_eps": 263.0,
                "eps_source": "Robert Shiller TTM EPS",
                "eps_source_quality": "interpolated_ttm_proxy",
                "eps_basis_date": "2026-03-01",
            },
            sep_rows=sep_projection_frame(),
            sep_history_rows=sep_history_frame(),
            current_prices=pd.DataFrame(
                [{"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7575.39}]
            ),
        )

        multiple = model["multiple_regime"]
        self.assertTrue(multiple["current_is_provisional"])
        self.assertEqual(multiple["current_price_basis_date"], "2026-07-10")
        self.assertAlmostEqual(multiple["current_pe"], 7575.39 / 263.0)

    def test_read_model_keeps_graph_one_ready_without_official_eps(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        model = build_sp500_valuation_read_model(
            monthly_rows=monthly_pe_frame(60),
            ttm_evidence={
                "status": "INSUFFICIENT_HISTORY",
                "quarter_count": 0,
                "ttm_eps": None,
                "value_status": "actual",
            },
            sep_rows=pd.DataFrame(),
            current_prices=pd.DataFrame(),
        )

        self.assertEqual(model["multiple_regime"]["status"], "READY")
        self.assertAlmostEqual(model["multiple_regime"]["current_pe"], 26.85)
        self.assertEqual(model["earnings_scenario"]["status"], "BLOCKED")

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

    def test_ttm_loader_excludes_future_release_vintages(self) -> None:
        from finance.loaders.sp500_valuation import load_latest_sp500_ttm_actual_eps

        captured: dict[str, object] = {}

        def query(sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
            captured["sql"] = sql
            captured["params"] = params
            return []

        load_latest_sp500_ttm_actual_eps(query_fn=query)

        self.assertIn("source_release_date <= CURRENT_DATE()", captured["sql"])
        self.assertEqual(captured["params"], ())

    def test_actual_eps_history_requires_eight_distinct_completed_quarters(self) -> None:
        from finance.loaders.sp500_valuation import load_sp500_actual_eps_history

        period_ends = [
            "2026-03-31",
            "2025-12-31",
            "2025-09-30",
            "2025-06-30",
            "2025-03-31",
            "2024-12-31",
            "2024-09-30",
            "2024-06-30",
        ]
        rows = [
            {
                "period_end": period_end,
                "eps": 72.0 - index * 2.0,
                "source_release_date": period_end,
            }
            for index, period_end in enumerate(period_ends)
        ]

        result = load_sp500_actual_eps_history(
            query_fn=lambda _sql, _params: rows
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["quarter_count"], 8)
        self.assertAlmostEqual(
            result["current_ttm_eps"],
            sum(row["eps"] for row in rows[:4]),
        )
        self.assertAlmostEqual(
            result["prior_ttm_eps"],
            sum(row["eps"] for row in rows[4:8]),
        )
        self.assertIsNotNone(result["growth_pct"])

    def test_actual_eps_history_bounds_period_and_release_vintage_by_as_of_date(self) -> None:
        from finance.loaders.sp500_valuation import load_sp500_actual_eps_history

        captured: dict[str, object] = {}

        def query(sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
            captured["sql"] = sql
            captured["params"] = params
            return []

        load_sp500_actual_eps_history(
            end_date="2026-03-31",
            query_fn=query,
        )

        self.assertIn("period_end <= %s", captured["sql"])
        self.assertIn("source_release_date <= %s", captured["sql"])
        self.assertEqual(captured["params"], ("2026-03-31", "2026-03-31"))

    def test_actual_eps_history_bounds_default_release_vintage_to_current_date(self) -> None:
        from finance.loaders.sp500_valuation import load_sp500_actual_eps_history

        captured: dict[str, object] = {}

        def query(sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
            captured["sql"] = sql
            captured["params"] = params
            return []

        load_sp500_actual_eps_history(query_fn=query)

        self.assertIn("period_end <= CURRENT_DATE()", captured["sql"])
        self.assertIn("source_release_date <= CURRENT_DATE()", captured["sql"])
        self.assertEqual(captured["params"], ())

    def test_sep_history_loader_returns_all_release_vintages(self) -> None:
        from finance.loaders.sp500_valuation import load_fomc_sep_projection_history

        captured: dict[str, object] = {}

        def query(sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
            captured["sql"] = sql
            captured["params"] = params
            return sep_history_frame().to_dict("records")

        frame = load_fomc_sep_projection_history(query_fn=query)

        self.assertEqual(frame["release_date"].nunique(), 5)
        self.assertNotIn("MAX(release_date)", str(captured["sql"]))
        self.assertEqual(captured["params"], ())

    def test_shiller_ttm_loader_returns_latest_positive_eps_with_basis_date(self) -> None:
        from finance.loaders.sp500_valuation import load_latest_shiller_ttm_eps

        captured: dict[str, object] = {}
        rows = [
            {
                "observation_month": "2026-03-01",
                "trailing_eps": 261.723,
                "source": "robert_shiller_irrational_exuberance",
                "source_ref": "https://www.econ.yale.edu/~shiller/data.htm",
                "data_quality": "interpolated",
            }
        ]

        def query(sql: str, params: tuple[object, ...]) -> list[dict[str, object]]:
            captured["sql"] = sql
            captured["params"] = params
            return rows

        result = load_latest_shiller_ttm_eps(query_fn=query)

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["current_ttm_eps"], 261.723)
        self.assertEqual(result["eps_source"], "Robert Shiller TTM EPS")
        self.assertEqual(result["eps_source_quality"], "interpolated_ttm_proxy")
        self.assertEqual(result["eps_basis_date"], "2026-03-01")
        self.assertIn("source = %s", str(captured["sql"]))
        self.assertEqual(
            captured["params"],
            ("robert_shiller_irrational_exuberance",),
        )

    def test_eps_resolver_prefers_official_actual_over_shiller(self) -> None:
        from finance.loaders.sp500_valuation import resolve_sp500_ttm_eps

        result = resolve_sp500_ttm_eps(
            official_evidence={
                "status": "READY",
                "ttm_eps": 270.0,
                "value_status": "actual",
                "latest_period_end": "2026-03-31",
            },
            shiller_evidence={
                "status": "READY",
                "current_ttm_eps": 261.723,
                "eps_basis_date": "2026-03-01",
            },
        )

        self.assertEqual(result["current_ttm_eps"], 270.0)
        self.assertEqual(result["eps_source"], "S&P 공식 실제 EPS")
        self.assertEqual(result["eps_source_quality"], "official_actual")
        self.assertIsNone(result["fallback_reason"])

    def test_eps_resolver_uses_shiller_when_official_actual_is_missing(self) -> None:
        from finance.loaders.sp500_valuation import resolve_sp500_ttm_eps

        result = resolve_sp500_ttm_eps(
            official_evidence={
                "status": "INSUFFICIENT_HISTORY",
                "quarter_count": 0,
                "ttm_eps": None,
            },
            shiller_evidence={
                "status": "READY",
                "current_ttm_eps": 261.723,
                "eps_source": "Robert Shiller TTM EPS",
                "eps_source_quality": "interpolated_ttm_proxy",
                "eps_basis_date": "2026-03-01",
            },
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["current_ttm_eps"], 261.723)
        self.assertEqual(result["eps_source"], "Robert Shiller TTM EPS")
        self.assertIn("공식 actual EPS", result["fallback_reason"])

    def test_fomc_eps_scenario_adds_real_gdp_and_pce(self) -> None:
        from app.services.overview.sp500_valuation import calculate_fomc_eps_scenarios

        result = calculate_fomc_eps_scenarios(270.0, sep_projection_frame())

        self.assertAlmostEqual(result["baseline"]["growth_pct"], 5.8, places=4)
        self.assertAlmostEqual(result["baseline"]["projected_eps"], 285.66, places=5)
        self.assertEqual(result["target_year"], 2026)

    def test_index_scenario_applies_one_expected_eps_to_multiple_band(self) -> None:
        from app.services.overview.sp500_valuation import calculate_index_scenario

        result = calculate_index_scenario(
            multiple_regime={
                "status": "READY",
                "minus_1sigma": 20.0,
                "mean_multiple": 25.0,
                "plus_1sigma": 30.0,
            },
            eps_scenarios={
                "status": "READY",
                "conservative": {"projected_eps": 90.0},
                "baseline": {"projected_eps": 100.0},
                "optimistic": {"projected_eps": 110.0},
            },
            current_spx={"date": "2026-07-10", "price": 2600.0},
        )

        self.assertEqual(
            result["spx_scenarios"],
            {"lower": 2000.0, "baseline": 2500.0, "upper": 3000.0},
        )
        self.assertAlmostEqual(result["current_vs_baseline_gap_pct"], 4.0)
        self.assertEqual(result["valuation_position"], "ABOVE_BASELINE")

    def test_read_model_uses_shiller_fallback_and_reports_macro_inputs(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        model = build_sp500_valuation_read_model(
            monthly_rows=monthly_pe_frame(60),
            ttm_evidence={
                "status": "READY",
                "current_ttm_eps": 261.723,
                "ttm_eps": 261.723,
                "eps_source": "Robert Shiller TTM EPS",
                "eps_source_quality": "interpolated_ttm_proxy",
                "eps_basis_date": "2026-03-01",
                "fallback_reason": "공식 actual EPS가 없어 Shiller 기준을 사용합니다.",
            },
            sep_rows=sep_projection_frame(),
            current_prices=pd.DataFrame(
                [
                    {"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7200.0},
                    {"symbol": "SPY", "latest_date": "2026-07-10", "price": 720.0},
                ]
            ),
        )

        earnings = model["earnings_scenario"]
        index = model["index_scenario"]
        self.assertEqual(model["status"], "READY")
        self.assertEqual(earnings["eps_source"], "Robert Shiller TTM EPS")
        self.assertEqual(earnings["eps_source_quality"], "interpolated_ttm_proxy")
        self.assertEqual(earnings["eps_basis_date"], "2026-03-01")
        self.assertEqual(earnings["baseline"]["real_gdp_pct"], 2.2)
        self.assertEqual(earnings["baseline"]["pce_inflation_pct"], 3.6)
        self.assertAlmostEqual(earnings["baseline"]["growth_pct"], 5.8)
        expected_eps = earnings["baseline"]["projected_eps"]
        self.assertAlmostEqual(
            index["spx_scenarios"]["lower"],
            expected_eps * model["multiple_regime"]["minus_1sigma"],
        )
        self.assertTrue(index["basis_date_mismatch"])

    def test_historical_scenario_uses_next_month_sep_and_calendar_year_target(self) -> None:
        from app.services.overview.sp500_valuation import calculate_historical_index_scenario

        months = pd.date_range("2019-12-01", "2026-07-01", freq="MS")
        rows = pd.DataFrame(
            {
                "observation_month": months,
                "spx_level": [3200.0 + index * 55.0 for index in range(len(months))],
                "trailing_eps": [
                    180.0 + index if month <= pd.Timestamp("2026-03-01") else None
                    for index, month in enumerate(months)
                ],
            }
        )
        rows["trailing_pe"] = rows["spx_level"] / rows["trailing_eps"]

        result = calculate_historical_index_scenario(
            rows,
            sep_history_frame(),
            current_spx={"date": "2026-07-10", "price": 7575.0},
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["window_months"], 12)
        self.assertEqual(len(result["series"]), 12)
        keyed = {row["month"]: row for row in result["series"]}
        self.assertEqual(keyed["2025-09-01"]["sep_release_date"], "2025-06-18")
        self.assertEqual(keyed["2025-10-01"]["sep_release_date"], "2025-09-17")
        self.assertEqual(keyed["2026-01-01"]["sep_release_date"], "2025-12-10")
        self.assertEqual(keyed["2026-01-01"]["target_year"], 2026)
        self.assertEqual(keyed["2026-04-01"]["sep_release_date"], "2026-03-18")
        self.assertEqual(keyed["2026-07-01"]["sep_release_date"], "2026-06-17")
        self.assertEqual(keyed["2026-07-01"]["eps_basis_date"], "2026-03-01")
        self.assertEqual(keyed["2026-07-01"]["actual_spx"], 7575.0)
        self.assertGreater(keyed["2026-07-01"]["upper_spx"], keyed["2026-07-01"]["baseline_spx"])
        self.assertLess(keyed["2026-07-01"]["lower_spx"], keyed["2026-07-01"]["baseline_spx"])

    def test_historical_scenario_supports_one_three_and_five_year_windows(self) -> None:
        from app.services.overview.sp500_valuation import calculate_historical_index_scenario

        rows = monthly_pe_frame(120, start="2016-08-01")
        sep_rows = five_year_sep_history_frame()

        for visible_months, expected_years in ((12, 1), (36, 3), (60, 5)):
            result = calculate_historical_index_scenario(
                rows,
                sep_rows,
                current_spx={"date": "2026-07-10", "price": 7575.0},
                visible_months=visible_months,
            )

            self.assertEqual(result["status"], "READY")
            self.assertEqual(result["window_months"], visible_months)
            self.assertEqual(result["window_years"], expected_years)
            self.assertEqual(result["observation_count"], visible_months)
            self.assertEqual(len(result["series"]), visible_months)
            self.assertEqual(result["coverage_start"], result["series"][0]["month"])
            self.assertEqual(result["coverage_end"], "2026-07-01")
            self.assertEqual(result["label"], f"최근 {expected_years}년 과거 시점 재구성 시나리오")

    def test_historical_scenario_explains_rolling_warmup_shortfall(self) -> None:
        from app.services.overview.sp500_valuation import calculate_historical_index_scenario

        result = calculate_historical_index_scenario(
            monthly_pe_frame(60, start="2021-08-01"),
            five_year_sep_history_frame(),
            current_spx={"date": "2026-07-10", "price": 7575.0},
            visible_months=60,
        )

        self.assertEqual(result["status"], "INSUFFICIENT_HISTORY")
        self.assertEqual(result["observation_count"], 1)
        self.assertEqual(
            result["reason_code"], "INSUFFICIENT_ROLLING_PER_WARMUP"
        )
        self.assertEqual(result["requested_display_months"], 60)
        self.assertEqual(result["rolling_window_months"], 60)
        self.assertEqual(result["required_history_months"], 119)
        self.assertEqual(result["available_history_months"], 60)
        self.assertEqual(result["missing_history_months"], 59)

    def test_historical_scenario_does_not_label_partial_visible_window_ready(self) -> None:
        from app.services.overview.sp500_valuation import calculate_historical_index_scenario

        result = calculate_historical_index_scenario(
            monthly_pe_frame(66, start="2021-02-01"),
            five_year_sep_history_frame(),
            current_spx={"date": "2026-07-10", "price": 7575.0},
            visible_months=60,
        )

        self.assertEqual(result["observation_count"], 7)
        self.assertEqual(result["status"], "INSUFFICIENT_HISTORY")
        self.assertEqual(
            result["reason_code"], "INSUFFICIENT_ROLLING_PER_WARMUP"
        )

    def test_read_model_exposes_one_year_reconstructed_history(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        rows = monthly_pe_frame(76, start="2020-04-01")
        model = build_sp500_valuation_read_model(
            monthly_rows=rows,
            ttm_evidence={
                "status": "READY",
                "current_ttm_eps": 261.7,
                "eps_source": "Robert Shiller TTM EPS",
                "eps_source_quality": "interpolated_ttm_proxy",
                "eps_basis_date": "2026-03-01",
            },
            sep_rows=sep_projection_frame(),
            sep_history_rows=sep_history_frame(),
            current_prices=pd.DataFrame(
                [{"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7575.0}]
            ),
        )

        history = model["index_scenario"]["history"]
        self.assertEqual(history["status"], "READY")
        self.assertEqual(history["window_months"], 12)
        self.assertIn("과거 시점 재구성", history["label"])

    def test_read_model_exposes_one_three_and_five_year_history_options(self) -> None:
        from app.services.overview.sp500_valuation import build_sp500_valuation_read_model

        rows = monthly_pe_frame(120, start="2016-08-01")
        model = build_sp500_valuation_read_model(
            monthly_rows=rows,
            ttm_evidence={
                "status": "READY",
                "current_ttm_eps": 261.7,
                "eps_source": "Robert Shiller TTM EPS",
                "eps_source_quality": "interpolated_ttm_proxy",
                "eps_basis_date": "2026-03-01",
            },
            sep_rows=sep_projection_frame(),
            sep_history_rows=five_year_sep_history_frame(),
            current_prices=pd.DataFrame(
                [{"symbol": "^GSPC", "latest_date": "2026-07-10", "price": 7575.0}]
            ),
        )

        options = model["index_scenario"]["history_options"]
        self.assertEqual(set(options), {"1y", "3y", "5y"})
        self.assertEqual([len(options[key]["series"]) for key in ("1y", "3y", "5y")], [12, 36, 60])
        self.assertEqual(model["index_scenario"]["history"], options["1y"])

    def test_index_scenario_blocks_spy_conversion_when_dates_differ(self) -> None:
        from app.services.overview.sp500_valuation import (
            calculate_fomc_eps_scenarios,
            calculate_index_scenario,
            calculate_multiple_regime,
        )

        result = calculate_index_scenario(
            multiple_regime=calculate_multiple_regime(monthly_pe_frame(60)),
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

    def test_valuation_collection_job_reports_source_results(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_sp500_valuation_context

        with patch(
            "app.jobs.ingestion_jobs.ensure_sp500_valuation_schemas",
        ), patch(
            "app.jobs.ingestion_jobs.collect_and_store_shiller_monthly_valuation",
            return_value={"rows_written": 60, "source": "shiller"},
        ), patch(
            "app.jobs.ingestion_jobs.collect_and_store_fomc_sep",
            return_value={"rows_written": 12, "source": "federal_reserve_sep", "release_date": "2026-06-17"},
        ), patch(
            "app.jobs.ingestion_jobs.collect_and_store_fomc_sep_history",
            return_value={"rows_written": 48, "source": "federal_reserve_sep", "release_dates": ["2025-06-18", "2025-09-17", "2025-12-10", "2026-03-18"]},
        ), patch(
            "app.jobs.ingestion_jobs.import_and_store_sp500_index_earnings",
            return_value={"rows_written": 8, "source": "sp_index_earnings"},
        ), patch(
            "app.jobs.ingestion_jobs.run_collect_ohlcv",
            return_value={"status": "success", "rows_written": 10, "message": "ok"},
        ):
            result = run_collect_sp500_valuation_context(
                index_earnings_path="fixture.xlsx",
                source_release_date="2026-07-01",
            )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 138)
        self.assertEqual(result["details"]["pipeline_type"], "sp500_valuation_context")
        self.assertTrue(
            any(step["label"] == "Federal Reserve SEP history" for step in result["details"]["steps"])
        )

    def test_sp500_index_earnings_upload_job_reports_economic_cycle_readiness(self) -> None:
        from app.jobs.ingestion_jobs import run_import_sp500_index_earnings_xlsx

        with patch(
            "app.jobs.ingestion_jobs.import_and_store_sp500_index_earnings",
            return_value={
                "rows_written": 16,
                "actual_quarter_count": 8,
                "latest_actual_period_end": "2026-03-31",
                "remaining_quarters": 0,
                "release_date": "2026-05-15",
                "source_ref": "https://www.spglobal.com/spdji/en/documents/additional-material/sp-500-eps-est.xlsx",
            },
        ) as importer:
            result = run_import_sp500_index_earnings_xlsx(
                workbook_content=b"xlsx",
                source_release_date="2026-05-15",
                source_name="sp-500-eps-est.xlsx",
            )

        importer.assert_called_once_with(
            b"xlsx",
            source_release_date="2026-05-15",
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 16)
        self.assertIn("8/8", result["message"])
        self.assertIn("계산할 수 있습니다", result["message"])
        self.assertEqual(result["details"]["remaining_quarters"], 0)
        self.assertNotIn("workbook_content", result["details"])

    def test_overview_automation_includes_daily_sep_vintage_check(self) -> None:
        from app.jobs.overview_automation import OVERVIEW_AUTOMATION_JOB_SPECS

        spec = next(item for item in OVERVIEW_AUTOMATION_JOB_SPECS if item.job_id == "sp500_valuation")

        self.assertEqual(spec.job_name, "collect_sp500_valuation_context")
        self.assertEqual(spec.cadence_minutes, 24 * 60)
        self.assertFalse(spec.market_hours_only)


if __name__ == "__main__":
    unittest.main()
