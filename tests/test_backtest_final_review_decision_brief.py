from __future__ import annotations

import json
import unittest
from copy import deepcopy


class FinalReviewDecisionBriefContractTests(unittest.TestCase):
    def _inputs(self) -> dict[str, object]:
        return {
            "source": {
                "source_id": "validation-grs-current",
                "source_type": "practical_validation_result",
                "source_title": "GRS current candidate",
                "updated_at": "2026-07-16T09:00:00+09:00",
            },
            "validation": {
                "validation_id": "validation-grs-current",
                "selection_source_id": "selection-grs-current",
                "evidence_closure": {
                    "summary": {
                        "unresolved_actionable_count": 0,
                        "critical_engineering_count": 0,
                        "missing_contract_count": 0,
                    },
                    "issues": [],
                },
            },
            "paper_observation": {},
            "decision_evidence": {
                "suggested_decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
            },
            "investability_packet": {
                "checks": [
                    {"Check": "source", "Ready": True},
                    {"Check": "benchmark", "Ready": True},
                    {"Check": "cost", "Ready": True},
                    {"Check": "liquidity", "Ready": False},
                ],
                "selection_gate_policy_snapshot": {
                    "select_allowed": True,
                    "suggested_decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "blockers": [],
                    "review_required": [],
                },
            },
            "decision_id": "final-review-grs-current",
            "existing_decision_ids": set(),
        }

    def _build(self, inputs: dict[str, object] | None = None) -> dict[str, object]:
        from app.services.backtest_final_review_decision_brief import (
            build_final_review_decision_brief,
        )

        return build_final_review_decision_brief(**(inputs or self._inputs()))

    def test_decision_brief_has_v1_schema_without_investment_scores(self) -> None:
        brief = self._build()
        serialized = json.dumps(brief, ensure_ascii=False, sort_keys=True)

        self.assertEqual(brief["schema_version"], "decision_brief_v1")
        for forbidden in (
            "overall_score",
            "headline_scores",
            "investment_score",
            "monitoring_readiness_score",
            "투자 매력도",
            "Monitoring 준비도",
        ):
            self.assertNotIn(forbidden, serialized)

    def test_current_eligible_brief_has_zero_preselection_unknowns(self) -> None:
        brief = self._build()
        eligibility = brief["eligibility"]

        self.assertTrue(eligibility["eligible"])
        self.assertEqual(eligibility["unresolved_actionable_count"], 0)
        self.assertEqual(eligibility["critical_engineering_count"], 0)
        self.assertEqual(eligibility["missing_contract_count"], 0)
        self.assertEqual(eligibility["pre_selection_unresolved_count"], 0)
        self.assertNotIn("pre_selection_unresolved", brief["disclosures"])

    def test_unresolved_or_missing_contract_forces_level2_route(self) -> None:
        for count_key in (
            "unresolved_actionable_count",
            "critical_engineering_count",
            "missing_contract_count",
        ):
            with self.subTest(count_key=count_key):
                inputs = deepcopy(self._inputs())
                inputs["validation"]["evidence_closure"]["summary"][count_key] = 1

                brief = self._build(inputs)

                self.assertFalse(brief["eligibility"]["eligible"])
                self.assertGreater(brief["eligibility"]["pre_selection_unresolved_count"], 0)
                self.assertEqual(brief["verdict"]["route"], "RE_REVIEW_REQUIRED")
                self.assertFalse(brief["capabilities"]["can_select_for_monitoring"])

    def test_route_labels_preserve_canonical_persistence_values(self) -> None:
        brief = self._build()
        labels_by_route = {
            option["route"]: option["label"]
            for option in brief["decision_action"]["options"]
        }

        self.assertEqual(
            labels_by_route,
            {
                "SELECT_FOR_PRACTICAL_PORTFOLIO": "계속 추적",
                "HOLD_FOR_MORE_PAPER_TRACKING": "관찰 후 재검토",
                "REJECT_FOR_PRACTICAL_USE": "추적 대상에서 제외",
                "RE_REVIEW_REQUIRED": "Level2로 돌려보내기",
            },
        )

    def test_evidence_confidence_is_secondary_ready_check_metadata(self) -> None:
        ready_inputs = deepcopy(self._inputs())
        lower_inputs = deepcopy(self._inputs())
        lower_inputs["investability_packet"]["checks"][1]["Ready"] = False
        lower_inputs["investability_packet"]["checks"][2]["Ready"] = False

        ready_brief = self._build(ready_inputs)
        lower_brief = self._build(lower_inputs)

        self.assertEqual(ready_brief["evidence_confidence"]["value"], 75)
        self.assertEqual(ready_brief["evidence_confidence"]["ready_checks"], 3)
        self.assertEqual(ready_brief["evidence_confidence"]["total_checks"], 4)
        self.assertEqual(lower_brief["evidence_confidence"]["value"], 25)
        self.assertEqual(ready_brief["verdict"]["route"], lower_brief["verdict"]["route"])

    def test_root_issue_and_observation_primary_roles_are_unique(self) -> None:
        from app.services.backtest_final_review_decision_brief import (
            _deduplicate_primary_roles,
        )

        strengths, weaknesses, conditions = _deduplicate_primary_roles(
            strengths=[
                {
                    "observation_id": "drawdown-pressure",
                    "root_issue_id": "drawdown-root",
                    "primary_role": "strength",
                }
            ],
            weaknesses=[
                {
                    "observation_id": "drawdown-pressure",
                    "root_issue_id": "drawdown-root",
                    "primary_role": "weakness",
                }
            ],
            monitoring_conditions=[
                {
                    "observation_id": "drawdown-pressure",
                    "root_issue_id": "drawdown-root",
                    "primary_role": "monitoring",
                }
            ],
        )
        visible = [*strengths, *weaknesses, *conditions]
        stable_ids = [row.get("observation_id") or row.get("root_issue_id") for row in visible]

        self.assertEqual(stable_ids, ["drawdown-pressure"])
        self.assertEqual([row["primary_role"] for row in visible], ["monitoring"])

    def test_candidate_selector_projects_python_owned_selection_state(self) -> None:
        from app.services.backtest_final_review_decision_brief import (
            build_final_review_candidate_selector,
        )

        selector = build_final_review_candidate_selector(
            [
                {
                    "source_id": "source-a",
                    "validation_id": "validation-a",
                    "title": "Candidate A",
                    "source_type": "practical_validation_result",
                    "eligible": True,
                    "registry_path": "/protected/registry.jsonl",
                },
                {
                    "source_id": "source-b",
                    "validation_id": "validation-b",
                    "title": "Candidate B",
                    "source_type": "practical_validation_result",
                    "eligible": False,
                    "can_write": True,
                },
            ],
            active_source_id="source-b",
        )
        options = selector["options"]

        self.assertEqual([option["selected"] for option in options], [False, True])
        self.assertEqual(
            set(options[0]),
            {"source_id", "validation_id", "title", "source_type", "eligible", "selected"},
        )
        self.assertNotIn("registry", json.dumps(selector, ensure_ascii=False).lower())
        self.assertNotIn("write", json.dumps(selector, ensure_ascii=False).lower())

    def test_duplicate_decision_id_disables_recording_without_writing(self) -> None:
        inputs = self._inputs()
        inputs["existing_decision_ids"] = {inputs["decision_id"]}

        brief = self._build(inputs)

        self.assertTrue(all(not option["recordable"] for option in brief["decision_action"]["options"]))
        self.assertTrue(
            all("이미 저장" in option["disabled_reason"] for option in brief["decision_action"]["options"])
        )
        self.assertFalse(brief["capabilities"]["can_record_decision"])
        self.assertFalse(brief["capabilities"]["storage_append_in_react"])
        self.assertFalse(brief["capabilities"]["provider_fetch"])
        self.assertFalse(brief["capabilities"]["validation_rerun"])


if __name__ == "__main__":
    unittest.main()
