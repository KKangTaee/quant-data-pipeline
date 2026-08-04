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


def test_cycle_bridge_is_db_only_and_keeps_provider_jobs_outside_ui() -> None:
    helper_source = Path("app/web/overview/market_context_helpers.py").read_text()
    bridge_source = Path(
        "app/web/overview/economic_cycle_react_component.py"
    ).read_text()
    service_source = Path("app/services/overview/economic_cycle.py").read_text()

    assert "build_economic_cycle_read_model" in helper_source
    assert "run_collect_economic_cycle" not in helper_source
    assert "run_materialize_economic_cycle" not in helper_source
    combined_source = helper_source + bridge_source + service_source
    assert "finance.data.economic_cycle_vintages" not in combined_source
    assert "run_economic_cycle_intramonth_refresh" not in combined_source
    assert "materialize_economic_cycle_intramonth_snapshot" not in combined_source


def test_cycle_component_returns_explicit_action_event() -> None:
    module = importlib.import_module(
        "app.web.overview.economic_cycle_react_component"
    )
    component = Mock(
        return_value={
            "event": {
                "id": "refresh_economic_cycle_data",
                "nonce": "cycle-1",
            }
        }
    )

    with patch.object(
        module,
        "_declare_economic_cycle_component",
        return_value=component,
    ):
        result = module.render_economic_cycle_component(
            {"schema_version": "economic_cycle_v2"}
        )

    assert result["event"]["id"] == "refresh_economic_cycle_data"


def test_cycle_event_runs_once_and_clears_cache_only_on_usable_success() -> None:
    helpers = importlib.import_module("app.web.overview.market_context_helpers")
    state = {}
    run_action = Mock(
        return_value={"status": "partial_success", "message": "refreshed"}
    )
    store = Mock()
    clear = Mock()
    rerun = Mock()
    event = {
        "event": {
            "id": "refresh_economic_cycle_data",
            "nonce": "cycle-1",
        }
    }

    assert (
        helpers._handle_economic_cycle_event(
            event,
            state=state,
            run_action=run_action,
            store_result=store,
            clear_cache=clear,
            rerun=rerun,
        )
        is True
    )
    assert (
        helpers._handle_economic_cycle_event(
            event,
            state=state,
            run_action=run_action,
            store_result=store,
            clear_cache=clear,
            rerun=rerun,
        )
        is False
    )
    run_action.assert_called_once_with()
    store.assert_called_once()
    clear.assert_called_once_with()
    rerun.assert_called_once_with()


def test_cycle_event_keeps_cache_on_incomplete_result() -> None:
    helpers = importlib.import_module("app.web.overview.market_context_helpers")
    clear = Mock()

    helpers._handle_economic_cycle_event(
        {
            "event": {
                "id": "refresh_economic_cycle_data",
                "nonce": "cycle-2",
            }
        },
        state={},
        run_action=lambda: {"status": "incomplete", "message": "kept"},
        store_result=Mock(),
        clear_cache=clear,
        rerun=Mock(),
    )

    clear.assert_not_called()


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
        'schema_version: "economic_cycle_v3"',
        'const PHASE_ORDER: Phase[] = ["recovery", "expansion", "slowdown", "contraction"]',
        'contraction: "위축"',
        "현재 관측 국면",
        "최근 1·3·6개월 변화",
        "순환 경로로 본 현재 위치",
        "현재 관측과 전환 기준",
        "가능성이 높다는 예측이 아닙니다",
        "지속성",
        "확산도",
        "활동·고용 동반 확인",
        'className="cycle-route-map"',
        'className="cycle-route-node"',
        "cycle-route-direction",
        "summarizeCycleRouteHistory",
        'evidence.group === "real_economy"',
        'evidence.group === "forecast_context"',
        "현재 국면과 전환의 판단 근거",
        "현재 위치의 근거",
        "현재점에 반영되는 생산·소비와 고용·소득",
        "전환을 해석할 참고 맥락",
        "현재 국면을 바꾸지 않고 전환 조건을 해석하는 금융·선행·물가·정책 정보",
        'financial_leading_score: "금융·선행 여건"',
        'statusLabel: "기준 이상"',
        'statusLabel: "기준 이하"',
        'statusLabel: "기준 부근"',
        'statusLabel: "전환 지원"',
        'statusLabel: "전환 제약"',
        'statusLabel: "제약 완화"',
        'statusLabel: "영향 중립"',
        "다음 국면 전환 조건을 지지하는 참고 맥락입니다",
        "다음 국면 전환 조건을 제약하는 참고 맥락입니다",
        "자기 과거 기준보다 낮아 현재 경기 위치를 낮추는 근거입니다",
        "resolveEconomicStatePresentation",
        'STRENGTHENING: "강화"',
        'WEAKENING: "약화"',
        'statusLabel: "자료 부족"',
        "resolveEvidencePresentation",
        'className="market-implications"',
        "자산별 확인 포인트",
        "사이클 판단의 공통 경제 배경",
        "현재 움직임",
        "함께 관찰된 경로",
        "현재 해석",
        "향후 1·2개월 확인 조건",
        "데이터 범위",
        "1주(5거래일)",
        "1개월(21거래일)",
        "3개월(63거래일)",
        'className="pathway-group"',
        'className="price-pathway"',
        'className="pathway-details"',
        'className="regime-ribbon"',
        'className="nber-recession"',
        "방법론과 품질",
        "관측 국면과 NBER 이력을 분리",
        "수익률 예측이나 매매 지시가 아닙니다",
    ):
        assert token in source
    for forbidden in (
        "probabilityCoordinate",
        "HorizonCard",
        'className="forecast-path"',
        "payload.horizons",
        "payload.history",
        "probability_deltas",
        "향후 1·2개월 경기 전망",
    ):
        assert forbidden not in source


