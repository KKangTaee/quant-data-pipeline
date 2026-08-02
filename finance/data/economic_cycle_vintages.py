"""Collect economic-cycle vintages through shared FRED/ALFRED primitives."""

from __future__ import annotations

import logging
import os
from datetime import datetime, timezone
from typing import Any, Iterable

from finance.economic_cycle_catalog import get_economic_cycle_catalog

from .db.mysql import MySQLClient
from .db.schema import PROVIDER_SCHEMAS, sync_table_schema
from .fred_vintages import (
    DEFAULT_OBSERVATION_PAGE_SIZE,
    DEFAULT_RETRIES,
    DEFAULT_TIMEOUT,
    EARLIEST_REALTIME_DATE,
    FRED_API_URL,
    FRED_SOURCE_MODE,
    FRED_VINTAGE_DATES_URL,
    MAX_VINTAGE_DATES_PER_REQUEST,
    MAX_VINTAGE_DATE_PAGE_SIZE,
    OPEN_ENDED_REALTIME_DATE,
    VINTAGE_TABLE,
    VINTAGE_UPSERT_MAX_STATEMENT_LENGTH,
    FredVintageError,
    _request_json,
    build_realtime_windows,
    fetch_fred_vintage_dates,
    fetch_fred_vintages,
    iter_fred_vintage_pages,
    normalize_fred_vintage_rows,
    time,
    upsert_fred_vintage_rows,
    urlopen,
)
from .fred_vintages import (
    load_latest_vintage_realtime_starts as load_latest_fred_realtime_starts,
)


DB_META = "finance_meta"
LOGGER = logging.getLogger(__name__)

# Backward-compatible error name for existing economic-cycle callers.
EconomicCycleVintageError = FredVintageError


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
    """Preserve the cycle writer API while using the shared idempotent UPSERT."""

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
        return upsert_fred_vintage_rows(rows, db=db)
    finally:
        if owns_connection:
            db.close()


def load_latest_vintage_realtime_starts(
    series_ids: Iterable[str],
    *,
    connection: Any = None,
) -> dict[str, str]:
    """Preserve the cycle reader API over the source-neutral boundary helper."""

    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    try:
        if owns_connection:
            db.use_db(DB_META)
        return load_latest_fred_realtime_starts(series_ids, db=db)
    finally:
        if owns_connection:
            db.close()


def collect_economic_cycle_vintages(
    *,
    series_ids: Iterable[str] | None = None,
    api_key: str | None = None,
    connection: Any = None,
    session: Any = None,
    page_size: int = DEFAULT_OBSERVATION_PAGE_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
) -> dict[str, object]:
    """Collect the locked cycle catalog through the shared official API path."""

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
    failed: list[dict[str, str]] = []
    coverage: dict[str, int] = {}
    found: set[str] = set()
    stored = 0
    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    try:
        if owns_connection:
            db.use_db(DB_META)
            schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
            db.execute(schema)
            sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
        for series_id in requested:
            try:
                for payload_rows in iter_fred_vintage_pages(
                    series_id,
                    api_key=resolved_key,
                    session=session,
                    page_size=int(page_size),
                    timeout=int(timeout),
                    retries=int(retries),
                ):
                    normalized_rows = normalize_fred_vintage_rows(
                        catalog[series_id],
                        payload_rows,
                        collected_at=collected_at,
                    )
                    stored += upsert_economic_cycle_vintages(
                        normalized_rows,
                        connection=db,
                    )
                    for row in normalized_rows:
                        status = str(row["coverage_status"])
                        coverage[status] = coverage.get(status, 0) + 1
                        found.add(str(row["series_id"]))
            except Exception as exc:
                LOGGER.warning(
                    "Economic-cycle vintage fetch failed for %s: %s",
                    series_id,
                    exc,
                )
                failed.append({"series_id": series_id, "reason": str(exc)[:500]})
    finally:
        if owns_connection:
            db.close()

    return {
        "requested": len(requested),
        "stored": stored,
        "missing": sorted(set(requested) - found),
        "failed": failed,
        "coverage": coverage,
        "source": "fred",
        "source_mode": FRED_SOURCE_MODE,
    }


def collect_incremental_economic_cycle_vintages(
    *,
    series_ids: Iterable[str] | None = None,
    api_key: str | None = None,
    connection: Any = None,
    session: Any = None,
    page_size: int = DEFAULT_OBSERVATION_PAGE_SIZE,
    timeout: int = DEFAULT_TIMEOUT,
    retries: int = DEFAULT_RETRIES,
    realtime_start_loader: Any = load_latest_vintage_realtime_starts,
    page_iter: Any = iter_fred_vintage_pages,
    writer: Any = upsert_economic_cycle_vintages,
) -> dict[str, object]:
    """Collect each cycle series from its latest stored boundary, inclusively."""

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
    failed: list[dict[str, str]] = []
    coverage: dict[str, int] = {}
    found: set[str] = set()
    stored = 0
    owns_connection = connection is None
    db = connection or MySQLClient("localhost", "root", "1234", 3306)
    overlap_starts: dict[str, str] = {}
    try:
        if owns_connection:
            db.use_db(DB_META)
            schema = PROVIDER_SCHEMAS[VINTAGE_TABLE]
            db.execute(schema)
            sync_table_schema(db, VINTAGE_TABLE, schema, DB_META)
        latest_starts = realtime_start_loader(requested, connection=db)
        overlap_starts = {
            series_id: latest_starts.get(series_id, EARLIEST_REALTIME_DATE)
            for series_id in requested
        }
        for series_id in requested:
            try:
                for payload_rows in page_iter(
                    series_id,
                    api_key=resolved_key,
                    session=session,
                    realtime_start=overlap_starts[series_id],
                    page_size=int(page_size),
                    timeout=int(timeout),
                    retries=int(retries),
                ):
                    normalized_rows = normalize_fred_vintage_rows(
                        catalog[series_id],
                        payload_rows,
                        collected_at=collected_at,
                    )
                    stored += writer(normalized_rows, connection=db)
                    for row in normalized_rows:
                        status = str(row["coverage_status"])
                        coverage[status] = coverage.get(status, 0) + 1
                        found.add(str(row["series_id"]))
            except Exception as exc:
                LOGGER.warning(
                    "Incremental economic-cycle vintage fetch failed for %s: %s",
                    series_id,
                    exc,
                )
                failed.append({"series_id": series_id, "reason": str(exc)[:500]})
    finally:
        if owns_connection:
            db.close()

    return {
        "requested": len(requested),
        "stored": stored,
        "missing": sorted(set(requested) - found),
        "failed": failed,
        "coverage": coverage,
        "source": "fred",
        "source_mode": FRED_SOURCE_MODE,
        "collection_mode": "incremental_overlap",
        "overlap_starts": overlap_starts,
    }
