"""Role taxonomy for Practical Validation REVIEW rows.

The validation status stays `REVIEW`, but the UI needs to know whether the
item is a current Practical Validation caution, a Final Review input, or a
Monitoring follow-up. This module is display/read-model policy only.
"""

from __future__ import annotations

from typing import Any


REVIEW_ROLE_METADATA = {
    "pv_data_caution": {
        "review_role_label": "데이터 주의",
        "stage_decision_surface": "Practical Validation",
        "pv_visibility": "category_board",
        "final_review_visibility": "evidence_appendix",
        "monitoring_visibility": "hidden",
        "review_gate_effect": "Practical Validation data caution",
    },
    "pv_practical_caution": {
        "review_role_label": "2단계 실용성 주의",
        "stage_decision_surface": "Practical Validation",
        "pv_visibility": "category_board",
        "final_review_visibility": "evidence_appendix",
        "monitoring_visibility": "optional_trigger",
        "review_gate_effect": "Practical Validation caution",
    },
    "final_decision_input": {
        "review_role_label": "최종 판단 참고",
        "stage_decision_surface": "Final Review",
        "pv_visibility": "handoff_reference",
        "final_review_visibility": "decision_cockpit",
        "monitoring_visibility": "hidden",
        "review_gate_effect": "Final Review decision input",
    },
    "monitoring_followup": {
        "review_role_label": "Monitoring 추적",
        "stage_decision_surface": "Operations > Portfolio Monitoring",
        "pv_visibility": "hidden",
        "final_review_visibility": "handoff_reference",
        "monitoring_visibility": "monitoring_board",
        "review_gate_effect": "Monitoring follow-up",
    },
    "final_readiness_blocker": {
        "review_role_label": "저장 전 보강",
        "stage_decision_surface": "Practical Validation",
        "pv_visibility": "handoff_reference",
        "final_review_visibility": "selected_route_gate",
        "monitoring_visibility": "hidden",
        "review_gate_effect": "Final Review readiness blocker",
    },
}

MODULE_REVIEW_ROLES = {
    "source_integrity": "pv_data_caution",
    "latest_replay": "pv_data_caution",
    "benchmark_parity": "pv_data_caution",
    "data_coverage": "pv_data_caution",
    "validation_efficacy": "pv_practical_caution",
    "construction_risk": "pv_practical_caution",
    "backtest_realism": "pv_practical_caution",
    "stress_robustness": "pv_practical_caution",
    "provider_investability": "pv_practical_caution",
    "leverage_inverse": "pv_practical_caution",
    "risk_contribution": "pv_practical_caution",
    "component_role_weight": "pv_practical_caution",
    "macro_regime": "pv_practical_caution",
    "tax_account_scope": "final_decision_input",
    "monitoring_baseline": "monitoring_followup",
    "selected_route_preflight": "final_readiness_blocker",
}


def review_role_for_module(module: dict[str, Any]) -> str:
    """Return the stage role for a validation module's REVIEW state."""
    module_id = str(module.get("module_id") or "").strip()
    if module_id in MODULE_REVIEW_ROLES:
        return MODULE_REVIEW_ROLES[module_id]
    stage_owner = str(module.get("stage_owner") or "").strip().lower()
    if stage_owner == "final_review":
        return "final_decision_input"
    if stage_owner == "selected_dashboard":
        return "monitoring_followup"
    return "pv_practical_caution"


def review_role_fields(module: dict[str, Any]) -> dict[str, str]:
    """Expose role metadata fields consumed by Streamlit and React read models."""
    role = review_role_for_module(module)
    metadata = REVIEW_ROLE_METADATA[role]
    return {
        "review_role": role,
        **metadata,
    }


def review_gate_effect(module: dict[str, Any]) -> str:
    """Return the gate-effect label associated with a module's REVIEW role."""
    return review_role_fields(module)["review_gate_effect"]
