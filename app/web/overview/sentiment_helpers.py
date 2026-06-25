from __future__ import annotations

from datetime import date
from html import escape
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_market_sentiment,
)
from app.web.backtest_ui_components import render_status_card_grid
from app.web.overview.session_helpers import _snapshot_value
from app.web.overview_dashboard_helpers import load_overview_market_sentiment_snapshot
from app.web.overview_ui_components import (
    OVERVIEW_COLOR_DANGER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_PRIMARY,
    OVERVIEW_COLOR_WARNING,
    OVERVIEW_SERIES_COLORS,
)


def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def _render_market_job_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = result.get("status")
    message = result.get("message") or ""
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    details = result.get("details") or {}
    if details:
        source = details.get("source") or "-"
        method = details.get("method") or details.get("method_requested") or "-"
        duration = result.get("duration_sec")
        st.caption(
            "Rows: "
            f"{result.get('rows_written') or 0}, "
            f"Events: {details.get('events_found') or '-'}, "
            f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
        )


def render_sentiment_header() -> None:
    st.markdown("### 시장 심리 컨텍스트")


def render_sentiment_controls() -> None:
    control_cols = st.columns([1.1, 1, 1], gap="small", vertical_alignment="bottom")
    if control_cols[0].button(
        "시장 심리 갱신",
        key="overview_market_sentiment_refresh",
        use_container_width=True,
        type="primary",
    ):
        with st.spinner("Refreshing CNN Fear & Greed / AAII sentiment..."):
            _store_overview_job_result(
                "overview_market_sentiment_result",
                run_overview_market_sentiment(),
            )
            load_overview_market_sentiment_snapshot.clear()
        st.rerun()
    if control_cols[1].button(
        "화면 새로고침",
        key="overview_market_sentiment_reload",
        use_container_width=True,
    ):
        load_overview_market_sentiment_snapshot.clear()
        st.rerun()
    control_cols[2].caption("CNN / AAII 저장 데이터 기준")


def render_sentiment_job_result() -> None:
    _render_market_job_result("overview_market_sentiment_result")


def load_sentiment_snapshot() -> dict[str, Any]:
    return load_overview_market_sentiment_snapshot()


def _sentiment_status_tone(status: Any) -> str:
    normalized = str(status or "").upper()
    if normalized == "OK":
        return "positive"
    if normalized in {"REVIEW", "DUE"}:
        return "warning"
    if normalized in {"MISSING", "ERROR", "STALE"}:
        return "danger"
    return "neutral"


def _sentiment_tone(value: Any) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in {"positive", "warning", "danger", "neutral"}:
        return normalized
    return _sentiment_status_tone(value)


def _sentiment_trend_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        rows = pd.DataFrame([{"Date": date.today().isoformat(), "Series": "No Data", "Value": 0.0, "Source": "-"}])
    chart_rows = rows.copy()
    chart_rows["Date Parsed"] = pd.to_datetime(chart_rows.get("Date"), errors="coerce")
    chart_rows["Value"] = pd.to_numeric(chart_rows.get("Value"), errors="coerce")
    chart_rows = chart_rows.dropna(subset=["Date Parsed", "Value"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Date Parsed": pd.Timestamp(date.today()), "Series": "No Data", "Value": 0.0, "Source": "-"}])
    return (
        alt.Chart(chart_rows)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("Date Parsed:T", title=None, axis=alt.Axis(format="%b %d", labelAngle=-35)),
            y=alt.Y("Value:Q", title=None),
            color=alt.Color(
                "Series:N",
                title=None,
                legend=alt.Legend(orient="bottom"),
                scale=alt.Scale(range=OVERVIEW_SERIES_COLORS),
            ),
            tooltip=["Date Parsed:T", "Series:N", "Value:Q", "Source:N"],
        )
        .properties(height=260)
    )


def _sentiment_component_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        rows = pd.DataFrame([{"Series": "No Data", "Score": 0.0, "Rating": "-", "Status": "-"}])
    chart_rows = rows.copy()
    chart_rows["Score"] = pd.to_numeric(chart_rows.get("Score"), errors="coerce").fillna(0.0)
    chart_rows["Bar Color"] = chart_rows["Score"].map(
        lambda value: OVERVIEW_COLOR_DANGER
        if value < 25
        else OVERVIEW_COLOR_WARNING
        if value < 45
        else OVERVIEW_COLOR_NEUTRAL
        if value < 55
        else OVERVIEW_COLOR_POSITIVE
        if value < 75
        else OVERVIEW_COLOR_PRIMARY
    )
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Score:Q", title=None, scale=alt.Scale(domain=[0, 100])),
            y=alt.Y("Series:N", sort="-x", title=None, axis=alt.Axis(labelLimit=180)),
            color=alt.Color("Bar Color:N", scale=None, legend=None),
            tooltip=["Series:N", "Score:Q", "Rating:N", "Status:N"],
        )
        .properties(height=max(220, min(390, len(chart_rows) * 38)))
    )


