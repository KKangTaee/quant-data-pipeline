from __future__ import annotations

from typing import Any

import streamlit as st

from app.jobs.run_history import load_run_history
from app.services.overview.data_health import (
    build_collection_ops_snapshot,
    build_overview_data_health_ingestion_handoff,
)
from app.services.overview.events import (
    build_market_events_snapshot,
    build_overview_macro_week_lane,
)
from app.services.overview.ia import load_overview_ia_closeout_model
from app.services.overview.market_context import (
    build_overview_macro_context_cockpit,
)
from app.services.overview.market_movers import (
    build_group_leadership_snapshot,
    build_market_movers_snapshot,
    build_overview_breadth_heatmap_summary,
    load_market_mover_sector_options,
)
from app.services.overview.why_it_moved import build_market_mover_research_snapshot
from app.services.overview.sentiment import build_market_sentiment_snapshot
from app.services.overview_market_context_analog import build_historical_analog_snapshot
from app.services.futures_macro_thermometer import load_overview_futures_macro_snapshot


# Load the DB-backed market movers snapshot for the Overview market scan tab.
def load_overview_market_movers_snapshot(
    *,
    universe_limit: int = 1000,
    universe_code: str | None = None,
    period: str = "daily",
    top_n: int = 20,
    sector: str | None = None,
) -> dict[str, Any]:
    return build_market_movers_snapshot(
        universe_limit=universe_limit,
        universe_code=universe_code,
        period=period,
        top_n=top_n,
        sector=sector,
    )


# Load sector filter options for the current Overview market mover universe.
def load_overview_market_mover_sectors(
    *,
    universe_code: str = "TOP1000",
    universe_limit: int = 1000,
) -> list[str]:
    return load_market_mover_sector_options(
        universe_code=universe_code,
        universe_limit=universe_limit,
    )


@st.cache_data(ttl=600, show_spinner=False)
def load_overview_market_mover_research_snapshot(
    *,
    mover: dict[str, Any],
) -> dict[str, Any]:
    """Cache the bounded DB-only research snapshot for one selected ranking row."""

    return build_market_mover_research_snapshot(mover=dict(mover or {}))


# Load the DB-backed sector / industry leadership snapshot for the Overview group tab.
@st.cache_data(ttl=600, show_spinner=False)
def load_overview_group_leadership_snapshot(
    *,
    universe_limit: int = 2000,
    universe_code: str | None = None,
    group_by: str = "sector",
    period: str = "monthly",
    top_n: int = 10,
    min_group_size: int = 5,
    as_of_date: str | None = None,
    prefer_intraday: bool = True,
    trend_groups: tuple[str, ...] = (),
) -> dict[str, Any]:
    return build_group_leadership_snapshot(
        universe_limit=universe_limit,
        universe_code=universe_code,
        group_by=group_by,
        period=period,
        top_n=top_n,
        min_group_size=min_group_size,
        as_of_date=as_of_date,
        prefer_intraday=prefer_intraday,
        trend_groups=trend_groups,
    )


# Build a scan-first breadth summary from the already loaded group leadership snapshot.
def load_overview_breadth_heatmap_summary(group_leadership_snapshot: dict[str, Any]) -> dict[str, Any]:
    return build_overview_breadth_heatmap_summary(group_leadership_snapshot)


# Load the DB-backed market event calendar snapshot for the Overview Events tab.
def load_overview_market_events_snapshot(
    *,
    event_type: str | None = "FOMC_MEETING",
    horizon_days: int = 365,
    limit: int = 200,
) -> dict[str, Any]:
    return build_market_events_snapshot(
        event_type=event_type,
        horizon_days=horizon_days,
        limit=limit,
    )


# Build a near-term macro week lane from the already loaded market events snapshot.
def load_overview_macro_week_lane(events_snapshot: dict[str, Any]) -> dict[str, Any]:
    return build_overview_macro_week_lane(events_snapshot)


