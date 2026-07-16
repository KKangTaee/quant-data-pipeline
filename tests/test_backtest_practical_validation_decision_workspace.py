from __future__ import annotations

import unittest
from importlib import import_module


class PracticalValidationTruthContractTests(unittest.TestCase):
    def test_single_component_weight_is_not_mix_concentration(self) -> None:
        from app.services.backtest_construction_risk_audit import (
            build_construction_risk_audit,
        )

        audit = build_construction_risk_audit(
            {
                "metrics": {
                    "active_components": 1,
                    "weight_total": 100.0,
                    "max_weight": 100.0,
                },
                "validation_profile": {
                    "thresholds": {"max_weight_review": 75.0},
                },
            }
        )
        row = next(
            row
            for row in audit["rows"]
            if row["Criteria"] == "Component weight concentration"
        )

        self.assertEqual(row["Status"], "NOT_APPLICABLE")
        self.assertTrue(row["Ready"])
        self.assertIn("단일 component", row["Current"])
        self.assertNotIn("Final Review 근거에 남깁니다", row["Next Action"])

    def test_pre_final_enrichment_is_resolve_now_only_with_registered_handler(
        self,
    ) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )

        contract = build_evidence_closure_contract(
            {
                "validation_id": "validation-action",
                "selection_source_id": "source-action",
                "validation_modules": [
                    {
                        "module_id": "pre_final_data_enrichment",
                        "label": "승격 전 필수 데이터 보강",
                        "status": "NEEDS_INPUT",
                        "requirement": "REQUIRED",
                        "review_role": "final_readiness_blocker",
                        "action_id": "run_practical_validation_provider_gap_collection",
                        "gate_effect": "Blocks Final Review",
                    }
                ],
            }
        )

        issue = contract["issues"][0]
        self.assertEqual(issue["resolution_class"], "resolve_now")
        self.assertTrue(issue["actionable_now"])
        self.assertEqual(
            issue["action_id"],
            "run_practical_validation_provider_gap_collection",
        )
        self.assertEqual(contract["summary"]["resolve_now_count"], 1)
        self.assertEqual(contract["summary"]["unresolved_actionable_count"], 1)

    def test_closure_summary_separates_handoff_classes(self) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )

        modules = [
            {
                "module_id": module_id,
                "label": module_id,
                "status": "REVIEW",
                "requirement": "REQUIRED",
                "review_role": "pv_practical_caution",
            }
            for module_id in (
                "validation_efficacy",
                "construction_risk",
                "backtest_realism",
                "stress_robustness",
                "provider_investability",
                "source_integrity",
            )
        ]
        modules.append(
            {
                "module_id": "tax_account_scope",
                "label": "Tax / Account Scope",
                "status": "REVIEW",
                "requirement": "REFERENCE",
                "review_role": "final_decision_input",
            }
        )

        summary = build_evidence_closure_contract(
            {
                "validation_id": "validation-grs-current",
                "selection_source_id": "source-grs-current",
                "validation_modules": modules,
            }
        )["summary"]

        self.assertEqual(summary["accepted_limit_count"], 6)
        self.assertEqual(summary["final_decision_count"], 1)
        self.assertEqual(summary["resolve_now_count"], 0)
        self.assertEqual(summary["critical_engineering_count"], 0)

    def test_registered_provider_action_resolves_to_callable_python_handler(
        self,
    ) -> None:
        from app.services.backtest_evidence_closure import (
            ACTION_HANDLER_CONTRACTS,
        )

        contract = ACTION_HANDLER_CONTRACTS[
            "run_practical_validation_provider_gap_collection"
        ]
        module_name, function_name = str(contract["handler"]).split(":", 1)
        handler = getattr(import_module(module_name), function_name)

        self.assertTrue(callable(handler))


if __name__ == "__main__":
    unittest.main()
