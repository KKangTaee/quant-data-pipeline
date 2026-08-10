"""Empirical PIT rate-path library and joint inflation-policy copula paths."""

from __future__ import annotations

import math
from bisect import bisect_right
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Mapping, Sequence

import numpy as np

from finance.inflation_path import (
    calculate_q4_over_q4,
    required_constant_mom_for_q4_target,
)
from finance.inflation_policy_simulation import SimulationPath
from finance.inflation_policy_validation import (
    ContinuousValidationPrediction,
    calculate_continuous_metrics,
)
from finance.policy_path import POLICY_NET_MOVE_BUCKETS
from finance.yield_resistance import build_dynamic_resistance_zones


RATE_INSTRUMENTS = ("DGS2", "DGS10", "DFII10", "T10YIE")
RATE_SCALE_GRID = (1.0, 1.2, 1.4, 1.6, 1.8, 2.0)
_BUCKET_STEPS = {
    "cut_3_plus": -3,
    "cut_2": -2,
    "cut_1": -1,
    "hold": 0,
    "hike_1": 1,
    "hike_2": 2,
    "hike_3_plus": 3,
}


@dataclass(frozen=True)
class RateEpisode:
    """One month-end origin and its same-calendar-year realized rate path."""

    origin_date: date
    target_date: date
    origin_month: int
    current_rates: Mapping[str, float]
    endpoint_rates: Mapping[str, float]
    rate_paths_pct: Mapping[str, tuple[float, ...]]
    q4_core_pce_pct: float
    policy_net_steps: int


@dataclass(frozen=True)
class JointRatePathArtifact:
    """Validated empirical path parameters and current joint simulation draws."""

    trained_cutoff_at: str
    training_start_date: str
    trained_through_date: str
    current_observation_date: str | None
    rate_scales: dict[str, float]
    validation_metrics: dict[str, object]
    publication_status: str
    reason_codes: tuple[str, ...]
    paths: tuple[SimulationPath, ...]


def _timestamp(value: object) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _observation_date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip()[:10])


def _series_map(
    macro_rows: Sequence[Mapping[str, object]],
    *,
    cutoff_at: str | datetime | None = None,
) -> dict[str, tuple[tuple[date, float], ...]]:
    selected = set(RATE_INSTRUMENTS) | {"FEDFUNDS", "PCEPILFE"}
    cutoff = _timestamp(cutoff_at) if cutoff_at is not None else None
    values: dict[str, dict[date, tuple[datetime, float]]] = {
        series: {} for series in selected
    }
    for row in macro_rows:
        series = str(row.get("series_id") or "").strip().upper()
        if series not in selected or row.get("value") in (None, ""):
            continue
        try:
            observed = _observation_date(row["observation_date"])
            value = float(row["value"])
            released = _timestamp(row.get("released_at") or observed.isoformat())
        except (KeyError, TypeError, ValueError):
            continue
        if not math.isfinite(value):
            continue
        if cutoff is not None and (
            observed > cutoff.date() or released > cutoff
        ):
            continue
        current = values[series].get(observed)
        if current is None or released >= current[0]:
            values[series][observed] = (released, value)
    return {
        series: tuple(
            (observed, payload[1])
            for observed, payload in sorted(rows.items())
        )
        for series, rows in values.items()
    }


def _latest(
    rows: Sequence[tuple[date, float]], target: date
) -> tuple[date, float] | None:
    if not rows:
        return None
    dates = [item[0] for item in rows]
    index = bisect_right(dates, target) - 1
    return rows[index] if index >= 0 else None


def _native_path(
    rows: Sequence[tuple[date, float]], *, origin: date, target: date
) -> tuple[float, ...]:
    start = _latest(rows, origin)
    if start is None:
        return ()
    values = [start[1]]
    values.extend(value for observed, value in rows if origin < observed <= target)
    return tuple(values)


