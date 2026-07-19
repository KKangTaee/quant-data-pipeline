from __future__ import annotations

import json
import unittest
from copy import deepcopy
from pathlib import Path
from unittest.mock import MagicMock, patch


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
            "observation_freshness": {},
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

    def _current_character_inputs(self) -> dict[str, object]:
        inputs = self._grs_inputs()
        validation = inputs["validation"]
        validation["metrics"]["max_weight"] = 100.0
        validation["validation_profile"]["thresholds"] = {
            "max_weight_review": 60.0,
            "mdd_review_line": -15.0,
            "one_way_cost_bps": 10.0,
        }
        source_snapshot = validation["selection_source_snapshot"]["source_snapshot"]
        source_snapshot["turnover_evidence_snapshot"]["avg_turnover"] = 0.032
        source_snapshot["cost_model_snapshot"].update(
            {
                "transaction_cost_bps": 10.0,
                "cost_application_status": "applied_to_result_curve",
            }
        )
        validation["curve_evidence"]["replay_attempt"]["portfolio_curve"][2][
            "Total Balance"
        ] = 105.084
        return inputs

    def _current_monitoring_inputs(self) -> dict[str, object]:
        inputs = self._current_character_inputs()
        paper = inputs["paper_observation"]
        paper.pop("review_trigger_details", None)
        paper.update(
            {
                "review_cadence": "monthly_or_rebalance_review",
                "review_triggers": [
                    "CAGR deterioration review",
                    "MDD expansion review",
                    "Benchmark-relative underperformance review",
                    "Data Trust refresh review",
                ],
            }
        )
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

    def test_level2_handoff_promotes_distinct_root_deduplicated_sections(self) -> None:
        inputs = deepcopy(self._inputs())
        inputs["validation"]["evidence_closure"]["issues"] = [
            {
                "root_issue_id": "tax_account_scope",
                "title": "세금·계좌 조건 반영 범위",
                "resolution_class": "final_decision",
                "terminal_state": "open",
                "observed": "세금과 최소 주문 단위는 사용자 계좌별 최종 판단입니다.",
                "completion_criteria": "최종 route 사유에 적용할 계좌 조건을 기록합니다.",
                "derived_checks": ["tax_account_scope"],
            },
            {
                "root_issue_id": "tax_account_scope",
                "title": "중복 세금 항목",
                "resolution_class": "accepted_limit",
                "terminal_state": "open",
            },
            {
                "root_issue_id": "historical_universe_coverage",
                "title": "과거 종목 목록과 상장 이력",
                "resolution_class": "accepted_limit",
                "terminal_state": "open",
                "observed": "profiles=7 / lifecycle=covered=4 / partial=3 / missing=0",
                "completion_criteria": "정적 universe 한계를 알고 판단 사유에 반영합니다.",
                "derived_checks": ["universe_listing_evidence"],
            },
            {
                "root_issue_id": "replay_period_coverage",
                "title": "월중 최신 평가와 완결 리밸런싱 구분",
                "resolution_class": "monitoring_transfer",
                "terminal_state": "open",
                "monitoring_condition": {
                    "observation_id": "monitoring:next-complete-rebalance",
                    "observation": "최신 평가일과 마지막 완결 리밸런싱일의 차이",
                    "threshold": "다음 완결 리밸런싱 결과 저장 시",
                    "cadence": "다음 리밸런싱 시점",
                    "re_review_action": "새 완결 리밸런싱 결과로 후보 판단을 다시 확인합니다.",
                    "evidence_refs": ["evidence_closure.replay_period_coverage.period"],
                },
            },
        ]

        brief = self._build(inputs)
        handoff = brief["level2_handoff"]

        self.assertEqual(handoff["state"], "promoted")
        self.assertEqual(handoff["summary"], {
            "final_decision_count": 1,
            "accepted_limit_count": 1,
            "monitoring_condition_count": 1,
        })
        self.assertEqual(
            [row["root_issue_id"] for row in handoff["final_decisions"]],
            ["tax_account_scope"],
        )
        self.assertEqual(
            [row["root_issue_id"] for row in handoff["accepted_limits"]],
            ["historical_universe_coverage"],
        )
        self.assertEqual(
            [row["root_issue_id"] for row in handoff["monitoring_conditions"]],
            ["replay_period_coverage"],
        )
        self.assertNotIn("profiles=", json.dumps(handoff, ensure_ascii=False))
        self.assertIn("정적 universe", handoff["accepted_limits"][0]["observed"])

    def test_incomplete_monitoring_transfer_blocks_promotion(self) -> None:
        inputs = deepcopy(self._inputs())
        inputs["validation"]["evidence_closure"]["issues"] = [
            {
                "root_issue_id": "monitoring_baseline",
                "title": "Monitoring 기준",
                "resolution_class": "monitoring_transfer",
                "terminal_state": "open",
                "completion_criteria": "나중에 Monitoring에서 확인합니다.",
            }
        ]

        brief = self._build(inputs)

        self.assertFalse(brief["eligibility"]["eligible"])
        self.assertEqual(brief["level2_handoff"]["state"], "blocked")
        self.assertEqual(brief["level2_handoff"]["monitoring_conditions"], [])
        self.assertEqual(brief["verdict"]["route"], "RE_REVIEW_REQUIRED")

    def test_accepted_limit_acknowledgements_are_normalized_in_expected_order(
        self,
    ) -> None:
        from app.services.backtest_final_review_decision_brief import (
            validate_accepted_limit_acknowledgements,
        )

        normalized, error = validate_accepted_limit_acknowledgements(
            level2_handoff={
                "accepted_limits": [
                    {"root_issue_id": "limit-a"},
                    {"root_issue_id": "limit-b"},
                ]
            },
            acknowledgements=[
                {"root_issue_id": "limit-b", "decision": "accepted"},
                {"root_issue_id": "limit-a", "decision": "return_to_level2"},
            ],
            decision_route="RE_REVIEW_REQUIRED",
        )

        self.assertEqual(error, "")
        self.assertEqual(
            normalized,
            [
                {"root_issue_id": "limit-a", "decision": "return_to_level2"},
                {"root_issue_id": "limit-b", "decision": "accepted"},
            ],
        )

    def test_accepted_limit_acknowledgements_reject_incomplete_or_stale_roots(
        self,
    ) -> None:
        from app.services.backtest_final_review_decision_brief import (
            validate_accepted_limit_acknowledgements,
        )

        handoff = {
            "accepted_limits": [
                {"root_issue_id": "limit-a"},
                {"root_issue_id": "limit-b"},
            ]
        }
        invalid_cases = (
            ([{"root_issue_id": "limit-a", "decision": "accepted"}], "모든"),
            (
                [
                    {"root_issue_id": "limit-a", "decision": "accepted"},
                    {"root_issue_id": "limit-a", "decision": "accepted"},
                    {"root_issue_id": "limit-b", "decision": "accepted"},
                ],
                "중복",
            ),
            (
                [
                    {"root_issue_id": "limit-a", "decision": "accepted"},
                    {"root_issue_id": "limit-b", "decision": "accepted"},
                    {"root_issue_id": "stale-limit", "decision": "accepted"},
                ],
                "현재",
            ),
            (
                [
                    {"root_issue_id": "limit-a", "decision": "unknown"},
                    {"root_issue_id": "limit-b", "decision": "accepted"},
                ],
                "선택값",
            ),
        )
        for acknowledgements, expected_message in invalid_cases:
            with self.subTest(acknowledgements=acknowledgements):
                normalized, error = validate_accepted_limit_acknowledgements(
                    level2_handoff=handoff,
                    acknowledgements=acknowledgements,
                    decision_route="RE_REVIEW_REQUIRED",
                )
                self.assertEqual(normalized, [])
                self.assertIn(expected_message, error)

    def test_return_to_level2_requires_re_review_route(self) -> None:
        from app.services.backtest_final_review_decision_brief import (
            validate_accepted_limit_acknowledgements,
        )

        normalized, error = validate_accepted_limit_acknowledgements(
            level2_handoff={"accepted_limits": [{"root_issue_id": "limit-a"}]},
            acknowledgements=[
                {"root_issue_id": "limit-a", "decision": "return_to_level2"}
            ],
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
        )

        self.assertEqual(normalized, [])
        self.assertIn("Level2로 돌려보내기", error)

    def test_missing_accepted_limit_decision_does_not_append_final_row(self) -> None:
        from app.web.backtest_final_review import page

        fake_st = MagicMock()
        fake_st.session_state = {}
        append_row = MagicMock()
        decision_brief = {
            "level2_handoff": {
                "accepted_limits": [{"root_issue_id": "limit-a"}]
            }
        }
        with (
            patch.object(page, "st", fake_st),
            patch.object(
                page,
                "build_final_review_decision_record_guide",
                return_value={"route_templates": {}},
            ),
            patch.object(
                page,
                "_build_final_review_save_evaluation",
                return_value={"can_save": True},
            ),
            patch.object(page, "append_current_final_selection_decision", append_row),
        ):
            page._consume_final_review_decision_intent(
                {
                    "action": "record_final_decision",
                    "intent_id": "missing-limit-ack",
                    "decision_route": "SELECT_FOR_PRACTICAL_PORTFOLIO",
                    "operator_reason": "한계 확인 후 계속 추적합니다.",
                },
                source={"source_id": "candidate-a"},
                validation={"validation_id": "validation-a"},
                paper_observation={},
                evidence={},
                investability_packet={},
                decision_brief=decision_brief,
                decision_id="decision-a",
                decision_id_key="decision-key-a",
                existing_decision_ids=set(),
            )

        append_row.assert_not_called()
        fake_st.error.assert_called_once()

    def test_final_review_react_emits_accepted_limit_acknowledgements(self) -> None:
        source = Path(
            "app/web/components/final_review_investment_report/frontend/src/"
            "DecisionBriefWorkspace.tsx"
        ).read_text(encoding="utf-8")
        types = Path(
            "app/web/components/final_review_investment_report/frontend/src/"
            "decisionBriefTypes.ts"
        ).read_text(encoding="utf-8")

        for token in (
            "한계를 인수하고 계속",
            "Level2로 되돌리기",
            "acceptedLimitDecisions",
            "accepted_limit_acknowledgements",
            "return_to_level2",
        ):
            self.assertIn(token, source + types)

    def test_refreshable_stale_observation_blocks_only_selected_route(self) -> None:
        inputs = self._inputs()
        inputs["observation_freshness"] = {
            "schema_version": "final_review_observation_freshness_v1",
            "status": "price_refresh_available",
            "selection_blocked": True,
            "can_refresh": True,
            "button_label": "최신 데이터로 다시 계산",
        }

        brief = self._build(inputs)
        options = {
            row["route"]: row for row in brief["decision_action"]["options"]
        }

        self.assertEqual(
            brief["observation_freshness"]["status"],
            "price_refresh_available",
        )
        self.assertFalse(
            options["SELECT_FOR_PRACTICAL_PORTFOLIO"]["recordable"]
        )
        self.assertIn(
            "최신 데이터",
            options["SELECT_FOR_PRACTICAL_PORTFOLIO"]["disabled_reason"],
        )
        self.assertTrue(options["HOLD_FOR_MORE_PAPER_TRACKING"]["recordable"])
        self.assertTrue(options["REJECT_FOR_PRACTICAL_USE"]["recordable"])
        self.assertTrue(options["RE_REVIEW_REQUIRED"]["recordable"])
        self.assertTrue(brief["capabilities"]["can_refresh_observation"])
        self.assertFalse(brief["capabilities"]["provider_fetch"])
        self.assertFalse(brief["capabilities"]["validation_rerun"])

    def test_up_to_date_observation_keeps_selected_route_recordable(self) -> None:
        inputs = self._inputs()
        inputs["observation_freshness"] = {
            "schema_version": "final_review_observation_freshness_v1",
            "status": "up_to_date",
            "selection_blocked": False,
            "can_refresh": False,
        }

        brief = self._build(inputs)
        selected = next(
            row
            for row in brief["decision_action"]["options"]
            if row["route"] == "SELECT_FOR_PRACTICAL_PORTFOLIO"
        )

        self.assertTrue(selected["recordable"])
        self.assertFalse(brief["capabilities"]["can_refresh_observation"])

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

    def test_character_profile_exposes_observed_values_without_criteria(self) -> None:
        brief = self._build(self._current_character_inputs())
        items = {
            row["axis_id"]: row for row in brief["character_profile"]["items"]
        }

        self.assertEqual(
            list(items),
            ["concentration", "drawdown", "turnover", "cost", "regime_dependency"],
        )
        self.assertEqual(items["concentration"]["display_value"], "100.00%")
        self.assertEqual(items["drawdown"]["display_value"], "-12.43%")
        self.assertEqual(items["turnover"]["display_value"], "3.20%")
        self.assertEqual(items["cost"]["display_value"], "10.00 bps")
        self.assertEqual(
            items["regime_dependency"]["measurement_status"], "evidence_missing"
        )
        self.assertEqual(
            items["regime_dependency"]["display_value"], "분석 근거 없음"
        )

    def test_review_pressure_links_drawdown_alias_and_separates_missing_states(
        self,
    ) -> None:
        brief = self._build(self._current_character_inputs())
        pressure = {
            row["axis_id"]: row for row in brief["review_pressure"]["items"]
        }

        self.assertEqual(pressure["concentration"]["status"], "exceeds_limit")
        self.assertEqual(pressure["concentration"]["delta_value"], 40.0)
        self.assertEqual(pressure["drawdown"]["status"], "within_limit")
        self.assertEqual(pressure["drawdown"]["criterion_value"], -15.0)
        self.assertEqual(pressure["drawdown"]["delta_value"], -2.57)
        self.assertIn("관리선 -15.00%", pressure["drawdown"]["summary"])
        self.assertEqual(pressure["turnover"]["status"], "criterion_missing")
        self.assertEqual(pressure["cost"]["status"], "criterion_missing")
        self.assertEqual(pressure["regime_dependency"]["status"], "evidence_missing")

    def test_one_way_cost_assumption_is_not_used_as_review_limit(self) -> None:
        brief = self._build(self._current_character_inputs())
        cost = next(
            row
            for row in brief["review_pressure"]["items"]
            if row["axis_id"] == "cost"
        )

        self.assertEqual(cost["display_value"], "10.00 bps")
        self.assertIsNone(cost["criterion_value"])
        self.assertEqual(cost["status"], "criterion_missing")

    def test_character_contract_has_no_trait_map_or_arbitrary_score(self) -> None:
        brief = self._build(self._current_character_inputs())
        serialized = json.dumps(brief, ensure_ascii=False, sort_keys=True)

        self.assertNotIn("trait_map", brief)
        self.assertNotIn("aggregate_score", serialized)
        self.assertNotIn("normalized_value", serialized)

    def test_zero_review_criterion_is_contract_error(self) -> None:
        inputs = self._current_character_inputs()
        inputs["validation"]["validation_profile"]["thresholds"][
            "max_weight_review"
        ] = 0.0

        with self.assertRaisesRegex(
            ValueError, "zero review criterion is invalid for concentration"
        ):
            self._build(inputs)

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

    def test_current_grs_derives_drawdown_and_benchmark_monitoring_conditions(self) -> None:
        brief = self._build(self._current_monitoring_inputs())
        conditions = {
            row["observation_id"]: row for row in brief["monitoring_conditions"]
        }

        self.assertEqual(
            set(conditions),
            {
                "monitoring:drawdown-breach",
                "monitoring:benchmark-underperformance",
            },
        )
        drawdown = conditions["monitoring:drawdown-breach"]
        self.assertEqual(drawdown["measured_value"], -12.43)
        self.assertEqual(drawdown["threshold_or_comparator"], -15.0)
        self.assertEqual(drawdown["cadence"], "월간 또는 리밸런싱 시점")
        self.assertIn("-15.00%", drawdown["threshold"])
        self.assertEqual(drawdown["evidence_refs"], ["behavior_board.underwater_series"])
        benchmark = conditions["monitoring:benchmark-underperformance"]
        self.assertEqual(benchmark["threshold_or_comparator"], 0.0)
        self.assertIn("0.00%p 이하", benchmark["threshold"])
        self.assertEqual(
            benchmark["evidence_refs"],
            ["behavior_board.cumulative_series", "behavior_board.benchmark_series"],
        )

    def test_derived_monitoring_conditions_preserve_current_findings(self) -> None:
        brief = self._build(self._current_monitoring_inputs())
        findings = {
            row["observation_id"]
            for row in [*brief["strengths"], *brief["weaknesses"]]
        }

        self.assertIn("drawdown-recovery-path", findings)
        self.assertIn("benchmark-relative-terminal", findings)
        self.assertIn("concentration-pressure", findings)

    def test_monitoring_producer_does_not_invent_cagr_or_data_trust_thresholds(self) -> None:
        brief = self._build(self._current_monitoring_inputs())
        serialized = json.dumps(brief["monitoring_conditions"], ensure_ascii=False)

        self.assertNotIn("CAGR", serialized)
        self.assertNotIn("Data Trust", serialized)
        self.assertNotIn("deterioration", serialized)

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
