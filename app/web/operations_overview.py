from __future__ import annotations

from typing import Any

import streamlit as st

from app.jobs.run_history import load_run_history
from app.runtime.candidate_library import load_candidate_library_records
from app.runtime.final_selected_portfolios import load_final_selected_portfolio_dashboard
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid


OPERATIONS_OVERVIEW_SCHEMA_VERSION = "operations_overview_v1"


def _safe_int(value: Any) -> int:
    try:
        return int(value or 0)
    except (TypeError, ValueError):
        return 0


def _system_tone(status: str) -> str:
    normalized = str(status or "").strip().lower()
    if normalized == "success":
        return "positive"
    if normalized in {"partial_success", "warning", "review_required"}:
        return "warning"
    if normalized in {"failed", "failure", "error"} or "fail" in normalized:
        return "danger"
    return "neutral"


def _portfolio_monitoring_status(*, dashboard_rows: int, watch_count: int, blocked_count: int, missing_count: int) -> str:
    if dashboard_rows <= 0:
        return "No Selected Rows"
    if blocked_count or missing_count:
        return "Blocked"
    if watch_count:
        return "Review Needed"
    return "Ready"


def build_operations_overview_model(
    *,
    selected_dashboard: dict[str, Any],
    run_history: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]],
) -> dict[str, Any]:
    """Build a Streamlit-free IA model for the Operations landing page."""

    dashboard_summary = dict(selected_dashboard.get("summary") or {})
    portfolio_state = dict(selected_dashboard.get("portfolio_state") or {})
    portfolio_metrics = dict(portfolio_state.get("metrics") or {})
    status_counts = dict(dashboard_summary.get("status_counts") or {})

    dashboard_rows = _safe_int(dashboard_summary.get("dashboard_row_count"))
    selected_count = _safe_int(dashboard_summary.get("selected_decision_count"))
    portfolio_count = _safe_int(portfolio_metrics.get("portfolio_count"))
    assigned_count = _safe_int(portfolio_metrics.get("assigned_strategy_reference_count"))
    missing_count = _safe_int(portfolio_metrics.get("missing_reference_count"))
    watch_count = (
        _safe_int(status_counts.get("watch"))
        + _safe_int(status_counts.get("rebalance_needed"))
        + _safe_int(status_counts.get("re_review_needed"))
    )
    blocked_count = _safe_int(status_counts.get("blocked"))

    latest_run = dict(run_history[0] if run_history else {})
    latest_status = str(latest_run.get("status") or "No runs")
    system_status = "Healthy" if latest_status.lower() == "success" else ("No Runs" if not run_history else "Attention Needed")

    lanes = [
        {
            "key": "portfolio_monitoring",
            "title": "Portfolio Monitoring",
            "priority": "primary",
            "status": _portfolio_monitoring_status(
                dashboard_rows=dashboard_rows,
                watch_count=watch_count,
                blocked_count=blocked_count,
                missing_count=missing_count,
            ),
            "tone": "danger" if blocked_count or missing_count else ("warning" if watch_count or not dashboard_rows else "positive"),
            "target_surface": "Operations > Portfolio Monitoring",
            "detail": "Final Review selected rows and user monitoring portfolios.",
            "metrics": {
                "selected_decision_count": selected_count,
                "dashboard_row_count": dashboard_rows,
                "portfolio_count": portfolio_count,
                "assigned_strategy_count": assigned_count,
                "watch_or_review_count": watch_count,
                "blocked_count": blocked_count,
                "missing_reference_count": missing_count,
            },
            "links": [{"target_key": "portfolio_monitoring", "label": "Open Portfolio Monitoring", "icon": "📊"}],
        },
        {
            "key": "system_data_health",
            "title": "System / Data Health",
            "priority": "primary",
            "status": system_status,
            "tone": _system_tone(latest_status),
            "target_surface": "Operations > System / Data Health",
            "detail": "Run health, failure artifacts, logs, and ingestion handoff.",
            "metrics": {
                "run_count": len(run_history),
                "latest_job": latest_run.get("job_name") or "-",
                "latest_status": latest_status,
            },
            "links": [{"target_key": "system_data_health", "label": "Open System / Data Health", "icon": "🧾"}],
        },
        {
            "key": "archive_recovery",
            "title": "Archive / Recovery",
            "priority": "secondary",
            "status": "Available" if run_history or candidate_records else "Empty",
            "tone": "neutral",
            "target_surface": "Operations > Archive / Recovery",
            "detail": "Replay old backtests and inspect saved candidates when recovery is needed.",
            "metrics": {
                "backtest_run_count": len(run_history),
                "candidate_count": len(candidate_records),
            },
            "links": [
                {"target_key": "archive_backtest_runs", "label": "Open Backtest Runs", "icon": "🗂️"},
                {"target_key": "archive_candidates", "label": "Open Candidates", "icon": "📌"},
            ],
        },
        {
            "key": "reference_reports",
            "title": "Reference / Reports",
            "priority": "secondary",
            "status": "Guide Ready",
            "tone": "neutral",
            "target_surface": "Reference > Guides",
            "detail": "Workflow meaning, decision boundaries, and future report handoff.",
            "metrics": {
                "report_export": "Planned",
                "guide": "Available",
            },
            "links": [{"target_key": "reference_guides", "label": "Open Guides", "icon": "📚"}],
        },
    ]
    return {
        "schema_version": OPERATIONS_OVERVIEW_SCHEMA_VERSION,
        "operations_model": "Portfolio Monitoring + System/Data Health + Archive/Recovery",
        "lanes": lanes,
        "execution_boundary": {
            "live_approval": False,
            "broker_order": False,
            "account_sync": False,
            "auto_rebalance": False,
            "registry_write": False,
        },
    }