# Load the DB-backed CNN / AAII sentiment snapshot for the Overview Sentiment tab.
@st.cache_data(ttl=120, show_spinner=False)
def load_overview_market_sentiment_snapshot(cache_schema_version: str = "sentiment-learning-v3") -> dict[str, Any]:
    del cache_schema_version
    return build_market_sentiment_snapshot()


@st.cache_data(ttl=120, show_spinner=False)
def load_overview_market_context_historical_analog(
    as_of_date: str | None = None,
    pattern_window: str = "5D",
    events_snapshot: dict[str, Any] | None = None,
    group_leadership_snapshot: dict[str, Any] | None = None,
    cache_schema_version: str = "overview-historical-analog-v6-macro-dimension-disabled-audit",
) -> dict[str, Any]:
    del cache_schema_version
    group_snapshot = group_leadership_snapshot
    if group_snapshot is None:
        group_snapshot = load_overview_group_leadership_snapshot(
            universe_code="SP500",
            group_by="sector",
            period="daily",
            top_n=20,
            as_of_date=as_of_date,
            prefer_intraday=as_of_date is None,
        )
    return build_historical_analog_snapshot(
        group_leadership_snapshot=group_snapshot,
        as_of_date=as_of_date,
        pattern_window=pattern_window,
        events_snapshot=events_snapshot,
    )


# Load the DB freshness and persisted job history snapshot for Overview Data Health.
def load_overview_collection_ops_snapshot() -> dict[str, Any]:
    return build_collection_ops_snapshot(history_rows=load_run_history(limit=200))


# Build the read-only Data Health -> owning collection surface handoff model.
def load_overview_data_health_ingestion_handoff(collection_ops_snapshot: dict[str, Any] | None = None) -> dict[str, Any]:
    return build_overview_data_health_ingestion_handoff(
        collection_ops_snapshot or load_overview_collection_ops_snapshot()
    )


# Load the summary-first market context cockpit from existing Overview read models only.
@st.cache_data(ttl=120, show_spinner=False)
def load_overview_macro_context_cockpit(
    as_of_date: str | None = None,
    pattern_window: str = "5D",
    market_session_context: dict[str, Any] | None = None,
    include_futures_macro: bool = False,
    include_historical_analog: bool = False,
    cache_schema_version: str = "overview-cockpit-v10-light-entry",
) -> dict[str, Any]:
    del cache_schema_version
    market_movers_snapshot = load_overview_market_movers_snapshot(
        universe_code="SP500",
        period="daily",
        top_n=10,
    )
    group_leadership_snapshot = load_overview_group_leadership_snapshot(
        universe_code="SP500",
        group_by="sector",
        period="daily",
        top_n=20,
    )
    futures_macro_snapshot = None
    if include_futures_macro:
        futures_macro_snapshot = load_overview_futures_macro_snapshot()
    sentiment_snapshot = load_overview_market_sentiment_snapshot()
    events_snapshot = load_overview_market_events_snapshot(
        event_type=None,
        horizon_days=60,
        limit=100,
    )
    collection_ops_snapshot = load_overview_collection_ops_snapshot()
    historical_analog_snapshot = None
    if include_historical_analog:
        historical_analog_snapshot = load_overview_market_context_historical_analog(
            as_of_date=as_of_date,
            pattern_window=pattern_window,
            events_snapshot=events_snapshot,
            group_leadership_snapshot=group_leadership_snapshot if not as_of_date else None,
        )
    return build_overview_macro_context_cockpit(
        market_movers_snapshot=market_movers_snapshot,
        group_leadership_snapshot=group_leadership_snapshot,
        futures_macro_snapshot=futures_macro_snapshot,
        sentiment_snapshot=sentiment_snapshot,
        events_snapshot=events_snapshot,
        collection_ops_snapshot=collection_ops_snapshot,
        historical_analog_snapshot=historical_analog_snapshot,
        market_session_context=market_session_context,
        include_futures_macro=include_futures_macro,
        direct_market_context_refresh_only=True,
    )
