from __future__ import annotations

import json
from datetime import date, datetime
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.web.backtest_practical_validation_helpers import (
    build_selection_source_from_candidate_draft,
    queue_practical_validation_source,
)
from app.web.backtest_strategy_catalog import strategy_key_to_display_name as catalog_strategy_key_to_display_name
from app.web.runtime import CURRENT_CANDIDATE_REGISTRY_FILE
from app.web.runtime.backtest import STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT

CANDIDATE_REVIEW_DECISION_OPTIONS = [
    "consider_registry_candidate",
    "keep_as_near_miss_review",
    "keep_as_scenario_review",
    "needs_more_evidence",
    "reject_for_now",
]
CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS = ["current_candidate", "near_miss", "scenario"]


def _history_strategy_display_name(record: dict[str, Any]) -> str:
    summary = record.get("summary") or {}
    return summary.get("strategy_name") or record.get("strategy_key") or "Unknown Strategy"


def _strategy_key_to_display_name(strategy_key: str | None) -> str | None:
    return catalog_strategy_key_to_display_name(strategy_key)


def _resolve_guardrail_reference_ticker_value(data: dict[str, Any] | None) -> str | None:
    data = dict(data or {})
    ticker = str(
        data.get("guardrail_reference_ticker")
        or data.get("benchmark_ticker")
        or ""
    ).strip().upper()
    return ticker or None


def _raw_guardrail_reference_ticker_value(data: dict[str, Any] | None) -> str | None:
    data = dict(data or {})
    ticker = str(data.get("guardrail_reference_ticker") or "").strip().upper()
    return ticker or None


def _current_candidate_registry_role_label(row: dict[str, Any]) -> str:
    record_type = str(row.get("record_type") or "").strip().lower()
    candidate_role = str(row.get("candidate_role") or "").strip().lower()
    if record_type == "current_candidate":
        return "current anchor"
    if record_type == "near_miss":
        return "lower-MDD near miss"
    if candidate_role == "cleaner_alternative":
        return "cleaner alternative"
    return candidate_role or record_type or "candidate"


def _current_candidate_registry_selection_label(row: dict[str, Any]) -> str:
    family = str(row.get("strategy_family") or "").replace("_", " ").title()
    registry_id = str(row.get("registry_id") or "").strip()
    label_parts = [
        family or "Candidate",
        _current_candidate_registry_role_label(row),
        str(row.get("title") or registry_id or "untitled"),
    ]
    if registry_id:
        label_parts.append(f"id={registry_id}")
    return " | ".join(label_parts)


def _current_candidate_registry_contract_summary(row: dict[str, Any]) -> str:
    contract = dict(row.get("contract") or {})
    parts: list[str] = []
    top_n = contract.get("top_n")
    if top_n is not None:
        parts.append(f"Top N {int(top_n)}")
    benchmark_contract = contract.get("benchmark_contract")
    benchmark_ticker = contract.get("benchmark_ticker")
    guardrail_reference_ticker = _resolve_guardrail_reference_ticker_value(contract)
    if benchmark_contract == STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
        parts.append("Benchmark Candidate Equal-Weight")
    elif benchmark_ticker:
        parts.append(f"Benchmark Ticker {benchmark_ticker}")
    raw_guardrail_reference_ticker = _raw_guardrail_reference_ticker_value(contract)
    if raw_guardrail_reference_ticker:
        parts.append(f"Guardrail Ref {guardrail_reference_ticker}")
    elif benchmark_ticker and benchmark_contract != STRICT_BENCHMARK_CONTRACT_CANDIDATE_EQUAL_WEIGHT:
        parts.append("Guardrail Ref same as benchmark")
    factor_adjustment = contract.get("factor_adjustment")
    if factor_adjustment:
        parts.append(str(factor_adjustment))
    quality_adjustment = contract.get("quality_adjustment")
    value_adjustment = contract.get("value_adjustment")
    if quality_adjustment:
        parts.append(f"quality {quality_adjustment}")
    if value_adjustment:
        parts.append(f"value {value_adjustment}")
    return " | ".join(parts) if parts else "-"


def _build_current_candidate_registry_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        result = dict(row.get("result") or {})
        display_rows.append(
            {
                "Family": str(row.get("strategy_family") or "").replace("_", " ").title(),
                "Role": _current_candidate_registry_role_label(row),
                "Title": row.get("title"),
                "Contract": _current_candidate_registry_contract_summary(row),
                "CAGR": result.get("cagr"),
                "MDD": result.get("mdd"),
                "Promotion": result.get("promotion"),
                "Shortlist": result.get("shortlist"),
                "Registry ID": row.get("registry_id"),
            }
        )
    return pd.DataFrame(display_rows)


def _load_current_candidate_registry_rows_all() -> list[dict[str, Any]]:
    if not CURRENT_CANDIDATE_REGISTRY_FILE.exists():
        return []

    rows: list[dict[str, Any]] = []
    for line in CURRENT_CANDIDATE_REGISTRY_FILE.read_text(encoding="utf-8", errors="ignore").splitlines():
        line = line.strip()
        if not line:
            continue
        try:
            row = json.loads(line)
        except json.JSONDecodeError:
            continue
        if isinstance(row, dict):
            rows.append(row)
    return rows


def _candidate_review_note_existing_registry_rows(note: dict[str, Any]) -> list[dict[str, Any]]:
    review_note_id = str(note.get("review_note_id") or "").strip()
    if not review_note_id:
        return []
    return [
        row
        for row in _load_current_candidate_registry_rows_all()
        if str(row.get("source_review_note_id") or "").strip() == review_note_id
        and str(row.get("status") or "active").strip().lower() == "active"
    ]


def _build_existing_review_note_registry_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    return pd.DataFrame(
        [
            {
                "Recorded At": row.get("recorded_at"),
                "Registry ID": row.get("registry_id"),
                "Revision ID": row.get("revision_id"),
                "Record Type": row.get("record_type"),
                "Title": row.get("title"),
            }
            for row in rows
        ]
    )


def _candidate_review_stage(row: dict[str, Any]) -> str:
    record_type = str(row.get("record_type") or "").strip().lower()
    result = dict(row.get("result") or {})
    promotion = str(result.get("promotion") or "").strip().lower()
    shortlist = str(result.get("shortlist") or "").strip().lower()
    deployment = str(result.get("deployment") or "").strip().lower()

    if record_type == "current_candidate" and promotion == "real_money_candidate":
        return "Main Review Candidate"
    if record_type == "near_miss":
        return "Near-Miss / Risk Alternative"
    if record_type == "scenario":
        return "Scenario / Cleaner Alternative"
    if shortlist == "watchlist" or deployment == "review_required":
        return "Watchlist Review"
    return "Manual Review"


