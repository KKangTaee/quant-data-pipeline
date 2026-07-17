from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.backtest_handoff_readiness import (
    build_next_step_readiness_evaluation,
)


MIX_ROLE_OPTIONS = ("core", "growth", "defense", "satellite")
MIX_ROLE_LABELS = {
    "core": "Core",
    "growth": "Growth",
    "defense": "Defense",
    "satellite": "Satellite",
}


def infer_mix_role(strategy_name: str) -> str:
    """Infer a stable Level1 role for legacy role-less mixes."""

    normalized = str(strategy_name).lower()
    if "risk parity" in normalized:
        return "defense"
    if "gtaa" in normalized or "equal weight" in normalized:
        return "core"
    if "relative strength" in normalized or "momentum" in normalized:
        return "growth"
    return "satellite"


def build_mix_role_weight_rows(
    *,
    strategy_names: list[str],
    weights_percent: list[float],
    component_roles: list[str] | None,
) -> list[dict[str, object]]:
    """Pair Python-owned role and weight truth in strategy order."""

    roles = [str(role) for role in list(component_roles or [])]
    if len(roles) != len(strategy_names):
        roles = [infer_mix_role(name) for name in strategy_names]
    return [
        {
            "strategy_name": str(name),
            "role": role,
            "role_label": MIX_ROLE_LABELS.get(role, role),
            "weight_percent": float(weight),
            "valid": role in MIX_ROLE_OPTIONS and float(weight) >= 0.0,
        }
        for name, weight, role in zip(strategy_names, weights_percent, roles)
    ]


def _safe_int_value(value: Any) -> int:
    try:
        if value is None or value == "":
            return 0
        return int(float(value))
    except (TypeError, ValueError):
        return 0


def _safe_interval_months_from_meta(meta: dict[str, Any]) -> int:
    for key in ("rebalance_interval", "interval"):
        try:
            value = meta.get(key)
            if value in (None, ""):
                continue
            interval = int(float(value))
            if interval > 0:
                return interval
        except (TypeError, ValueError):
            continue
    return 0


def _build_cadence_alignment_assessment(
    *,
    meta: dict[str, Any],
    requested_end: Any,
    actual_end: Any,
    shortened_days: int,
) -> dict[str, Any]:
    if shortened_days <= 31:
        return {}
    strategy_label = " ".join(
        str(meta.get(key) or "")
        for key in ("strategy_key", "strategy_name", "preset_name")
    ).lower()
    if "gtaa" not in strategy_label:
        return {}
    option = str(meta.get("option") or "").strip().lower()
    if option != "month_end":
        return {}
    interval = _safe_interval_months_from_meta(meta)
    if interval <= 1:
        return {}

    actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
    requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
    if pd.isna(actual_end_ts) or pd.isna(requested_end_ts):
        return {}
    actual_anchor = actual_end_ts + pd.offsets.MonthEnd(0)
    next_expected_close = actual_anchor + pd.offsets.MonthEnd(interval)
    if requested_end_ts.date() > next_expected_close.date():
        return {}
    return {
        "strategy": meta.get("strategy_name")
        or meta.get("strategy_key")
        or "GTAA",
        "interval": interval,
        "option": option,
        "actual_anchor": str(actual_anchor.date()),
        "next_expected_close": str(next_expected_close.date()),
        "requested_end": str(requested_end_ts.date()),
        "shortened_days": shortened_days,
        "judgment": (
            f"GTAA interval={interval}, month_end 기준 다음 확정 row "
            f"{next_expected_close.date()} 전의 정상 cadence gap"
        ),
    }


