from __future__ import annotations

import re
from typing import Any, Iterable


PATTERN_GUIDE_CONTRACT_SCHEMA_VERSION = "final_review_pattern_guide_contract_v2"
PATTERN_GUIDE_SCHEMA_VERSION = "final_review_pattern_guide_v2"

_STATE_META = {
    "actionable": ("판단 가능", "positive"),
    "conditional": ("조건부 추적", "warning"),
    "needs_validation": ("추가 검증 필요", "warning"),
    "not_applicable": ("적용 제외", "neutral"),
}

_SOURCE_LABELS = {
    "construction_risk_audit": "구성 위험 검증",
    "component_role_weight_audit": "구성요소 역할·비중 검증",
    "risk_contribution_audit": "위험 기여도 검증",
    "backtest_realism_audit": "비용·유동성 검증",
    "stress_window_rows": "스트레스 구간 검증",
    "rolling_validation": "롤링 성과 검증",
    "regime_split_validation": "시장 국면 분할 검증",
    "walkforward_validation": "Walk-forward 검증",
    "sensitivity_rows": "민감도 검증",
    "benchmark": "비교 기준 검증",
}


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _dict_rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in list(value or []) if isinstance(row, dict)]


def _number(value: Any) -> float | None:
    if isinstance(value, bool):
        return None
    if isinstance(value, (int, float)):
        return float(value)
    text = str(value or "").replace(",", "")
    match = re.search(r"-?\d+(?:\.\d+)?", text)
    return float(match.group()) if match else None


def _percent(value: float | None, *, ratio: bool = False) -> str:
    if value is None:
        return "-"
    normalized = value * 100.0 if ratio else value
    return f"{normalized:.1f}%"


def _date_text(value: Any) -> str:
    text = str(value or "").strip()
    return text[:10] if text else "-"


def _evidence_as_of(validation: dict[str, Any]) -> str:
    snapshot = _as_dict(validation.get("selection_source_snapshot"))
    period = _as_dict(snapshot.get("period"))
    return _date_text(
        period.get("actual_end")
        or period.get("end")
        or validation.get("updated_at")
        or validation.get("created_at")
    )


def _row_text(row: dict[str, Any]) -> str:
    return " | ".join(
        str(row.get(key) or "").strip()
        for key in ("Criteria", "Check", "Scenario", "Metric", "Current", "Evidence", "Meaning")
        if str(row.get(key) or "").strip()
    )


def _find_row(rows: Iterable[dict[str, Any]], *tokens: str) -> dict[str, Any]:
    lowered = tuple(token.lower() for token in tokens)
    for row in rows:
        text = _row_text(row).lower()
        if any(token in text for token in lowered):
            return dict(row)
    return {}


def _row_value(row: dict[str, Any], *keys: str) -> str:
    for key in keys:
        value = row.get(key)
        if value is not None and str(value).strip():
            return str(value).strip()
    return "-"


def _trace(
    *,
    label: str,
    value: str,
    threshold: str,
    source_key: str,
    technical_path: str,
    as_of: str,
) -> dict[str, str]:
    return {
        "label": label,
        "value": value,
        "threshold": threshold,
        "source_label": _SOURCE_LABELS[source_key],
        "technical_path": technical_path,
        "as_of": as_of,
    }


def _state_fields(state: str) -> dict[str, str]:
    label, tone = _STATE_META[state]
    return {"support": state, "support_label": label, "tone": tone}


def _card(
    *,
    pattern: dict[str, Any],
    state: str,
    applicable: bool,
    applicability_reason: str,
    current_diagnosis: str,
    meaning: str,
    change_condition: str,
    next_action: str,
    traces: list[dict[str, str]],
    missing_signals: list[str],
    salience: int,
) -> dict[str, Any]:
    evidence_sources = list(dict.fromkeys(trace["source_label"] for trace in traces))
    evidence_as_of = next((trace["as_of"] for trace in traces if trace["as_of"] != "-"), "-")
    observed = [f"{trace['label']}: {trace['value']}" for trace in traces[:3]]
    return {
        "key": pattern["key"],
        "label": pattern["label"],
        "question": pattern["question"],
        **_state_fields(state),
        "applicable": applicable,
        "applicability_reason": applicability_reason,
        "current_diagnosis": current_diagnosis,
        "meaning": meaning,
        "change_condition": change_condition,
        "next_action": next_action,
        "conclusion": f"{current_diagnosis} {meaning}".strip(),
        "observed": observed,
        "evidence_trace": traces,
        "evidence_sources": evidence_sources,
        "evidence_as_of": evidence_as_of,
        "missing_signals": missing_signals,
        "monitoring_trigger": change_condition,
        "experiment_candidate": f"{pattern['label']} 조건을 바꾼 대안은 별도 counterfactual backtest로 비교합니다.",
        "direct_scenario_claim": state == "actionable",
        "visible_first_read": False,
        "salience": salience,
    }


