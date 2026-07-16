from __future__ import annotations

import json
from typing import Any

import numpy as np
import pandas as pd

from app.runtime import load_backtest_run_history
from app.workspace_paths import PRACTICAL_VALIDATION_STRESS_WINDOW_FILE
from app.services.backtest_practical_validation_curve_context import (
    _aligned_monthly_returns,
    _combine_component_curves,
    _format_date,
    _format_percent,
    _normalize_result_curve,
    _parse_date,
    _price_proxy_curve,
    _summary_metrics_from_curve,
    _window_perturbation_rows,
)
from app.services.backtest_practical_validation_source import _optional_float


STRESS_WINDOW_FILE = PRACTICAL_VALIDATION_STRESS_WINDOW_FILE
ROBUSTNESS_LAB_BOARD_SCHEMA_VERSION = "robustness_lab_board_v1"


def _robustness_status(value: Any) -> str:
    text = str(value or "").strip().upper()
    if text in {"BLOCK", "BLOCKED"}:
        return "BLOCKED"
    if text in {"REVIEW", "WATCH", "FOLLOW_UP", "NEEDS_REVIEW", "REVIEW_REQUIRED"}:
        return "REVIEW"
    if text in {"PASS", "READY", "COMPUTED", "OK"}:
        return "PASS"
    if text in {"NOT_APPLICABLE", "NOT APPLICABLE"}:
        return "NOT_APPLICABLE"
    if text in {"NOT_RUN", "MISSING", "NEEDS_INPUT", ""}:
        return "NOT_RUN"
    return text


def _combine_robustness_status(statuses: list[Any]) -> str:
    normalized = [_robustness_status(status) for status in statuses if str(status or "").strip()]
    if not normalized:
        return "NOT_RUN"
    applicable = [
        status for status in normalized if status != "NOT_APPLICABLE"
    ]
    if not applicable:
        return "NOT_APPLICABLE"
    normalized = applicable
    if "BLOCKED" in normalized:
        return "BLOCKED"
    if "REVIEW" in normalized:
        return "REVIEW"
    if "NOT_RUN" in normalized:
        return "NOT_RUN" if set(normalized) == {"NOT_RUN"} else "REVIEW"
    if set(normalized) == {"PASS"}:
        return "PASS"
    return "REVIEW"


def _row_status(row: dict[str, Any]) -> str:
    return _robustness_status(row.get("Status") or row.get("Result Status") or row.get("Judgment"))


def _compact_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _stress_detail_row(row: dict[str, Any]) -> dict[str, Any]:
    status = (
        "NOT_APPLICABLE"
        if row.get("Coverage") == "NOT_COVERED"
        and row.get("Judgment") == "기간 미포함"
        else _row_status(row)
    )
    current_parts = [
        f"return {_format_percent(row.get('Portfolio Return'))}",
        f"MDD {_format_percent(row.get('Portfolio MDD'))}",
        f"spread {_format_percent(row.get('Benchmark Spread'))}",
    ]
    return {
        "Check": _compact_text(row.get("Scenario") or row.get("Check") or row.get("Metric")),
        "Status": status,
        "Current": " / ".join(current_parts),
        "Evidence": _compact_text(row.get("Window") or row.get("Finding") or row.get("Judgment")),
        "Meaning": _compact_text(row.get("Expected Check") or row.get("Why It Matters") or row.get("Decision Use")),
        "Next Check": _compact_text(row.get("Next Check")),
    }


def _sensitivity_detail_row(row: dict[str, Any]) -> dict[str, Any]:
    status = _row_status(row)
    current_parts = [
        f"CAGR delta {_format_percent(row.get('CAGR Delta'))}",
        f"MDD delta {_format_percent(row.get('MDD Delta'))}",
    ]
    return {
        "Check": _compact_text(row.get("Scenario") or row.get("Check") or row.get("Metric")),
        "Status": status,
        "Current": " / ".join(current_parts),
        "Evidence": _compact_text(row.get("Scope") or row.get("Finding") or row.get("Judgment")),
        "Meaning": _compact_text(row.get("Expected Check") or row.get("Why It Matters")),
        "Next Check": _compact_text(row.get("Next Check")),
    }


def _interpretation_detail_row(row: dict[str, Any]) -> dict[str, Any]:
    status = _row_status(row)
    return {
        "Check": _compact_text(row.get("Check") or row.get("Scenario") or row.get("Metric")),
        "Status": status,
        "Current": _compact_text(row.get("Finding") or row.get("Current") or row.get("Value")),
        "Evidence": _compact_text(row.get("Why It Matters") or row.get("Evidence") or row.get("Threshold")),
        "Meaning": _compact_text(row.get("Why It Matters") or row.get("Meaning") or row.get("Expected Check")),
        "Next Check": _compact_text(row.get("Next Check") or row.get("Required Action")),
    }


def _limited_rows(rows: list[dict[str, Any]], *, limit: int = 12) -> list[dict[str, Any]]:
    return [dict(row) for row in rows[:limit]]


