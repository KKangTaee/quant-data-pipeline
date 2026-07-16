"""DB-only daily futures reader for economic-cycle asset confirmation."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from finance.data.db.mysql import MySQLClient


QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
DB_PRICE = "finance_price"
DEFAULT_ASSET_SYMBOLS = ("GC=F", "DX-Y.NYB")


def _query(
    database: str,
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(database, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(database)
        return db.query(sql, params)
    finally:
        db.close()


def load_economic_cycle_asset_prices(
    *,
    symbols: Sequence[str] = DEFAULT_ASSET_SYMBOLS,
    lookback_rows: int = 80,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Return a bounded daily close window per symbol without provider access."""

    normalized = tuple(
        dict.fromkeys(str(symbol or "").strip().upper() for symbol in symbols)
    )
    normalized = tuple(symbol for symbol in normalized if symbol)
    if not normalized:
        return []
    bounded_rows = max(64, min(int(lookback_rows), 512))
    placeholders = ", ".join(["%s"] * len(normalized))
    sql = f"""
    WITH ranked_rows AS (
      SELECT provider_symbol, candle_time_utc, close, source, provider_status,
             ROW_NUMBER() OVER (
               PARTITION BY provider_symbol
               ORDER BY candle_time_utc DESC
             ) AS row_rank
      FROM futures_ohlcv
      WHERE interval_code = '1d'
        AND provider_symbol IN ({placeholders})
        AND close IS NOT NULL
        AND provider_status = 'ok'
    )
    SELECT provider_symbol, candle_time_utc, close, source, provider_status
    FROM ranked_rows
    WHERE row_rank <= %s
    ORDER BY provider_symbol ASC, candle_time_utc ASC
    """
    rows = _query(
        DB_PRICE,
        sql,
        (*normalized, bounded_rows),
        query_fn=query_fn,
    )
    return [dict(row) for row in rows]
