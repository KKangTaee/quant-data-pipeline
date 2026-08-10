"""Point-in-time hybrid monthly Core PCE nowcast model."""

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date, datetime, timedelta, timezone
from typing import Mapping, Sequence

import numpy as np

from finance.inflation_policy_validation import (
    ContinuousValidationPrediction,
    PublicationEvidence,
    PublicationThresholds,
    calculate_continuous_metrics,
    derive_capped_inverse_error_weights,
    evaluate_publication_gate,
)


CORE_PCE_MODEL_SERIES = (
    "PCEPILFE",
    "CPILFESL",
    "CPIAUCSL",
    "PPIACO",
    "CES0500000003",
    "PCETRIM12M159SFRBDAL",
    "MICH",
)

CORE_PCE_FEATURES = (
    "core_lag_1",
    "core_lag_3_mean",
    "core_lag_6_mean",
    "core_cpi_mom",
    "headline_cpi_mom",
    "ppi_mom",
    "wage_mom",
    "trimmed_mean_monthly_proxy",
    "michigan_expectations_monthly_proxy",
)

_BRIDGE_WEIGHTS = {
    "core_lag_3_mean": 0.45,
    "core_cpi_mom": 0.25,
    "headline_cpi_mom": 0.10,
    "ppi_mom": 0.05,
    "wage_mom": 0.05,
    "trimmed_mean_monthly_proxy": 0.10,
}


@dataclass(frozen=True)
class CorePCENowcastRow:
    observation_month: str
    forecast_origin_at: str
    target_available_at: str
    training_values_released_through_at: str
    features: dict[str, float | None]
    target_mom_pct: float
    complete_feature_ratio: float


@dataclass(frozen=True)
class CorePCEHybridArtifact:
    training_start_date: str
    trained_through_date: str
    trained_cutoff_at: str
    feature_names: tuple[str, ...]
    feature_means: tuple[float, ...]
    feature_scales: tuple[float, ...]
    ridge_coefficients: tuple[float, ...]
    ridge_alpha: float
    bridge_weights: dict[str, float]
    component_weights: dict[str, float]
    component_errors: dict[str, float]
    predictive_residuals_pct: tuple[float, ...]
    validation_metrics: dict[str, float]
    publication_status: str
    publication_reasons: tuple[str, ...]
    latest_component_mom_pct: dict[str, float]
    latest_feature_values: dict[str, float | None]


def _timestamp(value: object) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _month(value: object) -> date:
    if isinstance(value, datetime):
        parsed = value.date()
    elif isinstance(value, date):
        parsed = value
    else:
        parsed = date.fromisoformat(str(value).strip()[:10])
    return parsed.replace(day=1)


def _next_month(value: date) -> date:
    return date(
        value.year + (1 if value.month == 12 else 0),
        1 if value.month == 12 else value.month + 1,
        1,
    )


def _finite(value: object, *, field: str) -> float:
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _normalized_rows(
    vintage_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: object,
) -> tuple[dict[str, object], ...]:
    cutoff = _timestamp(as_of_at)
    normalized: list[dict[str, object]] = []
    for raw in vintage_rows:
        series_id = str(raw.get("series_id") or "").upper()
        if series_id not in CORE_PCE_MODEL_SERIES or raw.get("value") in (None, ""):
            continue
        try:
            released_at = _timestamp(raw.get("released_at"))
            observation = _month(raw.get("observation_date"))
            value = _finite(raw.get("value"), field=f"{series_id} value")
        except (TypeError, ValueError):
            continue
        if released_at > cutoff:
            continue
        row = dict(raw)
        row["series_id"] = series_id
        row["observation_date"] = observation
        row["released_at"] = released_at
        row["value"] = value
        normalized.append(row)
    return tuple(
        sorted(
            normalized,
            key=lambda row: (
                str(row["series_id"]),
                row["observation_date"],
                row["released_at"],
                str(row.get("realtime_start") or ""),
            ),
        )
    )


