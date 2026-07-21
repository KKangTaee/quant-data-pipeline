"""DB-only point-in-time readers for economic-cycle source and result data."""

from __future__ import annotations

from collections.abc import Callable, Iterable
from datetime import date, datetime
from typing import Any

from finance.data.db.mysql import MySQLClient
from finance.economic_cycle_catalog import get_economic_cycle_catalog


QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]
DB_META = "finance_meta"
SNAPSHOT_RUN_KINDS = {"current", "historical_replay", "intramonth_nowcast"}


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


def load_economic_cycle_vintage_history(
    series_ids: Iterable[str],
    *,
    start_date: str | date,
    end_date: str | date,
    as_of_date: str | date,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Load all raw intervals that can affect any origin in a bounded PIT panel."""

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
    SELECT
      series_id, observation_date, realtime_start, realtime_end,
      source, value, coverage_status, collected_at, updated_at
    FROM macro_series_vintage_observation
    WHERE series_id IN ({placeholders})
      AND observation_date >= %s
      AND observation_date <= %s
      AND realtime_start <= %s
      AND realtime_end >= %s
    ORDER BY series_id ASC, observation_date ASC, realtime_start ASC
    """
    params: tuple[Any, ...] = (
        *resolved_series,
        start.isoformat(),
        end.isoformat(),
        as_of.isoformat(),
        start.isoformat(),
    )
    raw_rows = _query(DB_META, sql, params, query_fn=query_fn)

    eligible: dict[tuple[str, date, date, str], dict[str, object]] = {}
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
        if realtime_start > as_of or realtime_end < start:
            continue
        source = str(row.get("source") or "")
        key = (series_id, observation, realtime_start, source)
        current = eligible.get(key)
        if current is not None and _updated_sort_value(
            row.get("updated_at")
        ) <= _updated_sort_value(current.get("updated_at")):
            continue
        row["series_id"] = series_id
        row["observation_date"] = observation.isoformat()
        row["realtime_start"] = realtime_start.isoformat()
        row["realtime_end"] = realtime_end.isoformat()
        eligible[key] = row

    return [
        eligible[key]
        for key in sorted(
            eligible,
            key=lambda item: (item[0], item[1], item[2], item[3]),
        )
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
    collected_values = [
        _updated_sort_value(row.get("collected_at"))
        for row in rows
        if row.get("collected_at") not in (None, "")
    ]
    return {
        "as_of_date": as_of.isoformat(),
        "requested_series": len(series_ids),
        "available_series": len(latest),
        "source_collected_at": max(collected_values) if collected_values else None,
        "series": items,
    }


def load_latest_approved_cycle_artifact(
    *,
    as_of_date: str | date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, object] | None:
    """Load the latest READY artifact trained no later than the requested date."""

    as_of = _date_value(as_of_date or date.today(), field="as_of_date")
    sql = """
    SELECT *
    FROM economic_cycle_model_artifact
    WHERE publication_status = 'READY'
      AND trained_through <= %s
    ORDER BY trained_through DESC, updated_at DESC
    """
    rows = _query(DB_META, sql, (as_of.isoformat(),), query_fn=query_fn)
    eligible = [
        dict(row)
        for row in rows
        if str(row.get("publication_status")) == "READY"
        and _date_value(row.get("trained_through"), field="trained_through") <= as_of
    ]
    if not eligible:
        return None
    selected = max(
        eligible,
        key=lambda row: (
            _date_value(row["trained_through"], field="trained_through"),
            _updated_sort_value(row.get("updated_at")),
        ),
    )
    selected["trained_through"] = _date_value(
        selected["trained_through"], field="trained_through"
    ).isoformat()
    return selected


def load_cycle_model_artifact(
    model_version: str,
    *,
    trained_through: str | date | None = None,
    query_fn: QueryFn | None = None,
) -> dict[str, object] | None:
    """Load one exact persisted artifact without changing its publication state."""

    resolved_version = str(model_version or "").strip()
    if not resolved_version:
        raise ValueError("model_version is required")
    where = ["model_version = %s"]
    params: list[object] = [resolved_version]
    resolved_training = None
    if trained_through is not None:
        resolved_training = _date_value(trained_through, field="trained_through")
        where.append("trained_through = %s")
        params.append(resolved_training.isoformat())
    sql = f"""
    SELECT *
    FROM economic_cycle_model_artifact
    WHERE {' AND '.join(where)}
    ORDER BY trained_through DESC, updated_at DESC
    LIMIT 1
    """
    rows = _query(DB_META, sql, tuple(params), query_fn=query_fn)
    eligible: list[dict[str, object]] = []
    for raw in rows:
        row = dict(raw)
        if str(row.get("model_version")) != resolved_version:
            continue
        row_training = _date_value(row.get("trained_through"), field="trained_through")
        if resolved_training is not None and row_training != resolved_training:
            continue
        row["trained_through"] = row_training.isoformat()
        eligible.append(row)
    if not eligible:
        return None
    return max(
        eligible,
        key=lambda row: (
            str(row["trained_through"]),
            _updated_sort_value(row.get("updated_at")),
        ),
    )


def load_cycle_snapshot(
    *,
    as_of_date: str | date | None = None,
    model_version: str | None = None,
    run_kind: str = "current",
    query_fn: QueryFn | None = None,
) -> dict[str, object] | None:
    """Load one compact persisted snapshot without calculating or fetching."""

    resolved_kind = str(run_kind)
    if resolved_kind not in SNAPSHOT_RUN_KINDS:
        raise ValueError(f"Unsupported run_kind: {run_kind}")
    cutoff = _date_value(as_of_date or date.today(), field="as_of_date")
    where = ["run_kind = %s", "as_of_date <= %s"]
    params: list[object] = [resolved_kind, cutoff.isoformat()]
    if model_version is not None:
        where.append("model_version = %s")
        params.append(str(model_version))
    sql = f"""
    SELECT *
    FROM economic_cycle_snapshot
    WHERE {' AND '.join(where)}
    ORDER BY as_of_date DESC, updated_at DESC
    LIMIT 1
    """
    rows = _query(DB_META, sql, tuple(params), query_fn=query_fn)
    eligible = []
    for raw in rows:
        row = dict(raw)
        if str(row.get("run_kind")) != resolved_kind:
            continue
        if model_version is not None and str(row.get("model_version")) != str(model_version):
            continue
        observed = _date_value(row.get("as_of_date"), field="as_of_date")
        if observed <= cutoff:
            row["as_of_date"] = observed.isoformat()
            eligible.append(row)
    return (
        max(eligible, key=lambda row: str(row["as_of_date"]))
        if eligible
        else None
    )


def load_cycle_history(
    *,
    start_date: str | date,
    end_date: str | date,
    known_at_date: str | date | None = None,
    query_fn: QueryFn | None = None,
) -> list[dict[str, object]]:
    """Load bounded month-end replay snapshots in chronological order."""

    start = _date_value(start_date, field="start_date")
    end = _date_value(end_date, field="end_date")
    if start > end:
        raise ValueError("start_date must be earlier than or equal to end_date")
    known_at = (
        _date_value(known_at_date, field="known_at_date")
        if known_at_date is not None
        else None
    )
    where = [
        "run_kind = 'historical_replay'",
        "as_of_date >= %s",
        "as_of_date <= %s",
    ]
    params: list[object] = [start.isoformat(), end.isoformat()]
    if known_at is not None:
        where.append("as_of_date <= %s")
        params.append(known_at.isoformat())
    sql = f"""
    SELECT *
    FROM economic_cycle_snapshot
    WHERE {' AND '.join(where)}
    ORDER BY as_of_date ASC
    """
    rows = _query(
        DB_META, sql, tuple(params), query_fn=query_fn
    )
    eligible: list[dict[str, object]] = []
    for raw in rows:
        row = dict(raw)
        if str(row.get("run_kind") or "historical_replay") != "historical_replay":
            continue
        observed = _date_value(row.get("as_of_date"), field="as_of_date")
        if not (start <= observed <= end):
            continue
        if known_at is not None:
            if row.get("data_cutoff_date") in (None, ""):
                continue
            data_cutoff = _date_value(
                row.get("data_cutoff_date"),
                field="data_cutoff_date",
            )
            if not (data_cutoff <= observed <= known_at):
                continue
            row["data_cutoff_date"] = data_cutoff.isoformat()
        row["as_of_date"] = observed.isoformat()
        eligible.append(row)
    return sorted(eligible, key=lambda row: str(row["as_of_date"]))
