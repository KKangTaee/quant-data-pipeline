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
    "pretax_income",
    "interest_expense",
    "net_income",
    "total_assets",
    "current_assets",
    "inventory",
    "total_liabilities",
    "current_liabilities",
    "short_term_debt",
    "long_term_debt",
    "total_debt",
    "shareholders_equity",
    "net_assets",
    "operating_cash_flow",
    "free_cash_flow",
    "capital_expenditure",
    "cash_and_equivalents",
    "dividends_paid",
    "shares_outstanding",
    "source_mode",
    "timing_basis",
    "gross_profit_source",
    "operating_income_source",
    "ebit_source",
    "free_cash_flow_source",
    "shares_outstanding_source",
    "total_debt_source",
    "shareholders_equity_source",
]

STATEMENT_FUNDAMENTAL_COLUMNS = FUNDAMENTAL_COLUMNS + [
    "latest_available_at",
    "latest_accession_no",
    "latest_form_type",
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


def load_statement_fundamentals_shadow(
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
        SELECT {", ".join(STATEMENT_FUNDAMENTAL_COLUMNS)}
        FROM nyse_fundamentals_statement
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
    if "latest_available_at" in df.columns:
        df["latest_available_at"] = pd.to_datetime(df["latest_available_at"])
    return df


def load_statement_shadow_coverage_summary(
    symbols: str | Iterable[str] | None = None,
    *,
    universe_source: str | None = None,
    freq: str = "annual",
) -> pd.DataFrame:
    resolved_symbols = resolve_loader_symbols(symbols=symbols, universe_source=universe_source)
    normalized_freq = normalize_loader_freq(freq)

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_fundamental")
        placeholders = ",".join(["%s"] * len(resolved_symbols))
        sql = f"""
        SELECT
          symbol,
          freq,
          COUNT(*) AS shadow_rows,
          MIN(period_end) AS min_period_end,
          MAX(period_end) AS max_period_end,
          MIN(latest_available_at) AS min_available_at,
          MAX(latest_available_at) AS max_available_at
        FROM nyse_fundamentals_statement
        WHERE symbol IN ({placeholders}) AND freq = %s
        GROUP BY symbol, freq
        ORDER BY symbol ASC
        """
        rows = db.query(sql, list(resolved_symbols) + [normalized_freq])
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return pd.DataFrame(
            columns=[
                "symbol",
                "freq",
                "shadow_rows",
                "min_period_end",
                "max_period_end",
                "min_available_at",
                "max_available_at",
            ]
        )

    df["min_period_end"] = pd.to_datetime(df["min_period_end"], errors="coerce")
    df["max_period_end"] = pd.to_datetime(df["max_period_end"], errors="coerce")
    df["min_available_at"] = pd.to_datetime(df["min_available_at"], errors="coerce")
    df["max_available_at"] = pd.to_datetime(df["max_available_at"], errors="coerce")
    return df
