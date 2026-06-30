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


if __name__ == "__main__":
    unittest.main()
