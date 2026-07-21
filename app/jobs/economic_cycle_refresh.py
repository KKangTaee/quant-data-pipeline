"""Fail-closed weekday refresh for the Overview economic-cycle nowcast."""

from __future__ import annotations

from datetime import date, datetime
from time import perf_counter
from typing import Any, Callable

from app.jobs.ingestion.common import JobResult, build_result
from finance.data.economic_cycle_vintages import (
    collect_incremental_economic_cycle_vintages,
)
from finance.economic_cycle_pipeline import (
    materialize_economic_cycle_intramonth_snapshot,
    rollover_closed_economic_cycle_month,
)


def _as_date(value: str | date | None) -> date:
    if value is None:
        return datetime.now().date()
    if isinstance(value, datetime):
        return value.date()
    if isinstance(value, date):
        return value
    return date.fromisoformat(str(value)[:10])


def _timestamp() -> str:
    return datetime.now().strftime("%Y-%m-%d %H:%M:%S")


def _failed_series(summary: dict[str, object]) -> list[str]:
    failed = []
    for item in summary.get("failed") or []:
        series_id = item.get("series_id") if isinstance(item, dict) else item
        if series_id:
            failed.append(str(series_id).upper())
    failed.extend(str(item).upper() for item in summary.get("missing") or [])
    return list(dict.fromkeys(failed))


def run_economic_cycle_intramonth_refresh(
    *,
    as_of_date: str | date | None = None,
    collector: Callable[..., dict[str, object]] = (
        collect_incremental_economic_cycle_vintages
    ),
    rollover: Callable[..., dict[str, object]] = (
        rollover_closed_economic_cycle_month
    ),
    materializer: Callable[..., object] = (
        materialize_economic_cycle_intramonth_snapshot
    ),
) -> JobResult:
    """Collect, roll a closed month, then append one usable intramonth row."""

    job_name = "refresh_economic_cycle_intramonth"
    started_at = _timestamp()
    t0 = perf_counter()
    resolved_date = _as_date(as_of_date)
    collection: dict[str, object] = {}
    rollover_result: dict[str, object] | None = None
    try:
        collection = collector()
        failed_series = _failed_series(collection)
        if failed_series:
            return build_result(
                job_name=job_name,
                status="failed",
                started_at=started_at,
                finished_at=_timestamp(),
                duration_sec=perf_counter() - t0,
                rows_written=0,
                symbols_requested=int(collection.get("requested") or 0),
                symbols_processed=0,
                failed_symbols=failed_series,
                message=(
                    "Economic-cycle source refresh has gaps; the last-good "
                    "intramonth snapshot was preserved."
                ),
                details={
                    "as_of_date": resolved_date.isoformat(),
                    "collection_rows_written": int(collection.get("stored") or 0),
                    "collection_mode": collection.get("collection_mode"),
                    "snapshot_written": False,
                },
            )

        rollover_result = rollover(as_of_date=resolved_date)
        snapshot = materializer(as_of_date=resolved_date)
        snapshot_status = str(getattr(snapshot, "status", "LIMITED"))
        return build_result(
            job_name=job_name,
            status=("success" if snapshot_status == "READY" else "partial_success"),
            started_at=started_at,
            finished_at=_timestamp(),
            duration_sec=perf_counter() - t0,
            rows_written=int(rollover_result.get("rows_written") or 0) + 1,
            symbols_requested=int(collection.get("requested") or 0),
            symbols_processed=int(collection.get("requested") or 0),
            message=(
                "Economic-cycle intramonth snapshot refreshed."
                if snapshot_status == "READY"
                else "Economic-cycle intramonth snapshot refreshed as provisional."
            ),
            details={
                "as_of_date": resolved_date.isoformat(),
                "model_version": getattr(snapshot, "model_version", None),
                "publication_status": snapshot_status,
                "collection_rows_written": int(collection.get("stored") or 0),
                "collection_mode": collection.get("collection_mode"),
                "rollover": rollover_result,
                "snapshot_written": True,
                "target_table": "finance_meta.economic_cycle_snapshot",
            },
        )
    except Exception as exc:
        return build_result(
            job_name=job_name,
            status="failed",
            started_at=started_at,
            finished_at=_timestamp(),
            duration_sec=perf_counter() - t0,
            rows_written=int((rollover_result or {}).get("rows_written") or 0),
            failed_symbols=_failed_series(collection),
            message=f"Economic-cycle intramonth refresh failed: {exc}",
            details={
                "as_of_date": resolved_date.isoformat(),
                "collection_rows_written": int(collection.get("stored") or 0),
                "collection_mode": collection.get("collection_mode"),
                "rollover": rollover_result,
                "snapshot_written": False,
                "target_table": "finance_meta.economic_cycle_snapshot",
            },
        )
