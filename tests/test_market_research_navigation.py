from pathlib import Path
from unittest.mock import patch

from app.web.overview.navigation import (
    MARKET_RESEARCH_FAMILY_OPTIONS,
    MARKET_RESEARCH_VIEW_OPTIONS,
    _market_research_navigation_css,
    market_research_default_view_for_family,
    market_research_family_for_view,
    market_research_local_navigation_context,
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


def test_market_research_local_navigation_context_covers_single_and_multi_view_families():
    assert market_research_local_navigation_context("market-environment") == (
        "시장 환경",
        ("economic-cycle", "futures-macro", "sentiment", "events"),
    )
    assert market_research_local_navigation_context("index-valuation") == (
        "지수 가치평가",
        ("sp500",),
    )
    assert market_research_local_navigation_context("unknown")[0] == "시장 환경"


def test_market_research_navigation_css_uses_compact_and_responsive_contract():
    css = _market_research_navigation_css()
    source = Path("app/web/overview/navigation.py").read_text(encoding="utf-8")
    assert ".st-key-market_research_local_navigation" in css
    assert "width: fit-content" in css
    assert 'stBaseButton-segmented_controlActive' in css
    assert ".mr-market-research-local-label" in css
    assert "repeat(3, minmax(0, 1fr))" in css
    assert "repeat(2, minmax(0, 1fr))" in css
    assert "button:only-child" in css
    assert "key=MARKET_RESEARCH_LOCAL_NAV_KEY" in source


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
    from app.web.overview.page import _market_research_header_html

    source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
    body = source[source.index("def render_overview_dashboard"):]
    assert "_market_research_header_html()" in body
    assert (
        "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다."
        in _market_research_header_html()
    )
    assert 'st.container(key="market_research_page_header")' in body
    assert "render_reference_contextual_help" not in body
    assert "render_market_session_banner" not in body
    assert "_render_market_research_selector()" in body


def test_market_research_page_uses_compact_keyed_header():
    from app.web.overview.page import (
        _market_research_header_html,
        _market_research_page_css,
    )

    source = Path("app/web/overview/page.py").read_text(encoding="utf-8")
    css = _market_research_page_css()
    assert 'st.container(key="market_research_page_header")' in source
    assert "mr-market-research-page-header" in _market_research_header_html()
    assert "<h1>Market Research</h1>" in _market_research_header_html()
    assert 'st.caption("RESEARCH WORKSPACE")' not in source
    assert "Today에서 발견한 질문을 시장·지수·종목 근거로 확장합니다." in source
    assert ".st-key-market_research_page_header" in css
    assert "clamp(" in css


def test_market_research_local_label_is_one_compact_html_block():
    source = Path("app/web/overview/navigation.py").read_text(encoding="utf-8")
    selector_body = source[source.index("def _render_market_research_selector"):]
    selector_body = selector_body[: selector_body.index("def _render_selected_market_research_view")]

    assert 'class="mr-market-research-local-label"' in selector_body
    assert 'st.caption("선택한 리서치")' not in selector_body
    assert "gap=\"small\"" in selector_body


def test_market_movers_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.market_movers import render_market_movers_tab

    with (
        patch("app.web.overview.market_movers.render_market_movers_header") as header,
        patch("app.web.overview.market_movers.render_market_movers_controls") as controls,
        patch("app.web.overview.market_movers.render_market_movers_context_captions"),
        patch("app.web.overview.market_movers.normalize_market_movers_refresh_mode"),
        patch(
            "app.web.overview.market_movers.is_market_movers_auto_refresh_enabled",
            return_value=False,
        ),
        patch("app.web.overview.market_movers.render_market_movers_snapshot"),
    ):
        controls.return_value = object()
        render_market_movers_tab(show_header=False)
    header.assert_not_called()


def test_futures_sentiment_events_keep_legacy_header_default():
    from app.web.overview.futures_macro import render_futures_macro_tab

    with (
        patch("app.web.overview.futures_macro.render_futures_macro_header") as header,
        patch("app.web.overview.futures_macro.render_futures_macro_fragment"),
    ):
        render_futures_macro_tab()
    header.assert_called_once_with()


def test_futures_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.futures_macro import render_futures_macro_tab

    with (
        patch("app.web.overview.futures_macro.render_futures_macro_header") as header,
        patch("app.web.overview.futures_macro.render_futures_macro_fragment"),
    ):
        render_futures_macro_tab(show_header=False)
    header.assert_not_called()


def test_sentiment_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.sentiment import render_sentiment_tab

    with (
        patch("app.web.overview.sentiment.render_sentiment_header") as header,
        patch("app.web.overview.sentiment.load_sentiment_snapshot", return_value={}),
        patch(
            "app.web.overview.sentiment.render_sentiment_react_workbench_section",
            return_value=True,
        ),
        patch("app.web.overview.sentiment.render_sentiment_job_result"),
        patch("app.web.overview.sentiment.has_sentiment_rows", return_value=False),
        patch("app.web.overview.sentiment.render_sentiment_empty_state"),
    ):
        render_sentiment_tab(show_header=False)
    header.assert_not_called()


def test_events_page_dispatch_can_suppress_duplicate_header():
    from app.web.overview.events import render_events_tab

    with (
        patch("app.web.overview.events.render_events_header") as header,
        patch("app.web.overview.events.events_react_workbench_available", return_value=True),
        patch("app.web.overview.events.load_event_snapshot_context", return_value={}),
        patch(
            "app.web.overview.events.render_events_react_workbench_section",
            return_value=True,
        ),
        patch("app.web.overview.events.has_event_rows", return_value=False),
        patch("app.web.overview.events.render_events_empty_state"),
    ):
        render_events_tab(show_header=False)
    header.assert_not_called()


@patch("app.web.overview.market_movers_helpers.st")
def test_market_movers_handoff_opens_same_selected_symbol(mock_st):
    from app.web.overview.market_context_helpers import US_STOCK_SELECTED_SYMBOL_KEY
    from app.web.overview.market_movers_helpers import (
        MarketMoverControls,
        _dispatch_market_movers_react_event,
    )
    from app.web.overview.navigation import MARKET_RESEARCH_VIEW_KEY

    controls = MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    mock_st.session_state = {"overview_market_movers_selected_symbol_SP500": "AMD"}
    mock_st.query_params = {}

    handled = _dispatch_market_movers_react_event(
        {"event": {"id": "open_us_stock_research", "symbol": "amd", "nonce": 1}},
        controls=controls,
    )

    assert handled is True
    assert mock_st.session_state[US_STOCK_SELECTED_SYMBOL_KEY] == "AMD"
    assert mock_st.session_state[MARKET_RESEARCH_VIEW_KEY] == "us-stock"
    assert mock_st.query_params["overview_tab"] == "us-stock"
    mock_st.rerun.assert_called_once_with()


@patch("app.web.overview.market_movers_helpers.st")
def test_market_movers_handoff_rejects_symbol_not_currently_selected(mock_st):
    from app.web.overview.market_movers_helpers import (
        MarketMoverControls,
        _dispatch_market_movers_react_event,
    )

    controls = MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    mock_st.session_state = {"overview_market_movers_selected_symbol_SP500": "AMD"}
    mock_st.query_params = {}

    handled = _dispatch_market_movers_react_event(
        {"event": {"id": "open_us_stock_research", "symbol": "AAPL", "nonce": 2}},
        controls=controls,
    )

    assert handled is False
    assert "overview_us_stock_valuation_selected_symbol" not in mock_st.session_state
    mock_st.rerun.assert_not_called()


def test_market_movers_action_plan_allow_lists_stock_research_handoff():
    from app.web.overview.market_movers_helpers import (
        MarketMoverControls,
        market_movers_react_action_plan,
    )

    controls = MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    assert market_movers_react_action_plan(
        "open_us_stock_research",
        controls=controls,
    ) == {"handler": "open_us_stock_research"}
