from __future__ import annotations

from typing import Any

import numpy as np
import pandas as pd

from app.services.backtest_practical_validation_source import _optional_float
from finance.loaders import load_price_history
from finance.performance import portfolio_performance_summary


def _parse_date(value: Any) -> pd.Timestamp | None:
    if value in (None, ""):
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        return None
    return parsed


def _format_date(value: Any) -> str | None:
    parsed = _parse_date(value)
    if parsed is None:
        return None
    return parsed.strftime("%Y-%m-%d")


def _format_percent(value: Any) -> str:
    numeric = _optional_float(value)
    if numeric is None:
        return "-"
    return f"{numeric:.2%}"


def _curve_records_from_df(result_df: pd.DataFrame, *, max_rows: int = 420) -> list[dict[str, Any]]:
    if not isinstance(result_df, pd.DataFrame) or result_df.empty:
        return []
    required = {"Date", "Total Balance"}
    if not required.issubset(set(result_df.columns)):
        return []
    working = result_df.copy()
    working["Date"] = pd.to_datetime(working["Date"], errors="coerce")
    working["Total Balance"] = pd.to_numeric(working["Total Balance"], errors="coerce")
    working = working.dropna(subset=["Date", "Total Balance"]).sort_values("Date")
    if working.empty:
        return []
    if "Total Return" not in working.columns:
        working["Total Return"] = working["Total Balance"].pct_change().fillna(0.0)
    else:
        working["Total Return"] = pd.to_numeric(working["Total Return"], errors="coerce").fillna(
            working["Total Balance"].pct_change()
        )
        working["Total Return"] = working["Total Return"].fillna(0.0)
    monthly = (
        working.assign(_month=working["Date"].dt.to_period("M"))
        .groupby("_month", as_index=False)
        .tail(1)
        .sort_values("Date")
    )
    if len(monthly) > max_rows:
        monthly = monthly.tail(max_rows)
    monthly["Date"] = monthly["Date"].dt.strftime("%Y-%m-%d")
    return monthly[["Date", "Total Balance", "Total Return"]].to_dict("records")


def compact_curve_snapshot_from_bundle(bundle: dict[str, Any], *, max_rows: int = 420) -> list[dict[str, Any]]:
    """Persist a compact monthly curve snapshot from a Streamlit result bundle."""
    result_df = dict(bundle or {}).get("result_df")
    return _curve_records_from_df(result_df, max_rows=max_rows) if isinstance(result_df, pd.DataFrame) else []


def compact_benchmark_curve_snapshot_from_bundle(bundle: dict[str, Any], *, max_rows: int = 420) -> list[dict[str, Any]]:
    """Persist a compact monthly benchmark curve snapshot from a Streamlit result bundle."""
    benchmark_df = dict(bundle or {}).get("benchmark_chart_df")
    if not isinstance(benchmark_df, pd.DataFrame) or benchmark_df.empty:
        return []
    if "Benchmark Total Balance" not in benchmark_df.columns:
        return []
    working = benchmark_df.rename(
        columns={
            "Benchmark Total Balance": "Total Balance",
            "Benchmark Total Return": "Total Return",
        }
    )
    return _curve_records_from_df(working, max_rows=max_rows)


def _normalize_result_curve(value: Any) -> pd.DataFrame:
    if isinstance(value, pd.DataFrame):
        raw = value.copy()
    elif isinstance(value, list):
        raw = pd.DataFrame(value)
    else:
        return pd.DataFrame()
    if raw.empty or "Date" not in raw.columns or "Total Balance" not in raw.columns:
        return pd.DataFrame()
    raw["Date"] = pd.to_datetime(raw["Date"], errors="coerce")
    raw["Total Balance"] = pd.to_numeric(raw["Total Balance"], errors="coerce")
    if "Total Return" in raw.columns:
        raw["Total Return"] = pd.to_numeric(raw["Total Return"], errors="coerce")
    raw = raw.dropna(subset=["Date", "Total Balance"]).sort_values("Date").reset_index(drop=True)
    if raw.empty:
        return raw
    raw["Total Return"] = raw.get("Total Return", raw["Total Balance"].pct_change()).fillna(
        raw["Total Balance"].pct_change()
    )
    raw["Total Return"] = raw["Total Return"].fillna(0.0)
    return raw[["Date", "Total Balance", "Total Return"]]


