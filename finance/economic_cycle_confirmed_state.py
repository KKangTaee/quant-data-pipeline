"""Canonical two-release confirmation for economic-cycle research state."""

from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass

import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE, ObservedStateResult


@dataclass(frozen=True)
class ConfirmedStateColumns:
    """Stable column names shared by state audit and transition datasets."""

    raw_phase: str = "raw_phase"
    confirmed_phase: str = "confirmed_phase"
    candidate_phase: str = "candidate_phase"
    candidate_streak: str = "candidate_streak"


CONFIRMED_STATE_COLUMNS = ConfirmedStateColumns()


def _month_end(value: object) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    timestamp = pd.Timestamp(parsed)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert(None)
    return timestamp.to_period("M").to_timestamp("M").normalize()


def build_confirmed_state_frame(
    history: Sequence[ObservedStateResult],
    *,
    confirmation_releases: int = 2,
) -> pd.DataFrame:
    """Confirm bootstrap and every unrestricted destination without backdating."""

    if confirmation_releases < 2:
        raise ValueError("confirmation_releases must be at least 2")

    confirmed: str | None = None
    candidate: str | None = None
    candidate_streak = 0
    episode_id: int | None = None
    phase_duration = 0
    rows: list[dict[str, object]] = []

    for item in history:
        state = item.observed_state
        origin = _month_end(state.get("as_of_date"))
        raw_phase = str(state.get("phase") or "")
        raw_usable = (
            origin is not None
            and raw_phase in PHASE_SEQUENCE
            and state.get("data_status") != "UNAVAILABLE"
        )
        transition_from: str | None = None
        transition_to: str | None = None

        if not raw_usable:
            candidate = None
            candidate_streak = 0
            raw_phase_value: str | None = None
        else:
            raw_phase_value = raw_phase
            if confirmed is None:
                if candidate == raw_phase:
                    candidate_streak += 1
                else:
                    candidate = raw_phase
                    candidate_streak = 1
                if candidate_streak >= confirmation_releases:
                    confirmed = raw_phase
                    episode_id = 0
                    phase_duration = 1
                    candidate = None
                    candidate_streak = 0
            elif raw_phase == confirmed:
                candidate = None
                candidate_streak = 0
                phase_duration += 1
            else:
                if candidate == raw_phase:
                    candidate_streak += 1
                else:
                    candidate = raw_phase
                    candidate_streak = 1
                if candidate_streak >= confirmation_releases:
                    transition_from = confirmed
                    transition_to = raw_phase
                    confirmed = raw_phase
                    episode_id = int(episode_id or 0) + 1
                    phase_duration = 1
                    candidate = None
                    candidate_streak = 0
                else:
                    phase_duration += 1

        official_usable = raw_usable and confirmed in PHASE_SEQUENCE
        rows.append(
            {
                "forecast_origin": origin,
                "data_status": "READY" if official_usable else "UNAVAILABLE",
                "raw_phase": raw_phase_value,
                "confirmed_phase": confirmed,
                "candidate_phase": candidate,
                "candidate_streak": candidate_streak,
                "episode_id": episode_id,
                "phase_duration": phase_duration if confirmed is not None else 0,
                "confirmed_transition_from": transition_from,
                "confirmed_transition_to": transition_to,
            }
        )

    return pd.DataFrame(
        rows,
        columns=(
            "forecast_origin",
            "data_status",
            "raw_phase",
            "confirmed_phase",
            "candidate_phase",
            "candidate_streak",
            "episode_id",
            "phase_duration",
            "confirmed_transition_from",
            "confirmed_transition_to",
        ),
    )


def build_confirmed_observed_history(
    state_frame: pd.DataFrame,
) -> tuple[ObservedStateResult, ...]:
    """Project a canonical state frame into the existing audit history contract."""

    output: list[ObservedStateResult] = []
    for row in state_frame.to_dict(orient="records"):
        origin = _month_end(row.get("forecast_origin"))
        phase = str(row.get("confirmed_phase") or "")
        ready = row.get("data_status") != "UNAVAILABLE" and phase in PHASE_SEQUENCE
        output.append(
            ObservedStateResult(
                observed_state={
                    "as_of_date": origin.date().isoformat() if origin is not None else None,
                    "phase": phase if ready else None,
                    "data_status": "READY" if ready else "UNAVAILABLE",
                    "raw_phase": row.get("raw_phase"),
                    "phase_duration": int(row.get("phase_duration") or 0),
                },
                recent_changes=(),
                transition_monitor={
                    "candidate_phase": row.get("candidate_phase"),
                    "candidate_streak": int(row.get("candidate_streak") or 0),
                    "confirmed_transition_from": row.get(
                        "confirmed_transition_from"
                    ),
                    "confirmed_transition_to": row.get("confirmed_transition_to"),
                },
            )
        )
    return tuple(output)
