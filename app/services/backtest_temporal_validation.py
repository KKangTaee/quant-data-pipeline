from __future__ import annotations

from typing import Any

import pandas as pd

from app.services.backtest_practical_validation_curve import normalize_result_curve


WALKFORWARD_VALIDATION_SCHEMA_VERSION = "walkforward_validation_contract_v1"
OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION = "oos_holdout_validation_contract_v1"
REGIME_SPLIT_VALIDATION_SCHEMA_VERSION = "regime_split_validation_contract_v1"
REGIME_MACRO_SERIES = ("VIXCLS", "T10Y3M", "BAA10Y")


def _safe_text(value: Any, fallback: str = "-") -> str:
    text = str(value or "").strip()
    return text or fallback


def _optional_float(value: Any) -> float | None:
    try:
        if value in (None, ""):
            return None
        return float(value)
    except (TypeError, ValueError):
        return None


def _date_text(value: Any) -> str:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return "-"
    return parsed.strftime("%Y-%m-%d")


def _pct_text(value: Any) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:.2%}"


def _result(
    *,
    status: str,
    summary: str,
    schema_version: str = WALKFORWARD_VALIDATION_SCHEMA_VERSION,
    rows: list[dict[str, Any]] | None = None,
    metrics: dict[str, Any] | None = None,
    limitations: list[str] | None = None,
    next_action: str | None = None,
) -> dict[str, Any]:
    return {
        "schema_version": schema_version,
        "status": status,
        "summary": summary,
        "rows": list(rows or []),
        "metrics": dict(metrics or {}),
        "limitations": list(limitations or []),
        "next_action": next_action or ("추가 조치 없음" if status == "PASS" else "walk-forward evidence를 보강합니다."),
        "write_policy": "read_only_temporal_validation",
        "db_write": False,
        "registry_write": False,
        "memo_persistence": False,
    }


def _monthly_curve(value: Any) -> pd.DataFrame:
    curve = normalize_result_curve(value)
    if curve.empty:
        return pd.DataFrame()
    monthly = (
        curve.assign(_month=curve["Date"].dt.to_period("M"))
        .groupby("_month", as_index=False)
        .tail(1)
        .sort_values("Date")
        .reset_index(drop=True)
    )
    return monthly[["Date", "Total Balance", "Total Return"]]


def _total_return(values: pd.Series) -> float | None:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if len(numeric) < 2:
        return None
    start = _optional_float(numeric.iloc[0])
    end = _optional_float(numeric.iloc[-1])
    if start is None or end is None or start <= 0:
        return None
    return float(end / start - 1.0)


def _max_drawdown(values: pd.Series) -> float | None:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if len(numeric) < 2:
        return None
    running_max = numeric.cummax()
    drawdown = numeric / running_max - 1.0
    return float(drawdown.min())


def _status_from_rows(rows: list[dict[str, Any]]) -> str:
    statuses = {str(row.get("Status") or "").upper() for row in rows}
    if "BLOCKED" in statuses:
        return "BLOCKED"
    if "NEEDS_INPUT" in statuses:
        return "NEEDS_INPUT"
    if "REVIEW" in statuses:
        return "REVIEW"
    return "PASS"


def _source_is_proxy(*values: Any) -> bool:
    text = " ".join(str(value or "").lower() for value in values)
    return "proxy" in text or "bridge" in text


def _aligned_monthly_curves(portfolio_curve: Any, benchmark_curve: Any) -> tuple[pd.DataFrame, int, int]:
    portfolio_monthly = _monthly_curve(portfolio_curve)
    benchmark_monthly = _monthly_curve(benchmark_curve)
    if portfolio_monthly.empty or benchmark_monthly.empty:
        return pd.DataFrame(), int(len(portfolio_monthly)), int(len(benchmark_monthly))
    portfolio = portfolio_monthly.rename(
        columns={"Date": "portfolio_date", "Total Balance": "portfolio_balance"}
    ).copy()
    benchmark = benchmark_monthly.rename(
        columns={"Date": "benchmark_date", "Total Balance": "benchmark_balance"}
    ).copy()
    portfolio["_month"] = portfolio["portfolio_date"].dt.to_period("M")
    benchmark["_month"] = benchmark["benchmark_date"].dt.to_period("M")
    aligned = (
        pd.merge(
            portfolio[["_month", "portfolio_date", "portfolio_balance"]],
            benchmark[["_month", "benchmark_date", "benchmark_balance"]],
            on="_month",
            how="inner",
        )
        .dropna(subset=["portfolio_balance", "benchmark_balance"])
        .sort_values("_month")
        .reset_index(drop=True)
    )
    return aligned, int(len(portfolio_monthly)), int(len(benchmark_monthly))


def _compound_return(values: pd.Series) -> float | None:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return None
    return float((1.0 + numeric).prod() - 1.0)


def _drawdown_from_returns(values: pd.Series) -> float | None:
    numeric = pd.to_numeric(values, errors="coerce").dropna()
    if numeric.empty:
        return None
    balance = (1.0 + numeric).cumprod()
    drawdown = balance / balance.cummax() - 1.0
    return float(drawdown.min())


