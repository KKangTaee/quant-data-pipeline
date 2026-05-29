from __future__ import annotations

from datetime import datetime
from html import escape
from inspect import signature
from typing import Any, Callable

import altair as alt
import pandas as pd
import streamlit as st

from app.jobs.run_history import append_run_history
from app.jobs.ingestion_jobs import (
    run_collect_earnings_calendar,
    run_collect_fomc_calendar,
    run_collect_macro_calendar,
    run_collect_market_intraday_snapshot,
    run_collect_sp500_universe,
)
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.overview_dashboard_helpers import (
    load_overview_collection_ops_snapshot,
    load_overview_dashboard_snapshot,
    load_overview_group_leadership_snapshot,
    load_overview_market_events_snapshot,
    load_overview_market_mover_sectors,
    load_overview_market_movers_snapshot,
)


MARKET_INTRADAY_REFRESH_MINUTES = 5
MARKET_MOVER_TABLE_CHROME_HEIGHT = 44
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
        age_tone = refresh_state.get("tone") or ("positive" if int(stale_minutes) <= 10 else "warning")
    else:
        age_value = _snapshot_value(stale_days)
        age_detail = "calendar days from effective date"
        age_tone = "positive" if stale_days is not None and int(stale_days) <= 3 else "warning"
    returnable = coverage.get("returnable_count") or 0
    universe_count = coverage.get("universe_count") or 0
    coverage_text = f"{returnable} / {universe_count}" if universe_count else "-"
    returnable_pct = coverage.get("returnable_pct")
    coverage_detail = f"{float(returnable_pct):.2f}% returnable" if returnable_pct is not None else None
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
                "detail": coverage_detail or f"missing: {missing_count}, failed: {failed_count}",
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


def _signed_return_axis_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_abs = max(1.0, float(numeric.abs().max()) if not numeric.empty else 1.0)
    return [-max_abs * 1.12, max_abs * 1.12]


def _symmetric_return_scale(values: pd.Series) -> alt.Scale:
    return alt.Scale(domain=_symmetric_return_domain(values), range=["#b91c1c", "#f8fafc", "#0f766e"])


def _positive_return_domain(values: pd.Series) -> list[float]:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    max_value = max(1.0, float(numeric.max()) if not numeric.empty else 1.0)
    return [0, max_value * 1.16]


def _market_mover_chart_height(row_count: int) -> int:
    if row_count <= 20:
        return 540
    if row_count <= 30:
        return 660
    if row_count <= 50:
        return 880
    if row_count <= 75:
        return 1120
    return 1360


def _build_return_bar_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    if not chart_rows.empty and "Return %" in chart_rows:
        chart_rows["Return %"] = pd.to_numeric(chart_rows["Return %"], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Return %"])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Symbol": "No Data", "Return %": 0.0}])
    if "Rank" in chart_rows:
        chart_rows = chart_rows.sort_values("Rank")
    chart_rows["Return Magnitude %"] = chart_rows["Return %"].abs()
    chart_rows["Return Label"] = chart_rows["Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    symbol_order = chart_rows["Symbol"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Return Magnitude %:Q",
            title="Move Magnitude %",
            stack=None,
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Return Magnitude %"])),
        ),
        y=alt.Y("Symbol:N", sort=symbol_order, title=None, axis=alt.Axis(labelLimit=80)),
        tooltip=["Rank:O", "Symbol:N", "Name:N", "Return Label:N", "Sector:N", "Industry:N"],
    )
    bars = (
        base
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            color=alt.condition(
                "datum['Return %'] < 0",
                alt.value("#dc2626"),
                alt.value("#0f766e"),
            )
        )
    )
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color="#111827")
        .encode(
            text=alt.Text("Return Label:N"),
        )
    )
    return (bars + labels).properties(height=_market_mover_chart_height(len(chart_rows)))


