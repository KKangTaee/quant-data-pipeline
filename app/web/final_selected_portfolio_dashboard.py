from __future__ import annotations

from datetime import date
from html import escape
from typing import Any

import pandas as pd
import streamlit as st

from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.final_selected_portfolio_dashboard_helpers import (
    build_selected_portfolio_current_weight_input_table,
    build_selected_portfolio_drift_alert_table,
    build_selected_portfolio_drift_table,
    build_selected_portfolio_component_table,
    build_selected_portfolio_dashboard_table,
    build_selected_portfolio_evidence_table,
    filter_selected_portfolio_rows,
    final_selected_portfolio_label,
    selected_portfolio_active_components,
    selected_portfolio_benchmark_options,
    selected_portfolio_component_default_symbol,
    selected_portfolio_source_type_options,
    selected_portfolio_status_options,
)
from app.web.runtime import (
    FINAL_SELECTED_PORTFOLIO_STATUS_LABELS,
    FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS,
    FINAL_SELECTION_DECISION_REGISTRY_FILE,
    build_selected_portfolio_current_weight_inputs,
    build_selected_portfolio_drift_alert_preview,
    build_selected_portfolio_drift_check,
    build_selected_portfolio_performance_recheck,
    build_selected_portfolio_recheck_defaults,
    load_final_selected_portfolio_dashboard,
    load_latest_selected_portfolio_prices,
)


def _status_tone(status: str) -> str:
    if status in {"normal"}:
        return "positive"
    if status in {"watch", "rebalance_needed", "re_review_needed"}:
        return "warning"
    if status == "blocked":
        return "danger"
    return "neutral"


def _alert_tone(alert_route: str) -> str:
    if alert_route == "NO_ALERT":
        return "positive"
    if alert_route in {"WATCH_ALERT", "INPUT_REVIEW_ALERT"}:
        return "warning"
    if alert_route == "REBALANCE_REVIEW_ALERT":
        return "danger"
    return "neutral"


def _review_trigger_tone(status: str) -> str:
    if status == "Clear":
        return "positive"
    if status == "Watch":
        return "warning"
    if status == "Breached":
        return "danger"
    return "neutral"


