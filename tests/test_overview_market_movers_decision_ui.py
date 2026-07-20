from __future__ import annotations

from app.web.overview.market_movers_decision_ui import (
    build_market_movers_decision_shell_payload,
)


def _decision_payload() -> dict[str, object]:
    return {
        "schema_version": "market_movers_decision_payload_v1",
        "trust": {
            "state": "PARTIAL",
            "publish_results": True,
            "metrics": {
                "return": {"valid": 498, "total": 503, "excluded": 5},
            },
            "primary_action": "QUOTE_REFRESH",
        },
        "ranking": {
            "period": "daily",
            "ranking_mode": "top_gainers",
            "rows": [],
            "views": {
                "top_gainers": {
                    "label": "상승",
                    "kind": "symbol",
                    "rows": [
                        {
                            "Rank": 1,
                            "Symbol": "AAA",
                            "Name": "AAA Corp",
                            "Return %": 7.5,
                            "Sector": "Technology",
                            "Industry": "Software",
                            "Market Cap": 100_000_000_000,
                        },
                        {
                            "Rank": 2,
                            "Symbol": "BBB",
                            "Name": "BBB Corp",
                            "Return %": 5.0,
                            "Sector": "Industrials",
                            "Industry": "Machinery",
                            "Market Cap": 50_000_000_000,
                        },
                    ],
                }
            },
        },
        "group_context": {
            "sector": {"daily": {"flow": [], "bellwethers": []}},
            "industry": {"daily": {"flow": [], "bellwethers": []}},
        },
        "selected_research": {
            "schema_version": "market_mover_research_snapshot_v2",
            "status": "OK",
            "symbol": "BBB",
            "ytd_return": {"status": "OK", "return_pct": 18.2, "series": []},
            "financial_factor_series": {
                "quarterly": {
                    "factor_groups": {
                        "income": ["revenue", "operating_income", "net_income", "diluted_eps"],
                        "profitability": ["operating_margin", "net_margin", "roe"],
                        "stability": ["current_ratio", "debt_ratio"],
                    },
                    "factors": {
                        "revenue": {
                            "label": "매출",
                            "group": "income",
                            "unit": "currency",
                            "points": [{"period_end": "2026-03-31", "value": 10.0}],
                            "available_count": 1,
                            "excluded_count": 0,
                        },
                        "operating_income": {
                            "label": "영업이익",
                            "group": "income",
                            "unit": "currency",
                            "points": [],
                            "available_count": 0,
                            "excluded_count": 1,
                        },
                    },
                },
                "annual": {
                    "factor_groups": {},
                    "factors": {
                        "revenue": {
                            "label": "매출",
                            "group": "income",
                            "unit": "currency",
                            "points": [{"period_end": "2025-12-31", "value": 35.0}],
                            "available_count": 1,
                            "excluded_count": 0,
                        }
                    },
                },
            },
            "current_valuation": {
                "status": "UNAVAILABLE",
                "reason_code": "INCOMPLETE_REPORTED_DILUTED_EPS",
            },
        },
    }


def test_decision_shell_keeps_ranking_controls_compact_and_defaults_selection() -> None:
    payload = build_market_movers_decision_shell_payload(
        decision_payload=_decision_payload(),
        command={
            "coverage": "SP500",
            "period": "daily",
            "ranking_mode": "top_gainers",
            "top_n": 20,
        },
        command_controls=[
            {"id": "coverage", "label": "Coverage", "value": "SP500", "options": []},
            {"id": "period", "label": "기간", "value": "daily", "options": []},
            {"id": "sector", "label": "섹터", "value": "All", "options": []},
            {"id": "top_n", "label": "표시", "value": "20", "options": []},
            {"id": "mode", "label": "랭킹", "value": "top_gainers", "options": []},
        ],
        actions=[],
        selected_symbol=None,
    )

    assert payload["schema_version"] == "market_movers_decision_workbench_v1"
    assert payload["component"] == "MarketMoversDecisionWorkbench"
    assert [item["id"] for item in payload["command_line"]["controls"]] == [
        "coverage",
        "period",
        "mode",
        "top_n",
    ]
    assert payload["selection"]["symbol"] == "AAA"
    assert payload["selection"]["row"]["Name"] == "AAA Corp"
    assert payload["trust"]["state"] == "PARTIAL"