def _render_sentiment_analysis_panel(analysis: dict[str, Any]) -> None:
    phase_label = escape(str(analysis.get("phase_label") or "-"))
    headline = escape(str(analysis.get("headline") or "-"))
    summary = escape(str(analysis.get("summary") or ""))
    tone = escape(_sentiment_tone(analysis.get("tone") or "neutral"))
    data_confidence = dict(analysis.get("data_confidence") or {})
    confidence_status = escape(str(data_confidence.get("status") or "-"))
    confidence_detail = escape(str(data_confidence.get("detail") or ""))

    st.markdown(
        """
        <style>
          .ov-sentiment-brief {
            margin: 0.45rem 0 0.8rem 0;
            padding: 0.92rem 1rem;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-left: 4px solid var(--ov-sentiment-tone, #64748b);
            border-radius: 8px;
            background: linear-gradient(135deg, color-mix(in srgb, var(--ov-sentiment-tone, #64748b) 8%, transparent), rgba(255,255,255,0.96));
          }
          .ov-sentiment-eyebrow {
            color: #475569;
            font-size: 0.75rem;
            font-weight: 760;
            letter-spacing: 0;
            text-transform: uppercase;
          }
          .ov-sentiment-headline {
            margin-top: 0.34rem;
            color: #111827;
            font-size: 1.08rem;
            line-height: 1.26;
            font-weight: 820;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-summary {
            margin-top: 0.35rem;
            max-width: 76rem;
            color: #334155;
            font-size: 0.88rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-meta {
            display: flex;
            gap: 0.45rem;
            flex-wrap: wrap;
            margin-top: 0.58rem;
          }
          .ov-sentiment-pill {
            display: inline-flex;
            align-items: center;
            min-height: 1.38rem;
            padding: 0.16rem 0.52rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--ov-sentiment-tone, #64748b) 13%, transparent);
            color: #111827;
            font-size: 0.76rem;
            font-weight: 760;
            line-height: 1.15;
          }
          .ov-sentiment-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(185px, 1fr));
            gap: 0.58rem;
            margin: 0.35rem 0 0.85rem 0;
          }
          .ov-sentiment-step-grid {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(270px, 1fr));
            gap: 0.72rem;
            margin: 0.4rem 0 0.95rem 0;
          }
          .ov-sentiment-step {
            min-height: 148px;
            padding: 0.86rem 0.92rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-left: 4px solid var(--ov-step-tone, #64748b);
            border-radius: 8px;
            background: rgba(255, 255, 255, 0.94);
          }
          .ov-sentiment-step-num {
            display: inline-flex;
            align-items: center;
            min-height: 1.32rem;
            padding: 0.12rem 0.42rem;
            border-radius: 999px;
            background: color-mix(in srgb, var(--ov-step-tone, #64748b) 11%, transparent);
            color: var(--ov-step-tone, #64748b);
            font-size: 0.72rem;
            font-weight: 820;
          }
          .ov-sentiment-step-title {
            margin-top: 0.42rem;
            color: #111827;
            font-size: 0.98rem;
            line-height: 1.25;
            font-weight: 800;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-step-status {
            margin-top: 0.34rem;
            color: #111827;
            font-size: 0.82rem;
            line-height: 1.2;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-step-detail {
            margin-top: 0.34rem;
            color: #334155;
            font-size: 0.8rem;
            line-height: 1.45;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-driver {
            min-height: 92px;
            padding: 0.62rem 0.7rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-left: 3px solid var(--ov-driver-tone, #64748b);
            border-radius: 8px;
            background: rgba(255,255,255,0.92);
          }
          .ov-sentiment-driver-title {
            color: #111827;
            font-size: 0.82rem;
            line-height: 1.25;
            font-weight: 780;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-driver-detail {
            margin-top: 0.22rem;
            color: #334155;
            font-size: 0.75rem;
            line-height: 1.32;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning {
            min-height: 184px;
            padding: 0.78rem 0.82rem;
            border: 1px solid rgba(100, 116, 139, 0.16);
            border-top: 4px solid var(--ov-learning-tone, #64748b);
            border-radius: 8px;
            background: rgba(255,255,255,0.94);
          }
          .ov-sentiment-learning-title {
            color: #111827;
            font-size: 0.92rem;
            line-height: 1.25;
            font-weight: 820;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning-score {
            margin-top: 0.3rem;
            color: var(--ov-learning-tone, #64748b);
            font-size: 0.82rem;
            line-height: 1.24;
            font-weight: 800;
          }
          .ov-sentiment-learning-body {
            margin-top: 0.34rem;
            color: #334155;
            font-size: 0.76rem;
            line-height: 1.38;
            overflow-wrap: anywhere;
          }
          .ov-sentiment-learning-body strong {
            color: #111827;
            font-weight: 780;
          }
        </style>
        """,
        unsafe_allow_html=True,
    )
    tone_color = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
        "neutral": OVERVIEW_COLOR_NEUTRAL,
    }.get(tone, OVERVIEW_COLOR_NEUTRAL)
    st.markdown(
        f"""
        <section class="ov-sentiment-brief" style="--ov-sentiment-tone:{tone_color};">
          <div class="ov-sentiment-eyebrow">시장 심리 컨텍스트</div>
          <div class="ov-sentiment-headline">{headline}</div>
          <div class="ov-sentiment-summary">{summary}</div>
          <div class="ov-sentiment-meta">
            <span class="ov-sentiment-pill">{phase_label}</span>
            <span class="ov-sentiment-pill">데이터 신뢰도: {confidence_status}</span>
            <span class="ov-sentiment-pill">{confidence_detail}</span>
          </div>
        </section>
        """,
        unsafe_allow_html=True,
    )


