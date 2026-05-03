from __future__ import annotations

from datetime import date, datetime
from typing import Any

import pandas as pd

from app.web.runtime import (
    FINAL_SELECTION_DECISION_SCHEMA_VERSION,
    PAPER_PORTFOLIO_LEDGER_SCHEMA_VERSION,
    PORTFOLIO_PROPOSAL_SCHEMA_VERSION,
)

PORTFOLIO_PROPOSAL_STATUS_OPTIONS = [
    "draft",
    "review_ready",
    "paper_tracking",
    "hold",
    "rejected",
    "superseded",
    "live_readiness_candidate",
]
PORTFOLIO_PROPOSAL_TYPE_OPTIONS = [
    "balanced_core",
    "lower_drawdown_core",
    "defensive_blend",
    "satellite_pack",
]
PORTFOLIO_PROPOSAL_ROLE_OPTIONS = [
    "core_anchor",
    "return_driver",
    "diversifier",
    "defensive_sleeve",
    "satellite",
    "watch_only",
]
PORTFOLIO_PROPOSAL_ROLE_DESCRIPTIONS = {
    "core_anchor": "포트폴리오의 중심 후보입니다. active weight가 있는 proposal에는 최소 1개가 필요합니다.",
    "return_driver": "수익률을 끌어올리는 공격 후보입니다. 중심 후보 없이 이것만 있으면 Live Readiness 전에 차단됩니다.",
    "diversifier": "core_anchor와 다른 위험 원천을 섞어 변동성과 drawdown을 낮추는 보조 후보입니다.",
    "defensive_sleeve": "시장 악화나 risk-off 구간을 완충하기 위한 방어 후보입니다.",
    "satellite": "작은 비중으로 특정 아이디어를 더하는 보조 후보입니다.",
    "watch_only": "이번 proposal에서는 관찰만 하고 active weight를 주지 않는 후보입니다.",
}
PORTFOLIO_PROPOSAL_WEIGHTING_OPTIONS = ["manual_weight", "equal_weight"]
PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD = -2.0
PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD = -5.0
PORTFOLIO_RISK_MAX_REVIEW_WEIGHT = 70.0
PORTFOLIO_ROBUSTNESS_MIN_WINDOW_YEARS = 5.0
PORTFOLIO_ROBUSTNESS_STRESS_SCHEMA_VERSION = "phase32_stress_summary_v1"
PAPER_PORTFOLIO_LEDGER_STATUS_OPTIONS = [
    "active_tracking",
    "watch",
    "paused",
    "re_review",
    "closed",
]
PAPER_PORTFOLIO_LEDGER_REVIEW_CADENCE_OPTIONS = [
    "weekly_review",
    "monthly_review",
    "quarterly_review",
    "rebalance_cadence_review",
    "event_driven_review",
]
FINAL_SELECTION_DECISION_ROUTE_OPTIONS = [
    "SELECT_FOR_PRACTICAL_PORTFOLIO",
    "HOLD_FOR_MORE_PAPER_TRACKING",
    "REJECT_FOR_PRACTICAL_USE",
    "RE_REVIEW_REQUIRED",
]
FINAL_SELECTION_DECISION_ROUTE_DESCRIPTIONS = {
    "SELECT_FOR_PRACTICAL_PORTFOLIO": "실전 후보로 선정하고 Phase 35 운영 가이드 작성으로 넘깁니다. 승인/주문은 아닙니다.",
    "HOLD_FOR_MORE_PAPER_TRACKING": "paper tracking 기간이나 trigger 확인이 더 필요해 보류합니다.",
    "REJECT_FOR_PRACTICAL_USE": "현재 근거로는 실전 후보에서 제외합니다.",
    "RE_REVIEW_REQUIRED": "구성, 비중, stress, paper tracking 조건을 재검토해야 합니다.",
}


# Parse a proposal component target weight into a safe float.
def _component_target_weight(component_input: dict[str, Any]) -> float:
    try:
        return float(component_input.get("target_weight") or 0.0)
    except (TypeError, ValueError):
        return 0.0


# Turn a current candidate row into an OK / warning / missing data trust label for proposal components.
def _portfolio_proposal_candidate_data_trust_status(row: dict[str, Any] | None) -> str:
    if not row:
        return "not_attached"
    review_context = dict(row.get("review_context") or {})
    data_trust = dict(review_context.get("data_trust_snapshot") or {})
    if not data_trust:
        return "not_attached"
    warning_count = data_trust.get("warning_count")
    excluded_tickers = list(data_trust.get("excluded_tickers") or [])
    malformed_count = int(data_trust.get("malformed_price_row_count") or 0)
    if malformed_count > 0:
        return "warning"
    try:
        if int(warning_count or 0) > 0:
            return "warning"
    except (TypeError, ValueError):
        return "warning"
    if excluded_tickers:
        return "warning"
    return "ok"


# Parse dates from registry snapshots that may store either date-only or timestamp strings.
def _portfolio_robustness_parse_date(value: Any) -> datetime | None:
    if value in (None, ""):
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, date):
        return datetime.combine(value, datetime.min.time())
    raw = str(value).strip()
    if not raw:
        return None
    for candidate in (raw, raw.replace("Z", "+00:00")):
        try:
            return datetime.fromisoformat(candidate)
        except ValueError:
            pass
    for fmt in ("%Y-%m-%d %H:%M:%S", "%Y-%m-%d"):
        try:
            return datetime.strptime(raw[:19] if "%H" in fmt else raw[:10], fmt)
        except ValueError:
            pass
    return None


def _portfolio_robustness_period_years(period: dict[str, Any]) -> float | None:
    start = _portfolio_robustness_parse_date(period.get("start"))
    end = _portfolio_robustness_parse_date(period.get("end"))
    if not start or not end or end <= start:
        return None
    return round((end - start).days / 365.25, 2)


def _portfolio_robustness_has_compare_evidence(row: dict[str, Any]) -> bool:
    compare_evidence = dict(row.get("compare_evidence") or {})
    comparison_snapshot = dict(compare_evidence.get("comparison_snapshot") or {})
    return bool(comparison_snapshot)


def _portfolio_robustness_contract_summary(contract: dict[str, Any]) -> str:
    if not contract:
        return "missing"
    keys = [
        "benchmark_ticker",
        "top_n",
        "top",
        "interval",
        "rebalance_freq",
        "factor_freq",
        "trend_filter_window",
        "score_lookback_months",
        "transaction_cost_bps",
    ]
    summary_parts = []
    for key in keys:
        if key in contract and contract.get(key) not in (None, ""):
            summary_parts.append(f"{key}={contract.get(key)}")
    return ", ".join(summary_parts[:5]) or f"{len(contract)} fields"


def _portfolio_robustness_format_percent(value: float | None) -> str:
    if value is None:
        return "-"
    return f"{value * 100:.1f}%"


def _portfolio_robustness_baseline_summary(active_components: list[dict[str, Any]]) -> dict[str, Any]:
    weighted_cagr = 0.0
    weighted_mdd = 0.0
    total_weight = 0.0
    cagr_complete = True
    mdd_complete = True
    years_values: list[float] = []
    for row in active_components:
        weight = _portfolio_proposal_optional_float(row.get("target_weight")) or 0.0
        cagr = _portfolio_proposal_optional_float(row.get("cagr"))
        mdd = _portfolio_proposal_optional_float(row.get("mdd"))
        years = _portfolio_robustness_period_years(dict(row.get("period") or {}))
        if cagr is None:
            cagr_complete = False
        else:
            weighted_cagr += cagr * weight
        if mdd is None:
            mdd_complete = False
        else:
            weighted_mdd += mdd * weight
        if years is not None:
            years_values.append(years)
        total_weight += weight
    baseline_cagr = weighted_cagr / total_weight if total_weight > 0.0 and cagr_complete else None
    baseline_mdd = weighted_mdd / total_weight if total_weight > 0.0 and mdd_complete else None
    min_years = min(years_values) if years_values else None
    return {
        "weighted_cagr": baseline_cagr,
        "weighted_mdd": baseline_mdd,
        "min_years": min_years,
        "weight_total": round(total_weight, 2),
        "component_count": len(active_components),
        "baseline_label": (
            f"CAGR {_portfolio_robustness_format_percent(baseline_cagr)} / "
            f"MDD {_portfolio_robustness_format_percent(baseline_mdd)} / "
            f"min years {min_years if min_years is not None else '-'}"
        ),
    }


def _portfolio_robustness_target_weight_total(active_components: list[dict[str, Any]]) -> float:
    total = 0.0
    for row in active_components:
        total += _portfolio_proposal_optional_float(row.get("target_weight")) or 0.0
    return round(total, 4)


def _portfolio_robustness_stress_result_contract() -> dict[str, Any]:
    return {
        "schema_version": PORTFOLIO_ROBUSTNESS_STRESS_SCHEMA_VERSION,
        "row_identity": ["source_type", "source_id", "stress_id"],
        "status_values": {
            "input_status": ["READY", "INPUT_GAP", "BLOCKED", "NOT_APPLICABLE"],
            "result_status": ["NOT_RUN", "PASS", "WATCH", "FAIL"],
        },
        "metric_fields": [
            "baseline_cagr",
            "baseline_mdd",
            "stress_cagr",
            "stress_mdd",
            "cagr_delta",
            "mdd_delta",
        ],
        "phase32_scope": "read-only summary contract; actual stress execution engine is future work",
    }


def _portfolio_robustness_stress_row(
    *,
    stress_id: str,
    category: str,
    scenario: str,
    ready: bool,
    robustness_route: str,
    baseline_label: str,
    expected_check: str,
    decision_use: str,
    next_action: str,
    not_applicable: bool = False,
) -> dict[str, Any]:
    if not_applicable:
        input_status = "NOT_APPLICABLE"
        judgment = "이 source에는 적용하지 않음"
    elif robustness_route == "BLOCKED_FOR_ROBUSTNESS":
        input_status = "BLOCKED"
        judgment = "robustness blocker 선해결 필요"
    elif ready:
        input_status = "READY"
        judgment = "실행 입력 준비됨"
    else:
        input_status = "INPUT_GAP"
        judgment = "stress 실행 전 입력 보강 필요"
    return {
        "Stress ID": stress_id,
        "Category": category,
        "Scenario": scenario,
        "Input Status": input_status,
        "Result Status": "NOT_RUN",
        "Baseline": baseline_label,
        "Expected Check": expected_check,
        "Judgment": judgment,
        "Decision Use": decision_use,
        "Next Action": next_action,
    }


def _build_portfolio_stress_summary_rows(
    *,
    source_type: str,
    active_components: list[dict[str, Any]],
    robustness_route: str,
    has_all_periods: bool,
    has_all_contracts: bool,
    has_all_benchmarks: bool,
    has_all_compare_evidence: bool,
) -> list[dict[str, Any]]:
    baseline = _portfolio_robustness_baseline_summary(active_components)
    baseline_label = str(baseline.get("baseline_label") or "-")
    has_long_windows = bool(
        active_components
        and all(
            (_portfolio_robustness_period_years(dict(row.get("period") or {})) or 0.0)
            >= PORTFOLIO_ROBUSTNESS_MIN_WINDOW_YEARS
            for row in active_components
        )
    )
    is_multi_component = source_type == "portfolio_proposal" and len(active_components) > 1
    weight_total = _portfolio_robustness_target_weight_total(active_components)
    weights_ready = is_multi_component and abs(weight_total - 100.0) <= 0.01
    return [
        _portfolio_robustness_stress_row(
            stress_id="period_split",
            category="Period",
            scenario="early / middle / recent 구간 분할",
            ready=has_all_periods and has_long_windows,
            robustness_route=robustness_route,
            baseline_label=baseline_label,
            expected_check="각 구간에서 CAGR / MDD 방향성이 유지되는지 확인",
            decision_use="특정 장기 구간에만 의존한 후보인지 판단",
            next_action="기간 분할 백테스트 runner가 붙으면 같은 contract로 구간별 결과를 채운다.",
        ),
        _portfolio_robustness_stress_row(
            stress_id="recent_window",
            category="Recent",
            scenario="최근 3Y / 5Y stress",
            ready=has_all_periods,
            robustness_route=robustness_route,
            baseline_label=baseline_label,
            expected_check="최근 구간의 성과 저하와 MDD 확대를 확인",
            decision_use="paper tracking 시작 전 최근 성과 이탈 여부 판단",
            next_action="최근 구간 result를 계산해 baseline 대비 deterioration을 표시한다.",
        ),
        _portfolio_robustness_stress_row(
            stress_id="benchmark_sensitivity",
            category="Benchmark",
            scenario="primary benchmark / SPY reference 비교",
            ready=has_all_benchmarks and has_all_compare_evidence,
            robustness_route=robustness_route,
            baseline_label=baseline_label,
            expected_check="benchmark를 바꿔도 후보 해석이 유지되는지 확인",
            decision_use="benchmark 선택 때문에 좋아 보이는 결과인지 판단",
            next_action="compare evidence와 formal benchmark 기준을 같이 채운다.",
        ),
        _portfolio_robustness_stress_row(
            stress_id="parameter_sensitivity",
            category="Parameter",
            scenario="top-N / lookback / rebalance interval sensitivity",
            ready=has_all_contracts,
            robustness_route=robustness_route,
            baseline_label=baseline_label,
            expected_check="주요 parameter를 조금 바꿔도 결과가 과도하게 무너지지 않는지 확인",
            decision_use="특정 parameter 조합에만 맞춘 후보인지 판단",
            next_action="contract snapshot 기반으로 family별 parameter sweep 후보를 만든다.",
        ),
        _portfolio_robustness_stress_row(
            stress_id="weight_sensitivity",
            category="Portfolio",
            scenario="component target weight +/-10% sensitivity",
            ready=weights_ready,
            robustness_route=robustness_route,
            baseline_label=baseline_label,
            expected_check="비중을 조금 바꿔도 proposal 성격이 유지되는지 확인",
            decision_use="paper ledger target weight가 지나치게 섬세한지 판단",
            next_action="다중 후보 proposal에서 target weight 주변 stress 결과를 채운다.",
            not_applicable=not is_multi_component,
        ),
        _portfolio_robustness_stress_row(
            stress_id="leave_one_out",
            category="Portfolio",
            scenario="component leave-one-out stress",
            ready=is_multi_component,
            robustness_route=robustness_route,
            baseline_label=baseline_label,
            expected_check="한 component를 제외해도 proposal이 완전히 무너지지 않는지 확인",
            decision_use="단일 component 의존도가 큰 proposal인지 판단",
            next_action="다중 후보 proposal에서 component를 하나씩 제외한 결과를 채운다.",
            not_applicable=not is_multi_component,
        ),
    ]


