from __future__ import annotations

import html
import json
import re
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
OPERABILITY_TABLE = "etf_operability_snapshot"
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

    for symbol in symbols:
        source_info = OFFICIAL_PROVIDER_SOURCES.get(symbol)
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
