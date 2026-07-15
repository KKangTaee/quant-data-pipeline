"""Build the Streamlit-free Final Review Decision Brief projection.

Python owns candidate eligibility, canonical decision routes, and save
capabilities.  Presentation clients receive a JSON-serializable projection and
must not infer or persist domain state themselves.
"""

from __future__ import annotations

from typing import Any


DECISION_BRIEF_SCHEMA_VERSION = "decision_brief_v1"

SELECT_FOR_PRACTICAL_PORTFOLIO = "SELECT_FOR_PRACTICAL_PORTFOLIO"
HOLD_FOR_MORE_PAPER_TRACKING = "HOLD_FOR_MORE_PAPER_TRACKING"
REJECT_FOR_PRACTICAL_USE = "REJECT_FOR_PRACTICAL_USE"
RE_REVIEW_REQUIRED = "RE_REVIEW_REQUIRED"

DECISION_BRIEF_ROUTE_PRESENTATION = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: "계속 추적",
    HOLD_FOR_MORE_PAPER_TRACKING: "관찰 후 재검토",
    REJECT_FOR_PRACTICAL_USE: "추적 대상에서 제외",
    RE_REVIEW_REQUIRED: "Level2로 돌려보내기",
}

_ROUTE_PRESENTATION = {
    SELECT_FOR_PRACTICAL_PORTFOLIO: {
        "tone": "positive",
        "headline": "계속 추적할 가치가 있는 후보입니다.",
        "button_label": "계속 추적으로 기록",
        "reason_placeholder": "어떤 관측값을 근거로 계속 추적할지 작성합니다.",
    },
    HOLD_FOR_MORE_PAPER_TRACKING: {
        "tone": "warning",
        "headline": "관찰을 더 이어간 뒤 다시 판단할 후보입니다.",
        "button_label": "관찰 후 재검토로 기록",
        "reason_placeholder": "추가로 관찰할 조건과 보류 이유를 작성합니다.",
    },
    REJECT_FOR_PRACTICAL_USE: {
        "tone": "danger",
        "headline": "현재 근거로는 추적 가치가 낮은 후보입니다.",
        "button_label": "추적 대상 제외로 기록",
        "reason_placeholder": "어떤 관측값 때문에 추적 대상에서 제외하는지 작성합니다.",
    },
    RE_REVIEW_REQUIRED: {
        "tone": "neutral",
        "headline": "Final Review 전에 Level2 근거를 다시 확인해야 합니다.",
        "button_label": "Level2 재검토로 기록",
        "reason_placeholder": "Level2에서 다시 확인할 근거와 이유를 작성합니다.",
    },
}

_TRAIT_AXES = (
    ("concentration_pressure", "집중 위험"),
    ("drawdown_pressure", "낙폭 압력"),
    ("turnover_burden", "회전 부담"),
    ("cost_burden", "비용 부담"),
    ("regime_dependency", "국면 의존"),
)


def _as_dict(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, dict) else {}


def _as_non_negative_int(value: Any) -> int:
    try:
        return max(0, int(value or 0))
    except (TypeError, ValueError):
        return 0


def _stable_ids(row: dict[str, Any]) -> tuple[str, ...]:
    return tuple(
        value
        for value in (
            str(row.get("observation_id") or "").strip(),
            str(row.get("root_issue_id") or "").strip(),
        )
        if value
    )


def _deduplicate_primary_roles(
    *,
    strengths: list[dict[str, Any]],
    weaknesses: list[dict[str, Any]],
    monitoring_conditions: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]], list[dict[str, Any]]]:
    """Assign one primary role to each observation/root, preferring triggers."""

    seen: set[str] = set()

    def keep(rows: list[dict[str, Any]], *, role: str) -> list[dict[str, Any]]:
        kept: list[dict[str, Any]] = []
        for raw_row in rows:
            row = dict(raw_row or {})
            stable_ids = _stable_ids(row)
            if not stable_ids or any(stable_id in seen for stable_id in stable_ids):
                continue
            row["primary_role"] = role
            kept.append(row)
            seen.update(stable_ids)
        return kept

    conditions = keep(monitoring_conditions, role="monitoring")
    weakness_rows = keep(weaknesses, role="weakness")
    strength_rows = keep(strengths, role="strength")
    return strength_rows, weakness_rows, conditions


