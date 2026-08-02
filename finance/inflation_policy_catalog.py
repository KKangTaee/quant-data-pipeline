"""Independent source catalog for the inflation and policy path model."""

from __future__ import annotations

import os
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Callable, Sequence

from finance.data.db.mysql import MySQLClient
from finance.data.db.schema import PROVIDER_SCHEMAS, sync_table_schema
from finance.data.fred_vintages import (
    VINTAGE_TABLE,
    fetch_fred_vintages,
    normalize_fred_vintage_rows,
    upsert_fred_vintage_rows,
)


DB_META = "finance_meta"


@dataclass(frozen=True)
class InflationPolicySeriesSpec:
    """Describe one official series and its role in the independent model."""

    series_id: str
    group: str
    frequency: str
    transform: str
    required_for: tuple[str, ...]
    release_policy: str


_CATALOG = (
    InflationPolicySeriesSpec("PCEPI", "inflation", "monthly", "index_mom_q4q4", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("PCEPILFE", "inflation", "monthly", "index_mom_q4q4", ("inflation", "policy"), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("CPIAUCSL", "inflation", "monthly", "index_mom_yoy", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("CPILFESL", "inflation", "monthly", "index_mom_yoy", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("PCETRIM12M159SFRBDAL", "inflation", "monthly", "yoy_level", ("inflation",), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("CES0500000003", "labor_cost", "monthly", "mom_yoy", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("ECIWAG", "labor_cost", "quarterly", "qoq_yoy", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("ULCNFB", "labor_cost", "quarterly", "annualized_qoq", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("PPIACO", "inflation", "monthly", "mom_yoy", ("inflation",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("MICH", "inflation", "monthly", "level", ("inflation", "rates"), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("UNRATE", "labor", "monthly", "level_change", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("PAYEMS", "labor", "monthly", "level_change", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("ICSA", "labor", "weekly", "four_week_mean", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("AWHMAN", "labor", "monthly", "level_change", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("TEMPHELPS", "labor", "monthly", "level_change", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("INDPRO", "activity", "monthly", "mom_3m", ("policy",), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("W875RX1", "activity", "monthly", "mom_3m", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("PCEC96", "activity", "monthly", "mom_3m", ("policy",), "OFFICIAL_0830_ET"),
    InflationPolicySeriesSpec("CMRMTSPL", "activity", "monthly", "mom_3m", ("policy",), "OFFICIAL_1000_ET"),
    InflationPolicySeriesSpec("FEDFUNDS", "policy", "monthly", "level", ("policy",), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("DGS2", "rates", "daily", "level", ("policy", "rates", "reverse"), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("DGS10", "rates", "daily", "level", ("rates", "reverse"), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("DFII10", "rates", "daily", "level", ("rates", "reverse"), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("T10YIE", "rates", "daily", "level", ("rates", "reverse"), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("T10Y2Y", "rates", "daily", "level", ("rates",), "END_OF_DAY_ET"),
    InflationPolicySeriesSpec("BAMLH0A0HYM2", "rates", "daily", "level", ("rates",), "END_OF_DAY_ET"),
)


def get_inflation_policy_catalog() -> tuple[InflationPolicySeriesSpec, ...]:
    """Return the immutable independent series catalog."""

    return _CATALOG


def collect_inflation_policy_vintages(
    *,
    catalog: Sequence[InflationPolicySeriesSpec] | None = None,
    api_key: str | None = None,
    db_factory: Callable[..., object] = MySQLClient,
) -> dict[str, object]:
    """Collect the catalog through ALFRED and persist only normalized raw rows."""

    resolved_key = str(api_key or os.environ.get("FRED_API_KEY") or "").strip()
    if not resolved_key:
        raise ValueError("FRED_API_KEY is required for inflation-policy vintages")
    specs = tuple(catalog or get_inflation_policy_catalog())
    if not specs:
        raise ValueError("catalog cannot be empty")

    db = db_factory("localhost", "root", "1234", 3306)
    coverage: dict[str, int] = {}
    failed: list[dict[str, str]] = []
    stored = 0
    collected_at = datetime.now(timezone.utc)
    try:
        db.use_db(DB_META)
        schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
        db.execute(schema)
        sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
        for spec in specs:
            try:
                payload_rows = fetch_fred_vintages(
                    spec.series_id,
                    api_key=resolved_key,
                )
                normalized = normalize_fred_vintage_rows(
                    spec,
                    payload_rows,
                    collected_at=collected_at,
                )
                count = upsert_fred_vintage_rows(normalized, db=db)
                stored += count
                coverage[spec.series_id] = count
            except Exception as exc:
                failed.append(
                    {"series_id": spec.series_id, "reason": str(exc)[:500]}
                )
    finally:
        db.close()

    status = "success" if not failed else "partial_success" if stored else "failed"
    return {
        "status": status,
        "requested": len(specs),
        "stored": stored,
        "coverage": coverage,
        "failed": failed,
        "source": "fred_alfred",
    }
