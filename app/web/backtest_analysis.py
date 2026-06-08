from __future__ import annotations

import pandas as pd
import streamlit as st

from app.services.backtest_risk_on_governance import build_risk_on_momentum_governance
from app.services.backtest_strategy_bridge import build_strict_annual_etf_bridge
from app.services.backtest_strategy_evidence_inventory import (
    build_strategy_evidence_inventory,
    build_strategy_evidence_inventory_summary,
)
from app.web.reference_contextual_help import render_reference_contextual_help
from app.web.backtest_compare import render_compare_portfolio_workspace
from app.web.backtest_single_strategy import render_single_strategy_workspace
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_ANALYSIS_MODE_OPTIONS,
    BACKTEST_ANALYSIS_MODE_SINGLE,
    BACKTEST_LEGACY_ANALYSIS_MODE_COMPARE,
)


def _bridge_rows_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Strategy": row.get("display_name") or "-",
                "Bridge Role": row.get("bridge_role") or "-",
                "Target Use": row.get("target_use") or "-",
                "Required Validation Evidence": "; ".join(row.get("required_practical_validation_evidence") or []),
                "Known Weakness": row.get("known_weakness") or "-",
                "Recommended Workflow": row.get("recommended_next_workflow") or "-",
            }
            for row in rows
        ]
    )


def _governance_evidence_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Evidence": row.get("evidence") or "-",
                "Status": row.get("status") or "-",
                "Interpretation": row.get("interpretation") or "-",
            }
            for row in rows
        ]
    )


def _governance_modules_table(rows: list[dict[str, object]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Module": row.get("module") or "-",
                "Owner Surface": row.get("owner_surface") or "-",
                "Readiness": row.get("readiness") or "-",
                "Blocker": row.get("blocker") or "-",
                "Next Action": row.get("next_action") or "-",
            }
            for row in rows
        ]
    )


def _simple_rows(items: list[str], column_name: str) -> pd.DataFrame:
    return pd.DataFrame([{column_name: item} for item in items])


def _strategy_inventory_table(rows: list[dict[str, object]], *, compact: bool = False) -> pd.DataFrame:
    columns = [
        ("display_name", "Strategy"),
        ("family", "Family"),
        ("maturity_label", "Maturity"),
        ("intended_role", "Role"),
        ("current_anchor", "Evidence Anchor"),
        ("main_weakness", "Main Weakness"),
        ("next_action", "Next Action"),
    ]
    if not compact:
        columns.insert(3, ("product_lane", "Lane"))
        columns.insert(4, ("governance_status", "Governance"))
        columns.insert(5, ("validation_readiness", "Validation Readiness"))
        columns.insert(6, ("monitoring_readiness", "Monitoring Readiness"))
    return pd.DataFrame(
        [
            {label: row.get(key) or "-" for key, label in columns}
            for row in rows
        ]
    )


