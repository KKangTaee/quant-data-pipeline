from __future__ import annotations

import importlib
import importlib.util
from datetime import date
from unittest.mock import patch

import pandas as pd

from finance.economic_cycle_model import PHASES, fit_horizon_model


def _load_module():
    spec = importlib.util.find_spec("finance.data.economic_cycle_results")
    assert spec is not None, "economic cycle result persistence module must exist"
    return importlib.import_module("finance.data.economic_cycle_results")


def _cluster_fixture() -> tuple[pd.DataFrame, pd.Series]:
    feature_names = (
        "activity_score",
        "labor_income_score",
        "activity_momentum_3m",
        "labor_income_momentum_3m",
    )
    centers = {
        "recovery": (-1.0, -1.0, 1.0, 1.0),
        "expansion": (1.0, 1.0, 1.0, 1.0),
        "slowdown": (1.0, 1.0, -1.0, -1.0),
        "recession": (-1.0, -1.0, -1.0, -1.0),
    }
    rows = [
        dict(zip(feature_names, center, strict=True))
        for center in centers.values()
        for _ in range(2)
    ]
    labels = pd.Series([phase for phase in centers for _ in range(2)])
    return pd.DataFrame(rows), labels


def test_economic_cycle_result_schemas_lock_business_keys_and_indexes() -> None:
    from finance.data.db.schema import ECONOMIC_CYCLE_SCHEMAS

    artifact_sql = " ".join(
        ECONOMIC_CYCLE_SCHEMAS["economic_cycle_model_artifact"].split()
    )
    snapshot_sql = " ".join(
        ECONOMIC_CYCLE_SCHEMAS["economic_cycle_snapshot"].split()
    )

    assert (
        "UNIQUE KEY uk_cycle_model_trained (model_version, trained_through)"
        in artifact_sql
    )
    assert "publication_status_json" in artifact_sql
    assert (
        "UNIQUE KEY uk_cycle_snapshot (as_of_date, model_version, run_kind)"
        in snapshot_sql
    )
    assert "KEY ix_cycle_snapshot_date_status (as_of_date, status)" in snapshot_sql
    assert "nber_recession" in snapshot_sql
    assert "'intramonth_nowcast'" in snapshot_sql
    assert "baseline_as_of_date DATE NULL" in snapshot_sql
    assert "source_collected_at DATETIME NULL" in snapshot_sql
    assert "source_coverage_json LONGTEXT NULL" in snapshot_sql


def test_model_artifact_and_snapshot_serializers_round_trip_vocabularies() -> None:
    module = _load_module()
    features, labels = _cluster_fixture()
    artifact = fit_horizon_model(features, labels, horizon_months=0)
    encoded_artifact = module.serialize_horizon_model_artifact(artifact)

    assert module.deserialize_horizon_model_artifact(encoded_artifact) == artifact

    snapshot = module.CycleSnapshot(
        as_of_date=date(2026, 6, 30),
        model_version="cycle-v1",
        status="LIMITED",
        horizons=(
            module.HorizonProbability(
                horizon_months=0,
                probabilities={phase: 0.25 for phase in PHASES},
                dominant_phase="expansion",
                confidence=0.25,
                publication_status="READY",
            ),
            module.HorizonProbability(
                horizon_months=1,
                probabilities=None,
                dominant_phase=None,
                confidence=None,
                publication_status="LIMITED",
                reason="VALIDATION_FAILED",
            ),
        ),
        factor_contributions=({"factor": "activity", "value": 0.4},),
        top_evidence=({"series_id": "INDPRO", "direction": "strengthening"},),
        warnings=("1개월 전망은 제한적입니다.",),
        expected_transition="expansion_to_slowdown",
    )
    payload = module.serialize_cycle_snapshot(snapshot)

    assert module.deserialize_cycle_snapshot(payload) == snapshot


def test_cycle_history_known_at_excludes_later_or_unsafe_replay_rows() -> None:
    from finance.loaders.economic_cycle import load_cycle_history

    rows = [
        {
            "as_of_date": "2026-06-30",
            "data_cutoff_date": "2026-06-30",
            "run_kind": "historical_replay",
        },
        {
            "as_of_date": "2026-07-31",
            "data_cutoff_date": "2026-07-31",
            "run_kind": "historical_replay",
        },
        {
            "as_of_date": "2026-06-15",
            "data_cutoff_date": "2026-06-20",
            "run_kind": "historical_replay",
        },
    ]

    loaded = load_cycle_history(
        start_date="2026-06-01",
        end_date="2026-07-31",
        known_at_date="2026-07-20",
        query_fn=lambda *_args: rows,
    )

    assert [row["as_of_date"] for row in loaded] == ["2026-06-30"]


