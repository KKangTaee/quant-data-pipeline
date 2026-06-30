from __future__ import annotations

from typing import Any


PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION = (
    "practical_validation_selected_route_preflight_v1"
)


def build_selected_route_preflight_from_packet(packet: dict[str, Any]) -> dict[str, Any]:
    """Map an investability evidence packet into the selected-route preflight contract."""

    policy = dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot") or {})
    select_allowed = bool(policy.get("select_allowed"))
    return {
        "schema_version": PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION,
        "route": (
            "SELECTED_ROUTE_PREFLIGHT_READY"
            if select_allowed
            else "SELECTED_ROUTE_PREFLIGHT_NEEDS_INPUT"
        ),
        "select_allowed": select_allowed,
        "policy_outcome": policy.get("outcome") or "-",
        "suggested_decision_route": policy.get("suggested_decision_route") or "-",
        "next_action": policy.get("next_action") or packet.get("next_action") or "-",
        "blockers": list(policy.get("blockers") or []),
        "review_required": list(policy.get("review_required") or []),
        "policy_rows": list(policy.get("policy_rows") or []),
        "packet_route": packet.get("route"),
        "packet_select_ready": bool(packet.get("select_ready")),
        "open_review_items": len(packet.get("open_review_items") or []),
    }


__all__ = [
    "PRACTICAL_VALIDATION_SELECTED_ROUTE_PREFLIGHT_SCHEMA_VERSION",
    "build_selected_route_preflight_from_packet",
]
