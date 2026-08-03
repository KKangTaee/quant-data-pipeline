"""Chronological validation for official SEP and FOMC policy marginals."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Mapping, Sequence

from finance.inflation_policy_validation import calculate_categorical_metrics
from finance.policy_path import (
    NEXT_MEETING_ACTIONS,
    POLICY_NET_MOVE_BUCKETS,
    derive_decision_action_prior,
    derive_sep_net_move_prior,
)


SMOOTHING_GRID = (0.0, 0.05, 0.10, 0.15, 0.20, 0.25, 0.30, 0.35, 0.40)


@dataclass(frozen=True)
class PolicyPathArtifact:
    """Validated calibration parameters for next-meeting and year-end paths."""

    trained_cutoff_at: str
    training_start_decision_date: str
    trained_through_decision_date: str
    next_meeting_smoothing: float
    year_end_smoothing: float
    next_meeting_validation: dict[str, object]
    year_end_validation: dict[str, object]
    publication_status: str
    reason_codes: tuple[str, ...]


def _timestamp(value: object) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _date(value: object) -> date:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value).strip()[:10])


def _normalized_probability_row(
    values: Mapping[str, object], *, labels: Sequence[str]
) -> dict[str, float]:
    approved = tuple(labels)
    if set(values) != set(approved):
        raise ValueError("probability row must contain the exact labels")
    row = {label: float(values[label]) for label in approved}
    if any(not math.isfinite(value) or value < 0.0 for value in row.values()):
        raise ValueError("probability row must be finite and non-negative")
    total = sum(row.values())
    if total <= 0.0:
        raise ValueError("probability row must contain positive mass")
    return {label: row[label] / total for label in approved}


def smooth_probability_row(
    values: Mapping[str, object],
    *,
    labels: Sequence[str],
    smoothing: float,
) -> dict[str, float]:
    """Shrink an official/vote marginal toward uniform mass for calibration."""

    approved = tuple(labels)
    row = _normalized_probability_row(values, labels=approved)
    shrinkage = float(smoothing)
    if not math.isfinite(shrinkage) or not 0.0 <= shrinkage <= 1.0:
        raise ValueError("smoothing must be in [0, 1]")
    uniform = 1.0 / len(approved)
    return {
        label: (1.0 - shrinkage) * row[label] + shrinkage * uniform
        for label in approved
    }


def _fit_smoothing(
    probability_rows: Sequence[Mapping[str, object]],
    targets: Sequence[str],
    *,
    labels: Sequence[str],
) -> float:
    if not probability_rows or len(probability_rows) != len(targets):
        raise ValueError("completed probability rows and targets are required")
    return min(
        SMOOTHING_GRID,
        key=lambda smoothing: calculate_categorical_metrics(
            [
                smooth_probability_row(
                    row, labels=labels, smoothing=smoothing
                )
                for row in probability_rows
            ],
            targets,
            labels=labels,
        )["brier_score"],
    )


def _rolling_calibrated_rows(
    probability_rows: Sequence[Mapping[str, object]],
    targets: Sequence[str],
    *,
    labels: Sequence[str],
    minimum_calibration_rows: int,
) -> tuple[list[dict[str, float]], list[str], list[float]]:
    predictions: list[dict[str, float]] = []
    evaluation_targets: list[str] = []
    smoothing_values: list[float] = []
    for index in range(int(minimum_calibration_rows), len(probability_rows)):
        smoothing = _fit_smoothing(
            probability_rows[:index], targets[:index], labels=labels
        )
        predictions.append(
            smooth_probability_row(
                probability_rows[index], labels=labels, smoothing=smoothing
            )
        )
        evaluation_targets.append(str(targets[index]))
        smoothing_values.append(smoothing)
    return predictions, evaluation_targets, smoothing_values


def _action(before: float, after: float) -> str:
    change = float(after) - float(before)
    if math.isclose(change, 0.0, abs_tol=1e-9):
        return "hold"
    return "hike" if change > 0.0 else "cut"


def _net_bucket(steps: int) -> str:
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


def _midpoint(row: Mapping[str, object], *, after: bool) -> float:
    suffix = "after" if after else "before"
    return (
        float(row[f"target_lower_{suffix}_pct"])
        + float(row[f"target_upper_{suffix}_pct"])
    ) / 2.0


def _directional_sep(values: Mapping[str, object]) -> dict[str, float]:
    row = _normalized_probability_row(values, labels=POLICY_NET_MOVE_BUCKETS)
    return {
        "cut": row["cut_3_plus"] + row["cut_2"] + row["cut_1"],
        "hold": row["hold"],
        "hike": row["hike_1"] + row["hike_2"] + row["hike_3_plus"],
    }


def _one_hot(label: str, *, labels: Sequence[str]) -> dict[str, float]:
    return {item: 1.0 if item == label else 0.0 for item in labels}


def _next_meeting_rows(
    decisions: Sequence[Mapping[str, object]],
    sep_rows: Sequence[Mapping[str, object]],
) -> tuple[
    list[dict[str, float]],
    list[str],
    dict[str, list[dict[str, float]]],
]:
    forecasts: list[dict[str, float]] = []
    targets: list[str] = []
    baselines: dict[str, list[dict[str, float]]] = {
        "always_hold": [],
        "previous_action": [],
        "latest_sep_direction": [],
    }
    for index, origin in enumerate(decisions[:-1]):
        target_row = decisions[index + 1]
        if origin.get("target_lower_before_pct") in (None, ""):
            continue
        origin_before = _midpoint(origin, after=False)
        origin_after = _midpoint(origin, after=True)
        target_before = _midpoint(target_row, after=False)
        target_after = _midpoint(target_row, after=True)
        target = _action(target_before, target_after)
        forecasts.append(derive_decision_action_prior(origin))
        targets.append(target)
        baselines["always_hold"].append(
            _one_hot("hold", labels=NEXT_MEETING_ACTIONS)
        )
        baselines["previous_action"].append(
            _one_hot(
                _action(origin_before, origin_after),
                labels=NEXT_MEETING_ACTIONS,
            )
        )
        origin_release = _timestamp(origin["released_at"])
        eligible_sep = [
            row
            for row in sep_rows
            if _timestamp(row["released_at"]) <= origin_release
        ]
        try:
            sep_prior = derive_sep_net_move_prior(
                eligible_sep,
                target_period=str(_date(origin["meeting_date"]).year),
                current_midpoint_pct=origin_after,
            )
            sep_direction = _directional_sep(sep_prior)
        except (KeyError, TypeError, ValueError):
            sep_direction = _one_hot("hold", labels=NEXT_MEETING_ACTIONS)
        baselines["latest_sep_direction"].append(sep_direction)
    return forecasts, targets, baselines


def _year_end_rows(
    decisions: Sequence[Mapping[str, object]],
    sep_rows: Sequence[Mapping[str, object]],
    *,
    cutoff: datetime,
) -> tuple[
    list[dict[str, float]],
    list[str],
    dict[str, list[dict[str, float]]],
]:
    decision_by_date = {
        _date(row["meeting_date"]): row
        for row in decisions
        if row.get("meeting_date") not in (None, "")
    }
    final_by_year: dict[int, Mapping[str, object]] = {}
    for row in decisions:
        meeting = _date(row["meeting_date"])
        current = final_by_year.get(meeting.year)
        if current is None or meeting > _date(current["meeting_date"]):
            final_by_year[meeting.year] = row
    releases = sorted(
        {
            (_date(row["meeting_date"]), _timestamp(row["released_at"]))
            for row in sep_rows
        },
        key=lambda item: item[1],
    )
    prior_release_by_year: dict[int, datetime] = {}
    forecasts: list[dict[str, float]] = []
    targets: list[str] = []
    baselines: dict[str, list[dict[str, float]]] = {
        "always_hold": [],
        "prior_sep": [],
    }
    for meeting_date, release_at in releases:
        year = meeting_date.year
        if year >= cutoff.year:
            continue
        origin_decision = decision_by_date.get(meeting_date)
        final_decision = final_by_year.get(year)
        if origin_decision is None or final_decision is None:
            continue
        if _date(final_decision["meeting_date"]).month != 12:
            continue
        final_release_at = _timestamp(final_decision["released_at"])
        if final_release_at > cutoff:
            continue
        # A December SEP published with the final decision has no forecast
        # horizon: the year-end target is already observed at that timestamp.
        # Only strictly earlier releases are valid policy forecast origins.
        if release_at >= final_release_at:
            continue
        current_midpoint = _midpoint(origin_decision, after=True)
        end_midpoint = _midpoint(final_decision, after=True)
        raw_steps = (end_midpoint - current_midpoint) * 4.0
        steps = int(round(raw_steps))
        if not math.isclose(raw_steps, steps, abs_tol=1e-6):
            continue
        eligible = [
            row
            for row in sep_rows
            if _timestamp(row["released_at"]) <= release_at
        ]
        try:
            forecast = derive_sep_net_move_prior(
                eligible,
                target_period=str(year),
                current_midpoint_pct=current_midpoint,
            )
        except (KeyError, TypeError, ValueError):
            continue
        forecasts.append(forecast)
        targets.append(_net_bucket(steps))
        baselines["always_hold"].append(
            _one_hot("hold", labels=POLICY_NET_MOVE_BUCKETS)
        )
        prior_release = prior_release_by_year.get(year)
        if prior_release is None:
            prior = _one_hot("hold", labels=POLICY_NET_MOVE_BUCKETS)
        else:
            prior_eligible = [
                row
                for row in sep_rows
                if _timestamp(row["released_at"]) <= prior_release
            ]
            try:
                prior = derive_sep_net_move_prior(
                    prior_eligible,
                    target_period=str(year),
                    current_midpoint_pct=current_midpoint,
                )
            except (KeyError, TypeError, ValueError):
                prior = _one_hot("hold", labels=POLICY_NET_MOVE_BUCKETS)
        baselines["prior_sep"].append(prior)
        prior_release_by_year[year] = release_at
    return forecasts, targets, baselines


def _validation_summary(
    forecasts: Sequence[Mapping[str, object]],
    targets: Sequence[str],
    baselines: Mapping[str, Sequence[Mapping[str, object]]],
    *,
    labels: Sequence[str],
    minimum_calibration_rows: int,
) -> dict[str, object]:
    predictions, evaluation_targets, smoothing_history = _rolling_calibrated_rows(
        forecasts,
        targets,
        labels=labels,
        minimum_calibration_rows=minimum_calibration_rows,
    )
    if not predictions:
        return {
            "origin_count": 0,
            "completed_origin_count": len(forecasts),
        }
    metrics = calculate_categorical_metrics(
        predictions, evaluation_targets, labels=labels
    )
    baseline_metrics: dict[str, dict[str, float]] = {}
    for name, rows in baselines.items():
        baseline_predictions, baseline_targets, _history = _rolling_calibrated_rows(
            rows,
            targets,
            labels=labels,
            minimum_calibration_rows=minimum_calibration_rows,
        )
        baseline_metrics[name] = calculate_categorical_metrics(
            baseline_predictions,
            baseline_targets,
            labels=labels,
        )
    best_name = min(
        baseline_metrics,
        key=lambda name: baseline_metrics[name]["brier_score"],
    )
    return {
        **metrics,
        "origin_count": len(predictions),
        "completed_origin_count": len(forecasts),
        "best_baseline": best_name,
        "baseline_brier_score": baseline_metrics[best_name]["brier_score"],
        "baseline_metrics": baseline_metrics,
        "rolling_smoothing_min": min(smoothing_history),
        "rolling_smoothing_max": max(smoothing_history),
    }


def fit_policy_path_artifact(
    decision_rows: Sequence[Mapping[str, object]],
    sep_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: str,
    minimum_next_origins: int = 30,
    minimum_year_end_origins: int = 12,
    minimum_calibration_rows: int = 6,
    maximum_calibration_error: float = 0.20,
    require_baseline_improvement: bool = True,
) -> PolicyPathArtifact:
    """Fit calibration using only policy targets completed by each origin."""

    cutoff = _timestamp(as_of_at)
    decisions = tuple(
        sorted(
            (
                dict(row)
                for row in decision_rows
                if row.get("released_at") not in (None, "")
                and _timestamp(row["released_at"]) <= cutoff
            ),
            key=lambda row: _timestamp(row["released_at"]),
        )
    )
    sep = tuple(
        dict(row)
        for row in sep_rows
        if row.get("released_at") not in (None, "")
        and _timestamp(row["released_at"]) <= cutoff
    )
    trained_through = (
        _date(decisions[-1]["meeting_date"]).isoformat() if decisions else ""
    )
    training_start = (
        _date(decisions[0]["meeting_date"]).isoformat() if decisions else ""
    )
    empty = PolicyPathArtifact(
        trained_cutoff_at=cutoff.isoformat(),
        training_start_decision_date=training_start,
        trained_through_decision_date=trained_through,
        next_meeting_smoothing=0.0,
        year_end_smoothing=0.0,
        next_meeting_validation={},
        year_end_validation={},
        publication_status="NOT_AVAILABLE",
        reason_codes=("completed_year_end_origins_missing",),
    )
    if len(decisions) < 2 or not sep:
        return empty
    next_forecasts, next_targets, next_baselines = _next_meeting_rows(decisions, sep)
    year_forecasts, year_targets, year_baselines = _year_end_rows(
        decisions, sep, cutoff=cutoff
    )
    if not year_forecasts:
        return empty
    calibration_rows = max(1, int(minimum_calibration_rows))
    next_validation = _validation_summary(
        next_forecasts,
        next_targets,
        next_baselines,
        labels=NEXT_MEETING_ACTIONS,
        minimum_calibration_rows=calibration_rows,
    )
    year_validation = _validation_summary(
        year_forecasts,
        year_targets,
        year_baselines,
        labels=POLICY_NET_MOVE_BUCKETS,
        minimum_calibration_rows=calibration_rows,
    )
    reasons: list[str] = []
    if int(next_validation.get("origin_count") or 0) < int(minimum_next_origins):
        reasons.append("insufficient_next_meeting_origins")
    if int(year_validation.get("origin_count") or 0) < int(minimum_year_end_origins):
        reasons.append("insufficient_year_end_origins")
    next_calibration = next_validation.get("calibration_error")
    year_calibration = year_validation.get("calibration_error")
    calibration_error = max(
        float(next_calibration) if next_calibration is not None else math.inf,
        float(year_calibration) if year_calibration is not None else math.inf,
    )
    if calibration_error > float(maximum_calibration_error):
        reasons.append("policy_calibration_error_too_high")
    if require_baseline_improvement:
        next_score = next_validation.get("brier_score")
        next_baseline = next_validation.get("baseline_brier_score")
        year_score = year_validation.get("brier_score")
        year_baseline = year_validation.get("baseline_brier_score")
        if not (
            float(next_score) if next_score is not None else math.inf
        ) < (
            float(next_baseline) if next_baseline is not None else -math.inf
        ):
            reasons.append("next_meeting_no_baseline_improvement")
        if not (
            float(year_score) if year_score is not None else math.inf
        ) < (
            float(year_baseline) if year_baseline is not None else -math.inf
        ):
            reasons.append("year_end_no_baseline_improvement")
    next_smoothing = _fit_smoothing(
        next_forecasts, next_targets, labels=NEXT_MEETING_ACTIONS
    )
    year_smoothing = _fit_smoothing(
        year_forecasts, year_targets, labels=POLICY_NET_MOVE_BUCKETS
    )
    return PolicyPathArtifact(
        trained_cutoff_at=cutoff.isoformat(),
        training_start_decision_date=training_start,
        trained_through_decision_date=trained_through,
        next_meeting_smoothing=next_smoothing,
        year_end_smoothing=year_smoothing,
        next_meeting_validation=next_validation,
        year_end_validation=year_validation,
        publication_status="LIMITED" if reasons else "READY",
        reason_codes=tuple(reasons),
    )