def _candidate_review_reason(row: dict[str, Any]) -> str:
    record_type = str(row.get("record_type") or "").strip().lower()
    role = _current_candidate_registry_role_label(row)
    if record_type == "current_candidate":
        return "현재 family의 기준 후보로 비교와 Pre-Live 운영 기록의 출발점입니다."
    if record_type == "near_miss":
        return "주 후보보다 일부 gate는 약하지만 MDD나 방어성이 좋아 다시 볼 후보입니다."
    if record_type == "scenario":
        return "주 후보를 바로 대체하기보다 설정 차이를 비교하기 위한 대안 후보입니다."
    return f"`{role}` 역할로 기록된 후보라 수동 확인이 필요합니다."


def _candidate_review_next_step(row: dict[str, Any]) -> str:
    record_type = str(row.get("record_type") or "").strip().lower()
    result = dict(row.get("result") or {})
    promotion = str(result.get("promotion") or "").strip().lower()
    shortlist = str(result.get("shortlist") or "").strip().lower()
    deployment = str(result.get("deployment") or "").strip().lower()

    if record_type == "current_candidate" and promotion == "real_money_candidate":
        return "Compare에서 다른 family 후보와 같이 본 뒤, 유지 후보라면 Candidate Review 안에서 Pre-Live 운영 상태를 기록합니다."
    if record_type == "near_miss":
        return "낙폭을 줄이는 대안이 필요한 상황에서 Compare로 주 후보와 비교합니다. 기본 후보로 자동 승격하지 않습니다."
    if record_type == "scenario":
        return "설정 차이를 확인하는 비교 대상으로 사용합니다. 필요할 때만 Pre-Live 후보로 넘깁니다."
    if shortlist == "watchlist" or deployment == "review_required":
        return "Watchlist 후보로 두고 다음 비교나 데이터 업데이트 후 재검토합니다."
    return "후보 역할과 Real-Money 신호를 확인한 뒤 compare 또는 Pre-Live 운영 기록 중 하나로 넘깁니다."


def _build_candidate_review_board_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        result = dict(row.get("result") or {})
        docs = dict(row.get("docs") or {})
        display_rows.append(
            {
                "Review Stage": _candidate_review_stage(row),
                "Family": str(row.get("strategy_family") or "").replace("_", " ").title(),
                "Role": _current_candidate_registry_role_label(row),
                "Title": row.get("title"),
                "CAGR": result.get("cagr"),
                "MDD": result.get("mdd"),
                "Promotion": result.get("promotion"),
                "Shortlist": result.get("shortlist"),
                "Deployment": result.get("deployment"),
                "Why It Exists": _candidate_review_reason(row),
                "Suggested Next Step": _candidate_review_next_step(row),
                "Docs": ", ".join(sorted(docs.keys())) if docs else "-",
                "Registry ID": row.get("registry_id"),
            }
        )
    return pd.DataFrame(display_rows)


def _build_candidate_board_operating_evaluation(row: dict[str, Any]) -> dict[str, Any]:
    record_type = str(row.get("record_type") or "").strip().lower()
    result = dict(row.get("result") or {})
    contract = dict(row.get("contract") or {})
    compare_prefill = dict(row.get("compare_prefill") or {})
    review_context = dict(row.get("review_context") or {})
    promotion = str(result.get("promotion") or "").strip().lower()
    deployment = str(result.get("deployment") or "").strip().lower()
    shortlist = str(result.get("shortlist") or "").strip().lower()

    identity_ready = (
        _candidate_intake_value_present(row.get("registry_id"))
        and _candidate_intake_value_present(row.get("strategy_family"))
        and _candidate_intake_value_present(row.get("strategy_name") or row.get("title"))
        and record_type in CURRENT_CANDIDATE_RECORD_TYPE_OPTIONS
    )
    result_ready = any(_candidate_intake_value_present(result.get(key)) for key in ("cagr", "mdd", "end_balance"))
    contract_ready = bool(contract) or bool(compare_prefill)
    review_context_ready = (
        _candidate_intake_value_present(row.get("notes"))
        or _candidate_intake_value_present(review_context.get("operator_reason"))
        or _candidate_intake_value_present(review_context.get("next_action"))
    )
    real_money_signal_ready = any(
        _candidate_intake_value_present(result.get(key))
        for key in ("promotion", "shortlist", "deployment", "validation_status", "monitoring_status")
    )
    real_money_not_blocked = (
        real_money_signal_ready
        and promotion not in {"", "hold"}
        and deployment not in {"", "blocked"}
    )
    core_board_ready = identity_ready and result_ready and contract_ready and review_context_ready
    can_move_to_pre_live = record_type == "current_candidate" and core_board_ready and real_money_not_blocked
    can_move_to_compare = record_type in {"near_miss", "scenario"} and core_board_ready and contract_ready

    warning_reasons: list[str] = []
    if record_type == "current_candidate" and shortlist in {"watchlist", "paper_probation"}:
        warning_reasons.append(f"Shortlist={shortlist}")
    if record_type in {"near_miss", "scenario"} and real_money_not_blocked:
        warning_reasons.append("Real-Money gate가 나쁘지 않더라도 이 row는 우선 비교/시나리오 범위입니다")

    if can_move_to_pre_live:
        route_label = "PRE_LIVE_READY"
        verdict = "Candidate Packaging 통과: Pre-Live 운영 기록을 남길 수 있음"
        next_action = "Candidate Review 안에서 paper tracking / watchlist / hold 같은 운영 상태를 저장합니다."
    elif can_move_to_compare:
        route_label = "COMPARE_REVIEW_READY"
        verdict = "Candidate Packaging 확인 완료: Compare에서 다시 비교할 후보"
        next_action = "Compare 후보 선택 목록에서 비교할 다른 후보를 추가한 뒤 실행합니다."
    else:
        route_label = "BOARD_HOLD"
        verdict = "Candidate Packaging 보류: Board에서 역할과 근거를 먼저 보강"
        next_action = "후보 식별, 성과 snapshot, 설정 snapshot, Real-Money 신호, 판단 메모를 확인합니다."

    checks = [
        {
            "criteria": "Registry Identity / Role",
            "ready": identity_ready,
            "points": 2.0,
            "current": f"id={row.get('registry_id') or '-'}, type={record_type or '-'}",
            "judgment": "보드에서 후보 역할을 읽을 수 있음" if identity_ready else "registry id / role / strategy 식별 부족",
        },
        {
            "criteria": "Result Snapshot",
            "ready": result_ready,
            "points": 1.5,
            "current": (
                f"CAGR={result.get('cagr') or '-'}, "
                f"MDD={result.get('mdd') or '-'}, "
                f"End={result.get('end_balance') or '-'}"
            ),
            "judgment": "운영 판단에 쓸 성과 snapshot 있음" if result_ready else "성과 snapshot 부족",
        },
        {
            "criteria": "Contract / Compare Prefill",
            "ready": contract_ready,
            "points": 2.0,
            "current": _current_candidate_registry_contract_summary(row),
            "judgment": "Compare 또는 Pre-Live에서 재진입 가능" if contract_ready else "설정 snapshot 부족",
        },
        {
            "criteria": "Review Context",
            "ready": review_context_ready,
            "points": 1.5,
            "current": "작성됨" if review_context_ready else "미작성",
            "judgment": "왜 남긴 후보인지 읽을 수 있음" if review_context_ready else "운영자 판단 근거 부족",
        },
        {
            "criteria": "Real-Money Signal",
            "ready": real_money_signal_ready,
            "points": 1.0,
            "current": f"promotion={promotion or '-'}, deployment={deployment or '-'}",
            "judgment": "신호 확인 가능" if real_money_signal_ready else "Real-Money signal 부족",
        },
        {
            "criteria": "Pre-Live Route",
            "ready": can_move_to_pre_live or can_move_to_compare,
            "points": 2.0,
            "current": route_label,
            "judgment": (
                "current candidate라 Pre-Live 가능"
                if can_move_to_pre_live
                else "비교/시나리오 후보라 Compare 가능"
                if can_move_to_compare
                else "다음 운영 경로 보류"
            ),
        },
    ]

    max_points = sum(float(item["points"]) for item in checks)
    earned_points = sum(float(item["points"]) for item in checks if item["ready"])
    score = round((earned_points / max_points) * 10.0, 1) if max_points else 0.0
    blocking_reasons = [str(item["criteria"]) for item in checks if not item["ready"]]
    if record_type == "current_candidate" and real_money_signal_ready and not real_money_not_blocked:
        blocking_reasons.append("current_candidate지만 Real-Money gate가 hold/blocked")

    return {
        "route_label": route_label,
        "score": score,
        "verdict": verdict,
        "next_action": next_action,
        "can_move_to_pre_live": can_move_to_pre_live,
        "can_move_to_compare": can_move_to_compare,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": warning_reasons,
        "criteria_rows": [
            {
                "기준": item["criteria"],
                "상태": "PASS" if item["ready"] else "CHECK",
                "현재 값": item["current"],
                "점수": f"{float(item['points']):g} / {float(item['points']):g}"
                if item["ready"]
                else f"0 / {float(item['points']):g}",
                "판단": item["judgment"],
            }
            for item in checks
        ],
    }


