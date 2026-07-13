from __future__ import annotations

import math
import json
import re
import statistics
import time
import xml.etree.ElementTree as ET
from collections.abc import Iterable, Mapping
from datetime import datetime, timezone
from io import StringIO
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, VALUATION_SCHEMAS, sync_table_schema


QQQ_CIK = "0001067839"
SEC_ARCHIVES_BASE_URL = "https://www.sec.gov/Archives/edgar/data"
SUPPORTED_HOLDINGS_FORMS = {"NPORT-P", "NPORT-P/A", "N-30B-2"}
MINIMUM_COVERAGE_PCT = 95.0
CALIBRATION_MEDIAN_LIMIT_PCT = 5.0
CALIBRATION_MAX_LIMIT_PCT = 10.0
SEC_USER_AGENT = "quant-data-pipeline/1.0 contact: local-research@example.com"
DB_META = "finance_meta"
NON_EQUITY_ASSET_CLASSES = {
    "cash",
    "currency",
    "future",
    "index future",
    "synthetic cash",
}
DILUTED_EPS_CONCEPT_SUFFIXES = (
    "EarningsPerShareDiluted",
    "EarningsPerShareBasicAndDiluted",
    "DilutedEarningsLossPerShare",
)


def _open_meta_db(
    db_factory: Any,
    *,
    host: str,
    user: str,
    password: str,
    port: int,
) -> MySQLClient:
    db = db_factory(host, user, password, port)
    db.use_db(DB_META)
    return db


