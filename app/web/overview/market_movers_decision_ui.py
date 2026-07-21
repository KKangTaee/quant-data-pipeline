from __future__ import annotations

from collections.abc import Mapping, Sequence
from typing import Any


COMMAND_CONTROL_ORDER = ("coverage", "period", "mode", "top_n")
FINANCIAL_FREQUENCIES = (
    {"id": "quarterly", "label": "분기"},
    {"id": "annual", "label": "연간"},
)
FINANCIAL_FACTOR_GROUPS = (
    ("income", "손익"),
    ("profitability", "수익성"),
    ("stability", "안정성"),
)


def _mapping(value: Any) -> dict[str, Any]:
    return dict(value) if isinstance(value, Mapping) else {}


def _records(value: Any) -> list[dict[str, Any]]:
    if not isinstance(value, Sequence) or isinstance(value, (str, bytes)):
        return []
    return [dict(item) for item in value if isinstance(item, Mapping)]


def _symbol(row: Mapping[str, Any]) -> str:
    return str(row.get("Symbol") or row.get("symbol") or "").strip().upper()


def _ranking_payload(decision_payload: Mapping[str, Any]) -> dict[str, Any]:
    ranking = _mapping(decision_payload.get("ranking"))
    mode = str(ranking.get("ranking_mode") or "top_gainers")
    views = _mapping(ranking.get("views"))
    selected_view = _mapping(views.get(mode))
    rows = _records(selected_view.get("rows")) or _records(ranking.get("rows"))
    return {
        **ranking,
        "ranking_mode": mode,
        "label": str(selected_view.get("label") or mode),
        "kind": str(selected_view.get("kind") or "symbol"),
        "rows": rows,
        "sort_basis": str(selected_view.get("sort_basis") or ""),
        "empty_reason": str(selected_view.get("empty_reason") or ""),
    }


def _selected_row(rows: Sequence[Mapping[str, Any]], selected_symbol: str | None) -> dict[str, Any]:
    requested = str(selected_symbol or "").strip().upper()
    if requested:
        for row in rows:
            if _symbol(row) == requested:
                return dict(row)
    return dict(rows[0]) if rows else {}


def _factor_catalog(research: Mapping[str, Any]) -> dict[str, Any]:
    series_by_frequency = _mapping(research.get("financial_factor_series"))
    factor_ids: list[str] = []
    factor_specs: dict[str, dict[str, Any]] = {}
    memberships: dict[str, list[str]] = {group_id: [] for group_id, _ in FINANCIAL_FACTOR_GROUPS}

    for frequency in ("quarterly", "annual"):
        frequency_payload = _mapping(series_by_frequency.get(frequency))
        factors = _mapping(frequency_payload.get("factors"))
        for factor_id, raw_spec in factors.items():
            spec = _mapping(raw_spec)
            normalized_id = str(factor_id)
            if normalized_id not in factor_ids:
                factor_ids.append(normalized_id)
            factor_specs.setdefault(normalized_id, spec)
            group_id = str(spec.get("group") or "")
            if group_id in memberships and normalized_id not in memberships[group_id]:
                memberships[group_id].append(normalized_id)

    factor_groups: list[dict[str, Any]] = []
    first_available_factor: str | None = None
    first_available_frequency: str | None = None
    for group_id, group_label in FINANCIAL_FACTOR_GROUPS:
        factors: list[dict[str, Any]] = []
        for factor_id in memberships[group_id]:
            spec = factor_specs[factor_id]
            available_by_frequency: dict[str, bool] = {}
            for frequency in ("quarterly", "annual"):
                frequency_spec = _mapping(
                    _mapping(_mapping(series_by_frequency.get(frequency)).get("factors")).get(factor_id)
                )
                available = bool(_records(frequency_spec.get("points")))
                available_by_frequency[frequency] = available
                if available and first_available_factor is None:
                    first_available_factor = factor_id
                    first_available_frequency = frequency
            factors.append(
                {
                    "id": factor_id,
                    "label": str(spec.get("label") or factor_id),
                    "unit": str(spec.get("unit") or "number"),
                    "available_by_frequency": available_by_frequency,
                }
            )
        factor_groups.append({"id": group_id, "label": group_label, "factors": factors})

    return {
        "frequencies": [dict(item) for item in FINANCIAL_FREQUENCIES],
        "factor_groups": factor_groups,
        "default_frequency": first_available_frequency or "quarterly",
        "default_factor": first_available_factor,
    }


def build_market_movers_decision_shell_payload(
    *,
    decision_payload: Mapping[str, Any],
    command: Mapping[str, Any],
    command_controls: Sequence[Mapping[str, Any]],
    actions: Sequence[Mapping[str, Any]],
    selected_symbol: str | None,
    action_note: str = "",
    breadth_selection: Mapping[str, Any] | None = None,
    timing: Mapping[str, Any] | None = None,
) -> dict[str, Any]:
    """Build the presentation-only contract for the approved decision workbench."""

    ranking = _ranking_payload(decision_payload)
    selected_row = _selected_row(ranking["rows"], selected_symbol)
    selected = _symbol(selected_row)
    research = _mapping(decision_payload.get("selected_research"))
    if str(research.get("symbol") or "").strip().upper() != selected:
        research = {}

    controls_by_id = {
        str(item.get("id") or ""): dict(item)
        for item in command_controls
        if isinstance(item, Mapping)
    }
    controls = [controls_by_id[item_id] for item_id in COMMAND_CONTROL_ORDER if item_id in controls_by_id]
    return {
        "schema_version": "market_movers_decision_workbench_v1",
        "component": "MarketMoversDecisionWorkbench",
        "command_line": {
            "values": dict(command),
            "controls": controls,
        },
        "trust": _mapping(decision_payload.get("trust")),
        "timing": {
            "current_time": str(_mapping(timing).get("current_time") or "-"),
            "market_date": str(_mapping(timing).get("market_date") or "-"),
            "data_as_of": str(_mapping(timing).get("data_as_of") or "-"),
            "last_refreshed_at": str(_mapping(timing).get("last_refreshed_at") or "수동 갱신 기록 없음"),
        },
        "ranking": ranking,
        "group_context": _mapping(decision_payload.get("group_context")),
        "breadth_selection": {
            "group_by": str(_mapping(breadth_selection).get("group_by") or "sector"),
            "period": str(_mapping(breadth_selection).get("period") or "daily"),
        },
        "selection": {
            "symbol": selected,
            "row": selected_row,
            "research": research or None,
            "financial_controls": _factor_catalog(research),
        },
        "actions": [dict(item) for item in actions if isinstance(item, Mapping)],
        "action_note": str(action_note or ""),
    }


__all__ = ["build_market_movers_decision_shell_payload"]
