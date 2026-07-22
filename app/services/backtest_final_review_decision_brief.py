"""Build the Streamlit-free Final Review Decision Brief projection.

Python owns candidate eligibility, canonical decision routes, and save
capabilities.  Presentation clients receive a JSON-serializable projection and
must not infer or persist domain state themselves.
"""

from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.backtest_evidence_closure import (
    build_structured_monitoring_condition,
)
from app.services.backtest_practical_validation_explanation import (
    explain_practical_validation_row,
)
from app.services.backtest_practical_validation_curve import normalize_result_curve
from app.services.backtest_realism_audit import (
    build_cost_model_source_contract,
    build_liquidity_capacity_contract,
    build_turnover_evidence_contract,
)

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

_LIQUIDITY_CAPACITY_STATUS_LABELS = {
    "official_fresh_capacity_evidence": "공식 제공처의 최신 유동성 근거 확보",
    "weak_source_or_proxy_liquidity_evidence": "공식 자료가 부족하거나 일부 대체 지표를 사용함",
    "partial_liquidity_coverage": "일부 구성요소의 유동성만 확인됨",
    "stale_or_unknown_provider_snapshot": "유동성 자료의 최신성 확인 필요",
    "provider_operability_review": "유동성 근거 추가 검토 필요",
    "missing_provider_operability": "유동성 근거가 아직 없음",
    "blocked_provider_operability": "가격 또는 제공처 문제로 유동성 확인 불가",
    "legacy_provider_pass_without_capacity_contract": "이전 형식 자료로 세부 유동성 근거 확인 필요",
    "incomplete_liquidity_capacity_evidence": "유동성 근거가 불완전함",
}

