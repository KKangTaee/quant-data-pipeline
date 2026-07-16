from __future__ import annotations

import importlib
from pathlib import Path
from unittest.mock import Mock, patch


def test_market_context_mode_order_default_and_unknown_fallback() -> None:
    module = importlib.import_module("app.web.overview.market_context")

    assert module.MARKET_CONTEXT_MODE_OPTIONS == (
        ("economic_cycle", "경제 사이클"),
        ("sp500", "S&P 500"),
        ("us_stock", "미국 개별주식"),
    )
    assert module.DEFAULT_MARKET_CONTEXT_MODE == "economic_cycle"
    assert module.normalize_market_context_mode(None) == "economic_cycle"
    assert module.normalize_market_context_mode("legacy") == "economic_cycle"
    assert module.normalize_market_context_mode("sp500") == "sp500"


def test_mode_selector_never_reassigns_widget_key_after_instantiation() -> None:
    module = importlib.import_module("app.web.overview.market_context")

    class WidgetState(dict):
        locked = False

        def __setitem__(self, key, value):
            if self.locked and key == module.MARKET_CONTEXT_MODE_KEY:
                raise RuntimeError("widget-owned key cannot be reassigned")
            super().__setitem__(key, value)

    state = WidgetState()

    def segmented_control(*_args, **_kwargs):
        assert module.MARKET_CONTEXT_MODE_KEY not in state
        state.locked = True
        return "economic_cycle"

    with patch.object(module.st, "segmented_control", side_effect=segmented_control):
        selected = module.render_market_context_mode_selector(state=state)

    assert selected == "economic_cycle"
    assert module.MARKET_CONTEXT_MODE_KEY not in state


def test_mode_selector_removes_legacy_widget_value_before_instantiation() -> None:
    module = importlib.import_module("app.web.overview.market_context")
    state = {module.MARKET_CONTEXT_MODE_KEY: "valuation"}

    def segmented_control(*_args, **kwargs):
        assert module.MARKET_CONTEXT_MODE_KEY not in state
        assert kwargs["default"] == "economic_cycle"
        return "economic_cycle"

    with patch.object(module.st, "segmented_control", side_effect=segmented_control):
        selected = module.render_market_context_mode_selector(state=state)

    assert selected == "economic_cycle"


def test_economic_cycle_mode_renders_only_cycle_surface() -> None:
    module = importlib.import_module("app.web.overview.market_context")
    cycle_renderer = Mock()
    valuation_renderer = Mock()

    selected = module.render_market_context_content(
        "economic_cycle",
        cycle_renderer=cycle_renderer,
        valuation_renderer=valuation_renderer,
    )

    assert selected == "economic_cycle"
    cycle_renderer.assert_called_once_with()
    valuation_renderer.assert_not_called()


def test_each_valuation_mode_builds_only_selected_instrument_without_inner_selector() -> (
    None
):
    service = importlib.import_module("app.services.overview.market_context_valuation")
    sp500 = {"status": "READY", "instrument": {"id": "sp500"}}
    stock = {
        "status": "READY",
        "instrument": {"id": "us_stock"},
        "multiple_regime": {"status": "READY", "current_pe": 20.0},
    }

    with (
        patch.object(
            service, "build_sp500_valuation_read_model", return_value=sp500
        ) as sp_builder,
        patch.object(
            service, "build_us_stock_valuation_read_model", return_value=stock
        ) as stock_builder,
        patch.object(
            service,
            "build_us_stock_turnaround_read_model",
            return_value={"status": "READY"},
        ),
    ):
        sp_model = service.build_market_context_valuation_read_model(
            default_instrument="sp500", show_instrument_selector=False
        )
        assert list(sp_model["instruments"]) == ["sp500"]
        assert sp_model["show_instrument_selector"] is False
        sp_builder.assert_called_once_with()
        stock_builder.assert_not_called()

    with (
        patch.object(
            service, "build_sp500_valuation_read_model", return_value=sp500
        ) as sp_builder,
        patch.object(
            service, "build_us_stock_valuation_read_model", return_value=stock
        ) as stock_builder,
        patch.object(
            service,
            "build_us_stock_turnaround_read_model",
            return_value={"status": "READY"},
        ),
        patch.object(
            service,
            "build_us_stock_data_freshness",
            return_value={"status": "READY"},
        ),
    ):
        stock_model = service.build_market_context_valuation_read_model(
            selected_symbol="AAPL",
            default_instrument="us_stock",
            show_instrument_selector=False,
        )
        assert list(stock_model["instruments"]) == ["us_stock"]
        assert stock_model["default_instrument"] == "us_stock"
        sp_builder.assert_not_called()
        stock_builder.assert_called_once_with(selected_symbol="AAPL", search_query=None)