PRE_LIVE_STATUS_OPTIONS = ["watchlist", "paper_tracking", "hold", "reject", "re_review"]


# Current Candidate의 Real-Money 신호로 기본 Pre-Live 운영 상태를 추천한다.
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


# Pre-Live status 값을 화면에서 읽기 쉬운 한국어 라벨로 바꾼다.
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


# 선택한 Pre-Live status별 기본 추적 계획을 만든다.
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


# Current Candidate와 status를 바탕으로 운영자 판단 기본 문장을 만든다.
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


# 선택한 Pre-Live status별 기본 다음 행동 문장을 만든다.
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
            "judgment": "Portfolio Proposal 후보로 사용 가능" if proposal_signal_ready else "Proposal 직행 범위는 아님",
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
        warning_reasons.append(f"{pre_live_status} 상태는 proposal 후보가 아님")
    if blockers:
        warning_reasons.append("Real-Money blocker가 남아 있음")

    if can_move_to_portfolio_proposal:
        route_label = "PORTFOLIO_PROPOSAL_READY"
        verdict = "운영 기록 통과: 저장 후 Portfolio Proposal 후보로 이동 가능"
        next_action_value = "Save Pre-Live Record로 운영 기록을 남긴 뒤 Portfolio Proposal에서 후보 묶음에 포함할지 검토합니다."
    elif can_save_record and pre_live_status == "watchlist":
        route_label = "WATCHLIST_ONLY"
        verdict = "Pre-Live 기록 가능: watchlist로 두고 다음 비교/업데이트 후 재검토"
        next_action_value = "후보를 저장하되 Proposal 직행보다는 비교 또는 데이터 업데이트 후 paper tracking 전환 여부를 다시 봅니다."
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
        "source_ref": ".note/finance/registries/CURRENT_CANDIDATE_REGISTRY.jsonl",
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
        "notes": "Created from Backtest > Candidate Review. This is a pre-live operating record, not a live-trading approval.",
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


def _candidate_review_record_type_suggestion(
    *,
    promotion: str | None,
    shortlist: str | None,
    deployment: str | None,
) -> str:
    promotion_value = str(promotion or "").strip().lower()
    shortlist_value = str(shortlist or "").strip().lower()
    deployment_value = str(deployment or "").strip().lower()
    if promotion_value == "real_money_candidate" and shortlist_value in {"paper_probation", "small_capital_trial"}:
        return "current_candidate_review"
    if shortlist_value == "watchlist" or promotion_value == "production_candidate":
        return "near_miss_review"
    if deployment_value in {"paper_only", "review_required"}:
        return "scenario_review"
    return "manual_review"


def _candidate_review_record_type_label(record_type_suggestion: str) -> str:
    labels = {
        "current_candidate_review": "Current candidate review",
        "near_miss_review": "Near-miss / watchlist review",
        "scenario_review": "Scenario review",
        "manual_review": "Manual review",
    }
    return labels.get(record_type_suggestion, record_type_suggestion)


def _candidate_review_draft_next_step(record_type_suggestion: str) -> str:
    if record_type_suggestion == "current_candidate_review":
        return "기존 current anchor와 비교한 뒤, 대체/유지 여부를 사람 검토로 결정합니다."
    if record_type_suggestion == "near_miss_review":
        return "near-miss 후보로 남길 가치가 있는지 MDD, gate, data trust를 같이 확인합니다."
    if record_type_suggestion == "scenario_review":
        return "설정 차이를 설명할 수 있는 scenario 후보인지 보고, 필요하면 compare에서 기존 후보와 나란히 봅니다."
    return "후보로 남길 근거가 충분한지 먼저 검토합니다."


def _candidate_review_summary_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    summary_df = bundle.get("summary_df")
    if isinstance(summary_df, pd.DataFrame) and not summary_df.empty:
        row = summary_df.iloc[0]
        return {
            "strategy_name": row.get("Name"),
            "start_date": str(row.get("Start Date")),
            "end_date": str(row.get("End Date")),
            "end_balance": row.get("End Balance"),
            "cagr": row.get("CAGR"),
            "sharpe_ratio": row.get("Sharpe Ratio"),
            "maximum_drawdown": row.get("Maximum Drawdown"),
        }
    return {}


