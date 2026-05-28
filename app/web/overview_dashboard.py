from __future__ import annotations

from datetime import datetime
from html import escape
from typing import Any, Callable

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.ingestion_jobs import run_collect_sp500_intraday_snapshot, run_collect_sp500_universe
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.overview_dashboard_helpers import (
    load_overview_dashboard_snapshot,
    load_overview_group_leadership_snapshot,
    load_overview_market_mover_sectors,
    load_overview_market_movers_snapshot,
)


SP500_INTRADAY_REFRESH_MINUTES = 5


# Render one ranked candidate card in the Overview priority section.
def _render_priority_candidate_card(candidate: dict[str, Any], rank: int) -> None:
    cagr = candidate.get("cagr")
    mdd = candidate.get("mdd")
    cagr_text = f"{float(cagr):.2f}%" if cagr is not None else "-"
    mdd_text = f"{float(mdd):.2f}%" if mdd is not None else "-"
    st.markdown(f"##### #{rank} {candidate.get('title') or '-'}")
    render_badge_strip(
        [
            {"label": "Score", "value": f"{candidate.get('score')} / 10", "tone": "positive"},
            {"label": "Family", "value": candidate.get("family") or "-", "tone": "neutral"},
            {"label": "Pre-Live", "value": candidate.get("pre_live_status") or "-", "tone": "positive"},
        ]
    )
    render_status_card_grid(
        [
            {"title": "CAGR", "value": cagr_text, "tone": "positive"},
            {"title": "MDD", "value": mdd_text, "tone": "warning"},
            {"title": "Promotion", "value": candidate.get("promotion") or "-", "tone": "neutral"},
        ]
    )
    st.caption(str(candidate.get("next_action") or ""))


# Build an Altair donut chart for the candidate/proposal funnel.
def _build_funnel_chart(funnel_rows: pd.DataFrame) -> alt.Chart:
    chart_rows = funnel_rows.copy()
    if chart_rows.empty or int(chart_rows["Count"].sum()) <= 0:
        chart_rows = pd.DataFrame([{"Stage": "No Data", "Count": 1}])
    return (
        alt.Chart(chart_rows)
        .mark_arc(innerRadius=58, outerRadius=96, stroke="#ffffff")
        .encode(
            theta=alt.Theta("Count:Q", stack=True),
            color=alt.Color(
                "Stage:N",
                scale=alt.Scale(
                    range=["#0f766e", "#2563eb", "#b45309", "#64748b", "#cbd5e1"]
                ),
                legend=alt.Legend(title=None, orient="bottom"),
            ),
            tooltip=["Stage:N", "Count:Q"],
        )
        .properties(height=260)
    )


# Render the next-action list as compact operator cards.
def _render_next_actions(actions: list[dict[str, Any]]) -> None:
    for action in actions:
        priority = str(action.get("priority") or "Low")
        tone = "danger" if priority == "High" else "warning" if priority == "Medium" else "neutral"
        with st.container(border=True):
            render_badge_strip(
                [
                    {"label": "Priority", "value": priority, "tone": tone},
                    {"label": "Target", "value": action.get("target") or "-", "tone": "neutral"},
                ]
            )
            st.markdown(f"**{escape(str(action.get('title') or '-'))}**")
            st.caption(str(action.get("detail") or ""))


# Return a compact display value for market-intelligence snapshot metadata.
def _snapshot_value(value: Any) -> str:
    if value in (None, ""):
        return "-"
    return str(value)


