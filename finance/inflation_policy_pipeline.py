"""Materialize independently gated inflation, policy, and resistance analysis."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass
from datetime import date, datetime, timezone
from typing import Callable, Mapping, Sequence

from finance.inflation_path import (
    CorePCEPathForecast,
    derive_state_definition,
    simulate_core_pce_paths,
)
from finance.inflation_policy_validation import (
    ContinuousValidationPrediction,
    PublicationThresholds,
    calculate_continuous_metrics,
    derive_capped_inverse_error_weights,
    evaluate_publication_gate,
    PublicationEvidence,
)
from finance.inflation_policy_model import (
    CORE_PCE_MODEL_SERIES,
    CorePCEHybridArtifact,
    fit_core_pce_hybrid_artifact,
)
from finance.loaders.inflation_policy import (
    InflationPolicyDataBundle,
    load_inflation_policy_data_bundle,
    load_inflation_policy_training_vintages,
)
from finance.policy_path import (
    POLICY_NET_MOVE_BUCKETS,
    build_policy_path_forecast,
    derive_decision_action_prior,
    derive_sep_net_move_prior,
    project_inflation_states_to_policy,
)
from finance.yield_resistance import (
    build_dynamic_resistance_zones,
    decompose_yield_driver,
    replay_resistance_state,
)


@dataclass(frozen=True)
class CorePCEMomentumArtifact:
    training_start_date: str
    trained_through_date: str
    trained_cutoff_at: str
    component_weights: dict[str, float]
    component_errors: dict[str, float]
    predictive_residuals_pct: tuple[float, ...]
    validation_metrics: dict[str, float]
    publication_status: str
    publication_reasons: tuple[str, ...]
    latest_component_mom_pct: dict[str, float]


@dataclass(frozen=True)
class InflationPolicyEngineConfig:
    model_version: str
    state_forecast_error_floor_pct: float
    price_stability_target_pct: float
    threshold_levels_pct: tuple[float, ...]
    reaction_matrix: Mapping[str, Mapping[str, object]]
    policy_component_weights: Mapping[str, object]
    next_action_component_weights: Mapping[str, object]
    max_component_weight: float
    core_validation_thresholds: PublicationThresholds


@dataclass(frozen=True)
class InflationPolicyMaterialization:
    snapshot_row: dict[str, object]
    model_artifact_rows: tuple[dict[str, object], ...]
    inflation: dict[str, object]
    policy: dict[str, object]
    rates: dict[str, object]
    reverse: dict[str, object]
    warnings: tuple[str, ...]


def build_limited_reference_config(*, model_version: str) -> InflationPolicyEngineConfig:
    """Return the versioned, deliberately uncalibrated policy reaction prior."""

    reaction = {
        state: {bucket: 0.0 for bucket in POLICY_NET_MOVE_BUCKETS}
        for state in (
            "rapid_disinflation",
            "gradual_disinflation",
            "sticky",
            "reacceleration",
            "shock_reacceleration",
        )
    }
    reaction["rapid_disinflation"].update({"cut_1": 0.60, "hold": 0.40})
    reaction["gradual_disinflation"].update({"cut_1": 0.30, "hold": 0.70})
    reaction["sticky"].update({"hold": 0.80, "hike_1": 0.20})
    reaction["reacceleration"].update(
        {"hold": 0.30, "hike_1": 0.50, "hike_2": 0.20}
    )
    reaction["shock_reacceleration"].update(
        {"hold": 0.20, "hike_1": 0.40, "hike_2": 0.30, "hike_3_plus": 0.10}
    )
    return InflationPolicyEngineConfig(
        model_version=str(model_version),
        state_forecast_error_floor_pct=0.20,
        price_stability_target_pct=2.0,
        threshold_levels_pct=(3.4, 3.5, 3.6),
        reaction_matrix=reaction,
        policy_component_weights={"sep": 0.50, "economic": 0.50},
        next_action_component_weights={"committee": 1.0},
        max_component_weight=0.70,
        core_validation_thresholds=PublicationThresholds(
            minimum_origins=36,
            minimum_complete_feature_ratio=0.80,
            maximum_calibration_error=0.20,
            require_baseline_improvement=True,
        ),
    )


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


def _timestamp(value: object) -> datetime:
    parsed = (
        value
        if isinstance(value, datetime)
        else datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    )
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _core_level_rows(
    macro_rows: Sequence[Mapping[str, object]],
) -> tuple[tuple[date, str, float], ...]:
    rows: dict[date, tuple[str, float]] = {}
    for row in macro_rows:
        if str(row.get("series_id") or "").upper() != "PCEPILFE":
            continue
        if row.get("value") in (None, ""):
            continue
        month = _month(row["observation_date"])
        rows[month] = (
            str(row.get("released_at") or month.isoformat()),
            _finite(row["value"], field="Core PCE index"),
        )
    return tuple(
        (month, rows[month][0], rows[month][1]) for month in sorted(rows)
    )


def _mom_history(
    macro_rows: Sequence[Mapping[str, object]],
) -> tuple[tuple[date, str, float], ...]:
    levels = _core_level_rows(macro_rows)
    changes: list[tuple[date, str, float]] = []
    for previous, current in zip(levels, levels[1:]):
        if _next_month(previous[0]) != current[0]:
            continue
        changes.append(
            (
                current[0],
                current[1],
                (current[2] / previous[2] - 1.0) * 100.0,
            )
        )
    return tuple(changes)


def _component_predictions(history: Sequence[float]) -> dict[str, float]:
    if len(history) < 6:
        raise ValueError("six monthly changes are required for momentum components")
    return {
        "persistence": float(history[-1]),
        "recent_3m": float(sum(history[-3:]) / 3.0),
        "recent_6m": float(sum(history[-6:]) / 6.0),
    }


def fit_core_pce_momentum_artifact(
    macro_rows: Sequence[Mapping[str, object]],
    *,
    thresholds: PublicationThresholds,
    minimum_history_months: int,
    max_component_weight: float,
) -> CorePCEMomentumArtifact:
    """Fit a transparent rolling-origin Core PCE ensemble and its residual evidence."""

    levels = _core_level_rows(macro_rows)
    changes = _mom_history(macro_rows)
    minimum = max(6, int(minimum_history_months))
    if len(levels) < minimum + 1 or len(changes) < minimum:
        raise ValueError("insufficient Core PCE history for rolling-origin validation")
    component_errors: dict[str, list[float]] = {
        "persistence": [],
        "recent_3m": [],
        "recent_6m": [],
    }
    validation_baseline_errors: dict[str, list[float]] = {
        "persistence": [],
        "rolling_3m": [],
        "rolling_6m": [],
    }
    residuals: list[float] = []
    predictions: list[ContinuousValidationPrediction] = []
    values = [item[2] for item in changes]
    for index in range(minimum, len(changes)):
        history = values[:index]
        components = _component_predictions(history)
        if all(component_errors[name] for name in component_errors):
            prior_mae = {
                name: max(sum(errors) / len(errors), 1e-9)
                for name, errors in component_errors.items()
            }
            weights = derive_capped_inverse_error_weights(
                prior_mae,
                max_component_weight=max_component_weight,
            )
        else:
            weights = {name: 1.0 / 3.0 for name in component_errors}
        predicted = sum(weights[name] * components[name] for name in components)
        if residuals:
            residual_center = sum(residuals) / len(residuals)
            prior_residuals = tuple(
                residual - residual_center for residual in residuals
            )
        else:
            prior_residuals = (0.0,)
        actual = values[index]
        training_release = max(_timestamp(item[1]) for item in changes[:index])
        target_release = _timestamp(changes[index][1])
        if training_release < target_release:
            predictions.append(
                ContinuousValidationPrediction(
                    forecast_origin_at=training_release.isoformat(),
                    target_available_at=target_release.isoformat(),
                    training_target_through_at=training_release.isoformat(),
                    actual_value=actual,
                    predicted_median=predicted,
                    predictive_samples=tuple(
                        predicted + residual for residual in prior_residuals
                    ),
                    baseline_prediction=components["persistence"],
                    complete_feature_ratio=1.0,
                )
            )
            for baseline_name, component_name in (
                ("persistence", "persistence"),
                ("rolling_3m", "recent_3m"),
                ("rolling_6m", "recent_6m"),
            ):
                validation_baseline_errors[baseline_name].append(
                    abs(actual - components[component_name])
                )
        for name, component_prediction in components.items():
            component_errors[name].append(abs(actual - component_prediction))
        residuals.append(actual - predicted)
    if predictions:
        metrics = calculate_continuous_metrics(predictions)
        calibration_error = max(
            abs(metrics["interval_50_coverage"] - 0.50),
            abs(metrics["interval_80_coverage"] - 0.80),
            abs(metrics["interval_95_coverage"] - 0.95),
        )
    else:
        fit_mae = sum(abs(value) for value in residuals) / len(residuals)
        fit_rmse = math.sqrt(sum(value**2 for value in residuals) / len(residuals))
        persistence_errors = component_errors["persistence"]
        metrics = {
            "mae": fit_mae,
            "rmse": fit_rmse,
            "crps": fit_mae,
            "baseline_crps": sum(persistence_errors) / len(persistence_errors),
            "interval_50_coverage": 0.0,
            "interval_80_coverage": 0.0,
            "interval_95_coverage": 0.0,
            "complete_feature_ratio": 0.0,
        }
        calibration_error = 1.0
    baseline_source = (
        validation_baseline_errors if predictions else {
            "persistence": component_errors["persistence"],
            "rolling_3m": component_errors["recent_3m"],
            "rolling_6m": component_errors["recent_6m"],
        }
    )
    baseline_scores = {
        name: sum(errors) / len(errors)
        for name, errors in baseline_source.items()
    }
    metrics.update(
        {
            "baseline_persistence_crps": baseline_scores["persistence"],
            "baseline_rolling_3m_crps": baseline_scores["rolling_3m"],
            "baseline_rolling_6m_crps": baseline_scores["rolling_6m"],
            "baseline_crps": min(baseline_scores.values()),
        }
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
    final_errors = {
        name: max(sum(errors) / len(errors), 1e-9)
        for name, errors in component_errors.items()
    }
    final_weights = derive_capped_inverse_error_weights(
        final_errors,
        max_component_weight=max_component_weight,
    )
    validation = {
        **metrics,
        "origin_count": float(len(predictions)),
        "calibration_error": calibration_error,
    }
    residual_center = sum(residuals) / len(residuals)
    centered_residuals = tuple(
        residual - residual_center for residual in residuals
    )
    return CorePCEMomentumArtifact(
        training_start_date=levels[0][0].isoformat(),
        trained_through_date=levels[-1][0].isoformat(),
        trained_cutoff_at=max(_timestamp(row[1]) for row in levels).isoformat(),
        component_weights=final_weights,
        component_errors=final_errors,
        predictive_residuals_pct=centered_residuals,
        validation_metrics=validation,
        publication_status=decision.status,
        publication_reasons=decision.reason_codes,
        latest_component_mom_pct=_component_predictions(values),
    )


def _not_available_materialization(
    *,
    bundle: InflationPolicyDataBundle,
    config: InflationPolicyEngineConfig,
    reason: str,
) -> InflationPolicyMaterialization:
    inflation = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    policy = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    rates = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    reverse = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    warnings = (reason, "recession_model_not_available")
    snapshot = {
        "as_of_at": bundle.as_of_at,
        "model_version": config.model_version,
        "run_kind": "historical_replay",
        "publication_status": "NOT_AVAILABLE",
        "inflation_json": inflation,
        "policy_json": policy,
        "rates_json": rates,
        "reverse_json": reverse,
        "evidence_json": {"coverage": bundle.coverage},
        "freshness_json": {"as_of_at": bundle.as_of_at},
        "warnings_json": warnings,
    }
    return InflationPolicyMaterialization(
        snapshot_row=snapshot,
        model_artifact_rows=(),
        inflation=inflation,
        policy=policy,
        rates=rates,
        reverse=reverse,
        warnings=warnings,
    )


def _forecast_months(last_known: date) -> tuple[date, ...]:
    months: list[date] = []
    current = _next_month(last_known)
    while current.year == last_known.year and current.month <= 12:
        months.append(current)
        current = _next_month(current)
    return tuple(months)


def _latest_decision(decisions: Sequence[Mapping[str, object]]) -> Mapping[str, object]:
    if not decisions:
        raise ValueError("FOMC decision history is required")
    return max(decisions, key=lambda row: str(row.get("released_at") or ""))


def _series_rows(
    macro_rows: Sequence[Mapping[str, object]], series_id: str
) -> list[dict[str, object]]:
    return sorted(
        (
            {
                "observation_date": row["observation_date"],
                "value": float(row["value"]),
            }
            for row in macro_rows
            if str(row.get("series_id") or "").upper() == series_id
            and row.get("value") not in (None, "")
        ),
        key=lambda row: str(row["observation_date"]),
    )


def _change_bp(rows: Sequence[Mapping[str, object]], *, lookback_rows: int = 21) -> float:
    if len(rows) < 2:
        raise ValueError("rate change requires at least two observations")
    window = rows[-max(2, int(lookback_rows)) :]
    return (float(window[-1]["value"]) - float(window[0]["value"])) * 100.0


def _freshness_summary(
    bundle: InflationPolicyDataBundle,
    *,
    trained_through_date: str | None = None,
    trained_cutoff_at: str | None = None,
) -> dict[str, object]:
    """Build compact release/observation evidence and enforce the PIT cutoff."""

    cutoff = _timestamp(bundle.as_of_at)
    if (trained_through_date is None) != (trained_cutoff_at is None):
        raise ValueError("artifact freshness fields must be provided together")
    artifact_cutoff: datetime | None = None
    trained_through: date | None = None
    if trained_cutoff_at is not None and trained_through_date is not None:
        artifact_cutoff = _timestamp(trained_cutoff_at)
        if artifact_cutoff > cutoff:
            raise ValueError(
                f"artifact trained_cutoff_at {artifact_cutoff.isoformat()} "
                f"exceeds cutoff {cutoff.isoformat()}"
            )
        if artifact_cutoff != cutoff:
            raise ValueError(
                f"artifact trained_cutoff_at {artifact_cutoff.isoformat()} "
                f"does not match replay cutoff {cutoff.isoformat()}"
            )
        trained_through = date.fromisoformat(
            str(trained_through_date).strip()[:10]
        )
        if trained_through > cutoff.date():
            raise ValueError(
                f"artifact trained_through_date {trained_through.isoformat()} "
                f"exceeds cutoff date {cutoff.date().isoformat()}"
            )
    all_releases: list[datetime] = []

    def component(
        rows: Sequence[Mapping[str, object]],
        *,
        observation_field: str,
    ) -> dict[str, object]:
        releases: list[datetime] = []
        observations: list[str] = []
        for row in rows:
            if row.get("released_at") in (None, ""):
                raise ValueError("input row is missing released_at")
            released_at = _timestamp(row["released_at"])
            if released_at > cutoff:
                raise ValueError(
                    f"input release {released_at.isoformat()} exceeds cutoff "
                    f"{cutoff.isoformat()}"
                )
            releases.append(released_at)
            all_releases.append(released_at)
            if row.get(observation_field) not in (None, ""):
                observations.append(str(row[observation_field])[:10])
        return {
            "row_count": len(rows),
            "latest_observation_date": max(observations) if observations else None,
            "latest_released_at": (
                max(releases).isoformat() if releases else None
            ),
        }

    macro_groups: dict[str, list[Mapping[str, object]]] = {}
    for row in bundle.macro_rows:
        series_id = str(row.get("series_id") or "").strip().upper()
        if not series_id:
            raise ValueError("macro input row is missing series_id")
        macro_groups.setdefault(series_id, []).append(row)
    macro_series = {
        series_id: component(rows, observation_field="observation_date")
        for series_id, rows in sorted(macro_groups.items())
    }
    sep = component(bundle.sep_rows, observation_field="meeting_date")
    decisions = component(bundle.decision_rows, observation_field="meeting_date")
    term_premium = component(
        bundle.term_premium_rows,
        observation_field="observation_date",
    )
    summary: dict[str, object] = {
        "as_of_at": cutoff.isoformat(),
        "max_released_at": max(all_releases).isoformat() if all_releases else None,
        "macro_series": macro_series,
        "sep": sep,
        "fomc_decisions": decisions,
        "term_premium": term_premium,
    }
    if artifact_cutoff is not None and trained_through is not None:
        summary.update(
            {
                "trained_cutoff_at": artifact_cutoff.isoformat(),
                "trained_through_date": trained_through.isoformat(),
            }
        )
    return summary


def _resistance_payload(
    rows: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    if not rows:
        return {"publication_status": "NOT_AVAILABLE", "zones": []}
    zones = build_dynamic_resistance_zones(
        rows,
        as_of_date=str(rows[-1]["observation_date"]),
    )
    recent = tuple(float(row["value"]) for row in rows[-5:])
    serialized_zones = []
    for zone in zones:
        payload = asdict(zone)
        payload["state"] = replay_resistance_state(
            rows,
            zone_lower_pct=zone.zone_lower_pct,
            zone_upper_pct=zone.zone_upper_pct,
            buffer_pct=zone.tolerance_pct,
            known_at_date=zone.known_at_date,
        )
        payload["breakout_probability"] = None
        payload["hold_probability"] = None
        serialized_zones.append(payload)
    current_value = recent[-1]
    engaged = [
        zone
        for zone in serialized_zones
        if zone["zone_lower_pct"] - zone["tolerance_pct"]
        <= current_value
        <= zone["zone_upper_pct"] + zone["tolerance_pct"]
    ]
    active_zone = None
    if engaged:
        active_zone = dict(
            max(engaged, key=lambda zone: float(zone["zone_strength"]))
        )
        active_zone["selection_reason"] = (
            "current_yield_inside_buffered_zone_highest_strength"
        )
        active_zone["distance_bp"] = 0.0
    overhead = [
        zone for zone in serialized_zones if float(zone["zone_lower_pct"]) > current_value
    ]
    next_overhead = None
    if overhead:
        next_overhead = dict(
            min(
                overhead,
                key=lambda zone: (
                    float(zone["zone_lower_pct"]),
                    -float(zone["zone_strength"]),
                ),
            )
        )
        next_overhead["selection_reason"] = "nearest_confirmed_overhead_zone"
        next_overhead["distance_bp"] = round(
            (float(next_overhead["zone_lower_pct"]) - current_value) * 100.0,
            4,
        )
    return {
        "publication_status": "LIMITED",
        "current_value_pct": current_value,
        "observation_date": str(rows[-1]["observation_date"]),
        "zones": serialized_zones,
        "active_test_zone": active_zone,
        "next_overhead_zone": next_overhead,
    }


def _build_rates_payload(bundle: InflationPolicyDataBundle) -> dict[str, object]:
    """Materialize Treasury evidence independently from the Core PCE gate."""

    rate_series = {
        series_id: _series_rows(bundle.macro_rows, series_id)
        for series_id in ("DGS2", "DGS10", "DFII10", "T10YIE")
    }
    if not rate_series["DGS10"]:
        return {
            "publication_status": "NOT_AVAILABLE",
            "reason": "DGS10_not_available",
        }
    instruments = {
        series_id: _resistance_payload(rows)
        for series_id, rows in rate_series.items()
    }
    try:
        driver = decompose_yield_driver(
            nominal_10y_change_bp=_change_bp(rate_series["DGS10"]),
            two_year_change_bp=_change_bp(rate_series["DGS2"]),
            real_10y_change_bp=_change_bp(rate_series["DFII10"]),
            breakeven_10y_change_bp=_change_bp(rate_series["T10YIE"]),
            term_premium_change_bp=(
                _change_bp(bundle.term_premium_rows)
                if len(bundle.term_premium_rows) >= 2
                else None
            ),
        )
        driver_payload: dict[str, object] = asdict(driver)
    except ValueError as exc:
        driver_payload = {
            "dominant_driver": "NOT_AVAILABLE",
            "reason": f"driver_inputs_not_available:{exc}",
        }
    return {
        "publication_status": "LIMITED",
        "reason": "resistance_event_calibration_not_ready",
        "instruments": instruments,
        # Keep the primary instrument at the top level for compact readers.
        "DGS10": instruments["DGS10"],
        "driver_decomposition": driver_payload,
        "inflation_confirmation": {
            "status": "UNCONFIRMED",
            "reason": "prior_inflation_probability_not_available",
        },
        "term_premium_status": bundle.coverage.get(
            "term_premium_status", "NOT_AVAILABLE"
        ),
    }


def _rates_only_materialization(
    *,
    bundle: InflationPolicyDataBundle,
    config: InflationPolicyEngineConfig,
    reason: str,
) -> InflationPolicyMaterialization:
    """Return independent rate evidence while keeping core-dependent outputs closed."""

    try:
        freshness = _freshness_summary(bundle)
    except (TypeError, ValueError) as exc:
        return _not_available_materialization(
            bundle=bundle,
            config=config,
            reason=f"freshness_not_available:{exc}",
        )
    inflation = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    policy = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    rates = _build_rates_payload(bundle)
    reverse = {"publication_status": "NOT_AVAILABLE", "reason": reason}
    warnings = tuple(
        dict.fromkeys(
            (
                reason,
                *(
                    ("resistance_event_calibration_not_ready",)
                    if rates["publication_status"] == "LIMITED"
                    else ()
                ),
                "recession_model_not_available",
            )
        )
    )
    overall_status = (
        "LIMITED"
        if rates["publication_status"] in {"READY", "LIMITED"}
        else "NOT_AVAILABLE"
    )
    snapshot = {
        "as_of_at": bundle.as_of_at,
        "model_version": config.model_version,
        "run_kind": "historical_replay",
        "publication_status": overall_status,
        "inflation_json": inflation,
        "policy_json": policy,
        "rates_json": rates,
        "reverse_json": reverse,
        "evidence_json": {"coverage": bundle.coverage},
        "freshness_json": freshness,
        "warnings_json": warnings,
    }
    return InflationPolicyMaterialization(
        snapshot_row=snapshot,
        model_artifact_rows=(),
        inflation=inflation,
        policy=policy,
        rates=rates,
        reverse=reverse,
        warnings=warnings,
    )


def _serialize_core_forecast(
    forecast: CorePCEPathForecast,
    *,
    publication_status: str,
    publication_reason: str,
    state_definition: object,
) -> dict[str, object]:
    return {
        "publication_status": publication_status,
        "reason": publication_reason,
        "q4_quantiles_pct": forecast.q4_quantiles_pct,
        "state_probabilities": forecast.state_probabilities,
        "threshold_probabilities": forecast.threshold_probabilities,
        "monthly_mom_quantiles_pct": forecast.monthly_mom_quantiles_pct,
        "monthly_index_quantiles": forecast.monthly_index_quantiles,
        "component_weights": forecast.component_weights,
        "state_definition": asdict(state_definition),
    }


def materialize_inflation_policy_analysis(
    bundle: InflationPolicyDataBundle,
    *,
    config: InflationPolicyEngineConfig,
    sample_count: int,
    seed: int,
    core_artifact: CorePCEMomentumArtifact | CorePCEHybridArtifact | None = None,
) -> InflationPolicyMaterialization:
    """Build a compact current/replay payload while preserving each component gate."""

    if core_artifact is None:
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason="core_pce_pit_artifact_required",
        )
    if core_artifact.publication_status not in {"READY", "LIMITED"}:
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason=(
                "core_pce_artifact_not_publishable:"
                f"{core_artifact.publication_status}"
            ),
        )
    try:
        freshness = _freshness_summary(
            bundle,
            trained_through_date=core_artifact.trained_through_date,
            trained_cutoff_at=core_artifact.trained_cutoff_at,
        )
    except (TypeError, ValueError) as exc:
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason=f"freshness_not_available:{exc}",
        )
    levels = _core_level_rows(bundle.macro_rows)
    if not levels:
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason="core_pce_current_levels_missing",
        )
    latest_month = levels[-1][0]
    if latest_month != _month(core_artifact.trained_through_date):
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason="core_pce_artifact_bundle_month_mismatch",
        )
    forecast_months = _forecast_months(latest_month)
    if not forecast_months:
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason="core_pce_forecast_horizon_empty",
        )
    level_mapping = {month: value for month, _released, value in levels}
    try:
        state_definition = derive_state_definition(
            bundle.sep_rows,
            target_period=str(latest_month.year),
            forecast_error_pct=max(
                float(config.state_forecast_error_floor_pct),
                float(core_artifact.validation_metrics["rmse"]),
            ),
            price_stability_target_pct=config.price_stability_target_pct,
        )
        component_paths = {
            name: {month: value for month in forecast_months}
            for name, value in core_artifact.latest_component_mom_pct.items()
        }
        core_forecast = simulate_core_pce_paths(
            level_mapping,
            forecast_months=forecast_months,
            component_monthly_mom_pct=component_paths,
            component_weights=core_artifact.component_weights,
            residual_history_pct=core_artifact.predictive_residuals_pct,
            sample_count=sample_count,
            seed=seed,
            state_definition=state_definition,
            thresholds_pct=config.threshold_levels_pct,
        )
    except ValueError as exc:
        return _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason=f"inflation_path_not_available:{exc}",
        )
    inflation = _serialize_core_forecast(
        core_forecast,
        # The component artifact is validated one month ahead.  Until the
        # complete Q4/Q4 path has its own PIT rolling-origin evidence, its
        # longer-horizon probabilities must not inherit the component READY.
        publication_status="LIMITED",
        publication_reason="q4_path_rolling_origin_validation_not_ready",
        state_definition=state_definition,
    )

    policy: dict[str, object]
    policy_warnings: list[str] = []
    try:
        decision = _latest_decision(bundle.decision_rows)
        current_midpoint = (
            float(decision["target_lower_after_pct"])
            + float(decision["target_upper_after_pct"])
        ) / 2.0
        sep_prior = derive_sep_net_move_prior(
            bundle.sep_rows,
            target_period=str(latest_month.year),
            current_midpoint_pct=current_midpoint,
        )
        economic = project_inflation_states_to_policy(
            core_forecast.state_probabilities,
            reaction_matrix=config.reaction_matrix,
        )
        committee = derive_decision_action_prior(decision)
        policy_forecast = build_policy_path_forecast(
            current_midpoint_pct=current_midpoint,
            net_move_components={"sep": sep_prior, "economic": economic},
            net_move_weights=config.policy_component_weights,
            next_action_components={"committee": committee},
            next_action_weights=config.next_action_component_weights,
            max_component_weight=config.max_component_weight,
        )
        policy = {
            "publication_status": "LIMITED",
            "reason": "policy_rolling_origin_validation_not_ready",
            "next_meeting_probabilities": policy_forecast.next_meeting_probabilities,
            "net_move_probabilities": policy_forecast.net_move_probabilities,
            "year_end_target_probabilities": policy_forecast.year_end_target_probabilities,
            "sep_net_move_prior": sep_prior,
            "committee_vote_prior": committee,
        }
        policy_warnings.append("policy_rolling_origin_validation_not_ready")
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        policy = {
            "publication_status": "NOT_AVAILABLE",
            "reason": f"policy_not_available:{exc}",
        }
        policy_warnings.append("policy_not_available")

    rates = _build_rates_payload(bundle)
    reverse = {
        "publication_status": "NOT_AVAILABLE",
        "reason": "joint_rate_path_validation_not_ready",
    }
    warnings = tuple(
        dict.fromkeys(
            (
                *(core_artifact.publication_reasons or ()),
                "q4_path_rolling_origin_validation_not_ready",
                *policy_warnings,
                "resistance_event_calibration_not_ready",
                "recession_model_not_available",
            )
        )
    )
    overall_status = (
        "LIMITED"
        if inflation["publication_status"] in {"READY", "LIMITED"}
        else "NOT_AVAILABLE"
    )
    hybrid = isinstance(core_artifact, CorePCEHybridArtifact)
    artifact_parameters: dict[str, object] = {
        "component_weights": core_artifact.component_weights,
        "component_errors": core_artifact.component_errors,
        "latest_component_mom_pct": core_artifact.latest_component_mom_pct,
        "predictive_residuals_pct": core_artifact.predictive_residuals_pct,
    }
    if hybrid:
        artifact_parameters.update(
            {
                "feature_names": core_artifact.feature_names,
                "feature_means": core_artifact.feature_means,
                "feature_scales": core_artifact.feature_scales,
                "ridge_coefficients": core_artifact.ridge_coefficients,
                "ridge_alpha": core_artifact.ridge_alpha,
                "bridge_weights": core_artifact.bridge_weights,
                "latest_feature_values": core_artifact.latest_feature_values,
            }
        )
    artifact_row = {
        "model_version": config.model_version,
        "trained_cutoff_at": core_artifact.trained_cutoff_at,
        "component": "core_pce_hybrid" if hybrid else "core_pce_momentum",
        "feature_schema_version": (
            "core-pce-hybrid-features-v1" if hybrid else "core-pce-level-v1"
        ),
        "transform_schema_version": "mom-index-q4q4-v1",
        "state_schema_version": state_definition.definition_version,
        "training_start_date": core_artifact.training_start_date,
        "forecast_horizon": (
            "one_month_core_pce_nowcast" if hybrid else "one_month_momentum"
        ),
        "ensemble_weight": 1.0,
        "parameters_json": artifact_parameters,
        "validation_json": core_artifact.validation_metrics,
        "calibration_json": {
            "publication_status": core_artifact.publication_status,
        },
        "publication_status": core_artifact.publication_status,
        "publication_reasons_json": core_artifact.publication_reasons,
    }
    snapshot = {
        "as_of_at": bundle.as_of_at,
        "model_version": config.model_version,
        "run_kind": "historical_replay",
        "publication_status": overall_status,
        "inflation_json": inflation,
        "policy_json": policy,
        "rates_json": rates,
        "reverse_json": reverse,
        "evidence_json": {
            "coverage": bundle.coverage,
            "core_validation": core_artifact.validation_metrics,
        },
        "freshness_json": freshness,
        "warnings_json": warnings,
    }
    return InflationPolicyMaterialization(
        snapshot_row=snapshot,
        model_artifact_rows=(artifact_row,),
        inflation=inflation,
        policy=policy,
        rates=rates,
        reverse=reverse,
        warnings=warnings,
    )


def run_inflation_policy_materialization(
    *,
    as_of_at: str,
    history_start: str,
    config: InflationPolicyEngineConfig,
    run_kind: str,
    sample_count: int = 10_000,
    seed: int = 20260802,
    persist: bool = False,
    bundle_loader: Callable[..., InflationPolicyDataBundle] = (
        load_inflation_policy_data_bundle
    ),
    vintage_loader: Callable[..., Sequence[Mapping[str, object]]] = (
        load_inflation_policy_training_vintages
    ),
    artifact_trainer: Callable[..., CorePCEHybridArtifact] = (
        fit_core_pce_hybrid_artifact
    ),
    artifact_saver: Callable[[Mapping[str, object]], object] | None = None,
    snapshot_saver: Callable[[Mapping[str, object]], object] | None = None,
) -> InflationPolicyMaterialization:
    """Train from PIT vintages, materialize one cutoff, and optionally persist it."""

    if run_kind not in {"current", "historical_replay", "scenario"}:
        raise ValueError("run_kind must be current, historical_replay, or scenario")
    bundle = bundle_loader(as_of_at=as_of_at, history_start=history_start)
    vintages = vintage_loader(
        as_of_at=as_of_at,
        history_start=history_start,
        series_ids=CORE_PCE_MODEL_SERIES,
    )
    try:
        artifact = artifact_trainer(
            vintages,
            as_of_at=as_of_at,
            thresholds=config.core_validation_thresholds,
            minimum_training_rows=36,
            ridge_alpha=1.0,
            max_component_weight=min(0.60, float(config.max_component_weight)),
        )
    except (TypeError, ValueError) as exc:
        unavailable = _rates_only_materialization(
            bundle=bundle,
            config=config,
            reason=f"core_pce_hybrid_not_available:{exc}",
        )
        snapshot = {**unavailable.snapshot_row, "run_kind": run_kind}
        return InflationPolicyMaterialization(
            snapshot_row=snapshot,
            model_artifact_rows=(),
            inflation=unavailable.inflation,
            policy=unavailable.policy,
            rates=unavailable.rates,
            reverse=unavailable.reverse,
            warnings=unavailable.warnings,
        )
    result = materialize_inflation_policy_analysis(
        bundle,
        config=config,
        sample_count=sample_count,
        seed=seed,
        core_artifact=artifact,
    )
    snapshot = {**result.snapshot_row, "run_kind": run_kind}
    result = InflationPolicyMaterialization(
        snapshot_row=snapshot,
        model_artifact_rows=result.model_artifact_rows,
        inflation=result.inflation,
        policy=result.policy,
        rates=result.rates,
        reverse=result.reverse,
        warnings=result.warnings,
    )
    if (
        not persist
        or snapshot["publication_status"] not in {"READY", "LIMITED"}
        or not result.model_artifact_rows
    ):
        return result
    if artifact_saver is None or snapshot_saver is None:
        from finance.data.inflation_policy_results import (
            save_inflation_policy_model_artifact,
            save_inflation_policy_snapshot,
        )

        artifact_saver = artifact_saver or save_inflation_policy_model_artifact
        snapshot_saver = snapshot_saver or save_inflation_policy_snapshot
    for row in result.model_artifact_rows:
        if row["publication_status"] in {"READY", "LIMITED"}:
            artifact_saver(row)
    snapshot_saver(snapshot)
    return result


def _compact_cli_payload(
    result: InflationPolicyMaterialization,
) -> dict[str, object]:
    dgs10 = result.rates.get("DGS10")
    dgs10 = dgs10 if isinstance(dgs10, Mapping) else {}
    return {
        "as_of_at": result.snapshot_row.get("as_of_at"),
        "model_version": result.snapshot_row.get("model_version"),
        "publication_status": result.snapshot_row.get("publication_status"),
        "inflation": {
            "publication_status": result.inflation.get("publication_status"),
            "q4_quantiles_pct": result.inflation.get("q4_quantiles_pct"),
            "state_probabilities": result.inflation.get("state_probabilities"),
            "threshold_probabilities": result.inflation.get(
                "threshold_probabilities"
            ),
        },
        "policy": {
            "publication_status": result.policy.get("publication_status"),
            "next_meeting_probabilities": result.policy.get(
                "next_meeting_probabilities"
            ),
            "net_move_probabilities": result.policy.get("net_move_probabilities"),
        },
        "DGS10": {
            "current_value_pct": dgs10.get("current_value_pct"),
            "active_test_zone": dgs10.get("active_test_zone"),
            "next_overhead_zone": dgs10.get("next_overhead_zone"),
        },
        "reverse": result.reverse,
        "warnings": result.warnings,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Materialize the independent inflation-policy-yield analysis."
    )
    parser.add_argument("--as-of-at", required=True)
    parser.add_argument("--history-start", default="2015-01-01")
    parser.add_argument("--model-version", default="inflation-policy-hybrid-v1")
    parser.add_argument(
        "--run-kind",
        choices=("current", "historical_replay", "scenario"),
        default="current",
    )
    parser.add_argument(
        "--persist",
        action="store_true",
        help="Persist READY/LIMITED artifacts and snapshot; default is read-only.",
    )
    args = parser.parse_args(argv)
    result = run_inflation_policy_materialization(
        as_of_at=args.as_of_at,
        history_start=args.history_start,
        config=build_limited_reference_config(model_version=args.model_version),
        run_kind=args.run_kind,
        persist=bool(args.persist),
    )
    print(
        json.dumps(
            _compact_cli_payload(result),
            ensure_ascii=False,
            sort_keys=True,
            default=str,
        )
    )
    return 1 if result.snapshot_row.get("publication_status") == "FAILED" else 0


if __name__ == "__main__":  # pragma: no cover - exercised through main()
    raise SystemExit(main())
