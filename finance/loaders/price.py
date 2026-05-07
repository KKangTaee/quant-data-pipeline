from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.db.mysql import MySQLClient
from finance.data.data import load_ohlcv_many_mysql

from ._common import normalize_date_range, normalize_timeframe, normalize_timestamp, resolve_loader_symbols


VALID_PRICE_FIELDS = {"open", "high", "low", "close", "adj_close", "volume", "dividends", "stock_splits"}
VALID_LATEST_PRICE_FIELDS = {"open", "high", "low", "close", "adj_close"}


def load_price_history(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> pd.DataFrame:
    """
    Load long-form OHLCV history from MySQL for the resolved symbol set.
    """
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    start_ts, end_ts = normalize_date_range(start=start, end=end)
    normalized_timeframe = normalize_timeframe(timeframe)

    df = load_ohlcv_many_mysql(
        resolved_symbols,
        start=start_ts.strftime("%Y-%m-%d") if start_ts is not None else None,
        end=end_ts.strftime("%Y-%m-%d") if end_ts is not None else None,
        timeframe=normalized_timeframe,
    )
    if df.empty:
        return df

    ordered_columns = [
        "symbol",
        "date",
        "open",
        "high",
        "low",
        "close",
        "adj_close",
        "volume",
        "dividends",
        "stock_splits",
    ]
    return df[ordered_columns]


def load_price_matrix(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    field: str = "close",
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> pd.DataFrame:
    """
    Load a wide price matrix indexed by date and columned by symbol.
    """
    normalized_field = str(field).strip().lower()
    if normalized_field not in VALID_PRICE_FIELDS:
        raise ValueError(f"Unsupported price field: {field!r}")

    history = load_price_history(
        symbols=symbols,
        universe_source=universe_source,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    if history.empty:
        return history

    matrix = history.pivot(index="date", columns="symbol", values=normalized_field).sort_index()
    matrix.columns.name = None
    return matrix


def load_latest_prices(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
    field: str = "close",
) -> pd.DataFrame:
    """
    Load one latest available OHLC price row per symbol from MySQL.
    """
    normalized_field = str(field).strip().lower()
    if normalized_field not in VALID_LATEST_PRICE_FIELDS:
        raise ValueError(f"Unsupported latest price field: {field!r}")

    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    normalized_timeframe = normalize_timeframe(timeframe)
    end_ts = normalize_timestamp(end, field_name="end") if end is not None else None

    if not resolved_symbols:
        return pd.DataFrame()

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_price")
        placeholders = ",".join(["%s"] * len(resolved_symbols))
        latest_where = [f"symbol IN ({placeholders})", "timeframe = %s"]
        latest_params: list[object] = list(resolved_symbols) + [normalized_timeframe]
        if end_ts is not None:
            latest_where.append("`date` <= %s")
            latest_params.append(end_ts.strftime("%Y-%m-%d"))

        sql = f"""
        SELECT
            ph.symbol,
            ph.`date` AS latest_date,
            ph.{normalized_field} AS price,
            ph.close,
            ph.adj_close
        FROM nyse_price_history ph
        INNER JOIN (
            SELECT symbol, MAX(`date`) AS latest_date
            FROM nyse_price_history
            WHERE {" AND ".join(latest_where)}
            GROUP BY symbol
        ) latest
            ON ph.symbol = latest.symbol
           AND ph.`date` = latest.latest_date
        WHERE ph.timeframe = %s
        ORDER BY ph.symbol ASC
        """
        rows = db.query(sql, latest_params + [normalized_timeframe])
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["latest_date"] = pd.to_datetime(df["latest_date"], errors="coerce")
    return df[["symbol", "latest_date", "price", "close", "adj_close"]]


def load_price_freshness_summary(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> pd.DataFrame:
    """
    Load per-symbol latest available price dates from MySQL.

    This is intended for preflight freshness checks where loading the full
    price history would be unnecessarily expensive.
    """
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    normalized_timeframe = normalize_timeframe(timeframe)
    end_ts = normalize_timestamp(end, field_name="end") if end is not None else None

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_price")
        placeholders = ",".join(["%s"] * len(resolved_symbols))
        where = [f"symbol IN ({placeholders})", "timeframe = %s"]
        params: list[object] = list(resolved_symbols) + [normalized_timeframe]

        if end_ts is not None:
            where.append("Date <= %s")
            params.append(end_ts.strftime("%Y-%m-%d"))

        sql = f"""
        SELECT
            symbol,
            MAX(Date) AS latest_date,
            COUNT(*) AS row_count
        FROM nyse_price_history
        WHERE {" AND ".join(where)}
        GROUP BY symbol
        ORDER BY symbol ASC
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    df["latest_date"] = pd.to_datetime(df["latest_date"], errors="coerce")
    return df


def load_latest_market_date(
    *,
    end: str | None = None,
    timeframe: str = "1d",
) -> pd.Timestamp | None:
    """
    Load the latest trading date present in MySQL up to the requested end date.

    This is used by preflight checks so weekend or holiday end dates can be
    compared against the last actual market session instead of being treated as
    universal staleness.
    """
    normalized_timeframe = normalize_timeframe(timeframe)
    end_ts = normalize_timestamp(end, field_name="end") if end is not None else None

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_price")
        where = ["timeframe = %s"]
        params: list[object] = [normalized_timeframe]

        if end_ts is not None:
            where.append("Date <= %s")
            params.append(end_ts.strftime("%Y-%m-%d"))

        sql = f"""
        SELECT MAX(Date) AS latest_market_date
        FROM nyse_price_history
        WHERE {" AND ".join(where)}
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    if not rows:
        return None

    latest_market_date = rows[0].get("latest_market_date")
    if latest_market_date is None:
        return None
    return pd.to_datetime(latest_market_date, errors="coerce")
