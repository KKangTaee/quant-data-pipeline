"""DB-backed read model for the inflation, policy, and yield workbench."""

from __future__ import annotations

import json
import math
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

from finance.loaders.inflation_policy import (
    load_latest_inflation_policy_snapshot,
    load_yield_resistance_definitions,
)


SnapshotLoader = Callable[..., Mapping[str, object] | None]
DefinitionsLoader = Callable[..., Sequence[Mapping[str, object]]]
PUBLICATION_STATUSES = {"READY", "LIMITED", "NOT_AVAILABLE", "FAILED"}
STATE_LABELS = {
    "rapid_disinflation": "빠른 둔화",
    "gradual_disinflation": "완만한 둔화",
    "sticky": "고착",
    "reacceleration": "재가속",
    "shock_reacceleration": "충격성 재가속",
}
REASON_LABELS = {
    "q4_path_rolling_origin_validation_not_ready": (
        "연말 Core PCE 경로의 시점별 검증이 아직 부족합니다."
    ),
    "policy_rolling_origin_validation_not_ready": (
        "정책 경로의 시점별 확률 검증이 아직 부족합니다."
    ),
    "resistance_event_calibration_not_ready": (
        "저항선 돌파·안착 확률 보정이 아직 완료되지 않았습니다."
    ),
    "joint_rate_path_validation_not_ready": (
        "물가·정책·금리의 공동 경로 검증이 아직 완료되지 않았습니다."
    ),
    "prior_inflation_probability_not_available": (
        "검증된 사전 인플레이션 확률이 없어 확인 상태를 확정할 수 없습니다."
    ),
    "benchmark_suite_incomplete": "필수 비교 검증 묶음이 아직 완전하지 않습니다.",
    "official_eps_vintages_not_available": (
        "공식 S&P 500 EPS 빈티지가 없어 주가 스트레스를 계산할 수 없습니다."
    ),
    "official_eps_vintages_or_joint_paths_not_available": (
        "공식 S&P 500 EPS 빈티지와 검증된 공동 거시경로가 필요합니다."
    ),
    "joint_rate_paths_not_available": (
        "검증된 물가·정책·금리 공동 경로가 없어 주가 스트레스를 계산할 수 없습니다."
    ),
    "recession_model_not_available": "침체 모델은 5차 개발 전까지 연결하지 않습니다.",
}


def _status(value: object, *, default: str = "NOT_AVAILABLE") -> str:
    candidate = str(value or default).upper()
    return candidate if candidate in PUBLICATION_STATUSES else "FAILED"


def _reason(value: object, *, fallback: str) -> str:
    raw = str(value or "").strip()
    if not raw:
        return fallback
    return REASON_LABELS.get(raw, raw.replace("_", " "))


def _decoded(value: object, *, default: object) -> object:
    if value in (None, ""):
        return default
    if isinstance(value, str):
        return json.loads(value)
    return value


def _mapping(value: object) -> dict[str, object]:
    decoded = _decoded(value, default={})
    if not isinstance(decoded, Mapping):
        raise ValueError("expected an object payload")
    return {str(key): item for key, item in decoded.items()}


def _sequence(value: object) -> list[object]:
    decoded = _decoded(value, default=[])
    if not isinstance(decoded, Sequence) or isinstance(decoded, (str, bytes)):
        raise ValueError("expected an array payload")
    return list(decoded)


def _finite(value: object, *, field: str) -> float:
    if isinstance(value, bool):
        raise ValueError(f"{field} must be finite")
    parsed = float(value)
    if not math.isfinite(parsed):
        raise ValueError(f"{field} must be finite")
    return parsed


def _simplex(value: object, *, field: str) -> dict[str, float]:
    raw = _mapping(value)
    if not raw:
        return {}
    parsed = {key: _finite(item, field=f"{field}.{key}") for key, item in raw.items()}
    if any(item < 0.0 for item in parsed.values()):
        raise ValueError(f"{field} probabilities cannot be negative")
    total = sum(parsed.values())
    if total <= 0.0:
        raise ValueError(f"{field} probabilities require positive mass")
    return {key: item / total for key, item in parsed.items()}