def _latest_points(
    rows: Sequence[Mapping[str, object]],
    *,
    series_id: str,
    cutoff: datetime,
    observation_cutoff: date,
) -> tuple[dict[str, object], ...]:
    latest: dict[date, dict[str, object]] = {}
    for raw in rows:
        if raw["series_id"] != series_id:
            continue
        observation = raw["observation_date"]
        released_at = raw["released_at"]
        if not isinstance(observation, date) or not isinstance(released_at, datetime):
            continue
        if observation > observation_cutoff or released_at > cutoff:
            continue
        current = latest.get(observation)
        candidate_key = (
            released_at,
            str(raw.get("realtime_start") or ""),
            str(raw.get("collected_at") or ""),
        )
        if current is None:
            latest[observation] = dict(raw)
            continue
        current_key = (
            current["released_at"],
            str(current.get("realtime_start") or ""),
            str(current.get("collected_at") or ""),
        )
        if candidate_key > current_key:
            latest[observation] = dict(raw)
    return tuple(latest[key] for key in sorted(latest))


def _consecutive_changes(points: Sequence[Mapping[str, object]]) -> tuple[float, ...]:
    changes: list[float] = []
    for previous, current in zip(points, points[1:]):
        previous_month = previous["observation_date"]
        current_month = current["observation_date"]
        if not isinstance(previous_month, date) or not isinstance(current_month, date):
            continue
        if _next_month(previous_month) != current_month:
            continue
        previous_value = _finite(previous["value"], field="previous level")
        current_value = _finite(current["value"], field="current level")
        if previous_value <= 0.0:
            continue
        changes.append((current_value / previous_value - 1.0) * 100.0)
    return tuple(changes)


def _latest_change(
    rows: Sequence[Mapping[str, object]],
    *,
    series_id: str,
    cutoff: datetime,
    observation_cutoff: date,
) -> tuple[float | None, tuple[dict[str, object], ...]]:
    points = _latest_points(
        rows,
        series_id=series_id,
        cutoff=cutoff,
        observation_cutoff=observation_cutoff,
    )
    if len(points) < 2:
        return None, points
    previous, current = points[-2:]
    if _next_month(previous["observation_date"]) != current["observation_date"]:
        return None, points
    previous_value = _finite(previous["value"], field=f"{series_id} previous")
    current_value = _finite(current["value"], field=f"{series_id} current")
    if previous_value <= 0.0:
        return None, points
    return (current_value / previous_value - 1.0) * 100.0, points


def _feature_row(
    rows: Sequence[Mapping[str, object]],
    *,
    cutoff: datetime,
    target_month: date,
) -> tuple[dict[str, float | None], datetime]:
    core_points = _latest_points(
        rows,
        series_id="PCEPILFE",
        cutoff=cutoff,
        observation_cutoff=target_month,
    )
    core_changes = _consecutive_changes(core_points)
    features: dict[str, float | None] = {
        "core_lag_1": core_changes[-1] if core_changes else None,
        "core_lag_3_mean": (
            sum(core_changes[-3:]) / 3.0 if len(core_changes) >= 3 else None
        ),
        "core_lag_6_mean": (
            sum(core_changes[-6:]) / 6.0 if len(core_changes) >= 6 else None
        ),
    }
    used_points: list[dict[str, object]] = list(core_points[-7:])
    for feature, series_id in (
        ("core_cpi_mom", "CPILFESL"),
        ("headline_cpi_mom", "CPIAUCSL"),
        ("ppi_mom", "PPIACO"),
        ("wage_mom", "CES0500000003"),
    ):
        value, points = _latest_change(
            rows,
            series_id=series_id,
            cutoff=cutoff,
            observation_cutoff=target_month,
        )
        features[feature] = value
        used_points.extend(points[-2:])
    for feature, series_id in (
        ("trimmed_mean_monthly_proxy", "PCETRIM12M159SFRBDAL"),
        ("michigan_expectations_monthly_proxy", "MICH"),
    ):
        points = _latest_points(
            rows,
            series_id=series_id,
            cutoff=cutoff,
            observation_cutoff=target_month,
        )
        features[feature] = (
            _finite(points[-1]["value"], field=series_id) / 12.0 if points else None
        )
        used_points.extend(points[-1:])
    release_through = max(
        (
            point["released_at"]
            for point in used_points
            if isinstance(point.get("released_at"), datetime)
        ),
        default=datetime.min.replace(tzinfo=timezone.utc),
    )
    return features, release_through


