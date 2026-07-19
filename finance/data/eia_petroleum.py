from __future__ import annotations

import logging
from collections.abc import Callable, Iterable
from datetime import datetime, timezone

import pandas as pd

from .macro import store_macro_observation_rows


LOGGER = logging.getLogger(__name__)

EIA_WEEKLY_PETROLEUM_SERIES: dict[str, dict[str, str]] = {
    "WCESTUS1": {
        "series_name": "Weekly U.S. Ending Stocks excluding SPR of Crude Oil",
        "category": "petroleum_inventory",
        "units": "thousand_barrels",
        "url": "https://www.eia.gov/dnav/pet/hist_xls/WCESTUS1w.xls",
    },
    "WCRFPUS2": {
        "series_name": "Weekly U.S. Field Production of Crude Oil",
        "category": "petroleum_production",
        "units": "thousand_barrels_per_day",
        "url": "https://www.eia.gov/dnav/pet/hist_xls/WCRFPUS2w.xls",
    },
    "WRPUPUS2": {
        "series_name": "Weekly U.S. Product Supplied of Petroleum Products",
        "category": "petroleum_product_supplied",
        "units": "thousand_barrels_per_day",
        "url": "https://www.eia.gov/dnav/pet/hist_xls/WRPUPUS2w.xls",
    },
}


def _normalize_series_ids(series_ids: str | Iterable[str] | None) -> list[str]:
    if series_ids is None:
        raw: Iterable[object] = EIA_WEEKLY_PETROLEUM_SERIES
    elif isinstance(series_ids, str):
        raw = series_ids.replace("\n", ",").split(",")
    else:
        raw = series_ids
    normalized: list[str] = []
    for value in raw:
        series_id = str(value).strip().upper()
        if series_id in EIA_WEEKLY_PETROLEUM_SERIES and series_id not in normalized:
            normalized.append(series_id)
    return normalized


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _read_eia_weekly_xls(url: str) -> pd.DataFrame:
    return pd.read_excel(url, sheet_name="Data 1", header=2, usecols=[0, 1])


def normalize_eia_weekly_frame(
    series_id: str,
    frame: pd.DataFrame,
    *,
    collected_at: str,
) -> list[dict[str, object]]:
    """Normalize one official EIA weekly workbook into macro observation rows."""
    normalized_id = str(series_id).strip().upper()
    config = EIA_WEEKLY_PETROLEUM_SERIES[normalized_id]
    normalized = frame.iloc[:, :2].copy()
    normalized.columns = ["observation_date", "value"]
    normalized["observation_date"] = pd.to_datetime(
        normalized["observation_date"], errors="coerce"
    )
    normalized["value"] = pd.to_numeric(normalized["value"], errors="coerce")
    normalized = normalized.dropna(subset=["observation_date", "value"])
    return [
        {
            "series_id": normalized_id,
            "observation_date": row.observation_date.strftime("%Y-%m-%d"),
            "source": "eia",
            "source_type": "official",
            "source_mode": "weekly_xls",
            "source_ref": config["url"],
            "series_name": config["series_name"],
            "category": config["category"],
            "frequency": "weekly",
            "units": config["units"],
            "value": float(row.value),
            "release_lag_days": None,
            "coverage_status": "actual",
            "missing_fields_json": "[]",
            "collected_at": collected_at,
            "error_msg": None,
        }
        for row in normalized.itertuples()
    ]


def fetch_eia_weekly_petroleum_rows(
    series_ids: str | Iterable[str] | None = None,
    *,
    fetcher: Callable[[str], pd.DataFrame] | None = None,
    collected_at: str | None = None,
) -> tuple[list[dict[str, object]], list[str], list[dict[str, str]]]:
    """Fetch official EIA XLS series and isolate missing and failed sources."""
    reader = fetcher or _read_eia_weekly_xls
    collected = collected_at or _utc_now_string()
    rows: list[dict[str, object]] = []
    missing: list[str] = []
    failed: list[dict[str, str]] = []
    for series_id in _normalize_series_ids(series_ids):
        try:
            frame = reader(EIA_WEEKLY_PETROLEUM_SERIES[series_id]["url"])
            series_rows = normalize_eia_weekly_frame(
                series_id,
                frame,
                collected_at=collected,
            )
            if series_rows:
                rows.extend(series_rows)
            else:
                missing.append(series_id)
        except Exception as exc:
            failed.append({"series_id": series_id, "reason": str(exc)[:500]})
            LOGGER.warning("EIA weekly series fetch failed for %s: %s", series_id, exc)
    return rows, missing, failed


def collect_and_store_eia_weekly_petroleum(
    series_ids: str | Iterable[str] | None = None,
    *,
    fetcher: Callable[[str], pd.DataFrame] | None = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, object]:
    """Collect EIA weekly petroleum observations and store them idempotently."""
    normalized = _normalize_series_ids(series_ids)
    rows, missing, failed = fetch_eia_weekly_petroleum_rows(
        normalized,
        fetcher=fetcher,
    )
    stored = store_macro_observation_rows(
        rows,
        host=host,
        user=user,
        password=password,
        port=port,
    )
    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1
    return {
        "requested": len(normalized),
        "stored": stored,
        "updated": None,
        "missing": missing,
        "failed": failed,
        "coverage": coverage,
        "source": "eia",
        "source_mode": "weekly_xls",
    }