def _candidate_review_draft_from_bundle(bundle: dict[str, Any]) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    summary = _candidate_review_summary_from_bundle(bundle)
    promotion = meta.get("promotion_decision")
    shortlist = meta.get("shortlist_status")
    deployment = meta.get("deployment_readiness_status")
    record_type_suggestion = _candidate_review_record_type_suggestion(
        promotion=promotion,
        shortlist=shortlist,
        deployment=deployment,
    )
    price_freshness = dict(meta.get("price_freshness") or {})
    return {
        "source_kind": "latest_backtest_run",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "candidate_review_status": "draft_only_not_saved",
        "strategy_key": meta.get("strategy_key"),
        "strategy_name": bundle.get("strategy_name") or summary.get("strategy_name"),
        "suggested_record_type": record_type_suggestion,
        "suggested_record_type_label": _candidate_review_record_type_label(record_type_suggestion),
        "suggested_next_step": _candidate_review_draft_next_step(record_type_suggestion),
        "result_snapshot": {
            "start_date": summary.get("start_date") or meta.get("actual_result_start") or meta.get("start"),
            "end_date": summary.get("end_date") or meta.get("actual_result_end") or meta.get("end"),
            "end_balance": summary.get("end_balance"),
            "cagr": summary.get("cagr"),
            "sharpe_ratio": summary.get("sharpe_ratio"),
            "maximum_drawdown": summary.get("maximum_drawdown"),
        },
        "real_money_signal": {
            "promotion": promotion,
            "shortlist": shortlist,
            "deployment": deployment,
            "validation_status": meta.get("validation_status"),
            "monitoring_status": meta.get("monitoring_status"),
        },
        "data_trust_snapshot": {
            "requested_end": meta.get("end"),
            "actual_result_start": meta.get("actual_result_start"),
            "actual_result_end": meta.get("actual_result_end"),
            "result_rows": meta.get("result_rows"),
            "price_freshness_status": price_freshness.get("status"),
            "excluded_tickers": meta.get("excluded_tickers") or [],
            "malformed_price_row_count": len(list(meta.get("malformed_price_rows") or [])),
            "warning_count": len(list(meta.get("warnings") or [])),
        },
        "settings_snapshot": {
            "tickers": meta.get("tickers") or [],
            "universe_mode": meta.get("universe_mode"),
            "preset_name": meta.get("preset_name"),
            "universe_contract": meta.get("universe_contract"),
            "factor_freq": meta.get("factor_freq"),
            "rebalance_freq": meta.get("rebalance_freq"),
            "top": meta.get("top"),
            "benchmark_contract": meta.get("benchmark_contract"),
            "benchmark_ticker": meta.get("benchmark_ticker"),
        },
        "notes": (
            "This is a Candidate Review draft. It is not appended to "
            "CURRENT_CANDIDATE_REGISTRY and is not an investment recommendation."
        ),
    }


def _candidate_review_draft_from_history_record(record: dict[str, Any]) -> dict[str, Any]:
    summary = dict(record.get("summary") or {})
    gate_snapshot = dict(record.get("gate_snapshot") or {})
    context = dict(record.get("context") or {})
    promotion = record.get("promotion_decision") or gate_snapshot.get("promotion_decision")
    shortlist = record.get("shortlist_status") or gate_snapshot.get("shortlist_status")
    deployment = record.get("deployment_readiness_status") or gate_snapshot.get("deployment_readiness_status")
    record_type_suggestion = _candidate_review_record_type_suggestion(
        promotion=promotion,
        shortlist=shortlist,
        deployment=deployment,
    )
    price_freshness = dict(record.get("price_freshness") or {})
    return {
        "source_kind": "history_record",
        "created_at": datetime.now().isoformat(timespec="seconds"),
        "candidate_review_status": "draft_only_not_saved",
        "recorded_at": record.get("recorded_at"),
        "run_kind": record.get("run_kind"),
        "strategy_key": record.get("strategy_key"),
        "strategy_name": summary.get("strategy_name") or _history_strategy_display_name(record),
        "suggested_record_type": record_type_suggestion,
        "suggested_record_type_label": _candidate_review_record_type_label(record_type_suggestion),
        "suggested_next_step": _candidate_review_draft_next_step(record_type_suggestion),
        "result_snapshot": {
            "start_date": summary.get("start_date") or record.get("actual_result_start") or record.get("input_start"),
            "end_date": summary.get("end_date") or record.get("actual_result_end") or record.get("input_end"),
            "end_balance": summary.get("end_balance"),
            "cagr": summary.get("cagr"),
            "sharpe_ratio": summary.get("sharpe_ratio"),
            "maximum_drawdown": summary.get("maximum_drawdown"),
        },
        "real_money_signal": {
            "promotion": promotion,
            "shortlist": shortlist,
            "deployment": deployment,
            "validation_status": gate_snapshot.get("validation_status"),
            "monitoring_status": gate_snapshot.get("monitoring_status"),
        },
        "data_trust_snapshot": {
            "requested_end": record.get("input_end"),
            "actual_result_start": record.get("actual_result_start"),
            "actual_result_end": record.get("actual_result_end"),
            "result_rows": record.get("result_rows"),
            "price_freshness_status": price_freshness.get("status") or gate_snapshot.get("price_freshness_status"),
            "excluded_tickers": record.get("excluded_tickers") or [],
            "malformed_price_row_count": len(list(record.get("malformed_price_rows") or [])),
            "warning_count": len(list(record.get("warnings") or [])),
        },
        "settings_snapshot": {
            "tickers": record.get("tickers") or [],
            "universe_mode": record.get("universe_mode"),
            "preset_name": record.get("preset_name"),
            "universe_contract": record.get("universe_contract"),
            "factor_freq": record.get("factor_freq"),
            "rebalance_freq": record.get("rebalance_freq"),
            "top": record.get("top"),
            "benchmark_contract": record.get("benchmark_contract"),
            "benchmark_ticker": record.get("benchmark_ticker"),
            "context_keys": sorted(context.keys()),
        },
        "notes": (
            "This is a Candidate Review draft from a persisted history record. "
            "It is not appended to CURRENT_CANDIDATE_REGISTRY and is not an investment recommendation."
        ),
    }


def _queue_candidate_review_draft(draft: dict[str, Any]) -> None:
    st.session_state.backtest_candidate_review_draft = draft
    st.session_state.backtest_candidate_review_draft_notice = (
        "후보 검토 초안을 legacy Candidate Packaging에도 보존했습니다. "
        "새 주 흐름은 Practical Validation으로 이어집니다."
    )
    source = build_selection_source_from_candidate_draft(draft)
    queue_practical_validation_source(source, persist=True)


def _candidate_intake_value_present(value: Any) -> bool:
    if value is None:
        return False
    if isinstance(value, str):
        normalized = value.strip().lower()
        return bool(normalized and normalized not in {"-", "none", "nan", "unknown"})
    if isinstance(value, (list, tuple, set, dict)):
        return bool(value)
    try:
        return not bool(pd.isna(value))
    except (TypeError, ValueError):
        return True


