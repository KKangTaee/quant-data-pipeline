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
    "conditional_evidence": {
        "display_label": "후보 특성별 추가 근거가 필요한가",
        "purpose": "ETF, weighted mix, tactical source처럼 후보 특성에 따라 필요한 추가 검증을 확인합니다.",
    },
}
MODULE_DISPLAY_TEXT = {
    "source_integrity": {
        "display_label": "후보 source와 비중 계약이 유효한가",
        "checked_evidence": "무엇을 확인했나: source id, active component, target weight, Data Trust, curve evidence가 연결됐는지 봅니다.",
        "missing_evidence": "부족한 점: source id, component, weight, Data Trust, curve evidence 중 비어 있는 항목이 있으면 보강이 필요합니다.",
        "action_label": "Backtest Analysis에서 후보를 다시 만들거나 source contract를 복구합니다.",
        "why_it_matters": "이 계약이 불완전하면 어떤 후보를 검증하는지 Final Review가 안정적으로 추적할 수 없습니다.",
    },
    "latest_replay": {
        "display_label": "최신 데이터로 전략을 다시 돌렸는가",
        "checked_evidence": "무엇을 확인했나: 저장된 과거 snapshot만이 아니라 현재 DB 기준으로 같은 전략을 다시 실행할 수 있는지 봅니다.",
        "missing_evidence": "부족한 점: 이 세션에서 최신 runtime 재검증을 아직 실행하지 않았거나, replay curve와 coverage가 충분히 확인되지 않았습니다.",
        "action_label": "Flow 2에서 `전략 재검증 실행`을 누르고 Recheck와 Coverage가 PASS 또는 REVIEW인지 확인합니다.",
        "why_it_matters": "최신 데이터로 재현되지 않은 후보는 Final Review에서 실전 검증 완료 후보로 보기 어렵습니다.",
    },
    "benchmark_parity": {
        "display_label": "후보와 비교 기준이 같은 조건으로 비교됐는가",
        "checked_evidence": "무엇을 확인했나: benchmark, cash, simple baseline, custom comparator가 후보와 같은 기간 / frequency / coverage로 만들어졌는지 봅니다.",
        "missing_evidence": "부족한 점: 비교 기준 curve의 기간, 빈도, coverage가 후보 curve와 맞지 않으면 보강이 필요합니다.",
        "action_label": "같은 기간 / frequency / coverage의 benchmark 또는 comparator curve를 보강합니다.",
        "why_it_matters": "비교 조건이 다르면 후보 성과가 좋아 보이는 이유를 공정하게 판단하기 어렵습니다.",
    },
    "validation_efficacy": {
        "display_label": "검증이 우연한 좋은 구간에만 기대지 않는가",
        "checked_evidence": "무엇을 확인했나: rolling 구간, OOS holdout, macro regime, PIT / look-ahead, survivorship 근거가 후보 판단을 지지하는지 봅니다.",
        "missing_evidence": "부족한 점: walk-forward / OOS / regime / PIT / survivorship 근거 중 일부가 비어 있거나 보강 필요 상태입니다.",
        "action_label": "Flow 4의 `Validation Efficacy Audit 상세`에서 보강 필요 항목을 열고, 재검증 또는 데이터 보강으로 빠진 근거를 채웁니다.",
        "why_it_matters": "이 근거가 부족하면 성과가 특정 기간에만 우연히 좋았는지 구분하기 어렵습니다.",
    },
    "data_coverage": {
        "display_label": "검증에 필요한 가격 / provider / 생존편향 데이터가 충분한가",
        "checked_evidence": "무엇을 확인했나: 최신 가격 window, provider freshness, PIT replay 기간, universe / lifecycle / survivorship evidence를 봅니다.",
        "missing_evidence": "부족한 점: 가격 window, provider freshness, lifecycle, survivorship evidence 중 비어 있거나 오래된 데이터가 있으면 보강이 필요합니다.",
        "action_label": "Flow 4의 Data Coverage Audit / Provider Data Gaps에서 부족 row를 확인하고 가능한 provider gap 수집 또는 데이터 보강을 실행합니다.",
        "why_it_matters": "데이터 coverage가 부족하면 검증 결과가 일부 ticker나 현재 snapshot에만 기대게 됩니다.",
    },
    "construction_risk": {
        "display_label": "구성 / 집중 위험을 설명할 근거가 있는가",
        "checked_evidence": "무엇을 확인했나: 비중 집중, holdings / exposure coverage, top holding, overlap, unknown exposure를 봅니다.",
        "missing_evidence": "부족한 점: ETF 내부 보유 / exposure coverage나 concentration evidence가 부족하면 보강이 필요합니다.",
        "action_label": "Construction Risk Audit에서 집중 / overlap / unknown exposure row를 확인합니다.",
        "why_it_matters": "구성 위험을 설명하지 못하면 좋은 백테스트라도 실제 운용 위험을 판단하기 어렵습니다.",
    },
    "backtest_realism": {
        "display_label": "실전 운용 비용과 거래 현실성이 반영됐는가",
        "checked_evidence": "무엇을 확인했나: cost, turnover, liquidity, net performance, rebalance timing evidence를 봅니다.",
        "missing_evidence": "부족한 점: 비용 적용, turnover, liquidity, net curve 근거가 없으면 보강이 필요합니다.",
        "action_label": "Backtest Realism Audit에서 cost / turnover / liquidity / net performance blocker를 확인합니다.",
        "why_it_matters": "비용과 거래 현실성이 빠지면 실전 성과가 백테스트보다 크게 달라질 수 있습니다.",
    },
    "stress_robustness": {
        "display_label": "시장 충격과 설정 변화에도 버티는가",
        "checked_evidence": "무엇을 확인했나: stress window, rolling validation, sensitivity, overfit summary를 봅니다.",
        "missing_evidence": "부족한 점: stress / rolling / sensitivity / overfit 근거 중 실행되지 않았거나 부족한 항목이 있으면 보강이 필요합니다.",
        "action_label": "Robustness Lab에서 미실행 또는 보강 필요 row를 확인합니다.",
        "why_it_matters": "강건성 근거가 약하면 특정 조건에 과최적화된 후보일 수 있습니다.",
    },
    "selected_route_preflight": {
        "display_label": "Final Review 저장 전에 막힐 필수 gap이 없는가",
        "checked_evidence": "무엇을 확인했나: Final Review에서 모니터링 후보로 저장하기 전에 막힐 deterministic evidence gap을 봅니다.",
        "missing_evidence": "부족한 점: Final Review 저장 전에 필요한 evidence packet, selected-route policy, review-required gap이 남아 있으면 보강이 필요합니다.",
        "action_label": "Flow 4의 기준 상세와 Final Review readiness preview에서 blocker / review-required 항목을 먼저 해결합니다.",
        "why_it_matters": "여기서 gap을 확인하지 않으면 Final Review로 넘어가도 저장 단계에서 다시 막힐 수 있습니다.",
    },
    "provider_investability": {
        "display_label": "ETF provider 근거가 충분한가",
        "checked_evidence": "무엇을 확인했나: ETF operability, holdings, exposure, provider freshness를 봅니다.",
        "missing_evidence": "부족한 점: provider snapshot이나 holdings / exposure 근거가 없으면 추가 확인이 필요합니다.",
        "action_label": "Provider Action Center에서 수집 가능한 부족분을 보강합니다.",
        "why_it_matters": "provider 근거가 약하면 ETF 내부 노출과 실전 운용 가능성을 판단하기 어렵습니다.",
    },
    "risk_contribution": {
        "display_label": "weighted mix의 위험 기여가 한쪽으로 쏠리지 않는가",
        "checked_evidence": "무엇을 확인했나: component return matrix, correlation, risk contribution, drop-one dependency를 봅니다.",
        "missing_evidence": "부족한 점: component matrix나 risk contribution evidence가 없으면 weighted mix 위험 설명이 부족합니다.",
        "action_label": "Risk Contribution Audit에서 component matrix / correlation / drop-one row를 확인합니다.",
        "why_it_matters": "위험 기여가 설명되지 않으면 여러 component를 섞은 이유를 Final Review에서 판단하기 어렵습니다.",
    },
    "component_role_weight": {
        "display_label": "component 역할과 비중 이유가 설명되는가",
        "checked_evidence": "무엇을 확인했나: role source, target weight, profile intent, weight rationale을 봅니다.",
        "missing_evidence": "부족한 점: component role이나 weight rationale이 없으면 mix 구성 의도가 부족합니다.",
        "action_label": "Component Role / Weight Audit에서 role source와 weight rationale row를 확인합니다.",
        "why_it_matters": "역할과 비중 이유가 없으면 좋은 결과가 우연한 조합인지 판단하기 어렵습니다.",
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
    module_ids: set[str],
    *,
    workspace_role: str,
) -> list[dict[str, Any]]:
    order = {module_id: index for index, module_id in enumerate(module_ids)}
    rows = [
        _normalize_module(module, workspace_role=workspace_role)
        for module in modules
        if _module_id(module) in module_ids and _module_applies(module)
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


def _module_display_fields(module: dict[str, Any]) -> dict[str, Any]:
    module_id = str(module.get("module_id") or "").strip()
    label = str(module.get("label") or module_id or "-").strip()
    status = normalize_validation_status(module.get("status"))
    reading = dict(MODULE_DISPLAY_TEXT.get(module_id) or MODULE_DISPLAY_TEXT.get(label) or {})
    reason = str(module.get("reason") or module.get("profile_effect") or "").strip()
    evidence = str(module.get("gate_reason") or module.get("evidence") or module.get("next_action") or "").strip()
    action = str(module.get("resolution_action") or module.get("next_action") or "").strip()
    missing_fallback = evidence or action or "현재 기준에서 추가로 확인할 근거를 Flow 4 상세에서 확인합니다."
    if status in {"PASS", "READY"}:
        missing_fallback = "부족한 점: 현재 기준에서 즉시 막는 부족분은 없습니다."
    return {
        "display_label": reading.get("display_label") or label,
        "status_label": _criteria_status_label(status),
        "technical_status": status,
        "technical_label": f"{label} · {status}",
        "checked_evidence": reading.get("checked_evidence")
        or f"무엇을 확인했나: {reason or label + ' 기준'}",
        "missing_evidence": reading.get("missing_evidence") or f"부족한 점: {missing_fallback}",
        "action_label": reading.get("action_label") or action or "Flow 4 상세에서 부족 항목을 확인합니다.",
        "why_it_matters": reading.get("why_it_matters")
        or "이 기준은 Final Review로 넘길 수 있는지 판단하는 근거입니다.",
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
        "checked_evidence": module.get("checked_evidence") or f"무엇을 확인했나: {explanation}",
        "missing_evidence": module.get("missing_evidence") or f"부족한 점: {evidence}",
        "action_label": module.get("action_label") or module.get("resolution_action") or module.get("next_action") or "-",
        "why_it_matters": module.get("why_it_matters") or "이 기준은 Final Review 이동 가능 여부 판단에 사용됩니다.",
        "gate_effect": module.get("gate_effect") or "-",
        "resolution_surface": module.get("resolution_surface") or "-",
        "resolution_action": module.get("resolution_action") or module.get("next_action") or "-",
        "module_type": module.get("module_type") or module.get("requirement") or "-",
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
    criteria_groups = _criteria_detail_groups(core_groups + conditional_groups)
    criteria_summary = _criteria_summary(criteria_groups)

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
        },
        "gate_summary": gate_summary,
        "fix_queue": fix_queue,
        "core_evidence_groups": core_groups,
        "conditional_evidence_groups": conditional_groups,
        "downstream_reference_groups": downstream_groups,
        "criteria_detail_groups": criteria_groups,
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
