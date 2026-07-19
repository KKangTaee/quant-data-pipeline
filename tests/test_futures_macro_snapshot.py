from __future__ import annotations

import json
import unittest
from datetime import date
from unittest.mock import patch

import pandas as pd


def _compatible_row(*, source_marker: str) -> dict[str, object]:
    return {
        "snapshot_key": "overview_current",
        "source_marker": source_marker,
        "as_of_date": "2026-07-17",
        "schema_version": "futures_macro_snapshot_v1",
        "algorithm_version": "pattern_outlook_v4_conservative_status_10y",
        "status": "READY",
        "snapshot_json": json.dumps(
            {
                "schema_version": "futures_macro_snapshot_v1",
                "source_marker": source_marker,
                "materialized_at": "2026-07-19 10:00:00",
                "macro": {"coverage": {"latest_daily_date": "2026-07-17"}},
                "pattern_outlook": {"horizons": []},
            }
        ),
        "materialized_at": "2026-07-19 10:00:00",
    }


def _minimal_macro() -> dict[str, object]:
    return {
        "status": "OK",
        "coverage": {"latest_daily_date": "2026-07-18"},
        "scores": pd.DataFrame([{"Score": "Risk On", "Value": 1.2}]),
        "score_components": pd.DataFrame(
            [{"Symbol": "ES=F", "Contribution": 0.4}]
        ),
        "symbols": pd.DataFrame([{"Symbol": "ES=F", "1D %": 0.2}]),
        "pattern_feature_frame": pd.DataFrame({"x": [1.0]}),
    }


def _minimal_outlook() -> dict[str, object]:
    return {
        "schema_version": "futures_macro_pattern_outlook_v1",
        "status": "READY",
        "as_of_date": "2026-07-18",
        "horizons": [],
    }


class FuturesMacroSnapshotPersistenceTests(unittest.TestCase):
    def test_schema_has_versioned_marker_and_unique_current_key(self) -> None:
        from finance.data.db.schema import FUTURES_MARKET_SCHEMAS

        schema = FUTURES_MARKET_SCHEMAS["futures_macro_snapshot"]

        self.assertIn("source_marker", schema)
        self.assertIn("schema_version", schema)
        self.assertIn("algorithm_version", schema)
        self.assertIn("snapshot_json LONGTEXT", schema)
        self.assertIn("UNIQUE KEY uk_futures_macro_snapshot_key", schema)

    def test_loader_returns_latest_row_without_calculation(self) -> None:
        from finance.loaders.futures_macro_snapshot import (
            load_latest_futures_macro_snapshot,
        )

        captured: dict[str, object] = {}

        def query(db_name, sql, params):
            captured.update(db_name=db_name, sql=sql, params=params)
            return [
                {
                    "snapshot_key": "overview_current",
                    "source_marker": "2026-07-17 00:00:00",
                }
            ]

        row = load_latest_futures_macro_snapshot(query_fn=query)

        self.assertIsNotNone(row)
        self.assertEqual(row["snapshot_key"], "overview_current")
        self.assertEqual(captured["db_name"], "finance_meta")
        self.assertNotIn("futures_ohlcv", str(captured["sql"]))