def _probabilities(value: object, *, field: str) -> dict[str, float]:
    raw = _mapping(value)
    result: dict[str, float] = {}
    for key, item in raw.items():
        parsed = _finite(item, field=f"{field}.{key}")
        if not 0.0 <= parsed <= 1.0:
            raise ValueError(f"{field}.{key} must be between zero and one")
        result[key] = parsed
    return result


def _json_safe(value: object) -> object:
    if value is None or isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        if not math.isfinite(value):
            raise ValueError("payload must contain only finite numbers")
        return value
    if isinstance(value, Decimal):
        parsed = float(value)
        if not math.isfinite(parsed):
            raise ValueError("payload must contain only finite numbers")
        return parsed
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, Sequence) and not isinstance(value, (str, bytes)):
        return [_json_safe(item) for item in value]
    return str(value)


def _empty_inflation(reason: str) -> dict[str, object]:
    return {
        "publication_status": "NOT_AVAILABLE",
        "reason": reason,
        "q4_quantiles_pct": {},
        "state_probabilities": {},
        "state_rows": [],
        "threshold_probabilities": {},
        "next_release_scenarios": [],
        "state_definition": {},
    }


def _empty_policy(reason: str) -> dict[str, object]:
    return {
        "publication_status": "NOT_AVAILABLE",
        "reason": reason,
        "next_meeting_probabilities": {},
        "net_move_probabilities": {},
        "year_end_target_probabilities": {},
        "committee_vote_prior": {},
        "sep_net_move_prior": {},
    }


def _empty_rates(reason: str) -> dict[str, object]:
    return {
        "publication_status": "NOT_AVAILABLE",
        "reason": reason,
        "ten_year": {},
        "instruments": {},
        "driver_decomposition": {},
        "inflation_confirmation": {"status": "UNCONFIRMED", "reason": reason},
        "term_premium_status": "NOT_AVAILABLE",
        "resistance_zones": [],
    }


def _empty_reverse(reason: str) -> dict[str, object]:
    return {"publication_status": "NOT_AVAILABLE", "reason": reason}


def _empty_equity(reason: str, *, status: str = "NOT_AVAILABLE") -> dict[str, object]:
    return {
        "publication_status": status,
        "reason": reason,
        "as_of_at": None,
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
    }


def _optional_finite(value: object, *, field: str) -> float | None:
    if value is None:
        return None
    return _finite(value, field=field)


def _finite_mapping(value: object, *, field: str) -> dict[str, float]:
    return {
        key: _finite(item, field=f"{field}.{key}")
        for key, item in _mapping(value).items()
    }


def _equity_section(value: object) -> dict[str, object]:
    unavailable_reason = "공식 S&P 500 EPS 빈티지와 검증된 공동 거시경로가 필요합니다."
    try:
        raw = _mapping(value)
        if not raw:
            return _empty_equity(unavailable_reason)
        status = _status(raw.get("publication_status"))
        ai_uplift = _finite(
            raw.get("user_ai_eps_uplift_pct", 0.0),
            field="equity.user_ai_eps_uplift_pct",
        )
        if not -30.0 <= ai_uplift <= 50.0:
            raise ValueError("equity.user_ai_eps_uplift_pct must be between -30 and 50")
        thresholds = _probabilities(
            raw.get("threshold_probabilities"), field="equity thresholds"
        )
        if status != "READY":
            thresholds = {}
        return {
            "publication_status": status,
            "reason": _reason(raw.get("reason"), fallback=unavailable_reason),
            "as_of_at": _json_safe(raw.get("as_of_at")),
            "index_quantiles": _finite_mapping(
                raw.get("index_quantiles"), field="equity.index_quantiles"
            ),
            "eps_quantiles": _finite_mapping(
                raw.get("eps_quantiles"), field="equity.eps_quantiles"
            ),
            "multiple_quantiles": _finite_mapping(
                raw.get("multiple_quantiles"), field="equity.multiple_quantiles"
            ),
            "threshold_probabilities": thresholds,
            "target_decompositions": _json_safe(
                _mapping(raw.get("target_decompositions"))
            ),
            "measured_next_year_eps_revision_pct": _optional_finite(
                raw.get("measured_next_year_eps_revision_pct"),
                field="equity.measured_next_year_eps_revision_pct",
            ),
            "user_ai_eps_uplift_pct": ai_uplift,
            "scenario_kind": str(raw.get("scenario_kind") or "MODEL_BASE"),
            "current_index_level": _optional_finite(
                raw.get("current_index_level"), field="equity.current_index_level"
            ),
            "base_forward_eps": _optional_finite(
                raw.get("base_forward_eps"), field="equity.base_forward_eps"
            ),
        }
    except (TypeError, ValueError, json.JSONDecodeError):
        return _empty_equity(
            "저장된 주가 스트레스 payload 검증에 실패했습니다.", status="FAILED"
        )


