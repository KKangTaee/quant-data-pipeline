"""Publish only validated current-state transition forecasts for Overview."""

from __future__ import annotations

import json
import math
from dataclasses import dataclass, replace
from datetime import date
from typing import Any, Callable, Mapping, Sequence

import numpy as np
import pandas as pd

from finance.data.economic_cycle_results import (
    upsert_cycle_model_artifact,
    upsert_cycle_snapshots,
)
from finance.economic_cycle_observed_state import PHASE_SEQUENCE
from finance.economic_cycle_state_transition_experiment import (
    DriverStageResult,
    StateStageResult,
    StateTransitionFeasibilityReport,
    _build_driver_stage,
    _build_state_stage,
    _normalized_cutoff,
    run_state_transition_feasibility,
)
from finance.economic_cycle_transition_dataset import TransitionDataset
from finance.economic_cycle_transition_drivers import REQUIRED_DRIVER_FEATURES
from finance.economic_cycle_transition_model import (
    TransitionModelArtifact,
    fit_binary_logit,
    fit_multiclass_temperature,
    fit_multinomial_logit,
    fit_platt_scaler,
    predict_binary_probability,
    predict_destination_probabilities,
)
from finance.economic_cycle_transition_validation import select_transition_l2
from finance.loaders.economic_cycle import load_cycle_snapshot


TRANSITION_MODEL_VERSION = "economic_cycle_transition_v1"
TRANSITION_FEATURE_SCHEMA_VERSION = "transition_forecast_features_v1"
TRANSITION_FORECAST_CONTRACT_VERSION = "transition_forecast_v1"


@dataclass(frozen=True)
class TransitionProductionForecast:
    """Serializable artifact, current forecast, and observed-state handoff."""

    as_of_date: str
    observed_state: dict[str, object]
    recent_changes: tuple[dict[str, object], ...]
    monitor: dict[str, object]
    artifacts: dict[str, dict[str, object]]


def _json_safe(value: Any) -> Any:
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (tuple, list)):
        return [_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, np.generic):
        return value.item()
    if isinstance(value, float) and not math.isfinite(value):
        return None
    return value


def _canonical_json(value: object) -> str:
    return json.dumps(
        _json_safe(value),
        ensure_ascii=False,
        sort_keys=True,
        separators=(",", ":"),
    )


def _current_row(dataset: TransitionDataset, cutoff: pd.Timestamp) -> pd.DataFrame:
    origins = pd.to_datetime(dataset.rows["forecast_origin"], errors="coerce")
    selected = dataset.rows.loc[
        dataset.rows["eligible"].astype(bool) & (origins == cutoff)
    ].tail(1)
    if selected.empty:
        raise ValueError("CURRENT_TRANSITION_FEATURES_UNAVAILABLE")
    return selected.copy()


def _known_training_rows(
    dataset: TransitionDataset,
    cutoff: pd.Timestamp,
    *,
    target_column: str,
    known_at_column: str,
) -> pd.DataFrame:
    known_at = pd.to_datetime(dataset.rows[known_at_column], errors="coerce")
    origins = pd.to_datetime(dataset.rows["forecast_origin"], errors="coerce")
    selected = dataset.rows.loc[
        dataset.rows["eligible"].astype(bool)
        & dataset.rows[target_column].notna()
        & known_at.notna()
        & (known_at <= cutoff)
        & (origins < cutoff)
    ].copy()
    if selected.empty:
        raise ValueError(f"{target_column.upper()}_TRAINING_UNAVAILABLE")
    return selected


def _calibrate_pressure(
    artifact: TransitionModelArtifact,
    validation: object,
) -> TransitionModelArtifact:
    records = tuple(getattr(validation, "pressure_predictions", ()) or ())
    if not records:
        return artifact
    return replace(
        artifact,
        calibration=fit_platt_scaler(
            [float(item.model_probabilities["transition"]) for item in records],
            [float(item.actual) for item in records],
            [float(item.weight) for item in records],
        ),
    )


def _calibrate_destination(
    artifact: TransitionModelArtifact,
    validation: object,
) -> TransitionModelArtifact:
    records = tuple(getattr(validation, "destination_predictions", ()) or ())
    if not records:
        return artifact
    class_index = {phase: index for index, phase in enumerate(PHASE_SEQUENCE)}
    probabilities = np.asarray(
        [
            [float(item.model_probabilities[phase]) for phase in PHASE_SEQUENCE]
            for item in records
        ],
        dtype=float,
    )
    return replace(
        artifact,
        calibration=fit_multiclass_temperature(
            probabilities,
            [class_index[str(item.actual)] for item in records],
            [float(item.weight) for item in records],
        ),
    )


