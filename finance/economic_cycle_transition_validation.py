"""Chronological episode validation and publication gates for cycle forecasts."""

from __future__ import annotations

import math
from collections import Counter
from dataclasses import asdict, dataclass, replace
from typing import Mapping, Sequence

import numpy as np
import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_dataset import TransitionDataset
from finance.economic_cycle_transition_model import (
    TransitionModelArtifact,
    fit_binary_logit,
    fit_multiclass_temperature,
    fit_multinomial_logit,
    fit_platt_scaler,
    predict_binary_probability,
    predict_destination_probabilities,
)


@dataclass(frozen=True)
class ProbabilityMetrics:
    brier: float
    log_loss: float
    ece: float

    def to_dict(self) -> dict[str, float]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionPrediction:
    task: str
    forecast_origin: pd.Timestamp
    scoring_episode_id: int
    training_episode_max: int
    training_target_known_through: pd.Timestamp
    actual: float | str
    model_probabilities: dict[str, float]
    baseline_probabilities: dict[str, float | dict[str, float]]
    weight: float
    current_phase: str


@dataclass(frozen=True)
class TransitionValidationReport:
    pressure_predictions: tuple[TransitionPrediction, ...]
    destination_predictions: tuple[TransitionPrediction, ...]
    pressure_metrics: ProbabilityMetrics
    pressure_baseline_metrics: dict[str, ProbabilityMetrics]
    destination_metrics: ProbabilityMetrics
    destination_baseline_metrics: dict[str, ProbabilityMetrics]
    pressure_event_count: int
    pressure_holdout_has_both: bool
    destination_event_count: int
    destination_event_counts: dict[str, int]
    destination_final_25_counts: dict[str, int]
    invalid_probability_count: int

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TransitionPublicationDecision:
    status: str
    reason_codes: tuple[str, ...]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def _normalized_weights(weights: np.ndarray) -> np.ndarray:
    parsed = np.asarray(weights, dtype=float)
    total = float(parsed.sum())
    if not len(parsed) or not np.isfinite(parsed).all() or total <= 0.0:
        raise ValueError("positive finite weights are required")
    return parsed / total


def _ece(
    confidence: np.ndarray,
    correctness: np.ndarray,
    weights: np.ndarray,
    *,
    bins: int,
) -> float:
    normalized = _normalized_weights(weights)
    result = 0.0
    edges = np.linspace(0.0, 1.0, bins + 1)
    for index in range(bins):
        lower = edges[index]
        upper = edges[index + 1]
        selected = (
            (confidence >= lower) & (confidence <= upper)
            if index == bins - 1
            else (confidence >= lower) & (confidence < upper)
        )
        if not selected.any():
            continue
        bin_weight = float(normalized[selected].sum())
        local = normalized[selected] / bin_weight
        predicted = float(np.sum(local * confidence[selected]))
        observed = float(np.sum(local * correctness[selected]))
        result += bin_weight * abs(predicted - observed)
    return result


def weighted_binary_metrics(
    probabilities: np.ndarray,
    targets: np.ndarray,
    weights: np.ndarray,
    *,
    bins: int = 10,
) -> ProbabilityMetrics:
    predicted = np.asarray(probabilities, dtype=float)
    actual = np.asarray(targets, dtype=float)
    normalized = _normalized_weights(np.asarray(weights, dtype=float))
    if len(predicted) != len(actual) or len(actual) != len(normalized):
        raise ValueError("probabilities, targets, and weights must align")
    clipped = np.clip(predicted, 1e-12, 1.0 - 1e-12)
    brier = float(np.sum(normalized * (predicted - actual) ** 2))
    log_loss = -float(
        np.sum(
            normalized
            * (actual * np.log(clipped) + (1.0 - actual) * np.log1p(-clipped))
        )
    )
    return ProbabilityMetrics(
        brier=brier,
        log_loss=log_loss,
        ece=_ece(predicted, actual, np.asarray(weights, dtype=float), bins=bins),
    )


