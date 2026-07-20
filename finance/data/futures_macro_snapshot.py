"""Persist the compact Overview Futures Macro snapshot."""

from __future__ import annotations

from typing import Any

from .db.mysql import MySQLClient
from .db.schema import FUTURES_MARKET_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
SNAPSHOT_TABLE = "futures_macro_snapshot"
HISTORY_TABLE = "futures_macro_forecast_history"


def upsert_futures_macro_snapshot(
    row: dict[str, object],
    *,
    connection: Any = None,
) -> int:
    """UPSERT one versioned current snapshot without replacing a good row first."""

    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    try:
        if owns_connection:
            db.use_db(DB_META)
            schema = FUTURES_MARKET_SCHEMAS[SNAPSHOT_TABLE]
            db.execute(schema)
            sync_table_schema(db, SNAPSHOT_TABLE, schema, DB_META)
        sql = f"""
        INSERT INTO {SNAPSHOT_TABLE} (
          snapshot_key, source_marker, as_of_date, input_fingerprint,
          schema_version, algorithm_version, session_status,
          status, snapshot_json, materialized_at
        ) VALUES (
          %(snapshot_key)s, %(source_marker)s, %(as_of_date)s, %(input_fingerprint)s,
          %(schema_version)s, %(algorithm_version)s, %(session_status)s,
          %(status)s, %(snapshot_json)s, %(materialized_at)s
        )
        ON DUPLICATE KEY UPDATE
          source_marker = VALUES(source_marker),
          as_of_date = VALUES(as_of_date),
          input_fingerprint = VALUES(input_fingerprint),
          schema_version = VALUES(schema_version),
          algorithm_version = VALUES(algorithm_version),
          session_status = VALUES(session_status),
          status = VALUES(status),
          snapshot_json = VALUES(snapshot_json),
          materialized_at = VALUES(materialized_at)
        """
        db.executemany(sql, [row])
        return 1
    finally:
        if owns_connection:
            db.close()


def persist_futures_macro_snapshot_bundle(
    current_row: dict[str, object],
    history_row: dict[str, object],
    *,
    connection: Any = None,
) -> dict[str, int]:
    """Atomically append immutable history and advance only a final, non-older current."""

    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    try:
        if owns_connection:
            db.use_db(DB_META)
            for table in (SNAPSHOT_TABLE, HISTORY_TABLE):
                schema = FUTURES_MARKET_SCHEMAS[table]
                db.execute(schema)
                sync_table_schema(db, table, schema, DB_META)
        db.begin()
        history_sql = f"""
        INSERT INTO {HISTORY_TABLE} (
          forecast_identity, as_of_date, source_marker, input_fingerprint,
          schema_version, feature_schema_version, algorithm_version,
          selected_models_json, status_json, forecast_json,
          known_at, materialized_at
        ) VALUES (
          %(forecast_identity)s, %(as_of_date)s, %(source_marker)s,
          %(input_fingerprint)s, %(schema_version)s, %(feature_schema_version)s,
          %(algorithm_version)s, %(selected_models_json)s, %(status_json)s,
          %(forecast_json)s, %(known_at)s, %(materialized_at)s
        )
        ON DUPLICATE KEY UPDATE forecast_identity = forecast_identity
        """
        db.executemany(history_sql, [history_row])
        current_sql = f"""
        INSERT INTO {SNAPSHOT_TABLE} (
          snapshot_key, source_marker, as_of_date, input_fingerprint,
          schema_version, algorithm_version, session_status,
          status, snapshot_json, materialized_at
        )
        SELECT
          %(snapshot_key)s, %(source_marker)s, %(as_of_date)s,
          %(input_fingerprint)s, %(schema_version)s, %(algorithm_version)s,
          %(session_status)s, %(status)s, %(snapshot_json)s, %(materialized_at)s
        FROM DUAL
        WHERE %(session_status)s = 'FINAL'
        ON DUPLICATE KEY UPDATE
          source_marker = IF(VALUES(as_of_date) >= as_of_date, VALUES(source_marker), source_marker),
          as_of_date = IF(VALUES(as_of_date) >= as_of_date, VALUES(as_of_date), as_of_date),
          input_fingerprint = IF(VALUES(as_of_date) >= as_of_date, VALUES(input_fingerprint), input_fingerprint),
          schema_version = IF(VALUES(as_of_date) >= as_of_date, VALUES(schema_version), schema_version),
          algorithm_version = IF(VALUES(as_of_date) >= as_of_date, VALUES(algorithm_version), algorithm_version),
          session_status = IF(VALUES(as_of_date) >= as_of_date, VALUES(session_status), session_status),
          status = IF(VALUES(as_of_date) >= as_of_date, VALUES(status), status),
          snapshot_json = IF(VALUES(as_of_date) >= as_of_date, VALUES(snapshot_json), snapshot_json),
          materialized_at = IF(VALUES(as_of_date) >= as_of_date, VALUES(materialized_at), materialized_at)
        """
        db.executemany(current_sql, [current_row])
        db.commit()
        return {"history_rows": 1, "current_rows": 1}
    except Exception:
        db.rollback()
        raise
    finally:
        if owns_connection:
            db.close()
