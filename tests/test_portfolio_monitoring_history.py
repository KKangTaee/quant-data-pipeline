from __future__ import annotations

import importlib
import unittest
from datetime import date, datetime


def _history():
    try:
        return importlib.import_module("app.services.portfolio_monitoring.history")
    except ModuleNotFoundError as exc:
        raise AssertionError("portfolio monitoring history module is required") from exc


class FakeHistoryRepository:
    def __init__(self):
        self.rows = {}

    def insert_snapshot_if_absent(self, identity, payload):
        inserted = identity not in self.rows
        self.rows.setdefault(identity, dict(payload))
        return {**self.rows[identity], "inserted": inserted}

    def list_snapshots(self, group_id, start_date, end_date):
        return [
            row for identity, row in self.rows.items()
            if identity[0] == group_id and start_date <= identity[1] <= end_date
        ]


class RecordingDb:
    def __init__(self):
        self.used_databases = []
        self.queries = []
        self.closed = False

    def use_db(self, name):
        self.used_databases.append(name)

    def query(self, sql, params=None):
        self.queries.append((sql, list(params or [])))
        return []

    def close(self):
        self.closed = True


def _workspace():
    return {
        "schema_version": "portfolio_monitoring_workspace_v1",
        "generated_at": "2026-07-19T12:00:00",
        "config_fingerprint": "a" * 64,
        "active_group": {
            "curve": [{"date": "2026-07-18", "total_value": 110}],
            "metrics": {"total_return": 0.1, "mdd": -0.05},
        },
        "diagnosis": {
            "policy_version": "portfolio_monitoring_policy_v1",
            "all_rows": [{
                "rule_id": "trend:a", "classification": "weakness", "severity": "WATCH",
                "confidence": "HIGH", "measured_fact": "63D -10%", "threshold": "watch -10%",
                "change_condition": "63D > -10%", "source_dates": ["2026-07-18"],
            }],
        },
        "macro_observation": {
            "version": "portfolio_monitoring_macro_context_v1",
            "rows": [{"rule_id": "macro_tech_risk_off", "state": "medium", "severity": "MEDIUM", "confidence": "MEDIUM", "source_dates": ["2026-07-18"]}],
        },
        "source_health": {"as_of_dates": {"futures_macro": "2026-07-18"}, "publication": "READY"},
        "catalog": {"items": [{"raw": "must not persist"}]},
    }


class PortfolioMonitoringHistoryTests(unittest.TestCase):
    def test_schema_defines_snapshot_and_calibration_identity(self) -> None:
        from finance.data.db.schema import PORTFOLIO_MONITORING_SCHEMAS

        snapshot = PORTFOLIO_MONITORING_SCHEMAS["monitoring_diagnosis_snapshot"]
        artifact = PORTFOLIO_MONITORING_SCHEMAS["monitoring_risk_calibration_artifact"]
        self.assertIn("config_fingerprint", snapshot)
        self.assertIn("policy_version", snapshot)
        self.assertIn("UNIQUE KEY uk_monitoring_diagnosis_identity", snapshot)
        self.assertIn("data_fingerprint", artifact)
        normalized = " ".join(artifact.split())
        self.assertIn(
            "(algorithm_version, data_fingerprint, config_fingerprint, policy_version, horizon_sessions)",
            normalized,
        )
        self.assertIn("publication_status", artifact)

    def test_latest_calibration_artifact_is_scoped_to_current_config_and_policy(self) -> None:
        history = _history()
        db = RecordingDb()
        repository = history.MySQLMonitoringHistoryRepository(lambda: db)

        result = repository.load_latest_calibration_artifact(
            config_fingerprint="a" * 64,
            policy_version="portfolio_monitoring_policy_v1",
        )

        self.assertIsNone(result)
        self.assertEqual(db.used_databases, ["finance_meta"])
        sql, params = db.queries[0]
        self.assertIn("WHERE config_fingerprint=%s AND policy_version=%s", " ".join(sql.split()))
        self.assertEqual(params, ["a" * 64, "portfolio_monitoring_policy_v1"])
        self.assertTrue(db.closed)

    def test_capture_is_idempotent_and_compact_with_immutable_as_of_inputs(self) -> None:
        history = _history()
        repository = FakeHistoryRepository()

        first = history.capture_diagnosis_snapshot("group", date(2026, 7, 18), _workspace(), repository)
        second = history.capture_diagnosis_snapshot("group", date(2026, 7, 18), _workspace(), repository)

        self.assertTrue(first.inserted)
        self.assertFalse(second.inserted)
        self.assertEqual(len(repository.rows), 1)
        payload = next(iter(repository.rows.values()))
        self.assertEqual(payload["config_fingerprint"], "a" * 64)
        self.assertEqual(payload["policy_version"], "portfolio_monitoring_policy_v1")
        self.assertEqual(payload["macro_version"], "portfolio_monitoring_macro_context_v1")
        self.assertEqual(payload["source_dates"]["futures_macro"], "2026-07-18")
        self.assertIsNone(payload["outcome_21"])
        self.assertIsNone(payload["outcome_63"])
        serialized = str(payload).lower()
        self.assertNotIn("curve", serialized)
        self.assertNotIn("catalog", serialized)
        self.assertNotIn("total_value", serialized)

    def test_capture_rejects_future_source_dates_and_invalid_fingerprint(self) -> None:
        history = _history()
        workspace = _workspace()
        workspace["source_health"]["as_of_dates"]["futures_macro"] = "2026-07-19"
        with self.assertRaises(ValueError):
            history.capture_diagnosis_snapshot("group", date(2026, 7, 18), workspace, FakeHistoryRepository())
        workspace = _workspace()
        workspace["config_fingerprint"] = "short"
        with self.assertRaises(ValueError):
            history.capture_diagnosis_snapshot("group", date(2026, 7, 18), workspace, FakeHistoryRepository())

    def test_load_history_preserves_publication_and_subsequent_outcomes(self) -> None:
        history = _history()
        repository = FakeHistoryRepository()
        history.capture_diagnosis_snapshot("group", date(2026, 7, 18), _workspace(), repository)
        identity = next(iter(repository.rows))
        repository.rows[identity].update(
            publication_time="2026-07-19T12:00:00", outcome_21=-0.08, outcome_63=-0.14,
            outcome_measured_at="2026-10-16", outcome_status="complete",
        )

        rows = history.load_diagnosis_history("group", date(2026, 7, 1), date(2026, 10, 31), repository=repository)

        self.assertEqual(len(rows), 1)
        self.assertEqual(rows[0]["as_of_date"], "2026-07-18")
        self.assertEqual(rows[0]["outcome_21"], -0.08)
        self.assertEqual(rows[0]["outcome_63"], -0.14)
        self.assertEqual(rows[0]["publication_time"], "2026-07-19T12:00:00")


if __name__ == "__main__":
    unittest.main()
