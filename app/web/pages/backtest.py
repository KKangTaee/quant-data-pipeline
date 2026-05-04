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
from app.web.backtest_compare import (
    _queue_current_candidate_compare_prefill,  # noqa: F401
    render_compare_portfolio_workspace,
)
from app.web.backtest_final_review import render_final_review_workspace
from app.web.backtest_portfolio_proposal import render_portfolio_proposal_workspace
from app.web.backtest_post_selection_guide import render_post_selection_guide_workspace
from app.web.backtest_candidate_review import render_candidate_review_workspace
from app.web.backtest_single_runner import _handle_backtest_run  # noqa: F401
from app.web.backtest_single_strategy import render_single_strategy_workspace


# Render the Backtest workflow as primary navigation.
def _render_backtest_panel_selector() -> str:
    st.markdown("#### 후보 검토 흐름")
    st.caption("전략 실행에서 후보 검토, Portfolio Proposal, Final Review, 최종 투자 지침 확인까지 이어지는 주 흐름입니다.")

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
    st.caption("과거 실행 기록은 `Operations > Backtest Run History`, 저장 후보 재검토는 `Operations > Candidate Library`에서 관리합니다.")
    return str(st.session_state.get("backtest_active_panel") or "Single Strategy")


def render_backtest_tab() -> None:
    _init_backtest_state()

    with st.expander("Backtest 사용 안내", expanded=False):
        st.markdown(
            """
            - `Single Strategy`: 전략 1개를 실행하고 결과를 바로 확인합니다.
            - `Compare & Portfolio Builder`: 여러 전략을 같은 기간으로 비교하고 후보 근거를 확인합니다.
            - `Candidate Review`: 후보 초안, Review Note, registry 저장, Pre-Live 운영 기록, Portfolio Proposal 이동 판단을 순서대로 처리합니다.
            - `Portfolio Proposal`: 후보 여러 개를 목적 / 역할 / 비중 근거와 함께 묶는 제안 초안을 만듭니다.
            - `Final Review`: 단일 후보 또는 저장된 proposal을 검증 근거와 함께 최종 선정 / 보류 / 거절 / 재검토로 판단합니다.
            - `Post-Selection Guide`: 최종 선정 후보의 투자 가능성과 리밸런싱 / 축소 / 중단 / 재검토 운영 전 기준을 확인합니다.
            - `Operations > Backtest Run History`: 저장된 실행 결과를 다시 보고, `Run Again` 또는 `Load Into Form`을 사용하는 운영 도구입니다.
            - `Operations > Candidate Library`: registry / Pre-Live 후보를 다시 열어보고, 저장된 contract로 result curve를 재생성합니다.
            - `Load Into Form`을 누르면 저장된 입력값이 `Single Strategy` 화면으로 자동 이동하며 다시 채워집니다.
            - `quarterly strict prototype` 전략은 현재 **research-only** 경로입니다.
            """
        )
        st.caption(
            "`늦은 active start`는 요청한 시작일에는 아직 usable한 statement shadow가 부족해서, "
            "실제 첫 보유/선택이 그보다 뒤에서 시작되는 상황을 뜻합니다."
        )

    active_panel = _render_backtest_panel_selector()

    if active_panel == "Single Strategy":
        render_single_strategy_workspace()
    elif active_panel == "Compare & Portfolio Builder":
        render_compare_portfolio_workspace()
    elif active_panel == "Candidate Review":
        render_candidate_review_workspace()
    elif active_panel == "Portfolio Proposal":
        render_portfolio_proposal_workspace()
    elif active_panel == "Final Review":
        render_final_review_workspace()
    else:
        render_post_selection_guide_workspace()


if __name__ == "__main__":
    st.title("Backtest")
    render_backtest_tab()
