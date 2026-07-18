"""Pure schema and validation contract for Level1 single-strategy settings."""

from __future__ import annotations

from copy import deepcopy
from datetime import date
from typing import Any, Mapping, Sequence


SETTINGS_SCHEMA_VERSION = "backtest_single_settings_workspace_v2"
ALLOWED_CONTROLS = frozenset(
    {
        "date",
        "number",
        "text",
        "single_select",
        "multi_select",
        "segmented",
        "toggle",
    }
)

SINGLE_SETTINGS_CONCRETE_KEYS: dict[str, tuple[str | None, ...]] = {
    "Equal Weight": (None,),
    "GTAA": (None,),
    "Global Relative Strength": (None,),
    "Risk Parity": (None,),
    "Dual Momentum": (None,),
    "Risk-On Momentum 5D": (None,),
    "Quality": ("Annual", "Quarterly", "Snapshot"),
    "Value": ("Annual", "Quarterly"),
    "Quality + Value": ("Annual", "Quarterly"),
}

_CONCRETE_STRATEGY_KEYS: dict[tuple[str, str | None], str] = {
    ("Equal Weight", None): "equal_weight",
    ("GTAA", None): "gtaa",
    ("Global Relative Strength", None): "global_relative_strength",
    ("Risk Parity", None): "risk_parity_trend",
    ("Dual Momentum", None): "dual_momentum",
    ("Risk-On Momentum 5D", None): "risk_on_momentum_5d",
    ("Quality", "Annual"): "quality_snapshot_strict_annual",
    ("Quality", "Quarterly"): "quality_snapshot_strict_quarterly_prototype",
    ("Quality", "Snapshot"): "quality_snapshot",
    ("Value", "Annual"): "value_snapshot_strict_annual",
    ("Value", "Quarterly"): "value_snapshot_strict_quarterly_prototype",
    ("Quality + Value", "Annual"): "quality_value_snapshot_strict_annual",
    (
        "Quality + Value",
        "Quarterly",
    ): "quality_value_snapshot_strict_quarterly_prototype",
}