def _concentration_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    audit = _as_dict(validation.get("construction_risk_audit"))
    metrics = _as_dict(audit.get("metrics"))
    rows = _dict_rows(audit.get("rows"))
    row = _find_row(rows, "component weight concentration", "top holding concentration")
    max_weight = _number(metrics.get("max_component_weight"))
    observed = _percent(max_weight) if max_weight is not None else _row_value(row, "observed_value", "Current")
    threshold_value = _row_value(row, "threshold", "Target")
    threshold = threshold_value if threshold_value != "-" else "75.0% 이하"
    source = _row_value(row, "evidence_source", "source_label", "Source Strength")
    row_as_of = _row_value(row, "as_of", "updated_at")
    trace_as_of = row_as_of if row_as_of != "-" else as_of
    applicable = bool(audit or row)
    complete = observed != "-" and threshold != "-" and (source != "-" or bool(metrics)) and trace_as_of != "-"
    if not applicable:
        state = "not_applicable"
    elif complete:
        state = "actionable"
    else:
        state = "needs_validation"
    coverage = _number(metrics.get("exposure_coverage_weight"))
    diagnosis = (
        f"최대 구성 비중이 {observed}로 집중 기준 {threshold}를 확인해야 합니다."
        if observed != "-"
        else "구성 비중 또는 look-through 집중도를 계산한 근거가 없습니다."
    )
    if coverage is not None and coverage < 99.5:
        diagnosis += f" Look-through 확인 범위는 {_percent(coverage)}입니다."
    traces = []
    if observed != "-":
        traces.append(
            _trace(
                label="최대 구성 비중",
                value=observed,
                threshold=threshold,
                source_key="construction_risk_audit",
                technical_path="validation.construction_risk_audit.metrics.max_component_weight",
                as_of=trace_as_of,
            )
        )
    return _card(
        pattern=pattern,
        state=state,
        applicable=applicable,
        applicability_reason="구성 비중 또는 보유 종목 집중도 근거가 있습니다." if applicable else "구성·보유 비중 근거가 없습니다.",
        current_diagnosis=diagnosis,
        meaning="한 구성요소의 약세가 포트폴리오 전체 성과와 위험을 좌우할 가능성이 큽니다." if complete else "집중 위험의 크기를 아직 확정할 수 없습니다.",
        change_condition=f"최대 구성 비중이 {threshold} 안으로 낮아지거나 look-through 범위가 넓어지면 재평가합니다.",
        next_action="Monitoring에서 최대 구성 비중과 위험 기여도가 함께 낮아지는지 확인합니다." if complete else "구성 비중과 look-through 집중도 근거를 2단계 검증에서 보강합니다.",
        traces=traces,
        missing_signals=[] if complete else ["component_weight", "holdings_or_exposure_concentration"],
        salience=100 if max_weight is not None and max_weight > 75.0 else 65,
    )


