"""Materialize independently gated inflation, policy, and resistance analysis."""

from __future__ import annotations

import argparse
import json
import math
from dataclasses import asdict, dataclass, field
from datetime import date, datetime, timezone
from typing import Callable, Mapping, Sequence

import numpy as np

from finance.core_pce_q4 import (
    CorePCEQ4Artifact,
    blend_q4_samples,
    fit_core_pce_q4_artifact,
    spf_probability_samples,
)

from finance.inflation_path import (
    CorePCEPathForecast,
    calculate_state_probabilities,
    calculate_threshold_probabilities,
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
from finance.inflation_policy_equity_stress import (
    EQUITY_RIDGE_ALPHA_CANDIDATES,
    EQUITY_PUBLICATION_CONTRACT_VERSION,
    EquityStressArtifact,
    EquityStressResult,
    build_equity_calibration_panel,
    build_equity_scenario_context,
    fit_equity_stress_model,
    simulate_equity_stress,
)
from finance.inflation_policy_recession import (
    RECESSION_COMPONENT,
    RECESSION_FEATURE_SCHEMA_VERSION,
    RECESSION_SERIES,
    RECESSION_VALIDATION_VERSION,
    RecessionRiskArtifact,
    RecessionRiskResult,
    build_recession_origin_panel,
    fit_recession_risk_model,
    predict_recession_risk,
)
from finance.inflation_policy_simulation import (
    JOINT_PATH_COMPONENT,
    RateTargetCondition,
    SimulationPath,
    calculate_target_probability,
    condition_paths_on_target,
    posterior_policy_hike_probability_for_next_pce,
)
from finance.joint_rate_paths import (
    JointRatePathArtifact,
    fit_joint_rate_path_artifact,
)
from finance.loaders.inflation_policy import (
    InflationPolicyDataBundle,
    InflationPolicyEquityBundle,
    load_inflation_policy_data_bundle,
    load_inflation_policy_equity_bundle,
    load_inflation_policy_model_artifact,
    load_inflation_policy_training_vintages,
)
from finance.policy_path import (
    POLICY_NET_MOVE_BUCKETS,
    build_policy_path_forecast,
    derive_decision_action_prior,
    derive_sep_net_move_prior,
    project_inflation_states_to_policy,
)
from finance.policy_validation import (
    PolicyPathArtifact,
    fit_policy_path_artifact,
    smooth_probability_row,
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
    q4_validation_thresholds: PublicationThresholds = PublicationThresholds(
        minimum_origins=20,
        minimum_complete_feature_ratio=0.80,
        maximum_calibration_error=0.35,
        require_baseline_improvement=True,
    )
    q4_minimum_target_years: int = 6


@dataclass(frozen=True)
class InflationPolicyMaterialization:
    snapshot_row: dict[str, object]
    model_artifact_rows: tuple[dict[str, object], ...]
    inflation: dict[str, object]
    policy: dict[str, object]
    rates: dict[str, object]
    reverse: dict[str, object]
    equity: dict[str, object]
    warnings: tuple[str, ...]
    recession: dict[str, object] = field(
        default_factory=lambda: {
            "publication_status": "NOT_AVAILABLE",
            "probability_12m": None,
            "risk_state": None,
            "risk_label": None,
            "horizon_months": 12,
            "top_drivers": (),
            "reason_codes": ("recession_model_not_available",),
            "validation_metrics": {},
        }
    )


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
    equity = _empty_equity_payload()
    recession = _empty_recession_payload()
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
        "equity_json": equity,
        "recession_json": recession,
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
        equity=equity,
        recession=recession,
        warnings=warnings,
    )


def _empty_equity_payload(
    reason: str = "verified_eps_vintages_or_joint_paths_not_available",
) -> dict[str, object]:
    """Return a typed, independently gated equity component payload."""

    return {
        "publication_status": "NOT_AVAILABLE",
        "reason": reason,
        "index_quantiles": {},
        "eps_quantiles": {},
        "multiple_quantiles": {},
        "threshold_probabilities": {},
        "target_decompositions": {},
        "measured_next_year_eps_revision_pct": None,
        "user_ai_eps_uplift_pct": 0.0,
        "scenario_kind": "MODEL_BASE",
        "current_index_level": None,
        "base_forward_eps": None,
        "scenario_feature_values": {},
    }


def _empty_recession_payload(
    reason: str = "recession_model_not_available",
) -> dict[str, object]:
    """Return the separately gated recession component without cycle fallback."""

    return {
        "publication_status": "NOT_AVAILABLE",
        "reason": reason,
        "probability_12m": None,
        "risk_state": None,
        "risk_label": None,
        "horizon_months": 12,
        "top_drivers": [],
        "validation_metrics": {},
    }


def _equity_payload_with_context(
    payload: Mapping[str, object], context: Mapping[str, object]
) -> dict[str, object]:
    """Attach snapshot-as-of inputs without mutating the model artifact identity."""

    return {
        **dict(payload),
        "as_of_at": context.get("as_of_at"),
        "current_index_level": context.get("current_index_level"),
        "base_forward_eps": context.get("base_forward_eps"),
        "measured_next_year_eps_revision_pct": context.get(
            "measured_next_year_eps_revision_pct"
        ),
        "scenario_feature_values": dict(
            context.get("scenario_feature_values") or {}
        ),
    }


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
    equity = _empty_equity_payload()
    recession = _empty_recession_payload()
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
        "equity_json": equity,
        "recession_json": recession,
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
        equity=equity,
        recession=recession,
        warnings=warnings,
    )


