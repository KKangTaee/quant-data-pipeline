from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.data import load_ohlcv_many_mysql

from ._common import normalize_date_range, normalize_timeframe, resolve_loader_symbols


VALID_PRICE_FIELDS = {"open", "high", "low", "close", "adj_close", "volume", "dividends", "stock_splits"}


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
