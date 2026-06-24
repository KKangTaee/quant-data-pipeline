from __future__ import annotations

from app.web.overview import legacy_dashboard as _legacy


def render_events_tab() -> None:
    """Render the Events Overview tab."""
    _legacy.st.markdown("### Events")
    event_filter = _legacy._render_event_refresh_toolbar()

    selected_event_type = None if event_filter == "ALL" else event_filter
    snapshot = _legacy.load_overview_market_events_snapshot(event_type=selected_event_type, horizon_days=540)
    coverage = dict(snapshot.get("coverage") or {})
    rows = snapshot.get("rows")
    calendar_rows = (
        _legacy._prepare_event_calendar_frame(rows)
        if isinstance(rows, _legacy.pd.DataFrame)
        else _legacy.pd.DataFrame()
    )
    if _legacy._has_event_refresh_result():
        with _legacy.st.expander("Refresh Results", expanded=False):
            _legacy._render_market_job_result("overview_fomc_calendar_result")
            _legacy._render_market_job_result("overview_earnings_calendar_result")
            _legacy._render_market_job_result("overview_macro_calendar_result")
    _legacy.render_events_summary_strip(
        _legacy._event_summary_items(calendar_rows, coverage, event_type=snapshot.get("event_type"))
    )
    _legacy.render_event_source_lane(_legacy._event_source_items(calendar_rows, event_filter=event_filter))
    _legacy.render_event_warning_strip(list(snapshot.get("warnings") or []))
    _legacy.render_macro_week_lane(_legacy.load_overview_macro_week_lane(snapshot))

    if not isinstance(rows, _legacy.pd.DataFrame) or rows.empty:
        _legacy.st.info(
            "Stored market event rows are not available for the selected filter. Run the matching refresh here or from Ingestion."
        )
        return

    filtered_rows = _legacy._filter_event_rows_for_calendar(calendar_rows)

    agenda_tab, calendar_tab, quality_tab, raw_tab = _legacy.st.tabs(["Agenda", "Calendar", "Quality", "Raw"])
    with agenda_tab:
        _legacy.render_event_agenda_sections(
            _legacy._event_agenda_sections(filtered_rows),
            empty_message="No upcoming event rows match the selected filters.",
        )
    with calendar_tab:
        _legacy._render_event_month_grid(filtered_rows)
        _legacy.st.altair_chart(_legacy._build_event_calendar_chart(filtered_rows), width="stretch")
    with quality_tab:
        _legacy.render_event_agenda_sections(
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
        _legacy.st.dataframe(filtered_rows.drop(columns=["Date Parsed"], errors="ignore"), width="stretch", hide_index=True)