def test_decision_shell_selected_symbol_and_financial_controls_are_independent() -> None:
    payload = build_market_movers_decision_shell_payload(
        decision_payload=_decision_payload(),
        command={
            "coverage": "SP500",
            "period": "daily",
            "ranking_mode": "top_gainers",
            "top_n": 20,
        },
        command_controls=[],
        actions=[],
        selected_symbol="BBB",
    )

    assert payload["selection"]["symbol"] == "BBB"
    controls = payload["selection"]["financial_controls"]
    assert controls["frequencies"] == [
        {"id": "quarterly", "label": "분기"},
        {"id": "annual", "label": "연간"},
    ]
    assert [group["id"] for group in controls["factor_groups"]] == [
        "income",
        "profitability",
        "stability",
    ]
    revenue = controls["factor_groups"][0]["factors"][0]
    operating_income = controls["factor_groups"][0]["factors"][1]
    assert revenue["available_by_frequency"] == {"quarterly": True, "annual": True}
    assert operating_income["available_by_frequency"] == {"quarterly": False, "annual": False}
    assert controls["default_frequency"] == "quarterly"
    assert controls["default_factor"] == "revenue"
    assert payload["selection"]["research"]["current_valuation"]["status"] == "UNAVAILABLE"


def test_decision_workbench_loader_builds_all_group_periods_and_selected_research(monkeypatch) -> None:
    import pandas as pd

    from app.web.overview import market_movers_helpers as helpers

    controls = helpers.MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    snapshot = {
        "period": "daily",
        "rows": pd.DataFrame(
            [
                {"Rank": 1, "Symbol": "AAA", "Name": "AAA Corp", "Return %": 5.0},
                {"Rank": 2, "Symbol": "BBB", "Name": "BBB Corp", "Return %": 4.0},
            ]
        ),
        "mover_views": {
            "top_gainers": {
                "label": "상승",
                "kind": "symbol",
                "rows": pd.DataFrame(
                    [
                        {"Rank": 1, "Symbol": "AAA", "Name": "AAA Corp", "Return %": 5.0},
                        {"Rank": 2, "Symbol": "BBB", "Name": "BBB Corp", "Return %": 4.0},
                    ]
                ),
            }
        },
        "collection_readiness": {"state": "COMPLETE", "publish_results": True},
        "coverage": {"refresh_state": {"label": "Fresh"}},
    }
    group_calls: list[tuple[str, str]] = []

    def fake_group_loader(**kwargs: object) -> dict[str, object]:
        group_by = str(kwargs["group_by"])
        period = str(kwargs["period"])
        group_calls.append((group_by, period))
        return {
            "status": "OK",
            "group_by": group_by,
            "group_flow": [],
            "market_cap_bellwether_rows": [],
            "rows": [],
        }

    research_calls: list[str] = []

    def fake_research_loader(*, mover: dict[str, object], **_: object) -> dict[str, object]:
        symbol = str(mover["Symbol"])
        research_calls.append(symbol)
        return {
            "schema_version": "market_mover_research_snapshot_v2",
            "status": "OK",
            "symbol": symbol,
            "financial_factor_series": {},
        }

    monkeypatch.setattr(helpers.st, "session_state", {"overview_market_movers_refresh_mode": "manual"})
    payload = helpers.build_market_movers_decision_react_payload(
        snapshot,
        controls=controls,
        selected_symbol="BBB",
        group_snapshot_loader=fake_group_loader,
        research_loader=fake_research_loader,
    )

    assert group_calls == [
        ("sector", "daily"),
        ("sector", "weekly"),
        ("sector", "monthly"),
        ("industry", "daily"),
        ("industry", "weekly"),
        ("industry", "monthly"),
    ]
    assert research_calls == ["BBB"]
    assert payload["component"] == "MarketMoversDecisionWorkbench"
    assert payload["selection"]["symbol"] == "BBB"
    assert set(payload["group_context"]["sector"]) == {"daily", "weekly", "monthly"}


