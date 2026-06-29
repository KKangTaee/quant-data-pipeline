from __future__ import annotations

from calendar import monthrange
from datetime import date, datetime
from typing import Any

import streamlit as st

from app.jobs.run_history import load_run_history
from app.runtime.final_selected_portfolios import load_final_selected_portfolio_dashboard
from app.web.backtest_ui_components import render_badge_strip, render_status_card_grid
from app.web.reference_contextual_help import render_reference_contextual_help


OPERATIONS_OVERVIEW_SCHEMA_VERSION = "operations_overview_v2"
OPERATIONS_CONSOLE_VERSION = "operations_console_v2"
OPERATIONS_PORTFOLIO_SUMMARY_SCHEMA_VERSION = "operations_portfolio_summary_v1"
OPERATIONS_EVIDENCE_HEALTH_SCHEMA_VERSION = "operations_evidence_health_v1"
OPERATIONS_REVIEW_QUEUE_SCHEMA_VERSION = "operations_review_queue_v1"


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


def _parse_date_value(value: Any) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    text = str(value or "").strip()
    if not text or text in {"-", "NaT", "nan", "None"}:
        return None
    candidates = [text]
    if len(text) >= 10:
        candidates.append(text[:10])
    for candidate in candidates:
        normalized = candidate.replace("/", "-")
        try:
            return datetime.fromisoformat(normalized.replace("Z", "+00:00")).date()
        except ValueError:
            pass
        for fmt in ("%Y-%m-%d", "%Y%m%d"):
            try:
                return datetime.strptime(normalized, fmt).date()
            except ValueError:
                continue
    return None


def _format_date_value(value: Any) -> str:
    parsed = _parse_date_value(value)
    return parsed.isoformat() if parsed else "-"


def _latest_date_text(values: list[Any]) -> str:
    parsed_values = [parsed for parsed in (_parse_date_value(value) for value in values) if parsed is not None]
    return max(parsed_values).isoformat() if parsed_values else "-"


def _earliest_date_text(values: list[Any]) -> str:
    parsed_values = [parsed for parsed in (_parse_date_value(value) for value in values) if parsed is not None]
    return min(parsed_values).isoformat() if parsed_values else "-"