def _macro_observations_frame(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        frame = value.copy()
    elif isinstance(value, list):
        frame = pd.DataFrame(value)
    else:
        return pd.DataFrame()
    if frame.empty or "series_id" not in frame.columns or "observation_date" not in frame.columns:
        return pd.DataFrame()
    work = frame.copy()
    for column in ("value", "coverage_status", "source_type", "source", "source_mode"):
        if column not in work.columns:
            work[column] = None
    work["series_id"] = work["series_id"].astype(str).str.upper()
    work["observation_date"] = pd.to_datetime(work["observation_date"], errors="coerce")
    work["value"] = pd.to_numeric(work["value"], errors="coerce")
    work = work.dropna(subset=["series_id", "observation_date", "value"]).sort_values("observation_date")
    if work.empty:
        return pd.DataFrame()
    return work[
        [
            "series_id",
            "observation_date",
            "value",
            "coverage_status",
            "source_type",
            "source",
            "source_mode",
        ]
    ].reset_index(drop=True)


def _macro_regime_label(values: dict[str, float]) -> tuple[str, list[str]]:
    reasons: list[str] = []
    vix = values.get("VIXCLS")
    curve = values.get("T10Y3M")
    credit = values.get("BAA10Y")
    if vix is not None and vix >= 30.0:
        reasons.append("VIX >= 30")
    if curve is not None and curve < 0.0:
        reasons.append("yield curve inverted")
    if credit is not None and credit >= 3.0:
        reasons.append("credit spread >= 3")
    if reasons:
        return "risk_off", reasons
    if vix is not None and vix >= 20.0:
        reasons.append("VIX >= 20")
    if curve is not None and curve < 0.5:
        reasons.append("yield curve < 0.5")
    if credit is not None and credit >= 2.5:
        reasons.append("credit spread >= 2.5")
    if reasons:
        return "caution", reasons
    return "neutral", ["macro thresholds neutral"]


def _monthly_macro_regimes(macro_observations: Any) -> tuple[pd.DataFrame, dict[str, Any]]:
    frame = _macro_observations_frame(macro_observations)
    if frame.empty:
        return pd.DataFrame(), {
            "macro_rows": 0,
            "macro_months": 0,
            "recognized_series": [],
            "source_types": [],
            "coverage_statuses": [],
            "sources": [],
        }
    work = frame.copy()
    work["_month"] = work["observation_date"].dt.to_period("M")
    recognized = work[work["series_id"].isin(REGIME_MACRO_SERIES)].copy()
    if recognized.empty:
        return pd.DataFrame(), {
            "macro_rows": int(len(work)),
            "macro_months": 0,
            "recognized_series": [],
            "source_types": sorted(set(work["source_type"].dropna().astype(str).str.lower())),
            "coverage_statuses": sorted(set(work["coverage_status"].dropna().astype(str).str.lower())),
            "sources": sorted(set(work["source"].dropna().astype(str).str.lower())),
        }
    latest = recognized.groupby(["_month", "series_id"], as_index=False).tail(1).sort_values(["_month", "series_id"])
    rows: list[dict[str, Any]] = []
    for month, month_frame in latest.groupby("_month", sort=True):
        values = {
            str(row.get("series_id") or "").upper(): float(row.get("value"))
            for _, row in month_frame.iterrows()
            if str(row.get("series_id") or "").upper() in REGIME_MACRO_SERIES
        }
        if not values:
            continue
        label, reasons = _macro_regime_label(values)
        rows.append(
            {
                "_month": month,
                "regime_bucket": label,
                "regime_reasons": ", ".join(reasons),
                "macro_series_count": len(values),
                "macro_values": values,
                "coverage_statuses": sorted(
                    set(month_frame["coverage_status"].dropna().astype(str).str.lower())
                ),
                "source_types": sorted(set(month_frame["source_type"].dropna().astype(str).str.lower())),
                "sources": sorted(set(month_frame["source"].dropna().astype(str).str.lower())),
            }
        )
    monthly = pd.DataFrame(rows)
    meta = {
        "macro_rows": int(len(recognized)),
        "macro_months": int(len(monthly)),
        "recognized_series": sorted(set(recognized["series_id"].astype(str).str.upper())),
        "source_types": sorted(set(recognized["source_type"].dropna().astype(str).str.lower())),
        "coverage_statuses": sorted(set(recognized["coverage_status"].dropna().astype(str).str.lower())),
        "sources": sorted(set(recognized["source"].dropna().astype(str).str.lower())),
    }
    return monthly, meta


def build_walkforward_validation(
    portfolio_curve: Any,
    benchmark_curve: Any,
    *,
    portfolio_curve_source: Any = None,
    benchmark_curve_source: Any = None,
    benchmark_parity: dict[str, Any] | None = None,
    window_months: int = 36,
    min_windows: int = 3,
    min_excess_return: float = 0.0,
    max_negative_excess_share: float = 0.35,
    max_drawdown_gap: float = -0.05,
    allow_proxy_pass: bool = False,
) -> dict[str, Any]:
    """Build compact benchmark-aligned walk-forward evidence without persistence."""

    window_months = max(3, int(window_months or 36))
    min_windows = max(1, int(min_windows or 1))
    portfolio_monthly = _monthly_curve(portfolio_curve)
    if portfolio_monthly.empty:
        return _result(
            status="NEEDS_INPUT",
            summary="portfolio curve가 없어 walk-forward 검증을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Walk-forward curve source",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(portfolio_curve_source, "missing"),
                    "Evidence": "portfolio curve missing",
                    "Meaning": "walk-forward 검증에는 월별 portfolio curve가 필요합니다.",
                }
            ],
            metrics={"window_months": window_months, "window_count": 0},
            next_action="runtime replay 또는 source curve evidence를 먼저 보강합니다.",
        )
    benchmark_monthly = _monthly_curve(benchmark_curve)
    if benchmark_monthly.empty:
        return _result(
            status="NEEDS_INPUT",
            summary="benchmark curve가 없어 상대 walk-forward 검증을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Walk-forward benchmark curve",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(benchmark_curve_source, "missing"),
                    "Evidence": "benchmark curve missing",
                    "Meaning": "benchmark가 없으면 rolling excess return과 drawdown gap을 판단할 수 없습니다.",
                }
            ],
            metrics={
                "window_months": window_months,
                "portfolio_months": int(len(portfolio_monthly)),
                "benchmark_months": 0,
                "window_count": 0,
            },
            next_action="같은 기간 / frequency / coverage의 benchmark curve를 보강합니다.",
        )

    aligned, _, _ = _aligned_monthly_curves(portfolio_curve, benchmark_curve)
    common_months = int(len(aligned))
    if common_months < window_months + min_windows:
        return _result(
            status="NEEDS_INPUT",
            summary=(
                f"{window_months}개월 walk-forward window를 만들기에 공통 월 데이터가 부족합니다 "
                f"({common_months} common months)."
            ),
            rows=[
                {
                    "Criteria": "Walk-forward aligned history",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": f"{common_months} common months",
                    "Evidence": f"required >= {window_months + min_windows}",
                    "Meaning": "짧은 기간에서는 split evidence를 pass로 볼 수 없습니다.",
                }
            ],
            metrics={
                "window_months": window_months,
                "portfolio_months": int(len(portfolio_monthly)),
                "benchmark_months": int(len(benchmark_monthly)),
                "common_months": common_months,
                "window_count": 0,
            },
            next_action="더 긴 기간의 runtime replay 또는 benchmark history를 확보합니다.",
        )

    window_rows: list[dict[str, Any]] = []
    for end_idx in range(window_months, len(aligned)):
        window = aligned.iloc[end_idx - window_months : end_idx + 1].copy()
        portfolio_return = _total_return(window["portfolio_balance"])
        benchmark_return = _total_return(window["benchmark_balance"])
        portfolio_mdd = _max_drawdown(window["portfolio_balance"])
        benchmark_mdd = _max_drawdown(window["benchmark_balance"])
        if portfolio_return is None or benchmark_return is None or portfolio_mdd is None or benchmark_mdd is None:
            continue
        excess_return = float(portfolio_return - benchmark_return)
        drawdown_gap = float(portfolio_mdd - benchmark_mdd)
        window_rows.append(
            {
                "Start": _date_text(window["portfolio_date"].iloc[0]),
                "End": _date_text(window["portfolio_date"].iloc[-1]),
                "Window Months": window_months,
                "Portfolio Return": portfolio_return,
                "Benchmark Return": benchmark_return,
                "Excess Return": excess_return,
                "Portfolio MDD": portfolio_mdd,
                "Benchmark MDD": benchmark_mdd,
                "Drawdown Gap": drawdown_gap,
            }
        )
    if len(window_rows) < min_windows:
        return _result(
            status="NEEDS_INPUT",
            summary=f"계산 가능한 walk-forward window가 부족합니다 ({len(window_rows)} windows).",
            rows=[
                {
                    "Criteria": "Walk-forward computed windows",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": str(len(window_rows)),
                    "Evidence": f"required >= {min_windows}",
                    "Meaning": "계산 가능한 rolling window가 부족하면 실전 검증 근거가 아닙니다.",
                }
            ],
            metrics={"window_months": window_months, "common_months": common_months, "window_count": len(window_rows)},
            next_action="curve alignment와 benchmark coverage를 확인합니다.",
        )

    worst_excess_row = min(window_rows, key=lambda row: float(row["Excess Return"]))
    worst_gap_row = min(window_rows, key=lambda row: float(row["Drawdown Gap"]))
    excess_values = [float(row["Excess Return"]) for row in window_rows]
    negative_excess_share = sum(1 for value in excess_values if value < min_excess_return) / len(excess_values)
    benchmark_parity_status = str(dict(benchmark_parity or {}).get("status") or "").upper()
    source_proxy = _source_is_proxy(portfolio_curve_source, benchmark_curve_source)
    rows = [
        {
            "Criteria": "Walk-forward windows",
            "Status": "PASS",
            "Ready": True,
            "Current": f"{len(window_rows)} windows / {common_months} common months",
            "Evidence": f"{window_months}M benchmark-aligned windows",
            "Meaning": "전체기간 1회 결과가 아니라 여러 rolling 구간에서 상대 성과를 확인합니다.",
        },
        {
            "Criteria": "Worst rolling excess return",
            "Status": "REVIEW" if float(worst_excess_row["Excess Return"]) < min_excess_return else "PASS",
            "Ready": float(worst_excess_row["Excess Return"]) >= min_excess_return,
            "Current": _pct_text(worst_excess_row["Excess Return"]),
            "Evidence": f"{worst_excess_row['Start']} -> {worst_excess_row['End']}",
            "Meaning": "가장 약한 rolling 구간에서도 benchmark 대비 초과성과가 유지되는지 확인합니다.",
        },
        {
            "Criteria": "Negative excess window share",
            "Status": "REVIEW" if negative_excess_share > max_negative_excess_share else "PASS",
            "Ready": negative_excess_share <= max_negative_excess_share,
            "Current": _pct_text(negative_excess_share),
            "Evidence": f"threshold <= {_pct_text(max_negative_excess_share)}",
            "Meaning": "benchmark를 밑돈 rolling 구간이 과도하게 많지 않은지 확인합니다.",
        },
        {
            "Criteria": "Worst drawdown gap",
            "Status": "REVIEW" if float(worst_gap_row["Drawdown Gap"]) < max_drawdown_gap else "PASS",
            "Ready": float(worst_gap_row["Drawdown Gap"]) >= max_drawdown_gap,
            "Current": _pct_text(worst_gap_row["Drawdown Gap"]),
            "Evidence": f"{worst_gap_row['Start']} -> {worst_gap_row['End']}",
            "Meaning": "나쁜 구간에서 strategy drawdown이 benchmark보다 과도하게 깊어지는지 봅니다.",
        },
    ]
    source_status = "PASS"
    source_evidence = "runtime or embedded curve evidence"
    limitations: list[str] = []
    if benchmark_parity_status and benchmark_parity_status != "PASS":
        source_status = "REVIEW"
        source_evidence = f"benchmark parity={benchmark_parity_status}"
        limitations.append("Benchmark parity가 PASS가 아니면 상대 walk-forward 판단은 REVIEW로 남깁니다.")
    if source_proxy and not allow_proxy_pass:
        source_status = "REVIEW"
        source_evidence = "proxy curve source"
        limitations.append("DB price proxy 또는 component proxy curve만으로는 walk-forward evidence를 PASS로 보지 않습니다.")
    rows.append(
        {
            "Criteria": "Walk-forward source strength",
            "Status": source_status,
            "Ready": source_status == "PASS",
            "Current": f"portfolio={_safe_text(portfolio_curve_source)} / benchmark={_safe_text(benchmark_curve_source)}",
            "Evidence": source_evidence,
            "Meaning": "runtime replay / embedded result / DB proxy evidence strength를 구분합니다.",
        }
    )
    status = _status_from_rows(rows)
    worst_excess = float(worst_excess_row["Excess Return"])
    worst_gap = float(worst_gap_row["Drawdown Gap"])
    summary = (
        f"{window_months}M walk-forward {len(window_rows)} windows: "
        f"worst excess {_pct_text(worst_excess)}, negative share {_pct_text(negative_excess_share)}, "
        f"worst drawdown gap {_pct_text(worst_gap)}."
    )
    metrics = {
        "window_months": window_months,
        "window_count": len(window_rows),
        "portfolio_months": int(len(portfolio_monthly)),
        "benchmark_months": int(len(benchmark_monthly)),
        "common_months": common_months,
        "worst_rolling_excess_return": worst_excess,
        "negative_excess_window_share": negative_excess_share,
        "worst_drawdown_gap": worst_gap,
        "worst_strategy_mdd": float(worst_gap_row["Portfolio MDD"]),
        "worst_benchmark_mdd": float(worst_gap_row["Benchmark MDD"]),
        "portfolio_curve_source": _safe_text(portfolio_curve_source),
        "benchmark_curve_source": _safe_text(benchmark_curve_source),
        "benchmark_parity_status": benchmark_parity_status or "-",
        "proxy_evidence": source_proxy,
        "window_rows_preview": window_rows[-12:],
    }
    next_action = (
        "walk-forward REVIEW 항목을 Final Review 판단 사유로 남기거나 runtime replay / benchmark parity를 보강합니다."
        if status != "PASS"
        else "Final Review에서 다른 audit row와 함께 확인합니다."
    )
    return _result(
        status=status,
        summary=summary,
        rows=rows,
        metrics=metrics,
        limitations=limitations,
        next_action=next_action,
    )


