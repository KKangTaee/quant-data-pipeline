from __future__ import annotations

from typing import Any


_PASS_STATUSES = {"", "normal", "ok", "pass", "passed", "fresh"}

_POLICY_SIGNAL_DISPLAY_COPY: dict[str, dict[str, Any]] = {
    "Promotion Decision": {
        "checked_evidence": "promotion_decision 생성 여부와 source 등록 차단 여부",
        "plain_explanation": "이 결과를 2차 검증 source로 넘길지, 아니면 승격 전 보강이 필요한지 구분합니다.",
        "checked_items": [
            {"label": "Promotion Decision", "detail": "runtime이 만든 승격 판단 값"},
            {"label": "Entry Blocker", "detail": "source 등록을 즉시 막는 hard blocker 여부"},
            {"label": "Review Reason", "detail": "hold라면 Practical Validation에 넘겨 확인할 이유"},
        ],
        "pass_note": "Practical Validation source 등록을 막는 promotion blocker가 없습니다.",
        "review_note": "hold 사유는 source와 함께 Practical Validation의 2차 확인 큐로 전달합니다.",
        "block_note": "Backtest를 다시 실행하거나 promotion signal 생성 경로를 먼저 확인해야 합니다.",
    },
    "Price Freshness": {
        "checked_evidence": "DB 가격 최신일, 계산 기준일, 결과 기간, 결측 / 비정상 가격 row",
        "plain_explanation": "백테스트 성과가 해석 가능한 최신 가격 범위에서 계산됐는지 확인합니다.",
        "checked_items": [
            {"label": "Effective Trading End", "detail": "결과가 실제로 계산된 마지막 거래일"},
            {"label": "Common Latest Price", "detail": "구성 종목이 함께 가진 공통 최신 가격일"},
            {"label": "Malformed / Missing Rows", "detail": "가격 결측이나 비정상 row로 해석이 깨지는지"},
        ],
        "pass_note": "결과가 해석 가능한 최신 가격 범위에서 계산됐습니다.",
        "review_note": "요청 종료일과 실제 계산 기준일 차이를 Practical Validation에서 이어서 확인합니다.",
        "block_note": "가격 최신성 또는 결측 가격 row를 먼저 해결해야 source 등록이 가능합니다.",
    },
    "Liquidity Policy": {
        "checked_evidence": "유동성 필터, clean coverage, 실전 해석에 필요한 거래 가능성 근거",
        "plain_explanation": "이 전략이 고른 종목들이 너무 거래가 얇아서 실전 운용 해석이 깨지지 않는가를 봅니다.",
        "checked_items": [
            {"label": "Min Avg Dollar Volume 20D", "detail": "최근 20거래일 평균 거래대금 필터"},
            {"label": "Liquidity Clean Coverage", "detail": "리밸런싱 시점 중 유동성 문제 없이 통과한 비율"},
            {"label": "Liquidity Excluded Rows", "detail": "유동성 필터 때문에 제외된 리밸런싱 row 수"},
        ],
        "pass_note": "유동성 원천이 source 등록을 막지 않는 상태입니다.",
        "review_note": "유동성 부담은 Practical Validation에서 provider / coverage 근거와 함께 확인합니다.",
        "block_note": "유동성 원천이 source 등록을 막는 상태입니다. 가격 / universe 근거를 먼저 보강하세요.",
    },
    "ETF Operability": {
        "checked_evidence": "ETF AUM, spread, provider profile, 운용 가능성 근거 상태",
        "plain_explanation": "ETF를 실제 운용 후보로 볼 때 AUM, 스프레드, provider 근거가 부족하지 않은지 봅니다.",
        "checked_items": [
            {"label": "ETF AUM", "detail": "운용자산 규모가 최소 선호 기준보다 낮은지"},
            {"label": "Spread / Tradability", "detail": "매수매도 스프레드와 거래 가능성 근거"},
            {"label": "Provider Profile", "detail": "운용사 / ETF 기본 정보가 충분히 연결됐는지"},
        ],
        "pass_note": "ETF 운용 가능성 근거가 source 등록을 막지 않습니다.",
        "review_note": "ETF 운용 가능성은 Practical Validation에서 provider evidence로 확인합니다.",
        "block_note": "ETF 운용 가능성 근거가 부족해 source 등록 전 보강이 필요합니다.",
    },
    "Benchmark Availability": {
        "checked_evidence": "후속 검증에서 비교할 benchmark curve 존재 여부",
        "plain_explanation": "전략이 잘한 것인지 비교하려면 같은 기간에 비교할 benchmark curve가 있는지 확인합니다.",
        "checked_items": [
            {"label": "Benchmark Ticker", "detail": "전략과 비교할 기준 ticker 또는 후보 benchmark"},
            {"label": "Benchmark Curve", "detail": "비교 가능한 benchmark equity curve 존재 여부"},
            {"label": "Period Match", "detail": "후속 검증에서 같은 기간으로 비교할 수 있는지"},
        ],
        "pass_note": "Practical Validation에서 기준선 비교를 이어갈 수 있습니다.",
        "review_note": "benchmark 비교 가능성은 Practical Validation에서 coverage와 함께 확인합니다.",
        "block_note": "benchmark curve가 없어 후속 검증 source 등록 전 기준선을 보강해야 합니다.",
    },
    "Validation": {
        "checked_evidence": "benchmark-relative drawdown / underperformance 진단 상태",
        "plain_explanation": "성과가 좋아 보여도 benchmark 대비 낙폭이나 반복 부진 구간이 과한지 먼저 봅니다.",
        "checked_items": [
            {"label": "Relative Drawdown", "detail": "benchmark와 비교했을 때 낙폭이 과한지"},
            {"label": "Underperformance", "detail": "반복적으로 benchmark에 밀리는 구간이 있는지"},
            {"label": "Validation Status", "detail": "runtime이 요약한 기본 검증 상태"},
        ],
        "pass_note": "기본 validation 진단이 source 등록을 막지 않는 상태입니다.",
        "review_note": "낙폭 / 부진 구간은 Practical Validation에서 상세 검증으로 이어서 확인합니다.",
        "block_note": "validation blocker를 해소한 뒤 source 등록을 다시 시도해야 합니다.",
    },
    "Benchmark Policy": {
        "checked_evidence": "benchmark coverage와 net CAGR spread 정책 기준",
        "plain_explanation": "benchmark와 비교할 데이터가 충분하고, 비용 반영 후 초과 성과가 최소 기준을 넘는지 봅니다.",
        "checked_items": [
            {"label": "Benchmark Row Coverage", "detail": "전략 결과 기간 중 benchmark 비교 가능 row 비율"},
            {"label": "Net CAGR Spread", "detail": "비용 반영 후 benchmark 대비 연환산 수익률 차이"},
            {"label": "Policy Threshold", "detail": "비교 가능성과 초과 성과의 최소 정책 기준"},
        ],
        "pass_note": "benchmark 정책 기준이 source 등록을 막지 않습니다.",
        "review_note": "benchmark 정책 여유는 Practical Validation에서 기준선 parity와 함께 확인합니다.",
        "block_note": "benchmark 정책 기준 미충족 항목을 먼저 보강해야 합니다.",
    },
    "Validation Policy": {
        "checked_evidence": "rolling underperformance 정책 기준",
        "plain_explanation": "특정 짧은 구간만 좋은 전략인지 보기 위해 rolling 부진 비율과 최악 구간을 확인합니다.",
        "checked_items": [
            {"label": "Rolling Underperformance Share", "detail": "rolling 구간 중 benchmark에 밀린 비율"},
            {"label": "Worst Rolling Excess Return", "detail": "가장 나빴던 rolling 초과 수익률"},
            {"label": "Observation Count", "detail": "rolling 판단에 사용된 표본 수"},
        ],
        "pass_note": "rolling underperformance 정책이 source 등록을 막지 않습니다.",
        "review_note": "rolling 부진 여부는 Practical Validation의 robustness / temporal 검증에서 확인합니다.",
        "block_note": "rolling underperformance 정책 blocker를 먼저 해결해야 합니다.",
    },
    "Portfolio Guardrail Policy": {
        "checked_evidence": "전략 낙폭과 benchmark 대비 낙폭 차이의 방어 기준",
        "plain_explanation": "전략의 최대 낙폭과 benchmark 대비 낙폭 차이가 방어 기준 안에 있는지 확인합니다.",
        "checked_items": [
            {"label": "Strategy Maximum Drawdown", "detail": "전략 자체의 최대 낙폭"},
            {"label": "Drawdown Gap vs Benchmark", "detail": "benchmark 대비 낙폭 차이"},
            {"label": "Guardrail Threshold", "detail": "낙폭이 허용 범위 안에 있는지 보는 정책 기준"},
        ],
        "pass_note": "낙폭 guardrail이 source 등록을 막지 않습니다.",
        "review_note": "낙폭 방어 여유는 Practical Validation의 guardrail 근거에서 이어서 확인합니다.",
        "block_note": "guardrail 기준을 벗어난 낙폭 근거를 먼저 확인해야 합니다.",
    },
    "Rolling Review": {
        "checked_evidence": "최근 구간 성과 약화 여부",
        "pass_note": "최근 구간 review 신호가 source 등록을 막지 않습니다.",
        "review_note": "최근 구간 약화 여부를 Practical Validation에서 우선 확인합니다.",
        "block_note": "최근 구간 blocker를 먼저 확인해야 합니다.",
    },
    "Split-Period Check": {
        "checked_evidence": "전반 / 후반 구간 성과 악화 여부",
        "pass_note": "전후반 구간 점검이 source 등록을 막지 않습니다.",
        "review_note": "전후반 구간 악화 여부를 Practical Validation에서 확인합니다.",
        "block_note": "전후반 구간 blocker를 먼저 확인해야 합니다.",
    },
    "Turnover Estimate": {
        "checked_evidence": "비용 해석에 필요한 holdings 기반 turnover 추정 근거",
        "pass_note": "turnover 근거가 source 등록을 막지 않습니다.",
        "review_note": "비용 해석 전에 turnover 추정 근거를 Practical Validation에서 확인합니다.",
        "block_note": "turnover 근거를 먼저 보강해야 합니다.",
    },
    "Cost Curve": {
        "checked_evidence": "net cost curve 적용 방식과 turnover 추정 결합 여부",
        "pass_note": "cost curve 근거가 source 등록을 막지 않습니다.",
        "review_note": "net cost curve가 충분한 turnover 근거와 연결됐는지 Practical Validation에서 확인합니다.",
        "block_note": "cost curve 근거를 먼저 보강해야 합니다.",
    },
}


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
    row = {
        "group": group,
        "signal": signal,
        "status": normalized or "normal",
        "role": role,
        "effect": effect,
        "meaning": meaning,
        "next_surface": next_surface,
        "source_key": source_key,
    }
    copy = _POLICY_SIGNAL_DISPLAY_COPY.get(signal, {})
    checked_items = copy.get("checked_items")
    row.update(
        {
            "checked_evidence": copy.get("checked_evidence", meaning),
            "plain_explanation": copy.get("plain_explanation", meaning),
            "checked_items": [
                dict(item)
                for item in checked_items
                if isinstance(item, dict)
            ]
            if isinstance(checked_items, list)
            else [],
            "pass_note": copy.get("pass_note", meaning),
            "review_note": copy.get("review_note", meaning),
            "block_note": copy.get("block_note", meaning),
        }
    )
    return row