def _criterion_row(
    raw: Mapping[str, object],
    *,
    fallback_owner: str | None = None,
    fallback_instrument: str = "DGS10",
    source: str = "SAVED",
) -> dict[str, object]:
    profile = _mapping(raw.get("confirmation_profile_json"))
    owner = str(raw.get("owner") or fallback_owner or "AUTO").upper()
    lower = _finite(
        raw.get("zone_lower_pct"), field="resistance_zone.zone_lower_pct"
    )
    upper = _finite(
        raw.get("zone_upper_pct"), field="resistance_zone.zone_upper_pct"
    )
    if lower > upper:
        raise ValueError("resistance zone lower bound cannot exceed upper bound")
    return {
        "definition_id": str(raw.get("definition_id") or ""),
        "owner": owner,
        "owner_label": "자동 추천" if owner == "AUTO" else "사용자 기준",
        "definition_name": str(raw.get("definition_name") or ""),
        "instrument": str(raw.get("instrument") or fallback_instrument).upper(),
        "zone_lower_pct": lower,
        "zone_upper_pct": upper,
        "buffer_pct": _finite(raw.get("buffer_pct") or 0.0, field="buffer_pct"),
        "short_lookback_days": raw.get("short_lookback_days"),
        "long_lookback_days": raw.get("long_lookback_days"),
        "confirmation_profile": profile,
        "known_at": raw.get("known_at") or raw.get("known_at_date"),
        "saved_at": raw.get("saved_at"),
        "algorithm_version": str(raw.get("algorithm_version") or ""),
        "state": raw.get("state"),
        "zone_strength": raw.get("zone_strength"),
        "timeframes": list(raw.get("timeframes") or []),
        "source": source,
        "editable": owner == "USER",
    }


