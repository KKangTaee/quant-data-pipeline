from __future__ import annotations

import unittest


def _pass_checks() -> list[dict[str, object]]:
    return [
        {"Criteria": "Selection source", "Ready": True, "Current": "PASS"},
        {"Criteria": "Active components", "Ready": True, "Current": "PASS"},
        {"Criteria": "Target weight total", "Ready": True, "Current": "PASS"},
        {"Criteria": "Data Trust", "Ready": True, "Current": "PASS"},
        {"Criteria": "Execution boundary", "Ready": True, "Current": "PASS"},
        {"Criteria": "Curve evidence", "Ready": True, "Current": "PASS"},
        {"Criteria": "Runtime recheck", "Ready": True, "Current": "PASS"},
        {
            "Criteria": "Runtime period coverage",
            "Ready": True,
            "Current": "PASS",
        },
        {"Criteria": "Benchmark parity", "Ready": True, "Current": "PASS"},
        {"Criteria": "Provider coverage", "Ready": True, "Current": "PASS"},
    ]


class PracticalValidationLevel2HardeningTests(unittest.TestCase):
    def test_validation_efficacy_pass_and_not_applicable_are_ready(self) -> None:
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_READY,
            build_validation_efficacy_audit,
        )

        audit = build_validation_efficacy_audit(
            {
                "temporal_validation": {
                    "status": "PASS",
                    "metrics": {"window_count": 12},
                },
                "oos_holdout_validation": {
                    "status": "PASS",
                    "metrics": {
                        "in_sample_months": 36,
                        "out_sample_months": 36,
                    },
                },
                "regime_split_validation": {
                    "status": "NOT_APPLICABLE",
                    "summary": "현재 후보에는 별도 macro regime 분리가 적용되지 않습니다.",
                    "metrics": {},
                },
            }
        )

        rows = {row["Criteria"]: row for row in audit["rows"]}
        self.assertEqual(audit["route"], VALIDATION_EFFICACY_READY)
        self.assertEqual(
            rows["Regime split validation"]["Status"],
            "NOT_APPLICABLE",
        )
        self.assertEqual(audit["metrics"]["not_applicable"], 1)
        self.assertEqual(audit["metrics"]["ready_rows"], 3)

    def test_realism_not_applicable_row_is_not_coerced_to_review(self) -> None:
        from app.services.backtest_realism_audit import (
            BACKTEST_REALISM_READY,
            _route_from_rows,
            _row,
        )

        rows = [
            _row(
                criteria="Computed realism",
                status="PASS",
                current="computed",
                evidence="computed",
                next_action="추가 조치 없음",
                meaning="계산된 근거",
            ),
            _row(
                criteria="Irrelevant realism",
                status="NOT_APPLICABLE",
                current="not applicable",
                evidence="candidate boundary",
                next_action="추가 조치 없음",
                meaning="현재 후보에는 적용하지 않음",
            ),
        ]

        self.assertEqual(rows[1]["Status"], "NOT_APPLICABLE")
        self.assertTrue(rows[1]["Ready"])
        self.assertEqual(_route_from_rows(rows), BACKTEST_REALISM_READY)

    def test_period_outside_stress_is_not_missing_validator(self) -> None:
        from app.services.backtest_practical_validation_stress_sensitivity import (
            _stress_interpretation_result,
            build_robustness_lab_board,
        )

        stress = _stress_interpretation_result(
            [
                {
                    "Scenario": "Dot-com bust",
                    "Coverage": "NOT_COVERED",
                    "Result Status": "NOT_RUN",
                    "Judgment": "기간 미포함",
                }
            ]
        )
        board = build_robustness_lab_board(
            stress_interpretation=stress,
            sensitivity_interpretation={
                "status": "PASS",
                "computed_count": 2,
            },
            rolling_evidence={"status": "PASS", "metrics": {"window_count": 12}},
            overfit_audit={"status": "PASS", "trial_count": 2},
        )

        self.assertEqual(stress["status"], "NOT_APPLICABLE")
        self.assertEqual(stress["period_outside_count"], 1)
        self.assertEqual(stress["missing_validator_count"], 0)
        self.assertTrue(
            all(
                row["Status"] == "NOT_APPLICABLE"
                for row in stress["rows"][:4]
            )
        )
        self.assertEqual(board["status"], "PASS")

    def test_missing_required_method_becomes_engineering_blocker(self) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )
        from app.services.backtest_practical_validation_modules import (
            build_validation_module_plan,
        )
        from app.services.backtest_validation_efficacy import (
            VALIDATION_EFFICACY_NEEDS_INPUT,
            build_validation_efficacy_audit,
        )

        efficacy = build_validation_efficacy_audit({})
        self.assertEqual(efficacy["route"], VALIDATION_EFFICACY_NEEDS_INPUT)

        pass_rows = [{"Criteria": "computed row", "Status": "PASS"}]
        plan = build_validation_module_plan(
            source={
                "source_kind": "latest_backtest_run",
                "construction": {"source": "single_strategy"},
                "components": [
                    {
                        "strategy_key": "quality_factor",
                        "target_weight": 100.0,
                        "universe": ["AAPL", "MSFT"],
                    }
                ],
            },
            validation_profile={
                "profile_id": "balanced_core",
                "profile_label": "균형형",
            },
            checks=_pass_checks(),
            diagnostics=[
                {"domain": "stress_scenario_diagnostics", "status": "PASS"},
                {"domain": "robustness_sensitivity_overfit", "status": "PASS"},
                {"domain": "monitoring_baseline_seed", "status": "PASS"},
            ],
            validation_efficacy_rows=list(efficacy["rows"]),
            data_coverage_rows=pass_rows,
            construction_risk_rows=[],
            risk_contribution_rows=[],
            component_role_weight_rows=[],
            backtest_realism_rows=pass_rows,
        )
        modules = {row["module_id"]: row for row in plan["modules"]}
        self.assertEqual(
            modules["validation_efficacy"]["evidence_state"],
            "missing",
        )
        self.assertFalse(plan["final_review_gate"]["can_save_and_move"])

        closure = build_evidence_closure_contract(
            {
                "validation_id": "validation-missing-method",
                "selection_source_id": "source-missing-method",
                "validation_modules": list(plan["modules"]),
                "validation_efficacy_audit": efficacy,
            }
        )
        issue = next(
            row
            for row in closure["issues"]
            if row["root_issue_id"] == "validation_method_strength"
        )
        self.assertEqual(issue["resolution_class"], "engineering_required")
        self.assertEqual(issue["terminal_state"], "deferred")
        self.assertFalse(closure["current_final_review_eligible"])

    def test_refreshable_provider_gap_uses_registered_level2_action(self) -> None:
        from app.services.backtest_evidence_closure import (
            build_evidence_closure_contract,
        )
        from app.services.backtest_practical_validation import (
            _apply_pre_final_enrichment_gate,
            build_pre_final_enrichment_gate,
            build_provider_gap_collection_plan,
        )

        validation = {
            "validation_id": "validation-provider-gap",
            "selection_source_id": "source-provider-gap",
            "validation_modules": [],
            "final_review_gate": {
                "route": "READY_FOR_FINAL_REVIEW",
                "can_save_and_move": True,
                "blocking_modules": [],
            },
            "provider_coverage": {
                "symbols": ["SPY"],
                "coverage": {
                    "operability": {
                        "missing_symbols": ["SPY"],
                        "provenance": {"stale_symbols": []},
                    },
                    "holdings": {"missing_symbols": []},
                    "exposure": {"missing_symbols": []},
                    "macro": {
                        "diagnostic_status": "PASS",
                        "series_count": 3,
                        "stale_count": 0,
                    },
                },
            },
        }
        provider_plan = build_provider_gap_collection_plan(validation)
        enrichment = build_pre_final_enrichment_gate(
            validation,
            provider_plan=provider_plan,
        )
        _apply_pre_final_enrichment_gate(validation, enrichment)
        closure = build_evidence_closure_contract(validation)
        issue = next(
            row
            for row in closure["issues"]
            if row["root_issue_id"] == "pre_final_data_enrichment"
        )

        self.assertEqual(issue["resolution_class"], "resolve_now")
        self.assertEqual(
            issue["action_id"],
            "run_practical_validation_provider_gap_collection",
        )
        self.assertTrue(issue["actionable_now"])


if __name__ == "__main__":
    unittest.main()