_PROFILES: dict[str, dict[str, str]] = {
    "Equal Weight": {
        "display_name": "Equal Weight",
        "purpose_label": "분산·기본 포트폴리오",
        "maturity_label": "운영 전략",
        "description": "선택한 자산을 같은 비중으로 보유하고 정해진 주기로 조정합니다.",
        "selection_rule": "지정한 투자 대상 전체를 같은 비중으로 선택합니다.",
        "holding_rule": "설정한 리밸런싱 간격마다 목표 비중으로 되돌립니다.",
        "risk_note": "투자 대상 구성과 거래비용이 결과에 직접 영향을 줍니다.",
    },
    "GTAA": {
        "display_name": "GTAA",
        "purpose_label": "모멘텀·전술 자산배분",
        "maturity_label": "운영 전략",
        "description": "자산군의 상대강도와 추세를 함께 비교해 공격·방어 자산을 선택합니다.",
        "selection_rule": "여러 관찰 기간의 수익률과 추세 기준으로 상위 자산을 고릅니다.",
        "holding_rule": "정해진 신호 갱신 주기마다 순위와 방어 전환 여부를 다시 계산합니다.",
        "risk_note": "점수 기간, 추세선, 방어 규칙을 함께 확인해야 합니다.",
    },
    "Global Relative Strength": {
        "display_name": "Global Relative Strength",
        "purpose_label": "글로벌 상대강도",
        "maturity_label": "운영 전략",
        "description": "글로벌 자산의 상대 성과를 비교해 강한 자산을 보유합니다.",
        "selection_rule": "설정한 관찰 기간의 상대강도 상위 자산을 선택합니다.",
        "holding_rule": "신호 갱신 시 순위를 다시 계산하고 필요하면 현금성 자산으로 이동합니다.",
        "risk_note": "관찰 기간과 추세 필터가 교체 빈도와 낙폭에 영향을 줍니다.",
    },
    "Risk Parity": {
        "display_name": "Risk Parity",
        "purpose_label": "위험 균형 자산배분",
        "maturity_label": "운영 전략",
        "description": "자산별 변동성을 반영해 위험 기여도를 균형 있게 배분합니다.",
        "selection_rule": "선택한 자산의 변동성과 추세 조건을 함께 확인합니다.",
        "holding_rule": "변동성 추정치와 리밸런싱 주기에 따라 목표 비중을 갱신합니다.",
        "risk_note": "변동성 관찰 기간과 거래비용 가정에 민감합니다.",
    },
    "Dual Momentum": {
        "display_name": "Dual Momentum",
        "purpose_label": "절대·상대 모멘텀",
        "maturity_label": "운영 전략",
        "description": "상대적으로 강하면서 절대 추세도 양호한 자산을 선택합니다.",
        "selection_rule": "상대 순위와 기준 자산 대비 절대 모멘텀을 함께 적용합니다.",
        "holding_rule": "신호 주기마다 상위 자산과 방어 자산 전환 여부를 갱신합니다.",
        "risk_note": "급격한 추세 반전에서는 신호 지연이 발생할 수 있습니다.",
    },
    "Risk-On Momentum 5D": {
        "display_name": "Risk-On Momentum 5D",
        "purpose_label": "단기 위험선호 모멘텀",
        "maturity_label": "개발 중 전략",
        "description": "단기 모멘텀과 시장 위험선호 조건을 결합한 개발 단계 전략입니다.",
        "selection_rule": "가격·유동성·거시 필터를 통과한 단기 모멘텀 후보를 선택합니다.",
        "holding_rule": "진입·청산·손절·익절 규칙으로 포지션을 관리합니다.",
        "risk_note": "개발 중이므로 Level2 후보 승격 전에 실행 근거를 더 검토해야 합니다.",
    },
    "Quality": {
        "display_name": "Quality",
        "purpose_label": "기업 품질 팩터",
        "maturity_label": "검증 전략",
        "description": "재무 품질 근거가 충분한 기업을 선별합니다.",
        "selection_rule": "point-in-time 재무지표와 품질 팩터를 결합해 상위 종목을 고릅니다.",
        "holding_rule": "재무 공시 주기와 월별 universe 기준에 맞춰 후보를 갱신합니다.",
        "risk_note": "재무 데이터 시점과 coverage 부족 종목 처리 기준을 확인해야 합니다.",
    },
    "Value": {
        "display_name": "Value",
        "purpose_label": "기업 가치 팩터",
        "maturity_label": "검증 전략",
        "description": "가격 대비 기업가치가 낮은 후보를 point-in-time 기준으로 선별합니다.",
        "selection_rule": "복수 가치 팩터와 데이터 coverage를 결합해 상위 종목을 고릅니다.",
        "holding_rule": "재무 공시와 월별 universe 변화에 맞춰 후보를 다시 평가합니다.",
        "risk_note": "가치 함정과 데이터 결측 처리 기준을 함께 확인해야 합니다.",
    },
    "Quality + Value": {
        "display_name": "Quality + Value",
        "purpose_label": "품질·가치 복합 팩터",
        "maturity_label": "검증 전략",
        "description": "재무 품질과 가격 매력을 함께 만족하는 기업을 선별합니다.",
        "selection_rule": "품질·가치 팩터와 coverage 기준을 결합해 최종 후보를 고릅니다.",
        "holding_rule": "공시 시점과 월별 universe 기준에 맞춰 복합 점수를 갱신합니다.",
        "risk_note": "팩터 균형과 결측 종목 대체 규칙을 함께 확인해야 합니다.",
    },
}

_SECTION_METADATA = {
    "execution": (
        "핵심 실행 설정",
        "검증 기간과 결과를 다시 계산하는 기본 주기를 정합니다.",
    ),
    "universe": (
        "투자 대상 Universe",
        "전략이 실제로 비교하고 선택할 자산 범위를 정합니다.",
    ),
    "rules": (
        "선택·보유 규칙",
        "어떤 후보를 선택하고 언제 교체할지 정합니다.",
    ),
    "risk": (
        "비용·위험 기준",
        "실행 비용과 결과를 제한하는 위험 기준을 정합니다.",
    ),
}

_VARIANT_LABELS = {
    "Annual": "연간 재무 기준",
    "Quarterly": "분기 재무 기준",
    "Snapshot": "기존 스냅샷",
}


class SettingsValidationError(ValueError):
    """Raised when a submitted settings draft cannot become an execution payload."""

    def __init__(self, errors: Mapping[str, str]):
        self.errors = dict(errors)
        super().__init__("설정값을 확인해 주세요.")