def build_rate_episodes(
    macro_rows: Sequence[Mapping[str, object]],
    *,
    cutoff_at: str,
) -> tuple[RateEpisode, ...]:
    """Build completed year-end episodes without using the current incomplete year."""

    cutoff = _timestamp(cutoff_at)
    series = _series_map(macro_rows, cutoff_at=cutoff)
    dgs10 = series["DGS10"]
    pce_levels = {observed.replace(day=1): value for observed, value in series["PCEPILFE"]}
    if not dgs10 or not pce_levels:
        return ()
    first_year = min(observed.year for observed, _value in dgs10)
    episodes: list[RateEpisode] = []
    for year in range(first_year, cutoff.year):
        december_dates = [
            observed
            for observed, _value in dgs10
            if observed.year == year and observed.month == 12
        ]
        if not december_dates:
            continue
        target_date = max(december_dates)
        try:
            q4 = calculate_q4_over_q4(pce_levels, year=year)
        except ValueError:
            continue
        for month in range(1, 12):
            origin_dates = [
                observed
                for observed, _value in dgs10
                if observed.year == year and observed.month == month
            ]
            if not origin_dates:
                continue
            origin_date = max(origin_dates)
            current_rates: dict[str, float] = {}
            endpoint_rates: dict[str, float] = {}
            paths: dict[str, tuple[float, ...]] = {}
            complete = True
            for instrument in RATE_INSTRUMENTS:
                current = _latest(series[instrument], origin_date)
                endpoint = _latest(series[instrument], target_date)
                path = _native_path(
                    series[instrument], origin=origin_date, target=target_date
                )
                if current is None or endpoint is None or len(path) < 2:
                    complete = False
                    break
                current_rates[instrument] = float(current[1])
                endpoint_rates[instrument] = float(endpoint[1])
                paths[instrument] = path
            current_policy = _latest(series["FEDFUNDS"], origin_date)
            end_policy = _latest(series["FEDFUNDS"], target_date)
            if not complete or current_policy is None or end_policy is None:
                continue
            raw_steps = (float(end_policy[1]) - float(current_policy[1])) * 4.0
            episodes.append(
                RateEpisode(
                    origin_date=origin_date,
                    target_date=target_date,
                    origin_month=month,
                    current_rates=current_rates,
                    endpoint_rates=endpoint_rates,
                    rate_paths_pct=paths,
                    q4_core_pce_pct=float(q4),
                    policy_net_steps=int(round(raw_steps)),
                )
            )
    return tuple(sorted(episodes, key=lambda row: row.origin_date))


def _resample(values: Sequence[float], *, size: int) -> np.ndarray:
    array = np.asarray(tuple(float(value) for value in values), dtype=float)
    if array.size < 2:
        raise ValueError("historical rate path requires at least two points")
    return np.interp(
        np.linspace(0.0, 1.0, int(size)),
        np.linspace(0.0, 1.0, array.size),
        array,
    )


def _scaled_endpoint_samples(
    origin: RateEpisode,
    candidates: Sequence[RateEpisode],
    *,
    instrument: str,
    scale: float,
) -> tuple[float, ...]:
    changes = np.asarray(
        [
            float(row.endpoint_rates[instrument])
            - float(row.current_rates[instrument])
            for row in candidates
        ],
        dtype=float,
    )
    median = float(np.median(changes))
    return tuple(
        float(origin.current_rates[instrument])
        + median
        + (float(change) - median) * float(scale)
        for change in changes
    )


def _prediction(
    origin: RateEpisode,
    candidates: Sequence[RateEpisode],
    *,
    instrument: str,
    scale: float,
) -> ContinuousValidationPrediction:
    samples = _scaled_endpoint_samples(
        origin, candidates, instrument=instrument, scale=scale
    )
    current = float(origin.current_rates[instrument])
    return ContinuousValidationPrediction(
        forecast_origin_at=origin.origin_date.isoformat(),
        target_available_at=origin.target_date.isoformat(),
        training_target_through_at=max(row.target_date for row in candidates).isoformat(),
        actual_value=float(origin.endpoint_rates[instrument]),
        predicted_median=float(np.median(np.asarray(samples))),
        predictive_samples=samples,
        baseline_prediction=current,
        baseline_samples=tuple(current for _item in samples),
        complete_feature_ratio=1.0,
    )


