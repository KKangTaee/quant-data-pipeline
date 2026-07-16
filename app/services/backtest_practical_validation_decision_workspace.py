from __future__ import annotations

from typing import Any

from app.services.backtest_evidence_closure import has_action_handler
from app.services.backtest_practical_validation_explanation import (
    PRACTICAL_VALIDATION_EVIDENCE_CATEGORIES,
    explain_practical_validation_row,
)
from app.services.backtest_practical_validation_source import (
    VALIDATION_PROFILE_OPTIONS,
)


PRACTICAL_VALIDATION_DECISION_WORKSPACE_SCHEMA_VERSION = (
    "practical_validation_decision_workspace_v1"
)

_ROOT_AUDIT_KEYS = {
    "validation_method_strength": "validation_efficacy_audit",
    "construction_risk": "construction_risk_audit",
    "backtest_realism": "backtest_realism_audit",
    "risk_contribution": "risk_contribution_audit",
    "component_role_weight": "component_role_weight_audit",
    "provider_investability": "data_coverage_audit",
    "historical_universe_coverage": "data_coverage_audit",
}

_ROOT_AUDIT_CRITERIA = {
    "provider_investability": {"Provider snapshot freshness"},
    "historical_universe_coverage": {
        "Universe / listing evidence",
        "Survivorship / delisting control",
    },
}

_AUDIT_LABELS = {
    "validation_efficacy_audit": "검증 방법론 강도",
    "construction_risk_audit": "포트폴리오 구성 근거",
    "backtest_realism_audit": "실전 운용 현실성",
    "risk_contribution_audit": "위험 기여",
    "component_role_weight_audit": "구성 역할과 비중",
    "data_coverage_audit": "데이터 범위와 최신성",
}

_SOURCE_KIND_LABELS = {
    "weighted_portfolio_mix": "혼합 포트폴리오",
    "saved_portfolio_mix": "저장 포트폴리오",
    "latest_backtest_run": "단일 전략 실행",
    "single_strategy": "단일 전략 실행",
}


def _dict_rows(value: Any) -> list[dict[str, Any]]:
    return [dict(row) for row in list(value or []) if isinstance(row, dict)]


def _audit_rows(
    validation_result: dict[str, Any],
    audit_key: str,
) -> list[dict[str, Any]]:
    return _dict_rows(dict(validation_result.get(audit_key) or {}).get("rows"))


def _stage_owner(row: dict[str, Any], *, default: str = "practical_validation") -> str:
    owner = str(row.get("stage_owner") or "").strip()
    if owner:
        return owner
    criterion = str(
        row.get("Criteria")
        or row.get("display_label")
        or row.get("label")
        or ""
    ).lower().replace("/", " ")
    return "final_review" if "tax" in criterion and "account" in criterion else default


def _explanation(row: dict[str, Any]) -> dict[str, Any]:
    return explain_practical_validation_row(
        row,
        stage_owner=_stage_owner(row),
    )


def _source_type_label(row: dict[str, Any]) -> str:
    source_kind = str(
        row.get("source_kind")
        or row.get("source_type")
        or ""
    ).strip().lower()
    return _SOURCE_KIND_LABELS.get(source_kind, "검증 후보")


def _source_option(row: dict[str, Any], selected_id: str) -> dict[str, Any]:
    source_id = str(row.get("selection_source_id") or "").strip()
    return {
        "selection_source_id": source_id,
        "title": str(
            row.get("source_title")
            or row.get("title")
            or row.get("strategy_name")
            or source_id
            or "후보"
        ),
        "source_type_label": _source_type_label(row),
        "selected": source_id == selected_id,
        "eligible": True,
    }


def _profile_model(profile: dict[str, Any]) -> dict[str, Any]:
    current_id = str(profile.get("profile_id") or "balanced_core")
    return {
        "profile_id": current_id,
        "profile_label": str(
            profile.get("profile_label")
            or dict(VALIDATION_PROFILE_OPTIONS.get(current_id) or {}).get("label")
            or current_id
        ),
        "options": [
            {
                "profile_id": profile_id,
                "label": str(config.get("label") or profile_id),
                "description": str(config.get("description") or ""),
                "selected": profile_id == current_id,
            }
            for profile_id, config in VALIDATION_PROFILE_OPTIONS.items()
        ],
        "advanced_control_owner": "streamlit_disclosure",
    }


