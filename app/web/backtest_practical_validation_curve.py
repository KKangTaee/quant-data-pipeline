from __future__ import annotations

from typing import Any

import pandas as pd


def optional_float(value: Any) -> float | None:
    if value is None:
        return None
    try:
        numeric = float(value)
    except (TypeError, ValueError):
        return None
    if pd.isna(numeric):
        return None
    return numeric


def normalize_result_curve(value: Any) -> pd.DataFrame:
    """Normalize embedded/proxy/runtime curve data into the Backtest result shape."""
    if isinstance(value, pd.DataFrame):
        working = value.copy()
    elif isinstance(value, list):
        working = pd.DataFrame(value)
    else:
        return pd.DataFrame()
    if working.empty or "Date" not in working.columns or "Total Balance" not in working.columns:
        return pd.DataFrame()
    working = working.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working["Total Balance"] = pd.to_numeric(working["Total Balance"], errors="coerce")
    working = working.dropna(subset=["Date", "Total Balance"]).sort_values("Date")
    if working.empty:
        return pd.DataFrame()
    if "Total Return" in working.columns:
        working["Total Return"] = pd.to_numeric(working["Total Return"], errors="coerce").fillna(0.0)
    else:
        working["Total Return"] = working["Total Balance"].pct_change().fillna(0.0)
    return working[["Date", "Total Balance", "Total Return"]].reset_index(drop=True)


def curve_records_from_df(result_df: pd.DataFrame, *, max_rows: int = 420) -> list[dict[str, Any]]:
    curve = normalize_result_curve(result_df)
    if curve.empty:
        return []
    if len(curve) > max_rows:
        monthly = (
            curve.assign(_month=curve["Date"].dt.to_period("M"))
            .groupby("_month", as_index=False)
            .tail(1)
            .drop(columns=["_month"])
            .sort_values("Date")
        )
        curve = monthly.tail(max_rows)
    return [
        {
            "Date": row["Date"].strftime("%Y-%m-%d") if not pd.isna(row["Date"]) else None,
            "Total Balance": optional_float(row["Total Balance"]),
            "Total Return": optional_float(row["Total Return"]),
        }
        for _, row in curve.iterrows()
    ]


def _month_set(curve: pd.DataFrame) -> set[str]:
    normalized = normalize_result_curve(curve)
    if normalized.empty:
        return set()
    return set(normalized["Date"].dt.to_period("M").astype(str).tolist())


def _date_text(value: Any) -> str | None:
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed.strftime("%Y-%m-%d")


def _median_step_days(curve: pd.DataFrame) -> float | None:
    normalized = normalize_result_curve(curve)
    if len(normalized) < 2:
        return None
    diffs = normalized["Date"].sort_values().diff().dropna().dt.days
    if diffs.empty:
        return None
    return optional_float(diffs.median())


def _frequency_label(curve: pd.DataFrame) -> str:
    step_days = _median_step_days(curve)
    if step_days is None:
        return "unknown"
    if step_days <= 3:
        return "daily"
    if 25 <= step_days <= 35:
        return "monthly"
    return f"step_{step_days:.0f}d"


