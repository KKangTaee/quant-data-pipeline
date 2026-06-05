from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from .macro import load_macro_series_observations, load_macro_snapshot


CORE_SENTIMENT_SERIES = (
    "CNN_FEAR_GREED",
    "AAII_BULLISH",
    "AAII_NEUTRAL",
    "AAII_BEARISH",
    "AAII_BULL_BEAR_SPREAD",
)
CNN_COMPONENT_SERIES = (
    "CNN_FNG_MARKET_MOMENTUM_SP500",
    "CNN_FNG_STOCK_PRICE_STRENGTH",
    "CNN_FNG_STOCK_PRICE_BREADTH",
    "CNN_FNG_PUT_CALL_OPTIONS",
    "CNN_FNG_MARKET_VOLATILITY_VIX",
    "CNN_FNG_JUNK_BOND_DEMAND",
    "CNN_FNG_SAFE_HAVEN_DEMAND",
)
DEFAULT_SENTIMENT_SERIES = CORE_SENTIMENT_SERIES + CNN_COMPONENT_SERIES


def load_market_sentiment_snapshot(
    series_ids: str | Iterable[str] | None = None,
    *,
    as_of_date: str | None = None,
    max_staleness_days: int = 14,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load latest DB-backed CNN / AAII sentiment rows for Overview."""
    return load_macro_snapshot(
        series_ids=series_ids or DEFAULT_SENTIMENT_SERIES,
        as_of_date=as_of_date,
        max_staleness_days=max_staleness_days,
        host=host,
        user=user,
        password=password,
        port=port,
    )


def load_market_sentiment_history(
    series_ids: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load stored CNN / AAII sentiment history for charts and tables."""
    return load_macro_series_observations(
        series_ids=series_ids or DEFAULT_SENTIMENT_SERIES,
        start=start,
        end=end,
        host=host,
        user=user,
        password=password,
        port=port,
    )
