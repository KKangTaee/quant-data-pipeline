from __future__ import annotations

from typing import Any

import streamlit as st

from app.web.backtest_practical_validation.components import (
    render_pv_alert_panel,
    render_pv_card_grid,
    render_pv_section_header,
)
from app.web.backtest_ui_components import render_badge_strip
from app.web.components.practical_validation_fix_queue import (
    is_practical_validation_fix_queue_available,
    render_practical_validation_fix_queue,
)


GATE_FIX_GUIDANCE = {
    "latest_replay": {
        "location": "3. 최신 데이터 기준 전략 재검증",
        "action": "`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
    },
    "Latest Runtime Replay": {
        "location": "3. 최신 데이터 기준 전략 재검증",
        "action": "`전략 재검증 실행` 버튼을 누른 뒤 Recheck가 PASS 또는 REVIEW이고 Coverage가 PASS인지 확인합니다.",
    },
    "validation_efficacy": {
        "location": "Validation Efficacy Audit",
        "action": "NEEDS_INPUT row를 확인해 walk-forward / OOS / regime / PIT / survivorship evidence 부족분을 보강합니다.",
    },
    "Validation Efficacy": {
        "location": "Validation Efficacy Audit",
        "action": "NEEDS_INPUT row를 확인해 walk-forward / OOS / regime / PIT / survivorship evidence 부족분을 보강합니다.",
    },
    "data_coverage": {
        "location": "Data Coverage Audit / Provider Data Gaps",
        "action": "가격 window, provider freshness, lifecycle / survivorship row 중 NEEDS_INPUT 항목을 확인하고 provider gap 수집 또는 데이터 보강을 진행합니다.",
    },
    "Data Coverage": {
        "location": "Data Coverage Audit / Provider Data Gaps",
        "action": "가격 window, provider freshness, lifecycle / survivorship row 중 NEEDS_INPUT 항목을 확인하고 provider gap 수집 또는 데이터 보강을 진행합니다.",
    },
}


def _status_tone(status: Any) -> str:
    status_text = str(status or "").upper()
    if status_text in {"PASS", "READY", "READY_FOR_FINAL_REVIEW"}:
        return "positive"
    if "BLOCKED" in status_text:
        return "danger"
    if status_text in {"REVIEW", "NEEDS_INPUT", "READY_WITH_REVIEW"}:
        return "warning"
    return "neutral"


