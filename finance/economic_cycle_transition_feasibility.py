"""Research-only feasibility checks for next economic-cycle transitions."""

from __future__ import annotations

import math
from collections import Counter
from collections.abc import Sequence
from dataclasses import asdict, dataclass

import pandas as pd

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


def extract_confirmed_state_events(
    state_frame: pd.DataFrame,
) -> tuple[ConfirmedTransitionEvent, ...]:
    """Read canonical confirmed transitions without confirming them a second time."""

    required = {
        "forecast_origin",
        "data_status",
        "raw_phase",
        "confirmed_phase",
        "confirmed_transition_from",
        "confirmed_transition_to",
    }
    missing = sorted(required.difference(state_frame.columns))
    if missing:
        raise ValueError(f"confirmed state frame missing columns: {', '.join(missing)}")

    rows = state_frame.reset_index(drop=True).to_dict(orient="records")
    anchor_started_at: str | None = None
    events: list[ConfirmedTransitionEvent] = []
    for index, row in enumerate(rows):
        origin = pd.to_datetime(row.get("forecast_origin"), errors="coerce")
        phase = str(row.get("confirmed_phase") or "")
        ready = (
            not pd.isna(origin)
            and row.get("data_status") != "UNAVAILABLE"
            and phase in APPROVED_PHASES
        )
        if not ready:
            continue

        origin_text = pd.Timestamp(origin).date().isoformat()
        transition_from = str(row.get("confirmed_transition_from") or "")
        transition_to = str(row.get("confirmed_transition_to") or "")
        if anchor_started_at is None:
            anchor_started_at = origin_text
        if transition_from not in APPROVED_PHASES or transition_to not in APPROVED_PHASES:
            continue

        candidate_origins: list[str] = []
        for prior in reversed(rows[: index + 1]):
            prior_origin = pd.to_datetime(prior.get("forecast_origin"), errors="coerce")
            if (
                pd.isna(prior_origin)
                or prior.get("data_status") == "UNAVAILABLE"
                or str(prior.get("raw_phase") or "") != transition_to
            ):
                break
            candidate_origins.append(pd.Timestamp(prior_origin).date().isoformat())
        candidate_origins.reverse()
        events.append(
            ConfirmedTransitionEvent(
                from_phase=transition_from,
                to_phase=transition_to,
                anchor_started_at=anchor_started_at,
                candidate_started_at=(
                    candidate_origins[0] if candidate_origins else origin_text
                ),
                confirmed_at=origin_text,
                releases_to_confirmation=max(1, len(candidate_origins)),
            )
        )
        anchor_started_at = origin_text
    return tuple(events)


def _build_sample_report(
    *,
    total_origins: int,
    usable_phases: Sequence[str],
    usable_dates: Sequence[str],
    events: tuple[ConfirmedTransitionEvent, ...],
    gate: TransitionSampleGate,
) -> TransitionFeasibilityReport:
    """Evaluate one already-defined origin/event sample against the shared gate."""

    if not 0.0 < gate.holdout_fraction < 1.0:
        raise ValueError("holdout_fraction must be between 0 and 1")

    holdout_size = (
        int(math.ceil(len(events) * gate.holdout_fraction)) if events else 0
    )
    holdout_events = events[-holdout_size:] if holdout_size else ()

    phase_origin_counts = _phase_counts(usable_phases)
    origin_event_counts = _phase_counts([item.from_phase for item in events])
    destination_event_counts = _phase_counts([item.to_phase for item in events])
    holdout_destination_counts = _phase_counts(
        [item.to_phase for item in holdout_events]
    )
    route_counts = Counter(f"{item.from_phase}->{item.to_phase}" for item in events)

    reasons: list[str] = []
    if len(usable_phases) < gate.minimum_usable_origins:
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
        total_origins=total_origins,
        usable_origins=len(usable_phases),
        first_usable_at=usable_dates[0] if usable_dates else None,
        last_usable_at=usable_dates[-1] if usable_dates else None,
        phase_origin_counts=phase_origin_counts,
        event_count=len(events),
        origin_event_counts=origin_event_counts,
        destination_event_counts=destination_event_counts,
        route_event_counts=dict(sorted(route_counts.items())),
        holdout_event_count=len(holdout_events),
        holdout_destination_event_counts=holdout_destination_counts,
        events=events,
    )


def evaluate_confirmed_transition_sample_feasibility(
    state_frame: pd.DataFrame,
    *,
    gate: TransitionSampleGate = DEFAULT_SAMPLE_GATE,
) -> TransitionFeasibilityReport:
    """Evaluate the canonical state frame without adding another confirmation lag."""

    events = extract_confirmed_state_events(state_frame)
    usable = state_frame.loc[
        state_frame["confirmed_phase"].isin(APPROVED_PHASES)
        & state_frame["data_status"].ne("UNAVAILABLE")
    ]
    usable_dates = [
        pd.Timestamp(value).date().isoformat()
        for value in pd.to_datetime(usable["forecast_origin"], errors="coerce")
        if not pd.isna(value)
    ]
    return _build_sample_report(
        total_origins=len(state_frame),
        usable_phases=[str(value) for value in usable["confirmed_phase"]],
        usable_dates=usable_dates,
        events=events,
        gate=gate,
    )


def evaluate_transition_sample_feasibility(
    history: Sequence[ObservedStateResult],
    *,
    gate: TransitionSampleGate = DEFAULT_SAMPLE_GATE,
) -> TransitionFeasibilityReport:
    """Fail closed when PIT origins or independent transitions are insufficient."""

    usable = [
        item
        for item in history
        if item.observed_state.get("phase") in APPROVED_PHASES
        and item.observed_state.get("data_status") != "UNAVAILABLE"
    ]
    events = extract_confirmed_transition_events(history)
    return _build_sample_report(
        total_origins=len(history),
        usable_phases=[str(item.observed_state["phase"]) for item in usable],
        usable_dates=[str(item.observed_state.get("as_of_date")) for item in usable],
        events=events,
        gate=gate,
    )
