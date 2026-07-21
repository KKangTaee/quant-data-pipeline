from __future__ import annotations

from collections import Counter
from collections.abc import Mapping, Sequence
from typing import Any


READINESS_STATES = ("COMPLETE", "PARTIAL", "BLOCKED")
GAP_CODES = (
    "STALE_SNAPSHOT",
    "MISSING_QUOTE",
    "LIMITED_HISTORY",
    "SYMBOL_REVIEW",
    "PROVIDER_GAP",
    "NO_UNIVERSE",
)


def classify_missing_row(row: Mapping[str, Any]) -> str:
    explicit = str(row.get("gap_code") or row.get("Gap Code") or "").strip().upper()
    if explicit in GAP_CODES:
        return explicit

    reason = " ".join(
        str(
            row.get("reason")
            or row.get("Reason")
            or row.get("Likely Cause")
            or ""
        ).lower().split()
    )
    profile_status = str(row.get("Profile Status") or row.get("profile_status") or "").lower()
    issue = str(row.get("Market Data Issue") or row.get("market_data_issue") or "").lower()

    if "stale" in reason:
        return "STALE_SNAPSHOT"
    if profile_status in {"error", "not_found", "delisted"}:
        return "SYMBOL_REVIEW"
    if any(token in reason for token in ("ticker", "symbol", "alias", "listing")):
        return "SYMBOL_REVIEW"
    if "start price" in reason or "history" in reason or "insufficient" in reason:
        return "LIMITED_HISTORY"
    if any(token in reason for token in ("end price", "latest price", "latest quote", "intraday")):
        return "MISSING_QUOTE"
    if issue and "no repeated market data issue" not in issue:
        return "PROVIDER_GAP"
    return "PROVIDER_GAP"


def _metric_counts(valid: int, total: int) -> dict[str, int]:
    bounded_total = max(0, int(total))
    bounded_valid = min(bounded_total, max(0, int(valid)))
    return {
        "valid": bounded_valid,
        "total": bounded_total,
        "excluded": bounded_total - bounded_valid,
    }


def _basis_label(value: str | None) -> str | None:
    normalized = str(value or "").strip().upper()
    if not normalized or normalized == "UNAVAILABLE":
        return None
    if "INTRADAY" in normalized:
        return "INTRADAY"
    if "EOD" in normalized or "DAILY DB" in normalized:
        return "EOD"
    return normalized


def build_collection_readiness(
    *,
    universe_count: int,
    returnable_count: int,
    volume_count: int,
    market_cap_count: int,
    missing_rows: Sequence[Mapping[str, Any]],
    basis: str | None,
    effective_end_date: str | None,
    stale_days: int | None,
) -> dict[str, Any]:
    """Build user-facing readiness without treating missing metrics as zero."""

    total = max(0, int(universe_count))
    normalized_basis = _basis_label(basis)
    return_metric = _metric_counts(returnable_count, total)
    volume_metric = _metric_counts(volume_count, total)
    market_cap_metric = _metric_counts(market_cap_count, total)
    stale = stale_days is not None and int(stale_days) > 0

    gaps = Counter(classify_missing_row(row) for row in missing_rows)
    if stale:
        gaps["STALE_SNAPSHOT"] += 1
    if total == 0:
        gaps["NO_UNIVERSE"] += 1

    if total == 0:
        state = "BLOCKED"
        primary_action = "UNIVERSE_SETUP"
    elif return_metric["valid"] == 0 or normalized_basis is None:
        state = "BLOCKED"
        primary_action = "PREPARE_HISTORY"
    elif stale or any(
        metric["excluded"] > 0
        for metric in (return_metric, volume_metric, market_cap_metric)
    ):
        state = "PARTIAL"
        if gaps.get("LIMITED_HISTORY"):
            primary_action = "PREPARE_HISTORY"
        elif gaps.get("SYMBOL_REVIEW"):
            primary_action = "REVIEW_SYMBOLS"
        else:
            primary_action = "REFRESH_MISSING"
    else:
        state = "COMPLETE"
        primary_action = None

    return {
        "schema_version": "market_movers_collection_readiness_v1",
        "state": state,
        "publish_results": state != "BLOCKED",
        "basis": normalized_basis,
        "effective_end_date": effective_end_date,
        "freshness": {
            "state": "UNKNOWN" if stale_days is None else ("STALE" if stale else "FRESH"),
            "stale_days": stale_days,
        },
        "metrics": {
            "return": return_metric,
            "volume": volume_metric,
            "market_cap": market_cap_metric,
        },
        "gap_summary": [
            {"code": code, "count": count}
            for code, count in sorted(gaps.items(), key=lambda item: (-item[1], item[0]))
        ],
        "primary_action": primary_action,
    }