def _gate_module_display_rows(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    display_rows: list[dict[str, Any]] = []
    for row in modules:
        module_id = str(row.get("module_id") or "").strip()
        label = str(row.get("label") or module_id or "-").strip()
        guidance = dict(GATE_FIX_GUIDANCE.get(module_id) or GATE_FIX_GUIDANCE.get(label) or {})
        fix_location = row.get("resolution_surface") or guidance.get("location") or "-"
        fix_action = (
            row.get("resolution_action")
            or guidance.get("action")
            or row.get("next_action")
            or "-"
        )
        display_rows.append(
            {
                "Module": label,
                "Status": row.get("status") or "-",
                "Fix Location": fix_location,
                "Fix Action": fix_action,
                "Gate Effect": row.get("gate_effect") or "-",
                "Gate Reason": row.get("gate_reason") or "-",
            }
        )
    return display_rows


def gate_module_display_rows(modules: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return _gate_module_display_rows(modules)


def _render_fix_queue(blocking_modules: list[dict[str, Any]]) -> None:
    if not blocking_modules:
        render_pv_card_grid(
            [
                {
                    "kicker": "Fix Queue",
                    "title": "필수 보강 항목 없음",
                    "status": "Ready",
                    "detail": "Final Review로 이동하기 전에 즉시 막는 필수 검증 blocker가 없습니다.",
                    "tone": "positive",
                }
            ],
            min_width=240,
        )
        return
    cards: list[dict[str, Any]] = []
    for module in blocking_modules:
        display_row = _gate_module_display_rows([module])[0]
        cards.append(
            {
                "kicker": display_row.get("Status") or "BLOCKING",
                "title": display_row.get("Module") or "-",
                "status": display_row.get("Fix Location") or "-",
                "detail": display_row.get("Fix Action") or "-",
                "meta": display_row.get("Gate Reason") or "",
                "tone": _status_tone(display_row.get("Status")),
            }
        )
    render_pv_section_header(
        eyebrow="Fix Queue",
        title=f"Final Review 이동 전 해결할 항목 {len(blocking_modules)}개",
        detail="각 카드의 Fix Location에서 보강한 뒤 Gate가 다시 계산됩니다.",
        tone="danger",
    )
    render_pv_card_grid(cards, min_width=260)


def _workspace_group_tone(modules: list[dict[str, Any]]) -> str:
    statuses = {str(module.get("status") or "").upper() for module in modules}
    if statuses & {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"}:
        return "danger"
    if "REVIEW" in statuses:
        return "warning"
    return "positive"


def _workspace_group_status(modules: list[dict[str, Any]]) -> str:
    counts: dict[str, int] = {}
    for module in modules:
        status = str(module.get("status") or "NOT_RUN").upper()
        counts[status] = counts.get(status, 0) + 1
    if not counts:
        return "-"
    return " / ".join(f"{status} {count}" for status, count in sorted(counts.items()))


def _workspace_group_cards(groups: list[dict[str, Any]], *, kicker: str) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for group in groups:
        modules = [dict(module or {}) for module in list(group.get("modules") or [])]
        cards.append(
            {
                "kicker": kicker,
                "title": group.get("label") or group.get("group_id") or "-",
                "status": _workspace_group_status(modules),
                "detail": group.get("purpose") or f"{len(modules)} module(s)",
                "tone": _workspace_group_tone(modules),
            }
        )
    return cards


def _react_fix_queue_items(fix_queue: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for row in _gate_module_display_rows(fix_queue):
        items.append(
            {
                "label": row.get("Module") or "-",
                "status": row.get("Status") or "-",
                "fixLocation": row.get("Fix Location") or "-",
                "fixAction": row.get("Fix Action") or "-",
                "gateReason": row.get("Gate Reason") or "",
                "tone": _status_tone(row.get("Status")),
            }
        )
    return items


def _react_core_group_items(core_groups: list[dict[str, Any]]) -> list[dict[str, Any]]:
    items: list[dict[str, Any]] = []
    for group in core_groups:
        modules = [dict(module or {}) for module in list(group.get("modules") or [])]
        items.append(
            {
                "label": group.get("label") or group.get("group_id") or "-",
                "status": _workspace_group_status(modules),
                "purpose": group.get("purpose") or f"{len(modules)} module(s)",
                "tone": _workspace_group_tone(modules),
                "modules": [
                    str(module.get("label") or module.get("module_id") or "-")
                    for module in modules
                    if module
                ],
            }
        )
    return items


def render_practical_validation_workspace_overview(validation_result: dict[str, Any]) -> None:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    gate_summary = dict(workspace.get("gate_summary") or validation_result.get("final_review_gate") or {})
    fix_queue = list(workspace.get("fix_queue") or gate_summary.get("blocking_modules") or [])
    core_groups = list(workspace.get("core_evidence_groups") or [])
    conditional_groups = list(workspace.get("conditional_evidence_groups") or [])
    downstream_groups = list(workspace.get("downstream_reference_groups") or [])

    render_pv_alert_panel(
        title="2차 검증 결론",
        detail=(
            f"{gate_summary.get('verdict') or ''} "
            f"{gate_summary.get('next_action') or ''}"
        ).strip()
        or "Practical Validation workspace가 gate와 evidence group을 요약합니다.",
        tone="positive" if gate_summary.get("can_save_and_move") else "danger",
    )
    render_badge_strip(
        [
            {
                "label": "Readiness",
                "value": gate_summary.get("route") or "-",
                "tone": _status_tone(gate_summary.get("route")),
            },
            {
                "label": "Final Review Move",
                "value": "Enabled" if gate_summary.get("can_save_and_move") else "Blocked",
                "tone": "positive" if gate_summary.get("can_save_and_move") else "danger",
            },
            {
                "label": "Fix Queue",
                "value": len(fix_queue),
                "tone": "danger" if fix_queue else "positive",
            },
            {
                "label": "Review Items",
                "value": gate_summary.get("review_count", 0),
                "tone": "warning" if gate_summary.get("review_count") else "neutral",
            },
        ]
    )
    if is_practical_validation_fix_queue_available():
        render_practical_validation_fix_queue(
            status_label=str(gate_summary.get("route") or "-"),
            tone="positive" if gate_summary.get("can_save_and_move") else "danger",
            verdict=str(gate_summary.get("verdict") or "2차 검증 결론"),
            next_action=str(gate_summary.get("next_action") or ""),
            can_save_and_move=bool(gate_summary.get("can_save_and_move")),
            fix_items=_react_fix_queue_items(fix_queue),
            core_groups=_react_core_group_items(core_groups),
            review_count=int(gate_summary.get("review_count") or 0),
            key="practical_validation_fix_queue_overview",
        )
    else:
        _render_fix_queue(fix_queue)
        if core_groups:
            render_pv_section_header(
                eyebrow="Core Evidence",
                title="2차 검증 핵심 근거",
                detail="Final Review로 넘기기 전에 먼저 확인할 source, validation, readiness preview 근거입니다.",
                tone="neutral",
            )
            render_pv_card_grid(_workspace_group_cards(core_groups, kicker="Core"), min_width=250)
    if conditional_groups or downstream_groups:
        with st.expander("조건부 근거와 후속 참고", expanded=False):
            if conditional_groups:
                render_pv_card_grid(
                    _workspace_group_cards(conditional_groups, kicker="Conditional"),
                    min_width=250,
                )
            if downstream_groups:
                render_pv_card_grid(
                    _workspace_group_cards(downstream_groups, kicker="Reference"),
                    min_width=250,
                )
