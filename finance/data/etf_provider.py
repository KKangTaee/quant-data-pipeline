from __future__ import annotations

import csv
import html
import io
import json
import re
import xml.etree.ElementTree as ET
from zipfile import ZipFile
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.request import Request, urlopen

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
DB_PRICE = "finance_price"
SOURCE_MAP_TABLE = "etf_provider_source_map"
OPERABILITY_TABLE = "etf_operability_snapshot"
HOLDINGS_TABLE = "etf_holdings_snapshot"
EXPOSURE_TABLE = "etf_exposure_snapshot"
DEFAULT_LOOKBACK_DAYS = 60
OFFICIAL_REQUEST_TIMEOUT = 20
OFFICIAL_USER_AGENT = (
    "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
    "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0 Safari/537.36"
)
OFFICIAL_PROVIDER_SOURCES: dict[str, dict[str, Any]] = {
    "AOR": {
        "source": "ishares",
        "parser": "ishares",
        "url": "https://www.ishares.com/us/products/239756/ishares-core-60-40-balanced-allocation-etf",
        "fund_family": "iShares",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
    "IEF": {
        "source": "ishares",
        "parser": "ishares",
        "url": "https://www.ishares.com/us/products/239456/ishares-7-10-year-treasury-bond-etf",
        "fund_family": "iShares",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
    "TLT": {
        "source": "ishares",
        "parser": "ishares",
        "url": "https://www.ishares.com/us/products/239454/ishares-20-year-treasury-bond-etf",
        "fund_family": "iShares",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
    "SPY": {
        "source": "ssga",
        "parser": "ssga",
        "url": "https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy",
        "fund_family": "SPDR",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
    "BIL": {
        "source": "ssga",
        "parser": "ssga",
        "url": "https://www.ssga.com/us/en/intermediary/etfs/spdr-bloomberg-1-3-month-t-bill-etf-bil",
        "fund_family": "SPDR",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
    "GLD": {
        "source": "ssga",
        "parser": "ssga",
        "url": "https://www.ssga.com/us/en/intermediary/etfs/spdr-gold-shares-gld",
        "fund_family": "SPDR",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
    "QQQ": {
        "source": "invesco",
        "parser": "invesco",
        "url": "https://www.invesco.com/qqq-etf/en/home.html",
        "fund_family": "Invesco",
        "leverage_factor": 1.0,
        "is_inverse": False,
        "has_daily_objective": False,
    },
}
HOLDINGS_PROVIDER_SOURCES: dict[str, dict[str, Any]] = {
    "AOR": {
        "source": "ishares",
        "parser": "ishares_csv",
        "url": "https://www.ishares.com/us/products/239756/ishares-core-60-40-balanced-allocation-etf/1467271812596.ajax?fileType=csv&fileName=AOR_holdings&dataType=fund",
    },
    "IEF": {
        "source": "ishares",
        "parser": "ishares_csv",
        "url": "https://www.ishares.com/us/products/239456/ishares-7-10-year-treasury-bond-etf/1467271812596.ajax?fileType=csv&fileName=IEF_holdings&dataType=fund",
    },
    "TLT": {
        "source": "ishares",
        "parser": "ishares_csv",
        "url": "https://www.ishares.com/us/products/239454/ishares-20-year-treasury-bond-etf/1467271812596.ajax?fileType=csv&fileName=TLT_holdings&dataType=fund",
    },
    "SPY": {
        "source": "ssga",
        "parser": "ssga_xlsx",
        "url": "https://www.ssga.com/library-content/products/fund-data/etfs/us/holdings-daily-us-en-spy.xlsx",
        "page_url": "https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy",
        "asset_class": "Equity",
    },
    "BIL": {
        "source": "ssga",
        "parser": "ssga_xlsx",
        "url": "https://www.ssga.com/library-content/products/fund-data/etfs/us/holdings-daily-us-en-bil.xlsx",
        "page_url": "https://www.ssga.com/us/en/intermediary/etfs/spdr-bloomberg-1-3-month-t-bill-etf-bil",
        "asset_class": "Fixed Income",
    },
    "GLD": {
        "source": "ssga",
        "parser": "pending",
        "url": "https://www.spdrgoldshares.com/usa/gld/",
        "asset_class": "Commodity",
    },
    "QQQ": {
        "source": "invesco",
        "parser": "invesco_json",
        "url": "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/QQQ/holdings/fund?idType=ticker&interval=monthly&productType=ETF",
        "page_url": "https://www.invesco.com/qqq-etf/en/about.html",
        "asset_class": "Equity",
    },
}
EXPOSURE_PROVIDER_SOURCES: dict[str, dict[str, Any]] = {
    "SPY": {
        "source": "ssga",
        "parser": "ssga_sector_page",
        "url": "https://www.ssga.com/us/en/intermediary/etfs/state-street-spdr-sp-500-etf-trust-spy",
    },
    "QQQ": {
        "source": "invesco",
        "parser": "invesco_sector_json",
        "url": "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/QQQ/weightedHoldings/fund?idType=ticker&productType=ETF&breakdown=sector",
        "page_url": "https://www.invesco.com/qqq-etf/en/about.html",
    },
}

ISHARES_PRODUCT_LIST_URL = "https://www.ishares.com/us/products/etf-investments"
SSGA_HOLDINGS_URL_TEMPLATE = (
    "https://www.ssga.com/library-content/products/fund-data/etfs/us/"
    "holdings-daily-us-en-{symbol}.xlsx"
)
INVESCO_HOLDINGS_URL_TEMPLATE = (
    "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/{symbol}/holdings/fund"
    "?idType=ticker&interval=monthly&productType=ETF"
)
INVESCO_SECTOR_URL_TEMPLATE = (
    "https://dng-api.invesco.com/cache/v1/accounts/en_US/shareclasses/{symbol}/weightedHoldings/fund"
    "?idType=ticker&productType=ETF&breakdown=sector"
)


def _sync_provider_source_map_schema(db: MySQLClient) -> None:
    db.execute(PROVIDER_SCHEMAS["etf_provider_source_map"])
    sync_table_schema(db, SOURCE_MAP_TABLE, PROVIDER_SCHEMAS["etf_provider_source_map"], DB_META)


def _infer_provider_key(*values: Any) -> str | None:
    text = " ".join(str(value or "") for value in values).lower()
    if "ishares" in text or "blackrock" in text:
        return "ishares"
    if "state street" in text or "spdr" in text or "select sector" in text:
        return "ssga"
    if "invesco" in text or "qqq" in text:
        return "invesco"
    if "vanguard" in text:
        return "vanguard"
    return None


def _is_gold_or_commodity_etf(*values: Any) -> bool:
    text = " ".join(str(value or "") for value in values).lower()
    return "gold" in text or "bullion" in text


def _fetch_ishares_product_index(timeout: int = OFFICIAL_REQUEST_TIMEOUT) -> dict[str, dict[str, str]]:
    document = _fetch_official_html(ISHARES_PRODUCT_LIST_URL, timeout=timeout)
    index: dict[str, dict[str, str]] = {}
    pattern = re.compile(
        r'<td class="links"><a href="(?P<href>/us/products/(?P<product_id>\d+)/(?P<slug>[^"]+))">'
        r"(?P<symbol>[A-Z0-9.\-]+)</a></td>",
        re.IGNORECASE,
    )
    for match in pattern.finditer(document):
        symbol = match.group("symbol").upper()
        href = html.unescape(match.group("href"))
        index[symbol] = {
            "symbol": symbol,
            "product_id": match.group("product_id"),
            "product_slug": match.group("slug"),
            "product_url": f"https://www.ishares.com{href}",
            "holdings_url": (
                f"https://www.ishares.com{href}/1467271812596.ajax?"
                f"fileType=csv&fileName={symbol}_holdings&dataType=fund"
            ),
        }
    return index


def _source_map_row(
    *,
    symbol: str,
    provider: str,
    data_kind: str,
    parser: str,
    source_url: str,
    source_status: str = "candidate",
    source_ref: str | None = None,
    fund_family: str | None = None,
    product_id: str | None = None,
    product_slug: str | None = None,
    discovered_from: str | None = None,
    metadata: dict[str, Any] | None = None,
    verified_at: str | None = None,
    last_checked_at: str | None = None,
    error_msg: str | None = None,
) -> dict[str, Any]:
    return {
        "symbol": str(symbol or "").upper(),
        "provider": provider,
        "data_kind": data_kind,
        "parser": parser,
        "source_url": source_url,
        "source_ref": source_ref,
        "source_status": source_status,
        "fund_family": fund_family,
        "product_id": product_id,
        "product_slug": product_slug,
        "discovered_from": discovered_from,
        "metadata_json": json.dumps(metadata or {}, ensure_ascii=False),
        "verified_at": verified_at,
        "last_checked_at": last_checked_at,
        "error_msg": error_msg,
    }


def _static_source_map_rows(symbol: str) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    if symbol in OFFICIAL_PROVIDER_SOURCES:
        info = OFFICIAL_PROVIDER_SOURCES[symbol]
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider=str(info.get("source") or "official"),
                data_kind="operability",
                parser=str(info.get("parser") or ""),
                source_url=str(info.get("url") or ""),
                source_status="verified",
                fund_family=info.get("fund_family"),
                discovered_from="static_code_map",
                metadata={key: info.get(key) for key in ("leverage_factor", "is_inverse", "has_daily_objective")},
                verified_at=_utc_now_string(),
                last_checked_at=_utc_now_string(),
            )
        )
    if symbol in HOLDINGS_PROVIDER_SOURCES:
        info = HOLDINGS_PROVIDER_SOURCES[symbol]
        parser = str(info.get("parser") or "")
        status = "unsupported" if parser == "pending" else "verified"
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider=str(info.get("source") or "official"),
                data_kind="holdings",
                parser=parser,
                source_url=str(info.get("url") or ""),
                source_status=status,
                source_ref=info.get("page_url"),
                discovered_from="static_code_map",
                metadata={key: info.get(key) for key in ("asset_class",)},
                verified_at=_utc_now_string() if status == "verified" else None,
                last_checked_at=_utc_now_string(),
                error_msg="official row-level holdings source pending" if parser == "pending" else None,
            )
        )
    if symbol in EXPOSURE_PROVIDER_SOURCES:
        info = EXPOSURE_PROVIDER_SOURCES[symbol]
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider=str(info.get("source") or "official"),
                data_kind="exposure",
                parser=str(info.get("parser") or ""),
                source_url=str(info.get("url") or ""),
                source_status="verified",
                source_ref=info.get("page_url"),
                discovered_from="static_code_map",
                verified_at=_utc_now_string(),
                last_checked_at=_utc_now_string(),
            )
        )
    return rows