def _render_snapshot_status_cards(snapshot: dict[str, Any]) -> None:
    coverage = dict(snapshot.get("coverage") or {})
    stale_days = coverage.get("stale_days")
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is not None:
        age_value = f"{int(stale_minutes)}m"
        age_detail = "from intraday snapshot"
        age_tone = "positive" if int(stale_minutes) <= 10 else "warning"
    else:
        age_value = _snapshot_value(stale_days)
        age_detail = "calendar days from effective date"
        age_tone = "positive" if stale_days is not None and int(stale_days) <= 3 else "warning"
    returnable = coverage.get("returnable_count") or 0
    universe_count = coverage.get("universe_count") or 0
    coverage_text = f"{returnable} / {universe_count}" if universe_count else "-"
    effective_value = coverage.get("snapshot_time_utc") or coverage.get("effective_end_date")
    raw_detail = coverage.get("price_mode") or f"raw latest: {_snapshot_value(coverage.get('latest_raw_date'))}"
    render_status_card_grid(
        [
            {
                "title": "Effective Price Time",
                "value": _snapshot_value(effective_value),
                "detail": raw_detail,
                "tone": "positive" if effective_value else "warning",
            },
            {
                "title": "Returnable Coverage",
                "value": coverage_text,
                "detail": f"missing: {coverage.get('missing_count') or 0}",
                "tone": "positive" if returnable else "warning",
            },
            {
                "title": "Snapshot Age",
                "value": age_value,
                "detail": age_detail,
                "tone": age_tone,
            },
            {
                "title": "Snapshot Status",
                "value": snapshot.get("status") or "-",
                "detail": coverage.get("coverage_basis") or snapshot.get("universe_label") or "-",
                "tone": "positive" if snapshot.get("status") == "OK" else "warning",
            },
        ]
    )


def _render_snapshot_warnings(snapshot: dict[str, Any]) -> None:
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))


def _build_return_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Symbol": "No Data", "Return %": 0.0}])
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X("Return %:Q", title="Return %"),
            y=alt.Y("Symbol:N", sort="-x", title=None),
            color=alt.Color(
                "Return %:Q",
                scale=alt.Scale(range=["#d97706", "#0f766e"]),
                legend=None,
            ),
            tooltip=["Rank:O", "Symbol:N", "Name:N", "Return %:Q", "Sector:N", "Industry:N"],
        )
        .properties(height=max(220, min(520, 28 * len(chart_rows))))
    )


def _render_missing_diagnostics(snapshot: dict[str, Any]) -> None:
    missing_rows = snapshot.get("missing_rows")
    if not isinstance(missing_rows, pd.DataFrame) or missing_rows.empty:
        return
    with st.expander(f"Coverage Diagnostics ({len(missing_rows)} missing)", expanded=False):
        st.dataframe(missing_rows, width="stretch", hide_index=True)


def _render_sp500_job_result(result_key: str) -> None:
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
            f"Processed: {result.get('symbols_processed') or 0} / {result.get('symbols_requested') or 0}, "
            f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
        )


def _is_sp500_daily_refresh_due(snapshot: dict[str, Any], *, universe_code: str, period: str) -> bool:
    if universe_code != "SP500" or period != "daily":
        return False
    coverage = dict(snapshot.get("coverage") or {})
    if coverage.get("price_mode") != "Intraday Snapshot":
        return True
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is None:
        return True
    return int(stale_minutes) >= SP500_INTRADAY_REFRESH_MINUTES