def _issue_model(
    issue: dict[str, Any],
    validation_result: dict[str, Any],
) -> dict[str, Any]:
    resolution_class = str(
        issue.get("resolution_class") or "engineering_required"
    )
    measurement = dict(issue.get("measurement") or {})
    observed = measurement.get("observed")
    comparator = (
        measurement.get("threshold")
        if measurement.get("threshold") is not None
        else measurement.get("comparator")
    )
    measured_caution = (
        resolution_class == "validated_caution"
        and observed is not None
        and comparator is not None
    )
    action_id = str(issue.get("action_id") or "").strip() or None
    terminal_state = str(issue.get("terminal_state") or "open")
    actionable = (
        resolution_class == "resolve_now"
        and terminal_state == "open"
        and has_action_handler(action_id)
    )
    if resolution_class == "resolve_now" and not actionable:
        resolution_class = "engineering_required"
        terminal_state = "deferred"
        action_id = None
    root_issue_id = str(issue.get("root_issue_id") or "")
    audit_key = _ROOT_AUDIT_KEYS.get(root_issue_id)
    evidence_rows = _audit_rows(validation_result, audit_key) if audit_key else []
    criteria_filter = _ROOT_AUDIT_CRITERIA.get(root_issue_id)
    if criteria_filter:
        evidence_rows = [
            row
            for row in evidence_rows
            if str(row.get("Criteria") or "") in criteria_filter
        ]
    relevant_rows = [
        row
        for row in evidence_rows
        if str(row.get("Status") or "").upper()
        not in {"PASS", "READY", "NOT_APPLICABLE"}
    ] or evidence_rows
    explanations = [_explanation(row) for row in relevant_rows]
    if not explanations:
        pseudo_status = (
            "NOT_RUN"
            if resolution_class == "engineering_required"
            else "REVIEW"
        )
        explanations = [
            explain_practical_validation_row(
                {
                    "Criteria": issue.get("title") or root_issue_id,
                    "Status": pseudo_status,
                    "Evidence": issue.get("observed") or "",
                },
                stage_owner=str(
                    issue.get("stage_owner")
                    or (
                        "final_review"
                        if resolution_class
                        in {"accepted_limit", "final_decision", "monitoring_transfer"}
                        else "practical_validation"
                    )
                ),
            )
        ]
    return {
        "root_issue_id": root_issue_id,
        "title": str(
            explanations[0].get("display_title")
            or issue.get("title")
            or root_issue_id
            or "검증 항목"
        ),
        "finding_kind": "measured_caution" if measured_caution else resolution_class,
        "resolution_class": resolution_class,
        "observed": " ".join(
            str(row.get("result_summary") or "")
            for row in explanations
            if row.get("result_summary")
        ),
        "expected": " ".join(
            dict.fromkeys(
                str(row.get("next_action") or "")
                for row in explanations
                if row.get("next_action")
            )
        ),
        "cause": str(issue.get("cause") or ""),
        "criticality": str(issue.get("criticality") or "noncritical"),
        "terminal_state": terminal_state,
        "actionable_now": actionable,
        "action_id": action_id if actionable else None,
        "action_label": str(issue.get("action_label") or ""),
        "completion_criteria": str(issue.get("completion_criteria") or ""),
        "derived_checks": list(issue.get("derived_checks") or []),
        "measurement": measurement,
        "explanations": explanations,
    }


def _verified_findings(validation_result: dict[str, Any]) -> list[dict[str, Any]]:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    findings: list[dict[str, Any]] = []
    seen: set[str] = set()
    for audit_key, audit_label in _AUDIT_LABELS.items():
        for row in _audit_rows(validation_result, audit_key):
            status = str(row.get("Status") or "").upper()
            if status not in {"PASS", "READY"}:
                continue
            stable_id = f"{audit_key}:{row.get('Criteria')}"
            if stable_id in seen:
                continue
            seen.add(stable_id)
            explanation = _explanation(row)
            findings.append(
                {
                    "finding_id": stable_id,
                    "finding_kind": "verified",
                    "category_id": audit_key,
                    **explanation,
                }
            )
    for group in _dict_rows(
        workspace.get("visible_criteria_detail_groups")
        or workspace.get("criteria_detail_groups")
    ):
        group_id = str(group.get("group_id") or group.get("label") or "")
        for card in _dict_rows(group.get("criteria_cards")):
            status = str(card.get("status") or "").upper()
            if status not in {"PASS", "READY"}:
                continue
            stable_id = (
                f"{group_id}:"
                f"{card.get('label') or card.get('display_label')}"
            )
            if stable_id in seen:
                continue
            seen.add(stable_id)
            explanation = _explanation(card)
            findings.append(
                {
                    "finding_id": stable_id,
                    "finding_kind": "verified",
                    "category_id": group_id,
                    **explanation,
                }
            )
    return findings


