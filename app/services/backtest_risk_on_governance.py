from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME


RISK_ON_MOMENTUM_STRATEGY_KEY = "risk_on_momentum_5d"

_RESEARCH_EVIDENCE = [
    {
        "evidence": "Swing Detail",
        "status": "Available",
        "interpretation": "Backtest Analysis shows the Daily Swing result context and assumptions.",
    },
    {
        "evidence": "trade log",
        "status": "Available",
        "interpretation": "Trade-level research evidence exists, but it is not yet a selected-route audit record.",
    },
    {
        "evidence": "scanner",
        "status": "Available",
        "interpretation": "Scanner output supports research review, not automated daily monitoring.",
    },
    {
        "evidence": "comparison / sensitivity / stability",
        "status": "Available",
        "interpretation": "V2 analysis can support review evidence once governance criteria are defined.",
    },
    {
        "evidence": "trade causes / quality warnings",
        "status": "Available",
        "interpretation": "Cause and warning rows help explain risk, but do not replace validation gates.",
    },
    {
        "evidence": "generated swing artifacts",
        "status": "Boundary needed",
        "interpretation": "Generated artifacts need storage and audit policy before downstream workflow use.",
    },
]

_REQUIRED_MODULES = [
    {
        "module_key": "research_evidence_review",
        "module": "Backtest Analysis research evidence review",
        "owner_surface": "Backtest Analysis",
        "readiness": "Available for review",
        "blocker": "",
        "next_action": "Use Swing Detail and generated artifacts as research context only.",
    },
    {
        "module_key": "daily_swing_practical_validation",
        "module": "Daily Swing Practical Validation module",
        "owner_surface": "Practical Validation",
        "readiness": "Needs design",
        "blocker": "Existing Practical Validation modules are built around candidate sources and longer rebalance horizons.",
        "next_action": "Define Daily Swing evidence rows for trade count, holding period, turnover, cost, macro filter, and failed-trade quality.",
    },
    {
        "module_key": "final_review_selected_route_rule",
        "module": "Final Review selected-route rule",
        "owner_surface": "Final Review",
        "readiness": "Deferred",
        "blocker": "No approved rule says when short-term swing research can become a selected portfolio candidate.",
        "next_action": "Design a selected-route policy that starts as review evidence and blocks automatic approval.",
    },
    {
        "module_key": "portfolio_monitoring_daily_policy",
        "module": "Portfolio Monitoring daily review cadence / signal policy",
        "owner_surface": "Operations > Portfolio Monitoring",
        "readiness": "Deferred",
        "blocker": "Daily signals need cadence, stale signal handling, manual review, and no-auto-order boundaries.",
        "next_action": "Define daily review cadence and signal expiration before any monitoring surface integration.",
    },
    {
        "module_key": "artifact_trade_log_storage_boundary",
        "module": "Artifact / trade log storage boundary",
        "owner_surface": "Runtime / reports / registries",
        "readiness": "Needs design",
        "blocker": "Generated swing artifacts are not compact registry evidence and should not be promoted by path alone.",
        "next_action": "Specify which compact artifact metadata can enter validation records and which raw artifacts stay generated.",
    },
    {
        "module_key": "universe_survivorship_review",
        "module": "Universe / survivorship assumption review",
        "owner_surface": "Backtest Analysis / Practical Validation",
        "readiness": "Needs design",
        "blocker": "S&P 500 / Top1000 / Top2000 / manual stock universes need explicit survivorship and listing assumptions.",
        "next_action": "Add review criteria for universe source, point-in-time membership, delisting, and symbol freshness evidence.",
    },
]

_GOVERNANCE_RULES = [
    "Keep Risk-On Momentum 5D in the Backtest Analysis Daily Swing research lane until a governance task explicitly promotes it.",
    "Start downstream work as review evidence, not an automatic monitoring signal.",
    "Do not reuse monthly / annual selected-route gates without a Daily Swing-specific Practical Validation module.",
    "Do not write validation results, final decisions, monitoring logs, registries, saved setups, or run history from this panel.",
    "Portfolio Monitoring integration, if later approved, must remain manual-review and no-live-order by default.",
]

_NEXT_WORKFLOW_STEPS = [
    "Define the Daily Swing Practical Validation module contract.",
    "Define the Final Review selected-route blocker / review-required policy for short holding-period strategies.",
    "Define artifact and trade-log compact evidence storage boundaries.",
    "Define Portfolio Monitoring daily review cadence before showing any daily signal.",
]


def build_risk_on_momentum_governance() -> dict[str, Any]:
    """Build a read-only governance readiness board for the Daily Swing research lane."""

    display_name = STRATEGY_KEY_TO_DISPLAY_NAME[RISK_ON_MOMENTUM_STRATEGY_KEY]
    return deepcopy(
        {
            "governance_id": "risk_on_momentum_5d_governance_v1",
            "title": "Risk-On Momentum 5D Governance",
            "strategy_key": RISK_ON_MOMENTUM_STRATEGY_KEY,
            "display_name": display_name,
            "status": "Governance deferred",
            "lane": "Backtest Analysis research lane",
            "summary": (
                "Risk-On Momentum 5D has mature Daily Swing research evidence, but it is not promoted "
                "to Practical Validation, Final Review, or Portfolio Monitoring until Daily Swing governance is approved."
            ),
            "promoted_to_practical_validation": False,
            "promoted_to_final_review": False,
            "monitoring_signal_enabled": False,
            "research_evidence": _RESEARCH_EVIDENCE,
            "required_modules": _REQUIRED_MODULES,
            "governance_rules": _GOVERNANCE_RULES,
            "next_workflow_steps": _NEXT_WORKFLOW_STEPS,
            "storage_boundary": (
                "Read-only governance board; does not write registries, saved setups, validation results, "
                "final decisions, monitoring logs, run history, or generated artifacts."
            ),
            "route_boundary": (
                "Backtest Analysis research lane only; not Practical Validation-ready, not Final Review-selected, "
                "and not a Portfolio Monitoring signal."
            ),
        }
    )
