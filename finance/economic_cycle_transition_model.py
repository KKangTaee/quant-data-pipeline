"""Small deterministic weighted probability models for economic-cycle routes."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass
from typing import Sequence

import numpy as np
import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE


class ModelNotReadyError(RuntimeError):
    """Raised when an artifact or prediction input cannot produce probabilities."""


@dataclass(frozen=True)
class TransitionModelArtifact:
    """Serializable parameters and publication state for one transition task."""

    task: str
    feature_names: tuple[str, ...]
    classes: tuple[str, ...]
    means: dict[str, float]
    scales: dict[str, float]
    coefficients: dict[str, dict[str, float]]
    intercepts: dict[str, float]
    l2: float
    calibration: dict[str, float]
    publication_status: str
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _validate_columns(rows: pd.DataFrame, columns: Sequence[str]) -> None:
    missing = [column for column in columns if column not in rows]
    if missing:
        raise ModelNotReadyError(
            "MISSING_MODEL_FEATURE: " + ", ".join(sorted(missing))
        )


def _feature_matrix(
    rows: pd.DataFrame,
    feature_names: Sequence[str],
) -> np.ndarray:
    _validate_columns(rows, feature_names)
    return rows.loc[:, list(feature_names)].apply(
        pd.to_numeric, errors="coerce"
    ).to_numpy(dtype=float)


def _limited_artifact(
    *,
    task: str,
    feature_names: tuple[str, ...],
    classes: tuple[str, ...],
    l2: float,
    reason: str,
) -> TransitionModelArtifact:
    return TransitionModelArtifact(
        task=task,
        feature_names=feature_names,
        classes=classes,
        means={feature: 0.0 for feature in feature_names},
        scales={feature: 1.0 for feature in feature_names},
        coefficients={
            label: {feature: 0.0 for feature in feature_names}
            for label in classes
        },
        intercepts={label: 0.0 for label in classes},
        l2=float(l2),
        calibration=(
            {"slope": 1.0, "intercept": 0.0}
            if task == "pressure"
            else {"temperature": 1.0}
        ),
        publication_status="LIMITED",
        reason_codes=(reason,),
    )


def _training_arrays(
    rows: pd.DataFrame,
    feature_names: tuple[str, ...],
    *,
    target_column: str,
    weight_column: str,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    _validate_columns(rows, (*feature_names, target_column, weight_column))
    matrix = _feature_matrix(rows, feature_names)
    targets = rows[target_column].to_numpy()
    weights = pd.to_numeric(rows[weight_column], errors="coerce").to_numpy(
        dtype=float
    )
    return matrix, targets, weights


def _weighted_standardize(
    matrix: np.ndarray,
    weights: np.ndarray,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    normalized = weights / weights.sum()
    means = np.sum(matrix * normalized[:, None], axis=0)
    variance = np.sum(((matrix - means) ** 2) * normalized[:, None], axis=0)
    scales = np.sqrt(np.maximum(variance, 0.0))
    scales = np.where(scales > 1e-12, scales, 1.0)
    return (matrix - means) / scales, means, scales


def _sigmoid(logits: np.ndarray) -> np.ndarray:
    clipped = np.clip(logits, -35.0, 35.0)
    return 1.0 / (1.0 + np.exp(-clipped))


def _softmax(logits: np.ndarray) -> np.ndarray:
    shifted = np.clip(logits, -35.0, 35.0)
    shifted = shifted - shifted.max(axis=1, keepdims=True)
    exponentials = np.exp(shifted)
    return exponentials / exponentials.sum(axis=1, keepdims=True)


def _binary_objective(
    matrix: np.ndarray,
    targets: np.ndarray,
    weights: np.ndarray,
    coefficients: np.ndarray,
    intercept: float,
    l2: float,
) -> tuple[float, np.ndarray, float]:
    probabilities = _sigmoid(matrix @ coefficients + intercept)
    clipped = np.clip(probabilities, 1e-12, 1.0 - 1e-12)
    loss = -np.sum(
        weights
        * (
            targets * np.log(clipped)
            + (1.0 - targets) * np.log1p(-clipped)
        )
    ) + 0.5 * l2 * float(coefficients @ coefficients)
    residual = weights * (probabilities - targets)
    gradient = matrix.T @ residual + l2 * coefficients
    intercept_gradient = float(residual.sum())
    return float(loss), gradient, intercept_gradient


def _fit_binary_parameters(
    matrix: np.ndarray,
    targets: np.ndarray,
    weights: np.ndarray,
    *,
    l2: float,
    initial_coefficients: np.ndarray | None = None,
    initial_intercept: float | None = None,
    max_iterations: int = 800,
) -> tuple[np.ndarray, float]:
    coefficients = (
        np.zeros(matrix.shape[1], dtype=float)
        if initial_coefficients is None
        else initial_coefficients.astype(float, copy=True)
    )
    prevalence = float(np.sum(weights * targets))
    prevalence = min(max(prevalence, 1e-6), 1.0 - 1e-6)
    intercept = (
        math.log(prevalence / (1.0 - prevalence))
        if initial_intercept is None
        else float(initial_intercept)
    )
    for _ in range(max_iterations):
        loss, gradient, intercept_gradient = _binary_objective(
            matrix,
            targets,
            weights,
            coefficients,
            intercept,
            l2,
        )
        gradient_norm = math.sqrt(
            float(gradient @ gradient) + intercept_gradient**2
        )
        if gradient_norm <= 1e-7:
            break
        step = 1.0
        accepted = False
        for _ in range(40):
            candidate_coefficients = coefficients - step * gradient
            candidate_intercept = intercept - step * intercept_gradient
            candidate_loss, _, _ = _binary_objective(
                matrix,
                targets,
                weights,
                candidate_coefficients,
                candidate_intercept,
                l2,
            )
            if candidate_loss <= loss:
                coefficients = candidate_coefficients
                intercept = candidate_intercept
                accepted = True
                break
            step *= 0.5
        if not accepted:
            break
    return coefficients, intercept


def fit_binary_logit(
    rows: pd.DataFrame,
    feature_names: Sequence[str],
    *,
    target_column: str = "pressure_target",
    weight_column: str = "episode_weight",
    l2: float = 1.0,
) -> TransitionModelArtifact:
    """Fit a deterministic L2 weighted transition-pressure model."""

    features = tuple(feature_names)
    matrix, raw_targets, raw_weights = _training_arrays(
        rows,
        features,
        target_column=target_column,
        weight_column=weight_column,
    )
    targets = pd.to_numeric(
        pd.Series(raw_targets), errors="coerce"
    ).to_numpy(dtype=float)
    valid = np.isfinite(targets) & np.isfinite(raw_weights) & (raw_weights > 0.0)
    matrix = matrix[valid]
    targets = targets[valid]
    weights = raw_weights[valid]
    if (
        not len(targets)
        or not np.isfinite(matrix).all()
        or not np.isin(targets, (0.0, 1.0)).all()
    ):
        return _limited_artifact(
            task="pressure",
            feature_names=features,
            classes=("transition",),
            l2=l2,
            reason="NON_FINITE_TRAINING_SUPPORT",
        )
    if len(np.unique(targets)) < 2:
        return _limited_artifact(
            task="pressure",
            feature_names=features,
            classes=("transition",),
            l2=l2,
            reason="MISSING_CLASS_SUPPORT",
        )

    weights = weights / weights.sum()
    standardized, means, scales = _weighted_standardize(matrix, weights)
    coefficients, intercept = _fit_binary_parameters(
        standardized,
        targets,
        weights,
        l2=float(l2),
    )
    return TransitionModelArtifact(
        task="pressure",
        feature_names=features,
        classes=("transition",),
        means=dict(zip(features, means.astype(float), strict=True)),
        scales=dict(zip(features, scales.astype(float), strict=True)),
        coefficients={
            "transition": dict(
                zip(features, coefficients.astype(float), strict=True)
            )
        },
        intercepts={"transition": float(intercept)},
        l2=float(l2),
        calibration={"slope": 1.0, "intercept": 0.0},
        publication_status="READY",
        reason_codes=(),
    )


def _multiclass_objective(
    matrix: np.ndarray,
    target_indices: np.ndarray,
    weights: np.ndarray,
    coefficients: np.ndarray,
    intercepts: np.ndarray,
    l2: float,
) -> tuple[float, np.ndarray, np.ndarray]:
    probabilities = _softmax(matrix @ coefficients.T + intercepts)
    loss = -np.sum(
        weights
        * np.log(
            np.clip(
                probabilities[np.arange(len(target_indices)), target_indices],
                1e-12,
                1.0,
            )
        )
    ) + 0.5 * l2 * float(np.sum(coefficients**2))
    residual = probabilities.copy()
    residual[np.arange(len(target_indices)), target_indices] -= 1.0
    residual *= weights[:, None]
    coefficient_gradient = residual.T @ matrix + l2 * coefficients
    intercept_gradient = residual.sum(axis=0)
    return float(loss), coefficient_gradient, intercept_gradient


def _fit_multiclass_parameters(
    matrix: np.ndarray,
    target_indices: np.ndarray,
    weights: np.ndarray,
    *,
    class_count: int,
    l2: float,
    max_iterations: int = 1200,
) -> tuple[np.ndarray, np.ndarray]:
    coefficients = np.zeros((class_count, matrix.shape[1]), dtype=float)
    prevalence = np.asarray(
        [np.sum(weights[target_indices == index]) for index in range(class_count)]
    )
    intercepts = np.log(np.clip(prevalence, 1e-12, 1.0))
    intercepts -= intercepts.mean()
    for _ in range(max_iterations):
        loss, coefficient_gradient, intercept_gradient = _multiclass_objective(
            matrix,
            target_indices,
            weights,
            coefficients,
            intercepts,
            l2,
        )
        gradient_norm = math.sqrt(
            float(np.sum(coefficient_gradient**2))
            + float(np.sum(intercept_gradient**2))
        )
        if gradient_norm <= 1e-7:
            break
        step = 1.0
        accepted = False
        for _ in range(40):
            candidate_coefficients = coefficients - step * coefficient_gradient
            candidate_intercepts = intercepts - step * intercept_gradient
            candidate_loss, _, _ = _multiclass_objective(
                matrix,
                target_indices,
                weights,
                candidate_coefficients,
                candidate_intercepts,
                l2,
            )
            if candidate_loss <= loss:
                coefficients = candidate_coefficients
                intercepts = candidate_intercepts
                accepted = True
                break
            step *= 0.5
        if not accepted:
            break
    return coefficients, intercepts


def fit_multinomial_logit(
    rows: pd.DataFrame,
    feature_names: Sequence[str],
    *,
    target_column: str = "destination_target",
    weight_column: str = "episode_weight",
    l2: float = 1.0,
) -> TransitionModelArtifact:
    """Fit an unrestricted four-destination weighted multinomial model."""

    features = tuple(feature_names)
    classes = tuple(PHASE_SEQUENCE)
    matrix, raw_targets, raw_weights = _training_arrays(
        rows,
        features,
        target_column=target_column,
        weight_column=weight_column,
    )
    targets = np.asarray([str(value) for value in raw_targets], dtype=object)
    valid = (
        np.asarray([value in classes for value in targets])
        & np.isfinite(raw_weights)
        & (raw_weights > 0.0)
    )
    matrix = matrix[valid]
    targets = targets[valid]
    weights = raw_weights[valid]
    if not len(targets) or not np.isfinite(matrix).all():
        return _limited_artifact(
            task="destination",
            feature_names=features,
            classes=classes,
            l2=l2,
            reason="NON_FINITE_TRAINING_SUPPORT",
        )
    if set(targets) != set(classes):
        return _limited_artifact(
            task="destination",
            feature_names=features,
            classes=classes,
            l2=l2,
            reason="MISSING_CLASS_SUPPORT",
        )

    weights = weights / weights.sum()
    standardized, means, scales = _weighted_standardize(matrix, weights)
    class_index = {label: index for index, label in enumerate(classes)}
    target_indices = np.asarray([class_index[label] for label in targets], dtype=int)
    coefficients, intercepts = _fit_multiclass_parameters(
        standardized,
        target_indices,
        weights,
        class_count=len(classes),
        l2=float(l2),
    )
    return TransitionModelArtifact(
        task="destination",
        feature_names=features,
        classes=classes,
        means=dict(zip(features, means.astype(float), strict=True)),
        scales=dict(zip(features, scales.astype(float), strict=True)),
        coefficients={
            label: dict(
                zip(features, coefficients[index].astype(float), strict=True)
            )
            for index, label in enumerate(classes)
        },
        intercepts={
            label: float(intercepts[index])
            for index, label in enumerate(classes)
        },
        l2=float(l2),
        calibration={"temperature": 1.0},
        publication_status="READY",
        reason_codes=(),
    )


def _standardized_prediction_matrix(
    artifact: TransitionModelArtifact,
    rows: pd.DataFrame,
) -> np.ndarray:
    if artifact.publication_status != "READY":
        raise ModelNotReadyError(
            "MODEL_NOT_READY: " + ", ".join(artifact.reason_codes)
        )
    matrix = _feature_matrix(rows, artifact.feature_names)
    if not np.isfinite(matrix).all():
        raise ModelNotReadyError("NON_FINITE_MODEL_FEATURE")
    means = np.asarray([artifact.means[item] for item in artifact.feature_names])
    scales = np.asarray([artifact.scales[item] for item in artifact.feature_names])
    return (matrix - means) / scales


def predict_binary_probability(
    artifact: TransitionModelArtifact,
    rows: pd.DataFrame,
) -> np.ndarray:
    """Predict calibrated transition pressure for finite feature rows."""

    matrix = _standardized_prediction_matrix(artifact, rows)
    label = artifact.classes[0]
    coefficients = np.asarray(
        [artifact.coefficients[label][item] for item in artifact.feature_names]
    )
    logits = matrix @ coefficients + artifact.intercepts[label]
    calibration = artifact.calibration
    logits = (
        float(calibration.get("slope", 1.0)) * logits
        + float(calibration.get("intercept", 0.0))
    )
    return _sigmoid(logits)


def predict_destination_probabilities(
    artifact: TransitionModelArtifact,
    rows: pd.DataFrame,
    *,
    current_phases: Sequence[str] | None = None,
) -> tuple[dict[str, float], ...]:
    """Predict destination distributions, optionally conditional on leaving state."""

    matrix = _standardized_prediction_matrix(artifact, rows)
    classes = artifact.classes
    coefficients = np.asarray(
        [
            [artifact.coefficients[label][item] for item in artifact.feature_names]
            for label in classes
        ]
    )
    intercepts = np.asarray([artifact.intercepts[label] for label in classes])
    temperature = float(artifact.calibration.get("temperature", 1.0))
    if not math.isfinite(temperature) or temperature <= 0.0:
        raise ModelNotReadyError("INVALID_CALIBRATION")
    probabilities = _softmax((matrix @ coefficients.T + intercepts) / temperature)
    if current_phases is not None:
        if len(current_phases) != len(probabilities):
            raise ValueError("current_phases length must match rows")
        class_index = {label: index for index, label in enumerate(classes)}
        for row_index, phase in enumerate(current_phases):
            excluded = class_index.get(str(phase))
            if excluded is None:
                continue
            probabilities[row_index, excluded] = 0.0
            denominator = probabilities[row_index].sum()
            if denominator <= 0.0:
                raise ModelNotReadyError("INVALID_CONDITIONAL_PROBABILITY")
            probabilities[row_index] /= denominator
    return tuple(
        {
            label: float(probabilities[row_index, class_index])
            for class_index, label in enumerate(classes)
        }
        for row_index in range(len(probabilities))
    )


def fit_platt_scaler(
    probabilities: Sequence[float] | np.ndarray,
    labels: Sequence[float] | np.ndarray,
    weights: Sequence[float] | np.ndarray | None = None,
) -> dict[str, float]:
    """Fit binary calibration and retain identity if optimization cannot improve."""

    raw = np.asarray(probabilities, dtype=float)
    targets = np.asarray(labels, dtype=float)
    sample_weights = (
        np.ones(len(raw), dtype=float)
        if weights is None
        else np.asarray(weights, dtype=float)
    )
    valid = (
        np.isfinite(raw)
        & np.isfinite(targets)
        & np.isfinite(sample_weights)
        & (sample_weights > 0.0)
        & np.isin(targets, (0.0, 1.0))
    )
    raw = raw[valid]
    targets = targets[valid]
    sample_weights = sample_weights[valid]
    if not len(raw) or len(np.unique(targets)) < 2:
        return {"slope": 1.0, "intercept": 0.0}
    sample_weights /= sample_weights.sum()
    clipped = np.clip(raw, 1e-12, 1.0 - 1e-12)
    logits = np.log(clipped / (1.0 - clipped))[:, None]
    baseline_loss, _, _ = _binary_objective(
        logits,
        targets,
        sample_weights,
        np.asarray([1.0]),
        0.0,
        0.0,
    )
    coefficients, intercept = _fit_binary_parameters(
        logits,
        targets,
        sample_weights,
        l2=0.0,
        initial_coefficients=np.asarray([1.0]),
        initial_intercept=0.0,
    )
    calibrated_loss, _, _ = _binary_objective(
        logits,
        targets,
        sample_weights,
        coefficients,
        intercept,
        0.0,
    )
    if not math.isfinite(calibrated_loss) or calibrated_loss > baseline_loss:
        return {"slope": 1.0, "intercept": 0.0}
    return {"slope": float(coefficients[0]), "intercept": float(intercept)}


def fit_multiclass_temperature(
    probabilities: np.ndarray,
    labels: Sequence[int] | np.ndarray,
    weights: Sequence[float] | np.ndarray | None = None,
) -> dict[str, float]:
    """Select a deterministic positive temperature by weighted log loss."""

    raw = np.asarray(probabilities, dtype=float)
    target_indices = np.asarray(labels, dtype=int)
    if raw.ndim != 2 or len(raw) != len(target_indices) or not len(raw):
        return {"temperature": 1.0}
    sample_weights = (
        np.ones(len(raw), dtype=float)
        if weights is None
        else np.asarray(weights, dtype=float)
    )
    if (
        not np.isfinite(raw).all()
        or not np.isfinite(sample_weights).all()
        or (sample_weights <= 0.0).any()
        or (raw <= 0.0).any()
        or (target_indices < 0).any()
        or (target_indices >= raw.shape[1]).any()
    ):
        return {"temperature": 1.0}
    sample_weights /= sample_weights.sum()
    normalized = raw / raw.sum(axis=1, keepdims=True)
    logits = np.log(np.clip(normalized, 1e-12, 1.0))
    candidates = np.unique(
        np.concatenate(
            [np.asarray([1.0]), np.exp(np.linspace(math.log(0.25), math.log(20.0), 801))]
        )
    )
    best_temperature = 1.0
    best_loss = math.inf
    for temperature in candidates:
        calibrated = _softmax(logits / temperature)
        loss = -float(
            np.sum(
                sample_weights
                * np.log(
                    np.clip(
                        calibrated[np.arange(len(target_indices)), target_indices],
                        1e-12,
                        1.0,
                    )
                )
            )
        )
        if loss < best_loss:
            best_loss = loss
            best_temperature = float(temperature)
    return {"temperature": best_temperature}