def _render_refresh_state_dot(*, color: str, label: str, detail: str) -> None:
    st.markdown(
        f"""
        <div style="
            display:flex;
            align-items:center;
            gap:10px;
            min-height:38px;
            padding:7px 10px;
            border:1px solid #e5e7eb;
            border-radius:8px;
            background:#ffffff;">
            <span style="
                width:10px;
                height:10px;
                border-radius:999px;
                background:{color};
                box-shadow:0 0 0 3px color-mix(in srgb, {color} 18%, transparent);"></span>
            <span style="font-weight:600;color:#111827;">{escape(label)}</span>
            <span style="color:#64748b;font-size:0.875rem;">{escape(detail)}</span>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _render_market_movers_refresh_bar(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> None:
    is_sp500_daily = universe_code == "SP500" and period == "daily"
    if not is_sp500_daily:
        return

    coverage = dict(snapshot.get("coverage") or {})
    price_mode = str(coverage.get("price_mode") or "")
    stale_minutes = coverage.get("snapshot_stale_minutes")
    refresh_due = _is_sp500_daily_refresh_due(snapshot, universe_code=universe_code, period=period)
    if price_mode != "Intraday Snapshot":
        dot_color = "#dc2626"
        label = "Update needed"
        detail = "using EOD fallback"
    elif refresh_due:
        dot_color = "#dc2626"
        label = "Update needed"
        detail = f"{int(stale_minutes or 0)}m old"
    else:
        dot_color = "#0f766e"
        label = "Fresh"
        detail = f"{int(stale_minutes or 0)}m old"

    with st.container(border=True):
        cols = st.columns([1.25, 1, 1, 1.1], gap="small", vertical_alignment="center")
        with cols[0]:
            _render_refresh_state_dot(color=dot_color, label=label, detail=detail)
        update_label = "Update Daily Snapshot" if refresh_due else "Snapshot Fresh"
        if cols[1].button(
            update_label,
            key="overview_sp500_intraday_refresh",
            use_container_width=True,
            disabled=not refresh_due,
        ):
            with st.spinner("Updating S&P 500 quote snapshot..."):
                st.session_state["overview_sp500_intraday_result"] = run_collect_sp500_intraday_snapshot(
                    interval="5m",
                    chunk_size=100,
                    quote_batch_size=200,
                    method="quote_fast",
                    fallback_to_yfinance=True,
                )
            st.rerun()
        if cols[2].button(
            "Refresh Universe",
            key="overview_sp500_universe_refresh",
            use_container_width=True,
        ):
            with st.spinner("Refreshing S&P 500 universe..."):
                st.session_state["overview_sp500_universe_result"] = run_collect_sp500_universe()
            st.rerun()
        if cols[3].button(
            "Reload View",
            key="overview_market_movers_reload",
            use_container_width=True,
        ):
            st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()

    _render_sp500_job_result("overview_sp500_universe_result")
    _render_sp500_job_result("overview_sp500_intraday_result")


def _render_market_movers_snapshot_panel(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    sector: str,
) -> None:
    snapshot = load_overview_market_movers_snapshot(
        universe_limit=universe_limit,
        universe_code=universe_code,
        period=period,
        top_n=top_n,
        sector=None if sector == "All" else sector,
    )
    _render_market_movers_refresh_bar(snapshot, universe_code=universe_code, period=period)
    _render_snapshot_status_cards(snapshot)
    _render_snapshot_warnings(snapshot)
    _render_missing_diagnostics(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed market mover rows are not available for the selected controls.")
        return

    left, right = st.columns([0.95, 1.25], gap="medium")
    with left:
        st.altair_chart(_build_return_bar_chart(rows), width="stretch")
    with right:
        st.dataframe(rows, width="stretch", hide_index=True)


def _render_market_movers_tab() -> None:
    st.markdown("### Market Movers")
    with st.container(border=True):
        controls = st.columns([1.1, 1.2, 1.1, 0.8, 0.9], gap="small", vertical_alignment="bottom")
        coverage = str(
            controls[0].segmented_control(
                "Coverage",
                ["SP500", "TOP1000", "TOP2000"],
                default="SP500",
                format_func=lambda value: {
                    "SP500": "S&P 500",
                    "TOP1000": "Top 1000",
                    "TOP2000": "Top 2000",
                }[value],
                key="overview_market_movers_coverage",
            )
        )
        universe_limit = {"SP500": 500, "TOP1000": 1000, "TOP2000": 2000}[coverage]
        period = str(
            controls[1].segmented_control(
                "Period",
                ["daily", "weekly", "monthly", "yearly"],
                default="daily",
                format_func=lambda value: {
                    "daily": "Daily",
                    "weekly": "Weekly",
                    "monthly": "Monthly",
                    "yearly": "Yearly",
                }[value],
                key="overview_market_movers_period",
            )
        )
        sector_options = ["All"] + load_overview_market_mover_sectors(
            universe_code=coverage,
            universe_limit=universe_limit,
        )
        sector = str(
            controls[2].selectbox(
                "Sector",
                sector_options,
                index=0,
                key="overview_market_movers_sector",
            )
        )
        top_n = int(
            controls[3].number_input(
                "Top N",
                min_value=5,
                max_value=100,
                value=20,
                step=5,
                key="overview_market_movers_top_n",
            )
        )
        refresh_mode = str(
            controls[4].selectbox(
                "Status Check",
                ["1 min", "5 min", "10 min"],
                index=0,
                key="overview_market_movers_status_check",
                disabled=coverage != "SP500" or period != "daily",
            )
        )

    reloaded_at = st.session_state.get("overview_market_movers_reloaded_at")
    if reloaded_at:
        st.caption(f"Last DB snapshot reload request: {reloaded_at}")
    if coverage == "SP500" and period == "daily":
        st.caption("Daily S&P 500 uses the latest stored intraday snapshot versus previous close when available.")

    refresh_seconds = {"1 min": 60, "5 min": 300, "10 min": 600}.get(refresh_mode)
    if coverage != "SP500" or period != "daily":
        refresh_seconds = None
    if refresh_seconds:
        @st.fragment(run_every=refresh_seconds)
        def _auto_refresh_panel() -> None:
            _render_market_movers_snapshot_panel(
                universe_code=coverage,
                universe_limit=universe_limit,
                period=period,
                top_n=top_n,
                sector=sector,
            )

        _auto_refresh_panel()
    else:
        _render_market_movers_snapshot_panel(
            universe_code=coverage,
            universe_limit=universe_limit,
            period=period,
            top_n=top_n,
            sector=sector,
        )


def _render_sector_industry_tab() -> None:
    st.markdown("### Sector / Industry Leadership")
    controls = st.columns([1, 1.1, 1, 1], gap="small")
    universe_limit = int(
        controls[0].selectbox(
            "Coverage",
            [1000, 2000],
            index=1,
            key="overview_group_leadership_coverage",
        )
    )
    group_by = str(
        controls[1].radio(
            "Group",
            ["sector", "industry"],
            index=0,
            horizontal=True,
            format_func=lambda value: {"sector": "Sector", "industry": "Industry"}[value],
            key="overview_group_leadership_group",
        )
    )
    top_n = int(
        controls[2].number_input(
            "Top N",
            min_value=5,
            max_value=100,
            value=10,
            step=5,
            key="overview_group_leadership_top_n",
        )
    )
    min_group_size = int(
        controls[3].number_input(
            "Min Symbols",
            min_value=1,
            max_value=50,
            value=5,
            step=1,
            key="overview_group_leadership_min_symbols",
        )
    )

    snapshot = load_overview_group_leadership_snapshot(
        universe_limit=universe_limit,
        group_by=group_by,
        top_n=top_n,
        min_group_size=min_group_size,
    )
    _render_snapshot_status_cards(snapshot)
    _render_snapshot_warnings(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed group leadership rows are not available for the selected controls.")
        return
    st.dataframe(rows, width="stretch", hide_index=True)


def _render_events_tab() -> None:
    st.markdown("### Events")
    render_status_card_grid(
        [
            {
                "title": "FOMC Calendar",
                "value": "Next Slice",
                "detail": "official Fed source, free web parse",
                "tone": "positive",
            },
            {
                "title": "Earnings Calendar",
                "value": "Prototype Later",
                "detail": "free library / parser source label required",
                "tone": "warning",
            },
            {
                "title": "Data Flow",
                "value": "Ingestion First",
                "detail": "store before Overview display",
                "tone": "neutral",
            },
        ]
    )
    cols = st.columns([1, 1, 2], gap="small")
    cols[0].button("Refresh FOMC Calendar", key="overview_events_refresh_fomc_disabled", disabled=True)
    cols[1].button("Refresh Earnings Calendar", key="overview_events_refresh_earnings_disabled", disabled=True)
    cols[2].caption("Calendar collectors are intentionally separated from the first DB-backed market scan slice.")


def _render_candidate_ops_tab(
    *,
    snapshot: dict[str, Any],
    latest_result: dict[str, Any] | None,
    recent_results: list[dict[str, Any]],
    runtime_marker: str,
    loaded_at: datetime,
    git_sha: str | None,
    render_runtime_snapshot: Callable[[], None] | None,
) -> None:
    kpis = dict(snapshot["kpis"])

    render_status_card_grid(
        [
            {
                "title": "Current Candidates",
                "value": kpis["current_candidates"],
                "detail": "registry에 남은 활성 후보",
                "tone": "positive" if kpis["current_candidates"] else "neutral",
            },
            {
                "title": "Paper Tracking",
                "value": kpis["paper_tracking"],
                "detail": "실전 전 관찰 중",
                "tone": "positive" if kpis["paper_tracking"] else "neutral",
            },
            {
                "title": "Proposal Drafts",
                "value": kpis["proposal_drafts"],
                "detail": "저장된 구성 초안",
                "tone": "positive" if kpis["proposal_drafts"] else "neutral",
            },
            {
                "title": "Recent Runs",
                "value": kpis["recent_runs"],
                "detail": "persistent backtest history",
                "tone": "positive" if kpis["recent_runs"] else "warning",
            },
        ]
    )

    st.markdown("### 검토 우선 후보 Top 3")
    st.caption("성과 순위가 아니라 Real-Money 신호, Pre-Live 상태, 배포 blocker, CAGR/MDD를 함께 본 운영 검토 우선순위입니다.")
    top_candidates = list(snapshot["top_candidates"])
    if top_candidates:
        candidate_cols = st.columns(len(top_candidates), gap="small")
        for index, candidate in enumerate(top_candidates, start=1):
            with candidate_cols[index - 1].container(border=True):
                _render_priority_candidate_card(candidate, index)
    else:
        st.info("아직 Overview에 표시할 current candidate가 없습니다.")

    left, right = st.columns([1.05, 1.15], gap="medium")
    with left:
        st.markdown("### Candidate Funnel")
        st.caption("현재 후보가 어느 운영 단계에 쌓여 있는지 한눈에 봅니다.")
        st.altair_chart(_build_funnel_chart(snapshot["funnel_rows"]), width="stretch")
        st.dataframe(snapshot["funnel_rows"], width="stretch", hide_index=True)

    with right:
        st.markdown("### Next Actions")
        st.caption("다음에 눌러야 할 탭을 설명하는 운영 체크리스트입니다.")
        _render_next_actions(list(snapshot["next_actions"]))

    st.markdown("### Recent Activity")
    st.caption("최근 candidate, pre-live, proposal, backtest history 이벤트를 한 줄 피드로 확인합니다.")
    activity_rows = snapshot["activity_rows"]
    if activity_rows.empty:
        st.info("표시할 최근 활동이 없습니다.")
    else:
        st.dataframe(activity_rows, width="stretch", hide_index=True)

    latest_status = str((latest_result or {}).get("status") or "").upper()
    if latest_result:
        with st.expander("Session Latest Completed Run", expanded=False):
            label = str(latest_result.get("label") or latest_result.get("job_name") or "latest_run")
            run_time = latest_result.get("finished_at") or latest_result.get("started_at") or "-"
            render_status_card_grid(
                [
                    {"title": "Label", "value": label, "tone": "neutral"},
                    {"title": "Status", "value": latest_status or "-", "tone": "positive" if latest_status == "SUCCESS" else "warning"},
                    {"title": "Finished At", "value": str(run_time), "tone": "neutral"},
                ]
            )
    elif not snapshot["history_rows"] and not recent_results:
        st.info("아직 완료된 실행 기록이 없습니다. 먼저 `Ingestion`이나 `Backtest`에서 작업을 실행하면 Overview에도 요약이 보입니다.")

    with st.expander("System Snapshot", expanded=False):
        if render_runtime_snapshot:
            render_runtime_snapshot()
        else:
            render_status_card_grid(
                [
                    {"title": "Runtime Marker", "value": runtime_marker, "tone": "neutral"},
                    {"title": "Loaded At", "value": loaded_at.strftime("%Y-%m-%d %H:%M:%S"), "tone": "neutral"},
                    {"title": "Git SHA", "value": git_sha or "unknown", "tone": "neutral"},
                ]
            )


# Render the top-level product dashboard for Workspace > Overview.
def render_overview_dashboard(
    *,
    runtime_marker: str,
    loaded_at: datetime,
    git_sha: str | None,
    latest_result: dict[str, Any] | None = None,
    recent_results: list[dict[str, Any]] | None = None,
    render_runtime_snapshot: Callable[[], None] | None = None,
) -> None:
    snapshot = load_overview_dashboard_snapshot()
    recent_results = recent_results or []

    st.title("Finance Console")
    st.caption("시장 스캔, 후보 운영, Portfolio Proposal, 다음 행동을 한 화면에서 읽는 퀀트 워크벤치 대시보드입니다.")

    market_tab, group_tab, events_tab, candidate_tab = st.tabs(
        ["Market Movers", "Sector / Industry", "Events", "Candidate Ops"]
    )
    with market_tab:
        _render_market_movers_tab()
    with group_tab:
        _render_sector_industry_tab()
    with events_tab:
        _render_events_tab()
    with candidate_tab:
        _render_candidate_ops_tab(
            snapshot=snapshot,
            latest_result=latest_result,
            recent_results=recent_results,
            runtime_marker=runtime_marker,
            loaded_at=loaded_at,
            git_sha=git_sha,
            render_runtime_snapshot=render_runtime_snapshot,
        )
