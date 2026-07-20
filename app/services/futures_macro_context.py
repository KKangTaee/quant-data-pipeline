"""Build point-in-time macro and scheduled-event context for futures states."""

from __future__ import annotations

import json
import math
from collections.abc import Sequence
from datetime import datetime, time, timezone
from typing import Any
from zoneinfo import ZoneInfo

import pandas as pd


MACRO_CONTEXT_COLUMNS = (
    "cycle_risk_balance",
    "cycle_entropy",
    "activity_contribution",
    "labor_income_contribution",
    "financial_leading_contribution",
    "inflation_policy_contribution",
)
EVENT_CONTEXT_COLUMNS = (
    "event_count_5d",
    "event_count_20d",
    "has_fomc_5d",
    "has_inflation_5d",
    "has_labor_5d",
    "has_growth_20d",
)
PHASES = ("recovery", "expansion", "slowdown", "recession")
FACTOR_PREFIXES = (
    "activity",
    "labor_income",
    "financial_leading",
    "inflation_policy",
)
NEW_YORK = ZoneInfo("America/New_York")


def _json_value(value: object, fallback: object) -> object:
    if isinstance(value, (dict, list)):
        return value
    try:
        return json.loads(str(value or ""))
    except (TypeError, ValueError, json.JSONDecodeError):
        return fallback


def _cycle_values(row: dict[str, object]) -> dict[str, float]:
    probabilities = _json_value(row.get("probabilities_json"), {})
    if not isinstance(probabilities, dict):
        return {}
    values: dict[str, float] = {}
    try:
        phase_values = [max(0.0, float(probabilities[phase])) for phase in PHASES]
    except (KeyError, TypeError, ValueError):
        return {}
    total = sum(phase_values)
    if total <= 0:
        return {}
    normalized = [value / total for value in phase_values]
    values["cycle_risk_balance"] = float(
        normalized[0] + normalized[1] - normalized[2] - normalized[3]
    )
    values["cycle_entropy"] = float(
        -sum(value * math.log(value) for value in normalized if value > 0)
        / math.log(len(PHASES))
    )
    contributions = _json_value(row.get("factor_contributions_json"), [])
    contribution_values = {prefix: 0.0 for prefix in FACTOR_PREFIXES}
    contribution_seen = {prefix: False for prefix in FACTOR_PREFIXES}
    if isinstance(contributions, list):
        for item in contributions:
            if not isinstance(item, dict):
                continue
            factor = str(item.get("factor") or "").strip().lower()
            try:
                contribution = float(item.get("value"))
            except (TypeError, ValueError):
                continue
            for prefix in FACTOR_PREFIXES:
                if factor == prefix or factor.startswith(f"{prefix}_"):
                    contribution_values[prefix] += contribution
                    contribution_seen[prefix] = True
                    break
    for prefix in FACTOR_PREFIXES:
        if contribution_seen[prefix]:
            values[f"{prefix}_contribution"] = float(contribution_values[prefix])
    return values


def _timestamp_utc(value: object) -> pd.Timestamp | None:
    parsed = pd.to_datetime(value, errors="coerce", utc=True)
    if pd.isna(parsed):
        return None
    return pd.Timestamp(parsed)


def _session_known_at(session_date: pd.Timestamp) -> pd.Timestamp:
    local = datetime.combine(session_date.date(), time(18, 15), tzinfo=NEW_YORK)
    return pd.Timestamp(local.astimezone(timezone.utc))


def _event_family(event_type: object) -> str:
    normalized = str(event_type or "").strip().upper()
    if normalized == "FOMC_MEETING":
        return "fomc"
    if normalized in {"MACRO_CPI", "MACRO_PPI", "MACRO_PCE"}:
        return "inflation"
    if normalized in {"MACRO_EMPLOYMENT", "MACRO_JOLTS", "MACRO_ECI"}:
        return "labor"
    if normalized in {
        "MACRO_GDP",
        "MACRO_RETAIL_SALES",
        "MACRO_DURABLE_GOODS",
        "MACRO_HOUSING",
    }:
        return "growth"
    return "other"


def build_futures_macro_context_frame(
    session_dates: pd.DatetimeIndex,
    *,
    cycle_rows: Sequence[dict[str, object]],
    event_rows: Sequence[dict[str, object]],
) -> pd.DataFrame:
    """As-of join stored cycle replays and origin-known official schedules."""

    dates = pd.DatetimeIndex(pd.to_datetime(session_dates, errors="coerce")).dropna().normalize().sort_values().unique()
    frame = pd.DataFrame(index=pd.DatetimeIndex(dates, name="Date"))
    for column in MACRO_CONTEXT_COLUMNS:
        frame[column] = float("nan")
    for column in EVENT_CONTEXT_COLUMNS:
        frame[column] = 0.0
    if frame.empty:
        return frame

    normalized_cycles: list[tuple[pd.Timestamp, dict[str, float]]] = []
    for raw in cycle_rows:
        row = dict(raw)
        as_of = pd.to_datetime(row.get("as_of_date"), errors="coerce")
        cutoff = pd.to_datetime(row.get("data_cutoff_date"), errors="coerce")
        if pd.isna(as_of) or pd.isna(cutoff) or cutoff > as_of:
            continue
        values = _cycle_values(row)
        if values:
            normalized_cycles.append((pd.Timestamp(as_of).normalize(), values))
    normalized_cycles.sort(key=lambda item: item[0])
    for session_date in frame.index:
        eligible = [item for item in normalized_cycles if item[0] <= session_date]
        if not eligible:
            continue
        for column, value in eligible[-1][1].items():
            frame.at[session_date, column] = value

    normalized_events: list[dict[str, Any]] = []
    for raw in event_rows:
        row = dict(raw)
        event_date = pd.to_datetime(row.get("event_date"), errors="coerce")
        collected = _timestamp_utc(row.get("collected_at"))
        if pd.isna(event_date) or collected is None:
            continue
        normalized_events.append(
            {
                "event_date": pd.Timestamp(event_date).normalize(),
                "collected_at": collected,
                "family": _event_family(row.get("event_type")),
            }
        )
    for position, origin in enumerate(frame.index):
        known_at = _session_known_at(origin)
        terminals = {
            5: (
                frame.index[position + 5]
                if position + 5 < len(frame.index)
                else origin + pd.Timedelta(days=7)
            ),
            20: (
                frame.index[position + 20]
                if position + 20 < len(frame.index)
                else origin + pd.Timedelta(days=28)
            ),
        }
        eligible = [
            event
            for event in normalized_events
            if event["collected_at"] <= known_at and event["event_date"] > origin
        ]
        five = [event for event in eligible if event["event_date"] <= terminals[5]]
        twenty = [event for event in eligible if event["event_date"] <= terminals[20]]
        frame.at[origin, "event_count_5d"] = float(len(five))
        frame.at[origin, "event_count_20d"] = float(len(twenty))
        frame.at[origin, "has_fomc_5d"] = float(any(event["family"] == "fomc" for event in five))
        frame.at[origin, "has_inflation_5d"] = float(any(event["family"] == "inflation" for event in five))
        frame.at[origin, "has_labor_5d"] = float(any(event["family"] == "labor" for event in five))
        frame.at[origin, "has_growth_20d"] = float(any(event["family"] == "growth" for event in twenty))
    return frame