def _category_for_group(group: dict[str, Any]) -> str | None:
    haystack = " ".join(
        str(group.get(key) or "")
        for key in ("group_id", "label", "display_label", "purpose")
    ).lower()
    for category in PRACTICAL_VALIDATION_EVIDENCE_CATEGORIES:
        if any(
            str(token).lower() in haystack
            for token in category.get("group_tokens", ())
        ):
            return str(category["category_id"])
    return None


def _category_summary(explanations: list[dict[str, Any]]) -> dict[str, int]:
    states = [str(row.get("evidence_state") or "missing") for row in explanations]
    return {
        "total_count": len(explanations),
        "verified_count": states.count("verified"),
        "review_count": states.count("computed"),
        "missing_count": states.count("missing"),
        "not_applicable_count": states.count("not_applicable"),
    }


def _category_outcome(summary: dict[str, int]) -> str:
    if summary["missing_count"]:
        return "보강 필요"
    if summary["review_count"]:
        return "주의 확인"
    if summary["verified_count"]:
        return "확인 완료"
    if summary["not_applicable_count"]:
        return "해당 없음"
    return "근거 없음"


def _category_disclosures(
    validation_result: dict[str, Any],
) -> list[dict[str, Any]]:
    workspace = dict(validation_result.get("practical_validation_workspace") or {})
    groups = _dict_rows(
        workspace.get("visible_criteria_detail_groups")
        or workspace.get("criteria_detail_groups")
    )
    disclosures: list[dict[str, Any]] = []
    seen_rows: set[tuple[str, str]] = set()
    for category in PRACTICAL_VALIDATION_EVIDENCE_CATEGORIES:
        category_id = str(category["category_id"])
        explanations: list[dict[str, Any]] = []
        for audit_key in category.get("audit_keys", ()):
            for row in _audit_rows(validation_result, str(audit_key)):
                explanation = _explanation(row)
                trace = dict(explanation.get("technical_trace") or {})
                stable_key = (
                    category_id,
                    str(trace.get("criterion") or ""),
                )
                if stable_key in seen_rows:
                    continue
                seen_rows.add(stable_key)
                explanations.append(explanation)
        for group in groups:
            if _category_for_group(group) != category_id:
                continue
            for row in _dict_rows(group.get("criteria_cards")):
                explanation = _explanation(row)
                trace = dict(explanation.get("technical_trace") or {})
                stable_key = (
                    category_id,
                    str(trace.get("criterion") or ""),
                )
                if stable_key in seen_rows:
                    continue
                seen_rows.add(stable_key)
                explanations.append(explanation)
        summary = _category_summary(explanations)
        disclosures.append(
            {
                "category_id": category_id,
                "title": str(category["title"]),
                "question": str(category["question"]),
                "outcome": _category_outcome(summary),
                "summary": summary,
                "verified_items": [
                    str(row.get("display_title") or "")
                    for row in explanations
                    if row.get("evidence_state") == "verified"
                ],
                "root_issue_ids": [
                    root_issue_id
                    for root_issue_id, mapped_key in _ROOT_AUDIT_KEYS.items()
                    if mapped_key in set(category.get("audit_keys", ()))
                ],
                "explanations": explanations,
            }
        )
    return disclosures