def _stock_bond_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    risk = _as_dict(validation.get("risk_contribution_audit"))
    roles = _as_dict(validation.get("component_role_weight_audit"))
    role_rows = _dict_rows(roles.get("component_rows"))
    searchable = " ".join(_row_text(row) for row in role_rows).lower()
    has_equity = any(token in searchable for token in ("equity", "stock", "주식"))
    has_bond = any(token in searchable for token in ("bond", "treasury", "채권"))
    avg_correlation = _number(_as_dict(risk.get("metrics")).get("average_correlation"))
    applicable = has_equity and has_bond
    traces = []
    if avg_correlation is not None:
        traces.append(
            _trace(
                label="구성요소 평균 상관",
                value=f"{avg_correlation:.2f}",
                threshold="주식·채권 역할별 비교 필요",
                source_key="risk_contribution_audit",
                technical_path="validation.risk_contribution_audit.metrics.average_correlation",
                as_of=as_of,
            )
        )
    return _card(
        pattern=pattern,
        state="conditional" if applicable and avg_correlation is not None else ("needs_validation" if applicable else "not_applicable"),
        applicable=applicable,
        applicability_reason="주식과 채권 역할을 가진 구성요소가 함께 있습니다." if applicable else "저장된 역할 근거에서 주식·채권 조합을 확인하지 못했습니다.",
        current_diagnosis=f"구성요소 평균 상관은 {avg_correlation:.2f}입니다." if applicable and avg_correlation is not None else "주식·채권 분산 효과를 직접 비교할 근거가 없습니다.",
        meaning="평균 상관만으로 방어력을 단정하지 않고 역할별 위험 기여 변화가 필요합니다.",
        change_condition="주식·채권 rolling correlation 또는 역할별 위험 기여가 기준 범위를 벗어나면 재검토합니다.",
        next_action="주식·채권 역할별 return matrix를 2단계 검증에 추가합니다." if applicable else "현재 후보에는 이 패턴을 적용하지 않습니다.",
        traces=traces if applicable else [],
        missing_signals=[] if applicable and avg_correlation is not None else ["component_role", "correlation_or_component_return_matrix"],
        salience=45,
    )


def _rate_or_inflation_card(
    pattern: dict[str, Any], validation: dict[str, Any], as_of: str, *, inflation: bool
) -> dict[str, Any]:
    stress_rows = _dict_rows(validation.get("stress_window_rows"))
    construction_rows = _dict_rows(_as_dict(validation.get("construction_risk_audit")).get("rows"))
    stress = _find_row(stress_rows, "inflation / rate shock", "inflation_rate_shock")
    exposure = _find_row(construction_rows, "duration", "treasury", "bond", "inflation")
    result_status = _row_value(stress, "Result Status", "Status")
    portfolio_return = _number(stress.get("Portfolio Return")) if stress else None
    portfolio_mdd = _number(stress.get("Portfolio MDD")) if stress else None
    scenario_computed = result_status.upper() in {"PASS", "REVIEW"} and portfolio_return is not None
    applicable = bool(stress or exposure)
    traces = []
    if scenario_computed:
        traces.append(
            _trace(
                label="2022 물가·금리 충격 수익률",
                value=_percent(portfolio_return, ratio=True),
                threshold="동일 구간 benchmark와 함께 해석",
                source_key="stress_window_rows",
                technical_path="validation.stress_window_rows[category=inflation_rate_shock]",
                as_of=as_of,
            )
        )
        if portfolio_mdd is not None:
            traces.append(
                _trace(
                    label="2022 물가·금리 충격 MDD",
                    value=_percent(portfolio_mdd, ratio=True),
                    threshold="후보 전체 MDD와 비교",
                    source_key="stress_window_rows",
                    technical_path="validation.stress_window_rows[category=inflation_rate_shock].Portfolio MDD",
                    as_of=as_of,
                )
            )
    if inflation:
        state = "conditional" if scenario_computed else ("needs_validation" if applicable else "not_applicable")
        diagnosis = (
            f"2022 물가·금리 충격 구간 수익률은 {_percent(portfolio_return, ratio=True)}, MDD는 {_percent(portfolio_mdd, ratio=True)}입니다."
            if scenario_computed
            else "인플레이션 충격 구간의 계산 결과가 없습니다."
        )
        meaning = "해당 구간 방어력은 관측됐지만 성장 둔화형·원자재형 인플레이션을 구분한 결과는 아닙니다."
        change = "물가 상승과 성장 둔화가 함께 나타날 때 MDD와 benchmark spread가 악화되면 재검토합니다."
        action = "Monitoring에서 물가·성장 국면별 MDD와 benchmark spread를 분리해 누적합니다."
        missing = [] if scenario_computed else ["inflation_regime_result", "inflation_sensitive_exposure"]
        salience = 72
    else:
        state = "conditional" if scenario_computed and exposure else ("needs_validation" if applicable else "not_applicable")
        diagnosis = (
            f"2022 금리 충격 구간 수익률은 {_percent(portfolio_return, ratio=True)}였지만 듀레이션 노출 근거는 충분하지 않습니다."
            if scenario_computed
            else "금리 구간 성과와 듀레이션 노출을 함께 확인할 근거가 없습니다."
        )
        meaning = "충격 구간 성과는 확인할 수 있어도 어떤 자산의 듀레이션이 결과를 만들었는지는 단정할 수 없습니다."
        change = "금리 상승 구간 MDD가 확대되거나 듀레이션 노출이 늘면 재검토합니다."
        action = "2단계 검증에서 듀레이션·금리 민감 노출을 연결한 뒤 Monitoring 조건으로 확정합니다."
        missing = [] if scenario_computed and exposure else ["duration_or_rate_sensitive_exposure"]
        salience = 86
    return _card(
        pattern=pattern,
        state=state,
        applicable=applicable,
        applicability_reason="물가·금리 스트레스 또는 민감 노출 근거가 있습니다." if applicable else "관련 스트레스·노출 근거가 없습니다.",
        current_diagnosis=diagnosis,
        meaning=meaning,
        change_condition=change,
        next_action=action if applicable else "현재 후보에는 이 패턴을 적용하지 않습니다.",
        traces=traces,
        missing_signals=missing,
        salience=salience,
    )


