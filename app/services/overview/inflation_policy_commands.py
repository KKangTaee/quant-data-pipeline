"""Explicit persistence and bounded reverse commands for the policy workbench."""

from __future__ import annotations

import json
import math
import uuid
from collections.abc import Callable, Mapping, Sequence
from dataclasses import asdict, is_dataclass
from datetime import datetime, timezone
from typing import Any

from finance.data.inflation_policy_results import save_yield_resistance_definition
from finance.inflation_policy_equity_stress import (
    EquityStressArtifact,
    simulate_equity_stress,
)
from finance.inflation_policy_simulation import (
    RateTargetCondition,
    SimulationPath,
    condition_paths_on_target,
    posterior_target_probability_for_next_pce,
)
from finance.loaders.inflation_policy import (
    load_inflation_policy_model_artifact,
    load_latest_inflation_policy_snapshot,
)


ALLOWED_INSTRUMENTS = {"DGS2", "DGS10", "DFII10", "T10YIE", "T10Y2Y", "ACMTP10"}
ALLOWED_LOOKBACKS = {63, 252, 504}
ALLOWED_TARGET_CONDITIONS = {"REACH", "CONFIRMED", "HOLD"}
MAX_TARGET_WIDTH_PCT = 2.0
MAX_SIMULATION_PATHS = 50_000


