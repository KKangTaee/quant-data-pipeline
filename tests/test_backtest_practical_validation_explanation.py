from __future__ import annotations

import unittest


class PracticalValidationExplanationTests(unittest.TestCase):
    def _explain(
        self,
        row: dict[str, object],
        *,
        stage_owner: str = "practical_validation",
    ) -> dict[str, object]:
        from app.services.backtest_practical_validation_explanation import (
            explain_practical_validation_row,
        )

        return explain_practical_validation_row(row, stage_owner=stage_owner)

    def test_walk_forward_review_is_explained_in_user_language(self) -> None:
        explanation = self._explain(
            {
                "Criteria": "Walk-forward temporal validation",
                "Status": "REVIEW",
                "Current": "REVIEW / windows=103 / source=actual_runtime_latest_recheck",
                "Evidence": "worst excess -4.46% / negative share 61.2%",
                "Next Action": "negative window 원인을 확인합니다.",
            }
        )

        self.assertEqual(explanation["display_title"], "기간을 이동한 반복 검증")
        self.assertEqual(explanation["status_label"], "주의해서 확인")
        self.assertIn("103개", explanation["result_summary"])
        self.assertIn("비교 기준", explanation["meaning"])
        self.assertNotIn("actual_runtime_latest_recheck", explanation["result_summary"])
        self.assertEqual(
            explanation["technical_trace"]["current"],
            "REVIEW / windows=103 / source=actual_runtime_latest_recheck",
        )

    def test_regime_split_pass_describes_the_computed_result(self) -> None:
        explanation = self._explain(
            {
                "Criteria": "Regime split validation",
                "Status": "PASS",
                "Current": "PASS / buckets=3 / months=126",
                "Evidence": "worst excess 19.88% in caution",
            }
        )

        self.assertEqual(explanation["status_label"], "확인 완료")
        self.assertIn("126개월", explanation["result_summary"])
        self.assertIn("3개 시장 국면", explanation["result_summary"])
        self.assertEqual(explanation["evidence_state"], "verified")

    def test_provider_freshness_review_guides_level2_collection(self) -> None:
        explanation = self._explain(
            {
                "Criteria": "Provider snapshot freshness",
                "Status": "REVIEW",
                "Current": "PASS, REVIEW",
                "Evidence": "freshness=stale / stale_or_unknown_provider_snapshot",
            }
        )

        self.assertEqual(explanation["display_title"], "ETF·외부 데이터 최신성")
        self.assertIn("기준일", explanation["result_summary"])
        self.assertIn("데이터 보강", explanation["next_action"])
        self.assertEqual(explanation["stage_owner"], "practical_validation")

    def test_cost_sensitivity_hides_runtime_function_path_from_first_read(self) -> None:
        explanation = self._explain(
            {
                "Criteria": "Cost / slippage sensitivity evidence",
                "Status": "PASS",
                "Current": "app.runtime.backtest._apply_transaction_cost_postprocess",
                "Evidence": "generic=126 / runtime follow-up=1",
            }
        )

        first_read = " ".join(
            str(explanation[key])
            for key in (
                "display_title",
                "what_was_checked",
                "result_summary",
                "meaning",
                "next_action",
            )
        )
        self.assertNotIn("app.runtime", first_read)
        self.assertIn("기본 민감도 결과 126개", explanation["result_summary"])
        self.assertEqual(
            explanation["technical_trace"]["current"],
            "app.runtime.backtest._apply_transaction_cost_postprocess",
        )

    def test_tax_account_scope_is_kept_as_final_review_handoff(self) -> None:
        explanation = self._explain(
            {
                "label": "Tax / Account Scope",
                "status": "REVIEW",
                "checked_evidence": "tax / account scope: not modeled",
            },
            stage_owner="final_review",
        )

        self.assertEqual(explanation["display_title"], "세금·계좌 조건 반영 범위")
        self.assertIn("계산되지 않았", explanation["result_summary"])
        self.assertIn("Final Review", explanation["next_action"])
        self.assertEqual(explanation["stage_owner"], "final_review")

    def test_not_run_is_missing_validation_not_a_handoff(self) -> None:
        explanation = self._explain(
            {
                "Criteria": "Relative Strength perturbation",
                "Status": "NOT_RUN",
                "Evidence": "-",
            }
        )

        self.assertEqual(explanation["status_label"], "검증 미실행")
        self.assertEqual(explanation["evidence_state"], "missing")
        self.assertIn("검증 기능", explanation["next_action"])
        self.assertNotIn("Final Review로 넘", explanation["next_action"])

    def test_not_applicable_is_explained_as_intentional_exclusion(self) -> None:
        explanation = self._explain(
            {
                "Criteria": "Component weight concentration",
                "Status": "NOT_APPLICABLE",
                "Current": "single component construction",
            }
        )

        self.assertEqual(explanation["status_label"], "해당 없음")
        self.assertEqual(explanation["evidence_state"], "not_applicable")
        self.assertIn("검증 대상이 아닙니다", explanation["meaning"])
        self.assertIn("추가 조치", explanation["next_action"])


if __name__ == "__main__":
    unittest.main()
