from __future__ import annotations

import unittest
from types import SimpleNamespace
from unittest.mock import Mock

import pandas as pd


NPORT_XML = """<?xml version="1.0" encoding="UTF-8"?>
<edgarSubmission xmlns="http://www.sec.gov/edgar/nport">
  <formData>
    <genInfo><repPdDate>2025-03-31</repPdDate></genInfo>
    <invstOrSecs>
      <invstOrSec>
        <name>Apple Inc.</name><lei>HWUPKR0MPOU8FGXBT394</lei>
        <title>Apple Inc.</title><cusip>037833100</cusip>
        <identifiers><isin value="US0378331005"/></identifiers>
        <balance>100</balance><units>NS</units><curCd>USD</curCd>
        <valUSD>600</valUSD><pctVal>60</pctVal><assetCat>EC</assetCat>
      </invstOrSec>
      <invstOrSec>
        <name>Microsoft Corp.</name><lei>INR2EJN1ERAN0W5ZP974</lei>
        <title>Microsoft Corp.</title><cusip>594918104</cusip>
        <identifiers><isin value="US5949181045"/></identifiers>
        <balance>50</balance><units>NS</units><curCd>USD</curCd>
        <valUSD>400</valUSD><pctVal>40</pctVal><assetCat>EC</assetCat>
      </invstOrSec>
    </invstOrSecs>
  </formData>
</edgarSubmission>
"""


N30B2_HTML = """
<html><body><table>
  <tr><td>Number of Shares</td><td></td><td>Security</td><td>Value</td></tr>
  <tr><td>100</td><td></td><td>Apple Inc.</td><td>600</td></tr>
  <tr><td>50</td><td></td><td>Microsoft Corp.</td><td>400</td></tr>
  <tr><td></td><td></td><td>Total Common Stocks</td><td>1000</td></tr>
</table>
<table>
  <tr><td>Proceeds from shares sold</td><td>2000</td><td>3000</td></tr>
  <tr><td>End of year</td><td>4000</td><td>5000</td></tr>
</table></body></html>
"""


def _quarterly_eps_rows(symbol: str) -> list[dict[str, object]]:
    return [
        {
            "symbol": symbol,
            "concept": "us-gaap:EarningsPerShareDiluted",
            "unit": "USD per share",
            "source_period_type": "duration",
            "period_type": "Q",
            "fiscal_year": 2025,
            "fiscal_quarter": quarter,
            "period_end": period_end,
            "value": 1.0,
            "available_at": "2026-05-01",
        }
        for quarter, period_end in enumerate(
            ("2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31"),
            1,
        )
    ]


def _repair_holdings_fixture() -> list[dict[str, object]]:
    base = {"as_of_date": "2026-05-29", "source": "invesco_current_csv"}
    return [
        {**base, "holding_symbol": "FULL", "holding_name": "Full Corp", "issuer_cik": "1", "weight_pct": 40.0, "asset_class": "Equity"},
        {**base, "holding_symbol": "MISS_EPS", "holding_name": "Missing EPS Corp", "issuer_cik": "2", "weight_pct": 25.0, "asset_class": "Equity"},
        {**base, "holding_symbol": "MISS_PRICE", "holding_name": "Missing Price Corp", "issuer_cik": "3", "weight_pct": 20.0, "asset_class": "Equity"},
        {**base, "holding_symbol": None, "holding_name": "Unknown Plc", "issuer_cik": None, "weight_pct": 5.0, "asset_class": "Equity"},
        {**base, "holding_symbol": "USD", "holding_name": "United States Dollar", "issuer_cik": None, "weight_pct": 5.0, "asset_class": "Currency"},
        {**base, "holding_symbol": "NQZ6", "holding_name": "Nasdaq 100 E-mini Index Future", "issuer_cik": None, "weight_pct": 5.0, "asset_class": "Index Future"},
    ]


def _repair_price_fixture() -> list[dict[str, object]]:
    rows: list[dict[str, object]] = []
    for symbol in ("FULL", "MISS_EPS"):
        rows.extend(
            {"symbol": symbol, "date": date_value, "close": price}
            for date_value, price in (
                ("2026-05-29", 100.0),
                ("2026-06-30", 101.0),
                ("2026-07-31", 102.0),
            )
        )
    rows.append({"symbol": "MISS_PRICE", "date": "2026-05-29", "close": 50.0})
    rows.extend(
        {"symbol": "QQQ", "date": date_value, "close": price}
        for date_value, price in (("2026-06-30", 700.0), ("2026-07-31", 710.0))
    )
    return rows


