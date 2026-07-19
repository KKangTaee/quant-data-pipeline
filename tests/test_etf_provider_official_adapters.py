from __future__ import annotations

import unittest
from unittest.mock import patch


def _ishares_workbook_bytes() -> bytes:
    return b'''<?xml version="1.0"?>
<ss:Workbook xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <ss:Worksheet ss:Name="Disclaimers"><ss:Table>
    <ss:Row><ss:Cell ss:HRef="https://example.com/?type=etf&view=all"><ss:Data ss:Type="String">Terms</ss:Data></ss:Cell></ss:Row>
  </ss:Table></ss:Worksheet>
  <ss:Worksheet ss:Name="Holdings"><ss:Table>
    <ss:Row><ss:Cell><ss:Data ss:Type="String">Fund Holdings as of</ss:Data></ss:Cell><ss:Cell><ss:Data ss:Type="String">Jul 15, 2026</ss:Data></ss:Cell></ss:Row>
    <ss:Row>
      <ss:Cell><ss:Data ss:Type="String">Ticker</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Name</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Sector</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Asset Class</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Market Value</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Weight (%)</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Quantity</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Location</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Currency</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">CUSIP</ss:Data></ss:Cell>
    </ss:Row>
    <ss:Row>
      <ss:Cell><ss:Data ss:Type="String">AAA</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Example Holding</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Industrials</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Equity</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">1250</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">12.5</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">100</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">United States</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">USD</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">123456789</ss:Data></ss:Cell>
    </ss:Row>
  </ss:Table></ss:Worksheet>
</ss:Workbook>'''


def _vanguard_payload() -> dict[str, object]:
    return {
        "size": 1,
        "asOfDate": "2026-06-30T00:00:00-04:00",
        "fund": {
            "entity": [
                {
                    "longName": "Welltower Inc.",
                    "ticker": "WELL",
                    "cusip": "95040Q104",
                    "isin": "US95040Q1040",
                    "percentWeight": "7.68",
                    "sharesHeld": "26143850",
                    "marketValue": 5368116721.0,
                    "secMainType": "Equity",
                }
            ]
        },
    }


def _ishares_duplicate_bond_workbook_bytes() -> bytes:
    return b'''<ss:Workbook xmlns:ss="urn:schemas-microsoft-com:office:spreadsheet">
  <ss:Worksheet ss:Name="Holdings"><ss:Table>
    <ss:Row><ss:Cell><ss:Data ss:Type="String">Fund Holdings as of</ss:Data></ss:Cell><ss:Cell><ss:Data ss:Type="String">Jul 15, 2026</ss:Data></ss:Cell></ss:Row>
    <ss:Row>
      <ss:Cell><ss:Data ss:Type="String">Name</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Asset Class</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Market Value</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Weight (%)</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Par Value</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Maturity</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Coupon (%)</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Effective Date</ss:Data></ss:Cell>
    </ss:Row>
    <ss:Row>
      <ss:Cell><ss:Data ss:Type="String">HSBC HOLDINGS PLC</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Fixed Income</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">13293137.89</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">0.0379</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">12141000</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Sep 15, 2037</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">6.5</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Sep 12, 2007</ss:Data></ss:Cell>
    </ss:Row>
    <ss:Row>
      <ss:Cell><ss:Data ss:Type="String">HSBC HOLDINGS PLC</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Fixed Income</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">10723636.54</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">0.03057</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">9957000</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Sep 15, 2037</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="Number">6.5</ss:Data></ss:Cell>
      <ss:Cell><ss:Data ss:Type="String">Sep 16, 2022</ss:Data></ss:Cell>
    </ss:Row>
  </ss:Table></ss:Worksheet>
</ss:Workbook>'''


