from __future__ import annotations

from typing import Any


CONSTRUCTION_RISK_AUDIT_SCHEMA_VERSION = "construction_risk_audit_v1"

CONSTRUCTION_RISK_READY = "CONSTRUCTION_RISK_READY"
CONSTRUCTION_RISK_REVIEW = "CONSTRUCTION_RISK_REVIEW"
CONSTRUCTION_RISK_NEEDS_INPUT = "CONSTRUCTION_RISK_NEEDS_INPUT"
CONSTRUCTION_RISK_BLOCKED = "CONSTRUCTION_RISK_BLOCKED"

CONSTRUCTION_RISK_ROUTE_LABELS = {
    CONSTRUCTION_RISK_READY: "Ready",
    CONSTRUCTION_RISK_REVIEW: "Review Required",
    CONSTRUCTION_RISK_NEEDS_INPUT: "Evidence Input Needed",
    CONSTRUCTION_RISK_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}

_DEFAULT_MAX_COMPONENT_WEIGHT = 75.0
_DEFAULT_TOP_HOLDING_REVIEW = 25.0
_DEFAULT_TOP_OVERLAP_REVIEW = 20.0
_DEFAULT_DOMINANT_ASSET_REVIEW = 85.0
_FULL_COVERAGE_LINE = 99.99


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
        return CONSTRUCTION_RISK_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return CONSTRUCTION_RISK_NEEDS_INPUT
    if "REVIEW" in statuses:
        return CONSTRUCTION_RISK_REVIEW
    return CONSTRUCTION_RISK_READY


def _find_diagnostic(validation: dict[str, Any], domain: str) -> dict[str, Any]:
    for diagnostic in _as_list(validation.get("diagnostic_results")):
        row = dict(diagnostic or {})
        if str(row.get("domain") or "") == domain:
            return row
    return {}


def _provider_context(validation: dict[str, Any]) -> dict[str, Any]:
    context = dict(validation.get("provider_coverage") or {})
    if context:
        return context
    return dict(dict(validation.get("input_evidence") or {}).get("provider_coverage") or {})


def _look_through_board(validation: dict[str, Any]) -> dict[str, Any]:
    context = _provider_context(validation)
    board = dict(context.get("look_through_board") or {})
    if board:
        return board
    metrics = dict(validation.get("metrics") or {})
    compact = dict(metrics.get("provider_look_through") or {})
    if compact:
        return compact
    return {}


def _profile_threshold(validation: dict[str, Any], key: str, default: float) -> float:
    profile = dict(validation.get("validation_profile") or {})
    thresholds = dict(profile.get("thresholds") or {})
    return _optional_float(thresholds.get(key)) or default


def _source_strength(validation: dict[str, Any], board: dict[str, Any]) -> str:
    holdings = _optional_float(board.get("holdings_coverage_weight")) or 0.0
    exposure = _optional_float(board.get("exposure_coverage_weight")) or 0.0
    board_status = _status(board.get("status"), default="NEEDS_INPUT")
    has_proxy_diagnostic = bool(_find_diagnostic(validation, "concentration_overlap_exposure"))
    if holdings <= 0.0 and exposure <= 0.0:
        return "proxy_only" if has_proxy_diagnostic else "missing_provider"
    if holdings < _FULL_COVERAGE_LINE or exposure < _FULL_COVERAGE_LINE or board_status != "PASS":
        return "partial_provider"
    return "provider_backed"