def test_overview_research_loader_keeps_selected_stock_query_behind_cached_boundary() -> None:
    from app.web.overview_dashboard_helpers import (
        load_overview_market_mover_research_snapshot,
    )

    result = load_overview_market_mover_research_snapshot(mover={})

    assert result["schema_version"] == "market_mover_research_snapshot_v2"
    assert result["status"] == "NO_SYMBOL"


def test_decision_react_shell_owns_ranking_breadth_and_selected_research() -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx"
    ).read_text(encoding="utf-8")
    style = Path(
        "app/web/streamlit_components/market_movers_workbench/src/style.css"
    ).read_text(encoding="utf-8")

    assert "MarketMoversDecisionWorkbenchPayload" in source
    assert "function MarketMoversCommandLine" in source
    assert "function RankingBoard" in source
    assert "function BreadthContext" in source
    assert "function QuickResearch" in source
    assert "function StockResearchTabs" in source
    assert 'payload.component === "MarketMoversDecisionWorkbench"' in source
    assert 'id: "select_symbol"' in source
    assert '["sector", "industry"]' in source
    assert '["daily", "weekly", "monthly"]' in source
    assert 'className="mm-decision__workbench"' in source
    assert 'className="mm-decision__ranking"' in source
    assert 'className="mm-decision__breadth"' in source
    assert ".mm-decision__workbench" in style
    assert "grid-template-columns: minmax(0, 1.62fr) minmax(320px, 1fr);" in style
    desktop_responsive = style[style.index("@media (max-width: 900px)") :]
    desktop_responsive = desktop_responsive[: desktop_responsive.index("@media (max-width: 760px)")]
    assert ".mm-decision__workbench" in desktop_responsive
    wide_responsive = style[style.index("@media (max-width: 1180px)") :]
    wide_responsive = wide_responsive[: wide_responsive.index("@media (max-width: 900px)")]
    assert ".mm-decision__workbench" not in wide_responsive


def test_decision_shell_uses_approved_hybrid_visual_foundation() -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx"
    ).read_text(encoding="utf-8")
    style = Path(
        "app/web/streamlit_components/market_movers_workbench/src/style.css"
    ).read_text(encoding="utf-8")
    decision_style = style[: style.index(".mm-workbench {")]

    assert 'className="mm-decision__surface-header"' in source
    assert "<h1>변동 종목</h1>" in source
    assert 'className="mm-decision__command-band"' in source
    assert "--mm-accent: #397fb7;" in decision_style
    assert "--mm-trust: #2f7f73;" in decision_style
    assert "border-radius: 20px;" in decision_style
    assert "border: 1px solid #d8e4ea;" in decision_style
    assert "linear-gradient(145deg, #f8fbfd 0%, #f2f7f9 62%, #eef5f7 100%)" in decision_style
    assert "border-top: 4px solid" not in decision_style


def test_decision_shell_connects_market_pulse_to_unified_decision_cards() -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx"
    ).read_text(encoding="utf-8")
    style = Path(
        "app/web/streamlit_components/market_movers_workbench/src/style.css"
    ).read_text(encoding="utf-8")
    decision_style = style[: style.index(".mm-workbench {")]

    assert "function MarketPulse" in source
    assert '<section className="mm-decision__pulse"' in source
    assert "<MarketPulse payload={payload} />" in source
    assert 'className="mm-decision__pulse-item"' in source
    assert "border-radius: 16px;" in decision_style
    assert "grid-template-columns: minmax(0, 1.62fr) minmax(320px, 1fr);" in decision_style
    assert "#7c3aed" not in decision_style
    assert 'id: "set_control"' in source
    assert 'id: "select_symbol"' in source


