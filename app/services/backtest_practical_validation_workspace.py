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
            "core_group_count": len(core_groups),
            "conditional_group_count": len(conditional_groups),
            "downstream_reference_group_count": len(downstream_groups),
        },
        "gate_summary": gate_summary,
        "fix_queue": fix_queue,
        "core_evidence_groups": core_groups,
        "conditional_evidence_groups": conditional_groups,
        "downstream_reference_groups": downstream_groups,
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
