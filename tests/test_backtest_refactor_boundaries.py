from __future__ import annotations

import unittest
from pathlib import Path


PROJECT_ROOT = Path(__file__).resolve().parents[1]


class BacktestRefactorBoundaryTests(unittest.TestCase):
    def test_backtest_page_uses_state_boundary_module(self) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_page.py").read_text()

        self.assertIn("from app.web.backtest_state import", source)
        self.assertNotIn(
            "from app.web.backtest_common import",
            source.split("from app.web.backtest_analysis import", 1)[0],
        )

    def test_backtest_state_exports_workflow_helpers(self) -> None:
        from app.web import backtest_state
        from app.web.backtest_workflow_routes import BACKTEST_STAGE_OPTIONS

        self.assertEqual(backtest_state.BACKTEST_WORKFLOW_PANEL_OPTIONS, BACKTEST_STAGE_OPTIONS)
        self.assertTrue(callable(backtest_state.init_backtest_state))
        self.assertTrue(callable(backtest_state.request_backtest_panel))
        self.assertTrue(callable(backtest_state.activate_backtest_workflow_panel))

    def test_backtest_formatters_are_streamlit_free(self) -> None:
        from app.web.backtest_formatters import (
            format_currency,
            format_percent,
            format_ratio,
            parse_manual_tickers,
        )

        self.assertEqual(parse_manual_tickers(" spy, QQQ, spy ,, GLD "), ["SPY", "QQQ", "GLD"])
        self.assertEqual(format_currency(1234.56), "$1,234.6")
        self.assertEqual(format_percent(0.1234), "12.34%")
        self.assertEqual(format_ratio(1.23456), "1.235")

        source = (PROJECT_ROOT / "app/web/backtest_formatters.py").read_text()
        self.assertNotIn("streamlit", source)

    def test_single_strategy_payload_normalization_is_service_owned(self) -> None:
        from app.services.backtest_single_payload import normalize_single_strategy_payload

        original = {
            "strategy_key": "gtaa",
            "tickers": ("SPY", "QQQ"),
            "start": "2020-01-01",
            "end": "2024-12-31",
        }

        normalized = normalize_single_strategy_payload(original, strategy_name="GTAA")

        self.assertIsNot(normalized, original)
        self.assertEqual(normalized["strategy_key"], "gtaa")
        self.assertEqual(normalized["strategy_name"], "GTAA")
        self.assertEqual(normalized["tickers"], ["SPY", "QQQ"])
        self.assertNotIn("strategy_name", original)

        runner_source = (PROJECT_ROOT / "app/web/backtest_single_runner.py").read_text()
        self.assertIn("from app.services.backtest_single_payload import normalize_single_strategy_payload", runner_source)
        self.assertIn("execution_payload = normalize_single_strategy_payload", runner_source)

    def test_portfolio_mix_role_flags_are_service_owned(self) -> None:
        from app.services.backtest_portfolio_mix_readiness import weighted_strategy_role_flags

        flags = weighted_strategy_role_flags(["GTAA", "Equal Weight", "Dual Momentum"])

        self.assertEqual(flags, {"gtaa": True, "equal_weight": True})
        self.assertEqual(
            weighted_strategy_role_flags(["Risk Parity Trend"]),
            {"gtaa": False, "equal_weight": False},
        )

        compare_source = (PROJECT_ROOT / "app/web/backtest_compare/page.py").read_text()
        self.assertIn(
            "from app.services.backtest_portfolio_mix_readiness import (",
            compare_source,
        )
        self.assertIn("weighted_strategy_role_flags,", compare_source)
        self.assertIn("return weighted_strategy_role_flags(strategy_names)", compare_source)
        self.assertTrue((PROJECT_ROOT / "app/web/backtest_compare/__init__.py").exists())
        self.assertTrue((PROJECT_ROOT / "app/web/backtest_compare/weight_builder.py").exists())

    def test_practical_validation_status_policy_is_service_owned(self) -> None:
        from app.services.backtest_validation_status_policy import (
            STATUS_RANK,
            normalize_validation_status,
            worst_validation_status,
        )

        self.assertEqual(normalize_validation_status(True), "PASS")
        self.assertEqual(normalize_validation_status("FALSE"), "NEEDS_INPUT")
        self.assertEqual(normalize_validation_status("unknown-status"), "NOT_RUN")
        self.assertGreater(STATUS_RANK["BLOCKED"], STATUS_RANK["PASS"])
        self.assertEqual(worst_validation_status(["PASS", "REVIEW", "BLOCKED"]), "BLOCKED")

        modules_source = (PROJECT_ROOT / "app/services/backtest_practical_validation_modules.py").read_text()
        self.assertIn("from app.services.backtest_validation_status_policy import", modules_source)
        self.assertNotIn("STATUS_RANK = {", modules_source)

    def test_final_review_selected_route_policy_is_service_owned(self) -> None:
        from app.services.backtest_final_review_policy import build_selected_route_preflight_from_packet

        packet = {
            "selection_gate_policy_snapshot": {
                "select_allowed": True,
                "outcome": "READY",
                "suggested_decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                "next_action": "Save selected candidate.",
                "blockers": [],
                "review_required": ["Cost review"],
                "policy_rows": [{"Criteria": "Gate", "Status": "PASS"}],
            },
            "route": "INVESTABILITY_PACKET_READY",
            "select_ready": True,
            "open_review_items": ["Cost review"],
        }

        preflight = build_selected_route_preflight_from_packet(packet)

        self.assertEqual(preflight["route"], "SELECTED_ROUTE_PREFLIGHT_READY")
        self.assertTrue(preflight["select_allowed"])
        self.assertEqual(preflight["policy_outcome"], "READY")
        self.assertEqual(preflight["open_review_items"], 1)

        source = (PROJECT_ROOT / "app/services/backtest_selected_route_preflight.py").read_text()
        self.assertIn("from app.services.backtest_final_review_policy import", source)
        self.assertIn("build_selected_route_preflight_from_packet(packet)", source)

    def test_runtime_runner_catalog_identifies_strategy_owners(self) -> None:
        from app.runtime.backtest.runner_catalog import (
            get_runner_definition_for_display_name,
            known_strategy_keys,
            load_runner_callable,
            require_runner_definition,
        )

        self.assertIn("equal_weight", known_strategy_keys())
        self.assertIn("quality_snapshot_strict_annual", known_strategy_keys())
        self.assertEqual(
            require_runner_definition("risk_on_momentum_5d").runtime_module,
            "app.runtime.backtest.runners.risk_on_momentum",
        )
        self.assertEqual(
            get_runner_definition_for_display_name("GTAA").strategy_key,
            "gtaa",
        )
        for strategy_key in known_strategy_keys():
            definition = require_runner_definition(strategy_key)
            self.assertTrue(definition.runner_name.startswith("run_"))
            self.assertTrue(callable(load_runner_callable(definition)))

        execution_source = (PROJECT_ROOT / "app/services/backtest_execution.py").read_text()
        compare_source = (PROJECT_ROOT / "app/services/backtest_compare_catalog.py").read_text()
        self.assertIn("from app.runtime.backtest.runner_catalog import", execution_source)
        self.assertIn("from app.runtime.backtest.runner_catalog import", compare_source)

    def test_runtime_backtest_package_preserves_public_imports(self) -> None:
        from app.runtime import backtest
        from app.runtime.backtest import BacktestDataError, BacktestInputError

        self.assertIs(backtest.BacktestInputError, BacktestInputError)
        self.assertIs(backtest.BacktestDataError, BacktestDataError)

        for public_name in [
            "run_equal_weight_backtest_from_db",
            "run_gtaa_backtest_from_db",
            "run_global_relative_strength_backtest_from_db",
            "run_risk_parity_trend_backtest_from_db",
            "run_dual_momentum_backtest_from_db",
            "run_risk_on_momentum_5d_backtest_from_db",
            "run_quality_snapshot_strict_annual_backtest_from_db",
        ]:
            self.assertTrue(callable(getattr(backtest, public_name)))

        self.assertTrue((PROJECT_ROOT / "app/runtime/backtest").is_dir())
        self.assertTrue((PROJECT_ROOT / "app/runtime/backtest/facade.py").exists())
        self.assertTrue((PROJECT_ROOT / "app/runtime/backtest/common.py").exists())

    def test_runtime_stores_and_read_models_have_separate_boundaries(self) -> None:
        store_paths = [
            PROJECT_ROOT / "app/runtime/backtest/stores/run_history.py",
            PROJECT_ROOT / "app/runtime/backtest/stores/candidate_registry.py",
            PROJECT_ROOT / "app/runtime/backtest/stores/portfolio_selection.py",
            PROJECT_ROOT / "app/runtime/backtest/stores/portfolio_store.py",
            PROJECT_ROOT / "app/runtime/backtest/stores/final_selection_decisions.py",
        ]
        for path in store_paths:
            source = path.read_text()
            self.assertNotIn("import streamlit", source)
            self.assertNotIn("finance.engine", source)
            self.assertNotIn("finance.strategy", source)

        for path in [
            PROJECT_ROOT / "app/runtime/backtest/read_models/candidate_library.py",
            PROJECT_ROOT / "app/runtime/backtest/read_models/final_selected_portfolios.py",
        ]:
            source = path.read_text()
            self.assertNotRegex(source, r"^def append_", msg=f"{path} should not own JSONL append helpers")

    def test_validation_and_final_review_ui_packages_preserve_render_imports(self) -> None:
        from app.web.backtest_final_review import render_final_review_workspace
        from app.web.backtest_practical_validation import render_practical_validation_workspace

        self.assertTrue(callable(render_practical_validation_workspace))
        self.assertTrue(callable(render_final_review_workspace))
        self.assertTrue((PROJECT_ROOT / "app/web/backtest_practical_validation/page.py").exists())
        self.assertTrue((PROJECT_ROOT / "app/web/backtest_practical_validation/evidence_boards.py").exists())
        self.assertTrue((PROJECT_ROOT / "app/web/backtest_final_review/page.py").exists())
        self.assertTrue((PROJECT_ROOT / "app/web/backtest_final_review/decision_cockpit.py").exists())

    def test_practical_validation_page_uses_one_decision_workspace(self) -> None:
        page_source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/page.py"
        ).read_text()
        render_body = page_source.split(
            "def render_practical_validation_workspace", 1
        )[1]

        self.assertIn(
            "render_practical_validation_decision_workspace(",
            render_body,
        )
        self.assertIn(
            "build_practical_validation_decision_workspace(",
            render_body,
        )
        self.assertNotIn(
            "render_practical_validation_workspace_overview(",
            render_body,
        )
        self.assertNotIn(
            "_render_data_action_board(validation_result)",
            render_body,
        )
        self.assertNotIn(
            "_render_final_review_data_enrichment_handoff(source)",
            render_body,
        )
        self.assertNotIn(
            "_render_practical_validation_recovery_progress(",
            render_body,
        )
        self.assertNotIn("render_pv_command_center(", render_body)
        self.assertNotIn("PORTFOLIO_SELECTION_SOURCE_FILE", render_body)
        self.assertNotIn("PRACTICAL_VALIDATION_RESULT_FILE", render_body)
        self.assertNotIn("validation_rows", render_body)
        self.assertNotIn('title="검증 기준 상세"', render_body)
        self.assertIn("고급 설정과 원본 근거", render_body)
        self.assertIn(
            "render_practical_validation_decision_workspace_fallback(",
            render_body,
        )

    def test_practical_validation_workspace_panel_owns_first_read_surface(self) -> None:
        page_source = (PROJECT_ROOT / "app/web/backtest_practical_validation/page.py").read_text()
        panel_path = PROJECT_ROOT / "app/web/backtest_practical_validation/workspace_panel.py"

        self.assertTrue(panel_path.exists())
        panel_source = panel_path.read_text()

        self.assertIn(
            "from app.web.backtest_practical_validation.workspace_panel import",
            page_source,
        )
        self.assertIn(
            "render_practical_validation_decision_workspace_fallback",
            page_source,
        )
        self.assertNotIn(
            "def _render_practical_validation_decision_workspace_fallback",
            page_source,
        )
        self.assertIn(
            "def render_practical_validation_decision_workspace_fallback",
            panel_source,
        )
        fallback_body = panel_source.split(
            "def render_practical_validation_decision_workspace_fallback",
            1,
        )[1]
        self.assertIn('workspace.get("resolution_lanes")', fallback_body)
        self.assertNotIn(
            "is_practical_validation_fix_queue_available()",
            fallback_body,
        )
        self.assertNotIn("from app.web.backtest_practical_validation.page import", panel_source)

    def test_practical_validation_status_display_normalizes_raw_routes(self) -> None:
        from app.web.backtest_practical_validation.status_display import (
            validation_status_label,
            validation_status_tone,
        )

        self.assertEqual(validation_status_label("BLOCKED_FOR_FINAL_REVIEW"), "BLOCKED")
        self.assertEqual(validation_status_label("READY_WITH_REVIEW"), "REVIEW")
        self.assertEqual(validation_status_label("READY_FOR_FINAL_REVIEW"), "PASS")
        self.assertEqual(validation_status_label("NOT_APPLICABLE"), "NOT_APPLICABLE")
        self.assertEqual(validation_status_tone("BLOCKED_FOR_FINAL_REVIEW"), "danger")
        self.assertEqual(validation_status_tone("READY_WITH_REVIEW"), "warning")
        self.assertEqual(validation_status_tone("READY_FOR_FINAL_REVIEW"), "positive")

        page_source = (PROJECT_ROOT / "app/web/backtest_practical_validation/page.py").read_text()
        panel_source = (PROJECT_ROOT / "app/web/backtest_practical_validation/workspace_panel.py").read_text()

        self.assertIn("validation_status_tone as _status_tone", page_source)
        self.assertIn("validation_status_label", panel_source)
        self.assertNotIn("def _status_tone", page_source)
        self.assertNotIn("def _status_tone", panel_source)

    def test_practical_validation_entry_surface_removes_context_only_distractions(self) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_practical_validation/page.py").read_text()
        render_body = source.split("def render_practical_validation_workspace", 1)[1]

        self.assertNotIn('render_reference_contextual_help("practical_validation")', render_body)
        self.assertNotIn("_render_market_sentiment_context_overlay()", render_body)
        self.assertNotIn("검증 근거를 위한 후보 통제 화면", render_body)
        self.assertIn(
            "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?",
            render_body,
        )

    def test_practical_validation_react_is_intent_only(self) -> None:
        source = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/"
            "PracticalValidationDecisionWorkspace.tsx"
        ).read_text()

        for action in (
            "select_source",
            "select_profile_preset",
            "run_replay",
            "run_resolution_action",
            "save_audit_only",
            "save_and_move",
        ):
            self.assertIn(action, source)
        for forbidden in (
            "fetch(",
            "resolution_class ===",
            "can_save_and_move =",
            "run_provider_gap_collection(",
            "save_practical_validation_result(",
        ):
            self.assertNotIn(forbidden, source)

    def test_practical_validation_separates_candidate_and_policy_selection(self) -> None:
        source = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/"
            "PracticalValidationDecisionWorkspace.tsx"
        ).read_text()
        style = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/"
            "style.css"
        ).read_text()

        self.assertIn("1A. 검증할 후보", source)
        self.assertIn("1B. 어떤 관점으로 검증할까요?", source)
        self.assertIn('aria-pressed={option.selected}', source)
        self.assertNotIn("disabled={option.selected || !option.eligible}", source)
        self.assertNotIn("disabled={option.selected}", source)
        self.assertIn(".pv2-candidate-section", style)
        self.assertIn(".pv2-policy-section", style)

    def test_practical_validation_candidate_selector_is_collapsed_inline_list(
        self,
    ) -> None:
        source = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/"
            "PracticalValidationDecisionWorkspace.tsx"
        ).read_text()
        context = source.split('{surface === "context"', 1)[1].split(
            '{surface === "decision"', 1
        )[0]

        self.assertIn("candidateListOpen", context)
        self.assertIn("aria-expanded={candidateListOpen}", context)
        self.assertIn("pv2-candidate-list", context)
        self.assertNotIn('<div className="pv2-choice-grid">', context)

    def test_practical_validation_fallback_summarizes_selection_before_change_controls(
        self,
    ) -> None:
        source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/workspace_panel.py"
        ).read_text()
        body = source.split(
            "def _render_practical_validation_context_surface_fallback", 1
        )[1].split("\ndef ", 1)[0]

        self.assertIn('st.markdown("#### 1. 후보와 검증 기준")', body)
        self.assertIn('st.caption("검증 대상")', body)
        self.assertIn('st.caption("판정 기준")', body)
        self.assertIn(
            'with st.expander("1A. 후보 변경", expanded=False):', body
        )
        self.assertLess(
            body.index('st.caption("검증 대상")'),
            body.index('with st.expander("1A. 후보 변경"'),
        )

    def test_practical_validation_workspace_uses_fragment_interaction_boundary(
        self,
    ) -> None:
        source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/page.py"
        ).read_text()
        render_body = source.split(
            "def render_practical_validation_workspace", 1
        )[1]

        self.assertIn("@st.fragment", source)
        self.assertIn(
            "_render_practical_validation_decision_workspace_fragment(",
            render_body,
        )
        self.assertIn('rerun_scope="fragment"', source)
        self.assertIn('st.rerun(scope="app")', source)

    def test_practical_validation_context_is_outside_decision_fragment(self) -> None:
        source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/page.py"
        ).read_text()
        render_body = source.split(
            "def render_practical_validation_workspace", 1
        )[1].split("@st.fragment", 1)[0]
        fragment_body = source.split(
            "def _render_practical_validation_decision_workspace_fragment", 1
        )[1]

        self.assertIn('surface="context"', render_body)
        self.assertIn(
            "_render_practical_validation_decision_workspace_fragment(",
            render_body,
        )
        self.assertIn('surface="decision"', fragment_body)
        self.assertNotIn('surface="context"', fragment_body)

    def test_practical_validation_react_and_fallback_define_two_surfaces(
        self,
    ) -> None:
        react_source = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/"
            "PracticalValidationDecisionWorkspace.tsx"
        ).read_text()
        index_source = (
            PROJECT_ROOT
            / "app/web/components/practical_validation_decision_workspace/frontend/src/index.tsx"
        ).read_text()
        fallback_source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/workspace_panel.py"
        ).read_text()

        self.assertIn('surface: "context" | "decision"', index_source)
        self.assertIn('surface={args.surface ?? "decision"}', index_source)
        self.assertTrue(
            index_source.rstrip().endswith(
                'render(<Component />)'
            )
        )
        self.assertIn("data-surface={surface}", react_source)
        self.assertIn('surface: Literal["context", "decision"]', fallback_source)
        self.assertIn('if surface == "context"', fallback_source)

    def test_practical_validation_replay_is_consumed_before_fragment_projection(
        self,
    ) -> None:
        source = (
            PROJECT_ROOT / "app/web/backtest_practical_validation/page.py"
        ).read_text()
        callback_body = source.split(
            "def _consume_practical_validation_component_change", 1
        )[1].split("\ndef ", 1)[0]
        fragment_body = source.split(
            "def _render_practical_validation_decision_workspace_fragment", 1
        )[1]

        self.assertIn('rerun_scope="none"', callback_body)
        self.assertNotIn("_rerun_practical_validation_workspace", callback_body)
        self.assertIn("on_change=", fragment_body)

    def test_final_review_decision_brief_service_owns_domain_projection(self) -> None:
        service_source = (
            PROJECT_ROOT / "app/services/backtest_final_review_decision_brief.py"
        ).read_text()
        workspace_source = (
            PROJECT_ROOT
            / "app/web/components/final_review_investment_report/frontend/src/DecisionBriefWorkspace.tsx"
        ).read_text()
        chart_source = (
            PROJECT_ROOT
            / "app/web/components/final_review_investment_report/frontend/src/DecisionBriefCharts.tsx"
        ).read_text()

        for token in (
            "_build_eligibility",
            "_stored_curve_inputs",
            "_underwater_points",
            "_build_character_profile",
            "_build_review_pressure",
            "_deduplicate_primary_roles",
            "_build_decision_action",
        ):
            self.assertIn(token, service_source)
        react_source = workspace_source + chart_source
        for forbidden in (
            "select_allowed",
            "Total Balance",
            "running_peak",
            "threshold * 50",
            "append_current_final_selection_decision",
            "PRACTICAL_VALIDATION_RESULTS",
        ):
            self.assertNotIn(forbidden, react_source)

    def test_backtest_analysis_react_is_intent_only(self) -> None:
        source = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/"
            "BacktestAnalysisDecisionWorkspace.tsx"
        ).read_text()

        for action in (
            "select_workspace_kind",
            "select_strategy",
            "save_and_move",
        ):
            self.assertIn(action, source)
        for forbidden in (
            "fetch(",
            "promotion_decision ===",
            "append_backtest_run_history(",
            "save_saved_portfolio(",
            "_queue_candidate_review_draft(",
        ):
            self.assertNotIn(forbidden, source)

    def test_backtest_analysis_react_has_three_surfaces_and_resize_observer(
        self,
    ) -> None:
        component = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/"
            "BacktestAnalysisDecisionWorkspace.tsx"
        ).read_text()
        index = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/index.tsx"
        ).read_text()
        style = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css"
        ).read_text()

        self.assertIn("surface: WorkspaceSurface", index)
        self.assertIn('"context" | "settings" | "decision"', (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/types.ts"
        ).read_text())
        self.assertIn("data-surface={surface}", component)
        self.assertIn("ResizeObserver", index)
        self.assertIn("Streamlit.setFrameHeight", index)
        self.assertIn("@media (max-width: 760px)", style)

    def test_level1_result_workspace_is_dedicated_intent_only_and_responsive(
        self,
    ) -> None:
        root = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_result_workspace/frontend/src"
        )
        source = (root / "BacktestAnalysisResultWorkspace.tsx").read_text()
        chart = (root / "ResultWorkspaceChart.tsx").read_text()
        types = (root / "types.ts").read_text()
        css = (root / "style.css").read_text()
        index = (root / "index.tsx").read_text()

        for token in (
            "performance_summary",
            "strategy_series",
            "current_allocation",
            "target_allocation",
            "technical_handoff_readiness",
            "level2_validation_questions",
            "evidence_groups",
            "performance_rows",
            "holding_change_rows",
            "technical_appendix",
        ):
            self.assertIn(token, types)
        for token in (
            "timeline_dates",
            "desktop_x_ticks",
            "compact_x_ticks",
            "hover_rows",
            "contract_label",
            "next_window_label",
            "calculation_basis",
            "data_basis",
            "result_trace",
        ):
            self.assertIn(token, types)
        self.assertIn('emitIntent("save_and_move"', source)
        self.assertIn("<svg", chart)
        self.assertIn("<title>", chart)
        self.assertIn("<desc>", chart)
        for token in (
            "onPointerMove",
            "onPointerLeave",
            "bt1r-pointer-capture",
            "bt1r-crosshair",
            "bt1r-chart-tooltip",
        ):
            self.assertIn(token, chart)
        self.assertIn("bt1r-schedule-strip", source)
        self.assertIn("계산 및 데이터 기준", source)
        self.assertIn("원본 필드 보기", source)
        self.assertIn("ResizeObserver", index)
        self.assertIn("@media (max-width: 760px)", css)
        self.assertIn(".bt1r-workspace {", css)
        self.assertIn(".bt1r-chart-tooltip", css)
        self.assertIn(".bt1r-schedule-strip", css)
        self.assertIn("overflow-x: hidden", css)
        self.assertIn("min-width: 0", css)
        self.assertNotIn("benchmark_available", source)
        self.assertNotIn("Next Balance", source)
        self.assertNotIn("canHandoff =", source)
        self.assertNotIn("/ total", source)
        self.assertNotIn("value / 100", chart)

        fallback = (
            PROJECT_ROOT / "app/web/backtest_analysis_result_workspace_panel.py"
        ).read_text()
        self.assertIn(
            "def render_backtest_analysis_result_workspace_fallback", fallback
        )
        self.assertIn("계산 및 데이터 기준", fallback)
        self.assertIn("next_window_label", fallback)
        self.assertNotIn("build_next_step_readiness_evaluation", fallback)

    def test_result_route_hides_before_first_run_and_removes_legacy_expander(
        self,
    ) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_result_display.py").read_text()
        body = source.split("def _render_last_run", 1)[1].split("\ndef ", 1)[0]

        self.assertLess(
            body.index("if not bundle"),
            body.index("render_backtest_analysis_result_workspace"),
        )
        self.assertNotIn('st.expander("상세 근거"', body)
        self.assertNotIn("render_backtest_analysis_decision_surface", body)
        self.assertNotIn("def _render_real_money_details_legacy", source)

    def test_result_runtime_queues_single_preserves_mix_and_persists_run_identity(
        self,
    ) -> None:
        single = (PROJECT_ROOT / "app/web/backtest_single_strategy.py").read_text()
        runner = (PROJECT_ROOT / "app/web/backtest_single_runner.py").read_text()
        compare = (PROJECT_ROOT / "app/web/backtest_compare/page.py").read_text()
        history = (
            PROJECT_ROOT / "app/runtime/backtest/stores/run_history.py"
        ).read_text()
        candidate = (
            PROJECT_ROOT / "app/web/backtest_candidate_review_helpers.py"
        ).read_text()
        source = (
            PROJECT_ROOT / "app/services/backtest_practical_validation_source.py"
        ).read_text()

        self.assertIn("backtest_pending_single_run", single)
        self.assertIn("_render_last_run(is_running=bool(pending))", single)
        self.assertIn('bundle["meta"].setdefault("run_id"', runner)
        self.assertGreaterEqual(
            compare.count('weighted_bundle["meta"].setdefault("run_id"'), 2
        )
        weighted_failure = compare.split(
            'st.session_state.backtest_weighted_error = f"Weighted portfolio build failed:',
            1,
        )[1].split("return", 1)[0]
        self.assertNotIn("backtest_weighted_bundle = None", weighted_failure)
        history_record = history.split("record = {", 1)[1].split("\n    }", 1)[0]
        self.assertIn('"run_result_id": meta.get("run_id")', history_record)
        self.assertIn('"run_result_id": meta.get("run_id")', candidate)
        self.assertIn('"run_result_id": draft.get("run_result_id")', source)

    def test_backtest_analysis_light_cards_pin_readable_text_in_dark_theme(
        self,
    ) -> None:
        style = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/style.css"
        ).read_text()

        self.assertIn("color-scheme: light", style)
        self.assertIn(".bt1-workspace h1", style)
        self.assertIn(".bt1-workspace h2", style)
        self.assertIn(".bt1-workspace dd", style)
        self.assertIn("color: #152033", style)

    def test_backtest_analysis_context_is_outside_work_fragment(self) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_analysis.py").read_text()
        render_prefix = source.split(
            "def render_backtest_analysis_workspace", 1
        )[1].split("@st.fragment", 1)[0]
        fragment = source.split(
            "def _render_backtest_analysis_work_fragment", 1
        )[1]

        self.assertIn('surface="context"', render_prefix)
        self.assertIn("render_backtest_analysis_decision_surface()", fragment)
        self.assertNotIn('surface="context"', fragment)

    def test_single_strategy_change_marks_stale_without_clearing_bundle(
        self,
    ) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_single_strategy.py").read_text()
        body = source.split(
            "def _mark_last_run_stale_if_strategy_selection_changed", 1
        )[1].split("\ndef ", 1)[0]

        self.assertIn("backtest_last_result_requires_rerun", body)
        self.assertNotIn("backtest_last_bundle = None", body)

    def test_single_workspace_has_no_duplicate_strategy_or_variant_selectbox(
        self,
    ) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_single_strategy.py").read_text()
        settings_source = (
            PROJECT_ROOT / "app/web/backtest_single_settings_workspace.py"
        ).read_text()

        self.assertNotIn('st.selectbox(\n        "Strategy"', source)
        self.assertNotIn('f"{strategy_choice} Variant"', source)
        self.assertIn("build_current_single_settings_workspace(", source)
        self.assertIn("render_single_settings_fallback(", source)
        self.assertIn("build_single_settings_workspace", settings_source)

    def test_single_context_keeps_current_work_summary_for_mix_only(self) -> None:
        source = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/"
            "BacktestAnalysisDecisionWorkspace.tsx"
        ).read_text()

        current_work = source.split(
            '<aside className="bt1-current-work">', 1
        )[0]
        self.assertIn('workspace.workspace_kind === "portfolio_mix"', current_work)

    def test_single_strategy_forms_use_contextual_setting_labels(self) -> None:
        form_paths = [
            PROJECT_ROOT / "app/web/backtest_single_forms/equal_weight.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/gtaa.py",
            PROJECT_ROOT
            / "app/web/backtest_single_forms/global_relative_strength.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/risk_parity.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/dual_momentum.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/risk_on_momentum.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/strict_factor.py",
        ]

        for path in form_paths:
            source = path.read_text()
            self.assertNotIn('st.expander("Advanced Inputs"', source, path.name)
            self.assertIn("선택·보유 규칙", source, path.name)
        combined = "\n".join(path.read_text() for path in form_paths)
        self.assertNotIn('st.expander("Promotion Policy Signal"', combined)
        self.assertIn("비용·위험 기준", combined)

    def test_tactical_single_strategy_forms_share_korean_settings_hierarchy(
        self,
    ) -> None:
        form_paths = [
            PROJECT_ROOT / "app/web/backtest_single_forms/equal_weight.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/gtaa.py",
            PROJECT_ROOT
            / "app/web/backtest_single_forms/global_relative_strength.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/risk_parity.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/dual_momentum.py",
            PROJECT_ROOT / "app/web/backtest_single_forms/risk_on_momentum.py",
        ]
        section_labels = [
            "핵심 실행 설정",
            "투자 대상 Universe",
            "선택·보유 규칙",
            "비용·위험 기준",
        ]

        for path in form_paths:
            source = path.read_text()
            offsets = [source.index(label) for label in section_labels]
            self.assertEqual(offsets, sorted(offsets), path.name)
            self.assertIn(
                'form_submit_button("이 설정으로 백테스트 실행"',
                source,
                path.name,
            )
            self.assertIn("single_settings_section(", source, path.name)

    def test_strict_factor_settings_hierarchy_is_korean_first(self) -> None:
        path = PROJECT_ROOT / "app/web/backtest_single_forms/strict_factor.py"
        source = path.read_text()
        renderer_names = [
            "_render_quality_snapshot_form",
            "_render_quality_snapshot_strict_annual_form",
            "_render_quality_snapshot_strict_quarterly_prototype_form",
            "_render_value_snapshot_strict_quarterly_prototype_form",
            "_render_value_snapshot_strict_annual_form",
            "_render_quality_value_snapshot_strict_quarterly_prototype_form",
            "_render_quality_value_snapshot_strict_annual_form",
        ]
        section_labels = [
            "핵심 실행 설정",
            "투자 대상 Universe",
            "선택·보유 규칙",
            "비용·위험 기준",
        ]

        for index, renderer_name in enumerate(renderer_names):
            start = source.index(f"def {renderer_name}")
            end = (
                source.index(f"def {renderer_names[index + 1]}")
                if index + 1 < len(renderer_names)
                else source.index("__all__", start)
            )
            body = source[start:end]
            offsets = [body.index(label) for label in section_labels]
            self.assertEqual(offsets, sorted(offsets), renderer_name)
            self.assertIn("이 설정으로 백테스트 실행", body, renderer_name)

        for raw_copy in (
            "Strict annual multi-factor strategy.",
            "Hidden defaults in this first pass",
            "Current mode:",
            "Selected tickers (300):",
        ):
            self.assertNotIn(raw_copy, source)

    def test_common_universe_preview_is_compact_and_korean_first(self) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_common.py").read_text()
        body = source.split("def _render_ticker_preview", 1)[1].split(
            "\ndef ", 1
        )[0]

        self.assertIn("render_compact_ticker_summary(", body)
        self.assertNotIn("Selected tickers", body)
        self.assertNotIn("Head:", body)
        self.assertNotIn("Tail:", body)

    def test_single_result_uses_dedicated_workspace_without_collapsed_legacy(
        self,
    ) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_result_display.py").read_text()
        wrapper = source.split("def _render_last_run", 1)[1].split(
            "\ndef ", 1
        )[0]

        self.assertLess(
            wrapper.index("if not bundle"),
            wrapper.index("render_backtest_analysis_result_workspace"),
        )
        self.assertNotIn("render_backtest_analysis_decision_surface", wrapper)
        self.assertNotIn('st.expander("상세 근거"', wrapper)
        self.assertNotIn("_render_last_run_details(bundle)", wrapper)

    def test_portfolio_mix_workspace_uses_inner_mode_roles_and_common_decision(
        self,
    ) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_compare/page.py").read_text()
        builder = source.split(
            "def _render_weighted_portfolio_builder", 1
        )[1].split("\ndef ", 1)[0]
        react = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace/frontend/src/BacktestAnalysisDecisionWorkspace.tsx"
        ).read_text()

        self.assertIn("새 Mix 만들기", source)
        self.assertIn("저장된 Mix 불러오기", source)
        self.assertIn("mix_role_", builder)
        self.assertNotIn(
            "_render_weighted_portfolio_practical_validation_panel(weighted_bundle)",
            builder,
        )
        self.assertIn('emitIntent("select_mix_mode"', react)
        self.assertIn('emitIntent("save_mix"', react)

    def test_single_settings_fallback_uses_the_same_pure_schema_and_projector(
        self,
    ) -> None:
        source = (
            PROJECT_ROOT / "app/web/backtest_single_settings_workspace.py"
        ).read_text()

        self.assertIn(
            "from app.services.backtest_single_settings_workspace import (",
            source,
        )
        self.assertIn("build_single_settings_workspace", source)
        self.assertIn("project_single_settings_payload", source)
        self.assertIn("def render_single_settings_fallback", source)
        self.assertIn('"run_single_strategy"', source)
        self.assertNotIn("_render_equal_weight_form", source)
        self.assertNotIn("_render_gtaa_form", source)

    def test_single_settings_fallback_applies_preset_profiles_before_submit(
        self,
    ) -> None:
        source = (
            PROJECT_ROOT / "app/web/backtest_single_settings_workspace.py"
        ).read_text()
        body = source.split("def render_single_settings_fallback", 1)[1].split(
            "\n\n__all__", 1
        )[0]

        self.assertIn("def _apply_fallback_preset_profile", source)
        self.assertIn("apply_single_settings_preset(", source)
        self.assertIn("on_change=", body)
        self.assertIn("st.button(", body)
        self.assertNotIn("with st.form(", body)
        self.assertNotIn("st.form_submit_button(", body)

    def test_react_settings_surface_is_schema_driven_and_responsive(self) -> None:
        root = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace"
        )
        wrapper = (root / "component.py").read_text()
        types = (root / "frontend/src/types.ts").read_text()
        index = (root / "frontend/src/index.tsx").read_text()
        component = (
            root / "frontend/src/BacktestAnalysisDecisionWorkspace.tsx"
        ).read_text()
        style = (root / "frontend/src/style.css").read_text()

        self.assertIn('Literal["context", "settings", "decision"]', wrapper)
        self.assertIn('"settings"', types.split("WorkspaceSurface", 1)[1])
        self.assertIn("export type SettingsField", types)
        self.assertIn("export type SingleSettingsWorkspace", types)
        self.assertIn("SingleSettingsWorkspace", index)
        self.assertIn('surface === "settings"', component)
        for control in (
            'case "date"',
            'case "number"',
            'case "text"',
            'case "single_select"',
            'case "multi_select"',
            'case "segmented"',
            'case "toggle"',
        ):
            self.assertIn(control, component)
        self.assertIn("emitSettingsIntent(", component)
        self.assertIn('"select_strategy_variant"', component)
        self.assertIn('"run_single_strategy"', component)
        self.assertIn("bt1-settings-grid", style)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr))", style)
        responsive = style.split("@media (max-width: 760px)", 1)[1]
        self.assertIn(".bt1-settings-grid", responsive)
        self.assertIn("grid-template-columns: minmax(0, 1fr)", responsive)
        self.assertIn("ResizeObserver", index)
        self.assertNotIn("dangerouslySetInnerHTML", component)
        self.assertNotIn("execute_single_backtest", component)

    def test_react_settings_applies_python_owned_preset_profiles_without_strategy_rules(
        self,
    ) -> None:
        root = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace"
            / "frontend/src"
        )
        types = (root / "types.ts").read_text()
        component = (root / "BacktestAnalysisDecisionWorkspace.tsx").read_text()

        self.assertIn("export type SettingsPresetProfile", types)
        self.assertIn("preset_profiles: Record<string, SettingsPresetProfile>", types)
        self.assertIn("function applyPresetProfile", component)
        self.assertIn("workspace.preset_profiles", component)
        self.assertIn('fieldId === "preset_name"', component)
        self.assertIn('fieldId === "universe_mode"', component)
        self.assertIn('role="status"', component)
        for strategy_specific_rule in (
            "GTAA Evidence",
            "GTAA SPY Low-MDD Style Top-2 ADV20",
            "score_lookback_months: [1, 6]",
            "trend_filter_window: 250",
        ):
            self.assertNotIn(strategy_specific_rule, component)

    def test_react_multi_select_is_modifier_free_and_adaptive(self) -> None:
        root = (
            PROJECT_ROOT
            / "app/web/components/backtest_analysis_decision_workspace"
        )
        component = (
            root / "frontend/src/BacktestAnalysisDecisionWorkspace.tsx"
        ).read_text()
        style = (root / "frontend/src/style.css").read_text()

        self.assertNotIn("event.target.selectedOptions", component)
        self.assertNotIn("select[multiple]", style)
        for token in (
            "const MULTI_SELECT_COMPACT_LIMIT = 20",
            "const MULTI_SELECT_RESULT_LIMIT = 100",
            "function normalizeMultiSelectValues(",
            "function MultiSelectFieldControl(",
            'className="bt1-multi-select-compact"',
            'className="bt1-multi-select-search"',
            'role="checkbox"',
            'aria-pressed={selected}',
            "검색 결과 전체 선택",
            "bt1-selected-chip",
            ".slice(0, MULTI_SELECT_RESULT_LIMIT)",
        ):
            self.assertIn(token, component)
        for token in (
            ".bt1-multi-select-compact",
            "grid-template-columns: repeat(2, minmax(0, 1fr))",
            ".bt1-multi-select-results",
            "max-height: 280px",
            "overflow-y: auto",
            ".bt1-selected-chip",
            ":focus-visible",
            "overflow-wrap: anywhere",
        ):
            self.assertIn(token, style)
        self.assertIn('className="bt1-multi-select-option-label"', component)
        self.assertNotIn("repeat(auto-fit, minmax(140px, 1fr))", style)
        responsive = style.split("@media (max-width: 760px)", 1)[1]
        self.assertIn(".bt1-multi-select-compact", responsive)
        self.assertIn("@media (max-width: 520px)", style)
        compact_mobile = style.split("@media (max-width: 520px)", 1)[1]
        self.assertIn(".bt1-multi-select-compact", compact_mobile)
        self.assertIn(
            "grid-template-columns: minmax(0, 1fr)",
            compact_mobile,
        )

    def test_primary_single_settings_route_has_no_legacy_form_dispatch(self) -> None:
        source = (PROJECT_ROOT / "app/web/backtest_single_strategy.py").read_text()
        render_body = source.split("def render_single_strategy_workspace", 1)[1]

        self.assertIn("build_current_single_settings_workspace", source)
        self.assertIn("render_backtest_analysis_decision_workspace", source)
        self.assertIn('surface="settings"', source)
        self.assertIn("consume_single_settings_intent", source)
        self.assertIn("render_single_settings_fallback", source)
        self.assertIn("_handle_backtest_run", source)
        self.assertNotIn("from app.web.backtest_single_forms import", source)
        for legacy_renderer in (
            "_render_equal_weight_form",
            "_render_gtaa_form",
            "_render_global_relative_strength_form",
            "_render_risk_parity_form",
            "_render_dual_momentum_form",
            "_render_risk_on_momentum_5d_form",
            "_render_single_strategy_family_form",
        ):
            self.assertNotIn(legacy_renderer, render_body)


if __name__ == "__main__":
    unittest.main()
