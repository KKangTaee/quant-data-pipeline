from __future__ import annotations

from app.web.overview.sentiment_helpers import (
    has_sentiment_rows,
    load_sentiment_snapshot,
    render_sentiment_controls,
    render_sentiment_detail_sections,
    render_sentiment_empty_state,
    render_sentiment_header,
    render_sentiment_job_result,
    render_sentiment_react_workbench_section,
    render_sentiment_snapshot_overview,
)


def render_sentiment_tab() -> None:
    """Render the Sentiment Overview tab."""
    render_sentiment_header()
    snapshot = load_sentiment_snapshot()
    react_rendered = render_sentiment_react_workbench_section(snapshot)
    if react_rendered:
        render_sentiment_job_result()
    else:
        render_sentiment_controls()
        render_sentiment_job_result()
        render_sentiment_snapshot_overview(snapshot)

    if not has_sentiment_rows(snapshot):
        render_sentiment_empty_state()
        return

    render_sentiment_detail_sections(snapshot)
