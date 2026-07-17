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
            "from app.services.backtest_portfolio_mix_readiness import weighted_strategy_role_flags",
            compare_source,
        )
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

        self.assertIn("1A. 검증할 후보 선택", source)
        self.assertIn("1B. 어떤 관점으로 검증할까요?", source)
        self.assertIn('aria-pressed={option.selected}', source)
        self.assertNotIn("disabled={option.selected || !option.eligible}", source)
        self.assertNotIn("disabled={option.selected}", source)
        self.assertIn(".pv2-candidate-section", style)
        self.assertIn(".pv2-policy-section", style)

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


if __name__ == "__main__":
    unittest.main()
