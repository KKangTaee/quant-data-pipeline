from __future__ import annotations

from typing import Any

import streamlit as st

from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.final_selected_portfolio_dashboard_helpers import (
    build_selected_portfolio_component_table,
    build_selected_portfolio_dashboard_table,
    build_selected_portfolio_evidence_table,
    filter_selected_portfolio_rows,
    final_selected_portfolio_label,
    selected_portfolio_benchmark_options,
    selected_portfolio_source_type_options,
    selected_portfolio_status_options,
)
from app.web.runtime import (
    FINAL_SELECTED_PORTFOLIO_STATUS_LABELS,
    FINAL_SELECTION_DECISION_REGISTRY_FILE,
    load_final_selected_portfolio_dashboard,
)


def _status_tone(status: str) -> str:
    if status in {"normal"}:
        return "positive"
    if status in {"watch", "rebalance_needed", "re_review_needed"}:
        return "warning"
    if status == "blocked":
        return "danger"
    return "neutral"


def _summary_cards(summary: dict[str, Any]) -> list[dict[str, Any]]:
    status_counts = dict(summary.get("status_counts") or {})
    return [
        {
            "title": "Final Review Records",
            "value": summary.get("final_decision_count", 0),
            "detail": "Final Review 전체 판단 row",
            "tone": "positive" if summary.get("final_decision_count") else "neutral",
        },
        {
            "title": "Selected Portfolios",
            "value": summary.get("selected_decision_count", 0),
            "detail": "`SELECT_FOR_PRACTICAL_PORTFOLIO`만 운영 대상으로 읽음",
            "tone": "positive" if summary.get("selected_decision_count") else "neutral",
        },
        {
            "title": "Normal",
            "value": status_counts.get("normal", 0),
            "detail": "첫 운영 대시보드 기준 통과",
            "tone": "positive" if status_counts.get("normal") else "neutral",
        },
        {
            "title": "Watch / Review",
            "value": status_counts.get("watch", 0)
            + status_counts.get("rebalance_needed", 0)
            + status_counts.get("re_review_needed", 0),
            "detail": "관찰 또는 재검토 필요",
            "tone": "warning" if (
                status_counts.get("watch", 0)
                + status_counts.get("rebalance_needed", 0)
                + status_counts.get("re_review_needed", 0)
            ) else "neutral",
        },
        {
            "title": "Blocked",
            "value": status_counts.get("blocked", 0),
            "detail": "운영 대상으로 보기 전 보강 필요",
            "tone": "danger" if status_counts.get("blocked") else "neutral",
        },
        {
            "title": "Live Approval / Order",
            "value": "Disabled",
            "detail": "Phase36은 승인/주문을 만들지 않음",
            "tone": "neutral",
        },
    ]


def _render_empty_state(summary: dict[str, Any]) -> None:
    if not summary.get("final_decision_count"):
        st.info("아직 Final Review에서 기록된 최종 판단 row가 없습니다.")
        st.caption(f"Path: {FINAL_SELECTION_DECISION_REGISTRY_FILE}")
        return
    st.warning(
        "Final Review 기록은 있지만 `SELECT_FOR_PRACTICAL_PORTFOLIO`로 선정된 포트폴리오가 없습니다. "
        "`Backtest > Final Review`에서 최종 판단이 선정으로 저장된 row만 이 대시보드에 운영 대상으로 표시됩니다."
    )
    st.caption(f"Path: {FINAL_SELECTION_DECISION_REGISTRY_FILE}")


