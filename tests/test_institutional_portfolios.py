from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


class Sec13FDataSetParserTests(unittest.TestCase):
    def test_normalize_sec_13f_frames_preserves_filing_timing_and_holdings(self) -> None:
        from finance.data.institutional_13f import SEC_13F_SOURCE_CAVEATS, normalize_sec_13f_frames

        frames = {
            "submission": pd.DataFrame(
                [
                    {
                        "ACCESSION_NUMBER": "0001067983-26-000001",
                        "FILING_DATE": "15-MAY-2026",
                        "SUBMISSIONTYPE": "13F-HR",
                        "CIK": "0001067983",
                        "PERIODOFREPORT": "31-MAR-2026",
                    }
                ]
            ),
            "coverpage": pd.DataFrame(
                [
                    {
                        "ACCESSION_NUMBER": "0001067983-26-000001",
                        "REPORTCALENDARORQUARTER": "31-MAR-2026",
                        "ISAMENDMENT": "",
                        "AMENDMENTNO": "",
                        "AMENDMENTTYPE": "",
                        "FILINGMANAGER_NAME": "BERKSHIRE HATHAWAY INC",
                        "REPORTTYPE": "13F HOLDINGS REPORT",
                        "FORM13FFILENUMBER": "028-01234",
                    }
                ]
            ),
            "summarypage": pd.DataFrame(
                [
                    {
                        "ACCESSION_NUMBER": "0001067983-26-000001",
                        "TABLEENTRYTOTAL": "2",
                        "TABLEVALUETOTAL": "3000",
                        "ISCONFIDENTIALOMITTED": "N",
                    }
                ]
            ),
            "infotable": pd.DataFrame(
                [
                    {
                        "ACCESSION_NUMBER": "0001067983-26-000001",
                        "INFOTABLE_SK": "1",
                        "NAMEOFISSUER": "APPLE INC",
                        "TITLEOFCLASS": "COM",
                        "CUSIP": "037833100",
                        "FIGI": "BBG000B9XRY4",
                        "VALUE": "1000",
                        "SSHPRNAMT": "10",
                        "SSHPRNAMTTYPE": "SH",
                        "PUTCALL": "",
                        "INVESTMENTDISCRETION": "SOLE",
                        "OTHERMANAGER": "",
                        "VOTING_AUTH_SOLE": "10",
                        "VOTING_AUTH_SHARED": "0",
                        "VOTING_AUTH_NONE": "0",
                    },
                    {
                        "ACCESSION_NUMBER": "0001067983-26-000001",
                        "INFOTABLE_SK": "2",
                        "NAMEOFISSUER": "BANK OF AMERICA CORP",
                        "TITLEOFCLASS": "COM",
                        "CUSIP": "060505104",
                        "FIGI": "",
                        "VALUE": "2000",
                        "SSHPRNAMT": "20",
                        "SSHPRNAMTTYPE": "SH",
                        "PUTCALL": "",
                        "INVESTMENTDISCRETION": "SOLE",
                        "OTHERMANAGER": "",
                        "VOTING_AUTH_SOLE": "20",
                        "VOTING_AUTH_SHARED": "0",
                        "VOTING_AUTH_NONE": "0",
                    },
                ]
            ),
        }

        normalized = normalize_sec_13f_frames(
            frames,
            source_dataset="2026-march-april-may",
            source_ref="https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip",
            collected_at="2026-07-08 00:00:00",
        )

        self.assertEqual(normalized["managers"][0]["cik"], "0001067983")
        self.assertEqual(normalized["managers"][0]["manager_name"], "BERKSHIRE HATHAWAY INC")
        self.assertEqual(normalized["filings"][0]["period_of_report"], "2026-03-31")
        self.assertEqual(normalized["filings"][0]["filing_date"], "2026-05-15")
        self.assertEqual(normalized["filings"][0]["table_entry_total"], 2)
        self.assertEqual(normalized["filings"][0]["table_value_total"], 3000)
        self.assertEqual(normalized["holdings"][0]["cusip"], "037833100")
        self.assertEqual(normalized["holdings"][0]["reported_value"], 1000)
        self.assertEqual(normalized["holdings"][0]["shares_or_principal_amount"], 10)
        self.assertEqual(normalized["holdings"][0]["source_dataset"], "2026-march-april-may")
        self.assertTrue(any("45 days" in caveat for caveat in SEC_13F_SOURCE_CAVEATS))

    def test_sec_13f_refresh_status_summarizes_latest_dataset_freshness(self) -> None:
        from finance.data.institutional_13f import build_sec_13f_refresh_status

        status = build_sec_13f_refresh_status(
            source_dataset="2026-march-april-may",
            source_ref="https://www.sec.gov/files/structureddata/data/form-13f-data-sets/01mar2026-31may2026_form13f.zip",
            collected_at="2026-07-09 00:00:00",
            normalized={
                "managers": [{"cik": "0001067983"}],
                "filings": [
                    {"period_of_report": "2025-12-31", "filing_date": "2026-02-14"},
                    {"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
                ],
                "holdings": [{"cusip": "037833100"}, {"cusip": "060505104"}],
            },
        )

        self.assertEqual(status["source_key"], "sec_form_13f_dataset")
        self.assertEqual(status["status"], "ok")
        self.assertEqual(status["latest_report_period"], "2026-03-31")
        self.assertEqual(status["latest_filing_date"], "2026-05-15")
        self.assertEqual(status["managers_written"], 1)
        self.assertEqual(status["filings_written"], 2)
        self.assertEqual(status["holdings_written"], 2)
        self.assertFalse(status["is_stale"])

    def test_schema_defines_refresh_status_and_watchlist_tables(self) -> None:
        from finance.data.db.schema import INSTITUTIONAL_13F_SCHEMAS

        self.assertIn("institutional_13f_refresh_status", INSTITUTIONAL_13F_SCHEMAS)
        self.assertIn("institutional_13f_manager_watchlist", INSTITUTIONAL_13F_SCHEMAS)
        self.assertIn("latest_report_period", INSTITUTIONAL_13F_SCHEMAS["institutional_13f_refresh_status"])
        self.assertIn("external_links_json", INSTITUTIONAL_13F_SCHEMAS["institutional_13f_manager_watchlist"])
        self.assertIn("ix_latest_accession_number", INSTITUTIONAL_13F_SCHEMAS["institutional_13f_manager"])
        self.assertIn("ix_report_period_cusip_cik", INSTITUTIONAL_13F_SCHEMAS["institutional_13f_holding"])

    def test_cusip_symbol_map_rows_use_unique_asset_profile_name_matches(self) -> None:
        from finance.data.institutional_13f import build_cusip_symbol_map_rows

        rows = build_cusip_symbol_map_rows(
            holdings=[
                {"cusip": "037833100", "issuer_name": "APPLE INC", "figi": "BBG000B9XRY4"},
                {"cusip": "060505104", "issuer_name": "BANK OF AMERICA CORP", "figi": ""},
                {"cusip": "999999999", "issuer_name": "DUPLICATE HOLDING", "figi": ""},
            ],
            asset_profiles=pd.DataFrame(
                [
                    {
                        "symbol": "AAPL",
                        "long_name": "Apple Inc.",
                        "sector": "Technology",
                        "industry": "Consumer Electronics",
                    },
                    {
                        "symbol": "BAC",
                        "long_name": "Bank of America Corporation",
                        "sector": "Financial Services",
                        "industry": "Banks",
                    },
                    {"symbol": "DUPA", "long_name": "Duplicate Holding Inc.", "sector": "Industrials", "industry": "Tools"},
                    {"symbol": "DUPB", "long_name": "Duplicate Holding Corp.", "sector": "Industrials", "industry": "Tools"},
                ]
            ),
            source_ref="unit-test",
        )

        mapped = {row["cusip"]: row for row in rows}
        self.assertEqual(mapped["037833100"]["symbol"], "AAPL")
        self.assertEqual(mapped["037833100"]["confidence"], 0.7)
        self.assertEqual(mapped["060505104"]["sector"], "Financial Services")
        self.assertNotIn("999999999", mapped)


class InstitutionalPortfolioReadModelTests(unittest.TestCase):
    def test_portfolio_model_builds_weights_changes_and_unmapped_sector_exposure(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model

        latest_holdings = pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 1500,
                    "shares_or_principal_amount": 15,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "cusip": "594918104",
                    "holding_symbol": "MSFT",
                    "issuer_name": "MICROSOFT CORP",
                    "reported_value": 500,
                    "shares_or_principal_amount": 5,
                    "sector": None,
                    "industry": None,
                },
            ]
        )
        previous_holdings = pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 1000,
                    "shares_or_principal_amount": 10,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "cusip": "060505104",
                    "holding_symbol": "BAC",
                    "issuer_name": "BANK OF AMERICA CORP",
                    "reported_value": 300,
                    "shares_or_principal_amount": 3,
                    "sector": "Financial Services",
                    "industry": "Banks",
                },
            ]
        )

        model = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={
                "accession_number": "0001067983-26-000001",
                "period_of_report": "2026-03-31",
                "filing_date": "2026-05-15",
                "source_ref": "https://www.sec.gov/Archives/edgar/data/1067983/000106798326000001/",
            },
            latest_holdings=latest_holdings,
            previous_filing={"period_of_report": "2025-12-31", "filing_date": "2026-02-14"},
            previous_holdings=previous_holdings,
        )

        self.assertEqual(model["summary"]["manager_name"], "BERKSHIRE HATHAWAY INC")
        self.assertEqual(model["summary"]["latest_report_period"], "2026-03-31")
        self.assertEqual(model["summary"]["total_reported_value"], 2000.0)
        self.assertEqual(model["summary"]["holding_count"], 2)
        self.assertEqual(model["change_summary"]["reported_new"], 1)
        self.assertEqual(model["change_summary"]["increased"], 1)
        self.assertEqual(model["change_summary"]["no_longer_reported"], 1)
        self.assertEqual(model["holdings"][0]["weight_pct"], 75.0)
        self.assertEqual(model["changes"][0]["change_type"], "increased")
        self.assertTrue(any(row["sector"] == "Unmapped" for row in model["sector_exposure"]))
        self.assertTrue(any("not a buy/sell signal" in caveat for caveat in model["caveats"]))

    def test_portfolio_performance_model_uses_report_period_price_window_and_coverage(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_performance_model

        model = {
            "summary": {"latest_report_period": "2026-03-31"},
            "holdings": [
                {
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 750.0,
                    "weight_pct": 75.0,
                },
                {
                    "holding_symbol": "MSFT",
                    "issuer_name": "MICROSOFT CORP",
                    "reported_value": 250.0,
                    "weight_pct": 25.0,
                },
                {
                    "holding_symbol": None,
                    "issuer_name": "UNMAPPED HOLDING",
                    "reported_value": 100.0,
                    "weight_pct": 10.0,
                },
            ],
        }
        prices = pd.DataFrame(
            [
                {"symbol": "AAPL", "date": "2026-03-31", "adj_close": 100.0, "close": 100.0},
                {"symbol": "AAPL", "date": "2026-07-07", "adj_close": 110.0, "close": 110.0},
                {"symbol": "MSFT", "date": "2026-04-01", "adj_close": 50.0, "close": 50.0},
                {"symbol": "MSFT", "date": "2026-07-07", "adj_close": 45.0, "close": 45.0},
            ]
        )

        performance = build_institutional_portfolio_performance_model(model, price_history=prices, as_of_date="2026-07-07")

        self.assertEqual(performance["status"], "ok")
        self.assertEqual(performance["report_period"], "2026-03-31")
        self.assertEqual(performance["latest_price_date"], "2026-07-07")
        self.assertAlmostEqual(performance["covered_weight_pct"], 90.9091)
        self.assertAlmostEqual(performance["portfolio_return_pct"], 4.5455)
        self.assertEqual(performance["rows"][0]["symbol"], "AAPL")
        self.assertEqual(performance["rows"][0]["return_pct"], 10.0)
        self.assertEqual(performance["top_contributors"][0]["symbol"], "AAPL")
        self.assertIn("가정", performance["caveat"])

    def test_selected_security_model_combines_holding_chart_and_holder_list(self) -> None:
        from app.services.institutional_portfolios import (
            build_institutional_interest_model,
            build_institutional_portfolio_model,
            build_institutional_selected_security_model,
        )

        latest_holdings = pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 1500,
                    "shares_or_principal_amount": 15,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                }
            ]
        )
        portfolio = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=latest_holdings,
            previous_filing=None,
            previous_holdings=pd.DataFrame(),
        )
        interest = build_institutional_interest_model(
            "AAPL",
            pd.DataFrame(
                [
                    {
                        "manager_name": "BERKSHIRE HATHAWAY INC",
                        "cik": "0001067983",
                        "period_of_report": "2026-03-31",
                        "filing_date": "2026-05-15",
                        "cusip": "037833100",
                        "holding_symbol": "AAPL",
                        "issuer_name": "APPLE INC",
                        "reported_value": 1500,
                        "shares_or_principal_amount": 15,
                        "weight_pct": 42.5,
                        "source_ref": "https://www.sec.gov/Archives/edgar/data/1067983/000106798326000001/",
                    }
                ]
            ),
        )
        prices = pd.DataFrame(
            [
                {
                    "symbol": "AAPL",
                    "date": "2026-03-31",
                    "open": 99.0,
                    "high": 103.0,
                    "low": 98.0,
                    "close": 100.0,
                    "adj_close": 100.0,
                    "volume": 1000,
                },
                {
                    "symbol": "AAPL",
                    "date": "2026-04-01",
                    "open": 100.0,
                    "high": 104.0,
                    "low": 99.0,
                    "close": 102.0,
                    "adj_close": 102.0,
                    "volume": 1100,
                },
                {
                    "symbol": "AAPL",
                    "date": "2026-05-01",
                    "open": 102.0,
                    "high": 106.0,
                    "low": 101.0,
                    "close": 105.0,
                    "adj_close": 105.0,
                    "volume": 1200,
                },
                {
                    "symbol": "AAPL",
                    "date": "2026-07-07",
                    "open": 106.0,
                    "high": 112.0,
                    "low": 105.0,
                    "close": 110.0,
                    "adj_close": 110.0,
                    "volume": 1300,
                },
            ]
        )

        detail = build_institutional_selected_security_model(
            portfolio_model=portfolio,
            query="AAPL",
            interest_model=interest,
            price_history=prices,
        )

        self.assertEqual(detail["status"], "ok")
        self.assertEqual(detail["security"]["symbol"], "AAPL")
        self.assertEqual(detail["security"]["sector"], "Technology")
        self.assertEqual(detail["portfolio_position"]["weight_label"], "100.0%")
        self.assertEqual(detail["holder_count"], 1)
        self.assertIn("daily", detail["charts"])
        self.assertIn("weekly", detail["charts"])
        self.assertIn("monthly", detail["charts"])
        self.assertTrue(detail["charts"]["daily"]["points"])
        first_daily_point = detail["charts"]["daily"]["points"][0]
        self.assertEqual(first_daily_point["open"], 99.0)
        self.assertEqual(first_daily_point["high"], 103.0)
        self.assertEqual(first_daily_point["low"], 98.0)
        self.assertEqual(first_daily_point["close"], 100.0)
        self.assertEqual(first_daily_point["volume"], 1000)

    def test_portfolio_model_resolves_safe_curated_cusip_symbols_for_charts(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model

        latest_holdings = pd.DataFrame(
            [
                {
                    "cusip": "191216100",
                    "holding_symbol": None,
                    "issuer_name": "COCA COLA CO",
                    "reported_value": 1200,
                    "shares_or_principal_amount": 40,
                    "sector": None,
                    "industry": None,
                },
                {
                    "cusip": "594918104",
                    "holding_symbol": None,
                    "issuer_name": "ABBVIE INC",
                    "reported_value": 300,
                    "shares_or_principal_amount": 3,
                    "sector": None,
                    "industry": None,
                },
            ]
        )

        model = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=latest_holdings,
            previous_filing=None,
            previous_holdings=pd.DataFrame(),
        )

        by_cusip = {row["cusip"]: row for row in model["holdings"]}
        self.assertEqual(by_cusip["191216100"]["holding_symbol"], "KO")
        self.assertEqual(by_cusip["191216100"]["symbol_source"], "curated_13f_cusip_seed")
        self.assertEqual(by_cusip["191216100"]["sector"], "Consumer Defensive")
        self.assertIsNone(by_cusip["594918104"]["holding_symbol"])

    def test_selected_security_model_exposes_price_collection_action_when_chart_missing(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model, build_institutional_selected_security_model

        portfolio = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=pd.DataFrame(
                [
                    {
                        "cusip": "191216100",
                        "holding_symbol": None,
                        "issuer_name": "COCA COLA CO",
                        "reported_value": 1200,
                        "shares_or_principal_amount": 40,
                    }
                ]
            ),
            previous_filing=None,
            previous_holdings=pd.DataFrame(),
        )

        detail = build_institutional_selected_security_model(
            portfolio_model=portfolio,
            query="KO",
            interest_model={"holders": [], "holder_count": 0},
            price_history=pd.DataFrame(),
        )

        self.assertEqual(detail["status"], "ok")
        self.assertEqual(detail["security"]["symbol"], "KO")
        self.assertFalse(detail["charts"]["daily"]["points"])
        self.assertEqual(detail["price_action"]["action_id"], "collect_price_history")
        self.assertEqual(detail["price_action"]["symbol"], "KO")
        self.assertTrue(detail["price_action"]["available"])

    def test_popularity_model_ranks_stocks_by_report_period_holder_count(self) -> None:
        from app.services.institutional_portfolios import build_institutional_popularity_model

        rows = pd.DataFrame(
            [
                {
                    "report_period": "2026-03-31",
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "holder_count": 130,
                    "total_reported_value": 8000000,
                    "sample_managers": "BERKSHIRE HATHAWAY INC, SAMPLE CAPITAL",
                },
                {
                    "report_period": "2026-03-31",
                    "cusip": "594918104",
                    "holding_symbol": "MSFT",
                    "issuer_name": "MICROSOFT CORP",
                    "holder_count": 120,
                    "total_reported_value": 9000000,
                    "sample_managers": "SAMPLE CAPITAL",
                },
            ]
        )

        model = build_institutional_popularity_model(rows, report_period="2026-03-31")

        self.assertEqual(model["status"], "ok")
        self.assertEqual(model["title"], "기관 보유 랭킹")
        self.assertEqual(model["report_period"], "2026-03-31")
        self.assertEqual(model["rows"][0]["rank"], 1)
        self.assertEqual(model["rows"][0]["symbol"], "AAPL")
        self.assertEqual(model["rows"][0]["holder_count"], 130)
        self.assertEqual(model["rows"][0]["drilldown_query"], "AAPL")

    def test_institutional_interest_model_accepts_symbol_or_cusip_lookup(self) -> None:
        from app.services.institutional_portfolios import build_institutional_interest_model

        holder_rows = pd.DataFrame(
            [
                {
                    "manager_name": "BERKSHIRE HATHAWAY INC",
                    "cik": "0001067983",
                    "period_of_report": "2026-03-31",
                    "filing_date": "2026-05-15",
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 1500,
                    "shares_or_principal_amount": 15,
                    "weight_pct": 42.5,
                    "source_ref": "https://www.sec.gov/Archives/edgar/data/1067983/000106798326000001/",
                },
                {
                    "manager_name": "SAMPLE CAPITAL",
                    "cik": "0000000001",
                    "period_of_report": "2026-03-31",
                    "filing_date": "2026-05-14",
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 100,
                    "shares_or_principal_amount": 1,
                    "weight_pct": 2.0,
                    "source_ref": "https://www.sec.gov/Archives/edgar/data/1/0001/",
                },
            ]
        )

        model = build_institutional_interest_model("AAPL", holder_rows)

        self.assertEqual(model["query"], "AAPL")
        self.assertEqual(model["holder_count"], 2)
        self.assertEqual(model["holders"][0]["manager_name"], "BERKSHIRE HATHAWAY INC")
        self.assertEqual(model["holders"][0]["weight_pct"], 42.5)
        self.assertTrue(any("CUSIP-symbol mapping" in caveat for caveat in model["caveats"]))

    def test_institutional_interest_model_applies_safe_curated_symbol_display(self) -> None:
        from app.services.institutional_portfolios import build_institutional_interest_model

        model = build_institutional_interest_model(
            "KO",
            pd.DataFrame(
                [
                    {
                        "manager_name": "BERKSHIRE HATHAWAY INC",
                        "cik": "0001067983",
                        "period_of_report": "2026-03-31",
                        "filing_date": "2026-05-15",
                        "cusip": "191216100",
                        "holding_symbol": None,
                        "issuer_name": "COCA COLA CO",
                        "reported_value": 1200,
                        "shares_or_principal_amount": 40,
                        "weight_pct": 11.5,
                    }
                ]
            ),
        )

        self.assertEqual(model["holders"][0]["holding_symbol"], "KO")

    def test_institutional_interest_loader_prefers_curated_cusip_for_curated_symbol_query(self) -> None:
        import app.services.institutional_portfolios as service

        calls: list[str] = []
        original_loader = service.load_institutional_13f_interest

        def fake_loader(query: str, *, limit: int = 100) -> pd.DataFrame:
            calls.append(query)
            if query == "191216100":
                return pd.DataFrame(
                    [
                        {
                            "manager_name": "BERKSHIRE HATHAWAY INC",
                            "cik": "0001067983",
                            "period_of_report": "2026-03-31",
                            "filing_date": "2026-05-15",
                            "cusip": "191216100",
                            "holding_symbol": None,
                            "issuer_name": "COCA COLA CO",
                            "reported_value": 1200,
                            "shares_or_principal_amount": 40,
                            "weight_pct": 11.5,
                        }
                    ]
                )
            return pd.DataFrame(
                [
                    {
                        "manager_name": "WRONG MAP CAPITAL",
                        "cik": "0000000001",
                        "period_of_report": "2026-03-31",
                        "filing_date": "2026-05-15",
                        "cusip": "031652100",
                        "holding_symbol": "AMKR",
                        "issuer_name": "AMKOR TECHNOLOGY INC",
                        "reported_value": 10,
                        "shares_or_principal_amount": 1,
                        "weight_pct": 1.0,
                    }
                ]
            )

        try:
            service.load_institutional_13f_interest = fake_loader
            model = service.load_institutional_interest_model("KO")["model"]
        finally:
            service.load_institutional_13f_interest = original_loader

        self.assertEqual(calls, ["191216100"])
        self.assertEqual(model["holders"][0]["issuer_name"], "COCA COLA CO")
        self.assertEqual(model["holders"][0]["holding_symbol"], "KO")

    def test_visual_workbench_payload_prioritizes_portfolio_chart_and_change_boards(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model, build_institutional_workbench_payload

        latest_holdings = pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 1500,
                    "shares_or_principal_amount": 15,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "cusip": "060505104",
                    "holding_symbol": "BAC",
                    "issuer_name": "BANK OF AMERICA CORP",
                    "reported_value": 900,
                    "shares_or_principal_amount": 30,
                    "sector": "Financial Services",
                    "industry": "Banks",
                },
                {
                    "cusip": "594918104",
                    "holding_symbol": "MSFT",
                    "issuer_name": "MICROSOFT CORP",
                    "reported_value": 600,
                    "shares_or_principal_amount": 6,
                    "sector": "Technology",
                    "industry": "Software",
                },
            ]
        )
        previous_holdings = pd.DataFrame(
            [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "reported_value": 1000,
                    "shares_or_principal_amount": 10,
                    "sector": "Technology",
                    "industry": "Consumer Electronics",
                },
                {
                    "cusip": "594918104",
                    "holding_symbol": "MICROSOFT CORP",
                    "issuer_name": "MICROSOFT CORP",
                    "reported_value": 800,
                    "shares_or_principal_amount": 8,
                    "sector": "Technology",
                    "industry": "Software",
                },
                {
                    "cusip": "459200101",
                    "holding_symbol": "IBM",
                    "issuer_name": "IBM",
                    "reported_value": 400,
                    "shares_or_principal_amount": 4,
                    "sector": "Technology",
                    "industry": "IT Services",
                },
            ]
        )
        model = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={
                "accession_number": "0001067983-26-000001",
                "period_of_report": "2026-03-31",
                "filing_date": "2026-05-15",
                "source_ref": "https://www.sec.gov/Archives/edgar/data/1067983/000106798326000001/",
            },
            latest_holdings=latest_holdings,
            previous_filing={"period_of_report": "2025-12-31", "filing_date": "2026-02-14"},
            previous_holdings=previous_holdings,
        )

        payload = build_institutional_workbench_payload(
            model=model,
            managers=[
                {"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC", "latest_report_period": "2026-03-31"},
                {"cik": "0001336528", "manager_name": "PERSHING SQUARE CAPITAL MANAGEMENT", "latest_report_period": "2026-03-31"},
            ],
            selected_cik="0001067983",
            interest_model=None,
            mode="live",
            allocation_limit=2,
            refresh_status={
                "status": "ok",
                "last_collected_at": "2026-07-09 00:00:00",
                "latest_report_period": "2026-03-31",
                "latest_filing_date": "2026-05-15",
                "stale_reason": "",
                "is_stale": False,
            },
        )

        self.assertEqual(payload["schema_version"], "institutional_portfolios_workbench_v1")
        self.assertEqual(payload["component"], "InstitutionalPortfoliosWorkbench")
        self.assertEqual(payload["mode"], "live")
        self.assertEqual(payload["hero"]["manager_name"], "BERKSHIRE HATHAWAY INC")
        self.assertGreaterEqual(len(payload["allocation"]["segments"]), 3)
        self.assertEqual(payload["allocation"]["segments"][0]["symbol"], "AAPL")
        self.assertIn("Other", {segment["label"] for segment in payload["allocation"]["segments"]})
        self.assertEqual(payload["change_board"]["groups"]["increased"]["count"], 1)
        self.assertEqual(payload["change_board"]["groups"]["reduced"]["count"], 1)
        self.assertEqual(payload["change_board"]["groups"]["no_longer_reported"]["count"], 1)
        self.assertTrue(payload["change_board"]["comparison_available"])
        self.assertEqual(payload["sector_exposure"]["bars"][0]["sector"], "Technology")
        self.assertEqual(payload["freshness"]["latest_report_period"], "2026-03-31")
        self.assertEqual(payload["refresh_action"]["action_id"], "collect_sec_13f_dataset")
        self.assertFalse(payload["refresh_action"]["primary"])
        self.assertTrue(payload["source_caveats"]["visible"])
        self.assertFalse(payload["boundary"]["trade_signal"])

    def test_visual_workbench_payload_explains_missing_previous_filing_comparison(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model, build_institutional_workbench_payload

        model = build_institutional_portfolio_model(
            manager={"cik": "0001656456", "manager_name": "APPALOOSA LP"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=pd.DataFrame(
                [
                    {
                        "cusip": "037833100",
                        "holding_symbol": "AAPL",
                        "issuer_name": "APPLE INC",
                        "reported_value": 1000,
                        "shares_or_principal_amount": 10,
                    }
                ]
            ),
            previous_filing=None,
            previous_holdings=pd.DataFrame(),
        )

        payload = build_institutional_workbench_payload(
            model=model,
            managers=[],
            selected_cik="0001656456",
            interest_model=None,
            mode="live",
        )

        self.assertFalse(payload["change_board"]["comparison_available"])
        self.assertIn("이전 보고 분기", payload["change_board"]["empty_reason"])

    def test_watchlist_manager_rail_keeps_seed_managers_visible_before_search_results(self) -> None:
        from app.services.institutional_portfolios import build_institutional_manager_rail

        rail = build_institutional_manager_rail(
            managers=[
                {"cik": "0009999999", "manager_name": "GENERAL INDEX FUND", "latest_report_period": "2026-03-31"},
                {"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC", "latest_report_period": "2026-03-31"},
            ],
            selected_cik="0001067983",
        )

        self.assertEqual(rail[0]["cik"], "0001067983")
        self.assertEqual(rail[0]["watchlist_label"], "Warren Buffett")
        self.assertTrue(rail[0]["selected"])
        self.assertTrue(rail[0]["external_links"])

    def test_preview_workbench_payload_is_labeled_and_not_live_data(self) -> None:
        from app.services.institutional_portfolios import build_institutional_preview_workbench_payload

        payload = build_institutional_preview_workbench_payload(message="Local 13F DB is empty.")

        self.assertEqual(payload["schema_version"], "institutional_portfolios_workbench_v1")
        self.assertEqual(payload["mode"], "preview")
        self.assertTrue(payload["data_state"]["is_preview"])
        self.assertIn("preview", payload["data_state"]["label"].lower())
        self.assertTrue(payload["allocation"]["segments"])
        self.assertFalse(payload["boundary"]["trade_signal"])
        self.assertFalse(payload["boundary"]["live_trading"])
        self.assertEqual(payload["refresh_action"]["action_id"], "collect_sec_13f_dataset")
        self.assertIn("13F", payload["refresh_action"]["label"])


class InstitutionalPortfoliosNavigationTests(unittest.TestCase):
    def test_selected_manager_resolver_keeps_watchlist_selection_outside_search_results(self) -> None:
        from app.web.institutional_portfolios import _resolve_selected_manager

        selected = _resolve_selected_manager(
            managers=[
                {
                    "cik": "0001475896",
                    "manager_name": "Asset Dedication, LLC",
                    "latest_report_period": "2026-03-31",
                }
            ],
            selected_cik="0001656456",
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected["cik"], "0001656456")
        self.assertEqual(selected["manager_name"], "APPALOOSA LP")

    def test_selected_manager_resolver_defaults_to_curated_first_portfolio(self) -> None:
        from app.web.institutional_portfolios import _resolve_selected_manager

        selected = _resolve_selected_manager(
            managers=[
                {
                    "cik": "0001475896",
                    "manager_name": "Asset Dedication, LLC",
                    "latest_report_period": "2026-03-31",
                }
            ],
            selected_cik="",
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected["cik"], "0001067983")
        self.assertEqual(selected["manager_name"], "BERKSHIRE HATHAWAY INC")

    def test_workbench_event_consumption_skips_replayed_component_value(self) -> None:
        from app.web.institutional_portfolios import _consume_workbench_event

        payload = {"id": "select_manager", "cik": "0001656456", "nonce": "n-1"}

        self.assertEqual(_consume_workbench_event(payload, None), (True, "select_manager:n-1"))
        self.assertEqual(_consume_workbench_event(payload, "select_manager:n-1"), (False, "select_manager:n-1"))

    def test_reverse_lookup_loader_uses_filing_total_without_full_holding_groupby(self) -> None:
        source = Path("finance/loaders/institutional_13f.py").read_text(encoding="utf-8")
        interest_source = source[source.index("def load_institutional_13f_interest") :]

        self.assertIn("f.table_value_total", source)
        self.assertNotIn("GROUP BY accession_number", interest_source)

    def test_popularity_loader_uses_report_period_cusip_index_without_external_sources(self) -> None:
        source = Path("finance/loaders/institutional_13f.py").read_text(encoding="utf-8")
        popularity_source = source[source.index("def load_institutional_13f_popularity_ranking") :]

        self.assertIn("FORCE INDEX(ix_report_period_cusip_cik)", source)
        self.assertIn("COUNT(DISTINCT h.cik)", source)
        self.assertNotIn("requests.", popularity_source)

    def test_missing_refresh_status_opens_refresh_panel_on_entry(self) -> None:
        from app.web.institutional_portfolios import _should_show_refresh_panel_on_entry

        self.assertTrue(
            _should_show_refresh_panel_on_entry(
                {"status": "missing", "latest_report_period": None, "rows_written": 0}
            )
        )
        self.assertTrue(
            _should_show_refresh_panel_on_entry(
                {"status": "ok", "latest_report_period": None, "rows_written": 0}
            )
        )
        self.assertFalse(
            _should_show_refresh_panel_on_entry(
                {"status": "ok", "latest_report_period": "2026-03-31", "rows_written": 123}
            )
        )

    def test_workspace_navigation_adds_institutional_portfolios_without_operations(self) -> None:
        source = Path("app/web/streamlit_app.py").read_text(encoding="utf-8")

        self.assertIn("render_institutional_portfolios_page", source)
        self.assertIn('title="Institutional Portfolios"', source)

        workspace_match = re.search(r'"Workspace": \[(.*?)\],\s*"Operations"', source, re.DOTALL)
        self.assertIsNotNone(workspace_match)
        workspace_block = workspace_match.group(1)
        self.assertIn("institutional_portfolios_page", workspace_block)
        self.assertLess(workspace_block.index("institutional_portfolios_page"), workspace_block.index("backtest_page"))

        operations_match = re.search(r'"Operations": \[(.*?)\],\s*"Reference"', source, re.DOTALL)
        self.assertIsNotNone(operations_match)
        self.assertNotIn("institutional_portfolios_page", operations_match.group(1))

    def test_ingestion_registry_exposes_sec_13f_dataset_job(self) -> None:
        from app.web.ingestion.guides import JOB_GUIDE, PROGRESS_ENABLED_ACTIONS
        from app.web.ingestion.registry import INGESTION_ACTION_REGISTRY, active_ingestion_actions

        definition = INGESTION_ACTION_REGISTRY["collect_sec_13f_dataset"]
        self.assertTrue(definition["active"])
        self.assertEqual(definition["write_behavior"], "db_write")
        self.assertIn("finance_meta.institutional_13f_holding", definition["target_tables"])
        self.assertIn("finance_meta.institutional_13f_refresh_status", definition["target_tables"])
        self.assertIn("collect_sec_13f_dataset", active_ingestion_actions())
        self.assertIn("collect_sec_13f_dataset", PROGRESS_ENABLED_ACTIONS)
        self.assertIn("SEC Form 13F", JOB_GUIDE["collect_sec_13f_dataset"]["title"])

    def test_institutional_portfolios_page_mounts_react_workbench_before_detail_tables(self) -> None:
        source = Path("app/web/institutional_portfolios.py").read_text(encoding="utf-8")

        self.assertIn("render_institutional_portfolios_workbench", source)
        self.assertIn("build_institutional_workbench_payload", source)
        self.assertIn("load_institutional_refresh_status", source)
        self.assertIn("_render_refresh_status_panel", source)
        self.assertLess(source.index("render_institutional_portfolios_workbench"), source.index("st.dataframe"))
        self.assertLess(source.index("render_institutional_portfolios_workbench"), source.index("_render_refresh_status_panel"))

    def test_refresh_strip_opens_streamlit_refresh_panel(self) -> None:
        page_source = Path("app/web/institutional_portfolios.py").read_text(encoding="utf-8")
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn("Streamlit.setComponentValue({ event: {", component_source)
        self.assertIn('id: "open_refresh"', component_source)
        self.assertIn('className="ip-freshness__action"', component_source)
        self.assertIn("갱신 설정 사용 가능", component_source)
        self.assertNotIn("refresh available below", component_source)
        self.assertIn("_workbench_event_payload", page_source)
        self.assertIn("institutional_13f_refresh_panel_expanded", page_source)
        self.assertIn('event_name = str(payload.get("id")', page_source)
        self.assertIn('event_name == "open_refresh"', page_source)
        self.assertIn("expanded=refresh_panel_expanded", page_source)
        self.assertIn("_render_requested_refresh_status_panel", page_source)
        self.assertLess(
            page_source.index("_render_requested_refresh_status_panel(refresh_status)"),
            page_source.index("manager_result = load_institutional_manager_choices"),
        )

    def test_workbench_preserves_scroll_and_exposes_security_detail_and_popularity_tab(self) -> None:
        page_source = Path("app/web/institutional_portfolios.py").read_text(encoding="utf-8")
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn('key="institutional_portfolios_workbench"', page_source)
        self.assertNotIn('key=f"institutional_portfolios_{', page_source)
        self.assertIn("restoreHostScroll", component_source)
        self.assertIn("managerRailRef", component_source)
        self.assertIn('"popularity"', component_source)
        self.assertIn("기관 보유 랭킹", component_source)
        self.assertIn("ip-security-detail", component_source)
        self.assertIn("ip-performance-panel", component_source)

    def test_selected_security_price_collection_button_routes_through_python_job_boundary(self) -> None:
        page_source = Path("app/web/institutional_portfolios.py").read_text(encoding="utf-8")
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn("run_collect_ohlcv", page_source)
        self.assertIn('event_name == "collect_price_history"', page_source)
        self.assertIn("institutional_price_refresh_result", page_source)
        self.assertIn('id: "collect_price_history"', component_source)
        self.assertIn("가격 데이터 수집", component_source)
        self.assertIn("ip-price-action", component_source)

    def test_selected_security_chart_supports_hover_candles_guides_and_pan_controls(self) -> None:
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")
        style_source = Path("app/web/streamlit_components/institutional_portfolios_workbench/src/style.css").read_text(
            encoding="utf-8"
        )

        self.assertIn("function InteractiveSecurityChart", component_source)
        self.assertIn("setHoveredIndex", component_source)
        self.assertIn("ip-chart-tooltip", component_source)
        self.assertIn("ip-chart-crosshair", component_source)
        self.assertIn("ip-chart-high-low-guide", component_source)
        self.assertIn("ip-candle", component_source)
        self.assertIn("ip-chart-range", component_source)
        self.assertIn("panWindow", component_source)
        self.assertIn("캔들", component_source)
        self.assertIn("strokeDasharray", component_source)
        self.assertIn(".ip-chart-tooltip", style_source)
        self.assertIn(".ip-chart-range", style_source)
        self.assertIn(".ip-chart-style-toggle", style_source)
        self.assertIn("stroke-dasharray", style_source)


if __name__ == "__main__":
    unittest.main()