def weighted_multiclass_metrics(
    probabilities: np.ndarray,
    target_indices: np.ndarray,
    weights: np.ndarray,
    *,
    bins: int = 10,
) -> ProbabilityMetrics:
    predicted = np.asarray(probabilities, dtype=float)
    actual = np.asarray(target_indices, dtype=int)
    normalized = _normalized_weights(np.asarray(weights, dtype=float))
    if predicted.ndim != 2 or len(predicted) != len(actual):
        raise ValueError("multiclass probabilities and targets must align")
    one_hot = np.zeros_like(predicted)
    one_hot[np.arange(len(actual)), actual] = 1.0
    brier = float(np.sum(normalized * np.sum((predicted - one_hot) ** 2, axis=1)))
    selected = np.clip(predicted[np.arange(len(actual)), actual], 1e-12, 1.0)
    log_loss = -float(np.sum(normalized * np.log(selected)))
    predicted_class = predicted.argmax(axis=1)
    confidence = predicted.max(axis=1)
    correctness = (predicted_class == actual).astype(float)
    return ProbabilityMetrics(
        brier=brier,
        log_loss=log_loss,
        ece=_ece(
            confidence,
            correctness,
            np.asarray(weights, dtype=float),
            bins=bins,
        ),
    )


def _empty_metrics() -> ProbabilityMetrics:
    return ProbabilityMetrics(brier=math.inf, log_loss=math.inf, ece=math.inf)


def _eligible_training_rows(
    rows: pd.DataFrame,
    *,
    episode_id: int,
    scoring_origin: pd.Timestamp,
    target_column: str,
    known_at_column: str,
) -> pd.DataFrame:
    known_at = pd.to_datetime(rows[known_at_column], errors="coerce")
    targets = rows[target_column]
    mask = (
        rows["eligible"].astype(bool)
        & targets.notna()
        & known_at.notna()
        & (known_at < scoring_origin)
        & (pd.to_numeric(rows["episode_id"], errors="coerce") < episode_id)
    )
    return rows.loc[mask].copy()


def _select_l2(
    training: pd.DataFrame,
    feature_names: tuple[str, ...],
    *,
    task: str,
    candidates: Sequence[float],
) -> float:
    episode_ids = sorted(int(value) for value in training["episode_id"].unique())
    if len(candidates) == 1 or len(episode_ids) < 5:
        return float(candidates[0])
    validation_count = max(1, int(math.ceil(len(episode_ids) * 0.20)))
    validation_ids = set(episode_ids[-validation_count:])
    fit_rows = training.loc[~training["episode_id"].isin(validation_ids)]
    validation_rows = training.loc[training["episode_id"].isin(validation_ids)]
    best = float(candidates[0])
    best_loss = math.inf
    for candidate in candidates:
        if task == "pressure":
            artifact = fit_binary_logit(fit_rows, feature_names, l2=float(candidate))
            if artifact.publication_status != "READY":
                continue
            probabilities = predict_binary_probability(artifact, validation_rows)
            labels = validation_rows["pressure_target"].to_numpy(dtype=float)
            metrics = weighted_binary_metrics(
                probabilities,
                labels,
                validation_rows["episode_weight"].to_numpy(dtype=float),
            )
        else:
            artifact = fit_multinomial_logit(
                fit_rows,
                feature_names,
                l2=float(candidate),
            )
            if artifact.publication_status != "READY":
                continue
            distributions = predict_destination_probabilities(
                artifact,
                validation_rows,
                current_phases=tuple(validation_rows["confirmed_phase"].astype(str)),
            )
            probabilities = np.asarray(
                [[item[phase] for phase in PHASE_SEQUENCE] for item in distributions]
            )
            class_index = {phase: index for index, phase in enumerate(PHASE_SEQUENCE)}
            labels = np.asarray(
                [class_index[str(value)] for value in validation_rows["destination_target"]]
            )
            metrics = weighted_multiclass_metrics(
                probabilities,
                labels,
                validation_rows["episode_weight"].to_numpy(dtype=float),
            )
        if metrics.log_loss < best_loss:
            best_loss = metrics.log_loss
            best = float(candidate)
    return best


def select_transition_l2(
    training: pd.DataFrame,
    feature_names: Sequence[str],
    *,
    task: str,
    candidates: Sequence[float] = (0.01, 0.1, 1.0, 10.0),
) -> float:
    """Select the production regularization with the validation contract."""

    if task not in {"pressure", "destination"}:
        raise ValueError(f"Unsupported transition task: {task}")
    return _select_l2(
        training,
        tuple(feature_names),
        task=task,
        candidates=candidates,
    )


def _duration_bucket(value: object) -> str:
    duration = int(float(value))
    if duration <= 1:
        return "1"
    if duration <= 3:
        return "2-3"
    if duration <= 6:
        return "4-6"
    return "7+"


