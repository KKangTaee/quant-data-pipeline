from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(__file__).resolve().parents[1]
DOCS = ROOT / ".aiworkspace" / "note" / "finance" / "docs"


class PortfolioMonitoringDocsTests(unittest.TestCase):
    def _read(self, path: Path) -> str:
        self.assertTrue(path.exists(), f"missing durable document: {path}")
        return path.read_text(encoding="utf-8")

    def test_architecture_names_route_owners_and_product_boundaries(self) -> None:
        text = self._read(DOCS / "architecture" / "PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md")
        for phrase in (
            "portfolio_monitoring_workspace_v2",
            "app/web/final_selected_portfolio_dashboard.py",
            "app/services/portfolio_monitoring/",
            "PortfolioMonitoringWorkbench.tsx",
            "Streamlit",
            "React",
            "provider fetch",
            "broker order",
            "auto rebalance",
        ):
            self.assertIn(phrase, text)

    def test_data_contract_names_tables_valuation_and_pit_semantics(self) -> None:
        text = self._read(DOCS / "data" / "PORTFOLIO_MONITORING_DATA_CONTRACT.md")
        for phrase in (
            "monitoring_portfolio_group",
            "monitoring_portfolio_item",
            "monitoring_portfolio_command",
            "monitoring_security_position_event",
            "monitoring_diagnosis_snapshot",
            "monitoring_risk_calibration_artifact",
            "integer shares",
            "raw close",
            "split",
            "cash dividend",
            "common basis date",
            "point-in-time",
            "SUPPRESSED",
            "READY",
        ):
            self.assertIn(phrase, text)

    def test_runbook_has_safe_migration_rollback_and_qa_contract(self) -> None:
        text = self._read(DOCS / "runbooks" / "PORTFOLIO_MONITORING_MIGRATION_AND_QA.md")
        for phrase in (
            "finance_meta_portfolio_monitoring_qa",
            "finance_meta",
            "ensure_schema",
            "default group",
            "legacy",
            "checksum",
            "rollback",
            "Browser QA",
            "1440",
            "760",
            "420",
            "unstaged",
        ):
            self.assertIn(phrase, text)

    def test_maps_and_flows_link_the_canonical_documents(self) -> None:
        project_map = self._read(DOCS / "PROJECT_MAP.md")
        roadmap = self._read(DOCS / "ROADMAP.md")
        backtest_flow = self._read(DOCS / "flows" / "BACKTEST_UI_FLOW.md")
        selection_flow = self._read(DOCS / "flows" / "PORTFOLIO_SELECTION_FLOW.md")
        self.assertIn("PORTFOLIO_MONITORING_REACT_COMMAND_CENTER.md", project_map)
        self.assertIn("Portfolio Monitoring React Command Center", roadmap)
        self.assertIn("Final Review", backtest_flow)
        self.assertIn("Portfolio Monitoring", backtest_flow)
        self.assertIn("monitoring_candidate", selection_flow)
        self.assertIn("Portfolio Monitoring", selection_flow)


if __name__ == "__main__":
    unittest.main()
