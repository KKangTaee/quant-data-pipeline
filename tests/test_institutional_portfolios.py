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
        self.assertEqual(payload["sector_exposure"]["bars"][0]["sector"], "Technology")
        self.assertTrue(payload["source_caveats"]["visible"])
        self.assertFalse(payload["boundary"]["trade_signal"])

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


class InstitutionalPortfoliosNavigationTests(unittest.TestCase):
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
        self.assertIn("collect_sec_13f_dataset", active_ingestion_actions())
        self.assertIn("collect_sec_13f_dataset", PROGRESS_ENABLED_ACTIONS)
        self.assertIn("SEC Form 13F", JOB_GUIDE["collect_sec_13f_dataset"]["title"])

    def test_institutional_portfolios_page_mounts_react_workbench_before_detail_tables(self) -> None:
        source = Path("app/web/institutional_portfolios.py").read_text(encoding="utf-8")

        self.assertIn("render_institutional_portfolios_workbench", source)
        self.assertIn("build_institutional_workbench_payload", source)
        self.assertLess(source.index("render_institutional_portfolios_workbench"), source.index("st.dataframe"))


if __name__ == "__main__":
    unittest.main()
