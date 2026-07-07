from __future__ import annotations

from app.web.overview.events_helpers import (
    filter_event_calendar_rows,
    has_event_rows,
    load_event_snapshot_context,
    render_event_detail_tabs,
    render_event_refresh_results,
    render_event_refresh_toolbar,
    render_events_streamlit_evidence_section,
    render_events_react_workbench_section,
    render_events_empty_state,
    render_events_header,
    render_events_overview_lanes,
    events_react_workbench_available,
)


def render_events_tab() -> None:
    """Render the Events Overview tab."""
    render_events_header()
    react_available = events_react_workbench_available()
    if react_available:
        event_filter = "ALL"
    else:
        event_filter = render_event_refresh_toolbar()
    context = load_event_snapshot_context(event_filter)
    react_rendered = render_events_react_workbench_section(context) if react_available else False
    if not react_rendered:
        render_event_refresh_results()
        render_events_overview_lanes(context)

    if not has_event_rows(context):
        render_events_empty_state()
        return

    if react_rendered:
        render_events_streamlit_evidence_section(context, expanded=False)
    else:
        filtered_rows = filter_event_calendar_rows(context)
        render_event_detail_tabs(filtered_rows)
