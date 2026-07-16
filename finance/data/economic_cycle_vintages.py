"""Collect and persist point-in-time FRED/ALFRED observation vintages."""

from __future__ import annotations

import json
import logging
import math
import os
import time
from datetime import date, datetime, timezone
from typing import Any, Iterable
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from finance.economic_cycle_catalog import IndicatorSpec, get_economic_cycle_catalog

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema


DB_META = "finance_meta"
VINTAGE_TABLE = "macro_series_vintage_observation"
FRED_API_URL = "https://api.stlouisfed.org/fred/series/observations"
EARLIEST_REALTIME_DATE = "1776-07-04"
OPEN_ENDED_REALTIME_DATE = "9999-12-31"
DEFAULT_TIMEOUT = 20
DEFAULT_RETRIES = 3

LOGGER = logging.getLogger(__name__)


class EconomicCycleVintageError(RuntimeError):
    """Raised when the vintage source contract cannot be satisfied safely."""


def _date_text(value: object, *, field: str) -> str:
    if isinstance(value, datetime):
        return value.date().isoformat()
    if isinstance(value, date):
        return value.isoformat()
    text = str(value or "").strip()
    try:
        return date.fromisoformat(text).isoformat()
    except ValueError as exc:
        raise EconomicCycleVintageError(f"Invalid {field}: {value!r}") from exc


def _collected_at_text(value: datetime | str) -> str:
    if isinstance(value, datetime):
        normalized = value
        if normalized.tzinfo is not None:
            normalized = normalized.astimezone(timezone.utc).replace(tzinfo=None)
        return normalized.strftime("%Y-%m-%d %H:%M:%S")
    text = str(value).strip()
    if not text:
        raise EconomicCycleVintageError("collected_at is required")
    return text


def _parse_value(value: object) -> float | None:
    if value is None:
        return None
    text = str(value).strip()
    if text in {"", ".", "-", "--", "NA", "N/A", "None", "nan"}:
        return None
    try:
        parsed = float(text.replace(",", ""))
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _urllib_json(params: dict[str, object], *, timeout: int, retries: int) -> dict[str, Any]:
    url = f"{FRED_API_URL}?{urlencode(params)}"
    request = Request(
        url,
        headers={
            "Accept": "application/json",
            "User-Agent": "quant-data-pipeline/economic-cycle-v1",
        },
    )
    last_error: Exception | None = None
    for attempt in range(max(1, int(retries))):
        try:
            with urlopen(request, timeout=int(timeout)) as response:
                return json.loads(response.read().decode("utf-8"))
        except (HTTPError, URLError, TimeoutError, json.JSONDecodeError) as exc:
            last_error = exc
            if attempt + 1 < max(1, int(retries)):
                time.sleep(0.4 * (attempt + 1))
    raise EconomicCycleVintageError(f"FRED vintage fetch failed: {last_error}") from last_error