def _verify_provider_source(row: dict[str, Any], *, timeout: int = OFFICIAL_REQUEST_TIMEOUT) -> dict[str, Any]:
    checked_at = _utc_now_string()
    parser = str(row.get("parser") or "")
    source_url = str(row.get("source_url") or "")
    try:
        if parser == "ishares_csv":
            data = _fetch_official_bytes(source_url, timeout=timeout, accept="text/csv,*/*")
            ok = len(data) > 100 and (b"Fund Holdings as of" in data[:1000] or b"Ticker,Name" in data[:3000])
            if not ok:
                raise RuntimeError("iShares holdings CSV did not contain holdings content")
        elif parser == "ssga_xlsx":
            data = _fetch_official_bytes(
                source_url,
                timeout=timeout,
                accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
            )
            if data[:2] != b"PK":
                raise RuntimeError("SSGA holdings endpoint did not return an XLSX payload")
        elif parser == "invesco_json":
            payload = _fetch_official_json(source_url, timeout=timeout)
            if "holdings" not in payload:
                raise RuntimeError("Invesco holdings payload has no holdings key")
        elif parser == "invesco_sector_json":
            payload = _fetch_official_json(source_url, timeout=timeout)
            if "holdingWeights" not in payload:
                raise RuntimeError("Invesco sector payload has no holdingWeights key")
        elif parser == "commodity_gold":
            pass
        elif parser in {"ishares", "ssga", "invesco"}:
            _fetch_official_html(source_url, timeout=timeout)
        else:
            return {**row, "source_status": "unsupported", "last_checked_at": checked_at, "error_msg": f"unsupported parser: {parser}"}
    except Exception as exc:
        return {**row, "source_status": "failed", "last_checked_at": checked_at, "error_msg": str(exc)[:1000]}
    return {**row, "source_status": "verified", "verified_at": checked_at, "last_checked_at": checked_at, "error_msg": None}


def _candidate_source_rows_for_universe_row(
    row: dict[str, Any],
    *,
    ishares_index: dict[str, dict[str, str]] | None = None,
) -> list[dict[str, Any]]:
    symbol = str(row.get("symbol") or "").upper()
    fund_family = _to_none(row.get("fund_family"))
    long_name = _to_none(row.get("long_name"))
    name = _to_none(row.get("name"))
    provider = _infer_provider_key(fund_family, long_name, name)
    rows = _static_source_map_rows(symbol)

    if _is_gold_or_commodity_etf(long_name, name):
        rows = [
            source_row
            for source_row in rows
            if not (
                source_row.get("data_kind") in {"holdings", "exposure"}
                and source_row.get("parser") == "pending"
            )
        ]
        if provider == "ishares" and ishares_index and symbol in ishares_index:
            product = ishares_index[symbol]
            rows.append(
                _source_map_row(
                    symbol=symbol,
                    provider="ishares",
                    data_kind="operability",
                    parser="ishares",
                    source_url=product["product_url"],
                    source_status="candidate",
                    fund_family=fund_family or "iShares",
                    product_id=product.get("product_id"),
                    product_slug=product.get("product_slug"),
                    discovered_from="ishares_product_list",
                )
            )
        gold_provider = provider or "commodity"
        for data_kind in ("holdings", "exposure"):
            rows.append(
                _source_map_row(
                    symbol=symbol,
                    provider=gold_provider,
                    data_kind=data_kind,
                    parser="commodity_gold",
                    source_url=str(row.get("url") or f"commodity://gold/{symbol.lower()}"),
                    source_status="candidate",
                    fund_family=fund_family,
                    discovered_from="asset_profile_gold_rule",
                    metadata={"asset_class": "Gold", "holding_name": "Gold Bullion"},
                )
            )
        return rows

    if provider == "ishares" and ishares_index and symbol in ishares_index:
        product = ishares_index[symbol]
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider="ishares",
                data_kind="operability",
                parser="ishares",
                source_url=product["product_url"],
                source_status="candidate",
                fund_family=fund_family or "iShares",
                product_id=product.get("product_id"),
                product_slug=product.get("product_slug"),
                discovered_from="ishares_product_list",
            )
        )
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider="ishares",
                data_kind="holdings",
                parser="ishares_csv",
                source_url=product["holdings_url"],
                source_ref=product["product_url"],
                source_status="candidate",
                fund_family=fund_family or "iShares",
                product_id=product.get("product_id"),
                product_slug=product.get("product_slug"),
                discovered_from="ishares_product_list",
            )
        )
    elif provider == "ssga":
        holdings_url = SSGA_HOLDINGS_URL_TEMPLATE.format(symbol=symbol.lower())
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider="ssga",
                data_kind="holdings",
                parser="ssga_xlsx",
                source_url=holdings_url,
                source_status="candidate",
                fund_family=fund_family,
                discovered_from="ssga_symbol_pattern",
                metadata={"asset_class": "Equity"},
            )
        )
    elif provider == "invesco":
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider="invesco",
                data_kind="holdings",
                parser="invesco_json",
                source_url=INVESCO_HOLDINGS_URL_TEMPLATE.format(symbol=symbol),
                source_status="candidate",
                fund_family=fund_family,
                discovered_from="invesco_symbol_pattern",
                metadata={"asset_class": "Equity"},
            )
        )
        rows.append(
            _source_map_row(
                symbol=symbol,
                provider="invesco",
                data_kind="exposure",
                parser="invesco_sector_json",
                source_url=INVESCO_SECTOR_URL_TEMPLATE.format(symbol=symbol),
                source_status="candidate",
                fund_family=fund_family,
                discovered_from="invesco_symbol_pattern",
            )
        )

    return rows


def _dedupe_source_map_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    priority = {"verified": 5, "candidate": 4, "failed": 3, "unsupported": 2, "missing": 1}
    deduped: dict[tuple[str, str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row.get("symbol") or "").upper(),
            str(row.get("data_kind") or ""),
            str(row.get("provider") or ""),
            str(row.get("parser") or ""),
        )
        existing = deduped.get(key)
        if existing is None or priority.get(str(row.get("source_status")), 0) >= priority.get(str(existing.get("source_status")), 0):
            deduped[key] = row
    return list(deduped.values())


