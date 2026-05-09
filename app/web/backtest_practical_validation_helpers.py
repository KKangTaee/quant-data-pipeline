from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import uuid4

import pandas as pd
import streamlit as st

from app.web.runtime import (
    FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
    PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
    append_portfolio_selection_source,
    append_practical_validation_result,
)


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def _slug(value: Any, default: str = "source") -> str:
    raw = str(value or default).strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw)
    return "_".join(part for part in cleaned.split("_") if part) or default


def _now_text() -> str:
    return datetime.now().isoformat(timespec="seconds")


def _metric_snapshot_from_result(result: dict[str, Any]) -> dict[str, Any]:
    return {
        "cagr": _optional_float(result.get("cagr")),
        "mdd": _optional_float(result.get("maximum_drawdown") or result.get("mdd")),
        "sharpe": _optional_float(result.get("sharpe_ratio") or result.get("sharpe")),
        "end_balance": _optional_float(result.get("end_balance")),
    }


def build_selection_source_from_candidate_draft(draft: dict[str, Any]) -> dict[str, Any]:
    """Convert a single run / compare draft into the Clean V2 selection-source contract."""
    created_at = _now_text()
    source_kind = str(draft.get("source_kind") or "latest_backtest_run")
    strategy_name = str(draft.get("strategy_name") or draft.get("strategy_key") or "Strategy")
    source_id = f"selection_{_slug(source_kind)}_{_slug(strategy_name)}_{uuid4().hex[:8]}"
    result = dict(draft.get("result_snapshot") or {})
    settings = dict(draft.get("settings_snapshot") or {})
    data_trust = dict(draft.get("data_trust_snapshot") or {})
    real_money = dict(draft.get("real_money_signal") or {})
    return {
        "schema_version": PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
        "selection_source_id": source_id,
        "created_at": created_at,
        "updated_at": created_at,
        "source_kind": source_kind,
        "source_title": strategy_name,
        "source_status": "selected_for_practical_validation",
        "period": {
            "start": result.get("start_date"),
            "end": result.get("end_date"),
            "actual_start": result.get("start_date") or data_trust.get("actual_result_start"),
            "actual_end": result.get("end_date") or data_trust.get("actual_result_end"),
        },
        "summary": _metric_snapshot_from_result(result),
        "data_trust": {
            "status": data_trust.get("price_freshness_status") or "snapshot",
            "requested_end": data_trust.get("requested_end"),
            "actual_result_start": data_trust.get("actual_result_start"),
            "actual_result_end": data_trust.get("actual_result_end"),
            "result_rows": data_trust.get("result_rows"),
            "warning_count": data_trust.get("warning_count"),
            "excluded_tickers": list(data_trust.get("excluded_tickers") or []),
        },
        "real_money_signal": real_money,
        "components": [
            {
                "component_id": f"{source_id}_component_1",
                "registry_id": draft.get("registry_id"),
                "title": strategy_name,
                "strategy_family": draft.get("strategy_key") or source_kind,
                "strategy_key": draft.get("strategy_key"),
                "strategy_name": strategy_name,
                "target_weight": 100.0,
                "benchmark": settings.get("benchmark_ticker") or "-",
                "universe": settings.get("tickers") or [],
                "baseline_cagr": _optional_float(result.get("cagr")),
                "baseline_mdd": _optional_float(result.get("maximum_drawdown")),
                "baseline_sharpe": _optional_float(result.get("sharpe_ratio")),
                "data_trust_status": data_trust.get("price_freshness_status") or "snapshot",
                "promotion": real_money.get("promotion"),
                "deployment": real_money.get("deployment"),
                "period_start": result.get("start_date"),
                "period_end": result.get("end_date"),
                "replay_contract": {
                    "settings_snapshot": settings,
                    "source_kind": source_kind,
                },
            }
        ],
        "construction": {
            "source": "single_strategy" if source_kind != "compare_focused_strategy" else "compare_focused_strategy",
            "target_weight_total": 100.0,
            "rebalance_cadence": settings.get("rebalance_freq") or settings.get("factor_freq"),
        },
        "source_snapshot": draft,
        "notes": "Clean V2 selection source. It is not a live approval or an investment recommendation.",
    }


