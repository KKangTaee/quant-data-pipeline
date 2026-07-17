from __future__ import annotations

import unittest
from pathlib import Path


ROOT = Path(
    "app/web/components/practical_validation_decision_workspace/frontend/src"
)
WORKSPACE = ROOT / "PracticalValidationDecisionWorkspace.tsx"
STYLE = ROOT / "style.css"
FINAL_REVIEW_STYLE = Path(
    "app/web/components/final_review_investment_report/frontend/src/style.css"
)


class PracticalValidationMarketContextVisualContractTests(unittest.TestCase):
    def test_workspace_uses_question_first_four_step_order(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn(
            "이 후보는 Final Review에서 실제 투자 판단을 할 만큼 검증되었는가?",
            source,
        )
        for label in (
            "1. 후보와 검증 기준",
            "2. 최신 데이터 기준 재검증",
            "3. 결과 해석과 해결 구분",
            "4. 저장하고 Final Review로 이동",
        ):
            self.assertIn(label, source)
        self.assertLess(
            source.index("1. 후보와 검증 기준"),
            source.index("2. 최신 데이터 기준 재검증"),
        )
        self.assertLess(
            source.index("2. 최신 데이터 기준 재검증"),
            source.index("3. 결과 해석과 해결 구분"),
        )
        self.assertLess(
            source.index("3. 결과 해석과 해결 구분"),
            source.index("4. 저장하고 Final Review로 이동"),
        )

    def test_style_uses_final_review_visual_tokens(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        reference = FINAL_REVIEW_STYLE.read_text(encoding="utf-8")
        for token in (
            "#152033",
            "#647589",
            "#dae4ee",
            "border-radius: 20px",
            "border-radius: 17px",
            "border-radius: 14px",
            "0 10px 30px rgba(33, 53, 72, .055)",
        ):
            self.assertIn(token, reference)
            self.assertIn(token, style)
        self.assertNotIn("border-radius: 0", style)

    def test_zero_action_lane_is_not_rendered(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("resolveNow.length > 0", source)
        self.assertIn("engineeringRequired.length > 0", source)
        self.assertIn("상세 검증 근거", source)
        self.assertNotIn("현재 표시할 항목이 없습니다.", source)

    def test_level2_handoff_is_compact_and_does_not_repeat_issue_cards(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("workspace.handoff_summary", source)
        self.assertIn("pv2-handoff-summary", source)
        self.assertIn("<h3>{workspace.handoff_summary.title}</h3>", source)
        self.assertIn("handoff_summary.items.map", source)
        self.assertNotIn("handoff.map((issue)", source)

    def test_detail_evidence_uses_category_selector_and_one_active_panel(
        self,
    ) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("activeEvidenceCategory", source)
        self.assertIn("pv2-evidence-category-tabs", source)
        self.assertIn("pv2-evidence-panel", source)
        self.assertIn("what_was_checked", source)
        self.assertIn("result_summary", source)
        self.assertIn("meaning", source)
        self.assertIn("next_action", source)
        self.assertIn("기술 원문", source)
        self.assertNotIn(
            "workspace.category_disclosures.map((group) => (",
            source,
        )

    def test_760_layout_collapses_to_one_column(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        responsive = style.split("@media (max-width: 760px)", 1)[1]

        self.assertIn("grid-template-columns: 1fr;", responsive)
        self.assertIn("overflow-wrap: anywhere;", style)

    def test_dynamic_content_updates_streamlit_frame_height(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("new ResizeObserver", source)
        self.assertIn("Streamlit.setFrameHeight()", source)

    def test_selected_candidate_context_is_inside_step_one_not_header(
        self,
    ) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")
        header = source.split('<header className="pv2-header">', 1)[1].split(
            "</header>", 1
        )[0]
        step_one = source.split('<section className="pv2-step">', 1)[1]

        self.assertNotIn("pv2-target-context", header)
        self.assertIn("pv2-selection-summary", step_one)
        self.assertIn("검증 대상", step_one)
        self.assertIn("판정 기준", step_one)
        self.assertLess(
            step_one.index("pv2-selection-summary"),
            step_one.index("pv2-candidate-toggle"),
        )

    def test_validation_profiles_use_five_columns_and_two_column_mobile_wrap(
        self,
    ) -> None:
        style = STYLE.read_text(encoding="utf-8")
        responsive = style.split("@media (max-width: 760px)", 1)[1]

        self.assertIn(
            "grid-template-columns: repeat(5, minmax(0, 1fr));",
            style,
        )
        self.assertIn(
            ".pv2-profile-grid {\n    grid-template-columns: repeat(2, minmax(0, 1fr));",
            responsive,
        )
        self.assertIn(
            ".pv2-profile-grid button:last-child:nth-child(odd)", responsive
        )
        self.assertIn("grid-column: 1 / -1;", responsive)


if __name__ == "__main__":
    unittest.main()
