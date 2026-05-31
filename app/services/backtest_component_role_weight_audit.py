from __future__ import annotations

from typing import Any


COMPONENT_ROLE_WEIGHT_AUDIT_SCHEMA_VERSION = "component_role_weight_audit_v1"

COMPONENT_ROLE_WEIGHT_READY = "COMPONENT_ROLE_WEIGHT_READY"
COMPONENT_ROLE_WEIGHT_REVIEW = "COMPONENT_ROLE_WEIGHT_REVIEW"
COMPONENT_ROLE_WEIGHT_NEEDS_INPUT = "COMPONENT_ROLE_WEIGHT_NEEDS_INPUT"
COMPONENT_ROLE_WEIGHT_BLOCKED = "COMPONENT_ROLE_WEIGHT_BLOCKED"

COMPONENT_ROLE_WEIGHT_ROUTE_LABELS = {
    COMPONENT_ROLE_WEIGHT_READY: "Ready",
    COMPONENT_ROLE_WEIGHT_REVIEW: "Review Required",
    COMPONENT_ROLE_WEIGHT_NEEDS_INPUT: "Evidence Input Needed",
    COMPONENT_ROLE_WEIGHT_BLOCKED: "Blocked",
}

_STATUS_RANK = {
    "PASS": 0,
    "REVIEW": 1,
    "NEEDS_INPUT": 2,
    "BLOCKED": 3,
}

_FULL_COVERAGE_LINE = 99.99
_DEFAULT_MAX_COMPONENT_WEIGHT = 75.0
_DEFAULT_ROLE_CONCENTRATION_REVIEW = 85.0


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
        return COMPONENT_ROLE_WEIGHT_BLOCKED
    if "NEEDS_INPUT" in statuses:
        return COMPONENT_ROLE_WEIGHT_NEEDS_INPUT
    if "REVIEW" in statuses:
        return COMPONENT_ROLE_WEIGHT_REVIEW
    return COMPONENT_ROLE_WEIGHT_READY


def _profile_threshold(validation: dict[str, Any], key: str, default: float) -> float:
    profile = dict(validation.get("validation_profile") or {})
    thresholds = dict(profile.get("thresholds") or {})
    return _optional_float(thresholds.get(key)) or default


def _active_components(validation: dict[str, Any]) -> list[dict[str, Any]]:
    source = dict(validation.get("selection_source_snapshot") or {})
    components = [dict(component or {}) for component in _as_list(source.get("components")) if isinstance(component, dict)]
    if not components:
        paper = dict(validation.get("paper_observation") or {})
        components = [
            dict(component or {})
            for component in _as_list(paper.get("active_components"))
            if isinstance(component, dict)
        ]
    if not components:
        components = [
            {
                "title": row.get("Component"),
                "proposal_role": row.get("Role"),
                "target_weight": row.get("Weight"),
                "strategy_name": row.get("Strategy"),
                "registry_id": row.get("Registry ID"),
            }
            for row in _as_list(validation.get("component_rows"))
            if isinstance(row, dict)
        ]
    return [
        component
        for component in components
        if (_optional_float(component.get("target_weight") or component.get("Weight")) or 0.0) > 0.0
    ]


def _component_weight(component: dict[str, Any]) -> float:
    return _optional_float(component.get("target_weight") or component.get("Weight")) or 0.0


def _component_title(component: dict[str, Any]) -> str:
    return _safe_text(
        component.get("title")
        or component.get("strategy_name")
        or component.get("Component")
        or component.get("component_id"),
    )


def _explicit_role(component: dict[str, Any]) -> tuple[str, str]:
    for key in ("proposal_role", "component_role", "portfolio_role", "Role", "role"):
        role = str(component.get(key) or "").strip()
        if role and role != "-":
            return role, key
    return "", "missing"


def _weight_reason(component: dict[str, Any]) -> str:
    return str(component.get("weight_reason") or component.get("Weight Reason") or "").strip()


