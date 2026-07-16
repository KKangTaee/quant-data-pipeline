from __future__ import annotations

import re
from typing import Any


PRACTICAL_VALIDATION_EVIDENCE_CATEGORIES: tuple[dict[str, Any], ...] = (
    {
        "category_id": "data_and_bias",
        "title": "데이터와 편향 통제",
        "question": "검증 기간과 ETF 근거가 실제 판단에 사용할 만큼 충분한가?",
        "audit_keys": ("data_coverage_audit",),
        "group_tokens": ("source", "data quality", "data coverage"),
    },
    {
        "category_id": "validation_method",
        "title": "검증 방법",
        "question": "특정 한 기간이 아니라 여러 구간에서도 결과가 유지되는가?",
        "audit_keys": ("validation_efficacy_audit",),
        "group_tokens": ("validation method", "validation efficacy"),
    },
    {
        "category_id": "portfolio_structure",
        "title": "포트폴리오 구성",
        "question": "비중·중복·위험 기여가 한 구성요소에 과도하게 집중되지 않았는가?",
        "audit_keys": (
            "construction_risk_audit",
            "risk_contribution_audit",
            "component_role_weight_audit",
        ),
        "group_tokens": ("construction", "risk contribution", "component role"),
    },
    {
        "category_id": "realism_and_cost",
        "title": "실전 운용 현실성",
        "question": "거래비용·유동성·세금 조건을 고려해도 해석 가능한 결과인가?",
        "audit_keys": ("backtest_realism_audit",),
        "group_tokens": ("backtest realism", "operability", "tax"),
    },
    {
        "category_id": "stress_and_robustness",
        "title": "스트레스와 강건성",
        "question": "시장 충격과 설정 변화에서도 결과가 과도하게 무너지지 않는가?",
        "audit_keys": ("robustness_validation",),
        "group_tokens": ("stress", "robustness", "sensitivity"),
    },
)


