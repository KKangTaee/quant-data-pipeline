from __future__ import annotations

import hashlib
import json
import re
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, date, datetime, timedelta
from io import StringIO
from typing import Any
from urllib.parse import urljoin
from urllib.request import Request, urlopen

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
EARNINGS_CALENDAR_SOURCE = "yfinance_calendar"
EARNINGS_CALENDAR_SOURCE_URL = "https://finance.yahoo.com/calendar/earnings"
DEFAULT_INTRADAY_INTERVAL = "5m"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
VALID_INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
MARKET_CAP_UNIVERSE_LIMITS = {"TOP1000": 1000, "TOP2000": 2000}
MARKET_UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
}
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


def _json_payload(value: Any) -> str | None:
    if value in (None, ""):
        return None
    if isinstance(value, str):
        try:
            parsed = json.loads(value)
        except json.JSONDecodeError:
            parsed = {"raw": value}
        return json.dumps(parsed, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)
    return json.dumps(value, ensure_ascii=False, sort_keys=True, separators=(",", ":"), default=str)


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
        row = {
            "event_date": event_date,
            "event_type": event_type,
            "symbol": _normalize_event_symbol(item.get("symbol")),
            "title": title,
            "source": source,
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
          source, source_url, confidence, collected_at, raw_payload_json
        ) VALUES (
          %(event_key)s, %(event_date)s, %(event_type)s, %(symbol)s, %(title)s,
          %(source)s, %(source_url)s, %(confidence)s, %(collected_at)s, %(raw_payload_json)s
        )
        ON DUPLICATE KEY UPDATE
          event_date = VALUES(event_date),
          event_type = VALUES(event_type),
          symbol = VALUES(symbol),
          title = VALUES(title),
          source = VALUES(source),
          source_url = VALUES(source_url),
          confidence = VALUES(confidence),
          collected_at = VALUES(collected_at),
          raw_payload_json = VALUES(raw_payload_json)
        """
        db.executemany(sql, normalized_rows)
        return len(normalized_rows)
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


def _parse_window_date(value: Any, *, default: date) -> date:
    parsed = _event_date_str(value)
    if not parsed:
        return default
    return datetime.strptime(parsed, "%Y-%m-%d").date()


def fetch_yfinance_earnings_calendar_events(
    symbols: str | Sequence[Any],
    *,
    start_date: str | date | None = None,
    end_date: str | date | None = None,
    lookahead_days: int = 120,
    max_symbols: int = 100,
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

    for symbol in normalized_symbols:
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
                continue
            for event_date in in_window_dates:
                events.append(
                    {
                        "event_date": event_date,
                        "event_type": "EARNINGS",
                        "symbol": symbol,
                        "title": f"{symbol} Earnings Release",
                        "source": EARNINGS_CALENDAR_SOURCE,
                        "source_url": f"https://finance.yahoo.com/quote/{symbol}/analysis",
                        "confidence": 0.65,
                        "raw_payload": {
                            "provider": EARNINGS_CALENDAR_SOURCE,
                            "provider_calendar": calendar,
                            "provider_earnings_dates": earnings_dates,
                            "event_date_basis": "yfinance_calendar_earnings_date",
                            "window_start": window_start.isoformat(),
                            "window_end": window_end.isoformat(),
                            "source_url": EARNINGS_CALENDAR_SOURCE_URL,
                        },
                    }
                )
        except Exception as exc:
            failed_symbols.append(f"{symbol}: {exc}")

    return {
        "source": EARNINGS_CALENDAR_SOURCE,
        "source_url": EARNINGS_CALENDAR_SOURCE_URL,
        "event_type": "EARNINGS",
        "method": "yfinance_ticker_calendar",
        "start_date": window_start.isoformat(),
        "end_date": window_end.isoformat(),
        "symbols_requested": len(normalized_symbols),
        "symbols_processed": len(normalized_symbols) - len(failed_symbols),
        "events": events,
        "events_found": len(events),
        "missing_symbols": missing_symbols,
        "failed_symbols": failed_symbols,
    }


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
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    source_symbols_loader: Callable[[], list[str]] | None = None,
    earnings_fetcher: Callable[..., dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Collect bounded upcoming earnings events and persist them to the common event calendar."""
    collected_at = _timestamp_str()
    normalized_source = str(symbol_source or "latest_movers").strip().lower()
    if symbols is not None:
        target_symbols = _normalize_symbol_list(symbols, max_symbols=max_symbols)
        normalized_source = "manual"
    else:
        loader = source_symbols_loader or (
            lambda: load_latest_intraday_mover_symbols(
                universe_code=universe_code,
                universe_limit=universe_limit,
                interval=interval,
                top_n=top_movers_limit,
                host=host,
                user=user,
                password=password,
                port=port,
            )
        )
        target_symbols = _normalize_symbol_list(loader(), max_symbols=max_symbols)

    if not target_symbols:
        return {
            "source": EARNINGS_CALENDAR_SOURCE,
            "source_url": EARNINGS_CALENDAR_SOURCE_URL,
            "event_type": "EARNINGS",
            "method": "yfinance_ticker_calendar",
            "symbol_source": normalized_source,
            "universe_code": universe_code,
            "rows_written": 0,
            "symbols_requested": 0,
            "symbols_processed": 0,
            "events_found": 0,
            "missing_symbols": [],
            "failed_symbols": [],
            "event_dates": [],
            "collected_at": collected_at,
            "message": "No target symbols were available for earnings calendar collection.",
        }

    fetcher = earnings_fetcher or fetch_yfinance_earnings_calendar_events
    result = fetcher(
        target_symbols,
        lookahead_days=lookahead_days,
        max_symbols=max_symbols,
    )
    events = [{**row, "collected_at": collected_at} for row in result.get("events", [])]
    rows_written = upsert_market_event_rows(events, host=host, user=user, password=password, port=port)
    event_dates = sorted({str(row["event_date"]) for row in events if row.get("event_date")})
    return {
        **result,
        "rows_written": rows_written,
        "symbol_source": normalized_source,
        "universe_code": universe_code,
        "universe_limit": universe_limit,
        "interval": interval,
        "top_movers_limit": top_movers_limit,
        "target_symbols": target_symbols,
        "event_dates": event_dates,
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