_CHARACTER_AXES = (
    ("concentration", "집중 성향", "percent", "최대 구성 비중 근거가 없습니다."),
    ("drawdown", "손실 특성", "percent", "running-peak 낙폭 curve가 없습니다."),
    ("turnover", "회전 성향", "ratio_percent", "holdings 기반 회전율 근거가 없습니다."),
    ("cost", "비용 가정", "bps", "거래비용 가정 근거가 없습니다."),
    (
        "regime_dependency",
        "국면 의존",
        "text",
        "국면별 성과 분산을 계산할 structured evidence가 없습니다.",
    ),
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
        incomplete_monitoring = (
            str(issue.get("resolution_class") or "").strip()
            == "monitoring_transfer"
            and build_structured_monitoring_condition(issue) is None
        )
        if not (
            bool(issue.get("actionable_now"))
            or str(issue.get("criticality") or "").strip() == "critical"
            or root_issue_id.startswith("missing_contract:")
            or incomplete_monitoring
        ):
            continue
        unresolved.append(
            {
                "root_issue_id": root_issue_id,
                "title": str(issue.get("title") or root_issue_id or "선정 전 근거 종결 필요"),
            }
        )
    return unresolved


def _build_level2_handoff(
    *,
    validation_id: str,
    closure_issues: list[dict[str, Any]],
    eligible: bool,
) -> dict[str, Any]:
    """Project each eligible Level2 root into exactly one Final Review lane."""

    empty = {
        "state": "blocked" if not eligible else "promoted",
        "validation_id": validation_id,
        "summary": {
            "final_decision_count": 0,
            "accepted_limit_count": 0,
            "monitoring_condition_count": 0,
        },
        "final_decisions": [],
        "accepted_limits": [],
        "monitoring_conditions": [],
    }
    if not eligible:
        return empty

    seen_root_issue_ids: set[str] = set()
    final_decisions: list[dict[str, Any]] = []
    accepted_limits: list[dict[str, Any]] = []
    monitoring_conditions: list[dict[str, Any]] = []
    for issue in closure_issues:
        root_issue_id = str(issue.get("root_issue_id") or "").strip()
        resolution_class = str(issue.get("resolution_class") or "").strip()
        if (
            not root_issue_id
            or root_issue_id in seen_root_issue_ids
            or resolution_class
            not in {"final_decision", "accepted_limit", "monitoring_transfer"}
        ):
            continue
        seen_root_issue_ids.add(root_issue_id)
        explanation = explain_practical_validation_row(
            {
                "Criteria": issue.get("title") or root_issue_id,
                "Status": "REVIEW",
                "Current": issue.get("observed") or "",
                "Next Action": (
                    issue.get("completion_criteria")
                    or issue.get("expected")
                    or ""
                ),
            },
            stage_owner="final_review",
        )
        if root_issue_id == "historical_universe_coverage":
            observed = (
                "현재 구성은 정적 universe를 사용합니다. 과거 편입·퇴출 "
                "전체 이력은 재현하지 않습니다."
            )
            guidance = (
                "이 범위가 성과를 유리하게 보이게 할 수 있음을 한계로 "
                "인수하고 최종 판단 사유에 남깁니다."
            )
        elif root_issue_id == "tax_account_scope":
            observed = (
                "세금, 계좌 유형, 최소 주문 단위는 현재 백테스트가 아니라 "
                "사용자의 실제 운용 조건에서 결정합니다."
            )
            guidance = (
                "적용할 계좌 조건과 수용 가능한 비용 범위를 최종 판단 "
                "사유에 기록합니다."
            )
        else:
            observed = str(explanation.get("result_summary") or "").strip()
            guidance = str(explanation.get("next_action") or "").strip()
        base = {
            "root_issue_id": root_issue_id,
            "title": str(
                explanation.get("display_title")
                or issue.get("title")
                or root_issue_id
            ),
            "observed": observed,
            "decision_guidance": guidance,
            "evidence_refs": [
                str(value).strip()
                for value in list(issue.get("derived_checks") or [])
                if str(value).strip()
            ],
        }
        if resolution_class == "final_decision":
            final_decisions.append(base)
        elif resolution_class == "accepted_limit":
            accepted_limits.append(base)
        else:
            condition = build_structured_monitoring_condition(issue)
            if condition is not None:
                monitoring_conditions.append(
                    {
                        **condition,
                        "root_issue_id": root_issue_id,
                        "title": str(issue.get("title") or root_issue_id),
                    }
                )

    return {
        "state": "promoted",
        "validation_id": validation_id,
        "summary": {
            "final_decision_count": len(final_decisions),
            "accepted_limit_count": len(accepted_limits),
            "monitoring_condition_count": len(monitoring_conditions),
        },
        "final_decisions": final_decisions,
        "accepted_limits": accepted_limits,
        "monitoring_conditions": monitoring_conditions,
    }


def validate_accepted_limit_acknowledgements(
    *,
    level2_handoff: dict[str, Any],
    acknowledgements: Any,
    decision_route: str,
) -> tuple[list[dict[str, str]], str]:
    """Validate one explicit Final Review decision for every promoted Level2 limit."""

    expected_root_issue_ids: list[str] = []
    for raw_item in list(_as_dict(level2_handoff).get("accepted_limits") or []):
        root_issue_id = str(_as_dict(raw_item).get("root_issue_id") or "").strip()
        if root_issue_id and root_issue_id not in expected_root_issue_ids:
            expected_root_issue_ids.append(root_issue_id)

    raw_acknowledgements = (
        list(acknowledgements) if isinstance(acknowledgements, list) else []
    )
    decisions_by_root: dict[str, str] = {}
    allowed_decisions = {"accepted", "return_to_level2"}
    for raw_acknowledgement in raw_acknowledgements:
        acknowledgement = _as_dict(raw_acknowledgement)
        root_issue_id = str(acknowledgement.get("root_issue_id") or "").strip()
        decision = str(acknowledgement.get("decision") or "").strip()
        if not root_issue_id:
            return [], "인수한 검증 한계의 식별값이 비어 있습니다."
        if root_issue_id in decisions_by_root:
            return [], "같은 검증 한계에 대한 선택이 중복되었습니다."
        if root_issue_id not in expected_root_issue_ids:
            return [], "현재 Final Review 인계 항목이 아닌 검증 한계가 포함되었습니다."
        if decision not in allowed_decisions:
            return [], "인수한 검증 한계에 지원하지 않는 선택값이 포함되었습니다."
        decisions_by_root[root_issue_id] = decision

    if any(root_issue_id not in decisions_by_root for root_issue_id in expected_root_issue_ids):
        return [], "모든 인수한 검증 한계에 대해 계속 인수할지 Level2로 되돌릴지 선택하세요."
    if any(
        decision == "return_to_level2"
        for decision in decisions_by_root.values()
    ) and str(decision_route or "").strip() != "RE_REVIEW_REQUIRED":
        return [], "Level2로 돌려보내기를 선택하면 최종 판단도 재검토 필요로 기록해야 합니다."

    return (
        [
            {
                "root_issue_id": root_issue_id,
                "decision": decisions_by_root[root_issue_id],
            }
            for root_issue_id in expected_root_issue_ids
        ],
        "",
    )


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
    observation_freshness: dict[str, Any],
) -> dict[str, Any]:
    normalized_decision_id = str(decision_id or "").strip()
    duplicate = bool(normalized_decision_id and normalized_decision_id in existing_decision_ids)
    options: list[dict[str, Any]] = []
    refresh_blocked = bool(observation_freshness.get("selection_blocked"))
    for option_route, label in DECISION_BRIEF_ROUTE_PRESENTATION.items():
        selected_route_blocked = (
            option_route == SELECT_FOR_PRACTICAL_PORTFOLIO
            and (
                not bool(eligibility.get("select_allowed"))
                or refresh_blocked
            )
        )
        recordable = bool(normalized_decision_id) and not duplicate and not selected_route_blocked
        if duplicate:
            disabled_reason = "같은 Decision ID가 이미 저장되어 있습니다."
        elif not normalized_decision_id:
            disabled_reason = "Decision ID가 없어 판단을 기록할 수 없습니다."
        elif selected_route_blocked:
            disabled_reason = (
                "최신 데이터로 다시 계산한 뒤 계속 추적으로 기록할 수 있습니다."
                if refresh_blocked
                else "선정 전 미해결 근거가 있어 계속 추적으로 기록할 수 없습니다."
            )
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


def _optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return None if pd.isna(numeric) else numeric


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _nested_date(validation: dict[str, Any], key: str) -> str | None:
    direct = _date_text(validation.get(key))
    if direct:
        return direct
    replay = _as_dict(_as_dict(validation.get("curve_evidence")).get("replay_attempt"))
    market_contract = _as_dict(replay.get("market_date_contract"))
    return _date_text(market_contract.get(key))


def _first_curve(
    candidates: list[tuple[Any, str]],
) -> tuple[pd.DataFrame, str | None]:
    for value, source in candidates:
        normalized = normalize_result_curve(value)
        if not normalized.empty:
            return normalized, source
    return pd.DataFrame(), None


def _stored_curve_inputs(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
) -> dict[str, Any]:
    """Resolve stored curves by provenance priority without replaying anything."""

    replay = _as_dict(_as_dict(validation.get("curve_evidence")).get("replay_attempt"))
    selection_snapshot = _as_dict(validation.get("selection_source_snapshot"))
    portfolio_curve, portfolio_source = _first_curve(
        [
            (
                replay.get("portfolio_curve"),
                "validation.curve_evidence.replay_attempt.portfolio_curve",
            ),
            (
                selection_snapshot.get("result_curve"),
                "validation.selection_source_snapshot.result_curve",
            ),
            (source.get("result_curve"), "source.result_curve"),
        ]
    )
    benchmark_curve, benchmark_source = _first_curve(
        [
            (
                replay.get("benchmark_curve"),
                "validation.curve_evidence.replay_attempt.benchmark_curve",
            ),
            (
                selection_snapshot.get("benchmark_curve"),
                "validation.selection_source_snapshot.benchmark_curve",
            ),
            (source.get("benchmark_curve"), "source.benchmark_curve"),
        ]
    )
    return {
        "portfolio_curve": portfolio_curve,
        "portfolio_source": portfolio_source,
        "benchmark_curve": benchmark_curve,
        "benchmark_source": benchmark_source,
    }


