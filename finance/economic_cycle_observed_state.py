"""Deterministic point-in-time economic-cycle state and transition evidence."""

from __future__ import annotations

import math
from dataclasses import dataclass
from typing import Mapping

import pandas as pd


REAL_ECONOMY_SERIES = (
    "INDPRO",
    "W875RX1",
    "RRSFS",
    "CFNAI",
    "PAYEMS",
    "UNRATE",
    "ICSA",
    "AWHMAN",
)
PHASE_SEQUENCE = ("recovery", "expansion", "slowdown", "contraction")
RECENT_CHANGE_HORIZONS = (1, 3, 6)


@dataclass(frozen=True)
class ObservedStateResult:
    """One materializable observed-state record and its decision evidence."""

    observed_state: dict[str, object]
    recent_changes: tuple[dict[str, object], ...]
    transition_monitor: dict[str, object]


def _finite(value: object) -> float | None:
    try:
        parsed = float(value)
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _origin_text(value: object) -> str:
    parsed = pd.Timestamp(value)
    if parsed.tzinfo is not None:
        parsed = parsed.tz_convert(None)
    return parsed.date().isoformat()


def phase_from_coordinates(level: float, momentum: float) -> str:
    """Map an actual level/momentum coordinate to one growth-cycle quadrant."""

    if level < 0.0:
        return "recovery" if momentum >= 0.0 else "contraction"
    return "expansion" if momentum >= 0.0 else "slowdown"


def _prepare_panel(panel: pd.DataFrame) -> pd.DataFrame:
    if panel.empty:
        return panel.copy()
    output = panel.copy()
    if "forecast_origin" not in output:
        raise ValueError("forecast_origin is required")
    output["forecast_origin"] = pd.to_datetime(
        output["forecast_origin"], errors="coerce"
    )
    output = output.dropna(subset=["forecast_origin"]).sort_values(
        "forecast_origin"
    ).reset_index(drop=True)
    activity = (
        pd.to_numeric(output["activity_score"], errors="coerce")
        if "activity_score" in output
        else pd.Series(math.nan, index=output.index, dtype="float64")
    )
    labor = (
        pd.to_numeric(output["labor_income_score"], errors="coerce")
        if "labor_income_score" in output
        else pd.Series(math.nan, index=output.index, dtype="float64")
    )
    output["_activity_level"] = activity.rolling(3, min_periods=3).mean()
    output["_labor_level"] = labor.rolling(3, min_periods=3).mean()
    output["_raw_level"] = 0.5 * activity + 0.5 * labor
    output["_level"] = output["_raw_level"].rolling(3, min_periods=3).mean()
    output["_momentum"] = output["_level"].diff(3)
    output["_activity_momentum"] = output["_activity_level"].diff(3)
    output["_labor_momentum"] = output["_labor_level"].diff(3)
    return output


def _breadth(
    panel: pd.DataFrame,
    index: int,
    *,
    lag: int | None = None,
) -> tuple[float | None, int]:
    positive = 0
    available = 0
    for series_id in REAL_ECONOMY_SERIES:
        column = f"{series_id}_z"
        current = _finite(panel.at[index, column]) if column in panel else None
        if current is None:
            continue
        if lag is None:
            value = current
        else:
            if index < lag:
                continue
            previous = _finite(panel.at[index - lag, column])
            if previous is None:
                continue
            value = current - previous
        available += 1
        if value > 0.0:
            positive += 1
    return ((positive / available) if available else None, available)


def _data_status(panel: pd.DataFrame, index: int) -> tuple[str, int, int]:
    available = 0
    stale = 0
    for series_id in REAL_ECONOMY_SERIES:
        value_column = f"{series_id}_z"
        value = _finite(panel.at[index, value_column]) if value_column in panel else None
        if value is None:
            continue
        available += 1
        stale_column = f"{series_id}_stale"
        if stale_column in panel and bool(panel.at[index, stale_column]):
            stale += 1
    required_factors = all(
        _finite(panel.at[index, column]) is not None
        for column in ("activity_score", "labor_income_score")
        if column in panel
    ) and all(column in panel for column in ("activity_score", "labor_income_score"))
    coordinate_ready = all(
        _finite(panel.at[index, column]) is not None
        for column in ("_level", "_momentum")
    )
    if available < 6 or not required_factors or not coordinate_ready:
        return "UNAVAILABLE", available, stale
    if available == 8 and stale == 0:
        return "READY", available, stale
    return "LIMITED", available, stale