def _pressure_level(probability: float) -> str:
    if probability < 0.35:
        return "LOW"
    if probability < 0.55:
        return "NORMAL"
    if probability < 0.70:
        return "ELEVATED"
    return "HIGH"


def _pressure_percentile(
    artifact: TransitionModelArtifact,
    dataset: TransitionDataset,
    current_probability: float,
    cutoff: pd.Timestamp,
) -> float:
    origins = pd.to_datetime(dataset.rows["forecast_origin"], errors="coerce")
    history = dataset.rows.loc[
        dataset.rows["eligible"].astype(bool) & (origins < cutoff)
    ]
    if history.empty:
        return 0.5
    historical = predict_binary_probability(artifact, history)
    return float(np.mean(historical <= current_probability))


def _driver_rows(
    artifact: TransitionModelArtifact,
    current: pd.DataFrame,
) -> list[dict[str, object]]:
    output: list[dict[str, object]] = []
    row = current.iloc[0]
    coefficients = artifact.coefficients["transition"]
    visible_features = (
        "level",
        "momentum",
        "phase_duration",
        "positive_breadth",
        *REQUIRED_DRIVER_FEATURES,
    )
    for feature in visible_features:
        value = float(row[feature])
        standardized = (value - artifact.means[feature]) / artifact.scales[feature]
        coefficient = float(coefficients[feature])
        contribution = coefficient * standardized
        output.append(
            {
                "driver_id": feature,
                "signal_group": (
                    "DRIVER" if feature in REQUIRED_DRIVER_FEATURES else "CORE"
                ),
                "value": value,
                "standardized_value": standardized,
                "contribution": contribution,
                "current_effect": (
                    "RAISES_PRESSURE"
                    if contribution > 0.05
                    else "LOWERS_PRESSURE"
                    if contribution < -0.05
                    else "NEUTRAL"
                ),
                "higher_value_effect": (
                    "RAISES_PRESSURE"
                    if coefficient > 0.0
                    else "LOWERS_PRESSURE"
                    if coefficient < 0.0
                    else "NEUTRAL"
                ),
            }
        )
    phase_contribution = 0.0
    for phase in PHASE_SEQUENCE:
        feature = f"phase_{phase}"
        value = float(row[feature])
        standardized = (value - artifact.means[feature]) / artifact.scales[feature]
        phase_contribution += float(coefficients[feature]) * standardized
    output.append(
        {
            "driver_id": "phase_context",
            "signal_group": "PHASE_CONTEXT",
            "value": 1.0,
            "standardized_value": None,
            "contribution": phase_contribution,
            "current_effect": (
                "RAISES_PRESSURE"
                if phase_contribution > 0.05
                else "LOWERS_PRESSURE"
                if phase_contribution < -0.05
                else "NEUTRAL"
            ),
            "higher_value_effect": "NEUTRAL",
        }
    )
    return output


def _latest_observed_state(
    state: StateStageResult,
    cutoff: pd.Timestamp,
) -> tuple[dict[str, object], tuple[dict[str, object], ...]]:
    current_state = state.confirmed_state_frame.copy()
    origins = pd.to_datetime(current_state["forecast_origin"], errors="coerce")
    selected = current_state.loc[origins == cutoff].tail(1)
    if selected.empty:
        raise ValueError("CURRENT_CONFIRMED_STATE_UNAVAILABLE")
    confirmed = selected.iloc[0]
    matching = [
        item
        for item in state.raw_history
        if str(item.observed_state.get("as_of_date") or "")[:10]
        == cutoff.date().isoformat()
    ]
    if not matching:
        raise ValueError("CURRENT_OBSERVED_STATE_UNAVAILABLE")
    raw = matching[-1]
    observed = dict(raw.observed_state)
    observed.update(
        {
            "phase": str(confirmed["confirmed_phase"]),
            "raw_phase": str(confirmed["raw_phase"]),
            "candidate_phase": (
                str(confirmed["candidate_phase"])
                if pd.notna(confirmed.get("candidate_phase"))
                else None
            ),
            "candidate_streak": int(confirmed.get("candidate_streak") or 0),
            "phase_duration": int(confirmed["phase_duration"]),
            "duration_months": int(confirmed["phase_duration"]),
        }
    )
    recent_changes = tuple(dict(item) for item in raw.recent_changes)
    if not recent_changes:
        recent_changes = _core_recent_changes(state, cutoff)
    return observed, recent_changes


