from __future__ import annotations

from typing import Any


DAILY_SWING_POLICY_SCHEMA_VERSION = "daily_swing_selected_route_policy_v1"


def build_daily_swing_policy(validation: dict[str, Any]) -> dict[str, Any]:
    """Translate Daily Swing validation into manual Final Review/Monitoring policy."""

    module = dict(dict(validation or {}).get("daily_swing_validation") or {})
    applies = bool(module.get("applies"))
    status = str(module.get("status") or "NOT_APPLICABLE").upper()
    blockers = list(module.get("blockers") or [])
    if applies and status in {"BLOCKED", "NEEDS_INPUT", "NOT_RUN"} and not blockers:
        blockers.append("Daily Swing validation evidence is incomplete.")
    review_required = list(module.get("review_required") or [])
    limitations = list(module.get("review_limitations") or [])
    monitoring_conditions = list(dict.fromkeys([*review_required, *limitations]))
    return {
        "schema_version": DAILY_SWING_POLICY_SCHEMA_VERSION,
        "applies": applies,
        "validation_status": status,
        "selected_route_allowed": (not applies) or not blockers,
        "blockers": blockers,
        "review_required": review_required,
        "monitoring_conditions": monitoring_conditions,
        "review_cadence": "daily_after_market_close" if applies else None,
        "stale_after_market_days": 1 if applies else None,
        "manual_recheck_required": applies,
        "signal_policy": "research_evidence_not_order_signal" if applies else None,
        "auto_order": False,
        "auto_rebalance": False,
        "live_approval": False,
    }


__all__ = [
    "DAILY_SWING_POLICY_SCHEMA_VERSION",
    "build_daily_swing_policy",
]