def _tail_risk_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    rolling = _as_dict(validation.get("rolling_validation"))
    if not rolling:
        rolling = _as_dict(_as_dict(validation.get("robustness_validation")).get("rolling_validation"))
    metrics = _as_dict(rolling.get("metrics"))
    worst_mdd = _number(metrics.get("worst_rolling_mdd"))
    stress_rows = _dict_rows(validation.get("stress_window_rows"))
    computed = [row for row in stress_rows if _row_value(row, "Result Status").upper() in {"PASS", "REVIEW"} and _number(row.get("Portfolio MDD")) is not None]
    applicable = worst_mdd is not None or bool(computed)
    traces = []
    if worst_mdd is not None:
        traces.append(
            _trace(
                label="최악 36개월 rolling MDD",
                value=_percent(worst_mdd, ratio=True),
                threshold="-25.0% 이상",
                source_key="rolling_validation",
                technical_path="validation.rolling_validation.metrics.worst_rolling_mdd",
                as_of=as_of,
            )
        )
    computed_mdds = [_number(row.get("Portfolio MDD")) for row in computed]
    computed_mdds = [value for value in computed_mdds if value is not None]
    worst_stress = min(computed_mdds) if computed_mdds else None
    if worst_stress is not None:
        traces.append(
            _trace(
                label="계산된 스트레스 최악 MDD",
                value=_percent(worst_stress, ratio=True),
                threshold="계산된 stress window 기준",
                source_key="stress_window_rows",
                technical_path="validation.stress_window_rows[*].Portfolio MDD",
                as_of=as_of,
            )
        )
    diagnosis = (
        f"36개월 rolling 최악 MDD는 {_percent(worst_mdd, ratio=True)}이며 계산된 stress window는 {len(computed)}개입니다."
        if worst_mdd is not None
        else "낙폭과 stress 결과를 직접 확인할 근거가 없습니다."
    )
    return _card(
        pattern=pattern,
        state="actionable" if applicable else "not_applicable",
        applicable=applicable,
        applicability_reason="rolling MDD 또는 계산된 stress 결과가 있습니다." if applicable else "낙폭·stress 계산 결과가 없습니다.",
        current_diagnosis=diagnosis,
        meaning="평균 수익보다 실제 손실 구간에서 허용 가능한 낙폭을 유지했는지가 핵심입니다.",
        change_condition="rolling MDD가 -25% 아래로 내려가거나 새 stress 구간 손실이 기존 최악치를 넘으면 재검토합니다.",
        next_action="Monitoring에서 rolling MDD와 아직 계산되지 않은 covered stress window를 함께 추적합니다." if applicable else "현재 후보에는 이 패턴을 적용하지 않습니다.",
        traces=traces,
        missing_signals=[] if applicable else ["drawdown_or_stress_result", "recovery_or_tail_metric"],
        salience=92,
    )