def _next_month_end(value: Any, interval: int = 1) -> str:
    parsed = _parse_date_value(value)
    if parsed is None:
        return "-"
    month_offset = max(_safe_int(interval), 1)
    month_index = parsed.month + month_offset
    year = parsed.year + ((month_index - 1) // 12)
    month = ((month_index - 1) % 12) + 1
    return date(year, month, monthrange(year, month)[1]).isoformat()


def _portfolio_strategy_rows(portfolio_state: dict[str, Any]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for portfolio in list(portfolio_state.get("portfolios") or []):
        for row in list(dict(portfolio or {}).get("strategy_rows") or []):
            if isinstance(row, dict):
                rows.append(dict(row))
    return rows


def _nested_dict(row: dict[str, Any], *keys: str) -> dict[str, Any]:
    for key in keys:
        value = row.get(key)
        if isinstance(value, dict):
            return dict(value)
    return {}


def _scenario_status(row: dict[str, Any]) -> str:
    for key in ("scenario_status", "monitoring_scenario_status", "scenario_freshness", "latest_scenario_status"):
        text = str(row.get(key) or "").strip().lower()
        if text:
            return text
    for nested_key in ("latest_scenario", "scenario", "latest_recheck_result"):
        nested = _nested_dict(row, nested_key)
        if bool(nested.get("stale")):
            return "stale"
        text = str(nested.get("status") or nested.get("freshness") or "").strip().lower()
        if text:
            return text
    if bool(row.get("scenario_stale")):
        return "stale"
    return ""


def _scenario_dates(row: dict[str, Any]) -> list[Any]:
    values: list[Any] = [
        row.get("latest_scenario_date"),
        row.get("scenario_updated_at"),
        row.get("scenario_as_of"),
        row.get("dashboard_updated_at"),
    ]
    for nested_key in ("latest_scenario", "scenario", "latest_recheck_result"):
        nested = _nested_dict(row, nested_key)
        values.extend(
            [
                nested.get("date"),
                nested.get("as_of"),
                nested.get("updated_at"),
                nested.get("dashboard_updated_at"),
            ]
        )
    return values


def _selected_components(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw_decision = dict(row.get("raw_decision") or {})
    components = raw_decision.get("selected_components")
    if components is None:
        components = row.get("selected_components")
    return [dict(component or {}) for component in list(components or []) if isinstance(component, dict)]


def _component_snapshot_date(component: dict[str, Any]) -> str:
    history = [dict(item or {}) for item in list(component.get("selection_history") or []) if isinstance(item, dict)]
    latest = history[-1] if history else {}
    return _format_date_value(latest.get("date") or component.get("period_end"))


def _component_review_interval(component: dict[str, Any]) -> int:
    replay_contract = dict(component.get("replay_contract") or {})
    settings = dict(replay_contract.get("settings_snapshot") or {})
    return max(_safe_int(settings.get("rebalance_interval") or settings.get("interval") or 1), 1)


def _open_review_item_count(strategy_rows: list[dict[str, Any]]) -> int:
    total = 0
    for row in strategy_rows:
        raw_decision = dict(row.get("raw_decision") or {})
        total += len([item for item in list(row.get("open_review_items") or raw_decision.get("open_review_items") or []) if item])
        total += len([item for item in list(row.get("blockers") or raw_decision.get("blockers") or []) if item])
    return total


def _selected_policy_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    raw_decision = dict(row.get("raw_decision") or {})
    packet = dict(raw_decision.get("investability_evidence_packet") or row.get("investability_evidence_packet") or {})
    return dict(
        raw_decision.get("selection_gate_policy_snapshot")
        or raw_decision.get("gate_policy_snapshot")
        or packet.get("selection_gate_policy_snapshot")
        or packet.get("gate_policy_snapshot")
        or {}
    )


def _policy_status(policy: dict[str, Any]) -> str:
    if not policy:
        return "NEEDS_INPUT"
    outcome = str(policy.get("outcome") or policy.get("route") or "").strip().upper()
    if policy.get("select_allowed") is False or "BLOCK" in outcome or policy.get("blockers"):
        return "BLOCKED"
    if any(token in outcome for token in ("NEEDS_INPUT", "NEEDS_DATA", "MISSING", "NOT_RUN")):
        return "NEEDS_INPUT"
    if policy.get("review_required"):
        return "REVIEW"
    if policy.get("select_allowed") is True or any(token in outcome for token in ("ALLOW", "READY", "PASS", "CLEAR")):
        return "PASS"
    return "REVIEW"


def _health_tone(status: str) -> str:
    mapping = {
        "PASS": "positive",
        "REVIEW": "warning",
        "NEEDS_INPUT": "warning",
        "BLOCKED": "danger",
    }
    return mapping.get(status, "neutral")


def _system_run_status(latest_status: str, run_history_count: int) -> str:
    normalized = str(latest_status or "").strip().lower()
    if run_history_count <= 0 or normalized == "no runs":
        return "NEEDS_INPUT"
    if normalized == "success":
        return "PASS"
    if normalized in {"partial_success", "warning", "review_required"}:
        return "REVIEW"
    if normalized in {"failed", "failure", "error"} or "fail" in normalized:
        return "BLOCKED"
    return "REVIEW"


def _overall_evidence_health_status(items: list[dict[str, Any]]) -> tuple[str, str]:
    statuses = {str(item.get("status") or "") for item in items}
    if "BLOCKED" in statuses:
        return "Blocked", "danger"
    if "NEEDS_INPUT" in statuses:
        return "Needs Input", "warning"
    if "REVIEW" in statuses:
        return "Review Needed", "warning"
    return "Ready", "positive"


def _build_portfolio_summary(
    *,
    dashboard_rows: int,
    selected_count: int,
    assigned_count: int,
    blocked_count: int,
    missing_count: int,
    portfolio_state: dict[str, Any],
    portfolio_metrics: dict[str, Any],
) -> dict[str, Any]:
    strategy_rows = _portfolio_strategy_rows(portfolio_state)
    scenario_statuses = [_scenario_status(row) for row in strategy_rows]
    stale_scenario_count = sum(1 for status in scenario_statuses if status in {"stale", "outdated", "expired"})
    current_scenario_count = sum(1 for status in scenario_statuses if status in {"current", "fresh", "good", "ready"})
    pending_scenario_count = sum(
        1
        for row, status in zip(strategy_rows, scenario_statuses)
        if bool(row.get("slot_input_complete", True)) and not status and _latest_date_text(_scenario_dates(row)) == "-"
    )
    incomplete_strategy_slot_count = _safe_int(portfolio_metrics.get("incomplete_strategy_slot_count"))
    open_review_item_count = _open_review_item_count(strategy_rows)

    snapshot_dates: list[Any] = []
    next_review_dates: list[Any] = []
    for row in strategy_rows:
        for component in _selected_components(row):
            snapshot_date = _component_snapshot_date(component)
            snapshot_dates.append(snapshot_date)
            next_review_dates.append(_next_month_end(snapshot_date, interval=_component_review_interval(component)))

    if dashboard_rows <= 0:
        status = "No Selected Rows"
        tone = "neutral"
        detail = "Final Review에서 선정된 monitoring row가 아직 없습니다."
    elif _safe_int(portfolio_metrics.get("portfolio_count")) <= 0:
        status = "Setup Needed"
        tone = "warning"
        detail = "선정 row는 있지만 monitoring portfolio setup이 아직 없습니다."
    elif blocked_count or missing_count or incomplete_strategy_slot_count:
        status = "Blocked"
        tone = "danger"
        detail = "차단 / 누락 reference / 설정 보강 항목을 먼저 확인해야 합니다."
    elif stale_scenario_count or pending_scenario_count or open_review_item_count:
        status = "Review Needed"
        tone = "warning"
        detail = "scenario freshness나 open review 항목 확인이 필요합니다."
    else:
        status = "Ready"
        tone = "positive"
        detail = "일상 portfolio monitoring 점검을 바로 진행할 수 있습니다."

    return {
        "schema_version": OPERATIONS_PORTFOLIO_SUMMARY_SCHEMA_VERSION,
        "status": status,
        "tone": tone,
        "detail": detail,
        "selected_decision_count": selected_count,
        "dashboard_row_count": dashboard_rows,
        "active_portfolio_count": _safe_int(portfolio_metrics.get("portfolio_count")),
        "assigned_strategy_count": assigned_count,
        "complete_strategy_slot_count": _safe_int(portfolio_metrics.get("complete_strategy_slot_count")),
        "incomplete_strategy_slot_count": incomplete_strategy_slot_count,
        "stale_scenario_count": stale_scenario_count,
        "current_scenario_count": current_scenario_count,
        "pending_scenario_count": pending_scenario_count,
        "blocked_count": blocked_count,
        "missing_reference_count": missing_count,
        "open_review_item_count": open_review_item_count,
        "latest_scenario_date": _latest_date_text([value for row in strategy_rows for value in _scenario_dates(row)]),
        "target_snapshot_date": _latest_date_text(snapshot_dates),
        "next_review_date": _earliest_date_text(next_review_dates),
        "execution_boundary": _disabled_action_boundary(),
    }


def _build_evidence_health(
    *,
    portfolio_summary: dict[str, Any],
    portfolio_state: dict[str, Any],
    latest_status: str,
    run_history_count: int,
) -> dict[str, Any]:
    strategy_rows = _portfolio_strategy_rows(portfolio_state)
    stale_scenario_count = _safe_int(portfolio_summary.get("stale_scenario_count"))
    pending_scenario_count = _safe_int(portfolio_summary.get("pending_scenario_count"))
    scenario_status = "REVIEW" if stale_scenario_count or pending_scenario_count else "PASS"
    if not strategy_rows and _safe_int(portfolio_summary.get("dashboard_row_count")) > 0:
        scenario_status = "NEEDS_INPUT"

    policy_statuses = [_policy_status(_selected_policy_snapshot(row)) for row in strategy_rows]
    ready_count = sum(1 for status in policy_statuses if status == "PASS")
    if not policy_statuses:
        selected_evidence_status = "NEEDS_INPUT"
    elif "BLOCKED" in policy_statuses:
        selected_evidence_status = "BLOCKED"
    elif "NEEDS_INPUT" in policy_statuses:
        selected_evidence_status = "NEEDS_INPUT"
    elif "REVIEW" in policy_statuses:
        selected_evidence_status = "REVIEW"
    else:
        selected_evidence_status = "PASS"

    open_review_count = _safe_int(portfolio_summary.get("open_review_item_count"))
    blocking_setup_count = (
        _safe_int(portfolio_summary.get("blocked_count"))
        + _safe_int(portfolio_summary.get("missing_reference_count"))
        + _safe_int(portfolio_summary.get("incomplete_strategy_slot_count"))
    )
    if blocking_setup_count:
        open_review_status = "BLOCKED"
    elif open_review_count:
        open_review_status = "REVIEW"
    else:
        open_review_status = "PASS"

    system_status = _system_run_status(latest_status, run_history_count)
    items = [
        {
            "key": "scenario_freshness",
            "label": "Scenario Freshness",
            "status": scenario_status,
            "tone": _health_tone(scenario_status),
            "value": f"{stale_scenario_count} stale / {pending_scenario_count} pending",
            "detail": f"latest={portfolio_summary.get('latest_scenario_date') or '-'}",
            "target_surface": "Operations > Portfolio Monitoring",
        },
        {
            "key": "selected_evidence",
            "label": "Selected Evidence",
            "status": selected_evidence_status,
            "tone": _health_tone(selected_evidence_status),
            "value": f"{ready_count}/{len(policy_statuses)} ready",
            "detail": "Final Review selected-route evidence snapshot",
            "target_surface": "Backtest > Final Review / Operations > Portfolio Monitoring",
        },
        {
            "key": "open_review",
            "label": "Open Review",
            "status": open_review_status,
            "tone": _health_tone(open_review_status),
            "value": f"{open_review_count} open",
            "detail": f"blocking setup={blocking_setup_count}",
            "target_surface": "Operations > Portfolio Monitoring",
        },
        {
            "key": "system_run_health",
            "label": "System Run Health",
            "status": system_status,
            "tone": _health_tone(system_status),
            "value": str(latest_status or "No runs"),
            "detail": f"run history={run_history_count}",
            "target_surface": "Operations > System / Data Health",
        },
    ]
    overall_status, overall_tone = _overall_evidence_health_status(items)
    return {
        "schema_version": OPERATIONS_EVIDENCE_HEALTH_SCHEMA_VERSION,
        "overall_status": overall_status,
        "overall_tone": overall_tone,
        "items": items,
        "execution_boundary": _disabled_action_boundary(),
    }


def _disabled_action_boundary() -> dict[str, bool]:
    return {
        "live_approval": False,
        "broker_order": False,
        "account_sync": False,
        "order_instruction": False,
        "auto_rebalance": False,
        "registry_write": False,
    }


def _queue_action(
    *,
    key: str,
    title: str,
    tone: str,
    priority: str,
    sort_rank: int,
    evidence_key: str,
    summary_metric: str,
    target_key: str,
    target_surface: str,
    reason: str,
    next_action: str,
) -> dict[str, Any]:
    return {
        "key": key,
        "title": title,
        "tone": tone,
        "priority": priority,
        "sort_rank": sort_rank,
        "evidence_key": evidence_key,
        "summary_metric": summary_metric,
        "target_key": target_key,
        "target_surface": target_surface,
        "reason": reason,
        "next_action": next_action,
        "execution_boundary": _disabled_action_boundary(),
    }


def _build_action_queue(
    *,
    dashboard_rows: int,
    watch_count: int,
    blocked_count: int,
    missing_count: int,
    portfolio_summary: dict[str, Any],
    latest_status: str,
    run_history_count: int,
) -> list[dict[str, Any]]:
    actions: list[dict[str, Any]] = []
    incomplete_slot_count = _safe_int(portfolio_summary.get("incomplete_strategy_slot_count"))
    blocking_setup_count = blocked_count + missing_count + incomplete_slot_count
    stale_scenario_count = _safe_int(portfolio_summary.get("stale_scenario_count"))
    pending_scenario_count = _safe_int(portfolio_summary.get("pending_scenario_count"))
    open_review_count = _safe_int(portfolio_summary.get("open_review_item_count"))

    if blocking_setup_count:
        actions.append(
            _queue_action(
                key="resolve_monitoring_setup_blockers",
                title="포트폴리오 설정 blocker 먼저 확인",
                tone="danger",
                priority="P0",
                sort_rank=10,
                evidence_key="open_review",
                summary_metric=f"{blocking_setup_count} blockers",
                target_key="portfolio_monitoring",
                target_surface="Operations > Portfolio Monitoring",
                reason=f"차단된 row {blocked_count}개, 누락 reference {missing_count}개, 미완료 slot {incomplete_slot_count}개입니다.",
                next_action="Portfolio Monitoring을 열고 차단 / 누락 / 미완료 strategy slot을 먼저 정리합니다.",
            )
        )

    normalized_status = str(latest_status or "").strip().lower()
    if normalized_status not in {"success", "no runs"}:
        failed_system = "fail" in normalized_status or normalized_status in {"failed", "failure", "error"}
        actions.append(
            _queue_action(
                key="inspect_system_data_health",
                title="시스템 / 데이터 상태 확인 필요",
                tone="danger" if failed_system else "warning",
                priority="P0" if failed_system else "P2",
                sort_rank=15 if failed_system else 35,
                evidence_key="system_run_health",
                summary_metric=str(latest_status or "-"),
                target_key="system_data_health",
                target_surface="Operations > System / Data Health",
                reason=f"최근 실행 상태는 {latest_status or '-'}이고, 확인 가능한 run은 {run_history_count}개입니다.",
                next_action="최신 monitoring evidence를 신뢰하기 전에 System / Data Health를 확인합니다.",
            )
        )

    if stale_scenario_count or pending_scenario_count:
        actions.append(
            _queue_action(
                key="refresh_monitoring_scenarios",
                title="모니터링 scenario freshness 확인",
                tone="warning",
                priority="P1",
                sort_rank=20,
                evidence_key="scenario_freshness",
                summary_metric=f"{stale_scenario_count} stale / {pending_scenario_count} pending",
                target_key="portfolio_monitoring",
                target_surface="Operations > Portfolio Monitoring",
                reason=f"stale scenario {stale_scenario_count}개, pending scenario {pending_scenario_count}개가 있습니다.",
                next_action="Portfolio Monitoring에서 pending / stale strategy의 scenario update 필요 여부를 확인합니다.",
            )
        )

    if open_review_count or watch_count:
        actions.append(
            _queue_action(
                key="review_portfolio_monitoring",
                title="포트폴리오 모니터링 검토 필요",
                tone="warning",
                priority="P2",
                sort_rank=30,
                evidence_key="open_review",
                summary_metric=f"{open_review_count} open review",
                target_key="portfolio_monitoring",
                target_surface="Operations > Portfolio Monitoring",
                reason=f"{open_review_count}개 open review와 {watch_count}개 관찰 / 재검토 row가 있습니다.",
                next_action="Portfolio Monitoring을 열고 review signal, open issue, target snapshot을 확인합니다.",
            )
        )

    has_portfolio_action = any(action.get("target_key") == "portfolio_monitoring" for action in actions)
    if dashboard_rows and not has_portfolio_action:
        actions.append(
            _queue_action(
                key="routine_portfolio_monitoring",
                title="포트폴리오 일상 점검 가능",
                tone="positive",
                priority="P3",
                sort_rank=50,
                evidence_key="selected_evidence",
                summary_metric=f"{dashboard_rows} selected rows",
                target_key="portfolio_monitoring",
                target_surface="Operations > Portfolio Monitoring",
                reason=f"{dashboard_rows}개 모니터링 후보 row를 일상 점검할 수 있습니다.",
                next_action="모니터링 scenario를 새로 계산하거나 상태를 확인할 때 Portfolio Monitoring을 엽니다.",
            )
        )
    elif dashboard_rows <= 0:
        actions.append(
            _queue_action(
                key="no_selected_rows",
                title="선정된 모니터링 row 없음",
                tone="neutral",
                priority="P3",
                sort_rank=60,
                evidence_key="selected_evidence",
                summary_metric="0 selected rows",
                target_key="reference_guides",
                target_surface="Reference > Guides",
                reason="아직 Final Review에서 selected monitoring row가 만들어지지 않았습니다.",
                next_action="먼저 Backtest -> Final Review에서 모니터링 후보를 저장합니다.",
            )
        )

    return sorted(actions, key=lambda action: (_safe_int(action.get("sort_rank")), str(action.get("key") or "")))[:4]


def build_operations_overview_model(
    *,
    selected_dashboard: dict[str, Any],
    run_history: list[dict[str, Any]],
    candidate_records: list[dict[str, Any]] | None = None,
) -> dict[str, Any]:
    """Build a Streamlit-free operator model for the Operations landing page."""

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
    portfolio_summary = _build_portfolio_summary(
        dashboard_rows=dashboard_rows,
        selected_count=selected_count,
        assigned_count=assigned_count,
        blocked_count=blocked_count,
        missing_count=missing_count,
        portfolio_state=portfolio_state,
        portfolio_metrics=portfolio_metrics,
    )

    latest_run = dict(run_history[0] if run_history else {})
    latest_status = str(latest_run.get("status") or "No runs")
    system_status = "Healthy" if latest_status.lower() == "success" else ("No Runs" if not run_history else "Attention Needed")
    evidence_health = _build_evidence_health(
        portfolio_summary=portfolio_summary,
        portfolio_state=portfolio_state,
        latest_status=latest_status,
        run_history_count=len(run_history),
    )

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
    ]
    return {
        "schema_version": OPERATIONS_OVERVIEW_SCHEMA_VERSION,
        "console_version": OPERATIONS_CONSOLE_VERSION,
        "operations_model": "Portfolio Monitoring + System/Data Health",
        "portfolio_summary": portfolio_summary,
        "evidence_health": evidence_health,
        "lanes": lanes,
        "action_queue_schema_version": OPERATIONS_REVIEW_QUEUE_SCHEMA_VERSION,
        "action_queue": _build_action_queue(
            dashboard_rows=dashboard_rows,
            watch_count=watch_count,
            blocked_count=blocked_count,
            missing_count=missing_count,
            portfolio_summary=portfolio_summary,
            latest_status=latest_status,
            run_history_count=len(run_history),
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
        "Setup Needed": "설정 필요",
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


def _render_portfolio_summary(model: dict[str, Any]) -> None:
    summary = dict(model.get("portfolio_summary") or {})
    st.markdown("### Portfolio Monitoring Status")
    st.caption("현재 monitoring portfolio setup과 selected strategy 상태를 먼저 요약합니다. 주문, 계좌 연동, 자동 리밸런싱은 만들지 않습니다.")
    with st.container(border=True):
        render_badge_strip(
            [
                {"label": "Status", "value": _status_label(summary.get("status")), "tone": summary.get("tone")},
                {
                    "label": "Scenario Freshness",
                    "value": f"{_format_metric_value(summary.get('stale_scenario_count'))} stale / {_format_metric_value(summary.get('pending_scenario_count'))} pending",
                    "tone": "warning" if _safe_int(summary.get("stale_scenario_count")) or _safe_int(summary.get("pending_scenario_count")) else "positive",
                },
                {"label": "Execution", "value": "Read-only", "tone": "neutral"},
            ]
        )
        st.caption(str(summary.get("detail") or ""))
        top_columns = st.columns(4, gap="small")
        top_columns[0].metric("Active Portfolios", _format_metric_value(summary.get("active_portfolio_count")))
        top_columns[1].metric("Assigned Strategies", _format_metric_value(summary.get("assigned_strategy_count")))
        top_columns[2].metric("Blocked / Missing", f"{_format_metric_value(summary.get('blocked_count'))} / {_format_metric_value(summary.get('missing_reference_count'))}")
        top_columns[3].metric("Incomplete Slots", _format_metric_value(summary.get("incomplete_strategy_slot_count")))

        bottom_columns = st.columns(4, gap="small")
        bottom_columns[0].metric("Stale Scenarios", _format_metric_value(summary.get("stale_scenario_count")))
        bottom_columns[1].metric("Open Review", _format_metric_value(summary.get("open_review_item_count")))
        bottom_columns[2].metric("Target Snapshot", _format_metric_value(summary.get("target_snapshot_date")))
        bottom_columns[3].metric("Next Review", _format_metric_value(summary.get("next_review_date")))


def _render_evidence_health_strip(model: dict[str, Any]) -> None:
    evidence = dict(model.get("evidence_health") or {})
    items = [dict(item or {}) for item in list(evidence.get("items") or [])]
    st.markdown("### Evidence Health")
    st.caption("운영 판단에 쓰는 근거가 바로 읽을 수 있는 상태인지 요약합니다. provider DB 세부 조회나 새 수집은 여기서 실행하지 않습니다.")
    render_badge_strip(
        [
            {"label": "Overall", "value": _status_label(evidence.get("overall_status")), "tone": evidence.get("overall_tone")},
            {"label": "Write Boundary", "value": "No registry / no order", "tone": "neutral"},
        ]
    )
    if not items:
        st.caption("표시할 evidence health 항목이 없습니다.")
        return
    columns = st.columns(len(items), gap="small")
    for column, item in zip(columns, items):
        with column.container(border=True):
            render_badge_strip(
                [
                    {"label": "Status", "value": item.get("status"), "tone": item.get("tone")},
                ]
            )
            st.metric(str(item.get("label") or "-"), _format_metric_value(item.get("value")))
            st.caption(str(item.get("detail") or item.get("target_surface") or ""))


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
    st.caption("먼저 확인할 항목만 보여줍니다. 모든 항목은 모니터링 검토 / 시스템 점검용이며 주문이나 자동 리밸런싱을 만들지 않습니다.")
    for action in list(model.get("action_queue") or []):
        with st.container(border=True):
            render_badge_strip(
                [
                    {"label": "Priority", "value": action.get("priority"), "tone": action.get("tone")},
                    {"label": "Evidence", "value": action.get("evidence_key"), "tone": "neutral"},
                    {"label": "Metric", "value": action.get("summary_metric"), "tone": "neutral"},
                    {"label": "주문 / 자동 리밸런싱", "value": "비활성", "tone": "neutral"},
                ]
            )
            st.markdown(f"#### {action.get('title') or '-'}")
            st.caption(str(action.get("reason") or ""))
            st.markdown(f"**다음 행동:** {action.get('next_action') or '-'}")
            target = page_targets.get(str(action.get("target_key") or ""))
            if target is not None:
                st.page_link(target, label=f"{action.get('target_surface')} 열기", use_container_width=True)


def render_operations_overview_page(*, page_targets: dict[str, Any] | None = None) -> None:
    """Render the Operations command center without mutating workflow registries."""

    selected_dashboard = load_final_selected_portfolio_dashboard()
    run_history = load_run_history(limit=30)
    model = build_operations_overview_model(
        selected_dashboard=selected_dashboard,
        run_history=run_history,
    )
    page_targets = dict(page_targets or {})

    st.title("Operations Console")
    st.caption("선정 후 portfolio monitoring 상태와 system/data health를 확인하는 운영 화면입니다.")
    _render_portfolio_summary(model)
    _render_evidence_health_strip(model)
    render_reference_contextual_help("operations_console")
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

    st.markdown("### Primary Operations")
    for lane in primary_lanes:
        _render_lane(lane, page_targets=page_targets)

    with st.expander("Execution Boundary", expanded=False):
        st.json(model.get("execution_boundary") or {})