def build_final_review_candidate_selector(
    candidates: list[dict[str, Any]],
    *,
    active_source_id: str | None,
) -> dict[str, Any]:
    """Project selectable candidates without exposing write/storage details."""

    requested_source_id = str(active_source_id or "").strip()
    selected_once = False
    options: list[dict[str, Any]] = []
    for candidate in candidates:
        row = _as_dict(candidate)
        source_id = str(row.get("source_id") or row.get("selection_source_id") or "").strip()
        selected = bool(requested_source_id and source_id == requested_source_id and not selected_once)
        selected_once = selected_once or selected
        options.append(
            {
                "source_id": source_id,
                "validation_id": str(row.get("validation_id") or "").strip(),
                "title": str(row.get("title") or row.get("source_title") or source_id or "후보"),
                "source_type": str(row.get("source_type") or "").strip(),
                "eligible": bool(row.get("eligible")),
                "selected": selected,
            }
        )
    return {
        "schema_version": "decision_brief_candidate_selector_v1",
        "options": options,
    }


def _pre_selection_unresolved_issues(validation: dict[str, Any]) -> list[dict[str, Any]]:
    closure = _as_dict(validation.get("evidence_closure"))
    unresolved: list[dict[str, Any]] = []
    for raw_issue in list(closure.get("issues") or []):
        issue = _as_dict(raw_issue)
        root_issue_id = str(issue.get("root_issue_id") or "").strip()
        if str(issue.get("terminal_state") or "").strip() != "open":
            continue
        if not (
            bool(issue.get("actionable_now"))
            or str(issue.get("criticality") or "").strip() == "critical"
            or root_issue_id.startswith("missing_contract:")
        ):
            continue
        unresolved.append(
            {
                "root_issue_id": root_issue_id,
                "title": str(issue.get("title") or root_issue_id or "선정 전 근거 종결 필요"),
            }
        )
    return unresolved


def _build_eligibility(
    *,
    validation: dict[str, Any],
    investability_packet: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]]]:
    closure = _as_dict(validation.get("evidence_closure"))
    summary = _as_dict(closure.get("summary"))
    gate = _as_dict(
        investability_packet.get("selection_gate_policy_snapshot")
        or investability_packet.get("gate_policy_snapshot")
    )
    unresolved_actionable_count = _as_non_negative_int(summary.get("unresolved_actionable_count"))
    critical_engineering_count = _as_non_negative_int(summary.get("critical_engineering_count"))
    missing_contract_count = _as_non_negative_int(summary.get("missing_contract_count"))
    unresolved_issues = _pre_selection_unresolved_issues(validation)
    pre_selection_unresolved_count = max(
        _as_non_negative_int(gate.get("pre_selection_unresolved_count")),
        len(unresolved_issues),
        unresolved_actionable_count + critical_engineering_count + missing_contract_count,
    )
    eligible = (
        bool(gate.get("select_allowed"))
        and unresolved_actionable_count == 0
        and critical_engineering_count == 0
        and missing_contract_count == 0
        and pre_selection_unresolved_count == 0
    )
    return (
        {
            "eligible": eligible,
            "unresolved_actionable_count": unresolved_actionable_count,
            "critical_engineering_count": critical_engineering_count,
            "missing_contract_count": missing_contract_count,
            "pre_selection_unresolved_count": pre_selection_unresolved_count,
            "select_allowed": eligible,
        },
        unresolved_issues,
    )


def _build_evidence_confidence(investability_packet: dict[str, Any]) -> dict[str, Any]:
    checks = [
        _as_dict(row)
        for row in list(investability_packet.get("checks") or [])
        if isinstance(row, dict)
    ]
    ready_checks = sum(1 for row in checks if bool(row.get("Ready", row.get("ready"))))
    total_checks = len(checks)
    value = round(ready_checks / total_checks * 100) if total_checks else 0
    if not total_checks:
        label = "미측정"
    elif value >= 80:
        label = "높음"
    elif value >= 50:
        label = "보통"
    else:
        label = "낮음"
    return {
        "value": value,
        "label": label,
        "ready_checks": ready_checks,
        "total_checks": total_checks,
        "basis": "저장된 investability ready check 비율이며 판단 route나 포트폴리오 품질을 결정하지 않습니다.",
    }


