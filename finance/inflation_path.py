"""Core PCE index-path math and versioned inflation-state projections."""

from __future__ import annotations

import hashlib
import math
from dataclasses import dataclass
from datetime import date, datetime
from typing import Mapping, Sequence

import numpy as np


INFLATION_STATES = (
    "rapid_disinflation",
    "gradual_disinflation",
    "sticky",
    "reacceleration",
    "shock_reacceleration",
)


@dataclass(frozen=True)
class InflationStateDefinition:
    """A release-specific projection vocabulary derived from one SEP."""

    definition_version: str
    target_period: str
    sep_released_at: str
    sep_center_pct: float
    forecast_error_pct: float
    price_stability_target_pct: float
    boundaries_pct: tuple[float, float, float, float]


@dataclass(frozen=True)
class CorePCEPathForecast:
    """Compact monthly and year-end distribution from auditable path samples."""

    monthly_mom_quantiles_pct: dict[str, dict[str, float]]
    monthly_index_quantiles: dict[str, dict[str, float]]
    q4_quantiles_pct: dict[str, float]
    q4_samples_pct: tuple[float, ...]
    state_probabilities: dict[str, float]
    threshold_probabilities: dict[str, float]
    component_weights: dict[str, float]
    state_definition_version: str


def _month(value: object) -> date:
    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    else:
        parsed = date.fromisoformat(str(value).strip()[:10])
    return parsed.replace(day=1)


def _finite_positive(value: object, *, field: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed) or parsed <= 0.0:
        raise ValueError(f"{field} must be finite and positive")
    return parsed


def _normalized_levels(levels: Mapping[object, object]) -> dict[date, float]:
    normalized: dict[date, float] = {}
    for raw_month, raw_value in levels.items():
        month = _month(raw_month)
        if month in normalized:
            raise ValueError(f"duplicate monthly index level: {month.isoformat()}")
        normalized[month] = _finite_positive(raw_value, field="index level")
    if not normalized:
        raise ValueError("index levels cannot be empty")
    return normalized


def calculate_q4_over_q4(levels: Mapping[object, object], *, year: int) -> float:
    """Calculate SEP-style Q4/Q4 inflation from monthly index levels."""

    normalized = _normalized_levels(levels)
    current = [date(int(year), month, 1) for month in (10, 11, 12)]
    previous = [date(int(year) - 1, month, 1) for month in (10, 11, 12)]
    missing = [month for month in (*previous, *current) if month not in normalized]
    if missing:
        raise ValueError(
            "Q4/Q4 requires previous and current October-December levels: "
            + ", ".join(item.isoformat() for item in missing)
        )
    current_mean = sum(normalized[item] for item in current) / 3.0
    previous_mean = sum(normalized[item] for item in previous) / 3.0
    return (current_mean / previous_mean - 1.0) * 100.0


def project_index_levels(
    levels: Mapping[object, object],
    *,
    monthly_mom_pct: Mapping[object, object],
) -> dict[date, float]:
    """Extend a known index path through consecutive monthly percentage changes."""

    projected = _normalized_levels(levels)
    forecast = sorted(
        (_month(raw_month), float(raw_value))
        for raw_month, raw_value in monthly_mom_pct.items()
    )
    if not forecast:
        return projected
    previous_month = max(projected)
    previous_level = projected[previous_month]
    for month, mom_pct in forecast:
        if not math.isfinite(mom_pct) or mom_pct <= -100.0:
            raise ValueError("monthly MoM values must be finite and greater than -100")
        expected_year = previous_month.year + (1 if previous_month.month == 12 else 0)
        expected_month = 1 if previous_month.month == 12 else previous_month.month + 1
        expected = date(expected_year, expected_month, 1)
        if month != expected:
            raise ValueError("forecast months must be consecutive after the last known level")
        previous_level *= 1.0 + mom_pct / 100.0
        projected[month] = previous_level
        previous_month = month
    return projected


def required_constant_mom_for_q4_target(
    levels: Mapping[object, object],
    *,
    forecast_months: Sequence[object],
    target_q4_over_q4: float,
    lower_bound_pct: float = -2.0,
    upper_bound_pct: float = 2.0,
) -> float:
    """Numerically solve the constant remaining MoM path for one Q4/Q4 target."""

    months = tuple(_month(value) for value in forecast_months)
    if not months:
        raise ValueError("forecast_months cannot be empty")
    target = float(target_q4_over_q4)
    if not math.isfinite(target):
        raise ValueError("target_q4_over_q4 must be finite")
    normalized = _normalized_levels(levels)
    target_year = months[-1].year

    def objective(mom_pct: float) -> float:
        projected = project_index_levels(
            normalized,
            monthly_mom_pct={month: mom_pct for month in months},
        )
        return calculate_q4_over_q4(projected, year=target_year) - target

    lower = float(lower_bound_pct)
    upper = float(upper_bound_pct)
    lower_value = objective(lower)
    upper_value = objective(upper)
    if lower_value == 0.0:
        return lower
    if upper_value == 0.0:
        return upper
    if lower_value * upper_value > 0.0:
        raise ValueError("target is outside the configured monthly MoM search interval")
    for _ in range(100):
        midpoint = (lower + upper) / 2.0
        midpoint_value = objective(midpoint)
        if abs(midpoint_value) <= 1e-12:
            return midpoint
        if lower_value * midpoint_value <= 0.0:
            upper = midpoint
        else:
            lower = midpoint
            lower_value = midpoint_value
    return (lower + upper) / 2.0


