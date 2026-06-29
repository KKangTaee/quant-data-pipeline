from __future__ import annotations

from html import escape
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.services.backtest_result_read_model import (
    build_monthly_component_balance_views,
    build_strategy_data_trust_rows,
    data_trust_status_label,
)
from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_practical_validation_handoff import queue_practical_validation_handoff_from_result_bundle
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_checkpoint_strip,
    render_readiness_route_panel,
    render_status_card_grid,
)


def _render_compare_altair_chart(
    compare_df: pd.DataFrame,
    *,
    title: str,
    y_title: str,
    show_end_markers: bool = False,
) -> None:
    long_df = (
        compare_df.reset_index()
        .melt(id_vars="Date", var_name="Strategy", value_name="Value")
        .dropna(subset=["Value"])
    )

    chart = (
        alt.Chart(long_df)
        .mark_line(point=True)
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Value:Q", title=y_title),
            color=alt.Color("Strategy:N", title="Strategy"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=",.3f"),
            ],
        )
        .properties(title=title, height=360)
    )

    if not show_end_markers:
        st.altair_chart(chart, use_container_width=True)
        return

    marker_df = long_df.sort_values("Date").groupby("Strategy", as_index=False).tail(1)
    end_points = (
        alt.Chart(marker_df)
        .mark_point(size=90, filled=True)
        .encode(
            x="Date:T",
            y="Value:Q",
            color=alt.Color("Strategy:N", legend=None),
            tooltip=[
                alt.Tooltip("Date:T", title="End Date"),
                alt.Tooltip("Strategy:N", title="Strategy"),
                alt.Tooltip("Value:Q", title=y_title, format=",.3f"),
            ],
        )
    )
    end_labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=8, dy=-8, fontSize=11)
        .encode(
            x="Date:T",
            y="Value:Q",
            text="Strategy:N",
            color=alt.Color("Strategy:N", legend=None),
        )
    )
    st.altair_chart(chart + end_points + end_labels, use_container_width=True)


def _render_swing_curve_chart(curve_df: pd.DataFrame | None, *, title: str) -> None:
    if curve_df is None or curve_df.empty:
        st.info("No comparison curve rows were produced for this suite.")
        return
    chart_df = curve_df.copy()
    chart_df["Date"] = pd.to_datetime(chart_df["Date"], errors="coerce")
    chart_df["cumulative_return"] = pd.to_numeric(chart_df["cumulative_return"], errors="coerce")
    chart = (
        alt.Chart(chart_df.dropna(subset=["Date", "cumulative_return"]))
        .mark_line(point=False)
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("cumulative_return:Q", title="Cumulative Return", axis=alt.Axis(format="%")),
            color=alt.Color("label:N", title="Variant"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("label:N", title="Variant"),
                alt.Tooltip("cumulative_return:Q", title="Cumulative Return", format=".2%"),
                alt.Tooltip("total_balance:Q", title="Total Balance", format=",.2f"),
            ],
        )
        .properties(title=title, height=280)
    )
    st.altair_chart(chart, use_container_width=True)


def _data_trust_result_integrity(meta: dict[str, Any]) -> dict[str, str]:
    price_freshness = meta.get("price_freshness") or {}
    status = str(price_freshness.get("status") or "").strip().lower()
    excluded_tickers = list(meta.get("excluded_tickers") or [])
    malformed_price_rows = list(meta.get("malformed_price_rows") or [])
    warnings = list(meta.get("warnings") or [])

    if status == "error":
        return {
            "label": "BLOCKED",
            "tone": "danger",
            "detail": "가격 최신성 오류가 있어 결과 해석 전에 데이터 보강이 필요합니다.",
        }
    if status == "warning" or excluded_tickers or malformed_price_rows or warnings:
        return {
            "label": "REVIEW",
            "tone": "warning",
            "detail": "결과는 읽을 수 있지만 기간, 제외 ticker, warning을 함께 확인해야 합니다.",
        }
    if status == "ok":
        return {
            "label": "OK",
            "tone": "positive",
            "detail": "요청 기간과 가격 최신성 기준에서 큰 차단 신호가 없습니다.",
        }
    return {
        "label": "UNKNOWN",
        "tone": "neutral",
        "detail": "가격 최신성 metadata가 제한적입니다. 결과 기간과 row 수를 먼저 확인합니다.",
    }


def _price_freshness_display(status: str | None) -> tuple[str, str]:
    normalized = str(status or "").strip().lower()
    if normalized == "ok":
        return "OK", "positive"
    if normalized == "warning":
        return "WARNING", "warning"
    if normalized == "error":
        return "ERROR", "danger"
    return "NOT ATTACHED", "neutral"


def _render_data_trust_summary(meta: dict[str, Any]) -> None:
    price_freshness = meta.get("price_freshness") or {}
    freshness_details = price_freshness.get("details") or {}
    excluded_tickers = list(meta.get("excluded_tickers") or [])
    malformed_price_rows = list(meta.get("malformed_price_rows") or [])
    integrity = _data_trust_result_integrity(meta)
    freshness_label, freshness_tone = _price_freshness_display(price_freshness.get("status"))

    st.markdown("#### Data Trust Summary")
    st.caption(
        "Checkpoint A · Result Integrity. 성과를 보기 전에 이 백테스트 결과가 어떤 데이터 범위에서 계산됐는지 확인합니다."
    )

    render_status_card_grid(
        [
            {
                "title": "Result Integrity",
                "value": integrity["label"],
                "detail": integrity["detail"],
                "tone": integrity["tone"],
            },
            {
                "title": "Price Freshness",
                "value": freshness_label,
                "detail": price_freshness.get("message") or "가격 최신성 metadata 기준",
                "tone": freshness_tone,
            },
            {
                "title": "Result Window",
                "value": meta.get("actual_result_end") or "-",
                "detail": f"Requested end: {meta.get('end') or '-'}",
                "tone": "neutral",
            },
            {
                "title": "Excluded Tickers",
                "value": len(excluded_tickers),
                "detail": "전략 계산에서 제외된 ticker 수",
                "tone": "warning" if excluded_tickers else "positive",
            },
        ]
    )

    render_badge_strip(
        [
            {"label": "Requested End", "value": meta.get("end") or "-", "tone": "neutral"},
            {"label": "Actual Result End", "value": meta.get("actual_result_end") or "-", "tone": "neutral"},
            {"label": "Result Rows", "value": meta.get("result_rows", "-"), "tone": "neutral"},
            {"label": "Malformed Rows", "value": len(malformed_price_rows), "tone": "warning" if malformed_price_rows else "positive"},
        ]
    )

    if freshness_details:
        render_badge_strip(
            [
                {"label": "Effective Trading End", "value": freshness_details.get("effective_end_date") or "-", "tone": "neutral"},
                {"label": "Common Latest Price", "value": freshness_details.get("common_latest_date") or "-", "tone": "neutral"},
                {"label": "Newest Latest Price", "value": freshness_details.get("newest_latest_date") or "-", "tone": "neutral"},
                {"label": "Latest-Date Spread", "value": f"{freshness_details.get('spread_days', 0)}d", "tone": freshness_tone},
            ]
        )
        status = str(price_freshness.get("status") or "").strip().lower()
        message = price_freshness.get("message")
        if status == "ok":
            st.success(message or "가격 최신성 점검이 통과되었습니다.")
        elif status == "warning":
            st.warning(message or "가격 최신성 점검에서 주의가 필요합니다.")
        elif status == "error":
            st.error(message or "가격 최신성 점검에 실패했습니다.")

    if excluded_tickers or malformed_price_rows:
        with st.expander("Data Quality Details", expanded=False):
            if excluded_tickers:
                st.markdown("**Excluded Tickers**")
                st.caption("전략 계산에 필요한 가격 이력이나 파생 지표가 부족해 이번 실행에서 제외된 ticker입니다.")
                st.code(", ".join(excluded_tickers))
            if malformed_price_rows:
                st.markdown("**Malformed / Missing Price Rows**")
                st.caption("가격 컬럼에 결측이 있는 ticker입니다. 공통 계산 가능 날짜가 짧아질 수 있습니다.")
                malformed_df = pd.DataFrame(malformed_price_rows).rename(
                    columns={
                        "ticker": "Ticker",
                        "price_col": "Price Column",
                        "count": "Missing Row Count",
                        "first_date": "First Missing Date",
                        "last_date": "Last Missing Date",
                        "sample_dates": "Sample Missing Dates",
                    }
                )
                st.dataframe(malformed_df, use_container_width=True, hide_index=True)

def _data_trust_status_label(status: str | None) -> str:
    return data_trust_status_label(status)


def _next_validation_step_label(value: Any) -> str:
    raw = str(value or "-")
    mapping = {
        "resolve_contract_gaps_before_shortlist": "resolve_contract_gaps_before_validation_handoff",
        "manual_review_then_paper_probation_gate": "manual_review_then_practical_validation_gate",
        "start_paper_probation_and_monitor_monthly": "send_to_practical_validation_for_paper_observation_check",
        "start_small_capital_trial_with_monthly_review": "send_to_practical_validation_for_small_capital_review",
        "resolve_failed_checks_before_probation": "resolve_preview_gaps_before_validation_handoff",
        "review_failed_checks_before_capital_increase": "review_preview_gaps_before_next_stage",
        "run_small_capital_trial_with_review_checklist": "validate_small_capital_review_conditions",
        "run_small_capital_trial": "validate_small_capital_review_conditions",
        "continue_paper_probation_until_checklist_improves": "continue_validation_review_until_preview_improves",
        "complete_robustness_review_before_paper_probation": "complete_robustness_review_before_next_stage",
        "resolve_contract_gaps_before_deployment": "resolve_contract_gaps_before_validation_handoff",
    }
    if raw in mapping:
        return mapping[raw]
    return (
        raw.replace("shortlist", "promotion_route")
        .replace("paper_probation", "paper_observation")
        .replace("small_capital_trial", "small_capital_review")
        .replace("deployment", "validation_handoff")
        .replace("probation", "validation_review")
        .replace("capital_increase", "next_stage")
        .replace("monitor_monthly", "review_in_next_stage")
    )


