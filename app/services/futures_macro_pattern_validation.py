from __future__ import annotations

from collections.abc import Sequence
from dataclasses import dataclass
from time import monotonic
from typing import Any

import pandas as pd

from app.services.futures_macro_pattern import (
    PATTERN_FEATURE_COLUMNS,
    PATTERN_FAMILY_KEYS,
    SCORE_TO_FAMILY_KEY,
    _pattern_close_matrix,
    build_current_pattern_snapshot,
    build_pattern_feature_frame,
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
from finance.data.futures_market import DEFAULT_CORE_FUTURES_SYMBOLS


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
PATTERN_ALGORITHM_VERSION = "pattern_outlook_v1"
PATTERN_OUTLOOK_CACHE_TTL_SECONDS = 900
PATTERN_OUTLOOK_LIMITATIONS = (
    "유사 episode는 조건부 빈도이며 미래 수익이나 체제를 보장하지 않습니다.",
    "yfinance continuous futures는 실제 만기와 roll 구조를 완전히 재현하지 못할 수 있습니다.",
    "표본이 겹치지 않도록 거래일 간격을 두므로 원시 날짜 수보다 유효 표본이 적습니다.",
)
_PATTERN_OUTLOOK_CACHE: dict[tuple[Any, ...], tuple[float, dict[str, Any]]] = {}


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


def _forward_path_stat_frame(
    *,
    close: pd.DataFrame,
    as_of_volatility: pd.DataFrame,
    horizon: int,
    definition: ScoreDefinition,
) -> pd.DataFrame:
    """Vectorize every as-of path while keeping volatility fixed at each origin."""

    member_columns = [symbol for symbol in definition.members if symbol in close.columns]
    if not member_columns:
        return pd.DataFrame(
            index=close.index,
            columns=["median_path_z", "path_iqr_z", "max_adverse_z"],
            dtype=float,
        )
    step_values: dict[int, pd.Series] = {}
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
        step_values[step] = weighted.mean(axis=1, skipna=True)
    paths = pd.DataFrame(step_values, index=close.index)
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
    path_statistics = {
        (horizon, SCORE_TO_FAMILY_KEY[definition.name]): _forward_path_stat_frame(
            close=close,
            as_of_volatility=as_of_vol,
            horizon=horizon,
            definition=definition,
        )
        for horizon in OUTLOOK_HORIZONS
        for definition in SCORE_DEFINITIONS
    }
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
                statistics = path_statistics[(horizon, family)].loc[as_of_date]
                record[f"{family}__median_path_z"] = statistics["median_path_z"]
                record[f"{family}__path_iqr_z"] = statistics["path_iqr_z"]
                record[f"{family}__max_adverse_z"] = statistics["max_adverse_z"]
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
    minimum_train = max(252 * 3, int(horizon) * 6)
    test_size = 63
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
        endpoint = pd.to_numeric(rows.get(f"{family}__forward_z"), errors="coerce").dropna()
        adverse = pd.to_numeric(rows.get(f"{family}__max_adverse_z"), errors="coerce").dropna()
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


def _build_horizon_outlook(
    *,
    horizon: int,
    feature_frame: pd.DataFrame,
    outcomes: pd.DataFrame,
    current_date: pd.Timestamp,
) -> dict[str, Any]:
    matches = select_similar_episodes(
        feature_frame,
        current_date=current_date,
        horizon=horizon,
    )
    horizon_outcomes = outcomes[outcomes["horizon"] == horizon].copy()
    selected = matches.merge(horizon_outcomes, on="as_of_date", how="inner")
    episode_count = int(len(selected))
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
            "estimate_status": "UNAVAILABLE",
            "status_reason": f"독립 episode {episode_count}개로 최소 30개 기준에 미달합니다.",
            "edge_label": "방향 우위 미확인",
            "brier_score": None,
            "baseline_brier_score": None,
            "calibration_error": None,
            "fold_improvement_ratio": 0.0,
            "closest_episodes": _closest_episode_rows(selected),
            "asset_pathways": {},
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
    estimate_status = publication_status_for_metrics(
        episode_count=episode_count,
        brier_score=metrics["brier_score"],
        baseline_brier_score=metrics["baseline_brier_score"],
        calibration_error=metrics["calibration_error"],
        fold_improvement_ratio=float(metrics["fold_improvement_ratio"] or 0.0),
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
        "estimate_status": estimate_status,
        "status_reason": (
            "시간순 검증과 확률 보정 기준을 충족했습니다."
            if estimate_status == "VERIFIED"
            else "계산 가능하지만 표본 또는 시간순 검증 기준 일부가 잠정입니다."
        ),
        "edge_label": regime_labels[edge_regime] if edge_is_distinct else "방향 우위 미확인",
        **metrics,
        "closest_episodes": _closest_episode_rows(selected),
        "asset_pathways": _asset_pathways(selected),
    }


def build_pattern_outlook_snapshot(
    candles: pd.DataFrame,
    feature_frame: pd.DataFrame,
    current_pattern: dict[str, Any],
    *,
    selected_symbols: Sequence[str],
) -> dict[str, Any]:
    """Build current context plus publishable conditional 5D/20D outlooks."""

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
                "estimate_status": "UNAVAILABLE",
                "status_reason": "패턴 feature 이력이 부족합니다.",
                "edge_label": "방향 우위 미확인",
                "brier_score": None,
                "baseline_brier_score": None,
                "calibration_error": None,
                "fold_improvement_ratio": 0.0,
                "closest_episodes": [],
                "asset_pathways": {},
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
        horizons = [
            _build_horizon_outlook(
                horizon=horizon,
                feature_frame=feature_frame,
                outcomes=outcomes,
                current_date=current_date,
            )
            for horizon in OUTLOOK_HORIZONS
        ]
    return {
        "schema_version": "futures_macro_pattern_outlook_v1",
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
            "baseline_brier": {str(item["horizon"]): item["baseline_brier_score"] for item in horizons},
            "calibration": {str(item["horizon"]): item["calibration_error"] for item in horizons},
        },
        "limitations": list(PATTERN_OUTLOOK_LIMITATIONS),
    }


def clear_futures_macro_pattern_validation_cache() -> None:
    _PATTERN_OUTLOOK_CACHE.clear()


def load_overview_futures_macro_pattern_outlook(
    *,
    query_fn: QueryFn | None = None,
    symbols: Sequence[str] | None = None,
    years: int = 5,
    cache_ttl_seconds: int = PATTERN_OUTLOOK_CACHE_TTL_SECONDS,
    force_refresh: bool = False,
) -> dict[str, Any]:
    """Load stored daily futures and cache the outlook by latest daily marker."""

    query = query_fn or _default_query
    selected_symbols = tuple(
        str(symbol).strip().upper()
        for symbol in (symbols or DEFAULT_CORE_FUTURES_SYMBOLS)
        if str(symbol).strip()
    )
    marker = _latest_daily_cache_marker(query, selected_symbols)
    cache_key = (
        id(query),
        selected_symbols,
        max(1, int(years)),
        marker,
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
    candles = normalize_futures_macro_daily_candles(rows)
    features = build_pattern_feature_frame(candles, selected_symbols=selected_symbols)
    current = build_current_pattern_snapshot(features)
    snapshot = build_pattern_outlook_snapshot(
        candles,
        features,
        current,
        selected_symbols=selected_symbols,
    )
    if cache_ttl_seconds > 0:
        _PATTERN_OUTLOOK_CACHE[cache_key] = (now, snapshot)
    return snapshot
