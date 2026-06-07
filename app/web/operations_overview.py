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
            "title": "Operations 정보 구조 기반",
            "status": "completed",
            "output": "Operations Overview에 Portfolio Monitoring, System / Data Health, Archive / Recovery lane을 분리했습니다.",
        },
        {
            "stage": "2차",
            "title": "화면 기능 감사",
            "status": "completed",
            "output": "Portfolio Monitoring과 System / Data Health는 primary로 유지하고, history / candidate 도구는 archive recovery로 낮췄습니다.",
        },
        {
            "stage": "3차",
            "title": "리밸런싱 의미 정정",
            "status": "completed",
            "output": "리밸런싱 row를 주문 지시가 아니라 target snapshot과 다음 수동 검토일로 표시합니다.",
        },
        {
            "stage": "4차",
            "title": "Archive 도구 격하",
            "status": "completed",
            "output": "Backtest Run History와 Candidate Library는 복구 / 감사 도구로 보존했습니다.",
        },
        {
            "stage": "5차",
            "title": "Operations Console",
            "status": "completed",
            "output": "첫 화면에서 점검 queue, primary operations, archive 도구, 실행 경계를 함께 확인합니다.",
        },
    ]


def _build_surface_audit() -> list[dict[str, Any]]:
    return [
        {
            "surface_key": "portfolio_monitoring",
            "surface": "Operations > Portfolio Monitoring",
            "primary_operations": True,
            "decision": "keep_primary_improve",
            "role": "선정 포트폴리오 모니터링, review signal, target snapshot 점검을 담당합니다.",
            "change": "사용자가 주로 보는 Operations 화면으로 유지하고 리밸런싱 의미를 명확히 했습니다.",
        },
        {
            "surface_key": "system_data_health",
            "surface": "Operations > System / Data Health",
            "primary_operations": True,
            "decision": "keep_primary_improve",
            "role": "실행 상태, 실패 artifact, log, 데이터 / 시스템 triage를 담당합니다.",
            "change": "primary system health 화면으로 유지합니다. 실제 수집 실행은 Ingestion 또는 replay 도구에서 처리합니다.",
        },
        {
            "surface_key": "backtest_run_history",
            "surface": "Operations > Archive: Backtest Runs",
            "primary_operations": False,
            "decision": "keep_as_archive_recovery",
            "role": "과거 backtest run을 복구 / 감사하고 필요할 때 form을 복원합니다.",
            "change": "삭제하지 않음. primary operations 아래의 복구 도구로 유지합니다.",
        },
        {
            "surface_key": "candidate_library",
            "surface": "Operations > Archive: Candidates",
            "primary_operations": False,
            "decision": "keep_as_archive_recovery",
            "role": "legacy / current / pre-live candidate snapshot을 확인하고 result curve를 재생성합니다.",
            "change": "삭제하지 않음. primary operations 아래의 후보 archive 도구로 유지합니다.",
        },
        {
            "surface_key": "reference_reports",
            "surface": "Reference > Guides",
            "primary_operations": False,
            "decision": "keep_reference_future_reports",
            "role": "workflow 의미와 향후 수동 report handoff 기준을 설명합니다.",
            "change": "Reference로 유지합니다. report export 구현은 이후 별도 범위입니다.",
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
                "title": "포트폴리오 blocker 확인 필요",
                "tone": "danger",
                "target_key": "portfolio_monitoring",
                "target_surface": "Operations > Portfolio Monitoring",
                "reason": f"차단된 row: {blocked_count}개, 누락된 reference: {missing_count}개입니다.",
                "next_action": "Portfolio Monitoring을 열고 차단되었거나 누락된 selected reference를 먼저 확인합니다.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    elif watch_count:
        actions.append(
            {
                "key": "review_portfolio_monitoring",
                "title": "포트폴리오 모니터링 검토 필요",
                "tone": "warning",
                "target_key": "portfolio_monitoring",
                "target_surface": "Operations > Portfolio Monitoring",
                "reason": f"{watch_count}개 selected row가 관찰 / 리밸런싱 검토 / 재검토 후보입니다.",
                "next_action": "Portfolio Monitoring을 열고 target snapshot, review signal, open issue를 확인합니다.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    elif dashboard_rows:
        actions.append(
            {
                "key": "routine_portfolio_monitoring",
                "title": "포트폴리오 일상 점검 가능",
                "tone": "positive",
                "target_key": "portfolio_monitoring",
                "target_surface": "Operations > Portfolio Monitoring",
                "reason": f"{dashboard_rows}개 모니터링 후보 row를 일상 점검할 수 있습니다.",
                "next_action": "모니터링 scenario를 새로 계산하거나 상태를 확인할 때 Portfolio Monitoring을 엽니다.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    else:
        actions.append(
            {
                "key": "no_selected_rows",
                "title": "선정된 모니터링 row 없음",
                "tone": "neutral",
                "target_key": "reference_guides",
                "target_surface": "Reference > Guides",
                "reason": "아직 Final Review에서 selected monitoring row가 만들어지지 않았습니다.",
                "next_action": "먼저 Backtest -> Final Review에서 모니터링 후보를 저장합니다.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )

    normalized_status = str(latest_status or "").strip().lower()
    if normalized_status not in {"success", "no runs"}:
        actions.append(
            {
                "key": "inspect_system_data_health",
                "title": "시스템 / 데이터 상태 확인 필요",
                "tone": "danger" if "fail" in normalized_status or normalized_status in {"failed", "failure", "error"} else "warning",
                "target_key": "system_data_health",
                "target_surface": "Operations > System / Data Health",
                "reason": f"최근 실행 상태는 {latest_status or '-'}이고, 확인 가능한 run은 {run_history_count}개입니다.",
                "next_action": "최신 monitoring evidence를 신뢰하기 전에 System / Data Health를 먼저 확인합니다.",
                "execution_boundary": _disabled_action_boundary(),
            }
        )
    if run_history_count or candidate_count:
        actions.append(
            {
                "key": "archive_recovery_available",
                "title": "Archive / Recovery 도구 사용 가능",
                "tone": "neutral",
                "target_key": "archive_backtest_runs" if run_history_count else "archive_candidates",
                "target_surface": "Operations > Archive / Recovery",
                "reason": f"Backtest run {run_history_count}개, candidate snapshot {candidate_count}개를 확인할 수 있습니다.",
                "next_action": "이전 작업을 복구하거나 감사할 때만 archive 도구를 사용합니다.",
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
            "detail": "Final Review에서 선정된 모니터링 후보와 사용자 portfolio setup을 확인합니다.",
            "metrics": {
                "selected_decision_count": selected_count,
                "dashboard_row_count": dashboard_rows,
                "portfolio_count": portfolio_count,
                "assigned_strategy_count": assigned_count,
                "watch_or_review_count": watch_count,
                "blocked_count": blocked_count,
                "missing_reference_count": missing_count,
            },
            "links": [{"target_key": "portfolio_monitoring", "label": "Portfolio Monitoring 열기", "icon": "📊"}],
        },
        {
            "key": "system_data_health",
            "title": "System / Data Health",
            "priority": "primary",
            "status": system_status,
            "tone": _system_tone(latest_status),
            "target_surface": "Operations > System / Data Health",
            "detail": "실행 상태, 실패 artifact, log, ingestion handoff를 확인합니다.",
            "metrics": {
                "run_count": len(run_history),
                "latest_job": latest_run.get("job_name") or "-",
                "latest_status": latest_status,
            },
            "links": [{"target_key": "system_data_health", "label": "System / Data Health 열기", "icon": "🧾"}],
        },
        {
            "key": "archive_recovery",
            "title": "Archive / Recovery",
            "priority": "secondary",
            "status": "Available" if run_history or candidate_records else "Empty",
            "tone": "neutral",
            "target_surface": "Operations > Archive / Recovery",
            "detail": "복구가 필요할 때 과거 backtest를 다시 열고 저장 후보를 확인합니다.",
            "metrics": {
                "backtest_run_count": len(run_history),
                "candidate_count": len(candidate_records),
            },
            "links": [
                {"target_key": "archive_backtest_runs", "label": "Backtest Runs 열기", "icon": "🗂️"},
                {"target_key": "archive_candidates", "label": "Candidates 열기", "icon": "📌"},
            ],
        },
        {
            "key": "reference_reports",
            "title": "Reference / Reports",
            "priority": "secondary",
            "status": "Guide Ready",
            "tone": "neutral",
            "target_surface": "Reference > Guides",
            "detail": "workflow 의미, 판단 경계, 향후 report handoff 기준을 확인합니다.",
            "metrics": {
                "report_export": "Planned",
                "guide": "Available",
            },
            "links": [{"target_key": "reference_guides", "label": "Guides 열기", "icon": "📚"}],
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
    mapping = {
        "success": "성공",
        "failed": "실패",
        "failure": "실패",
        "error": "오류",
        "partial_success": "부분 성공",
        "warning": "주의",
        "review_required": "검토 필요",
        "No runs": "실행 기록 없음",
        "Planned": "예정",
        "Available": "사용 가능",
    }
    text = str(value or "-")
    return mapping.get(text, text)


def _status_label(value: Any) -> str:
    mapping = {
        "No Selected Rows": "선정 row 없음",
        "Blocked": "차단",
        "Review Needed": "검토 필요",
        "Ready": "준비됨",
        "Healthy": "정상",
        "No Runs": "실행 기록 없음",
        "Attention Needed": "확인 필요",
        "Available": "사용 가능",
        "Empty": "비어 있음",
        "Guide Ready": "가이드 준비됨",
    }
    return mapping.get(str(value or ""), str(value or "-"))


def _priority_label(value: Any) -> str:
    mapping = {"primary": "주요", "secondary": "보조"}
    return mapping.get(str(value or ""), str(value or "-"))


def _metric_label(value: str) -> str:
    mapping = {
        "selected_decision_count": "선정 후보",
        "dashboard_row_count": "Dashboard Row",
        "portfolio_count": "Portfolio",
        "assigned_strategy_count": "배정 전략",
        "watch_or_review_count": "검토 필요",
        "blocked_count": "차단",
        "missing_reference_count": "누락 Reference",
        "run_count": "실행 기록",
        "latest_job": "최근 Job",
        "latest_status": "최근 상태",
        "backtest_run_count": "Backtest Run",
        "candidate_count": "Candidate",
        "report_export": "Report Export",
        "guide": "Guide",
    }
    return mapping.get(value, value.replace("_", " ").title())


def _lane_cards(model: dict[str, Any]) -> list[dict[str, Any]]:
    cards: list[dict[str, Any]] = []
    for lane in list(model.get("lanes") or []):
        cards.append(
            {
                "title": lane.get("title"),
                "value": _status_label(lane.get("status")),
                "detail": lane.get("target_surface"),
                "tone": lane.get("tone"),
            }
        )
    return cards


def _render_lane(lane: dict[str, Any], *, page_targets: dict[str, Any]) -> None:
    with st.container(border=True):
        render_badge_strip(
            [
                {"label": "구분", "value": _priority_label(lane.get("priority")), "tone": "positive" if lane.get("priority") == "primary" else "neutral"},
                {"label": "상태", "value": _status_label(lane.get("status")), "tone": lane.get("tone")},
            ]
        )
        st.markdown(f"#### {lane.get('title') or '-'}")
        st.caption(str(lane.get("detail") or ""))
        metric_items = list(dict(lane.get("metrics") or {}).items())[:4]
        if metric_items:
            columns = st.columns(len(metric_items), gap="small")
            for column, (label, value) in zip(columns, metric_items):
                column.metric(_metric_label(str(label)), _format_metric_value(value))
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
                    {"label": "점검 항목", "value": action.get("title"), "tone": action.get("tone")},
                    {"label": "이동 위치", "value": action.get("target_surface"), "tone": "neutral"},
                    {"label": "주문 / 자동 리밸런싱", "value": "비활성", "tone": "neutral"},
                ]
            )
            st.caption(str(action.get("reason") or ""))
            st.markdown(f"**다음 행동:** {action.get('next_action') or '-'}")
            target = page_targets.get(str(action.get("target_key") or ""))
            if target is not None:
                st.page_link(target, label=f"{action.get('target_surface')} 열기", use_container_width=True)


def _render_stage_roadmap(model: dict[str, Any]) -> None:
    with st.expander("Operations restructuring roadmap", expanded=False):
        st.caption("이 화면은 1차 보강에서 끝난 것이 아니라 2~5차까지 반영한 최종 Operations Console 기준입니다.")
        rows = []
        for row in list(model.get("stage_roadmap") or []):
            rows.append(
                {
                    "차수": row.get("stage"),
                    "제목": row.get("title"),
                    "상태": "완료" if row.get("status") == "completed" else row.get("status"),
                    "산출물": row.get("output"),
                }
            )
        st.dataframe(rows, width="stretch", hide_index=True)


def _render_surface_audit(model: dict[str, Any]) -> None:
    with st.expander("Operations surface audit / keep-improve-archive decisions", expanded=False):
        st.caption("삭제가 아니라 유지 / 개선 / archive 격하 기준을 먼저 고정한 감사표입니다.")
        decision_labels = {
            "keep_primary_improve": "주요 화면으로 유지 / 개선",
            "keep_as_archive_recovery": "Archive / Recovery로 보존",
            "keep_reference_future_reports": "Reference로 유지 / report는 후속 범위",
        }
        rows = []
        for row in list(model.get("surface_audit") or []):
            rows.append(
                {
                    "화면": row.get("surface"),
                    "주요 운영 화면": "예" if row.get("primary_operations") else "아니오",
                    "결정": decision_labels.get(str(row.get("decision") or ""), row.get("decision")),
                    "역할": row.get("role"),
                    "변경 내용": row.get("change"),
                }
            )
        st.dataframe(rows, width="stretch", hide_index=True)


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
            {"label": "Live Approval", "value": "비활성", "tone": "neutral"},
            {"label": "Order", "value": "비활성", "tone": "neutral"},
            {"label": "Auto Rebalance", "value": "비활성", "tone": "neutral"},
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