def _build_strategy_data_trust_rows(bundles: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return build_strategy_data_trust_rows(bundles)

def _render_strategy_data_trust_details(bundles: list[dict[str, Any]]) -> None:
    detail_found = False
    for bundle in bundles:
        meta = dict(bundle.get("meta") or {})
        excluded_tickers = list(meta.get("excluded_tickers") or [])
        malformed_price_rows = list(meta.get("malformed_price_rows") or [])
        warnings = list(meta.get("warnings") or [])
        price_freshness = dict(meta.get("price_freshness") or {})
        message = price_freshness.get("message")
        if not any([excluded_tickers, malformed_price_rows, warnings, message]):
            continue

        detail_found = True
        st.markdown(f"##### {bundle.get('strategy_name') or '-'}")
        if message:
            st.caption(str(message))
        if warnings:
            st.markdown("**Warnings**")
            for warning in warnings:
                st.warning(str(warning))
        if excluded_tickers:
            st.markdown("**Excluded Tickers**")
            st.code(", ".join(excluded_tickers))
        if malformed_price_rows:
            st.markdown("**Malformed / Missing Price Rows**")
            malformed_df = pd.DataFrame(malformed_price_rows).rename(
                columns={
                    "ticker": "Ticker",
                    "price_col": "Price Column",
                    "count": "Missing Row Count",
                    "first_date": "First Missing Date",
                    "last_date": "Last Missing Date",
                    "sample_dates": "Sample Missing Dates",
                }
            )
            st.dataframe(malformed_df, use_container_width=True, hide_index=True)
    if not detail_found:
        st.caption("이번 compare 구성에서는 별도 excluded ticker, malformed row, warning detail이 기록되지 않았습니다.")

def _render_strategy_data_trust_snapshot(
    bundles: list[dict[str, Any]],
    *,
    title: str = "Data Trust Snapshot",
    caption: str | None = None,
) -> list[dict[str, Any]]:
    rows = _build_strategy_data_trust_rows(bundles)
    if not rows:
        return []

    st.markdown(f"##### {title}")
    st.caption(
        caption
        or "여러 전략을 비교하거나 섞기 전에 각 전략이 실제로 어떤 데이터 기간과 품질 조건에서 계산됐는지 확인합니다."
    )
    st.dataframe(pd.DataFrame(rows), use_container_width=True, hide_index=True)
    with st.expander("Data Quality Details Across Strategies", expanded=False):
        _render_strategy_data_trust_details(bundles)
    return rows


def _availability_tone(is_available: bool) -> str:
    return "positive" if is_available else "warning"


def _render_latest_run_orientation(
    *,
    has_selection_history: bool,
    has_dynamic_details: bool,
    has_real_money_details: bool,
) -> None:
    st.caption(
        "Backtest Analysis는 후보를 만드는 화면입니다. 아래 체크포인트는 결과 해석 순서이며, "
        "최종 검증과 선택은 Practical Validation과 Final Review에서 이어집니다."
    )
    render_checkpoint_strip(
        [
            {
                "label": "A",
                "title": "Result Integrity",
                "detail": "Data Trust로 기간, 가격 최신성, 제외 ticker를 먼저 확인합니다.",
                "status": "Data Trust",
                "tone": "positive",
            },
            {
                "label": "B",
                "title": "Performance Shape",
                "detail": "Summary와 Equity Curve에서 수익률, 낙폭, 회복 구간을 봅니다.",
                "status": "Summary / Curve",
                "tone": "neutral",
            },
            {
                "label": "C",
                "title": "Candidate Readiness",
                "detail": "Promotion policy signal과 blocker로 다음 검토 가능성을 봅니다.",
                "status": "Policy Signal" if has_real_money_details else "Not available",
                "tone": _availability_tone(has_real_money_details),
            },
            {
                "label": "D",
                "title": "Next Action",
                "detail": "필요하면 Portfolio Mix Builder에서 조합하거나 Practical Validation 후보로 보냅니다.",
                "status": "Action after metrics",
                "tone": "neutral",
            },
        ]
    )
    render_badge_strip(
        [
            {"label": "Selection History", "value": "Available" if has_selection_history else "Strategy-specific", "tone": _availability_tone(has_selection_history)},
            {"label": "Dynamic Universe", "value": "Available" if has_dynamic_details else "Not included", "tone": "positive" if has_dynamic_details else "neutral"},
            {"label": "Policy Signal", "value": "Available" if has_real_money_details else "Not included", "tone": _availability_tone(has_real_money_details)},
            {"label": "Meta", "value": "Available", "tone": "positive"},
        ]
    )
    if not has_selection_history:
        st.caption(
            "`Selection History`는 snapshot / factor 계열처럼 리밸런싱별 선택 이력이 있는 전략에서만 표시됩니다. "
            "GTAA 같은 일부 ETF tactical 전략은 Result Table, Meta, Policy Signal에서 실행 조건을 확인합니다."
        )

def _build_practical_validation_handoff_state(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = bundle.get("meta") or {}
    evaluation = _build_next_step_readiness_evaluation(meta)
    can_submit = bool(evaluation.get("can_move_to_compare"))
    score = float(evaluation.get("score") or 0.0)
    blocking_reasons = [str(reason) for reason in list(evaluation.get("blocking_reasons") or [])]
    review_reasons = [str(reason) for reason in list(evaluation.get("review_reasons") or [])]

    if can_submit and score >= 8.0:
        status_label = "진입 가능"
        tone = "positive"
        summary = "1차 후보 판단을 통과했습니다."
        action_text = "이 결과를 2차 실전성 검증 입력 후보로 등록할 수 있습니다."
    elif can_submit:
        status_label = "조건부 진입 가능"
        tone = "warning"
        summary = "1차 후보 판단은 통과했지만, 다음 단계에서 확인할 review 신호가 있습니다."
        action_text = "Practical Validation으로 넘긴 뒤 표시된 review 신호를 우선 확인하세요."
    else:
        status_label = "진입 보류"
        tone = "danger"
        summary = "아직 1차 후보 판단을 통과하지 못했습니다."
        action_text = "버튼을 활성화하려면 Promotion / 실행 원천 / 검증 원천 blocker를 먼저 해결하세요."

    if blocking_reasons:
        display_reasons = blocking_reasons[:3]
        reason_title = "막는 이유"
    elif review_reasons:
        display_reasons = review_reasons[:3]
        reason_title = "다음 단계 확인 항목"
    else:
        display_reasons = ["막는 항목 없음"]
        reason_title = "상태"

    criteria = [
        {
            "label": "Promotion",
            "value": "통과" if bool(evaluation.get("promotion_ok")) else "보류",
            "tone": "positive" if bool(evaluation.get("promotion_ok")) else "danger",
        },
        {
            "label": "실행 원천",
            "value": (
                "통과"
                if int(evaluation.get("execution_blocker_count") or 0) == 0
                else f"block {int(evaluation.get('execution_blocker_count') or 0)}"
            ),
            "tone": "positive" if int(evaluation.get("execution_blocker_count") or 0) == 0 else "danger",
        },
        {
            "label": "검증 원천",
            "value": (
                "통과"
                if int(evaluation.get("validation_blocker_count") or 0) == 0
                else f"block {int(evaluation.get('validation_blocker_count') or 0)}"
            ),
            "tone": "positive" if int(evaluation.get("validation_blocker_count") or 0) == 0 else "danger",
        },
    ]

    return {
        "can_submit": can_submit,
        "status_label": status_label,
        "tone": tone,
        "summary": summary,
        "action_text": action_text,
        "score": score,
        "reason_title": reason_title,
        "display_reasons": display_reasons,
        "criteria": criteria,
        "evaluation": evaluation,
    }


def _render_practical_validation_handoff_card(state: dict[str, Any]) -> None:
    tone = str(state.get("tone") or "neutral")
    status = escape(str(state.get("status_label") or "-"))
    summary = escape(str(state.get("summary") or "-"))
    score = escape(f"{float(state.get('score') or 0.0):.1f} / 10")
    reason_title = escape(str(state.get("reason_title") or "상태"))
    reasons = list(state.get("display_reasons") or [])
    criteria = list(state.get("criteria") or [])
    reason_items = "".join(f"<li>{escape(str(reason))}</li>" for reason in reasons)
    criteria_items = "".join(
        '<div class="bt-handoff-chip bt-handoff-chip-{tone}">'
        '<span class="bt-handoff-chip-label">{label}</span>'
        '<span class="bt-handoff-chip-value">{value}</span>'
        "</div>".format(
            tone=escape(str(item.get("tone") or "neutral")),
            label=escape(str(item.get("label") or "-")),
            value=escape(str(item.get("value") or "-")),
        )
        for item in criteria
    )
    st.markdown(
        """
        <style>
          .bt-handoff-card {
            border: 1px solid rgba(49, 51, 63, 0.16);
            border-left: 5px solid #64748b;
            border-radius: 8px;
            padding: 1rem 1.05rem;
            margin: 0.35rem 0 0.85rem 0;
            background: #ffffff;
            box-shadow: 0 1px 3px rgba(15, 23, 42, 0.06);
          }
          .bt-handoff-positive { border-left-color: #0f766e; background: #f8fffd; }
          .bt-handoff-warning { border-left-color: #b45309; background: #fffaf0; }
          .bt-handoff-danger { border-left-color: #b91c1c; background: #fffafa; }
          .bt-handoff-head {
            display: flex;
            flex-wrap: wrap;
            align-items: center;
            justify-content: space-between;
            gap: 0.65rem;
            margin-bottom: 0.75rem;
          }
          .bt-handoff-title {
            font-size: 1.02rem;
            font-weight: 750;
            line-height: 1.35;
            color: #111827;
          }
          .bt-handoff-status {
            padding: 0.26rem 0.58rem;
            border-radius: 999px;
            border: 1px solid rgba(49, 51, 63, 0.16);
            font-size: 0.84rem;
            font-weight: 750;
            color: #111827;
            background: #f8fafc;
          }
          .bt-handoff-main {
            display: grid;
            grid-template-columns: minmax(220px, 0.9fr) minmax(260px, 1.1fr);
            gap: 0.8rem;
            align-items: stretch;
          }
          .bt-handoff-summary {
            font-size: 0.94rem;
            line-height: 1.45;
            color: #334155;
          }
          .bt-handoff-score {
            margin-top: 0.55rem;
            font-weight: 750;
            color: #111827;
          }
          .bt-handoff-chips {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.5rem;
            margin-top: 0.75rem;
          }
          .bt-handoff-chip {
            border: 1px solid rgba(49, 51, 63, 0.14);
            border-radius: 8px;
            padding: 0.62rem 0.68rem;
            background: #ffffff;
            min-width: 0;
          }
          .bt-handoff-chip-positive { border-color: rgba(15, 118, 110, 0.24); }
          .bt-handoff-chip-danger { border-color: rgba(185, 28, 28, 0.24); }
          .bt-handoff-chip-label {
            display: block;
            font-size: 0.78rem;
            color: #64748b;
            font-weight: 650;
            margin-bottom: 0.2rem;
          }
          .bt-handoff-chip-value {
            display: block;
            font-size: 0.96rem;
            font-weight: 750;
            color: #111827;
            overflow-wrap: anywhere;
          }
          .bt-handoff-reasons {
            border-radius: 8px;
            background: rgba(248, 250, 252, 0.9);
            border: 1px solid rgba(49, 51, 63, 0.12);
            padding: 0.72rem 0.82rem;
          }
          .bt-handoff-reason-title {
            font-size: 0.84rem;
            color: #64748b;
            font-weight: 700;
            margin-bottom: 0.4rem;
          }
          .bt-handoff-reasons ul {
            margin: 0;
            padding-left: 1.05rem;
            color: #334155;
            line-height: 1.45;
            font-size: 0.92rem;
          }
          @media (max-width: 760px) {
            .bt-handoff-main { grid-template-columns: 1fr; }
            .bt-handoff-chips { grid-template-columns: 1fr; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<div class="bt-handoff-card bt-handoff-{tone}">'
        f'<div class="bt-handoff-head">'
        f'<div class="bt-handoff-title">2차 실전성 검증 Handoff</div>'
        f'<div class="bt-handoff-status">{status}</div>'
        f"</div>"
        f'<div class="bt-handoff-main">'
        f'<div><div class="bt-handoff-summary">{summary}</div>'
        f'<div class="bt-handoff-score">Candidate Readiness {score}</div>'
        f'<div class="bt-handoff-chips">{criteria_items}</div></div>'
        f'<div class="bt-handoff-reasons"><div class="bt-handoff-reason-title">{reason_title}</div>'
        f"<ul>{reason_items}</ul></div>"
        f"</div>"
        f"</div>",
        unsafe_allow_html=True,
    )


def _render_practical_validation_next_action(bundle: dict[str, Any]) -> None:
    state = _build_practical_validation_handoff_state(bundle)
    _render_practical_validation_handoff_card(state)

    with st.container(border=True):
        st.markdown("##### 2차 실전성 검증 Handoff")
        st.caption(
            "이 버튼은 1차 후보 판단을 통과한 백테스트 결과를 Practical Validation이 읽을 current selection source로 등록합니다."
        )
        handoff_cols = st.columns([0.3, 0.7], gap="small")
        with handoff_cols[0]:
            if st.button(
                "실전성 검증으로 보내기",
                key="latest_run_practical_validation_handoff",
                use_container_width=True,
                disabled=not bool(state["can_submit"]),
                type="primary" if bool(state["can_submit"]) else "secondary",
            ):
                queue_practical_validation_handoff_from_result_bundle(bundle)
                st.rerun()
        with handoff_cols[1]:
            if bool(state["can_submit"]):
                st.success(str(state["action_text"]))
            else:
                st.warning(str(state["action_text"]))
            st.markdown("`Practical Validation`에서 provider / data coverage / realism / robustness를 확인합니다.")
            st.caption("최종 선택, 투자 추천, live 승인, 주문 지시는 여기서 발생하지 않습니다.")


def _render_swing_strategy_details(bundle: dict[str, Any]) -> None:
    meta = dict(bundle.get("meta") or {})
    metrics = dict(bundle.get("swing_metrics") or {})
    trade_log_df = bundle.get("swing_trade_log_df")
    scanner_df = bundle.get("swing_scanner_df")
    monthly_df = bundle.get("swing_monthly_returns_df")
    yearly_df = bundle.get("swing_yearly_returns_df")
    contribution_df = bundle.get("swing_ticker_contribution_df")
    random_df = bundle.get("swing_random_summary_df")
    comparison_df = bundle.get("swing_benchmark_comparison_df")
    v2_comparison_df = bundle.get("swing_comparison_df")
    exit_curve_df = bundle.get("swing_exit_curve_df")
    macro_curve_df = bundle.get("swing_macro_curve_df")
    holding_curve_df = bundle.get("swing_holding_curve_df")
    sensitivity_df = bundle.get("swing_sensitivity_df")
    yearly_stability_df = bundle.get("swing_yearly_stability_df")
    monthly_stability_df = bundle.get("swing_monthly_stability_df")
    ticker_dependency_df = bundle.get("swing_ticker_dependency_df")
    trade_cause_summary_df = bundle.get("swing_trade_cause_summary_df")
    quality_warning_df = bundle.get("swing_quality_warning_df")
    artifact = bundle.get("swing_artifact") or meta.get("swing_artifact") or {}

    st.caption("Close-based D+1 daily swing research detail. V2 analysis is historical research evidence, not Practical Validation, live approval, or order instruction.")
    metric_cols = st.columns(5)
    metric_cols[0].metric("Trades", str(int(metrics.get("total_trades") or 0)))
    if metrics.get("win_rate") is not None and not pd.isna(metrics.get("win_rate")):
        metric_cols[1].metric("Win Rate", f"{float(metrics.get('win_rate')):.2%}")
    if metrics.get("cagr") is not None and not pd.isna(metrics.get("cagr")):
        metric_cols[2].metric("CAGR", f"{float(metrics.get('cagr')):.2%}")
    if metrics.get("mdd") is not None and not pd.isna(metrics.get("mdd")):
        metric_cols[3].metric("MDD", f"{float(metrics.get('mdd')):.2%}")
    if metrics.get("avg_holding_days") is not None and not pd.isna(metrics.get("avg_holding_days")):
        metric_cols[4].metric("Avg Hold", f"{float(metrics.get('avg_holding_days')):.1f}d")

    render_badge_strip(
        [
            {"label": "Universe", "value": meta.get("preset_name") or meta.get("universe_mode") or "-", "tone": "neutral"},
            {"label": "Symbols", "value": meta.get("universe_symbol_count", "-"), "tone": "neutral"},
            {"label": "Execution", "value": meta.get("strategy_execution_mode") or "-", "tone": "neutral"},
            {"label": "Exit", "value": meta.get("exit_mode") or "-", "tone": "neutral"},
            {"label": "Macro", "value": meta.get("macro_filter_mode") or ("ON" if meta.get("macro_filter_enabled") else "OFF"), "tone": "positive" if meta.get("macro_filter_enabled") else "neutral"},
        ]
    )

    detail_tabs = st.tabs([
        "Comparison",
        "Sensitivity",
        "Stability",
        "Trade Causes",
        "Quality Warnings",
        "Trade Log",
        "Scanner",
        "Periods",
        "Contribution",
        "Artifact",
    ])
    with detail_tabs[0]:
        st.markdown("##### V2 One-Variable Comparisons")
        if v2_comparison_df is not None and not v2_comparison_df.empty:
            st.dataframe(v2_comparison_df, use_container_width=True, hide_index=True)
            chart_cols = st.columns(3)
            with chart_cols[0]:
                _render_swing_curve_chart(exit_curve_df, title="Exit Mode Comparison")
            with chart_cols[1]:
                _render_swing_curve_chart(macro_curve_df, title="Macro Mode Comparison")
            with chart_cols[2]:
                _render_swing_curve_chart(holding_curve_df, title="Holding Period Comparison")
        else:
            st.info("V2 comparison suite was not run for this result.")
        st.markdown("##### Benchmarks / Random Ranking")
        if comparison_df is not None and not comparison_df.empty:
            st.dataframe(comparison_df, use_container_width=True, hide_index=True)
        if random_df is not None and not random_df.empty:
            st.dataframe(random_df, use_container_width=True, hide_index=True)
    with detail_tabs[1]:
        st.caption("Sensitivity rows are bounded presets for overfit and cost-fragility inspection, not an optimizer.")
        if sensitivity_df is not None and not sensitivity_df.empty:
            st.dataframe(sensitivity_df, use_container_width=True, hide_index=True)
        else:
            st.info("V2 sensitivity suite was not run for this result.")
    with detail_tabs[2]:
        stability_tabs = st.tabs(["Yearly", "Monthly", "Ticker Dependency"])
        with stability_tabs[0]:
            if yearly_stability_df is not None and not yearly_stability_df.empty:
                st.dataframe(yearly_stability_df, use_container_width=True, hide_index=True)
            else:
                st.info("No yearly stability rows.")
        with stability_tabs[1]:
            if monthly_stability_df is not None and not monthly_stability_df.empty:
                st.dataframe(monthly_stability_df, use_container_width=True, hide_index=True)
            else:
                st.info("No monthly stability rows.")
        with stability_tabs[2]:
            if ticker_dependency_df is not None and not ticker_dependency_df.empty:
                st.dataframe(ticker_dependency_df, use_container_width=True, hide_index=True)
            else:
                st.info("No ticker dependency rows.")
    with detail_tabs[3]:
        if trade_cause_summary_df is not None and not trade_cause_summary_df.empty:
            st.dataframe(trade_cause_summary_df, use_container_width=True, hide_index=True)
        else:
            st.info("No trade cause summary rows.")
        if trade_log_df is not None and not trade_log_df.empty:
            with st.expander("Trade Cause Detail", expanded=False):
                detail_cols = [
                    col
                    for col in [
                        "entry_signal_date",
                        "exit_signal_date",
                        "symbol",
                        "exit_reason_code",
                        "net_return_pct",
                        "holding_days",
                        "ranking_score",
                        "ranking_score_raw",
                        "entry_macro_penalty_total",
                        "entry_return_20d",
                        "entry_return_5d",
                        "entry_volume_ratio",
                        "entry_ma20_distance",
                        "entry_ma50_distance",
                    ]
                    if col in trade_log_df.columns
                ]
                st.dataframe(trade_log_df[detail_cols], use_container_width=True, hide_index=True)
    with detail_tabs[4]:
        if quality_warning_df is not None and not quality_warning_df.empty:
            st.dataframe(quality_warning_df, use_container_width=True, hide_index=True)
        else:
            st.info("No quality warning rows were produced.")
    with detail_tabs[5]:
        if trade_log_df is not None and not trade_log_df.empty:
            st.dataframe(trade_log_df, use_container_width=True, hide_index=True)
        else:
            st.info("No trade rows were produced for this run.")
    with detail_tabs[6]:
        if scanner_df is not None and not scanner_df.empty:
            available_dates = sorted(scanner_df["date"].astype(str).unique().tolist())
            selected_date = st.selectbox(
                "Scanner Date",
                options=available_dates,
                index=max(0, len(available_dates) - 1),
                key="risk_on_momentum_scanner_date",
            )
            st.dataframe(
                scanner_df[scanner_df["date"].astype(str) == selected_date],
                use_container_width=True,
                hide_index=True,
            )
        else:
            st.info("No scanner rows were collected for this run.")
    with detail_tabs[7]:
        period_cols = st.columns(2, gap="large")
        with period_cols[0]:
            st.markdown("##### Monthly")
            if monthly_df is not None and not monthly_df.empty:
                st.dataframe(monthly_df, use_container_width=True, hide_index=True)
            else:
                st.info("No monthly return rows.")
        with period_cols[1]:
            st.markdown("##### Yearly")
            if yearly_df is not None and not yearly_df.empty:
                st.dataframe(yearly_df, use_container_width=True, hide_index=True)
            else:
                st.info("No yearly return rows.")
    with detail_tabs[8]:
        if contribution_df is not None and not contribution_df.empty:
            st.dataframe(contribution_df, use_container_width=True, hide_index=True)
        else:
            st.info("No closed-trade contribution rows.")
    with detail_tabs[9]:
        if artifact:
            st.json(artifact)
        else:
            st.info("No generated swing artifact was attached.")


def _render_last_run() -> None:
    error = st.session_state.backtest_last_error
    error_kind = st.session_state.backtest_last_error_kind
    bundle = st.session_state.backtest_last_bundle

    if error:
        if error_kind == "input":
            st.warning(error)
        elif error_kind == "data":
            st.error(error)
            st.caption("Hint: run the ingestion pipeline for the requested tickers and date range, then try again.")
        else:
            st.error(error)

    if not bundle:
        return

    summary_df = bundle["summary_df"]
    chart_df = bundle["chart_df"]
    result_df = bundle["result_df"]
    meta = bundle["meta"]
    warnings = list(meta.get("warnings") or [])

    st.markdown("### Latest Backtest Run")
    strategy_key = meta.get("strategy_key")
    has_selection_history = strategy_key in SNAPSHOT_SELECTION_HISTORY_STRATEGY_KEYS

    dynamic_snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    dynamic_candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []
    has_dynamic_details = bool(
        dynamic_snapshot_rows
        or dynamic_candidate_status_rows
        or meta.get("universe_contract") == HISTORICAL_DYNAMIC_PIT_UNIVERSE
    )
    has_real_money_details = bool(meta.get("real_money_hardening"))
    has_swing_details = bool(strategy_key == "risk_on_momentum_5d" or bundle.get("swing_trade_log_df") is not None)

    _render_latest_run_orientation(
        has_selection_history=has_selection_history,
        has_dynamic_details=has_dynamic_details,
        has_real_money_details=has_real_money_details,
    )

    _render_data_trust_summary(meta)

    if warnings:
        warning_lines = "\n".join(f"- {warning}" for warning in warnings)
        st.warning(
            "이번 실행에서 같이 봐야 할 주의 사항이 있습니다.\n\n"
            + warning_lines
        )

    st.markdown(f"#### {bundle['strategy_name']}")
    _render_summary_metrics(summary_df)
    _render_practical_validation_next_action(bundle)

    tab_labels = ["Summary", "Equity Curve", "Balance Extremes", "Period Extremes"]
    if has_selection_history:
        tab_labels.append("Selection History")
    if has_dynamic_details:
        tab_labels.append("Dynamic Universe")
    if has_real_money_details:
        tab_labels.append("Policy Signal")
    if has_swing_details:
        tab_labels.append("Swing Detail")
    tab_labels.extend(["Result Table", "Meta"])
    tabs = st.tabs(tab_labels)
    tab_iter = iter(tabs)
    summary_tab = next(tab_iter)
    curve_tab = next(tab_iter)
    balance_tab = next(tab_iter)
    periods_tab = next(tab_iter)
    selection_tab = next(tab_iter) if has_selection_history else None
    dynamic_tab = next(tab_iter) if has_dynamic_details else None
    real_money_tab = next(tab_iter) if has_real_money_details else None
    swing_tab = next(tab_iter) if has_swing_details else None
    table_tab = next(tab_iter)
    meta_tab = next(tab_iter)

    with summary_tab:
        st.dataframe(summary_df, use_container_width=True)

    with curve_tab:
        _render_balance_chart_with_markers(
            chart_df,
            result_df=result_df,
            title="Equity Curve",
        )
        st.caption(
            "고점 / 저점 / 마지막 지점과 최고 / 최저 기간 마커를 같이 보여줘서, "
            "단순 선 그래프보다 전략 흐름을 더 쉽게 읽을 수 있습니다."
        )

    with balance_tab:
        high_df, low_df = _build_balance_extremes_tables(chart_df, top_n=3)
        high_col, low_col = st.columns(2, gap="large")
        with high_col:
            st.markdown("##### Top 3 Balance Highs")
            st.dataframe(high_df, use_container_width=True, hide_index=True)
        with low_col:
            st.markdown("##### Top 3 Balance Lows")
            st.dataframe(low_df, use_container_width=True, hide_index=True)

    with periods_tab:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=3)
        best_col, worst_col = st.columns(2, gap="large")
        with best_col:
            st.markdown("##### Top 3 Best Periods")
            st.dataframe(best_df, use_container_width=True, hide_index=True)
        with worst_col:
            st.markdown("##### Top 3 Worst Periods")
            st.dataframe(worst_df, use_container_width=True, hide_index=True)

    if selection_tab is not None:
        with selection_tab:
            _render_snapshot_selection_history(
                result_df,
                strategy_name=bundle["strategy_name"],
                factor_names=(meta.get("quality_factors") or []) + [
                    name for name in (meta.get("value_factors") or [])
                    if name not in (meta.get("quality_factors") or [])
                ],
                snapshot_mode=meta.get("snapshot_mode"),
                snapshot_source=meta.get("snapshot_source"),
            )

    if dynamic_tab is not None:
        with dynamic_tab:
            _render_dynamic_universe_details(bundle)

    if real_money_tab is not None:
        with real_money_tab:
            _render_real_money_details(bundle)

    if swing_tab is not None:
        with swing_tab:
            _render_swing_strategy_details(bundle)

    with table_tab:
        st.dataframe(result_df, use_container_width=True)

    with meta_tab:
        left, right = st.columns([1.1, 1.2], gap="large")
        with left:
            st.markdown("##### Execution Context")
            st.markdown(f"- `Mode`: `{meta['execution_mode']}`")
            st.markdown(f"- `Data`: `{meta['data_mode']}`")
            st.markdown(f"- `Universe`: `{meta['universe_mode']}`")
            if meta.get("universe_contract"):
                st.markdown(f"- `Universe Contract`: `{meta['universe_contract']}`")
            st.markdown(f"- `Tickers`: `{', '.join(meta['tickers'])}`")
            st.markdown(f"- `Period`: `{meta['start']}` -> `{meta['end']}`")
            if meta.get("ui_elapsed_seconds") is not None:
                st.markdown(f"- `Elapsed`: `{meta['ui_elapsed_seconds']:.3f}s`")
            if meta.get("top") is not None:
                st.markdown(f"- `Top`: `{meta['top']}`")
            if meta.get("min_price_filter") is not None:
                st.markdown(f"- `Minimum Price`: `{float(meta['min_price_filter']):.2f}`")
            if meta.get("min_history_months_filter") is not None:
                st.markdown(f"- `Minimum History`: `{int(meta.get('min_history_months_filter') or 0)}M`")
            if meta.get("min_avg_dollar_volume_20d_m_filter") is not None:
                st.markdown(
                    f"- `Min Avg Dollar Volume 20D`: `{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M`"
                )
                if meta.get("liquidity_excluded_total") is not None:
                    st.markdown(
                        f"- `Liquidity Excluded`: total `{int(meta.get('liquidity_excluded_total') or 0)}`, "
                        f"rows `{int(meta.get('liquidity_excluded_active_rows') or 0)}`"
                    )
                if meta.get("liquidity_clean_coverage") is not None:
                    st.markdown(
                        f"- `Liquidity Clean Coverage`: `{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}`"
                    )
            if meta.get("transaction_cost_bps") is not None:
                st.markdown(f"- `Transaction Cost`: `{float(meta['transaction_cost_bps']):.1f} bps`")
            if meta.get("promotion_min_etf_aum_b") is not None:
                st.markdown(
                    f"- `Min ETF AUM`: `${float(meta.get('promotion_min_etf_aum_b') or 0.0):.1f}B`"
                )
            if meta.get("promotion_max_bid_ask_spread_pct") is not None:
                st.markdown(
                    f"- `Max Bid-Ask Spread`: `{float(meta.get('promotion_max_bid_ask_spread_pct') or 0.0):.2%}`"
                )
            if meta.get("benchmark_contract"):
                st.markdown(
                    f"- `Benchmark Contract`: `{_benchmark_contract_value_to_label(meta.get('benchmark_contract'))}`"
                )
            if meta.get("benchmark_ticker"):
                st.markdown(f"- `Benchmark Ticker`: `{meta['benchmark_ticker']}`")
            if _raw_guardrail_reference_ticker_value(meta):
                st.markdown(
                    f"- `Guardrail / Reference Ticker`: `{_raw_guardrail_reference_ticker_value(meta)}`"
                )
            elif meta.get("benchmark_ticker"):
                st.markdown("- `Guardrail / Reference Ticker`: `Same as Benchmark Ticker`")
            if meta.get("benchmark_symbol_count") is not None:
                st.markdown(f"- `Benchmark Universe`: `{int(meta.get('benchmark_symbol_count') or 0)}`")
            if meta.get("benchmark_eligible_symbol_count") is not None:
                st.markdown(f"- `Benchmark Eligible`: `{int(meta.get('benchmark_eligible_symbol_count') or 0)}`")
            if meta.get("benchmark_cagr") is not None:
                st.markdown(f"- `Benchmark CAGR`: `{float(meta['benchmark_cagr']):.2%}`")
            if meta.get("net_cagr_spread") is not None:
                st.markdown(f"- `Net CAGR Spread`: `{float(meta['net_cagr_spread']):.2%}`")
            if meta.get("benchmark_row_coverage") is not None:
                st.markdown(f"- `Benchmark Coverage`: `{float(meta['benchmark_row_coverage']):.2%}`")
            if meta.get("promotion_min_benchmark_coverage") is not None:
                st.markdown(
                    f"- `Min Benchmark Coverage`: `{float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_net_cagr_spread") is not None:
                st.markdown(
                    f"- `Min Net CAGR Spread`: `{float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_liquidity_clean_coverage") is not None:
                st.markdown(
                    f"- `Min Liquidity Clean Coverage`: `{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_underperformance_share") is not None:
                st.markdown(
                    f"- `Max Underperformance Share`: `{float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}`"
                )
            if meta.get("promotion_min_worst_rolling_excess_return") is not None:
                st.markdown(
                    f"- `Min Worst Rolling Excess`: `{float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_strategy_drawdown") is not None:
                st.markdown(
                    f"- `Max Strategy Drawdown`: `{float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}`"
                )
            if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
                st.markdown(
                    f"- `Max Drawdown Gap`: `{float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}`"
                )
            if meta.get("etf_operability_status"):
                st.markdown(f"- `ETF Operability Status`: `{meta.get('etf_operability_status')}`")
            if _should_show_guardrail_surface(meta):
                under_enabled = bool(meta.get("underperformance_guardrail_enabled"))
                draw_enabled = bool(meta.get("drawdown_guardrail_enabled"))
                st.markdown(
                    f"- `Underperformance Guardrail`: "
                    f"`{'ON' if under_enabled else 'OFF'}`, "
                    f"`{int(meta.get('underperformance_guardrail_window_months') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
                    f"`{float(meta.get('underperformance_guardrail_threshold') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD):.0%}`"
                )
                st.markdown(
                    f"- `Underperformance Trigger`: "
                    f"`{int(meta.get('underperformance_guardrail_trigger_count') or 0)}` / "
                    f"`{float(meta.get('underperformance_guardrail_trigger_share') or 0.0):.2%}`"
                )
                st.markdown(
                    f"- `Drawdown Guardrail`: "
                    f"`{'ON' if draw_enabled else 'OFF'}`, "
                    f"`{int(meta.get('drawdown_guardrail_window_months') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M`, "
                    f"`{float(meta.get('drawdown_guardrail_strategy_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD):.0%}`, "
                    f"`gap {float(meta.get('drawdown_guardrail_gap_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD):.0%}`"
                )
                st.markdown(
                    f"- `Drawdown Trigger`: "
                    f"`{int(meta.get('drawdown_guardrail_trigger_count') or 0)}` / "
                    f"`{float(meta.get('drawdown_guardrail_trigger_share') or 0.0):.2%}`"
                )
            if meta.get("avg_turnover") is not None:
                st.markdown(f"- `Average Turnover`: `{float(meta['avg_turnover']):.2%}`")
            if meta.get("estimated_cost_total") is not None:
                st.markdown(f"- `Estimated Cost Total`: `{float(meta['estimated_cost_total']):,.1f}`")
            if meta.get("validation_status"):
                st.markdown(f"- `Validation Status`: `{meta['validation_status']}`")
            if meta.get("benchmark_policy_status"):
                st.markdown(f"- `Benchmark Policy Status`: `{meta['benchmark_policy_status']}`")
            if meta.get("liquidity_policy_status"):
                st.markdown(f"- `Liquidity Policy Status`: `{meta['liquidity_policy_status']}`")
            if meta.get("validation_policy_status"):
                st.markdown(f"- `Validation Policy Status`: `{meta['validation_policy_status']}`")
            if meta.get("guardrail_policy_status"):
                st.markdown(f"- `Guardrail Policy Status`: `{meta['guardrail_policy_status']}`")
            if meta.get("promotion_decision"):
                st.markdown(f"- `Promotion Decision`: `{meta['promotion_decision']}`")
            if meta.get("promotion_next_step"):
                st.markdown(f"- `Promotion Next Step`: `{meta['promotion_next_step']}`")
            if meta.get("shortlist_status"):
                st.markdown(
                    f"- `Promotion Suggested Route`: `{meta['shortlist_status']}` "
                    f"(`{_shortlist_status_value_to_label(meta.get('shortlist_status'))}`)"
                )
            if meta.get("shortlist_next_step"):
                route_next_step = _next_validation_step_label(meta.get("shortlist_next_step"))
                st.markdown(f"- `Promotion Route Next Step`: `{route_next_step}`")
            if meta.get("shortlist_family"):
                st.markdown(f"- `Promotion Route Family`: `{meta['shortlist_family']}`")
            if meta.get("monitoring_focus"):
                st.markdown(
                    "- `Next Validation Focus`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("monitoring_focus") or []))
                )
            if meta.get("monitoring_breach_signals"):
                st.markdown(
                    "- `Validation Review Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("monitoring_breach_signals") or []))
                )
            if meta.get("deployment_readiness_status"):
                st.markdown(
                    f"- `Execution Preview`: `{meta['deployment_readiness_status']}` "
                    f"(`{_deployment_readiness_status_value_to_label(meta.get('deployment_readiness_status'))}`)"
                )
            if meta.get("deployment_readiness_next_step"):
                preview_next_step = _next_validation_step_label(meta.get("deployment_readiness_next_step"))
                st.markdown(f"- `Execution Preview Next Step`: `{preview_next_step}`")
            if meta.get("deployment_check_pass_count") is not None:
                st.markdown(
                    f"- `Execution Preview Counts`: pass `{int(meta.get('deployment_check_pass_count') or 0)}`, "
                    f"watch `{int(meta.get('deployment_check_watch_count') or 0)}`, "
                    f"fail `{int(meta.get('deployment_check_fail_count') or 0)}`, "
                    f"unavailable `{int(meta.get('deployment_check_unavailable_count') or 0)}`"
                )
            if meta.get("rolling_review_status"):
                st.markdown(
                    f"- `Rolling Review`: `{meta['rolling_review_status']}` "
                    f"(`{_review_status_value_to_label(meta.get('rolling_review_status'))}`)"
                )
            if meta.get("rolling_review_window_label"):
                st.markdown(f"- `Rolling Review Window`: `{meta['rolling_review_window_label']}`")
            if meta.get("rolling_review_recent_excess_return") is not None:
                st.markdown(
                    f"- `Recent Window Excess`: `{float(meta.get('rolling_review_recent_excess_return') or 0.0):.2%}`"
                )
            if meta.get("out_of_sample_review_status"):
                st.markdown(
                    f"- `Split-Period Check`: `{meta['out_of_sample_review_status']}` "
                    f"(`{_review_status_value_to_label(meta.get('out_of_sample_review_status'))}`)"
                )
            if meta.get("out_of_sample_out_sample_excess_return") is not None:
                st.markdown(
                    f"- `Back-Half Excess`: `{float(meta.get('out_of_sample_out_sample_excess_return') or 0.0):.2%}`"
                )
            if meta.get("strategy_max_drawdown") is not None:
                st.markdown(f"- `Strategy Max Drawdown`: `{float(meta['strategy_max_drawdown']):.2%}`")
            if meta.get("benchmark_max_drawdown") is not None:
                st.markdown(f"- `Benchmark Max Drawdown`: `{float(meta['benchmark_max_drawdown']):.2%}`")
            if meta.get("drawdown_gap_vs_benchmark") is not None:
                st.markdown(f"- `Drawdown Gap vs Benchmark`: `{float(meta['drawdown_gap_vs_benchmark']):.2%}`")
            if meta.get("rolling_underperformance_share") is not None:
                st.markdown(
                    f"- `Rolling Underperformance`: share `{float(meta['rolling_underperformance_share']):.2%}`, "
                    f"current streak `{int(meta.get('rolling_underperformance_current_streak') or 0)}`, "
                    f"worst excess `{float(meta.get('rolling_underperformance_worst_excess_return') or 0.0):.2%}`"
                )
            if meta.get("promotion_rationale"):
                st.markdown(
                    "- `Promotion Rationale`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("promotion_rationale") or []))
                )
            if meta.get("benchmark_policy_watch_signals"):
                st.markdown(
                    "- `Benchmark Policy Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("benchmark_policy_watch_signals") or []))
                )
            if meta.get("guardrail_policy_watch_signals"):
                st.markdown(
                    "- `Guardrail Policy Signals`: "
                    + ", ".join(f"`{item}`" for item in list(meta.get("guardrail_policy_watch_signals") or []))
                )
            if meta.get("dynamic_candidate_count") is not None:
                st.markdown(
                    f"- `Dynamic Candidate Pool`: `{meta.get('dynamic_candidate_count')}` "
                    f"(target `{meta.get('dynamic_target_size') or '-'}`)"
                )
            if dynamic_snapshot_rows or dynamic_candidate_status_rows:
                st.markdown(
                    f"- `Dynamic Detail Rows`: snapshot `{len(dynamic_snapshot_rows)}`, "
                    f"candidate `{len(dynamic_candidate_status_rows)}`"
                )
            if meta.get("trend_filter_enabled"):
                st.markdown(f"- `Trend Filter`: `MA{meta.get('trend_filter_window', STRICT_TREND_FILTER_DEFAULT_WINDOW)}`")
            if meta.get("market_regime_enabled"):
                st.markdown(
                    f"- `Market Regime`: `{meta.get('market_regime_benchmark', STRICT_MARKET_REGIME_DEFAULT_BENCHMARK)} < MA{meta.get('market_regime_window', STRICT_MARKET_REGIME_DEFAULT_WINDOW)} => cash`"
                )
            price_freshness = meta.get("price_freshness") or {}
            freshness_details = price_freshness.get("details") or {}
            if freshness_details:
                st.markdown(
                    f"- `Price Freshness`: common `{freshness_details.get('common_latest_date', '-')}`, "
                    f"newest `{freshness_details.get('newest_latest_date', '-')}`, "
                    f"spread `{freshness_details.get('spread_days', 0)}d`"
                )
            universe_debug = meta.get("universe_debug") or {}
            if universe_debug:
                st.markdown(
                    f"- `Membership Count`: avg `{universe_debug.get('avg_membership_count', '-')}`, "
                    f"min `{universe_debug.get('min_membership_count', '-')}`, "
                    f"max `{universe_debug.get('max_membership_count', '-')}`"
                )
                if universe_debug.get("price_window_start") or universe_debug.get("price_window_end"):
                    st.markdown(
                        f"- `Price Window`: `{universe_debug.get('price_window_start', '-')}` -> `{universe_debug.get('price_window_end', '-')}`"
                    )
                if universe_debug.get("profile_delisted_count") is not None or universe_debug.get("profile_issue_count") is not None:
                    st.markdown(
                        f"- `Profile Diagnostics`: active `{universe_debug.get('profile_active_count', '-')}`, "
                        f"delisted `{universe_debug.get('profile_delisted_count', '-')}`, "
                        f"issue `{universe_debug.get('profile_issue_count', '-')}`"
                    )
        with right:
            st.markdown("##### Runtime Metadata")
            st.json(meta)

def _build_balance_compare_view(bundles: list[dict]) -> pd.DataFrame:
    series_list = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy()
        name = bundle["strategy_name"]
        series = chart_df.set_index("Date")["Total Balance"].rename(name)
        series_list.append(series)

    return pd.concat(series_list, axis=1).sort_index()

def _build_monthly_component_balance_views(
    bundles: list[dict],
    *,
    strategy_names: list[str],
    weights: list[float],
    date_policy: str,
) -> tuple[pd.DataFrame, pd.DataFrame]:
    return build_monthly_component_balance_views(
        bundles,
        strategy_names=strategy_names,
        weights=weights,
        date_policy=date_policy,
    )

def _build_drawdown_compare_view(bundles: list[dict]) -> pd.DataFrame:
    drawdown_frames = []
    for bundle in bundles:
        result_df = bundle["result_df"].copy().sort_values("Date")
        balance = result_df["Total Balance"]
        drawdown = (balance / balance.cummax() - 1).rename(bundle["strategy_name"])
        drawdown_frames.append(pd.DataFrame({"Date": result_df["Date"], bundle["strategy_name"]: drawdown}))

    merged = drawdown_frames[0]
    for frame in drawdown_frames[1:]:
        merged = merged.merge(frame, on="Date", how="outer")

    return merged.sort_values("Date").set_index("Date")

def _build_total_return_compare_view(bundles: list[dict]) -> pd.DataFrame:
    series_list = []
    for bundle in bundles:
        chart_df = bundle["chart_df"].copy()
        name = bundle["strategy_name"]
        series = chart_df.set_index("Date")["Total Return"].rename(name)
        series_list.append(series)

    return pd.concat(series_list, axis=1).sort_index()

def _build_period_extremes_tables(result_df: pd.DataFrame, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    period_df = (
        result_df[["Date", "Total Return", "Total Balance"]]
        .dropna(subset=["Total Return"])
        .sort_values("Date")
        .copy()
    )

    best = (
        period_df.sort_values("Total Return", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    worst = (
        period_df.sort_values("Total Return", ascending=True)
        .head(top_n)
        .reset_index(drop=True)
    )
    return best, worst

def _build_balance_extremes_tables(chart_df: pd.DataFrame, top_n: int = 3) -> tuple[pd.DataFrame, pd.DataFrame]:
    balance_df = (
        chart_df[["Date", "Total Balance", "Total Return"]]
        .dropna(subset=["Total Balance"])
        .sort_values("Date")
        .copy()
    )

    highs = (
        balance_df.sort_values("Total Balance", ascending=False)
        .head(top_n)
        .reset_index(drop=True)
    )
    lows = (
        balance_df.sort_values("Total Balance", ascending=True)
        .head(top_n)
        .reset_index(drop=True)
    )
    return highs, lows

def _build_balance_marker_df(chart_df: pd.DataFrame, result_df: pd.DataFrame | None = None) -> pd.DataFrame:
    base_df = chart_df.copy()
    base_df["Date"] = pd.to_datetime(base_df["Date"])

    high_idx = base_df["Total Balance"].idxmax()
    low_idx = base_df["Total Balance"].idxmin()
    end_idx = base_df.index[-1]

    marker_df = pd.concat(
        [
            pd.DataFrame([base_df.loc[high_idx]]).assign(Marker="High"),
            pd.DataFrame([base_df.loc[low_idx]]).assign(Marker="Low"),
            pd.DataFrame([base_df.loc[end_idx]]).assign(Marker="End"),
        ],
        ignore_index=True,
    ).drop_duplicates(subset=["Date", "Marker"])

    if result_df is not None and not result_df.empty:
        best_df, worst_df = _build_period_extremes_tables(result_df, top_n=1)
        if not best_df.empty:
            best_row = base_df.loc[base_df["Date"] == pd.to_datetime(best_df.iloc[0]["Date"])]
            if not best_row.empty:
                marker_df = pd.concat(
                    [marker_df, best_row.assign(Marker="Best Period")],
                    ignore_index=True,
                )
        if not worst_df.empty:
            worst_row = base_df.loc[base_df["Date"] == pd.to_datetime(worst_df.iloc[0]["Date"])]
            if not worst_row.empty:
                marker_df = pd.concat(
                    [marker_df, worst_row.assign(Marker="Worst Period")],
                    ignore_index=True,
                )

    return marker_df.drop_duplicates(subset=["Date", "Marker"])

def _render_balance_chart_with_markers(
    chart_df: pd.DataFrame,
    *,
    result_df: pd.DataFrame | None = None,
    title: str = "Equity Curve",
) -> None:
    base_df = chart_df.copy()
    base_df["Date"] = pd.to_datetime(base_df["Date"])
    marker_df = _build_balance_marker_df(chart_df, result_df)

    line = (
        alt.Chart(base_df)
        .mark_line()
        .encode(
            x=alt.X("Date:T", title="Date"),
            y=alt.Y("Total Balance:Q", title="Total Balance"),
            tooltip=[
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Total Balance:Q", title="Total Balance", format=",.1f"),
                alt.Tooltip("Total Return:Q", title="Total Return", format=".3f"),
            ],
        )
    )

    points = (
        alt.Chart(marker_df)
        .mark_point(size=90, filled=True)
        .encode(
            x="Date:T",
            y="Total Balance:Q",
            color=alt.Color(
                "Marker:N",
                scale=alt.Scale(
                    domain=["High", "Low", "End", "Best Period", "Worst Period"],
                    range=["#d62728", "#1f77b4", "#2ca02c", "#ff7f0e", "#9467bd"],
                ),
            ),
            tooltip=[
                alt.Tooltip("Marker:N", title="Marker"),
                alt.Tooltip("Date:T", title="Date"),
                alt.Tooltip("Total Balance:Q", title="Total Balance", format=",.1f"),
            ],
        )
    )

    labels = (
        alt.Chart(marker_df)
        .mark_text(align="left", dx=8, dy=-8, fontSize=12)
        .encode(
            x="Date:T",
            y="Total Balance:Q",
            text="Marker:N",
            color=alt.value("#444"),
        )
    )

    st.altair_chart(
        (line + points + labels).properties(height=360, title=title),
        use_container_width=True,
    )

def _render_dynamic_universe_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    universe_debug = meta.get("universe_debug") or {}
    snapshot_rows = bundle.get("dynamic_universe_snapshot_rows") or []
    candidate_status_rows = bundle.get("dynamic_candidate_status_rows") or []

    if (
        not snapshot_rows
        and not candidate_status_rows
        and meta.get("universe_contract") != HISTORICAL_DYNAMIC_PIT_UNIVERSE
    ):
        st.caption("이번 결과는 `Historical Dynamic PIT Universe` run이 아니어서 dynamic universe 상세가 없습니다.")
        return

    st.caption(
        "`Historical Dynamic PIT Universe`에서는 리밸런싱 날짜마다 모집군을 다시 계산합니다. "
        "`dynamic_universe_snapshot_rows`는 날짜별 membership/continuity 요약이고, "
        "`dynamic_candidate_status_rows`는 후보 심볼별 가격 이력과 profile 상태를 보여줍니다."
    )

    if universe_debug:
        summary_cols = st.columns(4)
        summary_cols[0].metric("Candidate Pool", universe_debug.get("candidate_pool_count", "-"))
        summary_cols[1].metric("Target Size", universe_debug.get("target_size", "-"))
        summary_cols[2].metric("Membership Avg", universe_debug.get("avg_membership_count", "-"))
        summary_cols[3].metric("Turnover Avg", universe_debug.get("avg_turnover_count", "-"))

    if snapshot_rows:
        st.markdown("##### dynamic_universe_snapshot_rows")
        st.caption(
            "각 행은 리밸런싱 날짜 1개입니다. "
            "`membership_count`는 실제 편입 수, "
            "`continuity_ready_count`는 그 날짜를 가격 이력상 자연스럽게 커버하는 후보 수, "
            "`pre_listing_excluded_count` / `post_last_price_excluded_count`는 상장 전 또는 마지막 가격 이후라 제외된 후보 수입니다."
        )
        st.dataframe(pd.DataFrame(snapshot_rows), use_container_width=True, hide_index=True)

    if candidate_status_rows:
        st.markdown("##### dynamic_candidate_status_rows")
        st.caption(
            "각 행은 후보 심볼 1개입니다. "
            "`first_price_date` / `last_price_date`는 현재 DB 가격 이력 범위, "
            "`profile_status` / `profile_delisted_at`는 asset profile 기준 continuity 힌트입니다."
        )
        st.dataframe(pd.DataFrame(candidate_status_rows), use_container_width=True, hide_index=True)

def _build_next_step_readiness_evaluation(meta: dict[str, Any]) -> dict[str, Any]:
    promotion = str(meta.get("promotion_decision") or "").strip().lower()
    freshness_status = str((meta.get("price_freshness") or {}).get("status") or "").strip().lower()
    turnover_status = str(meta.get("turnover_estimation_status") or "").strip().lower()
    net_cost_curve_status = str(meta.get("net_cost_curve_status") or "").strip().lower()
    transaction_cost_bps = float(meta.get("transaction_cost_bps") or 0.0)

    def _source_bucket(
        value: Any,
        *,
        unavailable_blocks: bool = True,
        caution_blocks: bool = True,
    ) -> str:
        normalized = str(value or "").strip().lower()
        if not normalized or normalized in {"normal", "ok", "pass", "passed", "fresh"}:
            return "pass"
        if normalized in {"error", "missing"}:
            return "block"
        if normalized == "caution":
            return "block" if caution_blocks else "review"
        if normalized == "unavailable":
            return "block" if unavailable_blocks else "review"
        if normalized in {"watch", "warning"}:
            return "review"
        return "review"

    def _collect_source_reasons(
        specs: list[tuple[str, Any, bool, bool]],
    ) -> tuple[list[str], list[str]]:
        blockers: list[str] = []
        reviews: list[str] = []
        for label, status, unavailable_blocks, caution_blocks in specs:
            normalized = str(status or "").strip().lower()
            bucket = _source_bucket(
                normalized,
                unavailable_blocks=unavailable_blocks,
                caution_blocks=caution_blocks,
            )
            if bucket == "block":
                blockers.append(f"{label}: {normalized or '-'}")
            elif bucket == "review":
                reviews.append(f"{label}: {normalized or '-'}")
        return blockers, reviews

    execution_specs: list[tuple[str, Any, bool, bool]] = [
        ("Liquidity Policy", meta.get("liquidity_policy_status"), True, True),
        ("ETF Operability", meta.get("etf_operability_status"), True, True),
        ("Price Freshness", freshness_status, True, True),
    ]
    validation_specs: list[tuple[str, Any, bool, bool]] = [
        ("Benchmark 비교", "missing" if not bool(meta.get("benchmark_available")) else "", True, True),
        ("Validation", meta.get("validation_status"), True, True),
        ("Benchmark Policy", meta.get("benchmark_policy_status"), True, True),
        ("Validation Policy", meta.get("validation_policy_status"), True, True),
        ("Portfolio Guardrail Policy", meta.get("guardrail_policy_status"), True, True),
        # Backtest-level recent/split checks are useful warning signals, but they are not formal holdout validation.
        ("Rolling Review", meta.get("rolling_review_status"), False, False),
        ("Split-Period Check", meta.get("out_of_sample_review_status"), False, False),
    ]
    execution_blockers, execution_reviews = _collect_source_reasons(execution_specs)
    validation_blockers, validation_reviews = _collect_source_reasons(validation_specs)
    if transaction_cost_bps > 0.0 and turnover_status and turnover_status != "estimated_from_holdings":
        execution_reviews.append(f"Turnover Estimate: {turnover_status}")
    if net_cost_curve_status == "applied_without_turnover_estimate":
        execution_reviews.append("Cost Curve: turnover estimate unavailable")

    if promotion == "real_money_candidate":
        promotion_score = 4.0
        promotion_judgment = "강한 handoff policy signal"
    elif promotion == "production_candidate":
        promotion_score = 3.0
        promotion_judgment = "비교 가능, 추가 검토 필요"
    elif promotion and promotion != "hold":
        promotion_score = 2.0
        promotion_judgment = "비교 가능성은 있으나 보수적 확인 필요"
    else:
        promotion_score = 0.0
        promotion_judgment = "hold 해결 전에는 다음 단계 보류"

    if execution_blockers:
        execution_score = 0.0
        execution_judgment = "실행 원천 blocker가 남아 있음"
    elif execution_reviews:
        execution_score = 2.0
        execution_judgment = "실행 부담은 검토 가능하지만 확인 항목 있음"
    else:
        execution_score = 3.0
        execution_judgment = "실행 부담 원천 지표가 양호함"

    if validation_blockers:
        validation_score = 0.0
        validation_judgment = "검증 원천 blocker가 남아 있음"
    elif validation_reviews:
        validation_score = 2.0
        validation_judgment = "검증 근거는 있으나 후속 확인 필요"
    else:
        validation_score = 3.0
        validation_judgment = "검증 원천 지표가 양호함"

    score = round(promotion_score + execution_score + validation_score, 1)
    can_move_to_compare = (
        promotion not in {"", "hold"}
        and not execution_blockers
        and not validation_blockers
    )

    if can_move_to_compare and score >= 8.0:
        verdict = "후보 검토 진행 가능"
        tone = "success"
        route_label = "Portfolio Mix Builder 또는 Practical Validation"
        next_action = "Portfolio Mix Builder에서 다른 후보와 조합하거나 Practical Validation으로 보내 검증 근거를 확인합니다."
    elif can_move_to_compare:
        verdict = "후보 검토 가능, 개선 항목 동시 확인"
        tone = "warning"
        route_label = "조건부 후보 검토"
        next_action = "Portfolio Mix Builder 또는 Practical Validation으로 넘기기 전에 watch / preview 항목을 함께 확인합니다."
    else:
        verdict = "후보 보류: blocker 먼저 해결"
        tone = "error"
        route_label = "Hold / Review"
        next_action = "Hold 해결 가이드, 실행 부담 preview, 검토 근거의 caution 항목을 먼저 정리합니다."

    blocking_reasons: list[str] = []
    if promotion in {"", "hold"}:
        blocking_reasons.append("Promotion Decision이 hold이거나 비어 있음")
    blocking_reasons.extend(execution_blockers)
    blocking_reasons.extend(validation_blockers)

    review_reasons: list[str] = execution_reviews + validation_reviews

    criteria_rows = [
        {
            "기준": "Promotion Decision",
            "현재 값": promotion or "-",
            "점수": f"{promotion_score:g} / 4",
            "판단": promotion_judgment,
        },
        {
            "기준": "Execution Source Checks",
            "현재 값": "정상" if not execution_blockers and not execution_reviews else f"block {len(execution_blockers)} / review {len(execution_reviews)}",
            "점수": f"{execution_score:g} / 3",
            "판단": execution_judgment,
        },
        {
            "기준": "Validation Source Checks",
            "현재 값": "정상" if not validation_blockers and not validation_reviews else f"block {len(validation_blockers)} / review {len(validation_reviews)}",
            "점수": f"{validation_score:g} / 3",
            "판단": validation_judgment,
        },
    ]

    return {
        "score": score,
        "verdict": verdict,
        "tone": tone,
        "route_label": route_label,
        "next_action": next_action,
        "can_move_to_compare": can_move_to_compare,
        "criteria_rows": criteria_rows,
        "blocking_reasons": blocking_reasons,
        "review_reasons": review_reasons,
        "promotion_ok": promotion not in {"", "hold"},
        "execution_blocker_count": len(execution_blockers),
        "execution_review_count": len(execution_reviews),
        "validation_blocker_count": len(validation_blockers),
        "validation_review_count": len(validation_reviews),
    }

def _render_next_step_readiness_box(meta: dict[str, Any]) -> None:
    evaluation = _build_next_step_readiness_evaluation(meta)
    score = float(evaluation["score"])
    tone = str(evaluation["tone"])

    with st.container(border=True):
        st.markdown("##### Candidate Readiness Checkpoint")
        st.caption(
            "이 체크포인트는 투자 승인 기준이 아니라, 이 결과를 후보 비교나 Practical Validation으로 "
            "넘겨도 되는지 빠르게 보는 진단입니다."
        )
        render_readiness_route_panel(
            route_label=str(evaluation["route_label"]),
            score=score,
            blockers_count=len(evaluation["blocking_reasons"]),
            verdict=str(evaluation["verdict"]),
            next_action=str(evaluation["next_action"]),
            route_title="Next Route",
            score_title="Candidate Readiness",
        )
        st.progress(max(0.0, min(score / 10.0, 1.0)))
        st.caption(
            "점수 기준: `8.0점 이상`은 깔끔한 후보 검토, `8.0점 미만`이어도 Promotion / 실행 원천 / 검증 원천에 "
            "막는 항목이 없으면 조건부 검토, 막는 항목이 있으면 점수와 무관하게 blocker 해결이 먼저입니다."
        )

        message = (
            f"{evaluation['verdict']}: "
            f"`Promotion Decision != hold`, 실행 원천 blocker 없음, 검증 원천 blocker 없음 기준으로 계산했습니다."
        )
        if tone == "success":
            st.success(message)
        elif tone == "warning":
            st.warning(message)
        else:
            st.error(message)

        if evaluation["blocking_reasons"]:
            st.caption("막는 항목: " + ", ".join(f"`{item}`" for item in evaluation["blocking_reasons"]))
        elif evaluation["review_reasons"]:
            st.caption("같이 볼 개선 항목: " + ", ".join(f"`{item}`" for item in evaluation["review_reasons"]))
        else:
            st.caption("핵심 blocker가 보이지 않습니다. 비교 또는 Practical Validation 후보로 검토해도 되는 상태입니다.")

        with st.expander("점수 계산 기준 보기", expanded=False):
            st.dataframe(pd.DataFrame(evaluation["criteria_rows"]), use_container_width=True, hide_index=True)
            st.caption(
                "`real_money_candidate`는 가장 강한 handoff policy signal이고, "
                "`production_candidate`는 후보 검토는 가능하지만 Final Review 전 추가 검토가 필요한 상태입니다."
            )

def _render_real_money_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    if not meta.get("real_money_hardening"):
        st.caption("이 결과에는 Phase 12 promotion policy signal hardening 정보가 없습니다.")
        return

    result_df = bundle.get("result_df")
    benchmark_chart_df = bundle.get("benchmark_chart_df")
    benchmark_summary_df = bundle.get("benchmark_summary_df")

    def _render_value_list_caption(prefix: str, values: list[Any] | tuple[Any, ...] | None) -> None:
        if values:
            st.caption(prefix + ": " + ", ".join(f"`{value}`" for value in list(values)))

    def _section_header(title: str, description: str):
        section = st.container(border=True)
        with section:
            st.markdown(f"##### {title}")
            st.caption(description)
        return section

    def _status_tone(value: Any) -> str:
        normalized = str(value or "").strip().lower()
        if any(term in normalized for term in ["hold", "blocked", "reject", "fail", "caution", "breach"]):
            return "danger"
        if any(term in normalized for term in ["watch", "review", "production", "unavailable"]):
            return "warning"
        if any(term in normalized for term in ["real_money", "paper", "small_capital", "routine", "normal", "ready"]):
            return "positive"
        return "neutral"

    def _render_real_money_cards(cards: list[dict[str, Any]]) -> None:
        render_status_card_grid(cards)

    def _suggested_route_label() -> str:
        mapping = {
            "watchlist": "Watchlist Review",
            "paper_probation": "Paper Observation Candidate",
            "small_capital_trial": "Small-Capital Review Candidate",
            "hold": "Hold / Review",
        }
        return mapping.get(str(meta.get("shortlist_status") or "").strip().lower(), "-")

    def _promotion_detail() -> str:
        route = _suggested_route_label()
        next_step = str(meta.get("promotion_next_step") or "")
        if route and route != "-":
            return f"Suggested route: {route}"
        return next_step

    def _display_route_step(value: Any) -> str:
        return _next_validation_step_label(value)

    def _display_rationale_items(values: list[Any]) -> list[str]:
        return [
            str(value)
            .replace("shortlist_", "promotion_route_")
            .replace("paper_probation", "paper_observation")
            .replace("small_capital_trial", "small_capital_review")
            for value in values
        ]

    def _validation_focus_items() -> list[str]:
        return [str(item) for item in list(meta.get("monitoring_focus") or []) if str(item)]

    def _validation_review_signals() -> list[str]:
        return [str(item) for item in list(meta.get("monitoring_breach_signals") or []) if str(item)]

    def _execution_preview_label(value: Any) -> str:
        mapping = {
            "small_capital_ready": "Ready For Next Review",
            "small_capital_ready_with_review": "Review Required",
            "paper_only": "Paper Observation Check",
            "watchlist_only": "Watchlist Review",
            "review_required": "Review Required",
            "blocked": "Blocked",
        }
        return mapping.get(str(value or "").strip().lower(), "-")

    def _turnover_estimation_label(value: Any) -> str:
        mapping = {
            "estimated_from_holdings": "Holdings 기반 추정",
            "not_estimated_missing_holdings": "Holdings 근거 부족",
            "not_estimated_no_observations": "관측치 부족",
        }
        return mapping.get(str(value or "").strip().lower(), str(value or "-"))

    def _net_cost_curve_label(value: Any) -> str:
        mapping = {
            "applied_with_measurable_cost": "비용 반영됨",
            "applied_zero_cost_bps": "비용 0bps",
            "applied_without_turnover_estimate": "Turnover 근거 부족",
            "applied_no_cost_impact": "비용 영향 없음",
        }
        return mapping.get(str(value or "").strip().lower(), str(value or "-"))

    def _focus_label(value: Any) -> str:
        mapping = {
            "benchmark_relative_validation": "Benchmark-relative validation",
            "rolling_underperformance": "Rolling underperformance",
            "drawdown_control": "Drawdown control",
            "recent_regime_review": "Recent regime review",
            "split_period_consistency": "Split-period consistency",
            "liquidity_cleanliness": "Liquidity / cost realism",
            "etf_operability": "ETF operability",
            "price_freshness": "Price freshness",
        }
        return mapping.get(str(value or "").strip(), str(value or "-"))

    def _focus_rows() -> list[dict[str, Any]]:
        rows: list[dict[str, Any]] = []
        for item in _validation_focus_items():
            rows.append(
                {
                    "Type": "Focus",
                    "Item": _focus_label(item),
                    "Meaning": "Practical Validation / Final Review에서 확인할 항목",
                }
            )
        for signal in _validation_review_signals():
            rows.append(
                {
                    "Type": "Review Signal",
                    "Item": str(signal).replace("_", " "),
                    "Meaning": "Backtest 단계에서 확정하지 않고 다음 검증에서 재확인할 신호",
                }
            )
        return rows

    def _render_suggested_route_guidance(shortlist_status: str) -> None:
        if shortlist_status == "small_capital_trial":
            st.success(
                "Promotion 결과가 강해 다음 단계에서 소액 검토 가능성까지 확인해볼 수 있는 추천 경로입니다. "
                "실제 선택이나 운용 판단은 Practical Validation과 Final Review에서 다시 확인해야 합니다."
            )
        elif shortlist_status == "paper_probation":
            st.info(
                "Promotion 결과는 후보 검토가 가능하지만, 다음 단계에서 paper observation 조건을 먼저 확인하는 추천 경로입니다."
            )
        elif shortlist_status == "watchlist":
            st.info(
                "Promotion 결과는 후보로 볼 여지가 있지만, 추가 robustness와 validation focus를 먼저 확인하는 추천 경로입니다."
            )
        elif shortlist_status == "hold":
            st.warning(
                "Promotion 결과상 다음 검증으로 밀어붙이기보다 Hold / Review에 두는 추천 경로입니다. "
                "promotion / policy gap을 먼저 정리한 뒤 다시 보는 것이 좋습니다."
            )

    st.info(
        "이 탭은 Backtest 단계의 1차 후보성 해석을 한 번에 보기 위한 화면입니다. "
        "먼저 `현재 판단`에서 지금 상태를 보고, "
        "그다음 `검토 근거`에서 왜 그런 판단이 나왔는지 확인하고, "
        "`실행 부담`에서 비용/유동성/ETF 운용 가능성 preview를 본 뒤, "
        "마지막 `상세 데이터`에서 원자료를 확인하면 됩니다."
    )

    focus_count = len(_validation_focus_items())
    review_signal_count = len(_validation_review_signals())
    _render_real_money_cards(
        [
            {
                "title": "Promotion",
                "value": str(meta.get("promotion_decision") or "-").upper(),
                "detail": _promotion_detail(),
                "tone": _status_tone(meta.get("promotion_decision")),
            },
            {
                "title": "Suggested Route",
                "value": _suggested_route_label(),
                "detail": "다음 검증 후보 경로",
                "tone": _status_tone(meta.get("shortlist_status")),
            },
            {
                "title": "Validation Focus",
                "value": str(focus_count),
                "detail": "다음 단계에서 확인할 항목",
                "tone": "warning" if focus_count else "neutral",
            },
            {
                "title": "Review Signals",
                "value": str(review_signal_count),
                "detail": "확정이 아닌 재확인 신호",
                "tone": "danger" if review_signal_count else "neutral",
            },
            {
                "title": "Execution Preview",
                "value": _execution_preview_label(meta.get("deployment_readiness_status")),
                "detail": "배치 승인이 아닌 실행 부담 preview",
                "tone": _status_tone(meta.get("deployment_readiness_status")),
            },
            {
                "title": "Rolling Review",
                "value": _review_status_value_to_label(meta.get("rolling_review_status")),
                "detail": meta.get("rolling_review_window_label") or "",
                "tone": _status_tone(meta.get("rolling_review_status")),
            },
            {
                "title": "Validation",
                "value": _review_status_value_to_label(meta.get("validation_status")),
                "detail": meta.get("validation_window_label") or "",
                "tone": _status_tone(meta.get("validation_status")),
            },
        ]
    )

    overview_tab, review_tab, execution_tab, detail_tab = st.tabs(
        ["현재 판단", "검토 근거", "실행 부담", "상세 데이터"]
    )

    with overview_tab:
        st.caption(
            "이 섹션은 이 전략을 Backtest 1차 후보로 볼 수 있는지 보여줍니다. "
            "실제 paper observation, 소액 검토, 운영 모니터링 조건은 이후 단계에서 다시 정의합니다."
        )
        _render_next_step_readiness_box(meta)

        if meta.get("promotion_decision"):
            with _section_header(
                "전략 승격 판단",
                "Promotion은 이 결과를 다음 후보 검토 흐름으로 넘길 수 있는지 판단하고, 추천 경로를 함께 보여줍니다.",
            ):
                decision = str(meta.get("promotion_decision") or "-")
                next_step = str(meta.get("promotion_next_step") or "-")
                shortlist_status = str(meta.get("shortlist_status") or "")
                shortlist_label = _suggested_route_label()
                shortlist_next_step = _display_route_step(meta.get("shortlist_next_step"))
                _render_real_money_cards(
                    [
                        {
                            "title": "Decision",
                            "value": decision.upper(),
                            "detail": "현재 승격 판정",
                            "tone": _status_tone(decision),
                        },
                        {
                            "title": "Suggested Route",
                            "value": shortlist_label,
                            "detail": "다음 검증 후보 경로",
                            "tone": _status_tone(shortlist_status),
                        },
                        {
                            "title": "Promotion Next Step",
                            "value": next_step,
                            "detail": "승격 판정에서 이어지는 처리",
                            "tone": _status_tone(decision),
                        },
                        {
                            "title": "Route Next Step",
                            "value": shortlist_next_step,
                            "detail": "다음 검증 경로",
                            "tone": _status_tone(shortlist_status),
                        },
                    ]
                )
                rationale = list(meta.get("promotion_rationale") or [])
                if rationale:
                    st.caption("Promotion 판단 근거: " + ", ".join(f"`{item}`" for item in rationale))
                shortlist_rationale = list(meta.get("shortlist_rationale") or [])
                if shortlist_rationale:
                    st.caption(
                        "추천 경로 근거: "
                        + ", ".join(f"`{item}`" for item in _display_rationale_items(shortlist_rationale))
                    )
                _render_suggested_route_guidance(shortlist_status)
                if decision == "real_money_candidate":
                    st.success(
                        "현재 계약 기준에서는 실전형 후보로 읽을 수 있는 상태입니다. "
                        "다음 단계에서는 Practical Validation으로 보내 검증 근거를 확인하는 것이 자연스럽습니다."
                    )
                elif decision == "production_candidate":
                    st.info(
                        "지금은 많이 정리된 상태이지만, 더 강한 robustness 검토 전까지는 "
                        "production candidate로 두는 편이 맞습니다."
                    )
                elif decision == "hold":
                    st.warning(
                        "현재 run은 바로 승격하기보다 hold로 보는 편이 맞습니다. "
                        "validation gap 또는 contract issue를 먼저 정리하는 것이 좋습니다."
                    )
                    hold_guidance_rows = _build_hold_resolution_guidance_rows(meta)
                    with st.container(border=True):
                        st.markdown("##### Hold 해결 가이드")
                        st.caption(
                            "이 전략이 무조건 나쁘다는 뜻은 아닙니다. "
                            "지금은 승격 전에 먼저 풀어야 하는 검증 blocker가 있다는 뜻입니다."
                        )
                        st.caption(
                            "아래 표에서 `현재 상태`는 지금 막히는 정도를, "
                            "`상태를 보는 위치`는 실제 화면 위치를, "
                            "`바로 해볼 일`은 가장 먼저 손댈 설정이나 데이터를 뜻합니다."
                        )
                        if hold_guidance_rows:
                            st.dataframe(
                                pd.DataFrame(hold_guidance_rows),
                                use_container_width=True,
                                hide_index=True,
                            )
                        st.info(
                            "먼저 `검토 근거`에서 막히는 항목을 확인하고, "
                            "필요하면 `실행 부담`에서 유동성 / 비용 / ETF 운용 가능성까지 같이 점검하면 가장 빠릅니다."
                        )

        focus_rows = _focus_rows()
        if focus_rows:
            with _section_header(
                "Next Validation Focus",
                "Backtest에서 검증을 끝냈다는 뜻이 아니라, Practical Validation / Final Review에서 우선 확인할 항목입니다.",
            ):
                _render_real_money_cards(
                    [
                        {
                            "title": "Focus Items",
                            "value": str(focus_count),
                            "detail": "검증에서 볼 항목",
                            "tone": "warning" if focus_count else "neutral",
                        },
                        {
                            "title": "Review Signals",
                            "value": str(review_signal_count),
                            "detail": "재확인 신호",
                            "tone": "danger" if review_signal_count else "neutral",
                        },
                        {
                            "title": "Next Surface",
                            "value": "Practical Validation",
                            "detail": "정식 검증 위치",
                            "tone": "positive",
                        },
                    ]
                )
                st.dataframe(pd.DataFrame(focus_rows), use_container_width=True, hide_index=True)
                if review_signal_count:
                    st.warning(
                        "Backtest 단계의 review signal은 실전 관찰 결과가 아닙니다. "
                        "다음 단계에서 같은 신호가 Practical Evidence로 확인되는지 먼저 보셔야 합니다."
                    )
                else:
                    st.info(
                        "현재 Backtest 기준으로는 다음 검증에서 확인할 focus만 정리되었습니다. "
                        "실제 관찰 기간과 trigger는 Final Review 이후에 정의합니다."
                    )

        if meta.get("deployment_readiness_status"):
            with _section_header(
                "Execution Preview",
                "Backtest 단계의 실행 부담 미리보기입니다. 실제 배치 가능성은 Practical Validation과 Final Review에서 다시 판단합니다.",
            ):
                deployment_status = str(meta.get("deployment_readiness_status") or "-")
                deployment_next_step = _display_route_step(meta.get("deployment_readiness_next_step"))
                _render_real_money_cards(
                    [
                        {
                            "title": "Status",
                            "value": _execution_preview_label(deployment_status),
                            "detail": "현재 실행 부담 preview",
                            "tone": _status_tone(deployment_status),
                        },
                        {
                            "title": "Next Validation Step",
                            "value": deployment_next_step,
                            "detail": "다음 검증에서 확인할 처리",
                            "tone": _status_tone(deployment_status),
                        },
                        {
                            "title": "Pass",
                            "value": str(int(meta.get("deployment_check_pass_count") or 0)),
                            "detail": "통과 체크",
                            "tone": "positive",
                        },
                        {
                            "title": "Watch",
                            "value": str(int(meta.get("deployment_check_watch_count") or 0)),
                            "detail": "관찰 체크",
                            "tone": "warning" if int(meta.get("deployment_check_watch_count") or 0) else "neutral",
                        },
                        {
                            "title": "Fail",
                            "value": str(int(meta.get("deployment_check_fail_count") or 0)),
                            "detail": "검증 전 확인 필요",
                            "tone": "danger" if int(meta.get("deployment_check_fail_count") or 0) else "neutral",
                        },
                        {
                            "title": "Unavailable",
                            "value": str(int(meta.get("deployment_check_unavailable_count") or 0)),
                            "detail": "판단 불가 체크",
                            "tone": "warning" if int(meta.get("deployment_check_unavailable_count") or 0) else "neutral",
                        },
                    ]
                )

                deployment_rationale = list(meta.get("deployment_readiness_rationale") or [])
                if deployment_rationale:
                    st.caption("Execution preview 근거: " + ", ".join(f"`{item}`" for item in deployment_rationale))

                checklist_rows = list(meta.get("deployment_checklist_rows") or [])
                if checklist_rows:
                    display_checklist_rows: list[dict[str, Any]] = []
                    for row in checklist_rows:
                        if isinstance(row, dict):
                            display_row = dict(row)
                            if str(display_row.get("Check") or "").strip().lower() == "shortlist":
                                display_row["Check"] = "Promotion Route"
                            display_checklist_rows.append(display_row)
                        else:
                            display_checklist_rows.append({"Check": "Unknown", "Status": "-", "Detail": str(row)})
                    with st.expander("Preview 상세 보기", expanded=deployment_status in {"review_required", "blocked"}):
                        st.dataframe(pd.DataFrame(display_checklist_rows), use_container_width=True, hide_index=True)

                if deployment_status == "small_capital_ready":
                    st.success("현재 preview 기준에서는 실행 부담 원천 지표가 막히지 않아 다음 검증으로 넘겨볼 수 있습니다.")
                elif deployment_status == "small_capital_ready_with_review":
                    st.info(
                        "현재 preview 기준에서는 다음 검증으로 넘길 여지는 있지만, watch / unavailable 항목을 먼저 확인해야 합니다."
                    )
                elif deployment_status == "paper_only":
                    st.info("지금은 실제 배치 판단이 아니라 paper observation 요건을 다음 단계에서 확인하는 편이 맞습니다.")
                elif deployment_status == "review_required":
                    st.warning("failed preview 항목이 있어, Practical Validation / Final Review에서 재확인해야 합니다.")
                elif deployment_status == "blocked":
                    st.warning("현재 preview 기준에서는 다음 검증으로 넘기기 전에 blocker를 먼저 정리하는 편이 맞습니다.")

    with review_tab:
        st.caption(
            "이 섹션은 왜 이런 결론이 나왔는지 보여줍니다. "
            "benchmark 대비 성과, 최근 구간 consistency, 정책 기준 통과 여부를 함께 보시면 됩니다."
        )

        if meta.get("benchmark_available") or meta.get("benchmark_contract") or meta.get("benchmark_ticker"):
            with _section_header(
                "Benchmark / Validation 요약",
                "benchmark와 비교했을 때 현재 run이 어느 정도로 버티는지 빠르게 읽는 요약입니다.",
            ):
                benchmark_cols = st.columns(6, gap="small")
                benchmark_cols[0].metric("Benchmark Contract", _benchmark_contract_value_to_label(meta.get("benchmark_contract")))
                benchmark_cols[1].metric(
                    "Benchmark Baseline",
                    str(
                        meta.get("benchmark_label")
                        if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT
                        else meta.get("benchmark_ticker") or meta.get("benchmark_label") or "-"
                    ),
                )
                benchmark_cols[2].metric(
                    "Guardrail Reference",
                    _resolve_guardrail_reference_ticker_value(meta) or "-",
                )
                benchmark_cols[3].metric("Benchmark Available", "Yes" if meta.get("benchmark_available") else "No")
                if meta.get("benchmark_symbol_count") is not None:
                    benchmark_cols[4].metric("Benchmark Universe", str(int(meta.get("benchmark_symbol_count") or 0)))
                if meta.get("benchmark_eligible_symbol_count") is not None:
                    benchmark_cols[5].metric("Benchmark Eligible", str(int(meta.get("benchmark_eligible_symbol_count") or 0)))
                if meta.get("benchmark_end_balance") is not None:
                    st.caption(f"Benchmark End Balance `{float(meta.get('benchmark_end_balance')):,.1f}`")
                summary_lines: list[str] = []
                if meta.get("benchmark_cagr") is not None:
                    summary_lines.append(f"Benchmark CAGR `{float(meta.get('benchmark_cagr')):.2%}`")
                if meta.get("net_cagr_spread") is not None:
                    summary_lines.append(f"Net CAGR Spread `{float(meta.get('net_cagr_spread')):.2%}`")
                if meta.get("net_excess_end_balance") is not None:
                    summary_lines.append(f"Net Excess End Balance `{float(meta.get('net_excess_end_balance')):,.1f}`")
                if meta.get("benchmark_row_coverage") is not None:
                    summary_lines.append(f"Coverage `{float(meta.get('benchmark_row_coverage')):.2%}`")
                if summary_lines:
                    st.caption(" | ".join(summary_lines))
                if meta.get("benchmark_contract") == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
                    st.caption(
                        "Candidate-universe equal-weight benchmark는 같은 후보 universe를 단순히 균등 보유했을 때의 reference curve입니다."
                    )
                    st.caption(
                        "이 경우 `Guardrail Reference`는 benchmark curve 자체가 아니라 underperformance / drawdown guardrail이 따로 참고하는 ticker입니다."
                    )

        if meta.get("benchmark_available"):
            with _section_header(
                "Validation Surface",
                "benchmark 대비 최근 구간에서 얼마나 자주 뒤처졌는지, 낙폭이 얼마나 깊었는지를 요약합니다.",
            ):
                validation_cols = st.columns(4, gap="small")
                validation_cols[0].metric("Validation Status", str(meta.get("validation_status") or "normal").upper())
                if meta.get("strategy_max_drawdown") is not None:
                    validation_cols[1].metric("Strategy Max Drawdown", f"{float(meta.get('strategy_max_drawdown')):.2%}")
                if meta.get("benchmark_max_drawdown") is not None:
                    validation_cols[2].metric("Benchmark Max Drawdown", f"{float(meta.get('benchmark_max_drawdown')):.2%}")
                validation_cols[3].metric("Rolling Window", str(meta.get("validation_window_label") or "-"))

                rolling_cols = st.columns(4, gap="small")
                if meta.get("rolling_underperformance_share") is not None:
                    rolling_cols[0].metric("Underperformance Share", f"{float(meta.get('rolling_underperformance_share')):.2%}")
                rolling_cols[1].metric("Current Underperf Streak", str(int(meta.get("rolling_underperformance_current_streak") or 0)))
                rolling_cols[2].metric("Longest Underperf Streak", str(int(meta.get("rolling_underperformance_longest_streak") or 0)))
                if meta.get("rolling_underperformance_worst_excess_return") is not None:
                    rolling_cols[3].metric(
                        "Worst Rolling Excess",
                        f"{float(meta.get('rolling_underperformance_worst_excess_return')):.2%}",
                    )
                _render_value_list_caption("Validation watch signals", meta.get("validation_watch_signals"))

                status = str(meta.get("validation_status") or "normal")
                if status == "caution":
                    st.warning(
                        "Benchmark-relative drawdown 또는 rolling underperformance 진단이 높게 나왔습니다. "
                        "실전 승격 전 재검토가 필요한 상태로 보는 편이 맞습니다."
                    )
                elif status == "watch":
                    st.info(
                        "일부 benchmark-relative validation 지표가 watch 상태입니다. "
                        "추가 구간 검증이나 contract robustness 확인이 권장됩니다."
                    )

        if meta.get("rolling_review_status") or meta.get("out_of_sample_review_status"):
            with _section_header(
                "최근 구간 / 간이 전후반 구간 점검",
                "최근 구간과 전후반 구간을 따로 봐서, 특정 시기 우연인지 아니면 비교적 꾸준한지 확인하는 1차 점검입니다.",
            ):
                review_cols = st.columns(5, gap="small")
                review_cols[0].metric("Rolling Review", _review_status_value_to_label(meta.get("rolling_review_status")))
                review_cols[1].metric("Rolling Window", str(meta.get("rolling_review_window_label") or "-"))
                if meta.get("rolling_review_recent_excess_return") is not None:
                    review_cols[2].metric("Recent Excess", f"{float(meta.get('rolling_review_recent_excess_return')):.2%}")
                if meta.get("rolling_review_recent_drawdown_gap") is not None:
                    review_cols[3].metric("Recent DD Gap", f"{float(meta.get('rolling_review_recent_drawdown_gap')):.2%}")
                review_cols[4].metric("Split-Period Check", _review_status_value_to_label(meta.get("out_of_sample_review_status")))

                split_cols = st.columns(3, gap="small")
                if meta.get("out_of_sample_in_sample_excess_return") is not None:
                    split_cols[0].metric("Front-Half Excess", f"{float(meta.get('out_of_sample_in_sample_excess_return')):.2%}")
                if meta.get("out_of_sample_out_sample_excess_return") is not None:
                    split_cols[1].metric("Back-Half Excess", f"{float(meta.get('out_of_sample_out_sample_excess_return')):.2%}")
                if meta.get("out_of_sample_excess_change") is not None:
                    split_cols[2].metric("Excess Change", f"{float(meta.get('out_of_sample_excess_change')):.2%}")

                if meta.get("rolling_review_recent_start") is not None and meta.get("rolling_review_recent_end") is not None:
                    st.caption(
                        "Recent review window: "
                        f"`{meta.get('rolling_review_recent_start')}` -> `{meta.get('rolling_review_recent_end')}`"
                    )
                rolling_review_rationale = list(meta.get("rolling_review_rationale") or [])
                if rolling_review_rationale:
                    st.caption("Rolling review rationale: " + ", ".join(f"`{item}`" for item in rolling_review_rationale))
                if meta.get("out_of_sample_in_sample_start") is not None and meta.get("out_of_sample_out_sample_end") is not None:
                    st.caption(
                        "Simple split-period check: "
                        f"front half `{meta.get('out_of_sample_in_sample_start')}` -> `{meta.get('out_of_sample_in_sample_end')}`, "
                        f"back half `{meta.get('out_of_sample_out_sample_start')}` -> `{meta.get('out_of_sample_out_sample_end')}`"
                    )
                out_of_sample_review_rationale = list(meta.get("out_of_sample_review_rationale") or [])
                if out_of_sample_review_rationale:
                    st.caption("Split-period rationale: " + ", ".join(f"`{item}`" for item in out_of_sample_review_rationale))

                if str(meta.get("rolling_review_status") or "").strip().lower() == "caution" or str(
                    meta.get("out_of_sample_review_status") or ""
                ).strip().lower() == "caution":
                    st.warning(
                        "최근 구간 또는 간이 전후반 구간 점검에서 caution이 잡혔습니다. "
                        "지금은 후속 검증에서 recent regime robustness를 먼저 확인하는 편이 맞습니다."
                    )
                elif str(meta.get("rolling_review_status") or "").strip().lower() == "watch" or str(
                    meta.get("out_of_sample_review_status") or ""
                ).strip().lower() == "watch":
                    st.info(
                        "최근 구간 / 전후반 구간 점검은 완전히 깨지진 않았지만, current regime robustness를 조금 더 보수적으로 해석하는 편이 좋습니다."
                    )

        if (
            meta.get("benchmark_policy_status")
            or meta.get("liquidity_policy_status")
            or meta.get("validation_policy_status")
            or meta.get("guardrail_policy_status")
        ):
            with st.expander("세부 정책 기준 보기", expanded=False):
                st.caption(
                    "아래 항목은 승격 판단에 사용된 세부 정책 기준입니다. "
                    "평소에는 summary만 보고, 정책이 왜 `watch`나 `caution`인지 확인할 때만 펼쳐 보면 됩니다."
                )

                if meta.get("benchmark_policy_status"):
                    st.markdown("##### Benchmark Policy")
                    policy_cols = st.columns(5, gap="small")
                    policy_cols[0].metric("Policy Status", str(meta.get("benchmark_policy_status") or "normal").upper())
                    if meta.get("promotion_min_benchmark_coverage") is not None:
                        policy_cols[1].metric("Min Coverage", f"{float(meta.get('promotion_min_benchmark_coverage') or 0.0):.0%}")
                    if meta.get("benchmark_row_coverage") is not None:
                        policy_cols[2].metric("Actual Coverage", f"{float(meta.get('benchmark_row_coverage') or 0.0):.2%}")
                    if meta.get("promotion_min_net_cagr_spread") is not None:
                        policy_cols[3].metric("Min Net CAGR Spread", f"{float(meta.get('promotion_min_net_cagr_spread') or 0.0):.0%}")
                    if meta.get("net_cagr_spread") is not None:
                        policy_cols[4].metric("Actual Net CAGR Spread", f"{float(meta.get('net_cagr_spread') or 0.0):.2%}")
                    _render_value_list_caption("Benchmark policy signals", meta.get("benchmark_policy_watch_signals"))
                    policy_status = str(meta.get("benchmark_policy_status") or "normal").lower()
                    if policy_status == "caution":
                        st.warning("현재 benchmark policy 기준에서는 coverage 또는 상대 CAGR이 충분하지 않습니다. 승격 전 추가 검토가 필요한 상태입니다.")
                    elif policy_status == "watch":
                        st.info("Benchmark policy 기준에서 일부 watch 신호가 있습니다. 실전 승격 전 robustness 확인을 더 하는 편이 좋습니다.")

                if meta.get("liquidity_policy_status"):
                    st.markdown("##### Liquidity Policy")
                    liquidity_policy_cols = st.columns(4, gap="small")
                    liquidity_policy_cols[0].metric("Policy Status", str(meta.get("liquidity_policy_status") or "normal").upper())
                    if meta.get("promotion_min_liquidity_clean_coverage") is not None:
                        liquidity_policy_cols[1].metric("Min Clean Coverage", f"{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}")
                    if meta.get("liquidity_clean_coverage") is not None:
                        liquidity_policy_cols[2].metric("Actual Clean Coverage", f"{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}")
                    if meta.get("liquidity_excluded_active_rows") is not None:
                        liquidity_policy_cols[3].metric("Liquidity Excluded Rows", str(int(meta.get("liquidity_excluded_active_rows") or 0)))
                    _render_value_list_caption("Liquidity policy signals", meta.get("liquidity_policy_watch_signals"))
                    liquidity_policy_status = str(meta.get("liquidity_policy_status") or "normal").lower()
                    if liquidity_policy_status == "caution":
                        st.warning("현재 liquidity policy 기준에서는 유동성 제외가 너무 자주 발생했습니다. 실전 승격 전 후보군 또는 investability 계약을 다시 점검하는 편이 맞습니다.")
                    elif liquidity_policy_status == "watch":
                        st.info("Liquidity policy 기준에서 watch 신호가 있습니다. 유동성 제외 빈도와 후보군 구성을 한 번 더 검토하는 편이 좋습니다.")
                    elif liquidity_policy_status == "unavailable":
                        st.info("Liquidity policy는 현재 unavailable 상태입니다. 실전 승격 기준으로 보려면 `Min Avg Dollar Volume 20D` 필터를 함께 사용하는 편이 좋습니다.")

                if meta.get("validation_policy_status"):
                    st.markdown("##### Validation Policy")
                    validation_policy_cols = st.columns(5, gap="small")
                    validation_policy_cols[0].metric("Policy Status", str(meta.get("validation_policy_status") or "normal").upper())
                    if meta.get("promotion_max_underperformance_share") is not None:
                        validation_policy_cols[1].metric("Max Underperf Share", f"{float(meta.get('promotion_max_underperformance_share') or 0.0):.0%}")
                    if meta.get("rolling_underperformance_share") is not None:
                        validation_policy_cols[2].metric("Actual Underperf Share", f"{float(meta.get('rolling_underperformance_share') or 0.0):.2%}")
                    if meta.get("promotion_min_worst_rolling_excess_return") is not None:
                        validation_policy_cols[3].metric("Min Worst Excess", f"{float(meta.get('promotion_min_worst_rolling_excess_return') or 0.0):.0%}")
                    if meta.get("rolling_underperformance_worst_excess_return") is not None:
                        validation_policy_cols[4].metric("Actual Worst Excess", f"{float(meta.get('rolling_underperformance_worst_excess_return') or 0.0):.2%}")
                    _render_value_list_caption("Validation policy signals", meta.get("validation_policy_watch_signals"))
                    validation_policy_status = str(meta.get("validation_policy_status") or "normal").lower()
                    if validation_policy_status == "caution":
                        st.warning("현재 validation policy 기준에서는 rolling underperformance robustness가 충분하지 않습니다. 실전 승격 전 계약을 더 보수적으로 보는 편이 맞습니다.")
                    elif validation_policy_status == "watch":
                        st.info("Validation policy 기준에서 watch 신호가 있습니다. 추가 구간 robustness 검증을 더 하는 편이 좋습니다.")
                    elif validation_policy_status == "unavailable":
                        st.info("Validation policy는 현재 unavailable 상태입니다. aligned benchmark validation history가 있어야 승격 기준으로 해석할 수 있습니다.")

                if meta.get("guardrail_policy_status"):
                    st.markdown("##### Portfolio Guardrail Policy")
                    guardrail_policy_cols = st.columns(5, gap="small")
                    guardrail_policy_cols[0].metric("Policy Status", str(meta.get("guardrail_policy_status") or "normal").upper())
                    if meta.get("promotion_max_strategy_drawdown") is not None:
                        guardrail_policy_cols[1].metric("Max Strategy DD", f"{float(meta.get('promotion_max_strategy_drawdown') or 0.0):.0%}")
                    if meta.get("strategy_max_drawdown") is not None:
                        guardrail_policy_cols[2].metric("Actual Strategy DD", f"{float(meta.get('strategy_max_drawdown') or 0.0):.2%}")
                    if meta.get("promotion_max_drawdown_gap_vs_benchmark") is not None:
                        guardrail_policy_cols[3].metric("Max DD Gap", f"{float(meta.get('promotion_max_drawdown_gap_vs_benchmark') or 0.0):.0%}")
                    if meta.get("drawdown_gap_vs_benchmark") is not None:
                        guardrail_policy_cols[4].metric("Actual DD Gap", f"{float(meta.get('drawdown_gap_vs_benchmark') or 0.0):.2%}")
                    _render_value_list_caption("Guardrail policy signals", meta.get("guardrail_policy_watch_signals"))
                    guardrail_policy_status = str(meta.get("guardrail_policy_status") or "normal").lower()
                    if guardrail_policy_status == "caution":
                        st.warning("현재 portfolio guardrail policy 기준에서는 낙폭 방어가 충분하지 않습니다. 실전 승격 전 drawdown contract를 더 보수적으로 보는 편이 맞습니다.")
                    elif guardrail_policy_status == "watch":
                        st.info("Portfolio guardrail policy 기준에서 watch 신호가 있습니다. 최대 낙폭과 benchmark 대비 drawdown gap을 한 번 더 점검하는 편이 좋습니다.")
                    elif guardrail_policy_status == "unavailable":
                        st.info("Portfolio guardrail policy는 현재 unavailable 상태입니다. 실전 승격 기준으로 보려면 usable benchmark drawdown history가 필요합니다.")

        if benchmark_chart_df is not None and result_df is not None:
            with _section_header(
                "Strategy vs Benchmark Chart",
                "전략의 net 곡선과 benchmark reference curve를 겹쳐서 봅니다. 최근 구간에서 벌어지는 방향을 읽을 때 유용합니다.",
            ):
                strategy_line = (
                    bundle["chart_df"][["Date", "Total Balance"]]
                    .rename(columns={"Total Balance": bundle["strategy_name"]})
                    .set_index("Date")
                )
                benchmark_line = (
                    benchmark_chart_df[["Date", "Benchmark Total Balance"]]
                    .rename(
                        columns={
                            "Benchmark Total Balance": str(
                                meta.get("benchmark_label") or meta.get("benchmark_ticker") or "Benchmark"
                            )
                        }
                    )
                    .set_index("Date")
                )
                overlay_df = pd.concat([strategy_line, benchmark_line], axis=1).sort_index()
                _render_compare_altair_chart(
                    overlay_df,
                    title="Net Strategy vs Benchmark",
                    y_title="Total Balance",
                    show_end_markers=True,
                )
                st.caption("전략은 비용 반영 후 `net` 곡선이고, benchmark는 비용을 반영하지 않은 단순 reference curve입니다.")

    with execution_tab:
        st.caption(
            "이 섹션은 이 전략을 실제로 운용할 때 드는 부담을 봅니다. "
            "가격/유동성/turnover/비용/ETF 운용 가능성, 그리고 실제 방어 규칙이 여기에 모여 있습니다."
        )

        with _section_header(
            "실행 계약 요약",
            "가격, 이력, 유동성, turnover, 비용처럼 실제 운용 시 바로 영향을 주는 기본 조건을 보여줍니다.",
        ):
            turnover_status = str(meta.get("turnover_estimation_status") or "").strip().lower()
            net_cost_status = str(meta.get("net_cost_curve_status") or "").strip().lower()
            transaction_cost_bps = float(meta.get("transaction_cost_bps") or 0.0)
            turnover_estimated = turnover_status == "estimated_from_holdings"
            avg_turnover = meta.get("avg_turnover")
            estimated_cost_total = meta.get("estimated_cost_total")
            avg_turnover_display = (
                f"{float(avg_turnover):.2%}"
                if turnover_estimated and avg_turnover is not None
                else "N/A"
            )
            estimated_cost_display = (
                f"{float(estimated_cost_total or 0.0):,.1f}"
                if transaction_cost_bps <= 0.0 or net_cost_status != "applied_without_turnover_estimate"
                else "N/A"
            )
            top_cols = st.columns(6, gap="small")
            top_cols[0].metric("Minimum Price", f"{float(meta.get('min_price_filter') or 0.0):.2f}")
            top_cols[1].metric("Minimum History", f"{int(meta.get('min_history_months_filter') or 0)}M")
            top_cols[2].metric("Min Avg Dollar Volume 20D", f"{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M")
            top_cols[3].metric("Transaction Cost", f"{transaction_cost_bps:.1f} bps")
            top_cols[4].metric("Avg Turnover", avg_turnover_display)
            top_cols[5].metric("Estimated Cost Total", estimated_cost_display)
            st.caption(
                "Turnover estimate: "
                f"`{_turnover_estimation_label(turnover_status)}` | "
                "Cost curve: "
                f"`{_net_cost_curve_label(net_cost_status)}`"
            )
            if transaction_cost_bps > 0.0 and not turnover_estimated:
                st.warning(
                    "Turnover를 holdings 기반으로 추정하지 못해 비용 영향이 낮게 보일 수 있습니다. "
                    "이 경우 `Avg Turnover`와 `Estimated Cost Total`은 강한 실전성 근거로 보지 않는 편이 맞습니다."
                )
            if meta.get("liquidity_excluded_total") is not None:
                st.caption(
                    "Liquidity excluded candidates: "
                    f"`{int(meta.get('liquidity_excluded_total') or 0)}` total, "
                    f"`{int(meta.get('liquidity_excluded_active_rows') or 0)}` rows."
                )
            if meta.get("liquidity_clean_coverage") is not None:
                st.caption("Liquidity clean coverage on rebalance rows: " f"`{float(meta.get('liquidity_clean_coverage') or 0.0):.2%}`")

        if meta.get("liquidity_policy_status") or meta.get("promotion_min_liquidity_clean_coverage") is not None:
            with _section_header(
                "Liquidity Policy",
                "유동성 때문에 실제 운용 해석이 가능한지 보는 섹션입니다. "
                "특히 `unavailable`이면 현재 설정만으로는 유동성 검증을 아예 하지 못하고 있다는 뜻입니다.",
            ):
                liquidity_policy_status = str(meta.get("liquidity_policy_status") or "unavailable").lower()
                liquidity_policy_cols = st.columns(5, gap="small")
                liquidity_policy_cols[0].metric("Policy Status", liquidity_policy_status.upper())
                liquidity_policy_cols[1].metric(
                    "Min Avg Dollar Volume 20D",
                    f"{float(meta.get('min_avg_dollar_volume_20d_m_filter') or 0.0):.1f}M",
                )
                liquidity_policy_cols[2].metric(
                    "Min Clean Coverage",
                    f"{float(meta.get('promotion_min_liquidity_clean_coverage') or 0.0):.0%}",
                )
                liquidity_policy_cols[3].metric(
                    "Actual Clean Coverage",
                    (
                        f"{float(meta.get('liquidity_clean_coverage')):.2%}"
                        if meta.get("liquidity_clean_coverage") is not None
                        else "-"
                    ),
                )
                liquidity_policy_cols[4].metric(
                    "Liquidity Excluded Rows",
                    str(int(meta.get("liquidity_excluded_active_rows") or 0)),
                )

                st.caption(
                    "`Min Avg Dollar Volume 20D`는 최근 20거래일 평균 거래대금 기준이고, "
                    "`Liquidity Clean Coverage`는 리밸런싱 시점 중 유동성 제외 없이 지나간 비율입니다."
                )

                liquidity_policy_signals = [
                    _liquidity_policy_signal_to_korean_label(item)
                    for item in list(meta.get("liquidity_policy_watch_signals") or [])
                ]
                _render_value_list_caption("Liquidity policy signals", liquidity_policy_signals)

                min_avg_dollar_volume = float(meta.get("min_avg_dollar_volume_20d_m_filter") or 0.0)
                clean_coverage = meta.get("liquidity_clean_coverage")

                if liquidity_policy_status == "normal":
                    st.success(
                        "현재 유동성 정책 기준에서는 특별한 blocker가 없습니다. "
                        "실전 해석에서 유동성 쪽은 비교적 안정적으로 통과한 상태입니다."
                    )
                elif liquidity_policy_status == "watch":
                    st.info(
                        "현재 유동성 정책은 watch 상태입니다. "
                        "당장 막히는 수준은 아니지만, 유동성 제외 빈도가 기준에 가까워서 후보군을 조금 더 점검하는 편이 좋습니다."
                    )
                elif liquidity_policy_status == "caution":
                    st.warning(
                        "현재 유동성 정책은 caution 상태입니다. "
                        "리밸런싱 시점에서 유동성 제외가 너무 자주 발생해 실전 승격을 바로 열기 어렵습니다."
                    )
                    st.info(
                        "먼저 `Min Avg Dollar Volume 20D` 기준을 확인하고, 거래가 얇은 종목이 자주 걸리는지 후보군을 다시 점검해보세요."
                    )
                elif liquidity_policy_status == "unavailable":
                    if min_avg_dollar_volume <= 0.0:
                        st.warning(
                            "현재는 `Min Avg Dollar Volume 20D`가 `0.0M`이라 유동성 정책을 실제로 판정하지 못했습니다."
                        )
                        st.info(
                            "해결 방법: `Advanced Inputs`에서 `Min Avg Dollar Volume 20D`를 `0`보다 큰 값으로 설정한 뒤 다시 실행하세요. "
                            "즉 지금은 유동성 필터를 꺼둔 상태라, 승격 판단용 liquidity review가 비활성화된 것입니다."
                        )
                    elif clean_coverage is None:
                        st.warning(
                            "유동성 필터 값은 있지만, `Liquidity Clean Coverage`가 계산되지 않아 정책 판단을 못 하고 있습니다."
                        )
                        st.info(
                            "해결 방법: 결과 데이터에 유동성 제외/coverage가 실제로 계산됐는지 확인하고, 필요하면 기간이나 universe contract를 다시 점검하세요."
                        )
                    else:
                        st.info(
                            "현재 설정만으로는 유동성 정책을 충분히 해석하기 어렵습니다. "
                            "유동성 필터 값과 clean coverage 계산 여부를 함께 확인하는 편이 좋습니다."
                        )

        if (
            meta.get("promotion_min_etf_aum_b") is not None
            or meta.get("promotion_max_bid_ask_spread_pct") is not None
            or meta.get("etf_operability_status")
        ):
            with _section_header(
                "ETF 운용 가능성",
                "ETF 전략에서만 보이는 항목입니다. 현재 시점 기준으로 ETF 규모와 bid-ask spread가 너무 불안정하지 않은지 확인합니다.",
            ):
                etf_cols = st.columns(5, gap="small")
                etf_cols[0].metric("Policy Status", str(meta.get("etf_operability_status") or "unavailable").upper())
                if meta.get("promotion_min_etf_aum_b") is not None:
                    etf_cols[1].metric("Min ETF AUM", f"${float(meta.get('promotion_min_etf_aum_b') or 0.0):.1f}B")
                if meta.get("promotion_max_bid_ask_spread_pct") is not None:
                    etf_cols[2].metric("Max Bid-Ask Spread", f"{float(meta.get('promotion_max_bid_ask_spread_pct') or 0.0):.2%}")
                if meta.get("etf_operability_clean_coverage") is not None:
                    etf_cols[3].metric("Clean Coverage", f"{float(meta.get('etf_operability_clean_coverage') or 0.0):.2%}")
                if meta.get("etf_operability_clean_pass_count") is not None:
                    etf_cols[4].metric("Clean Pass", f"{int(meta.get('etf_operability_clean_pass_count') or 0)} / {int(meta.get('etf_symbol_count') or 0)}")
                if meta.get("etf_operability_data_coverage") is not None:
                    st.caption(f"ETF operability data coverage: `{float(meta.get('etf_operability_data_coverage') or 0.0):.2%}`")
                if meta.get("etf_aum_pass_count") is not None or meta.get("etf_spread_pass_count") is not None:
                    st.caption(
                        "Pass counts: "
                        f"AUM `{int(meta.get('etf_aum_pass_count') or 0)}` / `{int(meta.get('etf_symbol_count') or 0)}`, "
                        f"Spread `{int(meta.get('etf_spread_pass_count') or 0)}` / `{int(meta.get('etf_symbol_count') or 0)}`"
                    )
                with st.expander("문제 ETF / 누락 데이터 보기", expanded=False):
                    _render_value_list_caption("AUM-below-policy ETF", meta.get("etf_aum_failed_symbols"))
                    _render_value_list_caption("Spread-above-policy ETF", meta.get("etf_spread_failed_symbols"))
                    _render_value_list_caption("Missing ETF operability fields", meta.get("etf_operability_missing_data_symbols"))
                    _render_value_list_caption("ETF operability signals", meta.get("etf_operability_watch_signals"))
                etf_status = str(meta.get("etf_operability_status") or "unavailable").lower()
                if etf_status == "caution":
                    st.warning("현재 ETF operability policy 기준에서는 자산 규모나 bid-ask spread가 충분히 안정적이지 않습니다. 실전 승격 전 ETF universe를 다시 점검하는 편이 맞습니다.")
                elif etf_status == "watch":
                    st.info("ETF operability policy 기준에서 일부 watch 신호가 있습니다. 현재 AUM과 bid-ask spread를 한 번 더 점검하는 편이 좋습니다.")
                elif etf_status == "unavailable":
                    st.info("ETF operability policy는 현재 unavailable 상태입니다. ETF asset profile을 새로 수집한 뒤 다시 해석하는 편이 맞습니다.")

        if _should_show_guardrail_surface(meta):
            with _section_header(
                "실제 방어 규칙",
                "경고만 보여주는 것이 아니라, 조건이 깨지면 실제 rebalance를 더 보수적으로 만들 수 있는 규칙입니다.",
            ):
                under_enabled = bool(meta.get("underperformance_guardrail_enabled"))
                draw_enabled = bool(meta.get("drawdown_guardrail_enabled"))

                guardrail_cols = st.columns(5, gap="small")
                guardrail_cols[0].metric("Underperformance Guardrail", "ON" if under_enabled else "OFF")
                guardrail_cols[1].metric(
                    "Underperf Window",
                    f"{int(meta.get('underperformance_guardrail_window_months') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M",
                )
                guardrail_cols[2].metric(
                    "Underperf Threshold",
                    f"{float(meta.get('underperformance_guardrail_threshold') or STRICT_UNDERPERFORMANCE_GUARDRAIL_DEFAULT_THRESHOLD):.0%}",
                )
                guardrail_cols[3].metric(
                    "Underperf Trigger Count",
                    str(int(meta.get("underperformance_guardrail_trigger_count") or 0)),
                )
                guardrail_cols[4].metric(
                    "Underperf Trigger Share",
                    f"{float(meta.get('underperformance_guardrail_trigger_share') or 0.0):.2%}",
                )

                drawdown_guardrail_cols = st.columns(5, gap="small")
                drawdown_guardrail_cols[0].metric("Drawdown Guardrail", "ON" if draw_enabled else "OFF")
                drawdown_guardrail_cols[1].metric(
                    "Drawdown Window",
                    f"{int(meta.get('drawdown_guardrail_window_months') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_WINDOW_MONTHS)}M",
                )
                drawdown_guardrail_cols[2].metric(
                    "Strategy DD Threshold",
                    f"{float(meta.get('drawdown_guardrail_strategy_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_STRATEGY_THRESHOLD):.0%}",
                )
                drawdown_guardrail_cols[3].metric(
                    "DD Gap Threshold",
                    f"{float(meta.get('drawdown_guardrail_gap_threshold') or STRICT_DRAWDOWN_GUARDRAIL_DEFAULT_GAP_THRESHOLD):.0%}",
                )
                drawdown_guardrail_cols[4].metric(
                    "Drawdown Trigger Count",
                    str(int(meta.get("drawdown_guardrail_trigger_count") or 0)),
                )
                st.caption(
                    "Drawdown trigger share: "
                    f"`{float(meta.get('drawdown_guardrail_trigger_share') or 0.0):.2%}`"
                )

                if not under_enabled and not draw_enabled:
                    st.info(
                        "현재 run에서는 두 guardrail이 꺼져 있습니다. "
                        "그래도 여기서 기본 계약과 trigger 수를 확인할 수 있게 계속 노출합니다."
                    )

    with detail_tab:
        st.caption(
            "이 섹션은 원자료 확인용입니다. "
            "요약 판단은 앞의 세 탭에서 끝내고, 여기서는 세부 숫자나 표를 다시 확인할 때만 보시면 됩니다."
        )

        detail_cols: list[str] = []
        if result_df is not None and "Estimated Cost" in result_df.columns:
            with _section_header(
                "Cost Detail Preview",
                "비용이 실제로 어떻게 누적됐는지 확인하는 원자료 미리보기입니다.",
            ):
                detail_cols.append("Date")
                detail_cols.extend(
                    [
                        column
                        for column in [
                            "Gross Total Balance",
                            "Total Balance",
                            "Turnover",
                            "Estimated Cost",
                            "Cumulative Estimated Cost",
                        ]
                        if column in result_df.columns
                    ]
                )
                st.dataframe(result_df[detail_cols].head(12), use_container_width=True, hide_index=True)

        if benchmark_summary_df is not None:
            with _section_header(
                "Benchmark Summary",
                "benchmark와의 비교 결과를 표 형태로 다시 확인하는 상세 데이터입니다.",
            ):
                st.dataframe(benchmark_summary_df, use_container_width=True, hide_index=True)

def _build_snapshot_selection_history(result_df: pd.DataFrame) -> pd.DataFrame:
    if result_df.empty or "Selected Count" not in result_df.columns:
        return pd.DataFrame()

    selection_df = result_df.copy()

    def _first_series(frame: pd.DataFrame, column: str) -> pd.Series | None:
        if column not in frame.columns:
            return None
        value = frame[column]
        if isinstance(value, pd.DataFrame):
            return value.iloc[:, 0]
        return value

    if selection_df.columns.duplicated().any():
        selection_df = selection_df.loc[:, ~selection_df.columns.duplicated()].copy()

    selection_df["Date"] = pd.to_datetime(selection_df["Date"], errors="coerce")
    selection_df = selection_df.dropna(subset=["Date"])

    if "Rebalancing" in selection_df.columns:
        selection_df = selection_df[selection_df["Rebalancing"].fillna(False)]

    selected_count_series = _first_series(selection_df, "Selected Count")
    raw_selected_count_series = _first_series(selection_df, "Raw Selected Count")
    cash_only_state_series = _first_series(selection_df, "Cash Only State")
    selected_count = selected_count_series.fillna(0) if selected_count_series is not None else 0
    raw_selected_count = raw_selected_count_series.fillna(0) if raw_selected_count_series is not None else 0
    cash_only_state = (
        cash_only_state_series.fillna(False).astype(bool)
        if cash_only_state_series is not None
        else False
    )
    selection_df = selection_df[(selected_count > 0) | (raw_selected_count > 0) | cash_only_state].copy()
    if selection_df.empty:
        return pd.DataFrame()

    selection_df["Rejected Slot Handling"] = selection_df.apply(
        lambda row: _strict_rejection_handling_label_from_flags(
            rejected_slot_fill_enabled=bool(row.get("Rejected Slot Fill Enabled") or False),
            partial_cash_retention_enabled=bool(row.get("Partial Cash Retention Enabled") or False),
        ),
        axis=1,
    )
    selection_df["Weighting Contract"] = selection_df["Weighting Mode"].apply(_strict_weighting_mode_value_to_label)
    selection_df["Risk-Off Contract"] = selection_df["Risk-Off Mode"].apply(_strict_risk_off_mode_value_to_label)
    selection_df["Risk-Off Reasons"] = selection_df["Risk-Off Reason"].apply(
        lambda value: _stringify_label_list(value, label_fn=_strict_risk_off_reason_to_label)
    )

    keep_columns = [
        "Date",
        "Raw Selected Ticker",
        "Raw Selected Count",
        "Raw Selected Score",
        "Eligible Ticker",
        "Eligible Count",
        "Volatility Window",
        "Eligible Volatility",
        "Inverse Vol Weight",
        "Volatility Rejected Ticker",
        "Volatility Rejected Count",
        "Overlay Rejected Ticker",
        "Overlay Rejected Count",
        "Rejected Slot Handling",
        "Rejected Slot Fill Enabled",
        "Rejected Slot Fill Active",
        "Rejected Slot Fill Ticker",
        "Rejected Slot Fill Count",
        "Partial Cash Retention Enabled",
        "Partial Cash Retention Active",
        "Risk-Off Contract",
        "Risk-Off Mode",
        "Risk-Off Reason",
        "Risk-Off Reasons",
        "Cash Only State",
        "Cash Only Reason",
        "Defensive Sleeve Ticker",
        "Defensive Sleeve Count",
        "Regime Blocked Ticker",
        "Regime Blocked Count",
        "Next Ticker",
        "Selected Count",
        "Selected Score",
        "Trend Filter Enabled",
        "Trend Filter Column",
        "Weighting Contract",
        "Weighting Mode",
        "Target Slot Count",
        "Unfilled Slot Count",
        "Max Position Weight",
        "Concentration Status",
        "Low Vol Overweight Ticker",
        "Low Vol Overweight Reason",
        "Cash Proxy Ticker",
        "Cash Proxy Return",
        "Cash Reason",
        "Selection Changed",
        "Added Ticker",
        "Removed Ticker",
        "Whipsaw Status",
        "Market Regime Enabled",
        "Market Regime Benchmark",
        "Market Regime Column",
        "Market Regime State",
        "Cash",
        "Total Balance",
        "Total Return",
    ]
    existing = [column for column in keep_columns if column in selection_df.columns]
    selection_df = selection_df[existing].copy()
    rename_map = {
        "Next Ticker": "Selected Tickers",
        "Selected Score": "Selection Score",
        "Raw Selected Ticker": "Raw Selected Tickers",
        "Raw Selected Score": "Raw Selection Score",
        "Eligible Ticker": "Eligible Tickers",
        "Volatility Rejected Ticker": "Volatility Rejected Tickers",
        "Overlay Rejected Ticker": "Overlay Rejected Tickers",
        "Rejected Slot Fill Ticker": "Filled Tickers",
        "Rejected Slot Fill Count": "Filled Count",
        "Defensive Sleeve Ticker": "Defensive Sleeve Tickers",
        "Regime Blocked Ticker": "Regime Blocked Tickers",
        "Cash Only Reason": "Cash Only Reasons",
        "Cash Reason": "Cash Reasons",
        "Added Ticker": "Added Tickers",
        "Removed Ticker": "Removed Tickers",
    }
    selection_df = selection_df.rename(columns=rename_map).reset_index(drop=True)

    list_columns = [
        "Raw Selected Tickers",
        "Eligible Tickers",
        "Volatility Rejected Tickers",
        "Overlay Rejected Tickers",
        "Filled Tickers",
        "Defensive Sleeve Tickers",
        "Regime Blocked Tickers",
        "Selected Tickers",
        "Cash Only Reasons",
        "Cash Reasons",
        "Added Tickers",
        "Removed Tickers",
    ]
    score_list_columns = [
        "Raw Selection Score",
        "Selection Score",
        "Eligible Volatility",
        "Inverse Vol Weight",
    ]
    for column in list_columns:
        if column in selection_df.columns:
            selection_df[column] = selection_df[column].apply(_stringify_symbol_list)
    for column in score_list_columns:
        if column in selection_df.columns:
            selection_df[column] = selection_df[column].apply(_stringify_score_list)

    cash_series = _first_series(selection_df, "Cash")
    total_balance_series = _first_series(selection_df, "Total Balance")
    if cash_series is not None and total_balance_series is not None:
        total_balance = pd.to_numeric(total_balance_series, errors="coerce")
        cash_balance = pd.to_numeric(cash_series, errors="coerce").fillna(0.0)
        selection_df["Cash Share Ratio"] = np.where(
            total_balance > 0,
            cash_balance / total_balance,
            np.nan,
        )
    else:
        selection_df["Cash Share Ratio"] = np.nan

    def _build_interpretation(row: pd.Series) -> str:
        raw_count = int(row.get("Raw Selected Count") or 0)
        rejected_count = int(row.get("Overlay Rejected Count") or 0)
        regime_blocked_count = int(row.get("Regime Blocked Count") or 0)
        selected_count = int(row.get("Selected Count") or 0)
        regime_state = str(row.get("Market Regime State") or "").strip().lower()
        regime_benchmark = str(row.get("Market Regime Benchmark") or "").strip() or "benchmark"
        risk_off_contract = str(row.get("Risk-Off Contract") or "Cash Only").strip()
        risk_off_reasons = str(row.get("Risk-Off Reasons") or "").strip()
        weighting_contract = str(row.get("Weighting Contract") or "Equal Weight").strip()
        defensive_sleeve_count = int(row.get("Defensive Sleeve Count") or 0)
        defensive_sleeve_tickers = str(row.get("Defensive Sleeve Tickers") or "").strip()
        cash_only_reasons = str(row.get("Cash Only Reasons") or "").strip()
        cash_share = row.get("Cash Share Ratio")
        cash_share_text = (
            f"{float(cash_share) * 100:.1f}%"
            if pd.notna(cash_share)
            else "n/a"
        )

        if raw_count <= 0:
            if cash_only_reasons:
                return (
                    f"선택 가능한 최종 보유 종목이 없어 이 리밸런싱은 현금 상태로 유지됐습니다. "
                    f"이유: `{cash_only_reasons}`. 현금 비중: {cash_share_text}."
                )
            return "선택 가능한 ranked candidate가 없어 이 리밸런싱은 현금 상태로 유지됐습니다."
        if regime_blocked_count > 0 and regime_state == "risk_off":
            if risk_off_contract == "Defensive Sleeve Preference" and defensive_sleeve_count > 0:
                return (
                    f"Market regime overlay moved the portfolio into defensive sleeve `{defensive_sleeve_tickers}` "
                    f"because `{regime_benchmark}` was in risk-off state at this rebalance. "
                    f"It blocked {regime_blocked_count} post-filter candidate(s)."
                )
            return (
                f"Market regime overlay moved the portfolio fully to cash because `{regime_benchmark}` "
                f"was in risk-off state at this rebalance. It blocked {regime_blocked_count} post-filter candidate(s)."
            )
        if selected_count <= 0 and risk_off_reasons:
            destination_text = (
                f"rotated into defensive sleeve `{defensive_sleeve_tickers}`"
                if risk_off_contract == "Defensive Sleeve Preference" and defensive_sleeve_count > 0
                else "moved fully to cash"
            )
            return (
                f"Portfolio-wide risk-off rule (`{risk_off_contract}`) {destination_text} because "
                f"`{risk_off_reasons}` triggered after candidate selection."
            )
        if selected_count <= 0 and cash_only_reasons:
            return (
                f"최종 선택 종목이 없어 포트폴리오가 현금 상태로 유지됐습니다. "
                f"이유: `{cash_only_reasons}`. 현금 비중: {cash_share_text}."
            )
        if selected_count <= 0 and rejected_count > 0:
            handling_label = str(row.get("Rejected Slot Handling") or "current rejection handling")
            return (
                f"Trend overlay rejected all {raw_count} raw candidates under `{handling_label}`, "
                "so the portfolio moved fully to cash."
            )
        if rejected_count > 0:
            handling_label = str(row.get("Rejected Slot Handling") or "current rejection handling")
            fill_count = int(row.get("Rejected Slot Fill Count") or 0)
            fill_active = bool(row.get("Rejected Slot Fill Active") or False)
            partial_cash_retention_active = bool(row.get("Partial Cash Retention Active") or False)
            if fill_active and fill_count > 0:
                unfilled_count = max(rejected_count - fill_count, 0)
                fill_text = (
                    f"`{handling_label}` refilled {fill_count} rejected slot(s) with next-ranked eligible names"
                    + (
                        f" and left {unfilled_count} slot(s) in cash. Cash share after rebalance: {cash_share_text}."
                        if partial_cash_retention_active and unfilled_count > 0
                        else f". Cash share after rebalance: {cash_share_text}."
                    )
                )
                if not partial_cash_retention_active and selected_count < raw_count:
                    fill_text = (
                        f"`{handling_label}` refilled {fill_count} rejected slot(s), then reweighted the final survivors after "
                        f"{rejected_count} original rejection(s). Cash share after rebalance: {cash_share_text}."
                    )
                return (
                    f"Trend overlay kept {selected_count} of {raw_count} raw candidates and {fill_text} "
                    f"Final weighting contract: `{weighting_contract}`."
                )
            return (
                f"Trend overlay kept {selected_count} of {raw_count} raw candidates and "
                + (
                    f"`{handling_label}` left {rejected_count} rejected slot(s) in cash. Cash share after rebalance: {cash_share_text}. Final weighting contract: `{weighting_contract}`."
                    if partial_cash_retention_active
                    else f"`{handling_label}` reweighted the survivors after rejecting {rejected_count} name(s). Cash share after rebalance: {cash_share_text}. Final weighting contract: `{weighting_contract}`."
                )
            )
        if pd.notna(cash_share) and float(cash_share) > 0:
            return (
                f"All final candidates passed the current filters, but the portfolio still kept "
                f"{cash_share_text} in cash because fewer names were investable than the nominal top-N. "
                f"Final weighting contract: `{weighting_contract}`."
            )
        return (
            "All selected candidates passed the current rules and the portfolio remained fully invested. "
            f"Final weighting contract: `{weighting_contract}`."
        )

    selection_df["Interpretation"] = selection_df.apply(_build_interpretation, axis=1)
    if "Cash Share Ratio" in selection_df.columns:
        selection_df["Cash Share"] = selection_df["Cash Share Ratio"].apply(
            lambda value: f"{float(value) * 100:.1f}%" if pd.notna(value) else ""
        )

    return selection_df

def _build_overlay_rejection_frequency_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Overlay Rejected Tickers" not in selection_df.columns:
        return pd.DataFrame()

    exploded_rows: list[dict[str, Any]] = []
    for _, row in selection_df.iterrows():
        row_date = pd.to_datetime(row.get("Date"), errors="coerce")
        rejected_tickers = _normalize_symbol_sequence(row.get("Overlay Rejected Tickers"))
        for symbol in rejected_tickers:
            exploded_rows.append({"symbol": symbol, "Date": row_date})

    if not exploded_rows:
        return pd.DataFrame()

    exploded_df = pd.DataFrame(exploded_rows)
    rejection_df = (
        exploded_df.groupby("symbol", as_index=False)
        .agg(
            RejectedEvents=("Date", "size"),
            FirstRejected=("Date", "min"),
            LastRejected=("Date", "max"),
        )
        .sort_values(["RejectedEvents", "symbol"], ascending=[False, True])
        .reset_index(drop=True)
    )
    rejection_df["FirstRejected"] = pd.to_datetime(rejection_df["FirstRejected"]).dt.strftime("%Y-%m-%d")
    rejection_df["LastRejected"] = pd.to_datetime(rejection_df["LastRejected"]).dt.strftime("%Y-%m-%d")
    return rejection_df

def _build_market_regime_event_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Market Regime State" not in selection_df.columns:
        return pd.DataFrame()

    regime_df = selection_df.copy()
    regime_df = regime_df[regime_df["Market Regime State"].astype(str).str.lower() == "risk_off"].copy()
    if regime_df.empty:
        return pd.DataFrame()

    keep = [
        "Date",
        "Market Regime Benchmark",
        "Market Regime Column",
        "Raw Selected Count",
        "Regime Blocked Count",
        "Regime Blocked Tickers",
        "Cash Share",
    ]
    keep = [column for column in keep if column in regime_df.columns]
    event_df = regime_df[keep].copy()
    event_df["Date"] = pd.to_datetime(event_df["Date"]).dt.strftime("%Y-%m-%d")
    return event_df.reset_index(drop=True)

def _build_selection_interpretation_summary(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty:
        return pd.DataFrame()

    def _series_or_default(column: str, *, default: Any, dtype: str | None = None) -> pd.Series:
        if column in selection_df.columns:
            value = selection_df[column]
            if isinstance(value, pd.DataFrame):
                value = value.iloc[:, 0]
            return value
        return pd.Series([default] * len(selection_df), index=selection_df.index, dtype=dtype)

    raw_candidate_events = int(pd.to_numeric(_series_or_default("Raw Selected Count", default=0), errors="coerce").fillna(0).sum())
    final_selected_events = int(pd.to_numeric(_series_or_default("Selected Count", default=0), errors="coerce").fillna(0).sum())
    overlay_rejections = int(pd.to_numeric(_series_or_default("Overlay Rejected Count", default=0), errors="coerce").fillna(0).sum())
    filled_events = int(
        (
            pd.to_numeric(_series_or_default("Filled Count", default=0), errors="coerce")
            .fillna(0)
            .gt(0)
        ).sum()
    )
    cash_retained_events = int(
        (
            _series_or_default("Partial Cash Retention Active", default=False, dtype=bool)
            .fillna(False)
            .astype(bool)
        ).sum()
    )
    regime_rejections = int(pd.to_numeric(_series_or_default("Regime Blocked Count", default=0), errors="coerce").fillna(0).sum())
    regime_cash_rebalances = int(
        (
            _series_or_default("Market Regime State", default="", dtype=object)
            .astype(str)
            .str.lower()
            .eq("risk_off")
        ).sum()
    )
    cash_only_rebalances = int(
        (pd.to_numeric(_series_or_default("Selected Count", default=0), errors="coerce").fillna(0) <= 0).sum()
    )
    avg_selected_count = float(
        pd.to_numeric(_series_or_default("Selected Count", default=0), errors="coerce").fillna(0).mean()
    )
    cash_share_series = pd.to_numeric(_series_or_default("Cash Share Ratio", default=np.nan), errors="coerce")
    avg_cash_share = float(cash_share_series.fillna(0).mean())
    weighting_values = [
        str(value).strip()
        for value in _series_or_default("Weighting Contract", default="", dtype=object).tolist()
        if str(value).strip()
    ]
    unique_weighting = sorted(dict.fromkeys(weighting_values))
    weighting_summary = ", ".join(unique_weighting) if unique_weighting else "n/a"
    risk_off_values = [
        str(value).strip()
        for value in _series_or_default("Risk-Off Contract", default="", dtype=object).tolist()
        if str(value).strip()
    ]
    unique_risk_off = sorted(dict.fromkeys(risk_off_values))
    risk_off_summary = ", ".join(unique_risk_off) if unique_risk_off else "n/a"
    defensive_sleeve_activations = int(
        (
            pd.to_numeric(_series_or_default("Defensive Sleeve Count", default=0), errors="coerce")
            .fillna(0)
            .gt(0)
        ).sum()
    )
    handling_values = [
        str(value).strip()
        for value in _series_or_default("Rejected Slot Handling", default="", dtype=object).tolist()
        if str(value).strip()
    ]
    unique_handling = sorted(dict.fromkeys(handling_values))
    handling_summary = ", ".join(unique_handling) if unique_handling else "n/a"

    return pd.DataFrame(
        [
            {
                "Raw Candidate Events": raw_candidate_events,
                "Final Selected Events": final_selected_events,
                "Overlay Rejections": overlay_rejections,
                "Rejected Slot Handling": handling_summary,
                "Weighting Contract": weighting_summary,
                "Risk-Off Contract": risk_off_summary,
                "Filled Events": filled_events,
                "Cash-Retained Events": cash_retained_events,
                "Defensive Sleeve Activations": defensive_sleeve_activations,
                "Regime Blocked Events": regime_rejections,
                "Regime Cash Rebalances": regime_cash_rebalances,
                "Cash-Only Rebalances": cash_only_rebalances,
                "Avg Selected Count": round(avg_selected_count, 2),
                "Avg Cash Share": f"{avg_cash_share * 100:.1f}%",
            }
        ]
    )

def _normalize_symbol_sequence(value: Any) -> list[str]:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return []
    if isinstance(value, (list, tuple, set)):
        return [str(symbol).strip() for symbol in value if str(symbol).strip()]

    raw = str(value).strip()
    if not raw:
        return []

    raw = raw.strip("[]")
    cleaned = [part.strip().strip("'").strip('"') for part in raw.split(",")]
    return [symbol for symbol in cleaned if symbol]

def _stringify_symbol_list(value: Any) -> str:
    symbols = _normalize_symbol_sequence(value)
    return ", ".join(symbols)

def _stringify_score_list(value: Any) -> str:
    if value is None or (isinstance(value, float) and pd.isna(value)):
        return ""
    if isinstance(value, (list, tuple, set)):
        return ", ".join(f"{float(item):.3f}" for item in value)
    return str(value)

def _build_selection_frequency_view(selection_df: pd.DataFrame) -> pd.DataFrame:
    if selection_df.empty or "Selected Tickers" not in selection_df.columns:
        return pd.DataFrame()

    exploded_rows: list[dict[str, Any]] = []
    for _, row in selection_df.iterrows():
        row_date = pd.to_datetime(row.get("Date"), errors="coerce")
        selected_tickers = _normalize_symbol_sequence(row.get("Selected Tickers"))
        for symbol in selected_tickers:
            exploded_rows.append({"symbol": symbol, "Date": row_date})

    if not exploded_rows:
        return pd.DataFrame()

    exploded_df = pd.DataFrame(exploded_rows)
    frequency_df = (
        exploded_df.groupby("symbol", as_index=False)
        .agg(
            SelectedEvents=("Date", "size"),
            FirstSelected=("Date", "min"),
            LastSelected=("Date", "max"),
        )
        .sort_values(["SelectedEvents", "symbol"], ascending=[False, True])
        .reset_index(drop=True)
    )
    frequency_df["FirstSelected"] = pd.to_datetime(frequency_df["FirstSelected"]).dt.strftime("%Y-%m-%d")
    frequency_df["LastSelected"] = pd.to_datetime(frequency_df["LastSelected"]).dt.strftime("%Y-%m-%d")
    return frequency_df

def _render_snapshot_selection_history(
    result_df: pd.DataFrame,
    *,
    strategy_name: str,
    factor_names: list[str],
    snapshot_mode: str | None,
    snapshot_source: str | None,
) -> None:
    try:
        selection_df = _build_snapshot_selection_history(result_df)
    except Exception as exc:  # pragma: no cover - UI fallback path
        st.warning(
            "Selection history could not be rendered for this run payload. "
            "Try rerunning the backtest to rebuild the latest result bundle."
        )
        st.caption(f"Renderer detail: {type(exc).__name__}: {exc}")
        return

    if selection_df.empty:
        st.info("No active selection history is available for this run.")
        return

    first_active = pd.to_datetime(selection_df.iloc[0]["Date"]).strftime("%Y-%m-%d")
    event_count = len(selection_df)
    distinct_names = sorted(
        {
            symbol.strip()
            for value in selection_df["Selected Tickers"].dropna()
            for symbol in _normalize_symbol_sequence(value)
            if symbol.strip()
        }
    )
    overlay_active = (
        "Trend Filter Enabled" in selection_df.columns
        and selection_df["Trend Filter Enabled"].fillna(False).astype(bool).any()
    )
    regime_active = (
        "Market Regime Enabled" in selection_df.columns
        and selection_df["Market Regime Enabled"].fillna(False).astype(bool).any()
    )

    st.caption(
        "이 화면은 리밸런싱 전략 검토에서 가장 실무적인 질문인 "
        "‘각 리밸런싱 날짜에 실제로 어떤 종목이 선택되었는가?’를 읽기 쉽게 보여주기 위한 뷰입니다."
    )
    left, center, right = st.columns(3, gap="large")
    with left:
        st.metric("First Active Date", first_active)
    with center:
        st.metric("Active Rebalances", f"{event_count}")
    with right:
        st.metric("Distinct Selected Names", f"{len(distinct_names)}")

    meta_df = pd.DataFrame(
        [
            {
                "Strategy": strategy_name,
                "Snapshot Mode": snapshot_mode,
                "Snapshot Source": snapshot_source or "n/a",
                "Factors": ", ".join(factor_names) if factor_names else "n/a",
                "Trend Overlay": (
                    selection_df.loc[selection_df["Trend Filter Enabled"].fillna(False), "Trend Filter Column"].iloc[0]
                    if overlay_active and "Trend Filter Column" in selection_df.columns
                    else "off"
                ),
                "Rejected Slot Handling": (
                    ", ".join(
                        sorted(
                            dict.fromkeys(
                                str(value).strip()
                                for value in selection_df.get("Rejected Slot Handling", pd.Series(dtype=object)).tolist()
                                if str(value).strip()
                            )
                        )
                    )
                    or "n/a"
                ),
                "Weighting Contract": (
                    ", ".join(
                        sorted(
                            dict.fromkeys(
                                str(value).strip()
                                for value in selection_df.get("Weighting Contract", pd.Series(dtype=object)).tolist()
                                if str(value).strip()
                            )
                        )
                    )
                    or "n/a"
                ),
                "Risk-Off Contract": (
                    ", ".join(
                        sorted(
                            dict.fromkeys(
                                str(value).strip()
                                for value in selection_df.get("Risk-Off Contract", pd.Series(dtype=object)).tolist()
                                if str(value).strip()
                            )
                        )
                    )
                    or "n/a"
                ),
                "Market Regime Overlay": (
                    (
                        f"{selection_df.loc[selection_df['Market Regime Enabled'].fillna(False), 'Market Regime Benchmark'].iloc[0]} / "
                        f"{selection_df.loc[selection_df['Market Regime Enabled'].fillna(False), 'Market Regime Column'].iloc[0]}"
                    )
                    if regime_active
                    else "off"
                ),
            }
        ]
    )
    st.dataframe(meta_df, use_container_width=True, hide_index=True)
    if overlay_active:
        st.caption(
            "Raw Selected는 전략 점수로 뽑힌 1차 후보이고, Final Selected는 오버레이까지 반영한 실제 보유 후보입니다. Overlay Rejected는 월말 추세 필터를 통과하지 못한 원래 후보이고, Filled Tickers가 있으면 그 자리를 다음 순위의 추세 통과 종목으로 보충했다는 뜻입니다."
        )
    if regime_active:
        st.caption(
            "Market Regime은 개별 종목 필터가 아니라 시장 전체 상태를 보는 상위 오버레이입니다. risk-off로 판정된 리밸런싱에서는 strict factor 후보가 있어도 포트폴리오 전체가 현금으로 이동할 수 있습니다."
        )

    history_tab, interpretation_tab, frequency_tab = st.tabs(["Selection History Table", "Interpretation Summary", "Selection Frequency"])
    with history_tab:
        st.caption(
            "이 표는 각 리밸런싱 날짜별 실제 선택 결과입니다. "
            "`Rejected Slot Handling`, `Weighting Contract`, `Risk-Off Contract`와 함께 "
            "`Interpretation` 열을 보면 그 날짜에 무슨 일이 있었는지 한 줄로 읽을 수 있습니다."
        )
        cash_title_col, cash_help_col = st.columns([0.92, 0.08], gap="small")
        with cash_title_col:
            st.caption("`Cash Share`는 각 리밸런싱 직후 포트폴리오에서 현금으로 남아 있는 비중입니다.")
        with cash_help_col:
            _render_cash_share_help_popover()
        st.dataframe(
            selection_df.drop(
                columns=[
                    "Cash Share Ratio",
                    "Rejected Slot Fill Enabled",
                    "Rejected Slot Fill Active",
                    "Partial Cash Retention Enabled",
                    "Partial Cash Retention Active",
                    "Weighting Mode",
                    "Risk-Off Mode",
                    "Risk-Off Reason",
                ],
                errors="ignore",
            ),
            use_container_width=True,
            hide_index=True,
        )
    with interpretation_tab:
        interpretation_summary_df = _build_selection_interpretation_summary(selection_df)
        if not interpretation_summary_df.empty:
            summary_title_col, summary_help_col = st.columns([0.92, 0.08], gap="small")
            with summary_title_col:
                st.markdown("##### Interpretation Summary")
            with summary_help_col:
                _render_interpretation_summary_help_popover()
            st.caption(
                "이 표는 행별 문장이 아니라 실행 전체 요약입니다. "
                "`Rejected Slot Handling`, `Weighting Contract`, `Risk-Off Contract`, "
                "`Filled Events`, `Cash-Retained Events`, `Defensive Sleeve Activations`를 먼저 보면 됩니다."
            )
            st.caption("참고: 이 표의 Raw / Final 값은 전체 모집군 크기가 아니라 리밸런싱별 선택 이벤트의 누적 합계입니다.")
            st.dataframe(interpretation_summary_df, use_container_width=True, hide_index=True)
        rejection_df = _build_overlay_rejection_frequency_view(selection_df)
        if not rejection_df.empty:
            reject_title_col, reject_help_col = st.columns([0.92, 0.08], gap="small")
            with reject_title_col:
                st.markdown("##### Overlay Rejection Frequency")
            with reject_help_col:
                _render_overlay_rejection_frequency_help_popover()
            st.dataframe(rejection_df, use_container_width=True, hide_index=True)
        else:
            st.caption("이번 실행에서는 오버레이로 제외된 종목이 기록되지 않았습니다.")
        regime_event_df = _build_market_regime_event_view(selection_df)
        if not regime_event_df.empty:
            regime_title_col, regime_help_col = st.columns([0.92, 0.08], gap="small")
            with regime_title_col:
                st.markdown("##### Market Regime Events")
            with regime_help_col:
                _render_market_regime_events_help_popover()
            st.dataframe(regime_event_df, use_container_width=True, hide_index=True)
    with frequency_tab:
        frequency_df = _build_selection_frequency_view(selection_df)
        if frequency_df.empty:
            st.info("이번 실행에서는 선택 빈도 요약을 만들 수 있는 데이터가 없습니다.")
        else:
            st.caption("이 표는 전략이 여러 리밸런싱에 걸쳐 반복적으로 선택하는 종목이 무엇인지 보기 위한 요약입니다.")
            st.dataframe(frequency_df, use_container_width=True, hide_index=True)

__all__ = [name for name in globals() if not name.startswith("__")]
