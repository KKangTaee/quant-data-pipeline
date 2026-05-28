from __future__ import annotations

from collections.abc import Callable, Iterable, Sequence
from datetime import UTC, datetime
from io import StringIO
from typing import Any
from urllib.request import Request, urlopen

import pandas as pd
import yfinance as yf
from yfinance.data import YfData

from .db.mysql import MySQLClient
from .db.schema import MARKET_INTELLIGENCE_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
DB_PRICE = "finance_price"
SP500_SOURCE_URL = "https://en.wikipedia.org/wiki/List_of_S%26P_500_companies"
SP500_SOURCE = "wikipedia_sp500_constituents"
DEFAULT_INTRADAY_INTERVAL = "5m"
YAHOO_QUOTE_URL = "https://query1.finance.yahoo.com/v7/finance/quote"
VALID_INTRADAY_INTERVALS = {"1m", "2m", "5m", "15m", "30m", "60m", "90m", "1h"}
MARKET_CAP_UNIVERSE_LIMITS = {"TOP1000": 1000, "TOP2000": 2000}
MARKET_UNIVERSE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
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