def _render_sentiment_analysis_steps(analysis: dict[str, Any]) -> None:
    steps = list(analysis.get("analysis_steps") or [])
    if not steps:
        return
    html_steps: list[str] = []
    for index, step in enumerate(steps, start=1):
        tone = _sentiment_tone(step.get("tone") or "neutral")
        tone_color = {
            "positive": OVERVIEW_COLOR_POSITIVE,
            "warning": OVERVIEW_COLOR_WARNING,
            "danger": OVERVIEW_COLOR_DANGER,
            "neutral": OVERVIEW_COLOR_NEUTRAL,
        }.get(tone, OVERVIEW_COLOR_NEUTRAL)
        html_steps.append(
            f'<div class="ov-sentiment-step" style="--ov-step-tone:{tone_color};">'
            f'<div class="ov-sentiment-step-num">STEP {index}</div>'
            f'<div class="ov-sentiment-step-title">{escape(str(step.get("title") or "-"))}</div>'
            f'<div class="ov-sentiment-step-status">{escape(str(step.get("status") or "-"))}</div>'
            f'<div class="ov-sentiment-step-detail">{escape(str(step.get("detail") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### 시장 심리 읽기 - 6단계")
    st.markdown(f'<div class="ov-sentiment-step-grid">{"".join(html_steps)}</div>', unsafe_allow_html=True)


def _render_sentiment_driver_groups(analysis: dict[str, Any]) -> None:
    groups = dict(analysis.get("driver_groups") or {})
    labels = [
        ("greed", "탐욕 드라이버", OVERVIEW_COLOR_POSITIVE),
        ("fear", "공포 드라이버", OVERVIEW_COLOR_WARNING),
        ("neutral", "중립 드라이버", OVERVIEW_COLOR_NEUTRAL),
    ]
    html_cards: list[str] = []
    for key, title, color in labels:
        rows = list(groups.get(key) or [])
        if rows:
            detail = " / ".join(
                f"{row.get('label_ko') or row.get('series')}: {row.get('score')} ({row.get('rating_label_ko') or row.get('rating')})"
                for row in rows[:4]
            )
        else:
            detail = "이 구간의 활성 드라이버가 없습니다."
        html_cards.append(
            f'<div class="ov-sentiment-driver" style="--ov-driver-tone:{color};">'
            f'<div class="ov-sentiment-driver-title">{escape(title)} · {len(rows)}</div>'
            f'<div class="ov-sentiment-driver-detail">{escape(detail)}</div>'
            "</div>"
        )
    st.markdown("#### 드라이버 분해")
    st.markdown(f'<div class="ov-sentiment-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_sentiment_component_learning_cards(analysis: dict[str, Any]) -> None:
    explanations = list(analysis.get("component_explanations") or [])
    if not explanations:
        return
    tone_colors = {
        "positive": OVERVIEW_COLOR_POSITIVE,
        "warning": OVERVIEW_COLOR_WARNING,
        "danger": OVERVIEW_COLOR_DANGER,
        "neutral": OVERVIEW_COLOR_NEUTRAL,
    }
    html_cards: list[str] = []
    for item in explanations:
        tone_color = tone_colors.get(_sentiment_tone(item.get("tone") or "neutral"), OVERVIEW_COLOR_NEUTRAL)
        score = "-" if item.get("score") is None else f"{float(item.get('score')):.1f}"
        title = f"{item.get('label_ko') or '-'} · {item.get('series') or '-'}"
        html_cards.append(
            f'<div class="ov-sentiment-learning" style="--ov-learning-tone:{tone_color};">'
            f'<div class="ov-sentiment-learning-title">{escape(str(title))}</div>'
            f'<div class="ov-sentiment-learning-score">현재 {score} · {escape(str(item.get("rating_label_ko") or item.get("rating") or "-"))}</div>'
            f'<div class="ov-sentiment-learning-body"><strong>보는 것</strong><br>{escape(str(item.get("what_it_checks") or ""))}</div>'
            f'<div class="ov-sentiment-learning-body"><strong>현재 읽기</strong><br>{escape(str(item.get("current_reading") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### CNN 구성요소 학습 노트")
    st.markdown(f'<div class="ov-sentiment-step-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _render_sentiment_next_checks(analysis: dict[str, Any]) -> None:
    checks = list(analysis.get("next_checks") or [])
    if not checks:
        return
    html_cards: list[str] = []
    for check in checks:
        html_cards.append(
            f'<div class="ov-sentiment-driver" style="--ov-driver-tone:{OVERVIEW_COLOR_PRIMARY};">'
            f'<div class="ov-sentiment-driver-title">{escape(str(check.get("target") or "-"))}</div>'
            f'<div class="ov-sentiment-driver-detail"><strong>왜</strong> {escape(str(check.get("reason") or ""))}</div>'
            f'<div class="ov-sentiment-driver-detail"><strong>볼 것</strong> {escape(str(check.get("watch_for") or ""))}</div>'
            "</div>"
        )
    st.markdown("#### 다음 확인")
    st.markdown(f'<div class="ov-sentiment-grid">{"".join(html_cards)}</div>', unsafe_allow_html=True)


def _sentiment_status_cards(
    snapshot: dict[str, Any],
    coverage: dict[str, Any],
    analysis: dict[str, Any],
) -> list[dict[str, Any]]:
    return [
        {
            "title": "데이터 신뢰도",
            "value": dict(analysis.get("data_confidence") or {}).get("status") or snapshot.get("status") or "-",
            "detail": f"{coverage.get('missing_count') or 0} missing · {coverage.get('stale_count') or 0} stale",
            "tone": _sentiment_tone(
                dict(analysis.get("data_confidence") or {}).get("tone") or snapshot.get("status")
            ),
        },
        {
            "title": "CNN Fear & Greed",
            "value": "-" if coverage.get("cnn_score") is None else f"{float(coverage['cnn_score']):.1f}",
            "detail": str(coverage.get("cnn_rating") or "-"),
            "tone": "positive"
            if _safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) >= 55
            else "warning"
            if _safe_float(coverage.get("cnn_score")) is not None and float(coverage["cnn_score"]) < 45
            else "neutral",
        },
        {
            "title": "AAII Bearish",
            "value": "-" if coverage.get("aaii_bearish") is None else f"{float(coverage['aaii_bearish']):.1f}%",
            "detail": "weekly bearish sentiment",
            "tone": "warning"
            if _safe_float(coverage.get("aaii_bearish")) is not None
            and float(coverage["aaii_bearish"]) >= 40
            else "neutral",
        },
        {
            "title": "Bull-Bear Spread",
            "value": "-"
            if coverage.get("aaii_bull_bear_spread") is None
            else f"{float(coverage['aaii_bull_bear_spread']):+.1f} pp",
            "detail": "AAII bullish minus bearish",
            "tone": "positive"
            if _safe_float(coverage.get("aaii_bull_bear_spread")) is not None
            and float(coverage["aaii_bull_bear_spread"]) > 0
            else "warning"
            if _safe_float(coverage.get("aaii_bull_bear_spread")) is not None
            else "neutral",
        },
    ]


def render_sentiment_snapshot_overview(snapshot: dict[str, Any]) -> None:
    coverage = dict(snapshot.get("coverage") or {})
    analysis = dict(snapshot.get("analysis") or {})
    _render_sentiment_analysis_panel(analysis)
    _render_sentiment_analysis_steps(analysis)
    render_status_card_grid(_sentiment_status_cards(snapshot, coverage, analysis))
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))


def has_sentiment_rows(snapshot: dict[str, Any]) -> bool:
    rows = snapshot.get("rows")
    return isinstance(rows, pd.DataFrame) and not rows.empty


def render_sentiment_empty_state() -> None:
    st.info("Stored sentiment rows are not available yet. Run Market Sentiment refresh first.")


def render_sentiment_detail_sections(snapshot: dict[str, Any]) -> None:
    analysis = dict(snapshot.get("analysis") or {})
    rows = snapshot.get("rows")
    component_rows = snapshot.get("component_rows")
    history_rows = snapshot.get("history_rows")

    _render_sentiment_driver_groups(analysis)
    _render_sentiment_component_learning_cards(analysis)
    _render_sentiment_next_checks(analysis)

    trend_tab, components_tab, table_tab = st.tabs(["추세 근거", "CNN 구성 상세", "원천 테이블"])
    with trend_tab:
        st.altair_chart(
            _sentiment_trend_chart(
                history_rows if isinstance(history_rows, pd.DataFrame) else pd.DataFrame()
            ),
            width="stretch",
        )
    with components_tab:
        st.altair_chart(
            _sentiment_component_chart(
                component_rows if isinstance(component_rows, pd.DataFrame) else pd.DataFrame()
            ),
            width="stretch",
        )
        if isinstance(component_rows, pd.DataFrame) and not component_rows.empty:
            st.dataframe(component_rows, width="stretch", hide_index=True)
    with table_tab:
        st.dataframe(rows, width="stretch", hide_index=True)