def derive_state_definition(
    sep_rows: Sequence[Mapping[str, object]],
    *,
    target_period: str,
    forecast_error_pct: float,
    price_stability_target_pct: float,
) -> InflationStateDefinition:
    """Derive versioned five-state boundaries from the latest eligible SEP marginal."""

    error = _finite_positive(forecast_error_pct, field="forecast_error_pct")
    target = float(price_stability_target_pct)
    if not math.isfinite(target):
        raise ValueError("price_stability_target_pct must be finite")
    eligible = [
        dict(row)
        for row in sep_rows
        if str(row.get("target_period")) == str(target_period)
        and str(row.get("variable_name")) == "core_pce"
        and str(row.get("distribution_kind")) == "HISTOGRAM"
        and row.get("released_at") not in (None, "")
    ]
    if not eligible:
        raise ValueError("eligible Core PCE SEP histogram is required")
    latest_release = max(str(row["released_at"]) for row in eligible)
    release_rows = [row for row in eligible if str(row["released_at"]) == latest_release]
    weighted: list[tuple[float, int]] = []
    for row in release_rows:
        lower = float(row["bin_lower_pct"])
        upper = float(row["bin_upper_pct"])
        count = int(row["participant_count"])
        if not all(math.isfinite(value) for value in (lower, upper)) or lower > upper:
            raise ValueError("SEP histogram bins must be finite ordered ranges")
        if count < 0:
            raise ValueError("SEP participant counts cannot be negative")
        if count:
            weighted.append(((lower + upper) / 2.0, count))
    total = sum(count for _midpoint, count in weighted)
    if total <= 0:
        raise ValueError("SEP histogram must contain positive participant mass")
    cumulative = 0
    center = 0.0
    for midpoint, count in sorted(weighted):
        cumulative += count
        if cumulative >= total / 2.0:
            center = midpoint
            break
    # Anchor the middle transition at no less than the long-run target, then
    # expand outward. This preserves the high-inflation SEP spacing while
    # remaining ordered when the SEP median converges to or undershoots target.
    gradual_upper = max(target, center - error)
    rapid_upper = gradual_upper - error
    sticky_upper = max(center + error, gradual_upper + error)
    shock_lower = sticky_upper + 2.0 * error
    boundaries = (rapid_upper, gradual_upper, sticky_upper, shock_lower)
    if any(left >= right for left, right in zip(boundaries, boundaries[1:])):
        raise ValueError("SEP center and forecast error do not produce ordered states")
    rounded = tuple(round(value, 4) for value in boundaries)
    payload = "|".join(
        (
            latest_release,
            str(target_period),
            f"{center:.4f}",
            f"{error:.4f}",
            f"{target:.4f}",
            *(f"{value:.4f}" for value in rounded),
        )
    )
    release_stamp = latest_release[:10].replace("-", "")
    version = f"sep-{release_stamp}-{hashlib.sha256(payload.encode()).hexdigest()[:10]}"
    return InflationStateDefinition(
        definition_version=version,
        target_period=str(target_period),
        sep_released_at=latest_release,
        sep_center_pct=round(center, 4),
        forecast_error_pct=error,
        price_stability_target_pct=target,
        boundaries_pct=rounded,  # type: ignore[arg-type]
    )


def _finite_samples(samples: Sequence[object]) -> tuple[float, ...]:
    values = tuple(float(value) for value in samples)
    if not values or any(not math.isfinite(value) for value in values):
        raise ValueError("samples must be non-empty and finite")
    return values


def calculate_state_probabilities(
    q4_over_q4_samples: Sequence[object],
    definition: InflationStateDefinition,
) -> dict[str, float]:
    """Project continuous Q4/Q4 samples onto one versioned five-state vocabulary."""

    samples = _finite_samples(q4_over_q4_samples)
    boundaries = tuple(float(value) for value in definition.boundaries_pct)
    counts = {state: 0 for state in INFLATION_STATES}
    for sample in samples:
        if sample < boundaries[0]:
            state = INFLATION_STATES[0]
        elif sample < boundaries[1]:
            state = INFLATION_STATES[1]
        elif sample < boundaries[2]:
            state = INFLATION_STATES[2]
        elif sample < boundaries[3]:
            state = INFLATION_STATES[3]
        else:
            state = INFLATION_STATES[4]
        counts[state] += 1
    return {state: counts[state] / len(samples) for state in INFLATION_STATES}


