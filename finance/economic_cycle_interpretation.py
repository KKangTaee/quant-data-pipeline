"""Pure user-facing interpretation helpers for economic-cycle snapshots."""

from __future__ import annotations

from collections.abc import Mapping, Sequence

REASON_LABELS = {
    "NOT_COLLECTED": "필수 지표가 아직 수집되지 않았습니다.",
    "STALE": "일부 지표의 최신성이 부족합니다.",
    "VINTAGE_GAP": "당시 공개본을 재현할 빈티지가 부족합니다.",
    "VALIDATION_FAILED": "해당 전망 지평이 검증 기준을 통과하지 못했습니다.",
    "PARTIAL_FACTORS": "국면 판단에 필요한 요인 일부가 비어 있습니다.",
    "READ_ERROR": "저장된 경제사이클 결과를 읽지 못했습니다.",
    "NOT_MATERIALIZED": "아직 계산·저장된 경제사이클 결과가 없습니다.",
    "MISSING_APPROVED_HORIZON": "승인된 지평별 결과가 없습니다.",
    "MISSING_GATE_METADATA": "검증 근거가 완전하지 않습니다.",
    "INSUFFICIENT_ORIGINS": "검증에 사용할 과거 예측 원점이 부족합니다.",
    "INSUFFICIENT_RECESSION_EPISODES": "침체 구간 검증 표본이 부족합니다.",
    "INSUFFICIENT_PHASE_SUPPORT": "일부 국면의 검증 표본이 부족합니다.",
    "LOW_FEATURE_COVERAGE": "지표 커버리지가 공개 기준보다 낮습니다.",
    "CALIBRATION_ERROR": "확률 보정 오차가 공개 기준을 넘었습니다.",
    "INVALID_PROBABILITIES": "확률 결과의 완결성을 확인하지 못했습니다.",
    "BASELINE_UNDERPERFORMANCE": "단순 기준모형보다 확률 품질이 낮습니다.",
    "MISSING_PHASE_SUPPORT": "일부 국면의 학습 표본이 없어 확률을 계산할 수 없습니다.",
    "MODEL_NOT_SCORABLE": "모델 파라미터가 완전하지 않아 확률을 계산할 수 없습니다.",
    "MODEL_INPUT_UNAVAILABLE": "현재 입력 지표가 부족해 확률을 계산할 수 없습니다.",
}


def translate_reason_code(reason_code: object) -> str:
    """Translate stable machine codes without leaking internal exceptions."""

    code = str(reason_code or "PARTIAL_FACTORS").strip().upper()
    return REASON_LABELS.get(code, "현재 결과를 제한적으로만 해석할 수 있습니다.")


def evidence_direction(value: object) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "중립"
    if numeric > 0.15:
        return "강화"
    if numeric < -0.15:
        return "약화"
    return "중립"


def evidence_group(factor: object) -> str:
    normalized = str(factor or "").lower()
    if "activity" in normalized or "labor" in normalized or "income" in normalized:
        return "real_economy"
    return "forecast_context"


def _dominant_forecast_phase(horizons: Sequence[Mapping[str, object]]) -> str:
    for preferred in (2, 1, 0):
        item = next(
            (
                row
                for row in horizons
                if int(row.get("horizon_months") or 0) == preferred
            ),
            None,
        )
        phase = str((item or {}).get("dominant_phase") or "")
        if phase:
            return phase
    return "limited"


def build_market_implications(
    horizons: Sequence[Mapping[str, object]],
    evidence: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Describe conditional cross-asset context without predicting returns."""

    phase = _dominant_forecast_phase(horizons)
    phase_label = {
        "recovery": "회복",
        "expansion": "확장",
        "slowdown": "둔화",
        "recession": "침체",
        "limited": "판단 제한",
    }.get(phase, "판단 제한")
    context = {
        "rates": "성장·물가·정책 신호가 함께 확인되는 조건에서 금리 민감도를 점검합니다.",
        "equities": "이익 성장과 할인율이 같은 방향인지 확인하는 조건부 주식 맥락입니다.",
        "gold_dollar": "실질금리와 위험회피 신호가 겹치는 조건에서 금·달러 맥락을 봅니다.",
        "commodities": "실물 수요와 공급 충격이 함께 나타나는 조건에서 원자재 맥락을 봅니다.",
    }
    labels = {
        "rates": "금리",
        "equities": "주식",
        "gold_dollar": "금·달러",
        "commodities": "원자재",
    }
    evidence_count = len(list(evidence))
    return [
        {
            "asset_group": asset_group,
            "label": labels[asset_group],
            "phase_context": phase_label,
            "context": text,
            "evidence_count": evidence_count,
            "is_directional_forecast": False,
        }
        for asset_group, text in context.items()
    ]
