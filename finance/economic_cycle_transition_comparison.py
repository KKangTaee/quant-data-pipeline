"""Task-specific publication and paired model-skill comparisons."""

from __future__ import annotations

import math
from dataclasses import asdict, dataclass

import numpy as np

from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_validation import (
    TransitionPrediction,
    TransitionValidationReport,
    weighted_binary_metrics,
    weighted_multiclass_metrics,
)


@dataclass(frozen=True)
class TransitionTaskDecision:
    pressure_status: str
    pressure_reason_codes: tuple[str, ...]
    destination_status: str
    destination_reason_codes: tuple[str, ...]
    combined_status: str

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class PairedSkillReport:
    status: str
    reason_codes: tuple[str, ...]
    pressure_common_origins: int
    destination_common_origins: int
    pressure_mean_relative_skill: float
    destination_mean_relative_skill: float
    pressure_metrics: dict[str, float]
    destination_metrics: dict[str, float]

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


@dataclass(frozen=True)
class TaskSpecificForecastOutcome:
    """Publication result with pressure and destination routed to their owners."""

    status: str
    reason_codes: tuple[str, ...]
    pressure_ready: bool
    destination_ready: bool

    def to_dict(self) -> dict[str, object]:
        return asdict(self)


def evaluate_task_specific_outcome(
    core_decision: TransitionTaskDecision,
    pressure_decision: TransitionTaskDecision,
    paired_skill: PairedSkillReport,
) -> TaskSpecificForecastOutcome:
    """Require extended pressure skill and compact-core destination readiness."""

    pressure_ready = (
        pressure_decision.pressure_status == "READY"
        and paired_skill.pressure_common_origins > 0
        and paired_skill.pressure_mean_relative_skill > 0.0
    )
    destination_ready = core_decision.destination_status == "READY"
    reasons: list[str] = []
    if not pressure_ready:
        reasons.extend(pressure_decision.pressure_reason_codes)
        reasons.extend(
            reason
            for reason in paired_skill.reason_codes
            if "PRESSURE" in reason
        )
        if (
            paired_skill.pressure_common_origins <= 0
            and "NO_COMMON_PRESSURE_ORIGINS" not in reasons
        ):
            reasons.append("NO_COMMON_PRESSURE_ORIGINS")
        elif (
            paired_skill.pressure_mean_relative_skill <= 0.0
            and "PRESSURE_NO_PAIRED_IMPROVEMENT" not in reasons
        ):
            reasons.append("PRESSURE_NO_PAIRED_IMPROVEMENT")
    if not destination_ready:
        reasons.extend(core_decision.destination_reason_codes)

    if pressure_ready and destination_ready:
        status = "GO"
    elif pressure_ready or destination_ready:
        status = "LIMITED_GO"
    else:
        status = "NO_GO"
    return TaskSpecificForecastOutcome(
        status=status,
        reason_codes=tuple(dict.fromkeys(reasons)),
        pressure_ready=pressure_ready,
        destination_ready=destination_ready,
    )


def _best_metric(
    report: TransitionValidationReport,
    *,
    task: str,
    metric: str,
) -> float:
    baselines = (
        report.pressure_baseline_metrics
        if task == "pressure"
        else report.destination_baseline_metrics
    )
    return min(
        (float(getattr(value, metric)) for value in baselines.values()),
        default=math.inf,
    )


def evaluate_task_gates(
    report: TransitionValidationReport,
) -> TransitionTaskDecision:
    """Separate pressure and destination publication decisions."""

    pressure_reasons: list[str] = []
    if report.pressure_event_count < 48 or not report.pressure_holdout_has_both:
        pressure_reasons.append("INSUFFICIENT_PRESSURE_EVENTS")
    if not (
        report.pressure_metrics.brier
        <= _best_metric(report, task="pressure", metric="brier") * 0.98
        and report.pressure_metrics.log_loss
        <= _best_metric(report, task="pressure", metric="log_loss") * 0.98
    ):
        pressure_reasons.append("PRESSURE_BASELINE_UNDERPERFORMANCE")
    if (
        not math.isfinite(report.pressure_metrics.ece)
        or report.pressure_metrics.ece > 0.10
    ):
        pressure_reasons.append("PRESSURE_CALIBRATION_ERROR")

    destination_reasons: list[str] = []
    if report.destination_event_count < 48:
        destination_reasons.append("INSUFFICIENT_DESTINATION_EVENTS")
    if any(
        report.destination_event_counts.get(phase, 0) < 8
        or report.destination_final_25_counts.get(phase, 0) < 2
        for phase in PHASE_SEQUENCE
    ):
        destination_reasons.append("INSUFFICIENT_DESTINATION_SUPPORT")
    if not (
        report.destination_metrics.brier
        <= _best_metric(report, task="destination", metric="brier") * 0.98
        and report.destination_metrics.log_loss
        <= _best_metric(report, task="destination", metric="log_loss") * 0.98
    ):
        destination_reasons.append("DESTINATION_BASELINE_UNDERPERFORMANCE")
    if (
        not math.isfinite(report.destination_metrics.ece)
        or report.destination_metrics.ece > 0.12
    ):
        destination_reasons.append("DESTINATION_CALIBRATION_ERROR")
    if report.invalid_probability_count:
        pressure_reasons.append("INVALID_PROBABILITIES")
        destination_reasons.append("INVALID_PROBABILITIES")

    pressure_status = "READY" if not pressure_reasons else "LIMITED"
    destination_status = "READY" if not destination_reasons else "LIMITED"
    return TransitionTaskDecision(
        pressure_status=pressure_status,
        pressure_reason_codes=tuple(dict.fromkeys(pressure_reasons)),
        destination_status=destination_status,
        destination_reason_codes=tuple(dict.fromkeys(destination_reasons)),
        combined_status=(
            "READY"
            if pressure_status == destination_status == "READY"
            else "LIMITED"
        ),
    )