def _price_proxy_curve(
    tickers: list[str],
    *,
    start: Any,
    end: Any,
    weights: list[float] | None = None,
    initial_balance: float = 10000.0,
) -> tuple[pd.DataFrame, dict[str, Any]]:
    clean_tickers = [str(ticker or "").strip().upper() for ticker in tickers if str(ticker or "").strip()]
    clean_tickers = list(dict.fromkeys(clean_tickers))
    if not clean_tickers:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "ticker 없음"}
    start_text = _format_date(start)
    end_text = _format_date(end)
    try:
        history = load_price_history(symbols=clean_tickers, start=start_text, end=end_text, timeframe="1d")
    except Exception as exc:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": f"price DB load failed: {exc}"}
    if history.empty:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "price history 없음", "tickers": clean_tickers}
    price_col = "adj_close" if "adj_close" in history.columns else "close"
    matrix = history.pivot(index="date", columns="symbol", values=price_col).sort_index()
    matrix = matrix.apply(pd.to_numeric, errors="coerce").ffill().dropna(how="all")
    available = [ticker for ticker in clean_tickers if ticker in matrix.columns and matrix[ticker].dropna().shape[0] >= 2]
    if not available:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "usable price series 없음", "tickers": clean_tickers}
    matrix = matrix[available].dropna()
    if matrix.empty:
        return pd.DataFrame(), {"status": "NOT_RUN", "reason": "aligned price series 없음", "tickers": available}
    if weights and len(weights) == len(clean_tickers):
        weight_map = {ticker: float(weight or 0.0) for ticker, weight in zip(clean_tickers, weights)}
        raw_weights = np.array([weight_map.get(ticker, 0.0) for ticker in available], dtype=float)
    else:
        raw_weights = np.array([1.0 / len(available)] * len(available), dtype=float)
    if raw_weights.sum() <= 0:
        raw_weights = np.array([1.0 / len(available)] * len(available), dtype=float)
    raw_weights = raw_weights / raw_weights.sum()
    normalized = matrix.divide(matrix.iloc[0]).mul(raw_weights, axis=1).sum(axis=1)
    balance = normalized * float(initial_balance)
    result = pd.DataFrame({"Date": pd.to_datetime(balance.index), "Total Balance": balance.values})
    result["Total Return"] = result["Total Balance"].pct_change().fillna(0.0)
    missing = [ticker for ticker in clean_tickers if ticker not in available]
    return result.reset_index(drop=True), {
        "status": "PASS" if not missing else "REVIEW",
        "source": "db_price_proxy",
        "tickers": available,
        "missing_tickers": missing,
        "rows": len(result),
    }


def _summary_metrics_from_curve(result_df: pd.DataFrame, *, name: str = "Portfolio") -> dict[str, Any]:
    if not isinstance(result_df, pd.DataFrame) or result_df.empty:
        return {}
    try:
        summary_df = portfolio_performance_summary(result_df.copy(), name=name, freq="D")
    except Exception:
        return {}
    if summary_df.empty:
        return {}
    row = dict(summary_df.iloc[0])
    return {
        "start": _format_date(row.get("Start Date")),
        "end": _format_date(row.get("End Date")),
        "cagr": _optional_float(row.get("CAGR")),
        "mdd": _optional_float(row.get("Maximum Drawdown")),
        "sharpe": _optional_float(row.get("Sharpe Ratio")),
        "std": _optional_float(row.get("Standard Deviation")),
        "end_balance": _optional_float(row.get("End Balance")),
    }


def _combine_component_curves(
    component_curves: list[dict[str, Any]],
    *,
    initial_balance: float = 10000.0,
) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    weights: list[float] = []
    for idx, item in enumerate(component_curves):
        curve = _normalize_result_curve(item.get("curve"))
        if curve.empty:
            continue
        start_balance = _optional_float(curve["Total Balance"].iloc[0])
        if not start_balance or start_balance <= 0:
            continue
        normalized = curve[["Date", "Total Balance"]].copy()
        normalized[f"component_{idx}"] = normalized["Total Balance"] / start_balance
        frames.append(normalized[["Date", f"component_{idx}"]].set_index("Date"))
        weights.append(float(item.get("weight") or 0.0))
    if not frames:
        return pd.DataFrame()
    aligned = pd.concat(frames, axis=1, join="inner").sort_index()
    if aligned.empty:
        return pd.DataFrame()
    raw_weights = np.array(weights[: len(aligned.columns)], dtype=float)
    if raw_weights.sum() <= 0:
        raw_weights = np.array([1.0 / len(aligned.columns)] * len(aligned.columns), dtype=float)
    raw_weights = raw_weights / raw_weights.sum()
    balance = aligned.mul(raw_weights, axis=1).sum(axis=1) * float(initial_balance)
    result = pd.DataFrame({"Date": balance.index, "Total Balance": balance.values}).reset_index(drop=True)
    result["Total Return"] = result["Total Balance"].pct_change().fillna(0.0)
    return result