def _build_portfolio_phase33_handoff(
    *,
    source_type: str,
    source_id: str,
    active_components: list[dict[str, Any]],
    robustness_route: str,
    robustness_score: float,
    stress_summary_rows: list[dict[str, Any]],
) -> dict[str, Any]:
    input_gap_count = sum(1 for row in stress_summary_rows if row.get("Input Status") == "INPUT_GAP")
    blocked_count = sum(1 for row in stress_summary_rows if row.get("Input Status") == "BLOCKED")
    ready_count = sum(1 for row in stress_summary_rows if row.get("Input Status") == "READY")
    active_weight_total = _portfolio_robustness_target_weight_total(active_components)
    benchmarks = sorted({str(row.get("benchmark") or "-") for row in active_components if str(row.get("benchmark") or "").strip()})
    has_component_weights = bool(active_components) and (
        source_type == "single_candidate" or abs(active_weight_total - 100.0) <= 0.01
    )
    has_tracking_benchmark = bool(benchmarks)
    requirements = [
        {
            "Requirement": "Paper ledger source",
            "Status": "READY" if source_id else "BLOCKED",
            "Current": source_id or "-",
            "Why It Matters": "Phase 33 paper ledger가 어떤 후보 / proposal을 추적하는지 고정한다.",
        },
        {
            "Requirement": "Component weights",
            "Status": "READY" if has_component_weights else "INPUT_GAP",
            "Current": f"{active_weight_total:.1f}%",
            "Why It Matters": "paper portfolio 시작 비중과 이후 성과 추적 기준이 된다.",
        },
        {
            "Requirement": "Tracking benchmark",
            "Status": "READY" if has_tracking_benchmark else "INPUT_GAP",
            "Current": ", ".join(benchmarks) or "-",
            "Why It Matters": "paper 성과를 무엇과 비교할지 정한다.",
        },
        {
            "Requirement": "Stress summary contract",
            "Status": "READY" if ready_count > 0 and blocked_count == 0 else "INPUT_GAP",
            "Current": f"ready={ready_count}, input_gap={input_gap_count}, blocked={blocked_count}",
            "Why It Matters": "paper tracking 전에 남은 robustness 질문을 Phase 33이 이어받는다.",
        },
    ]
    if robustness_route == "BLOCKED_FOR_ROBUSTNESS" or blocked_count > 0:
        handoff_route = "BLOCKED_FOR_PAPER_LEDGER"
        verdict = "Phase 33 handoff 차단: robustness blocker 선해결 필요"
        next_action = "기간 / 성과 / 설정 snapshot blocker를 해결한 뒤 paper ledger 준비를 다시 봅니다."
    elif robustness_route == "NEEDS_ROBUSTNESS_INPUT_REVIEW" or input_gap_count > 0:
        handoff_route = "NEEDS_STRESS_INPUT_REVIEW"
        verdict = "Phase 33 전 입력 보강 필요: stress gap이 남아 있음"
        next_action = "benchmark, compare evidence, 기간 길이, weight gap을 보강한 뒤 paper ledger 초안을 만듭니다."
    else:
        handoff_route = "READY_FOR_PAPER_LEDGER_PREP"
        verdict = "Phase 33 paper ledger 준비 가능: 후보 / proposal 추적 조건을 만들 수 있음"
        next_action = "Phase 33에서 시작일, target weight, review cadence, stop/re-review trigger를 가진 paper ledger row를 만듭니다."
    handoff_score = min(10.0, round(robustness_score + max(0, ready_count - input_gap_count) * 0.2, 1))
    return {
        "handoff_route": handoff_route,
        "handoff_score": handoff_score,
        "verdict": verdict,
        "next_action": next_action,
        "requirements": requirements,
        "metrics": {
            "ready_stress_rows": ready_count,
            "input_gap_stress_rows": input_gap_count,
            "blocked_stress_rows": blocked_count,
            "active_weight_total": round(active_weight_total, 2),
        },
    }


def _paper_ledger_slug(value: Any) -> str:
    raw = str(value or "").strip().lower()
    cleaned = "".join(char if char.isalnum() else "_" for char in raw)
    return "_".join(part for part in cleaned.split("_") if part) or "source"


def _paper_ledger_parse_trigger_lines(value: str) -> list[str]:
    triggers = [line.strip("- ").strip() for line in str(value or "").splitlines()]
    return [line for line in triggers if line]


def _paper_ledger_default_benchmark(validation: dict[str, Any]) -> str:
    component_rows = [dict(row or {}) for row in list(validation.get("component_rows") or [])]
    benchmarks = [
        str(row.get("Benchmark") or "").strip()
        for row in component_rows
        if str(row.get("Benchmark") or "").strip() not in {"", "-"}
    ]
    if benchmarks:
        return benchmarks[0]
    robustness = dict(validation.get("robustness_validation") or {})
    phase33_handoff = dict(robustness.get("phase33_handoff") or {})
    for requirement in list(phase33_handoff.get("requirements") or []):
        requirement = dict(requirement or {})
        if requirement.get("Requirement") == "Tracking benchmark":
            current = str(requirement.get("Current") or "").strip()
            if current and current != "-":
                return current.split(",")[0].strip()
    return "SPY"


def _paper_ledger_target_components(validation: dict[str, Any]) -> list[dict[str, Any]]:
    components: list[dict[str, Any]] = []
    for row in list(validation.get("component_rows") or []):
        row = dict(row or {})
        components.append(
            {
                "registry_id": row.get("Registry ID"),
                "title": row.get("Title"),
                "proposal_role": row.get("Role"),
                "target_weight": _portfolio_proposal_optional_float(row.get("Weight")) or 0.0,
                "strategy_family": row.get("Family"),
                "benchmark": row.get("Benchmark"),
                "universe": row.get("Universe"),
                "factors": row.get("Factors"),
                "pre_live_status": row.get("Pre-Live"),
                "data_trust_status": row.get("Data Trust"),
                "promotion": row.get("Promotion"),
                "deployment": row.get("Deployment"),
                "baseline_cagr": row.get("CAGR"),
                "baseline_mdd": row.get("MDD"),
            }
        )
    return components


def _paper_ledger_baseline_snapshot(validation: dict[str, Any]) -> dict[str, Any]:
    components = _paper_ledger_target_components(validation)
    active_components = [
        component
        for component in components
        if (_portfolio_proposal_optional_float(component.get("target_weight")) or 0.0) > 0.0
    ]
    weighted_cagr = 0.0
    weighted_mdd = 0.0
    total_weight = 0.0
    cagr_complete = True
    mdd_complete = True
    for component in active_components:
        weight = _portfolio_proposal_optional_float(component.get("target_weight")) or 0.0
        cagr = _portfolio_proposal_optional_float(component.get("baseline_cagr"))
        mdd = _portfolio_proposal_optional_float(component.get("baseline_mdd"))
        if cagr is None:
            cagr_complete = False
        else:
            weighted_cagr += cagr * weight
        if mdd is None:
            mdd_complete = False
        else:
            weighted_mdd += mdd * weight
        total_weight += weight
    return {
        "component_count": len(components),
        "active_component_count": len(active_components),
        "target_weight_total": round(total_weight, 4),
        "weighted_cagr": round(weighted_cagr / total_weight, 6) if total_weight > 0 and cagr_complete else None,
        "weighted_mdd": round(weighted_mdd / total_weight, 6) if total_weight > 0 and mdd_complete else None,
    }


def _build_paper_portfolio_ledger_save_evaluation(
    *,
    validation: dict[str, Any],
    ledger_id: str,
    source_is_persisted: bool,
    tracking_start_date: date | None,
    tracking_benchmark: str,
    review_cadence: str,
    review_triggers: list[str],
    existing_ledger_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Evaluate whether a validation pack can be saved as a durable paper ledger row."""
    existing_ledger_ids = existing_ledger_ids or set()
    robustness = dict(validation.get("robustness_validation") or {})
    phase33_handoff = dict(robustness.get("phase33_handoff") or {})
    handoff_route = str(phase33_handoff.get("handoff_route") or "")
    baseline = _paper_ledger_baseline_snapshot(validation)
    identity_ready = bool(str(ledger_id or "").strip()) and str(ledger_id or "").strip() not in existing_ledger_ids
    source_ready = bool(validation.get("source_type") and validation.get("source_id") and source_is_persisted)
    handoff_ready = handoff_route == "READY_FOR_PAPER_LEDGER_PREP"
    components_ready = bool(baseline.get("active_component_count")) and abs(float(baseline.get("target_weight_total") or 0.0) - 100.0) <= 0.01
    tracking_ready = bool(tracking_start_date and str(tracking_benchmark or "").strip() and review_cadence)
    triggers_ready = bool(review_triggers)
    checks = [
        {
            "criteria": "Ledger Identity",
            "ready": identity_ready,
            "current_value": ledger_id or "-",
            "judgment": "ledger id 사용 가능" if identity_ready else "ledger id 중복 또는 누락",
            "score": 1.4,
        },
        {
            "criteria": "Persisted Source",
            "ready": source_ready,
            "current_value": f"{validation.get('source_type')} / {validation.get('source_id')}",
            "judgment": "저장된 후보 또는 proposal source" if source_ready else "proposal draft를 먼저 저장하거나 source id를 확인",
            "score": 1.8,
        },
        {
            "criteria": "Phase 33 Handoff",
            "ready": handoff_ready,
            "current_value": handoff_route or "-",
            "judgment": "paper ledger 준비 가능" if handoff_ready else "Phase 32 stress input gap 선확인 필요",
            "score": 2.0,
        },
        {
            "criteria": "Target Components",
            "ready": components_ready,
            "current_value": f"active={baseline.get('active_component_count')}, weight={baseline.get('target_weight_total')}%",
            "judgment": "추적 비중 합계 100%" if components_ready else "active component 또는 비중 합계 확인 필요",
            "score": 1.8,
        },
        {
            "criteria": "Tracking Rules",
            "ready": tracking_ready,
            "current_value": f"start={tracking_start_date}, benchmark={tracking_benchmark or '-'}, cadence={review_cadence or '-'}",
            "judgment": "시작일 / benchmark / review cadence 설정됨" if tracking_ready else "추적 시작 조건 보강 필요",
            "score": 1.6,
        },
        {
            "criteria": "Review Triggers",
            "ready": triggers_ready,
            "current_value": f"triggers={len(review_triggers)}",
            "judgment": "재검토 trigger 있음" if triggers_ready else "stop / re-review trigger 필요",
            "score": 1.4,
        },
    ]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    blockers = [str(check["criteria"]) for check in checks if not check["ready"]]
    if not blockers:
        route = "PAPER_LEDGER_SAVE_READY"
        verdict = "Paper ledger 저장 가능: 실제 돈 없이 추적 조건을 남길 수 있음"
        next_action = "Save Paper Tracking Ledger를 눌러 append-only ledger에 기록합니다."
    elif source_ready and handoff_ready and components_ready:
        route = "PAPER_LEDGER_DRAFT_NEEDS_INPUT"
        verdict = "Paper ledger 초안 보강 필요: 추적 규칙이나 trigger가 부족함"
        next_action = "tracking start date, benchmark, review cadence, trigger를 채운 뒤 저장합니다."
    else:
        route = "PAPER_LEDGER_BLOCKED"
        verdict = "Paper ledger 저장 차단: source 또는 Phase 33 handoff를 먼저 확인"
        next_action = "저장된 source와 Phase 32 handoff, target weight를 먼저 보강합니다."
    return {
        "route": route,
        "score": min(score, 10.0),
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "blockers": blockers,
        "can_save": not blockers,
    }


def _build_paper_portfolio_ledger_row(
    *,
    validation: dict[str, Any],
    ledger_id: str,
    paper_status: str,
    tracking_start_date: date,
    tracking_benchmark: str,
    review_cadence: str,
    review_triggers: list[str],
    operator_note: str,
) -> dict[str, Any]:
    """Convert a validation pack and user tracking inputs into one append-only ledger row."""
    now = datetime.now().isoformat(timespec="seconds")
    robustness = dict(validation.get("robustness_validation") or {})
    phase33_handoff = dict(robustness.get("phase33_handoff") or {})
    stress_rows = list(robustness.get("stress_summary_rows") or [])
    target_components = _paper_ledger_target_components(validation)
    return {
        "schema_version": PAPER_PORTFOLIO_LEDGER_SCHEMA_VERSION,
        "ledger_id": str(ledger_id or "").strip(),
        "created_at": now,
        "updated_at": now,
        "paper_status": paper_status,
        "source_type": validation.get("source_type"),
        "source_id": validation.get("source_id"),
        "source_title": validation.get("source_label") or validation.get("source_id"),
        "tracking_start_date": tracking_start_date.isoformat(),
        "tracking_benchmark": str(tracking_benchmark or "").strip(),
        "review_cadence": review_cadence,
        "target_components": target_components,
        "phase32_handoff_snapshot": {
            "validation_route": validation.get("validation_route"),
            "validation_score": validation.get("validation_score"),
            "robustness_route": robustness.get("robustness_route"),
            "robustness_score": robustness.get("robustness_score"),
            "phase33_handoff": phase33_handoff,
            "stress_summary_rows": stress_rows,
        },
        "baseline_snapshot": _paper_ledger_baseline_snapshot(validation),
        "tracking_rules": {
            "tracking_start_date": tracking_start_date.isoformat(),
            "tracking_benchmark": str(tracking_benchmark or "").strip(),
            "review_cadence": review_cadence,
            "performance_reference": "baseline_snapshot",
            "live_approval": False,
        },
        "review_triggers": review_triggers,
        "operator_note": str(operator_note or "").strip(),
        "phase34_handoff": _build_paper_portfolio_ledger_phase34_handoff(
            {
                "ledger_id": str(ledger_id or "").strip(),
                "paper_status": paper_status,
                "target_components": target_components,
                "tracking_start_date": tracking_start_date.isoformat(),
                "tracking_benchmark": str(tracking_benchmark or "").strip(),
                "review_cadence": review_cadence,
                "review_triggers": review_triggers,
                "baseline_snapshot": _paper_ledger_baseline_snapshot(validation),
            }
        ),
        "notes": "Created from Backtest > Portfolio Proposal. This is paper tracking, not live approval or an order instruction.",
    }


def _build_paper_portfolio_ledger_phase34_handoff(row: dict[str, Any]) -> dict[str, Any]:
    """Summarize whether a saved paper ledger row can feed Phase 34 final selection review."""
    baseline = dict(row.get("baseline_snapshot") or {})
    target_components = list(row.get("target_components") or [])
    active_components = [
        dict(component or {})
        for component in target_components
        if (_portfolio_proposal_optional_float(dict(component or {}).get("target_weight")) or 0.0) > 0.0
    ]
    status = str(row.get("paper_status") or "")
    has_tracking_rules = bool(row.get("tracking_start_date") and row.get("tracking_benchmark") and row.get("review_cadence"))
    has_triggers = bool(list(row.get("review_triggers") or []))
    weight_total = float(baseline.get("target_weight_total") or 0.0)
    has_component_weights = bool(active_components) and abs(weight_total - 100.0) <= 0.01
    blocker_count = 0
    if not row.get("ledger_id"):
        blocker_count += 1
    if not has_component_weights:
        blocker_count += 1
    if not has_tracking_rules:
        blocker_count += 1
    if status in {"paused", "re_review", "closed"}:
        blocker_count += 1
    if blocker_count:
        route = "BLOCKED_FOR_FINAL_SELECTION_REVIEW"
        verdict = "Phase 34 handoff 차단: paper ledger 상태나 입력을 먼저 확인"
        next_action = "ledger id, 비중, tracking rule, 상태를 보강한 뒤 최종 선정 검토로 넘깁니다."
    elif not has_triggers or status == "watch":
        route = "NEEDS_PAPER_TRACKING_REVIEW"
        verdict = "추가 관찰 필요: trigger 또는 watch 상태 확인"
        next_action = "review trigger와 관찰 기간을 보강한 뒤 Phase 34 decision pack에서 판단합니다."
    else:
        route = "READY_FOR_FINAL_SELECTION_REVIEW"
        verdict = "Phase 34 입력 가능: paper tracking 조건과 기준이 기록됨"
        next_action = "Phase 34에서 백테스트, stress, paper ledger, operator note를 함께 읽어 선정 / 보류 / 거절을 판단합니다."
    score = 10.0 - blocker_count * 2.0
    if not has_triggers:
        score -= 1.0
    if status == "watch":
        score -= 1.0
    return {
        "handoff_route": route,
        "handoff_score": round(max(0.0, min(score, 10.0)), 1),
        "verdict": verdict,
        "next_action": next_action,
        "metrics": {
            "active_components": len(active_components),
            "target_weight_total": weight_total,
            "has_tracking_rules": has_tracking_rules,
            "review_triggers": len(list(row.get("review_triggers") or [])),
            "blockers": blocker_count,
        },
    }


def _build_paper_portfolio_ledger_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten ledger records into a compact table for the saved ledger review surface."""
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        baseline = dict(row.get("baseline_snapshot") or {})
        handoff = dict(row.get("phase34_handoff") or _build_paper_portfolio_ledger_phase34_handoff(row))
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Ledger ID": row.get("ledger_id"),
                "Paper Status": row.get("paper_status"),
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Start Date": row.get("tracking_start_date"),
                "Benchmark": row.get("tracking_benchmark"),
                "Review Cadence": row.get("review_cadence"),
                "Components": baseline.get("active_component_count"),
                "Weight Total": baseline.get("target_weight_total"),
                "Phase34 Handoff": handoff.get("handoff_route"),
                "Handoff Score": handoff.get("handoff_score"),
            }
        )
    return pd.DataFrame(display_rows)