def build_oos_holdout_validation(
    portfolio_curve: Any,
    benchmark_curve: Any,
    *,
    portfolio_curve_source: Any = None,
    benchmark_curve_source: Any = None,
    benchmark_parity: dict[str, Any] | None = None,
    split_ratio: float = 0.5,
    min_sample_months: int = 12,
    min_out_sample_excess_return: float = 0.0,
    max_excess_deterioration: float = -0.10,
    max_out_sample_drawdown_gap: float = -0.05,
    allow_proxy_pass: bool = False,
) -> dict[str, Any]:
    """Build compact in-sample / out-of-sample holdout evidence without persistence."""

    split_ratio_value = _optional_float(split_ratio)
    split_ratio = min(max(split_ratio_value if split_ratio_value is not None else 0.5, 0.2), 0.8)
    min_sample_months_value = _optional_float(min_sample_months)
    min_sample_months = max(3, int(min_sample_months_value or 12))
    portfolio_monthly = _monthly_curve(portfolio_curve)
    if portfolio_monthly.empty:
        return _result(
            schema_version=OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="portfolio curve가 없어 OOS holdout 검증을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "OOS portfolio curve",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(portfolio_curve_source, "missing"),
                    "Evidence": "portfolio curve missing",
                    "Meaning": "OOS holdout 검증에는 월별 portfolio curve가 필요합니다.",
                }
            ],
            metrics={"common_months": 0, "in_sample_months": 0, "out_sample_months": 0},
            next_action="runtime replay 또는 source curve evidence를 먼저 보강합니다.",
        )
    benchmark_monthly = _monthly_curve(benchmark_curve)
    if benchmark_monthly.empty:
        return _result(
            schema_version=OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="benchmark curve가 없어 OOS holdout 상대 검증을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "OOS benchmark curve",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(benchmark_curve_source, "missing"),
                    "Evidence": "benchmark curve missing",
                    "Meaning": "benchmark가 없으면 OOS excess return과 drawdown gap을 판단할 수 없습니다.",
                }
            ],
            metrics={
                "portfolio_months": int(len(portfolio_monthly)),
                "benchmark_months": 0,
                "common_months": 0,
            },
            next_action="같은 기간 / frequency / coverage의 benchmark curve를 보강합니다.",
        )

    aligned, portfolio_months, benchmark_months = _aligned_monthly_curves(portfolio_curve, benchmark_curve)
    common_months = int(len(aligned))
    required_months = min_sample_months * 2
    if common_months < required_months:
        return _result(
            schema_version=OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary=(
                f"OOS holdout split을 만들기에 공통 월 데이터가 부족합니다 "
                f"({common_months} common months, required >= {required_months})."
            ),
            rows=[
                {
                    "Criteria": "OOS aligned history",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": f"{common_months} common months",
                    "Evidence": f"required >= {required_months}",
                    "Meaning": "짧은 기간에서는 in-sample / out-sample split을 pass로 볼 수 없습니다.",
                }
            ],
            metrics={
                "portfolio_months": portfolio_months,
                "benchmark_months": benchmark_months,
                "common_months": common_months,
                "in_sample_months": 0,
                "out_sample_months": 0,
            },
            next_action="더 긴 기간의 runtime replay 또는 benchmark history를 확보합니다.",
        )

    split_index = int(round(common_months * split_ratio))
    split_index = min(max(split_index, min_sample_months), common_months - min_sample_months)
    in_sample = aligned.iloc[:split_index].copy()
    out_sample = aligned.iloc[split_index:].copy()
    if len(in_sample) < min_sample_months or len(out_sample) < min_sample_months:
        return _result(
            schema_version=OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary=(
                f"OOS holdout split sample이 부족합니다 "
                f"(in={len(in_sample)} months, out={len(out_sample)} months)."
            ),
            rows=[
                {
                    "Criteria": "OOS split sample",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": f"in={len(in_sample)} / out={len(out_sample)}",
                    "Evidence": f"min each >= {min_sample_months}",
                    "Meaning": "한쪽 표본이 너무 짧으면 split 성과 차이를 신뢰하기 어렵습니다.",
                }
            ],
            metrics={
                "portfolio_months": portfolio_months,
                "benchmark_months": benchmark_months,
                "common_months": common_months,
                "in_sample_months": len(in_sample),
                "out_sample_months": len(out_sample),
            },
            next_action="split ratio 또는 검증 기간을 조정합니다.",
        )

    in_portfolio_return = _total_return(in_sample["portfolio_balance"])
    in_benchmark_return = _total_return(in_sample["benchmark_balance"])
    out_portfolio_return = _total_return(out_sample["portfolio_balance"])
    out_benchmark_return = _total_return(out_sample["benchmark_balance"])
    in_portfolio_mdd = _max_drawdown(in_sample["portfolio_balance"])
    in_benchmark_mdd = _max_drawdown(in_sample["benchmark_balance"])
    out_portfolio_mdd = _max_drawdown(out_sample["portfolio_balance"])
    out_benchmark_mdd = _max_drawdown(out_sample["benchmark_balance"])
    if any(
        value is None
        for value in (
            in_portfolio_return,
            in_benchmark_return,
            out_portfolio_return,
            out_benchmark_return,
            in_portfolio_mdd,
            in_benchmark_mdd,
            out_portfolio_mdd,
            out_benchmark_mdd,
        )
    ):
        return _result(
            schema_version=OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="OOS holdout metric 계산에 필요한 수익률 / drawdown 값이 부족합니다.",
            rows=[
                {
                    "Criteria": "OOS computed metrics",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "missing",
                    "Evidence": "return or drawdown metric missing",
                    "Meaning": "수익률과 낙폭이 모두 계산되어야 split deterioration을 확인할 수 있습니다.",
                }
            ],
            metrics={
                "common_months": common_months,
                "in_sample_months": len(in_sample),
                "out_sample_months": len(out_sample),
            },
            next_action="curve alignment와 benchmark coverage를 확인합니다.",
        )

    in_excess = float(in_portfolio_return - in_benchmark_return)
    out_excess = float(out_portfolio_return - out_benchmark_return)
    excess_change = float(out_excess - in_excess)
    in_drawdown_gap = float(in_portfolio_mdd - in_benchmark_mdd)
    out_drawdown_gap = float(out_portfolio_mdd - out_benchmark_mdd)
    rows = [
        {
            "Criteria": "OOS split sample",
            "Status": "PASS",
            "Ready": True,
            "Current": f"in={len(in_sample)} / out={len(out_sample)} months",
            "Evidence": f"{_date_text(in_sample['portfolio_date'].iloc[0])} -> {_date_text(out_sample['portfolio_date'].iloc[-1])}",
            "Meaning": "한 번의 전체기간 성과를 앞쪽 학습 구간과 뒤쪽 검증 구간으로 나누어 봅니다.",
        },
        {
            "Criteria": "Out-sample excess return",
            "Status": "REVIEW" if out_excess < min_out_sample_excess_return else "PASS",
            "Ready": out_excess >= min_out_sample_excess_return,
            "Current": _pct_text(out_excess),
            "Evidence": f"threshold >= {_pct_text(min_out_sample_excess_return)}",
            "Meaning": "뒤쪽 holdout 구간에서도 benchmark 대비 성과가 유지되는지 확인합니다.",
        },
        {
            "Criteria": "Split deterioration",
            "Status": "REVIEW" if excess_change < max_excess_deterioration else "PASS",
            "Ready": excess_change >= max_excess_deterioration,
            "Current": _pct_text(excess_change),
            "Evidence": f"in excess {_pct_text(in_excess)} -> out excess {_pct_text(out_excess)}",
            "Meaning": "뒤쪽 구간에서 성과 우위가 앞쪽 구간 대비 급격히 무너지는지 봅니다.",
        },
        {
            "Criteria": "Out-sample drawdown gap",
            "Status": "REVIEW" if out_drawdown_gap < max_out_sample_drawdown_gap else "PASS",
            "Ready": out_drawdown_gap >= max_out_sample_drawdown_gap,
            "Current": _pct_text(out_drawdown_gap),
            "Evidence": f"strategy MDD {_pct_text(out_portfolio_mdd)} / benchmark MDD {_pct_text(out_benchmark_mdd)}",
            "Meaning": "뒤쪽 holdout 구간의 strategy drawdown이 benchmark보다 과도하게 깊어지는지 봅니다.",
        },
    ]
    benchmark_parity_status = str(dict(benchmark_parity or {}).get("status") or "").upper()
    source_proxy = _source_is_proxy(portfolio_curve_source, benchmark_curve_source)
    source_status = "PASS"
    source_evidence = "runtime or embedded curve evidence"
    limitations: list[str] = []
    if benchmark_parity_status and benchmark_parity_status != "PASS":
        source_status = "REVIEW"
        source_evidence = f"benchmark parity={benchmark_parity_status}"
        limitations.append("Benchmark parity가 PASS가 아니면 OOS holdout 판단은 REVIEW로 남깁니다.")
    if source_proxy and not allow_proxy_pass:
        source_status = "REVIEW"
        source_evidence = "proxy curve source"
        limitations.append("DB price proxy 또는 component proxy curve만으로는 OOS holdout evidence를 PASS로 보지 않습니다.")
    rows.append(
        {
            "Criteria": "OOS source strength",
            "Status": source_status,
            "Ready": source_status == "PASS",
            "Current": f"portfolio={_safe_text(portfolio_curve_source)} / benchmark={_safe_text(benchmark_curve_source)}",
            "Evidence": source_evidence,
            "Meaning": "runtime replay / embedded result / DB proxy evidence strength를 구분합니다.",
        }
    )
    status = _status_from_rows(rows)
    summary = (
        f"OOS holdout: in excess {_pct_text(in_excess)}, out excess {_pct_text(out_excess)}, "
        f"change {_pct_text(excess_change)}, out drawdown gap {_pct_text(out_drawdown_gap)}."
    )
    metrics = {
        "split_ratio": split_ratio,
        "portfolio_months": portfolio_months,
        "benchmark_months": benchmark_months,
        "common_months": common_months,
        "in_sample_months": int(len(in_sample)),
        "out_sample_months": int(len(out_sample)),
        "in_sample_start": _date_text(in_sample["portfolio_date"].iloc[0]),
        "in_sample_end": _date_text(in_sample["portfolio_date"].iloc[-1]),
        "out_sample_start": _date_text(out_sample["portfolio_date"].iloc[0]),
        "out_sample_end": _date_text(out_sample["portfolio_date"].iloc[-1]),
        "in_sample_excess_return": in_excess,
        "out_sample_excess_return": out_excess,
        "excess_change": excess_change,
        "in_sample_strategy_mdd": float(in_portfolio_mdd),
        "in_sample_benchmark_mdd": float(in_benchmark_mdd),
        "out_sample_strategy_mdd": float(out_portfolio_mdd),
        "out_sample_benchmark_mdd": float(out_benchmark_mdd),
        "in_sample_drawdown_gap": in_drawdown_gap,
        "out_sample_drawdown_gap": out_drawdown_gap,
        "portfolio_curve_source": _safe_text(portfolio_curve_source),
        "benchmark_curve_source": _safe_text(benchmark_curve_source),
        "benchmark_parity_status": benchmark_parity_status or "-",
        "proxy_evidence": source_proxy,
    }
    next_action = (
        "OOS REVIEW 항목을 Final Review 판단 사유로 남기거나 runtime replay / benchmark parity를 보강합니다."
        if status != "PASS"
        else "Final Review에서 walk-forward / regime evidence와 함께 확인합니다."
    )
    return _result(
        schema_version=OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION,
        status=status,
        summary=summary,
        rows=rows,
        metrics=metrics,
        limitations=limitations,
        next_action=next_action,
    )


