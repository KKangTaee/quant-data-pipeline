from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.db.mysql import MySQLClient

from ._common import (
    normalize_date_range,
    normalize_loader_freq,
    resolve_loader_symbols,
    validate_snapshot_inputs,
)


FUNDAMENTAL_COLUMNS = [
    "symbol",
    "freq",
    "period_end",
    "currency",
    "total_revenue",
    "gross_profit",
    "operating_income",
    "ebit",
    "net_income",
    "total_assets",
    "current_assets",
    "total_liabilities",
    "current_liabilities",
    "total_debt",
    "net_assets",
    "operating_cash_flow",
    "free_cash_flow",
    "capital_expenditure",
    "cash_and_equivalents",
    "dividends_paid",
    "shares_outstanding",
]


def load_fundamentals(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    freq: str = "annual",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    normalized_freq = normalize_loader_freq(freq)
    start_ts, end_ts = normalize_date_range(start=start, end=end)

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_fundamental")
        placeholders = ",".join(["%s"] * len(resolved_symbols))
        where = [f"symbol IN ({placeholders})", "freq = %s"]
        params: list[object] = list(resolved_symbols) + [normalized_freq]

        if start_ts is not None:
            where.append("period_end >= %s")
            params.append(start_ts.strftime("%Y-%m-%d"))
        if end_ts is not None:
            where.append("period_end <= %s")
            params.append(end_ts.strftime("%Y-%m-%d"))

        sql = f"""
        SELECT {", ".join(FUNDAMENTAL_COLUMNS)}
        FROM nyse_fundamentals
        WHERE {" AND ".join(where)}
        ORDER BY symbol ASC, period_end ASC
        """
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    df["period_end"] = pd.to_datetime(df["period_end"])
    return df


def load_fundamental_snapshot(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    as_of_date: str,
    freq: str = "annual",
) -> pd.DataFrame:
    as_of_ts = validate_snapshot_inputs(as_of_date=as_of_date)
    df = load_fundamentals(
        symbols=symbols,
        universe_source=universe_source,
        freq=freq,
        end=as_of_ts.strftime("%Y-%m-%d"),
    )
    if df.empty:
        return df

    ordered = df.sort_values(["symbol", "period_end"])
    snapshot = ordered.groupby("symbol", as_index=False).tail(1).reset_index(drop=True)
    snapshot["as_of_date"] = as_of_ts.normalize()
    return snapshot
