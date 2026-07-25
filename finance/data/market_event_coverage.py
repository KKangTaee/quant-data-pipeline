from __future__ import annotations

import hashlib
import json
from collections.abc import Sequence
from typing import Any


SUCCESS_DIAGNOSTIC_STATUSES = {
    "checked_no_event",
    "event_found",
    "missing",
}


def _symbols(values: Sequence[Any] | None) -> list[str]:
    output: list[str] = []
    seen: set[str] = set()
    for value in values or []:
        symbol = str(value or "").strip().upper()
        if symbol and symbol not in seen:
            seen.add(symbol)
            output.append(symbol)
    return output


def merge_priority_earnings_symbols(
    *,
    retry_symbols: Sequence[Any] = (),
    portfolio_symbols: Sequence[Any] = (),
    watchlist_symbols: Sequence[Any] = (),
    major_cap_symbols: Sequence[Any] = (),
    known_event_symbols: Sequence[Any] = (),
) -> list[str]:
    """Merge earnings sources in priority order while removing duplicate symbols."""
    return _symbols(
        [
            *retry_symbols,
            *portfolio_symbols,
            *watchlist_symbols,
            *major_cap_symbols,
            *known_event_symbols,
        ]
    )


def _universe_hash(symbols: list[str]) -> str:
    return hashlib.sha256(
        json.dumps(symbols, separators=(",", ":")).encode("utf-8")
    ).hexdigest()


def build_sp500_shard_plan(
    universe_symbols: Sequence[Any],
    checkpoint: dict[str, Any] | None,
    *,
    batch_size: int = 100,
) -> dict[str, Any]:
    """Select the next deterministic S&P 500 shard for the active coverage cycle."""
    universe = _symbols(universe_symbols)
    prior = dict(checkpoint or {})
    details = dict(prior.get("details") or {})
    universe_hash = _universe_hash(universe)
    cycle_complete = str(prior.get("coverage_status") or "").lower() == "complete"
    same_universe = details.get("universe_hash") == universe_hash
    reset = not same_universe or cycle_complete
    cursor = 0 if reset else max(0, int(prior.get("cursor_offset") or 0))
    size = max(1, int(batch_size or 100))
    batch = universe[cursor : cursor + size]
    if not batch and universe:
        cursor = 0
        batch = universe[:size]
    return {
        "coverage_key": "earnings:sp500_cycle",
        "event_family": "earnings",
        "universe_scope": "sp500",
        "expected_symbols": universe,
        "expected_items": len(universe),
        "batch_symbols": batch,
        "batch_size": size,
        "cursor_offset": cursor,
        "prior": {} if reset else prior,
        "prior_missing_streaks": (
            dict(details.get("missing_streaks") or {})
            if cycle_complete and same_universe
            else {}
        ),
        "universe_hash": universe_hash,
        "cycle_reset": reset,
    }


def apply_sp500_shard_result(
    plan: dict[str, Any],
    diagnostics: Sequence[dict[str, Any]],
    *,
    checked_at: str,
) -> dict[str, Any]:
    """Apply only in-universe diagnostics and return the next persisted checkpoint."""
    prior = dict(plan.get("prior") or {})
    prior_details = dict(prior.get("details") or {})
    expected = _symbols(plan.get("expected_symbols"))
    expected_set = set(expected)
    covered = set(_symbols(prior_details.get("covered_symbols"))) & expected_set
    failed = set(_symbols(prior_details.get("failed_symbols"))) & expected_set
    missing_streaks = {
        str(key).upper(): int(value)
        for key, value in {
            **dict(plan.get("prior_missing_streaks") or {}),
            **dict(prior_details.get("missing_streaks") or {}),
        }.items()
        if str(key).upper() in expected_set
    }
    applied_diagnostic_count = 0
    for diagnostic in diagnostics:
        symbol = str(diagnostic.get("symbol") or "").strip().upper()
        status = str(diagnostic.get("status") or "").strip().lower()
        if not symbol or symbol not in expected_set:
            continue
        applied_diagnostic_count += 1
        if status in SUCCESS_DIAGNOSTIC_STATUSES:
            covered.add(symbol)
            failed.discard(symbol)
            if status in {"checked_no_event", "missing"}:
                missing_streaks[symbol] = missing_streaks.get(symbol, 0) + 1
            else:
                missing_streaks[symbol] = 0
        else:
            failed.add(symbol)

    next_cursor = int(plan.get("cursor_offset") or 0) + len(
        plan.get("batch_symbols") or []
    )
    if next_cursor >= len(expected):
        next_cursor = 0
    complete = bool(expected) and len(covered) == len(expected) and not failed
    return {
        "coverage_key": "earnings:sp500_cycle",
        "event_family": "earnings",
        "universe_scope": "sp500",
        "expected_items": len(expected),
        "covered_items": len(covered),
        "failed_items": len(failed),
        "cursor_offset": next_cursor,
        "batch_size": int(plan.get("batch_size") or 100),
        "coverage_status": "complete" if complete else "partial",
        "cycle_started_at": prior.get("cycle_started_at") or checked_at,
        "cycle_completed_at": checked_at if complete else None,
        "last_attempted_at": checked_at,
        "last_success_at": (
            checked_at
            if applied_diagnostic_count and not failed
            else prior.get("last_success_at")
        ),
        "details": {
            "universe_hash": plan.get("universe_hash"),
            "covered_symbols": sorted(covered),
            "failed_symbols": sorted(failed),
            "missing_streaks": dict(sorted(missing_streaks.items())),
        },
    }
