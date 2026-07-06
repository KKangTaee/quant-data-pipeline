from __future__ import annotations

from typing import Any

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
        "group_id": "validation_strength",
        "label": "Validation Strength / Robustness",
        "purpose": "성과가 특정 구간이나 설정에만 기대지 않는지 확인합니다.",
        "module_ids": ("validation_efficacy", "stress_robustness"),
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
        "purpose": "ETF provider, 레버리지 / 인버스, macro 조건처럼 후보 특성에 따라 필요한 추가 근거를 확인합니다.",
        "module_ids": ("provider_investability", "leverage_inverse", "macro_regime"),
    },
]
STATUS_LABELS = {
    "PASS": "통과",
    "READY": "통과",
    "REVIEW": "Final Review에서 확인",
    "NEEDS_INPUT": "근거 보강 필요",
    "NOT_RUN": "아직 실행 안 됨",
    "BLOCKED": "이동 차단",
    "NOT_APPLICABLE": "비적용",
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
    "validation_strength": {
        "display_label": "검증 강도 / 강건성",
        "purpose": "walk-forward, OOS, regime, stress, sensitivity 근거가 결과 해석에 충분한지 확인합니다.",
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
        "purpose": "ETF provider, 레버리지 / 인버스, macro 조건처럼 해당 후보에만 필요한 근거를 확인합니다.",
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
        "issue_title": "최신 runtime 재검증 미실행",
        "current_problem": "현재 세션에서 최신 DB 기준 재검증이 실행되지 않았거나 replay curve와 coverage가 충분히 확인되지 않았습니다.",
        "completion_criteria": "Flow 2 재검증 결과가 PASS 또는 Final Review 확인 상태이고 coverage가 Final Review 이동을 막지 않아야 합니다.",
        "fix_location": "Flow 2 · 실전 재검증 실행",
        "impact_summary": "최신 데이터로 재현되지 않은 후보는 Final Review에서 실전 검증 완료 후보로 보기 어렵습니다.",
    },
    "benchmark_parity": {
        "display_label": "후보와 비교 기준이 같은 조건으로 비교됐는가",
        "issue_title": "비교 기준 동등성 부족",
        "current_problem": "benchmark, cash, simple baseline, custom comparator의 기간 / frequency / coverage가 후보와 맞지 않으면 비교가 왜곡됩니다.",
        "completion_criteria": "Benchmark / Comparator Parity가 PASS 상태이고 후보와 비교 기준이 같은 기간 / frequency / coverage로 정렬되어야 합니다.",
        "fix_location": "검증 기준 상세 · 핵심 입력 근거",
        "impact_summary": "비교 조건이 다르면 후보 성과가 좋아 보이는 이유를 공정하게 판단하기 어렵습니다.",
    },
    "validation_efficacy": {
        "display_label": "검증이 우연한 좋은 구간에만 기대지 않는가",
        "issue_title": "검증 효력 근거 부족",
        "current_problem": "walk-forward / OOS / regime / PIT / survivorship 근거 중 일부가 비어 있거나 보강 필요 상태입니다.",
        "completion_criteria": "Validation Efficacy 핵심 항목이 PASS 또는 Final Review 확인 상태가 되어야 합니다.",
        "fix_location": "검증 기준 상세 · 검증 강도 / 강건성",
        "impact_summary": "이 근거가 부족하면 성과가 특정 기간에만 우연히 좋았는지 구분하기 어렵습니다.",
    },
    "data_coverage": {
        "display_label": "검증에 필요한 가격 / provider / 생존편향 데이터가 충분한가",
        "issue_title": "데이터 커버리지 부족",
        "current_problem": "가격 window, provider freshness, lifecycle, survivorship evidence 중 비어 있거나 오래된 데이터가 있습니다.",
        "completion_criteria": "데이터 커버리지 핵심 항목이 PASS 또는 Final Review 확인 상태이고 provider gap이 Final Review 이동을 막지 않아야 합니다.",
        "fix_location": "검증 기준 상세 · 데이터 품질 / Provider 보강",
        "impact_summary": "데이터 커버리지가 부족하면 검증 결과가 일부 ticker나 현재 snapshot에만 기대게 됩니다.",
    },
    "construction_risk": {
        "display_label": "구성 / 집중 위험을 설명할 근거가 있는가",
        "issue_title": "구성 / 집중 위험 근거 부족",
        "current_problem": "ETF 내부 보유 / exposure coverage나 concentration evidence가 부족하면 실제 구성 위험을 설명하기 어렵습니다.",
        "completion_criteria": "Construction Risk가 PASS 또는 Final Review 확인 상태이고 집중 / overlap / unknown exposure가 판단 근거로 정리되어야 합니다.",
        "fix_location": "검증 기준 상세 · 포트폴리오 구성 근거",
        "impact_summary": "구성 위험을 설명하지 못하면 좋은 백테스트라도 실제 운용 위험을 판단하기 어렵습니다.",
    },
    "backtest_realism": {
        "display_label": "실전 운용 비용과 거래 현실성이 반영됐는가",
        "issue_title": "실전 운용 현실성 근거 부족",
        "current_problem": "비용 적용, turnover, liquidity, net curve 근거가 없으면 백테스트 성과가 실전 운용 성과와 달라질 수 있습니다.",
        "completion_criteria": "Backtest Realism 핵심 항목이 PASS 또는 Final Review 확인 상태이고 cost / turnover / liquidity blocker가 없어야 합니다.",
        "fix_location": "검증 기준 상세 · 실전 운용 현실성",
        "impact_summary": "비용과 거래 현실성이 빠지면 실전 성과가 백테스트보다 크게 달라질 수 있습니다.",
    },
    "stress_robustness": {
        "display_label": "시장 충격과 설정 변화에도 버티는가",
        "issue_title": "강건성 근거 부족",
        "current_problem": "stress / rolling / sensitivity / overfit 근거 중 실행되지 않았거나 부족한 항목이 있습니다.",
        "completion_criteria": "Stress / Robustness가 PASS 또는 Final Review 확인 상태이고 미실행 핵심 항목이 없어야 합니다.",
        "fix_location": "검증 기준 상세 · 강건성 검증",
        "impact_summary": "강건성 근거가 약하면 특정 조건에 과최적화된 후보일 수 있습니다.",
    },
    "selected_route_preflight": {
        "display_label": "Final Review 저장 전에 막힐 필수 gap이 없는가",
        "issue_title": "Final Review 저장 전 필수 gap",
        "current_problem": "Final Review 저장 전에 필요한 evidence packet, selected-route policy, review-required gap이 남아 있습니다.",
        "completion_criteria": "Selected-route Preflight가 PASS 또는 Final Review 확인 상태이고 저장 차단 gap이 없어야 합니다.",
        "fix_location": "Final Review 이동 요약",
        "impact_summary": "여기서 gap을 확인하지 않으면 Final Review로 넘어가도 저장 단계에서 다시 막힐 수 있습니다.",
    },
    "provider_investability": {
        "display_label": "ETF provider 근거가 충분한가",
        "issue_title": "ETF provider 근거 부족",
        "current_problem": "provider snapshot이나 holdings / exposure 근거가 없으면 ETF 내부 노출과 운용 가능성을 판단하기 어렵습니다.",
        "completion_criteria": "ETF Provider Investability가 PASS 또는 Final Review 확인 상태이고 provider snapshot gap이 보강되어야 합니다.",
        "fix_location": "Provider / Data 보강 액션",
        "impact_summary": "provider 근거가 약하면 ETF 내부 노출과 실전 운용 가능성을 판단하기 어렵습니다.",
    },
    "risk_contribution": {
        "display_label": "weighted mix의 위험 기여가 한쪽으로 쏠리지 않는가",
        "issue_title": "위험 기여 설명 부족",
        "current_problem": "component matrix나 risk contribution evidence가 없으면 weighted mix 위험이 한쪽으로 쏠렸는지 설명하기 어렵습니다.",
        "completion_criteria": "Risk Contribution이 PASS 또는 Final Review 확인 상태이고 component matrix / correlation / drop-one 근거가 있어야 합니다.",
        "fix_location": "검증 기준 상세 · 포트폴리오 구성 근거",
        "impact_summary": "위험 기여가 설명되지 않으면 여러 component를 섞은 이유를 Final Review에서 판단하기 어렵습니다.",
    },
    "component_role_weight": {
        "display_label": "component 역할과 비중 이유가 설명되는가",
        "issue_title": "component 역할 / 비중 근거 부족",
        "current_problem": "component role이나 weight rationale이 없으면 mix 구성 의도가 부족합니다.",
        "completion_criteria": "Component Role / Weight가 PASS 또는 Final Review 확인 상태이고 role source와 weight rationale이 정리되어야 합니다.",
        "fix_location": "검증 기준 상세 · 포트폴리오 구성 근거",
        "impact_summary": "역할과 비중 이유가 없으면 좋은 결과가 우연한 조합인지 판단하기 어렵습니다.",
    },
}


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


