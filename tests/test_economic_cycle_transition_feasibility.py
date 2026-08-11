from __future__ import annotations

import json

import pandas as pd

from finance.economic_cycle_observed_state import ObservedStateResult
from finance.economic_cycle_transition_feasibility import (
    TransitionSampleGate,
    evaluate_transition_sample_feasibility,
    extract_confirmed_transition_events,
)


def _history(*phases: str | None) -> tuple[ObservedStateResult, ...]:
    rows: list[ObservedStateResult] = []
    for index, phase in enumerate(phases, start=1):
        rows.append(
            ObservedStateResult(
                observed_state={
                    "as_of_date": f"2020-{index:02d}-28",
                    "phase": phase,
                    "data_status": "READY" if phase is not None else "UNAVAILABLE",
                },
                recent_changes=(),
                transition_monitor={},
            )
        )
    return tuple(rows)


def _dated_history(phases: list[str | None]) -> tuple[ObservedStateResult, ...]:
    origins = pd.date_range("1990-01-31", periods=len(phases), freq="ME")
    rows: list[ObservedStateResult] = []
    for origin, phase in zip(origins, phases, strict=True):
        rows.append(
            ObservedStateResult(
                observed_state={
                    "as_of_date": origin.date().isoformat(),
                    "phase": phase,
                    "data_status": "READY" if phase is not None else "UNAVAILABLE",
                },
                recent_changes=(),
                transition_monitor={},
            )
        )
    return tuple(rows)


def test_extracts_non_adjacent_destination_only_after_two_consecutive_releases() -> None:
    events = extract_confirmed_transition_events(
        _history("contraction", "expansion", "expansion")
    )

    assert [
        (item.from_phase, item.to_phase, item.candidate_started_at, item.confirmed_at)
        for item in events
    ] == [("contraction", "expansion", "2020-02-28", "2020-03-28")]


def test_candidate_reversal_and_switch_do_not_create_false_transition() -> None:
    events = extract_confirmed_transition_events(
        _history(
            "contraction",
            "recovery",
            "contraction",
            "expansion",
            "slowdown",
            "slowdown",
        )
    )

    assert [(item.from_phase, item.to_phase) for item in events] == [
        ("contraction", "slowdown")
    ]


def test_unavailable_release_breaks_confirmation_streak() -> None:
    events = extract_confirmed_transition_events(
        _history(
            "contraction",
            "recovery",
            None,
            "recovery",
            "recovery",
        )
    )

    assert len(events) == 1
    assert events[0].candidate_started_at == "2020-04-28"
    assert events[0].confirmed_at == "2020-05-28"


def test_sample_gate_counts_independent_events_not_repeated_monthly_origins() -> None:
    report = evaluate_transition_sample_feasibility(
        _dated_history(["contraction"] * 200)
    )

    assert report.usable_origins == 200
    assert report.event_count == 0
    assert report.status == "NO_GO_DATA"
    assert "INSUFFICIENT_TRANSITION_EVENTS" in report.reason_codes


def _balanced_event_history() -> tuple[ObservedStateResult, ...]:
    phases: list[str] = []
    for phase in (
        "contraction",
        "recovery",
        "expansion",
        "slowdown",
        "contraction",
        "recovery",
        "expansion",
        "slowdown",
        "contraction",
    ):
        phases.extend([phase, phase])
    return _dated_history(phases)


def _balanced_gate(*, holdout_fraction: float) -> TransitionSampleGate:
    return TransitionSampleGate(
        minimum_usable_origins=18,
        minimum_events=8,
        minimum_events_per_destination=2,
        minimum_events_per_origin=2,
        holdout_fraction=holdout_fraction,
        minimum_holdout_events=2,
        minimum_holdout_events_per_destination=1,
    )


def test_sample_gate_allows_experiment_only_with_balanced_event_support() -> None:
    report = evaluate_transition_sample_feasibility(
        _balanced_event_history(), gate=_balanced_gate(holdout_fraction=0.5)
    )

    assert report.status == "GO_EXPERIMENT"
    assert report.reason_codes == ()
    assert report.event_count == 8
    assert report.destination_event_counts == {
        "recovery": 2,
        "expansion": 2,
        "slowdown": 2,
        "contraction": 2,
    }
    assert report.holdout_destination_event_counts == {
        "recovery": 1,
        "expansion": 1,
        "slowdown": 1,
        "contraction": 1,
    }
    json.dumps(report.to_dict(), allow_nan=False)


def test_sample_gate_rejects_holdout_missing_destination_classes() -> None:
    report = evaluate_transition_sample_feasibility(
        _balanced_event_history(), gate=_balanced_gate(holdout_fraction=0.25)
    )

    assert report.status == "NO_GO_DATA"
    assert report.reason_codes == (
        "INSUFFICIENT_HOLDOUT_DESTINATION_RECOVERY",
        "INSUFFICIENT_HOLDOUT_DESTINATION_EXPANSION",
    )