def _load_etf_universe_rows(
    db: MySQLClient,
    *,
    symbols: list[str] | None = None,
    limit: int | None = None,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []
    if symbols:
        placeholders = ",".join(["%s"] * len(symbols))
        where.append(f"ne.symbol IN ({placeholders})")
        params.extend(symbols)
    base_where = f"WHERE {' AND '.join(where)}" if where else ""
    limit_sql = " LIMIT %s" if limit is not None and int(limit) > 0 else ""
    if limit_sql:
        params.append(int(limit))
    return db.query(
        f"""
        SELECT
          ne.symbol,
          ne.name,
          ne.url,
          nap.long_name,
          nap.fund_family,
          nap.exchange,
          nap.total_assets,
          nap.status AS profile_status
        FROM nyse_etf ne
        LEFT JOIN nyse_asset_profile nap
          ON nap.symbol = ne.symbol
         AND nap.kind = 'etf'
        {base_where}
        ORDER BY ne.symbol ASC
        {limit_sql}
        """,
        params,
    )


def _upsert_etf_provider_source_map_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    sql = f"""
    INSERT INTO {SOURCE_MAP_TABLE} (
      symbol, provider, data_kind, parser, source_url, source_ref,
      source_status, fund_family, product_id, product_slug, discovered_from,
      metadata_json, verified_at, last_checked_at, error_msg
    )
    VALUES (
      %(symbol)s, %(provider)s, %(data_kind)s, %(parser)s, %(source_url)s, %(source_ref)s,
      %(source_status)s, %(fund_family)s, %(product_id)s, %(product_slug)s, %(discovered_from)s,
      %(metadata_json)s, %(verified_at)s, %(last_checked_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_url = VALUES(source_url),
      source_ref = VALUES(source_ref),
      source_status = VALUES(source_status),
      fund_family = VALUES(fund_family),
      product_id = VALUES(product_id),
      product_slug = VALUES(product_slug),
      discovered_from = VALUES(discovered_from),
      metadata_json = VALUES(metadata_json),
      verified_at = VALUES(verified_at),
      last_checked_at = VALUES(last_checked_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


def load_etf_provider_source_map(
    symbols: str | Iterable[str] | None = None,
    *,
    data_kind: str | None = None,
    only_verified: bool = True,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    """Load cached ETF provider source mappings discovered from ETF universe/profile data."""
    normalized_symbols = _normalize_symbols(symbols) if symbols is not None else []
    where: list[str] = []
    params: list[Any] = []
    if normalized_symbols:
        placeholders = ",".join(["%s"] * len(normalized_symbols))
        where.append(f"symbol IN ({placeholders})")
        params.extend(normalized_symbols)
    if data_kind:
        where.append("data_kind = %s")
        params.append(str(data_kind).strip())
    if only_verified:
        where.append("source_status = 'verified'")
    base_where = f"WHERE {' AND '.join(where)}" if where else ""

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        _sync_provider_source_map_schema(db)
        return db.query(
            f"""
            SELECT *
            FROM {SOURCE_MAP_TABLE}
            {base_where}
            ORDER BY symbol ASC, data_kind ASC, provider ASC, parser ASC
            """,
            params,
        )
    finally:
        db.close()


def _source_map_info_by_symbol(symbols: list[str], *, data_kind: str, only_source: str | None = None) -> dict[str, dict[str, Any]]:
    rows = load_etf_provider_source_map(symbols, data_kind=data_kind, only_verified=True)
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = str(row.get("symbol") or "").upper()
        if not symbol:
            continue
        if only_source is not None and str(row.get("provider") or "").lower() != str(only_source).lower():
            continue
        metadata = {}
        try:
            metadata = json.loads(row.get("metadata_json") or "{}")
        except Exception:
            metadata = {}
        out[symbol] = {
            "source": row.get("provider"),
            "parser": row.get("parser"),
            "url": row.get("source_url"),
            "page_url": row.get("source_ref"),
            "asset_class": metadata.get("asset_class"),
            "holding_name": metadata.get("holding_name"),
            "fund_family": row.get("fund_family"),
        }
    return out


def discover_and_store_etf_provider_source_map(
    symbols: str | Iterable[str] | None = None,
    *,
    limit: int | None = None,
    verify: bool = True,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Discover official ETF provider endpoints from NYSE universe/profile rows and cache them in DB."""
    normalized_symbols = _normalize_symbols(symbols) if symbols is not None else None
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        _sync_provider_source_map_schema(db)
        universe_rows = _load_etf_universe_rows(db, symbols=normalized_symbols, limit=limit)
    finally:
        db.close()

    needs_ishares_index = any(
        _infer_provider_key(row.get("fund_family"), row.get("long_name"), row.get("name")) == "ishares"
        and not _is_gold_or_commodity_etf(row.get("long_name"), row.get("name"))
        for row in universe_rows
    )
    ishares_index: dict[str, dict[str, str]] = {}
    index_error: str | None = None
    if needs_ishares_index:
        try:
            ishares_index = _fetch_ishares_product_index(timeout=timeout)
        except Exception as exc:
            index_error = str(exc)[:1000]

    rows: list[dict[str, Any]] = []
    for universe_row in universe_rows:
        rows.extend(_candidate_source_rows_for_universe_row(universe_row, ishares_index=ishares_index))
    rows = _dedupe_source_map_rows(rows)
    if verify:
        rows = [_verify_provider_source(row, timeout=timeout) for row in rows]
    elif rows:
        checked_at = _utc_now_string()
        rows = [{**row, "last_checked_at": row.get("last_checked_at") or checked_at} for row in rows]

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        _sync_provider_source_map_schema(db)
        _upsert_etf_provider_source_map_rows(db, rows)
    finally:
        db.close()

    status_counts: dict[str, int] = {}
    for row in rows:
        status = str(row.get("source_status") or "candidate")
        status_counts[status] = status_counts.get(status, 0) + 1
    failed = [
        {"symbol": row.get("symbol"), "data_kind": row.get("data_kind"), "reason": row.get("error_msg")}
        for row in rows
        if row.get("source_status") in {"failed", "unsupported", "missing"}
    ]
    return {
        "requested": len(universe_rows),
        "stored": len(rows),
        "verified": status_counts.get("verified", 0),
        "status_counts": status_counts,
        "failed": failed,
        "index_error": index_error,
        "symbols": [row.get("symbol") for row in universe_rows],
        "target_table": f"{DB_META}.{SOURCE_MAP_TABLE}",
    }


_DATE_PATTERN = re.compile(
    r"\b(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)"
    r"[a-z]*\.?\s+\d{1,2},?\s+\d{4}\b",
    re.IGNORECASE,
)
_PERCENT_PATTERN = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?\s*%")
_CURRENCY_PATTERN = re.compile(r"\$\s*[-+]?\d[\d,]*(?:\.\d+)?\s*[KMB]?", re.IGNORECASE)
_NUMBER_PATTERN = re.compile(r"[-+]?\d[\d,]*(?:\.\d+)?\s*[KMB]?", re.IGNORECASE)


def _normalize_symbols(symbols: str | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []
    raw_items = symbols.replace("\n", ",").split(",") if isinstance(symbols, str) else list(symbols)
    normalized: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        symbol = str(item).strip().upper()
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        normalized.append(symbol)
    return normalized


def _to_none(value: Any) -> Any:
    if value is None:
        return None
    try:
        if pd.isna(value):
            return None
    except Exception:
        pass
    if isinstance(value, pd.Timestamp):
        if pd.isna(value):
            return None
        return value.to_pydatetime()
    return value


def _date_string(value: Any) -> str | None:
    if value is None:
        return None
    ts = pd.to_datetime(value, errors="coerce")
    if pd.isna(ts):
        return None
    return pd.Timestamp(ts).strftime("%Y-%m-%d")


def _parse_provider_date(value: str | None) -> str | None:
    if not value:
        return None
    match = _DATE_PATTERN.search(str(value))
    if not match:
        return None
    raw = match.group(0).replace(".", "").replace("Sept", "Sep")
    for fmt in ("%b %d, %Y", "%b %d %Y", "%B %d, %Y", "%B %d %Y"):
        parsed = pd.to_datetime(raw, format=fmt, errors="coerce")
        if not pd.isna(parsed):
            return pd.Timestamp(parsed).strftime("%Y-%m-%d")
    parsed = pd.to_datetime(raw, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _fetch_official_html(url: str, *, timeout: int = OFFICIAL_REQUEST_TIMEOUT) -> str:
    request = Request(
        url,
        headers={
            "User-Agent": OFFICIAL_USER_AGENT,
            "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            charset = response.headers.get_content_charset() or "utf-8"
            return response.read().decode(charset, errors="replace")
    except HTTPError as exc:
        raise RuntimeError(f"official provider HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"official provider fetch failed: {exc.reason}") from exc


def _fetch_official_bytes(
    url: str,
    *,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    accept: str = "*/*",
) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": OFFICIAL_USER_AGENT,
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    try:
        with urlopen(request, timeout=timeout) as response:
            return response.read()
    except HTTPError as exc:
        raise RuntimeError(f"official provider HTTP {exc.code}") from exc
    except URLError as exc:
        raise RuntimeError(f"official provider fetch failed: {exc.reason}") from exc


def _fetch_official_json(url: str, *, timeout: int = OFFICIAL_REQUEST_TIMEOUT) -> dict[str, Any]:
    data = _fetch_official_bytes(url, timeout=timeout, accept="application/json,text/plain,*/*")
    try:
        parsed = json.loads(data.decode("utf-8"))
    except Exception as exc:
        raise RuntimeError("official provider returned invalid JSON") from exc
    if not isinstance(parsed, dict):
        raise RuntimeError("official provider returned non-object JSON")
    return parsed


def _html_to_lines(document: str) -> list[str]:
    text = re.sub(r"(?is)<(script|style).*?</\1>", " ", document)
    text = re.sub(r"(?is)<br\s*/?>", "\n", text)
    text = re.sub(r"(?is)</(p|div|li|tr|td|th|h[1-6]|span)>", "\n", text)
    text = re.sub(r"(?is)<[^>]+>", " ", text)
    text = html.unescape(text).replace("\ufeff", " ")
    lines = [re.sub(r"\s+", " ", line).strip() for line in text.splitlines()]
    return [line for line in lines if line]


def _find_line_index(lines: list[str], label: str, *, start: int = 0) -> int | None:
    lowered_label = label.lower()
    for idx in range(max(start, 0), len(lines)):
        if lowered_label in lines[idx].lower():
            return idx
    return None


def _joined_window(lines: list[str], idx: int | None, *, max_lines: int = 12) -> str:
    if idx is None:
        return ""
    return "\n".join(lines[idx : idx + max(max_lines, 1)])


def _parse_number_token(value: str | None, *, as_percent: bool = False) -> float | None:
    if not value:
        return None
    raw = str(value).strip()
    unit_match = re.search(r"([KMB])\s*%?$", raw, re.IGNORECASE)
    unit = unit_match.group(1).upper() if unit_match else None
    cleaned = re.sub(r"[$,%KMBkmb\s]", "", raw)
    if cleaned in {"", "+", "-"}:
        return None
    try:
        number = float(cleaned.replace(",", ""))
    except ValueError:
        return None
    if unit == "K":
        number *= 1_000
    elif unit == "M":
        number *= 1_000_000
    elif unit == "B":
        number *= 1_000_000_000
    if as_percent or "%" in raw:
        number /= 100.0
    return number


def _first_token_after_label(
    lines: list[str],
    label: str,
    pattern: re.Pattern[str],
    *,
    start: int = 0,
    max_lines: int = 12,
    as_percent: bool = False,
) -> float | None:
    idx = _find_line_index(lines, label, start=start)
    if idx is None:
        return None
    for offset, line in enumerate(lines[idx : idx + max(max_lines, 1)]):
        scan = line
        if offset == 0 and label.lower() in line.lower():
            scan = line[line.lower().find(label.lower()) + len(label) :]
        if scan.lower().startswith("as of"):
            continue
        match = pattern.search(scan)
        if match:
            return _parse_number_token(match.group(0), as_percent=as_percent)
    return None


def _date_after_label(lines: list[str], label: str, *, start: int = 0, max_lines: int = 8) -> str | None:
    idx = _find_line_index(lines, label, start=start)
    if idx is None:
        return None
    return _parse_provider_date(_joined_window(lines, idx, max_lines=max_lines))


def _text_after_label(lines: list[str], label: str, *, start: int = 0, max_lines: int = 4) -> str | None:
    idx = _find_line_index(lines, label, start=start)
    if idx is None:
        return None
    for line in lines[idx + 1 : idx + max(max_lines, 1)]:
        if line.lower().startswith("as of"):
            continue
        if _NUMBER_PATTERN.fullmatch(line):
            continue
        return line
    return None


def _ssga_metric_field(document: str, metric_key: str, field: str) -> str | None:
    unescaped = html.unescape(document)
    pattern = re.compile(
        rf'"{re.escape(metric_key)}"\s*:\s*\{{.*?"{re.escape(field)}"\s*:\s*"([^"]+)"',
        re.IGNORECASE | re.DOTALL,
    )
    match = pattern.search(unescaped)
    if not match:
        return None
    return html.unescape(match.group(1)).strip()


def _column_index(cell_ref: str) -> int:
    letters = re.sub(r"[^A-Z]", "", str(cell_ref).upper())
    value = 0
    for letter in letters:
        value = value * 26 + (ord(letter) - ord("A") + 1)
    return max(value - 1, 0)


def _xlsx_first_sheet_rows(data: bytes) -> list[list[str]]:
    ns = {"a": "http://schemas.openxmlformats.org/spreadsheetml/2006/main"}
    with ZipFile(io.BytesIO(data)) as workbook:
        shared_strings: list[str] = []
        if "xl/sharedStrings.xml" in workbook.namelist():
            shared_root = ET.fromstring(workbook.read("xl/sharedStrings.xml"))
            for item in shared_root.findall("a:si", ns):
                texts = [node.text or "" for node in item.findall(".//a:t", ns)]
                shared_strings.append("".join(texts))

        sheet_root = ET.fromstring(workbook.read("xl/worksheets/sheet1.xml"))
        rows: list[list[str]] = []
        for row_node in sheet_root.findall(".//a:row", ns):
            values: list[str] = []
            for cell_node in row_node.findall("a:c", ns):
                cell_idx = _column_index(cell_node.attrib.get("r", "A1"))
                while len(values) <= cell_idx:
                    values.append("")
                cell_type = cell_node.attrib.get("t")
                if cell_type == "inlineStr":
                    text = "".join(node.text or "" for node in cell_node.findall(".//a:t", ns))
                else:
                    value_node = cell_node.find("a:v", ns)
                    text = value_node.text if value_node is not None else ""
                    if cell_type == "s" and text:
                        text = shared_strings[int(text)]
                values[cell_idx] = str(text).strip()
            rows.append(values)
    return rows


def _clean_text(value: Any) -> str | None:
    if value is None:
        return None
    text = html.unescape(str(value)).replace("\xa0", " ").strip()
    if not text or text in {"-", "--", "—", "N/A", "n/a", "nan", "None"}:
        return None
    return re.sub(r"\s+", " ", text)


def _parse_float_value(value: Any) -> float | None:
    text = _clean_text(value)
    if text is None:
        return None
    try:
        return float(re.sub(r"[$,%\s,]", "", text))
    except ValueError:
        return None


def _parse_holdings_as_of(value: Any) -> str | None:
    text = _clean_text(value)
    if text is None:
        return None
    text = re.sub(r"^as of\s+", "", text, flags=re.IGNORECASE)
    parsed = pd.to_datetime(text, errors="coerce")
    if pd.isna(parsed):
        return _parse_provider_date(text)
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _holding_id_from_fields(row: dict[str, Any], row_number: int) -> str:
    for field in ("holding_id", "cusip", "isin", "identifier"):
        value = _clean_text(row.get(field))
        if value:
            return value.upper()
    symbol = _clean_text(row.get("holding_symbol"))
    name = _clean_text(row.get("holding_name"))
    maturity = _clean_text(row.get("maturity"))
    coupon = _clean_text(row.get("coupon"))
    parts = [part for part in (symbol, name, maturity, coupon) if part]
    if parts:
        return "|".join(parts).upper()[:255]
    return f"ROW_{row_number:06d}"


def _holding_missing_fields(row: dict[str, Any]) -> list[str]:
    checked_fields = ["holding_symbol", "sector", "asset_class", "country", "currency", "shares", "market_value"]
    return [field for field in checked_fields if row.get(field) is None]


def _holdings_coverage_status(rows: list[dict[str, Any]]) -> str:
    if not rows:
        return "missing"
    weight_sum = sum(float(row.get("weight_pct") or 0.0) for row in rows)
    if weight_sum >= 80:
        return "actual"
    return "partial"


def _apply_holdings_coverage(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    status = _holdings_coverage_status(rows)
    for row in rows:
        row["coverage_status"] = status
        row["missing_fields_json"] = json.dumps(_holding_missing_fields(row), ensure_ascii=False)
    return rows


def _is_missing_table_error(exc: Exception, table_name: str) -> bool:
    message = str(exc).lower()
    return table_name.lower() in message and ("doesn't exist" in message or "unknown table" in message)


def ensure_etf_operability_snapshot_schema(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    """Create or sync the ETF operability snapshot table in finance_meta."""
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["etf_operability_snapshot"])
        sync_table_schema(
            db,
            OPERABILITY_TABLE,
            PROVIDER_SCHEMAS["etf_operability_snapshot"],
            DB_META,
        )
    finally:
        db.close()


def ensure_etf_holdings_snapshot_schema(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    """Create or sync ETF holdings and exposure snapshot tables in finance_meta."""
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        for key, table_name in (
            ("etf_holdings_snapshot", HOLDINGS_TABLE),
            ("etf_exposure_snapshot", EXPOSURE_TABLE),
        ):
            db.execute(PROVIDER_SCHEMAS[key])
            sync_table_schema(
                db,
                table_name,
                PROVIDER_SCHEMAS[key],
                DB_META,
            )
    finally:
        db.close()


def _load_asset_profile_rows(db: MySQLClient, symbols: list[str]) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    db.use_db(DB_META)
    try:
        rows = db.query(
            f"""
            SELECT
                symbol,
                kind,
                quote_type,
                fund_family,
                total_assets,
                bid,
                ask,
                status,
                last_collected_at,
                error_msg
            FROM nyse_asset_profile
            WHERE symbol IN ({placeholders})
            """,
            symbols,
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "nyse_asset_profile"):
            return {}
        raise
    return {str(row.get("symbol") or "").upper(): row for row in rows if row.get("symbol")}


def _load_latest_price_dates(
    db: MySQLClient,
    symbols: list[str],
    *,
    as_of_date: str | None,
    timeframe: str,
) -> dict[str, pd.Timestamp]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    where = [f"symbol IN ({placeholders})", "timeframe = %s"]
    params: list[Any] = list(symbols) + [timeframe]
    if as_of_date is not None:
        where.append("`date` <= %s")
        params.append(as_of_date)

    db.use_db(DB_PRICE)
    try:
        rows = db.query(
            f"""
            SELECT symbol, MAX(`date`) AS latest_date
            FROM nyse_price_history
            WHERE {" AND ".join(where)}
            GROUP BY symbol
            """,
            params,
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "nyse_price_history"):
            return {}
        raise
    out: dict[str, pd.Timestamp] = {}
    for row in rows:
        latest = pd.to_datetime(row.get("latest_date"), errors="coerce")
        if pd.isna(latest):
            continue
        out[str(row.get("symbol") or "").upper()] = pd.Timestamp(latest).normalize()
    return out


def _load_price_metric_rows(
    db: MySQLClient,
    symbols: list[str],
    *,
    latest_dates: dict[str, pd.Timestamp],
    lookback_days: int,
    timeframe: str,
) -> dict[str, dict[str, Any]]:
    if not symbols or not latest_dates:
        return {}

    latest_values = [value for value in latest_dates.values() if value is not None]
    if not latest_values:
        return {}

    query_start = min(latest_values) - pd.Timedelta(days=max(int(lookback_days) * 3, 90))
    query_end = max(latest_values)
    placeholders = ",".join(["%s"] * len(symbols))

    db.use_db(DB_PRICE)
    try:
        rows = db.query(
            f"""
            SELECT symbol, `date`, close, adj_close, volume
            FROM nyse_price_history
            WHERE symbol IN ({placeholders})
              AND timeframe = %s
              AND `date` >= %s
              AND `date` <= %s
            ORDER BY symbol ASC, `date` ASC
            """,
            list(symbols) + [timeframe, query_start.strftime("%Y-%m-%d"), query_end.strftime("%Y-%m-%d")],
        )
    except Exception as exc:
        if _is_missing_table_error(exc, "nyse_price_history"):
            return {}
        raise
    frame = pd.DataFrame(rows)
    if frame.empty:
        return {}

    frame["symbol"] = frame["symbol"].astype(str).str.upper()
    frame["date"] = pd.to_datetime(frame["date"], errors="coerce")
    frame["close"] = pd.to_numeric(frame["close"], errors="coerce")
    frame["adj_close"] = pd.to_numeric(frame.get("adj_close"), errors="coerce")
    frame["volume"] = pd.to_numeric(frame["volume"], errors="coerce")
    frame = frame.dropna(subset=["symbol", "date"]).sort_values(["symbol", "date"])

    out: dict[str, dict[str, Any]] = {}
    for symbol, group in frame.groupby("symbol", sort=False):
        latest_date = latest_dates.get(str(symbol).upper())
        if latest_date is None:
            continue
        symbol_frame = group[group["date"] <= latest_date].tail(max(int(lookback_days), 1)).copy()
        if symbol_frame.empty:
            continue
        close_series = symbol_frame["close"].dropna()
        latest_close = float(close_series.iloc[-1]) if not close_series.empty else None
        volume_series = symbol_frame["volume"].dropna()
        avg_volume = float(volume_series.mean()) if not volume_series.empty else None
        dollar_volume = (symbol_frame["close"] * symbol_frame["volume"]).dropna()
        avg_dollar_volume = float(dollar_volume.mean()) if not dollar_volume.empty else None
        out[str(symbol).upper()] = {
            "latest_date": latest_date.strftime("%Y-%m-%d"),
            "market_price": latest_close,
            "avg_daily_volume": avg_volume,
            "avg_daily_dollar_volume": avg_dollar_volume,
        }
    return out


def _bid_ask_spread_pct(bid: Any, ask: Any) -> float | None:
    bid_value = pd.to_numeric(pd.Series([bid]), errors="coerce").iloc[0]
    ask_value = pd.to_numeric(pd.Series([ask]), errors="coerce").iloc[0]
    if pd.isna(bid_value) or pd.isna(ask_value) or bid_value <= 0 or ask_value <= 0:
        return None
    mid = (float(bid_value) + float(ask_value)) / 2.0
    if mid <= 0:
        return None
    return abs(float(ask_value) - float(bid_value)) / mid


def _missing_fields(row: dict[str, Any]) -> list[str]:
    required_proxy_fields = [
        "market_price",
        "avg_daily_dollar_volume",
        "total_assets",
        "bid_ask_spread_pct",
    ]
    missing = [field for field in required_proxy_fields if row.get(field) is None]
    provider_only_fields = [
        "expense_ratio",
        "nav",
        "premium_discount_pct",
        "median_bid_ask_spread_pct",
        "official_leverage_inverse_metadata",
    ]
    missing.extend(provider_only_fields)
    return missing


def _coverage_status(row: dict[str, Any]) -> str:
    has_profile_bridge = any(row.get(field) is not None for field in ("total_assets", "bid", "ask", "bid_ask_spread_pct"))
    has_price_proxy = any(row.get(field) is not None for field in ("market_price", "avg_daily_volume", "avg_daily_dollar_volume"))
    if has_profile_bridge:
        return "bridge"
    if has_price_proxy:
        return "proxy"
    return "missing"


def _source_type_for_status(status: str) -> str:
    if status == "proxy":
        return "computed_proxy"
    return "database_bridge"


def _official_missing_fields(row: dict[str, Any]) -> list[str]:
    core_fields = [
        "expense_ratio",
        "net_assets",
        "nav",
        "market_price",
        "premium_discount_pct",
        "median_bid_ask_spread_pct",
        "avg_daily_volume",
        "inception_date",
        "leverage_factor",
        "is_inverse",
        "has_daily_objective",
    ]
    return [field for field in core_fields if row.get(field) is None]


def _official_coverage_status(row: dict[str, Any]) -> str:
    groups = [
        row.get("expense_ratio") is not None,
        row.get("net_assets") is not None or row.get("total_assets") is not None,
        row.get("avg_daily_volume") is not None or row.get("avg_daily_dollar_volume") is not None,
        row.get("bid_ask_spread_pct") is not None or row.get("median_bid_ask_spread_pct") is not None,
        row.get("nav") is not None or row.get("market_price") is not None or row.get("premium_discount_pct") is not None,
    ]
    present_count = sum(1 for item in groups if item)
    if present_count >= 3:
        return "actual"
    if present_count > 0:
        return "partial"
    return "missing"


def _official_row_base(
    symbol: str,
    source_info: dict[str, Any] | None,
    *,
    as_of_date: str | None,
    collected_at: str,
    coverage_status: str = "missing",
    error_msg: str | None = None,
) -> dict[str, Any]:
    source_info = source_info or {}
    return {
        "symbol": symbol,
        "as_of_date": as_of_date or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
        "source": source_info.get("source") or "official_provider",
        "source_type": "official",
        "source_ref": source_info.get("url"),
        "fund_family": source_info.get("fund_family"),
        "category": None,
        "expense_ratio": None,
        "turnover_ratio": None,
        "total_assets": None,
        "net_assets": None,
        "nav": None,
        "market_price": None,
        "premium_discount_pct": None,
        "bid": None,
        "ask": None,
        "bid_ask_spread_pct": None,
        "median_bid_ask_spread_pct": None,
        "avg_daily_volume": None,
        "avg_daily_dollar_volume": None,
        "lookback_days": None,
        "inception_date": None,
        "leverage_factor": source_info.get("leverage_factor"),
        "is_inverse": source_info.get("is_inverse"),
        "has_daily_objective": source_info.get("has_daily_objective"),
        "coverage_status": coverage_status,
        "missing_fields_json": None,
        "collected_at": collected_at,
        "error_msg": error_msg,
    }


def _finalize_official_row(row: dict[str, Any]) -> dict[str, Any]:
    row["coverage_status"] = _official_coverage_status(row)
    missing = _official_missing_fields(row)
    row["missing_fields_json"] = json.dumps(missing, ensure_ascii=False)
    if row["coverage_status"] == "missing" and not row.get("error_msg"):
        row["error_msg"] = "official provider returned no usable operability fields"
    return row


def _parse_ishares_operability(
    symbol: str,
    source_info: dict[str, Any],
    document: str,
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> dict[str, Any]:
    lines = _html_to_lines(document)
    row = _official_row_base(symbol, source_info, as_of_date=as_of_fallback, collected_at=collected_at)

    nav_date = _date_after_label(lines, "NAV as of", max_lines=2)
    facts_date = _date_after_label(lines, "Net Assets of Fund", max_lines=5)
    row["as_of_date"] = facts_date or nav_date or row["as_of_date"]
    row["expense_ratio"] = _first_token_after_label(lines, "Net Expense Ratio", _PERCENT_PATTERN, max_lines=3, as_percent=True)
    if row["expense_ratio"] is None:
        row["expense_ratio"] = _first_token_after_label(lines, "Expense Ratio", _PERCENT_PATTERN, max_lines=3, as_percent=True)
    row["net_assets"] = _first_token_after_label(lines, "Net Assets of Fund", _CURRENCY_PATTERN, max_lines=5)
    row["total_assets"] = row["net_assets"]
    row["nav"] = _first_token_after_label(lines, "NAV as of", _CURRENCY_PATTERN, max_lines=3)
    row["market_price"] = _first_token_after_label(lines, "Closing Price", _NUMBER_PATTERN, max_lines=4)
    row["premium_discount_pct"] = _first_token_after_label(
        lines,
        "Premium/Discount",
        _NUMBER_PATTERN,
        start=_find_line_index(lines, "Net Assets of Fund") or 0,
        max_lines=5,
        as_percent=True,
    )
    row["median_bid_ask_spread_pct"] = _first_token_after_label(
        lines,
        "30 Day Median Bid/Ask Spread",
        _PERCENT_PATTERN,
        max_lines=5,
        as_percent=True,
    )
    row["avg_daily_volume"] = _first_token_after_label(lines, "30 Day Avg. Volume", _NUMBER_PATTERN, max_lines=5)
    if row["avg_daily_volume"] is not None and row["market_price"] is not None:
        row["avg_daily_dollar_volume"] = float(row["avg_daily_volume"]) * float(row["market_price"])
    row["lookback_days"] = 30 if row["avg_daily_volume"] is not None else None
    row["inception_date"] = _date_after_label(lines, "Fund Inception", max_lines=3)
    facts_idx = _find_line_index(lines, "Net Assets of Fund") or 0
    row["category"] = _text_after_label(lines, "Asset Class", start=facts_idx, max_lines=3)
    return _finalize_official_row(row)


def _parse_ssga_operability(
    symbol: str,
    source_info: dict[str, Any],
    document: str,
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> dict[str, Any]:
    lines = _html_to_lines(document)
    row = _official_row_base(symbol, source_info, as_of_date=as_of_fallback, collected_at=collected_at)

    nav_date = _date_after_label(lines, "Fund Net Asset Value", max_lines=8)
    aum_date = _date_after_label(lines, "Assets Under Management", max_lines=5)
    row["as_of_date"] = nav_date or aum_date or row["as_of_date"]
    row["expense_ratio"] = _parse_number_token(
        _ssga_metric_field(document, "gross-expense-ratio", "originalValue"),
        as_percent=True,
    )
    if row["expense_ratio"] is None:
        row["expense_ratio"] = _first_token_after_label(lines, "Gross Expense Ratio", _PERCENT_PATTERN, max_lines=8, as_percent=True)
    row["net_assets"] = _parse_number_token(_ssga_metric_field(document, "aum", "originalValue"))
    if row["net_assets"] is None:
        row["net_assets"] = _first_token_after_label(lines, "Assets Under Management", _CURRENCY_PATTERN, max_lines=5)
    row["total_assets"] = row["net_assets"]

    nav_idx = _find_line_index(lines, "Fund Net Asset Value")
    row["nav"] = _parse_number_token(_ssga_metric_field(document, "nav", "originalValue"))
    if row["nav"] is None:
        row["nav"] = _first_token_after_label(lines, "NAV", _CURRENCY_PATTERN, start=nav_idx or 0, max_lines=10)
    row["market_price"] = _first_token_after_label(lines, "Closing Price", _CURRENCY_PATTERN, max_lines=12)
    row["premium_discount_pct"] = _first_token_after_label(
        lines,
        "Premium/Discount",
        _PERCENT_PATTERN,
        max_lines=12,
        as_percent=True,
    )
    row["median_bid_ask_spread_pct"] = _first_token_after_label(
        lines,
        "30-Day Median Bid/Ask Spread",
        _PERCENT_PATTERN,
        max_lines=12,
        as_percent=True,
    )
    row["avg_daily_volume"] = _first_token_after_label(lines, "Exchange Volume (Shares)", _NUMBER_PATTERN, max_lines=8)
    if row["avg_daily_volume"] is not None and row["market_price"] is not None:
        row["avg_daily_dollar_volume"] = float(row["avg_daily_volume"]) * float(row["market_price"])
    row["lookback_days"] = 1 if row["avg_daily_volume"] is not None else None
    row["inception_date"] = _date_after_label(lines, "Inception Date", max_lines=3) or _date_after_label(
        lines, "Fund Inception Date", max_lines=3
    )
    return _finalize_official_row(row)


def _parse_invesco_operability(
    symbol: str,
    source_info: dict[str, Any],
    document: str,
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> dict[str, Any]:
    lines = _html_to_lines(document)
    row = _official_row_base(symbol, source_info, as_of_date=as_of_fallback, collected_at=collected_at)
    joined = "\n".join(lines)
    expense_match = re.search(r"expense ratio is\s+([-+]?\d[\d,]*(?:\.\d+)?\s*%)", joined, re.IGNORECASE)
    if expense_match:
        row["expense_ratio"] = _parse_number_token(expense_match.group(1), as_percent=True)
    inception_match = re.search(
        r"inception date of\s+("
        r"(?:Jan|Feb|Mar|Apr|May|Jun|Jul|Aug|Sep|Sept|Oct|Nov|Dec)[a-z]*\.?\s+\d{1,2},?\s+\d{4}"
        r")",
        joined,
        re.IGNORECASE,
    )
    row["inception_date"] = _parse_provider_date(inception_match.group(1) if inception_match else None)
    return _finalize_official_row(row)


def _build_official_rows(
    symbols: list[str],
    *,
    as_of_date: str | None,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    only_source: str | None = None,
) -> list[dict[str, Any]]:
    collected_at = _utc_now_string()
    rows: list[dict[str, Any]] = []
    parsers = {
        "ishares": _parse_ishares_operability,
        "ssga": _parse_ssga_operability,
        "invesco": _parse_invesco_operability,
    }
    source_map = _source_map_info_by_symbol(symbols, data_kind="operability", only_source=only_source)

    for symbol in symbols:
        source_info = source_map.get(symbol) or OFFICIAL_PROVIDER_SOURCES.get(symbol)
        if not source_info or (only_source is not None and source_info.get("source") != only_source):
            row = _official_row_base(
                symbol,
                {"source": only_source} if only_source is not None else None,
                as_of_date=as_of_date,
                collected_at=collected_at,
                coverage_status="missing",
                error_msg="no official operability provider source mapped",
            )
            row["missing_fields_json"] = json.dumps(_official_missing_fields(row), ensure_ascii=False)
            rows.append(row)
            continue

        try:
            document = _fetch_official_html(str(source_info["url"]), timeout=timeout)
            parser = parsers[str(source_info["parser"])]
            rows.append(
                parser(
                    symbol,
                    source_info,
                    document,
                    as_of_fallback=as_of_date,
                    collected_at=collected_at,
                )
            )
        except Exception as exc:
            row = _official_row_base(
                symbol,
                source_info,
                as_of_date=as_of_date,
                collected_at=collected_at,
                coverage_status="error",
                error_msg=str(exc)[:500],
            )
            row["missing_fields_json"] = json.dumps(_official_missing_fields(row), ensure_ascii=False)
            rows.append(row)

    return rows


def fetch_official_etf_operability_rows(
    symbols: str | Iterable[str],
    *,
    as_of_date: str | None = None,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
) -> list[dict[str, Any]]:
    """Fetch normalized ETF operability snapshots from mapped official issuer pages."""
    normalized_symbols = _normalize_symbols(symbols)
    as_of = _date_string(as_of_date) if as_of_date is not None else None
    return _build_official_rows(normalized_symbols, as_of_date=as_of, timeout=int(timeout))


def _holdings_row_base(
    fund_symbol: str,
    source_info: dict[str, Any],
    *,
    as_of_date: str,
    collected_at: str,
) -> dict[str, Any]:
    return {
        "fund_symbol": fund_symbol,
        "as_of_date": as_of_date,
        "source": source_info.get("source"),
        "source_type": "official",
        "source_ref": source_info.get("url"),
        "holding_id": None,
        "holding_symbol": None,
        "holding_name": None,
        "holding_type": None,
        "weight_pct": None,
        "shares": None,
        "market_value": None,
        "sector": None,
        "asset_class": source_info.get("asset_class"),
        "country": None,
        "currency": None,
        "coverage_status": "missing",
        "missing_fields_json": None,
        "collected_at": collected_at,
        "error_msg": None,
    }


def _parse_ishares_holdings_csv(
    fund_symbol: str,
    source_info: dict[str, Any],
    data: bytes,
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> list[dict[str, Any]]:
    text = data.decode("utf-8-sig", errors="replace")
    csv_rows = list(csv.reader(io.StringIO(text)))
    as_of = as_of_fallback
    header_idx: int | None = None
    for idx, raw_row in enumerate(csv_rows):
        row = [_clean_text(item) or "" for item in raw_row]
        if row and row[0].lower().startswith("fund holdings as of") and len(row) > 1:
            as_of = _parse_holdings_as_of(row[1]) or as_of
        if {"Name", "Weight (%)"}.issubset(set(row)):
            header_idx = idx
            break
    if header_idx is None:
        raise RuntimeError("iShares holdings CSV header not found")

    headers = [_clean_text(item) or "" for item in csv_rows[header_idx]]
    rows: list[dict[str, Any]] = []
    for row_number, raw_values in enumerate(csv_rows[header_idx + 1 :], start=1):
        if not raw_values or not any(_clean_text(value) for value in raw_values):
            break
        if "Name" in raw_values and "Weight (%)" in raw_values:
            break
        record = {headers[idx]: raw_values[idx] if idx < len(raw_values) else None for idx in range(len(headers))}
        weight = _parse_float_value(record.get("Weight (%)"))
        name = _clean_text(record.get("Name"))
        if weight is None or name is None:
            continue
        row = _holdings_row_base(
            fund_symbol,
            source_info,
            as_of_date=as_of or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
            collected_at=collected_at,
        )
        row.update(
            {
                "holding_symbol": _clean_text(record.get("Ticker")),
                "holding_name": name,
                "holding_type": _clean_text(record.get("Security Type")) or _clean_text(record.get("Asset Class")),
                "weight_pct": weight,
                "shares": _parse_float_value(record.get("Quantity") or record.get("Shares") or record.get("Par Value")),
                "market_value": _parse_float_value(record.get("Market Value")),
                "sector": _clean_text(record.get("Sector")),
                "asset_class": _clean_text(record.get("Asset Class")) or source_info.get("asset_class"),
                "country": _clean_text(record.get("Location")),
                "currency": _clean_text(record.get("Currency")),
            }
        )
        row["holding_id"] = _holding_id_from_fields(
            {
                "holding_id": record.get("CUSIP") or record.get("ISIN") or record.get("SEDOL"),
                "holding_symbol": row["holding_symbol"],
                "holding_name": row["holding_name"],
                "maturity": record.get("Maturity"),
                "coupon": record.get("Coupon (%)"),
            },
            row_number,
        )
        rows.append(row)
    return _apply_holdings_coverage(rows)


def _parse_ssga_holdings_xlsx(
    fund_symbol: str,
    source_info: dict[str, Any],
    data: bytes,
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> list[dict[str, Any]]:
    sheet_rows = _xlsx_first_sheet_rows(data)
    as_of = as_of_fallback
    header_idx: int | None = None
    for idx, raw_row in enumerate(sheet_rows):
        row = [_clean_text(item) or "" for item in raw_row]
        if row and row[0].lower().startswith("holdings") and len(row) > 1:
            as_of = _parse_holdings_as_of(row[1]) or as_of
        if "Name" in row and "Weight" in row:
            header_idx = idx
            break
    if header_idx is None:
        raise RuntimeError("SSGA holdings XLSX header not found")

    headers = [_clean_text(item) or "" for item in sheet_rows[header_idx]]
    rows: list[dict[str, Any]] = []
    for row_number, raw_values in enumerate(sheet_rows[header_idx + 1 :], start=1):
        if not raw_values or not any(_clean_text(value) for value in raw_values):
            continue
        record = {headers[idx]: raw_values[idx] if idx < len(raw_values) else None for idx in range(len(headers))}
        weight = _parse_float_value(record.get("Weight"))
        name = _clean_text(record.get("Name"))
        if weight is None or name is None:
            continue
        row = _holdings_row_base(
            fund_symbol,
            source_info,
            as_of_date=as_of or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
            collected_at=collected_at,
        )
        row.update(
            {
                "holding_symbol": _clean_text(record.get("Ticker")),
                "holding_name": name,
                "holding_type": _clean_text(record.get("Security Type")) or source_info.get("asset_class"),
                "weight_pct": weight,
                "shares": _parse_float_value(record.get("Shares Held") or record.get("Par Value")),
                "market_value": _parse_float_value(record.get("Market Value")),
                "sector": _clean_text(record.get("Sector")),
                "asset_class": source_info.get("asset_class"),
                "currency": _clean_text(record.get("Local Currency")),
            }
        )
        row["holding_id"] = _holding_id_from_fields(
            {
                "identifier": record.get("Identifier") or record.get("SEDOL"),
                "holding_symbol": row["holding_symbol"],
                "holding_name": row["holding_name"],
                "maturity": record.get("Maturity"),
                "coupon": record.get("Coupon"),
            },
            row_number,
        )
        rows.append(row)
    return _apply_holdings_coverage(rows)


def _parse_invesco_holdings_json(
    fund_symbol: str,
    source_info: dict[str, Any],
    payload: dict[str, Any],
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> list[dict[str, Any]]:
    as_of = _date_string(payload.get("effectiveBusinessDate")) or _date_string(payload.get("effectiveDate")) or as_of_fallback
    holdings = payload.get("holdings")
    if not isinstance(holdings, list):
        raise RuntimeError("Invesco holdings payload has no holdings list")

    rows: list[dict[str, Any]] = []
    for row_number, item in enumerate(holdings, start=1):
        if not isinstance(item, dict):
            continue
        weight = _parse_float_value(item.get("percentageOfTotalNetAssets"))
        name = _clean_text(item.get("issuerName"))
        if weight is None or name is None:
            continue
        security_type = _clean_text(item.get("securityTypeName"))
        row = _holdings_row_base(
            fund_symbol,
            source_info,
            as_of_date=as_of or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
            collected_at=collected_at,
        )
        row.update(
            {
                "holding_symbol": _clean_text(item.get("ticker")),
                "holding_name": name,
                "holding_type": security_type,
                "weight_pct": weight,
                "shares": _parse_float_value(item.get("units")),
                "asset_class": "Equity" if security_type and "stock" in security_type.lower() else source_info.get("asset_class"),
                "currency": _clean_text(item.get("currency")),
            }
        )
        row["holding_id"] = _holding_id_from_fields(
            {
                "cusip": item.get("cusip"),
                "holding_symbol": row["holding_symbol"],
                "holding_name": row["holding_name"],
            },
            row_number,
        )
        rows.append(row)
    return _apply_holdings_coverage(rows)


def _build_commodity_gold_holdings_rows(
    fund_symbol: str,
    source_info: dict[str, Any],
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> list[dict[str, Any]]:
    row = _holdings_row_base(
        fund_symbol,
        source_info,
        as_of_date=as_of_fallback or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
        collected_at=collected_at,
    )
    row.update(
        {
            "holding_id": "gold_bullion",
            "holding_symbol": "GOLD",
            "holding_name": source_info.get("holding_name") or "Gold Bullion",
            "holding_type": "Commodity",
            "weight_pct": 100.0,
            "asset_class": "Gold",
            "currency": "USD",
            "coverage_status": "actual",
            "missing_fields_json": json.dumps([], ensure_ascii=False),
        }
    )
    return [row]


def _build_official_holdings_rows(
    symbols: list[str],
    *,
    as_of_date: str | None,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    only_source: str | None = None,
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, str]]]:
    collected_at = _utc_now_string()
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    failed: list[dict[str, str]] = []
    source_map = _source_map_info_by_symbol(symbols, data_kind="holdings", only_source=only_source)

    for symbol in symbols:
        source_info = source_map.get(symbol) or HOLDINGS_PROVIDER_SOURCES.get(symbol)
        if not source_info or (only_source is not None and source_info.get("source") != only_source):
            missing.append(symbol)
            continue
        parser = str(source_info.get("parser") or "")
        if parser == "pending":
            missing.append(symbol)
            failed.append({"symbol": symbol, "reason": "official row-level holdings source pending"})
            continue
        try:
            if parser == "ishares_csv":
                data = _fetch_official_bytes(str(source_info["url"]), timeout=timeout, accept="text/csv,*/*")
                rows.extend(
                    _parse_ishares_holdings_csv(
                        symbol,
                        source_info,
                        data,
                        as_of_fallback=as_of_date,
                        collected_at=collected_at,
                    )
                )
            elif parser == "ssga_xlsx":
                data = _fetch_official_bytes(
                    str(source_info["url"]),
                    timeout=timeout,
                    accept="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet,*/*",
                )
                rows.extend(
                    _parse_ssga_holdings_xlsx(
                        symbol,
                        source_info,
                        data,
                        as_of_fallback=as_of_date,
                        collected_at=collected_at,
                    )
                )
            elif parser == "invesco_json":
                payload = _fetch_official_json(str(source_info["url"]), timeout=timeout)
                rows.extend(
                    _parse_invesco_holdings_json(
                        symbol,
                        source_info,
                        payload,
                        as_of_fallback=as_of_date,
                        collected_at=collected_at,
                    )
                )
            elif parser == "commodity_gold":
                rows.extend(
                    _build_commodity_gold_holdings_rows(
                        symbol,
                        source_info,
                        as_of_fallback=as_of_date,
                        collected_at=collected_at,
                    )
                )
            else:
                missing.append(symbol)
                failed.append({"symbol": symbol, "reason": f"unsupported holdings parser: {parser}"})
        except Exception as exc:
            failed.append({"symbol": symbol, "reason": str(exc)[:500]})

    found_symbols = {str(row.get("fund_symbol") or "").upper() for row in rows}
    for symbol in symbols:
        if symbol not in found_symbols and symbol not in missing and not any(item["symbol"] == symbol for item in failed):
            missing.append(symbol)
    return rows, missing, failed


def fetch_official_etf_holdings_rows(
    symbols: str | Iterable[str],
    *,
    as_of_date: str | None = None,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
) -> list[dict[str, Any]]:
    """Fetch normalized ETF holdings rows from mapped official issuer downloads."""
    normalized_symbols = _normalize_symbols(symbols)
    as_of = _date_string(as_of_date) if as_of_date is not None else None
    rows, _, _ = _build_official_holdings_rows(normalized_symbols, as_of_date=as_of, timeout=int(timeout))
    return rows


def _build_db_bridge_rows(
    symbols: list[str],
    *,
    as_of_date: str | None,
    lookback_days: int,
    profile_rows: dict[str, dict[str, Any]],
    price_rows: dict[str, dict[str, Any]],
) -> list[dict[str, Any]]:
    collected_at = _utc_now_string()
    rows: list[dict[str, Any]] = []
    today = pd.Timestamp.utcnow().strftime("%Y-%m-%d")

    for symbol in symbols:
        profile = profile_rows.get(symbol) or {}
        price = price_rows.get(symbol) or {}
        bid = _to_none(profile.get("bid"))
        ask = _to_none(profile.get("ask"))
        row_as_of = as_of_date or price.get("latest_date") or _date_string(profile.get("last_collected_at")) or today
        source_refs: list[str] = []
        if price:
            source_refs.append("finance_price.nyse_price_history")
        if profile:
            source_refs.append("finance_meta.nyse_asset_profile")

        row = {
            "symbol": symbol,
            "as_of_date": row_as_of,
            "source": "db_bridge",
            "source_type": "database_bridge",
            "source_ref": "+".join(source_refs) if source_refs else None,
            "fund_family": _to_none(profile.get("fund_family")),
            "category": None,
            "expense_ratio": None,
            "turnover_ratio": None,
            "total_assets": _to_none(profile.get("total_assets")),
            "net_assets": None,
            "nav": None,
            "market_price": _to_none(price.get("market_price")),
            "premium_discount_pct": None,
            "bid": bid,
            "ask": ask,
            "bid_ask_spread_pct": _bid_ask_spread_pct(bid, ask),
            "median_bid_ask_spread_pct": None,
            "avg_daily_volume": _to_none(price.get("avg_daily_volume")),
            "avg_daily_dollar_volume": _to_none(price.get("avg_daily_dollar_volume")),
            "lookback_days": int(lookback_days),
            "inception_date": None,
            "leverage_factor": None,
            "is_inverse": None,
            "has_daily_objective": None,
            "coverage_status": "missing",
            "missing_fields_json": None,
            "collected_at": collected_at,
            "error_msg": None,
        }
        status = _coverage_status(row)
        row["coverage_status"] = status
        row["source_type"] = _source_type_for_status(status)
        row["missing_fields_json"] = json.dumps(_missing_fields(row), ensure_ascii=False)
        if status == "missing":
            row["error_msg"] = "no price/profile bridge data"
        rows.append(row)

    return rows


def _upsert_etf_operability_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    sql = f"""
    INSERT INTO {OPERABILITY_TABLE} (
      symbol, as_of_date, source, source_type, source_ref,
      fund_family, category,
      expense_ratio, turnover_ratio, total_assets, net_assets, nav, market_price, premium_discount_pct,
      bid, ask, bid_ask_spread_pct, median_bid_ask_spread_pct,
      avg_daily_volume, avg_daily_dollar_volume, lookback_days,
      inception_date, leverage_factor, is_inverse, has_daily_objective,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(symbol)s, %(as_of_date)s, %(source)s, %(source_type)s, %(source_ref)s,
      %(fund_family)s, %(category)s,
      %(expense_ratio)s, %(turnover_ratio)s, %(total_assets)s, %(net_assets)s, %(nav)s, %(market_price)s, %(premium_discount_pct)s,
      %(bid)s, %(ask)s, %(bid_ask_spread_pct)s, %(median_bid_ask_spread_pct)s,
      %(avg_daily_volume)s, %(avg_daily_dollar_volume)s, %(lookback_days)s,
      %(inception_date)s, %(leverage_factor)s, %(is_inverse)s, %(has_daily_objective)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_type = VALUES(source_type),
      source_ref = VALUES(source_ref),
      fund_family = VALUES(fund_family),
      category = VALUES(category),
      expense_ratio = VALUES(expense_ratio),
      turnover_ratio = VALUES(turnover_ratio),
      total_assets = VALUES(total_assets),
      net_assets = VALUES(net_assets),
      nav = VALUES(nav),
      market_price = VALUES(market_price),
      premium_discount_pct = VALUES(premium_discount_pct),
      bid = VALUES(bid),
      ask = VALUES(ask),
      bid_ask_spread_pct = VALUES(bid_ask_spread_pct),
      median_bid_ask_spread_pct = VALUES(median_bid_ask_spread_pct),
      avg_daily_volume = VALUES(avg_daily_volume),
      avg_daily_dollar_volume = VALUES(avg_daily_dollar_volume),
      lookback_days = VALUES(lookback_days),
      inception_date = VALUES(inception_date),
      leverage_factor = VALUES(leverage_factor),
      is_inverse = VALUES(is_inverse),
      has_daily_objective = VALUES(has_daily_objective),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


def _delete_snapshot_scope(
    db: MySQLClient,
    table_name: str,
    *,
    key_symbol_column: str,
    scope_rows: list[dict[str, Any]],
) -> None:
    scopes = {
        (
            str(row.get(key_symbol_column) or "").upper(),
            str(row.get("as_of_date") or ""),
            str(row.get("source") or ""),
        )
        for row in scope_rows
        if row.get(key_symbol_column) and row.get("as_of_date") and row.get("source")
    }
    for symbol, as_of_date, source in sorted(scopes):
        db.execute(
            f"""
            DELETE FROM {table_name}
            WHERE {key_symbol_column} = %s
              AND as_of_date = %s
              AND source = %s
            """,
            (symbol, as_of_date, source),
        )


def _upsert_etf_holdings_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    sql = f"""
    INSERT INTO {HOLDINGS_TABLE} (
      fund_symbol, as_of_date, source, source_type, source_ref,
      holding_id, holding_symbol, holding_name, holding_type,
      weight_pct, shares, market_value,
      sector, asset_class, country, currency,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(fund_symbol)s, %(as_of_date)s, %(source)s, %(source_type)s, %(source_ref)s,
      %(holding_id)s, %(holding_symbol)s, %(holding_name)s, %(holding_type)s,
      %(weight_pct)s, %(shares)s, %(market_value)s,
      %(sector)s, %(asset_class)s, %(country)s, %(currency)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_type = VALUES(source_type),
      source_ref = VALUES(source_ref),
      holding_symbol = VALUES(holding_symbol),
      holding_name = VALUES(holding_name),
      holding_type = VALUES(holding_type),
      weight_pct = VALUES(weight_pct),
      shares = VALUES(shares),
      market_value = VALUES(market_value),
      sector = VALUES(sector),
      asset_class = VALUES(asset_class),
      country = VALUES(country),
      currency = VALUES(currency),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


def _upsert_etf_exposure_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return

    sql = f"""
    INSERT INTO {EXPOSURE_TABLE} (
      fund_symbol, as_of_date, source, source_type, source_ref, derived_from,
      exposure_type, exposure_name, weight_pct,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(fund_symbol)s, %(as_of_date)s, %(source)s, %(source_type)s, %(source_ref)s, %(derived_from)s,
      %(exposure_type)s, %(exposure_name)s, %(weight_pct)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_type = VALUES(source_type),
      source_ref = VALUES(source_ref),
      derived_from = VALUES(derived_from),
      weight_pct = VALUES(weight_pct),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


def _exposure_row(
    *,
    fund_symbol: str,
    as_of_date: str,
    source: str,
    source_type: str,
    source_ref: str | None,
    derived_from: str,
    exposure_type: str,
    exposure_name: str,
    weight_pct: float | None,
    coverage_status: str,
    collected_at: str,
    error_msg: str | None = None,
) -> dict[str, Any]:
    missing = []
    if weight_pct is None:
        missing.append("weight_pct")
    return {
        "fund_symbol": fund_symbol,
        "as_of_date": as_of_date,
        "source": source,
        "source_type": source_type,
        "source_ref": source_ref,
        "derived_from": derived_from,
        "exposure_type": exposure_type,
        "exposure_name": exposure_name,
        "weight_pct": weight_pct,
        "coverage_status": coverage_status,
        "missing_fields_json": json.dumps(missing, ensure_ascii=False),
        "collected_at": collected_at,
        "error_msg": error_msg,
    }


def _aggregate_exposure_rows_from_holdings(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []
    frame = pd.DataFrame(rows)
    if frame.empty:
        return []
    frame["weight_pct"] = pd.to_numeric(frame["weight_pct"], errors="coerce")
    collected_at = _utc_now_string()
    out: list[dict[str, Any]] = []
    for (fund_symbol, as_of_date, source), group in frame.groupby(["fund_symbol", "as_of_date", "source"], dropna=False):
        status = "actual" if float(group["weight_pct"].fillna(0).sum()) >= 80 else "partial"
        source_ref = next((value for value in group.get("source_ref", []) if value), None)
        source_type = next((value for value in group.get("source_type", []) if value), "official")
        for exposure_type, column in (
            ("asset_class", "asset_class"),
            ("sector", "sector"),
            ("country", "country"),
            ("currency", "currency"),
        ):
            if column not in group.columns:
                continue
            clean_group = group.dropna(subset=[column, "weight_pct"]).copy()
            if clean_group.empty:
                continue
            clean_group[column] = clean_group[column].astype(str).str.strip()
            clean_group = clean_group[~clean_group[column].isin(["", "-", "None", "nan"])]
            if clean_group.empty:
                continue
            for exposure_name, exposure_group in clean_group.groupby(column, dropna=False):
                weight = float(exposure_group["weight_pct"].sum())
                out.append(
                    _exposure_row(
                        fund_symbol=str(fund_symbol).upper(),
                        as_of_date=str(as_of_date),
                        source=str(source),
                        source_type=str(source_type),
                        source_ref=source_ref,
                        derived_from=HOLDINGS_TABLE,
                        exposure_type=exposure_type,
                        exposure_name=str(exposure_name),
                        weight_pct=weight,
                        coverage_status=status,
                        collected_at=collected_at,
                    )
                )
    return out


def _parse_ssga_sector_exposures(
    fund_symbol: str,
    source_info: dict[str, Any],
    document: str,
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> list[dict[str, Any]]:
    match = re.search(r'id="fund-sector-breakdown"\s+value="([^"]+)"', document, re.IGNORECASE | re.DOTALL)
    if not match:
        return []
    payload = json.loads(html.unescape(match.group(1)))
    as_of = _parse_holdings_as_of(payload.get("asOfDateSimple")) or _parse_holdings_as_of(payload.get("asOfDate")) or as_of_fallback
    rows: list[dict[str, Any]] = []
    for item in payload.get("attrArray", []):
        name = ((item.get("name") or {}).get("value") if isinstance(item, dict) else None)
        weight = ((item.get("weight") or {}).get("originalValue") if isinstance(item, dict) else None)
        exposure_name = _clean_text(name)
        weight_value = _parse_float_value(weight)
        if exposure_name is None or weight_value is None:
            continue
        rows.append(
            _exposure_row(
                fund_symbol=fund_symbol,
                as_of_date=as_of or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
                source=source_info["source"],
                source_type="official",
                source_ref=source_info["url"],
                derived_from="provider_aggregate",
                exposure_type="sector",
                exposure_name=exposure_name,
                weight_pct=weight_value,
                coverage_status="actual",
                collected_at=collected_at,
            )
        )
    return rows


def _parse_invesco_sector_exposures(
    fund_symbol: str,
    source_info: dict[str, Any],
    payload: dict[str, Any],
    *,
    as_of_fallback: str | None,
    collected_at: str,
) -> list[dict[str, Any]]:
    as_of = _date_string(payload.get("effectiveDate")) or as_of_fallback
    rows: list[dict[str, Any]] = []
    holdings = payload.get("holdingWeights")
    if not isinstance(holdings, list):
        return rows
    for item in holdings:
        if not isinstance(item, dict):
            continue
        exposure_name = _clean_text(item.get("name"))
        weight_value = _parse_float_value(item.get("value"))
        if exposure_name is None or weight_value is None:
            continue
        rows.append(
            _exposure_row(
                fund_symbol=fund_symbol,
                as_of_date=as_of or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
                source=source_info["source"],
                source_type="official",
                source_ref=source_info["url"],
                derived_from="provider_aggregate",
                exposure_type="sector",
                exposure_name=exposure_name,
                weight_pct=weight_value,
                coverage_status="actual",
                collected_at=collected_at,
            )
        )
    return rows


def _build_provider_aggregate_exposure_rows(
    symbols: list[str],
    *,
    as_of_date: str | None,
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    only_source: str | None = None,
) -> tuple[list[dict[str, Any]], list[dict[str, str]]]:
    collected_at = _utc_now_string()
    rows: list[dict[str, Any]] = []
    failed: list[dict[str, str]] = []
    source_map = _source_map_info_by_symbol(symbols, data_kind="exposure", only_source=only_source)
    for symbol in symbols:
        source_info = source_map.get(symbol) or EXPOSURE_PROVIDER_SOURCES.get(symbol)
        if not source_info or (only_source is not None and source_info.get("source") != only_source):
            continue
        try:
            parser = str(source_info.get("parser") or "")
            if parser == "ssga_sector_page":
                document = _fetch_official_html(str(source_info["url"]), timeout=timeout)
                rows.extend(
                    _parse_ssga_sector_exposures(
                        symbol,
                        source_info,
                        document,
                        as_of_fallback=as_of_date,
                        collected_at=collected_at,
                    )
                )
            elif parser == "invesco_sector_json":
                payload = _fetch_official_json(str(source_info["url"]), timeout=timeout)
                rows.extend(
                    _parse_invesco_sector_exposures(
                        symbol,
                        source_info,
                        payload,
                        as_of_fallback=as_of_date,
                        collected_at=collected_at,
                    )
                )
            elif parser == "commodity_gold":
                rows.append(
                    _exposure_row(
                        fund_symbol=symbol,
                        as_of_date=as_of_date or pd.Timestamp.utcnow().strftime("%Y-%m-%d"),
                        source=str(source_info.get("source") or "commodity"),
                        source_type="official",
                        source_ref=source_info.get("url"),
                        derived_from="provider_aggregate",
                        exposure_type="asset_class",
                        exposure_name="Gold",
                        weight_pct=100.0,
                        coverage_status="actual",
                        collected_at=collected_at,
                    )
                )
        except Exception as exc:
            failed.append({"symbol": symbol, "reason": str(exc)[:500]})
    return rows, failed


def collect_and_store_etf_operability(
    symbols: str | Iterable[str],
    *,
    as_of_date: str | None = None,
    provider: str = "db_bridge",
    refresh_mode: str = "upsert",
    lookback_days: int = DEFAULT_LOOKBACK_DAYS,
    timeframe: str = "1d",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Build ETF operability snapshots from official issuer pages and local DB bridge data."""
    normalized_symbols = _normalize_symbols(symbols)
    if not normalized_symbols:
        return {
            "requested": 0,
            "stored": 0,
            "missing": [],
            "failed": [],
            "coverage": {},
        }

    normalized_provider = str(provider or "db_bridge").strip().lower()
    if normalized_provider not in {"auto", "db_bridge", "official", "ishares", "ssga", "invesco"}:
        raise NotImplementedError("Unsupported ETF operability provider.")
    if str(refresh_mode or "upsert").strip().lower() != "upsert":
        raise NotImplementedError("Only upsert refresh_mode is supported for ETF operability bridge snapshots.")
    if int(lookback_days) <= 0:
        raise ValueError("lookback_days must be positive.")

    as_of = _date_string(as_of_date) if as_of_date is not None else None
    rows: list[dict[str, Any]] = []
    db_symbols = list(normalized_symbols)
    official_symbols = list(normalized_symbols)
    official_source_filter: str | None = None
    if normalized_provider in {"ishares", "ssga", "invesco"}:
        official_source_filter = normalized_provider
        db_symbols = []
    elif normalized_provider == "official":
        db_symbols = []
    elif normalized_provider == "db_bridge":
        official_symbols = []

    if official_symbols:
        rows.extend(_build_official_rows(official_symbols, as_of_date=as_of, only_source=official_source_filter))

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["etf_operability_snapshot"])
        sync_table_schema(
            db,
            OPERABILITY_TABLE,
            PROVIDER_SCHEMAS["etf_operability_snapshot"],
            DB_META,
        )
        if db_symbols:
            profile_rows = _load_asset_profile_rows(db, db_symbols)
            latest_dates = _load_latest_price_dates(
                db,
                db_symbols,
                as_of_date=as_of,
                timeframe=timeframe,
            )
            price_rows = _load_price_metric_rows(
                db,
                db_symbols,
                latest_dates=latest_dates,
                lookback_days=int(lookback_days),
                timeframe=timeframe,
            )
            rows.extend(
                _build_db_bridge_rows(
                    db_symbols,
                    as_of_date=as_of,
                    lookback_days=int(lookback_days),
                    profile_rows=profile_rows,
                    price_rows=price_rows,
                )
            )
        db.use_db(DB_META)
        _upsert_etf_operability_rows(db, rows)
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1
    missing = [row["symbol"] for row in rows if row.get("coverage_status") == "missing"]

    return {
        "requested": len(normalized_symbols),
        "stored": len(rows),
        "updated": None,
        "missing": missing,
        "failed": [],
        "coverage": coverage,
        "source": normalized_provider,
        "lookback_days": int(lookback_days),
    }


def collect_and_store_etf_holdings(
    symbols: str | Iterable[str],
    *,
    as_of_date: str | None = None,
    provider: str = "official",
    refresh_mode: str = "canonical_refresh",
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Fetch official ETF holdings downloads and store normalized row-level snapshots."""
    normalized_symbols = _normalize_symbols(symbols)
    if not normalized_symbols:
        return {
            "requested": 0,
            "stored": 0,
            "missing": [],
            "failed": [],
            "coverage": {},
        }

    normalized_provider = str(provider or "official").strip().lower()
    if normalized_provider not in {"official", "auto", "ishares", "ssga", "invesco"}:
        raise NotImplementedError("Unsupported ETF holdings provider.")
    normalized_refresh = str(refresh_mode or "canonical_refresh").strip().lower()
    if normalized_refresh not in {"canonical_refresh", "upsert"}:
        raise NotImplementedError("Only canonical_refresh and upsert refresh modes are supported for ETF holdings.")

    as_of = _date_string(as_of_date) if as_of_date is not None else None
    only_source = normalized_provider if normalized_provider in {"ishares", "ssga", "invesco"} else None
    rows, missing, failed = _build_official_holdings_rows(
        normalized_symbols,
        as_of_date=as_of,
        timeout=int(timeout),
        only_source=only_source,
    )

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        for key, table_name in (
            ("etf_holdings_snapshot", HOLDINGS_TABLE),
            ("etf_exposure_snapshot", EXPOSURE_TABLE),
        ):
            db.execute(PROVIDER_SCHEMAS[key])
            sync_table_schema(db, table_name, PROVIDER_SCHEMAS[key], DB_META)
        if normalized_refresh == "canonical_refresh":
            _delete_snapshot_scope(db, HOLDINGS_TABLE, key_symbol_column="fund_symbol", scope_rows=rows)
        _upsert_etf_holdings_rows(db, rows)
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1
    found_symbols = {str(row.get("fund_symbol") or "").upper() for row in rows}
    for symbol in normalized_symbols:
        if symbol not in found_symbols and symbol not in missing:
            missing.append(symbol)

    return {
        "requested": len(normalized_symbols),
        "stored": len(rows),
        "updated": None,
        "missing": sorted(set(missing)),
        "failed": failed,
        "coverage": coverage,
        "source": normalized_provider,
        "refresh_mode": normalized_refresh,
    }


def _load_latest_holdings_for_exposure(
    db: MySQLClient,
    symbols: list[str],
    *,
    as_of_date: str | None,
    source: str | None,
    latest: bool,
) -> list[dict[str, Any]]:
    where: list[str] = []
    params: list[Any] = []
    if symbols:
        placeholders = ",".join(["%s"] * len(symbols))
        where.append(f"fund_symbol IN ({placeholders})")
        params.extend(symbols)
    if source is not None:
        where.append("source = %s")
        params.append(str(source).strip())

    if latest:
        latest_where_parts = list(where)
        latest_params = list(params)
        if as_of_date is not None:
            latest_where_parts.append("as_of_date <= %s")
            latest_params.append(as_of_date)
        latest_where = f"WHERE {' AND '.join(latest_where_parts)}" if latest_where_parts else ""
        sql = f"""
        SELECT ehs.*
        FROM {HOLDINGS_TABLE} ehs
        INNER JOIN (
            SELECT fund_symbol, source, MAX(as_of_date) AS latest_as_of_date
            FROM {HOLDINGS_TABLE}
            {latest_where}
            GROUP BY fund_symbol, source
        ) latest_rows
            ON ehs.fund_symbol = latest_rows.fund_symbol
           AND ehs.source = latest_rows.source
           AND ehs.as_of_date = latest_rows.latest_as_of_date
        ORDER BY ehs.fund_symbol ASC, ehs.source ASC, ehs.weight_pct DESC
        """
        return db.query(sql, latest_params)

    if as_of_date is not None:
        where.append("as_of_date = %s")
        params.append(as_of_date)
    base_where = f"WHERE {' AND '.join(where)}" if where else ""
    return db.query(
        f"""
        SELECT *
        FROM {HOLDINGS_TABLE}
        {base_where}
        ORDER BY fund_symbol ASC, source ASC, weight_pct DESC
        """,
        params,
    )


def aggregate_and_store_etf_exposures(
    symbols: str | Iterable[str],
    *,
    as_of_date: str | None = None,
    source: str | None = None,
    latest: bool = True,
    include_provider_aggregates: bool = True,
    refresh_mode: str = "canonical_refresh",
    timeout: int = OFFICIAL_REQUEST_TIMEOUT,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Aggregate stored ETF holdings into exposure snapshots and optional official aggregate rows."""
    normalized_symbols = _normalize_symbols(symbols)
    if not normalized_symbols:
        return {
            "requested": 0,
            "stored": 0,
            "missing": [],
            "failed": [],
            "coverage": {},
        }
    normalized_refresh = str(refresh_mode or "canonical_refresh").strip().lower()
    if normalized_refresh not in {"canonical_refresh", "upsert"}:
        raise NotImplementedError("Only canonical_refresh and upsert refresh modes are supported for ETF exposures.")

    as_of = _date_string(as_of_date) if as_of_date is not None else None
    db = MySQLClient(host, user, password, port)
    failed: list[dict[str, str]] = []
    try:
        db.use_db(DB_META)
        for key, table_name in (
            ("etf_holdings_snapshot", HOLDINGS_TABLE),
            ("etf_exposure_snapshot", EXPOSURE_TABLE),
        ):
            db.execute(PROVIDER_SCHEMAS[key])
            sync_table_schema(db, table_name, PROVIDER_SCHEMAS[key], DB_META)
        try:
            holdings_rows = _load_latest_holdings_for_exposure(
                db,
                normalized_symbols,
                as_of_date=as_of,
                source=source,
                latest=latest,
            )
        except Exception as exc:
            if _is_missing_table_error(exc, HOLDINGS_TABLE):
                holdings_rows = []
            else:
                raise
        rows = _aggregate_exposure_rows_from_holdings(holdings_rows)
        if include_provider_aggregates:
            provider_rows, provider_failed = _build_provider_aggregate_exposure_rows(
                normalized_symbols,
                as_of_date=as_of,
                timeout=int(timeout),
                only_source=source,
            )
            rows.extend(provider_rows)
            failed.extend(provider_failed)
        if normalized_refresh == "canonical_refresh":
            _delete_snapshot_scope(db, EXPOSURE_TABLE, key_symbol_column="fund_symbol", scope_rows=rows)
        _upsert_etf_exposure_rows(db, rows)
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1
    found_symbols = {str(row.get("fund_symbol") or "").upper() for row in rows}
    missing = [symbol for symbol in normalized_symbols if symbol not in found_symbols]
    return {
        "requested": len(normalized_symbols),
        "stored": len(rows),
        "updated": None,
        "missing": missing,
        "failed": failed,
        "coverage": coverage,
        "source": source,
        "refresh_mode": normalized_refresh,
        "include_provider_aggregates": bool(include_provider_aggregates),
    }
