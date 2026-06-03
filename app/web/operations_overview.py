from __future__ import annotations

from typing import Any

import streamlit as st

from app.jobs.run_history import load_run_history
from app.runtime.candidate_library import load_candidate_library_records
from app.runtime.final_selected_portfolios import load_final_selected_portfolio_dashboard
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid


OPERATIONS_OVERVIEW_SCHEMA_VERSION = "operations_overview_v1"
OPERATIONS_CONSOLE_VERSION = "operations_console_v2_v5"


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


def _disabled_action_boundary() -> dict[str, bool]:
    return {
        "live_approval": False,
        "broker_order": False,
        "account_sync": False,
        "order_instruction": False,
        "auto_rebalance": False,
        "registry_write": False,
    }


def _build_stage_roadmap() -> list[dict[str, str]]:
    return [
        {
            "stage": "1차",
            "title": "Operations IA Foundation",
            "status": "completed",
            "output": "Operations Overview, Portfolio Monitoring, System / Data Health, Archive / Recovery lanes.",
        },
        {
            "stage": "2차",
            "title": "Surface Audit",
            "status": "completed",
            "output": "Keep primary monitoring / system health; demote history and candidate tools to archive recovery.",
        },
        {
            "stage": "3차",
            "title": "Rebalance Semantics",
            "status": "completed",
            "output": "Treat rebalance rows as target snapshots and next manual review dates, not order instructions.",
        },
        {
            "stage": "4차",
            "title": "Archive Demotion",
            "status": "completed",
            "output": "Backtest Run History and Candidate Library remain available as recovery / audit tools.",
        },
        {
            "stage": "5차",
            "title": "Operations Console",
            "status": "completed",
            "output": "Show action queue, primary operations, archive tools, and execution boundary on the landing surface.",
        },
    ]


def _build_surface_audit() -> list[dict[str, Any]]:
    return [
        {
            "surface_key": "portfolio_monitoring",
            "surface": "Operations > Portfolio Monitoring",
            "primary_operations": True,
            "decision": "keep_primary_improve",
            "role": "Selected portfolio monitoring, review signals, target snapshot checks.",
            "change": "Keep as the main user-facing Operations surface and clarify rebalance semantics.",
        },
        {
            "surface_key": "system_data_health",
            "surface": "Operations > System / Data Health",
            "primary_operations": True,
            "decision": "keep_primary_improve",
            "role": "Run health, failure artifacts, logs, and data/system triage.",
            "change": "Keep as primary system health surface; execution still belongs in Ingestion or replay tools.",
        },
        {
            "surface_key": "backtest_run_history",
            "surface": "Operations > Archive: Backtest Runs",
            "primary_operations": False,
            "decision": "keep_as_archive_recovery",
            "role": "Recover or audit old backtest runs and restore forms when needed.",
            "change": "Do not delete; keep below primary operations as recovery tooling.",
        },
        {
            "surface_key": "candidate_library",
            "surface": "Operations > Archive: Candidates",
            "primary_operations": False,
            "decision": "keep_as_archive_recovery",
            "role": "Inspect legacy/current/pre-live candidate snapshots and rebuild result curves.",
            "change": "Do not delete; keep below primary operations as candidate archive tooling.",
        },
        {
            "surface_key": "reference_reports",
            "surface": "Reference > Guides",
            "primary_operations": False,
            "decision": "keep_reference_future_reports",
            "role": "Explain workflow meaning and future manual report handoff.",
            "change": "Keep as reference; report export remains a later scope.",
        },
    ]


