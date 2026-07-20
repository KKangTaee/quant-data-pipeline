"""Pure predictor projection and weighted analog episode selection."""

from __future__ import annotations

import math
from dataclasses import dataclass

import pandas as pd

from app.services.futures_macro_context import (
    EVENT_CONTEXT_COLUMNS,
    MACRO_CONTEXT_COLUMNS,
)
from app.services.futures_macro_pattern import classify_pattern_state


MOMENTUM_PREDICTOR_COLUMNS = (
    "state_x",
    "state_y",
    "impulse_x",
    "impulse_y",
    "slope_x",
    "slope_y",
    "long_x",
    "long_y",
    "persistence_x",
    "persistence_y",
    "breadth_x",
    "breadth_y",
    "volatility_x",
    "volatility_y",
    "conflict_flag",
    "coverage_ratio",
)
PRESSURE_FAMILIES = (
    "rate_pressure",
    "dollar_pressure",
    "inflation_pressure",
)
TEMPERATURE_GRID = (0.5, 1.0, 2.0)


@dataclass(frozen=True)
class OutlookCandidate:
    key: str
    lambda_macro: float
    lambda_event: float


CANDIDATES = (
    OutlookCandidate("M1_MOMENTUM", 0.0, 0.0),
    OutlookCandidate("M2A_LIGHT", 0.25, 0.25),
    OutlookCandidate("M2B_BALANCED", 0.50, 0.50),
    OutlookCandidate("M2C_MACRO_SENSITIVE", 1.00, 0.50),
)


def _pressure_mean(feature_frame: pd.DataFrame, suffix: str) -> pd.Series:
    columns = [
        f"{family}__{suffix}"
        for family in PRESSURE_FAMILIES
        if f"{family}__{suffix}" in feature_frame.columns
    ]
    if not columns:
        return pd.Series(float("nan"), index=feature_frame.index, dtype=float)
    return feature_frame[columns].apply(pd.to_numeric, errors="coerce").mean(
        axis=1,
        skipna=True,
    )


def _numeric_column(feature_frame: pd.DataFrame, column: str) -> pd.Series:
    if column not in feature_frame.columns:
        return pd.Series(float("nan"), index=feature_frame.index, dtype=float)
    return pd.to_numeric(feature_frame[column], errors="coerce")


def build_momentum_predictor_frame(
    feature_frame: pd.DataFrame,
    *,
    selected_symbol_count: int,
) -> pd.DataFrame:
    """Project the full family feature frame onto 16 fixed predictors."""

    if feature_frame.empty:
        return pd.DataFrame(columns=MOMENTUM_PREDICTOR_COLUMNS).rename_axis("Date")
    ordered = feature_frame.sort_index()
    state_x = _numeric_column(ordered, "risk_on__5d_z")
    state_y = _pressure_mean(ordered, "5d_z")
    one_x = _numeric_column(ordered, "risk_on__1d_z")
    one_y = _pressure_mean(ordered, "1d_z")
    output = pd.DataFrame(index=ordered.index)
    output["state_x"] = state_x
    output["state_y"] = state_y
    output["impulse_x"] = one_x.sub(state_x)
    output["impulse_y"] = one_y.sub(state_y)
    output["slope_x"] = _numeric_column(ordered, "risk_on__5d_slope")
    output["slope_y"] = _pressure_mean(ordered, "5d_slope")
    output["long_x"] = _numeric_column(ordered, "risk_on__20d_z")
    output["long_y"] = _pressure_mean(ordered, "20d_z")
    output["persistence_x"] = _numeric_column(ordered, "risk_on__20d_persistence")
    output["persistence_y"] = _pressure_mean(ordered, "20d_persistence")
    output["breadth_x"] = _numeric_column(ordered, "risk_on__breadth")
    output["breadth_y"] = _pressure_mean(ordered, "breadth")
    output["volatility_x"] = _numeric_column(ordered, "risk_on__volatility_ratio")
    output["volatility_y"] = _pressure_mean(ordered, "volatility_ratio")
    output["conflict_flag"] = ordered.apply(
        lambda row: float(classify_pattern_state(row)["transition"] == "conflicting"),
        axis=1,
    )
    denominator = max(1, int(selected_symbol_count))
    output["coverage_ratio"] = _numeric_column(
        ordered,
        "available_symbol_count",
    ).div(denominator).clip(lower=0.0, upper=1.0)
    output.index.name = "Date"
    return output.loc[:, list(MOMENTUM_PREDICTOR_COLUMNS)]


def _empty_ranked(reason: str | None = None) -> pd.DataFrame:
    frame = pd.DataFrame(
        columns=[
            "as_of_date",
            "momentum_distance",
            "macro_distance",
            "event_distance",
            "combined_distance",
            "weight",
        ]
    )
    if reason:
        frame.attrs["unavailable_reason"] = reason
    return frame