def _serialize_core_forecast(
    forecast: CorePCEPathForecast,
    *,
    publication_status: str,
    publication_reason: str,
    state_definition: object,
    validation: Mapping[str, object] | None = None,
    q4_component_weights: Mapping[str, object] | None = None,
    next_release_scenarios: Sequence[Mapping[str, object]] = (),
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
        "q4_component_weights": dict(q4_component_weights or {}),
        "validation": dict(validation or {}),
        "next_release_scenarios": [dict(row) for row in next_release_scenarios],
        "state_definition": asdict(state_definition),
    }


def _q4_quantiles(samples: Sequence[object]) -> dict[str, float]:
    points = np.quantile(
        np.asarray(tuple(float(item) for item in samples)),
        (0.05, 0.20, 0.50, 0.80, 0.95),
    )
    return {
        label: float(value)
        for label, value in zip(("p05", "p20", "p50", "p80", "p95"), points, strict=True)
    }


def _next_release_scenarios(
    *,
    levels: Mapping[object, object],
    forecast_months: Sequence[object],
    component_paths: Mapping[str, Mapping[object, object]],
    core_artifact: CorePCEMomentumArtifact | CorePCEHybridArtifact,
    q4_artifact: CorePCEQ4Artifact,
    spf_samples: Sequence[object],
    base_state_probabilities: Mapping[str, object],
    state_definition: object,
    sample_count: int,
    seed: int,
) -> list[dict[str, object]]:
    """Condition only the next print; later months retain empirical uncertainty."""

    if not forecast_months:
        return []
    base_reacceleration = float(base_state_probabilities.get("reacceleration") or 0.0) + float(
        base_state_probabilities.get("shock_reacceleration") or 0.0
    )
    rows: list[dict[str, object]] = []
    first_month = forecast_months[0]
    for mom_pct in (0.1, 0.2, 0.3, 0.4, 0.5):
        scenario_model = simulate_core_pce_paths(
            levels,
            forecast_months=forecast_months,
            component_monthly_mom_pct=component_paths,
            component_weights=core_artifact.component_weights,
            residual_history_pct=core_artifact.predictive_residuals_pct,
            fixed_monthly_mom_pct={first_month: mom_pct},
            sample_count=sample_count,
            seed=seed + int(mom_pct * 1_000),
            state_definition=state_definition,
            thresholds_pct=(),
        )
        pooled = blend_q4_samples(
            scenario_model.q4_samples_pct,
            spf_samples,
            model_weight=q4_artifact.model_weight,
            sample_count=sample_count,
        )
        probabilities = calculate_state_probabilities(pooled, state_definition)
        reacceleration = probabilities["reacceleration"] + probabilities[
            "shock_reacceleration"
        ]
        rows.append(
            {
                "mom_pct": mom_pct,
                "publication_status": "READY",
                "inflation_publication_status": "READY",
                "policy_publication_status": "LIMITED",
                "reacceleration_delta": reacceleration - base_reacceleration,
                "hike_delta": None,
                "q4_p50_pct": _q4_quantiles(pooled)["p50"],
                "reason": "inflation_path_validated_policy_path_pending",
            }
        )
    return rows