def _core_recent_changes(
    state: StateStageResult,
    cutoff: pd.Timestamp,
) -> tuple[dict[str, object], ...]:
    """Describe 1/3/6-release movement from the same RTDSM core panel."""

    panel = getattr(state, "core_panel", pd.DataFrame()).copy()
    if panel.empty or "forecast_origin" not in panel:
        return ()
    panel["forecast_origin"] = pd.to_datetime(
        panel["forecast_origin"], errors="coerce"
    )
    panel = panel.dropna(subset=["forecast_origin"]).sort_values(
        "forecast_origin", kind="stable"
    )
    current_matches = panel.index[panel["forecast_origin"] == cutoff].tolist()
    if not current_matches:
        return ()
    current_position = panel.index.get_loc(current_matches[-1])
    records: list[dict[str, object]] = []
    signal_columns = ("IPT_z", "H_z", "EMPLOY_z", "RUC_z")
    for horizon in (1, 3, 6):
        record: dict[str, object] = {
            "horizon_months": horizon,
            "comparison_start_date": None,
            "comparison_end_date": cutoff.date().isoformat(),
            "status": "UNAVAILABLE",
            "composite_delta": None,
            "breadth": None,
            "available_pairs": 0,
            "activity_delta": None,
            "labor_income_delta": None,
        }
        prior_position = current_position - horizon
        if prior_position < 0:
            records.append(record)
            continue
        current = panel.iloc[current_position]
        prior = panel.iloc[prior_position]
        prior_origin = pd.Timestamp(prior["forecast_origin"])
        record["comparison_start_date"] = prior_origin.date().isoformat()
        try:
            delta = float(current["level"]) - float(prior["level"])
        except (KeyError, TypeError, ValueError):
            records.append(record)
            continue
        comparisons: list[bool] = []
        for column in signal_columns:
            if column not in panel:
                continue
            try:
                current_value = float(current[column])
                prior_value = float(prior[column])
            except (TypeError, ValueError):
                continue
            if math.isfinite(current_value) and math.isfinite(prior_value):
                comparisons.append(current_value > prior_value)
        breadth = (
            sum(comparisons) / len(comparisons) if comparisons else None
        )
        if breadth is None:
            status = "UNAVAILABLE"
        elif delta > 0.0 and breadth >= 0.50:
            status = "STRENGTHENING"
        elif delta < 0.0 and breadth <= 0.50:
            status = "WEAKENING"
        else:
            status = "MIXED"
        record.update(
            {
                "status": status,
                "composite_delta": delta,
                "breadth": breadth,
                "available_pairs": len(comparisons),
                "activity_delta": (
                    float(current["activity_score"])
                    - float(prior["activity_score"])
                    if "activity_score" in panel
                    else None
                ),
                "labor_income_delta": (
                    float(current["labor_income_score"])
                    - float(prior["labor_income_score"])
                    if "labor_income_score" in panel
                    else None
                ),
            }
        )
        records.append(record)
    return tuple(records)


def _recent_confirmed_phase_history(
    state: StateStageResult,
    cutoff: pd.Timestamp,
) -> list[dict[str, object]]:
    """Keep the route/ribbon on the same confirmed-state contract as current."""

    observed_by_date = {
        str(item.observed_state.get("as_of_date") or "")[:10]: item.observed_state
        for item in state.raw_history
    }
    frame = state.confirmed_state_frame.copy()
    frame["forecast_origin"] = pd.to_datetime(
        frame["forecast_origin"], errors="coerce"
    )
    frame = frame.loc[
        (frame["forecast_origin"] <= cutoff)
        & frame["confirmed_phase"].isin(PHASE_SEQUENCE)
    ].tail(12)
    output: list[dict[str, object]] = []
    for row in frame.to_dict(orient="records"):
        observed_at = pd.Timestamp(row["forecast_origin"]).date().isoformat()
        observed = observed_by_date.get(observed_at, {})
        try:
            level = float(observed.get("level"))
            momentum = float(observed.get("momentum"))
        except (TypeError, ValueError):
            continue
        if not math.isfinite(level) or not math.isfinite(momentum):
            continue
        output.append(
            {
                "date": observed_at,
                "level": level,
                "momentum": momentum,
                "phase": str(row["confirmed_phase"]),
                "nber_recession": False,
                "confidence": observed.get("confidence"),
                "revision_sensitivity": observed.get("revision_sensitivity"),
            }
        )
    return output