def _trend_regime_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    regime = _as_dict(validation.get("regime_split_validation"))
    walkforward = _as_dict(validation.get("walkforward_validation"))
    source_text = str(validation.get("source_title") or _as_dict(validation.get("selection_source_snapshot")).get("source_title") or "").lower()
    tactical = any(token in source_text for token in ("trend", "momentum", "gtaa", "relative strength"))
    metrics = _as_dict(regime.get("metrics"))
    bucket_count = _number(metrics.get("regime_bucket_count") or metrics.get("bucket_count"))
    applicable = tactical or bool(regime)
    traces = []
    if regime:
        traces.append(
            _trace(
                label="시장 국면 분할",
                value=f"{int(bucket_count)}개 국면" if bucket_count is not None else _row_value(regime, "summary", "status"),
                threshold="국면별 성과 비교",
                source_key="regime_split_validation",
                technical_path="validation.regime_split_validation",
                as_of=as_of,
            )
        )
    if walkforward:
        traces.append(
            _trace(
                label="Walk-forward 상태",
                value=_row_value(walkforward, "status", "route", "summary"),
                threshold="OOS 구간 유지",
                source_key="walkforward_validation",
                technical_path="validation.walkforward_validation",
                as_of=as_of,
            )
        )
    return _card(
        pattern=pattern,
        state="conditional" if applicable and regime else ("needs_validation" if applicable else "not_applicable"),
        applicable=applicable,
        applicability_reason="추세형 전략 또는 시장 국면 분할 근거가 있습니다." if applicable else "추세·국면형 후보라는 근거가 없습니다.",
        current_diagnosis="시장 국면 분할 결과는 있지만 추세장·횡보장별 원인을 직접 분리하지는 못했습니다." if regime else "추세형 후보이지만 국면별 결과가 없습니다.",
        meaning="추세장에서의 강점이 급반전·횡보장에서도 유지된다고 가정할 수 없습니다.",
        change_condition="국면별 초과성과가 음수로 전환되거나 OOS 열위가 반복되면 재검토합니다.",
        next_action="Monitoring에서 추세·횡보·반전 국면 라벨과 상대 성과를 함께 누적합니다." if applicable else "현재 후보에는 이 패턴을 적용하지 않습니다.",
        traces=traces,
        missing_signals=[] if regime and walkforward else ["trend_regime_result", "out_of_sample_or_regime_split"],
        salience=62,
    )


def _component_dependency_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    audit = _as_dict(validation.get("risk_contribution_audit"))
    metrics = _as_dict(audit.get("metrics"))
    active = int(_number(metrics.get("active_components")) or 0)
    contribution = _number(metrics.get("max_risk_contribution"))
    sensitivity = _dict_rows(validation.get("sensitivity_rows"))
    drop_rows = [row for row in sensitivity if str(row.get("Scenario") or "").startswith("Drop-one:")]
    worst_drop = min((_number(row.get("CAGR Delta")) for row in drop_rows), default=None)
    applicable = active > 1 or bool(drop_rows)
    traces = []
    if contribution is not None:
        traces.append(
            _trace(
                label="최대 위험 기여도",
                value=_percent(contribution, ratio=True),
                threshold="80.0% 이하",
                source_key="risk_contribution_audit",
                technical_path="validation.risk_contribution_audit.metrics.max_risk_contribution",
                as_of=as_of,
            )
        )
    if worst_drop is not None:
        traces.append(
            _trace(
                label="최악 drop-one CAGR 변화",
                value=_percent(worst_drop, ratio=True),
                threshold="구성요소 제거 시 급락 여부",
                source_key="sensitivity_rows",
                technical_path="validation.sensitivity_rows[Scenario^=Drop-one]",
                as_of=as_of,
            )
        )
    concentration = contribution is not None and contribution > 0.8
    diagnosis = (
        f"{active}개 구성 중 최대 위험 기여도가 {_percent(contribution, ratio=True)}로 80.0% 기준을 넘습니다."
        if contribution is not None
        else "구성요소별 위험 기여도를 계산한 근거가 없습니다."
    )
    return _card(
        pattern=pattern,
        state="actionable" if applicable and contribution is not None and drop_rows else ("needs_validation" if applicable else "not_applicable"),
        applicable=applicable,
        applicability_reason="복수 구성요소와 drop-one 또는 위험 기여도 근거가 있습니다." if applicable else "단일 구성 후보이거나 의존성 근거가 없습니다.",
        current_diagnosis=diagnosis,
        meaning="명목 비중이 분산돼 보여도 한 구성요소가 실제 변동성 대부분을 설명할 수 있습니다." if concentration else "구성요소 의존도를 계속 확인할 수 있습니다.",
        change_condition="최대 위험 기여도가 80%를 넘거나 핵심 구성 제거 시 CAGR가 크게 낮아지면 재검토합니다.",
        next_action="Monitoring에서 구성 비중과 위험 기여도를 함께 보고, 핵심 구성요소 약화 시 후보를 재검토합니다." if applicable else "현재 후보에는 이 패턴을 적용하지 않습니다.",
        traces=traces,
        missing_signals=[] if contribution is not None and drop_rows else ["risk_contribution", "drop_one_or_dependency_result"],
        salience=98 if concentration else 76,
    )


