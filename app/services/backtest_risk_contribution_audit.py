from __future__ import annotations

from typing import Any


RISK_CONTRIBUTION_AUDIT_SCHEMA_VERSION = "risk_contribution_audit_v1"

RISK_CONTRIBUTION_READY = "RISK_CONTRIBUTION_READY"
RISK_CONTRIBUTION_REVIEW = "RISK_CONTRIBUTION_REVIEW"
RISK_CONTRIBUTION_NEEDS_INPUT = "RISK_CONTRIBUTION_NEEDS_INPUT"
RISK_CONTRIBUTION_BLOCKED = "RISK_CONTRIBUTION_BLOCKED"

RISK_CONTRIBUTION_ROUTE_LABELS = {
    RISK_CONTRIBUTION_READY: "Ready",
    RISK_CONTRIBUTION_REVIEW: "Review Required",
    RISK_CONTRIBUTION_NEEDS_INPUT: "Evidence Input Needed",
    RISK_CONTRIBUTION_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}

_MAX_CORRELATION_REVIEW = 0.85
_MAX_RISK_CONTRIBUTION_REVIEW = 0.80


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        return float(value)
    except (TypeError, ValueError):
        return None


def _optional_int(value: Any) -> int | None:
    numeric = _optional_float(value)
    if numeric is None:
        return None
    return int(numeric)


def _format_float(value: Any, *, digits: int = 2) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:.{digits}f}"


def _format_pct(value: Any, *, digits: int = 1) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "-"
    return f"{numeric * 100.0:.{digits}f}%"


def _status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "NONE", "NULL", "N/A", "UNKNOWN"}:
        return default
    if text in {"BLOCKED", "BLOCK", "ERROR", "FAILED", "FAIL"} or "ERROR" in text:
        return "BLOCKED"
    if text in {"NOT_RUN", "MISSING", "NO_DATA", "UNAVAILABLE"}:
        return "NEEDS_INPUT"
    if text in {"PASS", "OK", "READY", "SUCCESS", "COMPLETE", "COMPLETED"}:
        return "PASS"
    if text.startswith("READY_"):
        return "PASS"
    if text in {"REVIEW", "STALE", "PARTIAL", "WARNING", "WARN", "WATCH"} or "REVIEW" in text:
        return "REVIEW"
    return default


def _row(
    *,
    criteria: str,
    status: str,
    current: Any,
    evidence: Any,
    next_action: str,
    meaning: str,
    source_strength: str,
) -> dict[str, Any]:
    normalized = status if status in _STATUS_RANK else _status(status, default="REVIEW")
    return {
        "Criteria": criteria,
        "Status": normalized,
        "Ready": normalized == "PASS",
        "Current": _safe_text(current),
        "Evidence": _safe_text(evidence),
        "Source Strength": source_strength,
        "Next Action": next_action,
        "Meaning": meaning,
    }


def _route_from_rows(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row.get("Status") or "NEEDS_INPUT").upper() for row in rows}
    if "BLOCKED" in statuses:
        return RISK_CONTRIBUTION_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return RISK_CONTRIBUTION_NEEDS_INPUT
    if "REVIEW" in statuses:
        return RISK_CONTRIBUTION_REVIEW
    return RISK_CONTRIBUTION_READY


def _find_diagnostic(validation: dict[str, Any], domain: str) -> dict[str, Any]:
    for diagnostic in _as_list(validation.get("diagnostic_results")):
        row = dict(diagnostic or {})
        if str(row.get("domain") or "") == domain:
            return row
    return {}


def _curve_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    rows = [dict(row or {}) for row in _as_list(curve_evidence.get("component_curve_rows")) if isinstance(row, dict)]
    if rows:
        return rows
    diagnostic = _find_diagnostic(validation, "correlation_diversification_risk_contribution")
    return [dict(row or {}) for row in _as_list(diagnostic.get("evidence_rows")) if isinstance(row, dict)]


def _source_strength(validation: dict[str, Any], diagnostic: dict[str, Any]) -> str:
    metrics = dict(validation.get("metrics") or {})
    active_components = _optional_int(metrics.get("active_components")) or 0
    diagnostic_metrics = dict(diagnostic.get("metrics") or {})
    monthly_rows = _optional_int(diagnostic_metrics.get("monthly_return_rows")) or 0
    if active_components <= 1:
        return "single_component"
    if monthly_rows <= 0:
        return "missing_component_matrix"
    rows = _curve_rows(validation)
    sources = {
        str(row.get("Curve Source") or row.get("source") or "").strip().lower()
        for row in rows
        if str(row.get("Curve Source") or row.get("source") or "").strip()
    }
    if not sources:
        return "component_matrix_no_source"
    if sources == {"actual_runtime_replay"}:
        return "runtime_component_curves"
    if sources == {"embedded_result_curve"}:
        return "embedded_component_curves"
    if sources == {"db_price_proxy"}:
        return "db_price_proxy"
    if any("proxy" in source for source in sources):
        return "mixed_with_proxy"
    return "mixed_component_curves"


