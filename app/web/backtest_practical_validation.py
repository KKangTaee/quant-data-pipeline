from __future__ import annotations

from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_practical_validation_helpers import (
    build_practical_validation_result,
    queue_final_review_source_from_validation,
    save_practical_validation_result,
    source_components_dataframe,
)
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_readiness_route_panel,
    render_stage_brief,
    render_status_card_grid,
)
from app.web.runtime import (
    PORTFOLIO_SELECTION_SOURCE_FILE,
    PRACTICAL_VALIDATION_RESULT_FILE,
    load_portfolio_selection_sources,
    load_practical_validation_results,
)


def _source_label(row: dict[str, Any]) -> str:
    return (
        f"{row.get('created_at') or '-'} | "
        f"{row.get('source_kind') or '-'} | "
        f"{row.get('source_title') or row.get('selection_source_id') or '-'}"
    )


def _render_source_summary(source: dict[str, Any]) -> None:
    summary = dict(source.get("summary") or {})
    period = dict(source.get("period") or {})
    construction = dict(source.get("construction") or {})
    render_badge_strip(
        [
            {"label": "Source", "value": source.get("source_kind") or "-", "tone": "neutral"},
            {"label": "Period", "value": f"{period.get('actual_start') or period.get('start') or '-'} -> {period.get('actual_end') or period.get('end') or '-'}", "tone": "neutral"},
            {"label": "CAGR", "value": summary.get("cagr") if summary.get("cagr") is not None else "-", "tone": "neutral"},
            {"label": "MDD", "value": summary.get("mdd") if summary.get("mdd") is not None else "-", "tone": "neutral"},
            {"label": "Weight Total", "value": f"{construction.get('target_weight_total', 0)}%", "tone": "neutral"},
        ]
    )
    component_df = source_components_dataframe(source)
    if component_df.empty:
        st.info("선택된 source에 component snapshot이 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)


def _render_validation_result(validation_result: dict[str, Any]) -> None:
    render_readiness_route_panel(
        route_label=str(validation_result.get("validation_route") or "-"),
        score=float(validation_result.get("validation_score") or 0.0),
        blockers_count=len(validation_result.get("hard_blockers") or []),
        verdict=str(validation_result.get("verdict") or "-"),
        next_action=str(validation_result.get("next_action") or "-"),
        route_title="Practical Validation",
        score_title="Validation Score",
    )
    st.dataframe(pd.DataFrame(validation_result.get("checks") or []), width="stretch", hide_index=True)
    if validation_result.get("hard_blockers"):
        for blocker in list(validation_result.get("hard_blockers") or []):
            st.error(str(blocker))
    if validation_result.get("review_gaps"):
        for gap in list(validation_result.get("review_gaps") or []):
            st.warning(str(gap))


def render_practical_validation_workspace() -> None:
    st.markdown("### Practical Validation")
    st.caption(
        "Backtest Analysis에서 선택한 후보를 실전 투입 전 관점으로 검증합니다. "
        "최종 사용자 메모와 최종 판단은 Final Review에서만 남깁니다."
    )

    sources = load_portfolio_selection_sources(limit=100)
    validation_rows = load_practical_validation_results(limit=100)
    session_source = st.session_state.get("backtest_practical_validation_source")
    notice = st.session_state.pop("backtest_practical_validation_notice", None)
    if notice:
        st.success(str(notice))

    render_status_card_grid(
        [
            {"title": "Selection Sources", "value": len(sources), "tone": "positive" if sources else "neutral"},
            {"title": "Validation Results", "value": len(validation_rows), "tone": "positive" if validation_rows else "neutral"},
            {"title": "Final Memo", "value": "Final Review Only", "tone": "neutral"},
            {"title": "Live Approval", "value": "Disabled", "tone": "neutral"},
        ]
    )

    with st.container(border=True):
        render_stage_brief(
            purpose="선택된 단일 전략, Compare 후보, 저장 Mix를 같은 Clean V2 source로 읽습니다.",
            result="Practical Validation result",
        )
        st.caption(f"Sources: `{PORTFOLIO_SELECTION_SOURCE_FILE}`")
        st.caption(f"Validation: `{PRACTICAL_VALIDATION_RESULT_FILE}`")

    selectable_sources: list[dict[str, Any]] = []
    if isinstance(session_source, dict) and session_source:
        selectable_sources.append(dict(session_source))
    existing_ids = {str(row.get("selection_source_id") or "") for row in selectable_sources}
    for row in sources:
        source_id = str(row.get("selection_source_id") or "")
        if source_id in existing_ids:
            continue
        selectable_sources.append(dict(row))

    if not selectable_sources:
        st.info("아직 Practical Validation으로 보낸 Clean V2 source가 없습니다.")
        st.caption("Backtest Analysis에서 Single / Compare / Saved Mix 결과를 선택하면 여기에 표시됩니다.")
        return

    labels = [_source_label(row) for row in selectable_sources]
    selected_label = st.selectbox("검증할 후보 source", options=labels, key="practical_validation_source_selected")
    source = selectable_sources[labels.index(selected_label)]

    st.markdown("#### 1. 선택 후보 확인")
    with st.container(border=True):
        _render_source_summary(source)

    validation_result = build_practical_validation_result(source)
    st.markdown("#### 2. 실전 검증 결과")
    with st.container(border=True):
        _render_validation_result(validation_result)

    st.markdown("#### 3. 다음 단계")
    with st.container(border=True):
        st.info(
            "이 단계는 구조화된 검증 자료를 저장합니다. "
            "선정 / 보류 / 거절 / 재검토 판단과 최종 메모는 Final Review에서 기록합니다."
        )
        action_cols = st.columns(2, gap="small")
        with action_cols[0]:
            if st.button("검증 결과 저장", key="practical_validation_save_result", width="stretch"):
                save_practical_validation_result(validation_result)
                st.success(f"검증 결과 `{validation_result['validation_id']}`를 저장했습니다.")
        with action_cols[1]:
            if st.button("Final Review로 이동", key="practical_validation_send_final_review", width="stretch"):
                queue_final_review_source_from_validation(
                    source=source,
                    validation_result=validation_result,
                    persist_validation=True,
                )
                st.rerun()

    with st.expander("Clean V2 Source JSON", expanded=False):
        st.json(source)
    with st.expander("Practical Validation Result JSON", expanded=False):
        st.json(validation_result)
