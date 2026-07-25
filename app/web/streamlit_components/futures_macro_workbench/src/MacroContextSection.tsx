import ResearchHeader from "../../market_research_header/ResearchHeader";
import type {
  ResearchHeaderAction,
  ResearchHeaderFact,
  ResearchHeaderMeta,
  ResearchHeaderTone,
} from "../../market_research_header/ResearchHeader";
import { OBSERVATION_LABEL } from "./presentation";
import type {
  CommandPayload,
  FuturesMacroAction,
  HeroPayload,
  SessionEvidence,
} from "./contracts";

type Props = {
  command: CommandPayload;
  hero: HeroPayload;
  sessionEvidence: SessionEvidence;
  pendingActionId: string;
  onAction: (action: FuturesMacroAction) => void;
};

function MacroContextSection({ command, hero, sessionEvidence, pendingActionId, onAction }: Props) {
  const hasPendingSession =
    sessionEvidence.status === "PENDING_SESSION_FINALIZATION" &&
    Boolean(sessionEvidence.pending_session);
  const observationTone: ResearchHeaderTone =
    hero.observation_status === "OBSERVED"
      ? "info"
      : hero.observation_status === "PARTIAL"
        ? "caution"
        : "neutral";
  const facts: ResearchHeaderFact[] = [
    {
      id: "observation",
      label: "관측 상태",
      value: OBSERVATION_LABEL[hero.observation_status],
      tone: observationTone,
      showIndicator: true,
    },
    {
      id: "as-of",
      label: "기준일",
      value: hero.as_of_date || "-",
    },
    {
      id: "coverage",
      label: "관측 범위",
      value: hero.coverage_label || "-",
    },
  ];
  const actions: ResearchHeaderAction[] = command.actions.map((action) => ({
    id: action.id,
    label: pendingActionId === action.id ? "요청 중" : action.label,
    kind: action.kind,
    title: action.detail,
    disabled: pendingActionId === action.id,
    onClick: () => onAction(action),
  }));
  const meta: ResearchHeaderMeta[] = [
    ...(command.detail ? [{ id: "command-detail", label: command.detail }] : []),
    ...hero.evidence.slice(0, 3).map((label, index) => ({
      id: `evidence-${index}`,
      label,
    })),
  ];
  const notice = hasPendingSession ? (
    <>
      <strong>{sessionEvidence.pending_session} 데이터는 완료 전이라 현재 위치와 전망에서 제외했습니다.</strong>
      <span>화면은 마지막 완료 세션 {sessionEvidence.latest_final_session || hero.as_of_date} 기준입니다.</span>
    </>
  ) : undefined;

  return (
    <ResearchHeader
      actions={actions}
      detail={hero.today_summary ? <>오늘의 재가격화 · {hero.today_summary}</> : undefined}
      eyebrow="FUTURES MACRO"
      facts={facts}
      kicker={hero.kicker}
      meta={meta}
      notice={notice}
      summary={hero.summary}
      title={hero.title}
      titleId="fm-hero-title"
      transition={hero.transition_label}
      variant="futures"
    />
  );
}

export default MacroContextSection;
