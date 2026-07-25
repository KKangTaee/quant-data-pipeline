import ResearchHeader from "../../market_research_header/ResearchHeader";
import type {
  ResearchHeaderFact,
  ResearchHeaderMeta,
  ResearchHeaderTone,
} from "../../market_research_header/ResearchHeader";

type Props = {
  asOfDate: string;
  estimateLabel: string;
  estimateTone: ResearchHeaderTone;
  hasIntramonth: boolean;
  summary: string;
  title: string;
};

function EconomicCycleHero({
  asOfDate,
  estimateLabel,
  estimateTone,
  hasIntramonth,
  summary,
  title,
}: Props) {
  const facts: ResearchHeaderFact[] = [
    {
      id: "as-of",
      label: "데이터 기준",
      value: asOfDate || "-",
    },
    {
      id: "estimate",
      label: "검증 상태",
      value: estimateLabel,
      tone: estimateTone,
      showIndicator: true,
    },
  ];
  const meta: ResearchHeaderMeta[] = [
    {
      id: "horizons",
      label: "현재 · +1개월 · +2개월",
    },
    ...(hasIntramonth
      ? [{ id: "intramonth", label: "월중 추정 별도 표시" }]
      : []),
  ];

  return (
    <ResearchHeader
      eyebrow="U.S. ECONOMIC CYCLE"
      facts={facts}
      kicker="현재 경기 위치"
      meta={meta}
      summary={summary}
      title={title}
      titleId="cycle-hero-title"
      variant="cycle"
    />
  );
}

export default EconomicCycleHero;