def build_benchmark_parity(portfolio_curve: Any, benchmark_curve: Any) -> dict[str, Any]:
    """Check whether candidate and benchmark curves are comparable before relative judgments."""
    portfolio = normalize_result_curve(portfolio_curve)
    benchmark = normalize_result_curve(benchmark_curve)
    if portfolio.empty:
        return {
            "status": "NOT_RUN",
            "summary": "portfolio curve가 없어 benchmark parity를 확인하지 못했습니다.",
            "rows": [],
            "metrics": {},
        }
    if benchmark.empty:
        return {
            "status": "NOT_RUN",
            "summary": "benchmark curve가 없어 같은 기간 상대 비교를 확인하지 못했습니다.",
            "rows": [
                {
                    "Check": "Benchmark curve",
                    "Status": "NOT_RUN",
                    "Portfolio": f"{_date_text(portfolio['Date'].min())} -> {_date_text(portfolio['Date'].max())}",
                    "Benchmark": "-",
                    "Meaning": "benchmark가 없으면 상대성과, stress spread, rolling excess return 해석이 제한됩니다.",
                }
            ],
            "metrics": {
                "portfolio_rows": len(portfolio),
                "benchmark_rows": 0,
                "portfolio_frequency": _frequency_label(portfolio),
                "benchmark_frequency": "unknown",
            },
        }

    portfolio_start = portfolio["Date"].min()
    portfolio_end = portfolio["Date"].max()
    benchmark_start = benchmark["Date"].min()
    benchmark_end = benchmark["Date"].max()
    start_gap_days = abs((portfolio_start - benchmark_start).days)
    end_gap_days = abs((portfolio_end - benchmark_end).days)
    portfolio_months = _month_set(portfolio)
    benchmark_months = _month_set(benchmark)
    common_months = portfolio_months & benchmark_months
    coverage_ratio = len(common_months) / len(portfolio_months) if portfolio_months else 0.0
    missing_benchmark_months = sorted(portfolio_months - benchmark_months)
    same_period = start_gap_days <= 7 and end_gap_days <= 7
    sufficient_coverage = coverage_ratio >= 0.95
    same_frequency = _frequency_label(portfolio) == _frequency_label(benchmark)
    status = "PASS" if same_period and sufficient_coverage else "REVIEW"
    rows = [
        {
            "Check": "Period alignment",
            "Status": "PASS" if same_period else "REVIEW",
            "Portfolio": f"{_date_text(portfolio_start)} -> {_date_text(portfolio_end)}",
            "Benchmark": f"{_date_text(benchmark_start)} -> {_date_text(benchmark_end)}",
            "Meaning": "후보와 benchmark가 같은 실제 기간에서 비교되는지 확인합니다.",
        },
        {
            "Check": "Monthly coverage",
            "Status": "PASS" if sufficient_coverage else "REVIEW",
            "Portfolio": f"{len(portfolio_months)} months",
            "Benchmark": f"{len(benchmark_months)} months / common {len(common_months)}",
            "Meaning": "rolling, stress, baseline spread를 같은 월 단위에서 비교할 수 있는지 확인합니다.",
        },
        {
            "Check": "Frequency",
            "Status": "PASS" if same_frequency else "REVIEW",
            "Portfolio": _frequency_label(portfolio),
            "Benchmark": _frequency_label(benchmark),
            "Meaning": "일간 curve와 월간 curve를 섞어 상대성과를 과신하지 않도록 확인합니다.",
        },
    ]
    summary = (
        "benchmark와 후보 curve가 같은 기간/coverage 기준으로 비교 가능합니다."
        if status == "PASS"
        else "benchmark와 후보 curve의 기간, coverage, frequency 차이를 Final Review에서 확인해야 합니다."
    )
    return {
        "status": status,
        "summary": summary,
        "rows": rows,
        "metrics": {
            "same_period": same_period,
            "same_frequency": same_frequency,
            "coverage_ratio": round(coverage_ratio, 6),
            "portfolio_rows": len(portfolio),
            "benchmark_rows": len(benchmark),
            "portfolio_months": len(portfolio_months),
            "benchmark_months": len(benchmark_months),
            "common_months": len(common_months),
            "missing_benchmark_month_count": len(missing_benchmark_months),
            "missing_benchmark_month_preview": missing_benchmark_months[:12],
            "start_gap_days": start_gap_days,
            "end_gap_days": end_gap_days,
            "portfolio_frequency": _frequency_label(portfolio),
            "benchmark_frequency": _frequency_label(benchmark),
        },
    }


def build_curve_provenance(
    *,
    curve_context: dict[str, Any],
    replay_result: dict[str, Any] | None = None,
) -> dict[str, Any]:
    replay = dict(replay_result or {})
    replay_status = str(replay.get("status") or "NOT_RUN")
    component_sources = list(curve_context.get("curve_rows") or [])
    return {
        "portfolio_curve_source": curve_context.get("portfolio_curve_source") or "unavailable",
        "portfolio_curve_rows": len(normalize_result_curve(curve_context.get("portfolio_curve"))),
        "benchmark_curve_source": dict(curve_context.get("benchmark_meta") or {}).get("source")
        or dict(curve_context.get("benchmark_meta") or {}).get("status")
        or "unavailable",
        "benchmark_curve_rows": len(normalize_result_curve(curve_context.get("benchmark_curve"))),
        "actual_runtime_replay_status": replay_status,
        "actual_runtime_replay_id": replay.get("replay_id"),
        "actual_runtime_attempted_at": replay.get("attempted_at"),
        "component_curve_sources": component_sources,
    }