def _suggested_route(
    *,
    eligibility: dict[str, Any],
    decision_evidence: dict[str, Any],
    investability_packet: dict[str, Any],
) -> str:
    if not bool(eligibility.get("eligible")):
        return RE_REVIEW_REQUIRED
    gate = _as_dict(
        investability_packet.get("selection_gate_policy_snapshot")
        or investability_packet.get("gate_policy_snapshot")
    )
    route = str(
        gate.get("suggested_decision_route")
        or decision_evidence.get("suggested_decision_route")
        or SELECT_FOR_PRACTICAL_PORTFOLIO
    ).strip()
    return route if route in DECISION_BRIEF_ROUTE_PRESENTATION else SELECT_FOR_PRACTICAL_PORTFOLIO


def _build_decision_action(
    *,
    route: str,
    eligibility: dict[str, Any],
    decision_id: str,
    existing_decision_ids: set[str],
) -> dict[str, Any]:
    normalized_decision_id = str(decision_id or "").strip()
    duplicate = bool(normalized_decision_id and normalized_decision_id in existing_decision_ids)
    options: list[dict[str, Any]] = []
    for option_route, label in DECISION_BRIEF_ROUTE_PRESENTATION.items():
        selected_route_blocked = (
            option_route == SELECT_FOR_PRACTICAL_PORTFOLIO
            and not bool(eligibility.get("select_allowed"))
        )
        recordable = bool(normalized_decision_id) and not duplicate and not selected_route_blocked
        if duplicate:
            disabled_reason = "같은 Decision ID가 이미 저장되어 있습니다."
        elif not normalized_decision_id:
            disabled_reason = "Decision ID가 없어 판단을 기록할 수 없습니다."
        elif selected_route_blocked:
            disabled_reason = "선정 전 미해결 근거가 있어 계속 추적으로 기록할 수 없습니다."
        else:
            disabled_reason = ""
        presentation = _ROUTE_PRESENTATION[option_route]
        options.append(
            {
                "route": option_route,
                "label": label,
                "tone": presentation["tone"],
                "recordable": recordable,
                "disabled_reason": disabled_reason,
                "reason_placeholder": presentation["reason_placeholder"],
                "button_label": presentation["button_label"],
            }
        )
    return {
        "suggested_route": route,
        "suggested_label": DECISION_BRIEF_ROUTE_PRESENTATION[route],
        "reason_label": "판단 사유",
        "reason_help": "저장된 관측값과 trade-off를 바탕으로 사용자의 판단 이유를 작성합니다.",
        "options": options,
    }


def _unmeasured_series(*, label: str, basis: str, reason: str) -> dict[str, Any]:
    return {
        "status": "unmeasured",
        "label": label,
        "source": None,
        "basis": basis,
        "missing_reason": reason,
        "points": [],
    }


def _build_behavior_board() -> dict[str, Any]:
    missing_reason = "저장된 curve 관측값이 아직 Decision Brief 행동 근거로 투영되지 않았습니다."
    return {
        "period": {"start": None, "end": None, "frequency": "stored_curve"},
        "cumulative_series": _unmeasured_series(
            label="후보 누적 성과 미측정",
            basis="stored_curve_cost_unverified",
            reason=missing_reason,
        ),
        "benchmark_series": _unmeasured_series(
            label="Benchmark 누적 성과 미측정",
            basis="benchmark",
            reason=missing_reason,
        ),
        "underwater_series": _unmeasured_series(
            label="Underwater drawdown 미측정",
            basis="stored_curve_cost_unverified",
            reason=missing_reason,
        ),
        "execution_observations": [],
    }


def _build_trait_map() -> dict[str, Any]:
    return {
        "axes": [
            {
                "axis_id": axis_id,
                "label": label,
                "normalized_value": None,
                "status": "unmeasured",
                "measured_value": None,
                "threshold_or_comparator": None,
                "evidence_refs": [],
                "as_of": None,
            }
            for axis_id, label in _TRAIT_AXES
        ],
        "aggregate_score": None,
    }


