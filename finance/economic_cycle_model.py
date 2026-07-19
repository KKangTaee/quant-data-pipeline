"""Interpretable probabilistic regime models for economic-cycle horizons."""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from typing import Mapping, Sequence

import pandas as pd

PHASES = ("recovery", "expansion", "slowdown", "recession")
HORIZONS = (0, 1, 2)
CURRENT_FEATURES = (
    "activity_score",
    "labor_income_score",
    "activity_momentum_3m",
    "labor_income_momentum_3m",
)
FORECAST_FEATURES = (
    *CURRENT_FEATURES,
    "financial_leading_score",
    "inflation_policy_score",
)
NEXT_PHASE = {
    "recovery": "expansion",
    "expansion": "slowdown",
    "slowdown": "recession",
    "recession": "recovery",
}
DEFAULT_TEMPERATURE_GRID = tuple(round(0.50 + 0.05 * index, 2) for index in range(51))


class ModelNotReadyError(RuntimeError):
    """Raised when a LIMITED artifact is asked to publish probabilities."""


@dataclass(frozen=True)
class HorizonModelArtifact:
    """Serializable parameters for one direct forecast horizon."""

    horizon_months: int
    feature_names: tuple[str, ...]
    class_priors: dict[str, float]
    means: dict[str, dict[str, float]]
    variances: dict[str, dict[str, float]]
    phase_support: dict[str, int]
    minimum_variance: float
    publication_status: str
    reason_codes: tuple[str, ...] = ()
    temperature: float = 1.0
    trained_through: str | None = None
    model_version: str = "economic_cycle_gaussian_v1"
    transition_matrix: dict[str, dict[str, float]] = field(default_factory=dict)


def fit_horizon_model(
    features: pd.DataFrame,
    labels: Sequence[object] | pd.Series,
    *,
    horizon_months: int,
    minimum_variance: float = 0.05,
) -> HorizonModelArtifact:
    """Fit a diagonal Gaussian model without sharing information across horizons."""

    horizon = int(horizon_months)
    if horizon not in HORIZONS:
        raise ValueError(f"Unsupported horizon: {horizon}")
    feature_names = tuple(str(column) for column in features.columns)
    if not feature_names:
        raise ValueError("At least one feature is required")
    if horizon == 0:
        invalid = [name for name in feature_names if name not in CURRENT_FEATURES]
        if invalid:
            raise ValueError(
                f"horizon 0 accepts only real-economy features; invalid: {', '.join(invalid)}"
            )
    if len(features) != len(labels):
        raise ValueError("features and labels must have identical row counts")
    minimum_variance = float(minimum_variance)
    if not math.isfinite(minimum_variance) or minimum_variance <= 0:
        raise ValueError("minimum_variance must be positive and finite")

    numeric = features.loc[:, list(feature_names)].apply(pd.to_numeric, errors="coerce")
    label_series = pd.Series(labels, index=features.index, dtype="object")
    finite_mask = numeric.notna().all(axis=1) & numeric.apply(
        lambda column: column.map(
            lambda value: math.isfinite(float(value)) if pd.notna(value) else False
        )
    ).all(axis=1)
    valid_label_mask = label_series.isin(PHASES)
    numeric = numeric.loc[finite_mask & valid_label_mask]
    label_series = label_series.loc[numeric.index]

    support = {phase: int((label_series == phase).sum()) for phase in PHASES}
    total = sum(support.values())
    priors = {phase: (support[phase] / total if total else 0.0) for phase in PHASES}
    means: dict[str, dict[str, float]] = {}
    variances: dict[str, dict[str, float]] = {}
    for phase in PHASES:
        phase_rows = numeric.loc[label_series == phase]
        if phase_rows.empty:
            means[phase] = {}
            variances[phase] = {}
            continue
        means[phase] = {name: float(phase_rows[name].mean()) for name in feature_names}
        variances[phase] = {
            name: max(float(phase_rows[name].var(ddof=0)), minimum_variance)
            for name in feature_names
        }

    missing_phase = any(support[phase] == 0 for phase in PHASES)
    return HorizonModelArtifact(
        horizon_months=horizon,
        feature_names=feature_names,
        class_priors=priors,
        means=means,
        variances=variances,
        phase_support=support,
        minimum_variance=minimum_variance,
        publication_status="LIMITED" if missing_phase else "READY",
        reason_codes=("MISSING_PHASE_SUPPORT",) if missing_phase else (),
    )


