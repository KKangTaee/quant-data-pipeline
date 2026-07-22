from pathlib import Path

from app.web.overview.navigation import (
    MARKET_RESEARCH_FAMILY_OPTIONS,
    MARKET_RESEARCH_VIEW_OPTIONS,
    market_research_default_view_for_family,
    market_research_family_for_view,
    market_research_views_for_family,
    normalize_market_research_view,
    resolve_market_research_seed_view,
)


def test_market_research_views_cover_three_purpose_families():
    assert MARKET_RESEARCH_FAMILY_OPTIONS == (
        "market-environment",
        "index-valuation",
        "stock-research",
    )
    assert MARKET_RESEARCH_VIEW_OPTIONS == (
        "economic-cycle",
        "futures-macro",
        "sentiment",
        "events",
        "sp500",
        "market-movers",
        "us-stock",
    )
    assert market_research_views_for_family("market-environment") == (
        "economic-cycle",
        "futures-macro",
        "sentiment",
        "events",
    )
    assert market_research_views_for_family("index-valuation") == ("sp500",)
    assert market_research_views_for_family("stock-research") == (
        "market-movers",
        "us-stock",
    )


def test_market_research_legacy_slug_normalization():
    assert normalize_market_research_view("market-context", "sp500") == "sp500"
    assert normalize_market_research_view("market-context", "us_stock") == "us-stock"
    assert normalize_market_research_view("market-context", None) == "economic-cycle"
    assert normalize_market_research_view("market-movers") == "market-movers"
    assert normalize_market_research_view("does-not-exist") == "economic-cycle"


def test_changed_query_wins_over_stale_widget_state():
    assert resolve_market_research_seed_view(
        query_slug="market-movers",
        applied_query_slug="economic-cycle",
        widget_view="sentiment",
        session_view="events",
        legacy_market_context_mode=None,
    ) == "market-movers"
    assert resolve_market_research_seed_view(
        query_slug="market-movers",
        applied_query_slug="market-movers",
        widget_view="us-stock",
        session_view="market-movers",
        legacy_market_context_mode=None,
    ) == "us-stock"


def test_market_research_defaults_are_stable():
    assert market_research_default_view_for_family("market-environment") == "economic-cycle"
    assert market_research_default_view_for_family("index-valuation") == "sp500"
    assert market_research_default_view_for_family("stock-research") == "market-movers"
    assert market_research_family_for_view("broken") == "market-environment"


def test_market_research_dispatch_calls_only_selected_view():
    from app.web.overview.navigation import _render_selected_market_research_view

    calls = []
    selected = _render_selected_market_research_view(
        "us-stock",
        renderers={
            "economic-cycle": lambda: calls.append("economic-cycle"),
            "us-stock": lambda: calls.append("us-stock"),
        },
    )
    assert selected == "us-stock"
    assert calls == ["us-stock"]


def test_market_research_page_removes_overview_global_blocks():
    source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
    body = source[source.index("def render_overview_dashboard"):]
    assert 'st.title("Market Research")' in body
    assert "Today에서 확인한 시장 판단을 환경·가치평가·종목 근거로 확장합니다." in body
    assert "render_reference_contextual_help" not in body
    assert "render_market_session_banner" not in body
    assert "_render_market_research_selector()" in body
