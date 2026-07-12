from __future__ import annotations

import json
import unittest


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
