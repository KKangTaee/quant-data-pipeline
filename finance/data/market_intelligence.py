from __future__ import annotations

import calendar
import hashlib
import json
import re
from collections import Counter
from collections.abc import Callable, Iterable, Sequence
from contextlib import redirect_stderr, redirect_stdout
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from inspect import Parameter, signature
from time import sleep
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen
from zoneinfo import ZoneInfo

import pandas as pd
import yfinance as yf
from bs4 import BeautifulSoup
from yfinance.data import YfData

from .db.mysql import MySQLClient
from .db.schema import MARKET_INTELLIGENCE_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
DB_PRICE = "finance_price"
SP500_SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SP500_SOURCE = "wikipedia_sp500_constituents"
FOMC_CALENDAR_SOURCE_URL = "https://www.federalreserve.gov/monetarypolicy/fomccalendars.htm"
FOMC_CALENDAR_SOURCE = "federal_reserve_fomc_calendar"
BLS_MACRO_CALENDAR_SOURCE_URL_TEMPLATE = "https://www.bls.gov/schedule/{year}/"
BLS_MACRO_CALENDAR_ICS_SOURCE_URL = "https://www.bls.gov/schedule/news_release/bls.ics"
BLS_MACRO_CALENDAR_SOURCE = "bureau_labor_statistics_release_schedule"
BEA_MACRO_CALENDAR_SOURCE_URL = "https://www.bea.gov/index.php/news/schedule/full"
BEA_MACRO_CALENDAR_SOURCE = "bureau_economic_analysis_release_schedule"
CENSUS_ECONOMIC_INDICATORS_SOURCE_URL = "https://www.census.gov/economic-indicators/calendar-listview.html"
CENSUS_ECONOMIC_INDICATORS_SOURCE = "census_economic_indicators_calendar"
ISM_REPORT_CALENDAR_SOURCE_URL = "https://www.ismworld.org/supply-management-news-and-reports/reports/rob-report-calendar/"
ISM_REPORT_CALENDAR_SOURCE = "ism_report_calendar"
TREASURY_AUCTIONS_SOURCE_URL = "https://www.treasurydirect.gov/auctions/upcoming/"
TREASURY_AUCTIONS_SOURCE = "treasurydirect_auction_calendar"
MACRO_CALENDAR_SOURCE = "official_macro_release_schedules"
NASDAQ_MARKET_HOLIDAY_SOURCE_URL = "https://www.nasdaqtrader.com/trader.aspx?id=calendar"
NASDAQ_MARKET_HOLIDAY_SOURCE = "nasdaqtrader_equity_options_holiday_calendar"
CBOE_OPTIONS_EXPIRATION_SOURCE_URL_TEMPLATE = "https://cdn.cboe.com/resources/options/Cboe{year}OPTIONSCalendar.pdf"
CBOE_OPTIONS_EXPIRATION_SOURCE = "cboe_options_expiration_calendar"
FTSE_RUSSELL_RECONSTITUTION_SOURCE_URL = (
    "https://www.lseg.com/en/media-centre/press-releases/ftse-russell/2026/"
    "russell-reconstitution-2026-schedule"
)
FTSE_RUSSELL_RECONSTITUTION_SOURCE = "ftse_russell_reconstitution_schedule"
MARKET_STRUCTURE_CALENDAR_SOURCE = "official_market_structure_calendars"
EARNINGS_CALENDAR_SOURCE = "yfinance_calendar"
EARNINGS_CALENDAR_SOURCE_URL = "https://finance.yahoo.com/calendar/earnings"
NASDAQ_EARNINGS_CALENDAR_SOURCE = "nasdaq_earnings_calendar"
NASDAQ_EARNINGS_CALENDAR_API_URL = "https://api.nasdaq.com/api/calendar/earnings"
COMPANY_IR_EARNINGS_SOURCE = "company_ir_calendar"
EARNINGS_PROVIDER_ESTIMATE_CONFIDENCE = 0.65
EARNINGS_CROSS_CHECKED_CONFIDENCE = 0.75
EARNINGS_NOT_CONFIRMED_CONFIDENCE = 0.6
EARNINGS_STALE_ESTIMATE_DAYS = 14
EARNINGS_SYMBOL_SOURCE_ALIASES = {
    "latest_movers": "latest_movers",
    "latest movers": "latest_movers",
    "latest_sp500_movers": "latest_movers",
    "sp500": "sp500",
    "sp500_universe": "sp500",
    "s&p500": "sp500",
    "s&p 500": "sp500",
    "top1000": "top1000",
    "top1000_batch": "top1000",
    "top2000": "top2000",
    "top2000_batch": "top2000",
    "major_cap": "major_cap",
    "large_cap": "major_cap",
    "large-cap": "major_cap",
    "nasdaq100": "nasdaq100",
    "nasdaq_100": "nasdaq100",
    "nasdaq 100": "nasdaq100",
    "portfolio": "portfolio",
    "watchlist": "watchlist",
    "manual": "manual",
    "universe": "universe",
}
EARNINGS_UNIVERSE_SCOPE_BY_SOURCE = {
    "latest_movers": "latest_movers",
    "sp500": "sp500",
    "top1000": "major_cap",
    "top2000": "major_cap",
    "major_cap": "major_cap",
    "nasdaq100": "nasdaq100",
    "portfolio": "portfolio",
    "watchlist": "watchlist",
    "manual": "watchlist",
}
DEFAULT_INTRADAY_INTERVAL = "5m"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
VALID_INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
MARKET_CAP_UNIVERSE_LIMITS = {"TOP1000": 1000, "TOP2000": 2000}
NASDAQ_SYMBOL_DIRECTORY_SOURCE = "nasdaq_symdir_nasdaqlisted"
NASDAQ_SYMBOL_DIRECTORY_URL = "https://www.nasdaqtrader.com/dynamic/SymDir/nasdaqlisted.txt"
LIQUIDITY_UNIVERSE_RANKING_SOURCE = "nyse_price_history.20d_avg_dollar_volume"
LIQUIDITY_UNIVERSE_PRICE_SOURCE = "finance_price.nyse_price_history"
LIQUIDITY_UNIVERSE_LISTING_SOURCES = (
    "nasdaq_symdir_nasdaqlisted",
    "nasdaq_symdir_otherlisted",
    "nyse_listings_directory",
    "sec_company_tickers_exchange",
)
MARKET_UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
    "NASDAQ": "Nasdaq-listed current snapshot",
}
BLS_MACRO_RELEASE_TYPES = [
    {
        "event_type": "MACRO_CPI",
        "label": "CPI",
        "match": "consumer price index",
        "aliases": ["cpi"],
    },
    {
        "event_type": "MACRO_PPI",
        "label": "PPI",
        "match": "producer price index",
        "aliases": ["ppi"],
    },
    {
        "event_type": "MACRO_EMPLOYMENT",
        "label": "Employment Situation",
        "match": "employment situation",
        "aliases": ["the employment situation"],
    },
    {
        "event_type": "MACRO_JOLTS",
        "label": "JOLTS",
        "match": "job openings and labor turnover survey",
        "aliases": ["jolts"],
    },
    {
        "event_type": "MACRO_ECI",
        "label": "Employment Cost Index",
        "match": "employment cost index",
        "aliases": ["eci"],
    },
]
CENSUS_MACRO_RELEASE_TYPES = [
    {
        "event_type": "MACRO_RETAIL_SALES",
        "label": "Retail Sales",
        "match": "advance monthly sales for retail and food services",
        "aliases": ["monthly retail trade", "retail and food services"],
    },
    {
        "event_type": "MACRO_DURABLE_GOODS",
        "label": "Durable Goods",
        "match": "durable goods",
        "aliases": ["manufacturers' shipments inventories and orders", "manufacturers shipments inventories and orders"],
    },
    {
        "event_type": "MACRO_HOUSING",
        "label": "Housing",
        "match": "new residential construction",
        "aliases": ["housing starts", "new residential sales"],
    },
    {
        "event_type": "MACRO_CONSTRUCTION_SPENDING",
        "label": "Construction Spending",
        "match": "construction spending",
        "aliases": [],
    },
    {
        "event_type": "MACRO_TRADE",
        "label": "Trade",
        "match": "international trade",
        "aliases": ["advance economic indicators", "goods and services"],
    },
]
ISM_MACRO_RELEASE_TYPES = [
    {
        "event_type": "MACRO_ISM_MANUFACTURING_PMI",
        "label": "ISM Manufacturing PMI",
        "match": "manufacturing",
        "aliases": ["manufacturing pmi", "manufacturing ism"],
    },
    {
        "event_type": "MACRO_ISM_SERVICES_PMI",
        "label": "ISM Services PMI",
        "match": "services",
        "aliases": ["services pmi", "service pmi", "services ism"],
    },
]
MONTH_NAME_TO_NUMBER = {
    "JAN": 1,
    "JANUARY": 1,
    "FEB": 2,
    "FEBRUARY": 2,
    "MAR": 3,
    "MARCH": 3,
    "APR": 4,
    "APRIL": 4,
    "MAY": 5,
    "JUN": 6,
    "JUNE": 6,
    "JUL": 7,
    "JULY": 7,
    "AUG": 8,
    "AUGUST": 8,
    "SEP": 9,
    "SEPT": 9,
    "SEPTEMBER": 9,
    "OCT": 10,
    "OCTOBER": 10,
    "NOV": 11,
    "NOVEMBER": 11,
    "DEC": 12,
    "DECEMBER": 12,
}


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(second=0, microsecond=0)


def _timestamp_str(value: datetime | None = None) -> str:
    return (value or _utc_now()).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper().replace(".", "-")


def _normalize_intraday_universe(
    universe_code: str | None,
    universe_limit: int | None = None,
) -> tuple[str, int]:
    normalized = str(universe_code or "").strip().upper()
    if normalized == "SP500":
        return "SP500", 500
    if normalized == "NASDAQ":
        return "NASDAQ", int(universe_limit or 5000)
    if normalized in MARKET_CAP_UNIVERSE_LIMITS:
        return normalized, MARKET_CAP_UNIVERSE_LIMITS[normalized]
    if universe_limit is not None:
        try:
            parsed_limit = int(universe_limit)
        except (TypeError, ValueError):
            parsed_limit = 1000
        return ("TOP2000", 2000) if parsed_limit >= 2000 else ("TOP1000", 1000)
    raise ValueError(f"Unsupported intraday universe: {universe_code!r}")


def normalize_earnings_symbol_source(value: Any) -> str:
    normalized = str(value or "latest_movers").strip().lower().replace("-", "_")
    return EARNINGS_SYMBOL_SOURCE_ALIASES.get(normalized, normalized or "latest_movers")


def earnings_universe_scope_for_source(
    symbol_source: Any,
    *,
    universe_code: str | None = None,
) -> str:
    normalized_source = normalize_earnings_symbol_source(symbol_source)
    if normalized_source == "universe":
        normalized_universe = str(universe_code or "").strip().upper()
        if normalized_universe == "SP500":
            return "sp500"
        if normalized_universe == "NASDAQ100":
            return "nasdaq100"
        if normalized_universe in MARKET_CAP_UNIVERSE_LIMITS:
            return "major_cap"
        return "unknown"
    return EARNINGS_UNIVERSE_SCOPE_BY_SOURCE.get(normalized_source, "unknown")


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(parsed):
        return None
    return parsed


def _safe_int(value: Any) -> int | None:
    parsed = _safe_float(value)
    if parsed is None:
        return None
    return int(parsed)


def _to_utc_naive(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    if ts.tzinfo is None:
        ts = ts.tz_localize(UTC)
    else:
        ts = ts.tz_convert(UTC)
    return ts.strftime("%Y-%m-%d %H:%M:%S")


def _epoch_to_utc_naive(value: Any) -> str | None:
    parsed = _safe_int(value)
    if parsed is None:
        return None
    return datetime.fromtimestamp(parsed, tz=UTC).replace(tzinfo=None).strftime("%Y-%m-%d %H:%M:%S")


def _db(host: str, user: str, password: str, port: int) -> MySQLClient:
    return MySQLClient(host, user, password, port)


def sync_market_intelligence_tables(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    meta_db = _db(host, user, password, port)
    price_db = _db(host, user, password, port)
    try:
        meta_db.use_db(DB_META)
        sync_table_schema(
            meta_db,
            "market_universe_member",
            MARKET_INTELLIGENCE_SCHEMAS["market_universe_member"],
            DB_META,
        )
        sync_table_schema(
            meta_db,
            "market_liquidity_universe_member",
            MARKET_INTELLIGENCE_SCHEMAS["market_liquidity_universe_member"],
            DB_META,
        )
        sync_table_schema(
            meta_db,
            "market_symbol_alias",
            MARKET_INTELLIGENCE_SCHEMAS["market_symbol_alias"],
            DB_META,
        )
        sync_table_schema(
            meta_db,
            "market_event_calendar",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"],
            DB_META,
        )
        sync_table_schema(
            meta_db,
            "market_data_issue",
            MARKET_INTELLIGENCE_SCHEMAS["market_data_issue"],
            DB_META,
        )
        price_db.use_db(DB_PRICE)
        sync_table_schema(
            price_db,
            "market_intraday_snapshot",
            MARKET_INTELLIGENCE_SCHEMAS["market_intraday_snapshot"],
            DB_PRICE,
        )
    finally:
        meta_db.close()
        price_db.close()


def fetch_sp500_constituents(source_url: str = SP500_SOURCE_URL) -> list[dict[str, Any]]:
    request = Request(
        source_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        html = response.read().decode("utf-8", errors="replace")
    tables = pd.read_html(StringIO(html), attrs={"id": "constituents"})
    if not tables:
        raise RuntimeError("S&P 500 constituents table was not found.")
    frame = tables[0]
    rows: list[dict[str, Any]] = []
    for item in frame.to_dict("records"):
        source_symbol = str(item.get("Symbol") or "").strip().upper()
        symbol = _normalize_symbol(source_symbol)
        if not symbol:
            continue
        rows.append(
            {
                "universe_code": "SP500",
                "symbol": symbol,
                "source_symbol": source_symbol,
                "name": item.get("Security") or "",
                "sector": item.get("GICS Sector") or "",
                "industry": item.get("GICS Sub-Industry") or "",
                "source": SP500_SOURCE,
                "source_url": source_url,
                "as_of_date": datetime.now(UTC).date().isoformat(),
                "active": 1,
                "collected_at": _timestamp_str(),
                "error_msg": None,
            }
        )
    return rows


def _event_date_str(value: Any) -> str | None:
    if value in (None, ""):
        return None
    ts = pd.Timestamp(value)
    if pd.isna(ts):
        return None
    return ts.strftime("%Y-%m-%d")


def _normalize_event_type(value: Any) -> str:
    return str(value or "").strip().upper().replace(" ", "_")


def _normalize_event_symbol(value: Any) -> str | None:
    symbol = _normalize_symbol(value)
    return symbol or None


def _normalize_event_taxonomy_value(value: Any) -> str | None:
    normalized = str(value or "").strip().lower().replace(" ", "_")
    return normalized or None


def _normalize_event_datetime_utc(value: Any) -> str | None:
    return _to_utc_naive(value)


def _event_subtype_from_type(event_type: str) -> str:
    normalized = _normalize_event_type(event_type)
    if normalized.startswith("MACRO_"):
        return normalized.replace("MACRO_", "").lower()
    return normalized.lower()


def _event_datetime_utc_from_eastern_time(event_date: str, release_time_et: str | None) -> str | None:
    if not release_time_et:
        return None
    try:
        local_dt = datetime.strptime(f"{event_date} {release_time_et}", "%Y-%m-%d %H:%M")
    except ValueError:
        return None
    eastern_dt = local_dt.replace(tzinfo=ZoneInfo("America/New_York"))
    return eastern_dt.astimezone(UTC).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_source_type(value: Any, *, event_type: str, source: str) -> str:
    normalized = str(value or "").strip().lower().replace(" ", "_")
    if normalized in {"official", "provider_estimate", "unknown"}:
        return normalized
    source_normalized = str(source or "").strip().lower()
    if source_normalized in {FOMC_CALENDAR_SOURCE, COMPANY_IR_EARNINGS_SOURCE}:
        return "official"
    if _normalize_event_type(event_type) == "EARNINGS":
        return "provider_estimate"
    return "unknown"


def _normalize_validation_status(value: Any, *, source_type: str) -> str:
    normalized = str(value or "").strip().lower().replace(" ", "_")
    if normalized in {"official", "estimate_only", "cross_checked", "not_confirmed", "conflict", "unknown"}:
        return normalized
    if source_type == "official":
        return "official"
    if source_type == "provider_estimate":
        return "estimate_only"
    return "unknown"


def _normalize_event_status(value: Any) -> str:
    normalized = str(value or "active").strip().lower().replace(" ", "_")
    if normalized in {"active", "superseded", "stale"}:
        return normalized
    return "active"


def _normalize_symbol_list(symbols: str | Sequence[Any] | None, *, max_symbols: int = 100) -> list[str]:
    if symbols is None:
        return []
    if isinstance(symbols, str):
        raw_items = re.split(r"[,\n\r\t ]+", symbols)
    else:
        raw_items = list(symbols)
    out: list[str] = []
    seen: set[str] = set()
    for item in raw_items:
        symbol = _normalize_symbol(item)
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        out.append(symbol)
        if len(out) >= max(1, int(max_symbols or 100)):
            break
    return out


def _json_safe_payload_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, dict):
        return {str(key): _json_safe_payload_value(val) for key, val in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe_payload_value(val) for val in value]
    if isinstance(value, float) and pd.isna(value):
        return None
    try:
        if pd.isna(value):
            return None
    except (TypeError, ValueError):
        pass
    return value


def _json_payload(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = {"raw": value}
        return json.dumps(
            _json_safe_payload_value(parsed),
            ensure_ascii=False,
            sort_keys=True,
            separators=(",", ":"),
            default=str,
            allow_nan=False,
        )
    return json.dumps(
        _json_safe_payload_value(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
        default=str,
        allow_nan=False,
    )


def _market_event_key(row: dict[str, Any]) -> str:
    parts = [
        str(row.get("event_date") or ""),
        _normalize_event_type(row.get("event_type")),
        _normalize_event_symbol(row.get("symbol")) or "",
        str(row.get("title") or "").strip(),
        str(row.get("source") or "").strip(),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def normalize_market_event_rows(
    rows: list[dict[str, Any]],
    *,
    collected_at: str | None = None,
) -> list[dict[str, Any]]:
    normalized_rows: list[dict[str, Any]] = []
    default_collected_at = collected_at or _timestamp_str()
    for item in rows:
        event_date = _event_date_str(item.get("event_date"))
        event_type = _normalize_event_type(item.get("event_type"))
        title = str(item.get("title") or "").strip()
        source = str(item.get("source") or "").strip()
        if not event_date or not event_type or not title or not source:
            continue
        source_type = _normalize_source_type(item.get("source_type"), event_type=event_type, source=source)
        validation_status = _normalize_validation_status(item.get("validation_status"), source_type=source_type)
        row = {
            "event_date": event_date,
            "event_type": event_type,
            "event_family": _normalize_event_taxonomy_value(item.get("event_family")),
            "event_subtype": _normalize_event_taxonomy_value(item.get("event_subtype")),
            "event_time_label": str(item.get("event_time_label") or "").strip() or None,
            "event_datetime_utc": _normalize_event_datetime_utc(item.get("event_datetime_utc")),
            "universe_scope": _normalize_event_taxonomy_value(item.get("universe_scope")),
            "source_authority": _normalize_event_taxonomy_value(item.get("source_authority")),
            "symbol": _normalize_event_symbol(item.get("symbol")),
            "title": title,
            "source": source,
            "source_type": source_type,
            "validation_status": validation_status,
            "event_status": _normalize_event_status(item.get("event_status")),
            "superseded_by_event_key": str(item.get("superseded_by_event_key") or "").strip() or None,
            "superseded_at": item.get("superseded_at") or None,
            "source_url": item.get("source_url") or None,
            "confidence": _safe_float(item.get("confidence")),
            "collected_at": item.get("collected_at") or default_collected_at,
            "raw_payload_json": _json_payload(item.get("raw_payload_json") or item.get("raw_payload")),
        }
        row["event_key"] = str(item.get("event_key") or "").strip() or _market_event_key(row)
        normalized_rows.append(row)
    return normalized_rows


def upsert_market_event_rows(
    rows: list[dict[str, Any]],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    normalized_rows = normalize_market_event_rows(rows)
    if not normalized_rows:
        return 0
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_event_calendar",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"],
            DB_META,
        )
        sql = """
        INSERT INTO market_event_calendar (
          event_key, event_date, event_type, event_family, event_subtype, event_time_label,
          event_datetime_utc, universe_scope, source_authority, symbol, title,
          source, source_type, validation_status, event_status, superseded_by_event_key, superseded_at,
          source_url, confidence, collected_at, raw_payload_json
        ) VALUES (
          %(event_key)s, %(event_date)s, %(event_type)s, %(event_family)s, %(event_subtype)s, %(event_time_label)s,
          %(event_datetime_utc)s, %(universe_scope)s, %(source_authority)s, %(symbol)s, %(title)s,
          %(source)s, %(source_type)s, %(validation_status)s, %(event_status)s,
          %(superseded_by_event_key)s, %(superseded_at)s,
          %(source_url)s, %(confidence)s, %(collected_at)s, %(raw_payload_json)s
        )
        ON DUPLICATE KEY UPDATE
          event_date = VALUES(event_date),
          event_type = VALUES(event_type),
          event_family = VALUES(event_family),
          event_subtype = VALUES(event_subtype),
          event_time_label = VALUES(event_time_label),
          event_datetime_utc = VALUES(event_datetime_utc),
          universe_scope = VALUES(universe_scope),
          source_authority = VALUES(source_authority),
          symbol = VALUES(symbol),
          title = VALUES(title),
          source = VALUES(source),
          source_type = VALUES(source_type),
          validation_status = VALUES(validation_status),
          event_status = VALUES(event_status),
          superseded_by_event_key = VALUES(superseded_by_event_key),
          superseded_at = VALUES(superseded_at),
          source_url = VALUES(source_url),
          confidence = VALUES(confidence),
          collected_at = VALUES(collected_at),
          raw_payload_json = VALUES(raw_payload_json)
        """
        db.executemany(sql, normalized_rows)
        return len(normalized_rows)
    finally:
        db.close()


def mark_superseded_earnings_events(
    current_rows: list[dict[str, Any]],
    *,
    superseded_at: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    normalized_rows = [
        row
        for row in normalize_market_event_rows(current_rows)
        if row.get("event_type") == "EARNINGS" and row.get("symbol") and row.get("source")
    ]
    if not normalized_rows:
        return 0

    grouped: dict[tuple[str, str], list[dict[str, Any]]] = {}
    for row in normalized_rows:
        grouped.setdefault((str(row["symbol"]), str(row["source"])), []).append(row)

    db = _db(host, user, password, port)
    marked = 0
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_event_calendar",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"],
            DB_META,
        )
        for (symbol, source), rows in grouped.items():
            current_keys = sorted({str(row["event_key"]) for row in rows if row.get("event_key")})
            if not current_keys:
                continue
            placeholders = ",".join(["%s"] * len(current_keys))
            candidates = db.query(
                f"""
                SELECT event_key
                FROM market_event_calendar
                WHERE event_type = %s
                  AND symbol = %s
                  AND source = %s
                  AND COALESCE(event_status, 'active') = 'active'
                  AND event_key NOT IN ({placeholders})
                """,
                ["EARNINGS", symbol, source] + current_keys,
            )
            candidate_keys = [str(row.get("event_key")) for row in candidates if row.get("event_key")]
            if not candidate_keys:
                continue
            replacement_key = current_keys[0]
            update_placeholders = ",".join(["%s"] * len(candidate_keys))
            db.execute(
                f"""
                UPDATE market_event_calendar
                SET event_status = %s,
                    superseded_by_event_key = %s,
                    superseded_at = %s
                WHERE event_key IN ({update_placeholders})
                """,
                ["superseded", replacement_key, superseded_at or _timestamp_str()] + candidate_keys,
            )
            marked += len(candidate_keys)
    finally:
        db.close()
    return marked


def mark_stale_earnings_estimates(
    *,
    stale_after_days: int = EARNINGS_STALE_ESTIMATE_DAYS,
    as_of_date: str | date | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    today = _parse_window_date(as_of_date, default=datetime.now(UTC).date())
    cutoff = today - timedelta(days=max(1, int(stale_after_days or EARNINGS_STALE_ESTIMATE_DAYS)))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_event_calendar",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"],
            DB_META,
        )
        candidates = db.query(
            """
            SELECT event_key
            FROM market_event_calendar
            WHERE event_type = %s
              AND COALESCE(source_type, 'provider_estimate') = %s
              AND COALESCE(event_status, 'active') = %s
              AND collected_at IS NOT NULL
              AND DATE(collected_at) < %s
            """,
            ["EARNINGS", "provider_estimate", "active", cutoff.isoformat()],
        )
        candidate_keys = [str(row.get("event_key")) for row in candidates if row.get("event_key")]
        if not candidate_keys:
            return 0
        placeholders = ",".join(["%s"] * len(candidate_keys))
        db.execute(
            f"""
            UPDATE market_event_calendar
            SET event_status = %s
            WHERE event_key IN ({placeholders})
            """,
            ["stale"] + candidate_keys,
        )
        return len(candidate_keys)
    finally:
        db.close()


def load_market_event_calendar(
    *,
    start_date: str | None = None,
    end_date: str | None = None,
    event_type: str | None = None,
    symbol: str | None = None,
    limit: int = 500,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    conditions = ["1=1"]
    params: list[Any] = []
    normalized_start = _event_date_str(start_date)
    normalized_end = _event_date_str(end_date)
    normalized_type = _normalize_event_type(event_type)
    normalized_symbol = _normalize_event_symbol(symbol)
    if normalized_start:
        conditions.append("event_date >= %s")
        params.append(normalized_start)
    if normalized_end:
        conditions.append("event_date <= %s")
        params.append(normalized_end)
    if normalized_type:
        if normalized_type == "MACRO":
            conditions.append("event_type LIKE %s")
            params.append("MACRO_%")
        else:
            conditions.append("event_type = %s")
            params.append(normalized_type)
    if normalized_symbol:
        conditions.append("symbol = %s")
        params.append(normalized_symbol)
    bounded_limit = max(1, min(int(limit or 500), 5000))

    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_event_calendar",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"],
            DB_META,
        )
        return db.query(
            f"""
            SELECT
                event_key,
                event_date,
                event_type,
                event_family,
                event_subtype,
                event_time_label,
                event_datetime_utc,
                universe_scope,
                source_authority,
                symbol,
                title,
                source,
                source_type,
                validation_status,
                event_status,
                superseded_by_event_key,
                superseded_at,
                source_url,
                confidence,
                collected_at,
                raw_payload_json
            FROM market_event_calendar
            WHERE {" AND ".join(conditions)}
            ORDER BY event_date ASC, event_type ASC, COALESCE(symbol, '') ASC, title ASC
            LIMIT %s
            """,
            params + [bounded_limit],
        )
    finally:
        db.close()


def _fetch_html(source_url: str) -> str:
    request = Request(
        source_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            )
        },
    )
    with urlopen(request, timeout=30) as response:
        return response.read().decode("utf-8", errors="replace")


