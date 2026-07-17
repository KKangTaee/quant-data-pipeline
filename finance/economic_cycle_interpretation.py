"""Pure user-facing interpretation helpers for economic-cycle snapshots."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date, datetime

from finance.economic_cycle_asset_pathways import build_asset_pathway_contexts

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
        "orientations": {
            "activity_score": 1,
            "labor_income_score": 1,
            "financial_leading_score": 1,
            "inflation_policy_score": -1,
        },
        "change_condition": "생산·고용과 금융여건이 같은 방향으로 개선되고 물가 부담이 낮아지는지 확인합니다.",
    },
    "gold": {
        "label": "금",
        "price_symbol": "GC=F",
        "macro_signal_labels": {
            "FAVORABLE": "금을 지지",
            "BURDEN": "금에 부담",
            "MIXED": "금 신호 혼재",
            "INSUFFICIENT": "판단 자료 부족",
        },
        "orientations": {
            "activity_score": -1,
            "labor_income_score": -1,
            "financial_leading_score": -1,
            "inflation_policy_score": 1,
        },
        "change_condition": "경제 배경과 금 가격이 같은 방향으로 확인되는지 점검합니다.",
    },
    "dollar": {
        "label": "달러",
        "price_symbol": "DX-Y.NYB",
        "macro_signal_labels": {
            "FAVORABLE": "달러를 지지",
            "BURDEN": "달러에 부담",
            "MIXED": "달러 신호 혼재",
            "INSUFFICIENT": "판단 자료 부족",
        },
        "orientations": {
            "activity_score": 1,
            "labor_income_score": 1,
            "financial_leading_score": -1,
            "inflation_policy_score": 1,
        },
        "change_condition": "미국 성장·정책 배경과 달러인덱스 가격이 같은 방향인지 확인합니다.",
    },
    "commodities": {
        "label": "원자재",
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

PRICE_STATUS_LABELS = {
    "RISING": "상승 확인",
    "FALLING": "하락 확인",
    "MIXED": "방향 혼재",
    "UNAVAILABLE": "자료 부족",
}

ALIGNMENT_LABELS = {
    "ALIGNED": "배경과 가격 일치",
    "DIVERGENCE": "배경과 가격 불일치",
    "MIXED": "종합 혼재",
    "PRICE_PENDING": "가격 확인 대기",
}

CURRENT_ENVIRONMENT_LABELS = {
    "FAVORABLE": "지지 요인 우세",
    "BURDEN": "부담 요인 우세",
    "MIXED": "신호 혼재",
    "INSUFFICIENT": "자료 부족",
}

PRICE_DIRECTION_LABELS = {
    "RISING": "상승",
    "FALLING": "하락",
    "MIXED": "방향 혼재",
    "UNAVAILABLE": "확인 대기",
}

RELATIONSHIP_LABELS = {
    "ALIGNED": "같은 방향",
    "DIVERGENCE": "서로 다른 방향",
    "MIXED": "판단 유보",
    "PRICE_PENDING": "비교 대기",
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


def _join_driver_phrases(drivers: Sequence[Mapping[str, object]]) -> str:
    phrases = [
        f"{str(driver.get('label') or '').strip()} {str(driver.get('direction') or '').strip()}".strip()
        for driver in drivers
        if str(driver.get("label") or "").strip()
    ]
    if not phrases:
        return "확인 가능한 경제 근거"
    if len(phrases) == 1:
        return phrases[0]
    if len(phrases) == 2:
        return f"{phrases[0]}와 {phrases[1]}"
    return f"{', '.join(phrases[:-1])}와 {phrases[-1]}"


def _drivers_for_assessment(
    drivers: Sequence[dict[str, object]], assessment: str
) -> list[dict[str, object]]:
    if assessment == "FAVORABLE":
        selected = [driver for driver in drivers if driver["impact"] == "FAVORABLE"]
    elif assessment == "BURDEN":
        selected = [driver for driver in drivers if driver["impact"] == "BURDEN"]
    else:
        selected = list(drivers)
    return sorted(
        selected,
        key=lambda driver: abs(float(driver.get("value") or 0.0)),
        reverse=True,
    )


def _environment_summary(
    *,
    asset_label: str,
    assessment: str,
    drivers: Sequence[dict[str, object]],
) -> str:
    if assessment == "INSUFFICIENT":
        return "자산별 조건을 판정할 미국 경기 근거가 아직 부족합니다."
    selected = _drivers_for_assessment(drivers, assessment)
    if assessment == "MIXED":
        selected = _display_drivers(drivers, assessment=assessment)
        return (
            f"미국 경기지표에서는 {_join_driver_phrases(selected)}의 자산 영향이 "
            "엇갈려 현재 신호가 한 방향으로 모이지 않습니다."
        )
    direction = "지지" if assessment == "FAVORABLE" else "부담"
    return (
        f"미국 경기지표에서는 {_join_driver_phrases(selected)} 등 "
        f"{asset_label}에 {direction} 요인이 우세합니다."
    )


def _price_aware_summary(
    *,
    asset_group: str,
    assessment: str,
    drivers: Sequence[dict[str, object]],
    price_status: str,
    alignment: str,
) -> str:
    if assessment == "INSUFFICIENT":
        macro_phrase = "판정할 미국 경기 근거가 부족하고"
    elif assessment == "MIXED":
        macro_phrase = (
            f"{_join_driver_phrases(_display_drivers(drivers, assessment=assessment))}의 "
            "영향이 엇갈리고"
        )
    else:
        selected = _drivers_for_assessment(drivers, assessment)
        if asset_group == "gold":
            condition = "금을 지지하는" if assessment == "FAVORABLE" else "금에 부담인"
        else:
            condition = (
                "달러를 지지하는"
                if assessment == "FAVORABLE"
                else "달러에 부담이 되는"
            )
        macro_phrase = (
            f"{_join_driver_phrases(selected)} 등 {condition} 조건이 우세하지만"
        )

    price_subject = "실제 달러지수는" if asset_group == "dollar" else "실제 가격은"
    if price_status == "RISING":
        price_phrase = f"{price_subject} 최근 1개월과 3개월 모두 상승"
    elif price_status == "FALLING":
        price_phrase = f"{price_subject} 최근 1개월과 3개월 모두 하락"
    elif price_status == "MIXED":
        price_phrase = f"{price_subject} 기간별 방향이 엇갈려"
    else:
        return (
            f"미국 경기지표에서는 {macro_phrase}, 실제 가격 자료가 부족해 "
            "두 신호를 아직 비교할 수 없습니다."
        )

    if alignment == "ALIGNED":
        relationship_phrase = "해 두 신호가 같은 방향입니다."
    elif alignment == "DIVERGENCE":
        relationship_phrase = "해 두 신호가 엇갈립니다."
    else:
        relationship_phrase = "해 두 신호 관계의 판단을 유보합니다."
    return (
        f"미국 경기지표에서는 {macro_phrase}, {price_phrase}{relationship_phrase}"
    )


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


def _date_value(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return date.fromisoformat(str(value or "").strip()[:10])
    except ValueError:
        return None


def _unavailable_price_context(
    symbol: str,
    *,
    reason_code: str,
    as_of_date: date | None = None,
) -> dict[str, object]:
    return {
        "symbol": symbol,
        "as_of_date": as_of_date.isoformat() if as_of_date else None,
        "status": "UNAVAILABLE",
        "status_label": PRICE_STATUS_LABELS["UNAVAILABLE"],
        "reason_code": reason_code,
        "returns": {
            "one_week": None,
            "one_month": None,
            "three_months": None,
        },
        "source_basis": "stored continuous futures daily OHLCV",
    }


def _price_context(
    symbol: str,
    price_rows: Sequence[Mapping[str, object]],
    *,
    reference_date: object = None,
) -> dict[str, object]:
    by_date: dict[date, dict[str, object]] = {}
    for raw in price_rows:
        if str(raw.get("provider_symbol") or "").strip().upper() != symbol:
            continue
        candle_date = _date_value(raw.get("candle_time_utc"))
        try:
            close = float(raw.get("close"))
        except (TypeError, ValueError):
            continue
        if candle_date is None or close <= 0:
            continue
        by_date[candle_date] = {"date": candle_date, "close": close, **dict(raw)}

    ordered = [by_date[key] for key in sorted(by_date)]
    if not ordered:
        return _unavailable_price_context(symbol, reason_code="NOT_COLLECTED")
    latest_date = ordered[-1]["date"]
    if len(ordered) < 64:
        return _unavailable_price_context(
            symbol,
            reason_code="INSUFFICIENT_HISTORY",
            as_of_date=latest_date,
        )
    resolved_reference = _date_value(reference_date) or date.today()
    if (resolved_reference - latest_date).days >= 7:
        return _unavailable_price_context(
            symbol,
            reason_code="STALE",
            as_of_date=latest_date,
        )

    latest_close = float(ordered[-1]["close"])
    returns = {
        "one_week": latest_close / float(ordered[-6]["close"]) - 1.0,
        "one_month": latest_close / float(ordered[-22]["close"]) - 1.0,
        "three_months": latest_close / float(ordered[-64]["close"]) - 1.0,
    }
    if returns["one_month"] > 0.01 and returns["three_months"] > 0.01:
        status = "RISING"
    elif returns["one_month"] < -0.01 and returns["three_months"] < -0.01:
        status = "FALLING"
    else:
        status = "MIXED"
    return {
        "symbol": symbol,
        "as_of_date": latest_date.isoformat(),
        "status": status,
        "status_label": PRICE_STATUS_LABELS[status],
        "reason_code": None,
        "returns": returns,
        "source_basis": "stored continuous futures daily OHLCV",
    }


def _alignment(assessment: str, price_status: str) -> str:
    if price_status == "UNAVAILABLE":
        return "PRICE_PENDING"
    if assessment in {"MIXED", "INSUFFICIENT"} or price_status == "MIXED":
        return "MIXED"
    if (assessment, price_status) in {
        ("FAVORABLE", "RISING"),
        ("BURDEN", "FALLING"),
    }:
        return "ALIGNED"
    return "DIVERGENCE"


def build_market_implications(
    horizons: Sequence[Mapping[str, object]],
    evidence: Sequence[Mapping[str, object]],
    price_rows: Sequence[Mapping[str, object]] = (),
    *,
    market_rows: Sequence[Mapping[str, object]] = (),
    economic_as_of_date: object = None,
    price_reference_date: object = None,
) -> list[dict[str, object]]:
    """Expose measured paths without turning the cycle model into a causal claim."""

    del horizons  # The economic state is evidence-based, not phase-label driven.
    reference = (
        _date_value(price_reference_date)
        or _date_value(economic_as_of_date)
        or date.today()
    )
    pilot_contexts = build_asset_pathway_contexts(
        evidence=evidence,
        market_rows=market_rows,
        price_rows=price_rows,
        reference_date=reference,
    )
    economic_state = pilot_contexts["gold"]["economic_state"]
    labels = {
        "rates": "채권·금리",
        "equities": "주식",
        "gold": "금",
        "dollar": "달러",
        "commodities": "원자재",
    }
    implications: list[dict[str, object]] = []
    for asset_group in ("rates", "equities", "gold", "dollar", "commodities"):
        if asset_group in pilot_contexts:
            item = dict(pilot_contexts[asset_group])
            coverage = str(item["coverage"])
            item.update(
                {
                    "label": labels[asset_group],
                    "analysis_status": {
                        "SUFFICIENT": "READY",
                        "PARTIAL": "PARTIAL",
                        "INSUFFICIENT": "LIMITED",
                    }[coverage],
                    "summary": item["narrative"],
                    "context": item["narrative"],
                    "is_directional_forecast": False,
                }
            )
        else:
            narrative = (
                f"{economic_state['summary']} {labels[asset_group]}의 세부 시장경로는 "
                "아직 연결하지 않아 자산 방향으로 해석하지 않습니다."
            )
            item = {
                "asset_group": asset_group,
                "label": labels[asset_group],
                "analysis_status": "PATHWAYS_NOT_CONNECTED",
                "coverage": "INSUFFICIENT",
                "economic_state": economic_state,
                "pathways": [],
                "unmeasured_pathways": [
                    {
                        "pathway_id": f"{asset_group}_market_paths",
                        "label": "자산 내부 시장경로",
                        "reason_code": "PATHWAYS_NOT_CONNECTED",
                    }
                ],
                "narrative": narrative,
                "summary": narrative,
                "context": narrative,
                "is_directional_forecast": False,
            }
        implications.append(item)
    return implications
