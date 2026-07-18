from __future__ import annotations

import math
from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime
from typing import Any

import pandas as pd

from app.services.backtest_strategy_catalog import LEVEL1_STRATEGY_MATURITY


BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION = (
    "backtest_analysis_result_workspace_v1"
)


def _strategy_maturity(strategy_choice: str | None) -> str:
    return LEVEL1_STRATEGY_MATURITY.get(str(strategy_choice or ""), "development")


def build_result_lifecycle(
    *,
    result_bundle: Mapping[str, Any] | None,
    current_configuration_fingerprint: str,
    result_configuration_fingerprint: str | None,
    result_requires_rerun: bool,
    is_running: bool,
    last_error: str | None,
    last_error_kind: str | None,
) -> dict[str, Any]:
    """Project run state without discarding the last successful result."""

    result_available = bool(result_bundle)
    fingerprint_matches = bool(
        result_available
        and result_configuration_fingerprint
        and current_configuration_fingerprint == result_configuration_fingerprint
    )
    reference_only = bool(
        result_available
        and (result_requires_rerun or not fingerprint_matches or last_error)
    )

    if is_running:
        state = "running_with_reference" if result_available else "running"
    elif last_error:
        state = "error_with_reference" if result_available else "error"
    elif not result_available:
        state = "hidden"
    elif reference_only:
        state = "stale"
    else:
        state = "fresh"

    display_labels = {
        "hidden": "",
        "running": "첫 결과를 만드는 중",
        "running_with_reference": "새 설정으로 실행 중",
        "error": "실행 결과를 만들지 못했습니다",
        "error_with_reference": "이전 설정 결과 · 참고용",
        "stale": "이전 설정 결과 · 참고용",
        "fresh": "현재 설정 결과",
    }
    return {
        "state": state,
        "display_label": display_labels[state],
        "show_workspace": result_available,
        "result_available": result_available,
        "fingerprint_matches": fingerprint_matches,
        "reference_only": reference_only or state == "running_with_reference",
        "is_running": is_running,
        "error": (
            {
                "kind": str(last_error_kind or "execution_failed"),
                "message": str(last_error),
            }
            if last_error
            else None
        ),
    }


def _core_result_reasons(
    result_bundle: Mapping[str, Any] | None,
) -> list[dict[str, str]]:
    bundle = dict(result_bundle or {})
    meta = dict(bundle.get("meta") or {})
    reasons: list[dict[str, str]] = []
    if not str(meta.get("run_id") or ""):
        reasons.append(
            {
                "root_issue_id": "run_identity",
                "message": "실행 결과 식별자가 없습니다.",
            }
        )
    for key, label in (
        ("summary_df", "성과 요약"),
        ("result_df", "결과 표"),
        ("chart_df", "성과 곡선"),
    ):
        value = bundle.get(key)
        if value is None or bool(getattr(value, "empty", False)):
            reasons.append(
                {
                    "root_issue_id": f"core:{key}",
                    "message": f"{label} 계약이 비어 있습니다.",
                }
            )
    return reasons


def build_level1_technical_handoff_readiness(
    *,
    workspace_kind: str,
    strategy_choice: str | None,
    result_bundle: Mapping[str, Any] | None,
    lifecycle: Mapping[str, Any],
    action_handlers: Mapping[str, Callable[..., Any] | None],
) -> dict[str, Any]:
    """Decide Level2 handoff from Level1-owned technical contracts only."""

    if not lifecycle.get("result_available"):
        return {
            "state": "result_required",
            "label": "결과 준비 필요",
            "can_handoff": False,
            "reasons": [],
            "action": None,
        }
    if (
        workspace_kind == "single_strategy"
        and _strategy_maturity(strategy_choice) != "production"
    ):
        return {
            "state": "unsupported",
            "label": "인계 기능 미지원",
            "can_handoff": False,
            "reasons": [],
            "action": None,
        }
    if not callable(action_handlers.get("save_and_move")):
        return {
            "state": "unsupported",
            "label": "인계 기능 미지원",
            "can_handoff": False,
            "reasons": [],
            "action": None,
        }

    reasons = _core_result_reasons(result_bundle)
    if lifecycle.get("state") != "fresh":
        return {
            "state": "rerun_required",
            "label": "재실행 필요",
            "can_handoff": False,
            "reasons": reasons,
            "action": None,
        }
    if reasons:
        return {
            "state": "result_required",
            "label": "결과 준비 필요",
            "can_handoff": False,
            "reasons": reasons,
            "action": None,
        }
    return {
        "state": "ready",
        "label": "Level2 인계 가능",
        "can_handoff": True,
        "reasons": [],
        "action": {
            "id": "save_and_move",
            "label": "후보로 저장하고 Level2로 이동",
            "enabled": True,
        },
    }