def _prediction_map(
    predictions: tuple[TransitionPrediction, ...],
) -> dict[tuple[int, object], TransitionPrediction]:
    return {
        (item.scoring_episode_id, item.forecast_origin): item
        for item in predictions
    }


def _relative_skill(core: float, extended: float) -> float:
    if not math.isfinite(core) or not math.isfinite(extended) or core <= 0.0:
        return 0.0
    return (core - extended) / core


def _paired_pressure_metrics(
    core: TransitionValidationReport,
    extended: TransitionValidationReport,
) -> tuple[int, dict[str, float]]:
    core_map = _prediction_map(core.pressure_predictions)
    extended_map = _prediction_map(extended.pressure_predictions)
    keys = sorted(set(core_map) & set(extended_map), key=lambda item: item[1])
    if not keys:
        return 0, {}
    actual = np.asarray([float(core_map[key].actual) for key in keys], dtype=float)
    if any(float(extended_map[key].actual) != actual[index] for index, key in enumerate(keys)):
        return 0, {}
    weights = np.asarray([float(core_map[key].weight) for key in keys], dtype=float)
    core_values = np.asarray(
        [float(core_map[key].model_probabilities["transition"]) for key in keys]
    )
    extended_values = np.asarray(
        [float(extended_map[key].model_probabilities["transition"]) for key in keys]
    )
    core_metrics = weighted_binary_metrics(core_values, actual, weights)
    extended_metrics = weighted_binary_metrics(extended_values, actual, weights)
    brier_skill = _relative_skill(core_metrics.brier, extended_metrics.brier)
    log_skill = _relative_skill(core_metrics.log_loss, extended_metrics.log_loss)
    return len(keys), {
        "core_brier": core_metrics.brier,
        "extended_brier": extended_metrics.brier,
        "core_log_loss": core_metrics.log_loss,
        "extended_log_loss": extended_metrics.log_loss,
        "brier_relative_skill": brier_skill,
        "log_loss_relative_skill": log_skill,
        "mean_relative_skill": (brier_skill + log_skill) / 2.0,
    }


def _paired_destination_metrics(
    core: TransitionValidationReport,
    extended: TransitionValidationReport,
) -> tuple[int, dict[str, float]]:
    core_map = _prediction_map(core.destination_predictions)
    extended_map = _prediction_map(extended.destination_predictions)
    keys = sorted(set(core_map) & set(extended_map), key=lambda item: item[1])
    if not keys:
        return 0, {}
    labels = [str(core_map[key].actual) for key in keys]
    if any(str(extended_map[key].actual) != labels[index] for index, key in enumerate(keys)):
        return 0, {}
    class_index = {phase: index for index, phase in enumerate(PHASE_SEQUENCE)}
    actual = np.asarray([class_index[label] for label in labels], dtype=int)
    weights = np.asarray([float(core_map[key].weight) for key in keys], dtype=float)
    core_values = np.asarray(
        [
            [float(core_map[key].model_probabilities[phase]) for phase in PHASE_SEQUENCE]
            for key in keys
        ]
    )
    extended_values = np.asarray(
        [
            [
                float(extended_map[key].model_probabilities[phase])
                for phase in PHASE_SEQUENCE
            ]
            for key in keys
        ]
    )
    core_metrics = weighted_multiclass_metrics(core_values, actual, weights)
    extended_metrics = weighted_multiclass_metrics(extended_values, actual, weights)
    brier_skill = _relative_skill(core_metrics.brier, extended_metrics.brier)
    log_skill = _relative_skill(core_metrics.log_loss, extended_metrics.log_loss)
    return len(keys), {
        "core_brier": core_metrics.brier,
        "extended_brier": extended_metrics.brier,
        "core_log_loss": core_metrics.log_loss,
        "extended_log_loss": extended_metrics.log_loss,
        "brier_relative_skill": brier_skill,
        "log_loss_relative_skill": log_skill,
        "mean_relative_skill": (brier_skill + log_skill) / 2.0,
    }


def compare_common_origin_skill(
    core: TransitionValidationReport,
    extended: TransitionValidationReport,
) -> PairedSkillReport:
    """Require the extended model to improve both tasks on identical origins."""

    pressure_count, pressure = _paired_pressure_metrics(core, extended)
    destination_count, destination = _paired_destination_metrics(core, extended)
    pressure_skill = float(pressure.get("mean_relative_skill", 0.0))
    destination_skill = float(destination.get("mean_relative_skill", 0.0))
    reasons: list[str] = []
    if not pressure_count:
        reasons.append("NO_COMMON_PRESSURE_ORIGINS")
    elif pressure_skill <= 0.0:
        reasons.append("PRESSURE_NO_PAIRED_IMPROVEMENT")
    if not destination_count:
        reasons.append("NO_COMMON_DESTINATION_ORIGINS")
    elif destination_skill <= 0.0:
        reasons.append("DESTINATION_NO_PAIRED_IMPROVEMENT")
    return PairedSkillReport(
        status="READY" if not reasons else "LIMITED",
        reason_codes=tuple(reasons),
        pressure_common_origins=pressure_count,
        destination_common_origins=destination_count,
        pressure_mean_relative_skill=pressure_skill,
        destination_mean_relative_skill=destination_skill,
        pressure_metrics=pressure,
        destination_metrics=destination,
    )