def _policy_signal_stage(row: dict[str, Any]) -> str:
    role = str(row.get("role") or "")
    effect = str(row.get("effect") or "")
    if effect == "context" or role == "context_only":
        return "context"
    if effect == "review":
        return "second_stage"
    if role == "practical_validation_review":
        return "second_stage"
    return "first_stage"


def _policy_signal_display_detail(row: dict[str, Any]) -> str:
    effect = str(row.get("effect") or "")
    if effect == "block":
        return str(row.get("block_note") or row.get("meaning") or "")
    if effect == "review":
        return str(row.get("review_note") or row.get("meaning") or "")
    if effect == "pass":
        return str(row.get("pass_note") or row.get("meaning") or "")
    return str(row.get("meaning") or "")


def _enrich_policy_signal_rows(rows: list[dict[str, Any]]) -> None:
    for row in rows:
        stage = _policy_signal_stage(row)
        row["stage_owner"] = stage
        row["display_detail"] = _policy_signal_display_detail(row)


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
    if not promotion:
        promotion_effect = "block"
    elif promotion == "hold":
        promotion_effect = "review"
    else:
        promotion_effect = "pass"
    rows.append(
        _signal_row(
            group="Promotion",
            signal="Promotion Decision",
            status=promotion or "missing",
            role="entry_gate",
            effect=promotion_effect,
            meaning="2차 검증으로 보낼 source인지와 실전 승격 전 보강이 필요한지 구분하는 신호",
            next_surface="Backtest Analysis / Practical Validation",
            source_key="promotion_decision",
        )
    )

    status_specs: list[dict[str, Any]] = [
        {
            "group": "Data Trust",
            "signal": "Price Freshness",
            "status": freshness_status,
            "role": "entry_gate",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "결과가 해석 가능한 최신 가격 범위에서 계산됐는지 확인",
            "next_surface": "Backtest Analysis",
            "source_key": "price_freshness.status",
        },
        {
            "group": "Execution Source",
            "signal": "Liquidity Policy",
            "status": meta.get("liquidity_policy_status"),
            "role": "execution_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "유동성 필터와 clean coverage가 실전 해석에 충분한지 확인",
            "next_surface": "Practical Validation",
            "source_key": "liquidity_policy_status",
        },
        {
            "group": "Execution Source",
            "signal": "ETF Operability",
            "status": meta.get("etf_operability_status"),
            "role": "execution_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "ETF AUM / spread / provider profile 근거가 운용 가능성 해석에 충분한지 확인",
            "next_surface": "Practical Validation",
            "source_key": "etf_operability_status",
        },
        {
            "group": "Validation Source",
            "signal": "Benchmark Availability",
            "status": "missing" if not bool(meta.get("benchmark_available")) else "normal",
            "role": "validation_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "후속 검증에서 기준선과 비교할 수 있는 benchmark curve 존재 여부",
            "next_surface": "Practical Validation",
            "source_key": "benchmark_available",
        },
        {
            "group": "Validation Source",
            "signal": "Validation",
            "status": meta.get("validation_status"),
            "role": "validation_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "benchmark-relative drawdown / underperformance 진단 상태",
            "next_surface": "Practical Validation",
            "source_key": "validation_status",
        },
        {
            "group": "Validation Source",
            "signal": "Benchmark Policy",
            "status": meta.get("benchmark_policy_status"),
            "role": "validation_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "benchmark coverage와 net CAGR spread가 정책 기준을 충족하는지 확인",
            "next_surface": "Practical Validation",
            "source_key": "benchmark_policy_status",
        },
        {
            "group": "Validation Source",
            "signal": "Validation Policy",
            "status": meta.get("validation_policy_status"),
            "role": "validation_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
            "meaning": "rolling underperformance 정책 기준을 충족하는지 확인",
            "next_surface": "Practical Validation",
            "source_key": "validation_policy_status",
        },
        {
            "group": "Validation Source",
            "signal": "Portfolio Guardrail Policy",
            "status": meta.get("guardrail_policy_status"),
            "role": "validation_source",
            "unavailable_blocks": False,
            "caution_blocks": False,
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

    _enrich_policy_signal_rows(rows)
    first_stage_rows = [row for row in rows if row["stage_owner"] == "first_stage"]
    second_stage_rows = [row for row in rows if row["stage_owner"] == "second_stage"]

    counts = {
        "block": sum(1 for row in rows if row["effect"] == "block"),
        "review": sum(1 for row in rows if row["effect"] == "review"),
        "pass": sum(1 for row in rows if row["effect"] == "pass"),
        "context": sum(1 for row in rows if row["effect"] == "context"),
        "first_stage": len(first_stage_rows),
        "first_stage_block": sum(1 for row in first_stage_rows if row["effect"] == "block"),
        "first_stage_pass": sum(1 for row in first_stage_rows if row["effect"] == "pass"),
        "second_stage": len(second_stage_rows),
        "second_stage_review": sum(1 for row in second_stage_rows if row["effect"] == "review"),
    }
    return {
        "schema_version": "backtest_policy_signal_inventory_v1",
        "rows": rows,
        "counts": counts,
        "blocker_rows": [row for row in rows if row["effect"] == "block"],
        "review_rows": [row for row in rows if row["effect"] == "review"],
        "context_rows": [row for row in rows if row["effect"] == "context"],
        "first_stage_rows": first_stage_rows,
        "first_stage_blocker_rows": [row for row in first_stage_rows if row["effect"] == "block"],
        "first_stage_pass_rows": [row for row in first_stage_rows if row["effect"] == "pass"],
        "second_stage_rows": second_stage_rows,
        "second_stage_review_rows": [row for row in second_stage_rows if row["effect"] == "review"],
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

    inventory = build_policy_signal_inventory(meta)
    inventory_rows = list(inventory.get("rows") or [])
    entry_blocker_rows = [
        row
        for row in inventory_rows
        if row.get("effect") == "block" and row.get("role") in {"entry_gate", "validation_source"}
    ]
    entry_review_rows = [
        row
        for row in inventory_rows
        if row.get("effect") == "review" and row.get("role") != "context_only"
    ]
    promotion_blockers = [
        f"{row.get('signal')}: {row.get('status')}"
        for row in entry_blocker_rows
        if row.get("group") == "Promotion"
    ]
    promotion_reviews = [
        f"{row.get('signal')}: {row.get('status')}"
        for row in entry_review_rows
        if row.get("group") == "Promotion"
    ]
    entry_execution_blockers = [
        f"{row.get('signal')}: {row.get('status')}"
        for row in entry_blocker_rows
        if row.get("group") in {"Data Trust", "Execution Source", "Execution Review"}
    ]
    entry_execution_reviews = [
        f"{row.get('signal')}: {row.get('status')}"
        for row in entry_review_rows
        if row.get("group") in {"Data Trust", "Execution Source", "Execution Review"}
    ]
    entry_validation_blockers = [
        f"{row.get('signal')}: {row.get('status')}"
        for row in entry_blocker_rows
        if row.get("group") in {"Validation Source", "Validation Review"}
    ]
    entry_validation_reviews = [
        f"{row.get('signal')}: {row.get('status')}"
        for row in entry_review_rows
        if row.get("group") in {"Validation Source", "Validation Review"}
    ]

    if promotion == "real_money_candidate":
        promotion_score = 4.0
        promotion_judgment = "강한 handoff policy signal"
    elif promotion == "production_candidate":
        promotion_score = 3.0
        promotion_judgment = "비교 가능, 추가 검토 필요"
    elif promotion and promotion != "hold":
        promotion_score = 2.0
        promotion_judgment = "비교 가능성은 있으나 보수적 확인 필요"
    elif promotion == "hold":
        promotion_score = 1.0
        promotion_judgment = "2차 검증에서 hold 사유 확인 필요"
    else:
        promotion_score = 0.0
        promotion_judgment = "promotion signal 생성 전에는 source 등록 보류"

    if entry_execution_blockers:
        execution_score = 0.0
        execution_judgment = "실행 원천 blocker가 남아 있음"
    elif entry_execution_reviews:
        execution_score = 2.0
        execution_judgment = "실행 부담은 검토 가능하지만 확인 항목 있음"
    else:
        execution_score = 3.0
        execution_judgment = "실행 부담 원천 지표가 양호함"

    if entry_validation_blockers:
        validation_score = 0.0
        validation_judgment = "검증 원천 blocker가 남아 있음"
    elif entry_validation_reviews:
        validation_score = 2.0
        validation_judgment = "검증 근거는 있으나 후속 확인 필요"
    else:
        validation_score = 3.0
        validation_judgment = "검증 원천 지표가 양호함"

    score = round(promotion_score + execution_score + validation_score, 1)
    can_enter_practical_validation = (
        not promotion_blockers
        and not entry_execution_blockers
        and not entry_validation_blockers
    )
    can_move_to_compare = (
        promotion not in {"", "hold"}
        and not execution_blockers
        and not validation_blockers
    )

    if can_enter_practical_validation and score >= 8.0 and not promotion_reviews:
        verdict = "후보 검토 진행 가능"
        tone = "success"
        route_label = "Portfolio Mix Builder 또는 Practical Validation"
        next_action = "Portfolio Mix Builder에서 다른 후보와 조합하거나 Practical Validation으로 보내 검증 근거를 확인합니다."
    elif can_enter_practical_validation:
        verdict = "2차 검증 진입 가능, 확인 항목 있음"
        tone = "warning"
        route_label = "Practical Validation 조건부 진입"
        next_action = "Practical Validation으로 넘긴 뒤 promotion hold 사유와 review 항목을 먼저 확인합니다."
    else:
        verdict = "2차 진입 보류: source blocker 먼저 해결"
        tone = "error"
        route_label = "Hold / Review"
        next_action = "가격 / benchmark / promotion signal처럼 source 등록을 막는 항목을 먼저 정리합니다."

    blocking_reasons: list[str] = []
    if promotion in {"", "hold"}:
        blocking_reasons.append("Promotion Decision이 hold이거나 비어 있음")
    blocking_reasons.extend(execution_blockers)
    blocking_reasons.extend(validation_blockers)

    entry_blocking_reasons: list[str] = []
    entry_blocking_reasons.extend(promotion_blockers)
    entry_blocking_reasons.extend(entry_execution_blockers)
    entry_blocking_reasons.extend(entry_validation_blockers)

    review_reasons: list[str] = []
    review_reasons.extend(promotion_reviews)
    review_reasons.extend(entry_execution_reviews)
    review_reasons.extend(entry_validation_reviews)

    criteria_rows = [
        {
            "기준": "Promotion Decision",
            "현재 값": promotion or "-",
            "점수": f"{promotion_score:g} / 4",
            "판단": promotion_judgment,
        },
        {
            "기준": "Execution Source Checks",
            "현재 값": "정상" if not entry_execution_blockers and not entry_execution_reviews else f"block {len(entry_execution_blockers)} / review {len(entry_execution_reviews)}",
            "점수": f"{execution_score:g} / 3",
            "판단": execution_judgment,
        },
        {
            "기준": "Validation Source Checks",
            "현재 값": "정상" if not entry_validation_blockers and not entry_validation_reviews else f"block {len(entry_validation_blockers)} / review {len(entry_validation_reviews)}",
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
        "can_enter_practical_validation": can_enter_practical_validation,
        "can_move_to_compare": can_move_to_compare,
        "criteria_rows": criteria_rows,
        "blocking_reasons": blocking_reasons,
        "entry_blocking_reasons": entry_blocking_reasons,
        "review_reasons": review_reasons,
        "execution_blockers": execution_blockers,
        "execution_reviews": execution_reviews,
        "validation_blockers": validation_blockers,
        "validation_reviews": validation_reviews,
        "promotion_ok": not promotion_blockers,
        "promotion_review_count": len(promotion_reviews),
        "entry_execution_blockers": entry_execution_blockers,
        "entry_execution_reviews": entry_execution_reviews,
        "entry_validation_blockers": entry_validation_blockers,
        "entry_validation_reviews": entry_validation_reviews,
        "execution_blocker_count": len(entry_execution_blockers),
        "execution_review_count": len(entry_execution_reviews),
        "validation_blocker_count": len(entry_validation_blockers),
        "validation_review_count": len(entry_validation_reviews),
        "policy_signal_inventory": inventory,
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
    inventory = dict(evaluation.get("policy_signal_inventory") or {})
    promotion_rows = [dict(row) for row in list(inventory.get("rows") or []) if row.get("group") == "Promotion"]
    promotion_blockers = [
        "Promotion signal이 비어 있습니다. Backtest 결과를 다시 실행해 promotion signal을 생성하세요."
        for row in promotion_rows
        if row.get("effect") == "block"
    ]
    promotion_reviews = [
        "Promotion은 hold 상태입니다. 2차 검증에서 hold 사유와 보강 항목을 먼저 확인하세요."
        for row in promotion_rows
        if row.get("effect") == "review"
    ]
    execution_blockers = [str(item) for item in list(evaluation.get("entry_execution_blockers") or [])]
    execution_reviews = [str(item) for item in list(evaluation.get("entry_execution_reviews") or [])]
    validation_blockers = [str(item) for item in list(evaluation.get("entry_validation_blockers") or [])]
    validation_reviews = [str(item) for item in list(evaluation.get("entry_validation_reviews") or [])]

    gate_groups = [
        _gate_group(
            label="Promotion",
            pass_value="통과",
            blockers=promotion_blockers,
            reviews=promotion_reviews,
            block_value="신호 없음",
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
    elif promotion_reviews:
        action_items.append(promotion_reviews[0])
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

    if not bool(evaluation.get("can_enter_practical_validation")):
        reason_title = "먼저 해결할 항목"
    elif action_items == ["막는 항목 없음"]:
        reason_title = "상태"
    else:
        reason_title = "다음 단계 확인 항목"

    return {
        "can_submit": bool(evaluation.get("can_enter_practical_validation")),
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