def _component_matrix_row(
    validation: dict[str, Any],
    diagnostic: dict[str, Any],
    source_strength: str,
) -> dict[str, Any]:
    metrics = dict(validation.get("metrics") or {})
    diagnostic_metrics = dict(diagnostic.get("metrics") or {})
    active_components = _optional_int(metrics.get("active_components")) or 0
    monthly_rows = _optional_int(diagnostic_metrics.get("monthly_return_rows")) or 0
    curve_rows = _curve_rows(validation)
    usable_curve_rows = [
        row for row in curve_rows if (_optional_int(row.get("Rows") or row.get("rows")) or 0) > 0
    ]
    if active_components <= 1:
        status = "REVIEW"
        next_action = "단일 component 후보는 상관 / risk contribution 분산을 판단할 수 없으므로 목적을 재확인합니다."
    elif monthly_rows <= 0 or len(usable_curve_rows) < 2:
        status = "NEEDS_INPUT"
        next_action = "component별 return curve replay 또는 usable curve evidence를 보강합니다."
    elif source_strength in {"db_price_proxy", "mixed_with_proxy", "mixed_component_curves", "component_matrix_no_source"}:
        status = "REVIEW"
        next_action = "proxy 또는 mixed source matrix이므로 실제 전략 replay와 차이를 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Component return matrix coverage",
        status=status,
        current=f"components {active_components} / monthly rows {monthly_rows} / curve rows {len(usable_curve_rows)}",
        evidence=diagnostic.get("summary") or "component return matrix evidence",
        next_action=next_action,
        meaning="상관 / risk contribution 계산에 필요한 component별 return matrix가 있는지 확인합니다.",
        source_strength=source_strength,
    )


def _correlation_row(diagnostic: dict[str, Any], source_strength: str) -> dict[str, Any]:
    metrics = dict(diagnostic.get("metrics") or {})
    max_corr = _optional_float(metrics.get("max_correlation"))
    avg_corr = _optional_float(metrics.get("average_correlation"))
    if max_corr is None:
        status = "NEEDS_INPUT"
        next_action = "component return matrix를 보강해 pairwise correlation을 계산합니다."
    elif max_corr > _MAX_CORRELATION_REVIEW:
        status = "REVIEW"
        next_action = "상관이 높은 component가 같은 risk source에 노출되는지 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Pairwise correlation",
        status=status,
        current=f"avg {_format_float(avg_corr)} / max {_format_float(max_corr)}",
        evidence=f"review line max correlation {_MAX_CORRELATION_REVIEW:.2f}",
        next_action=next_action,
        meaning="component 간 월별 수익률 움직임이 과도하게 같은 방향인지 확인합니다.",
        source_strength=source_strength,
    )


def _risk_contribution_row(diagnostic: dict[str, Any], source_strength: str) -> dict[str, Any]:
    metrics = dict(diagnostic.get("metrics") or {})
    max_risk = _optional_float(metrics.get("max_risk_contribution"))
    if max_risk is None:
        status = "NEEDS_INPUT"
        next_action = "component return matrix를 보강해 risk contribution proxy를 계산합니다."
    elif max_risk > _MAX_RISK_CONTRIBUTION_REVIEW:
        status = "REVIEW"
        next_action = "특정 component가 포트폴리오 변동성 대부분을 설명하는지 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Risk contribution concentration",
        status=status,
        current=f"max {_format_pct(max_risk)}",
        evidence=f"volatility contribution proxy / review line {_format_pct(_MAX_RISK_CONTRIBUTION_REVIEW)}",
        next_action=next_action,
        meaning="목표 비중이 낮아도 volatility 기준 risk contribution이 한 component에 몰리는지 확인합니다.",
        source_strength=source_strength,
    )


def _find_sensitivity_row(validation: dict[str, Any], check_name: str) -> dict[str, Any]:
    sensitivity = dict(validation.get("sensitivity_interpretation") or {})
    for row in _as_list(sensitivity.get("rows")):
        candidate = dict(row or {})
        if str(candidate.get("Check") or "").strip().lower() == check_name.strip().lower():
            return candidate
    robustness = dict(validation.get("robustness_validation") or {})
    robustness_sensitivity = dict(robustness.get("sensitivity_interpretation") or {})
    for row in _as_list(robustness_sensitivity.get("rows")):
        candidate = dict(row or {})
        if str(candidate.get("Check") or "").strip().lower() == check_name.strip().lower():
            return candidate
    return {}


def _component_dependency_row(validation: dict[str, Any], source_strength: str) -> dict[str, Any]:
    dependency = _find_sensitivity_row(validation, "Component dependency")
    raw_status = str(dependency.get("Status") or "NOT_RUN").upper()
    status = _status(raw_status, default="NEEDS_INPUT")
    if status == "NEEDS_INPUT":
        next_action = "drop-one component sensitivity를 계산해 특정 component 의존성을 확인합니다."
    elif status == "REVIEW":
        next_action = "해당 component가 빠졌을 때 성과 / MDD가 약해지는 이유를 Final Review 근거에 남깁니다."
    else:
        next_action = "추가 조치 없음"
    return _row(
        criteria="Drop-one component dependency",
        status=status,
        current=dependency.get("Finding") or raw_status,
        evidence=dependency.get("Why It Matters") or "component dependency row missing",
        next_action=next_action,
        meaning="특정 component 하나가 빠졌을 때 포트폴리오 안정성이 급격히 약해지는지 확인합니다.",
        source_strength=source_strength,
    )


