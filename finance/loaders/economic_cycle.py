"""DB-only point-in-time readers for economic-cycle source and result data."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from typing import Any

from finance.data.db.mysql import MySQLClient
from finance.economic_cycle_catalog import get_economic_cycle_catalog


QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
DB_META = "finance_meta"


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
    database: str,
    sql: str,
    params: tuple[Any, ...],
    *,
    query_fn: QueryFn | None,
) -> list[dict[str, Any]]:
    if query_fn is not None:
        return list(query_fn(database, sql, params))
    db = MySQLClient("localhost", "root", "1234", 3306)
    try:
        db.use_db(database)
        return db.query(sql, params)
    except Exception as exc:
        message = str(exc).lower()
        if "macro_series_vintage_observation" in message and (
            "doesn't exist" in message or "unknown table" in message
        ):
            return []
        raise
    finally:
        db.close()


def _normalized_series_ids(series_ids: Iterable[str]) -> tuple[str, ...]:
    normalized = tuple(
        dict.fromkeys(str(item or "").strip().upper() for item in series_ids)
    )
    if not normalized or any(not item for item in normalized):
        raise ValueError("At least one non-empty series_id is required")
    return normalized


def _updated_sort_value(value: object) -> str:
    if isinstance(value, datetime):
        return value.isoformat(sep=" ")
    return str(value or "")


def load_economic_cycle_vintages(
    series_ids: Iterable[str],
    *,
    start_date: str | date,
    end_date: str | date,
    as_of_date: str | date,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Return only the source versions that were eligible at one forecast origin."""

    resolved_series = _normalized_series_ids(series_ids)
    start = _date_value(start_date, field="start_date")
    end = _date_value(end_date, field="end_date")
    as_of = _date_value(as_of_date, field="as_of_date")
    if start > end:
        raise ValueError("start_date must be earlier than or equal to end_date")
    if end > as_of:
        end = as_of

    placeholders = ",".join(["%s"] * len(resolved_series))
    sql = f"""
    WITH eligible_versions AS (
      SELECT vintage_rows.*,
             ROW_NUMBER() OVER (
               PARTITION BY series_id, observation_date
               ORDER BY realtime_start DESC, updated_at DESC
             ) AS version_rank
      FROM macro_series_vintage_observation vintage_rows
      WHERE series_id IN ({placeholders})
        AND observation_date >= %s
        AND observation_date <= %s
        AND realtime_start <= %s
        AND realtime_end >= %s
    )
    SELECT *
    FROM eligible_versions
    WHERE version_rank = 1
    ORDER BY series_id ASC, observation_date ASC
    """
    params: tuple[Any, ...] = (
        *resolved_series,
        start.isoformat(),
        end.isoformat(),
        as_of.isoformat(),
        as_of.isoformat(),
    )
    raw_rows = _query(DB_META, sql, params, query_fn=query_fn)

    # The SQL owns the primary filter; this defensive pass keeps injected/test
    # readers and legacy duplicate rows from bypassing the PIT contract.
    eligible: dict[tuple[str, date], dict[str, object]] = {}
    for raw in raw_rows:
        row = dict(raw)
        series_id = str(row.get("series_id") or "").strip().upper()
        if series_id not in resolved_series:
            continue
        observation = _date_value(row.get("observation_date"), field="observation_date")
        realtime_start = _date_value(row.get("realtime_start"), field="realtime_start")
        realtime_end = _date_value(row.get("realtime_end"), field="realtime_end")
        if not (start <= observation <= end):
            continue
        if not (realtime_start <= as_of <= realtime_end):
            continue
        key = (series_id, observation)
        candidate_sort = (realtime_start, _updated_sort_value(row.get("updated_at")))
        current = eligible.get(key)
        if current is not None:
            current_sort = (
                _date_value(current.get("realtime_start"), field="realtime_start"),
                _updated_sort_value(current.get("updated_at")),
            )
            if candidate_sort <= current_sort:
                continue
        row["series_id"] = series_id
        row["observation_date"] = observation.isoformat()
        row["realtime_start"] = realtime_start.isoformat()
        row["realtime_end"] = realtime_end.isoformat()
        row.pop("version_rank", None)
        eligible[key] = row

    return [
        eligible[key]
        for key in sorted(eligible, key=lambda item: (item[0], item[1]))
    ]


def load_economic_cycle_series_coverage(
    *,
    as_of_date: str | date,
    query_fn: QueryFn | None = None,
) -> dict[str, object]:
    """Summarize per-series freshness without exposing raw rows to the UI."""

    as_of = _date_value(as_of_date, field="as_of_date")
    series_ids = [item.series_id for item in get_economic_cycle_catalog()]
    rows = load_economic_cycle_vintages(
        series_ids,
        start_date=date(1900, 1, 1),
        end_date=as_of,
        as_of_date=as_of,
        query_fn=query_fn,
    )
    latest: dict[str, dict[str, object]] = {}
    for row in rows:
        series_id = str(row["series_id"])
        observation = _date_value(row["observation_date"], field="observation_date")
        current = latest.get(series_id)
        if current is None or observation > _date_value(
            current["observation_date"], field="observation_date"
        ):
            latest[series_id] = row

    items = []
    for series_id in series_ids:
        row = latest.get(series_id)
        if row is None:
            items.append(
                {
                    "series_id": series_id,
                    "status": "NOT_COLLECTED",
                    "latest_observation_date": None,
                    "staleness_days": None,
                }
            )
            continue
        observation = _date_value(row["observation_date"], field="observation_date")
        items.append(
            {
                "series_id": series_id,
                "status": str(row.get("coverage_status") or "missing").upper(),
                "latest_observation_date": observation.isoformat(),
                "staleness_days": (as_of - observation).days,
            }
        )
    return {
        "as_of_date": as_of.isoformat(),
        "requested_series": len(series_ids),
        "available_series": len(latest),
        "series": items,
    }