def _resistance_zones(
    rates: Mapping[str, object],
    definitions: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    result: list[dict[str, object]] = []
    for raw in definitions:
        result.append(_criterion_row(raw))
    ten_year = _mapping(rates.get("DGS10"))
    for kind, name in (
        ("active_test_zone", "현재 자동 저항 구간"),
        ("next_overhead_zone", "다음 자동 저항 구간"),
    ):
        zone = _mapping(ten_year.get(kind))
        if not zone:
            continue
        lower = zone.get("zone_lower_pct")
        upper = zone.get("zone_upper_pct")
        identity = (
            "AUTO",
            "DGS10",
            float(lower) if lower is not None else None,
            float(upper) if upper is not None else None,
        )
        existing = {
            (
                item["owner"],
                item["instrument"],
                item["zone_lower_pct"],
                item["zone_upper_pct"],
            )
            for item in result
        }
        if identity in existing:
            continue
        result.append(
            _criterion_row(
                {
                    **zone,
                    "definition_id": (
                        f"snapshot-auto:DGS10:{kind}:{zone.get('known_at_date')}:"
                        f"{lower}:{upper}"
                    ),
                    "definition_name": name,
                    "buffer_pct": zone.get("tolerance_pct") or 0.0,
                },
                fallback_owner="AUTO",
                source="SNAPSHOT_AUTO",
            )
        )
    return sorted(
        result,
        key=lambda item: (
            0 if item["owner"] == "AUTO" else 1,
            str(item["instrument"]),
            float(item["zone_lower_pct"]),
        ),
    )


def _build_model(
    snapshot: Mapping[str, object],
    definitions: Sequence[Mapping[str, object]],
) -> dict[str, object]:
    publication_status = _status(snapshot.get("publication_status"))
    inflation_raw = _mapping(snapshot.get("inflation_json"))
    policy_raw = _mapping(snapshot.get("policy_json"))
    rates_raw = _mapping(snapshot.get("rates_json"))
    reverse_raw = _mapping(snapshot.get("reverse_json"))
    equity = _equity_section(snapshot.get("equity_json"))
    evidence_raw = _mapping(snapshot.get("evidence_json"))
    freshness_raw = _mapping(snapshot.get("freshness_json"))
    warning_rows = _sequence(snapshot.get("warnings_json"))

    state_probabilities = _simplex(
        inflation_raw.get("state_probabilities"), field="inflation states"
    )
    state_rows = [
        {
            "id": state_id,
            "label": STATE_LABELS.get(state_id, state_id),
            "probability": state_probabilities.get(state_id, 0.0),
        }
        for state_id in STATE_LABELS
        if state_id in state_probabilities
    ]
    inflation = {
        "publication_status": _status(
            inflation_raw.get("publication_status"), default=publication_status
        ),
        "reason": _reason(
            inflation_raw.get("reason"), fallback="저장된 물가 경로를 사용합니다."
        ),
        "q4_quantiles_pct": {
            key: _finite(value, field=f"q4_quantiles_pct.{key}")
            for key, value in _mapping(
                inflation_raw.get("q4_quantiles_pct")
            ).items()
        },
        "state_probabilities": state_probabilities,
        "state_rows": state_rows,
        "threshold_probabilities": _probabilities(
            inflation_raw.get("threshold_probabilities"),
            field="inflation thresholds",
        ),
        "next_release_scenarios": _sequence(
            inflation_raw.get("next_release_scenarios")
        ),
        "state_definition": _mapping(inflation_raw.get("state_definition")),
    }
    policy = {
        "publication_status": _status(
            policy_raw.get("publication_status"), default=publication_status
        ),
        "reason": _reason(
            policy_raw.get("reason"), fallback="저장된 정책 경로를 사용합니다."
        ),
        "next_meeting_probabilities": _simplex(
            policy_raw.get("next_meeting_probabilities"), field="next meeting"
        ),
        "net_move_probabilities": _simplex(
            policy_raw.get("net_move_probabilities"), field="net policy moves"
        ),
        "year_end_target_probabilities": _simplex(
            policy_raw.get("year_end_target_probabilities"), field="year-end targets"
        ),
        "committee_vote_prior": _simplex(
            policy_raw.get("committee_vote_prior"), field="committee prior"
        ),
        "sep_net_move_prior": _simplex(
            policy_raw.get("sep_net_move_prior"), field="SEP prior"
        ),
    }
    ten_year = _mapping(rates_raw.get("DGS10"))
    instruments = _mapping(rates_raw.get("instruments"))
    if not instruments:
        instruments = {
            key: value
            for key, value in rates_raw.items()
            if key in {"DGS2", "DGS10", "DFII10", "T10YIE", "T10Y2Y", "ACMTP10"}
        }
    rates = {
        "publication_status": _status(
            rates_raw.get("publication_status"), default=publication_status
        ),
        "reason": _reason(
            rates_raw.get("reason"), fallback="저장된 금리 경로를 사용합니다."
        ),
        "ten_year": ten_year,
        "instruments": instruments,
        "driver_decomposition": _mapping(rates_raw.get("driver_decomposition")),
        "inflation_confirmation": _mapping(rates_raw.get("inflation_confirmation")),
        "term_premium_status": _status(
            rates_raw.get("term_premium_status"), default="NOT_AVAILABLE"
        ),
        "resistance_zones": _resistance_zones(rates_raw, definitions),
    }
    reverse = {
        **reverse_raw,
        "publication_status": _status(reverse_raw.get("publication_status")),
        "reason": _reason(
            reverse_raw.get("reason"),
            fallback="저장된 공동 경로가 없어 역산할 수 없습니다.",
        ),
    }
    dominant_state = max(state_rows, key=lambda item: item["probability"], default=None)
    run_kind = str(snapshot.get("run_kind") or "current")
    historical = run_kind == "historical_replay"
    if publication_status == "READY" and dominant_state:
        summary = (
            f"가장 큰 물가 상태는 {dominant_state['label']}입니다. "
            "다음 Core PCE와 정책·금리 확인 조건을 함께 보세요."
        )
    elif publication_status == "LIMITED":
        summary = (
            "저장된 경로는 있지만 검증이 제한적입니다. 숫자 확률은 현재 판단으로 "
            "승격하지 않고 필요한 다음 조건과 제한 사유를 먼저 표시합니다."
        )
    else:
        summary = "검증된 물가·정책·금리 경로를 아직 공개할 수 없습니다."
    model = {
        "schema_version": "inflation_policy_v1",
        "publication_status": publication_status,
        "as_of_at": snapshot.get("as_of_at"),
        "model_version": str(snapshot.get("model_version") or ""),
        "headline": {
            "title": "연말 Core PCE 경로와 정책·금리 조건",
            "summary": summary,
            "is_historical": historical,
            "history_label": "과거 기준" if historical else "현재 기준",
            "run_kind": run_kind,
        },
        "inflation": inflation,
        "policy": policy,
        "rates": rates,
        "reverse_scenario": reverse,
        "equity_stress": equity,
        "recession": {
            "publication_status": "NOT_AVAILABLE",
            "reason": "침체 모델은 5차 개발 전까지 연결하지 않습니다.",
        },
        "evidence": {
            "items": _sequence(evidence_raw.get("top_evidence")),
            "details": evidence_raw,
        },
        "freshness": freshness_raw,
        "warnings": [
            _reason(item, fallback="확인할 제한 사항이 있습니다.")
            for item in warning_rows
        ],
    }
    safe = _json_safe(model)
    json.dumps(safe, ensure_ascii=False, allow_nan=False)
    return safe  # type: ignore[return-value]


def _unavailable_model(*, status: str, summary: str) -> dict[str, object]:
    reason = "저장된 inflation-policy snapshot이 없습니다."
    model = {
        "schema_version": "inflation_policy_v1",
        "publication_status": status,
        "as_of_at": None,
        "model_version": "",
        "headline": {
            "title": "연말 Core PCE 경로와 정책·금리 조건",
            "summary": summary,
            "is_historical": False,
            "history_label": "현재 기준",
            "run_kind": "current",
        },
        "inflation": _empty_inflation(reason),
        "policy": _empty_policy(reason),
        "rates": _empty_rates(reason),
        "reverse_scenario": _empty_reverse(reason),
        "equity_stress": _empty_equity(
            "공식 S&P 500 EPS 빈티지와 검증된 공동 거시경로가 필요합니다."
        ),
        "recession": {
            "publication_status": "NOT_AVAILABLE",
            "reason": "침체 모델은 5차 개발 전까지 연결하지 않습니다.",
        },
        "evidence": {"items": [], "details": {}},
        "freshness": {},
        "warnings": [],
    }
    return model


def build_inflation_policy_read_model(
    *,
    as_of_at: str | datetime | None = None,
    snapshot_loader: SnapshotLoader | None = None,
    definitions_loader: DefinitionsLoader | None = None,
) -> dict[str, object]:
    """Adapt persisted results without fitting a model or calling a provider."""

    resolved_snapshot_loader = snapshot_loader or load_latest_inflation_policy_snapshot
    resolved_definitions_loader = definitions_loader or load_yield_resistance_definitions
    snapshot = resolved_snapshot_loader(as_of_at=as_of_at)
    if snapshot is None:
        return _unavailable_model(
            status="NOT_AVAILABLE",
            summary="저장된 물가·정책·금리 분석 결과가 아직 없습니다.",
        )
    try:
        definitions = resolved_definitions_loader(
            as_of_at=snapshot.get("as_of_at") or as_of_at
        )
        return _build_model(snapshot, definitions)
    except (TypeError, ValueError, json.JSONDecodeError):
        failed = _unavailable_model(
            status="FAILED",
            summary="저장된 확률 payload 검증에 실패해 숫자를 공개하지 않습니다.",
        )
        failed["as_of_at"] = _json_safe(snapshot.get("as_of_at"))
        failed["model_version"] = str(snapshot.get("model_version") or "")
        return failed