def test_result_upserts_reuse_artifact_and_snapshot_business_keys() -> None:
    module = _load_module()

    class Connection:
        def __init__(self) -> None:
            self.artifacts: dict[tuple[object, ...], dict[str, object]] = {}
            self.snapshots: dict[tuple[object, ...], dict[str, object]] = {}
            self.sql: list[str] = []

        def executemany(self, sql: str, rows: list[dict[str, object]]) -> None:
            self.sql.append(sql)
            for row in rows:
                if "economic_cycle_model_artifact" in sql:
                    key = (row["model_version"], row["trained_through"])
                    self.artifacts[key] = dict(row)
                else:
                    key = (row["as_of_date"], row["model_version"], row["run_kind"])
                    self.snapshots[key] = dict(row)

    connection = Connection()
    artifact_row = {
        "model_version": "cycle-v1",
        "trained_through": "2026-05-31",
        "feature_schema_version": "features-v1",
        "parameters_json": "{}",
        "validation_metrics_json": "{}",
        "publication_status": "READY",
        "publication_status_json": '{"0":"READY"}',
    }
    snapshot_row = {
        "as_of_date": "2026-06-30",
        "model_version": "cycle-v1",
        "run_kind": "current",
        "training_cutoff_date": "2026-05-31",
        "data_cutoff_date": "2026-06-30",
        "status": "READY",
        "current_phase": "expansion",
        "expected_transition": "expansion_to_slowdown",
        "nber_recession": 0,
        "probabilities_json": "{}",
        "forecast_path_json": "[]",
        "factor_contributions_json": "[]",
        "top_evidence_json": "[]",
        "warnings_json": "[]",
    }

    module.upsert_cycle_model_artifact(artifact_row, connection=connection)
    module.upsert_cycle_model_artifact(artifact_row, connection=connection)
    module.upsert_cycle_snapshots([snapshot_row], connection=connection)
    module.upsert_cycle_snapshots([snapshot_row], connection=connection)

    assert len(connection.artifacts) == 1
    assert len(connection.snapshots) == 1
    assert all("ON DUPLICATE KEY UPDATE" in sql for sql in connection.sql)
    stored_snapshot = next(iter(connection.snapshots.values()))
    assert stored_snapshot["baseline_as_of_date"] is None
    assert stored_snapshot["source_collected_at"] is None
    assert stored_snapshot["source_coverage_json"] is None


def test_exact_artifact_loader_accepts_limited_artifact() -> None:
    loader = importlib.import_module("finance.loaders.economic_cycle")
    captured: list[tuple[str, str, tuple[object, ...]]] = []

    def query(database: str, sql: str, params: tuple[object, ...]):
        captured.append((database, sql, params))
        return [
            {
                "model_version": "cycle-limited",
                "trained_through": "2026-05-31",
                "publication_status": "LIMITED",
            }
        ]

    artifact = loader.load_cycle_model_artifact(
        "cycle-limited",
        trained_through="2026-05-31",
        query_fn=query,
    )

    assert artifact is not None
    assert artifact["model_version"] == "cycle-limited"
    assert artifact["publication_status"] == "LIMITED"
    assert "publication_status = 'READY'" not in captured[0][1]
    assert captured[0][2] == ("cycle-limited", "2026-05-31")


def test_cycle_snapshot_loader_accepts_intramonth_run_kind() -> None:
    loader = importlib.import_module("finance.loaders.economic_cycle")

    loaded = loader.load_cycle_snapshot(
        as_of_date="2026-07-21",
        run_kind="intramonth_nowcast",
        query_fn=lambda *_args: [
            {
                "as_of_date": "2026-07-21",
                "run_kind": "intramonth_nowcast",
                "model_version": "cycle-limited",
            }
        ],
    )

    assert loaded is not None
    assert loaded["as_of_date"] == "2026-07-21"
    assert loaded["run_kind"] == "intramonth_nowcast"


def test_result_schema_sync_extends_existing_snapshot_run_kind_enum() -> None:
    module = _load_module()

    class Connection:
        def __init__(self) -> None:
            self.executed: list[str] = []

        def use_db(self, _database: str) -> None:
            return None

        def execute(self, sql: str, *_args) -> None:
            self.executed.append(sql)

        def query(self, sql: str, *_args):
            if "information_schema.COLUMNS" in sql and "COLUMN_NAME = 'run_kind'" in sql:
                return [{"COLUMN_TYPE": "enum('historical_replay','current')"}]
            return []

    connection = Connection()
    with patch.object(module, "sync_table_schema"):
        module.ensure_economic_cycle_result_schemas(connection=connection)

    alter = next(
        sql for sql in connection.executed if "MODIFY COLUMN run_kind" in sql
    )
    assert "'intramonth_nowcast'" in alter


def test_result_loaders_choose_approved_artifact_and_bounded_sorted_history() -> None:
    module = _load_module()
    loader = importlib.import_module("finance.loaders.economic_cycle")
    captured: list[tuple[str, str, tuple[object, ...]]] = []

    def artifact_query(database: str, sql: str, params: tuple[object, ...]):
        captured.append((database, sql, params))
        return [
            {
                "model_version": "limited",
                "trained_through": "2026-06-30",
                "publication_status": "LIMITED",
            },
            {
                "model_version": "approved-old",
                "trained_through": "2026-04-30",
                "publication_status": "READY",
            },
            {
                "model_version": "approved-new",
                "trained_through": "2026-05-31",
                "publication_status": "READY",
            },
        ]

    artifact = loader.load_latest_approved_cycle_artifact(
        as_of_date="2026-06-15", query_fn=artifact_query
    )
    assert artifact["model_version"] == "approved-new"
    assert "publication_status = 'READY'" in captured[0][1]

    def history_query(_database: str, _sql: str, _params: tuple[object, ...]):
        return [
            {"as_of_date": "2025-03-31", "status": "READY"},
            {"as_of_date": "2024-12-31", "status": "READY"},
            {"as_of_date": "2025-02-28", "status": "LIMITED"},
            {"as_of_date": "2026-01-31", "status": "READY"},
        ]

    history = loader.load_cycle_history(
        start_date="2025-01-01",
        end_date="2025-12-31",
        query_fn=history_query,
    )
    assert [row["as_of_date"] for row in history] == ["2025-02-28", "2025-03-31"]
