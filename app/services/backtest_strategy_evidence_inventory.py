from __future__ import annotations

from copy import deepcopy
from typing import Any

from app.services.backtest_strategy_catalog import STRATEGY_KEY_TO_DISPLAY_NAME


FIRST_EVIDENCE_MATURE_CANDIDATE_KEYS = {
    "equal_weight",
    "gtaa",
    "quality_snapshot_strict_annual",
    "value_snapshot_strict_annual",
    "quality_value_snapshot_strict_annual",
}

STRICT_QUARTERLY_PROTOTYPE_KEYS = {
    "quality_snapshot_strict_quarterly_prototype",
    "value_snapshot_strict_quarterly_prototype",
    "quality_value_snapshot_strict_quarterly_prototype",
}

_FIRST_EVIDENCE_GROUP = "First evidence-mature candidate group"
_NO_FIRST_GROUP = "Later evidence expansion"

_BASE_ROW_BY_KEY: dict[str, dict[str, Any]] = {
    "equal_weight": {
        "family": "ETF static basket",
        "intended_role": "Exposure sleeve / baseline",
        "maturity_group": "Evidence mature",
        "maturity_label": "Evidence mature sleeve",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library ETF replay supported",
        "validation_readiness": "Bridge-ready with GTAA / strict annual; standalone alpha is not the claim",
        "monitoring_readiness": "Requires Practical Validation and Final Review selected-route gate first",
        "current_anchor": "Durable Equal Weight report and sleeve interpretation",
        "main_weakness": "Standalone alpha / low-MDD gate is weak",
        "evidence_anchor": "reports/backtests/strategies/EQUAL_WEIGHT.md",
        "next_action": "Use as a Practical Validation bridge sleeve with GTAA / strict annual candidates",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance beyond existing Practical Validation and Final Review gates.",
        "candidate_group": _FIRST_EVIDENCE_GROUP,
        "tags": ["ETF", "baseline", "bridge"],
    },
    "gtaa": {
        "family": "ETF tactical allocation",
        "intended_role": "Low-MDD tactical sleeve",
        "maturity_group": "Evidence mature",
        "maturity_label": "Evidence mature",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library ETF replay supported",
        "validation_readiness": "Bridge-ready; still needs provider, cost, and cadence evidence in Practical Validation",
        "monitoring_readiness": "Requires Final Review selected-route gate before monitoring",
        "current_anchor": "Durable GTAA report and current candidate interpretation",
        "main_weakness": "Universe, interval, score horizon, and benchmark interpretation remain sensitive",
        "evidence_anchor": "reports/backtests/strategies/GTAA.md",
        "next_action": "Use as a Practical Validation defensive / tactical sleeve with strict annual candidates",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance beyond existing Practical Validation and Final Review gates.",
        "candidate_group": _FIRST_EVIDENCE_GROUP,
        "tags": ["ETF", "tactical", "bridge"],
    },
    "global_relative_strength": {
        "family": "ETF relative strength",
        "intended_role": "Price-only ETF momentum",
        "maturity_group": "Evidence expansion needed",
        "maturity_label": "Executable / evidence expansion",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "UI / saved replay smoke exists; Candidate Library key present",
        "validation_readiness": "Needs current candidate anchor before Practical Validation emphasis",
        "monitoring_readiness": "Deferred until ETF evidence expansion and Final Review gate",
        "current_anchor": "Runtime and UI replay smoke reports",
        "main_weakness": "Current candidate hub and weakness follow-up are thin",
        "evidence_anchor": "reports/backtests/validation/runtime/GLOBAL_RELATIVE_STRENGTH_RUNTIME_SMOKE.md",
        "next_action": "Open ETF evidence expansion and write current anchor / weakness report",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance, but evidence depth is not yet GTAA-level.",
        "candidate_group": _NO_FIRST_GROUP,
        "tags": ["ETF", "momentum", "evidence-expansion"],
    },
    "risk_parity_trend": {
        "family": "ETF defensive allocation",
        "intended_role": "Volatility-aware defensive component",
        "maturity_group": "Early evidence",
        "maturity_label": "Low evidence",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library ETF replay supported",
        "validation_readiness": "Needs rerun matrix and strategy hub before Practical Validation emphasis",
        "monitoring_readiness": "Deferred until evidence expansion and Final Review gate",
        "current_anchor": "Runtime exposure exists, durable current report is limited",
        "main_weakness": "Current anchor, report depth, and low-vol overweight evidence are weak",
        "evidence_anchor": "Backtest runtime and Candidate Library support",
        "next_action": "Open ETF evidence expansion with rerun matrix and defensive role report",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance, but candidate evidence is not yet mature.",
        "candidate_group": _NO_FIRST_GROUP,
        "tags": ["ETF", "defensive", "evidence-expansion"],
    },
    "dual_momentum": {
        "family": "ETF tactical allocation",
        "intended_role": "Concentrated momentum switch",
        "maturity_group": "Early evidence",
        "maturity_label": "Low evidence",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library ETF replay supported",
        "validation_readiness": "Needs concentrated-momentum risk evidence before Practical Validation emphasis",
        "monitoring_readiness": "Deferred until evidence expansion and Final Review gate",
        "current_anchor": "Runtime exposure exists, durable current report is limited",
        "main_weakness": "Top-1 concentration, whipsaw, and trend-turn risk need explicit evidence",
        "evidence_anchor": "Backtest runtime and Candidate Library support",
        "next_action": "Open ETF evidence expansion with cash proxy, benchmark, and guardrail evidence",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance, but candidate evidence is not yet mature.",
        "candidate_group": _NO_FIRST_GROUP,
        "tags": ["ETF", "momentum", "evidence-expansion"],
    },
    "risk_on_momentum_5d": {
        "family": "Daily stock swing",
        "intended_role": "Short-term research lane",
        "maturity_group": "Research lane",
        "maturity_label": "Research evidence / governance deferred",
        "product_lane": "Backtest Analysis research lane",
        "runtime_support": "Supported",
        "compare_support": "Supported as research comparison",
        "replay_support": "History payload restore tests and generated artifacts exist",
        "validation_readiness": "Not Practical Validation-ready without a Daily Swing governance design",
        "monitoring_readiness": "Governance deferred; not a Portfolio Monitoring signal",
        "current_anchor": "Risk-On Momentum 5D V1/V2 research lane and Swing Detail evidence",
        "main_weakness": "Validation, final review, and daily monitoring governance are not implemented",
        "evidence_anchor": "tasks/active/risk-on-momentum-5d-v2/",
        "next_action": "Open a separate Risk-On Momentum governance design before any validation or monitoring route",
        "governance_status": "Deferred",
        "governance_note": "Governance deferred: keep this as a Backtest Analysis research lane until a Daily Swing policy is approved.",
        "candidate_group": "Research governance deferred",
        "tags": ["daily-swing", "research-lane", "governance-deferred"],
    },
    "quality_snapshot": {
        "family": "Broad factor prototype",
        "intended_role": "Early broad research path",
        "maturity_group": "Prototype",
        "maturity_label": "Legacy broad prototype",
        "product_lane": "Backtest Analysis legacy research path",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "History payload compatibility exists; not a primary candidate lifecycle",
        "validation_readiness": "Not a primary Practical Validation candidate",
        "monitoring_readiness": "Deferred; use strict annual family for candidate work",
        "current_anchor": "Legacy broad quality runtime path",
        "main_weakness": "Broad prototype is less controlled than strict annual variants",
        "evidence_anchor": "Backtest strict family split documentation",
        "next_action": "Prefer strict annual Quality for Practical Validation candidate work",
        "governance_status": "Legacy research",
        "governance_note": "Keep as broad research compatibility, not a new governance route.",
        "candidate_group": "Legacy prototype",
        "tags": ["factor", "legacy", "prototype"],
    },
    "quality_snapshot_strict_annual": {
        "family": "Factor equity",
        "intended_role": "Quality-only annual reference / stabilizer",
        "maturity_group": "Evidence mature",
        "maturity_label": "Evidence mature",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library strict annual replay supported",
        "validation_readiness": "Bridge-ready; requires Practical Validation provider, PIT, liquidity, and benchmark checks",
        "monitoring_readiness": "Requires Final Review selected-route gate before monitoring",
        "current_anchor": "Quality strict annual strategy hub",
        "main_weakness": "Quality factor alone is weaker and benchmark / overlay dependent",
        "evidence_anchor": "reports/backtests/strategies/QUALITY_STRICT_ANNUAL.md",
        "next_action": "Use in Practical Validation as reference / stabilizer within the strict annual bridge group",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance beyond existing Practical Validation and Final Review gates.",
        "candidate_group": _FIRST_EVIDENCE_GROUP,
        "tags": ["factor", "strict-annual", "bridge"],
    },
    "value_snapshot_strict_annual": {
        "family": "Factor equity",
        "intended_role": "Value annual return engine",
        "maturity_group": "Evidence mature",
        "maturity_label": "Evidence mature",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library strict annual replay supported",
        "validation_readiness": "Bridge-ready; requires Practical Validation drawdown, liquidity, and concentration checks",
        "monitoring_readiness": "Requires Final Review selected-route gate before monitoring",
        "current_anchor": "Value strict annual strategy hub",
        "main_weakness": "Strong raw return but MDD and review gaps remain material",
        "evidence_anchor": "reports/backtests/strategies/VALUE_STRICT_ANNUAL.md",
        "next_action": "Use in Practical Validation as return engine while tracking downside open review",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance beyond existing Practical Validation and Final Review gates.",
        "candidate_group": _FIRST_EVIDENCE_GROUP,
        "tags": ["factor", "strict-annual", "bridge"],
    },
    "quality_value_snapshot_strict_annual": {
        "family": "Factor equity",
        "intended_role": "Blended factor annual strategy",
        "maturity_group": "Evidence mature",
        "maturity_label": "Evidence mature",
        "product_lane": "Backtest Analysis candidate source",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate Library strict annual replay supported",
        "validation_readiness": "Bridge-ready; requires Practical Validation capacity, concentration, factor overlap, and drawdown checks",
        "monitoring_readiness": "Requires Final Review selected-route gate before monitoring",
        "current_anchor": "Quality + Value strict annual strategy hub",
        "main_weakness": "Still review-required and better suited to small-capital trial framing",
        "evidence_anchor": "reports/backtests/strategies/QUALITY_VALUE_STRICT_ANNUAL.md",
        "next_action": "Use in Practical Validation as first core bridge candidate with GTAA / Equal Weight sleeves",
        "governance_status": "Standard workflow",
        "governance_note": "No special governance beyond existing Practical Validation and Final Review gates.",
        "candidate_group": _FIRST_EVIDENCE_GROUP,
        "tags": ["factor", "strict-annual", "bridge"],
    },
    "quality_snapshot_strict_quarterly_prototype": {
        "family": "Factor equity prototype",
        "intended_role": "Quarterly quality contract validation",
        "maturity_group": "Prototype",
        "maturity_label": "Prototype / contract-smoke",
        "product_lane": "Backtest Analysis prototype lane",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate lifecycle incomplete",
        "validation_readiness": "Prototype only; not strict annual candidate maturity",
        "monitoring_readiness": "Deferred until quarterly maturation",
        "current_anchor": "Quarterly contract runtime smoke",
        "main_weakness": "Filing lag, PIT quarterly rows, replay, and validation evidence are incomplete",
        "evidence_anchor": "reports/backtests/validation/runtime/QUARTERLY_CONTRACT_RUNTIME_SMOKE.md",
        "next_action": "Keep prototype label and open quarterly maturation later",
        "governance_status": "Prototype",
        "governance_note": "Runtime contract smoke only; do not promote to annual strict readiness.",
        "candidate_group": "Quarterly prototype maturation",
        "tags": ["factor", "quarterly", "prototype"],
    },
    "value_snapshot_strict_quarterly_prototype": {
        "family": "Factor equity prototype",
        "intended_role": "Quarterly value contract validation",
        "maturity_group": "Prototype",
        "maturity_label": "Prototype / contract-smoke",
        "product_lane": "Backtest Analysis prototype lane",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate lifecycle incomplete",
        "validation_readiness": "Prototype only; not strict annual candidate maturity",
        "monitoring_readiness": "Deferred until quarterly maturation",
        "current_anchor": "Quarterly contract runtime smoke",
        "main_weakness": "Filing lag, PIT quarterly rows, replay, and validation evidence are incomplete",
        "evidence_anchor": "reports/backtests/validation/runtime/QUARTERLY_CONTRACT_RUNTIME_SMOKE.md",
        "next_action": "Keep prototype label and open quarterly maturation later",
        "governance_status": "Prototype",
        "governance_note": "Runtime contract smoke only; do not promote to annual strict readiness.",
        "candidate_group": "Quarterly prototype maturation",
        "tags": ["factor", "quarterly", "prototype"],
    },
    "quality_value_snapshot_strict_quarterly_prototype": {
        "family": "Factor equity prototype",
        "intended_role": "Quarterly blended factor contract validation",
        "maturity_group": "Prototype",
        "maturity_label": "Prototype / contract-smoke",
        "product_lane": "Backtest Analysis prototype lane",
        "runtime_support": "Supported",
        "compare_support": "Supported",
        "replay_support": "Candidate lifecycle incomplete",
        "validation_readiness": "Prototype only; not strict annual candidate maturity",
        "monitoring_readiness": "Deferred until quarterly maturation",
        "current_anchor": "Quarterly contract runtime smoke",
        "main_weakness": "Filing lag, PIT quarterly rows, replay, and validation evidence are incomplete",
        "evidence_anchor": "reports/backtests/validation/runtime/QUARTERLY_CONTRACT_RUNTIME_SMOKE.md",
        "next_action": "Keep prototype label and open quarterly maturation later",
        "governance_status": "Prototype",
        "governance_note": "Runtime contract smoke only; do not promote to annual strict readiness.",
        "candidate_group": "Quarterly prototype maturation",
        "tags": ["factor", "quarterly", "prototype"],
    },
}