class FuturesMacroSnapshotServiceTests(unittest.TestCase):
    def test_compact_payload_turns_dataframes_into_json_records(self) -> None:
        from app.services.futures_macro_snapshot import (
            build_compact_futures_macro_payload,
        )

        payload = build_compact_futures_macro_payload(
            _minimal_macro(),
            _minimal_outlook(),
            source_marker="2026-07-17 00:00:00",
            materialized_at="2026-07-19 10:00:00",
        )

        self.assertEqual(payload["macro"]["scores"][0]["Score"], "Risk On")
        self.assertNotIn("pattern_feature_frame", payload["macro"])
        json.dumps(payload, ensure_ascii=False, allow_nan=False)

    def test_compact_payload_normalizes_dates_and_non_finite_values(self) -> None:
        from app.services.futures_macro_snapshot import (
            build_compact_futures_macro_payload,
        )

        macro = _minimal_macro()
        macro["as_of_date"] = date(2026, 7, 17)
        macro["coverage"] = {"latest_daily_date": date(2026, 7, 17)}
        macro["scores"] = pd.DataFrame([{"Score": "Risk On", "Value": float("nan")}])

        payload = build_compact_futures_macro_payload(
            macro,
            _minimal_outlook(),
            source_marker="2026-07-17 00:00:00",
            materialized_at="2026-07-19 10:00:00",
        )

        self.assertEqual(payload["macro"]["as_of_date"], "2026-07-17")
        self.assertIsNone(payload["macro"]["scores"][0]["Value"])
        json.dumps(payload, ensure_ascii=False, allow_nan=False)

    def test_same_marker_and_versions_reuse_existing_snapshot(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-17 00:00:00",
            load_fn=lambda: _compatible_row(
                source_marker="2026-07-17 00:00:00"
            ),
            macro_builder=lambda: self.fail("macro calculation must be skipped"),
            outlook_builder=lambda: self.fail(
                "outlook calculation must be skipped"
            ),
            write_fn=lambda row: self.fail("write must be skipped"),
        )

        self.assertEqual(result["status"], "reused")

    def test_new_marker_calculates_and_writes_once(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        written: list[dict[str, object]] = []
        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-18 00:00:00",
            load_fn=lambda: _compatible_row(
                source_marker="2026-07-17 00:00:00"
            ),
            macro_builder=_minimal_macro,
            outlook_builder=_minimal_outlook,
            write_fn=lambda row: written.append(row) or 1,
            now_fn=lambda: "2026-07-19 10:00:00",
        )

        self.assertEqual(result["status"], "materialized")
        self.assertEqual(len(written), 1)
        self.assertEqual(written[0]["source_marker"], "2026-07-18 00:00:00")

    def test_compatible_materialized_snapshot_loads_without_builders(self) -> None:
        from app.services.futures_macro_snapshot import (
            load_overview_futures_macro_materialized_snapshot,
        )

        result = load_overview_futures_macro_materialized_snapshot(
            load_fn=lambda: _compatible_row(
                source_marker="2026-07-17 00:00:00"
            )
        )

        self.assertEqual(result["status"], "READY")
        self.assertEqual(
            result["metadata"]["source_marker"], "2026-07-17 00:00:00"
        )

    def test_default_materializer_builds_ten_year_outlook(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        with patch(
            "app.services.futures_macro_snapshot.load_overview_futures_macro_pattern_outlook",
            return_value=_minimal_outlook(),
        ) as outlook_builder:
            materialize_overview_futures_macro_snapshot(
                marker_fn=lambda: "2026-07-18 00:00:00",
                load_fn=lambda: None,
                macro_builder=_minimal_macro,
                write_fn=lambda row: 1,
                now_fn=lambda: "2026-07-19 10:00:00",
            )

        outlook_builder.assert_called_once_with(
            years=10,
            force_refresh=True,
            cache_ttl_seconds=0,
        )


class FuturesMacroSnapshotIngestionTests(unittest.TestCase):
    def test_non_daily_ingestion_skips_materialization(self) -> None:
        from app.jobs.ingestion_jobs import attach_futures_macro_materialization

        result = {"status": "success", "message": "ok", "details": {}}
        attached = attach_futures_macro_materialization(
            result,
            interval="1m",
            rows_written=10,
            materialize_fn=lambda: self.fail("must not materialize intraday"),
        )

        self.assertNotIn("futures_macro_snapshot", attached["details"])

    def test_daily_ingestion_attaches_materialization_result(self) -> None:
        from app.jobs.ingestion_jobs import attach_futures_macro_materialization

        result = {"status": "success", "message": "ok", "details": {}}
        attached = attach_futures_macro_materialization(
            result,
            interval="1d",
            rows_written=10,
            materialize_fn=lambda: {
                "status": "materialized",
                "source_marker": "2026-07-18 00:00:00",
            },
        )

        self.assertEqual(
            attached["details"]["futures_macro_snapshot"]["status"],
            "materialized",
        )
        self.assertEqual(attached["status"], "success")

    def test_daily_materialization_failure_is_partial_success(self) -> None:
        from app.jobs.ingestion_jobs import attach_futures_macro_materialization

        result = {"status": "success", "message": "collected", "details": {}}

        def fail():
            raise RuntimeError("snapshot failed")

        attached = attach_futures_macro_materialization(
            result,
            interval="1d",
            rows_written=10,
            materialize_fn=fail,
        )

        self.assertEqual(attached["status"], "partial_success")
        self.assertIn("snapshot failed", attached["message"])


if __name__ == "__main__":
    unittest.main()