def build_transition_production_forecast(
    as_of_date: str | date,
    *,
    state: StateStageResult,
    driver: DriverStageResult,
    feasibility: StateTransitionFeasibilityReport,
) -> TransitionProductionForecast:
    """Fit validated task owners and score one exact current forecast origin."""

    if str(feasibility.status) != "GO":
        raise ValueError("TRANSITION_FEASIBILITY_NOT_GO")
    cutoff = _normalized_cutoff(as_of_date)
    extended_current = _current_row(driver.extended_dataset, cutoff)
    core_current = _current_row(driver.core_dataset, cutoff)

    pressure_training = _known_training_rows(
        driver.extended_dataset,
        cutoff,
        target_column="pressure_target",
        known_at_column="target_known_at",
    )
    pressure_l2 = select_transition_l2(
        pressure_training,
        driver.extended_dataset.feature_names,
        task="pressure",
    )
    pressure_artifact = fit_binary_logit(
        pressure_training,
        driver.extended_dataset.feature_names,
        l2=pressure_l2,
    )
    pressure_artifact = _calibrate_pressure(
        pressure_artifact,
        feasibility.extended_validation,
    )
    if pressure_artifact.publication_status != "READY":
        raise ValueError("PRESSURE_MODEL_NOT_READY")
    pressure_probability = float(
        predict_binary_probability(pressure_artifact, extended_current)[0]
    )
    pressure_percentile = _pressure_percentile(
        pressure_artifact,
        driver.extended_dataset,
        pressure_probability,
        cutoff,
    )

    destination_training = _known_training_rows(
        driver.core_dataset,
        cutoff,
        target_column="destination_target",
        known_at_column="destination_known_at",
    )
    destination_l2 = select_transition_l2(
        destination_training,
        driver.core_dataset.feature_names,
        task="destination",
    )
    destination_artifact = fit_multinomial_logit(
        destination_training,
        driver.core_dataset.feature_names,
        l2=destination_l2,
    )
    destination_artifact = _calibrate_destination(
        destination_artifact,
        feasibility.core_validation,
    )
    if destination_artifact.publication_status != "READY":
        raise ValueError("DESTINATION_MODEL_NOT_READY")
    current_phase = str(core_current.iloc[0]["confirmed_phase"])
    destination_probabilities = predict_destination_probabilities(
        destination_artifact,
        core_current,
        current_phases=(current_phase,),
    )[0]
    ordered_destinations = sorted(
        (
            {"phase": phase, "probability": probability}
            for phase, probability in destination_probabilities.items()
            if phase != current_phase
        ),
        key=lambda item: float(item["probability"]),
        reverse=True,
    )
    observed_state, recent_changes = _latest_observed_state(state, cutoff)
    monitor = {
        "contract_version": TRANSITION_FORECAST_CONTRACT_VERSION,
        "status": "READY",
        "current_phase": current_phase,
        "pressure": {
            "probability": pressure_probability,
            "historical_percentile": pressure_percentile,
            "level": _pressure_level(pressure_probability),
            "horizon_releases": 3,
            "horizon_definition": "next_3_usable_releases",
        },
        "destination": {
            "probabilities": destination_probabilities,
            "primary_phase": ordered_destinations[0]["phase"],
            "alternatives": ordered_destinations,
            "current_phase_excluded": True,
            "horizon_definition": "next_confirmed_transition",
        },
        "drivers": _driver_rows(pressure_artifact, extended_current),
        "recent_phase_history": _recent_confirmed_phase_history(state, cutoff),
        "model_roles": {
            "current_state": "confirmed_rtdsm",
            "pressure": "required_extended_drivers",
            "destination": "compact_core_state",
        },
    }
    return TransitionProductionForecast(
        as_of_date=cutoff.date().isoformat(),
        observed_state=_json_safe(observed_state),
        recent_changes=tuple(_json_safe(recent_changes)),
        monitor=_json_safe(monitor),
        artifacts={
            "pressure": _json_safe(pressure_artifact.to_dict()),
            "destination": _json_safe(destination_artifact.to_dict()),
        },
    )


