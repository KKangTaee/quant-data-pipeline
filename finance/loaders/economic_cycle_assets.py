"""DB-only daily futures reader for economic-cycle asset confirmation."""

from __future__ import annotations

from collections.abc import Callable, Sequence
from typing import Any

from finance.data.db.mysql import MySQLClient
from finance.loaders.macro import load_macro_series_observations


QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
DB_PRICE = "finance_price"
DEFAULT_ASSET_SYMBOLS = ("GC=F", "DX-Y.NYB")
DEFAULT_PATHWAY_SERIES = ("DGS2", "DGS10", "DFII10", "VIXCLS", "BAA10Y")


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
    lookback_rows: int = 1500,
    end_date: object = None,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Return a bounded daily close window per symbol without provider access."""

    normalized = tuple(
        dict.fromkeys(str(symbol or "").strip().upper() for symbol in symbols)
    )
    normalized = tuple(symbol for symbol in normalized if symbol)
    if not normalized:
        return []
    bounded_rows = max(315, min(int(lookback_rows), 2000))
    placeholders = ", ".join(["%s"] * len(normalized))
    end_clause = ""
    params: tuple[object, ...] = normalized
    if end_date is not None:
        end_clause = "AND candle_time_utc < DATE_ADD(%s, INTERVAL 1 DAY)"
        params = (*params, str(end_date)[:10])
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
        {end_clause}
    )
    SELECT provider_symbol, candle_time_utc, close, source, provider_status
    FROM ranked_rows
    WHERE row_rank <= %s
    ORDER BY provider_symbol ASC, candle_time_utc ASC
    """
    rows = _query(
        DB_PRICE,
        sql,
        (*params, bounded_rows),
        query_fn=query_fn,
    )
    return [dict(row) for row in rows]


def load_economic_cycle_market_series(
    *,
    series_ids: Sequence[str] = DEFAULT_PATHWAY_SERIES,
    start_date: object,
    end_date: object,
    macro_loader: Callable[..., object] = load_macro_series_observations,
) -> list[dict[str, object]]:
    """Return bounded stored market-pathway observations without provider access."""

    frame = macro_loader(
        series_ids=series_ids,
        start=str(start_date)[:10],
        end=str(end_date)[:10],
    )
    if hasattr(frame, "to_dict"):
        return list(frame.to_dict("records"))
    return [dict(row) for row in frame]