def _curve_frequency(curve: pd.DataFrame) -> str:
    if len(curve) < 2:
        return "unknown"
    step_days = curve["Date"].sort_values().diff().dropna().dt.days.median()
    if pd.isna(step_days):
        return "unknown"
    if float(step_days) <= 3:
        return "daily"
    if 25 <= float(step_days) <= 35:
        return "monthly"
    return f"step_{float(step_days):.0f}d"


def _rebased_points(curve: pd.DataFrame) -> list[dict[str, Any]]:
    if curve.empty:
        return []
    first_balance = _optional_float(curve.iloc[0]["Total Balance"])
    if first_balance is None or first_balance == 0:
        return []
    return [
        {
            "date": pd.Timestamp(row["Date"]).strftime("%Y-%m-%d"),
            "value": round(float(row["Total Balance"]) / first_balance * 100.0, 4),
        }
        for _, row in curve.iterrows()
    ]


def _underwater_points(curve: pd.DataFrame) -> list[dict[str, Any]]:
    cumulative = _rebased_points(curve)
    running_peak = 0.0
    points: list[dict[str, Any]] = []
    for point in cumulative:
        value = float(point["value"])
        running_peak = max(running_peak, value)
        underwater = round((value / running_peak - 1.0) * 100.0, 4) if running_peak else 0.0
        points.append({"date": point["date"], "value": underwater})
    return points


def _measured_series(
    *,
    label: str,
    source: str | None,
    basis: str,
    points: list[dict[str, Any]],
) -> dict[str, Any]:
    return {
        "status": "measured",
        "label": label,
        "source": source,
        "basis": basis,
        "missing_reason": None,
        "points": points,
    }


def _profile_thresholds(validation: dict[str, Any]) -> dict[str, Any]:
    return _as_dict(_as_dict(validation.get("validation_profile")).get("thresholds"))


def _display_percent(value: float, *, ratio: bool = False) -> str:
    displayed = value * 100.0 if ratio else value
    return f"{displayed:.2f}%"


def _liquidity_capacity_status_label(proof_status: str) -> str:
    """Translate a stable audit identity into first-read Final Review copy."""

    return _LIQUIDITY_CAPACITY_STATUS_LABELS.get(
        str(proof_status or "").strip(),
        "유동성 근거 상태 확인 필요",
    )


def _observation(
    *,
    observation_id: str,
    title: str,
    interpretation: str,
    measured_value: float | str,
    display_value: str,
    threshold_or_comparator: float | str | None,
    evidence_refs: list[str],
    as_of: str | None,
    comparison: str | None = None,
    character_axis: str | None = None,
    finding_eligible: bool = True,
    root_issue_id: str | None = None,
) -> dict[str, Any]:
    return {
        "observation_id": observation_id,
        "root_issue_id": root_issue_id,
        "title": title,
        "interpretation": interpretation,
        "measured_value": measured_value,
        "display_value": display_value,
        "threshold_or_comparator": threshold_or_comparator,
        "evidence_refs": evidence_refs,
        "as_of": as_of,
        "_comparison": comparison,
        "_character_axis": character_axis,
        "_finding_eligible": finding_eligible,
    }


def _public_observation(row: dict[str, Any]) -> dict[str, Any]:
    return {key: value for key, value in row.items() if not key.startswith("_")}


