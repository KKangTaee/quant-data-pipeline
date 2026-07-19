from __future__ import annotations

import importlib
import importlib.util
import math
from dataclasses import replace

import pandas as pd

from finance.economic_cycle_model import PHASES


def _load_module():
    spec = importlib.util.find_spec("finance.economic_cycle_validation")
    assert spec is not None, "economic cycle validation module must exist"
    return importlib.import_module("finance.economic_cycle_validation")


def _validation_panel(periods: int = 24) -> tuple[pd.DataFrame, pd.Series]:
    labels = pd.Series([PHASES[index % 4] for index in range(periods)])
    centers = {
        "recovery": (-1.0, -1.0, 1.0, 1.0),
        "expansion": (1.0, 1.0, 1.0, 1.0),
        "slowdown": (1.0, 1.0, -1.0, -1.0),
        "recession": (-1.0, -1.0, -1.0, -1.0),
    }
    rows = []
    for index, phase in enumerate(labels):
        current = centers[phase]
        next_phase = labels.iloc[(index + 1) % periods]
        rows.append(
            {
                "forecast_origin": pd.Timestamp("2000-01-31")
                + pd.offsets.MonthEnd(index),
                "activity_score": current[0],
                "labor_income_score": current[1],
                "activity_momentum_3m": current[2],
                "labor_income_momentum_3m": current[3],
                "financial_leading_score": float(PHASES.index(next_phase)),
                "inflation_policy_score": float(index % 3) - 1.0,
                "overall_coverage": 1.0,
            }
        )
    return pd.DataFrame(rows), labels


def test_rolling_origin_artifacts_train_only_on_targets_before_origin() -> None:
    module = _load_module()
    panel, labels = _validation_panel()

    report = module.run_rolling_origin_validation(panel, labels, initial_train_months=8)

    assert report.predictions
    for prediction in report.predictions:
        assert (
            prediction.training_target_through_index < prediction.forecast_origin_index
        )
        assert prediction.target_index == (
            prediction.forecast_origin_index + prediction.horizon_months
        )


def test_rolling_origin_fit_receives_training_labels_not_evaluation_truth() -> None:
    module = _load_module()
    model_module = importlib.import_module("finance.economic_cycle_model")
    panel, training_labels = _validation_panel()
    evaluation_labels = pd.Series(["recession"] * len(training_labels))
    captured: list[list[str]] = []

    def fit_spy(features, labels, **kwargs):
        captured.append(list(labels))
        return model_module.fit_horizon_model(features, labels, **kwargs)

    module.run_rolling_origin_validation(
        panel,
        evaluation_labels,
        training_labels=training_labels,
        initial_train_months=8,
        fit_fn=fit_spy,
    )

    assert captured
    assert any(any(label != "recession" for label in fitted) for fitted in captured)


def test_multiclass_metrics_match_hand_calculation() -> None:
    module = _load_module()
    rows = [
        {"recovery": 0.7, "expansion": 0.1, "slowdown": 0.1, "recession": 0.1},
        {"recovery": 0.2, "expansion": 0.4, "slowdown": 0.2, "recession": 0.2},
    ]

    metrics = module.calculate_multiclass_metrics(rows, ["recovery", "expansion"])

    assert math.isclose(metrics["brier_score"], 0.3, abs_tol=1e-12)
    assert math.isclose(
        metrics["log_loss"], -(math.log(0.7) + math.log(0.4)) / 2.0, abs_tol=1e-12
    )
    assert metrics["accuracy"] == 1.0
    assert math.isclose(metrics["ece"], 0.45, abs_tol=1e-12)


def test_baselines_share_identical_forecast_safe_target_rows() -> None:
    module = _load_module()
    panel, labels = _validation_panel()

    report = module.run_rolling_origin_validation(panel, labels, initial_train_months=8)

    for horizon in (0, 1, 2):
        rows = [item for item in report.predictions if item.horizon_months == horizon]
        assert rows
        assert all(item.persistence_probabilities for item in rows)
        assert all(item.transition_probabilities for item in rows)
        assert all(item.target_label == labels.iloc[item.target_index] for item in rows)


def _ready_horizon(module):
    return module.HorizonValidation(
        origin_count=150,
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


def test_publication_gate_requires_counts_coverage_calibration_and_baselines() -> None:
    module = _load_module()
    ready = _ready_horizon(module)
    report = module.ValidationReport(horizons={0: ready}, predictions=())

    assert module.evaluate_publication_gate(report, 0).status == "READY"

    cases = [
        (replace(ready, origin_count=119), "INSUFFICIENT_ORIGINS"),
        (replace(ready, recession_episodes=1), "INSUFFICIENT_RECESSION_EPISODES"),
        (
            replace(ready, phase_support={**ready.phase_support, "recovery": 11}),
            "INSUFFICIENT_PHASE_SUPPORT",
        ),
        (replace(ready, complete_feature_ratio=0.74), "LOW_FEATURE_COVERAGE"),
        (
            replace(ready, metrics={**ready.metrics, "ece": 0.13}),
            "CALIBRATION_ERROR",
        ),
        (replace(ready, probabilities_valid=False), "INVALID_PROBABILITIES"),
        (
            replace(
                ready,
                metrics={**ready.metrics, "brier_score": 0.26, "log_loss": 0.61},
            ),
            "BASELINE_UNDERPERFORMANCE",
        ),
    ]
    for horizon_validation, expected_reason in cases:
        decision = module.evaluate_publication_gate(
            module.ValidationReport(horizons={0: horizon_validation}, predictions=()), 0
        )
        assert decision.status == "LIMITED"
        assert expected_reason in decision.reason_codes


def test_publication_gate_is_horizon_specific() -> None:
    module = _load_module()
    ready = _ready_horizon(module)
    limited = replace(ready, origin_count=80)
    report = module.ValidationReport(
        horizons={0: ready, 1: limited, 2: ready}, predictions=()
    )

    assert module.evaluate_publication_gate(report, 0).status == "READY"
    assert module.evaluate_publication_gate(report, 1).status == "LIMITED"
    assert module.evaluate_publication_gate(report, 2).status == "READY"