def _option(value: object, label: str | None = None) -> dict[str, object]:
    return {"value": deepcopy(value), "label": label or str(value)}


def _field(
    field_id: str,
    payload_key: str,
    label: str,
    control: str,
    default: object,
    help_text: str,
    **metadata: object,
) -> dict[str, object]:
    if control not in ALLOWED_CONTROLS:
        raise ValueError(f"지원하지 않는 설정 control입니다: {control}")
    result: dict[str, object] = {
        "field_id": field_id,
        "payload_key": payload_key,
        "label": label,
        "control": control,
        "value": deepcopy(default),
        "required": bool(metadata.pop("required", True)),
        "help": help_text,
    }
    result.update({key: deepcopy(value) for key, value in metadata.items()})
    return result


def _section(section_id: str, fields: Sequence[Mapping[str, object]]) -> dict[str, object]:
    title, description = _SECTION_METADATA[section_id]
    return {
        "section_id": section_id,
        "title": title,
        "description": description,
        "fields": [deepcopy(dict(item)) for item in fields],
        "disclosures": [],
    }


def _runtime_sequence(
    runtime_options: Mapping[str, object],
    key: str,
    fallback: Sequence[object],
) -> list[object]:
    candidate = runtime_options.get(key)
    if isinstance(candidate, Sequence) and not isinstance(candidate, (str, bytes)):
        return list(candidate)
    return list(fallback)


