from __future__ import annotations

from datetime import date
from typing import Any

import pandas as pd

from finance.loaders import load_latest_market_date
from finance.performance import portfolio_performance_summary

from .candidate_registry import load_current_candidate_registry_latest
from .final_selection_decisions import (
    FINAL_SELECTION_DECISION_REGISTRY_FILE,
    load_final_selection_decisions,
)


SELECTED_PRACTICAL_PORTFOLIO_ROUTE = "SELECT_FOR_PRACTICAL_PORTFOLIO"

FINAL_SELECTED_PORTFOLIO_STATUS_LABELS = {
    "normal": "정상 관찰",
    "watch": "관찰 필요",
    "rebalance_needed": "리밸런싱 확인 필요",
    "re_review_needed": "재검토 필요",
    "blocked": "운영 대상 차단",
}
FINAL_SELECTED_PORTFOLIO_STATUS_ORDER = [
    "normal",
    "watch",
    "rebalance_needed",
    "re_review_needed",
    "blocked",
]
FINAL_SELECTED_PORTFOLIO_DRIFT_ROUTE_LABELS = {
    "DRIFT_ALIGNED": "목표 비중 근처",
    "DRIFT_WATCH": "비중 관찰 필요",
    "REBALANCE_NEEDED": "리밸런싱 검토 필요",
    "DRIFT_INPUT_INCOMPLETE": "현재 비중 입력 확인 필요",
}
FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS = {
    "current_value": "현재 보유 평가금액으로 계산",
    "shares_x_price": "보유 수량과 가격으로 계산",
    "current_weight": "이미 계산한 현재 비중 입력",
}
FINAL_SELECTED_PORTFOLIO_DRIFT_ALERT_ROUTE_LABELS = {
    "NO_ALERT": "운영 경고 없음",
    "WATCH_ALERT": "관찰 경고",
    "REBALANCE_REVIEW_ALERT": "리밸런싱 검토 경고",
    "INPUT_REVIEW_ALERT": "입력 확인 경고",
}


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


def _clean_text(value: Any, default: str = "-") -> str:
    text = str(value or "").strip()
    return text or default


def _is_selected_practical_portfolio(row: dict[str, Any]) -> bool:
    return (
        row.get("selected_practical_portfolio") is True
        or str(row.get("decision_route") or "").strip() == SELECTED_PRACTICAL_PORTFOLIO_ROUTE
    )


def _active_components(row: dict[str, Any]) -> list[dict[str, Any]]:
    active: list[dict[str, Any]] = []
    for component in list(row.get("selected_components") or []):
        component_row = dict(component or {})
        weight = _optional_float(component_row.get("target_weight")) or 0.0
        if weight > 0.0:
            active.append(component_row)
    return active


def _component_identity(component: dict[str, Any], index: int) -> str:
    registry_id = _clean_text(component.get("registry_id"), "")
    if registry_id:
        return registry_id
    title = _clean_text(component.get("title"), "")
    if title:
        return title
    return f"component_{index + 1}"


def _format_date_value(value: Any) -> str | None:
    if value is None:
        return None
    if hasattr(value, "date"):
        return str(value.date())
    text = str(value).strip()
    return text or None


def _date_text(value: Any) -> str | None:
    formatted = _format_date_value(value)
    if not formatted:
        return None
    parsed = pd.to_datetime(formatted, errors="coerce")
    if pd.isna(parsed):
        return formatted
    return parsed.strftime("%Y-%m-%d")


def _baseline_component_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    raw_decision = dict(row.get("raw_decision") or row)
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    return [dict(item or {}) for item in list(robustness.get("component_rows") or [])]


def _baseline_snapshot(row: dict[str, Any]) -> dict[str, Any]:
    raw_decision = dict(row.get("raw_decision") or row)
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    baseline = dict(paper_snapshot.get("baseline_snapshot") or {})
    component_rows = _baseline_component_rows(raw_decision)
    starts = [_date_text(item.get("Start")) for item in component_rows if _date_text(item.get("Start"))]
    ends = [_date_text(item.get("End")) for item in component_rows if _date_text(item.get("End"))]
    active_components = _active_components(raw_decision)
    if not starts:
        starts = [
            _date_text(component.get("period_start") or component.get("start"))
            for component in active_components
            if _date_text(component.get("period_start") or component.get("start"))
        ]
    if not ends:
        ends = [
            _date_text(component.get("period_end") or component.get("end"))
            for component in active_components
            if _date_text(component.get("period_end") or component.get("end"))
        ]
    baseline_cagr = _optional_float(baseline.get("weighted_cagr"))
    baseline_mdd = _optional_float(baseline.get("weighted_mdd"))
    if baseline_cagr is None and component_rows:
        cagr_values = [_optional_float(item.get("CAGR")) for item in component_rows]
        cagr_values = [value for value in cagr_values if value is not None]
        baseline_cagr = sum(cagr_values) / len(cagr_values) if cagr_values else None
    if baseline_mdd is None and component_rows:
        mdd_values = [_optional_float(item.get("MDD")) for item in component_rows]
        mdd_values = [value for value in mdd_values if value is not None]
        baseline_mdd = min(mdd_values) if mdd_values else None
    return {
        "baseline_start": min(starts) if starts else None,
        "baseline_end": max(ends) if ends else None,
        "baseline_cagr": baseline_cagr,
        "baseline_mdd": baseline_mdd,
        "component_rows": component_rows,
    }