def _component_weight_row(validation: dict[str, Any], diagnostic: dict[str, Any], source_strength: str) -> dict[str, Any]:
    metrics = dict(validation.get("metrics") or {})
    active_components = _optional_int(metrics.get("active_components")) or 0
    weight_total = _optional_float(metrics.get("weight_total")) or 0.0
    max_weight = _optional_float(metrics.get("max_weight")) or 0.0
    review_line = _profile_threshold(validation, "max_weight_review", _DEFAULT_MAX_COMPONENT_WEIGHT)
    if active_components <= 0:
        status = "BLOCKED"
        next_action = "Backtest Analysis에서 active component가 있는 source를 다시 선택합니다."
    elif abs(weight_total - 100.0) > 0.01:
        status = "BLOCKED"
        next_action = "target weight 합계를 100%로 맞춘 뒤 다시 검증합니다."
    elif max_weight > review_line:
        status = "REVIEW"
        next_action = "최대 component 비중이 profile 기준을 넘는 이유를 Final Review 근거에 남깁니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Component weight concentration",
        status=status,
        current=f"max {max_weight:.1f}% / total {weight_total:.1f}% / components {active_components}",
        evidence=diagnostic.get("summary") or f"review line {review_line:.1f}%",
        next_action=next_action,
        meaning="목표 비중 자체가 한 component에 과도하게 집중됐는지 확인합니다.",
        source_strength=source_strength,
    )


def _provider_coverage_row(board: dict[str, Any], source_strength: str) -> dict[str, Any]:
    holdings = _optional_float(board.get("holdings_coverage_weight")) or 0.0
    exposure = _optional_float(board.get("exposure_coverage_weight")) or 0.0
    board_status = _status(board.get("status"), default="NEEDS_INPUT")
    if holdings <= 0.0 and exposure <= 0.0:
        status = "NEEDS_INPUT"
        next_action = "ETF holdings / exposure provider snapshot을 DB에 수집한 뒤 다시 검증합니다."
    elif holdings <= 0.0 or exposure <= 0.0:
        status = "NEEDS_INPUT"
        next_action = "holdings와 exposure 중 누락된 provider snapshot을 보강합니다."
    elif holdings < _FULL_COVERAGE_LINE or exposure < _FULL_COVERAGE_LINE:
        status = "REVIEW"
        next_action = "partial coverage ETF가 construction risk 판단에 미치는 영향을 확인합니다."
    else:
        status = board_status
        next_action = "REVIEW 상태이면 freshness, source mix, missing ETF를 확인합니다." if status != "PASS" else "추가 조치 없음"
    return _row(
        criteria="Provider look-through coverage",
        status=status,
        current=f"holdings {holdings:.1f}% / exposure {exposure:.1f}%",
        evidence=board.get("summary") or board.get("status") or "look-through board missing",
        next_action=next_action,
        meaning="구성 리스크 판단이 ticker proxy가 아니라 DB provider holdings / exposure에 연결됐는지 봅니다.",
        source_strength=source_strength,
    )


def _top_holding_row(board: dict[str, Any], source_strength: str) -> dict[str, Any]:
    holdings = _optional_float(board.get("holdings_coverage_weight")) or 0.0
    top_weight = _optional_float(board.get("top_holding_weight")) or 0.0
    if holdings <= 0.0:
        status = "NEEDS_INPUT"
        next_action = "holdings snapshot을 수집해 단일 underlying holding 집중도를 확인합니다."
    elif holdings < _FULL_COVERAGE_LINE:
        status = "REVIEW"
        next_action = "partial holdings coverage에서는 top holding이 과소평가될 수 있습니다."
    elif top_weight > _DEFAULT_TOP_HOLDING_REVIEW:
        status = "REVIEW"
        next_action = "단일 underlying holding 집중이 포트폴리오 목적과 맞는지 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Top holding concentration",
        status=status,
        current=f"{top_weight:.1f}%",
        evidence=f"holdings coverage {holdings:.1f}% / review line {_DEFAULT_TOP_HOLDING_REVIEW:.1f}%",
        next_action=next_action,
        meaning="ETF 내부 단일 holding이 전체 포트폴리오에서 차지하는 최대 비중입니다.",
        source_strength=source_strength,
    )