_PRESENTATION: dict[str, tuple[str, str, str]] = {
    "Walk-forward temporal validation": (
        "기간을 이동한 반복 검증",
        "검증 구간을 순차적으로 옮겨 특정 한 시기에만 좋은 결과인지 확인했습니다.",
        "기간별 비교 기준 하회가 반복되면 특정 시장 구간에 의존했을 가능성이 있습니다.",
    ),
    "Regime split validation": (
        "시장 국면별 성과 검증",
        "상승·중립·약세 같은 시장 환경으로 나눠 취약한 국면이 있는지 확인했습니다.",
        "국면별 차이는 후보가 약해지는 환경과 Monitoring 기준을 정하는 근거입니다.",
    ),
    "OOS holdout validation": (
        "학습 구간 밖 성과 검증",
        "전략을 구성할 때 사용하지 않은 별도 기간에서도 성과가 유지되는지 확인했습니다.",
        "별도 기간 결과가 유지되면 과거 데이터에만 맞춘 가능성이 낮아집니다.",
    ),
    "Universe / listing evidence": (
        "과거 종목 목록과 상장 이력",
        "현재 종목뿐 아니라 검증 시점에 실제로 존재했던 종목과 상장 기간을 반영했는지 확인했습니다.",
        "과거 종목 이력이 불완전하면 현재 살아남은 종목에 유리한 성과가 만들어질 수 있습니다.",
    ),
    "Survivorship / delisting control": (
        "상장폐지 종목과 생존편향 통제",
        "상장폐지 종목을 포함해 현재까지 살아남은 종목만 보는 편향을 통제했는지 확인했습니다.",
        "상장폐지 이력이 빠지면 백테스트 성과가 실제보다 좋아 보일 수 있습니다.",
    ),
    "Provider snapshot freshness": (
        "ETF·외부 데이터 최신성",
        "ETF 비용·운용성·보유 종목 자료의 기준일이 현재 판단에 충분히 가까운지 확인했습니다.",
        "오래된 자료는 현재 거래 조건과 실제 ETF 구성을 설명하는 확신을 낮춥니다.",
    ),
    "Provider / freshness evidence": (
        "ETF·외부 데이터 최신성",
        "ETF 비용·운용성·보유 종목 자료의 범위와 기준일을 확인했습니다.",
        "오래되거나 누락된 자료는 현재 운용 가능성을 보수적으로 보게 합니다.",
    ),
    "Cost / slippage sensitivity evidence": (
        "거래비용 변화 민감도",
        "수수료와 체결 오차를 높였을 때에도 결과 해석이 유지되는지 확인했습니다.",
        "비용 가정을 바꿨을 때 성과가 크게 달라지면 실전 성과의 불확실성이 커집니다.",
    ),
    "Transaction cost model": (
        "거래비용 반영 방식",
        "백테스트 결과에 수수료와 체결 오차가 실제 순성과로 반영되는지 확인했습니다.",
        "비용이 결과 곡선에 반영돼야 백테스트 수익률을 실전 기대치와 비교할 수 있습니다.",
    ),
    "Net cost curve proof": (
        "비용 차감 후 성과 곡선",
        "거래비용을 차감한 값이 최종 수익률과 자산 곡선에 실제로 연결되는지 확인했습니다.",
        "비용 차감 전 결과만 보면 실전에서 기대할 수 있는 성과를 과대평가할 수 있습니다.",
    ),
    "Storage / execution boundary": (
        "검증 중 저장·실행 안전 경계",
        "검증 과정이 DB·registry·실거래 승인 상태를 변경하지 않는 읽기 전용 경계인지 확인했습니다.",
        "읽기 전용 검증이어야 결과 확인 과정에서 운영 데이터나 승인 상태가 바뀌지 않습니다.",
    ),
    "Top holding concentration": (
        "상위 보유 종목 집중도",
        "ETF 내부의 한 종목이 포트폴리오 위험을 과도하게 좌우하는지 확인했습니다.",
        "상위 종목 비중이 크면 ETF가 여러 개여도 실제 분산 효과가 제한될 수 있습니다.",
    ),
    "Holdings overlap": (
        "ETF 간 보유 종목 중복",
        "서로 다른 ETF가 같은 종목을 반복 보유하는 비중을 확인했습니다.",
        "보유 종목 중복이 크면 상품 수와 달리 실제 분산 효과가 약해질 수 있습니다.",
    ),
    "Asset bucket exposure": (
        "자산군 노출 집중도",
        "주식·채권·원자재 등 자산군별 실제 노출이 한쪽에 과도하게 집중됐는지 확인했습니다.",
        "특정 자산군 의존도가 높으면 해당 시장 환경에서 포트폴리오 전체가 함께 흔들릴 수 있습니다.",
    ),
    "Provider look-through coverage": (
        "ETF 내부 구성 확인 범위",
        "ETF 내부 보유 종목과 자산군 노출을 실제 자료로 얼마나 확인했는지 측정했습니다.",
        "확인하지 못한 비중만큼 실제 집중도와 중복 보유를 과소평가할 수 있습니다.",
    ),
    "Tax / Account Scope": (
        "세금·계좌 조건 반영 범위",
        "세금과 계좌 유형에 따라 달라지는 실현 성과를 현재 검증이 어디까지 반영했는지 확인했습니다.",
        "세금과 계좌 조건을 반영하지 않은 성과는 실제 사용자 계좌에서 달라질 수 있습니다.",
    ),
    "Tax / account scope": (
        "세금·계좌 조건 반영 범위",
        "세금과 계좌 유형에 따라 달라지는 실현 성과를 현재 검증이 어디까지 반영했는지 확인했습니다.",
        "세금과 계좌 조건을 반영하지 않은 성과는 실제 사용자 계좌에서 달라질 수 있습니다.",
    ),
    "Component weight concentration": (
        "구성 비중 집중도",
        "한 전략 또는 구성요소가 포트폴리오 전체 비중을 지배하는지 확인했습니다.",
        "단일 구성 후보라면 혼합 포트폴리오의 비중 집중 검증은 적용 대상이 아닙니다.",
    ),
    "Relative Strength perturbation": (
        "모멘텀 기간 변경 검증",
        "모멘텀 계산 기간을 바꿔도 결과가 과도하게 흔들리지 않는지 확인합니다.",
        "검증 결과가 없으면 현재 설정값에 대한 의존도를 판단할 수 없습니다.",
    ),
    "GTAA parameter perturbation": (
        "GTAA 설정 변경 검증",
        "리밸런싱 주기와 핵심 설정을 바꿔도 결과가 유지되는지 확인합니다.",
        "검증 결과가 없으면 현재 리밸런싱 규칙에 대한 의존도를 판단할 수 없습니다.",
    ),
}

_STATUS_LABELS = {
    "PASS": "확인 완료",
    "READY": "확인 완료",
    "REVIEW": "주의해서 확인",
    "NEEDS_INPUT": "자료 보강 필요",
    "NOT_RUN": "검증 미실행",
    "NOT_APPLICABLE": "해당 없음",
    "BLOCKED": "진행 차단",
}


