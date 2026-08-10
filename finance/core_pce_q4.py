"""Direct Q4/Q4 validation and official-SPF/monthly-model linear pooling."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import math
from typing import Mapping, Sequence

import numpy as np

from finance.inflation_policy_validation import (
    ContinuousValidationPrediction,
    PublicationEvidence,
    PublicationThresholds,
    calculate_continuous_metrics,
    evaluate_publication_gate,
)


@dataclass(frozen=True)
class Q4ValidationOrigin:
    forecast_origin_at: str
    target_available_at: str
    target_year: int
    actual_q4_pct: float
    model_samples_pct: tuple[float, ...]
    spf_samples_pct: tuple[float, ...]
    naive_prediction_pct: float


@dataclass(frozen=True)
class CorePCEQ4Artifact:
    trained_cutoff_at: str
    training_start_date: str
    trained_through_date: str
    model_weight: float
    spf_weight: float
    validation_metrics: dict[str, float | str]
    publication_status: str
    publication_reasons: tuple[str, ...]


def _timestamp(value: object) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _finite_samples(values: Sequence[object], *, field: str) -> tuple[float, ...]:
    parsed = tuple(float(value) for value in values)
    if not parsed or any(not math.isfinite(value) for value in parsed):
        raise ValueError(f"{field} must contain finite samples")
    return parsed


def _midpoint(row: Mapping[str, object]) -> float:
    lower = row.get("bin_lower_pct")
    upper = row.get("bin_upper_pct")
    if lower is None and upper is None:
        raise ValueError("SPF probability bin must have at least one bound")
    if lower is None:
        return float(upper) - 0.25
    if upper is None:
        return float(lower) + 0.25
    return (float(lower) + float(upper)) / 2.0


def spf_probability_samples(
    rows: Sequence[Mapping[str, object]],
    *,
    target_year: int,
    sample_count: int,
) -> tuple[tuple[float, ...], str]:
    """Convert the latest released ten-bin SPF marginal into deterministic samples."""

    if int(sample_count) <= 0:
        raise ValueError("sample_count must be positive")
    eligible = [
        dict(row)
        for row in rows
        if int(row.get("target_year") or 0) == int(target_year)
        and row.get("released_at") not in (None, "")
    ]
    if not eligible:
        raise ValueError("released SPF Core PCE distribution is unavailable")
    latest_release = max(str(row["released_at"]) for row in eligible)
    latest = sorted(
        (row for row in eligible if str(row["released_at"]) == latest_release),
        key=lambda row: int(row.get("bin_number") or 0),
    )
    if len(latest) != 10 or [int(row.get("bin_number") or 0) for row in latest] != list(
        range(1, 11)
    ):
        raise ValueError("SPF Core PCE distribution must contain exact bins 1 through 10")
    probabilities = np.asarray(
        [float(row.get("mean_probability_pct") or 0.0) for row in latest],
        dtype=float,
    )
    if np.any(~np.isfinite(probabilities)) or np.any(probabilities < 0.0):
        raise ValueError("SPF Core PCE probabilities must be finite and non-negative")
    total = float(np.sum(probabilities))
    if not math.isclose(total, 100.0, abs_tol=0.25):
        raise ValueError("SPF Core PCE probabilities must sum to 100")
    cumulative = np.cumsum(probabilities / total)
    quantiles = (np.arange(int(sample_count), dtype=float) + 0.5) / int(sample_count)
    indices = np.searchsorted(cumulative, quantiles, side="left")
    midpoints = np.asarray([_midpoint(row) for row in latest], dtype=float)
    return tuple(float(midpoints[index]) for index in indices), latest_release


def blend_q4_samples(
    model_samples: Sequence[object],
    spf_samples: Sequence[object],
    *,
    model_weight: float,
    sample_count: int | None = None,
) -> tuple[float, ...]:
    """Build a deterministic linear pool while keeping a non-model SPF anchor."""

    model = np.sort(np.asarray(_finite_samples(model_samples, field="model"), dtype=float))
    spf = np.sort(np.asarray(_finite_samples(spf_samples, field="SPF"), dtype=float))
    weight = float(model_weight)
    if not math.isfinite(weight) or not 0.0 <= weight <= 1.0:
        raise ValueError("model_weight must be between zero and one")
    count = int(sample_count or max(len(model), len(spf)))
    if count <= 0:
        raise ValueError("sample_count must be positive")
    model_count = min(count, max(0, int(round(count * weight))))
    spf_count = count - model_count

    def select(values: np.ndarray, size: int) -> list[float]:
        if size <= 0:
            return []
        positions = ((np.arange(size, dtype=float) + 0.5) / size * len(values)).astype(int)
        positions = np.minimum(positions, len(values) - 1)
        return [float(values[index]) for index in positions]

    return tuple(sorted((*select(model, model_count), *select(spf, spf_count))))


def _empirical_crps(samples: Sequence[object], actual: float) -> float:
    values = sorted(float(value) for value in samples)
    count = len(values)
    first = sum(abs(value - actual) for value in values) / count
    pairwise = 2.0 * sum(
        (2 * index - count - 1) * value
        for index, value in enumerate(values, start=1)
    ) / (count**2)
    return first - 0.5 * pairwise


def _candidate_score(
    completed: Sequence[tuple[Q4ValidationOrigin, dict[float, float]]],
    weight: float,
) -> float:
    return sum(scores[weight] for _origin, scores in completed) / len(completed)


def fit_q4_linear_pool(
    origins: Sequence[Q4ValidationOrigin],
    *,
    as_of_at: object,
    thresholds: PublicationThresholds,
    minimum_target_years: int,
    candidate_model_weights: Sequence[float] = (0.0, 0.25, 0.50, 0.75),
    default_model_weight: float = 0.25,
) -> CorePCEQ4Artifact:
    """Choose the model/SPF weight only from targets known at each forecast origin."""

    cutoff = _timestamp(as_of_at)
    candidates = tuple(float(weight) for weight in candidate_model_weights)
    if not candidates or any(not 0.0 <= weight <= 0.75 for weight in candidates):
        raise ValueError("candidate model weights must stay in [0, 0.75]")
    if float(default_model_weight) not in candidates:
        raise ValueError("default_model_weight must be a configured candidate")
    ordered = tuple(sorted(origins, key=lambda row: _timestamp(row.forecast_origin_at)))
    predictions: list[ContinuousValidationPrediction] = []
    scored: list[tuple[Q4ValidationOrigin, dict[float, float]]] = []
    selected_weights: list[float] = []
    spf_scores: list[float] = []
    for origin in ordered:
        forecast_at = _timestamp(origin.forecast_origin_at)
        target_at = _timestamp(origin.target_available_at)
        if forecast_at > cutoff or target_at > cutoff:
            continue
        model = _finite_samples(origin.model_samples_pct, field="model")
        spf = _finite_samples(origin.spf_samples_pct, field="SPF")
        actual = float(origin.actual_q4_pct)
        completed = [
            item
            for item in scored
            if _timestamp(item[0].target_available_at) <= forecast_at
        ]
        if completed:
            selected = min(
                candidates,
                key=lambda weight: (_candidate_score(completed, weight), weight),
            )
            training_through = max(
                item[0].target_available_at for item in completed
            )
        else:
            selected = float(default_model_weight)
            training_through = forecast_at.isoformat()
        blends = {
            weight: blend_q4_samples(
                model,
                spf,
                model_weight=weight,
                sample_count=max(len(model), len(spf)),
            )
            for weight in candidates
        }
        selected_samples = blends[selected]
        predictions.append(
            ContinuousValidationPrediction(
                forecast_origin_at=forecast_at.isoformat(),
                target_available_at=target_at.isoformat(),
                training_target_through_at=training_through,
                actual_value=actual,
                predicted_median=float(np.quantile(selected_samples, 0.5)),
                predictive_samples=selected_samples,
                baseline_prediction=float(origin.naive_prediction_pct),
                complete_feature_ratio=1.0,
            )
        )
        selected_weights.append(selected)
        spf_scores.append(_empirical_crps(spf, actual))
        scored.append(
            (
                origin,
                {
                    weight: _empirical_crps(samples, actual)
                    for weight, samples in blends.items()
                },
            )
        )
    if not predictions:
        raise ValueError("no completed Q4 validation targets are available")
    metrics = calculate_continuous_metrics(predictions)
    target_years = sorted({origin.target_year for origin, _scores in scored})
    calibration_error = max(
        abs(metrics["interval_50_coverage"] - 0.50),
        abs(metrics["interval_80_coverage"] - 0.80),
        abs(metrics["interval_95_coverage"] - 0.95),
    )
    current_weight = min(
        candidates,
        key=lambda weight: (_candidate_score(scored, weight), weight),
    )
    decision = evaluate_publication_gate(
        PublicationEvidence(
            origin_count=len(predictions),
            complete_feature_ratio=metrics["complete_feature_ratio"],
            primary_score=metrics["crps"],
            baseline_score=metrics["baseline_crps"],
            calibration_error=calibration_error,
            probabilities_valid=True,
            critical_inputs_available=True,
        ),
        thresholds,
    )
    reasons = list(decision.reason_codes)
    if len(target_years) < int(minimum_target_years):
        reasons.append("insufficient_independent_target_years")
    status = decision.status
    if status == "READY" and reasons:
        status = "LIMITED"
    latest_target_at = max(_timestamp(row.target_available_at) for row, _ in scored)
    metrics_payload: dict[str, float | str] = {
        **metrics,
        "origin_count": float(len(predictions)),
        "target_year_count": float(len(target_years)),
        "calibration_error": calibration_error,
        "official_spf_crps": sum(spf_scores) / len(spf_scores),
        "selected_model_weight": current_weight,
        "mean_rolling_selected_model_weight": sum(selected_weights) / len(selected_weights),
        "latest_training_target_through_at": latest_target_at.isoformat(),
    }
    return CorePCEQ4Artifact(
        trained_cutoff_at=cutoff.isoformat(),
        training_start_date=f"{target_years[0]}-01-01",
        trained_through_date=f"{target_years[-1]}-12-31",
        model_weight=current_weight,
        spf_weight=1.0 - current_weight,
        validation_metrics=metrics_payload,
        publication_status=status,
        publication_reasons=tuple(dict.fromkeys(reasons)),
    )


def _month(value: object) -> date:
    parsed = (
        value.date()
        if isinstance(value, datetime)
        else value
        if isinstance(value, date)
        else date.fromisoformat(str(value).strip()[:10])
    )
    return parsed.replace(day=1)


def _next_month(value: date) -> date:
    return date(
        value.year + (1 if value.month == 12 else 0),
        1 if value.month == 12 else value.month + 1,
        1,
    )


def _first_release_core_levels(
    vintage_rows: Sequence[Mapping[str, object]], *, cutoff: datetime
) -> dict[date, tuple[datetime, float]]:
    first: dict[date, tuple[datetime, float]] = {}
    for row in vintage_rows:
        if str(row.get("series_id") or "").upper() != "PCEPILFE":
            continue
        try:
            released = _timestamp(row.get("released_at"))
            observation = _month(row.get("observation_date"))
            value = float(row.get("value"))
        except (TypeError, ValueError):
            continue
        if released > cutoff or not math.isfinite(value) or value <= 0.0:
            continue
        current = first.get(observation)
        if current is None or released < current[0]:
            first[observation] = (released, value)
    return first


def _actual_q4_targets(
    vintage_rows: Sequence[Mapping[str, object]], *, cutoff: datetime
) -> dict[int, tuple[float, datetime]]:
    from finance.inflation_path import calculate_q4_over_q4

    first = _first_release_core_levels(vintage_rows, cutoff=cutoff)
    years = sorted({month.year for month in first})
    targets: dict[int, tuple[float, datetime]] = {}
    for year in years:
        required = [
            date(target_year, month, 1)
            for target_year in (year - 1, year)
            for month in (10, 11, 12)
        ]
        if any(month not in first for month in required):
            continue
        available_at = first[date(year, 12, 1)][0]
        if available_at > cutoff:
            continue
        # Chain-price indexes are periodically rebased. Mixing each month's first
        # published level across different base vintages creates false jumps.
        # Score the outcome from the single internally consistent vintage known
        # when December was first released.
        values = _latest_core_levels_at(vintage_rows, origin=available_at)
        targets[year] = (calculate_q4_over_q4(values, year=year), available_at)
    return targets


def _latest_core_levels_at(
    vintage_rows: Sequence[Mapping[str, object]], *, origin: datetime
) -> dict[date, float]:
    latest: dict[date, tuple[datetime, str, float]] = {}
    for row in vintage_rows:
        if str(row.get("series_id") or "").upper() != "PCEPILFE":
            continue
        try:
            released = _timestamp(row.get("released_at"))
            observation = _month(row.get("observation_date"))
            value = float(row.get("value"))
        except (TypeError, ValueError):
            continue
        if released > origin or observation > origin.date() or value <= 0.0:
            continue
        candidate = (released, str(row.get("realtime_start") or ""), value)
        if observation not in latest or candidate[:2] > latest[observation][:2]:
            latest[observation] = candidate
    return {month: latest[month][2] for month in sorted(latest)}


def _model_q4_samples_at_origin(
    vintage_rows: Sequence[Mapping[str, object]],
    *,
    origin: datetime,
    target_year: int,
    sample_count: int,
    seed: int,
    minimum_training_rows: int,
) -> tuple[float, ...]:
    from finance.inflation_path import (
        InflationStateDefinition,
        simulate_core_pce_paths,
    )
    from finance.inflation_policy_model import fit_core_pce_hybrid_artifact

    artifact = fit_core_pce_hybrid_artifact(
        vintage_rows,
        as_of_at=origin,
        thresholds=PublicationThresholds(
            minimum_origins=1,
            minimum_complete_feature_ratio=0.0,
            maximum_calibration_error=1.0,
            require_baseline_improvement=False,
        ),
        minimum_training_rows=minimum_training_rows,
        ridge_alpha=1.0,
        max_component_weight=0.60,
    )
    levels = _latest_core_levels_at(vintage_rows, origin=origin)
    if not levels:
        raise ValueError("Core PCE levels are unavailable at Q4 validation origin")
    last_known = max(levels)
    final_month = date(int(target_year), 12, 1)
    if last_known >= final_month:
        raise ValueError("Q4 target was already observed at forecast origin")
    months: list[date] = []
    current = _next_month(last_known)
    while current <= final_month:
        months.append(current)
        current = _next_month(current)
    component_paths = {
        name: {month: value for month in months}
        for name, value in artifact.latest_component_mom_pct.items()
    }
    dummy_state = InflationStateDefinition(
        definition_version="q4-validation-only",
        target_period=str(target_year),
        sep_released_at=origin.isoformat(),
        sep_center_pct=2.0,
        forecast_error_pct=0.25,
        price_stability_target_pct=2.0,
        boundaries_pct=(1.5, 2.0, 3.0, 4.0),
    )
    forecast = simulate_core_pce_paths(
        levels,
        forecast_months=months,
        component_monthly_mom_pct=component_paths,
        component_weights=artifact.component_weights,
        residual_history_pct=artifact.predictive_residuals_pct,
        sample_count=sample_count,
        seed=seed,
        state_definition=dummy_state,
        thresholds_pct=(),
    )
    return forecast.q4_samples_pct


def build_q4_validation_origins(
    vintage_rows: Sequence[Mapping[str, object]],
    spf_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: object,
    sample_count: int = 400,
    minimum_training_rows: int = 36,
) -> tuple[Q4ValidationOrigin, ...]:
    """Build direct Q4 targets and exact-origin monthly/SPF forecast distributions."""

    cutoff = _timestamp(as_of_at)
    actuals = _actual_q4_targets(vintage_rows, cutoff=cutoff)
    grouped: dict[tuple[int, int, str], list[Mapping[str, object]]] = {}
    for row in spf_rows:
        try:
            survey_year = int(row.get("survey_year") or 0)
            target_year = int(row.get("target_year") or 0)
            quarter = int(row.get("survey_quarter") or 0)
            released_at = str(row.get("released_at") or "")
        except (TypeError, ValueError):
            continue
        if target_year != survey_year or not released_at:
            continue
        grouped.setdefault((target_year, quarter, released_at), []).append(row)
    origins: list[Q4ValidationOrigin] = []
    for (target_year, quarter, released_at), distribution in sorted(grouped.items()):
        if target_year not in actuals:
            continue
        origin = _timestamp(released_at)
        actual, target_available = actuals[target_year]
        if origin > cutoff or target_available > cutoff:
            continue
        try:
            spf_samples, _ = spf_probability_samples(
                distribution,
                target_year=target_year,
                sample_count=sample_count,
            )
            model_samples = _model_q4_samples_at_origin(
                vintage_rows,
                origin=origin,
                target_year=target_year,
                sample_count=sample_count,
                seed=target_year * 10 + quarter,
                minimum_training_rows=minimum_training_rows,
            )
        except (KeyError, TypeError, ValueError, np.linalg.LinAlgError):
            continue
        previous = actuals.get(target_year - 1)
        naive = previous[0] if previous is not None else 2.0
        origins.append(
            Q4ValidationOrigin(
                forecast_origin_at=origin.isoformat(),
                target_available_at=target_available.isoformat(),
                target_year=target_year,
                actual_q4_pct=actual,
                model_samples_pct=model_samples,
                spf_samples_pct=spf_samples,
                naive_prediction_pct=naive,
            )
        )
    return tuple(origins)


def fit_core_pce_q4_artifact(
    vintage_rows: Sequence[Mapping[str, object]],
    spf_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: object,
    thresholds: PublicationThresholds,
    minimum_target_years: int = 6,
    sample_count: int = 400,
    minimum_training_rows: int = 36,
) -> CorePCEQ4Artifact:
    """Fit the deployable Q4 linear pool from direct PIT rolling-origin evidence."""

    origins = build_q4_validation_origins(
        vintage_rows,
        spf_rows,
        as_of_at=as_of_at,
        sample_count=sample_count,
        minimum_training_rows=minimum_training_rows,
    )
    return fit_q4_linear_pool(
        origins,
        as_of_at=as_of_at,
        thresholds=thresholds,
        minimum_target_years=minimum_target_years,
    )
