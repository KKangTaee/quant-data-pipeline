from __future__ import annotations

import unittest
from unittest.mock import MagicMock, patch


class FakeSchemaDb:
    def __init__(self) -> None:
        self.used: list[str] = []
        self.executed: list[str] = []

    def use_db(self, name: str) -> None:
        self.used.append(name)

    def execute(self, sql: str, params=None) -> None:
        del params
        self.executed.append(sql)


class SentimentPitSchemaTests(unittest.TestCase):
    def test_schema_and_sync_contracts(self) -> None:
        from finance.data.db.schema import PROVIDER_SCHEMAS
        from finance.data.sentiment_store import (
            MARKET_SENTIMENT_TARGET_TABLES,
            ensure_market_sentiment_schema,
        )

        batch = PROVIDER_SCHEMAS["market_sentiment_collection_batch"]
        snapshot = PROVIDER_SCHEMAS["market_sentiment_observation_snapshot"]
        self.assertIn("batch_id CHAR(36) PRIMARY KEY", batch)
        self.assertIn("observed_at DATETIME(6) NULL", batch)
        self.assertIn("uk_sentiment_snapshot_batch_series_date_source", snapshot)
        self.assertIn("ix_sentiment_snapshot_as_known", snapshot)

        db = FakeSchemaDb()
        with patch("finance.data.sentiment_store.sync_table_schema") as sync:
            ensure_market_sentiment_schema(db)
        self.assertEqual(db.used, ["finance_meta"])
        self.assertEqual(len(MARKET_SENTIMENT_TARGET_TABLES), 3)
        self.assertEqual(sync.call_count, 3)


if __name__ == "__main__":
    unittest.main()