def _validate_catalog_coverage() -> None:
    catalog_keys = set(STRATEGY_KEY_TO_DISPLAY_NAME)
    row_keys = set(_BASE_ROW_BY_KEY)
    missing = sorted(catalog_keys - row_keys)
    extra = sorted(row_keys - catalog_keys)
    if missing or extra:
        parts: list[str] = []
        if missing:
            parts.append(f"missing rows for catalog keys: {', '.join(missing)}")
        if extra:
            parts.append(f"rows without catalog keys: {', '.join(extra)}")
        raise RuntimeError("Strategy evidence inventory catalog drift: " + "; ".join(parts))


def build_strategy_evidence_inventory() -> list[dict[str, Any]]:
    """Return a read-only product interpretation row for each strategy catalog key."""

    _validate_catalog_coverage()
    rows: list[dict[str, Any]] = []
    for strategy_key, display_name in STRATEGY_KEY_TO_DISPLAY_NAME.items():
        row = deepcopy(_BASE_ROW_BY_KEY[strategy_key])
        row["strategy_key"] = strategy_key
        row["display_name"] = display_name
        rows.append(row)
    return rows


def build_strategy_evidence_inventory_summary() -> dict[str, Any]:
    rows = build_strategy_evidence_inventory()
    maturity_counts: dict[str, int] = {}
    candidate_group_counts: dict[str, int] = {}
    for row in rows:
        maturity_counts[row["maturity_group"]] = maturity_counts.get(row["maturity_group"], 0) + 1
        candidate_group_counts[row["candidate_group"]] = candidate_group_counts.get(row["candidate_group"], 0) + 1

    return {
        "strategy_count": len(rows),
        "first_evidence_mature_count": len(FIRST_EVIDENCE_MATURE_CANDIDATE_KEYS),
        "risk_on_governance_status": _BASE_ROW_BY_KEY["risk_on_momentum_5d"]["governance_status"],
        "quarterly_prototype_count": len(STRICT_QUARTERLY_PROTOTYPE_KEYS),
        "maturity_counts": maturity_counts,
        "candidate_group_counts": candidate_group_counts,
        "first_evidence_mature_keys": sorted(FIRST_EVIDENCE_MATURE_CANDIDATE_KEYS),
        "next_scope_options": [
            "Strict annual + GTAA / Equal Weight bridge",
            "Risk-On Momentum governance",
            "ETF evidence expansion",
            "Quarterly prototype maturation",
        ],
    }