def materialize_inflation_policy_analysis(
    bundle: InflationPolicyDataBundle,
    *,
    config: InflationPolicyEngineConfig,
    sample_count: int,
    seed: int,
    core_artifact: CorePCEMomentumArtifact | CorePCEHybridArtifact | None = None,
    q4_artifact: CorePCEQ4Artifact | None = None,
    policy_artifact: PolicyPathArtifact | None = None,
    joint_path_builder: Callable[..., JointRatePathArtifact] | None = None,
    equity: Mapping[str, object] | EquityStressResult | None = None,
    equity_joint_paths_ready: bool = False,
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
    q4_weights: dict[str, float] = {}
    next_release_rows: list[dict[str, object]] = []
    if q4_artifact is not None and q4_artifact.publication_status in {"READY", "LIMITED"}:
        try:
            spf_samples, spf_released_at = spf_probability_samples(
                bundle.spf_rows,
                target_year=latest_month.year,
                sample_count=sample_count,
            )
            pooled_samples = blend_q4_samples(
                core_forecast.q4_samples_pct,
                spf_samples,
                model_weight=q4_artifact.model_weight,
                sample_count=sample_count,
            )
            q4_weights = {
                "monthly_model": q4_artifact.model_weight,
                "official_spf": q4_artifact.spf_weight,
            }
            core_forecast = CorePCEPathForecast(
                monthly_mom_quantiles_pct=core_forecast.monthly_mom_quantiles_pct,
                monthly_index_quantiles=core_forecast.monthly_index_quantiles,
                q4_quantiles_pct=_q4_quantiles(pooled_samples),
                q4_samples_pct=pooled_samples,
                state_probabilities=calculate_state_probabilities(
                    pooled_samples, state_definition
                ),
                threshold_probabilities=calculate_threshold_probabilities(
                    pooled_samples, config.threshold_levels_pct
                ),
                component_weights=core_forecast.component_weights,
                state_definition_version=core_forecast.state_definition_version,
            )
            next_release_rows = _next_release_scenarios(
                levels=level_mapping,
                forecast_months=forecast_months,
                component_paths=component_paths,
                core_artifact=core_artifact,
                q4_artifact=q4_artifact,
                spf_samples=spf_samples,
                base_state_probabilities=core_forecast.state_probabilities,
                state_definition=state_definition,
                sample_count=sample_count,
                seed=seed,
            )
            inflation_status = q4_artifact.publication_status
            inflation_reason = (
                "q4_direct_rolling_origin_validated"
                if inflation_status == "READY"
                else ",".join(q4_artifact.publication_reasons)
            )
            q4_validation = {
                **q4_artifact.validation_metrics,
                "official_spf_released_at": spf_released_at,
            }
        except (TypeError, ValueError) as exc:
            inflation_status = "NOT_AVAILABLE"
            inflation_reason = f"q4_linear_pool_not_available:{exc}"
            q4_validation = {}
    else:
        inflation_status = "LIMITED"
        inflation_reason = "q4_path_rolling_origin_validation_not_ready"
        q4_validation = {}
    inflation = _serialize_core_forecast(
        core_forecast,
        publication_status=inflation_status,
        publication_reason=inflation_reason,
        state_definition=state_definition,
        validation=q4_validation,
        q4_component_weights=q4_weights,
        next_release_scenarios=next_release_rows,
    )

    policy: dict[str, object]
    policy_warnings: list[str] = []
    current_policy_midpoint: float | None = None
    try:
        decision = _latest_decision(bundle.decision_rows)
        current_midpoint = (
            float(decision["target_lower_after_pct"])
            + float(decision["target_upper_after_pct"])
        ) / 2.0
        current_policy_midpoint = current_midpoint
        raw_sep_prior = derive_sep_net_move_prior(
            bundle.sep_rows,
            target_period=str(latest_month.year),
            current_midpoint_pct=current_midpoint,
        )
        raw_committee = derive_decision_action_prior(decision)
        if policy_artifact is not None:
            if _timestamp(policy_artifact.trained_cutoff_at) != _timestamp(
                core_artifact.trained_cutoff_at
            ):
                raise ValueError("policy artifact cutoff does not match core artifact")
            sep_prior = smooth_probability_row(
                raw_sep_prior,
                labels=POLICY_NET_MOVE_BUCKETS,
                smoothing=policy_artifact.year_end_smoothing,
            )
            committee = smooth_probability_row(
                raw_committee,
                labels=("cut", "hold", "hike"),
                smoothing=policy_artifact.next_meeting_smoothing,
            )
            policy_forecast = build_policy_path_forecast(
                current_midpoint_pct=current_midpoint,
                net_move_components={"sep": sep_prior},
                net_move_weights={"sep": 1.0},
                next_action_components={"committee": committee},
                next_action_weights={"committee": 1.0},
                max_component_weight=1.0,
            )
            policy_status = policy_artifact.publication_status
            policy_reason = (
                "policy_rolling_origin_validated"
                if policy_status == "READY"
                else ",".join(
                    policy_artifact.reason_codes
                    or ("policy_rolling_origin_validation_limited",)
                )
            )
            policy = {
                "publication_status": policy_status,
                "reason": policy_reason,
                "next_meeting_probabilities": policy_forecast.next_meeting_probabilities,
                "net_move_probabilities": policy_forecast.net_move_probabilities,
                "year_end_target_probabilities": policy_forecast.year_end_target_probabilities,
                "sep_net_move_prior": sep_prior,
                "committee_vote_prior": committee,
                "raw_sep_net_move_prior": raw_sep_prior,
                "raw_committee_vote_prior": raw_committee,
                "validation": {
                    "next_meeting": policy_artifact.next_meeting_validation,
                    "year_end": policy_artifact.year_end_validation,
                },
            }
            if policy_status != "READY":
                policy_warnings.extend(policy_artifact.reason_codes)
        else:
            economic = project_inflation_states_to_policy(
                core_forecast.state_probabilities,
                reaction_matrix=config.reaction_matrix,
            )
            policy_forecast = build_policy_path_forecast(
                current_midpoint_pct=current_midpoint,
                net_move_components={"sep": raw_sep_prior, "economic": economic},
                net_move_weights=config.policy_component_weights,
                next_action_components={"committee": raw_committee},
                next_action_weights=config.next_action_component_weights,
                max_component_weight=config.max_component_weight,
            )
            policy = {
                "publication_status": "LIMITED",
                "reason": "policy_rolling_origin_validation_not_ready",
                "next_meeting_probabilities": policy_forecast.next_meeting_probabilities,
                "net_move_probabilities": policy_forecast.net_move_probabilities,
                "year_end_target_probabilities": policy_forecast.year_end_target_probabilities,
                "sep_net_move_prior": raw_sep_prior,
                "committee_vote_prior": raw_committee,
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
    joint_artifact: JointRatePathArtifact | None = None
    joint_warnings: list[str] = []
    if (
        joint_path_builder is not None
        and inflation.get("publication_status") == "READY"
        and policy.get("publication_status") == "READY"
        and current_policy_midpoint is not None
    ):
        try:
            joint_artifact = joint_path_builder(
                macro_rows=bundle.macro_rows,
                q4_samples_pct=core_forecast.q4_samples_pct,
                policy_net_move_probabilities=policy["net_move_probabilities"],
                levels=level_mapping,
                forecast_months=forecast_months,
                current_policy_midpoint_pct=current_policy_midpoint,
                as_of_at=bundle.as_of_at,
                sample_count=min(2_000, int(sample_count)),
                seed=seed,
            )
            if _timestamp(joint_artifact.trained_cutoff_at) != _timestamp(
                core_artifact.trained_cutoff_at
            ):
                raise ValueError("joint artifact cutoff does not match core artifact")
            if joint_artifact.publication_status == "READY" and joint_artifact.paths:
                joint_paths = joint_artifact.paths
                total_weight = sum(float(path.weight) for path in joint_paths)
                base_hike = sum(
                    float(path.weight)
                    for path in joint_paths
                    if int(path.policy_net_steps) > 0
                ) / total_weight
                for row in next_release_rows:
                    observed_mom = float(row["mom_pct"])
                    row["policy_publication_status"] = "READY"
                    row["publication_status"] = "READY"
                    row["hike_delta"] = (
                        posterior_policy_hike_probability_for_next_pce(
                            joint_paths,
                            observed_mom_pct=observed_mom,
                            observation_noise_pct=0.08,
                        )
                        - base_hike
                    )
                    row["reason"] = "joint_policy_path_reweighted"
                inflation["next_release_scenarios"] = next_release_rows

                dgs10 = rates.get("DGS10")
                if isinstance(dgs10, Mapping):
                    zones = dgs10.get("zones")
                    if isinstance(zones, list):
                        for zone in zones:
                            if not isinstance(zone, dict):
                                continue
                            target = RateTargetCondition(
                                instrument="DGS10",
                                zone_lower_pct=float(zone["zone_lower_pct"]),
                                zone_upper_pct=float(zone["zone_upper_pct"]),
                                condition="BREAK",
                                buffer_pct=float(zone.get("tolerance_pct") or 0.0),
                                hold_days=3,
                            )
                            zone["breakout_probability"] = calculate_target_probability(
                                joint_paths, target
                            )
                    selected_zone = dgs10.get("next_overhead_zone") or dgs10.get(
                        "active_test_zone"
                    )
                    if isinstance(selected_zone, dict):
                        selected_breakout_target = RateTargetCondition(
                            instrument="DGS10",
                            zone_lower_pct=float(selected_zone["zone_lower_pct"]),
                            zone_upper_pct=float(selected_zone["zone_upper_pct"]),
                            condition="BREAK",
                            buffer_pct=float(
                                selected_zone.get("tolerance_pct") or 0.0
                            ),
                            hold_days=3,
                        )
                        # The selected zone is a copy of the canonical zone row.
                        # Publish its probability too so the UI does not lose the
                        # validated result while rendering the selected summary.
                        selected_zone["breakout_probability"] = (
                            calculate_target_probability(
                                joint_paths, selected_breakout_target
                            )
                        )
                        reverse_target = RateTargetCondition(
                            instrument="DGS10",
                            zone_lower_pct=float(selected_zone["zone_lower_pct"]),
                            zone_upper_pct=float(selected_zone["zone_upper_pct"]),
                            condition="REACH",
                            buffer_pct=float(
                                selected_zone.get("tolerance_pct") or 0.0
                            ),
                            hold_days=3,
                        )
                        summary = condition_paths_on_target(
                            joint_paths,
                            reverse_target,
                            minimum_supporting_paths=max(
                                1,
                                int(
                                    joint_artifact.validation_metrics.get(
                                        "reverse_minimum_supporting_paths"
                                    )
                                    or 20
                                ),
                            ),
                            minimum_effective_paths=max(
                                1.0,
                                float(
                                    joint_artifact.validation_metrics.get(
                                        "reverse_minimum_effective_paths"
                                    )
                                    or 10.0
                                ),
                            ),
                        )
                        reverse = {
                            **asdict(summary),
                            "publication_status": (
                                "READY"
                                if summary.status == "AVAILABLE"
                                else "NOT_AVAILABLE"
                            ),
                            "reason": (
                                "dynamic_resistance_joint_paths_ready"
                                if summary.status == "AVAILABLE"
                                else "dynamic_resistance_path_support_too_small"
                            ),
                            "target": {
                                "instrument": "DGS10",
                                "zone_lower_pct": reverse_target.zone_lower_pct,
                                "zone_upper_pct": reverse_target.zone_upper_pct,
                                "condition": "REACH",
                            },
                        }
                rates = {
                    **rates,
                    "publication_status": "READY",
                    "reason": "joint_rate_path_chronological_validation_ready",
                    "joint_path_validation": joint_artifact.validation_metrics,
                }
            else:
                joint_warnings.extend(
                    joint_artifact.reason_codes
                    or ("joint_rate_path_validation_not_ready",)
                )
        except (KeyError, TypeError, ValueError) as exc:
            joint_artifact = None
            joint_warnings.append(f"joint_rate_path_not_available:{exc}")
    if isinstance(equity, EquityStressResult):
        equity_payload = asdict(equity)
    elif equity is not None:
        equity_payload = dict(equity)
    else:
        equity_payload = _empty_equity_payload()
    if (
        str(equity_payload.get("publication_status") or "") in {"READY", "LIMITED"}
        and not equity_joint_paths_ready
    ):
        equity_payload = _equity_payload_with_context(
            _empty_equity_payload("joint_rate_paths_not_available"),
            equity_payload,
        )
    warnings = tuple(
        dict.fromkeys(
            (
                *(core_artifact.publication_reasons or ()),
                *(
                    ()
                    if inflation["publication_status"] == "READY"
                    else (str(inflation.get("reason") or "q4_path_not_ready"),)
                ),
                *policy_warnings,
                *(
                    ()
                    if joint_artifact is not None
                    and joint_artifact.publication_status == "READY"
                    else ("resistance_event_calibration_not_ready",)
                ),
                *joint_warnings,
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
    q4_artifact_row: dict[str, object] | None = None
    if q4_artifact is not None:
        q4_artifact_row = {
            "model_version": config.model_version,
            "trained_cutoff_at": q4_artifact.trained_cutoff_at,
            "component": "core_pce_q4_linear_pool",
            "feature_schema_version": "core-pce-q4-pit-origins-v1",
            "transform_schema_version": "spf-monthly-linear-pool-v1",
            "state_schema_version": state_definition.definition_version,
            "training_start_date": q4_artifact.training_start_date,
            "forecast_horizon": "calendar_year_q4_over_q4",
            "ensemble_weight": q4_artifact.model_weight,
            "parameters_json": {
                "monthly_model_weight": q4_artifact.model_weight,
                "official_spf_weight": q4_artifact.spf_weight,
            },
            "validation_json": q4_artifact.validation_metrics,
            "calibration_json": {
                "publication_status": q4_artifact.publication_status,
            },
            "publication_status": q4_artifact.publication_status,
            "publication_reasons_json": q4_artifact.publication_reasons,
        }
    policy_artifact_row: dict[str, object] | None = None
    if policy_artifact is not None:
        policy_artifact_row = {
            "model_version": config.model_version,
            "trained_cutoff_at": policy_artifact.trained_cutoff_at,
            "component": "policy_path",
            "feature_schema_version": "fomc-sep-vote-marginals-v1",
            "transform_schema_version": "chronological-probability-smoothing-v1",
            "state_schema_version": "policy-next-year-end-v1",
            "training_start_date": policy_artifact.training_start_decision_date,
            "forecast_horizon": "next_fomc_and_calendar_year_end",
            "ensemble_weight": 1.0,
            "parameters_json": {
                "next_meeting_smoothing": policy_artifact.next_meeting_smoothing,
                "year_end_smoothing": policy_artifact.year_end_smoothing,
            },
            "validation_json": {
                "next_meeting": policy_artifact.next_meeting_validation,
                "year_end": policy_artifact.year_end_validation,
                "trained_through_decision_date": (
                    policy_artifact.trained_through_decision_date
                ),
            },
            "calibration_json": {
                "publication_status": policy_artifact.publication_status,
            },
            "publication_status": policy_artifact.publication_status,
            "publication_reasons_json": policy_artifact.reason_codes,
        }
    joint_artifact_row: dict[str, object] | None = None
    if joint_artifact is not None:
        joint_artifact_row = {
            "model_version": config.model_version,
            "trained_cutoff_at": joint_artifact.trained_cutoff_at,
            "component": JOINT_PATH_COMPONENT,
            "feature_schema_version": "rate-episode-rank-copula-v1",
            "transform_schema_version": "year-end-empirical-path-v1",
            "state_schema_version": "joint-inflation-policy-rate-v1",
            "training_start_date": joint_artifact.training_start_date,
            "forecast_horizon": "calendar_year_end_joint_paths",
            "ensemble_weight": 1.0,
            "parameters_json": {
                "rate_scales": joint_artifact.rate_scales,
                "joint_rate_paths": [asdict(path) for path in joint_artifact.paths],
            },
            "validation_json": joint_artifact.validation_metrics,
            "calibration_json": {
                "publication_status": joint_artifact.publication_status,
            },
            "publication_status": joint_artifact.publication_status,
            "publication_reasons_json": joint_artifact.reason_codes,
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
        "equity_json": equity_payload,
        "recession_json": _empty_recession_payload(),
        "evidence_json": {
            "coverage": bundle.coverage,
            "core_validation": core_artifact.validation_metrics,
            "q4_validation": (
                q4_artifact.validation_metrics if q4_artifact is not None else {}
            ),
            "policy_validation": (
                {
                    "next_meeting": policy_artifact.next_meeting_validation,
                    "year_end": policy_artifact.year_end_validation,
                }
                if policy_artifact is not None
                else {}
            ),
            "joint_path_validation": (
                joint_artifact.validation_metrics
                if joint_artifact is not None
                else {}
            ),
        },
        "freshness_json": freshness,
        "warnings_json": warnings,
    }
    return InflationPolicyMaterialization(
        snapshot_row=snapshot,
        model_artifact_rows=(artifact_row,)
        + ((q4_artifact_row,) if q4_artifact_row is not None else ())
        + ((policy_artifact_row,) if policy_artifact_row is not None else ())
        + ((joint_artifact_row,) if joint_artifact_row is not None else ()),
        inflation=inflation,
        policy=policy,
        rates=rates,
        reverse=reverse,
        equity=equity_payload,
        recession=_empty_recession_payload(),
        warnings=warnings,
    )


def _decoded_object(value: object, *, field: str) -> dict[str, object]:
    try:
        decoded = json.loads(value) if isinstance(value, str) else value
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field} must be valid JSON") from exc
    if not isinstance(decoded, Mapping):
        raise ValueError(f"{field} must be an object")
    return {str(key): item for key, item in decoded.items()}


def _validated_joint_paths(
    artifact: Mapping[str, object] | None,
) -> tuple[SimulationPath, ...]:
    """Deserialize paths only when their own publication contract is READY."""

    if artifact is None or str(artifact.get("publication_status") or "") != "READY":
        return ()
    validation = _decoded_object(
        artifact.get("validation_json"), field="joint path validation_json"
    )
    if str(validation.get("joint_path_publication_status") or "") != "READY":
        return ()
    parameters = _decoded_object(
        artifact.get("parameters_json"), field="joint path parameters_json"
    )
    raw_paths = parameters.get("joint_rate_paths")
    if not isinstance(raw_paths, Sequence) or isinstance(raw_paths, (str, bytes)):
        return ()
    paths: list[SimulationPath] = []
    for index, raw in enumerate(raw_paths[:50_000]):
        if not isinstance(raw, Mapping):
            raise ValueError(f"joint_rate_paths[{index}] must be an object")
        rate_paths = _decoded_object(
            raw.get("rate_paths_pct"),
            field=f"joint_rate_paths[{index}].rate_paths_pct",
        )
        paths.append(
            SimulationPath(
                path_id=str(raw.get("path_id") or f"path-{index}"),
                weight=_finite(raw.get("weight"), field="joint path weight"),
                q4_core_pce_pct=_finite(
                    raw.get("q4_core_pce_pct"), field="joint path Core PCE"
                ),
                remaining_monthly_mom_pct=tuple(
                    _finite(item, field="joint path remaining PCE")
                    for item in (raw.get("remaining_monthly_mom_pct") or ())
                ),
                policy_net_steps=int(raw.get("policy_net_steps") or 0),
                year_end_policy_midpoint_pct=_finite(
                    raw.get("year_end_policy_midpoint_pct"),
                    field="joint path policy midpoint",
                ),
                rate_paths_pct={
                    str(instrument): tuple(
                        _finite(item, field=f"{instrument} joint path")
                        for item in values
                    )
                    for instrument, values in rate_paths.items()
                    if isinstance(values, Sequence)
                    and not isinstance(values, (str, bytes))
                },
            )
        )
    return tuple(paths)


def _equity_artifact_row(
    artifact: EquityStressArtifact,
    *,
    model_version: str,
    trained_cutoff_at: str,
) -> dict[str, object]:
    training_start = artifact.validation_metrics.get("training_start_date")
    if not training_start:
        raise ValueError("equity artifact training_start_date is required")
    artifact_payload = asdict(artifact)
    # Model artifacts are immutable for a training cutoff. Live market context is
    # snapshot-as-of state and must never be UPSERTed into this identity.
    artifact_payload["latest_measured_next_year_eps_revision_pct"] = None
    artifact_payload["scenario_feature_values"] = {}
    return {
        "model_version": str(model_version),
        "trained_cutoff_at": str(trained_cutoff_at),
        "component": "equity_stress",
        "feature_schema_version": "equity-year-end-path-features-v2",
        "transform_schema_version": "next-year-eps-forward-multiple-v2",
        "state_schema_version": "equity-conditional-stress-v1",
        "training_start_date": str(training_start),
        "forecast_horizon": "calendar_year_end",
        "ensemble_weight": 1.0,
        "parameters_json": {"artifact": artifact_payload},
        "validation_json": artifact.validation_metrics,
        "calibration_json": {
            "publication_status": artifact.publication_status,
            "publication_contract_version": artifact.validation_metrics.get(
                "publication_contract_version"
            ),
            "maximum_coverage_80_error": artifact.validation_metrics.get(
                "maximum_coverage_80_error"
            ),
        },
        "publication_status": artifact.publication_status,
        "publication_reasons_json": artifact.reason_codes,
    }


def _recession_artifact_row(
    artifact: RecessionRiskArtifact,
    *,
    model_version: str,
    trained_cutoff_at: str,
) -> dict[str, object]:
    """Serialize only immutable independent recession model state."""

    if not artifact.trained_through:
        raise ValueError("recession artifact trained_through is required")
    return {
        "model_version": model_version,
        "trained_cutoff_at": trained_cutoff_at,
        "component": RECESSION_COMPONENT,
        "feature_schema_version": RECESSION_FEATURE_SCHEMA_VERSION,
        "transform_schema_version": RECESSION_VALIDATION_VERSION,
        "state_schema_version": "recession-risk-five-band-v1",
        "training_start_date": artifact.validation_metrics.get("training_start_date")
        or artifact.trained_through,
        "forecast_horizon": "recession_within_12_months",
        "ensemble_weight": 1.0,
        "parameters_json": {
            "feature_names": artifact.feature_names,
            "feature_means": artifact.feature_means,
            "feature_scales": artifact.feature_scales,
            "coefficients": artifact.coefficients,
            "intercept": artifact.intercept,
            "forecast_horizon_months": artifact.forecast_horizon_months,
        },
        "validation_json": artifact.validation_metrics,
        "calibration_json": {
            "publication_status": artifact.publication_status,
            "validation_scheme": RECESSION_VALIDATION_VERSION,
        },
        "publication_status": artifact.publication_status,
        "publication_reasons_json": artifact.reason_codes,
    }


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
    recession_vintage_loader: Callable[..., Sequence[Mapping[str, object]]] | None = None,
    recession_panel_builder: Callable[..., object] = build_recession_origin_panel,
    recession_artifact_trainer: Callable[..., RecessionRiskArtifact] = (
        fit_recession_risk_model
    ),
    recession_predictor: Callable[..., RecessionRiskResult] = predict_recession_risk,
    artifact_trainer: Callable[..., CorePCEHybridArtifact] = (
        fit_core_pce_hybrid_artifact
    ),
    q4_artifact_trainer: Callable[..., CorePCEQ4Artifact] = (
        fit_core_pce_q4_artifact
    ),
    policy_artifact_trainer: Callable[..., PolicyPathArtifact] = (
        fit_policy_path_artifact
    ),
    joint_path_builder: Callable[..., JointRatePathArtifact] = (
        fit_joint_rate_path_artifact
    ),
    equity_bundle_loader: Callable[..., InflationPolicyEquityBundle] = (
        load_inflation_policy_equity_bundle
    ),
    equity_panel_builder: Callable[..., object] = build_equity_calibration_panel,
    equity_artifact_trainer: Callable[..., EquityStressArtifact] = (
        fit_equity_stress_model
    ),
    joint_path_artifact_loader: Callable[..., Mapping[str, object] | None] = (
        load_inflation_policy_model_artifact
    ),
    equity_scenario_runner: Callable[..., EquityStressResult] = simulate_equity_stress,
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
            equity=unavailable.equity,
            recession=unavailable.recession,
            warnings=unavailable.warnings,
        )
    q4_artifact: CorePCEQ4Artifact | None = None
    try:
        q4_artifact = q4_artifact_trainer(
            vintages,
            bundle.spf_rows,
            as_of_at=as_of_at,
            thresholds=config.q4_validation_thresholds,
            minimum_target_years=config.q4_minimum_target_years,
            sample_count=min(400, int(sample_count)),
            minimum_training_rows=36,
        )
    except (TypeError, ValueError, np.linalg.LinAlgError):
        q4_artifact = None
    policy_artifact: PolicyPathArtifact | None = None
    try:
        policy_artifact = policy_artifact_trainer(
            bundle.decision_rows,
            bundle.sep_rows,
            as_of_at=as_of_at,
        )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError):
        policy_artifact = None
    recession_payload: dict[str, object] = _empty_recession_payload()
    recession_artifact_row: dict[str, object] | None = None
    recession_enabled = (
        recession_vintage_loader is not None
        or vintage_loader is load_inflation_policy_training_vintages
    )
    if recession_enabled:
        resolved_recession_loader = (
            recession_vintage_loader or load_inflation_policy_training_vintages
        )
        try:
            recession_rows = resolved_recession_loader(
                as_of_at=as_of_at,
                history_start=min(str(history_start), "1988-01-01"),
                series_ids=RECESSION_SERIES,
            )
            recession_panel = recession_panel_builder(
                recession_rows,
                recession_rows,
                as_of_at=as_of_at,
            )
            recession_artifact = recession_artifact_trainer(
                recession_panel,
                as_of_at=as_of_at,
                model_version=config.model_version,
                minimum_origins=100,
                minimum_training_rows=40,
                minimum_complete_feature_ratio=0.60,
                maximum_calibration_error=0.15,
                ridge_alpha=50.0,
            )
            recession_result = recession_predictor(
                recession_artifact, as_of_at=as_of_at
            )
            recession_payload = asdict(recession_result)
            recession_payload["reason"] = (
                "independent_pit_recession_validation_ready"
                if recession_result.publication_status == "READY"
                else ",".join(recession_result.reason_codes)
                or "recession_model_not_available"
            )
            if recession_artifact.publication_status in {"READY", "LIMITED"}:
                recession_artifact_row = _recession_artifact_row(
                    recession_artifact,
                    model_version=config.model_version,
                    trained_cutoff_at=artifact.trained_cutoff_at,
                )
        except (KeyError, TypeError, ValueError, np.linalg.LinAlgError) as exc:
            recession_payload = _empty_recession_payload(
                f"recession_component_exception:{exc}"
            )
    equity_payload: Mapping[str, object] | EquityStressResult | None = None
    equity_artifact_row: dict[str, object] | None = None
    equity_context: Mapping[str, object] | None = None
    equity_joint_paths_ready = False
    try:
        equity_bundle = equity_bundle_loader(
            as_of_at=as_of_at, history_start=history_start
        )
        required_coverage = (
            "verified_eps_vintage_status",
            "sp500_price_status",
            "yield_status",
        )
        missing_coverage = [
            field
            for field in required_coverage
            if str(equity_bundle.coverage.get(field) or "") != "READY"
        ]
        if missing_coverage:
            equity_payload = _empty_equity_payload(
                "verified_eps_vintages_or_joint_paths_not_available"
            )
        else:
            equity_panel = equity_panel_builder(
                price_rows=equity_bundle.price_rows,
                eps_rows=equity_bundle.eps_rows,
                yield_rows=equity_bundle.yield_rows,
                as_of_at=equity_bundle.as_of_at,
            )
            equity_context = build_equity_scenario_context(
                equity_panel, as_of_at=equity_bundle.as_of_at
            )
            equity_artifact = equity_artifact_trainer(
                equity_panel,
                minimum_origins=60,
                ridge_alpha=1.0,
                ridge_alpha_candidates=EQUITY_RIDGE_ALPHA_CANDIDATES,
                model_version=config.model_version,
            )
            contract_version = str(
                equity_artifact.validation_metrics.get(
                    "publication_contract_version"
                )
                or ""
            )
            if (
                equity_artifact.publication_status in {"READY", "LIMITED"}
                and contract_version == EQUITY_PUBLICATION_CONTRACT_VERSION
            ):
                equity_artifact_row = _equity_artifact_row(
                    equity_artifact,
                    model_version=config.model_version,
                    trained_cutoff_at=artifact.trained_cutoff_at,
                )
                joint_artifact = joint_path_artifact_loader(
                    model_version=config.model_version,
                    trained_cutoff_at=artifact.trained_cutoff_at,
                    component=JOINT_PATH_COMPONENT,
                )
                joint_paths = _validated_joint_paths(joint_artifact)
                if joint_paths:
                    equity_payload = equity_scenario_runner(
                        equity_artifact,
                        joint_paths,
                        current_index=equity_context["current_index_level"],
                        forward_eps=equity_context["base_forward_eps"],
                        scenario_feature_values=equity_context[
                            "scenario_feature_values"
                        ],
                        measured_next_year_eps_revision_pct=equity_context[
                            "measured_next_year_eps_revision_pct"
                        ],
                        as_of_at=str(equity_context["as_of_at"]),
                    )
                    equity_joint_paths_ready = True
                else:
                    equity_payload = _equity_payload_with_context(
                        _empty_equity_payload("joint_rate_paths_not_available"),
                        equity_context,
                    )
            else:
                equity_payload = _equity_payload_with_context(
                    _empty_equity_payload(
                        "equity_model_not_publishable:"
                        + ",".join(
                            equity_artifact.reason_codes
                            or ("publication_contract_mismatch",)
                        )
                    ),
                    equity_context,
                )
    except (KeyError, TypeError, ValueError, json.JSONDecodeError) as exc:
        equity_payload = {
            **(
                _equity_payload_with_context(
                    _empty_equity_payload(f"equity_component_exception:{exc}"),
                    equity_context,
                )
                if equity_context is not None
                else _empty_equity_payload(f"equity_component_exception:{exc}")
            ),
            "publication_status": "FAILED",
        }

    result = materialize_inflation_policy_analysis(
        bundle,
        config=config,
        sample_count=sample_count,
        seed=seed,
        core_artifact=artifact,
        q4_artifact=q4_artifact,
        policy_artifact=policy_artifact,
        joint_path_builder=joint_path_builder,
        equity=equity_payload,
        equity_joint_paths_ready=equity_joint_paths_ready,
    )
    warnings = tuple(
        dict.fromkeys(
            (
                *(item for item in result.warnings if item != "recession_model_not_available"),
                *(
                    ()
                    if recession_payload.get("publication_status") == "READY"
                    else (
                        str(
                            recession_payload.get("reason")
                            or "recession_model_not_available"
                        ),
                    )
                ),
            )
        )
    )
    all_components_ready = all(
        str(component.get("publication_status") or "") == "READY"
        for component in (
            result.inflation,
            result.policy,
            result.rates,
            result.reverse,
            result.equity,
            recession_payload,
        )
    )
    snapshot = {
        **result.snapshot_row,
        "run_kind": run_kind,
        "publication_status": "READY" if all_components_ready else result.snapshot_row["publication_status"],
        "recession_json": recession_payload,
        "warnings_json": warnings,
    }
    has_publishable_core_identity = any(
        str(row.get("component") or "")
        in {"core_pce_hybrid", "core_pce_momentum"}
        for row in result.model_artifact_rows
    )
    # Equity shares the snapshot's model/cutoff identity. Do not persist an
    # otherwise valid equity fit under a failed or temporally invalid core run.
    artifact_rows = result.model_artifact_rows + (
        (equity_artifact_row,)
        if equity_artifact_row is not None and has_publishable_core_identity
        else ()
    ) + (
        (recession_artifact_row,)
        if recession_artifact_row is not None and has_publishable_core_identity
        else ()
    )
    result = InflationPolicyMaterialization(
        snapshot_row=snapshot,
        model_artifact_rows=artifact_rows,
        inflation=result.inflation,
        policy=result.policy,
        rates=result.rates,
        reverse=result.reverse,
        equity=result.equity,
        recession=recession_payload,
        warnings=warnings,
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
        "equity": result.equity,
        "recession": result.recession,
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