def _summary(
    *,
    verified_count: int,
    issues: list[dict[str, Any]],
    closure_summary: dict[str, Any],
) -> dict[str, int]:
    finding_counts = {
        finding_kind: sum(
            1
            for issue in issues
            if issue.get("finding_kind") == finding_kind
        )
        for finding_kind in (
            "measured_caution",
            "validated_caution",
            "resolve_now",
            "accepted_limit",
            "final_decision",
            "monitoring_transfer",
        )
    }
    engineering_blocker_count = sum(
        1
        for issue in issues
        if issue.get("resolution_class") == "engineering_required"
        and issue.get("criticality") == "critical"
        and issue.get("terminal_state")
        not in {"resolved", "accepted", "monitoring_transferred"}
    )
    return {
        "verified_count": verified_count,
        "measured_caution_count": finding_counts["measured_caution"],
        "validated_caution_count": sum(
            1
            for issue in issues
            if issue.get("resolution_class") == "validated_caution"
        ),
        "resolve_now_count": finding_counts["resolve_now"],
        "engineering_blocker_count": engineering_blocker_count,
        "accepted_limit_count": finding_counts["accepted_limit"],
        "final_decision_count": finding_counts["final_decision"],
        "monitoring_transfer_count": finding_counts["monitoring_transfer"],
        "missing_contract_count": int(
            closure_summary.get("missing_contract_count") or 0
        ),
    }


def _state(
    *,
    has_source: bool,
    replay_result: dict[str, Any] | None,
    validation_result: dict[str, Any] | None,
    summary: dict[str, int],
) -> str:
    if not has_source:
        return "source_required"
    if not replay_result:
        return "replay_required"
    if not validation_result:
        return "replay_required"
    if (
        summary["resolve_now_count"]
        or summary["engineering_blocker_count"]
        or summary["missing_contract_count"]
    ):
        return "resolution_required"
    if (
        summary["accepted_limit_count"]
        or summary["final_decision_count"]
        or summary["monitoring_transfer_count"]
    ):
        return "ready_with_handoff"
    return "ready"


def _verdict(state: str, summary: dict[str, int]) -> dict[str, str]:
    if state == "source_required":
        return {
            "tone": "neutral",
            "label": "후보 필요",
            "headline": "먼저 검증할 포트폴리오 후보를 선택하세요.",
            "detail": "Backtest Analysis에서 후보를 보내면 검증 기준과 replay 경로가 열립니다.",
        }
    if state == "replay_required":
        return {
            "tone": "neutral",
            "label": "재검증 필요",
            "headline": "최신 데이터 기준 재검증을 실행하세요.",
            "detail": "현재 세션 replay가 완료돼야 검증 결론과 저장 경로가 열립니다.",
        }
    if state == "resolution_required":
        return {
            "tone": "danger",
            "label": "이동 보류",
            "headline": "Final Review 전에 해결하거나 개발해야 할 항목이 있습니다.",
            "detail": (
                f"지금 해결 {summary['resolve_now_count']}건 · "
                f"개발 차단 {summary['engineering_blocker_count']}건"
            ),
        }
    if state == "ready_with_handoff":
        return {
            "tone": "warning",
            "label": "이동 가능",
            "headline": "Final Review로 이동할 수 있습니다.",
            "detail": (
                f"인수할 한계 {summary['accepted_limit_count']}건 · "
                f"최종 판단 {summary['final_decision_count']}건 · "
                f"Monitoring 이관 {summary['monitoring_transfer_count']}건을 전달합니다."
            ),
        }
    return {
        "tone": "positive",
        "label": "검증 완료",
        "headline": "추가 해결 항목 없이 Final Review로 이동할 수 있습니다.",
        "detail": "현재 검증 기준과 replay 결과가 이동 조건을 충족합니다.",
    }


