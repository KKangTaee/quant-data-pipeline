from __future__ import annotations

import unittest
from unittest.mock import Mock, patch

import pandas as pd


def _quarter(
    *,
    period_end: str,
    available_at: str,
    value: float,
    fiscal_year: int,
    fiscal_quarter: int,
    symbol: str = "NVDA",
) -> dict[str, object]:
    return {
        "symbol": symbol,
        "concept": "us-gaap:EarningsPerShareDiluted",
        "unit": "USD per share",
        "source_period_type": "duration",
        "period_type": "Q",
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "period_end": period_end,
        "report_date": period_end,
        "value": value,
        "available_at": available_at,
    }


class UsStockValuationCalculationTests(unittest.TestCase):
    def test_split_neutral_monthly_pe_keeps_price_and_eps_on_same_share_basis(self) -> None:
        from finance.data.us_stock_valuation import build_monthly_pit_valuation

        statements = [
            _quarter(period_end="2023-06-30", available_at="2023-08-01", value=10.0, fiscal_year=2024, fiscal_quarter=1),
            _quarter(period_end="2023-09-30", available_at="2023-11-01", value=10.0, fiscal_year=2024, fiscal_quarter=2),
            _quarter(period_end="2023-12-31", available_at="2024-02-01", value=10.0, fiscal_year=2024, fiscal_quarter=3),
            _quarter(period_end="2024-03-31", available_at="2024-05-01", value=10.0, fiscal_year=2025, fiscal_quarter=1),
        ]
        prices = [
            {"symbol": "NVDA", "date": "2024-05-31", "close": 400.0, "stock_splits": 0.0},
            {"symbol": "NVDA", "date": "2024-06-10", "close": 40.0, "stock_splits": 10.0},
            {"symbol": "NVDA", "date": "2024-06-28", "close": 40.0, "stock_splits": 0.0},
        ]

        rows = build_monthly_pit_valuation(
            statements,
            prices,
            start_month="2024-05-01",
            end_month="2024-06-30",
        )

        self.assertEqual([row["month"] for row in rows], ["2024-05-01", "2024-06-01"])
        self.assertAlmostEqual(rows[0]["ttm_eps"], 40.0)
        self.assertAlmostEqual(rows[0]["trailing_pe"], 10.0)
        self.assertAlmostEqual(rows[0]["split_factor"], 1.0)
        self.assertAlmostEqual(rows[1]["ttm_eps"], 4.0)
        self.assertAlmostEqual(rows[1]["trailing_pe"], 10.0)
        self.assertAlmostEqual(rows[1]["split_factor"], 10.0)

    def test_monthly_ttm_carries_forward_without_interpolation(self) -> None:
        from finance.data.us_stock_valuation import build_monthly_pit_valuation

        statements = [
            _quarter(period_end="2023-06-30", available_at="2023-08-01", value=1.0, fiscal_year=2023, fiscal_quarter=2, symbol="META"),
            _quarter(period_end="2023-09-30", available_at="2023-11-01", value=1.0, fiscal_year=2023, fiscal_quarter=3, symbol="META"),
            _quarter(period_end="2023-12-31", available_at="2024-02-01", value=1.0, fiscal_year=2023, fiscal_quarter=4, symbol="META"),
            _quarter(period_end="2024-03-31", available_at="2024-03-15", value=1.0, fiscal_year=2024, fiscal_quarter=1, symbol="META"),
        ]
        prices = [
            {"symbol": "META", "date": "2024-03-28", "close": 40.0, "stock_splits": 0.0},
            {"symbol": "META", "date": "2024-04-30", "close": 44.0, "stock_splits": 0.0},
        ]

        rows = build_monthly_pit_valuation(
            statements,
            prices,
            start_month="2024-03-01",
            end_month="2024-04-30",
        )

        self.assertEqual([row["ttm_eps"] for row in rows], [4.0, 4.0])
        self.assertEqual([row["eps_basis_date"] for row in rows], ["2024-03-15", "2024-03-15"])
        self.assertEqual([row["trailing_pe"] for row in rows], [10.0, 11.0])

    def test_monthly_ttm_does_not_use_future_filing(self) -> None:
        from finance.data.us_stock_valuation import build_monthly_pit_valuation

        statements = [
            _quarter(period_end="2023-06-30", available_at="2023-08-01", value=1.0, fiscal_year=2023, fiscal_quarter=2, symbol="AAPL"),
            _quarter(period_end="2023-09-30", available_at="2023-11-01", value=1.0, fiscal_year=2023, fiscal_quarter=3, symbol="AAPL"),
            _quarter(period_end="2023-12-31", available_at="2024-02-01", value=1.0, fiscal_year=2023, fiscal_quarter=4, symbol="AAPL"),
            _quarter(period_end="2024-03-31", available_at="2024-04-01", value=1.0, fiscal_year=2024, fiscal_quarter=1, symbol="AAPL"),
            _quarter(period_end="2024-06-30", available_at="2024-05-01", value=5.0, fiscal_year=2024, fiscal_quarter=2, symbol="AAPL"),
        ]
        prices = [
            {"symbol": "AAPL", "date": "2024-04-30", "close": 40.0, "stock_splits": 0.0},
            {"symbol": "AAPL", "date": "2024-05-31", "close": 48.0, "stock_splits": 0.0},
        ]

        rows = build_monthly_pit_valuation(
            statements,
            prices,
            start_month="2024-04-01",
            end_month="2024-05-31",
        )

        self.assertEqual(rows[0]["ttm_eps"], 4.0)
        self.assertEqual(rows[0]["eps_basis_date"], "2024-04-01")
        self.assertEqual(rows[1]["ttm_eps"], 8.0)
        self.assertEqual(rows[1]["eps_basis_date"], "2024-05-01")

    def test_non_positive_eps_and_missing_price_never_create_pe(self) -> None:
        from finance.data.us_stock_valuation import build_monthly_pit_valuation

        statements = [
            _quarter(period_end="2023-06-30", available_at="2023-08-01", value=-1.0, fiscal_year=2023, fiscal_quarter=2, symbol="LOSS"),
            _quarter(period_end="2023-09-30", available_at="2023-11-01", value=-1.0, fiscal_year=2023, fiscal_quarter=3, symbol="LOSS"),
            _quarter(period_end="2023-12-31", available_at="2024-02-01", value=-1.0, fiscal_year=2023, fiscal_quarter=4, symbol="LOSS"),
            _quarter(period_end="2024-02-29", available_at="2024-03-01", value=-1.0, fiscal_year=2024, fiscal_quarter=1, symbol="LOSS"),
        ]

        rows = build_monthly_pit_valuation(
            statements,
            [{"symbol": "LOSS", "date": "2024-03-28", "close": 20.0, "stock_splits": 0.0}],
            start_month="2024-03-01",
            end_month="2024-04-30",
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["quality"], "non_positive_eps")
        self.assertIsNone(rows[0]["trailing_pe"])
        self.assertEqual(rows[1]["quality"], "missing_price")
        self.assertIsNone(rows[1]["price"])
        self.assertIsNone(rows[1]["trailing_pe"])


class UsStockValuationLoaderTests(unittest.TestCase):
    def test_loader_identity_requires_current_active_stock_and_sec_cik(self) -> None:
        from finance.loaders.us_stock_valuation import load_us_stock_identity

        query_fn = Mock(
            return_value=[
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "exchange": "Nasdaq",
                    "related_cik": 320193,
                    "first_seen_date": "2006-01-03",
                    "last_seen_date": "2026-07-14",
                    "evidence_json": '{"exchange":"Nasdaq"}',
                }
            ]
        )

        result = load_us_stock_identity("aapl", query_fn=query_fn)

        database, sql, params = query_fn.call_args.args
        self.assertEqual(database, "finance_meta")
        self.assertIn("nyse_symbol_lifecycle", sql)
        self.assertIn("kind = 'stock'", sql)
        self.assertIn("listing_status = 'active'", sql)
        self.assertIn("source = 'sec_company_tickers_exchange'", sql)
        self.assertEqual(params, ("AAPL",))
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["cik"], "0000320193")
        self.assertEqual(result["exchange"], "Nasdaq")

    def test_loader_bounds_one_symbol_price_statement_and_sep_queries(self) -> None:
        from finance.loaders.us_stock_valuation import load_us_stock_valuation_inputs

        calls: list[tuple[str, str, tuple[object, ...]]] = []

        def query_fn(database: str, sql: str, params: tuple[object, ...]):
            calls.append((database, sql, params))
            if "nyse_symbol_lifecycle" in sql:
                return [
                    {
                        "symbol": "NVDA",
                        "name": "NVIDIA Corporation",
                        "exchange": "Nasdaq",
                        "related_cik": 1045810,
                        "first_seen_date": "2006-01-03",
                        "last_seen_date": "2026-07-14",
                    }
                ]
            return []

        result = load_us_stock_valuation_inputs(
            "nvda",
            as_of_date="2026-07-14",
            valuation_months=119,
            statement_lookback_months=18,
            query_fn=query_fn,
        )

        by_database = {database: (sql, params) for database, sql, params in calls if database != "finance_meta" or "fomc_sep_projection" in sql}
        price_sql, price_params = next((sql, params) for database, sql, params in calls if database == "finance_price")
        statement_sql, statement_params = next((sql, params) for database, sql, params in calls if database == "finance_fundamental")
        sep_sql, sep_params = next((sql, params) for database, sql, params in calls if "fomc_sep_projection" in sql)

        self.assertIn("timeframe = '1d'", price_sql)
        self.assertIn("close", price_sql)
        self.assertIn("stock_splits", price_sql)
        self.assertEqual(price_params, ("NVDA", "2016-09-01", "2026-07-14"))
        self.assertIn("available_at <= %s", statement_sql)
        self.assertIn("EarningsPerShareDiluted", statement_sql)
        self.assertEqual(statement_params, ("NVDA", "2015-03-01", "2026-07-14"))
        self.assertIn("release_date <= %s", sep_sql)
        self.assertEqual(sep_params, ("2015-03-01", "2026-07-14"))
        self.assertEqual(result["window"]["valuation_start"], "2016-09-01")
        self.assertEqual(result["window"]["statement_start"], "2015-03-01")
        self.assertEqual(result["identity"]["symbol"], "NVDA")
        self.assertEqual(by_database["finance_meta"][1], ("2015-03-01", "2026-07-14"))


def _monthly_points(count: int, *, start: str = "2020-01-01") -> list[dict[str, object]]:
    return [
        {
            "symbol": "AAPL",
            "month": month.strftime("%Y-%m-%d"),
            "price": (15.0 + index / 20.0) * 10.0,
            "price_basis_date": (month + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"),
            "ttm_eps": 10.0,
            "eps_basis_date": (month - pd.DateOffset(days=10)).strftime("%Y-%m-%d"),
            "trailing_pe": 15.0 + index / 20.0,
            "quality": "complete",
        }
        for index, month in enumerate(pd.date_range(start, periods=count, freq="MS"))
    ]


def _quarterly_ttm_points(
    count: int = 16,
    *,
    start: str = "2021-03-31",
) -> list[dict[str, object]]:
    return [
        {
            "period_end": end.strftime("%Y-%m-%d"),
            "available_at": (end + pd.DateOffset(days=35)).strftime("%Y-%m-%d"),
            "ttm_eps": 5.0 * (1.025**index),
        }
        for index, end in enumerate(pd.date_range(start, periods=count, freq="QE-DEC"))
    ]


def _sep_history(
    *,
    start_year: int = 2021,
    end_year: int = 2026,
) -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for target_year in range(start_year, end_year + 1):
        release_date = f"{target_year - 1}-12-15"
        rows.extend(
            [
                {"release_date": release_date, "target_year": target_year, "variable_name": "real_gdp", "statistic_name": "median", "value_pct": 2.0},
                {"release_date": release_date, "target_year": target_year, "variable_name": "pce_inflation", "statistic_name": "median", "value_pct": 2.0},
            ]
        )
    return rows


class UsStockValuationEngineTests(unittest.TestCase):
    def test_multiple_regime_requires_sixty_positive_complete_months_and_keeps_36m_sensitivity(self) -> None:
        from finance.data.us_stock_valuation import calculate_stock_multiple_regime

        insufficient = calculate_stock_multiple_regime(_monthly_points(59))
        ready = calculate_stock_multiple_regime(_monthly_points(60))

        self.assertEqual(insufficient["status"], "INSUFFICIENT_HISTORY")
        self.assertEqual(insufficient["observation_count"], 59)
        self.assertEqual(ready["status"], "READY")
        self.assertEqual(ready["observation_count"], 60)
        self.assertEqual(ready["window_months"], 60)
        self.assertEqual(ready["sensitivity"]["window_months"], 36)
        self.assertGreater(ready["plus_1sigma"], ready["mean_multiple"])
        self.assertLess(ready["minus_1sigma"], ready["mean_multiple"])

    def test_company_excess_growth_uses_only_applicable_sep_and_tukey_clips_outlier(self) -> None:
        from finance.data.us_stock_valuation import calculate_company_excess_growth

        quarters = _quarterly_ttm_points(16)
        quarters[-1]["ttm_eps"] = 100.0
        sep_rows = _sep_history() + [
            {"release_date": "2027-01-01", "target_year": 2025, "variable_name": "real_gdp", "statistic_name": "median", "value_pct": 99.0},
            {"release_date": "2027-01-01", "target_year": 2025, "variable_name": "pce_inflation", "statistic_name": "median", "value_pct": 99.0},
        ]

        result = calculate_company_excess_growth(
            quarters,
            sep_rows,
            as_of_date="2025-12-31",
        )

        self.assertEqual(result["status"], "READY")
        self.assertGreaterEqual(result["observation_count"], 8)
        self.assertTrue(
            all(point["sep_release_date"] <= point["available_at"] for point in result["observations"])
        )
        self.assertLess(result["clipped_max_pct"], result["raw_max_pct"])
        self.assertLessEqual(result["p25_pct"], result["p50_pct"])
        self.assertLessEqual(result["p50_pct"], result["p75_pct"])

    def test_company_excess_growth_requires_eight_positive_to_positive_yoy_observations(self) -> None:
        from finance.data.us_stock_valuation import calculate_company_excess_growth

        result = calculate_company_excess_growth(
            _quarterly_ttm_points(11),
            _sep_history(),
            as_of_date="2025-12-31",
        )

        self.assertEqual(result["status"], "INSUFFICIENT_HISTORY")
        self.assertEqual(result["observation_count"], 7)

    def test_stock_scenarios_combine_current_macro_excess_percentiles_and_multiple_anchors(self) -> None:
        from finance.data.us_stock_valuation import calculate_stock_scenarios

        result = calculate_stock_scenarios(
            10.0,
            {"status": "READY", "minus_1sigma": 15.0, "mean_multiple": 20.0, "plus_1sigma": 25.0},
            {"status": "READY", "current_macro_pct": 4.0, "p25_pct": -2.0, "p50_pct": 0.0, "p75_pct": 2.0},
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["conservative"]["growth_pct"], 2.0)
        self.assertEqual(result["baseline"]["growth_pct"], 4.0)
        self.assertEqual(result["optimistic"]["growth_pct"], 6.0)
        self.assertAlmostEqual(result["conservative"]["price"], 153.0)
        self.assertAlmostEqual(result["baseline"]["price"], 208.0)
        self.assertAlmostEqual(result["optimistic"]["price"], 265.0)

    def test_historical_stock_scenario_requires_complete_visible_points_after_60m_warmup(self) -> None:
        from finance.data.us_stock_valuation import calculate_historical_stock_scenario

        ready = calculate_historical_stock_scenario(
            _monthly_points(71),
            _quarterly_ttm_points(20),
            _sep_history(),
            visible_months=12,
        )
        insufficient = calculate_historical_stock_scenario(
            _monthly_points(70),
            _quarterly_ttm_points(20),
            _sep_history(),
            visible_months=12,
        )

        self.assertEqual(ready["status"], "READY")
        self.assertEqual(ready["observation_count"], 12)
        self.assertEqual(ready["required_history_months"], 71)
        self.assertEqual(insufficient["status"], "INSUFFICIENT_HISTORY")
        self.assertEqual(insufficient["reason_code"], "INSUFFICIENT_ROLLING_PER_WARMUP")

    def test_readiness_distinguishes_collectable_from_structural_not_applicable(self) -> None:
        from finance.data.us_stock_valuation import classify_us_stock_readiness

        identity = {"instrument_type": "common_stock", "adr_unit_status": "not_adr"}
        ready_rows = _monthly_points(60)
        cases = [
            ("READY", {"requested_months": 60, "price_missing": False, "statement_missing": False, "listing_months": 200}, ready_rows, {"status": "READY"}),
            ("COLLECTABLE", {"requested_months": 60, "price_missing": True, "statement_missing": False, "listing_months": 200}, ready_rows, {"status": "READY"}),
            ("COLLECTABLE", {"requested_months": 60, "price_missing": False, "statement_missing": True, "listing_months": 200}, ready_rows, {"status": "READY"}),
            ("NOT_APPLICABLE", {"requested_months": 60, "price_missing": True, "statement_missing": False, "listing_months": 20}, ready_rows, {"status": "READY"}),
            ("NOT_APPLICABLE", {"requested_months": 60, "price_missing": False, "statement_missing": False, "listing_months": 200}, [{**ready_rows[-1], "ttm_eps": -1.0, "trailing_pe": None, "quality": "non_positive_eps"}], {"status": "READY"}),
        ]
        for expected, coverage, monthly_rows, growth in cases:
            with self.subTest(expected=expected, coverage=coverage):
                result = classify_us_stock_readiness(identity, coverage, monthly_rows, growth)
                self.assertEqual(result["status"], expected)

        adr = classify_us_stock_readiness(
            {"instrument_type": "common_stock", "adr_unit_status": "unverified"},
            {"requested_months": 60, "price_missing": False, "statement_missing": False, "listing_months": 200},
            ready_rows,
            {"status": "READY"},
        )
        self.assertEqual(adr["status"], "NOT_APPLICABLE")
        self.assertEqual(adr["reason_code"], "ADR_UNIT_UNVERIFIED")


def _ready_loaded_inputs() -> dict[str, object]:
    return {
        "identity": {
            "symbol": "AAPL",
            "name": "Apple Inc.",
            "exchange": "Nasdaq",
            "cik": "0000320193",
            "instrument_type": "common_stock",
            "adr_unit_status": "not_adr",
        },
        "price_rows": [],
        "statement_rows": [],
        "sep_rows": _sep_history(start_year=2013, end_year=2027),
        "monthly_rows": _monthly_points(119, start="2016-01-01"),
        "quarterly_ttm_rows": _quarterly_ttm_points(52, start="2013-03-31"),
        "window": {
            "valuation_start": "2016-01-01",
            "statement_start": "2014-07-01",
            "as_of_date": "2025-11-30",
            "valuation_months": 119,
        },
        "coverage": {
            "requested_months": 119,
            "price_missing": False,
            "statement_missing": False,
            "listing_months": 240,
            "latest_price_date": "2025-11-28",
            "latest_statement_available_at": "2025-11-05",
        },
    }


class UsStockValuationServiceTests(unittest.TestCase):
    def test_service_not_selected_does_not_invoke_loader(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        with patch("app.services.overview.us_stock_valuation.load_us_stock_valuation_inputs") as loader:
            result = build_us_stock_valuation_read_model()

        loader.assert_not_called()
        self.assertEqual(result["status"], "NOT_SELECTED")
        self.assertEqual(result["instrument"]["id"], "us_stock")
        self.assertEqual(result["multiple_regime"]["status"], "NOT_SELECTED")

    def test_service_ready_payload_is_json_safe_and_exposes_stock_evidence(self) -> None:
        import json

        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        result = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=_ready_loaded_inputs(),
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["selection"]["symbol"], "AAPL")
        self.assertEqual(result["selection"]["exchange"], "Nasdaq")
        self.assertEqual(result["multiple_regime"]["observation_count"], 60)
        self.assertEqual(result["earnings_scenario"]["status"], "READY")
        self.assertEqual(result["index_scenario"]["status"], "READY")
        self.assertEqual(set(result["index_scenario"]["history_options"]), {"1y", "3y", "5y"})
        self.assertIn("FOMC", result["earnings_scenario"]["methodology"])
        self.assertIn("상대가치", result["index_scenario"]["label"])
        json.dumps(result, ensure_ascii=False)

    def test_service_collectable_exposes_exact_action_but_not_applicable_does_not(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        collectable_inputs = _ready_loaded_inputs()
        collectable_inputs["coverage"] = {
            **collectable_inputs["coverage"],
            "price_missing": True,
            "price_missing_range": {"start": "2021-01-01", "end": "2021-06-30"},
        }
        collectable = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=collectable_inputs,
        )

        loss_inputs = _ready_loaded_inputs()
        loss_inputs["monthly_rows"] = [
            {
                **loss_inputs["monthly_rows"][-1],
                "ttm_eps": -1.0,
                "trailing_pe": None,
                "quality": "non_positive_eps",
            }
        ]
        loss = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=loss_inputs,
        )

        self.assertEqual(collectable["status"], "COLLECTABLE")
        self.assertEqual(collectable["collection_action"]["id"], "collect_us_stock_valuation")
        self.assertEqual(
            collectable["collection_action"]["missing_ranges"]["prices"],
            {"start": "2021-01-01", "end": "2021-06-30"},
        )
        self.assertEqual(loss["status"], "NOT_APPLICABLE")
        self.assertNotIn("collection_action", loss)

    def test_service_schema_error_returns_stable_error_shape(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        broken = _ready_loaded_inputs()
        broken["identity"] = None

        result = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=broken,
        )

        self.assertEqual(result["status"], "ERROR")
        self.assertEqual(result["multiple_regime"]["status"], "ERROR")
        self.assertEqual(result["earnings_scenario"]["status"], "ERROR")
        self.assertEqual(result["index_scenario"]["status"], "ERROR")


if __name__ == "__main__":
    unittest.main()