class EtfProviderOfficialAdapterTests(unittest.TestCase):
    def test_ishares_discovery_uses_current_workbook_contract(self) -> None:
        from finance.data import etf_provider

        product_html = (
            '<td class="links"><a href="/us/products/239623/ishares-msci-eafe-etf">'
            "EFA</a></td>"
        )
        with patch.object(etf_provider, "_fetch_official_html", return_value=product_html):
            product = etf_provider._fetch_ishares_product_index()["EFA"]

        self.assertIn("get-fund-document", product["holdings_url"])
        self.assertIn("portfolioId=239623", product["holdings_url"])

        rows = etf_provider._candidate_source_rows_for_universe_row(
            {
                "symbol": "EFA",
                "fund_family": "iShares",
                "long_name": "iShares MSCI EAFE ETF",
            },
            ishares_index={"EFA": product},
        )
        holdings = next(row for row in rows if row["data_kind"] == "holdings")
        self.assertEqual(holdings["parser"], "ishares_workbook")
        self.assertEqual(holdings["source_url"], product["holdings_url"])

    def test_ishares_workbook_parser_normalizes_holdings(self) -> None:
        from finance.data import etf_provider

        rows = etf_provider._parse_ishares_holdings_workbook(
            "EFA",
            {
                "source": "ishares",
                "url": "https://official.example/efa.xls",
            },
            _ishares_workbook_bytes(),
            as_of_fallback=None,
            collected_at="2026-07-17 00:00:00",
        )

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["as_of_date"], "2026-07-15")
        self.assertEqual(rows[0]["holding_symbol"], "AAA")
        self.assertEqual(rows[0]["holding_name"], "Example Holding")
        self.assertEqual(rows[0]["weight_pct"], 12.5)
        self.assertEqual(rows[0]["coverage_status"], "partial")

    def test_ishares_bonds_with_same_name_maturity_and_coupon_keep_unique_ids(self) -> None:
        from finance.data import etf_provider

        rows = etf_provider._parse_ishares_holdings_workbook(
            "LQD",
            {
                "source": "ishares",
                "url": "https://official.example/lqd.xls",
            },
            _ishares_duplicate_bond_workbook_bytes(),
            as_of_fallback=None,
            collected_at="2026-07-17 00:00:00",
        )

        self.assertEqual(len(rows), 2)
        self.assertEqual(len({row["holding_id"] for row in rows}), 2)

    def test_vanguard_discovery_and_json_parser_normalize_vnq(self) -> None:
        from finance.data import etf_provider

        rows = etf_provider._candidate_source_rows_for_universe_row(
            {
                "symbol": "VNQ",
                "fund_family": "Vanguard",
                "long_name": "Vanguard Real Estate ETF",
            }
        )
        holdings = next(row for row in rows if row["data_kind"] == "holdings")
        self.assertEqual(holdings["provider"], "vanguard")
        self.assertEqual(holdings["parser"], "vanguard_json")
        self.assertIn("/vmf/api/VNQ/portfolio-holding/stock.json", holdings["source_url"])

        parsed = etf_provider._parse_vanguard_holdings_json(
            "VNQ",
            {
                "source": "vanguard",
                "url": holdings["source_url"],
                "asset_class": "Equity",
            },
            _vanguard_payload(),
            as_of_fallback=None,
            collected_at="2026-07-17 00:00:00",
        )
        self.assertEqual(len(parsed), 1)
        self.assertEqual(parsed[0]["as_of_date"], "2026-06-30")
        self.assertEqual(parsed[0]["holding_symbol"], "WELL")
        self.assertEqual(parsed[0]["holding_id"], "95040Q104")
        self.assertEqual(parsed[0]["weight_pct"], 7.68)

    def test_verification_and_dispatch_support_both_new_adapters(self) -> None:
        from app.services.backtest_practical_validation import (
            SUPPORTED_HOLDINGS_COLLECTOR_PARSERS,
        )
        from finance.data import etf_provider

        self.assertIn("ishares_workbook", SUPPORTED_HOLDINGS_COLLECTOR_PARSERS)
        self.assertIn("vanguard_json", SUPPORTED_HOLDINGS_COLLECTOR_PARSERS)

        source_map = {
            "EFA": {
                "source": "ishares",
                "parser": "ishares_workbook",
                "url": "https://official.example/efa.xls",
            },
            "VNQ": {
                "source": "vanguard",
                "parser": "vanguard_json",
                "url": "https://official.example/vnq.json",
                "asset_class": "Equity",
            },
        }
        with (
            patch.object(etf_provider, "_source_map_info_by_symbol", return_value=source_map),
            patch.object(etf_provider, "_fetch_official_bytes", return_value=_ishares_workbook_bytes()),
            patch.object(etf_provider, "_fetch_official_json", return_value=_vanguard_payload()),
        ):
            rows, missing, failed = etf_provider._build_official_holdings_rows(
                ["EFA", "VNQ"],
                as_of_date=None,
            )

        self.assertEqual({row["fund_symbol"] for row in rows}, {"EFA", "VNQ"})
        self.assertEqual(missing, [])
        self.assertEqual(failed, [])

        for source_row in (
            {
                "parser": "ishares_workbook",
                "source_url": "https://official.example/efa.xls",
            },
            {
                "parser": "vanguard_json",
                "source_url": "https://official.example/vnq.json",
            },
        ):
            with (
                patch.object(etf_provider, "_fetch_official_bytes", return_value=_ishares_workbook_bytes()),
                patch.object(etf_provider, "_fetch_official_json", return_value=_vanguard_payload()),
            ):
                verified = etf_provider._verify_provider_source(source_row)
            self.assertEqual(verified["source_status"], "verified")


if __name__ == "__main__":
    unittest.main()
