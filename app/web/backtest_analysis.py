from __future__ import annotations

import pandas as pd
import streamlit as st

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


def render_backtest_analysis_workspace() -> None:
    st.markdown("### Backtest Analysis")
    st.caption(
        "Single Strategy 또는 Portfolio Mix Builder로 1차 후보를 만들고, "
        "통과한 후보만 Practical Validation source로 보냅니다."
    )
    render_reference_contextual_help("backtest_analysis")
    _render_strategy_evidence_direction_panel()
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