def _pressure_baselines(
    training: pd.DataFrame,
    scoring: pd.DataFrame,
) -> tuple[np.ndarray, np.ndarray]:
    weights = training["episode_weight"].to_numpy(dtype=float)
    labels = training["pressure_target"].to_numpy(dtype=float)
    total = float(weights.sum())
    global_rate = (float(np.sum(weights * labels)) + 1.0) / (total + 2.0)
    global_probabilities = np.full(len(scoring), global_rate, dtype=float)

    training_buckets = training["phase_duration"].map(_duration_bucket)
    hazard: list[float] = []
    for duration in scoring["phase_duration"]:
        selected = training_buckets == _duration_bucket(duration)
        local_weights = weights[selected.to_numpy()]
        local_labels = labels[selected.to_numpy()]
        local_total = float(local_weights.sum())
        hazard.append(
            (float(np.sum(local_weights * local_labels)) + 1.0)
            / (local_total + 2.0)
        )
    return global_probabilities, np.asarray(hazard, dtype=float)


def _conditional_distribution(
    counts: Mapping[str, float],
    current_phase: str,
) -> dict[str, float]:
    values = {
        phase: (0.0 if phase == current_phase else float(counts.get(phase, 0.0)))
        for phase in PHASE_SEQUENCE
    }
    total = sum(values.values())
    if total <= 0.0:
        alternatives = [phase for phase in PHASE_SEQUENCE if phase != current_phase]
        return {
            phase: (1.0 / len(alternatives) if phase in alternatives else 0.0)
            for phase in PHASE_SEQUENCE
        }
    return {phase: values[phase] / total for phase in PHASE_SEQUENCE}


def _destination_baselines(
    training: pd.DataFrame,
    scoring: pd.DataFrame,
) -> tuple[tuple[dict[str, float], ...], tuple[dict[str, float], ...]]:
    frequencies: list[dict[str, float]] = []
    fixed_routes: list[dict[str, float]] = []
    phases = tuple(PHASE_SEQUENCE)
    for row in scoring.to_dict(orient="records"):
        current = str(row["confirmed_phase"])
        selected = training.loc[training["confirmed_phase"] == current]
        weighted_counts = {phase: 1.0 for phase in phases}
        for training_row in selected.to_dict(orient="records"):
            destination = str(training_row["destination_target"])
            if destination in weighted_counts:
                weighted_counts[destination] += float(training_row["episode_weight"])
        frequencies.append(_conditional_distribution(weighted_counts, current))

        sample_size = max(float(training["episode_weight"].sum()), 1.0)
        next_phase = phases[(phases.index(current) + 1) % len(phases)]
        route_counts = {phase: 1.0 for phase in phases}
        route_counts[next_phase] += sample_size
        fixed_routes.append(_conditional_distribution(route_counts, current))
    return tuple(frequencies), tuple(fixed_routes)


def _with_binary_calibration(
    artifact: TransitionModelArtifact,
    raw_probabilities: Sequence[float],
    labels: Sequence[float],
    weights: Sequence[float],
) -> TransitionModelArtifact:
    if not raw_probabilities:
        return artifact
    return replace(
        artifact,
        calibration=fit_platt_scaler(raw_probabilities, labels, weights),
    )


def _with_destination_calibration(
    artifact: TransitionModelArtifact,
    raw_probabilities: Sequence[Sequence[float]],
    labels: Sequence[int],
    weights: Sequence[float],
) -> TransitionModelArtifact:
    if not raw_probabilities:
        return artifact
    return replace(
        artifact,
        calibration=fit_multiclass_temperature(
            np.asarray(raw_probabilities, dtype=float),
            np.asarray(labels, dtype=int),
            np.asarray(weights, dtype=float),
        ),
    )


def _metrics_from_pressure_records(
    records: Sequence[TransitionPrediction],
) -> tuple[ProbabilityMetrics, dict[str, ProbabilityMetrics]]:
    if not records:
        return _empty_metrics(), {
            "global_rate": _empty_metrics(),
            "duration_hazard": _empty_metrics(),
        }
    labels = np.asarray([float(item.actual) for item in records])
    weights = np.asarray([item.weight for item in records])
    model = np.asarray([item.model_probabilities["transition"] for item in records])
    baselines = {
        name: weighted_binary_metrics(
            np.asarray([float(item.baseline_probabilities[name]) for item in records]),
            labels,
            weights,
        )
        for name in ("global_rate", "duration_hazard")
    }
    return weighted_binary_metrics(model, labels, weights), baselines


