from __future__ import annotations

import sys
import unittest


class BacktestAnalysisResearchBoardTests(unittest.TestCase):
    def test_research_board_is_streamlit_free_and_hidden_by_default(self) -> None:
        sys.modules.pop("streamlit", None)

        from app.services.backtest_analysis_research_board import build_backtest_analysis_research_board

        board = build_backtest_analysis_research_board()

        self.assertNotIn("streamlit", sys.modules)
        self.assertEqual(board["board_id"], "backtest_analysis_research_reference_board_v1")
        self.assertEqual(board["primary_flow_priority"], "strategy_execution_first")
        self.assertFalse(board["default_visible"])
        self.assertFalse(board["writes_registry"])
        self.assertFalse(board["writes_saved_setup"])
        self.assertFalse(board["writes_run_history"])
        self.assertFalse(board["writes_generated_artifacts"])
        self.assertIn("전략 실행", board["summary"])
        self.assertIn("기본 화면", board["summary"])

    def test_research_board_classifies_all_3a_to_4b_items(self) -> None:
        from app.services.backtest_analysis_research_board import build_backtest_analysis_research_board

        board = build_backtest_analysis_research_board()
        rows_by_key = {row["key"]: row for row in board["rows"]}

        self.assertEqual(
            set(rows_by_key),
            {
                "reference_help",
                "strategy_evidence_inventory",
                "strict_annual_etf_bridge",
                "risk_on_momentum_governance",
                "etf_evidence_expansion",
                "etf_current_anchor_workbench",
                "etf_rerun_matrix_workbench",
            },
        )
        self.assertEqual(rows_by_key["reference_help"]["default_display"], "접힘")
        self.assertEqual(rows_by_key["strategy_evidence_inventory"]["default_display"], "숨김")
        self.assertEqual(rows_by_key["strict_annual_etf_bridge"]["recommended_location"], "Reference / 문서")
        self.assertEqual(rows_by_key["risk_on_momentum_governance"]["recommended_location"], "전략 상세 / Reference")
        self.assertEqual(rows_by_key["etf_rerun_matrix_workbench"]["classification"], "고급 전략 실험")
        self.assertTrue(rows_by_key["etf_rerun_matrix_workbench"]["strategy_development_useful"])
        self.assertFalse(rows_by_key["strategy_evidence_inventory"]["required_for_backtest_execution"])

    def test_research_board_rows_are_returned_as_copies(self) -> None:
        from app.services.backtest_analysis_research_board import build_backtest_analysis_research_board

        first = build_backtest_analysis_research_board()
        first["rows"][0]["default_display"] = "mutated"

        fresh = build_backtest_analysis_research_board()

        self.assertNotEqual(fresh["rows"][0]["default_display"], "mutated")


if __name__ == "__main__":
    unittest.main()
