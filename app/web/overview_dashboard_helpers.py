from __future__ import annotations

from datetime import datetime
from typing import Any

import pandas as pd

from app.web.runtime import (
    load_backtest_run_history,
    load_candidate_review_notes,
    load_current_candidate_registry_latest,
    load_portfolio_proposals,
    load_pre_live_candidate_registry_latest,
    load_saved_portfolios,
)


# Convert registry numeric fields into a safe float for scoring and display.
def _safe_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


# Normalize metrics that may be stored either as 0.17 or 17.0 percentage-style values.
def _safe_percent_metric(value: Any) -> float | None:
    numeric = _safe_float(value)
    if numeric is None:
        return None
    if -1.0 <= numeric <= 1.0:
        return numeric * 100.0
    return numeric


# Return a stable ISO-ish timestamp string from the common row time fields.
def _row_time(row: dict[str, Any]) -> str:
    return str(row.get("updated_at") or row.get("created_at") or row.get("recorded_at") or "").strip()


# Convert a timestamp-like string into a compact display value without raising on older rows.
def _display_time(value: str) -> str:
    if not value:
        return "-"
    normalized = value.replace("Z", "+00:00")
    try:
        parsed = datetime.fromisoformat(normalized)
    except ValueError:
        return value[:19]
    return parsed.strftime("%Y-%m-%d %H:%M")