def build_core_pce_nowcast_panel(
    vintage_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: object,
) -> tuple[CorePCENowcastRow, ...]:
    """Build first-release Core PCE targets from strictly earlier feature vintages."""

    cutoff = _timestamp(as_of_at)
    rows = _normalized_rows(vintage_rows, as_of_at=cutoff)
    first_releases: dict[date, dict[str, object]] = {}
    for row in rows:
        if row["series_id"] != "PCEPILFE":
            continue
        observation = row["observation_date"]
        current = first_releases.get(observation)
        if current is None or row["released_at"] < current["released_at"]:
            first_releases[observation] = dict(row)
    panel: list[CorePCENowcastRow] = []
    for target_month in sorted(first_releases):
        target_row = first_releases[target_month]
        target_release = target_row["released_at"]
        if not isinstance(target_release, datetime) or target_release > cutoff:
            continue
        previous_month = date(
            target_month.year - (1 if target_month.month == 1 else 0),
            12 if target_month.month == 1 else target_month.month - 1,
            1,
        )
        previous_points = _latest_points(
            rows,
            series_id="PCEPILFE",
            cutoff=target_release,
            observation_cutoff=previous_month,
        )
        if not previous_points or previous_points[-1]["observation_date"] != previous_month:
            continue
        previous_value = _finite(previous_points[-1]["value"], field="previous Core PCE")
        if previous_value <= 0.0:
            continue
        origin = target_release - timedelta(microseconds=1)
        features, released_through = _feature_row(
            rows,
            cutoff=origin,
            target_month=target_month,
        )
        if features["core_lag_1"] is None:
            continue
        complete = sum(value is not None for value in features.values()) / len(
            CORE_PCE_FEATURES
        )
        panel.append(
            CorePCENowcastRow(
                observation_month=target_month.isoformat(),
                forecast_origin_at=origin.isoformat(),
                target_available_at=target_release.isoformat(),
                training_values_released_through_at=released_through.isoformat(),
                features=features,
                target_mom_pct=(
                    _finite(target_row["value"], field="target Core PCE")
                    / previous_value
                    - 1.0
                )
                * 100.0,
                complete_feature_ratio=complete,
            )
        )
    return tuple(panel)


def _ridge_fit(
    rows: Sequence[CorePCENowcastRow],
    *,
    alpha: float,
) -> tuple[np.ndarray, np.ndarray, np.ndarray]:
    if not rows:
        raise ValueError("ridge training rows cannot be empty")
    raw = np.asarray(
        [
            [
                np.nan if row.features[name] is None else float(row.features[name])
                for name in CORE_PCE_FEATURES
            ]
            for row in rows
        ],
        dtype=float,
    )
    means = np.nanmean(raw, axis=0)
    means = np.where(np.isfinite(means), means, 0.0)
    filled = np.where(np.isfinite(raw), raw, means)
    scales = np.std(filled, axis=0)
    scales = np.where(scales > 1e-9, scales, 1.0)
    standardized = (filled - means) / scales
    design = np.column_stack((np.ones(len(rows)), standardized))
    targets = np.asarray([row.target_mom_pct for row in rows], dtype=float)
    penalty = np.eye(design.shape[1], dtype=float) * float(alpha)
    penalty[0, 0] = 0.0
    coefficients = np.linalg.solve(
        design.T @ design + penalty,
        design.T @ targets,
    )
    if not np.all(np.isfinite(coefficients)):
        raise ValueError("ridge coefficients must be finite")
    return means, scales, coefficients


def _ridge_predict(
    features: Mapping[str, float | None],
    *,
    means: np.ndarray,
    scales: np.ndarray,
    coefficients: np.ndarray,
) -> float:
    values = np.asarray(
        [
            means[index] if features[name] is None else float(features[name])
            for index, name in enumerate(CORE_PCE_FEATURES)
        ],
        dtype=float,
    )
    design = np.concatenate(([1.0], (values - means) / scales))
    return float(design @ coefficients)