def test_decision_research_keeps_financial_period_and_factor_controls_separate() -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx"
    ).read_text(encoding="utf-8")
    style = Path(
        "app/web/streamlit_components/market_movers_workbench/src/style.css"
    ).read_text(encoding="utf-8")

    assert "function PriceMomentumChart" in source
    assert "function FinancialFactorChart" in source
    assert 'className="mm-decision__financial-frequency"' in source
    assert 'className="mm-decision__financial-groups"' in source
    assert 'className="mm-decision__financial-factors"' in source
    assert "available_by_frequency" in source
    assert "disabled={!available}" in source
    assert 'className="mm-decision__chart-layout"' in source
    assert "normalized_return_pct" in source
    assert "<polyline" in source
    assert ".mm-decision__chart-layout" in style
    assert "grid-template-columns: minmax(0, 7fr) minmax(220px, 3fr);" in style
    assert "@media (max-width: 760px)" in style


def test_decision_research_uses_report_family_tabs_and_responsive_focus_contract() -> None:
    from pathlib import Path

    source = Path(
        "app/web/streamlit_components/market_movers_workbench/src/MarketMoversWorkbench.tsx"
    ).read_text(encoding="utf-8")
    style = Path(
        "app/web/streamlit_components/market_movers_workbench/src/style.css"
    ).read_text(encoding="utf-8")
    decision_style = style[: style.index(".mm-workbench {")]

    assert "aria-selected={tab === id}" in source
    assert 'aria-controls={`mm-decision-panel-${id}`}' in source
    assert 'id={`mm-decision-tab-${id}`}' in source
    assert "border-bottom: 2px solid transparent;" in decision_style
    assert "border-bottom-color: var(--mm-accent);" in decision_style
    assert ".mm-decision button:focus-visible" in decision_style
    assert ".mm-decision select:focus-visible" in decision_style
    assert "outline: 2px solid rgba(57, 127, 183, 0.35);" in decision_style
    assert "@media (max-width: 900px)" in style
    assert "@media (max-width: 600px)" in style
    assert "grid-template-columns: minmax(0, 7fr) minmax(220px, 3fr);" in decision_style
    assert "payload.ranking.empty_reason" in source
    assert 'className="mm-decision__empty"' in source
    assert "mm-decision__trust--${trustState.toLowerCase()}" in source
    assert "#2563eb" not in source
    assert "#0f766e" not in decision_style


def test_market_movers_page_uses_decision_shell_without_legacy_duplicate() -> None:
    from pathlib import Path

    source = Path("app/web/overview/market_movers_helpers.py").read_text(encoding="utf-8")
    render_body = source[source.index("def render_market_movers_snapshot") :]

    assert "if market_movers_react_component_available():" in render_body
    assert "_render_market_movers_decision_shell(" in render_body
    decision_branch = render_body[
        render_body.index("if market_movers_react_component_available():") :
        render_body.index("react_event = _render_market_movers_react_summary")
    ]
    assert "_render_market_movers_snapshot_panel(" not in decision_branch
    assert "return" in decision_branch
    assert "_render_market_movers_snapshot_panel(" in render_body


def test_decision_shell_selection_event_updates_symbol_once(monkeypatch) -> None:
    from app.web.overview import market_movers_helpers as helpers

    controls = helpers.MarketMoverControls(
        coverage="SP500",
        universe_limit=500,
        period="daily",
        sector="All",
        top_n=20,
        mode="top_gainers",
    )
    monkeypatch.setattr(helpers.st, "session_state", {})
    rerun_calls: list[bool] = []
    monkeypatch.setattr(helpers.st, "rerun", lambda: rerun_calls.append(True))
    event = {"event": {"id": "select_symbol", "symbol": "bbb", "nonce": 101}}

    assert helpers._dispatch_market_movers_react_event(event, controls=controls) is True
    assert helpers.st.session_state["overview_market_movers_selected_symbol_SP500"] == "BBB"
    assert rerun_calls == [True]
    assert helpers._dispatch_market_movers_react_event(event, controls=controls) is False
    assert rerun_calls == [True]
