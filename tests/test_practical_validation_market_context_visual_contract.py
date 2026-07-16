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

    def test_760_layout_collapses_to_one_column(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        responsive = style.split("@media (max-width: 760px)", 1)[1]

        self.assertIn("grid-template-columns: 1fr;", responsive)
        self.assertIn("overflow-wrap: anywhere;", style)

    def test_dynamic_content_updates_streamlit_frame_height(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")

        self.assertIn("new ResizeObserver", source)
        self.assertIn("Streamlit.setFrameHeight()", source)


if __name__ == "__main__":
    unittest.main()
