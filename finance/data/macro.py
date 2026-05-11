from __future__ import annotations

import csv
import io
import json
import logging
import os
import sys
import time
from collections.abc import Iterable
from datetime import datetime, timezone
from typing import Any
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

import pandas as pd

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
MACRO_TABLE = "macro_series_observation"
DEFAULT_MACRO_SERIES = ("VIXCLS", "T10Y3M", "BAA10Y")
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
FRED_CSV_URL = "https://fred.stlouisfed.org/graph/fredgraph.csv"
FRED_USER_AGENT = f"Python-urllib/{sys.version_info.major}.{sys.version_info.minor}"
DEFAULT_TIMEOUT = 20
DEFAULT_RETRIES = 2

LOGGER = logging.getLogger(__name__)

FRED_SERIES_CONFIG: dict[str, dict[str, Any]] = {
    "VIXCLS": {
        "series_name": "CBOE Volatility Index: VIX",
        "category": "volatility",
        "frequency": "daily",
        "units": "index",
    },
    "T10Y3M": {
        "series_name": "10-Year Treasury Constant Maturity Minus 3-Month Treasury Constant Maturity",
        "category": "yield_curve",
        "frequency": "daily",
        "units": "percent",
    },
    "BAA10Y": {
        "series_name": "Moody's Seasoned Baa Corporate Bond Yield Relative to Yield on 10-Year Treasury",
        "category": "credit_spread",
        "frequency": "daily",
        "units": "percent",
    },
}


def _normalize_series_ids(series_ids: str | Iterable[str] | None) -> list[str]:
    raw_values: Iterable[Any]
    if series_ids is None:
        raw_values = DEFAULT_MACRO_SERIES
    elif isinstance(series_ids, str):
        raw_values = series_ids.replace("\n", ",").split(",")
    else:
        raw_values = series_ids

    out: list[str] = []
    seen: set[str] = set()
    for item in raw_values:
        series_id = str(item).strip().upper()
        if not series_id or series_id in seen:
            continue
        seen.add(series_id)
        out.append(series_id)
    return out


def _date_string(value: Any) -> str | None:
    if value is None:
        return None
    parsed = pd.to_datetime(value, errors="coerce")
    if pd.isna(parsed):
        raise ValueError(f"Invalid date: {value!r}")
    return pd.Timestamp(parsed).strftime("%Y-%m-%d")


def _utc_now_string() -> str:
    return datetime.now(timezone.utc).strftime("%Y-%m-%d %H:%M:%S")


def _parse_float_value(value: Any) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if not text or text in {".", "-", "--", "NA", "N/A", "nan", "None"}:
        return None
    try:
        return float(text.replace(",", ""))
    except ValueError:
        return None