def test_cycle_component_renders_provisional_intramonth_change_without_replacing_headline() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        "type IntramonthChange",
        "function IntramonthChangePanel",
        "월말 이후 잠정 변화",
        "정식 월말 국면을 바꾸지 않습니다",
        "payload.intramonth_change",
        'className="intramonth-change-panel"',
        'className="intramonth-factor-deltas"',
    ):
        assert token in source
    assert "current_horizon" not in source
    assert "probability_deltas" not in source
    assert ".intramonth-change-panel" in css
    assert ".intramonth-factor-deltas" in css


def test_cycle_component_has_compact_manual_freshness_action() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        "data_freshness?: EconomicCycleFreshness",
        "refresh_result?: RefreshResult",
        "최신 데이터로 다시 계산",
        'id: "refresh_economic_cycle_data"',
        "Streamlit.setComponentValue",
        'className="cycle-freshness-bar"',
    ):
        assert token in source
    assert ".cycle-freshness-bar" in css
    assert "rows_written" not in source
    assert "failed_symbols" not in source
    assert "@media (max-width: 760px)" in css
    assert "@media (max-width: 420px)" in css

    assert "관측된 경제 상태" not in source
    assert "ECONOMIC_DIRECTION_LABEL[observation.direction]" not in source
    assert "강화 · 약화 · 중립" not in source
    assert "경제 국면:" not in source
    assert "바뀌는 조건" not in source
    assert "alignment" not in source
    assert "assessment" not in source
    assert "상승 요인이 될 수 있는 측정 경로" not in source
    assert "하락 요인이 될 수 있는 측정 경로" not in source
    assert "국면을 움직인 근거" not in source
    assert 'title="실물경제 근거"' not in source
    assert 'title="전망 맥락"' not in source


def test_cycle_component_evidence_role_styles_are_present() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        ".evidence-row-heading",
        ".evidence-description",
        ".evidence-tone-positive-level",
        ".evidence-tone-weak-level",
        ".evidence-tone-support",
        ".evidence-tone-burden",
        ".evidence-tone-neutral",
    ):
        assert token in source


def _pathway_style_block(style: str) -> str:
    start = style.index(".pathway-group")
    end = style.index(".method-disclosure", start)
    return style[start:end]


def test_economic_cycle_asset_ui_uses_observation_sections_without_left_rails() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    style = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        'schema_version: "economic_cycle_v3"',
        "사이클 판단의 공통 경제 배경",
        "현재 움직임",
        "함께 관찰된 경로",
        "현재 해석",
        "향후 1·2개월 확인 조건",
        "21거래일",
        "63거래일",
    ):
        assert token in source
    assert "관측된 경제 상태" not in source
    assert "ECONOMIC_DIRECTION_LABEL[observation.direction]" not in source
    assert "상승 요인이 될 수 있는 측정 경로" not in source
    observation_start = style.index(".observation-block")
    observation_style = style[observation_start : observation_start + 900]
    assert "border-left" not in observation_style
    assert "background: #f7fafb" in observation_style
    assert ".implication-card .movement-grid { grid-template-columns: 1fr; }" in style


