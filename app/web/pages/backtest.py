from __future__ import annotations

import sys
from pathlib import Path

import streamlit as st

PROJECT_ROOT = Path(__file__).resolve().parents[3]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from app.web.backtest_common import (  # noqa: F401
    BACKTEST_WORKFLOW_PANEL_OPTIONS,
    QUALITY_STRICT_PRESETS,
    _activate_backtest_workflow_panel,
    _init_backtest_state,
    _request_backtest_panel,
    _set_single_strategy_target_from_strategy_key,
    clear_backtest_preview_caches,
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
    BACKTEST_STAGE_ANALYSIS,
    BACKTEST_STAGE_FINAL_REVIEW,
    BACKTEST_STAGE_PRACTICAL_VALIDATION,
)


# Render the Backtest workflow as primary navigation.
def _render_backtest_panel_selector() -> str:
    st.markdown("#### 후보 선정 흐름")
    st.caption("Backtest Analysis에서 후보를 만들고, Practical Validation에서 검증한 뒤, Final Review에서 최종 판단합니다.")

    if hasattr(st, "segmented_control"):
        st.segmented_control(
            "Backtest Workflow",
            options=BACKTEST_WORKFLOW_PANEL_OPTIONS,
            selection_mode="single",
            required=True,
            key="backtest_workflow_active_panel",
            on_change=_activate_backtest_workflow_panel,
            label_visibility="collapsed",
            width="stretch",
        )
    else:
        st.radio(
            "Backtest Workflow",
            options=BACKTEST_WORKFLOW_PANEL_OPTIONS,
            horizontal=True,
            key="backtest_workflow_active_panel",
            on_change=_activate_backtest_workflow_panel,
            label_visibility="collapsed",
        )
    st.caption("과거 실행 기록은 `Operations > Backtest Run History`, 선정 이후 관리는 `Operations > Selected Portfolio Dashboard`에서 확인합니다.")
    return str(st.session_state.get("backtest_active_panel") or BACKTEST_STAGE_ANALYSIS)


def render_backtest_tab() -> None:
    _init_backtest_state()

    with st.expander("Backtest 사용 안내", expanded=False):
        st.markdown(
            """
            - `Backtest Analysis`: Single Strategy, Compare, 저장된 비중 조합 replay로 후보 source를 만듭니다.
            - `Practical Validation`: 선택한 단일 후보, Compare 후보, Saved Mix를 실전 검증 자료로 구조화합니다.
            - `Final Review`: 검증 자료를 기준으로 최종 선정 / 보류 / 거절 / 재검토를 한 번만 기록합니다.
            - `Operations > Backtest Run History`: 저장된 실행 결과를 다시 보고, `Run Again` 또는 `Load Into Form`을 사용하는 운영 도구입니다.
            - `Operations > Selected Portfolio Dashboard`: Final Review에서 선정된 V2 decision을 읽어 선정 이후 성과와 review signal을 확인합니다.
            - `Load Into Form`을 누르면 저장된 입력값이 `Single Strategy` 화면으로 자동 이동하며 다시 채워집니다.
            - `quarterly strict prototype` 전략은 현재 **research-only** 경로입니다.
            """
        )
        st.caption(
            "`늦은 active start`는 요청한 시작일에는 아직 usable한 statement shadow가 부족해서, "
            "실제 첫 보유/선택이 그보다 뒤에서 시작되는 상황을 뜻합니다."
        )

    active_panel = _render_backtest_panel_selector()

    if active_panel == BACKTEST_STAGE_ANALYSIS:
        render_backtest_analysis_workspace()
    elif active_panel == BACKTEST_STAGE_PRACTICAL_VALIDATION:
        render_practical_validation_workspace()
    elif active_panel == BACKTEST_STAGE_FINAL_REVIEW:
        render_final_review_workspace()
    elif active_panel == "Single Strategy":
        render_single_strategy_workspace()
    elif active_panel == "Compare & Portfolio Builder":
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
