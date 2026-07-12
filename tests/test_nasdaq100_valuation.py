from __future__ import annotations

import unittest
from unittest.mock import Mock


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


class Nasdaq100ValuationCoverageTests(unittest.TestCase):
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


if __name__ == "__main__":
    unittest.main()