def ensure_nasdaq100_valuation_schemas(
    *,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    """Create or extend the QQQ holdings and Nasdaq-100 valuation tables."""
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        for table_name, schema in (
            ("etf_holdings_snapshot", PROVIDER_SCHEMAS["etf_holdings_snapshot"]),
            ("nasdaq100_monthly_valuation", VALUATION_SCHEMAS["nasdaq100_monthly_valuation"]),
        ):
            db.execute(schema)
            sync_table_schema(db, table_name, schema, DB_META)
    finally:
        db.close()


def store_qqq_holdings_rows(
    rows: list[dict[str, Any]],
    *,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    """Idempotently persist official QQQ holdings without deleting other providers."""
    if not rows:
        return 0
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        db.executemany(
            """
            INSERT INTO etf_holdings_snapshot (
              fund_symbol, as_of_date, source, source_type, source_ref,
              holding_id, holding_symbol, holding_name, holding_type,
              cusip, isin, lei, issuer_cik, filing_date, accession_no,
              holding_snapshot_quality, weight_pct, shares, market_value,
              sector, asset_class, country, currency, coverage_status,
              missing_fields_json, collected_at, error_msg
            ) VALUES (
              %(fund_symbol)s, %(as_of_date)s, %(source)s, %(source_type)s, %(source_ref)s,
              %(holding_id)s, %(holding_symbol)s, %(holding_name)s, %(holding_type)s,
              %(cusip)s, %(isin)s, %(lei)s, %(issuer_cik)s, %(filing_date)s, %(accession_no)s,
              %(holding_snapshot_quality)s, %(weight_pct)s, %(shares)s, %(market_value)s,
              %(sector)s, %(asset_class)s, %(country)s, %(currency)s, %(coverage_status)s,
              %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
            )
            ON DUPLICATE KEY UPDATE
              holding_symbol = VALUES(holding_symbol), holding_name = VALUES(holding_name),
              holding_type = VALUES(holding_type), cusip = VALUES(cusip), isin = VALUES(isin),
              lei = VALUES(lei), issuer_cik = VALUES(issuer_cik), filing_date = VALUES(filing_date),
              accession_no = VALUES(accession_no),
              holding_snapshot_quality = VALUES(holding_snapshot_quality),
              weight_pct = VALUES(weight_pct), shares = VALUES(shares),
              market_value = VALUES(market_value), sector = VALUES(sector),
              asset_class = VALUES(asset_class), country = VALUES(country),
              currency = VALUES(currency), coverage_status = VALUES(coverage_status),
              missing_fields_json = VALUES(missing_fields_json),
              collected_at = VALUES(collected_at), error_msg = VALUES(error_msg),
              source_ref = VALUES(source_ref)
            """,
            rows,
        )
    finally:
        db.close()
    return len(rows)


def store_nasdaq100_monthly_rows(
    rows: list[dict[str, Any]],
    *,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    """Idempotently preserve both ready and coverage-blocked monthly evidence."""
    if not rows:
        return 0
    db = _open_meta_db(
        db_factory, host=host, user=user, password=password, port=port
    )
    try:
        db.executemany(
            """
            INSERT INTO nasdaq100_monthly_valuation (
              observation_month, proxy_symbol, qqq_price, reconstructed_ttm_eps,
              trailing_pe, earnings_yield, coverage_weight_pct, unmapped_weight_pct,
              holding_snapshot_date, holding_snapshot_quality,
              earnings_available_through, price_basis_date, data_quality,
              source, source_ref, collected_at, error_msg
            ) VALUES (
              %(observation_month)s, %(proxy_symbol)s, %(qqq_price)s,
              %(reconstructed_ttm_eps)s, %(trailing_pe)s, %(earnings_yield)s,
              %(coverage_weight_pct)s, %(unmapped_weight_pct)s,
              %(holding_snapshot_date)s, %(holding_snapshot_quality)s,
              %(earnings_available_through)s, %(price_basis_date)s, %(data_quality)s,
              %(source)s, %(source_ref)s, %(collected_at)s, %(error_msg)s
            )
            ON DUPLICATE KEY UPDATE
              qqq_price = VALUES(qqq_price),
              reconstructed_ttm_eps = VALUES(reconstructed_ttm_eps),
              trailing_pe = VALUES(trailing_pe), earnings_yield = VALUES(earnings_yield),
              coverage_weight_pct = VALUES(coverage_weight_pct),
              unmapped_weight_pct = VALUES(unmapped_weight_pct),
              holding_snapshot_date = VALUES(holding_snapshot_date),
              holding_snapshot_quality = VALUES(holding_snapshot_quality),
              earnings_available_through = VALUES(earnings_available_through),
              price_basis_date = VALUES(price_basis_date), data_quality = VALUES(data_quality),
              source_ref = VALUES(source_ref), collected_at = VALUES(collected_at),
              error_msg = VALUES(error_msg)
            """,
            rows,
        )
    finally:
        db.close()
    return len(rows)


def fetch_sec_text(
    url: str,
    *,
    timeout: int = 20,
    attempts: int = 3,
    opener: Any = urlopen,
    sleep_fn: Any = time.sleep,
) -> str:
    """Fetch an official SEC document with bounded retry and an identifying User-Agent."""
    last_error: Exception | None = None
    for attempt in range(max(1, int(attempts))):
        try:
            request = Request(
                str(url),
                headers={"User-Agent": SEC_USER_AGENT},
            )
            with opener(request, timeout=int(timeout)) as response:
                return response.read().decode("utf-8", errors="replace")
        except Exception as exc:  # provider boundary; raised after bounded attempts
            last_error = exc
            if attempt + 1 < max(1, int(attempts)):
                sleep_fn(0.25 * (attempt + 1))
    raise RuntimeError(f"SEC fetch failed after {max(1, int(attempts))} attempts: {url}: {last_error}")


def _clean_text(value: Any) -> str | None:
    if value is None or (isinstance(value, float) and math.isnan(value)):
        return None
    text = re.sub(r"\s+", " ", str(value).replace("\xa0", " ")).strip()
    if not text or text.lower() in {"nan", "none", "n/a", "-", "--"}:
        return None
    return text


def _optional_float(value: Any) -> float | None:
    text = _clean_text(value)
    if text is None:
        return None
    normalized = re.sub(r"[$,%\s,()]", "", text)
    if text.strip().startswith("(") and text.strip().endswith(")"):
        normalized = f"-{normalized}"
    try:
        parsed = float(normalized)
    except ValueError:
        return None
    return parsed if math.isfinite(parsed) else None


def _normalize_name(value: Any) -> str:
    text = (_clean_text(value) or "").lower()
    text = re.sub(r"\([a-z0-9*]+\)", " ", text)
    text = text.replace("&", " and ")
    text = re.sub(r"\bcorporation\b", "corp", text)
    text = re.sub(r"\bincorporated\b", "inc", text)
    text = re.sub(r"\bclass\s+[a-z0-9]+\b", " ", text)
    text = re.sub(r"\b(adr|ordinary shares?|common stock|new york registry shares?)\b", " ", text)
    text = re.sub(r"\b(plc|ltd|limited|corp|inc|co|company|nv|sa|ag)\b", " ", text)
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


def _normalize_override_key(value: Any) -> str:
    text = (_clean_text(value) or "").lower()
    text = re.sub(r"\([a-z0-9*]+\)$", " ", text)
    text = text.replace("&", " and ")
    return re.sub(r"[^a-z0-9]+", " ", text).strip()


# Reviewed historical QQQ identities. These are explicit ticker/name bridges, not fuzzy matches.
QQQ_REVIEWED_IDENTITY_OVERRIDES: dict[str, dict[str, str]] = {
    "facebook inc class a": {"symbol": "META", "issuer_cik": "0001326801"},
    "google inc class a": {"symbol": "GOOGL", "issuer_cik": "0001652044"},
    "google inc class c": {"symbol": "GOOG", "issuer_cik": "0001652044"},
    "priceline group inc": {"symbol": "BKNG", "issuer_cik": "0001075531"},
    "adobe systems inc": {"symbol": "ADBE", "issuer_cik": "0000796343"},
    "tesla motors inc": {"symbol": "TSLA", "issuer_cik": "0001318605"},
    "walgreens boots alliance inc": {"symbol": "WBA", "issuer_cik": "0001618921"},
    "activision blizzard inc": {"symbol": "ATVI", "issuer_cik": "0000718877"},
    "ansys inc": {"symbol": "ANSS", "issuer_cik": "0001013462"},
    "zoom video communications inc": {"symbol": "ZM", "issuer_cik": "0001585521"},
    "celgene corp": {"symbol": "CELG", "issuer_cik": "0000816284"},
    "sirius xm holdings inc": {"symbol": "SIRI", "issuer_cik": "0000908937"},
    "xilinx inc": {"symbol": "XLNX", "issuer_cik": "0000743988"},
    "alexion pharmaceuticals inc": {"symbol": "ALXN", "issuer_cik": "0000899866"},
    "cerner corp": {"symbol": "CERN", "issuer_cik": "0000804753"},
    "the trade desk inc": {"symbol": "TTD", "issuer_cik": "0001671933"},
    "trade desk inc the": {"symbol": "TTD", "issuer_cik": "0001671933"},
    "splunk inc": {"symbol": "SPLK", "issuer_cik": "0001353283"},
    "twenty first century fox inc class a": {"symbol": "FOXA", "issuer_cik": "0001308161"},
    "twenty first century fox inc class b": {"symbol": "FOX", "issuer_cik": "0001308161"},
    "maxim integrated products inc": {"symbol": "MXIM", "issuer_cik": "0000743316"},
    "express scripts holding co": {"symbol": "ESRX", "issuer_cik": "0001532063"},
    "seagen inc": {"symbol": "SGEN", "issuer_cik": "0001060736"},
    "citrix systems inc": {"symbol": "CTXS", "issuer_cik": "0000877890"},
    "symantec corp": {"symbol": "SYMC", "issuer_cik": "0000849399"},
    "fiserv inc": {"symbol": "FI", "issuer_cik": "0000798354"},
    "moderna inc": {"symbol": "MRNA", "issuer_cik": "0001682852"},
    "illumina inc": {"symbol": "ILMN", "issuer_cik": "0001110803"},
    "dollar tree inc": {"symbol": "DLTR", "issuer_cik": "0000935703"},
    "ebay inc": {"symbol": "EBAY", "issuer_cik": "0001065088"},
    "verisign inc": {"symbol": "VRSN", "issuer_cik": "0001014473"},
    "cdw corp": {"symbol": "CDW", "issuer_cik": "0001402057"},
    "skyworks solutions inc": {"symbol": "SWKS", "issuer_cik": "0000004127"},
    "biogen inc": {"symbol": "BIIB", "issuer_cik": "0000875045"},
    "atlassian corp": {"symbol": "TEAM", "issuer_cik": "0001650372"},
    "globalfoundries inc": {"symbol": "GFS", "issuer_cik": "0001709048"},
    "docusign inc": {"symbol": "DOCU", "issuer_cik": "0001261333"},
    "jd com inc": {"symbol": "JD", "issuer_cik": "0001549802"},
    "jd com inc adr": {"symbol": "JD", "issuer_cik": "0001549802"},
    "baidu inc": {"symbol": "BIDU", "issuer_cik": "0001329099"},
    "baidu inc adr": {"symbol": "BIDU", "issuer_cik": "0001329099"},
    "netease inc": {"symbol": "NTES", "issuer_cik": "0001110646"},
    "netease inc adr": {"symbol": "NTES", "issuer_cik": "0001110646"},
    "trip com group ltd": {"symbol": "TCOM", "issuer_cik": "0001269238"},
    "ctrip com international ltd adr": {"symbol": "TCOM", "issuer_cik": "0001269238"},
    "yahoo inc": {"symbol": "YHOO", "issuer_cik": "0001011006"},
    "avago technologies ltd": {"symbol": "AVGO", "issuer_cik": "0001730168"},
    "liberty global plc series c": {"symbol": "LBTYK", "issuer_cik": "0001570585"},
    "liberty global plc class c": {"symbol": "LBTYK", "issuer_cik": "0001570585"},
    "liberty global plc series a": {"symbol": "LBTYA", "issuer_cik": "0001570585"},
    "mylan nv": {"symbol": "MYL", "issuer_cik": "0001623613"},
    "altera corp": {"symbol": "ALTR", "issuer_cik": "0000768251"},
    "viacom inc class b": {"symbol": "VIAB", "issuer_cik": "0001339947"},
    "seagate technology plc": {"symbol": "STX", "issuer_cik": "0001137789"},
    "dish network corp class a": {"symbol": "DISH", "issuer_cik": "0001001082"},
    "vodafone group plc adr": {"symbol": "VOD", "issuer_cik": "0000839923"},
    "ca inc": {"symbol": "CA", "issuer_cik": "0000356028"},
    "stericycle inc": {"symbol": "SRCL", "issuer_cik": "0000861878"},
    "whole foods market inc": {"symbol": "WFM", "issuer_cik": "0000865436"},
    "liberty interactive corp qvc group class a": {"symbol": "QVCA", "issuer_cik": "0001355096"},
    "expedia inc": {"symbol": "EXPE", "issuer_cik": "0001324424"},
    "ulta salon cosmetics and fragrance inc": {"symbol": "ULTA", "issuer_cik": "0001403568"},
    "linear technology corp": {"symbol": "LLTC", "issuer_cik": "0000791907"},
    "kla tencor corp": {"symbol": "KLAC", "issuer_cik": "0000319201"},
    "norwegian cruise line holdings ltd": {"symbol": "NCLH", "issuer_cik": "0001513761"},
    "jb hunt transport services inc": {"symbol": "JBHT", "issuer_cik": "0000728535"},
    "shire plc adr": {"symbol": "SHPG", "issuer_cik": "0000936402"},
    "hologic inc": {"symbol": "HOLX", "issuer_cik": "0000859737"},
    "qurate retail inc": {"symbol": "QRTEA", "issuer_cik": "0001355096"},
    "marvell technology group ltd": {"symbol": "MRVL", "issuer_cik": "0001835632"},
}


def _filing_columns(payload: Mapping[str, Any]) -> dict[str, list[Any]]:
    recent = dict((payload.get("filings") or {}).get("recent") or {})
    return {str(key): list(value or []) for key, value in recent.items()}


def discover_qqq_sec_filings(payload: dict[str, Any]) -> list[dict[str, Any]]:
    """Normalize official QQQ N-PORT/N-30B-2 filing metadata and archive URLs."""
    columns = _filing_columns(payload)
    forms = columns.get("form", [])
    cik = str(payload.get("cik") or QQQ_CIK).lstrip("0") or "0"
    rows: list[dict[str, Any]] = []
    for index, form_value in enumerate(forms):
        form = str(form_value or "").upper()
        if form not in SUPPORTED_HOLDINGS_FORMS:
            continue
        accession = str(columns.get("accessionNumber", [])[index])
        accession_digits = accession.replace("-", "")
        primary_document = str(columns.get("primaryDocument", [])[index])
        primary_basename = primary_document.rsplit("/", 1)[-1]
        report_date = str(columns.get("reportDate", [])[index])
        filing_date = str(columns.get("filingDate", [])[index])
        rows.append(
            {
                "accession_no": accession,
                "filing_date": filing_date,
                "report_date": report_date,
                "form": form,
                "primary_document": primary_basename,
                "source_url": (
                    f"{SEC_ARCHIVES_BASE_URL}/{cik}/{accession_digits}/{primary_basename}"
                ),
                "holding_snapshot_quality": (
                    "quarterly_anchor" if form.startswith("NPORT") else "annual_anchor"
                ),
            }
        )
    return sorted(rows, key=lambda row: (row["report_date"], row["filing_date"], row["accession_no"]))


def _holding_base(filing: Mapping[str, Any]) -> dict[str, Any]:
    return {
        "fund_symbol": "QQQ",
        "as_of_date": filing.get("report_date"),
        "source": "sec_qqq_nport" if str(filing.get("form") or "").startswith("NPORT") else "sec_qqq_n30b2",
        "source_type": "official",
        "source_ref": filing.get("source_url"),
        "filing_date": filing.get("filing_date"),
        "accession_no": filing.get("accession_no"),
        "holding_snapshot_quality": filing.get("holding_snapshot_quality"),
        "holding_symbol": None,
        "issuer_cik": None,
        "identity_method": "unresolved",
        "coverage_status": "actual",
        "error_msg": None,
    }


def parse_qqq_nport_xml(
    xml_text: str,
    *,
    filing: dict[str, Any],
) -> list[dict[str, Any]]:
    """Parse equity-like QQQ N-PORT investment rows without depending on prefixes."""
    root = ET.fromstring(xml_text)
    rows: list[dict[str, Any]] = []
    for investment in root.findall(".//{*}invstOrSec"):
        def text(tag: str) -> str | None:
            node = investment.find(f"{{*}}{tag}")
            return _clean_text(node.text if node is not None else None)

        asset_category = text("assetCat")
        units = text("units")
        if asset_category not in {None, "EC"} or units not in {None, "NS"}:
            continue
        name = text("name") or text("title")
        cusip = text("cusip")
        if name is None:
            continue
        isin_node = investment.find(".//{*}isin")
        isin = _clean_text(isin_node.attrib.get("value") if isin_node is not None else None)
        row = _holding_base({**filing, "form": filing.get("form") or "NPORT-P"})
        row.update(
            {
                "holding_id": cusip or isin or _normalize_name(name).upper(),
                "holding_name": name,
                "holding_type": "Equity",
                "cusip": cusip,
                "isin": isin,
                "lei": text("lei"),
                "weight_pct": _optional_float(text("pctVal")),
                "shares": _optional_float(text("balance")),
                "market_value": _optional_float(text("valUSD")),
                "asset_class": "Equity",
                "country": text("invCountry"),
                "currency": text("curCd"),
            }
        )
        rows.append(row)
    return rows


def _annual_name_candidate(values: list[Any]) -> str | None:
    excluded = (
        "number of shares",
        "common stocks",
        "equity interests",
        "total common",
        "schedule of investments",
        "value",
    )
    candidates: list[str] = []
    for value in values:
        text = _clean_text(value)
        if text is None or _optional_float(text) is not None or text == "$":
            continue
        lowered = text.lower()
        if any(term in lowered for term in excluded) or re.search(r"—\s*\d+(?:\.\d+)?%", text):
            continue
        candidates.append(text)
    if not candidates:
        return None
    return max(candidates, key=len)


def parse_qqq_n30b2_html(
    html_text: str,
    *,
    filing: dict[str, Any],
) -> list[dict[str, Any]]:
    """Parse annual schedule rows and derive weights from reported market values."""
    parsed: list[dict[str, Any]] = []
    for table in pd.read_html(StringIO(html_text)):
        table_text = " ".join(
            text for text in (_clean_text(value) for value in table.to_numpy().ravel()) if text
        ).lower()
        if not all(token in table_text for token in ("shares", "value", "common stock")):
            continue
        for raw in table.itertuples(index=False, name=None):
            values = list(raw)
            numeric = [value for value in (_optional_float(item) for item in values) if value is not None and value > 0]
            if len(numeric) < 2:
                continue
            name = _annual_name_candidate(values)
            if name is None:
                continue
            shares, market_value = numeric[0], numeric[-1]
            row = _holding_base({**filing, "form": "N-30B-2"})
            row.update(
                {
                    "holding_id": _normalize_name(name).upper(),
                    "holding_name": re.sub(r"\([a-z0-9*]+\)$", "", name).strip(),
                    "holding_type": "Equity",
                    "cusip": None,
                    "isin": None,
                    "lei": None,
                    "weight_pct": None,
                    "shares": shares,
                    "market_value": market_value,
                    "asset_class": "Equity",
                    "country": None,
                    "currency": "USD",
                }
            )
            parsed.append(row)
    total_value = sum(float(row["market_value"]) for row in parsed)
    if total_value <= 0:
        return []
    for row in parsed:
        row["weight_pct"] = (float(row["market_value"]) / total_value) * 100.0
    return parsed


def parse_sec_companyfacts_diluted_eps(
    payload: Mapping[str, Any],
    *,
    symbol: str,
) -> list[dict[str, Any]]:
    """Normalize explicit USD/share discrete-quarter and FY diluted EPS facts."""
    concept_paths = (
        ("us-gaap", "EarningsPerShareDiluted"),
        # Some issuers report a single value because basic and diluted EPS are equal.
        ("us-gaap", "EarningsPerShareBasicAndDiluted"),
        ("ifrs-full", "DilutedEarningsLossPerShare"),
    )
    rows: list[dict[str, Any]] = []
    facts = dict(payload.get("facts") or {})
    for taxonomy, concept_name in concept_paths:
        concept = dict((facts.get(taxonomy) or {}).get(concept_name) or {})
        for raw_unit, observations in dict(concept.get("units") or {}).items():
            if str(raw_unit).lower() not in {"usd/shares", "usd/share", "usd per share"}:
                continue
            for observation in observations or []:
                start = pd.to_datetime(observation.get("start"), errors="coerce")
                end = pd.to_datetime(observation.get("end"), errors="coerce")
                filed = pd.to_datetime(observation.get("filed"), errors="coerce")
                value = _optional_float(observation.get("val"))
                fiscal_period = str(observation.get("fp") or "").upper()
                form = str(observation.get("form") or "").upper()
                if pd.isna(start) or pd.isna(end) or pd.isna(filed) or value is None:
                    continue
                duration_days = int((end - start).days) + 1
                if fiscal_period in {"Q1", "Q2", "Q3"} and form in {"10-Q", "10-Q/A"}:
                    if not 70 <= duration_days <= 120:
                        continue
                    period_type = "Q"
                    fiscal_quarter = int(fiscal_period[-1])
                elif fiscal_period == "FY" and form in {"10-K", "10-K/A", "20-F", "20-F/A"}:
                    if not 250 <= duration_days <= 390:
                        continue
                    period_type = "FY"
                    fiscal_quarter = None
                else:
                    continue
                rows.append(
                    {
                        "symbol": str(symbol),
                        "concept": f"{taxonomy}:{concept_name}",
                        "unit": "USD per share",
                        "source_period_type": "duration",
                        "period_type": period_type,
                        "fiscal_year": observation.get("fy"),
                        "fiscal_quarter": fiscal_quarter,
                        "period_start": pd.Timestamp(start).strftime("%Y-%m-%d"),
                        "period_end": pd.Timestamp(end).strftime("%Y-%m-%d"),
                        "value": value,
                        "available_at": pd.Timestamp(filed).strftime("%Y-%m-%d"),
                        "form_type": form,
                        "accession_no": observation.get("accn"),
                        "source": "sec_companyfacts",
                    }
                )
    keyed: dict[tuple[Any, ...], dict[str, Any]] = {}
    for row in rows:
        key = (
            row["symbol"],
            row["concept"],
            row["period_start"],
            row["period_end"],
            row["fiscal_year"],
            row["fiscal_quarter"],
            row["accession_no"],
        )
        keyed[key] = row
    return sorted(
        keyed.values(),
        key=lambda row: (row["symbol"], row["period_end"], row["available_at"], str(row["accession_no"])),
    )


def resolve_holding_identities(
    holdings: Iterable[dict[str, Any]],
    identity_rows: Iterable[dict[str, Any]],
    *,
    overrides: Mapping[str, Mapping[str, Any]] | None = None,
) -> list[dict[str, Any]]:
    """Resolve only deterministic CUSIP/name/reviewed mappings; fuzzy matches stay missing."""
    by_cusip: dict[str, dict[str, Any]] = {}
    by_name: dict[str, dict[str, Any]] = {}
    for raw in identity_rows:
        row = dict(raw)
        cusip = (_clean_text(row.get("cusip") or row.get("holding_id")) or "").upper()
        name = _normalize_name(row.get("name") or row.get("holding_name"))
        if cusip:
            by_cusip[cusip] = row
        if name:
            by_name[name] = row
    reviewed_source = QQQ_REVIEWED_IDENTITY_OVERRIDES if overrides is None else overrides
    reviewed = {_normalize_override_key(key): dict(value) for key, value in reviewed_source.items()}

    resolved: list[dict[str, Any]] = []
    for raw in holdings:
        row = dict(raw)
        cusip = (_clean_text(row.get("cusip")) or "").upper()
        name = _normalize_name(row.get("holding_name"))
        override_key = _normalize_override_key(row.get("holding_name"))
        match: dict[str, Any] | None = None
        method = "unresolved"
        if cusip and cusip in by_cusip:
            match, method = by_cusip[cusip], "cusip_exact"
        elif name and name in by_name:
            match, method = by_name[name], "name_exact"
        elif override_key and override_key in reviewed:
            match, method = reviewed[override_key], "reviewed_override"
        if match:
            row["holding_symbol"] = match.get("symbol") or match.get("holding_symbol")
            row["issuer_cik"] = match.get("issuer_cik") or match.get("cik")
            if not row.get("issuer_cik") and name in by_name:
                row["issuer_cik"] = by_name[name].get("issuer_cik") or by_name[name].get("cik")
        row["identity_method"] = method
        resolved.append(row)
    return resolved


def _eligible_statement_rows(
    statement_rows: Iterable[dict[str, Any]],
    *,
    as_of_date: str,
) -> pd.DataFrame:
    frame = pd.DataFrame(list(statement_rows))
    if frame.empty:
        return frame
    required = {"symbol", "period_end", "period_type", "value", "available_at"}
    if not required.issubset(frame.columns):
        return pd.DataFrame()
    for column in ("period_end", "available_at"):
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    frame["value"] = pd.to_numeric(frame["value"], errors="coerce")
    cutoff = pd.Timestamp(as_of_date) + pd.Timedelta(days=1)
    concept = frame.get("concept", pd.Series("", index=frame.index)).astype(str)
    unit = frame.get("unit", pd.Series("", index=frame.index)).astype(str).str.lower()
    source_period_type = frame.get("source_period_type", pd.Series("duration", index=frame.index)).astype(str).str.lower()
    eligible = frame.loc[
        concept.str.endswith(DILUTED_EPS_CONCEPT_SUFFIXES)
        & unit.isin({"usd per share", "usd/shares", "usd/share"})
        & source_period_type.eq("duration")
        & frame["period_type"].astype(str).str.upper().isin({"Q", "FY"})
        & frame["available_at"].notna()
        & (frame["available_at"] < cutoff)
        & frame["period_end"].notna()
        & frame["value"].notna()
    ].copy()
    eligible["eps_concept_priority"] = concept.loc[eligible.index].map(
        lambda value: 1 if value.endswith("EarningsPerShareBasicAndDiluted") else 2
    )
    return eligible


def derive_filing_aware_ttm_eps(
    statement_rows: Iterable[dict[str, Any]],
    *,
    as_of_date: str,
) -> dict[str, dict[str, Any]]:
    """Build four discrete diluted-EPS quarters using only facts available by month-end."""
    frame = _eligible_statement_rows(statement_rows, as_of_date=as_of_date)
    if frame.empty:
        return {}
    frame["fiscal_year"] = pd.to_numeric(frame.get("fiscal_year"), errors="coerce")
    frame["fiscal_quarter"] = pd.to_numeric(frame.get("fiscal_quarter"), errors="coerce")
    frame = frame.sort_values(
        ["symbol", "period_end", "available_at", "eps_concept_priority"]
    )
    results: dict[str, dict[str, Any]] = {}
    for symbol, symbol_rows in frame.groupby("symbol"):
        discrete: list[dict[str, Any]] = []
        quarter_rows = symbol_rows.loc[symbol_rows["period_type"].astype(str).str.upper() == "Q"]
        quarter_rows = quarter_rows.drop_duplicates(["period_end"], keep="last")
        for row in quarter_rows.itertuples():
            discrete.append(
                {
                    "period_end": pd.Timestamp(row.period_end),
                    "eps": float(row.value),
                    "available_at": pd.Timestamp(row.available_at),
                    "fiscal_year": int(row.fiscal_year) if not pd.isna(row.fiscal_year) else None,
                    "fiscal_quarter": int(row.fiscal_quarter) if not pd.isna(row.fiscal_quarter) else None,
                    "derivation": "reported_quarter",
                }
            )
        fy_rows = symbol_rows.loc[symbol_rows["period_type"].astype(str).str.upper() == "FY"]
        fy_rows = fy_rows.drop_duplicates(["period_end"], keep="last")
        for fy in fy_rows.itertuples():
            fiscal_year = int(fy.fiscal_year) if not pd.isna(fy.fiscal_year) else None
            same_year = [
                row for row in discrete
                if row["fiscal_year"] == fiscal_year and row["fiscal_quarter"] in {1, 2, 3}
            ]
            quarters = {row["fiscal_quarter"]: row for row in same_year}
            if set(quarters) != {1, 2, 3}:
                continue
            q4_eps = float(fy.value) - sum(float(quarters[q]["eps"]) for q in (1, 2, 3))
            discrete.append(
                {
                    "period_end": pd.Timestamp(fy.period_end),
                    "eps": q4_eps,
                    "available_at": pd.Timestamp(fy.available_at),
                    "fiscal_year": fiscal_year,
                    "fiscal_quarter": 4,
                    "derivation": "fy_minus_q1_q2_q3",
                }
            )
        unique: dict[pd.Timestamp, dict[str, Any]] = {}
        for row in sorted(discrete, key=lambda item: (item["period_end"], item["available_at"])):
            unique[row["period_end"]] = row
        latest = sorted(unique.values(), key=lambda item: item["period_end"])[-4:]
        if len(latest) != 4:
            continue
        results[str(symbol)] = {
            "status": "READY",
            "quarter_count": 4,
            "ttm_eps": sum(float(row["eps"]) for row in latest),
            "earnings_available_through": max(row["available_at"] for row in latest).strftime("%Y-%m-%d"),
            "quarters": [
                {
                    **row,
                    "period_end": row["period_end"].strftime("%Y-%m-%d"),
                    "available_at": row["available_at"].strftime("%Y-%m-%d"),
                }
                for row in latest
            ],
        }
    return results


def _price_at(
    prices: Mapping[str, Mapping[str, Any]],
    symbol: str,
    date_value: str,
) -> float | None:
    return _optional_float((prices.get(symbol) or {}).get(date_value))


def nasdaq100_repair_window(*, end_month: str, months: int = 60) -> tuple[str, str]:
    """Return an inclusive calendar-month repair window."""
    end = pd.Timestamp(end_month).to_period("M").to_timestamp()
    start = end - pd.DateOffset(months=max(1, int(months)) - 1)
    return (
        start.strftime("%Y-%m-%d"),
        (end + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"),
    )


def is_nasdaq100_equity_holding(row: Mapping[str, Any]) -> bool:
    """Exclude cash and derivative rows even when a provider labels them Equity."""
    asset_class = str(row.get("asset_class") or "equity").strip().lower()
    name = str(row.get("holding_name") or "").strip().lower()
    symbol = str(row.get("holding_symbol") or "").strip().upper()
    if asset_class in NON_EQUITY_ASSET_CLASSES or symbol == "USD":
        return False
    return "future" not in name and "synthetic cash" not in name


def _holding_symbol(row: Mapping[str, Any]) -> str:
    value = row.get("holding_symbol")
    if value is None or pd.isna(value):
        return ""
    return str(value).strip().upper()


def drift_holding_weights(
    holdings: Iterable[dict[str, Any]],
    prices: Mapping[str, Mapping[str, Any]],
    *,
    snapshot_date: str,
    observation_month: str,
) -> list[dict[str, Any]]:
    """Drift an anchor's weights by security price return and renormalize valid rows."""
    rows: list[dict[str, Any]] = []
    total = 0.0
    missing_weight = 0.0
    for raw in holdings:
        row = dict(raw)
        symbol = str(row.get("holding_symbol") or "")
        weight = _optional_float(row.get("weight_pct"))
        start = _price_at(prices, symbol, snapshot_date) if symbol else None
        end = _price_at(prices, symbol, observation_month) if symbol else None
        drifted = weight * end / start if weight is not None and start and end else None
        row["snapshot_price"] = start
        row["month_end_price"] = end
        row["drifted_value"] = drifted
        row["month_weight_pct"] = None
        if drifted is not None and drifted > 0:
            total += drifted
        elif weight is not None and weight > 0:
            missing_weight += weight
            row["month_weight_pct"] = weight
        rows.append(row)
    if total > 0:
        valid_weight_budget = max(0.0, 100.0 - missing_weight)
        for row in rows:
            if row["drifted_value"] is not None and row["drifted_value"] > 0:
                row["month_weight_pct"] = row["drifted_value"] / total * valid_weight_budget
    return rows


def reconstruct_monthly_valuation(
    holdings: Iterable[dict[str, Any]],
    eps_by_symbol: Mapping[str, Mapping[str, Any]],
    prices: Mapping[str, Any],
    *,
    observation_month: str,
    qqq_price: float,
    minimum_coverage_pct: float = MINIMUM_COVERAGE_PCT,
) -> dict[str, Any]:
    """Aggregate covered constituent earnings yields without imputing missing weight."""
    coverage = 0.0
    weighted_yield = 0.0
    available_dates: list[str] = []
    for row in holdings:
        symbol = str(row.get("holding_symbol") or "")
        weight = _optional_float(row.get("month_weight_pct"))
        price = _optional_float(prices.get(symbol)) if symbol else None
        evidence = eps_by_symbol.get(symbol) or {}
        eps = _optional_float(evidence.get("ttm_eps"))
        if not symbol or weight is None or weight <= 0 or price is None or price <= 0 or eps is None:
            continue
        coverage += weight
        weighted_yield += (weight / 100.0) * (eps / price)
        if evidence.get("earnings_available_through"):
            available_dates.append(str(evidence["earnings_available_through"]))
    base = {
        "observation_month": pd.Timestamp(observation_month).to_period("M").to_timestamp().strftime("%Y-%m-%d"),
        "proxy_symbol": "QQQ",
        "qqq_price": float(qqq_price),
        "coverage_weight_pct": coverage,
        "unmapped_weight_pct": max(0.0, 100.0 - coverage),
        "earnings_available_through": max(available_dates) if available_dates else None,
    }
    if coverage + 1e-9 < float(minimum_coverage_pct):
        return {
            **base,
            "reconstructed_ttm_eps": None,
            "trailing_pe": None,
            "earnings_yield": None,
            "data_quality": "blocked",
            "error_code": "INSUFFICIENT_EARNINGS_COVERAGE",
        }
    portfolio_yield = weighted_yield / (coverage / 100.0)
    if portfolio_yield <= 0:
        return {
            **base,
            "reconstructed_ttm_eps": None,
            "trailing_pe": None,
            "earnings_yield": portfolio_yield,
            "data_quality": "blocked",
            "error_code": "NON_POSITIVE_AGGREGATE_EARNINGS",
        }
    trailing_pe = 1.0 / portfolio_yield
    return {
        **base,
        "reconstructed_ttm_eps": float(qqq_price) / trailing_pe,
        "trailing_pe": trailing_pe,
        "earnings_yield": portfolio_yield,
        "data_quality": "reconstructed_actual",
        "error_code": None,
    }


def _price_history_frame(price_rows: Iterable[dict[str, Any]]) -> pd.DataFrame:
    frame = pd.DataFrame(list(price_rows))
    if frame.empty or not {"symbol", "date"}.issubset(frame.columns):
        return pd.DataFrame(columns=["symbol", "date", "price"])
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    price_column = "close" if "close" in frame else "adj_close"
    frame["price"] = pd.to_numeric(frame.get(price_column), errors="coerce")
    return (
        frame.dropna(subset=["symbol", "date", "price"])
        .loc[lambda value: value["price"] > 0, ["symbol", "date", "price"]]
        .sort_values(["symbol", "date"])
        .drop_duplicates(["symbol", "date"], keep="last")
        .reset_index(drop=True)
    )


def _latest_prices_as_of(frame: pd.DataFrame, as_of: pd.Timestamp) -> dict[str, dict[str, Any]]:
    eligible = frame.loc[frame["date"] <= as_of]
    if eligible.empty:
        return {}
    latest = eligible.groupby("symbol", as_index=False).tail(1)
    return {
        str(row.symbol): {
            "date": pd.Timestamp(row.date).strftime("%Y-%m-%d"),
            "price": float(row.price),
        }
        for row in latest.itertuples()
    }


def _latest_prices_in_month(frame: pd.DataFrame, month_end: pd.Timestamp) -> dict[str, dict[str, Any]]:
    """Return latest prices only when the symbol traded in the observation month."""
    month_start = month_end.to_period("M").to_timestamp()
    eligible = frame.loc[(frame["date"] >= month_start) & (frame["date"] <= month_end)]
    if eligible.empty:
        return {}
    latest = eligible.groupby("symbol", as_index=False).tail(1)
    return {
        str(row.symbol): {
            "date": pd.Timestamp(row.date).strftime("%Y-%m-%d"),
            "price": float(row.price),
        }
        for row in latest.itertuples()
    }


def materialize_monthly_valuation_rows(
    holding_rows: Iterable[dict[str, Any]],
    statement_rows: Iterable[dict[str, Any]],
    price_rows: Iterable[dict[str, Any]],
    *,
    start_month: str,
    end_month: str,
    minimum_coverage_pct: float = MINIMUM_COVERAGE_PCT,
) -> list[dict[str, Any]]:
    """Build monthly reconstructed QQQ rows from normalized in-memory source rows."""
    holdings = pd.DataFrame(
        [dict(row) for row in holding_rows if is_nasdaq100_equity_holding(row)]
    )
    prices = _price_history_frame(price_rows)
    statements = list(statement_rows)
    if holdings.empty or prices.empty or "as_of_date" not in holdings:
        return []
    holdings["as_of_date"] = pd.to_datetime(holdings["as_of_date"], errors="coerce")
    holdings = holdings.dropna(subset=["as_of_date"]).sort_values("as_of_date")
    if holdings.empty:
        return []

    start = pd.Timestamp(start_month).to_period("M").to_timestamp()
    end = pd.Timestamp(end_month).to_period("M").to_timestamp()
    rows: list[dict[str, Any]] = []
    for month in pd.date_range(start, end, freq="MS"):
        calendar_end = month + pd.offsets.MonthEnd(0)
        eligible_snapshots = holdings.loc[holdings["as_of_date"] <= calendar_end, "as_of_date"]
        if eligible_snapshots.empty:
            continue
        snapshot_date = pd.Timestamp(eligible_snapshots.max())
        snapshot = holdings.loc[holdings["as_of_date"] == snapshot_date].to_dict("records")
        snapshot_prices = _latest_prices_as_of(prices, snapshot_date)
        month_prices = _latest_prices_in_month(prices, calendar_end)
        drift_prices = {
            symbol: {
                snapshot_date.strftime("%Y-%m-%d"): evidence["price"],
                calendar_end.strftime("%Y-%m-%d"): month_prices.get(symbol, {}).get("price"),
            }
            for symbol, evidence in snapshot_prices.items()
        }
        drifted = drift_holding_weights(
            snapshot,
            drift_prices,
            snapshot_date=snapshot_date.strftime("%Y-%m-%d"),
            observation_month=calendar_end.strftime("%Y-%m-%d"),
        )
        eps_by_symbol = derive_filing_aware_ttm_eps(
            statements,
            as_of_date=calendar_end.strftime("%Y-%m-%d"),
        )
        qqq = month_prices.get("QQQ")
        raw_quality = snapshot[0].get("holding_snapshot_quality")
        if raw_quality is None or pd.isna(raw_quality) or str(raw_quality).lower() == "nan":
            quality = (
                "current_issuer_snapshot"
                if str(snapshot[0].get("source") or "").startswith("invesco")
                else "quarterly_anchor"
            )
        else:
            quality = str(raw_quality)
        if qqq is None:
            row = {
                "observation_month": month.strftime("%Y-%m-%d"),
                "proxy_symbol": "QQQ",
                "qqq_price": None,
                "coverage_weight_pct": 0.0,
                "unmapped_weight_pct": 100.0,
                "reconstructed_ttm_eps": None,
                "trailing_pe": None,
                "earnings_yield": None,
                "earnings_available_through": None,
                "data_quality": "blocked",
                "error_code": "INSUFFICIENT_PROXY_PRICE",
            }
        else:
            row = reconstruct_monthly_valuation(
                drifted,
                eps_by_symbol,
                {symbol: evidence["price"] for symbol, evidence in month_prices.items()},
                observation_month=month.strftime("%Y-%m-%d"),
                qqq_price=float(qqq["price"]),
                minimum_coverage_pct=minimum_coverage_pct,
            )
        row.update(
            {
                "holding_snapshot_date": snapshot_date.strftime("%Y-%m-%d"),
                "holding_snapshot_quality": quality,
                "price_basis_date": qqq.get("date") if qqq else None,
            }
        )
        rows.append(row)
    return rows


def build_nasdaq100_coverage_repair_plan(
    holding_rows: Iterable[dict[str, Any]],
    statement_rows: Iterable[dict[str, Any]],
    price_rows: Iterable[dict[str, Any]],
    issue_rows: Iterable[dict[str, Any]] | None = None,
    *,
    start_month: str,
    end_month: str,
) -> dict[str, Any]:
    """Build repeat-safe missing EPS and price targets for a monthly QQQ window."""
    normalized_holdings = [
        dict(row) for row in holding_rows if is_nasdaq100_equity_holding(row)
    ]
    holdings = pd.DataFrame(normalized_holdings)
    prices = _price_history_frame(price_rows)
    statements = list(statement_rows)
    start = pd.Timestamp(start_month).to_period("M").to_timestamp()
    end = pd.Timestamp(end_month).to_period("M").to_timestamp()
    months = list(pd.date_range(start, end, freq="MS"))
    exhausted_prices = {
        str(row.get("symbol") or "").strip().upper()
        for row in list(issue_rows or [])
        if str(row.get("latest_status") or "active").strip().lower() == "active"
    }
    targets: dict[str, dict[str, Any]] = {}
    unsupported_map: dict[tuple[str | None, str], dict[str, Any]] = {}

    if not holdings.empty and "as_of_date" in holdings:
        holdings["as_of_date"] = pd.to_datetime(holdings["as_of_date"], errors="coerce")
        holdings = holdings.dropna(subset=["as_of_date"]).sort_values("as_of_date")

    for month in months:
        calendar_end = month + pd.offsets.MonthEnd(0)
        if holdings.empty:
            continue
        eligible = holdings.loc[holdings["as_of_date"] <= calendar_end]
        if eligible.empty:
            continue
        snapshot_date = pd.Timestamp(eligible["as_of_date"].max())
        snapshot = eligible.loc[eligible["as_of_date"] == snapshot_date].to_dict("records")
        snapshot_prices = _latest_prices_as_of(prices, snapshot_date)
        month_prices = _latest_prices_in_month(prices, calendar_end)
        eps_by_symbol = derive_filing_aware_ttm_eps(
            statements,
            as_of_date=calendar_end.strftime("%Y-%m-%d"),
        )
        month_text = month.strftime("%Y-%m-%d")
        for holding in snapshot:
            symbol = _holding_symbol(holding)
            weight = _optional_float(holding.get("weight_pct")) or 0.0
            if not symbol:
                key = (None, "missing_identity")
                row = unsupported_map.setdefault(
                    key,
                    {
                        "symbol": None,
                        "holding_name": holding.get("holding_name"),
                        "reason": "missing_identity",
                        "affected_months": 0,
                        "max_weight_pct": 0.0,
                    },
                )
                row["affected_months"] += 1
                row["max_weight_pct"] = max(float(row["max_weight_pct"]), weight)
                continue

            needs: set[str] = set()
            if symbol not in eps_by_symbol:
                needs.add("quarterly_diluted_eps")
            if symbol not in snapshot_prices or symbol not in month_prices:
                if symbol in exhausted_prices:
                    key = (symbol, "unsupported_free_source")
                    row = unsupported_map.setdefault(
                        key,
                        {
                            "symbol": symbol,
                            "holding_name": holding.get("holding_name"),
                            "reason": "unsupported_free_source",
                            "affected_months": 0,
                            "max_weight_pct": 0.0,
                        },
                    )
                    row["affected_months"] += 1
                    row["max_weight_pct"] = max(float(row["max_weight_pct"]), weight)
                else:
                    needs.add("eod_price")
            if not needs:
                continue
            target = targets.setdefault(
                symbol,
                {
                    "symbol": symbol,
                    "issuer_cik": holding.get("issuer_cik"),
                    "needs": set(),
                    "affected_months_set": set(),
                    "max_weight_pct": 0.0,
                    "start_date": snapshot_date.strftime("%Y-%m-%d"),
                    "end_date": calendar_end.strftime("%Y-%m-%d"),
                },
            )
            target["needs"].update(needs)
            target["affected_months_set"].add(month_text)
            target["max_weight_pct"] = max(float(target["max_weight_pct"]), weight)
            target["start_date"] = min(
                str(target["start_date"]), snapshot_date.strftime("%Y-%m-%d")
            )
            target["end_date"] = max(
                str(target["end_date"]), calendar_end.strftime("%Y-%m-%d")
            )

    normalized_targets = []
    for target in targets.values():
        affected = target.pop("affected_months_set")
        normalized_targets.append(
            {
                **target,
                "needs": sorted(target["needs"]),
                "affected_months": len(affected),
            }
        )
    materialized = materialize_monthly_valuation_rows(
        normalized_holdings,
        statements,
        list(price_rows) if isinstance(price_rows, list) else prices.rename(
            columns={"price": "close"}
        ).to_dict("records"),
        start_month=start_month,
        end_month=end_month,
    )
    ready_rows = [
        row for row in materialized if row.get("data_quality") == "reconstructed_actual"
    ]
    return {
        "window": {
            "start_month": start.strftime("%Y-%m-%d"),
            "end_month": (end + pd.offsets.MonthEnd(0)).strftime("%Y-%m-%d"),
            "months": len(months),
        },
        "targets": sorted(
            normalized_targets,
            key=lambda row: (-float(row["max_weight_pct"]), str(row["symbol"])),
        ),
        "unsupported": sorted(
            unsupported_map.values(),
            key=lambda row: (-float(row["max_weight_pct"]), str(row.get("symbol") or "")),
        ),
        "before": {
            "ready_months": len(ready_rows),
            "blocked_months": max(0, len(months) - len(ready_rows)),
        },
    }


def evaluate_pe_calibration(
    reconstructed_rows: Iterable[dict[str, Any]],
    fixtures: Iterable[dict[str, Any]],
    *,
    median_limit_pct: float = CALIBRATION_MEDIAN_LIMIT_PCT,
    max_limit_pct: float = CALIBRATION_MAX_LIMIT_PCT,
) -> dict[str, Any]:
    """Apply the approved median/max APE production gate to matched month fixtures."""
    reconstructed: dict[str, float] = {}
    for row in reconstructed_rows:
        value = _optional_float(row.get("trailing_pe"))
        if value is None or value <= 0:
            continue
        month = pd.Timestamp(row.get("observation_month")).to_period("M").to_timestamp().strftime("%Y-%m-%d")
        reconstructed[month] = value
    observations: list[dict[str, Any]] = []
    for fixture in fixtures:
        expected = _optional_float(fixture.get("trailing_pe"))
        if expected is None or expected <= 0:
            continue
        month = pd.Timestamp(fixture.get("observation_month")).to_period("M").to_timestamp().strftime("%Y-%m-%d")
        actual = reconstructed.get(month)
        if actual is None:
            continue
        ape = abs(actual - expected) / expected * 100.0
        observations.append(
            {
                "observation_month": month,
                "reconstructed_pe": actual,
                "fixture_pe": expected,
                "absolute_percentage_error_pct": ape,
            }
        )
    if not observations:
        return {
            "status": "BLOCKED",
            "reason": "NO_MATCHED_CALIBRATION_OBSERVATIONS",
            "observation_count": 0,
            "median_ape_pct": None,
            "max_ape_pct": None,
            "observations": [],
        }
    errors = [float(row["absolute_percentage_error_pct"]) for row in observations]
    median_error = statistics.median(errors)
    max_error = max(errors)
    ready = median_error <= float(median_limit_pct) and max_error <= float(max_limit_pct)
    return {
        "status": "READY" if ready else "BLOCKED",
        "reason": None if ready else "CALIBRATION_ERROR_EXCEEDED",
        "observation_count": len(observations),
        "median_ape_pct": median_error,
        "max_ape_pct": max_error,
        "median_limit_pct": float(median_limit_pct),
        "max_limit_pct": float(max_limit_pct),
        "observations": observations,
    }


def _load_qqq_identity_rows(
    *,
    db_factory: Any,
    host: str,
    user: str,
    password: str,
    port: int,
) -> list[dict[str, Any]]:
    db = _open_meta_db(db_factory, host=host, user=user, password=password, port=port)
    try:
        holdings = db.query(
            """
            SELECT cusip, holding_symbol AS symbol, issuer_cik, holding_name AS name
            FROM etf_holdings_snapshot
            WHERE fund_symbol = 'QQQ' AND holding_symbol IS NOT NULL
            ORDER BY as_of_date DESC
            """,
            (),
        )
        lifecycle = db.query(
            """
            SELECT NULL AS cusip, symbol, related_cik AS issuer_cik, name
            FROM nyse_symbol_lifecycle
            WHERE kind = 'stock' AND name IS NOT NULL
            """,
            (),
        )
        return list(holdings) + list(lifecycle)
    finally:
        db.close()


def collect_and_store_qqq_sec_holdings(
    *,
    submissions_payload: Mapping[str, Any] | None = None,
    identity_rows: Iterable[dict[str, Any]] | None = None,
    start_date: str = "2016-09-01",
    end_date: str | None = None,
    fetch_text_fn: Any = fetch_sec_text,
    rows_writer: Any = store_qqq_holdings_rows,
    collected_at: str | None = None,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Collect free, accountless official QQQ holdings filings and upsert normalized rows."""
    if submissions_payload is None:
        submissions_payload = json.loads(
            fetch_text_fn(f"https://data.sec.gov/submissions/CIK{QQQ_CIK}.json")
        )
    identities = list(identity_rows) if identity_rows is not None else _load_qqq_identity_rows(
        db_factory=db_factory, host=host, user=user, password=password, port=port
    )
    start = pd.Timestamp(start_date)
    end = pd.Timestamp(end_date) if end_date else pd.Timestamp.now(tz="UTC").tz_localize(None)
    filings = [
        row for row in discover_qqq_sec_filings(submissions_payload)
        if start <= pd.Timestamp(row["report_date"]) <= end
    ]
    # N-30B-2 is the pre-NPORT annual anchor; prefer NPORT if both exist for a date.
    selected: dict[str, dict[str, Any]] = {}
    for filing in filings:
        key = str(filing["report_date"])
        existing = selected.get(key)
        if existing is None or str(filing.get("form", "")).startswith("NPORT"):
            selected[key] = filing

    normalized: list[dict[str, Any]] = []
    warnings: list[str] = []
    timestamp = collected_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    for filing in sorted(selected.values(), key=lambda row: row["report_date"]):
        try:
            document = fetch_text_fn(filing["source_url"])
            parsed = (
                parse_qqq_nport_xml(document, filing=filing)
                if str(filing.get("form", "")).startswith("NPORT")
                else parse_qqq_n30b2_html(document, filing=filing)
            )
        except Exception as exc:
            warnings.append(f"{filing['report_date']}: {exc}")
            continue
        for row in resolve_holding_identities(parsed, identities):
            missing = [field for field in ("holding_symbol", "issuer_cik") if not row.get(field)]
            row.update(
                {
                    "fund_symbol": "QQQ",
                    "source_type": "official",
                    "sector": row.get("sector"),
                    "country": row.get("country"),
                    "currency": row.get("currency") or "USD",
                    "coverage_status": "actual" if not missing else "partial",
                    "missing_fields_json": json.dumps(missing) if missing else None,
                    "collected_at": timestamp,
                    "error_msg": None,
                }
            )
            normalized.append(row)
    rows_writer(
        normalized,
        db_factory=db_factory,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    return {
        "rows_written": len(normalized),
        "snapshot_count": len({row["as_of_date"] for row in normalized}),
        "unresolved_rows": sum(not row.get("holding_symbol") for row in normalized),
        "warnings": warnings,
    }


def _load_nasdaq100_materialization_inputs(
    *,
    start_month: str,
    end_month: str,
    db_factory: Any,
    host: str,
    user: str,
    password: str,
    port: int,
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    db = db_factory(host, user, password, port)
    try:
        db.use_db(DB_META)
        holdings = db.query(
            """
            SELECT as_of_date, source, holding_symbol, holding_name, asset_class,
                   issuer_cik, weight_pct, holding_snapshot_quality
            FROM etf_holdings_snapshot
            WHERE fund_symbol = 'QQQ' AND as_of_date <= %s
            ORDER BY as_of_date, weight_pct DESC
            """,
            (end_month,),
        )
        symbols = sorted(
            {
                str(row["holding_symbol"])
                for row in holdings
                if row.get("holding_symbol") and is_nasdaq100_equity_holding(row)
            }
        )
        statements: list[dict[str, Any]] = []
        prices: list[dict[str, Any]] = []
        if symbols:
            placeholders = ",".join(["%s"] * len(symbols))
            db.use_db("finance_fundamental")
            statements = db.query(
                f"""
                SELECT symbol,
                       CASE WHEN concept LIKE '%%:%%' THEN concept
                            ELSE CONCAT(COALESCE(taxonomy, 'us-gaap'), ':', concept) END AS concept,
                       unit, source_period_type, period_type, fiscal_year, fiscal_quarter,
                       period_start, period_end, value, available_at, form_type, accession_no
                FROM nyse_financial_statement_values
                WHERE symbol IN ({placeholders})
                  AND (concept LIKE '%%EarningsPerShareDiluted'
                       OR concept LIKE '%%EarningsPerShareBasicAndDiluted'
                       OR concept LIKE '%%DilutedEarningsLossPerShare')
                  AND unit IN ('USD per share', 'USD/shares', 'USD/share')
                  AND available_at <= %s
                """,
                tuple(symbols) + (end_month,),
            )
            db.use_db("finance_price")
            price_start = (
                pd.Timestamp(start_month) - pd.DateOffset(years=1)
            ).strftime("%Y-%m-%d")
            prices = db.query(
                f"""
                SELECT symbol, `date`, close, adj_close
                FROM nyse_price_history
                WHERE symbol IN ({','.join(['%s'] * (len(symbols) + 1))})
                  AND timeframe = '1d' AND `date` BETWEEN %s AND %s
                ORDER BY symbol, `date`
                """,
                tuple(symbols + ["QQQ"]) + (price_start, end_month),
            )
        return list(holdings), list(statements), list(prices)
    finally:
        db.close()


def _load_nasdaq100_limited_price_issues(
    *,
    db_factory: Any,
    host: str,
    user: str,
    password: str,
    port: int,
) -> list[dict[str, Any]]:
    db = db_factory(host, user, password, port)
    try:
        db.use_db(DB_META)
        return list(
            db.query(
                """
                SELECT symbol, latest_status, diagnosis, latest_evidence
                FROM market_data_issue
                WHERE universe_code = 'NASDAQ100'
                  AND issue_type = 'limited_price_history'
                  AND latest_status = 'active'
                ORDER BY symbol
                """,
                (),
            )
        )
    finally:
        db.close()


def load_nasdaq100_coverage_repair_plan(
    *,
    months: int = 60,
    end_month: str | None = None,
    input_loader: Any = None,
    issue_loader: Any = None,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Load stored inputs and return a deterministic Nasdaq repair plan."""
    resolved_end = end_month or pd.Timestamp.today().strftime("%Y-%m-%d")
    start, end = nasdaq100_repair_window(end_month=resolved_end, months=months)
    load_inputs = input_loader or _load_nasdaq100_materialization_inputs
    load_issues = issue_loader or _load_nasdaq100_limited_price_issues
    holdings, statements, prices = load_inputs(
        start_month=start,
        end_month=end,
        db_factory=db_factory,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    issues = load_issues(
        db_factory=db_factory,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    return build_nasdaq100_coverage_repair_plan(
        holdings,
        statements,
        prices,
        issues,
        start_month=start,
        end_month=end,
    )


def materialize_and_store_nasdaq100_monthly(
    *,
    start_month: str = "2016-09-01",
    end_month: str | None = None,
    holding_rows: Iterable[dict[str, Any]] | None = None,
    statement_rows: Iterable[dict[str, Any]] | None = None,
    price_rows: Iterable[dict[str, Any]] | None = None,
    rows_writer: Any = store_nasdaq100_monthly_rows,
    collected_at: str | None = None,
    db_factory: Any = MySQLClient,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Materialize DB-backed monthly rows while retaining failed coverage gates."""
    resolved_end = end_month or pd.Timestamp.today().strftime("%Y-%m-%d")
    if holding_rows is None or statement_rows is None or price_rows is None:
        holding_rows, statement_rows, price_rows = _load_nasdaq100_materialization_inputs(
            start_month=start_month, end_month=resolved_end, db_factory=db_factory,
            host=host, user=user, password=password, port=port,
        )
    rows = materialize_monthly_valuation_rows(
        holding_rows, statement_rows, price_rows,
        start_month=start_month, end_month=resolved_end,
    )
    timestamp = collected_at or datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")
    source_ref = f"https://www.sec.gov/Archives/edgar/data/{int(QQQ_CIK)}"
    for row in rows:
        row.update(
            {
                "source": "sec_qqq_holdings_sec_actual",
                "source_ref": source_ref,
                "collected_at": timestamp,
                "error_msg": row.pop("error_code", None),
            }
        )
    rows_writer(
        rows, db_factory=db_factory, host=host, user=user, password=password, port=port
    )
    return {
        "rows_written": len(rows),
        "ready_rows": sum(row["data_quality"] == "reconstructed_actual" for row in rows),
        "blocked_rows": sum(row["data_quality"] == "blocked" for row in rows),
        "latest_coverage_weight_pct": rows[-1]["coverage_weight_pct"] if rows else None,
        "warnings": [] if rows else ["materialization inputs produced no monthly rows"],
    }