def _build_candidate_intake_readiness_evaluation(
    draft: dict[str, Any],
    *,
    operator_reason: str,
    next_action: str,
) -> dict[str, Any]:
    result = dict(draft.get("result_snapshot") or {})
    signal = dict(draft.get("real_money_signal") or {})
    data_trust = dict(draft.get("data_trust_snapshot") or {})
    settings = dict(draft.get("settings_snapshot") or {})

    identity_ready = _candidate_intake_value_present(draft.get("strategy_name")) or _candidate_intake_value_present(
        draft.get("strategy_key")
    )
    source_ready = _candidate_intake_value_present(draft.get("source_kind"))
    result_ready = all(
        _candidate_intake_value_present(result.get(key))
        for key in ("end_balance", "cagr", "maximum_drawdown")
    )
    data_status = str(data_trust.get("price_freshness_status") or "").strip().lower()
    data_snapshot_ready = bool(data_trust) and any(
        _candidate_intake_value_present(data_trust.get(key))
        for key in ("requested_end", "actual_result_start", "actual_result_end", "result_rows", "price_freshness_status")
    )
    data_ready = data_snapshot_ready and data_status != "error"
    real_money_ready = bool(signal) and any(_candidate_intake_value_present(value) for value in signal.values())
    settings_core_ready = any(
        _candidate_intake_value_present(settings.get(key))
        for key in ("tickers", "preset_name", "universe_mode", "universe_contract")
    )
    settings_contract_ready = any(
        _candidate_intake_value_present(settings.get(key))
        for key in ("factor_freq", "rebalance_freq", "top", "benchmark_contract", "benchmark_ticker")
    )
    settings_ready = bool(settings) and settings_core_ready and settings_contract_ready
    operator_ready = _candidate_intake_value_present(operator_reason) and _candidate_intake_value_present(next_action)

    checks = [
        {
            "criteria": "후보 식별 / Source",
            "ready": identity_ready and source_ready,
            "points": 1.5,
            "current": f"{draft.get('strategy_name') or draft.get('strategy_key') or '-'} / {draft.get('source_kind') or '-'}",
            "judgment": "후보 이름과 source가 확인됨" if identity_ready and source_ready else "후보 이름 또는 source가 부족함",
        },
        {
            "criteria": "Result Snapshot",
            "ready": result_ready,
            "points": 2.0,
            "current": (
                f"CAGR={result.get('cagr') or '-'}, "
                f"MDD={result.get('maximum_drawdown') or '-'}, "
                f"End={result.get('end_balance') or '-'}"
            ),
            "judgment": "성과 snapshot이 저장 가능" if result_ready else "CAGR / MDD / End Balance 중 누락 있음",
        },
        {
            "criteria": "Data Trust Snapshot",
            "ready": data_ready,
            "points": 1.5,
            "current": data_status.upper() if data_status else "SNAPSHOT_ONLY",
            "judgment": (
                "Data Trust가 해석 가능"
                if data_ready
                else "Data Trust snapshot이 없거나 price freshness error 상태"
            ),
        },
        {
            "criteria": "Real-Money Signal",
            "ready": real_money_ready,
            "points": 1.5,
            "current": (
                f"promotion={signal.get('promotion') or '-'}, "
                f"deployment={signal.get('deployment') or '-'}"
            ),
            "judgment": "Real-Money signal이 비어 있지 않음" if real_money_ready else "Real-Money signal이 비어 있음",
        },
        {
            "criteria": "Settings Snapshot",
            "ready": settings_ready,
            "points": 2.0,
            "current": (
                f"universe={settings.get('universe_mode') or settings.get('preset_name') or '-'}, "
                f"tickers={len(settings.get('tickers') or []) if isinstance(settings.get('tickers'), list) else '-'}, "
                f"top={settings.get('top') or '-'}, rebalance={settings.get('rebalance_freq') or '-'}"
            ),
            "judgment": "재현 가능한 설정 snapshot이 있음" if settings_ready else "universe / ticker / cadence 정보가 부족함",
        },
        {
            "criteria": "Operator Reason / Next Action",
            "ready": operator_ready,
            "points": 1.5,
            "current": "작성됨" if operator_ready else "미작성",
            "judgment": "운영자 판단과 다음 행동이 작성됨" if operator_ready else "Review Note 저장 전 판단 메모 필요",
        },
    ]

    max_points = sum(float(row["points"]) for row in checks)
    earned_points = sum(float(row["points"]) for row in checks if row["ready"])
    score = round((earned_points / max_points) * 10.0, 1) if max_points else 0.0
    ready = all(bool(row["ready"]) for row in checks)

    blocking_reasons = [str(row["criteria"]) for row in checks if not row["ready"]]
    warning_reasons: list[str] = []
    if data_status == "warning":
        warning_reasons.append("Data Trust가 warning 상태이므로 Review Note에 사유를 남겨야 함")
    excluded_tickers = data_trust.get("excluded_tickers") or []
    if isinstance(excluded_tickers, list) and excluded_tickers:
        warning_reasons.append(f"Excluded ticker {len(excluded_tickers)}개")
    malformed_count = int(data_trust.get("malformed_price_row_count") or 0)
    warning_count = int(data_trust.get("warning_count") or 0)
    if malformed_count:
        warning_reasons.append(f"Malformed price row group {malformed_count}개")
    if warning_count:
        warning_reasons.append(f"Data warning {warning_count}개")

    if ready:
        verdict = "Candidate Packaging Review Note 저장 가능"
        next_step = "Save Candidate Review Note를 누른 뒤 같은 Candidate Packaging 안에서 registry 후보 범위를 정합니다."
    else:
        verdict = "Candidate Packaging 저장 전 Draft 보강 필요"
        next_step = "막힌 항목을 보강하거나, Latest / History / Compare에서 후보 초안을 다시 보내 확인합니다."

    return {
        "ready": ready,
        "score": score,
        "verdict": verdict,
        "next_action": next_step,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": warning_reasons,
        "criteria_rows": [
            {
                "기준": row["criteria"],
                "상태": "PASS" if row["ready"] else "BLOCK",
                "현재 값": row["current"],
                "점수": f"{float(row['points']):g} / {float(row['points']):g}" if row["ready"] else f"0 / {float(row['points']):g}",
                "판단": row["judgment"],
            }
            for row in checks
        ],
    }


def _candidate_review_draft_widget_key(draft: dict[str, Any]) -> str:
    raw = "_".join(
        [
            str(draft.get("source_kind") or "draft"),
            str(draft.get("strategy_key") or draft.get("strategy_name") or "candidate"),
            str(draft.get("created_at") or draft.get("recorded_at") or "unknown"),
        ]
    )
    return "".join(char if char.isalnum() else "_" for char in raw)[:96]


def _candidate_review_decision_label(decision: str) -> str:
    labels = {
        "consider_registry_candidate": "Registry Candidate 검토: 후보 기록으로 남길지 검토",
        "keep_as_near_miss_review": "Near-Miss 검토 노트: 대안 후보로 계속 관찰",
        "keep_as_scenario_review": "Scenario 검토 노트: 설정 비교용으로 유지",
        "needs_more_evidence": "추가 근거 필요: 데이터나 비교가 더 필요",
        "reject_for_now": "Reject For Now: 지금은 후보로 남기지 않음",
    }
    return labels.get(decision, decision)


