from __future__ import annotations

import re
from typing import Any

from app.services.backtest_component_role_weight_audit import build_component_role_weight_audit
from app.services.backtest_construction_risk_audit import build_construction_risk_audit
from app.services.backtest_data_coverage_audit import build_data_coverage_audit
from app.services.backtest_final_review_guidance import (
    build_pattern_guide as _build_pattern_guide_v2,
    build_pattern_guide_contract as _build_pattern_guide_contract_v2,
)
from app.services.backtest_realism_audit import build_backtest_realism_audit
from app.services.backtest_risk_contribution_audit import build_risk_contribution_audit
from app.services.backtest_validation_efficacy import build_validation_efficacy_audit


SELECT_FOR_PRACTICAL_PORTFOLIO = "SELECT_FOR_PRACTICAL_PORTFOLIO"
DECISION_DOSSIER_SCHEMA_VERSION = "decision_dossier_v1"
DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION = "selected_decision_source_consistency_v1"
CANDIDATE_BOARD_SCHEMA_VERSION = "final_review_candidate_board_v1"
DECISION_RECORD_GUIDE_SCHEMA_VERSION = "final_review_decision_record_guide_v1"
SAVED_DECISION_REVIEW_SCHEMA_VERSION = "final_review_saved_decision_review_v1"
INVESTMENT_REPORT_SCHEMA_VERSION = "final_review_investment_report_v1"
LEVEL2_REVIEW_DISPOSITION_SCHEMA_VERSION = "final_review_level2_review_disposition_v1"
FINAL_REVIEW_SCORECARD_SCHEMA_VERSION = "final_review_scorecard_v1"
SAVE_HANDOFF_SUMMARY_SCHEMA_VERSION = "final_review_save_handoff_summary_v1"
WEAKNESS_IMPROVEMENT_SCHEMA_VERSION = "final_review_weakness_improvement_v1"
SELECTION_RATIONALE_SCHEMA_VERSION = "final_review_selection_rationale_v1"
DECISION_SUMMARY_SCHEMA_VERSION = "final_review_decision_summary_v1"
INTERPRETATION_CARD_SCHEMA_VERSION = "final_review_interpretation_card_v1"
PATTERN_GUIDE_CONTRACT_SCHEMA_VERSION = "final_review_pattern_guide_contract_v2"

FINAL_REVIEW_PATTERN_CATALOG = (
    {
        "key": "concentration",
        "label": "주식 / 섹터 집중도",
        "question": "특정 자산, 섹터 또는 보유 종목에 성과와 위험이 과도하게 집중되는가?",
        "experiment_change": "최대 비중이 큰 구성요소를 낮추고 나머지 비중을 비례 재배분합니다.",
        "primary_evidence": ["construction_risk_audit", "component_role_weight_audit"],
        "required_signals": ["component_weight", "holdings_or_exposure_concentration"],
    },
    {
        "key": "stock_bond_diversification",
        "label": "주식-채권 분산과 상관",
        "question": "주식과 채권의 역할 및 상관 변화에도 분산 효과가 유지되는가?",
        "experiment_change": "채권 역할 구성요소의 비중을 한 단계 높인 대안을 만듭니다.",
        "primary_evidence": ["risk_contribution_audit", "component_role_weight_audit"],
        "required_signals": ["component_role", "correlation_or_component_return_matrix"],
    },
    {
        "key": "rate_duration",
        "label": "금리 / 듀레이션 민감도",
        "question": "금리 상승 또는 하락 구간에서 어떤 노출이 후보를 강화하거나 약화하는가?",
        "experiment_change": "듀레이션 민감 구성요소의 비중을 낮추거나 단기채 역할로 교체합니다.",
        "primary_evidence": ["macro_regime_evidence", "construction_risk_audit"],
        "required_signals": ["rate_regime_result", "duration_or_rate_sensitive_exposure"],
    },
    {
        "key": "inflation",
        "label": "인플레이션 민감도",
        "question": "인플레이션 유형과 구간 변화에서 후보의 방어력은 어떻게 달라지는가?",
        "experiment_change": "인플레이션 방어 역할 구성요소를 추가하거나 비중을 높입니다.",
        "primary_evidence": ["macro_regime_evidence", "stress_robustness_evidence"],
        "required_signals": ["inflation_regime_result", "inflation_sensitive_exposure"],
    },
    {
        "key": "tail_risk",
        "label": "변동성 / 낙폭 / tail risk",
        "question": "급격한 변동성과 낙폭 구간에서 손실 구조와 회복력이 확인되는가?",
        "experiment_change": "낙폭 기여가 큰 구성요소 비중을 낮춘 방어형 대안을 만듭니다.",
        "primary_evidence": ["stress_robustness_evidence", "risk_contribution_audit"],
        "required_signals": ["drawdown_or_stress_result", "recovery_or_tail_metric"],
    },
    {
        "key": "trend_regime",
        "label": "추세 / 모멘텀 체제",
        "question": "추세장과 반전 또는 횡보장에서 전략 성과가 어떻게 달라지는가?",
        "experiment_change": "추세 신호 또는 리밸런싱 주기 한 가지만 바꾼 대안을 만듭니다.",
        "primary_evidence": ["macro_regime_evidence", "validation_efficacy_audit"],
        "required_signals": ["trend_regime_result", "out_of_sample_or_regime_split"],
    },
    {
        "key": "component_dependency",
        "label": "위험 기여도 / 구성요소 의존",
        "question": "한 구성요소 제거 또는 변동성 확대가 포트폴리오 전체를 좌우하는가?",
        "experiment_change": "위험 기여도가 가장 큰 구성요소를 제외하거나 비중을 낮춥니다.",
        "primary_evidence": ["risk_contribution_audit", "component_role_weight_audit"],
        "required_signals": ["risk_contribution", "drop_one_or_dependency_result"],
    },
    {
        "key": "liquidity_cost",
        "label": "유동성 / 비용 / turnover",
        "question": "거래비용, 회전율, 유동성이 순성과와 실제 운용 가능성을 훼손하는가?",
        "experiment_change": "리밸런싱 빈도를 낮추거나 비용 가정을 높인 대안을 만듭니다.",
        "primary_evidence": ["backtest_realism_audit", "construction_risk_audit"],
        "required_signals": ["turnover_or_cost", "liquidity_or_capacity"],
    },
    {
        "key": "benchmark_dependency",
        "label": "벤치마크 의존 / 상대 성과",
        "question": "동일 기간과 빈도의 비교 기준에서 상대 우위와 열위가 반복되는가?",
        "experiment_change": "전략 구성은 유지하고 비교 benchmark 또는 비교 구간을 바꿉니다.",
        "primary_evidence": ["benchmark_parity_evidence", "validation_efficacy_audit"],
        "required_signals": ["benchmark_parity", "relative_performance"],
    },
    {
        "key": "parameter_sensitivity",
        "label": "파라미터 / 리밸런싱 민감도",
        "question": "파라미터와 리밸런싱 주기를 바꿔도 결론이 유지되는가?",
        "experiment_change": "핵심 파라미터 또는 리밸런싱 주기 한 가지만 인접 값으로 바꿉니다.",
        "primary_evidence": ["stress_robustness_evidence", "validation_efficacy_audit"],
        "required_signals": ["sensitivity_result", "rebalance_or_parameter_range"],
    },
)

FINAL_REVIEW_DECISION_LABELS = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "모니터링 후보 선정",
    "HOLD_FOR_MORE_PAPER_TRACKING": "내용 부족 / 관찰 필요",
    "REJECT_FOR_PRACTICAL_USE": "투자하면 안 됨",
    "RE_REVIEW_REQUIRED": "재검토 필요",
}
FINAL_REVIEW_STATUS_DISPLAY = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: {
        "route": "FINAL_REVIEW_DECISION_COMPLETE",
        "verdict": "최종 판단 완료: Portfolio Monitoring 후보로 선정됨",
        "next_action": "이 기록은 모니터링 후보 선정 판단입니다. 실제 투자 금액, 리밸런싱, 주문 승인 여부는 별도 운영 / 승인 단계에서 사용자가 결정합니다.",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "route": "FINAL_REVIEW_HOLD_FOR_MORE_OBSERVATION",
        "verdict": "최종 판단 보류: 내용 부족 / 추가 관찰 필요",
        "next_action": "추가 paper observation이나 근거 보강 후 Final Review에서 다시 판단합니다.",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "route": "FINAL_REVIEW_REJECTED",
        "verdict": "최종 판단 완료: 모니터링 후보에서 제외됨",
        "next_action": "필요하면 후보 탐색, Compare, Portfolio Proposal 단계로 되돌아갑니다.",
    },
    "RE_REVIEW_REQUIRED": {
        "route": "FINAL_REVIEW_REVIEW_REQUIRED",
        "verdict": "최종 판단 재검토 필요: 구성 / 비중 / 검증 근거를 다시 확인",
        "next_action": "구성, 비중, validation, robustness, paper observation 근거를 보강한 뒤 Final Review에서 다시 판단합니다.",
    },
}
FINAL_REVIEW_DECISION_RECORD_TEMPLATES = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: {
        "reason": "투자 검토서와 selection gate가 모니터링 후보 선정 가능 상태이며, 남은 blocker 없이 Portfolio Monitoring 추적 후보로 기록한다.",
        "constraints": "실제 투자 전 투입 금액, 리밸런싱 규칙, 중단 / 재검토 기준, 세금 / 계좌 조건은 별도로 확인한다.",
        "next_action": "Operations > Portfolio Monitoring에서 read-only monitoring / recheck 기준을 확인한다.",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "reason": "critical blocker는 아니지만 review-required evidence나 관찰 공백이 남아 있어 선정 전 추가 paper tracking이 필요하다.",
        "constraints": "관찰 기간, benchmark, review trigger, 보강할 evidence row를 명시하고 선정 판단은 보류한다.",
        "next_action": "추가 관찰 또는 evidence 보강 후 Final Review에서 다시 판단한다.",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "reason": "현재 검증 근거와 gate evidence로는 모니터링 후보로 사용하기 어렵다고 판단한다.",
        "constraints": "동일 source를 다시 검토하려면 blocker 해소나 후보 재구성이 먼저 필요하다.",
        "next_action": "필요하면 Backtest Analysis, Practical Validation, Portfolio Mix 단계로 돌아가 새 후보를 만든다.",
    },
    "RE_REVIEW_REQUIRED": {
        "reason": "구성, 비중, 검증 근거, 데이터 상태 중 최종 판단 전에 다시 검토해야 할 항목이 남아 있다.",
        "constraints": "재검토 대상 evidence row와 보강 책임 범위를 남기고 선정 route로 저장하지 않는다.",
        "next_action": "구성 / 비중 / validation / provider / robustness evidence를 보강한 뒤 Final Review에서 재검토한다.",
    },
}
FINAL_REVIEW_SAVED_DECISION_FILTER_OPTIONS = (
    "All",
    "Selected",
    "Hold",
    "Reject",
    "Re-review",
    "Unknown",
)
GATE_POLICY_SCHEMA_VERSION = "investability_gate_policy_v1"
SELECTION_GATE_POLICY_SCHEMA_VERSION = "final_review_selection_gate_policy_v1"
DEPLOYMENT_READINESS_GATE_POLICY_SCHEMA_VERSION = "deployment_readiness_gate_policy_v1"
GATE_POLICY_MODE_SELECTION = "selection_readiness"
GATE_POLICY_MODE_DEPLOYMENT = "deployment_readiness"
GATE_POLICY_GROUP_LABELS = {
    "data_trust": "Data Trust / Source Contract",
    "benchmark": "Benchmark / Comparator Parity",
    "provider_coverage": "Provider / Look-through",
    "stress_robustness": "Stress / Robustness",
    "leveraged_inverse": "Leveraged / Inverse Suitability",
    "paper_observation": "Paper Observation",
    "final_review_evidence": "Final Review Evidence",
    "validation_efficacy": "Validation Method Strength",
    "data_coverage": "Data Coverage",
    "construction_risk": "Construction Risk",
    "risk_contribution": "Risk Contribution",
    "component_role_weight": "Component Role / Weight",
    "backtest_realism": "Backtest Realism",
}
GATE_POLICY_GROUP_ACTIONS = {
    "data_trust": "원본 source, 가격, 비중, Data Trust blocker를 먼저 해소합니다.",
    "benchmark": "같은 기간 / frequency / coverage의 benchmark parity를 보강합니다.",
    "provider_coverage": "ETF 운용성 / holdings / exposure / macro coverage를 actual evidence로 보강합니다.",
    "stress_robustness": "stress, rolling, sensitivity, overfit evidence를 실행 가능한 근거로 보강합니다.",
    "leveraged_inverse": "leveraged / inverse 노출 목적, 보유 기간, 위험 한계를 명시합니다.",
    "paper_observation": "관찰 benchmark, active component, review trigger를 보강합니다.",
    "final_review_evidence": "Final Review evidence route가 ready가 되도록 validation / robustness / observation blocker를 해소합니다.",
    "validation_efficacy": "walk-forward / OOS / regime split 방법론 evidence gap을 보강합니다.",
    "data_coverage": "DB price window, provider freshness, PIT replay, universe / survivorship evidence gap을 보강합니다.",
    "construction_risk": "component weight, provider look-through coverage, top holding / overlap, asset exposure evidence gap을 보강합니다.",
    "risk_contribution": "component return matrix, correlation, risk contribution, drop-one dependency evidence gap을 보강합니다.",
    "component_role_weight": "component role source, profile intent, target weight, weight rationale evidence gap을 보강합니다.",
    "backtest_realism": "거래비용, turnover, liquidity, net performance, tax/account scope 같은 실전성 근거를 보강합니다.",
}
GATE_POLICY_DOMAIN_GROUPS = {
    "input_evidence_layer": "data_trust",
    "asset_allocation_fit": "provider_coverage",
    "concentration_overlap_exposure": "construction_risk",
    "correlation_diversification_risk_contribution": "risk_contribution",
    "regime_macro_suitability": "provider_coverage",
    "sentiment_risk_on_off_overlay": "provider_coverage",
    "stress_scenario_diagnostics": "stress_robustness",
    "alternative_portfolio_challenge": "benchmark",
    "leveraged_inverse_etf_suitability": "leveraged_inverse",
    "operability_cost_liquidity": "provider_coverage",
    "robustness_sensitivity_overfit": "stress_robustness",
    "monitoring_baseline_seed": "paper_observation",
}
GATE_POLICY_SECTION_GROUPS = {
    "source chain": "data_trust",
    "backtest contract / data trust": "data_trust",
    "runtime replay": "stress_robustness",
    "provider / look-through": "provider_coverage",
    "benchmark parity": "benchmark",
    "robustness / stress": "stress_robustness",
    "paper observation": "paper_observation",
    "critical gaps": "final_review_evidence",
    "validation efficacy audit": "validation_efficacy",
    "data coverage audit": "data_coverage",
    "construction risk audit": "construction_risk",
    "risk contribution audit": "risk_contribution",
    "component role / weight audit": "component_role_weight",
    "backtest realism audit": "backtest_realism",
}
GATE_POLICY_CRITICAL_GROUPS_BY_PROFILE = {
    "conservative_defensive": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "paper_observation",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "balanced_core": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "paper_observation",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "growth_aggressive": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "hedged_tactical": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
    "custom": {
        "data_trust",
        "benchmark",
        "provider_coverage",
        "stress_robustness",
        "leveraged_inverse",
        "paper_observation",
        "final_review_evidence",
        "validation_efficacy",
        "data_coverage",
        "construction_risk",
        "risk_contribution",
        "component_role_weight",
        "backtest_realism",
    },
}
GATE_POLICY_REVIEW_GROUPS_BY_PROFILE = {
    "growth_aggressive": {"paper_observation"},
    "hedged_tactical": {"paper_observation"},
}
_POLICY_SEVERITY_RANK = {
    "PASS": 0,
    "WATCH": 1,
    "REVIEW_REQUIRED": 2,
    "BLOCK": 3,
}
_SELECTION_STATUS_BLOCKING_GROUPS = {
    "data_trust",
    "benchmark",
    "stress_robustness",
    "paper_observation",
    "final_review_evidence",
    "leveraged_inverse",
}
_SELECTION_VALIDATION_EFFICACY_BLOCKING_TERMS = {
    "walk-forward",
    "walkforward",
    "temporal validation",
    "oos",
    "holdout",
    "regime",
    "method",
}
_SELECTION_DATA_COVERAGE_BLOCKING_TERMS = {
    "price db window",
    "price coverage",
    "window coverage",
    "pit",
    "survivorship",
    "delisting",
}
_SELECTION_BACKTEST_REALISM_BLOCKING_TERMS = {
    "transaction cost",
    "net cost curve",
    "net performance",
    "execution boundary",
    "cost input",
    "gross",
}
_SELECTION_COMPONENT_ROLE_BLOCKING_TERMS = {
    "component role source",
    "weight rationale",
    "profile intent",
}


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _float_or_none(value: Any) -> float | None:
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _ready_from_check(check: dict[str, Any]) -> bool:
    if "Ready" in check:
        return bool(check.get("Ready"))
    return bool(check.get("ready"))


def _find_check(checks: list[dict[str, Any]], criteria: str) -> dict[str, Any]:
    criteria_key = criteria.lower()
    for check in checks:
        check_row = dict(check or {})
        label = _safe_text(check_row.get("Criteria") or check_row.get("criteria"), "").lower()
        if label == criteria_key:
            return check_row
    return {}


def _status_counts(validation: dict[str, Any]) -> dict[str, int]:
    summary = dict(validation.get("diagnostic_summary") or {})
    return dict(summary.get("status_counts") or {})


def _provider_status_summary(validation: dict[str, Any]) -> str:
    provider_context = dict(validation.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    statuses = sorted(
        {
            _safe_text(dict(item or {}).get("diagnostic_status"), "")
            for item in coverage.values()
            if isinstance(item, dict)
        }
    )
    return ", ".join([status for status in statuses if status]) or "-"


def _profile_gate_policy_sets(validation: dict[str, Any]) -> tuple[str, str, set[str], set[str]]:
    profile = dict(validation.get("validation_profile") or {})
    summary = dict(validation.get("diagnostic_summary") or {})
    profile_id = _safe_text(profile.get("profile_id") or summary.get("profile_id"), "balanced_core")
    if profile_id not in GATE_POLICY_CRITICAL_GROUPS_BY_PROFILE:
        profile_id = "balanced_core"
    profile_label = _safe_text(profile.get("profile_label") or summary.get("profile_label"), "균형형")
    critical_groups = set(GATE_POLICY_CRITICAL_GROUPS_BY_PROFILE.get(profile_id) or set())
    review_groups = set(GATE_POLICY_REVIEW_GROUPS_BY_PROFILE.get(profile_id) or set())
    return profile_id, profile_label, critical_groups, review_groups


def _policy_status_from_current(*, ready: bool, current: Any) -> str:
    text = str(current or "").strip().upper()
    if not ready:
        if not text or text == "-" or any(token in text for token in ("BLOCK", "ERROR", "MISSING", "NEEDS_INPUT", "NOT_RUN")):
            return "NOT_RUN"
        return "REVIEW"
    if any(token in text for token in ("BLOCK", "ERROR", "MISSING", "NEEDS_INPUT", "NOT_RUN")):
        return "NOT_RUN"
    if any(token in text for token in ("REVIEW", "PROXY", "BRIDGE", "STALE", "PARTIAL", "WATCH", "NEEDS_REVIEW")):
        return "REVIEW"
    return "PASS"


def _policy_severity(
    *,
    group: str,
    status: str,
    critical_groups: set[str],
    review_groups: set[str],
    policy_mode: str = GATE_POLICY_MODE_DEPLOYMENT,
    criteria: str = "",
    current: Any = "",
    evidence: Any = "",
) -> str:
    normalized = str(status or "").upper()
    if policy_mode == GATE_POLICY_MODE_SELECTION:
        return _selection_policy_severity(
            group=group,
            status=normalized,
            criteria=criteria,
            current=current,
            evidence=evidence,
        )
    if normalized in {"BLOCKED", "BLOCK", "NOT_RUN", "NEEDS_INPUT", "MISSING"}:
        return "BLOCK" if group in critical_groups else "REVIEW_REQUIRED"
    if normalized == "REVIEW":
        if group in critical_groups:
            return "REVIEW_REQUIRED"
        if group in review_groups:
            return "REVIEW_REQUIRED"
        return "WATCH"
    return "PASS"


def _text_has_any(value: str, terms: set[str]) -> bool:
    text = value.lower()
    return any(term in text for term in terms)


def _selection_policy_severity(
    *,
    group: str,
    status: str,
    criteria: str,
    current: Any,
    evidence: Any,
) -> str:
    if status in {"", "PASS", "OK", "READY"}:
        return "PASS"
    joined = " ".join(
        [
            str(criteria or ""),
            str(current or ""),
            str(evidence or ""),
        ]
    ).lower()
    if status in {"BLOCKED", "BLOCK"}:
        return "BLOCK"
    if status in {"NOT_RUN", "NEEDS_INPUT", "MISSING"}:
        if group in _SELECTION_STATUS_BLOCKING_GROUPS:
            return "BLOCK"
        if group == "validation_efficacy" and _text_has_any(joined, _SELECTION_VALIDATION_EFFICACY_BLOCKING_TERMS):
            return "BLOCK"
        if group == "data_coverage" and _text_has_any(joined, _SELECTION_DATA_COVERAGE_BLOCKING_TERMS):
            return "BLOCK"
        if group == "backtest_realism" and _text_has_any(joined, _SELECTION_BACKTEST_REALISM_BLOCKING_TERMS):
            return "BLOCK"
        if group == "component_role_weight" and _text_has_any(joined, _SELECTION_COMPONENT_ROLE_BLOCKING_TERMS):
            return "BLOCK"
        return "WATCH"
    if status == "REVIEW":
        if group == "benchmark":
            return "REVIEW_REQUIRED"
        specific_joined = " ".join([str(criteria or ""), str(current or "")]).lower()
        if group == "backtest_realism" and _text_has_any(
            specific_joined,
            {"transaction cost", "net cost curve", "net performance", "gross"},
        ):
            return "REVIEW_REQUIRED"
        return "WATCH"
    return "PASS"


def _selection_source_is_weighted_mix(validation: dict[str, Any]) -> bool:
    traits = dict(validation.get("source_traits") or {})
    if "is_weighted_mix" in traits:
        return bool(traits.get("is_weighted_mix"))
    source = dict(validation.get("selection_source_snapshot") or validation.get("source_snapshot") or {})
    construction = dict(source.get("construction") or {})
    source_kind = str(source.get("source_kind") or validation.get("source_kind") or "").lower()
    construction_source = str(construction.get("source") or "").lower()
    if "weighted" in source_kind or "mix" in construction_source:
        return True
    components = list(
        source.get("components")
        or validation.get("component_rows")
        or validation.get("selected_components")
        or []
    )
    active = [
        component
        for component in components
        if (_float_or_none(dict(component or {}).get("target_weight") or dict(component or {}).get("Weight")) or 0.0)
        > 0.0
    ]
    return len(active) > 1


def _selection_not_applicable_groups(validation: dict[str, Any]) -> set[str]:
    if _selection_source_is_weighted_mix(validation):
        return set()
    return {"risk_contribution", "component_role_weight"}


def _gate_group_from_gap(gap: dict[str, Any]) -> str:
    area = _safe_text(gap.get("Area"), "").lower()
    text = f"{area} {_safe_text(gap.get('Gap'), '').lower()}"
    if "paper" in text or "observation" in text:
        return "paper_observation"
    if "benchmark" in text:
        return "benchmark"
    if any(token in text for token in ("provider", "holding", "exposure", "operability", "macro", "liquidity")):
        return "provider_coverage"
    if any(token in text for token in ("cost", "turnover", "slippage", "execution", "tax", "account", "rebalance")):
        return "backtest_realism"
    if any(token in text for token in ("stress", "scenario", "robust", "sensitivity", "overfit", "correlation")):
        return "stress_robustness"
    if "leverag" in text or "inverse" in text:
        return "leveraged_inverse"
    if "decision evidence" in text:
        return "final_review_evidence"
    return "data_trust"


def _finding_label(group: str) -> str:
    return GATE_POLICY_GROUP_LABELS.get(group, group.replace("_", " ").title())


def _merge_policy_state(
    states: dict[str, dict[str, Any]],
    *,
    group: str,
    severity: str,
    current: Any,
    evidence: Any,
    required_action: str | None = None,
) -> None:
    if not group:
        return
    state = states.setdefault(
        group,
        {
            "group": group,
            "severity": "PASS",
            "current": [],
            "evidence": [],
            "required_action": GATE_POLICY_GROUP_ACTIONS.get(group, "근거를 보강합니다."),
        },
    )
    if _POLICY_SEVERITY_RANK.get(severity, 0) > _POLICY_SEVERITY_RANK.get(str(state.get("severity") or "PASS"), 0):
        state["severity"] = severity
        state["current"] = [item for item in state.get("current", []) if item != "PASS"]
        state["evidence"] = [item for item in state.get("evidence", []) if item != "No policy finding"]
    current_text = _safe_text(current)
    if current_text not in state["current"]:
        state["current"].append(current_text)
    evidence_text = _safe_text(evidence)
    if evidence_text not in state["evidence"]:
        state["evidence"].append(evidence_text)
    if required_action:
        state["required_action"] = required_action


def _merge_audit_rows_into_policy(
    states: dict[str, dict[str, Any]],
    *,
    audit: dict[str, Any],
    group: str,
    critical_groups: set[str],
    review_groups: set[str],
    policy_mode: str = GATE_POLICY_MODE_DEPLOYMENT,
    skipped_groups: set[str] | None = None,
) -> None:
    if group in set(skipped_groups or set()):
        return
    for raw_row in _as_list(dict(audit or {}).get("rows")):
        if not isinstance(raw_row, dict):
            continue
        row = dict(raw_row or {})
        raw_status = row.get("Status") or row.get("status")
        status = str(raw_status or "").strip().upper()
        if not status and not _ready_from_check(row):
            status = _policy_status_from_current(
                ready=False,
                current=row.get("Current") or row.get("current") or "-",
            )
        if status in {"", "PASS", "OK", "READY"}:
            continue
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=policy_mode,
            criteria=_safe_text(row.get("Criteria") or row.get("criteria"), "Audit row"),
            current=row.get("Current") or row.get("current") or status,
            evidence=row.get("Meaning") or row.get("Evidence") or row.get("evidence"),
        )
        criteria = _safe_text(row.get("Criteria") or row.get("criteria"), "Audit row")
        evidence = _safe_text(
            row.get("Meaning")
            or row.get("Evidence")
            or row.get("evidence")
            or row.get("Current")
            or row.get("current"),
            "audit evidence gap",
        )
        current = _safe_text(row.get("Current") or row.get("current") or status)
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=f"{criteria}: {status} / {current}",
            evidence=f"{criteria}: {evidence}",
            required_action=row.get("Next Action") or row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )


def build_investability_gate_policy(
    *,
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    packet_checks: list[dict[str, Any]] | None = None,
    critical_gaps: list[dict[str, Any]] | None = None,
    policy_mode: str = GATE_POLICY_MODE_DEPLOYMENT,
) -> dict[str, Any]:
    """Summarize profile-aware gate policy without persisting raw validation data."""

    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    profile_id, profile_label, critical_groups, review_groups = _profile_gate_policy_sets(validation)
    mode = policy_mode if policy_mode in {GATE_POLICY_MODE_SELECTION, GATE_POLICY_MODE_DEPLOYMENT} else GATE_POLICY_MODE_DEPLOYMENT
    skipped_groups = _selection_not_applicable_groups(validation) if mode == GATE_POLICY_MODE_SELECTION else set()
    states: dict[str, dict[str, Any]] = {}
    for group in sorted(critical_groups | review_groups):
        if group in skipped_groups:
            _merge_policy_state(
                states,
                group=group,
                severity="PASS",
                current="NOT_APPLICABLE",
                evidence="Current source traits mark this audit as not applicable for Final Review selection.",
                required_action="추가 조치 없음",
            )
            continue
        _merge_policy_state(
            states,
            group=group,
            severity="PASS",
            current="PASS",
            evidence="No policy finding",
            required_action=GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    for check in list(packet_checks or []):
        check_row = dict(check or {})
        section = _safe_text(check_row.get("Section") or check_row.get("Criteria"), "").lower()
        group = GATE_POLICY_SECTION_GROUPS.get(section)
        if not group:
            continue
        if group in skipped_groups:
            continue
        current = check_row.get("Current") or "-"
        status = _policy_status_from_current(ready=_ready_from_check(check_row), current=current)
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=mode,
            criteria=section,
            current=current,
            evidence=check_row.get("Meaning") or section,
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=current,
            evidence=check_row.get("Meaning") or section,
            required_action=GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    for diagnostic in _as_list(validation.get("diagnostic_results")):
        if not isinstance(diagnostic, dict):
            continue
        diagnostic_row = dict(diagnostic or {})
        domain = str(diagnostic_row.get("domain") or "")
        group = GATE_POLICY_DOMAIN_GROUPS.get(domain)
        if not group:
            continue
        if group in skipped_groups:
            continue
        status = str(diagnostic_row.get("status") or "NOT_RUN").upper()
        if status not in {"BLOCKED", "NOT_RUN", "REVIEW"}:
            continue
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=mode,
            criteria=diagnostic_row.get("title") or domain,
            current=status,
            evidence=diagnostic_row.get("summary") or diagnostic_row.get("title") or domain,
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=status,
            evidence=diagnostic_row.get("title") or domain,
            required_action=diagnostic_row.get("next_action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    for gap in list(critical_gaps or []):
        if not isinstance(gap, dict):
            continue
        gap_row = dict(gap or {})
        group = _gate_group_from_gap(gap_row)
        if group in skipped_groups:
            continue
        status = "BLOCKED" if str(gap_row.get("Severity") or "").upper() == "BLOCK" else "REVIEW"
        severity = _policy_severity(
            group=group,
            status=status,
            critical_groups=critical_groups,
            review_groups=review_groups,
            policy_mode=mode,
            criteria=gap_row.get("Area"),
            current=status,
            evidence=gap_row.get("Gap"),
        )
        _merge_policy_state(
            states,
            group=group,
            severity=severity,
            current=status,
            evidence=gap_row.get("Gap") or gap_row.get("Area"),
            required_action=gap_row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group),
        )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("validation_efficacy_audit") or {}),
        group="validation_efficacy",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("construction_risk_audit") or {}),
        group="construction_risk",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("risk_contribution_audit") or {}),
        group="risk_contribution",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("component_role_weight_audit") or {}),
        group="component_role_weight",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    _merge_audit_rows_into_policy(
        states,
        audit=dict(validation.get("backtest_realism_audit") or {}),
        group="backtest_realism",
        critical_groups=critical_groups,
        review_groups=review_groups,
        policy_mode=mode,
        skipped_groups=skipped_groups,
    )
    if decision_evidence.get("route") not in {"READY_FOR_FINAL_DECISION", None, ""}:
        _merge_policy_state(
            states,
            group="final_review_evidence",
            severity="BLOCK" if mode == GATE_POLICY_MODE_SELECTION else "REVIEW_REQUIRED",
            current=decision_evidence.get("route") or "-",
            evidence=decision_evidence.get("verdict") or "Final Review evidence is not ready",
            required_action=decision_evidence.get("next_action") or GATE_POLICY_GROUP_ACTIONS["final_review_evidence"],
        )
    if paper_observation.get("blockers"):
        _merge_policy_state(
            states,
            group="paper_observation",
            severity="BLOCK" if "paper_observation" in critical_groups else "REVIEW_REQUIRED",
            current=paper_observation.get("route") or "-",
            evidence=", ".join(str(item) for item in _as_list(paper_observation.get("blockers"))),
            required_action=GATE_POLICY_GROUP_ACTIONS["paper_observation"],
        )
    policy_rows = []
    for group, state in sorted(states.items()):
        severity = str(state.get("severity") or "PASS")
        ready = severity in {"PASS", "WATCH"}
        current_values = list(state.get("current") or ["-"])
        evidence_values = list(state.get("evidence") or ["-"])
        if severity != "PASS":
            current_values = [item for item in current_values if item != "PASS"] or ["-"]
            evidence_values = [item for item in evidence_values if item != "No policy finding"] or ["-"]
        if ready and severity == "WATCH":
            selected_route_label = "Allowed with watch"
        elif ready:
            selected_route_label = "Allowed"
        else:
            selected_route_label = "Blocked"
        policy_rows.append(
            {
                "Criteria": _finding_label(group),
                "Group": group,
                "Policy": (
                    "not-applicable"
                    if group in skipped_groups
                    else "selection"
                    if mode == GATE_POLICY_MODE_SELECTION
                    else "critical"
                    if group in critical_groups
                    else "review-required"
                ),
                "Ready": ready,
                "Severity": severity,
                "Current": "; ".join(current_values),
                "Evidence": "; ".join(evidence_values),
                "Required Action": state.get("required_action") or GATE_POLICY_GROUP_ACTIONS.get(group, "-"),
                "Selected Route": selected_route_label,
            }
        )
    blockers = [
        f"{row['Criteria']}: {row['Evidence']}"
        for row in policy_rows
        if row.get("Severity") == "BLOCK"
    ]
    review_required = [
        f"{row['Criteria']}: {row['Evidence']}"
        for row in policy_rows
        if row.get("Severity") == "REVIEW_REQUIRED"
    ]
    if blockers:
        outcome = "blocked"
        suggested_decision_route = "RE_REVIEW_REQUIRED"
        next_action = "critical blocker를 해소한 뒤 Final Review에서 판단 route와 Monitoring handoff 가능 여부를 다시 확인합니다."
    elif review_required:
        outcome = "hold_or_re_review"
        suggested_decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
        next_action = "부족한 evidence를 보강하거나 보류 / 재검토 판단으로 기록한 뒤 Monitoring handoff 가능 여부를 다시 확인합니다."
    else:
        outcome = "select_ready"
        suggested_decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO
        next_action = "Final Review에서 판단 route를 저장하고, 선택 route라면 Portfolio Monitoring 후보 handoff를 남깁니다."
    return {
        "schema_version": (
            SELECTION_GATE_POLICY_SCHEMA_VERSION
            if mode == GATE_POLICY_MODE_SELECTION
            else DEPLOYMENT_READINESS_GATE_POLICY_SCHEMA_VERSION
        ),
        "legacy_schema_version": GATE_POLICY_SCHEMA_VERSION,
        "policy_mode": mode,
        "profile_id": profile_id,
        "profile_label": profile_label,
        "critical_groups": sorted(critical_groups),
        "review_required_groups": sorted(review_groups),
        "not_applicable_groups": sorted(skipped_groups),
        "outcome": outcome,
        "select_allowed": outcome == "select_ready",
        "suggested_decision_route": suggested_decision_route,
        "next_action": next_action,
        "waiver_supported": False,
        "waiver_required_for_select": bool(blockers or review_required),
        "policy_rows": policy_rows,
        "blockers": blockers,
        "review_required": review_required,
    }


def _critical_gap_rows(
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for blocker in _as_list(validation.get("hard_blockers")):
        gaps.append(
            {
                "Area": "Hard blocker",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "Backtest Analysis 또는 Practical Validation에서 blocker를 먼저 해소합니다.",
            }
        )
    for item in _as_list(validation.get("not_run_critical_domains")):
        item_row = dict(item or {})
        gaps.append(
            {
                "Area": _safe_text(item_row.get("title") or item_row.get("domain"), "Critical NOT_RUN"),
                "Gap": "중요 진단이 실행되지 않았습니다.",
                "Severity": "BLOCK",
                "Required Action": _safe_text(item_row.get("next_action"), "데이터 / replay / benchmark 근거를 보강합니다."),
            }
        )
    for gap in _as_list(validation.get("paper_tracking_gaps")):
        gaps.append(
            {
                "Area": "Observation gap",
                "Gap": _safe_text(gap),
                "Severity": "REVIEW",
                "Required Action": "Final Review에서 보류 / 재검토 사유로 확인합니다.",
            }
        )
    for blocker in _as_list(paper_observation.get("blockers")):
        gaps.append(
            {
                "Area": "Paper observation",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "관찰 benchmark / component / weight 기준을 보강합니다.",
            }
        )
    for blocker in _as_list(decision_evidence.get("blockers")):
        gaps.append(
            {
                "Area": "Decision evidence",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "Final Review evidence route를 먼저 통과 가능한 상태로 만듭니다.",
            }
        )
    return gaps


def _assumption_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    status_counts = _status_counts(validation)
    rows = [
        {
            "Assumption": "Hypothetical backtest",
            "Current": "applies",
            "Meaning": "백테스트와 재검증 결과는 미래 수익을 보장하지 않습니다.",
        },
        {
            "Assumption": "No live approval / order",
            "Current": "disabled",
            "Meaning": "Final Review는 투자 승인, 주문 지시, 자동 리밸런싱이 아닙니다.",
        },
        {
            "Assumption": "Compact evidence only",
            "Current": "JSONL stores summary evidence",
            "Meaning": "full holdings / macro / provider raw row는 DB 영역에 두고 판단 row에는 compact 근거만 남깁니다.",
        },
        {
            "Assumption": "Current provider snapshots",
            "Current": _provider_status_summary(validation),
            "Meaning": "ETF provider snapshot은 validation 기준 current evidence이며 과거 특정 시점의 완전한 PIT truth가 아닐 수 있습니다.",
        },
        {
            "Assumption": "Macro vintage",
            "Current": "ALFRED vintage not implemented",
            "Meaning": "macro context는 observation 기준이며 revision vintage까지 보장하지 않습니다.",
        },
        {
            "Assumption": "Cost / slippage limits",
            "Current": curve_evidence.get("portfolio_curve_source") or "source dependent",
            "Meaning": "비용, slippage, 세금, 계좌 제약은 제한적으로만 반영됐을 수 있습니다.",
        },
    ]
    if int(status_counts.get("NOT_RUN", 0) or 0) > 0:
        rows.append(
            {
                "Assumption": "Missing diagnostics",
                "Current": f"{status_counts.get('NOT_RUN', 0)} NOT_RUN",
                "Meaning": "실행되지 않은 진단은 통과가 아니라 판단 전 확인해야 하는 공백입니다.",
            }
        )
    return rows


def _open_review_items_from_policies(
    *,
    selection_policy: dict[str, Any],
    deployment_policy: dict[str, Any],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    seen: set[tuple[str, str]] = set()
    selection_rows = {
        str(row.get("Group") or ""): dict(row or {})
        for row in list(selection_policy.get("policy_rows") or [])
        if isinstance(row, dict)
    }
    for raw_row in list(deployment_policy.get("policy_rows") or []):
        row = dict(raw_row or {})
        group = str(row.get("Group") or "")
        severity = str(row.get("Severity") or "")
        if severity not in {"WATCH", "REVIEW_REQUIRED"}:
            continue
        selection_row = selection_rows.get(group, {})
        if str(selection_row.get("Severity") or "") == "BLOCK":
            continue
        key = (group, str(row.get("Criteria") or ""))
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "Group": group,
                "Criteria": row.get("Criteria") or _finding_label(group),
                "Severity": "OPEN_REVIEW",
                "Current": row.get("Current") or "-",
                "Evidence": row.get("Evidence") or "-",
                "Required Action": row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group, "-"),
                "Selection Gate Effect": "Open review item",
                "Deployment Gate Effect": severity,
            }
        )
    for raw_row in list(selection_policy.get("policy_rows") or []):
        row = dict(raw_row or {})
        if str(row.get("Severity") or "") != "WATCH":
            continue
        group = str(row.get("Group") or "")
        key = (group, str(row.get("Criteria") or ""))
        if key in seen:
            continue
        seen.add(key)
        items.append(
            {
                "Group": group,
                "Criteria": row.get("Criteria") or _finding_label(group),
                "Severity": "OPEN_REVIEW",
                "Current": row.get("Current") or "-",
                "Evidence": row.get("Evidence") or "-",
                "Required Action": row.get("Required Action") or GATE_POLICY_GROUP_ACTIONS.get(group, "-"),
                "Selection Gate Effect": "Open review item",
                "Deployment Gate Effect": "-",
            }
        )
    return items


