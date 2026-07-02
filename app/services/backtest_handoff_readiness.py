from __future__ import annotations

from typing import Any


_PASS_STATUSES = {"", "normal", "ok", "pass", "passed", "fresh"}


def _source_bucket(
    value: Any,
    *,
    unavailable_blocks: bool = True,
    caution_blocks: bool = True,
) -> str:
    normalized = str(value or "").strip().lower()
    if normalized in _PASS_STATUSES:
        return "pass"
    if normalized in {"error", "missing"}:
        return "block"
    if normalized == "caution":
        return "block" if caution_blocks else "review"
    if normalized == "unavailable":
        return "block" if unavailable_blocks else "review"
    if normalized in {"watch", "warning"}:
        return "review"
    return "review"


def _signal_row(
    *,
    group: str,
    signal: str,
    status: Any,
    role: str,
    effect: str,
    meaning: str,
    next_surface: str,
    source_key: str,
) -> dict[str, Any]:
    normalized = str(status or "").strip().lower()
    return {
        "group": group,
        "signal": signal,
        "status": normalized or "normal",
        "role": role,
        "effect": effect,
        "meaning": meaning,
        "next_surface": next_surface,
        "source_key": source_key,
    }


def _status_signal_effect(
    value: Any,
    *,
    unavailable_blocks: bool = True,
    caution_blocks: bool = True,
) -> str:
    bucket = _source_bucket(
        value,
        unavailable_blocks=unavailable_blocks,
        caution_blocks=caution_blocks,
    )
    if bucket == "block":
        return "block"
    if bucket == "review":
        return "review"
    return "pass"