def _holdings_overlap_row(board: dict[str, Any], source_strength: str) -> dict[str, Any]:
    holdings = _optional_float(board.get("holdings_coverage_weight")) or 0.0
    overlap_weight = _optional_float(board.get("top_overlap_weight")) or 0.0
    if holdings <= 0.0:
        status = "NEEDS_INPUT"
        next_action = "holdings snapshot을 수집해 ETF 간 중복 holding을 확인합니다."
    elif holdings < _FULL_COVERAGE_LINE:
        status = "REVIEW"
        next_action = "partial holdings coverage에서는 overlap이 과소평가될 수 있습니다."
    elif overlap_weight > _DEFAULT_TOP_OVERLAP_REVIEW:
        status = "REVIEW"
        next_action = "중복 holding이 의도한 diversification을 훼손하는지 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Holdings overlap",
        status=status,
        current=f"{overlap_weight:.1f}%",
        evidence=f"holdings coverage {holdings:.1f}% / review line {_DEFAULT_TOP_OVERLAP_REVIEW:.1f}%",
        next_action=next_action,
        meaning="여러 ETF에 중복 포함된 holding의 최대 portfolio weight입니다.",
        source_strength=source_strength,
    )


def _asset_bucket_row(board: dict[str, Any], source_strength: str) -> dict[str, Any]:
    exposure = _optional_float(board.get("exposure_coverage_weight")) or 0.0
    dominant_bucket = _safe_text(board.get("dominant_asset_bucket"))
    dominant_weight = _optional_float(board.get("dominant_asset_weight")) or 0.0
    unknown_weight = _optional_float(board.get("unknown_exposure_weight")) or 0.0
    if exposure <= 0.0:
        status = "NEEDS_INPUT"
        next_action = "exposure snapshot을 수집해 asset bucket look-through를 확인합니다."
    elif exposure < _FULL_COVERAGE_LINE:
        status = "REVIEW"
        next_action = "partial exposure coverage에서는 dominant asset과 unknown exposure를 보수적으로 봅니다."
    elif unknown_weight > 0.0:
        status = "REVIEW"
        next_action = "unknown exposure가 남아 있으면 asset bucket 판단을 보강합니다."
    elif dominant_weight > _DEFAULT_DOMINANT_ASSET_REVIEW:
        status = "REVIEW"
        next_action = "dominant asset bucket 집중이 profile과 맞는지 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Asset bucket exposure",
        status=status,
        current=f"{dominant_bucket} {dominant_weight:.1f}% / unknown {unknown_weight:.1f}%",
        evidence=f"exposure coverage {exposure:.1f}% / dominant review line {_DEFAULT_DOMINANT_ASSET_REVIEW:.1f}%",
        next_action=next_action,
        meaning="provider exposure 기준 가장 큰 자산군과 미분류 exposure가 포트폴리오를 지배하는지 확인합니다.",
        source_strength=source_strength,
    )


def _execution_boundary_row(source_strength: str) -> dict[str, Any]:
    return _row(
        criteria="Storage / execution boundary",
        status="PASS",
        current="read-only compact evidence",
        evidence="db_write=False / registry_write=False / live approval disabled",
        next_action="추가 조치 없음",
        meaning="이 audit은 raw holdings나 주문 정보를 저장하지 않는 검증 read model입니다.",
        source_strength=source_strength,
    )


