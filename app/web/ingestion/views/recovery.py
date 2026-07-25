"""Diagnosis-led recovery entry view for Data Operations."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.web.ingestion.guides import _job_guide, _job_title
from app.web.ingestion.workflows import (
    RECOVERY_DIAGNOSTIC_ACTIONS,
    RECOVERY_MANUAL_ACTIONS,
)


def _render_recovery_action(
    action: str,
    *,
    button_label: str,
    on_action_focus: Callable[[str], None],
) -> None:
    guide = _job_guide(action)
    with st.container(border=True):
        st.markdown(f"#### {_job_title(action)}")
        st.write(str(guide.get("purpose") or ""))
        caveats = [
            str(item)
            for item in guide.get("caveats") or []
            if str(item).strip()
        ]
        if caveats:
            st.caption("주의: " + " / ".join(caveats))
        if st.button(
            button_label,
            key=f"data_ops_recovery_{action}",
            use_container_width=True,
        ):
            on_action_focus(action)


def render_recovery_view(
    *,
    on_action_focus: Callable[[str], None],
) -> None:
    st.subheader("문제 복구")
    st.caption(
        "먼저 읽기 전용 진단으로 원인을 좁힌 뒤, 필요한 심볼과 기간만 수동으로 보강하세요."
    )
    st.markdown("### 원인 진단")
    for action in RECOVERY_DIAGNOSTIC_ACTIONS:
        _render_recovery_action(
            action,
            button_label="진단 설정 열기",
            on_action_focus=on_action_focus,
        )

    with st.expander("직접 복구 도구", expanded=False):
        st.caption(
            "진단 결과가 이미 있거나 범위를 정확히 아는 경우에만 사용합니다. "
            "모든 write action은 실행 전 preflight를 다시 확인합니다."
        )
        for action in RECOVERY_MANUAL_ACTIONS:
            _render_recovery_action(
                action,
                button_label="복구 설정 열기",
                on_action_focus=on_action_focus,
            )


__all__ = ["render_recovery_view"]
