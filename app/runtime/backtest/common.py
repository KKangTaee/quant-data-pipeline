from __future__ import annotations

import pandas as pd


class BacktestInputError(ValueError):
    """Raised when user-facing backtest input is structurally invalid."""


class BacktestDataError(ValueError):
    """Raised when the requested DB-backed backtest cannot find required market data."""


def validate_backtest_date_range(start: str | None, end: str | None) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    start_ts = pd.to_datetime(start) if start is not None else None
    end_ts = pd.to_datetime(end) if end is not None else None

    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise BacktestInputError("Start date must be earlier than or equal to end date.")

    return start_ts, end_ts


__all__ = [
    "BacktestDataError",
    "BacktestInputError",
    "validate_backtest_date_range",
]