class Nasdaq100ValuationCoverageTests(unittest.TestCase):
    def test_materialization_excludes_non_equity_holdings_before_weight_normalization(self) -> None:
        from finance.data.nasdaq100_valuation import materialize_monthly_valuation_rows

        rows = materialize_monthly_valuation_rows(
            [
                {"as_of_date": "2026-05-29", "holding_symbol": "FULL", "holding_name": "Full Corp", "weight_pct": 94.0, "asset_class": "Equity"},
                {"as_of_date": "2026-05-29", "holding_symbol": "USD", "holding_name": "United States Dollar", "weight_pct": 6.0, "asset_class": "Currency"},
            ],
            _quarterly_eps_rows("FULL"),
            [
                {"symbol": "FULL", "date": "2026-05-29", "close": 100.0},
                {"symbol": "FULL", "date": "2026-06-30", "close": 101.0},
                {"symbol": "QQQ", "date": "2026-06-30", "close": 700.0},
            ],
            start_month="2026-06-01",
            end_month="2026-06-30",
        )

        self.assertEqual(rows[0]["data_quality"], "reconstructed_actual")
        self.assertAlmostEqual(rows[0]["coverage_weight_pct"], 100.0)

    def test_builds_repair_plan_without_non_equity_targets(self) -> None:
        from finance.data.nasdaq100_valuation import build_nasdaq100_coverage_repair_plan

        plan = build_nasdaq100_coverage_repair_plan(
            holding_rows=_repair_holdings_fixture(),
            statement_rows=_quarterly_eps_rows("FULL") + _quarterly_eps_rows("MISS_PRICE"),
            price_rows=_repair_price_fixture(),
            issue_rows=[],
            start_month="2026-06-01",
            end_month="2026-07-31",
        )

        by_symbol = {row["symbol"]: row for row in plan["targets"]}
        self.assertEqual(by_symbol["MISS_EPS"]["needs"], ["quarterly_diluted_eps"])
        self.assertEqual(by_symbol["MISS_PRICE"]["needs"], ["eod_price"])
        self.assertEqual(by_symbol["MISS_EPS"]["affected_months"], 2)
        self.assertNotIn("USD", by_symbol)
        self.assertNotIn("NQZ6", by_symbol)
        self.assertEqual(plan["window"]["months"], 2)
        self.assertEqual(plan["before"], {"ready_months": 0, "blocked_months": 2})
        self.assertEqual(
            {row["reason"] for row in plan["unsupported"]},
            {"missing_identity"},
        )

    def test_repair_plan_does_not_repeat_exhausted_price_history(self) -> None:
        from finance.data.nasdaq100_valuation import build_nasdaq100_coverage_repair_plan

        plan = build_nasdaq100_coverage_repair_plan(
            holding_rows=_repair_holdings_fixture(),
            statement_rows=_quarterly_eps_rows("FULL") + _quarterly_eps_rows("MISS_PRICE"),
            price_rows=_repair_price_fixture(),
            issue_rows=[{"symbol": "MISS_PRICE", "latest_status": "active"}],
            start_month="2026-06-01",
            end_month="2026-07-31",
        )

        self.assertNotIn("MISS_PRICE", {row["symbol"] for row in plan["targets"]})
        self.assertIn(
            ("MISS_PRICE", "unsupported_free_source"),
            {(row.get("symbol"), row["reason"]) for row in plan["unsupported"]},
        )

    def test_load_repair_plan_resolves_inclusive_month_window(self) -> None:
        from finance.data.nasdaq100_valuation import load_nasdaq100_coverage_repair_plan

        input_loader = Mock(
            return_value=(
                _repair_holdings_fixture(),
                _quarterly_eps_rows("FULL") + _quarterly_eps_rows("MISS_PRICE"),
                _repair_price_fixture(),
            )
        )
        issue_loader = Mock(return_value=[])

        plan = load_nasdaq100_coverage_repair_plan(
            months=2,
            end_month="2026-07-13",
            input_loader=input_loader,
            issue_loader=issue_loader,
        )

        self.assertEqual(
            plan["window"],
            {"start_month": "2026-06-01", "end_month": "2026-07-31", "months": 2},
        )
        input_loader.assert_called_once()
        self.assertEqual(input_loader.call_args.kwargs["start_month"], "2026-06-01")
        self.assertEqual(input_loader.call_args.kwargs["end_month"], "2026-07-31")
        issue_loader.assert_called_once()

    def test_scenario_history_repair_window_covers_119_inclusive_months(self) -> None:
        from finance.data.nasdaq100_valuation import (
            NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS,
            nasdaq100_repair_window,
        )

        self.assertEqual(NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS, 119)
        self.assertEqual(
            nasdaq100_repair_window(
                end_month="2026-07-31",
                months=NASDAQ100_SCENARIO_HISTORY_REPAIR_MONTHS,
            ),
            ("2016-09-01", "2026-07-31"),
        )

    def test_repair_input_collection_keeps_successful_batches_and_reports_failures(self) -> None:
        from app.jobs.ingestion_jobs import collect_nasdaq100_repair_inputs

        plan = {
            "targets": [
                {"symbol": "EPS_A", "needs": ["quarterly_diluted_eps"], "start_date": "2021-08-01", "end_date": "2026-07-31"},
                {"symbol": "EPS_B", "needs": ["quarterly_diluted_eps"], "start_date": "2021-08-01", "end_date": "2026-07-31"},
                {"symbol": "PRICE_A", "needs": ["eod_price"], "start_date": "2021-08-01", "end_date": "2026-07-31"},
            ]
        }
        events: list[dict[str, object]] = []
        statement_calls: list[list[str]] = []
        price_calls: list[list[str]] = []

        def statement_runner(symbols, **_kwargs):
            statement_calls.append(list(symbols))
            if list(symbols) == ["EPS_B"]:
                raise RuntimeError("SEC unavailable")
            return {"status": "success", "rows_written": 4, "failed_symbols": []}

        def price_runner(symbols, **_kwargs):
            price_calls.append(list(symbols))
            return {"status": "success", "rows_written": 10, "failed_symbols": []}

        result = collect_nasdaq100_repair_inputs(
            plan,
            batch_size=1,
            progress_callback=events.append,
            statement_runner=statement_runner,
            price_runner=price_runner,
            price_limit_persister=lambda *_args, **_kwargs: {"symbols": [], "rows_written": 0},
        )

        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 14)
        self.assertEqual(result["failed_symbols"], ["EPS_B"])
        self.assertEqual(statement_calls, [["EPS_A"], ["EPS_B"]])
        self.assertEqual(price_calls, [["PRICE_A"]])
        self.assertEqual(
            [event["stage"] for event in events if event["event"] == "stage_start"],
            ["eps", "prices"],
        )

    def test_persists_only_successfully_attempted_price_targets_that_remain_missing(self) -> None:
        from app.jobs.ingestion_jobs import persist_nasdaq100_exhausted_price_targets

        issue_builder = Mock(return_value=[{"issue_key": "issue-1"}])
        issue_writer = Mock(return_value=1)
        result = persist_nasdaq100_exhausted_price_targets(
            [
                {"symbol": "PRICE_A", "start_date": "2021-08-01", "end_date": "2026-07-31"},
                {"symbol": "RECOVERED", "start_date": "2021-08-01", "end_date": "2026-07-31"},
            ],
            months=60,
            end_month="2026-07-31",
            plan_loader=lambda **_kwargs: {
                "targets": [
                    {"symbol": "PRICE_A", "needs": ["eod_price"], "affected_months": 12}
                ]
            },
            freshness_loader=lambda **_kwargs: pd.DataFrame(
                [
                    {
                        "symbol": "PRICE_A",
                        "first_date": "2021-08-02",
                        "latest_date": "2025-12-31",
                        "row_count": 1100,
                    }
                ]
            ),
            issue_builder=issue_builder,
            issue_writer=issue_writer,
        )

        self.assertEqual(result, {"symbols": ["PRICE_A"], "rows_written": 1})
        evidence = issue_builder.call_args.args[0]
        self.assertEqual(evidence[0]["symbol"], "PRICE_A")
        self.assertEqual(evidence[0]["min_rows"], 12)
        issue_builder.assert_called_once_with(evidence, universe_code="NASDAQ100")
        issue_writer.assert_called_once_with([{"issue_key": "issue-1"}])

    def test_repair_collection_persists_only_successful_price_attempts(self) -> None:
        from app.jobs.ingestion_jobs import collect_nasdaq100_repair_inputs

        persister = Mock(return_value={"symbols": ["PRICE_A"], "rows_written": 1})
        result = collect_nasdaq100_repair_inputs(
            {
                "window": {"months": 60, "end_month": "2026-07-31"},
                "targets": [
                    {"symbol": "PRICE_A", "needs": ["eod_price"], "start_date": "2021-08-01", "end_date": "2026-07-31"},
                    {"symbol": "PRICE_B", "needs": ["eod_price"], "start_date": "2021-08-01", "end_date": "2026-07-31"},
                ],
            },
            batch_size=2,
            statement_runner=Mock(),
            price_runner=lambda *_args, **_kwargs: {
                "status": "partial_success",
                "rows_written": 100,
                "failed_symbols": ["PRICE_B"],
            },
            price_limit_persister=persister,
        )

        attempted = persister.call_args.args[0]
        self.assertEqual([row["symbol"] for row in attempted], ["PRICE_A"])
        persister.assert_called_once_with(
            attempted,
            months=60,
            end_month="2026-07-31",
        )
        self.assertEqual(result["price_limit_issues"]["rows_written"], 1)

    def test_repair_job_rematerializes_after_partial_collection_and_reports_before_after(self) -> None:
        from app.jobs.ingestion_jobs import run_repair_nasdaq100_valuation_coverage

        before = {
            "window": {"start_month": "2021-08-01", "end_month": "2026-07-31", "months": 60},
            "targets": [{"symbol": "OLD", "needs": ["eod_price"]}],
            "unsupported": [],
            "before": {"ready_months": 5, "blocked_months": 55},
        }
        after = {
            "window": dict(before["window"]),
            "targets": [{"symbol": "OLD", "needs": ["eod_price"]}],
            "unsupported": [{"symbol": "OLD", "reason": "unsupported_free_source"}],
            "before": {"ready_months": 48, "blocked_months": 12},
        }
        plan_loader = Mock(side_effect=[before, after])
        input_collector = Mock(
            return_value={
                "status": "partial_success",
                "rows_written": 10,
                "failed_symbols": ["OLD"],
                "steps": [],
                "price_limit_issues": {"symbols": [], "rows_written": 0},
            }
        )
        materializer = Mock(
            return_value={"rows_written": 60, "ready_rows": 48, "blocked_rows": 12}
        )
        events: list[dict[str, object]] = []

        result = run_repair_nasdaq100_valuation_coverage(
            months=60,
            plan_loader=plan_loader,
            input_collector=input_collector,
            materializer=materializer,
            progress_callback=events.append,
        )

        self.assertEqual(result["status"], "partial_success")
        self.assertEqual(result["rows_written"], 70)
        self.assertEqual(result["failed_symbols"], ["OLD"])
        self.assertEqual(result["details"]["before"], before["before"])
        self.assertEqual(result["details"]["after"], after["before"])
        input_collector.assert_called_once_with(
            before,
            batch_size=20,
            progress_callback=events.append,
        )
        materializer.assert_called_once_with(
            start_month="2021-08-01",
            end_month="2026-07-31",
        )
        self.assertEqual(
            [event["stage"] for event in events if event["event"] == "stage_start"],
            ["diagnose", "materialize"],
        )

    def test_repair_job_only_succeeds_when_all_requested_months_are_ready(self) -> None:
        from app.jobs.ingestion_jobs import run_repair_nasdaq100_valuation_coverage

        complete = {
            "window": {"start_month": "2021-08-01", "end_month": "2026-07-31", "months": 60},
            "targets": [],
            "unsupported": [],
            "before": {"ready_months": 60, "blocked_months": 0},
        }
        result = run_repair_nasdaq100_valuation_coverage(
            plan_loader=Mock(side_effect=[complete, complete]),
            input_collector=Mock(),
            materializer=Mock(return_value={"rows_written": 60, "ready_rows": 60, "blocked_rows": 0}),
        )

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["details"]["after"]["ready_months"], 60)

    def test_repair_job_progress_uses_requested_119_month_window(self) -> None:
        from app.jobs.ingestion_jobs import run_repair_nasdaq100_valuation_coverage

        complete = {
            "window": {
                "start_month": "2016-09-01",
                "end_month": "2026-07-31",
                "months": 119,
            },
            "targets": [],
            "unsupported": [],
            "before": {"ready_months": 119, "blocked_months": 0},
        }
        events: list[dict[str, object]] = []
        result = run_repair_nasdaq100_valuation_coverage(
            months=119,
            plan_loader=Mock(side_effect=[complete, complete]),
            input_collector=Mock(),
            materializer=Mock(
                return_value={
                    "rows_written": 119,
                    "ready_rows": 119,
                    "blocked_rows": 0,
                }
            ),
            progress_callback=events.append,
        )

        self.assertEqual(result["status"], "success")
        messages = [str(event.get("message") or "") for event in events]
        self.assertTrue(any("119개월 누락 자료" in message for message in messages))
        self.assertTrue(any("119개월 가치평가" in message for message in messages))
        self.assertIn("119-month repair", result["message"])

    def test_parses_companyfacts_diluted_eps_with_filing_availability(self) -> None:
        from finance.data.nasdaq100_valuation import parse_sec_companyfacts_diluted_eps

        payload = {
            "facts": {
                "us-gaap": {
                    "EarningsPerShareDiluted": {
                        "units": {
                            "USD/shares": [
                                {"start": "2025-01-01", "end": "2025-03-31", "val": 1.0, "accn": "a1", "fy": 2025, "fp": "Q1", "form": "10-Q", "filed": "2025-05-01"},
                                {"start": "2025-04-01", "end": "2025-06-30", "val": 1.2, "accn": "a2", "fy": 2025, "fp": "Q2", "form": "10-Q", "filed": "2025-08-01"},
                                {"start": "2025-01-01", "end": "2025-06-30", "val": 2.2, "accn": "ytd", "fy": 2025, "fp": "Q2", "form": "10-Q", "filed": "2025-08-01"},
                            ]
                        }
                    }
                }
            }
        }

        rows = parse_sec_companyfacts_diluted_eps(payload, symbol="ABC")

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["concept"], "us-gaap:EarningsPerShareDiluted")
        self.assertEqual(rows[0]["unit"], "USD per share")
        self.assertEqual(rows[1]["fiscal_quarter"], 2)
        self.assertEqual(rows[1]["available_at"], "2025-08-01")

    def test_parses_basic_and_diluted_eps_as_combined_diluted_fallback(self) -> None:
        from finance.data.nasdaq100_valuation import parse_sec_companyfacts_diluted_eps

        payload = {
            "facts": {
                "us-gaap": {
                    "EarningsPerShareBasicAndDiluted": {
                        "units": {
                            "USD/shares": [
                                {
                                    "start": "2020-02-01",
                                    "end": "2020-04-30",
                                    "val": -0.26,
                                    "accn": "combined-q1",
                                    "fy": 2021,
                                    "fp": "Q1",
                                    "form": "10-Q",
                                    "filed": "2020-06-05",
                                }
                            ]
                        }
                    }
                }
            }
        }

        rows = parse_sec_companyfacts_diluted_eps(payload, symbol="DOCU")

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["concept"], "us-gaap:EarningsPerShareBasicAndDiluted")
        self.assertEqual(rows[0]["value"], -0.26)

    def test_canonical_statement_rows_keep_combined_eps_when_edgar_omits_statement_type(self) -> None:
        from finance.data.financial_statements import _iter_value_rows_from_source

        fact = SimpleNamespace(
            statement_type=None,
            form_type="10-Q",
            fiscal_period="Q1",
            label="Basic and diluted earnings per share",
            concept="us-gaap:EarningsPerShareBasicAndDiluted",
            period_start="2020-02-01",
            period_end="2020-04-30",
            numeric_value=-0.26,
            filing_date="2020-06-05",
            accession="combined-q1",
            unit="USD per share",
            fiscal_year=2021,
            period_type="duration",
            taxonomy="us-gaap",
            data_quality=None,
            is_audited=None,
            is_restated=None,
            is_estimated=None,
            confidence_score=None,
        )
        source = {
            "facts": [fact],
            "filings_by_accession": {
                "combined-q1": {
                    "accepted_at": "2020-06-05 16:00:00",
                    "report_date": "2020-04-30",
                }
            },
        }

        rows = _iter_value_rows_from_source("DOCU", source, "quarterly", 0)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["statement_type"], "income_statement")
        self.assertEqual(rows[0]["concept"], "us-gaap:EarningsPerShareBasicAndDiluted")

    def test_sec_fetch_retries_bounded_connection_failure(self) -> None:
        from finance.data.nasdaq100_valuation import fetch_sec_text

        response = Mock()
        response.__enter__ = Mock(return_value=response)
        response.__exit__ = Mock(return_value=False)
        response.read.return_value = b"official payload"
        opener = Mock(side_effect=[TimeoutError("connect timeout"), response])

        text = fetch_sec_text(
            "https://www.sec.gov/fixture",
            opener=opener,
            attempts=2,
            sleep_fn=lambda _seconds: None,
        )

        self.assertEqual(text, "official payload")
        self.assertEqual(opener.call_count, 2)

    def test_discovers_qqq_holdings_filings_with_archive_urls(self) -> None:
        from finance.data.nasdaq100_valuation import discover_qqq_sec_filings

        payload = {
            "cik": "0001067839",
            "filings": {
                "recent": {
                    "accessionNumber": ["0001067839-26-000024", "0001193125-18-355790", "x"],
                    "filingDate": ["2026-05-28", "2018-12-21", "2026-01-01"],
                    "reportDate": ["2026-03-31", "2018-09-30", "2025-12-31"],
                    "form": ["NPORT-P", "N-30B-2", "8-K"],
                    "primaryDocument": [
                        "xslFormNPORT-P_X01/primary_doc.xml",
                        "d638310dn30b2.htm",
                        "ignored.htm",
                    ],
                }
            },
        }

        rows = discover_qqq_sec_filings(payload)

        self.assertEqual([row["report_date"] for row in rows], ["2018-09-30", "2026-03-31"])
        self.assertEqual(rows[0]["holding_snapshot_quality"], "annual_anchor")
        self.assertEqual(rows[1]["holding_snapshot_quality"], "quarterly_anchor")
        self.assertEqual(
            rows[1]["source_url"],
            "https://www.sec.gov/Archives/edgar/data/1067839/000106783926000024/primary_doc.xml",
        )

    def test_parses_nport_identity_and_weights(self) -> None:
        from finance.data.nasdaq100_valuation import parse_qqq_nport_xml

        rows = parse_qqq_nport_xml(
            NPORT_XML,
            filing={
                "report_date": "2025-03-31",
                "filing_date": "2025-05-29",
                "accession_no": "0001752724-25-127952",
                "source_url": "https://www.sec.gov/fixture.xml",
                "holding_snapshot_quality": "quarterly_anchor",
            },
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(rows[0]["cusip"], "037833100")
        self.assertEqual(rows[0]["isin"], "US0378331005")
        self.assertEqual(rows[0]["weight_pct"], 60.0)
        self.assertEqual(rows[0]["holding_id"], "037833100")
        self.assertEqual(rows[0]["filing_date"], "2025-05-29")

    def test_parses_n30b2_schedule_and_normalizes_market_value_weights(self) -> None:
        from finance.data.nasdaq100_valuation import parse_qqq_n30b2_html

        rows = parse_qqq_n30b2_html(
            N30B2_HTML,
            filing={
                "report_date": "2018-09-30",
                "filing_date": "2018-12-21",
                "accession_no": "0001193125-18-355790",
                "source_url": "https://www.sec.gov/fixture.htm",
                "holding_snapshot_quality": "annual_anchor",
            },
        )

        self.assertEqual([row["holding_name"] for row in rows], ["Apple Inc.", "Microsoft Corp."])
        self.assertEqual([row["weight_pct"] for row in rows], [60.0, 40.0])
        self.assertTrue(all(row["holding_snapshot_quality"] == "annual_anchor" for row in rows))

    def test_resolves_cusip_then_name_then_reviewed_override(self) -> None:
        from finance.data.nasdaq100_valuation import resolve_holding_identities

        rows = resolve_holding_identities(
            [
                {"cusip": "037833100", "holding_name": "Apple Inc."},
                {"cusip": None, "holding_name": "Microsoft Corporation"},
                {"cusip": None, "holding_name": "Comcast Corp., Class A"},
                {"cusip": None, "holding_name": "Facebook, Inc., Class A"},
                {"cusip": None, "holding_name": "Unknown Plc"},
            ],
            [
                {"cusip": "037833100", "symbol": "AAPL", "issuer_cik": "0000320193", "name": "Apple Inc."},
                {"cusip": None, "symbol": "MSFT", "issuer_cik": "0000789019", "name": "Microsoft Corp."},
                {"cusip": None, "symbol": "CMCSA", "issuer_cik": "0001166691", "name": "Comcast Corporation"},
            ],
        )

        self.assertEqual([row.get("holding_symbol") for row in rows], ["AAPL", "MSFT", "CMCSA", "META", None])
        self.assertEqual([row["identity_method"] for row in rows], ["cusip_exact", "name_exact", "name_exact", "reviewed_override", "unresolved"])

    def test_derives_q4_from_fy_and_keeps_negative_quarter_in_ttm(self) -> None:
        from finance.data.nasdaq100_valuation import derive_filing_aware_ttm_eps

        base = {
            "symbol": "ABC",
            "concept": "us-gaap:EarningsPerShareDiluted",
            "unit": "USD per share",
            "source_period_type": "duration",
            "fiscal_year": 2025,
        }
        rows = [
            {**base, "period_type": "Q", "fiscal_quarter": 1, "period_end": "2025-03-31", "value": 1.0, "available_at": "2025-05-01"},
            {**base, "period_type": "Q", "fiscal_quarter": 2, "period_end": "2025-06-30", "value": -0.5, "available_at": "2025-08-01"},
            {**base, "period_type": "Q", "fiscal_quarter": 3, "period_end": "2025-09-30", "value": 2.0, "available_at": "2025-11-01"},
            {**base, "period_type": "FY", "fiscal_quarter": None, "period_end": "2025-12-31", "value": 4.0, "available_at": "2026-02-01"},
        ]

        result = derive_filing_aware_ttm_eps(rows, as_of_date="2026-02-28")

        self.assertEqual(result["ABC"]["quarter_count"], 4)
        self.assertAlmostEqual(result["ABC"]["ttm_eps"], 4.0)
        self.assertAlmostEqual(result["ABC"]["quarters"][-1]["eps"], 1.5)
        self.assertEqual(result["ABC"]["quarters"][-1]["derivation"], "fy_minus_q1_q2_q3")

    def test_ttm_resolver_ignores_later_filing_comparative_fy_fact(self) -> None:
        from finance.data.nasdaq100_valuation import derive_filing_aware_ttm_eps

        base = {
            "symbol": "AMZN",
            "concept": "us-gaap:EarningsPerShareDiluted",
            "unit": "USD per share",
            "source_period_type": "duration",
            "fiscal_year": 2024,
        }
        rows = [
            {**base, "period_type": "Q", "fiscal_quarter": 1, "period_end": "2024-03-31", "report_date": "2024-03-31", "value": 0.98, "available_at": "2024-04-30"},
            {**base, "period_type": "Q", "fiscal_quarter": 2, "period_end": "2024-06-30", "report_date": "2024-06-30", "value": 1.26, "available_at": "2024-08-02"},
            {**base, "period_type": "Q", "fiscal_quarter": 3, "period_end": "2024-09-30", "report_date": "2024-09-30", "value": 1.43, "available_at": "2024-11-01"},
            {
                **base,
                "period_type": "FY",
                "fiscal_quarter": None,
                "period_end": "2023-12-31",
                "report_date": "2024-12-31",
                "value": 2.90,
                "available_at": "2025-02-07",
                "accession_no": "2024-10k-comparative-2023",
            },
        ]

        result = derive_filing_aware_ttm_eps(rows, as_of_date="2025-02-28")

        self.assertNotIn("AMZN", result)

    def test_ttm_resolver_derives_q4_only_from_true_fiscal_year_end(self) -> None:
        from finance.data.nasdaq100_valuation import derive_filing_aware_ttm_eps

        base = {
            "symbol": "AAPL",
            "concept": "us-gaap:EarningsPerShareDiluted",
            "unit": "USD per share",
            "source_period_type": "duration",
            "fiscal_year": 2025,
        }
        rows = [
            {**base, "period_type": "Q", "fiscal_quarter": 1, "period_end": "2024-12-28", "report_date": "2024-12-28", "value": 0.90, "available_at": "2025-01-31"},
            {**base, "period_type": "Q", "fiscal_quarter": 2, "period_end": "2025-03-29", "report_date": "2025-03-29", "value": 1.40, "available_at": "2025-05-02"},
            {**base, "period_type": "Q", "fiscal_quarter": 3, "period_end": "2025-06-28", "report_date": "2025-06-28", "value": 1.60, "available_at": "2025-08-01"},
            {
                **base,
                "period_type": "FY",
                "fiscal_quarter": None,
                "period_end": "2025-09-27",
                "report_date": "2025-09-27",
                "value": 6.00,
                "available_at": "2025-10-31",
                "accession_no": "2025-10k",
            },
        ]

        result = derive_filing_aware_ttm_eps(rows, as_of_date="2025-11-30")

        quarters = result["AAPL"]["quarters"]
        self.assertEqual([row["fiscal_quarter"] for row in quarters], [1, 2, 3, 4])
        self.assertAlmostEqual(quarters[-1]["eps"], 2.10)
        self.assertEqual(quarters[-1]["period_end"], "2025-09-27")
        self.assertEqual(quarters[-1]["derivation"], "fy_minus_q1_q2_q3")

    def test_derives_ttm_from_combined_basic_and_diluted_eps_fallback(self) -> None:
        from finance.data.nasdaq100_valuation import derive_filing_aware_ttm_eps

        base = {
            "symbol": "DOCU",
            "concept": "us-gaap:EarningsPerShareBasicAndDiluted",
            "unit": "USD per share",
            "source_period_type": "duration",
            "fiscal_year": 2021,
        }
        rows = [
            {**base, "period_type": "Q", "fiscal_quarter": 1, "period_end": "2020-04-30", "value": -0.26, "available_at": "2020-06-05"},
            {**base, "period_type": "Q", "fiscal_quarter": 2, "period_end": "2020-07-31", "value": -0.35, "available_at": "2020-09-04"},
            {**base, "period_type": "Q", "fiscal_quarter": 3, "period_end": "2020-10-31", "value": -0.31, "available_at": "2020-12-04"},
            {**base, "period_type": "FY", "fiscal_quarter": None, "period_end": "2021-01-31", "value": -1.31, "available_at": "2021-03-31"},
        ]

        result = derive_filing_aware_ttm_eps(rows, as_of_date="2021-08-31")

        self.assertEqual(result["DOCU"]["quarter_count"], 4)
        self.assertAlmostEqual(result["DOCU"]["ttm_eps"], -1.31)

    def test_drift_weights_by_security_price_and_renormalizes(self) -> None:
        from finance.data.nasdaq100_valuation import drift_holding_weights

        rows = drift_holding_weights(
            [
                {"holding_symbol": "AAA", "weight_pct": 60.0},
                {"holding_symbol": "BBB", "weight_pct": 40.0},
            ],
            {
                "AAA": {"2025-03-31": 10.0, "2025-04-30": 20.0},
                "BBB": {"2025-03-31": 10.0, "2025-04-30": 10.0},
            },
            snapshot_date="2025-03-31",
            observation_month="2025-04-30",
        )

        self.assertAlmostEqual(rows[0]["month_weight_pct"], 75.0)
        self.assertAlmostEqual(rows[1]["month_weight_pct"], 25.0)

    def test_reconstruction_counts_negative_yield_and_enforces_coverage_gate(self) -> None:
        from finance.data.nasdaq100_valuation import reconstruct_monthly_valuation

        ready = reconstruct_monthly_valuation(
            [
                {"holding_symbol": "AAA", "month_weight_pct": 96.0},
                {"holding_symbol": "LOSS", "month_weight_pct": 4.0},
            ],
            {"AAA": {"ttm_eps": 5.0, "earnings_available_through": "2026-01-31"}, "LOSS": {"ttm_eps": -1.0, "earnings_available_through": "2026-01-31"}},
            {"AAA": 100.0, "LOSS": 20.0},
            observation_month="2026-02-28",
            qqq_price=500.0,
        )
        blocked = reconstruct_monthly_valuation(
            [{"holding_symbol": "AAA", "month_weight_pct": 94.0}, {"holding_symbol": None, "month_weight_pct": 6.0}],
            {"AAA": {"ttm_eps": 5.0, "earnings_available_through": "2026-01-31"}},
            {"AAA": 100.0},
            observation_month="2026-02-28",
            qqq_price=500.0,
        )

        self.assertEqual(ready["data_quality"], "reconstructed_actual")
        self.assertAlmostEqual(ready["coverage_weight_pct"], 100.0)
        self.assertAlmostEqual(ready["earnings_yield"], (0.96 * 0.05) + (0.04 * -0.05))
        self.assertEqual(blocked["data_quality"], "blocked")
        self.assertEqual(blocked["error_code"], "INSUFFICIENT_EARNINGS_COVERAGE")

    def test_calibration_gate_reports_median_and_max_absolute_percentage_error(self) -> None:
        from finance.data.nasdaq100_valuation import evaluate_pe_calibration

        result = evaluate_pe_calibration(
            [
                {"observation_month": "2026-05-01", "trailing_pe": 31.0},
                {"observation_month": "2026-06-01", "trailing_pe": 33.0},
            ],
            [
                {"observation_month": "2026-05-01", "trailing_pe": 30.0},
                {"observation_month": "2026-06-01", "trailing_pe": 30.0},
            ],
        )

        self.assertEqual(result["status"], "BLOCKED")
        self.assertAlmostEqual(result["median_ape_pct"], (3.3333333333 + 10.0) / 2.0, places=6)
        self.assertAlmostEqual(result["max_ape_pct"], 10.0)

    def test_materializes_monthly_row_from_latest_holdings_filing_cutoff_and_prices(self) -> None:
        from finance.data.nasdaq100_valuation import materialize_monthly_valuation_rows

        holdings = [
            {"as_of_date": "2025-03-31", "holding_symbol": "AAA", "weight_pct": 60.0, "holding_snapshot_quality": "quarterly_anchor"},
            {"as_of_date": "2025-03-31", "holding_symbol": "BBB", "weight_pct": 40.0, "holding_snapshot_quality": "quarterly_anchor"},
        ]
        statement_rows = []
        for symbol, eps in (("AAA", 1.0), ("BBB", 2.0)):
            for quarter, period_end in enumerate(("2024-06-30", "2024-09-30", "2024-12-31", "2025-03-31"), start=1):
                statement_rows.append(
                    {
                        "symbol": symbol,
                        "concept": "us-gaap:EarningsPerShareDiluted",
                        "unit": "USD per share",
                        "source_period_type": "duration",
                        "period_type": "Q",
                        "fiscal_year": 2025,
                        "fiscal_quarter": quarter,
                        "period_end": period_end,
                        "value": eps,
                        "available_at": "2025-04-15",
                    }
                )
        price_rows = [
            {"symbol": "AAA", "date": "2025-03-31", "close": 10.0},
            {"symbol": "BBB", "date": "2025-03-31", "close": 20.0},
            {"symbol": "QQQ", "date": "2025-03-31", "close": 500.0},
            {"symbol": "AAA", "date": "2025-04-30", "close": 20.0},
            {"symbol": "BBB", "date": "2025-04-30", "close": 20.0},
            {"symbol": "QQQ", "date": "2025-04-30", "close": 520.0},
        ]

        rows = materialize_monthly_valuation_rows(
            holdings,
            statement_rows,
            price_rows,
            start_month="2025-04-01",
            end_month="2025-04-30",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["holding_snapshot_date"], "2025-03-31")
        self.assertEqual(rows[0]["holding_snapshot_quality"], "quarterly_anchor")
        self.assertEqual(rows[0]["data_quality"], "reconstructed_actual")
        self.assertAlmostEqual(rows[0]["coverage_weight_pct"], 100.0)

    def test_schema_adds_holding_identity_and_monthly_valuation_business_key(self) -> None:
        from finance.data.db.schema import PROVIDER_SCHEMAS, VALUATION_SCHEMAS

        holdings = PROVIDER_SCHEMAS["etf_holdings_snapshot"]
        monthly = VALUATION_SCHEMAS["nasdaq100_monthly_valuation"]

        self.assertIn("cusip VARCHAR(32) NULL", holdings)
        self.assertIn("issuer_cik VARCHAR(16) NULL", holdings)
        self.assertIn("holding_snapshot_quality ENUM", holdings)
        self.assertIn("UNIQUE KEY uk_nasdaq100_month_proxy_source", monthly)
        self.assertIn("coverage_weight_pct DOUBLE", monthly)
        self.assertIn("data_quality ENUM('reconstructed_actual','partial','blocked')", monthly)

    def test_schema_bootstrap_syncs_holdings_and_monthly_tables(self) -> None:
        from finance.data.nasdaq100_valuation import ensure_nasdaq100_valuation_schemas

        db = Mock()
        db.query.return_value = [{"cnt": 0}]

        ensure_nasdaq100_valuation_schemas(db_factory=lambda *_args, **_kwargs: db)

        executed = "\n".join(call.args[0] for call in db.execute.call_args_list)
        self.assertIn("etf_holdings_snapshot", executed)
        self.assertIn("nasdaq100_monthly_valuation", executed)
        db.close.assert_called_once()

    def test_holdings_and_monthly_writers_use_idempotent_upsert(self) -> None:
        from finance.data.nasdaq100_valuation import (
            store_nasdaq100_monthly_rows,
            store_qqq_holdings_rows,
        )

        db = Mock()
        db.query.return_value = [{"cnt": 0}]
        holding = {
            "fund_symbol": "QQQ", "as_of_date": "2025-03-31", "source": "sec_qqq_nport",
            "source_type": "official", "source_ref": "https://www.sec.gov/fixture.xml",
            "holding_id": "037833100", "holding_symbol": "AAPL", "holding_name": "Apple Inc.",
            "holding_type": "Equity", "cusip": "037833100", "isin": "US0378331005",
            "lei": "HWUPKR0MPOU8FGXBT394", "issuer_cik": "0000320193", "filing_date": "2025-05-29",
            "accession_no": "0001752724-25-127952", "holding_snapshot_quality": "quarterly_anchor",
            "weight_pct": 12.0, "shares": 100.0, "market_value": 1000.0, "sector": None,
            "asset_class": "Equity", "country": "US", "currency": "USD", "coverage_status": "actual",
            "missing_fields_json": None, "collected_at": "2026-07-13 10:00:00", "error_msg": None,
        }
        monthly = {
            "observation_month": "2026-07-01", "proxy_symbol": "QQQ", "qqq_price": 709.43,
            "reconstructed_ttm_eps": None, "trailing_pe": None, "earnings_yield": None,
            "coverage_weight_pct": 94.47, "unmapped_weight_pct": 5.53,
            "holding_snapshot_date": "2026-05-29", "holding_snapshot_quality": "current_issuer_snapshot",
            "earnings_available_through": "2026-05-21", "price_basis_date": "2026-07-07",
            "data_quality": "blocked", "source": "sec_qqq_holdings_sec_actual",
            "source_ref": "https://www.sec.gov/Archives/edgar/data/1067839",
            "collected_at": "2026-07-13 10:00:00", "error_msg": "INSUFFICIENT_EARNINGS_COVERAGE",
        }

        store_qqq_holdings_rows([holding], db_factory=lambda *_args, **_kwargs: db)
        store_nasdaq100_monthly_rows([monthly], db_factory=lambda *_args, **_kwargs: db)

        sql = "\n".join(call.args[0] for call in db.executemany.call_args_list)
        self.assertIn("ON DUPLICATE KEY UPDATE", sql)
        self.assertIn("INSERT INTO etf_holdings_snapshot", sql)
        self.assertIn("INSERT INTO nasdaq100_monthly_valuation", sql)

    def test_loader_keeps_blocked_rows_and_latest_coverage_evidence(self) -> None:
        from finance.loaders.nasdaq100_valuation import (
            load_latest_nasdaq100_ttm_proxy,
            load_nasdaq100_monthly_valuation,
        )

        query_fn = Mock(return_value=[])
        load_nasdaq100_monthly_valuation(query_fn=query_fn)
        self.assertEqual(query_fn.call_args.args[1], ("QQQ", 120))

        evidence = load_latest_nasdaq100_ttm_proxy(
            query_fn=lambda _sql, _params: [
                {
                    "observation_month": "2026-07-01", "qqq_price": 709.43,
                    "reconstructed_ttm_eps": None, "trailing_pe": None,
                    "coverage_weight_pct": 94.47, "unmapped_weight_pct": 5.53,
                    "holding_snapshot_date": "2026-05-29", "holding_snapshot_quality": "current_issuer_snapshot",
                    "earnings_available_through": "2026-05-21", "price_basis_date": "2026-07-07",
                    "data_quality": "blocked", "source": "sec_qqq_holdings_sec_actual",
                    "source_ref": "https://www.sec.gov/fixture", "error_msg": "INSUFFICIENT_EARNINGS_COVERAGE",
                }
            ]
        )

        self.assertEqual(evidence["status"], "BLOCKED")
        self.assertEqual(evidence["coverage_weight_pct"], 94.47)
        self.assertEqual(evidence["error_code"], "INSUFFICIENT_EARNINGS_COVERAGE")

    def test_collects_official_filing_rows_and_passes_normalized_rows_to_writer(self) -> None:
        from finance.data.nasdaq100_valuation import collect_and_store_qqq_sec_holdings

        submissions = {
            "cik": "0001067839",
            "filings": {"recent": {
                "accessionNumber": ["0001067839-25-000001"],
                "filingDate": ["2025-05-29"], "reportDate": ["2025-03-31"],
                "form": ["NPORT-P"], "primaryDocument": ["primary_doc.xml"],
            }},
        }
        writer = Mock(return_value=2)

        result = collect_and_store_qqq_sec_holdings(
            submissions_payload=submissions,
            identity_rows=[
                {"cusip": "037833100", "symbol": "AAPL", "issuer_cik": "0000320193", "name": "Apple Inc."},
                {"cusip": "594918104", "symbol": "MSFT", "issuer_cik": "0000789019", "name": "Microsoft Corp."},
            ],
            fetch_text_fn=lambda _url: NPORT_XML,
            rows_writer=writer,
            collected_at="2026-07-13 10:00:00",
        )

        self.assertEqual(result["rows_written"], 2)
        stored = writer.call_args.args[0]
        self.assertEqual(stored[0]["holding_symbol"], "AAPL")
        self.assertEqual(stored[0]["coverage_status"], "actual")
        self.assertEqual(stored[0]["source_type"], "official")

    def test_materialization_wrapper_keeps_blocked_month_and_writes_it(self) -> None:
        from finance.data.nasdaq100_valuation import materialize_and_store_nasdaq100_monthly

        writer = Mock(return_value=1)
        result = materialize_and_store_nasdaq100_monthly(
            start_month="2026-07-01", end_month="2026-07-31",
            holding_rows=[
                {"as_of_date": "2026-06-30", "holding_symbol": "AAA", "weight_pct": 94.0,
                 "holding_snapshot_quality": "quarterly_anchor"},
                {"as_of_date": "2026-06-30", "holding_symbol": None, "weight_pct": 6.0,
                 "holding_snapshot_quality": "quarterly_anchor"},
            ],
            statement_rows=[
                {"symbol": "AAA", "concept": "us-gaap:EarningsPerShareDiluted", "unit": "USD per share",
                 "source_period_type": "duration", "period_type": "Q", "fiscal_year": 2025,
                 "fiscal_quarter": quarter, "period_end": period_end, "value": 1.0,
                 "available_at": "2026-05-01"}
                for quarter, period_end in enumerate(("2025-06-30", "2025-09-30", "2025-12-31", "2026-03-31"), 1)
            ],
            price_rows=[
                {"symbol": "AAA", "date": "2026-06-30", "close": 100.0},
                {"symbol": "AAA", "date": "2026-07-31", "close": 101.0},
                {"symbol": "QQQ", "date": "2026-07-31", "close": 700.0},
            ],
            rows_writer=writer, collected_at="2026-07-13 10:00:00",
        )

        self.assertEqual(result["blocked_rows"], 1)
        self.assertEqual(writer.call_args.args[0][0]["error_msg"], "INSUFFICIENT_EARNINGS_COVERAGE")


if __name__ == "__main__":
    unittest.main()
