from __future__ import annotations

from collections.abc import Iterable
from datetime import datetime

import pandas as pd

from finance.data.asset_profile import load_symbols_from_asset_profile
from finance.data.db.mysql import MySQLClient


VALID_FREQS = {"annual", "quarterly"}
VALID_TIMEFRAMES = {"1d", "1wk", "1mo"}
VALID_UNIVERSE_SOURCES = {
    "nyse_stocks",
    "nyse_etfs",
    "nyse_stocks_etfs",
    "profile_filtered_stocks",
    "profile_filtered_etfs",
    "profile_filtered_stocks_etfs",
}


def parse_symbol_list(symbols: str | Iterable[str] | None) -> list[str]:
    if symbols is None:
        return []

    if isinstance(symbols, str):
        raw = symbols.replace("\n", ",").split(",")
    else:
        raw = list(symbols)

    out: list[str] = []
    seen: set[str] = set()

    for item in raw:
        sym = str(item).strip().upper()
        if not sym or sym in seen:
            continue
        seen.add(sym)
        out.append(sym)

    return out


def normalize_timestamp(value: str | datetime | pd.Timestamp | None, *, field_name: str) -> pd.Timestamp | None:
    if value is None:
        return None

    ts = pd.Timestamp(value)
    if pd.isna(ts):
        raise ValueError(f"Invalid {field_name}: {value!r}")
    return ts


def normalize_date_range(
    *,
    start: str | datetime | pd.Timestamp | None = None,
    end: str | datetime | pd.Timestamp | None = None,
) -> tuple[pd.Timestamp | None, pd.Timestamp | None]:
    start_ts = normalize_timestamp(start, field_name="start")
    end_ts = normalize_timestamp(end, field_name="end")

    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start must be earlier than or equal to end.")

    return start_ts, end_ts


def validate_snapshot_inputs(
    *,
    as_of_date: str | datetime | pd.Timestamp | None,
    start: str | datetime | pd.Timestamp | None = None,
    end: str | datetime | pd.Timestamp | None = None,
) -> pd.Timestamp | None:
    if as_of_date is None:
        return None
    if start is not None or end is not None:
        raise ValueError("Snapshot loaders do not allow start/end together with as_of_date.")
    return normalize_timestamp(as_of_date, field_name="as_of_date")


def normalize_loader_freq(freq: str | None) -> str | None:
    if freq is None:
        return None
    normalized = str(freq).strip().lower()
    if normalized not in VALID_FREQS:
        raise ValueError(f"Unsupported freq: {freq!r}")
    return normalized


def normalize_timeframe(timeframe: str | None) -> str:
    normalized = "1d" if timeframe is None else str(timeframe).strip().lower()
    if normalized not in VALID_TIMEFRAMES:
        raise ValueError(f"Unsupported timeframe: {timeframe!r}")
    return normalized


def _query_symbols(table: str) -> list[str]:
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db("finance_meta")
        rows = db.query(f"SELECT symbol FROM {table} ORDER BY symbol")
        return [row["symbol"] for row in rows if row.get("symbol")]
    finally:
        db.close()


def _merge_unique(*groups: list[str]) -> list[str]:
    out: list[str] = []
    seen: set[str] = set()
    for group in groups:
        for symbol in group:
            if symbol in seen:
                continue
            seen.add(symbol)
            out.append(symbol)
    return out


def resolve_loader_symbols(
    *,
    symbols: str | Iterable[str] | None = None,
    universe_source: str | None = None,
) -> list[str]:
    parsed = parse_symbol_list(symbols)
    if parsed:
        return parsed

    if universe_source is None:
        raise ValueError("Either symbols or universe_source must be provided.")

    source = str(universe_source).strip().lower()
    if source not in VALID_UNIVERSE_SOURCES:
        raise ValueError(f"Unsupported universe_source: {universe_source!r}")

    if source == "nyse_stocks":
        return _query_symbols("nyse_stock")
    if source == "nyse_etfs":
        return _query_symbols("nyse_etf")
    if source == "nyse_stocks_etfs":
        return _merge_unique(_query_symbols("nyse_stock"), _query_symbols("nyse_etf"))
    if source == "profile_filtered_stocks":
        return load_symbols_from_asset_profile("stock", on_filter=True)
    if source == "profile_filtered_etfs":
        return load_symbols_from_asset_profile("etf", on_filter=True)
    if source == "profile_filtered_stocks_etfs":
        return _merge_unique(
            load_symbols_from_asset_profile("stock", on_filter=True),
            load_symbols_from_asset_profile("etf", on_filter=True),
        )

    raise ValueError(f"Unsupported universe_source: {universe_source!r}")