def _default_candidate_review_decision_from_draft(draft: dict[str, Any]) -> str:
    suggested_type = str(draft.get("suggested_record_type") or "").strip().lower()
    signal = dict(draft.get("real_money_signal") or {})
    promotion = str(signal.get("promotion") or "").strip().lower()
    if suggested_type == "current_candidate_review" or promotion == "real_money_candidate":
        return "consider_registry_candidate"
    if suggested_type == "near_miss_review":
        return "keep_as_near_miss_review"
    if suggested_type == "scenario_review":
        return "keep_as_scenario_review"
    return "needs_more_evidence"


def _default_candidate_review_operator_reason(draft: dict[str, Any], decision: str) -> str:
    strategy_name = str(draft.get("strategy_name") or draft.get("strategy_key") or "candidate")
    result = dict(draft.get("result_snapshot") or {})
    signal = dict(draft.get("real_money_signal") or {})
    base = (
        f"{strategy_name}: CAGR={result.get('cagr') or 'unknown'}, "
        f"MDD={result.get('maximum_drawdown') or 'unknown'}, "
        f"promotion={signal.get('promotion') or 'unknown'}, "
        f"shortlist={signal.get('shortlist') or 'unknown'}."
    )
    if decision == "consider_registry_candidate":
        return f"{base} 후보 기록으로 남길 가치가 있는지 기존 current anchor와 비교가 필요하다."
    if decision == "keep_as_near_miss_review":
        return f"{base} 주 후보는 아니지만 낙폭, 안정성, 설정 차이 측면에서 대안 후보로 다시 볼 가치가 있다."
    if decision == "keep_as_scenario_review":
        return f"{base} 바로 승격하기보다 설정 비교용 scenario로 남겨두는 것이 적절하다."
    if decision == "reject_for_now":
        return f"{base} 현재 근거만으로는 후보 검토를 계속하기 어렵다."
    return f"{base} 후보 판단 전에 데이터 신뢰성, 기존 후보와의 비교, Real-Money 신호를 더 확인해야 한다."


def _default_candidate_review_next_action(decision: str) -> str:
    if decision == "consider_registry_candidate":
        return "기존 current candidate와 같은 기간 / 같은 contract로 compare한 뒤 registry 기록 여부를 결정한다."
    if decision == "keep_as_near_miss_review":
        return "near-miss로 남길지 판단하기 위해 MDD, benchmark gap, data trust를 기존 후보와 비교한다."
    if decision == "keep_as_scenario_review":
        return "scenario 설명이 충분한지 확인하고, 필요할 때 compare 대상으로만 사용한다."
    if decision == "reject_for_now":
        return "현재 초안은 후보 기록으로 남기지 않는다. 같은 아이디어는 새 근거가 생겼을 때 다시 검토한다."
    return "누락 데이터, price freshness, history replay 가능성, Real-Money blocker를 먼저 보강한 뒤 다시 검토한다."


def _build_candidate_review_note_from_draft(
    draft: dict[str, Any],
    *,
    review_decision: str,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
) -> dict[str, Any]:
    return {
        "schema_version": 1,
        "review_note_id": f"candidate_review_note_{uuid4().hex[:12]}",
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "record_status": "active",
        "source_kind": draft.get("source_kind"),
        "source_created_at": draft.get("created_at"),
        "source_recorded_at": draft.get("recorded_at"),
        "strategy_key": draft.get("strategy_key"),
        "strategy_name": draft.get("strategy_name"),
        "suggested_record_type": draft.get("suggested_record_type"),
        "suggested_record_type_label": draft.get("suggested_record_type_label"),
        "review_decision": review_decision,
        "review_decision_label": _candidate_review_decision_label(review_decision),
        "operator_reason": operator_reason,
        "next_action": next_action,
        "review_date": review_date_value.isoformat() if review_date_value else None,
        "result_snapshot": dict(draft.get("result_snapshot") or {}),
        "real_money_signal": dict(draft.get("real_money_signal") or {}),
        "data_trust_snapshot": dict(draft.get("data_trust_snapshot") or {}),
        "settings_snapshot": dict(draft.get("settings_snapshot") or {}),
        "compare_readiness_evaluation": dict(draft.get("compare_readiness_evaluation") or {}),
        "notes": (
            "Created from Backtest > Candidate Review > Candidate Packaging Flow. "
            "This is an operator review note, not CURRENT_CANDIDATE_REGISTRY insertion, "
            "not Pre-Live approval, and not an investment recommendation."
        ),
    }


def _build_candidate_review_notes_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        result = dict(row.get("result_snapshot") or {})
        signal = dict(row.get("real_money_signal") or {})
        data_trust = dict(row.get("data_trust_snapshot") or {})
        display_rows.append(
            {
                "Recorded At": row.get("recorded_at"),
                "Decision": row.get("review_decision_label") or _candidate_review_decision_label(str(row.get("review_decision") or "")),
                "Strategy": row.get("strategy_name") or row.get("strategy_key"),
                "CAGR": result.get("cagr"),
                "MDD": result.get("maximum_drawdown"),
                "Promotion": signal.get("promotion"),
                "Shortlist": signal.get("shortlist"),
                "Data Trust": data_trust.get("price_freshness_status"),
                "Next Action": row.get("next_action"),
                "Review Date": row.get("review_date"),
                "Review Note ID": row.get("review_note_id"),
            }
        )
    return pd.DataFrame(display_rows)


def _candidate_review_note_widget_key(note: dict[str, Any]) -> str:
    raw = "_".join(
        [
            str(note.get("review_note_id") or "review_note"),
            str(note.get("strategy_key") or note.get("strategy_name") or "candidate"),
            str(note.get("recorded_at") or "unknown"),
        ]
    )
    return "".join(char if char.isalnum() else "_" for char in raw)[:96]


def _current_candidate_record_type_label(record_type: str) -> str:
    labels = {
        "current_candidate": "Current Candidate: 현재 기준 후보",
        "near_miss": "Near Miss: 아깝지만 다시 볼 대안",
        "scenario": "Scenario: 설정 비교용 후보",
    }
    return labels.get(record_type, record_type)


