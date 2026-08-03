"""Forward rate-path composition and reverse conditional scenario summaries."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping, Sequence


JOINT_PATH_COMPONENT = "joint_macro_paths"


@dataclass(frozen=True)
class RatePathProjection:
    """A 2-year path and two separate explanatory 10-year lenses."""

    two_year_path_pct: tuple[float, ...]
    ten_year_policy_term_lens_pct: tuple[float, ...]
    ten_year_real_inflation_lens_pct: tuple[float, ...]
    ten_year_path_pct: tuple[float, ...]


@dataclass(frozen=True)
class SimulationPath:
    """One auditable joint draw across inflation, policy, and rate paths."""

    path_id: str
    weight: float
    q4_core_pce_pct: float
    remaining_monthly_mom_pct: tuple[float, ...]
    policy_net_steps: int
    year_end_policy_midpoint_pct: float
    rate_paths_pct: Mapping[str, tuple[float, ...]]


@dataclass(frozen=True)
class RateTargetCondition:
    instrument: str
    zone_lower_pct: float
    zone_upper_pct: float
    condition: str
    buffer_pct: float
    hold_days: int


@dataclass(frozen=True)
class ReverseScenarioSummary:
    status: str
    target_probability: float
    supporting_path_count: int
    effective_path_count: float
    q4_core_pce_quantiles_pct: dict[str, float] | None
    required_remaining_mom_quantiles_pct: dict[str, float] | None
    policy_net_step_probabilities: dict[str, float] | None
    year_end_policy_target_probabilities: dict[str, float] | None


def _finite(value: object, *, field: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _finite_path(values: Sequence[object], *, field: str) -> tuple[float, ...]:
    path = tuple(_finite(value, field=field) for value in values)
    if not path:
        raise ValueError(f"{field} cannot be empty")
    return path


def compose_rate_path(
    *,
    expected_two_year_path_pct: Sequence[object],
    expected_short_rate_path_pct: Sequence[object],
    term_premium_path_pct: Sequence[object],
    real_10y_path_pct: Sequence[object],
    breakeven_10y_path_pct: Sequence[object],
    policy_term_weight: float,
    real_inflation_weight: float,
) -> RatePathProjection:
    """Blend calibrated lenses; never map one 25bp policy step to 25bp at 10 years."""

    two_year = _finite_path(expected_two_year_path_pct, field="two-year path")
    short_rate = _finite_path(
        expected_short_rate_path_pct, field="expected short-rate path"
    )
    term = _finite_path(term_premium_path_pct, field="term-premium path")
    real = _finite_path(real_10y_path_pct, field="real 10-year path")
    breakeven = _finite_path(
        breakeven_10y_path_pct, field="breakeven 10-year path"
    )
    lengths = {len(two_year), len(short_rate), len(term), len(real), len(breakeven)}
    if len(lengths) != 1:
        raise ValueError("all rate paths must have the same horizon length")
    policy_weight = _finite(policy_term_weight, field="policy_term_weight")
    real_weight = _finite(real_inflation_weight, field="real_inflation_weight")
    if policy_weight < 0.0 or real_weight < 0.0 or policy_weight + real_weight <= 0.0:
        raise ValueError("rate-lens weights must contain positive non-negative mass")
    total = policy_weight + real_weight
    policy_weight /= total
    real_weight /= total
    policy_lens = tuple(
        short_value + term_value
        for short_value, term_value in zip(short_rate, term, strict=True)
    )
    real_lens = tuple(
        real_value + breakeven_value
        for real_value, breakeven_value in zip(real, breakeven, strict=True)
    )
    ten_year = tuple(
        round(policy_weight * policy_value + real_weight * real_value, 10)
        for policy_value, real_value in zip(policy_lens, real_lens, strict=True)
    )
    return RatePathProjection(
        two_year_path_pct=two_year,
        ten_year_policy_term_lens_pct=policy_lens,
        ten_year_real_inflation_lens_pct=real_lens,
        ten_year_path_pct=ten_year,
    )


def _normalized_paths(paths: Sequence[SimulationPath]) -> tuple[tuple[SimulationPath, float], ...]:
    if not paths:
        raise ValueError("simulation paths cannot be empty")
    raw: list[tuple[SimulationPath, float]] = []
    for path in paths:
        weight = _finite(path.weight, field="path weight")
        if weight < 0.0:
            raise ValueError("path weights cannot be negative")
        _finite(path.q4_core_pce_pct, field="q4_core_pce_pct")
        _finite(path.year_end_policy_midpoint_pct, field="year_end midpoint")
        if not path.remaining_monthly_mom_pct:
            raise ValueError("remaining monthly path cannot be empty")
        raw.append((path, weight))
    total = sum(weight for _path, weight in raw)
    if total <= 0.0:
        raise ValueError("simulation paths must contain positive mass")
    return tuple((path, weight / total) for path, weight in raw)


def _condition_matches(path: SimulationPath, target: RateTargetCondition) -> bool:
    if target.instrument not in path.rate_paths_pct:
        raise ValueError(f"path {path.path_id} is missing {target.instrument}")
    values = _finite_path(
        path.rate_paths_pct[target.instrument], field=f"{target.instrument} path"
    )
    lower = _finite(target.zone_lower_pct, field="zone_lower_pct")
    upper = _finite(target.zone_upper_pct, field="zone_upper_pct")
    buffer = _finite(target.buffer_pct, field="buffer_pct")
    if lower > upper or buffer < 0.0 or int(target.hold_days) <= 0:
        raise ValueError("target zone configuration is invalid")
    condition = str(target.condition).upper()
    if condition == "REACH":
        return max(values) >= lower
    if condition == "BREAK":
        return sum(value > upper + buffer for value in values[-5:]) >= 3
    if condition == "HOLD":
        return len(values) >= int(target.hold_days) and all(
            value > upper + buffer for value in values[-int(target.hold_days) :]
        )
    raise ValueError("target condition must be REACH, BREAK, or HOLD")


def calculate_target_probability(
    paths: Sequence[SimulationPath],
    target: RateTargetCondition,
) -> float:
    """Return the total normalized likelihood mass that satisfies a rate target."""

    return sum(
        weight for path, weight in _normalized_paths(paths) if _condition_matches(path, target)
    )


def _weighted_quantiles(
    values: Sequence[float],
    weights: Sequence[float],
) -> dict[str, float]:
    ordered = sorted(zip(values, weights, strict=True), key=lambda item: item[0])
    total = sum(weight for _value, weight in ordered)
    if total <= 0.0:
        raise ValueError("weighted quantiles require positive mass")
    labels = (("p05", 0.05), ("p20", 0.20), ("p50", 0.50), ("p80", 0.80), ("p95", 0.95))
    result: dict[str, float] = {}
    for label, quantile in labels:
        threshold = quantile * total
        cumulative = 0.0
        selected = ordered[-1][0]
        for value, weight in ordered:
            cumulative += weight
            if cumulative + 1e-15 >= threshold:
                selected = value
                break
        result[label] = float(selected)
    return result


def _policy_step_label(steps: int) -> str:
    if steps <= -3:
        return "cut_3_plus"
    if steps == -2:
        return "cut_2"
    if steps == -1:
        return "cut_1"
    if steps == 0:
        return "hold"
    if steps == 1:
        return "hike_1"
    if steps == 2:
        return "hike_2"
    return "hike_3_plus"


def condition_paths_on_target(
    paths: Sequence[SimulationPath],
    target: RateTargetCondition,
    *,
    minimum_supporting_paths: int,
    minimum_effective_paths: float,
) -> ReverseScenarioSummary:
    """Summarize target-consistent paths or fail closed when conditional support is sparse."""

    normalized = _normalized_paths(paths)
    selected = [
        (path, weight)
        for path, weight in normalized
        if _condition_matches(path, target)
    ]
    target_probability = sum(weight for _path, weight in selected)
    if target_probability > 0.0:
        conditional = [
            (path, weight / target_probability) for path, weight in selected
        ]
        effective = 1.0 / sum(weight**2 for _path, weight in conditional)
    else:
        conditional = []
        effective = 0.0
    if (
        len(selected) < int(minimum_supporting_paths)
        or effective < float(minimum_effective_paths)
    ):
        return ReverseScenarioSummary(
            status="NOT_AVAILABLE",
            target_probability=target_probability,
            supporting_path_count=len(selected),
            effective_path_count=effective,
            q4_core_pce_quantiles_pct=None,
            required_remaining_mom_quantiles_pct=None,
            policy_net_step_probabilities=None,
            year_end_policy_target_probabilities=None,
        )

    conditional_weights = [weight for _path, weight in conditional]
    policy: dict[str, float] = {}
    targets: dict[str, float] = {}
    for path, weight in conditional:
        step_label = _policy_step_label(int(path.policy_net_steps))
        policy[step_label] = policy.get(step_label, 0.0) + weight
        target_label = f"{path.year_end_policy_midpoint_pct:.4f}"
        targets[target_label] = targets.get(target_label, 0.0) + weight
    return ReverseScenarioSummary(
        status="AVAILABLE",
        target_probability=target_probability,
        supporting_path_count=len(selected),
        effective_path_count=effective,
        q4_core_pce_quantiles_pct=_weighted_quantiles(
            [path.q4_core_pce_pct for path, _weight in conditional],
            conditional_weights,
        ),
        required_remaining_mom_quantiles_pct=_weighted_quantiles(
            [
                sum(path.remaining_monthly_mom_pct)
                / len(path.remaining_monthly_mom_pct)
                for path, _weight in conditional
            ],
            conditional_weights,
        ),
        policy_net_step_probabilities=policy,
        year_end_policy_target_probabilities=targets,
    )


def posterior_target_probability_for_next_pce(
    paths: Sequence[SimulationPath],
    target: RateTargetCondition,
    *,
    observed_mom_pct: float,
    observation_noise_pct: float,
) -> float:
    """Reweight joint paths by a proposed next print instead of firing a threshold rule."""

    observed = _finite(observed_mom_pct, field="observed_mom_pct")
    noise = _finite(observation_noise_pct, field="observation_noise_pct")
    if noise <= 0.0:
        raise ValueError("observation_noise_pct must be positive")
    weighted: list[tuple[SimulationPath, float]] = []
    for path, prior_weight in _normalized_paths(paths):
        expected = _finite(
            path.remaining_monthly_mom_pct[0], field="next path MoM"
        )
        likelihood = math.exp(-0.5 * ((observed - expected) / noise) ** 2)
        weighted.append((path, prior_weight * likelihood))
    denominator = sum(weight for _path, weight in weighted)
    if denominator <= 0.0:
        raise ValueError("next PCE scenario has no supported likelihood mass")
    return sum(
        weight
        for path, weight in weighted
        if _condition_matches(path, target)
    ) / denominator