def build_policy_signal_inventory(meta: dict[str, Any]) -> dict[str, Any]:
    """Classify Backtest policy signals by how they should be used in the workflow."""
    promotion = str(meta.get("promotion_decision") or "").strip().lower()
    freshness_status = str((meta.get("price_freshness") or {}).get("status") or "").strip().lower()
    turnover_status = str(meta.get("turnover_estimation_status") or "").strip().lower()
    net_cost_curve_status = str(meta.get("net_cost_curve_status") or "").strip().lower()
    transaction_cost_bps = float(meta.get("transaction_cost_bps") or 0.0)

    rows: list[dict[str, Any]] = []
    promotion_effect = "block" if promotion in {"", "hold"} else "pass"
    rows.append(
        _signal_row(
            group="Promotion",
            signal="Promotion Decision",
            status=promotion or "missing",
            role="entry_gate",
            effect=promotion_effect,
            meaning="Backtest 1차 후보로 다음 검증에 넘길 수 있는지 보는 신호",
            next_surface="Backtest Analysis",
            source_key="promotion_decision",
        )
    )

    status_specs: list[dict[str, Any]] = [
        {
            "group": "Data Trust",
            "signal": "Price Freshness",
            "status": freshness_status,
            "role": "entry_gate",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "결과가 해석 가능한 최신 가격 범위에서 계산됐는지 확인",
            "next_surface": "Backtest Analysis",
            "source_key": "price_freshness.status",
        },
        {
            "group": "Execution Source",
            "signal": "Liquidity Policy",
            "status": meta.get("liquidity_policy_status"),
            "role": "execution_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "유동성 필터와 clean coverage가 실전 해석에 충분한지 확인",
            "next_surface": "Practical Validation",
            "source_key": "liquidity_policy_status",
        },
        {
            "group": "Execution Source",
            "signal": "ETF Operability",
            "status": meta.get("etf_operability_status"),
            "role": "execution_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "ETF AUM / spread / provider profile 근거가 운용 가능성 해석에 충분한지 확인",
            "next_surface": "Practical Validation",
            "source_key": "etf_operability_status",
        },
        {
            "group": "Validation Source",
            "signal": "Benchmark Availability",
            "status": "missing" if not bool(meta.get("benchmark_available")) else "normal",
            "role": "validation_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "후속 검증에서 기준선과 비교할 수 있는 benchmark curve 존재 여부",
            "next_surface": "Practical Validation",
            "source_key": "benchmark_available",
        },
        {
            "group": "Validation Source",
            "signal": "Validation",
            "status": meta.get("validation_status"),
            "role": "validation_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "benchmark-relative drawdown / underperformance 진단 상태",
            "next_surface": "Practical Validation",
            "source_key": "validation_status",
        },
        {
            "group": "Validation Source",
            "signal": "Benchmark Policy",
            "status": meta.get("benchmark_policy_status"),
            "role": "validation_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "benchmark coverage와 net CAGR spread가 정책 기준을 충족하는지 확인",
            "next_surface": "Practical Validation",
            "source_key": "benchmark_policy_status",
        },
        {
            "group": "Validation Source",
            "signal": "Validation Policy",
            "status": meta.get("validation_policy_status"),
            "role": "validation_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "rolling underperformance 정책 기준을 충족하는지 확인",
            "next_surface": "Practical Validation",
            "source_key": "validation_policy_status",
        },
        {
            "group": "Validation Source",
            "signal": "Portfolio Guardrail Policy",
            "status": meta.get("guardrail_policy_status"),
            "role": "validation_source",
            "unavailable_blocks": True,
            "caution_blocks": True,
            "meaning": "전략 낙폭과 benchmark 대비 낙폭 차이가 방어 기준 안에 있는지 확인",
            "next_surface": "Practical Validation",
            "source_key": "guardrail_policy_status",
        },
        {
            "group": "Validation Review",
            "signal": "Rolling Review",
            "status": meta.get("rolling_review_status"),
            "role": "practical_validation_review",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "최근 구간 약화 여부를 2차에서 우선 확인할 review 신호",
            "next_surface": "Practical Validation",
            "source_key": "rolling_review_status",
        },
        {
            "group": "Validation Review",
            "signal": "Split-Period Check",
            "status": meta.get("out_of_sample_review_status"),
            "role": "practical_validation_review",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "전후반 구간 성과 악화 여부를 2차에서 확인할 review 신호",
            "next_surface": "Practical Validation",
            "source_key": "out_of_sample_review_status",
        },
    ]

    for spec in status_specs:
        status = spec["status"]
        effect = _status_signal_effect(
            status,
            unavailable_blocks=bool(spec["unavailable_blocks"]),
            caution_blocks=bool(spec["caution_blocks"]),
        )
        rows.append(
            _signal_row(
                group=str(spec["group"]),
                signal=str(spec["signal"]),
                status=status,
                role=str(spec["role"]),
                effect=effect,
                meaning=str(spec["meaning"]),
                next_surface=str(spec["next_surface"]),
                source_key=str(spec["source_key"]),
            )
        )

    if transaction_cost_bps > 0.0 and turnover_status and turnover_status != "estimated_from_holdings":
        rows.append(
            _signal_row(
                group="Execution Review",
                signal="Turnover Estimate",
                status=turnover_status,
                role="practical_validation_review",
                effect="review",
                meaning="비용 해석에 필요한 holdings 기반 turnover 근거 부족 여부",
                next_surface="Practical Validation",
                source_key="turnover_estimation_status",
            )
        )
    if net_cost_curve_status == "applied_without_turnover_estimate":
        rows.append(
            _signal_row(
                group="Execution Review",
                signal="Cost Curve",
                status=net_cost_curve_status,
                role="practical_validation_review",
                effect="review",
                meaning="net cost curve가 turnover 추정 없이 적용됐는지 여부",
                next_surface="Practical Validation",
                source_key="net_cost_curve_status",
            )
        )

    for signal, key in [
        ("Suggested Route", "shortlist_status"),
        ("Execution Preview", "deployment_readiness_status"),
        ("Monitoring Preview", "monitoring_status"),
    ]:
        value = meta.get(key)
        if value:
            rows.append(
                _signal_row(
                    group="Context",
                    signal=signal,
                    status=value,
                    role="context_only",
                    effect="context",
                    meaning="후속 설명용 preview이며 2차 source 등록 버튼을 직접 막지 않음",
                    next_surface="Reference / Practical Validation",
                    source_key=key,
                )
            )

    counts = {
        "block": sum(1 for row in rows if row["effect"] == "block"),
        "review": sum(1 for row in rows if row["effect"] == "review"),
        "pass": sum(1 for row in rows if row["effect"] == "pass"),
        "context": sum(1 for row in rows if row["effect"] == "context"),
    }
    return {
        "schema_version": "backtest_policy_signal_inventory_v1",
        "rows": rows,
        "counts": counts,
        "blocker_rows": [row for row in rows if row["effect"] == "block"],
        "review_rows": [row for row in rows if row["effect"] == "review"],
        "context_rows": [row for row in rows if row["effect"] == "context"],
    }


def _collect_source_reasons(
    specs: list[tuple[str, Any, bool, bool]],
) -> tuple[list[str], list[str]]:
    blockers: list[str] = []
    reviews: list[str] = []
    for label, status, unavailable_blocks, caution_blocks in specs:
        normalized = str(status or "").strip().lower()
        bucket = _source_bucket(
            normalized,
            unavailable_blocks=unavailable_blocks,
            caution_blocks=caution_blocks,
        )
        if bucket == "block":
            blockers.append(f"{label}: {normalized or '-'}")
        elif bucket == "review":
            reviews.append(f"{label}: {normalized or '-'}")
    return blockers, reviews


