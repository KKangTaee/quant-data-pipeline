from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient

from ._common import normalize_timestamp, parse_symbol_list


OPERABILITY_COLUMNS = [
    "symbol",
    "as_of_date",
    "source",
    "source_type",
    "source_ref",
    "fund_family",
    "category",
    "expense_ratio",
    "turnover_ratio",
    "total_assets",
    "net_assets",
    "nav",
    "market_price",
    "premium_discount_pct",
    "bid",
    "ask",
    "bid_ask_spread_pct",
    "median_bid_ask_spread_pct",
    "avg_daily_volume",
    "avg_daily_dollar_volume",
    "lookback_days",
    "inception_date",
    "leverage_factor",
    "is_inverse",
    "has_daily_objective",
    "coverage_status",
    "missing_fields_json",
    "collected_at",
    "error_msg",
]


def _empty_operability_frame() -> pd.DataFrame:
    return pd.DataFrame(columns=OPERABILITY_COLUMNS)


def _is_missing_table_error(exc: Exception, table_name: str) -> bool:
    message = str(exc).lower()
    return table_name.lower() in message and ("doesn't exist" in message or "unknown table" in message)


def _normalize_operability_frame(rows: list[dict[str, Any]]) -> pd.DataFrame:
    if not rows:
        return _empty_operability_frame()

    frame = pd.DataFrame(rows)
    for column in OPERABILITY_COLUMNS:
        if column not in frame.columns:
            frame[column] = None

    for column in ["as_of_date", "inception_date", "collected_at"]:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")

    numeric_columns = [
        "expense_ratio",
        "turnover_ratio",
        "total_assets",
        "net_assets",
        "nav",
        "market_price",
        "premium_discount_pct",
        "bid",
        "ask",
        "bid_ask_spread_pct",
        "median_bid_ask_spread_pct",
        "avg_daily_volume",
        "avg_daily_dollar_volume",
        "lookback_days",
        "leverage_factor",
        "is_inverse",
        "has_daily_objective",
    ]
    for column in numeric_columns:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")

    frame["symbol"] = frame["symbol"].astype(str).str.upper()
    return frame[OPERABILITY_COLUMNS]


def load_etf_operability_snapshot(
    symbols: str | Iterable[str] | None = None,
    *,
    as_of_date: str | None = None,
    latest: bool = True,
    source: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load ETF operability snapshots from finance_meta without remote provider calls."""
    resolved_symbols = parse_symbol_list(symbols)
    as_of_ts = normalize_timestamp(as_of_date, field_name="as_of_date") if as_of_date is not None else None

    where: list[str] = []
    params: list[Any] = []
    if resolved_symbols:
        placeholders = ",".join(["%s"] * len(resolved_symbols))
        where.append(f"symbol IN ({placeholders})")
        params.extend(resolved_symbols)
    if source is not None:
        where.append("source = %s")
        params.append(str(source).strip())

    if as_of_ts is not None:
        if latest:
            params_for_latest_date = params + [as_of_ts.strftime("%Y-%m-%d")]
        else:
            where.append("as_of_date = %s")
            params.append(as_of_ts.strftime("%Y-%m-%d"))
            params_for_latest_date = params
    else:
        params_for_latest_date = params

    base_where = f"WHERE {' AND '.join(where)}" if where else ""

    if latest:
        latest_where_parts = list(where)
        if as_of_ts is not None:
            latest_where_parts.append("as_of_date <= %s")
        latest_where = f"WHERE {' AND '.join(latest_where_parts)}" if latest_where_parts else ""
        sql = f"""
        SELECT eos.*
        FROM etf_operability_snapshot eos
        INNER JOIN (
            SELECT symbol, source, MAX(as_of_date) AS latest_as_of_date
            FROM etf_operability_snapshot
            {latest_where}
            GROUP BY symbol, source
        ) latest_rows
            ON eos.symbol = latest_rows.symbol
           AND eos.source = latest_rows.source
           AND eos.as_of_date = latest_rows.latest_as_of_date
        ORDER BY eos.symbol ASC, eos.source ASC
        """
        query_params = params_for_latest_date
    else:
        sql = f"""
        SELECT *
        FROM etf_operability_snapshot
        {base_where}
        ORDER BY symbol ASC, as_of_date DESC, source ASC
        """
        query_params = params

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db("finance_meta")
        try:
            rows = db.query(sql, query_params)
        except Exception as exc:
            if _is_missing_table_error(exc, "etf_operability_snapshot"):
                return _empty_operability_frame()
            raise
    finally:
        db.close()

    return _normalize_operability_frame(rows)