def _build_paper_portfolio_ledger_component_rows(row: dict[str, Any]) -> pd.DataFrame:
    """Flatten the selected ledger's target components for operator review."""
    display_rows: list[dict[str, Any]] = []
    for component in list(row.get("target_components") or []):
        component = dict(component or {})
        display_rows.append(
            {
                "Registry ID": component.get("registry_id"),
                "Title": component.get("title"),
                "Role": component.get("proposal_role"),
                "Weight": component.get("target_weight"),
                "Family": component.get("strategy_family"),
                "Benchmark": component.get("benchmark"),
                "Pre-Live": component.get("pre_live_status"),
                "Data Trust": component.get("data_trust_status"),
                "CAGR": component.get("baseline_cagr"),
                "MDD": component.get("baseline_mdd"),
            }
        )
    return pd.DataFrame(display_rows)


def _final_selection_decision_active_components(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Return active paper-ledger components that would enter a final portfolio decision."""
    components: list[dict[str, Any]] = []
    for component in list(row.get("target_components") or []):
        component = dict(component or {})
        if (_portfolio_proposal_optional_float(component.get("target_weight")) or 0.0) > 0.0:
            components.append(component)
    return components


def _build_final_selection_decision_evidence_pack(row: dict[str, Any]) -> dict[str, Any]:
    """Evaluate whether a saved paper ledger is ready for final practical selection."""
    handoff = dict(row.get("phase34_handoff") or _build_paper_portfolio_ledger_phase34_handoff(row))
    baseline = dict(row.get("baseline_snapshot") or {})
    phase32_snapshot = dict(row.get("phase32_handoff_snapshot") or {})
    active_components = _final_selection_decision_active_components(row)
    review_triggers = [str(value) for value in list(row.get("review_triggers") or []) if str(value).strip()]
    paper_status = str(row.get("paper_status") or "")
    handoff_route = str(handoff.get("handoff_route") or "")
    validation_route = str(phase32_snapshot.get("validation_route") or "")
    robustness_route = str(phase32_snapshot.get("robustness_route") or "")
    weight_total = _portfolio_proposal_optional_float(baseline.get("target_weight_total"))
    if weight_total is None:
        weight_total = sum(
            _portfolio_proposal_optional_float(component.get("target_weight")) or 0.0 for component in active_components
        )
    has_weight_total = bool(active_components) and abs(float(weight_total or 0.0) - 100.0) <= 0.01
    has_tracking_rules = bool(row.get("tracking_start_date") and row.get("tracking_benchmark") and row.get("review_cadence"))
    has_live_block = bool(row.get("live_approval") or row.get("order_instruction"))
    robustness_blocked = validation_route == "BLOCKED_FOR_LIVE_READINESS" or robustness_route == "BLOCKED_FOR_ROBUSTNESS"
    paper_status_ready = paper_status == "active_tracking"

    checks = [
        {
            "criteria": "Paper Ledger Source",
            "ready": bool(row.get("ledger_id")),
            "current_value": row.get("ledger_id") or "-",
            "judgment": "저장된 paper ledger source" if row.get("ledger_id") else "paper ledger id 없음",
            "score": 1.2,
        },
        {
            "criteria": "Phase 34 Handoff",
            "ready": handoff_route == "READY_FOR_FINAL_SELECTION_REVIEW",
            "current_value": handoff_route or "-",
            "judgment": "final selection review 입력 가능"
            if handoff_route == "READY_FOR_FINAL_SELECTION_REVIEW"
            else "paper ledger handoff 보강 필요",
            "score": 2.0,
        },
        {
            "criteria": "Paper Status",
            "ready": paper_status_ready,
            "current_value": paper_status or "-",
            "judgment": "active tracking 상태" if paper_status_ready else "watch / paused / re-review / closed 상태 확인 필요",
            "score": 1.2,
        },
        {
            "criteria": "Target Components",
            "ready": has_weight_total,
            "current_value": f"active={len(active_components)}, weight={round(float(weight_total or 0.0), 4)}%",
            "judgment": "최종 판단용 component와 비중 합계 100%" if has_weight_total else "component 또는 target weight 합계 확인 필요",
            "score": 1.6,
        },
        {
            "criteria": "Tracking Rules",
            "ready": has_tracking_rules,
            "current_value": f"start={row.get('tracking_start_date')}, benchmark={row.get('tracking_benchmark')}, cadence={row.get('review_cadence')}",
            "judgment": "paper tracking 기준 있음" if has_tracking_rules else "tracking start / benchmark / cadence 보강 필요",
            "score": 1.2,
        },
        {
            "criteria": "Review Triggers",
            "ready": bool(review_triggers),
            "current_value": f"triggers={len(review_triggers)}",
            "judgment": "재검토 trigger 있음" if review_triggers else "최종 선정 전 stop / re-review trigger 필요",
            "score": 1.0,
        },
        {
            "criteria": "Robustness Snapshot",
            "ready": not robustness_blocked,
            "current_value": f"validation={validation_route or '-'}, robustness={robustness_route or '-'}",
            "judgment": "이전 validation / robustness blocker 없음" if not robustness_blocked else "Phase 31/32 blocker 선해결 필요",
            "score": 1.4,
        },
        {
            "criteria": "Execution Boundary",
            "ready": not has_live_block,
            "current_value": "live/order disabled" if not has_live_block else "live/order flag detected",
            "judgment": "선정 판단만 저장함" if not has_live_block else "live approval 또는 order flag 제거 필요",
            "score": 0.4,
        },
    ]
    blocker_criteria = {
        "Paper Ledger Source",
        "Phase 34 Handoff",
        "Target Components",
        "Tracking Rules",
        "Robustness Snapshot",
        "Execution Boundary",
    }
    blockers = [str(check["criteria"]) for check in checks if not check["ready"] and check["criteria"] in blocker_criteria]
    review_items = [str(check["criteria"]) for check in checks if not check["ready"] and check["criteria"] not in blocker_criteria]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    score = min(score, 10.0)

    if blockers:
        route = "FINAL_DECISION_BLOCKED"
        verdict = "최종 선정 판단 차단: source, 비중, tracking, robustness 경계를 먼저 확인"
        next_action = "blocker를 해결하거나 `RE_REVIEW_REQUIRED` / `REJECT_FOR_PRACTICAL_USE`로 기록합니다."
        suggested_decision_route = "RE_REVIEW_REQUIRED"
    elif review_items:
        route = "FINAL_DECISION_NEEDS_REVIEW"
        verdict = "최종 선정 전 추가 확인 필요: paper 상태나 trigger 검토가 남아 있음"
        next_action = "`HOLD_FOR_MORE_PAPER_TRACKING`으로 보류하거나 trigger를 보강한 뒤 다시 봅니다."
        suggested_decision_route = "HOLD_FOR_MORE_PAPER_TRACKING"
    else:
        route = "READY_FOR_FINAL_DECISION"
        verdict = "최종 실전 후보 선정 판단 가능: paper ledger와 validation 근거가 연결됨"
        next_action = "선정 사유와 제약 조건을 남기고 Final Selection Decision을 저장합니다."
        suggested_decision_route = "SELECT_FOR_PRACTICAL_PORTFOLIO"

    return {
        "route": route,
        "score": score,
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "blockers": blockers,
        "review_items": review_items,
        "suggested_decision_route": suggested_decision_route,
        "metrics": {
            "active_components": len(active_components),
            "target_weight_total": round(float(weight_total or 0.0), 4),
            "review_triggers": len(review_triggers),
            "paper_status": paper_status,
            "phase34_handoff_route": handoff_route,
            "phase34_handoff_score": handoff.get("handoff_score"),
            "validation_route": validation_route,
            "robustness_route": robustness_route,
            "tracking_start_date": row.get("tracking_start_date"),
            "tracking_benchmark": row.get("tracking_benchmark"),
            "review_cadence": row.get("review_cadence"),
        },
    }


def _build_final_selection_decision_save_evaluation(
    *,
    paper_ledger_row: dict[str, Any],
    decision_id: str,
    decision_route: str,
    operator_reason: str,
    existing_decision_ids: set[str] | None = None,
) -> dict[str, Any]:
    """Evaluate whether one final selection decision can be appended safely."""
    existing_decision_ids = existing_decision_ids or set()
    evidence = _build_final_selection_decision_evidence_pack(paper_ledger_row)
    decision_id_clean = str(decision_id or "").strip()
    decision_route_clean = str(decision_route or "").strip()
    identity_ready = bool(decision_id_clean) and decision_id_clean not in existing_decision_ids
    source_ready = bool(str(paper_ledger_row.get("ledger_id") or "").strip())
    route_ready = decision_route_clean in FINAL_SELECTION_DECISION_ROUTE_OPTIONS
    reason_ready = bool(str(operator_reason or "").strip())
    select_readiness_ready = decision_route_clean != "SELECT_FOR_PRACTICAL_PORTFOLIO" or evidence.get("route") == "READY_FOR_FINAL_DECISION"
    checks = [
        {
            "criteria": "Decision Identity",
            "ready": identity_ready,
            "current_value": decision_id_clean or "-",
            "judgment": "decision id 사용 가능" if identity_ready else "decision id 중복 또는 누락",
            "score": 1.2,
        },
        {
            "criteria": "Source Paper Ledger",
            "ready": source_ready,
            "current_value": paper_ledger_row.get("ledger_id") or "-",
            "judgment": "paper ledger source 연결됨" if source_ready else "paper ledger source 없음",
            "score": 1.4,
        },
        {
            "criteria": "Decision Route",
            "ready": route_ready,
            "current_value": decision_route_clean or "-",
            "judgment": "허용된 최종 판단 route" if route_ready else "허용되지 않은 route",
            "score": 1.0,
        },
        {
            "criteria": "Operator Reason",
            "ready": reason_ready,
            "current_value": "attached" if reason_ready else "-",
            "judgment": "사용자 판단 사유 있음" if reason_ready else "선정 / 보류 / 거절 / 재검토 사유 필요",
            "score": 1.2,
        },
        {
            "criteria": "Select Readiness",
            "ready": select_readiness_ready,
            "current_value": str(evidence.get("route") or "-"),
            "judgment": "선정 route에 필요한 근거 충족"
            if select_readiness_ready
            else "SELECT 저장 전 evidence blocker / review item 해결 필요",
            "score": 1.4,
        },
        {
            "criteria": "Live Approval Boundary",
            "ready": True,
            "current_value": "disabled",
            "judgment": "final decision은 승인이나 주문이 아님",
            "score": 0.4,
        },
    ]
    blockers = [str(check["criteria"]) for check in checks if not check["ready"]]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    if not blockers:
        route = "FINAL_DECISION_SAVE_READY"
        verdict = "Final Selection Decision 저장 가능"
        next_action = "Save Final Selection Decision을 눌러 append-only decision registry에 기록합니다."
    elif source_ready and route_ready and reason_ready and decision_route_clean != "SELECT_FOR_PRACTICAL_PORTFOLIO":
        route = "FINAL_DECISION_DRAFT_NEEDS_INPUT"
        verdict = "최종 선정은 아니지만 보류/거절/재검토 기록은 보강 후 저장 가능"
        next_action = "decision id 중복과 필수 사유를 확인한 뒤 저장합니다."
    else:
        route = "FINAL_DECISION_BLOCKED"
        verdict = "Final Selection Decision 저장 차단"
        next_action = "decision id, source ledger, route, operator reason, SELECT readiness를 확인합니다."
    return {
        "route": route,
        "score": min(score, 10.0),
        "verdict": verdict,
        "next_action": next_action,
        "checks": checks,
        "blockers": blockers,
        "can_save": not blockers,
        "evidence_pack": evidence,
    }


def _build_final_selection_decision_phase35_handoff(row: dict[str, Any]) -> dict[str, Any]:
    """Summarize how a saved final decision should be read by Phase 35."""
    decision_route = str(row.get("decision_route") or "")
    evidence = dict(row.get("decision_evidence_snapshot") or {})
    if decision_route == "SELECT_FOR_PRACTICAL_PORTFOLIO":
        handoff_route = "READY_FOR_POST_SELECTION_OPERATING_GUIDE"
        verdict = "Phase 35 운영 가이드 작성 가능: 최종 후보 선정 기록이 있음"
        next_action = "투입 금액, 리밸런싱, 모니터링, stop/re-review 기준을 운영 가이드로 정리합니다."
    elif decision_route == "HOLD_FOR_MORE_PAPER_TRACKING":
        handoff_route = "WAIT_FOR_MORE_PAPER_TRACKING"
        verdict = "Phase 35 보류: paper tracking 근거를 더 쌓아야 함"
        next_action = "추가 관찰 기간 또는 trigger 충족 후 final decision을 다시 남깁니다."
    elif decision_route == "REJECT_FOR_PRACTICAL_USE":
        handoff_route = "NO_PHASE35_HANDOFF"
        verdict = "Phase 35 대상 아님: 실전 후보에서 제외됨"
        next_action = "필요하면 후보군/전략 탐색 단계로 되돌아갑니다."
    else:
        handoff_route = "RE_REVIEW_BEFORE_OPERATING_GUIDE"
        verdict = "Phase 35 전 재검토 필요: 구성 / 비중 / 근거를 다시 확인"
        next_action = "paper ledger 또는 proposal 구성 근거를 보강한 뒤 final decision을 다시 저장합니다."
    return {
        "handoff_route": handoff_route,
        "verdict": verdict,
        "next_action": next_action,
        "requirements": [
            {
                "Requirement": "Final decision route",
                "Status": "READY" if decision_route == "SELECT_FOR_PRACTICAL_PORTFOLIO" else "NOT_READY",
                "Current": decision_route or "-",
                "Why It Matters": "Phase 35는 선정된 후보만 운영 가이드로 바꾼다.",
            },
            {
                "Requirement": "Evidence pack",
                "Status": "READY" if evidence.get("route") == "READY_FOR_FINAL_DECISION" else "REVIEW",
                "Current": evidence.get("route") or "-",
                "Why It Matters": "실전 후보 선정 근거가 paper ledger와 validation snapshot에 연결되어야 한다.",
            },
            {
                "Requirement": "Execution boundary",
                "Status": "READY",
                "Current": "live approval disabled / order instruction disabled",
                "Why It Matters": "선정 기록은 주문 실행이 아니라 다음 운영 가이드 입력이다.",
            },
        ],
    }


def _build_final_selection_decision_row(
    *,
    paper_ledger_row: dict[str, Any],
    decision_id: str,
    decision_route: str,
    operator_reason: str,
    operator_constraints: str,
    operator_next_action: str,
) -> dict[str, Any]:
    """Convert a paper ledger row and user judgment into one final decision record."""
    now = datetime.now().isoformat(timespec="seconds")
    evidence_pack = _build_final_selection_decision_evidence_pack(paper_ledger_row)
    active_components = _final_selection_decision_active_components(paper_ledger_row)
    row = {
        "schema_version": FINAL_SELECTION_DECISION_SCHEMA_VERSION,
        "decision_id": str(decision_id or "").strip(),
        "created_at": now,
        "updated_at": now,
        "decision_status": "recorded",
        "decision_route": str(decision_route or "").strip(),
        "selected_practical_portfolio": decision_route == "SELECT_FOR_PRACTICAL_PORTFOLIO",
        "source_paper_ledger_id": paper_ledger_row.get("ledger_id"),
        "source_type": paper_ledger_row.get("source_type"),
        "source_id": paper_ledger_row.get("source_id"),
        "source_title": paper_ledger_row.get("source_title") or paper_ledger_row.get("source_id"),
        "selected_components": active_components,
        "decision_evidence_snapshot": evidence_pack,
        "risk_and_validation_snapshot": paper_ledger_row.get("phase32_handoff_snapshot") or {},
        "paper_tracking_snapshot": {
            "paper_status": paper_ledger_row.get("paper_status"),
            "tracking_start_date": paper_ledger_row.get("tracking_start_date"),
            "tracking_benchmark": paper_ledger_row.get("tracking_benchmark"),
            "review_cadence": paper_ledger_row.get("review_cadence"),
            "baseline_snapshot": paper_ledger_row.get("baseline_snapshot") or {},
            "review_triggers": list(paper_ledger_row.get("review_triggers") or []),
            "operator_note": paper_ledger_row.get("operator_note"),
        },
        "operator_decision": {
            "reason": str(operator_reason or "").strip(),
            "constraints": str(operator_constraints or "").strip(),
            "next_action": str(operator_next_action or "").strip(),
        },
        "live_approval": False,
        "order_instruction": False,
        "notes": "Created from Backtest > Portfolio Proposal. This is a final selection decision record, not live approval or an order instruction.",
    }
    row["phase35_handoff"] = _build_final_selection_decision_phase35_handoff(row)
    return row


def _build_final_selection_decision_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    """Flatten final decision records into a compact review table."""
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        handoff = dict(row.get("phase35_handoff") or {})
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "Source Ledger": row.get("source_paper_ledger_id"),
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route"),
                "Evidence Score": evidence.get("score"),
                "Phase35 Handoff": handoff.get("handoff_route"),
                "Live Approval": "Disabled",
            }
        )
    return pd.DataFrame(display_rows)


def _build_final_selection_decision_component_rows(row: dict[str, Any]) -> pd.DataFrame:
    """Flatten final decision selected components for operator review."""
    display_rows: list[dict[str, Any]] = []
    for component in list(row.get("selected_components") or []):
        component = dict(component or {})
        display_rows.append(
            {
                "Registry ID": component.get("registry_id"),
                "Title": component.get("title"),
                "Role": component.get("proposal_role"),
                "Weight": component.get("target_weight"),
                "Family": component.get("strategy_family"),
                "Benchmark": component.get("benchmark"),
                "Data Trust": component.get("data_trust_status"),
                "Promotion": component.get("promotion"),
                "Deployment": component.get("deployment"),
                "Baseline CAGR": component.get("baseline_cagr"),
                "Baseline MDD": component.get("baseline_mdd"),
            }
        )
    return pd.DataFrame(display_rows)


# Build the Phase 32 first-pass robustness readiness pack from Phase 31 validation input.
def _build_portfolio_robustness_validation_result(
    validation_input: dict[str, Any],
    *,
    phase31_route: str,
) -> dict[str, Any]:
    source_type = str(validation_input.get("source_type") or "")
    source_id = str(validation_input.get("source_id") or "").strip()
    components = [dict(row or {}) for row in list(validation_input.get("component_rows") or [])]
    active_components = [
        row
        for row in components
        if (_portfolio_proposal_optional_float(row.get("target_weight")) or 0.0) > 0.0
    ]

    blockers: list[str] = []
    input_gaps: list[str] = []
    suggested_sweeps: list[str] = []
    component_rows: list[dict[str, Any]] = []

    if phase31_route == "BLOCKED_FOR_LIVE_READINESS":
        blockers.append("Phase 31 validation is blocked. Resolve portfolio risk hard blockers first.")
    if not source_id:
        blockers.append("Robustness source id is missing.")
    if not active_components:
        blockers.append("No active component is available for robustness validation.")

    for row in active_components:
        registry_id = str(row.get("registry_id") or "-")
        period = dict(row.get("period") or {})
        contract = dict(row.get("contract") or {})
        years = _portfolio_robustness_period_years(period)
        cagr = _portfolio_proposal_optional_float(row.get("cagr"))
        mdd = _portfolio_proposal_optional_float(row.get("mdd"))
        has_metrics = cagr is not None and mdd is not None
        has_period = years is not None
        has_long_window = bool(years is not None and years >= PORTFOLIO_ROBUSTNESS_MIN_WINDOW_YEARS)
        has_contract = bool(contract)
        has_compare = _portfolio_robustness_has_compare_evidence(row)
        benchmark = str(row.get("benchmark") or "").strip()
        stress_ready = has_metrics and has_period and has_contract and bool(benchmark)

        if not has_metrics:
            blockers.append(f"{registry_id}: CAGR / MDD snapshot is missing.")
        if not has_period:
            blockers.append(f"{registry_id}: result period start/end is missing.")
        elif not has_long_window:
            input_gaps.append(
                f"{registry_id}: result window `{years}` years is shorter than `{PORTFOLIO_ROBUSTNESS_MIN_WINDOW_YEARS}` years."
            )
        if not has_contract:
            blockers.append(f"{registry_id}: reproducible contract snapshot is missing.")
        if not benchmark:
            input_gaps.append(f"{registry_id}: benchmark label is missing.")
        if not has_compare:
            input_gaps.append(f"{registry_id}: compare evidence snapshot is missing.")

        component_rows.append(
            {
                "Registry ID": registry_id,
                "Title": row.get("title") or "-",
                "Years": years,
                "Start": period.get("start") or "-",
                "End": period.get("end") or "-",
                "CAGR": cagr,
                "MDD": mdd,
                "Benchmark": benchmark or "-",
                "Contract": _portfolio_robustness_contract_summary(contract),
                "Compare Evidence": "attached" if has_compare else "missing",
                "Stress Ready": stress_ready,
            }
        )

    families = sorted({str(row.get("strategy_family") or "-") for row in active_components})
    benchmarks = sorted({str(row.get("benchmark") or "-") for row in active_components})
    if source_type == "portfolio_proposal" and len(active_components) > 1:
        suggested_sweeps.append("component weight sensitivity: +/-10% around target weights")
        suggested_sweeps.append("component leave-one-out stress: remove one active component at a time")
    suggested_sweeps.append("period split stress: early / middle / recent windows")
    suggested_sweeps.append("recent-window stress: last 3Y and last 5Y where data is available")
    if len(benchmarks) == 1 and benchmarks[0] not in {"-", ""}:
        suggested_sweeps.append(f"benchmark sensitivity: compare against `{benchmarks[0]}` and SPY/reference benchmark")
    else:
        suggested_sweeps.append("benchmark sensitivity: define primary benchmark before stress comparison")
    if families:
        suggested_sweeps.append(f"family-specific parameter sensitivity: {', '.join(families[:4])}")

    has_all_periods = bool(active_components) and all(
        _portfolio_robustness_period_years(dict(row.get("period") or {})) is not None for row in active_components
    )
    has_all_metrics = bool(active_components) and all(
        _portfolio_proposal_optional_float(row.get("cagr")) is not None
        and _portfolio_proposal_optional_float(row.get("mdd")) is not None
        for row in active_components
    )
    has_all_contracts = bool(active_components) and all(bool(dict(row.get("contract") or {})) for row in active_components)
    has_all_benchmarks = bool(active_components) and all(
        bool(str(row.get("benchmark") or "").strip()) for row in active_components
    )
    has_all_compare_evidence = bool(active_components) and all(
        _portfolio_robustness_has_compare_evidence(row) for row in active_components
    )
    attached_compare_count = sum(1 for row in active_components if _portfolio_robustness_has_compare_evidence(row))
    contract_count = sum(1 for row in active_components if dict(row.get("contract") or {}))

    checks = [
        {
            "criteria": "Phase 31 Input",
            "ready": phase31_route != "BLOCKED_FOR_LIVE_READINESS",
            "current_value": phase31_route or "-",
            "judgment": "Phase 31 hard blocker 없음" if phase31_route != "BLOCKED_FOR_LIVE_READINESS" else "Phase 31 blocker 선해결 필요",
            "score": 2.0,
        },
        {
            "criteria": "Result Period",
            "ready": has_all_periods,
            "current_value": f"components={len(active_components)}",
            "judgment": "기간 snapshot 있음" if has_all_periods else "기간 snapshot 보강 필요",
            "score": 1.8,
        },
        {
            "criteria": "Metric Snapshot",
            "ready": has_all_metrics,
            "current_value": "CAGR/MDD",
            "judgment": "성과 snapshot 있음" if has_all_metrics else "성과 snapshot 보강 필요",
            "score": 1.8,
        },
        {
            "criteria": "Reproducible Contract",
            "ready": has_all_contracts,
            "current_value": f"contracts={contract_count}",
            "judgment": "설정 snapshot 있음" if has_all_contracts else "설정 contract 보강 필요",
            "score": 1.6,
        },
        {
            "criteria": "Benchmark Context",
            "ready": has_all_benchmarks,
            "current_value": ", ".join(benchmarks) or "-",
            "judgment": "benchmark 비교 기준 있음" if has_all_benchmarks else "benchmark 기준 보강 필요",
            "score": 1.2,
        },
        {
            "criteria": "Compare Evidence",
            "ready": has_all_compare_evidence,
            "current_value": f"attached={attached_compare_count}",
            "judgment": "compare evidence 있음" if has_all_compare_evidence else "compare evidence 보강 필요",
            "score": 1.6,
        },
    ]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    score = min(score, 10.0)

    if blockers:
        route = "BLOCKED_FOR_ROBUSTNESS"
        verdict = "Robustness 검증 입력 차단: 필수 snapshot 보강 필요"
        next_action = "Phase 31 blocker와 누락된 기간 / 성과 / 설정 snapshot을 먼저 보강합니다."
    elif input_gaps:
        route = "NEEDS_ROBUSTNESS_INPUT_REVIEW"
        verdict = "Robustness 입력 보강 필요: stress 실행 전 확인 항목 있음"
        next_action = "benchmark, compare evidence, 기간 길이 같은 입력 gap을 확인한 뒤 stress sweep을 실행합니다."
    else:
        route = "READY_FOR_STRESS_SWEEP"
        verdict = "Stress 검증 실행 후보 가능: robustness 입력 first pass 통과"
        next_action = "기간 분할, 최근 구간, benchmark 변경, parameter sensitivity 검증을 실행할 수 있습니다."

    stress_summary_rows = _build_portfolio_stress_summary_rows(
        source_type=source_type,
        active_components=active_components,
        robustness_route=route,
        has_all_periods=has_all_periods,
        has_all_contracts=has_all_contracts,
        has_all_benchmarks=has_all_benchmarks,
        has_all_compare_evidence=has_all_compare_evidence,
    )
    stress_metrics = {
        "rows": len(stress_summary_rows),
        "ready_rows": sum(1 for row in stress_summary_rows if row.get("Input Status") == "READY"),
        "input_gap_rows": sum(1 for row in stress_summary_rows if row.get("Input Status") == "INPUT_GAP"),
        "blocked_rows": sum(1 for row in stress_summary_rows if row.get("Input Status") == "BLOCKED"),
        "not_applicable_rows": sum(1 for row in stress_summary_rows if row.get("Input Status") == "NOT_APPLICABLE"),
        "not_run_rows": sum(1 for row in stress_summary_rows if row.get("Result Status") == "NOT_RUN"),
    }
    phase33_handoff = _build_portfolio_phase33_handoff(
        source_type=source_type,
        source_id=source_id,
        active_components=active_components,
        robustness_route=route,
        robustness_score=score,
        stress_summary_rows=stress_summary_rows,
    )

    return {
        "source_type": source_type,
        "source_id": source_id,
        "stress_result_contract": _portfolio_robustness_stress_result_contract(),
        "robustness_route": route,
        "robustness_score": score,
        "verdict": verdict,
        "next_action": next_action,
        "blockers": blockers,
        "input_gaps": input_gaps,
        "suggested_sweeps": suggested_sweeps,
        "checks": checks,
        "component_rows": component_rows,
        "stress_summary_rows": stress_summary_rows,
        "stress_metrics": stress_metrics,
        "phase33_handoff": phase33_handoff,
        "metrics": {
            "components": len(active_components),
            "families": len(families),
            "benchmarks": len([value for value in benchmarks if value not in {"-", ""}]),
            "suggested_sweeps": len(suggested_sweeps),
            "stress_rows": stress_metrics["rows"],
            "ready_stress_rows": stress_metrics["ready_rows"],
        },
    }


# Convert latest Pre-Live rows into a registry_id -> status lookup for proposal component cards.
def _portfolio_proposal_pre_live_status_by_registry_id(pre_live_rows: list[dict[str, Any]]) -> dict[str, str]:
    statuses: dict[str, str] = {}
    for row in pre_live_rows:
        registry_id = str(row.get("source_candidate_registry_id") or "").strip()
        if registry_id:
            statuses[registry_id] = str(row.get("pre_live_status") or "not_started")
    return statuses


# Build the append-only Portfolio Proposal registry row from selected candidates and operator inputs.
def _build_portfolio_proposal_row(
    *,
    proposal_id: str,
    proposal_status: str,
    proposal_type: str,
    primary_goal: str,
    secondary_goal: str,
    target_holding_style: str,
    capital_scope: str,
    weighting_method: str,
    benchmark_policy: str,
    selected_rows: list[dict[str, Any]],
    component_inputs: dict[str, dict[str, Any]],
    open_blockers: list[str],
    operator_decision: str,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
) -> dict[str, Any]:
    now = datetime.now().isoformat(timespec="seconds")
    candidate_refs: list[dict[str, Any]] = []
    evidence_components: list[dict[str, Any]] = []
    for row in selected_rows:
        registry_id = str(row.get("registry_id") or "")
        component_input = dict(component_inputs.get(registry_id) or {})
        result = dict(row.get("result") or {})
        candidate_ref = {
            "registry_id": registry_id,
            "strategy_family": row.get("strategy_family"),
            "strategy_name": row.get("strategy_name"),
            "candidate_role": row.get("candidate_role"),
            "proposal_role": component_input.get("proposal_role"),
            "target_weight": component_input.get("target_weight"),
            "weight_reason": component_input.get("weight_reason"),
            "data_trust_status": component_input.get("data_trust_status") or "not_attached",
            "real_money_status": {
                "promotion": result.get("promotion"),
                "shortlist": result.get("shortlist"),
                "deployment": result.get("deployment"),
            },
            "pre_live_status": component_input.get("pre_live_status") or "not_started",
            "open_candidate_blockers": component_input.get("open_candidate_blockers") or [],
        }
        candidate_refs.append(candidate_ref)
        evidence_components.append(
            {
                "registry_id": registry_id,
                "title": row.get("title"),
                "cagr": result.get("cagr"),
                "mdd": result.get("mdd"),
                "promotion": result.get("promotion"),
                "shortlist": result.get("shortlist"),
                "deployment": result.get("deployment"),
                "period": row.get("period") or {},
            }
        )

    return {
        "schema_version": PORTFOLIO_PROPOSAL_SCHEMA_VERSION,
        "proposal_id": proposal_id.strip(),
        "created_at": now,
        "updated_at": now,
        "proposal_status": proposal_status,
        "proposal_type": proposal_type,
        "objective": {
            "primary_goal": primary_goal.strip(),
            "secondary_goal": secondary_goal.strip(),
            "target_holding_style": target_holding_style.strip(),
            "capital_scope": capital_scope,
        },
        "candidate_refs": candidate_refs,
        "construction": {
            "weighting_method": weighting_method,
            "benchmark_policy": benchmark_policy.strip(),
            "date_alignment": "compare_or_saved_portfolio_context_required",
        },
        "risk_constraints": {
            "max_component_weight": max(
                [float(ref.get("target_weight") or 0.0) for ref in candidate_refs],
                default=0.0,
            ),
            "requires_component_data_trust_review": True,
            "requires_real_money_review": True,
            "requires_pre_live_review": True,
        },
        "evidence_snapshot": {
            "component_count": len(candidate_refs),
            "components": evidence_components,
        },
        "open_blockers": open_blockers,
        "operator_decision": {
            "decision": operator_decision.strip(),
            "reason": operator_reason.strip(),
            "next_action": next_action.strip(),
            "review_date": review_date_value.isoformat() if review_date_value else None,
        },
        "notes": (
            "Created from Backtest > Portfolio Proposal. This is a proposal draft, "
            "not live trading approval and not an order instruction."
        ),
    }


# Summarize saved proposal rows for the compact saved-proposals table.
def _build_portfolio_proposal_rows_for_display(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        objective = dict(row.get("objective") or {})
        construction = dict(row.get("construction") or {})
        operator_decision = dict(row.get("operator_decision") or {})
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Type": row.get("proposal_type"),
                "Primary Goal": objective.get("primary_goal"),
                "Components": len(row.get("candidate_refs") or []),
                "Weighting": construction.get("weighting_method"),
                "Next Action": operator_decision.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


# Add all component target weights in a saved proposal row.
def _portfolio_proposal_weight_total(row: dict[str, Any]) -> float:
    total = 0.0
    for ref in list(row.get("candidate_refs") or []):
        try:
            total += float(ref.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            continue
    return round(total, 4)


# Find non-blocking review gaps that should be visible before later approval stages.
def _portfolio_proposal_review_gaps(row: dict[str, Any]) -> list[str]:
    gaps: list[str] = []
    operator_decision = dict(row.get("operator_decision") or {})
    if not operator_decision.get("review_date"):
        gaps.append("Review date is not set.")

    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "-")
        data_trust_status = str(ref.get("data_trust_status") or "not_attached")
        pre_live_status = str(ref.get("pre_live_status") or "not_started")
        if data_trust_status in {"not_attached", "unknown", "missing"}:
            gaps.append(f"{registry_id}: data trust status needs review.")
        if pre_live_status == "not_started":
            gaps.append(f"{registry_id}: pre-live status is not started.")
    return gaps


# Find hard proposal blockers that should stop an active proposal weight.
def _portfolio_proposal_monitoring_blockers(row: dict[str, Any]) -> list[str]:
    blockers = [str(value) for value in list(row.get("open_blockers") or []) if str(value).strip()]
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "-")
        real_money_status = dict(ref.get("real_money_status") or {})
        try:
            target_weight = float(ref.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            target_weight = 0.0
        pre_live_status = str(ref.get("pre_live_status") or "not_started")
        proposal_role = str(ref.get("proposal_role") or "")
        deployment_status = str(real_money_status.get("deployment") or "").lower()
        component_blockers = [str(value) for value in list(ref.get("open_candidate_blockers") or []) if str(value).strip()]
        for blocker in component_blockers:
            blockers.append(f"{registry_id}: {blocker}")
        if pre_live_status == "reject" and target_weight > 0:
            blockers.append(f"{registry_id}: rejected pre-live candidate has active weight.")
        if deployment_status == "blocked" and proposal_role == "core_anchor":
            blockers.append(f"{registry_id}: blocked candidate is marked as core anchor.")
    return blockers


# Convert saved proposal blockers and gaps into a compact monitoring state label.
def _portfolio_proposal_monitoring_state(row: dict[str, Any]) -> str:
    if _portfolio_proposal_monitoring_blockers(row):
        return "blocked"
    if _portfolio_proposal_review_gaps(row):
        return "needs_review"
    return "review_ready"


# Build the saved proposal monitoring summary table.
def _build_portfolio_proposal_monitoring_rows(rows: list[dict[str, Any]]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        operator_decision = dict(row.get("operator_decision") or {})
        blockers = _portfolio_proposal_monitoring_blockers(row)
        review_gaps = _portfolio_proposal_review_gaps(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Monitoring State": _portfolio_proposal_monitoring_state(row),
                "Components": len(row.get("candidate_refs") or []),
                "Weight Total": _portfolio_proposal_weight_total(row),
                "Blockers": len(blockers),
                "Review Gaps": len(review_gaps),
                "Review Date": operator_decision.get("review_date"),
                "Next Action": operator_decision.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


# Build the saved proposal component table for inspection.
def _build_portfolio_proposal_component_rows(row: dict[str, Any]) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for ref in list(row.get("candidate_refs") or []):
        real_money_status = dict(ref.get("real_money_status") or {})
        blockers = [str(value) for value in list(ref.get("open_candidate_blockers") or []) if str(value).strip()]
        display_rows.append(
            {
                "Registry ID": ref.get("registry_id"),
                "Family": ref.get("strategy_family"),
                "Strategy": ref.get("strategy_name"),
                "Candidate Role": ref.get("candidate_role"),
                "Proposal Role": ref.get("proposal_role"),
                "Target Weight": ref.get("target_weight"),
                "Data Trust": ref.get("data_trust_status"),
                "Pre-Live": ref.get("pre_live_status"),
                "Promotion": real_money_status.get("promotion"),
                "Shortlist": real_money_status.get("shortlist"),
                "Deployment": real_money_status.get("deployment"),
                "Weight Reason": ref.get("weight_reason"),
                "Candidate Blockers": "; ".join(blockers) if blockers else "-",
            }
        )
    return pd.DataFrame(display_rows)


# Create a stable, human-readable label for selecting a saved proposal row.
def _portfolio_proposal_selection_label(row: dict[str, Any]) -> str:
    return f"{row.get('updated_at') or row.get('created_at')} | {row.get('proposal_status')} | {row.get('proposal_id')}"


# Convert latest Pre-Live rows into a registry_id -> row lookup for feedback comparisons.
def _portfolio_proposal_pre_live_record_by_registry_id(pre_live_rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    records: dict[str, dict[str, Any]] = {}
    for row in pre_live_rows:
        registry_id = str(row.get("source_candidate_registry_id") or "").strip()
        if registry_id:
            records[registry_id] = dict(row)
    return records


# Parse ISO-like review date values from saved JSONL records.
def _portfolio_proposal_parse_review_date(value: Any) -> date | None:
    if not value:
        return None
    try:
        return date.fromisoformat(str(value)[:10])
    except ValueError:
        return None


# Parse optional numeric values from JSONL snapshots and table cells.
def _portfolio_proposal_optional_float(value: Any) -> float | None:
    if value is None:
        return None
    if isinstance(value, (int, float)):
        if pd.isna(value):
            return None
        return float(value)
    value_text = str(value).strip()
    if not value_text or value_text.lower() in {"none", "nan", "null"} or value_text == "-":
        return None
    value_text = value_text.replace("%", "").replace(",", "")
    try:
        return float(value_text)
    except ValueError:
        return None


# Calculate current-minus-saved metric deltas for paper tracking feedback.
def _portfolio_proposal_metric_delta(current_value: Any, saved_value: Any) -> float | None:
    current_float = _portfolio_proposal_optional_float(current_value)
    saved_float = _portfolio_proposal_optional_float(saved_value)
    if current_float is None or saved_float is None:
        return None
    return round(current_float - saved_float, 4)


# Convert a saved proposal evidence snapshot into a registry_id -> evidence lookup.
def _portfolio_proposal_evidence_by_registry_id(row: dict[str, Any]) -> dict[str, dict[str, Any]]:
    evidence = dict(row.get("evidence_snapshot") or {})
    records: dict[str, dict[str, Any]] = {}
    for component in list(evidence.get("components") or []):
        registry_id = str(dict(component).get("registry_id") or "").strip()
        if registry_id:
            records[registry_id] = dict(component)
    return records


# Classify whether current paper tracking performance is stable, missing, or worsened.
def _portfolio_proposal_paper_tracking_signal(
    *,
    current_status: str,
    saved_cagr: Any,
    current_cagr: Any,
    saved_mdd: Any,
    current_mdd: Any,
) -> str:
    if current_status != "paper_tracking":
        return "needs_paper_tracking"
    if current_cagr is None or current_mdd is None:
        return "missing_current_result"
    if saved_cagr is None or saved_mdd is None:
        return "missing_saved_snapshot"
    cagr_delta = _portfolio_proposal_metric_delta(current_cagr, saved_cagr)
    mdd_delta = _portfolio_proposal_metric_delta(current_mdd, saved_mdd)
    if cagr_delta is None or mdd_delta is None:
        return "missing_current_result"
    if (
        cagr_delta <= PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD
        or mdd_delta <= PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD
    ):
        return "worsened"
    return "stable_or_better"


# Build row-level comparison between saved proposal Pre-Live snapshot and current Pre-Live state.
def _portfolio_proposal_pre_live_feedback_rows(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        saved_status = str(ref.get("pre_live_status") or "not_started")
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        tracking_plan = dict(pre_live_record.get("tracking_plan") or {})
        review_date = pre_live_record.get("review_date")
        review_date_value = _portfolio_proposal_parse_review_date(review_date)
        display_rows.append(
            {
                "Registry ID": registry_id or "-",
                "Proposal Role": ref.get("proposal_role"),
                "Target Weight": ref.get("target_weight"),
                "Saved Pre-Live": saved_status,
                "Current Pre-Live": current_status,
                "Status Drift": "changed" if saved_status != current_status else "same",
                "Current Review Date": review_date,
                "Review Overdue": bool(review_date_value and review_date_value < date.today()),
                "Tracking Cadence": tracking_plan.get("cadence"),
                "Current Next Action": pre_live_record.get("next_action"),
            }
        )
    return pd.DataFrame(display_rows)


# Find gaps between a saved proposal and the latest Pre-Live registry rows.
def _portfolio_proposal_pre_live_feedback_gaps(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> list[str]:
    gaps: list[str] = []
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        if not registry_id:
            continue
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        saved_status = str(ref.get("pre_live_status") or "not_started")
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        try:
            target_weight = float(ref.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            target_weight = 0.0
        if not pre_live_record:
            gaps.append(f"{registry_id}: no active Pre-Live record is linked.")
        if saved_status != current_status:
            gaps.append(f"{registry_id}: proposal snapshot `{saved_status}` differs from current Pre-Live `{current_status}`.")
        if current_status in {"hold", "reject", "re_review"} and target_weight > 0:
            gaps.append(f"{registry_id}: current Pre-Live status `{current_status}` needs review for active weight.")
        review_date_value = _portfolio_proposal_parse_review_date(pre_live_record.get("review_date"))
        if review_date_value and review_date_value < date.today():
            gaps.append(f"{registry_id}: Pre-Live review date `{review_date_value.isoformat()}` is overdue.")
    return gaps


# Build a saved proposal summary table for current Pre-Live feedback.
def _build_portfolio_proposal_pre_live_feedback_summary_rows(
    rows: list[dict[str, Any]],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        feedback_df = _portfolio_proposal_pre_live_feedback_rows(row, pre_live_by_registry_id)
        gaps = _portfolio_proposal_pre_live_feedback_gaps(row, pre_live_by_registry_id)
        if feedback_df.empty:
            linked_count = 0
            paper_tracking_count = 0
            drift_count = 0
            overdue_count = 0
        else:
            linked_count = int((feedback_df["Current Pre-Live"] != "not_started").sum())
            paper_tracking_count = int((feedback_df["Current Pre-Live"] == "paper_tracking").sum())
            drift_count = int((feedback_df["Status Drift"] == "changed").sum())
            overdue_count = int(feedback_df["Review Overdue"].sum())
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Components": len(row.get("candidate_refs") or []),
                "Linked Pre-Live": linked_count,
                "Paper Tracking": paper_tracking_count,
                "Status Drift": drift_count,
                "Overdue Reviews": overdue_count,
                "Feedback Gaps": len(gaps),
            }
        )
    return pd.DataFrame(display_rows)


# Build component-level paper tracking metric feedback rows.
def _portfolio_proposal_paper_tracking_feedback_rows(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    evidence_by_registry_id = _portfolio_proposal_evidence_by_registry_id(row)
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        evidence = evidence_by_registry_id.get(registry_id) or {}
        result_snapshot = dict(pre_live_record.get("result_snapshot") or {})
        tracking_plan = dict(pre_live_record.get("tracking_plan") or {})
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        saved_cagr = _portfolio_proposal_optional_float(evidence.get("cagr"))
        saved_mdd = _portfolio_proposal_optional_float(evidence.get("mdd"))
        current_cagr = _portfolio_proposal_optional_float(result_snapshot.get("cagr"))
        current_mdd = _portfolio_proposal_optional_float(result_snapshot.get("mdd"))
        display_rows.append(
            {
                "Registry ID": registry_id or "-",
                "Proposal Role": ref.get("proposal_role"),
                "Target Weight": ref.get("target_weight"),
                "Current Pre-Live": current_status,
                "Saved CAGR": saved_cagr,
                "Current CAGR": current_cagr,
                "CAGR Delta": _portfolio_proposal_metric_delta(current_cagr, saved_cagr),
                "Saved MDD": saved_mdd,
                "Current MDD": current_mdd,
                "MDD Delta": _portfolio_proposal_metric_delta(current_mdd, saved_mdd),
                "Performance Signal": _portfolio_proposal_paper_tracking_signal(
                    current_status=current_status,
                    saved_cagr=saved_cagr,
                    current_cagr=current_cagr,
                    saved_mdd=saved_mdd,
                    current_mdd=current_mdd,
                ),
                "Tracking Cadence": tracking_plan.get("cadence"),
                "Stop Condition": tracking_plan.get("stop_condition"),
                "Success Condition": tracking_plan.get("success_condition"),
            }
        )
    return pd.DataFrame(display_rows)


# Find paper tracking feedback gaps between a proposal snapshot and the latest Pre-Live snapshots.
def _portfolio_proposal_paper_tracking_feedback_gaps(
    row: dict[str, Any],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> list[str]:
    gaps: list[str] = []
    evidence_by_registry_id = _portfolio_proposal_evidence_by_registry_id(row)
    for ref in list(row.get("candidate_refs") or []):
        registry_id = str(ref.get("registry_id") or "")
        if not registry_id:
            continue
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        evidence = evidence_by_registry_id.get(registry_id) or {}
        result_snapshot = dict(pre_live_record.get("result_snapshot") or {})
        tracking_plan = dict(pre_live_record.get("tracking_plan") or {})
        current_status = str(pre_live_record.get("pre_live_status") or "not_started")
        saved_cagr = _portfolio_proposal_optional_float(evidence.get("cagr"))
        saved_mdd = _portfolio_proposal_optional_float(evidence.get("mdd"))
        current_cagr = _portfolio_proposal_optional_float(result_snapshot.get("cagr"))
        current_mdd = _portfolio_proposal_optional_float(result_snapshot.get("mdd"))
        cagr_delta = _portfolio_proposal_metric_delta(current_cagr, saved_cagr)
        mdd_delta = _portfolio_proposal_metric_delta(current_mdd, saved_mdd)
        if not pre_live_record:
            gaps.append(f"{registry_id}: no active Pre-Live record is linked for paper tracking feedback.")
            continue
        if current_status != "paper_tracking":
            gaps.append(f"{registry_id}: current Pre-Live status is `{current_status}`, not `paper_tracking`.")
        if saved_cagr is None or saved_mdd is None:
            gaps.append(f"{registry_id}: proposal evidence snapshot is missing CAGR or MDD.")
        if current_cagr is None or current_mdd is None:
            gaps.append(f"{registry_id}: current Pre-Live result snapshot is missing CAGR or MDD.")
        if cagr_delta is not None and cagr_delta <= PORTFOLIO_PROPOSAL_PAPER_CAGR_DETERIORATION_THRESHOLD:
            gaps.append(f"{registry_id}: CAGR delta `{cagr_delta}` is below the paper tracking threshold.")
        if mdd_delta is not None and mdd_delta <= PORTFOLIO_PROPOSAL_PAPER_MDD_DETERIORATION_THRESHOLD:
            gaps.append(f"{registry_id}: MDD delta `{mdd_delta}` is below the paper tracking threshold.")
        if current_status == "paper_tracking" and not tracking_plan.get("cadence"):
            gaps.append(f"{registry_id}: paper tracking cadence is not set.")
    return gaps


# Build a saved proposal summary table for paper tracking performance feedback.
def _build_portfolio_proposal_paper_tracking_feedback_summary_rows(
    rows: list[dict[str, Any]],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        feedback_df = _portfolio_proposal_paper_tracking_feedback_rows(row, pre_live_by_registry_id)
        gaps = _portfolio_proposal_paper_tracking_feedback_gaps(row, pre_live_by_registry_id)
        if feedback_df.empty:
            paper_tracking_count = 0
            missing_current_result_count = 0
            worsened_count = 0
            stable_or_better_count = 0
        else:
            paper_tracking_count = int((feedback_df["Current Pre-Live"] == "paper_tracking").sum())
            missing_current_result_count = int((feedback_df["Performance Signal"] == "missing_current_result").sum())
            worsened_count = int((feedback_df["Performance Signal"] == "worsened").sum())
            stable_or_better_count = int((feedback_df["Performance Signal"] == "stable_or_better").sum())
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Status": row.get("proposal_status"),
                "Components": len(row.get("candidate_refs") or []),
                "Paper Tracking": paper_tracking_count,
                "Missing Current Result": missing_current_result_count,
                "Worsened": worsened_count,
                "Stable / Better": stable_or_better_count,
                "Feedback Gaps": len(gaps),
            }
        )
    return pd.DataFrame(display_rows)


# Convert current candidate rows into a registry_id -> row lookup for validation pack inputs.
def _portfolio_proposal_current_candidate_by_registry_id(rows: list[dict[str, Any]]) -> dict[str, dict[str, Any]]:
    candidates: dict[str, dict[str, Any]] = {}
    for row in rows:
        registry_id = str(row.get("registry_id") or "").strip()
        if registry_id:
            candidates[registry_id] = dict(row)
    return candidates


# Extract a benchmark-like label from saved candidate contracts and result snapshots.
def _portfolio_risk_component_benchmark(row: dict[str, Any] | None, ref: dict[str, Any] | None = None) -> str:
    candidate = dict(row or {})
    ref = dict(ref or {})
    contract = dict(candidate.get("contract") or {})
    result = dict(candidate.get("result") or {})
    real_money = dict(ref.get("real_money_status") or {})
    for value in (
        contract.get("benchmark_ticker"),
        contract.get("benchmark"),
        result.get("benchmark_ticker"),
        real_money.get("benchmark_ticker"),
    ):
        if value not in (None, ""):
            return str(value)
    return "-"


# Extract a compact universe label that can be compared across proposal components.
def _portfolio_risk_component_universe(row: dict[str, Any] | None) -> str:
    candidate = dict(row or {})
    contract = dict(candidate.get("contract") or {})
    tickers = list(contract.get("tickers") or [])
    if tickers:
        return ",".join(str(ticker) for ticker in tickers)
    for key in ("universe_contract", "universe_mode", "preset_name"):
        value = contract.get(key)
        if value not in (None, ""):
            return str(value)
    return "-"


# Extract a factor set label for strict equity candidates when saved contracts include factor names.
def _portfolio_risk_component_factors(row: dict[str, Any] | None) -> str:
    candidate = dict(row or {})
    contract = dict(candidate.get("contract") or {})
    factors: list[str] = []
    for key in (
        "factors",
        "factor_set",
        "quality_factors",
        "value_factors",
        "selected_factors",
        "factor_columns",
    ):
        value = contract.get(key)
        if isinstance(value, list):
            factors.extend(str(item) for item in value if str(item).strip())
        elif isinstance(value, str) and value.strip():
            factors.append(value.strip())
    if not factors:
        return "-"
    return ",".join(sorted(dict.fromkeys(factors)))


# Build the Phase 31 validation input for one already-packaged candidate.
def _build_portfolio_risk_validation_input_for_single_candidate(
    *,
    selected_row: dict[str, Any],
    pre_live_record: dict[str, Any] | None,
    pre_live_status: str,
    data_trust_status: str,
) -> dict[str, Any]:
    registry_id = str(selected_row.get("registry_id") or "").strip()
    result = dict(selected_row.get("result") or {})
    review_context = dict(selected_row.get("review_context") or {})
    return {
        "source_type": "single_candidate",
        "source_id": registry_id,
        "source_label": selected_row.get("title") or registry_id,
        "objective": {
            "primary_goal": "single_candidate_live_readiness_validation",
            "capital_scope": "paper_only",
        },
        "component_rows": [
            {
                "registry_id": registry_id,
                "title": selected_row.get("title") or registry_id,
                "strategy_family": selected_row.get("strategy_family"),
                "strategy_name": selected_row.get("strategy_name"),
                "candidate_role": selected_row.get("candidate_role"),
                "proposal_role": "core_anchor",
                "target_weight": 100.0,
                "data_trust_status": data_trust_status,
                "pre_live_status": pre_live_status or "not_started",
                "promotion": result.get("promotion"),
                "shortlist": result.get("shortlist"),
                "deployment": result.get("deployment"),
                "cagr": result.get("cagr"),
                "mdd": result.get("mdd"),
                "period": dict(selected_row.get("period") or {}),
                "contract": dict(selected_row.get("contract") or {}),
                "compare_evidence": dict(review_context.get("compare_readiness_evaluation") or {}),
                "benchmark": _portfolio_risk_component_benchmark(selected_row),
                "universe": _portfolio_risk_component_universe(selected_row),
                "factors": _portfolio_risk_component_factors(selected_row),
                "has_current_candidate": bool(selected_row),
                "has_pre_live_record": bool(pre_live_record),
                "open_candidate_blockers": list(result.get("blockers") or []),
            }
        ],
    }


# Build the Phase 31 validation input for a saved or draft Portfolio Proposal row.
def _build_portfolio_risk_validation_input_for_proposal(
    *,
    proposal_row: dict[str, Any],
    current_by_registry_id: dict[str, dict[str, Any]],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> dict[str, Any]:
    component_rows: list[dict[str, Any]] = []
    evidence_by_registry_id = _portfolio_proposal_evidence_by_registry_id(proposal_row)
    for ref in list(proposal_row.get("candidate_refs") or []):
        ref = dict(ref or {})
        registry_id = str(ref.get("registry_id") or "").strip()
        current_row = current_by_registry_id.get(registry_id) or {}
        pre_live_record = pre_live_by_registry_id.get(registry_id) or {}
        real_money_status = dict(ref.get("real_money_status") or {})
        evidence = evidence_by_registry_id.get(registry_id) or {}
        result = dict(current_row.get("result") or {})
        review_context = dict(current_row.get("review_context") or {})
        pre_live_settings = dict(pre_live_record.get("settings_snapshot") or {})
        data_trust_status = str(ref.get("data_trust_status") or "").strip()
        if not data_trust_status:
            data_trust_status = _portfolio_proposal_candidate_data_trust_status(current_row)
        component_rows.append(
            {
                "registry_id": registry_id,
                "title": current_row.get("title") or evidence.get("title") or registry_id,
                "strategy_family": ref.get("strategy_family") or current_row.get("strategy_family"),
                "strategy_name": ref.get("strategy_name") or current_row.get("strategy_name"),
                "candidate_role": ref.get("candidate_role") or current_row.get("candidate_role"),
                "proposal_role": ref.get("proposal_role"),
                "target_weight": _portfolio_proposal_optional_float(ref.get("target_weight")) or 0.0,
                "data_trust_status": data_trust_status or "not_attached",
                "pre_live_status": str(pre_live_record.get("pre_live_status") or ref.get("pre_live_status") or "not_started"),
                "promotion": real_money_status.get("promotion") or result.get("promotion"),
                "shortlist": real_money_status.get("shortlist") or result.get("shortlist"),
                "deployment": real_money_status.get("deployment") or result.get("deployment"),
                "cagr": result.get("cagr", evidence.get("cagr")),
                "mdd": result.get("mdd", evidence.get("mdd")),
                "period": dict(current_row.get("period") or evidence.get("period") or pre_live_settings.get("period") or {}),
                "contract": dict(current_row.get("contract") or pre_live_settings.get("contract") or {}),
                "compare_evidence": dict(review_context.get("compare_readiness_evaluation") or {}),
                "benchmark": _portfolio_risk_component_benchmark(current_row, ref),
                "universe": _portfolio_risk_component_universe(current_row),
                "factors": _portfolio_risk_component_factors(current_row),
                "has_current_candidate": bool(current_row),
                "has_pre_live_record": bool(pre_live_record),
                "open_candidate_blockers": list(ref.get("open_candidate_blockers") or []),
            }
        )

    objective = dict(proposal_row.get("objective") or {})
    return {
        "source_type": "portfolio_proposal",
        "source_id": str(proposal_row.get("proposal_id") or "").strip(),
        "source_label": str(proposal_row.get("proposal_id") or "").strip(),
        "objective": objective,
        "proposal_status": proposal_row.get("proposal_status"),
        "component_rows": component_rows,
    }


def _portfolio_risk_count_values(rows: list[dict[str, Any]], key: str) -> dict[str, int]:
    counts: dict[str, int] = {}
    for row in rows:
        value = str(row.get(key) or "-").strip() or "-"
        counts[value] = counts.get(value, 0) + 1
    return counts


# Score a single candidate or proposal draft for Phase 31 portfolio risk / live readiness validation.
def _build_portfolio_risk_validation_result(validation_input: dict[str, Any]) -> dict[str, Any]:
    source_type = str(validation_input.get("source_type") or "")
    source_id = str(validation_input.get("source_id") or "").strip()
    components = [dict(row or {}) for row in list(validation_input.get("component_rows") or [])]
    active_components = [
        row
        for row in components
        if (_portfolio_proposal_optional_float(row.get("target_weight")) or 0.0) > 0.0
    ]
    active_count = len(active_components)
    weight_total = round(
        sum((_portfolio_proposal_optional_float(row.get("target_weight")) or 0.0) for row in active_components),
        4,
    )
    max_weight = max(
        [(_portfolio_proposal_optional_float(row.get("target_weight")) or 0.0) for row in active_components],
        default=0.0,
    )
    has_core_anchor = any(str(row.get("proposal_role") or "") == "core_anchor" for row in active_components)

    hard_blockers: list[str] = []
    review_gaps: list[str] = []
    paper_tracking_gaps: list[str] = []

    if not source_id:
        hard_blockers.append("Validation source id is missing.")
    if not components:
        hard_blockers.append("No validation component is attached.")
    if active_count == 0:
        hard_blockers.append("No active component weight is attached.")
    if active_count and abs(weight_total - 100.0) > 0.01:
        hard_blockers.append(f"Active target weights must sum to 100%, current={weight_total}%.")
    if active_count and not has_core_anchor:
        hard_blockers.append("At least one active core_anchor component is required.")

    for row in active_components:
        registry_id = str(row.get("registry_id") or "-")
        pre_live_status = str(row.get("pre_live_status") or "not_started")
        promotion = str(row.get("promotion") or "").lower()
        deployment = str(row.get("deployment") or "").lower()
        data_trust_status = str(row.get("data_trust_status") or "not_attached").lower()
        component_blockers = [str(value) for value in list(row.get("open_candidate_blockers") or []) if str(value).strip()]
        for blocker in component_blockers:
            hard_blockers.append(f"{registry_id}: {blocker}")
        if not row.get("has_current_candidate"):
            review_gaps.append(f"{registry_id}: current candidate registry row is not linked.")
        if not row.get("has_pre_live_record"):
            paper_tracking_gaps.append(f"{registry_id}: active Pre-Live record is not linked.")
        if pre_live_status in {"hold", "reject", "rejected", "pre_live_hold"}:
            hard_blockers.append(f"{registry_id}: active component has `{pre_live_status}` Pre-Live status.")
        elif pre_live_status != "paper_tracking":
            paper_tracking_gaps.append(f"{registry_id}: Pre-Live status is `{pre_live_status}`, not `paper_tracking`.")
        if promotion == "hold":
            hard_blockers.append(f"{registry_id}: Real-Money promotion is hold.")
        if deployment in {"blocked", "reject", "rejected"}:
            hard_blockers.append(f"{registry_id}: deployment status is `{deployment}`.")
        if not promotion and not deployment:
            review_gaps.append(f"{registry_id}: Real-Money signal is missing.")
        if data_trust_status in {"blocked", "error"}:
            hard_blockers.append(f"{registry_id}: Data Trust is `{data_trust_status}`.")
        elif data_trust_status in {"not_attached", "missing", "unknown", ""}:
            review_gaps.append(f"{registry_id}: Data Trust snapshot is not attached.")

    if source_type == "portfolio_proposal" and active_count > 1:
        if max_weight > PORTFOLIO_RISK_MAX_REVIEW_WEIGHT:
            review_gaps.append(f"Max component weight `{max_weight}%` is above review threshold `{PORTFOLIO_RISK_MAX_REVIEW_WEIGHT}%`.")
        for label, key in (
            ("strategy family", "strategy_family"),
            ("benchmark", "benchmark"),
            ("universe", "universe"),
            ("factor set", "factors"),
        ):
            counts = _portfolio_risk_count_values(active_components, key)
            dominant_value, dominant_count = max(counts.items(), key=lambda item: item[1]) if counts else ("-", 0)
            if dominant_value != "-" and dominant_count == active_count:
                review_gaps.append(f"All active components share the same {label}: `{dominant_value}`.")

    hard_blockers = list(dict.fromkeys(hard_blockers))
    paper_tracking_gaps = list(dict.fromkeys(paper_tracking_gaps))
    review_gaps = list(dict.fromkeys(review_gaps))

    identity_ready = bool(source_id and components)
    construction_ready = bool(active_count and abs(weight_total - 100.0) <= 0.01 and has_core_anchor)
    concentration_ready = source_type == "single_candidate" or max_weight <= PORTFOLIO_RISK_MAX_REVIEW_WEIGHT
    pre_live_ready = bool(active_count) and not paper_tracking_gaps
    real_money_ready = not any("Real-Money" in item or "deployment status" in item for item in hard_blockers)
    data_trust_ready = not any("Data Trust" in item for item in hard_blockers + review_gaps)
    overlap_ready = not any("share the same" in item for item in review_gaps)
    blocker_ready = not hard_blockers
    checks = [
        {
            "criteria": "Source Identity",
            "ready": identity_ready,
            "current_value": f"type={source_type}, id={source_id or '-'}",
            "judgment": "검증 입력 식별 가능" if identity_ready else "source id 또는 component 필요",
            "score": 1.0,
        },
        {
            "criteria": "Portfolio Construction",
            "ready": construction_ready,
            "current_value": f"components={active_count}, weight_total={weight_total}%, core_anchor={has_core_anchor}",
            "judgment": "비중과 중심 후보 확인" if construction_ready else "비중 합계 또는 core anchor 확인 필요",
            "score": 1.8,
        },
        {
            "criteria": "Concentration",
            "ready": concentration_ready,
            "current_value": f"max_weight={max_weight}%",
            "judgment": "집중도 first pass 통과" if concentration_ready else "비중 집중 검토 필요",
            "score": 1.2,
        },
        {
            "criteria": "Pre-Live / Paper Tracking",
            "ready": pre_live_ready,
            "current_value": ", ".join(sorted({str(row.get("pre_live_status") or "not_started") for row in active_components})) or "-",
            "judgment": "active 후보가 paper_tracking 상태" if pre_live_ready else "paper tracking 또는 Pre-Live 연결 필요",
            "score": 1.4,
        },
        {
            "criteria": "Real-Money / Deployment",
            "ready": real_money_ready,
            "current_value": ", ".join(sorted({str(row.get("deployment") or "-") for row in active_components})) or "-",
            "judgment": "hold / blocked hard blocker 없음" if real_money_ready else "Real-Money hard blocker 확인 필요",
            "score": 1.4,
        },
        {
            "criteria": "Data Trust",
            "ready": data_trust_ready,
            "current_value": ", ".join(sorted({str(row.get("data_trust_status") or "not_attached") for row in active_components})) or "-",
            "judgment": "Data Trust attached" if data_trust_ready else "Data Trust 보강 필요",
            "score": 1.0,
        },
        {
            "criteria": "Overlap First Pass",
            "ready": overlap_ready,
            "current_value": f"families={len(_portfolio_risk_count_values(active_components, 'strategy_family'))}",
            "judgment": "중복 위험 first pass 통과" if overlap_ready else "family / benchmark / universe / factor 편중 검토 필요",
            "score": 1.0,
        },
        {
            "criteria": "Hard Blockers",
            "ready": blocker_ready,
            "current_value": f"hard_blockers={len(hard_blockers)}",
            "judgment": "hard blocker 없음" if blocker_ready else "차단 항목 해결 필요",
            "score": 1.2,
        },
    ]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    score = min(score, 10.0)

    if hard_blockers:
        validation_route = "BLOCKED_FOR_LIVE_READINESS"
        verdict = "Live Readiness 검증 차단: hard blocker 해결 필요"
        next_action = "차단 항목을 해결한 뒤 Candidate Review / Pre-Live / Portfolio Proposal 입력을 다시 확인합니다."
    elif paper_tracking_gaps:
        validation_route = "PAPER_TRACKING_REQUIRED"
        verdict = "Paper tracking 보강 필요: 실전 검토 전 운영 기록 연결 필요"
        next_action = "active 후보의 Pre-Live paper_tracking record와 tracking plan을 먼저 정리합니다."
    elif review_gaps:
        validation_route = "NEEDS_PORTFOLIO_RISK_REVIEW"
        verdict = "Portfolio Risk 보강 필요: robustness 전 확인 항목 있음"
        next_action = "비중 집중, 중복, Data Trust gap을 확인한 뒤 Phase 32 robustness 검증으로 넘길지 판단합니다."
    else:
        validation_route = "READY_FOR_ROBUSTNESS_REVIEW"
        verdict = "Phase 32 검증 후보 가능: portfolio risk first pass 통과"
        next_action = "이 후보 또는 proposal을 Phase 32 Robustness / Stress Validation Pack 입력으로 사용할 수 있습니다."

    robustness_validation = _build_portfolio_robustness_validation_result(
        validation_input,
        phase31_route=validation_route,
    )

    component_rows = [
        {
            "Registry ID": row.get("registry_id") or "-",
            "Title": row.get("title") or "-",
            "Role": row.get("proposal_role") or "-",
            "Weight": _portfolio_proposal_optional_float(row.get("target_weight")) or 0.0,
            "Family": row.get("strategy_family") or "-",
            "Benchmark": row.get("benchmark") or "-",
            "Universe": row.get("universe") or "-",
            "Factors": row.get("factors") or "-",
            "Pre-Live": row.get("pre_live_status") or "not_started",
            "Data Trust": row.get("data_trust_status") or "not_attached",
            "Promotion": row.get("promotion") or "-",
            "Deployment": row.get("deployment") or "-",
            "CAGR": row.get("cagr"),
            "MDD": row.get("mdd"),
        }
        for row in components
    ]
    return {
        "source_type": source_type,
        "source_id": source_id,
        "source_label": validation_input.get("source_label") or source_id,
        "validation_route": validation_route,
        "validation_score": score,
        "verdict": verdict,
        "next_action": next_action,
        "hard_blockers": hard_blockers,
        "paper_tracking_gaps": paper_tracking_gaps,
        "review_gaps": review_gaps,
        "checks": checks,
        "component_rows": component_rows,
        "metrics": {
            "components": len(components),
            "active_components": active_count,
            "weight_total": weight_total,
            "max_weight": max_weight,
            "has_core_anchor": has_core_anchor,
        },
        "handoff_summary": {
            "next_phase": "Phase 32 Robustness And Stress Validation Pack",
            "ready_for_robustness": validation_route == "READY_FOR_ROBUSTNESS_REVIEW",
            "requires_paper_tracking": validation_route == "PAPER_TRACKING_REQUIRED",
            "blocked": validation_route == "BLOCKED_FOR_LIVE_READINESS",
            "source_type": source_type,
            "source_id": source_id,
        },
        "robustness_validation": robustness_validation,
    }


# Build a compact validation summary table for saved Portfolio Proposal rows.
def _build_portfolio_risk_validation_summary_rows(
    rows: list[dict[str, Any]],
    current_by_registry_id: dict[str, dict[str, Any]],
    pre_live_by_registry_id: dict[str, dict[str, Any]],
) -> pd.DataFrame:
    display_rows: list[dict[str, Any]] = []
    for row in rows:
        validation_input = _build_portfolio_risk_validation_input_for_proposal(
            proposal_row=row,
            current_by_registry_id=current_by_registry_id,
            pre_live_by_registry_id=pre_live_by_registry_id,
        )
        validation = _build_portfolio_risk_validation_result(validation_input)
        metrics = dict(validation.get("metrics") or {})
        robustness = dict(validation.get("robustness_validation") or {})
        phase33_handoff = dict(robustness.get("phase33_handoff") or {})
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Proposal ID": row.get("proposal_id"),
                "Validation Route": validation.get("validation_route"),
                "Score": validation.get("validation_score"),
                "Robustness Route": robustness.get("robustness_route"),
                "Robustness Score": robustness.get("robustness_score"),
                "Phase33 Handoff": phase33_handoff.get("handoff_route"),
                "Components": metrics.get("active_components"),
                "Weight Total": metrics.get("weight_total"),
                "Max Weight": metrics.get("max_weight"),
                "Hard Blockers": len(validation.get("hard_blockers") or []),
                "Paper Gaps": len(validation.get("paper_tracking_gaps") or []),
                "Review Gaps": len(validation.get("review_gaps") or []),
            }
        )
    return pd.DataFrame(display_rows)


# Build save blockers from selected proposal components and their target roles/weights.
def _portfolio_proposal_open_blockers(
    *,
    selected_rows: list[dict[str, Any]],
    component_inputs: dict[str, dict[str, Any]],
    proposal_id: str,
    total_weight: float,
    existing_proposal_ids: set[str] | None = None,
) -> list[str]:
    blockers: list[str] = []
    proposal_id = proposal_id.strip()
    existing_proposal_ids = existing_proposal_ids or set()
    if not proposal_id:
        blockers.append("Proposal ID is required.")
    elif proposal_id in existing_proposal_ids:
        blockers.append(f"Proposal ID `{proposal_id}` already exists. Change Proposal ID before saving a new draft.")
    if not selected_rows:
        blockers.append("No current candidate selected.")
    for row in selected_rows:
        registry_id = str(row.get("registry_id") or "")
        component_input = component_inputs.get(registry_id) or {}
        try:
            target_weight = float(component_input.get("target_weight") or 0.0)
        except (TypeError, ValueError):
            target_weight = 0.0
        if component_input.get("pre_live_status") == "reject" and target_weight > 0:
            blockers.append(f"{registry_id}: rejected pre-live candidate cannot have active weight.")
        if component_input.get("proposal_role") == "core_anchor":
            result = dict(row.get("result") or {})
            if str(result.get("deployment") or "").lower() == "blocked":
                blockers.append(f"{registry_id}: blocked candidate cannot be core anchor without review.")
    return blockers


def _portfolio_proposal_readiness_guidance(
    *,
    checks: list[dict[str, Any]],
    open_blockers: list[str],
    total_weight: float,
) -> list[str]:
    guidance: list[str] = []
    for check in checks:
        if check.get("ready"):
            continue
        criteria = str(check.get("criteria") or "")
        if criteria == "Proposal Identity":
            guidance.append("Proposal ID가 비어 있거나 후보가 선택되지 않았습니다. 후보 선택과 proposal id를 먼저 확인하세요.")
        elif criteria == "Portfolio Construction":
            guidance.append(f"Target Weight 합계를 100%로 맞추세요. 현재 합계는 {round(total_weight, 4)}%입니다.")
        elif criteria == "Component Role":
            guidance.append("active weight가 있는 후보 중 최소 1개는 Proposal Role을 `core_anchor`로 지정하세요.")
        elif criteria == "Pre-Live State":
            guidance.append("active weight가 있는 후보는 Pre-Live 상태가 `paper_tracking`이어야 합니다.")
        elif criteria == "Operator Context":
            guidance.append("Operator Reason, Next Action, Review Date를 채워 다음 검토 근거를 남기세요.")
        elif criteria == "Blocking Scope":
            if open_blockers:
                guidance.extend(str(blocker) for blocker in open_blockers)
            else:
                guidance.append("저장 blocker가 남아 있습니다. 상세 보기의 open blockers를 확인하세요.")
        else:
            guidance.append(str(check.get("judgment") or criteria))
    return list(dict.fromkeys(guidance))


# Score whether one already-packaged candidate can move directly to the later Live Readiness review.
def _build_portfolio_proposal_direct_readiness_evaluation(
    *,
    selected_row: dict[str, Any] | None,
    pre_live_status: str,
    data_trust_status: str,
) -> dict[str, Any]:
    if not selected_row:
        return {
            "score": 0.0,
            "checks": [
                {
                    "criteria": "Candidate Selection",
                    "ready": False,
                    "current_value": "no candidate",
                    "judgment": "Live Readiness로 보낼 후보 선택 필요",
                    "score": 10.0,
                }
            ],
            "route_label": "LIVE_READINESS_DIRECT_BLOCKED",
            "verdict": "단일 후보 선택 필요",
            "next_action": "Candidate Review를 통과한 current candidate 1개를 선택합니다.",
            "blocking_reasons": ["Candidate Selection"],
            "can_move_to_live_readiness": False,
        }

    result = dict(selected_row.get("result") or {})
    registry_id = str(selected_row.get("registry_id") or "").strip()
    identity_ready = bool(registry_id and (selected_row.get("strategy_family") or selected_row.get("strategy_name")))
    result_ready = any(result.get(key) not in (None, "") for key in ("cagr", "mdd", "end_balance"))
    pre_live_ready = pre_live_status == "paper_tracking"
    promotion = str(result.get("promotion") or "").lower()
    deployment = str(result.get("deployment") or "").lower()
    real_money_signal_ready = bool(promotion or deployment)
    real_money_ready = real_money_signal_ready and promotion != "hold" and deployment not in {"blocked", "reject", "rejected"}
    data_trust_ready = data_trust_status in {"ok", "warning"}
    direct_context_ready = True

    checks = [
        {
            "criteria": "Candidate Identity",
            "ready": identity_ready,
            "current_value": f"id={registry_id or '-'}, family={selected_row.get('strategy_family') or '-'}",
            "judgment": "후보 식별 가능" if identity_ready else "후보 registry id 또는 strategy 식별자 필요",
            "score": 1.4,
        },
        {
            "criteria": "Result Snapshot",
            "ready": result_ready,
            "current_value": f"CAGR={result.get('cagr')}, MDD={result.get('mdd')}, End={result.get('end_balance')}",
            "judgment": "성과 snapshot 있음" if result_ready else "성과 snapshot 필요",
            "score": 1.4,
        },
        {
            "criteria": "Pre-Live State",
            "ready": pre_live_ready,
            "current_value": pre_live_status or "not_started",
            "judgment": "paper tracking 운영 기록 있음" if pre_live_ready else "paper_tracking Pre-Live record 필요",
            "score": 2.0,
        },
        {
            "criteria": "Real-Money Signal",
            "ready": real_money_ready,
            "current_value": f"promotion={promotion or '-'}, deployment={deployment or '-'}",
            "judgment": "hold / blocked 아님" if real_money_ready else "Real-Money hold / blocked 또는 신호 공백",
            "score": 1.8,
        },
        {
            "criteria": "Data Trust",
            "ready": data_trust_ready,
            "current_value": data_trust_status or "not_attached",
            "judgment": "Data Trust attached" if data_trust_ready else "Data Trust snapshot 필요",
            "score": 1.4,
        },
        {
            "criteria": "Direct Portfolio Context",
            "ready": direct_context_ready,
            "current_value": "role=core_anchor, weight=100%, capital=paper_only",
            "judgment": "단일 후보 기본 구성으로 평가" if direct_context_ready else "구성 기본값 필요",
            "score": 2.0,
        },
    ]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    score = min(score, 10.0)
    blocking_reasons = [str(check["criteria"]) for check in checks if not check["ready"]]
    can_move_to_live_readiness = not blocking_reasons

    if can_move_to_live_readiness:
        route_label = "LIVE_READINESS_DIRECT_READY"
        verdict = "단일 후보 통과: 저장 없이 Live Readiness 검토 후보로 볼 수 있음"
        next_action = "이 후보는 별도 proposal draft 저장 없이 이후 Live Readiness 단계에서 실전 전 검토 대상으로 읽을 수 있습니다."
    elif identity_ready and result_ready:
        route_label = "LIVE_READINESS_DIRECT_REVIEW_REQUIRED"
        verdict = "단일 후보 보강 필요: Live Readiness 직행 전 확인 항목 있음"
        next_action = "Pre-Live paper tracking, Real-Money signal, Data Trust snapshot 중 부족한 항목을 보강합니다."
    else:
        route_label = "LIVE_READINESS_DIRECT_BLOCKED"
        verdict = "단일 후보 직행 불가: 후보 패키지 식별 또는 성과 snapshot 필요"
        next_action = "Candidate Review에서 current candidate / Pre-Live 운영 기록을 먼저 정리합니다."

    return {
        "score": score,
        "checks": checks,
        "route_label": route_label,
        "verdict": verdict,
        "next_action": next_action,
        "blocking_reasons": blocking_reasons,
        "can_move_to_live_readiness": can_move_to_live_readiness,
    }


# Score whether the proposal draft is only saveable or ready for a later Live Readiness step.
def _build_portfolio_proposal_readiness_evaluation(
    *,
    selected_rows: list[dict[str, Any]],
    component_inputs: dict[str, dict[str, Any]],
    proposal_id: str,
    total_weight: float,
    operator_reason: str,
    next_action: str,
    review_date_value: date | None,
    open_blockers: list[str],
) -> dict[str, Any]:
    active_components = [
        (row, component_inputs.get(str(row.get("registry_id") or ""), {}))
        for row in selected_rows
        if _component_target_weight(component_inputs.get(str(row.get("registry_id") or ""), {}) or {}) > 0
    ]
    has_active_components = bool(active_components)
    has_core_anchor = any(str(component.get("proposal_role") or "") == "core_anchor" for _, component in active_components)
    component_role_ready = (not has_active_components) or has_core_anchor
    pre_live_ready = (not has_active_components) or all(
        str(component.get("pre_live_status") or "") == "paper_tracking"
        for _, component in active_components
    )
    reason_ready = bool(operator_reason.strip())
    next_action_ready = bool(next_action.strip())
    review_date_ready = bool(review_date_value)
    identity_ready = bool(proposal_id.strip()) and bool(selected_rows)
    construction_ready = bool(selected_rows) and abs(total_weight - 100.0) <= 0.01
    blocker_ready = not open_blockers

    checks = [
        {
            "criteria": "Proposal Identity",
            "ready": identity_ready,
            "current_value": f"id={proposal_id or '-'}, components={len(selected_rows)}",
            "judgment": "proposal 초안 식별 가능" if identity_ready else "proposal id 또는 후보 선택 필요",
            "score": 1.2,
        },
        {
            "criteria": "Portfolio Construction",
            "ready": construction_ready,
            "current_value": f"weight_total={total_weight}%",
            "judgment": "비중 합계 100%" if construction_ready else "target weight 합계 확인 필요",
            "score": 1.8,
        },
        {
            "criteria": "Component Role",
            "ready": component_role_ready,
            "current_value": "core_anchor 있음" if has_core_anchor else "active component 없음" if not has_active_components else "core_anchor 없음",
            "judgment": "포트폴리오 중심 후보 있음"
            if has_core_anchor
            else "active weight를 먼저 입력"
            if not has_active_components
            else "최소 1개 core anchor 필요",
            "score": 1.2,
        },
        {
            "criteria": "Pre-Live State",
            "ready": pre_live_ready,
            "current_value": ", ".join(
                sorted({str(component.get("pre_live_status") or "not_started") for _, component in active_components})
            )
            or "no active component",
            "judgment": "active 후보가 paper_tracking 상태" if pre_live_ready else "active 후보는 paper_tracking 상태가 필요",
            "score": 1.6,
        },
        {
            "criteria": "Operator Context",
            "ready": reason_ready and next_action_ready and review_date_ready,
            "current_value": (
                f"reason={'ok' if reason_ready else 'missing'}, "
                f"next_action={'ok' if next_action_ready else 'missing'}, "
                f"review_date={review_date_value.isoformat() if review_date_value else 'missing'}"
            ),
            "judgment": "판단 이유 / 다음 행동 / 날짜 있음"
            if reason_ready and next_action_ready and review_date_ready
            else "판단 이유, 다음 행동, review date 보강 필요",
            "score": 1.4,
        },
        {
            "criteria": "Blocking Scope",
            "ready": blocker_ready,
            "current_value": f"blockers={len(open_blockers)}",
            "judgment": "저장 blocker 없음" if blocker_ready else "저장 blocker 해결 필요",
            "score": 2.8,
        },
    ]
    score = round(sum(float(check["score"]) for check in checks if check["ready"]), 1)
    score = min(score, 10.0)
    live_readiness_blockers = [str(check["criteria"]) for check in checks if not check["ready"]]
    blocking_guidance = _portfolio_proposal_readiness_guidance(
        checks=checks,
        open_blockers=open_blockers,
        total_weight=total_weight,
    )
    can_save_proposal = bool(identity_ready and construction_ready and blocker_ready)
    can_move_to_live_readiness = bool(can_save_proposal and not live_readiness_blockers)

    if can_move_to_live_readiness:
        route_label = "LIVE_READINESS_CANDIDATE_READY"
        verdict = "Proposal 통과: 저장 후 Live Readiness 후보로 이동 가능"
        next_step = "Save Portfolio Proposal Draft로 포트폴리오 초안을 남긴 뒤 이후 Live Readiness 단계에서 실전 전 검토를 진행합니다."
    elif can_save_proposal:
        route_label = "PROPOSAL_DRAFT_READY"
        verdict = "Proposal 저장 가능: Live Readiness 전 보강 항목 있음"
        next_step = "Proposal draft는 저장할 수 있습니다. 남은 보강 항목을 해결한 뒤 Live Readiness 후보 여부를 다시 판단합니다."
    else:
        route_label = "PROPOSAL_BLOCKED"
        verdict = "Proposal 저장 전 blocker 해결 필요"
        next_step = "후보 선택, weight 합계, rejected/blocked 후보 비중 같은 저장 blocker를 먼저 해결합니다."

    return {
        "score": score,
        "checks": checks,
        "route_label": route_label,
        "verdict": verdict,
        "next_action": next_step,
        "blocking_reasons": live_readiness_blockers,
        "blocking_guidance": blocking_guidance,
        "open_blockers": open_blockers,
        "can_save_proposal": can_save_proposal,
        "can_move_to_live_readiness": can_move_to_live_readiness,
    }
