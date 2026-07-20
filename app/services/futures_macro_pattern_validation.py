from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from datetime import datetime, timezone
import math
from time import monotonic
from typing import Any

import numpy as np
import pandas as pd

from app.services.futures_macro_context import build_futures_macro_context_frame
from app.services.futures_macro_pattern import (
    PATTERN_FEATURE_COLUMNS,
    PATTERN_FAMILY_KEYS,
    SCORE_TO_FAMILY_KEY,
    _pattern_close_matrix,
    build_current_pattern_snapshot,
    build_pattern_feature_frame,
    build_pattern_state_frame,
)
from app.services.futures_macro_outlook_model import (
    CANDIDATES,
    TEMPERATURE_GRID,
    build_momentum_predictor_frame,
    rank_weighted_analog_episodes,
    select_candidate_from_inner_evaluations,
)
from app.services.futures_macro_sessions import (
    FUTURES_DAILY_SESSION_VERSION,
    futures_session_evaluation_token,
    select_completed_futures_daily_rows,
)
from app.services.futures_macro_thermometer import (
    SCORE_DEFINITIONS,
    SIGNAL_Z_THRESHOLD,
    QueryFn,
    ScoreDefinition,
    _default_query,
    _latest_daily_cache_marker,
    normalize_futures_macro_daily_candles,
)
from app.services.futures_macro_validation import _load_validation_futures_rows
from finance.data.futures_market import (
    DEFAULT_CORE_FUTURES_SYMBOLS,
    FUTURES_MACRO_HISTORY_YEARS,
)
from finance.loaders.economic_cycle import load_cycle_history
from finance.loaders.market_events import load_official_macro_event_history


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
PATTERN_ALGORITHM_VERSION = "pattern_outlook_v5_same_state_nested_hybrid"
PATTERN_OUTLOOK_SCHEMA_VERSION = "futures_macro_pattern_outlook_v2"
NESTED_OUTER_MINIMUM_TRAIN = 756
NESTED_INNER_MINIMUM_TRAIN = 504
NESTED_TEST_SIZE = 63
BOOTSTRAP_SAMPLES = 2_000
BOOTSTRAP_SEED = 20260720
PATTERN_OUTLOOK_CACHE_TTL_SECONDS = 900
PATTERN_OUTLOOK_LIMITATIONS = (
    "유사 episode는 조건부 빈도이며 미래 수익이나 체제를 보장하지 않습니다.",
    "yfinance continuous futures는 실제 만기와 roll 구조를 완전히 재현하지 못할 수 있습니다.",
    "표본이 겹치지 않도록 거래일 간격을 두므로 원시 날짜 수보다 유효 표본이 적습니다.",
)
_PATTERN_OUTLOOK_CACHE: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}


