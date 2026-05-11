from __future__ import annotations

from collections.abc import Iterable
from typing import Any

import pandas as pd

from finance.data.db.mysql import MySQLClient

from ._common import normalize_timestamp, parse_symbol_list


MACRO_COLUMNS = [
    "series_id",
    "observation_date",
    "source",
    "source_type",
    "source_mode",
    "source_ref",
    "series_name",
    "category",
    "frequency",
    "units",
    "value",
    "release_lag_days",
    "coverage_status",
    "missing_fields_json",
    "collected_at",
    "error_msg",
]
MACRO_SNAPSHOT_COLUMNS = MACRO_COLUMNS + ["staleness_days", "snapshot_status"]


def _empty_macro_frame(*, snapshot: bool = False) -> pd.DataFrame:
    return pd.DataFrame(columns=MACRO_SNAPSHOT_COLUMNS if snapshot else MACRO_COLUMNS)


def _is_missing_table_error(exc: Exception, table_name: str) -> bool:
    message = str(exc).lower()
    return table_name.lower() in message and ("doesn't exist" in message or "unknown table" in message)


def _normalize_macro_frame(rows: list[dict[str, Any]], *, snapshot: bool = False) -> pd.DataFrame:
    if not rows:
        return _empty_macro_frame(snapshot=snapshot)

    frame = pd.DataFrame(rows)
    for column in MACRO_SNAPSHOT_COLUMNS if snapshot else MACRO_COLUMNS:
        if column not in frame.columns:
            frame[column] = None

    for column in ["observation_date", "collected_at"]:
        frame[column] = pd.to_datetime(frame[column], errors="coerce")
    for column in ["value", "release_lag_days"]:
        frame[column] = pd.to_numeric(frame[column], errors="coerce")
    if snapshot:
        frame["staleness_days"] = pd.to_numeric(frame["staleness_days"], errors="coerce")
    frame["series_id"] = frame["series_id"].astype(str).str.upper()
    return frame[MACRO_SNAPSHOT_COLUMNS if snapshot else MACRO_COLUMNS]


def load_macro_series_observations(
    series_ids: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    source: str | None = None,
    category: str | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load stored market-context macro observations from finance_meta."""
    resolved_series = parse_symbol_list(series_ids)
    start_ts = normalize_timestamp(start, field_name="start") if start is not None else None
    end_ts = normalize_timestamp(end, field_name="end") if end is not None else None
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start must be earlier than or equal to end.")

    where: list[str] = []
    params: list[Any] = []
    if resolved_series:
        placeholders = ",".join(["%s"] * len(resolved_series))
        where.append(f"series_id IN ({placeholders})")
        params.extend(resolved_series)
    if source is not None:
        where.append("source = %s")
        params.append(str(source).strip())
    if category is not None:
        where.append("category = %s")
        params.append(str(category).strip())
    if start_ts is not None:
        where.append("observation_date >= %s")
        params.append(start_ts.strftime("%Y-%m-%d"))
    if end_ts is not None:
        where.append("observation_date <= %s")
        params.append(end_ts.strftime("%Y-%m-%d"))

    base_where = f"WHERE {' AND '.join(where)}" if where else ""
    sql = f"""
    SELECT *
    FROM macro_series_observation
    {base_where}
    ORDER BY series_id ASC, observation_date ASC, source ASC
    """

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db("finance_meta")
        try:
            rows = db.query(sql, params)
        except Exception as exc:
            if _is_missing_table_error(exc, "macro_series_observation"):
                return _empty_macro_frame()
            raise
    finally:
        db.close()

    return _normalize_macro_frame(rows)


def load_macro_snapshot(
    series_ids: str | Iterable[str] | None = None,
    *,
    as_of_date: str | None = None,
    source: str | None = None,
    category: str | None = None,
    max_staleness_days: int = 10,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> pd.DataFrame:
    """Load latest available macro observations on or before as_of_date with staleness status."""
    resolved_series = parse_symbol_list(series_ids)
    as_of_ts = normalize_timestamp(as_of_date, field_name="as_of_date") if as_of_date is not None else pd.Timestamp.utcnow()
    as_of = pd.Timestamp(as_of_ts)
    if as_of.tzinfo is not None:
        as_of = as_of.tz_convert(None)
    as_of = as_of.normalize()
    if int(max_staleness_days) < 0:
        raise ValueError("max_staleness_days must be non-negative.")

    where: list[str] = ["observation_date <= %s"]
    params: list[Any] = [as_of.strftime("%Y-%m-%d")]
    if resolved_series:
        placeholders = ",".join(["%s"] * len(resolved_series))
        where.append(f"series_id IN ({placeholders})")
        params.extend(resolved_series)
    if source is not None:
        where.append("source = %s")
        params.append(str(source).strip())
    if category is not None:
        where.append("category = %s")
        params.append(str(category).strip())

    latest_where = f"WHERE {' AND '.join(where)}"
    sql = f"""
    SELECT macro_rows.*
    FROM macro_series_observation macro_rows
    INNER JOIN (
        SELECT series_id, source, MAX(observation_date) AS latest_observation_date
        FROM macro_series_observation
        {latest_where}
        GROUP BY series_id, source
    ) latest_rows
        ON macro_rows.series_id = latest_rows.series_id
       AND macro_rows.source = latest_rows.source
       AND macro_rows.observation_date = latest_rows.latest_observation_date
    ORDER BY macro_rows.series_id ASC, macro_rows.source ASC
    """

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db("finance_meta")
        try:
            rows = db.query(sql, params)
        except Exception as exc:
            if _is_missing_table_error(exc, "macro_series_observation"):
                return _empty_macro_frame(snapshot=True)
            raise
    finally:
        db.close()

    frame = _normalize_macro_frame(rows)
    if frame.empty:
        return _empty_macro_frame(snapshot=True)

    frame["staleness_days"] = (as_of - frame["observation_date"]).dt.days
    frame["snapshot_status"] = frame.apply(
        lambda row: "actual"
        if row.get("coverage_status") == "actual" and row.get("staleness_days") <= int(max_staleness_days)
        else "stale",
        axis=1,
    )
    return frame[MACRO_SNAPSHOT_COLUMNS]
