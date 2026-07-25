import ResearchHeader from "../../market_research_header/ResearchHeader";
import type {
  ResearchHeaderAction,
  ResearchHeaderFact,
  ResearchHeaderMeta,
} from "../../market_research_header/ResearchHeader";

type EventsHeroCounts = {
  today?: number;
  thisWeek?: number;
  next30d?: number;
  staleEstimate?: number;
};

export function buildEventsHeroCounts(
  counts: Record<string, number> | undefined,
  calendarDays: Array<{ stale_count?: number }>,
): EventsHeroCounts {
  return {
    next30d: counts?.next_30d ?? 0,
    staleEstimate: calendarDays.reduce(
      (total, day) => total + (day.stale_count ?? 0),
      0,
    ),
    thisWeek: counts?.this_week ?? 0,
    today: counts?.today ?? 0,
  };
}

type EventsHeroNextEvent = {
  date: string;
  title: string;
};

type EventsHeroPrimaryAction = {
  disabled: boolean;
  label: string;
  onClick: () => void;
};

type Props = {
  boundaryNote: string;
  counts: EventsHeroCounts;
  nextEvent?: EventsHeroNextEvent | null;
  primaryAction?: EventsHeroPrimaryAction;
  title: string;
};

function EventsHero({
  boundaryNote,
  counts,
  nextEvent,
  primaryAction,
  title,
}: Props) {
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
  const actions: ResearchHeaderAction[] = primaryAction
    ? [{
        id: "refresh-official",
        label: primaryAction.label,
        kind: "primary",
        disabled: primaryAction.disabled,
        onClick: primaryAction.onClick,
      }]
    : [];

  return (
    <ResearchHeader
      actions={actions}
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
