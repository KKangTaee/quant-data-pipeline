from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path


class FinalReviewDecisionBriefContractTests(unittest.TestCase):
    @classmethod
    def setUpClass(cls) -> None:
        fixture_path = Path("tests/fixtures/final_review_grs_decision_brief.json")
        cls.grs_fixture = json.loads(fixture_path.read_text(encoding="utf-8"))

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

    def _grs_inputs(self) -> dict[str, object]:
        inputs = deepcopy(self.grs_fixture)
        inputs["existing_decision_ids"] = set()
        return inputs

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

    def test_latest_stored_replay_wins_over_stale_source_curve(self) -> None:
        brief = self._build(self._grs_inputs())
        cumulative = brief["behavior_board"]["cumulative_series"]

        self.assertEqual(cumulative["status"], "measured")
        self.assertEqual(cumulative["points"][-1]["date"], "2026-06-30")
        self.assertEqual(
            cumulative["source"],
            "validation.curve_evidence.replay_attempt.portfolio_curve",
        )

    def test_aligned_curves_are_rebased_to_100_on_same_dates(self) -> None:
        brief = self._build(self._grs_inputs())
        candidate = brief["behavior_board"]["cumulative_series"]["points"]
        benchmark = brief["behavior_board"]["benchmark_series"]["points"]

        self.assertEqual([point["date"] for point in candidate], [point["date"] for point in benchmark])
        self.assertEqual(candidate[0]["value"], 100.0)
        self.assertEqual(benchmark[0]["value"], 100.0)

    def test_underwater_series_uses_running_peak_and_recovery_path(self) -> None:
        brief = self._build(self._grs_inputs())
        underwater = brief["behavior_board"]["underwater_series"]

        self.assertEqual(
            [point["value"] for point in underwater["points"]],
            [0.0, 0.0, -25.0, 0.0],
        )

    def test_missing_benchmark_is_explicitly_unmeasured(self) -> None:
        inputs = self._grs_inputs()
        inputs["validation"]["curve_evidence"]["replay_attempt"].pop("benchmark_curve")
        inputs["source"].pop("benchmark_curve")

        brief = self._build(inputs)
        benchmark = brief["behavior_board"]["benchmark_series"]

        self.assertEqual(benchmark["status"], "unmeasured")
        self.assertEqual(benchmark["points"], [])
        self.assertTrue(benchmark["missing_reason"])
        self.assertTrue(brief["disclosures"]["source_gaps"])

    def test_cost_unverified_curve_is_not_presented_as_net(self) -> None:
        inputs = self._grs_inputs()
        cost_snapshot = inputs["validation"]["selection_source_snapshot"]["source_snapshot"]["cost_model_snapshot"]
        cost_snapshot["cost_application_status"] = "assumption_only"

        brief = self._build(inputs)
        cumulative = brief["behavior_board"]["cumulative_series"]

        self.assertEqual(cumulative["basis"], "stored_curve_cost_unverified")
        self.assertNotIn("net", cumulative["label"].lower())
        self.assertNotIn("순", cumulative["label"])
        self.assertTrue(any("비용" in gap for gap in brief["disclosures"]["source_gaps"]))

    def test_execution_observations_use_structured_values_and_refs(self) -> None:
        brief = self._build(self._grs_inputs())
        observations = {
            row["observation_id"]: row
            for row in brief["behavior_board"]["execution_observations"]
        }

        self.assertEqual(observations["concentration-pressure"]["measured_value"], 45.0)
        self.assertEqual(observations["concentration-pressure"]["threshold_or_comparator"], 60.0)
        self.assertEqual(observations["turnover-burden"]["measured_value"], 0.4)
        self.assertEqual(observations["turnover-burden"]["threshold_or_comparator"], 0.3)
        self.assertEqual(observations["cost-burden"]["measured_value"], 10.0)
        self.assertEqual(observations["cost-burden"]["threshold_or_comparator"], 20.0)
        for observation in observations.values():
            self.assertTrue(observation["evidence_refs"])
            self.assertEqual(observation["as_of"], "2026-06-30")

    def test_trait_axes_keep_unmeasured_as_none_without_aggregate_score(self) -> None:
        brief = self._build(self._grs_inputs())
        trait_map = brief["trait_map"]
        axes = {axis["axis_id"]: axis for axis in trait_map["axes"]}

        self.assertEqual(len(axes), 5)
        self.assertEqual(axes["concentration_pressure"]["normalized_value"], 37.5)
        self.assertEqual(axes["regime_dependency"]["status"], "unmeasured")
        self.assertIsNone(axes["regime_dependency"]["normalized_value"])
        self.assertIsNone(trait_map["aggregate_score"])

    def test_strengths_and_weaknesses_require_measurement_and_comparator(self) -> None:
        inputs = self._grs_inputs()
        thresholds = inputs["validation"]["validation_profile"]["thresholds"]
        thresholds.pop("transaction_cost_bps_review")

        brief = self._build(inputs)
        strengths = {row["observation_id"] for row in brief["strengths"]}
        weaknesses = {row["observation_id"] for row in brief["weaknesses"]}

        self.assertIn("concentration-pressure", strengths)
        self.assertIn("turnover-burden", weaknesses)
        self.assertNotIn("cost-burden", strengths | weaknesses)

    def test_monitoring_conditions_are_structured_limited_and_primary_role_deduped(self) -> None:
        brief = self._build(self._grs_inputs())
        conditions = brief["monitoring_conditions"]
        finding_ids = {
            row["observation_id"]
            for row in [*brief["strengths"], *brief["weaknesses"]]
        }

        self.assertGreaterEqual(len(conditions), 2)
        self.assertLessEqual(len(conditions), 4)
        for condition in conditions:
            for key in ("observation", "threshold", "cadence", "re_review_action", "evidence_refs"):
                self.assertTrue(condition[key])
            self.assertEqual(condition["primary_role"], "monitoring")
            self.assertNotIn(condition["observation_id"], finding_ids)

    def test_current_grs_fixture_keeps_2026_06_valuation_in_behavior_series(self) -> None:
        brief = self._build(self._grs_inputs())
        period = brief["behavior_board"]["period"]
        cumulative = brief["behavior_board"]["cumulative_series"]

        self.assertEqual(cumulative["points"][-1]["date"], "2026-06-30")
        self.assertEqual(period["end"], "2026-06-30")
        self.assertEqual(period["latest_valuation_date"], "2026-06-30")
        self.assertEqual(period["last_complete_rebalance_date"], "2026-05-29")

    def test_decision_brief_snapshot_excludes_curve_points_and_keeps_trigger_contract(self) -> None:
        from app.services.backtest_final_review_decision_brief import (
            build_final_review_decision_brief_snapshot,
        )

        brief = self._build(self._grs_inputs())
        snapshot = build_final_review_decision_brief_snapshot(brief)
        serialized = json.dumps(snapshot, ensure_ascii=False, sort_keys=True)

        self.assertEqual(snapshot["schema_version"], "decision_brief_snapshot_v1")
        self.assertNotIn("behavior_board", snapshot)
        self.assertNotIn('"points"', serialized)
        self.assertEqual(
            set(snapshot["monitoring_conditions"][0]),
            {"observation_id", "title", "threshold", "cadence", "re_review_action"},
        )
        self.assertEqual(
            snapshot["monitoring_conditions"][0]["observation_id"],
            brief["monitoring_conditions"][0]["observation_id"],
        )


if __name__ == "__main__":
    unittest.main()