def build_investability_evidence_packet(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact Final Review decision packet without adding persistence."""

    source = dict(source or {})
    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    validation_checks = [dict(row or {}) for row in _as_list(validation.get("checks")) if isinstance(row, dict)]
    benchmark_check = _find_check(validation_checks, "Benchmark parity")
    provider_check = _find_check(validation_checks, "Provider coverage")
    period_check = _find_check(validation_checks, "Runtime period coverage")
    runtime_check = _find_check(validation_checks, "Runtime recheck")
    status_counts = _status_counts(validation)
    robustness = dict(validation.get("robustness_validation") or {})
    critical_gaps = _critical_gap_rows(validation, paper_observation, decision_evidence)
    blocking_gaps = [gap for gap in critical_gaps if str(gap.get("Severity") or "") == "BLOCK"]
    assumptions = _assumption_rows(validation)
    data_coverage_audit = dict(validation.get("data_coverage_audit") or build_data_coverage_audit(validation))
    data_coverage_route = str(data_coverage_audit.get("route") or "")
    validation_for_efficacy = dict(validation)
    validation_for_efficacy.setdefault("data_coverage_audit", data_coverage_audit)
    validation_efficacy_audit = dict(
        validation.get("validation_efficacy_audit") or build_validation_efficacy_audit(validation_for_efficacy)
    )
    validation_efficacy_route = str(validation_efficacy_audit.get("route") or "")
    construction_risk_audit = dict(
        validation.get("construction_risk_audit") or build_construction_risk_audit(validation)
    )
    construction_risk_route = str(construction_risk_audit.get("route") or "")
    risk_contribution_audit = dict(
        validation.get("risk_contribution_audit") or build_risk_contribution_audit(validation)
    )
    risk_contribution_route = str(risk_contribution_audit.get("route") or "")
    component_role_weight_audit = dict(
        validation.get("component_role_weight_audit") or build_component_role_weight_audit(validation)
    )
    component_role_weight_route = str(component_role_weight_audit.get("route") or "")
    backtest_realism_audit = dict(validation.get("backtest_realism_audit") or build_backtest_realism_audit(validation))
    backtest_realism_route = str(backtest_realism_audit.get("route") or "")
    source_chain = {
        "source_type": source.get("source_type") or validation.get("source_type"),
        "source_id": source.get("source_id") or validation.get("selection_source_id"),
        "selection_source_id": validation.get("selection_source_id"),
        "validation_id": validation.get("validation_id"),
        "decision_id": None,
        "monitoring_snapshot_id": None,
    }
    checks = [
        {
            "Section": "Source Chain",
            "Ready": bool(source_chain.get("source_id") or source_chain.get("selection_source_id")),
            "Current": source_chain.get("validation_id") or source_chain.get("selection_source_id") or "-",
            "Meaning": "Backtest source와 Practical Validation result가 이어지는지 확인합니다.",
        },
        {
            "Section": "Backtest Contract / Data Trust",
            "Ready": _ready_from_check(_find_check(validation_checks, "Data Trust")) if validation_checks else True,
            "Current": dict(_find_check(validation_checks, "Data Trust")).get("Current") or validation.get("validation_route") or "-",
            "Meaning": "원본 실행 결과의 데이터 품질과 차단 상태를 확인합니다.",
        },
        {
            "Section": "Runtime Replay",
            "Ready": _ready_from_check(runtime_check) and _ready_from_check(period_check) if runtime_check or period_check else False,
            "Current": f"{runtime_check.get('Current') or '-'} / {period_check.get('Current') or '-'}",
            "Meaning": "저장 snapshot이 아니라 runtime 재검증과 기간 coverage가 충분한지 봅니다.",
        },
        {
            "Section": "Provider / Look-through",
            "Ready": _ready_from_check(provider_check) if provider_check else False,
            "Current": provider_check.get("Current") or _provider_status_summary(validation),
            "Meaning": "ETF 운용성 / holdings / exposure / macro coverage가 검증에 연결됐는지 봅니다.",
        },
        {
            "Section": "Benchmark / Comparator Parity",
            "Ready": _ready_from_check(benchmark_check) if benchmark_check else False,
            "Current": benchmark_check.get("Current") or "-",
            "Meaning": "후보와 benchmark / comparator가 같은 기간 / coverage / frequency로 비교되는지 봅니다.",
        },
        {
            "Section": "Robustness / Stress",
            "Ready": str(robustness.get("robustness_route") or "") == "READY_FOR_STRESS_SWEEP"
            or decision_evidence.get("route") == "READY_FOR_FINAL_DECISION",
            "Current": robustness.get("robustness_route") or decision_evidence.get("route") or "-",
            "Meaning": "stress / sensitivity / robustness 근거가 최종 선택에 충분한지 봅니다.",
        },
        {
            "Section": "Paper Observation",
            "Ready": not bool(paper_observation.get("blockers")),
            "Current": paper_observation.get("route") or "-",
            "Meaning": "모니터링에서 관찰할 benchmark와 trigger seed가 있는지 봅니다.",
        },
        {
            "Section": "Critical Gaps",
            "Ready": not blocking_gaps,
            "Current": str(len(blocking_gaps)),
            "Meaning": "critical NOT_RUN, hard blocker, evidence blocker가 선택을 막는지 봅니다.",
        },
        {
            "Section": "Validation Method Strength Audit",
            "Ready": validation_efficacy_route == "VALIDATION_EFFICACY_READY",
            "Current": (
                f"{validation_efficacy_audit.get('route_label')} / {validation_efficacy_route}"
                if validation_efficacy_audit.get("route_label") and validation_efficacy_route
                else validation_efficacy_route or validation_efficacy_audit.get("route_label") or "-"
            ),
            "Meaning": "walk-forward / OOS / regime split 방법론 evidence gap을 최종 선택 전에 분리해서 봅니다.",
        },
        {
            "Section": "Data Coverage Audit",
            "Ready": data_coverage_route == "DATA_COVERAGE_READY",
            "Current": (
                f"{data_coverage_audit.get('route_label')} / {data_coverage_route}"
                if data_coverage_audit.get("route_label") and data_coverage_route
                else data_coverage_route or data_coverage_audit.get("route_label") or "-"
            ),
            "Meaning": "DB price window, provider freshness, PIT replay, universe / survivorship evidence를 분리해서 봅니다.",
        },
        {
            "Section": "Construction Risk Audit",
            "Ready": construction_risk_route == "CONSTRUCTION_RISK_READY",
            "Current": (
                f"{construction_risk_audit.get('route_label')} / {construction_risk_route}"
                if construction_risk_audit.get("route_label") and construction_risk_route
                else construction_risk_route or construction_risk_audit.get("route_label") or "-"
            ),
            "Meaning": "component weight concentration, provider look-through, top holding / overlap, asset exposure risk를 분리해서 봅니다.",
        },
        {
            "Section": "Risk Contribution Audit",
            "Ready": risk_contribution_route == "RISK_CONTRIBUTION_READY",
            "Current": (
                f"{risk_contribution_audit.get('route_label')} / {risk_contribution_route}"
                if risk_contribution_audit.get("route_label") and risk_contribution_route
                else risk_contribution_route or risk_contribution_audit.get("route_label") or "-"
            ),
            "Meaning": "component return matrix, correlation, risk contribution proxy, drop-one dependency risk를 분리해서 봅니다.",
        },
        {
            "Section": "Component Role / Weight Audit",
            "Ready": component_role_weight_route == "COMPONENT_ROLE_WEIGHT_READY",
            "Current": (
                f"{component_role_weight_audit.get('route_label')} / {component_role_weight_route}"
                if component_role_weight_audit.get("route_label") and component_role_weight_route
                else component_role_weight_route or component_role_weight_audit.get("route_label") or "-"
            ),
            "Meaning": "component role source, profile intent, target weight, weight rationale discipline을 분리해서 봅니다.",
        },
        {
            "Section": "Backtest Realism Audit",
            "Ready": backtest_realism_route == "BACKTEST_REALISM_READY",
            "Current": (
                f"{backtest_realism_audit.get('route_label')} / {backtest_realism_route}"
                if backtest_realism_audit.get("route_label") and backtest_realism_route
                else backtest_realism_route or backtest_realism_audit.get("route_label") or "-"
            ),
            "Meaning": "거래비용, turnover, liquidity, net performance, tax/account scope 같은 실전성 가정을 분리해서 봅니다.",
        },
        {
            "Section": "Execution Boundary",
            "Ready": True,
            "Current": "live approval disabled / order disabled",
            "Meaning": "이 packet은 투자 판단 보조 근거이며 주문이나 자동매매가 아닙니다.",
        },
    ]
    validation_for_gate_policy = dict(validation)
    validation_for_gate_policy.setdefault("validation_efficacy_audit", validation_efficacy_audit)
    validation_for_gate_policy.setdefault("construction_risk_audit", construction_risk_audit)
    validation_for_gate_policy.setdefault("risk_contribution_audit", risk_contribution_audit)
    validation_for_gate_policy.setdefault("component_role_weight_audit", component_role_weight_audit)
    selection_gate_policy = build_investability_gate_policy(
        validation=validation_for_gate_policy,
        paper_observation=paper_observation,
        decision_evidence=decision_evidence,
        packet_checks=checks,
        critical_gaps=critical_gaps,
        policy_mode=GATE_POLICY_MODE_SELECTION,
    )
    deployment_gate_policy = build_investability_gate_policy(
        validation=validation_for_gate_policy,
        paper_observation=paper_observation,
        decision_evidence=decision_evidence,
        packet_checks=checks,
        critical_gaps=critical_gaps,
        policy_mode=GATE_POLICY_MODE_DEPLOYMENT,
    )
    open_review_items = _open_review_items_from_policies(
        selection_policy=selection_gate_policy,
        deployment_policy=deployment_gate_policy,
    )
    checks.append(
        {
            "Section": "Selection Gate Policy",
            "Ready": bool(selection_gate_policy.get("select_allowed")),
            "Current": selection_gate_policy.get("outcome") or "-",
            "Meaning": "Final Review selection gate가 Portfolio Monitoring 추적 후보 선정 가능 여부를 판정합니다.",
        }
    )
    checks.append(
        {
            "Section": "Deployment Readiness Policy",
            "Ready": bool(deployment_gate_policy.get("select_allowed")),
            "Current": deployment_gate_policy.get("outcome") or "-",
            "Meaning": "향후 Live / Deployment Readiness에서 이어서 볼 엄격한 감사 상태입니다.",
        }
    )
    score = round(
        sum(1 for check in checks if bool(check.get("Ready"))) / len(checks) * 10.0,
        1,
    ) if checks else 0.0
    policy_blockers = list(selection_gate_policy.get("blockers") or [])
    policy_review_required = list(selection_gate_policy.get("review_required") or [])
    if policy_blockers:
        route = "INVESTABILITY_PACKET_BLOCKED"
        verdict = "모니터링 후보 선정 차단: selection gate blocker가 남아 있습니다."
        next_action = "validation evidence를 보강한 뒤 Final Review에서 모니터링 후보 가능 여부를 다시 확인합니다."
    elif policy_review_required:
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "모니터링 후보 선정 전 반드시 해소해야 할 review가 남아 있습니다."
        next_action = "부족한 evidence를 보강한 뒤 selected-route gate를 다시 확인합니다."
    elif decision_evidence.get("route") == "READY_FOR_FINAL_DECISION":
        route = "INVESTABILITY_PACKET_READY"
        verdict = "Portfolio Monitoring에서 추적할 모니터링 후보로 기록 가능한 evidence packet입니다."
        next_action = "Final Review 판단을 저장하고, 선택 route라면 open review item은 Portfolio Monitoring / Live Readiness에서 이어서 확인합니다."
    else:
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "hard blocker는 없지만 Final Review evidence가 아직 완전하지 않습니다."
        next_action = "부족한 validation / robustness / observation 근거를 보강합니다."
    return {
        "schema_version": "investability_evidence_packet_v1",
        "route": route,
        "score": score,
        "select_ready": route == "INVESTABILITY_PACKET_READY",
        "verdict": verdict,
        "next_action": next_action,
        "source_chain": source_chain,
        "checks": checks,
        "critical_gaps": critical_gaps,
        "gate_policy_snapshot": selection_gate_policy,
        "selection_gate_policy_snapshot": selection_gate_policy,
        "deployment_readiness_policy_snapshot": deployment_gate_policy,
        "open_review_items": open_review_items,
        "assumptions_and_limits": assumptions,
        "validation_efficacy_audit": validation_efficacy_audit,
        "data_coverage_audit": data_coverage_audit,
        "construction_risk_audit": construction_risk_audit,
        "risk_contribution_audit": risk_contribution_audit,
        "component_role_weight_audit": component_role_weight_audit,
        "backtest_realism_audit": backtest_realism_audit,
        "summary": {
            "pass": int(status_counts.get("PASS", 0) or 0),
            "review": int(status_counts.get("REVIEW", 0) or 0),
            "blocked": int(status_counts.get("BLOCKED", 0) or 0),
            "not_run": int(status_counts.get("NOT_RUN", 0) or 0),
            "provider_status": _provider_status_summary(validation),
            "decision_evidence_route": decision_evidence.get("route"),
            "robustness_route": robustness.get("robustness_route"),
            "gate_policy_outcome": selection_gate_policy.get("outcome"),
            "selection_gate_policy_outcome": selection_gate_policy.get("outcome"),
            "deployment_readiness_policy_outcome": deployment_gate_policy.get("outcome"),
            "open_review_items": len(open_review_items),
            "validation_efficacy_route": validation_efficacy_audit.get("route"),
            "data_coverage_route": data_coverage_audit.get("route"),
            "construction_risk_route": construction_risk_audit.get("route"),
            "risk_contribution_route": risk_contribution_audit.get("route"),
            "component_role_weight_route": component_role_weight_audit.get("route"),
            "backtest_realism_route": backtest_realism_audit.get("route"),
        },
    }


def build_selected_route_gate(
    *,
    decision_route: str,
    investability_packet: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return whether the selected route is allowed by the investability packet."""

    route = str(decision_route or "").strip()
    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    selected = route == SELECT_FOR_PRACTICAL_PORTFOLIO
    select_allowed = bool(gate_policy.get("select_allowed")) if gate_policy else bool(packet.get("select_ready"))
    ready = (not selected) or select_allowed
    current = gate_policy.get("outcome") or packet.get("route") or "packet_not_attached"
    return {
        "Criteria": "Investability evidence packet",
        "Ready": ready,
        "Current": current,
        "Meaning": (
            "Monitoring 후보 handoff는 Final Review selection gate가 허용할 때만 가능합니다. live 투입 판단은 별도 단계입니다."
            if selected
            else "보류 / 거절 / 재검토 판단은 저장할 수 있지만 Monitoring 후보 handoff는 만들지 않습니다."
        ),
    }


def build_final_review_decision_record_guide(
    *,
    decision_route: str,
    decision_evidence: dict[str, Any] | None,
    investability_packet: dict[str, Any] | None,
) -> dict[str, Any]:
    """Explain how the selected final route should be recorded without revalidating evidence."""

    route = str(decision_route or "").strip()
    evidence = dict(decision_evidence or {})
    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    suggested_route = (
        gate_policy.get("suggested_decision_route")
        or evidence.get("suggested_decision_route")
        or SELECT_FOR_PRACTICAL_PORTFOLIO
    )
    selected_gate = build_selected_route_gate(
        decision_route=route,
        investability_packet=packet,
    )
    selected = route == SELECT_FOR_PRACTICAL_PORTFOLIO
    valid_route = route in FINAL_REVIEW_DECISION_LABELS
    route_templates = dict(
        FINAL_REVIEW_DECISION_RECORD_TEMPLATES.get(
            route,
            FINAL_REVIEW_DECISION_RECORD_TEMPLATES["RE_REVIEW_REQUIRED"],
        )
    )
    if selected and not bool(selected_gate.get("Ready")):
        route_state = "SELECT_ROUTE_BLOCKED"
        route_state_label = "Monitoring handoff 차단"
        notice_level = "warning"
        notice = "Monitoring 후보 handoff는 Final Review selection gate가 허용할 때만 활성화됩니다. 보류 / 재검토 / 거절은 Final Review 판단 기록으로 저장할 수 있습니다."
    elif selected:
        route_state = "SELECT_ROUTE_READY"
        route_state_label = "선정 기록 가능"
        notice_level = "success"
        notice = "현재 selection gate가 선정 기록을 허용합니다. 판단 사유를 남기면 최종 검토 기록으로 저장할 수 있습니다."
    else:
        route_state = "JUDGMENT_ROUTE_READY" if valid_route else "INVALID_ROUTE"
        route_state_label = "판단 기록 가능" if valid_route else "판단 route 확인 필요"
        notice_level = "info"
        notice = "보류 / 거절 / 재검토는 Final Review 판단 기록으로 저장됩니다. Monitoring 후보 handoff는 선택 route가 gate를 통과할 때만 만들어집니다."
    checklist_rows = [
        {
            "Criteria": "Suggested decision",
            "Ready": True,
            "Current": "matches suggestion" if route == suggested_route else "manual override",
            "Meaning": f"권장 route는 {_decision_route_label(suggested_route)}입니다.",
        },
        {
            "Criteria": "Selected route",
            "Ready": valid_route,
            "Current": _decision_route_label(route) if valid_route else route or "-",
            "Meaning": "최종 판단으로 저장될 route입니다.",
        },
        {
            "Criteria": "Monitoring handoff",
            "Ready": True,
            "Current": "requested" if selected else "not requested",
            "Meaning": "Monitoring 후보 handoff는 선택 route에서만 요청됩니다. non-select route는 판단 기록으로만 남습니다.",
        },
        selected_gate,
        {
            "Criteria": "Operator reason",
            "Ready": True,
            "Current": "required at save",
            "Meaning": "저장 가능 여부는 실제 판단 사유 입력 후 최종 save gate에서 다시 확인합니다.",
        },
        {
            "Criteria": "Live approval / order",
            "Ready": True,
            "Current": "disabled",
            "Meaning": "Final Review는 승인, 주문, 계좌 연동, 자동 리밸런싱을 만들지 않습니다.",
        },
    ]
    blockers = [str(row.get("Criteria")) for row in checklist_rows if not bool(row.get("Ready"))]
    return {
        "schema_version": DECISION_RECORD_GUIDE_SCHEMA_VERSION,
        "decision_route": route,
        "decision_label": _decision_route_label(route),
        "suggested_decision_route": suggested_route,
        "suggested_decision_label": _decision_route_label(suggested_route),
        "route_state": route_state,
        "route_state_label": route_state_label,
        "notice_level": notice_level,
        "notice": notice,
        "selected_route_gate": selected_gate,
        "recordable_route": valid_route and ((not selected) or bool(selected_gate.get("Ready"))),
        "monitoring_handoff_candidate": valid_route and selected and bool(selected_gate.get("Ready")),
        "checklist_rows": checklist_rows,
        "blockers": blockers,
        "route_templates": route_templates,
        "record_boundary": {
            "write_policy": "append_final_review_decision_record",
            "validation_rerun": False,
            "provider_fetch": False,
            "waiver_persistence": False,
            "non_select_persistence": True,
            "monitoring_handoff": valid_route and selected and bool(selected_gate.get("Ready")),
            "live_approval": False,
            "order_instruction": False,
            "account_sync": False,
            "auto_rebalance": False,
        },
    }


def build_final_review_save_handoff_summary(*, decision_record_guide: dict[str, Any]) -> dict[str, Any]:
    """Summarize the difference between judgment persistence and Monitoring handoff."""

    guide = dict(decision_record_guide or {})
    decision_route = str(guide.get("decision_route") or "").strip()
    selected_route = decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO
    recordable = bool(guide.get("recordable_route"))
    handoff_candidate = bool(guide.get("monitoring_handoff_candidate"))
    selected_gate = dict(guide.get("selected_route_gate") or {})
    if handoff_candidate:
        handoff_state = "ready"
        handoff_label = "Monitoring handoff ready"
        handoff_detail = "선택 route와 selection gate가 모두 통과해 Portfolio Monitoring 후보로 연결됩니다."
        record_type = "monitoring_candidate"
    elif selected_route:
        handoff_state = "blocked"
        handoff_label = "Monitoring handoff blocked"
        handoff_detail = "선택 route를 요청했지만 selection gate가 통과하지 않아 Monitoring handoff가 차단됩니다."
        record_type = "blocked_selected_route"
    else:
        handoff_state = "not_requested"
        handoff_label = "Decision only"
        handoff_detail = "보류 / 거절 / 재검토는 Final Review 판단 기록으로만 남고 Monitoring 후보로 연결되지 않습니다."
        record_type = "judgment_decision"
    return {
        "schema_version": SAVE_HANDOFF_SUMMARY_SCHEMA_VERSION,
        "decision_route": decision_route,
        "decision_label": guide.get("decision_label") or _decision_route_label(decision_route),
        "record_type": record_type,
        "judgment_record": {
            "ready": recordable,
            "label": "Final Review 판단 저장 가능" if recordable else "Final Review 판단 저장 확인 필요",
            "detail": guide.get("notice") or "-",
        },
        "monitoring_handoff": {
            "candidate": handoff_candidate,
            "state": handoff_state,
            "label": handoff_label,
            "detail": handoff_detail,
            "selected_gate_ready": bool(selected_gate.get("Ready")),
            "selected_gate_current": selected_gate.get("Current") or "-",
        },
        "boundaries": {
            "append_final_review_decision_record": True,
            "non_select_persistence": True,
            "monitoring_handoff_requires_selected_route": True,
            "validation_rerun": False,
            "provider_fetch": False,
            "live_approval": False,
            "order_instruction": False,
            "account_sync": False,
            "auto_rebalance": False,
        },
    }


def _decision_route_label(route: Any) -> str:
    return FINAL_REVIEW_DECISION_LABELS.get(_safe_text(route, ""), "재검토 필요")


def _is_monitoring_handoff_candidate(row: dict[str, Any]) -> bool:
    if "monitoring_candidate" in row:
        return row.get("monitoring_candidate") is True
    return (
        row.get("selected_practical_portfolio") is True
        or str(row.get("decision_route") or "").strip() == SELECT_FOR_PRACTICAL_PORTFOLIO
    )


def _policy_rows_by_severity(gate_policy: dict[str, Any], severity: str) -> list[dict[str, Any]]:
    target = str(severity or "").upper()
    return [
        dict(row or {})
        for row in list(dict(gate_policy or {}).get("policy_rows") or [])
        if str(dict(row or {}).get("Severity") or "").upper() == target
    ]


def _decision_cockpit_state(gate_policy: dict[str, Any], packet: dict[str, Any]) -> tuple[str, str, str]:
    outcome = str(dict(gate_policy or {}).get("outcome") or "").strip()
    route = str(dict(packet or {}).get("route") or "").strip()
    if outcome == "select_ready" or route == "INVESTABILITY_PACKET_READY":
        return (
            "SELECT_READY",
            "모니터링 후보 가능",
            "현재 gate policy상 Portfolio Monitoring 후보로 저장할 수 있습니다.",
        )
    if outcome == "blocked" or route == "INVESTABILITY_PACKET_BLOCKED":
        return (
            "SELECT_BLOCKED",
            "선정 차단",
            "critical blocker가 남아 있어 Monitoring 후보 handoff가 차단됩니다.",
        )
    return (
        "HOLD_OR_RE_REVIEW",
        "보류 / 재검토 권장",
        "hard blocker는 아니지만 선정 전 확인해야 할 review-required 근거가 남아 있습니다.",
    )


def _candidate_board_state_priority(state: Any) -> int:
    state_text = str(state or "").upper()
    if state_text == "SELECT_READY":
        return 1
    if state_text == "HOLD_OR_RE_REVIEW":
        return 2
    return 3


def _candidate_board_policy_reason(rows: list[dict[str, Any]], fallback: str) -> str:
    if not rows:
        return fallback
    row = dict(rows[0] or {})
    label = _safe_text(row.get("Criteria") or row.get("Group"), "Evidence")
    evidence = _safe_text(row.get("Required Action") or row.get("Evidence") or row.get("Current"), fallback)
    return f"{label}: {evidence}"


def _candidate_board_action(cockpit: dict[str, Any]) -> tuple[str, str, str]:
    state = str(dict(cockpit or {}).get("state") or "").upper()
    if state == "SELECT_READY":
        return (
            "모니터링 후보 선정",
            "모니터링 후보로 저장 가능한 상태입니다. 투자 검토서와 선정 조건을 확인한 뒤 Portfolio Monitoring 추적 후보로 저장합니다.",
            "모니터링 후보 가능",
        )
    if state == "SELECT_BLOCKED":
        return (
            "차단 원인 해소",
            _candidate_board_policy_reason(
                list(dict(cockpit or {}).get("must_fix_rows") or []),
                "critical blocker를 먼저 해소한 뒤 다시 확인합니다.",
            ),
            "선정 차단",
        )
    return (
        "보강 후 재확인",
        _candidate_board_policy_reason(
            list(dict(cockpit or {}).get("must_review_rows") or []),
            "review-required 근거를 확인하고 evidence를 보강합니다.",
        ),
        "보류 필요",
    )


def build_final_review_decision_cockpit(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    investability_packet: dict[str, Any],
) -> dict[str, Any]:
    """Build the summary that Final Review should show before detailed evidence tables."""

    source = dict(source or {})
    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    source_chain = dict(packet.get("source_chain") or {})
    summary = dict(packet.get("summary") or {})
    state, state_label, verdict = _decision_cockpit_state(gate_policy, packet)
    suggested_route = (
        gate_policy.get("suggested_decision_route")
        or decision_evidence.get("suggested_decision_route")
        or SELECT_FOR_PRACTICAL_PORTFOLIO
    )
    must_fix = _policy_rows_by_severity(gate_policy, "BLOCK")
    must_review = _policy_rows_by_severity(gate_policy, "REVIEW_REQUIRED")
    watch_rows = _policy_rows_by_severity(gate_policy, "WATCH")
    ready_rows = _policy_rows_by_severity(gate_policy, "PASS")
    baseline = dict(paper_observation.get("baseline_snapshot") or {})
    return {
        "schema_version": "final_review_decision_cockpit_v1",
        "state": state,
        "state_label": state_label,
        "verdict": verdict,
        "next_action": gate_policy.get("next_action") or packet.get("next_action") or decision_evidence.get("next_action") or "-",
        "suggested_decision_route": suggested_route,
        "suggested_decision_label": _decision_route_label(suggested_route),
        "select_allowed": bool(gate_policy.get("select_allowed")),
        "packet_route": packet.get("route"),
        "packet_score": packet.get("score"),
        "gate_outcome": gate_policy.get("outcome"),
        "source_chain": source_chain,
        "source_title": source.get("source_title") or validation.get("source_title") or source_chain.get("source_id") or "-",
        "source_type": source.get("source_type") or validation.get("source_type") or source_chain.get("source_type") or "-",
        "blockers": list(gate_policy.get("blockers") or []),
        "review_required": list(gate_policy.get("review_required") or []),
        "critical_gaps": list(packet.get("critical_gaps") or []),
        "must_fix_rows": must_fix,
        "must_review_rows": must_review,
        "watch_rows": watch_rows,
        "open_review_items": list(packet.get("open_review_items") or []),
        "ready_rows": ready_rows,
        "monitoring_handoff": {
            "route": paper_observation.get("route"),
            "review_cadence": paper_observation.get("review_cadence"),
            "tracking_benchmark": paper_observation.get("tracking_benchmark"),
            "review_triggers": list(paper_observation.get("review_triggers") or []),
            "active_components": len(paper_observation.get("active_components") or []),
            "target_weight_total": baseline.get("target_weight_total"),
        },
        "metrics": {
            "not_run": summary.get("not_run", 0),
            "review": summary.get("review", 0),
            "blocked": summary.get("blocked", 0),
            "policy_blockers": len(gate_policy.get("blockers") or []),
            "policy_review_required": len(gate_policy.get("review_required") or []),
            "critical_gaps": len(packet.get("critical_gaps") or []),
            "open_review_items": len(packet.get("open_review_items") or []),
            "provider_status": summary.get("provider_status") or "-",
            "validation_efficacy_route": summary.get("validation_efficacy_route") or "-",
            "data_coverage_route": summary.get("data_coverage_route") or "-",
            "backtest_realism_route": summary.get("backtest_realism_route") or "-",
        },
    }


def _report_tone_from_state(state: Any) -> str:
    state_text = str(state or "").upper()
    if state_text == "SELECT_READY":
        return "positive"
    if state_text == "SELECT_BLOCKED":
        return "danger"
    return "warning"


def _score_band(score: Any, state: Any) -> str:
    numeric = _float_or_none(score)
    state_text = str(state or "").upper()
    if state_text == "SELECT_BLOCKED":
        return "차단"
    if numeric is None:
        return "미산정"
    if state_text == "SELECT_READY" and numeric < 6.0:
        return "선정 가능 / 보강 추적"
    if numeric >= 8.0:
        return "강함"
    if numeric >= 6.0:
        return "보류권"
    return "취약"


def _report_policy_card(row: dict[str, Any], *, fallback_title: str, tone: str) -> dict[str, Any]:
    return {
        "title": _safe_text(row.get("Criteria") or row.get("Group"), fallback_title),
        "detail": _safe_text(row.get("Evidence") or row.get("Current"), "-"),
        "action": _safe_text(row.get("Required Action") or row.get("Next Action"), "-"),
        "severity": _safe_text(row.get("Severity"), "PASS"),
        "tone": tone,
    }


def _score_limit_summary(score_limits: list[dict[str, Any]]) -> str:
    if not score_limits:
        return "score cap 없음"
    caps = [int(limit.get("cap") or 100) for limit in score_limits if isinstance(limit, dict)]
    cap = min(caps) if caps else 100
    return f"score cap {cap} 적용"


def _report_dimension_strengths(scorecard: dict[str, Any]) -> list[dict[str, Any]]:
    strengths: list[dict[str, Any]] = []
    for dimension in list(dict(scorecard or {}).get("dimensions") or []):
        if not isinstance(dimension, dict):
            continue
        score = int(dimension.get("score") or 0)
        if score < 80:
            continue
        strengths.append(
            {
                "title": _safe_text(dimension.get("label"), "Score strength"),
                "detail": f"{score}/100 - {_safe_text(dimension.get('interpretation'), '-')}",
                "action": _safe_text(dimension.get("evidence"), "현재 Final Review scorecard 근거를 유지합니다."),
                "severity": "HIGH_SCORE",
                "tone": _safe_text(dimension.get("tone"), "positive"),
            }
        )
    return strengths[:4]


def _report_strengths(cockpit: dict[str, Any], packet: dict[str, Any], scorecard: dict[str, Any] | None = None) -> list[dict[str, Any]]:
    dimension_strengths = _report_dimension_strengths(scorecard or {})
    policy_strengths = [
        _report_policy_card(dict(row or {}), fallback_title="Evidence ready", tone="positive")
        for row in list(cockpit.get("ready_rows") or [])
        if isinstance(row, dict)
    ]
    strengths = dimension_strengths + policy_strengths
    if strengths:
        deduped: list[dict[str, Any]] = []
        seen: set[str] = set()
        for strength in strengths:
            title = _safe_text(strength.get("title"), "")
            if title in seen:
                continue
            seen.add(title)
            deduped.append(strength)
        return deduped[:6]
    fallback_rows = [
        dict(row or {})
        for row in list(packet.get("checks") or [])
        if isinstance(row, dict) and _ready_from_check(dict(row or {}))
    ]
    return [
        {
            "title": _safe_text(row.get("Section") or row.get("Criteria"), "Evidence ready"),
            "detail": _safe_text(row.get("Meaning") or row.get("Current"), "-"),
            "action": "추가 조치 없음",
            "severity": "PASS",
            "tone": "positive",
        }
        for row in fallback_rows[:6]
    ]


def _dimension_by_rank(scorecard: dict[str, Any], *, strongest: bool) -> dict[str, Any]:
    dimensions = [dict(row or {}) for row in list(dict(scorecard or {}).get("dimensions") or []) if isinstance(row, dict)]
    if not dimensions:
        return {}
    return (max if strongest else min)(dimensions, key=lambda row: int(row.get("score") or 0))


def _dimension_detail(dimension: dict[str, Any]) -> str:
    if not dimension:
        return "확인할 세부 점수 없음"
    return (
        f"{_safe_text(dimension.get('label'), '-')} {int(dimension.get('score') or 0)}/100 - "
        f"{_safe_text(dimension.get('interpretation'), '-')}"
    )


def _build_decision_summary(
    *,
    scorecard: dict[str, Any],
    selection_rationale: dict[str, Any],
) -> dict[str, Any]:
    overall = int(dict(scorecard or {}).get("overall_score") or 0)
    pre_cap = int(dict(scorecard or {}).get("pre_cap_score") or overall)
    score_limits = [dict(row or {}) for row in list(dict(scorecard or {}).get("score_limits") or []) if isinstance(row, dict)]
    strongest = _dimension_by_rank(scorecard, strongest=True)
    weakest = _dimension_by_rank(scorecard, strongest=False)
    dimensions = {str(row.get("key") or ""): dict(row or {}) for row in list(dict(scorecard or {}).get("dimensions") or []) if isinstance(row, dict)}
    readiness = dimensions.get("readiness", {})
    classification_label = _safe_text(scorecard.get("classification_label"), _safe_text(selection_rationale.get("classification_label"), "-"))
    monitoring_candidate = bool(scorecard.get("monitoring_candidate"))
    headline = (
        "모니터링 후보로 검토할 수 있습니다"
        if monitoring_candidate
        else f"{classification_label} 상태로 추가 판단 필요"
    )
    limit_summary = _score_limit_summary(score_limits)
    inputs = dict(dict(scorecard or {}).get("inputs") or {})
    review_summary = (
        f"warning {int(inputs.get('warning_count') or 0)}, "
        f"open {int(inputs.get('open_review_count') or 0)}, "
        f"monitoring {int(inputs.get('monitoring_followup_count') or 0)}"
    )
    items = [
        {
            "label": "최종 선택 사유",
            "detail": _safe_text(selection_rationale.get("decision_reason"), "-"),
            "tone": "positive" if monitoring_candidate else "warning",
            "source": "selection_rationale",
        },
        {
            "label": "가장 강한 근거",
            "detail": _dimension_detail(strongest),
            "tone": _safe_text(strongest.get("tone"), "neutral"),
            "source": "scorecard",
        },
        {
            "label": "Monitoring 준비도",
            "detail": _dimension_detail(readiness),
            "tone": _safe_text(readiness.get("tone"), "neutral"),
            "source": "scorecard",
        },
        {
            "label": "가장 큰 확인 지점",
            "detail": _dimension_detail(weakest),
            "tone": _safe_text(weakest.get("tone"), "neutral"),
            "source": "scorecard",
        },
        {
            "label": "Level2 REVIEW 반영",
            "detail": review_summary,
            "tone": "warning" if int(inputs.get("open_review_count") or 0) else "neutral",
            "source": "level2_review_disposition",
        },
    ]
    if score_limits:
        items.append(
            {
                "label": "점수 제한",
                "detail": "; ".join(_safe_text(limit.get("detail"), _safe_text(limit.get("label"), "-")) for limit in score_limits),
                "tone": "warning",
                "source": "scorecard",
            }
        )
    return {
        "schema_version": DECISION_SUMMARY_SCHEMA_VERSION,
        "headline": headline,
        "status_label": classification_label,
        "score_line": f"종합 {overall}/100, 원점수 {pre_cap}/100, {limit_summary}",
        "items": items,
        "boundary": {
            "provider_fetch": False,
            "storage_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


def _build_interpretation_cards(
    *,
    scorecard: dict[str, Any],
    cockpit: dict[str, Any],
    packet: dict[str, Any],
    monitoring: dict[str, Any],
) -> list[dict[str, Any]]:
    dimensions = {str(row.get("key") or ""): dict(row or {}) for row in list(dict(scorecard or {}).get("dimensions") or []) if isinstance(row, dict)}
    inputs = dict(dict(scorecard or {}).get("inputs") or {})
    trigger_count = len(list(dict(monitoring or {}).get("review_triggers") or []))
    blocker_count = int(inputs.get("blocker_count") or 0)
    open_review_count = int(inputs.get("open_review_count") or 0)
    inherited_limit_count = int(inputs.get("warning_count") or 0)
    score_limits = [dict(row or {}) for row in list(dict(scorecard or {}).get("score_limits") or []) if isinstance(row, dict)]
    investment = dimensions.get("investment", {})
    evidence_quality = dimensions.get("evidence_quality", {})
    weakest = _dimension_by_rank(scorecard, strongest=False)
    weakest_label = {
        "investment": "투자 매력도",
        "evidence_quality": "근거 신뢰도",
        "readiness": "선정 준비도",
        "monitoring_suitability": "Monitoring 적합성",
    }.get(str(weakest.get("key") or ""), _safe_text(weakest.get("label"), "확인 지점"))
    weakest_summary = f"{weakest_label} {int(weakest.get('score') or 0)}/100"
    overall = int(dict(scorecard or {}).get("overall_score") or 0)
    cadence_raw = _safe_text(monitoring.get("review_cadence"), "미지정")
    cadence_label = {
        "monthly_or_rebalance_review": "월 1회 또는 리밸런싱 시점",
        "monthly": "월 1회",
        "quarterly": "분기 1회",
    }.get(cadence_raw, cadence_raw)
    benchmark = _safe_text(monitoring.get("tracking_benchmark"), "미지정")
    return [
        {
            "schema_version": INTERPRETATION_CARD_SCHEMA_VERSION,
            "kind": "performance_interpretation",
            "title": "성과 해석",
            "detail": (
                f"과거 성과와 실전성 근거를 합친 투자 매력도는 {int(investment.get('score') or 0)}/100입니다. "
                "미래 수익 예측이 아니라 현재 후보끼리 비교하기 위한 점수입니다."
            ),
            "tone": _safe_text(investment.get("tone"), "neutral"),
            "badges": [
                f"투자 매력도 {int(investment.get('score') or 0)}/100",
                f"종합 {overall}/100",
                f"점수 상한 {min(int(row.get('cap') or 100) for row in score_limits)}/100" if score_limits else "점수 제한 없음",
            ],
        },
        {
            "schema_version": INTERPRETATION_CARD_SCHEMA_VERSION,
            "kind": "risk_interpretation",
            "title": "위험 해석",
            "detail": (
                f"현재 가장 약한 판단 축은 {weakest_summary}입니다. "
                f"선정 차단 {blocker_count}개, 사용자가 결정할 항목 {open_review_count}개를 구분해 봅니다."
            ),
            "tone": "danger" if blocker_count else ("warning" if int(weakest.get("score") or 0) < 70 else "positive"),
            "badges": [
                f"선정 차단 {blocker_count}",
                f"직접 결정 {open_review_count}",
            ],
        },
        {
            "schema_version": INTERPRETATION_CARD_SCHEMA_VERSION,
            "kind": "evidence_confidence",
            "title": "근거 신뢰도",
            "detail": (
                f"저장된 검증 근거의 신뢰도는 {int(evidence_quality.get('score') or 0)}/100입니다. "
                f"2단계에서 허용한 제한 {inherited_limit_count}개는 투자 매력도와 분리해 해석 확신에 반영했습니다."
            ),
            "tone": _safe_text(evidence_quality.get("tone"), "neutral"),
            "badges": [
                f"근거 신뢰도 {int(evidence_quality.get('score') or 0)}/100",
                f"인수 제한 {inherited_limit_count}",
            ],
        },
        {
            "schema_version": INTERPRETATION_CARD_SCHEMA_VERSION,
            "kind": "monitoring_fit",
            "title": "Monitoring 적합성",
            "detail": (
                f"선정한다면 {cadence_label}에 {trigger_count}개 변화 조건을 확인합니다. "
                f"비교 기준은 {benchmark}이며, 조건 이탈 시 후보를 다시 검토합니다."
            ),
            "tone": _safe_text(dimensions.get("monitoring_suitability", {}).get("tone"), "neutral"),
            "badges": [f"점검 주기 {cadence_label}", f"변화 조건 {trigger_count}개"],
        },
    ]


def _build_watch_items(
    *,
    weaknesses: list[dict[str, Any]],
    scorecard: dict[str, Any],
) -> list[dict[str, Any]]:
    if weaknesses:
        return [dict(row or {}) for row in weaknesses[:4] if isinstance(row, dict)]
    weakest = _dimension_by_rank(scorecard, strongest=False)
    score_limits = [dict(row or {}) for row in list(dict(scorecard or {}).get("score_limits") or []) if isinstance(row, dict)]
    items = [
        {
            "title": "확인 지점",
            "detail": _dimension_detail(weakest),
            "action": "Monitoring에서 이 차원의 score 변화와 review trigger를 같이 봅니다.",
            "severity": "WATCH",
            "tone": _safe_text(weakest.get("tone"), "neutral"),
        }
    ]
    for limit in score_limits[:2]:
        items.append(
            {
                "title": _safe_text(limit.get("label"), "점수 제한"),
                "detail": _safe_text(limit.get("detail") or limit.get("reason"), "-"),
                "action": f"cap {int(limit.get('cap') or 0)} 기준을 확인합니다.",
                "severity": "SCORE_CAP",
                "tone": _safe_text(limit.get("tone"), "warning"),
            }
        )
    return items[:4]


def _report_weaknesses(cockpit: dict[str, Any]) -> list[dict[str, Any]]:
    rows = []
    for gap in list(cockpit.get("critical_gaps") or []):
        if not isinstance(gap, dict):
            continue
        gap_row = dict(gap or {})
        severity = "BLOCK" if str(gap_row.get("Severity") or "").upper() == "BLOCK" else "REVIEW_REQUIRED"
        rows.append(
            {
                "title": _safe_text(gap_row.get("Area"), "Critical gap"),
                "detail": _safe_text(gap_row.get("Gap"), "-"),
                "action": _safe_text(gap_row.get("Required Action"), "-"),
                "severity": severity,
                "tone": "danger" if severity == "BLOCK" else "warning",
            }
        )
    for row in list(cockpit.get("must_fix_rows") or []):
        if isinstance(row, dict):
            rows.append(_report_policy_card(dict(row or {}), fallback_title="Selection blocker", tone="danger"))
    for row in list(cockpit.get("must_review_rows") or []):
        if isinstance(row, dict):
            rows.append(_report_policy_card(dict(row or {}), fallback_title="Review required", tone="warning"))
    return rows[:6]


def _review_disposition_for_role(role: str, status: str) -> tuple[str, str, str]:
    role_text = str(role or "").strip()
    status_text = str(status or "").strip().upper()
    if status_text in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"} or role_text == "final_readiness_blocker":
        return "blocker", "Blocker", "danger"
    if role_text in {"pv_data_caution", "pv_practical_caution"}:
        return "warning", "Warning", "warning"
    if role_text == "monitoring_followup":
        return "monitoring_followup", "Monitoring follow-up", "neutral"
    return "open_review", "Open review", "warning"


def _level2_review_cards(validation: dict[str, Any]) -> list[dict[str, Any]]:
    workspace = dict(validation.get("practical_validation_workspace") or {})
    groups = list(workspace.get("criteria_detail_groups") or workspace.get("visible_criteria_detail_groups") or [])
    cards = [
        dict(card or {})
        for group in groups
        for card in list(dict(group or {}).get("criteria_cards") or [])
        if isinstance(card, dict)
    ]
    fallback_rows = [
        *list(validation.get("validation_module_display_rows") or []),
        *list(validation.get("validation_modules") or []),
    ]
    fallback_cards = [dict(row or {}) for row in fallback_rows if isinstance(row, dict)]
    if not cards:
        return fallback_cards
    # The workspace contains the most readable Level2 cautions, while the module
    # contract can contain Final Review / Monitoring roles omitted from that view.
    existing_roles = {str(card.get("review_role") or "") for card in cards}
    cards.extend(
        card
        for card in fallback_cards
        if str(card.get("review_role") or "")
        and str(card.get("review_role") or "") not in existing_roles
    )
    return cards


def _level2_review_action(role: str) -> dict[str, str]:
    actions = {
        "pv_data_caution": {
            "action_outcome": "score_reflected",
            "action_label": "이미 신뢰도에 반영",
            "action_detail": "2단계에서 인수한 데이터 제한입니다. Final Review에서 다시 해결하지 않습니다.",
        },
        "pv_practical_caution": {
            "action_outcome": "score_reflected",
            "action_label": "이미 신뢰도에 반영",
            "action_detail": "2단계에서 허용한 측정 제한입니다. Final Review에서는 판단의 확신 수준에만 반영합니다.",
        },
        "final_decision_input": {
            "action_outcome": "pre_save_check",
            "action_label": "선택·보류 사유에 반영",
            "action_detail": "사용자가 지금 선택 또는 보류 판단에 반영해야 하는 항목입니다.",
        },
        "monitoring_followup": {
            "action_outcome": "monitoring_condition",
            "action_label": "추적 조건으로 확정",
            "action_detail": "선정한다면 Portfolio Monitoring에서 추적할 조건으로 확정합니다.",
        },
        "final_readiness_blocker": {
            "action_outcome": "blocker",
            "action_label": "2단계에서 해소 필요",
            "action_detail": "해소 전에는 Monitoring 후보로 선정할 수 없습니다.",
        },
    }
    return dict(actions.get(role) or actions["final_decision_input"])


def _review_trace_value(card: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = card.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return "-"


_FINAL_REVIEW_TRACE_SOURCES: dict[str, tuple[str, str]] = {
    "data_coverage": ("data_coverage_audit", "데이터 품질 / 편향 통제 audit"),
    "backtest_realism": ("backtest_realism_audit", "실전 운용 현실성 audit"),
    "validation_efficacy": ("validation_efficacy_audit", "검증 방법론 강도 audit"),
    "construction_risk": ("construction_risk_audit", "포트폴리오 구성 audit"),
    "risk_contribution": ("risk_contribution_audit", "위험 기여 audit"),
    "component_role_weight": ("component_role_weight_audit", "Component 역할 / 비중 audit"),
    "provider_investability": ("provider_coverage", "ETF 운용사 evidence"),
    "stress_robustness": ("robustness_validation", "Stress / sensitivity evidence"),
}


_FINAL_REVIEW_TRACE_PRESENTATION: dict[str, tuple[str, str]] = {
    "Provider snapshot freshness": (
        "ETF·외부 데이터 최신성",
        "ETF 비용·운용성·보유 종목 자료가 현재 판단에 사용할 만큼 최근 자료인지 확인합니다.",
    ),
    "Universe / listing evidence": (
        "종목 목록과 상장 이력 반영",
        "현재 종목 목록뿐 아니라 상장 시점과 종목별 데이터 이력이 검증 기간에 맞게 반영됐는지 확인합니다.",
    ),
    "Survivorship / delisting control": (
        "상장폐지 종목 포함 여부",
        "현재 살아남은 종목만 사용해 성과가 과대평가되는 생존편향을 통제했는지 확인합니다.",
    ),
    "Price DB window coverage": (
        "가격 데이터 기간 충족 여부",
        "후보를 구성하는 각 종목의 가격 데이터가 선택한 백테스트 기간을 모두 덮는지 확인합니다.",
    ),
    "PIT price window coverage": (
        "시점 기준 가격 재현 범위",
        "당시 알 수 있었던 가격만 사용해 같은 기간을 다시 계산할 수 있는지 확인합니다.",
    ),
    "Cost / slippage sensitivity evidence": (
        "거래비용 변화 민감도",
        "수수료와 체결 오차를 높였을 때에도 결과 해석이 유지되는지 확인합니다.",
    ),
    "Liquidity / operability evidence": (
        "실제 거래 가능성과 유동성",
        "후보 ETF를 현실적으로 거래할 수 있는지와 관련 자료가 충분히 최신인지 확인합니다.",
    ),
    "Tax / account scope": (
        "세금·계좌 조건 반영 범위",
        "세금과 계좌 유형에 따라 달라지는 실현 성과를 현재 검증이 어디까지 반영했는지 확인합니다.",
    ),
    "Walk-forward temporal validation": (
        "기간을 이동한 반복 검증",
        "검증 구간을 순차적으로 옮겨도 특정 한 시기에만 좋은 결과가 나오는지 확인합니다.",
    ),
    "Regime split validation": (
        "시장 국면별 성과 검증",
        "시장 환경을 여러 구간으로 나눴을 때 취약한 국면이 있는지 확인합니다.",
    ),
    "Exclude last 12M": (
        "최근 12개월 제외 검증",
        "최근 성과를 제외해도 장기 결과의 방향이 유지되는지 확인합니다.",
    ),
    "Exclude first 12M": (
        "초기 12개월 제외 검증",
        "초기 구간의 우연한 성과를 제외해도 결과가 유지되는지 확인합니다.",
    ),
    "Relative Strength perturbation": (
        "모멘텀 기간 변경 검증",
        "상대강도 계산 기간을 바꿔도 전략 결과가 과도하게 흔들리지 않는지 확인합니다.",
    ),
    "GTAA parameter perturbation": (
        "GTAA 설정 변경 검증",
        "리밸런싱 주기 등 GTAA 핵심 설정을 바꿔도 결과가 유지되는지 확인합니다.",
    ),
    "Component weight concentration": (
        "구성 비중 집중도",
        "한 전략 또는 구성요소의 비중이 포트폴리오 전체를 지배하는지 확인합니다.",
    ),
    "Provider look-through coverage": (
        "ETF 내부 구성 확인 범위",
        "ETF 내부 보유 종목과 자산 노출을 실제 자료로 얼마나 확인했는지 측정합니다.",
    ),
    "Top holding concentration": (
        "상위 보유 종목 집중도",
        "ETF 내부의 한 종목이 전체 포트폴리오 위험을 과도하게 좌우하는지 확인합니다.",
    ),
    "Holdings overlap": (
        "ETF 간 보유 종목 중복",
        "서로 다른 ETF가 같은 종목을 반복 보유해 분산 효과가 약해지는지 확인합니다.",
    ),
    "Pairwise correlation": (
        "구성요소 간 상관관계",
        "구성요소가 함께 움직여 기대한 분산 효과가 약해지는지 확인합니다.",
    ),
    "Risk contribution concentration": (
        "위험 기여 집중도",
        "표면 비중과 별개로 한 구성요소가 실제 변동 위험을 과도하게 만들고 있는지 확인합니다.",
    ),
    "Profile-aware weight discipline": (
        "목표 성격에 맞는 비중",
        "후보의 운용 목적과 비교해 특정 구성요소 비중이 지나치게 큰지 확인합니다.",
    ),
    "Role concentration discipline": (
        "구성 역할 집중도",
        "방어·성장·헤지 같은 하나의 역할에 포트폴리오가 과도하게 치우쳤는지 확인합니다.",
    ),
    "ETF Operability": (
        "ETF 거래 가능성 근거",
        "ETF 비용과 거래 가능성을 공식 자료 또는 DB 근거로 확인할 수 있는지 봅니다.",
    ),
    "ETF Holdings": (
        "ETF 보유 종목 근거",
        "ETF 내부 보유 종목을 공식 자료로 얼마나 확인했는지 봅니다.",
    ),
    "ETF Exposure": (
        "ETF 자산·섹터 노출 근거",
        "ETF의 자산군과 섹터 노출을 공식 자료로 얼마나 확인했는지 봅니다.",
    ),
    "Dot-com bust / early-2000s bear market": (
        "닷컴버블 붕괴 구간",
        "2000년대 초 장기 약세장에서 후보가 어떻게 움직였을지 확인하는 역사적 충격 검증입니다.",
    ),
    "9/11 market closure and reopening stress": (
        "9·11 시장 충격 구간",
        "시장 폐쇄와 재개가 있었던 단기 충격 구간에서의 반응을 확인합니다.",
    ),
    "Global financial crisis bear market": (
        "글로벌 금융위기 구간",
        "2007~2009년 금융위기 약세장에서의 손실과 회복력을 확인합니다.",
    ),
}


def _review_trace_presentation(label: str) -> tuple[str, str]:
    normalized_label = label.lower().replace("/", " ")
    if "tax" in normalized_label and "account" in normalized_label:
        return _FINAL_REVIEW_TRACE_PRESENTATION["Tax / account scope"]
    if label.startswith("Drop-one: "):
        component = label.split(":", 1)[1].strip()
        return (
            f"{component} 제외 검증",
            "해당 구성요소를 제외했을 때 성과와 위험이 얼마나 달라지는지 확인합니다.",
        )
    return _FINAL_REVIEW_TRACE_PRESENTATION.get(
        label,
        (label, "저장된 2단계 세부 근거를 사용해 이 항목이 최종 판단에 미치는 영향을 확인합니다."),
    )


def _review_trace_status_label(status: str, observed_value: str) -> str:
    normalized = str(status or "").strip().upper()
    if str(observed_value or "").strip() == "기간 미포함":
        return "검증 기간 밖"
    return {
        "PASS": "충분",
        "READY": "충분",
        "REVIEW": "일부 확인",
        "NEEDS_INPUT": "자료 필요",
        "NOT_RUN": "확인하지 못함",
        "NOT_APPLICABLE": "해당 없음",
        "BLOCKED": "차단",
    }.get(normalized, normalized or "확인 필요")


def _review_trace_observed_copy(label: str, observed_value: str, status: str) -> str:
    observed = str(observed_value or "").strip()
    if observed == "기간 미포함":
        return "선택한 백테스트 기간에 이 충격 구간이 포함되지 않습니다."
    if observed in {"", "-"}:
        return "아직 계산된 결과가 없습니다." if str(status or "").upper() == "NOT_RUN" else "수치로 자동 판정하지 않는 항목입니다."
    if label == "Provider snapshot freshness":
        return "최신 자료와 오래된 자료가 함께 있어 기준일 확인이 필요합니다."
    if label == "Survivorship / delisting control" and "not proven" in observed.lower():
        covered = re.search(r"covered=(\d+)", observed)
        partial = re.search(r"partial=(\d+)", observed)
        suffix = f" 확인 완료 {covered.group(1)}개, 부분 확인 {partial.group(1)}개" if covered and partial else ""
        return f"상장폐지 종목 반영이 충분히 입증되지 않았습니다.{suffix}"
    if label == "Tax / account scope" and "not modeled" in observed.lower():
        return "세금과 계좌 유형별 차이는 현재 결과에 계산되지 않았습니다."
    replacements = (
        ("windows=", "반복 검증 구간 "),
        ("negative share=", "비교 기준 하회 비율 "),
        ("profiles=", "종목 정보 "),
        ("lifecycle=", "상장 이력 "),
        ("symbols=", "대상 종목 "),
        ("generic=", "기본 민감도 결과 "),
        ("runtime follow-up=", "전략 전용 후속 검증 "),
        ("freshness=stale", "자료 최신성=오래됨"),
        ("stale_or_unknown_provider_snapshot", "오래됐거나 기준일을 확인하지 못한 ETF 자료"),
        ("coverage=", "확인 비중="),
        ("holdings ", "보유 종목 "),
        ("exposure ", "자산·섹터 노출 "),
        ("max ", "최대 "),
        ("total ", "합계 "),
        ("components ", "구성요소 "),
        ("avg ", "평균 "),
    )
    readable = observed
    for source, target in replacements:
        readable = readable.replace(source, target)
    return readable


def _review_trace_basis_copy(label: str, basis: str) -> str:
    text = str(basis or "").strip()
    if text in {"", "-"}:
        return "비교 기준이 저장된 근거에 포함되지 않아 세부 기준 확인이 필요합니다."
    if text == "return / MDD / benchmark spread":
        return "해당 충격 구간의 수익률·최대낙폭·비교 기준 대비 차이를 계산해야 합니다."
    replacements = (
        ("review line", "확인 기준"),
        ("max correlation", "최대 상관계수"),
        ("max weight", "최대 비중"),
        ("volatility contribution proxy", "변동성 기반 위험 기여 추정치"),
        ("role review line", "역할 집중 확인 기준"),
        ("holdings coverage", "보유 종목 확인 비중"),
        ("window gaps=", "전체 기간을 채우지 못한 종목="),
        ("stored_period", "저장된 백테스트 기간"),
        ("cadence 민감도", "리밸런싱 주기 변경 결과가 필요합니다."),
        ("momentum window 민감도", "모멘텀 계산 기간 변경 결과가 필요합니다."),
        ("특정 component 의존성", "특정 구성요소를 제외했을 때 결과 변화가 확인 기준입니다."),
    )
    readable = text
    for source, target in replacements:
        readable = readable.replace(source, target)
    return readable


_FINAL_REVIEW_TRACE_MEANINGS: dict[str, str] = {
    "Provider snapshot freshness": "일부 ETF 자료의 기준일이 오래되어 현재 거래 조건을 설명하는 확신이 낮아질 수 있습니다.",
    "Universe / listing evidence": "현재 종목 정보는 있으나 일부 종목의 과거 상장 이력이 완전하지 않아 기간 전체의 재현성을 주의해야 합니다.",
    "Survivorship / delisting control": "상장폐지 종목이 충분히 포함됐다는 근거가 없어 백테스트 성과가 실제보다 좋아 보일 가능성을 배제하지 못합니다.",
    "Price DB window coverage": "일부 종목의 가격 시작일이 늦으면 후보별 비교 기간과 실제 투자 가능 시점이 달라질 수 있습니다.",
    "PIT price window coverage": "재실행은 가능하지만 일부 가격 기간 gap 때문에 시점 기준 재현의 확신이 낮아질 수 있습니다.",
    "Cost / slippage sensitivity evidence": "기본 비용 민감도는 계산됐지만 전략 전용 설정 변화까지 모두 확인된 것은 아닙니다.",
    "Liquidity / operability evidence": "거래 가능성 근거가 오래됐거나 일부만 확인돼 현재 운용 현실성을 다시 확인해야 합니다.",
    "Tax / account scope": "세금과 계좌 조건을 반영하지 않은 성과이므로 사용자의 실제 계좌에서는 결과가 달라질 수 있습니다.",
    "Walk-forward temporal validation": "기간을 옮긴 반복 검증에서 비교 기준을 자주 하회하면 특정 시기 의존 가능성이 있습니다.",
    "Regime split validation": "시장 국면별 성과 차이가 있어 후보가 약해지는 환경을 최종 판단과 Monitoring 조건에 반영해야 합니다.",
    "Exclude last 12M": "최근 구간을 제외했을 때 성과가 크게 달라지면 최근 성과 의존 가능성이 있습니다.",
    "Exclude first 12M": "초기 구간을 제외했을 때 성과가 크게 달라지면 시작 시점 의존 가능성이 있습니다.",
    "Relative Strength perturbation": "모멘텀 기간 변경 결과가 없어 현재 설정값에 대한 의존도를 판단할 수 없습니다.",
    "GTAA parameter perturbation": "GTAA 설정 변경 결과가 없어 현재 리밸런싱 규칙에 대한 의존도를 판단할 수 없습니다.",
    "Component weight concentration": "한 구성요소 비중이 크면 그 구성요소의 약세가 포트폴리오 전체에 직접 영향을 줍니다.",
    "Provider look-through coverage": "ETF 내부 구성을 확인하지 못한 비중만큼 실제 자산·섹터 집중도를 과소평가할 수 있습니다.",
    "Top holding concentration": "상위 보유 종목 비중이 크면 ETF가 여러 개여도 실제 분산 효과가 제한될 수 있습니다.",
    "Holdings overlap": "ETF 간 중복 보유가 크면 서로 다른 상품을 담아도 동일 종목 위험이 반복됩니다.",
    "Pairwise correlation": "구성요소 간 상관이 높으면 시장 충격에서 함께 하락해 기대한 분산 효과가 약해질 수 있습니다.",
    "Risk contribution concentration": "표면 비중보다 실제 위험 기여가 한쪽에 집중돼 특정 구성요소가 손실을 주도할 수 있습니다.",
    "Profile-aware weight discipline": "후보의 목표보다 한 구성요소 비중이 커 의도한 운용 성격이 왜곡될 수 있습니다.",
    "Role concentration discipline": "같은 역할의 구성요소가 많으면 이름이 달라도 동일한 시장 환경에 함께 취약할 수 있습니다.",
    "ETF Operability": "ETF 거래 가능성 자료의 범위 또는 최신성이 충분하지 않아 실제 운용 조건을 보수적으로 봐야 합니다.",
    "ETF Holdings": "확인하지 못한 ETF 내부 종목 때문에 실제 집중도와 중복 보유를 완전히 계산하지 못했습니다.",
    "ETF Exposure": "확인하지 못한 ETF 자산·섹터 노출 때문에 시장 환경별 민감도를 완전히 설명하지 못했습니다.",
}


def _review_trace_guidance(label: str, status: str, observed_value: str) -> dict[str, str]:
    normalized_status = str(status or "").strip().upper()
    observed = str(observed_value or "").strip()
    display_label, _ = _review_trace_presentation(label)
    if observed == "기간 미포함":
        return {
            "meaning": "이 검증은 실패한 것이 아니라 현재 백테스트 시작일보다 과거의 충격 구간이라 계산할 수 없었습니다.",
            "action_type": "period_outside",
            "action_label": "기간 확장 또는 대체 검증",
            "improvement_action": "과거 가격 이력이 충분하면 백테스트 시작일을 확장하고, 어렵다면 최근 유사 충격 구간이나 별도 프록시 스트레스 검증을 사용합니다.",
            "action_owner": "Backtest Analysis / Practical Validation",
            "action_tone": "neutral",
        }
    normalized_label = label.lower().replace("/", " ")
    if "tax" in normalized_label and "account" in normalized_label:
        return {
            "meaning": _FINAL_REVIEW_TRACE_MEANINGS["Tax / account scope"],
            "action_type": "user_decision",
            "action_label": "판단 사유에 기록",
            "improvement_action": "현재 계좌의 세금·수수료 조건을 별도로 확인하고, 이 제한을 수용하는 이유를 선택 또는 보류 사유에 기록합니다.",
            "action_owner": "Final Review 사용자 판단",
            "action_tone": "neutral",
        }
    if normalized_status == "NOT_RUN":
        return {
            "meaning": _FINAL_REVIEW_TRACE_MEANINGS.get(label, f"{display_label} 결과가 없어 현재 설정에 대한 의존도를 판단할 수 없습니다."),
            "action_type": "implementation_gap",
            "action_label": "검증 기능 추가 필요",
            "improvement_action": "이 전략에 맞는 설정 변경 runner를 구현한 뒤 2단계 검증을 다시 실행합니다. 일반 데이터 갱신으로는 해결되지 않습니다.",
            "action_owner": "Practical Validation 검증 개발",
            "action_tone": "warning",
        }
    if label in {
        "Provider snapshot freshness",
        "Liquidity / operability evidence",
        "Provider look-through coverage",
        "ETF Operability",
        "ETF Holdings",
        "ETF Exposure",
    }:
        return {
            "meaning": _FINAL_REVIEW_TRACE_MEANINGS.get(label, "ETF 외부 데이터의 범위 또는 최신성이 충분하지 않습니다."),
            "action_type": "refreshable_data",
            "action_label": "2단계 데이터 보강 가능",
            "improvement_action": "Practical Validation의 데이터 보강에서 수집 가능한 ETF snapshot을 갱신하고, 2단계 재검증 후 새 결과를 저장합니다.",
            "action_owner": "Practical Validation 데이터 보강",
            "action_tone": "warning",
        }
    if label in {"Universe / listing evidence", "Survivorship / delisting control"}:
        return {
            "meaning": _FINAL_REVIEW_TRACE_MEANINGS[label],
            "action_type": "source_discovery",
            "action_label": "과거 종목 이력 보강 필요",
            "improvement_action": "현재 snapshot 갱신이 아니라 과거 상장·상장폐지 이력을 제공하는 source와 point-in-time universe 계약을 보강한 뒤 재검증합니다.",
            "action_owner": "데이터 파이프라인 / Practical Validation",
            "action_tone": "warning",
        }
    if label in {"Price DB window coverage", "PIT price window coverage"}:
        return {
            "meaning": _FINAL_REVIEW_TRACE_MEANINGS[label],
            "action_type": "rerun_required",
            "action_label": "가격 보강 후 재검증",
            "improvement_action": "부족한 종목의 DB 가격 기간을 보강한 뒤 같은 후보를 2단계에서 다시 검증합니다.",
            "action_owner": "가격 ingestion / Practical Validation",
            "action_tone": "warning",
        }
    if label.startswith("Drop-one: "):
        meaning = "구성요소를 제외했을 때 성과 변화가 커 해당 구성요소 의존도를 최종 판단에 반영해야 합니다."
    else:
        meaning = _FINAL_REVIEW_TRACE_MEANINGS.get(
            label,
            "저장된 검증 결과가 확인 기준을 완전히 충족하지 않아 후보의 한계로 함께 해석해야 합니다.",
        )
    return {
        "meaning": meaning,
        "action_type": "inherited_limit",
        "action_label": "현재 제한 수용 여부 판단",
        "improvement_action": "현재 결과를 후보의 약점으로 받아들일지 판단하고, 선정한다면 재검토 조건으로 Monitoring에 넘깁니다. 데이터 갱신만으로 수치가 바뀌지는 않습니다.",
        "action_owner": "Final Review / Portfolio Monitoring",
        "action_tone": "neutral",
    }


def _review_trace_row_status(row: dict[str, Any]) -> str:
    return _review_trace_value(row, "Status", "Result Status", "Diagnostic Status", "status").upper()


def _review_trace_row_observed(row: dict[str, Any]) -> str:
    observed = _review_trace_value(row, "Current", "Summary", "Judgment", "Coverage", "current_value")
    if observed != "-":
        return observed
    metric_parts = []
    for key in ("CAGR", "MDD", "CAGR Delta", "MDD Delta", "Coverage Weight"):
        value = row.get(key)
        if value is None or value == "":
            continue
        if isinstance(value, (int, float)) and key != "Coverage Weight":
            metric_parts.append(f"{key} {float(value) * 100:.2f}%")
        else:
            metric_parts.append(f"{key} {value}")
    return " / ".join(metric_parts) or "-"


def _review_trace_item(
    *,
    label: str,
    status: str,
    observed_value: str,
    judgment_basis: str,
    evidence_source: str,
    evidence_as_of: str,
) -> dict[str, str]:
    display_label, validation_description = _review_trace_presentation(label)
    guidance = _review_trace_guidance(label, status, observed_value)
    return {
        "label": label,
        "display_label": display_label,
        "validation_description": validation_description,
        "status": status,
        "status_label": _review_trace_status_label(status, observed_value),
        "observed_value": observed_value,
        "observed_label": "현재 확인된 내용",
        "display_observed_value": _review_trace_observed_copy(label, observed_value, status),
        "judgment_basis": judgment_basis,
        "judgment_basis_label": "왜 확인이 필요한가",
        "display_judgment_basis": _review_trace_basis_copy(label, judgment_basis),
        **guidance,
        "evidence_source": evidence_source,
        "evidence_as_of": evidence_as_of,
    }


def _review_trace_rows(validation: dict[str, Any], module_id: str) -> tuple[list[dict[str, str]], str]:
    """Connect a Level2 summary card to stored audit rows without inventing thresholds."""

    source_spec = _FINAL_REVIEW_TRACE_SOURCES.get(module_id)
    if not source_spec:
        return [], "-"
    source_key, source_label = source_spec
    source_payload = validation.get(source_key)
    raw_rows: list[Any] = []
    if module_id == "provider_investability":
        provider = dict(source_payload) if isinstance(source_payload, dict) else {}
        raw_rows = list(validation.get("provider_coverage_display_rows") or provider.get("display_rows") or [])
    elif module_id == "stress_robustness":
        robustness = dict(source_payload) if isinstance(source_payload, dict) else {}
        raw_rows = [
            *list(robustness.get("sensitivity_rows") or validation.get("sensitivity_rows") or []),
            *list(robustness.get("stress_summary_rows") or validation.get("stress_window_rows") or []),
        ]
    else:
        audit = dict(source_payload) if isinstance(source_payload, dict) else {}
        raw_rows = list(audit.get("rows") or [])
    non_pass_rows = [
        dict(row or {})
        for row in raw_rows
        if isinstance(row, dict)
        and _review_trace_row_status(dict(row or {})) not in {"", "PASS", "READY", "OK"}
    ]
    traces: list[dict[str, str]] = []
    for row in non_pass_rows[:3]:
        label = _review_trace_value(row, "Criteria", "Scenario", "Area", "Module", "label")
        status = _review_trace_row_status(row) or "REVIEW"
        observed_value = _review_trace_row_observed(row)
        judgment_basis = _review_trace_value(
            row,
            "Target",
            "Expected Check",
            "Evidence",
            "Meaning",
            "criterion",
        )
        row_source = _review_trace_value(
            row,
            "Source",
            "Source Strength",
            "Source Mix",
            "evidence_source",
        )
        traces.append(
            _review_trace_item(
                label=label,
                status=status,
                observed_value=observed_value,
                judgment_basis=judgment_basis,
                evidence_source=row_source if row_source != "-" else source_label,
                evidence_as_of=_review_trace_value(
                    row,
                    "As Of",
                    "As Of Range",
                    "as_of",
                    "snapshot_at",
                ),
            )
        )
    return traces, source_label


def _build_final_review_data_enrichment_action(validation: dict[str, Any]) -> dict[str, Any]:
    """Describe only provider jobs the existing Level2 Python boundary can run."""

    from app.services.backtest_practical_validation import build_provider_gap_collection_plan

    plan = build_provider_gap_collection_plan(dict(validation or {}))
    operability_symbols = sorted(
        {
            *list(plan.get("operability_official") or []),
            *list(plan.get("operability_bridge") or []),
        }
    )
    stale_symbols = sorted(set(plan.get("operability_stale") or []))
    holdings_symbols = sorted(set(plan.get("holdings_exposure") or []))
    discovery_symbols = sorted(set(plan.get("source_map_discovery") or []))
    items: list[dict[str, Any]] = []
    if operability_symbols:
        items.append(
            {
                "key": "operability",
                "label": "ETF 거래 가능성 자료",
                "symbols": operability_symbols,
                "detail": (
                    f"오래된 snapshot {len(stale_symbols)}개를 포함해 비용·거래 가능성 자료를 갱신합니다."
                    if stale_symbols
                    else "누락된 비용·거래 가능성 자료를 보강합니다."
                ),
                "tone": "warning",
            }
        )
    if holdings_symbols:
        items.append(
            {
                "key": "holdings_exposure",
                "label": "ETF 보유 종목·노출",
                "symbols": holdings_symbols,
                "detail": "검증된 공식 source가 있는 holdings·exposure를 수집합니다.",
                "tone": "warning",
            }
        )
    if discovery_symbols:
        items.append(
            {
                "key": "source_map_discovery",
                "label": "ETF 공식 source 탐색",
                "symbols": discovery_symbols,
                "detail": "holdings·exposure 수집 전 공식 원천 위치를 찾아 수집 가능 여부를 다시 확인합니다.",
                "tone": "neutral",
            }
        )
    if bool(plan.get("macro")):
        items.append(
            {
                "key": "macro",
                "label": "시장 환경 자료",
                "symbols": ["VIXCLS", "T10Y3M", "BAA10Y"],
                "detail": "부족하거나 오래된 FRED 시장 환경 series를 갱신합니다.",
                "tone": "warning",
            }
        )
    unique_symbols = sorted(
        {
            str(symbol)
            for item in items
            for symbol in list(item.get("symbols") or [])
            if str(symbol).strip()
        }
    )
    selection_source = dict(validation.get("selection_source_snapshot") or {})
    selection_source_id = _safe_text(
        selection_source.get("selection_source_id") or validation.get("selection_source_id"),
        "-",
    )
    return {
        "available": bool(items),
        "title": "2단계에서 보강 가능한 데이터",
        "detail": (
            "현재 Python 수집 경계에서 보강할 수 있는 자료만 모았습니다. "
            "기간 밖 stress, 미구현 검증, 세금·계좌 판단은 이 작업에 포함되지 않습니다."
        ),
        "item_count": len(items),
        "symbol_count": len(unique_symbols),
        "items": items,
        "selection_source_id": selection_source_id,
        "validation_id": _safe_text(validation.get("validation_id"), "-"),
        "button_label": "2단계 데이터 보강으로 이동",
        "next_step": "데이터 보강 후 Flow 2 재검증을 실행하고 새 결과를 저장한 뒤 Final Review에서 검토서를 다시 확인합니다.",
        "boundary": "이 버튼은 Final Review에서 provider를 직접 호출하지 않고, 같은 후보를 Practical Validation 데이터 보강으로 전달합니다.",
    }


def build_final_review_level2_review_disposition(*, validation: dict[str, Any]) -> dict[str, Any]:
    """Classify Practical Validation REVIEW handoff items for Final Review consumption."""

    validation = dict(validation or {})
    groups: dict[str, list[dict[str, Any]]] = {
        "blocker": [],
        "warning": [],
        "open_review": [],
        "monitoring_followup": [],
    }
    seen: set[tuple[str, str, str]] = set()
    for raw_card in _level2_review_cards(validation):
        card = dict(raw_card or {})
        status = _safe_text(card.get("status") or card.get("Status") or card.get("Current"), "")
        role = _safe_text(card.get("review_role"), "")
        if status.upper() == "PASS" or status.upper() == "READY":
            continue
        if status.upper() != "REVIEW" and role not in {"final_readiness_blocker"}:
            continue
        disposition, disposition_label, tone = _review_disposition_for_role(role, status)
        title = _safe_text(
            card.get("display_label")
            or card.get("label")
            or card.get("Criteria")
            or card.get("Module")
            or card.get("module_id"),
            "Review item",
        )
        key = (title, role, disposition)
        if key in seen:
            continue
        seen.add(key)
        normalized_role = role or "final_decision_input"
        observed_value = _review_trace_value(card, "observed_value", "current_value", "metric_value", "Value")
        threshold = _review_trace_value(card, "threshold", "pass_criteria", "criterion", "Target")
        evidence_source = _review_trace_value(
            card,
            "evidence_source",
            "source_label",
            "provider",
            "module_id",
            "Module",
        )
        evidence_as_of = _review_trace_value(card, "as_of", "snapshot_at", "collected_at", "updated_at", "generated_at")
        trace_items: list[dict[str, str]] = []
        direct_trace = observed_value != "-" or threshold != "-"
        if direct_trace:
            trace_items.append(
                _review_trace_item(
                    label=title,
                    status=status.upper() or "REVIEW",
                    observed_value=observed_value,
                    judgment_basis=threshold,
                    evidence_source=evidence_source,
                    evidence_as_of=evidence_as_of,
                )
            )
        else:
            trace_items, adapter_source = _review_trace_rows(
                validation,
                _safe_text(card.get("module_id") or card.get("Module"), ""),
            )
            if trace_items:
                first_trace = trace_items[0]
                observed_value = _safe_text(first_trace.get("observed_value"), "-")
                threshold = _safe_text(first_trace.get("judgment_basis"), "-")
                evidence_source = _safe_text(first_trace.get("evidence_source"), adapter_source)
                evidence_as_of = _safe_text(first_trace.get("evidence_as_of"), "-")
        if not trace_items and normalized_role in {"final_decision_input", "monitoring_followup"}:
            trace_items.append(
                _review_trace_item(
                    label=title,
                    status=status.upper() or "REVIEW",
                    observed_value=observed_value,
                    judgment_basis=threshold,
                    evidence_source=evidence_source,
                    evidence_as_of=evidence_as_of,
                )
            )
        if observed_value != "-" and threshold != "-" and direct_trace:
            trace_status = "measured"
            trace_label = "측정 근거 확인"
        elif normalized_role in {"final_decision_input", "monitoring_followup"}:
            trace_status = "qualitative"
            trace_label = "사용자 판단 항목"
        elif trace_items:
            trace_status = "derived"
            trace_label = f"세부 근거 {len(trace_items)}개 확인"
        else:
            trace_status = "missing_contract"
            trace_label = "세부 설명 준비 안 됨"
        ownership = {
            "pv_data_caution": "level2_inherited_limit",
            "pv_practical_caution": "level2_inherited_limit",
            "final_decision_input": "final_review_decision",
            "monitoring_followup": "monitoring_handoff",
            "final_readiness_blocker": "selection_blocker",
        }.get(normalized_role, "final_review_decision")
        user_instruction = {
            "pv_data_caution": "총평과 근거 신뢰도에 이 제한이 반영됐는지만 확인합니다. 보강 작업은 2단계 책임입니다.",
            "pv_practical_caution": "선택 판단의 확신을 낮추는 제한으로 받아들입니다. Final Review에서 검증을 다시 실행하지 않습니다.",
            "final_decision_input": "이 항목을 수용할지 판단하고 선택 또는 보류 사유에 기록합니다.",
            "monitoring_followup": "선정한다면 어떤 변화에서 재검토할지 Monitoring 조건으로 확정합니다.",
            "final_readiness_blocker": "Final Review를 중단하고 2단계로 돌아가 이 항목을 먼저 해소합니다.",
        }.get(normalized_role, "선택 또는 보류 사유에 반영합니다.")
        why_visible = {
            "level2_inherited_limit": "2단계에서 통과는 허용했지만 판단 확신과 점수 해석에 영향을 주는 제한입니다.",
            "final_review_decision": "검증으로 자동 결정할 수 없어 사용자의 최종 판단이 필요합니다.",
            "monitoring_handoff": "선정 후에도 조건 변화 여부를 지속해서 확인해야 합니다.",
            "selection_blocker": "선정 전에 반드시 해소해야 하는 차단 항목입니다.",
        }[ownership]
        raw_resolution_action = _safe_text(
            card.get("resolution_action")
            or card.get("next_action_summary")
            or card.get("action_label")
            or card.get("Next Action")
            or card.get("Required Action"),
            "-",
        )
        groups[disposition].append(
            {
                "title": title,
                "status": status.upper() or "REVIEW",
                "role": normalized_role,
                "role_label": _safe_text(card.get("review_role_label"), "최종 판단 참고"),
                "stage_surface": _safe_text(card.get("stage_decision_surface"), "Final Review"),
                "disposition": disposition,
                "disposition_label": disposition_label,
                "detail": _safe_text(
                    card.get("evidence")
                    or card.get("current_problem")
                    or card.get("missing_summary")
                    or card.get("Meaning")
                    or card.get("Current"),
                    "-",
                ),
                "action": user_instruction,
                "user_instruction": user_instruction,
                "why_visible": why_visible,
                "ownership": ownership,
                "final_review_action_required": ownership != "level2_inherited_limit",
                "level2_resolution_action": raw_resolution_action,
                "observed_value": observed_value,
                "threshold": threshold,
                "evidence_source": evidence_source,
                "evidence_as_of": evidence_as_of,
                "trace_status": trace_status,
                "trace_label": trace_label,
                "trace_items": trace_items,
                "tone": tone,
                **_level2_review_action(normalized_role),
            }
        )
    total = sum(len(items) for items in groups.values())
    all_items = [item for items in groups.values() for item in items]
    role_specs = [
        ("pv_data_caution", "데이터 주의", "warning"),
        ("pv_practical_caution", "2단계 실용성 주의", "warning"),
        ("final_decision_input", "최종 판단 참고", "warning"),
        ("monitoring_followup", "Monitoring 추적", "warning"),
        ("final_readiness_blocker", "저장 전 보강", "danger"),
    ]
    role_sections = []
    for role, label, tone in role_specs:
        action = _level2_review_action(role)
        items = [dict(item) for item in all_items if item.get("role") == role]
        role_sections.append(
            {
                "role": role,
                "label": label,
                "tone": tone,
                "count": len(items),
                "items": items,
                **action,
            }
        )
    final_review_section_specs = [
        (
            "decision",
            "최종 판단에서 결정할 것",
            "선택·보류 사유에 반영",
            "검증으로 자동 결정할 수 없는 조건을 사용자가 수용하거나 보류합니다.",
            {"final_decision_input"},
            "warning",
        ),
        (
            "inherited_limits",
            "2단계에서 인수한 제한사항",
            "이미 점수·신뢰도에 반영",
            "2단계에서 통과를 허용한 제한입니다. Final Review에서 보강 작업을 다시 수행하지 않습니다.",
            {"pv_data_caution", "pv_practical_caution"},
            "neutral",
        ),
        (
            "monitoring_handoff",
            "Monitoring으로 넘길 조건",
            "추적 조건으로 확정",
            "선정 후 어떤 변화에서 재검토할지 운영 조건으로 넘깁니다.",
            {"monitoring_followup"},
            "warning",
        ),
        (
            "selection_blockers",
            "선정 전 해소할 차단 항목",
            "2단계에서 해소 필요",
            "이 항목이 있으면 Final Review에서 선정하지 않고 2단계로 돌아갑니다.",
            {"final_readiness_blocker"},
            "danger",
        ),
    ]
    final_review_sections = []
    for key, label, action_label, detail, roles, tone in final_review_section_specs:
        items = [dict(item) for item in all_items if item.get("role") in roles]
        if not items:
            continue
        final_review_sections.append(
            {
                "key": key,
                "label": label,
                "tone": tone,
                "count": len(items),
                "action_label": action_label,
                "action_detail": detail,
                "items": items,
            }
        )
    trace_actions: list[dict[str, str]] = []
    seen_trace_actions: set[tuple[str, str, str]] = set()
    for item in all_items:
        for trace in list(item.get("trace_items") or []):
            if not isinstance(trace, dict):
                continue
            action_type = _safe_text(trace.get("action_type"), "inherited_limit")
            action_key = (
                _safe_text(trace.get("display_label") or trace.get("label"), "세부 근거"),
                action_type,
                _safe_text(trace.get("observed_value"), "-"),
            )
            if action_key in seen_trace_actions:
                continue
            seen_trace_actions.add(action_key)
            trace_actions.append(
                {
                    "label": action_key[0],
                    "action_type": action_type,
                    "action_label": _safe_text(trace.get("action_label"), "현재 제한 확인"),
                    "improvement_action": _safe_text(trace.get("improvement_action"), "최종 판단에 반영합니다."),
                    "action_owner": _safe_text(trace.get("action_owner"), "Final Review"),
                    "tone": _safe_text(trace.get("action_tone"), "neutral"),
                }
            )
    action_type_counts: dict[str, int] = {}
    for trace in trace_actions:
        action_type = trace["action_type"]
        action_type_counts[action_type] = action_type_counts.get(action_type, 0) + 1
    return {
        "schema_version": LEVEL2_REVIEW_DISPOSITION_SCHEMA_VERSION,
        "summary": {
            "total": total,
            "blocker": len(groups["blocker"]),
            "warning": len(groups["warning"]),
            "open_review": len(groups["open_review"]),
            "monitoring_followup": len(groups["monitoring_followup"]),
        },
        "groups": groups,
        "role_sections": role_sections,
        "final_review_sections": final_review_sections,
        "trace_action_summary": {
            "total": len(trace_actions),
            "refreshable_data": action_type_counts.get("refreshable_data", 0),
            "source_discovery": action_type_counts.get("source_discovery", 0),
            "rerun_required": action_type_counts.get("rerun_required", 0),
            "period_outside": action_type_counts.get("period_outside", 0),
            "implementation_gap": action_type_counts.get("implementation_gap", 0),
            "user_decision": action_type_counts.get("user_decision", 0),
            "inherited_limit": action_type_counts.get("inherited_limit", 0),
        },
        "trace_actions": trace_actions,
        "data_enrichment_action": _build_final_review_data_enrichment_action(validation),
        "boundary": {
            "validation_rerun": False,
            "provider_fetch": False,
            "storage_write": False,
            "solves_level2_review": False,
            "final_review_consumes_evidence": True,
        },
    }


def _clamped_score(value: float, *, lower: float = 0.0, upper: float = 100.0) -> int:
    return int(round(max(lower, min(upper, value))))


def build_final_review_pattern_guide_contract() -> dict[str, Any]:
    """Describe the structured evidence contract for conditional guidance."""

    return _build_pattern_guide_contract_v2(FINAL_REVIEW_PATTERN_CATALOG)


def build_final_review_pattern_guide(
    *,
    validation: dict[str, Any],
    investability_packet: dict[str, Any],
) -> dict[str, Any]:
    """Evaluate ten patterns from named evidence adapters without new I/O."""

    return _build_pattern_guide_v2(
        validation=validation,
        investability_packet=investability_packet,
        catalog=FINAL_REVIEW_PATTERN_CATALOG,
    )


def _scorecard_category(category: str, score: int, evidence: str, effect: str) -> dict[str, Any]:
    if score >= 80:
        tone = "positive"
    elif score >= 60:
        tone = "warning"
    else:
        tone = "danger"
    return {
        "category": category,
        "score": score,
        "evidence": evidence,
        "effect": effect,
        "tone": tone,
    }


def _scorecard_dimension(
    *,
    key: str,
    label: str,
    score: int,
    weight: float,
    evidence: str,
    interpretation: str,
) -> dict[str, Any]:
    if score >= 80:
        tone = "positive"
    elif score >= 60:
        tone = "warning"
    else:
        tone = "danger"
    return {
        "key": key,
        "label": label,
        "score": _clamped_score(score),
        "weight": weight,
        "evidence": evidence,
        "interpretation": interpretation,
        "tone": tone,
    }


def _weighted_dimension_score(dimensions: list[dict[str, Any]]) -> int:
    total = 0.0
    for dimension in dimensions:
        total += float(dimension.get("score") or 0.0) * float(dimension.get("weight") or 0.0)
    return _clamped_score(total)


def _score_limit(*, code: str, label: str, cap: int, detail: str, tone: str = "warning") -> dict[str, Any]:
    return {
        "code": code,
        "label": label,
        "cap": _clamped_score(cap),
        "detail": detail,
        "tone": tone,
    }


def _review_impact_for_item(item: dict[str, Any]) -> dict[str, Any]:
    role = _safe_text(item.get("role"), "final_decision_input")
    mapping = {
        "pv_data_caution": ("evidence_confidence", 6, "confidence_adjustment", "데이터 주의는 투자 매력도가 아니라 근거 신뢰도를 낮춥니다."),
        "pv_practical_caution": ("evidence_confidence", 4, "confidence_adjustment", "미측정 실용성 공백은 투자 매력도가 아니라 근거 신뢰도를 낮춥니다."),
        "final_decision_input": ("evidence_confidence", 0, "no_score_effect", "관측값과 기준이 없는 최종 판단 참고는 자동 감점하지 않습니다."),
        "monitoring_followup": ("monitoring_readiness", 4, "readiness_adjustment", "Monitoring 추적 항목은 추적 준비도에만 반영합니다."),
        "final_readiness_blocker": ("monitoring_readiness", 20, "blocker", "저장 전 보강 항목은 Monitoring 준비 blocker입니다."),
    }
    target_dimension, deduction, score_policy, rationale = mapping.get(
        role,
        ("evidence_confidence", 0, "no_score_effect", "근거가 없는 일반 REVIEW는 자동 감점하지 않습니다."),
    )
    return {
        "title": _safe_text(item.get("title"), "Review item"),
        "role": role,
        "role_label": _safe_text(item.get("role_label"), "최종 판단 참고"),
        "disposition": _safe_text(item.get("disposition"), "open_review"),
        "target_dimension": target_dimension,
        "score_effect": -deduction,
        "score_policy": score_policy,
        "detail": _safe_text(item.get("detail"), "-"),
        "action": _safe_text(item.get("action"), "-"),
        "observed_value": _safe_text(item.get("observed_value"), "-"),
        "threshold": _safe_text(item.get("threshold"), "-"),
        "evidence_source": _safe_text(item.get("evidence_source"), "-"),
        "evidence_as_of": _safe_text(item.get("evidence_as_of"), "-"),
        "trace_status": _safe_text(item.get("trace_status"), "context_only"),
        "trace_label": _safe_text(item.get("trace_label"), "근거 상태"),
        "trace_items": [dict(row or {}) for row in list(item.get("trace_items") or []) if isinstance(row, dict)],
        "rationale": rationale,
        "tone": _safe_text(item.get("tone"), "warning"),
    }


def build_final_review_scorecard(
    *,
    investability_packet: dict[str, Any],
    level2_review_disposition: dict[str, Any],
) -> dict[str, Any]:
    """Build the Final Review recommendation taxonomy from existing gate evidence."""

    packet = dict(investability_packet or {})
    gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    disposition = dict(level2_review_disposition or {})
    disposition_summary = dict(disposition.get("summary") or {})
    gate_outcome = str(gate_policy.get("outcome") or packet.get("route") or "").strip()
    packet_score = _float_or_none(packet.get("score")) or 0.0
    gate_blocker_count = len(gate_policy.get("blockers") or [])
    blocker_count = gate_blocker_count + int(disposition_summary.get("blocker", 0) or 0)
    review_required_count = len(gate_policy.get("review_required") or [])
    warning_count = int(disposition_summary.get("warning", 0) or 0)
    open_review_count = int(disposition_summary.get("open_review", 0) or 0)
    monitoring_followup_count = int(disposition_summary.get("monitoring_followup", 0) or 0)
    review_impacts: list[dict[str, Any]] = []
    for items in dict(disposition.get("groups") or {}).values():
        for item in list(items or []):
            if isinstance(item, dict):
                review_impacts.append(_review_impact_for_item(item))
    impact_deductions = {
        key: sum(
            abs(int(impact.get("score_effect") or 0))
            for impact in review_impacts
            if impact.get("target_dimension") == key
        )
        for key in ("evidence_confidence", "monitoring_readiness")
    }
    select_ready = bool(gate_policy.get("select_allowed")) or gate_outcome == "select_ready"
    gate_score = 100 if select_ready else 35 if gate_outcome == "blocked" else 65
    evidence_score = _clamped_score(packet_score * 10.0)
    weights = {
        "investment": 0.30,
        "risk": 0.20,
        "readiness": 0.20,
        "evidence_quality": 0.20,
        "monitoring_suitability": 0.10,
    }
    investment_score = evidence_score
    risk_score = evidence_score
    readiness_score = _clamped_score(
        gate_score - min(45, gate_blocker_count * 20 + review_required_count * 5 + impact_deductions["monitoring_readiness"])
    )
    evidence_quality_score = _clamped_score(
        evidence_score - min(40, impact_deductions["evidence_confidence"])
    )
    monitoring_score = _clamped_score(
        (90 if select_ready else 55) - min(40, gate_blocker_count * 20 + impact_deductions["monitoring_readiness"])
    )
    dimensions = [
        _scorecard_dimension(
            key="investment",
            label="투자 성과 매력도",
            score=investment_score,
            weight=weights["investment"],
            evidence=f"investability packet {packet_score:.1f} / 10; REVIEW 개수 자동 감점 없음",
            interpretation="성과 / benchmark / 전략 매력도 기반의 최종 선택 매력도",
        ),
        _scorecard_dimension(
            key="risk",
            label="위험 방어력",
            score=risk_score,
            weight=weights["risk"],
            evidence="저장 evidence의 risk / robustness 해석; REVIEW 개수 자동 감점 없음",
            interpretation="측정된 drawdown / robustness / construction 근거의 위험 방어력",
        ),
        _scorecard_dimension(
            key="readiness",
            label="선정 준비도",
            score=readiness_score,
            weight=weights["readiness"],
            evidence=gate_outcome or "-",
            interpretation="Final Review 판단 저장과 Monitoring handoff 준비도",
        ),
        _scorecard_dimension(
            key="evidence_quality",
            label="근거 품질",
            score=evidence_quality_score,
            weight=weights["evidence_quality"],
            evidence=f"근거 신뢰도 조정 {impact_deductions['evidence_confidence']}점",
            interpretation="데이터 / 검증 공백이 결론의 신뢰도에 미치는 영향",
        ),
        _scorecard_dimension(
            key="monitoring_suitability",
            label="Monitoring 적합성",
            score=monitoring_score,
            weight=weights["monitoring_suitability"],
            evidence=f"Monitoring 준비도 조정 {impact_deductions['monitoring_readiness']}점",
            interpretation="Monitoring에 올렸을 때 추적 조건을 관리할 수 있는지",
        ),
    ]
    attractiveness_score = _clamped_score(investment_score * 0.65 + risk_score * 0.35)
    monitoring_readiness_score = _clamped_score(readiness_score * 0.65 + monitoring_score * 0.35)
    headline_scores = [
        _scorecard_dimension(
            key="attractiveness",
            label="투자 매력도",
            score=attractiveness_score,
            weight=1.0,
            evidence="투자 성과 매력도 65% + 위험 방어력 35%",
            interpretation="측정된 성과와 위험 근거만 반영하며 REVIEW 개수로 감점하지 않습니다.",
        ),
        _scorecard_dimension(
            key="evidence_confidence",
            label="근거 신뢰도",
            score=evidence_quality_score,
            weight=1.0,
            evidence=f"근거 품질 조정 {impact_deductions['evidence_confidence']}점",
            interpretation="미측정과 데이터 주의가 결론의 신뢰도에 미치는 영향입니다.",
        ),
        _scorecard_dimension(
            key="monitoring_readiness",
            label="Monitoring 준비도",
            score=monitoring_readiness_score,
            weight=1.0,
            evidence=f"gate {gate_outcome or '-'}; 준비도 조정 {impact_deductions['monitoring_readiness']}점",
            interpretation="저장 전 blocker와 Monitoring 추적 준비 상태입니다.",
        ),
    ]
    pre_cap_score = attractiveness_score
    overall = attractiveness_score
    score_limits: list[dict[str, Any]] = []
    cap_applied = False
    route_constraints = []
    if blocker_count:
        route_constraints.append({"code": "hard_blocker", "label": "저장 전 blocker", "tone": "danger"})
    if not select_ready:
        route_constraints.append({"code": "selected_route_not_ready", "label": "선택 route 준비 필요", "tone": "warning"})
    if review_required_count:
        route_constraints.append({"code": "gate_review_required", "label": "gate 확인 필요", "tone": "warning"})
    strongest_dimension = max(dimensions, key=lambda dimension: int(dimension.get("score") or 0))
    weakest_dimension = min(dimensions, key=lambda dimension: int(dimension.get("score") or 0))
    positive_drivers = [
        {
            "label": strongest_dimension["label"],
            "detail": strongest_dimension["interpretation"],
            "score": strongest_dimension["score"],
            "tone": strongest_dimension["tone"],
        },
        {
            "label": "선정 가능 조건",
            "detail": "selected-route gate 통과 상태" if select_ready else "selected-route gate 추가 확인 필요",
            "score": gate_score,
            "tone": "positive" if select_ready else "warning",
        },
    ]
    negative_drivers = [
        {
            "label": weakest_dimension["label"],
            "detail": weakest_dimension["interpretation"],
            "score": weakest_dimension["score"],
            "tone": weakest_dimension["tone"],
        },
        {
            "label": "근거 신뢰도",
            "detail": f"데이터 / 실용성 근거 조정 {impact_deductions['evidence_confidence']}점; 최종 판단 참고는 자동 감점 없음",
            "score": evidence_quality_score,
            "tone": "warning" if impact_deductions["evidence_confidence"] else "neutral",
        },
    ]
    if blocker_count:
        classification = "REVIEW_REQUIRED"
        classification_label = "재검토 필요"
        decision_route = "RE_REVIEW_REQUIRED"
    elif select_ready and overall >= 80:
        classification = "MONITORING_CANDIDATE"
        classification_label = "추천 / 모니터링 후보"
        decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO
    elif select_ready:
        classification = "MONITORING_CANDIDATE_WITH_WATCH"
        classification_label = "모니터링 후보 / 보강 추적"
        decision_route = SELECT_FOR_PRACTICAL_PORTFOLIO
    elif overall >= 55:
        classification = "HOLD"
        classification_label = "보류 / 추가 관찰"
        decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
    elif overall >= 35:
        classification = "REVIEW_REQUIRED"
        classification_label = "재검토 필요"
        decision_route = "RE_REVIEW_REQUIRED"
    else:
        classification = "REJECT"
        classification_label = "탈락 / 실전 사용 제외"
        decision_route = "REJECT_FOR_PRACTICAL_USE"
    if overall >= 80:
        score_band = "강함"
    elif overall >= 70:
        score_band = "선정 가능 / 보강 추적"
    elif overall >= 55:
        score_band = "보류권"
    elif overall >= 35:
        score_band = "재검토권"
    else:
        score_band = "탈락권"
    return {
        "schema_version": FINAL_REVIEW_SCORECARD_SCHEMA_VERSION,
        "overall_score": overall,
        "pre_cap_score": pre_cap_score,
        "score_band": score_band,
        "classification": classification,
        "classification_label": classification_label,
        "decision_route": decision_route,
        "decision_label": _decision_route_label(decision_route),
        "monitoring_candidate": decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO and select_ready and blocker_count == 0,
        "basis": "투자 매력도와 근거 신뢰도, Monitoring 준비도를 분리한 evidence-only scorecard",
        "weights": weights,
        "dimensions": dimensions,
        "headline_scores": headline_scores,
        "review_impacts": review_impacts,
        "score_drivers": {
            "positive": positive_drivers,
            "negative": negative_drivers,
        },
        "score_limits": score_limits,
        "route_constraints": route_constraints,
        "cap_applied": cap_applied,
        "inputs": {
            "gate_outcome": gate_outcome,
            "packet_score_0_10": packet_score,
            "blocker_count": blocker_count,
            "review_required_count": review_required_count,
            "warning_count": warning_count,
            "open_review_count": open_review_count,
            "monitoring_followup_count": monitoring_followup_count,
            "review_impact_count": len(review_impacts),
        },
        "categories": [
            _scorecard_category(
                "Selection Gate",
                gate_score,
                gate_outcome or "-",
                "Monitoring 후보 handoff 가능 여부",
            ),
            _scorecard_category(
                "Evidence Packet",
                evidence_score,
                f"{packet_score:.1f} / 10",
                "기존 investability evidence ready-check",
            ),
            _scorecard_category(
                "투자 매력도",
                attractiveness_score,
                "측정된 성과 / 위험 evidence",
                "REVIEW 개수 자동 감점 없음",
            ),
            _scorecard_category(
                "근거 신뢰도",
                evidence_quality_score,
                f"근거 품질 조정 {impact_deductions['evidence_confidence']}점",
                "미측정 / 데이터 주의 분리",
            ),
            _scorecard_category(
                "Monitoring 준비도",
                monitoring_readiness_score,
                f"준비도 조정 {impact_deductions['monitoring_readiness']}점",
                "blocker / 추적 조건 분리",
            ),
        ],
        "boundaries": {
            "validation_rerun": False,
            "provider_fetch": False,
            "storage_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


def build_final_review_weakness_improvement_plan(
    *,
    weaknesses: list[dict[str, Any]],
    scorecard: dict[str, Any],
) -> dict[str, Any]:
    """Suggest verifiable weakness mitigations without generating a new strategy."""

    weakness_rows = [dict(row or {}) for row in list(weaknesses or []) if isinstance(row, dict)]
    current_score = int(dict(scorecard or {}).get("overall_score") or 0)
    proposals: list[dict[str, Any]] = []
    for row in weakness_rows[:5]:
        title = _safe_text(row.get("title"), "약점")
        action = _safe_text(row.get("action"), "근거를 보강하고 Final Review scorecard를 다시 확인합니다.")
        proposals.append(
            {
                "weakness": title,
                "current_gap": _safe_text(row.get("detail"), "-"),
                "proposed_change": action,
                "expected_effect": "이 변경의 효과는 별도 재검증 전에는 점수 개선으로 추정하지 않습니다.",
                "verification_step": f"{action} 이후 Practical Validation 검증 결과와 Final Review scorecard를 다시 비교합니다.",
                "scope": "evidence_and_validation",
                "auto_generate_strategy": False,
            }
        )
    if not proposals:
        proposals.append(
            {
                "weakness": "선택 차단 약점 없음",
                "current_gap": "현재 selected-route blocker는 없습니다.",
                "proposed_change": "새 비중이나 전략을 자동 생성하지 않고, Monitoring trigger와 open review를 추적합니다.",
                "expected_effect": "현재 후보 상태를 유지하면서 사후 recheck에서 성과 악화나 근거 stale을 확인합니다.",
                "verification_step": "Portfolio Monitoring에서 정해진 review trigger와 scorecard 변화를 검증합니다.",
                "scope": "monitoring_followup",
                "auto_generate_strategy": False,
            }
        )
    return {
        "schema_version": WEAKNESS_IMPROVEMENT_SCHEMA_VERSION,
        "proposals": proposals,
        "comparison": {
            "current_score": current_score,
            "weakness_count": len(weakness_rows),
            "score_projection_available": False,
            "verification_status": "counterfactual_required" if weakness_rows else "monitoring_required",
            "projection_note": "대안 적용 후 Practical Validation과 counterfactual backtest 전에는 예상 점수 범위를 제공하지 않습니다.",
        },
        "boundary": {
            "auto_generate_strategy": False,
            "auto_backtest": False,
            "auto_save_portfolio": False,
            "verification_required": bool(weakness_rows),
            "provider_fetch": False,
            "storage_write": False,
        },
    }


def build_final_review_selection_rationale(*, scorecard: dict[str, Any]) -> dict[str, Any]:
    """Summarize why the final route is selectable, held, rejected, or needs review."""

    scorecard = dict(scorecard or {})
    dimensions = [dict(row or {}) for row in list(scorecard.get("dimensions") or []) if isinstance(row, dict)]
    headline_scores = {
        str(row.get("key") or ""): dict(row or {})
        for row in list(scorecard.get("headline_scores") or [])
        if isinstance(row, dict)
    }
    strongest = max(dimensions, key=lambda row: int(row.get("score") or 0)) if dimensions else {}
    weakest = min(dimensions, key=lambda row: int(row.get("score") or 0)) if dimensions else {}
    inputs = dict(scorecard.get("inputs") or {})
    score_limits = [dict(row or {}) for row in list(scorecard.get("score_limits") or []) if isinstance(row, dict)]
    decision_route = _safe_text(scorecard.get("decision_route"), "HOLD_FOR_MORE_PAPER_TRACKING")
    overall_score = int(scorecard.get("overall_score") or 0)
    pre_cap_score = int(scorecard.get("pre_cap_score") or overall_score)
    classification_label = _safe_text(scorecard.get("classification_label"), _decision_route_label(decision_route))
    attractiveness = int(dict(headline_scores.get("attractiveness") or {}).get("score") or overall_score)
    evidence_confidence = int(dict(headline_scores.get("evidence_confidence") or {}).get("score") or 0)
    monitoring_readiness = int(dict(headline_scores.get("monitoring_readiness") or {}).get("score") or 0)
    route_constraints = [
        dict(row or {})
        for row in list(scorecard.get("route_constraints") or [])
        if isinstance(row, dict)
    ]
    if decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO:
        headline = "Monitoring 후보로 올릴 수 있는 최종 선택 근거입니다."
    elif decision_route == "HOLD_FOR_MORE_PAPER_TRACKING":
        headline = "선정 전 추가 관찰로 보류해야 하는 근거입니다."
    elif decision_route == "RE_REVIEW_REQUIRED":
        headline = "실전 후보 판단 전에 재검토해야 하는 근거입니다."
    else:
        headline = "실전 사용 후보에서 제외해야 하는 근거입니다."
    limit_summary = "투자 매력도 자동 cap 없음"
    route_summary = (
        ", ".join(_safe_text(item.get("label"), "route 확인") for item in route_constraints)
        if route_constraints
        else "선택 route 제약 없음"
    )
    review_summary = (
        f"Level2 REVIEW warning {int(inputs.get('warning_count') or 0)}, "
        f"open {int(inputs.get('open_review_count') or 0)}, "
        f"monitoring follow-up {int(inputs.get('monitoring_followup_count') or 0)}"
    )
    decision_reason = (
        f"{classification_label}. 투자 매력도 {attractiveness}/100, 근거 신뢰도 {evidence_confidence}/100, "
        f"Monitoring 준비도 {monitoring_readiness}/100입니다. {route_summary}."
    )
    key_points = [
        {
            "label": "투자 매력도",
            "detail": f"{attractiveness}/100 ({_safe_text(scorecard.get('score_band'), '-')})",
            "tone": "positive" if overall_score >= 80 else "warning" if overall_score >= 55 else "danger",
        },
        {
            "label": "가장 강한 근거",
            "detail": f"{_safe_text(strongest.get('label'), '-')} {int(strongest.get('score') or 0)}/100 - {_safe_text(strongest.get('interpretation'), '-')}",
            "tone": _safe_text(strongest.get("tone"), "neutral"),
        },
        {
            "label": "가장 큰 확인 지점",
            "detail": f"{_safe_text(weakest.get('label'), '-')} {int(weakest.get('score') or 0)}/100 - {_safe_text(weakest.get('interpretation'), '-')}",
            "tone": _safe_text(weakest.get("tone"), "neutral"),
        },
        {
            "label": "Level2 REVIEW 반영",
            "detail": review_summary,
            "tone": "warning" if int(inputs.get("open_review_count") or 0) else "neutral",
        },
    ]
    if score_limits:
        key_points.append(
            {
                "label": "점수 제한",
                "detail": "; ".join(_safe_text(limit.get("detail"), _safe_text(limit.get("label"), "-")) for limit in score_limits),
                "tone": "warning",
            }
        )
    return {
        "schema_version": SELECTION_RATIONALE_SCHEMA_VERSION,
        "headline": headline,
        "decision_route": decision_route,
        "decision_label": _decision_route_label(decision_route),
        "classification": scorecard.get("classification"),
        "classification_label": classification_label,
        "score_summary": (
            f"투자 매력도 {attractiveness}/100, 근거 신뢰도 {evidence_confidence}/100, "
            f"Monitoring 준비도 {monitoring_readiness}/100, {limit_summary}, {route_summary}"
        ),
        "decision_reason": decision_reason,
        "key_points": key_points,
        "monitoring_handoff_reason": (
            "Monitoring 후보로 올리고 review trigger를 추적합니다."
            if bool(scorecard.get("monitoring_candidate"))
            else "Monitoring handoff 전에 보강 또는 추가 관찰이 필요합니다."
        ),
        "boundary": {
            "provider_fetch": False,
            "storage_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


def build_final_review_required_decision_notes(*, scorecard: dict[str, Any], selection_rationale: dict[str, Any]) -> list[dict[str, Any]]:
    """Describe the user-authored notes needed before saving a Final Review judgment."""

    scorecard = dict(scorecard or {})
    inputs = dict(scorecard.get("inputs") or {})
    score_limits = [dict(row or {}) for row in list(scorecard.get("score_limits") or []) if isinstance(row, dict)]
    review_count = int(inputs.get("review_impact_count") or 0)
    notes = [
        {
            "kind": "decision_reason",
            "label": "선택 / 보류 / 탈락 사유",
            "prompt": _safe_text(selection_rationale.get("decision_reason"), "최종 판단 사유를 기록합니다."),
            "required": True,
            "source": "selection_rationale",
            "boundary": {"storage_write": False, "provider_fetch": False},
        },
        {
            "kind": "score",
            "label": "점수 해석과 route 조건",
            "prompt": _safe_text(selection_rationale.get("score_summary"), "세 점수와 route 조건을 구분해 기록합니다."),
            "required": True,
            "source": "scorecard",
            "boundary": {"storage_write": False, "provider_fetch": False},
        },
        {
            "kind": "level2_review",
            "label": "Level2 REVIEW 처리 메모",
            "prompt": f"Final Review에서 해결하지 않는 REVIEW {review_count}개를 최종 판단 근거 또는 Monitoring 추적 조건으로 기록합니다.",
            "required": bool(review_count or score_limits),
            "source": "level2_review_disposition",
            "boundary": {"storage_write": False, "provider_fetch": False},
        },
        {
            "kind": "monitoring_handoff",
            "label": "Monitoring 추적 조건",
            "prompt": _safe_text(selection_rationale.get("monitoring_handoff_reason"), "Monitoring handoff 조건을 기록합니다."),
            "required": bool(scorecard.get("monitoring_candidate")),
            "source": "monitoring_conditions",
            "boundary": {"storage_write": False, "provider_fetch": False},
        },
    ]
    return notes


def build_final_review_investment_report(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    investability_packet: dict[str, Any],
) -> dict[str, Any]:
    """Build a human-readable Final Review report from existing evidence only."""

    source = dict(source or {})
    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    packet = dict(investability_packet or {})
    cockpit = build_final_review_decision_cockpit(
        source=source,
        validation=validation,
        paper_observation=paper_observation,
        decision_evidence=decision_evidence,
        investability_packet=packet,
    )
    state = str(cockpit.get("state") or "")
    suggested_route = str(cockpit.get("suggested_decision_route") or SELECT_FOR_PRACTICAL_PORTFOLIO)
    score_value = _float_or_none(packet.get("score") if packet.get("score") is not None else decision_evidence.get("score"))
    score_value = round(score_value, 1) if score_value is not None else 0.0
    tone = _report_tone_from_state(state)
    monitoring = dict(cockpit.get("monitoring_handoff") or {})
    weaknesses = _report_weaknesses(cockpit)
    level2_review_disposition = build_final_review_level2_review_disposition(validation=validation)
    scorecard = build_final_review_scorecard(
        investability_packet=packet,
        level2_review_disposition=level2_review_disposition,
    )
    strengths = _report_strengths(cockpit, packet, scorecard)
    suggested_route = str(scorecard.get("decision_route") or suggested_route)
    decision_record_guide = build_final_review_decision_record_guide(
        decision_route=suggested_route,
        decision_evidence=decision_evidence,
        investability_packet=packet,
    )
    save_handoff_summary = build_final_review_save_handoff_summary(
        decision_record_guide=decision_record_guide,
    )
    weakness_improvement = build_final_review_weakness_improvement_plan(
        weaknesses=weaknesses,
        scorecard=scorecard,
    )
    selection_rationale = build_final_review_selection_rationale(scorecard=scorecard)
    required_final_decision_notes = build_final_review_required_decision_notes(
        scorecard=scorecard,
        selection_rationale=selection_rationale,
    )
    decision_summary = _build_decision_summary(
        scorecard=scorecard,
        selection_rationale=selection_rationale,
    )
    interpretation_cards = _build_interpretation_cards(
        scorecard=scorecard,
        cockpit=cockpit,
        packet=packet,
        monitoring=monitoring,
    )
    watch_items = _build_watch_items(
        weaknesses=weaknesses,
        scorecard=scorecard,
    )
    decision_questions = []
    question_effects = {
        "decision_reason": "최종 판단 기록",
        "score": "점수 해석",
        "level2_review": "저장 전 확인",
        "monitoring_handoff": "Monitoring 조건",
    }
    for note in required_final_decision_notes:
        decision_questions.append(
            {
                "kind": note.get("kind"),
                "label": note.get("label"),
                "question": note.get("prompt"),
                "required": bool(note.get("required")),
                "effect": question_effects.get(str(note.get("kind") or ""), "판단 참고"),
                "source": note.get("source"),
            }
        )
    pattern_guide = build_final_review_pattern_guide(
        validation=validation,
        investability_packet=packet,
    )
    score_value = round(float(scorecard.get("overall_score") or 0.0) / 10.0, 1)
    if state == "SELECT_READY":
        headline = "모니터링 후보로 올릴 수 있는 Final Review 근거입니다."
    elif state == "SELECT_BLOCKED":
        headline = "Monitoring handoff 전에 반드시 해소해야 할 차단 항목이 있습니다."
    else:
        headline = "선정 전 추가 관찰 또는 재검토가 필요한 후보입니다."
    return {
        "schema_version": INVESTMENT_REPORT_SCHEMA_VERSION,
        "source": {
            "title": source.get("source_title") or cockpit.get("source_title") or "-",
            "type": source.get("source_type") or cockpit.get("source_type") or "-",
            "source_id": source.get("source_id") or dict(packet.get("source_chain") or {}).get("source_id") or "-",
            "validation_id": validation.get("validation_id") or dict(packet.get("source_chain") or {}).get("validation_id") or "-",
        },
        "recommendation": {
            "route": suggested_route,
            "label": _decision_route_label(suggested_route),
            "classification": scorecard.get("classification"),
            "classification_label": scorecard.get("classification_label"),
            "state": state,
            "state_label": cockpit.get("state_label") or "-",
            "tone": tone,
            "monitoring_candidate": bool(scorecard.get("monitoring_candidate")),
            "monitoring_handoff_state": "ready" if cockpit.get("select_allowed") else "blocked",
        },
        "score": {
            "value": score_value,
            "label": scorecard.get("score_band") or _score_band(score_value, state),
            "scale": "0-10",
            "basis": scorecard.get("basis") or "Investability packet ready-check ratio",
        },
        "scorecard": scorecard,
        "decision_summary": decision_summary,
        "report_narrative": {
            "total_assessment": {
                "label": "총평",
                "headline": selection_rationale.get("classification_label"),
                "detail": selection_rationale.get("decision_reason"),
                "tone": "positive" if scorecard.get("monitoring_candidate") else "warning",
            },
            "decision_questions": decision_questions,
            "boundary_note": "저장된 Practical Validation evidence를 해석한 결과이며 새 검증이나 투자 주문을 실행하지 않습니다.",
        },
        "pattern_guide_contract": build_final_review_pattern_guide_contract(),
        "pattern_guide": pattern_guide,
        "selection_rationale": selection_rationale,
        "required_final_decision_notes": required_final_decision_notes,
        "save_handoff_summary": save_handoff_summary,
        "weakness_improvement": weakness_improvement,
        "summary": {
            "headline": headline,
            "verdict": cockpit.get("verdict") or packet.get("verdict") or "-",
            "next_action": cockpit.get("next_action") or packet.get("next_action") or "-",
            "strongest_evidence": strengths[0]["title"] if strengths else "근거 확인 필요",
            "weakest_constraint": weaknesses[0]["title"] if weaknesses else "현재 선택 차단 약점 없음",
        },
        "strengths": strengths,
        "weaknesses": weaknesses,
        "watch_items": watch_items,
        "interpretation_cards": interpretation_cards,
        "performance_interpretation": {
            "title": "성과 해석",
            "detail": _safe_text(
                next((card.get("detail") for card in interpretation_cards if card.get("kind") == "performance_interpretation"), ""),
                cockpit.get("verdict") or "-",
            ),
            "score": score_value,
        },
        "scenario_fit": {
            "title": "환경 적합성",
            "detail": _safe_text(
                next((card.get("detail") for card in interpretation_cards if card.get("kind") == "monitoring_fit"), ""),
                monitoring.get("tracking_benchmark"),
            ),
            "review_cadence": monitoring.get("review_cadence") or "-",
        },
        "expected_range_and_risk": {
            "title": "위험 해석",
            "detail": _safe_text(
                next((card.get("detail") for card in interpretation_cards if card.get("kind") == "risk_interpretation"), ""),
                "open review와 blocker를 기준으로 추적합니다.",
            ),
            "open_review_items": int(dict(cockpit.get("metrics") or {}).get("open_review_items", 0) or 0),
            "policy_blockers": int(dict(cockpit.get("metrics") or {}).get("policy_blockers", 0) or 0),
        },
        "benchmark_rationale": {
            "title": "Benchmark / 대체 전략 대비 선택 이유",
            "detail": _safe_text(
                next((card.get("detail") for card in interpretation_cards if card.get("kind") == "benchmark_rationale"), ""),
                next(
                    (
                        dict(row or {}).get("Evidence") or dict(row or {}).get("Current")
                        for row in list(dict(packet.get("selection_gate_policy_snapshot") or {}).get("policy_rows") or [])
                        if str(dict(row or {}).get("Group") or "") == "benchmark"
                    ),
                    "",
                ),
            ),
        },
        "level2_review_disposition": level2_review_disposition,
        "monitoring_conditions": {
            "handoff_ready": bool(cockpit.get("select_allowed")),
            "tracking_benchmark": monitoring.get("tracking_benchmark") or "-",
            "review_cadence": monitoring.get("review_cadence") or "-",
            "review_triggers": list(monitoring.get("review_triggers") or []),
            "active_components": int(monitoring.get("active_components") or 0),
            "target_weight_total": monitoring.get("target_weight_total"),
        },
        "boundaries": {
            "validation_rerun": False,
            "provider_fetch": False,
            "registry_write": False,
            "storage_append": False,
            "live_approval": False,
            "order_instruction": False,
            "account_sync": False,
            "auto_rebalance": False,
        },
    }


def build_final_review_candidate_board_rows(candidates: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten Final Review eligible candidates into a comparison board."""

    rows: list[dict[str, Any]] = []
    for index, candidate in enumerate(list(candidates or []), start=1):
        source = dict(candidate.get("source") or {})
        validation = dict(candidate.get("validation") or {})
        paper_observation = dict(candidate.get("paper_observation") or {})
        decision_evidence = dict(candidate.get("decision_evidence") or {})
        packet = dict(candidate.get("investability_packet") or {})
        if not packet:
            packet = build_investability_evidence_packet(
                source=source,
                validation=validation,
                paper_observation=paper_observation,
                decision_evidence=decision_evidence,
            )
        cockpit = build_final_review_decision_cockpit(
            source=source,
            validation=validation,
            paper_observation=paper_observation,
            decision_evidence=decision_evidence,
            investability_packet=packet,
        )
        source_chain = dict(packet.get("source_chain") or {})
        summary = dict(packet.get("summary") or {})
        action_label, primary_reason, priority_label = _candidate_board_action(cockpit)
        metrics = dict(cockpit.get("metrics") or {})
        packet_score = packet.get("score")
        try:
            sortable_score = float(packet_score or 0.0)
        except (TypeError, ValueError):
            sortable_score = 0.0
        state_priority = _candidate_board_state_priority(cockpit.get("state"))
        rows.append(
            {
                "Rank": index,
                "Review Priority": f"P{index}",
                "Priority Label": priority_label,
                "Candidate": cockpit.get("source_title") or candidate.get("label") or "-",
                "Decision State": cockpit.get("state_label"),
                "Suggested Decision": cockpit.get("suggested_decision_label"),
                "Board Action": action_label,
                "Primary Reason": primary_reason,
                "Next Review Focus": cockpit.get("next_action") or "-",
                "Gate Outcome": cockpit.get("gate_outcome") or "-",
                "Select Allowed": "Yes" if cockpit.get("select_allowed") else "No",
                "Blockers": metrics.get("policy_blockers", 0),
                "Review Required": metrics.get("policy_review_required", 0),
                "Open Review": metrics.get("open_review_items", 0),
                "Critical Gaps": metrics.get("critical_gaps", 0),
                "NOT_RUN": summary.get("not_run", 0),
                "Provider": summary.get("provider_status") or "-",
                "Validation Method Strength": summary.get("validation_efficacy_route") or "-",
                "Data Coverage": summary.get("data_coverage_route") or "-",
                "Backtest Realism": summary.get("backtest_realism_route") or "-",
                "Packet Score": packet.get("score"),
                "Validation ID": source_chain.get("validation_id") or validation.get("validation_id") or "-",
                "Source ID": source_chain.get("selection_source_id")
                or source_chain.get("source_id")
                or source.get("source_id")
                or "-",
                "_sort_key": (
                    state_priority,
                    int(metrics.get("policy_blockers", 0) or 0),
                    int(metrics.get("policy_review_required", 0) or 0),
                    int(metrics.get("open_review_items", 0) or 0),
                    int(metrics.get("critical_gaps", 0) or 0),
                    int(summary.get("not_run", 0) or 0),
                    -sortable_score,
                    index,
                ),
            }
        )
    rows.sort(key=lambda row: tuple(row.get("_sort_key") or (99, 99, 99, 99, 99, 99, 0, 9999)))
    for rank, row in enumerate(rows, start=1):
        row["Rank"] = rank
        row["Review Priority"] = f"P{rank}"
        row.pop("_sort_key", None)
    return rows


def build_final_review_candidate_board(candidates: list[dict[str, Any]]) -> dict[str, Any]:
    """Build the Final Review candidate comparison board and review queue."""

    rows = build_final_review_candidate_board_rows(candidates)
    total = len(rows)
    select_ready = sum(1 for row in rows if row.get("Decision State") == "모니터링 후보 가능")
    blocked = sum(1 for row in rows if row.get("Decision State") == "선정 차단")
    hold_or_re_review = max(0, total - select_ready - blocked)
    first_row = dict(rows[0] or {}) if rows else {}
    queue_rows = [
        {
            "Priority": row.get("Review Priority"),
            "Candidate": row.get("Candidate"),
            "Action": row.get("Board Action"),
            "Reason": row.get("Primary Reason"),
            "Suggested Decision": row.get("Suggested Decision"),
            "Packet Score": row.get("Packet Score"),
        }
        for row in rows[:5]
    ]
    return {
        "schema_version": CANDIDATE_BOARD_SCHEMA_VERSION,
        "summary": {
            "total_candidates": total,
            "select_ready": select_ready,
            "hold_or_re_review": hold_or_re_review,
            "blocked": blocked,
            "first_review_candidate": first_row.get("Candidate") or "-",
            "first_review_action": first_row.get("Board Action") or "-",
            "first_review_reason": first_row.get("Primary Reason") or "-",
        },
        "review_queue_rows": queue_rows,
        "rows": rows,
    }


def build_final_review_status_display(row: dict[str, Any]) -> dict[str, str]:
    """Translate a saved final decision row into the current Final Review status copy."""

    decision_route = str(row.get("decision_route") or "").strip()
    status = dict(FINAL_REVIEW_STATUS_DISPLAY.get(decision_route) or {})
    if status:
        return status
    legacy_handoff = dict(row.get("phase35_handoff") or {})
    return {
        "route": str(legacy_handoff.get("handoff_route") or "FINAL_REVIEW_STATUS_UNKNOWN"),
        "verdict": "최종 판단 상태 확인 필요",
        "next_action": "decision route와 evidence를 확인한 뒤 Final Review에서 다시 판단합니다.",
    }


def build_final_review_decision_display_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten saved final decision records for a UI table without depending on Streamlit."""

    display_rows: list[dict[str, Any]] = []
    for row in rows:
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        gate_policy = dict(row.get("selection_gate_policy_snapshot") or row.get("gate_policy_snapshot") or {})
        if not gate_policy:
            packet = dict(row.get("investability_evidence_packet") or {})
            gate_policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
        status_display = build_final_review_status_display(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "판단 라벨": FINAL_REVIEW_DECISION_LABELS.get(str(row.get("decision_route") or ""), "재검토 필요"),
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Observation": row.get("source_observation_id") or row.get("source_paper_ledger_id") or "-",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route"),
                "Evidence Score": evidence.get("score"),
                "Gate Outcome": gate_policy.get("outcome") or "-",
                "Final Status": status_display.get("route"),
                "Live Approval": "Disabled",
            }
        )
    return display_rows


def _saved_decision_route_family(route: Any) -> str:
    route_text = str(route or "").strip()
    if route_text == SELECT_FOR_PRACTICAL_PORTFOLIO:
        return "Selected"
    if route_text == "HOLD_FOR_MORE_PAPER_TRACKING":
        return "Hold"
    if route_text == "REJECT_FOR_PRACTICAL_USE":
        return "Reject"
    if route_text == "RE_REVIEW_REQUIRED":
        return "Re-review"
    return "Unknown"


def _decision_gate_policy(row: dict[str, Any]) -> dict[str, Any]:
    gate_policy = dict(row.get("selection_gate_policy_snapshot") or row.get("gate_policy_snapshot") or {})
    if gate_policy:
        return gate_policy
    packet = dict(row.get("investability_evidence_packet") or {})
    return dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})


def build_saved_final_review_decision_review(rows: list[dict[str, Any]]) -> dict[str, Any]:
    """Summarize saved Final Review decisions for review without adding persistence."""

    indexed_rows = [
        (index, dict(row or {}))
        for index, row in enumerate(list(rows or []))
    ]
    indexed_rows.sort(
        key=lambda item: _safe_text(item[1].get("updated_at") or item[1].get("created_at"), ""),
        reverse=True,
    )
    review_rows: list[dict[str, Any]] = []
    family_counts = {key: 0 for key in FINAL_REVIEW_SAVED_DECISION_FILTER_OPTIONS if key != "All"}
    dashboard_eligible = 0
    for display_index, (raw_index, row) in enumerate(indexed_rows, start=1):
        route = str(row.get("decision_route") or "").strip()
        family = _saved_decision_route_family(route)
        family_counts[family] = int(family_counts.get(family, 0) or 0) + 1
        if route == SELECT_FOR_PRACTICAL_PORTFOLIO:
            dashboard_eligible += 1
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        packet = dict(row.get("investability_evidence_packet") or {})
        gate_policy = _decision_gate_policy(row)
        operator = dict(row.get("operator_decision") or {})
        status_display = build_final_review_status_display(row)
        issue_count = (
            len(evidence.get("blockers") or [])
            + len(packet.get("critical_gaps") or [])
            + len(gate_policy.get("blockers") or [])
            + len(gate_policy.get("review_required") or [])
        )
        review_rows.append(
            {
                "Rank": display_index,
                "Updated At": row.get("updated_at") or row.get("created_at") or "-",
                "Decision ID": row.get("decision_id") or "-",
                "Decision": FINAL_REVIEW_DECISION_LABELS.get(route, "재검토 필요"),
                "Route Family": family,
                "Decision Route": route or "-",
                "Final Status": status_display.get("route") or "-",
                "Source": f"{row.get('source_type') or '-'} / {row.get('source_id') or '-'}",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route") or "-",
                "Evidence Score": evidence.get("score") if evidence.get("score") is not None else "-",
                "Packet Route": packet.get("route") or "-",
                "Gate Outcome": gate_policy.get("outcome") or "-",
                "Select Allowed": "Yes" if bool(gate_policy.get("select_allowed")) else "No",
                "Evidence Issues": issue_count,
                "Dashboard Eligible": "Yes" if _is_monitoring_handoff_candidate(row) else "No",
                "Operator Reason": _safe_text(operator.get("reason"), "-"),
                "Next Action": _safe_text(operator.get("next_action") or status_display.get("next_action"), "-"),
                "Live Approval": "Disabled",
                "_row_index": raw_index,
            }
        )
    latest = dict(review_rows[0]) if review_rows else {}
    return {
        "schema_version": SAVED_DECISION_REVIEW_SCHEMA_VERSION,
        "summary": {
            "total_records": len(review_rows),
            "selected": int(family_counts.get("Selected", 0) or 0),
            "hold": int(family_counts.get("Hold", 0) or 0),
            "reject": int(family_counts.get("Reject", 0) or 0),
            "re_review": int(family_counts.get("Re-review", 0) or 0),
            "unknown": int(family_counts.get("Unknown", 0) or 0),
            "dashboard_eligible": dashboard_eligible,
            "latest_decision_id": latest.get("Decision ID") or "-",
            "latest_decision": latest.get("Decision") or "-",
            "latest_updated_at": latest.get("Updated At") or "-",
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
        "filter_options": list(FINAL_REVIEW_SAVED_DECISION_FILTER_OPTIONS),
        "rows": review_rows,
    }


def _append_check_rows(
    display_rows: list[dict[str, Any]],
    *,
    area: str,
    checks: list[dict[str, Any]],
) -> None:
    for check in checks:
        check_row = dict(check or {})
        display_rows.append(
            {
                "Area": area,
                "Criteria": check_row.get("Criteria")
                or check_row.get("criteria")
                or check_row.get("Section")
                or check_row.get("Group")
                or check_row.get("Check")
                or "-",
                "Ready": check_row.get("Ready")
                if "Ready" in check_row
                else check_row.get("ready")
                if "ready" in check_row
                else str(check_row.get("Status") or "").upper() == "PASS",
                "Current": check_row.get("Current")
                or check_row.get("current")
                or check_row.get("current_value")
                or check_row.get("Status")
                or "-",
                "Meaning": check_row.get("Meaning")
                or check_row.get("meaning")
                or check_row.get("Required Action")
                or check_row.get("Evidence")
                or "-",
                "Score": check_row.get("Score") or check_row.get("score") or "-",
            }
        )


def build_final_decision_evidence_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand a final decision row into evidence check rows shared by review and dashboard views."""

    raw_decision = dict(row.get("raw_decision") or row)
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    display_rows: list[dict[str, Any]] = []
    packet = dict(raw_decision.get("investability_evidence_packet") or {})
    gate_policy = dict(
        raw_decision.get("selection_gate_policy_snapshot")
        or raw_decision.get("gate_policy_snapshot")
        or packet.get("selection_gate_policy_snapshot")
        or packet.get("gate_policy_snapshot")
        or {}
    )
    look_through = dict(risk_snapshot.get("provider_look_through_board") or {})
    if not look_through:
        provider_context = dict(risk_snapshot.get("provider_coverage") or {})
        look_through = dict(provider_context.get("look_through_board") or {})
    robustness_lab = dict(robustness.get("robustness_lab_board") or risk_snapshot.get("robustness_lab_board") or {})
    validation_efficacy = dict(
        risk_snapshot.get("validation_efficacy_audit") or packet.get("validation_efficacy_audit") or {}
    )
    data_coverage = dict(risk_snapshot.get("data_coverage_audit") or packet.get("data_coverage_audit") or {})
    construction_risk = dict(
        risk_snapshot.get("construction_risk_audit") or packet.get("construction_risk_audit") or {}
    )
    risk_contribution = dict(
        risk_snapshot.get("risk_contribution_audit") or packet.get("risk_contribution_audit") or {}
    )
    component_role_weight = dict(
        risk_snapshot.get("component_role_weight_audit") or packet.get("component_role_weight_audit") or {}
    )
    backtest_realism = dict(risk_snapshot.get("backtest_realism_audit") or packet.get("backtest_realism_audit") or {})
    _append_check_rows(display_rows, area="Final Review Evidence", checks=list(evidence.get("checks") or []))
    _append_check_rows(display_rows, area="Investability Packet", checks=list(packet.get("checks") or []))
    _append_check_rows(display_rows, area="Gate Policy", checks=list(gate_policy.get("policy_rows") or []))
    _append_check_rows(display_rows, area="Validation", checks=list(risk_snapshot.get("validation_checks") or []))
    _append_check_rows(display_rows, area="Validation Method Strength", checks=list(validation_efficacy.get("rows") or []))
    _append_check_rows(display_rows, area="Data Coverage", checks=list(data_coverage.get("rows") or []))
    _append_check_rows(display_rows, area="Construction Risk", checks=list(construction_risk.get("rows") or []))
    _append_check_rows(display_rows, area="Risk Contribution", checks=list(risk_contribution.get("rows") or []))
    _append_check_rows(display_rows, area="Component Role / Weight", checks=list(component_role_weight.get("rows") or []))
    _append_check_rows(display_rows, area="Backtest Realism", checks=list(backtest_realism.get("rows") or []))
    _append_check_rows(display_rows, area="Look-through Exposure", checks=list(look_through.get("summary_rows") or []))
    _append_check_rows(display_rows, area="Robustness Lab", checks=list(robustness_lab.get("summary_rows") or []))
    _append_check_rows(display_rows, area="Robustness", checks=list(robustness.get("checks") or []))
    _append_check_rows(display_rows, area="Paper Observation", checks=list(paper_snapshot.get("checks") or []))
    return display_rows


def _markdown_value(value: Any, default: str = "-") -> str:
    if value is None:
        text = default
    elif isinstance(value, str):
        text = value.strip() or default
    else:
        text = str(value).strip() or default
    return text.replace("|", "\\|").replace("\n", "<br>")


def _markdown_table(rows: list[dict[str, Any]], columns: list[str]) -> list[str]:
    if not rows:
        return ["- 표시할 row가 없습니다."]
    lines = [
        "| " + " | ".join(columns) + " |",
        "| " + " | ".join("---" for _ in columns) + " |",
    ]
    for row in rows:
        lines.append("| " + " | ".join(_markdown_value(row.get(column)) for column in columns) + " |")
    return lines


def _decision_dossier_filename(decision_id: Any) -> str:
    safe_id = "".join(
        char if char.isalnum() or char in {"-", "_"} else "_"
        for char in _safe_text(decision_id, "final_decision")
    )
    return f"{safe_id}_decision_dossier.md"


def _decision_source_contract(
    raw_decision: dict[str, Any],
    *,
    surface: str,
    monitoring_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    timeline_contract = dict(dict(monitoring_timeline or {}).get("source_contract") or {})
    session_sources = [
        str(source).strip()
        for source in list(timeline_contract.get("session_evidence_sources") or [])
        if str(source or "").strip()
    ]
    decision_id = _safe_text(raw_decision.get("decision_id"), "")
    source_type = _safe_text(raw_decision.get("source_type"), "")
    source_id = _safe_text(raw_decision.get("source_id"), "")
    return {
        "schema_version": DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION,
        "surface": _safe_text(surface, "decision_dossier"),
        "decision_id": decision_id,
        "decision_route": _safe_text(raw_decision.get("decision_route"), ""),
        "selected_practical_portfolio": bool(raw_decision.get("selected_practical_portfolio")),
        "source_type": source_type,
        "source_id": source_id,
        "source_title": _safe_text(raw_decision.get("source_title"), ""),
        "selection_source_id": _safe_text(raw_decision.get("selection_source_id"), ""),
        "validation_id": _safe_text(raw_decision.get("validation_id"), ""),
        "source_identity": f"{source_type}:{source_id}" if source_type or source_id else "",
        "durable_source": "FINAL_PORTFOLIO_SELECTION_DECISIONS",
        "registry_file": "FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl",
        "timeline_contract_present": bool(timeline_contract),
        "timeline_contract_consistent": _timeline_contract_matches_decision(raw_decision, timeline_contract)
        if timeline_contract
        else None,
        "session_evidence_sources": session_sources,
        "evidence_scope": "final_decision_plus_optional_session_timeline",
        "execution_boundary": {
            "write_policy": "read_only_decision_source_contract",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Decision Dossier reads the saved Final Decision row and optional Portfolio Monitoring session timeline only.",
        },
    }


def _timeline_contract_matches_decision(raw_decision: dict[str, Any], timeline_contract: dict[str, Any]) -> bool:
    if not timeline_contract:
        return False
    fields = ("decision_id", "decision_route", "source_type", "source_id", "selection_source_id", "validation_id")
    return all(
        _safe_text(raw_decision.get(field), "") == _safe_text(timeline_contract.get(field), "")
        for field in fields
    )


def _decision_dossier_component_rows(raw_decision: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for index, component in enumerate(list(raw_decision.get("selected_components") or []), start=1):
        component_row = dict(component or {})
        rows.append(
            {
                "Order": index,
                "Title": component_row.get("title")
                or component_row.get("strategy_name")
                or component_row.get("registry_id")
                or f"component_{index}",
                "Registry ID": component_row.get("registry_id") or "-",
                "Target Weight": component_row.get("target_weight") or component_row.get("weight") or "-",
                "Benchmark": component_row.get("benchmark") or "-",
            }
        )
    return rows


def _decision_dossier_markdown(dossier: dict[str, Any]) -> str:
    decision = dict(dossier.get("decision") or {})
    operator = dict(dossier.get("operator") or {})
    validation = dict(dossier.get("validation_summary") or {})
    gate_policy = dict(dossier.get("gate_policy") or {})
    monitoring = dict(dossier.get("monitoring_timeline") or {})
    source_contract = dict(dossier.get("source_contract") or {})
    boundary = dict(dossier.get("execution_boundary") or {})
    metrics = dict(dossier.get("metrics") or {})
    lines = [
        "# Final Decision Dossier",
        "",
        "## Summary",
        f"- Decision ID: `{_markdown_value(decision.get('decision_id'))}`",
        f"- Source: `{_markdown_value(decision.get('source_type'))}` / `{_markdown_value(decision.get('source_id'))}`",
        f"- Title: {_markdown_value(decision.get('source_title'))}",
        f"- Decision: {_markdown_value(decision.get('decision_label'))} (`{_markdown_value(decision.get('decision_route'))}`)",
        f"- Final Status: `{_markdown_value(decision.get('status_route'))}`",
        f"- Evidence Route: `{_markdown_value(decision.get('evidence_route'))}`",
        f"- Gate Outcome: `{_markdown_value(gate_policy.get('outcome'))}`",
        f"- Selected Practical Portfolio: `{_markdown_value(decision.get('selected_practical_portfolio'))}`",
        "",
        "## Source Contract",
        f"- Durable Source: `{_markdown_value(source_contract.get('durable_source'))}`",
        f"- Source Identity: `{_markdown_value(source_contract.get('source_identity'))}`",
        f"- Timeline Contract Present: `{_markdown_value(source_contract.get('timeline_contract_present'))}`",
        f"- Timeline Contract Consistent: `{_markdown_value(source_contract.get('timeline_contract_consistent'))}`",
        f"- Session Evidence Sources: {_markdown_value(', '.join(source_contract.get('session_evidence_sources') or []))}",
        "",
        "## Operator Decision",
        f"- Reason: {_markdown_value(operator.get('reason'))}",
        f"- Constraints: {_markdown_value(operator.get('constraints'))}",
        f"- Next Action: {_markdown_value(operator.get('next_action'))}",
        f"- Review Cadence: `{_markdown_value(operator.get('review_cadence'))}`",
        f"- Review Triggers: {_markdown_value(', '.join(operator.get('review_triggers') or []))}",
        "",
        "## Validation Snapshot",
        f"- Validation Route: `{_markdown_value(validation.get('validation_route'))}`",
        f"- Validation Score: `{_markdown_value(validation.get('validation_score'))}`",
        f"- Robustness Route: `{_markdown_value(validation.get('robustness_route'))}`",
        f"- Paper Observation Route: `{_markdown_value(validation.get('paper_observation_route'))}`",
        f"- Diagnostic Counts: `{_markdown_value(validation.get('status_counts'))}`",
        "",
        "## Selected Components",
        *_markdown_table(
            list(dossier.get("components") or []),
            ["Order", "Title", "Registry ID", "Target Weight", "Benchmark"],
        ),
        "",
        "## Evidence Checks",
        *_markdown_table(
            list(dossier.get("evidence_checks") or []),
            ["Area", "Criteria", "Ready", "Current", "Meaning", "Score"],
        ),
        "",
        "## Gate Policy",
        *_markdown_table(
            list(gate_policy.get("policy_rows") or []),
            ["Group", "Status", "Severity", "Current", "Evidence", "Required Action"],
        ),
        "",
        "## Monitoring Timeline",
    ]
    if monitoring.get("present"):
        lines.extend(
            _markdown_table(
                list(monitoring.get("rows") or []),
                ["order", "event", "timestamp", "status_label", "signal", "next_action", "source"],
            )
        )
    else:
        lines.append("- 현재 dossier에는 Portfolio Monitoring session timeline이 포함되지 않았습니다.")
    lines.extend(
        [
            "",
            "## Execution Boundary",
            *_markdown_table(
                [
                    {"Boundary": "Write Policy", "Value": boundary.get("write_policy")},
                    {"Boundary": "DB Write", "Value": boundary.get("db_write")},
                    {"Boundary": "Registry Write", "Value": boundary.get("registry_write")},
                    {"Boundary": "Report Auto Write", "Value": boundary.get("report_auto_write")},
                    {"Boundary": "Monitoring Log Auto Write", "Value": boundary.get("monitoring_log_auto_write")},
                    {"Boundary": "Live Approval", "Value": boundary.get("live_approval")},
                    {"Boundary": "Order Instruction", "Value": boundary.get("order_instruction")},
                    {"Boundary": "Auto Rebalance", "Value": boundary.get("auto_rebalance")},
                ],
                ["Boundary", "Value"],
            ),
            "",
            "## Metrics",
            f"- Components: `{_markdown_value(metrics.get('component_count'))}`",
            f"- Evidence Checks: `{_markdown_value(metrics.get('evidence_check_count'))}`",
            f"- Not Ready Evidence Checks: `{_markdown_value(metrics.get('not_ready_evidence_check_count'))}`",
            "",
            "> This dossier is a decision-support export. It is not live approval, broker order instruction, or automated rebalance authorization.",
        ]
    )
    return "\n".join(lines) + "\n"


def build_decision_dossier(
    row: dict[str, Any],
    *,
    monitoring_timeline: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a read-only human-readable dossier for a saved final decision row."""

    raw_decision = dict(row.get("raw_decision") or row or {})
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    packet = dict(raw_decision.get("investability_evidence_packet") or {})
    gate_policy = dict(
        raw_decision.get("selection_gate_policy_snapshot")
        or raw_decision.get("gate_policy_snapshot")
        or packet.get("selection_gate_policy_snapshot")
        or packet.get("gate_policy_snapshot")
        or {}
    )
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    operator_decision = dict(raw_decision.get("operator_decision") or {})
    status_display = build_final_review_status_display(raw_decision)
    decision_route = _safe_text(raw_decision.get("decision_route"))
    evidence_checks = build_final_decision_evidence_rows(raw_decision)
    not_ready_count = sum(1 for check in evidence_checks if not bool(check.get("Ready")))
    timeline = dict(monitoring_timeline or {})
    source_contract = _decision_source_contract(
        raw_decision,
        surface="decision_dossier",
        monitoring_timeline=timeline,
    )
    monitoring_payload = {
        "present": bool(timeline),
        "schema_version": timeline.get("schema_version"),
        "timeline_status": timeline.get("timeline_status"),
        "timeline_label": timeline.get("timeline_label"),
        "conclusion": timeline.get("conclusion"),
        "rows": list(timeline.get("rows") or []),
        "metrics": dict(timeline.get("metrics") or {}),
    }
    dossier: dict[str, Any] = {
        "schema_version": DECISION_DOSSIER_SCHEMA_VERSION,
        "decision": {
            "decision_id": raw_decision.get("decision_id"),
            "created_at": raw_decision.get("created_at"),
            "updated_at": raw_decision.get("updated_at"),
            "decision_route": decision_route,
            "decision_label": FINAL_REVIEW_DECISION_LABELS.get(decision_route, "재검토 필요"),
            "selected_practical_portfolio": bool(raw_decision.get("selected_practical_portfolio")),
            "source_type": raw_decision.get("source_type"),
            "source_id": raw_decision.get("source_id"),
            "source_title": raw_decision.get("source_title"),
            "selection_source_id": raw_decision.get("selection_source_id"),
            "validation_id": raw_decision.get("validation_id"),
            "evidence_route": evidence.get("route"),
            "packet_route": packet.get("route"),
            "status_route": status_display.get("route"),
            "status_verdict": status_display.get("verdict"),
            "status_next_action": status_display.get("next_action"),
        },
        "operator": {
            "reason": operator_decision.get("reason"),
            "constraints": operator_decision.get("constraints"),
            "next_action": operator_decision.get("next_action"),
            "review_cadence": paper_snapshot.get("review_cadence"),
            "review_triggers": list(paper_snapshot.get("review_triggers") or []),
        },
        "validation_summary": {
            "validation_route": risk_snapshot.get("validation_route"),
            "validation_score": risk_snapshot.get("validation_score"),
            "status_counts": dict(dict(risk_snapshot.get("diagnostic_summary") or {}).get("status_counts") or {}),
            "provider_status": _provider_status_summary(risk_snapshot),
            "robustness_route": robustness.get("robustness_route"),
            "robustness_score": robustness.get("robustness_score"),
            "paper_observation_route": paper_snapshot.get("route"),
            "not_run_domains": list(risk_snapshot.get("not_run_domains") or []),
            "not_run_critical_domains": list(risk_snapshot.get("not_run_critical_domains") or []),
        },
        "components": _decision_dossier_component_rows(raw_decision),
        "evidence_checks": evidence_checks,
        "gate_policy": {
            "schema_version": gate_policy.get("schema_version"),
            "outcome": gate_policy.get("outcome"),
            "select_allowed": bool(gate_policy.get("select_allowed")),
            "blockers": list(gate_policy.get("blockers") or []),
            "review_required": list(gate_policy.get("review_required") or []),
            "policy_rows": list(gate_policy.get("policy_rows") or []),
        },
        "monitoring_timeline": monitoring_payload,
        "source_contract": source_contract,
        "metrics": {
            "component_count": len(raw_decision.get("selected_components") or []),
            "evidence_check_count": len(evidence_checks),
            "not_ready_evidence_check_count": not_ready_count,
            "gate_policy_row_count": len(gate_policy.get("policy_rows") or []),
            "monitoring_timeline_present": bool(timeline),
            "source_contract_present": True,
            "timeline_source_contract_present": source_contract.get("timeline_contract_present"),
            "source_contract_consistent": source_contract.get("timeline_contract_consistent")
            if source_contract.get("timeline_contract_present")
            else True,
        },
        "execution_boundary": {
            "write_policy": "read_only_dossier",
            "db_write": False,
            "registry_write": False,
            "report_auto_write": False,
            "monitoring_log_auto_write": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Dossier is generated from existing final decision evidence and optional session timeline only.",
        },
    }
    dossier["filename"] = _decision_dossier_filename(raw_decision.get("decision_id"))
    dossier["markdown"] = _decision_dossier_markdown(dossier)
    return dossier


__all__ = [
    "DECISION_DOSSIER_SCHEMA_VERSION",
    "DECISION_SOURCE_CONSISTENCY_SCHEMA_VERSION",
    "CANDIDATE_BOARD_SCHEMA_VERSION",
    "DECISION_RECORD_GUIDE_SCHEMA_VERSION",
    "SAVED_DECISION_REVIEW_SCHEMA_VERSION",
    "FINAL_REVIEW_DECISION_LABELS",
    "FINAL_REVIEW_STATUS_DISPLAY",
    "SELECT_FOR_PRACTICAL_PORTFOLIO",
    "build_decision_dossier",
    "build_final_review_candidate_board",
    "build_final_review_candidate_board_rows",
    "build_final_review_decision_cockpit",
    "build_final_review_decision_record_guide",
    "build_saved_final_review_decision_review",
    "build_investability_gate_policy",
    "build_investability_evidence_packet",
    "build_final_decision_evidence_rows",
    "build_final_review_decision_display_rows",
    "build_final_review_status_display",
    "build_selected_route_gate",
]
