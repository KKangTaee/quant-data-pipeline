from __future__ import annotations

from collections.abc import Callable

import streamlit as st


# Render the Operations-owned Backtest run history surface.
def render_backtest_run_history_page(*, open_backtest_page: Callable[[], None] | None = None) -> None:
    st.title("Backtest Run History")
    st.caption(
        "저장된 백테스트 실행 기록을 운영 관점에서 다시 열고, form 복원, 재실행, Candidate Review 초안 전달을 처리합니다."
    )
    st.info(
        "이 화면은 후보 검토의 본 단계가 아니라 과거 실행을 재현하고 감사하는 운영 도구입니다. "
        "`Load Into Form`, `Run Again`, `Review As Candidate Draft`를 사용하면 Backtest 작업 흐름으로 이동합니다."
    )

    from app.web.pages import backtest as bt

    bt._render_persistent_backtest_history(open_backtest_page=open_backtest_page)
