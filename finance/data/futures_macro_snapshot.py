"""Persist the compact Overview Futures Macro snapshot."""

from __future__ import annotations

from typing import Any

from .db.mysql import MySQLClient
from .db.schema import FUTURES_MARKET_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
SNAPSHOT_TABLE = "futures_macro_snapshot"


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
          snapshot_key, source_marker, as_of_date, schema_version,
          algorithm_version, status, snapshot_json, materialized_at
        ) VALUES (
          %(snapshot_key)s, %(source_marker)s, %(as_of_date)s, %(schema_version)s,
          %(algorithm_version)s, %(status)s, %(snapshot_json)s, %(materialized_at)s
        )
        ON DUPLICATE KEY UPDATE
          source_marker = VALUES(source_marker),
          as_of_date = VALUES(as_of_date),
          schema_version = VALUES(schema_version),
          algorithm_version = VALUES(algorithm_version),
          status = VALUES(status),
          snapshot_json = VALUES(snapshot_json),
          materialized_at = VALUES(materialized_at)
        """
        db.executemany(sql, [row])
        return 1
    finally:
        if owns_connection:
            db.close()
