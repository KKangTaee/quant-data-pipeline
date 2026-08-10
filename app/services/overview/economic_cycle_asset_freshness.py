"""Frequency-aware DB freshness for Economic Cycle asset pathways."""

from __future__ import annotations

from collections.abc import Callable, Mapping, Sequence
from datetime import date, datetime, timedelta
from typing import Any

import pandas as pd

from finance.loaders.economic_cycle_assets import (
    load_economic_cycle_asset_prices,
    load_economic_cycle_market_series,
)

DAILY_MACRO_SERIES = (
    "DGS2",
    "DGS10",
    "DFII10",
    "T10YIE",
    "VIXCLS",
    "BAA10Y",
)
WEEKLY_MACRO_SERIES = ("WCESTUS1", "WCRFPUS2", "WRPUPUS2")
DAILY_PRICE_SERIES = ("GC=F", "DX-Y.NYB", "CL=F", "HG=F", "^GSPC", "SPY")
DAILY_MAX_BUSINESS_AGE = 5
WEEKLY_MAX_CALENDAR_AGE = 14


def _as_date(value: object) -> date | None:
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    try:
        return pd.Timestamp(value).date()
    except (TypeError, ValueError):
        return None


def _latest_dates(
    rows: Sequence[Mapping[str, object]],
    *,
    key_field: str,
    date_field: str,
    value_field: str,
    reference_date: date,
) -> dict[str, date]:
    latest: dict[str, date] = {}
    for row in rows:
        key = str(row.get(key_field) or "").strip().upper()
        observed = _as_date(row.get(date_field))
        if not key or observed is None or observed > reference_date:
            continue
        value = row.get(value_field)
        if value is None or not bool(pd.notna(value)):
            continue
        if key not in latest or observed > latest[key]:
            latest[key] = observed
    return latest


def build_asset_pathway_freshness(
    market_rows: Sequence[Mapping[str, object]],
    price_rows: Sequence[Mapping[str, object]],
    *,
    reference_date: str | date | datetime,
) -> dict[str, object]:
    """Classify daily and weekly inputs against their own release cadence."""

    reference = _as_date(reference_date)
    if reference is None:
        return {
            "status": "ERROR",
            "reference_date": None,
            "latest_observation_date": None,
            "refresh_required": True,
            "stale_series": [],
            "missing_series": [],
            "series": {},
            "message": "자산 경로 기준일을 확인하지 못했습니다.",
        }

    market_latest = _latest_dates(
        market_rows,
        key_field="series_id",
        date_field="observation_date",
        value_field="value",
        reference_date=reference,
    )
    price_latest = _latest_dates(
        price_rows,
        key_field="provider_symbol",
        date_field="candle_time_utc",
        value_field="close",
        reference_date=reference,
    )

    series: dict[str, dict[str, object]] = {}
    stale_series: list[str] = []
    missing_series: list[str] = []
    all_latest: list[date] = []
    for series_id in (*DAILY_MACRO_SERIES, *WEEKLY_MACRO_SERIES):
        latest = market_latest.get(series_id)
        cadence = "weekly" if series_id in WEEKLY_MACRO_SERIES else "daily"
        if latest is None:
            status = "MISSING"
            age = None
            missing_series.append(series_id)
        else:
            all_latest.append(latest)
            age = (
                (reference - latest).days
                if cadence == "weekly"
                else len(pd.bdate_range(latest, reference, inclusive="right"))
            )
            limit = (
                WEEKLY_MAX_CALENDAR_AGE
                if cadence == "weekly"
                else DAILY_MAX_BUSINESS_AGE
            )
            status = "READY" if age <= limit else "STALE"
            if status == "STALE":
                stale_series.append(series_id)
        series[series_id] = {
            "latest_date": latest.isoformat() if latest else None,
            "status": status,
            "cadence": cadence,
            "age": age,
        }

    for symbol in DAILY_PRICE_SERIES:
        latest = price_latest.get(symbol)
        if latest is None:
            status = "MISSING"
            age = None
            missing_series.append(symbol)
        else:
            all_latest.append(latest)
            age = len(pd.bdate_range(latest, reference, inclusive="right"))
            status = "READY" if age <= DAILY_MAX_BUSINESS_AGE else "STALE"
            if status == "STALE":
                stale_series.append(symbol)
        series[symbol] = {
            "latest_date": latest.isoformat() if latest else None,
            "status": status,
            "cadence": "daily",
            "age": age,
        }

    if len(missing_series) == len(series):
        status = "MISSING"
        message = "자산별 확인 포인트의 저장 자료가 없습니다."
    elif stale_series or missing_series:
        status = "REFRESH_AVAILABLE"
        message = "일부 자산 경로 자료를 최신 기준으로 확인할 수 있습니다."
    else:
        status = "READY"
        message = "자산별 확인 포인트가 최신 저장 자료를 사용하고 있습니다."
    return {
        "status": status,
        "reference_date": reference.isoformat(),
        "latest_observation_date": max(all_latest).isoformat() if all_latest else None,
        "refresh_required": status != "READY",
        "stale_series": stale_series,
        "missing_series": missing_series,
        "series": series,
        "message": message,
    }


def load_asset_pathway_freshness(
    *,
    reference_date: str | date | datetime | None = None,
    market_series_loader: Callable[..., Sequence[Mapping[str, object]]] = (
        load_economic_cycle_market_series
    ),
    asset_price_loader: Callable[..., Sequence[Mapping[str, object]]] = (
        load_economic_cycle_asset_prices
    ),
) -> dict[str, object]:
    """Load a bounded DB window and evaluate it without provider access."""

    reference = _as_date(reference_date) or date.today()
    start = reference - timedelta(days=45)
    try:
        market_rows = list(
            market_series_loader(start_date=start, end_date=reference)
        )
        price_rows = list(
            asset_price_loader(lookback_rows=315, end_date=reference)
        )
    except Exception:
        return {
            "status": "ERROR",
            "reference_date": reference.isoformat(),
            "latest_observation_date": None,
            "refresh_required": True,
            "stale_series": [],
            "missing_series": [],
            "series": {},
            "message": "저장된 자산 경로의 최신성을 확인하지 못했습니다.",
        }
    return build_asset_pathway_freshness(
        market_rows,
        price_rows,
        reference_date=reference,
    )