def _render_selected_row_detail(row: dict[str, Any]) -> None:
    st.markdown("#### 선택 포트폴리오 상세")
    render_badge_strip(
        [
            {
                "label": "Status",
                "value": row.get("operation_status_label"),
                "tone": _status_tone(str(row.get("operation_status") or "")),
            },
            {"label": "Decision ID", "value": row.get("decision_id"), "tone": "neutral"},
            {"label": "Source", "value": f"{row.get('source_type')} / {row.get('source_id')}", "tone": "neutral"},
            {"label": "Target Weight", "value": f"{float(row.get('target_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Benchmark", "value": row.get("benchmark_label"), "tone": "neutral"},
            {"label": "Evidence", "value": row.get("evidence_route"), "tone": "positive"},
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption(str(row.get("status_reason") or "-"))

    component_df = build_selected_portfolio_component_table(row)
    if component_df.empty:
        st.warning("선택된 포트폴리오에 active component가 없습니다.")
    else:
        st.markdown("##### Target Allocation")
        st.dataframe(component_df, width="stretch", hide_index=True)

    detail_cols = st.columns(2, gap="small")
    with detail_cols[0]:
        with st.container(border=True):
            st.markdown("##### 운영 판단")
            st.write(
                {
                    "reason": row.get("operator_reason"),
                    "constraints": row.get("operator_constraints"),
                    "next_action": row.get("operator_next_action"),
                }
            )
    with detail_cols[1]:
        with st.container(border=True):
            st.markdown("##### 관찰 기준")
            st.write(
                {
                    "review_cadence": row.get("review_cadence"),
                    "review_triggers": row.get("review_triggers") or [],
                    "blockers": row.get("blockers") or [],
                }
            )

    evidence_df = build_selected_portfolio_evidence_table(row)
    with st.expander("검증 근거 상세", expanded=False):
        if evidence_df.empty:
            st.info("표시할 evidence check row가 없습니다.")
        else:
            st.dataframe(evidence_df, width="stretch", hide_index=True)

    with st.container(border=True):
        st.markdown("##### 실행 경계")
        st.caption(
            "이 대시보드는 최종 선정 포트폴리오를 운영 대상으로 읽는 화면입니다. "
            "실제 투자 승인, broker 주문, 자동 리밸런싱은 만들지 않습니다."
        )
        action_cols = st.columns(3, gap="small")
        action_cols[0].button("Live Approval", disabled=True, width="stretch")
        action_cols[1].button("Broker Order", disabled=True, width="stretch")
        action_cols[2].button("Auto Rebalance", disabled=True, width="stretch")

    with st.expander("Final Review 원본 JSON", expanded=False):
        st.json(row.get("raw_decision") or {})


def render_final_selected_portfolio_dashboard_page() -> None:
    st.title("Selected Portfolio Dashboard")
    st.caption(
        "Final Review에서 실전 후보로 선정된 포트폴리오를 운영 관점으로 모아 보는 Phase36 대시보드입니다. "
        "새 registry를 쓰지 않고 최종 판단 기록을 읽기만 합니다."
    )

    dashboard = load_final_selected_portfolio_dashboard()
    summary = dict(dashboard.get("summary") or {})
    rows = list(dashboard.get("dashboard_rows") or [])

    render_status_card_grid(_summary_cards(summary))

    with st.container(border=True):
        st.markdown("#### 데이터 기준")
        st.write(
            {
                "source": str(FINAL_SELECTION_DECISION_REGISTRY_FILE),
                "selected_filter": "decision_route == SELECT_FOR_PRACTICAL_PORTFOLIO 또는 selected_practical_portfolio == true",
                "write_policy": "read_only_dashboard",
                "live_approval": False,
                "order_instruction": False,
            }
        )

    if not rows:
        _render_empty_state(summary)
        return

    st.markdown("#### 운영 대상 목록")
    filter_cols = st.columns([0.32, 0.28, 0.24, 0.16], gap="small")
    status_options = selected_portfolio_status_options(rows)
    source_type_options = selected_portfolio_source_type_options(rows)
    benchmark_options = selected_portfolio_benchmark_options(rows)
    with filter_cols[0]:
        selected_statuses = st.multiselect(
            "Status",
            options=status_options,
            default=status_options,
            format_func=lambda status: FINAL_SELECTED_PORTFOLIO_STATUS_LABELS.get(status, status),
            key="selected_portfolio_dashboard_status_filter",
        )
    with filter_cols[1]:
        selected_source_types = st.multiselect(
            "Source Type",
            options=source_type_options,
            default=source_type_options,
            key="selected_portfolio_dashboard_source_filter",
        )
    with filter_cols[2]:
        selected_benchmark = st.selectbox(
            "Benchmark",
            options=benchmark_options,
            key="selected_portfolio_dashboard_benchmark_filter",
        )
    with filter_cols[3]:
        st.metric("Total", len(rows))

    filtered_rows = filter_selected_portfolio_rows(
        rows,
        statuses=selected_statuses,
        source_types=selected_source_types,
        benchmark=str(selected_benchmark),
    )
    filter_cols[3].metric("Shown", len(filtered_rows))
    if not filtered_rows:
        st.warning("현재 filter 조건에 맞는 선정 포트폴리오가 없습니다.")
        return

    st.dataframe(build_selected_portfolio_dashboard_table(filtered_rows), width="stretch", hide_index=True)
    labels = [final_selected_portfolio_label(row) for row in filtered_rows]
    selected_label = st.selectbox(
        "상세 확인",
        options=labels,
        key="selected_portfolio_dashboard_selected_row",
    )
    selected_row = filtered_rows[labels.index(selected_label)]
    _render_selected_row_detail(selected_row)
