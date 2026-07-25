type EventsHeroCounts = {
  today?: number;
  thisWeek?: number;
  next30d?: number;
  staleEstimate?: number;
};

type EventsHeroNextEvent = {
  date: string;
  title: string;
};

type Props = {
  boundaryNote: string;
  counts: EventsHeroCounts;
  nextEvent?: EventsHeroNextEvent | null;
  title: string;
};

function EventsHero({ boundaryNote, counts, nextEvent, title }: Props) {
  const facts: ResearchHeaderFact[] = [
    {
      id: "next-event",
      label: "다음 이벤트",
      value: nextEvent ? `${nextEvent.date} · ${nextEvent.title}` : "예정 없음",
    },
  ];
  const meta: ResearchHeaderMeta[] = [
    {
      id: "today",
      label: <>오늘 {counts.today ?? 0}건</>,
    },
    {
      id: "week",
      label: <>이번 주 {counts.thisWeek ?? 0}건</>,
    },
    {
      id: "next-30d",
      label: <>30일 내 {counts.next30d ?? 0}건</>,
    },
    {
      id: "stale",
      label: <>오래된 추정 {counts.staleEstimate ?? 0}건</>,
    },
  ];

  return (
    <ResearchHeader
      eyebrow="MARKET EVENTS"
      facts={facts}
      kicker="다가오는 시장 이벤트 브리프"
      meta={meta}
      summary={boundaryNote || "공식 일정과 추정 일정을 구분해서 확인합니다."}
      title={title || "다가오는 시장 이벤트 브리프"}
      titleId="events-hero-title"
      variant="events"
    />
  );
}

export default EventsHero;
import ResearchHeader from "../../market_research_header/ResearchHeader";
import type {
  ResearchHeaderFact,
  ResearchHeaderMeta,
} from "../../market_research_header/ResearchHeader";