def build_final_review_decision_brief(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    investability_packet: dict[str, Any],
    decision_id: str,
    existing_decision_ids: set[str],
) -> dict[str, Any]:
    """Project stored Final Review evidence into the current Decision Brief."""

    source = _as_dict(source)
    validation = _as_dict(validation)
    paper_observation = _as_dict(paper_observation)
    decision_evidence = _as_dict(decision_evidence)
    investability_packet = _as_dict(investability_packet)
    eligibility, unresolved_issues = _build_eligibility(
        validation=validation,
        investability_packet=investability_packet,
    )
    route = _suggested_route(
        eligibility=eligibility,
        decision_evidence=decision_evidence,
        investability_packet=investability_packet,
    )
    route_presentation = _ROUTE_PRESENTATION[route]
    evidence_confidence = _build_evidence_confidence(investability_packet)
    strengths, weaknesses, monitoring_conditions = _deduplicate_primary_roles(
        strengths=[],
        weaknesses=[],
        monitoring_conditions=[],
    )
    decision_action = _build_decision_action(
        route=route,
        eligibility=eligibility,
        decision_id=decision_id,
        existing_decision_ids={str(value) for value in existing_decision_ids},
    )
    closure = _as_dict(validation.get("evidence_closure"))
    closure_issues = [_as_dict(row) for row in list(closure.get("issues") or []) if isinstance(row, dict)]
    disclosures: dict[str, Any] = {
        "accepted_limits": [
            {
                "root_issue_id": str(row.get("root_issue_id") or ""),
                "title": str(row.get("title") or row.get("root_issue_id") or "인수한 한계"),
            }
            for row in closure_issues
            if str(row.get("resolution_class") or "") == "accepted_limit"
        ],
        "source_gaps": [],
        "provenance": [
            str(row.get("root_issue_id"))
            for row in closure_issues
            if str(row.get("root_issue_id") or "").strip()
        ],
    }
    if int(eligibility.get("pre_selection_unresolved_count") or 0) > 0:
        disclosures["pre_selection_unresolved"] = unresolved_issues or [
            {
                "title": "선정 전 근거 종결 필요",
                "count": int(eligibility["pre_selection_unresolved_count"]),
            }
        ]

    candidate_source_id = str(
        source.get("source_id")
        or validation.get("selection_source_id")
        or validation.get("validation_id")
        or ""
    ).strip()
    behavior_board = _build_behavior_board()
    capabilities = {
        "can_record_decision": any(
            bool(option.get("recordable")) for option in decision_action["options"]
        ),
        "can_select_for_monitoring": any(
            option.get("route") == SELECT_FOR_PRACTICAL_PORTFOLIO
            and bool(option.get("recordable"))
            for option in decision_action["options"]
        ),
        "provider_fetch": False,
        "validation_rerun": False,
        "storage_append_in_react": False,
    }
    return {
        "schema_version": DECISION_BRIEF_SCHEMA_VERSION,
        "candidate": {
            "source_id": candidate_source_id,
            "validation_id": str(validation.get("validation_id") or source.get("source_id") or "").strip(),
            "title": str(
                source.get("source_title")
                or validation.get("source_title")
                or source.get("title")
                or candidate_source_id
                or "후보"
            ),
            "source_type": str(source.get("source_type") or "").strip(),
            "as_of": source.get("updated_at") or validation.get("updated_at"),
        },
        "eligibility": eligibility,
        "verdict": {
            "route": route,
            "label": DECISION_BRIEF_ROUTE_PRESENTATION[route],
            "tone": route_presentation["tone"],
            "headline": route_presentation["headline"],
            "thesis": (
                "저장된 관측값을 행동 근거로 투영하기 전까지 포트폴리오의 강점과 trade-off는 미측정으로 유지합니다."
            ),
        },
        "evidence_confidence": evidence_confidence,
        "behavior_board": behavior_board,
        "trait_map": _build_trait_map(),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "monitoring_conditions": monitoring_conditions,
        "decision_action": decision_action,
        "disclosures": disclosures,
        "capabilities": capabilities,
    }


__all__ = [
    "DECISION_BRIEF_ROUTE_PRESENTATION",
    "DECISION_BRIEF_SCHEMA_VERSION",
    "build_final_review_candidate_selector",
    "build_final_review_decision_brief",
]
