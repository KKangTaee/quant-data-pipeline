from __future__ import annotations

from datetime import date, datetime
from typing import Any
from uuid import uuid4

import pandas as pd

PRE_LIVE_STATUS_OPTIONS = ["watchlist", "paper_tracking", "hold", "reject", "re_review"]


def _default_pre_live_status_from_current_candidate(row: dict[str, Any]) -> str:
    result = dict(row.get("result") or {})
    promotion = str(result.get("promotion") or "").lower()
    shortlist = str(result.get("shortlist") or "").lower()
    deployment = str(result.get("deployment") or "").lower()
    blockers = result.get("blockers") if isinstance(result.get("blockers"), list) else []

    if any(term in promotion for term in ["reject", "fail"]) or any(term in deployment for term in ["reject", "blocked"]):
        return "reject"
    if blockers:
        return "hold"
    if shortlist in {"paper_probation", "small_capital_trial"} or deployment == "paper_only":
        return "paper_tracking"
    if shortlist == "watchlist":
        return "watchlist"
    if deployment == "review_required":
        return "watchlist"
    return "re_review"


def _pre_live_status_korean_label(status: str) -> str:
    labels = {
        "watchlist": "Watchlist: 다시 볼 후보",
        "paper_tracking": "Paper Tracking: 실제 돈 없이 추적",
        "hold": "Hold: 보류",
        "reject": "Reject: 추적 종료",
        "re_review": "Re-Review: 정해진 날짜에 재검토",
    }
    return labels.get(status, status)


# Pre-Live system 추천 상태가 왜 나왔는지 operator에게 짧은 근거로 보여준다.
def _pre_live_status_suggestion_reason(row: dict[str, Any], suggested_status: str) -> str:
    result = dict(row.get("result") or {})
    promotion = str(result.get("promotion") or "unknown")
    shortlist = str(result.get("shortlist") or "unknown")
    deployment = str(result.get("deployment") or "unknown")
    blockers = result.get("blockers") if isinstance(result.get("blockers"), list) else []
    signal = f"promotion={promotion}, shortlist={shortlist}, deployment={deployment}"

    if suggested_status == "reject":
        reason = "promotion 또는 deployment가 reject / fail / blocked 계열이라 Pre-Live 추적 유지보다 종료가 우선입니다."
    elif suggested_status == "hold":
        blocker_label = ", ".join(str(item) for item in blockers[:3]) if blockers else "확인 필요 blocker"
        reason = f"blocker가 남아 있어 먼저 해소 여부를 봐야 합니다: {blocker_label}."
    elif suggested_status == "paper_tracking":
        reason = "paper_probation, small_capital_trial, paper_only 신호가 있어 실제 돈 없이 관찰하는 경로가 가장 자연스럽습니다."
    elif suggested_status == "watchlist":
        reason = "watchlist 또는 review_required 신호라 바로 paper tracking보다 후보로 남겨 재검토하는 경로가 적절합니다."
    else:
        reason = "즉시 분류할 강한 신호가 부족해 정해진 날짜에 다시 확인하는 경로로 둡니다."
    return f"{_pre_live_status_korean_label(suggested_status)} 추천: {reason} ({signal})"


def _pre_live_tracking_plan(status: str) -> dict[str, str | None]:
    if status == "paper_tracking":
        return {
            "cadence": "monthly",
            "stop_condition": "Real-Money blocker가 새로 생기거나 drawdown / benchmark gap이 크게 악화되면 중단한다.",
            "success_condition": "정해진 관찰 기간 동안 핵심 Real-Money blocker 없이 후보 성격이 유지되면 재검토한다.",
        }
    if status == "watchlist":
        return {
            "cadence": "next_strategy_review",
            "stop_condition": "동일 family에서 더 나은 후보가 나오거나 핵심 지표가 훼손되면 watchlist에서 내린다.",
            "success_condition": "다음 비교에서 여전히 후보 가치가 있으면 paper tracking 전환을 검토한다.",
        }
    if status == "re_review":
        return {
            "cadence": "scheduled_review",
            "stop_condition": "재검토 시점에도 blocker가 유지되면 hold 또는 reject로 바꾼다.",
            "success_condition": "재검토 시점에 blocker가 해소되면 watchlist 또는 paper tracking으로 전환한다.",
        }
    return {"cadence": None, "stop_condition": None, "success_condition": None}


