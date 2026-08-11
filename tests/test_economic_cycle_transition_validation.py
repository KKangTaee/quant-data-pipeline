from __future__ import annotations

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_transition_dataset import TransitionDataset


def _synthetic_dataset(episode_count: int = 16) -> TransitionDataset:
    records: list[dict[str, object]] = []
    origin = pd.Timestamp("2000-01-31")
    for episode_id in range(episode_count):
        current = PHASE_SEQUENCE[episode_id % len(PHASE_SEQUENCE)]
        destination = (
            PHASE_SEQUENCE[(episode_id + 1) % len(PHASE_SEQUENCE)]
            if episode_id + 1 < episode_count
            else None
        )
        destination_known_at = origin + pd.offsets.MonthEnd(4)
        for position in range(4):
            forecast_origin = origin + pd.offsets.MonthEnd(position)
            pressure = 1.0 if position >= 2 and destination is not None else 0.0
            records.append(
                {
                    "forecast_origin": forecast_origin,
                    "confirmed_phase": current,
                    "episode_id": episode_id,
                    "episode_weight": 0.25,
                    "eligible": True,
                    "signal": 1.0 if pressure else -1.0,
                    "destination_signal": float(
                        PHASE_SEQUENCE.index(destination)
                        if destination is not None
                        else 0
                    ),
                    "phase_duration": position + 1,
                    "pressure_target": pressure,
                    "target_known_at": forecast_origin + pd.Timedelta(days=1),
                    "destination_target": destination,
                    "destination_known_at": (
                        destination_known_at if destination is not None else pd.NaT
                    ),
                }
            )
        origin += pd.offsets.MonthEnd(4)
    return TransitionDataset(
        feature_names=("signal", "destination_signal", "phase_duration"),
        rows=pd.DataFrame(records),
    )


def test_expanding_validation_never_trains_on_future_or_current_episode() -> None:
    from finance.economic_cycle_transition_validation import (
        run_transition_validation,
    )

    report = run_transition_validation(
        _synthetic_dataset(),
        initial_training_events=8,
        l2_candidates=(0.1,),
    )

    assert report.pressure_predictions
    assert report.destination_predictions
    for record in (*report.pressure_predictions, *report.destination_predictions):
        assert record.training_target_known_through < record.forecast_origin
        assert record.training_episode_max < record.scoring_episode_id


def test_every_baseline_scores_the_same_oos_target_and_weight() -> None:
    from finance.economic_cycle_transition_validation import (
        run_transition_validation,
    )

    report = run_transition_validation(
        _synthetic_dataset(),
        initial_training_events=8,
        l2_candidates=(0.1,),
    )

    for record in report.pressure_predictions:
        assert set(record.baseline_probabilities) == {"global_rate", "duration_hazard"}
        assert all(0.0 < value < 1.0 for value in record.baseline_probabilities.values())
    for record in report.destination_predictions:
        assert set(record.baseline_probabilities) == {
            "phase_frequency",
            "fixed_cycle",
        }
        assert all(
            abs(sum(distribution.values()) - 1.0) < 1e-12
            for distribution in record.baseline_probabilities.values()
        )


def test_weighted_metric_helpers_are_hand_checkable() -> None:
    from finance.economic_cycle_transition_validation import (
        weighted_binary_metrics,
        weighted_multiclass_metrics,
    )

    binary = weighted_binary_metrics(
        np.asarray([0.25, 0.75]),
        np.asarray([0.0, 1.0]),
        np.asarray([1.0, 1.0]),
        bins=2,
    )
    multiclass = weighted_multiclass_metrics(
        np.asarray([[0.75, 0.25], [0.25, 0.75]]),
        np.asarray([0, 1]),
        np.asarray([1.0, 1.0]),
        bins=2,
    )

    assert binary.brier == pytest.approx(0.0625)
    assert binary.log_loss == pytest.approx(-np.log(0.75))
    assert binary.ece == pytest.approx(0.25)
    assert multiclass.brier == pytest.approx(0.125)
    assert multiclass.log_loss == pytest.approx(-np.log(0.75))
    assert multiclass.ece == pytest.approx(0.25)


