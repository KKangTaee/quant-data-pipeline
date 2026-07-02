from __future__ import annotations

from typing import Any


def _source_bucket(
    value: Any,
    *,
    unavailable_blocks: bool = True,
    caution_blocks: bool = True,
) -> str:
    normalized = str(value or "").strip().lower()
    if not normalized or normalized in {"normal", "ok", "pass", "passed", "fresh"}:
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
        "promotion_ok": promotion not in {"", "hold"},
        "execution_blocker_count": len(execution_blockers),
        "execution_review_count": len(execution_reviews),
        "validation_blocker_count": len(validation_blockers),
        "validation_review_count": len(validation_reviews),
    }


__all__ = ["build_next_step_readiness_evaluation"]
