from __future__ import annotations

import importlib.util
import unittest
from pathlib import Path
from types import ModuleType


REPO_ROOT = Path(__file__).resolve().parents[1]
SCRIPTS_DIR = REPO_ROOT / ".aiworkspace" / "plugins" / "quant-finance-workflow" / "scripts"


def _load_script(name: str) -> ModuleType:
    path = SCRIPTS_DIR / f"{name}.py"
    spec = importlib.util.spec_from_file_location(name, path)
    if spec is None or spec.loader is None:
        raise RuntimeError(f"cannot load script: {path}")
    module = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


class FinancePhaseBundleContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.bootstrap = _load_script("bootstrap_finance_phase_bundle")

    def test_phase_bundle_uses_current_six_file_contract(self) -> None:
        operations = self.bootstrap._build_operations(
            "document-governance-alignment",
            "Document Governance Alignment",
        )

        relative_paths = {
            path.relative_to(self.bootstrap.PHASES_DIR).as_posix()
            for path in operations
        }
        self.assertEqual(
            relative_paths,
            {
                "active/document-governance-alignment/PLAN.md",
                "active/document-governance-alignment/DESIGN.md",
                "active/document-governance-alignment/TASKS.md",
                "active/document-governance-alignment/STATUS.md",
                "active/document-governance-alignment/RISKS.md",
                "active/document-governance-alignment/INTEGRATION.md",
            },
        )

        status = next(content for path, content in operations.items() if path.name == "STATUS.md")
        self.assertIn("State: active", status)

    def test_phase_id_rejects_numbered_legacy_shape(self) -> None:
        with self.assertRaises(ValueError):
            self.bootstrap._build_operations("phase21", "Legacy Phase")


class FinanceHygieneContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        cls.hygiene = _load_script("check_finance_refinement_hygiene")

    def test_semantic_phase_folder_is_classified_as_phase_docs(self) -> None:
        path = ".aiworkspace/note/finance/phases/active/document-governance-alignment/PLAN.md"

        groups = self.hygiene._classify([path])

        self.assertEqual(groups["phase_docs"], [path])

    def test_ordinary_phase_or_task_closeout_does_not_require_index_or_root_logs(self) -> None:
        groups = self.hygiene._classify(
            [
                ".aiworkspace/note/finance/phases/active/document-governance-alignment/STATUS.md",
                ".aiworkspace/note/finance/tasks/active/example-task/STATUS.md",
                ".aiworkspace/note/finance/tasks/active/example-task/RUNS.md",
            ]
        )

        checks = self.hygiene._build_checks(groups)
        check_names = {check["name"] for check in checks}

        self.assertNotIn("active phase TODO synced", check_names)
        self.assertNotIn("index docs reviewed", check_names)
        self.assertNotIn("root concise logs reviewed", check_names)

    def test_generated_artifact_advisory_is_preserved(self) -> None:
        groups = self.hygiene._classify(
            [".aiworkspace/note/finance/run_history/BACKTEST_RUN_HISTORY.jsonl"]
        )

        checks = self.hygiene._build_checks(groups)
        generated_check = next(
            check for check in checks if check["name"] == "protected artifacts remain unstaged"
        )

        self.assertEqual(generated_check["ok"], "yes")

    def test_all_finance_registry_jsonl_files_are_classified_as_registries(self) -> None:
        paths = [
            ".aiworkspace/note/finance/registries/PORTFOLIO_SELECTION_SOURCES.jsonl",
            ".aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl",
        ]

        groups = self.hygiene._classify(paths)

        self.assertEqual(groups["registries"], paths)
        self.assertEqual(groups["other_files"], [])

    def test_staged_registry_is_reported_as_a_protected_artifact_violation(self) -> None:
        path = ".aiworkspace/note/finance/registries/PRACTICAL_VALIDATION_RESULTS.jsonl"
        groups = self.hygiene._classify([path])

        checks = self.hygiene._build_checks(groups, staged_paths={path})
        protected_check = next(
            check for check in checks if check["name"] == "protected artifacts remain unstaged"
        )

        self.assertEqual(protected_check["ok"], "no")
        self.assertIn(path, protected_check["detail"])


if __name__ == "__main__":
    unittest.main()
