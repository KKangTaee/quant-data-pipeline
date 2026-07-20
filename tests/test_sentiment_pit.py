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


class FakeTransactionDb(FakeSchemaDb):
    def __init__(self, fail_snapshot: bool = False) -> None:
        super().__init__()
        self.fail_snapshot = fail_snapshot
        self.events: list[str] = []

    def begin(self) -> None:
        self.events.append("begin")

    def commit(self) -> None:
        self.events.append("commit")

    def rollback(self) -> None:
        self.events.append("rollback")

    def executemany(self, sql: str, rows: list[dict]) -> None:
        del rows
        if self.fail_snapshot and "observation_snapshot" in sql:
            raise RuntimeError("snapshot write failed")
        self.events.append("snapshot" if "observation_snapshot" in sql else "canonical")

    def execute(self, sql: str, params=None) -> None:
        del sql
        if params is not None:
            self.events.append("batch")


def sentiment_row(value: float) -> dict:
    return {
        "series_id": "CNN_FEAR_GREED",
        "observation_date": "2026-07-17",
        "source": "cnn_fear_greed",
        "source_type": "official",
        "source_mode": "json",
        "source_ref": "https://www.cnn.com/markets/fear-and-greed",
        "series_name": "CNN Fear & Greed Index",
        "category": "sentiment_index",
        "frequency": "daily",
        "units": "score_0_100",
        "value": value,
        "release_lag_days": None,
        "coverage_status": "actual",
        "missing_fields_json": '{"rating":"fear"}',
        "collected_at": "2026-07-20 01:00:00",
        "error_msg": None,
    }


class SentimentPitPersistenceTests(unittest.TestCase):
    def test_deduplication_keeps_last_value(self) -> None:
        from finance.data.sentiment_store import deduplicate_sentiment_rows

        rows = deduplicate_sentiment_rows([sentiment_row(37.0), sentiment_row(37.1)])
        self.assertEqual([row["value"] for row in rows], [37.1])

    def test_success_commits_snapshot_and_canonical_together(self) -> None:
        from finance.data.sentiment_store import persist_market_sentiment_source_capture

        db = FakeTransactionDb()
        result = persist_market_sentiment_source_capture(
            db,
            collection_id="c",
            batch_id="b",
            source="cnn_fear_greed",
            source_ref="cnn",
            requested_at="2026-07-20 00:59:59.000000",
            observed_at="2026-07-20 01:00:00.000000",
            completed_at="2026-07-20 01:00:01.000000",
            status="success",
            coverage={"expected": 8, "observed": 8, "missing_series": []},
            rows=[sentiment_row(37.1)],
        )
        self.assertEqual(db.events, ["begin", "batch", "snapshot", "canonical", "commit"])
        self.assertEqual(result["snapshot_rows_written"], 1)

    def test_snapshot_failure_rolls_back_before_canonical(self) -> None:
        from finance.data.sentiment_store import persist_market_sentiment_source_capture

        db = FakeTransactionDb(fail_snapshot=True)
        with self.assertRaisesRegex(RuntimeError, "snapshot write failed"):
            persist_market_sentiment_source_capture(
                db,
                collection_id="c",
                batch_id="b",
                source="cnn_fear_greed",
                source_ref="cnn",
                requested_at="2026-07-20 00:59:59.000000",
                observed_at="2026-07-20 01:00:00.000000",
                completed_at="2026-07-20 01:00:01.000000",
                status="success",
                coverage={},
                rows=[sentiment_row(37.1)],
            )
        self.assertEqual(db.events, ["begin", "batch", "rollback"])

    def test_source_failure_records_only_a_batch(self) -> None:
        from finance.data.sentiment_store import record_market_sentiment_source_failure

        db = FakeTransactionDb()
        record_market_sentiment_source_failure(
            db,
            collection_id="c",
            batch_id="b",
            source="cnn_fear_greed",
            source_ref="cnn",
            requested_at="2026-07-20 00:59:59.000000",
            completed_at="2026-07-20 01:00:01.000000",
            status="error",
            error_msg="blocked",
        )
        self.assertEqual(db.events, ["batch"])


if __name__ == "__main__":
    unittest.main()
