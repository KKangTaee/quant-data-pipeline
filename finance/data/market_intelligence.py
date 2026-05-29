from __future__ import annotations

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
MACRO_CALENDAR_SOURCE = "official_macro_release_schedules"
EARNINGS_CALENDAR_SOURCE = "yfinance_calendar"
EARNINGS_CALENDAR_SOURCE_URL = "https://finance.yahoo.com/calendar/earnings"
NASDAQ_EARNINGS_CALENDAR_SOURCE = "nasdaq_earnings_calendar"
NASDAQ_EARNINGS_CALENDAR_API_URL = "https://api.nasdaq.com/api/calendar/earnings"
COMPANY_IR_EARNINGS_SOURCE = "company_ir_calendar"
EARNINGS_PROVIDER_ESTIMATE_CONFIDENCE = 0.65
EARNINGS_CROSS_CHECKED_CONFIDENCE = 0.75
EARNINGS_NOT_CONFIRMED_CONFIDENCE = 0.6
EARNINGS_STALE_ESTIMATE_DAYS = 14
DEFAULT_INTRADAY_INTERVAL = "5m"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
VALID_INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
MARKET_CAP_UNIVERSE_LIMITS = {"TOP1000": 1000, "TOP2000": 2000}
MARKET_UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
}
BLS_MACRO_RELEASE_TYPES = [
    {
        "event_type": "MACRO_CPI",
        "label": "CPI",
        "match": "consumer price index",
    },
    {
        "event_type": "MACRO_PPI",
        "label": "PPI",
        "match": "producer price index",
    },
    {
        "event_type": "MACRO_EMPLOYMENT",
        "label": "Employment Situation",
        "match": "employment situation",
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
    if normalized in MARKET_CAP_UNIVERSE_LIMITS:
        return normalized, MARKET_CAP_UNIVERSE_LIMITS[normalized]
    if universe_limit is not None:
        try:
            parsed_limit = int(universe_limit)
        except (TypeError, ValueError):
            parsed_limit = 1000
        return ("TOP2000", 2000) if parsed_limit >= 2000 else ("TOP1000", 1000)
    raise ValueError(f"Unsupported intraday universe: {universe_code!r}")


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
            "market_event_calendar",
            MARKET_INTELLIGENCE_SCHEMAS["market_event_calendar"],
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
          event_key, event_date, event_type, symbol, title,
          source, source_type, validation_status, event_status, superseded_by_event_key, superseded_at,
          source_url, confidence, collected_at, raw_payload_json
        ) VALUES (
          %(event_key)s, %(event_date)s, %(event_type)s, %(symbol)s, %(title)s,
          %(source)s, %(source_type)s, %(validation_status)s, %(event_status)s,
          %(superseded_by_event_key)s, %(superseded_at)s,
          %(source_url)s, %(confidence)s, %(collected_at)s, %(raw_payload_json)s
        )
        ON DUPLICATE KEY UPDATE
          event_date = VALUES(event_date),
          event_type = VALUES(event_type),
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
        if str(item["match"]) in normalized:
            return item
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
    confidence: float = 0.95,
    raw_payload: dict[str, Any] | None = None,
) -> dict[str, Any]:
    payload = dict(raw_payload or {})
    payload.setdefault("release_time_et", release_time_et)
    payload.setdefault("event_date_basis", "official_release_date")
    payload = _json_safe_payload_value(payload)
    return {
        "event_date": event_date,
        "event_type": event_type,
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


def parse_bea_gdp_calendar_events_from_html(
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
        if not _is_bea_gdp_release(release_title):
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
                event_type="MACRO_GDP",
                title=f"GDP: {release_title}",
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


def fetch_macro_calendar_events(
    *,
    years: Sequence[int] | None = None,
    include_bls: bool = True,
    include_bea: bool = True,
    bls_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
    bea_fetcher: Callable[..., list[dict[str, Any]]] | None = None,
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
            fetcher = bea_fetcher or fetch_bea_gdp_calendar_events
            events.extend(fetcher(years=years))
        except Exception as exc:
            failed_sources.append(f"BEA: {exc}")
    if not events:
        detail = "; ".join(failed_sources) if failed_sources else "no enabled source returned events"
        raise RuntimeError(f"No macro calendar events were collected: {detail}")
    return {
        "source": MACRO_CALENDAR_SOURCE,
        "source_url": ", ".join(
            [
                item
                for item in [
                    BLS_MACRO_CALENDAR_SOURCE_URL_TEMPLATE.format(
                        year=(int(years[0]) if years else datetime.now(UTC).year)
                    )
                    if include_bls
                    else None,
                    BEA_MACRO_CALENDAR_SOURCE_URL if include_bea else None,
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
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    macro_fetcher: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Collect official macro release dates and persist them to the common event calendar."""
    collected_at = _timestamp_str()
    fetcher = macro_fetcher or fetch_macro_calendar_events
    result = fetcher(years=years, include_bls=include_bls, include_bea=include_bea)
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
            row["confidence"] = confidence
            raw_payload = dict(row.get("raw_payload") or {})
            raw_payload["source_validation"] = validation_payload
            row["raw_payload"] = raw_payload

    return {
        "source": EARNINGS_CALENDAR_SOURCE,
        "source_url": EARNINGS_CALENDAR_SOURCE_URL,
        "event_type": "EARNINGS",
        "method": "yfinance_ticker_calendar",
        "validation_source": validation_source,
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
) -> tuple[list[str], str]:
    if symbols is not None:
        return _slice_symbols(symbols, offset=batch_offset, max_symbols=max_symbols), "manual"

    normalized_source = str(symbol_source or "latest_movers").strip().lower()
    if source_symbols_loader is not None:
        return _slice_symbols(source_symbols_loader(), offset=batch_offset, max_symbols=max_symbols), normalized_source

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

    source_to_universe = {
        "sp500": "SP500",
        "sp500_universe": "SP500",
        "s&p500": "SP500",
        "top1000": "TOP1000",
        "top2000": "TOP2000",
        "universe": universe_code,
    }
    resolved_universe = source_to_universe.get(normalized_source, universe_code)
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
    )

    if not target_symbols:
        return {
            "source": EARNINGS_CALENDAR_SOURCE,
            "source_url": EARNINGS_CALENDAR_SOURCE_URL,
            "event_type": "EARNINGS",
            "method": "yfinance_ticker_calendar",
            "symbol_source": normalized_source,
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
    events = [{**row, "collected_at": collected_at} for row in result.get("events", [])]
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
    interval_code: str,
    snapshot_time_utc: str,
    quote_row: dict[str, Any] | None,
    db_previous_close: dict[str, Any] | None = None,
) -> dict[str, Any]:
    quote_row = dict(quote_row or {})
    db_previous_close = dict(db_previous_close or {})
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
    if market_state:
        source_ref += f";market_state={market_state}"
    return {
        "universe_code": universe_code,
        "symbol": symbol,
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
) -> tuple[list[dict[str, Any]], list[str], dict[str, Any]]:
    fetcher = quote_fetcher or _fetch_yahoo_quote_rows
    previous_close_map = previous_close_map or {}
    rows: list[dict[str, Any]] = []
    failed_symbols: list[str] = []
    batches: list[dict[str, Any]] = []
    for batch in _chunked(symbols, max(1, int(quote_batch_size))):
        batch_started = datetime.now(UTC)
        quote_rows = fetcher(batch)
        quote_map = {
            _normalize_symbol(row.get("symbol")): row
            for row in quote_rows
            if _normalize_symbol(row.get("symbol"))
        }
        batches.append(
            {
                "requested": len(batch),
                "returned": len(quote_map),
                "duration_sec": round((datetime.now(UTC) - batch_started).total_seconds(), 3),
            }
        )
        for symbol in batch:
            row = _build_quote_snapshot_row(
                universe_code=universe_code,
                symbol=symbol,
                interval_code=interval_code,
                snapshot_time_utc=snapshot_time,
                quote_row=quote_map.get(symbol),
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
          universe_code, symbol, interval_code, snapshot_time_utc, quote_time_utc,
          source, source_ref, previous_close, latest_price, return_pct, volume,
          provider_status, error_msg
        ) VALUES (
          %(universe_code)s, %(symbol)s, %(interval_code)s, %(snapshot_time_utc)s, %(quote_time_utc)s,
          %(source)s, %(source_ref)s, %(previous_close)s, %(latest_price)s, %(return_pct)s, %(volume)s,
          %(provider_status)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
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
    else:
        loader = lambda: load_market_cap_universe_members(
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
    snapshot_rows: list[dict[str, Any]]
    failed_symbols: list[str]
    source = "yfinance"
    method_used = "yfinance_5m"

    if normalized_method == "quote_fast" and price_downloader is None:
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
            )
            diagnostics.update(quote_diagnostics)
            source = "yahoo_quote"
            method_used = "quote_fast"
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