def _calibration_error(metrics: Mapping[str, object]) -> float:
    return max(
        abs(float(metrics["interval_50_coverage"]) - 0.50),
        abs(float(metrics["interval_80_coverage"]) - 0.80),
        abs(float(metrics["interval_95_coverage"]) - 0.95),
    )


def _select_rate_scale(
    episodes: Sequence[RateEpisode], *, instrument: str
) -> float:
    inner: list[tuple[RateEpisode, list[RateEpisode]]] = []
    for origin in episodes:
        candidates = [
            row
            for row in episodes
            if row.origin_date.year < origin.origin_date.year
            and abs(row.origin_month - origin.origin_month) <= 2
        ]
        if len(candidates) >= 10:
            inner.append((origin, candidates))
    if len(inner) < 10:
        return 1.0

    def score(scale: float) -> float:
        metrics = calculate_continuous_metrics(
            [
                _prediction(
                    origin,
                    candidates,
                    instrument=instrument,
                    scale=scale,
                )
                for origin, candidates in inner
            ]
        )
        return float(metrics["crps"]) + 0.30 * _calibration_error(metrics)

    return min(RATE_SCALE_GRID, key=score)


def validate_rate_episode_library(
    episodes: Sequence[RateEpisode],
) -> tuple[dict[str, object], dict[str, float]]:
    """Nested chronological validation with random-walk endpoint baselines."""

    ordered = tuple(sorted(episodes, key=lambda row: row.origin_date))
    instrument_metrics: dict[str, object] = {}
    final_scales: dict[str, float] = {}
    for instrument in RATE_INSTRUMENTS:
        predictions: list[ContinuousValidationPrediction] = []
        scale_cache: dict[int, float] = {}
        for origin in ordered:
            training = [
                row
                for row in ordered
                if row.origin_date.year < origin.origin_date.year
            ]
            candidates = [
                row
                for row in training
                if abs(row.origin_month - origin.origin_month) <= 2
            ]
            if len(candidates) < 20:
                continue
            scale = scale_cache.setdefault(
                origin.origin_date.year,
                _select_rate_scale(training, instrument=instrument),
            )
            predictions.append(
                _prediction(
                    origin,
                    candidates,
                    instrument=instrument,
                    scale=scale,
                )
            )
        if not predictions:
            continue
        metrics = calculate_continuous_metrics(predictions)
        instrument_metrics[instrument] = {
            **metrics,
            "origin_count": len(predictions),
            "calibration_error": _calibration_error(metrics),
        }
        final_scales[instrument] = _select_rate_scale(
            ordered, instrument=instrument
        )
    return {
        "instruments": instrument_metrics,
        "minimum_origin_count": min(
            (
                int(row["origin_count"])
                for row in instrument_metrics.values()
                if isinstance(row, Mapping)
            ),
            default=0,
        ),
    }, final_scales


