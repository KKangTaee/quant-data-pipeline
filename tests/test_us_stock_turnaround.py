from __future__ import annotations

import unittest


def _fact(
    *,
    value: float,
    period_start: str | None,
    period_end: str,
    available_at: str,
    fiscal_year: int,
    fiscal_quarter: int | None,
    period_type: str = "Q",
    source_period_type: str = "duration",
    concept: str = "us-gaap:Revenues",
    unit: str = "USD",
    report_date: str | None = None,
    accession_no: str | None = None,
    symbol: str = "RIVN",
) -> dict[str, object]:
    return {
        "symbol": symbol,
        "concept": concept,
        "unit": unit,
        "source_period_type": source_period_type,
        "period_type": period_type,
        "fiscal_year": fiscal_year,
        "fiscal_quarter": fiscal_quarter,
        "period_start": period_start,
        "period_end": period_end,
        "report_date": report_date or period_end,
        "value": value,
        "available_at": available_at,
        "form_type": "10-K" if period_type == "FY" else "10-Q",
        "accession_no": accession_no or f"{fiscal_year}-{fiscal_quarter or 'FY'}",
        "source": "edgar",
    }


class TurnaroundQuarterResolverTests(unittest.TestCase):
    def test_resolver_builds_direct_q1_and_cumulative_q2_q3_q4(self) -> None:
        from finance.data.us_stock_turnaround import resolve_discrete_quarters

        rows = [
            _fact(
                value=100.0,
                period_start="2024-01-01",
                period_end="2024-03-31",
                available_at="2024-05-10",
                fiscal_year=2024,
                fiscal_quarter=1,
            ),
            _fact(
                value=250.0,
                period_start="2024-01-01",
                period_end="2024-06-30",
                available_at="2024-08-09",
                fiscal_year=2024,
                fiscal_quarter=2,
            ),
            _fact(
                value=390.0,
                period_start="2024-01-01",
                period_end="2024-09-30",
                available_at="2024-11-08",
                fiscal_year=2024,
                fiscal_quarter=3,
            ),
            _fact(
                value=540.0,
                period_start="2024-01-01",
                period_end="2024-12-31",
                available_at="2025-02-20",
                fiscal_year=2024,
                fiscal_quarter=None,
                period_type="FY",
            ),
        ]

        resolved = resolve_discrete_quarters(
            rows,
            metric="revenue",
            concepts=("us-gaap:Revenues",),
            units=("USD",),
            as_of_date="2025-03-01",
        )

        self.assertEqual([row["fiscal_quarter"] for row in resolved], [1, 2, 3, 4])
        self.assertEqual([row["value"] for row in resolved], [100.0, 150.0, 140.0, 150.0])
        self.assertEqual(
            [row["derivation"] for row in resolved],
            ["reported_quarter", "h1_minus_q1", "nine_months_minus_h1", "fy_minus_q1_q2_q3"],
        )
        self.assertEqual(
            [row["available_at"] for row in resolved],
            ["2024-05-10", "2024-08-09", "2024-11-08", "2025-02-20"],
        )
        self.assertEqual(len(resolved[-1]["provenance"]["operands"]), 4)

    def test_primary_direct_quarter_wins_over_cumulative_derivation(self) -> None:
        from finance.data.us_stock_turnaround import resolve_discrete_quarters

        rows = [
            _fact(
                value=100.0,
                period_start="2024-01-01",
                period_end="2024-03-31",
                available_at="2024-05-10",
                fiscal_year=2024,
                fiscal_quarter=1,
            ),
            _fact(
                value=250.0,
                period_start="2024-01-01",
                period_end="2024-06-30",
                available_at="2024-08-09",
                fiscal_year=2024,
                fiscal_quarter=2,
                accession_no="2024-Q2",
            ),
            _fact(
                value=155.0,
                period_start="2024-04-01",
                period_end="2024-06-30",
                available_at="2024-08-09",
                fiscal_year=2024,
                fiscal_quarter=2,
                accession_no="2024-Q2",
            ),
        ]

        resolved = resolve_discrete_quarters(
            rows,
            metric="revenue",
            concepts=("us-gaap:Revenues",),
            units=("USD",),
            as_of_date="2024-08-31",
        )

        q2_rows = [row for row in resolved if row["fiscal_quarter"] == 2]
        self.assertEqual(len(q2_rows), 1)
        q2 = q2_rows[0]
        self.assertEqual(q2["value"], 155.0)
        self.assertEqual(q2["derivation"], "reported_quarter")

    def test_later_comparative_fact_does_not_overwrite_primary_quarter(self) -> None:
        from finance.data.us_stock_turnaround import resolve_discrete_quarters

        rows = [
            _fact(
                value=100.0,
                period_start="2024-01-01",
                period_end="2024-03-31",
                available_at="2024-05-01",
                fiscal_year=2024,
                fiscal_quarter=1,
                accession_no="primary-2024-q1",
            ),
            _fact(
                value=120.0,
                period_start="2024-01-01",
                period_end="2024-03-31",
                available_at="2025-05-01",
                fiscal_year=2024,
                fiscal_quarter=1,
                report_date="2025-03-31",
                accession_no="comparative-2025-q1",
            ),
        ]

        resolved = resolve_discrete_quarters(
            rows,
            metric="revenue",
            concepts=("us-gaap:Revenues",),
            units=("USD",),
            as_of_date="2025-06-01",
        )

        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["value"], 100.0)
        self.assertEqual(resolved[0]["accession_no"], "primary-2024-q1")

    def test_mismatched_or_missing_operand_never_creates_a_quarter(self) -> None:
        from finance.data.us_stock_turnaround import resolve_discrete_quarters

        rows = [
            _fact(
                value=100.0,
                period_start="2024-01-01",
                period_end="2024-03-31",
                available_at="2024-05-01",
                fiscal_year=2024,
                fiscal_quarter=1,
                unit="USD",
            ),
            _fact(
                value=250.0,
                period_start="2024-01-01",
                period_end="2024-06-30",
                available_at="2024-08-01",
                fiscal_year=2024,
                fiscal_quarter=2,
                unit="EUR",
            ),
            _fact(
                value=400.0,
                period_start="2025-01-01",
                period_end="2025-09-30",
                available_at="2025-11-01",
                fiscal_year=2025,
                fiscal_quarter=3,
            ),
        ]

        resolved = resolve_discrete_quarters(
            rows,
            metric="revenue",
            concepts=("us-gaap:Revenues",),
            units=("USD",),
            as_of_date="2025-12-01",
        )

        self.assertEqual([(row["fiscal_year"], row["fiscal_quarter"]) for row in resolved], [(2024, 1)])

    def test_future_filing_is_excluded_by_as_of_cutoff(self) -> None:
        from finance.data.us_stock_turnaround import resolve_discrete_quarters

        rows = [
            _fact(
                value=100.0,
                period_start="2024-01-01",
                period_end="2024-03-31",
                available_at="2024-05-01",
                fiscal_year=2024,
                fiscal_quarter=1,
            ),
            _fact(
                value=999.0,
                period_start="2024-04-01",
                period_end="2024-06-30",
                available_at="2024-08-01",
                fiscal_year=2024,
                fiscal_quarter=2,
            ),
        ]

        resolved = resolve_discrete_quarters(
            rows,
            metric="revenue",
            concepts=("us-gaap:Revenues",),
            units=("USD",),
            as_of_date="2024-06-30",
        )

        self.assertEqual([row["fiscal_quarter"] for row in resolved], [1])


