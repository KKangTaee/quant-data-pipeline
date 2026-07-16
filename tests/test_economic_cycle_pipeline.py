from __future__ import annotations

import importlib
import importlib.util
import json
from datetime import date

import pandas as pd
import pytest

from finance.economic_cycle_model import PHASES
from finance.economic_cycle_validation import HorizonValidation, ValidationReport


def _load_module():
    spec = importlib.util.find_spec("finance.economic_cycle_pipeline")
    assert spec is not None, "economic cycle pipeline module must exist"
    return importlib.import_module("finance.economic_cycle_pipeline")


def _panel(periods: int = 32) -> tuple[pd.DataFrame, pd.Series]:
    phases = pd.Series([PHASES[index % 4] for index in range(periods)])
    centers = {
        "recovery": (-1.0, -1.0, 1.0, 1.0),
        "expansion": (1.0, 1.0, 1.0, 1.0),
        "slowdown": (1.0, 1.0, -1.0, -1.0),
        "recession": (-1.0, -1.0, -1.0, -1.0),
    }
    rows = []
    for index, phase in enumerate(phases):
        current = centers[phase]
        rows.append(
            {
                "forecast_origin": pd.Timestamp("2000-01-31")
                + pd.offsets.MonthEnd(index),
                "activity_score": current[0],
                "labor_income_score": current[1],
                "activity_momentum_3m": current[2],
                "labor_income_momentum_3m": current[3],
                "financial_leading_score": float(index % 4),
                "inflation_policy_score": float(index % 3) - 1.0,
                "overall_coverage": 1.0,
            }
        )
    return pd.DataFrame(rows), phases


def _horizon_validation(*, ready: bool = True) -> HorizonValidation:
    return HorizonValidation(
        origin_count=150 if ready else 80,
        metrics={
            "brier_score": 0.20,
            "log_loss": 0.50,
            "accuracy": 0.70,
            "ece": 0.10,
        },
        baseline_metrics={
            "persistence": {"brier_score": 0.25, "log_loss": 0.60},
            "historical_transition": {"brier_score": 0.30, "log_loss": 0.70},
        },
        phase_support={phase: 20 for phase in PHASES},
        recession_episodes=3,
        complete_feature_ratio=0.90,
        probabilities_valid=True,
    )


class TrainingLoader:
    def __init__(self, panel: pd.DataFrame, labels: pd.Series) -> None:
        self.panel = panel
        self.labels = labels

    def load_training_data(self, _trained_through):
        return self.panel, self.labels, self.labels


class Writer:
    def __init__(self) -> None:
        self.artifacts: dict[tuple[object, object], dict[str, object]] = {}
        self.snapshots: dict[tuple[object, object, object], dict[str, object]] = {}

    def upsert_artifact(self, row):
        self.artifacts[(row["model_version"], row["trained_through"])] = dict(row)
        return 1

    def upsert_snapshot(self, row):
        key = (row["as_of_date"], row["model_version"], row["run_kind"])
        self.snapshots[key] = dict(row)
        return 1


def test_training_never_approves_missing_gate_metadata_and_records_partial_status() -> (
    None
):
    module = _load_module()
    panel, labels = _panel()

    missing_writer = Writer()
    missing = module.train_validate_economic_cycle_model(
        trained_through="2002-08-31",
        loader=TrainingLoader(panel, labels),
        writer=missing_writer,
        validator=lambda *_args, **_kwargs: ValidationReport(
            horizons={0: _horizon_validation()}, predictions=()
        ),
    )
    assert missing["publication_status"] == "LIMITED"
    assert all(
        row["publication_status"] != "READY"
        for row in missing_writer.artifacts.values()
    )

    partial_writer = Writer()
    partial = module.train_validate_economic_cycle_model(
        trained_through="2002-08-31",
        loader=TrainingLoader(panel, labels),
        writer=partial_writer,
        validator=lambda *_args, **_kwargs: ValidationReport(
            horizons={
                0: _horizon_validation(),
                1: _horizon_validation(ready=False),
                2: _horizon_validation(ready=False),
            },
            predictions=(),
        ),
    )
    statuses = json.loads(partial["artifact_row"]["publication_status_json"])
    assert partial["publication_status"] == "READY"
    assert statuses["0"]["status"] == "READY"
    assert statuses["1"]["status"] == "LIMITED"
    assert statuses["2"]["status"] == "LIMITED"