def _liquidity_cost_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    audit = _as_dict(validation.get("backtest_realism_audit"))
    cost = _as_dict(audit.get("cost_model_contract"))
    turnover = _as_dict(audit.get("turnover_evidence_contract"))
    liquidity = _as_dict(audit.get("liquidity_capacity_contract"))
    bps = _number(cost.get("transaction_cost_bps"))
    avg_turnover = _number(turnover.get("avg_turnover"))
    freshness = str(liquidity.get("freshness_status") or "unknown")
    applicable = bool(audit)
    traces = []
    if bps is not None:
        traces.append(
            _trace(
                label="적용 거래비용",
                value=f"{bps:.1f} bps",
                threshold="net curve 반영",
                source_key="backtest_realism_audit",
                technical_path="validation.backtest_realism_audit.cost_model_contract.transaction_cost_bps",
                as_of=as_of,
            )
        )
    if avg_turnover is not None:
        traces.append(
            _trace(
                label="평균 turnover",
                value=_percent(avg_turnover, ratio=True),
                threshold="비용 민감도와 함께 해석",
                source_key="backtest_realism_audit",
                technical_path="validation.backtest_realism_audit.turnover_evidence_contract.avg_turnover",
                as_of=as_of,
            )
        )
    state = "conditional" if applicable and bps is not None and avg_turnover is not None else ("needs_validation" if applicable else "not_applicable")
    diagnosis = (
        f"거래비용 {bps:.1f} bps가 net curve에 반영됐고 평균 turnover는 {_percent(avg_turnover, ratio=True)}입니다. 유동성 snapshot은 {freshness} 상태입니다."
        if bps is not None and avg_turnover is not None
        else "비용·turnover·유동성을 함께 판단할 근거가 부족합니다."
    )
    return _card(
        pattern=pattern,
        state=state,
        applicable=applicable,
        applicability_reason="net cost 또는 turnover 검증 근거가 있습니다." if applicable else "비용·유동성 검증 근거가 없습니다.",
        current_diagnosis=diagnosis,
        meaning="과거 gross 성과가 좋아도 회전율과 유동성 악화가 실제 net 성과를 낮출 수 있습니다.",
        change_condition="turnover 또는 추정 비용이 기준보다 커지거나 유동성 snapshot이 오래되면 재검토합니다.",
        next_action="Monitoring에서 turnover와 추정 비용을 함께 누적하고 stale 유동성은 다음 2단계 검증에서 갱신합니다." if applicable else "현재 후보에는 이 패턴을 적용하지 않습니다.",
        traces=traces,
        missing_signals=[] if state == "conditional" else ["turnover_or_cost", "liquidity_or_capacity"],
        salience=84,
    )