def test_content_router_passes_mode_and_hidden_selector_to_valuation() -> None:
    module = importlib.import_module("app.web.overview.market_context")
    valuation_renderer = Mock()

    module.render_market_context_content(
        "us_stock",
        cycle_renderer=Mock(),
        valuation_renderer=valuation_renderer,
    )

    valuation_renderer.assert_called_once_with(
        default_instrument="us_stock", show_instrument_selector=False
    )


def test_cycle_bridge_is_db_only_and_has_no_action_event() -> None:
    helper_source = Path("app/web/overview/market_context_helpers.py").read_text()
    bridge_source = Path(
        "app/web/overview/economic_cycle_react_component.py"
    ).read_text()

    assert "build_economic_cycle_read_model" in helper_source
    assert "run_collect_economic_cycle" not in helper_source
    assert "run_materialize_economic_cycle" not in helper_source
    assert "finance.data.economic_cycle_vintages" not in helper_source + bridge_source
    assert "event" not in bridge_source.lower()


def test_legacy_valuation_call_keeps_both_instruments_and_internal_selector() -> None:
    service = importlib.import_module("app.services.overview.market_context_valuation")
    with (
        patch.object(
            service,
            "build_sp500_valuation_read_model",
            return_value={"status": "READY", "instrument": {"id": "sp500"}},
        ),
        patch.object(
            service,
            "build_us_stock_valuation_read_model",
            return_value={
                "status": "READY",
                "instrument": {"id": "us_stock"},
                "multiple_regime": {"status": "READY", "current_pe": 20.0},
            },
        ),
        patch.object(
            service,
            "build_us_stock_turnaround_read_model",
            return_value={"status": "READY"},
        ),
        patch.object(
            service,
            "build_us_stock_data_freshness",
            return_value={"status": "READY"},
        ),
    ):
        model = service.build_market_context_valuation_read_model()

    assert model["default_instrument"] == "sp500"
    assert model["show_instrument_selector"] is True
    assert set(model["instruments"]) == {"sp500", "us_stock"}


def test_us_stock_event_contract_remains_available_after_outer_routing() -> None:
    helpers = importlib.import_module("app.web.overview.market_context_helpers")
    state = {helpers.US_STOCK_SELECTED_SYMBOL_KEY: "AAPL"}
    rerun = Mock()

    handled = helpers._handle_market_context_valuation_event(
        {
            "event": {
                "id": "select_us_stock",
                "symbol": "MSFT",
                "nonce": "route-test",
            }
        },
        state=state,
        rerun=rerun,
    )

    assert handled is True
    assert state[helpers.US_STOCK_SELECTED_SYMBOL_KEY] == "MSFT"
    rerun.assert_called_once_with()


def test_cycle_component_source_contract_covers_full_reading_flow() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    for token in (
        'const PHASE_ORDER: Phase[] = ["recovery", "expansion", "slowdown", "recession"]',
        '0: "현재"',
        '1: "1개월 후"',
        '2: "2개월 후"',
        'className="probability-bar"',
        ".slice(-12)",
        "실선은 최근 12개월",
        "최근 5년 + 2개월 전망",
        'className="cycle-quadrant"',
        'className="observed-path"',
        'className="forecast-path"',
        "probabilityCoordinate",
        "resolveEstimateStatus",
        "잠정 모델 추정",
        "검증된 모델 추정",
        'evidence.group === "real_economy"',
        'evidence.group === "forecast_context"',
        'className="market-implications"',
        "자산별 확인 포인트",
        "매매 신호가 아닌 조건부 점검",
        'className={`implication-status assessment-${item.assessment.toLowerCase()}`}',
        'className="implication-drivers"',
        "바뀌는 조건",
        'className="regime-ribbon"',
        'className="nber-recession"',
        'className="limited-hatch"',
        "방법론과 품질",
        "모델과 NBER 이력을 분리",
        "수익률 예측이나 매매 지시가 아닙니다",
    ):
        assert token in source