def build_same_state_target_frame(
    feature_frame: pd.DataFrame,
    *,
    horizons: Sequence[int] = OUTLOOK_HORIZONS,
) -> pd.DataFrame:
    """Pair every origin with the canonical state observed h sessions later."""

    family_columns = [
        f"terminal_{family}__5d_z"
        for family in PATTERN_FAMILY_KEYS
    ]
    columns = [
        "origin_date",
        "terminal_date",
        "horizon",
        "origin_x",
        "origin_y",
        "terminal_x",
        "terminal_y",
        "delta_x",
        "delta_y",
        "terminal_regime",
        "terminal_transition",
        *family_columns,
    ]
    states = build_pattern_state_frame(feature_frame)
    if states.empty:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, Any]] = []
    for horizon_value in horizons:
        horizon = max(1, int(horizon_value))
        for position in range(0, max(0, len(states) - horizon)):
            origin = states.iloc[position]
            terminal = states.iloc[position + horizon]
            record: dict[str, Any] = {
                "origin_date": pd.Timestamp(states.index[position]),
                "terminal_date": pd.Timestamp(states.index[position + horizon]),
                "horizon": horizon,
                "origin_x": float(origin["x"]),
                "origin_y": float(origin["y"]),
                "terminal_x": float(terminal["x"]),
                "terminal_y": float(terminal["y"]),
                "delta_x": float(terminal["x"] - origin["x"]),
                "delta_y": float(terminal["y"] - origin["y"]),
                "terminal_regime": str(terminal["regime"]),
                "terminal_transition": str(terminal["transition"]),
            }
            for family in PATTERN_FAMILY_KEYS:
                value = terminal.get(f"{family}__5d_z")
                record[f"terminal_{family}__5d_z"] = (
                    float(value) if pd.notna(value) else None
                )
            rows.append(record)
    return (
        pd.DataFrame(rows, columns=columns)
        .sort_values(["origin_date", "horizon"])
        .reset_index(drop=True)
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


def _forward_family_step_frame(
    *,
    close: pd.DataFrame,
    as_of_volatility: pd.DataFrame,
    horizon: int,
    definition: ScoreDefinition,
) -> pd.DataFrame:
    """Return every cumulative family move with scale fixed at each origin."""

    member_columns = [symbol for symbol in definition.members if symbol in close.columns]
    if not member_columns:
        return pd.DataFrame(
            index=close.index,
            columns=range(1, int(horizon) + 1),
            dtype=float,
        )
    output = pd.DataFrame(index=close.index)
    for step in range(1, int(horizon) + 1):
        forward_return = close[member_columns].shift(-step).divide(close[member_columns]).sub(1.0)
        scale = as_of_volatility[member_columns].mul(step**0.5).replace(0, pd.NA)
        scaled = forward_return.divide(scale)
        weighted = pd.concat(
            [
                scaled[symbol].mul(float(definition.members[symbol])).rename(symbol)
                for symbol in member_columns
            ],
            axis=1,
        )
        output[step] = weighted.mean(axis=1, skipna=True)
    return output


def _forward_path_stat_frame(
    *,
    close: pd.DataFrame,
    as_of_volatility: pd.DataFrame,
    horizon: int,
    definition: ScoreDefinition,
) -> pd.DataFrame:
    """Vectorize every as-of path while keeping volatility fixed at each origin."""

    paths = _forward_family_step_frame(
        close=close,
        as_of_volatility=as_of_volatility,
        horizon=horizon,
        definition=definition,
    )
    lower = paths.quantile(0.25, axis=1)
    upper = paths.quantile(0.75, axis=1)
    return pd.DataFrame(
        {
            "median_path_z": paths.median(axis=1, skipna=True),
            "path_iqr_z": upper.sub(lower),
            "max_adverse_z": paths.min(axis=1, skipna=True).clip(upper=0.0),
        },
        index=close.index,
    )


def build_forward_coordinate_frame(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    *,
    selected_symbols: Sequence[str],
) -> pd.DataFrame:
    """Build actual same-state displacement paths for every completed origin."""

    del candles, selected_symbols
    columns = ["as_of_date", "horizon", "step", "delta_x", "delta_y"]
    states = build_pattern_state_frame(feature_frame)
    if states.empty:
        return pd.DataFrame(columns=columns)
    rows: list[dict[str, Any]] = []
    for horizon in OUTLOOK_HORIZONS:
        for position in range(0, max(0, len(states) - horizon)):
            origin = states.iloc[position]
            for step in range(1, horizon + 1):
                terminal = states.iloc[position + step]
                rows.append(
                    {
                        "as_of_date": pd.Timestamp(states.index[position]),
                        "horizon": horizon,
                        "step": step,
                        "delta_x": float(terminal["x"] - origin["x"]),
                        "delta_y": float(terminal["y"] - origin["y"]),
                    }
                )
    return (
        pd.DataFrame(rows, columns=columns)
        .sort_values(["as_of_date", "horizon", "step"])
        .reset_index(drop=True)
    )


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
    """Attach terminal regimes and family moves from the same state function."""

    del candles, selected_symbols
    states = build_pattern_state_frame(feature_frame)
    targets = build_same_state_target_frame(feature_frame)
    if states.empty or targets.empty:
        return pd.DataFrame(
            columns=["as_of_date", "terminal_date", "horizon", "outcome_regime"]
        )
    positions = {pd.Timestamp(value): index for index, value in enumerate(states.index)}
    rows: list[dict[str, Any]] = []
    for _, target in targets.iterrows():
        origin_date = pd.Timestamp(target["origin_date"])
        position = positions[origin_date]
        horizon = int(target["horizon"])
        record: dict[str, Any] = {
            "as_of_date": origin_date,
            "terminal_date": pd.Timestamp(target["terminal_date"]),
            "horizon": horizon,
            "outcome_regime": str(target["terminal_regime"]),
            "terminal_x": float(target["terminal_x"]),
            "terminal_y": float(target["terminal_y"]),
            "delta_x": float(target["delta_x"]),
            "delta_y": float(target["delta_y"]),
        }
        for family in PATTERN_FAMILY_KEYS:
            column = f"{family}__5d_z"
            origin_value = states.iloc[position].get(column)
            terminal_value = states.iloc[position + horizon].get(column)
            if pd.isna(origin_value) or pd.isna(terminal_value):
                record[f"{family}__forward_z"] = None
                record[f"{family}__median_path_z"] = None
                record[f"{family}__path_iqr_z"] = None
                record[f"{family}__max_adverse_z"] = None
                continue
            path = pd.to_numeric(
                states.iloc[position + 1 : position + horizon + 1][column],
                errors="coerce",
            ).sub(float(origin_value)).dropna()
            record[f"{family}__forward_z"] = float(terminal_value - origin_value)
            record[f"{family}__median_path_z"] = (
                float(path.median()) if not path.empty else None
            )
            record[f"{family}__path_iqr_z"] = (
                float(path.quantile(0.75) - path.quantile(0.25))
                if not path.empty
                else None
            )
            record[f"{family}__max_adverse_z"] = (
                float(min(0.0, path.min())) if not path.empty else None
            )
        rows.append(record)
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


def _regime_probabilities(rows: pd.DataFrame) -> dict[str, float]:
    if rows.empty or "outcome_regime" not in rows.columns:
        return {}
    counts = rows["outcome_regime"].value_counts()
    total = int(counts.sum())
    if total <= 0:
        return {}
    return {
        regime: float(counts.get(regime, 0)) / total
        for regime in OUTCOME_REGIMES
    }


def multiclass_brier_score(
    actual: Sequence[str],
    probabilities: Sequence[dict[str, float]],
) -> float | None:
    if not actual or len(actual) != len(probabilities):
        return None
    losses = [
        sum(
            (float(forecast.get(regime, 0.0)) - float(observed == regime)) ** 2
            for regime in OUTCOME_REGIMES
        )
        for observed, forecast in zip(actual, probabilities)
    ]
    return float(sum(losses) / len(losses))


def _calibration_error(
    actual: Sequence[str],
    probabilities: Sequence[dict[str, float]],
) -> float | None:
    if not actual or len(actual) != len(probabilities):
        return None
    weighted_error = 0.0
    observation_count = 0
    boundaries = (0.0, 0.2, 0.4, 0.6, 0.8, 1.0000001)
    for regime in OUTCOME_REGIMES:
        for lower, upper in zip(boundaries, boundaries[1:]):
            bucket = [
                index
                for index, forecast in enumerate(probabilities)
                if lower <= float(forecast.get(regime, 0.0)) < upper
            ]
            if not bucket:
                continue
            predicted = sum(float(probabilities[index].get(regime, 0.0)) for index in bucket) / len(bucket)
            observed = sum(actual[index] == regime for index in bucket) / len(bucket)
            weighted_error += abs(predicted - observed) * len(bucket)
            observation_count += len(bucket)
    return float(weighted_error / observation_count) if observation_count else None


def publication_status_for_metrics(
    *,
    episode_count: int,
    brier_score: float | None,
    baseline_brier_score: float | None,
    calibration_error: float | None,
    fold_improvement_ratio: float,
) -> str:
    if episode_count < MIN_INDEPENDENT_EPISODES:
        return "UNAVAILABLE"
    if episode_count < VERIFIED_EPISODES:
        return "PROVISIONAL"
    improved = (
        brier_score is not None
        and baseline_brier_score is not None
        and brier_score < baseline_brier_score
    )
    calibrated = calibration_error is not None and calibration_error <= 0.10
    stable = fold_improvement_ratio >= 0.60
    return "VERIFIED" if improved and calibrated and stable else "PROVISIONAL"


def probability_publication_status_v2(
    *,
    episode_count: int,
    evaluation_count: int,
    brier_score: float | None,
    baseline_brier_scores: Sequence[float | None],
    log_loss: float | None,
    baseline_log_losses: Sequence[float | None],
    calibration_error: float | None,
    fold_improvement_ratio: float,
    bootstrap_improvement_lower: float | None,
) -> str:
    """Apply the approved probability gate without tuning to actual results."""

    if episode_count < MIN_INDEPENDENT_EPISODES or evaluation_count <= 0:
        return "UNAVAILABLE"
    valid_brier = [float(value) for value in baseline_brier_scores if value is not None]
    valid_log = [float(value) for value in baseline_log_losses if value is not None]
    if brier_score is None or not valid_brier:
        return "PROVISIONAL"
    if evaluation_count >= VERIFIED_EPISODES and float(brier_score) >= min(valid_brier):
        return "NO_EDGE"
    verified = (
        episode_count >= VERIFIED_EPISODES
        and evaluation_count >= VERIFIED_EPISODES
        and all(float(brier_score) < value for value in valid_brier)
        and log_loss is not None
        and bool(valid_log)
        and all(float(log_loss) < value for value in valid_log)
        and calibration_error is not None
        and float(calibration_error) <= 0.10
        and float(fold_improvement_ratio) >= 0.60
        and bootstrap_improvement_lower is not None
        and float(bootstrap_improvement_lower) > 0.0
    )
    return "VERIFIED" if verified else "PROVISIONAL"


def coordinate_publication_status_v2(
    *,
    episode_count: int,
    evaluation_count: int,
    median_error: float | None,
    baseline_median_errors: Sequence[float | None],
    coverage_50: float | None,
    coverage_80: float | None,
    region_area_80: float | None,
    baseline_region_area_80: float | None,
    evaluated_fold_count: int,
    bootstrap_improvement_lower: float | None,
) -> str:
    """Apply the independent terminal-coordinate publication gate."""

    if episode_count < MIN_INDEPENDENT_EPISODES or evaluation_count <= 0:
        return "UNAVAILABLE"
    baselines = [float(value) for value in baseline_median_errors if value is not None]
    if median_error is None or not baselines:
        return "PROVISIONAL"
    if evaluation_count >= VERIFIED_EPISODES and float(median_error) >= min(baselines):
        return "NO_EDGE"
    verified = (
        episode_count >= VERIFIED_EPISODES
        and evaluation_count >= VERIFIED_EPISODES
        and all(float(median_error) < value for value in baselines)
        and coverage_50 is not None
        and 0.40 <= float(coverage_50) <= 0.60
        and coverage_80 is not None
        and 0.70 <= float(coverage_80) <= 0.90
        and region_area_80 is not None
        and baseline_region_area_80 is not None
        and float(region_area_80) < float(baseline_region_area_80)
        and int(evaluated_fold_count) >= 3
        and bootstrap_improvement_lower is not None
        and float(bootstrap_improvement_lower) > 0.0
    )
    return "VERIFIED" if verified else "PROVISIONAL"


def vector_publication_status_v2(
    *,
    coordinate_status: str,
    lower_dx: float | None,
    upper_dx: float | None,
    lower_dy: float | None,
    upper_dy: float | None,
    median_dx: float | None,
    median_dy: float | None,
) -> str:
    """Allow a direction vector only when uncertainty excludes zero."""

    if coordinate_status != "VERIFIED":
        return str(coordinate_status)
    values = (lower_dx, upper_dx, lower_dy, upper_dy, median_dx, median_dy)
    if any(value is None for value in values):
        return "PROVISIONAL"
    x_excludes = float(lower_dx) > 0.0 or float(upper_dx) < 0.0
    y_excludes = float(lower_dy) > 0.0 or float(upper_dy) < 0.0
    displacement = (float(median_dx) ** 2 + float(median_dy) ** 2) ** 0.5
    return "VERIFIED" if (x_excludes or y_excludes) and displacement >= 0.35 else "PROVISIONAL"


def build_weighted_terminal_regions(rows: pd.DataFrame) -> list[dict[str, float]]:
    """Approximate joint 80%/50% terminal regions with weighted covariance ellipses."""

    required = {"terminal_x", "terminal_y", "weight"}
    if rows.empty or not required.issubset(rows.columns):
        return []
    values = rows.loc[:, ["terminal_x", "terminal_y", "weight"]].apply(
        pd.to_numeric,
        errors="coerce",
    ).dropna()
    values = values[values["weight"] > 0]
    if len(values) < 2:
        return []
    weights = values["weight"].to_numpy(dtype=float)
    coordinates = values[["terminal_x", "terminal_y"]].to_numpy(dtype=float)
    weights = weights / weights.sum()
    center = np.average(coordinates, axis=0, weights=weights)
    centered = coordinates - center
    covariance = (centered * weights[:, None]).T @ centered
    eigenvalues, eigenvectors = np.linalg.eigh(covariance)
    order = np.argsort(eigenvalues)[::-1]
    eigenvalues = np.maximum(eigenvalues[order], 0.0)
    eigenvectors = eigenvectors[:, order]
    angle = math.degrees(math.atan2(eigenvectors[1, 0], eigenvectors[0, 0]))
    regions: list[dict[str, float]] = []
    for mass in (0.8, 0.5):
        scale = math.sqrt(-2.0 * math.log(1.0 - mass))
        regions.append(
            {
                "mass": mass,
                "center_x": float(center[0]),
                "center_y": float(center[1]),
                "radius_major": float(scale * math.sqrt(eigenvalues[0])),
                "radius_minor": float(scale * math.sqrt(eigenvalues[1])),
                "rotation_deg": float(angle),
            }
        )
    return regions


def _weighted_regime_probabilities(rows: pd.DataFrame) -> dict[str, float]:
    if rows.empty or not {"outcome_regime", "weight"}.issubset(rows.columns):
        return {}
    usable = rows.loc[:, ["outcome_regime", "weight"]].copy()
    usable["weight"] = pd.to_numeric(usable["weight"], errors="coerce")
    usable = usable.dropna(subset=["outcome_regime", "weight"])
    usable = usable[usable["weight"] > 0]
    total = float(usable["weight"].sum())
    if total <= 0:
        return {}
    return {
        regime: float(usable.loc[usable["outcome_regime"] == regime, "weight"].sum()) / total
        for regime in OUTCOME_REGIMES
    }


def _weighted_quantile(values: pd.Series, weights: pd.Series, quantile: float) -> float | None:
    numeric = pd.DataFrame({"value": values, "weight": weights}).apply(
        pd.to_numeric,
        errors="coerce",
    ).dropna()
    numeric = numeric[numeric["weight"] > 0].sort_values("value")
    if numeric.empty:
        return None
    cumulative = numeric["weight"].cumsum().div(float(numeric["weight"].sum()))
    position = int(np.searchsorted(cumulative.to_numpy(dtype=float), quantile, side="left"))
    return float(numeric.iloc[min(position, len(numeric) - 1)]["value"])


def _single_brier_loss(actual: str, probabilities: dict[str, float]) -> float:
    return float(
        sum(
            (float(probabilities.get(regime, 0.0)) - float(actual == regime)) ** 2
            for regime in OUTCOME_REGIMES
        )
    )


def _mean_log_loss(
    actual: Sequence[str],
    probabilities: Sequence[dict[str, float]],
) -> float | None:
    if not actual or len(actual) != len(probabilities):
        return None
    losses = [
        -math.log(max(1e-12, float(forecast.get(observed, 0.0))))
        for observed, forecast in zip(actual, probabilities)
    ]
    return float(sum(losses) / len(losses))


def _moving_block_bootstrap_lower(
    improvements: Sequence[float],
    *,
    block_size: int,
) -> float | None:
    values = np.asarray(list(improvements), dtype=float)
    values = values[np.isfinite(values)]
    if values.size < 2:
        return None
    block = max(1, min(int(block_size), int(values.size)))
    starts = np.arange(max(1, values.size - block + 1))
    generator = np.random.default_rng(BOOTSTRAP_SEED)
    sample_means = np.empty(BOOTSTRAP_SAMPLES, dtype=float)
    for sample_index in range(BOOTSTRAP_SAMPLES):
        sampled: list[float] = []
        while len(sampled) < values.size:
            start = int(generator.choice(starts))
            sampled.extend(values[start : start + block].tolist())
        sample_means[sample_index] = float(np.mean(sampled[: values.size]))
    return float(np.quantile(sample_means, 0.05))


def _region_area(region: dict[str, float] | None) -> float | None:
    if not region:
        return None
    return float(
        math.pi
        * max(0.0, float(region.get("radius_major", 0.0)))
        * max(0.0, float(region.get("radius_minor", 0.0)))
    )


def _region_contains(region: dict[str, float] | None, x: float, y: float) -> bool | None:
    if not region:
        return None
    major = float(region.get("radius_major", 0.0))
    minor = float(region.get("radius_minor", 0.0))
    if major <= 1e-12 or minor <= 1e-12:
        return None
    theta = math.radians(float(region.get("rotation_deg", 0.0)))
    dx = float(x) - float(region.get("center_x", 0.0))
    dy = float(y) - float(region.get("center_y", 0.0))
    rotated_major = math.cos(theta) * dx + math.sin(theta) * dy
    rotated_minor = -math.sin(theta) * dx + math.cos(theta) * dy
    return (rotated_major / major) ** 2 + (rotated_minor / minor) ** 2 <= 1.0


def _candidate_configurations() -> tuple[tuple[str, float], ...]:
    return (
        ("B0_UNCONDITIONAL", 0.0),
        ("B1_PERSISTENCE", 0.0),
        *tuple(
            (candidate.key, float(temperature))
            for candidate in CANDIDATES
            for temperature in TEMPERATURE_GRID
        ),
    )


def _forecast_for_configuration(
    *,
    configuration: tuple[str, float],
    origin_date: pd.Timestamp,
    horizon: int,
    momentum_frame: pd.DataFrame,
    context_frame: pd.DataFrame,
    states: pd.DataFrame,
    outcomes: pd.DataFrame,
) -> dict[str, Any] | None:
    key, temperature = configuration
    current_date = pd.Timestamp(origin_date)
    if current_date not in states.index:
        return None
    known = outcomes[
        (outcomes["horizon"] == int(horizon))
        & (pd.to_datetime(outcomes["terminal_date"]) <= current_date)
    ].copy()
    if key == "B0_UNCONDITIONAL":
        selected = known.copy()
        selected["weight"] = 1.0
    elif key == "B1_PERSISTENCE":
        state = states.loc[current_date]
        selected = pd.DataFrame(
            [
                {
                    "as_of_date": current_date,
                    "outcome_regime": str(state["regime"]),
                    "terminal_x": float(state["x"]),
                    "terminal_y": float(state["y"]),
                    "delta_x": 0.0,
                    "delta_y": 0.0,
                    "weight": 1.0,
                }
            ]
        )
    else:
        candidate = next((item for item in CANDIDATES if item.key == key), None)
        if candidate is None:
            return None
        analogs = rank_weighted_analog_episodes(
            momentum_frame,
            context_frame,
            current_date=current_date,
            horizon=horizon,
            candidate=candidate,
            temperature=temperature,
        )
        if analogs.empty:
            return None
        selected = analogs.merge(known, on="as_of_date", how="inner")
    probabilities = _weighted_regime_probabilities(selected)
    if selected.empty or not probabilities:
        return None
    regions = build_weighted_terminal_regions(selected)
    weight = pd.to_numeric(selected["weight"], errors="coerce").fillna(0.0)
    total_weight = float(weight.sum())
    if total_weight <= 0:
        return None
    center_x = float(np.average(pd.to_numeric(selected["terminal_x"]), weights=weight))
    center_y = float(np.average(pd.to_numeric(selected["terminal_y"]), weights=weight))
    return {
        "candidate": key,
        "temperature": float(temperature),
        "probabilities": probabilities,
        "rows": selected,
        "regions": regions,
        "center_x": center_x,
        "center_y": center_y,
    }


def _eligible_inner_origins(
    outcomes: pd.DataFrame,
    *,
    states: pd.DataFrame,
    horizon: int,
    cutoff: pd.Timestamp,
) -> list[pd.Timestamp]:
    horizon_rows = outcomes[
        (outcomes["horizon"] == int(horizon))
        & (pd.to_datetime(outcomes["terminal_date"]) <= pd.Timestamp(cutoff))
    ].copy()
    if horizon_rows.empty:
        return []
    positions = {pd.Timestamp(value): index for index, value in enumerate(states.index)}
    horizon_rows["position"] = horizon_rows["as_of_date"].map(
        lambda value: positions.get(pd.Timestamp(value), -1)
    )
    horizon_rows = horizon_rows[
        horizon_rows["position"] >= NESTED_INNER_MINIMUM_TRAIN + int(horizon)
    ].sort_values("as_of_date")
    return [
        pd.Timestamp(value)
        for value in horizon_rows.iloc[:: max(1, int(horizon))]["as_of_date"]
    ]


def _select_configuration_at_cutoff(
    *,
    cutoff: pd.Timestamp,
    horizon: int,
    momentum_frame: pd.DataFrame,
    context_frame: pd.DataFrame,
    states: pd.DataFrame,
    outcomes: pd.DataFrame,
    forecast_cache: dict[tuple[pd.Timestamp, str, float], dict[str, Any] | None],
) -> dict[str, str | float | int] | None:
    actual_by_date = {
        pd.Timestamp(row["as_of_date"]): str(row["outcome_regime"])
        for _, row in outcomes[
            (outcomes["horizon"] == int(horizon))
            & (pd.to_datetime(outcomes["terminal_date"]) <= pd.Timestamp(cutoff))
        ].iterrows()
    }
    evaluations: list[dict[str, Any]] = []
    for origin in _eligible_inner_origins(
        outcomes,
        states=states,
        horizon=horizon,
        cutoff=cutoff,
    ):
        actual = actual_by_date.get(origin)
        if actual is None:
            continue
        for configuration in _candidate_configurations():
            cache_key = (origin, configuration[0], configuration[1])
            if cache_key not in forecast_cache:
                forecast_cache[cache_key] = _forecast_for_configuration(
                    configuration=configuration,
                    origin_date=origin,
                    horizon=horizon,
                    momentum_frame=momentum_frame,
                    context_frame=context_frame,
                    states=states,
                    outcomes=outcomes,
                )
            forecast = forecast_cache[cache_key]
            if forecast is None:
                continue
            evaluations.append(
                {
                    "candidate": configuration[0],
                    "temperature": configuration[1],
                    "brier_loss": _single_brier_loss(actual, forecast["probabilities"]),
                }
            )
    return select_candidate_from_inner_evaluations(pd.DataFrame(evaluations))


def _closest_weighted_episodes(rows: pd.DataFrame) -> list[dict[str, Any]]:
    if rows.empty or "as_of_date" not in rows.columns:
        return []
    ordered = rows.sort_values("weight", ascending=False).head(5)
    return [
        {
            "date": pd.Timestamp(row["as_of_date"]).date().isoformat(),
            "weight": round(float(row.get("weight") or 0.0), 6),
            "outcome_regime": str(row.get("outcome_regime") or "mixed"),
        }
        for _, row in ordered.iterrows()
    ]


def _build_nested_horizon_outlook(
    *,
    horizon: int,
    feature_frame: pd.DataFrame,
    context_frame: pd.DataFrame,
    outcomes: pd.DataFrame,
    current_date: pd.Timestamp,
) -> dict[str, Any]:
    states = build_pattern_state_frame(feature_frame)
    momentum = build_momentum_predictor_frame(
        feature_frame,
        selected_symbol_count=int(
            pd.to_numeric(feature_frame.get("available_symbol_count"), errors="coerce").max()
            if "available_symbol_count" in feature_frame
            else 1
        ),
    )
    cache: dict[tuple[pd.Timestamp, str, float], dict[str, Any] | None] = {}
    actual_all: list[str] = []
    forecast_all: list[dict[str, float]] = []
    b0_all: list[dict[str, float]] = []
    b1_all: list[dict[str, float]] = []
    selected_errors: list[float] = []
    b0_errors: list[float] = []
    b1_errors: list[float] = []
    coverage_50: list[float] = []
    coverage_80: list[float] = []
    area_80: list[float] = []
    baseline_area_80: list[float] = []
    improved_folds = 0
    evaluated_folds = 0
    selection_counts: dict[str, int] = {}
    horizon_rows = outcomes[outcomes["horizon"] == int(horizon)].copy()
    for fold in build_walk_forward_folds(feature_frame, horizon=horizon):
        selected_config = _select_configuration_at_cutoff(
            cutoff=fold.train_end,
            horizon=horizon,
            momentum_frame=momentum,
            context_frame=context_frame,
            states=states,
            outcomes=outcomes,
            forecast_cache=cache,
        )
        if selected_config is None:
            continue
        configuration = (
            str(selected_config["candidate"]),
            float(selected_config["temperature"]),
        )
        selection_counts[configuration[0]] = selection_counts.get(configuration[0], 0) + 1
        test = horizon_rows[
            (horizon_rows["as_of_date"] >= fold.test_start)
            & (horizon_rows["as_of_date"] <= fold.test_end)
        ].iloc[:: max(1, int(horizon))]
        fold_model_losses: list[float] = []
        fold_baseline_losses: list[float] = []
        for _, actual_row in test.iterrows():
            origin = pd.Timestamp(actual_row["as_of_date"])
            actual = str(actual_row["outcome_regime"])
            forecasts: dict[str, dict[str, Any] | None] = {}
            for name, temperature in (
                configuration,
                ("B0_UNCONDITIONAL", 0.0),
                ("B1_PERSISTENCE", 0.0),
            ):
                key = (origin, name, temperature)
                if key not in cache:
                    cache[key] = _forecast_for_configuration(
                        configuration=(name, temperature),
                        origin_date=origin,
                        horizon=horizon,
                        momentum_frame=momentum,
                        context_frame=context_frame,
                        states=states,
                        outcomes=outcomes,
                    )
                forecasts[name] = cache[key]
            model = forecasts.get(configuration[0])
            b0 = forecasts.get("B0_UNCONDITIONAL")
            b1 = forecasts.get("B1_PERSISTENCE")
            if model is None or b0 is None or b1 is None:
                continue
            actual_all.append(actual)
            forecast_all.append(model["probabilities"])
            b0_all.append(b0["probabilities"])
            b1_all.append(b1["probabilities"])
            model_loss = _single_brier_loss(actual, model["probabilities"])
            baseline_loss = min(
                _single_brier_loss(actual, b0["probabilities"]),
                _single_brier_loss(actual, b1["probabilities"]),
            )
            fold_model_losses.append(model_loss)
            fold_baseline_losses.append(baseline_loss)
            actual_x = float(actual_row["terminal_x"])
            actual_y = float(actual_row["terminal_y"])
            selected_errors.append(
                _euclidean_error(actual_x, actual_y, model["center_x"], model["center_y"])
            )
            b0_errors.append(_euclidean_error(actual_x, actual_y, b0["center_x"], b0["center_y"]))
            b1_errors.append(_euclidean_error(actual_x, actual_y, b1["center_x"], b1["center_y"]))
            regions = {float(item["mass"]): item for item in model["regions"]}
            baseline_regions = {float(item["mass"]): item for item in b0["regions"]}
            inside_50 = _region_contains(regions.get(0.5), actual_x, actual_y)
            inside_80 = _region_contains(regions.get(0.8), actual_x, actual_y)
            if inside_50 is not None:
                coverage_50.append(float(inside_50))
            if inside_80 is not None:
                coverage_80.append(float(inside_80))
            selected_area = _region_area(regions.get(0.8))
            unconditional_area = _region_area(baseline_regions.get(0.8))
            if selected_area is not None:
                area_80.append(selected_area)
            if unconditional_area is not None:
                baseline_area_80.append(unconditional_area)
        if fold_model_losses:
            evaluated_folds += 1
            improved_folds += float(np.mean(fold_model_losses)) < float(np.mean(fold_baseline_losses))

    selected_now = _select_configuration_at_cutoff(
        cutoff=current_date,
        horizon=horizon,
        momentum_frame=momentum,
        context_frame=context_frame,
        states=states,
        outcomes=outcomes,
        forecast_cache=cache,
    )
    if selected_now is None:
        selected_now = {
            "candidate": "M1_MOMENTUM",
            "temperature": 1.0,
            "mean_brier": float("nan"),
            "evaluation_count": 0,
        }
    current_configuration = (
        str(selected_now["candidate"]),
        float(selected_now["temperature"]),
    )
    current_forecast = _forecast_for_configuration(
        configuration=current_configuration,
        origin_date=current_date,
        horizon=horizon,
        momentum_frame=momentum,
        context_frame=context_frame,
        states=states,
        outcomes=outcomes,
    )
    m1_evidence = _forecast_for_configuration(
        configuration=("M1_MOMENTUM", current_configuration[1] or 1.0),
        origin_date=current_date,
        horizon=horizon,
        momentum_frame=momentum,
        context_frame=context_frame,
        states=states,
        outcomes=outcomes,
    )
    episode_count = int(len(m1_evidence["rows"])) if m1_evidence else 0
    probabilities = current_forecast["probabilities"] if current_forecast else {}
    brier = multiclass_brier_score(actual_all, forecast_all)
    b0_brier = multiclass_brier_score(actual_all, b0_all)
    b1_brier = multiclass_brier_score(actual_all, b1_all)
    log_loss = _mean_log_loss(actual_all, forecast_all)
    b0_log = _mean_log_loss(actual_all, b0_all)
    b1_log = _mean_log_loss(actual_all, b1_all)
    model_losses = [
        _single_brier_loss(actual, forecast)
        for actual, forecast in zip(actual_all, forecast_all)
    ]
    b0_losses = [_single_brier_loss(actual, forecast) for actual, forecast in zip(actual_all, b0_all)]
    b1_losses = [_single_brier_loss(actual, forecast) for actual, forecast in zip(actual_all, b1_all)]
    baseline_losses = [min(left, right) for left, right in zip(b0_losses, b1_losses)]
    probability_bootstrap = _moving_block_bootstrap_lower(
        [baseline - model for baseline, model in zip(baseline_losses, model_losses)],
        block_size=horizon,
    )
    probability_status = probability_publication_status_v2(
        episode_count=episode_count,
        evaluation_count=len(actual_all),
        brier_score=brier,
        baseline_brier_scores=(b0_brier, b1_brier),
        log_loss=log_loss,
        baseline_log_losses=(b0_log, b1_log),
        calibration_error=_calibration_error(actual_all, forecast_all),
        fold_improvement_ratio=float(improved_folds / evaluated_folds) if evaluated_folds else 0.0,
        bootstrap_improvement_lower=probability_bootstrap,
    )
    median_error = float(pd.Series(selected_errors).median()) if selected_errors else None
    b0_median = float(pd.Series(b0_errors).median()) if b0_errors else None
    b1_median = float(pd.Series(b1_errors).median()) if b1_errors else None
    coordinate_bootstrap = _moving_block_bootstrap_lower(
        [min(left, right) - model for left, right, model in zip(b0_errors, b1_errors, selected_errors)],
        block_size=horizon,
    )
    coordinate_status = coordinate_publication_status_v2(
        episode_count=episode_count,
        evaluation_count=len(selected_errors),
        median_error=median_error,
        baseline_median_errors=(b0_median, b1_median),
        coverage_50=float(np.mean(coverage_50)) if coverage_50 else None,
        coverage_80=float(np.mean(coverage_80)) if coverage_80 else None,
        region_area_80=float(np.mean(area_80)) if area_80 else None,
        baseline_region_area_80=float(np.mean(baseline_area_80)) if baseline_area_80 else None,
        evaluated_fold_count=evaluated_folds,
        bootstrap_improvement_lower=coordinate_bootstrap,
    )
    current_rows = current_forecast["rows"] if current_forecast else pd.DataFrame()
    weights = current_rows.get("weight", pd.Series(dtype=float))
    lower_dx = _weighted_quantile(current_rows.get("delta_x", pd.Series(dtype=float)), weights, 0.10)
    upper_dx = _weighted_quantile(current_rows.get("delta_x", pd.Series(dtype=float)), weights, 0.90)
    lower_dy = _weighted_quantile(current_rows.get("delta_y", pd.Series(dtype=float)), weights, 0.10)
    upper_dy = _weighted_quantile(current_rows.get("delta_y", pd.Series(dtype=float)), weights, 0.90)
    median_dx = _weighted_quantile(current_rows.get("delta_x", pd.Series(dtype=float)), weights, 0.50)
    median_dy = _weighted_quantile(current_rows.get("delta_y", pd.Series(dtype=float)), weights, 0.50)
    vector_status = vector_publication_status_v2(
        coordinate_status=coordinate_status,
        lower_dx=lower_dx,
        upper_dx=upper_dx,
        lower_dy=lower_dy,
        upper_dy=upper_dy,
        median_dx=median_dx,
        median_dy=median_dy,
    )
    baseline_now = _forecast_for_configuration(
        configuration=("B0_UNCONDITIONAL", 0.0),
        origin_date=current_date,
        horizon=horizon,
        momentum_frame=momentum,
        context_frame=context_frame,
        states=states,
        outcomes=outcomes,
    )
    baseline_probabilities = baseline_now["probabilities"] if baseline_now else {}
    lift = {
        regime: float(probabilities.get(regime, 0.0) - baseline_probabilities.get(regime, 0.0))
        for regime in OUTCOME_REGIMES
    }
    candidate_key = current_configuration[0]
    macro_used = candidate_key.startswith("M2")
    regions = current_forecast["regions"] if current_forecast else []
    return {
        "horizon": int(horizon),
        "label": "다음 1주" if horizon == 5 else "다음 1개월",
        "selected_candidate": candidate_key if candidate_key.startswith("M") else None,
        "selected_configuration": candidate_key,
        "selected_temperature": current_configuration[1],
        "probability_status": probability_status,
        "coordinate_status": coordinate_status,
        "vector_status": vector_status,
        "estimate_status": probability_status,
        "status_reason": (
            "시간순 검증에서 baseline 대비 예측 우위가 확인되지 않았습니다."
            if probability_status == "NO_EDGE"
            else "시간순 검증과 공개 기준을 통과했습니다."
            if probability_status == "VERIFIED"
            else "계산은 가능하지만 공개 검증 기준을 아직 모두 충족하지 못했습니다."
            if probability_status == "PROVISIONAL"
            else "독립 표본 또는 시간순 평가가 부족합니다."
        ),
        "probabilities": probabilities,
        "baseline_probabilities": baseline_probabilities,
        "probability_lift": lift,
        "dominant_regime": max(probabilities, key=probabilities.get) if probabilities else None,
        "episode_count": episode_count,
        "evaluation_count": len(actual_all),
        "terminal_regions": regions,
        "direction_vector": {
            "median_dx": median_dx,
            "median_dy": median_dy,
            "lower_dx": lower_dx,
            "upper_dx": upper_dx,
            "lower_dy": lower_dy,
            "upper_dy": upper_dy,
        },
        "macro_adjustment": {
            "used": macro_used,
            "candidate": candidate_key if macro_used else None,
            "reason": (
                "PIT macro/event context가 inner Brier에서 momentum-only보다 개선되어 선택되었습니다."
                if macro_used
                else "macro/event context가 추가 OOS 개선을 만들지 않아 momentum/baseline 선택을 유지했습니다."
            ),
        },
        "closest_episodes": _closest_weighted_episodes(current_rows),
        "asset_pathways": _asset_pathways(current_rows),
        "brier_score": brier,
        "baseline_brier_scores": {"B0_UNCONDITIONAL": b0_brier, "B1_PERSISTENCE": b1_brier},
        "log_loss": log_loss,
        "baseline_log_losses": {"B0_UNCONDITIONAL": b0_log, "B1_PERSISTENCE": b1_log},
        "calibration_error": _calibration_error(actual_all, forecast_all),
        "fold_improvement_ratio": float(improved_folds / evaluated_folds) if evaluated_folds else 0.0,
        "selection_counts": selection_counts,
        "probability_bootstrap_improvement_lower": probability_bootstrap,
        "coordinate_validation": {
            "median_error": median_error,
            "baseline_median_errors": {"B0_UNCONDITIONAL": b0_median, "B1_PERSISTENCE": b1_median},
            "coverage_50": float(np.mean(coverage_50)) if coverage_50 else None,
            "coverage_80": float(np.mean(coverage_80)) if coverage_80 else None,
            "region_area_80": float(np.mean(area_80)) if area_80 else None,
            "baseline_region_area_80": float(np.mean(baseline_area_80)) if baseline_area_80 else None,
            "evaluated_fold_count": evaluated_folds,
            "bootstrap_improvement_lower": coordinate_bootstrap,
        },
    }


@dataclass(frozen=True)
class WalkForwardFold:
    train_start: pd.Timestamp
    train_end: pd.Timestamp
    test_start: pd.Timestamp
    test_end: pd.Timestamp


def build_walk_forward_folds(
    feature_frame: pd.DataFrame,
    *,
    horizon: int,
) -> list[WalkForwardFold]:
    dates = pd.DatetimeIndex(feature_frame.index).sort_values()
    minimum_train = max(NESTED_OUTER_MINIMUM_TRAIN, int(horizon) * 6)
    test_size = NESTED_TEST_SIZE
    folds: list[WalkForwardFold] = []
    cursor = minimum_train + int(horizon)
    while cursor + test_size <= len(dates):
        train_end_position = cursor - int(horizon) - 1
        folds.append(
            WalkForwardFold(
                train_start=dates[0],
                train_end=dates[train_end_position],
                test_start=dates[cursor],
                test_end=dates[min(cursor + test_size - 1, len(dates) - 1)],
            )
        )
        cursor += test_size
    return folds


def _walk_forward_metrics(
    *,
    feature_frame: pd.DataFrame,
    outcomes: pd.DataFrame,
    horizon: int,
) -> dict[str, float | None]:
    actual_all: list[str] = []
    forecast_all: list[dict[str, float]] = []
    baseline_all: list[dict[str, float]] = []
    improved_folds = 0
    evaluated_folds = 0
    horizon_outcomes = outcomes[outcomes["horizon"] == horizon].copy()
    for fold in build_walk_forward_folds(feature_frame, horizon=horizon):
        train = horizon_outcomes[horizon_outcomes["as_of_date"] <= fold.train_end]
        test = horizon_outcomes[
            (horizon_outcomes["as_of_date"] >= fold.test_start)
            & (horizon_outcomes["as_of_date"] <= fold.test_end)
        ].iloc[:: max(1, int(horizon))]
        baseline = _regime_probabilities(train)
        fold_actual: list[str] = []
        fold_forecasts: list[dict[str, float]] = []
        fold_baselines: list[dict[str, float]] = []
        for _, observed_row in test.iterrows():
            test_date = pd.Timestamp(observed_row["as_of_date"])
            matches = select_similar_episodes(
                feature_frame,
                current_date=test_date,
                horizon=horizon,
            )
            matched = matches.merge(
                train[["as_of_date", "outcome_regime"]],
                on="as_of_date",
                how="inner",
            )
            forecast = _regime_probabilities(matched)
            if len(matched) < 10 or not forecast or not baseline:
                continue
            fold_actual.append(str(observed_row["outcome_regime"]))
            fold_forecasts.append(forecast)
            fold_baselines.append(baseline)
        forecast_brier = multiclass_brier_score(fold_actual, fold_forecasts)
        baseline_brier = multiclass_brier_score(fold_actual, fold_baselines)
        if forecast_brier is not None and baseline_brier is not None:
            evaluated_folds += 1
            improved_folds += forecast_brier < baseline_brier
            actual_all.extend(fold_actual)
            forecast_all.extend(fold_forecasts)
            baseline_all.extend(fold_baselines)
    return {
        "brier_score": multiclass_brier_score(actual_all, forecast_all),
        "baseline_brier_score": multiclass_brier_score(actual_all, baseline_all),
        "calibration_error": _calibration_error(actual_all, forecast_all),
        "fold_improvement_ratio": (
            float(improved_folds / evaluated_folds) if evaluated_folds else 0.0
        ),
        "evaluated_fold_count": float(evaluated_folds),
    }


def _euclidean_error(
    actual_x: float,
    actual_y: float,
    predicted_x: float,
    predicted_y: float,
) -> float:
    return float(
        ((actual_x - predicted_x) ** 2 + (actual_y - predicted_y) ** 2) ** 0.5
    )


def _walk_forward_path_metrics(
    *,
    feature_frame: pd.DataFrame,
    coordinates: pd.DataFrame,
    horizon: int,
) -> dict[str, float | int | None]:
    """Evaluate terminal analog coordinates using chronological train-only rows."""

    terminal = coordinates[
        (coordinates["horizon"] == horizon)
        & (coordinates["step"] == horizon)
    ].dropna(subset=["delta_x", "delta_y"])
    errors: list[float] = []
    baseline_errors: list[float] = []
    coverage_rows: list[float] = []
    evaluated_folds = 0
    for fold in build_walk_forward_folds(feature_frame, horizon=horizon):
        train = terminal[terminal["as_of_date"] <= fold.train_end]
        test = terminal[
            (terminal["as_of_date"] >= fold.test_start)
            & (terminal["as_of_date"] <= fold.test_end)
        ].iloc[:: max(1, horizon)]
        if train.empty or test.empty:
            continue
        fold_predictions = 0
        baseline_x = float(train["delta_x"].median())
        baseline_y = float(train["delta_y"].median())
        for _, actual in test.iterrows():
            test_date = pd.Timestamp(actual["as_of_date"])
            matches = select_similar_episodes(
                feature_frame,
                current_date=test_date,
                horizon=horizon,
            )
            analogs = matches.merge(
                train[["as_of_date", "delta_x", "delta_y"]],
                on="as_of_date",
                how="inner",
            )
            if len(analogs) < 10:
                continue
            lower_x, predicted_x, upper_x = (
                analogs["delta_x"].quantile([0.25, 0.5, 0.75]).tolist()
            )
            lower_y, predicted_y, upper_y = (
                analogs["delta_y"].quantile([0.25, 0.5, 0.75]).tolist()
            )
            actual_x = float(actual["delta_x"])
            actual_y = float(actual["delta_y"])
            errors.append(
                _euclidean_error(actual_x, actual_y, predicted_x, predicted_y)
            )
            baseline_errors.append(
                _euclidean_error(actual_x, actual_y, baseline_x, baseline_y)
            )
            coverage_rows.append(
                float(
                    lower_x <= actual_x <= upper_x
                    and lower_y <= actual_y <= upper_y
                )
            )
            fold_predictions += 1
        evaluated_folds += int(fold_predictions > 0)
    return {
        "median_error": float(pd.Series(errors).median()) if errors else None,
        "baseline_median_error": (
            float(pd.Series(baseline_errors).median()) if baseline_errors else None
        ),
        "coverage_50": (
            float(sum(coverage_rows) / len(coverage_rows))
            if coverage_rows
            else None
        ),
        "evaluated_fold_count": evaluated_folds,
    }


def path_publication_status(
    *,
    episode_count: int,
    median_error: float | None,
    baseline_median_error: float | None,
    coverage_50: float | None,
    evaluated_fold_count: int,
) -> str:
    if episode_count < MIN_INDEPENDENT_EPISODES:
        return "UNAVAILABLE"
    verified = (
        episode_count >= VERIFIED_EPISODES
        and median_error is not None
        and baseline_median_error is not None
        and median_error < baseline_median_error
        and coverage_50 is not None
        and 0.35 <= coverage_50 <= 0.65
        and evaluated_fold_count >= 2
    )
    return "VERIFIED" if verified else "PROVISIONAL"


def combined_outlook_publication_status(
    probability_status: str,
    path_status: str,
) -> str:
    """Publish the conservative status when probability and path quality differ."""

    status_rank = {"UNAVAILABLE": 0, "PROVISIONAL": 1, "VERIFIED": 2}
    return min(
        (probability_status, path_status),
        key=lambda value: status_rank.get(value, 0),
    )


def _asset_pathways(rows: pd.DataFrame) -> dict[str, dict[str, float | None]]:
    family_map = {
        "risk_assets": "risk_on",
        "rates": "rate_pressure",
        "dollar": "dollar_pressure",
        "safe_haven": "safe_haven",
        "commodities": "inflation_pressure",
    }
    pathways: dict[str, dict[str, float | None]] = {}
    for key, family in family_map.items():
        endpoint = pd.to_numeric(
            rows.get(f"{family}__forward_z", pd.Series(dtype=float)),
            errors="coerce",
        ).dropna()
        adverse = pd.to_numeric(
            rows.get(f"{family}__max_adverse_z", pd.Series(dtype=float)),
            errors="coerce",
        ).dropna()
        pathways[key] = {
            "median_forward_z": float(endpoint.median()) if not endpoint.empty else None,
            "lower_quartile_z": float(endpoint.quantile(0.25)) if not endpoint.empty else None,
            "upper_quartile_z": float(endpoint.quantile(0.75)) if not endpoint.empty else None,
            "median_max_adverse_z": float(adverse.median()) if not adverse.empty else None,
        }
    return pathways


def _closest_episode_rows(rows: pd.DataFrame) -> list[dict[str, Any]]:
    return [
        {
            "date": pd.Timestamp(row["as_of_date"]).date().isoformat(),
            "similarity_distance": round(float(row["similarity_distance"]), 4),
            "outcome_regime": str(row["outcome_regime"]),
        }
        for _, row in rows.head(5).iterrows()
    ]


def _conditional_path_payload(
    selected_paths: pd.DataFrame,
    *,
    current_location: dict[str, Any],
    horizon: int,
    episode_count: int,
    status: str,
    validation: dict[str, Any],
) -> dict[str, Any]:
    """Translate analog path deltas onto the current map location."""

    base = {
        "status": str(status),
        "episode_count": int(episode_count),
        "band_label": "과거 유사 패턴 가운데 50%",
        "validation": dict(validation),
    }
    if (
        str(status) == "UNAVAILABLE"
        or episode_count < MIN_INDEPENDENT_EPISODES
        or selected_paths.empty
    ):
        return {**base, "status": "UNAVAILABLE", "points": [], "terminal": None}
    current_x = float(current_location.get("x") or 0.0)
    current_y = float(current_location.get("y") or 0.0)
    points: list[dict[str, float | int]] = []
    for step, rows in selected_paths.groupby("step", sort=True):
        x_values = pd.to_numeric(rows["delta_x"], errors="coerce").dropna()
        y_values = pd.to_numeric(rows["delta_y"], errors="coerce").dropna()
        if x_values.empty or y_values.empty:
            continue
        points.append(
            {
                "step": int(step),
                "x": current_x + float(x_values.median()),
                "y": current_y + float(y_values.median()),
                "lower_x": current_x + float(x_values.quantile(0.25)),
                "upper_x": current_x + float(x_values.quantile(0.75)),
                "lower_y": current_y + float(y_values.quantile(0.25)),
                "upper_y": current_y + float(y_values.quantile(0.75)),
            }
        )
    if len(points) < max(1, (int(horizon) + 1) // 2):
        return {**base, "status": "UNAVAILABLE", "points": [], "terminal": None}
    return {**base, "points": points, "terminal": points[-1]}


def _build_horizon_outlook(
    *,
    horizon: int,
    feature_frame: pd.DataFrame,
    outcomes: pd.DataFrame,
    coordinates: pd.DataFrame,
    current_date: pd.Timestamp,
    current_location: dict[str, Any],
) -> dict[str, Any]:
    matches = select_similar_episodes(
        feature_frame,
        current_date=current_date,
        horizon=horizon,
    )
    horizon_outcomes = outcomes[outcomes["horizon"] == horizon].copy()
    selected = matches.merge(horizon_outcomes, on="as_of_date", how="inner")
    episode_count = int(len(selected))
    selected_paths = matches[["as_of_date"]].merge(
        coordinates[coordinates["horizon"] == horizon],
        on="as_of_date",
        how="inner",
    )
    current_position = int(feature_frame.index.get_loc(current_date))
    eligible_position = current_position - int(horizon) - 1
    baseline_cutoff = feature_frame.index[max(0, eligible_position)]
    baseline_rows = horizon_outcomes[horizon_outcomes["as_of_date"] <= baseline_cutoff]
    baseline = _regime_probabilities(baseline_rows)
    if episode_count < MIN_INDEPENDENT_EPISODES:
        return {
            "horizon": horizon,
            "label": "다음 1주" if horizon == 5 else "다음 1개월",
            "probabilities": {},
            "baseline_probabilities": {},
            "probability_lift": {},
            "dominant_regime": None,
            "episode_count": episode_count,
            "probability_status": "UNAVAILABLE",
            "estimate_status": "UNAVAILABLE",
            "status_reason": f"독립 episode {episode_count}개로 최소 30개 기준에 미달합니다.",
            "edge_label": "방향 우위 미확인",
            "brier_score": None,
            "baseline_brier_score": None,
            "calibration_error": None,
            "fold_improvement_ratio": 0.0,
            "closest_episodes": _closest_episode_rows(selected),
            "asset_pathways": {},
            "conditional_path": _conditional_path_payload(
                selected_paths,
                current_location=current_location,
                horizon=horizon,
                episode_count=episode_count,
                status="UNAVAILABLE",
                validation={
                    "median_error": None,
                    "baseline_median_error": None,
                    "coverage_50": None,
                    "evaluated_fold_count": 0,
                },
            ),
        }
    probabilities = _regime_probabilities(selected)
    lift = {
        regime: probabilities.get(regime, 0.0) - baseline.get(regime, 0.0)
        for regime in OUTCOME_REGIMES
    }
    metrics = _walk_forward_metrics(
        feature_frame=feature_frame,
        outcomes=outcomes,
        horizon=horizon,
    )
    probability_status = publication_status_for_metrics(
        episode_count=episode_count,
        brier_score=metrics["brier_score"],
        baseline_brier_score=metrics["baseline_brier_score"],
        calibration_error=metrics["calibration_error"],
        fold_improvement_ratio=float(metrics["fold_improvement_ratio"] or 0.0),
    )
    path_metrics = _walk_forward_path_metrics(
        feature_frame=feature_frame,
        coordinates=coordinates,
        horizon=horizon,
    )
    path_status = path_publication_status(
        episode_count=episode_count,
        median_error=path_metrics["median_error"],
        baseline_median_error=path_metrics["baseline_median_error"],
        coverage_50=path_metrics["coverage_50"],
        evaluated_fold_count=int(path_metrics["evaluated_fold_count"] or 0),
    )
    estimate_status = combined_outlook_publication_status(
        probability_status,
        path_status,
    )
    dominant = max(probabilities, key=probabilities.get)
    edge_regime = max(lift, key=lift.get)
    selected_probability = probabilities[edge_regime]
    baseline_probability = baseline.get(edge_regime, 0.0)
    standard_error = (
        selected_probability * (1.0 - selected_probability) / episode_count
        + baseline_probability * (1.0 - baseline_probability) / max(1, len(baseline_rows))
    ) ** 0.5
    edge_is_distinct = (
        episode_count >= VERIFIED_EPISODES
        and lift[edge_regime] > 1.96 * standard_error
    )
    regime_labels = {
        "risk_seeking": "위험선호 체제 우위",
        "defensive": "방어적 체제 우위",
        "inflation_rate_pressure": "물가·금리 부담 체제 우위",
        "mixed": "혼재 체제 우위",
    }
    return {
        "horizon": horizon,
        "label": "다음 1주" if horizon == 5 else "다음 1개월",
        "probabilities": probabilities,
        "baseline_probabilities": baseline,
        "probability_lift": lift,
        "dominant_regime": dominant,
        "episode_count": episode_count,
        "probability_status": probability_status,
        "estimate_status": estimate_status,
        "status_reason": (
            "확률과 경로의 시간순 검증 기준을 모두 충족했습니다."
            if estimate_status == "VERIFIED"
            else "확률 검증은 충족했지만 경로 검증 기준 일부가 잠정입니다."
            if probability_status == "VERIFIED" and path_status != "VERIFIED"
            else "계산 가능하지만 표본 또는 시간순 검증 기준 일부가 잠정입니다."
        ),
        "edge_label": regime_labels[edge_regime] if edge_is_distinct else "방향 우위 미확인",
        **metrics,
        "closest_episodes": _closest_episode_rows(selected),
        "asset_pathways": _asset_pathways(selected),
        "conditional_path": _conditional_path_payload(
            selected_paths,
            current_location=current_location,
            horizon=horizon,
            episode_count=episode_count,
            status=estimate_status,
            validation=path_metrics,
        ),
    }


def build_pattern_outlook_snapshot(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    current_pattern: dict[str, Any],
    *,
    selected_symbols: Sequence[str],
    context_frame: pd.DataFrame | None = None,
) -> dict[str, Any]:
    """Build nested same-state 5D/20D distributions and independent gates."""

    if feature_frame.empty:
        horizons = [
            {
                "horizon": horizon,
                "label": "다음 1주" if horizon == 5 else "다음 1개월",
                "probabilities": {},
                "baseline_probabilities": {},
                "probability_lift": {},
                "dominant_regime": None,
                "episode_count": 0,
                "evaluation_count": 0,
                "selected_candidate": None,
                "selected_configuration": None,
                "selected_temperature": None,
                "probability_status": "UNAVAILABLE",
                "coordinate_status": "UNAVAILABLE",
                "vector_status": "UNAVAILABLE",
                "estimate_status": "UNAVAILABLE",
                "status_reason": "패턴 feature 이력이 부족합니다.",
                "edge_label": "방향 우위 미확인",
                "brier_score": None,
                "baseline_brier_scores": {},
                "log_loss": None,
                "baseline_log_losses": {},
                "calibration_error": None,
                "fold_improvement_ratio": 0.0,
                "selection_counts": {},
                "probability_bootstrap_improvement_lower": None,
                "closest_episodes": [],
                "asset_pathways": {},
                "terminal_regions": [],
                "direction_vector": None,
                "macro_adjustment": {
                    "used": False,
                    "candidate": None,
                    "reason": "forecast input이 없습니다.",
                },
                "coordinate_validation": {},
            }
            for horizon in OUTLOOK_HORIZONS
        ]
    else:
        outcomes = build_forward_outcome_frame(
            candles,
            feature_frame,
            selected_symbols=selected_symbols,
        )
        current_date = pd.Timestamp(feature_frame.index[-1])
        aligned_context = (
            context_frame.reindex(feature_frame.index)
            if context_frame is not None
            else pd.DataFrame(index=feature_frame.index)
        )
        horizons = [
            _build_nested_horizon_outlook(
                horizon=horizon,
                feature_frame=feature_frame,
                context_frame=aligned_context,
                outcomes=outcomes,
                current_date=current_date,
            )
            for horizon in OUTLOOK_HORIZONS
        ]
    return {
        "schema_version": PATTERN_OUTLOOK_SCHEMA_VERSION,
        "status": (
            "READY"
            if any(item["estimate_status"] != "UNAVAILABLE" for item in horizons)
            else "LIMITED"
        ),
        "as_of_date": current_pattern.get("as_of_date"),
        "current_pattern": current_pattern,
        "horizons": horizons,
        "method": {
            "algorithm_version": PATTERN_ALGORITHM_VERSION,
            "minimum_episodes": MIN_INDEPENDENT_EPISODES,
            "verified_episodes": VERIFIED_EPISODES,
            "effective_episodes": {str(item["horizon"]): item["episode_count"] for item in horizons},
            "brier": {str(item["horizon"]): item["brier_score"] for item in horizons},
            "baseline_brier": {str(item["horizon"]): item["baseline_brier_scores"] for item in horizons},
            "calibration": {str(item["horizon"]): item["calibration_error"] for item in horizons},
            "coordinate_validation": {
                str(item["horizon"]): dict(item["coordinate_validation"])
                for item in horizons
            },
            "selected_candidates": {
                str(item["horizon"]): item["selected_candidate"] for item in horizons
            },
            "selected_configurations": {
                str(item["horizon"]): item["selected_configuration"] for item in horizons
            },
            "nested_validation": {
                "outer_minimum_train": NESTED_OUTER_MINIMUM_TRAIN,
                "inner_minimum_train": NESTED_INNER_MINIMUM_TRAIN,
                "test_size": NESTED_TEST_SIZE,
                "purge": "horizon",
                "bootstrap_samples": BOOTSTRAP_SAMPLES,
                "bootstrap_seed": BOOTSTRAP_SEED,
            },
        },
        "limitations": list(PATTERN_OUTLOOK_LIMITATIONS),
    }


def clear_futures_macro_pattern_validation_cache() -> None:
    _PATTERN_OUTLOOK_CACHE.clear()


def load_overview_futures_macro_pattern_outlook(
    *,
    query_fn: QueryFn | None = None,
    symbols: Sequence[str] | None = None,
    years: int = FUTURES_MACRO_HISTORY_YEARS,
    cache_ttl_seconds: int = PATTERN_OUTLOOK_CACHE_TTL_SECONDS,
    force_refresh: bool = False,
    evaluation_time: datetime | None = None,
) -> dict[str, Any]:
    """Load stored daily futures and cache the outlook by latest daily marker."""

    query = query_fn or _default_query
    selected_symbols = tuple(
        str(symbol).strip().upper()
        for symbol in (symbols or DEFAULT_CORE_FUTURES_SYMBOLS)
        if str(symbol).strip()
    )
    marker = _latest_daily_cache_marker(query, selected_symbols)
    evaluated_at = evaluation_time or datetime.now(timezone.utc)
    cache_key = (
        id(query),
        selected_symbols,
        max(1, int(years)),
        marker,
        futures_session_evaluation_token(evaluated_at),
        PATTERN_ALGORITHM_VERSION,
    )
    now = monotonic()
    cached = _PATTERN_OUTLOOK_CACHE.get(cache_key)
    if (
        cached is not None
        and not force_refresh
        and cache_ttl_seconds > 0
        and now - cached[0] <= cache_ttl_seconds
    ):
        return cached[1]
    rows = _load_validation_futures_rows(
        query,
        symbols=selected_symbols,
        lookback_days=max(1, int(years)) * 366 + 90,
    )
    completed = select_completed_futures_daily_rows(
        rows,
        evaluation_time=evaluated_at,
    )
    candles = normalize_futures_macro_daily_candles(completed.rows)
    features = build_pattern_feature_frame(candles, selected_symbols=selected_symbols)
    current = build_current_pattern_snapshot(features)
    if features.empty:
        context = pd.DataFrame(index=features.index)
    else:
        first_date = pd.Timestamp(features.index[0]).date()
        current_date = pd.Timestamp(features.index[-1]).date()
        try:
            cycle_rows = load_cycle_history(
                start_date=first_date,
                end_date=current_date,
                known_at_date=current_date,
                query_fn=query,
            )
        except Exception:
            cycle_rows = []
        try:
            event_rows = load_official_macro_event_history(
                start_date=first_date,
                end_date=current_date + pd.Timedelta(days=35),
                known_at=evaluated_at,
                query_fn=query,
            )
        except Exception:
            event_rows = []
        context = build_futures_macro_context_frame(
            pd.DatetimeIndex(features.index),
            cycle_rows=cycle_rows,
            event_rows=event_rows,
        )
    snapshot = build_pattern_outlook_snapshot(
        candles,
        features,
        current,
        selected_symbols=selected_symbols,
        context_frame=context,
    )
    snapshot["session"] = {
        "resolver_version": FUTURES_DAILY_SESSION_VERSION,
        "latest_final_session": completed.latest_final_session,
        "pending_session": completed.pending_session,
        "excluded_unknown_rows": completed.excluded_unknown_rows,
        "status": (
            "PENDING_SESSION_FINALIZATION"
            if completed.pending_session
            else "OBSERVED"
        ),
    }
    if cache_ttl_seconds > 0:
        _PATTERN_OUTLOOK_CACHE[cache_key] = (now, snapshot)
    return snapshot
