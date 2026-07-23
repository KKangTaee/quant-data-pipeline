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
        "schema_version": "futures_macro_snapshot_v2",
        "algorithm_version": "pattern_outlook_v5_same_state_nested_hybrid",
        "input_fingerprint": "a" * 64,
        "session_status": "FINAL",
        "status": "READY",
        "snapshot_json": json.dumps(
            {
                "schema_version": "futures_macro_snapshot_v2",
                "source_marker": source_marker,
                "materialized_at": "2026-07-19 10:00:00",
                "macro": {"coverage": {"latest_daily_date": "2026-07-17"}},
                "pattern_outlook": {"horizons": []},
            }
        ),
        "materialized_at": "2026-07-19 10:00:00",
    }


def _compatible_pending_row(*, source_marker: str) -> dict[str, object]:
    row = _compatible_row(source_marker=source_marker)
    payload = json.loads(str(row["snapshot_json"]))
    payload["pattern_outlook"]["session"] = {
        "status": "PENDING_SESSION_FINALIZATION",
        "latest_final_session": "2026-07-17",
        "pending_session": "2026-07-20",
    }
    row["snapshot_json"] = json.dumps(payload)
    return row


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
        "schema_version": "futures_macro_pattern_outlook_v2",
        "status": "READY",
        "as_of_date": "2026-07-18",
        "input_fingerprint": "b" * 64,
        "session": {"status": "OBSERVED", "latest_final_session": "2026-07-18"},
        "method": {"selected_candidates": {"5": "M1_MOMENTUM", "20": None}},
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
        self.assertIn("input_fingerprint CHAR(64)", schema)
        self.assertIn("session_status VARCHAR(32)", schema)
        self.assertIn("UNIQUE KEY uk_futures_macro_snapshot_key", schema)

        history = FUTURES_MARKET_SCHEMAS["futures_macro_forecast_history"]
        self.assertIn("forecast_identity CHAR(64)", history)
        self.assertIn("selected_models_json LONGTEXT", history)
        self.assertIn("UNIQUE KEY uk_futures_macro_forecast_identity", history)

    def test_input_fingerprint_is_deterministic_for_canonical_evidence(self) -> None:
        from app.services.futures_macro_snapshot import (
            compute_futures_macro_input_fingerprint,
        )

        left = {
            "resolver_version": "v1",
            "daily_rows": [
                {"symbol": "NQ=F", "close": 2.0},
                {"symbol": "ES=F", "close": 1.0},
            ],
            "event_keys": ["cpi", "fomc"],
        }
        right = {
            "event_keys": ["fomc", "cpi"],
            "daily_rows": [
                {"close": 1.0, "symbol": "ES=F"},
                {"close": 2.0, "symbol": "NQ=F"},
            ],
            "resolver_version": "v1",
        }

        self.assertEqual(
            compute_futures_macro_input_fingerprint(left),
            compute_futures_macro_input_fingerprint(right),
        )

    def test_bundle_persistence_is_idempotent_and_transactional(self) -> None:
        from finance.data.futures_macro_snapshot import (
            persist_futures_macro_snapshot_bundle,
        )

        class Connection:
            def __init__(self, fail_on: int | None = None):
                self.calls: list[str] = []
                self.fail_on = fail_on

            def begin(self): self.calls.append("begin")
            def commit(self): self.calls.append("commit")
            def rollback(self): self.calls.append("rollback")
            def executemany(self, sql, rows):
                self.calls.append(sql)
                if self.fail_on == len([item for item in self.calls if "INSERT" in item]):
                    raise RuntimeError("write failed")

        current = {
            "snapshot_key": "overview_current",
            "source_marker": "2026-07-18",
            "as_of_date": "2026-07-18",
            "input_fingerprint": "a" * 64,
            "schema_version": "futures_macro_snapshot_v2",
            "algorithm_version": "algo",
            "session_status": "FINAL",
            "status": "READY",
            "snapshot_json": "{}",
            "materialized_at": "2026-07-20 10:00:00",
        }
        history = {
            "forecast_identity": "b" * 64,
            "as_of_date": "2026-07-18",
            "source_marker": "2026-07-18",
            "input_fingerprint": "a" * 64,
            "schema_version": "futures_macro_snapshot_v2",
            "feature_schema_version": "state_v2",
            "algorithm_version": "algo",
            "selected_models_json": "{}",
            "status_json": "{}",
            "forecast_json": "{}",
            "known_at": "2026-07-20 10:00:00",
            "materialized_at": "2026-07-20 10:00:00",
        }
        connection = Connection()

        result = persist_futures_macro_snapshot_bundle(
            current,
            history,
            connection=connection,
        )

        self.assertEqual(result, {"history_rows": 1, "current_rows": 1})
        self.assertEqual(connection.calls[0], "begin")
        self.assertEqual(connection.calls[-1], "commit")
        sql = "\n".join(connection.calls)
        self.assertIn("ON DUPLICATE KEY UPDATE forecast_identity = forecast_identity", sql)
        self.assertIn("VALUES(as_of_date) >= as_of_date", sql)
        self.assertIn("session_status = 'LEGACY'", sql)

        failing = Connection(fail_on=2)
        with self.assertRaisesRegex(RuntimeError, "write failed"):
            persist_futures_macro_snapshot_bundle(current, history, connection=failing)
        self.assertEqual(failing.calls[-1], "rollback")

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

    def test_loader_falls_back_to_legacy_columns_before_schema_migration(self) -> None:
        from finance.loaders.futures_macro_snapshot import (
            load_latest_futures_macro_snapshot,
        )

        calls: list[str] = []

        def query(_db_name, sql, _params):
            calls.append(sql)
            if "input_fingerprint" in sql:
                raise RuntimeError("Unknown column 'input_fingerprint' in 'field list'")
            return [{"snapshot_key": "overview_current", "schema_version": "legacy"}]

        row = load_latest_futures_macro_snapshot(query_fn=query)

        self.assertEqual(row["schema_version"], "legacy")
        self.assertEqual(row["input_fingerprint"], "")
        self.assertEqual(row["session_status"], "LEGACY")
        self.assertEqual(len(calls), 2)

    def test_history_loader_reads_immutable_rows_without_calculation(self) -> None:
        from finance.loaders.futures_macro_snapshot import (
            load_futures_macro_forecast_history,
        )

        captured: dict[str, object] = {}

        def query(db_name, sql, params):
            captured.update(db_name=db_name, sql=sql, params=params)
            return [{"forecast_identity": "f" * 64, "as_of_date": "2026-07-18"}]

        rows = load_futures_macro_forecast_history(
            as_of_date="2026-07-18",
            query_fn=query,
        )

        self.assertEqual(rows[0]["forecast_identity"], "f" * 64)
        self.assertIn("futures_macro_forecast_history", str(captured["sql"]))
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

    def test_same_input_fingerprint_reuses_existing_snapshot_even_if_raw_marker_moves(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-20 00:00:00",
            load_fn=lambda: _compatible_row(
                source_marker="2026-07-17 00:00:00"
            ),
            macro_builder=_minimal_macro,
            outlook_builder=lambda: {
                **_minimal_outlook(),
                "input_fingerprint": "a" * 64,
                "as_of_date": "2026-07-17",
            },
            write_fn=lambda row: self.fail("write must be skipped"),
        )

        self.assertEqual(result["status"], "reused")

    def test_pending_session_reuses_latest_good_current(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-20 00:00:00",
            load_fn=lambda: _compatible_pending_row(source_marker="2026-07-17 00:00:00"),
            macro_builder=_minimal_macro,
            outlook_builder=lambda: {
                **_minimal_outlook(),
                "input_fingerprint": "a" * 64,
                "as_of_date": "2026-07-17",
                "session": {
                    "status": "PENDING_SESSION_FINALIZATION",
                    "latest_final_session": "2026-07-17",
                    "pending_session": "2026-07-20",
                },
            },
            write_fn=lambda *_args: self.fail("pending snapshot must not overwrite current"),
        )

        self.assertEqual(result["status"], "reused_pending")
        self.assertEqual(result["as_of_date"], "2026-07-17")

    def test_pending_session_refreshes_stored_evidence_when_forecast_input_is_same(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        written: list[dict[str, object]] = []
        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-20 00:00:00",
            load_fn=lambda: _compatible_row(source_marker="2026-07-17 00:00:00"),
            macro_builder=_minimal_macro,
            outlook_builder=lambda: {
                **_minimal_outlook(),
                "input_fingerprint": "a" * 64,
                "as_of_date": "2026-07-17",
                "session": {
                    "status": "PENDING_SESSION_FINALIZATION",
                    "latest_final_session": "2026-07-17",
                    "pending_session": "2026-07-20",
                },
            },
            write_fn=lambda current, history: written.append(
                {"current": current, "history": history}
            ),
            now_fn=lambda: "2026-07-20 14:00:00",
        )

        self.assertEqual(result["status"], "materialized_pending_evidence")
        self.assertEqual(len(written), 1)
        payload = json.loads(str(written[0]["current"]["snapshot_json"]))
        self.assertEqual(
            payload["pattern_outlook"]["session"]["pending_session"],
            "2026-07-20",
        )

    def test_pending_session_materializes_newly_completed_base_when_fingerprint_moves(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        written: list[dict[str, object]] = []
        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-21 00:00:00",
            load_fn=lambda: _compatible_row(source_marker="2026-07-20 00:00:00"),
            macro_builder=lambda: {
                **_minimal_macro(),
                "coverage": {"latest_daily_date": "2026-07-20"},
            },
            outlook_builder=lambda: {
                **_minimal_outlook(),
                "as_of_date": "2026-07-20",
                "input_fingerprint": "b" * 64,
                "session": {
                    "status": "PENDING_SESSION_FINALIZATION",
                    "latest_final_session": "2026-07-20",
                    "pending_session": "2026-07-21",
                },
            },
            write_fn=lambda current, history: written.append(
                {"current": current, "history": history}
            ),
            now_fn=lambda: "2026-07-21 14:00:00",
        )

        self.assertEqual(result["status"], "materialized_pending_base")
        self.assertEqual(result["as_of_date"], "2026-07-20")
        self.assertEqual(len(written), 1)

    def test_pending_session_replaces_incompatible_legacy_with_completed_base(self) -> None:
        from app.services.futures_macro_snapshot import (
            materialize_overview_futures_macro_snapshot,
        )

        written: list[dict[str, object]] = []
        result = materialize_overview_futures_macro_snapshot(
            marker_fn=lambda: "2026-07-20 00:00:00",
            load_fn=lambda: {
                **_compatible_row(source_marker="2026-07-20 00:00:00"),
                "as_of_date": "2026-07-20",
                "schema_version": "futures_macro_snapshot_v1",
                "algorithm_version": "pattern_outlook_v4",
                "session_status": "LEGACY",
            },
            macro_builder=lambda: {
                **_minimal_macro(),
                "coverage": {"latest_daily_date": "2026-07-17"},
            },
            outlook_builder=lambda: {
                **_minimal_outlook(),
                "as_of_date": "2026-07-17",
                "session": {
                    "status": "PENDING_SESSION_FINALIZATION",
                    "latest_final_session": "2026-07-17",
                    "pending_session": "2026-07-20",
                },
            },
            write_fn=lambda current, history: written.append(
                {"current": current, "history": history}
            ),
            now_fn=lambda: "2026-07-20 14:00:00",
        )

        self.assertEqual(result["status"], "materialized_pending_base")
        self.assertEqual(result["as_of_date"], "2026-07-17")
        self.assertEqual(len(written), 1)
        self.assertEqual(written[0]["current"]["session_status"], "FINAL")

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
            write_fn=lambda current, history: written.append(
                {"current": current, "history": history}
            ) or 1,
            now_fn=lambda: "2026-07-19 10:00:00",
        )

        self.assertEqual(result["status"], "materialized")
        self.assertEqual(len(written), 1)
        self.assertEqual(written[0]["current"]["source_marker"], "2026-07-18 00:00:00")
        self.assertEqual(len(written[0]["history"]["forecast_identity"]), 64)

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
                write_fn=lambda current, history: 1,
                now_fn=lambda: "2026-07-19 10:00:00",
            )

        outlook_builder.assert_called_once_with(
            years=10,
            force_refresh=True,
            cache_ttl_seconds=0,
            evaluation_time=unittest.mock.ANY,
        )


class FuturesMacroSnapshotIngestionTests(unittest.TestCase):
    def test_daily_collection_can_defer_materialization_for_grouped_refresh(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_futures_ohlcv

        collected = {
            "source": "yfinance",
            "period": "1y",
            "interval": "1d",
            "cadence_mode": "manual_macro_daily_routine",
            "rows_written": 250,
            "symbols_requested": 1,
            "symbols_processed": 1,
            "failed_symbols": [],
            "latest_candle_time_utc": "2026-07-22 00:00:00",
            "run_id": "run-1",
            "diagnostics": {},
        }
        with (
            patch(
                "app.jobs.ingestion_jobs.collect_and_store_futures_ohlcv",
                return_value=collected,
            ),
            patch(
                "app.jobs.ingestion_jobs.attach_futures_macro_materialization"
            ) as attach,
        ):
            result = run_collect_futures_ohlcv(
                symbols=["ES=F"],
                period="1y",
                interval="1d",
                materialize_snapshot=False,
            )

        attach.assert_not_called()
        self.assertEqual(result["status"], "success")
        self.assertNotIn("futures_macro_snapshot", result["details"])

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
