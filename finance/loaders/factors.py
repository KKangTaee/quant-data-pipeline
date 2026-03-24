from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.factors import build_quality_factor_snapshot_from_statement_snapshot
from finance.data.db.mysql import MySQLClient

from ._common import (
    normalize_date_range,
    normalize_loader_freq,
    resolve_loader_symbols,
    validate_snapshot_inputs,
)
from .financial_statements import load_statement_snapshot_strict


FACTOR_COLUMNS = [
    "symbol",
    "freq",
    "period_end",
    "price",
    "price_date",
    "price_match_gap_days",
    "price_source",
    "price_timeframe",
    "timing_basis",
    "pit_mode",
    "market_cap",
    "enterprise_value",
    "psr",
    "sales_yield",
    "gpa",
    "por",
    "operating_income_yield",
    "ev_ebit",
    "per",
    "earnings_yield",
    "liquidation_value",
    "current_ratio",
    "cash_ratio",
    "pbr",
    "book_to_market",
    "debt_ratio",
    "debt_to_assets",
    "net_debt",
    "net_debt_to_equity",
    "pcr",
    "ocf_yield",
    "pfcr",
    "fcf_yield",
    "dividend_payout",
    "gross_margin",
    "operating_margin",
    "net_margin",
    "ocf_margin",
    "fcf_margin",
    "revenue_growth",
    "gross_profit_growth",
    "op_income_growth",
    "net_income_growth",
    "roe",
    "roa",
    "asset_turnover",
    "interest_coverage",
    "asset_growth",
    "debt_growth",
    "fcf_growth",
    "shares_growth",
]

STATEMENT_FACTOR_COLUMNS = [
    "symbol",
    "freq",
    "period_end",
    "fundamental_available_at",
    "fundamental_accession_no",
] + FACTOR_COLUMNS[3:]


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


def load_statement_quality_snapshot_strict(
    factor_names: list[str] | None = None,
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    as_of_date: str,
    freq: str = "annual",
) -> pd.DataFrame:
    as_of_ts = validate_snapshot_inputs(as_of_date=as_of_date)
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    normalized_freq = normalize_loader_freq(freq)

    statement_snapshot = load_statement_snapshot_strict(
        symbols=resolved_symbols,
        as_of_date=as_of_ts.strftime("%Y-%m-%d"),
        freq=normalized_freq,
    )
    quality_snapshot = build_quality_factor_snapshot_from_statement_snapshot(
        statement_snapshot,
        as_of_date=as_of_ts,
        freq=normalized_freq,
    )
    if quality_snapshot.empty:
        return quality_snapshot

    quality_snapshot["freq"] = normalized_freq
    quality_snapshot["as_of_date"] = as_of_ts.normalize()

    if factor_names:
        keep = ["symbol", "freq", "statement_period_end", "as_of_date"] + [
            name for name in factor_names if name in quality_snapshot.columns
        ]
        quality_snapshot = quality_snapshot[keep]
    return quality_snapshot


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


def load_statement_factors_shadow(
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
        SELECT {", ".join(STATEMENT_FACTOR_COLUMNS)}
        FROM nyse_factors_statement
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
    if "price_date" in df.columns:
        df["price_date"] = pd.to_datetime(df["price_date"])
    if "fundamental_available_at" in df.columns:
        df["fundamental_available_at"] = pd.to_datetime(df["fundamental_available_at"])
    return df