def calculate_threshold_probabilities(
    q4_over_q4_samples: Sequence[object],
    thresholds_pct: Sequence[object],
) -> dict[str, float]:
    """Return exceedance probabilities without folding user levels into state labels."""

    samples = _finite_samples(q4_over_q4_samples)
    thresholds = tuple(float(value) for value in thresholds_pct)
    if any(not math.isfinite(value) for value in thresholds):
        raise ValueError("thresholds must be finite")
    return {
        f"{threshold:.4f}": sum(sample >= threshold for sample in samples)
        / len(samples)
        for threshold in thresholds
    }


def _quantiles(values: Sequence[float]) -> dict[str, float]:
    array = np.asarray(values, dtype=float)
    points = np.quantile(array, (0.05, 0.20, 0.50, 0.80, 0.95))
    return {
        label: float(value)
        for label, value in zip(
            ("p05", "p20", "p50", "p80", "p95"), points, strict=True
        )
    }


def simulate_core_pce_paths(
    levels: Mapping[object, object],
    *,
    forecast_months: Sequence[object],
    component_monthly_mom_pct: Mapping[str, Mapping[object, object]],
    component_weights: Mapping[str, object],
    residual_history_pct: Sequence[object],
    sample_count: int,
    seed: int,
    state_definition: InflationStateDefinition,
    thresholds_pct: Sequence[object],
    fixed_monthly_mom_pct: Mapping[object, object] | None = None,
) -> CorePCEPathForecast:
    """Simulate a weighted component mixture with bootstrapped predictive residuals."""

    months = tuple(_month(value) for value in forecast_months)
    if not months:
        raise ValueError("forecast_months cannot be empty")
    if int(sample_count) <= 0:
        raise ValueError("sample_count must be positive")
    residuals = tuple(float(value) for value in residual_history_pct)
    if not residuals or any(not math.isfinite(value) for value in residuals):
        raise ValueError("residual_history_pct must be non-empty and finite")
    component_names = tuple(sorted(str(name) for name in component_monthly_mom_pct))
    if not component_names or set(component_names) != set(component_weights):
        raise ValueError("component forecasts and weights must have identical names")
    weights = {name: float(component_weights[name]) for name in component_names}
    if any(not math.isfinite(value) or value < 0.0 for value in weights.values()):
        raise ValueError("component weights must be finite and non-negative")
    total_weight = sum(weights.values())
    if total_weight <= 0.0:
        raise ValueError("component weights must contain positive mass")
    weights = {name: value / total_weight for name, value in weights.items()}
    fixed = {
        _month(raw_month): float(raw_value)
        for raw_month, raw_value in (fixed_monthly_mom_pct or {}).items()
    }
    if not set(fixed).issubset(set(months)) or any(
        not math.isfinite(value) or value <= -100.0 for value in fixed.values()
    ):
        raise ValueError("fixed monthly scenarios must be finite requested months")

    components: dict[str, dict[date, float]] = {}
    for name in component_names:
        values = {
            _month(raw_month): float(raw_value)
            for raw_month, raw_value in component_monthly_mom_pct[name].items()
        }
        if set(values) != set(months):
            raise ValueError(f"component {name} must forecast every requested month")
        if any(not math.isfinite(value) or value <= -100.0 for value in values.values()):
            raise ValueError("component monthly forecasts must be finite and above -100")
        components[name] = values

    rng = np.random.default_rng(int(seed))
    choices = rng.choice(
        np.asarray(component_names, dtype=object),
        size=int(sample_count),
        p=np.asarray([weights[name] for name in component_names]),
    )
    monthly_mom_samples: dict[date, list[float]] = {month: [] for month in months}
    monthly_index_samples: dict[date, list[float]] = {month: [] for month in months}
    q4_samples: list[float] = []
    normalized_levels = _normalized_levels(levels)
    for raw_choice in choices:
        name = str(raw_choice)
        monthly_changes = {
            month: (
                fixed[month]
                if month in fixed
                else components[name][month] + float(rng.choice(residuals))
            )
            for month in months
        }
        projected = project_index_levels(
            normalized_levels,
            monthly_mom_pct=monthly_changes,
        )
        for month in months:
            monthly_mom_samples[month].append(monthly_changes[month])
            monthly_index_samples[month].append(projected[month])
        q4_samples.append(calculate_q4_over_q4(projected, year=months[-1].year))

    return CorePCEPathForecast(
        monthly_mom_quantiles_pct={
            month.isoformat(): _quantiles(monthly_mom_samples[month])
            for month in months
        },
        monthly_index_quantiles={
            month.isoformat(): _quantiles(monthly_index_samples[month])
            for month in months
        },
        q4_quantiles_pct=_quantiles(q4_samples),
        q4_samples_pct=tuple(q4_samples),
        state_probabilities=calculate_state_probabilities(q4_samples, state_definition),
        threshold_probabilities=calculate_threshold_probabilities(
            q4_samples, thresholds_pct
        ),
        component_weights=weights,
        state_definition_version=state_definition.definition_version,
    )