def _revision_phases(revised_panel: pd.DataFrame | None) -> dict[str, str]:
    if revised_panel is None or revised_panel.empty:
        return {}
    revised = _prepare_panel(revised_panel)
    phases: dict[str, str] = {}
    for index in revised.index:
        level = _finite(revised.at[index, "_level"])
        momentum = _finite(revised.at[index, "_momentum"])
        if level is None or momentum is None:
            continue
        phases[_origin_text(revised.at[index, "forecast_origin"])] = (
            phase_from_coordinates(level, momentum)
        )
    return phases


def _recent_changes(panel: pd.DataFrame, index: int) -> tuple[dict[str, object], ...]:
    records: list[dict[str, object]] = []
    current_raw = _finite(panel.at[index, "_raw_level"])
    for horizon in RECENT_CHANGE_HORIZONS:
        record: dict[str, object] = {
            "horizon_months": horizon,
            "status": "UNAVAILABLE",
            "composite_delta": None,
            "breadth": None,
            "available_pairs": 0,
            "activity_delta": None,
            "labor_income_delta": None,
        }
        if index < horizon or current_raw is None:
            records.append(record)
            continue
        previous_raw = _finite(panel.at[index - horizon, "_raw_level"])
        breadth, available_pairs = _breadth(panel, index, lag=horizon)
        record["available_pairs"] = available_pairs
        if previous_raw is None or breadth is None or available_pairs < 6:
            records.append(record)
            continue
        delta = current_raw - previous_raw
        if delta > 0.0 and breadth >= 0.60:
            status = "STRENGTHENING"
        elif delta < 0.0 and breadth <= 0.40:
            status = "WEAKENING"
        else:
            status = "MIXED"
        current_activity = _finite(panel.at[index, "activity_score"])
        prior_activity = _finite(panel.at[index - horizon, "activity_score"])
        current_labor = _finite(panel.at[index, "labor_income_score"])
        prior_labor = _finite(panel.at[index - horizon, "labor_income_score"])
        record.update(
            {
                "status": status,
                "composite_delta": delta,
                "breadth": breadth,
                "activity_delta": (
                    current_activity - prior_activity
                    if current_activity is not None and prior_activity is not None
                    else None
                ),
                "labor_income_delta": (
                    current_labor - prior_labor
                    if current_labor is not None and prior_labor is not None
                    else None
                ),
            }
        )
        records.append(record)
    return tuple(records)


def _breadth_support(value: float, breadth: float | None) -> bool:
    if breadth is None:
        return False
    return breadth >= 0.60 if value >= 0.0 else breadth <= 0.40


def _transition_context(row: Mapping[str, object], target_phase: str | None) -> list[dict[str, object]]:
    if target_phase is None:
        return []
    target_positive = target_phase in {"recovery", "expansion"}
    contexts: list[dict[str, object]] = []
    for factor, invert in (("financial_leading_score", False), ("inflation_policy_score", True)):
        value = _finite(row.get(factor))
        if value is None or abs(value) < 1e-12:
            relation = "MIXED"
        else:
            factor_positive = value > 0.0
            points_positive = (not factor_positive) if invert else factor_positive
            relation = (
                "TOWARD_TARGET"
                if points_positive == target_positive
                else "SUPPORT_CURRENT"
            )
        contexts.append({"factor": factor, "value": value, "relation": relation})
    return contexts


def _next_phase(phase: str | None) -> str | None:
    if phase not in PHASE_SEQUENCE:
        return None
    return PHASE_SEQUENCE[(PHASE_SEQUENCE.index(phase) + 1) % len(PHASE_SEQUENCE)]


def _condition_record(
    condition_id: str,
    *,
    status: str,
    value: object,
    threshold: str,
) -> dict[str, object]:
    return {
        "condition_id": condition_id,
        "status": status,
        "value": value,
        "threshold": threshold,
    }


def _matches_direction(value: float, *, positive: bool) -> bool:
    return value >= 0.0 if positive else value < 0.0


