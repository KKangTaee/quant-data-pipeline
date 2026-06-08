from __future__ import annotations

import importlib.util
import subprocess
import sys
import tempfile
import unittest
from pathlib import Path


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPT_PATH = REPO_ROOT / ".aiworkspace/plugins/quant-finance-workflow/scripts/check_strategy_promotion_contract.py"
TEMPLATE_PATH = REPO_ROOT / ".aiworkspace/note/finance/reports/backtests/templates/STRATEGY_PROMOTION_CONTRACT_TEMPLATE.md"


def _load_contract_checker():
    spec = importlib.util.spec_from_file_location("check_strategy_promotion_contract", SCRIPT_PATH)
    module = importlib.util.module_from_spec(spec)
    assert spec.loader is not None
    spec.loader.exec_module(module)
    return module


class StrategyPromotionContractCheckerTests(unittest.TestCase):
    def test_template_has_all_required_strategy_promotion_sections(self) -> None:
        checker = _load_contract_checker()

        report = checker.build_report(TEMPLATE_PATH)

        self.assertTrue(report["ok"])
        self.assertEqual(report["missing_required_sections"], [])
        self.assertEqual(report["missing_state_tokens"], [])

    def test_incomplete_contract_reports_missing_required_sections(self) -> None:
        checker = _load_contract_checker()
        with tempfile.TemporaryDirectory() as tmp:
            contract_path = Path(tmp) / "incomplete_contract.md"
            contract_path.write_text(
                "\n".join(
                    [
                        "# Incomplete Strategy Promotion Contract",
                        "",
                        "## Metadata",
                        "",
                        "| Field | Value |",
                        "|---|---|",
                        "| Strategy Family | Example |",
                    ]
                ),
                encoding="utf-8",
            )

            report = checker.build_report(contract_path)

        self.assertFalse(report["ok"])
        self.assertIn("Strategy Identity", report["missing_required_sections"])
        self.assertIn("Practical Validation Source Payload Conditions", report["missing_required_sections"])
        self.assertIn("NOT_RUN", report["missing_state_tokens"])

    def test_cli_returns_failure_for_incomplete_contract(self) -> None:
        with tempfile.TemporaryDirectory() as tmp:
            contract_path = Path(tmp) / "incomplete_contract.md"
            contract_path.write_text("# Incomplete\n\n## Metadata\n", encoding="utf-8")

            proc = subprocess.run(
                [sys.executable, str(SCRIPT_PATH), str(contract_path)],
                cwd=REPO_ROOT,
                capture_output=True,
                text=True,
                check=False,
            )

        self.assertEqual(proc.returncode, 1)
        self.assertIn("Strategy Promotion Contract Check", proc.stdout)
        self.assertIn("Result: FAIL", proc.stdout)
        self.assertIn("Strategy Identity", proc.stdout)


if __name__ == "__main__":
    unittest.main()
