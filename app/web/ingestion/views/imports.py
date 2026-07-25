"""Official-file entry view for Data Operations."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.web.ingestion.guides import _job_guide, _job_title
from app.web.ingestion.workflows import OFFICIAL_IMPORT_ACTIONS


IMPORT_CONTEXT = {
    "import_sp500_index_earnings_xlsx": (
        "S&P 공식 Index Earnings workbook과 자료 발표일을 등록합니다.",
        "등록 후 Market Research의 S&P 500 가치평가와 Economic Cycle을 다시 확인합니다.",
    ),
    "import_bls_macro_calendar_ics": (
        "BLS 자동 일정 수집이 차단되거나 누락됐을 때 공식 .ics 파일로 보강합니다.",
        "등록 후 Market Research의 일정 화면에서 BLS 발표일을 확인합니다.",
    ),
}


def render_imports_view(
    *,
    on_action_focus: Callable[[str], None],
) -> None:
    st.caption(
        "자동 provider 수집이 대신할 수 없는 공식 workbook과 fallback 파일만 이곳에서 등록합니다."
    )
    for action in OFFICIAL_IMPORT_ACTIONS:
        guide = _job_guide(action)
        context, handoff = IMPORT_CONTEXT[action]
        with st.container(border=True):
            st.markdown(f"#### {_job_title(action)}")
            st.write(context)
            st.caption(str(guide.get("purpose") or ""))
            st.caption("다음 확인: " + handoff)
            if st.button(
                "파일 설정 열기",
                key=f"data_ops_import_{action}",
                use_container_width=True,
            ):
                on_action_focus(action)


__all__ = ["render_imports_view"]