def _window_perturbation_rows(
    portfolio_curve: pd.DataFrame | None,
    *,
    base_summary: dict[str, Any],
) -> list[dict[str, Any]]:
    curve = _normalize_result_curve(portfolio_curve)
    if curve.empty or not base_summary:
        return [
            {
                "Scenario": "Window perturbation",
                "Scope": "start/end, recent 3y/5y",
                "Result Status": "NOT_RUN",
                "Expected Check": "CAGR / MDD / Sharpe dispersion",
            }
        ]

    base_cagr = _optional_float(base_summary.get("cagr"))
    base_mdd = _optional_float(base_summary.get("mdd"))
    if base_cagr is None and base_mdd is None:
        return [
            {
                "Scenario": "Window perturbation",
                "Scope": "start/end, recent 3y/5y",
                "Result Status": "NOT_RUN",
                "Expected Check": "CAGR / MDD / Sharpe dispersion",
            }
        ]

    min_date = curve["Date"].min()
    max_date = curve["Date"].max()
    windows = [
        ("Recent 3Y", max_date - pd.DateOffset(years=3), max_date),
        ("Recent 5Y", max_date - pd.DateOffset(years=5), max_date),
        ("Exclude first 12M", min_date + pd.DateOffset(months=12), max_date),
        ("Exclude last 12M", min_date, max_date - pd.DateOffset(months=12)),
    ]
    rows: list[dict[str, Any]] = []
    for scenario, start_date, end_date in windows:
        window = curve[(curve["Date"] >= start_date) & (curve["Date"] <= end_date)].copy()
        if window["Date"].nunique() < 12:
            rows.append(
                {
                    "Scenario": scenario,
                    "Scope": f"{_format_date(start_date)} -> {_format_date(end_date)}",
                    "Result Status": "NOT_RUN",
                    "Expected Check": "기간 변경 민감도",
                    "Reason": "usable curve rows < 12",
                }
            )
            continue
        summary = _summary_metrics_from_curve(window, name=scenario)
        window_cagr = _optional_float(summary.get("cagr"))
        window_mdd = _optional_float(summary.get("mdd"))
        cagr_delta = window_cagr - base_cagr if window_cagr is not None and base_cagr is not None else None
        mdd_delta = window_mdd - base_mdd if window_mdd is not None and base_mdd is not None else None
        review = (cagr_delta is not None and cagr_delta < -0.03) or (
            mdd_delta is not None and mdd_delta < -0.05
        )
        rows.append(
            {
                "Scenario": scenario,
                "Scope": f"{_format_date(summary.get('start') or start_date)} -> {_format_date(summary.get('end') or end_date)}",
                "Result Status": "REVIEW" if review else "PASS",
                "Expected Check": "기간 변경 민감도",
                "CAGR": window_cagr,
                "MDD": window_mdd,
                "CAGR Delta": cagr_delta,
                "MDD Delta": mdd_delta,
            }
        )
    return rows


def _aligned_monthly_returns(curves: list[dict[str, Any]]) -> pd.DataFrame:
    frames: list[pd.DataFrame] = []
    for idx, item in enumerate(curves):
        curve = _normalize_result_curve(item.get("curve"))
        if curve.empty:
            continue
        monthly = (
            curve.assign(_month=curve["Date"].dt.to_period("M"))
            .groupby("_month", as_index=False)
            .tail(1)
            .sort_values("Date")
        )
        monthly[f"component_{idx}"] = monthly["Total Balance"].pct_change()
        frames.append(monthly[["Date", f"component_{idx}"]].dropna().set_index("Date"))
    if not frames:
        return pd.DataFrame()
    return pd.concat(frames, axis=1, join="inner").dropna(how="any")
