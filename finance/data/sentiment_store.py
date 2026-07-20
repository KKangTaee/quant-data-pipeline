from __future__ import annotations

import json
from typing import Any, Literal

from finance.data.db.mysql import MySQLClient
from finance.data.db.schema import PROVIDER_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
MACRO_TABLE = "macro_series_observation"
MARKET_SENTIMENT_BATCH_TABLE = "market_sentiment_collection_batch"
MARKET_SENTIMENT_SNAPSHOT_TABLE = "market_sentiment_observation_snapshot"
MARKET_SENTIMENT_TARGET_TABLES = (
    MACRO_TABLE,
    MARKET_SENTIMENT_BATCH_TABLE,
    MARKET_SENTIMENT_SNAPSHOT_TABLE,
)
SENTIMENT_CAPTURE_SCHEMA_VERSION = "market_sentiment_capture_v1"
CaptureStatus = Literal["success", "partial", "missing", "error"]
AAII_CANONICAL_SERIES = {
    "AAII_BULLISH",
    "AAII_NEUTRAL",
    "AAII_BEARISH",
    "AAII_BULL_BEAR_SPREAD",
}


def ensure_market_sentiment_schema(db: MySQLClient) -> None:
    """Create or additively sync the three sentiment persistence tables."""
    db.use_db(DB_META)
    for table_name in MARKET_SENTIMENT_TARGET_TABLES:
        sql = PROVIDER_SCHEMAS[table_name]
        db.execute(sql)
        sync_table_schema(db, table_name, sql, DB_META)


def deduplicate_sentiment_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Keep the last normalized row for each canonical business key."""
    by_key: dict[tuple[str, str, str], dict[str, Any]] = {}
    for row in rows:
        key = (
            str(row.get("series_id") or "").upper(),
            str(row.get("observation_date") or ""),
            str(row.get("source") or ""),
        )
        if all(key):
            by_key[key] = dict(row)
    return [by_key[key] for key in sorted(by_key)]


def _batch_params(**values: Any) -> dict[str, Any]:
    rows = values.pop("rows")
    coverage = values.pop("coverage")
    error_msg = values.pop("error_msg", None)
    dates = sorted(str(row["observation_date"]) for row in rows if row.get("observation_date"))
    return {
        **values,
        "schema_version": SENTIMENT_CAPTURE_SCHEMA_VERSION,
        "observation_start": dates[0] if dates else None,
        "observation_end": dates[-1] if dates else None,
        "row_count": len(rows),
        "coverage_json": json.dumps(coverage, ensure_ascii=False, sort_keys=True),
        "error_msg": str(error_msg or "")[:500] or None,
    }


def _insert_batch(db: MySQLClient, params: dict[str, Any]) -> None:
    db.execute(
        f"""
        INSERT INTO {MARKET_SENTIMENT_BATCH_TABLE} (
          batch_id, collection_id, source, source_ref, schema_version, status,
          requested_at, observed_at, completed_at, observation_start,
          observation_end, row_count, coverage_json, error_msg
        ) VALUES (
          %(batch_id)s, %(collection_id)s, %(source)s, %(source_ref)s,
          %(schema_version)s, %(status)s, %(requested_at)s, %(observed_at)s,
          %(completed_at)s, %(observation_start)s, %(observation_end)s,
          %(row_count)s, %(coverage_json)s, %(error_msg)s
        ) ON DUPLICATE KEY UPDATE batch_id = VALUES(batch_id)
        """,
        params,
    )


def _insert_snapshot_rows(
    db: MySQLClient,
    batch_id: str,
    collection_id: str,
    observed_at: str,
    rows: list[dict[str, Any]],
) -> None:
    params = [
        {
            **row,
            "batch_id": batch_id,
            "collection_id": collection_id,
            "observed_at": observed_at,
        }
        for row in rows
    ]
    db.executemany(
        f"""
        INSERT INTO {MARKET_SENTIMENT_SNAPSHOT_TABLE} (
          batch_id, collection_id, series_id, observation_date, source,
          source_type, source_mode, source_ref, series_name, category,
          frequency, units, value, release_lag_days, coverage_status,
          missing_fields_json, observed_at, error_msg
        ) VALUES (
          %(batch_id)s, %(collection_id)s, %(series_id)s, %(observation_date)s,
          %(source)s, %(source_type)s, %(source_mode)s, %(source_ref)s,
          %(series_name)s, %(category)s, %(frequency)s, %(units)s, %(value)s,
          %(release_lag_days)s, %(coverage_status)s, %(missing_fields_json)s,
          %(observed_at)s, %(error_msg)s
        ) ON DUPLICATE KEY UPDATE id = id
        """,
        params,
    )


def _upsert_canonical_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    db.executemany(
        f"""
        INSERT INTO {MACRO_TABLE} (
          series_id, observation_date, source, source_type, source_mode,
          source_ref, series_name, category, frequency, units, value,
          release_lag_days, coverage_status, missing_fields_json,
          collected_at, error_msg
        ) VALUES (
          %(series_id)s, %(observation_date)s, %(source)s, %(source_type)s,
          %(source_mode)s, %(source_ref)s, %(series_name)s, %(category)s,
          %(frequency)s, %(units)s, %(value)s, %(release_lag_days)s,
          %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s,
          %(error_msg)s
        ) ON DUPLICATE KEY UPDATE
          source_type=VALUES(source_type), source_mode=VALUES(source_mode),
          source_ref=VALUES(source_ref), series_name=VALUES(series_name),
          category=VALUES(category), frequency=VALUES(frequency),
          units=VALUES(units), value=VALUES(value),
          release_lag_days=VALUES(release_lag_days),
          coverage_status=VALUES(coverage_status),
          missing_fields_json=VALUES(missing_fields_json),
          collected_at=VALUES(collected_at), error_msg=VALUES(error_msg)
        """,
        rows,
    )


def replace_aaii_canonical_history(
    db: MySQLClient,
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Replace official AAII canonical history without manufacturing PIT snapshots."""
    normalized = deduplicate_sentiment_rows(rows)
    dates_by_series: dict[str, set[str]] = {
        series_id: set() for series_id in AAII_CANONICAL_SERIES
    }
    for row in normalized:
        series_id = str(row.get("series_id") or "").upper()
        if (
            row.get("source") != "aaii_sentiment_survey"
            or series_id not in AAII_CANONICAL_SERIES
        ):
            raise RuntimeError(
                "AAII canonical backfill contains an unexpected source or series"
            )
        dates_by_series[series_id].add(str(row.get("observation_date") or ""))
    date_sets = list(dates_by_series.values())
    if not date_sets[0] or any(item != date_sets[0] for item in date_sets[1:]):
        raise RuntimeError(
            "AAII canonical backfill requires four series with aligned dates"
        )

    dates = sorted(date_sets[0])
    db.begin()
    try:
        db.execute(
            f"""
            DELETE FROM {MACRO_TABLE}
            WHERE source = %(source)s
              AND series_id IN (
                'AAII_BULLISH', 'AAII_NEUTRAL', 'AAII_BEARISH',
                'AAII_BULL_BEAR_SPREAD'
              )
              AND observation_date <= %(latest_date)s
            """,
            {
                "source": "aaii_sentiment_survey",
                "latest_date": dates[-1],
            },
        )
        _upsert_canonical_rows(db, normalized)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {
        "canonical_rows_written": len(normalized),
        "observation_start": dates[0],
        "observation_end": dates[-1],
        "week_count": len(dates),
    }


