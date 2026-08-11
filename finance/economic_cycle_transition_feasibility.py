"""Research-only feasibility checks for next economic-cycle transitions."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass

from finance.economic_cycle_observed_state import (
    PHASE_SEQUENCE,
    ObservedStateResult,
)


APPROVED_PHASES = frozenset(PHASE_SEQUENCE)


@dataclass(frozen=True)
class ConfirmedTransitionEvent:
    """One independent phase change confirmed by consecutive monthly releases."""

    from_phase: str
    to_phase: str
    anchor_started_at: str
    candidate_started_at: str
    confirmed_at: str
    releases_to_confirmation: int


@dataclass(frozen=True)
class TransitionSampleGate:
    """Minimum evidence required before any probability model experiment."""

    minimum_usable_origins: int
    minimum_events: int
    minimum_events_per_destination: int
    minimum_events_per_origin: int
    holdout_fraction: float
    minimum_holdout_events: int
    minimum_holdout_events_per_destination: int


DEFAULT_SAMPLE_GATE = TransitionSampleGate(
    minimum_usable_origins=180,
    minimum_events=48,
    minimum_events_per_destination=8,
    minimum_events_per_origin=8,
    holdout_fraction=0.25,
    minimum_holdout_events=12,
    minimum_holdout_events_per_destination=2,
)


@dataclass(frozen=True)
class TransitionFeasibilityReport:
    """Independent-event support and the resulting experiment decision."""

    status: str
    reason_codes: tuple[str, ...]
    total_origins: int
    usable_origins: int
    first_usable_at: str | None
    last_usable_at: str | None
    phase_origin_counts: dict[str, int]
    event_count: int
    origin_event_counts: dict[str, int]
    destination_event_counts: dict[str, int]
    route_event_counts: dict[str, int]
    holdout_event_count: int
    holdout_destination_event_counts: dict[str, int]
    events: tuple[ConfirmedTransitionEvent, ...]

    def to_dict(self) -> dict[str, object]:
        """Return a JSON-safe audit payload without changing the decision."""

        payload = asdict(self)
        payload["events"] = [asdict(item) for item in self.events]
        return payload


def extract_confirmed_transition_events(
    history: Sequence[ObservedStateResult],
    *,
    confirmation_releases: int = 2,
) -> tuple[ConfirmedTransitionEvent, ...]:
    """Confirm any destination phase without imposing the fixed cycle order."""

    if confirmation_releases < 1:
        raise ValueError("confirmation_releases must be at least 1")

    anchor_phase: str | None = None
    anchor_started_at: str | None = None
    candidate_phase: str | None = None
    candidate_started_at: str | None = None
    candidate_streak = 0
    events: list[ConfirmedTransitionEvent] = []

    for item in history:
        state = item.observed_state
        phase = str(state.get("phase") or "")
        as_of_date = str(state.get("as_of_date") or "")
        unavailable = state.get("data_status") == "UNAVAILABLE"
        if unavailable or phase not in APPROVED_PHASES or not as_of_date:
            candidate_phase = None
            candidate_started_at = None
            candidate_streak = 0
            continue

        if anchor_phase is None:
            anchor_phase = phase
            anchor_started_at = as_of_date
            continue

        if phase == anchor_phase:
            candidate_phase = None
            candidate_started_at = None
            candidate_streak = 0
            continue

        if phase == candidate_phase:
            candidate_streak += 1
        else:
            candidate_phase = phase
            candidate_started_at = as_of_date
            candidate_streak = 1

        if candidate_streak < confirmation_releases:
            continue

        events.append(
            ConfirmedTransitionEvent(
                from_phase=anchor_phase,
                to_phase=phase,
                anchor_started_at=str(anchor_started_at),
                candidate_started_at=str(candidate_started_at),
                confirmed_at=as_of_date,
                releases_to_confirmation=candidate_streak,
            )
        )
        anchor_phase = phase
        anchor_started_at = str(candidate_started_at)
        candidate_phase = None
        candidate_started_at = None
        candidate_streak = 0

    return tuple(events)


def _phase_counts(values: Sequence[str]) -> dict[str, int]:
    counts = Counter(values)
    return {phase: int(counts.get(phase, 0)) for phase in PHASE_SEQUENCE}


def evaluate_transition_sample_feasibility(
    history: Sequence[ObservedStateResult],
    *,
    gate: TransitionSampleGate = DEFAULT_SAMPLE_GATE,
) -> TransitionFeasibilityReport:
    """Fail closed when PIT origins or independent transitions are insufficient."""

    if not 0.0 < gate.holdout_fraction < 1.0:
        raise ValueError("holdout_fraction must be between 0 and 1")

    usable = [
        item
        for item in history
        if item.observed_state.get("phase") in APPROVED_PHASES
        and item.observed_state.get("data_status") != "UNAVAILABLE"
    ]
    events = extract_confirmed_transition_events(history)
    holdout_size = (
        int(math.ceil(len(events) * gate.holdout_fraction)) if events else 0
    )
    holdout_events = events[-holdout_size:] if holdout_size else ()

    phase_origin_counts = _phase_counts(
        [str(item.observed_state["phase"]) for item in usable]
    )
    origin_event_counts = _phase_counts([item.from_phase for item in events])
    destination_event_counts = _phase_counts([item.to_phase for item in events])
    holdout_destination_counts = _phase_counts(
        [item.to_phase for item in holdout_events]
    )
    route_counts = Counter(
        f"{item.from_phase}->{item.to_phase}" for item in events
    )

    reasons: list[str] = []
    if len(usable) < gate.minimum_usable_origins:
        reasons.append("INSUFFICIENT_USABLE_ORIGINS")
    if len(events) < gate.minimum_events:
        reasons.append("INSUFFICIENT_TRANSITION_EVENTS")
    for phase in PHASE_SEQUENCE:
        suffix = phase.upper()
        if destination_event_counts[phase] < gate.minimum_events_per_destination:
            reasons.append(f"INSUFFICIENT_DESTINATION_{suffix}")
        if origin_event_counts[phase] < gate.minimum_events_per_origin:
            reasons.append(f"INSUFFICIENT_ORIGIN_{suffix}")
    if len(holdout_events) < gate.minimum_holdout_events:
        reasons.append("INSUFFICIENT_HOLDOUT_EVENTS")
    for phase in PHASE_SEQUENCE:
        if (
            holdout_destination_counts[phase]
            < gate.minimum_holdout_events_per_destination
        ):
            reasons.append(f"INSUFFICIENT_HOLDOUT_DESTINATION_{phase.upper()}")

    return TransitionFeasibilityReport(
        status="NO_GO_DATA" if reasons else "GO_EXPERIMENT",
        reason_codes=tuple(reasons),
        total_origins=len(history),
        usable_origins=len(usable),
        first_usable_at=(
            str(usable[0].observed_state.get("as_of_date")) if usable else None
        ),
        last_usable_at=(
            str(usable[-1].observed_state.get("as_of_date")) if usable else None
        ),
        phase_origin_counts=phase_origin_counts,
        event_count=len(events),
        origin_event_counts=origin_event_counts,
        destination_event_counts=destination_event_counts,
        route_event_counts=dict(sorted(route_counts.items())),
        holdout_event_count=len(holdout_events),
        holdout_destination_event_counts=holdout_destination_counts,
        events=events,
    )
