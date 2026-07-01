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


if __name__ == "__main__":
    unittest.main()