def _clean_text(value: Any) -> str:
    return re.sub(r"\s+", " ", str(value or "")).strip()


def _fomc_month_numbers(month_text: str) -> list[int]:
    out: list[int] = []
    for token in re.split(r"[/,&\s]+", month_text):
        normalized = re.sub(r"[^A-Za-z]", "", token).upper()
        month_number = MONTH_NAME_TO_NUMBER.get(normalized)
        if month_number:
            out.append(month_number)
    return out


def _fomc_event_date(year: int, month_text: str, date_text: str) -> str | None:
    month_numbers = _fomc_month_numbers(month_text)
    day_numbers = [int(item) for item in re.findall(r"\d{1,2}", date_text)]
    if not month_numbers or not day_numbers:
        return None

    start_month = month_numbers[0]
    end_month = month_numbers[-1]
    start_day = day_numbers[0]
    end_day = day_numbers[-1]
    end_year = int(year)
    if len(month_numbers) == 1 and len(day_numbers) >= 2 and end_day < start_day:
        end_month = 1 if start_month == 12 else start_month + 1
    if end_month < start_month:
        end_year += 1
    try:
        return datetime(end_year, end_month, end_day).date().isoformat()
    except ValueError:
        return None


def _parse_fomc_calendar_events_from_html(
    html: str,
    *,
    source_url: str = FOMC_CALENDAR_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    year_filter = {int(year) for year in years or []}
    soup = BeautifulSoup(html, "html.parser")
    events: list[dict[str, Any]] = []

    for panel in soup.select("div.panel.panel-default"):
        heading = panel.find("h4")
        heading_text = _clean_text(heading.get_text(" ")) if heading else ""
        match = re.search(r"\b(20\d{2})\s+FOMC\s+Meetings\b", heading_text)
        if not match:
            continue
        year = int(match.group(1))
        if year_filter and year not in year_filter:
            continue

        for meeting in panel.select("div.fomc-meeting"):
            month_node = meeting.select_one(".fomc-meeting__month")
            date_node = meeting.select_one(".fomc-meeting__date")
            month_text = _clean_text(month_node.get_text(" ")) if month_node else ""
            date_text = _clean_text(date_node.get_text(" ")) if date_node else ""
            event_date = _fomc_event_date(year, month_text, date_text)
            if not event_date:
                continue
            links = [
                {"label": _clean_text(link.get_text(" ")), "url": urljoin(source_url, str(link.get("href") or ""))}
                for link in meeting.find_all("a")
                if link.get("href")
            ]
            range_text = f"{month_text} {date_text}".strip()
            events.append(
                {
                    "event_date": event_date,
                    "event_type": "FOMC_MEETING",
                    "symbol": None,
                    "title": f"FOMC Meeting: {range_text}, {year}",
                    "source": FOMC_CALENDAR_SOURCE,
                    "source_url": source_url,
                    "confidence": 1.0,
                    "raw_payload": {
                        "year": year,
                        "month_text": month_text,
                        "date_text": date_text,
                        "meeting_range": range_text,
                        "event_date_basis": "final_meeting_day",
                        "has_summary_of_economic_projections": "*" in date_text,
                        "links": links,
                    },
                }
            )
    return events


def fetch_fomc_calendar_events(
    *,
    source_url: str = FOMC_CALENDAR_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    html = _fetch_html(source_url)
    events = _parse_fomc_calendar_events_from_html(html, source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No FOMC calendar events were parsed{year_text}.")
    return events


def collect_and_store_fomc_calendar(
    *,
    source_url: str = FOMC_CALENDAR_SOURCE_URL,
    years: Sequence[int] | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    collected_at = _timestamp_str()
    events = fetch_fomc_calendar_events(source_url=source_url, years=years)
    rows = [{**row, "collected_at": collected_at} for row in events]
    rows_written = upsert_market_event_rows(rows, host=host, user=user, password=password, port=port)
    event_dates = sorted({str(row["event_date"]) for row in rows if row.get("event_date")})
    return {
        "source": FOMC_CALENDAR_SOURCE,
        "source_url": source_url,
        "event_type": "FOMC_MEETING",
        "method": "official_html",
        "years_requested": [int(year) for year in years] if years else None,
        "events_found": len(rows),
        "rows_written": rows_written,
        "event_dates": event_dates,
        "collected_at": collected_at,
    }


def _normalize_release_time(value: Any) -> str | None:
    text = _clean_text(value).upper().replace(".", "")
    match = re.search(r"(\d{1,2}:\d{2})\s*([AP]M)", text)
    if not match:
        return None
    try:
        return datetime.strptime(f"{match.group(1)} {match.group(2)}", "%I:%M %p").strftime("%H:%M")
    except ValueError:
        return None


def _parse_release_date_time(value: Any, *, default_year: int | None = None) -> tuple[str | None, str | None]:
    text = _clean_text(value).replace("\xa0", " ")
    if not text:
        return None, None
    text = re.sub(r"^[A-Za-z]+,\s*", "", text)
    match = re.search(
        r"([A-Za-z]+)\s+(\d{1,2}),?\s+(20\d{2})(?:\s+(\d{1,2}:\d{2})\s*([AP]\.?M\.?))?",
        text,
        flags=re.IGNORECASE,
    )
    if not match and default_year:
        match = re.search(
            r"([A-Za-z]+)\s+(\d{1,2})(?:\s+(\d{1,2}:\d{2})\s*([AP]\.?M\.?))?",
            text,
            flags=re.IGNORECASE,
        )
        if match:
            month_text, day_text, time_text, meridiem = match.groups()
            year = int(default_year)
        else:
            return None, None
    elif match:
        month_text, day_text, year_text, time_text, meridiem = match.groups()
        year = int(year_text)
    else:
        return None, None
    month_number = MONTH_NAME_TO_NUMBER.get(re.sub(r"[^A-Za-z]", "", month_text).upper())
    if not month_number:
        return None, None
    try:
        event_date = datetime(year, month_number, int(day_text)).date().isoformat()
    except ValueError:
        return None, None
    release_time = _normalize_release_time(f"{time_text or ''} {meridiem or ''}")
    return event_date, release_time


def _frame_records_from_html_table(html: str) -> list[dict[str, Any]]:
    try:
        tables = pd.read_html(StringIO(html))
    except ValueError:
        return []
    records: list[dict[str, Any]] = []
    for frame in tables:
        if frame.empty:
            continue
        normalized_frame = frame.copy()
        normalized_frame.columns = [_clean_text(column) for column in normalized_frame.columns]
        records.extend(normalized_frame.to_dict("records"))
    return records


def _record_value_by_hint(record: dict[str, Any], hints: Sequence[str], *, fallback_index: int | None = None) -> Any:
    lowered_hints = [hint.lower() for hint in hints]
    for key, value in record.items():
        normalized_key = _clean_text(key).lower()
        if any(hint in normalized_key for hint in lowered_hints):
            return value
    if fallback_index is not None:
        values = list(record.values())
        if 0 <= fallback_index < len(values):
            return values[fallback_index]
    return None


def _bls_macro_release_type(release_title: Any) -> dict[str, str] | None:
    normalized = _clean_text(release_title).lower()
    for item in BLS_MACRO_RELEASE_TYPES:
        terms = [str(item["match"])] + [str(alias) for alias in item.get("aliases", [])]
        for term in terms:
            if re.search(rf"\b{re.escape(term.lower())}\b", normalized):
                return item
        if str(item["match"]) in normalized:
            return item
    return None


def _calendar_release_type(release_title: Any, release_types: Sequence[dict[str, Any]]) -> dict[str, str] | None:
    normalized = _clean_text(release_title).lower()
    for item in release_types:
        terms = [str(item["match"])] + [str(alias) for alias in item.get("aliases", [])]
        for term in terms:
            cleaned = term.lower().strip()
            if cleaned and cleaned in normalized:
                return {str(key): str(value) for key, value in item.items() if key != "aliases"}
    return None


def _reference_period_from_release_title(release_title: str) -> str | None:
    match = re.search(r"\bfor\s+(.+)$", release_title, flags=re.IGNORECASE)
    return _clean_text(match.group(1)) if match else None


def _macro_event_row(
    *,
    event_date: str,
    event_type: str,
    title: str,
    source: str,
    source_url: str,
    release_time_et: str | None,
    event_family: str = "macro",
    event_subtype: str | None = None,
    universe_scope: str = "official_macro",
    source_authority: str = "official",
    confidence: float = 0.95,
    raw_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(raw_payload or {})
    payload.setdefault("release_time_et", release_time_et)
    payload.setdefault("event_date_basis", "official_release_date")
    payload = _json_safe_payload_value(payload)
    time_label = f"{release_time_et} ET" if release_time_et else None
    return {
        "event_date": event_date,
        "event_type": event_type,
        "event_family": event_family,
        "event_subtype": event_subtype or _event_subtype_from_type(event_type),
        "event_time_label": time_label,
        "event_datetime_utc": _event_datetime_utc_from_eastern_time(event_date, release_time_et),
        "universe_scope": universe_scope,
        "source_authority": source_authority,
        "symbol": None,
        "title": title,
        "source": source,
        "source_type": "official",
        "validation_status": "official",
        "event_status": "active",
        "source_url": source_url,
        "confidence": confidence,
        "raw_payload": payload,
    }


def parse_bls_macro_calendar_events_from_html(
    html: str,
    *,
    source_url: str,
    year: int,
) -> list[dict[str, Any]]:
    events: list[dict[str, Any]] = []
    for record in _frame_records_from_html_table(html):
        release_title = _clean_text(_record_value_by_hint(record, ["release"], fallback_index=2))
        release_type = _bls_macro_release_type(release_title)
        if not release_type:
            continue
        date_time_text = _record_value_by_hint(record, ["date", "time"], fallback_index=0)
        event_date, release_time = _parse_release_date_time(date_time_text, default_year=year)
        if not event_date:
            continue
        label = release_type["label"]
        events.append(
            _macro_event_row(
                event_date=event_date,
                event_type=release_type["event_type"],
                title=f"{label}: {release_title}",
                source=BLS_MACRO_CALENDAR_SOURCE,
                source_url=source_url,
                release_time_et=release_time,
                raw_payload={
                    "agency": "BLS",
                    "calendar_year": year,
                    "release_title": release_title,
                    "reference_period": _reference_period_from_release_title(release_title),
                    "release_time_et": release_time,
                    "source_row": record,
                },
            )
        )
    return events


def _decode_ics_text(value: Any) -> str:
    text = str(value or "")
    return (
        text.replace("\\n", " ")
        .replace("\\N", " ")
        .replace("\\,", ",")
        .replace("\\;", ";")
        .replace("\\\\", "\\")
    )


def _unfold_ics_lines(ics_text: str) -> list[str]:
    lines: list[str] = []
    for line in str(ics_text or "").replace("\r\n", "\n").replace("\r", "\n").split("\n"):
        if line.startswith((" ", "\t")) and lines:
            lines[-1] += line[1:]
        elif line:
            lines.append(line)
    return lines


def _parse_ics_property(line: str) -> tuple[str, dict[str, str], str] | None:
    if ":" not in line:
        return None
    key_text, value = line.split(":", 1)
    parts = key_text.split(";")
    name = parts[0].strip().upper()
    if not name:
        return None
    params: dict[str, str] = {}
    for part in parts[1:]:
        if "=" in part:
            param_name, param_value = part.split("=", 1)
            params[param_name.strip().upper()] = param_value.strip().strip('"')
    return name, params, value.strip()


def _parse_ics_events(ics_text: str) -> list[dict[str, dict[str, Any]]]:
    events: list[dict[str, dict[str, Any]]] = []
    current: dict[str, dict[str, Any]] | None = None
    for line in _unfold_ics_lines(ics_text):
        upper_line = line.strip().upper()
        if upper_line == "BEGIN:VEVENT":
            current = {}
            continue
        if upper_line == "END:VEVENT":
            if current:
                events.append(current)
            current = None
            continue
        if current is None:
            continue
        parsed = _parse_ics_property(line)
        if not parsed:
            continue
        name, params, raw_value = parsed
        current[name] = {
            "raw": raw_value,
            "value": _clean_text(_decode_ics_text(raw_value)),
            "params": params,
        }
    return events


def _parse_ics_dtstart(prop: dict[str, Any] | None) -> tuple[str | None, str | None]:
    if not prop:
        return None, None
    raw_value = str(prop.get("raw") or "").strip()
    params = {str(key).upper(): str(value) for key, value in dict(prop.get("params") or {}).items()}
    if not raw_value:
        return None, None
    if params.get("VALUE", "").upper() == "DATE" or re.fullmatch(r"\d{8}", raw_value):
        try:
            return datetime.strptime(raw_value[:8], "%Y%m%d").date().isoformat(), None
        except ValueError:
            return None, None
    value = raw_value.rstrip("Z")
    parsed: datetime | None = None
    for pattern in ("%Y%m%dT%H%M%S", "%Y%m%dT%H%M"):
        try:
            parsed = datetime.strptime(value, pattern)
            break
        except ValueError:
            continue
    if parsed is None:
        return None, None
    if raw_value.endswith("Z"):
        eastern = parsed.replace(tzinfo=UTC).astimezone(ZoneInfo("America/New_York"))
        return eastern.date().isoformat(), eastern.strftime("%H:%M")
    tzid = params.get("TZID")
    if tzid:
        try:
            localized = parsed.replace(tzinfo=ZoneInfo(tzid))
            return localized.date().isoformat(), localized.strftime("%H:%M")
        except Exception:
            pass
    return parsed.date().isoformat(), parsed.strftime("%H:%M")


def parse_bls_macro_calendar_events_from_ics(
    ics_text: str,
    *,
    source_url: str = BLS_MACRO_CALENDAR_ICS_SOURCE_URL,
    years: Sequence[int] | None = None,
    source_name: str | None = None,
) -> list[dict[str, Any]]:
    year_filter = {int(year) for year in years or []}
    events: list[dict[str, Any]] = []
    for item in _parse_ics_events(ics_text):
        summary = _clean_text((item.get("SUMMARY") or {}).get("value"))
        description = _clean_text((item.get("DESCRIPTION") or {}).get("value"))
        release_text = summary or description
        release_type = _bls_macro_release_type(f"{summary} {description}")
        if not release_type or not release_text:
            continue
        event_date, release_time = _parse_ics_dtstart(item.get("DTSTART"))
        if not event_date:
            continue
        event_year = int(event_date[:4])
        if year_filter and event_year not in year_filter:
            continue
        label = release_type["label"]
        events.append(
            _macro_event_row(
                event_date=event_date,
                event_type=release_type["event_type"],
                title=f"{label}: {release_text}",
                source=BLS_MACRO_CALENDAR_SOURCE,
                source_url=source_url,
                release_time_et=release_time,
                raw_payload={
                    "agency": "BLS",
                    "calendar_year": event_year,
                    "release_title": release_text,
                    "reference_period": _reference_period_from_release_title(release_text),
                    "release_time_et": release_time,
                    "source_file_name": source_name,
                    "import_method": "official_ics_file",
                    "ics_uid": (item.get("UID") or {}).get("value"),
                    "ics_dtstart": (item.get("DTSTART") or {}).get("raw"),
                    "ics_summary": summary,
                },
            )
        )
    return events


def collect_and_store_bls_macro_calendar_ics(
    ics_text: str,
    *,
    years: Sequence[int] | None = None,
    source_url: str = BLS_MACRO_CALENDAR_ICS_SOURCE_URL,
    source_name: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    collected_at = _timestamp_str()
    events = parse_bls_macro_calendar_events_from_ics(
        ics_text,
        source_url=source_url,
        years=years,
        source_name=source_name,
    )
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No BLS macro calendar events were parsed from ICS{year_text}.")
    rows = [{**row, "collected_at": collected_at} for row in events]
    rows_written = upsert_market_event_rows(rows, host=host, user=user, password=password, port=port)
    event_dates = sorted({str(row["event_date"]) for row in rows if row.get("event_date")})
    event_types = sorted({str(row["event_type"]) for row in rows if row.get("event_type")})
    return {
        "source": BLS_MACRO_CALENDAR_SOURCE,
        "source_url": source_url,
        "event_type": "MACRO",
        "method": "official_ics_file",
        "years_requested": [int(year) for year in years] if years else None,
        "source_name": source_name,
        "events_found": len(rows),
        "rows_written": rows_written,
        "event_dates": event_dates,
        "event_types": event_types,
        "collected_at": collected_at,
    }


def _bea_schedule_year_from_records(records: list[dict[str, Any]]) -> int | None:
    for record in records:
        for key in record:
            match = re.search(r"\b(20\d{2})\b", _clean_text(key))
            if match:
                return int(match.group(1))
    return None


def _is_bea_gdp_release(release_title: Any) -> bool:
    normalized = _clean_text(release_title).lower()
    if not normalized:
        return False
    if "gross domestic product by state" in normalized or "gross domestic product by county" in normalized:
        return False
    if "gdp by state" in normalized or "gdp by county" in normalized:
        return False
    return "gross domestic product" in normalized or normalized.startswith("gdp ")


def _bea_macro_release_type(release_title: Any) -> dict[str, str] | None:
    normalized = _clean_text(release_title).lower()
    if _is_bea_gdp_release(release_title):
        return {"event_type": "MACRO_GDP", "label": "GDP"}
    if "personal income and outlays" in normalized:
        return {"event_type": "MACRO_PCE", "label": "PCE"}
    return None


def parse_bea_macro_calendar_events_from_html(
    html: str,
    *,
    source_url: str = BEA_MACRO_CALENDAR_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    records = _frame_records_from_html_table(html)
    default_year = _bea_schedule_year_from_records(records)
    year_filter = {int(year) for year in years or []}
    events: list[dict[str, Any]] = []
    for record in records:
        release_title = _clean_text(_record_value_by_hint(record, ["release"], fallback_index=2))
        release_type = _bea_macro_release_type(release_title)
        if not release_type:
            continue
        date_time_text = _record_value_by_hint(record, ["year", "date"], fallback_index=0)
        event_date, release_time = _parse_release_date_time(date_time_text, default_year=default_year)
        if not event_date:
            continue
        event_year = int(event_date[:4])
        if year_filter and event_year not in year_filter:
            continue
        events.append(
            _macro_event_row(
                event_date=event_date,
                event_type=release_type["event_type"],
                title=f"{release_type['label']}: {release_title}",
                source=BEA_MACRO_CALENDAR_SOURCE,
                source_url=source_url,
                release_time_et=release_time,
                raw_payload={
                    "agency": "BEA",
                    "calendar_year": event_year,
                    "release_title": release_title,
                    "release_time_et": release_time,
                    "source_row": record,
                },
            )
        )
    return events


def parse_bea_gdp_calendar_events_from_html(
    html: str,
    *,
    source_url: str = BEA_MACRO_CALENDAR_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    return [
        row
        for row in parse_bea_macro_calendar_events_from_html(html, source_url=source_url, years=years)
        if row.get("event_type") == "MACRO_GDP"
    ]


def parse_census_macro_calendar_events_from_html(
    html: str,
    *,
    source_url: str = CENSUS_ECONOMIC_INDICATORS_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    year_filter = {int(year) for year in years or []}
    events: list[dict[str, Any]] = []
    for record in _frame_records_from_html_table(html):
        release_title = _clean_text(
            _record_value_by_hint(record, ["indicator", "name", "title"], fallback_index=2)
        )
        release_type = _calendar_release_type(release_title, CENSUS_MACRO_RELEASE_TYPES)
        if not release_type:
            continue
        date_text = _record_value_by_hint(record, ["release date", "date"], fallback_index=0)
        time_text = _record_value_by_hint(record, ["time"], fallback_index=1)
        event_date, release_time = _parse_release_date_time(f"{date_text or ''} {time_text or ''}")
        if not event_date:
            continue
        event_year = int(event_date[:4])
        if year_filter and event_year not in year_filter:
            continue
        events.append(
            _macro_event_row(
                event_date=event_date,
                event_type=release_type["event_type"],
                title=f"{release_type['label']}: {release_title}",
                source=CENSUS_ECONOMIC_INDICATORS_SOURCE,
                source_url=source_url,
                release_time_et=release_time,
                raw_payload={
                    "agency": "Census",
                    "calendar_year": event_year,
                    "release_title": release_title,
                    "release_time_et": release_time,
                    "source_row": record,
                },
            )
        )
    return events


def parse_ism_macro_calendar_events_from_html(
    html: str,
    *,
    source_url: str = ISM_REPORT_CALENDAR_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    year_filter = {int(year) for year in years or []}
    events: list[dict[str, Any]] = []
    for record in _frame_records_from_html_table(html):
        release_title = _clean_text(_record_value_by_hint(record, ["report", "release"], fallback_index=0))
        release_type = _calendar_release_type(release_title, ISM_MACRO_RELEASE_TYPES)
        if not release_type:
            continue
        date_text = _record_value_by_hint(record, ["release date", "date"], fallback_index=1)
        time_text = _record_value_by_hint(record, ["time"], fallback_index=2)
        event_date, release_time = _parse_release_date_time(f"{date_text or ''} {time_text or ''}")
        if not event_date:
            continue
        event_year = int(event_date[:4])
        if year_filter and event_year not in year_filter:
            continue
        events.append(
            _macro_event_row(
                event_date=event_date,
                event_type=release_type["event_type"],
                title=f"{release_type['label']}: {release_title}",
                source=ISM_REPORT_CALENDAR_SOURCE,
                source_url=source_url,
                release_time_et=release_time,
                raw_payload={
                    "agency": "ISM",
                    "calendar_year": event_year,
                    "release_title": release_title,
                    "release_time_et": release_time,
                    "source_row": record,
                },
            )
        )
    return events


def parse_treasury_auction_calendar_events_from_html(
    html: str,
    *,
    source_url: str = TREASURY_AUCTIONS_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    year_filter = {int(year) for year in years or []}
    events: list[dict[str, Any]] = []
    for record in _frame_records_from_html_table(html):
        auction_date_text = _record_value_by_hint(record, ["auction date"], fallback_index=2)
        event_date, release_time = _parse_release_date_time(auction_date_text)
        if not event_date:
            continue
        event_year = int(event_date[:4])
        if year_filter and event_year not in year_filter:
            continue
        security_type = _clean_text(_record_value_by_hint(record, ["security type", "security"], fallback_index=0))
        term = _clean_text(_record_value_by_hint(record, ["term"], fallback_index=1))
        title_detail = " ".join(item for item in [term, security_type] if item).strip() or "Treasury security"
        events.append(
            _macro_event_row(
                event_date=event_date,
                event_type="TREASURY_AUCTION",
                title=f"Treasury Auction: {title_detail}",
                source=TREASURY_AUCTIONS_SOURCE,
                source_url=source_url,
                release_time_et=release_time,
                event_family="fixed_income",
                event_subtype="treasury_auction",
                universe_scope="official_macro",
                raw_payload={
                    "agency": "TreasuryDirect",
                    "calendar_year": event_year,
                    "security_type": security_type,
                    "term": term,
                    "auction_date": event_date,
                    "source_row": record,
                },
            )
        )
    return events


def _market_structure_event_row(
    *,
    event_date: str,
    event_type: str,
    title: str,
    source: str,
    source_url: str,
    event_subtype: str | None = None,
    event_time_label: str | None = None,
    release_time_et: str | None = None,
    confidence: float = 0.95,
    raw_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    return {
        "event_date": event_date,
        "event_type": event_type,
        "event_family": "market_structure",
        "event_subtype": event_subtype or _event_subtype_from_type(event_type),
        "event_time_label": event_time_label,
        "event_datetime_utc": _event_datetime_utc_from_eastern_time(event_date, release_time_et),
        "universe_scope": "all_us",
        "source_authority": "official",
        "title": title,
        "source": source,
        "source_type": "official",
        "validation_status": "official",
        "event_status": "active",
        "source_url": source_url,
        "confidence": confidence,
        "raw_payload": raw_payload or {},
    }


def _holiday_status_from_text(text: str) -> tuple[str | None, str | None, str | None]:
    normalized = text.lower()
    if "early close" in normalized or "1:00" in normalized or "1 p.m" in normalized or "1pm" in normalized:
        return "EARLY_CLOSE", "Early close 13:00 ET", "13:00"
    if "closed" in normalized:
        return "MARKET_HOLIDAY", "Closed", None
    return None, None, None


def parse_nasdaq_market_holiday_calendar_events_from_html(
    html: str,
    *,
    source_url: str = NASDAQ_MARKET_HOLIDAY_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    year_filter = {int(year) for year in years or []}
    events: list[dict[str, Any]] = []
    for record in _frame_records_from_html_table(html):
        values = [_clean_text(value) for value in record.values() if _clean_text(value)]
        if not values:
            continue
        event_date = None
        date_text = ""
        for value in values:
            try:
                parsed = _event_date_str(re.sub(r"^[A-Za-z]+,\s*", "", value))
            except Exception:
                parsed = None
            if parsed:
                event_date = parsed
                date_text = value
                break
        if not event_date:
            continue
        event_year = int(event_date[:4])
        if year_filter and event_year not in year_filter:
            continue
        row_text = " ".join(values)
        event_type, event_time_label, release_time = _holiday_status_from_text(row_text)
        if not event_type:
            continue
        title_candidates = [
            value
            for value in values
            if value != date_text and not _holiday_status_from_text(value)[0]
        ]
        holiday_title = title_candidates[0] if title_candidates else "US Equity and Options Markets"
        title_prefix = "US Market Early Close" if event_type == "EARLY_CLOSE" else "US Market Holiday"
        events.append(
            _market_structure_event_row(
                event_date=event_date,
                event_type=event_type,
                title=f"{title_prefix}: {holiday_title}",
                source=NASDAQ_MARKET_HOLIDAY_SOURCE,
                source_url=source_url,
                event_subtype="early_close" if event_type == "EARLY_CLOSE" else "market_holiday",
                event_time_label=event_time_label,
                release_time_et=release_time,
                raw_payload={
                    "exchange": "Nasdaq Trader",
                    "calendar_year": event_year,
                    "holiday": holiday_title,
                    "market_status": event_time_label,
                    "source_row": record,
                },
            )
        )
    return events


def _previous_business_day(value: date, *, exchange_holidays: set[str]) -> date:
    current = value
    while current.weekday() >= 5 or current.isoformat() in exchange_holidays:
        current -= timedelta(days=1)
    return current


def _third_friday(year: int, month: int) -> date:
    fridays = [
        week[calendar.FRIDAY]
        for week in calendar.monthcalendar(year, month)
        if week[calendar.FRIDAY]
    ]
    return date(year, month, fridays[2])


def build_options_expiration_calendar_events(
    *,
    years: Sequence[int] | None = None,
    exchange_holidays: set[str] | Sequence[str] | None = None,
    source_url_template: str = CBOE_OPTIONS_EXPIRATION_SOURCE_URL_TEMPLATE,
) -> list[dict[str, Any]]:
    target_years = [int(year) for year in years] if years else [datetime.now(UTC).year]
    holiday_set = {str(item) for item in exchange_holidays or []}
    events: list[dict[str, Any]] = []
    for year in target_years:
        source_url = source_url_template.format(year=year)
        for month in range(1, 13):
            scheduled = _third_friday(year, month)
            adjusted = _previous_business_day(scheduled, exchange_holidays=holiday_set)
            is_quarter_month = month in {3, 6, 9, 12}
            events.append(
                _market_structure_event_row(
                    event_date=adjusted.isoformat(),
                    event_type="OPTIONS_EXPIRATION",
                    title=(
                        "Quarterly Options Expiration / Triple Witch"
                        if is_quarter_month
                        else "Monthly Options Expiration"
                    ),
                    source=CBOE_OPTIONS_EXPIRATION_SOURCE,
                    source_url=source_url,
                    event_subtype="triple_witch" if is_quarter_month else "options_expiration",
                    event_time_label="Market close ET",
                    release_time_et="16:00",
                    confidence=0.9,
                    raw_payload={
                        "exchange": "Cboe",
                        "calendar_year": year,
                        "scheduled_expiration_date": scheduled.isoformat(),
                        "holiday_adjusted": adjusted != scheduled,
                        "calculation_basis": "third_friday_standard_options_expiration",
                        "source_url_template": source_url_template,
                    },
                )
            )
    return events


def _month_day_dates_from_text(text: str, *, year: int) -> list[str]:
    patterns = [
        r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?[,]?\s*([A-Za-z]+)\s+(\d{1,2})(?:st|nd|rd|th)?",
        r"(?:Monday|Tuesday|Wednesday|Thursday|Friday|Saturday|Sunday)?[,]?\s*(\d{1,2})(?:st|nd|rd|th)?\s+([A-Za-z]+)",
    ]
    dates: list[str] = []
    seen: set[str] = set()
    for pattern in patterns:
        for match in re.finditer(pattern, text, flags=re.IGNORECASE):
            first, second = match.groups()
            if first.isdigit():
                day = int(first)
                month_name = second
            else:
                month_name = first
                day = int(second)
            month = MONTH_NAME_TO_NUMBER.get(month_name.upper())
            if not month:
                continue
            try:
                parsed = date(year, month, day).isoformat()
            except ValueError:
                continue
            if parsed not in seen:
                seen.add(parsed)
                dates.append(parsed)
    return dates


def parse_russell_reconstitution_events_from_html(
    html: str,
    *,
    source_url: str = FTSE_RUSSELL_RECONSTITUTION_SOURCE_URL,
    years: Sequence[int] | None = None,
) -> list[dict[str, Any]]:
    text = _clean_text(BeautifulSoup(html, "html.parser").get_text(" "))
    detected_years = sorted({int(item) for item in re.findall(r"\b(20\d{2})\b", text)})
    target_years = [int(year) for year in years] if years else detected_years or [datetime.now(UTC).year]
    events: list[dict[str, Any]] = []
    for year in target_years:
        sentences = re.split(r"(?<=[.!?])\s+", text)
        for sentence in sentences:
            normalized = sentence.lower()
            dates = _month_day_dates_from_text(sentence, year=year)
            if not dates:
                continue
            if "rank day" in normalized:
                events.append(
                    _market_structure_event_row(
                        event_date=dates[0],
                        event_type="RUSSELL_RECONSTITUTION",
                        title="Russell US Index Rank Day",
                        source=FTSE_RUSSELL_RECONSTITUTION_SOURCE,
                        source_url=source_url,
                        event_subtype="russell_rank_day",
                        raw_payload={"provider": "FTSE Russell", "calendar_year": year, "source_sentence": sentence},
                    )
                )
            elif "preliminary" in normalized and ("list" in normalized or "membership" in normalized):
                events.append(
                    _market_structure_event_row(
                        event_date=dates[0],
                        event_type="RUSSELL_RECONSTITUTION",
                        title="Russell US Index Preliminary Additions/Deletions",
                        source=FTSE_RUSSELL_RECONSTITUTION_SOURCE,
                        source_url=source_url,
                        event_subtype="russell_preliminary_lists",
                        event_time_label="After market close ET",
                        release_time_et="18:00",
                        raw_payload={"provider": "FTSE Russell", "calendar_year": year, "source_sentence": sentence},
                    )
                )
            elif "update" in normalized and ("provided" in normalized or "post" in normalized or "list" in normalized):
                for event_date in dates:
                    events.append(
                        _market_structure_event_row(
                            event_date=event_date,
                            event_type="RUSSELL_RECONSTITUTION",
                            title="Russell US Index Reconstitution Update",
                            source=FTSE_RUSSELL_RECONSTITUTION_SOURCE,
                            source_url=source_url,
                            event_subtype="russell_update",
                            event_time_label="After market close ET",
                            release_time_et="18:00",
                            raw_payload={"provider": "FTSE Russell", "calendar_year": year, "source_sentence": sentence},
                        )
                    )
            elif "take effect" in normalized or "effective" in normalized or "reconstituted indexes" in normalized:
                events.append(
                    _market_structure_event_row(
                        event_date=dates[-1],
                        event_type="RUSSELL_RECONSTITUTION",
                        title="Russell US Index Reconstitution Effective",
                        source=FTSE_RUSSELL_RECONSTITUTION_SOURCE,
                        source_url=source_url,
                        event_subtype="russell_reconstitution",
                        event_time_label="After market close ET",
                        release_time_et="16:00",
                        raw_payload={"provider": "FTSE Russell", "calendar_year": year, "source_sentence": sentence},
                    )
                )
    deduped: list[dict[str, Any]] = []
    seen_keys: set[tuple[str, str]] = set()
    for row in sorted(events, key=lambda item: (str(item.get("event_date") or ""), str(item.get("event_subtype") or ""))):
        key = (str(row.get("event_date") or ""), str(row.get("event_subtype") or ""))
        if key in seen_keys:
            continue
        seen_keys.add(key)
        deduped.append(row)
    return deduped


def fetch_bls_macro_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url_template: str = BLS_MACRO_CALENDAR_SOURCE_URL_TEMPLATE,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    target_years = [int(year) for year in years] if years else [datetime.now(UTC).year]
    fetcher = html_fetcher or _fetch_html
    events: list[dict[str, Any]] = []
    for year in target_years:
        source_url = source_url_template.format(year=year)
        html = fetcher(source_url)
        events.extend(parse_bls_macro_calendar_events_from_html(html, source_url=source_url, year=year))
    if not events:
        raise RuntimeError(f"No BLS macro calendar events were parsed for years {target_years}.")
    return events


def fetch_bea_gdp_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = BEA_MACRO_CALENDAR_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_bea_gdp_calendar_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No BEA GDP calendar events were parsed{year_text}.")
    return events


def fetch_bea_macro_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = BEA_MACRO_CALENDAR_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_bea_macro_calendar_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No BEA macro calendar events were parsed{year_text}.")
    return events


def fetch_census_macro_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = CENSUS_ECONOMIC_INDICATORS_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_census_macro_calendar_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No Census economic indicator calendar events were parsed{year_text}.")
    return events


def fetch_ism_macro_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = ISM_REPORT_CALENDAR_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_ism_macro_calendar_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No ISM report calendar events were parsed{year_text}.")
    return events


def fetch_treasury_auction_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = TREASURY_AUCTIONS_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_treasury_auction_calendar_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No Treasury auction calendar events were parsed{year_text}.")
    return events


def fetch_nasdaq_market_holiday_calendar_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = NASDAQ_MARKET_HOLIDAY_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_nasdaq_market_holiday_calendar_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No Nasdaq Trader market holiday events were parsed{year_text}.")
    return events


def fetch_russell_reconstitution_events(
    *,
    years: Sequence[int] | None = None,
    source_url: str = FTSE_RUSSELL_RECONSTITUTION_SOURCE_URL,
    html_fetcher: Callable[[str], str] | None = None,
) -> list[dict[str, Any]]:
    fetcher = html_fetcher or _fetch_html
    events = parse_russell_reconstitution_events_from_html(fetcher(source_url), source_url=source_url, years=years)
    if not events:
        year_text = f" for years {list(years)}" if years else ""
        raise RuntimeError(f"No Russell reconstitution events were parsed{year_text}.")
    return events


def fetch_market_structure_calendar_events(
    *,
    years: Sequence[int] | None = None,
    include_holidays: bool = True,
    include_options_expiration: bool = True,
    include_russell: bool = True,
    holiday_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    russell_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    options_builder: Callable[..., list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    target_years = tuple(int(year) for year in years) if years else (datetime.now(UTC).year,)
    events: list[dict[str, Any]] = []
    failed_sources: list[str] = []
    exchange_holidays: set[str] = set()

    if include_holidays:
        try:
            fetcher = holiday_fetcher or fetch_nasdaq_market_holiday_calendar_events
            holiday_events = fetcher(years=target_years)
            events.extend(holiday_events)
            exchange_holidays = {
                str(row.get("event_date"))
                for row in holiday_events
                if row.get("event_type") == "MARKET_HOLIDAY" and row.get("event_date")
            }
        except Exception as exc:
            failed_sources.append(f"Nasdaq Trader: {exc}")
    if include_options_expiration:
        try:
            builder = options_builder or build_options_expiration_calendar_events
            events.extend(builder(years=target_years, exchange_holidays=exchange_holidays))
        except Exception as exc:
            failed_sources.append(f"Cboe: {exc}")
    if include_russell:
        try:
            fetcher = russell_fetcher or fetch_russell_reconstitution_events
            events.extend(fetcher(years=target_years))
        except Exception as exc:
            failed_sources.append(f"FTSE Russell: {exc}")

    return {
        "source": MARKET_STRUCTURE_CALENDAR_SOURCE,
        "source_url": NASDAQ_MARKET_HOLIDAY_SOURCE_URL,
        "event_type": "MARKET_STRUCTURE",
        "method": "official_market_structure_calendar_sources",
        "years": list(target_years),
        "include_holidays": include_holidays,
        "include_options_expiration": include_options_expiration,
        "include_russell": include_russell,
        "events": events,
        "events_found": len(events),
        "failed_sources": failed_sources,
    }


def fetch_macro_calendar_events(
    *,
    years: Sequence[int] | None = None,
    include_bls: bool = True,
    include_bea: bool = True,
    include_census: bool = True,
    include_ism: bool = True,
    include_treasury: bool = True,
    bls_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    bea_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    census_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    ism_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    treasury_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    events: list[dict[str, Any]] = []
    failed_sources: list[str] = []
    if include_bls:
        try:
            fetcher = bls_fetcher or fetch_bls_macro_calendar_events
            events.extend(fetcher(years=years))
        except Exception as exc:
            failed_sources.append(f"BLS: {exc}")
    if include_bea:
        try:
            fetcher = bea_fetcher or fetch_bea_macro_calendar_events
            events.extend(fetcher(years=years))
        except Exception as exc:
            failed_sources.append(f"BEA: {exc}")
    if include_census:
        try:
            fetcher = census_fetcher or fetch_census_macro_calendar_events
            events.extend(fetcher(years=years))
        except Exception as exc:
            failed_sources.append(f"Census: {exc}")
    if include_ism:
        try:
            fetcher = ism_fetcher or fetch_ism_macro_calendar_events
            events.extend(fetcher(years=years))
        except Exception as exc:
            failed_sources.append(f"ISM: {exc}")
    if include_treasury:
        try:
            fetcher = treasury_fetcher or fetch_treasury_auction_calendar_events
            events.extend(fetcher(years=years))
        except Exception as exc:
            failed_sources.append(f"Treasury: {exc}")
    if not events:
        detail = "; ".join(failed_sources) if failed_sources else "no enabled source returned events"
        raise RuntimeError(f"No macro calendar events were collected: {detail}")
    target_year = int(years[0]) if years else datetime.now(UTC).year
    return {
        "source": MACRO_CALENDAR_SOURCE,
        "source_url": ", ".join(
            [
                item
                for item in [
                    BLS_MACRO_CALENDAR_SOURCE_URL_TEMPLATE.format(
                        year=target_year
                    )
                    if include_bls
                    else None,
                    BEA_MACRO_CALENDAR_SOURCE_URL if include_bea else None,
                    CENSUS_ECONOMIC_INDICATORS_SOURCE_URL if include_census else None,
                    ISM_REPORT_CALENDAR_SOURCE_URL if include_ism else None,
                    TREASURY_AUCTIONS_SOURCE_URL if include_treasury else None,
                ]
                if item
            ]
        ),
        "event_type": "MACRO",
        "method": "official_html",
        "years_requested": [int(year) for year in years] if years else None,
        "events": events,
        "events_found": len(events),
        "failed_sources": failed_sources,
    }


def collect_and_store_macro_calendar(
    *,
    years: Sequence[int] | None = None,
    include_bls: bool = True,
    include_bea: bool = True,
    include_census: bool = True,
    include_ism: bool = True,
    include_treasury: bool = True,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    macro_fetcher: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Collect official macro release dates and persist them to the common event calendar."""
    collected_at = _timestamp_str()
    fetcher = macro_fetcher or fetch_macro_calendar_events
    result = fetcher(
        years=years,
        include_bls=include_bls,
        include_bea=include_bea,
        include_census=include_census,
        include_ism=include_ism,
        include_treasury=include_treasury,
    )
    events = [{**row, "collected_at": collected_at} for row in result.get("events", [])]
    rows_written = upsert_market_event_rows(events, host=host, user=user, password=password, port=port)
    event_dates = sorted({str(row["event_date"]) for row in events if row.get("event_date")})
    event_types = sorted({str(row["event_type"]) for row in events if row.get("event_type")})
    return {
        **result,
        "rows_written": rows_written,
        "event_dates": event_dates,
        "event_types": event_types,
        "include_bls": include_bls,
        "include_bea": include_bea,
        "include_census": include_census,
        "include_ism": include_ism,
        "include_treasury": include_treasury,
        "collected_at": collected_at,
    }


def collect_and_store_market_structure_calendar(
    *,
    years: Sequence[int] | None = None,
    include_holidays: bool = True,
    include_options_expiration: bool = True,
    include_russell: bool = True,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    market_structure_fetcher: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Collect market-structure dates that explain trading-calendar density, not signals."""
    collected_at = _timestamp_str()
    target_years = tuple(int(year) for year in years) if years else None
    fetcher = market_structure_fetcher or fetch_market_structure_calendar_events
    result = fetcher(
        years=target_years,
        include_holidays=include_holidays,
        include_options_expiration=include_options_expiration,
        include_russell=include_russell,
    )
    events = [{**row, "collected_at": collected_at} for row in result.get("events", [])]
    rows_written = upsert_market_event_rows(events, host=host, user=user, password=password, port=port)
    event_dates = sorted({str(row["event_date"]) for row in events if row.get("event_date")})
    event_types = sorted({str(row["event_type"]) for row in events if row.get("event_type")})
    return {
        **result,
        "rows_written": rows_written,
        "event_dates": event_dates,
        "event_types": event_types,
        "include_holidays": include_holidays,
        "include_options_expiration": include_options_expiration,
        "include_russell": include_russell,
        "collected_at": collected_at,
    }


def load_latest_intraday_mover_symbols(
    *,
    universe_code: str = "SP500",
    universe_limit: int | None = None,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    top_n: int = 20,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[str]:
    """Return top positive movers from the latest stored intraday snapshot."""
    normalized_universe, _ = _normalize_intraday_universe(universe_code, universe_limit)
    bounded_top_n = max(1, min(int(top_n or 20), 200))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        sync_table_schema(
            db,
            "market_intraday_snapshot",
            MARKET_INTELLIGENCE_SCHEMAS["market_intraday_snapshot"],
            DB_PRICE,
        )
        rows = db.query(
            """
            SELECT s.symbol
            FROM market_intraday_snapshot s
            JOIN (
                SELECT MAX(snapshot_time_utc) AS snapshot_time_utc
                FROM market_intraday_snapshot
                WHERE universe_code = %s
                  AND interval_code = %s
            ) latest
              ON latest.snapshot_time_utc = s.snapshot_time_utc
            WHERE s.universe_code = %s
              AND s.interval_code = %s
              AND s.provider_status = %s
              AND s.return_pct IS NOT NULL
            ORDER BY s.return_pct DESC, s.symbol ASC
            LIMIT %s
            """,
            [normalized_universe, interval, normalized_universe, interval, "ok", bounded_top_n],
        )
    finally:
        db.close()
    return _normalize_symbol_list([row.get("symbol") for row in rows], max_symbols=bounded_top_n)


def _calendar_mapping(value: Any) -> dict[str, Any]:
    if isinstance(value, pd.DataFrame):
        return value.to_dict(orient="list")
    if isinstance(value, pd.Series):
        return value.to_dict()
    if isinstance(value, dict):
        return dict(value)
    return {}


def _calendar_value(mapping: dict[str, Any], *keys: str) -> Any:
    for wanted in keys:
        for key, value in mapping.items():
            if str(key).strip().lower().replace(" ", "_") == wanted.lower().replace(" ", "_"):
                return value
    return None


def _event_date_values(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str) and not value.strip():
        return []
    if isinstance(value, (pd.Series, pd.Index)):
        values = list(value)
    elif isinstance(value, (list, tuple, set)):
        values = list(value)
    else:
        values = [value]
    out: list[str] = []
    seen: set[str] = set()
    for item in values:
        event_date = _event_date_str(item)
        if event_date and event_date not in seen:
            seen.add(event_date)
            out.append(event_date)
    return out


def _earnings_symbol_diagnostic(
    *,
    symbol: str,
    status: str,
    reason: str,
    detail: str,
    event_dates: Sequence[str] | None = None,
    provider_dates: Sequence[str] | None = None,
) -> dict[str, Any]:
    return {
        "symbol": _normalize_symbol(symbol),
        "status": status,
        "reason": reason,
        "detail": detail,
        "event_dates": list(event_dates or []),
        "provider_dates": list(provider_dates or []),
    }


def _earnings_reason_counts(
    diagnostics: Sequence[dict[str, Any]],
    *,
    statuses: set[str],
) -> dict[str, int]:
    counts = Counter(
        str(item.get("reason") or "unknown")
        for item in diagnostics
        if str(item.get("status") or "") in statuses
    )
    return dict(sorted(counts.items()))


def _parse_window_date(value: Any, *, default: date) -> date:
    parsed = _event_date_str(value)
    if not parsed:
        return default
    return datetime.strptime(parsed, "%Y-%m-%d").date()


def _earnings_source_authority(validation_status: str | None) -> str:
    normalized = str(validation_status or "").strip().lower()
    if normalized == "cross_checked":
        return "cross_checked"
    if normalized == "not_confirmed":
        return "not_confirmed"
    if normalized == "conflict":
        return "conflict"
    return "provider_estimate"


def _fetch_json(source_url: str, *, timeout: int = 20) -> dict[str, Any]:
    request = Request(
        source_url,
        headers={
            "User-Agent": (
                "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
                "AppleWebKit/537.36 (KHTML, like Gecko) Chrome/125.0 Safari/537.36"
            ),
            "Accept": "application/json, text/plain, */*",
            "Origin": "https://www.nasdaq.com",
            "Referer": "https://www.nasdaq.com/market-activity/earnings",
        },
    )
    with urlopen(request, timeout=timeout) as response:
        return json.loads(response.read().decode("utf-8", errors="replace"))


def _parse_nasdaq_earnings_rows(payload: dict[str, Any]) -> list[dict[str, Any]]:
    data = payload.get("data") if isinstance(payload, dict) else None
    rows = data.get("rows") if isinstance(data, dict) else None
    if not isinstance(rows, list):
        return []
    parsed: list[dict[str, Any]] = []
    for item in rows:
        if not isinstance(item, dict):
            continue
        symbol = _normalize_symbol(item.get("symbol"))
        if not symbol:
            continue
        parsed.append(
            {
                "symbol": symbol,
                "name": item.get("name"),
                "time": item.get("time"),
                "fiscalQuarterEnding": item.get("fiscalQuarterEnding"),
                "epsForecast": item.get("epsForecast"),
                "noOfEsts": item.get("noOfEsts"),
            }
        )
    return parsed


def fetch_nasdaq_earnings_calendar_by_date(
    event_date: str | date,
    *,
    source_url: str = NASDAQ_EARNINGS_CALENDAR_API_URL,
    http_json_fetcher: Callable[[str], dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_date = _event_date_str(event_date)
    if not normalized_date:
        return {"event_date": None, "symbols": [], "rows": [], "source_url": source_url}
    request_url = f"{source_url}?date={normalized_date}"
    fetcher = http_json_fetcher or _fetch_json
    payload = fetcher(request_url)
    rows = _parse_nasdaq_earnings_rows(payload)
    symbols = sorted({row["symbol"] for row in rows if row.get("symbol")})
    return {
        "event_date": normalized_date,
        "symbols": symbols,
        "rows": rows,
        "source": NASDAQ_EARNINGS_CALENDAR_SOURCE,
        "source_url": request_url,
    }


def fetch_nasdaq_earnings_calendar_symbols_by_date(
    dates: Sequence[Any],
    *,
    max_dates: int = 20,
    request_sleep_sec: float = 0.1,
    date_fetcher: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, dict[str, Any]]:
    normalized_dates = []
    seen: set[str] = set()
    for item in dates:
        parsed = _event_date_str(item)
        if not parsed or parsed in seen:
            continue
        seen.add(parsed)
        normalized_dates.append(parsed)
        if len(normalized_dates) >= max(1, int(max_dates or 20)):
            break

    fetcher = date_fetcher or fetch_nasdaq_earnings_calendar_by_date
    out: dict[str, dict[str, Any]] = {}
    for index, item in enumerate(normalized_dates):
        try:
            result = fetcher(item)
            out[item] = {
                "symbols": list(result.get("symbols") or []),
                "source": result.get("source") or NASDAQ_EARNINGS_CALENDAR_SOURCE,
                "source_url": result.get("source_url"),
                "status": "ok",
            }
        except Exception as exc:
            out[item] = {
                "symbols": [],
                "source": NASDAQ_EARNINGS_CALENDAR_SOURCE,
                "source_url": f"{NASDAQ_EARNINGS_CALENDAR_API_URL}?date={item}",
                "status": "failed",
                "error": str(exc),
            }
        if request_sleep_sec > 0 and index < len(normalized_dates) - 1:
            sleep(float(request_sleep_sec))
    return out


def _earnings_source_validation_payload(
    *,
    symbol: str,
    event_date: str,
    nasdaq_by_date: dict[str, dict[str, Any]] | None,
) -> tuple[str, float, dict[str, Any]]:
    nasdaq_result = dict((nasdaq_by_date or {}).get(event_date) or {})
    nasdaq_symbols = {_normalize_symbol(item) for item in nasdaq_result.get("symbols") or []}
    checked = bool(nasdaq_result)
    matched = checked and symbol in nasdaq_symbols
    if matched:
        validation_status = "cross_checked"
        confidence = EARNINGS_CROSS_CHECKED_CONFIDENCE
    elif checked and nasdaq_result.get("status") == "ok":
        validation_status = "not_confirmed"
        confidence = EARNINGS_NOT_CONFIRMED_CONFIDENCE
    elif checked:
        validation_status = "estimate_only"
        confidence = EARNINGS_PROVIDER_ESTIMATE_CONFIDENCE
    else:
        validation_status = "estimate_only"
        confidence = EARNINGS_PROVIDER_ESTIMATE_CONFIDENCE
    payload = {
        "source_type": "provider_estimate",
        "validation_status": validation_status,
        "source_authority": _earnings_source_authority(validation_status),
        "fallback_order": [
            {
                "source": COMPANY_IR_EARNINGS_SOURCE,
                "source_type": "official",
                "status": "future_symbol_specific_parser",
                "confidence": 0.95,
            },
            {
                "source": NASDAQ_EARNINGS_CALENDAR_SOURCE,
                "source_type": "provider_estimate",
                "status": "checked" if checked else "not_requested",
                "matched": matched if checked else None,
                "source_url": nasdaq_result.get("source_url"),
                "confidence": EARNINGS_CROSS_CHECKED_CONFIDENCE,
            },
            {
                "source": EARNINGS_CALENDAR_SOURCE,
                "source_type": "provider_estimate",
                "status": "primary",
                "confidence": EARNINGS_PROVIDER_ESTIMATE_CONFIDENCE,
            },
        ],
    }
    return validation_status, confidence, payload


def fetch_yfinance_earnings_calendar_events(
    symbols: str | Sequence[Any],
    *,
    start_date: str | date | None = None,
    end_date: str | date | None = None,
    lookahead_days: int = 120,
    max_symbols: int = 100,
    universe_scope: str = "latest_movers",
    symbol_source: str = "latest_movers",
    validate_with_nasdaq: bool = False,
    nasdaq_fetcher: Callable[..., dict[str, dict[str, Any]]] | None = None,
    request_sleep_sec: float = 0.0,
    ticker_factory: Callable[[str], Any] | None = None,
) -> dict[str, Any]:
    """Build normalized earnings event rows from yfinance's lightweight calendar field."""
    today = datetime.now(UTC).date()
    window_start = _parse_window_date(start_date, default=today)
    window_end = _parse_window_date(
        end_date,
        default=window_start + timedelta(days=max(1, int(lookahead_days or 120))),
    )
    if window_end < window_start:
        window_end = window_start

    normalized_symbols = _normalize_symbol_list(symbols, max_symbols=max_symbols)
    normalized_symbol_source = normalize_earnings_symbol_source(symbol_source)
    normalized_universe_scope = _normalize_event_taxonomy_value(universe_scope) or earnings_universe_scope_for_source(
        normalized_symbol_source
    )
    source_authority = _earnings_source_authority("estimate_only")
    ticker_factory = ticker_factory or yf.Ticker
    events: list[dict[str, Any]] = []
    missing_symbols: list[str] = []
    failed_symbols: list[str] = []
    symbol_diagnostics: list[dict[str, Any]] = []

    for index, symbol in enumerate(normalized_symbols):
        try:
            ticker = ticker_factory(symbol)
            calendar_value = getattr(ticker, "calendar", None)
            calendar = _calendar_mapping(calendar_value() if callable(calendar_value) else calendar_value)
            earnings_dates = _event_date_values(
                _calendar_value(calendar, "Earnings Date", "earningsDate", "earnings_date")
            )
            in_window_dates = [
                item
                for item in earnings_dates
                if window_start <= datetime.strptime(item, "%Y-%m-%d").date() <= window_end
            ]
            if not in_window_dates:
                missing_symbols.append(symbol)
                if earnings_dates:
                    symbol_diagnostics.append(
                        _earnings_symbol_diagnostic(
                            symbol=symbol,
                            status="missing",
                            reason="outside_window",
                            detail=(
                                f"Provider returned earnings date(s), but none are within "
                                f"{window_start.isoformat()} to {window_end.isoformat()}."
                            ),
                            provider_dates=earnings_dates,
                        )
                    )
                else:
                    symbol_diagnostics.append(
                        _earnings_symbol_diagnostic(
                            symbol=symbol,
                            status="missing",
                            reason="no_provider_earnings_date",
                            detail="Provider calendar did not include an upcoming earnings date.",
                        )
                    )
                continue
            symbol_diagnostics.append(
                _earnings_symbol_diagnostic(
                    symbol=symbol,
                    status="event_found",
                    reason="ok",
                    detail="Provider calendar returned at least one earnings date in the selected window.",
                    event_dates=in_window_dates,
                    provider_dates=earnings_dates,
                )
            )
            for event_date in in_window_dates:
                events.append(
                    {
                        "event_date": event_date,
                        "event_type": "EARNINGS",
                        "event_family": "earnings",
                        "event_subtype": "earnings_release",
                        "universe_scope": normalized_universe_scope,
                        "source_authority": source_authority,
                        "symbol": symbol,
                        "title": f"{symbol} Earnings Release",
                        "source": EARNINGS_CALENDAR_SOURCE,
                        "source_type": "provider_estimate",
                        "validation_status": "estimate_only",
                        "event_status": "active",
                        "source_url": f"https://finance.yahoo.com/quote/{symbol}/analysis",
                        "confidence": EARNINGS_PROVIDER_ESTIMATE_CONFIDENCE,
                        "raw_payload": {
                            "provider": EARNINGS_CALENDAR_SOURCE,
                            "symbol_source": normalized_symbol_source,
                            "universe_scope": normalized_universe_scope,
                            "provider_calendar": calendar,
                            "provider_earnings_dates": earnings_dates,
                            "event_date_basis": "yfinance_calendar_earnings_date",
                            "window_start": window_start.isoformat(),
                            "window_end": window_end.isoformat(),
                            "source_url": EARNINGS_CALENDAR_SOURCE_URL,
                            "collection_quality": {
                                "symbol_status": "event_found",
                                "provider_date_count": len(earnings_dates),
                                "in_window_date_count": len(in_window_dates),
                            },
                            "source_validation": {
                                "source_type": "provider_estimate",
                                "validation_status": "estimate_only",
                                "source_authority": source_authority,
                            },
                        },
                    }
                )
        except Exception as exc:
            failed_symbols.append(symbol)
            symbol_diagnostics.append(
                _earnings_symbol_diagnostic(
                    symbol=symbol,
                    status="failed",
                    reason="provider_error",
                    detail=str(exc),
                )
            )
        if request_sleep_sec > 0 and index < len(normalized_symbols) - 1:
            sleep(float(request_sleep_sec))

    validation_source = "not_requested"
    if validate_with_nasdaq and events:
        fetcher = nasdaq_fetcher or fetch_nasdaq_earnings_calendar_symbols_by_date
        event_dates = sorted({str(row["event_date"]) for row in events if row.get("event_date")})
        nasdaq_by_date = fetcher(event_dates)
        validation_source = NASDAQ_EARNINGS_CALENDAR_SOURCE
        for row in events:
            validation_status, confidence, validation_payload = _earnings_source_validation_payload(
                symbol=str(row["symbol"]),
                event_date=str(row["event_date"]),
                nasdaq_by_date=nasdaq_by_date,
            )
            row["validation_status"] = validation_status
            row["source_authority"] = _earnings_source_authority(validation_status)
            row["confidence"] = confidence
            raw_payload = dict(row.get("raw_payload") or {})
            raw_payload["source_validation"] = validation_payload
            raw_payload["universe_scope"] = normalized_universe_scope
            raw_payload["symbol_source"] = normalized_symbol_source
            row["raw_payload"] = raw_payload

    return {
        "source": EARNINGS_CALENDAR_SOURCE,
        "source_url": EARNINGS_CALENDAR_SOURCE_URL,
        "event_type": "EARNINGS",
        "method": "yfinance_ticker_calendar",
        "validation_source": validation_source,
        "symbol_source": normalized_symbol_source,
        "universe_scope": normalized_universe_scope,
        "start_date": window_start.isoformat(),
        "end_date": window_end.isoformat(),
        "symbols_requested": len(normalized_symbols),
        "symbols_processed": len(normalized_symbols) - len(failed_symbols),
        "events": events,
        "events_found": len(events),
        "missing_symbols": missing_symbols,
        "failed_symbols": failed_symbols,
        "symbol_diagnostics": symbol_diagnostics,
        "missing_reason_counts": _earnings_reason_counts(symbol_diagnostics, statuses={"missing"}),
        "failed_reason_counts": _earnings_reason_counts(symbol_diagnostics, statuses={"failed"}),
        "symbols_with_events": len(
            {
                str(item.get("symbol") or "")
                for item in symbol_diagnostics
                if item.get("status") == "event_found"
            }
        ),
    }


def _slice_symbols(symbols: Sequence[Any], *, offset: int = 0, max_symbols: int = 100) -> list[str]:
    normalized = _normalize_symbol_list(symbols, max_symbols=max(len(symbols), max_symbols))
    start = max(0, int(offset or 0))
    end = start + max(1, int(max_symbols or 100))
    return normalized[start:end]


def resolve_earnings_collection_symbols(
    *,
    symbols: str | Sequence[Any] | None = None,
    symbol_source: str = "latest_movers",
    universe_code: str = "SP500",
    universe_limit: int | None = None,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    top_movers_limit: int = 20,
    max_symbols: int = 100,
    batch_offset: int = 0,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    source_symbols_loader: Callable[[], list[str]] | None = None,
    source_symbol_loaders: dict[str, Callable[[], list[str]]] | None = None,
) -> tuple[list[str], str]:
    if symbols is not None:
        return _slice_symbols(symbols, offset=batch_offset, max_symbols=max_symbols), "manual"

    normalized_source = normalize_earnings_symbol_source(symbol_source)
    if source_symbols_loader is not None:
        return _slice_symbols(source_symbols_loader(), offset=batch_offset, max_symbols=max_symbols), normalized_source
    loader = (source_symbol_loaders or {}).get(normalized_source)
    if loader is not None:
        return _slice_symbols(loader(), offset=batch_offset, max_symbols=max_symbols), normalized_source

    if normalized_source == "latest_movers":
        latest_limit = max(1, min(int(top_movers_limit or 20), int(max_symbols or 100)))
        target_symbols = load_latest_intraday_mover_symbols(
            universe_code=universe_code,
            universe_limit=universe_limit,
            interval=interval,
            top_n=latest_limit,
            host=host,
            user=user,
            password=password,
            port=port,
        )
        return _slice_symbols(target_symbols, offset=batch_offset, max_symbols=max_symbols), normalized_source

    if normalized_source == "portfolio":
        raise ValueError("Portfolio earnings source requires a source_symbol_loaders['portfolio'] loader.")
    if normalized_source == "watchlist":
        raise ValueError("Watchlist earnings source requires a source_symbol_loaders['watchlist'] loader.")

    source_to_universe = {
        "sp500": "SP500",
        "top1000": "TOP1000",
        "top2000": "TOP2000",
        "major_cap": "TOP1000",
        "nasdaq100": "NASDAQ100",
        "universe": universe_code,
    }
    resolved_universe = source_to_universe.get(normalized_source, universe_code)
    if resolved_universe == "NASDAQ100":
        rows = load_market_universe_members("NASDAQ100", host=host, user=user, password=password, port=port)
        return _slice_symbols([row.get("symbol") for row in rows], offset=batch_offset, max_symbols=max_symbols), normalized_source
    normalized_universe, normalized_limit = _normalize_intraday_universe(resolved_universe, universe_limit)
    if normalized_universe == "SP500":
        rows = load_market_universe_members("SP500", host=host, user=user, password=password, port=port)
    else:
        rows = load_market_cap_universe_members(
            normalized_universe,
            universe_limit=normalized_limit,
            host=host,
            user=user,
            password=password,
            port=port,
        )
    return _slice_symbols([row.get("symbol") for row in rows], offset=batch_offset, max_symbols=max_symbols), normalized_source


def collect_and_store_earnings_calendar(
    *,
    symbols: str | Sequence[Any] | None = None,
    symbol_source: str = "latest_movers",
    universe_code: str = "SP500",
    universe_limit: int | None = None,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    top_movers_limit: int = 20,
    lookahead_days: int = 120,
    max_symbols: int = 100,
    batch_offset: int = 0,
    validate_with_nasdaq: bool = False,
    request_sleep_sec: float = 0.0,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    source_symbols_loader: Callable[[], list[str]] | None = None,
    source_symbol_loaders: dict[str, Callable[[], list[str]]] | None = None,
    earnings_fetcher: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Collect bounded upcoming earnings events and persist them to the common event calendar."""
    collected_at = _timestamp_str()
    target_symbols, normalized_source = resolve_earnings_collection_symbols(
        symbols=symbols,
        symbol_source=symbol_source,
        universe_code=universe_code,
        universe_limit=universe_limit,
        interval=interval,
        top_movers_limit=top_movers_limit,
        max_symbols=max_symbols,
        batch_offset=batch_offset,
        host=host,
        user=user,
        password=password,
        port=port,
        source_symbols_loader=source_symbols_loader,
        source_symbol_loaders=source_symbol_loaders,
    )
    universe_scope = earnings_universe_scope_for_source(normalized_source, universe_code=universe_code)

    if not target_symbols:
        return {
            "source": EARNINGS_CALENDAR_SOURCE,
            "source_url": EARNINGS_CALENDAR_SOURCE_URL,
            "event_type": "EARNINGS",
            "method": "yfinance_ticker_calendar",
            "symbol_source": normalized_source,
            "universe_scope": universe_scope,
            "universe_code": universe_code,
            "batch_offset": batch_offset,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "events_found": 0,
            "missing_symbols": [],
            "failed_symbols": [],
            "symbol_diagnostics": [],
            "missing_reason_counts": {},
            "failed_reason_counts": {},
            "symbols_with_events": 0,
            "event_dates": [],
            "collected_at": collected_at,
            "message": "No target symbols were available for earnings calendar collection.",
        }

    fetcher = earnings_fetcher or fetch_yfinance_earnings_calendar_events
    fetch_kwargs = {
        "lookahead_days": lookahead_days,
        "max_symbols": max_symbols,
        "symbol_source": normalized_source,
        "universe_scope": universe_scope,
        "validate_with_nasdaq": validate_with_nasdaq,
        "request_sleep_sec": request_sleep_sec,
    }
    supported_params = signature(fetcher).parameters
    if any(param.kind == Parameter.VAR_KEYWORD for param in supported_params.values()):
        supported_kwargs = fetch_kwargs
    else:
        supported_kwargs = {key: value for key, value in fetch_kwargs.items() if key in supported_params}
    result = fetcher(
        target_symbols,
        **supported_kwargs,
    )
    events = []
    for row in result.get("events", []):
        enriched = {**row, "collected_at": collected_at}
        if str(enriched.get("event_type") or "").strip().upper() == "EARNINGS":
            enriched.setdefault("event_family", "earnings")
            enriched.setdefault("event_subtype", "earnings_release")
            enriched.setdefault("universe_scope", universe_scope)
            enriched.setdefault("source_authority", _earnings_source_authority(enriched.get("validation_status")))
            raw_payload = dict(enriched.get("raw_payload") or {})
            raw_payload.setdefault("symbol_source", normalized_source)
            raw_payload.setdefault("universe_scope", universe_scope)
            enriched["raw_payload"] = raw_payload
        events.append(enriched)
    rows_written = upsert_market_event_rows(events, host=host, user=user, password=password, port=port)
    superseded_rows_marked = mark_superseded_earnings_events(
        events,
        superseded_at=collected_at,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    stale_rows_marked = mark_stale_earnings_estimates(
        stale_after_days=EARNINGS_STALE_ESTIMATE_DAYS,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    event_dates = sorted({str(row["event_date"]) for row in events if row.get("event_date")})
    symbol_diagnostics = list(result.get("symbol_diagnostics") or [])
    if symbol_diagnostics:
        missing_reason_counts = _earnings_reason_counts(symbol_diagnostics, statuses={"missing"})
        failed_reason_counts = _earnings_reason_counts(symbol_diagnostics, statuses={"failed"})
        symbols_with_events = len(
            {
                str(item.get("symbol") or "")
                for item in symbol_diagnostics
                if item.get("status") == "event_found"
            }
        )
    else:
        missing_reason_counts = dict(result.get("missing_reason_counts") or {})
        failed_reason_counts = dict(result.get("failed_reason_counts") or {})
        symbols_with_events = int(result.get("symbols_with_events") or 0)
    return {
        **result,
        "rows_written": rows_written,
        "symbol_source": normalized_source,
        "universe_scope": universe_scope,
        "universe_code": universe_code,
        "universe_limit": universe_limit,
        "interval": interval,
        "top_movers_limit": top_movers_limit,
        "batch_offset": batch_offset,
        "validate_with_nasdaq": validate_with_nasdaq,
        "request_sleep_sec": request_sleep_sec,
        "target_symbols": target_symbols,
        "event_dates": event_dates,
        "symbol_diagnostics": symbol_diagnostics,
        "missing_reason_counts": missing_reason_counts,
        "failed_reason_counts": failed_reason_counts,
        "symbols_with_events": symbols_with_events,
        "symbols_missing_count": len(result.get("missing_symbols") or []),
        "symbols_failed_count": len(result.get("failed_symbols") or []),
        "superseded_rows_marked": superseded_rows_marked,
        "stale_rows_marked": stale_rows_marked,
        "collected_at": collected_at,
    }


def upsert_market_universe_members(
    rows: list[dict[str, Any]],
    *,
    universe_code: str = "SP500",
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_universe_member",
            MARKET_INTELLIGENCE_SCHEMAS["market_universe_member"],
            DB_META,
        )
        if not rows:
            return 0
        sql = """
        INSERT INTO market_universe_member (
          universe_code, symbol, source_symbol, name, sector, industry,
          source, source_url, as_of_date, active, collected_at, error_msg
        ) VALUES (
          %(universe_code)s, %(symbol)s, %(source_symbol)s, %(name)s, %(sector)s, %(industry)s,
          %(source)s, %(source_url)s, %(as_of_date)s, %(active)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          source_symbol = VALUES(source_symbol),
          name = VALUES(name),
          sector = VALUES(sector),
          industry = VALUES(industry),
          source = VALUES(source),
          source_url = VALUES(source_url),
          as_of_date = VALUES(as_of_date),
          active = VALUES(active),
          collected_at = VALUES(collected_at),
          error_msg = VALUES(error_msg)
        """
        db.executemany(sql, rows)
        symbols = [row["symbol"] for row in rows if row.get("symbol")]
        placeholders = ",".join(["%s"] * len(symbols))
        db.execute(
            f"""
            UPDATE market_universe_member
            SET active = 0
            WHERE universe_code = %s
              AND symbol NOT IN ({placeholders})
            """,
            [universe_code] + symbols,
        )
        return len(rows)
    finally:
        db.close()


def collect_and_store_sp500_universe(
    *,
    source_url: str = SP500_SOURCE_URL,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    rows = fetch_sp500_constituents(source_url)
    rows_written = upsert_market_universe_members(
        rows,
        universe_code="SP500",
        host=host,
        user=user,
        password=password,
        port=port,
    )
    return {
        "rows_written": rows_written,
        "symbols": [row["symbol"] for row in rows],
        "source": SP500_SOURCE,
        "source_url": source_url,
        "collected_at": _timestamp_str(),
    }


def load_market_universe_members(
    universe_code: str = "SP500",
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        return db.query(
            """
            SELECT universe_code, symbol, source_symbol, name, sector, industry, source, source_url, as_of_date,
                   active, collected_at, error_msg
            FROM market_universe_member
            WHERE universe_code = %s
              AND active = 1
            ORDER BY symbol ASC
            """,
            [universe_code],
        )
    finally:
        db.close()


def _market_liquidity_universe_row(
    row: dict[str, Any],
    *,
    universe_code: str,
    rank_position: int,
    generated_at: str,
) -> dict[str, Any] | None:
    symbol = _normalize_symbol(row.get("symbol"))
    if not symbol:
        return None
    return {
        "universe_code": universe_code,
        "symbol": symbol,
        "rank_position": _safe_int(row.get("rank_position")) or rank_position,
        "source_symbol": _normalize_symbol(row.get("source_symbol") or row.get("symbol")) or symbol,
        "name": row.get("name") or row.get("long_name"),
        "sector": row.get("sector"),
        "industry": row.get("industry"),
        "market_cap": _safe_int(row.get("market_cap")),
        "avg_dollar_volume_20d": _safe_float(row.get("avg_dollar_volume_20d")),
        "dollar_volume_days": _safe_int(row.get("dollar_volume_days")),
        "ranking_window_start_date": row.get("ranking_window_start_date"),
        "ranking_end_date": row.get("ranking_end_date"),
        "ranking_source": row.get("ranking_source") or LIQUIDITY_UNIVERSE_RANKING_SOURCE,
        "price_source": row.get("price_source") or LIQUIDITY_UNIVERSE_PRICE_SOURCE,
        "listing_source": row.get("listing_source") or row.get("source"),
        "listing_source_url": row.get("listing_source_url") or row.get("source_url"),
        "listing_source_type": row.get("listing_source_type"),
        "listing_coverage_status": row.get("listing_coverage_status"),
        "listing_event_type": row.get("listing_event_type"),
        "listing_status": row.get("listing_status"),
        "listing_event_date": row.get("listing_event_date") or row.get("as_of_date"),
        "listing_collected_at": row.get("listing_collected_at") or row.get("collected_at"),
        "generated_at": generated_at,
        "active": _safe_int(row.get("active")) if row.get("active") is not None else 1,
        "error_msg": row.get("error_msg"),
    }


def upsert_market_liquidity_universe_members(
    rows: list[dict[str, Any]],
    *,
    universe_code: str = "TOP1000",
    generated_at: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    normalized_code, _ = _normalize_intraday_universe(universe_code)
    generated_at_value = generated_at or _timestamp_str()
    normalized_rows = [
        normalized
        for index, row in enumerate(rows, start=1)
        if (
            normalized := _market_liquidity_universe_row(
                row,
                universe_code=normalized_code,
                rank_position=index,
                generated_at=generated_at_value,
            )
        )
    ]
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_liquidity_universe_member",
            MARKET_INTELLIGENCE_SCHEMAS["market_liquidity_universe_member"],
            DB_META,
        )
        if not normalized_rows:
            return 0
        sql = """
        INSERT INTO market_liquidity_universe_member (
          universe_code, symbol, rank_position, source_symbol, name, sector, industry, market_cap,
          avg_dollar_volume_20d, dollar_volume_days, ranking_window_start_date, ranking_end_date,
          ranking_source, price_source,
          listing_source, listing_source_url, listing_source_type, listing_coverage_status,
          listing_event_type, listing_status, listing_event_date, listing_collected_at,
          generated_at, active, error_msg
        ) VALUES (
          %(universe_code)s, %(symbol)s, %(rank_position)s, %(source_symbol)s, %(name)s, %(sector)s, %(industry)s, %(market_cap)s,
          %(avg_dollar_volume_20d)s, %(dollar_volume_days)s, %(ranking_window_start_date)s, %(ranking_end_date)s,
          %(ranking_source)s, %(price_source)s,
          %(listing_source)s, %(listing_source_url)s, %(listing_source_type)s, %(listing_coverage_status)s,
          %(listing_event_type)s, %(listing_status)s, %(listing_event_date)s, %(listing_collected_at)s,
          %(generated_at)s, %(active)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          rank_position = VALUES(rank_position),
          source_symbol = VALUES(source_symbol),
          name = VALUES(name),
          sector = VALUES(sector),
          industry = VALUES(industry),
          market_cap = VALUES(market_cap),
          avg_dollar_volume_20d = VALUES(avg_dollar_volume_20d),
          dollar_volume_days = VALUES(dollar_volume_days),
          ranking_window_start_date = VALUES(ranking_window_start_date),
          ranking_end_date = VALUES(ranking_end_date),
          ranking_source = VALUES(ranking_source),
          price_source = VALUES(price_source),
          listing_source = VALUES(listing_source),
          listing_source_url = VALUES(listing_source_url),
          listing_source_type = VALUES(listing_source_type),
          listing_coverage_status = VALUES(listing_coverage_status),
          listing_event_type = VALUES(listing_event_type),
          listing_status = VALUES(listing_status),
          listing_event_date = VALUES(listing_event_date),
          listing_collected_at = VALUES(listing_collected_at),
          generated_at = VALUES(generated_at),
          active = VALUES(active),
          error_msg = VALUES(error_msg)
        """
        db.executemany(sql, normalized_rows)
        symbols = [row["symbol"] for row in normalized_rows if row.get("symbol")]
        placeholders = ",".join(["%s"] * len(symbols))
        db.execute(
            f"""
            UPDATE market_liquidity_universe_member
            SET active = 0
            WHERE universe_code = %s
              AND symbol NOT IN ({placeholders})
            """,
            [normalized_code] + symbols,
        )
        return len(normalized_rows)
    finally:
        db.close()


def load_market_liquidity_universe_members(
    universe_code: str = "TOP1000",
    *,
    universe_limit: int | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    normalized_code, normalized_limit = _normalize_intraday_universe(universe_code, universe_limit)
    limit = int(universe_limit or normalized_limit)
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        return db.query(
            """
            SELECT
                universe_code, symbol, rank_position, source_symbol, name, sector, industry, market_cap,
                avg_dollar_volume_20d, dollar_volume_days, ranking_window_start_date, ranking_end_date,
                ranking_source, price_source,
                listing_source, listing_source_url, listing_source_type, listing_coverage_status,
                listing_event_type, listing_status, listing_event_date, listing_collected_at,
                generated_at, active, error_msg
            FROM market_liquidity_universe_member
            WHERE universe_code = %s
              AND active = 1
            ORDER BY rank_position ASC, symbol ASC
            LIMIT %s
            """,
            [normalized_code, limit],
        )
    finally:
        db.close()


def _market_symbol_alias_row(
    row: dict[str, Any],
    *,
    status: str,
    detected_at: str,
    applied_at: str | None,
) -> dict[str, Any] | None:
    source_symbol = _normalize_symbol(row.get("source_symbol") or row.get("symbol"))
    alias_symbol = _normalize_symbol(row.get("alias_symbol") or row.get("replacement_symbol"))
    if not source_symbol or not alias_symbol or source_symbol == alias_symbol:
        return None
    row_status = str(row.get("status") or status or "candidate").strip().lower()
    if row_status not in {"candidate", "active", "rejected"}:
        row_status = "candidate"
    evidence = row.get("evidence_json") if row.get("evidence_json") is not None else row.get("evidence")
    return {
        "source_symbol": source_symbol,
        "alias_symbol": alias_symbol,
        "alias_type": str(row.get("alias_type") or "ticker_change").strip() or "ticker_change",
        "status": row_status,
        "confidence": _safe_float(row.get("confidence")),
        "evidence_json": _json_payload(evidence),
        "detected_at": row.get("detected_at") or detected_at,
        "applied_at": row.get("applied_at") or applied_at,
    }


def upsert_market_symbol_aliases(
    rows: list[dict[str, Any]],
    *,
    status: str | None = None,
    detected_at: str | None = None,
    applied_at: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    effective_status = status or ("active" if applied_at else "candidate")
    detected_at_value = detected_at or _timestamp_str()
    normalized_rows = [
        normalized
        for row in rows
        if (
            normalized := _market_symbol_alias_row(
                row,
                status=effective_status,
                detected_at=detected_at_value,
                applied_at=applied_at,
            )
        )
    ]
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_symbol_alias",
            MARKET_INTELLIGENCE_SCHEMAS["market_symbol_alias"],
            DB_META,
        )
        if not normalized_rows:
            return 0
        sql = """
        INSERT INTO market_symbol_alias (
          source_symbol, alias_symbol, alias_type, status, confidence,
          evidence_json, detected_at, applied_at
        ) VALUES (
          %(source_symbol)s, %(alias_symbol)s, %(alias_type)s, %(status)s, %(confidence)s,
          %(evidence_json)s, %(detected_at)s, %(applied_at)s
        )
        ON DUPLICATE KEY UPDATE
          status = VALUES(status),
          confidence = VALUES(confidence),
          evidence_json = VALUES(evidence_json),
          detected_at = VALUES(detected_at),
          applied_at = VALUES(applied_at)
        """
        db.executemany(sql, normalized_rows)
        return len(normalized_rows)
    finally:
        db.close()


def load_active_market_symbol_aliases(
    symbols: Sequence[Any],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, dict[str, Any]]:
    normalized_symbols = sorted({_normalize_symbol(symbol) for symbol in symbols if _normalize_symbol(symbol)})
    if not normalized_symbols:
        return {}
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_symbol_alias",
            MARKET_INTELLIGENCE_SCHEMAS["market_symbol_alias"],
            DB_META,
        )
        placeholders = ",".join(["%s"] * len(normalized_symbols))
        rows = db.query(
            f"""
            SELECT
                source_symbol, alias_symbol, alias_type, status, confidence,
                evidence_json, detected_at, applied_at
            FROM market_symbol_alias
            WHERE source_symbol IN ({placeholders})
              AND status = %s
            ORDER BY confidence DESC, applied_at DESC, detected_at DESC
            """,
            normalized_symbols + ["active"],
        )
    finally:
        db.close()

    aliases: dict[str, dict[str, Any]] = {}
    for row in rows:
        source_symbol = _normalize_symbol(row.get("source_symbol"))
        alias_symbol = _normalize_symbol(row.get("alias_symbol"))
        if not source_symbol or not alias_symbol or source_symbol in aliases:
            continue
        normalized = dict(row)
        normalized["source_symbol"] = source_symbol
        normalized["alias_symbol"] = alias_symbol
        aliases[source_symbol] = normalized
    return aliases


def _normalized_company_name(value: Any) -> str:
    text = re.sub(r"[^A-Z0-9]+", " ", str(value or "").upper())
    suffixes = {
        "INC",
        "INCORPORATED",
        "CORP",
        "CORPORATION",
        "CO",
        "COMPANY",
        "LTD",
        "PLC",
        "HOLDING",
        "HOLDINGS",
        "GROUP",
        "CLASS",
        "COMMON",
        "STOCK",
    }
    tokens = [token for token in text.split() if token and token not in suffixes]
    return " ".join(tokens)


def _default_symbol_alias_search(query: str, *, max_results: int = 8) -> list[dict[str, Any]]:
    try:
        search = yf.Search(query, max_results=max_results)
        quotes = getattr(search, "quotes", None)
        return list(quotes or [])
    except Exception:
        return []


def _symbol_alias_candidate_score(
    *,
    source_name: str,
    candidate: dict[str, Any],
    expected_exchange: str | None,
) -> float:
    candidate_name = candidate.get("longname") or candidate.get("shortname") or candidate.get("name")
    source_normalized = _normalized_company_name(source_name)
    candidate_normalized = _normalized_company_name(candidate_name)
    if not source_normalized or not candidate_normalized:
        score = 0.55
    elif source_normalized == candidate_normalized:
        score = 0.96
    elif source_normalized in candidate_normalized or candidate_normalized in source_normalized:
        score = 0.88
    else:
        source_tokens = set(source_normalized.split())
        candidate_tokens = set(candidate_normalized.split())
        overlap = len(source_tokens & candidate_tokens) / max(len(source_tokens), 1)
        score = 0.62 + min(0.2, overlap * 0.2)
    exchange = str(candidate.get("exchange") or candidate.get("exchDisp") or "").strip().upper()
    if expected_exchange and exchange and exchange != str(expected_exchange).strip().upper():
        score -= 0.05
    if str(candidate.get("quoteType") or "").strip().upper() not in {"", "EQUITY"}:
        score -= 0.1
    return max(0.0, min(0.99, score))


def detect_market_symbol_alias_candidates(
    symbols: Sequence[Any],
    *,
    metadata_by_symbol: dict[str, dict[str, Any]] | None = None,
    quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    search_fn: Callable[..., list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    """Suggest replacement tickers for quote-missing universe symbols without applying them."""
    fetcher = quote_fetcher or _fetch_yahoo_quote_rows
    search = search_fn or _default_symbol_alias_search
    metadata_by_symbol = metadata_by_symbol or {}
    candidates: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    for raw_symbol in symbols:
        source_symbol = _normalize_symbol(raw_symbol)
        if not source_symbol:
            continue
        metadata = metadata_by_symbol.get(source_symbol) or {}
        source_name = str(metadata.get("long_name") or metadata.get("name") or "").strip()
        if not source_name:
            continue
        expected_exchange = metadata.get("profile_exchange") or metadata.get("exchange")
        search_rows = search(source_name, max_results=8)
        ranked: list[tuple[float, dict[str, Any]]] = []
        for row in search_rows:
            alias_symbol = _normalize_symbol(row.get("symbol"))
            if not alias_symbol or alias_symbol == source_symbol:
                continue
            score = _symbol_alias_candidate_score(
                source_name=source_name,
                candidate=row,
                expected_exchange=expected_exchange,
            )
            ranked.append((score, row))
        ranked.sort(key=lambda item: item[0], reverse=True)
        for score, row in ranked[:3]:
            alias_symbol = _normalize_symbol(row.get("symbol"))
            if not alias_symbol or (source_symbol, alias_symbol) in seen:
                continue
            quote_rows = fetcher([alias_symbol])
            quote_map = {
                _normalize_symbol(quote.get("symbol")): quote
                for quote in quote_rows
                if _normalize_symbol(quote.get("symbol"))
            }
            if alias_symbol not in quote_map:
                continue
            seen.add((source_symbol, alias_symbol))
            candidates.append(
                {
                    "symbol": source_symbol,
                    "source_symbol": source_symbol,
                    "alias_symbol": alias_symbol,
                    "alias_type": "ticker_change",
                    "status": "candidate",
                    "confidence": round(score, 2),
                    "reason": "old ticker missing, replacement quote active",
                    "evidence": {
                        "source_name": source_name,
                        "search_symbol": row.get("symbol"),
                        "search_name": row.get("longname") or row.get("shortname"),
                        "search_exchange": row.get("exchange") or row.get("exchDisp"),
                        "quote_provider": "yahoo_quote_v7",
                    },
                }
            )
            break
    return candidates


def _dedupe_liquidity_candidate_rows(rows: Sequence[dict[str, Any]]) -> list[dict[str, Any]]:
    deduped: list[dict[str, Any]] = []
    seen: set[str] = set()
    for row in rows:
        symbol = _normalize_symbol(row.get("symbol"))
        if not symbol or symbol in seen:
            continue
        seen.add(symbol)
        item = dict(row)
        item["symbol"] = symbol
        item["source_symbol"] = _normalize_symbol(row.get("source_symbol") or symbol) or symbol
        item["name"] = row.get("name") or row.get("long_name")
        item["listing_source"] = row.get("listing_source") or row.get("source")
        item["listing_source_url"] = row.get("listing_source_url") or row.get("source_url") or row.get("source_ref")
        deduped.append(item)
    return deduped


def load_market_liquidity_universe_candidate_symbols(
    universe_code: str = "TOP1000",
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    _normalize_intraday_universe(universe_code)
    source_placeholders = ",".join(["%s"] * len(LIQUIDITY_UNIVERSE_LISTING_SOURCES))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        rows = db.query(
            f"""
            SELECT
                l.symbol,
                l.symbol AS source_symbol,
                COALESCE(NULLIF(p.long_name, ''), NULLIF(l.name, ''), s.name) AS name,
                p.sector,
                p.industry,
                p.market_cap,
                l.source AS listing_source,
                l.source_ref AS listing_source_url,
                l.source_type AS listing_source_type,
                l.coverage_status AS listing_coverage_status,
                l.event_type AS listing_event_type,
                l.listing_status AS listing_status,
                l.event_date AS listing_event_date,
                l.collected_at AS listing_collected_at,
                l.error_msg
            FROM nyse_symbol_lifecycle l
            LEFT JOIN nyse_asset_profile p
              ON p.symbol = l.symbol
             AND p.kind = l.kind
            LEFT JOIN nyse_stock s
              ON s.symbol = l.symbol
            WHERE l.source IN ({source_placeholders})
              AND l.source_type = %s
              AND l.event_type = %s
              AND l.kind = %s
              AND l.listing_status = %s
              AND COALESCE(l.event_date, DATE(l.collected_at)) = (
                    SELECT MAX(COALESCE(latest.event_date, DATE(latest.collected_at)))
                    FROM nyse_symbol_lifecycle latest
                    WHERE latest.source = l.source
                      AND latest.source_type = %s
                      AND latest.event_type = %s
                      AND latest.kind = %s
                      AND latest.listing_status = %s
              )
              AND (p.is_spac IS NULL OR p.is_spac <> 1)
              AND (p.status IS NULL OR LOWER(p.status) NOT IN ('dilist', 'delist', 'delisted'))
            ORDER BY
              l.symbol ASC,
              CASE l.source
                WHEN 'nasdaq_symdir_nasdaqlisted' THEN 1
                WHEN 'nasdaq_symdir_otherlisted' THEN 2
                WHEN 'nyse_listings_directory' THEN 3
                WHEN 'sec_company_tickers_exchange' THEN 4
                ELSE 9
              END ASC
            """,
            list(LIQUIDITY_UNIVERSE_LISTING_SOURCES)
            + [
                "current_listing_snapshot",
                "listing_observed",
                "stock",
                "active",
                "current_listing_snapshot",
                "listing_observed",
                "stock",
                "active",
            ],
        )
        return _dedupe_liquidity_candidate_rows(rows)
    finally:
        db.close()


def load_market_dollar_volume_universe_members(
    universe_code: str = "TOP1000",
    *,
    universe_limit: int | None = None,
    candidate_rows: list[dict[str, Any]] | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    normalized_code, normalized_limit = _normalize_intraday_universe(universe_code, universe_limit)
    limit = int(universe_limit or normalized_limit)
    candidates = _dedupe_liquidity_candidate_rows(
        candidate_rows
        if candidate_rows is not None
        else load_market_liquidity_universe_candidate_symbols(
            normalized_code,
            host=host,
            user=user,
            password=password,
            port=port,
        )
    )
    symbols = [_normalize_symbol(row.get("symbol")) for row in candidates if row.get("symbol")]
    symbols = [symbol for symbol in symbols if symbol]
    if not symbols:
        return []

    symbol_meta = {str(row["symbol"]): row for row in candidates if row.get("symbol")}
    placeholders = ",".join(["%s"] * len(symbols))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        latest_rows = db.query(
            f"""
            SELECT MAX(`date`) AS latest_price_date
            FROM nyse_price_history
            WHERE symbol IN ({placeholders})
              AND timeframe = %s
              AND COALESCE(adj_close, close) IS NOT NULL
              AND volume IS NOT NULL
              AND volume > 0
            """,
            symbols + ["1d"],
        )
        latest_price_date = _event_date_str((latest_rows[0] or {}).get("latest_price_date")) if latest_rows else None
        if not latest_price_date:
            return []
        ranking_rows = db.query(
            f"""
            WITH recent_dates AS (
                SELECT DISTINCT `date`
                FROM nyse_price_history
                WHERE symbol IN ({placeholders})
                  AND timeframe = %s
                  AND `date` <= %s
                  AND COALESCE(adj_close, close) IS NOT NULL
                  AND volume IS NOT NULL
                  AND volume > 0
                ORDER BY `date` DESC
                LIMIT 20
            )
            SELECT
                p.symbol,
                AVG(COALESCE(adj_close, close) * volume) AS avg_dollar_volume_20d,
                COUNT(*) AS dollar_volume_days,
                MIN(p.`date`) AS ranking_window_start_date,
                MAX(p.`date`) AS ranking_end_date
            FROM nyse_price_history p
            JOIN recent_dates rd
              ON rd.`date` = p.`date`
            WHERE p.symbol IN ({placeholders})
              AND p.timeframe = %s
              AND COALESCE(p.adj_close, p.close) IS NOT NULL
              AND p.volume IS NOT NULL
              AND p.volume > 0
            GROUP BY p.symbol
            HAVING MAX(p.`date`) = %s
            ORDER BY avg_dollar_volume_20d DESC, p.symbol ASC
            LIMIT %s
            """,
            symbols + ["1d", latest_price_date] + symbols + ["1d", latest_price_date, limit],
        )
    finally:
        db.close()

    out: list[dict[str, Any]] = []
    for rank, row in enumerate(ranking_rows[:limit], start=1):
        symbol = _normalize_symbol(row.get("symbol"))
        if not symbol:
            continue
        meta = symbol_meta.get(symbol, {})
        out.append(
            {
                **meta,
                "universe_code": normalized_code,
                "symbol": symbol,
                "rank_position": rank,
                "avg_dollar_volume_20d": _safe_float(row.get("avg_dollar_volume_20d")),
                "dollar_volume_days": _safe_int(row.get("dollar_volume_days")),
                "ranking_window_start_date": _event_date_str(row.get("ranking_window_start_date")),
                "ranking_end_date": _event_date_str(row.get("ranking_end_date")) or latest_price_date,
                "ranking_source": LIQUIDITY_UNIVERSE_RANKING_SOURCE,
                "price_source": LIQUIDITY_UNIVERSE_PRICE_SOURCE,
            }
        )
    return out


def collect_and_store_market_liquidity_universe(
    *,
    universe_code: str = "TOP1000",
    universe_limit: int | None = None,
    candidate_rows: list[dict[str, Any]] | None = None,
    generated_at: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    normalized_code, normalized_limit = _normalize_intraday_universe(universe_code, universe_limit)
    rows = load_market_dollar_volume_universe_members(
        normalized_code,
        universe_limit=normalized_limit,
        candidate_rows=candidate_rows,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    generated_at_value = generated_at or _timestamp_str()
    rows_written = upsert_market_liquidity_universe_members(
        rows,
        universe_code=normalized_code,
        generated_at=generated_at_value,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    ranking_dates = [row.get("ranking_end_date") for row in rows if row.get("ranking_end_date")]
    return {
        "universe_code": normalized_code,
        "universe_limit": normalized_limit,
        "rows_computed": len(rows),
        "rows_written": rows_written,
        "symbols": [row["symbol"] for row in rows if row.get("symbol")],
        "ranking_source": LIQUIDITY_UNIVERSE_RANKING_SOURCE,
        "price_source": LIQUIDITY_UNIVERSE_PRICE_SOURCE,
        "ranking_end_date": max(ranking_dates) if ranking_dates else None,
        "generated_at": generated_at_value,
        "target_table": "finance_meta.market_liquidity_universe_member",
    }


def load_market_cap_universe_members(
    universe_code: str = "TOP1000",
    *,
    universe_limit: int | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    normalized_code, normalized_limit = _normalize_intraday_universe(universe_code, universe_limit)
    if normalized_code == "SP500":
        return load_market_universe_members("SP500", host=host, user=user, password=password, port=port)
    if normalized_code == "NASDAQ":
        return load_nasdaq_symbol_directory_universe_members(host=host, user=user, password=password, port=port)

    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        return db.query(
            """
            SELECT
                %s AS universe_code,
                symbol,
                symbol AS source_symbol,
                long_name AS name,
                sector,
                industry,
                'nyse_asset_profile.market_cap' AS source,
                NULL AS source_url,
                DATE(last_collected_at) AS as_of_date,
                1 AS active,
                last_collected_at AS collected_at,
                error_msg
            FROM nyse_asset_profile
            WHERE kind = %s
              AND country = %s
              AND market_cap IS NOT NULL
              AND market_cap > 0
              AND (is_spac IS NULL OR is_spac <> 1)
              AND (status IS NULL OR LOWER(status) NOT IN ('dilist', 'delist', 'delisted'))
            ORDER BY market_cap DESC, symbol ASC
            LIMIT %s
            """,
            [normalized_code, "stock", "United States", normalized_limit],
        )
    finally:
        db.close()


def load_nasdaq_symbol_directory_universe_members(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    """Read latest Nasdaq-listed current snapshot rows from symbol lifecycle evidence."""
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        return db.query(
            """
            SELECT
                'NASDAQ' AS universe_code,
                l.symbol,
                l.symbol AS source_symbol,
                l.name,
                p.sector,
                p.industry,
                l.source,
                l.source_ref AS source_url,
                l.event_date AS as_of_date,
                1 AS active,
                l.collected_at,
                l.error_msg
            FROM nyse_symbol_lifecycle l
            LEFT JOIN nyse_asset_profile p
              ON p.symbol = l.symbol
             AND p.kind = l.kind
            WHERE l.source = %s
              AND l.source_type = %s
              AND l.event_type = %s
              AND l.kind = %s
              AND l.listing_status = %s
              AND COALESCE(l.event_date, DATE(l.collected_at)) = (
                    SELECT MAX(COALESCE(event_date, DATE(collected_at)))
                    FROM nyse_symbol_lifecycle
                    WHERE source = %s
                      AND source_type = %s
                      AND event_type = %s
                      AND kind = %s
                      AND listing_status = %s
              )
            ORDER BY COALESCE(p.market_cap, 0) DESC, l.symbol ASC
            """,
            [
                NASDAQ_SYMBOL_DIRECTORY_SOURCE,
                "current_listing_snapshot",
                "listing_observed",
                "stock",
                "active",
                NASDAQ_SYMBOL_DIRECTORY_SOURCE,
                "current_listing_snapshot",
                "listing_observed",
                "stock",
                "active",
            ],
        )
    finally:
        db.close()


def _load_db_previous_close_map(
    symbols: Sequence[str],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        rows = db.query(
            f"""
            SELECT p.symbol, p.`date`, COALESCE(p.adj_close, p.close) AS previous_close
            FROM nyse_price_history p
            JOIN (
                SELECT symbol, MAX(`date`) AS max_date
                FROM nyse_price_history
                WHERE symbol IN ({placeholders})
                  AND timeframe = %s
                  AND COALESCE(adj_close, close) IS NOT NULL
                GROUP BY symbol
            ) latest
              ON latest.symbol = p.symbol
             AND latest.max_date = p.`date`
            WHERE p.timeframe = %s
            """,
            list(symbols) + ["1d", "1d"],
        )
    finally:
        db.close()
    out: dict[str, dict[str, Any]] = {}
    for row in rows:
        symbol = _normalize_symbol(row.get("symbol"))
        if not symbol:
            continue
        out[symbol] = {
            "previous_close": _safe_float(row.get("previous_close")),
            "previous_close_date": row.get("date"),
        }
    return out


def _chunked(items: Sequence[str], size: int) -> Iterable[list[str]]:
    for index in range(0, len(items), size):
        yield list(items[index : index + size])


def _download_prices(
    symbols: list[str],
    *,
    period: str,
    interval: str,
    progress: bool = False,
) -> pd.DataFrame:
    if not symbols:
        return pd.DataFrame()
    return yf.download(
        tickers=symbols,
        period=period,
        interval=interval,
        auto_adjust=False,
        group_by="ticker",
        threads=True,
        progress=progress,
        prepost=False,
    )


def _fetch_yahoo_quote_rows(symbols: list[str], *, timeout: int = 15) -> list[dict[str, Any]]:
    if not symbols:
        return []
    data = YfData().get_raw_json(
        YAHOO_QUOTE_URL,
        params={"symbols": ",".join(symbols)},
        timeout=timeout,
    )
    return list(data.get("quoteResponse", {}).get("result", []) or [])


def _fast_info_value(info: Any, *keys: str) -> Any:
    for key in keys:
        try:
            if hasattr(info, "get"):
                value = info.get(key)
                if value not in (None, ""):
                    return value
        except Exception:
            pass
        try:
            value = info[key]
            if value not in (None, ""):
                return value
        except Exception:
            pass
        attr_name = key.replace("-", "_")
        try:
            value = getattr(info, attr_name)
            if value not in (None, ""):
                return value
        except Exception:
            pass
    return None


def _fetch_fast_info_evidence(
    symbol: str,
    *,
    ticker_factory: Callable[[str], Any] | None = None,
) -> dict[str, Any]:
    factory = ticker_factory or yf.Ticker
    try:
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            ticker = factory(symbol)
            info = getattr(ticker, "fast_info", None)
            latest_price = _safe_float(_fast_info_value(info, "lastPrice", "last_price", "lastPrice"))
            previous_close = _safe_float(
                _fast_info_value(info, "previousClose", "previous_close", "regularMarketPreviousClose")
            )
        status = "ok" if latest_price is not None or previous_close is not None else "missing"
        return {
            "status": status,
            "latest_price": latest_price,
            "previous_close": previous_close,
            "detail": None if status == "ok" else "fast_info returned no price fields",
        }
    except Exception as exc:
        return {
            "status": "error",
            "latest_price": None,
            "previous_close": None,
            "detail": str(exc),
        }


def _history_evidence_from_frame(symbol: str, frame: pd.DataFrame) -> dict[str, Any]:
    symbol_history = _symbol_frame(frame, symbol)
    quote_time, latest_price, _volume = _latest_close_row(symbol_history)
    previous_close = _previous_close(symbol_history, quote_time)
    status = "ok" if latest_price is not None else "missing"
    return {
        "status": status,
        "latest_price": latest_price,
        "previous_close": previous_close,
        "latest_price_date": quote_time,
        "detail": None if status == "ok" else "5d daily history returned no close rows",
    }


def _fetch_history_evidence_map(
    symbols: Sequence[str],
    *,
    downloader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    price_downloader = downloader or _download_prices
    normalized_symbols = [_normalize_symbol(item) for item in symbols if _normalize_symbol(item)]
    if not normalized_symbols:
        return {}
    try:
        with redirect_stdout(StringIO()), redirect_stderr(StringIO()):
            frame = price_downloader(normalized_symbols, period="5d", interval="1d", progress=False)
        return {item: _history_evidence_from_frame(item, frame) for item in normalized_symbols}
    except Exception as exc:
        return {
            item: {
                "status": "error",
                "latest_price": None,
                "previous_close": None,
                "latest_price_date": None,
                "detail": str(exc),
            }
            for item in normalized_symbols
        }


def _load_asset_profile_evidence_map(
    symbols: Sequence[str],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, dict[str, Any]]:
    if not symbols:
        return {}
    placeholders = ",".join(["%s"] * len(symbols))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        rows = db.query(
            f"""
            SELECT symbol, long_name, quote_type, exchange, status, error_msg, last_collected_at
            FROM nyse_asset_profile
            WHERE symbol IN ({placeholders})
              AND kind = %s
            """,
            list(symbols) + ["stock"],
        )
    finally:
        db.close()
    return {
        _normalize_symbol(row.get("symbol")): {
            "long_name": row.get("long_name"),
            "quote_type": row.get("quote_type"),
            "exchange": row.get("exchange"),
            "status": row.get("status"),
            "error_msg": row.get("error_msg"),
            "last_collected_at": row.get("last_collected_at"),
        }
        for row in rows
        if _normalize_symbol(row.get("symbol"))
    }


def _quote_gap_recommended_action(diagnosis: str) -> str:
    return {
        "batch_only_gap": "Rerun Update Daily Snapshot; if it repeats, use smaller batches or a single-symbol retry fallback.",
        "provider_quote_gap": "Treat as Yahoo quote endpoint coverage gap; use yfinance history/fast_info evidence or rerun later.",
        "history_gap_quote_available": "Quote-like price exists but short OHLCV history is weak; inspect yfinance history coverage before using fallback.",
        "missing_previous_close": "Refresh daily OHLCV history or inspect previous-close coverage before calculating daily return.",
        "possible_stale_universe": "Refresh universe/profile data and inspect whether the symbol should remain in the coverage universe.",
        "provider_endpoint_issue": "Provider evidence is inconclusive; rerun later and inspect alternate sources before excluding the symbol.",
    }.get(diagnosis, "Inspect provider data and rerun the relevant refresh.")


def _classify_quote_gap_diagnostic(
    *,
    quote_status: str,
    quote_latest_price: float | None,
    quote_previous_close: float | None,
    fast_info: dict[str, Any],
    history: dict[str, Any],
    db_price: dict[str, Any],
    profile: dict[str, Any],
) -> tuple[str, float, str]:
    fast_latest = _safe_float(fast_info.get("latest_price"))
    fast_previous = _safe_float(fast_info.get("previous_close"))
    history_latest = _safe_float(history.get("latest_price"))
    history_previous = _safe_float(history.get("previous_close"))
    db_latest = _safe_float(db_price.get("previous_close"))
    has_latest = any(value is not None for value in [quote_latest_price, fast_latest, history_latest, db_latest])
    has_previous = any(value is not None for value in [quote_previous_close, fast_previous, history_previous, db_latest])
    profile_status = str(profile.get("status") or "").lower()

    if quote_status == "ok" and quote_latest_price is not None and has_previous:
        diagnosis = "batch_only_gap"
        confidence = 0.9
        evidence = "Single-symbol Yahoo quote returned enough price fields; the original batch response likely missed this symbol."
    elif fast_latest is not None and history_latest is None and quote_latest_price is None:
        diagnosis = "history_gap_quote_available"
        confidence = 0.78
        evidence = "fast_info has current price evidence, but short daily history / quote endpoint evidence is missing."
    elif has_latest and not has_previous:
        diagnosis = "missing_previous_close"
        confidence = 0.76
        evidence = "A latest/current price exists, but previous-close evidence is missing."
    elif has_latest:
        diagnosis = "provider_quote_gap"
        confidence = 0.82
        evidence = "Yahoo quote endpoint did not return a complete row, but another price source still has evidence."
    elif profile_status in {"delisted", "not_found", "error"}:
        diagnosis = "possible_stale_universe"
        confidence = 0.7
        evidence = f"Asset profile status is `{profile_status or 'unknown'}` and no current price evidence was found."
    else:
        diagnosis = "provider_endpoint_issue"
        confidence = 0.58
        evidence = "No alternate price evidence was found in the quick free-source diagnostic."
    return diagnosis, confidence, evidence


def diagnose_market_quote_gaps(
    symbols: str | Sequence[Any],
    *,
    universe_code: str = "SP500",
    interval_code: str = DEFAULT_INTRADAY_INTERVAL,
    snapshot_time_utc: str | None = None,
    max_symbols: int = 50,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    ticker_factory: Callable[[str], Any] | None = None,
    history_downloader: Callable[..., pd.DataFrame] | None = None,
    db_previous_close_map: dict[str, dict[str, Any]] | None = None,
    profile_map: dict[str, dict[str, Any]] | None = None,
) -> dict[str, Any]:
    normalized_symbols = _normalize_symbol_list(symbols, max_symbols=max_symbols)
    if not normalized_symbols:
        return {
            "universe_code": universe_code,
            "interval_code": interval_code,
            "snapshot_time_utc": snapshot_time_utc,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "diagnosis_counts": {},
            "diagnostics": [],
        }

    fetcher = quote_fetcher or _fetch_yahoo_quote_rows
    db_map = db_previous_close_map
    if db_map is None:
        db_map = _load_db_previous_close_map(normalized_symbols, host=host, user=user, password=password, port=port)
    normalized_db_map = {_normalize_symbol(key): dict(value or {}) for key, value in db_map.items()}
    profiles = profile_map
    if profiles is None:
        profiles = _load_asset_profile_evidence_map(normalized_symbols, host=host, user=user, password=password, port=port)
    normalized_profiles = {_normalize_symbol(key): dict(value or {}) for key, value in profiles.items()}
    history_map = _fetch_history_evidence_map(normalized_symbols, downloader=history_downloader)

    diagnostics: list[dict[str, Any]] = []
    for symbol in normalized_symbols:
        try:
            quote_rows = fetcher([symbol])
            quote_row = next((row for row in quote_rows if _normalize_symbol(row.get("symbol")) == symbol), None)
            quote_error = None
        except Exception as exc:
            quote_row = None
            quote_error = str(exc)
        quote_latest_price = _safe_float((quote_row or {}).get("regularMarketPrice"))
        quote_previous_close = _safe_float((quote_row or {}).get("regularMarketPreviousClose"))
        quote_status = "ok" if quote_row and quote_latest_price is not None else "missing"
        if quote_error:
            quote_status = "error"

        history = history_map.get(
            symbol,
            {
                "status": "missing",
                "latest_price": None,
                "previous_close": None,
                "latest_price_date": None,
                "detail": "5d daily history was not checked",
            },
        )
        db_price = normalized_db_map.get(symbol, {})
        needs_fast_info = (
            quote_latest_price is None
            and history.get("latest_price") is None
            and db_price.get("previous_close") is None
        )
        fast_info = (
            _fetch_fast_info_evidence(symbol, ticker_factory=ticker_factory)
            if needs_fast_info
            else {"status": "skipped", "latest_price": None, "previous_close": None, "detail": "alternate price evidence already found"}
        )
        profile = normalized_profiles.get(symbol, {})
        diagnosis, confidence, evidence_summary = _classify_quote_gap_diagnostic(
            quote_status=quote_status,
            quote_latest_price=quote_latest_price,
            quote_previous_close=quote_previous_close,
            fast_info=fast_info,
            history=history,
            db_price=db_price,
            profile=profile,
        )
        diagnostics.append(
            {
                "Symbol": symbol,
                "Diagnosis": diagnosis,
                "Confidence": round(confidence, 2),
                "Evidence Summary": evidence_summary,
                "Recommended Action": _quote_gap_recommended_action(diagnosis),
                "Quote Single Status": quote_status,
                "Fast Info Status": fast_info.get("status") or "-",
                "History Status": history.get("status") or "-",
                "DB Price Status": "ok" if db_price.get("previous_close") is not None else "missing",
                "Profile Status": profile.get("status") or "-",
                "Quote Price": quote_latest_price,
                "Fast Info Price": fast_info.get("latest_price"),
                "History Price": history.get("latest_price"),
                "DB Latest Price": db_price.get("previous_close"),
                "DB Latest Date": db_price.get("previous_close_date"),
                "Profile Error": profile.get("error_msg") or "-",
                "Provider Detail": quote_error or fast_info.get("detail") or history.get("detail") or "-",
            }
        )

    counts = Counter(str(row.get("Diagnosis") or "unknown") for row in diagnostics)
    return {
        "universe_code": universe_code,
        "interval_code": interval_code,
        "snapshot_time_utc": snapshot_time_utc,
        "symbols_requested": len(normalized_symbols),
        "symbols_processed": len(diagnostics),
        "diagnosis_counts": dict(counts),
        "diagnostics": diagnostics,
    }


def _market_data_issue_key(*, universe_code: str, symbol: str, issue_type: str) -> str:
    parts = [
        str(universe_code or "").strip().upper(),
        _normalize_symbol(symbol),
        str(issue_type or "").strip().lower(),
    ]
    return hashlib.sha256("|".join(parts).encode("utf-8")).hexdigest()


def build_quote_gap_issue_rows(
    diagnostics: Sequence[dict[str, Any]],
    *,
    universe_code: str,
    interval_code: str = DEFAULT_INTRADAY_INTERVAL,
    snapshot_time_utc: str | None = None,
    seen_at: str | None = None,
) -> list[dict[str, Any]]:
    normalized_universe = str(universe_code or "SP500").strip().upper()
    normalized_interval = str(interval_code or DEFAULT_INTRADAY_INTERVAL).strip()
    collected_at = seen_at or _timestamp_str()
    rows: list[dict[str, Any]] = []
    for item in diagnostics:
        symbol = _normalize_symbol(item.get("Symbol") or item.get("symbol"))
        diagnosis = str(item.get("Diagnosis") or item.get("diagnosis") or "").strip()
        if not symbol or not diagnosis:
            continue
        issue_type = "quote_gap"
        issue_key = _market_data_issue_key(
            universe_code=normalized_universe,
            symbol=symbol,
            issue_type=issue_type,
        )
        rows.append(
            {
                "issue_key": issue_key,
                "issue_type": issue_type,
                "universe_code": normalized_universe,
                "symbol": symbol,
                "interval_code": normalized_interval,
                "diagnosis": diagnosis,
                "latest_status": "active",
                "occurrence_count": 1,
                "first_seen_at": collected_at,
                "last_seen_at": collected_at,
                "last_snapshot_time_utc": snapshot_time_utc,
                "latest_confidence": _safe_float(item.get("Confidence") or item.get("confidence")),
                "latest_evidence": item.get("Evidence Summary") or item.get("evidence_summary"),
                "latest_recommended_action": item.get("Recommended Action") or item.get("recommended_action"),
                "raw_payload_json": _json_payload(item),
            }
        )
    return rows


def build_price_history_limit_issue_rows(
    evidence_rows: Sequence[dict[str, Any]],
    *,
    universe_code: str,
    seen_at: str | None = None,
) -> list[dict[str, Any]]:
    """Build durable evidence for symbols whose full provider window is still too short."""
    normalized_universe = str(universe_code or "SP500").strip().upper()
    collected_at = seen_at or _timestamp_str()
    rows: list[dict[str, Any]] = []
    for item in evidence_rows:
        symbol = _normalize_symbol(item.get("symbol"))
        if not symbol:
            continue
        period = str(item.get("period") or "").strip().lower()
        row_count = int(item.get("row_count") or 0)
        min_rows = int(item.get("min_rows") or 0)
        first_date = str(item.get("first_date") or "-")
        latest_date = str(item.get("latest_date") or "-")
        issue_type = "limited_price_history"
        payload = {
            "symbol": symbol,
            "period": period,
            "first_date": first_date,
            "latest_date": latest_date,
            "row_count": row_count,
            "min_rows": min_rows,
            "source": "yfinance OHLCV full-window refresh",
        }
        rows.append(
            {
                "issue_key": _market_data_issue_key(
                    universe_code=normalized_universe,
                    symbol=symbol,
                    issue_type=issue_type,
                ),
                "issue_type": issue_type,
                "universe_code": normalized_universe,
                "symbol": symbol,
                "interval_code": "1d",
                "diagnosis": "available_history_short",
                "latest_status": "active",
                "occurrence_count": 1,
                "first_seen_at": collected_at,
                "last_seen_at": collected_at,
                "last_snapshot_time_utc": None,
                "latest_confidence": 1.0,
                "latest_evidence": (
                    f"period={period or '-'}; rows={row_count}/{min_rows}; "
                    f"first={first_date}; latest={latest_date}"
                ),
                "latest_recommended_action": (
                    "Wait for additional trading history; do not repeat the same full-window refresh."
                ),
                "raw_payload_json": _json_payload(payload),
            }
        )
    return rows


def upsert_market_data_issue_rows(
    rows: Sequence[dict[str, Any]],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    normalized_rows = [dict(row) for row in rows if row.get("issue_key")]
    if not normalized_rows:
        return 0
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_data_issue",
            MARKET_INTELLIGENCE_SCHEMAS["market_data_issue"],
            DB_META,
        )
        sql = """
        INSERT INTO market_data_issue (
          issue_key, issue_type, universe_code, symbol, interval_code,
          diagnosis, latest_status, occurrence_count,
          first_seen_at, last_seen_at, last_snapshot_time_utc,
          latest_confidence, latest_evidence, latest_recommended_action, raw_payload_json
        ) VALUES (
          %(issue_key)s, %(issue_type)s, %(universe_code)s, %(symbol)s, %(interval_code)s,
          %(diagnosis)s, %(latest_status)s, %(occurrence_count)s,
          %(first_seen_at)s, %(last_seen_at)s, %(last_snapshot_time_utc)s,
          %(latest_confidence)s, %(latest_evidence)s, %(latest_recommended_action)s, %(raw_payload_json)s
        )
        ON DUPLICATE KEY UPDATE
          universe_code = VALUES(universe_code),
          symbol = VALUES(symbol),
          interval_code = VALUES(interval_code),
          diagnosis = VALUES(diagnosis),
          latest_status = VALUES(latest_status),
          occurrence_count = occurrence_count + 1,
          last_seen_at = VALUES(last_seen_at),
          last_snapshot_time_utc = VALUES(last_snapshot_time_utc),
          latest_confidence = VALUES(latest_confidence),
          latest_evidence = VALUES(latest_evidence),
          latest_recommended_action = VALUES(latest_recommended_action),
          raw_payload_json = VALUES(raw_payload_json)
        """
        db.executemany(sql, normalized_rows)
        return len(normalized_rows)
    finally:
        db.close()


def load_market_data_issues(
    *,
    universe_code: str | None = None,
    symbols: Sequence[Any] | None = None,
    issue_type: str = "quote_gap",
    limit: int = 100,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> list[dict[str, Any]]:
    clauses = ["issue_type = %s"]
    params: list[Any] = [str(issue_type or "quote_gap").strip().lower()]
    normalized_universe = str(universe_code or "").strip().upper()
    if normalized_universe:
        clauses.append("universe_code = %s")
        params.append(normalized_universe)
    normalized_symbols = _normalize_symbol_list(symbols, max_symbols=500) if symbols else []
    if normalized_symbols:
        placeholders = ",".join(["%s"] * len(normalized_symbols))
        clauses.append(f"symbol IN ({placeholders})")
        params.extend(normalized_symbols)
    params.append(max(1, int(limit or 100)))
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_META)
        sync_table_schema(
            db,
            "market_data_issue",
            MARKET_INTELLIGENCE_SCHEMAS["market_data_issue"],
            DB_META,
        )
        return db.query(
            f"""
            SELECT
              universe_code, symbol, issue_type, diagnosis, latest_status,
              occurrence_count, first_seen_at, last_seen_at, last_snapshot_time_utc,
              latest_confidence, latest_evidence, latest_recommended_action
            FROM market_data_issue
            WHERE {" AND ".join(clauses)}
            ORDER BY last_seen_at DESC, occurrence_count DESC, symbol ASC
            LIMIT %s
            """,
            params,
        )
    finally:
        db.close()


def persist_quote_gap_diagnostics(
    diagnostics: Sequence[dict[str, Any]],
    *,
    universe_code: str,
    interval_code: str = DEFAULT_INTRADAY_INTERVAL,
    snapshot_time_utc: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    issue_rows = build_quote_gap_issue_rows(
        diagnostics,
        universe_code=universe_code,
        interval_code=interval_code,
        snapshot_time_utc=snapshot_time_utc,
    )
    rows_written = upsert_market_data_issue_rows(
        issue_rows,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    symbols = [row["symbol"] for row in issue_rows]
    history = load_market_data_issues(
        universe_code=universe_code,
        symbols=symbols,
        issue_type="quote_gap",
        limit=max(len(symbols), 1),
        host=host,
        user=user,
        password=password,
        port=port,
    )
    return {
        "rows_written": rows_written,
        "issues": history,
    }


def _symbol_frame(frame: pd.DataFrame, symbol: str) -> pd.DataFrame:
    if frame is None or frame.empty:
        return pd.DataFrame()
    if isinstance(frame.columns, pd.MultiIndex):
        if symbol in frame.columns.get_level_values(0):
            out = frame[symbol]
        else:
            return pd.DataFrame()
    else:
        out = frame
    if not isinstance(out, pd.DataFrame):
        return pd.DataFrame()
    return out.dropna(how="all")


def _latest_close_row(frame: pd.DataFrame) -> tuple[str | None, float | None, int | None]:
    if frame.empty or "Close" not in frame.columns:
        return None, None, None
    close = pd.to_numeric(frame["Close"], errors="coerce").dropna()
    if close.empty:
        return None, None, None
    index = close.index[-1]
    volume = None
    if "Volume" in frame.columns:
        try:
            volume = _safe_int(frame.loc[index, "Volume"])
        except Exception:
            volume = None
    return _to_utc_naive(index), _safe_float(close.iloc[-1]), volume


def _previous_close(daily_frame: pd.DataFrame, quote_time_utc: str | None) -> float | None:
    if daily_frame.empty or "Close" not in daily_frame.columns:
        return None
    close = pd.to_numeric(daily_frame["Close"], errors="coerce").dropna()
    if close.empty:
        return None
    if quote_time_utc:
        quote_date = pd.Timestamp(quote_time_utc).date()
        prior = close[[pd.Timestamp(idx).date() < quote_date for idx in close.index]]
        if not prior.empty:
            return _safe_float(prior.iloc[-1])
    if len(close) >= 2:
        return _safe_float(close.iloc[-2])
    return None


def _build_quote_snapshot_row(
    *,
    universe_code: str,
    symbol: str,
    quote_symbol: str | None = None,
    interval_code: str,
    snapshot_time_utc: str,
    quote_row: dict[str, Any] | None,
    db_previous_close: dict[str, Any] | None = None,
) -> dict[str, Any]:
    quote_row = dict(quote_row or {})
    db_previous_close = dict(db_previous_close or {})
    normalized_quote_symbol = _normalize_symbol(quote_symbol or symbol) or symbol
    latest_price = _safe_float(quote_row.get("regularMarketPrice"))
    previous_close = _safe_float(quote_row.get("regularMarketPreviousClose"))
    previous_source = "quote"
    if previous_close is None or previous_close <= 0:
        previous_close = _safe_float(db_previous_close.get("previous_close"))
        previous_source = "db_previous_close"
    quote_time_utc = _epoch_to_utc_naive(quote_row.get("regularMarketTime")) or snapshot_time_utc
    volume = _safe_int(quote_row.get("regularMarketVolume"))

    status = "ok"
    error_msg = None
    if not quote_row:
        status = "missing"
        error_msg = "missing quote row"
    elif latest_price is None:
        status = "missing"
        error_msg = "missing latest quote price"
    elif previous_close is None or previous_close <= 0:
        status = "missing"
        error_msg = "missing previous close"

    return_pct = None
    if status == "ok" and latest_price is not None and previous_close:
        return_pct = (latest_price / previous_close - 1.0) * 100.0

    market_state = quote_row.get("marketState") or ""
    source_ref = f"yahoo_quote_v7;previous_close={previous_source}"
    if normalized_quote_symbol != symbol:
        source_ref += f";alias_symbol={normalized_quote_symbol}"
    if market_state:
        source_ref += f";market_state={market_state}"
    return {
        "universe_code": universe_code,
        "symbol": symbol,
        "quote_symbol": normalized_quote_symbol,
        "interval_code": interval_code,
        "snapshot_time_utc": snapshot_time_utc,
        "quote_time_utc": quote_time_utc,
        "source": "yahoo_quote",
        "source_ref": source_ref,
        "previous_close": previous_close,
        "latest_price": latest_price,
        "return_pct": return_pct,
        "volume": volume,
        "provider_status": status,
        "error_msg": error_msg,
    }


def _build_snapshot_row(
    *,
    universe_code: str,
    symbol: str,
    interval_code: str,
    snapshot_time_utc: str,
    intraday_frame: pd.DataFrame,
    daily_frame: pd.DataFrame,
) -> dict[str, Any]:
    quote_time_utc, latest_price, volume = _latest_close_row(intraday_frame)
    previous_close = _previous_close(daily_frame, quote_time_utc)
    source_ref = "yfinance.download(period=1d/10d)"
    status = "ok"
    error_msg = None
    if latest_price is None:
        daily_quote_time, daily_latest, daily_volume = _latest_close_row(daily_frame)
        quote_time_utc = daily_quote_time
        latest_price = daily_latest
        volume = volume if volume is not None else daily_volume
        source_ref = "yfinance.download(daily_fallback)"
    if latest_price is None:
        status = "missing"
        error_msg = "missing latest price"
    elif previous_close is None or previous_close <= 0:
        status = "missing"
        error_msg = "missing previous close"

    return_pct = None
    if status == "ok" and latest_price is not None and previous_close:
        return_pct = (latest_price / previous_close - 1.0) * 100.0

    return {
        "universe_code": universe_code,
        "symbol": symbol,
        "quote_symbol": symbol,
        "interval_code": interval_code,
        "snapshot_time_utc": snapshot_time_utc,
        "quote_time_utc": quote_time_utc,
        "source": "yfinance",
        "source_ref": source_ref,
        "previous_close": previous_close,
        "latest_price": latest_price,
        "return_pct": return_pct,
        "volume": volume,
        "provider_status": status,
        "error_msg": error_msg,
    }


def _collect_quote_snapshot_rows(
    symbols: list[str],
    *,
    universe_code: str,
    interval_code: str,
    snapshot_time: str,
    quote_batch_size: int,
    quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    previous_close_map: dict[str, dict[str, Any]] | None = None,
    alias_map: dict[str, dict[str, Any]] | None = None,
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    fetcher = quote_fetcher or _fetch_yahoo_quote_rows
    previous_close_map = previous_close_map or {}
    alias_map = alias_map or {}
    rows: list[dict[str, Any]] = []
    failed_symbols: list[str] = []
    batches: list[dict[str, Any]] = []
    for batch in _chunked(symbols, max(1, int(quote_batch_size))):
        batch_started = datetime.now(UTC)
        quote_symbols_by_source = {
            symbol: _normalize_symbol(dict(alias_map.get(symbol) or {}).get("alias_symbol") or symbol) or symbol
            for symbol in batch
        }
        quote_request_symbols = list(dict.fromkeys(quote_symbols_by_source.values()))
        quote_rows = fetcher(quote_request_symbols)
        quote_map = {
            _normalize_symbol(row.get("symbol")): row
            for row in quote_rows
            if _normalize_symbol(row.get("symbol"))
        }
        batches.append(
            {
                "requested": len(batch),
                "quote_requested": len(quote_request_symbols),
                "returned": len(quote_map),
                "duration_sec": round((datetime.now(UTC) - batch_started).total_seconds(), 3),
            }
        )
        for symbol in batch:
            quote_symbol = quote_symbols_by_source.get(symbol) or symbol
            row = _build_quote_snapshot_row(
                universe_code=universe_code,
                symbol=symbol,
                quote_symbol=quote_symbol,
                interval_code=interval_code,
                snapshot_time_utc=snapshot_time,
                quote_row=quote_map.get(quote_symbol),
                db_previous_close=previous_close_map.get(symbol),
            )
            if row["provider_status"] != "ok":
                failed_symbols.append(symbol)
            rows.append(row)
    return rows, failed_symbols, {"quote_batches": batches}


def _collect_yfinance_snapshot_rows(
    symbols: list[str],
    *,
    universe_code: str,
    interval_code: str,
    snapshot_time: str,
    chunk_size: int,
    downloader: Callable[..., pd.DataFrame],
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    failed_symbols: list[str] = []
    batches: list[dict[str, Any]] = []
    for batch in _chunked(symbols, max(1, int(chunk_size))):
        batch_started = datetime.now(UTC)
        intraday = downloader(batch, period="1d", interval=interval_code, progress=False)
        daily = downloader(batch, period="10d", interval="1d", progress=False)
        batches.append(
            {
                "requested": len(batch),
                "duration_sec": round((datetime.now(UTC) - batch_started).total_seconds(), 3),
            }
        )
        for symbol in batch:
            row = _build_snapshot_row(
                universe_code=universe_code,
                symbol=symbol,
                interval_code=interval_code,
                snapshot_time_utc=snapshot_time,
                intraday_frame=_symbol_frame(intraday, symbol),
                daily_frame=_symbol_frame(daily, symbol),
            )
            if row["provider_status"] != "ok":
                failed_symbols.append(symbol)
            rows.append(row)
    return rows, failed_symbols, {"yfinance_batches": batches}


def upsert_intraday_snapshot_rows(
    rows: list[dict[str, Any]],
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    if not rows:
        return 0
    db = _db(host, user, password, port)
    try:
        db.use_db(DB_PRICE)
        sync_table_schema(
            db,
            "market_intraday_snapshot",
            MARKET_INTELLIGENCE_SCHEMAS["market_intraday_snapshot"],
            DB_PRICE,
        )
        sql = """
        INSERT INTO market_intraday_snapshot (
          universe_code, symbol, quote_symbol, interval_code, snapshot_time_utc, quote_time_utc,
          source, source_ref, previous_close, latest_price, return_pct, volume,
          provider_status, error_msg
        ) VALUES (
          %(universe_code)s, %(symbol)s, %(quote_symbol)s, %(interval_code)s, %(snapshot_time_utc)s, %(quote_time_utc)s,
          %(source)s, %(source_ref)s, %(previous_close)s, %(latest_price)s, %(return_pct)s, %(volume)s,
          %(provider_status)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          quote_symbol = VALUES(quote_symbol),
          quote_time_utc = VALUES(quote_time_utc),
          source = VALUES(source),
          source_ref = VALUES(source_ref),
          previous_close = VALUES(previous_close),
          latest_price = VALUES(latest_price),
          return_pct = VALUES(return_pct),
          volume = VALUES(volume),
          provider_status = VALUES(provider_status),
          error_msg = VALUES(error_msg)
        """
        db.executemany(sql, rows)
        return len(rows)
    finally:
        db.close()


def _portfolio_snapshot_minute(value: datetime | None = None) -> str:
    instant = value or _utc_now()
    if instant.tzinfo is None:
        instant = instant.replace(tzinfo=UTC)
    return _timestamp_str(
        instant.astimezone(UTC).replace(second=0, microsecond=0)
    )


def _portfolio_quote_error_rows(
    *,
    symbols: Sequence[str],
    universe_code: str,
    interval_code: str,
    snapshot_time_utc: str,
    source_ref: str,
    error: BaseException,
) -> list[dict[str, Any]]:
    return [
        {
            "universe_code": universe_code,
            "symbol": symbol,
            "quote_symbol": symbol,
            "interval_code": interval_code,
            "snapshot_time_utc": snapshot_time_utc,
            "quote_time_utc": None,
            "source": "yahoo_quote",
            "source_ref": f"{source_ref};yahoo_quote_v7;batch_error",
            "previous_close": None,
            "latest_price": None,
            "return_pct": None,
            "volume": None,
            "provider_status": "error",
            "error_msg": str(error)[:2000],
        }
        for symbol in symbols
    ]


def collect_and_store_symbol_intraday_snapshot(
    *,
    symbols: Sequence[str],
    universe_code: str,
    source_ref: str,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    quote_batch_size: int = 200,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    snapshot_time_utc: datetime | None = None,
    upsert: Callable[[list[dict[str, Any]]], int] | None = None,
    previous_close_loader: Callable[[list[str]], dict[str, dict[str, Any]]] | None = None,
    alias_loader: Callable[[list[str]], dict[str, dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    """Persist one bounded Today portfolio quote attempt by explicit symbols."""

    normalized_symbols = sorted(
        {
            symbol
            for value in symbols
            if (symbol := _normalize_symbol(value))
        }
    )
    if not 1 <= len(normalized_symbols) <= 10:
        raise ValueError(
            "Portfolio intraday symbols must contain 1 to 10 unique symbols."
        )
    normalized_universe = str(universe_code or "").strip().upper()
    if re.fullmatch(r"TODAY_[0-9A-F]{16}", normalized_universe) is None:
        raise ValueError(
            "Portfolio intraday universe_code must use TODAY_<16 hex>."
        )
    normalized_interval = str(interval or "").strip()
    if normalized_interval != "5m":
        raise ValueError("Portfolio intraday collection supports only 5m.")
    normalized_source_ref = str(source_ref or "").strip()
    if not normalized_source_ref or len(normalized_source_ref) > 128:
        raise ValueError("A compact portfolio source_ref is required.")

    started_at = datetime.now(UTC)
    snapshot_time = _portfolio_snapshot_minute(snapshot_time_utc)
    load_previous = previous_close_loader or (
        lambda requested: _load_db_previous_close_map(
            requested,
            host=host,
            user=user,
            password=password,
            port=port,
        )
    )
    load_aliases = alias_loader or (
        lambda requested: load_active_market_symbol_aliases(
            requested,
            host=host,
            user=user,
            password=password,
            port=port,
        )
    )
    try:
        rows, failed_symbols, diagnostics = _collect_quote_snapshot_rows(
            normalized_symbols,
            universe_code=normalized_universe,
            interval_code=normalized_interval,
            snapshot_time=snapshot_time,
            quote_batch_size=quote_batch_size,
            quote_fetcher=quote_fetcher,
            previous_close_map=load_previous(normalized_symbols),
            alias_map=load_aliases(normalized_symbols),
        )
        for row in rows:
            row["source_ref"] = (
                f"{normalized_source_ref};{row.get('source_ref') or 'yahoo_quote_v7'}"
            )[:255]
    except Exception as exc:
        rows = _portfolio_quote_error_rows(
            symbols=normalized_symbols,
            universe_code=normalized_universe,
            interval_code=normalized_interval,
            snapshot_time_utc=snapshot_time,
            source_ref=normalized_source_ref,
            error=exc,
        )
        failed_symbols = list(normalized_symbols)
        diagnostics = {"quote_batch_error": str(exc)}

    writer = upsert or (
        lambda values: upsert_intraday_snapshot_rows(
            values,
            host=host,
            user=user,
            password=password,
            port=port,
        )
    )
    rows_written = writer(rows)
    return {
        "rows_written": rows_written,
        "symbols_requested": len(normalized_symbols),
        "symbols_processed": len(normalized_symbols) - len(failed_symbols),
        "failed_symbols": failed_symbols,
        "snapshot_time_utc": snapshot_time,
        "universe_code": normalized_universe,
        "interval": normalized_interval,
        "source": "yahoo_quote",
        "method": "quote_fast",
        "duration_sec": round(
            (datetime.now(UTC) - started_at).total_seconds(),
            3,
        ),
        "diagnostics": diagnostics,
        "message": "Today portfolio intraday snapshot attempt stored.",
    }


def collect_and_store_market_intraday_snapshot(
    *,
    universe_code: str = "SP500",
    universe_limit: int | None = None,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    chunk_size: int = 100,
    quote_batch_size: int = 200,
    method: str = "quote_fast",
    fallback_to_yfinance: bool = True,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    universe_loader: Callable[[], list[dict[str, Any]]] | None = None,
    price_downloader: Callable[..., pd.DataFrame] | None = None,
    quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    normalized_universe, normalized_limit = _normalize_intraday_universe(universe_code, universe_limit)
    universe_label = MARKET_UNIVERSE_LABELS.get(normalized_universe, normalized_universe)
    normalized_interval = str(interval or DEFAULT_INTRADAY_INTERVAL).strip()
    if normalized_interval not in VALID_INTRADAY_INTERVALS:
        raise ValueError(f"Unsupported intraday interval: {interval!r}")
    normalized_method = str(method or "quote_fast").strip().lower()
    if normalized_method not in {"quote_fast", "yfinance_5m"}:
        raise ValueError(f"Unsupported snapshot method: {method!r}")

    started_at = datetime.now(UTC)
    sync_market_intelligence_tables(host=host, user=user, password=password, port=port)
    if universe_loader is not None:
        loader = universe_loader
    elif normalized_universe == "SP500":
        loader = lambda: load_market_universe_members("SP500", host=host, user=user, password=password, port=port)
    elif normalized_universe == "NASDAQ":
        loader = lambda: load_nasdaq_symbol_directory_universe_members(
            host=host,
            user=user,
            password=password,
            port=port,
        )
    else:
        loader = lambda: load_market_liquidity_universe_members(
            normalized_universe,
            universe_limit=normalized_limit,
            host=host,
            user=user,
            password=password,
            port=port,
        )
    members = loader()
    if not members and normalized_universe == "SP500":
        collect_and_store_sp500_universe(host=host, user=user, password=password, port=port)
        members = loader()
    metadata_by_symbol = {
        symbol: dict(row)
        for row in members
        if (symbol := _normalize_symbol(row.get("symbol")))
    }
    symbols = [_normalize_symbol(row.get("symbol")) for row in members if row.get("symbol")]
    symbols = sorted({symbol for symbol in symbols if symbol})
    if not symbols:
        return {
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "failed_symbols": [],
            "snapshot_time_utc": None,
            "universe_code": normalized_universe,
            "universe_limit": normalized_limit,
            "message": f"No {universe_label} symbols available.",
        }

    downloader = price_downloader or _download_prices
    snapshot_time = _timestamp_str(_utc_now())
    diagnostics: dict[str, Any] = {
        "method_requested": normalized_method,
        "universe_code": normalized_universe,
        "universe_limit": normalized_limit,
    }
    active_aliases: dict[str, dict[str, Any]] = {}
    ticker_alias_candidates: list[dict[str, Any]] = []
    snapshot_rows: list[dict[str, Any]]
    failed_symbols: list[str]
    source = "yfinance"
    method_used = "yfinance_5m"

    if normalized_method == "quote_fast" and price_downloader is None:
        active_aliases = load_active_market_symbol_aliases(
            symbols,
            host=host,
            user=user,
            password=password,
            port=port,
        )
        diagnostics["active_symbol_alias_count"] = len(active_aliases)
        previous_close_map = _load_db_previous_close_map(
            symbols,
            host=host,
            user=user,
            password=password,
            port=port,
        )
        try:
            snapshot_rows, failed_symbols, quote_diagnostics = _collect_quote_snapshot_rows(
                symbols,
                universe_code=normalized_universe,
                interval_code=normalized_interval,
                snapshot_time=snapshot_time,
                quote_batch_size=quote_batch_size,
                quote_fetcher=quote_fetcher,
                previous_close_map=previous_close_map,
                alias_map=active_aliases,
            )
            diagnostics.update(quote_diagnostics)
            source = "yahoo_quote"
            method_used = "quote_fast"
            missing_quote_symbols = [
                symbol
                for symbol in failed_symbols
                if str(
                    next(
                        (
                            row.get("error_msg")
                            for row in snapshot_rows
                            if row.get("symbol") == symbol and row.get("provider_status") != "ok"
                        ),
                        "",
                    )
                ).lower()
                == "missing quote row"
            ]
            if missing_quote_symbols:
                try:
                    ticker_alias_candidates = detect_market_symbol_alias_candidates(
                        missing_quote_symbols,
                        metadata_by_symbol=metadata_by_symbol,
                        quote_fetcher=quote_fetcher,
                    )
                    if ticker_alias_candidates:
                        upsert_market_symbol_aliases(
                            ticker_alias_candidates,
                            status="candidate",
                            host=host,
                            user=user,
                            password=password,
                            port=port,
                        )
                except Exception as exc:
                    diagnostics["ticker_alias_candidate_error"] = str(exc)
            diagnostics["ticker_alias_candidate_count"] = len(ticker_alias_candidates)
        except Exception as exc:
            diagnostics["quote_fast_error"] = str(exc)
            if not fallback_to_yfinance:
                raise
            snapshot_rows, failed_symbols, fallback_diagnostics = _collect_yfinance_snapshot_rows(
                symbols,
                universe_code=normalized_universe,
                interval_code=normalized_interval,
                snapshot_time=snapshot_time,
                chunk_size=chunk_size,
                downloader=downloader,
            )
            diagnostics.update(fallback_diagnostics)
            source = "yfinance"
            method_used = "yfinance_5m_fallback"
    else:
        snapshot_rows, failed_symbols, yfinance_diagnostics = _collect_yfinance_snapshot_rows(
            symbols,
            universe_code=normalized_universe,
            interval_code=normalized_interval,
            snapshot_time=snapshot_time,
            chunk_size=chunk_size,
            downloader=downloader,
        )
        diagnostics.update(yfinance_diagnostics)

    rows_written = upsert_intraday_snapshot_rows(
        snapshot_rows,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    return {
        "rows_written": rows_written,
        "symbols_requested": len(symbols),
        "symbols_processed": len(symbols) - len(failed_symbols),
        "failed_symbols": failed_symbols,
        "snapshot_time_utc": snapshot_time,
        "universe_code": normalized_universe,
        "universe_limit": normalized_limit,
        "interval": normalized_interval,
        "source": source,
        "method": method_used,
        "active_symbol_aliases": [
            {"source_symbol": source_symbol, "alias_symbol": alias.get("alias_symbol")}
            for source_symbol, alias in sorted(active_aliases.items())
        ],
        "ticker_alias_candidates": ticker_alias_candidates,
        "duration_sec": round((datetime.now(UTC) - started_at).total_seconds(), 3),
        "diagnostics": diagnostics,
        "message": f"{universe_label} intraday snapshot completed.",
    }


def collect_and_store_sp500_intraday_snapshot(
    *,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    chunk_size: int = 100,
    quote_batch_size: int = 200,
    method: str = "quote_fast",
    fallback_to_yfinance: bool = True,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    universe_loader: Callable[[], list[dict[str, Any]]] | None = None,
    price_downloader: Callable[..., pd.DataFrame] | None = None,
    quote_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
) -> dict[str, Any]:
    return collect_and_store_market_intraday_snapshot(
        universe_code="SP500",
        universe_limit=500,
        interval=interval,
        chunk_size=chunk_size,
        quote_batch_size=quote_batch_size,
        method=method,
        fallback_to_yfinance=fallback_to_yfinance,
        host=host,
        user=user,
        password=password,
        port=port,
        universe_loader=universe_loader,
        price_downloader=price_downloader,
        quote_fetcher=quote_fetcher,
    )
