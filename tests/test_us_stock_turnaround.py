from __future__ import annotations

import unittest

import pandas as pd


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


_METRIC_CONCEPTS = {
    "revenue": ("us-gaap:RevenueFromContractWithCustomerExcludingAssessedTax", "USD"),
    "gross_profit": ("us-gaap:GrossProfit", "USD"),
    "cost_of_revenue": ("us-gaap:CostOfRevenue", "USD"),
    "operating_income": ("us-gaap:OperatingIncomeLoss", "USD"),
    "net_income": ("us-gaap:NetIncomeLoss", "USD"),
    "ocf": ("us-gaap:NetCashProvidedByUsedInOperatingActivities", "USD"),
    "capex": ("us-gaap:PaymentsToAcquirePropertyPlantAndEquipment", "USD"),
    "diluted_eps": ("us-gaap:EarningsPerShareDiluted", "USD per share"),
    "diluted_shares": ("us-gaap:WeightedAverageNumberOfDilutedSharesOutstanding", "shares"),
    "interest_expense": ("us-gaap:InterestExpenseNonOperating", "USD"),
    "da": ("us-gaap:DepreciationDepletionAndAmortization", "USD"),
}


def _metric_facts(metric: str, values: list[float | None], *, symbol: str = "RIVN") -> list[dict[str, object]]:
    concept, unit = _METRIC_CONCEPTS[metric]
    rows: list[dict[str, object]] = []
    for end, value in zip(pd.date_range("2023-03-31", periods=len(values), freq="QE-DEC"), values):
        if value is None:
            continue
        quarter = int((end.month - 1) // 3) + 1
        start = end - pd.DateOffset(months=3) + pd.Timedelta(days=1)
        rows.append(
            _fact(
                value=float(value),
                period_start=start.strftime("%Y-%m-%d"),
                period_end=end.strftime("%Y-%m-%d"),
                available_at=(end + pd.Timedelta(days=40)).strftime("%Y-%m-%d"),
                fiscal_year=int(end.year),
                fiscal_quarter=quarter,
                concept=concept,
                unit=unit,
                accession_no=f"{end.year}-Q{quarter}",
                symbol=symbol,
            )
        )
    return rows


def _core_statement_rows() -> list[dict[str, object]]:
    values = {
        "revenue": [100, 110, 120, 130, 120, 140, 160, 180],
        "gross_profit": [20, 22, 24, 26, 30, 35, 45, 55],
        "operating_income": [-30, -28, -26, -24, -20, -15, -10, -5],
        "net_income": [-35, -33, -30, -28, -24, -18, -12, -4],
        "ocf": [-40, -35, -30, -25, -20, -10, 5, 15],
        "capex": [10, 10, 11, 11, 12, 12, 13, 13],
        "diluted_eps": [-1.0, -0.9, -0.8, -0.7, -0.6, -0.4, -0.2, -0.1],
        "diluted_shares": [100, 101, 102, 103, 104, 106, 108, 110],
        "interest_expense": [5, 5, 5, 5, 5, 5, 5, 5],
    }
    return [row for metric, metric_values in values.items() for row in _metric_facts(metric, metric_values)]


class TurnaroundSeriesTests(unittest.TestCase):
    def test_series_builds_canonical_quarters_ttm_margins_and_cash_flow(self) -> None:
        from finance.data.us_stock_turnaround import build_turnaround_quarterly_series

        result = build_turnaround_quarterly_series(
            _core_statement_rows(),
            [],
            as_of_date="2025-03-31",
        )

        self.assertEqual(len(result["timeline"]), 8)
        latest = result["timeline"][-1]
        self.assertEqual(latest["status"], "AVAILABLE")
        self.assertEqual(latest["ttm_revenue"], 600.0)
        self.assertAlmostEqual(latest["revenue_yoy_pct"], (180 / 130 - 1) * 100)
        self.assertEqual(latest["ttm_gross_profit"], 165.0)
        self.assertAlmostEqual(latest["ttm_gross_margin_pct"], 165 / 600 * 100)
        self.assertEqual(latest["ttm_operating_income"], -50.0)
        self.assertAlmostEqual(latest["ttm_operating_margin_pct"], -50 / 600 * 100)
        self.assertEqual(latest["ttm_ocf"], -10.0)
        self.assertEqual(latest["ttm_capex"], 50.0)
        self.assertEqual(latest["ttm_fcf"], -60.0)
        self.assertAlmostEqual(latest["ttm_eps"], -1.3)

    def test_gross_profit_fallback_requires_compatible_same_filing_revenue_and_cost(self) -> None:
        from finance.data.us_stock_turnaround import build_turnaround_quarterly_series

        revenue = _metric_facts("revenue", [100, 110, 120, 130])
        cost = _metric_facts("cost_of_revenue", [80, 86, 92, 98])
        incompatible = [dict(cost[-1], accession_no="different-filing")]

        compatible_result = build_turnaround_quarterly_series(
            revenue + cost,
            [],
            as_of_date="2024-06-01",
        )
        incompatible_result = build_turnaround_quarterly_series(
            revenue + cost[:-1] + incompatible,
            [],
            as_of_date="2024-06-01",
        )

        self.assertEqual(
            [row["gross_profit"] for row in compatible_result["timeline"]],
            [20.0, 24.0, 28.0, 32.0],
        )
        self.assertIsNone(incompatible_result["timeline"][-1]["gross_profit"])
        self.assertEqual(
            incompatible_result["timeline"][-1]["metric_reasons"]["gross_profit"],
            "INCOMPATIBLE_REVENUE_COST_PROVENANCE",
        )

    def test_missing_quarter_keeps_fiscal_slot_and_breaks_ttm(self) -> None:
        from finance.data.us_stock_turnaround import build_turnaround_quarterly_series

        rows = []
        for metric in ("revenue", "gross_profit", "operating_income", "ocf", "capex", "diluted_eps"):
            rows.extend(_metric_facts(metric, [10, 11, 12, 13, None, 15]))

        result = build_turnaround_quarterly_series(rows, [], as_of_date="2024-12-31")

        missing = result["timeline"][4]
        latest = result["timeline"][-1]
        self.assertEqual(missing["slot_key"], "2024-Q1")
        self.assertEqual(missing["status"], "MISSING")
        self.assertIsNone(latest["ttm_revenue"])
        self.assertEqual(latest["metric_reasons"]["ttm_revenue"], "MISSING_QUARTER_IN_WINDOW")

    def test_capex_is_normalized_to_positive_cash_outflow_magnitude(self) -> None:
        from finance.data.us_stock_turnaround import build_turnaround_quarterly_series

        rows = _metric_facts("ocf", [10, 10, 10, 10]) + _metric_facts("capex", [-3, -4, -5, -6])

        result = build_turnaround_quarterly_series(rows, [], as_of_date="2024-06-01")

        self.assertEqual([row["capex"] for row in result["timeline"]], [3.0, 4.0, 5.0, 6.0])
        self.assertEqual(result["timeline"][-1]["ttm_fcf"], 22.0)

    def test_current_balance_prefers_direct_total_debt_over_components(self) -> None:
        from finance.data.us_stock_turnaround import build_turnaround_quarterly_series

        common = {
            "period_start": None,
            "period_end": "2024-12-31",
            "available_at": "2025-02-15",
            "fiscal_year": 2024,
            "fiscal_quarter": 4,
            "period_type": "DATE",
            "source_period_type": "instant",
            "report_date": "2024-12-31",
            "accession_no": "2024-FY",
        }
        rows = [
            _fact(value=50.0, concept="us-gaap:CashAndCashEquivalentsAtCarryingValue", **common),
            _fact(value=20.0, concept="us-gaap:ShortTermInvestments", **common),
            _fact(value=400.0, concept="us-gaap:LongTermDebtAndFinanceLeaseObligations", **common),
            _fact(value=100.0, concept="us-gaap:LongTermDebtCurrent", **common),
            _fact(value=300.0, concept="us-gaap:LongTermDebtNoncurrent", **common),
        ]

        direct = build_turnaround_quarterly_series(rows, [], as_of_date="2025-03-01")
        components = build_turnaround_quarterly_series(
            [row for row in rows if row["concept"] != "us-gaap:LongTermDebtAndFinanceLeaseObligations"],
            [],
            as_of_date="2025-03-01",
        )

        self.assertEqual(direct["current_balance"].get("total_debt"), 400.0)
        self.assertEqual(components["current_balance"].get("total_debt"), 400.0)
        self.assertEqual(direct["current_balance"].get("accession_no"), "2024-FY")


def _analysis_timeline(
    *,
    ttm_ocf: list[float] | None = None,
    quarterly_eps: list[float] | None = None,
    ttm_eps: list[float] | None = None,
    shares: list[float] | None = None,
) -> list[dict[str, object]]:
    ocf = ttm_ocf or [-20.0] * 8
    eps = quarterly_eps or [-1.0] * 8
    trailing_eps = ttm_eps or [-4.0] * 8
    share_values = shares or [100.0] * 8
    rows = []
    for index in range(8):
        rows.append(
            {
                "slot_key": f"202{3 + index // 4}-Q{index % 4 + 1}",
                "status": "AVAILABLE",
                "revenue_yoy_pct": [None, None, None, None, 1.0, 2.0, 3.0, 5.0][index],
                "ttm_revenue_yoy_pct": [None, None, None, None, 1.0, 2.0, 3.0, 5.0][index],
                "ttm_gross_profit": 20.0,
                "ttm_gross_margin_pct": [20, 20, 20, 20, 21, 22, 23, 24][index],
                "ttm_operating_margin_pct": [-20, -19, -18, -17, -15, -14, -12, -10][index],
                "operating_margin_yoy_delta_pp": [None, None, None, None, 5, 5, 6, 7][index],
                "ttm_ocf": ocf[index],
                "ttm_fcf": ocf[index] - 5.0,
                "ttm_operating_income": -10.0,
                "ttm_interest_expense": 5.0,
                "diluted_eps": eps[index],
                "ttm_eps": trailing_eps[index],
                "split_neutral_diluted_shares": share_values[index],
            }
        )
    return rows


class TurnaroundMilestoneAndRiskTests(unittest.TestCase):
    def test_operating_and_cash_milestones_are_independent(self) -> None:
        from finance.data.us_stock_turnaround import classify_turnaround_milestones

        series = {"timeline": _analysis_timeline(ttm_ocf=[-20, -18, -16, -14, -12, -10, -8, -6])}
        result = classify_turnaround_milestones(series, per_status="BLOCKED")

        self.assertEqual(result["headline"], "OPERATING_IMPROVEMENT")
        self.assertEqual(result["milestones"]["OPERATING_IMPROVEMENT"]["status"], "MET")
        self.assertEqual(result["milestones"]["CASH_FLOW_TURN"]["status"], "NOT_MET")
        self.assertEqual(result["evidence"]["burn_improving"], True)

    def test_cash_flow_turn_needs_two_consecutive_positive_ttm_observations(self) -> None:
        from finance.data.us_stock_turnaround import classify_turnaround_milestones

        one_positive = {"timeline": _analysis_timeline(ttm_ocf=[-10, -9, -8, -7, -6, -5, -4, 1])}
        two_positive = {"timeline": _analysis_timeline(ttm_ocf=[-10, -9, -8, -7, -6, -5, 1, 2])}

        self.assertEqual(
            classify_turnaround_milestones(one_positive, per_status="BLOCKED")["milestones"]["CASH_FLOW_TURN"]["status"],
            "NOT_MET",
        )
        self.assertEqual(
            classify_turnaround_milestones(two_positive, per_status="BLOCKED")["milestones"]["CASH_FLOW_TURN"]["status"],
            "MET",
        )

    def test_earnings_turn_candidate_and_per_ready_use_distinct_eps_contracts(self) -> None:
        from finance.data.us_stock_turnaround import classify_turnaround_milestones

        earnings = {
            "timeline": _analysis_timeline(
                quarterly_eps=[-1, -1, -1, -1, -1, 0.1, 0.2, -0.1],
                ttm_eps=[-4, -4, -4, -4, -3, -2, -1, -0.5],
            )
        }
        candidate = {"timeline": _analysis_timeline(ttm_eps=[-4, -3, -2, -1, -0.5, 0.1, 0.2, 0.3])}
        ready = {"timeline": _analysis_timeline(ttm_eps=[-4, -3, -2, -1, 0.1, 0.2, 0.3, 0.4])}

        earnings_result = classify_turnaround_milestones(earnings, per_status="BLOCKED")
        candidate_result = classify_turnaround_milestones(candidate, per_status="BLOCKED")
        ready_result = classify_turnaround_milestones(ready, per_status="READY")

        self.assertEqual(earnings_result["headline"], "EARNINGS_TURN")
        self.assertEqual(earnings_result["milestones"]["CASH_FLOW_TURN"]["status"], "NOT_MET")
        self.assertEqual(candidate_result["headline"], "PER_CANDIDATE")
        self.assertEqual(ready_result["headline"], "PER_READY")

    def test_less_than_eight_quarters_keeps_stage_unconfirmed(self) -> None:
        from finance.data.us_stock_turnaround import classify_turnaround_milestones

        result = classify_turnaround_milestones(
            {"timeline": _analysis_timeline()[-7:]},
            per_status="BLOCKED",
        )

        self.assertEqual(result["status"], "PARTIAL")
        self.assertEqual(result["headline"], "UNCONFIRMED")

    def test_risks_classify_runway_debt_service_net_debt_and_dilution_independently(self) -> None:
        from finance.data.us_stock_turnaround import evaluate_turnaround_risks

        timeline = _analysis_timeline(shares=[100, 100, 100, 100, 100, 100, 100, 110])
        timeline[-1].update(
            {
                "ttm_fcf": -120.0,
                "ttm_ocf": -20.0,
                "ttm_operating_income": 5.0,
                "ttm_interest_expense": 10.0,
            }
        )
        result = evaluate_turnaround_risks(
            {
                "timeline": timeline,
                "current_balance": {"cash": 50.0, "short_term_investments": 10.0, "total_debt": 200.0},
            }
        )

        self.assertEqual(result["cash_runway"]["status"], "HIGH_RISK")
        self.assertEqual(result["cash_runway"]["quarters"], 2.0)
        self.assertEqual(result["debt_service"]["status"], "HIGH_RISK")
        self.assertEqual(result["debt_service"]["interest_coverage"], 0.5)
        self.assertEqual(result["dilution"]["status"], "HIGH_RISK")
        self.assertAlmostEqual(result["dilution"]["yoy_pct"], 10.0)
        self.assertIn("NET_DEBT_WITH_NEGATIVE_OCF", result["flags"])

    def test_non_positive_operating_income_never_creates_interest_coverage(self) -> None:
        from finance.data.us_stock_turnaround import evaluate_turnaround_risks

        timeline = _analysis_timeline()
        timeline[-1].update({"ttm_operating_income": -1.0, "ttm_interest_expense": 5.0})
        result = evaluate_turnaround_risks({"timeline": timeline, "current_balance": {}})

        self.assertEqual(result["debt_service"]["status"], "NOT_MEANINGFUL")
        self.assertIsNone(result["debt_service"]["interest_coverage"])


def _valuation_series(**latest_overrides: float) -> dict[str, object]:
    timeline = _analysis_timeline()
    timeline[-1].update(
        {
            "ttm_revenue": 500.0,
            "ttm_gross_profit": 200.0,
            "ttm_operating_income": 80.0,
            "ttm_da": 20.0,
            "ttm_ocf": 150.0,
            "ttm_fcf": 100.0,
            "ttm_eps": -1.0,
            **latest_overrides,
        }
    )
    return {
        "timeline": timeline,
        "current_balance": {
            "cash": 100.0,
            "short_term_investments": 20.0,
            "total_debt": 200.0,
            "currency": "USD",
            "basis_date": "2026-06-30",
            "accession_no": "2026-Q2",
        },
    }


class TurnaroundValuationTests(unittest.TestCase):
    def test_per_ready_routes_to_existing_relative_value_handoff(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        result = route_turnaround_valuation(
            series=_valuation_series(),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="READY",
            as_of_date="2026-07-15",
        )

        self.assertEqual(result["method"], "P_E_HANDOFF")
        self.assertEqual(result["status"], "READY")
        self.assertIsNone(result["multiple"])

    def test_positive_fcf_uses_equity_value_multiple_and_yield(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        result = route_turnaround_valuation(
            series=_valuation_series(),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )

        self.assertEqual(result["method"], "P_FCF")
        self.assertEqual(result["multiple"], 10.0)
        self.assertEqual(result["yield_pct"], 10.0)
        self.assertEqual(result["market_cap_basis_date"], "2026-07-14")

    def test_positive_ocf_does_not_use_enterprise_value(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        result = route_turnaround_valuation(
            series=_valuation_series(ttm_fcf=-1.0, ttm_ocf=125.0),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )

        self.assertEqual(result["method"], "P_OCF")
        self.assertEqual(result["multiple"], 8.0)
        self.assertNotEqual(result["method"], "EV_OCF")

    def test_stale_or_unverified_input_suppresses_numeric_valuation(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        stale = route_turnaround_valuation(
            series=_valuation_series(),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-01", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )
        unverified = route_turnaround_valuation(
            series=_valuation_series(ttm_fcf=-1.0, ttm_ocf=-1.0, ttm_gross_profit=200.0),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": None},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )

        self.assertEqual(stale["reason_code"], "INPUT_STALE")
        self.assertIsNone(stale["multiple"])
        self.assertEqual(unverified["reason_code"], "UNIT_UNVERIFIED")
        self.assertIsNone(unverified["multiple"])

    def test_ev_method_requires_cash_debt_components_but_not_da(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        missing_components = _valuation_series(ttm_fcf=-1.0, ttm_ocf=-1.0, ttm_da=0.0)
        missing_components["current_balance"] = {"cash": 100.0, "currency": "USD", "basis_date": "2026-06-30"}
        blocked = route_turnaround_valuation(
            series=missing_components,
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )
        ready = route_turnaround_valuation(
            series=_valuation_series(ttm_fcf=-1.0, ttm_ocf=-1.0, ttm_da=0.0),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )

        self.assertEqual(blocked["reason_code"], "COMPONENT_MISSING")
        self.assertEqual(ready["method"], "EV_GROSS_PROFIT")
        self.assertAlmostEqual(ready["multiple"], 1080 / 200)

    def test_ev_method_blocks_misaligned_statement_components(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        series = _valuation_series(ttm_fcf=-1.0, ttm_ocf=-1.0, ttm_da=0.0)
        series["current_balance"]["component_alignment"] = False

        result = route_turnaround_valuation(
            series=series,
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )

        self.assertEqual(result["reason_code"], "COMPONENT_MISSING")
        self.assertIsNone(result["multiple"])

    def test_zero_denominators_and_specialized_sector_never_create_generic_multiple(self) -> None:
        from finance.data.us_stock_turnaround import route_turnaround_valuation

        zero = route_turnaround_valuation(
            series=_valuation_series(
                ttm_fcf=0.0,
                ttm_ocf=0.0,
                ttm_operating_income=0.0,
                ttm_da=0.0,
                ttm_gross_profit=0.0,
                ttm_revenue=0.0,
            ),
            profile={"market_cap": 1_000.0, "last_collected_at": "2026-07-14", "currency": "USD"},
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )
        bank = route_turnaround_valuation(
            series=_valuation_series(),
            profile={
                "market_cap": 1_000.0,
                "last_collected_at": "2026-07-14",
                "currency": "USD",
                "industry": "Banks - Regional",
            },
            latest_price={"date": "2026-07-15", "close": 10.0, "currency": "USD"},
            per_status="BLOCKED",
            as_of_date="2026-07-15",
        )

        self.assertEqual(zero["reason_code"], "NEGATIVE_OR_ZERO_DENOMINATOR")
        self.assertIsNone(zero["multiple"])
        self.assertEqual(bank["reason_code"], "SECTOR_METHOD_UNSUPPORTED")
        self.assertIsNone(bank["multiple"])

    def test_section_partial_does_not_hide_ready_operating_and_cash_charts(self) -> None:
        from finance.data.us_stock_turnaround import build_turnaround_analysis

        result = build_turnaround_analysis(
            statement_rows=_core_statement_rows(),
            price_rows=[],
            profile={"market_cap": None, "last_collected_at": None, "currency": "USD"},
            latest_price=None,
            per_status="BLOCKED",
            as_of_date="2025-03-31",
        )

        self.assertEqual(result["sections"]["operating_chart"]["status"], "READY")
        self.assertEqual(result["sections"]["cash_chart"]["status"], "READY")
        self.assertIn(result["sections"]["valuation"]["status"], {"PARTIAL", "BLOCKED"})
        self.assertIn(result["status"], {"READY", "PARTIAL"})


if __name__ == "__main__":
    unittest.main()
