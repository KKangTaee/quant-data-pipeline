from __future__ import annotations

from datetime import datetime
from html import escape
from inspect import signature
from typing import Any, Callable

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.ingestion_jobs import (
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_market_intraday_snapshot,
    run_collect_sp500_universe,
)
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.overview_dashboard_helpers import (
    load_overview_dashboard_snapshot,
    load_overview_group_leadership_snapshot,
    load_overview_market_events_snapshot,
    load_overview_market_mover_sectors,
    load_overview_market_movers_snapshot,
)


MARKET_INTRADAY_REFRESH_MINUTES = 5
MARKET_COVERAGE_LABELS = {
    "SP500": "S&P 500",
    "TOP1000": "Top 1000",
    "TOP2000": "Top 2000",
}


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
    total_count = max(1, int(chart_rows["Count"].sum()))
    return (
        alt.Chart(chart_rows)
        .mark_arc(innerRadius=58, outerRadius=96, stroke="#ffffff")
        .encode(
            theta=alt.Theta("Count:Q", stack=True, scale=alt.Scale(domain=[0, total_count])),
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
    refresh_state = dict(coverage.get("refresh_state") or {})
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
    missing_count = coverage.get("missing_count") or 0
    failed_count = coverage.get("failed_count") or missing_count
    effective_value = coverage.get("snapshot_time_utc") or coverage.get("effective_end_date")
    raw_detail = coverage.get("price_mode") or f"raw latest: {_snapshot_value(coverage.get('latest_raw_date'))}"
    status_title = "Refresh State" if refresh_state else "Snapshot Status"
    status_value = refresh_state.get("label") or snapshot.get("status") or "-"
    status_detail = refresh_state.get("detail") or coverage.get("coverage_basis") or snapshot.get("universe_label") or "-"
    status_tone = refresh_state.get("tone") or ("positive" if snapshot.get("status") == "OK" else "warning")
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
                "detail": f"missing: {missing_count}, failed: {failed_count}",
                "tone": "positive" if returnable else "warning",
            },
            {
                "title": "Snapshot Age",
                "value": age_value,
                "detail": age_detail,
                "tone": age_tone,
            },
            {
                "title": status_title,
                "value": status_value,
                "detail": status_detail,
                "tone": status_tone,
            },
        ]
    )


def _render_snapshot_warnings(snapshot: dict[str, Any]) -> None:
    for warning in snapshot.get("warnings") or []:
        st.warning(str(warning))


def _symmetric_return_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_abs = max(1.0, float(numeric.abs().max()) if not numeric.empty else 1.0)
    return [-max_abs, 0, max_abs]


def _symmetric_return_scale(values: pd.Series) -> alt.Scale:
    return alt.Scale(domain=_symmetric_return_domain(values), range=["#b91c1c", "#f8fafc", "#0f766e"])


def _build_return_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    if not chart_rows.empty and "Return %" in chart_rows:
        chart_rows["Return %"] = pd.to_numeric(chart_rows["Return %"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Return %"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Symbol": "No Data", "Return %": 0.0}])
    chart_rows["Return Label"] = chart_rows["Return %"].map(lambda value: f"{float(value):.2f}%" if pd.notna(value) else "-")
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X(
                "Return %:Q",
                title="Return %",
                stack=None,
                scale=alt.Scale(domain=_symmetric_return_domain(chart_rows["Return %"])),
            ),
            y=alt.Y("Symbol:N", sort="-x", title=None, axis=alt.Axis(labelLimit=80)),
            color=alt.Color(
                "Return %:Q",
                scale=_symmetric_return_scale(chart_rows["Return %"]),
                legend=None,
            ),
            tooltip=["Rank:O", "Symbol:N", "Name:N", "Return Label:N", "Sector:N", "Industry:N"],
        )
        .properties(height=max(220, min(520, 28 * len(chart_rows))))
    )


def _build_market_mover_sector_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty or "Sector" not in rows or "Return %" not in rows:
        chart_rows = pd.DataFrame([{"Sector": "No Data", "Average Return %": 0.0, "Count": 0, "Top Return %": 0.0}])
    else:
        chart_rows = (
            rows.assign(
                Sector=rows["Sector"].fillna("Unknown"),
                **{"Return %": pd.to_numeric(rows["Return %"], errors="coerce")},
            )
            .dropna(subset=["Return %"])
            .groupby("Sector", as_index=False)
            .agg(
                **{
                    "Average Return %": ("Return %", "mean"),
                    "Top Return %": ("Return %", "max"),
                    "Count": ("Symbol", "count"),
                }
            )
            .sort_values(["Average Return %", "Top Return %"], ascending=[False, False])
            .head(12)
        )
        if chart_rows.empty:
            chart_rows = pd.DataFrame([{"Sector": "No Data", "Average Return %": 0.0, "Count": 0, "Top Return %": 0.0}])
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            x=alt.X(
                "Average Return %:Q",
                title="Avg Return %",
                stack=None,
                scale=alt.Scale(domain=_symmetric_return_domain(chart_rows["Average Return %"])),
            ),
            y=alt.Y("Sector:N", sort="-x", title=None, axis=alt.Axis(labelLimit=150)),
            color=alt.Color(
                "Average Return %:Q",
                scale=_symmetric_return_scale(chart_rows["Average Return %"]),
                legend=None,
            ),
            tooltip=["Sector:N", "Count:Q", "Average Return %:Q", "Top Return %:Q"],
        )
        .properties(height=max(180, min(360, 26 * len(chart_rows))))
    )


def _build_group_leadership_heatmap(rows: pd.DataFrame) -> alt.Chart:
    metric_columns = [
        "Equal Weight Return %",
        "Market Cap Weighted Return %",
        "Top Symbol Return %",
    ]
    if rows.empty:
        chart_rows = pd.DataFrame(
            [{"Group": "No Data", "Metric": "Equal Weight", "Return %": 0.0, "Symbols": 0, "Top Symbol": "-"}]
        )
    else:
        available_metrics = [column for column in metric_columns if column in rows.columns]
        chart_rows = rows.melt(
            id_vars=[column for column in ["Group", "Symbols", "Top Symbol"] if column in rows.columns],
            value_vars=available_metrics,
            var_name="Metric",
            value_name="Return %",
        )
        chart_rows["Metric"] = chart_rows["Metric"].replace(
            {
                "Equal Weight Return %": "Equal Weight",
                "Market Cap Weighted Return %": "Cap Weighted",
                "Top Symbol Return %": "Top Symbol",
            }
        )
        chart_rows["Return %"] = pd.to_numeric(chart_rows["Return %"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Return %"])
        if chart_rows.empty:
            chart_rows = pd.DataFrame(
                [{"Group": "No Data", "Metric": "Equal Weight", "Return %": 0.0, "Symbols": 0, "Top Symbol": "-"}]
            )
        chart_rows["Return Label"] = chart_rows["Return %"].map(
            lambda value: f"{float(value):.2f}%" if pd.notna(value) else "-"
        )
    group_order = chart_rows["Group"].drop_duplicates().tolist() if "Group" in chart_rows else ["No Data"]
    base = (
        alt.Chart(chart_rows)
        .mark_rect(cornerRadius=2)
        .encode(
            x=alt.X("Metric:N", title=None),
            y=alt.Y("Group:N", sort=group_order, title=None, axis=alt.Axis(labelLimit=190)),
            color=alt.Color(
                "Return %:Q",
                scale=_symmetric_return_scale(chart_rows["Return %"]),
                legend=alt.Legend(title="Return %", orient="bottom"),
            ),
            tooltip=["Group:N", "Metric:N", "Return Label:N", "Symbols:Q", "Top Symbol:N"],
        )
    )
    text = (
        alt.Chart(chart_rows)
        .mark_text(fontSize=11)
        .encode(
            x=alt.X("Metric:N", title=None),
            y=alt.Y("Group:N", sort=group_order, title=None),
            text=alt.Text("Return Label:N"),
            color=alt.condition("datum['Return %'] >= 8 || datum['Return %'] <= -8", alt.value("#ffffff"), alt.value("#111827")),
        )
    )
    return (base + text).properties(height=max(240, min(620, 30 * len(group_order))))


def _render_missing_diagnostics(snapshot: dict[str, Any]) -> None:
    missing_rows = snapshot.get("missing_rows")
    if not isinstance(missing_rows, pd.DataFrame) or missing_rows.empty:
        return
    with st.expander(f"Coverage Diagnostics ({len(missing_rows)} missing)", expanded=False):
        reason_counts = missing_rows["Reason"].value_counts().head(3) if "Reason" in missing_rows else pd.Series()
        if not reason_counts.empty:
            st.caption(
                "Top issues: "
                + ", ".join(f"{reason} ({count})" for reason, count in reason_counts.items())
            )
        st.dataframe(missing_rows, width="stretch", hide_index=True)


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
        if result.get("symbols_requested") is None and result.get("symbols_processed") is None:
            st.caption(
                "Rows: "
                f"{result.get('rows_written') or 0}, "
                f"Events: {details.get('events_found') or '-'}, "
                f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
            )
        else:
            st.caption(
                "Rows: "
                f"{result.get('rows_written') or 0}, "
                f"Processed: {result.get('symbols_processed') or 0} / {result.get('symbols_requested') or 0}, "
                f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
            )
    failed_symbols = result.get("failed_symbols") or []
    if failed_symbols:
        with st.expander(f"Failed / Missing Symbols ({len(failed_symbols)})", expanded=False):
            st.write(", ".join(str(symbol) for symbol in failed_symbols[:100]))


def _is_daily_intraday_refresh_due(snapshot: dict[str, Any], *, period: str) -> bool:
    if period != "daily":
        return False
    coverage = dict(snapshot.get("coverage") or {})
    if coverage.get("price_mode") != "Intraday Snapshot":
        return True
    stale_minutes = coverage.get("snapshot_stale_minutes")
    if stale_minutes is None:
        return True
    return int(stale_minutes) >= MARKET_INTRADAY_REFRESH_MINUTES


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


def _run_collect_market_intraday_snapshot_compat(
    *,
    universe_code: str,
    universe_limit: int,
) -> dict[str, Any]:
    refresh_kwargs: dict[str, Any] = {
        "universe_code": universe_code,
        "universe_limit": universe_limit,
        "interval": "5m",
        "chunk_size": 100,
        "quote_batch_size": 200,
        "method": "quote_fast",
        "fallback_to_yfinance": universe_code == "SP500",
    }
    supported_params = signature(run_collect_market_intraday_snapshot).parameters
    supported_kwargs = {key: value for key, value in refresh_kwargs.items() if key in supported_params}
    return run_collect_market_intraday_snapshot(**supported_kwargs)


def _load_market_movers_snapshot(
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
    top_n: int,
    sector: str,
) -> dict[str, Any]:
    return load_overview_market_movers_snapshot(
        universe_limit=universe_limit,
        universe_code=universe_code,
        period=period,
        top_n=top_n,
        sector=None if sector == "All" else sector,
    )


def _get_market_movers_refresh_state(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> dict[str, str | bool] | None:
    if period != "daily":
        return None

    coverage = dict(snapshot.get("coverage") or {})
    service_state = dict(coverage.get("refresh_state") or {})
    if service_state:
        status = str(service_state.get("status") or "unknown")
        dot_color = {
            "fresh": "#0f766e",
            "partial": "#b45309",
            "due": "#b45309",
            "stale": "#dc2626",
            "failed": "#dc2626",
        }.get(status, "#64748b")
        return {
            "dot_color": dot_color,
            "label": str(service_state.get("label") or status.title()),
            "detail": str(service_state.get("recommended_action") or service_state.get("detail") or ""),
            "refresh_due": bool(service_state.get("refresh_due")),
        }

    price_mode = str(coverage.get("price_mode") or "")
    stale_minutes = coverage.get("snapshot_stale_minutes")
    refresh_due = _is_daily_intraday_refresh_due(snapshot, period=period)
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
    return {
        "dot_color": dot_color,
        "label": label,
        "detail": detail,
        "refresh_due": refresh_due,
    }


def _render_market_movers_refresh_status(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> None:
    state = _get_market_movers_refresh_state(snapshot, universe_code=universe_code, period=period)
    if state is None:
        return

    _render_refresh_state_dot(
        color=str(state["dot_color"]),
        label=str(state["label"]),
        detail=str(state["detail"]),
    )


def _render_market_movers_refresh_bar(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    universe_limit: int,
    period: str,
) -> None:
    if period != "daily":
        return

    universe_label = MARKET_COVERAGE_LABELS.get(universe_code, universe_code)
    intraday_result_key = f"overview_{universe_code.lower()}_intraday_result"
    state = _get_market_movers_refresh_state(snapshot, universe_code=universe_code, period=period)

    with st.container(border=True):
        if state is not None:
            _render_refresh_state_dot(
                color=str(state["dot_color"]),
                label=str(state["label"]),
                detail=str(state["detail"]),
            )
        cols = st.columns([1, 1, 1], gap="small", vertical_alignment="center")
        if cols[0].button(
            "Update Daily Snapshot",
            key=f"overview_{universe_code.lower()}_intraday_refresh",
            use_container_width=True,
            help=str(state.get("detail") or "Collect the latest quote snapshot.") if state else None,
        ):
            with st.spinner(f"Updating {universe_label} quote snapshot..."):
                st.session_state[intraday_result_key] = _run_collect_market_intraday_snapshot_compat(
                    universe_code=universe_code,
                    universe_limit=universe_limit,
                )
            st.rerun()
        if universe_code == "SP500" and cols[1].button(
            "Refresh Universe",
            key="overview_sp500_universe_refresh",
            use_container_width=True,
        ):
            with st.spinner("Refreshing S&P 500 universe..."):
                st.session_state["overview_sp500_universe_result"] = run_collect_sp500_universe()
            st.rerun()
        if universe_code != "SP500":
            cols[1].empty()
        if cols[2].button(
            "Reload View",
            key=f"overview_{universe_code.lower()}_market_movers_reload",
            use_container_width=True,
        ):
            st.session_state["overview_market_movers_reloaded_at"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            st.rerun()

    if universe_code == "SP500":
        _render_market_job_result("overview_sp500_universe_result")
    _render_market_job_result(intraday_result_key)


def _render_market_movers_snapshot_panel(
    snapshot: dict[str, Any],
    *,
    universe_code: str,
    period: str,
) -> None:
    _render_snapshot_status_cards(snapshot)
    _render_snapshot_warnings(snapshot)
    _render_missing_diagnostics(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed market mover rows are not available for the selected controls.")
        return

    left, right = st.columns([0.95, 1.25], gap="medium")
    with left:
        chart_tab, sector_tab = st.tabs(["Rank", "Sector Pulse"])
        with chart_tab:
            st.altair_chart(_build_return_bar_chart(rows), width="stretch")
        with sector_tab:
            st.altair_chart(_build_market_mover_sector_chart(rows), width="stretch")
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
    if period == "daily":
        st.caption("Daily movers use the latest stored quote snapshot versus previous close when available.")

    snapshot = _load_market_movers_snapshot(
        universe_code=coverage,
        universe_limit=universe_limit,
        period=period,
        top_n=top_n,
        sector=sector,
    )
    _render_market_movers_refresh_bar(
        snapshot,
        universe_code=coverage,
        universe_limit=universe_limit,
        period=period,
    )

    refresh_seconds = {"1 min": 60, "5 min": 300, "10 min": 600}.get(refresh_mode)
    if coverage != "SP500" or period != "daily":
        refresh_seconds = None
    if refresh_seconds:
        @st.fragment(run_every=refresh_seconds)
        def _auto_refresh_panel() -> None:
            snapshot = _load_market_movers_snapshot(
                universe_code=coverage,
                universe_limit=universe_limit,
                period=period,
                top_n=top_n,
                sector=sector,
            )
            _render_market_movers_snapshot_panel(
                snapshot,
                universe_code=coverage,
                period=period,
            )

        _auto_refresh_panel()
    else:
        _render_market_movers_snapshot_panel(
            snapshot,
            universe_code=coverage,
            period=period,
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
    heatmap_tab, table_tab = st.tabs(["Heatmap", "Table"])
    with heatmap_tab:
        st.altair_chart(_build_group_leadership_heatmap(rows), width="stretch")
    with table_tab:
        st.dataframe(rows, width="stretch", hide_index=True)


def _event_type_label(value: Any) -> str:
    labels = {
        "FOMC_MEETING": "FOMC",
        "EARNINGS": "Earnings",
        "MACRO": "Macro",
    }
    return labels.get(str(value or ""), str(value or "-").replace("_", " ").title())


def _prepare_event_calendar_frame(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["Date Parsed"] = pd.to_datetime(out.get("Date"), errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    out["Days Until"] = (out["Date Parsed"] - today).dt.days
    out["Month"] = out["Date Parsed"].dt.strftime("%Y-%m")
    out["Week"] = out["Date Parsed"].dt.to_period("W").astype(str)
    out["Type Label"] = out.get("Type", pd.Series(dtype=str)).map(_event_type_label)
    out["Symbol Label"] = out.get("Symbol", pd.Series(dtype=str)).replace({"-": ""})
    out["Summary"] = out.apply(
        lambda row: f"{row.get('Type Label')}: {row.get('Symbol Label') or row.get('Title') or '-'}",
        axis=1,
    )
    return out


def _filter_event_rows_for_calendar(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    filter_cols = st.columns([1, 1, 1], gap="small")
    source_options = ["All"] + sorted(
        value for value in rows.get("Source Type", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    validation_options = ["All"] + sorted(
        value for value in rows.get("Validation", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    window = str(
        filter_cols[0].segmented_control(
            "Window",
            ["30D", "90D", "All"],
            default="90D",
            key="overview_events_window_filter",
        )
    )
    source_filter = str(
        filter_cols[1].selectbox(
            "Source Type",
            source_options,
            index=0,
            key="overview_events_source_filter",
        )
    )
    validation_filter = str(
        filter_cols[2].selectbox(
            "Validation",
            validation_options,
            index=0,
            key="overview_events_validation_filter",
        )
    )

    filtered = rows.copy()
    if window != "All":
        days = 30 if window == "30D" else 90
        filtered = filtered[(filtered["Days Until"].isna()) | ((filtered["Days Until"] >= 0) & (filtered["Days Until"] <= days))]
    if source_filter != "All" and "Source Type" in filtered:
        filtered = filtered[filtered["Source Type"] == source_filter]
    if validation_filter != "All" and "Validation" in filtered:
        filtered = filtered[filtered["Validation"] == validation_filter]
    return filtered


def _build_event_calendar_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        chart_rows = pd.DataFrame(
            [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Event Types": "No Data", "Count": 0}]
        )
    else:
        valid_rows = rows.dropna(subset=["Date Parsed"])
        if valid_rows.empty:
            chart_rows = pd.DataFrame(
                [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Event Types": "No Data", "Count": 0}]
            )
        else:
            chart_rows = (
                valid_rows
                .groupby("Date Parsed", as_index=False)
                .agg(
                    **{
                        "Count": ("Type Label", "size"),
                        "Event Types": ("Type Label", lambda values: ", ".join(sorted(set(values)))),
                    }
                )
            )
    date_min = chart_rows["Date Parsed"].min()
    date_max = chart_rows["Date Parsed"].max()
    if pd.isna(date_min) or pd.isna(date_max):
        date_min = pd.Timestamp(datetime.now().date())
        date_max = date_min + pd.Timedelta(days=1)
    elif date_min == date_max:
        date_max = date_min + pd.Timedelta(days=1)
    max_count = max(1, int(chart_rows["Count"].max() or 0))
    return (
        alt.Chart(chart_rows)
        .mark_line(point=True, color="#2563eb")
        .encode(
            x=alt.X(
                "Date Parsed:T",
                title=None,
                axis=alt.Axis(format="%b %d", labelAngle=-35),
                scale=alt.Scale(domain=[date_min, date_max]),
            ),
            y=alt.Y("Count:Q", title="Events", stack=None, scale=alt.Scale(domain=[0, max_count])),
            tooltip=["Date Parsed:T", "Event Types:N", "Count:Q"],
        )
        .properties(height=240)
    )


def _render_event_date_groups(rows: pd.DataFrame) -> None:
    if rows.empty:
        st.info("No stored event rows match the selected calendar filters.")
        return
    display_columns = [
        column
        for column in ["Type Label", "Symbol", "Title", "Source Type", "Validation", "Freshness", "Age Days"]
        if column in rows.columns
    ]
    for date_value, day_rows in rows.sort_values(["Date Parsed", "Type Label", "Symbol"]).groupby("Date", sort=True):
        day_count = len(day_rows)
        days_until = day_rows["Days Until"].dropna()
        days_text = "-"
        if not days_until.empty:
            day_number = int(days_until.iloc[0])
            days_text = "today" if day_number == 0 else f"{day_number}d"
        type_counts = day_rows["Type Label"].value_counts().to_dict()
        with st.container(border=True):
            header_cols = st.columns([1, 2], gap="small", vertical_alignment="center")
            header_cols[0].markdown(f"##### {date_value}")
            header_cols[1].caption(
                f"{days_text} | {day_count} events | "
                + ", ".join(f"{key}: {value}" for key, value in type_counts.items())
            )
            st.dataframe(day_rows[display_columns], width="stretch", hide_index=True)


def _render_events_tab() -> None:
    st.markdown("### Events")
    with st.container(border=True):
        controls = st.columns([1.1, 1.4, 1.4, 2.1], gap="small", vertical_alignment="bottom")
        event_filter = str(
            controls[0].segmented_control(
                "Type",
                ["ALL", "FOMC_MEETING", "EARNINGS"],
                default="ALL",
                format_func=lambda value: {
                    "ALL": "All",
                    "FOMC_MEETING": "FOMC",
                    "EARNINGS": "Earnings",
                }[value],
                key="overview_events_type_filter",
            )
        )
        if controls[1].button("Refresh FOMC Calendar", key="overview_events_refresh_fomc", use_container_width=True):
            current_year = datetime.now().year
            with st.spinner("Collecting FOMC calendar from the official Fed page..."):
                st.session_state["overview_fomc_calendar_result"] = run_collect_fomc_calendar(
                    years=(current_year, current_year + 1)
                )
            st.rerun()
        if controls[2].button(
            "Refresh Earnings Calendar",
            key="overview_events_refresh_earnings",
            use_container_width=True,
            help="Collects upcoming earnings for the latest S&P 500 market movers snapshot.",
        ):
            with st.spinner("Collecting earnings dates from yfinance calendar for latest S&P 500 movers..."):
                st.session_state["overview_earnings_calendar_result"] = run_collect_earnings_calendar(
                    symbol_source="latest_movers",
                    universe_code="SP500",
                    top_movers_limit=20,
                    lookahead_days=120,
                    max_symbols=50,
                    validate_with_nasdaq=True,
                )
            st.rerun()
        controls[3].caption(
            "Overview reads stored rows from `finance_meta.market_event_calendar`; refresh writes through ingestion job wrappers."
        )

    selected_event_type = None if event_filter == "ALL" else event_filter
    snapshot = load_overview_market_events_snapshot(event_type=selected_event_type, horizon_days=540)
    coverage = dict(snapshot.get("coverage") or {})
    render_status_card_grid(
        [
            {
                "title": "Next Event",
                "value": _snapshot_value(coverage.get("next_event_date")),
                "detail": f"filter: {snapshot.get('event_type') or 'All'}",
                "tone": "positive" if coverage.get("next_event_date") else "warning",
            },
            {
                "title": "Stored Events",
                "value": coverage.get("event_count") or 0,
                "detail": (
                    f"official: {coverage.get('official_count') or 0}, "
                    f"estimates: {coverage.get('estimate_count') or 0}"
                ),
                "tone": "positive" if coverage.get("event_count") else "warning",
            },
            {
                "title": "Latest Collection",
                "value": _snapshot_value(coverage.get("latest_collected_at")),
                "detail": (
                    f"cross-checked: {coverage.get('cross_checked_count') or 0}, "
                    f"not confirmed: {coverage.get('not_confirmed_count') or 0}"
                ),
                "tone": "warning" if coverage.get("stale_estimate_count") or coverage.get("not_confirmed_count") else "neutral",
            },
        ]
    )
    _render_snapshot_warnings(snapshot)
    _render_market_job_result("overview_fomc_calendar_result")
    _render_market_job_result("overview_earnings_calendar_result")

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("Stored market event rows are not available for the selected filter. Run the matching refresh here or from Ingestion.")
        return
    calendar_rows = _prepare_event_calendar_frame(rows)
    filtered_rows = _filter_event_rows_for_calendar(calendar_rows)
    calendar_tab, table_tab = st.tabs(["Calendar", "Table"])
    with calendar_tab:
        st.altair_chart(_build_event_calendar_chart(filtered_rows), width="stretch")
        _render_event_date_groups(filtered_rows)
    with table_tab:
        st.dataframe(filtered_rows.drop(columns=["Date Parsed"], errors="ignore"), width="stretch", hide_index=True)


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