def validate_dynamic_resistance_reach(
    episodes: Sequence[RateEpisode],
    dgs10_rows: Sequence[tuple[date, float]],
) -> dict[str, float]:
    """Validate empirical path reach probabilities against PIT dynamic zones."""

    ordered = tuple(sorted(episodes, key=lambda row: row.origin_date))
    probability_rows: list[tuple[float, float]] = []
    scale_cache: dict[int, float] = {}
    observations = [
        {"observation_date": observed.isoformat(), "value": value}
        for observed, value in dgs10_rows
    ]
    for origin in ordered:
        training = [
            row
            for row in ordered
            if row.origin_date.year < origin.origin_date.year
        ]
        candidates = [
            row
            for row in training
            if abs(row.origin_month - origin.origin_month) <= 2
        ]
        if len(candidates) < 20:
            continue
        history = [
            row
            for row in observations
            if str(row["observation_date"]) <= origin.origin_date.isoformat()
        ]
        zones = build_dynamic_resistance_zones(
            history, as_of_date=origin.origin_date
        )
        current = float(origin.current_rates["DGS10"])
        overhead = [zone for zone in zones if zone.zone_lower_pct > current]
        engaged = [
            zone
            for zone in zones
            if zone.zone_lower_pct - zone.tolerance_pct
            <= current
            <= zone.zone_upper_pct + zone.tolerance_pct
        ]
        selected = (
            min(overhead, key=lambda zone: zone.zone_lower_pct)
            if overhead
            else max(engaged, key=lambda zone: zone.zone_strength)
            if engaged
            else None
        )
        if selected is None:
            continue
        scale = scale_cache.setdefault(
            origin.origin_date.year,
            _select_rate_scale(training, instrument="DGS10"),
        )
        raw_deltas: list[np.ndarray] = []
        for candidate in candidates:
            sampled = _resample(candidate.rate_paths_pct["DGS10"], size=21)
            raw_deltas.append(sampled - sampled[0])
        center = np.median(np.asarray(raw_deltas), axis=0)
        projected = [
            current + center + scale * (raw_delta - center)
            for raw_delta in raw_deltas
        ]
        probability = sum(
            float(np.max(path)) >= float(selected.zone_lower_pct)
            for path in projected
        ) / len(projected)
        actual = float(
            max(origin.rate_paths_pct["DGS10"]) >= selected.zone_lower_pct
        )
        probability_rows.append((probability, actual))
    if not probability_rows:
        return {
            "origin_count": 0.0,
            "brier_score": math.inf,
            "baseline_brier_score": math.inf,
            "calibration_error": math.inf,
        }
    count = len(probability_rows)
    brier = sum((probability - actual) ** 2 for probability, actual in probability_rows) / count
    # A no-break random-walk baseline cannot reach an overhead zone without a
    # rate change; active zones are already reached by definition.
    baseline_brier = sum(actual**2 for _probability, actual in probability_rows) / count
    bins: list[list[tuple[float, float]]] = [[] for _index in range(10)]
    for probability, actual in probability_rows:
        index = min(9, max(0, math.ceil(probability * 10.0) - 1))
        bins[index].append((probability, actual))
    calibration_error = sum(
        len(members)
        / count
        * abs(
            sum(item[0] for item in members) / len(members)
            - sum(item[1] for item in members) / len(members)
        )
        for members in bins
        if members
    )
    return {
        "origin_count": float(count),
        "brier_score": float(brier),
        "baseline_brier_score": float(baseline_brier),
        "calibration_error": float(calibration_error),
        "event_rate": sum(actual for _probability, actual in probability_rows)
        / count,
        "mean_probability": sum(
            probability for probability, _actual in probability_rows
        )
        / count,
    }


def _normalized_policy_probabilities(
    values: Mapping[str, object],
) -> tuple[np.ndarray, np.ndarray]:
    unknown = set(values) - set(POLICY_NET_MOVE_BUCKETS)
    if unknown:
        raise ValueError("policy net-move probabilities contain unknown labels")
    probabilities = np.asarray(
        [float(values.get(label, 0.0)) for label in POLICY_NET_MOVE_BUCKETS],
        dtype=float,
    )
    if np.any(~np.isfinite(probabilities)) or np.any(probabilities < 0.0):
        raise ValueError("policy probabilities must be finite and non-negative")
    total = float(probabilities.sum())
    if total <= 0.0:
        raise ValueError("policy probabilities must contain positive mass")
    steps = np.asarray(
        [_BUCKET_STEPS[label] for label in POLICY_NET_MOVE_BUCKETS], dtype=int
    )
    return steps, probabilities / total


def _rank_assign(latent: np.ndarray, requested: np.ndarray) -> np.ndarray:
    result = np.empty_like(requested)
    result[np.argsort(latent, kind="stable")] = np.sort(requested)
    return result