def _build_component_data_trust_assessment(
    bundle: dict[str, Any],
) -> dict[str, Any]:
    meta = dict(bundle.get("meta") or {})
    result_df = bundle.get("result_df")
    price_freshness = dict(meta.get("price_freshness") or {})
    freshness_status = str(price_freshness.get("status") or "").strip().lower()
    excluded_tickers = list(meta.get("excluded_tickers") or [])
    malformed_price_rows = list(meta.get("malformed_price_rows") or [])
    warnings = list(meta.get("warnings") or [])
    requested_end = meta.get("end") or meta.get("requested_end") or meta.get(
        "input_end"
    )
    actual_end = meta.get("actual_result_end")
    if (
        not actual_end
        and isinstance(result_df, pd.DataFrame)
        and not result_df.empty
        and "Date" in result_df.columns
    ):
        actual_end = str(
            pd.to_datetime(result_df["Date"], errors="coerce").max().date()
        )
    actual_end_ts = pd.to_datetime(actual_end, errors="coerce")
    requested_end_ts = pd.to_datetime(requested_end, errors="coerce")
    period_shortened = (
        pd.notna(actual_end_ts)
        and pd.notna(requested_end_ts)
        and actual_end_ts.date() < requested_end_ts.date()
    )
    shortened_days = (
        (requested_end_ts.date() - actual_end_ts.date()).days
        if period_shortened
        else 0
    )
    cadence_alignment = _build_cadence_alignment_assessment(
        meta={
            **meta,
            "strategy_name": bundle.get("strategy_name")
            or meta.get("strategy_name"),
        },
        requested_end=requested_end,
        actual_end=actual_end,
        shortened_days=shortened_days,
    )
    data_blocked = freshness_status == "error" or (
        shortened_days > 31 and not cadence_alignment
    )
    data_warning = (
        period_shortened
        or freshness_status == "warning"
        or bool(excluded_tickers)
        or bool(malformed_price_rows)
        or bool(warnings)
    )
    return {
        "gate_status": "blocked"
        if data_blocked
        else "warning"
        if data_warning
        else "ok",
        "cadence_alignment": cadence_alignment,
    }