def _text(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = str(row.get(key) or "").strip()
        if value:
            return value
    return ""


def _criterion(row: dict[str, Any]) -> str:
    return _text(row, "Criteria", "display_label", "label", "module_id") or "검증 항목"


def _presentation(criterion: str) -> tuple[str, str, str]:
    normalized = criterion.lower().replace("/", " ")
    if "tax" in normalized and "account" in normalized:
        return _PRESENTATION["Tax / account scope"]
    return _PRESENTATION.get(
        criterion,
        (
            criterion,
            "저장된 검증 근거와 판정 기준을 확인했습니다.",
            "이 결과가 후보의 재현성·운용 가능성·위험 해석에 미치는 영향을 확인합니다.",
        ),
    )


def _match(pattern: str, text: str) -> str:
    matched = re.search(pattern, text, flags=re.IGNORECASE)
    return matched.group(1) if matched else ""


def _result_summary(
    criterion: str,
    *,
    status: str,
    current: str,
    evidence: str,
) -> str:
    combined = " / ".join(value for value in (current, evidence) if value)
    if status == "NOT_APPLICABLE":
        return "현재 후보 구조에서는 이 검증을 적용하지 않습니다."
    if status == "NOT_RUN":
        return "현재 결과에 계산된 검증 근거가 없습니다."
    if status in {"NEEDS_INPUT", "BLOCKED"}:
        return "판정에 필요한 자료 또는 계산 결과가 충분하지 않습니다."
    if criterion == "Walk-forward temporal validation":
        windows = _match(r"windows=(\d+)", combined)
        worst = _match(r"worst excess\s+([-\d.]+)%", combined)
        result = (
            f"기간을 이동한 반복 검증 {windows}개를 계산했습니다."
            if windows
            else "기간을 이동한 반복 검증 결과를 계산했습니다."
        )
        if worst:
            result += f" 가장 약한 구간의 비교 기준 대비 성과는 {worst}%입니다."
        return result
    if criterion == "Regime split validation":
        buckets = _match(r"buckets=(\d+)", combined)
        months = _match(r"months=(\d+)", combined)
        if buckets and months:
            return f"총 {months}개월을 {buckets}개 시장 국면으로 나눠 성과 차이를 계산했습니다."
        return "시장 환경을 여러 국면으로 나눠 성과 차이를 계산했습니다."
    if criterion == "OOS holdout validation":
        out_excess = _match(r"out excess\s+([-\d.]+)%", combined)
        drawdown_gap = _match(r"out drawdown gap\s+([-\d.]+)%", combined)
        if out_excess:
            suffix = (
                f" 최대낙폭 차이는 {drawdown_gap}%입니다."
                if drawdown_gap
                else ""
            )
            return f"별도 검증 기간의 비교 기준 대비 성과는 {out_excess}%입니다.{suffix}"
        return "전략 구성에 사용하지 않은 별도 기간의 성과를 계산했습니다."
    if criterion in {"Provider snapshot freshness", "Provider / freshness evidence"}:
        if "stale" in combined.lower() or "review" in combined.lower():
            return "최신 자료와 오래되거나 기준일이 불명확한 자료가 함께 확인됐습니다."
        return "현재 판단에 사용할 ETF·외부 자료의 기준일을 확인했습니다."
    if criterion == "Cost / slippage sensitivity evidence":
        generic = _match(r"generic=(\d+)", combined)
        follow_up = _match(r"runtime follow-up=(\d+)", combined)
        if generic:
            suffix = (
                f" 전략 전용 후속 검증은 {follow_up}개입니다."
                if follow_up
                else ""
            )
            return f"기본 민감도 결과 {generic}개를 계산했습니다.{suffix}"
        return "거래비용과 체결 오차 변화에 따른 성과 차이를 계산했습니다."
    normalized = criterion.lower().replace("/", " ")
    if "tax" in normalized and "account" in normalized:
        if "not modeled" in combined.lower():
            return "세금과 계좌 유형별 차이는 현재 결과에 계산되지 않았습니다."
        return "현재 결과가 세금·계좌 조건을 반영하는 범위를 확인했습니다."
    if criterion == "Transaction cost model":
        return "거래비용이 백테스트 순성과 계산에 연결되는 구조를 확인했습니다."
    if criterion == "Net cost curve proof":
        return "비용 차감 후 값이 최종 자산 곡선과 수익률 계산에 연결됨을 확인했습니다."
    if criterion == "Storage / execution boundary":
        return "검증 중 DB·registry 쓰기와 실거래 승인이 비활성화된 상태를 확인했습니다."
    if criterion in {"Top holding concentration", "Holdings overlap"}:
        coverage = _match(r"coverage\s+([\d.]+)%", combined)
        review_line = _match(r"review line\s+([\d.]+)%", combined)
        if coverage:
            suffix = (
                f" 주의 기준은 {review_line}%입니다."
                if review_line
                else ""
            )
            return f"ETF 내부 종목 확인 비중은 {coverage}%입니다.{suffix}"
    if criterion == "Asset bucket exposure":
        coverage = _match(r"coverage\s+([\d.]+)%", combined)
        dominant = _match(r"review line\s+([\d.]+)%", combined)
        if coverage:
            suffix = (
                f" 지배적 노출 주의 기준은 {dominant}%입니다."
                if dominant
                else ""
            )
            return f"자산군 노출 확인 비중은 {coverage}%입니다.{suffix}"
    if criterion == "Provider look-through coverage":
        holdings = _match(r"holdings\s+([\d.]+)%", combined)
        exposure = _match(r"exposure\s+([\d.]+)%", combined)
        if holdings and exposure:
            return f"ETF 보유 종목은 {holdings}%, 자산군 노출은 {exposure}%까지 확인했습니다."
    if status in {"PASS", "READY"}:
        return "저장된 계산 근거가 현재 기준을 충족했습니다."
    if status == "REVIEW":
        return "계산 결과는 있으나 주의 기준에 해당합니다."
    return "현재 상태와 저장된 근거를 확인했습니다."


def _evidence_state(status: str, current: str, evidence: str) -> str:
    if status == "NOT_APPLICABLE":
        return "not_applicable"
    if status in {"PASS", "READY"}:
        return "verified"
    if status in {"NOT_RUN", "NEEDS_INPUT", "BLOCKED"}:
        return "missing"
    observed = " ".join((current, evidence)).strip(" -/")
    return "computed" if observed else "missing"


def _next_action(
    criterion: str,
    *,
    status: str,
    stage_owner: str,
) -> str:
    if status in {"PASS", "READY", "NOT_APPLICABLE"}:
        return "추가 조치가 필요하지 않습니다."
    normalized = criterion.lower().replace("/", " ")
    if "tax" in normalized and "account" in normalized:
        return "Final Review에서 실제 계좌의 세금·수수료 조건과 수용 여부를 판단 근거에 기록합니다."
    if criterion in {"Provider snapshot freshness", "Provider / freshness evidence"}:
        return "Level2 데이터 보강에서 수집 가능한 자료를 갱신한 뒤 최신 데이터 기준 재검증을 실행합니다."
    if status == "NOT_RUN":
        return "이 전략에 필요한 검증 기능을 구현한 뒤 Level2 검증을 다시 실행합니다."
    if stage_owner == "final_review":
        return "검증된 한계와 실제 투자 조건을 Final Review 판단 근거로 확인합니다."
    if status in {"NEEDS_INPUT", "BLOCKED"}:
        return "Level2에서 필요한 데이터 또는 검증 계산을 보강한 뒤 다시 검증합니다."
    return "Level2에서 주의가 발생한 구간과 비교 기준을 확인하고 결과를 기록합니다."


def explain_practical_validation_row(
    row: dict[str, Any],
    *,
    stage_owner: str,
) -> dict[str, Any]:
    """Translate a stored validation row into user language with nested raw trace."""

    criterion = _criterion(row)
    status = _text(row, "Status", "status", "display_status").upper() or "NOT_RUN"
    current = _text(row, "Current", "current_problem")
    evidence = _text(row, "Evidence", "checked_evidence", "evidence", "explanation")
    raw_next_action = _text(row, "Next Action", "next_action", "completion_criteria")
    display_title, what_was_checked, meaning = _presentation(criterion)
    evidence_state = _evidence_state(status, current, evidence)
    if status == "NOT_APPLICABLE":
        meaning = "현재 후보 구조에서는 의도적으로 검증 대상이 아닙니다."
    elif status == "NOT_RUN":
        meaning = (
            f"{meaning} 현재 근거가 없으므로 Final Review로 넘기기 전에 "
            "Level2 검증 기능 또는 계산을 보강해야 합니다."
        )
    return {
        "display_title": display_title,
        "status_label": _STATUS_LABELS.get(status, "확인 필요"),
        "what_was_checked": what_was_checked,
        "result_summary": _result_summary(
            criterion,
            status=status,
            current=current,
            evidence=evidence,
        ),
        "meaning": meaning,
        "next_action": _next_action(
            criterion,
            status=status,
            stage_owner=stage_owner,
        ),
        "evidence_state": evidence_state,
        "stage_owner": stage_owner,
        "technical_trace": {
            "criterion": criterion,
            "status": status,
            "current": current,
            "evidence": evidence,
            "next_action": raw_next_action,
        },
    }


__all__ = [
    "PRACTICAL_VALIDATION_EVIDENCE_CATEGORIES",
    "explain_practical_validation_row",
]
