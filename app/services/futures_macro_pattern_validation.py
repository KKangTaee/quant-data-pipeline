from __future__ import annotations

from collections.abc import Sequence
from typing import Any

import pandas as pd

from app.services.futures_macro_pattern import (
    PATTERN_FEATURE_COLUMNS,
    PATTERN_FAMILY_KEYS,
    SCORE_TO_FAMILY_KEY,
    _pattern_close_matrix,
)
from app.services.futures_macro_thermometer import (
    SCORE_DEFINITIONS,
    SIGNAL_Z_THRESHOLD,
    ScoreDefinition,
)


OUTLOOK_HORIZONS: tuple[int, ...] = (5, 20)
OUTCOME_REGIMES: tuple[str, ...] = (
    "risk_seeking",
    "defensive",
    "inflation_rate_pressure",
    "mixed",
)
MIN_INDEPENDENT_EPISODES = 30
VERIFIED_EPISODES = 60
SIMILARITY_SUFFIXES = (
    "1d_z",
    "5d_z",
    "20d_z",
    "5d_slope",
    "20d_slope",
    "acceleration",
    "5d_persistence",
    "20d_persistence",
    "breadth",
    "volatility_ratio",
)


def _family_forward_values(
    scaled_symbol_returns: pd.Series,
    definition: ScoreDefinition,
) -> tuple[float | None, float | None]:
    weighted = [
        float(scaled_symbol_returns[symbol]) * float(weight)
        for symbol, weight in definition.members.items()
        if symbol in scaled_symbol_returns.index and pd.notna(scaled_symbol_returns[symbol])
    ]
    if not weighted:
        return None, None
    positive = sum(value > 0 for value in weighted)
    return float(sum(weighted) / len(weighted)), float(positive / len(weighted))


def _forward_family_record(
    *,
    as_of_date: pd.Timestamp,
    horizon: int,
    scaled_symbol_returns: pd.Series,
) -> dict[str, Any] | None:
    record: dict[str, Any] = {
        "as_of_date": pd.Timestamp(as_of_date),
        "horizon": int(horizon),
    }
    available_count = 0
    for definition in SCORE_DEFINITIONS:
        family = SCORE_TO_FAMILY_KEY[definition.name]
        value, breadth = _family_forward_values(scaled_symbol_returns, definition)
        record[f"{family}__forward_z"] = value
        record[f"{family}__breadth"] = breadth
        if value is not None:
            available_count += 1
    if available_count < 4 or record.get("risk_on__forward_z") is None:
        return None
    return record


def _forward_path_statistics(
    *,
    close: pd.DataFrame,
    as_of_volatility: pd.Series,
    as_of_date: pd.Timestamp,
    horizon: int,
    definition: ScoreDefinition,
) -> dict[str, float] | None:
    """Summarize the cumulative family path with volatility fixed at as-of."""

    position = int(close.index.get_loc(as_of_date))
    if position + horizon >= len(close):
        return None
    base = close.iloc[position]
    values: list[float] = []
    for step in range(1, horizon + 1):
        forward_return = close.iloc[position + step].divide(base).sub(1.0)
        scaled = forward_return.divide(as_of_volatility.mul(step**0.5).replace(0, pd.NA))
        family_value, _ = _family_forward_values(scaled, definition)
        if family_value is not None:
            values.append(family_value)
    if not values:
        return None
    series = pd.Series(values, dtype=float)
    return {
        "median_path_z": float(series.median()),
        "path_iqr_z": float(series.quantile(0.75) - series.quantile(0.25)),
        "max_adverse_z": float(min(0.0, series.min())),
    }


def _classify_forward_regime(row: pd.Series) -> str:
    pressures = sum(
        float(row.get(f"{family}__forward_z") or 0.0) >= SIGNAL_Z_THRESHOLD
        for family in ("rate_pressure", "dollar_pressure", "inflation_pressure")
    )
    risk_on = float(row.get("risk_on__forward_z") or 0.0)
    if pressures >= 2 and risk_on < SIGNAL_Z_THRESHOLD:
        return "inflation_rate_pressure"
    if risk_on <= -SIGNAL_Z_THRESHOLD and (
        float(row.get("safe_haven__forward_z") or 0.0) >= SIGNAL_Z_THRESHOLD
        or float(row.get("dollar_pressure__forward_z") or 0.0) >= SIGNAL_Z_THRESHOLD
    ):
        return "defensive"
    if risk_on >= SIGNAL_Z_THRESHOLD and float(row.get("risk_on__breadth") or 0.0) >= 0.6:
        return "risk_seeking"
    return "mixed"