def _benchmark_card(pattern: dict[str, Any], validation: dict[str, Any], packet: dict[str, Any], as_of: str) -> dict[str, Any]:
    stress_rows = _dict_rows(validation.get("stress_window_rows"))
    spreads = [_number(row.get("Benchmark Spread")) for row in stress_rows if _number(row.get("Benchmark Spread")) is not None]
    walkforward = _as_dict(validation.get("walkforward_validation"))
    gate = _as_dict(packet.get("selection_gate_policy_snapshot") or packet.get("gate_policy_snapshot"))
    benchmark_rows = [row for row in _dict_rows(gate.get("policy_rows")) if str(row.get("Group") or "").lower() == "benchmark"]
    applicable = bool(spreads or walkforward or benchmark_rows)
    traces = []
    if spreads:
        traces.append(
            _trace(
                label="계산된 stress benchmark spread 범위",
                value=f"{_percent(min(spreads), ratio=True)} ~ {_percent(max(spreads), ratio=True)}",
                threshold="동일 구간 비교",
                source_key="benchmark",
                technical_path="validation.stress_window_rows[*].Benchmark Spread",
                as_of=as_of,
            )
        )
    state = "conditional" if applicable and spreads else ("needs_validation" if applicable else "not_applicable")
    return _card(
        pattern=pattern,
        state=state,
        applicable=applicable,
        applicability_reason="benchmark spread, walk-forward 또는 benchmark policy 근거가 있습니다." if applicable else "비교 기준 근거가 없습니다.",
        current_diagnosis=f"계산된 stress 구간의 benchmark spread는 {_percent(min(spreads), ratio=True)}에서 {_percent(max(spreads), ratio=True)} 사이입니다." if spreads else "비교 기준은 있으나 구간별 상대 성과를 계산한 근거가 부족합니다.",
        meaning="일부 구간 우위만으로 후보 고유의 지속적 초과성과를 단정할 수 없습니다.",
        change_condition="rolling 또는 stress 상대 성과가 반복적으로 음수가 되면 선정 근거를 재검토합니다.",
        next_action="Monitoring에서 동일 기간·빈도의 benchmark 대비 rolling 상대 성과를 누적합니다." if applicable else "2단계 검증에서 비교 기준을 먼저 지정합니다.",
        traces=traces,
        missing_signals=[] if spreads else ["benchmark_parity", "relative_performance"],
        salience=78,
    )


def _parameter_card(pattern: dict[str, Any], validation: dict[str, Any], as_of: str) -> dict[str, Any]:
    rows = _dict_rows(validation.get("sensitivity_rows"))
    computed = [row for row in rows if _row_value(row, "Result Status").upper() in {"PASS", "REVIEW"}]
    pending = [row for row in rows if _row_value(row, "Result Status").upper() == "NOT_RUN"]
    review = [row for row in rows if _row_value(row, "Result Status").upper() == "REVIEW"]
    applicable = bool(rows)
    deltas = [abs(value) for value in (_number(row.get("CAGR Delta")) for row in computed) if value is not None]
    worst = max(deltas) if deltas else None
    traces = []
    if computed:
        traces.append(
            _trace(
                label="계산된 민감도",
                value=f"{len(computed)}개 (REVIEW {len(review)}개)",
                threshold="기간·비중·구성 변화",
                source_key="sensitivity_rows",
                technical_path="validation.sensitivity_rows",
                as_of=as_of,
            )
        )
    if worst is not None:
        traces.append(
            _trace(
                label="최대 절대 CAGR 변화",
                value=_percent(worst, ratio=True),
                threshold="민감도 결과 비교",
                source_key="sensitivity_rows",
                technical_path="validation.sensitivity_rows[*].CAGR Delta",
                as_of=as_of,
            )
        )
    state = "conditional" if applicable and computed else ("needs_validation" if applicable else "not_applicable")
    return _card(
        pattern=pattern,
        state=state,
        applicable=applicable,
        applicability_reason="기간·구성·비중 민감도 row가 있습니다." if applicable else "민감도 검증 근거가 없습니다.",
        current_diagnosis=f"민감도 {len(computed)}개를 계산했고 {len(review)}개는 REVIEW, 고급 parameter perturbation {len(pending)}개는 미실행입니다." if applicable else "파라미터와 리밸런싱 변화에 대한 결과가 없습니다.",
        meaning="기본 결과는 비교할 수 있지만 전략 내부 파라미터 변화까지 안정적이라고 말할 수는 없습니다.",
        change_condition="기간·비중·파라미터 변경 시 CAGR 또는 MDD 변화가 기존 민감도 범위를 넘으면 재검토합니다.",
        next_action="Monitoring에서는 계산된 민감도 범위를 기준선으로 쓰고, 미실행 parameter perturbation은 다음 2단계 검증 과제로 남깁니다." if applicable else "2단계 검증에서 민감도 시나리오를 먼저 계산합니다.",
        traces=traces,
        missing_signals=[] if not pending and computed else ["strategy_parameter_perturbation"],
        salience=88,
    )