# Build a latest pre-live lookup by source current-candidate registry id.
def _pre_live_by_candidate_id(pre_live_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    latest: dict[str, dict[str, Any]] = {}
    for row in pre_live_rows:
        registry_id = str(row.get("source_candidate_registry_id") or "").strip()
        if not registry_id:
            continue
        previous = latest.get(registry_id)
        if previous is None or _row_time(row) >= _row_time(previous):
            latest[registry_id] = row
    return latest


# Score candidates for an overview "review priority" list without treating it as investment advice.
def _candidate_review_priority_score(row: dict[str, Any], pre_live_row: dict[str, Any] | None) -> float:
    result = dict(row.get("result") or {})
    promotion = str(result.get("promotion") or "").lower()
    shortlist = str(result.get("shortlist") or "").lower()
    deployment = str(result.get("deployment") or "").lower()
    record_type = str(row.get("record_type") or "").lower()
    candidate_role = str(row.get("candidate_role") or "").lower()
    pre_live_status = str((pre_live_row or {}).get("pre_live_status") or "not_started").lower()
    cagr = _safe_percent_metric(result.get("cagr"))
    mdd = _safe_percent_metric(result.get("mdd"))

    promotion_score = {
        "real_money_candidate": 2.4,
        "production_candidate": 2.0,
        "candidate": 1.3,
        "hold": -2.5,
    }.get(promotion, 0.4 if promotion else 0.0)
    shortlist_score = {
        "paper_probation": 1.4,
        "paper_tracking": 1.4,
        "watchlist": 0.9,
        "none": 0.0,
    }.get(shortlist, 0.2 if shortlist else 0.0)
    deployment_score = {
        "review_required": 0.9,
        "paper_only": 1.1,
        "watchlist_only": 0.7,
        "blocked": -2.5,
    }.get(deployment, 0.2 if deployment else 0.0)
    pre_live_score = {
        "paper_tracking": 2.0,
        "watchlist": 0.9,
        "scheduled_review": 0.6,
        "re_review": 0.4,
        "hold": -1.5,
        "reject": -2.0,
        "rejected": -2.0,
        "not_started": 0.0,
    }.get(pre_live_status, 0.0)
    record_score = {"current_candidate": 1.0, "near_miss": 0.5, "scenario": 0.2}.get(record_type, 0.0)
    role_score = 0.4 if "current" in candidate_role or "anchor" in candidate_role else 0.0
    cagr_score = min(max(cagr or 0.0, 0.0), 35.0) / 35.0 * 1.2
    mdd_score = 0.0
    if mdd is not None:
        mdd_score = max(0.0, 35.0 - abs(mdd)) / 35.0 * 0.7
    score = promotion_score + shortlist_score + deployment_score + pre_live_score + record_score + role_score + cagr_score + mdd_score
    return round(max(0.0, min(score, 10.0)), 1)


# Build one overview card row for a candidate priority result.
def _candidate_priority_row(row: dict[str, Any], pre_live_row: dict[str, Any] | None) -> dict[str, Any]:
    result = dict(row.get("result") or {})
    registry_id = str(row.get("registry_id") or "")
    pre_live_status = str((pre_live_row or {}).get("pre_live_status") or "not_started")
    if pre_live_status == "paper_tracking":
        next_action = "Portfolio Proposal 또는 Live Readiness 검토"
    elif str(row.get("record_type") or "") == "current_candidate":
        next_action = "Candidate Review에서 Pre-Live 운영 기록 확인"
    else:
        next_action = "Compare에서 상대 근거 재확인"
    return {
        "registry_id": registry_id,
        "title": row.get("title") or registry_id or "-",
        "family": row.get("strategy_family") or "-",
        "role": row.get("candidate_role") or row.get("record_type") or "-",
        "score": _candidate_review_priority_score(row, pre_live_row),
        "cagr": _safe_percent_metric(result.get("cagr")),
        "mdd": _safe_percent_metric(result.get("mdd")),
        "promotion": result.get("promotion") or "-",
        "deployment": result.get("deployment") or "-",
        "pre_live_status": pre_live_status,
        "next_action": next_action,
    }


# Build the top review-priority candidates for the Overview page.
def build_overview_top_candidates(
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
    *,
    limit: int = 3,
) -> list[dict[str, Any]]:
    pre_live_by_id = _pre_live_by_candidate_id(pre_live_rows)
    scored = [
        _candidate_priority_row(row, pre_live_by_id.get(str(row.get("registry_id") or "")))
        for row in current_rows
    ]
    return sorted(scored, key=lambda item: (-float(item["score"]), str(item["title"])))[:limit]


# Build funnel rows for the dashboard status distribution chart.
def build_overview_funnel_rows(
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
    proposal_rows: list[dict[str, Any]],
) -> pd.DataFrame:
    paper_tracking = sum(1 for row in pre_live_rows if str(row.get("pre_live_status") or "") == "paper_tracking")
    watch_or_hold = sum(
        1
        for row in pre_live_rows
        if str(row.get("pre_live_status") or "") in {"watchlist", "hold", "re_review", "scheduled_review"}
    )
    return pd.DataFrame(
        [
            {"Stage": "Current Candidates", "Count": len(current_rows)},
            {"Stage": "Paper Tracking", "Count": paper_tracking},
            {"Stage": "Watch / Hold", "Count": watch_or_hold},
            {"Stage": "Proposal Drafts", "Count": len(proposal_rows)},
        ]
    )


# Build prioritized operator next actions from current registry gaps.
def build_overview_next_actions(
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
    proposal_rows: list[dict[str, Any]],
    history_rows: list[dict[str, Any]],
) -> list[dict[str, Any]]:
    pre_live_by_id = _pre_live_by_candidate_id(pre_live_rows)
    current_without_pre_live = [
        row
        for row in current_rows
        if str(row.get("record_type") or "") == "current_candidate"
        and str(row.get("registry_id") or "") not in pre_live_by_id
    ]
    paper_tracking = [
        row
        for row in pre_live_rows
        if str(row.get("pre_live_status") or "") == "paper_tracking"
    ]
    blocked_candidates = [
        row
        for row in current_rows
        if str(dict(row.get("result") or {}).get("deployment") or "").lower() == "blocked"
        or str(dict(row.get("result") or {}).get("promotion") or "").lower() == "hold"
    ]
    actions: list[dict[str, Any]] = []
    if current_without_pre_live:
        actions.append(
            {
                "priority": "High",
                "title": "Pre-Live 운영 기록이 없는 current 후보 확인",
                "detail": f"{len(current_without_pre_live)}개 current candidate가 아직 paper/watchlist 운영 상태로 저장되지 않았습니다.",
                "target": "Backtest > Candidate Review",
            }
        )
    if paper_tracking and not proposal_rows:
        actions.append(
            {
                "priority": "High",
                "title": "Paper Tracking 후보를 Portfolio Proposal에서 확인",
                "detail": f"{len(paper_tracking)}개 후보가 paper_tracking 상태입니다. 단일 후보 직행 평가 또는 다중 후보 구성안을 확인하세요.",
                "target": "Backtest > Portfolio Proposal",
            }
        )
    if blocked_candidates:
        actions.append(
            {
                "priority": "Medium",
                "title": "Hold / Blocked 후보 정리",
                "detail": f"{len(blocked_candidates)}개 후보가 hold 또는 blocked 신호를 갖고 있습니다.",
                "target": "Backtest > Candidate Review",
            }
        )
    if not history_rows:
        actions.append(
            {
                "priority": "Medium",
                "title": "Backtest run history 생성",
                "detail": "최근 실행 기록이 없습니다. Single Strategy 또는 Compare 실행 후 History에서 재현성을 확인하세요.",
                "target": "Backtest",
            }
        )
    if proposal_rows:
        actions.append(
            {
                "priority": "Low",
                "title": "Saved Proposal feedback 확인",
                "detail": f"{len(proposal_rows)}개 proposal draft가 저장되어 있습니다. Monitoring / Paper Tracking feedback을 확인하세요.",
                "target": "Backtest > Portfolio Proposal",
            }
        )
    if not actions:
        actions.append(
            {
                "priority": "Low",
                "title": "현재 큰 blocker 없음",
                "detail": "후보 / Pre-Live / Proposal 흐름에 즉시 보여줄 빈 구간이 없습니다.",
                "target": "Overview",
            }
        )
    priority_order = {"High": 0, "Medium": 1, "Low": 2}
    return sorted(actions, key=lambda item: priority_order.get(str(item["priority"]), 9))[:5]


# Build a compact activity feed from candidate, pre-live, proposal, and backtest history rows.
def build_overview_activity_rows(
    current_rows: list[dict[str, Any]],
    pre_live_rows: list[dict[str, Any]],
    proposal_rows: list[dict[str, Any]],
    history_rows: list[dict[str, Any]],
    *,
    limit: int = 8,
) -> pd.DataFrame:
    activities: list[dict[str, Any]] = []
    for row in current_rows:
        activities.append(
            {
                "Time": _display_time(_row_time(row)),
                "Sort Time": _row_time(row),
                "Type": "Candidate",
                "Title": row.get("title") or row.get("registry_id") or "-",
                "Status": row.get("record_type") or "-",
            }
        )
    for row in pre_live_rows:
        activities.append(
            {
                "Time": _display_time(_row_time(row)),
                "Sort Time": _row_time(row),
                "Type": "Pre-Live",
                "Title": row.get("title") or row.get("pre_live_id") or "-",
                "Status": row.get("pre_live_status") or "-",
            }
        )
    for row in proposal_rows:
        activities.append(
            {
                "Time": _display_time(_row_time(row)),
                "Sort Time": _row_time(row),
                "Type": "Proposal",
                "Title": row.get("proposal_id") or "-",
                "Status": row.get("proposal_status") or "-",
            }
        )
    for row in history_rows:
        summary = dict(row.get("summary") or {})
        activities.append(
            {
                "Time": _display_time(_row_time(row)),
                "Sort Time": _row_time(row),
                "Type": "Backtest",
                "Title": summary.get("strategy_name") or row.get("strategy_key") or row.get("run_kind") or "-",
                "Status": row.get("run_kind") or "-",
            }
        )
    activities = sorted(activities, key=lambda item: str(item.get("Sort Time") or ""), reverse=True)[:limit]
    return pd.DataFrame([{key: value for key, value in item.items() if key != "Sort Time"} for item in activities])


# Load all durable data sources needed by the Overview dashboard.
def load_overview_dashboard_snapshot() -> dict[str, Any]:
    current_rows = load_current_candidate_registry_latest()
    pre_live_rows = load_pre_live_candidate_registry_latest()
    proposal_rows = load_portfolio_proposals(limit=50)
    history_rows = load_backtest_run_history(limit=30)
    saved_portfolios = load_saved_portfolios(limit=50)
    review_notes = load_candidate_review_notes()
    top_candidates = build_overview_top_candidates(current_rows, pre_live_rows)
    funnel_rows = build_overview_funnel_rows(current_rows, pre_live_rows, proposal_rows)
    next_actions = build_overview_next_actions(current_rows, pre_live_rows, proposal_rows, history_rows)
    activity_rows = build_overview_activity_rows(current_rows, pre_live_rows, proposal_rows, history_rows)
    paper_tracking_count = int((funnel_rows.loc[funnel_rows["Stage"] == "Paper Tracking", "Count"].sum() or 0))
    return {
        "current_rows": current_rows,
        "pre_live_rows": pre_live_rows,
        "proposal_rows": proposal_rows,
        "history_rows": history_rows,
        "saved_portfolios": saved_portfolios,
        "review_notes": review_notes,
        "top_candidates": top_candidates,
        "funnel_rows": funnel_rows,
        "next_actions": next_actions,
        "activity_rows": activity_rows,
        "kpis": {
            "current_candidates": len(current_rows),
            "paper_tracking": paper_tracking_count,
            "proposal_drafts": len(proposal_rows),
            "recent_runs": len(history_rows),
            "saved_portfolios": len(saved_portfolios),
            "review_notes": len(review_notes),
        },
    }