def _normalize_role_category(role: str, component: dict[str, Any]) -> str:
    text = " ".join(
        [
            str(role or ""),
            str(component.get("strategy_name") or ""),
            str(component.get("strategy_family") or ""),
            str(component.get("title") or ""),
        ]
    ).strip().lower()
    if not text:
        return "unknown"
    if any(term in text for term in ("hedge", "tactical", "trend", "momentum", "gtaa", "relative")):
        return "tactical_hedge"
    if any(term in text for term in ("defensive", "defense", "bond", "cash", "treasury", "gold", "risk parity", "risk_parity")):
        return "defensive"
    if any(term in text for term in ("diversifier", "diversification", "satellite", "alternative")):
        return "diversifier"
    if any(term in text for term in ("growth", "aggressive", "equity", "sector", "theme", "qqq")):
        return "growth"
    if any(term in text for term in ("core", "anchor")):
        return "core"
    return "unknown"


def _component_audit_rows(components: list[dict[str, Any]]) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    for component in components:
        role, role_source = _explicit_role(component)
        rows.append(
            {
                "Component": _component_title(component),
                "Weight": _component_weight(component),
                "Role": role or "-",
                "Role Category": _normalize_role_category(role, component),
                "Role Source": role_source,
                "Weight Reason": _weight_reason(component) or "-",
                "Strategy": component.get("strategy_name") or component.get("strategy_key") or "-",
                "Registry ID": component.get("registry_id") or "-",
            }
        )
    return rows


def _source_strength(components: list[dict[str, Any]]) -> str:
    if not components:
        return "missing_components"
    explicit_weight = sum(_component_weight(component) for component in components if _explicit_role(component)[0])
    if explicit_weight >= _FULL_COVERAGE_LINE:
        return "explicit_role_metadata"
    if explicit_weight > 0.0:
        return "partial_role_metadata"
    if len(components) == 1:
        return "single_component_no_role"
    return "missing_role_metadata"


def _role_weights(component_rows: list[dict[str, Any]]) -> dict[str, float]:
    weights: dict[str, float] = {}
    for row in component_rows:
        category = str(row.get("Role Category") or "unknown")
        weights[category] = round(weights.get(category, 0.0) + (_optional_float(row.get("Weight")) or 0.0), 4)
    return weights


def _role_review_line(validation: dict[str, Any]) -> float:
    profile = dict(validation.get("validation_profile") or {})
    profile_id = str(profile.get("profile_id") or "balanced_core")
    answers = dict(profile.get("answers") or {})
    primary_goal = str(answers.get("primary_goal") or "").strip()
    if profile_id == "growth_aggressive" or primary_goal in {"growth", "aggressive"}:
        return 95.0
    if profile_id in {"conservative_defensive", "hedged_tactical"} or primary_goal in {"defensive", "hedged_tactical"}:
        return 80.0
    return _DEFAULT_ROLE_CONCENTRATION_REVIEW


def _required_profile_categories(validation: dict[str, Any]) -> tuple[set[str], str]:
    profile = dict(validation.get("validation_profile") or {})
    profile_id = str(profile.get("profile_id") or "balanced_core")
    answers = dict(profile.get("answers") or {})
    primary_goal = str(answers.get("primary_goal") or "").strip()
    if profile_id == "hedged_tactical" or primary_goal == "hedged_tactical":
        return {"tactical_hedge", "defensive", "diversifier"}, "hedged / tactical profile needs hedge, defensive, or diversifier role evidence"
    if profile_id == "conservative_defensive" or primary_goal == "defensive":
        return {"defensive", "diversifier", "tactical_hedge"}, "defensive profile needs defensive or diversifying role evidence"
    if profile_id == "growth_aggressive" or primary_goal in {"growth", "aggressive"}:
        return {"growth", "core", "tactical_hedge"}, "growth profile needs growth, core, or tactical role evidence"
    return set(), "balanced profile has no mandatory role category"