def _feature_log_likelihood(
    artifact: HorizonModelArtifact,
    phase: str,
    feature_name: str,
    value: float,
) -> float:
    mean = artifact.means[phase][feature_name]
    variance = max(artifact.variances[phase][feature_name], artifact.minimum_variance)
    delta = value - mean
    return -0.5 * (math.log(2.0 * math.pi * variance) + (delta * delta / variance))


def _row_values(
    artifact: HorizonModelArtifact,
    feature_row: Mapping[str, object],
) -> dict[str, float]:
    values: dict[str, float] = {}
    for name in artifact.feature_names:
        try:
            value = float(feature_row[name])
        except (KeyError, TypeError, ValueError) as exc:
            raise ValueError(f"Missing or invalid model feature: {name}") from exc
        if not math.isfinite(value):
            raise ValueError(f"Model feature must be finite: {name}")
        values[name] = value
    return values


def _phase_log_scores(
    artifact: HorizonModelArtifact,
    values: Mapping[str, float],
    *,
    transition_prior: Mapping[str, float] | None = None,
) -> dict[str, float]:
    scores: dict[str, float] = {}
    for phase in PHASES:
        prior = (
            float(transition_prior[phase])
            if transition_prior is not None
            else artifact.class_priors[phase]
        )
        log_score = math.log(max(prior, 1e-12))
        for name in artifact.feature_names:
            log_score += _feature_log_likelihood(
                artifact, phase, name, float(values[name])
            )
        scores[phase] = log_score
    return scores


def predict_phase_probabilities(
    artifact: HorizonModelArtifact,
    feature_row: Mapping[str, object],
    *,
    transition_prior: Mapping[str, float] | None = None,
    temperature: float | None = None,
) -> dict[str, float]:
    """Return a stable four-phase probability simplex for one feature row."""

    if artifact.publication_status != "READY":
        raise ModelNotReadyError(
            f"Artifact is {artifact.publication_status}: {artifact.reason_codes}"
        )
    values = _row_values(artifact, feature_row)
    scores = _phase_log_scores(artifact, values, transition_prior=transition_prior)
    resolved_temperature = float(
        artifact.temperature if temperature is None else temperature
    )
    if not math.isfinite(resolved_temperature) or resolved_temperature <= 0:
        raise ValueError("temperature must be positive and finite")
    scaled = {phase: score / resolved_temperature for phase, score in scores.items()}
    maximum = max(scaled.values())
    weights = {phase: math.exp(score - maximum) for phase, score in scaled.items()}
    denominator = sum(weights.values())
    probabilities = {phase: weights[phase] / denominator for phase in PHASES}
    # Normalize once more to absorb the final floating-point division residual.
    total = sum(probabilities.values())
    return {phase: probabilities[phase] / total for phase in PHASES}


def explain_phase_prediction(
    artifact: HorizonModelArtifact,
    feature_row: Mapping[str, object],
) -> dict[str, object]:
    """Explain winner-vs-runner evidence as feature log-likelihood differences."""

    values = _row_values(artifact, feature_row)
    probabilities = predict_phase_probabilities(artifact, values)
    ordered = sorted(PHASES, key=lambda phase: probabilities[phase], reverse=True)
    winner, runner_up = ordered[:2]
    contributions = {
        name: _feature_log_likelihood(artifact, winner, name, values[name])
        - _feature_log_likelihood(artifact, runner_up, name, values[name])
        for name in artifact.feature_names
    }
    return {
        "winner": winner,
        "runner_up": runner_up,
        "probabilities": probabilities,
        "contributions": contributions,
        "feature_log_odds_difference": sum(contributions.values()),
    }


def estimate_transition_matrix(
    labels: Sequence[object],
    *,
    alpha_same: float = 3.0,
    alpha_next: float = 2.0,
    alpha_other: float = 0.5,
) -> dict[str, dict[str, float]]:
    """Estimate transitions with a non-zero prior favoring same/next phases."""

    alphas = (float(alpha_same), float(alpha_next), float(alpha_other))
    if any(not math.isfinite(value) or value <= 0 for value in alphas):
        raise ValueError("transition prior alphas must be positive and finite")
    counts: dict[str, dict[str, float]] = {}
    for origin in PHASES:
        counts[origin] = {
            target: (
                float(alpha_same)
                if target == origin
                else (
                    float(alpha_next)
                    if target == NEXT_PHASE[origin]
                    else float(alpha_other)
                )
            )
            for target in PHASES
        }
    normalized_labels = [str(label) for label in labels]
    for origin, target in zip(normalized_labels, normalized_labels[1:], strict=False):
        if origin in PHASES and target in PHASES:
            counts[origin][target] += 1.0
    return {
        origin: {
            target: counts[origin][target] / sum(counts[origin].values())
            for target in PHASES
        }
        for origin in PHASES
    }