def build_forward_outcome_frame(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    *,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    """Attach forward regimes using only volatility known on each feature date."""

    close = _pattern_close_matrix(candles, selected_symbols)
    if close.empty or feature_frame.empty:
        return pd.DataFrame(columns=["as_of_date", "horizon", "outcome_regime"])
    returns = close.pct_change(fill_method=None)
    as_of_vol = returns.rolling(60, min_periods=60).std(ddof=0)
    rows: list[dict[str, Any]] = []
    for horizon in OUTLOOK_HORIZONS:
        forward = close.shift(-horizon).divide(close).sub(1.0)
        scaled = forward.divide(as_of_vol.mul(horizon**0.5).replace(0, pd.NA))
        for as_of_date in feature_frame.index.intersection(scaled.index):
            scaled_returns = scaled.loc[as_of_date]
            record = _forward_family_record(
                as_of_date=pd.Timestamp(as_of_date),
                horizon=horizon,
                scaled_symbol_returns=scaled_returns,
            )
            if record is None:
                continue
            record["outcome_regime"] = _classify_forward_regime(pd.Series(record))
            for definition in SCORE_DEFINITIONS:
                family = SCORE_TO_FAMILY_KEY[definition.name]
                statistics = _forward_path_statistics(
                    close=close,
                    as_of_volatility=as_of_vol.loc[as_of_date],
                    as_of_date=pd.Timestamp(as_of_date),
                    horizon=horizon,
                    definition=definition,
                )
                record[f"{family}__median_path_z"] = (
                    statistics["median_path_z"] if statistics is not None else None
                )
                record[f"{family}__path_iqr_z"] = (
                    statistics["path_iqr_z"] if statistics is not None else None
                )
                record[f"{family}__max_adverse_z"] = (
                    statistics["max_adverse_z"] if statistics is not None else None
                )
            rows.append(record)
    if not rows:
        return pd.DataFrame(columns=["as_of_date", "horizon", "outcome_regime"])
    return pd.DataFrame(rows).sort_values(["as_of_date", "horizon"]).reset_index(drop=True)


def _select_spaced_episode_anchors(
    ranked: pd.DataFrame,
    *,
    feature_index: pd.Index,
    minimum_spacing: int,
    limit: int,
) -> pd.DataFrame:
    positions = {pd.Timestamp(value): position for position, value in enumerate(feature_index)}
    accepted_rows: list[pd.Series] = []
    accepted_positions: list[int] = []
    for _, row in ranked.iterrows():
        position = positions.get(pd.Timestamp(row["as_of_date"]))
        if position is None:
            continue
        if any(abs(position - prior) < minimum_spacing for prior in accepted_positions):
            continue
        accepted_rows.append(row)
        accepted_positions.append(position)
        if len(accepted_rows) >= limit:
            break
    if not accepted_rows:
        return ranked.iloc[0:0].copy()
    return pd.DataFrame(accepted_rows).reset_index(drop=True)


def select_similar_episodes(
    feature_frame: pd.DataFrame,
    *,
    current_date: pd.Timestamp,
    horizon: int,
    max_episodes: int = 120,
) -> pd.DataFrame:
    """Rank past-only features and suppress adjacent trading-row duplicates."""

    ordered = feature_frame.sort_index()
    if current_date not in ordered.index:
        return pd.DataFrame(columns=["as_of_date", "similarity_distance"])
    current_position = int(ordered.index.get_loc(current_date))
    eligible_end = current_position - int(horizon)
    candidates = ordered.iloc[: max(0, eligible_end)].copy()
    if candidates.empty:
        return pd.DataFrame(columns=["as_of_date", "similarity_distance"])
    columns = [
        column
        for column in PATTERN_FEATURE_COLUMNS
        if column in ordered.columns and column.endswith(SIMILARITY_SUFFIXES)
    ]
    train = candidates[columns].replace([float("inf"), float("-inf")], pd.NA)
    scale = train.quantile(0.75) - train.quantile(0.25)
    scale = scale.where(scale.abs() > 1e-9, 1.0)
    current = ordered.loc[current_date, columns]
    distance = train.sub(current).divide(scale).pow(2).mean(axis=1, skipna=True).pow(0.5)
    ranked = distance.dropna().sort_values().rename("similarity_distance").reset_index()
    ranked = ranked.rename(columns={ranked.columns[0]: "as_of_date"})
    return _select_spaced_episode_anchors(
        ranked,
        feature_index=ordered.index,
        minimum_spacing=max(1, int(horizon)),
        limit=max(1, int(max_episodes)),
    )
