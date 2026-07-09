from __future__ import annotations

from typing import Any

from app.services.backtest_practical_validation_stage_roles import review_role_fields
from app.services.backtest_validation_status_policy import normalize_validation_status


SOURCE_READINESS_MODULE_IDS = {
    "source_integrity",
    "latest_replay",
    "benchmark_parity",
}
VALIDATION_READINESS_MODULE_IDS = {
    "validation_efficacy",
    "data_coverage",
    "construction_risk",
    "backtest_realism",
    "stress_robustness",
}
FINAL_REVIEW_READINESS_PREVIEW_MODULE_IDS = {
    "selected_route_preflight",
}
CONDITIONAL_EVIDENCE_MODULE_IDS = {
    "provider_investability",
    "leverage_inverse",
    "risk_contribution",
    "component_role_weight",
    "macro_regime",
}
DOWNSTREAM_STAGE_OWNERS = {
    "final_review",
    "selected_dashboard",
}
STAGE_OWNER_LABELS = {
    "backtest_analysis": "Backtest Analysis",
    "practical_validation": "Practical Validation",
    "final_review": "Final Review",
    "selected_dashboard": "Operations > Portfolio Monitoring",
}
STAGE_OWNER_ORDER = ("backtest_analysis", "practical_validation", "final_review", "selected_dashboard")
FLOW4_CATEGORY_GROUP_SPECS = [
    {
        "group_id": "source_replay",
        "label": "Source & Replay",
        "purpose": "후보 source 계약과 최신 runtime replay가 같은 후보를 재현하는지 확인합니다.",
        "module_ids": ("source_integrity", "latest_replay"),
    },
    {
        "group_id": "data_bias_control",
        "label": "Data Quality / Bias Control",
        "purpose": "가격, 기간, PIT, 생존편향 근거가 검증 결과를 왜곡하지 않는지 확인합니다.",
        "module_ids": ("data_coverage",),
    },
    {
        "group_id": "comparison_validity",
        "label": "Comparison Validity",
        "purpose": "benchmark와 comparator가 후보와 같은 조건으로 비교되는지 확인합니다.",
        "module_ids": ("benchmark_parity",),
    },
    {
        "group_id": "realism_tradability",
        "label": "Realism / Tradability",
        "purpose": "비용, turnover, liquidity, net curve, rebalance timing이 실전 해석에 충분한지 확인합니다.",
        "module_ids": ("backtest_realism",),
    },
    {
        "group_id": "validation_method_strength",
        "label": "Validation Method Strength",
        "purpose": "walk-forward, OOS, regime split으로 성과가 특정 구간에만 기대지 않는지 확인합니다.",
        "module_ids": ("validation_efficacy",),
    },
    {
        "group_id": "stress_robustness",
        "label": "Stress / Robustness",
        "purpose": "stress, rolling, sensitivity, overfit 근거로 설정 변화와 시장 충격에 대한 강건성을 확인합니다.",
        "module_ids": ("stress_robustness",),
    },
    {
        "group_id": "portfolio_construction",
        "label": "Portfolio Construction",
        "purpose": "ETF-like 또는 weighted mix 후보의 구성, 집중, 위험 기여, 역할 / 비중 근거를 확인합니다.",
        "module_ids": ("construction_risk", "risk_contribution", "component_role_weight"),
    },
    {
        "group_id": "conditional_context",
        "label": "Conditional Evidence",
        "purpose": "ETF 운용사 / 공식 외부 데이터, 레버리지 / 인버스, macro 조건처럼 후보 특성에 따라 필요한 추가 근거를 확인합니다.",
        "module_ids": ("provider_investability", "leverage_inverse", "macro_regime"),
    },
]
STATUS_LABELS = {
    "PASS": "통과",
    "READY": "통과",
    "REVIEW": "확인 필요",
    "NEEDS_INPUT": "근거 보강 필요",
    "NOT_RUN": "아직 실행 안 됨",
    "BLOCKED": "이동 차단",
    "NOT_APPLICABLE": "비적용",
}
OUTCOME_TEXT = {
    "pass": {
        "label": "통과",
        "detail": "현재 기준에서 Final Review 이동을 막는 항목은 없습니다.",
        "headline": "카테고리별 검증 결과가 통과 상태입니다.",
        "tone": "positive",
    },
    "repair_required": {
        "label": "보강 후 재검증 필요",
        "detail": "자료, 근거, 실행 gap을 보강한 뒤 다시 검증해야 합니다.",
        "headline": "보강 후 재검증할 항목이 남아 있습니다.",
        "tone": "warning",
    },
    "review_required": {
        "label": "주의 확인 필요",
        "detail": "자동 차단은 아니지만 stage role에 따라 확인해야 합니다.",
        "headline": "역할별 REVIEW 항목이 남아 있습니다.",
        "tone": "warning",
    },
    "not_practical": {
        "label": "실전 사용 어려움",
        "detail": "현재 상태로는 포트폴리오를 실전 후보로 사용하기 어렵습니다.",
        "headline": "현재 상태로는 실전 사용이 어렵습니다.",
        "tone": "danger",
    },
    "not_applicable": {
        "label": "비적용",
        "detail": "현재 후보에는 적용되지 않는 기준입니다.",
        "headline": "현재 후보에 적용되지 않는 기준입니다.",
        "tone": "neutral",
    },
}
GROUP_DISPLAY_TEXT = {
    "source_readiness": {
        "display_label": "후보 source가 검증 가능한가",
        "purpose": "Backtest Analysis에서 넘어온 후보가 source id, 최신 재검증, 비교 기준을 갖췄는지 확인합니다.",
    },
    "validation_readiness": {
        "display_label": "검증 근거가 충분한가",
        "purpose": "데이터, 구성, 현실성, robustness 근거가 Final Review 이동에 충분한지 확인합니다.",
    },
    "final_review_readiness_preview": {
        "display_label": "Final Review 저장 전에 막힐 gap이 없는가",
        "purpose": "Final Review 후보로 넘겼을 때 저장을 막을 deterministic evidence gap을 미리 확인합니다.",
    },
    "source_replay": {
        "display_label": "후보 source / 최신 재검증",
        "purpose": "Backtest Analysis에서 넘어온 후보가 같은 계약으로 최신 데이터에서도 재현되는지 확인합니다.",
    },
    "data_bias_control": {
        "display_label": "데이터 품질 / 편향 통제",
        "purpose": "가격, 기간, point-in-time, 생존편향 근거가 검증 결과를 왜곡하지 않는지 확인합니다.",
    },
    "comparison_validity": {
        "display_label": "비교 기준 동등성",
        "purpose": "후보와 benchmark / comparator가 같은 기간, frequency, coverage로 비교되는지 확인합니다.",
    },
    "realism_tradability": {
        "display_label": "실전 운용 현실성",
        "purpose": "비용, turnover, liquidity, net curve, rebalance timing이 실전 해석에 충분한지 확인합니다.",
    },
    "validation_method_strength": {
        "display_label": "검증 방법론 강도",
        "purpose": "walk-forward, OOS, regime split 근거가 결과 해석에 충분한지 확인합니다.",
    },
    "stress_robustness": {
        "display_label": "강건성 / 스트레스",
        "purpose": "stress, rolling, sensitivity, overfit 근거가 결과 해석에 충분한지 확인합니다.",
    },
    "portfolio_construction": {
        "display_label": "포트폴리오 구성 근거",
        "purpose": "구성 집중, look-through, 위험 기여, component 역할 / 비중 근거를 확인합니다.",
    },
    "conditional_evidence": {
        "display_label": "후보 특성별 추가 근거가 필요한가",
        "purpose": "ETF, weighted mix, tactical source처럼 후보 특성에 따라 필요한 추가 검증을 확인합니다.",
    },
    "conditional_context": {
        "display_label": "후보 특성별 추가 근거",
        "purpose": "ETF 운용사 / 공식 외부 데이터, 레버리지 / 인버스, macro 조건처럼 해당 후보에만 필요한 근거를 확인합니다.",
    },
    "final_review_handoff_summary": {
        "display_label": "Final Review 이동 요약",
        "purpose": "검증 category가 아니라 Final Review 저장 전에 막힐 gap을 요약합니다.",
    },
}
MODULE_DISPLAY_TEXT = {
    "source_integrity": {
        "display_label": "후보 source와 비중 계약이 유효한가",
        "issue_title": "후보 source 계약 불완전",
        "current_problem": "source id, active component, target weight, Data Trust, curve evidence 중 연결되지 않은 항목이 있으면 어떤 후보를 검증하는지 추적하기 어렵습니다.",
        "completion_criteria": "Source Integrity가 PASS 상태이고 후보 source / component / weight / curve evidence가 같은 계약으로 연결되어야 합니다.",
        "fix_location": "Flow 1 · 후보 Source 확인",
        "impact_summary": "source 계약이 불완전하면 Final Review가 같은 후보를 안정적으로 다시 읽을 수 없습니다.",
    },
    "latest_replay": {
        "display_label": "최신 데이터로 전략을 다시 돌렸는가",
        "issue_title": "최신 재검증 / 기간 coverage 확인 필요",
        "current_problem": "현재 세션에서 최신 DB 기준 재검증이 실행되지 않았거나 요청 종료일까지 replay curve가 충분히 따라왔는지 확인이 필요합니다.",
        "completion_criteria": "Flow 2 재검증 결과가 PASS 또는 REVIEW이고, 미실행 / 보강 필요 상태가 없어야 합니다.",
        "fix_location": "Flow 2 · 실전 재검증 실행",
        "impact_summary": "최신 데이터로 재현되지 않은 후보는 Final Review에서 실전 검증 완료 후보로 보기 어렵습니다.",
    },
    "benchmark_parity": {
        "display_label": "후보와 비교 기준이 같은 조건으로 비교됐는가",
        "issue_title": "비교 기준 동등성 부족",
        "current_problem": "benchmark, cash, simple baseline, custom comparator의 기간 / frequency / coverage가 후보와 맞지 않으면 비교가 왜곡됩니다.",
        "completion_criteria": "Benchmark / Comparator Parity가 PASS 상태이고 후보와 비교 기준이 같은 기간 / frequency / coverage로 정렬되어야 합니다.",
        "fix_location": "Flow4 > 핵심 근거 > Input Evidence / Curve·Recheck Evidence",
        "impact_summary": "비교 조건이 다르면 후보 성과가 좋아 보이는 이유를 공정하게 판단하기 어렵습니다.",
    },
    "validation_efficacy": {
        "display_label": "검증이 우연한 좋은 구간에만 기대지 않는가",
        "issue_title": "검증 방법론 근거 부족",
        "current_problem": "walk-forward / OOS / regime split 근거 중 일부가 비어 있거나 보강 필요 상태입니다.",
        "completion_criteria": "Validation Method Strength 핵심 항목이 PASS 또는 해당 REVIEW 역할 확인 상태가 되어야 합니다.",
        "fix_location": "Flow4 > 검증 방법론 > 검증 방법론 강도 상세",
        "impact_summary": "검증 방법 근거가 부족하면 성과가 특정 기간에만 우연히 좋았는지 구분하기 어렵습니다.",
    },
    "data_coverage": {
        "display_label": "검증에 필요한 가격 / ETF 운용사 / 생존편향 데이터가 충분한가",
        "issue_title": "데이터 커버리지 부족",
        "current_problem": "가격 window, ETF 운용사 / 공식 외부 데이터 freshness, lifecycle, survivorship evidence 중 비어 있거나 오래된 데이터가 있습니다.",
        "completion_criteria": "데이터 커버리지 핵심 항목이 PASS 또는 해당 REVIEW 역할 확인 상태이고 수집 가능한 외부 데이터 gap이 저장 / 이동을 막지 않아야 합니다.",
        "fix_location": "Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세",
        "impact_summary": "데이터 커버리지가 부족하면 검증 결과가 일부 ticker나 현재 snapshot에만 기대게 됩니다.",
    },
    "construction_risk": {
        "display_label": "구성 / 집중 위험을 설명할 근거가 있는가",
        "issue_title": "구성 / 집중 위험 근거 부족",
        "current_problem": "ETF 내부 보유 / exposure coverage나 concentration evidence가 부족하면 실제 구성 위험을 설명하기 어렵습니다.",
        "completion_criteria": "Construction Risk가 PASS 또는 해당 REVIEW 역할 확인 상태이고 집중 / overlap / unknown exposure가 판단 근거로 정리되어야 합니다.",
        "fix_location": "Flow4 > 구성 / 리스크 > 포트폴리오 구성 근거 상세",
        "impact_summary": "구성 위험을 설명하지 못하면 좋은 백테스트라도 실제 운용 위험을 판단하기 어렵습니다.",
    },
    "backtest_realism": {
        "display_label": "실전 운용 비용과 거래 현실성이 반영됐는가",
        "issue_title": "실전 운용 현실성 근거 부족",
        "current_problem": "비용 적용, turnover, liquidity, net curve 근거가 없으면 백테스트 성과가 실전 운용 성과와 달라질 수 있습니다.",
        "completion_criteria": "Backtest Realism 핵심 항목이 PASS 또는 해당 REVIEW 역할 확인 상태이고 cost / turnover / liquidity blocker가 없어야 합니다.",
        "fix_location": "Flow4 > 실전성 > 실전 운용 현실성 상세",
        "impact_summary": "비용과 거래 현실성이 빠지면 실전 성과가 백테스트보다 크게 달라질 수 있습니다.",
    },
    "stress_robustness": {
        "display_label": "시장 충격과 설정 변화에도 버티는가",
        "issue_title": "강건성 근거 부족",
        "current_problem": "stress / rolling / sensitivity / overfit 근거 중 실행되지 않았거나 부족한 항목이 있습니다.",
        "completion_criteria": "Stress / Robustness가 PASS 또는 해당 REVIEW 역할 확인 상태이고 미실행 핵심 항목이 없어야 합니다.",
        "fix_location": "Flow4 > 강건성 > Stress / sensitivity 상세",
        "impact_summary": "강건성 근거가 약하면 특정 조건에 과최적화된 후보일 수 있습니다.",
    },
    "selected_route_preflight": {
        "display_label": "Final Review 저장 전에 막힐 필수 gap이 없는가",
        "issue_title": "Final Review 저장 전 필수 gap",
        "current_problem": "Final Review 저장 전에 필요한 evidence packet, selected-route policy, review-required gap이 남아 있습니다.",
        "completion_criteria": "Selected-route Preflight가 PASS 또는 저장 전 보강 확인 상태이고 저장 차단 gap이 없어야 합니다.",
        "fix_location": "Final Review 이동 요약",
        "impact_summary": "여기서 gap을 확인하지 않으면 Final Review로 넘어가도 저장 단계에서 다시 막힐 수 있습니다.",
    },
    "provider_investability": {
        "display_label": "ETF 운용사 / 공식 외부 데이터 근거가 충분한가",
        "issue_title": "ETF 운용사 / 공식 외부 데이터 근거 부족",
        "current_problem": "ETF 운용사 snapshot이나 holdings / exposure 근거가 없으면 ETF 내부 노출과 운용 가능성을 판단하기 어렵습니다.",
        "completion_criteria": "ETF Provider Investability가 PASS 또는 해당 REVIEW 역할 확인 상태이고 운용사 / 공식 외부 데이터 snapshot gap이 보강되어야 합니다.",
        "fix_location": "Flow4 > 데이터 보강 / 수집 실행",
        "impact_summary": "운용사 / 공식 외부 데이터 근거가 약하면 ETF 내부 노출과 실전 운용 가능성을 판단하기 어렵습니다.",
    },
    "leverage_inverse": {
        "display_label": "레버리지 / 인버스 노출이 목적과 맞는가",
        "issue_title": "레버리지 / 인버스 적합성 확인 필요",
        "current_problem": "레버리지 / 인버스 ticker가 포함되면 일간 목표 상품 특성과 보유 기간, 손실 허용 기준이 후보 목적과 맞는지 별도 확인이 필요합니다.",
        "completion_criteria": "노출 목적, 보유 기간, 손실 허용 기준이 2단계 실용성 주의 근거로 정리되어야 합니다.",
        "fix_location": "Flow4 > 조건부 근거 > 레버리지 / 인버스 적합성",
        "impact_summary": "레버리지 / 인버스 노출은 장기 보유 목적과 충돌하거나 손실 확대 위험을 만들 수 있습니다.",
    },
    "risk_contribution": {
        "display_label": "weighted mix의 위험 기여가 한쪽으로 쏠리지 않는가",
        "issue_title": "위험 기여 설명 부족",
        "current_problem": "component matrix나 risk contribution evidence가 없으면 weighted mix 위험이 한쪽으로 쏠렸는지 설명하기 어렵습니다.",
        "completion_criteria": "Risk Contribution이 PASS 또는 해당 REVIEW 역할 확인 상태이고 component matrix / correlation / drop-one 근거가 있어야 합니다.",
        "fix_location": "Flow4 > 구성 / 리스크 > 위험 기여 상세",
        "impact_summary": "위험 기여가 설명되지 않으면 여러 component를 섞은 이유를 Final Review에서 판단하기 어렵습니다.",
    },
    "component_role_weight": {
        "display_label": "component 역할과 비중 이유가 설명되는가",
        "issue_title": "component 역할 / 비중 근거 부족",
        "current_problem": "component role이나 weight rationale이 없으면 mix 구성 의도가 부족합니다.",
        "completion_criteria": "Component Role / Weight가 PASS 또는 해당 REVIEW 역할 확인 상태이고 role source와 weight rationale이 정리되어야 합니다.",
        "fix_location": "Flow4 > 구성 / 리스크 > Component 역할 / 비중 상세",
        "impact_summary": "역할과 비중 이유가 없으면 좋은 결과가 우연한 조합인지 판단하기 어렵습니다.",
    },
    "macro_regime": {
        "display_label": "전술형 전략의 macro / regime 근거가 있는가",
        "issue_title": "macro / regime 근거 확인 필요",
        "current_problem": "전술형 또는 헤지형 후보는 macro regime과 risk-on/off context가 전략 약점과 충돌하지 않는지 확인해야 합니다.",
        "completion_criteria": "macro snapshot, regime split, risk-on/off context가 2단계 실용성 주의 근거로 정리되어야 합니다.",
        "fix_location": "Flow4 > Raw Evidence > Practical Diagnostics",
        "impact_summary": "macro / regime 근거가 없으면 전술형 전략의 성과가 특정 시장 환경에만 기대는지 판단하기 어렵습니다.",
    },
}
MODULE_RESOLUTION_GUIDES = {
    "source_integrity": {
        "checked_summary": "후보 source id, active component, target weight, Data Trust, curve evidence가 같은 후보 계약으로 연결되는지 확인합니다.",
        "missing_summary": "source 계약 중 연결되지 않은 항목",
        "next_action_summary": "Flow 1에서 source snapshot을 확인하고 부족하면 Backtest Analysis에서 후보를 다시 구성합니다.",
        "action_steps": [
            "Flow 1의 source snapshot에서 source id, active component, target weight가 같은 후보를 가리키는지 확인합니다.",
            "Data Trust 또는 curve evidence가 빠졌으면 Backtest Analysis에서 후보를 다시 구성한 뒤 Practical Validation으로 넘깁니다.",
        ],
        "location": "Flow1 > 후보 Source 확인",
    },
    "latest_replay": {
        "checked_summary": "저장 당시 성과가 아니라 현재 DB 최신 시장일까지 같은 전략이 재현되는지 확인합니다.",
        "missing_summary": "현재 세션의 latest runtime replay 또는 coverage 확인",
        "next_action_summary": "`전략 재검증 실행`을 누른 뒤 Recheck와 Coverage가 Final Review 이동을 막지 않는지 확인합니다.",
        "action_steps": [
            "Flow 2에서 `전략 재검증 실행`을 눌러 현재 DB 최신 시장일까지 replay를 실행합니다.",
            "Recheck End와 coverage가 저장 시점 이후 기간을 포함하는지 확인합니다.",
            "재검증 후 같은 기준 카드가 PASS 또는 해당 REVIEW 역할 확인 상태로 바뀌었는지 확인합니다.",
        ],
        "location": "Flow2 > 검증 기준 설정 / 실전 재검증 실행",
    },
    "benchmark_parity": {
        "checked_summary": "후보와 benchmark / cash / simple baseline / custom comparator가 같은 기간, frequency, coverage로 비교됐는지 확인합니다.",
        "missing_summary": "비교 기준 curve의 기간, frequency, coverage 정렬 근거",
        "next_action_summary": "핵심 근거 탭에서 comparator curve와 recheck evidence를 확인하고 부족한 비교 기준 근거를 보강합니다.",
        "action_steps": [
            "비교 기준 curve가 후보와 같은 기간, frequency, coverage로 만들어졌는지 확인합니다.",
            "비교 기준이 빠졌으면 핵심 근거의 comparator evidence를 보강합니다.",
            "후보 성과가 cash / benchmark / simple baseline과 같은 조건에서 비교되는지 다시 확인합니다.",
        ],
        "location": "Flow4 > 핵심 근거 > Input Evidence / Curve·Recheck Evidence",
    },
    "validation_efficacy": {
        "checked_summary": "walk-forward, OOS, regime split 근거가 성과 해석에 충분한지 확인합니다.",
        "missing_summary": "walk-forward / OOS / regime split 중 보강 필요 항목",
        "next_action_summary": "검증 방법론 강도 상세에서 non-PASS row를 확인하고 부족한 방법론 근거를 보강합니다.",
        "action_steps": [
            "검증 방법론 강도 상세에서 non-PASS 기준이 walk-forward, OOS, regime split 중 무엇인지 확인합니다.",
            "부족한 방법론 근거를 보강합니다.",
            "보강 후 Flow 2 재검증으로 해당 기준이 PASS 또는 해당 REVIEW 역할 확인 상태인지 확인합니다.",
        ],
        "location": "Flow4 > 검증 방법론 > 검증 방법론 강도 상세",
    },
    "data_coverage": {
        "checked_summary": "가격 window, ETF 운용사 / 공식 외부 데이터 freshness, PIT replay, universe / lifecycle, survivorship 근거가 충분한지 확인합니다.",
        "missing_summary": "가격 window / ETF 운용사 freshness / lifecycle / survivorship 중 비어 있거나 오래된 항목",
        "next_action_summary": "데이터 품질 상세에서 non-PASS row를 확인하고, 수집 가능한 외부 데이터 gap은 데이터 보강 / 수집 실행에서 처리합니다.",
        "action_steps": [
            "운용사 / 공식 외부 데이터 gap은 데이터 보강 / 수집 실행에서 수집하고, 가격 window gap은 DB price ingestion으로 보강합니다.",
            "보강 후 Flow 2 재검증을 다시 실행해 coverage blocker가 해소됐는지 확인합니다.",
            "그래도 막히면 데이터 품질 / 편향 통제 상세에서 lifecycle 또는 survivorship 기준까지 확인합니다.",
        ],
        "location": "Flow4 > 데이터 > 데이터 품질 / 편향 통제 상세",
        "action_location": "Flow4 > 데이터 보강 / 수집 실행",
    },
    "construction_risk": {
        "checked_summary": "ETF-like 또는 weighted mix 후보의 구성 집중, look-through, top holding, overlap, unknown exposure를 확인합니다.",
        "missing_summary": "구성 집중, holdings / exposure coverage, overlap, unknown exposure 근거",
        "next_action_summary": "포트폴리오 구성 근거 상세에서 non-PASS row를 확인하고 운용사 look-through 근거를 보강합니다.",
        "action_steps": [
            "포트폴리오 구성 근거 상세에서 집중, holdings coverage, overlap, unknown exposure 중 막힌 기준을 확인합니다.",
            "ETF 또는 mix 구성의 look-through / top holding / exposure 근거를 보강합니다.",
            "구성 위험이 설명 가능한 수준인지 2단계 실용성 주의 근거로 다시 확인합니다.",
        ],
        "location": "Flow4 > 구성 / 리스크 > 포트폴리오 구성 근거 상세",
    },
    "backtest_realism": {
        "checked_summary": "거래비용, turnover, liquidity, net curve, rebalance timing이 실전 해석에 반영됐는지 확인합니다.",
        "missing_summary": "cost / turnover / liquidity / net performance / rebalance timing 중 부족한 근거",
        "next_action_summary": "실전 운용 현실성 상세에서 non-PASS row를 확인하고 비용 / 거래 현실성 근거를 보강합니다.",
        "action_steps": [
            "실전 운용 현실성 상세에서 비용, turnover, liquidity, net curve, rebalance timing 중 막힌 기준을 확인합니다.",
            "비용 반영 또는 거래 가능성 근거가 빠졌으면 해당 evidence를 보강합니다.",
            "보강된 net performance가 후보 성과 해석을 바꾸는지 확인합니다.",
        ],
        "location": "Flow4 > 실전성 > 실전 운용 현실성 상세",
    },
    "stress_robustness": {
        "checked_summary": "stress window, rolling, sensitivity, overfit warning 근거가 있는지 확인합니다.",
        "missing_summary": "stress / rolling / sensitivity / overfit 중 미실행 또는 보강 필요 항목",
        "next_action_summary": "Stress / sensitivity 상세에서 non-PASS row와 follow-up을 확인합니다.",
        "action_steps": [
            "Stress / sensitivity 상세에서 stress, rolling, sensitivity, overfit 중 non-PASS 기준을 확인합니다.",
            "민감도 또는 특정 구간 의존성이 과하면 Final Review에서 보류 근거로 남깁니다.",
            "추가 stress evidence가 필요하면 재검증 후 결과가 안정적인지 다시 확인합니다.",
        ],
        "location": "Flow4 > 강건성 > Stress / sensitivity 상세",
    },
    "selected_route_preflight": {
        "checked_summary": "Final Review 저장 전에 selected-route policy가 막을 deterministic evidence gap이 있는지 확인합니다.",
        "missing_summary": "Final Review 저장을 막는 selected-route blocker 또는 review-required gap",
        "next_action_summary": "Final Review 이동 요약의 blocker를 해소한 뒤 저장 / 이동을 다시 확인합니다.",
        "action_steps": [
            "Final Review 이동 요약에서 저장을 막는 deterministic blocker가 남아 있는지 확인합니다.",
            "blocker가 Flow4 검증 기준에서 발생했다면 해당 기준의 해결 방법을 먼저 처리합니다.",
            "blocker가 사라진 뒤 Flow 3 저장 / Final Review 이동 CTA를 다시 실행합니다.",
        ],
        "location": "Flow4 > 카테고리별 검증 결과 > Final Review 이동 요약",
    },
    "provider_investability": {
        "checked_summary": "ETF 운용사 operability, holdings, exposure, freshness가 충분한지 확인합니다.",
        "missing_summary": "ETF 운용사 snapshot, holdings, exposure, operability gap",
        "next_action_summary": "데이터 보강 / 수집 실행에서 수집 가능한 운용사 / 공식 외부 데이터 gap을 먼저 보강합니다.",
        "action_steps": [
            "데이터 보강 / 수집 실행에서 holdings, exposure, 운용사 freshness 중 수집 가능한 gap을 확인합니다.",
            "운용사 / 공식 외부 데이터 evidence를 보강한 뒤 데이터 품질 / 구성 기준의 blocker가 해소됐는지 확인합니다.",
        ],
        "location": "Flow4 > 데이터 보강 / 수집 실행",
    },
    "leverage_inverse": {
        "checked_summary": "레버리지 / 인버스 노출의 목적, 보유 기간, 손실 허용 기준이 후보 목적과 맞는지 확인합니다.",
        "missing_summary": "노출 목적, 보유 기간, 손실 허용 기준",
        "next_action_summary": "Flow4에서 레버리지 / 인버스 노출을 2단계 실용성 주의 근거로 확인합니다.",
        "action_steps": [
            "레버리지 / 인버스 노출의 목적과 보유 기간이 후보 목적과 맞는지 확인합니다.",
            "손실 허용 기준을 넘을 가능성이 있으면 2단계 실용성 주의 또는 보류 근거로 남깁니다.",
        ],
        "location": "Flow4 > 조건부 근거 > 레버리지 / 인버스 적합성",
    },
    "risk_contribution": {
        "checked_summary": "weighted mix의 component return matrix, correlation, risk contribution, drop-one dependency를 확인합니다.",
        "missing_summary": "component matrix, correlation, risk contribution, drop-one dependency 근거",
        "next_action_summary": "위험 기여 상세에서 non-PASS row를 확인하고 component risk 근거를 보강합니다.",
        "action_steps": [
            "위험 기여 상세에서 component matrix, correlation, risk contribution, drop-one 중 부족한 기준을 확인합니다.",
            "mix 성과가 특정 component 하나에 과도하게 의존하는지 근거를 보강합니다.",
            "보강 후 component risk가 후보 구성 의도를 설명하는지 다시 확인합니다.",
        ],
        "location": "Flow4 > 구성 / 리스크 > 위험 기여 상세",
    },
    "component_role_weight": {
        "checked_summary": "weighted mix의 component role, target weight, profile intent, weight rationale을 확인합니다.",
        "missing_summary": "component 역할, 비중 의도, weight rationale 근거",
        "next_action_summary": "Component 역할 / 비중 상세에서 non-PASS row를 확인하고 역할 / 비중 근거를 보강합니다.",
        "action_steps": [
            "Component 역할 / 비중 상세에서 역할 설명, target weight, profile intent, weight rationale 중 부족한 기준을 확인합니다.",
            "각 component가 왜 포함됐고 왜 그 비중인지 설명 근거를 보강합니다.",
            "보강 후 mix 구성이 후보 목적과 맞는지 2단계 실용성 주의로 확인합니다.",
        ],
        "location": "Flow4 > 구성 / 리스크 > Component 역할 / 비중 상세",
    },
    "macro_regime": {
        "checked_summary": "전술형 / 헤지형 후보의 macro regime, risk-on/off context, regime split 근거를 확인합니다.",
        "missing_summary": "macro snapshot, regime split, risk-on/off context 근거",
        "next_action_summary": "Raw Evidence의 Practical Diagnostics에서 macro / regime row를 확인하고 2단계 실용성 주의로 정리합니다.",
        "action_steps": [
            "Raw Evidence의 Practical Diagnostics에서 macro snapshot, regime split, risk-on/off context를 확인합니다.",
            "전술형 성과가 특정 regime에 과도하게 의존하면 Final Review에서 선택 리스크로 남깁니다.",
        ],
        "location": "Flow4 > Raw Evidence > Practical Diagnostics",
    },
}
MODULE_EVIDENCE_ROW_KEYS = {
    "validation_efficacy": ("validation_efficacy_display_rows", "validation_efficacy_audit.rows"),
    "data_coverage": ("data_coverage_display_rows", "data_coverage_audit.rows"),
    "construction_risk": ("construction_risk_display_rows", "construction_risk_audit.rows"),
    "backtest_realism": ("backtest_realism_display_rows", "backtest_realism_audit.rows"),
    "risk_contribution": ("risk_contribution_display_rows", "risk_contribution_audit.rows"),
    "component_role_weight": ("component_role_weight_display_rows", "component_role_weight_audit.rows"),
}
COLLECTABLE_DATA_ACTION_KEYWORDS = (
    "provider",
    "holdings",
    "exposure",
    "macro",
    "fred",
    "operability",
    "snapshot",
    "운용성",
)
COLLECTABLE_DATA_ACTIONS = {
    "data_coverage": {
        "surface": "Flow4 > 데이터 보강 / 수집 실행",
        "detail": "ETF 운용사 snapshot, holdings / exposure, macro context처럼 수집 가능한 데이터 gap만 같은 화면에서 보강합니다.",
    },
    "construction_risk": {
        "surface": "Flow4 > 데이터 보강 / 수집 실행",
        "detail": "구성 리스크 중 ETF holdings / exposure 누락처럼 수집 가능한 gap만 보강합니다.",
    },
    "provider_investability": {
        "surface": "Flow4 > 데이터 보강 / 수집 실행",
        "detail": "ETF 운용성, holdings / exposure, macro context 중 수집 가능한 외부 데이터 gap을 보강합니다.",
    },
}
DATA_ACTION_GROUPS = (
    {
        "group_id": "immediate_collect",
        "label": "지금 수집 가능",
        "description": "아래 수집 실행 버튼으로 바로 처리할 수 있는 외부 데이터 근거입니다.",
        "tone": "warning",
    },
    {
        "group_id": "source_map_discovery",
        "label": "Source map 탐색",
        "description": "ETF 공식 원천 위치를 자동으로 찾은 뒤 수집 가능 여부를 다시 확인해야 합니다.",
        "tone": "warning",
    },
    {
        "group_id": "connector_needed",
        "label": "Connector mapping 필요",
        "description": "자동 탐색 이후에도 수동 원천 connector mapping이 필요한 항목입니다.",
        "tone": "danger",
    },
    {
        "group_id": "no_action",
        "label": "현재 수집으로 해결 불가",
        "description": "데이터 수집 버튼이 아니라 재검증, 방법론 보강, 판단 단계에서 처리할 항목입니다.",
        "tone": "neutral",
    },
)
DATA_ACTION_EXCLUDED_MODULE_IDS = {"selected_route_preflight"}
DATA_ACTION_EXCLUDED_LABEL_TOKENS = ("final review", "monitoring")