def _build_action_queue(
    *,
    dashboard_rows: int,
    watch_count: int,
    blocked_count: int,
    missing_count: int,
    latest_status: str,
    run_history_count: int,
    candidate_count: int,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    if blocked_count or missing_count:
        actions.append(
            {
                "key": "fix_portfolio_monitoring_blockers",
                "title": "Portfolio blockers need review",
                "tone": "danger",
                "target_key": "portfolio_monitoring",
                "target_surface": "Operations > Portfolio Monitoring",
                "reason": f"Blocked rows: {blocked_count}, missing references: {missing_count}.",
                "next_action": "Open Portfolio Monitoring and resolve blocked or missing selected references.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    elif watch_count:
        actions.append(
            {
                "key": "review_portfolio_monitoring",
                "title": "Portfolio monitoring needs review",
                "tone": "warning",
                "target_key": "portfolio_monitoring",
                "target_surface": "Operations > Portfolio Monitoring",
                "reason": f"{watch_count} selected rows are watch / rebalance-review / re-review candidates.",
                "next_action": "Open Portfolio Monitoring and inspect target snapshots, review signals, and open issues.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    elif dashboard_rows:
        actions.append(
            {
                "key": "routine_portfolio_monitoring",
                "title": "Portfolio monitoring ready",
                "tone": "positive",
                "target_key": "portfolio_monitoring",
                "target_surface": "Operations > Portfolio Monitoring",
                "reason": f"{dashboard_rows} selected rows are available for routine monitoring.",
                "next_action": "Open Portfolio Monitoring when you want to refresh or inspect monitoring scenarios.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    else:
        actions.append(
            {
                "key": "no_selected_rows",
                "title": "No selected monitoring rows",
                "tone": "neutral",
                "target_key": "reference_guides",
                "target_surface": "Reference > Guides",
                "reason": "Final Review has not produced selected monitoring rows yet.",
                "next_action": "Use Backtest -> Final Review to create selected monitoring candidates first.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )

    normalized_status = str(latest_status or "").strip().lower()
    if normalized_status not in {"success", "no runs"}:
        actions.append(
            {
                "key": "inspect_system_data_health",
                "title": "System / data health needs attention",
                "tone": "danger" if "fail" in normalized_status or normalized_status in {"failed", "failure", "error"} else "warning",
                "target_key": "system_data_health",
                "target_surface": "Operations > System / Data Health",
                "reason": f"Latest run status is {latest_status or '-'}; run count: {run_history_count}.",
                "next_action": "Open System / Data Health before relying on fresh monitoring evidence.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    if run_history_count or candidate_count:
        actions.append(
            {
                "key": "archive_recovery_available",
                "title": "Archive / recovery tools available",
                "tone": "neutral",
                "target_key": "archive_backtest_runs" if run_history_count else "archive_candidates",
                "target_surface": "Operations > Archive / Recovery",
                "reason": f"Backtest runs: {run_history_count}, candidate snapshots: {candidate_count}.",
                "next_action": "Use archive tools only when recovering or auditing previous work.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    return actions[:4]


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
        "console_version": OPERATIONS_CONSOLE_VERSION,
        "operations_model": "Portfolio Monitoring + System/Data Health + Archive/Recovery",
        "lanes": lanes,
        "stage_roadmap": _build_stage_roadmap(),
        "surface_audit": _build_surface_audit(),
        "action_queue": _build_action_queue(
            dashboard_rows=dashboard_rows,
            watch_count=watch_count,
            blocked_count=blocked_count,
            missing_count=missing_count,
            latest_status=latest_status,
            run_history_count=len(run_history),
            candidate_count=len(candidate_records),
        ),
        "execution_boundary": {
            "live_approval": False,
            "broker_order": False,
            "account_sync": False,
            "order_instruction": False,
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


def _render_action_queue(model: dict[str, Any], *, page_targets: dict[str, Any]) -> None:
    st.markdown("### Today's Operations Queue")
    st.caption("먼저 확인할 항목만 보여줍니다. 모든 항목은 검토 / 복구 / 감사용이며 주문이나 자동 리밸런싱을 만들지 않습니다.")
    for action in list(model.get("action_queue") or []):
        with st.container(border=True):
            render_badge_strip(
                [
                    {"label": "Action", "value": action.get("title"), "tone": action.get("tone")},
                    {"label": "Target", "value": action.get("target_surface"), "tone": "neutral"},
                    {"label": "Order / Rebalance", "value": "Disabled", "tone": "neutral"},
                ]
            )
            st.caption(str(action.get("reason") or ""))
            st.markdown(f"**Next:** {action.get('next_action') or '-'}")
            target = page_targets.get(str(action.get("target_key") or ""))
            if target is not None:
                st.page_link(target, label=f"Open {action.get('target_surface')}", use_container_width=True)


def _render_stage_roadmap(model: dict[str, Any]) -> None:
    with st.expander("Operations restructuring roadmap", expanded=False):
        st.caption("이 화면은 1차 보강에서 끝난 것이 아니라 2~5차까지 반영한 최종 Operations Console 기준입니다.")
        st.dataframe(list(model.get("stage_roadmap") or []), width="stretch", hide_index=True)


def _render_surface_audit(model: dict[str, Any]) -> None:
    with st.expander("Operations surface audit / keep-improve-archive decisions", expanded=False):
        st.caption("삭제가 아니라 유지 / 개선 / archive 격하 기준을 먼저 고정한 감사표입니다.")
        st.dataframe(list(model.get("surface_audit") or []), width="stretch", hide_index=True)


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

    st.title("Operations Console")
    st.caption("선정 후 portfolio monitoring과 system/data health를 먼저 보고, archive/recovery는 필요할 때만 여는 운영 화면입니다.")
    _render_action_queue(model, page_targets=page_targets)
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

    _render_stage_roadmap(model)
    _render_surface_audit(model)
    with st.expander("Execution Boundary", expanded=False):
        st.json(model.get("execution_boundary") or {})
