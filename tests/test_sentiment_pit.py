from __future__ import annotations

from datetime import date, timedelta
import unittest
from unittest.mock import MagicMock, patch

import pandas as pd


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
        if getattr(self, "fail_canonical", False) and "macro_series_observation" in sql:
            raise RuntimeError("canonical write failed")
        self.events.append("snapshot" if "observation_snapshot" in sql else "canonical")

    def execute(self, sql: str, params=None) -> None:
        if "DELETE FROM macro_series_observation" in sql:
            self.events.append("delete")
            self.deleted_params = dict(params or {})
            return
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


def aaii_week_rows(observation_date: str) -> list[dict]:
    values = {
        "AAII_BULLISH": 44.9,
        "AAII_NEUTRAL": 22.2,
        "AAII_BEARISH": 32.9,
        "AAII_BULL_BEAR_SPREAD": 12.0,
    }
    return [
        {
            **sentiment_row(value),
            "series_id": series_id,
            "observation_date": observation_date,
            "source": "aaii_sentiment_survey",
            "source_mode": "xls",
        }
        for series_id, value in values.items()
    ]


class SentimentAaiiWorkbookTests(unittest.TestCase):
    def test_workbook_frame_normalizes_four_series_per_complete_week(self) -> None:
        from finance.data.sentiment import parse_aaii_sentiment_frame

        frame = pd.DataFrame(
            {
                "Reported Date": [pd.Timestamp("1987-07-24"), pd.Timestamp("2026-07-16")],
                "Bullish": [0.35, 0.449074],
                "Neutral": [0.30, 0.222222],
                "Bearish": [0.35, 0.328704],
            }
        )

        rows = parse_aaii_sentiment_frame(
            frame,
            collected_at="2026-07-20 09:00:00",
            source_mode="xls",
            source_ref="https://www.aaii.com/files/surveys/sentiment.xls",
        )

        self.assertEqual(len(rows), 8)
        latest = {
            row["series_id"]: row
            for row in rows
            if row["observation_date"] == "2026-07-16"
        }
        self.assertAlmostEqual(latest["AAII_BULLISH"]["value"], 44.9074, places=4)
        self.assertAlmostEqual(latest["AAII_BULL_BEAR_SPREAD"]["value"], 12.037, places=3)
        self.assertIn(
            '"reported_date": "2026-07-16"',
            latest["AAII_BULLISH"]["missing_fields_json"],
        )

    def test_workbook_frame_skips_incomplete_week(self) -> None:
        from finance.data.sentiment import parse_aaii_sentiment_frame

        frame = pd.DataFrame(
            {
                "Reported Date": [pd.Timestamp("2026-07-09"), pd.Timestamp("2026-07-16")],
                "Bullish": [0.40, 0.44],
                "Neutral": [0.25, None],
                "Bearish": [0.35, 0.33],
            }
        )

        rows = parse_aaii_sentiment_frame(
            frame,
            collected_at="2026-07-20 09:00:00",
            source_mode="xls",
            source_ref="xls",
        )

        self.assertEqual({row["observation_date"] for row in rows}, {"2026-07-09"})
        self.assertEqual(len(rows), 4)

    def test_daily_fetch_keeps_latest_26_complete_weeks(self) -> None:
        from finance.data import sentiment

        rows = []
        for offset in range(30):
            observed = date(2026, 1, 1) + timedelta(days=7 * offset)
            for series_id in (
                "AAII_BULLISH",
                "AAII_NEUTRAL",
                "AAII_BEARISH",
                "AAII_BULL_BEAR_SPREAD",
            ):
                rows.append(
                    {"series_id": series_id, "observation_date": observed.isoformat()}
                )
        with patch.object(
            sentiment,
            "fetch_aaii_sentiment_history_rows",
            return_value=rows,
        ):
            recent = sentiment.fetch_aaii_sentiment_rows()

        self.assertEqual(len(recent), 104)
        self.assertEqual(
            min(row["observation_date"] for row in recent),
            "2026-01-29",
        )

    def test_daily_fetch_falls_back_to_html_and_anchors_wednesday_on_thursday(self) -> None:
        from finance.data import sentiment

        html = b"""
        <table>
          <tr><th>Reported Date</th><th>Bullish</th><th>Neutral</th><th>Bearish</th></tr>
          <tr><td>Jul 15</td><td>44.9%</td><td>22.2%</td><td>32.9%</td></tr>
        </table>
        """
        with (
            patch.object(
                sentiment,
                "fetch_aaii_sentiment_history_rows",
                side_effect=RuntimeError("blocked"),
            ),
            patch.object(sentiment, "_fetch_bytes", return_value=html),
        ):
            rows = sentiment.fetch_aaii_sentiment_rows(today=date(2026, 7, 20))

        self.assertEqual({row["observation_date"] for row in rows}, {"2026-07-16"})
        self.assertTrue(
            all(
                '"reported_date_raw": "Jul 15"' in row["missing_fields_json"]
                for row in rows
            )
        )