def simulate_joint_rate_paths(
    episodes: Sequence[RateEpisode],
    *,
    q4_samples_pct: Sequence[object],
    policy_net_move_probabilities: Mapping[str, object],
    current_rates: Mapping[str, object],
    current_policy_midpoint_pct: float,
    levels: Mapping[object, object],
    forecast_months: Sequence[object],
    rate_scales: Mapping[str, object],
    sample_count: int,
    seed: int,
) -> tuple[SimulationPath, ...]:
    """Apply empirical ranks while preserving validated current marginals."""

    library = tuple(episodes)
    if not library or int(sample_count) <= 0:
        raise ValueError("rate episodes and a positive sample_count are required")
    count = int(sample_count)
    q4_values = np.asarray(tuple(float(item) for item in q4_samples_pct), dtype=float)
    if q4_values.size == 0 or np.any(~np.isfinite(q4_values)):
        raise ValueError("q4 samples must be non-empty and finite")
    rates = {instrument: float(current_rates[instrument]) for instrument in RATE_INSTRUMENTS}
    if any(not math.isfinite(value) for value in rates.values()):
        raise ValueError("current rates must be finite")
    steps, policy_probabilities = _normalized_policy_probabilities(
        policy_net_move_probabilities
    )
    rng = np.random.default_rng(int(seed))
    chosen_indices = rng.integers(0, len(library), size=count)
    chosen = [library[int(index)] for index in chosen_indices]
    q4_draws = rng.choice(
        q4_values,
        size=count,
        replace=q4_values.size < count,
    )
    policy_draws = rng.choice(
        steps, size=count, replace=True, p=policy_probabilities
    )
    assigned_q4 = _rank_assign(
        np.asarray([row.q4_core_pce_pct for row in chosen], dtype=float),
        np.asarray(q4_draws, dtype=float),
    )
    assigned_policy = _rank_assign(
        np.asarray([row.policy_net_steps for row in chosen], dtype=float),
        np.asarray(policy_draws, dtype=float),
    ).astype(int)
    path_points = max(5, len(tuple(forecast_months)) * 4 + 1)
    median_deltas: dict[str, np.ndarray] = {}
    for instrument in RATE_INSTRUMENTS:
        deltas = []
        for row in library:
            sampled = _resample(row.rate_paths_pct[instrument], size=path_points)
            deltas.append(sampled - sampled[0])
        median_deltas[instrument] = np.median(np.asarray(deltas), axis=0)

    paths: list[SimulationPath] = []
    for index, historical in enumerate(chosen):
        rate_paths: dict[str, tuple[float, ...]] = {}
        for instrument in RATE_INSTRUMENTS:
            sampled = _resample(
                historical.rate_paths_pct[instrument], size=path_points
            )
            raw_delta = sampled - sampled[0]
            center = median_deltas[instrument]
            scale = float(rate_scales[instrument])
            projected = rates[instrument] + center + scale * (raw_delta - center)
            projected[0] = rates[instrument]
            rate_paths[instrument] = tuple(float(value) for value in projected)
        q4 = float(assigned_q4[index])
        required_mom = required_constant_mom_for_q4_target(
            levels,
            forecast_months=forecast_months,
            target_q4_over_q4=q4,
        )
        policy_steps = int(assigned_policy[index])
        paths.append(
            SimulationPath(
                path_id=f"joint-{index:05d}",
                weight=1.0 / count,
                q4_core_pce_pct=q4,
                remaining_monthly_mom_pct=tuple(
                    required_mom for _month in forecast_months
                ),
                policy_net_steps=policy_steps,
                year_end_policy_midpoint_pct=(
                    float(current_policy_midpoint_pct) + 0.25 * policy_steps
                ),
                rate_paths_pct=rate_paths,
            )
        )
    return tuple(paths)