def _build_candidate_registry_scope_evaluation(note: dict[str, Any]) -> dict[str, Any]:
    decision = str(note.get("review_decision") or "").strip().lower()
    result = dict(note.get("result_snapshot") or {})
    signal = dict(note.get("real_money_signal") or {})
    data_trust = dict(note.get("data_trust_snapshot") or {})
    settings = dict(note.get("settings_snapshot") or {})
    compare_readiness = dict(note.get("compare_readiness_evaluation") or {})

    result_ready = all(
        _candidate_intake_value_present(result.get(key))
        for key in ("end_balance", "cagr", "maximum_drawdown")
    )
    operator_ready = _candidate_intake_value_present(note.get("operator_reason")) and _candidate_intake_value_present(
        note.get("next_action")
    )
    data_status = str(data_trust.get("price_freshness_status") or "").strip().lower()
    data_ready = bool(data_trust) and data_status != "error"
    real_money_ready = bool(signal) and any(_candidate_intake_value_present(value) for value in signal.values())
    promotion = str(signal.get("promotion") or "").strip().lower()
    deployment = str(signal.get("deployment") or "").strip().lower()
    real_money_not_blocked = (
        real_money_ready
        and promotion not in {"", "hold"}
        and deployment not in {"", "blocked"}
    )
    settings_ready = bool(settings) and any(
        _candidate_intake_value_present(settings.get(key))
        for key in ("tickers", "preset_name", "universe_mode", "universe_contract")
    )
    has_compare_evidence = (
        str(note.get("source_kind") or "").strip().lower() == "compare_focused_strategy"
        or _candidate_intake_value_present(compare_readiness.get("verdict"))
        or _candidate_intake_value_present(compare_readiness.get("score"))
    )
    reject = decision == "reject_for_now"

    warning_reasons: list[str] = []
    if data_status == "warning":
        warning_reasons.append("Data Trust warning")
    if not has_compare_evidence:
        warning_reasons.append("Compare 근거가 Review Note에 직접 남아 있지 않음")
    if decision == "needs_more_evidence":
        warning_reasons.append("추가 근거 필요 상태이므로 registry에는 near-miss 범위만 검토")

    current_scope_ready = (
        decision == "consider_registry_candidate"
        and result_ready
        and operator_ready
        and data_ready
        and real_money_not_blocked
        and settings_ready
        and has_compare_evidence
    )
    near_miss_scope_ready = (
        decision in {"keep_as_near_miss_review", "needs_more_evidence"}
        and result_ready
        and operator_ready
        and data_ready
        and settings_ready
        and not reject
    )
    scenario_scope_ready = (
        decision == "keep_as_scenario_review"
        and operator_ready
        and settings_ready
        and data_ready
        and not reject
    )

    if current_scope_ready:
        scope_label = "CURRENT_CANDIDATE_SCOPE"
        recommended_record_type = "current_candidate"
        allowed_record_types = ["current_candidate"]
        verdict = "Current Candidate registry 저장 가능"
        next_action = "Current Candidate row preview를 확인한 뒤 append 버튼으로 저장합니다."
    elif near_miss_scope_ready:
        scope_label = "NEAR_MISS_SCOPE"
        recommended_record_type = "near_miss"
        allowed_record_types = ["near_miss"]
        verdict = "Near Miss registry 저장 가능"
        next_action = "Near Miss row로 남기되, 다음 비교 / 재검토 조건을 notes에 남깁니다."
    elif scenario_scope_ready:
        scope_label = "SCENARIO_SCOPE"
        recommended_record_type = "scenario"
        allowed_record_types = ["scenario"]
        verdict = "Scenario registry 저장 가능"
        next_action = "Scenario row로 남기고, 비교용 설정이라는 점을 notes에 남깁니다."
    else:
        scope_label = "STOP_OR_REVIEW_MORE"
        recommended_record_type = ""
        allowed_record_types = []
        verdict = "Registry 저장 전 추가 확인 필요"
        next_action = "Review Note의 판단, Data Trust, 설정 snapshot, 비교 근거를 먼저 보강합니다."

    checks = [
        {
            "criteria": "Review Decision",
            "ready": not reject and decision in {
                "consider_registry_candidate",
                "keep_as_near_miss_review",
                "keep_as_scenario_review",
                "needs_more_evidence",
            },
            "points": 2.0,
            "current": _candidate_review_decision_label(decision) if decision else "-",
            "judgment": "registry 범위 검토 가능한 decision" if not reject else "reject는 registry append 중단",
        },
        {
            "criteria": "Result Snapshot",
            "ready": result_ready,
            "points": 1.5,
            "current": (
                f"CAGR={result.get('cagr') or '-'}, "
                f"MDD={result.get('maximum_drawdown') or '-'}, "
                f"End={result.get('end_balance') or '-'}"
            ),
            "judgment": "후보 row에 남길 성과 snapshot 있음" if result_ready else "성과 snapshot 부족",
        },
        {
            "criteria": "Data Trust",
            "ready": data_ready,
            "points": 1.5,
            "current": data_status.upper() if data_status else "SNAPSHOT_ONLY",
            "judgment": "해석 가능" if data_ready else "Data Trust error 또는 snapshot 부족",
        },
        {
            "criteria": "Real-Money Gate",
            "ready": real_money_not_blocked,
            "points": 2.0,
            "current": f"promotion={promotion or '-'}, deployment={deployment or '-'}",
            "judgment": "current 후보 범위 가능" if real_money_not_blocked else "current 후보가 아니라 near-miss/scenario 범위 검토",
        },
        {
            "criteria": "Settings Snapshot",
            "ready": settings_ready,
            "points": 1.5,
            "current": (
                f"universe={settings.get('universe_mode') or settings.get('preset_name') or '-'}, "
                f"tickers={len(settings.get('tickers') or []) if isinstance(settings.get('tickers'), list) else '-'}"
            ),
            "judgment": "후보 row 재진입 정보 있음" if settings_ready else "재현 가능한 설정 부족",
        },
        {
            "criteria": "Compare Evidence",
            "ready": has_compare_evidence or decision in {"keep_as_near_miss_review", "keep_as_scenario_review", "needs_more_evidence"},
            "points": 1.0,
            "current": compare_readiness.get("verdict") or note.get("source_kind") or "-",
            "judgment": "current 후보 근거 있음" if has_compare_evidence else "current 후보 전에는 compare 보강 필요",
        },
        {
            "criteria": "Operator Reason / Next Action",
            "ready": operator_ready,
            "points": 0.5,
            "current": "작성됨" if operator_ready else "미작성",
            "judgment": "후보로 남기는 이유와 다음 행동 있음" if operator_ready else "판단 메모 부족",
        },
    ]

    max_points = sum(float(row["points"]) for row in checks)
    earned_points = sum(float(row["points"]) for row in checks if row["ready"])
    score = round((earned_points / max_points) * 10.0, 1) if max_points else 0.0
    blocking_reasons = [str(row["criteria"]) for row in checks if not row["ready"]]
    if not allowed_record_types and not blocking_reasons:
        blocking_reasons.append("registry에 남길 범위를 결정하지 못함")

    recommended_label = (
        _current_candidate_record_type_label(recommended_record_type)
        if recommended_record_type
        else "Registry append 보류"
    )

    return {
        "scope_label": scope_label,
        "recommended_record_type": recommended_record_type,
        "recommended_record_type_label": recommended_label,
        "allowed_record_types": allowed_record_types,
        "can_prepare_registry_row": bool(allowed_record_types),
        "score": score,
        "verdict": verdict,
        "next_action": next_action,
        "blocking_reasons": blocking_reasons,
        "warning_reasons": warning_reasons,
        "criteria_rows": [
            {
                "기준": row["criteria"],
                "상태": "PASS" if row["ready"] else "CHECK",
                "현재 값": row["current"],
                "점수": f"{float(row['points']):g} / {float(row['points']):g}" if row["ready"] else f"0 / {float(row['points']):g}",
                "판단": row["judgment"],
            }
            for row in checks
        ],
    }