def _transition_conditions(
    panel: pd.DataFrame,
    index: int,
    *,
    target_phase: str | None,
    data_status: str,
    previous_data_status: str | None,
    level_breadth: float | None,
    level_pairs: int,
    momentum_breadth: float | None,
    momentum_pairs: int,
) -> tuple[dict[str, object], ...]:
    if target_phase not in PHASE_SEQUENCE or data_status == "UNAVAILABLE":
        return tuple(
            _condition_record(
                condition_id,
                status="UNAVAILABLE",
                value=None,
                threshold="data required",
            )
            for condition_id in ("persistence", "diffusion", "corroboration")
        )

    uses_momentum = target_phase in {"recovery", "slowdown"}
    positive = target_phase in {"recovery", "expansion"}
    axis_column = "_momentum" if uses_momentum else "_level"
    component_columns = (
        ("_activity_momentum", "_labor_momentum")
        if uses_momentum
        else ("_activity_level", "_labor_level")
    )
    axis_value = _finite(panel.at[index, axis_column])
    prior_axis = _finite(panel.at[index - 1, axis_column]) if index >= 1 else None
    persistence_met = (
        axis_value is not None
        and prior_axis is not None
        and previous_data_status not in {None, "UNAVAILABLE"}
        and _matches_direction(axis_value, positive=positive)
        and _matches_direction(prior_axis, positive=positive)
    )
    persistence = _condition_record(
        "persistence",
        status="MET" if persistence_met else "UNMET",
        value={"current": axis_value, "previous": prior_axis},
        threshold=(">= 0 for two releases" if positive else "< 0 for two releases"),
    )

    breadth = momentum_breadth if uses_momentum else level_breadth
    breadth_pairs = momentum_pairs if uses_momentum else level_pairs
    if breadth is None or breadth_pairs < 6:
        diffusion_status = "UNAVAILABLE"
    else:
        diffusion_met = breadth >= 0.60 if positive else breadth <= 0.40
        diffusion_status = "MET" if diffusion_met else "UNMET"
    diffusion = _condition_record(
        "diffusion",
        status=diffusion_status,
        value={"breadth": breadth, "available_pairs": breadth_pairs},
        threshold=(">= 0.60" if positive else "<= 0.40"),
    )

    components = [_finite(panel.at[index, column]) for column in component_columns]
    if any(value is None for value in components):
        corroboration_status = "UNAVAILABLE"
    else:
        corroboration_met = all(
            _matches_direction(value, positive=positive)
            for value in components
            if value is not None
        )
        corroboration_status = "MET" if corroboration_met else "UNMET"
    corroboration = _condition_record(
        "corroboration",
        status=corroboration_status,
        value={"activity": components[0], "labor_income": components[1]},
        threshold=("both >= 0" if positive else "both < 0"),
    )
    return persistence, diffusion, corroboration


