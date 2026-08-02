"""Normalize BEA NIPA PCE price-index components for breadth calculations."""

from __future__ import annotations

import json
import math
import os
import re
from datetime import date, datetime, timezone
from statistics import median
from typing import Callable, Mapping, Sequence
from urllib.parse import urlencode
from urllib.request import Request, urlopen

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema
from .fred_vintages import VINTAGE_TABLE, upsert_fred_vintage_rows


BEA_TABLE_NAME = "T20804"
BEA_SOURCE = "bea_nipa_t20804"
BEA_SOURCE_REF = "https://apps.bea.gov/api/data/?datasetname=NIPA&TableName=T20804"
REQUIRED_AGGREGATE_ROLES = ("headline", "goods", "services", "core")
DB_META = "finance_meta"
BEA_API_URL = "https://apps.bea.gov/api/data"


def _parse_datetime(value: str, *, field: str) -> datetime:
    try:
        parsed = datetime.fromisoformat(str(value).strip().replace("Z", "+00:00"))
    except ValueError as exc:
        raise ValueError(f"Invalid {field}: {value!r}") from exc
    if parsed.tzinfo is None:
        parsed = parsed.replace(tzinfo=timezone.utc)
    return parsed.astimezone(timezone.utc)


def _parse_month(value: object) -> str:
    match = re.fullmatch(r"(\d{4})M(\d{1,2})", str(value or "").strip())
    if match is None:
        raise ValueError(f"Invalid BEA monthly TimePeriod: {value!r}")
    year, month = int(match.group(1)), int(match.group(2))
    return date(year, month, 1).isoformat()


def _parse_number(value: object, multiplier: object) -> float | None:
    text = str(value or "").strip()
    if text in {"", "--", "...", "(NA)"}:
        return None
    try:
        parsed = float(text.replace(",", "")) * (10 ** int(str(multiplier or "0")))
    except (TypeError, ValueError):
        return None
    return parsed if math.isfinite(parsed) else None


def _component_role(description: str) -> str:
    normalized = " ".join(str(description or "").split()).strip().casefold()
    normalized = re.sub(r"\s+\d+$", "", normalized)
    if normalized.startswith(
        "personal consumption expenditures excluding food and energy"
    ):
        return "core"
    if normalized == "personal consumption expenditures":
        return "headline"
    if normalized == "goods":
        return "goods"
    if normalized == "services":
        return "services"
    if normalized.startswith("addenda"):
        return "addenda"
    return "detail"


def _extract_data(payload: Mapping[str, object]) -> list[Mapping[str, object]]:
    bea = payload.get("BEAAPI")
    if not isinstance(bea, Mapping):
        raise ValueError("BEA payload has no BEAAPI object")
    results = bea.get("Results")
    if not isinstance(results, Mapping):
        raise ValueError("BEA payload has no Results object")
    if results.get("Error") is not None:
        raise ValueError("BEA payload contains an API error")
    data = results.get("Data")
    if not isinstance(data, list):
        raise ValueError("BEA payload has no Data list")
    return [row for row in data if isinstance(row, Mapping)]


def normalize_bea_pce_components(
    payload: Mapping[str, object],
    *,
    released_at: str,
    collected_at: str,
) -> list[dict[str, object]]:
    """Normalize one stored BEA release without pretending it existed earlier."""

    released = _parse_datetime(released_at, field="released_at")
    collected = _parse_datetime(collected_at, field="collected_at")
    rows: list[dict[str, object]] = []
    for item in _extract_data(payload):
        if str(item.get("TableName") or "").strip().upper() != BEA_TABLE_NAME:
            continue
        line_number = str(item.get("LineNumber") or "").strip()
        description = " ".join(
            str(item.get("LineDescription") or "").split()
        ).strip()
        if not line_number or not description:
            continue
        observation_date = _parse_month(item.get("TimePeriod"))
        value = _parse_number(item.get("DataValue"), item.get("UNIT_MULT"))
        missing_fields = ["value"] if value is None else []
        rows.append(
            {
                "series_id": f"BEA_PCE_{line_number}",
                "observation_date": observation_date,
                "realtime_start": released.date().isoformat(),
                "realtime_end": "9999-12-31",
                "released_at": released.isoformat(),
                "source": BEA_SOURCE,
                "source_type": "official",
                "source_mode": "bea_nipa_getdata_release",
                "source_ref": BEA_SOURCE_REF,
                "series_name": description,
                "factor_group": "inflation_pce_component",
                "frequency": "monthly",
                "units": str(item.get("CL_UNIT") or "").strip() or None,
                "value": value,
                "release_lag_days": (
                    released.date() - date.fromisoformat(observation_date)
                ).days,
                "coverage_status": "missing" if missing_fields else "actual",
                "missing_fields_json": json.dumps(missing_fields),
                "collected_at": collected.replace(tzinfo=None).strftime(
                    "%Y-%m-%d %H:%M:%S.%f"
                ),
                "error_msg": None,
                "line_number": line_number,
                "component_role": _component_role(description),
            }
        )
    return sorted(
        rows,
        key=lambda row: (
            str(row["series_id"]),
            str(row["observation_date"]),
        ),
    )