def _dict_list(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, list):
        return []
    return [dict(row or {}) for row in value if isinstance(row, dict)]


def _module_id(module: dict[str, Any]) -> str:
    return str(module.get("module_id") or "").strip()


def _module_applies(module: dict[str, Any]) -> bool:
    return bool(module.get("applies", True))


def _module_requirement(module: dict[str, Any]) -> str:
    return str(module.get("requirement") or "").strip().upper()


def _module_stage_owner(module: dict[str, Any]) -> str:
    return str(module.get("stage_owner") or "").strip().lower()


def _normalize_module(
    module: dict[str, Any],
    *,
    workspace_role: str,
    evidence_rows: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    row = dict(module or {})
    row["module_id"] = _module_id(row)
    row["status"] = normalize_validation_status(row.get("status"))
    row["workspace_role"] = workspace_role
    row.update(_module_display_fields(row, evidence_rows=evidence_rows))
    row.update(review_role_fields(row))
    return row


def _ordered_modules(
    modules: list[dict[str, Any]],
    module_ids: set[str] | tuple[str, ...],
    *,
    workspace_role: str,
    evidence_rows_by_module: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    module_order = list(module_ids)
    module_id_set = set(module_order)
    order = {module_id: index for index, module_id in enumerate(module_order)}
    rows = [
        _normalize_module(
            module,
            workspace_role=workspace_role,
            evidence_rows=(evidence_rows_by_module or {}).get(_module_id(module)),
        )
        for module in modules
        if _module_id(module) in module_id_set and _module_applies(module)
    ]
    return sorted(rows, key=lambda module: order.get(_module_id(module), len(order)))


def _group(
    *,
    group_id: str,
    label: str,
    purpose: str,
    modules: list[dict[str, Any]],
) -> dict[str, Any] | None:
    if not modules:
        return None
    return {
        "group_id": group_id,
        "label": label,
        "purpose": purpose,
        "module_count": len(modules),
        "modules": modules,
    }


def _status_tone(status: Any) -> str:
    normalized = normalize_validation_status(status)
    if normalized in {"PASS", "READY"}:
        return "positive"
    if normalized == "REVIEW":
        return "warning"
    if normalized in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}:
        return "danger"
    return "neutral"


def _status_label(status: Any) -> str:
    return normalize_validation_status(status)


def _criteria_status_label(status: Any) -> str:
    normalized = normalize_validation_status(status)
    return STATUS_LABELS.get(normalized, normalized)


def _criteria_outcome(status: Any) -> dict[str, str]:
    normalized = normalize_validation_status(status)
    if normalized == "BLOCKED":
        key = "not_practical"
    elif normalized in {"NEEDS_INPUT", "NOT_RUN"}:
        key = "repair_required"
    elif normalized == "REVIEW":
        key = "review_required"
    elif normalized in {"PASS", "READY"}:
        key = "pass"
    elif normalized == "NOT_APPLICABLE":
        key = "not_applicable"
    else:
        key = "repair_required"
    text = OUTCOME_TEXT[key]
    return {
        "outcome_key": key,
        "outcome_label": text["label"],
        "outcome_detail": text["detail"],
        "outcome_tone": text["tone"],
    }


def _clean_issue_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    replacements = {
        "NEEDS_INPUT row": "보강 필요 항목",
        "NEEDS_INPUT 항목": "보강 필요 항목",
        "NOT_RUN row": "미실행 항목",
        "REVIEW row": "역할별 REVIEW 확인 항목",
    }
    for raw, replacement in replacements.items():
        text = text.replace(raw, replacement)
    return text


def _nested_rows(value: dict[str, Any], key_path: str) -> list[dict[str, Any]]:
    current: Any = value
    for key in key_path.split("."):
        if not isinstance(current, dict):
            return []
        current = current.get(key)
    return _dict_list(current)


def _module_evidence_row_map(validation: dict[str, Any]) -> dict[str, list[dict[str, Any]]]:
    rows_by_module: dict[str, list[dict[str, Any]]] = {}
    for module_id, key_paths in MODULE_EVIDENCE_ROW_KEYS.items():
        rows: list[dict[str, Any]] = []
        for key_path in key_paths:
            rows.extend(_nested_rows(validation, key_path))
        rows_by_module[module_id] = rows
    return rows_by_module


def _evidence_row_status(row: dict[str, Any]) -> str:
    return normalize_validation_status(
        row.get("Status")
        or row.get("Diagnostic Status")
        or row.get("Coverage")
        or row.get("Result Status")
        or row.get("Policy Status")
    )


def _evidence_row_label(row: dict[str, Any]) -> str:
    for key in ("Criteria", "Area", "Check", "Module", "Board", "Route"):
        text = _clean_issue_text(row.get(key))
        if text and text != "-":
            return text
    return "-"


def _evidence_row_action(row: dict[str, Any]) -> str:
    for key in ("Next Action", "Required Action", "Action", "Recommended Action"):
        text = _clean_issue_text(row.get(key))
        if text and text not in {"-", "none", "No action", "조치 없음"}:
            return text
    return ""


def _join_limited(items: list[str], *, limit: int = 4) -> str:
    clean = []
    for item in items:
        text = _clean_issue_text(item)
        if text and text not in clean and text != "-":
            clean.append(text)
    if not clean:
        return ""
    visible = clean[:limit]
    suffix = f" 외 {len(clean) - limit}개" if len(clean) > limit else ""
    return " / ".join(visible) + suffix


def _clean_limited_items(items: list[str], *, limit: int = 4) -> list[str]:
    clean: list[str] = []
    for item in items:
        text = _clean_issue_text(item)
        if text and text not in clean and text != "-":
            clean.append(text)
    return clean[:limit]


def _merge_action_steps(*groups: list[str], limit: int = 4) -> list[str]:
    steps: list[str] = []
    for group in groups:
        for item in group:
            text = _clean_issue_text(item)
            if text and text not in steps and text != "-":
                steps.append(text)
            if len(steps) >= limit:
                return steps
    return steps


def _string_list(value: Any) -> list[str]:
    if value is None:
        return []
    if isinstance(value, str):
        raw_items = [value]
    elif isinstance(value, (list, tuple, set)):
        raw_items = list(value)
    else:
        raw_items = [value]
    items: list[str] = []
    for item in raw_items:
        text = str(item or "").strip().upper()
        if text and text != "-" and text not in items:
            items.append(text)
    return items


def _provider_gap_plan_for_board(validation: dict[str, Any]) -> dict[str, Any]:
    plan = dict(validation.get("provider_gap_collection_plan") or {})
    if plan:
        return {
            "operability_official": _string_list(plan.get("operability_official")),
            "operability_bridge": _string_list(plan.get("operability_bridge")),
            "holdings_exposure": _string_list(plan.get("holdings_exposure")),
            "source_map_discovery": _string_list(plan.get("source_map_discovery")),
            "mapping_needed": _string_list(plan.get("mapping_needed")),
            "macro": bool(plan.get("macro")),
        }

    provider_context = dict(validation.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    operability_missing = _string_list(dict(coverage.get("operability") or {}).get("missing_symbols"))
    holdings_missing = _string_list(dict(coverage.get("holdings") or {}).get("missing_symbols"))
    exposure_missing = _string_list(dict(coverage.get("exposure") or {}).get("missing_symbols"))
    macro = dict(coverage.get("macro") or {})
    macro_needs_collection = str(macro.get("diagnostic_status") or "").upper() in {"NOT_RUN", "REVIEW"} and (
        int(macro.get("series_count") or 0) < 3 or int(macro.get("stale_count") or 0) > 0
    )
    return {
        "operability_official": [],
        "operability_bridge": operability_missing,
        "holdings_exposure": [],
        "source_map_discovery": sorted(set(holdings_missing) | set(exposure_missing)),
        "mapping_needed": [],
        "macro": macro_needs_collection,
    }


def _data_action_item(
    *,
    group_id: str,
    category: str,
    tickers: list[str] | None = None,
    reason: str,
    next_action: str,
    availability: str,
    module_id: str = "",
    source: str = "",
    target_anchor: str = "pv-provider-data-action",
) -> dict[str, Any]:
    return {
        "group_id": group_id,
        "module_id": module_id,
        "category": category,
        "tickers": list(tickers or []),
        "reason": reason,
        "next_action": next_action,
        "availability": availability,
        "source": source,
        "target_anchor": target_anchor,
    }


def _data_action_items_from_plan(plan: dict[str, Any]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    if plan.get("operability_official"):
        items.append(
            _data_action_item(
                group_id="immediate_collect",
                category="ETF operability",
                tickers=_string_list(plan.get("operability_official")),
                reason="공식 source map 또는 내장 공식 source로 운용성 snapshot을 보강할 수 있습니다.",
                next_action="아래 수집 실행에서 운용성 데이터를 수집합니다.",
                availability="기존 Python 수집 경계에서 실행 가능",
                source="provider_gap_collection_plan.operability_official",
            )
        )
    if plan.get("operability_bridge"):
        items.append(
            _data_action_item(
                group_id="immediate_collect",
                category="ETF operability",
                tickers=_string_list(plan.get("operability_bridge")),
                reason="공식 source가 없거나 부족해도 DB bridge로 운용성 근거를 보강할 수 있습니다.",
                next_action="아래 수집 실행에서 DB bridge 보강을 실행합니다.",
                availability="기존 Python 수집 경계에서 실행 가능",
                source="provider_gap_collection_plan.operability_bridge",
            )
        )
    if plan.get("holdings_exposure"):
        items.append(
            _data_action_item(
                group_id="immediate_collect",
                category="ETF holdings / exposure",
                tickers=_string_list(plan.get("holdings_exposure")),
                reason="검증된 holdings 또는 exposure source가 있어 look-through 근거를 보강할 수 있습니다.",
                next_action="아래 수집 실행에서 holdings / exposure를 수집합니다.",
                availability="기존 Python 수집 경계에서 실행 가능",
                source="provider_gap_collection_plan.holdings_exposure",
            )
        )
    if plan.get("macro"):
        items.append(
            _data_action_item(
                group_id="immediate_collect",
                category="Macro context",
                tickers=["VIXCLS", "T10Y3M", "BAA10Y"],
                reason="저장된 macro context series가 부족하거나 오래되어 FRED series 보강이 필요합니다.",
                next_action="아래 수집 실행에서 macro context를 수집합니다.",
                availability="기존 Python 수집 경계에서 실행 가능",
                source="provider_gap_collection_plan.macro",
            )
        )
    if plan.get("source_map_discovery"):
        items.append(
            _data_action_item(
                group_id="source_map_discovery",
                category="ETF holdings / exposure",
                tickers=_string_list(plan.get("source_map_discovery")),
                reason="holdings / exposure 수집 전 verified source map을 먼저 찾아야 합니다.",
                next_action="자동 source map 탐색을 실행한 뒤 같은 Flow 4 보강 액션을 다시 확인합니다.",
                availability="자동 탐색 후 수집 가능 여부 재확인",
                source="provider_gap_collection_plan.source_map_discovery",
            )
        )
    if plan.get("mapping_needed"):
        items.append(
            _data_action_item(
                group_id="connector_needed",
                category="ETF holdings / exposure",
                tickers=_string_list(plan.get("mapping_needed")),
                reason="자동 탐색 이후에도 검증된 issuer URL / parser mapping이 없습니다.",
                next_action="수동 connector mapping을 추가한 뒤 외부 데이터 보강을 다시 실행합니다.",
                availability="수동 connector mapping 필요",
                source="provider_gap_collection_plan.mapping_needed",
            )
        )
    return items


def _row_tickers(row: dict[str, Any]) -> list[str]:
    for key in ("Ticker", "ETF", "Symbol", "Symbols", "Tickers", "symbol", "symbols"):
        tickers = _string_list(row.get(key))
        if tickers:
            return tickers
    return []


def _data_action_no_action_items(
    modules: list[dict[str, Any]],
    evidence_rows_by_module: dict[str, list[dict[str, Any]]],
) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for module in modules:
        if not _module_applies(module):
            continue
        module_id = _module_id(module)
        if module_id in DATA_ACTION_EXCLUDED_MODULE_IDS:
            continue
        label_text = f"{module.get('label') or ''} {module.get('group') or ''}".lower()
        if any(token in label_text for token in DATA_ACTION_EXCLUDED_LABEL_TOKENS):
            continue
        stage_key = _stage_owner_key(module)
        requirement = _module_requirement(module)
        if stage_key in DOWNSTREAM_STAGE_OWNERS or requirement == "REFERENCE":
            continue
        status = normalize_validation_status(module.get("status"))
        if status in {"PASS", "READY", "REVIEW", "NOT_APPLICABLE"}:
            continue
        evidence_rows = list(evidence_rows_by_module.get(module_id) or [])
        actionable_rows = 0
        non_action_rows = 0
        for row in evidence_rows:
            row_status = _evidence_row_status(row)
            if row_status in {"PASS", "READY", "REVIEW", "NOT_APPLICABLE"}:
                continue
            if _row_mentions_collectable_data_action(row):
                actionable_rows += 1
                continue
            non_action_rows += 1
            items.append(
                _data_action_item(
                    group_id="no_action",
                    module_id=module_id,
                    category=str(module.get("label") or module_id or "-"),
                    tickers=_row_tickers(row),
                    reason=_evidence_row_label(row),
                    next_action=_evidence_row_action(row)
                    or str(module.get("resolution_action") or module.get("next_action") or "해당 기준 상세에서 보강한 뒤 Flow 2 재검증을 실행합니다."),
                    availability="현재 Provider / Data 수집 버튼으로 직접 해결되지 않음",
                    source=f"{module_id}.evidence_rows",
                    target_anchor="",
                )
            )
        if evidence_rows and (actionable_rows or non_action_rows):
            continue
        if not evidence_rows:
            collection_action = _collection_action(module_id, status, [])
            if collection_action.get("available"):
                continue
            items.append(
                _data_action_item(
                    group_id="no_action",
                    module_id=module_id,
                    category=str(module.get("label") or module_id or "-"),
                    tickers=[],
                    reason=_clean_issue_text(module.get("gate_reason") or module.get("reason") or module.get("evidence"))
                    or "현재 기준에 보강 필요 상태가 남아 있습니다.",
                    next_action=_clean_issue_text(module.get("resolution_action") or module.get("next_action"))
                    or "해당 기준 상세에서 보강한 뒤 Flow 2 재검증을 실행합니다.",
                    availability="현재 Provider / Data 수집 버튼으로 직접 해결되지 않음",
                    source=f"{module_id}.module_status",
                    target_anchor="",
                )
            )
    return items


def _data_action_board(
    validation: dict[str, Any],
    modules: list[dict[str, Any]],
    evidence_rows_by_module: dict[str, list[dict[str, Any]]],
) -> dict[str, Any]:
    plan = _provider_gap_plan_for_board(validation)
    items = _data_action_items_from_plan(plan)
    items.extend(_data_action_no_action_items(modules, evidence_rows_by_module))
    grouped_items = {spec["group_id"]: [] for spec in DATA_ACTION_GROUPS}
    for item in items:
        group_id = str(item.get("group_id") or "no_action")
        grouped_items.setdefault(group_id, []).append(item)
    groups: list[dict[str, Any]] = []
    for spec in DATA_ACTION_GROUPS:
        group_id = str(spec["group_id"])
        group_items = list(grouped_items.get(group_id) or [])
        groups.append(
            {
                "group_id": group_id,
                "label": spec["label"],
                "description": spec["description"],
                "tone": spec["tone"],
                "count": len(group_items),
                "items": group_items,
            }
        )
    summary = {f"{group['group_id']}_count": int(group["count"]) for group in groups}
    summary["actionable_count"] = (
        summary.get("immediate_collect_count", 0)
        + summary.get("source_map_discovery_count", 0)
        + summary.get("connector_needed_count", 0)
    )
    summary["item_count"] = len(items)
    return {
        "title": "데이터 보강 대상",
        "detail": "수집 실행 전에 지금 보강할 수 있는 데이터 항목과 현재 수집으로 해결되지 않는 항목을 분리합니다.",
        "summary": summary,
        "groups": groups,
        "items": items,
    }


def _non_pass_row_summary(evidence_rows: list[dict[str, Any]]) -> dict[str, Any]:
    missing: list[str] = []
    actions: list[str] = []
    review: list[str] = []
    for row in evidence_rows:
        status = _evidence_row_status(row)
        if status in {"PASS", "READY", "NOT_APPLICABLE"}:
            continue
        label = _evidence_row_label(row)
        if status == "REVIEW":
            review.append(label)
        else:
            missing.append(label)
        action = _evidence_row_action(row)
        if action:
            actions.append(action)
    return {
        "missing": _join_limited(missing),
        "review": _join_limited(review),
        "actions": _join_limited(actions, limit=3),
        "missing_items": _clean_limited_items(missing),
        "review_items": _clean_limited_items(review),
        "action_items": _clean_limited_items(actions, limit=3),
    }


def _empty_collection_action() -> dict[str, Any]:
    return {
        "available": False,
        "label": "",
        "surface": "",
        "detail": "",
        "target_anchor": "",
    }


def _row_mentions_collectable_data_action(row: dict[str, Any]) -> bool:
    status = _evidence_row_status(row)
    if status in {"PASS", "READY", "NOT_APPLICABLE"}:
        return False
    text = " ".join(
        _clean_issue_text(row.get(key))
        for key in ("Criteria", "Evidence", "Next Action", "Required Action", "Action", "Meaning")
    ).lower()
    return any(keyword in text for keyword in COLLECTABLE_DATA_ACTION_KEYWORDS)


def _collection_action(module_id: str, status: str, evidence_rows: list[dict[str, Any]]) -> dict[str, Any]:
    if status in {"PASS", "READY", "NOT_APPLICABLE", "REVIEW"}:
        return _empty_collection_action()
    spec = COLLECTABLE_DATA_ACTIONS.get(module_id)
    if not spec:
        return _empty_collection_action()
    if module_id in {"data_coverage", "construction_risk"} and not any(
        _row_mentions_collectable_data_action(row) for row in evidence_rows
    ):
        return _empty_collection_action()
    return {
        "available": True,
        "label": "수집하기",
        "surface": spec["surface"],
        "detail": f"수집 가능한 항목만 실행합니다. {spec['detail']}",
        "target_anchor": "pv-provider-data-action",
    }


def _resolution_guide(
    module: dict[str, Any],
    *,
    status: str,
    checked_summary: str,
    missing_summary: str,
    next_action: str,
    pass_criteria: str,
    fix_location: str,
    evidence_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    module_id = str(module.get("module_id") or "").strip()
    guide = dict(MODULE_RESOLUTION_GUIDES.get(module_id) or {})
    row_summary = _non_pass_row_summary(evidence_rows)
    collection_action = _collection_action(module_id, status, evidence_rows)

    checked = guide.get("checked_summary") or checked_summary
    missing = row_summary.get("missing") or row_summary.get("review") or guide.get("missing_summary") or missing_summary
    action = row_summary.get("actions") or guide.get("next_action_summary") or next_action
    location = guide.get("location") or fix_location
    action_location = guide.get("action_location") or ""
    configured_action_steps = [
        str(item).strip()
        for item in list(guide.get("action_steps") or [])
        if str(item).strip()
    ]
    row_action_steps = list(row_summary.get("action_items") or [])

    if status in {"PASS", "READY"}:
        guide_type = "evidence"
        issue_label = "현재 상태"
        action_label = "다음 행동"
        outcome_label = "통과 기준"
        location_label = "위치"
        missing = "현재 기준에서 부족한 항목은 없습니다."
        action = "추가 보강 없이 다음 단계 참고 근거로 사용할 수 있습니다."
        action_steps = [action]
        pass_criteria = pass_criteria or "현재 기준이 통과 상태입니다."
    elif status == "REVIEW":
        role = review_role_fields(module)
        guide_type = "review"
        issue_label = "확인할 항목"
        action_label = "확인 방법"
        outcome_label = "완료 기준"
        location_label = "확인 위치"
        missing = row_summary.get("review") or missing
        action = (
            row_summary.get("actions")
            or action
            or f"{role['stage_decision_surface']}에서 {role['review_role_label']} 항목을 확인합니다."
        )
        action_steps = _merge_action_steps(
            row_action_steps,
            configured_action_steps,
            [action or f"{role['stage_decision_surface']}에서 {role['review_role_label']} 항목을 확인합니다."],
        )
        pass_criteria = pass_criteria.replace("Final Review 확인 상태", role["review_role_label"])
        pass_criteria = pass_criteria.replace("해당 REVIEW 역할 확인 상태", role["review_role_label"])
        pass_criteria = pass_criteria or f"{role['review_role_label']}로 확인할 근거와 판단 사유가 남아 있어야 합니다."
    elif status == "NOT_APPLICABLE":
        guide_type = "none"
        issue_label = "적용 여부"
        action_label = "다음 행동"
        outcome_label = "완료 기준"
        location_label = "위치"
        missing = "현재 후보에는 적용되지 않는 기준입니다."
        action = "별도 보강이 필요하지 않습니다."
        action_steps = [action]
        pass_criteria = "현재 후보에는 적용되지 않는 기준입니다."
    else:
        guide_type = "fix"
        issue_label = "해결해야 할 항목"
        action_label = "해결 방법"
        outcome_label = "통과 기준"
        location_label = "위치"
        action_steps = _merge_action_steps(row_action_steps, configured_action_steps, [action])
        pass_criteria = pass_criteria or "필수 기준이 PASS 또는 해당 REVIEW 역할 확인 상태가 되어야 합니다."

    if action_steps:
        action = action_steps[0]

    if action_location and action_location not in location:
        location = f"{location} / 실행: {action_location}"

    return {
        "type": guide_type,
        "checked_label": "검증한 것",
        "checked": checked or "-",
        "issue_label": issue_label,
        "missing": missing or "-",
        "action_label": action_label,
        "next_action": action or "-",
        "action_steps": action_steps,
        "outcome_label": outcome_label,
        "pass_criteria": pass_criteria or "-",
        "location_label": location_label,
        "location": location or "-",
        "action_location": action_location,
        "collection_action": collection_action,
    }


def _module_display_fields(module: dict[str, Any], evidence_rows: list[dict[str, Any]] | None = None) -> dict[str, Any]:
    module_id = str(module.get("module_id") or "").strip()
    label = str(module.get("label") or module_id or "-").strip()
    status = normalize_validation_status(module.get("status"))
    reading = dict(MODULE_DISPLAY_TEXT.get(module_id) or MODULE_DISPLAY_TEXT.get(label) or {})
    reason = str(module.get("reason") or module.get("profile_effect") or "").strip()
    evidence = _clean_issue_text(module.get("gate_reason") or module.get("evidence") or module.get("next_action") or "")
    action = _clean_issue_text(module.get("resolution_action") or module.get("next_action") or "")
    current_problem = (
        reading.get("current_problem")
        or evidence
        or reason
        or "현재 기준에서 Final Review 이동 전에 정리할 이슈가 있습니다."
    )
    completion_criteria = (
        reading.get("completion_criteria")
        or action
        or f"{label} 기준이 PASS 또는 해당 REVIEW 역할 확인 상태가 되어야 합니다."
    )
    if status in {"PASS", "READY"}:
        current_problem = "현재 기준에서 Final Review 이동을 즉시 막는 문제는 없습니다."
        completion_criteria = f"{label} 기준이 통과 상태입니다."
    outcome = _criteria_outcome(status)
    fix_location = reading.get("fix_location") or module.get("resolution_surface") or "Flow 4 기준 상세"
    impact_summary = (
        reading.get("impact_summary")
        or "이 기준이 해결되지 않으면 Final Review 이동 또는 저장 단계에서 다시 보류될 수 있습니다."
    )
    resolution_guide = _resolution_guide(
        module,
        status=status,
        checked_summary=reason or current_problem,
        missing_summary=evidence or current_problem,
        next_action=action or completion_criteria,
        pass_criteria=completion_criteria,
        fix_location=fix_location,
        evidence_rows=list(evidence_rows or []),
    )
    return {
        "display_label": reading.get("display_label") or label,
        "issue_title": reading.get("issue_title") or reading.get("display_label") or label,
        "status_label": _criteria_status_label(status),
        "technical_status": status,
        "technical_label": f"{label} · {status}",
        **outcome,
        "current_problem": current_problem,
        "completion_criteria": completion_criteria,
        "fix_location": fix_location,
        "impact_summary": impact_summary,
        "checked_evidence": current_problem,
        "missing_evidence": current_problem,
        "action_label": completion_criteria,
        "why_it_matters": impact_summary,
        "resolution_guide": resolution_guide,
        "checked_summary": resolution_guide.get("checked"),
        "missing_summary": resolution_guide.get("missing"),
        "next_action_summary": resolution_guide.get("next_action"),
        "pass_criteria_summary": resolution_guide.get("pass_criteria"),
        "location_summary": resolution_guide.get("location"),
    }


def _group_status(modules: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for module in modules:
        status = _criteria_status_label(module.get("status") or "NOT_RUN")
        counts[status] = counts.get(status, 0) + 1
    if not counts:
        return "-"
    return " / ".join(f"{status} {count}" for status, count in sorted(counts.items()))


def _group_tone(modules: list[dict[str, Any]]) -> str:
    statuses = {normalize_validation_status(module.get("status")) for module in modules}
    if statuses & {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}:
        return "danger"
    if "REVIEW" in statuses:
        return "warning"
    return "positive"


def _criteria_card(module: dict[str, Any]) -> dict[str, Any]:
    status = _status_label(module.get("status") or "NOT_RUN")
    outcome = _criteria_outcome(status)
    role_fields = review_role_fields(module)
    status_label = module.get("status_label") or _criteria_status_label(status)
    outcome_label = module.get("outcome_label") or outcome["outcome_label"]
    outcome_detail = module.get("outcome_detail") or outcome["outcome_detail"]
    if status == "REVIEW":
        status_label = role_fields["review_role_label"]
        outcome_label = role_fields["review_role_label"]
        outcome_detail = f"{role_fields['stage_decision_surface']}에서 확인할 주의 항목입니다."
    evidence = (
        module.get("gate_reason")
        or module.get("evidence")
        or module.get("reason")
        or module.get("next_action")
        or "-"
    )
    explanation = module.get("reason") or module.get("profile_effect") or "-"
    current_problem = module.get("current_problem") or evidence
    completion_criteria = module.get("completion_criteria") or module.get("resolution_action") or "-"
    resolution_guide = dict(module.get("resolution_guide") or {})
    return {
        "module_id": module.get("module_id") or "-",
        "label": module.get("label") or module.get("module_id") or "-",
        "display_label": module.get("display_label") or module.get("label") or module.get("module_id") or "-",
        "status": status,
        "status_label": status_label,
        "technical_status": module.get("technical_status") or status,
        "technical_label": module.get("technical_label") or f"{module.get('label') or module.get('module_id') or '-'} · {status}",
        "outcome_key": module.get("outcome_key") or outcome["outcome_key"],
        "outcome_label": outcome_label,
        "outcome_detail": outcome_detail,
        "outcome_tone": module.get("outcome_tone") or outcome["outcome_tone"],
        "tone": _status_tone(status),
        **role_fields,
        "explanation": explanation,
        "evidence": evidence,
        "issue_title": module.get("issue_title") or module.get("display_label") or module.get("label") or "-",
        "current_problem": current_problem,
        "completion_criteria": completion_criteria,
        "fix_location": module.get("fix_location") or module.get("resolution_surface") or "-",
        "impact_summary": module.get("impact_summary") or "Final Review 이동 가능 여부 판단에 사용됩니다.",
        "checked_evidence": module.get("checked_evidence") or current_problem,
        "missing_evidence": module.get("missing_evidence") or current_problem,
        "action_label": module.get("action_label") or completion_criteria,
        "why_it_matters": module.get("why_it_matters") or "이 기준은 Final Review 이동 가능 여부 판단에 사용됩니다.",
        "gate_effect": module.get("gate_effect") or "-",
        "resolution_surface": module.get("resolution_surface") or "-",
        "resolution_action": module.get("resolution_action") or module.get("next_action") or "-",
        "module_type": module.get("module_type") or module.get("requirement") or "-",
        "resolution_guide": resolution_guide,
        "checked_summary": resolution_guide.get("checked") or module.get("checked_summary") or current_problem,
        "missing_summary": resolution_guide.get("missing") or module.get("missing_summary") or current_problem,
        "next_action_summary": resolution_guide.get("next_action") or module.get("next_action_summary") or completion_criteria,
        "pass_criteria_summary": resolution_guide.get("pass_criteria") or module.get("pass_criteria_summary") or completion_criteria,
        "location_summary": resolution_guide.get("location") or module.get("location_summary") or module.get("fix_location") or "-",
    }


def _criteria_group_summary(cards: list[dict[str, Any]]) -> dict[str, Any]:
    passed = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") in {"PASS", "READY"}
    ]
    remaining = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
    ]
    repair = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") in {"NEEDS_INPUT", "NOT_RUN"}
    ]
    not_practical = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "BLOCKED"
    ]
    review = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "REVIEW"
    ]
    pv_data_caution = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "REVIEW" and card.get("review_role") == "pv_data_caution"
    ]
    pv_practical_caution = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "REVIEW" and card.get("review_role") == "pv_practical_caution"
    ]
    final_review_reference = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "REVIEW" and card.get("review_role") == "final_decision_input"
    ]
    monitoring_followup = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "REVIEW" and card.get("review_role") == "monitoring_followup"
    ]
    if not_practical:
        decision = f"현재 상태로 실전 사용이 어려운 기준 {len(not_practical)}개가 있습니다."
    elif repair:
        decision = f"보강 필요: 재검증할 기준 {len(repair)}개가 남아 있습니다."
    elif pv_practical_caution:
        decision = f"실용성 판단에서 주의할 REVIEW 기준 {len(pv_practical_caution)}개가 있습니다."
    elif pv_data_caution:
        decision = f"데이터 / 기본 검증에서 주의할 REVIEW 기준 {len(pv_data_caution)}개가 있습니다."
    elif final_review_reference:
        decision = f"최종 판단 메모에서 참고할 기준 {len(final_review_reference)}개가 있습니다."
    elif monitoring_followup:
        decision = f"Monitoring에서 추적할 기준 {len(monitoring_followup)}개가 있습니다."
    elif review:
        decision = f"역할 확인이 필요한 REVIEW 기준 {len(review)}개가 있습니다."
    else:
        decision = "이 기준 그룹은 현재 통과 상태입니다."
    if not_practical:
        display_status = f"실전 사용 어려움 {len(not_practical)}"
    elif repair:
        display_status = f"보강 필요 {len(repair)}"
    elif pv_practical_caution:
        display_status = f"2단계 실용성 주의 {len(pv_practical_caution)}"
    elif pv_data_caution:
        display_status = f"데이터 주의 {len(pv_data_caution)}"
    elif final_review_reference:
        display_status = f"최종 판단 참고 {len(final_review_reference)}"
    elif monitoring_followup:
        display_status = f"Monitoring 추적 {len(monitoring_followup)}"
    elif review:
        display_status = f"REVIEW {len(review)}"
    elif passed:
        display_status = f"통과 {len(passed)}"
    else:
        display_status = "비적용"
    visible_in_practical_validation = bool(passed or remaining or pv_data_caution or pv_practical_caution)
    return {
        "passed_criteria": passed,
        "remaining_issues": remaining,
        "repair_criteria": repair,
        "not_practical_criteria": not_practical,
        "review_criteria": review,
        "pv_data_caution_criteria": pv_data_caution,
        "pv_practical_caution_criteria": pv_practical_caution,
        "final_review_reference_criteria": final_review_reference,
        "monitoring_followup_criteria": monitoring_followup,
        "pv_data_caution_count": len(pv_data_caution),
        "pv_practical_caution_count": len(pv_practical_caution),
        "final_review_reference_count": len(final_review_reference),
        "monitoring_followup_count": len(monitoring_followup),
        "visible_in_practical_validation": visible_in_practical_validation,
        "display_status": display_status,
        "decision_summary": decision,
    }