def _build_execution_observations(
    *,
    validation: dict[str, Any],
    behavior_board: dict[str, Any],
    cost_contract: dict[str, Any],
) -> list[dict[str, Any]]:
    """Normalize only structured measurements; prose is never parsed as data."""

    thresholds = _profile_thresholds(validation)
    metrics = _as_dict(validation.get("metrics"))
    period = _as_dict(behavior_board.get("period"))
    as_of = str(period.get("end") or _nested_date(validation, "latest_valuation_date") or "") or None
    observations: list[dict[str, Any]] = []

    max_weight = _optional_float(metrics.get("max_weight"))
    max_weight_threshold = _optional_float(thresholds.get("max_weight_review"))
    if max_weight is not None:
        observations.append(
            _observation(
                observation_id="concentration-pressure",
                title="최대 구성 비중",
                interpretation="가장 큰 구성요소 비중을 저장된 profile review 기준과 비교합니다.",
                measured_value=max_weight,
                display_value=_display_percent(max_weight),
                threshold_or_comparator=max_weight_threshold,
                evidence_refs=["validation.metrics.max_weight", "validation.validation_profile.thresholds.max_weight_review"],
                as_of=as_of,
                comparison="less_or_equal",
                character_axis="concentration",
            )
        )

    turnover = build_turnover_evidence_contract(validation)
    avg_turnover = _optional_float(turnover.get("avg_turnover"))
    turnover_threshold = _optional_float(
        thresholds.get("avg_turnover_review")
        or thresholds.get("turnover_review")
    )
    if avg_turnover is not None:
        observations.append(
            _observation(
                observation_id="turnover-burden",
                title="평균 회전율",
                interpretation="저장된 holdings 기반 평균 회전율을 명시된 review 기준과 비교합니다.",
                measured_value=avg_turnover,
                display_value=_display_percent(avg_turnover, ratio=True),
                threshold_or_comparator=turnover_threshold,
                evidence_refs=["validation.backtest_realism_audit.turnover_evidence_contract.avg_turnover"],
                as_of=as_of,
                comparison="less_or_equal",
                character_axis="turnover",
            )
        )

    transaction_cost_bps = _optional_float(cost_contract.get("transaction_cost_bps"))
    cost_threshold = _optional_float(thresholds.get("transaction_cost_bps_review"))
    cost_applied = str(cost_contract.get("application_status") or "").startswith(
        "applied_to_result_curve"
    )
    if transaction_cost_bps is not None:
        observations.append(
            _observation(
                observation_id="cost-burden",
                title="거래비용 가정",
                interpretation="거래비용 bps와 result curve 적용 증명을 함께 확인합니다.",
                measured_value=transaction_cost_bps,
                display_value=f"{transaction_cost_bps:.2f} bps",
                threshold_or_comparator=cost_threshold,
                evidence_refs=["validation.backtest_realism_audit.cost_model_contract.transaction_cost_bps"],
                as_of=as_of,
                comparison="less_or_equal",
                character_axis="cost",
                finding_eligible=cost_applied,
            )
        )

    liquidity = build_liquidity_capacity_contract(validation)
    liquidity_status = str(liquidity.get("proof_status") or "").strip()
    if liquidity_status:
        observations.append(
            _observation(
                observation_id="liquidity-capacity",
                title="유동성·운용 가능성 근거",
                interpretation="공식 제공처의 유동성 자료 범위와 최신성을 확인합니다.",
                measured_value=liquidity_status,
                display_value=_liquidity_capacity_status_label(liquidity_status),
                threshold_or_comparator=_liquidity_capacity_status_label(
                    "official_fresh_capacity_evidence"
                ),
                evidence_refs=["validation.backtest_realism_audit.liquidity_capacity_contract"],
                as_of=as_of,
                finding_eligible=False,
            )
        )

    underwater_points = list(_as_dict(behavior_board.get("underwater_series")).get("points") or [])
    drawdown_threshold = _optional_float(thresholds.get("max_drawdown_review_pct"))
    if drawdown_threshold is None:
        drawdown_threshold = _optional_float(thresholds.get("mdd_review_line"))
    if underwater_points:
        max_drawdown = min(float(point.get("value") or 0.0) for point in underwater_points)
        observations.append(
            _observation(
                observation_id="drawdown-recovery-path",
                title="최대 underwater 낙폭",
                interpretation="저장된 curve의 running peak 대비 최대 낙폭 압력입니다.",
                measured_value=max_drawdown,
                display_value=_display_percent(max_drawdown),
                threshold_or_comparator=drawdown_threshold,
                evidence_refs=["behavior_board.underwater_series"],
                as_of=as_of,
                comparison="absolute_less_or_equal",
                character_axis="drawdown",
            )
        )

    cumulative = list(_as_dict(behavior_board.get("cumulative_series")).get("points") or [])
    benchmark = list(_as_dict(behavior_board.get("benchmark_series")).get("points") or [])
    if cumulative and benchmark:
        relative_terminal = round(float(cumulative[-1]["value"]) - float(benchmark[-1]["value"]), 4)
        observations.append(
            _observation(
                observation_id="benchmark-relative-terminal",
                title="동일 기간 Benchmark 상대 성과",
                interpretation="공통일·공통 기준점으로 정렬한 terminal 누적 성과 차이입니다.",
                measured_value=relative_terminal,
                display_value=f"{relative_terminal:+.2f}%p",
                threshold_or_comparator=0.0,
                evidence_refs=["behavior_board.cumulative_series", "behavior_board.benchmark_series"],
                as_of=as_of,
                comparison="greater_or_equal",
            )
        )
    return observations