def store_bea_pce_components(
    payload: Mapping[str, object],
    *,
    released_at: str,
    collected_at: str,
    db_factory: Callable[..., object] = MySQLClient,
) -> dict[str, object]:
    """Persist one actual BEA release without historical release backfilling."""

    rows = normalize_bea_pce_components(
        payload,
        released_at=released_at,
        collected_at=collected_at,
    )
    if not rows:
        return {"status": "failed", "stored": 0, "source": BEA_SOURCE}

    db = db_factory("localhost", "root", "1234", 3306)
    try:
        db.use_db(DB_META)
        schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
        db.execute(schema)
        sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
        stored = upsert_fred_vintage_rows(rows, db=db)
    finally:
        db.close()
    return {"status": "success", "stored": stored, "source": BEA_SOURCE}


def fetch_bea_pce_components(api_key: str) -> Mapping[str, object]:
    """Fetch the current official monthly T20804 table from the BEA API."""

    key = str(api_key or "").strip()
    if not key:
        raise ValueError("BEA_API_KEY is required")
    params = {
        "UserID": key,
        "method": "GetData",
        "datasetname": "NIPA",
        "TableName": BEA_TABLE_NAME,
        "Frequency": "M",
        "Year": "X",
        "ResultFormat": "JSON",
    }
    request = Request(
        f"{BEA_API_URL}?{urlencode(params)}",
        headers={"User-Agent": "quant-data-pipeline/1.0 research@example.com"},
    )
    with urlopen(request, timeout=60) as response:
        payload = json.loads(response.read().decode("utf-8"))
    if not isinstance(payload, Mapping):
        raise ValueError("BEA response must be a JSON object")
    return payload


def collect_and_store_bea_pce_components(
    *,
    api_key: str | None = None,
    collected_at: str | None = None,
    payload_fetcher: Callable[[str], Mapping[str, object]] = fetch_bea_pce_components,
    db_factory: Callable[..., object] = MySQLClient,
) -> dict[str, object]:
    """Store the current BEA table only from the instant it was collected."""

    resolved_key = str(api_key or os.environ.get("BEA_API_KEY") or "").strip()
    if not resolved_key:
        return {
            "status": "not_available",
            "stored": 0,
            "source": BEA_SOURCE,
            "reason": "BEA_API_KEY missing",
        }
    observed = collected_at or datetime.now(timezone.utc).isoformat()
    payload = payload_fetcher(resolved_key)
    return store_bea_pce_components(
        payload,
        released_at=observed,
        collected_at=observed,
        db_factory=db_factory,
    )


def calculate_component_breadth(
    rows: Sequence[Mapping[str, object]],
    *,
    threshold_pct: float = 0.3,
) -> dict[str, object]:
    """Calculate latest component breadth from consecutive stored index values."""

    threshold = float(threshold_pct)
    if not math.isfinite(threshold):
        raise ValueError("threshold_pct must be finite")

    by_series: dict[str, list[Mapping[str, object]]] = {}
    for row in rows:
        series_id = str(row.get("series_id") or "").strip()
        if series_id:
            by_series.setdefault(series_id, []).append(row)

    changes: list[dict[str, object]] = []
    available_roles: set[str] = set()
    for series_id, series_rows in by_series.items():
        eligible = sorted(
            (
                row
                for row in series_rows
                if isinstance(row.get("value"), (int, float))
                and math.isfinite(float(row["value"]))
            ),
            key=lambda row: str(row.get("observation_date") or ""),
        )
        if not eligible:
            continue
        role = str(eligible[-1].get("component_role") or "detail")
        available_roles.add(role)
        if len(eligible) < 2:
            continue
        previous, current = eligible[-2], eligible[-1]
        previous_value = float(previous["value"])
        if previous_value <= 0:
            continue
        mom_pct = (float(current["value"]) / previous_value - 1.0) * 100.0
        changes.append(
            {
                "series_id": series_id,
                "role": role,
                "observation_date": str(current["observation_date"]),
                "mom_pct": mom_pct,
            }
        )

    missing_roles = [
        role for role in REQUIRED_AGGREGATE_ROLES if role not in available_roles
    ]
    if missing_roles:
        return {
            "status": "NOT_AVAILABLE",
            "reason": "missing_required_aggregates",
            "missing_roles": missing_roles,
            "component_count": 0,
        }

    roles_with_history = {str(item["role"]) for item in changes}
    insufficient_roles = [
        role for role in REQUIRED_AGGREGATE_ROLES if role not in roles_with_history
    ]
    if insufficient_roles:
        return {
            "status": "NOT_AVAILABLE",
            "reason": "insufficient_required_history",
            "missing_roles": insufficient_roles,
            "component_count": 0,
        }

    aggregate_mom = {
        role: next(
            item["mom_pct"] for item in changes if item["role"] == role
        )
        for role in REQUIRED_AGGREGATE_ROLES
    }
    components = [
        item
        for item in changes
        if item["role"] in {"goods", "services", "detail"}
    ]
    if not components:
        return {
            "status": "NOT_AVAILABLE",
            "reason": "no_comparable_components",
            "missing_roles": [],
            "component_count": 0,
        }
    latest_month = max(str(item["observation_date"]) for item in components)
    current_components = [
        item for item in components if item["observation_date"] == latest_month
    ]
    above = sum(
        float(item["mom_pct"]) + 1e-12 >= threshold
        for item in current_components
    )
    return {
        "status": "READY",
        "as_of_month": latest_month,
        "threshold_pct": threshold,
        "component_count": len(current_components),
        "above_threshold_count": above,
        "share_above_threshold": above / len(current_components),
        "median_mom_pct": median(
            float(item["mom_pct"]) for item in current_components
        ),
        "aggregate_mom_pct": aggregate_mom,
    }
