from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from .price import load_price_history


PRICE_COLUMN_MAP = {
    "date": "Date",
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "adj_close": "Adj Close",
    "volume": "Volume",
    "dividends": "Dividends",
    "stock_splits": "Stock Splits",
}


def adapt_price_history_to_strategy_dfs(history: pd.DataFrame) -> dict[str, pd.DataFrame]:
    """
    Convert loader long-form price history into the ticker-keyed OHLCV dict
    expected by the existing strategy/transform layer.
    """
    if history is None or history.empty:
        return {}

    required = {"symbol", "date", "open", "high", "low", "close", "adj_close", "volume", "dividends", "stock_splits"}
    missing = required.difference(history.columns)
    if missing:
        raise ValueError(f"Price history is missing required columns: {sorted(missing)}")

    dfs: dict[str, pd.DataFrame] = {}

    for symbol, group in history.groupby("symbol", sort=True):
        d = group.copy().sort_values("date").reset_index(drop=True)
        d["date"] = pd.to_datetime(d["date"])
        d = d.rename(columns=PRICE_COLUMN_MAP)
        d["Ticker"] = symbol

        ordered_columns = [
            "Date",
            "Ticker",
            "Open",
            "High",
            "Low",
            "Close",
            "Adj Close",
            "Volume",
            "Dividends",
            "Stock Splits",
        ]
        dfs[symbol] = d[ordered_columns]

    return dfs


def load_price_strategy_dfs(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    start: str | None = None,
    end: str | None = None,
    timeframe: str = "1d",
) -> dict[str, pd.DataFrame]:
    """
    Convenience helper for the first DB-backed strategy runtime path.
    """
    history = load_price_history(
        symbols=symbols,
        universe_source=universe_source,
        start=start,
        end=end,
        timeframe=timeframe,
    )
    return adapt_price_history_to_strategy_dfs(history)
