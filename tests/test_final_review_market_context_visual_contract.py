import unittest
from pathlib import Path


FINAL_REVIEW_ROOT = Path(
    "app/web/components/final_review_investment_report/frontend/src"
)
WORKSPACE = FINAL_REVIEW_ROOT / "DecisionBriefWorkspace.tsx"
CHARTS = FINAL_REVIEW_ROOT / "DecisionBriefCharts.tsx"
CHARACTER = FINAL_REVIEW_ROOT / "DecisionBriefCharacter.tsx"
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

    def test_section_heading_groups_eyebrow_above_korean_title(self) -> None:
        source = WORKSPACE.read_text(encoding="utf-8")
        heading = source.split("function SectionHeading", 1)[1].split(
            "function CandidateSelector", 1
        )[0]

        self.assertIn('className="db-section-heading-copy"', heading)
        self.assertLess(heading.index("{eyebrow}"), heading.index("<h2>{title}</h2>"))

    def test_observation_strip_has_complete_responsive_grid_and_wraps_long_values(
        self,
    ) -> None:
        style = STYLE.read_text(encoding="utf-8")

        self.assertIn("grid-template-columns: repeat(3, minmax(0, 1fr));", style)
        self.assertIn("grid-template-columns: repeat(2, minmax(0, 1fr));", style)
        self.assertIn("overflow-wrap: anywhere;", style)
        self.assertIn("word-break: break-word;", style)
        observation_block = style.split(".db-observation-strip {", 1)[1].split(
            ".db-empty,", 1
        )[0]
        self.assertNotIn("background: #e1e8f0;", observation_block)

    def test_charts_expose_ticks_hover_tooltip_and_underwater_meaning(self) -> None:
        source = CHARTS.read_text(encoding="utf-8")
        style = STYLE.read_text(encoding="utf-8")

        for token in (
            "type ChartUnit",
            "function niceExtent",
            "function buildTickIndices",
            "function buildYTicks",
            "function pointerIndex",
            "onPointerMove",
            "db-chart-hover-rule",
            "db-chart-focus-dot",
            "db-chart-tooltip",
            'unit="percent"',
            "고점 대비 낙폭 (Underwater)",
            "0%는 이전 최고점 회복",
        ):
            self.assertIn(token, source + style)

    def test_character_and_review_pressure_use_bounded_responsive_layout(self) -> None:
        source = CHARACTER.read_text(encoding="utf-8")
        style = STYLE.read_text(encoding="utf-8")

        for token in (
            "db-character-layout",
            "db-character-list",
            "db-pressure-list",
        ):
            self.assertIn(token, source + style)
        layout = style.split(".db-character-layout {", 1)[1].split("}", 1)[0]
        self.assertIn("grid-template-columns: minmax(0, 1.12fr) minmax(0, .88fr);", layout)
        responsive = style.split("@media (max-width: 760px)", 1)[1]
        self.assertIn(".db-character-layout", responsive)
        self.assertIn("grid-template-columns: 1fr;", responsive)
        self.assertNotIn("83.3 / 100", source)


if __name__ == "__main__":
    unittest.main()