def build_observed_state_history(
    panel: pd.DataFrame,
    *,
    revised_panel: pd.DataFrame | None = None,
) -> tuple[ObservedStateResult, ...]:
    """Build one sequential observed record per feature origin without look-ahead."""

    prepared = _prepare_panel(panel)
    if prepared.empty:
        return ()
    revised_phases = _revision_phases(revised_panel)
    results: list[ObservedStateResult] = []
    anchor_phase: str | None = None
    anchor_started_at: str | None = None
    anchor_source: str | None = None
    anchor_confirmed_at: str | None = None
    pending_anchor: str | None = None
    pending_anchor_confirmed_at: str | None = None
    candidate_started_at: str | None = None
    previous_phase: str | None = None
    duration = 0
    for index in prepared.index:
        origin = _origin_text(prepared.at[index, "forecast_origin"])
        data_status, available, stale = _data_status(prepared, index)
        level = _finite(prepared.at[index, "_level"])
        momentum = _finite(prepared.at[index, "_momentum"])
        level_breadth, level_pairs = _breadth(prepared, index)
        momentum_breadth, momentum_pairs = _breadth(prepared, index, lag=3)
        phase = (
            phase_from_coordinates(level, momentum)
            if data_status != "UNAVAILABLE" and level is not None and momentum is not None
            else None
        )
        if data_status != "UNAVAILABLE" and pending_anchor is not None:
            anchor_phase = pending_anchor
            anchor_started_at = pending_anchor_confirmed_at or origin
            anchor_source = "CONFIRMED"
            anchor_confirmed_at = pending_anchor_confirmed_at
            pending_anchor = None
            pending_anchor_confirmed_at = None
            candidate_started_at = None
        if phase is not None and phase == previous_phase:
            duration += 1
        elif phase is not None:
            duration = 1
        else:
            duration = 0
        previous_phase = phase
        revised_phase = revised_phases.get(origin)
        revision_sensitivity = (
            "UNAVAILABLE"
            if phase is None or revised_phase is None
            else "STABLE"
            if phase == revised_phase
            else "SENSITIVE"
        )
        if data_status in {"LIMITED", "UNAVAILABLE"}:
            confidence = "LIMITED"
        elif (
            level is not None
            and momentum is not None
            and revision_sensitivity == "STABLE"
            and duration >= 2
            and _breadth_support(level, level_breadth)
            and _breadth_support(momentum, momentum_breadth)
        ):
            confidence = "HIGH"
        else:
            confidence = "MEDIUM"
        if anchor_phase is None and phase is not None:
            anchor_phase = phase
            anchor_started_at = origin
            anchor_source = "INITIALIZED"
            anchor_confirmed_at = None
        target_phase = _next_phase(anchor_phase)
        previous_data_status = (
            str(results[-1].observed_state["data_status"]) if results else None
        )
        conditions = _transition_conditions(
            prepared,
            index,
            target_phase=target_phase,
            data_status=data_status,
            previous_data_status=previous_data_status,
            level_breadth=level_breadth,
            level_pairs=level_pairs,
            momentum_breadth=momentum_breadth,
            momentum_pairs=momentum_pairs,
        )
        conditions_met = sum(row["status"] == "MET" for row in conditions)
        if data_status == "UNAVAILABLE":
            status = "MAINTAIN"
            candidate_started_at = None
        elif conditions_met == 3:
            status = "CONFIRMED"
            if candidate_started_at is None:
                candidate_started_at = origin
            pending_anchor = target_phase
            pending_anchor_confirmed_at = origin
        elif conditions_met > 0 or (phase is not None and phase != anchor_phase):
            status = "WATCH"
            if candidate_started_at is None:
                candidate_started_at = origin
        else:
            status = "MAINTAIN"
            candidate_started_at = None
        non_adjacent = bool(
            phase is not None
            and anchor_phase is not None
            and phase not in {anchor_phase, target_phase}
        )
        observed_state = {
            "as_of_date": origin,
            "raw_level": _finite(prepared.at[index, "_raw_level"]),
            "level": level,
            "momentum": momentum,
            "phase": phase,
            "activity_level": _finite(prepared.at[index, "_activity_level"]),
            "labor_income_level": _finite(prepared.at[index, "_labor_level"]),
            "activity_momentum": _finite(prepared.at[index, "_activity_momentum"]),
            "labor_income_momentum": _finite(prepared.at[index, "_labor_momentum"]),
            "level_breadth": level_breadth,
            "momentum_breadth": momentum_breadth,
            "level_breadth_available": level_pairs,
            "momentum_breadth_available": momentum_pairs,
            "available_series": available,
            "stale_series": stale,
            "duration_months": duration,
            "confidence": confidence,
            "revision_sensitivity": revision_sensitivity,
            "revised_phase": revised_phase,
            "data_status": data_status,
        }
        transition_monitor = {
            "observed_phase": phase,
            "anchor_phase": anchor_phase,
            "anchor_started_at": anchor_started_at,
            "anchor_source": anchor_source,
            "anchor_confirmed_at": anchor_confirmed_at,
            "target_phase": target_phase,
            "status": status,
            "conditions_met": conditions_met,
            "conditions_total": 3,
            "candidate_started_at": candidate_started_at,
            "confirmed_at": origin if status == "CONFIRMED" else None,
            "non_adjacent_observation": non_adjacent,
            "conditions": conditions,
            "context": _transition_context(prepared.loc[index].to_dict(), target_phase),
        }
        results.append(
            ObservedStateResult(
                observed_state=observed_state,
                recent_changes=_recent_changes(prepared, index),
                transition_monitor=transition_monitor,
            )
        )
    return tuple(results)


def build_observed_state_snapshot(
    panel: pd.DataFrame,
    *,
    revised_panel: pd.DataFrame | None = None,
) -> ObservedStateResult:
    """Return the latest observed-state record from a bounded feature panel."""

    history = build_observed_state_history(panel, revised_panel=revised_panel)
    if not history:
        raise LookupError("No economic-cycle feature rows are available")
    return history[-1]
