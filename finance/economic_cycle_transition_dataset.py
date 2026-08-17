"""Leakage-safe transition targets derived from the canonical core state."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Sequence

import pandas as pd

from finance.economic_cycle_confirmed_state import build_confirmed_state_frame
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
COMPACT_CORE_FORECAST_FEATURES = (
    "level",
    "momentum",
    "phase_duration",
    "positive_breadth",
    *PHASE_FEATURES,
)


@dataclass(frozen=True)
class TransitionDataset:
    """Forecast-ready rows plus the exact ordered model feature contract."""

    feature_names: tuple[str, ...]
    rows: pd.DataFrame


def restrict_transition_dataset_features(
    dataset: TransitionDataset,
    feature_names: Sequence[str],
) -> TransitionDataset:
    """Rebuild model eligibility and episode weights for a locked feature set."""

    selected = tuple(dict.fromkeys(str(item) for item in feature_names))
    if not selected:
        raise ValueError("feature_names cannot be empty")
    missing = [feature for feature in selected if feature not in dataset.rows]
    if missing:
        raise ValueError("Missing transition features: " + ", ".join(missing))

    rows = dataset.rows.copy()
    finite_features = rows.loc[:, selected].apply(
        pd.to_numeric,
        errors="coerce",
    ).map(_finite).all(axis=1)
    phase_ready = rows.get(
        "confirmed_phase",
        pd.Series(index=rows.index, dtype=object),
    ).isin(PHASE_SEQUENCE)
    if "raw_phase" in rows:
        phase_ready &= rows["raw_phase"].isin(PHASE_SEQUENCE)
    rows["eligible"] = finite_features & phase_ready
    rows["ineligible_reason"] = rows["eligible"].map(
        {True: "", False: "MISSING_MODEL_FEATURE"}
    )
    rows["episode_weight"] = 0.0
    eligible = rows.loc[rows["eligible"] & rows["episode_id"].notna()]
    for episode_id, size in eligible.groupby("episode_id").size().items():
        rows.loc[
            rows["eligible"] & (rows["episode_id"] == episode_id),
            "episode_weight",
        ] = 1.0 / float(size)
    return TransitionDataset(feature_names=selected, rows=rows)


def _month_end(value: object) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    timestamp = pd.Timestamp(parsed)
    if timestamp.tzinfo is not None:
        timestamp = timestamp.tz_convert(None)
    return timestamp.to_period("M").to_timestamp("M").normalize()


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
    confirmed_state_frame: pd.DataFrame | None = None,
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

    rows["forecast_origin"] = rows["forecast_origin"].map(_month_end)
    state = (
        build_confirmed_state_frame(history)
        if confirmed_state_frame is None
        else confirmed_state_frame.copy()
    )
    if "forecast_origin" not in state:
        raise ValueError("confirmed_state_frame requires forecast_origin")
    state["forecast_origin"] = state["forecast_origin"].map(_month_end)
    state = state.dropna(subset=["forecast_origin"]).drop_duplicates(
        "forecast_origin", keep="last"
    )
    state_columns = (
        "raw_phase",
        "confirmed_phase",
        "episode_id",
        "phase_duration",
        "candidate_phase",
        "candidate_streak",
        "confirmed_transition_from",
        "confirmed_transition_to",
    )
    for column in state_columns:
        if column not in state:
            raise ValueError(f"confirmed_state_frame requires {column}")
    confirmation_frame = state.set_index("forecast_origin")[list(state_columns)]
    # Confirmed episode duration, rather than a one-release candidate, is the
    # state-duration feature the model is allowed to see.
    rows = rows.drop(columns=["phase_duration"], errors="ignore").join(
        confirmation_frame,
        on="forecast_origin",
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