def build_construction_risk_audit(validation: dict[str, Any]) -> dict[str, Any]:
    """Summarize concentration / overlap / exposure evidence without adding persistence."""

    validation = dict(validation or {})
    diagnostic = _find_diagnostic(validation, "concentration_overlap_exposure")
    board = _look_through_board(validation)
    source_strength = _source_strength(validation, board)
    rows = [
        _component_weight_row(validation, diagnostic, source_strength),
        _provider_coverage_row(board, source_strength),
        _top_holding_row(board, source_strength),
        _holdings_overlap_row(board, source_strength),
        _asset_bucket_row(board, source_strength),
        _execution_boundary_row(source_strength),
    ]
    route = _route_from_rows(rows)
    status_counts = {
        status: sum(1 for row in rows if row.get("Status") == status)
        for status in _STATUS_RANK
    }
    if route == CONSTRUCTION_RISK_READY:
        conclusion = "구성 리스크 audit 기준으로 즉시 보강이 필요한 concentration / overlap / exposure 공백이 없습니다."
        next_action = "Final Review에서 다른 gate와 operator 판단을 함께 확인합니다."
    elif route == CONSTRUCTION_RISK_BLOCKED:
        conclusion = "구성 리스크 audit에서 source 또는 target weight 차단 항목이 발견됐습니다."
        next_action = "component / target weight 계약을 먼저 복구합니다."
    elif route == CONSTRUCTION_RISK_NEEDS_INPUT:
        conclusion = "구성 리스크 판단을 위해 provider holdings / exposure evidence가 더 필요합니다."
        next_action = "ETF holdings / exposure provider snapshot을 우선 보강합니다."
    else:
        conclusion = "구성 리스크 근거는 일부 확인됐지만 concentration / overlap / exposure REVIEW 항목이 남아 있습니다."
        next_action = "REVIEW 항목을 Final Review 판단 사유에 명시하거나 provider evidence를 보강합니다."

    holdings_coverage = _optional_float(board.get("holdings_coverage_weight")) or 0.0
    exposure_coverage = _optional_float(board.get("exposure_coverage_weight")) or 0.0
    metrics = {
        "ready_rows": status_counts["PASS"],
        "total_rows": len(rows),
        "pass": status_counts["PASS"],
        "review": status_counts["REVIEW"],
        "needs_input": status_counts["NEEDS_INPUT"],
        "blocked": status_counts["BLOCKED"],
        "source_strength": source_strength,
        "max_component_weight": _optional_float(dict(validation.get("metrics") or {}).get("max_weight")) or 0.0,
        "target_weight_total": _optional_float(dict(validation.get("metrics") or {}).get("weight_total")) or 0.0,
        "active_components": _optional_int(dict(validation.get("metrics") or {}).get("active_components")) or 0,
        "holdings_coverage_weight": round(holdings_coverage, 4),
        "exposure_coverage_weight": round(exposure_coverage, 4),
        "top_holding_weight": round(_optional_float(board.get("top_holding_weight")) or 0.0, 4),
        "top_overlap_weight": round(_optional_float(board.get("top_overlap_weight")) or 0.0, 4),
        "dominant_asset_bucket": board.get("dominant_asset_bucket") or "-",
        "dominant_asset_weight": round(_optional_float(board.get("dominant_asset_weight")) or 0.0, 4),
        "unknown_exposure_weight": round(_optional_float(board.get("unknown_exposure_weight")) or 0.0, 4),
    }
    return {
        "schema_version": CONSTRUCTION_RISK_AUDIT_SCHEMA_VERSION,
        "route": route,
        "route_label": CONSTRUCTION_RISK_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("CONSTRUCTION_RISK_", ""),
        "conclusion": conclusion,
        "next_action": next_action,
        "source_strength": source_strength,
        "rows": rows,
        "metrics": metrics,
        "limitations": [
            "V1은 provider holdings / exposure의 compact look-through board를 읽습니다.",
            "ETF-of-ETF 2차 underlying expansion, issuer grouping, sector grouping은 후속 작업입니다.",
            "Full holdings row와 raw provider response는 DB boundary에 두고 workflow payload에는 저장하지 않습니다.",
            "11-2는 gate-ready contract만 만들며 selected-route gate policy enforcement는 11-5에서 처리합니다.",
        ],
        "execution_boundary": {
            "write_policy": "read_only_construction_risk_audit",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "CONSTRUCTION_RISK_AUDIT_SCHEMA_VERSION",
    "CONSTRUCTION_RISK_READY",
    "CONSTRUCTION_RISK_REVIEW",
    "CONSTRUCTION_RISK_NEEDS_INPUT",
    "CONSTRUCTION_RISK_BLOCKED",
    "build_construction_risk_audit",
]
