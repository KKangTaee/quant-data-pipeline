"""Consumer-purpose preparation view for Data Operations."""

from __future__ import annotations

from collections.abc import Callable

import streamlit as st

from app.web.ingestion.guides import _job_guide, _job_title
from app.web.ingestion.navigation import (
    clear_data_operations_workflow,
    select_data_operations_workflow,
    selected_data_operations_workflow,
)
from app.web.ingestion.workflows import (
    DATA_OPERATIONS_WORKFLOWS,
    workflow_for_id,
)


def _render_workflow_card(workflow: dict[str, object]) -> None:
    workflow_id = str(workflow["id"])
    with st.container(border=True):
        st.markdown(f"#### {workflow['title']}")
        st.write(str(workflow["purpose"]))
        st.caption(str(workflow["included"]))
        st.caption("권장 시점: " + str(workflow["cadence"]))
        if st.button(
            "열기",
            key=f"data_ops_open_workflow_{workflow_id}",
            use_container_width=True,
        ):
            select_data_operations_workflow(workflow_id)
            st.rerun()


def _render_workflow_step(
    action: str,
    *,
    step_number: int,
    on_action_focus: Callable[[str], None],
) -> None:
    guide = _job_guide(action)
    caveats = [
        str(item)
        for item in guide.get("caveats") or []
        if str(item).strip()
    ]
    with st.container(border=True):
        st.caption(f"STEP {step_number}")
        st.markdown(f"#### {_job_title(action)}")
        st.write(str(guide.get("purpose") or ""))
        if caveats:
            st.caption("주의: " + " / ".join(caveats))
        if st.button(
            "설정 열기",
            key=f"data_ops_focus_action_{action}",
            use_container_width=True,
        ):
            on_action_focus(action)


def render_preparation_view(
    *,
    on_action_focus: Callable[[str], None],
) -> None:
    """Render purpose cards or one selected workflow's ordered steps."""

    selected_workflow_id = selected_data_operations_workflow()
    if selected_workflow_id is None:
        st.subheader("어떤 데이터를 준비할까요?")
        st.caption(
            "collector 이름 대신 실제로 사용하려는 Research·Portfolio 흐름을 먼저 선택하세요. "
            "실행은 각 단계의 범위와 preflight를 확인한 뒤 시작됩니다."
        )
        for start in range(0, len(DATA_OPERATIONS_WORKFLOWS), 2):
            columns = st.columns(2)
            for column, workflow in zip(
                columns,
                DATA_OPERATIONS_WORKFLOWS[start : start + 2],
            ):
                with column:
                    _render_workflow_card(workflow)
        return

    workflow = workflow_for_id(selected_workflow_id)
    back_col, _ = st.columns([1, 4])
    if back_col.button(
        "← 준비 목적",
        key="data_ops_back_to_workflows",
        use_container_width=True,
    ):
        clear_data_operations_workflow()
        st.rerun()

    st.subheader(str(workflow["title"]))
    st.write(str(workflow["purpose"]))
    st.caption(
        "각 단계는 자동으로 이어서 실행되지 않습니다. 필요한 단계만 열어 범위와 주의사항을 확인하세요."
    )
    for index, action in enumerate(workflow["actions"], start=1):
        _render_workflow_step(
            str(action),
            step_number=index,
            on_action_focus=on_action_focus,
        )


__all__ = ["render_preparation_view"]