def _build_behavior_board(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
) -> tuple[dict[str, Any], list[dict[str, Any]], list[str]]:
    curve_inputs = _stored_curve_inputs(source=source, validation=validation)
    portfolio_curve = curve_inputs["portfolio_curve"]
    benchmark_curve = curve_inputs["benchmark_curve"]
    portfolio_source = curve_inputs["portfolio_source"]
    benchmark_source = curve_inputs["benchmark_source"]
    cost_contract = build_cost_model_source_contract(validation)
    cost_applied = str(cost_contract.get("application_status") or "").startswith(
        "applied_to_result_curve"
    )
    candidate_basis = "net_cost_applied" if cost_applied else "stored_curve_cost_unverified"
    candidate_label = "후보 누적 순성과" if cost_applied else "후보 누적 성과"
    source_gaps: list[str] = []

    if portfolio_curve.empty:
        candidate_reason = "저장된 후보 curve가 없어 누적 성과를 측정하지 못했습니다."
        source_gaps.append(candidate_reason)
    else:
        candidate_reason = "Benchmark와 공통인 저장일이 2개 미만이라 상대 누적 성과를 측정하지 못했습니다."
    if benchmark_curve.empty:
        parity_reason = "저장된 Benchmark curve가 없어 공통 기간 상대 성과를 측정하지 못했습니다."
        source_gaps.append(parity_reason)
    else:
        parity_reason = candidate_reason

    aligned = pd.DataFrame()
    if not portfolio_curve.empty and not benchmark_curve.empty:
        candidate = portfolio_curve.drop_duplicates(subset=["Date"], keep="last")
        benchmark = benchmark_curve.drop_duplicates(subset=["Date"], keep="last")
        aligned = candidate[["Date", "Total Balance"]].merge(
            benchmark[["Date", "Total Balance"]],
            on="Date",
            how="inner",
            suffixes=("_candidate", "_benchmark"),
        ).sort_values("Date")

    if len(aligned) >= 2:
        candidate_aligned = aligned[["Date", "Total Balance_candidate"]].rename(
            columns={"Total Balance_candidate": "Total Balance"}
        )
        benchmark_aligned = aligned[["Date", "Total Balance_benchmark"]].rename(
            columns={"Total Balance_benchmark": "Total Balance"}
        )
        candidate_points = _rebased_points(candidate_aligned)
        benchmark_points = _rebased_points(benchmark_aligned)
        cumulative_series = _measured_series(
            label=candidate_label,
            source=portfolio_source,
            basis=candidate_basis,
            points=candidate_points,
        )
        benchmark_series = _measured_series(
            label="Benchmark 누적 성과",
            source=benchmark_source,
            basis="benchmark",
            points=benchmark_points,
        )
        period_curve = candidate_aligned
    else:
        if not portfolio_curve.empty and not benchmark_curve.empty:
            source_gaps.append(parity_reason)
        cumulative_series = _unmeasured_series(
            label="후보 누적 성과 미측정",
            basis=candidate_basis,
            reason=parity_reason if not benchmark_curve.empty or not portfolio_curve.empty else candidate_reason,
        )
        benchmark_series = _unmeasured_series(
            label="Benchmark 누적 성과 미측정",
            basis="benchmark",
            reason=parity_reason,
        )
        period_curve = portfolio_curve

    underwater_points = _underwater_points(portfolio_curve)
    if underwater_points:
        underwater_series = _measured_series(
            label="Underwater drawdown",
            source=portfolio_source,
            basis=candidate_basis,
            points=underwater_points,
        )
    else:
        underwater_series = _unmeasured_series(
            label="Underwater drawdown 미측정",
            basis=candidate_basis,
            reason=candidate_reason,
        )
    if not portfolio_curve.empty and not cost_applied:
        source_gaps.append("거래비용이 저장 curve에 적용됐다는 증명이 없어 순성과로 표시하지 않습니다.")

    period_start = _date_text(period_curve["Date"].min()) if not period_curve.empty else None
    period_end = _date_text(period_curve["Date"].max()) if not period_curve.empty else None
    behavior_board = {
        "period": {
            "start": period_start,
            "end": period_end,
            "frequency": _curve_frequency(period_curve),
            "requested_market_date": _nested_date(validation, "requested_market_date"),
            "last_complete_rebalance_date": _nested_date(validation, "last_complete_rebalance_date"),
            "latest_valuation_date": _nested_date(validation, "latest_valuation_date"),
        },
        "cumulative_series": cumulative_series,
        "benchmark_series": benchmark_series,
        "underwater_series": underwater_series,
        "execution_observations": [],
    }
    internal_observations = _build_execution_observations(
        validation=validation,
        behavior_board=behavior_board,
        cost_contract=cost_contract,
    )
    behavior_board["execution_observations"] = [
        _public_observation(row) for row in internal_observations
    ]
    return behavior_board, internal_observations, list(dict.fromkeys(source_gaps))


