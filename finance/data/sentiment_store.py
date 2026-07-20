from __future__ import annotations

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


def ensure_market_sentiment_schema(db: MySQLClient) -> None:
    """Create or additively sync the three sentiment persistence tables."""
    db.use_db(DB_META)
    for table_name in MARKET_SENTIMENT_TARGET_TABLES:
        sql = PROVIDER_SCHEMAS[table_name]
        db.execute(sql)
        sync_table_schema(db, table_name, sql, DB_META)