def _format_pct(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return f"{numeric:.2%}"


def _format_money(value: Any, *, default: str = "-") -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return default
    if pd.isna(numeric):
        return default
    return f"{numeric:,.0f}"


def _coerce_date(value: Any, fallback: date) -> date:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return fallback
    return parsed.date()


def _render_info_card_grid(cards: list[dict[str, Any]], *, min_width: int = 210) -> None:
    html_cards: list[str] = []
    for card in cards:
        title = escape(str(card.get("title") or ""))
        value = escape(str(card.get("value") if card.get("value") is not None else "-"))
        detail = escape(str(card.get("detail") or ""))
        tone = escape(str(card.get("tone") or "neutral"))
        detail_html = f'<div class="fsp-info-card-detail">{detail}</div>' if detail else ""
        html_cards.append(
            f'<div class="fsp-info-card fsp-info-card-{tone}">'
            f'<div class="fsp-info-card-title">{title}</div>'
            f'<div class="fsp-info-card-value">{value}</div>'
            f"{detail_html}"
            "</div>"
        )
    st.markdown(
        f"""
        <style>
          .fsp-info-card-grid {{
            display: grid;
            gap: 0.75rem;
            margin: 0.35rem 0 1rem 0;
          }}
          .fsp-info-card {{
            min-height: 92px;
            padding: 0.85rem 0.95rem;
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-top: 4px solid #64748b;
            border-radius: 8px;
            background: #ffffff;
            box-shadow: 0 1px 2px rgba(15, 23, 42, 0.05);
          }}
          .fsp-info-card-positive {{ border-top-color: #0f766e; }}
          .fsp-info-card-warning {{ border-top-color: #b45309; }}
          .fsp-info-card-danger {{ border-top-color: #b91c1c; }}
          .fsp-info-card-neutral {{ border-top-color: #475569; }}
          .fsp-info-card-title {{
            font-size: 0.82rem;
            font-weight: 720;
            color: #64748b;
            line-height: 1.25;
            overflow-wrap: anywhere;
          }}
          .fsp-info-card-value {{
            margin-top: 0.35rem;
            font-size: 1.08rem;
            font-weight: 780;
            color: #111827;
            line-height: 1.25;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
          .fsp-info-card-detail {{
            margin-top: 0.4rem;
            font-size: 0.82rem;
            line-height: 1.35;
            color: #64748b;
            overflow-wrap: anywhere;
            word-break: break-word;
          }}
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="fsp-info-card-grid" style="grid-template-columns: repeat(auto-fit, minmax({min_width}px, 1fr));">{"".join(html_cards)}</div>',
        unsafe_allow_html=True,
    )


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
            "detail": "최신 기간 재검증 대상",
            "tone": "positive" if summary.get("selected_decision_count") else "neutral",
        },
        {
            "title": "Normal",
            "value": status_counts.get("normal", 0),
            "detail": "선정 row / allocation / blocker 기준 통과",
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
    _render_snapshot(row)
    _render_performance_recheck(row)
    _render_operator_context(row)

    with st.expander("Audit / Developer Details", expanded=False):
        st.caption("일반 QA에서는 이 원본 JSON을 보지 않아도 됩니다. 저장 row 구조를 확인할 때만 펼쳐 봅니다.")
        st.json(row.get("raw_decision") or {})


def _decision_key(row: dict[str, Any]) -> str:
    return str(row.get("decision_id") or "selected_portfolio")


def _latest_recheck_result(row: dict[str, Any]) -> dict[str, Any]:
    return dict(st.session_state.get(f"selected_portfolio_recheck_result_{_decision_key(row)}") or {})


def _latest_drift_check(row: dict[str, Any]) -> dict[str, Any]:
    return dict(st.session_state.get(f"selected_portfolio_drift_check_result_{_decision_key(row)}") or {})


def _trigger_row(
    *,
    trigger: str,
    current_signal: str,
    status: str,
    why_it_matters: str,
    suggested_action: str,
) -> dict[str, str]:
    return {
        "Trigger": trigger,
        "Current Signal": current_signal,
        "Status": status,
        "Why It Matters": why_it_matters,
        "Suggested Action": suggested_action,
    }


def _status_from_delta(
    value: Any,
    *,
    breach_below: float | None = None,
    watch_below: float | None = None,
    clear_label: str = "Clear",
) -> str:
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return "Needs Input"
    if pd.isna(numeric):
        return "Needs Input"
    if breach_below is not None and numeric < breach_below:
        return "Breached"
    if watch_below is not None and numeric < watch_below:
        return "Watch"
    return clear_label


# Build the operator-facing trigger board by translating latest recheck/drift state into actionable rows.
def _build_review_trigger_board(row: dict[str, Any]) -> tuple[list[dict[str, str]], str, str]:
    recheck_result = _latest_recheck_result(row)
    drift_check = _latest_drift_check(row)
    blockers = [str(blocker) for blocker in list(row.get("blockers") or []) if str(blocker)]
    evidence_route = str(row.get("evidence_route") or "-")
    rows: list[dict[str, str]] = []

    evidence_status = "Clear" if not blockers and evidence_route == "READY_FOR_FINAL_DECISION" else "Watch"
    rows.append(
        _trigger_row(
            trigger="Final Review evidence",
            current_signal=evidence_route,
            status=evidence_status,
            why_it_matters="선정 당시 검증 근거가 아직 운영 대상 조건을 만족하는지 확인합니다.",
            suggested_action=(
                "남은 blocker가 없으므로 성과와 보유 상태를 계속 점검합니다."
                if evidence_status == "Clear"
                else "Selection Evidence tab에서 남은 blocker와 검증 근거를 다시 확인합니다."
            ),
        )
    )

    if not recheck_result:
        rows.extend(
            [
                _trigger_row(
                    trigger="CAGR deterioration",
                    current_signal="Performance Recheck not run",
                    status="Needs Input",
                    why_it_matters="선정 당시 수익률 근거가 최신 기간에서도 유지되는지 봅니다.",
                    suggested_action="Performance Recheck에서 기간과 가상 투자금을 확인한 뒤 Run Recheck를 실행합니다.",
                ),
                _trigger_row(
                    trigger="MDD expansion",
                    current_signal="Performance Recheck not run",
                    status="Needs Input",
                    why_it_matters="최신 기간에서 최대 낙폭이 커졌는지 확인합니다.",
                    suggested_action="Performance Recheck 실행 후 drawdown 변화를 확인합니다.",
                ),
                _trigger_row(
                    trigger="Benchmark underperformance",
                    current_signal="Performance Recheck not run",
                    status="Needs Input",
                    why_it_matters="선정 포트폴리오가 benchmark 대비 우위를 유지하는지 봅니다.",
                    suggested_action="Performance Recheck 실행 후 benchmark spread를 확인합니다.",
                ),
            ]
        )
    elif recheck_result.get("status") == "error":
        error_text = str(recheck_result.get("error") or "recheck failed")
        rows.extend(
            [
                _trigger_row(
                    trigger="CAGR deterioration",
                    current_signal=error_text,
                    status="Needs Input",
                    why_it_matters="성과 유지 여부를 판단하려면 recheck 결과가 필요합니다.",
                    suggested_action="입력 기간과 selected component contract를 확인한 뒤 다시 실행합니다.",
                ),
                _trigger_row(
                    trigger="MDD expansion",
                    current_signal=error_text,
                    status="Needs Input",
                    why_it_matters="리스크 확대 여부를 판단하려면 recheck 결과가 필요합니다.",
                    suggested_action="Performance Recheck 오류를 먼저 해결합니다.",
                ),
                _trigger_row(
                    trigger="Benchmark underperformance",
                    current_signal=error_text,
                    status="Needs Input",
                    why_it_matters="benchmark 대비 성과를 판단하려면 recheck 결과가 필요합니다.",
                    suggested_action="Performance Recheck 오류를 먼저 해결합니다.",
                ),
            ]
        )
    else:
        change = dict(recheck_result.get("change_summary") or {})
        portfolio_summary = dict(recheck_result.get("portfolio_summary") or {})
        baseline_summary = dict(recheck_result.get("baseline_summary") or {})
        cagr_delta = change.get("cagr_delta_vs_baseline")
        mdd_delta = change.get("mdd_delta_vs_baseline")
        spread = change.get("net_cagr_spread")
        cagr_status = _status_from_delta(cagr_delta, breach_below=-0.03, watch_below=0.0)
        mdd_status = _status_from_delta(mdd_delta, breach_below=-0.05, watch_below=0.0)
        spread_status = _status_from_delta(spread, breach_below=0.0, watch_below=0.02)
        rows.extend(
            [
                _trigger_row(
                    trigger="CAGR deterioration",
                    current_signal=(
                        f"Recheck {_format_pct(portfolio_summary.get('cagr'))} vs "
                        f"baseline {_format_pct(baseline_summary.get('cagr'))} "
                        f"(delta {_format_pct(cagr_delta)})"
                    ),
                    status=cagr_status,
                    why_it_matters="선정 근거였던 장기 수익률이 최신 기간에서 약해졌는지 봅니다.",
                    suggested_action=(
                        "CAGR 약화 폭이 큽니다. What Changed와 Contribution tab에서 원인을 확인합니다."
                        if cagr_status == "Breached"
                        else "다음 점검에서도 하락이 이어지는지 관찰합니다."
                        if cagr_status == "Watch"
                        else "현재 수익률 근거는 유지됩니다."
                    ),
                ),
                _trigger_row(
                    trigger="MDD expansion",
                    current_signal=(
                        f"Recheck {_format_pct(portfolio_summary.get('mdd'))} vs "
                        f"baseline {_format_pct(baseline_summary.get('mdd'))} "
                        f"(delta {_format_pct(mdd_delta)})"
                    ),
                    status=mdd_status,
                    why_it_matters="최신 기간에서 손실 위험이 선정 당시보다 커졌는지 봅니다.",
                    suggested_action=(
                        "MDD 확대가 큽니다. 약한 기간과 component contribution을 먼저 확인합니다."
                        if mdd_status == "Breached"
                        else "drawdown이 더 커지는지 다음 점검에서 확인합니다."
                        if mdd_status == "Watch"
                        else "현재 drawdown 근거는 유지됩니다."
                    ),
                ),
                _trigger_row(
                    trigger="Benchmark underperformance",
                    current_signal=f"Benchmark spread {_format_pct(spread)}",
                    status=spread_status,
                    why_it_matters="포트폴리오가 비교 기준 대비 우위를 유지하는지 봅니다.",
                    suggested_action=(
                        "benchmark를 밑돌았습니다. 선정 thesis를 재검토합니다."
                        if spread_status == "Breached"
                        else "spread가 얇습니다. 다음 recheck에서 우위가 유지되는지 봅니다."
                        if spread_status == "Watch"
                        else "benchmark 대비 우위가 유지됩니다."
                    ),
                ),
            ]
        )

    drift_route = str(drift_check.get("route") or "")
    drift_signal = str(drift_check.get("route_label") or "Holding Drift Check not run")
    if not drift_check:
        drift_status = "Needs Input"
        drift_action = "Holding Drift Check tab에서 현재 평가금액, 보유수량, 또는 현재 비중을 입력합니다."
    elif drift_route == "DRIFT_ALIGNED":
        drift_status = "Clear"
        drift_action = "현재 입력 기준으로 target allocation 근처입니다."
    elif drift_route == "DRIFT_WATCH":
        drift_status = "Watch"
        drift_action = "watch component의 drift가 확대되는지 다음 점검에서 확인합니다."
    elif drift_route == "REBALANCE_NEEDED":
        drift_status = "Breached"
        drift_action = "주문 지시가 아니라, drift가 큰 component를 운영 검토 목록에 올립니다."
    else:
        drift_status = "Needs Input"
        drift_action = "입력 합계와 누락 component를 확인한 뒤 다시 계산합니다."
    rows.append(
        _trigger_row(
            trigger="Holding drift",
            current_signal=drift_signal,
            status=drift_status,
            why_it_matters="실제 또는 가정 보유 비중이 선정 target allocation에서 벗어났는지 봅니다.",
            suggested_action=drift_action,
        )
    )

    statuses = [row_item["Status"] for row_item in rows]
    if "Breached" in statuses:
        return rows, "Breached", "재검토가 필요한 trigger가 있습니다. Breached row의 Suggested Action부터 확인합니다."
    if "Needs Input" in statuses:
        return rows, "Needs Input", "운영 판단을 완성하려면 Performance Recheck 또는 Holding Drift Check 입력이 더 필요합니다."
    if "Watch" in statuses:
        return rows, "Watch", "큰 차단은 없지만 watch trigger가 있습니다. 다음 점검에서 같은 항목이 악화되는지 확인합니다."
    return rows, "Clear", "현재 trigger board 기준으로 선정 thesis와 운영 점검 상태가 유지됩니다."


def _render_snapshot(row: dict[str, Any]) -> None:
    st.markdown("#### Snapshot")
    _render_info_card_grid(
        [
            {
                "title": "Selection Status",
                "value": row.get("operation_status_label"),
                "detail": row.get("status_reason"),
                "tone": _status_tone(str(row.get("operation_status") or "")),
            },
            {
                "title": "Original Test Period",
                "value": f"{row.get('baseline_start') or '-'} -> {row.get('baseline_end') or '-'}",
                "detail": "Final Review에서 선정할 때 확인된 기준 기간",
                "tone": "neutral",
            },
            {
                "title": "Baseline CAGR",
                "value": _format_pct(row.get("baseline_cagr")),
                "detail": f"Benchmark {row.get('benchmark_label') or '-'}",
                "tone": "positive",
            },
            {
                "title": "Baseline MDD",
                "value": _format_pct(row.get("baseline_mdd")),
                "detail": "선정 당시 최대 낙폭 기준",
                "tone": "warning",
            },
            {
                "title": "Target Allocation",
                "value": f"{float(row.get('target_weight_total') or 0.0):.1f}%",
                "detail": f"{row.get('component_count') or 0} component",
                "tone": "neutral",
            },
        ],
        min_width=180,
    )
    with st.expander("Identity / Source", expanded=False):
        st.markdown(f"**Decision ID**  \n`{row.get('decision_id') or '-'}`")
        st.markdown(f"**Source**  \n`{row.get('source_type') or '-'}` / `{row.get('source_id') or '-'}`")
        st.markdown(f"**Title**  \n{row.get('source_title') or '-'}")
    component_df = build_selected_portfolio_component_table(row)
    st.markdown("##### Portfolio Blueprint")
    st.caption("이 포트폴리오가 어떤 component와 target weight로 선정됐는지 보여줍니다. 실제 보유 상태 점검은 Monitoring Playbook의 Holding Drift Check에서 확인합니다.")
    if component_df.empty:
        st.warning("선택된 포트폴리오에 active component가 없습니다.")
    else:
        st.dataframe(component_df, width="stretch", hide_index=True)


def _render_operator_context(row: dict[str, Any]) -> None:
    st.markdown("#### Monitoring Playbook")
    st.caption(
        "이 영역은 선정된 포트폴리오를 어떻게 계속 확인할지 정리합니다. "
        "선정 근거, 관찰 기준, 보유 비중 점검, 실행 경계를 같은 흐름에서 봅니다."
    )
    triggers = [str(trigger) for trigger in list(row.get("review_triggers") or []) if str(trigger)]
    blockers = [str(blocker) for blocker in list(row.get("blockers") or []) if str(blocker)]
    _render_info_card_grid(
        [
            {
                "title": "1. 선정 근거 확인",
                "value": row.get("evidence_route"),
                "detail": "Final Review evidence / validation / robustness / paper observation",
                "tone": "positive" if not blockers else "warning",
            },
            {
                "title": "2. 성과 유지 확인",
                "value": "Performance Recheck",
                "detail": "새 기간으로 CAGR, MDD, benchmark spread를 다시 계산",
                "tone": "neutral",
            },
            {
                "title": "3. 보유 상태 확인",
                "value": "Holding Drift Check",
                "detail": "실제 또는 가상 보유 비중이 target에서 벗어났는지 확인",
                "tone": "neutral",
            },
            {
                "title": "4. 실행 경계",
                "value": "Read Only",
                "detail": "승인, 주문, 자동 리밸런싱은 만들지 않음",
                "tone": "neutral",
            },
        ],
        min_width=190,
    )
    evidence_df = build_selected_portfolio_evidence_table(row)
    evidence_tab, trigger_tab, drift_tab, boundary_tab = st.tabs(
        ["Selection Evidence", "Trigger Board", "Holding Drift Check", "Execution Boundary"]
    )
    with evidence_tab:
        st.caption("Final Review에서 이 포트폴리오가 실전 후보로 선정될 수 있었던 검증 근거입니다.")
        if evidence_df.empty:
            st.info("표시할 evidence check row가 없습니다.")
        else:
            st.dataframe(evidence_df, width="stretch", hide_index=True)
    with trigger_tab:
        st.caption(
            "Performance Recheck와 Holding Drift Check의 최신 입력을 운영 trigger 상태로 번역합니다. "
            "먼저 Summary를 보고, Watch / Breached row의 Suggested Action을 확인합니다."
        )
        trigger_rows, board_status, board_conclusion = _build_review_trigger_board(row)
        render_badge_strip(
            [
                {"label": "Board Status", "value": board_status, "tone": _review_trigger_tone(board_status)},
                {"label": "Review Cadence", "value": row.get("review_cadence"), "tone": "neutral"},
                {"label": "Stored Triggers", "value": len(triggers), "tone": "neutral"},
                {"label": "Writes", "value": "Disabled", "tone": "neutral"},
            ]
        )
        if board_status == "Breached":
            st.warning(board_conclusion)
        elif board_status in {"Watch", "Needs Input"}:
            st.info(board_conclusion)
        else:
            st.success(board_conclusion)
        st.dataframe(pd.DataFrame(trigger_rows), width="stretch", hide_index=True)
        with st.expander("Original Operator Notes", expanded=False):
            st.markdown(f"**선정 사유**  \n{row.get('operator_reason') or '-'}")
            st.markdown(f"**제약 조건**  \n{row.get('operator_constraints') or '-'}")
            st.markdown(f"**다음 행동**  \n{row.get('operator_next_action') or '-'}")
            st.markdown(f"**점검 주기**  \n{row.get('review_cadence') or '-'}")
            if triggers:
                st.markdown("**Final Review에 저장된 원본 trigger**")
                for trigger in triggers:
                    st.markdown(f"- {trigger}")
            else:
                st.caption("등록된 review trigger가 없습니다.")
            if blockers:
                st.warning("남아 있는 blocker: " + ", ".join(blockers))
    with drift_tab:
        _render_selected_row_drift_check(row)
    with boundary_tab:
        _render_execution_boundary()


def _render_execution_boundary() -> None:
    with st.container(border=True):
        st.markdown("#### Execution Boundary")
        st.caption(
            "이 대시보드는 최종 선정 포트폴리오를 운영 대상으로 읽는 화면입니다. "
            "기간 확장 재검증과 drift 점검은 read-only이며 실제 투자 승인, broker 주문, 자동 리밸런싱은 만들지 않습니다."
        )
        action_cols = st.columns(3, gap="small")
        action_cols[0].button("Live Approval", disabled=True, width="stretch")
        action_cols[1].button("Broker Order", disabled=True, width="stretch")
        action_cols[2].button("Auto Rebalance", disabled=True, width="stretch")


def _render_performance_recheck(row: dict[str, Any]) -> None:
    st.markdown("#### Performance Recheck")
    st.caption(
        "선정 당시의 component contract를 다시 실행해, 사용자가 지정한 기간에서 포트폴리오 성과가 유지되는지 확인합니다. "
        "기본 종료일은 DB에 있는 최신 시장일입니다."
    )
    defaults = build_selected_portfolio_recheck_defaults(row)
    if defaults.get("latest_market_date_error"):
        st.warning(f"최신 시장일 확인 실패: {defaults.get('latest_market_date_error')}")

    fallback_start = date(2016, 1, 1)
    fallback_end = date.today()
    default_start = _coerce_date(defaults.get("default_start"), fallback_start)
    default_end = _coerce_date(defaults.get("default_end"), fallback_end)
    decision_id = str(row.get("decision_id") or "selected_portfolio")
    form_cols = st.columns([0.22, 0.22, 0.24, 0.18, 0.14], gap="small")
    with form_cols[0]:
        recheck_start = st.date_input(
            "Recheck start",
            value=default_start,
            key=f"selected_portfolio_recheck_start_{decision_id}",
        )
    with form_cols[1]:
        recheck_end = st.date_input(
            "Recheck end",
            value=default_end,
            key=f"selected_portfolio_recheck_end_{decision_id}",
        )
    with form_cols[2]:
        initial_capital = st.number_input(
            "Virtual capital",
            min_value=1_000.0,
            value=10_000.0,
            step=1_000.0,
            key=f"selected_portfolio_recheck_capital_{decision_id}",
        )
    with form_cols[3]:
        st.metric("Original End", defaults.get("baseline_end") or "-")
    with form_cols[4]:
        run_clicked = st.button(
            "Run Recheck",
            key=f"selected_portfolio_run_recheck_{decision_id}",
            width="stretch",
        )

    result_key = f"selected_portfolio_recheck_result_{decision_id}"
    if run_clicked:
        with st.spinner("선정 포트폴리오 contract를 재실행하는 중입니다..."):
            st.session_state[result_key] = build_selected_portfolio_performance_recheck(
                row,
                start=str(recheck_start),
                end=str(recheck_end),
                initial_capital=float(initial_capital),
            )

    result = dict(st.session_state.get(result_key) or {})
    if not result:
        st.info("날짜 범위와 가상 투자금을 확인한 뒤 `Run Recheck`를 누르면 최신 기간 기준 성과를 바로 계산합니다.")
        return
    if result.get("status") == "error":
        st.error(str(result.get("error") or "Performance recheck failed."))
        for blocker in list(result.get("blockers") or []):
            st.warning(str(blocker))
        return

    for blocker in list(result.get("blockers") or []):
        st.warning(str(blocker))

    portfolio_summary = dict(result.get("portfolio_summary") or {})
    benchmark_summary = dict(result.get("benchmark_summary") or {})
    baseline_summary = dict(result.get("baseline_summary") or {})
    change_summary = dict(result.get("change_summary") or {})
    period = dict(result.get("period") or {})
    summary_tab, curve_tab, result_table_tab, changed_tab, contribution_tab, extremes_tab = st.tabs(
        ["Summary", "Equity Curve", "Result Table", "What Changed", "Contribution", "Extremes"]
    )
    with summary_tab:
        render_status_card_grid(
            [
                {
                    "title": "Recheck Verdict",
                    "value": result.get("verdict_route"),
                    "detail": result.get("verdict"),
                    "tone": "positive" if result.get("verdict_route") == "SELECTION_THESIS_HOLDS" else "warning",
                },
                {
                    "title": "Portfolio Value",
                    "value": _format_money(portfolio_summary.get("end_balance")),
                    "detail": f"Total return {_format_pct(portfolio_summary.get('total_return'))}",
                    "tone": "positive",
                },
                {
                    "title": "Recheck CAGR",
                    "value": _format_pct(portfolio_summary.get("cagr")),
                    "detail": f"Original {_format_pct(baseline_summary.get('cagr'))}",
                    "tone": "positive" if (change_summary.get("cagr_delta_vs_baseline") or 0.0) >= 0 else "warning",
                },
                {
                    "title": "Recheck MDD",
                    "value": _format_pct(portfolio_summary.get("mdd")),
                    "detail": f"Original {_format_pct(baseline_summary.get('mdd'))}",
                    "tone": "warning",
                },
                {
                    "title": "Benchmark Spread",
                    "value": _format_pct(change_summary.get("net_cagr_spread")),
                    "detail": f"Benchmark {result.get('benchmark_label') or '-'} CAGR {_format_pct(benchmark_summary.get('cagr'))}",
                    "tone": "positive" if (change_summary.get("net_cagr_spread") or 0.0) >= 0 else "warning",
                },
            ]
        )
        st.caption(
            f"Original period: {period.get('baseline_start') or '-'} -> {period.get('baseline_end') or '-'} | "
            f"Recheck period: {period.get('start') or '-'} -> {period.get('end') or '-'}"
        )

    chart_df = result.get("chart_df")
    with curve_tab:
        if isinstance(chart_df, pd.DataFrame) and not chart_df.empty:
            chart_view = chart_df.copy()
            chart_view["Date"] = pd.to_datetime(chart_view["Date"], errors="coerce")
            chart_view = chart_view.dropna(subset=["Date"]).set_index("Date")
            st.line_chart(chart_view)
        else:
            st.info("표시할 equity curve가 없습니다.")

    with result_table_tab:
        result_df = result.get("portfolio_result_df")
        if isinstance(result_df, pd.DataFrame) and not result_df.empty:
            display_df = result_df[["Date", "Total Balance", "Total Return"]].copy()
            display_df["Date"] = pd.to_datetime(display_df["Date"], errors="coerce").dt.strftime("%Y-%m-%d")
            display_df["Total Balance"] = display_df["Total Balance"].map(lambda value: _format_money(value))
            display_df["Total Return"] = display_df["Total Return"].map(lambda value: _format_pct(value))
            st.dataframe(display_df, width="stretch", hide_index=True)
        else:
            st.info("표시할 result table이 없습니다.")

    with changed_tab:
        comparison_df = pd.DataFrame(
            [
                {
                    "Metric": "CAGR",
                    "Original": baseline_summary.get("cagr"),
                    "Recheck": portfolio_summary.get("cagr"),
                    "Change": change_summary.get("cagr_delta_vs_baseline"),
                },
                {
                    "Metric": "Maximum Drawdown",
                    "Original": baseline_summary.get("mdd"),
                    "Recheck": portfolio_summary.get("mdd"),
                    "Change": change_summary.get("mdd_delta_vs_baseline"),
                },
                {
                    "Metric": "Benchmark CAGR Spread",
                    "Original": None,
                    "Recheck": change_summary.get("net_cagr_spread"),
                    "Change": None,
                },
            ]
        )
        for column in ["Original", "Recheck", "Change"]:
            comparison_df[column] = comparison_df[column].map(
                lambda value: _format_pct(value) if value is not None else "-"
            )
        st.dataframe(comparison_df, width="stretch", hide_index=True)

    with contribution_tab:
        component_df = pd.DataFrame(list(result.get("component_rows") or []))
        if component_df.empty:
            st.info("표시할 component contribution이 없습니다.")
        else:
            for column in ["Total Return", "Weighted Contribution", "CAGR", "MDD"]:
                if column in component_df.columns:
                    component_df[column] = component_df[column].map(
                        lambda value: _format_pct(value) if value is not None else "-"
                    )
            if "Target Weight" in component_df.columns:
                component_df["Target Weight"] = component_df["Target Weight"].map(
                    lambda value: f"{float(value):.1f}%" if value is not None and not pd.isna(value) else "-"
                )
            st.dataframe(component_df, width="stretch", hide_index=True)

    with extremes_tab:
        extremes = dict(result.get("period_extremes") or {})
        extreme_cols = st.columns(2, gap="small")
        with extreme_cols[0]:
            best_df = pd.DataFrame(extremes.get("best") or [])
            st.markdown("##### Strongest periods")
            if best_df.empty:
                st.caption("표시할 strong period가 없습니다.")
            else:
                if "Total Return" in best_df.columns:
                    best_df["Total Return"] = best_df["Total Return"].map(lambda value: _format_pct(value))
                if "Total Balance" in best_df.columns:
                    best_df["Total Balance"] = best_df["Total Balance"].map(lambda value: _format_money(value))
                st.dataframe(best_df, width="stretch", hide_index=True)
        with extreme_cols[1]:
            worst_df = pd.DataFrame(extremes.get("worst") or [])
            st.markdown("##### Weakest periods")
            if worst_df.empty:
                st.caption("표시할 weak period가 없습니다.")
            else:
                if "Total Return" in worst_df.columns:
                    worst_df["Total Return"] = worst_df["Total Return"].map(lambda value: _format_pct(value))
                if "Total Balance" in worst_df.columns:
                    worst_df["Total Balance"] = worst_df["Total Balance"].map(lambda value: _format_money(value))
                st.dataframe(worst_df, width="stretch", hide_index=True)


def _render_selected_row_drift_check(row: dict[str, Any]) -> None:
    st.markdown("##### Allocation Check")
    st.caption(
        "이 영역은 성과 재검증이 아니라, 실제 또는 가정 보유 상태가 target allocation에서 얼마나 벗어났는지 보는 고급 점검입니다. "
        "입력값은 저장되지 않고 주문도 만들지 않습니다."
    )
    components = selected_portfolio_active_components(row)
    if not components:
        st.info("drift를 계산할 active component가 없습니다.")
        return

    threshold_cols = st.columns([0.34, 0.33, 0.33], gap="small")
    with threshold_cols[0]:
        drift_threshold = st.number_input(
            "Rebalance threshold (%)",
            min_value=0.5,
            max_value=50.0,
            value=5.0,
            step=0.5,
            key=f"selected_portfolio_drift_threshold_{row.get('decision_id')}",
            help="component별 target/current 차이가 이 값 이상이면 리밸런싱 검토 필요로 봅니다.",
        )
    with threshold_cols[1]:
        watch_threshold = st.number_input(
            "Watch threshold (%)",
            min_value=0.1,
            max_value=50.0,
            value=2.0,
            step=0.5,
            key=f"selected_portfolio_watch_threshold_{row.get('decision_id')}",
            help="리밸런싱 전 관찰이 필요한 drift 기준입니다.",
        )
    with threshold_cols[2]:
        total_tolerance = st.number_input(
            "Total tolerance (%)",
            min_value=0.1,
            max_value=10.0,
            value=1.0,
            step=0.1,
            key=f"selected_portfolio_total_tolerance_{row.get('decision_id')}",
            help="현재 비중 합계가 100%에서 이 범위 이상 벗어나면 입력 확인이 필요합니다.",
        )

    current_weights: dict[str, float] = {}
    input_mode = st.radio(
        "현재 보유 상태 입력 방식",
        options=["current_value", "shares_x_price", "current_weight"],
        format_func=lambda mode: FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(mode, mode),
        horizontal=True,
        key=f"selected_portfolio_current_input_mode_{row.get('decision_id')}",
    )
    value_input_contract: dict[str, Any] | None = None
    if input_mode == "current_weight":
        st.caption("이미 다른 곳에서 현재 비중을 계산해 둔 경우에만 씁니다. 기본값은 target weight입니다.")
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            target_weight = float(component.get("target_weight") or 0.0)
            with input_cols[index % 2]:
                current_weights[component_id] = st.number_input(
                    f"{title} current weight (%)",
                    min_value=0.0,
                    max_value=100.0,
                    value=target_weight,
                    step=0.5,
                    key=f"selected_portfolio_current_weight_{row.get('decision_id')}_{component_id}",
                )
    elif input_mode == "current_value":
        st.caption(
            "실제 또는 가정 보유금액을 component별로 입력하면 전체 평가금액 대비 현재 비중으로 변환합니다. "
            "통화 단위는 모두 같기만 하면 됩니다."
        )
        cash_value = st.number_input(
            "Unassigned cash / outside value",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"selected_portfolio_cash_value_{row.get('decision_id')}",
            help="target component 밖에 남아 있는 현금이나 제외 자산이 있으면 입력합니다.",
        )
        component_inputs: dict[str, dict[str, Any]] = {}
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            target_weight = float(component.get("target_weight") or 0.0)
            with input_cols[index % 2]:
                component_inputs[component_id] = {
                    "current_value": st.number_input(
                        f"{title} current value",
                        min_value=0.0,
                        value=target_weight,
                        step=1.0,
                        key=f"selected_portfolio_current_value_{row.get('decision_id')}_{component_id}",
                    ),
                    "price_source": "manual_current_value",
                }
        value_input_contract = build_selected_portfolio_current_weight_inputs(
            row,
            component_inputs=component_inputs,
            cash_value=cash_value,
            input_mode="current_value",
        )
        current_weights = dict(value_input_contract.get("current_weights") or {})
    else:
        st.caption(
            "실제 보유 수량과 현재가를 알고 있을 때 쓰는 고급 입력입니다. "
            "DB latest close는 보조값이며, 가격과 수량은 저장되지 않습니다."
        )
        component_symbols: dict[str, str] = {}
        symbol_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            default_symbol = selected_portfolio_component_default_symbol(component)
            with symbol_cols[index % 2]:
                component_symbols[component_id] = st.text_input(
                    f"{title} holding symbol",
                    value=default_symbol,
                    key=f"selected_portfolio_holding_symbol_{row.get('decision_id')}_{component_id}",
                    help="DB latest close 조회에만 쓰는 선택 입력입니다.",
                ).strip().upper()

        fetch_cols = st.columns([0.35, 0.35, 0.30], gap="small")
        with fetch_cols[0]:
            price_end = st.text_input(
                "DB price end date",
                value="",
                placeholder="YYYY-MM-DD",
                key=f"selected_portfolio_price_end_{row.get('decision_id')}",
            ).strip()
        symbols_to_fetch = sorted({symbol for symbol in component_symbols.values() if symbol})
        fetch_key = f"selected_portfolio_latest_price_result_{row.get('decision_id')}"
        with fetch_cols[1]:
            if st.button(
                "Load latest close",
                disabled=not symbols_to_fetch,
                key=f"selected_portfolio_load_latest_price_{row.get('decision_id')}",
                width="stretch",
            ):
                price_result = load_latest_selected_portfolio_prices(symbols_to_fetch, end=price_end or None)
                st.session_state[fetch_key] = price_result
                price_by_symbol = dict(price_result.get("price_by_symbol") or {})
                for index, component in enumerate(components):
                    component_id = str(component.get("component_id") or f"component_{index + 1}")
                    symbol = component_symbols.get(component_id)
                    price_row = dict(price_by_symbol.get(symbol) or {})
                    if price_row.get("price") is not None:
                        st.session_state[
                            f"selected_portfolio_holding_price_{row.get('decision_id')}_{component_id}"
                        ] = float(price_row.get("price") or 0.0)
                        st.session_state[
                            f"selected_portfolio_holding_price_date_{row.get('decision_id')}_{component_id}"
                        ] = price_row.get("latest_date")
        with fetch_cols[2]:
            st.metric("Symbols", len(symbols_to_fetch))

        latest_price_result = dict(st.session_state.get(fetch_key) or {})
        if latest_price_result.get("status") == "error":
            st.warning(f"DB latest close 조회 실패: {latest_price_result.get('error')}")
        elif latest_price_result.get("rows"):
            with st.expander("Loaded latest close rows", expanded=False):
                st.dataframe(list(latest_price_result.get("rows") or []), width="stretch", hide_index=True)
                missing = list(latest_price_result.get("missing_symbols") or [])
                if missing:
                    st.caption(f"missing symbols: {', '.join(missing)}")

        cash_value = st.number_input(
            "Unassigned cash / outside value",
            min_value=0.0,
            value=0.0,
            step=1.0,
            key=f"selected_portfolio_holding_cash_value_{row.get('decision_id')}",
            help="target component 밖에 남아 있는 현금이나 제외 자산이 있으면 입력합니다.",
        )
        component_inputs = {}
        input_cols = st.columns(2, gap="small")
        for index, component in enumerate(components):
            component_id = str(component.get("component_id") or f"component_{index + 1}")
            title = str(component.get("title") or component_id)
            price_key = f"selected_portfolio_holding_price_{row.get('decision_id')}_{component_id}"
            price_date_key = f"selected_portfolio_holding_price_date_{row.get('decision_id')}_{component_id}"
            with input_cols[index % 2]:
                shares = st.number_input(
                    f"{title} shares",
                    min_value=0.0,
                    value=0.0,
                    step=1.0,
                    key=f"selected_portfolio_holding_shares_{row.get('decision_id')}_{component_id}",
                )
                price_kwargs = {
                    "min_value": 0.0,
                    "step": 0.01,
                    "key": price_key,
                }
                if price_key not in st.session_state:
                    price_kwargs["value"] = 0.0
                price = st.number_input(f"{title} current price", **price_kwargs)
            component_inputs[component_id] = {
                "symbol": component_symbols.get(component_id),
                "shares": shares,
                "price": price,
                "price_date": st.session_state.get(price_date_key),
                "price_source": "db_latest_close" if st.session_state.get(price_date_key) else "manual_price",
            }
        value_input_contract = build_selected_portfolio_current_weight_inputs(
            row,
            component_inputs=component_inputs,
            cash_value=cash_value,
            input_mode="shares_x_price",
        )
        current_weights = dict(value_input_contract.get("current_weights") or {})

    if value_input_contract is not None:
        value_metrics = dict(value_input_contract.get("metrics") or {})
        render_badge_strip(
            [
                {"label": "Input Mode", "value": value_input_contract.get("input_mode_label"), "tone": "neutral"},
                {"label": "Portfolio Value", "value": f"{float(value_metrics.get('portfolio_value_total') or 0.0):,.2f}", "tone": "neutral"},
                {"label": "Cash / Outside", "value": f"{float(value_metrics.get('cash_value') or 0.0):,.2f}", "tone": "neutral"},
                {"label": "Weight Total", "value": f"{float(value_metrics.get('current_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            ]
        )
        input_df = build_selected_portfolio_current_weight_input_table(value_input_contract)
        if not input_df.empty:
            st.dataframe(input_df, width="stretch", hide_index=True)
        for blocker in list(value_input_contract.get("blockers") or []):
            st.warning(str(blocker))

    drift_check = build_selected_portfolio_drift_check(
        row,
        current_weights=current_weights,
        drift_threshold_pct=float(drift_threshold),
        watch_threshold_pct=float(watch_threshold),
        total_weight_tolerance_pct=float(total_tolerance),
    )
    st.session_state[f"selected_portfolio_drift_check_result_{_decision_key(row)}"] = drift_check
    metrics = dict(drift_check.get("metrics") or {})
    render_badge_strip(
        [
            {"label": "Drift Route", "value": drift_check.get("route_label"), "tone": _status_tone("rebalance_needed" if drift_check.get("route") == "REBALANCE_NEEDED" else "normal" if drift_check.get("route") == "DRIFT_ALIGNED" else "watch")},
            {"label": "Current Total", "value": f"{float(metrics.get('current_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Target Total", "value": f"{float(metrics.get('target_weight_total') or 0.0):.1f}%", "tone": "neutral"},
            {"label": "Max Drift", "value": f"{float(metrics.get('max_abs_drift') or 0.0):.1f}%", "tone": "warning" if float(metrics.get("max_abs_drift") or 0.0) >= float(drift_threshold) else "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption(str(drift_check.get("verdict") or "-"))
    drift_df = build_selected_portfolio_drift_table(drift_check)
    if not drift_df.empty:
        st.dataframe(drift_df, width="stretch", hide_index=True)
    if drift_check.get("blockers"):
        for blocker in list(drift_check.get("blockers") or []):
            st.warning(str(blocker))
    alert_preview = build_selected_portfolio_drift_alert_preview(row, drift_check=drift_check)
    st.session_state[f"selected_portfolio_drift_alert_result_{_decision_key(row)}"] = alert_preview
    alert_metrics = dict(alert_preview.get("metrics") or {})
    st.markdown("##### Drift Alert / Review Trigger Preview")
    st.caption(
        "drift 결과를 운영 경고와 Final Review review trigger 관점으로 다시 읽습니다. "
        "이 preview는 alert registry를 저장하지 않고 주문 지시도 만들지 않습니다."
    )
    render_badge_strip(
        [
            {
                "label": "Alert Route",
                "value": alert_preview.get("alert_route_label"),
                "tone": _alert_tone(str(alert_preview.get("alert_route") or "")),
            },
            {"label": "Alert Level", "value": alert_preview.get("alert_level"), "tone": "neutral"},
            {
                "label": "Review Triggers",
                "value": alert_metrics.get("review_trigger_count", 0),
                "tone": "neutral",
            },
            {"label": "Alert Save", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
        ]
    )
    st.caption(str(alert_preview.get("verdict") or "-"))
    alert_df = build_selected_portfolio_drift_alert_table(alert_preview)
    if alert_df.empty:
        st.info("표시할 drift alert / review trigger row가 없습니다.")
    else:
        st.dataframe(alert_df, width="stretch", hide_index=True)
    st.info(str(drift_check.get("next_action") or "-"))
    st.info(str(alert_preview.get("next_action") or "-"))


def render_final_selected_portfolio_dashboard_page() -> None:
    st.title("Selected Portfolio Dashboard")
    st.caption(
        "Final Review에서 실전 후보로 선정한 포트폴리오를 최신 기간으로 다시 계산하고, "
        "선정 당시 근거가 유지되는지 확인하는 Phase36 대시보드입니다."
    )

    dashboard = load_final_selected_portfolio_dashboard()
    summary = dict(dashboard.get("summary") or {})
    rows = list(dashboard.get("dashboard_rows") or [])

    render_status_card_grid(_summary_cards(summary))

    st.markdown("#### 데이터 출처와 화면 경계")
    _render_info_card_grid(
        [
            {
                "title": "Source",
                "value": "Final Review Decisions",
                "detail": "최종 선정 판단 row를 읽습니다.",
                "tone": "neutral",
            },
            {
                "title": "Selected Filter",
                "value": "Practical Portfolio",
                "detail": "`SELECT_FOR_PRACTICAL_PORTFOLIO` 또는 selected flag만 운영 대상으로 봅니다.",
                "tone": "positive",
            },
            {
                "title": "Write Policy",
                "value": "Read Only",
                "detail": "재검증과 drift 점검은 새 판단 row나 주문 row를 저장하지 않습니다.",
                "tone": "neutral",
            },
        ],
        min_width=220,
    )
    with st.expander("Registry path", expanded=False):
        st.code(str(FINAL_SELECTION_DECISION_REGISTRY_FILE), language="text")

    if not rows:
        _render_empty_state(summary)
        return

    st.markdown("#### 운영 대상 선택")
    with st.container(border=True):
        status_options = selected_portfolio_status_options(rows)
        source_type_options = selected_portfolio_source_type_options(rows)
        benchmark_options = selected_portfolio_benchmark_options(rows)
        filter_top_cols = st.columns(2, gap="small")
        with filter_top_cols[0]:
            selected_statuses = st.multiselect(
                "Status",
                options=status_options,
                default=status_options,
                format_func=lambda status: FINAL_SELECTED_PORTFOLIO_STATUS_LABELS.get(status, status),
                key="selected_portfolio_dashboard_status_filter",
            )
        with filter_top_cols[1]:
            selected_benchmark = st.selectbox(
                "Benchmark",
                options=benchmark_options,
                key="selected_portfolio_dashboard_benchmark_filter",
            )
        filter_bottom_cols = st.columns([0.64, 0.36], gap="small")
        with filter_bottom_cols[0]:
            selected_source_types = st.multiselect(
                "Source Type",
                options=source_type_options,
                default=source_type_options,
                key="selected_portfolio_dashboard_source_filter",
            )

        filtered_rows = filter_selected_portfolio_rows(
            rows,
            statuses=selected_statuses,
            source_types=selected_source_types,
            benchmark=str(selected_benchmark),
        )
        with filter_bottom_cols[1]:
            _render_info_card_grid(
                [
                    {"title": "Total", "value": len(rows), "detail": "selected rows", "tone": "neutral"},
                    {"title": "Shown", "value": len(filtered_rows), "detail": "after filter", "tone": "positive"},
                ],
                min_width=120,
            )
        if not filtered_rows:
            st.warning("현재 filter 조건에 맞는 선정 포트폴리오가 없습니다.")
            return

        st.dataframe(build_selected_portfolio_dashboard_table(filtered_rows), width="stretch", hide_index=True)
        labels = [final_selected_portfolio_label(row) for row in filtered_rows]
        selected_label = st.selectbox(
            "포트폴리오 선택",
            options=labels,
            key="selected_portfolio_dashboard_selected_row",
        )
    selected_row = filtered_rows[labels.index(selected_label)]
    _render_selected_row_detail(selected_row)
