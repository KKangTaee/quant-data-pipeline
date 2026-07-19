from __future__ import annotations

from typing import Any
from uuid import uuid4

import streamlit as st


def render_backtest_workflow_shell_fallback(
    shell: dict[str, Any],
) -> dict[str, Any] | None:
    """Render the page workflow from the same Python-owned shell projection."""

    active_context = dict(shell.get("active_stage_context") or {})
    with st.container(border=True):
        st.caption("BACKTEST DECISION PIPELINE")
        st.markdown(f"## {shell.get('headline') or 'Backtest'}")
        st.caption(str(shell.get("description") or ""))
        st.markdown(
            f"**현재 단계 · {active_context.get('level_label') or 'LEVEL 1'} — "
            f"{active_context.get('title') or '후보 분석'}**"
        )
        st.caption(str(active_context.get("responsibility") or ""))

        stages = list(shell.get("stages") or [])
        columns = st.columns(max(1, len(stages)))
        for index, stage in enumerate(stages):
            stage_key = str(stage.get("stage_key") or "")
            label = (
                f"{stage.get('level_label') or ''} · {stage.get('title') or ''}\n"
                f"{stage.get('english_title') or ''}"
            )
            if columns[index].button(
                label,
                key=f"backtest_workflow_shell_fallback_{stage_key}",
                type="primary" if stage.get("is_active") else "secondary",
                use_container_width=True,
            ):
                return {
                    "type": "select_stage",
                    "stage_key": stage_key,
                    "nonce": uuid4().hex,
                }
    return None


__all__ = ["render_backtest_workflow_shell_fallback"]