def build_next_step_readiness_evaluation(meta: dict[str, Any]) -> dict[str, Any]:
    """Evaluate whether a Backtest result can be handed off to Practical Validation."""
    promotion = str(meta.get("promotion_decision") or "").strip().lower()
    freshness_status = str((meta.get("price_freshness") or {}).get("status") or "").strip().lower()
    turnover_status = str(meta.get("turnover_estimation_status") or "").strip().lower()
    net_cost_curve_status = str(meta.get("net_cost_curve_status") or "").strip().lower()
    transaction_cost_bps = float(meta.get("transaction_cost_bps") or 0.0)

    execution_specs: list[tuple[str, Any, bool, bool]] = [
        ("Liquidity Policy", meta.get("liquidity_policy_status"), True, True),
        ("ETF Operability", meta.get("etf_operability_status"), True, True),
        ("Price Freshness", freshness_status, True, True),
    ]
    validation_specs: list[tuple[str, Any, bool, bool]] = [
        ("Benchmark 비교", "missing" if not bool(meta.get("benchmark_available")) else "", True, True),
        ("Validation", meta.get("validation_status"), True, True),
        ("Benchmark Policy", meta.get("benchmark_policy_status"), True, True),
        ("Validation Policy", meta.get("validation_policy_status"), True, True),
        ("Portfolio Guardrail Policy", meta.get("guardrail_policy_status"), True, True),
        # Backtest-level recent/split checks are useful warning signals, but they are not formal holdout validation.
        ("Rolling Review", meta.get("rolling_review_status"), False, False),
        ("Split-Period Check", meta.get("out_of_sample_review_status"), False, False),
    ]
    execution_blockers, execution_reviews = _collect_source_reasons(execution_specs)
    validation_blockers, validation_reviews = _collect_source_reasons(validation_specs)
    if transaction_cost_bps > 0.0 and turnover_status and turnover_status != "estimated_from_holdings":
        execution_reviews.append(f"Turnover Estimate: {turnover_status}")
    if net_cost_curve_status == "applied_without_turnover_estimate":
        execution_reviews.append("Cost Curve: turnover estimate unavailable")

    if promotion == "real_money_candidate":
        promotion_score = 4.0
        promotion_judgment = "강한 handoff policy signal"
    elif promotion == "production_candidate":
        promotion_score = 3.0
        promotion_judgment = "비교 가능, 추가 검토 필요"
    elif promotion and promotion != "hold":
        promotion_score = 2.0
        promotion_judgment = "비교 가능성은 있으나 보수적 확인 필요"
    else:
        promotion_score = 0.0
        promotion_judgment = "hold 해결 전에는 다음 단계 보류"

    if execution_blockers:
        execution_score = 0.0
        execution_judgment = "실행 원천 blocker가 남아 있음"
    elif execution_reviews:
        execution_score = 2.0
        execution_judgment = "실행 부담은 검토 가능하지만 확인 항목 있음"
    else:
        execution_score = 3.0
        execution_judgment = "실행 부담 원천 지표가 양호함"

    if validation_blockers:
        validation_score = 0.0
        validation_judgment = "검증 원천 blocker가 남아 있음"
    elif validation_reviews:
        validation_score = 2.0
        validation_judgment = "검증 근거는 있으나 후속 확인 필요"
    else:
        validation_score = 3.0
        validation_judgment = "검증 원천 지표가 양호함"

    score = round(promotion_score + execution_score + validation_score, 1)
    can_move_to_compare = (
        promotion not in {"", "hold"}
        and not execution_blockers
        and not validation_blockers
    )

    if can_move_to_compare and score >= 8.0:
        verdict = "후보 검토 진행 가능"
        tone = "success"
        route_label = "Portfolio Mix Builder 또는 Practical Validation"
        next_action = "Portfolio Mix Builder에서 다른 후보와 조합하거나 Practical Validation으로 보내 검증 근거를 확인합니다."
    elif can_move_to_compare:
        verdict = "후보 검토 가능, 개선 항목 동시 확인"
        tone = "warning"
        route_label = "조건부 후보 검토"
        next_action = "Portfolio Mix Builder 또는 Practical Validation으로 넘기기 전에 watch / preview 항목을 함께 확인합니다."
    else:
        verdict = "후보 보류: blocker 먼저 해결"
        tone = "error"
        route_label = "Hold / Review"
        next_action = "Hold 해결 가이드, 실행 부담 preview, 검토 근거의 caution 항목을 먼저 정리합니다."

    blocking_reasons: list[str] = []
    if promotion in {"", "hold"}:
        blocking_reasons.append("Promotion Decision이 hold이거나 비어 있음")
    blocking_reasons.extend(execution_blockers)
    blocking_reasons.extend(validation_blockers)

    review_reasons: list[str] = execution_reviews + validation_reviews

    criteria_rows = [
        {
            "기준": "Promotion Decision",
            "현재 값": promotion or "-",
            "점수": f"{promotion_score:g} / 4",
            "판단": promotion_judgment,
        },
        {
            "기준": "Execution Source Checks",
            "현재 값": "정상" if not execution_blockers and not execution_reviews else f"block {len(execution_blockers)} / review {len(execution_reviews)}",
            "점수": f"{execution_score:g} / 3",
            "판단": execution_judgment,
        },
        {
            "기준": "Validation Source Checks",
            "현재 값": "정상" if not validation_blockers and not validation_reviews else f"block {len(validation_blockers)} / review {len(validation_reviews)}",
            "점수": f"{validation_score:g} / 3",
            "판단": validation_judgment,
        },
    ]

    return {
        "score": score,
        "verdict": verdict,
        "tone": tone,
        "route_label": route_label,
        "next_action": next_action,
        "can_move_to_compare": can_move_to_compare,
        "criteria_rows": criteria_rows,
        "blocking_reasons": blocking_reasons,
        "review_reasons": review_reasons,
        "execution_blockers": execution_blockers,
        "execution_reviews": execution_reviews,
        "validation_blockers": validation_blockers,
        "validation_reviews": validation_reviews,
        "promotion_ok": promotion not in {"", "hold"},
        "execution_blocker_count": len(execution_blockers),
        "execution_review_count": len(execution_reviews),
        "validation_blocker_count": len(validation_blockers),
        "validation_review_count": len(validation_reviews),
    }


