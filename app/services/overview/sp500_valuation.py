from __future__ import annotations

import math
import statistics
from typing import Any

import pandas as pd


def _bucket(z_score: float) -> str:
    if z_score < -1.0:
        return "LOW"
    if z_score < 1.0:
        return "NEUTRAL"
    if z_score < 2.0:
        return "HIGH"
    return "EXTREME_HIGH"


def _distribution(values: list[float], window_months: int) -> dict[str, Any]:
    selected = values[-window_months:]
    logs = [math.log(value) for value in selected]
    mean_log = statistics.fmean(logs)
    std_log = statistics.stdev(logs)
    return {
        "window_months": window_months,
        "observation_count": len(selected),
        "mean_log": mean_log,
        "std_log": std_log,
        "mean_multiple": math.exp(mean_log),
        "minus_1sigma": math.exp(mean_log - std_log),
        "plus_1sigma": math.exp(mean_log + std_log),
        "plus_2sigma": math.exp(mean_log + (2.0 * std_log)),
    }


def calculate_multiple_regime(
    monthly_rows: pd.DataFrame | list[dict[str, Any]],
    *,
    current_spx: float,
    current_ttm_eps: float,
    official_window: int = 60,
    sensitivity_window: int = 36,
) -> dict[str, Any]:
    """Calculate descriptive log(P/E) zones over 60m with a 36m sensitivity view."""
    current_spx = float(current_spx)
    current_ttm_eps = float(current_ttm_eps)
    if current_spx <= 0 or current_ttm_eps <= 0:
        raise ValueError("current_spx and current_ttm_eps must be positive.")

    frame = pd.DataFrame(monthly_rows).copy()
    if frame.empty or "observation_month" not in frame or "trailing_pe" not in frame:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": int(official_window),
            "observation_count": 0,
            "series": [],
        }
    frame["observation_month"] = pd.to_datetime(
        frame["observation_month"], errors="coerce"
    )
    frame["trailing_pe"] = pd.to_numeric(frame["trailing_pe"], errors="coerce")
    frame = (
        frame.dropna(subset=["observation_month", "trailing_pe"])
        .loc[lambda value: value["trailing_pe"] > 0]
        .sort_values("observation_month")
        .drop_duplicates("observation_month", keep="last")
    )
    required = max(int(official_window), int(sensitivity_window), 2)
    if len(frame) < required:
        return {
            "status": "INSUFFICIENT_HISTORY",
            "window_months": int(official_window),
            "observation_count": len(frame),
            "series": [],
        }

    official_frame = frame.tail(int(official_window))
    values = frame["trailing_pe"].astype(float).tolist()
    official = _distribution(values, int(official_window))
    sensitivity = _distribution(values, int(sensitivity_window))
    current_pe = current_spx / current_ttm_eps
    current_log = math.log(current_pe)
    current_z = (current_log - official["mean_log"]) / official["std_log"]
    sensitivity_z = (
        current_log - sensitivity["mean_log"]
    ) / sensitivity["std_log"]
    bucket = _bucket(current_z)
    sensitivity_bucket = _bucket(sensitivity_z)

    series = [
        {
            "month": row.observation_month.strftime("%Y-%m-%d"),
            "trailing_pe": float(row.trailing_pe),
        }
        for row in official_frame.itertuples()
    ]
    return {
        "status": "READY",
        "window_months": int(official_window),
        "observation_count": len(series),
        "series": series,
        "mean_multiple": official["mean_multiple"],
        "minus_1sigma": official["minus_1sigma"],
        "plus_1sigma": official["plus_1sigma"],
        "plus_2sigma": official["plus_2sigma"],
        "current_pe": current_pe,
        "current_z": current_z,
        "bucket": bucket,
        "sensitivity": {
            "window_months": int(sensitivity_window),
            "observation_count": sensitivity["observation_count"],
            "mean_multiple": sensitivity["mean_multiple"],
            "current_z": sensitivity_z,
            "bucket": sensitivity_bucket,
        },
        "period_sensitive": bucket != sensitivity_bucket,
        "basis_start": series[0]["month"],
        "basis_end": series[-1]["month"],
        "methodology": "월별 후행 PER의 자연로그 평균과 표본 표준편차",
        "limitation": "이 구간은 상대적 가치평가 범위이며 확률적 신뢰구간이 아닙니다.",
    }