def _target_weight_total(row: dict[str, Any], active_components: list[dict[str, Any]]) -> float:
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    baseline = dict(paper_snapshot.get("baseline_snapshot") or {})
    baseline_total = _optional_float(baseline.get("target_weight_total"))
    if baseline_total is not None:
        return round(baseline_total, 4)
    return round(
        sum((_optional_float(component.get("target_weight")) or 0.0) for component in active_components),
        4,
    )


def _component_benchmarks(active_components: list[dict[str, Any]]) -> list[str]:
    benchmarks = {
        _clean_text(component.get("benchmark"), "")
        for component in active_components
        if _clean_text(component.get("benchmark"), "")
    }
    return sorted(benchmarks)


def _evidence_blockers(row: dict[str, Any]) -> list[str]:
    evidence = dict(row.get("decision_evidence_snapshot") or {})
    blockers = [str(blocker) for blocker in list(evidence.get("blockers") or []) if str(blocker)]
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    blockers.extend(str(blocker) for blocker in list(paper_snapshot.get("blockers") or []) if str(blocker))
    return blockers


def _derive_operation_status(
    row: dict[str, Any],
    *,
    active_components: list[dict[str, Any]],
    target_weight_total: float,
    blockers: list[str],
) -> tuple[str, str]:
    if not _is_selected_practical_portfolio(row):
        return "blocked", "Final Review에서 실전 후보로 선정된 row가 아닙니다."
    if not active_components:
        return "blocked", "선정된 component가 없어 운영 대상으로 볼 수 없습니다."
    if abs(target_weight_total - 100.0) > 0.01:
        return "blocked", f"목표 비중 합계가 100%가 아닙니다. current={target_weight_total:.2f}%"
    if blockers:
        return "re_review_needed", "Final Review evidence 또는 paper observation blocker가 남아 있습니다."

    evidence = dict(row.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(row.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    evidence_route = str(evidence.get("route") or "").strip()
    validation_route = str(risk_snapshot.get("validation_route") or "").strip()
    robustness_route = str(robustness.get("robustness_route") or "").strip()
    paper_route = str(paper_snapshot.get("route") or "").strip()
    watch_routes = []
    if evidence_route and evidence_route != "READY_FOR_FINAL_DECISION":
        watch_routes.append(f"evidence={evidence_route}")
    if validation_route and validation_route != "READY_FOR_ROBUSTNESS_REVIEW":
        watch_routes.append(f"validation={validation_route}")
    if robustness_route and robustness_route != "READY_FOR_STRESS_SWEEP":
        watch_routes.append(f"robustness={robustness_route}")
    if paper_route and paper_route != "PAPER_OBSERVATION_READY":
        watch_routes.append(f"paper={paper_route}")
    if watch_routes:
        return "watch", " / ".join(watch_routes)
    return "normal", "최종 선정 기록, component, 목표 비중, evidence blocker 기준이 운영 대시보드 첫 범위를 통과했습니다."


def build_final_selected_portfolio_dashboard_row(row: dict[str, Any]) -> dict[str, Any]:
    """Convert one Final Review selected decision into the Phase36 dashboard read model."""
    active_components = _active_components(row)
    target_weight_total = _target_weight_total(row, active_components)
    blockers = _evidence_blockers(row)
    operation_status, status_reason = _derive_operation_status(
        row,
        active_components=active_components,
        target_weight_total=target_weight_total,
        blockers=blockers,
    )
    evidence = dict(row.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(row.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(row.get("paper_tracking_snapshot") or {})
    operator_decision = dict(row.get("operator_decision") or {})
    benchmarks = _component_benchmarks(active_components)
    baseline = _baseline_snapshot(row)
    return {
        "decision_id": _clean_text(row.get("decision_id")),
        "updated_at": _clean_text(row.get("updated_at") or row.get("created_at")),
        "decision_route": _clean_text(row.get("decision_route")),
        "source_type": _clean_text(row.get("source_type")),
        "source_id": _clean_text(row.get("source_id")),
        "source_title": _clean_text(row.get("source_title") or row.get("source_id")),
        "operation_status": operation_status,
        "operation_status_label": FINAL_SELECTED_PORTFOLIO_STATUS_LABELS.get(operation_status, operation_status),
        "status_reason": status_reason,
        "component_count": len(active_components),
        "target_weight_total": target_weight_total,
        "benchmarks": benchmarks,
        "benchmark_label": ", ".join(benchmarks) if benchmarks else "-",
        "evidence_route": _clean_text(evidence.get("route")),
        "evidence_score": _optional_float(evidence.get("score")),
        "validation_route": _clean_text(risk_snapshot.get("validation_route")),
        "validation_score": _optional_float(risk_snapshot.get("validation_score")),
        "robustness_route": _clean_text(robustness.get("robustness_route")),
        "robustness_score": _optional_float(robustness.get("robustness_score")),
        "paper_observation_route": _clean_text(paper_snapshot.get("route")),
        "review_cadence": _clean_text(paper_snapshot.get("review_cadence")),
        "review_triggers": list(paper_snapshot.get("review_triggers") or []),
        "blockers": blockers,
        "baseline_start": baseline.get("baseline_start"),
        "baseline_end": baseline.get("baseline_end"),
        "baseline_cagr": baseline.get("baseline_cagr"),
        "baseline_mdd": baseline.get("baseline_mdd"),
        "operator_reason": _clean_text(operator_decision.get("reason")),
        "operator_constraints": _clean_text(operator_decision.get("constraints")),
        "operator_next_action": _clean_text(operator_decision.get("next_action")),
        "live_approval": bool(row.get("live_approval")),
        "order_instruction": bool(row.get("order_instruction")),
        "raw_decision": dict(row),
    }


def build_selected_portfolio_drift_check(
    row: dict[str, Any],
    *,
    current_weights: dict[str, Any],
    drift_threshold_pct: float = 5.0,
    watch_threshold_pct: float = 2.0,
    total_weight_tolerance_pct: float = 1.0,
) -> dict[str, Any]:
    """Compare target weights against operator-provided current weights without creating orders."""
    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    target_weight_total = _target_weight_total(raw_decision, active_components)
    rows: list[dict[str, Any]] = []
    current_weight_total = 0.0
    missing_inputs: list[str] = []
    rebalancing_components: list[str] = []
    watch_components: list[str] = []
    max_abs_drift = 0.0

    for index, component in enumerate(active_components):
        identity = _component_identity(component, index)
        title = _clean_text(component.get("title") or identity)
        target_weight = _optional_float(component.get("target_weight")) or 0.0
        current_weight = _optional_float(current_weights.get(identity))
        if current_weight is None:
            missing_inputs.append(identity)
            current_weight = 0.0
        drift = current_weight - target_weight
        abs_drift = abs(drift)
        max_abs_drift = max(max_abs_drift, abs_drift)
        current_weight_total += current_weight
        if abs_drift >= drift_threshold_pct:
            rebalancing_components.append(identity)
        elif abs_drift >= watch_threshold_pct:
            watch_components.append(identity)
        rows.append(
            {
                "component_id": identity,
                "title": title,
                "target_weight": round(target_weight, 4),
                "current_weight": round(current_weight, 4),
                "drift": round(drift, 4),
                "abs_drift": round(abs_drift, 4),
                "drift_direction": "overweight" if drift > 0 else "underweight" if drift < 0 else "aligned",
                "threshold_breached": abs_drift >= drift_threshold_pct,
                "watch_breached": abs_drift >= watch_threshold_pct,
            }
        )

    total_weight_gap = current_weight_total - target_weight_total
    blockers: list[str] = []
    if not active_components:
        blockers.append("active component 없음")
    if missing_inputs:
        blockers.append("현재 비중 입력 누락")
    if abs(current_weight_total - 100.0) > total_weight_tolerance_pct:
        blockers.append("현재 비중 합계가 100% 근처가 아님")

    if blockers:
        route = "DRIFT_INPUT_INCOMPLETE"
        verdict = "현재 비중 입력을 먼저 확인해야 합니다."
        next_action = "component별 현재 비중을 입력하고 합계가 100% 근처인지 확인합니다."
    elif rebalancing_components:
        route = "REBALANCE_NEEDED"
        verdict = "목표 비중 대비 drift가 커서 리밸런싱 검토가 필요합니다."
        next_action = "주문 지시가 아니라, drift가 큰 component를 검토 목록에 올립니다."
    elif watch_components:
        route = "DRIFT_WATCH"
        verdict = "목표 비중에서 일부 벗어났지만 즉시 리밸런싱 판단 전 관찰이 필요합니다."
        next_action = "다음 점검일에 drift가 커지는지 확인합니다."
    else:
        route = "DRIFT_ALIGNED"
        verdict = "현재 비중이 목표 비중 근처에 있습니다."
        next_action = "정기 점검 주기에 따라 계속 관찰합니다."

    return {
        "route": route,
        "route_label": FINAL_SELECTED_PORTFOLIO_DRIFT_ROUTE_LABELS.get(route, route),
        "verdict": verdict,
        "next_action": next_action,
        "rows": rows,
        "blockers": blockers,
        "rebalancing_components": rebalancing_components,
        "watch_components": watch_components,
        "metrics": {
            "target_weight_total": round(target_weight_total, 4),
            "current_weight_total": round(current_weight_total, 4),
            "total_weight_gap": round(total_weight_gap, 4),
            "max_abs_drift": round(max_abs_drift, 4),
            "drift_threshold_pct": round(float(drift_threshold_pct), 4),
            "watch_threshold_pct": round(float(watch_threshold_pct), 4),
            "total_weight_tolerance_pct": round(float(total_weight_tolerance_pct), 4),
            "active_components": len(active_components),
        },
        "execution_boundary": {
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "This drift check is read-only and does not create broker orders.",
        },
    }


def build_selected_portfolio_current_weight_inputs(
    row: dict[str, Any],
    *,
    component_inputs: dict[str, Any],
    cash_value: Any = 0.0,
    input_mode: str = "current_value",
) -> dict[str, Any]:
    """Convert value or holding inputs into component current weights for drift checks."""
    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    rows: list[dict[str, Any]] = []
    current_weights: dict[str, float] = {}
    missing_inputs: list[str] = []
    invalid_inputs: list[str] = []
    component_value_total = 0.0
    normalized_mode = str(input_mode or "current_value").strip() or "current_value"

    component_value_rows: list[tuple[int, dict[str, Any], str, str, float, dict[str, Any]]] = []
    for index, component in enumerate(active_components):
        identity = _component_identity(component, index)
        title = _clean_text(component.get("title") or identity)
        target_weight = _optional_float(component.get("target_weight")) or 0.0
        input_row = dict((component_inputs or {}).get(identity) or {})
        current_value = _optional_float(input_row.get("current_value"))
        shares = _optional_float(input_row.get("shares"))
        price = _optional_float(input_row.get("price"))
        if current_value is None and shares is not None and price is not None:
            current_value = shares * price

        if current_value is None:
            missing_inputs.append(identity)
            current_value = 0.0
        elif current_value < 0.0:
            invalid_inputs.append(identity)
            current_value = 0.0

        component_value_total += current_value
        component_value_rows.append((index, component, identity, title, target_weight, input_row | {"current_value": current_value}))

    normalized_cash_value = _optional_float(cash_value)
    if normalized_cash_value is None:
        normalized_cash_value = 0.0
    elif normalized_cash_value < 0.0:
        invalid_inputs.append("cash_value")
        normalized_cash_value = 0.0

    portfolio_value_total = component_value_total + normalized_cash_value
    for _index, component, identity, title, target_weight, input_row in component_value_rows:
        current_value = _optional_float(input_row.get("current_value")) or 0.0
        current_weight = (current_value / portfolio_value_total * 100.0) if portfolio_value_total > 0.0 else 0.0
        current_weights[identity] = current_weight
        rows.append(
            {
                "component_id": identity,
                "title": title,
                "target_weight": round(target_weight, 4),
                "symbol": _clean_text(input_row.get("symbol"), ""),
                "shares": _optional_float(input_row.get("shares")),
                "price": _optional_float(input_row.get("price")),
                "price_date": _format_date_value(input_row.get("price_date")),
                "price_source": _clean_text(input_row.get("price_source"), ""),
                "current_value": round(current_value, 4),
                "current_weight": round(current_weight, 4),
                "input_mode": normalized_mode,
                "input_mode_label": FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(normalized_mode, normalized_mode),
                "input_complete": identity not in missing_inputs and identity not in invalid_inputs,
            }
        )

    blockers: list[str] = []
    if not active_components:
        blockers.append("active component 없음")
    if missing_inputs:
        blockers.append("현재 평가금액 입력 누락")
    if invalid_inputs:
        blockers.append("현재 평가금액 또는 현금 입력값이 음수")
    if portfolio_value_total <= 0.0:
        blockers.append("현재 평가금액 합계가 0보다 커야 함")

    return {
        "input_mode": normalized_mode,
        "input_mode_label": FINAL_SELECTED_PORTFOLIO_VALUE_INPUT_MODE_LABELS.get(normalized_mode, normalized_mode),
        "current_weights": current_weights,
        "rows": rows,
        "blockers": blockers,
        "missing_inputs": missing_inputs,
        "invalid_inputs": invalid_inputs,
        "metrics": {
            "component_value_total": round(component_value_total, 4),
            "cash_value": round(normalized_cash_value, 4),
            "portfolio_value_total": round(portfolio_value_total, 4),
            "current_weight_total": round(sum(current_weights.values()), 4),
            "active_components": len(active_components),
        },
        "execution_boundary": {
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
            "notes": "Value and holding inputs only estimate current weights; they do not create broker orders.",
        },
    }


def build_selected_portfolio_drift_alert_preview(
    row: dict[str, Any],
    *,
    drift_check: dict[str, Any],
) -> dict[str, Any]:
    """Translate a drift check into read-only alert and review-trigger guidance."""
    raw_decision = dict(row.get("raw_decision") or row)
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    review_triggers = [
        str(trigger).strip()
        for trigger in list(row.get("review_triggers") or paper_snapshot.get("review_triggers") or [])
        if str(trigger).strip()
    ]
    drift_route = str(drift_check.get("route") or "").strip()
    drift_rows = [dict(item or {}) for item in list(drift_check.get("rows") or [])]
    drift_row_by_id = {str(item.get("component_id") or ""): item for item in drift_rows}
    rebalancing_components = [str(item) for item in list(drift_check.get("rebalancing_components") or [])]
    watch_components = [str(item) for item in list(drift_check.get("watch_components") or [])]
    blockers = [str(item) for item in list(drift_check.get("blockers") or []) if str(item)]
    metrics = dict(drift_check.get("metrics") or {})
    alert_rows: list[dict[str, Any]] = []

    if drift_route == "DRIFT_INPUT_INCOMPLETE":
        alert_route = "INPUT_REVIEW_ALERT"
        alert_level = "input_review"
        verdict = "drift 판단 전에 입력값을 먼저 확인해야 합니다."
        next_action = "현재 비중 / 평가금액 / 보유 수량 입력을 보강한 뒤 다시 확인합니다."
        for blocker in blockers:
            alert_rows.append(
                {
                    "area": "Input Review",
                    "trigger": blocker,
                    "status": "CHECK_INPUT",
                    "current": f"current_weight_total={metrics.get('current_weight_total', '-')}",
                    "next_action": next_action,
                }
            )
    elif drift_route == "REBALANCE_NEEDED":
        alert_route = "REBALANCE_REVIEW_ALERT"
        alert_level = "high"
        verdict = "목표 비중 대비 drift가 리밸런싱 검토 기준을 넘었습니다."
        next_action = "주문 생성이 아니라, drift가 큰 component를 운영 검토 목록에 올립니다."
        for component_id in rebalancing_components:
            component_row = dict(drift_row_by_id.get(component_id) or {})
            alert_rows.append(
                {
                    "area": "Rebalance Review",
                    "trigger": component_row.get("title") or component_id,
                    "status": "THRESHOLD_BREACHED",
                    "current": f"drift={component_row.get('drift', '-')}, abs={component_row.get('abs_drift', '-')}",
                    "next_action": "리밸런싱 필요 여부와 해당 component의 최신 근거를 확인합니다.",
                }
            )
    elif drift_route == "DRIFT_WATCH":
        alert_route = "WATCH_ALERT"
        alert_level = "medium"
        verdict = "목표 비중에서 벗어나기 시작했으므로 다음 관찰 주기에 확인합니다."
        next_action = "watch component의 drift가 확대되는지 review cadence에 맞춰 다시 봅니다."
        for component_id in watch_components:
            component_row = dict(drift_row_by_id.get(component_id) or {})
            alert_rows.append(
                {
                    "area": "Watch Review",
                    "trigger": component_row.get("title") or component_id,
                    "status": "WATCH_BREACHED",
                    "current": f"drift={component_row.get('drift', '-')}, abs={component_row.get('abs_drift', '-')}",
                    "next_action": "다음 점검일에 drift 확대 여부를 확인합니다.",
                }
            )
    else:
        alert_route = "NO_ALERT"
        alert_level = "none"
        verdict = "현재 drift 기준으로 별도 운영 경고는 없습니다."
        next_action = "Final Review에 남긴 review cadence와 trigger에 따라 정기 점검합니다."

    for trigger in review_triggers:
        alert_rows.append(
            {
                "area": "Final Review Trigger",
                "trigger": trigger,
                "status": "REFERENCE_TRIGGER" if alert_route == "NO_ALERT" else "CHECK_WITH_ALERT",
                "current": drift_check.get("route_label") or drift_route or "-",
                "next_action": "drift 경고와 함께 이 trigger가 재검토 조건에 해당하는지 확인합니다."
                if alert_route != "NO_ALERT"
                else "정기 점검 시 이 trigger 기준을 다시 확인합니다.",
            }
        )

    return {
        "alert_route": alert_route,
        "alert_route_label": FINAL_SELECTED_PORTFOLIO_DRIFT_ALERT_ROUTE_LABELS.get(alert_route, alert_route),
        "alert_level": alert_level,
        "verdict": verdict,
        "next_action": next_action,
        "rows": alert_rows,
        "review_triggers": review_triggers,
        "metrics": {
            "review_trigger_count": len(review_triggers),
            "alert_row_count": len(alert_rows),
            "drift_route": drift_route,
            "max_abs_drift": metrics.get("max_abs_drift"),
            "current_weight_total": metrics.get("current_weight_total"),
        },
        "execution_boundary": {
            "live_approval": False,
            "order_instruction": False,
            "alert_persistence": False,
            "notes": "This preview is read-only and does not save alert records or create orders.",
        },
    }


def load_selected_portfolio_latest_market_date(
    *,
    end: str | None = None,
    timeframe: str = "1d",
) -> dict[str, Any]:
    """Return the latest available market date for dashboard recheck defaults."""
    try:
        latest = load_latest_market_date(end=end, timeframe=timeframe)
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        return {"status": "error", "latest_market_date": None, "error": str(exc)}
    return {
        "status": "ok" if latest is not None else "empty",
        "latest_market_date": _format_date_value(latest),
        "error": None,
    }


def build_selected_portfolio_recheck_defaults(row: dict[str, Any]) -> dict[str, Any]:
    """Extract the originally selected validation period for the dashboard recheck controls."""
    baseline = _baseline_snapshot(row)
    latest_result = load_selected_portfolio_latest_market_date()
    latest_date = latest_result.get("latest_market_date")
    return {
        "baseline_start": baseline.get("baseline_start"),
        "baseline_end": baseline.get("baseline_end"),
        "baseline_cagr": baseline.get("baseline_cagr"),
        "baseline_mdd": baseline.get("baseline_mdd"),
        "latest_market_date": latest_date,
        "latest_market_date_status": latest_result.get("status"),
        "latest_market_date_error": latest_result.get("error"),
        "default_start": baseline.get("baseline_start") or "2016-01-01",
        "default_end": latest_date or baseline.get("baseline_end") or date.today().isoformat(),
    }


def _summary_metrics_from_df(result_df: pd.DataFrame, *, name: str, freq: str = "M") -> dict[str, Any]:
    if result_df.empty:
        return {"name": name}
    summary_df = portfolio_performance_summary(result_df, name=name, freq=freq)
    row = dict(summary_df.iloc[0]) if not summary_df.empty else {}
    start_balance = _optional_float(row.get("Start Balance"))
    end_balance = _optional_float(row.get("End Balance"))
    total_return = (end_balance / start_balance - 1.0) if start_balance and end_balance is not None else None
    return {
        "name": name,
        "start_date": _format_date_value(row.get("Start Date")),
        "end_date": _format_date_value(row.get("End Date")),
        "start_balance": start_balance,
        "end_balance": end_balance,
        "total_return": total_return,
        "cagr": _optional_float(row.get("CAGR")),
        "mdd": _optional_float(row.get("Maximum Drawdown")),
        "sharpe": _optional_float(row.get("Sharpe Ratio")),
        "std": _optional_float(row.get("Standard Deviation")),
    }


def _scale_result_df(result_df: pd.DataFrame, *, initial_capital: float) -> pd.DataFrame:
    scaled = result_df[["Date", "Total Balance", "Total Return"]].copy()
    scaled["Date"] = pd.to_datetime(scaled["Date"], errors="coerce")
    scaled = scaled.dropna(subset=["Date", "Total Balance"]).sort_values("Date").reset_index(drop=True)
    if scaled.empty:
        return scaled
    start_balance = _optional_float(scaled["Total Balance"].iloc[0]) or 0.0
    scale = float(initial_capital) / start_balance if start_balance > 0 else 1.0
    scaled["Total Balance"] = pd.to_numeric(scaled["Total Balance"], errors="coerce") * scale
    scaled["Total Return"] = scaled["Total Balance"].pct_change().fillna(0.0)
    return scaled


def _scale_benchmark_df(benchmark_df: pd.DataFrame, *, initial_capital: float) -> pd.DataFrame:
    if benchmark_df is None or benchmark_df.empty or "Benchmark Total Balance" not in benchmark_df.columns:
        return pd.DataFrame()
    scaled = benchmark_df[["Date", "Benchmark Total Balance", "Benchmark Total Return"]].copy()
    scaled["Date"] = pd.to_datetime(scaled["Date"], errors="coerce")
    scaled = scaled.dropna(subset=["Date", "Benchmark Total Balance"]).sort_values("Date").reset_index(drop=True)
    if scaled.empty:
        return scaled
    start_balance = _optional_float(scaled["Benchmark Total Balance"].iloc[0]) or 0.0
    scale = float(initial_capital) / start_balance if start_balance > 0 else 1.0
    scaled["Benchmark Total Balance"] = pd.to_numeric(scaled["Benchmark Total Balance"], errors="coerce") * scale
    scaled["Benchmark Total Return"] = scaled["Benchmark Total Balance"].pct_change().fillna(0.0)
    return scaled


def _combine_component_result_dfs(
    dfs: list[pd.DataFrame],
    *,
    ratios: list[float],
    initial_capital: float,
) -> pd.DataFrame:
    if not dfs:
        return pd.DataFrame()
    normalized_frames: list[pd.DataFrame] = []
    for index, result_df in enumerate(dfs):
        working = result_df[["Date", "Total Balance"]].copy()
        working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
        working["Total Balance"] = pd.to_numeric(working["Total Balance"], errors="coerce")
        working = working.dropna(subset=["Date", "Total Balance"]).sort_values("Date")
        if working.empty:
            continue
        start_balance = _optional_float(working["Total Balance"].iloc[0]) or 0.0
        if start_balance <= 0.0:
            continue
        working[f"component_{index}"] = working["Total Balance"] / start_balance
        normalized_frames.append(working[["Date", f"component_{index}"]].set_index("Date"))
    if not normalized_frames:
        return pd.DataFrame()

    combined = pd.concat(normalized_frames, axis=1, join="inner").sort_index()
    if combined.empty:
        return pd.DataFrame()
    weights = pd.Series(
        [float(ratio or 0.0) for ratio in ratios[: len(combined.columns)]],
        index=list(combined.columns),
        dtype=float,
    )
    if float(weights.sum()) <= 0.0:
        weights = pd.Series([1.0 / len(combined.columns)] * len(combined.columns), index=list(combined.columns))
    else:
        weights = weights / float(weights.sum())
    weighted_balance = combined.mul(weights, axis=1).sum(axis=1) * float(initial_capital)
    output = pd.DataFrame(
        {
            "Date": weighted_balance.index,
            "Total Balance": weighted_balance.values,
        }
    ).reset_index(drop=True)
    output["Total Return"] = output["Total Balance"].pct_change().fillna(0.0)
    return output


def _period_extremes(result_df: pd.DataFrame, *, top_n: int = 3) -> dict[str, list[dict[str, Any]]]:
    if result_df.empty or "Total Return" not in result_df.columns:
        return {"best": [], "worst": []}
    working = result_df[["Date", "Total Balance", "Total Return"]].copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working["Total Return"] = pd.to_numeric(working["Total Return"], errors="coerce")
    working = working.dropna(subset=["Date", "Total Return"])
    if working.empty:
        return {"best": [], "worst": []}
    working["Date"] = working["Date"].dt.strftime("%Y-%m-%d")
    records = working.to_dict("records")
    return {
        "best": sorted(records, key=lambda item: float(item.get("Total Return") or 0.0), reverse=True)[:top_n],
        "worst": sorted(records, key=lambda item: float(item.get("Total Return") or 0.0))[:top_n],
    }


def _find_candidate_rows_by_registry_id() -> dict[str, dict[str, Any]]:
    return {
        str(row.get("registry_id") or "").strip(): row
        for row in load_current_candidate_registry_latest()
        if str(row.get("registry_id") or "").strip()
    }


def build_selected_portfolio_performance_recheck(
    row: dict[str, Any],
    *,
    start: str,
    end: str,
    initial_capital: float = 10000.0,
) -> dict[str, Any]:
    """Replay selected components over a user-selected period and compare against the original baseline."""
    start_ts = pd.to_datetime(start, errors="coerce")
    end_ts = pd.to_datetime(end, errors="coerce")
    if pd.isna(start_ts) or pd.isna(end_ts):
        return {"status": "error", "error": "재검증 시작일과 종료일을 확인해야 합니다."}
    if start_ts > end_ts:
        return {"status": "error", "error": "재검증 시작일은 종료일보다 늦을 수 없습니다."}
    capital = float(initial_capital or 0.0)
    if capital <= 0:
        return {"status": "error", "error": "가상 투자금은 0보다 커야 합니다."}

    raw_decision = dict(row.get("raw_decision") or row)
    active_components = _active_components(raw_decision)
    if not active_components:
        return {"status": "error", "error": "재검증할 active component가 없습니다."}

    try:
        from app.web.backtest_candidate_library_helpers import (
            build_candidate_replay_payload,
            run_candidate_replay_payload,
        )
    except Exception as exc:  # pragma: no cover - defensive import boundary
        return {"status": "error", "error": f"candidate replay helper import failed: {exc}"}

    candidate_by_id = _find_candidate_rows_by_registry_id()
    component_dfs: list[pd.DataFrame] = []
    ratios: list[float] = []
    component_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    first_benchmark_df = pd.DataFrame()
    first_benchmark_label = "-"

    for index, component in enumerate(active_components):
        identity = _component_identity(component, index)
        title = _clean_text(component.get("title") or identity)
        weight = (_optional_float(component.get("target_weight")) or 0.0) / 100.0
        registry_id = _clean_text(component.get("registry_id"), "")
        current_row = candidate_by_id.get(registry_id)
        if not current_row:
            blockers.append(f"{title}: Candidate Registry row를 찾지 못했습니다. registry_id={registry_id or '-'}")
            continue
        try:
            payload = build_candidate_replay_payload(current_row)
            payload["start"] = start_ts.strftime("%Y-%m-%d")
            payload["end"] = end_ts.strftime("%Y-%m-%d")
            bundle = run_candidate_replay_payload(payload, current_row=current_row)
        except Exception as exc:
            blockers.append(f"{title}: 재검증 실행 실패 - {exc}")
            continue

        result_df = bundle.get("result_df")
        if not isinstance(result_df, pd.DataFrame) or result_df.empty:
            blockers.append(f"{title}: 재검증 결과가 비어 있습니다.")
            continue
        component_dfs.append(result_df)
        ratios.append(weight)

        scaled_component_df = _scale_result_df(result_df, initial_capital=capital)
        component_summary = _summary_metrics_from_df(scaled_component_df, name=title)
        component_return = _optional_float(component_summary.get("total_return"))
        component_rows.append(
            {
                "Component": title,
                "Registry ID": registry_id or "-",
                "Target Weight": round(weight * 100.0, 4),
                "Start": component_summary.get("start_date"),
                "End": component_summary.get("end_date"),
                "Total Return": component_return,
                "Weighted Contribution": component_return * weight if component_return is not None else None,
                "CAGR": component_summary.get("cagr"),
                "MDD": component_summary.get("mdd"),
                "Sharpe": component_summary.get("sharpe"),
            }
        )

        benchmark_df = bundle.get("benchmark_chart_df")
        if first_benchmark_df.empty and isinstance(benchmark_df, pd.DataFrame) and not benchmark_df.empty:
            first_benchmark_df = benchmark_df
            first_benchmark_label = str(payload.get("benchmark_ticker") or component.get("benchmark") or "Benchmark")

    if not component_dfs:
        return {
            "status": "error",
            "error": "재검증 가능한 component 결과가 없습니다.",
            "blockers": blockers,
        }

    portfolio_df = _combine_component_result_dfs(component_dfs, ratios=ratios, initial_capital=capital)
    if portfolio_df.empty:
        return {"status": "error", "error": "포트폴리오 성과 합성 결과가 비어 있습니다.", "blockers": blockers}
    portfolio_summary = _summary_metrics_from_df(portfolio_df, name="Selected Portfolio")
    benchmark_scaled = _scale_benchmark_df(first_benchmark_df, initial_capital=capital)
    benchmark_summary = (
        _summary_metrics_from_df(
            benchmark_scaled.rename(
                columns={
                    "Benchmark Total Balance": "Total Balance",
                    "Benchmark Total Return": "Total Return",
                }
            ),
            name=first_benchmark_label,
        )
        if not benchmark_scaled.empty
        else {}
    )

    baseline = _baseline_snapshot(raw_decision)
    latest_cagr = _optional_float(portfolio_summary.get("cagr"))
    latest_mdd = _optional_float(portfolio_summary.get("mdd"))
    baseline_cagr = _optional_float(baseline.get("baseline_cagr"))
    baseline_mdd = _optional_float(baseline.get("baseline_mdd"))
    cagr_delta = latest_cagr - baseline_cagr if latest_cagr is not None and baseline_cagr is not None else None
    mdd_delta = latest_mdd - baseline_mdd if latest_mdd is not None and baseline_mdd is not None else None
    benchmark_cagr = _optional_float(benchmark_summary.get("cagr"))
    net_cagr_spread = latest_cagr - benchmark_cagr if latest_cagr is not None and benchmark_cagr is not None else None
    if blockers:
        verdict_route = "PARTIAL_RECHECK"
        verdict = "일부 component만 재검증되어 결과 해석에 주의가 필요합니다."
    elif cagr_delta is not None and cagr_delta < -0.03:
        verdict_route = "PERFORMANCE_WEAKENED"
        verdict = "원래 검증 대비 CAGR이 의미 있게 낮아졌습니다. 약화 원인을 확인해야 합니다."
    elif mdd_delta is not None and mdd_delta < -0.05:
        verdict_route = "RISK_DRAWDOWN_EXPANDED"
        verdict = "원래 검증 대비 최대 낙폭이 커졌습니다. 리스크 재검토가 필요합니다."
    else:
        verdict_route = "SELECTION_THESIS_HOLDS"
        verdict = "선택한 재검증 기간에서 기존 선정 근거가 대체로 유지됩니다."

    chart_df = portfolio_df[["Date", "Total Balance"]].rename(columns={"Total Balance": "Selected Portfolio"})
    if not benchmark_scaled.empty:
        chart_df = chart_df.merge(
            benchmark_scaled[["Date", "Benchmark Total Balance"]].rename(
                columns={"Benchmark Total Balance": first_benchmark_label}
            ),
            on="Date",
            how="left",
        )

    return {
        "status": "ok" if not blockers else "partial",
        "verdict_route": verdict_route,
        "verdict": verdict,
        "period": {
            "start": start_ts.strftime("%Y-%m-%d"),
            "end": end_ts.strftime("%Y-%m-%d"),
            "baseline_start": baseline.get("baseline_start"),
            "baseline_end": baseline.get("baseline_end"),
            "added_days_vs_baseline": (
                (end_ts - pd.to_datetime(baseline.get("baseline_end"), errors="coerce")).days
                if baseline.get("baseline_end") and not pd.isna(pd.to_datetime(baseline.get("baseline_end"), errors="coerce"))
                else None
            ),
        },
        "initial_capital": capital,
        "portfolio_summary": portfolio_summary,
        "benchmark_summary": benchmark_summary,
        "benchmark_label": first_benchmark_label,
        "baseline_summary": {
            "cagr": baseline_cagr,
            "mdd": baseline_mdd,
            "start": baseline.get("baseline_start"),
            "end": baseline.get("baseline_end"),
        },
        "change_summary": {
            "cagr_delta_vs_baseline": cagr_delta,
            "mdd_delta_vs_baseline": mdd_delta,
            "benchmark_cagr": benchmark_cagr,
            "net_cagr_spread": net_cagr_spread,
        },
        "component_rows": component_rows,
        "chart_df": chart_df,
        "portfolio_result_df": portfolio_df,
        "period_extremes": _period_extremes(portfolio_df),
        "blockers": blockers,
        "execution_boundary": {
            "write_policy": "read_only_recheck",
            "live_approval": False,
            "order_instruction": False,
            "notes": "Performance recheck replays stored candidate contracts over a selected period and does not save portfolio records.",
        },
    }


def load_latest_selected_portfolio_prices(
    symbols: list[str],
    *,
    end: str | None = None,
    timeframe: str = "1d",
    field: str = "close",
) -> dict[str, Any]:
    """Read latest DB prices for optional dashboard input assistance without mutating portfolio records."""
    cleaned_symbols: list[str] = []
    seen: set[str] = set()
    for symbol in symbols:
        cleaned = str(symbol or "").strip().upper()
        if not cleaned or cleaned in seen:
            continue
        seen.add(cleaned)
        cleaned_symbols.append(cleaned)

    if not cleaned_symbols:
        return {
            "status": "empty",
            "rows": [],
            "price_by_symbol": {},
            "missing_symbols": [],
            "error": None,
        }

    try:
        from finance.loaders.price import load_latest_prices
    except Exception as exc:  # pragma: no cover - defensive UI boundary
        return {
            "status": "error",
            "rows": [],
            "price_by_symbol": {},
            "missing_symbols": cleaned_symbols,
            "error": f"latest price loader import failed: {exc}",
        }

    try:
        price_df = load_latest_prices(symbols=cleaned_symbols, end=end, timeframe=timeframe, field=field)
    except Exception as exc:  # pragma: no cover - depends on local MySQL availability
        return {
            "status": "error",
            "rows": [],
            "price_by_symbol": {},
            "missing_symbols": cleaned_symbols,
            "error": str(exc),
        }

    rows: list[dict[str, Any]] = []
    price_by_symbol: dict[str, dict[str, Any]] = {}
    for record in price_df.to_dict("records") if not price_df.empty else []:
        symbol = str(record.get("symbol") or "").strip().upper()
        price = _optional_float(record.get("price"))
        if not symbol or price is None:
            continue
        row = {
            "symbol": symbol,
            "latest_date": _format_date_value(record.get("latest_date")),
            "price": round(price, 6),
            "close": _optional_float(record.get("close")),
            "adj_close": _optional_float(record.get("adj_close")),
            "field": field,
            "timeframe": timeframe,
        }
        rows.append(row)
        price_by_symbol[symbol] = row

    missing_symbols = [symbol for symbol in cleaned_symbols if symbol not in price_by_symbol]
    return {
        "status": "ok" if rows else "empty",
        "rows": rows,
        "price_by_symbol": price_by_symbol,
        "missing_symbols": missing_symbols,
        "error": None,
    }


def _build_summary(
    *,
    all_final_decisions: list[dict[str, Any]],
    selected_rows: list[dict[str, Any]],
    dashboard_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    status_counts = {status: 0 for status in FINAL_SELECTED_PORTFOLIO_STATUS_ORDER}
    for row in dashboard_rows:
        status = str(row.get("operation_status") or "blocked")
        if status not in status_counts:
            status_counts[status] = 0
        status_counts[status] += 1
    return {
        "registry_path": str(FINAL_SELECTION_DECISION_REGISTRY_FILE),
        "final_decision_count": len(all_final_decisions),
        "selected_decision_count": len(selected_rows),
        "dashboard_row_count": len(dashboard_rows),
        "status_counts": status_counts,
        "component_count": sum(int(row.get("component_count") or 0) for row in dashboard_rows),
        "live_approval_enabled_count": sum(1 for row in selected_rows if bool(row.get("live_approval"))),
        "order_instruction_enabled_count": sum(1 for row in selected_rows if bool(row.get("order_instruction"))),
    }


def load_final_selected_portfolio_dashboard(limit: int | None = 250) -> dict[str, Any]:
    """Load Phase36 dashboard data from Final Review decisions without writing new registry rows."""
    all_rows = load_final_selection_decisions(limit=limit)
    selected_rows = [row for row in all_rows if _is_selected_practical_portfolio(row)]
    dashboard_rows = [build_final_selected_portfolio_dashboard_row(row) for row in selected_rows]
    return {
        "all_final_decisions": all_rows,
        "selected_final_decisions": selected_rows,
        "dashboard_rows": dashboard_rows,
        "summary": _build_summary(
            all_final_decisions=all_rows,
            selected_rows=selected_rows,
            dashboard_rows=dashboard_rows,
        ),
    }