def _gate_group(
    *,
    label: str,
    pass_value: str,
    blockers: list[str],
    reviews: list[str],
    block_value: str | None = None,
) -> dict[str, Any]:
    if blockers:
        return {
            "label": label,
            "value": block_value or f"block {len(blockers)}",
            "tone": "danger",
            "status": "block",
            "blockers": blockers,
            "reviews": reviews,
        }
    if reviews:
        return {
            "label": label,
            "value": f"review {len(reviews)}",
            "tone": "warning",
            "status": "review",
            "blockers": blockers,
            "reviews": reviews,
        }
    return {
        "label": label,
        "value": pass_value,
        "tone": "positive",
        "status": "pass",
        "blockers": blockers,
        "reviews": reviews,
    }


def build_handoff_gate_summary(meta: dict[str, Any]) -> dict[str, Any]:
    """Build a grouped, user-facing handoff gate summary from result metadata."""
    evaluation = build_next_step_readiness_evaluation(meta)
    promotion_ok = bool(evaluation.get("promotion_ok"))
    promotion_blockers = [] if promotion_ok else ["Promotion signal이 보류 상태입니다. Promotion / policy 기준을 보강한 뒤 다시 실행하세요."]
    execution_blockers = [str(item) for item in list(evaluation.get("execution_blockers") or [])]
    execution_reviews = [str(item) for item in list(evaluation.get("execution_reviews") or [])]
    validation_blockers = [str(item) for item in list(evaluation.get("validation_blockers") or [])]
    validation_reviews = [str(item) for item in list(evaluation.get("validation_reviews") or [])]

    gate_groups = [
        _gate_group(
            label="Promotion",
            pass_value="통과",
            blockers=promotion_blockers,
            reviews=[],
            block_value="보류",
        ),
        _gate_group(
            label="실행 원천",
            pass_value="통과",
            blockers=execution_blockers,
            reviews=execution_reviews,
        ),
        _gate_group(
            label="검증 원천",
            pass_value="통과",
            blockers=validation_blockers,
            reviews=validation_reviews,
        ),
    ]

    action_items: list[str] = []
    if promotion_blockers:
        action_items.append(promotion_blockers[0])
    if execution_blockers:
        action_items.append(f"실행 원천 blocker {len(execution_blockers)}개를 먼저 해결하세요.")
    elif execution_reviews:
        action_items.append(f"실행 원천 review {len(execution_reviews)}개는 Practical Validation에서 비용 / 유동성 근거로 확인하세요.")
    if validation_blockers:
        action_items.append(f"검증 원천 blocker {len(validation_blockers)}개를 먼저 해결하세요.")
    elif validation_reviews:
        action_items.append(f"검증 원천 review {len(validation_reviews)}개는 Practical Validation에서 근거를 확인하세요.")
    if not action_items:
        action_items.append("막는 항목 없음")

    if not bool(evaluation.get("can_move_to_compare")):
        reason_title = "먼저 해결할 항목"
    elif action_items == ["막는 항목 없음"]:
        reason_title = "상태"
    else:
        reason_title = "다음 단계 확인 항목"

    return {
        "can_submit": bool(evaluation.get("can_move_to_compare")),
        "gate_groups": gate_groups,
        "action_items": action_items,
        "reason_title": reason_title,
        "evaluation": evaluation,
    }


__all__ = [
    "build_handoff_gate_summary",
    "build_next_step_readiness_evaluation",
    "build_policy_signal_inventory",
]