def _role_source_row(
    *,
    components: list[dict[str, Any]],
    component_rows: list[dict[str, Any]],
    source_strength: str,
) -> dict[str, Any]:
    explicit_weight = sum(
        _optional_float(row.get("Weight")) or 0.0
        for row in component_rows
        if str(row.get("Role Source") or "") != "missing"
    )
    if not components:
        status = "BLOCKED"
        next_action = "Backtest Analysis에서 active component가 있는 source를 다시 선택합니다."
    elif explicit_weight >= _FULL_COVERAGE_LINE:
        status = "PASS"
        next_action = "추가 조치 없음"
    elif explicit_weight > 0.0:
        status = "NEEDS_INPUT"
        next_action = "role이 누락된 component의 proposal role source를 보강합니다."
    elif len(components) == 1:
        status = "REVIEW"
        next_action = "단일 component 후보는 core 역할로 볼 수 있는지 Final Review에서 명시 확인합니다."
    else:
        status = "NEEDS_INPUT"
        next_action = "component별 proposal role source를 보강합니다."
    return _row(
        criteria="Component role source coverage",
        status=status,
        current=f"explicit role weight {explicit_weight:.1f}% / components {len(components)}",
        evidence=source_strength,
        next_action=next_action,
        meaning="component 역할이 사용자가 저장한 메모가 아니라 selection source의 명시 role metadata에서 왔는지 확인합니다.",
        source_strength=source_strength,
    )


def _weight_discipline_row(
    *,
    validation: dict[str, Any],
    components: list[dict[str, Any]],
    source_strength: str,
) -> dict[str, Any]:
    weight_total = round(sum(_component_weight(component) for component in components), 4)
    max_weight = max((_component_weight(component) for component in components), default=0.0)
    review_line = _profile_threshold(validation, "max_weight_review", _DEFAULT_MAX_COMPONENT_WEIGHT)
    if not components:
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
        criteria="Profile-aware weight discipline",
        status=status,
        current=f"max {max_weight:.1f}% / total {weight_total:.1f}%",
        evidence=f"max weight review line {review_line:.1f}%",
        next_action=next_action,
        meaning="component 목표 비중이 validation profile의 최대 비중 기준을 넘는지 확인합니다.",
        source_strength=source_strength,
    )


def _role_concentration_row(
    *,
    role_weights: dict[str, float],
    source_strength: str,
    review_line: float,
) -> dict[str, Any]:
    unknown_weight = role_weights.get("unknown", 0.0)
    known_weights = {role: weight for role, weight in role_weights.items() if role != "unknown"}
    dominant_role, dominant_weight = max(known_weights.items(), key=lambda item: item[1], default=("-", 0.0))
    if unknown_weight >= _FULL_COVERAGE_LINE:
        status = "NEEDS_INPUT" if source_strength != "single_component_no_role" else "REVIEW"
        next_action = "role metadata가 없어 role concentration을 판단할 수 없습니다."
        current = f"unknown {unknown_weight:.1f}%"
    elif unknown_weight > 0.0:
        status = "NEEDS_INPUT"
        next_action = "role이 누락된 component를 보강한 뒤 role concentration을 다시 확인합니다."
        current = f"{dominant_role} {dominant_weight:.1f}% / unknown {unknown_weight:.1f}%"
    elif dominant_weight > review_line:
        status = "REVIEW"
        next_action = "특정 role에 비중이 몰린 이유와 대체 component 필요성을 확인합니다."
        current = f"{dominant_role} {dominant_weight:.1f}%"
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
        current = f"{dominant_role} {dominant_weight:.1f}%"
    return _row(
        criteria="Role concentration discipline",
        status=status,
        current=current,
        evidence=f"role review line {review_line:.1f}%",
        next_action=next_action,
        meaning="component 비중이 특정 portfolio role에 과도하게 몰리는지 확인합니다.",
        source_strength=source_strength,
    )


