from __future__ import annotations

import unittest
from importlib import import_module
from types import SimpleNamespace
from unittest.mock import MagicMock, patch


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
                        "completion_criteria": "데이터 보강 후 새 replay에서 blocker 0건",
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
        self.assertEqual(
            issue["completion_criteria"],
            "데이터 보강 후 새 replay에서 blocker 0건",
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
                "evidence_state": "computed",
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

        self.assertEqual(summary["validated_caution_count"], 6)
        self.assertEqual(summary["accepted_limit_count"], 0)
        self.assertEqual(summary["final_decision_count"], 1)
        self.assertEqual(summary["resolve_now_count"], 0)
        self.assertEqual(summary["critical_engineering_count"], 0)

    def test_computed_level2_caution_is_resolved_without_final_review_handoff(
        self,
    ) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )

        contract = build_evidence_closure_contract(
            {
                "validation_id": "validation-computed-caution",
                "selection_source_id": "source-computed-caution",
                "validation_modules": [
                    {
                        "module_id": "validation_efficacy",
                        "label": "Validation Method Strength",
                        "status": "REVIEW",
                        "requirement": "REQUIRED",
                        "review_role": "pv_practical_caution",
                        "evidence_state": "computed",
                    }
                ],
            }
        )

        issue = contract["issues"][0]
        self.assertEqual(issue["resolution_class"], "validated_caution")
        self.assertEqual(issue["owner_stage"], "practical_validation")
        self.assertEqual(issue["terminal_state"], "resolved")
        self.assertEqual(contract["summary"]["validated_caution_count"], 1)
        self.assertEqual(contract["summary"]["accepted_limit_count"], 0)
        self.assertTrue(contract["current_final_review_eligible"])

    def test_missing_level2_validation_is_engineering_blocker(self) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )

        contract = build_evidence_closure_contract(
            {
                "validation_id": "validation-missing-caution",
                "selection_source_id": "source-missing-caution",
                "validation_modules": [
                    {
                        "module_id": "stress_robustness",
                        "label": "Stress / Robustness",
                        "status": "REVIEW",
                        "requirement": "REQUIRED",
                        "review_role": "pv_practical_caution",
                        "evidence_state": "missing",
                    }
                ],
            }
        )

        issue = contract["issues"][0]
        self.assertEqual(issue["resolution_class"], "engineering_required")
        self.assertEqual(issue["owner_stage"], "development")
        self.assertEqual(issue["criticality"], "critical")
        self.assertEqual(issue["terminal_state"], "deferred")
        self.assertFalse(contract["current_final_review_eligible"])

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
        level2_cautions = [
            {
                "root_issue_id": root_id,
                "title": title,
                "resolution_class": "validated_caution",
                "criticality": "noncritical",
                "terminal_state": "resolved",
                "owner_stage": "practical_validation",
                "actionable_now": False,
                "derived_checks": [root_id],
            }
            for root_id, title in (
                ("validation_method_strength", "Validation Method Strength"),
                ("construction_risk", "Construction Risk"),
                ("backtest_realism", "Backtest Realism"),
                ("stress_robustness", "Stress / Robustness"),
                ("provider_investability", "Provider Investability"),
            )
        ]
        accepted_limit = {
            "root_issue_id": "historical_universe_coverage",
            "title": "과거 universe와 상장폐지 반영 범위",
            "resolution_class": "accepted_limit",
            "criticality": "noncritical",
            "terminal_state": "open",
            "owner_stage": "final_review",
            "actionable_now": False,
            "derived_checks": ["historical_universe_coverage"],
        }
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
                "issues": [*level2_cautions, accepted_limit, final_decision],
                "summary": {
                    "total": 7,
                    "unresolved_actionable_count": 0,
                    "critical_engineering_count": 0,
                    "missing_contract_count": 0,
                    "resolve_now_count": 0,
                    "engineering_required_count": 0,
                    "validated_caution_count": 5,
                    "accepted_limit_count": 1,
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

    def test_workspace_projects_profile_questions_and_recheck_mode(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )
        from app.services.backtest_practical_validation_source import (
            build_validation_profile,
        )

        profile = build_validation_profile(
            "balanced_core",
            {
                "drawdown_tolerance": "dd_10",
                "holding_period": "lt_3m",
            },
        )
        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile=profile,
            replay_result=None,
            validation_result=None,
            source_options=[self._source()],
            recheck_mode="stored_period",
        )

        self.assertEqual(len(model["profile"]["questions"]), 5)
        drawdown = next(
            row
            for row in model["profile"]["questions"]
            if row["question_id"] == "drawdown_tolerance"
        )
        self.assertEqual(drawdown["value"], "dd_10")
        self.assertEqual(drawdown["options"][0]["value"], "dd_20")
        self.assertEqual(model["profile"]["threshold_summary"]["mdd_review_line"], -10.0)
        self.assertEqual(model["profile"]["threshold_summary"]["rolling_window_months"], 12)
        self.assertEqual(model["replay"]["mode"], "stored_period")
        self.assertEqual(model["replay"]["mode_label"], "저장 기간 그대로 재현")
        self.assertEqual(len(model["replay"]["mode_options"]), 2)

    def test_workspace_projects_compact_candidate_provenance(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        source = self._source()
        source.update(
            {
                "summary": {"cagr": 0.1356, "mdd": -0.146},
                "components": [
                    {"component_id": "gtaa"},
                    {"component_id": "grs"},
                    {"component_id": "risk-parity"},
                ],
                "data_trust": {
                    "status": "weighted_mix_snapshot",
                    "warning_count": 1,
                },
                "source_snapshot": {"large_internal": [1, 2, 3]},
                "result_curve": [{"Date": "2026-07-15"}],
            }
        )

        model = build_practical_validation_decision_workspace(
            source=source,
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result=None,
            validation_result=None,
            source_options=[source],
        )

        provenance = model["candidate"]["provenance"]
        self.assertEqual(provenance["period_label"], "2016-01-29 → 2026-07-15")
        self.assertEqual(provenance["cagr_label"], "13.56%")
        self.assertEqual(provenance["mdd_label"], "-14.60%")
        self.assertEqual(provenance["component_count"], 3)
        self.assertEqual(provenance["data_trust_label"], "주의 필요")
        self.assertEqual(provenance["warning_count"], 1)
        self.assertNotIn("source_snapshot", provenance)
        self.assertNotIn("result_curve", provenance)

    def test_workspace_projects_replay_provenance_and_validation_record(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        replay = {
            "status": "PASS",
            "replay_id": "pv_recheck_1234",
            "attempted_at": "2026-07-19T20:10:00+09:00",
            "recheck_mode": "extend_to_latest",
            "recheck_mode_label": "최신 DB 데이터까지 확장 검증",
            "period_coverage": {
                "status": "PASS",
                "requested_period": {
                    "start": "2016-01-29",
                    "end": "2026-07-17",
                },
                "actual_period": {
                    "start": "2016-01-29",
                    "end": "2026-07-17",
                },
                "latest_common_price_date": "2026-07-17",
                "end_gap_days": 0,
                "limiting_symbols": ["TIP"],
            },
        }
        validation = self._validation()

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result=replay,
            validation_result=validation,
            source_options=[self._source()],
        )

        provenance = model["replay"]["provenance"]
        self.assertTrue(provenance["visible"])
        self.assertEqual(provenance["mode_label"], "최신 DB 데이터까지 확장 검증")
        self.assertEqual(
            provenance["requested_period_label"],
            "2016-01-29 → 2026-07-17",
        )
        self.assertEqual(
            provenance["actual_period_label"],
            "2016-01-29 → 2026-07-17",
        )
        self.assertEqual(provenance["latest_common_price_date"], "2026-07-17")
        self.assertEqual(provenance["coverage_status"], "PASS")
        self.assertEqual(provenance["end_gap_days"], 0)
        self.assertEqual(provenance["limiting_symbols"], ["TIP"])

        record = model["record"]
        self.assertTrue(record["visible"])
        self.assertEqual(record["profile_label"], "균형형")
        self.assertEqual(record["recheck_mode_label"], "최신 DB 데이터까지 확장 검증")
        self.assertEqual(record["attempted_at"], "2026-07-19T20:10:00+09:00")
        self.assertEqual(record["replay_id"], "pv_recheck_1234")
        self.assertEqual(record["validation_id"], "validation-grs-current")

    def test_workspace_hides_replay_provenance_and_record_before_replay(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result=None,
            validation_result=None,
            source_options=[self._source()],
        )

        self.assertFalse(model["replay"]["provenance"]["visible"])
        self.assertFalse(model["record"]["visible"])

    def test_workspace_projects_collection_recheck_lifecycle_without_claiming_full_success(
        self,
    ) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core"},
            replay_result=None,
            validation_result=None,
            source_options=[self._source()],
            enrichment_progress={
                "status": "recheck_required",
                "result_count": 3,
            },
            collection_results=[
                {
                    "status": "SUCCESS",
                    "run_metadata": {
                        "input_params": {"provider_area": "operability"}
                    },
                },
                {
                    "status": "PARTIAL",
                    "run_metadata": {
                        "input_params": {"provider_area": "holdings"}
                    },
                },
                {
                    "status": "FAILED",
                    "run_metadata": {
                        "input_params": {"provider_area": "macro"}
                    },
                },
            ],
        )

        lifecycle = model["enrichment_lifecycle"]
        summary = lifecycle["collection_summary"]
        self.assertTrue(lifecycle["visible"])
        self.assertEqual(lifecycle["state"], "recheck_required")
        self.assertEqual(summary["success_count"], 1)
        self.assertEqual(summary["review_count"], 1)
        self.assertEqual(summary["failure_count"], 1)
        self.assertEqual(summary["areas"], ["holdings", "macro", "operability"])
        self.assertEqual(
            model["actions"]["run_replay"]["label"],
            "보강된 데이터로 재검증",
        )

    def test_semantic_notice_uses_warning_renderer_for_recheck_required(
        self,
    ) -> None:
        from app.web.backtest_practical_validation import page

        fake_streamlit = SimpleNamespace(
            success=MagicMock(),
            warning=MagicMock(),
            error=MagicMock(),
            info=MagicMock(),
        )
        with patch.object(page, "st", fake_streamlit):
            page._render_practical_validation_notice(
                {
                    "tone": "warning",
                    "title": "자료 보강을 실행했습니다",
                    "detail": "보강된 데이터로 재검증하세요.",
                }
            )

        fake_streamlit.warning.assert_called_once_with(
            "자료 보강을 실행했습니다 보강된 데이터로 재검증하세요."
        )
        fake_streamlit.success.assert_not_called()

    def test_profile_answer_intent_rebuilds_decision_without_clearing_replay(
        self,
    ) -> None:
        from app.web.backtest_practical_validation import page

        source = self._source()
        decision_key = "practical_validation_decision_result_source-grs-current"
        replay_key = (
            "practical_validation_recheck_source-grs-current_extend_to_latest"
        )
        fake_streamlit = SimpleNamespace(
            session_state={
                decision_key: {"validation_result": {"validation_id": "old"}},
                replay_key: {"status": "PASS", "replay_id": "replay-current"},
            },
            rerun=MagicMock(),
        )

        with patch.object(page, "st", fake_streamlit):
            page._consume_practical_validation_decision_workspace_intent(
                {
                    "action": "update_profile_answer",
                    "intent_id": "intent-profile-answer",
                    "selection_source_id": "source-grs-current",
                    "validation_result_id": "",
                    "question_id": "drawdown_tolerance",
                    "answer": "dd_10",
                },
                sources=[source],
                source=source,
                validation_result=None,
                replay_result=None,
                rerun_scope="app",
            )

        self.assertEqual(
            fake_streamlit.session_state[
                "practical_validation_profile_answer_drawdown_tolerance"
            ],
            "dd_10",
        )
        self.assertNotIn(decision_key, fake_streamlit.session_state)
        self.assertIn(replay_key, fake_streamlit.session_state)
        fake_streamlit.rerun.assert_called_once_with(scope="app")

    def test_recheck_mode_intent_clears_current_source_replay_and_result(
        self,
    ) -> None:
        from app.web.backtest_practical_validation import page

        source = self._source()
        decision_key = "practical_validation_decision_result_source-grs-current"
        replay_key = (
            "practical_validation_recheck_source-grs-current_extend_to_latest"
        )
        fake_streamlit = SimpleNamespace(
            session_state={
                decision_key: {"validation_result": {"validation_id": "old"}},
                replay_key: {"status": "PASS", "replay_id": "replay-current"},
            },
            rerun=MagicMock(),
        )

        with patch.object(page, "st", fake_streamlit):
            page._consume_practical_validation_decision_workspace_intent(
                {
                    "action": "select_recheck_mode",
                    "intent_id": "intent-recheck-mode",
                    "selection_source_id": "source-grs-current",
                    "validation_result_id": "",
                    "recheck_mode": "stored_period",
                },
                sources=[source],
                source=source,
                validation_result=None,
                replay_result=None,
                rerun_scope="fragment",
            )

        self.assertEqual(
            fake_streamlit.session_state[
                "practical_validation_recheck_mode_source-grs-current"
            ],
            "stored_period",
        )
        self.assertNotIn(decision_key, fake_streamlit.session_state)
        self.assertNotIn(replay_key, fake_streamlit.session_state)
        fake_streamlit.rerun.assert_called_once_with(scope="fragment")

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
        self.assertEqual(model["summary"]["validated_caution_count"], 5)
        self.assertEqual(model["summary"]["accepted_limit_count"], 1)
        self.assertEqual(model["summary"]["final_decision_count"], 1)
        self.assertEqual(model["resolution_lanes"]["resolve_now"], [])
        self.assertEqual(len(model["validated_cautions"]), 5)
        self.assertEqual(len(model["resolution_lanes"]["final_review_handoff"]), 2)
        self.assertIn("Final Review로 이동할 수 있습니다", model["verdict"]["headline"])
        self.assertEqual(model["handoff_presentation"]["state"], "promoted")
        self.assertEqual(
            model["handoff_presentation"]["title"],
            "Final Review에서 이어서 판단할 항목",
        )

    def test_ready_handoff_projects_compact_stage_actions_once_per_root(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"]["issues"].append(
            {
                **validation["evidence_closure"]["issues"][-1],
                "title": "중복 최종 판단",
            }
        )
        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        handoff = model["handoff_summary"]
        self.assertEqual(handoff["state"], "promoted")
        self.assertEqual(handoff["title"], "Final Review 인계 준비 완료")
        self.assertEqual(
            handoff["counts"],
            {
                "final_decision": 1,
                "accepted_limit": 1,
                "monitoring_transfer": 0,
            },
        )
        self.assertEqual(
            [row["root_issue_id"] for row in handoff["items"]],
            ["historical_universe_coverage", "tax_account_scope"],
        )
        self.assertEqual(
            [row["handoff_label"] for row in handoff["items"]],
            ["한계 인수 판단", "Final Review에서 결정"],
        )
        self.assertTrue(all(row["summary"] for row in handoff["items"]))
        self.assertTrue(all(row["next_stage_action"] for row in handoff["items"]))

    def test_blocked_workspace_labels_handoff_as_prospective(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"]["issues"].append(
            {
                "root_issue_id": "missing_contract:required_validator",
                "title": "필수 검증기 개발 필요",
                "resolution_class": "engineering_required",
                "criticality": "critical",
                "terminal_state": "deferred",
            }
        )
        validation["evidence_closure"]["summary"]["critical_engineering_count"] = 1
        validation["final_review_gate"]["can_save_and_move"] = False

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "resolution_required")
        self.assertEqual(model["handoff_presentation"]["state"], "prospective")
        self.assertEqual(
            model["handoff_presentation"]["title"],
            "검증 통과 후 Final Review에서 확인할 항목",
        )
        self.assertIn("아직 승격되지 않았습니다", model["handoff_presentation"]["detail"])

    def test_incomplete_monitoring_transfer_becomes_engineering_blocker(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"]["issues"] = [
            {
                "root_issue_id": "monitoring_baseline",
                "title": "Monitoring 기준",
                "resolution_class": "monitoring_transfer",
                "criticality": "noncritical",
                "terminal_state": "open",
                "completion_criteria": "Final Review에서 확인",
            }
        ]
        validation["evidence_closure"]["summary"].update(
            {
                "critical_engineering_count": 0,
                "monitoring_transfer_count": 1,
                "accepted_limit_count": 0,
                "final_decision_count": 0,
            }
        )
        validation["final_review_gate"]["can_save_and_move"] = False

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={"profile_id": "balanced_core", "profile_label": "균형형"},
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["state"], "resolution_required")
        self.assertEqual(model["summary"]["monitoring_transfer_count"], 0)
        self.assertEqual(model["summary"]["engineering_blocker_count"], 1)
        self.assertEqual(model["resolution_lanes"]["final_review_handoff"], [])
        self.assertEqual(
            model["resolution_lanes"]["engineering_required"][0]["root_issue_id"],
            "monitoring_baseline",
        )

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

    def test_source_kind_is_presented_as_user_language(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        weighted_source = {
            **self._source(),
            "source_kind": "weighted_portfolio_mix",
            "source_type": "",
        }
        single_source = {
            **self._source(),
            "selection_source_id": "source-single",
            "source_kind": "latest_backtest_run",
            "source_type": "",
        }
        model = build_practical_validation_decision_workspace(
            source=weighted_source,
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result=None,
            validation_result=None,
            source_options=[weighted_source, single_source],
        )

        labels = {
            row["selection_source_id"]: row["source_type_label"]
            for row in model["candidate_selector"]["options"]
        }
        self.assertEqual(labels["source-grs-current"], "혼합 포트폴리오")
        self.assertEqual(labels["source-single"], "단일 전략 실행")
        self.assertEqual(
            model["candidate"]["source_type_label"],
            "혼합 포트폴리오",
        )
        self.assertNotIn("selection_source", set(labels.values()))

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
        self.assertFalse(model["actions"]["run_replay"]["enabled"])
        self.assertEqual(
            model["actions"]["run_replay"]["label"],
            "데이터 보강 후 재검증",
        )
        self.assertFalse(model["actions"]["save_and_move"]["enabled"])

    def test_root_issue_without_audit_adapter_keeps_readable_observed_reason(
        self,
    ) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"] = {
            "issues": [
                {
                    "root_issue_id": "pre_final_data_contract",
                    "title": "필수 데이터 수집기 개발 필요",
                    "observed": (
                        "COMT, LQD의 보유종목 근거는 검증 가능한 공식 source "
                        "계약이 없거나 현재 자동 수집기가 처리하지 못합니다."
                    ),
                    "resolution_class": "engineering_required",
                    "criticality": "critical",
                    "terminal_state": "deferred",
                    "actionable_now": False,
                    "action_id": None,
                    "completion_criteria": (
                        "지원 parser 구현 후 holdings/exposure 근거를 저장합니다."
                    ),
                }
            ],
            "summary": {
                "unresolved_actionable_count": 0,
                "critical_engineering_count": 1,
                "missing_contract_count": 0,
                "resolve_now_count": 0,
                "engineering_required_count": 1,
                "accepted_limit_count": 0,
                "final_decision_count": 0,
                "monitoring_transfer_count": 0,
            },
        }
        validation["final_review_gate"]["can_save_and_move"] = False

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        issue = model["resolution_lanes"]["engineering_required"][0]
        self.assertIn("COMT, LQD", issue["observed"])
        self.assertIn("현재 자동 수집기가 처리하지 못합니다", issue["observed"])
        self.assertIn("지원 parser 구현", issue["completion_criteria"])

    def test_measured_accepted_limit_remains_final_review_handoff(self) -> None:
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

        self.assertEqual(model["summary"]["measured_caution_count"], 0)
        self.assertEqual(model["summary"]["accepted_limit_count"], 1)
        self.assertEqual(model["measured_cautions"], [])
        self.assertEqual(
            [
                row["root_issue_id"]
                for row in model["resolution_lanes"]["final_review_handoff"]
            ],
            ["provider_liquidity_pressure"],
        )

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

        verified_titles = {
            row["display_title"] for row in model["verified_findings"]
        }
        method_issue = next(
            row
            for row in model["validated_cautions"]
            if row["root_issue_id"] == "validation_method_strength"
        )
        self.assertIn("학습 구간 밖 성과 검증", verified_titles)
        self.assertIn("시장 국면별 성과 검증", verified_titles)
        self.assertIn("반복 검증 103개", method_issue["observed"])
        self.assertNotIn("근거 없음", method_issue["observed"])

    def test_detail_projection_uses_plain_language_and_five_categories(
        self,
    ) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["validation_efficacy_audit"] = {
            "overall_status": "REVIEW",
            "rows": [
                {
                    "Criteria": "Walk-forward temporal validation",
                    "Status": "REVIEW",
                    "Current": (
                        "REVIEW / windows=103 / "
                        "source=actual_runtime_latest_recheck"
                    ),
                    "Evidence": "worst excess -4.46%",
                },
                {
                    "Criteria": "Regime split validation",
                    "Status": "PASS",
                    "Current": "PASS / buckets=3 / months=126",
                    "Evidence": "worst excess 19.88%",
                },
            ],
        }

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(len(model["category_disclosures"]), 5)
        self.assertEqual(
            [row["category_id"] for row in model["category_disclosures"]],
            [
                "data_and_bias",
                "validation_method",
                "portfolio_structure",
                "realism_and_cost",
                "stress_and_robustness",
            ],
        )
        method = next(
            row
            for row in model["category_disclosures"]
            if row["category_id"] == "validation_method"
        )
        self.assertEqual(method["summary"]["total_count"], 2)
        self.assertEqual(method["summary"]["verified_count"], 1)
        self.assertEqual(method["summary"]["review_count"], 1)
        first_read = " ".join(
            str(value)
            for row in method["explanations"]
            for key, value in row.items()
            if key != "technical_trace"
        )
        self.assertNotIn("actual_runtime_latest_recheck", first_read)
        self.assertIn(
            "actual_runtime_latest_recheck",
            str(method["explanations"][0]["technical_trace"]),
        )

    def test_engineering_blockers_are_counted_once_per_root_issue(self) -> None:
        from app.services.backtest_practical_validation_decision_workspace import (
            build_practical_validation_decision_workspace,
        )

        validation = self._validation()
        validation["evidence_closure"] = {
            "issues": [
                {
                    "root_issue_id": root_issue_id,
                    "title": root_issue_id,
                    "resolution_class": "engineering_required",
                    "criticality": "critical",
                    "terminal_state": "deferred",
                    "actionable_now": False,
                }
                for root_issue_id in ("missing-provider", "missing-contract")
            ],
            "summary": {
                "unresolved_actionable_count": 0,
                "critical_engineering_count": 2,
                "missing_contract_count": 0,
            },
        }
        validation["final_review_gate"]["can_save_and_move"] = False

        model = build_practical_validation_decision_workspace(
            source=self._source(),
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            replay_result={"status": "PASS", "replay_id": "replay-current"},
            validation_result=validation,
            source_options=[self._source()],
        )

        self.assertEqual(model["summary"]["engineering_blocker_count"], 2)
        self.assertEqual(
            len(model["resolution_lanes"]["engineering_required"]),
            2,
        )

    def test_same_replay_and_profile_reuse_validation_result_id(self) -> None:
        from app.web.backtest_practical_validation import page

        fake_streamlit = SimpleNamespace(session_state={})
        source = self._source()
        profile = {
            "profile_id": "balanced_core",
            "answers": {"primary_goal": "balanced"},
        }
        replay = {
            "status": "PASS",
            "replay_id": "replay-current",
        }
        with (
            patch.object(page, "st", fake_streamlit),
            patch.object(
                page,
                "build_practical_validation_result",
                side_effect=[
                    {"validation_id": "validation-stable"},
                    {"validation_id": "validation-changed"},
                ],
            ) as builder,
        ):
            first = page._build_or_reuse_decision_workspace_validation_result(
                source=source,
                validation_profile=profile,
                replay_result=replay,
            )
            second = page._build_or_reuse_decision_workspace_validation_result(
                source=source,
                validation_profile=profile,
                replay_result=replay,
            )

        self.assertEqual(first["validation_id"], "validation-stable")
        self.assertEqual(second["validation_id"], "validation-stable")
        self.assertEqual(builder.call_count, 1)

    def test_component_wrapper_forwards_surface_and_on_change_callback(self) -> None:
        from app.web.components.practical_validation_decision_workspace import (
            component,
        )

        fake_component = MagicMock(return_value=None)
        on_change = MagicMock()
        with patch.object(component, "_component", fake_component):
            result = component.render_practical_validation_decision_workspace(
                workspace={"schema_version": "practical_validation_decision_workspace_v1"},
                surface="context",
                key="practical-validation-callback",
                on_change=on_change,
            )

        self.assertIsNone(result)
        fake_component.assert_called_once_with(
            workspace={"schema_version": "practical_validation_decision_workspace_v1"},
            surface="context",
            key="practical-validation-callback",
            default=None,
            on_change=on_change,
        )

    def test_component_change_consumes_replay_before_projection_without_rerun(
        self,
    ) -> None:
        from app.web.backtest_practical_validation import page

        component_key = "practical-validation-decision-workspace-source-grs-current"
        source = self._source()
        fake_streamlit = SimpleNamespace(
            session_state={
                component_key: {
                    "action": "run_replay",
                    "intent_id": "intent-callback-replay",
                    "selection_source_id": "source-grs-current",
                    "validation_result_id": "",
                }
            },
            rerun=MagicMock(),
        )
        with (
            patch.object(page, "st", fake_streamlit),
            patch.object(
                page,
                "_execute_practical_validation_replay",
                return_value={"status": "PASS", "replay_id": "replay-callback"},
            ) as replay,
        ):
            page._consume_practical_validation_component_change(
                component_key=component_key,
                allowed_actions={"run_replay", "run_resolution_action"},
                sources=[source],
                source=source,
                validation_result=None,
                replay_result=None,
            )

        replay.assert_called_once()
        fake_streamlit.rerun.assert_not_called()
        self.assertEqual(
            fake_streamlit.session_state[
                "practical_validation_workspace_last_intent_id"
            ],
            "intent-callback-replay",
        )
        self.assertEqual(
            fake_streamlit.session_state["backtest_practical_validation_notice"],
            "최신 데이터 기준 재검증을 완료했습니다.",
        )

    def test_context_surface_rejects_replay_intent(self) -> None:
        from app.web.backtest_practical_validation import page

        component_key = "practical-validation-decision-workspace-context"
        source = self._source()
        fake_streamlit = SimpleNamespace(
            session_state={
                component_key: {
                    "action": "run_replay",
                    "intent_id": "intent-cross-surface-replay",
                    "selection_source_id": "source-grs-current",
                    "validation_result_id": "",
                }
            },
            rerun=MagicMock(),
        )
        with (
            patch.object(page, "st", fake_streamlit),
            patch.object(
                page,
                "_execute_practical_validation_replay",
                return_value={"status": "PASS"},
            ) as replay,
        ):
            page._consume_practical_validation_component_change(
                component_key=component_key,
                allowed_actions={"select_source", "select_profile_preset"},
                sources=[source],
                source=source,
                validation_result=None,
                replay_result=None,
            )

        replay.assert_not_called()
        self.assertNotIn(
            "practical_validation_workspace_last_intent_id",
            fake_streamlit.session_state,
        )
        fake_streamlit.rerun.assert_not_called()

    def test_replay_intent_can_skip_explicit_rerun_in_component_callback(self) -> None:
        from app.web.backtest_practical_validation import page

        fake_streamlit = SimpleNamespace(
            session_state={},
            rerun=MagicMock(),
        )
        source = self._source()
        with (
            patch.object(page, "st", fake_streamlit),
            patch.object(
                page,
                "_execute_practical_validation_replay",
                return_value={"status": "PASS"},
            ) as replay,
        ):
            page._consume_practical_validation_decision_workspace_intent(
                {
                    "action": "run_replay",
                    "intent_id": "intent-fragment-replay",
                    "selection_source_id": "source-grs-current",
                    "validation_result_id": "",
                },
                sources=[source],
                source=source,
                validation_result=None,
                replay_result=None,
                rerun_scope="none",
            )

        replay.assert_called_once()
        fake_streamlit.rerun.assert_not_called()

    def test_replay_resolution_intent_uses_the_selected_recheck_mode(self) -> None:
        from app.services.backtest_practical_validation_replay import (
            RECHECK_MODE_STORED_PERIOD,
        )
        from app.web.backtest_practical_validation import page

        source = self._source()
        fake_streamlit = SimpleNamespace(
            session_state={
                "practical_validation_recheck_mode_source-grs-current": (
                    RECHECK_MODE_STORED_PERIOD
                )
            },
            rerun=MagicMock(),
        )
        validation = {
            "validation_id": "validation-replay-mode",
            "evidence_closure": {
                "issues": [
                    {
                        "root_issue_id": "replay_period_coverage",
                        "actionable_now": True,
                        "action_id": "run_practical_validation_replay",
                    }
                ]
            },
        }
        with (
            patch.object(page, "st", fake_streamlit),
            patch.object(
                page,
                "_execute_practical_validation_replay",
                return_value={"status": "PASS"},
            ) as replay,
        ):
            page._consume_practical_validation_decision_workspace_intent(
                {
                    "action": "run_resolution_action",
                    "intent_id": "intent-resolution-replay-mode",
                    "selection_source_id": "source-grs-current",
                    "validation_result_id": "validation-replay-mode",
                    "root_issue_id": "replay_period_coverage",
                    "action_id": "run_practical_validation_replay",
                },
                sources=[source],
                source=source,
                validation_result=validation,
                replay_result={"status": "REVIEW"},
                rerun_scope="fragment",
            )

        replay.assert_called_once_with(
            source,
            mode=RECHECK_MODE_STORED_PERIOD,
        )
        fake_streamlit.rerun.assert_called_once_with(scope="fragment")


if __name__ == "__main__":
    unittest.main()