def _bridge_prediction(features: Mapping[str, float | None]) -> float:
    available = {
        name: weight
        for name, weight in _BRIDGE_WEIGHTS.items()
        if features.get(name) is not None
    }
    if not available:
        raise ValueError("bridge prediction has no available features")
    total = sum(available.values())
    return sum(
        available[name] / total * float(features[name])  # type: ignore[arg-type]
        for name in available
    )


def _component_predictions(
    features: Mapping[str, float | None],
    *,
    means: np.ndarray,
    scales: np.ndarray,
    coefficients: np.ndarray,
) -> dict[str, float]:
    momentum = features.get("core_lag_3_mean")
    if momentum is None:
        momentum = features.get("core_lag_1")
    if momentum is None:
        raise ValueError("Core PCE momentum is required")
    return {
        "bridge": _bridge_prediction(features),
        "ridge": _ridge_predict(
            features,
            means=means,
            scales=scales,
            coefficients=coefficients,
        ),
        "momentum": float(momentum),
    }


def fit_core_pce_hybrid_artifact(
    vintage_rows: Sequence[Mapping[str, object]],
    *,
    as_of_at: object,
    thresholds: PublicationThresholds,
    minimum_training_rows: int,
    ridge_alpha: float,
    max_component_weight: float,
) -> CorePCEHybridArtifact:
    """Fit bridge, ridge, and momentum components with chronological validation."""

    panel = build_core_pce_nowcast_panel(vintage_rows, as_of_at=as_of_at)
    minimum = max(12, int(minimum_training_rows))
    if len(panel) <= minimum:
        raise ValueError("insufficient PIT Core PCE rows for hybrid training")
    component_errors: dict[str, list[float]] = {
        "bridge": [],
        "ridge": [],
        "momentum": [],
    }
    baseline_errors: dict[str, list[float]] = {
        "persistence": [],
        "rolling_3m": [],
        "rolling_6m": [],
    }
    residuals: list[float] = []
    predictions: list[ContinuousValidationPrediction] = []
    release_groups: dict[str, list[CorePCENowcastRow]] = {}
    for row in panel:
        release_groups.setdefault(row.target_available_at, []).append(row)
    origin_count = 0
    for release_at in sorted(release_groups, key=_timestamp):
        training = tuple(
            row
            for row in panel
            if _timestamp(row.target_available_at) < _timestamp(release_at)
        )
        if len(training) < minimum:
            continue
        means, scales, coefficients = _ridge_fit(training, alpha=ridge_alpha)
        if all(component_errors[name] for name in component_errors):
            weights = derive_capped_inverse_error_weights(
                {
                    name: max(sum(errors) / len(errors), 1e-9)
                    for name, errors in component_errors.items()
                },
                max_component_weight=max_component_weight,
            )
        else:
            weights = {name: 1.0 / len(component_errors) for name in component_errors}
        if residuals:
            residual_center = sum(residuals) / len(residuals)
            prior_residuals = tuple(
                residual - residual_center for residual in residuals
            )
        else:
            prior_residuals = (0.0,)
        training_through = max(
            training,
            key=lambda row: _timestamp(row.target_available_at),
        ).target_available_at
        batch_updates: list[tuple[dict[str, float], float, float]] = []
        for evaluation in release_groups[release_at]:
            components = _component_predictions(
                evaluation.features,
                means=means,
                scales=scales,
                coefficients=coefficients,
            )
            predicted = sum(
                weights[name] * components[name] for name in components
            )
            actual = evaluation.target_mom_pct
            baseline_values = {
                "persistence": evaluation.features["core_lag_1"],
                "rolling_3m": evaluation.features["core_lag_3_mean"],
                "rolling_6m": evaluation.features["core_lag_6_mean"],
            }
            if any(value is None for value in baseline_values.values()):
                raise ValueError("Core PCE baseline features are incomplete")
            predictions.append(
                ContinuousValidationPrediction(
                    forecast_origin_at=evaluation.forecast_origin_at,
                    target_available_at=evaluation.target_available_at,
                    training_target_through_at=training_through,
                    actual_value=actual,
                    predicted_median=predicted,
                    predictive_samples=tuple(
                        predicted + residual for residual in prior_residuals
                    ),
                    baseline_prediction=float(evaluation.features["core_lag_1"]),
                    complete_feature_ratio=evaluation.complete_feature_ratio,
                )
            )
            for name, value in baseline_values.items():
                baseline_errors[name].append(abs(actual - float(value)))
            batch_updates.append((components, actual, predicted))
        # Targets released in one batch cannot update sibling predictions.
        for components, actual, predicted in batch_updates:
            for name, value in components.items():
                component_errors[name].append(abs(actual - value))
            residuals.append(actual - predicted)
        origin_count += 1
    metrics = calculate_continuous_metrics(predictions)
    baseline_scores = {
        name: sum(errors) / len(errors)
        for name, errors in baseline_errors.items()
    }
    metrics.update(
        {
            "baseline_persistence_crps": baseline_scores["persistence"],
            "baseline_rolling_3m_crps": baseline_scores["rolling_3m"],
            "baseline_rolling_6m_crps": baseline_scores["rolling_6m"],
            "baseline_crps": min(baseline_scores.values()),
        }
    )
    calibration_error = max(
        abs(metrics["interval_50_coverage"] - 0.50),
        abs(metrics["interval_80_coverage"] - 0.80),
        abs(metrics["interval_95_coverage"] - 0.95),
    )
    decision = evaluate_publication_gate(
        PublicationEvidence(
            origin_count=origin_count,
            complete_feature_ratio=metrics["complete_feature_ratio"],
            primary_score=metrics["crps"],
            baseline_score=metrics["baseline_crps"],
            calibration_error=calibration_error,
            probabilities_valid=True,
            critical_inputs_available=True,
        ),
        thresholds,
    )
    publication_status = decision.status
    publication_reasons = decision.reason_codes
    errors = {
        name: max(sum(values) / len(values), 1e-9)
        for name, values in component_errors.items()
    }
    weights = derive_capped_inverse_error_weights(
        errors,
        max_component_weight=max_component_weight,
    )
    means, scales, coefficients = _ridge_fit(panel, alpha=ridge_alpha)
    normalized = _normalized_rows(vintage_rows, as_of_at=as_of_at)
    core_points = _latest_points(
        normalized,
        series_id="PCEPILFE",
        cutoff=_timestamp(as_of_at),
        observation_cutoff=_timestamp(as_of_at).date().replace(day=1),
    )
    if not core_points:
        raise ValueError("current Core PCE level is unavailable")
    current_features, _released_through = _feature_row(
        normalized,
        cutoff=_timestamp(as_of_at),
        target_month=_next_month(core_points[-1]["observation_date"]),
    )
    latest_components = _component_predictions(
        current_features,
        means=means,
        scales=scales,
        coefficients=coefficients,
    )
    validation = {
        **metrics,
        "origin_count": float(origin_count),
        "target_count": float(len(predictions)),
        "calibration_error": calibration_error,
    }
    residual_center = sum(residuals) / len(residuals)
    centered_residuals = tuple(
        residual - residual_center for residual in residuals
    )
    return CorePCEHybridArtifact(
        training_start_date=panel[0].observation_month,
        trained_through_date=core_points[-1]["observation_date"].isoformat(),
        trained_cutoff_at=_timestamp(as_of_at).isoformat(),
        feature_names=CORE_PCE_FEATURES,
        feature_means=tuple(float(value) for value in means),
        feature_scales=tuple(float(value) for value in scales),
        ridge_coefficients=tuple(float(value) for value in coefficients),
        ridge_alpha=float(ridge_alpha),
        bridge_weights=dict(_BRIDGE_WEIGHTS),
        component_weights=weights,
        component_errors=errors,
        predictive_residuals_pct=centered_residuals,
        validation_metrics=validation,
        publication_status=publication_status,
        publication_reasons=publication_reasons,
        latest_component_mom_pct=latest_components,
        latest_feature_values=current_features,
    )
