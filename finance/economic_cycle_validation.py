"""Forecast-safe rolling-origin validation for economic-cycle models."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Callable, Mapping, Sequence

import pandas as pd

from finance.economic_cycle_model import (
    CURRENT_FEATURES,
    FORECAST_FEATURES,
    HORIZONS,
    PHASES,
    HorizonModelArtifact,
    apply_temperature,
    blend_likelihood_and_transition,
    estimate_transition_matrix,
    fit_horizon_model,
    fit_temperature,
    predict_phase_probabilities,
)

READY_GATE = {
    "minimum_origins": 120,
    "minimum_recession_episodes": 2,
    "minimum_targets_per_phase": 12,
    "minimum_complete_feature_ratio": 0.75,
    "maximum_ece": 0.12,
}


@dataclass(frozen=True)
class ValidationPrediction:
    """One out-of-fold prediction and its forecast-safe baselines."""

    horizon_months: int
    forecast_origin_index: int
    forecast_origin_date: str
    target_index: int
    target_date: str
    training_target_through_index: int
    target_label: str
    probabilities: dict[str, float]
    persistence_probabilities: dict[str, float]
    transition_probabilities: dict[str, float]
    temperature: float
    complete_feature_ratio: float


@dataclass(frozen=True)
class HorizonValidation:
    """Metrics and publication evidence for one forecast horizon."""

    origin_count: int
    metrics: dict[str, float]
    baseline_metrics: dict[str, dict[str, float]]
    phase_support: dict[str, int]
    recession_episodes: int
    complete_feature_ratio: float
    probabilities_valid: bool


@dataclass(frozen=True)
class ValidationReport:
    """All horizon validation summaries plus their aligned prediction rows."""

    horizons: dict[int, HorizonValidation]
    predictions: tuple[ValidationPrediction, ...]


@dataclass(frozen=True)
class PublicationDecision:
    """Stable READY/LIMITED decision for one independently gated horizon."""

    horizon_months: int
    status: str
    reason_codes: tuple[str, ...]


def _normalized_probability_row(
    probabilities: Mapping[str, float],
) -> dict[str, float]:
    if set(probabilities) != set(PHASES):
        raise ValueError("probability rows must contain the exact approved phases")
    values = {phase: float(probabilities[phase]) for phase in PHASES}
    if any(not math.isfinite(value) or value < 0.0 for value in values.values()):
        raise ValueError("probabilities must be finite and non-negative")
    total = sum(values.values())
    if total <= 0.0:
        raise ValueError("probability rows must contain positive mass")
    return {phase: values[phase] / total for phase in PHASES}


def calculate_multiclass_metrics(
    probability_rows: Sequence[Mapping[str, float]],
    target_labels: Sequence[object],
) -> dict[str, float]:
    """Calculate multiclass Brier, log loss, accuracy, and 10-bin ECE."""

    rows = [_normalized_probability_row(row) for row in probability_rows]
    targets = [str(target) for target in target_labels]
    if not rows or len(rows) != len(targets):
        raise ValueError("probability rows and targets must be non-empty and aligned")
    if any(target not in PHASES for target in targets):
        raise ValueError("targets must use the approved phase vocabulary")

    brier = sum(
        sum((row[phase] - (1.0 if phase == target else 0.0)) ** 2 for phase in PHASES)
        for row, target in zip(rows, targets, strict=True)
    ) / len(rows)
    log_loss = -sum(
        math.log(max(row[target], 1e-15))
        for row, target in zip(rows, targets, strict=True)
    ) / len(rows)
    predicted = [max(PHASES, key=row.__getitem__) for row in rows]
    accuracy = sum(
        prediction == target
        for prediction, target in zip(predicted, targets, strict=True)
    ) / len(rows)

    # Fixed bins are (0.0, 0.1], ..., (0.9, 1.0], with zero included first.
    bin_members: list[list[tuple[float, float]]] = [[] for _ in range(10)]
    for row, prediction, target in zip(rows, predicted, targets, strict=True):
        confidence = row[prediction]
        bin_index = min(9, max(0, math.ceil(confidence * 10.0) - 1))
        bin_members[bin_index].append(
            (confidence, 1.0 if prediction == target else 0.0)
        )
    ece = 0.0
    for members in bin_members:
        if not members:
            continue
        mean_confidence = sum(item[0] for item in members) / len(members)
        mean_accuracy = sum(item[1] for item in members) / len(members)
        ece += (len(members) / len(rows)) * abs(mean_accuracy - mean_confidence)

    return {
        "brier_score": float(brier),
        "log_loss": float(log_loss),
        "accuracy": float(accuracy),
        "ece": float(ece),
    }


def _date_at(panel: pd.DataFrame, index: int) -> str:
    if "forecast_origin" not in panel:
        return str(index)
    value = panel.iloc[index]["forecast_origin"]
    if pd.isna(value):
        return str(index)
    timestamp = pd.Timestamp(value)
    return timestamp.date().isoformat()


def _advance_transition(
    matrix: Mapping[str, Mapping[str, float]],
    origin_phase: str,
    steps: int,
) -> dict[str, float]:
    distribution = {phase: 1.0 if phase == origin_phase else 0.0 for phase in PHASES}
    for _ in range(steps):
        distribution = {
            target: sum(
                distribution[source] * float(matrix[source][target])
                for source in PHASES
            )
            for target in PHASES
        }
    return _normalized_probability_row(distribution)


def _finite_simplex(probabilities: Mapping[str, float]) -> bool:
    try:
        normalized = _normalized_probability_row(probabilities)
    except (KeyError, TypeError, ValueError):
        return False
    return math.isclose(sum(normalized.values()), 1.0, abs_tol=1e-9)


def _count_recession_episodes(rows: Sequence[ValidationPrediction]) -> int:
    episodes = 0
    previous_target_index: int | None = None
    previous_label: str | None = None
    for row in sorted(rows, key=lambda item: item.target_index):
        contiguous_recession = (
            previous_target_index is not None
            and row.target_index == previous_target_index + 1
            and previous_label == "recession"
        )
        if row.target_label == "recession" and not contiguous_recession:
            episodes += 1
        previous_target_index = row.target_index
        previous_label = row.target_label
    return episodes


def _prior_temperature(
    raw_rows: Sequence[tuple[int, Mapping[str, float]]],
    training_labels: pd.Series,
    forecast_origin_index: int,
) -> float:
    eligible = [
        (target_index, probabilities)
        for target_index, probabilities in raw_rows
        if target_index < forecast_origin_index
        and str(training_labels.iloc[target_index]) in PHASES
    ]
    if len(eligible) < 2:
        return 1.0
    return fit_temperature(
        [item[1] for item in eligible],
        [str(training_labels.iloc[item[0]]) for item in eligible],
    )


def run_rolling_origin_validation(
    panel: pd.DataFrame,
    labels: Sequence[object] | pd.Series,
    *,
    training_labels: Sequence[object] | pd.Series | None = None,
    initial_train_months: int = 120,
    fit_fn: Callable[..., HorizonModelArtifact] = fit_horizon_model,
) -> ValidationReport:
    """Retrain at each origin without exposing evaluation truth to model fitting."""

    if initial_train_months < 2:
        raise ValueError("initial_train_months must be at least 2")
    evaluation = pd.Series(labels, dtype="object").reset_index(drop=True)
    eligible_labels = pd.Series(
        labels if training_labels is None else training_labels, dtype="object"
    ).reset_index(drop=True)
    feature_panel = panel.reset_index(drop=True)
    if len(feature_panel) != len(evaluation) or len(feature_panel) != len(
        eligible_labels
    ):
        raise ValueError("panel, evaluation labels, and training labels must align")

    predictions: list[ValidationPrediction] = []
    raw_oof: dict[int, list[tuple[int, dict[str, float]]]] = {
        horizon: [] for horizon in HORIZONS
    }
    for origin in range(initial_train_months, len(feature_panel)):
        known_labels = eligible_labels.iloc[:origin]
        known_phase = str(known_labels.iloc[-1])
        if known_phase not in PHASES:
            continue
        transition_matrix = estimate_transition_matrix(known_labels)

        for horizon in HORIZONS:
            target_index = origin + horizon
            if target_index >= len(feature_panel):
                continue
            feature_names = CURRENT_FEATURES if horizon == 0 else FORECAST_FEATURES
            if any(name not in feature_panel for name in feature_names):
                raise ValueError(f"missing features for horizon {horizon}")

            # A shifted training pair is allowed only when its target precedes origin.
            last_training_feature_index = origin - horizon - 1
            if last_training_feature_index < 0:
                continue
            training_feature_indices = list(range(last_training_feature_index + 1))
            training_targets = pd.Series(
                [
                    eligible_labels.iloc[index + horizon]
                    for index in training_feature_indices
                ],
                dtype="object",
            )
            training_features = feature_panel.loc[
                training_feature_indices, list(feature_names)
            ].reset_index(drop=True)
            artifact = fit_fn(
                training_features,
                training_targets,
                horizon_months=horizon,
            )
            if artifact.publication_status != "READY":
                continue

            likelihood = predict_phase_probabilities(
                artifact,
                feature_panel.iloc[origin].to_dict(),
                temperature=1.0,
            )
            transition_probabilities = _advance_transition(
                transition_matrix, known_phase, horizon + 1
            )
            uncalibrated = (
                likelihood
                if horizon == 0
                else blend_likelihood_and_transition(
                    likelihood, transition_probabilities
                )
            )
            temperature = _prior_temperature(raw_oof[horizon], eligible_labels, origin)
            probabilities = apply_temperature(uncalibrated, temperature)
            raw_oof[horizon].append((target_index, uncalibrated))

            persistence = {
                phase: 1.0 if phase == known_phase else 0.0 for phase in PHASES
            }
            coverage_value = feature_panel.iloc[origin].get("overall_coverage", 1.0)
            try:
                coverage = float(coverage_value)
            except (TypeError, ValueError):
                coverage = 0.0
            if not math.isfinite(coverage):
                coverage = 0.0
            predictions.append(
                ValidationPrediction(
                    horizon_months=horizon,
                    forecast_origin_index=origin,
                    forecast_origin_date=_date_at(feature_panel, origin),
                    target_index=target_index,
                    target_date=_date_at(feature_panel, target_index),
                    training_target_through_index=origin - 1,
                    target_label=str(evaluation.iloc[target_index]),
                    probabilities=probabilities,
                    persistence_probabilities=persistence,
                    transition_probabilities=transition_probabilities,
                    temperature=temperature,
                    complete_feature_ratio=max(0.0, min(1.0, coverage)),
                )
            )

    horizon_summaries: dict[int, HorizonValidation] = {}
    for horizon in HORIZONS:
        rows = [row for row in predictions if row.horizon_months == horizon]
        if not rows:
            horizon_summaries[horizon] = HorizonValidation(
                origin_count=0,
                metrics={
                    "brier_score": math.inf,
                    "log_loss": math.inf,
                    "accuracy": 0.0,
                    "ece": math.inf,
                },
                baseline_metrics={
                    "persistence": {"brier_score": math.inf, "log_loss": math.inf},
                    "historical_transition": {
                        "brier_score": math.inf,
                        "log_loss": math.inf,
                    },
                },
                phase_support={phase: 0 for phase in PHASES},
                recession_episodes=0,
                complete_feature_ratio=0.0,
                probabilities_valid=False,
            )
            continue
        targets = [row.target_label for row in rows]
        model_metrics = calculate_multiclass_metrics(
            [row.probabilities for row in rows], targets
        )
        persistence_metrics = calculate_multiclass_metrics(
            [row.persistence_probabilities for row in rows], targets
        )
        transition_metrics = calculate_multiclass_metrics(
            [row.transition_probabilities for row in rows], targets
        )
        horizon_summaries[horizon] = HorizonValidation(
            origin_count=len(rows),
            metrics=model_metrics,
            baseline_metrics={
                "persistence": persistence_metrics,
                "historical_transition": transition_metrics,
            },
            phase_support={phase: targets.count(phase) for phase in PHASES},
            recession_episodes=_count_recession_episodes(rows),
            complete_feature_ratio=sum(row.complete_feature_ratio for row in rows)
            / len(rows),
            probabilities_valid=all(_finite_simplex(row.probabilities) for row in rows),
        )

    return ValidationReport(
        horizons=horizon_summaries,
        predictions=tuple(predictions),
    )


def evaluate_publication_gate(
    report: ValidationReport,
    horizon: int,
) -> PublicationDecision:
    """Apply stable, horizon-specific evidence gates before publishing numbers."""

    resolved_horizon = int(horizon)
    if resolved_horizon not in report.horizons:
        return PublicationDecision(
            horizon_months=resolved_horizon,
            status="LIMITED",
            reason_codes=("MISSING_HORIZON_VALIDATION",),
        )
    validation = report.horizons[resolved_horizon]
    reasons: list[str] = []
    if validation.origin_count < READY_GATE["minimum_origins"]:
        reasons.append("INSUFFICIENT_ORIGINS")
    if validation.recession_episodes < READY_GATE["minimum_recession_episodes"]:
        reasons.append("INSUFFICIENT_RECESSION_EPISODES")
    if any(
        validation.phase_support.get(phase, 0) < READY_GATE["minimum_targets_per_phase"]
        for phase in PHASES
    ):
        reasons.append("INSUFFICIENT_PHASE_SUPPORT")
    if (
        not math.isfinite(validation.complete_feature_ratio)
        or validation.complete_feature_ratio
        < READY_GATE["minimum_complete_feature_ratio"]
    ):
        reasons.append("LOW_FEATURE_COVERAGE")
    ece = float(validation.metrics.get("ece", math.inf))
    if not math.isfinite(ece) or ece > READY_GATE["maximum_ece"]:
        reasons.append("CALIBRATION_ERROR")
    if not validation.probabilities_valid:
        reasons.append("INVALID_PROBABILITIES")

    baseline_rows = list(validation.baseline_metrics.values())
    model_brier = float(validation.metrics.get("brier_score", math.inf))
    model_log_loss = float(validation.metrics.get("log_loss", math.inf))
    best_brier = min(
        (float(row.get("brier_score", math.inf)) for row in baseline_rows),
        default=math.inf,
    )
    best_log_loss = min(
        (float(row.get("log_loss", math.inf)) for row in baseline_rows),
        default=math.inf,
    )
    if (
        not math.isfinite(model_brier)
        or not math.isfinite(model_log_loss)
        or model_brier > best_brier + 1e-12
        or model_log_loss > best_log_loss + 1e-12
    ):
        reasons.append("BASELINE_UNDERPERFORMANCE")

    return PublicationDecision(
        horizon_months=resolved_horizon,
        status="LIMITED" if reasons else "READY",
        reason_codes=tuple(reasons),
    )