def _overall_outcome_summary(summary: dict[str, int]) -> dict[str, Any]:
    not_practical_count = int(summary.get("criteria_not_practical_count") or 0)
    repair_count = int(summary.get("criteria_repair_count") or 0)
    if not_practical_count:
        key = "not_practical"
        count = not_practical_count
    elif repair_count:
        key = "repair_required"
        count = repair_count
    else:
        key = "pass"
        count = int(summary.get("criteria_pass_count") or 0)
    text = OUTCOME_TEXT[key]
    return {
        "overall_outcome_key": key,
        "overall_outcome_label": text["label"],
        "overall_outcome_detail": text["detail"],
        "overall_outcome_headline": text["headline"],
        "overall_outcome_tone": text["tone"],
        "overall_outcome_count": count,
    }


def _criteria_detail_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    detail_groups: list[dict[str, Any]] = []
    for group in groups:
        modules = [dict(module or {}) for module in list(group.get("modules") or [])]
        cards = [_criteria_card(module) for module in modules if module]
        if not cards:
            continue
        group_id = str(group.get("group_id") or "").strip()
        display = GROUP_DISPLAY_TEXT.get(group_id, {})
        summary = _criteria_group_summary(cards)
        detail_groups.append(
            {
                "group_id": group_id or "-",
                "label": group.get("label") or group.get("group_id") or "-",
                "display_label": display.get("display_label") or group.get("label") or group.get("group_id") or "-",
                "purpose": display.get("purpose") or group.get("purpose") or f"{len(cards)} criteria",
                "status": _group_status(modules),
                "tone": _group_tone(modules),
                "module_count": len(cards),
                "criteria_cards": cards,
                **summary,
            }
        )
    return detail_groups


