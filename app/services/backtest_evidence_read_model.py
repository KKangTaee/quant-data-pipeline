from __future__ import annotations

from typing import Any


SELECT_FOR_PRACTICAL_PORTFOLIO = "SELECT_FOR_PRACTICAL_PORTFOLIO"

FINAL_REVIEW_DECISION_LABELS = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "실전 검토 통과 후보",
    "HOLD_FOR_MORE_PAPER_TRACKING": "내용 부족 / 관찰 필요",
    "REJECT_FOR_PRACTICAL_USE": "투자하면 안 됨",
    "RE_REVIEW_REQUIRED": "재검토 필요",
}
FINAL_REVIEW_STATUS_DISPLAY = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: {
        "route": "FINAL_REVIEW_DECISION_COMPLETE",
        "verdict": "최종 판단 완료: 실전 검토 통과 후보로 선정됨",
        "next_action": "이 기록은 투자 후보 선정 판단입니다. 실제 투자 금액, 리밸런싱, 주문 승인 여부는 별도 운영 / 승인 단계에서 사용자가 결정합니다.",
    },
    "HOLD_FOR_MORE_PAPER_TRACKING": {
        "route": "FINAL_REVIEW_HOLD_FOR_MORE_OBSERVATION",
        "verdict": "최종 판단 보류: 내용 부족 / 추가 관찰 필요",
        "next_action": "추가 paper observation이나 근거 보강 후 Final Review에서 다시 판단합니다.",
    },
    "REJECT_FOR_PRACTICAL_USE": {
        "route": "FINAL_REVIEW_REJECTED",
        "verdict": "최종 판단 완료: 실전 후보에서 제외됨",
        "next_action": "필요하면 후보 탐색, Compare, Portfolio Proposal 단계로 되돌아갑니다.",
    },
    "RE_REVIEW_REQUIRED": {
        "route": "FINAL_REVIEW_REVIEW_REQUIRED",
        "verdict": "최종 판단 재검토 필요: 구성 / 비중 / 검증 근거를 다시 확인",
        "next_action": "구성, 비중, validation, robustness, paper observation 근거를 보강한 뒤 Final Review에서 다시 판단합니다.",
    },
}


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _as_list(value: Any) -> list[Any]:
    if isinstance(value, list):
        return value
    if value in (None, ""):
        return []
    return [value]


def _ready_from_check(check: dict[str, Any]) -> bool:
    if "Ready" in check:
        return bool(check.get("Ready"))
    return bool(check.get("ready"))


def _find_check(checks: list[dict[str, Any]], criteria: str) -> dict[str, Any]:
    criteria_key = criteria.lower()
    for check in checks:
        check_row = dict(check or {})
        label = _safe_text(check_row.get("Criteria") or check_row.get("criteria"), "").lower()
        if label == criteria_key:
            return check_row
    return {}


def _status_counts(validation: dict[str, Any]) -> dict[str, int]:
    summary = dict(validation.get("diagnostic_summary") or {})
    return dict(summary.get("status_counts") or {})


def _provider_status_summary(validation: dict[str, Any]) -> str:
    provider_context = dict(validation.get("provider_coverage") or {})
    coverage = dict(provider_context.get("coverage") or {})
    statuses = sorted(
        {
            _safe_text(dict(item or {}).get("diagnostic_status"), "")
            for item in coverage.values()
            if isinstance(item, dict)
        }
    )
    return ", ".join([status for status in statuses if status]) or "-"


def _critical_gap_rows(
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
) -> list[dict[str, Any]]:
    gaps: list[dict[str, Any]] = []
    for blocker in _as_list(validation.get("hard_blockers")):
        gaps.append(
            {
                "Area": "Hard blocker",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "Backtest Analysis 또는 Practical Validation에서 blocker를 먼저 해소합니다.",
            }
        )
    for item in _as_list(validation.get("not_run_critical_domains")):
        item_row = dict(item or {})
        gaps.append(
            {
                "Area": _safe_text(item_row.get("title") or item_row.get("domain"), "Critical NOT_RUN"),
                "Gap": "중요 진단이 실행되지 않았습니다.",
                "Severity": "BLOCK",
                "Required Action": _safe_text(item_row.get("next_action"), "데이터 / replay / benchmark 근거를 보강합니다."),
            }
        )
    for gap in _as_list(validation.get("paper_tracking_gaps")):
        gaps.append(
            {
                "Area": "Observation gap",
                "Gap": _safe_text(gap),
                "Severity": "REVIEW",
                "Required Action": "Final Review에서 보류 / 재검토 사유로 확인합니다.",
            }
        )
    for blocker in _as_list(paper_observation.get("blockers")):
        gaps.append(
            {
                "Area": "Paper observation",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "관찰 benchmark / component / weight 기준을 보강합니다.",
            }
        )
    for blocker in _as_list(decision_evidence.get("blockers")):
        gaps.append(
            {
                "Area": "Decision evidence",
                "Gap": _safe_text(blocker),
                "Severity": "BLOCK",
                "Required Action": "Final Review evidence route를 먼저 통과 가능한 상태로 만듭니다.",
            }
        )
    return gaps


