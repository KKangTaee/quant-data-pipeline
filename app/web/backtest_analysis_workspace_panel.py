from __future__ import annotations

from typing import Any, Literal
from uuid import uuid4

import streamlit as st


def _intent(action: str, payload: dict[str, Any] | None = None) -> dict[str, Any]:
    return {
        "action": action,
        "payload": dict(payload or {}),
        "nonce": uuid4().hex,
    }


def render_backtest_analysis_workspace_fallback(
    workspace: dict[str, Any],
    *,
    surface: Literal["context", "decision"],
) -> dict[str, Any] | None:
    """Render a Streamlit fallback from the same Python-owned read model."""

    if surface == "context":
        st.markdown(f"### {dict(workspace.get('header') or {}).get('question') or 'Backtest Analysis'}")
        st.caption("후보 유형과 목적을 고정하고 필요한 설정만 입력합니다.")
        single_col, mix_col = st.columns(2)
        with single_col:
            if st.button(
                "Single Strategy",
                key="backtest_analysis_fallback_single",
                use_container_width=True,
            ):
                return _intent(
                    "select_workspace_kind",
                    {"workspace_kind": "single_strategy"},
                )
        with mix_col:
            if st.button(
                "Portfolio Mix",
                key="backtest_analysis_fallback_mix",
                use_container_width=True,
            ):
                return _intent(
                    "select_workspace_kind",
                    {"workspace_kind": "portfolio_mix"},
                )
        if workspace.get("workspace_kind") == "single_strategy":
            for group in list(workspace.get("strategy_catalog") or []):
                st.markdown(f"**{group.get('label') or '-'}**")
                columns = st.columns(2)
                for index, item in enumerate(list(group.get("items") or [])):
                    choice = str(item.get("strategy_choice") or "")
                    with columns[index % 2]:
                        if st.button(
                            choice,
                            key=f"backtest_analysis_fallback_strategy_{choice}",
                            use_container_width=True,
                        ):
                            return _intent(
                                "select_strategy",
                                {"strategy_choice": choice},
                            )
        return None

    decision = dict(workspace.get("decision") or {})
    st.markdown("#### 3. 실행 결과 해석")
    st.markdown(f"**{decision.get('headline') or '-'}**")
    st.caption(str(decision.get("summary") or ""))
    error = dict(workspace.get("error") or {})
    if error:
        st.error(str(error.get("message") or "실행을 완료하지 못했습니다."))
    metrics = list(decision.get("metrics") or [])
    if metrics:
        columns = st.columns(min(4, len(metrics)))
        for index, metric in enumerate(metrics):
            columns[index % len(columns)].metric(
                str(metric.get("label") or "-"),
                str(metric.get("value") if metric.get("value") is not None else "-"),
            )
    action = dict(dict(workspace.get("actions") or {}).get("save_and_move") or {})
    if action.get("enabled") and st.button(
        str(action.get("label") or "후보로 저장하고 Level2로 이동"),
        key="backtest_analysis_fallback_save_and_move",
        use_container_width=True,
    ):
        return _intent("save_and_move")
    return None


__all__ = ["render_backtest_analysis_workspace_fallback"]