def build_robustness_lab_board(
    *,
    stress_interpretation: dict[str, Any] | None = None,
    sensitivity_interpretation: dict[str, Any] | None = None,
    stress_rows: list[dict[str, Any]] | None = None,
    sensitivity_rows: list[dict[str, Any]] | None = None,
    overfit_audit: dict[str, Any] | None = None,
    rolling_evidence: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Build a compact evidence board from existing robustness diagnostics."""

    stress = dict(stress_interpretation or {})
    sensitivity = dict(sensitivity_interpretation or {})
    overfit = dict(overfit_audit or {})
    rolling = dict(rolling_evidence or {})
    rolling_metrics = dict(rolling.get("metrics") or {})
    stress_computed = int(stress.get("computed_count") or 0)
    stress_covered = int(stress.get("covered_count") or 0)
    sensitivity_computed = int(sensitivity.get("computed_count") or 0)
    sensitivity_review = int(sensitivity.get("review_count") or 0)
    runtime_followup = int(sensitivity.get("runtime_followup_count") or 0)
    local_trial_count = int(overfit.get("trial_count") or 0)
    sensitivity_status = _robustness_status(sensitivity.get("status"))
    if runtime_followup and sensitivity_status == "PASS":
        sensitivity_status = "REVIEW"
    status = _combine_robustness_status(
        [
            stress.get("status"),
            sensitivity_status,
            rolling.get("status"),
            overfit.get("status"),
        ]
    )

    stress_detail_rows = _limited_rows(
        [_interpretation_detail_row(dict(row or {})) for row in list(stress.get("rows") or [])]
        + [_stress_detail_row(dict(row or {})) for row in list(stress_rows or [])],
        limit=12,
    )
    sensitivity_detail_rows = _limited_rows(
        [_interpretation_detail_row(dict(row or {})) for row in list(sensitivity.get("rows") or [])]
        + [_sensitivity_detail_row(dict(row or {})) for row in list(sensitivity_rows or [])],
        limit=12,
    )
    rolling_status = _robustness_status(rolling.get("status"))
    overfit_status = _robustness_status(overfit.get("status"))
    summary_rows = [
        {
            "Check": "Stress window coverage",
            "Status": _robustness_status(stress.get("status")),
            "Current": f"{stress_computed}/{stress_covered} computed",
            "Evidence": _compact_text(stress.get("summary")),
            "Meaning": "후보 기간과 겹치는 위기 구간을 실제 curve로 계산했는지 확인합니다.",
        },
        {
            "Check": "Worst computed stress",
            "Status": _row_status({"Status": stress.get("status")}) if stress.get("worst_mdd") is None else (
                "REVIEW" if (_optional_float(stress.get("worst_mdd")) or 0.0) < -0.20 else "PASS"
            ),
            "Current": (
                f"{stress.get('worst_mdd_scenario') or '-'} / "
                f"MDD {_format_percent(stress.get('worst_mdd'))} / "
                f"spread {_format_percent(stress.get('worst_benchmark_spread'))}"
            ),
            "Evidence": "stress MDD와 benchmark spread",
            "Meaning": "위기 구간 손실 방어와 단순 benchmark 대비 약점을 봅니다.",
        },
        {
            "Check": "Sensitivity coverage",
            "Status": sensitivity_status,
            "Current": f"computed {sensitivity_computed} / review {sensitivity_review} / runtime follow-up {runtime_followup}",
            "Evidence": _compact_text(sensitivity.get("summary")),
            "Meaning": "기간, 구성요소, 비중 변화에 결과가 과도하게 흔들리는지 확인합니다.",
        },
        {
            "Check": "Worst sensitivity delta",
            "Status": "REVIEW" if sensitivity_review else sensitivity_status,
            "Current": (
                f"{sensitivity.get('worst_scenario') or '-'} / "
                f"CAGR delta {_format_percent(sensitivity.get('worst_cagr_delta'))} / "
                f"MDD delta {_format_percent(sensitivity.get('worst_mdd_delta'))}"
            ),
            "Evidence": "window / drop-one / weight tilt sensitivity",
            "Meaning": "한 component나 특정 기간만으로 성과가 설명되는지 봅니다.",
        },
        {
            "Check": "Rolling validation",
            "Status": rolling_status,
            "Current": (
                f"windows {rolling_metrics.get('window_count', '-')} / "
                f"worst CAGR {_format_percent(rolling_metrics.get('worst_rolling_cagr'))} / "
                f"worst MDD {_format_percent(rolling_metrics.get('worst_rolling_mdd'))}"
            ),
            "Evidence": _compact_text(rolling.get("summary")),
            "Meaning": "전체 기간 1회 성과가 아니라 여러 rolling 구간에서 논리가 유지되는지 봅니다.",
        },
        {
            "Check": "Local overfit audit",
            "Status": overfit_status,
            "Current": f"{local_trial_count} local matched trials",
            "Evidence": _compact_text(overfit.get("interpretation")),
            "Meaning": "local run_history에서 과도한 반복 실험 흔적이 있는지 compact summary로만 확인합니다.",
        },
    ]
    follow_up_rows = _limited_rows(
        [
            row
            for row in summary_rows + stress_detail_rows + sensitivity_detail_rows
            if _robustness_status(row.get("Status"))
            not in {"PASS", "NOT_APPLICABLE"}
        ],
        limit=12,
    )
    limitations = [
        "Robustness Lab은 기존 Practical Validation evidence의 compact read model이며 새 저장 체인이 아닙니다.",
        "Strategy-specific parameter perturbation은 runtime follow-up으로 남기고, 구현 전에는 PASS로 간주하지 않습니다.",
    ]
    if stress.get("uncomputed_count"):
        limitations.append("Covered stress window 중 daily replay가 필요한 항목은 NOT_RUN / REVIEW 근거로 남깁니다.")
    if runtime_followup:
        limitations.append("GTAA interval, MA window, momentum lookback 같은 전략 내부 parameter는 후속 runtime perturbation이 필요합니다.")

    return {
        "schema_version": ROBUSTNESS_LAB_BOARD_SCHEMA_VERSION,
        "status": status,
        "summary": (
            f"Stress {stress_computed}/{stress_covered}, sensitivity {sensitivity_computed}, "
            f"runtime follow-up {runtime_followup}, local trials {local_trial_count} 기준으로 robustness evidence를 요약했습니다."
        ),
        "summary_rows": summary_rows,
        "stress_rows": stress_detail_rows,
        "sensitivity_rows": sensitivity_detail_rows,
        "follow_up_rows": follow_up_rows,
        "metrics": {
            "stress_status": _robustness_status(stress.get("status")),
            "covered_stress_windows": stress_covered,
            "computed_stress_windows": stress_computed,
            "uncomputed_stress_windows": int(stress.get("uncomputed_count") or 0),
            "sensitivity_status": sensitivity_status,
            "computed_sensitivity_checks": sensitivity_computed,
            "sensitivity_review_count": sensitivity_review,
            "runtime_followup_count": runtime_followup,
            "rolling_status": rolling_status,
            "rolling_window_count": rolling_metrics.get("window_count"),
            "overfit_status": overfit_status,
            "local_trial_count": local_trial_count,
        },
        "limitations": limitations,
    }


def _simple_component_title(component: dict[str, Any]) -> str:
    return str(component.get("title") or component.get("strategy_name") or component.get("component_id") or "-")


def _simple_component_weight(component: dict[str, Any]) -> float:
    return _optional_float(component.get("target_weight")) or 0.0


def _rolling_validation_evidence(
    portfolio_curve: pd.DataFrame,
    benchmark_curve: pd.DataFrame,
    *,
    window_months: int,
    mdd_review_line: float,
) -> dict[str, Any]:
    curve = _normalize_result_curve(portfolio_curve)
    if curve.empty:
        return {"status": "NOT_RUN", "rows": [], "summary": "portfolio curve 없음"}
    monthly = (
        curve.assign(_month=curve["Date"].dt.to_period("M"))
        .groupby("_month", as_index=False)
        .tail(1)
        .sort_values("Date")
        .reset_index(drop=True)
    )
    if len(monthly) < max(window_months + 1, 6):
        return {"status": "NOT_RUN", "rows": [], "summary": f"{window_months}개월 rolling 계산에 필요한 월별 데이터가 부족합니다."}
    rows: list[dict[str, Any]] = []
    for end_idx in range(window_months, len(monthly)):
        window = monthly.iloc[end_idx - window_months : end_idx + 1].copy()
        start_balance = _optional_float(window["Total Balance"].iloc[0])
        end_balance = _optional_float(window["Total Balance"].iloc[-1])
        if not start_balance or end_balance is None or start_balance <= 0:
            continue
        years = max((window["Date"].iloc[-1] - window["Date"].iloc[0]).days / 365.25, 1 / 12)
        cagr = (end_balance / start_balance) ** (1 / years) - 1
        drawdown = window["Total Balance"] / window["Total Balance"].cummax() - 1
        rows.append(
            {
                "Window End": _format_date(window["Date"].iloc[-1]),
                "Window Months": window_months,
                "CAGR": cagr,
                "MDD": float(drawdown.min()),
            }
        )
    if not rows:
        return {"status": "NOT_RUN", "rows": [], "summary": "rolling windows 계산 실패"}
    worst_mdd = min(float(row["MDD"]) for row in rows)
    worst_cagr = min(float(row["CAGR"]) for row in rows)
    negative_share = sum(1 for row in rows if float(row["CAGR"]) < 0) / len(rows)
    evidence_rows = [
        {
            "Metric": "Rolling windows",
            "Value": len(rows),
            "Threshold": f"{window_months}M",
            "Judgment": "computed",
        },
        {
            "Metric": "Worst rolling CAGR",
            "Value": worst_cagr,
            "Threshold": ">= 0 preferred",
            "Judgment": "REVIEW" if worst_cagr < 0 else "PASS",
        },
        {
            "Metric": "Worst rolling MDD",
            "Value": worst_mdd,
            "Threshold": mdd_review_line / 100.0,
            "Judgment": "REVIEW" if worst_mdd < (mdd_review_line / 100.0) else "PASS",
        },
        {
            "Metric": "Negative rolling CAGR share",
            "Value": negative_share,
            "Threshold": "<= 35%",
            "Judgment": "REVIEW" if negative_share > 0.35 else "PASS",
        },
    ]
    status = "REVIEW" if any(row["Judgment"] == "REVIEW" for row in evidence_rows) else "PASS"
    return {
        "status": status,
        "rows": evidence_rows,
        "summary": f"{window_months}개월 rolling 기준 worst CAGR {worst_cagr:.2%}, worst MDD {worst_mdd:.2%}",
        "metrics": {
            "window_months": window_months,
            "window_count": len(rows),
            "worst_rolling_cagr": worst_cagr,
            "worst_rolling_mdd": worst_mdd,
            "negative_rolling_cagr_share": negative_share,
        },
    }


def _load_static_stress_windows() -> list[dict[str, Any]]:
    if not STRESS_WINDOW_FILE.exists():
        return []
    try:
        payload = json.loads(STRESS_WINDOW_FILE.read_text(encoding="utf-8"))
    except (OSError, json.JSONDecodeError):
        return []
    return [dict(row or {}) for row in list(payload.get("windows") or []) if isinstance(row, dict)]


def _period_curve_metrics(result_df: pd.DataFrame, *, start: Any, end: Any) -> dict[str, Any]:
    curve = _normalize_result_curve(result_df)
    start_ts = _parse_date(start)
    end_ts = _parse_date(end)
    if curve.empty or start_ts is None or end_ts is None:
        return {}
    window = curve[(curve["Date"] >= start_ts) & (curve["Date"] <= end_ts)].copy()
    if len(window) < 2:
        return {}
    start_balance = _optional_float(window["Total Balance"].iloc[0])
    end_balance = _optional_float(window["Total Balance"].iloc[-1])
    if not start_balance or end_balance is None or start_balance <= 0:
        return {}
    drawdown = window["Total Balance"] / window["Total Balance"].cummax() - 1
    return {
        "start": _format_date(window["Date"].iloc[0]),
        "end": _format_date(window["Date"].iloc[-1]),
        "return": end_balance / start_balance - 1.0,
        "mdd": float(drawdown.min()),
        "rows": len(window),
    }


def _stress_window_rows(
    source_period: dict[str, Any],
    portfolio_curve: pd.DataFrame | None = None,
    benchmark_curve: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    actual_start = _parse_date(source_period.get("actual_start") or source_period.get("start"))
    actual_end = _parse_date(source_period.get("actual_end") or source_period.get("end"))
    portfolio_curve = _normalize_result_curve(portfolio_curve)
    benchmark_curve = _normalize_result_curve(benchmark_curve)
    rows: list[dict[str, Any]] = []
    for window in _load_static_stress_windows():
        start = _parse_date(window.get("start"))
        end = _parse_date(window.get("end"))
        if actual_start is None or actual_end is None or start is None or end is None:
            coverage = "UNKNOWN"
            result_status = "NOT_RUN"
            judgment = "기간 정보 부족"
        elif actual_end < start or actual_start > end:
            coverage = "NOT_COVERED"
            result_status = "NOT_RUN"
            judgment = "기간 미포함"
        else:
            coverage = "COVERED"
            portfolio_metrics = _period_curve_metrics(portfolio_curve, start=start, end=end)
            benchmark_metrics = _period_curve_metrics(benchmark_curve, start=start, end=end)
            if portfolio_metrics:
                result_status = "REVIEW" if (_optional_float(portfolio_metrics.get("mdd")) or 0.0) < -0.20 else "PASS"
                judgment = "구간 성과 계산됨"
            else:
                result_status = "NOT_RUN"
                judgment = "curve replay 필요"
            benchmark_return = _optional_float(benchmark_metrics.get("return"))
            portfolio_return = _optional_float(portfolio_metrics.get("return"))
            benchmark_spread = (
                portfolio_return - benchmark_return
                if portfolio_return is not None and benchmark_return is not None
                else None
            )
        rows.append(
            {
                "Scenario": window.get("label") or window.get("id"),
                "Window": f"{window.get('start')} -> {window.get('end')}",
                "Category": window.get("category"),
                "Coverage": coverage,
                "Result Status": result_status,
                "Portfolio Return": portfolio_metrics.get("return") if coverage == "COVERED" and "portfolio_metrics" in locals() else None,
                "Portfolio MDD": portfolio_metrics.get("mdd") if coverage == "COVERED" and "portfolio_metrics" in locals() else None,
                "Benchmark Spread": benchmark_spread if coverage == "COVERED" and "benchmark_spread" in locals() else None,
                "Expected Check": "return / MDD / benchmark spread",
                "Judgment": judgment,
                "Decision Use": "Stress / scenario evidence",
            }
        )
        if "portfolio_metrics" in locals():
            del portfolio_metrics
        if "benchmark_metrics" in locals():
            del benchmark_metrics
        if "benchmark_spread" in locals():
            del benchmark_spread
    return rows


def _stress_interpretation_result(
    stress_rows: list[dict[str, Any]],
    *,
    provider_macro: dict[str, Any] | None = None,
    asset_exposure: dict[str, Any] | None = None,
) -> dict[str, Any]:
    """Turn stress-window measurements into operator-facing review triggers."""
    rows = [dict(row or {}) for row in stress_rows]
    covered_rows = [row for row in rows if row.get("Coverage") == "COVERED"]
    computed_rows = [
        row
        for row in covered_rows
        if str(row.get("Result Status") or "") in {"PASS", "REVIEW"}
        and _optional_float(row.get("Portfolio MDD")) is not None
    ]
    uncomputed_rows = [row for row in covered_rows if str(row.get("Result Status") or "") == "NOT_RUN"]
    review_rows = [row for row in computed_rows if str(row.get("Result Status") or "") == "REVIEW"]
    worst_mdd_row = min(
        computed_rows,
        key=lambda row: _optional_float(row.get("Portfolio MDD")) or 0.0,
    ) if computed_rows else {}
    worst_return_row = min(
        computed_rows,
        key=lambda row: _optional_float(row.get("Portfolio Return")) or 0.0,
    ) if computed_rows else {}
    spread_rows = [row for row in computed_rows if _optional_float(row.get("Benchmark Spread")) is not None]
    worst_spread_row = min(
        spread_rows,
        key=lambda row: _optional_float(row.get("Benchmark Spread")) or 0.0,
    ) if spread_rows else {}

    worst_mdd = _optional_float(worst_mdd_row.get("Portfolio MDD"))
    worst_return = _optional_float(worst_return_row.get("Portfolio Return"))
    worst_spread = _optional_float(worst_spread_row.get("Benchmark Spread"))
    macro_metrics = dict(dict(provider_macro or {}).get("metrics") or {})
    risk_label = str(macro_metrics.get("risk_label") or "-")
    exposure = dict(asset_exposure or {})
    exposure_lens = (
        f"equity {_optional_float(exposure.get('equity')) or 0.0:.1f}% / "
        f"bond {_optional_float(exposure.get('bond')) or 0.0:.1f}% / "
        f"gold {_optional_float(exposure.get('gold')) or 0.0:.1f}%"
    ) if exposure else "-"

    trigger_reasons: list[str] = []
    if review_rows:
        trigger_reasons.append("stress MDD trigger")
    if worst_spread is not None and worst_spread < -0.05:
        trigger_reasons.append("benchmark spread < -5%p")
    if uncomputed_rows:
        trigger_reasons.append("covered stress windows need daily replay")

    if not rows:
        status = "NOT_RUN"
        summary = "stress calendar를 읽지 못해 scenario 해석을 만들지 못했습니다."
    elif not covered_rows:
        status = "NOT_APPLICABLE"
        summary = "저장된 stress window가 모두 후보 기간 밖이므로 미실행 검증이 아니라 적용 제외로 분류합니다."
    elif computed_rows and not trigger_reasons:
        status = "PASS"
        summary = (
            f"{len(computed_rows)}/{len(covered_rows)}개 stress window를 계산했고, "
            f"worst MDD {_format_percent(worst_mdd)} / benchmark spread {_format_percent(worst_spread)}입니다."
        )
    else:
        status = "REVIEW"
        summary = (
            f"{len(computed_rows)}/{len(covered_rows)}개 covered stress window만 계산됐습니다. "
            f"확인 trigger: {', '.join(trigger_reasons) if trigger_reasons else 'stress replay 필요'}."
        )

    interpretation_rows = [
        {
            "Check": "Stress coverage",
            "Status": status,
            "Finding": f"{len(computed_rows)}/{len(covered_rows)} covered windows computed",
            "Why It Matters": "후보 기간에 포함된 위기 구간을 실제 curve로 잘라 볼 수 있는지 확인합니다.",
            "Next Check": "NOT_RUN covered window는 daily runtime replay로 다시 계산합니다.",
        },
        {
            "Check": "Worst computed MDD",
            "Status": (
                "NOT_APPLICABLE"
                if status == "NOT_APPLICABLE"
                else (
                    "REVIEW"
                    if worst_mdd is not None and worst_mdd < -0.20
                    else "PASS" if worst_mdd is not None else "NOT_RUN"
                )
            ),
            "Finding": f"{worst_mdd_row.get('Scenario') or '-'} / MDD {_format_percent(worst_mdd)}",
            "Why It Matters": "위기 구간에서 손실 방어가 선택 기준과 맞는지 확인합니다.",
            "Next Check": "MDD가 커지면 해당 구간의 component와 asset exposure를 확인합니다.",
        },
        {
            "Check": "Benchmark spread",
            "Status": (
                "NOT_APPLICABLE"
                if status == "NOT_APPLICABLE"
                else (
                    "REVIEW"
                    if worst_spread is not None and worst_spread < -0.05
                    else "PASS" if worst_spread is not None else "NOT_RUN"
                )
            ),
            "Finding": f"{worst_spread_row.get('Scenario') or '-'} / spread {_format_percent(worst_spread)}",
            "Why It Matters": "위기 구간에서 단순 benchmark보다 방어 또는 회복이 약했는지 봅니다.",
            "Next Check": "benchmark보다 5%p 이상 약하면 후보 목적을 다시 확인합니다.",
        },
        {
            "Check": "Return shock",
            "Status": (
                "NOT_APPLICABLE"
                if status == "NOT_APPLICABLE"
                else (
                    "REVIEW"
                    if worst_return is not None and worst_return < -0.10
                    else "PASS" if worst_return is not None else "NOT_RUN"
                )
            ),
            "Finding": f"{worst_return_row.get('Scenario') or '-'} / return {_format_percent(worst_return)}",
            "Why It Matters": "stress window의 절대 손실이 운영 감내선 안에 있는지 봅니다.",
            "Next Check": "절대 손실이 크면 monitoring trigger를 더 엄격하게 둡니다.",
        },
        {
            "Check": "Current macro / exposure lens",
            "Status": "PASS" if risk_label == "neutral / risk-on" else "REVIEW" if risk_label != "-" else "NOT_RUN",
            "Finding": f"macro {risk_label} / {exposure_lens}",
            "Why It Matters": "과거 stress 취약점이 현재 금리/변동성/자산군 노출과 다시 맞물리는지 봅니다.",
            "Next Check": "risk-off면 Final Review에서 신규 진입 또는 추적 기간을 보수적으로 둡니다.",
        },
    ]
    return {
        "status": status,
        "summary": summary,
        "rows": interpretation_rows,
        "covered_count": len(covered_rows),
        "computed_count": len(computed_rows),
        "uncomputed_count": len(uncomputed_rows),
        "period_outside_count": sum(
            1
            for row in rows
            if row.get("Coverage") == "NOT_COVERED"
            and row.get("Judgment") == "기간 미포함"
        ),
        "missing_validator_count": len(uncomputed_rows),
        "review_count": len(review_rows),
        "worst_mdd": worst_mdd,
        "worst_mdd_scenario": worst_mdd_row.get("Scenario"),
        "worst_return": worst_return,
        "worst_return_scenario": worst_return_row.get("Scenario"),
        "worst_benchmark_spread": worst_spread,
        "worst_benchmark_spread_scenario": worst_spread_row.get("Scenario"),
        "trigger_reasons": trigger_reasons,
    }


def _build_overfit_audit(source_row: dict[str, Any], active_components: list[dict[str, Any]]) -> dict[str, Any]:
    strategy_keys = {
        str(component.get("strategy_key") or component.get("strategy_family") or "").strip()
        for component in active_components
        if str(component.get("strategy_key") or component.get("strategy_family") or "").strip()
    }
    source_title = str(source_row.get("source_title") or "").lower()
    try:
        history_rows = load_backtest_run_history(limit=500)
    except Exception:
        history_rows = []
    matched: list[dict[str, Any]] = []
    for row in history_rows:
        strategy_key = str(row.get("strategy_key") or "").strip()
        selected_strategies = {
            str(item or "").strip()
            for item in list(dict(row.get("context") or {}).get("selected_strategies") or [])
            if str(item or "").strip()
        }
        title_match = source_title and source_title in str(row.get("strategy_name") or row.get("preset_name") or "").lower()
        if strategy_key in strategy_keys or strategy_keys.intersection(selected_strategies) or title_match:
            matched.append(row)
    if not matched:
        return {
            "audit_source": "local_run_history_summary",
            "status": "NOT_RUN",
            "trial_count": 0,
            "interpretation": "관련 run_history 자동 매칭이 없어 선택 과정 audit을 실행하지 못했습니다.",
        }
    period_variants = {
        (str(row.get("input_start") or ""), str(row.get("input_end") or ""))
        for row in matched
    }
    weight_variants = {
        json.dumps(dict(row.get("context") or {}).get("weights_percent") or {}, sort_keys=True, default=str)
        for row in matched
        if dict(row.get("context") or {}).get("weights_percent")
    }
    strategy_variants = {
        str(row.get("strategy_key") or tuple(dict(row.get("context") or {}).get("selected_strategies") or []))
        for row in matched
    }
    trial_count = len(matched)
    status = "REVIEW" if trial_count > 30 else "PASS"
    return {
        "audit_source": "local_run_history_summary",
        "status": status,
        "trial_count": trial_count,
        "unique_strategy_variants": len(strategy_variants),
        "unique_weight_variants": len(weight_variants),
        "unique_period_variants": len(period_variants),
        "run_history_window": "latest_500_local_rows",
        "interpretation": "관련 실험 횟수가 많아 sensitivity 검증을 강화해야 합니다."
        if status == "REVIEW"
        else "관련 local trial count가 과도하게 높지는 않습니다.",
    }


def _baseline_rows(
    portfolio_curve: pd.DataFrame | None = None,
    *,
    source_period: dict[str, Any] | None = None,
    success_metric: str = "better_risk_adjusted",
) -> list[dict[str, Any]]:
    portfolio_curve = _normalize_result_curve(portfolio_curve)
    if not portfolio_curve.empty:
        start_value = portfolio_curve["Date"].min()
        end_value = portfolio_curve["Date"].max()
    else:
        source_period = dict(source_period or {})
        start_value = source_period.get("actual_start") or source_period.get("start")
        end_value = source_period.get("actual_end") or source_period.get("end")
    candidate_summary = _summary_metrics_from_curve(portfolio_curve, name="Candidate")
    definitions = [
        ("SPY", "미국 대형주 broad equity 단순 대안", ["SPY"], [1.0], "MVP"),
        ("QQQ", "성장 / Nasdaq 노출 단순 대안", ["QQQ"], [1.0], "MVP"),
        ("60/40 proxy", "주식 + 채권 균형 대안", ["SPY", "TLT"], [0.6, 0.4], "MVP"),
        ("cash-aware baseline", "현금 또는 단기채를 섞은 방어형 대안", ["SPY", "TLT", "BIL"], [0.6, 0.2, 0.2], "MVP"),
        ("All Weather-like proxy", "regime 분산형 대리 비교군", ["SPY", "TLT", "IEF", "GLD", "DBC"], [0.30, 0.30, 0.15, 0.15, 0.10], "Future"),
    ]
    rows: list[dict[str, Any]] = []
    for name, purpose, tickers, weights, priority in definitions:
        baseline_curve, meta = _price_proxy_curve(tickers, start=start_value, end=end_value, weights=weights)
        baseline_summary = _summary_metrics_from_curve(baseline_curve, name=name)
        candidate_cagr = _optional_float(candidate_summary.get("cagr"))
        candidate_mdd = _optional_float(candidate_summary.get("mdd"))
        candidate_sharpe = _optional_float(candidate_summary.get("sharpe"))
        baseline_cagr = _optional_float(baseline_summary.get("cagr"))
        baseline_mdd = _optional_float(baseline_summary.get("mdd"))
        baseline_sharpe = _optional_float(baseline_summary.get("sharpe"))
        cagr_spread = candidate_cagr - baseline_cagr if candidate_cagr is not None and baseline_cagr is not None else None
        mdd_advantage = candidate_mdd - baseline_mdd if candidate_mdd is not None and baseline_mdd is not None else None
        sharpe_spread = candidate_sharpe - baseline_sharpe if candidate_sharpe is not None and baseline_sharpe is not None else None
        if baseline_curve.empty or not candidate_summary:
            result_status = "NOT_RUN"
            judgment = str(meta.get("reason") or "candidate/baseline curve 부족")
        elif success_metric == "higher_return":
            result_status = "PASS" if (cagr_spread or 0.0) > 0 else "REVIEW"
            judgment = "CAGR spread 기준"
        elif success_metric == "lower_mdd":
            result_status = "PASS" if (mdd_advantage or 0.0) >= 0 else "REVIEW"
            judgment = "MDD advantage 기준"
        elif success_metric == "better_downside_defense":
            result_status = "PASS" if (mdd_advantage or 0.0) >= 0 else "REVIEW"
            judgment = "downside defense 기준"
        else:
            result_status = "PASS" if (sharpe_spread or 0.0) >= 0 else "REVIEW"
            judgment = "risk-adjusted spread 기준"
        rows.append(
            {
                "Baseline": name,
                "Purpose": purpose,
                "Priority": priority,
                "Result Status": result_status,
                "Candidate CAGR": candidate_cagr,
                "Baseline CAGR": baseline_cagr,
                "CAGR Spread": cagr_spread,
                "Candidate MDD": candidate_mdd,
                "Baseline MDD": baseline_mdd,
                "MDD Advantage": mdd_advantage,
                "Sharpe Spread": sharpe_spread,
                "Judgment": judgment,
            }
        )
    return rows


def _sensitivity_rows(
    active_components: list[dict[str, Any]],
    component_curves: list[dict[str, Any]] | None = None,
    portfolio_curve: pd.DataFrame | None = None,
) -> list[dict[str, Any]]:
    rows: list[dict[str, Any]] = []
    portfolio_summary = _summary_metrics_from_curve(_normalize_result_curve(portfolio_curve), name="Portfolio")
    rows.extend(_window_perturbation_rows(portfolio_curve, base_summary=portfolio_summary))
    if len(active_components) > 1:
        usable_curves = list(component_curves or [])
        if usable_curves and portfolio_summary:
            base_cagr = _optional_float(portfolio_summary.get("cagr"))
            base_mdd = _optional_float(portfolio_summary.get("mdd"))
            for drop_idx, component in enumerate(active_components):
                drop_curves = [
                    dict(item)
                    for idx, item in enumerate(usable_curves)
                    if idx != drop_idx and not _normalize_result_curve(item.get("curve")).empty
                ]
                if not drop_curves:
                    continue
                drop_result = _combine_component_curves(drop_curves)
                drop_summary = _summary_metrics_from_curve(drop_result, name="Drop One")
                drop_cagr = _optional_float(drop_summary.get("cagr"))
                drop_mdd = _optional_float(drop_summary.get("mdd"))
                cagr_delta = drop_cagr - base_cagr if drop_cagr is not None and base_cagr is not None else None
                mdd_delta = drop_mdd - base_mdd if drop_mdd is not None and base_mdd is not None else None
                review = (cagr_delta is not None and cagr_delta < -0.03) or (
                    mdd_delta is not None and mdd_delta < -0.05
                )
                rows.append(
                    {
                        "Scenario": f"Drop-one: {_simple_component_title(component)}",
                        "Scope": "remove one component and renormalize",
                        "Result Status": "REVIEW" if review else "PASS",
                        "Expected Check": "특정 component 의존성",
                        "CAGR Delta": cagr_delta,
                        "MDD Delta": mdd_delta,
                    }
                )
            if len(active_components) == len(usable_curves):
                for tilt_idx, component in enumerate(active_components):
                    original_weights = np.array([_simple_component_weight(item) for item in active_components], dtype=float)
                    if original_weights.sum() <= 0:
                        continue
                    tilted = original_weights.copy()
                    tilted[tilt_idx] = min(100.0, tilted[tilt_idx] + 5.0)
                    reduce_total = tilted.sum() - 100.0
                    if reduce_total > 0 and len(tilted) > 1:
                        other_indices = [idx for idx in range(len(tilted)) if idx != tilt_idx]
                        other_total = tilted[other_indices].sum()
                        if other_total > 0:
                            for idx in other_indices:
                                tilted[idx] = max(0.0, tilted[idx] - reduce_total * tilted[idx] / other_total)
                    tilted_curves = []
                    for idx, item in enumerate(usable_curves):
                        item_copy = dict(item)
                        item_copy["weight"] = float(tilted[idx])
                        tilted_curves.append(item_copy)
                    tilted_result = _combine_component_curves(tilted_curves)
                    tilted_summary = _summary_metrics_from_curve(tilted_result, name="Tilted")
                    tilted_cagr = _optional_float(tilted_summary.get("cagr"))
                    tilted_mdd = _optional_float(tilted_summary.get("mdd"))
                    rows.append(
                        {
                            "Scenario": f"Mix weight +5%p: {_simple_component_title(component)}",
                            "Scope": "component weights",
                            "Result Status": "PASS",
                            "Expected Check": "비중 민감도",
                            "CAGR Delta": tilted_cagr - base_cagr if tilted_cagr is not None and base_cagr is not None else None,
                            "MDD Delta": tilted_mdd - base_mdd if tilted_mdd is not None and base_mdd is not None else None,
                        }
                    )
        else:
            rows.extend(
                [
                    {"Scenario": "Mix weight +/- 5%p", "Scope": "component weights", "Result Status": "NOT_RUN", "Expected Check": "60:40 등 특정 비중 의존성"},
                    {"Scenario": "Drop-one component", "Scope": "remove one component and renormalize", "Result Status": "NOT_RUN", "Expected Check": "특정 component 의존성"},
                ]
            )
    strategy_keys = {str(component.get("strategy_key") or component.get("strategy_family") or "").lower() for component in active_components}
    if any("gtaa" in key for key in strategy_keys):
        rows.append({"Scenario": "GTAA parameter perturbation", "Scope": "interval / MA window / rebalance day", "Result Status": "NOT_RUN", "Expected Check": "cadence 민감도"})
    if any("equal" in key for key in strategy_keys):
        rows.append({"Scenario": "Equal Weight perturbation", "Scope": "rebalance frequency / ticker subset", "Result Status": "NOT_RUN", "Expected Check": "ticker set 민감도"})
    if any("relative" in key or "grs" in key for key in strategy_keys):
        rows.append({"Scenario": "Relative Strength perturbation", "Scope": "lookback / top_n / skip period", "Result Status": "NOT_RUN", "Expected Check": "momentum window 민감도"})
    return rows


def _worst_delta_row(rows: list[dict[str, Any]], *, prefix: str | None = None) -> dict[str, Any]:
    candidates = [
        dict(row)
        for row in rows
        if (prefix is None or str(row.get("Scenario") or "").startswith(prefix))
        and (
            _optional_float(row.get("MDD Delta")) is not None
            or _optional_float(row.get("CAGR Delta")) is not None
        )
    ]
    if not candidates:
        return {}

    def sort_key(row: dict[str, Any]) -> tuple[float, float]:
        mdd_delta = _optional_float(row.get("MDD Delta"))
        cagr_delta = _optional_float(row.get("CAGR Delta"))
        return (mdd_delta if mdd_delta is not None else 0.0, cagr_delta if cagr_delta is not None else 0.0)

    return min(candidates, key=sort_key)


def _sensitivity_interpretation_result(
    sensitivity_rows: list[dict[str, Any]],
    *,
    overfit_audit: dict[str, Any],
    rolling_evidence: dict[str, Any],
) -> dict[str, Any]:
    """Summarize local sensitivity rows into the weakest assumptions to review."""
    rows = [dict(row or {}) for row in sensitivity_rows]
    computed_rows = [row for row in rows if str(row.get("Result Status") or "") in {"PASS", "REVIEW"}]
    review_rows = [row for row in computed_rows if str(row.get("Result Status") or "") == "REVIEW"]
    not_run_rows = [row for row in rows if str(row.get("Result Status") or "") == "NOT_RUN"]
    window_rows = [row for row in computed_rows if str(row.get("Expected Check") or "") == "기간 변경 민감도"]
    drop_rows = [row for row in computed_rows if str(row.get("Scenario") or "").startswith("Drop-one:")]
    weight_rows = [row for row in computed_rows if str(row.get("Scenario") or "").startswith("Mix weight")]
    runtime_followup_rows = [
        row
        for row in not_run_rows
        if str(row.get("Expected Check") or "") in {"cadence 민감도", "ticker set 민감도", "momentum window 민감도"}
    ]
    worst_window = _worst_delta_row(window_rows)
    worst_drop = _worst_delta_row(drop_rows)
    worst_weight = _worst_delta_row(weight_rows)
    all_delta_worst = _worst_delta_row(computed_rows)
    rolling_metrics = dict(rolling_evidence.get("metrics") or {})
    rolling_status = str(rolling_evidence.get("status") or "NOT_RUN")
    overfit_status = str(overfit_audit.get("status") or "NOT_RUN")

    trigger_reasons: list[str] = []
    if overfit_status == "REVIEW":
        trigger_reasons.append("local trial count review")
    if rolling_status == "REVIEW":
        trigger_reasons.append("rolling validation review")
    if review_rows:
        trigger_reasons.append("sensitivity worst-case review")

    if not computed_rows and rolling_status == "NOT_RUN":
        status = "NOT_RUN"
        summary = "curve 기반 sensitivity와 rolling validation을 계산하지 못했습니다."
    elif trigger_reasons:
        status = "REVIEW"
        worst_name = all_delta_worst.get("Scenario") or (review_rows[0].get("Scenario") if review_rows else "-")
        summary = (
            f"{len(computed_rows)}개 sensitivity를 계산했고, {worst_name}에서 검토 trigger가 있습니다. "
            f"남은 strategy-specific runtime 항목은 {len(runtime_followup_rows)}개입니다."
        )
    else:
        status = "PASS"
        summary = (
            f"{len(computed_rows)}개 curve 기반 sensitivity와 rolling validation이 즉시 review trigger 없이 계산됐습니다. "
            f"strategy-specific runtime 후속 항목은 {len(runtime_followup_rows)}개입니다."
        )

    interpretation_rows = [
        {
            "Check": "Computed sensitivity coverage",
            "Status": status if computed_rows else "NOT_RUN",
            "Finding": (
                f"computed {len(computed_rows)} / window {len(window_rows)} / "
                f"drop-one {len(drop_rows)} / weight {len(weight_rows)} / runtime follow-up {len(runtime_followup_rows)}"
            ),
            "Why It Matters": "현재 결과가 단일 기간, 단일 구성, 단일 비중에만 의존하는지 봅니다.",
            "Next Check": "runtime follow-up은 전략별 parameter perturbation 구현 후 다시 확인합니다.",
        },
        {
            "Check": "Rolling validation",
            "Status": rolling_status,
            "Finding": (
                f"windows {rolling_metrics.get('window_count', '-')} / "
                f"worst CAGR {_format_percent(rolling_metrics.get('worst_rolling_cagr'))} / "
                f"worst MDD {_format_percent(rolling_metrics.get('worst_rolling_mdd'))}"
            ),
            "Why It Matters": "한 번의 전체기간 성과가 아니라 여러 rolling 구간에서 성과가 유지되는지 봅니다.",
            "Next Check": "negative rolling share가 커지면 추적 또는 보류 기준을 강화합니다.",
        },
        {
            "Check": "Window sensitivity",
            "Status": str(worst_window.get("Result Status") or "NOT_RUN"),
            "Finding": (
                f"{worst_window.get('Scenario') or '-'} / "
                f"CAGR delta {_format_percent(worst_window.get('CAGR Delta'))} / "
                f"MDD delta {_format_percent(worst_window.get('MDD Delta'))}"
            ),
            "Why It Matters": "시작일과 종료일을 조금 바꿔도 논리가 유지되는지 봅니다.",
            "Next Check": "특정 기간 제외 시 성과가 무너지면 선택 근거를 다시 봅니다.",
        },
        {
            "Check": "Component dependency",
            "Status": str(worst_drop.get("Result Status") or "NOT_RUN"),
            "Finding": (
                f"{worst_drop.get('Scenario') or '-'} / "
                f"CAGR delta {_format_percent(worst_drop.get('CAGR Delta'))} / "
                f"MDD delta {_format_percent(worst_drop.get('MDD Delta'))}"
            ),
            "Why It Matters": "특정 component 하나가 빠졌을 때 포트폴리오 안정성이 급격히 약해지는지 봅니다.",
            "Next Check": "REVIEW면 해당 component가 왜 필요한지 Final Review 근거에 남깁니다.",
        },
        {
            "Check": "Weight tilt sensitivity",
            "Status": str(worst_weight.get("Result Status") or "NOT_RUN"),
            "Finding": (
                f"{worst_weight.get('Scenario') or '-'} / "
                f"CAGR delta {_format_percent(worst_weight.get('CAGR Delta'))} / "
                f"MDD delta {_format_percent(worst_weight.get('MDD Delta'))}"
            ),
            "Why It Matters": "목표 비중이 조금 달라져도 결과가 과도하게 흔들리는지 봅니다.",
            "Next Check": "비중 변화에 민감하면 rebalancing drift trigger를 좁힙니다.",
        },
        {
            "Check": "Strategy runtime follow-up",
            "Status": "FOLLOW_UP" if runtime_followup_rows else "PASS",
            "Finding": ", ".join(str(row.get("Scenario") or "-") for row in runtime_followup_rows) or "-",
            "Why It Matters": "GTAA interval, MA window 같은 전략 내부 parameter는 curve-only 계산만으로 대체할 수 없습니다.",
            "Next Check": "후속 runtime perturbation이 붙기 전까지는 Final Review에서 별도 확인 항목으로 둡니다.",
        },
    ]
    return {
        "status": status,
        "summary": summary,
        "rows": interpretation_rows,
        "computed_count": len(computed_rows),
        "review_count": len(review_rows),
        "not_run_count": len(not_run_rows),
        "runtime_followup_count": len(runtime_followup_rows),
        "worst_scenario": all_delta_worst.get("Scenario"),
        "worst_cagr_delta": _optional_float(all_delta_worst.get("CAGR Delta")),
        "worst_mdd_delta": _optional_float(all_delta_worst.get("MDD Delta")),
        "trigger_reasons": trigger_reasons,
    }


def _correlation_risk_evidence(component_curves: list[dict[str, Any]]) -> dict[str, Any]:
    returns = _aligned_monthly_returns(component_curves)
    if returns.empty or returns.shape[1] < 2:
        return {
            "status": "NOT_RUN",
            "summary": "component return matrix가 부족해 상관 / 위험기여를 계산하지 못했습니다.",
            "rows": [],
            "metrics": {},
        }
    corr = returns.corr()
    off_diag_values = [
        float(corr.iloc[i, j])
        for i in range(corr.shape[0])
        for j in range(corr.shape[1])
        if i < j and not pd.isna(corr.iloc[i, j])
    ]
    avg_corr = float(np.mean(off_diag_values)) if off_diag_values else None
    max_corr = float(np.max(off_diag_values)) if off_diag_values else None
    vols = returns.std().fillna(0.0)
    weights = np.array([float(item.get("weight") or 0.0) for item in component_curves[: len(vols)]], dtype=float)
    if weights.sum() <= 0:
        weights = np.array([1.0 / len(vols)] * len(vols), dtype=float)
    weights = weights / weights.sum()
    raw_risk = weights * vols.values
    risk_contribution = raw_risk / raw_risk.sum() if raw_risk.sum() > 0 else np.array([0.0] * len(raw_risk))
    max_risk_contribution = float(risk_contribution.max()) if len(risk_contribution) else None
    rows = [
        {
            "Component": component_curves[idx].get("component"),
            "Weight": round(float(weights[idx]) * 100.0, 4),
            "Monthly Vol": float(vols.iloc[idx]),
            "Risk Contribution Proxy": float(risk_contribution[idx]) if idx < len(risk_contribution) else None,
        }
        for idx in range(len(vols))
    ]
    status = "REVIEW" if (max_corr is not None and max_corr > 0.85) or (max_risk_contribution or 0.0) > 0.80 else "PASS"
    return {
        "status": status,
        "summary": f"평균 상관 {avg_corr:.2f}, 최대 risk contribution {max_risk_contribution:.1%}" if avg_corr is not None and max_risk_contribution is not None else "상관 / 위험기여 proxy 계산됨",
        "rows": rows,
        "metrics": {
            "average_correlation": avg_corr,
            "max_correlation": max_corr,
            "max_risk_contribution": max_risk_contribution,
            "monthly_return_rows": len(returns),
        },
    }


def _market_context_evidence(benchmark_curve: pd.DataFrame, *, label: str) -> dict[str, Any]:
    curve = _normalize_result_curve(benchmark_curve)
    if curve.empty or len(curve) < 20:
        return {
            "status": "NOT_RUN",
            "summary": f"{label} proxy 계산에 필요한 benchmark curve가 없습니다.",
            "rows": [],
            "metrics": {},
        }
    recent = curve.tail(min(len(curve), 63)).copy()
    start_balance = _optional_float(recent["Total Balance"].iloc[0])
    end_balance = _optional_float(recent["Total Balance"].iloc[-1])
    recent_return = end_balance / start_balance - 1.0 if start_balance and end_balance is not None else None
    recent_drawdown = float((recent["Total Balance"] / recent["Total Balance"].cummax() - 1).min())
    recent_vol = float(pd.to_numeric(recent["Total Return"], errors="coerce").std() * np.sqrt(252))
    status = "REVIEW" if (recent_drawdown < -0.10 or recent_vol > 0.35) else "PASS"
    return {
        "status": status,
        "summary": f"{label} proxy: recent return {recent_return:.2%}, drawdown {recent_drawdown:.2%}, vol {recent_vol:.2%}" if recent_return is not None else f"{label} proxy 계산됨",
        "rows": [
            {"Metric": "Recent return", "Value": recent_return, "Judgment": "REVIEW" if recent_return is not None and recent_return < -0.10 else "PASS"},
            {"Metric": "Recent drawdown", "Value": recent_drawdown, "Judgment": "REVIEW" if recent_drawdown < -0.10 else "PASS"},
            {"Metric": "Recent annualized vol", "Value": recent_vol, "Judgment": "REVIEW" if recent_vol > 0.35 else "PASS"},
        ],
        "metrics": {
            "recent_return": recent_return,
            "recent_drawdown": recent_drawdown,
            "recent_annualized_vol": recent_vol,
        },
    }