def _metrics_from_destination_records(
    records: Sequence[TransitionPrediction],
) -> tuple[ProbabilityMetrics, dict[str, ProbabilityMetrics]]:
    if not records:
        return _empty_metrics(), {
            "phase_frequency": _empty_metrics(),
            "fixed_cycle": _empty_metrics(),
        }
    class_index = {phase: index for index, phase in enumerate(PHASE_SEQUENCE)}
    labels = np.asarray([class_index[str(item.actual)] for item in records])
    weights = np.asarray([item.weight for item in records])

    def matrix_for(name: str | None) -> np.ndarray:
        distributions = (
            [item.model_probabilities for item in records]
            if name is None
            else [item.baseline_probabilities[name] for item in records]
        )
        return np.asarray(
            [[distribution[phase] for phase in PHASE_SEQUENCE] for distribution in distributions],
            dtype=float,
        )

    baselines = {
        name: weighted_multiclass_metrics(matrix_for(name), labels, weights)
        for name in ("phase_frequency", "fixed_cycle")
    }
    return weighted_multiclass_metrics(matrix_for(None), labels, weights), baselines


def _invalid_probability_count(
    pressure: Sequence[TransitionPrediction],
    destination: Sequence[TransitionPrediction],
) -> int:
    invalid = 0
    for item in pressure:
        distributions = [item.model_probabilities, item.baseline_probabilities]
        values: list[float] = []
        for distribution in distributions:
            for value in distribution.values():
                if isinstance(value, dict):
                    values.extend(float(nested) for nested in value.values())
                else:
                    values.append(float(value))
        if any(not math.isfinite(value) or value <= 0.0 or value >= 1.0 for value in values):
            invalid += 1
    for item in destination:
        distributions = [item.model_probabilities]
        distributions.extend(
            value
            for value in item.baseline_probabilities.values()
            if isinstance(value, dict)
        )
        if any(
            any(not math.isfinite(float(value)) or float(value) < 0.0 or float(value) > 1.0 for value in distribution.values())
            or abs(sum(float(value) for value in distribution.values()) - 1.0) > 1e-9
            for distribution in distributions
        ):
            invalid += 1
    return invalid