def _build_character_profile(observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Project actual stored traits independently from review criteria."""

    by_axis = {
        str(row.get("_character_axis")): row
        for row in observations
        if str(row.get("_character_axis") or "").strip()
    }
    items: list[dict[str, Any]] = []
    for axis_id, label, unit, missing_reason in _CHARACTER_AXES:
        observation = by_axis.get(axis_id, {})
        measured = _optional_float(observation.get("measured_value"))
        observed = measured is not None
        items.append(
            {
                "axis_id": axis_id,
                "label": label,
                "measurement_status": "observed" if observed else "evidence_missing",
                "measured_value": measured,
                "display_value": (
                    str(observation.get("display_value"))
                    if observed
                    else "분석 근거 없음"
                ),
                "unit": unit,
                "interpretation": (
                    str(observation.get("interpretation") or "")
                    if observed
                    else missing_reason
                ),
                "evidence_refs": list(observation.get("evidence_refs") or []),
                "as_of": observation.get("as_of"),
            }
        )
    return {"items": items}


def _criterion_display(axis_id: str, value: float) -> str:
    if axis_id == "cost":
        return f"{value:.2f} bps"
    if axis_id == "turnover":
        return _display_percent(value, ratio=True)
    return _display_percent(value)


def _delta_display(axis_id: str, delta: float, *, favorable: bool) -> str:
    displayed = delta * 100.0 if axis_id == "turnover" else delta
    unit = "bps" if axis_id == "cost" else "%p"
    return f"{abs(displayed):.2f}{unit} {'이내' if favorable else '초과'}"


def _criterion_favorable(measured: float, criterion: float, comparison: str) -> bool:
    if comparison == "absolute_less_or_equal":
        return abs(measured) <= abs(criterion)
    if comparison == "less_or_equal":
        return measured <= criterion
    if comparison == "greater_or_equal":
        return measured >= criterion
    raise ValueError(f"unsupported review comparison: {comparison}")


def _build_review_pressure(observations: list[dict[str, Any]]) -> dict[str, Any]:
    """Compare observed traits only when an explicit review criterion exists."""

    by_axis = {
        str(row.get("_character_axis")): row
        for row in observations
        if str(row.get("_character_axis") or "").strip()
    }
    items: list[dict[str, Any]] = []
    for axis_id, label, _unit, missing_reason in _CHARACTER_AXES:
        observation = by_axis.get(axis_id, {})
        measured = _optional_float(observation.get("measured_value"))
        criterion = _optional_float(observation.get("threshold_or_comparator"))
        comparison = str(observation.get("_comparison") or "")
        common = {
            "axis_id": axis_id,
            "label": label,
            "evidence_refs": list(observation.get("evidence_refs") or []),
            "as_of": observation.get("as_of"),
        }
        if measured is None:
            items.append(
                {
                    **common,
                    "status": "evidence_missing",
                    "measured_value": None,
                    "display_value": "분석 근거 없음",
                    "criterion_value": None,
                    "criterion_display": None,
                    "comparison": None,
                    "delta_value": None,
                    "delta_display": None,
                    "ratio_to_criterion": None,
                    "summary": missing_reason,
                }
            )
            continue
        display_value = str(observation.get("display_value") or measured)
        if criterion is None or not comparison:
            items.append(
                {
                    **common,
                    "status": "criterion_missing",
                    "measured_value": measured,
                    "display_value": display_value,
                    "criterion_value": None,
                    "criterion_display": None,
                    "comparison": comparison or None,
                    "delta_value": None,
                    "delta_display": None,
                    "ratio_to_criterion": None,
                    "summary": f"{label} 값은 관측됐지만 review 기준이 설정되지 않았습니다.",
                }
            )
            continue
        if criterion == 0:
            raise ValueError(f"zero review criterion is invalid for {axis_id}")
        favorable = _criterion_favorable(measured, criterion, comparison)
        delta = round(abs(measured) - abs(criterion), 4)
        criterion_display = _criterion_display(axis_id, criterion)
        delta_display = _delta_display(axis_id, delta, favorable=favorable)
        criterion_prefix = "관리선" if axis_id == "drawdown" else "기준"
        items.append(
            {
                **common,
                "status": "within_limit" if favorable else "exceeds_limit",
                "measured_value": measured,
                "display_value": display_value,
                "criterion_value": criterion,
                "criterion_display": criterion_display,
                "comparison": comparison,
                "delta_value": (
                    round(delta * 100.0, 4) if axis_id == "turnover" else delta
                ),
                "delta_display": delta_display,
                "ratio_to_criterion": round(abs(measured) / abs(criterion), 4),
                "summary": f"{criterion_prefix} {criterion_display} 대비 {delta_display}",
            }
        )
    return {"items": items}


def _build_findings(
    observations: list[dict[str, Any]],
) -> tuple[list[dict[str, Any]], list[dict[str, Any]]]:
    strengths: list[dict[str, Any]] = []
    weaknesses: list[dict[str, Any]] = []
    for observation in observations:
        measured = _optional_float(observation.get("measured_value"))
        comparator = _optional_float(observation.get("threshold_or_comparator"))
        comparison = str(observation.get("_comparison") or "")
        if (
            measured is None
            or comparator is None
            or not comparison
            or not bool(observation.get("_finding_eligible"))
        ):
            continue
        favorable = _criterion_favorable(measured, comparator, comparison)
        role = "strength" if favorable else "weakness"
        finding = {
            **_public_observation(observation),
            "interpretation": (
                f"{observation['display_value']} 관측값이 저장된 비교 기준 "
                f"{comparator:g} {'이내' if favorable and comparison in {'less_or_equal', 'absolute_less_or_equal'} else '이상' if favorable else '밖'}입니다."
            ),
            "primary_role": role,
        }
        (strengths if favorable else weaknesses).append(finding)
    return strengths, weaknesses


def _build_monitoring_conditions(
    *,
    paper_observation: dict[str, Any],
    observations: list[dict[str, Any]],
    behavior_period: dict[str, Any],
) -> tuple[list[dict[str, Any]], list[str]]:
    """Project complete stored triggers, then derive only explicit safe fallbacks."""

    cadence_labels = {
        "monthly_or_rebalance_review": "월간 또는 리밸런싱 시점",
        "monthly": "월간",
        "quarterly": "분기",
        "rebalance": "리밸런싱 시점",
    }
    stored_cadence = str(paper_observation.get("review_cadence") or "").strip()
    if stored_cadence:
        cadence = cadence_labels.get(stored_cadence, stored_cadence)
    else:
        frequency = str(behavior_period.get("frequency") or "").strip().lower()
        cadence = {"monthly": "월간", "quarterly": "분기"}.get(frequency, "")

    conditions: list[dict[str, Any]] = []
    unstructured: list[str] = []
    covered_semantics: set[str] = set()
    semantic_ids = {
        "drawdown-recovery-path": "drawdown",
        "monitoring:drawdown-breach": "drawdown",
        "benchmark-relative-terminal": "benchmark",
        "monitoring:benchmark-underperformance": "benchmark",
    }
    for raw_row in list(paper_observation.get("review_trigger_details") or []):
        row = _as_dict(raw_row)
        observation_id = str(row.get("observation_id") or "").strip()
        observation = str(row.get("observation") or "").strip()
        threshold = str(row.get("threshold") or "").strip()
        cadence = str(row.get("cadence") or "").strip()
        action = str(row.get("re_review_action") or "").strip()
        evidence_refs = [str(value) for value in list(row.get("evidence_refs") or []) if str(value).strip()]
        measured_value = row.get("measured_value")
        comparator = row.get("threshold_or_comparator")
        if not (
            observation_id
            and observation
            and threshold
            and cadence
            and action
            and evidence_refs
            and _optional_float(measured_value) is not None
            and _optional_float(comparator) is not None
        ):
            text = str(row.get("title") or observation or row.get("trigger") or "").strip()
            if text:
                unstructured.append(text)
            continue
        conditions.append(
            {
                "observation_id": observation_id,
                "root_issue_id": str(row.get("root_issue_id") or "").strip() or None,
                "title": str(row.get("title") or observation),
                "interpretation": action,
                "measured_value": measured_value,
                "display_value": str(row.get("display_value") or measured_value),
                "threshold_or_comparator": comparator,
                "evidence_refs": evidence_refs,
                "as_of": _date_text(row.get("as_of")),
                "observation": observation,
                "threshold": threshold,
                "cadence": cadence,
                "re_review_action": action,
                "primary_role": "monitoring",
            }
        )
        semantic = semantic_ids.get(observation_id)
        if semantic:
            covered_semantics.add(semantic)
        if len(conditions) == 4:
            break

    observations_by_id = {
        str(row.get("observation_id") or "").strip(): row
        for row in observations
        if str(row.get("observation_id") or "").strip()
    }

    drawdown = observations_by_id.get("drawdown-recovery-path", {})
    drawdown_measured = _optional_float(drawdown.get("measured_value"))
    drawdown_comparator = _optional_float(drawdown.get("threshold_or_comparator"))
    drawdown_evidence = [
        str(value)
        for value in list(drawdown.get("evidence_refs") or [])
        if str(value).strip()
    ]
    drawdown_as_of = _date_text(drawdown.get("as_of"))
    if (
        len(conditions) < 4
        and "drawdown" not in covered_semantics
        and drawdown_measured is not None
        and drawdown_comparator is not None
        and str(drawdown.get("_comparison") or "") == "absolute_less_or_equal"
        and cadence
        and drawdown_evidence
        and drawdown_as_of
    ):
        display_value = str(
            drawdown.get("display_value") or _display_percent(drawdown_measured)
        )
        criterion_display = _display_percent(drawdown_comparator)
        conditions.append(
            {
                "observation_id": "monitoring:drawdown-breach",
                "root_issue_id": None,
                "title": "낙폭 관리선 이탈 재검토",
                "interpretation": (
                    "최대 낙폭이 관리선을 벗어나면 손실 감내 조건과 "
                    "계속 추적 thesis를 다시 검토합니다."
                ),
                "measured_value": drawdown_measured,
                "display_value": display_value,
                "threshold_or_comparator": drawdown_comparator,
                "evidence_refs": drawdown_evidence,
                "as_of": drawdown_as_of,
                "observation": f"현재 최대 underwater 낙폭 {display_value}",
                "threshold": f"최대 낙폭이 {criterion_display} 이하로 악화",
                "cadence": cadence,
                "re_review_action": (
                    "손실 감내 조건과 계속 추적 thesis를 다시 검토합니다."
                ),
                "primary_role": "monitoring",
            }
        )
        covered_semantics.add("drawdown")

    benchmark = observations_by_id.get("benchmark-relative-terminal", {})
    benchmark_measured = _optional_float(benchmark.get("measured_value"))
    benchmark_comparator = _optional_float(benchmark.get("threshold_or_comparator"))
    benchmark_evidence = [
        str(value)
        for value in list(benchmark.get("evidence_refs") or [])
        if str(value).strip()
    ]
    benchmark_as_of = _date_text(benchmark.get("as_of"))
    if (
        len(conditions) < 4
        and "benchmark" not in covered_semantics
        and benchmark_measured is not None
        and benchmark_comparator is not None
        and str(benchmark.get("_comparison") or "") == "greater_or_equal"
        and cadence
        and benchmark_evidence
        and benchmark_as_of
    ):
        display_value = str(
            benchmark.get("display_value") or f"{benchmark_measured:+.2f}%p"
        )
        conditions.append(
            {
                "observation_id": "monitoring:benchmark-underperformance",
                "root_issue_id": None,
                "title": "Benchmark 상대 성과 재검토",
                "interpretation": (
                    "동일 기간 상대 성과가 0%p 이하로 내려가면 "
                    "Benchmark 대비 추적 가치를 다시 검토합니다."
                ),
                "measured_value": benchmark_measured,
                "display_value": display_value,
                "threshold_or_comparator": benchmark_comparator,
                "evidence_refs": benchmark_evidence,
                "as_of": benchmark_as_of,
                "observation": (
                    f"현재 동일 기간 Benchmark 상대 성과 {display_value}"
                ),
                "threshold": (
                    "동일 기간 Benchmark 상대 성과가 "
                    f"{benchmark_comparator:.2f}%p 이하"
                ),
                "cadence": cadence,
                "re_review_action": (
                    "Benchmark 대비 추적 가치와 최종 route를 다시 검토합니다."
                ),
                "primary_role": "monitoring",
            }
        )
        covered_semantics.add("benchmark")

    for raw_trigger in list(paper_observation.get("review_triggers") or []):
        trigger = str(raw_trigger or "").strip()
        normalized = trigger.lower()
        if not trigger:
            continue
        if "drawdown" in covered_semantics and (
            "mdd" in normalized or "drawdown" in normalized
        ):
            continue
        if "benchmark" in covered_semantics and "benchmark" in normalized:
            continue
        unstructured.append(trigger)

    return conditions[:4], list(dict.fromkeys(unstructured))


def _build_thesis(
    *,
    strengths: list[dict[str, Any]],
    weaknesses: list[dict[str, Any]],
    source_gaps: list[str],
) -> str:
    if strengths and weaknesses:
        return (
            f"{strengths[0]['title']}은 저장된 비교 기준에서 강점으로 관측됐습니다. "
            f"반면 {weaknesses[0]['title']}은 가장 먼저 추적할 trade-off입니다."
        )
    if strengths:
        gap = source_gaps[0] if source_gaps else "반대편 trade-off는 미측정입니다."
        return f"{strengths[0]['title']}은 직접 관측된 강점입니다. {gap}"
    if weaknesses:
        return f"{weaknesses[0]['title']}은 직접 관측된 trade-off이며, 강점 근거는 아직 미측정입니다."
    return source_gaps[0] if source_gaps else "비교 가능한 행동 관측값이 아직 미측정입니다."


def build_final_review_decision_brief(
    *,
    source: dict[str, Any],
    validation: dict[str, Any],
    paper_observation: dict[str, Any],
    decision_evidence: dict[str, Any],
    investability_packet: dict[str, Any],
    decision_id: str,
    existing_decision_ids: set[str],
    observation_freshness: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Project stored Final Review evidence into the current Decision Brief."""

    source = _as_dict(source)
    validation = _as_dict(validation)
    paper_observation = _as_dict(paper_observation)
    decision_evidence = _as_dict(decision_evidence)
    investability_packet = _as_dict(investability_packet)
    observation_freshness = _as_dict(observation_freshness)
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
    behavior_board, internal_observations, source_gaps = _build_behavior_board(
        source=source,
        validation=validation,
    )
    projected_strengths, projected_weaknesses = _build_findings(internal_observations)
    projected_conditions, unstructured_triggers = _build_monitoring_conditions(
        paper_observation=paper_observation,
        observations=internal_observations,
        behavior_period=_as_dict(behavior_board.get("period")),
    )
    strengths, weaknesses, monitoring_conditions = _deduplicate_primary_roles(
        strengths=projected_strengths,
        weaknesses=projected_weaknesses,
        monitoring_conditions=projected_conditions,
    )
    decision_action = _build_decision_action(
        route=route,
        eligibility=eligibility,
        decision_id=decision_id,
        existing_decision_ids={str(value) for value in existing_decision_ids},
        observation_freshness=observation_freshness,
    )
    closure = _as_dict(validation.get("evidence_closure"))
    closure_issues = [_as_dict(row) for row in list(closure.get("issues") or []) if isinstance(row, dict)]
    validation_id = str(
        validation.get("validation_id") or source.get("source_id") or ""
    ).strip()
    level2_handoff = _build_level2_handoff(
        validation_id=validation_id,
        closure_issues=closure_issues,
        eligible=bool(eligibility.get("eligible")),
    )
    disclosures: dict[str, Any] = {
        "accepted_limits": list(level2_handoff["accepted_limits"]),
        "source_gaps": source_gaps,
        "provenance": [
            str(row.get("root_issue_id"))
            for row in closure_issues
            if str(row.get("root_issue_id") or "").strip()
        ],
    }
    if unstructured_triggers:
        disclosures["unstructured_monitoring_triggers"] = unstructured_triggers
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
        "can_refresh_observation": bool(observation_freshness.get("can_refresh")),
    }
    return {
        "schema_version": DECISION_BRIEF_SCHEMA_VERSION,
        "candidate": {
            "source_id": candidate_source_id,
            "validation_id": validation_id,
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
            "thesis": _build_thesis(
                strengths=strengths,
                weaknesses=weaknesses,
                source_gaps=source_gaps,
            ),
        },
        "evidence_confidence": evidence_confidence,
        "behavior_board": behavior_board,
        "character_profile": _build_character_profile(internal_observations),
        "review_pressure": _build_review_pressure(internal_observations),
        "strengths": strengths,
        "weaknesses": weaknesses,
        "monitoring_conditions": monitoring_conditions,
        "level2_handoff": level2_handoff,
        "decision_action": decision_action,
        "observation_freshness": observation_freshness,
        "disclosures": disclosures,
        "capabilities": capabilities,
    }