def _profile_intent_row(
    *,
    validation: dict[str, Any],
    role_weights: dict[str, float],
    source_strength: str,
) -> dict[str, Any]:
    required_categories, requirement = _required_profile_categories(validation)
    unknown_weight = role_weights.get("unknown", 0.0)
    matched_weight = sum(role_weights.get(category, 0.0) for category in required_categories)
    if unknown_weight >= _FULL_COVERAGE_LINE:
        status = "NEEDS_INPUT" if source_strength != "single_component_no_role" else "REVIEW"
        next_action = "profile 목적과 맞는 component role source를 보강합니다."
    elif required_categories and matched_weight <= 0.0:
        status = "REVIEW"
        next_action = "profile 목적과 맞는 hedge / defensive / growth role이 있는지 확인합니다."
    else:
        status = "PASS"
        next_action = "추가 조치 없음"
    return _row(
        criteria="Profile intent role fit",
        status=status,
        current=f"matched role weight {matched_weight:.1f}% / unknown {unknown_weight:.1f}%",
        evidence=requirement,
        next_action=next_action,
        meaning="validation profile 목적과 component role 구성이 충돌하지 않는지 확인합니다.",
        source_strength=source_strength,
    )


def _weight_rationale_row(
    *,
    components: list[dict[str, Any]],
    component_rows: list[dict[str, Any]],
    source_strength: str,
) -> dict[str, Any]:
    rationale_weight = sum(
        _optional_float(row.get("Weight")) or 0.0
        for row in component_rows
        if str(row.get("Weight Reason") or "").strip() not in {"", "-"}
    )
    if not components:
        status = "BLOCKED"
        next_action = "Backtest Analysis에서 active component가 있는 source를 다시 선택합니다."
    elif rationale_weight >= _FULL_COVERAGE_LINE:
        status = "PASS"
        next_action = "추가 조치 없음"
    elif rationale_weight > 0.0:
        status = "REVIEW"
        next_action = "weight reason이 없는 component의 비중 근거를 source 단계에서 확인합니다."
    elif len(components) == 1:
        status = "REVIEW"
        next_action = "단일 component 100% 비중이 전략 목적과 맞는지 Final Review에서 확인합니다."
    else:
        status = "NEEDS_INPUT"
        next_action = "multi-component source에는 compact weight reason을 보강합니다."
    return _row(
        criteria="Weight rationale coverage",
        status=status,
        current=f"rationale weight {rationale_weight:.1f}%",
        evidence="existing component weight_reason only; no memo persistence",
        next_action=next_action,
        meaning="비중 근거가 별도 사용자 메모 저장이 아니라 기존 component source metadata로 확인되는지 봅니다.",
        source_strength=source_strength,
    )


def _execution_boundary_row(source_strength: str) -> dict[str, Any]:
    return _row(
        criteria="Storage / execution boundary",
        status="PASS",
        current="read-only compact evidence",
        evidence="role preset storage disabled / memo_persistence=False / live approval disabled",
        next_action="추가 조치 없음",
        meaning="이 audit은 역할 preset, 사용자 메모, 주문, 자동 리밸런싱을 만들지 않는 검증 read model입니다.",
        source_strength=source_strength,
    )