def _default_pre_live_operator_reason(row: dict[str, Any], status: str) -> str:
    result = dict(row.get("result") or {})
    title = str(row.get("title") or row.get("registry_id") or "candidate")
    signal = (
        f"promotion={result.get('promotion') or 'unknown'}, "
        f"shortlist={result.get('shortlist') or 'unknown'}, "
        f"deployment={result.get('deployment') or 'unknown'}"
    )
    if status == "paper_tracking":
        return f"{title}는 Real-Money 신호가 paper 관찰 후보에 가까워 실제 돈 없이 추적한다 ({signal})."
    if status == "watchlist":
        return f"{title}는 다시 볼 가치는 있지만 즉시 paper tracking 전 추가 비교가 필요하다 ({signal})."
    if status == "hold":
        return f"{title}는 blocker 또는 운영상 미확인 요소가 남아 있어 보류한다 ({signal})."
    if status == "reject":
        return f"{title}는 현재 기준에서 Pre-Live 추적 대상으로 유지하기 어렵다 ({signal})."
    return f"{title}는 지금 즉시 분류하기보다 정해진 시점에 다시 확인한다 ({signal})."


def _default_pre_live_next_action(status: str) -> str:
    if status == "paper_tracking":
        return "실제 돈을 넣지 않고 월 1회 기준으로 성과, MDD, benchmark gap, Real-Money blocker 변화를 기록한다."
    if status == "watchlist":
        return "다음 후보 비교 또는 데이터 업데이트 후 paper tracking 전환 여부를 다시 판단한다."
    if status == "hold":
        return "보류 사유를 해소할 수 있는 데이터, 설정, 검증 조건을 먼저 확인한다."
    if status == "reject":
        return "현재 기준에서는 추적을 종료하고, 같은 후보를 다시 쓰려면 새 근거가 생겼을 때 새 기록으로 검토한다."
    return "review_date에 후보 상태와 Real-Money 신호를 다시 확인한다."