def build_regime_split_validation(
    portfolio_curve: Any,
    benchmark_curve: Any,
    macro_observations: Any,
    *,
    portfolio_curve_source: Any = None,
    benchmark_curve_source: Any = None,
    macro_source: Any = None,
    benchmark_parity: dict[str, Any] | None = None,
    min_common_months: int = 24,
    min_bucket_count: int = 2,
    min_stress_months: int = 3,
    min_regime_excess_return: float = 0.0,
    max_regime_drawdown_gap: float = -0.05,
    allow_proxy_pass: bool = False,
) -> dict[str, Any]:
    """Build compact macro-regime split evidence from DB-backed observations."""

    min_common_months = max(6, int(_optional_float(min_common_months) or 24))
    min_bucket_count = max(1, int(_optional_float(min_bucket_count) or 2))
    min_stress_months = max(1, int(_optional_float(min_stress_months) or 3))
    portfolio_monthly = _monthly_curve(portfolio_curve)
    if portfolio_monthly.empty:
        return _result(
            schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="portfolio curve가 없어 regime split 검증을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Regime portfolio curve",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(portfolio_curve_source, "missing"),
                    "Evidence": "portfolio curve missing",
                    "Meaning": "regime split 검증에는 월별 portfolio curve가 필요합니다.",
                }
            ],
            metrics={"common_months": 0, "regime_months": 0},
            next_action="runtime replay 또는 source curve evidence를 먼저 보강합니다.",
        )
    benchmark_monthly = _monthly_curve(benchmark_curve)
    if benchmark_monthly.empty:
        return _result(
            schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="benchmark curve가 없어 regime split 상대 검증을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Regime benchmark curve",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(benchmark_curve_source, "missing"),
                    "Evidence": "benchmark curve missing",
                    "Meaning": "benchmark가 없으면 regime별 excess return과 drawdown gap을 판단할 수 없습니다.",
                }
            ],
            metrics={"portfolio_months": int(len(portfolio_monthly)), "benchmark_months": 0},
            next_action="같은 기간 / frequency / coverage의 benchmark curve를 보강합니다.",
        )
    macro_monthly, macro_meta = _monthly_macro_regimes(macro_observations)
    if macro_monthly.empty:
        return _result(
            schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="macro observation history가 없어 historical regime split을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Regime macro history",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": _safe_text(macro_source, "missing"),
                    "Evidence": "macro_series_observation missing or no recognized series",
                    "Meaning": "regime split에는 DB에 저장된 VIX / yield curve / credit spread history가 필요합니다.",
                }
            ],
            metrics={
                **macro_meta,
                "portfolio_months": int(len(portfolio_monthly)),
                "benchmark_months": int(len(benchmark_monthly)),
            },
            next_action="Workspace > Ingestion에서 Macro Context Snapshot / FRED macro series를 수집합니다.",
        )

    aligned, portfolio_months, benchmark_months = _aligned_monthly_curves(portfolio_curve, benchmark_curve)
    if aligned.empty:
        return _result(
            schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="portfolio / benchmark 공통 월 데이터가 없어 regime split을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Regime curve alignment",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "0 common months",
                    "Evidence": "portfolio / benchmark monthly alignment missing",
                    "Meaning": "regime별 성과는 같은 월의 portfolio / benchmark curve가 있어야 계산됩니다.",
                }
            ],
            metrics={**macro_meta, "portfolio_months": portfolio_months, "benchmark_months": benchmark_months},
            next_action="portfolio / benchmark curve alignment를 먼저 보강합니다.",
        )

    aligned = aligned.copy()
    aligned["portfolio_monthly_return"] = pd.to_numeric(aligned["portfolio_balance"], errors="coerce").pct_change()
    aligned["benchmark_monthly_return"] = pd.to_numeric(aligned["benchmark_balance"], errors="coerce").pct_change()
    merged = (
        pd.merge(
            aligned,
            macro_monthly[
                [
                    "_month",
                    "regime_bucket",
                    "regime_reasons",
                    "macro_series_count",
                    "coverage_statuses",
                    "source_types",
                    "sources",
                ]
            ],
            on="_month",
            how="inner",
        )
        .dropna(subset=["portfolio_monthly_return", "benchmark_monthly_return"])
        .sort_values("_month")
        .reset_index(drop=True)
    )
    common_months = int(len(merged))
    if common_months < min_common_months:
        return _result(
            schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary=(
                f"regime split을 만들기에 공통 월 데이터가 부족합니다 "
                f"({common_months} common months, required >= {min_common_months})."
            ),
            rows=[
                {
                    "Criteria": "Regime aligned history",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": f"{common_months} common months",
                    "Evidence": f"required >= {min_common_months}",
                    "Meaning": "짧은 기간에서는 regime bucket별 성과 차이를 신뢰하기 어렵습니다.",
                }
            ],
            metrics={
                **macro_meta,
                "portfolio_months": portfolio_months,
                "benchmark_months": benchmark_months,
                "common_months": common_months,
            },
            next_action="더 긴 기간의 runtime replay, benchmark history, macro history를 확보합니다.",
        )

    bucket_rows: list[dict[str, Any]] = []
    for bucket, bucket_frame in merged.groupby("regime_bucket", sort=True):
        portfolio_return = _compound_return(bucket_frame["portfolio_monthly_return"])
        benchmark_return = _compound_return(bucket_frame["benchmark_monthly_return"])
        portfolio_mdd = _drawdown_from_returns(bucket_frame["portfolio_monthly_return"])
        benchmark_mdd = _drawdown_from_returns(bucket_frame["benchmark_monthly_return"])
        if portfolio_return is None or benchmark_return is None or portfolio_mdd is None or benchmark_mdd is None:
            continue
        bucket_rows.append(
            {
                "Regime": bucket,
                "Months": int(len(bucket_frame)),
                "Portfolio Return": portfolio_return,
                "Benchmark Return": benchmark_return,
                "Excess Return": float(portfolio_return - benchmark_return),
                "Portfolio MDD": portfolio_mdd,
                "Benchmark MDD": benchmark_mdd,
                "Drawdown Gap": float(portfolio_mdd - benchmark_mdd),
                "Sample Start": _date_text(bucket_frame["portfolio_date"].min()),
                "Sample End": _date_text(bucket_frame["portfolio_date"].max()),
                "Reasons": _safe_text(
                    bucket_frame["regime_reasons"].mode().iloc[0]
                    if not bucket_frame["regime_reasons"].mode().empty
                    else "-"
                ),
            }
        )
    if not bucket_rows:
        return _result(
            schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
            status="NEEDS_INPUT",
            summary="regime bucket별 수익률 / drawdown metric을 계산하지 못했습니다.",
            rows=[
                {
                    "Criteria": "Regime computed metrics",
                    "Status": "NEEDS_INPUT",
                    "Ready": False,
                    "Current": "missing",
                    "Evidence": "bucket returns or drawdown missing",
                    "Meaning": "regime별 월간 수익률이 있어야 bucket 성과를 비교할 수 있습니다.",
                }
            ],
            metrics={"common_months": common_months, "regime_months": int(len(macro_monthly))},
            next_action="curve alignment와 macro coverage를 확인합니다.",
        )

    bucket_count = len(bucket_rows)
    stress_months = sum(
        int(row["Months"])
        for row in bucket_rows
        if str(row.get("Regime") or "") in {"risk_off", "caution"}
    )
    worst_excess_row = min(bucket_rows, key=lambda row: float(row["Excess Return"]))
    worst_gap_row = min(bucket_rows, key=lambda row: float(row["Drawdown Gap"]))
    coverage_statuses = set(macro_meta.get("coverage_statuses") or [])
    source_types = set(macro_meta.get("source_types") or [])
    benchmark_parity_status = str(dict(benchmark_parity or {}).get("status") or "").upper()
    source_proxy = _source_is_proxy(
        portfolio_curve_source,
        benchmark_curve_source,
        macro_source,
        " ".join(sorted(coverage_statuses)),
        " ".join(sorted(source_types)),
    )
    rows = [
        {
            "Criteria": "Regime aligned history",
            "Status": "PASS",
            "Ready": True,
            "Current": f"{common_months} common months",
            "Evidence": f"macro months={macro_meta.get('macro_months', 0)} / curve months={len(aligned)}",
            "Meaning": "portfolio / benchmark / macro history가 같은 월 단위로 결합되는지 확인합니다.",
        },
        {
            "Criteria": "Regime bucket coverage",
            "Status": "REVIEW" if bucket_count < min_bucket_count or stress_months < min_stress_months else "PASS",
            "Ready": bucket_count >= min_bucket_count and stress_months >= min_stress_months,
            "Current": f"{bucket_count} buckets / stress={stress_months} months",
            "Evidence": f"required buckets >= {min_bucket_count}, stress months >= {min_stress_months}",
            "Meaning": "neutral뿐 아니라 caution / risk-off 성격의 월에서도 검증됐는지 봅니다.",
        },
        {
            "Criteria": "Worst regime excess return",
            "Status": "REVIEW" if float(worst_excess_row["Excess Return"]) < min_regime_excess_return else "PASS",
            "Ready": float(worst_excess_row["Excess Return"]) >= min_regime_excess_return,
            "Current": _pct_text(worst_excess_row["Excess Return"]),
            "Evidence": f"{worst_excess_row['Regime']} / {worst_excess_row['Months']} months",
            "Meaning": "가장 약한 macro regime에서도 benchmark 대비 성과가 유지되는지 확인합니다.",
        },
        {
            "Criteria": "Worst regime drawdown gap",
            "Status": "REVIEW" if float(worst_gap_row["Drawdown Gap"]) < max_regime_drawdown_gap else "PASS",
            "Ready": float(worst_gap_row["Drawdown Gap"]) >= max_regime_drawdown_gap,
            "Current": _pct_text(worst_gap_row["Drawdown Gap"]),
            "Evidence": f"{worst_gap_row['Regime']} / {worst_gap_row['Months']} months",
            "Meaning": "나쁜 macro regime에서 strategy drawdown이 benchmark보다 과도하게 깊어지는지 봅니다.",
        },
    ]
    source_status = "PASS"
    source_evidence = "DB-backed macro observation and runtime or embedded curve evidence"
    limitations: list[str] = []
    if benchmark_parity_status and benchmark_parity_status != "PASS":
        source_status = "REVIEW"
        source_evidence = f"benchmark parity={benchmark_parity_status}"
        limitations.append("Benchmark parity가 PASS가 아니면 regime split 판단은 REVIEW로 남깁니다.")
    if len(macro_meta.get("recognized_series") or []) < 2:
        source_status = "REVIEW"
        source_evidence = "macro recognized series < 2"
        limitations.append("VIX / yield curve / credit spread 중 최소 2개 이상이 있어야 regime source를 강하게 볼 수 있습니다.")
    if (
        not coverage_statuses
        or not source_types
        or coverage_statuses.difference({"actual"})
        or source_types.difference({"official"})
    ):
        source_status = "REVIEW"
        source_evidence = "macro source is not fully official actual"
        limitations.append("macro source가 actual / official이 아니면 historical regime evidence를 PASS로 보지 않습니다.")
    if source_proxy and not allow_proxy_pass:
        source_status = "REVIEW"
        source_evidence = "proxy or bridge source"
        limitations.append("DB bridge / proxy curve 또는 macro source만으로는 regime split evidence를 PASS로 보지 않습니다.")
    rows.append(
        {
            "Criteria": "Regime source strength",
            "Status": source_status,
            "Ready": source_status == "PASS",
            "Current": (
                f"portfolio={_safe_text(portfolio_curve_source)} / "
                f"benchmark={_safe_text(benchmark_curve_source)} / "
                f"macro={_safe_text(macro_source)}"
            ),
            "Evidence": source_evidence,
            "Meaning": "runtime / embedded curve와 DB-backed macro observation의 source strength를 구분합니다.",
        }
    )
    status = _status_from_rows(rows)
    worst_excess = float(worst_excess_row["Excess Return"])
    worst_gap = float(worst_gap_row["Drawdown Gap"])
    summary = (
        f"Regime split {bucket_count} buckets / {common_months} months: "
        f"worst excess {_pct_text(worst_excess)} in {worst_excess_row['Regime']}, "
        f"worst drawdown gap {_pct_text(worst_gap)} in {worst_gap_row['Regime']}."
    )
    metrics = {
        **macro_meta,
        "portfolio_months": portfolio_months,
        "benchmark_months": benchmark_months,
        "common_months": common_months,
        "regime_bucket_count": bucket_count,
        "stress_regime_months": stress_months,
        "worst_regime": worst_excess_row["Regime"],
        "worst_regime_excess_return": worst_excess,
        "worst_regime_drawdown_gap": worst_gap,
        "portfolio_curve_source": _safe_text(portfolio_curve_source),
        "benchmark_curve_source": _safe_text(benchmark_curve_source),
        "macro_source": _safe_text(macro_source),
        "benchmark_parity_status": benchmark_parity_status or "-",
        "proxy_evidence": source_proxy,
        "bucket_rows": bucket_rows,
    }
    next_action = (
        "regime REVIEW 항목을 Final Review 판단 사유로 남기거나 macro history / benchmark parity를 보강합니다."
        if status != "PASS"
        else "Final Review에서 walk-forward / OOS evidence와 함께 확인합니다."
    )
    return _result(
        schema_version=REGIME_SPLIT_VALIDATION_SCHEMA_VERSION,
        status=status,
        summary=summary,
        rows=rows,
        metrics=metrics,
        limitations=limitations,
        next_action=next_action,
    )


__all__ = [
    "OOS_HOLDOUT_VALIDATION_SCHEMA_VERSION",
    "REGIME_MACRO_SERIES",
    "REGIME_SPLIT_VALIDATION_SCHEMA_VERSION",
    "WALKFORWARD_VALIDATION_SCHEMA_VERSION",
    "build_oos_holdout_validation",
    "build_regime_split_validation",
    "build_walkforward_validation",
]
