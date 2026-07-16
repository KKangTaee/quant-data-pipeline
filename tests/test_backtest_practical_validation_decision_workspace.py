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


class PracticalValidationDecisionWorkspaceTests(unittest.TestCase):
    def _source(self) -> dict[str, object]:
        return {
            "selection_source_id": "source-grs-current",
            "title": "GRS Macro Top 3",
            "source_type": "single_strategy",
            "period": {"actual_start": "2016-01-29", "actual_end": "2026-07-15"},
        }

    def _validation(self) -> dict[str, object]:
        accepted = [
            {
                "root_issue_id": root_id,
                "title": title,
                "resolution_class": "accepted_limit",
                "criticality": "noncritical",
                "terminal_state": "open",
                "actionable_now": False,
                "derived_checks": [root_id],
            }
            for root_id, title in (
                ("historical_universe_coverage", "과거 universe와 상장폐지 반영 범위"),
                ("validation_method_strength", "Validation Method Strength"),
                ("construction_risk", "Construction Risk"),
                ("backtest_realism", "Backtest Realism"),
                ("stress_robustness", "Stress / Robustness"),
                ("provider_investability", "Provider Investability"),
            )
        ]
        final_decision = {
            "root_issue_id": "tax_account_scope",
            "title": "세금 / 계좌 적용 범위",
            "resolution_class": "final_decision",
            "criticality": "noncritical",
            "terminal_state": "open",
            "actionable_now": False,
            "derived_checks": ["tax_account_scope"],
        }
        return {
            "validation_id": "validation-grs-current",
            "selection_source_id": "source-grs-current",
            "validation_route": "READY_FOR_FINAL_REVIEW",
            "final_review_gate": {
                "route": "READY_WITH_REVIEW",
                "can_save_and_move": True,
                "blocking_modules": [],
                "review_modules": [],
            },
            "evidence_closure": {
                "issues": [*accepted, final_decision],
                "summary": {
                    "total": 7,
                    "unresolved_actionable_count": 0,
                    "critical_engineering_count": 0,
                    "missing_contract_count": 0,
                    "resolve_now_count": 0,
                    "engineering_required_count": 0,
                    "accepted_limit_count": 6,
                    "final_decision_count": 1,
                    "monitoring_transfer_count": 0,
                },
                "current_final_review_eligible": True,
            },
            "practical_validation_workspace": {
                "visible_criteria_detail_groups": [
                    {
                        "group_id": "source_replay",
                        "display_label": "Source & Replay",
                        "purpose": "같은 후보를 최신 데이터로 재현했는가?",
                        "criteria_cards": [
                            {
                                "label": "Latest Runtime Replay",
                                "status": "PASS",
                                "checked_evidence": "requested / actual period 일치",
                            }
                        ],
                    }
                ],
                "next_stage_action": {
                    "primary_action": {
                        "id": "save_and_move",
                        "label": "저장하고 Final Review로 이동",
                        "enabled": True,
                    },
                    "secondary_action": {
                        "id": "save_audit_only",
                        "label": "검증 결과 저장",
                        "enabled": True,
                    },
                },
            },
        }

    def test_ready_with_handoff_separates_limits_and_final_decision(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=self._validation(),
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "ready_with_handoff")
        self.assertEqual(model["validation_result_id"], "validation-grs-current")
        self.assertEqual(model["summary"]["resolve_now_count"], 0)
        self.assertEqual(model["summary"]["engineering_blocker_count"], 0)
        self.assertEqual(model["summary"]["accepted_limit_count"], 6)
        self.assertEqual(model["summary"]["final_decision_count"], 1)
        self.assertEqual(model["resolution_lanes"]["resolve_now"], [])
        self.assertEqual(len(model["resolution_lanes"]["final_review_handoff"]), 7)
        self.assertIn("Final Review로 이동할 수 있습니다", model["verdict"]["headline"])

    def test_source_required_disables_replay_and_save(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source={},
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result=None,
            validation_result=None,
            source_options=[],
        )

        self.assertEqual(model["state"], "source_required")
        self.assertFalse(model["actions"]["run_replay"]["enabled"])
        self.assertFalse(model["actions"]["save_audit_only"]["enabled"])
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])

    def test_replay_required_hides_result_and_save_actions(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result=None,
            validation_result=None,
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "replay_required")
        self.assertEqual(model["verified_findings"], [])
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])
        self.assertTrue(model["actions"]["run_replay"]["enabled"])

    def test_action_lane_contains_only_registered_current_actions(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"] = {
            "issues": [
                {
                    "root_issue_id": "pre_final_data_enrichment",
                    "title": "필수 provider 근거 보강",
                    "resolution_class": "resolve_now",
                    "criticality": "critical",
                    "terminal_state": "open",
                    "actionable_now": True,
                    "action_id": "run_practical_validation_provider_gap_collection",
                    "completion_criteria": "수집 후 replay와 새 validation 저장",
                },
                {
                    "root_issue_id": "unknown-action",
                    "title": "미구현 action",
                    "resolution_class": "engineering_required",
                    "criticality": "critical",
                    "terminal_state": "deferred",
                    "actionable_now": False,
                    "action_id": None,
                },
            ],
            "summary": {
                "unresolved_actionable_count": 1,
                "critical_engineering_count": 1,
                "missing_contract_count": 0,
                "resolve_now_count": 1,
                "engineering_required_count": 1,
                "accepted_limit_count": 0,
                "final_decision_count": 0,
                "monitoring_transfer_count": 0,
            },
        }
        validation["final_review_gate"]["can_save_and_move"] = False

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "resolution_required")
        self.assertEqual(
            [row["root_issue_id"] for row in model["resolution_lanes"]["resolve_now"]],
            ["pre_final_data_enrichment"],
        )
        self.assertEqual(
            [row["root_issue_id"] for row in model["resolution_lanes"]["engineering_required"]],
            ["unknown-action"],
        )
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])

    def test_explicit_measurement_is_one_caution_not_a_duplicate_handoff(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"] = {
            "issues": [
                {
                    "root_issue_id": "provider_liquidity_pressure",
                    "title": "유동성 여유",
                    "resolution_class": "accepted_limit",
                    "criticality": "noncritical",
                    "terminal_state": "open",
                    "actionable_now": False,
                    "measurement": {
                        "observed": 42.0,
                        "threshold": 30.0,
                        "unit": "%",
                        "as_of": "2026-07-15",
                    },
                }
            ],
            "summary": {
                "unresolved_actionable_count": 0,
                "critical_engineering_count": 0,
                "missing_contract_count": 0,
                "accepted_limit_count": 1,
            },
        }

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["summary"]["measured_caution_count"], 1)
        self.assertEqual(model["summary"]["accepted_limit_count"], 0)
        self.assertEqual(
            [row["root_issue_id"] for row in model["measured_cautions"]],
            ["provider_liquidity_pressure"],
        )
        self.assertEqual(model["resolution_lanes"]["final_review_handoff"], [])

    def test_method_strength_separates_computed_passes_from_remaining_review(
        self,
    ) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["validation_efficacy_audit"] = {
            "rows": [
                {
                    "Criteria": "Walk-forward temporal validation",
                    "Status": "REVIEW",
                    "Current": "REVIEW / windows=103",
                    "Evidence": "worst excess -4.46%",
                    "Next Action": "negative window 원인을 확인합니다.",
                },
                {
                    "Criteria": "OOS holdout validation",
                    "Status": "PASS",
                    "Current": "PASS / in=64 / out=63",
                    "Evidence": "out excess 144.32%",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "PASS",
                    "Current": "PASS / buckets=3 / months=126",
                    "Evidence": "worst excess 19.88%",
                },
            ]
        }

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        verified_titles = {row["title"] for row in model["verified_findings"]}
        method_issue = next(
            row
            for row in model["resolution_lanes"]["final_review_handoff"]
            if row["root_issue_id"] == "validation_method_strength"
        )
        self.assertIn("OOS holdout validation", verified_titles)
        self.assertIn("Regime split validation", verified_titles)
        self.assertIn("windows=103", method_issue["observed"])
        self.assertNotIn("근거 없음", method_issue["observed"])


if __name__ == "__main__":
    unittest.main()