# Pre-Live 저장 초안이 Portfolio Proposal로 이어질 수 있는지 operator-facing score로 요약한다.
def _build_pre_live_operating_readiness_evaluation(
    row: dict[str, Any],
    *,
    pre_live_status: str,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
) -> dict[str, Any]:
    result = dict(row.get("result") or {})
    record_type = str(row.get("record_type") or "").strip().lower()
    tracking_plan = _pre_live_tracking_plan(pre_live_status)
    blockers = result.get("blockers") if isinstance(result.get("blockers"), list) else []
    promotion = str(result.get("promotion") or "").strip().lower()
    shortlist = str(result.get("shortlist") or "").strip().lower()
    deployment = str(result.get("deployment") or "").strip().lower()

    def has_value(value: Any) -> bool:
        if value in (None, "", [], {}):
            return False
        try:
            return not bool(pd.isna(value))
        except (TypeError, ValueError):
            return True

    identity_ready = (
        has_value(row.get("registry_id"))
        and has_value(row.get("strategy_family"))
        and has_value(row.get("strategy_name") or row.get("title"))
    )
    result_ready = any(has_value(result.get(key)) for key in ("cagr", "mdd", "end_balance"))
    real_money_ready = any(
        has_value(result.get(key))
        for key in ("promotion", "shortlist", "deployment", "validation_status", "monitoring_status")
    )
    status_ready = pre_live_status in PRE_LIVE_STATUS_OPTIONS
    operator_ready = has_value(operator_reason) and has_value(next_action)
    review_date_required = pre_live_status in {"paper_tracking", "re_review"}
    review_date_ready = not review_date_required or review_date_value is not None
    tracking_plan_ready = pre_live_status in {"hold", "reject"} or bool(
        tracking_plan.get("cadence") or tracking_plan.get("stop_condition") or tracking_plan.get("success_condition")
    )
    proposal_signal_ready = (
        record_type == "current_candidate"
        and pre_live_status == "paper_tracking"
        and promotion not in {"", "hold", "reject", "failed", "fail"}
        and deployment not in {"", "blocked", "reject"}
        and not blockers
    )

    checks = [
        {
            "criteria": "Candidate Identity",
            "ready": identity_ready,
            "points": 1.2,
            "current": f"id={row.get('registry_id') or '-'}, type={record_type or '-'}",
            "judgment": "후보 식별 가능" if identity_ready else "registry identity 부족",
        },
        {
            "criteria": "Result Snapshot",
            "ready": result_ready,
            "points": 1.3,
            "current": f"CAGR={result.get('cagr') or '-'}, MDD={result.get('mdd') or '-'}",
            "judgment": "운영 기록에 남길 성과 snapshot 있음" if result_ready else "성과 snapshot 부족",
        },
        {
            "criteria": "Real-Money Signal",
            "ready": real_money_ready,
            "points": 1.5,
            "current": f"promotion={promotion or '-'}, deployment={deployment or '-'}",
            "judgment": "후보 상태 해석 가능" if real_money_ready else "Real-Money 신호 부족",
        },
        {
            "criteria": "Pre-Live Status",
            "ready": status_ready,
            "points": 1.2,
            "current": _pre_live_status_korean_label(pre_live_status),
            "judgment": "운영 상태 선택됨" if status_ready else "운영 상태 선택 필요",
        },
        {
            "criteria": "Operator Reason / Next Action",
            "ready": operator_ready,
            "points": 1.2,
            "current": "작성됨" if operator_ready else "미작성",
            "judgment": "왜/다음 행동이 남아 있음" if operator_ready else "운영 판단 메모 부족",
        },
        {
            "criteria": "Review Date",
            "ready": review_date_ready,
            "points": 1.0,
            "current": review_date_value.isoformat() if review_date_value else "-",
            "judgment": "다음 점검일 있음" if review_date_ready else "paper/re-review에는 점검일 필요",
        },
        {
            "criteria": "Tracking Plan",
            "ready": tracking_plan_ready,
            "points": 1.0,
            "current": tracking_plan.get("cadence") or "-",
            "judgment": "추적 방식 있음" if tracking_plan_ready else "추적 계획 부족",
        },
        {
            "criteria": "Portfolio Proposal Route",
            "ready": proposal_signal_ready,
            "points": 1.6,
            "current": f"status={pre_live_status}, shortlist={shortlist or '-'}",
            "judgment": "8단계 후보로 사용 가능" if proposal_signal_ready else "8단계 직행 범위는 아님",
        },
    ]
    max_points = sum(float(check["points"]) for check in checks)
    earned_points = sum(float(check["points"]) for check in checks if check["ready"])
    score = round((earned_points / max_points) * 10.0, 1) if max_points else 0.0
    can_save_record = identity_ready and result_ready and real_money_ready and status_ready and operator_ready and review_date_ready
    can_move_to_portfolio_proposal = bool(can_save_record and tracking_plan_ready and proposal_signal_ready)

    warning_reasons: list[str] = []
    if record_type != "current_candidate":
        warning_reasons.append(f"Record Type={record_type or '-'}")
    if pre_live_status == "watchlist":
        warning_reasons.append("watchlist는 Portfolio Proposal 직행보다 재검토 후보로 해석")
    if pre_live_status in {"hold", "reject"}:
        warning_reasons.append(f"{pre_live_status} 상태는 8단계 proposal 후보가 아님")
    if blockers:
        warning_reasons.append("Real-Money blocker가 남아 있음")

    if can_move_to_portfolio_proposal:
        route_label = "PORTFOLIO_PROPOSAL_READY"
        verdict = "7단계 통과: 저장 후 Portfolio Proposal 후보로 이동 가능"
        next_action_value = "Save Pre-Live Record로 운영 기록을 남긴 뒤 8단계 Portfolio Proposal에서 후보 묶음에 포함할지 검토합니다."
    elif can_save_record and pre_live_status == "watchlist":
        route_label = "WATCHLIST_ONLY"
        verdict = "Pre-Live 기록 가능: watchlist로 두고 다음 비교/업데이트 후 재검토"
        next_action_value = "후보를 저장하되 8단계 직행보다는 비교 또는 데이터 업데이트 후 paper tracking 전환 여부를 다시 봅니다."
    elif can_save_record and pre_live_status == "re_review":
        route_label = "SCHEDULED_REVIEW"
        verdict = "Pre-Live 기록 가능: 정해진 날짜에 다시 판단"
        next_action_value = "review date에 Real-Money 신호와 blocker를 다시 확인해 watchlist/paper/hold 중 하나로 재분류합니다."
    elif can_save_record and pre_live_status == "hold":
        route_label = "PRE_LIVE_HOLD"
        verdict = "Pre-Live 보류 기록 가능"
        next_action_value = "보류 사유를 해소한 뒤 다시 Pre-Live 운영 상태를 판단합니다."
    elif can_save_record and pre_live_status == "reject":
        route_label = "REJECTED"
        verdict = "Pre-Live 추적 종료 기록 가능"
        next_action_value = "현재 후보 흐름은 종료하고, 새 근거가 있을 때 새 후보로 다시 검토합니다."
    else:
        route_label = "PRE_LIVE_CHECK_REQUIRED"
        verdict = "Pre-Live 저장 전 추가 확인 필요"
        next_action_value = "후보 식별, 성과 snapshot, Real-Money 신호, 운영 판단 메모, review date를 보강합니다."

    blocking_reasons = [str(check["criteria"]) for check in checks if not check["ready"] and check["criteria"] != "Portfolio Proposal Route"]
    if not can_move_to_portfolio_proposal and not blocking_reasons and pre_live_status == "paper_tracking":
        blocking_reasons.append("Portfolio Proposal Route")

    return {
        "route_label": route_label,
        "score": score,
        "verdict": verdict,
        "next_action": next_action_value,
        "can_save_record": can_save_record,
        "can_move_to_portfolio_proposal": can_move_to_portfolio_proposal,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": warning_reasons,
        "criteria_rows": [
            {
                "기준": check["criteria"],
                "상태": "PASS" if check["ready"] else "CHECK",
                "현재 값": check["current"],
                "점수": f"{float(check['points']):g} / {float(check['points']):g}" if check["ready"] else f"0 / {float(check['points']):g}",
                "판단": check["judgment"],
            }
            for check in checks
        ],
    }


