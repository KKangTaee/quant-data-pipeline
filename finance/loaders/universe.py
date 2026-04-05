from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.db.mysql import MySQLClient

from ._common import parse_symbol_list, resolve_loader_symbols


def load_universe(
    source: str | None = None,
    *,
    symbols: str | Iterable[str] | None = None,
) -> list[str]:
    """
    Resolve a normalized symbol universe for loader/runtime use.

    Parameters
    ----------
    source:
        Named universe source such as ``nyse_stocks`` or
        ``profile_filtered_stocks``.
    symbols:
        Explicit symbol override. If provided, this takes precedence.
    """
    return resolve_loader_symbols(symbols=symbols, universe_source=source)


def load_asset_profile_status_summary(
    symbols: str | Iterable[str] | None = None,
) -> pd.DataFrame:
    """
    Load a minimal asset-profile summary for the requested symbols.

    This is intended for lightweight runtime diagnostics such as
    stale-symbol classification in strict backtest preflight checks.
    """
    resolved_symbols = parse_symbol_list(symbols)
    if not resolved_symbols:
        return pd.DataFrame(
            columns=[
                "symbol",
                "kind",
                "quote_type",
                "status",
                "error_msg",
                "last_collected_at",
                "delisted_at",
                "exchange",
                "country",
                "long_name",
                "market_cap",
                "total_assets",
                "fund_family",
                "bid",
                "ask",
                "bid_size",
                "ask_size",
            ]
        )

    placeholders = ",".join(["%s"] * len(resolved_symbols))
    sql = f"""
        SELECT
            symbol,
            kind,
            quote_type,
            status,
            error_msg,
            last_collected_at,
            delisted_at,
            exchange,
            country,
            long_name,
            market_cap,
            total_assets,
            fund_family,
            bid,
            ask,
            bid_size,
            ask_size
        FROM nyse_asset_profile
        WHERE symbol IN ({placeholders})
        ORDER BY symbol ASC
    """

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_meta")
        rows = db.query(sql, resolved_symbols)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df

    for column in ["last_collected_at", "delisted_at"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")

    if "symbol" in df.columns:
        df["symbol"] = df["symbol"].astype(str).str.upper()

    return df
