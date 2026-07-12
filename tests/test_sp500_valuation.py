from __future__ import annotations

import unittest
from unittest.mock import Mock
from unittest.mock import patch

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

    def test_multiple_regime_uses_latest_shiller_per_as_current_marker(self) -> None:
        from app.services.overview.sp500_valuation import calculate_multiple_regime

        result = calculate_multiple_regime(monthly_pe_frame(72))

        self.assertEqual(result["window_months"], 60)
        self.assertEqual(result["sensitivity"]["window_months"], 36)
        self.assertAlmostEqual(result["current_pe"], 28.65)
        self.assertIn(result["bucket"], {"LOW", "NEUTRAL", "HIGH", "EXTREME_HIGH"})
        self.assertEqual(len(result["series"]), 60)
        self.assertEqual(result["current_basis_date"], "2025-12-01")

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
        self.assertEqual(result["rows_written"], 90)
        self.assertEqual(result["details"]["pipeline_type"], "sp500_valuation_context")

    def test_overview_automation_includes_daily_sep_vintage_check(self) -> None:
        from app.jobs.overview_automation import OVERVIEW_AUTOMATION_JOB_SPECS

        spec = next(item for item in OVERVIEW_AUTOMATION_JOB_SPECS if item.job_id == "sp500_valuation")

        self.assertEqual(spec.job_name, "collect_sp500_valuation_context")
        self.assertEqual(spec.cadence_minutes, 24 * 60)
        self.assertFalse(spec.market_hours_only)


if __name__ == "__main__":
    unittest.main()
