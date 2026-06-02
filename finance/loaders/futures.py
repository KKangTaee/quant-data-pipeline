from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.db.mysql import MySQLClient

from ._common import normalize_date_range, parse_symbol_list


def load_futures_ohlcv(
    symbols: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    interval_code: str = "1d",
) -> pd.DataFrame:
    """Load stored futures OHLCV rows from `finance_price.futures_ohlcv`."""

    resolved_symbols = parse_symbol_list(symbols)
    start_ts, end_ts = normalize_date_range(start=start, end=end)
    normalized_interval = str(interval_code or "1d").strip()

    where = ["interval_code = %s"]
    params: list[object] = [normalized_interval]
    if resolved_symbols:
        placeholders = ",".join(["%s"] * len(resolved_symbols))
        where.append(f"provider_symbol IN ({placeholders})")
        params.extend(resolved_symbols)
    if start_ts is not None:
        where.append("candle_time_utc >= %s")
        params.append(start_ts.strftime("%Y-%m-%d"))
    if end_ts is not None:
        where.append("candle_time_utc <= %s")
        params.append(end_ts.strftime("%Y-%m-%d 23:59:59"))

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_price")
        rows = db.query(
            f"""
            SELECT
                provider_symbol,
                interval_code,
                candle_time_utc,
                open,
                high,
                low,
                close,
                volume,
                source,
                provider_status
            FROM futures_ohlcv
            WHERE {" AND ".join(where)}
            ORDER BY provider_symbol ASC, candle_time_utc ASC
            """,
            params,
        )
    finally:
        db.close()

    frame = pd.DataFrame(rows)
    if frame.empty:
        return frame
    frame["provider_symbol"] = frame["provider_symbol"].astype(str).str.upper()
    frame["candle_time_utc"] = pd.to_datetime(frame["candle_time_utc"], errors="coerce")
    for column in ["open", "high", "low", "close", "volume"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    return frame