class SentimentAaiiBackfillTests(unittest.TestCase):
    def test_canonical_backfill_deletes_only_through_workbook_latest_then_upserts(self) -> None:
        from finance.data.sentiment_store import replace_aaii_canonical_history

        db = FakeTransactionDb()
        result = replace_aaii_canonical_history(
            db,
            aaii_week_rows("1987-07-24") + aaii_week_rows("2026-07-16"),
        )

        self.assertEqual(db.events, ["begin", "delete", "canonical", "commit"])
        self.assertEqual(db.deleted_params["latest_date"], "2026-07-16")
        self.assertEqual(result["week_count"], 2)
        self.assertEqual(result["canonical_rows_written"], 8)

    def test_canonical_backfill_rejects_misaligned_series_before_transaction(self) -> None:
        from finance.data.sentiment_store import replace_aaii_canonical_history

        db = FakeTransactionDb()
        with self.assertRaisesRegex(RuntimeError, "aligned dates"):
            replace_aaii_canonical_history(
                db,
                aaii_week_rows("2026-07-16")[:-1],
            )
        self.assertEqual(db.events, [])

    def test_canonical_backfill_rolls_back_when_upsert_fails(self) -> None:
        from finance.data.sentiment_store import replace_aaii_canonical_history

        db = FakeTransactionDb()
        db.fail_canonical = True
        with self.assertRaisesRegex(RuntimeError, "canonical write failed"):
            replace_aaii_canonical_history(db, aaii_week_rows("2026-07-16"))
        self.assertEqual(db.events, ["begin", "delete", "rollback"])

    def test_backfill_fetches_before_db_and_never_writes_snapshot(self) -> None:
        from finance.data import sentiment

        rows = aaii_week_rows("2026-07-16")
        db = MagicMock()
        with (
            patch.object(
                sentiment,
                "fetch_aaii_sentiment_history_rows",
                return_value=rows,
            ) as fetch,
            patch.object(sentiment, "MySQLClient", return_value=db),
            patch.object(sentiment, "ensure_market_sentiment_schema") as ensure,
            patch.object(
                sentiment,
                "replace_aaii_canonical_history",
                return_value={"canonical_rows_written": 4},
            ) as replace,
        ):
            result = sentiment.backfill_aaii_sentiment_history()

        fetch.assert_called_once()
        ensure.assert_called_once_with(db)
        replace.assert_called_once_with(db, rows)
        db.close.assert_called_once_with()
        self.assertNotIn("snapshot_rows_written", result)


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


class SentimentPitCollectorTests(unittest.TestCase):
    def test_cnn_failure_does_not_block_aaii(self) -> None:
        from finance.data import sentiment

        aaii = {
            **sentiment_row(44.9),
            "series_id": "AAII_BULLISH",
            "source": "aaii_sentiment_survey",
        }
        persisted: list[str] = []
        failures: list[str] = []
        db = MagicMock()
        with (
            patch.object(
                sentiment,
                "fetch_cnn_fear_greed_rows",
                side_effect=RuntimeError("CNN blocked"),
            ),
            patch.object(sentiment, "fetch_aaii_sentiment_rows", return_value=[aaii]),
            patch.object(sentiment, "MySQLClient", return_value=db),
            patch.object(sentiment, "ensure_market_sentiment_schema"),
            patch.object(
                sentiment,
                "persist_market_sentiment_source_capture",
                side_effect=lambda _db, **kw: persisted.append(kw["source"])
                or {
                    "batch_id": kw["batch_id"],
                    "status": kw["status"],
                    "snapshot_rows_written": 1,
                    "canonical_rows_written": 1,
                },
            ),
            patch.object(
                sentiment,
                "record_market_sentiment_source_failure",
                side_effect=lambda _db, **kw: failures.append(kw["source"]),
            ),
        ):
            with self.assertLogs(sentiment.LOGGER.name, level="WARNING"):
                result = sentiment.collect_and_store_market_sentiment()
        self.assertEqual(persisted, ["aaii_sentiment_survey"])
        self.assertEqual(failures, ["cnn_fear_greed"])
        self.assertEqual(result["stored"], 1)
        self.assertIn("cnn_fear_greed", result["batch_ids"])

    def test_success_uses_distinct_batches_and_source_observed_times(self) -> None:
        from finance.data import sentiment

        cnn = sentiment_row(37.1)
        aaii = {
            **sentiment_row(44.9),
            "series_id": "AAII_BULLISH",
            "source": "aaii_sentiment_survey",
            "collected_at": "2026-07-20 01:05:00",
        }
        captures: list[dict] = []
        db = MagicMock()
        with (
            patch.object(sentiment, "fetch_cnn_fear_greed_rows", return_value=[cnn]),
            patch.object(sentiment, "fetch_aaii_sentiment_rows", return_value=[aaii]),
            patch.object(sentiment, "MySQLClient", return_value=db),
            patch.object(sentiment, "ensure_market_sentiment_schema"),
            patch.object(
                sentiment,
                "persist_market_sentiment_source_capture",
                side_effect=lambda _db, **kw: captures.append(kw)
                or {
                    "batch_id": kw["batch_id"],
                    "status": kw["status"],
                    "snapshot_rows_written": 1,
                    "canonical_rows_written": 1,
                },
            ),
        ):
            result = sentiment.collect_and_store_market_sentiment()
        self.assertEqual(len({row["batch_id"] for row in captures}), 2)
        self.assertEqual(
            [row["observed_at"] for row in captures],
            [cnn["collected_at"], aaii["collected_at"]],
        )
        self.assertEqual(result["snapshot_rows_stored"], 2)
        self.assertEqual(result["stored"], 2)
        self.assertEqual(set(result["batch_ids"]), {"cnn_fear_greed", "aaii_sentiment_survey"})

    def test_failure_recording_error_still_allows_next_source(self) -> None:
        from finance.data import sentiment

        aaii = {
            **sentiment_row(44.9),
            "series_id": "AAII_BULLISH",
            "source": "aaii_sentiment_survey",
        }
        persisted: list[str] = []
        db = MagicMock()
        with (
            patch.object(
                sentiment,
                "fetch_cnn_fear_greed_rows",
                side_effect=RuntimeError("CNN blocked"),
            ),
            patch.object(sentiment, "fetch_aaii_sentiment_rows", return_value=[aaii]),
            patch.object(sentiment, "MySQLClient", return_value=db),
            patch.object(sentiment, "ensure_market_sentiment_schema"),
            patch.object(
                sentiment,
                "persist_market_sentiment_source_capture",
                side_effect=lambda _db, **kw: persisted.append(kw["source"])
                or {
                    "batch_id": kw["batch_id"],
                    "status": kw["status"],
                    "snapshot_rows_written": 1,
                    "canonical_rows_written": 1,
                },
            ),
            patch.object(
                sentiment,
                "record_market_sentiment_source_failure",
                side_effect=RuntimeError("failure batch blocked"),
            ),
        ):
            with self.assertLogs(sentiment.LOGGER.name, level="WARNING"):
                result = sentiment.collect_and_store_market_sentiment()
        self.assertEqual(persisted, ["aaii_sentiment_survey"])
        self.assertEqual(result["stored"], 1)
        self.assertNotIn("cnn_fear_greed", result["batch_ids"])