def _assumption_rows(validation: dict[str, Any]) -> list[dict[str, Any]]:
    curve_evidence = dict(validation.get("curve_evidence") or {})
    status_counts = _status_counts(validation)
    rows = [
        {
            "Assumption": "Hypothetical backtest",
            "Current": "applies",
            "Meaning": "백테스트와 재검증 결과는 미래 수익을 보장하지 않습니다.",
        },
        {
            "Assumption": "No live approval / order",
            "Current": "disabled",
            "Meaning": "Final Review는 투자 승인, 주문 지시, 자동 리밸런싱이 아닙니다.",
        },
        {
            "Assumption": "Compact evidence only",
            "Current": "JSONL stores summary evidence",
            "Meaning": "full holdings / macro / provider raw row는 DB 영역에 두고 판단 row에는 compact 근거만 남깁니다.",
        },
        {
            "Assumption": "Current provider snapshots",
            "Current": _provider_status_summary(validation),
            "Meaning": "ETF provider snapshot은 validation 기준 current evidence이며 과거 특정 시점의 완전한 PIT truth가 아닐 수 있습니다.",
        },
        {
            "Assumption": "Macro vintage",
            "Current": "ALFRED vintage not implemented",
            "Meaning": "macro context는 observation 기준이며 revision vintage까지 보장하지 않습니다.",
        },
        {
            "Assumption": "Cost / slippage limits",
            "Current": curve_evidence.get("portfolio_curve_source") or "source dependent",
            "Meaning": "비용, slippage, 세금, 계좌 제약은 제한적으로만 반영됐을 수 있습니다.",
        },
    ]
    if int(status_counts.get("NOT_RUN", 0) or 0) > 0:
        rows.append(
            {
                "Assumption": "Missing diagnostics",
                "Current": f"{status_counts.get('NOT_RUN', 0)} NOT_RUN",
                "Meaning": "실행되지 않은 진단은 통과가 아니라 판단 전 확인해야 하는 공백입니다.",
            }
        )
    return rows