def fetch_fred_vintages(
    series_id: str,
    *,
    api_key: str,
    session: Any = None,
    limit: int = 100_000,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> list[dict[str, object]]:
    """Fetch every real-time version for one series with deterministic pagination."""

    normalized_series = str(series_id or "").strip().upper()
    normalized_key = str(api_key or "").strip()
    if not normalized_series:
        raise EconomicCycleVintageError("series_id is required")
    if not normalized_key:
        raise EconomicCycleVintageError("FRED_API_KEY is required for vintage data")

    page_size = max(1, min(int(limit), 100_000))
    offset = 0
    rows: list[dict[str, object]] = []
    while True:
        params: dict[str, object] = {
            "series_id": normalized_series,
            "api_key": normalized_key,
            "file_type": "json",
            "output_type": 2,
            "sort_order": "asc",
            "realtime_start": EARLIEST_REALTIME_DATE,
            "realtime_end": OPEN_ENDED_REALTIME_DATE,
            "limit": page_size,
            "offset": offset,
        }
        if session is None:
            payload = _urllib_json(params, timeout=int(timeout), retries=int(retries))
        else:
            response = session.get(FRED_API_URL, params=params, timeout=int(timeout))
            response.raise_for_status()
            payload = response.json()
        if not isinstance(payload, dict):
            raise EconomicCycleVintageError("FRED vintage response must be a JSON object")
        if payload.get("error_code") is not None:
            raise EconomicCycleVintageError(
                f"FRED API error {payload.get('error_code')}: {payload.get('error_message')}"
            )
        observations = payload.get("observations")
        if not isinstance(observations, list):
            raise EconomicCycleVintageError("FRED vintage response has no observations list")
        rows.extend(item for item in observations if isinstance(item, dict))

        count = int(payload.get("count") or len(rows))
        offset += len(observations)
        if not observations or offset >= count:
            break

    return sorted(
        rows,
        key=lambda item: (
            str(item.get("date") or ""),
            str(item.get("realtime_start") or ""),
            str(item.get("realtime_end") or ""),
        ),
    )


def normalize_fred_vintage_rows(
    spec: IndicatorSpec,
    payload_rows: Iterable[dict[str, object]],
    *,
    collected_at: datetime | str,
) -> list[dict[str, object]]:
    """Normalize raw vintage rows without dropping missing or unusual source facts."""

    collected_text = _collected_at_text(collected_at)
    normalized: list[dict[str, object]] = []
    for item in payload_rows:
        observation_date = _date_text(item.get("date"), field="observation date")
        realtime_start = _date_text(
            item.get("realtime_start"), field="realtime_start"
        )
        realtime_end = _date_text(
            item.get("realtime_end") or OPEN_ENDED_REALTIME_DATE,
            field="realtime_end",
        )
        value = _parse_value(item.get("value"))
        release_lag_days = (
            date.fromisoformat(realtime_start) - date.fromisoformat(observation_date)
        ).days
        missing_fields = ["value"] if value is None else []
        negative_lag = release_lag_days < 0
        coverage_status = (
            "missing" if missing_fields else "partial" if negative_lag else "actual"
        )
        normalized.append(
            {
                "series_id": spec.series_id,
                "observation_date": observation_date,
                "realtime_start": realtime_start,
                "realtime_end": realtime_end,
                "source": "fred",
                "source_type": "official",
                "source_mode": "fred_output_type_2",
                "source_ref": f"https://fred.stlouisfed.org/series/{spec.series_id}",
                "series_name": spec.series_id,
                "factor_group": spec.factor,
                "frequency": spec.frequency,
                "units": None,
                "value": value,
                "release_lag_days": release_lag_days,
                "coverage_status": coverage_status,
                "missing_fields_json": json.dumps(
                    missing_fields, ensure_ascii=False, sort_keys=True
                ),
                "collected_at": collected_text,
                "error_msg": "negative_release_lag" if negative_lag else None,
            }
        )
    return sorted(
        normalized,
        key=lambda row: (
            str(row["series_id"]),
            str(row["observation_date"]),
            str(row["realtime_start"]),
        ),
    )


def ensure_economic_cycle_vintage_schema(
    *,
    connection: Any = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> None:
    """Create/sync the raw vintage table without touching revised macro rows."""

    owns_connection = connection is None
    db = connection or MySQLClient(host, user, password, port)
    try:
        db.use_db(DB_META)
        schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
        db.execute(schema)
        sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
    finally:
        if owns_connection:
            db.close()


def upsert_economic_cycle_vintages(
    rows: list[dict[str, object]],
    *,
    connection: Any = None,
    host: str = "localhost",
    user: str = "root",
    password: str = "1234",
    port: int = 3306,
) -> int:
    """Idempotently store raw versions by series/date/realtime/source identity."""

    if not rows:
        return 0
    owns_connection = connection is None
    db = connection or MySQLClient(host, user, password, port)
    try:
        if owns_connection:
            db.use_db(DB_META)
            schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
            db.execute(schema)
            sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
        sql = f"""
        INSERT INTO {VINTAGE_TABLE} (
          series_id, observation_date, realtime_start, realtime_end,
          source, source_type, source_mode, source_ref,
          series_name, factor_group, frequency, units, value, release_lag_days,
          coverage_status, missing_fields_json, collected_at, error_msg
        ) VALUES (
          %(series_id)s, %(observation_date)s, %(realtime_start)s, %(realtime_end)s,
          %(source)s, %(source_type)s, %(source_mode)s, %(source_ref)s,
          %(series_name)s, %(factor_group)s, %(frequency)s, %(units)s, %(value)s, %(release_lag_days)s,
          %(coverage_status)s, %(missing_fields_json)s, %(collected_at)s, %(error_msg)s
        )
        ON DUPLICATE KEY UPDATE
          realtime_end = VALUES(realtime_end),
          source_type = VALUES(source_type), source_mode = VALUES(source_mode),
          source_ref = VALUES(source_ref), series_name = VALUES(series_name),
          factor_group = VALUES(factor_group), frequency = VALUES(frequency),
          units = VALUES(units), value = VALUES(value),
          release_lag_days = VALUES(release_lag_days),
          coverage_status = VALUES(coverage_status),
          missing_fields_json = VALUES(missing_fields_json),
          collected_at = VALUES(collected_at), error_msg = VALUES(error_msg)
        """
        db.executemany(sql, rows)
        return len(rows)
    finally:
        if owns_connection:
            db.close()


def collect_economic_cycle_vintages(
    *,
    series_ids: Iterable[str] | None = None,
    api_key: str | None = None,
    connection: Any = None,
    session: Any = None,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> dict[str, object]:
    """Collect the locked catalog through the vintage-only official API path."""

    resolved_key = str(api_key or os.environ.get("FRED_API_KEY") or "").strip()
    if not resolved_key:
        raise EconomicCycleVintageError(
            "FRED_API_KEY is required; revised CSV cannot substitute for vintages"
        )

    catalog = {item.series_id: item for item in get_economic_cycle_catalog()}
    requested = (
        list(catalog)
        if series_ids is None
        else list(dict.fromkeys(str(item).strip().upper() for item in series_ids))
    )
    unsupported = [series_id for series_id in requested if series_id not in catalog]
    if unsupported:
        raise EconomicCycleVintageError(
            f"Unsupported economic-cycle series: {', '.join(unsupported)}"
        )

    collected_at = datetime.now(timezone.utc)
    rows: list[dict[str, object]] = []
    failed: list[dict[str, str]] = []
    for series_id in requested:
        try:
            payload_rows = fetch_fred_vintages(
                series_id,
                api_key=resolved_key,
                session=session,
                timeout=int(timeout),
                retries=int(retries),
            )
            rows.extend(
                normalize_fred_vintage_rows(
                    catalog[series_id], payload_rows, collected_at=collected_at
                )
            )
        except Exception as exc:
            LOGGER.warning("Economic-cycle vintage fetch failed for %s: %s", series_id, exc)
            failed.append({"series_id": series_id, "reason": str(exc)[:500]})

    stored = upsert_economic_cycle_vintages(rows, connection=connection)
    coverage: dict[str, int] = {}
    for row in rows:
        status = str(row["coverage_status"])
        coverage[status] = coverage.get(status, 0) + 1
    found = {str(row["series_id"]) for row in rows}
    return {
        "requested": len(requested),
        "stored": stored,
        "missing": sorted(set(requested) - found),
        "failed": failed,
        "coverage": coverage,
        "source": "fred",
        "source_mode": "fred_output_type_2",
    }