def _scaled_distance(
    train: pd.DataFrame,
    current: pd.Series,
    columns: tuple[str, ...],
    *,
    minimum_present: int,
) -> pd.Series:
    numeric = train.loc[:, list(columns)].apply(pd.to_numeric, errors="coerce")
    current_values = pd.to_numeric(current.reindex(columns), errors="coerce")
    scale = numeric.quantile(0.75) - numeric.quantile(0.25)
    scale = scale.where(scale.abs() > 1e-9, 1.0)
    squared = numeric.sub(current_values).divide(scale).pow(2)
    present = squared.notna().sum(axis=1)
    return squared.mean(axis=1, skipna=True).pow(0.5).where(
        present >= minimum_present
    )


def rank_weighted_analog_episodes(
    momentum_frame: pd.DataFrame,
    context_frame: pd.DataFrame,
    *,
    current_date: pd.Timestamp,
    horizon: int,
    candidate: OutlookCandidate,
    temperature: float,
    max_episodes: int = 120,
) -> pd.DataFrame:
    """Rank past-only, de-overlapped episodes with train-scaled distance blocks."""

    if temperature <= 0:
        raise ValueError("temperature must be positive")
    ordered = momentum_frame.sort_index()
    current_key = pd.Timestamp(current_date)
    if current_key not in ordered.index:
        return _empty_ranked("current_state_missing")
    current_position = int(ordered.index.get_loc(current_key))
    candidate_end = current_position - max(1, int(horizon))
    train = ordered.iloc[: max(0, candidate_end)].copy()
    if train.empty:
        return _empty_ranked("eligible_history_missing")
    minimum_momentum = max(4, math.ceil(len(MOMENTUM_PREDICTOR_COLUMNS) * 0.75))
    momentum_distance = _scaled_distance(
        train,
        ordered.loc[current_key],
        MOMENTUM_PREDICTOR_COLUMNS,
        minimum_present=minimum_momentum,
    )
    context = context_frame.reindex(ordered.index)
    macro_distance = pd.Series(0.0, index=train.index, dtype=float)
    event_distance = pd.Series(0.0, index=train.index, dtype=float)
    if candidate.lambda_macro > 0:
        if not set(MACRO_CONTEXT_COLUMNS).issubset(context.columns):
            return _empty_ranked("macro_context_missing")
        current_macro = context.loc[current_key, list(MACRO_CONTEXT_COLUMNS)]
        if current_macro.isna().any():
            return _empty_ranked("macro_context_missing")
        macro_distance = _scaled_distance(
            context.loc[train.index],
            context.loc[current_key],
            MACRO_CONTEXT_COLUMNS,
            minimum_present=len(MACRO_CONTEXT_COLUMNS),
        )
    if candidate.lambda_event > 0:
        if not set(EVENT_CONTEXT_COLUMNS).issubset(context.columns):
            return _empty_ranked("event_context_missing")
        current_event = context.loc[current_key, list(EVENT_CONTEXT_COLUMNS)]
        if current_event.isna().any():
            return _empty_ranked("event_context_missing")
        event_distance = _scaled_distance(
            context.loc[train.index],
            context.loc[current_key],
            EVENT_CONTEXT_COLUMNS,
            minimum_present=len(EVENT_CONTEXT_COLUMNS),
        )
    combined = (
        momentum_distance
        + float(candidate.lambda_macro) * macro_distance
        + float(candidate.lambda_event) * event_distance
    )
    ranked = pd.DataFrame(
        {
            "momentum_distance": momentum_distance,
            "macro_distance": macro_distance,
            "event_distance": event_distance,
            "combined_distance": combined,
        }
    ).dropna(subset=["combined_distance"])
    if ranked.empty:
        return _empty_ranked("eligible_context_history_missing")
    ranked = ranked.sort_values("combined_distance")
    positions = {pd.Timestamp(value): index for index, value in enumerate(ordered.index)}
    accepted_dates: list[pd.Timestamp] = []
    accepted_positions: list[int] = []
    for value in ranked.index:
        date_value = pd.Timestamp(value)
        position = positions[date_value]
        if any(abs(position - prior) < max(1, int(horizon)) for prior in accepted_positions):
            continue
        accepted_dates.append(date_value)
        accepted_positions.append(position)
        if len(accepted_dates) >= max(1, int(max_episodes)):
            break
    selected = ranked.loc[accepted_dates].copy()
    selected["weight"] = selected["combined_distance"].map(
        lambda value: math.exp(-float(value) / float(temperature))
    )
    return selected.rename_axis("as_of_date").reset_index()
