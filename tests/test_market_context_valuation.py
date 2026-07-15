from __future__ import annotations

import unittest
from unittest.mock import Mock, patch
from pathlib import Path

import pandas as pd


def _sep_rows() -> pd.DataFrame:
    rows = []
    values = {
        "central_tendency_lower": (1.5, 2.0),
        "median": (2.0, 2.2),
        "central_tendency_upper": (2.5, 2.4),
    }
    for statistic, (gdp, pce) in values.items():
        rows.extend(
            [
                {"target_year": 2027, "variable_name": "real_gdp", "statistic_name": statistic, "value_pct": gdp, "release_date": "2026-06-15"},
                {"target_year": 2027, "variable_name": "pce_inflation", "statistic_name": statistic, "value_pct": pce, "release_date": "2026-06-15"},
            ]
        )
    return pd.DataFrame(rows)


class MarketContextValuationTests(unittest.TestCase):
    def test_nasdaq_model_preserves_coverage_block_evidence(self) -> None:
        from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model

        model = build_nasdaq100_valuation_read_model(
            monthly_rows=[{"observation_month": "2026-07-01", "qqq_price": 709.43, "trailing_pe": None,
                           "reconstructed_ttm_eps": None, "coverage_weight_pct": 94.47,
                           "unmapped_weight_pct": 5.53, "data_quality": "blocked",
                           "error_msg": "INSUFFICIENT_EARNINGS_COVERAGE"}],
            ttm_evidence={"status": "BLOCKED", "coverage_weight_pct": 94.47,
                          "unmapped_weight_pct": 5.53, "error_code": "INSUFFICIENT_EARNINGS_COVERAGE"},
            sep_rows=_sep_rows(), sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 709.43}],
        )

        self.assertEqual(model["status"], "BLOCKED")
        self.assertEqual(model["coverage"]["coverage_weight_pct"], 94.47)
        self.assertEqual(model["instrument"]["proxy_symbol"], "QQQ")
        self.assertEqual(model["earnings_scenario"]["status"], "BLOCKED")

    def test_nasdaq_model_ready_contract_uses_sixty_complete_months(self) -> None:
        from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model

        rows = [
            {"observation_month": date, "qqq_price": 500.0 + index,
             "reconstructed_ttm_eps": 20.0, "trailing_pe": 20.0 + index / 20,
             "coverage_weight_pct": 97.0, "unmapped_weight_pct": 3.0,
             "data_quality": "reconstructed_actual"}
            for index, date in enumerate(pd.date_range("2021-08-01", periods=60, freq="MS"))
        ]
        model = build_nasdaq100_valuation_read_model(
            monthly_rows=rows,
            ttm_evidence={"status": "READY", "current_ttm_eps": 20.0,
                          "coverage_weight_pct": 97.0, "unmapped_weight_pct": 3.0,
                          "eps_source_quality": "reconstructed_actual",
                          "eps_basis_date": "2026-07-01"},
            sep_rows=_sep_rows(), sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 700.0}],
        )

        self.assertEqual(model["multiple_regime"]["status"], "READY")
        self.assertEqual(model["multiple_regime"]["observation_count"], 60)
        self.assertIn("price_scenarios", model["index_scenario"])
        self.assertEqual(
            model["index_scenario"]["history_repair_action"],
            {
                "id": "repair_nasdaq100_history_119m",
                "label": "1·3·5년 적정구간 자료 보강",
                "detail": (
                    "60개월 rolling PER 사전 이력을 포함해 부족한 EPS와 "
                    "가격을 보강합니다."
                ),
                "months": 119,
                "enabled": True,
            },
        )
        self.assertEqual(
            model["earnings_scenario"]["eps_source"],
            "QQQ 구성종목 실제 희석 EPS 재구성",
        )
        self.assertEqual(
            model["earnings_scenario"]["eps_source_quality"],
            "reconstructed_actual",
        )
        self.assertEqual(
            model["earnings_scenario"]["eps_basis_date"], "2026-07-01"
        )

    def test_nasdaq_repair_action_is_exposed_only_while_blocked(self) -> None:
        from app.services.overview.nasdaq100_valuation import build_nasdaq100_valuation_read_model

        blocked = build_nasdaq100_valuation_read_model(
            monthly_rows=[
                {
                    "observation_month": "2026-07-01",
                    "qqq_price": 709.43,
                    "coverage_weight_pct": 94.47,
                    "unmapped_weight_pct": 5.53,
                    "data_quality": "blocked",
                    "error_msg": "INSUFFICIENT_EARNINGS_COVERAGE",
                }
            ],
            ttm_evidence={
                "status": "BLOCKED",
                "coverage_weight_pct": 94.47,
                "unmapped_weight_pct": 5.53,
                "error_code": "INSUFFICIENT_EARNINGS_COVERAGE",
            },
            sep_rows=_sep_rows(),
            sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 709.43}],
        )
        ready_rows = [
            {
                "observation_month": date,
                "qqq_price": 500.0 + index,
                "reconstructed_ttm_eps": 20.0,
                "trailing_pe": 20.0 + index / 20,
                "coverage_weight_pct": 97.0,
                "unmapped_weight_pct": 3.0,
                "data_quality": "reconstructed_actual",
            }
            for index, date in enumerate(pd.date_range("2021-08-01", periods=60, freq="MS"))
        ]
        ready = build_nasdaq100_valuation_read_model(
            monthly_rows=ready_rows,
            ttm_evidence={
                "status": "READY",
                "current_ttm_eps": 20.0,
                "coverage_weight_pct": 97.0,
                "unmapped_weight_pct": 3.0,
                "eps_source_quality": "reconstructed_actual",
            },
            sep_rows=_sep_rows(),
            sep_history_rows=_sep_rows(),
            current_prices=[{"symbol": "QQQ", "latest_date": "2026-07-10", "price": 700.0}],
        )

        self.assertEqual(
            blocked["coverage"]["repair_action"],
            {
                "id": "repair_nasdaq100_60m",
                "label": "60개월 가치평가 자료 보강",
                "detail": "누락된 구성 종목 EPS와 가격 이력을 보강한 뒤 다시 계산합니다.",
                "enabled": True,
            },
        )
        self.assertNotIn("repair_action", ready["coverage"])

    def test_combined_model_keeps_sp500_payload_and_isolates_stock_failure(self) -> None:
        from app.services.overview.market_context_valuation import build_market_context_valuation_read_model

        sp500 = {
            "status": "READY",
            "instrument": {"id": "sp500", "label": "S&P 500"},
            "marker": "unchanged",
        }
        with patch(
            "app.services.overview.market_context_valuation.build_sp500_valuation_read_model",
            return_value=sp500,
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_valuation_read_model",
            side_effect=RuntimeError("db unavailable"),
        ) as stock_builder, patch(
            "app.services.overview.market_context_valuation.build_us_stock_turnaround_read_model",
            return_value={"status": "ERROR", "reason": "turnaround unavailable"},
        ):
            model = build_market_context_valuation_read_model(
                selected_symbol="AAPL",
                search_query="apple",
            )

        self.assertEqual(model["schema_version"], "market_context_valuation_v5")
        self.assertEqual(set(model["instruments"]), {"sp500", "us_stock"})
        self.assertEqual(model["instruments"]["sp500"], sp500)
        self.assertEqual(model["instruments"]["us_stock"]["status"], "ERROR")
        stock_builder.assert_called_once_with(
            selected_symbol="AAPL",
            search_query="apple",
        )

    def test_combined_model_preserves_per_fields_and_isolates_turnaround_failure(self) -> None:
        from app.services.overview.market_context_valuation import build_market_context_valuation_read_model

        per = {
            "schema_version": "us_stock_valuation_v1",
            "status": "READY",
            "selection": {"symbol": "AAPL"},
            "multiple_regime": {"status": "READY", "current_pe": 31.5},
            "marker": {"nested": "unchanged"},
        }
        with patch(
            "app.services.overview.market_context_valuation.build_sp500_valuation_read_model",
            return_value={"status": "READY", "instrument": {"id": "sp500"}},
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_valuation_read_model",
            return_value=per,
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_turnaround_read_model",
            side_effect=RuntimeError("statement schema unavailable"),
        ):
            model = build_market_context_valuation_read_model(selected_symbol="AAPL")

        stock = model["instruments"]["us_stock"]
        for key, value in per.items():
            self.assertEqual(stock[key], value)
        self.assertEqual(stock["turnaround_analysis"]["status"], "ERROR")
        self.assertEqual(stock["recommended_analysis"], "per")

    def test_combined_model_recommends_turnaround_without_positive_ready_per(self) -> None:
        from app.services.overview.market_context_valuation import build_market_context_valuation_read_model

        per = {
            "status": "NOT_APPLICABLE",
            "selection": {"symbol": "RIVN"},
            "multiple_regime": {"status": "BLOCKED", "current_pe": None},
            "instrument": {
                "id": "us_stock",
                "label": "미국 개별주식",
                "proxy_symbol": None,
                "price_label": "선택 종목 주가",
                "multiple_label": "후행 PER",
                "method_label": "기업 자체 이력 기반",
            },
        }
        turnaround = {"status": "READY", "selection": {"symbol": "RIVN"}}
        with patch(
            "app.services.overview.market_context_valuation.build_sp500_valuation_read_model",
            return_value={"status": "READY", "instrument": {"id": "sp500"}},
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_valuation_read_model",
            return_value=per,
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_turnaround_read_model",
            return_value=turnaround,
        ) as turnaround_builder:
            model = build_market_context_valuation_read_model(selected_symbol="RIVN")

        stock = model["instruments"]["us_stock"]
        self.assertEqual(stock["turnaround_analysis"], turnaround)
        self.assertEqual(stock["recommended_analysis"], "turnaround")
        turnaround_builder.assert_called_once_with(
            selected_symbol="RIVN",
            per_model=per,
        )

    def test_combined_model_exposes_one_selected_stock_freshness_contract(self) -> None:
        from app.services.overview.market_context_valuation import (
            build_market_context_valuation_read_model,
        )

        per = {
            "status": "NOT_APPLICABLE",
            "selection": {
                "symbol": "NET",
                "name": "Cloudflare Inc",
                "cik": None,
                "latest_price_date": "2026-07-07",
            },
            "multiple_regime": {"status": "INSUFFICIENT_HISTORY", "current_pe": None},
        }
        turnaround = {
            "status": "READY",
            "coverage": {
                "profile_basis_date": "2026-02-04",
                "price_basis_date": "2026-07-07",
                "statement_period_end": "2026-03-31",
                "statement_available_at": "2026-05-08",
                "statement_core_missing": False,
            },
            "collection_plan": {"scopes": []},
        }
        with patch(
            "app.services.overview.market_context_valuation.build_sp500_valuation_read_model",
            return_value={"status": "READY", "instrument": {"id": "sp500"}},
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_valuation_read_model",
            return_value=per,
        ), patch(
            "app.services.overview.market_context_valuation.build_us_stock_turnaround_read_model",
            return_value=turnaround,
        ):
            model = build_market_context_valuation_read_model(selected_symbol="NET")

        freshness = model["instruments"]["us_stock"]["data_freshness"]
        self.assertEqual(freshness["status"], "REFRESH_AVAILABLE")
        self.assertEqual(freshness["action"]["symbol"], "NET")
        self.assertEqual(freshness["action"]["scopes"], ["asset_profile", "prices"])

    def test_react_surface_has_stock_selector_search_and_status_contract(self) -> None:
        component = Path("app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx").read_text()
        helper = Path("app/web/overview/market_context_helpers.py").read_text()

        for token in (
            "instrument-selector",
            "미국 개별주식",
            "stock-search",
            "search_us_stock",
            "select_us_stock",
            "COLLECTABLE",
            "NOT_APPLICABLE",
        ):
            self.assertIn(token, component)
        self.assertNotIn("Nasdaq-100", component)
        self.assertNotIn("QQQ", component)
        self.assertIn("build_market_context_valuation_read_model", helper)

    def test_react_stock_refresh_is_explicit_and_relative_value_copy_is_clear(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        for token in (
            "refresh_us_stock_data",
            "Streamlit.setComponentValue",
            "최신 데이터로 다시 계산",
            "갱신 중",
            "상대가치 시나리오",
            "공식 적정가·목표주가·매매 신호가 아닙니다",
        ):
            self.assertIn(token, component)
        self.assertNotIn("collect_us_stock_valuation", component)
        self.assertNotIn("collect_us_stock_turnaround", component)
        self.assertNotIn("rows_written", component)

    def test_selected_stock_renders_one_header_refresh_action_before_analysis_selector(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        self.assertIn("function FreshnessBar", component)
        self.assertIn('emitEvent(action.id, { symbol: action.symbol })', component)
        self.assertEqual(component.count("<FreshnessBar"), 1)
        self.assertLess(
            component.index("<FreshnessBar"),
            component.index('className="analysis-selector"', component.index("<FreshnessBar")),
        )
        self.assertNotIn('className={`collection-result', component)

    def test_selected_stock_basis_labels_separate_price_statement_and_availability(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        self.assertIn("가격 기준일", component)
        self.assertIn("재무 기준일", component)
        self.assertIn("statement_available_at", component)
        self.assertIn("공개", component)

    def test_react_stock_scenario_shows_macro_company_growth_and_history_periods(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        for token in (
            "FOMC 거시 기준",
            "기업 초과성장",
            "예상 EPS",
            'key: "1y"',
            'key: "3y"',
            'key: "5y"',
        ):
            self.assertIn(token, component)

    def test_react_stock_history_renders_partial_timeline_without_connecting_gaps(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        for token in (
            'history.status === "PARTIAL"',
            "history.timeline",
            "contiguousHistorySegments",
            "계산 가능",
            "결측 월은 연결·보간하지 않습니다",
        ):
            self.assertIn(token, component)

    def test_react_selected_stock_has_symbol_keyed_per_turnaround_selector(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/MarketContextValuation.tsx"
        ).read_text()

        for token in (
            'import TurnaroundAnalysis',
            'type AnalysisChoice = "per" | "turnaround"',
            "recommended_analysis",
            "analysisBySymbol",
            "PER 상대가치",
            "전환 분석",
            "analysis-selector",
            "payload.selection?.symbol",
        ):
            self.assertIn(token, component)
        self.assertNotIn('emitEvent("switch_us_stock_analysis"', component)

    def test_turnaround_surface_has_gap_safe_shared_window_charts_and_no_pe_rendering(self) -> None:
        component = Path(
            "app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx"
        ).read_text()

        for token in (
            "전환 단계",
            "OPERATING_IMPROVEMENT",
            "CASH_FLOW_TURN",
            "PER_READY",
            "8분기",
            "12분기",
            "20분기",
            "contiguousTurnaroundSegments",
            "zero-axis",
            "그래프 1 · 영업 전환",
            "그래프 2 · 현금 전환",
            "생존·자본 위험",
            "현재 적용 가능한 가치평가 프레임",
        ):
            self.assertIn(token, component)
        self.assertNotIn("current_pe", component)
        self.assertNotIn("trailing_pe", component)
        self.assertNotIn("collect_us_stock_turnaround", component)

    def test_turnaround_rail_distinguishes_transition_from_established_state(self) -> None:
        source = Path(
            "app/web/streamlit_components/market_context_valuation/src/TurnaroundAnalysis.tsx"
        ).read_text()

        for token in (
            'type MilestoneDisplayState = "MET" | "ESTABLISHED" | "NOT_MET" | "UNKNOWN"',
            "매출 성장 / GP 개선",
            "영업 수익성 개선",
            "OCF 양수 지속",
            "FCF 양수",
            "EPS 양전 신호",
            "TTM EPS 양수",
            "PER 적용 가능",
            "이미 양수",
            "흑자 · 개선폭 미달",
            "분석 가능",
        ):
            self.assertIn(token, source)
        self.assertNotIn('label: "영업손실 축소"', source)
        self.assertNotIn('label: "PER READY"', source)

    def test_turnaround_established_state_has_distinct_non_failure_style(self) -> None:
        style = Path(
            "app/web/streamlit_components/market_context_valuation/src/style.css"
        ).read_text()

        for token in (
            ".milestone-established",
            ".milestone-established > span",
            ".milestone-established strong",
        ):
            self.assertIn(token, style)

    def test_turnaround_styles_stack_risk_cards_at_phone_width(self) -> None:
        style = Path(
            "app/web/streamlit_components/market_context_valuation/src/style.css"
        ).read_text()

        for token in (
            ".analysis-selector",
            ".freshness-bar",
            ".turnaround-milestone-rail",
            ".turnaround-risk-grid",
            ".turnaround-chart-grid",
            "@media (max-width: 460px)",
            ".turnaround-risk-grid { grid-template-columns: 1fr; }",
            ".freshness-bar { grid-template-columns: 1fr; }",
            ".freshness-bar button { width: 100%; }",
        ):
            self.assertIn(token, style)

    def test_overview_repair_facade_preserves_result_and_changes_job_name(self) -> None:
        from app.jobs.overview_actions import run_overview_nasdaq100_valuation_repair

        progress = Mock()
        with patch(
            "app.jobs.overview_actions.run_repair_nasdaq100_valuation_coverage",
            return_value={
                "job_name": "repair_nasdaq100_valuation_coverage",
                "status": "partial_success",
                "rows_written": 70,
                "details": {"after": {"ready_months": 48}},
            },
        ) as runner:
            result = run_overview_nasdaq100_valuation_repair(
                months=60,
                progress_callback=progress,
            )

        runner.assert_called_once_with(months=60, progress_callback=progress)
        self.assertEqual(result["job_name"], "overview_nasdaq100_valuation_repair")
        self.assertEqual(result["details"]["after"]["ready_months"], 48)

    def test_overview_repair_facade_forwards_history_warmup_months(self) -> None:
        from app.jobs.overview_actions import run_overview_nasdaq100_valuation_repair

        with patch(
            "app.jobs.overview_actions.run_repair_nasdaq100_valuation_coverage",
            return_value={"status": "success", "details": {}},
        ) as runner:
            result = run_overview_nasdaq100_valuation_repair(months=119)

        runner.assert_called_once_with(months=119, progress_callback=None)
        self.assertEqual(result["details"]["requested_months"], 119)

    def test_market_context_search_and_selection_are_read_only_state_events(self) -> None:
        from app.web.overview import market_context_helpers

        state: dict[str, object] = {}
        run_action = Mock()
        rerun = Mock()

        searched = market_context_helpers._handle_market_context_valuation_event(
            {"event": {"id": "search_us_stock", "query": "apple", "nonce": 123}},
            state=state,
            run_action=run_action,
            rerun=rerun,
        )
        selected = market_context_helpers._handle_market_context_valuation_event(
            {"event": {"id": "select_us_stock", "symbol": "aapl", "nonce": 124}},
            state=state,
            run_action=run_action,
            rerun=rerun,
        )

        self.assertTrue(searched)
        self.assertTrue(selected)
        self.assertEqual(
            state[market_context_helpers.US_STOCK_SEARCH_QUERY_KEY], "apple"
        )
        self.assertEqual(
            state[market_context_helpers.US_STOCK_SELECTED_SYMBOL_KEY], "AAPL"
        )
        run_action.assert_not_called()
        self.assertEqual(rerun.call_count, 2)

    def test_market_context_unified_refresh_validates_selection_and_runs_once(self) -> None:
        from app.web.overview import market_context_helpers

        state: dict[str, object] = {
            market_context_helpers.US_STOCK_SELECTED_SYMBOL_KEY: "AAPL"
        }
        run_action = Mock(
            return_value={
                "job_name": "overview_us_stock_data_refresh",
                "status": "success",
                "rows_written": 168,
            }
        )
        store_result = Mock()
        clear_cache = Mock()
        rerun = Mock()
        event = {
            "event": {
                "id": "refresh_us_stock_data",
                "symbol": "AAPL",
                "nonce": 456,
            }
        }

        first = market_context_helpers._handle_market_context_valuation_event(
            event,
            state=state,
            run_action=run_action,
            store_result=store_result,
            clear_cache=clear_cache,
            rerun=rerun,
        )
        second = market_context_helpers._handle_market_context_valuation_event(
            event,
            state=state,
            run_action=run_action,
            store_result=store_result,
            clear_cache=clear_cache,
            rerun=rerun,
        )
        rejected = market_context_helpers._handle_market_context_valuation_event(
            {
                "event": {
                    "id": "refresh_us_stock_data",
                    "symbol": "MSFT",
                    "nonce": 457,
                }
            },
            state=state,
            run_action=run_action,
            store_result=store_result,
            clear_cache=clear_cache,
            rerun=rerun,
        )

        self.assertTrue(first)
        self.assertFalse(second)
        self.assertFalse(rejected)
        run_action.assert_called_once_with("AAPL")
        store_result.assert_called_once_with(run_action.return_value)
        clear_cache.assert_called_once_with()
        rerun.assert_called_once_with()

    def test_legacy_collection_events_and_analysis_switch_are_not_python_actions(self) -> None:
        from app.web.overview import market_context_helpers

        state: dict[str, object] = {
            market_context_helpers.US_STOCK_SELECTED_SYMBOL_KEY: "RIVN"
        }
        run_action = Mock(return_value={"status": "success", "rows_written": 44})
        clear_cache = Mock()
        rerun = Mock()

        legacy = market_context_helpers._handle_market_context_valuation_event(
            {
                "event": {
                    "id": "collect_us_stock_turnaround",
                    "symbol": "RIVN",
                    "nonce": 700,
                }
            },
            state=state,
            run_action=run_action,
            clear_cache=clear_cache,
            rerun=rerun,
        )
        local_switch = market_context_helpers._handle_market_context_valuation_event(
            {"event": {"id": "switch_us_stock_analysis", "analysis": "per", "nonce": 701}},
            state=state,
            run_action=run_action,
            clear_cache=clear_cache,
            rerun=rerun,
        )

        self.assertFalse(legacy)
        self.assertFalse(local_switch)
        run_action.assert_not_called()
        clear_cache.assert_not_called()
        rerun.assert_not_called()

    def test_collection_reflection_excludes_visible_row_diagnostics(self) -> None:
        from app.web.overview.market_context_helpers import (
            _us_stock_collection_reflection,
        )

        reflection = _us_stock_collection_reflection(
            {
                "status": "partial_success",
                "message": "시장 자료 반영 완료, SEC identity 확인 필요",
                "rows_written": 42,
            }
        )

        self.assertEqual(
            reflection,
            {
                "status": "partial_success",
                "message": "시장 자료 반영 완료, SEC identity 확인 필요",
            },
        )

    def test_old_nasdaq_repair_events_are_no_longer_user_actions(self) -> None:
        from app.web.overview import market_context_helpers

        handled = market_context_helpers._handle_market_context_valuation_event(
            {"event": {"id": "repair_nasdaq100_60m", "nonce": 999}},
            state={},
            run_action=Mock(),
            rerun=Mock(),
        )

        self.assertFalse(handled)

    def test_nasdaq_collection_job_reports_holdings_and_monthly_steps(self) -> None:
        from app.jobs.ingestion_jobs import run_collect_nasdaq100_valuation_context

        with patch("app.jobs.ingestion_jobs.ensure_nasdaq100_valuation_schemas"), \
             patch("app.jobs.ingestion_jobs.collect_and_store_qqq_sec_holdings", return_value={"rows_written": 505}), \
             patch("app.jobs.ingestion_jobs.materialize_and_store_nasdaq100_monthly", return_value={"rows_written": 17, "blocked_rows": 17}), \
             patch("app.jobs.ingestion_jobs.run_collect_ohlcv", return_value={"status": "success", "rows_written": 5, "message": "ok"}):
            result = run_collect_nasdaq100_valuation_context()

        self.assertEqual(result["status"], "success")
        self.assertEqual(result["rows_written"], 527)
        self.assertEqual(result["details"]["pipeline_type"], "nasdaq100_valuation_context")

    def test_automation_includes_daily_nasdaq_valuation_job(self) -> None:
        from app.jobs.overview_automation import OVERVIEW_AUTOMATION_JOB_SPECS

        spec = next(item for item in OVERVIEW_AUTOMATION_JOB_SPECS if item.job_id == "nasdaq100_valuation")
        self.assertEqual(spec.cadence_minutes, 24 * 60)
        self.assertFalse(spec.market_hours_only)


if __name__ == "__main__":
    unittest.main()
