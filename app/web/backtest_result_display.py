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
from app.services.backtest_handoff_readiness import (
    build_handoff_gate_summary,
    build_next_step_readiness_evaluation,
    build_policy_signal_inventory,
)
from app.services.backtest_price_refresh import (
    build_backtest_price_refresh_plan,
    run_backtest_price_refresh,
)
from app.web.backtest_common import *  # noqa: F401,F403
from app.web.backtest_ui_components import (
    render_badge_strip,
    render_status_card_grid,
)
from app.web.components.backtest_handoff_action import (
    is_backtest_handoff_action_available,
    render_backtest_handoff_action,
)
from app.web.components.backtest_policy_signal_board import (
    is_backtest_policy_signal_board_available,
    render_backtest_policy_signal_board,
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


def _display_data_trust_value(value: Any) -> str:
    if value is None:
        return "-"
    text = str(value).strip()
    return text or "-"


def _format_data_trust_count(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{int(value):,}"
    except (TypeError, ValueError):
        return _display_data_trust_value(value)


def _format_latest_date_spread(value: Any) -> str:
    if value is None:
        return "-"
    try:
        return f"{int(value)}d"
    except (TypeError, ValueError):
        return f"{value}d"


def _data_trust_price_status_label(status: str) -> str:
    mapping = {
        "ok": "최신성 정상",
        "warning": "최신성 확인",
        "error": "가격 보강 필요",
    }
    return mapping.get(status, "기준 제한")


def _build_data_trust_issue_cards(
    *,
    excluded_tickers: list[Any],
    malformed_price_rows: list[Any],
) -> list[dict[str, str]]:
    issue_cards: list[dict[str, str]] = []

    if excluded_tickers:
        sample = ", ".join(str(ticker) for ticker in excluded_tickers[:8])
        suffix = "..." if len(excluded_tickers) > 8 else ""
        issue_cards.append(
            {
                "priority": f"확인 {len(issue_cards) + 1}",
                "title": "제외 종목",
                "detail": f"{len(excluded_tickers)}개 ticker가 이번 계산에서 빠졌습니다: {sample}{suffix}",
                "tone": "warning",
            }
        )

    if malformed_price_rows:
        sample_symbols = [
            str(row.get("ticker") or row.get("symbol") or "").strip()
            for row in malformed_price_rows
            if isinstance(row, dict)
        ]
        sample = ", ".join(symbol for symbol in sample_symbols[:6] if symbol)
        detail = f"가격 결측 row {len(malformed_price_rows)}개가 있어 공통 계산 가능 기간을 줄일 수 있습니다."
        if sample:
            detail = f"{detail} 먼저 볼 ticker: {sample}"
        issue_cards.append(
            {
                "priority": f"확인 {len(issue_cards) + 1}",
                "title": "결측 가격 row",
                "detail": detail,
                "tone": "warning",
            }
        )

    return issue_cards


def _build_data_trust_brief(meta: dict[str, Any]) -> dict[str, Any]:
    price_freshness = meta.get("price_freshness") or {}
    freshness_details = price_freshness.get("details") or {}
    status = str(price_freshness.get("status") or "").strip().lower()
    excluded_tickers = list(meta.get("excluded_tickers") or [])
    malformed_price_rows = list(meta.get("malformed_price_rows") or [])
    tickers = list(meta.get("tickers") or [])
    requested_end = _display_data_trust_value(meta.get("end"))
    actual_end = _display_data_trust_value(
        meta.get("actual_result_end")
        or freshness_details.get("effective_end_date")
        or freshness_details.get("common_latest_date")
        or meta.get("end")
    )
    common_latest = _display_data_trust_value(freshness_details.get("common_latest_date") or actual_end)
    newest_latest = _display_data_trust_value(freshness_details.get("newest_latest_date") or common_latest)
    spread_label = _format_latest_date_spread(freshness_details.get("spread_days"))
    result_rows = _format_data_trust_count(meta.get("result_rows"))
    symbol_count = len(tickers)
    symbol_label = f"{symbol_count}개 종목" if symbol_count else "종목 수 미상"
    issue_cards = _build_data_trust_issue_cards(
        excluded_tickers=excluded_tickers,
        malformed_price_rows=malformed_price_rows,
    )

    if status == "error":
        status_label = "자료 보강 필요"
        tone = "danger"
        headline = f"가격 데이터 보강 전까지 {actual_end} 기준 결과는 검토용으로만 봅니다."
        price_tone = "danger"
    elif excluded_tickers or malformed_price_rows or status == "warning":
        status_label = "확인 필요"
        tone = "warning"
        headline = f"백테스트는 {actual_end}까지 계산됐고, 데이터 기준을 함께 확인해야 합니다."
        price_tone = "warning"
    elif status == "ok":
        status_label = "자료 정상"
        tone = "positive"
        headline = f"백테스트는 {actual_end}까지 저장된 가격으로 정상 계산됐습니다."
        price_tone = "positive"
    else:
        status_label = "자료 제한"
        tone = "neutral"
        headline = f"백테스트는 {actual_end} 기준으로 계산됐지만 데이터 기준 정보가 제한적입니다."
        price_tone = "neutral"

    if requested_end != "-" and actual_end != "-" and requested_end != actual_end:
        subtitle = (
            f"요청 종료일 {requested_end}보다 실제 계산 기준일은 {actual_end}입니다. "
            "저장 DB에서 모든 구성 종목이 함께 갖춘 최신 가격일을 기준으로 읽습니다."
        )
    elif requested_end != "-":
        subtitle = f"요청 종료일 {requested_end}까지 저장된 가격 기준으로 읽습니다."
    else:
        subtitle = "저장 DB의 공통 최신 가격일을 기준으로 결과를 읽습니다."

    if excluded_tickers or malformed_price_rows:
        next_check_label = "1차 데이터 확인"
        next_check_value = "데이터 이슈 확인"
        next_check_detail = "제외 종목과 결측 row를 확인합니다."
    elif status == "error":
        next_check_label = "1차 데이터 확인"
        next_check_value = "데이터 보강"
        next_check_detail = "가격 수집 또는 DB 보강 후 다시 실행합니다."
    else:
        next_check_label = "1차 데이터 확인"
        next_check_value = "바로 성과 확인"
        next_check_detail = "아래 성과 metric과 차트를 이어서 봅니다."

    summary_items = [
        {"label": "계산 기준일", "value": actual_end, "detail": f"요청 {requested_end}", "tone": "neutral"},
        {
            "label": "가격 기준",
            "value": _data_trust_price_status_label(status),
            "detail": f"공통 {common_latest} · 최신 {newest_latest} · 차이 {spread_label}",
            "tone": price_tone,
        },
        {
            "label": "사용 데이터",
            "value": symbol_label,
            "detail": f"성과 row {result_rows} · 제외 {len(excluded_tickers)}개 · 결측 row {len(malformed_price_rows)}개",
            "tone": "positive" if not excluded_tickers and not malformed_price_rows else "warning",
        },
        {"label": next_check_label, "value": next_check_value, "detail": next_check_detail, "tone": tone},
    ]

    return {
        "tone": tone,
        "status_label": status_label,
        "headline": headline,
        "subtitle": subtitle,
        "summary_items": summary_items,
        "issue_cards": issue_cards,
        "price_message": price_freshness.get("message"),
        "excluded_tickers": excluded_tickers,
        "malformed_price_rows": malformed_price_rows,
        "warnings": [],
        "second_stage_review_count": 0,
        "newest_latest": newest_latest,
    }


def _render_data_trust_issue_queue(brief: dict[str, Any]) -> str:
    issue_cards = list(brief.get("issue_cards") or [])
    if not issue_cards:
        return """
  <div class="data-trust-brief__issues data-trust-brief__issues--empty">
    <div class="data-trust-brief__issues-head">
      <span>1차 데이터 확인</span>
      <strong>추가 확인 없음</strong>
    </div>
    <p>현재 데이터 기준에서는 성과를 보기 전에 따로 볼 경고가 없습니다.</p>
  </div>
        """

    issue_html = "".join(
        (
            f'<div class="data-trust-brief__issue data-trust-brief__issue--{escape(str(card.get("tone") or "warning"))}">'
            f'<span class="data-trust-brief__issue-priority">{escape(str(card.get("priority") or "-"))}</span>'
            '<div>'
            f'<strong>{escape(str(card.get("title") or "-"))}</strong>'
            f'<p>{escape(str(card.get("detail") or "-"))}</p>'
            "</div>"
            "</div>"
        )
        for card in issue_cards
    )
    return f"""
  <div class="data-trust-brief__issues">
    <div class="data-trust-brief__issues-head">
      <span>1차 데이터 확인</span>
      <strong>{len(issue_cards)}개 확인</strong>
    </div>
    <div class="data-trust-brief__issue-list">{issue_html}</div>
  </div>
    """


def _render_data_trust_brief_panel(brief: dict[str, Any]) -> None:
    tone = str(brief.get("tone") or "neutral")
    status_label = escape(str(brief.get("status_label") or "-"))
    headline = escape(str(brief.get("headline") or "-"))
    subtitle = escape(str(brief.get("subtitle") or "-"))
    summary_html = "".join(
        (
            f'<div class="data-trust-brief__summary-item data-trust-brief__summary-item--{escape(str(item.get("tone") or "neutral"))}">'
            f'<span>{escape(str(item.get("label") or "-"))}</span>'
            f'<strong>{escape(str(item.get("value") or "-"))}</strong>'
            f'<small>{escape(str(item.get("detail") or "-"))}</small>'
            "</div>"
        )
        for item in list(brief.get("summary_items") or [])
    )
    issue_queue_html = _render_data_trust_issue_queue(brief)
    st.markdown(
        f"""
<style>
.data-trust-brief {{
  --dt-accent: #0f8f83;
  --dt-soft: rgba(15, 143, 131, 0.10);
  border-left: 4px solid var(--dt-accent);
  border-top: 1px solid rgba(148, 163, 184, 0.24);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  padding: 1.1rem 1.2rem 1rem;
  margin: 0.75rem 0 1rem;
  background: linear-gradient(90deg, var(--dt-soft), rgba(255, 255, 255, 0));
}}
.data-trust-brief--warning {{
  --dt-accent: #b45309;
  --dt-soft: rgba(180, 83, 9, 0.10);
}}
.data-trust-brief--danger {{
  --dt-accent: #b42318;
  --dt-soft: rgba(180, 35, 24, 0.10);
}}
.data-trust-brief--neutral {{
  --dt-accent: #667085;
  --dt-soft: rgba(102, 112, 133, 0.10);
}}
.data-trust-brief__top {{
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}}
.data-trust-brief__section-title {{
  color: var(--dt-accent);
  font-size: 0.88rem;
  font-weight: 800;
  margin-bottom: 0.7rem;
}}
.data-trust-brief__section-kicker {{
  color: #667085;
  font-size: 0.92rem;
  font-weight: 800;
  margin-bottom: 0.2rem;
}}
.data-trust-brief h4 {{
  margin: 0;
  color: var(--text-color);
  font-size: 1.35rem;
  line-height: 1.35;
  letter-spacing: 0;
}}
.data-trust-brief__top p {{
  margin: 0.55rem 0 0;
  color: #667085;
  font-size: 1rem;
  line-height: 1.55;
}}
.data-trust-brief__pill {{
  flex: 0 0 auto;
  border: 1px solid rgba(15, 143, 131, 0.38);
  color: var(--dt-accent);
  background: rgba(255, 255, 255, 0.72);
  border-radius: 999px;
  padding: 0.34rem 0.72rem;
  font-size: 0.86rem;
  font-weight: 800;
}}
.data-trust-brief__summary {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.24);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
}}
.data-trust-brief__summary-item {{
  padding: 0.85rem 0.95rem;
  border-right: 1px solid rgba(148, 163, 184, 0.22);
  min-width: 0;
}}
.data-trust-brief__summary-item:last-child {{
  border-right: 0;
}}
.data-trust-brief__summary-item span {{
  display: block;
  color: var(--dt-accent);
  font-size: 0.86rem;
  font-weight: 800;
}}
.data-trust-brief__summary-item strong {{
  display: block;
  margin-top: 0.18rem;
  color: var(--text-color);
  font-size: 1.05rem;
  line-height: 1.3;
}}
.data-trust-brief__summary-item small {{
  display: block;
  margin-top: 0.22rem;
  color: #667085;
  font-size: 0.82rem;
  line-height: 1.35;
}}
.data-trust-brief__issues {{
  margin-top: 1rem;
  padding-top: 0.85rem;
  border-top: 1px solid rgba(148, 163, 184, 0.24);
}}
.data-trust-brief__issues-head {{
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: center;
  margin-bottom: 0.25rem;
}}
.data-trust-brief__issues-head span {{
  color: #667085;
  font-size: 0.88rem;
  font-weight: 800;
}}
.data-trust-brief__issues-head strong {{
  color: var(--dt-accent);
  font-size: 0.9rem;
}}
.data-trust-brief__issue-list {{
  margin-top: 0.45rem;
}}
.data-trust-brief__issue {{
  display: grid;
  grid-template-columns: 4.6rem minmax(0, 1fr);
  gap: 0.85rem;
  align-items: start;
  padding: 0.7rem 0;
  border-bottom: 1px solid rgba(148, 163, 184, 0.22);
}}
.data-trust-brief__issue:last-child {{
  border-bottom: 0;
}}
.data-trust-brief__issue-priority {{
  justify-self: start;
  min-width: 3.8rem;
  border-radius: 999px;
  color: var(--dt-accent);
  background: var(--dt-soft);
  padding: 0.18rem 0.5rem;
  font-size: 0.8rem;
  font-weight: 800;
}}
.data-trust-brief__issue strong {{
  display: block;
  color: var(--text-color);
  font-size: 1.02rem;
  line-height: 1.3;
}}
.data-trust-brief__issue p,
.data-trust-brief__issues--empty p {{
  margin: 0.14rem 0 0;
  color: #667085;
  line-height: 1.45;
}}
@media (max-width: 900px) {{
  .data-trust-brief__top {{
    display: block;
  }}
  .data-trust-brief__pill {{
    display: inline-block;
    margin-top: 0.75rem;
  }}
  .data-trust-brief__summary {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
  .data-trust-brief__summary-item:nth-child(2) {{
    border-right: 0;
  }}
  .data-trust-brief__issue {{
    grid-template-columns: 1fr;
    gap: 0.35rem;
  }}
}}
</style>
<section class="data-trust-brief data-trust-brief--{escape(tone)}">
  <div class="data-trust-brief__section-title">데이터 기준 요약</div>
  <div class="data-trust-brief__top">
    <div>
      <div class="data-trust-brief__section-kicker">먼저 볼 결론</div>
      <h4>{headline}</h4>
      <p>{subtitle}</p>
    </div>
    <div class="data-trust-brief__pill">{status_label}</div>
  </div>
  <div class="data-trust-brief__summary">{summary_html}</div>
{issue_queue_html}
</section>
        """,
        unsafe_allow_html=True,
    )


def _data_trust_refresh_state_key(plan: dict[str, Any]) -> str:
    tickers_key = "_".join(str(symbol) for symbol in list(plan.get("tickers") or [])[:12])
    safe_tickers = "".join(ch if ch.isalnum() else "_" for ch in tickers_key)[:96]
    current = str(plan.get("current_common_latest") or "none").replace("-", "")
    target = str(plan.get("target_end") or "none").replace("-", "")
    return f"backtest_data_trust_price_refresh_result_{safe_tickers}_{current}_{target}"


def _render_data_trust_refresh_job_result(result: dict[str, Any]) -> None:
    status = str(result.get("status") or "").strip().lower()
    rows_written = result.get("rows_written")
    message = str(result.get("message") or "가격 데이터 업데이트 실행 결과가 없습니다.")
    if status == "success":
        st.success(f"{message} 저장 rows: {rows_written or 0:,}")
    elif status == "partial_success":
        failed = ", ".join(str(symbol) for symbol in list(result.get("failed_symbols") or [])[:8])
        suffix = f" 확인 필요: {failed}" if failed else ""
        st.warning(f"{message} 저장 rows: {rows_written or 0:,}.{suffix}")
    elif status == "skipped":
        st.info(message)
    else:
        st.error(message)
    st.caption("업데이트 후 최신 가격 기준 성과를 보려면 `Run Backtest`를 다시 실행하세요.")


def _render_data_trust_refresh_action(meta: dict[str, Any]) -> None:
    plan = build_backtest_price_refresh_plan(meta)
    if not plan.get("eligible"):
        return

    state_key = _data_trust_refresh_state_key(plan)
    target_end = escape(str(plan.get("target_end") or "-"))
    current_latest = escape(str(plan.get("current_common_latest") or "-"))
    collection_start = escape(str(plan.get("collection_start") or "-"))
    ticker_count = int(plan.get("ticker_count") or 0)
    summary = escape(str(plan.get("summary") or "가격 데이터 업데이트가 가능합니다."))
    detail = escape(str(plan.get("detail") or ""))

    st.markdown(
        f"""
<style>
.data-trust-refresh-action {{
  border-left: 4px solid #b45309;
  border-top: 1px solid rgba(148, 163, 184, 0.24);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  background: linear-gradient(90deg, rgba(180, 83, 9, 0.10), rgba(255, 255, 255, 0));
  margin: -0.35rem 0 0.9rem;
  padding: 0.88rem 1.2rem;
}}
.data-trust-refresh-action__kicker {{
  color: #b45309;
  font-size: 0.84rem;
  font-weight: 850;
  margin-bottom: 0.24rem;
}}
.data-trust-refresh-action__title {{
  color: var(--text-color);
  font-size: 1.02rem;
  font-weight: 850;
  line-height: 1.35;
}}
.data-trust-refresh-action__meta {{
  color: #667085;
  font-size: 0.86rem;
  line-height: 1.45;
  margin-top: 0.34rem;
}}
</style>
<section class="data-trust-refresh-action">
  <div class="data-trust-refresh-action__kicker">가격 데이터 업데이트 가능</div>
  <div class="data-trust-refresh-action__title">{summary}</div>
  <div class="data-trust-refresh-action__meta">
    현재 공통 기준일 {current_latest} · 목표 기준일 {target_end} · 수집 시작 {collection_start} · 대상 {ticker_count:,}개 종목<br/>
    {detail}
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )
    action_cols = st.columns([0.26, 0.74], gap="small", vertical_alignment="center")
    if action_cols[0].button(
        str(plan.get("button_label") or "가격 데이터 업데이트"),
        key=f"{state_key}_button",
        type="primary",
        use_container_width=True,
        help="기존 OHLCV 수집 pipeline으로 현재 백테스트 ticker의 daily 가격 이력을 보강합니다.",
    ):
        with st.spinner("현재 백테스트 ticker의 OHLCV 가격 데이터를 업데이트하는 중입니다...", show_time=True):
            st.session_state[state_key] = run_backtest_price_refresh(meta)
        st.rerun()
    action_cols[1].caption(
        "이 버튼은 가격 DB만 보강합니다. 백테스트 성과, 후보 등록, 2차 검증 전송은 자동으로 다시 실행하지 않습니다."
    )
    result = st.session_state.get(state_key)
    if isinstance(result, dict):
        _render_data_trust_refresh_job_result(result)


def _render_data_trust_summary(meta: dict[str, Any]) -> None:
    brief = _build_data_trust_brief(meta)

    _render_data_trust_brief_panel(brief)
    _render_data_trust_refresh_action(meta)


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


def _build_practical_validation_handoff_state(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = bundle.get("meta") or {}
    evaluation = build_next_step_readiness_evaluation(meta)
    gate_summary = build_handoff_gate_summary(meta)
    can_submit = bool(evaluation.get("can_enter_practical_validation"))
    blocking_reasons = [str(reason) for reason in list(evaluation.get("blocking_reasons") or [])]
    review_reasons = [str(reason) for reason in list(evaluation.get("review_reasons") or [])]
    inventory = dict(evaluation.get("policy_signal_inventory") or {})
    inventory_counts = dict(inventory.get("counts") or {})
    first_stage_blocker_count = int(inventory_counts.get("first_stage_block") or 0)
    second_stage_review_count = int(inventory_counts.get("second_stage_review") or len(review_reasons))
    if not can_submit:
        first_stage_blocker_count = max(
            first_stage_blocker_count,
            len(list(evaluation.get("entry_blocking_reasons") or [])),
        )

    if can_submit:
        status_label = "1차 통과"
        tone = "positive"
        summary = "1차 source 등록 기준은 통과했습니다. 다음 단계에서 실전성 검증을 진행합니다."
        action_text = "Practical Validation에서 실전성, 유동성, 검증 근거를 확인합니다."
        button_label = "2차 검증으로 보내기"
    else:
        status_label = "1차 진입 보류"
        tone = "danger"
        summary = "1차 source 등록 기준에 blocker가 있습니다."
        action_text = "먼저 해결 항목을 정리한 뒤 다시 실행하세요."
        button_label = "진입 기준 확인 필요"

    if not can_submit:
        display_reasons = [str(item) for item in list(gate_summary.get("action_items") or [])][:3]
        reason_title = str(gate_summary.get("reason_title") or ("막는 이유" if blocking_reasons else "상태"))
    else:
        display_reasons = ["Practical Validation에서 실전성 검증을 이어갑니다."]
        reason_title = "다음 단계"
    entry_cards = [
        {
            "label": "1차 진입 기준",
            "value": "통과" if can_submit else "보류",
            "detail": "source 등록 가능" if can_submit else "source 등록 차단",
            "tone": "positive" if can_submit else "danger",
        },
        {
            "label": "먼저 해결",
            "value": f"{first_stage_blocker_count}개",
            "detail": "1차 blocker",
            "tone": "danger" if first_stage_blocker_count else "positive",
        },
        {
            "label": "다음 단계",
            "value": "Practical Validation",
            "detail": "실전성 검증",
            "tone": "neutral",
        },
    ]

    return {
        "can_submit": can_submit,
        "status_label": status_label,
        "tone": tone,
        "summary": summary,
        "action_text": action_text,
        "button_label": button_label,
        "reason_title": reason_title,
        "display_reasons": display_reasons,
        "entry_cards": entry_cards,
        "evaluation": evaluation,
        "first_stage_blocker_count": first_stage_blocker_count,
        "second_stage_review_count": second_stage_review_count,
    }


def _render_practical_validation_handoff_panel(state: dict[str, Any]) -> None:
    tone = str(state.get("tone") or "neutral")
    status = escape(str(state.get("status_label") or "-"))
    summary = escape(str(state.get("summary") or "-"))
    action_text = escape(str(state.get("action_text") or "-"))
    reason_title = escape(str(state.get("reason_title") or "상태"))
    reasons = list(state.get("display_reasons") or [])
    entry_cards = list(state.get("entry_cards") or [])
    action_label = "등록 가능" if bool(state.get("can_submit")) else "기준 확인 필요"
    action_detail = (
        "아래 버튼을 누르면 이 결과를 Practical Validation이 읽는 current selection source로 등록합니다."
        if bool(state.get("can_submit"))
        else "막는 항목이 남아 있으면 source 등록 버튼은 비활성화됩니다."
    )
    reason_items = "".join(f"<li>{escape(str(reason))}</li>" for reason in reasons)
    entry_items = "".join(
        '<div class="bt-handoff-chip bt-handoff-chip-{tone}">'
        '<span class="bt-handoff-chip-label">{label}</span>'
        '<span class="bt-handoff-chip-value">{value}</span>'
        '<small class="bt-handoff-chip-detail">{detail}</small>'
        "</div>".format(
            tone=escape(str(item.get("tone") or "neutral")),
            label=escape(str(item.get("label") or "-")),
            value=escape(str(item.get("value") or "-")),
            detail=escape(str(item.get("detail") or "")),
        )
        for item in entry_cards
    )
    st.markdown(
        """
        <style>
          .bt-handoff-panel {
            --bt-handoff-accent: #64748b;
            --bt-handoff-soft: rgba(100, 116, 139, 0.10);
            border-left: 4px solid var(--bt-handoff-accent);
            border-top: 1px solid rgba(148, 163, 184, 0.24);
            border-bottom: 1px solid rgba(148, 163, 184, 0.24);
            border-radius: 8px;
            padding: 1.1rem 1.2rem;
            margin: 1rem 0 0.6rem 0;
            background: linear-gradient(90deg, var(--bt-handoff-soft), rgba(255, 255, 255, 0));
          }
          .bt-handoff-panel--positive {
            --bt-handoff-accent: #0f8f83;
            --bt-handoff-soft: rgba(15, 143, 131, 0.10);
          }
          .bt-handoff-panel--warning {
            --bt-handoff-accent: #b45309;
            --bt-handoff-soft: rgba(180, 83, 9, 0.10);
          }
          .bt-handoff-panel--danger {
            --bt-handoff-accent: #b42318;
            --bt-handoff-soft: rgba(180, 35, 24, 0.10);
          }
          .bt-handoff-head {
            display: flex;
            flex-wrap: wrap;
            align-items: flex-start;
            justify-content: space-between;
            gap: 0.85rem;
            margin-bottom: 0.9rem;
          }
          .bt-handoff-kicker {
            color: var(--bt-handoff-accent);
            font-size: 0.88rem;
            font-weight: 800;
            margin-bottom: 0.24rem;
          }
          .bt-handoff-title {
            font-size: 1.2rem;
            font-weight: 800;
            line-height: 1.35;
            color: var(--text-color);
            margin: 0;
          }
          .bt-handoff-status {
            padding: 0.34rem 0.72rem;
            border-radius: 999px;
            border: 1px solid var(--bt-handoff-accent);
            font-size: 0.86rem;
            font-weight: 800;
            color: var(--bt-handoff-accent);
            background: rgba(255, 255, 255, 0.76);
          }
          .bt-handoff-main {
            display: grid;
            grid-template-columns: minmax(220px, 0.9fr) minmax(260px, 1.1fr);
            gap: 0.9rem;
            align-items: stretch;
          }
          .bt-handoff-summary {
            font-size: 1rem;
            line-height: 1.55;
            color: var(--text-color);
            opacity: 0.74;
          }
          .bt-handoff-chips {
            display: grid;
            grid-template-columns: repeat(3, minmax(0, 1fr));
            gap: 0.5rem;
            margin-top: 0.82rem;
          }
          .bt-handoff-chip {
            border-right: 1px solid rgba(148, 163, 184, 0.22);
            border-top: 1px solid rgba(148, 163, 184, 0.20);
            border-bottom: 1px solid rgba(148, 163, 184, 0.20);
            border-left: 0;
            border-radius: 8px;
            padding: 0.62rem 0.68rem;
            background: var(--secondary-background-color);
            min-width: 0;
          }
          .bt-handoff-chip-positive { border-top-color: rgba(15, 143, 131, 0.32); }
          .bt-handoff-chip-danger { border-top-color: rgba(180, 35, 24, 0.32); }
          .bt-handoff-chip-label {
            display: block;
            font-size: 0.78rem;
            color: var(--text-color);
            opacity: 0.68;
            font-weight: 800;
            margin-bottom: 0.2rem;
          }
          .bt-handoff-chip-value {
            display: block;
            font-size: 0.96rem;
            font-weight: 800;
            color: var(--text-color);
            overflow-wrap: anywhere;
          }
          .bt-handoff-chip-detail {
            display: block;
            margin-top: 0.12rem;
            color: var(--text-color);
            opacity: 0.62;
            font-size: 0.72rem;
            line-height: 1.3;
          }
          .bt-handoff-reasons {
            border-radius: 8px;
            background: var(--secondary-background-color);
            border: 1px solid rgba(148, 163, 184, 0.22);
            padding: 0.76rem 0.86rem;
          }
          .bt-handoff-reason-title {
            font-size: 0.84rem;
            color: var(--bt-handoff-accent);
            font-weight: 800;
            margin-bottom: 0.4rem;
          }
          .bt-handoff-reasons ul {
            margin: 0;
            padding-left: 1.05rem;
            color: var(--text-color);
            opacity: 0.78;
            line-height: 1.45;
            font-size: 0.92rem;
          }
          .bt-handoff-action {
            display: grid;
            grid-template-columns: minmax(220px, 0.8fr) minmax(260px, 1.2fr);
            gap: 0.9rem;
            margin-top: 0.95rem;
            padding-top: 0.85rem;
            border-top: 1px solid rgba(148, 163, 184, 0.24);
          }
          .bt-handoff-action-label {
            color: var(--bt-handoff-accent);
            font-size: 0.88rem;
            font-weight: 800;
            margin-bottom: 0.18rem;
          }
          .bt-handoff-action-text {
            color: var(--text-color);
            font-size: 1.02rem;
            font-weight: 800;
            line-height: 1.35;
          }
          .bt-handoff-boundary {
            color: var(--text-color);
            opacity: 0.76;
            font-size: 0.92rem;
            line-height: 1.45;
          }
          .bt-handoff-action-hint {
            min-height: 2.45rem;
            display: flex;
            align-items: center;
            border-left: 4px solid var(--bt-handoff-accent);
            background: var(--bt-handoff-soft);
            border-radius: 8px;
            padding: 0.58rem 0.72rem;
            color: var(--text-color);
            opacity: 0.76;
            font-size: 0.92rem;
            line-height: 1.4;
          }
          .bt-handoff-action-hint--positive {
            --bt-handoff-accent: #0f8f83;
            --bt-handoff-soft: rgba(15, 143, 131, 0.10);
          }
          .bt-handoff-action-hint--warning {
            --bt-handoff-accent: #b45309;
            --bt-handoff-soft: rgba(180, 83, 9, 0.10);
          }
          .bt-handoff-action-hint--danger {
            --bt-handoff-accent: #b42318;
            --bt-handoff-soft: rgba(180, 35, 24, 0.10);
          }
          @media (max-width: 760px) {
            .bt-handoff-main { grid-template-columns: 1fr; }
            .bt-handoff-chips { grid-template-columns: 1fr; }
            .bt-handoff-action { grid-template-columns: 1fr; }
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    st.markdown(
        f'<section class="bt-handoff-panel bt-handoff-panel--{tone}">'
        f'<div class="bt-handoff-head">'
        f"<div><div class=\"bt-handoff-kicker\">2차 단계 진입 판단</div>"
        f'<h4 class="bt-handoff-title">2차 실전성 검증 Handoff</h4></div>'
        f'<div class="bt-handoff-status">{status}</div>'
        f"</div>"
        f'<div class="bt-handoff-main">'
        f'<div><div class="bt-handoff-summary">{summary}</div>'
        f'<div class="bt-handoff-chips">{entry_items}</div></div>'
        f'<div class="bt-handoff-reasons"><div class="bt-handoff-reason-title">{reason_title}</div>'
        f"<ul>{reason_items}</ul></div>"
        f"</div>"
        f'<div class="bt-handoff-action">'
        f"<div>"
        f'<div class="bt-handoff-action-label">{escape(action_label)}</div>'
        f'<div class="bt-handoff-action-text">{action_text}</div>'
        f"</div>"
        f'<div class="bt-handoff-boundary">{escape(action_detail)} '
        f"이 단계는 검증 source 등록만 수행합니다. 최종 선택, 투자 추천, live 승인, 주문 지시는 발생하지 않습니다.</div>"
        f"</div>"
        f"</section>",
        unsafe_allow_html=True,
    )


def _consume_practical_validation_handoff_action(action_value: dict[str, Any] | None, bundle: dict[str, Any]) -> None:
    """Handle the React card submit event without duplicating the source write on rerun."""
    if not isinstance(action_value, dict) or action_value.get("action") != "submit":
        return
    nonce = str(action_value.get("nonce") or "")
    if not nonce:
        return
    consumed_key = "latest_run_candidate_review_draft_component_nonce"
    if st.session_state.get(consumed_key) == nonce:
        return
    st.session_state[consumed_key] = nonce
    _queue_candidate_review_draft(_candidate_review_draft_from_bundle(bundle))
    st.rerun()


def _render_policy_signal_summary_panel(meta: dict[str, Any]) -> None:
    gate_summary = build_handoff_gate_summary(meta)
    evaluation = dict(gate_summary.get("evaluation") or {})
    can_submit = bool(gate_summary.get("can_submit"))
    tone = "positive" if can_submit and str(evaluation.get("tone") or "") == "success" else "warning" if can_submit else "danger"
    status = "1차 통과" if can_submit else "기준 확인 필요"
    route_label = escape(str(evaluation.get("route_label") or "-"))
    verdict = escape(str(evaluation.get("verdict") or "-"))
    next_action = escape(str(evaluation.get("next_action") or "-"))
    if can_submit:
        action_title = "다음 단계"
        action_items = ["Practical Validation에서 실전성 검증을 이어갑니다."]
    else:
        action_title = str(gate_summary.get("reason_title") or "상태")
        action_items = [str(item) for item in list(gate_summary.get("action_items") or [])] or ["막는 항목 없음"]
    gate_groups = list(gate_summary.get("gate_groups") or [])

    chip_html = "".join(
        (
            f'<div class="bt-policy-signal__chip bt-policy-signal__chip--{escape(str(group.get("tone") or "neutral"))}">'
            f'<span>{escape(str(group.get("label") or "-"))}</span>'
            f'<strong>{escape(str(group.get("value") or "-"))}</strong>'
            "</div>"
        )
        for group in gate_groups
    )
    action_html = "".join(f"<li>{escape(item)}</li>" for item in action_items)

    st.markdown(
        f"""
<style>
.bt-policy-signal {{
  --ps-accent: #64748b;
  --ps-soft: rgba(100, 116, 139, 0.10);
  border-left: 4px solid var(--ps-accent);
  border-top: 1px solid rgba(148, 163, 184, 0.24);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  padding: 1.05rem 1.15rem 1rem;
  margin: 0.35rem 0 1rem;
  background: linear-gradient(90deg, var(--ps-soft), rgba(255, 255, 255, 0));
}}
.bt-policy-signal--positive {{
  --ps-accent: #0f8f83;
  --ps-soft: rgba(15, 143, 131, 0.10);
}}
.bt-policy-signal--warning {{
  --ps-accent: #b45309;
  --ps-soft: rgba(180, 83, 9, 0.10);
}}
.bt-policy-signal--danger {{
  --ps-accent: #b42318;
  --ps-soft: rgba(180, 35, 24, 0.10);
}}
.bt-policy-signal__head {{
  display: flex;
  justify-content: space-between;
  gap: 1rem;
  align-items: flex-start;
}}
.bt-policy-signal__kicker {{
  color: var(--ps-accent);
  font-size: 0.86rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
}}
.bt-policy-signal h4 {{
  margin: 0;
  color: var(--text-color);
  font-size: 1.25rem;
  line-height: 1.35;
  letter-spacing: 0;
}}
.bt-policy-signal__status {{
  flex: 0 0 auto;
  border: 1px solid var(--ps-accent);
  border-radius: 999px;
  color: var(--ps-accent);
  background: rgba(255, 255, 255, 0.76);
  padding: 0.34rem 0.72rem;
  font-size: 0.84rem;
  font-weight: 800;
}}
.bt-policy-signal__body {{
  display: grid;
  grid-template-columns: minmax(0, 1.1fr) minmax(16rem, 0.9fr);
  gap: 1rem;
  margin-top: 0.95rem;
}}
.bt-policy-signal__verdict {{
  color: var(--text-color);
  font-size: 1.05rem;
  font-weight: 800;
  line-height: 1.45;
}}
.bt-policy-signal__route {{
  margin-top: 0.35rem;
  color: #667085;
  line-height: 1.55;
}}
.bt-policy-signal__chips {{
  display: grid;
  grid-template-columns: repeat(3, minmax(0, 1fr));
  gap: 0.55rem;
  margin-top: 0.9rem;
}}
.bt-policy-signal__chip {{
  border-top: 3px solid rgba(100, 116, 139, 0.24);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  padding: 0.62rem 0.65rem;
  background: rgba(148, 163, 184, 0.06);
  min-width: 0;
}}
.bt-policy-signal__chip--positive {{ border-top-color: rgba(15, 143, 131, 0.34); }}
.bt-policy-signal__chip--warning {{ border-top-color: rgba(180, 83, 9, 0.34); }}
.bt-policy-signal__chip--danger {{ border-top-color: rgba(180, 35, 24, 0.34); }}
.bt-policy-signal__chip span {{
  display: block;
  color: #667085;
  font-size: 0.78rem;
  font-weight: 800;
}}
.bt-policy-signal__chip strong {{
  display: block;
  margin-top: 0.16rem;
  color: var(--text-color);
  font-size: 1rem;
  line-height: 1.25;
}}
.bt-policy-signal__actions {{
  border-left: 1px solid rgba(148, 163, 184, 0.30);
  padding-left: 1rem;
}}
.bt-policy-signal__actions span {{
  display: block;
  color: var(--ps-accent);
  font-size: 0.86rem;
  font-weight: 800;
  margin-bottom: 0.42rem;
}}
.bt-policy-signal__actions ul {{
  margin: 0;
  padding-left: 1rem;
  color: #667085;
  line-height: 1.6;
}}
@media (max-width: 900px) {{
  .bt-policy-signal__body {{ grid-template-columns: 1fr; }}
  .bt-policy-signal__chips {{ grid-template-columns: 1fr; }}
  .bt-policy-signal__actions {{ border-left: 0; padding-left: 0; }}
}}
</style>
<section class="bt-policy-signal bt-policy-signal--{tone}">
  <div class="bt-policy-signal__head">
    <div>
      <div class="bt-policy-signal__kicker">검증 신호 요약</div>
      <h4>{verdict}</h4>
    </div>
    <div class="bt-policy-signal__status">{escape(status)}</div>
  </div>
  <div class="bt-policy-signal__body">
    <div>
      <div class="bt-policy-signal__verdict">다음 경로: {route_label}</div>
      <div class="bt-policy-signal__route">{next_action}</div>
      <div class="bt-policy-signal__chips">{chip_html}</div>
    </div>
    <div class="bt-policy-signal__actions">
      <span>{escape(action_title)}</span>
      <ul>{action_html}</ul>
    </div>
  </div>
</section>
        """,
        unsafe_allow_html=True,
    )

def _policy_signal_effect_label(value: Any) -> str:
    mapping = {
        "block": "먼저 해결",
        "review": "2차 확인",
        "pass": "통과",
        "context": "참고",
    }
    return mapping.get(str(value or "").strip().lower(), str(value or "-"))


def _policy_signal_effect_tone(value: Any) -> str:
    mapping = {
        "block": "danger",
        "review": "warning",
        "pass": "positive",
        "context": "neutral",
    }
    return mapping.get(str(value or "").strip().lower(), "neutral")


def _policy_signal_row_sort_key(row: dict[str, Any]) -> tuple[int, str, str]:
    rank = {"block": 0, "review": 1, "pass": 2, "context": 3}
    effect = str(row.get("effect") or "").strip().lower()
    return (
        rank.get(effect, 4),
        str(row.get("group") or ""),
        str(row.get("signal") or ""),
    )


def _policy_signal_display_rows(frame_rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    return [
        {
            "구분": row.get("group") or "-",
            "신호": row.get("signal") or "-",
            "상태": row.get("status") or "-",
            "판정": _policy_signal_effect_label(row.get("effect")),
            "다음 위치": row.get("next_surface") or "-",
            "확인한 것": row.get("checked_evidence") or "-",
            "표시 근거": row.get("display_detail") or row.get("meaning") or "-",
            "의미": row.get("meaning") or "-",
        }
        for row in frame_rows
    ]


def _policy_signal_group_status(rows: list[dict[str, Any]]) -> tuple[str, str]:
    counts = {
        "block": sum(1 for row in rows if row.get("effect") == "block"),
        "review": sum(1 for row in rows if row.get("effect") == "review"),
        "pass": sum(1 for row in rows if row.get("effect") == "pass"),
        "context": sum(1 for row in rows if row.get("effect") == "context"),
    }
    if counts["block"]:
        return f"먼저 해결 {counts['block']}", "danger"
    if counts["review"]:
        return f"2차 확인 {counts['review']}", "warning"
    if counts["pass"]:
        return f"통과 {counts['pass']}", "positive"
    return f"참고 {counts['context']}", "neutral"


def _render_policy_signal_gate_board(rows: list[dict[str, Any]], evaluation: dict[str, Any]) -> None:
    inventory = dict(evaluation.get("policy_signal_inventory") or {})
    sorted_rows = sorted([dict(row or {}) for row in rows], key=_policy_signal_row_sort_key)
    first_stage_rows = sorted(
        [
            dict(row or {})
            for row in list(inventory.get("first_stage_rows") or [])
            if row.get("effect") in {"block", "pass"}
        ],
        key=_policy_signal_row_sort_key,
    )
    if not first_stage_rows:
        first_stage_rows = [
            row
            for row in sorted_rows
            if row.get("stage_owner") == "first_stage" and row.get("effect") in {"block", "pass"}
        ]
    first_block_count = sum(1 for row in first_stage_rows if row.get("effect") == "block")
    first_pass_count = sum(1 for row in first_stage_rows if row.get("effect") == "pass")
    context_count = sum(1 for row in sorted_rows if row.get("effect") == "context")
    entry_ready = bool(evaluation.get("can_enter_practical_validation"))
    board_tone = "positive" if entry_ready else "danger"
    headline = (
        "1차에서 확인할 기준이 모두 통과 상태입니다."
        if entry_ready
        else "source 등록 전 먼저 해결할 1차 기준이 있습니다."
    )
    subhead = (
        "이 보드는 Backtest Analysis에서 확정 가능한 source 등록 기준만 보여줍니다."
    )
    metrics = [
        {
            "label": "먼저 해결",
            "value": str(first_block_count),
            "detail": "1차 source 등록 차단",
            "tone": "danger" if first_block_count else "positive",
        },
        {
            "label": "1차 통과",
            "value": str(first_pass_count),
            "detail": "Backtest에서 확인 완료",
            "tone": "positive",
        },
        {
            "label": "기술 근거",
            "value": str(len(sorted_rows)),
            "detail": f"참고 {context_count}개 별도 보존",
            "tone": "neutral",
        },
    ]

    if is_backtest_policy_signal_board_available():
        render_backtest_policy_signal_board(
            tone=board_tone,
            headline=headline,
            subhead=subhead,
            metrics=metrics,
            first_stage_rows=first_stage_rows,
            key="backtest_policy_signal_board",
        )
        return

    st.warning("Policy Signal React component build를 찾지 못했습니다. 기술 원천 표로 대체 표시합니다.")
    st.dataframe(pd.DataFrame(_policy_signal_display_rows(first_stage_rows)), width="stretch", hide_index=True)
    return


def _render_practical_validation_next_action(bundle: dict[str, Any]) -> None:
    state = _build_practical_validation_handoff_state(bundle)
    if not is_backtest_handoff_action_available():
        st.error("Handoff React component build를 찾지 못했습니다. component build 후 source 등록 UI가 표시됩니다.")
        return
    can_submit = bool(state.get("can_submit"))
    boundary_text = (
        "이 버튼은 결과를 Practical Validation이 읽는 current selection source로 등록합니다. "
        "최종 선택, 투자 추천, live 승인, 주문 지시는 발생하지 않습니다."
        if can_submit
        else "source 등록을 막는 항목이 남아 있어 버튼이 비활성화되어 있습니다. "
        "먼저 Handoff 카드의 blocker를 해소한 뒤 다시 실행하세요."
    )
    action_value = render_backtest_handoff_action(
        status_label=str(state.get("status_label") or "-"),
        tone=str(state.get("tone") or "neutral"),
        summary=str(state.get("summary") or "-"),
        reason_title=str(state.get("reason_title") or "상태"),
        reasons=[str(item) for item in list(state.get("display_reasons") or [])],
        entry_cards=[dict(item) for item in list(state.get("entry_cards") or [])],
        action_text=str(state.get("action_text") or "-"),
        button_label=str(state.get("button_label") or "2차 검증으로 보내기"),
        disabled=not can_submit,
        boundary_text=boundary_text,
        key="latest_run_candidate_review_draft_component",
    )
    _consume_practical_validation_handoff_action(action_value, bundle)


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


def _render_backtest_input_warning(message: str) -> None:
    st.warning(message)


def _display_result_header_value(value: Any) -> str:
    text = str(value or "").strip()
    return text or "-"


def _format_result_kpi_value(row: pd.Series, column: str, formatter: Any) -> str:
    try:
        value = row[column]
        if pd.isna(value):
            return "-"
        return formatter(float(value))
    except (KeyError, TypeError, ValueError):
        return "-"


def _build_result_kpi_items(summary_df: pd.DataFrame) -> list[dict[str, str]]:
    row = summary_df.iloc[0] if summary_df is not None and not summary_df.empty else pd.Series(dtype=object)
    return [
        {
            "label": "End Balance",
            "caption": "최종 평가액",
            "value": _format_result_kpi_value(row, "End Balance", _format_currency),
            "tone": "balance",
        },
        {
            "label": "CAGR",
            "caption": "연환산 수익률",
            "value": _format_result_kpi_value(row, "CAGR", _format_percent),
            "tone": "return",
        },
        {
            "label": "Sharpe Ratio",
            "caption": "위험 대비 성과",
            "value": _format_result_kpi_value(row, "Sharpe Ratio", _format_ratio),
            "tone": "ratio",
        },
        {
            "label": "Maximum Drawdown",
            "caption": "최대 낙폭",
            "value": _format_result_kpi_value(row, "Maximum Drawdown", _format_percent),
            "tone": "risk",
        },
    ]


def _render_backtest_result_header(bundle: dict[str, Any], summary_df: pd.DataFrame) -> None:
    meta = dict(bundle.get("meta") or {})
    strategy_name = _display_result_header_value(bundle.get("strategy_name") or meta.get("strategy_name"))
    start = _display_result_header_value(meta.get("start"))
    end = _display_result_header_value(meta.get("end"))
    actual_end = _display_result_header_value(meta.get("actual_result_end") or end)
    universe = _display_result_header_value(meta.get("preset_name") or meta.get("universe_mode"))
    data_mode = _display_result_header_value(meta.get("data_mode"))
    execution_mode = _display_result_header_value(meta.get("execution_mode"))
    tickers = list(meta.get("tickers") or [])
    ticker_label = f"{len(tickers)}개 종목" if tickers else "종목 수 미상"
    period_label = f"{start} -> {end}" if start != "-" and end != "-" else "기간 정보 제한"
    actual_label = actual_end if actual_end != "-" else "계산 기준 제한"
    headline = f"{strategy_name} 백테스트 결과"
    subtitle = (
        "핵심 성과를 먼저 보고, 바로 아래에서 이 성과가 어떤 데이터 기준으로 계산됐는지 확인합니다."
    )
    basis_items = [
        ("기간", period_label),
        ("계산 기준", actual_label),
        ("Universe", universe),
        ("구성", ticker_label),
        ("Data", data_mode),
        ("Execution", execution_mode),
    ]
    basis_html = "".join(
        (
            '<span class="backtest-result-hero__basis-item">'
            f'<b>{escape(label)}</b>'
            f' {escape(value)}'
            '</span>'
        )
        for label, value in basis_items
    )
    kpi_html = "".join(
        (
            f'<div class="backtest-result-hero__kpi backtest-result-hero__kpi--{escape(item["tone"])}">'
            f'<div class="backtest-result-hero__kpi-label">{escape(item["label"])}</div>'
            f'<div class="backtest-result-hero__kpi-value">{escape(item["value"])}</div>'
            f'<div class="backtest-result-hero__kpi-caption">{escape(item["caption"])}</div>'
            '</div>'
        )
        for item in _build_result_kpi_items(summary_df)
    )
    st.markdown(
        f"""
<style>
.backtest-result-hero {{
  border-left: 4px solid #ff4b4b;
  border-top: 1px solid rgba(148, 163, 184, 0.24);
  border-bottom: 1px solid rgba(148, 163, 184, 0.24);
  padding: 1.05rem 1.15rem 0;
  margin: 1.2rem 0 1.15rem;
  background:
    linear-gradient(90deg, rgba(255, 75, 75, 0.08), rgba(255, 255, 255, 0) 68%);
}}
.backtest-result-hero__eyebrow {{
  color: #ff6b6b;
  font-size: 0.86rem;
  font-weight: 800;
  margin-bottom: 0.25rem;
}}
.backtest-result-hero h3 {{
  margin: 0;
  color: var(--text-color);
  font-size: 1.75rem;
  line-height: 1.25;
  letter-spacing: 0;
}}
.backtest-result-hero p {{
  margin: 0.45rem 0 0;
  color: #667085;
  line-height: 1.5;
}}
.backtest-result-hero__basis {{
  display: flex;
  flex-wrap: wrap;
  gap: 0.35rem 1.15rem;
  margin-top: 0.85rem;
  color: #667085;
  font-size: 0.84rem;
  line-height: 1.35;
}}
.backtest-result-hero__basis-item {{
  min-width: 0;
  overflow-wrap: anywhere;
}}
.backtest-result-hero__basis-item b {{
  color: var(--text-color);
  margin-right: 0.34rem;
}}
.backtest-result-hero__kpis {{
  display: grid;
  grid-template-columns: repeat(4, minmax(0, 1fr));
  margin-top: 1rem;
  border-top: 1px solid rgba(148, 163, 184, 0.22);
}}
.backtest-result-hero__kpi {{
  min-width: 0;
  padding: 0.92rem 1rem 1rem;
  border-left: 1px solid rgba(148, 163, 184, 0.18);
}}
.backtest-result-hero__kpi:first-child {{
  border-left: 0;
  padding-left: 0;
}}
.backtest-result-hero__kpi-label {{
  color: #475467;
  font-size: 0.82rem;
  font-weight: 800;
  line-height: 1.25;
}}
.backtest-result-hero__kpi-value {{
  margin-top: 0.25rem;
  color: var(--text-color);
  font-size: 1.85rem;
  font-weight: 760;
  line-height: 1.12;
  letter-spacing: 0;
  overflow-wrap: anywhere;
}}
.backtest-result-hero__kpi-caption {{
  margin-top: 0.25rem;
  color: #667085;
  font-size: 0.82rem;
  line-height: 1.35;
}}
.backtest-result-hero__kpi--return .backtest-result-hero__kpi-value {{
  color: #087f5b;
}}
.backtest-result-hero__kpi--risk .backtest-result-hero__kpi-value {{
  color: #b54708;
}}
@media (max-width: 760px) {{
  .backtest-result-hero__kpis {{
    grid-template-columns: repeat(2, minmax(0, 1fr));
  }}
  .backtest-result-hero__kpi:nth-child(odd) {{
    border-left: 0;
    padding-left: 0;
  }}
  .backtest-result-hero__kpi:nth-child(n + 3) {{
    border-top: 1px solid rgba(148, 163, 184, 0.18);
  }}
}}
@media (max-width: 520px) {{
  .backtest-result-hero__kpis {{
    grid-template-columns: 1fr;
  }}
  .backtest-result-hero__kpi {{
    border-left: 0;
    border-top: 1px solid rgba(148, 163, 184, 0.18);
    padding-left: 0;
  }}
  .backtest-result-hero__kpi:first-child {{
    border-top: 0;
  }}
}}
</style>
<section class="backtest-result-hero">
  <div class="backtest-result-hero__eyebrow">백테스트 결과</div>
  <h3>{escape(headline)}</h3>
  <p>{escape(subtitle)}</p>
  <div class="backtest-result-hero__basis">{basis_html}</div>
  <div class="backtest-result-hero__kpis">{kpi_html}</div>
</section>
        """,
        unsafe_allow_html=True,
    )


def _render_last_run() -> None:
    error = st.session_state.backtest_last_error
    error_kind = st.session_state.backtest_last_error_kind
    bundle = st.session_state.backtest_last_bundle

    if error:
        if error_kind == "input":
            _render_backtest_input_warning(error)
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

    _render_backtest_result_header(bundle, summary_df)
    _render_data_trust_summary(meta)
    _render_practical_validation_next_action(bundle)

    tab_labels = ["Summary", "Equity Curve", "Balance Extremes", "Period Extremes"]
    if has_selection_history:
        tab_labels.append("Selection History")
    if has_dynamic_details:
        tab_labels.append("Dynamic Universe")
    if has_real_money_details:
        tab_labels.append("검증 신호 · Policy Signals")
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

def _render_real_money_details(bundle: dict[str, Any]) -> None:
    meta = bundle.get("meta") or {}
    if not meta.get("real_money_hardening"):
        st.caption("이 결과에는 promotion policy signal hardening 정보가 없습니다.")
        return

    result_df = bundle.get("result_df")
    benchmark_chart_df = bundle.get("benchmark_chart_df")
    benchmark_summary_df = bundle.get("benchmark_summary_df")
    inventory = build_policy_signal_inventory(meta)
    evaluation = build_next_step_readiness_evaluation(meta)
    rows = list(inventory.get("rows") or [])
    context_rows = [row for row in rows if row.get("effect") == "context"]

    def _value_list_caption(prefix: str, values: list[Any] | tuple[Any, ...] | None) -> None:
        if values:
            st.caption(prefix + ": " + ", ".join(f"`{value}`" for value in list(values)))

    def _optional_pct(value: Any) -> str:
        return f"{float(value):.2%}" if value is not None else "-"

    _render_policy_signal_gate_board(rows, evaluation)

    if context_rows:
        with st.expander("참고 신호 보기", expanded=False):
            st.dataframe(pd.DataFrame(_policy_signal_display_rows(context_rows)), width="stretch", hide_index=True)

    with st.expander("성과 / Benchmark 근거", expanded=False):
        metric_rows: list[dict[str, Any]] = []
        for label, value in [
            ("Benchmark", meta.get("benchmark_label") or meta.get("benchmark_ticker") or meta.get("benchmark_contract")),
            ("Benchmark Available", "Yes" if meta.get("benchmark_available") else "No"),
            ("Benchmark CAGR", _optional_pct(meta.get("benchmark_cagr"))),
            ("Net CAGR Spread", _optional_pct(meta.get("net_cagr_spread"))),
            ("Benchmark Coverage", _optional_pct(meta.get("benchmark_row_coverage"))),
            ("Validation Status", str(meta.get("validation_status") or "normal").upper()),
            ("Rolling Review", str(meta.get("rolling_review_status") or "-").upper()),
            ("Split-Period Check", str(meta.get("out_of_sample_review_status") or "-").upper()),
        ]:
            metric_rows.append({"항목": label, "값": value})
        st.dataframe(pd.DataFrame(metric_rows), use_container_width=True, hide_index=True)
        if benchmark_chart_df is not None and result_df is not None:
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
            st.caption("전략은 비용 반영 후 net 곡선이고, benchmark는 reference curve입니다.")

    with st.expander("실행 / 비용 / 유동성 근거", expanded=False):
        turnover_status = str(meta.get("turnover_estimation_status") or "").strip().lower()
        net_cost_status = str(meta.get("net_cost_curve_status") or "").strip().lower()
        execution_rows = [
            {"항목": "Transaction Cost", "값": f"{float(meta.get('transaction_cost_bps') or 0.0):.1f} bps"},
            {"항목": "Turnover Estimate", "값": turnover_status or "-"},
            {"항목": "Net Cost Curve", "값": net_cost_status or "-"},
            {"항목": "Avg Turnover", "값": _optional_pct(meta.get("avg_turnover"))},
            {"항목": "Estimated Cost Total", "값": f"{float(meta.get('estimated_cost_total') or 0.0):,.1f}" if meta.get("estimated_cost_total") is not None else "-"},
            {"항목": "Liquidity Policy", "값": str(meta.get("liquidity_policy_status") or "-").upper()},
            {"항목": "Liquidity Clean Coverage", "값": _optional_pct(meta.get("liquidity_clean_coverage"))},
            {"항목": "ETF Operability", "값": str(meta.get("etf_operability_status") or "-").upper()},
            {"항목": "Guardrail Policy", "값": str(meta.get("guardrail_policy_status") or "-").upper()},
        ]
        st.dataframe(pd.DataFrame(execution_rows), use_container_width=True, hide_index=True)
        _value_list_caption("Liquidity policy signals", meta.get("liquidity_policy_watch_signals"))
        _value_list_caption("ETF operability signals", meta.get("etf_operability_watch_signals"))
        _value_list_caption("Guardrail policy signals", meta.get("guardrail_policy_watch_signals"))

    with st.expander("기술 원천 보기", expanded=False):
        st.dataframe(pd.DataFrame(evaluation.get("criteria_rows") or []), width="stretch", hide_index=True)
        if result_df is not None and "Estimated Cost" in result_df.columns:
            detail_cols = [
                column
                for column in [
                    "Date",
                    "Gross Total Balance",
                    "Total Balance",
                    "Turnover",
                    "Estimated Cost",
                    "Cumulative Estimated Cost",
                ]
                if column in result_df.columns
            ]
            if detail_cols:
                st.markdown("##### Cost Detail Preview")
                st.dataframe(result_df[detail_cols].head(12), use_container_width=True, hide_index=True)
        if benchmark_summary_df is not None:
            st.markdown("##### Benchmark Summary")
            st.dataframe(benchmark_summary_df, use_container_width=True, hide_index=True)


def _render_real_money_details_legacy(bundle: dict[str, Any]) -> None:
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

    focus_count = len(_validation_focus_items())
    review_signal_count = len(_validation_review_signals())
    _render_policy_signal_summary_panel(meta)

    overview_tab, review_tab, execution_tab, detail_tab = st.tabs(
        ["현재 판단", "검토 근거", "실행 부담", "기술 상세"]
    )

    with overview_tab:
        st.caption(
            "이 섹션은 이 전략을 Backtest 1차 후보로 볼 수 있는지 보여줍니다. "
            "실제 paper observation, 소액 검토, 운영 모니터링 조건은 이후 단계에서 다시 정의합니다."
        )

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