def _passing_report():
    from finance.economic_cycle_transition_validation import (
        ProbabilityMetrics,
        TransitionValidationReport,
    )

    model = ProbabilityMetrics(brier=0.10, log_loss=0.20, ece=0.05)
    baseline = ProbabilityMetrics(brier=0.12, log_loss=0.24, ece=0.08)
    return TransitionValidationReport(
        pressure_predictions=(),
        destination_predictions=(),
        pressure_metrics=model,
        pressure_baseline_metrics={"global_rate": baseline, "duration_hazard": baseline},
        destination_metrics=model,
        destination_baseline_metrics={"phase_frequency": baseline, "fixed_cycle": baseline},
        pressure_event_count=50,
        pressure_holdout_has_both=True,
        destination_event_count=50,
        destination_event_counts={phase: 12 for phase in PHASE_SEQUENCE},
        destination_final_25_counts={phase: 3 for phase in PHASE_SEQUENCE},
        invalid_probability_count=0,
    )


@pytest.mark.parametrize(
    ("changes", "reason"),
    (
        ({"pressure_event_count": 47}, "INSUFFICIENT_PRESSURE_EVENTS"),
        (
            {
                "pressure_metrics": None,
            },
            "PRESSURE_BASELINE_UNDERPERFORMANCE",
        ),
        (
            {
                "pressure_metrics": "bad_calibration",
            },
            "PRESSURE_CALIBRATION_ERROR",
        ),
        ({"destination_event_count": 47}, "INSUFFICIENT_DESTINATION_EVENTS"),
        (
            {"destination_event_counts": {phase: 7 for phase in PHASE_SEQUENCE}},
            "INSUFFICIENT_DESTINATION_SUPPORT",
        ),
        (
            {
                "destination_metrics": None,
            },
            "DESTINATION_BASELINE_UNDERPERFORMANCE",
        ),
        (
            {
                "destination_metrics": "bad_calibration",
            },
            "DESTINATION_CALIBRATION_ERROR",
        ),
        ({"invalid_probability_count": 1}, "INVALID_PROBABILITIES"),
    ),
)
def test_publication_gate_reports_independent_failure_reasons(
    changes: dict[str, object], reason: str
) -> None:
    from finance.economic_cycle_transition_validation import (
        ProbabilityMetrics,
        evaluate_transition_publication_gate,
    )

    report = _passing_report()
    normalized = dict(changes)
    if normalized.get("pressure_metrics") is None:
        normalized["pressure_metrics"] = ProbabilityMetrics(
            brier=0.13, log_loss=0.25, ece=0.05
        )
    elif normalized.get("pressure_metrics") == "bad_calibration":
        normalized["pressure_metrics"] = ProbabilityMetrics(
            brier=0.10, log_loss=0.20, ece=0.11
        )
    if normalized.get("destination_metrics") is None:
        normalized["destination_metrics"] = ProbabilityMetrics(
            brier=0.13, log_loss=0.25, ece=0.05
        )
    elif normalized.get("destination_metrics") == "bad_calibration":
        normalized["destination_metrics"] = ProbabilityMetrics(
            brier=0.10, log_loss=0.20, ece=0.13
        )

    decision = evaluate_transition_publication_gate(replace(report, **normalized))

    assert decision.status == "LIMITED"
    assert reason in decision.reason_codes


def test_publication_gate_accepts_only_complete_passing_report() -> None:
    from finance.economic_cycle_transition_validation import (
        evaluate_transition_publication_gate,
    )

    decision = evaluate_transition_publication_gate(_passing_report())

    assert decision.status == "READY"
    assert decision.reason_codes == ()