class SentimentPitLoaderTests(unittest.TestCase):
    def test_as_known_uses_cutoff_and_default_observation_end(self) -> None:
        from finance.loaders.sentiment import load_market_sentiment_as_known

        captured = {}

        def query(database, sql, params):
            captured.update(database=database, sql=sql, params=params)
            return [
                {
                    **sentiment_row(37.1),
                    "id": 1,
                    "batch_id": "b",
                    "collection_id": "c",
                    "observed_at": "2026-07-20 01:00:00",
                }
            ]

        frame = load_market_sentiment_as_known(
            known_at="2026-07-20T01:30:00Z",
            series_ids=["CNN_FEAR_GREED"],
            query_fn=query,
        )
        self.assertIn("ROW_NUMBER() OVER", captured["sql"])
        self.assertIn("observed_at <= %s", captured["sql"])
        self.assertIn("observation_date <= %s", captured["sql"])
        self.assertIn("ORDER BY observed_at DESC, id DESC", captured["sql"])
        self.assertIn("2026-07-20", tuple(str(value) for value in captured["params"]))
        self.assertEqual(frame.iloc[0]["value"], 37.1)

    def test_as_known_before_first_capture_returns_typed_empty_frame(self) -> None:
        from finance.loaders.sentiment import PIT_COLUMNS, load_market_sentiment_as_known

        frame = load_market_sentiment_as_known(
            known_at="2026-07-19T23:00:00Z",
            query_fn=lambda *_: [],
        )
        self.assertTrue(frame.empty)
        self.assertEqual(list(frame.columns), PIT_COLUMNS)

    def test_as_known_defensively_excludes_revision_after_cutoff(self) -> None:
        from finance.loaders.sentiment import load_market_sentiment_as_known

        rows = [
            {
                **sentiment_row(37.0),
                "id": 1,
                "batch_id": "early",
                "collection_id": "c1",
                "observed_at": "2026-07-20 00:30:00",
            },
            {
                **sentiment_row(42.0),
                "id": 2,
                "batch_id": "late",
                "collection_id": "c2",
                "observed_at": "2026-07-20 02:00:00",
            },
        ]
        frame = load_market_sentiment_as_known(
            known_at="2026-07-20T01:00:00Z",
            query_fn=lambda *_: rows,
        )
        self.assertEqual(frame["batch_id"].tolist(), ["early"])
        self.assertEqual(frame["value"].tolist(), [37.0])

    def test_capture_summary_groups_sources(self) -> None:
        from finance.loaders.sentiment import load_market_sentiment_capture_summary

        summary = load_market_sentiment_capture_summary(
            query_fn=lambda *_: [
                {
                    "source": "cnn_fear_greed",
                    "pit_start_at": "2026-07-20 01:00:00",
                    "latest_capture_at": "2026-07-21 01:00:00",
                    "capture_count": 2,
                }
            ]
        )
        self.assertEqual(summary["cnn_fear_greed"]["capture_count"], 2)


if __name__ == "__main__":
    unittest.main()