def test_economic_cycle_asset_section_prefers_explicit_copy_and_scopes_larger_type() -> None:
    component = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/"
        "EconomicCycleWorkbench.tsx"
    ).read_text()
    style = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    assert 'className="market-implications"' in component
    assert "item.summary || item.narrative || item.context" in component
    assert "asset.summary || asset.narrative" in component
    assert (
        "item.current_interpretation?.length "
        "? item.current_interpretation "
        ": [item.narrative || item.summary || item.context]"
    ) in component
    for rule in (
        ".market-implications .section-heading > div > span { font-size: 11px; }",
        ".market-implications .section-heading h3 { font-size: 19px; }",
        ".market-implications .section-heading > small { font-size: 11px; }",
        ".market-implications .implication-summary { font-size: 12px; }",
        ".market-implications .economic-state-block p { font-size: 11px; }",
        ".market-implications .observation-block li { font-size: 10px; }",
        ".market-implications .series-primary-metrics > * { font-size: 9px; }",
        ".market-implications .price-return-grid strong { font-size: 11px; }",
    ):
        assert rule in style


def test_cycle_component_ready_and_limited_observed_state_semantics_are_safe() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert "payload.observed_state" in source
    assert "confidence_label" in source
    assert "revision_sensitivity_label" in source
    assert "data_status" in source
    assert "probabilities" not in source
    assert "판단 불가" in source


def test_cycle_component_uses_persisted_history_without_plotting_coordinates() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert 'className="cycle-route-map"' in source
    assert "summarizeCycleRouteHistory(payload.cycle_map.points)" in source
    assert "cycle-route-direction" in source
    assert "points.length - 7" in source
    assert "points.length - 4" in source
    assert "points.length - 2" in source
    assert 'className="cycle-quadrant"' not in source
    assert "actualCoordinate" not in source
    assert "forecastSegments" not in source
    assert "forecastSlots" not in source


def test_cycle_component_ribbon_grid_uses_actual_history_month_count() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    assert "--history-month-count" in source
    assert "Math.max(points.length, 1)" in source
    assert "repeat(var(--history-month-count)" in css
    assert "repeat(121" not in css


def test_cycle_component_route_map_exposes_accessible_current_and_direction_text() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    for token in (
        'className="cycle-route-map"',
        'className="cycle-route-node"',
        "현재 관측",
        "방향 관찰 · 예측 아님",
        "aria-label",
    ):
        assert token in source


def test_cycle_component_ribbon_preserves_empty_actual_history_without_forecast_slots() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert "ribbon-empty-history" in source
    assert "forecast-ribbon" not in source
    assert "+2M" not in source
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
    assert ".recent-change-grid" in css
    assert "grid-template-columns: 1fr" in css
    assert ".cycle-layout" in css
    assert ".regime-ribbon" in css


def test_cycle_component_has_collapsed_monthly_signal_usage_guide() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()
    css = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/style.css"
    ).read_text()

    for token in (
        '<details className="cycle-usage-guide">',
        "월별 사이클 신호 활용법",
        "한 달 신호",
        "같은 방향이 여러 달",
        "실물·금융·가격",
        "회복 신호",
        "확장 신호",
        "둔화 신호",
        "위축 신호",
        "위축 → 회복",
        "회복 → 확장",
        "확장 → 둔화",
        "둔화 → 위축",
    ):
        assert token in source

    assert ".cycle-guide-phase-grid" in css
    assert ".cycle-guide-transition-grid" in css
    guide_start = css.index(".cycle-usage-guide")
    guide_end = css.index(".method-disclosure", guide_start)
    assert "border-left" not in css[guide_start:guide_end]


def test_cycle_component_formats_rate_levels_and_explains_basis_points() -> None:
    source = Path(
        "app/web/streamlit_components/economic_cycle_workbench/src/EconomicCycleWorkbench.tsx"
    ).read_text()

    assert "formatMovementLevel" in source
    assert 'unit === "percent" ? `연 ${value.toFixed(2)}%`' in source
    assert 'row.level_unit === "percent" || row.level_unit === "bp"' in source
    assert "현재 값은 최신 저장 관측치이며, 금리 변화는 bp 기준입니다." in source
    assert "row.current_value.toFixed(2)} {row.level_unit" not in source


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