def test_materialization_persists_provisional_probabilities_for_limited_horizons() -> (
    None
):
    module = _load_module()
    panel, labels = _panel()
    writer = Writer()
    training = module.train_validate_economic_cycle_model(
        trained_through="2002-07-31",
        loader=TrainingLoader(panel, labels),
        writer=writer,
        validator=lambda *_args, **_kwargs: ValidationReport(
            horizons={
                0: _horizon_validation(),
                1: _horizon_validation(ready=False),
                2: _horizon_validation(ready=False),
            },
            predictions=(),
        ),
    )

    class Loader:
        def load_artifact(self, **_kwargs):
            return training["artifact_row"]

        def load_prediction_data(self, _as_of_date):
            return panel.iloc[-1].to_dict()

    snapshot = module.materialize_economic_cycle_snapshot(
        as_of_date="2002-08-31", loader=Loader(), writer=writer
    )

    assert snapshot.horizons[0].probabilities is not None
    assert snapshot.horizons[0].dominant_phase in PHASES
    assert snapshot.horizons[1].probabilities is not None
    assert snapshot.horizons[1].dominant_phase in PHASES
    assert snapshot.horizons[1].confidence is not None
    assert snapshot.horizons[1].publication_status == "LIMITED"
    assert snapshot.horizons[1].reason is not None
    assert snapshot.horizons[2].probabilities is not None
    assert snapshot.horizons[2].dominant_phase in PHASES
    assert snapshot.horizons[2].confidence is not None
    assert snapshot.horizons[2].publication_status == "LIMITED"
    assert snapshot.warnings


def test_materialization_marks_incomplete_artifact_unavailable_without_aborting() -> (
    None
):
    module = _load_module()
    panel, labels = _panel()
    keep = labels != "recession"
    limited_panel = panel.loc[keep].reset_index(drop=True)
    limited_labels = labels.loc[keep].reset_index(drop=True)
    writer = Writer()
    training = module.train_validate_economic_cycle_model(
        trained_through="2002-07-31",
        loader=TrainingLoader(limited_panel, limited_labels),
        writer=writer,
        validator=lambda *_args, **_kwargs: ValidationReport(
            horizons={
                horizon: _horizon_validation(ready=False)
                for horizon in (0, 1, 2)
            },
            predictions=(),
        ),
    )

    class Loader:
        def load_artifact(self, **_kwargs):
            return training["artifact_row"]

        def load_prediction_data(self, _as_of_date):
            return limited_panel.iloc[-1].to_dict()

    snapshot = module.materialize_economic_cycle_snapshot(
        as_of_date="2002-08-31", loader=Loader(), writer=writer
    )

    assert snapshot.status == "LIMITED"
    assert all(item.probabilities is None for item in snapshot.horizons)
    assert all(item.dominant_phase is None for item in snapshot.horizons)
    assert all(item.publication_status == "LIMITED" for item in snapshot.horizons)


def test_materialization_isolates_one_horizon_with_missing_phase_parameter_map() -> (
    None
):
    module = _load_module()
    panel, labels = _panel()
    writer = Writer()
    training = module.train_validate_economic_cycle_model(
        trained_through="2002-07-31",
        loader=TrainingLoader(panel, labels),
        writer=writer,
        validator=lambda *_args, **_kwargs: ValidationReport(
            horizons={horizon: _horizon_validation() for horizon in (0, 1, 2)},
            predictions=(),
        ),
    )
    artifact_row = dict(training["artifact_row"])
    parameters = json.loads(str(artifact_row["parameters_json"]))
    del parameters["horizons"]["1"]["means"]["recession"]
    artifact_row["parameters_json"] = json.dumps(parameters)

    class Loader:
        def load_artifact(self, **_kwargs):
            return artifact_row

        def load_prediction_data(self, _as_of_date):
            return panel.iloc[-1].to_dict()

    snapshot = module.materialize_economic_cycle_snapshot(
        as_of_date="2002-08-31", loader=Loader(), writer=writer
    )

    assert snapshot.horizons[0].probabilities is not None
    assert snapshot.horizons[1].probabilities is None
    assert snapshot.horizons[1].dominant_phase is None
    assert snapshot.horizons[1].publication_status == "LIMITED"
    assert snapshot.horizons[2].probabilities is not None


