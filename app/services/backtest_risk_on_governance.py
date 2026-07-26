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
        "status": "Compact boundary implemented",
        "interpretation": "Raw rows stay generated while JSON-safe compact evidence enters downstream validation.",
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
        "readiness": "Implemented",
        "blocker": "",
        "next_action": "Review trade count, holding period, turnover, cost, macro, robustness, and universe-bias rows.",
    },
    {
        "module_key": "final_review_selected_route_rule",
        "module": "Final Review selected-route rule",
        "owner_surface": "Final Review",
        "readiness": "Implemented",
        "blocker": "",
        "next_action": "Require compact evidence and carry REVIEW limitations into the selected-route record.",
    },
    {
        "module_key": "portfolio_monitoring_daily_policy",
        "module": "Portfolio Monitoring daily review cadence / signal policy",
        "owner_surface": "Operations > Portfolio Monitoring",
        "readiness": "Implemented",
        "blocker": "",
        "next_action": "Review after market close; expire after one market day; keep manual recheck and no-auto-order.",
    },
    {
        "module_key": "artifact_trade_log_storage_boundary",
        "module": "Artifact / trade log storage boundary",
        "owner_surface": "Runtime / reports / registries",
        "readiness": "Implemented",
        "blocker": "",
        "next_action": "Keep raw trade/scanner rows generated and pass only compact JSON-safe metadata downstream.",
    },
    {
        "module_key": "universe_survivorship_review",
        "module": "Universe / survivorship assumption review",
        "owner_surface": "Backtest Analysis / Practical Validation",
        "readiness": "Implemented",
        "blocker": "",
        "next_action": "Treat current membership and missing delisting coverage as explicit REVIEW limitations.",
    },
]

_GOVERNANCE_RULES = [
    "Promote Risk-On Momentum 5D through the Daily Swing-specific Practical Validation module.",
    "Keep downstream work as review evidence, not an automatic monitoring signal.",
    "Use the Daily Swing selected-route policy in addition to generic Final Review gates.",
    "Do not write validation results, final decisions, monitoring logs, registries, saved setups, or run history from this panel.",
    "Portfolio Monitoring integration, if later approved, must remain manual-review and no-live-order by default.",
]

_NEXT_WORKFLOW_STEPS = [
    "Run the compact Daily Swing evidence and current-runtime replay.",
    "Acknowledge survivorship/PIT limitations in Final Review.",
    "Use daily-after-close manual review and one-market-day stale handling in Monitoring.",
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
            "status": "Governance implemented",
            "lane": "Daily Swing validation and monitoring lane",
            "summary": (
                "Risk-On Momentum 5D carries compact Daily Swing evidence through Practical Validation "
                "and Final Review into manual, stale-aware Portfolio Monitoring."
            ),
            "promoted_to_practical_validation": True,
            "promoted_to_final_review": True,
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
                "Daily Swing selected-route is manual-review only; evidence is not an automatic Portfolio "
                "Monitoring signal, live approval, broker order, or auto rebalance."
            ),
        }
    )