def _build_market_mover_sector_chart(rows: pd.DataFrame) -> alt.Chart:
    source_row_count = len(rows)
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
    chart_rows["Average Return Magnitude %"] = chart_rows["Average Return %"].abs()
    chart_rows["Average Return Label"] = chart_rows["Average Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    chart_rows["Top Return Label"] = chart_rows["Top Return %"].map(
        lambda value: f"{float(value):+.2f}%" if pd.notna(value) else "-"
    )
    sector_order = chart_rows["Sector"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            "Average Return Magnitude %:Q",
            title="Avg Move Magnitude %",
            stack=None,
            scale=alt.Scale(domain=_positive_return_domain(chart_rows["Average Return Magnitude %"])),
        ),
        y=alt.Y("Sector:N", sort=sector_order, title=None, axis=alt.Axis(labelLimit=150)),
        tooltip=["Sector:N", "Count:Q", "Average Return Label:N", "Top Return Label:N"],
    )
    bars = (
        base
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            color=alt.condition(
                "datum['Average Return %'] < 0",
                alt.value("#dc2626"),
                alt.value("#0f766e"),
            )
        )
    )
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color="#111827")
        .encode(
            text=alt.Text("Average Return Label:N"),
        )
    )
    return (bars + labels).properties(height=_market_mover_chart_height(source_row_count))


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