def test_replay_uses_one_strict_origin_load_and_origin_specific_artifact() -> None:
    module = _load_module()

    class Loader:
        def __init__(self) -> None:
            self.calls: list[str] = []

        def load_for_origin(self, origin):
            self.calls.append(str(origin))
            return [{"origin": str(origin)}]

        def load_latest_current_artifact(self, *_args, **_kwargs):
            raise AssertionError("historical replay must not read a current artifact")

    loader = Loader()
    writer = Writer()
    trained: list[tuple[str, str]] = []

    def trainer(*, trained_through, preloaded_vintage_rows, **_kwargs):
        origin = str(preloaded_vintage_rows[0]["origin"])
        trained.append((str(trained_through), origin))
        return {
            "model_version": f"model-{origin}",
            "artifact_row": {"model_version": f"model-{origin}"},
        }

    def materializer(*, as_of_date, model_version, run_kind, writer, **_kwargs):
        row = {
            "as_of_date": str(as_of_date),
            "model_version": model_version,
            "run_kind": run_kind,
        }
        writer.upsert_snapshot(row)
        return row

    for _ in range(2):
        module.replay_economic_cycle_history(
            start_date="2025-01-31",
            end_date="2025-03-31",
            loader=loader,
            writer=writer,
            trainer=trainer,
            materializer=materializer,
        )

    assert len(loader.calls) == 6
    assert all(cutoff < origin for cutoff, origin in trained)
    assert len(writer.snapshots) == 3
    assert all(key[2] == "historical_replay" for key in writer.snapshots)


def test_training_does_not_cache_forecast_origin_rows_under_prior_cutoff() -> None:
    module = _load_module()
    panel, labels = _panel()

    class Loader(TrainingLoader):
        def __init__(self) -> None:
            super().__init__(panel, labels)
            self.remembered: list[tuple[object, object]] = []

        def remember_origin(self, origin, rows):
            self.remembered.append((origin, rows))

    loader = Loader()
    module.train_validate_economic_cycle_model(
        trained_through="2002-07-31",
        loader=loader,
        writer=Writer(),
        preloaded_vintage_rows=[{"origin": "2002-08-31"}],
        validator=lambda *_args, **_kwargs: ValidationReport(
            horizons={horizon: _horizon_validation() for horizon in (0, 1, 2)},
            predictions=(),
        ),
    )

    assert loader.remembered == []


def test_default_loader_builds_and_reuses_one_bulk_pit_panel() -> None:
    module = _load_module()
    loader = module.EconomicCyclePipelineLoader(
        history_start=date(2020, 1, 31)
    )
    source_rows = [
        {
            "series_id": "PAYEMS",
            "observation_date": "2020-01-01",
            "realtime_start": "2020-01-15",
            "realtime_end": "9999-12-31",
            "value": 100.0,
            "source": "fred",
        }
    ]

    with pytest.MonkeyPatch.context() as monkeypatch:
        history_calls: list[date] = []

        def load_history(*_args, as_of_date, **_kwargs):
            history_calls.append(as_of_date)
            return source_rows

        monkeypatch.setattr(module, "load_economic_cycle_vintage_history", load_history)
        monkeypatch.setattr(
            module,
            "load_economic_cycle_vintages",
            lambda *_args, **_kwargs: (_ for _ in ()).throw(
                AssertionError("panel construction must not issue one query per origin")
            ),
        )
        loader.prime_panel(date(2020, 3, 31))
        shorter = loader._panel_through(date(2020, 2, 29))

    assert history_calls == [date(2020, 3, 31)]
    assert shorter["forecast_origin"].dt.date.tolist() == [
        date(2020, 1, 31),
        date(2020, 2, 29),
    ]


def test_economic_cycle_jobs_delegate_without_registering_a_schedule() -> None:
    jobs = importlib.import_module("app.jobs.ingestion_jobs")
    collected: list[dict[str, object]] = []
    materialized: list[dict[str, object]] = []

    collect_result = jobs.run_collect_economic_cycle_vintages(
        api_key="test-key",
        collector=lambda **kwargs: collected.append(kwargs)
        or {"stored": 17, "requested_series": 17, "failed": []},
    )
    materialize_result = jobs.run_materialize_economic_cycle(
        as_of_date="2026-06-30",
        materializer=lambda **kwargs: materialized.append(kwargs)
        or type("Snapshot", (), {"status": "LIMITED", "model_version": "cycle-v1"})(),
    )

    assert collect_result["status"] == "success"
    assert collect_result["rows_written"] == 17
    assert collected and collected[0]["api_key"] == "test-key"
    assert materialize_result["status"] == "partial_success"
    assert materialized == [{"as_of_date": "2026-06-30"}]
    assert "schedule" not in collect_result["details"]
    assert "schedule" not in materialize_result["details"]


def test_pipeline_errors_do_not_replace_latest_approved_rows() -> None:
    module = _load_module()
    writer = Writer()
    approved = {
        "model_version": "approved-v1",
        "trained_through": "2026-05-31",
        "publication_status": "READY",
    }
    writer.upsert_artifact(approved)

    class FailingLoader:
        def load_training_data(self, _trained_through):
            raise RuntimeError("database unavailable")

    with pytest.raises(RuntimeError, match="database unavailable"):
        module.train_validate_economic_cycle_model(
            trained_through="2026-06-30",
            loader=FailingLoader(),
            writer=writer,
        )

    assert list(writer.artifacts.values()) == [approved]
