from __future__ import annotations

from typing import Any


VALIDATION_EFFICACY_AUDIT_SCHEMA_VERSION = "validation_efficacy_audit_v1"

VALIDATION_EFFICACY_READY = "VALIDATION_EFFICACY_READY"
VALIDATION_EFFICACY_REVIEW = "VALIDATION_EFFICACY_REVIEW"
VALIDATION_EFFICACY_NEEDS_INPUT = "VALIDATION_EFFICACY_NEEDS_INPUT"
VALIDATION_EFFICACY_BLOCKED = "VALIDATION_EFFICACY_BLOCKED"

VALIDATION_EFFICACY_ROUTE_LABELS = {
    VALIDATION_EFFICACY_READY: "Ready",
    VALIDATION_EFFICACY_REVIEW: "Review Required",
    VALIDATION_EFFICACY_NEEDS_INPUT: "Evidence Input Needed",
    VALIDATION_EFFICACY_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    return list(value) if isinstance(value, list) else []


def _truthy(value: Any) -> bool:
    if isinstance(value, bool):
        return value
    return str(value or "").strip().lower() in {"1", "true", "yes", "y", "pass", "ready", "enabled"}


def _status(value: Any, *, default: str = "NEEDS_INPUT") -> str:
    text = str(value or "").strip().upper()
    if not text or text in {"-", "NONE", "NULL", "N/A", "UNKNOWN"}:
        return default
    if text in {"BLOCKED", "BLOCK", "ERROR", "FAILED", "FAIL"} or "ERROR" in text:
        return "BLOCKED"
    if text in {"NOT_RUN", "MISSING", "NO_DATA", "UNAVAILABLE"}:
        return "NEEDS_INPUT"
    if text in {"PASS", "OK", "READY", "SUCCESS", "FRESH", "COMPLETE", "COMPLETED"}:
        return "PASS"
    if text.startswith("READY_"):
        return "PASS"
    if text in {"REVIEW", "STALE", "PARTIAL", "WARNING", "WARN", "WATCH"} or "REVIEW" in text:
        return "REVIEW"
    return default


def _find_check(checks: list[dict[str, Any]], criteria: str) -> dict[str, Any]:
    expected = criteria.strip().lower()
    for check in checks:
        label = str(check.get("Criteria") or check.get("criteria") or check.get("Section") or "").strip().lower()
        if label == expected:
            return dict(check)
    return {}


def _ready(check: dict[str, Any]) -> bool:
    return _truthy(check.get("Ready") if "Ready" in check else check.get("ready"))


def _check_status(check: dict[str, Any], *, missing: str = "NEEDS_INPUT", false_status: str = "REVIEW") -> str:
    if not check:
        return missing
    current_status = _status(check.get("Current") or check.get("current"), default=false_status)
    if _ready(check):
        return "REVIEW" if current_status == "REVIEW" else "PASS"
    if current_status in {"BLOCKED", "NEEDS_INPUT"}:
        return current_status
    return false_status


def _row(
    *,
    criteria: str,
    status: str,
    current: Any,
    evidence: Any,
    next_action: str,
    meaning: str,
) -> dict[str, Any]:
    normalized = status if status in _STATUS_RANK else _status(status, default="REVIEW")
    return {
        "Criteria": criteria,
        "Status": normalized,
        "Ready": normalized == "PASS",
        "Current": _safe_text(current),
        "Evidence": _safe_text(evidence),
        "Next Action": next_action,
        "Meaning": meaning,
    }


def _source_contract_row(validation: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    source_check = _find_check(checks, "Selection source")
    component_check = _find_check(checks, "Active components")
    weight_check = _find_check(checks, "Target weight total")
    blockers = []
    if not _ready(source_check):
        blockers.append("source")
    if not _ready(component_check):
        blockers.append("components")
    if not _ready(weight_check):
        blockers.append("weights")
    status = "BLOCKED" if blockers else "PASS"
    current = (
        f"{source_check.get('Current') or validation.get('selection_source_id') or '-'} / "
        f"{component_check.get('Current') or '-'} components / "
        f"{weight_check.get('Current') or '-'}"
    )
    return _row(
        criteria="Backtest source contract",
        status=status,
        current=current,
        evidence="; ".join(blockers) if blockers else "source, components, weights attached",
        next_action="source / component / weight contract를 먼저 복구합니다." if blockers else "추가 조치 없음",
        meaning="Final Review로 넘길 후보 source와 비중 계약이 유효한지 확인합니다.",
    )


def _data_trust_row(checks: list[dict[str, Any]]) -> dict[str, Any]:
    check = _find_check(checks, "Data Trust")
    status = _check_status(check, missing="NEEDS_INPUT", false_status="BLOCKED")
    return _row(
        criteria="Data Trust boundary",
        status=status,
        current=check.get("Current") or "missing",
        evidence=check.get("Meaning") or "Data Trust check",
        next_action="Data Trust blocker / error를 해소합니다." if status == "BLOCKED" else "warning이 있으면 최종 판단 근거에 남깁니다.",
        meaning="원본 backtest의 데이터 품질 문제가 실전 후보 판단을 막는지 확인합니다.",
    )


def _runtime_replay_row(validation: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
    replay_attempt = dict(curve_evidence.get("replay_attempt") or {})
    check = _find_check(checks, "Runtime recheck")
    replay_status = (
        replay_attempt.get("status")
        or curve_provenance.get("runtime_recheck_status")
        or curve_provenance.get("actual_runtime_replay_status")
        or check.get("Current")
        or dict(validation.get("metrics") or {}).get("runtime_recheck_status")
    )
    status = _status(replay_status)
    if status == "PASS" and not (curve_evidence.get("portfolio_curve_rows") or curve_provenance.get("portfolio_curve_rows")):
        status = "NEEDS_INPUT"
    if status == "REVIEW" and _ready(check):
        status = "REVIEW"
    return _row(
        criteria="Runtime replay evidence",
        status=status,
        current=replay_status or "NOT_RUN",
        evidence=curve_provenance.get("runtime_recheck_id") or replay_attempt.get("replay_id") or "runtime replay id missing",
        next_action="최신 DB 기준 runtime replay를 실행합니다." if status == "NEEDS_INPUT" else "REVIEW 상태면 runtime 결과 차이를 확인합니다.",
        meaning="저장 snapshot만이 아니라 실제 runtime으로 다시 재현된 curve evidence가 있는지 봅니다.",
    )


def _period_coverage_row(validation: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    period_coverage = dict(curve_evidence.get("period_coverage") or {})
    curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
    check = _find_check(checks, "Runtime period coverage")
    current = period_coverage.get("status") or curve_provenance.get("period_coverage_status") or check.get("Current")
    status = _status(current)
    requested = dict(period_coverage.get("requested_period") or curve_provenance.get("requested_period") or {})
    actual = dict(period_coverage.get("actual_period") or curve_provenance.get("actual_period") or {})
    evidence = (
        f"actual {actual.get('start') or '-'}..{actual.get('end') or '-'} / "
        f"requested {requested.get('start') or '-'}..{requested.get('end') or '-'}"
    )
    return _row(
        criteria="Runtime period coverage",
        status=status,
        current=current or "NOT_RUN",
        evidence=evidence,
        next_action="요청 종료일까지 curve가 이어지는지 재검증합니다." if status != "PASS" else "추가 조치 없음",
        meaning="최신 검증 기간이 실제 portfolio curve에 충분히 반영됐는지 확인합니다.",
    )


def _benchmark_parity_row(validation: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    benchmark_parity = dict(curve_evidence.get("benchmark_parity") or {})
    check = _find_check(checks, "Benchmark parity")
    current = benchmark_parity.get("status") or check.get("Current")
    metrics = dict(benchmark_parity.get("metrics") or {})
    status = _status(current)
    evidence = (
        f"coverage={metrics.get('coverage_ratio', '-')} / "
        f"same_period={metrics.get('same_period', '-')} / "
        f"same_frequency={metrics.get('same_frequency', '-')}"
    )
    return _row(
        criteria="Benchmark parity",
        status=status,
        current=current or "NOT_RUN",
        evidence=evidence,
        next_action="같은 기간 / frequency / coverage의 benchmark curve를 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="후보 성과와 benchmark가 같은 조건에서 비교되는지 확인합니다.",
    )


def _provider_display_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    rows = [dict(row or {}) for row in _as_list(validation.get("provider_coverage_display_rows")) if isinstance(row, dict)]
    if rows:
        return rows
    provider_context = dict(validation.get("provider_coverage") or {})
    rows = [dict(row or {}) for row in _as_list(provider_context.get("display_rows")) if isinstance(row, dict)]
    if rows:
        return rows
    input_context = dict(dict(validation.get("input_evidence") or {}).get("provider_coverage") or {})
    return [dict(row or {}) for row in _as_list(input_context.get("display_rows")) if isinstance(row, dict)]


def _provider_coverage_row(validation: dict[str, Any], checks: list[dict[str, Any]]) -> dict[str, Any]:
    rows = _provider_display_rows(validation)
    statuses = [
        _status(row.get("Diagnostic Status") or row.get("Status") or row.get("Coverage"))
        for row in rows
    ]
    freshness = {str(row.get("Freshness") or "").strip().lower() for row in rows}
    if not rows:
        check = _find_check(checks, "Provider coverage")
        status = _check_status(check, missing="NEEDS_INPUT", false_status="NEEDS_INPUT")
        current = check.get("Current") or "NOT_RUN"
        evidence = "provider display rows missing"
    elif "BLOCKED" in statuses:
        status = "BLOCKED"
        current = ", ".join(sorted(set(statuses)))
        evidence = "provider error / blocked status"
    elif "NEEDS_INPUT" in statuses:
        status = "NEEDS_INPUT"
        current = ", ".join(sorted(set(statuses)))
        evidence = f"freshness={', '.join(sorted(item for item in freshness if item)) or '-'}"
    elif "REVIEW" in statuses or freshness.intersection({"stale", "unknown", "not_run"}):
        status = "REVIEW"
        current = ", ".join(sorted(set(statuses)))
        evidence = f"freshness={', '.join(sorted(item for item in freshness if item)) or '-'}"
    else:
        status = "PASS"
        current = ", ".join(sorted(set(statuses))) or "PASS"
        evidence = f"{len(rows)} provider areas"
    return _row(
        criteria="Provider / freshness evidence",
        status=status,
        current=current,
        evidence=evidence,
        next_action="provider / holdings / exposure / macro snapshot을 DB에 보강합니다." if status == "NEEDS_INPUT" else "stale / partial snapshot은 최종 판단 근거에 남깁니다.",
        meaning="검증 시점의 provider coverage와 freshness가 충분한지 확인합니다.",
    )


def _robustness_row(validation: dict[str, Any]) -> dict[str, Any]:
    robustness = dict(validation.get("robustness_validation") or {})
    board = dict(robustness.get("robustness_lab_board") or {})
    metrics_board = dict(dict(validation.get("metrics") or {}).get("robustness_lab") or {})
    board_status = board.get("status") or metrics_board.get("status")
    route = robustness.get("robustness_route")
    not_run_critical = [
        dict(row or {})
        for row in _as_list(validation.get("not_run_critical_domains"))
        if isinstance(row, dict)
    ]
    status = _status(board_status, default="REVIEW" if route else "NEEDS_INPUT")
    if any("stress" in str(row.get("domain") or "").lower() or "robustness" in str(row.get("domain") or "").lower() for row in not_run_critical):
        status = "NEEDS_INPUT"
    if status == "PASS":
        evidence = board.get("summary") or "robustness lab board PASS"
    else:
        evidence = board.get("summary") or route or "robustness lab board missing"
    return _row(
        criteria="Robustness / stress coverage",
        status=status,
        current=board_status or route or "NOT_RUN",
        evidence=evidence,
        next_action="stress / rolling / sensitivity evidence를 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="성과가 특정 기간이나 파라미터에만 의존하는지 확인할 근거가 있는지 봅니다.",
    )


def _pit_guard_row(validation: dict[str, Any]) -> dict[str, Any]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    curve_provenance = dict(curve_evidence.get("curve_provenance") or {})
    source = _safe_text(curve_evidence.get("portfolio_curve_source") or curve_provenance.get("portfolio_curve_source"), "unavailable")
    runtime_status = _status(curve_provenance.get("runtime_recheck_status") or dict(curve_evidence.get("replay_attempt") or {}).get("status"))
    period_status = _status(curve_provenance.get("period_coverage_status") or dict(curve_evidence.get("period_coverage") or {}).get("status"))
    source_lower = source.lower()
    if runtime_status == "BLOCKED" or period_status == "BLOCKED":
        status = "BLOCKED"
    elif runtime_status == "PASS" and period_status == "PASS" and "runtime" in source_lower:
        status = "PASS"
    elif runtime_status == "NEEDS_INPUT" or period_status == "NEEDS_INPUT":
        status = "NEEDS_INPUT"
    else:
        status = "REVIEW"
    if any(token in source_lower for token in ("embedded", "snapshot", "proxy", "stored")) and status == "PASS":
        status = "REVIEW"
    return _row(
        criteria="PIT / look-ahead guard",
        status=status,
        current=f"{source} / replay={runtime_status} / period={period_status}",
        evidence=curve_provenance.get("runtime_recheck_mode_label") or curve_provenance.get("runtime_recheck_mode") or "curve provenance",
        next_action="runtime replay와 기간 coverage를 보강해 look-ahead 위험을 낮춥니다." if status != "PASS" else "추가 조치 없음",
        meaning="최신 데이터로 재검증하면서도 미래 데이터를 섞어 보지 않는지 확인합니다.",
    )


def _nested_values_for_keys(value: Any, keys: set[str]) -> list[Any]:
    found: list[Any] = []
    if isinstance(value, dict):
        for key, child in value.items():
            if str(key or "").strip().lower() in keys:
                found.append(child)
            if isinstance(child, dict):
                found.extend(_nested_values_for_keys(child, keys))
    return found


def _survivorship_row(validation: dict[str, Any]) -> dict[str, Any]:
    keys = {
        "survivorship_control",
        "survivorship_bias_control",
        "survivorship_status",
        "historical_universe",
        "pit_universe",
        "universe_history",
        "listing_history",
    }
    values = _nested_values_for_keys(validation, keys)
    status = "REVIEW"
    evidence = "historical universe / delisting evidence not attached"
    for value in values:
        if isinstance(value, dict):
            candidate = value.get("status") or value.get("Current") or value.get("current") or value.get("mode")
        else:
            candidate = value
        candidate_text = str(candidate or "").strip().lower()
        if isinstance(value, bool) and value:
            status = "PASS"
            evidence = "explicit survivorship control flag"
            break
        if candidate_text in {"pass", "controlled", "historical", "pit", "point_in_time", "point-in-time"}:
            status = "PASS"
            evidence = _safe_text(candidate)
            break
        if candidate_text in {"blocked", "error", "fail", "failed"}:
            status = "BLOCKED"
            evidence = _safe_text(candidate)
            break
    return _row(
        criteria="Survivorship / universe guard",
        status=status,
        current=evidence,
        evidence="; ".join(_safe_text(value) for value in values[:3]) if values else evidence,
        next_action="historical universe / listing / delisting 기준을 별도 evidence로 보강합니다." if status != "PASS" else "추가 조치 없음",
        meaning="현재 살아있는 종목만으로 과거를 재구성하는 survivorship bias 위험을 확인합니다.",
    )


def _execution_boundary_row(validation: dict[str, Any]) -> dict[str, Any]:
    prohibited = {
        "live_approval": validation.get("live_approval"),
        "order_instruction": validation.get("order_instruction"),
        "auto_rebalance": validation.get("auto_rebalance"),
    }
    active = [name for name, value in prohibited.items() if _truthy(value)]
    status = "BLOCKED" if active else "PASS"
    return _row(
        criteria="Execution / storage boundary",
        status=status,
        current=" / ".join(active) if active else "read-only audit / writes disabled",
        evidence="db_write=False / registry_write=False / memo_persistence=False",
        next_action="주문 / 승인 / 자동 리밸런싱 경계를 제거합니다." if active else "추가 조치 없음",
        meaning="검증 효력 audit은 새 저장 기능이나 실거래 동작을 만들지 않는다는 경계입니다.",
    )


def _route_from_rows(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row.get("Status") or "") for row in rows}
    if "BLOCKED" in statuses:
        return VALIDATION_EFFICACY_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return VALIDATION_EFFICACY_NEEDS_INPUT
    if "REVIEW" in statuses:
        return VALIDATION_EFFICACY_REVIEW
    return VALIDATION_EFFICACY_READY


def build_validation_efficacy_audit(validation: dict[str, Any]) -> dict[str, Any]:
    """Summarize whether Practical Validation evidence is strong enough for final selection."""

    validation = dict(validation or {})
    checks = [dict(row or {}) for row in _as_list(validation.get("checks")) if isinstance(row, dict)]
    rows = [
        _source_contract_row(validation, checks),
        _data_trust_row(checks),
        _runtime_replay_row(validation, checks),
        _period_coverage_row(validation, checks),
        _benchmark_parity_row(validation, checks),
        _provider_coverage_row(validation, checks),
        _robustness_row(validation),
        _pit_guard_row(validation),
        _survivorship_row(validation),
        _execution_boundary_row(validation),
    ]
    route = _route_from_rows(rows)
    status_counts = {
        status: sum(1 for row in rows if row.get("Status") == status)
        for status in _STATUS_RANK
    }
    total = len(rows)
    ready = status_counts["PASS"]
    if route == VALIDATION_EFFICACY_READY:
        conclusion = "검증 효력 audit 기준으로 즉시 차단되는 공백이 없습니다."
        next_action = "Final Review에서 operator 판단과 gate policy를 함께 확인합니다."
    elif route == VALIDATION_EFFICACY_BLOCKED:
        conclusion = "검증 효력 audit에서 차단 항목이 발견됐습니다."
        next_action = "BLOCKED 항목을 먼저 해소한 뒤 Final Review 선택 판단을 진행합니다."
    elif route == VALIDATION_EFFICACY_NEEDS_INPUT:
        conclusion = "검증 효력을 판단하기 위해 추가 evidence가 필요합니다."
        next_action = "runtime replay, provider snapshot, benchmark parity, robustness evidence를 우선 보강합니다."
    else:
        conclusion = "검증 효력은 확인 가능하지만 REVIEW 항목이 남아 있습니다."
        next_action = "REVIEW 항목을 최종 판단 사유에 명시하거나 evidence를 보강합니다."
    return {
        "schema_version": VALIDATION_EFFICACY_AUDIT_SCHEMA_VERSION,
        "route": route,
        "route_label": VALIDATION_EFFICACY_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("VALIDATION_EFFICACY_", ""),
        "conclusion": conclusion,
        "next_action": next_action,
        "rows": rows,
        "metrics": {
            "ready_rows": ready,
            "total_rows": total,
            "pass": status_counts["PASS"],
            "review": status_counts["REVIEW"],
            "needs_input": status_counts["NEEDS_INPUT"],
            "blocked": status_counts["BLOCKED"],
            "not_run_diagnostics": int(
                dict(dict(validation.get("diagnostic_summary") or {}).get("status_counts") or {}).get("NOT_RUN", 0)
                or 0
            ),
        },
        "execution_boundary": {
            "write_policy": "read_only_validation_efficacy_audit",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "VALIDATION_EFFICACY_AUDIT_SCHEMA_VERSION",
    "VALIDATION_EFFICACY_READY",
    "VALIDATION_EFFICACY_REVIEW",
    "VALIDATION_EFFICACY_NEEDS_INPUT",
    "VALIDATION_EFFICACY_BLOCKED",
    "build_validation_efficacy_audit",
]
