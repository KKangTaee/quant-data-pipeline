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
    hero.observation_mode === "INTRADAY_PROVISIONAL" && hero.observation_status === "PARTIAL"
      ? "caution"
      : hero.observation_status === "OBSERVED"
      ? "info"
      : hero.observation_status === "PARTIAL"
        ? "caution"
        : "neutral";
  const facts: ResearchHeaderFact[] = [
    {
      id: "observation",
      label: "현재 관측",
      value: hero.observation_label || OBSERVATION_LABEL[hero.observation_status],
      tone: observationTone,
      showIndicator: true,
    },
    {
      id: "as-of",
      label: "현재 기준일",
      value: hero.as_of_date || "-",
    },
    {
      id: "completed-as-of",
      label: "검증 기준일",
      value: hero.completed_as_of_date || "-",
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
  const notice = hero.observation_mode === "INTRADAY_PROVISIONAL" ? (
    <>
      <strong>{hero.as_of_date} 세션을 장중 잠정 관측으로 반영했습니다.</strong>
      <span>
        {hero.observation_detail}
        {hero.observed_at_et ? ` 관측 시각 ${hero.observed_at_et}` : ""}
      </span>
    </>
  ) : hasPendingSession ? (
    <>
      <strong>{sessionEvidence.pending_session} 세션은 현재 관측에 사용하지 못했습니다.</strong>
      <span>{hero.observation_detail} 완료 기준일 {hero.completed_as_of_date}</span>
    </>
  ) : undefined;

  return (
    <ResearchHeader
      actions={actions}
      detail={hero.today_summary ? <>완료 일봉 배경 · {hero.today_summary}</> : undefined}
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