def fit_forecast_models(
    feature_panel: pd.DataFrame,
    labels: Sequence[object] | pd.Series,
    *,
    minimum_variance: float = 0.05,
) -> dict[int, HorizonModelArtifact]:
    """Fit h0/h1/h2 against direct target labels rather than matrix powers."""

    label_series = pd.Series(labels, index=feature_panel.index, dtype="object")
    models: dict[int, HorizonModelArtifact] = {}
    for horizon in HORIZONS:
        feature_names = CURRENT_FEATURES if horizon == 0 else FORECAST_FEATURES
        missing = [name for name in feature_names if name not in feature_panel]
        if missing:
            raise ValueError(
                f"Missing horizon {horizon} features: {', '.join(missing)}"
            )
        targets = label_series.shift(-horizon) if horizon else label_series
        valid = targets.notna()
        models[horizon] = fit_horizon_model(
            feature_panel.loc[valid, list(feature_names)].reset_index(drop=True),
            targets.loc[valid].reset_index(drop=True),
            horizon_months=horizon,
            minimum_variance=minimum_variance,
        )
    return models


def blend_likelihood_and_transition(
    likelihood: Mapping[str, float],
    transition_prior: Mapping[str, float],
    *,
    likelihood_weight: float = 0.7,
) -> dict[str, float]:
    """Combine model evidence and transition context in stable log space."""

    weight = float(likelihood_weight)
    if not math.isfinite(weight) or not 0.0 <= weight <= 1.0:
        raise ValueError("likelihood_weight must be between 0 and 1")
    log_scores = {
        phase: weight * math.log(max(float(likelihood[phase]), 1e-300))
        + (1.0 - weight) * math.log(max(float(transition_prior[phase]), 1e-300))
        for phase in PHASES
    }
    maximum = max(log_scores.values())
    unnormalized = {phase: math.exp(log_scores[phase] - maximum) for phase in PHASES}
    total = sum(unnormalized.values())
    return {phase: unnormalized[phase] / total for phase in PHASES}


def apply_temperature(
    probabilities: Mapping[str, float],
    temperature: float,
) -> dict[str, float]:
    """Calibrate one probability row while preserving phase order and rank."""

    resolved_temperature = float(temperature)
    if not math.isfinite(resolved_temperature) or resolved_temperature <= 0:
        raise ValueError("temperature must be positive and finite")
    values = {phase: float(probabilities[phase]) for phase in PHASES}
    if any(not math.isfinite(value) or value < 0 for value in values.values()):
        raise ValueError("probabilities must be finite and non-negative")
    total = sum(values.values())
    if total <= 0:
        raise ValueError("probabilities must contain positive mass")
    normalized = {phase: values[phase] / total for phase in PHASES}
    log_scores = {
        phase: math.log(max(normalized[phase], 1e-300)) / resolved_temperature
        for phase in PHASES
    }
    maximum = max(log_scores.values())
    weights = {phase: math.exp(log_scores[phase] - maximum) for phase in PHASES}
    denominator = sum(weights.values())
    return {phase: weights[phase] / denominator for phase in PHASES}


def fit_temperature(
    probability_rows: Sequence[Mapping[str, float]],
    target_labels: Sequence[object],
    *,
    grid: Sequence[float] | None = None,
) -> float:
    """Choose the deterministic temperature minimizing OOF multiclass log loss."""

    rows = list(probability_rows)
    targets = [str(target) for target in target_labels]
    if not rows or len(rows) != len(targets):
        raise ValueError(
            "probability_rows and target_labels must be non-empty and aligned"
        )
    if any(target not in PHASES for target in targets):
        raise ValueError("target_labels must use the approved phase vocabulary")
    candidates = sorted(
        set(float(value) for value in (grid or DEFAULT_TEMPERATURE_GRID))
    )
    if not candidates or any(
        not math.isfinite(value) or value <= 0 for value in candidates
    ):
        raise ValueError("temperature grid must contain positive finite values")

    best_temperature = candidates[0]
    best_loss = math.inf
    for candidate in candidates:
        calibrated = [apply_temperature(row, candidate) for row in rows]
        loss = -sum(
            math.log(max(row[target], 1e-15))
            for row, target in zip(calibrated, targets, strict=True)
        ) / len(targets)
        if loss < best_loss - 1e-15:
            best_loss = loss
            best_temperature = candidate
    return best_temperature
