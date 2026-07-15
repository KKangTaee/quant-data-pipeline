import unittest
from pathlib import Path


FINAL_REVIEW_ROOT = Path(
    "app/web/components/final_review_investment_report/frontend/src"
)
WORKSPACE = FINAL_REVIEW_ROOT / "DecisionBriefWorkspace.tsx"
CHARTS = FINAL_REVIEW_ROOT / "DecisionBriefCharts.tsx"
STYLE = FINAL_REVIEW_ROOT / "style.css"
MARKET_CONTEXT_STYLE = Path(
    "app/web/streamlit_components/market_context_valuation/src/style.css"
)


class FinalReviewMarketContextVisualContractTests(unittest.TestCase):
    def test_workspace_uses_approved_question_first_header(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")
        render = source.split("export function DecisionBriefWorkspace", 1)[1]

        self.assertIn("function WorkspaceHeader", source)
        self.assertIn("이 포트폴리오를 실제 투자 검토 대상으로", source)
        self.assertLess(render.index("<WorkspaceHeader"), render.index("<VerdictHero"))
        self.assertNotIn("<CandidateSelector model=", render)

    def test_style_uses_market_context_tokens_without_editorial_drift(self) -> None:
        style = STYLE.read_text(encoding="utf-8")
        reference = MARKET_CONTEXT_STYLE.read_text(encoding="utf-8")
        canonical_tokens = (
            "#152033",
            "#647589",
            "#dae4ee",
            "border-radius: 20px",
            "border-radius: 17px",
            "0 10px 30px rgba(33, 53, 72, .055)",
        )

        for token in canonical_tokens:
            self.assertIn(token, reference)
            self.assertIn(token, style)
        for token in (
            "--db-ink: #172019",
            "grid-template-columns: repeat(12",
            "border-radius: 2px",
            "4.3vw",
            "52px",
        ):
            self.assertNotIn(token, style)

    def test_charts_use_market_context_visual_family(self) -> None:
        source = CHARTS.read_text(encoding="utf-8")

        for color in ("#274764", "#269789", "#e2763b"):
            self.assertIn(color, source)
        for old_color in ("#166534", "#64748b", "#b45309"):
            self.assertNotIn(old_color, source)


if __name__ == "__main__":
    unittest.main()