_LEVEL2_QUESTION_SPECS = (
    (
        "benchmark_comparison",
        "benchmark",
        "benchmark_available",
        {False, None, ""},
        "기준지수와 손익·낙폭 비교",
        "동일 기간 기준지수와의 차이를 Practical Validation에서 확인합니다.",
    ),
    (
        "rolling_oos_validation",
        "temporal_validation",
        "rolling_review_status",
        {"review", "not_run", "unavailable", ""},
        "구간별 성과 지속성",
        "rolling/OOS 구간에서 결과가 유지되는지 확인합니다.",
    ),
    (
        "split_oos_validation",
        "temporal_validation",
        "out_of_sample_review_status",
        {"review", "not_run", "unavailable", ""},
        "분할·홀드아웃 재검증",
        "학습 외 구간의 재현성을 확인합니다.",
    ),
    (
        "cost_turnover_realism",
        "execution_realism",
        "net_cost_curve_status",
        {"not_run", "unavailable", "applied_without_turnover_estimate", ""},
        "비용·교체 현실성",
        "turnover와 거래비용 반영 수준을 확인합니다.",
    ),
    (
        "liquidity_realism",
        "execution_realism",
        "liquidity_policy_status",
        {"caution", "review", "unavailable", ""},
        "유동성 적합성",
        "보유 후보의 거래 가능 규모를 확인합니다.",
    ),
    (
        "etf_operability",
        "execution_realism",
        "etf_operability_status",
        {"caution", "review", "unavailable", ""},
        "ETF 운용 가능성",
        "AUM·spread·holdings 근거를 확인합니다.",
    ),
    (
        "regime_validation",
        "temporal_validation",
        "regime_split_validation_status",
        {"review", "not_run", "unavailable", ""},
        "시장 국면별 재현성",
        "상승·하락·중립 국면에서 결과가 유지되는지 확인합니다.",
    ),
    (
        "construction_overlap",
        "execution_realism",
        "construction_risk_status",
        {"review", "not_run", "unavailable", ""},
        "집중도·중복 구성",
        "상위 보유 집중도와 구성 간 중복을 확인합니다.",
    ),
    (
        "latest_data_replay",
        "temporal_validation",
        "latest_data_replay_status",
        {"review", "not_run", "unavailable", ""},
        "최신 데이터 재검증",
        "현재 DB 기준으로 같은 설정을 다시 실행해 차이를 확인합니다.",
    ),
    (
        "evidence_development",
        "execution_realism",
        "evidence_adapter_status",
        {"review", "not_run", "unavailable", ""},
        "추가 검증 근거 필요 여부",
        "현재 근거로 확인할 수 없는 항목은 Level2에서 adapter 개발 필요성을 판단합니다.",
    ),
)


