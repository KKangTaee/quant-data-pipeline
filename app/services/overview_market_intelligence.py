from __future__ import annotations

from typing import Any, Callable

from app.services.overview.data_health import (
    build_collection_ops_snapshot,
    build_overview_data_health_ingestion_handoff,
)
from app.services.overview.events import (
    build_market_events_snapshot,
    build_overview_macro_week_lane,
)
from app.services.overview.market_context import (
    build_overview_macro_context_cockpit,
    build_overview_source_confidence_catalog,
)
from app.services.overview.market_movers import (
    _query_latest_raw_date,
    build_group_leadership_snapshot,
    build_market_movers_snapshot,
    build_overview_breadth_heatmap_summary,
    load_market_mover_sector_options,
    resolve_effective_market_dates,
    resolve_group_trend_market_dates,
)
from app.services.overview.sentiment import build_market_sentiment_snapshot
from app.services.overview.why_it_moved import (
    WHY_IT_MOVED_KOREAN_NEWS_COLUMNS,
    WHY_IT_MOVED_NEWS_COLUMNS,
    WHY_IT_MOVED_SEC_COLUMNS,
    _fetch_google_news_kr_rss_metadata,
    _fetch_sec_recent_filing_metadata,
    _fetch_yfinance_news_metadata,
    build_market_mover_catalyst_links,
    build_market_mover_metadata_not_requested_state,
    build_market_mover_metadata_status_strip,
    build_market_mover_why_it_moved_read_model,
    sort_market_mover_sec_filings_by_form_priority,
)
from app.services.overview import why_it_moved as _why_it_moved


def fetch_market_mover_compact_metadata(
    symbol: str,
    *,
    name: str | None = None,
    max_news: int = 5,
    max_korean_news: int = 5,
    max_filings: int = 5,
    news_fetcher: Callable[[str, int], list[dict[str, Any]]] | None = None,
    korean_news_fetcher: Callable[[str, str | None, int, float], list[dict[str, Any]]] | None = None,
    sec_fetcher: Callable[[str, int, str | None, float], list[dict[str, Any]]] | None = None,
    user_agent: str | None = None,
    request_timeout: float = 8.0,
) -> dict[str, Any]:
    """Compatibility wrapper preserving monkeypatchable legacy provider hooks."""
    return _why_it_moved.fetch_market_mover_compact_metadata(
        symbol,
        name=name,
        max_news=max_news,
        max_korean_news=max_korean_news,
        max_filings=max_filings,
        news_fetcher=news_fetcher or _fetch_yfinance_news_metadata,
        korean_news_fetcher=korean_news_fetcher or _fetch_google_news_kr_rss_metadata,
        sec_fetcher=sec_fetcher or _fetch_sec_recent_filing_metadata,
        user_agent=user_agent,
        request_timeout=request_timeout,
    )


__all__ = [
    "WHY_IT_MOVED_KOREAN_NEWS_COLUMNS",
    "WHY_IT_MOVED_NEWS_COLUMNS",
    "WHY_IT_MOVED_SEC_COLUMNS",
    "_fetch_google_news_kr_rss_metadata",
    "_query_latest_raw_date",
    "build_collection_ops_snapshot",
    "build_group_leadership_snapshot",
    "build_market_events_snapshot",
    "build_market_mover_catalyst_links",
    "build_market_mover_metadata_not_requested_state",
    "build_market_mover_metadata_status_strip",
    "build_market_mover_why_it_moved_read_model",
    "build_market_movers_snapshot",
    "build_market_sentiment_snapshot",
    "build_overview_breadth_heatmap_summary",
    "build_overview_data_health_ingestion_handoff",
    "build_overview_macro_context_cockpit",
    "build_overview_macro_week_lane",
    "build_overview_source_confidence_catalog",
    "fetch_market_mover_compact_metadata",
    "load_market_mover_sector_options",
    "resolve_effective_market_dates",
    "resolve_group_trend_market_dates",
    "sort_market_mover_sec_filings_by_form_priority",
]
