"""Advanced low-level action forms for Data Operations."""

from __future__ import annotations

from typing import Any

import streamlit as st

from app.web.ingestion.guides import _job_title
from app.web.ingestion.registry import (
    INGESTION_COLLECTION_MANUAL,
    INGESTION_COLLECTION_OPERATIONAL,
)
from app.web.ingestion.sections import (
    render_manual_section,
    render_operational_section,
)
from app.web.ingestion.workflows import action_definition


def section_for_action(action: str) -> str:
    """Return the legacy form section for one active action."""

    definition = action_definition(action)
    section = str(definition.get("section") or "")
    if section not in {
        INGESTION_COLLECTION_OPERATIONAL,
        INGESTION_COLLECTION_MANUAL,
    }:
        raise KeyError(f"Active action has no supported form section: {action}")
    return section


def render_advanced_view(
    *,
    focused_action: str | None,
) -> Any:
    """Render the single existing form implementation for advanced execution."""

    st.subheader("고급 도구")
    st.caption(
        "저수준 collector와 복구 작업의 범위·provider 옵션·preflight를 직접 설정합니다. "
        "일상 작업은 데이터 준비 화면에서 목적을 먼저 선택하는 것을 권장합니다."
    )

    if focused_action:
        selected_section = section_for_action(focused_action)
        st.info(
            f"선택한 작업: **{_job_title(focused_action)}**. "
            "아래 고급 설정에서 범위와 preflight를 확인한 뒤 실행하세요."
        )
    else:
        if "data_operations_advanced_section" not in st.session_state:
            st.session_state["data_operations_advanced_section"] = (
                INGESTION_COLLECTION_OPERATIONAL
            )
        selected_section = st.pills(
            "고급 도구 구분",
            options=[
                INGESTION_COLLECTION_OPERATIONAL,
                INGESTION_COLLECTION_MANUAL,
            ],
            key="data_operations_advanced_section",
            label_visibility="collapsed",
        )
        if selected_section not in {
            INGESTION_COLLECTION_OPERATIONAL,
            INGESTION_COLLECTION_MANUAL,
        }:
            selected_section = INGESTION_COLLECTION_OPERATIONAL

    if selected_section == INGESTION_COLLECTION_MANUAL:
        return render_manual_section(focused_action=focused_action)
    return render_operational_section(focused_action=focused_action)


__all__ = ["render_advanced_view", "section_for_action"]
