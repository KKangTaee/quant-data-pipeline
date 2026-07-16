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

FACTOR_LABELS = {
    "activity_score": "생산·소비 활동",
    "labor_income_score": "고용·소득",
    "financial_leading_score": "금융·선행 여건",
    "inflation_policy_score": "물가·정책 압력",
}

ASSET_CONTEXT = {
    "rates": {
        "label": "채권·금리",
        "summary_subject": "채권의 금리 민감도",
        "orientations": {
            "activity_score": -1,
            "labor_income_score": -1,
            "financial_leading_score": -1,
            "inflation_policy_score": -1,
        },
        "change_condition": "물가·정책 압력과 금융여건이 낮아지거나 실물 방향이 반전되는지 확인합니다.",
    },
    "equities": {
        "label": "주식",
        "summary_subject": "주식 환경",
        "orientations": {
            "activity_score": 1,
            "labor_income_score": 1,
            "financial_leading_score": 1,
            "inflation_policy_score": -1,
        },
        "change_condition": "생산·고용과 금융여건이 같은 방향으로 개선되고 물가 부담이 낮아지는지 확인합니다.",
    },
    "gold_dollar": {
        "label": "금·달러",
        "summary_subject": "금·달러의 방어 맥락",
        "orientations": {
            "activity_score": -1,
            "labor_income_score": -1,
            "financial_leading_score": -1,
            "inflation_policy_score": 1,
        },
        "change_condition": "위험회피·실질금리·정책 불확실성 중 어느 신호가 우세해지는지 확인합니다.",
    },
    "commodities": {
        "label": "원자재",
        "summary_subject": "원자재 수요 환경",
        "orientations": {
            "activity_score": 1,
            "labor_income_score": 1,
            "financial_leading_score": 1,
            "inflation_policy_score": 1,
        },
        "change_condition": "실물 수요와 물가 압력이 같은 방향으로 이어지는지 확인합니다.",
    },
}

ASSESSMENT_LABELS = {
    "FAVORABLE": "우호",
    "BURDEN": "부담",
    "MIXED": "혼재",
    "INSUFFICIENT": "자료 부족",
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


def _factor_signal(value: object) -> int:
    """Return a stable -1/0/+1 signal using the public evidence threshold."""

    direction = evidence_direction(value)
    return {"약화": -1, "중립": 0, "강화": 1}[direction]


def _canonical_factor_evidence(
    evidence: Sequence[Mapping[str, object]],
) -> dict[str, Mapping[str, object]]:
    """Keep one strongest available row per canonical factor."""

    canonical: dict[str, Mapping[str, object]] = {}
    for row in evidence:
        factor = str(row.get("factor") or "")
        if factor not in FACTOR_LABELS:
            continue
        current = canonical.get(factor)
        try:
            magnitude = abs(float(row.get("value")))
        except (TypeError, ValueError):
            magnitude = 0.0
        try:
            current_magnitude = abs(float((current or {}).get("value")))
        except (TypeError, ValueError):
            current_magnitude = -1.0
        if current is None or magnitude > current_magnitude:
            canonical[factor] = row
    return canonical


def _assessment_summary(
    *,
    assessment: str,
    summary_subject: str,
    phase_label: str,
) -> str:
    if assessment == "FAVORABLE":
        return f"{phase_label} 국면의 현재 근거 조합은 {summary_subject}에 상대적으로 우호적입니다."
    if assessment == "BURDEN":
        return f"{phase_label} 국면의 현재 근거 조합은 {summary_subject}에 부담 요인이 우세합니다."
    if assessment == "MIXED":
        return f"{phase_label} 국면에서 우호와 부담 근거가 맞서 한 방향으로 읽기 어렵습니다."
    return "자산별 조건을 판정할 경제 근거가 아직 부족합니다."


def _display_drivers(
    drivers: Sequence[dict[str, object]],
    *,
    assessment: str,
) -> list[dict[str, object]]:
    ranked = sorted(
        drivers,
        key=lambda driver: abs(float(driver["value"] or 0.0)),
        reverse=True,
    )
    if assessment != "MIXED":
        return ranked[:2]
    favorable = next(
        (driver for driver in ranked if driver["impact"] == "FAVORABLE"),
        None,
    )
    burden = next(
        (driver for driver in ranked if driver["impact"] == "BURDEN"),
        None,
    )
    if favorable is not None and burden is not None:
        return [favorable, burden]
    return ranked[:2]


def build_market_implications(
    horizons: Sequence[Mapping[str, object]],
    evidence: Sequence[Mapping[str, object]],
) -> list[dict[str, object]]:
    """Translate cycle evidence into conditional asset context, not return forecasts."""

    phase = _dominant_forecast_phase(horizons)
    phase_label = {
        "recovery": "회복",
        "expansion": "확장",
        "slowdown": "둔화",
        "recession": "침체",
        "limited": "판단 제한",
    }.get(phase, "판단 제한")
    canonical = _canonical_factor_evidence(evidence)
    implications: list[dict[str, object]] = []

    for asset_group, config in ASSET_CONTEXT.items():
        orientations = config["orientations"]
        drivers = []
        for factor, row in canonical.items():
            signal = _factor_signal(row.get("value"))
            if signal == 0:
                continue
            impact_score = signal * int(orientations[factor])
            impact = "FAVORABLE" if impact_score > 0 else "BURDEN"
            direction = evidence_direction(row.get("value"))
            drivers.append(
                {
                    "factor": factor,
                    "label": FACTOR_LABELS[factor],
                    "direction": direction,
                    "impact": impact,
                    "impact_label": ASSESSMENT_LABELS[impact],
                    "text": (
                        f"{FACTOR_LABELS[factor]} {direction} · "
                        f"{ASSESSMENT_LABELS[impact]} 요인"
                    ),
                    "value": row.get("value"),
                }
            )

        favorable_count = sum(
            driver["impact"] == "FAVORABLE" for driver in drivers
        )
        burden_count = sum(driver["impact"] == "BURDEN" for driver in drivers)
        if len(drivers) < 2:
            assessment = "INSUFFICIENT"
            displayed_drivers: list[dict[str, object]] = []
            change_condition = (
                "서로 다른 경제 요인 2개 이상이 확보되면 자산별 조건을 판정합니다."
            )
        elif favorable_count >= burden_count + 2:
            assessment = "FAVORABLE"
            displayed_drivers = _display_drivers(drivers, assessment=assessment)
            change_condition = str(config["change_condition"])
        elif burden_count >= favorable_count + 2:
            assessment = "BURDEN"
            displayed_drivers = _display_drivers(drivers, assessment=assessment)
            change_condition = str(config["change_condition"])
        else:
            assessment = "MIXED"
            displayed_drivers = _display_drivers(drivers, assessment=assessment)
            change_condition = str(config["change_condition"])

        asset_label = str(config["label"])
        summary = _assessment_summary(
            assessment=assessment,
            summary_subject=str(config["summary_subject"]),
            phase_label=phase_label,
        )
        implications.append(
            {
                "asset_group": asset_group,
                "label": asset_label,
                "phase_context": phase_label,
                "assessment": assessment,
                "assessment_label": ASSESSMENT_LABELS[assessment],
                "summary": summary,
                "context": summary,
                "drivers": displayed_drivers,
                "change_condition": change_condition,
                "evidence_count": len(canonical),
                "is_directional_forecast": False,
            }
        )

    return implications