# Current Candidate row를 append-only Pre-Live registry에 저장할 초안 row로 변환한다.
def _build_pre_live_draft_from_current_candidate(
    row: dict[str, Any],
    *,
    pre_live_status: str,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
) -> dict[str, Any]:
    result = dict(row.get("result") or {})
    registry_id = str(row.get("registry_id") or "unknown_current_candidate")
    return {
        "schema_version": 1,
        "pre_live_id": f"pre_live_{registry_id}",
        "revision_id": f"rev_{uuid4().hex[:12]}",
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "record_status": "active",
        "source_kind": "current_candidate_registry",
        "source_ref": ".note/finance/CURRENT_CANDIDATE_REGISTRY.jsonl",
        "source_candidate_registry_id": registry_id,
        "title": f"{row.get('title') or registry_id} - Pre-Live review",
        "strategy_or_bundle": {
            "kind": "single_strategy",
            "family": row.get("strategy_family"),
            "name": row.get("strategy_name"),
            "candidate_role": row.get("candidate_role"),
        },
        "settings_snapshot": {
            "period": row.get("period"),
            "contract": row.get("contract"),
            "source_ref": row.get("source_ref"),
        },
        "result_snapshot": {
            "cagr": result.get("cagr"),
            "mdd": result.get("mdd"),
            "sharpe": result.get("sharpe"),
            "end_balance": result.get("end_balance"),
        },
        "real_money_signal": {
            "promotion": result.get("promotion") or "unknown",
            "shortlist": result.get("shortlist") or "unknown",
            "deployment": result.get("deployment") or "unknown",
            "validation_status": result.get("validation_status") or "unknown",
            "liquidity_status": result.get("liquidity_status") or "unknown",
            "blockers": result.get("blockers") if isinstance(result.get("blockers"), list) else [],
        },
        "pre_live_status": pre_live_status,
        "operator_reason": operator_reason,
        "next_action": next_action,
        "review_date": review_date_value.isoformat() if review_date_value else None,
        "tracking_plan": _pre_live_tracking_plan(pre_live_status),
        "docs": row.get("docs") or {},
        "notes": "Created from Backtest > Pre-Live Review. This is a pre-live operating record, not a live-trading approval.",
    }


# Pre-Live registry rows를 Streamlit inspection table에 맞게 평탄화한다.
def _build_pre_live_registry_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        result = dict(row.get("result_snapshot") or {})
        signal = dict(row.get("real_money_signal") or {})
        strategy = dict(row.get("strategy_or_bundle") or {})
        display_rows.append(
            {
                "Status": row.get("pre_live_status"),
                "Title": row.get("title"),
                "Family": str(strategy.get("family") or "").replace("_", " ").title(),
                "Candidate Role": strategy.get("candidate_role"),
                "CAGR": result.get("cagr"),
                "MDD": result.get("mdd"),
                "Promotion": signal.get("promotion"),
                "Shortlist": signal.get("shortlist"),
                "Deployment": signal.get("deployment"),
                "Next Action": row.get("next_action"),
                "Review Date": row.get("review_date"),
                "Pre-Live ID": row.get("pre_live_id"),
            }
        )
    return pd.DataFrame(display_rows)
