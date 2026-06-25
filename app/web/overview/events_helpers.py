from __future__ import annotations

from dataclasses import dataclass
from typing import Any

from app.web.overview import legacy_dashboard as _legacy
from app.web.overview.components.events import (
    render_event_agenda_sections,
    render_event_source_lane,
    render_event_warning_strip,
    render_events_summary_strip,
    render_macro_week_lane,
)


@dataclass(frozen=True)
class EventSnapshotContext:
    event_filter: str
    selected_event_type: str | None
    snapshot: dict[str, Any]
    coverage: dict[str, Any]
    rows: Any
    calendar_rows: Any


def render_events_header() -> None:
    _legacy.st.markdown("### Events")


def render_event_refresh_toolbar() -> str:
    return _legacy._render_event_refresh_toolbar()


def load_event_snapshot_context(event_filter: str) -> EventSnapshotContext:
    selected_event_type = None if event_filter == "ALL" else event_filter
    snapshot = _legacy.load_overview_market_events_snapshot(
        event_type=selected_event_type,
        horizon_days=540,
    )
    coverage = dict(snapshot.get("coverage") or {})
    rows = snapshot.get("rows")
    calendar_rows = (
        _legacy._prepare_event_calendar_frame(rows)
        if isinstance(rows, _legacy.pd.DataFrame)
        else _legacy.pd.DataFrame()
    )
    return EventSnapshotContext(
        event_filter=event_filter,
        selected_event_type=selected_event_type,
        snapshot=snapshot,
        coverage=coverage,
        rows=rows,
        calendar_rows=calendar_rows,
    )


def render_event_refresh_results() -> None:
    if not _legacy._has_event_refresh_result():
        return
    with _legacy.st.expander("Refresh Results", expanded=False):
        _legacy._render_market_job_result("overview_fomc_calendar_result")
        _legacy._render_market_job_result("overview_earnings_calendar_result")
        _legacy._render_market_job_result("overview_macro_calendar_result")


def render_events_overview_lanes(context: EventSnapshotContext) -> None:
    render_events_summary_strip(
        _legacy._event_summary_items(
            context.calendar_rows,
            context.coverage,
            event_type=context.snapshot.get("event_type"),
        )
    )
    render_event_source_lane(
        _legacy._event_source_items(context.calendar_rows, event_filter=context.event_filter)
    )
    render_event_warning_strip(list(context.snapshot.get("warnings") or []))
    render_macro_week_lane(_legacy.load_overview_macro_week_lane(context.snapshot))


def has_event_rows(context: EventSnapshotContext) -> bool:
    return isinstance(context.rows, _legacy.pd.DataFrame) and not context.rows.empty


def render_events_empty_state() -> None:
    _legacy.st.info(
        "Stored market event rows are not available for the selected filter. Run the matching refresh here or from Ingestion."
    )


def filter_event_calendar_rows(context: EventSnapshotContext) -> Any:
    return _legacy._filter_event_rows_for_calendar(context.calendar_rows)


def render_event_detail_tabs(filtered_rows: Any) -> None:
    agenda_tab, calendar_tab, quality_tab, raw_tab = _legacy.st.tabs(["Agenda", "Calendar", "Quality", "Raw"])
    with agenda_tab:
        render_event_agenda_sections(
            _legacy._event_agenda_sections(filtered_rows),
            empty_message="No upcoming event rows match the selected filters.",
        )
    with calendar_tab:
        _legacy._render_event_month_grid(filtered_rows)
        _legacy.st.altair_chart(_legacy._build_event_calendar_chart(filtered_rows), width="stretch")
    with quality_tab:
        render_event_agenda_sections(
            _legacy._event_quality_sections(filtered_rows),
            empty_message="No event rows currently need source or validation review.",
        )
        quality_rows = _legacy._event_quality_rows(filtered_rows)
        if not quality_rows.empty:
            _legacy.st.dataframe(
                quality_rows[_legacy._event_focus_display_columns(quality_rows)],
                width="stretch",
                hide_index=True,
            )
    with raw_tab:
        _legacy.st.dataframe(
            filtered_rows.drop(columns=["Date Parsed"], errors="ignore"),
            width="stretch",
            hide_index=True,
        )
