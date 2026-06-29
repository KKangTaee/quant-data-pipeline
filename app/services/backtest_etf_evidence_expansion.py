from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME


ETF_EVIDENCE_EXPANSION_TARGET_KEYS = (
    "global_relative_strength",
    "risk_parity_trend",
    "dual_momentum",
)

ETF_EVIDENCE_BASELINE_REFERENCE_KEYS = ["gtaa", "equal_weight"]

_COMMON_ROUTE_BOUNDARY = (
    "Backtest Analysis evidence-expansion view only; Practical Validation owns evidence results, "
    "Final Review owns selected-route decisions, and Portfolio Monitoring remains read-only."
)

_DETAIL_BY_KEY: dict[str, dict[str, Any]] = {
    "global_relative_strength": {
        "family": "ETF relative strength",
        "priority": "First ETF expansion target",
        "current_anchor": "Core/runtime validation, UI replay smoke, saved replay smoke, and Candidate Library key exist.",
        "near_miss": "Price-only ETF momentum is clear and replay-connected, so it is the closest non-GTAA ETF follow-up.",
        "not_ready_reason": "Current candidate hub and GTAA-level weakness report are still missing.",
        "evidence_gap": "Price freshness, excluded ticker handling, cash proxy handling, provider operability, and benchmark parity need a single anchor.",
        "required_evidence": [
            "DB-backed smoke / rerun matrix with price freshness and excluded ticker notes",
            "Cash proxy handling and benchmark / comparator parity",
            "ETF provider operability, cost, liquidity, and capacity evidence",
            "Current candidate hub with explicit weakness and near-miss interpretation",
        ],
        "next_workflow": (
            "Write the GRS strategy hub / current anchor first, then run Practical Validation only after the rerun matrix and provider evidence are available."
        ),
    },
    "risk_parity_trend": {
        "family": "ETF defensive allocation",
        "priority": "Second ETF expansion target",
        "current_anchor": "Runtime exposure and Candidate Library ETF replay support exist.",
        "near_miss": "Defensive allocation concept is strong, but low-vol overweight and correlation-regime behavior need evidence.",
        "not_ready_reason": "Current anchor, rerun matrix, and durable report depth are not yet sufficient.",
        "evidence_gap": "Volatility window sensitivity, correlation regime, stale ETF data, provider coverage, and benchmark fit are not normalized.",
        "required_evidence": [
            "Volatility window sensitivity and correlation regime matrix",
            "ETF provider freshness, operability, holdings, exposure, and liquidity evidence",
            "Benchmark / comparator parity and stale ETF data handling",
            "Defensive role report that explains low-vol overweight risk",
        ],
        "next_workflow": (
            "Build the defensive role report and rerun matrix before using Practical Validation as more than an exploratory check."
        ),
    },
    "dual_momentum": {
        "family": "ETF tactical allocation",
        "priority": "Third ETF expansion target",
        "current_anchor": "Runtime exposure and Candidate Library ETF replay support exist.",
        "near_miss": "Simple tactical switch is easy to explain, but concentrated top-1 exposure can dominate outcomes.",
        "not_ready_reason": "Top-1 concentration, whipsaw, trend-turn risk, and cash proxy policy are not yet explicit enough.",
        "evidence_gap": "Cash proxy, benchmark, guardrail, turnover / cost, and concentrated momentum risk evidence need a shared anchor.",
        "required_evidence": [
            "Cash proxy handling and benchmark / comparator parity",
            "Concentrated momentum top-1 exposure and whipsaw risk report",
            "Guardrail, turnover, transaction cost, and trend-turn sensitivity evidence",
            "ETF provider operability, liquidity, and stale-data evidence",
        ],
        "next_workflow": (
            "Document concentrated momentum risk and guardrail evidence before emphasizing this strategy in Practical Validation."
        ),
    },
}

_NEXT_WORKFLOW_STEPS = [
    "Start with Global Relative Strength because runtime / UI replay smoke already exists.",
    "Create a current anchor / near-miss / not-ready reason note for each target ETF strategy before registry promotion.",
    "Run DB-backed rerun matrix and provider evidence collection in a later approved task.",
    "Use Practical Validation only after the current anchor and ETF operability / cost evidence are available.",
]


def build_etf_evidence_expansion() -> dict[str, Any]:
    """Build the read-only 3D ETF evidence expansion board for non-GTAA ETF strategies."""

    rows: list[dict[str, Any]] = []
    for strategy_key in ETF_EVIDENCE_EXPANSION_TARGET_KEYS:
        detail = _DETAIL_BY_KEY[strategy_key]
        rows.append(
            {
                "strategy_key": strategy_key,
                "display_name": STRATEGY_KEY_TO_DISPLAY_NAME[strategy_key],
                "family": detail["family"],
                "priority": detail["priority"],
                "current_anchor": detail["current_anchor"],
                "near_miss": detail["near_miss"],
                "not_ready_reason": detail["not_ready_reason"],
                "evidence_gap": detail["evidence_gap"],
                "required_evidence": list(detail["required_evidence"]),
                "next_workflow": detail["next_workflow"],
                "route_boundary": _COMMON_ROUTE_BOUNDARY,
            }
        )

    return deepcopy(
        {
            "expansion_id": "etf_evidence_expansion_v1",
            "title": "ETF Evidence Expansion",
            "status": "Read-only evidence expansion",
            "target_strategy_keys": list(ETF_EVIDENCE_EXPANSION_TARGET_KEYS),
            "baseline_reference_keys": list(ETF_EVIDENCE_BASELINE_REFERENCE_KEYS),
            "summary": (
                "GRS / Risk Parity / Dual Momentum are executable ETF strategies, but they need current anchors, "
                "provider / cost evidence, and weakness reports before they are treated like GTAA-level candidates."
            ),
            "rows": rows,
            "next_workflow_steps": list(_NEXT_WORKFLOW_STEPS),
            "creates_current_candidate": False,
            "runs_backtests": False,
            "writes_validation_results": False,
            "storage_boundary": (
                "Read-only evidence expansion board; does not write the Current candidate registry, saved setups, "
                "run history, validation results, final decisions, monitoring logs, or provider snapshots."
            ),
            "route_boundary": _COMMON_ROUTE_BOUNDARY,
        }
    )