class TurnaroundInstantAndSplitTests(unittest.TestCase):
    def test_instant_and_duration_facts_are_resolved_separately(self) -> None:
        from finance.data.us_stock_turnaround import resolve_instant_facts

        rows = [
            _fact(
                value=1_000.0,
                period_start=None,
                period_end="2024-06-30",
                available_at="2024-08-01",
                fiscal_year=2024,
                fiscal_quarter=2,
                period_type="DATE",
                source_period_type="instant",
                concept="us-gaap:CashAndCashEquivalentsAtCarryingValue",
            ),
            _fact(
                value=300.0,
                period_start="2024-04-01",
                period_end="2024-06-30",
                available_at="2024-08-01",
                fiscal_year=2024,
                fiscal_quarter=2,
                concept="us-gaap:CashAndCashEquivalentsAtCarryingValue",
            ),
        ]

        resolved = resolve_instant_facts(
            rows,
            metric="cash",
            concepts=("us-gaap:CashAndCashEquivalentsAtCarryingValue",),
            units=("USD",),
            as_of_date="2024-08-31",
        )

        self.assertEqual(len(resolved), 1)
        self.assertEqual(resolved[0]["value"], 1_000.0)
        self.assertEqual(resolved[0]["source_period_type"], "instant")

    def test_split_neutral_share_series_ignores_future_split(self) -> None:
        from finance.data.us_stock_turnaround import build_split_neutral_share_series

        quarters = [
            {
                "period_end": "2023-12-31",
                "available_at": "2024-02-01",
                "value": 100.0,
            },
            {
                "period_end": "2024-12-31",
                "available_at": "2025-02-01",
                "value": 200.0,
            },
        ]
        prices = [
            {"date": "2024-06-15", "stock_splits": 2.0},
            {"date": "2026-01-15", "stock_splits": 2.0},
        ]

        resolved = build_split_neutral_share_series(
            quarters,
            prices,
            as_of_date="2025-03-01",
        )

        self.assertEqual([row["split_factor"] for row in resolved], [2.0, 1.0])
        self.assertEqual([row["split_neutral_value"] for row in resolved], [200.0, 200.0])


if __name__ == "__main__":
    unittest.main()