def build_selection_source_from_saved_mix_prefill(prefill: dict[str, Any]) -> dict[str, Any]:
    """Convert a replayed saved mix prefill into the Clean V2 selection-source contract."""
    created_at = _now_text()
    saved_id = str(prefill.get("saved_portfolio_id") or "saved_mix")
    saved_name = str(prefill.get("saved_portfolio_name") or saved_id)
    source_id = f"selection_saved_mix_{_slug(saved_id)}_{uuid4().hex[:8]}"
    weighted_summary = dict(prefill.get("weighted_summary") or {})
    weighted_period = dict(prefill.get("weighted_period") or {})
    components: list[dict[str, Any]] = []
    for idx, raw_component in enumerate(list(prefill.get("components") or [])):
        component = dict(raw_component or {})
        component_id = str(component.get("registry_id") or f"{source_id}_component_{idx + 1}")
        components.append(
            {
                "component_id": component_id,
                "registry_id": component.get("registry_id"),
                "title": component.get("title") or component.get("strategy_name") or component_id,
                "strategy_family": component.get("strategy_family"),
                "strategy_key": component.get("strategy_key") or component.get("strategy_family"),
                "strategy_name": component.get("strategy_name"),
                "proposal_role": component.get("proposal_role"),
                "target_weight": _optional_float(component.get("target_weight")) or 0.0,
                "benchmark": component.get("benchmark") or "-",
                "universe": component.get("universe") or [],
                "baseline_cagr": _optional_float(component.get("cagr")),
                "baseline_mdd": _optional_float(component.get("mdd")),
                "data_trust_status": component.get("data_trust_status") or "snapshot",
                "promotion": component.get("promotion"),
                "deployment": component.get("deployment"),
                "period_start": dict(component.get("period") or {}).get("start"),
                "period_end": dict(component.get("period") or {}).get("end"),
                "replay_contract": {
                    "contract": dict(component.get("contract") or {}),
                    "compare_evidence": dict(component.get("compare_evidence") or {}),
                    "saved_portfolio_id": saved_id,
                },
            }
        )
    target_weight_total = round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in components),
        4,
    )
    return {
        "schema_version": PORTFOLIO_SELECTION_SOURCE_SCHEMA_VERSION,
        "selection_source_id": source_id,
        "created_at": created_at,
        "updated_at": created_at,
        "source_kind": "saved_portfolio_mix",
        "source_title": saved_name,
        "source_status": "selected_for_practical_validation",
        "period": {
            "start": weighted_period.get("start"),
            "end": weighted_period.get("end"),
            "actual_start": weighted_period.get("start"),
            "actual_end": weighted_period.get("end"),
        },
        "summary": {
            "cagr": _optional_float(weighted_summary.get("cagr")),
            "mdd": _optional_float(weighted_summary.get("mdd")),
            "sharpe": _optional_float(weighted_summary.get("sharpe_ratio") or weighted_summary.get("sharpe")),
            "end_balance": _optional_float(weighted_summary.get("end_balance")),
        },
        "data_trust": {
            "status": "mix_replay_snapshot",
            "warning_count": 0,
        },
        "real_money_signal": {
            "route": "saved_mix_component_snapshot",
            "blockers": [],
            "review_gaps": [],
        },
        "components": components,
        "construction": {
            "source": "saved_mix",
            "saved_portfolio_id": saved_id,
            "target_weight_total": target_weight_total,
            "date_policy": dict(prefill.get("portfolio_context") or {}).get("date_policy"),
        },
        "source_snapshot": prefill,
        "notes": "Clean V2 saved mix selection source. It is not a live approval or an investment recommendation.",
    }


def queue_practical_validation_source(source: dict[str, Any], *, persist: bool = True) -> None:
    """Send a selected source into the Practical Validation stage and optionally persist it."""
    source_row = dict(source or {})
    if persist:
        append_portfolio_selection_source(source_row)
    st.session_state.backtest_practical_validation_source = source_row
    st.session_state.backtest_practical_validation_notice = (
        f"`{source_row.get('source_title') or source_row.get('selection_source_id')}`를 Practical Validation으로 보냈습니다. "
        "이 기록은 후보 검증 자료이며 live approval이나 주문 지시가 아닙니다."
    )
    st.session_state.backtest_practical_validation_mode = "Selected Source"
    st.session_state.backtest_requested_panel = "Practical Validation"