def test_cycle_component_ready_and_limited_probability_semantics_are_safe() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert "PHASE_ORDER.map((phase)" in source
    assert "horizon.probabilities" in source
    assert 'horizon.estimate_status === "PROVISIONAL"' in source
    assert 'horizon.estimate_status === "VERIFIED"' in source
    assert "formatPercent(horizon.probabilities[phase])" in source
    assert "horizon.probabilities ?? { recovery: 0" not in source
    assert "formatPercent(0)" not in source
    assert "판단 불가" in source


def test_cycle_component_breaks_paths_at_unavailable_months_and_horizons() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert "splitPointSegments" in source
    assert "payload.history.slice(-12)" in source
    assert "const forecastSlots = [0, 1, 2].map" in source
    assert "observedSegments.map" in source
    assert "forecastSegments.map" in source
    assert "payload.history\n    .filter" not in source
    assert "payload.horizons\n    .filter" not in source


def test_cycle_component_ribbon_grid_uses_actual_history_month_count() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    assert "--history-month-count" in source
    assert "Math.max(history.length, 1)" in source
    assert "repeat(var(--history-month-count)" in css
    assert "repeat(121" not in css


def test_cycle_component_cycle_points_expose_hover_and_focus_tooltips() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        "cycle-hover-target",
        "cycle-hover-area",
        "cycle-tooltip",
        "cycleTooltipPosition",
        "cyclePointLabel",
        "tabIndex={0}",
        "aria-label={label}",
    ):
        assert token in source
    assert ".cycle-tooltip { opacity: 0" in css
    assert ".cycle-hover-target:hover .cycle-tooltip" in css
    assert ".cycle-hover-target:focus .cycle-tooltip" in css


def test_cycle_component_ribbon_preserves_empty_history_and_forecast_slots() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert "const forecastSlots = [1, 2].map" in source
    assert "forecastSlots.map" in source
    assert "ribbon-empty-history" in source
    assert "horizons.filter((item) => item.horizon_months > 0)" not in source
    assert 'role="group"' in source
    assert 'role="img"' in source


def test_cycle_component_has_no_fetch_job_trading_or_refresh_loop() -> None:
    root = Path("app/web/streamlit_components/economic_cycle_workbench")
    source = "\n".join(
        path.read_text()
        for path in (root / "src").glob("*")
        if path.suffix in {".tsx", ".ts", ".css"}
    ).lower()

    for forbidden in (
        "fetch(",
        "axios",
        "setinterval",
        "settimeout",
        "streamlit.setcomponentvalue",
        "run_collect",
        "materialize",
        "매수",
        "매도",
        "주문",
    ):
        assert forbidden not in source


def test_cycle_component_responsive_contract_avoids_mobile_horizontal_scroll() -> None:
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    assert "@media (max-width: 420px)" in css
    assert "overflow-x: hidden" in css
    assert ".horizon-grid" in css
    assert "grid-template-columns: 1fr" in css
    assert ".cycle-layout" in css
    assert ".regime-ribbon" in css


def test_valuation_component_honors_hidden_selector_with_legacy_default() -> None:
    source = Path(
        "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
    ).read_text()

    assert "show_instrument_selector?: boolean" in source
    assert "combined.show_instrument_selector !== false" in source
    assert (
        "combined ?"
        not in source[
            source.index('className="instrument-selector"')
            - 80 : source.index('className="instrument-selector"')
        ]
    )