def build_level2_validation_questions(
    *,
    meta: Mapping[str, Any],
    workspace_kind: str,
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> list[dict[str, str]]:
    """Project unresolved practical checks without affecting Level1 readiness."""

    del workspace_kind, component_bundles
    lane_labels = {
        "benchmark": "성과·위험 검증",
        "temporal_validation": "기간·재현성 검증",
        "execution_realism": "실행 현실성 검증",
    }
    rows: list[dict[str, str]] = []
    seen: set[str] = set()
    for question_id, lane, field, unresolved, title, summary in _LEVEL2_QUESTION_SPECS:
        raw = meta.get(field)
        normalized = (
            raw
            if raw is None or isinstance(raw, bool)
            else str(raw).strip().lower()
        )
        if normalized not in unresolved:
            continue
        root = f"level2:{lane}:{question_id}"
        if root in seen:
            continue
        seen.add(root)
        rows.append(
            {
                "question_id": question_id,
                "root_issue_id": root,
                "lane": lane,
                "lane_label": lane_labels[lane],
                "status": "needs_validation",
                "title": title,
                "summary": summary,
            }
        )
    return rows


def _optional_float(value: Any) -> float | None:
    if value is None or isinstance(value, bool):
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    return numeric if math.isfinite(numeric) else None


def _format_percent(value: Any) -> str:
    numeric = _optional_float(value)
    return "-" if numeric is None else f"{numeric:.1%}"


def _format_number(value: Any, *, decimals: int = 1) -> str:
    numeric = _optional_float(value)
    return "-" if numeric is None else f"{numeric:,.{decimals}f}"


def _date_label(value: Any) -> str:
    if value is None:
        return ""
    try:
        timestamp = pd.to_datetime(value, errors="coerce")
    except (TypeError, ValueError):
        return str(value)
    if pd.isna(timestamp):
        return str(value)
    return timestamp.date().isoformat()


def _safe_list(value: Any) -> list[Any]:
    if value is None:
        return []
    if isinstance(value, list):
        return value
    if isinstance(value, tuple):
        return list(value)
    if isinstance(value, pd.Series):
        return value.tolist()
    return []


def _ticker_list(value: Any) -> list[str]:
    return [
        text
        for item in _safe_list(value)
        if (text := str(item or "").strip().upper())
    ]


def _numeric_list(value: Any) -> list[float]:
    rows: list[float] = []
    for item in _safe_list(value):
        numeric = _optional_float(item)
        if numeric is not None:
            rows.append(numeric)
    return rows


def _json_value(value: Any) -> Any:
    if value is None:
        return None
    if isinstance(value, (str, bool, int)):
        return value
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if isinstance(value, (pd.Timestamp, datetime, date)):
        return _date_label(value)
    if isinstance(value, Mapping):
        return {str(key): _json_value(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set, pd.Series)):
        return [_json_value(item) for item in list(value)]
    if hasattr(value, "item"):
        try:
            return _json_value(value.item())
        except (TypeError, ValueError):
            pass
    return str(value)


def _frame(value: Any) -> pd.DataFrame:
    return value.copy() if isinstance(value, pd.DataFrame) else pd.DataFrame()


def _latest_rows(frame: pd.DataFrame) -> pd.DataFrame:
    if frame.empty or "Date" not in frame.columns:
        return frame.reset_index(drop=True)
    result = frame.copy()
    result["__workspace_date"] = pd.to_datetime(result["Date"], errors="coerce")
    return (
        result.sort_values("__workspace_date", na_position="first")
        .drop(columns=["__workspace_date"])
        .reset_index(drop=True)
    )


def _allocation_rows(
    tickers: list[str],
    *,
    weights: list[float] | None = None,
    balances: list[float] | None = None,
    total_balance: float | None = None,
    cash: float | None = None,
) -> list[dict[str, Any]]:
    resolved: list[float] = []
    if weights and len(weights) == len(tickers):
        resolved = list(weights)
    elif (
        balances
        and len(balances) == len(tickers)
        and total_balance is not None
        and total_balance > 0
    ):
        resolved = [float(balance) / total_balance for balance in balances]

    rows = [
        {
            "ticker": ticker,
            "weight": round(resolved[index], 6) if index < len(resolved) else None,
            "weight_label": (
                _format_percent(resolved[index])
                if index < len(resolved)
                else "비중 근거 없음"
            ),
        }
        for index, ticker in enumerate(tickers)
    ]
    cash_weight = (
        float(cash or 0.0) / total_balance
        if total_balance is not None and total_balance > 0
        else 0.0
    )
    if cash_weight > 0 or (not rows and cash and total_balance):
        rows.append(
            {
                "ticker": "현금",
                "weight": round(cash_weight, 6),
                "weight_label": _format_percent(cash_weight),
            }
        )
    return rows


def _summary_row(bundle: Mapping[str, Any]) -> dict[str, Any]:
    summary_df = _frame(bundle.get("summary_df"))
    if summary_df.empty:
        return {}
    return dict(summary_df.iloc[0].to_dict())


def _performance_summary(
    summary_value: Any,
    result_value: Any,
) -> list[dict[str, Any]]:
    summary_df = _frame(summary_value)
    result_df = _latest_rows(_frame(result_value))
    summary = dict(summary_df.iloc[0].to_dict()) if not summary_df.empty else {}

    start_date = summary.get("Start Date")
    end_date = summary.get("End Date")
    if not result_df.empty:
        start_date = start_date or result_df.iloc[0].get("Date")
        end_date = end_date or result_df.iloc[-1].get("Date")

    start_balance = _optional_float(summary.get("Start Balance"))
    end_balance = _optional_float(summary.get("End Balance"))
    if not result_df.empty and "Total Balance" in result_df.columns:
        start_balance = start_balance or _optional_float(
            result_df.iloc[0].get("Total Balance")
        )
        end_balance = end_balance or _optional_float(
            result_df.iloc[-1].get("Total Balance")
        )
    cumulative = (
        end_balance / start_balance - 1.0
        if start_balance is not None and start_balance > 0 and end_balance is not None
        else None
    )
    period_label = (
        f"{_date_label(start_date)} ~ {_date_label(end_date)}"
        if start_date is not None and end_date is not None
        else "-"
    )
    specs = (
        ("period", "검증 기간", period_label, period_label),
        ("cumulative_return", "누적 수익률", cumulative, _format_percent(cumulative)),
        ("cagr", "연환산 수익률", summary.get("CAGR"), _format_percent(summary.get("CAGR"))),
        (
            "maximum_drawdown",
            "최대 낙폭",
            summary.get("Maximum Drawdown"),
            _format_percent(summary.get("Maximum Drawdown")),
        ),
        (
            "sharpe",
            "위험 대비 수익",
            summary.get("Sharpe Ratio"),
            _format_number(summary.get("Sharpe Ratio"), decimals=2),
        ),
        (
            "volatility",
            "변동성",
            summary.get("Standard Deviation"),
            _format_percent(summary.get("Standard Deviation")),
        ),
    )
    return [
        {
            "metric_id": metric_id,
            "label": label,
            "value": _json_value(value),
            "value_label": value_label,
        }
        for metric_id, label, value, value_label in specs
    ]


def _curve_rows(frame: pd.DataFrame, balance_columns: Sequence[str]) -> list[dict[str, Any]]:
    if frame.empty or "Date" not in frame.columns:
        return []
    balance_column = next((column for column in balance_columns if column in frame.columns), None)
    if not balance_column:
        return []
    prepared = pd.DataFrame(
        {
            "date": pd.to_datetime(frame["Date"], errors="coerce"),
            "balance": pd.to_numeric(frame[balance_column], errors="coerce"),
        }
    ).dropna()
    prepared = prepared.sort_values("date").drop_duplicates("date", keep="last")
    return [
        {"date": row.date.date().isoformat(), "balance": float(row.balance)}
        for row in prepared.itertuples(index=False)
    ]


def _normalize_curve(rows: list[dict[str, Any]]) -> list[dict[str, Any]]:
    if not rows:
        return []
    base = _optional_float(rows[0].get("balance"))
    if base is None or base == 0:
        return []
    return [
        {
            "date": str(row["date"]),
            "value": round(float(row["balance"]) / base * 100.0, 6),
            "value_label": f"{float(row['balance']) / base * 100.0:,.1f}",
        }
        for row in rows
    ]


def _chart_projection(bundle: Mapping[str, Any]) -> dict[str, Any]:
    chart_df = _frame(bundle.get("chart_df"))
    result_df = _frame(bundle.get("result_df"))
    source = chart_df if not chart_df.empty else result_df
    strategy_rows = _curve_rows(
        source,
        ("Net Total Balance", "Total Balance", "End Balance"),
    )

    benchmark_frame = _frame(bundle.get("benchmark_chart_df"))
    if benchmark_frame.empty and any(
        column in source.columns
        for column in ("Benchmark Total Balance", "Benchmark Balance")
    ):
        benchmark_frame = source
    benchmark_rows = _curve_rows(
        benchmark_frame,
        ("Benchmark Total Balance", "Benchmark Balance", "Total Balance"),
    )

    if strategy_rows and benchmark_rows:
        common_dates = {row["date"] for row in strategy_rows}.intersection(
            row["date"] for row in benchmark_rows
        )
        strategy_rows = [row for row in strategy_rows if row["date"] in common_dates]
        benchmark_rows = [row for row in benchmark_rows if row["date"] in common_dates]
    strategy_series = _normalize_curve(strategy_rows)
    benchmark_series = _normalize_curve(benchmark_rows)

    markers: list[dict[str, Any]] = []
    if strategy_series:
        high = max(strategy_series, key=lambda row: row["value"])
        low = min(strategy_series, key=lambda row: row["value"])
        for marker_id, label, row in (
            ("high", "최고", high),
            ("low", "최저", low),
        ):
            markers.append({"marker_id": marker_id, "label": label, **row})
        peak = float(strategy_series[0]["value"])
        drawdown_row: dict[str, Any] | None = None
        drawdown_value = 0.0
        for row in strategy_series:
            peak = max(peak, float(row["value"]))
            current = float(row["value"]) / peak - 1.0 if peak else 0.0
            if current < drawdown_value:
                drawdown_value = current
                drawdown_row = row
        if drawdown_row is not None:
            markers.append(
                {
                    "marker_id": "maximum_drawdown",
                    "label": "최대 낙폭",
                    **drawdown_row,
                    "drawdown": round(drawdown_value, 6),
                    "drawdown_label": _format_percent(drawdown_value),
                }
            )

    return {
        "strategy_series": strategy_series,
        "benchmark_series": benchmark_series,
        "markers": markers,
        "benchmark_missing_reason": (
            "동일 기간 기준지수 곡선이 없어 Level2에서 비교합니다."
            if not benchmark_series
            else ""
        ),
    }


def _row_tickers(
    row: Mapping[str, Any],
    *,
    field: str,
    fallback_field: str | None,
    balance_field: str,
    allow_static_equal_weight: bool,
) -> list[str]:
    tickers = _ticker_list(row.get(field))
    if tickers or not allow_static_equal_weight or not fallback_field:
        return tickers
    fallback = _ticker_list(row.get(fallback_field))
    balances = _numeric_list(row.get(balance_field))
    return fallback if fallback and len(fallback) == len(balances) else []


def _single_holdings_projection(bundle: Mapping[str, Any]) -> dict[str, Any]:
    result_df = _latest_rows(_frame(bundle.get("result_df")))
    meta = dict(bundle.get("meta") or {})
    equal_weight = str(meta.get("strategy_key") or "") == "equal_weight"
    if result_df.empty:
        return {
            "as_of": "",
            "target_as_of": "",
            "current_allocation": [],
            "target_allocation": [],
            "additions": [],
            "removals": [],
            "cash": None,
            "status": "unavailable",
            "explanation": "결과 표에 보유 근거가 없습니다.",
            "unavailable_reason": "result_df가 비어 있습니다.",
            "evidence_status": "missing",
        }

    latest = dict(result_df.iloc[-1].to_dict())
    total_balance = _optional_float(latest.get("Total Balance"))
    cash = _optional_float(latest.get("Cash")) or 0.0
    current_tickers = _row_tickers(
        latest,
        field="End Ticker",
        fallback_field="Ticker",
        balance_field="End Balance",
        allow_static_equal_weight=equal_weight,
    )
    current_balances = _numeric_list(latest.get("End Balance"))
    current_weights = _numeric_list(latest.get("End Weight"))
    current_allocation = _allocation_rows(
        current_tickers,
        weights=current_weights,
        balances=current_balances,
        total_balance=total_balance,
        cash=cash,
    )

    target_row: dict[str, Any] | None = None
    for _, candidate in result_df.iloc[::-1].iterrows():
        row = dict(candidate.to_dict())
        candidate_tickers = _row_tickers(
            row,
            field="Next Ticker",
            fallback_field="Ticker",
            balance_field="Next Balance",
            allow_static_equal_weight=equal_weight,
        )
        if candidate_tickers and bool(row.get("Rebalancing")):
            target_row = row
            break
    if target_row is None:
        for _, candidate in result_df.iloc[::-1].iterrows():
            row = dict(candidate.to_dict())
            candidate_tickers = _row_tickers(
                row,
                field="Next Ticker",
                fallback_field="Ticker",
                balance_field="Next Balance",
                allow_static_equal_weight=equal_weight,
            )
            if candidate_tickers:
                target_row = row
                break

    target_allocation: list[dict[str, Any]] = []
    additions: list[str] = []
    removals: list[str] = []
    target_as_of = ""
    if target_row is not None:
        target_tickers = _row_tickers(
            target_row,
            field="Next Ticker",
            fallback_field="Ticker",
            balance_field="Next Balance",
            allow_static_equal_weight=equal_weight,
        )
        target_allocation = _allocation_rows(
            target_tickers,
            weights=_numeric_list(target_row.get("Next Weight")),
            balances=_numeric_list(target_row.get("Next Balance")),
            total_balance=_optional_float(target_row.get("Total Balance")),
        )
        additions = _ticker_list(target_row.get("Added Ticker"))
        removals = _ticker_list(target_row.get("Removed Ticker"))
        target_as_of = _date_label(target_row.get("Date"))

    status = "available"
    unavailable_reason = ""
    if current_allocation and all(row["ticker"] == "현금" for row in current_allocation):
        status = "cash_only"
    elif not current_allocation and not target_allocation:
        status = "unavailable"
        unavailable_reason = (
            "End Ticker/End Balance 또는 명시적 Next 비중 근거가 없습니다."
        )
    elif not bool(latest.get("Rebalancing")):
        status = "hold_current_until_rebalance"

    explanations = {
        "available": "마지막 평가 구성과 마지막 유효 신호의 목표 구성을 비교합니다.",
        "cash_only": "마지막 평가 시점의 모의 포트폴리오는 현금으로만 구성됩니다.",
        "hold_current_until_rebalance": "최신 행은 리밸런싱 시점이 아니므로 다음 리밸런싱까지 현재 구성을 유지합니다.",
        "unavailable": "결과 계약에서 보유 비중을 안전하게 계산할 근거를 찾지 못했습니다.",
    }
    return {
        "as_of": _date_label(latest.get("Date")),
        "target_as_of": target_as_of,
        "current_allocation": current_allocation,
        "target_allocation": target_allocation,
        "additions": additions,
        "removals": removals,
        "cash": cash,
        "status": status,
        "explanation": explanations[status],
        "unavailable_reason": unavailable_reason,
        "evidence_status": "available" if status != "unavailable" else "missing",
    }


def _holdings_projection(
    bundle: Mapping[str, Any],
    *,
    component_bundles: Sequence[Mapping[str, Any]],
) -> dict[str, Any]:
    primary = _single_holdings_projection(bundle)
    if not component_bundles:
        return primary

    components: list[dict[str, Any]] = []
    all_targets_available = True
    aggregated: dict[str, float] = {}
    for index, component in enumerate(component_bundles):
        projection = _single_holdings_projection(component)
        meta = dict(component.get("meta") or {})
        component_weight = _optional_float(
            meta.get("component_weight") or component.get("weight")
        )
        components.append(
            {
                "component_id": str(
                    meta.get("component_id") or f"component-{index + 1}"
                ),
                "label": str(
                    component.get("strategy_name")
                    or meta.get("strategy_name")
                    or f"구성 {index + 1}"
                ),
                "weight": component_weight,
                "target_allocation": projection["target_allocation"],
                "status": projection["status"],
            }
        )
        target_rows = projection["target_allocation"]
        if component_weight is None or not target_rows or any(
            row.get("weight") is None for row in target_rows
        ):
            all_targets_available = False
            continue
        for row in target_rows:
            ticker = str(row["ticker"])
            aggregated[ticker] = aggregated.get(ticker, 0.0) + (
                component_weight * float(row["weight"])
            )

    primary["components"] = components
    if all_targets_available and components:
        primary["target_allocation"] = [
            {
                "ticker": ticker,
                "weight": round(weight, 6),
                "weight_label": _format_percent(weight),
            }
            for ticker, weight in sorted(
                aggregated.items(), key=lambda item: item[1], reverse=True
            )
        ]
        primary["evidence_status"] = "available"
        if primary["status"] == "unavailable":
            primary["status"] = "available"
    else:
        primary["status"] = "partial"
        primary["evidence_status"] = "partial"
        primary["explanation"] = (
            "구성별 목표 근거는 표시하지만 모든 비중 근거가 없어 통합 종목 비중은 계산하지 않습니다."
        )
    return primary


def _performance_rows(result_value: Any) -> list[dict[str, Any]]:
    frame = _latest_rows(_frame(result_value)).tail(420)
    if frame.empty:
        return []
    running_peak: float | None = None
    previous_balance: float | None = None
    rows: list[dict[str, Any]] = []
    for _, source in frame.iterrows():
        row = dict(source.to_dict())
        balance = _optional_float(row.get("Total Balance"))
        if balance is not None:
            running_peak = balance if running_peak is None else max(running_peak, balance)
        period_return = next(
            (
                value
                for key in ("Period Return", "Return", "Total Return")
                if (value := _optional_float(row.get(key))) is not None
            ),
            None,
        )
        if period_return is None and balance is not None and previous_balance:
            period_return = balance / previous_balance - 1.0
        drawdown = _optional_float(row.get("Drawdown"))
        if drawdown is None and balance is not None and running_peak:
            drawdown = balance / running_peak - 1.0
        current_tickers = _ticker_list(row.get("End Ticker")) or _ticker_list(
            row.get("Ticker")
        )
        turnover = next(
            (
                value
                for key in ("Turnover", "Portfolio Turnover", "turnover")
                if (value := _optional_float(row.get(key))) is not None
            ),
            None,
        )
        cost = next(
            (
                value
                for key in ("Transaction Cost", "Trading Cost", "Cost")
                if (value := _optional_float(row.get(key))) is not None
            ),
            None,
        )
        rows.append(
            {
                "date": _date_label(row.get("Date")),
                "balance": _format_number(balance, decimals=2),
                "period_return": _format_percent(period_return),
                "drawdown": _format_percent(drawdown),
                "holding_count": len(current_tickers),
                "turnover": _format_percent(turnover),
                "cost": _format_number(cost, decimals=2),
            }
        )
        if balance is not None:
            previous_balance = balance
    return rows


def _holding_change_rows(result_value: Any) -> list[dict[str, Any]]:
    frame = _latest_rows(_frame(result_value)).tail(420)
    rows: list[dict[str, Any]] = []
    for _, source in frame.iterrows():
        row = dict(source.to_dict())
        current = _ticker_list(row.get("End Ticker")) or _ticker_list(row.get("Ticker"))
        target = _ticker_list(row.get("Next Ticker")) or current
        state = "리밸런싱" if bool(row.get("Rebalancing")) else "유지"
        rows.append(
            {
                "date": _date_label(row.get("Date")),
                "state": state,
                "current": ", ".join(current) or "-",
                "target": ", ".join(target) or "-",
                "additions": ", ".join(_ticker_list(row.get("Added Ticker"))) or "-",
                "removals": ", ".join(_ticker_list(row.get("Removed Ticker"))) or "-",
                "cash": _format_number(row.get("Cash"), decimals=2),
            }
        )
    return rows


def _evidence_groups(bundle: Mapping[str, Any]) -> list[dict[str, Any]]:
    meta = dict(bundle.get("meta") or {})
    summary = _summary_row(bundle)
    result_df = _frame(bundle.get("result_df"))
    specs = (
        (
            "performance_risk",
            "성과·위험",
            "수익, 낙폭과 기준지수 비교 근거",
            (
                ("연환산 수익률", _format_percent(summary.get("CAGR"))),
                ("최대 낙폭", _format_percent(summary.get("Maximum Drawdown"))),
                (
                    "기준지수",
                    str(meta.get("benchmark_label") or meta.get("benchmark_ticker") or "Level2 확인"),
                ),
            ),
        ),
        (
            "selection_holdings",
            "선택·보유",
            "보유 구성과 변경 이력 근거",
            (
                ("결과 행", f"{len(result_df):,}개"),
                ("전략", str(bundle.get("strategy_name") or meta.get("strategy_key") or "-")),
                ("구성 위험", str(meta.get("construction_risk_status") or "Level2 확인")),
            ),
        ),
        (
            "execution_realism",
            "실행 현실성",
            "비용, 교체와 운용 가능성 근거",
            (
                ("거래비용", _format_number(meta.get("transaction_cost_bps"), decimals=1)),
                ("유동성", str(meta.get("liquidity_policy_status") or "Level2 확인")),
                ("ETF 운용", str(meta.get("etf_operability_status") or "Level2 확인")),
            ),
        ),
        (
            "data_trust",
            "데이터 신뢰",
            "계산 기준일과 데이터 준비 근거",
            (
                ("가격 최신성", str(dict(meta.get("price_freshness") or {}).get("status") or "-")),
                ("Universe", str(meta.get("universe") or meta.get("universe_name") or "-")),
                ("Factor 준비", str(meta.get("factor_readiness_status") or "해당 없음")),
            ),
        ),
    )
    return [
        {
            "group_id": group_id,
            "label": label,
            "summary": description,
            "items": [
                {"label": item_label, "value": item_value}
                for item_label, item_value in items
            ],
        }
        for group_id, label, description, items in specs
    ]


def _technical_appendix(bundle: Mapping[str, Any]) -> dict[str, Any]:
    result_df = _frame(bundle.get("result_df"))
    prepared_rows = [
        {str(key): _json_value(value) for key, value in row.items()}
        for row in result_df.head(100).to_dict(orient="records")
    ]
    meta = dict(bundle.get("meta") or {})
    return {
        "row_count": len(result_df),
        "columns": [str(column) for column in result_df.columns],
        "prepared_rows": prepared_rows,
        "preview_limited": len(result_df) > len(prepared_rows),
        "meta_rows": [
            {"key": str(key), "value": _json_value(value)}
            for key, value in sorted(meta.items(), key=lambda item: str(item[0]))
        ],
    }


def build_backtest_analysis_result_workspace(
    *,
    workspace_kind: str,
    strategy_choice: str | None,
    result_bundle: Mapping[str, Any] | None,
    current_configuration_fingerprint: str,
    result_configuration_fingerprint: str | None,
    result_requires_rerun: bool,
    is_running: bool,
    last_error: str | None,
    last_error_kind: str | None,
    action_handlers: Mapping[str, Callable[..., Any] | None],
    component_bundles: Sequence[Mapping[str, Any]] = (),
) -> dict[str, Any]:
    """Build the JSON-ready Level1 result workspace for every renderer."""

    lifecycle = build_result_lifecycle(
        result_bundle=result_bundle,
        current_configuration_fingerprint=current_configuration_fingerprint,
        result_configuration_fingerprint=result_configuration_fingerprint,
        result_requires_rerun=result_requires_rerun,
        is_running=is_running,
        last_error=last_error,
        last_error_kind=last_error_kind,
    )
    if not lifecycle["show_workspace"]:
        return {
            "schema_version": BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION,
            "visible": False,
            "lifecycle": lifecycle,
        }

    bundle = dict(result_bundle or {})
    meta = dict(bundle.get("meta") or {})
    readiness = build_level1_technical_handoff_readiness(
        workspace_kind=workspace_kind,
        strategy_choice=strategy_choice,
        result_bundle=bundle,
        lifecycle=lifecycle,
        action_handlers=action_handlers,
    )
    summary = _performance_summary(bundle.get("summary_df"), bundle.get("result_df"))
    period_label = next(
        (
            str(item.get("value_label") or "")
            for item in summary
            if item.get("metric_id") == "period"
        ),
        "",
    )
    return {
        "schema_version": BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION,
        "visible": True,
        "configuration_fingerprint": current_configuration_fingerprint,
        "lifecycle": lifecycle,
        "identity": {
            "run_result_id": str(meta.get("run_id") or ""),
            "candidate_source_id": str(meta.get("selection_source_id") or ""),
            "validation_result_id": str(meta.get("validation_result_id") or ""),
            "strategy_name": str(
                bundle.get("strategy_name") or strategy_choice or "Portfolio Mix"
            ),
            "variant_name": str(meta.get("variant") or ""),
            "run_at": _date_label(meta.get("run_at") or meta.get("created_at")),
            "period_label": period_label,
        },
        "performance_summary": summary,
        "chart": _chart_projection(bundle),
        "holdings": _holdings_projection(
            bundle,
            component_bundles=component_bundles,
        ),
        "technical_handoff_readiness": readiness,
        "level2_validation_questions": build_level2_validation_questions(
            meta=meta,
            workspace_kind=workspace_kind,
            component_bundles=component_bundles,
        ),
        "evidence_groups": _evidence_groups(bundle),
        "performance_rows": _performance_rows(bundle.get("result_df")),
        "holding_change_rows": _holding_change_rows(bundle.get("result_df")),
        "technical_appendix": _technical_appendix(bundle),
        "actions": (
            {"save_and_move": readiness["action"]}
            if readiness.get("action")
            else {}
        ),
        "boundaries": {
            "react_calculates_gate": False,
            "react_calculates_weights": False,
            "react_classifies_status": False,
            "python_validates_intent": True,
        },
    }


__all__ = [
    "BACKTEST_ANALYSIS_RESULT_WORKSPACE_SCHEMA_VERSION",
    "build_level1_technical_handoff_readiness",
    "build_level2_validation_questions",
    "build_backtest_analysis_result_workspace",
    "build_result_lifecycle",
]
