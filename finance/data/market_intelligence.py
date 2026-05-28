from __future__ import annotations

from io import StringIO
from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd
import yfinance as yf

from .db.mysql import MySQLClient
from .db.schema import MARKET_INTELLIGENCE_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
DB_PRICE = "finance_price"
SP500_SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SP500_SOURCE = "wikipedia_sp500_constituents"
DEFAULT_INTRADAY_INTERVAL = "5m"
VALID_INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}


def _utc_now() -> datetime:
    return datetime.now(UTC).replace(second=0, microsecond=0)


def _timestamp_str(value: datetime | None = None) -> str:
    return (value or _utc_now()).strftime("%Y-%m-%d %H:%M:%S")


def _normalize_symbol(value: Any) -> str:
    return str(value or "").strip().upper().replace(".", "-")


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


def collect_and_store_sp500_intraday_snapshot(
    *,
    interval: str = DEFAULT_INTRADAY_INTERVAL,
    chunk_size: int = 100,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
    universe_loader: Callable[[], list[dict[str, Any]]] | None = None,
    price_downloader: Callable[..., pd.DataFrame] | None = None,
) -> dict[str, Any]:
    normalized_interval = str(interval or DEFAULT_INTRADAY_INTERVAL).strip()
    if normalized_interval not in VALID_INTRADAY_INTERVALS:
        raise ValueError(f"Unsupported intraday interval: {interval!r}")

    sync_market_intelligence_tables(host=host, user=user, password=password, port=port)
    loader = universe_loader or (
        lambda: load_market_universe_members("SP500", host=host, user=user, password=password, port=port)
    )
    members = loader()
    if not members:
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
            "message": "No S&P 500 symbols available.",
        }

    downloader = price_downloader or _download_prices
    snapshot_time = _timestamp_str(_utc_now())
    snapshot_rows: list[dict[str, Any]] = []
    failed_symbols: list[str] = []
    for batch in _chunked(symbols, max(1, int(chunk_size))):
        intraday = downloader(batch, period="1d", interval=normalized_interval, progress=False)
        daily = downloader(batch, period="10d", interval="1d", progress=False)
        for symbol in batch:
            row = _build_snapshot_row(
                universe_code="SP500",
                symbol=symbol,
                interval_code=normalized_interval,
                snapshot_time_utc=snapshot_time,
                intraday_frame=_symbol_frame(intraday, symbol),
                daily_frame=_symbol_frame(daily, symbol),
            )
            if row["provider_status"] != "ok":
                failed_symbols.append(symbol)
            snapshot_rows.append(row)

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
        "interval": normalized_interval,
        "source": "yfinance",
        "message": "S&P 500 intraday snapshot completed.",
    }
