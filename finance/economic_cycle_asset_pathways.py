"""Pure time-series evaluation for economic-cycle asset pathways."""

from __future__ import annotations

from collections.abc import Mapping, Sequence
from datetime import date
from math import isclose
from statistics import median
from typing import Literal

import pandas as pd


HORIZONS = (5, 21, 63)
MIN_HISTORICAL_CHANGES = 252
MAX_STALENESS_BUSINESS_DAYS = 5
ChangeMode = Literal["PERCENT_RETURN", "BASIS_POINT"]


def _as_date(value: object) -> date:
    return pd.Timestamp(value).date()


def _change(current: float, previous: float, mode: ChangeMode) -> float:
    if mode == "BASIS_POINT":
        return (current - previous) * 100.0
    if previous <= 0:
        raise ValueError("PERCENT_RETURN requires a positive lagged value")
    return (current / previous - 1.0) * 100.0


def _direction(value: float, *, threshold: float) -> str:
    magnitude = abs(value)
    if value == 0 or (
        magnitude < threshold
        and not isclose(magnitude, threshold, rel_tol=1e-9, abs_tol=1e-12)
    ):
        return "NEUTRAL"
    return "UP" if value > 0 else "DOWN"


def _unavailable(
    series_id: str,
    reason_code: str,
    *,
    as_of_date: date | None = None,
) -> dict[str, object]:
    return {
        "series_id": series_id,
        "as_of_date": as_of_date.isoformat() if as_of_date else None,
        "unit": None,
        "freshness": "UNAVAILABLE",
        "reason_code": reason_code,
        "changes": {"5d": None, "21d": None, "63d": None},
        "thresholds": {"21d": None, "63d": None},
        "directions": {"21d": "UNAVAILABLE", "63d": "UNAVAILABLE"},
    }


def evaluate_series(
    points: Sequence[Mapping[str, object]],
    *,
    series_id: str,
    reference_date: object,
    change_mode: ChangeMode,
) -> dict[str, object]:
    """Evaluate current 5/21/63-day changes against prior five-year medians."""

    reference = _as_date(reference_date)
    by_date: dict[date, float] = {}
    for row in points:
        try:
            row_date = _as_date(row["date"])
            value = float(row["value"])
        except (KeyError, TypeError, ValueError):
            continue
        if row_date <= reference and (change_mode == "BASIS_POINT" or value > 0):
            by_date[row_date] = value

    ordered = sorted(by_date.items())
    if not ordered:
        return _unavailable(series_id, "MISSING_SERIES")

    latest_date = ordered[-1][0]
    business_age = len(
        pd.bdate_range(latest_date, reference, inclusive="right")
    )
    if business_age > MAX_STALENESS_BUSINESS_DAYS:
        return _unavailable(series_id, "STALE_SERIES", as_of_date=latest_date)
    if len(ordered) - 63 < MIN_HISTORICAL_CHANGES:
        return _unavailable(
            series_id,
            "INSUFFICIENT_HISTORY",
            as_of_date=latest_date,
        )

    values = [value for _, value in ordered]
    changes = {
        f"{horizon}d": _change(values[-1], values[-1 - horizon], change_mode)
        for horizon in HORIZONS
    }
    five_year_start = pd.Timestamp(reference) - pd.DateOffset(years=5)
    thresholds: dict[str, float] = {}
    for horizon in (21, 63):
        history = [
            abs(_change(values[index], values[index - horizon], change_mode))
            for index in range(horizon, len(values) - 1)
            if pd.Timestamp(ordered[index][0]) >= five_year_start
        ]
        if len(history) < MIN_HISTORICAL_CHANGES:
            return _unavailable(
                series_id,
                "INSUFFICIENT_HISTORY",
                as_of_date=latest_date,
            )
        thresholds[f"{horizon}d"] = median(history)

    unit = "bp" if change_mode == "BASIS_POINT" else "percent"
    return {
        "series_id": series_id,
        "as_of_date": latest_date.isoformat(),
        "unit": unit,
        "freshness": "CURRENT",
        "reason_code": None,
        "changes": changes,
        "thresholds": thresholds,
        "directions": {
            key: _direction(changes[key], threshold=thresholds[key])
            for key in ("21d", "63d")
        },
    }
