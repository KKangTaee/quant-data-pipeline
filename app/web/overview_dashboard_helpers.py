from __future__ import annotations

from typing import Any

import streamlit as st

from app.jobs.run_history import load_run_history
from app.services.overview_market_intelligence import (
    build_collection_ops_snapshot,
    build_group_leadership_snapshot,
    build_market_events_snapshot,
    build_market_movers_snapshot,
    build_market_sentiment_snapshot,
    load_market_mover_sector_options,
)


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


# Load the DB-backed sector / industry leadership snapshot for the Overview group tab.
@st.cache_data(ttl=120, show_spinner=False)
def load_overview_group_leadership_snapshot(
    *,
    universe_limit: int = 2000,
    universe_code: str | None = None,
    group_by: str = "sector",
    period: str = "monthly",
    top_n: int = 10,
    min_group_size: int = 5,
    trend_groups: tuple[str, ...] = (),
) -> dict[str, Any]:
    return build_group_leadership_snapshot(
        universe_limit=universe_limit,
        universe_code=universe_code,
        group_by=group_by,
        period=period,
        top_n=top_n,
        min_group_size=min_group_size,
        trend_groups=trend_groups,
    )


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


# Load the DB-backed CNN / AAII sentiment snapshot for the Overview Sentiment tab.
@st.cache_data(ttl=120, show_spinner=False)
def load_overview_market_sentiment_snapshot(cache_schema_version: str = "sentiment-learning-v3") -> dict[str, Any]:
    del cache_schema_version
    return build_market_sentiment_snapshot()


# Load the DB freshness and persisted job history snapshot for Overview Data Health.
def load_overview_collection_ops_snapshot() -> dict[str, Any]:
    return build_collection_ops_snapshot(history_rows=load_run_history(limit=200))
