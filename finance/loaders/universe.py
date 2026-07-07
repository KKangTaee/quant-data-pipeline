from __future__ import annotations

from collections.abc import Iterable

import pandas as pd

from finance.data.pit_universe import PIT_UNIVERSE_METHOD_VERSION
from finance.data.db.mysql import MySQLClient

from ._common import normalize_date_range, parse_symbol_list, resolve_loader_symbols


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


def load_symbol_lifecycle_coverage_summary(
    symbols: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
) -> pd.DataFrame:
    """
    Load compact symbol lifecycle evidence for survivorship diagnostics.

    The loader reads lifecycle metadata only. It does not load listing history
    snapshots in full and does not mutate DB state.
    """
    resolved_symbols = parse_symbol_list(symbols)
    if not resolved_symbols:
        return pd.DataFrame(
            columns=[
                "symbol",
                "kind",
                "listing_status",
                "source",
                "source_type",
                "coverage_status",
                "first_seen_date",
                "last_seen_date",
                "inactive_detected_at",
                "event_type",
                "event_date",
                "related_symbol",
                "related_cik",
                "collected_at",
                "source_ref",
                "name",
                "error_msg",
                "requested_start",
                "requested_end",
            ]
        )

    start_ts, end_ts = normalize_date_range(start=start, end=end)
    placeholders = ",".join(["%s"] * len(resolved_symbols))
    sql = f"""
        SELECT
            symbol,
            kind,
            listing_status,
            source,
            source_type,
            coverage_status,
            first_seen_date,
            last_seen_date,
            inactive_detected_at,
            event_type,
            event_date,
            related_symbol,
            related_cik,
            collected_at,
            source_ref,
            name,
            error_msg
        FROM nyse_symbol_lifecycle
        WHERE symbol IN ({placeholders})
        ORDER BY
            symbol ASC,
            CASE source_type
                WHEN 'historical_listing' THEN 0
                WHEN 'delisting_feed' THEN 1
                WHEN 'computed_from_snapshots' THEN 2
                WHEN 'asset_profile_bridge' THEN 3
                ELSE 4
            END ASC,
            CASE coverage_status
                WHEN 'actual' THEN 0
                WHEN 'partial' THEN 1
                WHEN 'bridge' THEN 2
                WHEN 'proxy' THEN 3
                ELSE 4
            END ASC,
            last_seen_date DESC
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

    for column in ["first_seen_date", "last_seen_date", "inactive_detected_at", "event_date", "collected_at"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    if "symbol" in df.columns:
        df["symbol"] = df["symbol"].astype(str).str.upper()

    df["requested_start"] = start_ts.strftime("%Y-%m-%d") if start_ts is not None else None
    df["requested_end"] = end_ts.strftime("%Y-%m-%d") if end_ts is not None else None
    return df


def load_pit_universe_members(
    universe_code: str,
    *,
    start: str | None = None,
    end: str | None = None,
    method_version: str = PIT_UNIVERSE_METHOD_VERSION,
    target_size: int | None = None,
    included_only: bool = True,
) -> pd.DataFrame:
    """
    Load prebuilt point-in-time universe member rows from finance_meta.

    The loader is read-only. It expects ingestion/build jobs to create
    `equity_universe_member` rows ahead of backtest execution.
    """
    normalized_code = str(universe_code or "").strip().upper()
    if not normalized_code:
        raise ValueError("universe_code is required.")

    start_ts, end_ts = normalize_date_range(start=start, end=end)
    where = ["universe_code = %s", "method_version = %s"]
    params: list[object] = [normalized_code, method_version]
    if included_only:
        where.append("included = 1")
    if start_ts is not None:
        where.append("as_of_date >= %s")
        params.append(start_ts.strftime("%Y-%m-%d"))
    if end_ts is not None:
        where.append("as_of_date <= %s")
        params.append(end_ts.strftime("%Y-%m-%d"))
    if target_size is not None:
        where.append("(rank_no IS NULL OR rank_no <= %s)")
        params.append(int(target_size))

    sql = f"""
        SELECT
            universe_code,
            as_of_date,
            symbol,
            rank_no,
            eligible,
            included,
            excluded_reason,
            price_date,
            close,
            shares_outstanding,
            shares_source,
            approx_market_cap,
            avg_dollar_volume_20d,
            listing_status,
            lifecycle_source,
            method_version,
            evidence_json
        FROM equity_universe_member
        WHERE {" AND ".join(where)}
        ORDER BY as_of_date ASC, rank_no ASC, symbol ASC
    """

    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_meta")
        rows = db.query(sql, params)
    finally:
        db.close()

    df = pd.DataFrame(rows)
    if df.empty:
        return df
    for column in ["as_of_date", "price_date"]:
        if column in df.columns:
            df[column] = pd.to_datetime(df[column], errors="coerce")
    if "symbol" in df.columns:
        df["symbol"] = df["symbol"].astype(str).str.upper()
    return df


def load_pit_universe_membership_snapshots(
    universe_code: str,
    *,
    start: str | None = None,
    end: str | None = None,
    method_version: str = PIT_UNIVERSE_METHOD_VERSION,
    target_size: int | None = None,
) -> dict[str, list[str]]:
    """Return included PIT members grouped by snapshot date in rank order."""
    members = load_pit_universe_members(
        universe_code,
        start=start,
        end=end,
        method_version=method_version,
        target_size=target_size,
        included_only=True,
    )
    if members.empty:
        return {}

    grouped: dict[str, list[str]] = {}
    working = members.sort_values(["as_of_date", "rank_no", "symbol"]).copy()
    for as_of_date, group in working.groupby("as_of_date", sort=True):
        key = pd.Timestamp(as_of_date).strftime("%Y-%m-%d")
        grouped[key] = [str(symbol).upper() for symbol in group["symbol"].tolist()]
    return grouped