def build_component_role_weight_audit(validation: dict[str, Any]) -> dict[str, Any]:
    """Summarize component role and weight discipline without creating role presets."""

    validation = dict(validation or {})
    components = _active_components(validation)
    component_rows = _component_audit_rows(components)
    source_strength = _source_strength(components)
    role_weights = _role_weights(component_rows)
    role_review_line = _role_review_line(validation)
    rows = [
        _role_source_row(components=components, component_rows=component_rows, source_strength=source_strength),
        _weight_discipline_row(validation=validation, components=components, source_strength=source_strength),
        _role_concentration_row(
            role_weights=role_weights,
            source_strength=source_strength,
            review_line=role_review_line,
        ),
        _profile_intent_row(validation=validation, role_weights=role_weights, source_strength=source_strength),
        _weight_rationale_row(components=components, component_rows=component_rows, source_strength=source_strength),
        _execution_boundary_row(source_strength),
    ]
    route = _route_from_rows(rows)
    status_counts = {
        status: sum(1 for row in rows if row.get("Status") == status)
        for status in _STATUS_RANK
    }
    if route == COMPONENT_ROLE_WEIGHT_READY:
        conclusion = "Component role / weight discipline 기준으로 즉시 보강이 필요한 역할 / 비중 공백이 없습니다."
        next_action = "Final Review에서 role fit과 construction risk를 함께 확인합니다."
    elif route == COMPONENT_ROLE_WEIGHT_BLOCKED:
        conclusion = "Component role / weight audit에서 source 차단 항목이 발견됐습니다."
        next_action = "active component 또는 target weight total을 복구한 뒤 다시 검증합니다."
    elif route == COMPONENT_ROLE_WEIGHT_NEEDS_INPUT:
        conclusion = "역할 / 비중 discipline 판단을 위해 component role source 또는 weight rationale이 더 필요합니다."
        next_action = "proposal role과 compact weight reason을 source 단계에서 보강합니다."
    else:
        conclusion = "역할 / 비중 discipline 근거는 일부 확인됐지만 REVIEW 항목이 남아 있습니다."
        next_action = "REVIEW 항목을 Final Review 판단 사유에 명시하거나 component role evidence를 보강합니다."

    weight_total = round(sum(_component_weight(component) for component in components), 4)
    max_weight = max((_component_weight(component) for component in components), default=0.0)
    explicit_role_weight = sum(
        _optional_float(row.get("Weight")) or 0.0
        for row in component_rows
        if str(row.get("Role Source") or "") != "missing"
    )
    rationale_weight = sum(
        _optional_float(row.get("Weight")) or 0.0
        for row in component_rows
        if str(row.get("Weight Reason") or "").strip() not in {"", "-"}
    )
    known_role_weights = {role: weight for role, weight in role_weights.items() if role != "unknown"}
    dominant_role, dominant_role_weight = max(known_role_weights.items(), key=lambda item: item[1], default=("-", 0.0))
    metrics = {
        "ready_rows": status_counts["PASS"],
        "total_rows": len(rows),
        "pass": status_counts["PASS"],
        "review": status_counts["REVIEW"],
        "needs_input": status_counts["NEEDS_INPUT"],
        "blocked": status_counts["BLOCKED"],
        "source_strength": source_strength,
        "active_components": len(components),
        "weight_total": weight_total,
        "max_weight": max_weight,
        "max_weight_review_line": _profile_threshold(validation, "max_weight_review", _DEFAULT_MAX_COMPONENT_WEIGHT),
        "explicit_role_weight": round(explicit_role_weight, 4),
        "weight_rationale_coverage_weight": round(rationale_weight, 4),
        "role_weights": role_weights,
        "dominant_role": dominant_role,
        "dominant_role_weight": dominant_role_weight,
        "role_concentration_review_line": role_review_line,
    }
    return {
        "schema_version": COMPONENT_ROLE_WEIGHT_AUDIT_SCHEMA_VERSION,
        "route": route,
        "route_label": COMPONENT_ROLE_WEIGHT_ROUTE_LABELS.get(route, route),
        "overall_status": route.replace("COMPONENT_ROLE_WEIGHT_", ""),
        "conclusion": conclusion,
        "next_action": next_action,
        "source_strength": source_strength,
        "rows": rows,
        "metrics": metrics,
        "component_rows": component_rows,
        "limitations": [
            "V1은 existing component proposal_role / target_weight / weight_reason만 읽습니다.",
            "역할이 없을 때 새 role preset, user memo, saved setup을 만들지 않습니다.",
            "Profile intent fit은 REVIEW / NEEDS_INPUT evidence이며 selected-route enforcement는 11-5 scope입니다.",
        ],
        "execution_boundary": {
            "write_policy": "read_only_component_role_weight_audit",
            "db_write": False,
            "registry_write": False,
            "memo_persistence": False,
            "role_preset_persistence": False,
            "saved_setup_persistence": False,
            "live_approval": False,
            "order_instruction": False,
            "auto_rebalance": False,
        },
    }


__all__ = [
    "COMPONENT_ROLE_WEIGHT_AUDIT_SCHEMA_VERSION",
    "COMPONENT_ROLE_WEIGHT_READY",
    "COMPONENT_ROLE_WEIGHT_REVIEW",
    "COMPONENT_ROLE_WEIGHT_NEEDS_INPUT",
    "COMPONENT_ROLE_WEIGHT_BLOCKED",
    "build_component_role_weight_audit",
]