def _normalize_module(module: dict[str, Any], *, workspace_role: str) -> dict[str, Any]:
    row = dict(module or {})
    row["module_id"] = _module_id(row)
    row["status"] = normalize_validation_status(row.get("status"))
    row["workspace_role"] = workspace_role
    row.update(_module_display_fields(row))
    return row


def _ordered_modules(
    modules: list[dict[str, Any]],
    module_ids: set[str] | tuple[str, ...],
    *,
    workspace_role: str,
) -> list[dict[str, Any]]:
    module_order = list(module_ids)
    module_id_set = set(module_order)
    order = {module_id: index for index, module_id in enumerate(module_order)}
    rows = [
        _normalize_module(module, workspace_role=workspace_role)
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


def _clean_issue_text(value: Any) -> str:
    text = str(value or "").strip()
    if not text:
        return ""
    replacements = {
        "NEEDS_INPUT row": "보강 필요 항목",
        "NEEDS_INPUT 항목": "보강 필요 항목",
        "NOT_RUN row": "미실행 항목",
        "REVIEW row": "Final Review 확인 항목",
    }
    for raw, replacement in replacements.items():
        text = text.replace(raw, replacement)
    return text


def _module_display_fields(module: dict[str, Any]) -> dict[str, Any]:
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
        or f"{label} 기준이 PASS 또는 Final Review 확인 상태가 되어야 합니다."
    )
    if status in {"PASS", "READY"}:
        current_problem = "현재 기준에서 Final Review 이동을 즉시 막는 문제는 없습니다."
        completion_criteria = f"{label} 기준이 통과 상태입니다."
    fix_location = reading.get("fix_location") or module.get("resolution_surface") or "Flow 4 기준 상세"
    impact_summary = (
        reading.get("impact_summary")
        or "이 기준이 해결되지 않으면 Final Review 이동 또는 저장 단계에서 다시 보류될 수 있습니다."
    )
    return {
        "display_label": reading.get("display_label") or label,
        "issue_title": reading.get("issue_title") or reading.get("display_label") or label,
        "status_label": _criteria_status_label(status),
        "technical_status": status,
        "technical_label": f"{label} · {status}",
        "current_problem": current_problem,
        "completion_criteria": completion_criteria,
        "fix_location": fix_location,
        "impact_summary": impact_summary,
        "checked_evidence": current_problem,
        "missing_evidence": current_problem,
        "action_label": completion_criteria,
        "why_it_matters": impact_summary,
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
    return {
        "module_id": module.get("module_id") or "-",
        "label": module.get("label") or module.get("module_id") or "-",
        "display_label": module.get("display_label") or module.get("label") or module.get("module_id") or "-",
        "status": status,
        "status_label": module.get("status_label") or _criteria_status_label(status),
        "technical_status": module.get("technical_status") or status,
        "technical_label": module.get("technical_label") or f"{module.get('label') or module.get('module_id') or '-'} · {status}",
        "tone": _status_tone(status),
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
    review = [
        str(card.get("display_label") or card.get("label") or "-")
        for card in cards
        if card.get("status") == "REVIEW"
    ]
    if remaining:
        decision = f"보강 필요 {len(remaining)}개가 남아 있어 Final Review 이동 전 확인이 필요합니다."
    elif review:
        decision = f"Final Review에서 확인할 기준 {len(review)}개가 남아 있습니다."
    else:
        decision = "이 기준 그룹은 현재 통과 상태입니다."
    return {
        "passed_criteria": passed,
        "remaining_issues": remaining,
        "review_criteria": review,
        "decision_summary": decision,
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


def _criteria_summary(groups: list[dict[str, Any]]) -> dict[str, int]:
    cards = [
        dict(card or {})
        for group in groups
        for card in list(group.get("criteria_cards") or [])
        if isinstance(card, dict)
    ]
    return {
        "criteria_group_count": len(groups),
        "criteria_card_count": len(cards),
        "criteria_pass_count": len([card for card in cards if card.get("status") in {"PASS", "READY"}]),
        "criteria_review_count": len([card for card in cards if card.get("status") == "REVIEW"]),
        "criteria_blocker_count": len(
            [
                card
                for card in cards
                if card.get("status") in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}
            ]
        ),
    }


def _category_result_groups(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    groups: list[dict[str, Any]] = []
    for spec in FLOW4_CATEGORY_GROUP_SPECS:
        category_modules = _ordered_modules(
            modules,
            tuple(spec.get("module_ids") or ()),
            workspace_role="validation_category",
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


def _fallback_fix_queue(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for module in modules:
        status = normalize_validation_status(module.get("status"))
        gate_effect = str(module.get("gate_effect") or "")
        if status in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"} or gate_effect == "Blocks Final Review":
            rows.append(_normalize_module(module, workspace_role="fix_queue"))
    return rows


def _fix_queue(validation: dict[str, Any], modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    gate = dict(validation.get("final_review_gate") or {})
    blocking_rows = _dict_list(gate.get("blocking_modules"))
    if blocking_rows:
        module_by_id = {_module_id(module): module for module in modules}
        merged_rows: list[dict[str, Any]] = []
        for row in blocking_rows:
            module_id = _module_id(row)
            merged = {**dict(module_by_id.get(module_id) or {}), **row}
            merged_rows.append(_normalize_module(merged, workspace_role="fix_queue"))
        return merged_rows
    return _fallback_fix_queue(modules)


def build_practical_validation_workspace(validation: dict[str, Any]) -> dict[str, Any]:
    """Build a screen-oriented Practical Validation workspace model from validation evidence."""

    validation_row = dict(validation or {})
    modules = _dict_list(validation_row.get("validation_modules"))
    gate = dict(validation_row.get("final_review_gate") or {})

    source_readiness = _ordered_modules(
        modules,
        SOURCE_READINESS_MODULE_IDS,
        workspace_role="core_evidence",
    )
    validation_readiness = _ordered_modules(
        modules,
        VALIDATION_READINESS_MODULE_IDS,
        workspace_role="core_evidence",
    )
    final_review_preview = _ordered_modules(
        modules,
        FINAL_REVIEW_READINESS_PREVIEW_MODULE_IDS,
        workspace_role="final_review_readiness_preview",
    )
    conditional_evidence = _ordered_modules(
        modules,
        CONDITIONAL_EVIDENCE_MODULE_IDS,
        workspace_role="conditional_evidence",
    )
    downstream_references = [
        _normalize_module(module, workspace_role="downstream_reference")
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
    fix_queue = _fix_queue(validation_row, modules)
    review_rows = _dict_list(gate.get("review_modules"))
    category_groups = _category_result_groups(modules)
    criteria_groups = _criteria_detail_groups(category_groups)
    criteria_summary = _criteria_summary(criteria_groups)
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