def build_practical_validation_decision_workspace(
    *,
    source: dict[str, Any],
    validation_profile: dict[str, Any],
    replay_result: dict[str, Any] | None,
    validation_result: dict[str, Any] | None,
    source_options: list[dict[str, Any]],
) -> dict[str, Any]:
    """Project Level2 truth into a question-first, root-deduplicated read model."""

    selected_source_id = str(source.get("selection_source_id") or "")
    validation = dict(validation_result or {})
    closure = dict(validation.get("evidence_closure") or {})
    issues: list[dict[str, Any]] = []
    seen_root_ids: set[str] = set()
    for row in _dict_rows(closure.get("issues")):
        issue = _issue_model(row, validation)
        root_issue_id = str(issue.get("root_issue_id") or "")
        if not root_issue_id or root_issue_id in seen_root_ids:
            continue
        seen_root_ids.add(root_issue_id)
        issues.append(issue)
    verified = _verified_findings(validation)
    measured_cautions = [
        issue
        for issue in issues
        if issue["finding_kind"] in {"measured_caution", "validated_caution"}
    ]
    validated_cautions = [
        issue
        for issue in issues
        if issue["resolution_class"] == "validated_caution"
    ]
    summary = _summary(
        verified_count=len(verified),
        issues=issues,
        closure_summary=dict(closure.get("summary") or {}),
    )
    state = _state(
        has_source=bool(selected_source_id),
        replay_result=replay_result,
        validation_result=validation_result,
        summary=summary,
    )
    resolve_now = [
        issue
        for issue in issues
        if issue["finding_kind"] == "resolve_now" and issue["actionable_now"]
    ]
    engineering_required = [
        issue
        for issue in issues
        if issue["finding_kind"] == "engineering_required"
    ]
    final_review_handoff = [
        issue
        for issue in issues
        if issue["resolution_class"]
        in {"accepted_limit", "final_decision", "monitoring_transfer"}
    ]
    legacy_actions = dict(
        dict(validation.get("practical_validation_workspace") or {}).get(
            "next_stage_action"
        )
        or {}
    )
    primary = dict(legacy_actions.get("primary_action") or {})
    secondary = dict(legacy_actions.get("secondary_action") or {})
    can_move = state in {"ready", "ready_with_handoff"} and bool(
        dict(validation.get("final_review_gate") or {}).get("can_save_and_move")
    )
    return {
        "schema_version": PRACTICAL_VALIDATION_DECISION_WORKSPACE_SCHEMA_VERSION,
        "selection_source_id": selected_source_id,
        "validation_result_id": str(validation.get("validation_id") or ""),
        "state": state,
        "header": {
            "question": "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?",
            "detail": "후보와 기준을 확인하고 최신 데이터로 재검증한 뒤, 해결할 일과 넘길 판단을 구분합니다.",
        },
        "candidate_selector": {
            "selected_source_id": selected_source_id,
            "options": [
                _source_option(row, selected_source_id)
                for row in source_options
            ],
        },
        "candidate": {
            "selection_source_id": selected_source_id,
            "title": str(
                source.get("source_title")
                or source.get("title")
                or selected_source_id
                or "후보"
            ),
            "source_type_label": _source_type_label(source),
            "as_of": str(
                dict(source.get("period") or {}).get("actual_end")
                or validation.get("created_at")
                or ""
            ),
        },
        "profile": _profile_model(validation_profile),
        "replay": {
            "status": str(dict(replay_result or {}).get("status") or "NOT_RUN"),
            "replay_id": str(
                dict(replay_result or {}).get("replay_id") or ""
            ),
            "completed": bool(replay_result),
        },
        "verdict": _verdict(state, summary),
        "summary": summary,
        "verified_findings": verified,
        "validated_cautions": validated_cautions,
        "measured_cautions": measured_cautions,
        "resolution_lanes": {
            "resolve_now": resolve_now,
            "engineering_required": engineering_required,
            "final_review_handoff": final_review_handoff,
        },
        "category_disclosures": _category_disclosures(validation),
        "actions": {
            "run_replay": {
                "id": "run_replay",
                "label": "최신 데이터 기준 재검증",
                "enabled": bool(selected_source_id),
            },
            "save_audit_only": {
                "id": "save_audit_only",
                "label": str(secondary.get("label") or "검증 결과 저장"),
                "enabled": bool(secondary.get("enabled", True))
                and bool(validation_result),
            },
            "save_and_move": {
                "id": "save_and_move",
                "label": str(
                    primary.get("label")
                    or "저장하고 Final Review로 이동"
                ),
                "enabled": can_move,
            },
        },
        "boundaries": {
            "react_executes_validation": False,
            "react_executes_collection": False,
            "react_executes_storage": False,
            "python_validates_intent": True,
        },
    }


__all__ = [
    "PRACTICAL_VALIDATION_DECISION_WORKSPACE_SCHEMA_VERSION",
    "build_practical_validation_decision_workspace",
]
