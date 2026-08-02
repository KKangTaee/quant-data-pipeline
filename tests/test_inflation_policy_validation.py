from __future__ import annotations

import math


def test_rolling_origin_training_uses_only_targets_available_by_origin() -> None:
    from finance.inflation_policy_validation import (
        ContinuousOriginRow,
        run_continuous_rolling_origin,
    )

    rows = (
        ContinuousOriginRow("2026-01-01", "2026-02-01", {"x": 1.0}, 1.1),
        ContinuousOriginRow("2026-02-01", "2026-04-01", {"x": 2.0}, 2.1),
        ContinuousOriginRow("2026-03-01", "2026-04-01", {"x": 3.0}, 3.1),
        ContinuousOriginRow("2026-04-01", "2026-05-01", {"x": 4.0}, 4.1),
    )
    training_targets: list[tuple[float, ...]] = []

    def fit(training):
        targets = tuple(row.target_value for row in training)
        training_targets.append(targets)
        return sum(targets) / len(targets)

    predictions = run_continuous_rolling_origin(
        rows,
        minimum_training_rows=1,
        fit_fn=fit,
        predict_fn=lambda artifact, _row: artifact,
        baseline_fn=lambda training, _row: training[-1].target_value,
    )

    assert training_targets == [(1.1,), (1.1,), (1.1, 2.1, 3.1)]
    assert [row.training_target_through_at for row in predictions] == [
        "2026-02-01",
        "2026-02-01",
        "2026-04-01",
    ]


def test_continuous_metrics_compare_distribution_score_and_interval_coverage() -> None:
    from finance.inflation_policy_validation import (
        ContinuousValidationPrediction,
        calculate_continuous_metrics,
    )

    predictions = tuple(
        ContinuousValidationPrediction(
            forecast_origin_at=f"2026-0{index}-01",
            target_available_at=f"2026-0{index + 1}-01",
            training_target_through_at=f"2026-0{index - 1}-01",
            actual_value=actual,
            predicted_median=actual,
            predictive_samples=(actual - 0.2, actual, actual + 0.2),
            baseline_prediction=0.0,
            complete_feature_ratio=1.0,
        )
        for index, actual in enumerate((1.0, 2.0, 3.0), start=2)
    )

    metrics = calculate_continuous_metrics(predictions)

    assert metrics["mae"] == 0.0
    assert metrics["rmse"] == 0.0
    assert metrics["crps"] < metrics["baseline_crps"]
    assert metrics["interval_80_coverage"] == 1.0
    assert metrics["complete_feature_ratio"] == 1.0


def test_categorical_metrics_require_exact_simplex_and_report_calibration() -> None:
    from finance.inflation_policy_validation import calculate_categorical_metrics

    metrics = calculate_categorical_metrics(
        (
            {"cut": 1.0, "hold": 0.0, "hike": 0.0},
            {"cut": 0.0, "hold": 1.0, "hike": 0.0},
            {"cut": 0.0, "hold": 0.0, "hike": 1.0},
        ),
        ("cut", "hold", "hike"),
        labels=("cut", "hold", "hike"),
    )

    assert metrics == {
        "brier_score": 0.0,
        "log_loss": 0.0,
        "accuracy": 1.0,
        "calibration_error": 0.0,
    }


def test_publication_gate_never_upgrades_weak_or_invalid_evidence() -> None:
    from finance.inflation_policy_validation import (
        PublicationEvidence,
        PublicationThresholds,
        evaluate_publication_gate,
    )

    thresholds = PublicationThresholds(
        minimum_origins=3,
        minimum_complete_feature_ratio=0.8,
        maximum_calibration_error=0.15,
        require_baseline_improvement=True,
    )
    ready = PublicationEvidence(
        origin_count=5,
        complete_feature_ratio=0.9,
        primary_score=0.10,
        baseline_score=0.20,
        calibration_error=0.05,
        probabilities_valid=True,
        critical_inputs_available=True,
    )

    assert evaluate_publication_gate(ready, thresholds).status == "READY"
    assert (
        evaluate_publication_gate(
            PublicationEvidence(**{**ready.__dict__, "origin_count": 2}), thresholds
        ).status
        == "LIMITED"
    )
    assert (
        evaluate_publication_gate(
            PublicationEvidence(**{**ready.__dict__, "primary_score": 0.25}),
            thresholds,
        ).status
        == "LIMITED"
    )
    assert (
        evaluate_publication_gate(
            PublicationEvidence(**{**ready.__dict__, "probabilities_valid": False}),
            thresholds,
        ).status
        == "FAILED"
    )
    assert (
        evaluate_publication_gate(
            PublicationEvidence(
                **{**ready.__dict__, "critical_inputs_available": False}
            ),
            thresholds,
        ).status
        == "NOT_AVAILABLE"
    )


def test_inverse_error_weights_are_capped_before_use_in_ensemble() -> None:
    from finance.inflation_policy_validation import derive_capped_inverse_error_weights

    weights = derive_capped_inverse_error_weights(
        {"bridge": 0.10, "linear": 0.20, "recent_mean": 0.40},
        max_component_weight=0.60,
    )

    assert math.isclose(sum(weights.values()), 1.0)
    assert max(weights.values()) <= 0.60 + 1e-12
    assert weights["bridge"] > weights["linear"] > weights["recent_mean"]
