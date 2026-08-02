"""Chronological validation metrics and fail-closed publication gates."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Mapping, Sequence

import numpy as np


@dataclass(frozen=True)
class ContinuousOriginRow:
    """One forecast origin whose target has an explicit availability timestamp."""

    forecast_origin_at: str
    target_available_at: str
    features: Mapping[str, object]
    target_value: float
    complete_feature_ratio: float = 1.0


@dataclass(frozen=True)
class ContinuousValidationPrediction:
    forecast_origin_at: str
    target_available_at: str
    training_target_through_at: str
    actual_value: float
    predicted_median: float
    predictive_samples: tuple[float, ...]
    baseline_prediction: float
    complete_feature_ratio: float


@dataclass(frozen=True)
class PublicationThresholds:
    minimum_origins: int
    minimum_complete_feature_ratio: float
    maximum_calibration_error: float
    require_baseline_improvement: bool


@dataclass(frozen=True)
class PublicationEvidence:
    origin_count: int
    complete_feature_ratio: float
    primary_score: float
    baseline_score: float
    calibration_error: float
    probabilities_valid: bool
    critical_inputs_available: bool


@dataclass(frozen=True)
class PublicationDecision:
    status: str
    reason_codes: tuple[str, ...]


def _timestamp(value: object) -> datetime:
    parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _finite(value: object, *, field: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def run_continuous_rolling_origin(
    rows: Sequence[ContinuousOriginRow],
    *,
    minimum_training_rows: int,
    fit_fn: Callable[[tuple[ContinuousOriginRow, ...]], object],
    predict_fn: Callable[[object, ContinuousOriginRow], object],
    baseline_fn: Callable[[tuple[ContinuousOriginRow, ...], ContinuousOriginRow], object],
) -> tuple[ContinuousValidationPrediction, ...]:
    """Refit at every origin using only targets released by that origin."""

    if int(minimum_training_rows) <= 0:
        raise ValueError("minimum_training_rows must be positive")
    ordered = tuple(sorted(rows, key=lambda row: _timestamp(row.forecast_origin_at)))
    predictions: list[ContinuousValidationPrediction] = []
    for evaluation in ordered:
        origin = _timestamp(evaluation.forecast_origin_at)
        training = tuple(
            row
            for row in ordered
            if row is not evaluation and _timestamp(row.target_available_at) <= origin
        )
        if len(training) < int(minimum_training_rows):
            continue
        artifact = fit_fn(training)
        raw_prediction = predict_fn(artifact, evaluation)
        if isinstance(raw_prediction, Sequence) and not isinstance(
            raw_prediction, (str, bytes, bytearray)
        ):
            samples = tuple(
                _finite(value, field="predictive sample") for value in raw_prediction
            )
            if not samples:
                raise ValueError("predict_fn cannot return an empty sample")
            predicted_median = float(np.quantile(np.asarray(samples), 0.5))
        else:
            predicted_median = _finite(raw_prediction, field="prediction")
            samples = (predicted_median,)
        training_through = max(
            training, key=lambda row: _timestamp(row.target_available_at)
        ).target_available_at
        predictions.append(
            ContinuousValidationPrediction(
                forecast_origin_at=evaluation.forecast_origin_at,
                target_available_at=evaluation.target_available_at,
                training_target_through_at=training_through,
                actual_value=_finite(evaluation.target_value, field="target_value"),
                predicted_median=predicted_median,
                predictive_samples=samples,
                baseline_prediction=_finite(
                    baseline_fn(training, evaluation), field="baseline prediction"
                ),
                complete_feature_ratio=max(
                    0.0,
                    min(
                        1.0,
                        _finite(
                            evaluation.complete_feature_ratio,
                            field="complete_feature_ratio",
                        ),
                    ),
                ),
            )
        )
    return tuple(predictions)


def _empirical_crps(samples: Sequence[float], actual: float) -> float:
    values = tuple(float(value) for value in samples)
    first = sum(abs(value - actual) for value in values) / len(values)
    pairwise = sum(abs(left - right) for left in values for right in values)
    return first - 0.5 * pairwise / (len(values) ** 2)


def calculate_continuous_metrics(
    predictions: Sequence[ContinuousValidationPrediction],
) -> dict[str, float]:
    """Calculate point, distribution, interval, baseline, and coverage metrics."""

    if not predictions:
        raise ValueError("continuous predictions cannot be empty")
    errors: list[float] = []
    squared: list[float] = []
    crps: list[float] = []
    baseline_crps: list[float] = []
    interval_hits = {0.50: 0, 0.80: 0, 0.95: 0}
    for row in predictions:
        actual = _finite(row.actual_value, field="actual_value")
        predicted = _finite(row.predicted_median, field="predicted_median")
        samples = tuple(
            _finite(value, field="predictive sample")
            for value in row.predictive_samples
        )
        if not samples:
            raise ValueError("predictive samples cannot be empty")
        error = predicted - actual
        errors.append(abs(error))
        squared.append(error**2)
        crps.append(_empirical_crps(samples, actual))
        baseline_crps.append(abs(_finite(row.baseline_prediction, field="baseline") - actual))
        array = np.asarray(samples, dtype=float)
        for coverage in interval_hits:
            tail = (1.0 - coverage) / 2.0
            lower, upper = np.quantile(array, (tail, 1.0 - tail))
            interval_hits[coverage] += int(float(lower) <= actual <= float(upper))
    count = len(predictions)
    return {
        "mae": sum(errors) / count,
        "rmse": math.sqrt(sum(squared) / count),
        "crps": sum(crps) / count,
        "baseline_crps": sum(baseline_crps) / count,
        "interval_50_coverage": interval_hits[0.50] / count,
        "interval_80_coverage": interval_hits[0.80] / count,
        "interval_95_coverage": interval_hits[0.95] / count,
        "complete_feature_ratio": sum(
            max(0.0, min(1.0, float(row.complete_feature_ratio)))
            for row in predictions
        )
        / count,
    }


def calculate_categorical_metrics(
    probability_rows: Sequence[Mapping[str, object]],
    targets: Sequence[str],
    *,
    labels: Sequence[str],
) -> dict[str, float]:
    """Calculate multiclass Brier, log loss, accuracy, and confidence ECE."""

    approved = tuple(labels)
    if not probability_rows or len(probability_rows) != len(targets):
        raise ValueError("probability rows and targets must be non-empty and aligned")
    rows: list[dict[str, float]] = []
    for raw in probability_rows:
        if set(raw) != set(approved):
            raise ValueError("probability row must contain exact labels")
        row = {label: _finite(raw[label], field="probability") for label in approved}
        if any(value < 0.0 for value in row.values()) or not math.isclose(
            sum(row.values()), 1.0, abs_tol=1e-9
        ):
            raise ValueError("probability rows must be finite simplexes")
        rows.append(row)
    if any(target not in approved for target in targets):
        raise ValueError("categorical target uses an unknown label")
    count = len(rows)
    brier = sum(
        sum(
            (row[label] - (1.0 if label == target else 0.0)) ** 2
            for label in approved
        )
        for row, target in zip(rows, targets, strict=True)
    ) / count
    log_loss = -sum(
        math.log(max(row[target], 1e-15))
        for row, target in zip(rows, targets, strict=True)
    ) / count
    predictions = [max(approved, key=row.__getitem__) for row in rows]
    accuracy = sum(
        predicted == target
        for predicted, target in zip(predictions, targets, strict=True)
    ) / count
    bins: list[list[tuple[float, float]]] = [[] for _ in range(10)]
    for row, predicted, target in zip(rows, predictions, targets, strict=True):
        confidence = row[predicted]
        index = min(9, max(0, math.ceil(confidence * 10.0) - 1))
        bins[index].append((confidence, 1.0 if predicted == target else 0.0))
    calibration = 0.0
    for members in bins:
        if members:
            calibration += len(members) / count * abs(
                sum(item[0] for item in members) / len(members)
                - sum(item[1] for item in members) / len(members)
            )
    return {
        "brier_score": brier,
        "log_loss": log_loss,
        "accuracy": accuracy,
        "calibration_error": calibration,
    }


def evaluate_publication_gate(
    evidence: PublicationEvidence,
    thresholds: PublicationThresholds,
) -> PublicationDecision:
    """Apply precommitted evidence thresholds without last-good probability fallback."""

    if not evidence.critical_inputs_available:
        return PublicationDecision("NOT_AVAILABLE", ("critical_inputs_missing",))
    numeric = (
        evidence.complete_feature_ratio,
        evidence.primary_score,
        evidence.baseline_score,
        evidence.calibration_error,
    )
    if not evidence.probabilities_valid or any(
        not math.isfinite(float(value)) for value in numeric
    ):
        return PublicationDecision("FAILED", ("invalid_probability_or_metric",))
    reasons: list[str] = []
    if int(evidence.origin_count) < int(thresholds.minimum_origins):
        reasons.append("insufficient_origins")
    if float(evidence.complete_feature_ratio) < float(
        thresholds.minimum_complete_feature_ratio
    ):
        reasons.append("insufficient_feature_coverage")
    if float(evidence.calibration_error) > float(
        thresholds.maximum_calibration_error
    ):
        reasons.append("calibration_error_too_high")
    if thresholds.require_baseline_improvement and not (
        float(evidence.primary_score) < float(evidence.baseline_score)
    ):
        reasons.append("no_baseline_improvement")
    return PublicationDecision(
        "LIMITED" if reasons else "READY",
        tuple(reasons),
    )


def derive_capped_inverse_error_weights(
    component_errors: Mapping[str, object],
    *,
    max_component_weight: float,
) -> dict[str, float]:
    """Convert rolling-origin errors to weights without allowing one component monopoly."""

    if not component_errors:
        raise ValueError("component_errors cannot be empty")
    cap = _finite(max_component_weight, field="max_component_weight")
    if cap <= 0.0 or cap > 1.0:
        raise ValueError("max_component_weight must be in (0, 1]")
    if len(component_errors) > 1 and cap * len(component_errors) < 1.0 - 1e-12:
        raise ValueError("weight cap is infeasible for the component count")
    scores: dict[str, float] = {}
    for name, raw_error in component_errors.items():
        error = _finite(raw_error, field=f"component error {name}")
        if error <= 0.0:
            raise ValueError("component errors must be positive")
        scores[str(name)] = 1.0 / error
    if len(scores) == 1:
        return {next(iter(scores)): 1.0}

    remaining = set(scores)
    weights = {name: 0.0 for name in scores}
    remaining_mass = 1.0
    while remaining:
        score_total = sum(scores[name] for name in remaining)
        provisional = {
            name: remaining_mass * scores[name] / score_total for name in remaining
        }
        capped = [name for name, value in provisional.items() if value > cap + 1e-12]
        if not capped:
            for name, value in provisional.items():
                weights[name] = value
            break
        for name in capped:
            weights[name] = cap
            remaining_mass -= cap
            remaining.remove(name)
    total = sum(weights.values())
    return {name: value / total for name, value in weights.items()}
