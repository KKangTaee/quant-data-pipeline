"""DB-only reader for the materialized Overview Futures Macro snapshot."""

from __future__ import annotations

from collections.abc import Callable
from typing import Any

from finance.data.db.mysql import MySQLClient


DB_META = "finance_meta"
SNAPSHOT_TABLE = "futures_macro_snapshot"
HISTORY_TABLE = "futures_macro_forecast_history"
QueryFn = Callable[[str, str, tuple[Any, ...]], list[dict[str, Any]]]


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
        if (SNAPSHOT_TABLE in message or HISTORY_TABLE in message) and (
            "doesn't exist" in message or "unknown table" in message
        ):
            return []
        raise
    finally:
        db.close()


def load_latest_futures_macro_snapshot(
    *,
    snapshot_key: str = "overview_current",
    query_fn: QueryFn | None = None,
) -> dict[str, Any] | None:
    """Return one persisted row without loading futures candles or calculating."""

    try:
        rows = _query(
            DB_META,
            f"""
            SELECT snapshot_key, source_marker, as_of_date, schema_version,
                   input_fingerprint, algorithm_version, session_status,
                   status, snapshot_json, materialized_at,
                   created_at, updated_at
            FROM {SNAPSHOT_TABLE}
            WHERE snapshot_key = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (str(snapshot_key),),
            query_fn=query_fn,
        )
    except Exception as exc:
        message = str(exc).lower()
        if "unknown column" not in message or not any(
            column in message for column in ("input_fingerprint", "session_status")
        ):
            raise
        rows = _query(
            DB_META,
            f"""
            SELECT snapshot_key, source_marker, as_of_date, schema_version,
                   algorithm_version, status, snapshot_json, materialized_at,
                   created_at, updated_at
            FROM {SNAPSHOT_TABLE}
            WHERE snapshot_key = %s
            ORDER BY updated_at DESC
            LIMIT 1
            """,
            (str(snapshot_key),),
            query_fn=query_fn,
        )
        for row in rows:
            row.setdefault("input_fingerprint", "")
            row.setdefault("session_status", "LEGACY")
    return dict(rows[0]) if rows else None


def load_futures_macro_forecast_history(
    *,
    as_of_date: str | None = None,
    limit: int = 60,
    query_fn: QueryFn | None = None,
) -> list[dict[str, Any]]:
    """Return immutable compact forecasts without rebuilding their model inputs."""

    where = "WHERE as_of_date = %s" if as_of_date else ""
    params: tuple[Any, ...] = (str(as_of_date),) if as_of_date else ()
    rows = _query(
        DB_META,
        f"""
        SELECT forecast_identity, as_of_date, source_marker, input_fingerprint,
               schema_version, feature_schema_version, algorithm_version,
               selected_models_json, status_json, forecast_json,
               known_at, materialized_at, created_at
        FROM {HISTORY_TABLE}
        {where}
        ORDER BY as_of_date DESC, materialized_at DESC
        LIMIT {max(1, min(int(limit), 500))}
        """,
        params,
        query_fn=query_fn,
    )
    return [dict(row) for row in rows]