def fit_joint_rate_path_artifact(
    *,
    macro_rows: Sequence[Mapping[str, object]],
    q4_samples_pct: Sequence[object],
    policy_net_move_probabilities: Mapping[str, object],
    levels: Mapping[object, object],
    forecast_months: Sequence[object],
    current_policy_midpoint_pct: float,
    as_of_at: str,
    sample_count: int = 2_000,
    seed: int = 20260803,
    minimum_origins: int = 48,
    maximum_calibration_error: float = 0.25,
) -> JointRatePathArtifact:
    """Validate empirical rate changes, then materialize current joint paths."""

    cutoff = _timestamp(as_of_at)
    empty = JointRatePathArtifact(
        trained_cutoff_at=cutoff.isoformat(),
        training_start_date="",
        trained_through_date="",
        current_observation_date=None,
        rate_scales={},
        validation_metrics={},
        publication_status="NOT_AVAILABLE",
        reason_codes=("rate_episode_library_missing",),
        paths=(),
    )
    episodes = build_rate_episodes(macro_rows, cutoff_at=cutoff.isoformat())
    if not episodes:
        return empty
    validation, scales = validate_rate_episode_library(episodes)
    series = _series_map(macro_rows, cutoff_at=cutoff)
    reach_validation = validate_dynamic_resistance_reach(
        episodes, series["DGS10"]
    )
    validation["dynamic_resistance_reach"] = reach_validation
    reasons: list[str] = []
    if int(validation.get("minimum_origin_count") or 0) < int(minimum_origins):
        reasons.append("insufficient_joint_rate_origins")
    instrument_metrics = validation.get("instruments")
    if not isinstance(instrument_metrics, Mapping) or set(instrument_metrics) != set(
        RATE_INSTRUMENTS
    ):
        reasons.append("joint_rate_instrument_validation_missing")
    else:
        for instrument in RATE_INSTRUMENTS:
            metrics = instrument_metrics[instrument]
            if not isinstance(metrics, Mapping):
                reasons.append(f"{instrument.lower()}_validation_missing")
                continue
            if not (
                float(metrics["crps"]) < float(metrics["baseline_crps"])
            ):
                reasons.append(f"{instrument.lower()}_no_baseline_improvement")
            if float(metrics["calibration_error"]) > float(
                maximum_calibration_error
            ):
                reasons.append(f"{instrument.lower()}_calibration_error_too_high")
    if int(reach_validation.get("origin_count") or 0) < 48:
        reasons.append("insufficient_resistance_event_origins")
    reach_brier = reach_validation.get("brier_score")
    reach_baseline_brier = reach_validation.get("baseline_brier_score")
    if (
        reach_brier is None
        or reach_baseline_brier is None
        or float(reach_brier) >= float(reach_baseline_brier)
    ):
        reasons.append("resistance_event_no_baseline_improvement")
    reach_calibration_error = reach_validation.get("calibration_error")
    if reach_calibration_error is None or float(reach_calibration_error) > float(
        maximum_calibration_error
    ):
        reasons.append("resistance_event_calibration_error_too_high")
    latest_rates = {
        instrument: _latest(series[instrument], cutoff.date())
        for instrument in RATE_INSTRUMENTS
    }
    if any(value is None for value in latest_rates.values()):
        reasons.append("current_rate_inputs_missing")
    current_observation = latest_rates["DGS10"]
    candidate_month = current_observation[0].month if current_observation else 0
    candidates = tuple(
        row
        for row in episodes
        if abs(row.origin_month - candidate_month) <= 2
    )
    if len(candidates) < 20:
        reasons.append("current_horizon_episode_support_too_small")
    paths: tuple[SimulationPath, ...] = ()
    if not reasons:
        paths = simulate_joint_rate_paths(
            candidates,
            q4_samples_pct=q4_samples_pct,
            policy_net_move_probabilities=policy_net_move_probabilities,
            current_rates={
                instrument: latest_rates[instrument][1]  # type: ignore[index]
                for instrument in RATE_INSTRUMENTS
            },
            current_policy_midpoint_pct=current_policy_midpoint_pct,
            levels=levels,
            forecast_months=forecast_months,
            rate_scales=scales,
            sample_count=sample_count,
            seed=seed,
        )
    status = "READY" if not reasons else "LIMITED"
    return JointRatePathArtifact(
        trained_cutoff_at=cutoff.isoformat(),
        training_start_date=min(row.origin_date for row in episodes).isoformat(),
        trained_through_date=max(row.target_date for row in episodes).isoformat(),
        current_observation_date=(
            current_observation[0].isoformat() if current_observation else None
        ),
        rate_scales=scales,
        validation_metrics={
            **validation,
            "joint_path_publication_status": status,
            "episode_count": len(episodes),
            "current_horizon_episode_count": len(candidates),
            "reverse_minimum_supporting_paths": max(20, int(sample_count) // 100),
            "reverse_minimum_effective_paths": max(10.0, float(sample_count) / 200.0),
        },
        publication_status=status,
        reason_codes=tuple(reasons),
        paths=paths,
    )