def _preset_catalog(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> dict[str, list[str]]:
    all_presets = runtime_options.get("presets")
    if not isinstance(all_presets, Mapping):
        return {"기본 구성": []}
    strategy_presets = all_presets.get(strategy_choice)
    if not isinstance(strategy_presets, Mapping):
        return {"기본 구성": []}
    return {
        str(name): [str(ticker) for ticker in members]
        for name, members in strategy_presets.items()
        if isinstance(members, Sequence) and not isinstance(members, (str, bytes))
    } or {"기본 구성": []}


def _base_sections(
    strategy_choice: str,
    runtime_options: Mapping[str, object],
) -> list[dict[str, object]]:
    presets = _preset_catalog(strategy_choice, runtime_options)
    preset_names = list(presets)
    tickers = [str(value) for value in _runtime_sequence(runtime_options, "tickers", [])]
    benchmarks = [
        str(value)
        for value in _runtime_sequence(runtime_options, "benchmarks", ["SPY"])
    ]
    benchmark_default = benchmarks[0] if benchmarks else "SPY"

    execution = [
        _field(
            "start",
            "start",
            "검증 시작일",
            "date",
            "2016-01-01",
            "전략 계산을 시작할 날짜입니다.",
        ),
        _field(
            "end",
            "end",
            "검증 종료일",
            "date",
            "2026-07-18",
            "전략 계산에 포함할 마지막 날짜입니다.",
        ),
        _field(
            "rebalance_interval",
            "rebalance_interval",
            "리밸런싱 간격(개월)",
            "number",
            12,
            "선택 비중을 다시 맞추는 개월 간격입니다.",
            min=1,
            max=120,
            step=1,
        ),
    ]
    universe = [
        _field(
            "universe_mode",
            "universe_mode",
            "투자 대상 선택 방식",
            "segmented",
            "preset",
            "기본 구성 또는 직접 입력 중 하나를 선택합니다.",
            options=[_option("preset", "기본 구성"), _option("manual", "직접 입력")],
        ),
        _field(
            "preset_name",
            "preset_name",
            "기본 구성",
            "single_select",
            preset_names[0],
            "검증 목적에 맞는 기본 자산 구성을 선택합니다.",
            options=[_option(name) for name in preset_names],
            visible_when={"universe_mode": "preset"},
        ),
        _field(
            "tickers",
            "tickers",
            "직접 입력할 종목",
            "multi_select",
            [],
            "직접 검증할 종목을 하나 이상 선택합니다.",
            options=[_option(ticker) for ticker in tickers],
            visible_when={"universe_mode": "manual"},
        ),
    ]
    rules = [
        _field(
            "timeframe",
            "timeframe",
            "가격 계산 주기",
            "single_select",
            "1Day",
            "일별 가격을 기준으로 전략 신호를 계산합니다.",
            options=[_option("1Day", "일별")],
            advanced=True,
        )
    ]
    risk = [
        _field(
            "transaction_cost_bps",
            "transaction_cost_bps",
            "거래비용(bps)",
            "number",
            10.0,
            "매매 때 반영할 편도 거래비용 가정입니다.",
            min=0.0,
            max=500.0,
            step=1.0,
        ),
        _field(
            "benchmark_ticker",
            "benchmark_ticker",
            "비교 기준 자산",
            "single_select",
            benchmark_default,
            "전략 결과와 비교할 대표 자산입니다.",
            options=[_option(value) for value in benchmarks] or [_option("SPY")],
        ),
    ]
    return [
        _section("execution", execution),
        _section("universe", universe),
        _section("rules", rules),
        _section("risk", risk),
    ]


def _normalized_variant(strategy_choice: str, variant: str | None) -> str | None:
    if strategy_choice not in SINGLE_SETTINGS_CONCRETE_KEYS:
        raise ValueError(f"알 수 없는 전략입니다: {strategy_choice}")
    allowed_variants = SINGLE_SETTINGS_CONCRETE_KEYS[strategy_choice]
    if variant not in allowed_variants:
        raise ValueError(
            f"{strategy_choice}에서 사용할 수 없는 variant입니다: {variant}"
        )
    return variant


def _all_fields(workspace: Mapping[str, object]) -> list[dict[str, object]]:
    sections = workspace.get("sections")
    if not isinstance(sections, Sequence):
        return []
    fields: list[dict[str, object]] = []
    for section in sections:
        if not isinstance(section, Mapping):
            continue
        section_fields = section.get("fields")
        if not isinstance(section_fields, Sequence):
            continue
        fields.extend(dict(item) for item in section_fields if isinstance(item, Mapping))
    return fields


def _effective_values(
    workspace: Mapping[str, object],
    submitted: Mapping[str, object],
) -> dict[str, object]:
    effective = {
        str(field["field_id"]): deepcopy(field.get("value"))
        for field in _all_fields(workspace)
    }
    effective.update({str(key): deepcopy(value) for key, value in submitted.items()})
    return effective


def _is_visible(field: Mapping[str, object], values: Mapping[str, object]) -> bool:
    visible_when = field.get("visible_when")
    if not isinstance(visible_when, Mapping):
        return True
    return all(values.get(str(key)) == expected for key, expected in visible_when.items())


def _option_values(field: Mapping[str, object]) -> list[object]:
    options = field.get("options")
    if not isinstance(options, Sequence) or isinstance(options, (str, bytes)):
        return []
    values = []
    for option in options:
        if isinstance(option, Mapping) and "value" in option:
            values.append(option["value"])
        else:
            values.append(option)
    return values


def _value_error(field: Mapping[str, object], value: object) -> str | None:
    if bool(field.get("required", True)) and (
        value is None or value == "" or value == []
    ):
        return "필수 설정입니다."

    control = str(field.get("control") or "")
    if value is None:
        return None
    if control == "date":
        if not isinstance(value, str):
            return "날짜 형식으로 입력해 주세요."
        try:
            date.fromisoformat(value)
        except ValueError:
            return "YYYY-MM-DD 날짜 형식으로 입력해 주세요."
    elif control == "number":
        if isinstance(value, bool) or not isinstance(value, (int, float)):
            return "숫자로 입력해 주세요."
        minimum = field.get("min")
        maximum = field.get("max")
        if isinstance(minimum, (int, float)) and value < minimum:
            return f"최솟값 {minimum} 이상이어야 합니다."
        if isinstance(maximum, (int, float)) and value > maximum:
            return f"최댓값 {maximum} 이하여야 합니다."
    elif control in {"single_select", "segmented"}:
        if not isinstance(value, (str, int, float)) or isinstance(value, bool):
            return "선택 항목 형식으로 입력해 주세요."
        allowed = _option_values(field)
        if allowed and value not in allowed:
            return "선택할 수 없는 값입니다."
    elif control == "multi_select":
        if not isinstance(value, list):
            return "여러 항목은 목록으로 입력해 주세요."
        if len(value) != len({repr(item) for item in value}):
            return "중복 항목은 한 번만 선택해 주세요."
        allowed = _option_values(field)
        if allowed and any(item not in allowed for item in value):
            return "선택할 수 없는 값이 포함되어 있습니다."
    elif control == "toggle":
        if not isinstance(value, bool):
            return "켜기 또는 끄기로 선택해 주세요."
    elif control == "text" and not isinstance(value, str):
        return "문자열로 입력해 주세요."
    return None


def build_single_settings_workspace(
    strategy_choice: str,
    variant: str | None,
    values: Mapping[str, object] | None,
    runtime_options: Mapping[str, object] | None,
) -> dict[str, object]:
    """Build a JSON-ready settings read model without importing web/runtime modules."""

    normalized_variant = _normalized_variant(strategy_choice, variant)
    runtime = dict(runtime_options or {})
    sections = _base_sections(strategy_choice, runtime)
    workspace: dict[str, object] = {
        "schema_version": SETTINGS_SCHEMA_VERSION,
        "strategy_choice": strategy_choice,
        "concrete_strategy_key": _CONCRETE_STRATEGY_KEYS[
            (strategy_choice, normalized_variant)
        ],
        "draft_key": f"{strategy_choice}:{normalized_variant or 'default'}",
        "profile": deepcopy(_PROFILES[strategy_choice]),
        "variant": {
            "value": normalized_variant,
            "options": [
                {
                    "value": item,
                    "label": _VARIANT_LABELS.get(str(item), str(item)),
                }
                for item in SINGLE_SETTINGS_CONCRETE_KEYS[strategy_choice]
                if item is not None
            ],
        },
        "sections": sections,
        "evidence": {
            "universe_summary": "투자 대상 구성을 선택해 검증 범위를 고정합니다.",
            "universe_full_text": "",
            "technical_rows": [],
        },
        "action": {
            "id": "run_single_strategy",
            "label": "이 설정으로 백테스트 실행",
            "enabled": True,
        },
        "validation_errors": {},
        "payload_constants": {
            "strategy_key": _CONCRETE_STRATEGY_KEYS[
                (strategy_choice, normalized_variant)
            ],
            "option": "backtest",
        },
    }
    supplied = dict(values or {})
    for field in _all_fields(workspace):
        field_id = str(field["field_id"])
        if field_id in supplied:
            field["value"] = deepcopy(supplied[field_id])
    return deepcopy(workspace)


def validate_single_settings_draft(
    workspace: Mapping[str, object],
    values: Mapping[str, object] | None,
) -> dict[str, str]:
    """Validate submitted fields before any runner or persistence boundary is reached."""

    submitted = {str(key): value for key, value in dict(values or {}).items()}
    fields = _all_fields(workspace)
    field_by_id = {str(field["field_id"]): field for field in fields}
    effective = _effective_values(workspace, submitted)
    errors: dict[str, str] = {}

    for field_id in submitted:
        if field_id not in field_by_id:
            errors[field_id] = "허용되지 않은 설정입니다."

    for field_id, field in field_by_id.items():
        visible = _is_visible(field, effective)
        if field_id in submitted and not visible:
            errors[field_id] = "현재 조건에서는 사용할 수 없는 설정입니다."
            continue
        if not visible:
            continue
        message = _value_error(field, effective.get(field_id))
        if message:
            errors[field_id] = message
    return errors


def project_single_settings_payload(
    workspace: Mapping[str, object],
    values: Mapping[str, object] | None,
) -> dict[str, object]:
    """Project only validated visible fields and Python-owned constants into a payload."""

    submitted = dict(values or {})
    errors = validate_single_settings_draft(workspace, submitted)
    if errors:
        raise SettingsValidationError(errors)

    effective = _effective_values(workspace, submitted)
    payload_constants = workspace.get("payload_constants")
    payload: dict[str, object] = (
        deepcopy(dict(payload_constants))
        if isinstance(payload_constants, Mapping)
        else {}
    )
    for field in _all_fields(workspace):
        if not _is_visible(field, effective):
            continue
        field_id = str(field["field_id"])
        payload_key = str(field["payload_key"])
        payload[payload_key] = deepcopy(effective.get(field_id))
    return payload


__all__ = [
    "ALLOWED_CONTROLS",
    "SETTINGS_SCHEMA_VERSION",
    "SINGLE_SETTINGS_CONCRETE_KEYS",
    "SettingsValidationError",
    "build_single_settings_workspace",
    "project_single_settings_payload",
    "validate_single_settings_draft",
]