def build_weighted_mix_candidate_readiness_evaluation(
    weighted_bundle: dict[str, Any] | None,
    component_bundles: list[dict[str, Any]],
) -> dict[str, Any]:
    """Evaluate a weighted Mix as one Level1 candidate."""

    components = list(component_bundles or [])
    replay_ready = (
        isinstance(weighted_bundle, dict)
        and isinstance(weighted_bundle.get("summary_df"), pd.DataFrame)
        and not weighted_bundle["summary_df"].empty
        and isinstance(weighted_bundle.get("result_df"), pd.DataFrame)
        and not weighted_bundle["result_df"].empty
    )
    component_names = list(
        (weighted_bundle or {}).get("component_strategy_names") or []
    )
    input_weights = [
        float(weight)
        for weight in list(
            (weighted_bundle or {}).get("component_input_weights") or []
        )
        if weight is not None
    ]
    if not input_weights:
        input_weights = [
            round(float(weight) * 100.0, 4)
            for weight in list(
                (weighted_bundle or {}).get("component_weights") or []
            )
            if weight is not None
        ]
    target_weight_total = round(sum(input_weights), 4)
    positive_weight_count = sum(
        1 for weight in input_weights if float(weight) > 0.0
    )
    date_policy = str(
        (weighted_bundle or {}).get("date_policy")
        or dict((weighted_bundle or {}).get("meta") or {}).get("date_policy")
        or "-"
    )

    replay_score = 2.0 if replay_ready else 0.0
    replay_status = "PASS" if replay_ready else "FAIL"
    replay_judgment = (
        "weighted mix result가 생성됨"
        if replay_ready
        else "weighted mix result를 먼저 생성해야 함"
    )
    if abs(target_weight_total - 100.0) <= 0.01 and positive_weight_count >= 2:
        weight_status, weight_score = "PASS", 2.0
        weight_judgment = "2개 이상 구성 전략의 target weight 합계가 100%"
    elif abs(target_weight_total - 100.0) <= 0.01:
        weight_status, weight_score = "FAIL", 0.0
        weight_judgment = (
            "positive weight가 1개뿐이면 mix 후보가 아니라 단일 후보에 가까움"
        )
    elif positive_weight_count >= 2:
        weight_status, weight_score = "FAIL", 0.0
        weight_judgment = (
            "positive weight는 2개 이상이지만 target weight 합계가 100%가 아님"
        )
    else:
        weight_status, weight_score = "FAIL", 0.0
        weight_judgment = "2개 이상 구성 전략과 100% target weight가 필요함"

    data_rows = list(
        (weighted_bundle or {}).get("component_data_trust_rows") or []
    )
    assessments = [
        _build_component_data_trust_assessment(bundle) for bundle in components
    ]
    cadence_alignments = [
        dict(row.get("cadence_alignment") or {})
        for row in assessments
        if row.get("cadence_alignment")
    ]
    has_component_error = any(
        str(row.get("Price Freshness") or "").strip().lower() == "error"
        for row in data_rows
    ) or any(row.get("gate_status") == "blocked" for row in assessments)
    has_component_review = any(
        str(row.get("Interpretation") or "").strip()
        not in {"", "-", "눈에 띄는 데이터 이슈 없음"}
        or _safe_int_value(row.get("Warnings")) > 0
        or _safe_int_value(row.get("Excluded Tickers")) > 0
        or _safe_int_value(row.get("Malformed Tickers")) > 0
        for row in data_rows
    ) or any(row.get("gate_status") == "warning" for row in assessments)
    if not replay_ready:
        data_status, data_score = "FAIL", 0.0
        data_judgment = "mix result가 없어 component data trust를 확정할 수 없음"
    elif has_component_error:
        data_status, data_score = "FAIL", 0.0
        data_judgment = "구성 전략 데이터에 hard blocker가 있음"
    elif cadence_alignments:
        data_status, data_score = "CADENCE ALIGNED", 1.5
        data_judgment = "구성 전략 종료일 차이 중 정상 cadence로 보이는 항목이 있음"
    elif has_component_review:
        data_status, data_score = "REVIEW", 1.0
        data_judgment = "구성 전략 데이터 warning / 제외 ticker / 기간 확인 필요"
    else:
        data_status, data_score = "PASS", 2.0
        data_judgment = "구성 전략 data trust가 mix 생성을 막지 않음"

    component_rows: list[dict[str, Any]] = []
    blockers: list[str] = []
    reviews: list[str] = []
    component_scores: list[float] = []
    for bundle in components:
        strategy_name = str(
            bundle.get("strategy_name")
            or dict(bundle.get("meta") or {}).get("strategy_name")
            or "-"
        )
        meta = dict(bundle.get("meta") or {})
        readiness = build_next_step_readiness_evaluation(meta)
        component_scores.append(float(readiness.get("score") or 0.0))
        if not bool(readiness.get("can_move_to_compare")):
            blockers.extend(
                f"{strategy_name}: {reason}"
                for reason in readiness.get("blocking_reasons") or []
            )
        reviews.extend(
            f"{strategy_name}: {reason}"
            for reason in readiness.get("review_reasons") or []
        )
        component_rows.append(
            {
                "Component": strategy_name,
                "Promotion": meta.get("promotion_decision") or "-",
                "Readiness": readiness.get("verdict") or "-",
                "Score": readiness.get("score"),
                "Blockers": len(readiness.get("blocking_reasons") or []),
                "Review": len(readiness.get("review_reasons") or []),
            }
        )
    if not components:
        component_status, component_score = "FAIL", 0.0
        component_judgment = "구성 전략 실행 결과가 없음"
    elif blockers:
        component_status, component_score = "FAIL", 0.0
        component_judgment = "구성 전략 중 1차 후보 blocker가 있음"
    elif reviews:
        component_status = "REVIEW"
        component_score = min(
            4.0,
            round(
                (sum(component_scores) / max(len(component_scores), 1))
                / 10.0
                * 4.0,
                1,
            ),
        )
        component_judgment = "구성 전략은 이동 가능하지만 review 항목이 있음"
    else:
        component_status, component_score = "PASS", 4.0
        component_judgment = "구성 전략 1차 후보 판단이 mix handoff를 막지 않음"

    score = round(replay_score + weight_score + data_score + component_score, 1)
    hard_blocked = "FAIL" in {
        replay_status,
        weight_status,
        data_status,
        component_status,
    }
    can_send = not hard_blocked
    if (
        can_send
        and score >= 8.0
        and data_status == "PASS"
        and weight_status == "PASS"
        and component_status == "PASS"
    ):
        stage_status, tone = "PASS", "success"
        verdict = "PASS: mix 후보를 Practical Validation으로 보낼 수 있습니다."
        next_action = "mix 전체를 2차 실전성 검증 source로 등록합니다."
    elif can_send:
        stage_status, tone = "CONDITIONAL", "warning"
        verdict = (
            "CONDITIONAL: review 항목을 남기고 Practical Validation으로 보낼 수 있습니다."
        )
        next_action = (
            "Practical Validation에서 component warning과 weight / data trust 확인을 이어갑니다."
        )
    else:
        stage_status, tone = "HOLD", "error"
        verdict = "HOLD: mix 후보를 보내기 전에 blocker를 해결해야 합니다."
        next_action = (
            "weight 합계, component promotion, data trust blocker를 먼저 정리합니다."
        )

    blocking_reasons = []
    if replay_status == "FAIL":
        blocking_reasons.append(replay_judgment)
    if weight_status == "FAIL":
        blocking_reasons.append(weight_judgment)
    if data_status == "FAIL":
        blocking_reasons.append(data_judgment)
    blocking_reasons.extend(blockers)
    review_reasons = []
    if data_status in {"REVIEW", "CADENCE ALIGNED"}:
        review_reasons.append(data_judgment)
    review_reasons.extend(reviews)
    criteria_rows = [
        {
            "기준": "Mix Result",
            "상태": replay_status,
            "현재 값": "created" if replay_ready else "missing",
            "점수": f"{replay_score:g} / 2",
            "판단": replay_judgment,
        },
        {
            "기준": "Weight Discipline",
            "상태": weight_status,
            "현재 값": f"{target_weight_total:.1f}% / positive {positive_weight_count}",
            "점수": f"{weight_score:g} / 2",
            "판단": weight_judgment,
        },
        {
            "기준": "Component Data Trust",
            "상태": data_status,
            "현재 값": f"{len(data_rows)}개 component row",
            "점수": f"{data_score:g} / 2",
            "판단": data_judgment,
        },
        {
            "기준": "Component 1차 후보 판단",
            "상태": component_status,
            "현재 값": f"{len(components)}개 component",
            "점수": f"{component_score:g} / 4",
            "판단": component_judgment,
        },
    ]
    return {
        "score": score,
        "stage_status": stage_status,
        "verdict": verdict,
        "tone": tone,
        "next_action": next_action,
        "can_send_to_practical_validation": can_send,
        "component_count": len(component_names),
        "target_weight_total": target_weight_total,
        "positive_weight_count": positive_weight_count,
        "date_policy": date_policy,
        "criteria_rows": criteria_rows,
        "component_readiness_rows": component_rows,
        "data_rows": data_rows,
        "cadence_alignments": cadence_alignments,
        "blocking_reasons": blocking_reasons,
        "review_reasons": review_reasons,
    }


def weighted_strategy_role_flags(strategy_names: list[str]) -> dict[str, bool]:
    """Detect common portfolio mix roles from strategy display names."""

    normalized_names = [str(name).lower() for name in strategy_names]
    return {
        "gtaa": any("gtaa" in name for name in normalized_names),
        "equal_weight": any("equal weight" in name for name in normalized_names),
    }


__all__ = [
    "MIX_ROLE_LABELS",
    "MIX_ROLE_OPTIONS",
    "build_mix_role_weight_rows",
    "build_weighted_mix_candidate_readiness_evaluation",
    "infer_mix_role",
    "weighted_strategy_role_flags",
]
