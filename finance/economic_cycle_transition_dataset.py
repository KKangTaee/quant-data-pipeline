"""Leakage-safe transition targets derived from the canonical core state."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from finance.economic_cycle_observed_state import PHASE_SEQUENCE, ObservedStateResult


CORE_FORECAST_FEATURES = (
    "IPT_z",
    "H_z",
    "EMPLOY_z",
    "RUC_z",
    "activity_score",
    "labor_income_score",
    "level",
    "momentum",
    "level_change_1m",
    "level_change_3m",
    "level_change_6m",
    "momentum_change_1m",
    "momentum_change_3m",
    "momentum_change_6m",
    "activity_labor_dispersion",
    "positive_breadth",
    "phase_duration",
)
PHASE_FEATURES = tuple(f"phase_{phase}" for phase in PHASE_SEQUENCE)


@dataclass(frozen=True)
class TransitionDataset:
    """Forecast-ready rows plus the exact ordered model feature contract."""

    feature_names: tuple[str, ...]
    rows: pd.DataFrame


def _month_end(value: object) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    timestamp = pd.Timestamp(parsed)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert(None)
    return timestamp.to_period("M").to_timestamp("M").normalize()


def _phase_by_month(
    history: Sequence[ObservedStateResult],
) -> dict[pd.Timestamp, str]:
    phases: dict[pd.Timestamp, str] = {}
    for item in history:
        state = item.observed_state
        phase = str(state.get("phase") or "")
        month = _month_end(state.get("as_of_date"))
        if (
            month is not None
            and phase in PHASE_SEQUENCE
            and state.get("data_status") != "UNAVAILABLE"
        ):
            phases[month] = phase
    return phases


def _confirmed_state_rows(raw_phases: Sequence[str | None]) -> list[dict[str, object]]:
    """Confirm a new state after two consecutive releases without route limits."""

    output: list[dict[str, object]] = []
    confirmed: str | None = None
    candidate: str | None = None
    candidate_streak = 0
    episode_id = -1
    episode_duration = 0

    for raw_phase in raw_phases:
        transition_from: str | None = None
        transition_to: str | None = None
        if raw_phase not in PHASE_SEQUENCE:
            candidate = None
            candidate_streak = 0
        elif confirmed is None:
            confirmed = raw_phase
            episode_id = 0
            episode_duration = 1
        elif raw_phase == confirmed:
            candidate = None
            candidate_streak = 0
            episode_duration += 1
        else:
            if raw_phase == candidate:
                candidate_streak += 1
            else:
                candidate = raw_phase
                candidate_streak = 1
            if candidate_streak >= 2:
                transition_from = confirmed
                transition_to = candidate
                confirmed = candidate
                episode_id += 1
                episode_duration = 1
                candidate = None
                candidate_streak = 0
            else:
                episode_duration += 1
        output.append(
            {
                "confirmed_phase": confirmed,
                "episode_id": episode_id if confirmed is not None else None,
                "phase_duration": episode_duration if confirmed is not None else 0,
                "candidate_phase": candidate,
                "candidate_streak": candidate_streak,
                "confirmed_transition_from": transition_from,
                "confirmed_transition_to": transition_to,
            }
        )
    return output


def _finite(value: object) -> bool:
    try:
        return math.isfinite(float(value))
    except (TypeError, ValueError):
        return False


def build_transition_dataset(
    panel: pd.DataFrame,
    history: Sequence[ObservedStateResult],
    *,
    pressure_horizon_releases: int = 3,
) -> TransitionDataset:
    """Build pressure and unrestricted next-destination labels without look-ahead.

    Pressure is one when a two-release-confirmed phase change occurs within the
    next ``pressure_horizon_releases`` usable publications. Destination is the
    next confirmed phase, with no fixed recovery/expansion/slowdown/contraction
    route imposed. Episode weights stop long calm periods dominating training.
    """

    if pressure_horizon_releases < 1:
        raise ValueError("pressure_horizon_releases must be positive")
    if "forecast_origin" not in panel:
        raise ValueError("forecast_origin is required")

    rows = panel.copy()
    rows["forecast_origin"] = pd.to_datetime(
        rows["forecast_origin"], errors="coerce"
    )
    rows = rows.dropna(subset=["forecast_origin"]).sort_values(
        "forecast_origin", kind="stable"
    ).reset_index(drop=True)
    for feature in CORE_FORECAST_FEATURES:
        if feature not in rows:
            rows[feature] = math.nan
        rows[feature] = pd.to_numeric(rows[feature], errors="coerce")

    phase_lookup = _phase_by_month(history)
    rows["forecast_origin"] = rows["forecast_origin"].map(_month_end)
    rows["raw_phase"] = rows["forecast_origin"].map(phase_lookup)

    confirmations = _confirmed_state_rows(rows["raw_phase"].tolist())
    confirmation_frame = pd.DataFrame(confirmations, index=rows.index)
    # Confirmed episode duration, rather than a one-release candidate, is the
    # state-duration feature the model is allowed to see.
    rows = rows.drop(columns=["phase_duration"], errors="ignore").join(
        confirmation_frame
    )
    for phase in PHASE_SEQUENCE:
        rows[f"phase_{phase}"] = (rows["confirmed_phase"] == phase).astype(float)

    usable_indices = [
        index
        for index, phase in enumerate(rows["raw_phase"].tolist())
        if phase in PHASE_SEQUENCE
    ]
    usable_position = {row_index: position for position, row_index in enumerate(usable_indices)}
    event_indices = [
        index
        for index, destination in enumerate(rows["confirmed_transition_to"].tolist())
        if destination in PHASE_SEQUENCE
    ]

    pressure_targets: list[float] = []
    destination_targets: list[str | None] = []
    pressure_known_at: list[pd.Timestamp | None] = []
    destination_known_at: list[pd.Timestamp | None] = []
    for index in rows.index:
        position = usable_position.get(index)
        later_events = [event_index for event_index in event_indices if event_index > index]
        next_event = later_events[0] if later_events else None

        destination_targets.append(
            str(rows.at[next_event, "confirmed_transition_to"])
            if next_event is not None
            else None
        )
        destination_known_at.append(
            rows.at[next_event, "forecast_origin"] if next_event is not None else None
        )

        if position is None or position + pressure_horizon_releases >= len(usable_indices):
            pressure_targets.append(math.nan)
            pressure_known_at.append(None)
            continue
        horizon_index = usable_indices[position + pressure_horizon_releases]
        if next_event is not None and next_event <= horizon_index:
            pressure_targets.append(1.0)
            pressure_known_at.append(rows.at[next_event, "forecast_origin"])
        else:
            pressure_targets.append(0.0)
            pressure_known_at.append(rows.at[horizon_index, "forecast_origin"])

    rows["pressure_target"] = pressure_targets
    rows["destination_target"] = destination_targets
    rows["target_known_at"] = pd.to_datetime(pressure_known_at)
    rows["destination_known_at"] = pd.to_datetime(destination_known_at)

    feature_names = CORE_FORECAST_FEATURES + PHASE_FEATURES
    eligibility: list[bool] = []
    reasons: list[str] = []
    for row in rows.to_dict(orient="records"):
        if row.get("raw_phase") not in PHASE_SEQUENCE or row.get("confirmed_phase") not in PHASE_SEQUENCE:
            eligibility.append(False)
            reasons.append("MISSING_PHASE_OBSERVATION")
        elif not all(_finite(row.get(feature)) for feature in feature_names):
            eligibility.append(False)
            reasons.append("MISSING_MODEL_FEATURE")
        else:
            eligibility.append(True)
            reasons.append("")
    rows["eligible"] = eligibility
    rows["ineligible_reason"] = reasons
    rows["episode_weight"] = 0.0
    eligible_rows = rows.loc[rows["eligible"]]
    episode_sizes = eligible_rows.groupby("episode_id").size()
    for episode_id, size in episode_sizes.items():
        rows.loc[
            rows["eligible"] & (rows["episode_id"] == episode_id),
            "episode_weight",
        ] = 1.0 / float(size)

    return TransitionDataset(feature_names=feature_names, rows=rows)
