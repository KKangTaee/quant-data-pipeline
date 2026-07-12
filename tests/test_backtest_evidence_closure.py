from __future__ import annotations

import json
import unittest
from pathlib import Path


def _issue(contract: dict[str, object], root_issue_id: str) -> dict[str, object]:
    return next(
        dict(row)
        for row in list(contract.get("issues") or [])
        if isinstance(row, dict) and row.get("root_issue_id") == root_issue_id
    )


def _grs_validation_fixture() -> dict[str, object]:
    return {
        "validation_id": "validation-grs",
        "selection_source_id": "source-grs",
        "validation_modules": [
            {
                "module_id": "latest_replay",
                "label": "Latest Runtime Replay",
                "status": "REVIEW",
                "requirement": "REQUIRED",
                "review_role": "pv_data_caution",
            },
            {
                "module_id": "data_coverage",
                "label": "Data Coverage",
                "status": "REVIEW",
                "requirement": "REQUIRED",
                "review_role": "pv_data_caution",
            },
        ],
        "curve_evidence": {
            "portfolio_curve_source": "actual_runtime_latest_recheck",
            "curve_provenance": {
                "portfolio_curve_source": "actual_runtime_latest_recheck",
                "runtime_recheck_status": "REVIEW",
                "runtime_recheck_mode": "extend_to_latest",
                "period_coverage_status": "REVIEW",
                "period_coverage": {
                    "status": "REVIEW",
                    "requested_period": {"start": "2016-01-29", "end": "2026-07-10"},
                    "actual_period": {"start": "2016-01-29", "end": "2026-05-29"},
                    "end_gap_days": 42,
                },
            },
        },
        "data_coverage_audit": {
            "rows": [
                {
                    "Criteria": "PIT price window coverage",
                    "Status": "REVIEW",
                    "Current": "actual_runtime_latest_recheck / replay=REVIEW / period=REVIEW",
                    "Evidence": "extend_to_latest",
                }
            ]
        },
    }