def _visible_criteria_detail_groups(groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        dict(group or {})
        for group in groups
        if dict(group or {}).get("visible_in_practical_validation", True)
    ]


def _criteria_summary(groups: list[dict[str, Any]]) -> dict[str, Any]:
    cards = [
        dict(card or {})
        for group in groups
        for card in list(group.get("criteria_cards") or [])
        if isinstance(card, dict)
    ]
    repair_count = len([card for card in cards if card.get("status") in {"NEEDS_INPUT", "NOT_RUN"}])
    not_practical_count = len([card for card in cards if card.get("status") == "BLOCKED"])
    summary = {
        "criteria_group_count": len(groups),
        "criteria_card_count": len(cards),
        "criteria_pass_count": len([card for card in cards if card.get("status") in {"PASS", "READY"}]),
        "criteria_review_count": len([card for card in cards if card.get("status") == "REVIEW"]),
        "pv_data_caution_count": len(
            [
                card
                for card in cards
                if card.get("status") == "REVIEW" and card.get("review_role") == "pv_data_caution"
            ]
        ),
        "pv_practical_caution_count": len(
            [
                card
                for card in cards
                if card.get("status") == "REVIEW" and card.get("review_role") == "pv_practical_caution"
            ]
        ),
        "final_review_reference_count": len(
            [
                card
                for card in cards
                if card.get("status") == "REVIEW" and card.get("review_role") == "final_decision_input"
            ]
        ),
        "monitoring_followup_count": len(
            [
                card
                for card in cards
                if card.get("status") == "REVIEW" and card.get("review_role") == "monitoring_followup"
            ]
        ),
        "criteria_repair_count": repair_count,
        "criteria_not_practical_count": not_practical_count,
        "criteria_blocker_count": len(
            [
                card
                for card in cards
                if card.get("status") in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
            ]
        ),
    }
    return {**summary, **_overall_outcome_summary(summary)}


