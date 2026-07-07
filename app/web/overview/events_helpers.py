from __future__ import annotations

import calendar
from dataclasses import dataclass
from datetime import datetime
from html import escape
from typing import Any

import altair as alt
import pandas as pd
import streamlit as st

from app.services.overview.events import build_events_workbench_payload
from app.jobs.overview_actions import (
    record_overview_action_result,
    run_overview_earnings_calendar,
    run_overview_fomc_calendar,
    run_overview_macro_calendar,
    run_overview_market_structure_calendar,
)
from app.web.overview.events_react_component import (
    events_react_component_available,
    render_events_react_workbench,
)
from app.web.overview.components.events import (
    render_event_agenda_sections,
    render_event_source_lane,
    render_event_warning_strip,
    render_events_summary_strip,
    render_macro_week_lane,
)
from app.web.overview.session_helpers import _snapshot_value
from app.web.overview_dashboard_helpers import (
    load_overview_macro_week_lane,
    load_overview_market_events_snapshot,
)
from app.web.overview.components.common import (
    OVERVIEW_COLOR_BORDER,
    OVERVIEW_COLOR_NEUTRAL,
    OVERVIEW_COLOR_POSITIVE,
    OVERVIEW_COLOR_PRIMARY,
    OVERVIEW_COLOR_PURPLE,
    OVERVIEW_COLOR_SOFT,
    OVERVIEW_COLOR_SURFACE,
    OVERVIEW_COLOR_SURFACE_ALT,
    OVERVIEW_COLOR_SURFACE_SUBTLE,
    OVERVIEW_COLOR_TEXT,
    OVERVIEW_COLOR_TEXT_INVERSE,
    OVERVIEW_COLOR_TEXT_MUTED,
    OVERVIEW_COLOR_TEXT_SUBTLE,
    OVERVIEW_COLOR_WARNING,
    render_overview_toolbar_label,
)


EVENT_TYPE_LABELS = {
    "ALL": "All",
    "FOMC_MEETING": "FOMC",
    "EARNINGS": "Earnings",
    "MACRO": "Macro",
}


@dataclass(frozen=True)
class EventSnapshotContext:
    event_filter: str
    selected_event_type: str | None
    snapshot: dict[str, Any]
    coverage: dict[str, Any]
    rows: Any
    calendar_rows: Any


def _option_index(options: list[str], current: Any, *, default: int = 0) -> int:
    try:
        return options.index(str(current))
    except ValueError:
        return default


def _event_filter_label(value: str) -> str:
    return EVENT_TYPE_LABELS.get(value, value.replace("_", " ").title())


def _store_overview_job_result(result_key: str, result: dict[str, Any]) -> None:
    st.session_state[result_key] = result
    try:
        record_overview_action_result(result)
    except Exception as exc:  # pragma: no cover - UI resilience only
        st.session_state["overview_run_history_warning"] = f"Run history write failed: {exc}"


def render_events_header() -> None:
    st.markdown("### Events")