class EvidenceClosureContractTests(unittest.TestCase):
    def test_selected_decision_finalizes_limits_and_monitoring_for_same_validation(self) -> None:
        from app.services.backtest_evidence_closure import finalize_evidence_closure

        contract = {
            "validation_id": "validation-1",
            "issues": [
                {
                    "root_issue_id": "static_universe_limit",
                    "resolution_class": "accepted_limit",
                    "terminal_state": "open",
                    "title": "정적 universe 사후 선택 한계",
                },
                {
                    "root_issue_id": "monitoring_baseline",
                    "resolution_class": "monitoring_transfer",
                    "terminal_state": "open",
                    "title": "Monitoring baseline",
                    "completion_criteria": "월별 drawdown trigger 추적",
                },
            ],
            "summary": {},
        }

        snapshot = finalize_evidence_closure(
            contract,
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="한계를 확인하고 추적 조건을 수용함",
        )

        self.assertEqual(snapshot["validation_id"], "validation-1")
        self.assertEqual(snapshot["terminal_state_counts"]["accepted"], 1)
        self.assertEqual(snapshot["terminal_state_counts"]["monitoring_transferred"], 1)
        self.assertEqual(snapshot["open_count"], 0)
        self.assertEqual(snapshot["monitoring_conditions"], ["월별 drawdown trigger 추적"])

    def test_score_impact_is_measured_and_root_deduplicated(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_scorecard

        measured_issue = {
            "root_issue_id": "replay_period_coverage",
            "title": "최신 재검증 기간",
            "measurement": {
                "observed": 42,
                "threshold": 30,
                "comparison": "less_than_or_equal",
                "target_dimension": "evidence_confidence",
                "score_effect": -3,
            },
        }
        scorecard = build_final_review_scorecard(
            investability_packet={
                "score": 9.0,
                "selection_gate_policy_snapshot": {
                    "outcome": "select_ready",
                    "select_allowed": True,
                    "blockers": [],
                },
            },
            level2_review_disposition={
                "summary": {"blocker": 0, "warning": 1, "open_review": 0, "monitoring_followup": 0},
                "groups": {},
                "closure_summary": {
                    "unresolved_actionable_count": 0,
                    "critical_engineering_count": 0,
                    "missing_contract_count": 0,
                },
                "closure_issues": [measured_issue, dict(measured_issue)],
            },
        )

        impacts = scorecard["review_impacts"]
        self.assertEqual([row["root_issue_id"] for row in impacts], ["replay_period_coverage"])
        self.assertEqual(impacts[0]["score_effect"], -3)
        self.assertEqual(impacts[0]["measurement"]["observed"], 42)

    def test_missing_contract_and_open_actionable_are_gate_not_score(self) -> None:
        from app.services.backtest_evidence_read_model import build_final_review_scorecard

        scorecard = build_final_review_scorecard(
            investability_packet={
                "score": 9.0,
                "selection_gate_policy_snapshot": {
                    "outcome": "select_ready",
                    "select_allowed": True,
                    "blockers": [],
                },
            },
            level2_review_disposition={
                "summary": {"blocker": 0, "warning": 0, "open_review": 0, "monitoring_followup": 0},
                "groups": {},
                "closure_summary": {
                    "unresolved_actionable_count": 1,
                    "critical_engineering_count": 0,
                    "missing_contract_count": 1,
                },
                "closure_issues": [
                    {
                        "root_issue_id": "missing_contract:required_unknown",
                        "resolution_class": "engineering_required",
                        "terminal_state": "deferred",
                    }
                ],
            },
        )

        self.assertEqual(scorecard["review_impacts"], [])
        self.assertIn(
            "evidence_closure_blocker",
            [row["code"] for row in scorecard["route_constraints"]],
        )

    def test_decision_row_does_not_promote_selected_route_with_engineering_blocker(self) -> None:
        from app.web.backtest_final_review_helpers import _build_final_review_decision_row

        validation = {
            "validation_id": "validation-blocked",
            "selection_source_id": "source-blocked",
            "evidence_closure": {
                "validation_id": "validation-blocked",
                "issues": [
                    {
                        "root_issue_id": "historical_universe_coverage",
                        "title": "PIT membership 근거",
                        "resolution_class": "engineering_required",
                        "criticality": "critical",
                        "terminal_state": "deferred",
                    }
                ],
                "summary": {"critical_engineering_count": 1},
            },
        }
        packet = {
            "selection_gate_policy_snapshot": {
                "outcome": "select_ready",
                "select_allowed": True,
                "blockers": [],
            }
        }

        row = _build_final_review_decision_row(
            source={"source_id": "source-blocked", "source_type": "practical_validation_result"},
            validation=validation,
            paper_observation={"active_components": []},
            evidence={"route": "READY_FOR_FINAL_DECISION"},
            investability_packet=packet,
            decision_id="decision-blocked",
            decision_route="SELECT_FOR_PRACTICAL_PORTFOLIO",
            operator_reason="근거 확인",
            operator_constraints="",
            operator_next_action="",
        )

        self.assertFalse(row["monitoring_candidate"])
        self.assertEqual(row["evidence_closure_snapshot"]["selection_blocker_count"], 1)

    def test_recheck_plan_uses_component_common_date_not_whole_db_max(self) -> None:
        import pandas as pd
        from unittest.mock import patch

        from app.services import backtest_practical_validation_replay as replay_service

        source = {
            "period": {"actual_start": "2016-08-31", "actual_end": "2026-02-28"},
            "components": [
                {
                    "strategy_key": "global_relative_strength",
                    "universe": ["SPY"],
                    "contract": {"cash_ticker": "BIL"},
                }
            ],
        }
        freshness = pd.DataFrame(
            [
                {"symbol": "SPY", "latest_date": "2026-06-30", "row_count": 100},
                {"symbol": "BIL", "latest_date": "2026-06-26", "row_count": 100},
            ]
        )

        with (
            patch.object(replay_service, "load_latest_market_date", return_value="2026-07-10"),
            patch.object(replay_service, "load_price_freshness_summary", return_value=freshness),
        ):
            plan = replay_service.build_practical_validation_recheck_plan(source)

        self.assertEqual(plan["market_date_contract"]["requested_market_date"], "2026-07-10")
        self.assertEqual(plan["market_date_contract"]["latest_common_price_date"], "2026-06-26")
        self.assertEqual(plan["market_date_contract"]["limiting_symbols"], ["BIL"])
        self.assertEqual(plan["requested_period"]["end"], "2026-06-26")

    def test_static_manual_survivorship_gap_is_accepted_limit_candidate(self) -> None:
        from app.services.backtest_evidence_closure import build_evidence_closure_contract

        validation = _grs_validation_fixture()
        validation["data_coverage_audit"] = {
            "universe_contract": {
                "mode": "static_manual",
                "requires_pit_membership": False,
                "survivorship_applicability": "accepted_limit_allowed",
            },
            "rows": [
                {"Criteria": "Universe / listing evidence", "Status": "REVIEW", "Current": "partial"},
                {"Criteria": "Survivorship / delisting control", "Status": "REVIEW", "Current": "not proven"},
            ],
        }

        issue = _issue(build_evidence_closure_contract(validation), "historical_universe_coverage")

        self.assertEqual(issue["resolution_class"], "accepted_limit")
        self.assertEqual(issue["criticality"], "noncritical")

    def test_dynamic_universe_missing_pit_membership_is_critical_engineering_blocker(self) -> None:
        from app.services.backtest_evidence_closure import build_evidence_closure_contract

        validation = _grs_validation_fixture()
        validation["data_coverage_audit"] = {
            "universe_contract": {
                "mode": "dynamic_historical",
                "requires_pit_membership": True,
                "survivorship_applicability": "critical_required",
            },
            "rows": [
                {"Criteria": "Universe / listing evidence", "Status": "NEEDS_INPUT", "Current": "missing PIT"},
                {"Criteria": "Survivorship / delisting control", "Status": "NEEDS_INPUT", "Current": "not proven"},
            ],
        }

        contract = build_evidence_closure_contract(validation)
        issue = _issue(contract, "historical_universe_coverage")

        self.assertEqual(issue["resolution_class"], "engineering_required")
        self.assertEqual(issue["criticality"], "critical")
        self.assertEqual(issue["terminal_state"], "deferred")
        self.assertFalse(contract["current_final_review_eligible"])

    def test_resolve_now_without_registered_handler_has_no_cta_and_blocks(self) -> None:
        from app.services.backtest_evidence_closure import normalize_evidence_issue

        issue = normalize_evidence_issue(
            {
                "root_issue_id": "unknown_action",
                "resolution_class": "resolve_now",
                "action_id": "missing_handler",
                "terminal_state": "open",
            }
        )

        self.assertFalse(issue["actionable_now"])
        self.assertEqual(issue["resolution_class"], "engineering_required")
        self.assertEqual(issue["gate_effect"], "block_final_review")
        self.assertEqual(issue["action_label"], "개발 후 재검토")

    def test_current_final_review_eligibility_requires_zero_unresolved_actionable(self) -> None:
        from app.web.backtest_final_review_helpers import _is_final_review_eligible_validation_result

        validation = {
            "validation_id": "validation-actionable",
            "selection_source_id": "source-actionable",
            "final_review_gate": {"can_save_and_move": True},
            "selected_route_preflight": {"select_allowed": True},
            "evidence_closure": {
                "summary": {
                    "unresolved_actionable_count": 1,
                    "critical_engineering_count": 0,
                    "missing_contract_count": 0,
                }
            },
        }

        self.assertFalse(_is_final_review_eligible_validation_result(validation))

    def test_workspace_separates_now_engineering_and_accepted_limit(self) -> None:
        from app.services.backtest_practical_validation_workspace import (
            build_practical_validation_workspace,
        )

        validation = {
            "evidence_closure": {
                "issues": [
                    {
                        "root_issue_id": "replay_period_coverage",
                        "title": "최신 재검증 기간 충족 여부",
                        "resolution_class": "resolve_now",
                        "terminal_state": "open",
                        "actionable_now": True,
                        "action_id": "run_practical_validation_replay",
                        "completion_criteria": "새 validation 저장",
                    },
                    {
                        "root_issue_id": "missing_contract:dynamic_universe",
                        "title": "과거 universe 근거",
                        "resolution_class": "engineering_required",
                        "terminal_state": "deferred",
                        "actionable_now": False,
                        "action_id": None,
                        "completion_criteria": "provider 개발 후 재검토",
                    },
                    {
                        "root_issue_id": "historical_universe_coverage",
                        "title": "상장폐지 반영 한계",
                        "resolution_class": "accepted_limit",
                        "terminal_state": "open",
                        "actionable_now": False,
                        "action_id": None,
                        "completion_criteria": "Final Review 판단 사유에 반영",
                    },
                ],
                "summary": {
                    "unresolved_actionable_count": 1,
                    "critical_engineering_count": 1,
                    "missing_contract_count": 1,
                },
            },
            "validation_modules": [],
            "final_review_gate": {"can_save_and_move": False},
        }

        workspace = build_practical_validation_workspace(validation)

        self.assertEqual(
            [group["label"] for group in workspace["evidence_closure_groups"]],
            ["지금 해결 가능", "개발 필요", "한계 인수 가능"],
        )
        engineering_card = workspace["evidence_closure_groups"][1]["items"][0]
        self.assertFalse(engineering_card["actionable_now"])
        self.assertEqual(engineering_card["action_label"], "개발 후 재검토")

    def test_level2_closure_cards_only_reference_registered_python_replay_action(self) -> None:
        page_source = Path("app/web/backtest_practical_validation/page.py").read_text(
            encoding="utf-8"
        )

        self.assertIn('action_id == "run_practical_validation_replay"', page_source)
        self.assertIn("_render_evidence_closure_groups(validation_result)", page_source)
        self.assertNotIn('action_id == "missing_handler"', page_source)

    def test_final_review_react_renders_python_closure_sections_without_domain_recalculation(self) -> None:
        source = Path(
            "app/web/components/final_review_investment_report/frontend/src/FinalReviewInvestmentReport.tsx"
        ).read_text(encoding="utf-8")

        self.assertIn("선정 전 미해결 항목", source)
        self.assertIn("인수한 한계와 최종 판단 항목", source)
        self.assertNotIn("resolutionClass ===", source)
        self.assertNotIn("fetch(", source)
        self.assertNotIn("scoreEffect =", source)

    def test_latest_replay_adapter_uses_stored_requested_actual_and_gap(self) -> None:
        from app.services.backtest_evidence_closure import build_evidence_closure_contract

        contract = build_evidence_closure_contract(_grs_validation_fixture())
        replay_issue = _issue(contract, "replay_period_coverage")

        self.assertEqual(
            replay_issue["derived_checks"],
            ["latest_replay", "pit_price_window_coverage"],
        )
        self.assertEqual(replay_issue["period"]["requested_market_date"], "2026-07-10")
        self.assertEqual(replay_issue["period"]["actual_result_date"], "2026-05-29")
        self.assertEqual(replay_issue["period"]["end_gap_days"], 42)

    def test_replay_and_pit_rows_become_one_root_issue(self) -> None:
        from app.services.backtest_evidence_closure import build_evidence_closure_contract

        contract = build_evidence_closure_contract(_grs_validation_fixture())

        self.assertEqual(
            [row["root_issue_id"] for row in contract["issues"]].count("replay_period_coverage"),
            1,
        )

    def test_listing_and_survivorship_rows_become_one_root_issue(self) -> None:
        from app.services.backtest_evidence_closure import build_evidence_closure_contract

        validation = _grs_validation_fixture()
        validation["data_coverage_audit"] = {
            "rows": [
                {
                    "Criteria": "Universe / listing evidence",
                    "Status": "REVIEW",
                    "Current": "profiles=7 / lifecycle=covered=4 / partial=3 / symbols=7",
                    "Evidence": "partial=BIL,IEF,TLT",
                },
                {
                    "Criteria": "Survivorship / delisting control",
                    "Status": "REVIEW",
                    "Current": "not proven / covered=4 / partial=3",
                    "Evidence": "historical delisting evidence not attached",
                },
            ]
        }

        contract = build_evidence_closure_contract(validation)
        universe_issue = _issue(contract, "historical_universe_coverage")

        self.assertEqual(
            universe_issue["derived_checks"],
            ["universe_listing_evidence", "survivorship_delisting_control"],
        )
        self.assertEqual(
            [row["root_issue_id"] for row in contract["issues"]].count("historical_universe_coverage"),
            1,
        )

    def test_required_missing_adapter_is_contract_blocker_not_score_impact(self) -> None:
        from app.services.backtest_evidence_closure import build_evidence_closure_contract

        validation = {
            "validation_id": "validation-missing",
            "selection_source_id": "source-missing",
            "validation_modules": [
                {
                    "module_id": "required_unknown",
                    "label": "Required Unknown",
                    "status": "REVIEW",
                    "requirement": "REQUIRED",
                    "review_role": "pv_data_caution",
                }
            ],
        }

        contract = build_evidence_closure_contract(validation)
        issue = _issue(contract, "missing_contract:required_unknown")

        self.assertEqual(issue["resolution_class"], "engineering_required")
        self.assertEqual(issue["criticality"], "critical")
        self.assertEqual(issue["gate_effect"], "block_final_review")
        self.assertEqual(issue["score_impact"], 0)
        self.assertEqual(contract["summary"]["missing_contract_count"], 1)
        self.assertFalse(contract["current_final_review_eligible"])

    def test_required_missing_adapter_blocks_final_review_eligibility(self) -> None:
        from app.web.backtest_final_review_helpers import _is_final_review_eligible_validation_result

        validation = {
            "validation_id": "validation-missing",
            "selection_source_id": "source-missing",
            "final_review_gate": {"can_save_and_move": True},
            "selected_route_preflight": {"select_allowed": True},
            "validation_modules": [
                {
                    "module_id": "required_unknown",
                    "label": "Required Unknown",
                    "status": "REVIEW",
                    "requirement": "REQUIRED",
                    "review_role": "pv_data_caution",
                }
            ],
        }

        self.assertFalse(_is_final_review_eligible_validation_result(validation))

    def test_required_missing_adapter_is_not_rendered_as_user_review_item(self) -> None:
        from app.services.backtest_evidence_read_model import (
            build_final_review_level2_review_disposition,
        )

        validation = {
            "validation_id": "validation-missing",
            "selection_source_id": "source-missing",
            "validation_modules": [
                {
                    "module_id": "required_unknown",
                    "label": "Required Unknown",
                    "status": "REVIEW",
                    "requirement": "REQUIRED",
                    "review_role": "pv_data_caution",
                }
            ],
        }

        disposition = build_final_review_level2_review_disposition(validation=validation)

        self.assertEqual(disposition["closure_summary"]["missing_contract_count"], 1)
        self.assertNotIn("세부 설명 준비 안 됨", json.dumps(disposition, ensure_ascii=False))


if __name__ == "__main__":
    unittest.main()
