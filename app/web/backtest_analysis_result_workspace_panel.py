from __future__ import annotations

import json
from uuid import uuid4
from typing import Any

import pandas as pd
import streamlit as st


def _render_allocation(rows: list[dict[str, Any]]) -> None:
    if not rows:
        st.caption("표시 가능한 비중 근거가 없습니다.")
        return
    for row in rows:
        st.markdown(
            f"**{row.get('ticker') or '-'}** · {row.get('weight_label') or '비중 근거 없음'}"
        )


def render_backtest_analysis_result_workspace_fallback(
    workspace: dict[str, Any],
) -> dict[str, Any] | None:
    """Render the Python-owned result model when the React build is unavailable."""

    if not workspace.get("visible"):
        return None

    identity = dict(workspace.get("identity") or {})
    lifecycle = dict(workspace.get("lifecycle") or {})
    st.markdown(f"## {identity.get('strategy_name') or 'Backtest 결과'}")
    st.caption(
        f"{lifecycle.get('display_label') or '결과 상태 미확인'} · "
        f"{identity.get('period_label') or '기간 미측정'}"
    )
    if lifecycle.get("reference_message"):
        st.caption(str(lifecycle["reference_message"]))
    error = dict(lifecycle.get("error") or {})
    if error:
        st.warning(str(error.get("message") or "이전 실행에서 오류가 발생했습니다."))

    st.markdown("### 1. 성과 요약")
    metrics = list(workspace.get("performance_summary") or [])
    for offset in range(0, len(metrics), 2):
        columns = st.columns(2)
        for column, metric in zip(columns, metrics[offset : offset + 2]):
            column.metric(str(metric.get("label") or "-"), str(metric.get("value_label") or "-"))

    st.markdown("### 2. 전략과 기준의 흐름")
    chart = dict(workspace.get("chart") or {})
    strategy_label = str(chart.get("strategy_label") or "전략")
    benchmark = dict(chart.get("benchmark") or {})
    benchmark_label = str(benchmark.get("label") or "기준지수")
    chart_rows = [
        {
            "Date": row.get("date"),
            strategy_label: row.get("strategy_value"),
            benchmark_label: row.get("benchmark_value"),
        }
        for row in list(chart.get("hover_rows") or [])
    ]
    if chart_rows:
        chart_df = pd.DataFrame(chart_rows).set_index("Date")
        st.line_chart(chart_df)
        st.caption(str(chart.get("normalized_explanation") or ""))
    else:
        st.info("표시 가능한 성과 곡선이 없습니다.")
    if benchmark.get("missing_reason"):
        st.caption(str(benchmark["missing_reason"]))

    st.markdown("### 3. 현재 보유와 최신 신호 기준 목표 구성")
    st.caption("백테스트 모의 구성으로 실제 계좌나 주문이 아닙니다.")
    holdings = dict(workspace.get("holdings") or {})
    schedule = dict(holdings.get("schedule") or {})
    schedule_columns = st.columns(5)
    schedule_specs = (
        ("현재 평가일", schedule.get("valuation_as_of")),
        ("최신 신호일", schedule.get("latest_signal_as_of")),
        ("마지막 리밸런싱", schedule.get("last_rebalance_as_of")),
        ("주기", schedule.get("cadence_label")),
        ("다음 예상", schedule.get("next_window_label")),
    )
    for column, (label, value) in zip(schedule_columns, schedule_specs):
        column.markdown(f"**{label}**  \n{value or '-'}")
    current_column, target_column = st.columns(2)
    with current_column:
        st.markdown(f"#### 현재 보유 · {holdings.get('as_of') or '기준일 없음'}")
        _render_allocation(list(holdings.get("current_allocation") or []))
    with target_column:
        st.markdown(f"#### 목표 구성 · {holdings.get('target_as_of') or '기준일 없음'}")
        _render_allocation(list(holdings.get("target_allocation") or []))
    st.caption(str(holdings.get("explanation") or ""))

    st.markdown("### 4. Level2 인계 상태와 검증 질문")
    readiness = dict(workspace.get("technical_handoff_readiness") or {})
    st.info(str(readiness.get("label") or "결과 준비 상태 미확인"))
    for reason in list(readiness.get("reasons") or []):
        st.caption(str(reason.get("message") or ""))
    for question in list(workspace.get("level2_validation_questions") or []):
        st.markdown(
            f"**{question.get('lane_label') or '-'} · {question.get('title') or '-'}**  \n"
            f"{question.get('summary') or ''}"
        )

    st.markdown("### 5. 목적별 검증 근거")
    evidence_groups = list(workspace.get("evidence_groups") or [])
    for offset in range(0, len(evidence_groups), 2):
        columns = st.columns(2)
        for column, group in zip(columns, evidence_groups[offset : offset + 2]):
            with column:
                st.markdown(f"#### {group.get('label') or '-'}")
                st.caption(str(group.get("summary") or ""))
                for item in list(group.get("items") or []):
                    st.markdown(f"- {item.get('label') or '-'}: **{item.get('value') or '-'}**")

    st.markdown("### 6. 사용자용 결과 표")
    performance_rows = list(workspace.get("performance_rows") or [])
    holding_rows = list(workspace.get("holding_change_rows") or [])
    if performance_rows:
        st.markdown("#### 성과 시계열")
        st.dataframe(pd.DataFrame(performance_rows), use_container_width=True, hide_index=True)
    if holding_rows:
        st.markdown("#### 보유 변화")
        st.dataframe(pd.DataFrame(holding_rows), use_container_width=True, hide_index=True)

    appendix = dict(workspace.get("technical_appendix") or {})
    with st.expander("계산 및 데이터 기준", expanded=False):
        for section in list(appendix.get("sections") or []):
            st.markdown(f"#### {section.get('label') or '-'}")
            for row in list(section.get("rows") or []):
                st.markdown(
                    f"**{row.get('label') or '-'}** · {row.get('value_label') or '-'}  \n"
                    f"{row.get('explanation') or ''}"
                )
        raw = dict(appendix.get("raw") or {})
        st.markdown("#### 원본 필드 보기")
        st.caption(
            f"원본 결과 {int(raw.get('row_count') or 0):,}행 · "
            f"{', '.join(str(column) for column in list(raw.get('columns') or []))}"
        )
        st.code(
            json.dumps(raw.get("meta") or {}, ensure_ascii=False, indent=2, default=str),
            language="json",
        )

    action = dict(dict(workspace.get("actions") or {}).get("save_and_move") or {})
    if action and st.button(
        str(action.get("label") or "후보로 저장하고 Level2로 이동"),
        disabled=not bool(action.get("enabled")),
        type="primary",
        key=f"bt1_result_fallback_handoff_{identity.get('run_result_id') or 'none'}",
    ):
        return {
            "action": "save_and_move",
            "payload": {
                "run_result_id": str(identity.get("run_result_id") or ""),
                "current_configuration_fingerprint": str(
                    workspace.get("configuration_fingerprint") or ""
                ),
            },
            "nonce": str(uuid4()),
        }
    return None