def _render_strategy_evidence_direction_panel() -> None:
    rows = build_strategy_evidence_inventory()
    summary = build_strategy_evidence_inventory_summary()
    first_group_rows = [
        row
        for row in rows
        if row["candidate_group"] == "First evidence-mature candidate group"
    ]

    with st.expander("Strategy Evidence Inventory / Direction Panel", expanded=True):
        st.caption(
            "Read-only Backtest Analysis guide. It does not run strategies, fetch providers, "
            "or write registries / saved setups / run history."
        )
        metric_cols = st.columns(4)
        metric_cols[0].metric("Catalog strategies", summary["strategy_count"])
        metric_cols[1].metric("Evidence-mature group", summary["first_evidence_mature_count"])
        metric_cols[2].metric("Quarterly prototypes", summary["quarterly_prototype_count"])
        metric_cols[3].metric("Risk-On governance", summary["risk_on_governance_status"])

        st.markdown("**First evidence-mature candidate group**")
        st.dataframe(
            _strategy_inventory_table(first_group_rows, compact=True),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**All catalog strategy maturity / next action**")
        st.dataframe(
            _strategy_inventory_table(rows),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**Next implementation scopes**")
        st.write(" / ".join(summary["next_scope_options"]))


def _render_strict_annual_etf_bridge_panel() -> None:
    bridge = build_strict_annual_etf_bridge()
    rows = bridge["rows"]

    with st.expander(bridge["title"], expanded=True):
        st.caption(bridge["candidate_intent"])
        metric_cols = st.columns(3)
        metric_cols[0].metric("Bridge strategies", len(rows))
        metric_cols[1].metric("Validation checks", len(bridge["validation_checklist"]))
        metric_cols[2].metric("Deferred strategies", len(bridge["deferred_exclusions"]))

        st.markdown("**Bridge role / validation handoff**")
        st.dataframe(
            _bridge_rows_table(rows),
            hide_index=True,
            width="stretch",
        )

        checklist_col, workflow_col = st.columns(2)
        with checklist_col:
            st.markdown("**Practical Validation checklist**")
            st.dataframe(
                _simple_rows(bridge["validation_checklist"], "Check"),
                hide_index=True,
                width="stretch",
            )
        with workflow_col:
            st.markdown("**Next workflow**")
            st.dataframe(
                _simple_rows(bridge["next_workflow_steps"], "Step"),
                hide_index=True,
                width="stretch",
            )

        st.caption(bridge["storage_boundary"])
        st.caption(bridge["route_boundary"])


def _render_risk_on_governance_panel() -> None:
    governance = build_risk_on_momentum_governance()

    with st.expander(governance["title"], expanded=True):
        st.caption(governance["summary"])
        metric_cols = st.columns(4)
        metric_cols[0].metric("Governance", str(governance["status"]).replace("Governance ", "").title())
        metric_cols[1].metric(
            "Practical Validation",
            "Disabled" if not governance["promoted_to_practical_validation"] else "Enabled",
        )
        metric_cols[2].metric(
            "Final Review",
            "Disabled" if not governance["promoted_to_final_review"] else "Enabled",
        )
        metric_cols[3].metric(
            "Monitoring Signal",
            "Disabled" if not governance["monitoring_signal_enabled"] else "Enabled",
        )

        st.markdown("**Research evidence available now**")
        st.dataframe(
            _governance_evidence_table(governance["research_evidence"]),
            hide_index=True,
            width="stretch",
        )

        st.markdown("**Governance modules required before promotion**")
        st.dataframe(
            _governance_modules_table(governance["required_modules"]),
            hide_index=True,
            width="stretch",
        )

        rules_col, workflow_col = st.columns(2)
        with rules_col:
            st.markdown("**Governance rules**")
            st.dataframe(
                _simple_rows(governance["governance_rules"], "Rule"),
                hide_index=True,
                width="stretch",
            )
        with workflow_col:
            st.markdown("**Next workflow**")
            st.dataframe(
                _simple_rows(governance["next_workflow_steps"], "Step"),
                hide_index=True,
                width="stretch",
            )

        st.caption(governance["storage_boundary"])
        st.caption(governance["route_boundary"])


def render_backtest_analysis_workspace() -> None:
    st.markdown("### Backtest Analysis")
    st.caption(
        "Single Strategy 또는 Portfolio Mix Builder로 1차 후보를 만들고, "
        "통과한 후보만 Practical Validation source로 보냅니다."
    )
    render_reference_contextual_help("backtest_analysis")
    _render_strategy_evidence_direction_panel()
    _render_strict_annual_etf_bridge_panel()
    _render_risk_on_governance_panel()
    current_mode = st.session_state.get("backtest_analysis_mode")
    if current_mode == BACKTEST_LEGACY_ANALYSIS_MODE_COMPARE:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_COMPARE
    elif current_mode not in BACKTEST_ANALYSIS_MODE_OPTIONS:
        st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
    mode = st.radio(
        "Analysis Mode",
        options=BACKTEST_ANALYSIS_MODE_OPTIONS,
        horizontal=True,
        key="backtest_analysis_mode",
        label_visibility="collapsed",
    )
    if mode == BACKTEST_ANALYSIS_MODE_COMPARE:
        render_compare_portfolio_workspace()
    else:
        if mode != BACKTEST_ANALYSIS_MODE_SINGLE:
            st.session_state.backtest_analysis_mode = BACKTEST_ANALYSIS_MODE_SINGLE
        render_single_strategy_workspace()
