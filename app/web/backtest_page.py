from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.web.backtest_state import (  # noqa: F401
    BACKTEST_WORKFLOW_PANEL_OPTIONS,
    QUALITY_STRICT_PRESETS,
    activate_backtest_workflow_panel,
    clear_backtest_preview_caches,
    init_backtest_state,
    request_backtest_panel,
    set_single_strategy_target_from_strategy_key,
)
from app.web.backtest_analysis import render_backtest_analysis_workspace
from app.web.backtest_compare import (
    _queue_current_candidate_compare_prefill,  # noqa: F401
    render_compare_portfolio_workspace,
)
from app.web.backtest_final_review import render_final_review_workspace
from app.web.backtest_portfolio_proposal import render_portfolio_proposal_workspace
from app.web.backtest_candidate_review import render_candidate_review_workspace
from app.web.backtest_practical_validation import render_practical_validation_workspace
from app.web.backtest_single_runner import _handle_backtest_run  # noqa: F401
from app.web.backtest_single_strategy import render_single_strategy_workspace
from app.web.backtest_workflow_routes import (
    BACKTEST_ANALYSIS_MODE_COMPARE,
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


BACKTEST_WORKFLOW_STAGE_DISPLAY = {
    BACKTEST_STAGE_ANALYSIS: "후보 분석 · Backtest Analysis",
    BACKTEST_STAGE_PRACTICAL_VALIDATION: "실전 검증 · Practical Validation",
    BACKTEST_STAGE_FINAL_REVIEW: "최종 검토 · Final Review",
}


def _backtest_workflow_stage_label(stage: str) -> str:
    return BACKTEST_WORKFLOW_STAGE_DISPLAY.get(stage, str(stage))


def _backtest_workflow_nav_css() -> str:
    return (
        """
<style>
/* bt-primary-nav: scoped override for the Backtest workflow st.pills selector. */
.st-key-backtest_workflow_active_panel [data-testid="stButtonGroup"] {
  margin: 0.42rem 0 1.08rem 0;
  padding: 0;
  border-bottom: 1px solid rgba(100, 116, 139, 0.24);
}
.st-key-backtest_workflow_active_panel div[data-baseweb="button-group"] {
  gap: 1.45rem;
  align-items: flex-end;
}
.st-key-backtest_workflow_active_panel [data-testid="stBaseButton-pills"],
.st-key-backtest_workflow_active_panel [data-testid="stBaseButton-pillsActive"] {
  min-height: 2.15rem;
  padding: 0 0 0.62rem 0;
  border: 0 !important;
  border-bottom: 2px solid transparent !important;
  border-radius: 0;
  background: transparent !important;
  color: rgba(100, 116, 139, 0.95);
  color: color-mix(in srgb, var(--text-color) 70%, transparent);
  box-shadow: none !important;
  font-weight: 650;
  letter-spacing: 0;
}
.st-key-backtest_workflow_active_panel [data-testid="stBaseButton-pillsActive"] {
  border-bottom-color: #ff4b4b !important;
  background: transparent !important;
  color: #ff4b4b !important;
  box-shadow: none !important;
}
.st-key-backtest_workflow_active_panel [data-testid="stBaseButton-pills"]:hover {
  color: #ff4b4b;
  background: transparent !important;
}
@media (max-width: 760px) {
  .st-key-backtest_workflow_active_panel [data-testid="stBaseButton-pills"],
  .st-key-backtest_workflow_active_panel [data-testid="stBaseButton-pillsActive"] {
    min-height: 2.1rem;
    padding-bottom: 0.55rem;
  }
}
</style>
"""
    )


# Render the Backtest workflow as primary navigation.
def _render_backtest_panel_selector() -> str:
    st.markdown("#### 후보 선정 흐름")
    st.caption("Backtest Analysis에서 후보를 만들고, Practical Validation에서 검증 근거를 만든 뒤, Final Review에서 Portfolio Monitoring 후보 여부를 판단합니다.")

    current_panel = str(st.session_state.get("backtest_active_panel") or BACKTEST_STAGE_ANALYSIS)
    if current_panel not in BACKTEST_WORKFLOW_PANEL_OPTIONS:
        current_panel = BACKTEST_STAGE_ANALYSIS
    if st.session_state.get("backtest_workflow_active_panel") not in BACKTEST_WORKFLOW_PANEL_OPTIONS:
        st.session_state.backtest_workflow_active_panel = current_panel
    st.markdown(_backtest_workflow_nav_css(), unsafe_allow_html=True)
    selected_panel = st.pills(
        "Backtest Workflow",
        BACKTEST_WORKFLOW_PANEL_OPTIONS,
        selection_mode="single",
        required=True,
        format_func=_backtest_workflow_stage_label,
        key="backtest_workflow_active_panel",
        on_change=activate_backtest_workflow_panel,
        label_visibility="collapsed",
        width="stretch",
    )
    if selected_panel in BACKTEST_WORKFLOW_PANEL_OPTIONS:
        st.session_state.backtest_active_stage = selected_panel
        st.session_state.backtest_active_panel = selected_panel
    return str(st.session_state.get("backtest_active_panel") or BACKTEST_STAGE_ANALYSIS)


def render_backtest_tab() -> None:
    init_backtest_state()

    active_panel = _render_backtest_panel_selector()

    if active_panel == BACKTEST_STAGE_ANALYSIS:
        render_backtest_analysis_workspace()
    elif active_panel == BACKTEST_STAGE_PRACTICAL_VALIDATION:
        render_practical_validation_workspace()
    elif active_panel == BACKTEST_STAGE_FINAL_REVIEW:
        render_final_review_workspace()
    elif active_panel == "Single Strategy":
        render_single_strategy_workspace()
    elif active_panel in {"Compare & Portfolio Builder", BACKTEST_ANALYSIS_MODE_COMPARE}:
        render_compare_portfolio_workspace()
    elif active_panel == "Candidate Review":
        render_candidate_review_workspace()
    elif active_panel == "Portfolio Proposal":
        render_portfolio_proposal_workspace()
    else:
        render_final_review_workspace()


if __name__ == "__main__":
    st.title("Backtest")
    render_backtest_tab()