def build_pattern_guide_contract(catalog: Iterable[dict[str, Any]]) -> dict[str, Any]:
    patterns = []
    for rank, raw_pattern in enumerate(catalog, start=1):
        pattern = dict(raw_pattern)
        patterns.append(
            {
                "rank": rank,
                **pattern,
                "support_contract": {
                    "actionable": "적용 대상이며 관측값과 비교 기준이 있어 현재 판단과 Monitoring 조건을 제시합니다.",
                    "conditional": "직접 근거는 있지만 원인 귀속 또는 일부 축이 부족해 조건부로 추적합니다.",
                    "needs_validation": "후보에 적용되지만 필수 근거가 부족해 2단계 검증 과제로 돌립니다.",
                    "not_applicable": "후보 구성과 저장 evidence상 이 패턴을 적용할 이유가 없습니다.",
                },
            }
        )
    return {
        "schema_version": PATTERN_GUIDE_CONTRACT_SCHEMA_VERSION,
        "patterns": patterns,
        "support_states": [
            {"key": key, "label": label, "tone": tone}
            for key, (label, tone) in _STATE_META.items()
        ],
        "rules": {
            "stored_evidence_only": True,
            "freeform_generation": False,
            "structured_source_adapters_only": True,
            "first_read_card_limit": 6,
            "direct_scenario_claim_requires_observation": True,
            "alternative_allocation_requires_counterfactual_backtest": True,
        },
        "boundaries": {
            "validation_rerun": False,
            "provider_fetch": False,
            "storage_write": False,
            "investment_advice": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


def build_pattern_guide(
    *,
    validation: dict[str, Any],
    investability_packet: dict[str, Any],
    catalog: Iterable[dict[str, Any]],
) -> dict[str, Any]:
    validation = _as_dict(validation)
    packet = _as_dict(investability_packet)
    as_of = _evidence_as_of(validation)
    builders = {
        "concentration": lambda pattern: _concentration_card(pattern, validation, as_of),
        "stock_bond_diversification": lambda pattern: _stock_bond_card(pattern, validation, as_of),
        "rate_duration": lambda pattern: _rate_or_inflation_card(pattern, validation, as_of, inflation=False),
        "inflation": lambda pattern: _rate_or_inflation_card(pattern, validation, as_of, inflation=True),
        "tail_risk": lambda pattern: _tail_risk_card(pattern, validation, as_of),
        "trend_regime": lambda pattern: _trend_regime_card(pattern, validation, as_of),
        "component_dependency": lambda pattern: _component_dependency_card(pattern, validation, as_of),
        "liquidity_cost": lambda pattern: _liquidity_cost_card(pattern, validation, as_of),
        "benchmark_dependency": lambda pattern: _benchmark_card(pattern, validation, packet, as_of),
        "parameter_sensitivity": lambda pattern: _parameter_card(pattern, validation, as_of),
    }
    cards = [builders[str(pattern["key"])](dict(pattern)) for pattern in catalog]
    first_read = sorted(
        [card for card in cards if card["support"] != "not_applicable"],
        key=lambda card: (-int(card["salience"]), str(card["key"])),
    )[:6]
    visible_keys = {str(card["key"]) for card in first_read}
    for card in cards:
        card["visible_first_read"] = str(card["key"]) in visible_keys
    visible_cards = [card for card in cards if card["visible_first_read"]]
    additional_cards = [card for card in cards if not card["visible_first_read"]]
    support_counts = {
        state: sum(1 for card in cards if card["support"] == state)
        for state in _STATE_META
    }
    return {
        "schema_version": PATTERN_GUIDE_SCHEMA_VERSION,
        "summary": {
            "headline": "저장된 검증 근거로 지금 추적할 변화와 다음 행동을 정리합니다.",
            "support_counts": support_counts,
            "visible_count": len(visible_cards),
            "additional_count": len(additional_cards),
            "boundary_note": "새 검증을 실행하지 않습니다. 근거가 부족한 패턴은 단정하지 않고 2단계 검증 과제로 구분합니다.",
        },
        "cards": cards,
        "visible_cards": visible_cards,
        "additional_cards": additional_cards,
        "contract": build_pattern_guide_contract(catalog),
        "boundaries": {
            "validation_rerun": False,
            "provider_fetch": False,
            "storage_write": False,
            "freeform_generation": False,
            "investment_advice": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }
