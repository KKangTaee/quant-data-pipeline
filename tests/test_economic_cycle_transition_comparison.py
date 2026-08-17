from __future__ import annotations

import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_validation import (
    ProbabilityMetrics,
    TransitionPrediction,
    TransitionValidationReport,
)


def _metrics(*, ready: bool) -> ProbabilityMetrics:
    return ProbabilityMetrics(
        brier=0.10 if ready else 0.14,
        log_loss=0.20 if ready else 0.28,
        ece=0.05,
    )


def _report(
    *,
    pressure_ready: bool,
    destination_ready: bool,
    pressure_predictions: tuple[TransitionPrediction, ...] = (),
    destination_predictions: tuple[TransitionPrediction, ...] = (),
) -> TransitionValidationReport:
    baseline = ProbabilityMetrics(brier=0.12, log_loss=0.24, ece=0.08)
    return TransitionValidationReport(
        pressure_predictions=pressure_predictions,
        destination_predictions=destination_predictions,
        pressure_metrics=_metrics(ready=pressure_ready),
        pressure_baseline_metrics={
            "global_rate": baseline,
            "duration_hazard": baseline,
        },
        destination_metrics=_metrics(ready=destination_ready),
        destination_baseline_metrics={
            "phase_frequency": baseline,
            "fixed_cycle": baseline,
        },
        pressure_event_count=50,
        pressure_holdout_has_both=True,
        destination_event_count=50,
        destination_event_counts={phase: 12 for phase in PHASE_SEQUENCE},
        destination_final_25_counts={phase: 3 for phase in PHASE_SEQUENCE},
        invalid_probability_count=0,
    )


def test_task_gate_can_publish_pressure_without_destination() -> None:
    from finance.economic_cycle_transition_comparison import evaluate_task_gates

    decision = evaluate_task_gates(
        _report(pressure_ready=True, destination_ready=False)
    )

    assert decision.pressure_status == "READY"
    assert decision.destination_status == "LIMITED"
    assert decision.combined_status == "LIMITED"
    assert decision.pressure_reason_codes == ()
    assert "DESTINATION_BASELINE_UNDERPERFORMANCE" in (
        decision.destination_reason_codes
    )


def _pressure_prediction(
    *,
    episode: int,
    actual: float,
    probability: float,
) -> TransitionPrediction:
    origin = pd.Timestamp("2000-01-31") + pd.offsets.MonthEnd(episode)
    return TransitionPrediction(
        task="pressure",
        forecast_origin=origin,
        scoring_episode_id=episode,
        training_episode_max=episode - 1,
        training_target_known_through=origin - pd.offsets.MonthEnd(1),
        actual=actual,
        model_probabilities={"transition": probability},
        baseline_probabilities={},
        weight=1.0,
        current_phase="recovery",
    )


def _destination_prediction(
    *,
    episode: int,
    actual: str,
    actual_probability: float,
) -> TransitionPrediction:
    origin = pd.Timestamp("2000-01-31") + pd.offsets.MonthEnd(episode)
    remainder = (1.0 - actual_probability) / 3.0
    probabilities = {phase: remainder for phase in PHASE_SEQUENCE}
    probabilities[actual] = actual_probability
    return TransitionPrediction(
        task="destination",
        forecast_origin=origin,
        scoring_episode_id=episode,
        training_episode_max=episode - 1,
        training_target_known_through=origin - pd.offsets.MonthEnd(1),
        actual=actual,
        model_probabilities=probabilities,
        baseline_probabilities={},
        weight=1.0,
        current_phase="recovery",
    )


def test_paired_skill_requires_both_pressure_and_destination_mean_improvement() -> None:
    from finance.economic_cycle_transition_comparison import (
        compare_common_origin_skill,
    )

    core = _report(
        pressure_ready=True,
        destination_ready=True,
        pressure_predictions=(
            _pressure_prediction(episode=1, actual=0.0, probability=0.4),
            _pressure_prediction(episode=2, actual=1.0, probability=0.6),
        ),
        destination_predictions=(
            _destination_prediction(
                episode=1,
                actual="expansion",
                actual_probability=0.8,
            ),
            _destination_prediction(
                episode=2,
                actual="slowdown",
                actual_probability=0.8,
            ),
        ),
    )
    extended = _report(
        pressure_ready=True,
        destination_ready=True,
        pressure_predictions=(
            _pressure_prediction(episode=1, actual=0.0, probability=0.2),
            _pressure_prediction(episode=2, actual=1.0, probability=0.8),
        ),
        destination_predictions=(
            _destination_prediction(
                episode=1,
                actual="expansion",
                actual_probability=0.4,
            ),
            _destination_prediction(
                episode=2,
                actual="slowdown",
                actual_probability=0.4,
            ),
        ),
    )

    report = compare_common_origin_skill(core, extended)

    assert report.pressure_common_origins == 2
    assert report.destination_common_origins == 2
    assert report.pressure_mean_relative_skill > 0
    assert report.destination_mean_relative_skill < 0
    assert report.status == "LIMITED"
    assert "DESTINATION_NO_PAIRED_IMPROVEMENT" in report.reason_codes


def test_paired_skill_fails_closed_without_common_origins() -> None:
    from finance.economic_cycle_transition_comparison import (
        compare_common_origin_skill,
    )

    report = compare_common_origin_skill(
        _report(pressure_ready=True, destination_ready=True),
        _report(pressure_ready=True, destination_ready=True),
    )

    assert report.status == "LIMITED"
    assert set(report.reason_codes) == {
        "NO_COMMON_PRESSURE_ORIGINS",
        "NO_COMMON_DESTINATION_ORIGINS",
    }


def test_task_specific_outcome_routes_pressure_and_destination_to_owners() -> None:
    from finance.economic_cycle_transition_comparison import (
        PairedSkillReport,
        TransitionTaskDecision,
        evaluate_task_specific_outcome,
    )

    core = TransitionTaskDecision(
        pressure_status="LIMITED",
        pressure_reason_codes=("CORE_PRESSURE_UNUSED",),
        destination_status="READY",
        destination_reason_codes=(),
        combined_status="LIMITED",
    )
    pressure = TransitionTaskDecision(
        pressure_status="READY",
        pressure_reason_codes=(),
        destination_status="LIMITED",
        destination_reason_codes=("EXTENDED_DESTINATION_UNUSED",),
        combined_status="LIMITED",
    )
    skill = PairedSkillReport(
        status="LIMITED",
        reason_codes=("DESTINATION_NO_PAIRED_IMPROVEMENT",),
        pressure_common_origins=40,
        destination_common_origins=40,
        pressure_mean_relative_skill=0.03,
        destination_mean_relative_skill=-0.02,
        pressure_metrics={},
        destination_metrics={},
    )

    outcome = evaluate_task_specific_outcome(core, pressure, skill)

    assert outcome.status == "GO"
    assert outcome.reason_codes == ()
    assert outcome.pressure_ready is True
    assert outcome.destination_ready is True


def test_task_specific_outcome_reports_only_required_task_failures() -> None:
    from finance.economic_cycle_transition_comparison import (
        PairedSkillReport,
        TransitionTaskDecision,
        evaluate_task_specific_outcome,
    )

    core = TransitionTaskDecision(
        pressure_status="READY",
        pressure_reason_codes=(),
        destination_status="LIMITED",
        destination_reason_codes=("DESTINATION_LIMITED",),
        combined_status="LIMITED",
    )
    pressure = TransitionTaskDecision(
        pressure_status="READY",
        pressure_reason_codes=(),
        destination_status="READY",
        destination_reason_codes=(),
        combined_status="READY",
    )
    skill = PairedSkillReport(
        status="READY",
        reason_codes=(),
        pressure_common_origins=40,
        destination_common_origins=40,
        pressure_mean_relative_skill=0.03,
        destination_mean_relative_skill=0.02,
        pressure_metrics={},
        destination_metrics={},
    )

    outcome = evaluate_task_specific_outcome(core, pressure, skill)

    assert outcome.status == "LIMITED_GO"
    assert outcome.reason_codes == ("DESTINATION_LIMITED",)
