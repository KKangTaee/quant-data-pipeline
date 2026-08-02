"""Point-in-time Treasury resistance zones, states, and driver lenses."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime
from statistics import median
from typing import Mapping, Sequence


@dataclass(frozen=True)
class ConfirmedPivot:
    """A pivot high that becomes usable only on its right-confirmation date."""

    pivot_date: str
    known_at_date: str
    value_pct: float
    timeframe_days: int


@dataclass(frozen=True)
class ResistanceZone:
    """A cluster of confirmed pivots, versionable at one as-of date."""

    zone_lower_pct: float
    zone_upper_pct: float
    tolerance_pct: float
    touch_count: int
    timeframes: tuple[int, ...]
    known_at_date: str
    as_of_date: str
    zone_strength: float


@dataclass(frozen=True)
class YieldDriverDecomposition:
    """Two non-additive explanatory lenses for one nominal 10-year move."""

    dominant_driver: str
    real_inflation_lens: dict[str, float]
    policy_term_lens: dict[str, float | None]


def _date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip()[:10])


def _finite(value: object, *, field: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def detect_confirmed_pivots(
    observations: Sequence[Mapping[str, object]],
    *,
    left_days: int,
    right_days: int,
    as_of_date: object,
    timeframe_days: int | None = None,
) -> tuple[ConfirmedPivot, ...]:
    """Detect strict highs and attach the first date they were knowable."""

    left = int(left_days)
    right = int(right_days)
    if left <= 0 or right <= 0:
        raise ValueError("pivot confirmation windows must be positive")
    cutoff = _date(as_of_date)
    normalized = sorted(
        (
            _date(row["observation_date"]),
            _finite(row["value"], field="observation value"),
        )
        for row in observations
        if _date(row["observation_date"]) <= cutoff
    )
    if len({item[0] for item in normalized}) != len(normalized):
        raise ValueError("observation dates must be unique")
    pivots: list[ConfirmedPivot] = []
    for index in range(left, len(normalized) - right):
        pivot_date, value = normalized[index]
        left_values = [item[1] for item in normalized[index - left : index]]
        right_values = [
            item[1] for item in normalized[index + 1 : index + right + 1]
        ]
        if value <= max(left_values) or value <= max(right_values):
            continue
        known_at = normalized[index + right][0]
        if known_at > cutoff:
            continue
        pivots.append(
            ConfirmedPivot(
                pivot_date=pivot_date.isoformat(),
                known_at_date=known_at.isoformat(),
                value_pct=value,
                timeframe_days=int(timeframe_days or len(normalized)),
            )
        )
    return tuple(pivots)


def adaptive_pivot_tolerance(
    observations: Sequence[Mapping[str, object]],
    *,
    lookback_days: int = 63,
    minimum_bp: float = 5.0,
) -> float:
    """Use the larger of 5bp and recent median absolute daily yield change."""

    values = [
        _finite(row["value"], field="observation value")
        for row in sorted(observations, key=lambda row: _date(row["observation_date"]))
    ][-max(2, int(lookback_days)) :]
    if len(values) < 2:
        return float(minimum_bp) / 100.0
    absolute_changes = [abs(current - previous) for previous, current in zip(values, values[1:])]
    return max(float(minimum_bp) / 100.0, float(median(absolute_changes)))


def cluster_resistance_zones(
    pivots: Sequence[ConfirmedPivot],
    *,
    tolerance_pct: float,
    as_of_date: object,
) -> tuple[ResistanceZone, ...]:
    """Cluster nearby confirmed highs without embedding any absolute yield level."""

    tolerance = _finite(tolerance_pct, field="tolerance_pct")
    if tolerance <= 0.0:
        raise ValueError("tolerance_pct must be positive")
    cutoff = _date(as_of_date)
    eligible = sorted(
        (pivot for pivot in pivots if _date(pivot.known_at_date) <= cutoff),
        key=lambda pivot: pivot.value_pct,
    )
    clusters: list[list[ConfirmedPivot]] = []
    for pivot in eligible:
        if not clusters:
            clusters.append([pivot])
            continue
        center = sum(item.value_pct for item in clusters[-1]) / len(clusters[-1])
        if abs(pivot.value_pct - center) <= tolerance:
            clusters[-1].append(pivot)
        else:
            clusters.append([pivot])
    zones: list[ResistanceZone] = []
    for cluster in clusters:
        timeframes = tuple(sorted({int(item.timeframe_days) for item in cluster}))
        touch_count = len({(item.pivot_date, item.value_pct) for item in cluster})
        recency_days = max(
            0,
            (cutoff - max(_date(item.pivot_date) for item in cluster)).days,
        )
        recency_score = 1.0 / (1.0 + recency_days / 252.0)
        strength = touch_count + 0.5 * (len(timeframes) - 1) + recency_score
        zones.append(
            ResistanceZone(
                zone_lower_pct=min(item.value_pct for item in cluster),
                zone_upper_pct=max(item.value_pct for item in cluster),
                tolerance_pct=tolerance,
                touch_count=touch_count,
                timeframes=timeframes,
                known_at_date=max(item.known_at_date for item in cluster),
                as_of_date=cutoff.isoformat(),
                zone_strength=float(strength),
            )
        )
    return tuple(sorted(zones, key=lambda zone: zone.zone_lower_pct))


def build_dynamic_resistance_zones(
    observations: Sequence[Mapping[str, object]],
    *,
    as_of_date: object,
    lookbacks: Sequence[int] = (63, 252, 504),
    left_days: int = 3,
    right_days: int = 3,
    minimum_bp: float = 5.0,
) -> tuple[ResistanceZone, ...]:
    """Build multi-timeframe zones using only pivots confirmed by the cutoff."""

    cutoff = _date(as_of_date)
    ordered = sorted(
        (row for row in observations if _date(row["observation_date"]) <= cutoff),
        key=lambda row: _date(row["observation_date"]),
    )
    pivots: list[ConfirmedPivot] = []
    for lookback in lookbacks:
        window = ordered[-int(lookback) :]
        pivots.extend(
            detect_confirmed_pivots(
                window,
                left_days=left_days,
                right_days=right_days,
                as_of_date=cutoff,
                timeframe_days=int(lookback),
            )
        )
    tolerance = adaptive_pivot_tolerance(
        ordered,
        lookback_days=min(63, len(ordered)),
        minimum_bp=minimum_bp,
    )
    return cluster_resistance_zones(
        pivots,
        tolerance_pct=tolerance,
        as_of_date=cutoff,
    )


def classify_resistance_state(
    recent_values_pct: Sequence[object],
    *,
    zone_lower_pct: float,
    zone_upper_pct: float,
    buffer_pct: float,
    prior_state: str | None = None,
    hold_days: int = 5,
) -> str | None:
    """Apply point-in-time approach, attempt, confirmation, hold, and failure rules."""

    values = tuple(_finite(value, field="recent yield") for value in recent_values_pct)
    if not values:
        raise ValueError("recent_values_pct cannot be empty")
    lower = _finite(zone_lower_pct, field="zone_lower_pct")
    upper = _finite(zone_upper_pct, field="zone_upper_pct")
    buffer = _finite(buffer_pct, field="buffer_pct")
    if lower > upper or buffer < 0.0 or int(hold_days) <= 0:
        raise ValueError("zone and hold configuration is invalid")
    latest = values[-1]
    engaged_states = {"ATTEMPT", "CONFIRMED", "HOLD"}
    if prior_state in engaged_states and latest < lower - buffer:
        return "FAILED"
    if prior_state in {"CONFIRMED", "HOLD"} and len(values) >= int(hold_days):
        if all(value > upper + buffer for value in values[-int(hold_days) :]):
            return "HOLD"
    confirmation_window = values[-5:]
    if sum(value > upper + buffer for value in confirmation_window) >= 3:
        return "CONFIRMED"
    if any(value > upper + buffer for value in confirmation_window):
        return "ATTEMPT"
    if latest >= lower - buffer:
        return "APPROACH"
    return None


def decompose_yield_driver(
    *,
    nominal_10y_change_bp: float,
    two_year_change_bp: float,
    real_10y_change_bp: float,
    breakeven_10y_change_bp: float,
    term_premium_change_bp: float | None,
    dominance_ratio: float = 0.60,
) -> YieldDriverDecomposition:
    """Classify a move while keeping real/inflation and policy/term lenses separate."""

    nominal = _finite(nominal_10y_change_bp, field="nominal_10y_change_bp")
    two_year = _finite(two_year_change_bp, field="two_year_change_bp")
    real = _finite(real_10y_change_bp, field="real_10y_change_bp")
    breakeven = _finite(
        breakeven_10y_change_bp, field="breakeven_10y_change_bp"
    )
    term = (
        None
        if term_premium_change_bp is None
        else _finite(term_premium_change_bp, field="term_premium_change_bp")
    )
    ratio = _finite(dominance_ratio, field="dominance_ratio")
    scale = max(abs(nominal), 1e-9)
    if breakeven > 0.0 and breakeven / scale >= ratio and breakeven > real:
        driver = "inflation_driven"
    elif real > 0.0 and real / scale >= ratio:
        driver = "real_growth_driven"
    elif term is not None and term > 0.0 and term / scale >= ratio:
        driver = "term_premium_driven"
    elif two_year > 0.0 and two_year / scale >= ratio:
        driver = "policy_driven"
    else:
        driver = "mixed"
    return YieldDriverDecomposition(
        dominant_driver=driver,
        real_inflation_lens={
            "real_10y_change_bp": real,
            "breakeven_10y_change_bp": breakeven,
            "identity_gap_bp": nominal - real - breakeven,
        },
        policy_term_lens={
            "two_year_policy_proxy_change_bp": two_year,
            "term_premium_change_bp": term,
        },
    )


def evaluate_inflation_confirmation(
    *,
    resistance_state: str | None,
    dominant_driver: str,
    breakeven_confirmed: bool,
    reacceleration_probability_before: float,
    reacceleration_probability_after: float,
    term_premium_only: bool,
) -> str:
    """Require joint rate-driver and inflation evidence; a 10-year break is insufficient."""

    if resistance_state not in {"CONFIRMED", "HOLD"} or term_premium_only:
        return "UNCONFIRMED"
    before = _finite(
        reacceleration_probability_before,
        field="reacceleration_probability_before",
    )
    after = _finite(
        reacceleration_probability_after,
        field="reacceleration_probability_after",
    )
    probability_rose = after > before
    if dominant_driver == "inflation_driven" and breakeven_confirmed and probability_rose:
        return "INFLATION_CONFIRMED"
    if dominant_driver in {"inflation_driven", "mixed"} and (
        breakeven_confirmed or probability_rose
    ):
        return "MIXED"
    return "UNCONFIRMED"