def _execution_boundary_row(source_strength: str) -> dict[str, Any]:
    return _row(
        criteria="Storage / execution boundary",
        status="PASS",
        current="read-only compact evidence",
        evidence="raw return matrix storage disabled / registry_write=False / live approval disabled",
        next_action="추가 조치 없음",
        meaning="이 audit은 raw return matrix나 covariance artifact를 저장하지 않는 검증 read model입니다.",
        source_strength=source_strength,
    )


def build_risk_contribution_audit(validation: dict[str, Any]) -> dict[str, Any]:
    """Summarize correlation / risk contribution evidence without storing raw matrices."""

    validation = dict(validation or {})
    diagnostic = _find_diagnostic(validation, "correlation_diversification_risk_contribution")
    source_strength = _source_strength(validation, diagnostic)
    rows = [
        _component_matrix_row(validation, diagnostic, source_strength),
        _correlation_row(diagnostic, source_strength),
        _risk_contribution_row(diagnostic, source_strength),
        _component_dependency_row(validation, source_strength),
        _execution_boundary_row(source_strength),
    ]
    route = _route_from_rows(rows)
    status_counts = {
        status: sum(1 for row in rows if row.get("Status") == status)
        for status in _STATUS_RANK
    }
    if route == RISK_CONTRIBUTION_READY:
        conclusion = "Risk contribution audit 기준으로 즉시 보강이 필요한 상관 / 위험기여 공백이 없습니다."
        next_action = "Final Review에서 concentration / overlap과 함께 operator 판단을 확인합니다."
    elif route == RISK_CONTRIBUTION_BLOCKED:
        conclusion = "Risk contribution audit에서 source 차단 항목이 발견됐습니다."
        next_action = "component curve source를 복구한 뒤 다시 검증합니다."
    elif route == RISK_CONTRIBUTION_NEEDS_INPUT:
        conclusion = "상관 / 위험기여 판단을 위해 component return matrix 또는 drop-one evidence가 더 필요합니다."
        next_action = "component별 runtime replay 또는 usable curve evidence를 우선 보강합니다."
    else:
        conclusion = "상관 / 위험기여 근거는 일부 확인됐지만 REVIEW 항목이 남아 있습니다."
        next_action = "REVIEW 항목을 Final Review 판단 사유에 명시하거나 component evidence를 보강합니다."

    diagnostic_metrics = dict(diagnostic.get("metrics") or {})
    metrics = {
        "ready_rows": status_counts["PASS"],
        "total_rows": len(rows),
        "pass": status_counts["PASS"],
        "review": status_counts["REVIEW"],
        "needs_input": status_counts["NEEDS_INPUT"],
        "blocked": status_counts["BLOCKED"],
        "source_strength": source_strength,
        "active_components": _optional_int(dict(validation.get("metrics") or {}).get("active_components")) or 0,
        "monthly_return_rows": _optional_int(diagnostic_metrics.get("monthly_return_rows")) or 0,
        "average_correlation": _optional_float(diagnostic_metrics.get("average_correlation")),
        "max_correlation": _optional_float(diagnostic_metrics.get("max_correlation")),
        "max_risk_contribution": _optional_float(diagnostic_metrics.get("max_risk_contribution")),
    }
    return {
        "schema_version": RISK_CONTRIBUTION_AUDIT_SCHEMA_VERSION,
        "route": route,
        "route_label": RISK_CONTRIBUTION_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("RISK_CONTRIBUTION_", ""),
        "conclusion": conclusion,
        "next_action": next_action,
        "source_strength": source_strength,
        "rows": rows,
        "metrics": metrics,
        "component_rows": list(diagnostic.get("evidence_rows") or []),
        "limitations": [
            "V1 risk contribution은 component weight x monthly volatility 기반 proxy입니다.",
            "Full covariance / marginal contribution matrix는 계산하거나 workflow artifact로 저장하지 않습니다.",
            "DB price proxy 또는 mixed source matrix는 실제 strategy path와 다를 수 있어 REVIEW로 남깁니다.",
            "11-3은 gate-ready contract만 만들며 selected-route gate policy enforcement는 11-5에서 처리합니다.",
        ],
        "execution_boundary": {
            "write_policy": "read_only_risk_contribution_audit",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "raw_matrix_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "RISK_CONTRIBUTION_AUDIT_SCHEMA_VERSION",
    "RISK_CONTRIBUTION_READY",
    "RISK_CONTRIBUTION_REVIEW",
    "RISK_CONTRIBUTION_NEEDS_INPUT",
    "RISK_CONTRIBUTION_BLOCKED",
    "build_risk_contribution_audit",
]
