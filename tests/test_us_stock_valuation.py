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

    def test_split_year_normalizes_quarters_before_deriving_q4(self) -> None:
        from finance.data.us_stock_valuation import build_monthly_pit_valuation

        statements = [
            _quarter(
                period_end="2024-04-28",
                available_at="2024-05-29",
                value=5.98,
                fiscal_year=2025,
                fiscal_quarter=1,
            ),
            _quarter(
                period_end="2024-07-28",
                available_at="2024-08-28",
                value=0.67,
                fiscal_year=2025,
                fiscal_quarter=2,
            ),
            _quarter(
                period_end="2024-10-27",
                available_at="2024-11-20",
                value=0.78,
                fiscal_year=2025,
                fiscal_quarter=3,
            ),
            {
                "symbol": "NVDA",
                "concept": "us-gaap:EarningsPerShareDiluted",
                "unit": "USD per share",
                "source_period_type": "duration",
                "period_type": "FY",
                "fiscal_year": 2025,
                "fiscal_quarter": None,
                "period_end": "2025-01-26",
                "report_date": "2025-01-26",
                "value": 2.94,
                "available_at": "2025-02-26",
            },
        ]
        prices = [
            {"symbol": "NVDA", "date": "2024-05-31", "close": 1_100.0, "stock_splits": 0.0},
            {"symbol": "NVDA", "date": "2024-06-10", "close": 121.0, "stock_splits": 10.0},
            {"symbol": "NVDA", "date": "2025-02-28", "close": 120.0, "stock_splits": 0.0},
        ]

        row = build_monthly_pit_valuation(
            statements,
            prices,
            start_month="2025-02-01",
            end_month="2025-02-28",
        )[0]

        self.assertAlmostEqual(row["quarters"][-1]["eps"], 0.892)
        self.assertAlmostEqual(row["ttm_eps"], 2.94)
        self.assertAlmostEqual(row["trailing_pe"], 120.0 / 2.94)

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
    def test_search_is_db_only_and_ignores_empty_or_one_character_query(self) -> None:
        from finance.loaders.us_stock_valuation import search_us_common_stocks

        query_fn = Mock()

        self.assertEqual(search_us_common_stocks("", query_fn=query_fn), [])
        self.assertEqual(search_us_common_stocks("a", query_fn=query_fn), [])
        query_fn.assert_not_called()

    def test_search_ranks_ticker_prefix_before_company_name_match(self) -> None:
        from finance.loaders.us_stock_valuation import search_us_common_stocks

        query_fn = Mock(
            return_value=[
                {"symbol": "ZZZ", "name": "Apple Hospitality REIT", "exchange": "NYSE", "related_cik": 1, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
                {"symbol": "AAPL", "name": "Apple Inc.", "exchange": "Nasdaq", "related_cik": 320193, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
                {"symbol": "APLE", "name": "Apple Hospitality REIT, Inc.", "exchange": "NYSE", "related_cik": 1418121, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
            ]
        )

        result = search_us_common_stocks("apple", limit=12, query_fn=query_fn)

        database, sql, params = query_fn.call_args.args
        self.assertEqual(database, "finance_meta")
        self.assertIn("nyse_symbol_lifecycle", sql)
        self.assertEqual(params[:2], ("APPLE%", "%APPLE%"))
        self.assertEqual([row["symbol"] for row in result], ["AAPL", "APLE", "ZZZ"])
        self.assertTrue(all(row["cik"] for row in result))

    def test_search_excludes_non_common_and_inactive_security_rows(self) -> None:
        from finance.loaders.us_stock_valuation import search_us_common_stocks

        rows = [
            {"symbol": "GOOD", "name": "Good Company Common Stock", "exchange": "NYSE", "related_cik": 100, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
            {"symbol": "ETF", "name": "Example ETF", "exchange": "Nasdaq", "related_cik": 101, "kind": "etf", "listing_status": "active", "quote_type": "ETF"},
            {"symbol": "PREF", "name": "Example Preferred Stock", "exchange": "NYSE", "related_cik": 102, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
            {"symbol": "WARR", "name": "Example Warrant", "exchange": "Nasdaq", "related_cik": 103, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
            {"symbol": "UNIT", "name": "Example Unit", "exchange": "NYSE American", "related_cik": 104, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
            {"symbol": "RIGHT", "name": "Example Rights", "exchange": "NYSE", "related_cik": 105, "kind": "stock", "listing_status": "active", "quote_type": "EQUITY"},
            {"symbol": "OLD", "name": "Old Company", "exchange": "NYSE", "related_cik": 106, "kind": "stock", "listing_status": "inactive", "quote_type": "EQUITY"},
        ]

        result = search_us_common_stocks(
            "example",
            query_fn=Mock(return_value=rows),
        )

        self.assertEqual([row["symbol"] for row in result], ["GOOD"])

    def test_search_keeps_active_common_stock_when_sec_cik_snapshot_is_missing(self) -> None:
        from finance.loaders.us_stock_valuation import search_us_common_stocks

        query_fn = Mock(
            return_value=[
                {
                    "symbol": "AAPL",
                    "name": "Apple Inc.",
                    "exchange": "NMS",
                    "related_cik": None,
                    "kind": "stock",
                    "listing_status": "active",
                    "quote_type": "EQUITY",
                    "profile_status": "active",
                    "source": "nyse_listings_directory",
                }
            ]
        )

        result = search_us_common_stocks("apple", query_fn=query_fn)

        self.assertEqual(result[0]["symbol"], "AAPL")
        self.assertEqual(result[0]["exchange"], "Nasdaq")
        self.assertIsNone(result[0]["cik"])
        self.assertEqual(result[0]["cik_link_status"], "missing")
        self.assertNotIn(
            "AND l.source = 'sec_company_tickers_exchange'",
            query_fn.call_args.args[1],
        )

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
        self.assertEqual(params, ("AAPL",))
        self.assertEqual(result["symbol"], "AAPL")
        self.assertEqual(result["cik"], "0000320193")
        self.assertEqual(result["exchange"], "Nasdaq")

    def test_loader_identity_uses_current_profile_without_sec_cik_for_read_only_evaluation(self) -> None:
        from finance.loaders.us_stock_valuation import load_us_stock_identity

        query_fn = Mock(
            return_value=[
                {
                    "symbol": "NVDA",
                    "name": "NVIDIA Corporation",
                    "exchange": "NMS",
                    "related_cik": None,
                    "first_seen_date": "2026-05-31",
                    "last_seen_date": "2026-05-31",
                    "source": "nyse_listings_directory",
                    "quote_type": "EQUITY",
                    "profile_status": "active",
                }
            ]
        )

        result = load_us_stock_identity("NVDA", query_fn=query_fn)

        self.assertEqual(result["symbol"], "NVDA")
        self.assertEqual(result["exchange"], "Nasdaq")
        self.assertIsNone(result["cik"])
        self.assertEqual(result["cik_link_status"], "missing")
        self.assertEqual(result["identity_source"], "nyse_listings_directory")

    def test_loader_marks_non_us_issuer_share_unit_unverified(self) -> None:
        from finance.loaders.us_stock_valuation import load_us_stock_identity

        query_fn = Mock(
            return_value=[
                {
                    "symbol": "TSM",
                    "name": "Taiwan Semiconductor Manufacturing Company Limited",
                    "exchange": "NYQ",
                    "country": "Taiwan",
                    "related_cik": None,
                    "source": "nyse_listings_directory",
                    "quote_type": "EQUITY",
                    "profile_status": "active",
                }
            ]
        )

        result = load_us_stock_identity("TSM", query_fn=query_fn)

        self.assertEqual(result["exchange"], "NYSE")
        self.assertEqual(result["country"], "Taiwan")
        self.assertEqual(result["adr_unit_status"], "unverified")

    def test_listing_months_use_stored_price_history_not_recent_snapshot_date(self) -> None:
        from finance.loaders.us_stock_valuation import _coverage

        prices = [
            {"date": month.strftime("%Y-%m-%d"), "close": 100.0}
            for month in pd.date_range("2021-08-01", periods=60, freq="MS")
        ]
        result = _coverage(
            identity={"first_seen_date": "2026-05-31"},
            prices=prices,
            statements=[],
            valuation_months=60,
            as_of=pd.Timestamp("2026-07-14"),
        )

        self.assertEqual(result["listing_months"], 60)

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

        identity = {
            "instrument_type": "common_stock",
            "adr_unit_status": "not_adr",
            "cik": "0000320193",
        }
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

    def test_growth_gap_blocks_scenario_but_keeps_main_pe_ready(self) -> None:
        from finance.data.us_stock_valuation import classify_us_stock_readiness

        result = classify_us_stock_readiness(
            {
                "instrument_type": "common_stock",
                "adr_unit_status": "not_adr",
                "cik": "0000002488",
            },
            {
                "requested_months": 60,
                "price_missing": False,
                "statement_missing": False,
                "listing_months": 200,
            },
            _monthly_points(60),
            {"status": "INSUFFICIENT_HISTORY", "observation_count": 7},
        )

        self.assertEqual(result["status"], "READY")
        self.assertIsNone(result["reason_code"])


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
    def test_service_search_reads_db_results_without_loading_valuation(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        search_result = [
            {
                "symbol": "AAPL",
                "name": "Apple Inc.",
                "exchange": "Nasdaq",
                "cik": "0000320193",
                "instrument_type": "common_stock",
                "adr_unit_status": "not_adr",
            }
        ]
        with patch(
            "app.services.overview.us_stock_valuation.search_us_common_stocks",
            return_value=search_result,
        ) as search, patch(
            "app.services.overview.us_stock_valuation.load_us_stock_valuation_inputs"
        ) as loader:
            result = build_us_stock_valuation_read_model(search_query="apple")

        search.assert_called_once_with("apple")
        loader.assert_not_called()
        self.assertEqual(result["status"], "NOT_SELECTED")
        self.assertEqual(result["search"], {"query": "apple", "results": search_result})

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

    def test_service_keeps_graph_one_ready_when_growth_history_only_blocks_graph_two(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        inputs = _ready_loaded_inputs()
        inputs["quarterly_ttm_rows"] = _quarterly_ttm_points(
            11,
            start="2023-03-31",
        )

        result = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=inputs,
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(result["multiple_regime"]["status"], "READY")
        self.assertEqual(result["earnings_scenario"]["status"], "BLOCKED")
        self.assertEqual(
            result["earnings_scenario"]["reason_code"],
            "INSUFFICIENT_GROWTH_HISTORY",
        )
        self.assertEqual(result["earnings_scenario"]["observation_count"], 7)
        self.assertEqual(result["earnings_scenario"]["required_observations"], 8)
        self.assertEqual(result["index_scenario"]["status"], "BLOCKED")
        self.assertIn("7/8", result["index_scenario"]["reason"])

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

    def test_service_main_ready_gate_does_not_require_all_119_history_months(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        inputs = _ready_loaded_inputs()
        inputs["coverage"] = {
            **inputs["coverage"],
            "price_months": 60,
            "price_missing": True,
        }

        result = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=inputs,
        )

        self.assertEqual(result["status"], "READY")
        self.assertNotIn("collection_action", result)

    def test_service_raw_gap_without_cik_link_collects_identity_first(self) -> None:
        from app.services.overview.us_stock_valuation import build_us_stock_valuation_read_model

        inputs = _ready_loaded_inputs()
        inputs["identity"] = {**inputs["identity"], "cik": None}
        inputs["coverage"] = {**inputs["coverage"], "price_missing": True}

        result = build_us_stock_valuation_read_model(
            selected_symbol="AAPL",
            loaded_inputs=inputs,
        )

        self.assertEqual(result["status"], "COLLECTABLE")
        self.assertEqual(result["readiness"]["reason_code"], "RAW_DATA_GAP")
        self.assertEqual(
            result["readiness"]["collection_scopes"],
            ["sec_identity", "prices"],
        )
        self.assertEqual(
            result["collection_action"]["scopes"],
            ["sec_identity", "prices"],
        )

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


class UsStockValuationCollectionTests(unittest.TestCase):
    def test_preflight_distinguishes_exact_raw_gaps_from_structural_short_listing(self) -> None:
        from finance.loaders.us_stock_valuation import build_us_stock_valuation_collection_plan

        monthly = _monthly_points(60, start="2021-08-01")
        monthly[5] = {**monthly[5], "price": None, "price_basis_date": None, "trailing_pe": None, "quality": "missing_price"}
        monthly[8] = {**monthly[8], "ttm_eps": None, "eps_basis_date": None, "trailing_pe": None, "quality": "insufficient_eps"}
        loaded = {
            "identity": _ready_loaded_inputs()["identity"],
            "monthly_rows": monthly,
            "window": {
                "valuation_start": "2016-09-01",
                "statement_start": "2015-03-01",
                "as_of_date": "2026-07-14",
                "valuation_months": 119,
            },
            "coverage": {"listing_months": 240},
        }

        collectable = build_us_stock_valuation_collection_plan(
            "AAPL",
            loaded_inputs=loaded,
        )
        short = build_us_stock_valuation_collection_plan(
            "AAPL",
            loaded_inputs={**loaded, "coverage": {"listing_months": 20}},
        )

        self.assertEqual(collectable["status"], "COLLECTABLE")
        self.assertEqual(collectable["scopes"], ["prices", "sec_statements"])
        self.assertEqual(
            collectable["missing_ranges"]["prices"],
            {"start": "2022-01-01", "end": "2022-01-31"},
        )
        self.assertEqual(
            collectable["missing_ranges"]["sec_statements"],
            {"start": "2015-03-01", "end": "2026-07-14"},
        )
        self.assertEqual(short["status"], "NOT_APPLICABLE")
        self.assertEqual(short["reason_code"], "STRUCTURALLY_SHORT_LISTING")
        self.assertEqual(short["scopes"], [])

    def test_preflight_negative_eps_is_not_collectable_and_complete_inputs_are_ready(self) -> None:
        from finance.loaders.us_stock_valuation import build_us_stock_valuation_collection_plan

        ready_inputs = _ready_loaded_inputs()
        ready = build_us_stock_valuation_collection_plan("AAPL", loaded_inputs=ready_inputs)
        negative_rows = list(ready_inputs["monthly_rows"])
        negative_rows[-1] = {
            **negative_rows[-1],
            "ttm_eps": -1.0,
            "trailing_pe": None,
            "quality": "non_positive_eps",
        }
        negative = build_us_stock_valuation_collection_plan(
            "AAPL",
            loaded_inputs={**ready_inputs, "monthly_rows": negative_rows},
        )

        self.assertEqual(ready["status"], "READY")
        self.assertEqual(ready["scopes"], [])
        self.assertEqual(negative["status"], "NOT_APPLICABLE")
        self.assertEqual(negative["reason_code"], "NON_POSITIVE_EPS")
        self.assertEqual(negative["scopes"], [])

    def test_preflight_missing_raw_data_without_cik_link_collects_identity_first(self) -> None:
        from finance.loaders.us_stock_valuation import build_us_stock_valuation_collection_plan

        loaded = _ready_loaded_inputs()
        loaded["identity"] = {**loaded["identity"], "cik": None}
        loaded["monthly_rows"] = [
            {**row, "price": None, "trailing_pe": None, "quality": "missing_price"}
            if index == len(loaded["monthly_rows"]) - 1
            else row
            for index, row in enumerate(loaded["monthly_rows"])
        ]

        result = build_us_stock_valuation_collection_plan(
            "AAPL",
            loaded_inputs=loaded,
        )

        self.assertEqual(result["status"], "COLLECTABLE")
        self.assertEqual(result["reason_code"], "RAW_DATA_GAP")
        self.assertEqual(result["scopes"], ["sec_identity", "prices"])

    def test_overview_collection_resolves_missing_cik_before_selected_raw_scopes(self) -> None:
        from app.jobs.overview_actions import run_overview_us_stock_valuation_collection

        before = {
            "status": "COLLECTABLE",
            "identity": {"symbol": "AAPL", "cik": None},
            "scopes": ["sec_identity", "prices"],
            "missing_ranges": {
                "prices": {"start": "2021-01-01", "end": "2021-06-30"}
            },
        }
        linked = {
            **before,
            "identity": {"symbol": "AAPL", "cik": "0000320193"},
            "scopes": ["prices"],
        }
        ready = {
            "status": "READY",
            "identity": linked["identity"],
            "scopes": [],
            "missing_ranges": {},
        }
        plan_builder = Mock(side_effect=[before, linked, ready])
        identity_runner = Mock(
            return_value={"status": "success", "rows_written": 1, "message": "linked"}
        )
        collection_runner = Mock(
            return_value={
                "job_name": "collect_us_stock_valuation_inputs",
                "status": "success",
                "rows_written": 120,
                "failed_symbols": [],
                "message": "stored",
                "details": {},
            }
        )
        progress = Mock()

        result = run_overview_us_stock_valuation_collection(
            "AAPL",
            progress_callback=progress,
            plan_builder=plan_builder,
            identity_runner=identity_runner,
            collection_runner=collection_runner,
        )

        identity_runner.assert_called_once_with(
            ["AAPL"],
            progress_callback=None,
        )
        collection_runner.assert_called_once_with(
            "AAPL",
            cik="0000320193",
            identity_cik="0000320193",
            price_start="2021-01-01",
            price_end="2021-06-30",
            collect_prices=True,
            collect_statements=False,
            progress_callback=progress,
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 121)
        self.assertIn({"event": "stage", "stage": "identity", "symbol": "AAPL"}, [call.args[0] for call in progress.call_args_list])

    def test_selected_symbol_collection_runs_exact_scopes_synchronously(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_us_stock_valuation_inputs

        price_runner = Mock(return_value={"status": "success", "rows_written": 120, "failed_symbols": []})
        statement_runner = Mock(return_value={"status": "success", "rows_written": 48, "failed_symbols": []})
        events: list[dict[str, object]] = []

        result = run_collect_us_stock_valuation_inputs(
            "AAPL",
            cik="0000320193",
            identity_cik="0000320193",
            price_start="2021-01-01",
            price_end="2021-06-30",
            collect_prices=True,
            collect_statements=True,
            progress_callback=events.append,
            price_runner=price_runner,
            statement_runner=statement_runner,
        )

        price_runner.assert_called_once_with(
            ["AAPL"],
            start="2021-01-01",
            end="2021-07-01",
            interval="1d",
            execution_profile="managed_safe",
        )
        statement_runner.assert_called_once_with(
            ["AAPL"],
            freq="quarterly",
            periods=0,
            period="quarterly",
        )
        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 168)
        self.assertEqual(
            [event["stage"] for event in events],
            ["preflight", "prices", "sec", "complete"],
        )

    def test_selected_symbol_collection_rejects_cik_mismatch_before_provider_calls(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_us_stock_valuation_inputs

        price_runner = Mock()
        statement_runner = Mock()

        result = run_collect_us_stock_valuation_inputs(
            "AAPL",
            cik="0000320193",
            identity_cik="0000000001",
            price_start="2021-01-01",
            price_end="2021-06-30",
            collect_prices=True,
            collect_statements=True,
            price_runner=price_runner,
            statement_runner=statement_runner,
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("CIK", result["message"])
        price_runner.assert_not_called()
        statement_runner.assert_not_called()

    def test_selected_symbol_collection_rejects_missing_cik_before_provider_calls(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_us_stock_valuation_inputs

        price_runner = Mock()
        statement_runner = Mock()

        result = run_collect_us_stock_valuation_inputs(
            "AAPL",
            cik="",
            identity_cik="",
            price_start="2021-01-01",
            price_end="2021-06-30",
            collect_prices=True,
            collect_statements=True,
            price_runner=price_runner,
            statement_runner=statement_runner,
        )

        self.assertEqual(result["status"], "failed")
        self.assertIn("CIK", result["message"])
        price_runner.assert_not_called()
        statement_runner.assert_not_called()

    def test_overview_collection_rechecks_plan_and_narrows_retry_scope(self) -> None:
        from app.jobs.overview_actions import run_overview_us_stock_valuation_collection

        before = {
            "status": "COLLECTABLE",
            "identity": {"symbol": "AAPL", "cik": "0000320193"},
            "scopes": ["prices", "sec_statements"],
            "missing_ranges": {
                "prices": {"start": "2021-01-01", "end": "2021-06-30"},
                "sec_statements": {"start": "2020-01-01", "end": "2026-07-14"},
            },
        }
        after = {
            "status": "COLLECTABLE",
            "identity": before["identity"],
            "scopes": ["sec_statements"],
            "missing_ranges": {"sec_statements": before["missing_ranges"]["sec_statements"]},
        }
        plan_builder = Mock(side_effect=[before, after])
        collector = Mock(
            return_value={
                "status": "partial_success",
                "rows_written": 120,
                "failed_symbols": [],
                "message": "price stored; SEC remains",
                "details": {},
            }
        )

        result = run_overview_us_stock_valuation_collection(
            "AAPL",
            plan_builder=plan_builder,
            collection_runner=collector,
        )

        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["details"]["after"]["scopes"], ["sec_statements"])
        collector.assert_called_once_with(
            "AAPL",
            cik="0000320193",
            identity_cik="0000320193",
            price_start="2021-01-01",
            price_end="2021-06-30",
            collect_prices=True,
            collect_statements=True,
            progress_callback=None,
        )

    def test_overview_collection_resume_skips_satisfied_price_scope_and_ready_is_noop(self) -> None:
        from app.jobs.overview_actions import run_overview_us_stock_valuation_collection

        statement_only = {
            "status": "COLLECTABLE",
            "identity": {"symbol": "AAPL", "cik": "0000320193"},
            "scopes": ["sec_statements"],
            "missing_ranges": {
                "sec_statements": {"start": "2020-01-01", "end": "2026-07-14"}
            },
        }
        ready = {
            "status": "READY",
            "identity": statement_only["identity"],
            "scopes": [],
            "missing_ranges": {},
        }
        collector = Mock(
            return_value={
                "job_name": "collect_us_stock_valuation_inputs",
                "status": "success",
                "rows_written": 48,
                "failed_symbols": [],
                "message": "ok",
                "details": {},
            }
        )

        resumed = run_overview_us_stock_valuation_collection(
            "AAPL",
            plan_builder=Mock(side_effect=[statement_only, ready]),
            collection_runner=collector,
        )
        noop_collector = Mock()
        noop = run_overview_us_stock_valuation_collection(
            "AAPL",
            plan_builder=Mock(return_value=ready),
            collection_runner=noop_collector,
        )

        collector.assert_called_once_with(
            "AAPL",
            cik="0000320193",
            identity_cik="0000320193",
            price_start=None,
            price_end=None,
            collect_prices=False,
            collect_statements=True,
            progress_callback=None,
        )
        self.assertEqual(resumed["status"], "success")
        noop_collector.assert_not_called()
        self.assertEqual(noop["status"], "success")
        self.assertEqual(noop["rows_written"], 0)


if __name__ == "__main__":
    unittest.main()
