"""Transparent SEP, economic, and committee policy-path probability components."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass
from typing import Mapping, Sequence

from finance.inflation_path import INFLATION_STATES


POLICY_NET_MOVE_BUCKETS = (
    "cut_3_plus",
    "cut_2",
    "cut_1",
    "hold",
    "hike_1",
    "hike_2",
    "hike_3_plus",
)
NEXT_MEETING_ACTIONS = ("cut", "hold", "hike")
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
class PolicyPathForecast:
    """Consistent next-meeting and year-end policy marginal distributions."""

    next_meeting_probabilities: dict[str, float]
    net_move_probabilities: dict[str, float]
    year_end_target_probabilities: dict[str, float]
    current_midpoint_pct: float
    step_bps: int


def _probability_row(
    values: Mapping[str, object],
    *,
    labels: Sequence[str],
    field: str,
) -> dict[str, float]:
    if set(values) != set(labels):
        raise ValueError(f"{field} must contain the exact approved labels")
    normalized = {label: float(values[label]) for label in labels}
    if any(
        not math.isfinite(value) or value < 0.0 for value in normalized.values()
    ):
        raise ValueError(f"{field} must be finite and non-negative")
    total = sum(normalized.values())
    if total <= 0.0:
        raise ValueError(f"{field} must contain positive mass")
    return {label: normalized[label] / total for label in labels}


def _bucket_for_steps(steps: int) -> str:
    if steps <= -3:
        return "cut_3_plus"
    if steps >= 3:
        return "hike_3_plus"
    return {
        -2: "cut_2",
        -1: "cut_1",
        0: "hold",
        1: "hike_1",
        2: "hike_2",
    }[steps]


def derive_sep_net_move_prior(
    sep_rows: Sequence[Mapping[str, object]],
    *,
    target_period: str,
    current_midpoint_pct: float,
    step_bps: int = 25,
) -> dict[str, float]:
    """Translate the latest anonymous rate-dot marginal into net-move buckets."""

    midpoint = float(current_midpoint_pct)
    if not math.isfinite(midpoint) or int(step_bps) <= 0:
        raise ValueError("current midpoint and step_bps must be valid")
    eligible = [
        dict(row)
        for row in sep_rows
        if str(row.get("target_period")) == str(target_period)
        and str(row.get("variable_name")) == "federal_funds_rate"
        and str(row.get("distribution_kind")) == "DOT"
        and row.get("released_at") not in (None, "")
    ]
    if not eligible:
        raise ValueError("eligible federal funds rate dots are required")
    latest_release = max(str(row["released_at"]) for row in eligible)
    counts = {bucket: 0 for bucket in POLICY_NET_MOVE_BUCKETS}
    for row in eligible:
        if str(row["released_at"]) != latest_release:
            continue
        value = float(row["bin_value_pct"])
        count = int(row["participant_count"])
        raw_steps = (value - midpoint) * 100.0 / int(step_bps)
        steps = int(round(raw_steps))
        if not math.isclose(raw_steps, steps, abs_tol=1e-6):
            raise ValueError("SEP rate dot is not aligned to the configured policy step")
        if count < 0:
            raise ValueError("SEP participant counts cannot be negative")
        counts[_bucket_for_steps(steps)] += count
    return _probability_row(counts, labels=POLICY_NET_MOVE_BUCKETS, field="SEP prior")


def _action_from_change(before: float, after: float) -> str:
    change = after - before
    if math.isclose(change, 0.0, abs_tol=1e-9):
        return "hold"
    return "hike" if change > 0.0 else "cut"


def _action_from_preference(value: object) -> str:
    normalized = str(value or "").strip().upper()
    if normalized.startswith("HIKE"):
        return "hike"
    if normalized.startswith("CUT"):
        return "cut"
    if normalized.startswith("HOLD"):
        return "hold"
    raise ValueError(f"unsupported dissent preference: {value!r}")


def derive_decision_action_prior(
    decision_row: Mapping[str, object],
) -> dict[str, float]:
    """Preserve actual vote directions as a next-meeting committee marginal."""

    before = (
        float(decision_row["target_lower_before_pct"])
        + float(decision_row["target_upper_before_pct"])
    ) / 2.0
    after = (
        float(decision_row["target_lower_after_pct"])
        + float(decision_row["target_upper_after_pct"])
    ) / 2.0
    vote_for = int(decision_row["vote_for_count"])
    vote_against = int(decision_row["vote_against_count"])
    if vote_for < 0 or vote_against < 0 or vote_for + vote_against <= 0:
        raise ValueError("decision vote counts must contain positive mass")
    raw_dissents = decision_row.get("dissents_json") or "[]"
    dissents = json.loads(raw_dissents) if isinstance(raw_dissents, str) else raw_dissents
    if not isinstance(dissents, list) or len(dissents) != vote_against:
        raise ValueError("dissent details must align with vote_against_count")
    counts = {action: 0 for action in NEXT_MEETING_ACTIONS}
    counts[_action_from_change(before, after)] += vote_for
    for dissent in dissents:
        if not isinstance(dissent, Mapping):
            raise ValueError("dissent rows must be mappings")
        counts[_action_from_preference(dissent.get("preferred_action"))] += 1
    return _probability_row(
        counts, labels=NEXT_MEETING_ACTIONS, field="decision action prior"
    )


def project_inflation_states_to_policy(
    state_probabilities: Mapping[str, object],
    *,
    reaction_matrix: Mapping[str, Mapping[str, object]],
) -> dict[str, float]:
    """Apply one versioned reaction matrix without creating boolean policy rules."""

    states = _probability_row(
        state_probabilities,
        labels=INFLATION_STATES,
        field="inflation state probabilities",
    )
    if set(reaction_matrix) != set(INFLATION_STATES):
        raise ValueError("reaction matrix must contain every inflation state")
    rows = {
        state: _probability_row(
            reaction_matrix[state],
            labels=POLICY_NET_MOVE_BUCKETS,
            field=f"reaction matrix {state}",
        )
        for state in INFLATION_STATES
    }
    return {
        bucket: sum(states[state] * rows[state][bucket] for state in INFLATION_STATES)
        for bucket in POLICY_NET_MOVE_BUCKETS
    }


def blend_probability_components(
    components: Mapping[str, Mapping[str, object] | None],
    *,
    weights: Mapping[str, object],
    labels: Sequence[str],
    max_component_weight: float,
) -> dict[str, float]:
    """Blend available calibrated components and renormalize missing optional priors."""

    available = {name: row for name, row in components.items() if row is not None}
    if not available:
        raise ValueError("at least one probability component is required")
    if not set(available).issubset(weights):
        raise ValueError("every available component requires a weight")
    raw_weights = {name: float(weights[name]) for name in available}
    if any(
        not math.isfinite(value) or value < 0.0 for value in raw_weights.values()
    ):
        raise ValueError("component weights must be finite and non-negative")
    weight_total = sum(raw_weights.values())
    if weight_total <= 0.0:
        raise ValueError("available components must contain positive weight")
    normalized_weights = {
        name: value / weight_total for name, value in raw_weights.items()
    }
    cap = float(max_component_weight)
    if len(available) > 1 and any(
        value > cap + 1e-12 for value in normalized_weights.values()
    ):
        raise ValueError("available component exceeds the configured weight cap")
    rows = {
        name: _probability_row(
            row or {}, labels=labels, field=f"component {name}"
        )
        for name, row in available.items()
    }
    return {
        label: sum(
            normalized_weights[name] * rows[name][label] for name in available
        )
        for label in labels
    }


def build_policy_path_forecast(
    *,
    current_midpoint_pct: float,
    net_move_components: Mapping[str, Mapping[str, object] | None],
    net_move_weights: Mapping[str, object],
    next_action_components: Mapping[str, Mapping[str, object] | None],
    next_action_weights: Mapping[str, object],
    max_component_weight: float,
    step_bps: int = 25,
) -> PolicyPathForecast:
    """Build mutually consistent policy marginals without linking member identities."""

    midpoint = float(current_midpoint_pct)
    if not math.isfinite(midpoint) or int(step_bps) <= 0:
        raise ValueError("current midpoint and step_bps must be valid")
    net_moves = blend_probability_components(
        net_move_components,
        weights=net_move_weights,
        labels=POLICY_NET_MOVE_BUCKETS,
        max_component_weight=max_component_weight,
    )
    next_actions = blend_probability_components(
        next_action_components,
        weights=next_action_weights,
        labels=NEXT_MEETING_ACTIONS,
        max_component_weight=max_component_weight,
    )
    target_bins: dict[str, float] = {}
    for bucket in POLICY_NET_MOVE_BUCKETS:
        if net_moves[bucket] <= 0.0:
            continue
        target = midpoint + _BUCKET_STEPS[bucket] * int(step_bps) / 100.0
        label = f"{target:.4f}"
        target_bins[label] = target_bins.get(label, 0.0) + net_moves[bucket]
    return PolicyPathForecast(
        next_meeting_probabilities=next_actions,
        net_move_probabilities=net_moves,
        year_end_target_probabilities=target_bins,
        current_midpoint_pct=midpoint,
        step_bps=int(step_bps),
    )