def _stage_owner_key(module: dict[str, Any]) -> str:
    owner = _module_stage_owner(module)
    if owner in STAGE_OWNER_LABELS:
        return owner
    return "practical_validation"


def _stage_visibility_label(stage_key: str, status: str, requirement: str) -> str:
    if stage_key in DOWNSTREAM_STAGE_OWNERS:
        return "후속 단계 판단"
    if status in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"} and requirement != "REFERENCE":
        return "현재 단계 보강"
    return "현재 단계 근거"


def _stage_ownership_inventory(modules: list[dict[str, Any]]) -> dict[str, Any]:
    rows: list[dict[str, Any]] = []
    for module in modules:
        if not _module_applies(module):
            continue
        stage_key = _stage_owner_key(module)
        status = normalize_validation_status(module.get("status"))
        requirement = _module_requirement(module) or str(module.get("requirement") or "-").upper()
        rows.append(
            {
                "module_id": _module_id(module),
                "label": module.get("label") or _module_id(module) or "-",
                "stage_key": stage_key,
                "stage": STAGE_OWNER_LABELS[stage_key],
                "requirement": requirement or "-",
                "status": status,
                "visibility": _stage_visibility_label(stage_key, status, requirement),
                "surface": module.get("resolution_surface") or module.get("stage_owner") or "-",
            }
        )

    stage_summaries: list[dict[str, Any]] = []
    for stage_key in STAGE_OWNER_ORDER:
        stage_rows = [row for row in rows if row["stage_key"] == stage_key]
        blocking_count = len(
            [
                row
                for row in stage_rows
                if row["status"] in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
                and row["requirement"] != "REFERENCE"
            ]
        )
        stage_summaries.append(
            {
                "stage_key": stage_key,
                "stage": STAGE_OWNER_LABELS[stage_key],
                "module_count": len(stage_rows),
                "required_count": len([row for row in stage_rows if row["requirement"] == "REQUIRED"]),
                "conditional_count": len([row for row in stage_rows if row["requirement"] == "CONDITIONAL"]),
                "reference_count": len([row for row in stage_rows if row["requirement"] == "REFERENCE"]),
                "blocking_count": blocking_count,
            }
        )

    misplaced_downstream_blocker_count = len(
        [
            row
            for row in rows
            if row["stage_key"] in DOWNSTREAM_STAGE_OWNERS
            and row["status"] in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
            and row["requirement"] != "REFERENCE"
        ]
    )
    return {
        "stage_summaries": stage_summaries,
        "rows": rows,
        "misplaced_downstream_blocker_count": misplaced_downstream_blocker_count,
    }