def run_transition_validation(
    dataset: TransitionDataset,
    *,
    initial_training_events: int = 40,
    l2_candidates: Sequence[float] = (0.01, 0.1, 1.0, 10.0),
) -> TransitionValidationReport:
    """Score complete future episodes using only targets known before each fold."""

    rows = dataset.rows.copy()
    rows["forecast_origin"] = pd.to_datetime(rows["forecast_origin"], errors="coerce")
    rows["target_known_at"] = pd.to_datetime(rows["target_known_at"], errors="coerce")
    rows["destination_known_at"] = pd.to_datetime(
        rows["destination_known_at"], errors="coerce"
    )
    rows = rows.dropna(subset=["forecast_origin", "episode_id"]).sort_values(
        "forecast_origin", kind="stable"
    )
    episode_ids = sorted(int(value) for value in rows["episode_id"].unique())

    pressure_records: list[TransitionPrediction] = []
    destination_records: list[TransitionPrediction] = []
    pressure_raw_oof: list[float] = []
    pressure_oof_labels: list[float] = []
    pressure_oof_weights: list[float] = []
    destination_raw_oof: list[list[float]] = []
    destination_oof_labels: list[int] = []
    destination_oof_weights: list[float] = []
    class_index = {phase: index for index, phase in enumerate(PHASE_SEQUENCE)}

    for episode_id in episode_ids:
        if episode_id < initial_training_events:
            continue
        scoring_all = rows.loc[rows["episode_id"] == episode_id]
        if scoring_all.empty:
            continue
        scoring_origin = pd.Timestamp(scoring_all["forecast_origin"].min())

        pressure_training = _eligible_training_rows(
            rows,
            episode_id=episode_id,
            scoring_origin=scoring_origin,
            target_column="pressure_target",
            known_at_column="target_known_at",
        )
        pressure_scoring = scoring_all.loc[
            scoring_all["eligible"].astype(bool)
            & scoring_all["pressure_target"].notna()
        ]
        if not pressure_training.empty and not pressure_scoring.empty:
            l2 = _select_l2(
                pressure_training,
                dataset.feature_names,
                task="pressure",
                candidates=l2_candidates,
            )
            raw_artifact = fit_binary_logit(
                pressure_training,
                dataset.feature_names,
                l2=l2,
            )
            if raw_artifact.publication_status == "READY":
                raw = predict_binary_probability(raw_artifact, pressure_scoring)
                artifact = _with_binary_calibration(
                    raw_artifact,
                    pressure_raw_oof,
                    pressure_oof_labels,
                    pressure_oof_weights,
                )
                calibrated = predict_binary_probability(artifact, pressure_scoring)
                global_rate, duration_hazard = _pressure_baselines(
                    pressure_training,
                    pressure_scoring,
                )
                training_known = pd.Timestamp(
                    pressure_training["target_known_at"].max()
                )
                training_episode_max = int(pressure_training["episode_id"].max())
                for position, (_, row) in enumerate(pressure_scoring.iterrows()):
                    label = float(row["pressure_target"])
                    weight = float(row["episode_weight"])
                    pressure_records.append(
                        TransitionPrediction(
                            task="pressure",
                            forecast_origin=pd.Timestamp(row["forecast_origin"]),
                            scoring_episode_id=episode_id,
                            training_episode_max=training_episode_max,
                            training_target_known_through=training_known,
                            actual=label,
                            model_probabilities={
                                "transition": float(calibrated[position])
                            },
                            baseline_probabilities={
                                "global_rate": float(global_rate[position]),
                                "duration_hazard": float(duration_hazard[position]),
                            },
                            weight=weight,
                            current_phase=str(row["confirmed_phase"]),
                        )
                    )
                    pressure_raw_oof.append(float(raw[position]))
                    pressure_oof_labels.append(label)
                    pressure_oof_weights.append(weight)

        destination_training = _eligible_training_rows(
            rows,
            episode_id=episode_id,
            scoring_origin=scoring_origin,
            target_column="destination_target",
            known_at_column="destination_known_at",
        )
        destination_scoring = scoring_all.loc[
            scoring_all["eligible"].astype(bool)
            & scoring_all["destination_target"].notna()
        ]
        if not destination_training.empty and not destination_scoring.empty:
            l2 = _select_l2(
                destination_training,
                dataset.feature_names,
                task="destination",
                candidates=l2_candidates,
            )
            raw_artifact = fit_multinomial_logit(
                destination_training,
                dataset.feature_names,
                l2=l2,
            )
            if raw_artifact.publication_status == "READY":
                current = tuple(destination_scoring["confirmed_phase"].astype(str))
                raw_distributions = predict_destination_probabilities(
                    raw_artifact,
                    destination_scoring,
                )
                raw_matrix = np.asarray(
                    [
                        [distribution[phase] for phase in PHASE_SEQUENCE]
                        for distribution in raw_distributions
                    ]
                )
                artifact = _with_destination_calibration(
                    raw_artifact,
                    destination_raw_oof,
                    destination_oof_labels,
                    destination_oof_weights,
                )
                calibrated = predict_destination_probabilities(
                    artifact,
                    destination_scoring,
                    current_phases=current,
                )
                phase_frequency, fixed_cycle = _destination_baselines(
                    destination_training,
                    destination_scoring,
                )
                training_known = pd.Timestamp(
                    destination_training["destination_known_at"].max()
                )
                training_episode_max = int(destination_training["episode_id"].max())
                for position, (_, row) in enumerate(destination_scoring.iterrows()):
                    label = str(row["destination_target"])
                    weight = float(row["episode_weight"])
                    destination_records.append(
                        TransitionPrediction(
                            task="destination",
                            forecast_origin=pd.Timestamp(row["forecast_origin"]),
                            scoring_episode_id=episode_id,
                            training_episode_max=training_episode_max,
                            training_target_known_through=training_known,
                            actual=label,
                            model_probabilities=calibrated[position],
                            baseline_probabilities={
                                "phase_frequency": phase_frequency[position],
                                "fixed_cycle": fixed_cycle[position],
                            },
                            weight=weight,
                            current_phase=str(row["confirmed_phase"]),
                        )
                    )
                    destination_raw_oof.append(raw_matrix[position].tolist())
                    destination_oof_labels.append(class_index[label])
                    destination_oof_weights.append(weight)

    pressure_metrics, pressure_baselines = _metrics_from_pressure_records(
        pressure_records
    )
    destination_metrics, destination_baselines = _metrics_from_destination_records(
        destination_records
    )
    pressure_episode_labels: dict[int, set[float]] = {}
    for record in pressure_records:
        pressure_episode_labels.setdefault(record.scoring_episode_id, set()).add(
            float(record.actual)
        )
    pressure_events = sum(1 for labels in pressure_episode_labels.values() if 1.0 in labels)
    ordered_pressure_episodes = sorted(pressure_episode_labels)
    blocks = [item for item in np.array_split(ordered_pressure_episodes, 4) if len(item)]
    holdout_has_both = bool(blocks) and all(
        {label for episode in block for label in pressure_episode_labels[int(episode)]}
        == {0.0, 1.0}
        for block in blocks
    )

    destination_by_episode: dict[int, str] = {}
    for record in destination_records:
        destination_by_episode.setdefault(
            record.scoring_episode_id,
            str(record.actual),
        )
    counts = Counter(destination_by_episode.values())
    ordered_destination = sorted(destination_by_episode)
    final_count = int(math.ceil(len(ordered_destination) * 0.25))
    final_episodes = ordered_destination[-final_count:] if final_count else []
    final_counts = Counter(destination_by_episode[item] for item in final_episodes)

    return TransitionValidationReport(
        pressure_predictions=tuple(pressure_records),
        destination_predictions=tuple(destination_records),
        pressure_metrics=pressure_metrics,
        pressure_baseline_metrics=pressure_baselines,
        destination_metrics=destination_metrics,
        destination_baseline_metrics=destination_baselines,
        pressure_event_count=pressure_events,
        pressure_holdout_has_both=holdout_has_both,
        destination_event_count=len(destination_by_episode),
        destination_event_counts={
            phase: int(counts.get(phase, 0)) for phase in PHASE_SEQUENCE
        },
        destination_final_25_counts={
            phase: int(final_counts.get(phase, 0)) for phase in PHASE_SEQUENCE
        },
        invalid_probability_count=_invalid_probability_count(
            pressure_records,
            destination_records,
        ),
    )