def _fallback_evidence(
    driver: DriverStageResult,
    cutoff: pd.Timestamp,
) -> list[dict[str, object]]:
    rows = _current_row(driver.core_dataset, cutoff)
    row = rows.iloc[0]
    return [
        {
            "factor": factor,
            "value": float(row[column]),
            "source_date": cutoff.date().isoformat(),
        }
        for factor, column in (
            ("activity_score", "level"),
            ("labor_income_score", "momentum"),
        )
    ]


def publish_transition_production_forecast(
    as_of_date: str | date,
    *,
    state_builder: Callable[[pd.Timestamp], StateStageResult] = _build_state_stage,
    driver_builder: Callable[[pd.Timestamp, StateStageResult], DriverStageResult] = _build_driver_stage,
    feasibility_runner: Callable[..., StateTransitionFeasibilityReport] = run_state_transition_feasibility,
    artifact_writer: Callable[[dict[str, object]], object] = upsert_cycle_model_artifact,
    snapshot_writer: Callable[[list[dict[str, object]]], object] = upsert_cycle_snapshots,
    base_snapshot_loader: Callable[..., Mapping[str, object] | None] = load_cycle_snapshot,
) -> dict[str, object]:
    """Validate, fit and atomically publish a last-good compatible snapshot."""

    cutoff = _normalized_cutoff(as_of_date)
    state = state_builder(cutoff)
    driver = driver_builder(cutoff, state)
    feasibility = feasibility_runner(
        cutoff.date().isoformat(),
        state_builder=lambda _cutoff: state,
        driver_builder=lambda _cutoff, _state: driver,
    )
    if feasibility.status != "GO":
        return {
            "status": str(feasibility.status),
            "reason_codes": list(feasibility.reason_codes),
            "snapshot_written": False,
        }

    forecast = build_transition_production_forecast(
        cutoff.date().isoformat(),
        state=state,
        driver=driver,
        feasibility=feasibility,
    )
    validation = (
        feasibility.to_dict()
        if hasattr(feasibility, "to_dict")
        else {"status": feasibility.status, "reason_codes": feasibility.reason_codes}
    )
    artifact_writer(
        {
            "model_version": TRANSITION_MODEL_VERSION,
            "trained_through": forecast.as_of_date,
            "feature_schema_version": TRANSITION_FEATURE_SCHEMA_VERSION,
            "parameters_json": _canonical_json(forecast.artifacts),
            "validation_metrics_json": _canonical_json(validation),
            "publication_status": "READY",
            "publication_status_json": _canonical_json(
                {"status": "GO", "reason_codes": []}
            ),
        }
    )
    try:
        base = dict(base_snapshot_loader(as_of_date=forecast.as_of_date) or {})
    except Exception:
        base = {}
    evidence = json.loads(str(base.get("top_evidence_json") or "[]"))
    if not evidence:
        evidence = _fallback_evidence(driver, cutoff)
    drivers = list(forecast.monitor["drivers"])
    snapshot_writer(
        [
            {
                "as_of_date": forecast.as_of_date,
                "model_version": TRANSITION_MODEL_VERSION,
                "run_kind": "current",
                "training_cutoff_date": forecast.as_of_date,
                "data_cutoff_date": forecast.as_of_date,
                "baseline_as_of_date": None,
                "source_collected_at": base.get("source_collected_at"),
                "source_coverage_json": base.get("source_coverage_json"),
                "status": "READY",
                "current_phase": forecast.observed_state["phase"],
                "expected_transition": forecast.monitor["destination"]["primary_phase"],
                "nber_recession": base.get("nber_recession"),
                "observed_state_json": _canonical_json(forecast.observed_state),
                "recent_changes_json": _canonical_json(forecast.recent_changes),
                "transition_monitor_json": _canonical_json(forecast.monitor),
                "probabilities_json": "{}",
                "forecast_path_json": "[]",
                "factor_contributions_json": _canonical_json(drivers),
                "top_evidence_json": _canonical_json(evidence),
                "warnings_json": _canonical_json(
                    [
                        "전환압력은 정확한 전환 월이 아니라 다음 3개 usable release 안의 가능성입니다.",
                        "목적지 분포는 전환이 발생할 경우의 다음 confirmed phase 조건부 확률입니다.",
                    ]
                ),
            }
        ]
    )
    return {
        "status": "READY",
        "model_version": TRANSITION_MODEL_VERSION,
        "as_of_date": forecast.as_of_date,
        "current_phase": forecast.observed_state["phase"],
        "primary_destination": forecast.monitor["destination"]["primary_phase"],
        "pressure_probability": forecast.monitor["pressure"]["probability"],
        "snapshot_written": True,
    }
