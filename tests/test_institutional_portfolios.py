from __future__ import annotations

import re
import sys
import unittest
from pathlib import Path

import pandas as pd

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))


def _component_source() -> str:
    return Path(
        "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
    ).read_text(encoding="utf-8")


def _component_style_source() -> str:
    return Path(
        "app/web/streamlit_components/institutional_portfolios_workbench/src/style.css"
    ).read_text(encoding="utf-8")


def _css_rule(style_source: str, *selectors: str) -> str:
    selector_pattern = r"\s*,\s*".join(re.escape(selector) for selector in selectors)
    match = re.search(rf"(?:^|[}}\n])\s*{selector_pattern}\s*\{{(?P<body>[^}}]*)\}}", style_source)
    if not match:
        raise AssertionError(f"CSS rule not found: {', '.join(selectors)}")
    return match.group("body")


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
    def test_workbench_v2_keeps_all_holdings_for_client_side_explorer(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model, build_institutional_workbench_payload

        holdings = pd.DataFrame(
            [
                {
                    "issuer_name": f"Issuer {index:04d}",
                    "cusip": f"{index:09d}",
                    "reported_value": 1_000 - index,
                    "shares_or_principal_amount": 10,
                }
                for index in range(993)
            ]
        )
        model = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=holdings,
        )
        payload = build_institutional_workbench_payload(
            model=model,
            managers=[],
            selected_cik="0001067983",
            interest_model=None,
        )

        self.assertEqual(payload["schema_version"], "institutional_portfolios_workbench_v2")
        self.assertEqual(payload["holdings_explorer"]["default_page_size"], 50)
        self.assertEqual(len(payload["holdings_explorer"]["rows"]), 993)
        self.assertEqual(payload["coverage"]["holding_count_total"], 993)

    def test_workbench_v2_suppresses_change_items_without_previous_filing(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model, build_institutional_workbench_payload

        model = build_institutional_portfolio_model(
            manager={"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=pd.DataFrame(
                [
                    {
                        "issuer_name": "APPLE INC",
                        "holding_symbol": "AAPL",
                        "cusip": "037833100",
                        "reported_value": 750,
                        "shares_or_principal_amount": 10,
                        "sector": "Technology",
                    },
                    {
                        "issuer_name": "UNMAPPED HOLDING",
                        "cusip": "999999999",
                        "reported_value": 250,
                        "shares_or_principal_amount": 10,
                    },
                ]
            ),
        )
        payload = build_institutional_workbench_payload(
            model=model,
            managers=[],
            selected_cik="0001067983",
            interest_model=None,
        )

        self.assertFalse(payload["change_board"]["comparison_available"])
        self.assertEqual(payload["change_board"]["groups"], {})
        self.assertEqual(payload["context_summary"]["comparison_state"], "unavailable")
        self.assertEqual(payload["coverage"]["holding_count_total"], 2)
        self.assertEqual(payload["coverage"]["holding_count_mapped"], 1)
        self.assertEqual(payload["coverage"]["holding_count_unmapped"], 1)
        self.assertIn("mapped_weight_pct", payload["coverage"])
        self.assertIn("performance_covered_weight_pct", payload["coverage"])

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
        self.assertEqual(detail["price_action"]["state"], "price_missing")
        self.assertEqual(detail["price_action"]["reason_code"], "price_history_missing")

    def test_selected_security_model_blocks_price_action_when_symbol_mapping_is_missing(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model, build_institutional_selected_security_model

        portfolio = build_institutional_portfolio_model(
            manager={"cik": "0001536411", "manager_name": "DUQUESNE FAMILY OFFICE LLC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=pd.DataFrame(
                [
                    {
                        "cusip": "632307104",
                        "holding_symbol": None,
                        "issuer_name": "NATERA INC",
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
            query="632307104",
            interest_model={"holders": [], "holder_count": 0},
            price_history=pd.DataFrame(),
        )

        self.assertIsNone(detail["security"]["symbol"])
        self.assertFalse(detail["price_action"]["available"])
        self.assertEqual(detail["price_action"]["state"], "symbol_missing")
        self.assertEqual(detail["price_action"]["reason_code"], "cusip_symbol_mapping_missing")
        self.assertIn("티커 매핑", detail["price_action"]["reason"])

    def test_selected_security_model_resolves_mapped_interest_holder_outside_selected_portfolio(self) -> None:
        from app.services.institutional_portfolios import build_institutional_selected_security_model

        portfolio = {
            "summary": {"latest_report_period": "2026-03-31"},
            "holdings": [
                {
                    "cusip": "037833100",
                    "holding_symbol": "AAPL",
                    "issuer_name": "APPLE INC",
                    "weight_pct": 100.0,
                    "reported_value": 1000,
                }
            ],
        }
        interest = {
            "query": "NVDA",
            "holder_count": 1,
            "holders": [
                {
                    "manager_name": "OTHER MANAGER",
                    "cik": "0000000001",
                    "issuer_name": "NVIDIA CORP",
                    "holding_symbol": "NVDA",
                    "cusip": "67066G104",
                    "weight_pct": 8.5,
                    "reported_value": 250,
                }
            ],
        }
        prices = pd.DataFrame(
            [
                {"symbol": "NVDA", "date": "2026-03-31", "close": 100.0},
                {"symbol": "NVDA", "date": "2026-04-01", "close": 103.0},
            ]
        )

        detail = build_institutional_selected_security_model(
            portfolio_model=portfolio,
            query="nvda",
            interest_model=interest,
            price_history=prices,
        )

        self.assertEqual(detail["status"], "ok")
        self.assertEqual(detail["query"], "NVDA")
        self.assertEqual(detail["security"]["symbol"], "NVDA")
        self.assertEqual(detail["security"]["issuer_name"], "NVIDIA CORP")
        self.assertFalse(detail["portfolio_position"]["available"])
        self.assertEqual(detail["portfolio_position"]["weight_label"], "-")
        self.assertTrue(detail["charts"]["daily"]["points"])
        self.assertEqual(detail["price_action"]["state"], "ready")
        self.assertEqual(detail["holder_count"], 1)

    def test_selected_security_loader_loads_prices_for_interest_identity_outside_portfolio(self) -> None:
        import app.services.institutional_portfolios as service

        calls: list[dict[str, object]] = []
        original_loader = service.load_price_history

        def fake_price_loader(**kwargs: object) -> pd.DataFrame:
            calls.append(dict(kwargs))
            return pd.DataFrame(
                [
                    {"symbol": "NVDA", "date": "2026-03-31", "close": 100.0},
                    {"symbol": "NVDA", "date": "2026-04-01", "close": 103.0},
                ]
            )

        try:
            service.load_price_history = fake_price_loader
            detail = service.load_institutional_selected_security_model(
                portfolio_model={
                    "summary": {"latest_report_period": "2026-03-31"},
                    "holdings": [
                        {
                            "cusip": "037833100",
                            "holding_symbol": "AAPL",
                            "issuer_name": "APPLE INC",
                            "weight_pct": 100.0,
                            "reported_value": 1000,
                        }
                    ],
                },
                query="Nvidia Corp",
                interest_model={
                    "query": "NVIDIA CORP",
                    "holder_count": 1,
                    "holders": [
                        {
                            "manager_name": "OTHER MANAGER",
                            "issuer_name": "NVIDIA CORP",
                            "holding_symbol": "NVDA",
                            "cusip": "67066G104",
                        }
                    ],
                },
            )
        finally:
            service.load_price_history = original_loader

        self.assertEqual(calls, [{"symbols": ["NVDA"], "start": "2026-03-31", "timeframe": "1d"}])
        self.assertEqual(detail["status"], "ok")
        self.assertEqual(detail["security"]["symbol"], "NVDA")
        self.assertFalse(detail["portfolio_position"]["available"])
        self.assertTrue(detail["charts"]["daily"]["points"])

    def test_selected_security_model_rejects_ambiguous_interest_identities_for_issuer_query(self) -> None:
        from app.services.institutional_portfolios import build_institutional_selected_security_model

        detail = build_institutional_selected_security_model(
            portfolio_model={"summary": {"latest_report_period": "2026-03-31"}, "holdings": []},
            query="Alpha",
            interest_model={
                "query": "ALPHA",
                "holder_count": 2,
                "holders": [
                    {
                        "manager_name": "FIRST MANAGER",
                        "issuer_name": "ALPHA SOFTWARE INC",
                        "holding_symbol": "MSFT",
                        "cusip": "594918104",
                    },
                    {
                        "manager_name": "SECOND MANAGER",
                        "issuer_name": "ALPHABET INC",
                        "holding_symbol": "GOOGL",
                        "cusip": "02079K305",
                    },
                ],
            },
            price_history=pd.DataFrame(),
        )

        self.assertEqual(detail["status"], "ambiguous")
        self.assertIn("정확한 ticker 또는 CUSIP", detail["empty_text"])
        self.assertNotIn("security", detail)
        self.assertNotIn("price_action", detail)
        self.assertEqual(detail["holder_count"], 2)

    def test_selected_security_model_exact_symbol_or_cusip_resolves_among_multiple_interest_identities(self) -> None:
        from app.services.institutional_portfolios import build_institutional_selected_security_model

        interest_model = {
            "holder_count": 2,
            "holders": [
                {
                    "manager_name": "FIRST MANAGER",
                    "issuer_name": "MICROSOFT CORP",
                    "holding_symbol": "MSFT",
                    "cusip": "594918104",
                },
                {
                    "manager_name": "SECOND MANAGER",
                    "issuer_name": "ALPHABET INC",
                    "holding_symbol": "GOOGL",
                    "cusip": "02079K305",
                },
            ],
        }

        for query, expected_symbol in [("msft", "MSFT"), ("02079K305", "GOOGL")]:
            with self.subTest(query=query):
                detail = build_institutional_selected_security_model(
                    portfolio_model={"summary": {"latest_report_period": "2026-03-31"}, "holdings": []},
                    query=query,
                    interest_model=interest_model,
                    price_history=pd.DataFrame(),
                )
                self.assertEqual(detail["status"], "ok")
                self.assertEqual(detail["security"]["symbol"], expected_symbol)
                self.assertFalse(detail["portfolio_position"]["available"])

    def test_selected_security_loader_does_not_load_price_for_ambiguous_interest_identities(self) -> None:
        import app.services.institutional_portfolios as service

        calls: list[dict[str, object]] = []
        original_loader = service.load_price_history

        def fake_price_loader(**kwargs: object) -> pd.DataFrame:
            calls.append(dict(kwargs))
            return pd.DataFrame()

        try:
            service.load_price_history = fake_price_loader
            detail = service.load_institutional_selected_security_model(
                portfolio_model={"summary": {"latest_report_period": "2026-03-31"}, "holdings": []},
                query="Alpha",
                interest_model={
                    "query": "ALPHA",
                    "holder_count": 2,
                    "holders": [
                        {"issuer_name": "ALPHA SOFTWARE INC", "holding_symbol": "MSFT", "cusip": "594918104"},
                        {"issuer_name": "ALPHABET INC", "holding_symbol": "GOOGL", "cusip": "02079K305"},
                    ],
                },
            )
        finally:
            service.load_price_history = original_loader

        self.assertEqual(calls, [])
        self.assertEqual(detail["status"], "ambiguous")

    def test_portfolio_model_marks_ambiguous_cusip_symbol_mapping_unresolved(self) -> None:
        from app.services.institutional_portfolios import build_institutional_portfolio_model

        model = build_institutional_portfolio_model(
            manager={"cik": "0001536411", "manager_name": "DUQUESNE FAMILY OFFICE LLC"},
            latest_filing={"period_of_report": "2026-03-31", "filing_date": "2026-05-15"},
            latest_holdings=pd.DataFrame(
                [
                    {
                        "cusip": "46137V357",
                        "holding_symbol": "AVGO",
                        "symbol_source": "ambiguous_cusip_symbol_map",
                        "issuer_name": "INVESCO EXCHANGE TRADED FD T",
                        "reported_value": 1200,
                        "shares_or_principal_amount": 40,
                    }
                ]
            ),
            previous_filing=None,
            previous_holdings=pd.DataFrame(),
        )

        holding = model["holdings"][0]
        self.assertIsNone(holding["holding_symbol"])
        self.assertEqual(holding["symbol_source"], "ambiguous_cusip_symbol_map")
        self.assertEqual(holding["mapping_status"], "ambiguous")

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

        self.assertEqual(payload["schema_version"], "institutional_portfolios_workbench_v2")
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

    def test_watchlist_manager_rail_includes_expanded_guru_alias_seeds(self) -> None:
        from app.services.institutional_portfolios import build_institutional_manager_rail

        rail = build_institutional_manager_rail(
            managers=[
                {"cik": "0001536411", "manager_name": "Duquesne Family Office LLC", "latest_report_period": "2026-03-31"},
            ],
            selected_cik="0001536411",
        )

        duquesne = next(item for item in rail if item["cik"] == "0001536411")
        self.assertEqual(duquesne["watchlist_label"], "Stanley Druckenmiller")
        self.assertIn("Druckenmiller", duquesne["search_aliases"])
        self.assertTrue(duquesne["selected"])

    def test_watchlist_manager_rail_respects_search_result_order(self) -> None:
        from app.services.institutional_portfolios import build_institutional_manager_rail

        rail = build_institutional_manager_rail(
            managers=[
                {"cik": "0001536411", "manager_name": "Duquesne Family Office LLC", "latest_report_period": "2026-03-31"},
                {"cik": "0001067983", "manager_name": "BERKSHIRE HATHAWAY INC", "latest_report_period": "2026-03-31"},
            ],
            selected_cik="0001536411",
            preserve_manager_order=True,
        )

        self.assertEqual(rail[0]["cik"], "0001536411")
        self.assertEqual(rail[0]["watchlist_label"], "Stanley Druckenmiller")
        self.assertTrue(rail[0]["selected"])

    def test_workbench_payload_exposes_zero_result_manager_search_without_replacing_context(self) -> None:
        from app.services.institutional_portfolios import build_institutional_workbench_payload

        payload = build_institutional_workbench_payload(
            model={
                "summary": {
                    "manager_name": "BERKSHIRE HATHAWAY INC",
                    "cik": "0001067983",
                    "latest_report_period": "2026-03-31",
                },
                "holdings": [],
                "changes": [],
                "sector_exposure": [],
            },
            managers=[],
            selected_cik="0001067983",
            interest_model=None,
            manager_search_query="No Such Manager",
            preserve_manager_order=True,
        )

        self.assertEqual(payload["mode"], "live")
        self.assertEqual(payload["hero"]["manager_name"], "BERKSHIRE HATHAWAY INC")
        self.assertEqual(payload["manager_picker"]["search_query"], "No Such Manager")
        self.assertEqual(payload["manager_picker"]["search_result_count"], 0)
        self.assertEqual(payload["manager_picker"]["search_state"], "empty")
        self.assertIn("검색 결과", payload["manager_picker"]["search_empty_message"])

    def test_manager_choices_search_uses_watchlist_alias_before_exact_sec_name(self) -> None:
        import app.services.institutional_portfolios as service

        calls: list[object] = []
        original_search = service.load_institutional_13f_managers
        original_by_ciks = service.load_institutional_13f_managers_by_ciks

        def fake_search(query: str | None = None, *, limit: int = 100) -> pd.DataFrame:
            calls.append(("search", query))
            return pd.DataFrame()

        def fake_by_ciks(ciks: list[str]) -> pd.DataFrame:
            calls.append(("by_ciks", tuple(ciks)))
            return pd.DataFrame(
                [
                    {
                        "cik": "0001067983",
                        "manager_name": "Berkshire Hathaway Inc",
                        "latest_report_period": "2026-03-31",
                        "latest_filing_date": "2026-05-15",
                    },
                    {
                        "cik": "0001536411",
                        "manager_name": "Duquesne Family Office LLC",
                        "latest_report_period": "2026-03-31",
                        "latest_filing_date": "2026-05-15",
                    }
                ]
            )

        try:
            service.load_institutional_13f_managers = fake_search
            service.load_institutional_13f_managers_by_ciks = fake_by_ciks
            result = service.load_institutional_manager_choices("드러켄밀러")
        finally:
            service.load_institutional_13f_managers = original_search
            service.load_institutional_13f_managers_by_ciks = original_by_ciks

        self.assertEqual(result["status"], "ok")
        self.assertEqual(result["managers"][0]["cik"], "0001536411")
        self.assertIn(("search", "드러켄밀러"), calls)

    def test_preview_workbench_payload_is_labeled_and_not_live_data(self) -> None:
        from app.services.institutional_portfolios import build_institutional_preview_workbench_payload

        payload = build_institutional_preview_workbench_payload(message="Local 13F DB is empty.")

        self.assertEqual(payload["schema_version"], "institutional_portfolios_workbench_v2")
        self.assertEqual(payload["mode"], "preview")
        self.assertTrue(payload["data_state"]["is_preview"])
        self.assertIn("preview", payload["data_state"]["label"].lower())
        self.assertTrue(payload["allocation"]["segments"])
        self.assertFalse(payload["boundary"]["trade_signal"])
        self.assertFalse(payload["boundary"]["live_trading"])
        self.assertEqual(payload["refresh_action"]["action_id"], "collect_sec_13f_dataset")
        self.assertIn("13F", payload["refresh_action"]["label"])


class InstitutionalPortfoliosNavigationTests(unittest.TestCase):
    def test_context_hero_basis_and_controls_share_alignment_contract(self) -> None:
        component_source = _component_source()
        style_source = _component_style_source()
        hero_grid_rule = _css_rule(style_source, ".ip-context-hero__grid")
        controls_rule = _css_rule(style_source, ".ip-context-controls")
        basis_span_rule = _css_rule(
            style_source,
            ".ip-context-basis__snapshot",
            ".ip-context-basis .ip-source-link",
        )
        shared_label_rule = _css_rule(
            style_source,
            ".ip-manager-search > label",
            ".ip-context-control-label",
        )
        freshness_rule = _css_rule(style_source, ".ip-freshness")
        freshness_action_rule = _css_rule(style_source, ".ip-freshness__action")
        freshness_period_rule = _css_rule(style_source, ".ip-freshness strong")
        freshness_time_rule = _css_rule(style_source, ".ip-freshness em")
        mobile_style_source = style_source[
            style_source.index("@media (max-width: 720px) {") : style_source.index("@media (max-width: 420px) {")
        ]
        mobile_freshness_rule = _css_rule(mobile_style_source, ".ip-freshness")

        self.assertIn('className="ip-context-basis__snapshot"', component_source)
        self.assertIn('className="ip-freshness-block"', component_source)
        self.assertIn('className="ip-context-control-label">데이터 기준</span>', component_source)
        self.assertIn("--ip-context-columns: minmax(0, 1.45fr) minmax(320px, 0.75fr);", style_source)
        for grid_rule in (hero_grid_rule, controls_rule):
            self.assertIn("grid-template-columns: var(--ip-context-columns);", grid_rule)
            self.assertIn("gap: 18px;", grid_rule)
        self.assertIn("align-items: start;", controls_rule)
        self.assertIn("grid-column: 1 / -1;", basis_span_rule)
        for declaration in (
            "display: block;",
            "min-height: 18px;",
            "margin-bottom: 6px;",
            "color: #334155;",
            "font-size: 12px;",
            "font-weight: 800;",
            "line-height: 18px;",
        ):
            self.assertIn(declaration, shared_label_rule)
        self.assertIn('grid-template-areas: "action period" "time time";', freshness_rule)
        self.assertIn("grid-area: action;", freshness_action_rule)
        self.assertIn("grid-area: period;", freshness_period_rule)
        self.assertIn("grid-area: time;", freshness_time_rule)
        self.assertIn("white-space: normal;", freshness_time_rule)
        self.assertIn('grid-template-areas: "action" "period" "time";', mobile_freshness_rule)

        build_dir = Path("app/web/streamlit_components/institutional_portfolios_workbench/component_static")
        index_source = (build_dir / "index.html").read_text(encoding="utf-8")
        asset_paths = re.findall(r'(?:src|href)="\./(assets/[^"]+)"', index_source)
        css_paths = [asset_path for asset_path in asset_paths if asset_path.endswith(".css")]
        javascript_paths = [asset_path for asset_path in asset_paths if asset_path.endswith(".js")]
        self.assertEqual(len(css_paths), 1)
        self.assertEqual(len(javascript_paths), 1)
        runtime_css = (build_dir / css_paths[0]).read_text(encoding="utf-8")
        runtime_javascript = (build_dir / javascript_paths[0]).read_text(encoding="utf-8")
        runtime_hero_rule = _css_rule(runtime_css, ".ip-hero")
        runtime_hero_grid_rule = _css_rule(runtime_css, ".ip-context-hero__grid")
        runtime_controls_rule = _css_rule(runtime_css, ".ip-context-controls")
        runtime_basis_span_rule = _css_rule(
            runtime_css,
            ".ip-context-basis__snapshot",
            ".ip-context-basis .ip-source-link",
        )
        runtime_freshness_rule = _css_rule(runtime_css, ".ip-freshness")
        runtime_freshness_action_rule = _css_rule(runtime_css, ".ip-freshness__action")
        runtime_freshness_period_rule = _css_rule(runtime_css, ".ip-freshness strong")
        runtime_freshness_time_rule = _css_rule(runtime_css, ".ip-freshness em")
        runtime_mobile_style = runtime_css[
            runtime_css.index("@media(max-width:720px){") : runtime_css.index("@media(max-width:420px){")
        ]
        runtime_mobile_freshness_rule = _css_rule(runtime_mobile_style, ".ip-freshness")
        self.assertRegex(
            runtime_hero_rule,
            r"--ip-context-columns:\s*minmax\(0,\s*1\.45fr\)\s*minmax\(320px,\s*0?\.75fr\)",
        )
        for runtime_grid_rule in (runtime_hero_grid_rule, runtime_controls_rule):
            self.assertIn("grid-template-columns:var(--ip-context-columns)", runtime_grid_rule)
            self.assertIn("gap:18px", runtime_grid_rule)
        self.assertIn("grid-column:1 / -1", runtime_basis_span_rule)
        self.assertIn('grid-template-areas:"action period" "time time"', runtime_freshness_rule)
        self.assertIn("grid-area:action", runtime_freshness_action_rule)
        self.assertIn("grid-area:period", runtime_freshness_period_rule)
        self.assertIn("grid-area:time", runtime_freshness_time_rule)
        self.assertIn("white-space:normal", runtime_freshness_time_rule)
        self.assertIn('grid-template-areas:"action" "period" "time"', runtime_mobile_freshness_rule)
        self.assertIn("ip-freshness-block", runtime_css)
        self.assertIn("ip-freshness-block", runtime_javascript)
        self.assertIn("데이터 기준", runtime_javascript)
        self.assertNotIn("slice(0,80)", runtime_javascript)
        self.assertNotIn("slice(0, 80)", runtime_javascript)

    def test_manager_rail_shows_complete_cards_and_wraps_labels(self) -> None:
        style_source = _component_style_source()
        rail_rule = _css_rule(style_source, ".ip-manager-rail")
        favorites_rule = _css_rule(style_source, ".ip-manager-favorites")
        compact_card_rule = _css_rule(style_source, ".ip-manager-favorites .ip-manager-tab")
        text_rule = _css_rule(style_source, ".ip-manager-tab strong", ".ip-manager-tab span")
        tablet_style = style_source[
            style_source.index("@media (max-width: 980px) {") : style_source.index("@media (max-width: 720px) {")
        ]
        mobile_style = style_source[
            style_source.index("@media (max-width: 720px) {") : style_source.index("@media (max-width: 420px) {")
        ]
        for declaration in (
            "display: grid;",
            "grid-auto-flow: column;",
            "grid-auto-columns: var(--ip-manager-card-width);",
            "align-items: stretch;",
            "--ip-manager-card-width: calc((100% - 24px) / 4);",
            "scroll-snap-type: x mandatory;",
        ):
            self.assertIn(declaration, rail_rule)
        self.assertIn("margin: 0 0 12px;", favorites_rule)
        self.assertIn("padding-bottom: 10px;", favorites_rule)
        self.assertIn("min-width: 0;", compact_card_rule)
        self.assertIn("width: 100%;", compact_card_rule)
        self.assertIn("height: auto;", compact_card_rule)
        self.assertIn("scroll-snap-align: start;", compact_card_rule)
        self.assertIn("scroll-snap-stop: always;", compact_card_rule)
        for declaration in (
            "overflow: visible;",
            "text-overflow: clip;",
            "white-space: normal;",
            "overflow-wrap: anywhere;",
        ):
            self.assertIn(declaration, text_rule)
        tablet_rail_rule = _css_rule(tablet_style, ".ip-manager-rail")
        mobile_rail_rule = _css_rule(mobile_style, ".ip-manager-rail")
        self.assertIn("--ip-manager-card-width: calc((100% - 16px) / 3);", tablet_rail_rule)
        self.assertIn("--ip-manager-card-width: 100%;", mobile_rail_rule)

        build_dir = Path("app/web/streamlit_components/institutional_portfolios_workbench/component_static")
        index_source = (build_dir / "index.html").read_text(encoding="utf-8")
        css_paths = re.findall(r'href="\./(assets/[^"]+\.css)"', index_source)
        self.assertEqual(len(css_paths), 1)
        runtime_css = (build_dir / css_paths[0]).read_text(encoding="utf-8")
        runtime_rail_rule = _css_rule(runtime_css, ".ip-manager-rail")
        runtime_favorites_rule = _css_rule(runtime_css, ".ip-manager-favorites")
        runtime_card_rule = _css_rule(runtime_css, ".ip-manager-favorites .ip-manager-tab")
        runtime_text_rule = _css_rule(runtime_css, ".ip-manager-tab strong", ".ip-manager-tab span")
        runtime_tablet_marker = "@media(max-width:980px){"
        runtime_mobile_marker = "@media(max-width:720px){"
        runtime_tablet_style = runtime_css[
            runtime_css.index(runtime_tablet_marker) + len(runtime_tablet_marker) : runtime_css.index(
                runtime_mobile_marker
            )
        ]
        runtime_mobile_style = runtime_css[
            runtime_css.index(runtime_mobile_marker) + len(runtime_mobile_marker) : runtime_css.index(
                "@media(max-width:420px){"
            )
        ]
        runtime_tablet_rule = _css_rule(runtime_tablet_style, ".ip-manager-rail")
        runtime_mobile_rule = _css_rule(runtime_mobile_style, ".ip-manager-rail")
        runtime_rail_compact = re.sub(r"\s+", "", runtime_rail_rule)
        runtime_tablet_compact = re.sub(r"\s+", "", runtime_tablet_rule)
        runtime_mobile_compact = re.sub(r"\s+", "", runtime_mobile_rule)

        self.assertIn("display:grid", runtime_rail_rule)
        self.assertIn("grid-auto-flow:column", runtime_rail_rule)
        self.assertIn("grid-auto-columns:var(--ip-manager-card-width)", runtime_rail_rule)
        self.assertIn("align-items:stretch", runtime_rail_rule)
        self.assertIn("--ip-manager-card-width:calc((100%-24px)/4)", runtime_rail_compact)
        self.assertIn("scroll-snap-type:x mandatory", runtime_rail_rule)
        self.assertIn("margin:0 0 12px", runtime_favorites_rule)
        self.assertIn("padding-bottom:10px", runtime_favorites_rule)
        self.assertIn("scroll-snap-align:start", runtime_card_rule)
        self.assertIn("scroll-snap-stop:always", runtime_card_rule)
        self.assertIn("white-space:normal", runtime_text_rule)
        self.assertIn("overflow-wrap:anywhere", runtime_text_rule)
        self.assertIn("--ip-manager-card-width:calc((100%-16px)/3)", runtime_tablet_compact)
        self.assertIn("--ip-manager-card-width:100%", runtime_mobile_compact)

    def test_workbench_v2_has_complete_holdings_explorer_and_explicit_security_search(self) -> None:
        component_source = _component_source()
        self.assertIn('schema_version: "institutional_portfolios_workbench_v2"', component_source)
        self.assertNotIn("rows.slice(0, 80)", component_source)
        self.assertIn("HOLDINGS_PAGE_SIZE = 50", component_source)
        self.assertIn('id: "security_search"', component_source)
        self.assertIn("holdingSearch", component_source)
        self.assertIn("mappingFilter", component_source)
        self.assertIn("holdingSort", component_source)
        self.assertIn("visibleHoldings", component_source)
        self.assertIn("INSTITUTIONAL PORTFOLIO CONTEXT", component_source)

    def test_workbench_fix_contract_covers_manager_search_reset_coverage_other_and_mapping_badges(self) -> None:
        component_source = _component_source()
        page_source = Path("app/web/institutional_portfolios.py").read_text(encoding="utf-8")
        render_source = page_source[page_source.index("def render_institutional_portfolios_page(") :]

        self.assertIn("managerSearch", component_source)
        self.assertIn('id: "manager_search"', component_source)
        self.assertIn("submitManagerSearch", component_source)
        self.assertIn("resetHoldingsExplorer", component_source)
        self.assertIn("payload?.manager_picker.selected_cik", component_source)
        self.assertIn("payload.coverage.holding_count_unmapped.toLocaleString()", component_source)
        self.assertIn("payload.coverage.holding_count_ambiguous.toLocaleString()", component_source)
        self.assertIn("allocationOtherCount", component_source)
        self.assertIn("allocationOtherWeight", component_source)
        self.assertIn('mapped ? "ticker 연결됨"', component_source)
        self.assertNotIn('search = st.text_input(', render_source)
        self.assertIn('event_name == "manager_search"', page_source)

    def test_workbench_review_fix_contract_connects_normalized_state_and_explicit_empty_ux(self) -> None:
        component_source = _component_source()
        pending_effect = component_source[
            component_source.index('if (pendingAction.kind === "manager"') : component_source.index(
                "}, [payload, pendingAction]);"
            )
        ]
        unresolved_handler = component_source[
            component_source.index("const handleHoldingDrilldown") : component_source.index(
                "const handleAllocationDrilldown"
            )
        ]
        manager_submit = component_source[
            component_source.index("const submitManagerSearch") : component_source.index(
                "const handleManagerSelect"
            )
        ]

        self.assertIn('from "./workbenchState"', component_source)
        self.assertIn("filterSortAndPaginateHoldings", component_source)
        self.assertIn("queriesMatch(payload.interest.query, pendingAction.query)", pending_effect)
        self.assertIn("ip-manager-search-empty", component_source)
        self.assertIn("search_result_count", component_source)
        self.assertIn("detail?.portfolio_position?.available === false", component_source)
        self.assertIn("ip-security-position-unavailable", component_source)
        self.assertIn('setActiveView("holdings")', unresolved_handler)
        self.assertIn("setLocalSelectedQuery(\"\")", manager_submit)
        self.assertIn("setSecuritySearch(\"\")", manager_submit)

    def test_tracked_workbench_bundle_serves_v2_runtime_contract(self) -> None:
        build_dir = Path("app/web/streamlit_components/institutional_portfolios_workbench/component_static")
        index_source = (build_dir / "index.html").read_text(encoding="utf-8")
        asset_paths = re.findall(r'(?:src|href)="\./(assets/[^"]+)"', index_source)

        self.assertGreaterEqual(len(asset_paths), 2)
        for asset_path in asset_paths:
            self.assertTrue((build_dir / asset_path).exists(), asset_path)
        javascript = "\n".join(
            (build_dir / asset_path).read_text(encoding="utf-8")
            for asset_path in asset_paths
            if asset_path.endswith(".js")
        )
        self.assertIn("institutional_portfolios_workbench_v2", javascript)
        self.assertIn("INSTITUTIONAL PORTFOLIO CONTEXT", javascript)
        self.assertIn("manager_search", javascript)
        self.assertNotIn("slice(0,80)", javascript)

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

    def test_selected_manager_resolver_prefers_query_match_during_search(self) -> None:
        from app.web.institutional_portfolios import _resolve_selected_manager

        selected = _resolve_selected_manager(
            managers=[
                {
                    "cik": "0001536411",
                    "manager_name": "Duquesne Family Office LLC",
                    "latest_report_period": "2026-03-31",
                    "query_match": True,
                },
                {
                    "cik": "0001067983",
                    "manager_name": "BERKSHIRE HATHAWAY INC",
                    "latest_report_period": "2026-03-31",
                    "query_match": False,
                },
            ],
            selected_cik="0001067983",
            search_active=True,
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected["cik"], "0001536411")

    def test_selected_manager_resolver_preserves_curated_live_context_when_search_has_no_results(self) -> None:
        from app.web.institutional_portfolios import _resolve_selected_manager

        selected = _resolve_selected_manager(
            managers=[],
            selected_cik="0001067983",
            search_active=True,
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected["cik"], "0001067983")
        self.assertEqual(selected["manager_name"], "BERKSHIRE HATHAWAY INC")

    def test_selected_manager_resolver_preserves_generic_live_context_when_search_has_no_results(self) -> None:
        from app.services.institutional_portfolios import build_institutional_workbench_payload
        from app.web.institutional_portfolios import _resolve_selected_manager

        selected = _resolve_selected_manager(
            managers=[],
            selected_cik="1234567",
            search_active=True,
        )

        self.assertIsNotNone(selected)
        self.assertEqual(selected["cik"], "0001234567")

        payload = build_institutional_workbench_payload(
            model={
                "summary": {
                    "manager_name": "GENERIC LIVE MANAGER LLC",
                    "cik": "0001234567",
                    "latest_report_period": "2026-03-31",
                },
                "holdings": [],
                "changes": [],
                "sector_exposure": [],
            },
            managers=[],
            selected_cik=selected["cik"],
            interest_model=None,
            manager_search_query="No Such Manager",
            preserve_manager_order=True,
        )

        self.assertEqual(payload["mode"], "live")
        self.assertEqual(payload["hero"]["manager_name"], "GENERIC LIVE MANAGER LLC")
        self.assertEqual(payload["manager_picker"]["search_state"], "empty")

    def test_workbench_event_consumption_skips_replayed_component_value(self) -> None:
        from app.web.institutional_portfolios import _consume_workbench_event

        payload = {"id": "select_manager", "cik": "0001656456", "nonce": "n-1"}

        self.assertEqual(_consume_workbench_event(payload, None), (True, "select_manager:n-1"))
        self.assertEqual(_consume_workbench_event(payload, "select_manager:n-1"), (False, "select_manager:n-1"))

    def test_holding_drilldown_and_security_search_events_update_selected_security_state(self) -> None:
        import app.web.institutional_portfolios as page

        class FakeStreamlit:
            def __init__(self) -> None:
                self.session_state: dict[str, object] = {}
                self.rerun_count = 0

            def rerun(self) -> None:
                self.rerun_count += 1

        original_streamlit = page.st
        try:
            for event_name in ["holding_drilldown", "security_search"]:
                with self.subTest(event_name=event_name):
                    fake_streamlit = FakeStreamlit()
                    page.st = fake_streamlit
                    page._handle_workbench_event({"id": event_name, "query": " AAPL ", "nonce": event_name})

                    self.assertEqual(fake_streamlit.session_state["institutional_interest_query"], "AAPL")
                    self.assertTrue(fake_streamlit.session_state["institutional_interest_query_needs_load"])
                    self.assertEqual(fake_streamlit.session_state["institutional_price_refresh_result"], {})
                    self.assertEqual(fake_streamlit.rerun_count, 1)
        finally:
            page.st = original_streamlit

    def test_manager_search_event_updates_existing_manager_query_state_on_submit(self) -> None:
        import app.web.institutional_portfolios as page

        class FakeStreamlit:
            def __init__(self) -> None:
                self.session_state: dict[str, object] = {}
                self.rerun_count = 0

            def rerun(self) -> None:
                self.rerun_count += 1

        original_streamlit = page.st
        fake_streamlit = FakeStreamlit()
        try:
            page.st = fake_streamlit
            page._handle_workbench_event(
                {"id": "manager_search", "query": " Pershing Square ", "nonce": "manager-search-1"}
            )
        finally:
            page.st = original_streamlit

        self.assertEqual(
            fake_streamlit.session_state["institutional_portfolios_manager_search"],
            "Pershing Square",
        )
        self.assertEqual(fake_streamlit.rerun_count, 1)

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

    def test_workbench_uses_two_tier_portfolio_and_security_tabs(self) -> None:
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")
        style_source = Path("app/web/streamlit_components/institutional_portfolios_workbench/src/style.css").read_text(
            encoding="utf-8"
        )

        self.assertIn('type ViewName = "overview" | "holdings" | "security" | "popularity";', component_source)
        self.assertIn('type WorkspaceSection = "portfolio" | "security";', component_source)
        self.assertIn("activeWorkspaceSection", component_source)
        self.assertIn("switchWorkspaceSection", component_source)
        self.assertIn('aria-label="작업 영역"', component_source)
        self.assertIn('"포트폴리오 세부 보기"', component_source)
        self.assertIn('"종목 분석 세부 보기"', component_source)
        self.assertIn("포트폴리오", component_source)
        self.assertIn("종목 분석", component_source)
        self.assertIn("종목 상세", component_source)
        self.assertIn('setActiveView("security")', component_source)
        self.assertIn('activeView === "security"', component_source)
        self.assertNotIn("보유 기관 조회", component_source)
        self.assertIn(".ip-view-navigation", style_source)
        self.assertIn(".ip-primary-tabs", style_source)
        self.assertIn(".ip-secondary-tabs", style_source)
        self.assertIn(".ip-primary-tabs__active", style_source)
        self.assertNotIn("ip-tab-group__label", component_source)
        self.assertNotIn(".ip-tab-group", style_source)

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
        self.assertIn("ip-chart-market-strip", component_source)
        self.assertIn("ip-volume-bars", component_source)
        self.assertIn("ip-chart-navigator", component_source)
        self.assertIn("panWindow", component_source)
        self.assertIn("캔들", component_source)
        self.assertIn("strokeDasharray", component_source)
        self.assertIn(".ip-chart-tooltip", style_source)
        self.assertIn(".ip-chart-market-strip", style_source)
        self.assertIn(".ip-volume-bars", style_source)
        self.assertIn(".ip-chart-navigator", style_source)
        self.assertIn(".ip-chart-style-toggle", style_source)
        self.assertIn("stroke-dasharray", style_source)
        self.assertNotIn('type="range"', component_source)

    def test_selected_security_chart_stretches_and_uses_date_axis_ticks(self) -> None:
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn("CHART_VIEWBOX_WIDTH", component_source)
        self.assertIn("const chartWidth = CHART_VIEWBOX_WIDTH", component_source)
        self.assertIn("viewBox={`0 0 ${CHART_VIEWBOX_WIDTH} ${height}`}", component_source)
        self.assertIn("pointSignature", component_source)
        self.assertIn("setWindowStart(0)", component_source)
        self.assertNotIn("ResizeObserver", component_source)
        self.assertNotIn("setChartWidth", component_source)
        self.assertIn("dateTicks", component_source)
        self.assertIn("ip-chart-date-tick", component_source)
        self.assertIn("tick.point.date", component_source)
        self.assertNotIn("activePoint ? priceLabel(activePoint.price) : \"\"", component_source)

    def test_selected_security_detail_uses_two_row_chart_and_scrollable_holder_layout(self) -> None:
        component_source = Path(
            "app/web/streamlit_components/institutional_portfolios_workbench/src/InstitutionalPortfoliosWorkbench.tsx"
        ).read_text(encoding="utf-8")
        style_source = Path("app/web/streamlit_components/institutional_portfolios_workbench/src/style.css").read_text(
            encoding="utf-8"
        )

        self.assertIn("ip-security-overview", component_source)
        self.assertIn("ip-security-context-card", component_source)
        self.assertIn("ip-security-chart-row", component_source)
        self.assertIn("ip-holder-panel--scroll", component_source)
        self.assertIn("ip-holder-scroll", component_source)
        self.assertIn("포트폴리오 내 종목 위치", component_source)
        self.assertIn("현재 선택한 기관 포트폴리오 기준", component_source)
        self.assertIn("표시 중", component_source)
        self.assertIn("holders.map", component_source)
        self.assertNotIn("holders.slice(0, 24)", component_source)
        self.assertIn(".ip-security-overview", style_source)
        self.assertIn(".ip-security-chart-row", style_source)
        self.assertIn(".ip-holder-panel--scroll", style_source)
        self.assertIn(".ip-holder-scroll", style_source)
        self.assertIn("overflow-y: auto", style_source)


if __name__ == "__main__":
    unittest.main()