def render_event_refresh_toolbar() -> str:
    render_overview_toolbar_label("일정 타입")
    controls = st.columns([0.95, 2.9, 0.9], gap="small", vertical_alignment="bottom")
    event_options = list(EVENT_TYPE_LABELS.keys())
    event_filter = str(
        controls[0].selectbox(
            "Type",
            event_options,
            index=_option_index(
                event_options,
                st.session_state.get("overview_events_type_filter", "ALL"),
            ),
            format_func=_event_filter_label,
            key="overview_events_type_filter",
        )
    )
    with controls[2].popover(
        "Refresh",
        icon=":material/sync:",
        use_container_width=True,
    ):
        if st.button("FOMC", key="overview_events_refresh_fomc", use_container_width=True):
            current_year = datetime.now().year
            with st.spinner("Collecting FOMC calendar from the official Fed page..."):
                _store_overview_job_result(
                    "overview_fomc_calendar_result",
                    run_overview_fomc_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
        if st.button(
            "Earnings",
            key="overview_events_refresh_earnings",
            use_container_width=True,
            help="Collects upcoming earnings for the latest S&P 500 market movers snapshot.",
        ):
            with st.spinner("Collecting earnings dates from yfinance calendar for latest S&P 500 movers..."):
                _store_overview_job_result(
                    "overview_earnings_calendar_result",
                    run_overview_earnings_calendar(),
                )
            st.rerun()
        if st.button(
            "Macro",
            key="overview_events_refresh_macro",
            use_container_width=True,
            help="Collects official macro release, PMI, Treasury auction, and related calendar dates.",
        ):
            current_year = datetime.now().year
            with st.spinner("Collecting official macro and Treasury calendars..."):
                _store_overview_job_result(
                    "overview_macro_calendar_result",
                    run_overview_macro_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
        if st.button(
            "Market Structure",
            key="overview_events_refresh_market_structure",
            use_container_width=True,
            help="Collects official market holiday, early close, options expiration, and index event dates.",
        ):
            current_year = datetime.now().year
            with st.spinner("Collecting official market structure calendars..."):
                _store_overview_job_result(
                    "overview_market_structure_calendar_result",
                    run_overview_market_structure_calendar(years=(current_year, current_year + 1)),
                )
            st.rerun()
    return event_filter


def _event_type_label(value: Any) -> str:
    labels = {
        "FOMC_MEETING": "FOMC",
        "EARNINGS": "Earnings",
        "MACRO": "Macro",
        "MACRO_CPI": "CPI",
        "MACRO_PPI": "PPI",
        "MACRO_EMPLOYMENT": "Jobs",
        "MACRO_GDP": "GDP",
        "MACRO_JOLTS": "JOLTS",
        "MACRO_ECI": "ECI",
        "MACRO_PCE": "PCE",
        "MACRO_RETAIL_SALES": "Retail Sales",
        "MACRO_DURABLE_GOODS": "Durable Goods",
        "MACRO_HOUSING": "Housing",
        "MACRO_CONSTRUCTION_SPENDING": "Construction Spending",
        "MACRO_TRADE": "Trade",
        "MACRO_ISM_MANUFACTURING_PMI": "ISM Mfg PMI",
        "MACRO_ISM_SERVICES_PMI": "ISM Services PMI",
        "TREASURY_AUCTION": "Treasury Auction",
        "MARKET_HOLIDAY": "Market Holiday",
        "EARLY_CLOSE": "Early Close",
        "OPTIONS_EXPIRATION": "Options Expiration",
        "RUSSELL_RECONSTITUTION": "Russell Reconstitution",
        "INDEX_REBALANCE": "Index Rebalance",
        "SP500_REBALANCE": "S&P Rebalance",
        "NASDAQ100_RECONSTITUTION": "Nasdaq-100 Reconstitution",
    }
    return labels.get(str(value or ""), str(value or "-").replace("_", " ").title())


def _event_importance_from_type(value: Any) -> str:
    event_type = str(value or "").upper()
    if (
        event_type == "FOMC_MEETING"
        or event_type == "MACRO"
        or event_type.startswith("MACRO_")
        or event_type.startswith("TREASURY_")
    ):
        return "High"
    if event_type == "EARNINGS":
        return "Medium"
    if event_type in {
        "MARKET_HOLIDAY",
        "EARLY_CLOSE",
        "OPTIONS_EXPIRATION",
        "RUSSELL_RECONSTITUTION",
        "INDEX_REBALANCE",
        "SP500_REBALANCE",
        "NASDAQ100_RECONSTITUTION",
    }:
        return "Medium"
    return "Low"


def _event_focus_from_row(row: pd.Series) -> str:
    quality_action = str(row.get("Quality Action") or "")
    if quality_action and quality_action != "No action":
        return "Needs Review"
    days_until = row.get("Days Until")
    if pd.isna(days_until):
        return "Unknown"
    day_number = int(days_until)
    if day_number < 0:
        return "Past"
    if day_number == 0:
        return "Today"
    if day_number <= 7:
        return "This Week"
    if day_number <= 30:
        return "Next 30D"
    return "Later"


def _prepare_event_calendar_frame(rows: pd.DataFrame) -> pd.DataFrame:
    out = rows.copy()
    out["Date Parsed"] = pd.to_datetime(out.get("Date"), errors="coerce")
    today = pd.Timestamp(datetime.now().date())
    calculated_days = (out["Date Parsed"] - today).dt.days
    if "Days Until" in out:
        out["Days Until"] = pd.to_numeric(out["Days Until"], errors="coerce")
        out["Days Until"] = out["Days Until"].where(out["Days Until"].notna(), calculated_days)
    else:
        out["Days Until"] = calculated_days
    out["Month"] = out["Date Parsed"].dt.strftime("%Y-%m")
    out["Week"] = out["Date Parsed"].dt.to_period("W").astype(str)
    out["Type Label"] = out.get("Type", pd.Series(dtype=str)).map(_event_type_label)
    if "Importance" not in out:
        out["Importance"] = out.get("Type", pd.Series(dtype=str)).map(_event_importance_from_type)
    else:
        fallback_importance = out.get("Type", pd.Series(dtype=str)).map(_event_importance_from_type)
        out["Importance"] = out["Importance"].where(out["Importance"].notna() & (out["Importance"] != ""), fallback_importance)
    if "Focus" not in out:
        out["Focus"] = out.apply(_event_focus_from_row, axis=1)
    else:
        fallback_focus = out.apply(_event_focus_from_row, axis=1)
        out["Focus"] = out["Focus"].where(out["Focus"].notna() & (out["Focus"] != ""), fallback_focus)
    out["Symbol Label"] = out.get("Symbol", pd.Series(dtype=str)).replace({"-": ""})
    out["Summary"] = out.apply(
        lambda row: f"{row.get('Type Label')}: {row.get('Symbol Label') or row.get('Title') or '-'}",
        axis=1,
    )
    return out


def load_event_snapshot_context(event_filter: str) -> EventSnapshotContext:
    selected_event_type = None if event_filter == "ALL" else event_filter
    snapshot = load_overview_market_events_snapshot(
        event_type=selected_event_type,
        horizon_days=540,
    )
    coverage = dict(snapshot.get("coverage") or {})
    rows = snapshot.get("rows")
    calendar_rows = (
        _prepare_event_calendar_frame(rows)
        if isinstance(rows, pd.DataFrame)
        else pd.DataFrame()
    )
    return EventSnapshotContext(
        event_filter=event_filter,
        selected_event_type=selected_event_type,
        snapshot=snapshot,
        coverage=coverage,
        rows=rows,
        calendar_rows=calendar_rows,
    )


def _render_market_job_result(result_key: str) -> None:
    result = st.session_state.get(result_key)
    if not isinstance(result, dict):
        return
    status = result.get("status")
    message = result.get("message") or ""
    if status == "success":
        st.success(message)
    elif status == "partial_success":
        st.warning(message)
    else:
        st.error(message)
    details = result.get("details") or {}
    if details:
        source = details.get("source") or "-"
        method = details.get("method") or details.get("method_requested") or "-"
        duration = result.get("duration_sec")
        st.caption(
            "Rows: "
            f"{result.get('rows_written') or 0}, "
            f"Events: {details.get('events_found') or '-'}, "
            f"Source: {source}, Method: {method}, Duration: {_snapshot_value(duration)}s"
        )


def _has_event_refresh_result() -> bool:
    return any(
        isinstance(st.session_state.get(key), dict)
        for key in [
            "overview_fomc_calendar_result",
            "overview_earnings_calendar_result",
            "overview_macro_calendar_result",
            "overview_market_structure_calendar_result",
        ]
    )


def render_event_refresh_results() -> None:
    if not _has_event_refresh_result():
        return
    with st.expander("Refresh Results", expanded=False):
        _render_market_job_result("overview_fomc_calendar_result")
        _render_market_job_result("overview_earnings_calendar_result")
        _render_market_job_result("overview_macro_calendar_result")
        _render_market_job_result("overview_market_structure_calendar_result")


def _events_react_event_payload(value: Any) -> dict[str, Any] | None:
    if not isinstance(value, dict):
        return None
    event = value.get("event")
    if isinstance(event, dict):
        return event
    if value.get("id") or value.get("action_id"):
        return value
    return None


def _events_react_event_token(event: dict[str, Any]) -> str:
    action_id = str(event.get("id") or event.get("action_id") or "").strip()
    nonce = str(event.get("nonce") or event.get("ts") or "").strip()
    return f"{action_id}:{nonce}" if nonce else action_id


def _handle_events_react_event(event: dict[str, Any], context: EventSnapshotContext) -> None:
    del context
    action_id = str(event.get("id") or event.get("action_id") or "").strip()
    if not action_id:
        return
    event_token = _events_react_event_token(event)
    if st.session_state.get("overview_events_react_event_token") == event_token:
        return
    st.session_state["overview_events_react_event_token"] = event_token
    current_year = datetime.now().year
    if action_id == "reload":
        st.rerun()
    if action_id == "refresh_fomc":
        with st.spinner("Collecting FOMC calendar from the official Fed page..."):
            _store_overview_job_result(
                "overview_fomc_calendar_result",
                run_overview_fomc_calendar(years=(current_year, current_year + 1)),
            )
        st.rerun()
    if action_id == "refresh_macro":
        with st.spinner("Collecting official macro and Treasury calendars..."):
            _store_overview_job_result(
                "overview_macro_calendar_result",
                run_overview_macro_calendar(years=(current_year, current_year + 1)),
            )
        st.rerun()
    if action_id == "refresh_market_structure":
        with st.spinner("Collecting official market structure calendars..."):
            _store_overview_job_result(
                "overview_market_structure_calendar_result",
                run_overview_market_structure_calendar(years=(current_year, current_year + 1)),
            )
        st.rerun()
    if action_id == "refresh_earnings":
        with st.spinner("Collecting earnings dates from yfinance calendar for latest S&P 500 movers..."):
            _store_overview_job_result(
                "overview_earnings_calendar_result",
                run_overview_earnings_calendar(),
            )
        st.rerun()


def render_events_react_workbench_section(context: EventSnapshotContext) -> bool:
    if not events_react_component_available():
        return False
    payload = build_events_workbench_payload(context.snapshot)
    react_event = render_events_react_workbench(
        payload,
        key=f"overview_events_workbench_{context.event_filter}",
    )
    event_payload = _events_react_event_payload(react_event)
    if event_payload:
        st.session_state["overview_events_react_event"] = event_payload
        _handle_events_react_event(event_payload, context)
    return True


def _event_tone(value: Any) -> str:
    text = str(value or "").lower()
    if text in {"fomc", "fomc_meeting"}:
        return "fomc"
    if text in {"macro", "cpi", "ppi", "jobs", "gdp"} or text.startswith("macro"):
        return "macro"
    if text == "earnings":
        return "earnings"
    if text in {"high", "needs review", "not confirmed", "conflict", "stale estimate"}:
        return "review"
    if text in {"official", "cross-checked", "no action"}:
        return "official"
    if text in {"estimate only", "provider estimate", "medium", "current estimate"}:
        return "estimate"
    return "neutral"


def _event_days_text(value: Any) -> str:
    if value in (None, "") or pd.isna(value):
        return "date pending"
    day_number = int(value)
    if day_number < 0:
        return f"{abs(day_number)}d ago"
    if day_number == 0:
        return "today"
    if day_number == 1:
        return "tomorrow"
    return f"in {day_number}d"


def _event_main_title(row: pd.Series) -> str:
    symbol = str(row.get("Symbol Label") or row.get("Symbol") or "").strip()
    if symbol == "-":
        symbol = ""
    title = str(row.get("Title") or "-")
    return f"{symbol} · {title}" if symbol else title


def _event_subtitle(row: pd.Series) -> str:
    parts = [
        str(row.get("Type Label") or row.get("Type") or "-"),
        str(row.get("Source Type") or "-"),
        str(row.get("Freshness") or "-"),
    ]
    action = str(row.get("Quality Action") or "")
    if action and action != "No action":
        parts.append(action)
    return " · ".join(part for part in parts if part and part != "-")


def _event_agenda_item(row: pd.Series) -> dict[str, Any]:
    return {
        "date": str(row.get("Date") or "-"),
        "countdown": _event_days_text(row.get("Days Until")),
        "title": _event_main_title(row),
        "subtitle": _event_subtitle(row),
        "badges": [
            {"label": row.get("Type Label") or row.get("Type") or "-", "tone": _event_tone(row.get("Type Label"))},
            {"label": row.get("Importance") or "-", "tone": _event_tone(row.get("Importance"))},
            {"label": row.get("Validation") or "-", "tone": _event_tone(row.get("Validation"))},
            {"label": row.get("Focus") or "-", "tone": _event_tone(row.get("Focus"))},
        ],
    }


def _event_agenda_sections(rows: pd.DataFrame) -> list[dict[str, Any]]:
    if rows.empty:
        return []
    focus_rows = rows.copy()
    focus_rows["Days Until"] = pd.to_numeric(focus_rows.get("Days Until"), errors="coerce")
    recent_major_rows = focus_rows[
        (focus_rows["Days Until"] < 0)
        & (focus_rows["Days Until"] >= -7)
        & (focus_rows.get("Importance") == "High")
    ].sort_values(
        ["Date Parsed", "Type Label", "Symbol"],
        ascending=[False, True, True],
    )
    future_rows = focus_rows[focus_rows["Days Until"].isna() | (focus_rows["Days Until"] >= 0)].sort_values(
        ["Date Parsed", "Importance", "Type Label", "Symbol"],
        ascending=[True, True, True, True],
    )
    sections: list[dict[str, Any]] = []
    if not recent_major_rows.empty:
        recent_rows = recent_major_rows.head(8)
        sections.append(
            {
                "title": "Recent Major",
                "meta": f"{len(recent_rows)} shown",
                "rows": [_event_agenda_item(row) for _, row in recent_rows.iterrows()],
            }
        )
    section_specs = [
        ("Today", future_rows["Days Until"] == 0, 8),
        ("This Week", (future_rows["Days Until"] > 0) & (future_rows["Days Until"] <= 7), 10),
        ("Next 30D", (future_rows["Days Until"] > 7) & (future_rows["Days Until"] <= 30), 12),
        ("Later", future_rows["Days Until"] > 30, 12),
    ]
    for title, mask, limit in section_specs:
        section_rows = future_rows[mask].head(limit)
        if section_rows.empty:
            continue
        sections.append(
            {
                "title": title,
                "meta": f"{len(section_rows)} shown",
                "rows": [_event_agenda_item(row) for _, row in section_rows.iterrows()],
            }
        )
    unknown_rows = future_rows[future_rows["Days Until"].isna()].head(6)
    if not unknown_rows.empty:
        sections.append(
            {
                "title": "Date Pending",
                "meta": f"{len(unknown_rows)} shown",
                "rows": [_event_agenda_item(row) for _, row in unknown_rows.iterrows()],
            }
        )
    return sections


def _event_quality_rows(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    return rows[
        (rows.get("Focus") == "Needs Review")
        | ((rows.get("Quality Action") != "No action") & rows.get("Quality Action").notna())
        | (rows.get("Validation").isin(["Estimate only", "Not confirmed", "Conflict"]))
        | (rows.get("Freshness").isin(["Stale estimate", "Stale source"]))
    ].sort_values(["Date Parsed", "Type Label", "Symbol"])


def _event_quality_sections(rows: pd.DataFrame) -> list[dict[str, Any]]:
    quality_rows = _event_quality_rows(rows)
    if quality_rows.empty:
        return []
    review_mask = (quality_rows.get("Focus") == "Needs Review") | (
        (quality_rows.get("Quality Action") != "No action") & quality_rows.get("Quality Action").notna()
    )
    estimate_mask = quality_rows.get("Validation").isin(["Estimate only", "Not confirmed", "Conflict"])
    freshness_mask = quality_rows.get("Freshness").isin(["Stale estimate", "Stale source"])
    section_specs = [
        ("Action Required", quality_rows[review_mask].head(18)),
        ("Estimate Validation", quality_rows[estimate_mask].head(18)),
        ("Freshness", quality_rows[freshness_mask].head(18)),
    ]
    sections: list[dict[str, Any]] = []
    seen_keys: set[tuple[Any, Any, Any]] = set()
    for title, section_rows in section_specs:
        if section_rows.empty:
            continue
        deduped_rows = []
        for _, row in section_rows.iterrows():
            key = (row.get("Date"), row.get("Type"), row.get("Symbol"), row.get("Title"))
            if key in seen_keys:
                continue
            seen_keys.add(key)
            deduped_rows.append(_event_agenda_item(row))
        if deduped_rows:
            sections.append({"title": title, "meta": f"{len(deduped_rows)} shown", "rows": deduped_rows})
    return sections


def _event_summary_items(rows: pd.DataFrame, coverage: dict[str, Any], *, event_type: Any) -> list[dict[str, Any]]:
    if rows.empty:
        next_value = _snapshot_value(coverage.get("next_event_date"))
        next_detail = f"filter: {event_type or 'All'}"
    else:
        rows_with_days = rows.copy()
        rows_with_days["Days Until"] = pd.to_numeric(rows_with_days.get("Days Until"), errors="coerce")
        upcoming = rows_with_days[rows_with_days["Days Until"].isna() | (rows_with_days["Days Until"] >= 0)].sort_values(
            ["Date Parsed", "Type Label", "Symbol"],
            ascending=[True, True, True],
        )
        next_row = upcoming.iloc[0] if not upcoming.empty else rows_with_days.sort_values("Date Parsed").iloc[0]
        next_value = str(next_row.get("Date") or _snapshot_value(coverage.get("next_event_date")))
        next_detail = f"{_event_days_text(next_row.get('Days Until'))} · {_event_main_title(next_row)}"
    needs_review_count = int(len(_event_quality_rows(rows))) if not rows.empty else int(coverage.get("needs_review_count") or 0)
    return [
        {"label": "Next Event", "value": next_value, "detail": next_detail, "tone": "primary"},
        {
            "label": "This Week",
            "value": coverage.get("this_week_count") or 0,
            "detail": "today through 7D",
            "tone": "positive",
        },
        {
            "label": "Next 30D",
            "value": coverage.get("next_30d_count") or 0,
            "detail": f"stored rows: {coverage.get('event_count') or 0}",
            "tone": "neutral",
        },
        {
            "label": "Needs Review",
            "value": needs_review_count,
            "detail": f"latest: {_snapshot_value(coverage.get('latest_collected_at'))}",
            "tone": "danger" if needs_review_count else "positive",
        },
    ]


def _latest_collected_at(rows: pd.DataFrame) -> str:
    if rows.empty or "Collected At" not in rows:
        return "-"
    values = rows["Collected At"].replace("-", pd.NA).dropna().astype(str)
    return values.max() if not values.empty else "-"


def _compact_event_timestamp(value: str) -> str:
    if len(value) >= 16 and value[:4].isdigit():
        return value[5:16]
    return value


def _event_source_items(rows: pd.DataFrame, *, event_filter: str) -> list[dict[str, Any]]:
    source_specs = [
        ("FOMC", "FOMC_MEETING", lambda frame: frame["Type"].astype(str).str.upper() == "FOMC_MEETING", "fomc"),
        ("Earnings", "EARNINGS", lambda frame: frame["Type"].astype(str).str.upper() == "EARNINGS", "earnings"),
        ("Macro", "MACRO", lambda frame: frame["Type"].astype(str).str.upper().str.startswith("MACRO"), "macro"),
    ]
    selected_filter = str(event_filter or "ALL").upper()
    items: list[dict[str, Any]] = []
    for title, source_filter, mask_fn, base_tone in source_specs:
        if selected_filter != "ALL" and source_filter != selected_filter:
            continue
        subset = rows[mask_fn(rows)] if not rows.empty and "Type" in rows else pd.DataFrame()
        review_count = len(_event_quality_rows(subset)) if not subset.empty else 0
        if subset.empty:
            status = "Missing"
            tone = "danger"
        elif review_count:
            status = "Review"
            tone = "review"
        else:
            status = "OK"
            tone = base_tone
        latest = _latest_collected_at(subset)
        items.append(
            {
                "title": title,
                "status": status,
                "detail": f"{len(subset)} rows · latest {latest} · review {review_count}",
                "rows": len(subset),
                "latest": _compact_event_timestamp(latest),
                "review_count": review_count,
                "tone": tone,
            }
        )
    return items


def render_events_overview_lanes(context: EventSnapshotContext) -> None:
    render_events_summary_strip(
        _event_summary_items(
            context.calendar_rows,
            context.coverage,
            event_type=context.snapshot.get("event_type"),
        )
    )
    render_event_source_lane(
        _event_source_items(context.calendar_rows, event_filter=context.event_filter)
    )
    render_event_warning_strip(list(context.snapshot.get("warnings") or []))
    render_macro_week_lane(load_overview_macro_week_lane(context.snapshot))


def has_event_rows(context: EventSnapshotContext) -> bool:
    return isinstance(context.rows, pd.DataFrame) and not context.rows.empty


def render_events_empty_state() -> None:
    st.info(
        "Stored market event rows are not available for the selected filter. Run the matching refresh here or from Ingestion."
    )


def filter_event_calendar_rows(context: EventSnapshotContext) -> Any:
    return _filter_event_rows_for_calendar(context.calendar_rows)


def _filter_event_rows_for_calendar(rows: pd.DataFrame) -> pd.DataFrame:
    if rows.empty:
        return rows
    render_overview_toolbar_label("보기 조건")
    filter_cols = st.columns([1, 1, 1, 1], gap="small")
    source_options = ["All"] + sorted(
        value for value in rows.get("Source Type", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    validation_options = ["All"] + sorted(
        value for value in rows.get("Validation", pd.Series(dtype=str)).dropna().unique().tolist() if value != "-"
    )
    importance_values = rows.get("Importance", pd.Series(dtype=str)).dropna().unique().tolist()
    importance_options = ["All"] + [
        value for value in ["High", "Medium", "Low"] if value in importance_values
    ]
    window = str(
        filter_cols[0].selectbox(
            "Window",
            ["30D", "90D", "All"],
            index=_option_index(
                ["30D", "90D", "All"],
                st.session_state.get("overview_events_window_filter", "90D"),
                default=1,
            ),
            key="overview_events_window_filter",
        )
    )
    source_filter = str(
        filter_cols[1].selectbox(
            "Source Type",
            source_options,
            index=0,
            key="overview_events_source_filter",
        )
    )
    validation_filter = str(
        filter_cols[2].selectbox(
            "Validation",
            validation_options,
            index=0,
            key="overview_events_validation_filter",
        )
    )
    importance_filter = str(
        filter_cols[3].selectbox(
            "Importance",
            importance_options,
            index=0,
            key="overview_events_importance_filter",
        )
    )

    filtered = rows.copy()
    if window != "All":
        days = 30 if window == "30D" else 90
        filtered = filtered[(filtered["Days Until"].isna()) | ((filtered["Days Until"] >= 0) & (filtered["Days Until"] <= days))]
    if source_filter != "All" and "Source Type" in filtered:
        filtered = filtered[filtered["Source Type"] == source_filter]
    if validation_filter != "All" and "Validation" in filtered:
        filtered = filtered[filtered["Validation"] == validation_filter]
    if importance_filter != "All" and "Importance" in filtered:
        filtered = filtered[filtered["Importance"] == importance_filter]
    return filtered


def _build_event_calendar_chart(rows: pd.DataFrame) -> alt.Chart:
    if rows.empty:
        chart_rows = pd.DataFrame(
            [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Type Label": "No Data", "Count": 0}]
        )
    else:
        valid_rows = rows.dropna(subset=["Date Parsed"])
        if valid_rows.empty:
            chart_rows = pd.DataFrame(
                [{"Date Parsed": pd.Timestamp(datetime.now().date()), "Type Label": "No Data", "Count": 0}]
            )
        else:
            chart_rows = (
                valid_rows
                .groupby(["Date Parsed", "Type Label"], as_index=False)
                .size()
                .rename(columns={"size": "Count"})
            )
    date_min = chart_rows["Date Parsed"].min()
    date_max = chart_rows["Date Parsed"].max()
    if pd.isna(date_min) or pd.isna(date_max):
        date_min = pd.Timestamp(datetime.now().date())
        date_max = date_min + pd.Timedelta(days=1)
    elif date_min == date_max:
        date_max = date_min + pd.Timedelta(days=1)
    max_count = max(1, int(chart_rows.groupby("Date Parsed")["Count"].sum().max() or 0))
    return (
        alt.Chart(chart_rows)
        .mark_bar(cornerRadiusTopLeft=2, cornerRadiusTopRight=2)
        .encode(
            x=alt.X(
                "Date Parsed:T",
                title=None,
                axis=alt.Axis(format="%b %d", labelAngle=-35),
                scale=alt.Scale(domain=[date_min, date_max]),
            ),
            y=alt.Y("Count:Q", title="Events", stack="zero", scale=alt.Scale(domain=[0, max_count])),
            color=alt.Color(
                "Type Label:N",
                title=None,
                legend=alt.Legend(orient="bottom"),
                scale=alt.Scale(
                    range=[
                        OVERVIEW_COLOR_PRIMARY,
                        OVERVIEW_COLOR_POSITIVE,
                        OVERVIEW_COLOR_WARNING,
                        OVERVIEW_COLOR_PURPLE,
                        OVERVIEW_COLOR_NEUTRAL,
                        OVERVIEW_COLOR_SOFT,
                    ]
                ),
            ),
            tooltip=["Date Parsed:T", "Type Label:N", "Count:Q"],
        )
        .properties(height=240)
    )


def _event_month_options(rows: pd.DataFrame) -> list[str]:
    if rows.empty or "Month" not in rows:
        return []
    return sorted(value for value in rows["Month"].dropna().astype(str).unique().tolist() if value)


def _default_event_month_index(month_options: list[str]) -> int:
    if not month_options:
        return 0
    current_month = datetime.now().strftime("%Y-%m")
    if current_month in month_options:
        return month_options.index(current_month)
    future_months = [month for month in month_options if month >= current_month]
    if future_months:
        return month_options.index(future_months[0])
    return 0


def _event_month_label(month_value: str) -> str:
    try:
        month_date = pd.Timestamp(f"{month_value}-01")
    except ValueError:
        return month_value
    if pd.isna(month_date):
        return month_value
    return month_date.strftime("%B %Y")


def _event_calendar_tone_class(row: pd.Series) -> str:
    event_type = str(row.get("Type") or "").upper()
    type_label = str(row.get("Type Label") or "").lower()
    if event_type == "FOMC_MEETING" or type_label == "fomc":
        return "fomc"
    if event_type == "EARNINGS" or type_label == "earnings":
        return "earnings"
    if event_type == "MACRO" or event_type.startswith("MACRO_") or type_label in {"cpi", "ppi", "jobs", "gdp", "macro"}:
        return "macro"
    return "other"


def _event_calendar_item_html(row: pd.Series) -> str:
    type_label = str(row.get("Type Label") or row.get("Type") or "-")
    symbol = str(row.get("Symbol Label") or row.get("Symbol") or "").strip()
    if symbol == "-":
        symbol = ""
    title = str(row.get("Title") or "-")
    importance = str(row.get("Importance") or "Low").lower()
    tone = _event_calendar_tone_class(row)
    detail = symbol or title
    full_text = f"{type_label}: {symbol or title}"
    return (
        f'<div class="event-calendar-item event-calendar-{tone} '
        f'event-calendar-importance-{escape(importance)}" title="{escape(full_text)}">'
        f'<span class="event-calendar-type event-calendar-type-{tone}">{escape(type_label)}</span>'
        f'<span class="event-calendar-text">{escape(detail)}</span>'
        "</div>"
    )


def _event_calendar_legend_html(rows: pd.DataFrame) -> str:
    counts = {"fomc": 0, "earnings": 0, "macro": 0, "other": 0}
    if not rows.empty:
        for _, row in rows.iterrows():
            counts[_event_calendar_tone_class(row)] += 1
    labels = [
        ("FOMC", "fomc"),
        ("Earnings", "earnings"),
        ("Macro", "macro"),
        ("Other", "other"),
    ]
    return "".join(
        '<span class="event-calendar-legend-item">'
        f'<span class="event-calendar-legend-dot event-calendar-legend-{tone}"></span>'
        f"{escape(label)} {counts[tone]}"
        "</span>"
        for label, tone in labels
        if counts[tone] or tone != "other"
    )


def _render_event_month_grid(rows: pd.DataFrame) -> None:
    valid_rows = rows.dropna(subset=["Date Parsed"]) if "Date Parsed" in rows else pd.DataFrame()
    month_options = _event_month_options(valid_rows)
    if not month_options:
        st.info("No dated event rows match the selected calendar filters.")
        return

    selected_month = str(
        st.selectbox(
            "Month",
            month_options,
            index=_default_event_month_index(month_options),
            format_func=_event_month_label,
            key="overview_events_calendar_month",
        )
    )
    month_start = pd.Timestamp(f"{selected_month}-01")
    if pd.isna(month_start):
        st.info("No dated event rows match the selected calendar filters.")
        return

    month_rows = valid_rows[valid_rows["Month"] == selected_month].copy()
    month_rows["Date Key"] = month_rows["Date Parsed"].dt.strftime("%Y-%m-%d")
    importance_rank = {"High": 0, "Medium": 1, "Low": 2}
    month_rows["Importance Rank"] = month_rows.get("Importance", pd.Series(dtype=str)).map(importance_rank).fillna(3)
    grouped_rows = {
        date_key: day_rows.sort_values(["Importance Rank", "Type Label", "Symbol"]).reset_index(drop=True)
        for date_key, day_rows in month_rows.groupby("Date Key", sort=True)
    }

    today_value = datetime.now().date()
    calendar_weeks = calendar.Calendar(firstweekday=0).monthdatescalendar(int(month_start.year), int(month_start.month))
    weekday_html = "".join(f'<div class="event-calendar-weekday">{label}</div>' for label in ["Mon", "Tue", "Wed", "Thu", "Fri", "Sat", "Sun"])
    day_cells: list[str] = []
    for week in calendar_weeks:
        for day_value in week:
            date_key = day_value.isoformat()
            day_rows = grouped_rows.get(date_key, pd.DataFrame())
            muted_class = " event-calendar-muted" if day_value.month != int(month_start.month) else ""
            today_class = " event-calendar-today" if day_value == today_value else ""
            event_class = " event-calendar-has-events" if not day_rows.empty else ""
            high_class = (
                " event-calendar-has-high"
                if not day_rows.empty and (day_rows.get("Importance", pd.Series(dtype=str)) == "High").any()
                else ""
            )
            visible_rows = day_rows.head(3) if not day_rows.empty else pd.DataFrame()
            event_html = "".join(_event_calendar_item_html(row) for _, row in visible_rows.iterrows())
            extra_count = max(0, len(day_rows) - len(visible_rows))
            if extra_count:
                event_html += f'<div class="event-calendar-more">+{extra_count} more</div>'
            count_html = f'<span class="event-calendar-count">{len(day_rows)}</span>' if not day_rows.empty else ""
            day_cells.append(
                f'<div class="event-calendar-day{muted_class}{today_class}{event_class}{high_class}">'
                '<div class="event-calendar-day-head">'
                f'<div class="event-calendar-date">{day_value.day}</div>'
                f"{count_html}"
                "</div>"
                f'<div class="event-calendar-items">{event_html}</div>'
                "</div>"
            )

    event_count = len(month_rows)
    high_impact_count = int((month_rows.get("Importance", pd.Series(dtype=str)) == "High").sum())
    legend_html = _event_calendar_legend_html(month_rows)
    month_label = _event_month_label(selected_month)
    st.markdown(
        f"""
        <style>
          .event-calendar-shell {{
            border: 1px solid {OVERVIEW_COLOR_BORDER};
            border-radius: 8px;
            overflow: hidden;
            background: {OVERVIEW_COLOR_SURFACE};
          }}
          .event-calendar-topbar {{
            display: flex;
            align-items: flex-start;
            justify-content: space-between;
            gap: 14px;
            padding: 12px 14px;
            border-bottom: 1px solid {OVERVIEW_COLOR_BORDER};
            background:
              linear-gradient(135deg, rgba(37, 99, 235, 0.08), rgba(15, 118, 110, 0.05)),
              {OVERVIEW_COLOR_SURFACE_SUBTLE};
          }}
          .event-calendar-title {{
            color: {OVERVIEW_COLOR_TEXT};
            font-size: 16px;
            font-weight: 780;
            line-height: 1.2;
          }}
          .event-calendar-subtitle {{
            color: {OVERVIEW_COLOR_TEXT_SUBTLE};
            font-size: 12px;
            font-weight: 650;
            margin-top: 3px;
          }}
          .event-calendar-legend {{
            display: flex;
            justify-content: flex-end;
            gap: 8px;
            flex-wrap: wrap;
            max-width: 58%;
          }}
          .event-calendar-legend-item {{
            display: inline-flex;
            align-items: center;
            gap: 5px;
            min-height: 24px;
            padding: 3px 8px;
            border: 1px solid {OVERVIEW_COLOR_BORDER};
            border-radius: 999px;
            background: {OVERVIEW_COLOR_SURFACE};
            color: {OVERVIEW_COLOR_TEXT_SUBTLE};
            font-size: 11px;
            font-weight: 720;
          }}
          .event-calendar-legend-dot {{
            width: 8px;
            height: 8px;
            border-radius: 999px;
            flex: 0 0 auto;
          }}
          .event-calendar-legend-fomc {{ background: {OVERVIEW_COLOR_PRIMARY}; }}
          .event-calendar-legend-macro {{ background: {OVERVIEW_COLOR_POSITIVE}; }}
          .event-calendar-legend-earnings {{ background: {OVERVIEW_COLOR_WARNING}; }}
          .event-calendar-legend-other {{ background: {OVERVIEW_COLOR_NEUTRAL}; }}
          .event-calendar-grid {{
            display: grid;
            grid-template-columns: repeat(7, minmax(0, 1fr));
          }}
          .event-calendar-weekday {{
            padding: 8px 10px;
            background: {OVERVIEW_COLOR_SURFACE_SUBTLE};
            border-bottom: 1px solid {OVERVIEW_COLOR_BORDER};
            color: {OVERVIEW_COLOR_NEUTRAL};
            font-size: 12px;
            font-weight: 700;
            text-transform: uppercase;
          }}
          .event-calendar-day {{
            min-height: 126px;
            padding: 8px;
            border-right: 1px solid {OVERVIEW_COLOR_BORDER};
            border-bottom: 1px solid {OVERVIEW_COLOR_BORDER};
            background: {OVERVIEW_COLOR_SURFACE};
          }}
          .event-calendar-day:nth-child(7n) {{
            border-right: 0;
          }}
          .event-calendar-muted {{
            background: {OVERVIEW_COLOR_SURFACE_SUBTLE};
            color: {OVERVIEW_COLOR_TEXT_MUTED};
          }}
          .event-calendar-has-events {{
            background:
              linear-gradient(180deg, rgba(248, 250, 252, 0.96), rgba(255, 255, 255, 0.98)),
              {OVERVIEW_COLOR_SURFACE_ALT};
          }}
          .event-calendar-has-high {{
            background:
              linear-gradient(180deg, rgba(180, 83, 9, 0.07), rgba(255, 255, 255, 0.98)),
              {OVERVIEW_COLOR_SURFACE_ALT};
          }}
          .event-calendar-today {{
            box-shadow: inset 0 0 0 2px {OVERVIEW_COLOR_PRIMARY};
          }}
          .event-calendar-day-head {{
            display: flex;
            align-items: center;
            justify-content: space-between;
            gap: 6px;
            margin-bottom: 8px;
          }}
          .event-calendar-date {{
            color: {OVERVIEW_COLOR_TEXT};
            font-size: 13px;
            font-weight: 700;
            line-height: 1;
          }}
          .event-calendar-count {{
            display: inline-flex;
            align-items: center;
            justify-content: center;
            min-width: 20px;
            height: 20px;
            border-radius: 999px;
            background: rgba(37, 99, 235, 0.10);
            color: {OVERVIEW_COLOR_PRIMARY};
            font-size: 10px;
            font-weight: 800;
          }}
          .event-calendar-items {{
            display: flex;
            flex-direction: column;
            gap: 5px;
          }}
          .event-calendar-item {{
            display: grid;
            grid-template-columns: auto minmax(0, 1fr);
            gap: 5px;
            align-items: center;
            border: 1px solid rgba(100, 116, 139, 0.18);
            border-radius: 6px;
            background: {OVERVIEW_COLOR_SURFACE};
            padding: 4px 5px;
            min-width: 0;
          }}
          .event-calendar-type {{
            color: {OVERVIEW_COLOR_TEXT_INVERSE};
            font-size: 10px;
            font-weight: 800;
            text-transform: uppercase;
            white-space: nowrap;
            border-radius: 999px;
            padding: 2px 5px;
          }}
          .event-calendar-type-fomc {{ background: {OVERVIEW_COLOR_PRIMARY}; }}
          .event-calendar-type-macro {{ background: {OVERVIEW_COLOR_POSITIVE}; }}
          .event-calendar-type-earnings {{ background: {OVERVIEW_COLOR_WARNING}; }}
          .event-calendar-type-other {{ background: {OVERVIEW_COLOR_NEUTRAL}; }}
          .event-calendar-text {{
            color: {OVERVIEW_COLOR_TEXT};
            font-size: 11px;
            overflow: hidden;
            text-overflow: ellipsis;
            white-space: nowrap;
            min-width: 0;
          }}
          .event-calendar-importance-high {{
            border-color: rgba(180, 83, 9, 0.35);
          }}
          .event-calendar-more {{
            color: {OVERVIEW_COLOR_NEUTRAL};
            font-size: 11px;
            font-weight: 700;
            padding: 2px 6px;
          }}
          @media (max-width: 760px) {{
            .event-calendar-topbar {{ flex-direction: column; }}
            .event-calendar-legend {{ justify-content: flex-start; max-width: 100%; }}
            .event-calendar-weekday {{ padding: 6px 4px; font-size: 10px; }}
            .event-calendar-day {{ min-height: 92px; padding: 5px; }}
            .event-calendar-item {{ display: block; padding: 3px 4px; }}
            .event-calendar-type {{ display: block; font-size: 9px; }}
            .event-calendar-text {{ display: block; font-size: 10px; }}
          }}
        </style>
        <div class="event-calendar-shell">
          <div class="event-calendar-topbar">
            <div>
              <div class="event-calendar-title">{escape(month_label)}</div>
              <div class="event-calendar-subtitle">{event_count} events · {high_impact_count} high impact</div>
            </div>
            <div class="event-calendar-legend">{legend_html}</div>
          </div>
          <div class="event-calendar-grid">
            {weekday_html}
            {"".join(day_cells)}
          </div>
        </div>
        """,
        unsafe_allow_html=True,
    )


def _event_focus_display_columns(rows: pd.DataFrame) -> list[str]:
    return [
        column
        for column in [
            "Date",
            "Days Until",
            "Type Label",
            "Symbol",
            "Title",
            "Importance",
            "Focus",
            "Validation",
            "Quality Action",
            "Freshness",
        ]
        if column in rows.columns
    ]


def render_event_detail_tabs(filtered_rows: Any) -> None:
    agenda_tab, calendar_tab, quality_tab, raw_tab = st.tabs(["Agenda", "Calendar", "Quality", "Raw"])
    with agenda_tab:
        render_event_agenda_sections(
            _event_agenda_sections(filtered_rows),
            empty_message="No upcoming event rows match the selected filters.",
        )
    with calendar_tab:
        _render_event_month_grid(filtered_rows)
        st.altair_chart(_build_event_calendar_chart(filtered_rows), width="stretch")
    with quality_tab:
        render_event_agenda_sections(
            _event_quality_sections(filtered_rows),
            empty_message="No event rows currently need source or validation review.",
        )
        quality_rows = _event_quality_rows(filtered_rows)
        if not quality_rows.empty:
            st.dataframe(
                quality_rows[_event_focus_display_columns(quality_rows)],
                width="stretch",
                hide_index=True,
            )
    with raw_tab:
        st.dataframe(
            filtered_rows.drop(columns=["Date Parsed"], errors="ignore"),
            width="stretch",
            hide_index=True,
        )