def evaluate_transition_publication_gate(
    report: TransitionValidationReport,
) -> TransitionPublicationDecision:
    """Apply pre-registered support, baseline-skill, calibration, and validity gates."""

    reasons: list[str] = []
    if report.pressure_event_count < 48 or not report.pressure_holdout_has_both:
        reasons.append("INSUFFICIENT_PRESSURE_EVENTS")
    pressure_best_brier = min(
        (item.brier for item in report.pressure_baseline_metrics.values()),
        default=math.inf,
    )
    pressure_best_log_loss = min(
        (item.log_loss for item in report.pressure_baseline_metrics.values()),
        default=math.inf,
    )
    if not (
        report.pressure_metrics.brier <= pressure_best_brier * 0.98
        and report.pressure_metrics.log_loss <= pressure_best_log_loss * 0.98
    ):
        reasons.append("PRESSURE_BASELINE_UNDERPERFORMANCE")
    if not math.isfinite(report.pressure_metrics.ece) or report.pressure_metrics.ece > 0.10:
        reasons.append("PRESSURE_CALIBRATION_ERROR")

    if report.destination_event_count < 48:
        reasons.append("INSUFFICIENT_DESTINATION_EVENTS")
    if any(
        report.destination_event_counts.get(phase, 0) < 8
        or report.destination_final_25_counts.get(phase, 0) < 2
        for phase in PHASE_SEQUENCE
    ):
        reasons.append("INSUFFICIENT_DESTINATION_SUPPORT")
    destination_best_brier = min(
        (item.brier for item in report.destination_baseline_metrics.values()),
        default=math.inf,
    )
    destination_best_log_loss = min(
        (item.log_loss for item in report.destination_baseline_metrics.values()),
        default=math.inf,
    )
    if not (
        report.destination_metrics.brier <= destination_best_brier * 0.98
        and report.destination_metrics.log_loss <= destination_best_log_loss * 0.98
    ):
        reasons.append("DESTINATION_BASELINE_UNDERPERFORMANCE")
    if (
        not math.isfinite(report.destination_metrics.ece)
        or report.destination_metrics.ece > 0.12
    ):
        reasons.append("DESTINATION_CALIBRATION_ERROR")
    if report.invalid_probability_count:
        reasons.append("INVALID_PROBABILITIES")
    return TransitionPublicationDecision(
        status="READY" if not reasons else "LIMITED",
        reason_codes=tuple(reasons),
    )
