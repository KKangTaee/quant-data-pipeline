from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME
from app.services.backtest_strategy_evidence_inventory import (
    FIRST_EVIDENCE_MATURE_CANDIDATE_KEYS,
    build_strategy_evidence_inventory,
)


STRICT_ANNUAL_ETF_BRIDGE_KEYS = (
    "quality_value_snapshot_strict_annual",
    "value_snapshot_strict_annual",
    "quality_snapshot_strict_annual",
    "gtaa",
    "equal_weight",
)

_COMMON_ROUTE_BOUNDARY = (
    "Backtest Analysis bridge only; Practical Validation owns evidence results, "
    "Final Review owns selected-route decisions, and Portfolio Monitoring remains read-only."
)

_BRIDGE_DETAIL_BY_KEY: dict[str, dict[str, Any]] = {
    "quality_value_snapshot_strict_annual": {
        "bridge_role": "Core blended strict annual candidate",
        "target_use": "Use as the first core factor candidate when the user wants a balanced quality + value anchor.",
        "required_practical_validation_evidence": [
            "PIT factor / statement availability",
            "Provider / liquidity coverage",
            "Concentration and factor overlap",
            "Drawdown and rolling underperformance",
            "Backtest realism cost / turnover proof",
        ],
        "recommended_next_workflow": (
            "Run Practical Validation first as the core bridge candidate, then review selected-route readiness in Final Review."
        ),
    },
    "value_snapshot_strict_annual": {
        "bridge_role": "Return engine strict annual candidate",
        "target_use": "Use as a higher-return sleeve only when downside and concentration evidence can be reviewed explicitly.",
        "required_practical_validation_evidence": [
            "Drawdown and downside open review",
            "Provider / liquidity coverage",
            "Concentration and position capacity",
            "Benchmark-relative temporal validation",
            "Backtest realism cost / turnover proof",
        ],
        "recommended_next_workflow": (
            "Run Practical Validation with downside review focus before any Final Review selected-route decision."
        ),
    },
    "quality_snapshot_strict_annual": {
        "bridge_role": "Quality stabilizer strict annual candidate",
        "target_use": "Use as a reference / stabilizer sleeve rather than a standalone return winner.",
        "required_practical_validation_evidence": [
            "PIT factor / statement availability",
            "Benchmark and overlay dependency",
            "Provider / liquidity coverage",
            "Temporal validation versus benchmark",
            "Role / weight discipline",
        ],
        "recommended_next_workflow": (
            "Run Practical Validation as a stabilizer/reference sleeve and keep role discipline visible for Final Review."
        ),
    },
    "gtaa": {
        "bridge_role": "ETF tactical sleeve",
        "target_use": "Use as defensive / tactical allocation sleeve beside strict annual factor candidates.",
        "required_practical_validation_evidence": [
            "ETF provider and operability coverage",
            "Transaction cost / slippage assumption",
            "Cadence and benchmark alignment",
            "Universe / score horizon sensitivity",
            "Backtest realism net performance proof",
        ],
        "recommended_next_workflow": (
            "Run Practical Validation as the tactical ETF sleeve and compare cadence / benchmark evidence before Final Review."
        ),
    },
    "equal_weight": {
        "bridge_role": "ETF baseline sleeve",
        "target_use": "Use as exposure baseline / ballast, not as a standalone alpha claim.",
        "required_practical_validation_evidence": [
            "ETF provider and operability coverage",
            "Cost and liquidity evidence",
            "Concentration / exposure look-through",
            "Benchmark-relative baseline interpretation",
            "Role / weight discipline",
        ],
        "recommended_next_workflow": (
            "Run Practical Validation as a baseline sleeve paired with GTAA or strict annual candidates."
        ),
    },
}

_VALIDATION_CHECKLIST = [
    "Confirm PIT factor / statement source strength for strict annual equity candidates.",
    "Confirm ETF provider / liquidity / operability evidence for GTAA and Equal Weight sleeves.",
    "Review concentration, factor overlap, and role / weight discipline before treating the group as a portfolio bridge.",
    "Check drawdown, rolling underperformance, and temporal validation before Final Review.",
    "Check cost / turnover / net-cost proof in Backtest Realism before selected-route decisions.",
    "Keep Risk-On Momentum out of this bridge; strict quarterly candidates use their own post-run Factor Readiness path before portfolio bridge decisions.",
]

_NEXT_WORKFLOW_STEPS = [
    "Select one core strict annual candidate and one optional ETF sleeve in Backtest Analysis.",
    "Run Practical Validation for the selected source or mix with bridge role notes visible.",
    "Use Final Review only after Practical Validation evidence is complete.",
    "Move to Portfolio Monitoring only through selected-route decisions; no live approval or broker order is created.",
]


def _inventory_by_key() -> dict[str, dict[str, Any]]:
    return {row["strategy_key"]: row for row in build_strategy_evidence_inventory()}


def build_strict_annual_etf_bridge() -> dict[str, Any]:
    """Build the read-only 3B bridge from evidence-mature strategies to validation work."""

    if set(STRICT_ANNUAL_ETF_BRIDGE_KEYS) != set(FIRST_EVIDENCE_MATURE_CANDIDATE_KEYS):
        raise RuntimeError("Strict annual ETF bridge drifted from first evidence-mature group")

    inventory_rows = _inventory_by_key()
    bridge_rows: list[dict[str, Any]] = []
    for strategy_key in STRICT_ANNUAL_ETF_BRIDGE_KEYS:
        inventory = inventory_rows[strategy_key]
        detail = _BRIDGE_DETAIL_BY_KEY[strategy_key]
        bridge_rows.append(
            {
                "strategy_key": strategy_key,
                "display_name": STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key],
                "family": inventory["family"],
                "maturity_label": inventory["maturity_label"],
                "bridge_role": detail["bridge_role"],
                "target_use": detail["target_use"],
                "current_anchor": inventory["current_anchor"],
                "known_weakness": inventory["main_weakness"],
                "required_practical_validation_evidence": list(detail["required_practical_validation_evidence"]),
                "recommended_next_workflow": detail["recommended_next_workflow"],
                "route_boundary": _COMMON_ROUTE_BOUNDARY,
            }
        )

    deferred_exclusions = [
        strategy_key
        for strategy_key in STRATEGY_KEY_TO_DISPLAY_NAME
        if strategy_key not in set(STRICT_ANNUAL_ETF_BRIDGE_KEYS)
    ]

    return deepcopy(
        {
            "bridge_id": "strict_annual_etf_bridge_v1",
            "title": "Strict Annual + GTAA / Equal Weight Bridge",
            "status": "Read-only bridge",
            "candidate_intent": (
                "Practical Validation-ready bridge for the first evidence-mature group: "
                "strict annual factor candidates plus GTAA / Equal Weight ETF sleeves."
            ),
            "bridge_group_keys": list(STRICT_ANNUAL_ETF_BRIDGE_KEYS),
            "rows": bridge_rows,
            "validation_checklist": list(_VALIDATION_CHECKLIST),
            "next_workflow_steps": list(_NEXT_WORKFLOW_STEPS),
            "deferred_exclusions": deferred_exclusions,
            "storage_boundary": (
                "This bridge does not write registry rows, saved setups, run history, validation results, or final decisions."
            ),
            "route_boundary": _COMMON_ROUTE_BOUNDARY,
        }
    )