def build_practical_validation_result(source: dict[str, Any]) -> dict[str, Any]:
    """Build the structured Practical Validation result used by Final Review V2."""
    now = _now_text()
    source_row = dict(source or {})
    source_id = str(source_row.get("selection_source_id") or "").strip()
    components = [dict(item or {}) for item in list(source_row.get("components") or [])]
    active_components = [
        component
        for component in components
        if (_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    target_weight_total = round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in active_components),
        4,
    )
    data_trust = dict(source_row.get("data_trust") or {})
    real_money = dict(source_row.get("real_money_signal") or {})
    hard_blockers: list[str] = []
    review_gaps: list[str] = []
    if not source_id:
        hard_blockers.append("selection_source_id 없음")
    if not active_components:
        hard_blockers.append("active component 없음")
    if active_components and abs(target_weight_total - 100.0) > 0.01:
        hard_blockers.append(f"target weight 합계가 100%가 아님: {target_weight_total:.2f}%")
    if str(data_trust.get("status") or "").lower() in {"error", "blocked"}:
        hard_blockers.append(f"Data Trust blocked: {data_trust.get('status')}")
    if real_money.get("deployment") in {"blocked", "deployment_blocked"}:
        hard_blockers.append("Real-Money deployment blocked")
    if data_trust.get("warning_count"):
        review_gaps.append(f"Data Trust warning {data_trust.get('warning_count')}개")
    if not any(str(component.get("benchmark") or "").strip() not in {"", "-"} for component in active_components):
        review_gaps.append("benchmark snapshot 부족")

    checks = [
        {
            "Criteria": "Selection source",
            "Ready": bool(source_id),
            "Current": source_id or "-",
            "Meaning": "Backtest Analysis에서 선택한 Clean V2 source가 있는지 봅니다.",
        },
        {
            "Criteria": "Active components",
            "Ready": bool(active_components),
            "Current": str(len(active_components)),
            "Meaning": "실전 검증할 component가 있는지 봅니다.",
        },
        {
            "Criteria": "Target weight total",
            "Ready": bool(active_components) and abs(target_weight_total - 100.0) <= 0.01,
            "Current": f"{target_weight_total:.2f}%",
            "Meaning": "포트폴리오 비중 합계가 100%인지 봅니다.",
        },
        {
            "Criteria": "Data Trust",
            "Ready": str(data_trust.get("status") or "").lower() not in {"error", "blocked"},
            "Current": data_trust.get("status") or "snapshot",
            "Meaning": "원본 실행 결과의 Data Trust가 차단 상태인지 봅니다.",
        },
        {
            "Criteria": "Execution boundary",
            "Ready": True,
            "Current": "live approval disabled / order instruction disabled",
            "Meaning": "이 검증은 후보 자료이며 주문이나 자동매매가 아닙니다.",
        },
    ]
    if hard_blockers:
        route = "BLOCKED"
        verdict = "Practical Validation 차단: 먼저 blocker를 해결해야 합니다."
        next_action = "Backtest Analysis에서 설정 / 데이터 / 비중을 다시 확인합니다."
    elif review_gaps:
        route = "NEEDS_REVIEW"
        verdict = "Practical Validation 보강 필요: Final Review 전 확인 항목이 있습니다."
        next_action = "review gap을 확인한 뒤 보류 또는 Final Review 판단으로 넘깁니다."
    else:
        route = "READY_FOR_FINAL_REVIEW"
        verdict = "Final Review로 이동 가능: 실전 후보 검증 자료가 구성되었습니다."
        next_action = "Final Review에서 최종 선택 / 보류 / 거절 / 재검토 판단을 남깁니다."

    return {
        "schema_version": PRACTICAL_VALIDATION_RESULT_SCHEMA_VERSION,
        "validation_id": f"validation_{_slug(source_id)}_{uuid4().hex[:8]}",
        "selection_source_id": source_id,
        "created_at": now,
        "updated_at": now,
        "source_kind": source_row.get("source_kind"),
        "source_title": source_row.get("source_title") or source_id,
        "validation_route": route,
        "validation_score": round((len(checks) - len(hard_blockers)) / len(checks) * 10.0, 1),
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "hard_blockers": hard_blockers,
        "review_gaps": review_gaps,
        "paper_tracking_gaps": [],
        "metrics": {
            "active_components": len(active_components),
            "weight_total": target_weight_total,
            "max_weight": max([_optional_float(component.get("target_weight")) or 0.0 for component in active_components], default=0.0),
        },
        "component_rows": [
            {
                "Component": component.get("title") or component.get("strategy_name") or component.get("component_id"),
                "Role": component.get("proposal_role") or "-",
                "Weight": component.get("target_weight"),
                "CAGR": component.get("baseline_cagr"),
                "MDD": component.get("baseline_mdd"),
                "Benchmark": component.get("benchmark"),
                "Data Trust": component.get("data_trust_status"),
                "Registry ID": component.get("registry_id") or "-",
            }
            for component in active_components
        ],
        "robustness_validation": {
            "robustness_route": "READY_FOR_STRESS_SWEEP" if not hard_blockers else "BLOCKED_FOR_ROBUSTNESS",
            "robustness_score": 8.0 if not hard_blockers else 4.0,
            "verdict": "기본 source snapshot과 component contract가 확인되었습니다." if not hard_blockers else "source blocker가 있어 robustness preview가 차단됩니다.",
            "next_action": "Final Review에서 stress 질문과 관찰 기준을 함께 확인합니다.",
            "blockers": list(hard_blockers),
            "component_rows": [
                {
                    "Component": component.get("title") or component.get("strategy_name") or component.get("component_id"),
                    "Start": component.get("period_start") or dict(source_row.get("period") or {}).get("actual_start"),
                    "End": component.get("period_end") or dict(source_row.get("period") or {}).get("actual_end"),
                    "CAGR": component.get("baseline_cagr"),
                    "MDD": component.get("baseline_mdd"),
                    "Target Weight": component.get("target_weight"),
                }
                for component in active_components
            ],
            "stress_summary_rows": [
                {
                    "Question": "Source replay contract present",
                    "Result Status": "READY" if active_components else "NOT_READY",
                    "Interpretation": "Final Review 이후 dashboard recheck는 selection source snapshot을 우선 사용합니다.",
                }
            ],
        },
        "paper_observation": {
            "mode": "inline_paper_observation",
            "route": "PAPER_OBSERVATION_READY" if not hard_blockers else "PAPER_OBSERVATION_REVIEW",
            "baseline_snapshot": {
                "target_weight_total": target_weight_total,
                "weighted_cagr": dict(source_row.get("summary") or {}).get("cagr"),
                "weighted_mdd": dict(source_row.get("summary") or {}).get("mdd"),
                "active_component_count": len(active_components),
            },
            "active_components": active_components,
            "review_cadence": "monthly_or_rebalance_review",
            "review_triggers": [
                "CAGR deterioration review",
                "MDD expansion review",
                "Benchmark-relative underperformance review",
                "Data Trust refresh review",
            ],
        },
        "selection_source_snapshot": source_row,
        "final_decision_schema_target": FINAL_SELECTION_DECISION_V2_SCHEMA_VERSION,
    }