def _timestamp(value: object, *, field: str) -> datetime:
    if isinstance(value, datetime):
        parsed = value
    else:
        try:
            parsed = datetime.fromisoformat(
                str(value).strip().replace("Z", "+00:00")
            )
        except ValueError as exc:
            raise ValueError(f"Invalid {field}: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _finite(value: object, *, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be finite")
    try:
        parsed = float(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{field} must be finite") from exc
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _decoded_mapping(value: object, *, field: str) -> dict[str, object]:
    try:
        decoded = json.loads(value) if isinstance(value, str) else value
    except json.JSONDecodeError as exc:
        raise ValueError(f"{field} must be valid JSON") from exc
    if decoded in (None, ""):
        return {}
    if not isinstance(decoded, Mapping):
        raise ValueError(f"{field} must be an object")
    return {str(key): item for key, item in decoded.items()}


def _bounds(command: Mapping[str, object]) -> tuple[float, float, float]:
    lower = _finite(
        command.get("zone_lower_pct", command.get("lower_pct")), field="구간 하단"
    )
    upper = _finite(
        command.get("zone_upper_pct", command.get("upper_pct")), field="구간 상단"
    )
    buffer = _finite(command.get("buffer_pct", 0.0), field="buffer_pct")
    if lower > upper:
        raise ValueError("구간 하단은 상단을 초과할 수 없습니다.")
    if buffer < 0.0:
        raise ValueError("buffer_pct는 음수일 수 없습니다.")
    return lower, upper, buffer


def _instrument(command: Mapping[str, object]) -> str:
    instrument = str(command.get("instrument") or "").strip().upper()
    if instrument not in ALLOWED_INSTRUMENTS:
        raise ValueError(
            "instrument는 DGS2, DGS10, DFII10, T10YIE, T10Y2Y, ACMTP10 중 하나여야 합니다."
        )
    return instrument


def save_user_resistance_definition(
    command: Mapping[str, object],
    *,
    result_saver: Callable[[Mapping[str, object]], object] = (
        save_yield_resistance_definition
    ),
    id_factory: Callable[[], object] = uuid.uuid4,
    now_factory: Callable[[], object] = lambda: datetime.now(timezone.utc),
) -> dict[str, object]:
    """Validate and persist one criterion that is explicitly owned by the user."""

    if str(command.get("owner") or "USER").upper() != "USER":
        raise ValueError("사용자 저장 기준의 owner는 USER여야 합니다.")
    instrument = _instrument(command)
    lower, upper, buffer = _bounds(command)
    short_lookback = int(command.get("short_lookback_days") or 63)
    long_lookback = int(command.get("long_lookback_days") or 504)
    if short_lookback not in ALLOWED_LOOKBACKS or long_lookback not in ALLOWED_LOOKBACKS:
        raise ValueError("lookback은 63, 252, 504일 중 하나여야 합니다.")
    if short_lookback > long_lookback:
        raise ValueError("short lookback은 long lookback을 초과할 수 없습니다.")
    profile_input = _decoded_mapping(
        command.get("confirmation_profile"), field="confirmation_profile"
    )
    confirmation_count = int(
        command.get(
            "confirmation_count", profile_input.get("confirmation_count", 3)
        )
    )
    confirmation_window = int(
        command.get(
            "confirmation_window", profile_input.get("confirmation_window", 5)
        )
    )
    if not 1 <= confirmation_count <= 20 or not 1 <= confirmation_window <= 20:
        raise ValueError("확인 횟수와 확인 기간은 1~20이어야 합니다.")
    if confirmation_count > confirmation_window:
        raise ValueError("확인 횟수는 확인 기간을 초과할 수 없습니다.")
    generated_id = str(uuid.UUID(str(id_factory())))
    saved_at = _timestamp(now_factory(), field="saved_at").isoformat()
    known_at = _timestamp(
        command.get("as_of_at") or saved_at, field="as_of_at"
    ).isoformat()
    profile = {
        "confirmation_count": confirmation_count,
        "confirmation_window": confirmation_window,
        "require_breakeven_confirmation": bool(
            command.get(
                "require_breakeven_confirmation",
                profile_input.get("require_breakeven_confirmation", False),
            )
        ),
        "exclude_term_premium_only": bool(
            command.get(
                "exclude_term_premium_only",
                profile_input.get("exclude_term_premium_only", True),
            )
        ),
    }
    row: dict[str, object] = {
        "definition_id": generated_id,
        "owner": "USER",
        "definition_name": str(command.get("definition_name") or "사용자 금리 기준").strip(),
        "instrument": instrument,
        "short_lookback_days": short_lookback,
        "long_lookback_days": long_lookback,
        "zone_lower_pct": lower,
        "zone_upper_pct": upper,
        "buffer_pct": buffer,
        "confirmation_profile_json": profile,
        "known_at": known_at,
        "algorithm_version": "user-resistance-criterion-v1",
        "is_active": 1,
        "saved_at": saved_at,
    }
    result_saver(row)
    return {
        "publication_status": "READY",
        "message": "사용자 금리 기준을 저장했습니다.",
        "definition": {
            **row,
            "owner_label": "사용자 기준",
            "confirmation_profile": profile,
            "editable": True,
        },
    }


def _not_available(
    *, reason: str, snapshot: Mapping[str, object] | None = None
) -> dict[str, object]:
    return {
        "publication_status": "NOT_AVAILABLE",
        "reason": reason,
        "as_of_at": snapshot.get("as_of_at") if snapshot else None,
        "model_version": str(snapshot.get("model_version") or "") if snapshot else "",
    }


def _simulation_paths(value: object) -> tuple[SimulationPath, ...]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        raise ValueError("joint_rate_paths must be an array")
    result: list[SimulationPath] = []
    for index, raw in enumerate(value[:MAX_SIMULATION_PATHS]):
        if not isinstance(raw, Mapping):
            raise ValueError(f"joint_rate_paths[{index}] must be an object")
        rate_paths = _decoded_mapping(
            raw.get("rate_paths_pct"), field=f"joint_rate_paths[{index}].rate_paths_pct"
        )
        result.append(
            SimulationPath(
                path_id=str(raw.get("path_id") or f"path-{index}"),
                weight=_finite(raw.get("weight"), field="path weight"),
                q4_core_pce_pct=_finite(
                    raw.get("q4_core_pce_pct"), field="q4_core_pce_pct"
                ),
                remaining_monthly_mom_pct=tuple(
                    _finite(item, field="remaining monthly PCE")
                    for item in (raw.get("remaining_monthly_mom_pct") or [])
                ),
                policy_net_steps=int(raw.get("policy_net_steps") or 0),
                year_end_policy_midpoint_pct=_finite(
                    raw.get("year_end_policy_midpoint_pct"),
                    field="year_end_policy_midpoint_pct",
                ),
                rate_paths_pct={
                    str(instrument): tuple(
                        _finite(item, field=f"{instrument} path")
                        for item in values
                    )
                    for instrument, values in rate_paths.items()
                    if isinstance(values, Sequence) and not isinstance(values, (str, bytes))
                },
            )
        )
    return tuple(result)


def _summary_mapping(value: object) -> dict[str, object]:
    if isinstance(value, Mapping):
        return {str(key): item for key, item in value.items()}
    if is_dataclass(value):
        return asdict(value)
    raise ValueError("reverse scenario runner returned an invalid summary")


def run_reverse_scenario_command(
    command: Mapping[str, object],
    *,
    snapshot_loader: Callable[..., Mapping[str, object] | None] = (
        load_latest_inflation_policy_snapshot
    ),
    artifact_loader: Callable[..., Mapping[str, object] | None] = (
        load_inflation_policy_model_artifact
    ),
    scenario_runner: Callable[..., object] = condition_paths_on_target,
) -> dict[str, object]:
    """Condition exact stored joint paths on a bounded user-selected rate target."""

    instrument = _instrument(command)
    lower, upper, buffer = _bounds(command)
    if upper - lower > MAX_TARGET_WIDTH_PCT + 1e-12:
        raise ValueError("목표 구간 폭은 200bp를 초과할 수 없습니다.")
    condition = str(command.get("condition") or "REACH").strip().upper()
    if condition not in ALLOWED_TARGET_CONDITIONS:
        raise ValueError("condition은 REACH, CONFIRMED, HOLD 중 하나여야 합니다.")
    hold_days = int(command.get("hold_days") or 3)
    if not 1 <= hold_days <= 20:
        raise ValueError("hold_days는 1~20이어야 합니다.")
    snapshot = snapshot_loader(as_of_at=command.get("as_of_at"))
    if snapshot is None:
        return _not_available(reason="선택한 기준시각의 snapshot이 없습니다.")
    snapshot_as_of = _timestamp(snapshot.get("as_of_at"), field="snapshot.as_of_at")
    horizon = _timestamp(command.get("horizon_at"), field="horizon_at")
    if horizon < snapshot_as_of:
        raise ValueError("horizon은 snapshot 기준시각보다 빠를 수 없습니다.")
    freshness = _decoded_mapping(snapshot.get("freshness_json"), field="freshness_json")
    trained_cutoff_at = freshness.get("trained_cutoff_at") or snapshot.get("as_of_at")
    model_version = str(snapshot.get("model_version") or "")
    artifact = artifact_loader(
        model_version=model_version,
        trained_cutoff_at=trained_cutoff_at,
        component="core_pce_hybrid",
    )
    if artifact is None:
        return _not_available(
            reason="선택한 snapshot과 정확히 일치하는 검증 artifact가 없습니다.",
            snapshot=snapshot,
        )
    if str(artifact.get("publication_status") or "") != "READY":
        return _not_available(
            reason="정확히 일치하는 artifact가 아직 READY 검증을 통과하지 못했습니다.",
            snapshot=snapshot,
        )
    parameters = _decoded_mapping(artifact.get("parameters_json"), field="parameters_json")
    raw_paths = parameters.get("joint_rate_paths")
    if not isinstance(raw_paths, Sequence) or isinstance(raw_paths, (str, bytes)) or not raw_paths:
        return _not_available(
            reason="검증 artifact에 공동 물가·정책·금리 경로가 저장되어 있지 않습니다.",
            snapshot=snapshot,
        )
    paths = _simulation_paths(raw_paths)
    validation = _decoded_mapping(artifact.get("validation_json"), field="validation_json")
    minimum_supporting_paths = max(
        1, int(validation.get("reverse_minimum_supporting_paths") or 100)
    )
    minimum_effective_paths = max(
        1.0, float(validation.get("reverse_minimum_effective_paths") or 50.0)
    )
    target = RateTargetCondition(
        instrument=instrument,
        zone_lower_pct=lower,
        zone_upper_pct=upper,
        condition="BREAK" if condition == "CONFIRMED" else condition,
        buffer_pct=buffer,
        hold_days=hold_days,
    )
    summary = _summary_mapping(
        scenario_runner(
            paths,
            target,
            minimum_supporting_paths=minimum_supporting_paths,
            minimum_effective_paths=minimum_effective_paths,
        )
    )
    available = str(summary.get("status") or "") == "AVAILABLE"
    result: dict[str, object] = {
        "publication_status": "READY" if available else "NOT_AVAILABLE",
        "reason": (
            "선택한 목표를 만족하는 검증 경로의 조건부분포입니다."
            if available
            else "목표를 만족하는 경로 표본이 부족해 조건부분포를 공개하지 않습니다."
        ),
        "as_of_at": snapshot.get("as_of_at"),
        "model_version": model_version,
        "target": {
            "instrument": instrument,
            "zone_lower_pct": lower,
            "zone_upper_pct": upper,
            "buffer_pct": buffer,
            "condition": condition,
            "hold_days": hold_days,
            "horizon_at": horizon.isoformat(),
        },
        **summary,
    }
    if available:
        result["next_print_sensitivity"] = [
            {
                "mom_pct": value,
                "target_probability": posterior_target_probability_for_next_pce(
                    paths,
                    target,
                    observed_mom_pct=value,
                    observation_noise_pct=0.08,
                ),
            }
            for value in (0.1, 0.2, 0.3, 0.4, 0.5)
        ]
    return result


def _equity_artifact(value: Mapping[str, object]) -> EquityStressArtifact:
    parameters = _decoded_mapping(value.get("parameters_json"), field="parameters_json")
    artifact_raw = _decoded_mapping(parameters.get("artifact", parameters), field="artifact")
    residual_rows = artifact_raw.get("joint_residuals") or []
    residuals: list[tuple[float, float]] = []
    if isinstance(residual_rows, Sequence) and not isinstance(residual_rows, (str, bytes)):
        for index, row in enumerate(residual_rows):
            if not isinstance(row, Sequence) or isinstance(row, (str, bytes)) or len(row) != 2:
                raise ValueError(f"joint_residuals[{index}] must contain two values")
            residuals.append(
                (
                    _finite(row[0], field="EPS residual"),
                    _finite(row[1], field="multiple residual"),
                )
            )
    eps_response = _decoded_mapping(artifact_raw.get("eps_response"), field="eps_response")
    multiple_response = _decoded_mapping(
        artifact_raw.get("multiple_response"), field="multiple_response"
    )
    scenario_features = _decoded_mapping(
        artifact_raw.get("scenario_feature_values"), field="scenario_feature_values"
    )
    return EquityStressArtifact(
        model_version=str(value.get("model_version") or artifact_raw.get("model_version") or ""),
        eps_response={key: _finite(item, field=f"eps_response.{key}") for key, item in eps_response.items()},
        multiple_response={key: _finite(item, field=f"multiple_response.{key}") for key, item in multiple_response.items()},
        joint_residuals=tuple(residuals),
        validation_metrics=_decoded_mapping(
            value.get("validation_json"), field="validation_json"
        ),
        trained_through=(
            str(artifact_raw.get("trained_through"))
            if artifact_raw.get("trained_through")
            else None
        ),
        publication_status=str(value.get("publication_status") or "NOT_AVAILABLE"),
        reason_codes=tuple(
            str(item)
            for item in (artifact_raw.get("reason_codes") or [])
        ),
        latest_measured_next_year_eps_revision_pct=(
            _finite(
                artifact_raw.get("latest_measured_next_year_eps_revision_pct"),
                field="latest measured EPS revision",
            )
            if artifact_raw.get("latest_measured_next_year_eps_revision_pct") is not None
            else None
        ),
        scenario_feature_values={
            key: _finite(item, field=f"scenario_feature_values.{key}")
            for key, item in scenario_features.items()
        },
    )


def run_equity_stress_scenario_command(
    command: Mapping[str, object],
    *,
    snapshot_loader: Callable[..., Mapping[str, object] | None] = (
        load_latest_inflation_policy_snapshot
    ),
    artifact_loader: Callable[..., Mapping[str, object] | None] = (
        load_inflation_policy_model_artifact
    ),
    scenario_runner: Callable[..., object] = simulate_equity_stress,
) -> dict[str, object]:
    """Run a bounded user EPS/level scenario against exact stored artifacts."""

    target_level = _finite(command.get("target_level"), field="target level")
    if target_level <= 0.0:
        raise ValueError("target level must be positive")
    uplift = _finite(
        command.get("user_ai_eps_uplift_pct", 0.0), field="AI EPS uplift"
    )
    if not -30.0 <= uplift <= 50.0:
        raise ValueError("AI EPS uplift must be between -30% and +50%")
    snapshot = snapshot_loader(as_of_at=command.get("as_of_at"))
    if snapshot is None:
        return _not_available(reason="선택한 기준시각의 snapshot이 없습니다.")
    freshness = _decoded_mapping(snapshot.get("freshness_json"), field="freshness_json")
    trained_cutoff_at = freshness.get("trained_cutoff_at") or snapshot.get("as_of_at")
    model_version = str(snapshot.get("model_version") or "")
    equity_row = artifact_loader(
        model_version=model_version,
        trained_cutoff_at=trained_cutoff_at,
        component="equity_stress",
    )
    if equity_row is None:
        return _not_available(
            reason="선택한 snapshot과 정확히 일치하는 주식 스트레스 artifact가 없습니다.",
            snapshot=snapshot,
        )
    macro_row = artifact_loader(
        model_version=model_version,
        trained_cutoff_at=trained_cutoff_at,
        component="core_pce_hybrid",
    )
    if macro_row is None:
        return _not_available(
            reason="선택한 snapshot과 정확히 일치하는 공동 거시경로 artifact가 없습니다.",
            snapshot=snapshot,
        )
    equity_parameters = _decoded_mapping(
        equity_row.get("parameters_json"), field="equity parameters"
    )
    macro_parameters = _decoded_mapping(
        macro_row.get("parameters_json"), field="macro parameters"
    )
    current_index = equity_parameters.get("current_index_level")
    forward_eps = equity_parameters.get("base_forward_eps")
    raw_paths = macro_parameters.get("joint_rate_paths")
    if current_index is None or forward_eps is None:
        return _not_available(
            reason="주식 스트레스 artifact에 현재 지수와 차년도 EPS 기준이 없습니다.",
            snapshot=snapshot,
        )
    if not isinstance(raw_paths, Sequence) or isinstance(raw_paths, (str, bytes)) or not raw_paths:
        return _not_available(
            reason="검증 artifact에 공동 물가·정책·금리 경로가 저장되어 있지 않습니다.",
            snapshot=snapshot,
        )
    result = scenario_runner(
        _equity_artifact(equity_row),
        _simulation_paths(raw_paths),
        current_index=_finite(current_index, field="current index"),
        forward_eps=_finite(forward_eps, field="forward EPS"),
        user_ai_eps_uplift_pct=uplift,
        target_levels=(target_level,),
    )
    return {
        **_summary_mapping(result),
        "reason": "저장된 공동 경로에 사용자 EPS 가정과 지수 조건을 적용했습니다.",
        "model_version": model_version,
        "as_of_at": snapshot.get("as_of_at"),
    }