def _candidate_review_registry_record_type_default(note: dict[str, Any]) -> str:
    decision = str(note.get("review_decision") or "").strip().lower()
    if decision == "consider_registry_candidate":
        return "current_candidate"
    if decision == "keep_as_near_miss_review" or decision == "needs_more_evidence":
        return "near_miss"
    return "scenario"


def _infer_strategy_family_from_review_note(note: dict[str, Any]) -> str:
    strategy_key = str(note.get("strategy_key") or "").strip().lower()
    strategy_name = str(note.get("strategy_name") or "").strip().lower()
    combined = f"{strategy_key} {strategy_name}"
    if "quality_value" in combined or "quality + value" in combined:
        return "quality_value"
    if "quality" in combined:
        return "quality"
    if "value" in combined:
        return "value"
    if "gtaa" in combined:
        return "gtaa"
    if "global_relative_strength" in combined or "global relative strength" in combined:
        return "global_relative_strength"
    if "risk_parity" in combined or "risk parity" in combined:
        return "risk_parity_trend"
    if "dual_momentum" in combined or "dual momentum" in combined:
        return "dual_momentum"
    if "equal_weight" in combined or "equal weight" in combined:
        return "equal_weight"
    return "manual_review"


def _candidate_review_registry_role_default(record_type: str, note: dict[str, Any]) -> str:
    decision = str(note.get("review_decision") or "").strip().lower()
    if record_type == "current_candidate":
        return "candidate_from_review_note"
    if record_type == "near_miss":
        if decision == "needs_more_evidence":
            return "needs_more_evidence_near_miss"
        return "review_note_near_miss"
    return "review_note_scenario"


def _slugify_registry_part(value: str) -> str:
    slug = "".join(char.lower() if char.isalnum() else "_" for char in value)
    while "__" in slug:
        slug = slug.replace("__", "_")
    return slug.strip("_") or "candidate"


def _candidate_review_note_to_registry_defaults(note: dict[str, Any]) -> dict[str, str]:
    record_type = _candidate_review_registry_record_type_default(note)
    strategy_family = _infer_strategy_family_from_review_note(note)
    strategy_name = str(note.get("strategy_name") or _strategy_key_to_display_name(note.get("strategy_key")) or note.get("strategy_key") or "")
    role = _candidate_review_registry_role_default(record_type, note)
    title_base = strategy_name or strategy_family.replace("_", " ").title()
    note_suffix = str(note.get("review_note_id") or uuid4().hex[:8]).split("_")[-1]
    registry_id = "_".join(
        [
            _slugify_registry_part(strategy_family),
            _slugify_registry_part(record_type),
            _slugify_registry_part(note_suffix),
        ]
    )
    return {
        "registry_id": registry_id,
        "record_type": record_type,
        "strategy_family": strategy_family,
        "strategy_name": strategy_name,
        "candidate_role": role,
        "title": f"{title_base} review candidate",
        "notes": (
            f"Created from Candidate Review Note `{note.get('review_note_id')}`. "
            f"Decision: {note.get('review_decision_label') or _candidate_review_decision_label(str(note.get('review_decision') or ''))}. "
            f"Operator reason: {note.get('operator_reason') or '-'} "
            f"Next action: {note.get('next_action') or '-'}"
        ),
    }


def _compact_dict_without_empty_values(payload: dict[str, Any]) -> dict[str, Any]:
    return {
        key: value
        for key, value in payload.items()
        if value not in (None, "", [], {})
    }


def _candidate_review_note_contract_snapshot(note: dict[str, Any]) -> dict[str, Any]:
    settings = dict(note.get("settings_snapshot") or {})
    return _compact_dict_without_empty_values(
        {
            "tickers": settings.get("tickers"),
            "top_n": settings.get("top_n") or settings.get("top"),
            "preset_name": settings.get("preset_name"),
            "universe_mode": settings.get("universe_mode"),
            "universe_contract": settings.get("universe_contract"),
            "factor_freq": settings.get("factor_freq"),
            "rebalance_freq": settings.get("rebalance_freq"),
            "benchmark_contract": settings.get("benchmark_contract"),
            "benchmark_ticker": settings.get("benchmark_ticker"),
        }
    )


def _candidate_review_note_execution_context(note: dict[str, Any]) -> dict[str, Any]:
    result = dict(note.get("result_snapshot") or {})
    settings = dict(note.get("settings_snapshot") or {})
    return _compact_dict_without_empty_values(
        {
            "start": result.get("start_date"),
            "end": result.get("end_date"),
            "timeframe": settings.get("timeframe") or "1d",
            "option": settings.get("option") or "month_end",
        }
    )


def _build_current_candidate_registry_row_from_review_note(
    note: dict[str, Any],
    *,
    registry_id: str,
    record_type: str,
    strategy_family: str,
    strategy_name: str,
    candidate_role: str,
    title: str,
    notes: str,
) -> dict[str, Any]:
    result = dict(note.get("result_snapshot") or {})
    signal = dict(note.get("real_money_signal") or {})
    contract = _candidate_review_note_contract_snapshot(note)
    execution_context = _candidate_review_note_execution_context(note)
    return {
        "schema_version": 1,
        "recorded_at": datetime.now().isoformat(timespec="seconds"),
        "status": "active",
        "source_kind": "candidate_review_note_registry_append",
        "source_ref": ".note/finance/registries/CANDIDATE_REVIEW_NOTES.jsonl",
        "source_review_note_id": note.get("review_note_id"),
        "registry_id": str(registry_id).strip(),
        "revision_id": f"rev_{uuid4().hex[:12]}",
        "record_type": record_type,
        "strategy_family": str(strategy_family).strip(),
        "strategy_name": str(strategy_name).strip(),
        "candidate_role": str(candidate_role).strip(),
        "title": str(title).strip() or str(registry_id).strip(),
        "period": {
            "start": result.get("start_date"),
            "end": result.get("end_date"),
        },
        "contract": contract,
        "execution_context": execution_context,
        "compare_prefill": {
            "strategy_name": str(strategy_name).strip(),
            "strategy_override": contract,
        },
        "result": {
            "cagr": result.get("cagr"),
            "mdd": result.get("maximum_drawdown"),
            "sharpe": result.get("sharpe_ratio"),
            "end_balance": result.get("end_balance"),
            "promotion": signal.get("promotion") or "unknown",
            "shortlist": signal.get("shortlist") or "unknown",
            "deployment": signal.get("deployment") or "unknown",
            "validation_status": signal.get("validation_status") or "unknown",
            "monitoring_status": signal.get("monitoring_status") or "unknown",
        },
        "docs": {},
        "review_context": {
            "review_decision": note.get("review_decision"),
            "review_decision_label": note.get("review_decision_label"),
            "operator_reason": note.get("operator_reason"),
            "next_action": note.get("next_action"),
            "review_date": note.get("review_date"),
            "data_trust_snapshot": note.get("data_trust_snapshot") or {},
            "compare_readiness_evaluation": note.get("compare_readiness_evaluation") or {},
        },
        "notes": notes,
    }
