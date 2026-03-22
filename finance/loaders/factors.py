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


FACTOR_COLUMNS = [
    "symbol",
    "freq",
    "period_end",
    "price",
    "market_cap",
    "enterprise_value",
    "psr",
    "gpa",
    "por",
    "ev_ebit",
    "per",
    "liquidation_value",
    "current_ratio",
    "pbr",
    "debt_ratio",
    "pcr",
    "pfcr",
    "dividend_payout",
    "op_income_growth",
    "roe",
    "roa",
    "asset_turnover",
    "interest_coverage",
    "asset_growth",
    "debt_growth",
    "shares_growth",
]


def load_factors(
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
        SELECT {", ".join(FACTOR_COLUMNS)}
        FROM nyse_factors
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


def load_factor_snapshot(
    factor_names: list[str] | None,
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    as_of_date: str,
    freq: str = "annual",
) -> pd.DataFrame:
    as_of_ts = validate_snapshot_inputs(as_of_date=as_of_date)
    df = load_factors(
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

    if factor_names:
        keep = ["symbol", "freq", "period_end", "as_of_date"] + [name for name in factor_names if name in snapshot.columns]
        snapshot = snapshot[keep]
    return snapshot


def load_factor_matrix(
    factor_name: str,
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    freq: str = "annual",
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    df = load_factors(
        symbols=symbols,
        universe_source=universe_source,
        freq=freq,
        start=start,
        end=end,
    )
    if df.empty:
        return df
    if factor_name not in df.columns:
        raise ValueError(f"Unsupported factor column: {factor_name!r}")

    matrix = df.pivot(index="period_end", columns="symbol", values=factor_name).sort_index()
    matrix.columns.name = None
    return matrix
