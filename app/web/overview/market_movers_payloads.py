from __future__ import annotations

import math
from collections.abc import Mapping, Sequence
from datetime import date, datetime
from decimal import Decimal
from typing import Any

import pandas as pd


GROUP_PERIODS = ("daily", "weekly", "monthly")


def _json_safe(value: Any) -> Any:
    if isinstance(value, pd.DataFrame):
        safe = value.astype(object).where(pd.notna(value), None)
        return [_json_safe(row) for row in safe.to_dict(orient="records")]
    if isinstance(value, pd.Series):
        return _json_safe(value.to_dict())
    if isinstance(value, Mapping):
        return {str(key): _json_safe(item) for key, item in value.items()}
    if isinstance(value, (list, tuple, set)):
        return [_json_safe(item) for item in value]
    if isinstance(value, pd.Timestamp):
        return value.isoformat()
    if isinstance(value, (datetime, date)):
        return value.isoformat()
    if isinstance(value, Decimal):
        return float(value)
    if isinstance(value, float):
        return value if math.isfinite(value) else None
    if value is pd.NA:
        return None
    item_method = getattr(value, "item", None)
    if callable(item_method):
        try:
            return _json_safe(item_method())
        except (TypeError, ValueError):
            return str(value)
    return value


def _records(value: Any) -> list[dict[str, Any]]:
    converted = _json_safe(value)
    if not isinstance(converted, list):
        return []
    return [dict(row) for row in converted if isinstance(row, Mapping)]


def _group_period_payload(snapshot: Mapping[str, Any] | None) -> dict[str, Any]:
    if not isinstance(snapshot, Mapping):
        return {
            "status": "UNAVAILABLE",
            "flow": [],
            "bellwethers": [],
            "ticker_leaders": [],
            "groups": [],
            "coverage": {},
        }
    return {
        "status": str(snapshot.get("status") or "UNAVAILABLE"),
        "group_by": snapshot.get("group_by"),
        "flow": _records(snapshot.get("group_flow")),
        "bellwethers": _records(snapshot.get("market_cap_bellwether_rows")),
        "ticker_leaders": _records(snapshot.get("ticker_leader_rows")),
        "groups": _records(snapshot.get("rows")),
        "coverage": _json_safe(snapshot.get("coverage") or {}),
        "date_window": _json_safe(snapshot.get("date_window") or {}),
    }


def _group_symbol(row: Mapping[str, Any]) -> tuple[str, str]:
    group = str(row.get("Group") or row.get("group") or "Unknown")
    symbol = str(row.get("Symbol") or row.get("symbol") or "").strip().upper()
    return group, symbol


def _period_value(row: Mapping[str, Any], *keys: str) -> float | None:
    for key in keys:
        if key not in row:
            continue
        try:
            value = float(row.get(key))
        except (TypeError, ValueError):
            return None
        return value if math.isfinite(value) else None
    return None


def _attach_bellwether_period_evidence(
    periods: dict[str, dict[str, Any]],
) -> dict[str, dict[str, Any]]:
    returns: dict[tuple[str, str], dict[str, float | None]] = {}
    relatives: dict[tuple[str, str], dict[str, float | None]] = {}
    for period, payload in periods.items():
        for row in payload["bellwethers"]:
            key = _group_symbol(row)
            returns.setdefault(key, {})[period] = _period_value(row, "Return %", "return_pct")
            relatives.setdefault(key, {})[period] = _period_value(
                row,
                "Relative To Group pp",
                "relative_to_group_pp",
            )
    for payload in periods.values():
        for row in payload["bellwethers"]:
            key = _group_symbol(row)
            row["period_returns_pct"] = {
                period: returns.get(key, {}).get(period) for period in GROUP_PERIODS
            }
            row["period_relative_to_group_pp"] = {
                period: relatives.get(key, {}).get(period) for period in GROUP_PERIODS
            }
    return periods


def _group_mode_payload(
    snapshots: Mapping[str, Mapping[str, Any]],
) -> dict[str, dict[str, Any]]:
    periods = {
        period: _group_period_payload(snapshots.get(period))
        for period in GROUP_PERIODS
    }
    return _attach_bellwether_period_evidence(periods)


def build_market_movers_decision_payload(
    *,
    market_snapshot: Mapping[str, Any],
    sector_snapshots: Mapping[str, Mapping[str, Any]],
    industry_snapshots: Mapping[str, Mapping[str, Any]],
    selected_research: Mapping[str, Any] | None,
) -> dict[str, Any]:
    """Assemble the JSON-only boundary consumed by the phase-4 React shell."""

    readiness = dict(market_snapshot.get("collection_readiness") or {})
    if not readiness:
        readiness = {
            "schema_version": "market_movers_collection_readiness_v1",
            "state": "UNKNOWN",
            "publish_results": False,
        }
    payload = {
        "schema_version": "market_movers_decision_payload_v1",
        "trust": readiness,
        "ranking": {
            "period": market_snapshot.get("period"),
            "ranking_mode": market_snapshot.get("ranking_mode") or "top_gainers",
            "rows": _records(market_snapshot.get("rows")),
            "views": _json_safe(market_snapshot.get("mover_views") or {}),
        },
        "group_context": {
            "sector": _group_mode_payload(sector_snapshots),
            "industry": _group_mode_payload(industry_snapshots),
        },
        "selected_research": _json_safe(selected_research) if selected_research else None,
    }
    return _json_safe(payload)


__all__ = ["build_market_movers_decision_payload"]