def save_practical_validation_result(result: dict[str, Any]) -> None:
    append_practical_validation_result(dict(result or {}))


def queue_final_review_source_from_validation(
    *,
    source: dict[str, Any],
    validation_result: dict[str, Any],
    persist_validation: bool = True,
) -> None:
    if persist_validation:
        save_practical_validation_result(validation_result)
    st.session_state.final_review_practical_validation_source = {
        "source": dict(source or {}),
        "validation_result": dict(validation_result or {}),
    }
    st.session_state.final_review_practical_validation_notice = (
        f"`{validation_result.get('source_title') or validation_result.get('selection_source_id')}`를 Final Review로 보냈습니다."
    )
    st.session_state.backtest_requested_panel = "Final Review"


def source_components_dataframe(source: dict[str, Any]) -> pd.DataFrame:
    rows: list[dict[str, Any]] = []
    for component in list(dict(source or {}).get("components") or []):
        component_row = dict(component or {})
        rows.append(
            {
                "Component": component_row.get("title") or component_row.get("strategy_name") or component_row.get("component_id"),
                "Weight": component_row.get("target_weight"),
                "CAGR": component_row.get("baseline_cagr"),
                "MDD": component_row.get("baseline_mdd"),
                "Benchmark": component_row.get("benchmark"),
                "Data Trust": component_row.get("data_trust_status"),
            }
        )
    return pd.DataFrame(rows)
