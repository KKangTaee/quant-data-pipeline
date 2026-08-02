"""Backend-only orchestration for inflation-policy raw source refreshes."""

from __future__ import annotations

import argparse
import json
from collections.abc import Callable, Mapping, Sequence
from datetime import datetime, timezone
from typing import Any

from finance.data.bea_pce_components import collect_and_store_bea_pce_components
from finance.data.fomc_policy import (
    collect_and_store_fomc_policy_history,
    collect_and_store_fomc_sep_distributions,
)
from finance.data.nyfed_term_premium import collect_and_store_acm_term_premium
from finance.inflation_policy_catalog import collect_inflation_policy_vintages


REQUIRED_SOURCES = ("macro_vintages", "sep", "decisions")
OPTIONAL_SOURCES = ("term_premium", "pce_components")
SOURCE_ORDER = (*REQUIRED_SOURCES, *OPTIONAL_SOURCES)
REQUIRED_MACRO_SERIES = ("PCEPILFE", "DGS2", "DGS10", "DFII10", "T10YIE")
SUCCESS_STATUSES = {"success", "partial_success", "ready", "limited"}


def _row_count(payload: Mapping[str, object]) -> int:
    for field in ("rows", "stored", "rows_written"):
        value = payload.get(field)
        if value is not None:
            try:
                return max(0, int(value))
            except (TypeError, ValueError):
                return 0
    return 0


def _source_status(payload: Mapping[str, object]) -> str:
    explicit = str(payload.get("status") or "").strip().casefold()
    if explicit:
        return explicit
    return "success" if _row_count(payload) > 0 else "failed"


def _compact_source(payload: Mapping[str, object]) -> dict[str, object]:
    compact: dict[str, object] = {
        "status": _source_status(payload),
        "rows": _row_count(payload),
    }
    for field in ("coverage_status", "reason", "requested", "source"):
        if payload.get(field) not in (None, ""):
            compact[field] = payload[field]
    failed = payload.get("failed")
    if isinstance(failed, (list, tuple, set)):
        compact["failed_count"] = len(failed)
    return compact


def _default_collectors(observed_at: str) -> dict[str, Callable[[], Mapping[str, object]]]:
    return {
        "macro_vintages": collect_inflation_policy_vintages,
        "sep": collect_and_store_fomc_sep_distributions,
        "decisions": collect_and_store_fomc_policy_history,
        "term_premium": lambda: collect_and_store_acm_term_premium(
            collected_at=observed_at
        ),
        "pce_components": lambda: collect_and_store_bea_pce_components(
            collected_at=observed_at
        ),
    }


def run_inflation_policy_raw_refresh(
    *,
    as_of_at: str | None = None,
    collectors: Mapping[str, Callable[[], Mapping[str, object]]] | None = None,
) -> dict[str, object]:
    """Run bounded named collectors and fail closed on required source gaps."""

    observed_at = str(as_of_at or datetime.now(timezone.utc).isoformat())
    resolved = dict(collectors or _default_collectors(observed_at))
    source_results: dict[str, dict[str, object]] = {}
    raw_results: dict[str, Mapping[str, object]] = {}
    failed_sources: list[str] = []
    limited_sources: list[str] = []

    for source_name in SOURCE_ORDER:
        collector = resolved.get(source_name)
        if collector is None:
            payload: Mapping[str, object] = {
                "status": "failed" if source_name in REQUIRED_SOURCES else "not_available",
                "rows": 0,
                "reason": "collector missing",
            }
        else:
            try:
                payload = dict(collector() or {})
            except Exception as exc:
                payload = {
                    "status": "failed",
                    "rows": 0,
                    "reason": f"{type(exc).__name__}: {str(exc)[:300]}",
                }
        raw_results[source_name] = payload
        source_results[source_name] = _compact_source(payload)
        status = _source_status(payload)
        rows = _row_count(payload)
        unavailable = status not in SUCCESS_STATUSES or rows <= 0
        if source_name in REQUIRED_SOURCES and unavailable:
            failed_sources.append(source_name)
        elif source_name in OPTIONAL_SOURCES and (
            unavailable
            or str(payload.get("coverage_status") or "").upper()
            in {"LIMITED", "NOT_AVAILABLE", "FAILED"}
        ):
            limited_sources.append(source_name)

    required_series_gaps: list[str] = []
    macro_coverage = raw_results.get("macro_vintages", {}).get("coverage")
    if isinstance(macro_coverage, Mapping):
        required_series_gaps = sorted(
            series_id
            for series_id in REQUIRED_MACRO_SERIES
            if int(macro_coverage.get(series_id) or 0) <= 0
        )
    materialization_allowed = not failed_sources and not required_series_gaps
    if not materialization_allowed:
        status = "failed"
    elif limited_sources:
        status = "partial_success"
    else:
        status = "success"
    rows_written = sum(int(item["rows"]) for item in source_results.values())
    return {
        "status": status,
        "as_of_at": observed_at,
        "rows_written": rows_written,
        "failed_sources": sorted(failed_sources),
        "limited_sources": sorted(limited_sources),
        "required_series_gaps": required_series_gaps,
        "materialization_allowed": materialization_allowed,
        "sources": source_results,
    }


def main(argv: Sequence[str] | None = None) -> int:
    parser = argparse.ArgumentParser(
        description="Refresh official inflation-policy raw sources."
    )
    parser.add_argument("--as-of-at", default=None)
    args = parser.parse_args(argv)
    result = run_inflation_policy_raw_refresh(as_of_at=args.as_of_at)
    print(json.dumps(result, ensure_ascii=False, sort_keys=True))
    return 0 if result["status"] in {"success", "partial_success"} else 1


if __name__ == "__main__":
    raise SystemExit(main())