def build_investability_evidence_packet(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Build a compact Final Review decision packet without adding persistence."""

    source = dict(source or {})
    validation = dict(validation or {})
    paper_observation = dict(paper_observation or {})
    decision_evidence = dict(decision_evidence or {})
    validation_checks = [dict(row or {}) for row in _as_list(validation.get("checks")) if isinstance(row, dict)]
    benchmark_check = _find_check(validation_checks, "Benchmark parity")
    provider_check = _find_check(validation_checks, "Provider coverage")
    period_check = _find_check(validation_checks, "Runtime period coverage")
    runtime_check = _find_check(validation_checks, "Runtime recheck")
    status_counts = _status_counts(validation)
    robustness = dict(validation.get("robustness_validation") or {})
    critical_gaps = _critical_gap_rows(validation, paper_observation, decision_evidence)
    blocking_gaps = [gap for gap in critical_gaps if str(gap.get("Severity") or "") == "BLOCK"]
    assumptions = _assumption_rows(validation)
    source_chain = {
        "source_type": source.get("source_type") or validation.get("source_type"),
        "source_id": source.get("source_id") or validation.get("selection_source_id"),
        "selection_source_id": validation.get("selection_source_id"),
        "validation_id": validation.get("validation_id"),
        "decision_id": None,
        "monitoring_snapshot_id": None,
    }
    checks = [
        {
            "Section": "Source Chain",
            "Ready": bool(source_chain.get("source_id") or source_chain.get("selection_source_id")),
            "Current": source_chain.get("validation_id") or source_chain.get("selection_source_id") or "-",
            "Meaning": "Backtest source와 Practical Validation result가 이어지는지 확인합니다.",
        },
        {
            "Section": "Backtest Contract / Data Trust",
            "Ready": _ready_from_check(_find_check(validation_checks, "Data Trust")) if validation_checks else True,
            "Current": dict(_find_check(validation_checks, "Data Trust")).get("Current") or validation.get("validation_route") or "-",
            "Meaning": "원본 실행 결과의 데이터 품질과 차단 상태를 확인합니다.",
        },
        {
            "Section": "Runtime Replay",
            "Ready": _ready_from_check(runtime_check) and _ready_from_check(period_check) if runtime_check or period_check else False,
            "Current": f"{runtime_check.get('Current') or '-'} / {period_check.get('Current') or '-'}",
            "Meaning": "저장 snapshot이 아니라 runtime 재검증과 기간 coverage가 충분한지 봅니다.",
        },
        {
            "Section": "Provider / Look-through",
            "Ready": _ready_from_check(provider_check) if provider_check else False,
            "Current": provider_check.get("Current") or _provider_status_summary(validation),
            "Meaning": "ETF 운용성 / holdings / exposure / macro coverage가 검증에 연결됐는지 봅니다.",
        },
        {
            "Section": "Benchmark Parity",
            "Ready": _ready_from_check(benchmark_check) if benchmark_check else False,
            "Current": benchmark_check.get("Current") or "-",
            "Meaning": "후보와 benchmark가 같은 기간 / coverage / frequency로 비교되는지 봅니다.",
        },
        {
            "Section": "Robustness / Stress",
            "Ready": str(robustness.get("robustness_route") or "") == "READY_FOR_STRESS_SWEEP"
            or decision_evidence.get("route") == "READY_FOR_FINAL_DECISION",
            "Current": robustness.get("robustness_route") or decision_evidence.get("route") or "-",
            "Meaning": "stress / sensitivity / robustness 근거가 최종 선택에 충분한지 봅니다.",
        },
        {
            "Section": "Paper Observation",
            "Ready": not bool(paper_observation.get("blockers")),
            "Current": paper_observation.get("route") or "-",
            "Meaning": "선정 이후 관찰 benchmark와 trigger seed가 있는지 봅니다.",
        },
        {
            "Section": "Critical Gaps",
            "Ready": not blocking_gaps,
            "Current": str(len(blocking_gaps)),
            "Meaning": "critical NOT_RUN, hard blocker, evidence blocker가 선택을 막는지 봅니다.",
        },
        {
            "Section": "Execution Boundary",
            "Ready": True,
            "Current": "live approval disabled / order disabled",
            "Meaning": "이 packet은 투자 판단 보조 근거이며 주문이나 자동매매가 아닙니다.",
        },
    ]
    score = round(
        sum(1 for check in checks if bool(check.get("Ready"))) / len(checks) * 10.0,
        1,
    ) if checks else 0.0
    if blocking_gaps:
        route = "INVESTABILITY_PACKET_BLOCKED"
        verdict = "실전 후보 선정 차단: critical gap이 남아 있습니다."
        next_action = "선택 대신 보류 / 재검토로 기록하거나 validation evidence를 보강합니다."
    elif any(gap for gap in critical_gaps if str(gap.get("Severity") or "") == "REVIEW"):
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "실전 후보 선정 전 추가 검토가 필요합니다."
        next_action = "REVIEW gap을 최종 판단 사유와 monitoring 조건으로 확인합니다."
    elif decision_evidence.get("route") == "READY_FOR_FINAL_DECISION":
        route = "INVESTABILITY_PACKET_READY"
        verdict = "실전 검토 통과 후보로 기록 가능한 evidence packet입니다."
        next_action = "Final Review에서 선정 / 보류 / 거절 / 재검토 판단을 기록합니다."
    else:
        route = "INVESTABILITY_PACKET_NEEDS_REVIEW"
        verdict = "hard blocker는 없지만 Final Review evidence가 아직 완전하지 않습니다."
        next_action = "부족한 validation / robustness / observation 근거를 보강합니다."
    return {
        "schema_version": "investability_evidence_packet_v1",
        "route": route,
        "score": score,
        "select_ready": route == "INVESTABILITY_PACKET_READY",
        "verdict": verdict,
        "next_action": next_action,
        "source_chain": source_chain,
        "checks": checks,
        "critical_gaps": critical_gaps,
        "assumptions_and_limits": assumptions,
        "summary": {
            "pass": int(status_counts.get("PASS", 0) or 0),
            "review": int(status_counts.get("REVIEW", 0) or 0),
            "blocked": int(status_counts.get("BLOCKED", 0) or 0),
            "not_run": int(status_counts.get("NOT_RUN", 0) or 0),
            "provider_status": _provider_status_summary(validation),
            "decision_evidence_route": decision_evidence.get("route"),
            "robustness_route": robustness.get("robustness_route"),
        },
    }


def build_selected_route_gate(
    *,
    decision_route: str,
    investability_packet: dict[str, Any] | None,
) -> dict[str, Any]:
    """Return whether the selected route is allowed by the investability packet."""

    route = str(decision_route or "").strip()
    packet = dict(investability_packet or {})
    selected = route == SELECT_FOR_PRACTICAL_PORTFOLIO
    ready = (not selected) or bool(packet.get("select_ready"))
    current = packet.get("route") or "packet_not_attached"
    return {
        "Criteria": "Investability evidence packet",
        "Ready": ready,
        "Current": current,
        "Meaning": (
            "실전 검토 통과 후보 선정은 critical gap이 없는 evidence packet일 때만 저장합니다."
            if selected
            else "보류 / 거절 / 재검토 판단은 evidence gap이 있어도 기록할 수 있습니다."
        ),
    }


def build_final_review_status_display(row: dict[str, Any]) -> dict[str, str]:
    """Translate a saved final decision row into the current Final Review status copy."""

    decision_route = str(row.get("decision_route") or "").strip()
    status = dict(FINAL_REVIEW_STATUS_DISPLAY.get(decision_route) or {})
    if status:
        return status
    legacy_handoff = dict(row.get("phase35_handoff") or {})
    return {
        "route": str(legacy_handoff.get("handoff_route") or "FINAL_REVIEW_STATUS_UNKNOWN"),
        "verdict": "최종 판단 상태 확인 필요",
        "next_action": "decision route와 evidence를 확인한 뒤 Final Review에서 다시 판단합니다.",
    }


def build_final_review_decision_display_rows(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    """Flatten saved final decision records for a UI table without depending on Streamlit."""

    display_rows: list[dict[str, Any]] = []
    for row in rows:
        evidence = dict(row.get("decision_evidence_snapshot") or {})
        status_display = build_final_review_status_display(row)
        display_rows.append(
            {
                "Updated At": row.get("updated_at") or row.get("created_at"),
                "Decision ID": row.get("decision_id"),
                "Decision Route": row.get("decision_route"),
                "투자 가능성": FINAL_REVIEW_DECISION_LABELS.get(str(row.get("decision_route") or ""), "재검토 필요"),
                "Source": f"{row.get('source_type')} / {row.get('source_id')}",
                "Observation": row.get("source_observation_id") or row.get("source_paper_ledger_id") or "-",
                "Components": len(row.get("selected_components") or []),
                "Evidence Route": evidence.get("route"),
                "Evidence Score": evidence.get("score"),
                "Final Status": status_display.get("route"),
                "Live Approval": "Disabled",
            }
        )
    return display_rows


def _append_check_rows(
    display_rows: list[dict[str, Any]],
    *,
    area: str,
    checks: list[dict[str, Any]],
) -> None:
    for check in checks:
        check_row = dict(check or {})
        display_rows.append(
            {
                "Area": area,
                "Criteria": check_row.get("Criteria")
                or check_row.get("criteria")
                or check_row.get("Section")
                or "-",
                "Ready": check_row.get("Ready") if "Ready" in check_row else check_row.get("ready"),
                "Current": check_row.get("Current")
                or check_row.get("current")
                or check_row.get("current_value")
                or "-",
                "Meaning": check_row.get("Meaning") or check_row.get("meaning") or "-",
                "Score": check_row.get("Score") or check_row.get("score") or "-",
            }
        )


def build_final_decision_evidence_rows(row: dict[str, Any]) -> list[dict[str, Any]]:
    """Expand a final decision row into evidence check rows shared by review and dashboard views."""

    raw_decision = dict(row.get("raw_decision") or row)
    evidence = dict(raw_decision.get("decision_evidence_snapshot") or {})
    risk_snapshot = dict(raw_decision.get("risk_and_validation_snapshot") or {})
    robustness = dict(risk_snapshot.get("robustness_validation") or {})
    paper_snapshot = dict(raw_decision.get("paper_tracking_snapshot") or {})
    display_rows: list[dict[str, Any]] = []
    packet = dict(raw_decision.get("investability_evidence_packet") or {})
    _append_check_rows(display_rows, area="Final Review Evidence", checks=list(evidence.get("checks") or []))
    _append_check_rows(display_rows, area="Investability Packet", checks=list(packet.get("checks") or []))
    _append_check_rows(display_rows, area="Validation", checks=list(risk_snapshot.get("validation_checks") or []))
    _append_check_rows(display_rows, area="Robustness", checks=list(robustness.get("checks") or []))
    _append_check_rows(display_rows, area="Paper Observation", checks=list(paper_snapshot.get("checks") or []))
    return display_rows


__all__ = [
    "FINAL_REVIEW_DECISION_LABELS",
    "FINAL_REVIEW_STATUS_DISPLAY",
    "SELECT_FOR_PRACTICAL_PORTFOLIO",
    "build_investability_evidence_packet",
    "build_final_decision_evidence_rows",
    "build_final_review_decision_display_rows",
    "build_final_review_status_display",
    "build_selected_route_gate",
]