def _format_metric_value(value: Any) -> str:
    if isinstance(value, (int, float)):
        return f"{value:,}"
    return str(value or "-")


def _lane_cards(model: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for lane in list(model.get("lanes") or []):
        cards.append(
            {
                "title": lane.get("title"),
                "value": lane.get("status"),
                "detail": lane.get("target_surface"),
                "tone": lane.get("tone"),
            }
        )
    return cards


def _render_lane(lane: dict[str, Any], *, page_targets: dict[str, Any]) -> None:
    with st.container(border=True):
        render_badge_strip(
            [
                {"label": "Lane", "value": lane.get("priority"), "tone": "positive" if lane.get("priority") == "primary" else "neutral"},
                {"label": "Status", "value": lane.get("status"), "tone": lane.get("tone")},
            ]
        )
        st.markdown(f"#### {lane.get('title') or '-'}")
        st.caption(str(lane.get("detail") or ""))
        metric_items = list(dict(lane.get("metrics") or {}).items())[:4]
        if metric_items:
            columns = st.columns(len(metric_items), gap="small")
            for column, (label, value) in zip(columns, metric_items):
                column.metric(label.replace("_", " ").title(), _format_metric_value(value))
        link_columns = st.columns(max(len(lane.get("links") or []), 1), gap="small")
        for column, link in zip(link_columns, list(lane.get("links") or [])):
            target = page_targets.get(str(link.get("target_key") or ""))
            if target is None:
                column.caption(str(link.get("label") or lane.get("target_surface") or ""))
            else:
                column.page_link(
                    target,
                    label=str(link.get("label") or lane.get("target_surface") or "Open"),
                    icon=link.get("icon"),
                    use_container_width=True,
                )


def render_operations_overview_page(*, page_targets: dict[str, Any] | None = None) -> None:
    """Render the Operations command center without mutating workflow registries."""

    selected_dashboard = load_final_selected_portfolio_dashboard()
    run_history = load_run_history(limit=30)
    candidate_records = load_candidate_library_records()
    model = build_operations_overview_model(
        selected_dashboard=selected_dashboard,
        run_history=run_history,
        candidate_records=candidate_records,
    )
    page_targets = dict(page_targets or {})

    st.title("Operations Overview")
    st.caption("Portfolio monitoring, system/data health, and archive recovery are separated here before opening a detailed tool.")
    render_status_card_grid(_lane_cards(model))
    render_badge_strip(
        [
            {"label": "Live Approval", "value": "Disabled", "tone": "neutral"},
            {"label": "Order", "value": "Disabled", "tone": "neutral"},
            {"label": "Auto Rebalance", "value": "Disabled", "tone": "neutral"},
        ]
    )

    lanes = list(model.get("lanes") or [])
    primary_lanes = [lane for lane in lanes if lane.get("priority") == "primary"]
    secondary_lanes = [lane for lane in lanes if lane.get("priority") != "primary"]

    st.markdown("### Primary Operations")
    for lane in primary_lanes:
        _render_lane(lane, page_targets=page_targets)

    st.markdown("### Archive / Reference")
    for lane in secondary_lanes:
        _render_lane(lane, page_targets=page_targets)

    with st.expander("Execution Boundary", expanded=False):
        st.json(model.get("execution_boundary") or {})