def persist_market_sentiment_source_capture(
    db: MySQLClient,
    *,
    collection_id: str,
    batch_id: str,
    source: str,
    source_ref: str | None,
    requested_at: str,
    observed_at: str,
    completed_at: str,
    status: Literal["success", "partial"],
    coverage: dict[str, Any],
    rows: list[dict[str, Any]],
) -> dict[str, Any]:
    """Persist one source response atomically to immutable and canonical stores."""
    normalized = deduplicate_sentiment_rows(rows)
    batch = _batch_params(
        collection_id=collection_id,
        batch_id=batch_id,
        source=source,
        source_ref=source_ref,
        requested_at=requested_at,
        observed_at=observed_at,
        completed_at=completed_at,
        status=status,
        coverage=coverage,
        rows=normalized,
        error_msg=None,
    )
    db.begin()
    try:
        _insert_batch(db, batch)
        _insert_snapshot_rows(db, batch_id, collection_id, observed_at, normalized)
        _upsert_canonical_rows(db, normalized)
        db.commit()
    except Exception:
        db.rollback()
        raise
    return {
        "batch_id": batch_id,
        "status": status,
        "snapshot_rows_written": len(normalized),
        "canonical_rows_written": len(normalized),
    }


def record_market_sentiment_source_failure(
    db: MySQLClient,
    *,
    collection_id: str,
    batch_id: str,
    source: str,
    source_ref: str | None,
    requested_at: str,
    completed_at: str,
    status: Literal["missing", "error"],
    error_msg: str,
) -> None:
    """Record a failed source attempt without creating normalized observations."""
    _insert_batch(
        db,
        _batch_params(
            collection_id=collection_id,
            batch_id=batch_id,
            source=source,
            source_ref=source_ref,
            requested_at=requested_at,
            observed_at=None,
            completed_at=completed_at,
            status=status,
            coverage={},
            rows=[],
            error_msg=error_msg,
        ),
    )