def _fetch_url_bytes(
    url: str,
    *,
    accept: str,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> bytes:
    request = Request(
        url,
        headers={
            "User-Agent": FRED_USER_AGENT,
            "Accept": accept,
            "Accept-Language": "en-US,en;q=0.9",
        },
    )
    last_error: Exception | None = None
    for attempt in range(max(int(retries), 1)):
        try:
            with urlopen(request, timeout=timeout) as response:
                return response.read()
        except (HTTPError, URLError, TimeoutError) as exc:
            last_error = exc
            if attempt + 1 < max(int(retries), 1):
                time.sleep(0.4 * (attempt + 1))
    if isinstance(last_error, HTTPError):
        raise RuntimeError(f"FRED HTTP {last_error.code}") from last_error
    if isinstance(last_error, URLError):
        raise RuntimeError(f"FRED fetch failed: {last_error.reason}") from last_error
    raise RuntimeError(f"FRED fetch failed: {last_error}") from last_error


def _series_config(series_id: str) -> dict[str, Any]:
    configured = FRED_SERIES_CONFIG.get(series_id.upper(), {})
    return {
        "series_name": configured.get("series_name") or series_id.upper(),
        "category": configured.get("category") or "market_context",
        "frequency": configured.get("frequency") or "unknown",
        "units": configured.get("units"),
        "release_lag_days": configured.get("release_lag_days"),
    }


def _macro_row(
    series_id: str,
    *,
    observation_date: str,
    value: float,
    source_mode: str,
    collected_at: str,
) -> dict[str, Any]:
    config = _series_config(series_id)
    missing_fields = [
        field
        for field, field_value in (
            ("value", value),
            ("category", config.get("category")),
            ("frequency", config.get("frequency")),
        )
        if field_value is None
    ]
    return {
        "series_id": series_id.upper(),
        "observation_date": observation_date,
        "source": "fred",
        "source_type": "official",
        "source_mode": source_mode,
        "source_ref": f"https://fred.stlouisfed.org/series/{series_id.upper()}",
        "series_name": config.get("series_name"),
        "category": config.get("category"),
        "frequency": config.get("frequency"),
        "units": config.get("units"),
        "value": value,
        "release_lag_days": config.get("release_lag_days"),
        "coverage_status": "actual" if not missing_fields else "partial",
        "missing_fields_json": json.dumps(missing_fields, ensure_ascii=False),
        "collected_at": collected_at,
        "error_msg": None,
    }


def _parse_fred_api_rows(
    series_id: str,
    payload: dict[str, Any],
    *,
    source_mode: str,
    collected_at: str,
) -> list[dict[str, Any]]:
    observations = payload.get("observations")
    if not isinstance(observations, list):
        raise RuntimeError("FRED API response has no observations list")

    rows: list[dict[str, Any]] = []
    for item in observations:
        if not isinstance(item, dict):
            continue
        observation_date = _date_string(item.get("date"))
        value = _parse_float_value(item.get("value"))
        if observation_date is None or value is None:
            continue
        rows.append(
            _macro_row(
                series_id,
                observation_date=observation_date,
                value=value,
                source_mode=source_mode,
                collected_at=collected_at,
            )
        )
    return rows


def _parse_fred_csv_rows(
    series_id: str,
    data: bytes,
    *,
    source_mode: str,
    collected_at: str,
) -> list[dict[str, Any]]:
    text = data.decode("utf-8-sig", errors="replace")
    reader = csv.DictReader(io.StringIO(text))
    rows: list[dict[str, Any]] = []
    for record in reader:
        observation_date = _date_string(record.get("observation_date"))
        value = _parse_float_value(record.get(series_id.upper()) or record.get(series_id))
        if observation_date is None or value is None:
            continue
        rows.append(
            _macro_row(
                series_id,
                observation_date=observation_date,
                value=value,
                source_mode=source_mode,
                collected_at=collected_at,
            )
        )
    return rows


def _fetch_fred_api_rows(
    series_id: str,
    *,
    start: str | None,
    end: str | None,
    api_key: str,
    timeout: int,
    retries: int,
    collected_at: str,
) -> list[dict[str, Any]]:
    params: dict[str, str] = {
        "series_id": series_id.upper(),
        "api_key": api_key,
        "file_type": "json",
        "sort_order": "asc",
        "limit": "100000",
    }
    if start is not None:
        params["observation_start"] = start
    if end is not None:
        params["observation_end"] = end
    url = f"{FRED_API_URL}?{urlencode(params)}"
    data = _fetch_url_bytes(url, accept="application/json,text/plain,*/*", timeout=timeout, retries=retries)
    payload = json.loads(data.decode("utf-8"))
    if "error_code" in payload:
        raise RuntimeError(f"FRED API error {payload.get('error_code')}: {payload.get('error_message')}")
    return _parse_fred_api_rows(series_id, payload, source_mode="api", collected_at=collected_at)


def _fetch_fred_csv_rows(
    series_id: str,
    *,
    start: str | None,
    end: str | None,
    timeout: int,
    retries: int,
    collected_at: str,
) -> list[dict[str, Any]]:
    params: dict[str, str] = {"id": series_id.upper()}
    if start is not None:
        params["cosd"] = start
    if end is not None:
        params["coed"] = end
    url = f"{FRED_CSV_URL}?{urlencode(params)}"
    data = _fetch_url_bytes(url, accept="text/csv,*/*", timeout=timeout, retries=retries)
    return _parse_fred_csv_rows(series_id, data, source_mode="csv", collected_at=collected_at)


def fetch_fred_macro_series_rows(
    series_ids: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    source_mode: str = "auto",
    api_key: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> tuple[list[dict[str, Any]], list[str], list[dict[str, str]]]:
    """Fetch normalized FRED market-context observations without writing to DB."""
    normalized_series = _normalize_series_ids(series_ids)
    start_date = _date_string(start)
    end_date = _date_string(end)
    if start_date is not None and end_date is not None and start_date > end_date:
        raise ValueError("start must be earlier than or equal to end.")

    normalized_mode = str(source_mode or "auto").strip().lower()
    if normalized_mode not in {"auto", "api", "csv"}:
        raise ValueError("source_mode must be one of: auto, api, csv.")

    resolved_api_key = api_key or os.environ.get("FRED_API_KEY")
    if normalized_mode == "auto":
        normalized_mode = "api" if resolved_api_key else "csv"
    if normalized_mode == "api" and not resolved_api_key:
        raise ValueError("FRED API mode requires api_key or FRED_API_KEY.")

    collected_at = _utc_now_string()
    rows: list[dict[str, Any]] = []
    missing: list[str] = []
    failed: list[dict[str, str]] = []

    for series_id in normalized_series:
        try:
            if normalized_mode == "api":
                series_rows = _fetch_fred_api_rows(
                    series_id,
                    start=start_date,
                    end=end_date,
                    api_key=str(resolved_api_key),
                    timeout=int(timeout),
                    retries=int(retries),
                    collected_at=collected_at,
                )
            else:
                series_rows = _fetch_fred_csv_rows(
                    series_id,
                    start=start_date,
                    end=end_date,
                    timeout=int(timeout),
                    retries=int(retries),
                    collected_at=collected_at,
                )
            if series_rows:
                rows.extend(series_rows)
            else:
                missing.append(series_id)
        except Exception as exc:
            failed.append({"series_id": series_id, "reason": str(exc)[:500]})
            LOGGER.warning("FRED macro series fetch failed for %s: %s", series_id, exc)

    return rows, missing, failed


def ensure_macro_series_schema(
    *,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    """Create or sync the macro market-context observation table."""
    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["macro_series_observation"])
        sync_table_schema(db, MACRO_TABLE, PROVIDER_SCHEMAS["macro_series_observation"], DB_META)
    finally:
        db.close()


def _upsert_macro_rows(db: MySQLClient, rows: list[dict[str, Any]]) -> None:
    if not rows:
        return
    sql = f"""
    INSERT INTO {MACRO_TABLE} (
      series_id, observation_date, source, source_type, source_mode, source_ref,
      series_name, category, frequency, units, value, release_lag_days,
      coverage_status, missing_fields_json, collected_at, error_msg
    ) VALUES (
      %(series_id)s, %(observation_date)s, %(source)s, %(source_type)s, %(source_mode)s, %(source_ref)s,
      %(series_name)s, %(category)s, %(frequency)s, %(units)s, %(value)s, %(release_lag_days)s,
      %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
    )
    ON DUPLICATE KEY UPDATE
      source_type = VALUES(source_type),
      source_mode = VALUES(source_mode),
      source_ref = VALUES(source_ref),
      series_name = VALUES(series_name),
      category = VALUES(category),
      frequency = VALUES(frequency),
      units = VALUES(units),
      value = VALUES(value),
      release_lag_days = VALUES(release_lag_days),
      coverage_status = VALUES(coverage_status),
      missing_fields_json = VALUES(missing_fields_json),
      collected_at = VALUES(collected_at),
      error_msg = VALUES(error_msg)
    """
    db.executemany(sql, rows)


def collect_and_store_macro_series(
    series_ids: str | Iterable[str] | None = None,
    *,
    start: str | None = None,
    end: str | None = None,
    provider: str = "fred",
    source_mode: str = "auto",
    api_key: str | None = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> dict[str, Any]:
    """Collect FRED market-context series and UPSERT them into finance_meta."""
    normalized_provider = str(provider or "fred").strip().lower()
    if normalized_provider != "fred":
        raise NotImplementedError("Only FRED macro provider is supported.")

    normalized_series = _normalize_series_ids(series_ids)
    rows, missing, failed = fetch_fred_macro_series_rows(
        normalized_series,
        start=start,
        end=end,
        source_mode=source_mode,
        api_key=api_key,
        timeout=int(timeout),
        retries=int(retries),
    )

    db = MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        db.execute(PROVIDER_SCHEMAS["macro_series_observation"])
        sync_table_schema(db, MACRO_TABLE, PROVIDER_SCHEMAS["macro_series_observation"], DB_META)
        _upsert_macro_rows(db, rows)
    finally:
        db.close()

    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row.get("coverage_status") or "missing")
        coverage[status] = coverage.get(status, 0) + 1
    found_series = {str(row.get("series_id") or "").upper() for row in rows}
    for series_id in normalized_series:
        if series_id not in found_series and series_id not in missing:
            missing.append(series_id)

    return {
        "requested": len(normalized_series),
        "stored": len(rows),
        "updated": None,
        "missing": sorted(set(missing)),
        "failed": failed,
        "coverage": coverage,
        "source": normalized_provider,
        "source_mode": rows[0]["source_mode"] if rows else str(source_mode or "auto").strip().lower(),
        "start": _date_string(start),
        "end": _date_string(end),
    }