def _category_result_groups(
    modules: list[dict[str, Any]],
    evidence_rows_by_module: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for spec in FLOW4_CATEGORY_GROUP_SPECS:
        category_modules = _ordered_modules(
            modules,
            tuple(spec.get("module_ids") or ()),
            workspace_role="validation_category",
            evidence_rows_by_module=evidence_rows_by_module,
        )
        group = _group(
            group_id=str(spec.get("group_id") or ""),
            label=str(spec.get("label") or ""),
            purpose=str(spec.get("purpose") or ""),
            modules=category_modules,
        )
        if group is not None:
            groups.append(group)
    return groups


def _fallback_fix_queue(
    modules: list[dict[str, Any]],
    evidence_rows_by_module: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for module in modules:
        status = normalize_validation_status(module.get("status"))
        gate_effect = str(module.get("gate_effect") or "")
        if status in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"} or gate_effect == "Blocks Final Review":
            rows.append(
                _normalize_module(
                    module,
                    workspace_role="fix_queue",
                    evidence_rows=(evidence_rows_by_module or {}).get(_module_id(module)),
                )
            )
    return rows


def _fix_queue(
    validation: dict[str, Any],
    modules: list[dict[str, Any]],
    evidence_rows_by_module: dict[str, list[dict[str, Any]]] | None = None,
) -> list[dict[str, Any]]:
    gate = dict(validation.get("final_review_gate") or {})
    blocking_rows = _dict_list(gate.get("blocking_modules"))
    if blocking_rows:
        module_by_id = {_module_id(module): module for module in modules}
        merged_rows: list[dict[str, Any]] = []
        for row in blocking_rows:
            module_id = _module_id(row)
            merged = {**dict(module_by_id.get(module_id) or {}), **row}
            merged_rows.append(
                _normalize_module(
                    merged,
                    workspace_role="fix_queue",
                    evidence_rows=(evidence_rows_by_module or {}).get(module_id),
                )
            )
        return merged_rows
    return _fallback_fix_queue(modules, evidence_rows_by_module=evidence_rows_by_module)


def _next_stage_action(gate: dict[str, Any], *, blocker_count: int, caution_count: int = 0) -> dict[str, Any]:
    can_save_and_move = bool(gate.get("can_save_and_move"))
    route = str(gate.get("route") or "").strip().upper()
    ready_with_review = can_save_and_move and (
        route == "READY_WITH_REVIEW" or bool(gate.get("review_modules")) or int(caution_count or 0) > 0
    )
    disabled_reason = (
        ""
        if can_save_and_move
        else "Flow4에서 보강 항목을 확인하고 Flow2 재검증을 다시 실행한 뒤 Final Review로 이동할 수 있습니다."
    )
    if ready_with_review:
        status_label = "주의 포함 이동 가능"
        primary_detail = (
            "검증 결과와 REVIEW 주의 신호를 저장하고 Final Review에서 수익성, 벤치마크, 후보 비교, "
            "모니터링 후보 선정 판단을 이어갑니다."
        )
    elif can_save_and_move:
        status_label = "이동 가능"
        primary_detail = "검증 결과를 저장하고 Final Review에서 수익성, 벤치마크, 후보 비교, 모니터링 후보 선정 판단을 이어갑니다."
    else:
        status_label = "보강 필요"
        primary_detail = disabled_reason
    return {
        "target_stage": "Final Review",
        "status_label": status_label,
        "blocker_count": int(blocker_count),
        "disabled_reason": disabled_reason,
        "primary_action": {
            "id": "save_and_move",
            "label": "저장하고 Final Review로 이동",
            "detail": primary_detail,
            "enabled": can_save_and_move,
            "tone": "positive" if can_save_and_move else "danger",
        },
        "secondary_action": {
            "id": "save_audit_only",
            "label": "검증 결과 저장(기록용)",
            "detail": "audit trail만 남깁니다. Gate 미통과 row는 Final Review 후보 목록에 노출되지 않습니다.",
            "enabled": True,
            "tone": "neutral",
        },
        "boundary_note": (
            "Final Review 이동은 최종 승인, 투자 추천, live approval, broker order, auto rebalance가 아닙니다. "
            "Final Review에서 수익성, 벤치마크, 후보 비교, 모니터링 후보 선정 가능 여부를 판단합니다."
        ),
        "side_effects": {
            "react_executes_storage": False,
            "react_executes_handoff": False,
            "python_executes_storage": True,
            "python_executes_handoff": True,
            "validation_gate_calculation": "existing_python_service",
        },
    }


def build_practical_validation_workspace(validation: dict[str, Any]) -> dict[str, Any]:
    """Build a screen-oriented Practical Validation workspace model from validation evidence."""

    validation_row = dict(validation or {})
    modules = _dict_list(validation_row.get("validation_modules"))
    gate = dict(validation_row.get("final_review_gate") or {})
    evidence_rows_by_module = _module_evidence_row_map(validation_row)

    source_readiness = _ordered_modules(
        modules,
        SOURCE_READINESS_MODULE_IDS,
        workspace_role="core_evidence",
        evidence_rows_by_module=evidence_rows_by_module,
    )
    validation_readiness = _ordered_modules(
        modules,
        VALIDATION_READINESS_MODULE_IDS,
        workspace_role="core_evidence",
        evidence_rows_by_module=evidence_rows_by_module,
    )
    final_review_preview = _ordered_modules(
        modules,
        FINAL_REVIEW_READINESS_PREVIEW_MODULE_IDS,
        workspace_role="final_review_readiness_preview",
        evidence_rows_by_module=evidence_rows_by_module,
    )
    conditional_evidence = _ordered_modules(
        modules,
        CONDITIONAL_EVIDENCE_MODULE_IDS,
        workspace_role="conditional_evidence",
        evidence_rows_by_module=evidence_rows_by_module,
    )
    downstream_references = [
        _normalize_module(
            module,
            workspace_role="downstream_reference",
            evidence_rows=evidence_rows_by_module.get(_module_id(module)),
        )
        for module in modules
        if _module_applies(module)
        and (
            _module_requirement(module) == "REFERENCE"
            or _module_stage_owner(module) in DOWNSTREAM_STAGE_OWNERS
        )
    ]

    core_groups = [
        group
        for group in [
            _group(
                group_id="source_readiness",
                label="Source Readiness",
                purpose="Backtest Analysis에서 넘어온 후보가 검증 가능한 source인지 확인합니다.",
                modules=source_readiness,
            ),
            _group(
                group_id="validation_readiness",
                label="Validation Readiness",
                purpose="데이터, 구성, 현실성, robustness 근거가 Final Review 이동에 충분한지 확인합니다.",
                modules=validation_readiness,
            ),
            _group(
                group_id="final_review_readiness_preview",
                label="Final Review Readiness Preview",
                purpose="Final Review 저장 전에 막힐 deterministic evidence gap을 미리 확인합니다.",
                modules=final_review_preview,
            ),
        ]
        if group is not None
    ]
    conditional_groups = [
        group
        for group in [
            _group(
                group_id="conditional_evidence",
                label="Conditional Evidence",
                purpose="ETF, weighted mix, tactical source처럼 후보 특성에 따라 필요한 검증을 모읍니다.",
                modules=conditional_evidence,
            )
        ]
        if group is not None
    ]
    downstream_groups = [
        group
        for group in [
            _group(
                group_id="downstream_references",
                label="Final Review / Monitoring References",
                purpose="Stage 2 이동을 막는 근거가 아니라 Final Review와 Selected Dashboard에서 확인할 참고 근거입니다.",
                modules=downstream_references,
            )
        ]
        if group is not None
    ]
    fix_queue = _fix_queue(validation_row, modules, evidence_rows_by_module=evidence_rows_by_module)
    review_rows = _dict_list(gate.get("review_modules"))
    category_groups = _category_result_groups(modules, evidence_rows_by_module=evidence_rows_by_module)
    criteria_groups = _criteria_detail_groups(category_groups)
    visible_criteria_groups = _visible_criteria_detail_groups(criteria_groups)
    criteria_summary = _criteria_summary(criteria_groups)
    stage_ownership_inventory = _stage_ownership_inventory(modules)
    data_action_board = _data_action_board(
        validation_row,
        modules,
        evidence_rows_by_module,
    )
    handoff_summary_groups = [
        group
        for group in [
            _group(
                group_id="final_review_handoff_summary",
                label="Final Review Handoff Summary",
                purpose="검증 category가 아니라 Final Review 저장 전에 막힐 deterministic gap을 요약합니다.",
                modules=final_review_preview,
            )
        ]
        if group is not None
    ]

    gate_summary = {
        "route": gate.get("route") or "-",
        "can_save_and_move": bool(gate.get("can_save_and_move")),
        "verdict": gate.get("verdict") or "",
        "next_action": gate.get("next_action") or "",
        "blocker_count": len(fix_queue),
        "review_count": len(review_rows),
    }
    pv_caution_count = int(criteria_summary.get("pv_data_caution_count") or 0) + int(
        criteria_summary.get("pv_practical_caution_count") or 0
    )
    next_stage_action = _next_stage_action(gate, blocker_count=len(fix_queue), caution_count=pv_caution_count)

    return {
        "summary": {
            **gate_summary,
            **criteria_summary,
            "fix_item_count": len(fix_queue),
            "core_group_count": len(core_groups),
            "conditional_group_count": len(conditional_groups),
            "downstream_reference_group_count": len(downstream_groups),
            "handoff_summary_group_count": len(handoff_summary_groups),
        },
        "gate_summary": gate_summary,
        "fix_queue": fix_queue,
        "core_evidence_groups": core_groups,
        "conditional_evidence_groups": conditional_groups,
        "downstream_reference_groups": downstream_groups,
        "criteria_detail_groups": criteria_groups,
        "visible_criteria_detail_groups": visible_criteria_groups,
        "data_action_board": data_action_board,
        "next_stage_action": next_stage_action,
        "stage_ownership_inventory": stage_ownership_inventory,
        "category_result_groups": category_groups,
        "handoff_summary_groups": handoff_summary_groups,
        "technical_details": {
            "raw_diagnostics": _dict_list(validation_row.get("diagnostics")),
            "module_display_rows": _dict_list(validation_row.get("validation_module_display_rows")),
            "board_display_rows": _dict_list(validation_row.get("validation_board_display_rows")),
            "board_map": dict(validation_row.get("validation_board_map") or {}),
        },
    }


__all__ = [
    "build_practical_validation_workspace",
]
