"""DB-only readers for Philadelphia Fed RTDSM signal history."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from typing import Any

from finance.data.db.mysql import MySQLClient
from finance.data.philadelphia_rtdsm import RTDSM_SOURCE


DB_META = "finance_meta"
QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]


def _date_value(value: object, *, field: str) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value).strip()[:10])
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc


def _query(
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(DB_META, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(DB_META)
        return db.query(sql, params)
    finally:
        db.close()


def load_rtdsm_signal_history(
    series_ids: Iterable[str],
    *,
    start_date: str | date,
    end_date: str | date,
    as_of_date: str | date,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Load RTDSM vintages and only the raw months required by transforms."""

    requested = tuple(
        dict.fromkeys(str(item or "").strip().upper() for item in series_ids)
    )
    if not requested or any(not item for item in requested):
        raise ValueError("At least one RTDSM series_id is required")
    start = _date_value(start_date, field="start_date")
    end = _date_value(end_date, field="end_date")
    as_of = _date_value(as_of_date, field="as_of_date")
    if start > end:
        raise ValueError("start_date must be earlier than or equal to end_date")
    end = min(end, as_of)
    placeholders = ",".join(["%s"] * len(requested))
    sql = f"""
    SELECT
      series_id, observation_date, realtime_start, realtime_end,
      source, source_mode, value, coverage_status, collected_at, updated_at
    FROM macro_series_vintage_observation
    WHERE source = %s
      AND series_id IN ({placeholders})
      AND realtime_start <= %s
      AND realtime_end >= %s
      AND observation_date >= DATE_SUB(realtime_start, INTERVAL 12 MONTH)
      AND observation_date <= realtime_start
    ORDER BY series_id ASC, realtime_start ASC, observation_date ASC
    """
    params: tuple[Any, ...] = (
        RTDSM_SOURCE,
        *requested,
        end.isoformat(),
        start.isoformat(),
    )
    raw_rows = _query(sql, params, query_fn=query_fn)

    selected: dict[tuple[str, date, date], dict[str, object]] = {}
    for raw in raw_rows:
        row = dict(raw)
        series_id = str(row.get("series_id") or "").strip().upper()
        source = str(row.get("source") or "")
        if series_id not in requested or source != RTDSM_SOURCE:
            continue
        observation = _date_value(
            row.get("observation_date"), field="observation_date"
        )
        realtime_start = _date_value(
            row.get("realtime_start"), field="realtime_start"
        )
        realtime_end = _date_value(row.get("realtime_end"), field="realtime_end")
        if realtime_start > end or realtime_end < start:
            continue
        if observation > realtime_start:
            continue
        if (realtime_start - observation).days > 370:
            continue
        key = (series_id, observation, realtime_start)
        current = selected.get(key)
        if current is not None and str(row.get("updated_at") or "") <= str(
            current.get("updated_at") or ""
        ):
            continue
        row["series_id"] = series_id
        row["observation_date"] = observation.isoformat()
        row["realtime_start"] = realtime_start.isoformat()
        row["realtime_end"] = realtime_end.isoformat()
        selected[key] = row
    return [
        selected[key]
        for key in sorted(
            selected,
            key=lambda item: (item[0], item[2], item[1]),
        )
    ]
