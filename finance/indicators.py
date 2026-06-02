from __future__ import annotations

import pandas as pd


def add_atr(
    price_history: pd.DataFrame,
    *,
    period: int = 14,
    method: str = "simple",
    symbol_col: str = "symbol",
    date_col: str = "date",
    high_col: str = "high",
    low_col: str = "low",
    close_col: str = "close",
    true_range_col: str = "true_range",
    output_col: str | None = None,
) -> pd.DataFrame:
    """Add True Range and simple rolling ATR columns to long-form OHLC rows."""
    if price_history is None or price_history.empty:
        return pd.DataFrame()
    if method != "simple":
        raise ValueError("Only method='simple' ATR is supported.")
    period = int(period)
    if period <= 0:
        raise ValueError("ATR period must be positive.")

    required = {symbol_col, date_col, high_col, low_col, close_col}
    missing = required.difference(price_history.columns)
    if missing:
        raise KeyError(f"price_history is missing required columns for ATR: {sorted(missing)}")

    d = price_history.copy()
    d[symbol_col] = d[symbol_col].astype(str).str.upper()
    d[date_col] = pd.to_datetime(d[date_col], errors="coerce")
    d = d.dropna(subset=[symbol_col, date_col]).sort_values([symbol_col, date_col]).reset_index(drop=True)

    for column in [high_col, low_col, close_col]:
        d[column] = pd.to_numeric(d[column], errors="coerce")

    grouped = d.groupby(symbol_col, sort=False)
    high = d[high_col].astype(float)
    low = d[low_col].astype(float)
    prev_close = grouped[close_col].shift(1)
    true_range = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)

    atr_col = output_col or f"atr{period}"
    d[true_range_col] = true_range
    d[atr_col] = d.groupby(symbol_col, sort=False)[true_range_col].transform(
        lambda s: s.rolling(period, min_periods=period).mean()
    )
    return d