def _build_group_leadership_rank_chart(rows: pd.DataFrame) -> alt.Chart:
    chart_rows = rows.copy()
    metric = "Market Cap Weighted Return %"
    if not chart_rows.empty and metric in chart_rows:
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=[metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame(
            [{"Rank": 1, "Group": "No Data", metric: 0.0, "Equal Weight Return %": 0.0, "Symbols": 0, "Top Symbol": "-"}]
        )
    chart_rows = chart_rows.sort_values("Rank") if "Rank" in chart_rows else chart_rows
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    group_order = chart_rows["Group"].drop_duplicates().tolist()
    base = alt.Chart(chart_rows).encode(
        x=alt.X(
            f"{metric}:Q",
            title="Cap Weighted Return %",
            stack=None,
            scale=alt.Scale(domain=_signed_return_axis_domain(chart_rows[metric])),
        ),
        y=alt.Y("Group:N", sort=group_order, title=None, axis=alt.Axis(labelLimit=220)),
        tooltip=[
            "Rank:O",
            "Group:N",
            "Symbols:Q",
            "Return Label:N",
            "Equal Weight Return %:Q",
            "Top Symbol:N",
            "Top Symbol Return %:Q",
        ],
    )
    bars = (
        base
        .mark_bar(cornerRadiusEnd=3)
        .encode(
            color=alt.condition(
                f"datum['{metric}'] < 0",
                alt.value("#dc2626"),
                alt.value("#0f766e"),
            )
        )
    )
    labels = (
        base
        .mark_text(align="left", baseline="middle", dx=5, fontSize=11, color="#111827")
        .encode(text=alt.Text("Return Label:N"))
    )
    return (bars + labels).properties(height=max(320, min(680, 34 * len(chart_rows))))


def _build_group_leadership_trend_chart(rows: pd.DataFrame) -> alt.Chart:
    metric = "Market Cap Weighted Return %"
    chart_rows = rows.copy()
    if not chart_rows.empty and metric in chart_rows and "Date" in chart_rows:
        chart_rows["Date"] = pd.to_datetime(chart_rows["Date"], errors="coerce")
        chart_rows[metric] = pd.to_numeric(chart_rows[metric], errors="coerce")
        chart_rows = chart_rows.dropna(subset=["Date", metric])
    if chart_rows.empty:
        chart_rows = pd.DataFrame([{"Date": pd.Timestamp.today().normalize(), "Group": "No Data", metric: 0.0}])
    chart_rows["Return Label"] = chart_rows[metric].map(lambda value: f"{float(value):+.2f}%")
    line = (
        alt.Chart(chart_rows)
        .mark_line(point=True, strokeWidth=2)
        .encode(
            x=alt.X("Date:T", title=None),
            y=alt.Y(f"{metric}:Q", title="Cap Weighted Return %"),
            color=alt.Color("Group:N", legend=alt.Legend(title=None, orient="bottom")),
            tooltip=["Date:T", "Group:N", "Return Label:N", "Symbols:Q", "Top Symbol:N"],
        )
    )
    return line.properties(height=420)


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
            if details.get("universe_code") and details.get("snapshot_time_utc"):
                with st.expander("Snapshot Diagnostics", expanded=False):
                    metric_cols = st.columns(4)
                    metric_cols[0].metric("Snapshot Time", _snapshot_value(details.get("snapshot_time_utc")))
                    metric_cols[1].metric("Rows Written", result.get("rows_written") or 0)
                    metric_cols[2].metric("Failed", len(result.get("failed_symbols") or []))
                    metric_cols[3].metric("Method", method)
                    diagnostics = details.get("diagnostics") or {}
                    if diagnostics:
                        diag_rows = [
                            {"Key": key, "Value": str(value)}
                            for key, value in diagnostics.items()
                            if value not in (None, "", [], {})
                        ]
                        if diag_rows:
                            st.dataframe(pd.DataFrame(diag_rows), width="stretch", hide_index=True)
    failed_symbols = result.get("failed_symbols") or []
    if failed_symbols:
        with st.expander(f"Failed / Missing Symbols ({len(failed_symbols)})", expanded=False):
            st.write(", ".join(str(symbol) for symbol in failed_symbols[:100]))
    diagnostics = [item for item in details.get("symbol_diagnostics") or [] if isinstance(item, dict)]
    if diagnostics:
        issue_rows = [
            {
                "Symbol": item.get("symbol") or "-",
                "Status": item.get("status") or "-",
                "Reason": item.get("reason") or "-",
                "Detail": item.get("detail") or "-",
                "Provider Dates": ", ".join(str(value) for value in item.get("provider_dates") or []),
                "Event Dates": ", ".join(str(value) for value in item.get("event_dates") or []),
            }
            for item in diagnostics
            if item.get("status") != "event_found"
        ]
        with st.expander(f"Earnings Diagnostics ({len(issue_rows)} issue symbols)", expanded=False):
            metric_cols = st.columns(4)
            metric_cols[0].metric("With Events", details.get("symbols_with_events") or 0)
            metric_cols[1].metric("Missing", details.get("symbols_missing_count") or len(details.get("missing_symbols") or []))
            metric_cols[2].metric("Failed", details.get("symbols_failed_count") or len(details.get("failed_symbols") or []))
            metric_cols[3].metric("Events Found", details.get("events_found") or 0)
            reason_rows = [
                {"Status": "missing", "Reason": key, "Count": value}
                for key, value in (details.get("missing_reason_counts") or {}).items()
            ] + [
                {"Status": "failed", "Reason": key, "Count": value}
                for key, value in (details.get("failed_reason_counts") or {}).items()
            ]
            if reason_rows:
                st.caption("Issue reason counts")
                st.dataframe(pd.DataFrame(reason_rows), width="stretch", hide_index=True)
            if issue_rows:
                st.caption("Symbol-level issues")
                st.dataframe(pd.DataFrame(issue_rows), width="stretch", hide_index=True)
            else:
                st.success("All requested symbols had at least one earnings date in the selected window.")


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        append_run_history(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


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
    coverage = dict(snapshot.get("coverage") or {})
    state = _get_market_movers_refresh_state(snapshot, universe_code=universe_code, period=period)

    with st.container(border=True):
        if state is not None:
            _render_refresh_state_dot(
                color=str(state["dot_color"]),
                label=str(state["label"]),
                detail=str(state["detail"]),
            )
        refresh_state = dict(coverage.get("refresh_state") or {})
        returnable = coverage.get("returnable_count") or 0
        universe_count = coverage.get("universe_count") or 0
        returnable_pct = coverage.get("returnable_pct")
        next_due = refresh_state.get("next_due_in_minutes")
        next_check_text = "now" if next_due in (None, 0) else f"{int(next_due)}m"
        render_badge_strip(
            [
                {"label": "Universe", "value": universe_label, "tone": "neutral"},
                {"label": "Mode", "value": coverage.get("price_mode") or "-", "tone": "neutral"},
                {
                    "label": "Coverage",
                    "value": (
                        f"{returnable} / {universe_count}"
                        + (f" ({float(returnable_pct):.1f}%)" if returnable_pct is not None else "")
                    ),
                    "tone": "positive" if universe_count and returnable == universe_count else "warning",
                },
                {"label": "Next Check", "value": next_check_text, "tone": "neutral"},
            ]
        )
        if refresh_state.get("recommended_action"):
            st.caption(str(refresh_state.get("recommended_action")))
        cols = st.columns([1, 1, 1], gap="small", vertical_alignment="center")
        if cols[0].button(
            "Update Daily Snapshot",
            key=f"overview_{universe_code.lower()}_intraday_refresh",
            use_container_width=True,
            help="Collect provider quotes and store a new DB snapshot. The timed status check only reloads stored DB rows.",
        ):
            with st.spinner(f"Updating {universe_label} quote snapshot..."):
                _store_overview_job_result(
                    intraday_result_key,
                    _run_collect_market_intraday_snapshot_compat(
                        universe_code=universe_code,
                        universe_limit=universe_limit,
                    ),
                )
            st.rerun()
        if universe_code == "SP500" and cols[1].button(
            "Refresh Universe",
            key="overview_sp500_universe_refresh",
            use_container_width=True,
        ):
            with st.spinner("Refreshing S&P 500 universe..."):
                _store_overview_job_result("overview_sp500_universe_result", run_collect_sp500_universe())
            st.rerun()
        if universe_code != "SP500":
            cols[1].caption("Universe is based on market-cap ranked asset profiles.")
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
        st.dataframe(
            rows,
            width="stretch",
            height=_market_mover_chart_height(len(rows)) + MARKET_MOVER_TABLE_CHROME_HEIGHT,
            hide_index=True,
        )


def _render_market_movers_tab() -> None:
    st.markdown("### Market Movers")
    with st.container(border=True):
        controls = st.columns([1.1, 1.2, 1.1, 0.8, 0.9], gap="small", vertical_alignment="bottom")
        coverage = str(
            controls[0].selectbox(
                "Coverage",
                ["SP500", "TOP1000", "TOP2000"],
                index=0,
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
            controls[1].selectbox(
                "Period",
                ["daily", "weekly", "monthly", "yearly"],
                index=0,
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
                disabled=period != "daily",
                help="Reloads the stored DB snapshot status. It does not collect provider data automatically.",
            )
        )

    reloaded_at = st.session_state.get("overview_market_movers_reloaded_at")
    if reloaded_at:
        st.caption(f"Last DB snapshot reload request: {reloaded_at}")
    if period == "daily":
        st.caption(
            "Daily movers use the latest stored quote snapshot versus previous close when available. "
            "Status Check reloads DB state only; provider refresh stays manual."
        )

    refresh_seconds = {"1 min": 60, "5 min": 300, "10 min": 600}.get(refresh_mode)
    if period != "daily":
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
            _render_market_movers_refresh_bar(
                snapshot,
                universe_code=coverage,
                universe_limit=universe_limit,
                period=period,
            )
            _render_market_movers_snapshot_panel(
                snapshot,
                universe_code=coverage,
                period=period,
            )

        _auto_refresh_panel()
    else:
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
        _render_market_movers_snapshot_panel(
            snapshot,
            universe_code=coverage,
            period=period,
        )


def _render_sector_industry_tab() -> None:
    st.markdown("### Sector / Industry Leadership")
    controls = st.columns([1.1, 1, 1, 0.8, 0.9], gap="small", vertical_alignment="bottom")
    coverage = str(
        controls[0].selectbox(
            "Coverage",
            ["SP500", "TOP1000", "TOP2000"],
            index=0,
            format_func=lambda value: {
                "SP500": "S&P 500",
                "TOP1000": "Top 1000",
                "TOP2000": "Top 2000",
            }[value],
            key="overview_group_leadership_coverage_code",
        )
    )
    universe_limit = {"SP500": 500, "TOP1000": 1000, "TOP2000": 2000}[coverage]
    group_by = str(
        controls[1].selectbox(
            "Group",
            ["sector", "industry"],
            index=0,
            format_func=lambda value: {"sector": "Sector", "industry": "Industry"}[value],
            key="overview_group_leadership_group",
        )
    )
    period = str(
        controls[2].selectbox(
            "Period",
            ["daily", "weekly", "monthly"],
            index=2,
            format_func=lambda value: {
                "daily": "Daily",
                "weekly": "Weekly",
                "monthly": "Monthly",
            }[value],
            key="overview_group_leadership_period",
        )
    )
    top_n = int(
        controls[3].number_input(
            "Top N",
            min_value=5,
            max_value=100,
            value=10,
            step=5,
            key="overview_group_leadership_top_n",
        )
    )
    min_group_size = int(
        controls[4].number_input(
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
        universe_code=coverage,
        group_by=group_by,
        period=period,
        top_n=top_n,
        min_group_size=min_group_size,
    )
    _render_snapshot_status_cards(snapshot)
    _render_snapshot_warnings(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("DB-backed group leadership rows are not available for the selected controls.")
        return
    trend_rows = snapshot.get("trend_rows")
    chart_tab, table_tab = st.tabs(["Trend", "Table"])
    with chart_tab:
        st.markdown("#### Latest Ranking")
        st.altair_chart(_build_group_leadership_rank_chart(rows), width="stretch")
        if isinstance(trend_rows, pd.DataFrame) and not trend_rows.empty:
            st.markdown("#### Trend")
            st.altair_chart(_build_group_leadership_trend_chart(trend_rows), width="stretch")
    with table_tab:
        st.dataframe(rows, width="stretch", hide_index=True)
        if isinstance(trend_rows, pd.DataFrame) and not trend_rows.empty:
            st.dataframe(trend_rows, width="stretch", hide_index=True)


def _event_type_label(value: Any) -> str:
    labels = {
        "FOMC_MEETING": "FOMC",
        "EARNINGS": "Earnings",
        "MACRO": "Macro",
        "MACRO_CPI": "CPI",
        "MACRO_PPI": "PPI",
        "MACRO_EMPLOYMENT": "Jobs",
        "MACRO_GDP": "GDP",
    }
    return labels.get(str(value or ""), str(value or "-").replace("_", " ").title())


def _event_importance_from_type(value: Any) -> str:
    event_type = str(value or "").upper()
    if event_type == "FOMC_MEETING" or event_type == "MACRO" or event_type.startswith("MACRO_"):
        return "High"
    if event_type == "EARNINGS":
        return "Medium"
    return "Low"


def _event_focus_from_row(row: pd.Series) -> str:
    quality_action = str(row.get("Quality Action") or "")
    if quality_action and quality_action != "No action":
        return "Needs Review"
    days_until = row.get("Days Until")
    if pd.isna(days_until):
        return "Unknown"
    day_number = int(days_until)
    if day_number < 0:
        return "Past"
    if day_number == 0:
        return "Today"
    if day_number <= 7:
        return "This Week"
    if day_number <= 30:
        return "Next 30D"
    return "Later"


def _prepare_event_calendar_frame(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["Date Parsed"] = pd.to_datetime(out.get("Date"), errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    calculated_days = (out["Date Parsed"] - today).dt.days
    if "Days Until" in out:
        out["Days Until"] = pd.to_numeric(out["Days Until"], errors="coerce")
        out["Days Until"] = out["Days Until"].where(out["Days Until"].notna(), calculated_days)
    else:
        out["Days Until"] = calculated_days
    out["Month"] = out["Date Parsed"].dt.strftime("%Y-%m")
    out["Week"] = out["Date Parsed"].dt.to_period("W").astype(str)
    out["Type Label"] = out.get("Type", pd.Series(dtype=str)).map(_event_type_label)
    if "Importance" not in out:
        out["Importance"] = out.get("Type", pd.Series(dtype=str)).map(_event_importance_from_type)
    else:
        fallback_importance = out.get("Type", pd.Series(dtype=str)).map(_event_importance_from_type)
        out["Importance"] = out["Importance"].where(out["Importance"].notna() & (out["Importance"] != ""), fallback_importance)
    if "Focus" not in out:
        out["Focus"] = out.apply(_event_focus_from_row, axis=1)
    else:
        fallback_focus = out.apply(_event_focus_from_row, axis=1)
        out["Focus"] = out["Focus"].where(out["Focus"].notna() & (out["Focus"] != ""), fallback_focus)
    out["Symbol Label"] = out.get("Symbol", pd.Series(dtype=str)).replace({"-": ""})
    out["Summary"] = out.apply(
        lambda row: f"{row.get('Type Label')}: {row.get('Symbol Label') or row.get('Title') or '-'}",
        axis=1,
    )
    return out


def _filter_event_rows_for_calendar(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    filter_cols = st.columns([1, 1, 1, 1], gap="small")
    source_options = ["All"] + sorted(
        value for value in rows.get("Source Type", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    validation_options = ["All"] + sorted(
        value for value in rows.get("Validation", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    importance_values = rows.get("Importance", pd.Series(dtype=str)).dropna().unique().tolist()
    importance_options = ["All"] + [
        value for value in ["High", "Medium", "Low"] if value in importance_values
    ]
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
    importance_filter = str(
        filter_cols[3].selectbox(
            "Importance",
            importance_options,
            index=0,
            key="overview_events_importance_filter",
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
    if importance_filter != "All" and "Importance" in filtered:
        filtered = filtered[filtered["Importance"] == importance_filter]
    return filtered


def _build_event_calendar_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        chart_rows = pd.DataFrame(
            [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Type Label": "No Data", "Count": 0}]
        )
    else:
        valid_rows = rows.dropna(subset=["Date Parsed"])
        if valid_rows.empty:
            chart_rows = pd.DataFrame(
                [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Type Label": "No Data", "Count": 0}]
            )
        else:
            chart_rows = (
                valid_rows
                .groupby(["Date Parsed", "Type Label"], as_index=False)
                .size()
                .rename(columns={"size": "Count"})
            )
    date_min = chart_rows["Date Parsed"].min()
    date_max = chart_rows["Date Parsed"].max()
    if pd.isna(date_min) or pd.isna(date_max):
        date_min = pd.Timestamp(datetime.now().date())
        date_max = date_min + pd.Timedelta(days=1)
    elif date_min == date_max:
        date_max = date_min + pd.Timedelta(days=1)
    max_count = max(1, int(chart_rows.groupby("Date Parsed")["Count"].sum().max() or 0))
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(
                "Date Parsed:T",
                title=None,
                axis=alt.Axis(format="%b %d", labelAngle=-35),
                scale=alt.Scale(domain=[date_min, date_max]),
            ),
            y=alt.Y("Count:Q", title="Events", stack="zero", scale=alt.Scale(domain=[0, max_count])),
            color=alt.Color(
                "Type Label:N",
                title=None,
                legend=alt.Legend(orient="bottom"),
                scale=alt.Scale(range=["#2563eb", "#0f766e", "#b45309", "#7c3aed", "#475569", "#cbd5e1"]),
            ),
            tooltip=["Date Parsed:T", "Type Label:N", "Count:Q"],
        )
        .properties(height=240)
    )


def _event_focus_display_columns(rows: pd.DataFrame) -> list[str]:
    return [
        column
        for column in [
            "Date",
            "Days Until",
            "Type Label",
            "Symbol",
            "Title",
            "Importance",
            "Focus",
            "Validation",
            "Quality Action",
            "Freshness",
        ]
        if column in rows.columns
    ]


def _render_event_focus_table(rows: pd.DataFrame, *, empty_message: str) -> None:
    if rows.empty:
        st.info(empty_message)
        return
    st.dataframe(
        rows[_event_focus_display_columns(rows)].head(20),
        width="stretch",
        hide_index=True,
    )


def _render_event_focus_panel(rows: pd.DataFrame) -> None:
    if rows.empty:
        st.info("No stored event rows match the selected filters.")
        return
    focus_rows = rows.copy()
    focus_rows["Days Until"] = pd.to_numeric(focus_rows.get("Days Until"), errors="coerce")
    upcoming_rows = focus_rows[focus_rows["Days Until"].isna() | (focus_rows["Days Until"] >= 0)].sort_values(
        ["Date Parsed", "Importance", "Type Label", "Symbol"],
        ascending=[True, True, True, True],
    )
    needs_review_rows = focus_rows[
        (focus_rows.get("Focus") == "Needs Review")
        | ((focus_rows.get("Quality Action") != "No action") & focus_rows.get("Quality Action").notna())
    ].sort_values(["Date Parsed", "Type Label", "Symbol"])
    high_impact_rows = focus_rows[focus_rows.get("Importance") == "High"].sort_values(
        ["Date Parsed", "Type Label", "Symbol"]
    )
    this_week_count = int(focus_rows.get("Focus", pd.Series(dtype=str)).isin(["Today", "This Week"]).sum())
    next_30d_count = int(((focus_rows["Days Until"] >= 0) & (focus_rows["Days Until"] <= 30)).sum())
    render_status_card_grid(
        [
            {
                "title": "This Week",
                "value": this_week_count,
                "detail": "today through 7D",
                "tone": "positive" if this_week_count else "neutral",
            },
            {
                "title": "Next 30D",
                "value": next_30d_count,
                "detail": "upcoming stored events",
                "tone": "positive" if next_30d_count else "neutral",
            },
            {
                "title": "High Impact",
                "value": len(high_impact_rows),
                "detail": "FOMC and macro rows",
                "tone": "warning" if len(high_impact_rows) else "neutral",
            },
            {
                "title": "Needs Review",
                "value": len(needs_review_rows),
                "detail": "estimate or source action",
                "tone": "danger" if len(needs_review_rows) else "positive",
            },
        ]
    )
    upcoming_tab, review_tab, impact_tab = st.tabs(["Upcoming", "Needs Review", "High Impact"])
    with upcoming_tab:
        _render_event_focus_table(upcoming_rows, empty_message="No upcoming event rows match the selected filters.")
    with review_tab:
        _render_event_focus_table(needs_review_rows, empty_message="No rows currently require source or validation action.")
    with impact_tab:
        _render_event_focus_table(high_impact_rows, empty_message="No high impact FOMC or macro rows match the selected filters.")


def _render_event_date_groups(rows: pd.DataFrame) -> None:
    if rows.empty:
        st.info("No stored event rows match the selected calendar filters.")
        return
    display_columns = [
        column
        for column in [
            "Type Label",
            "Symbol",
            "Title",
            "Importance",
            "Focus",
            "Source Type",
            "Validation",
            "Freshness",
            "Quality Action",
            "Age Days",
        ]
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
        controls = st.columns([1.1, 1.25, 1.25, 1.25, 1.8], gap="small", vertical_alignment="bottom")
        event_filter = str(
            controls[0].segmented_control(
                "Type",
                ["ALL", "FOMC_MEETING", "EARNINGS", "MACRO"],
                default="ALL",
                format_func=lambda value: {
                    "ALL": "All",
                    "FOMC_MEETING": "FOMC",
                    "EARNINGS": "Earnings",
                    "MACRO": "Macro",
                }[value],
                key="overview_events_type_filter",
            )
        )
        if controls[1].button("Refresh FOMC Calendar", key="overview_events_refresh_fomc", use_container_width=True):
            current_year = datetime.now().year
            with st.spinner("Collecting FOMC calendar from the official Fed page..."):
                _store_overview_job_result(
                    "overview_fomc_calendar_result",
                    run_collect_fomc_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
        if controls[2].button(
            "Refresh Earnings Calendar",
            key="overview_events_refresh_earnings",
            use_container_width=True,
            help="Collects upcoming earnings for the latest S&P 500 market movers snapshot.",
        ):
            with st.spinner("Collecting earnings dates from yfinance calendar for latest S&P 500 movers..."):
                _store_overview_job_result(
                    "overview_earnings_calendar_result",
                    run_collect_earnings_calendar(
                        symbol_source="latest_movers",
                        universe_code="SP500",
                        top_movers_limit=20,
                        lookahead_days=120,
                        max_symbols=50,
                        validate_with_nasdaq=True,
                    ),
                )
            st.rerun()
        if controls[3].button(
            "Refresh Macro Calendar",
            key="overview_events_refresh_macro",
            use_container_width=True,
            help="Collects CPI, PPI, Employment Situation, and GDP release dates from official schedules.",
        ):
            current_year = datetime.now().year
            with st.spinner("Collecting macro calendar from official BLS and BEA schedules..."):
                _store_overview_job_result(
                    "overview_macro_calendar_result",
                    run_collect_macro_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
        controls[4].caption(
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
                    f"high impact: {coverage.get('high_importance_count') or 0}, "
                    f"needs review: {coverage.get('needs_review_count') or 0}"
                ),
                "tone": "warning" if coverage.get("stale_estimate_count") or coverage.get("not_confirmed_count") else "neutral",
            },
            {
                "title": "Upcoming Focus",
                "value": coverage.get("next_30d_count") or 0,
                "detail": f"this week: {coverage.get('this_week_count') or 0}",
                "tone": "positive" if coverage.get("next_30d_count") else "neutral",
            },
        ]
    )
    _render_snapshot_warnings(snapshot)
    _render_market_job_result("overview_fomc_calendar_result")
    _render_market_job_result("overview_earnings_calendar_result")
    _render_market_job_result("overview_macro_calendar_result")

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("Stored market event rows are not available for the selected filter. Run the matching refresh here or from Ingestion.")
        return
    calendar_rows = _prepare_event_calendar_frame(rows)
    filtered_rows = _filter_event_rows_for_calendar(calendar_rows)
    focus_tab, calendar_tab, table_tab = st.tabs(["Focus", "Calendar", "Table"])
    with focus_tab:
        _render_event_focus_panel(filtered_rows)
    with calendar_tab:
        st.altair_chart(_build_event_calendar_chart(filtered_rows), width="stretch")
        _render_event_date_groups(filtered_rows)
    with table_tab:
        st.dataframe(filtered_rows.drop(columns=["Date Parsed"], errors="ignore"), width="stretch", hide_index=True)


def _ops_tone(status: str) -> str:
    normalized = str(status or "").lower()
    if normalized == "ok":
        return "positive"
    if normalized in {"due", "partial"}:
        return "warning"
    if normalized in {"failed", "stale", "missing"}:
        return "danger"
    return "neutral"


def _render_collection_ops_tab() -> None:
    st.markdown("### Data Health")
    st.caption("Stored DB freshness and local collection run history for Overview market intelligence.")
    warning = st.session_state.get("overview_run_history_warning")
    if warning:
        st.warning(str(warning))

    snapshot = load_overview_collection_ops_snapshot()
    coverage = dict(snapshot.get("coverage") or {})
    review_count = sum(
        int(coverage.get(key) or 0)
        for key in ("due_count", "stale_count", "missing_count", "failed_count", "partial_count")
    )
    render_status_card_grid(
        [
            {
                "title": "Ops Status",
                "value": snapshot.get("status") or "-",
                "detail": f"{review_count} item(s) need review",
                "tone": "positive" if snapshot.get("status") == "OK" else "warning",
            },
            {
                "title": "Healthy",
                "value": f"{coverage.get('ok_count') or 0} / {coverage.get('job_count') or 0}",
                "detail": "collection targets",
                "tone": "positive" if coverage.get("ok_count") else "neutral",
            },
            {
                "title": "Latest Success",
                "value": _snapshot_value(coverage.get("latest_success_at")),
                "detail": "from local run history",
                "tone": "positive" if coverage.get("latest_success_at") else "neutral",
            },
            {
                "title": "Latest Issue",
                "value": _snapshot_value(coverage.get("latest_issue_at")),
                "detail": "failed or partial run",
                "tone": "danger" if coverage.get("latest_issue_at") else "neutral",
            },
        ]
    )
    _render_snapshot_warnings(snapshot)

    rows = snapshot.get("rows")
    if not isinstance(rows, pd.DataFrame) or rows.empty:
        st.info("No collection ops status is available yet.")
        return

    status_counts = rows["Status"].value_counts().to_dict() if "Status" in rows else {}
    render_badge_strip(
        [
            {"label": str(status), "value": count, "tone": _ops_tone(str(status))}
            for status, count in status_counts.items()
        ]
    )
    st.dataframe(rows, width="stretch", hide_index=True)


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

    market_tab, group_tab, events_tab, ops_tab, candidate_tab = st.tabs(
        ["Market Movers", "Sector / Industry", "Events", "Data Health", "Candidate Ops"]
    )
    with market_tab:
        _render_market_movers_tab()
    with group_tab:
        _render_sector_industry_tab()
    with events_tab:
        _render_events_tab()
    with ops_tab:
        _render_collection_ops_tab()
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