def build_final_review_decision_brief_snapshot(
    decision_brief: dict[str, Any],
    *,
    accepted_limit_acknowledgements: list[dict[str, str]] | None = None,
) -> dict[str, Any]:
    """Keep durable judgment and Monitoring fields without chart payload bulk."""

    brief = _as_dict(decision_brief)
    verdict = _as_dict(brief.get("verdict"))
    confidence = _as_dict(brief.get("evidence_confidence"))
    disclosures = _as_dict(brief.get("disclosures"))

    def unique_values(rows: list[Any], key: str) -> list[str]:
        values: list[str] = []
        for raw_row in rows:
            value = str(_as_dict(raw_row).get(key) or "").strip()
            if value and value not in values:
                values.append(value)
        return values

    monitoring_conditions = [
        {
            "observation_id": str(row.get("observation_id") or "").strip(),
            "title": str(row.get("title") or "").strip(),
            "threshold": str(row.get("threshold") or "").strip(),
            "cadence": str(row.get("cadence") or "").strip(),
            "re_review_action": str(row.get("re_review_action") or "").strip(),
        }
        for row in (
            _as_dict(raw_row)
            for raw_row in list(brief.get("monitoring_conditions") or [])
        )
        if str(row.get("observation_id") or "").strip()
    ]
    return {
        "schema_version": "decision_brief_snapshot_v1",
        "verdict": {
            "route": str(verdict.get("route") or "").strip(),
            "label": str(verdict.get("label") or "").strip(),
            "headline": str(verdict.get("headline") or "").strip(),
        },
        "evidence_confidence": {
            "value": _as_non_negative_int(confidence.get("value")),
            "basis": str(confidence.get("basis") or "").strip(),
        },
        "strength_observation_ids": unique_values(
            list(brief.get("strengths") or []),
            "observation_id",
        ),
        "weakness_observation_ids": unique_values(
            list(brief.get("weaknesses") or []),
            "observation_id",
        ),
        "monitoring_conditions": monitoring_conditions,
        "accepted_limit_root_issue_ids": unique_values(
            list(disclosures.get("accepted_limits") or []),
            "root_issue_id",
        ),
        "accepted_limit_acknowledgements": [
            {
                "root_issue_id": str(row.get("root_issue_id") or "").strip(),
                "decision": str(row.get("decision") or "").strip(),
            }
            for row in (
                _as_dict(raw_row)
                for raw_row in list(accepted_limit_acknowledgements or [])
            )
            if str(row.get("root_issue_id") or "").strip()
            and str(row.get("decision") or "").strip()
        ],
        "source_gaps": [
            str(value).strip()
            for value in list(disclosures.get("source_gaps") or [])
            if str(value).strip()
        ],
    }


__all__ = [
    "DECISION_BRIEF_ROUTE_PRESENTATION",
    "DECISION_BRIEF_SCHEMA_VERSION",
    "build_final_review_candidate_selector",
    "build_final_review_decision_brief",
    "build_final_review_decision_brief_snapshot",
    "validate_accepted_limit_acknowledgements",
]
