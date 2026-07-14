from __future__ import annotations

import unittest


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


if __name__ == "__main__":
    unittest.main()
