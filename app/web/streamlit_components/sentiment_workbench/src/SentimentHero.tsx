import ResearchHeader from "../../market_research_header/ResearchHeader";
import type {
  ResearchHeaderAction,
  ResearchHeaderFact,
  ResearchHeaderMeta,
  ResearchHeaderTone,
} from "../../market_research_header/ResearchHeader";
import type { SentimentAction, SentimentWorkbenchPayload } from "./SentimentWorkbench";

type Props = {
  payload: SentimentWorkbenchPayload;
  pendingActionLabel: string;
  onAction: (action: SentimentAction) => void;
};

function sentimentTone(value: string): ResearchHeaderTone {
  if (value === "positive") return "positive";
  if (value === "warning") return "caution";
  if (value === "danger") return "negative";
  return value === "primary" ? "info" : "neutral";
}

function SentimentHero({ payload, pendingActionLabel, onAction }: Props) {
  const facts: ResearchHeaderFact[] = [
    {
      id: "cnn",
      label: "CNN 시장 행동",
      value: payload.axes.market_behavior.direction_label,
      tone: sentimentTone(payload.axes.market_behavior.tone),
      showIndicator: true,
    },
    {
      id: "aaii",
      label: "AAII 투자자 설문",
      value: payload.axes.investor_survey.direction_label,
      tone: sentimentTone(payload.axes.investor_survey.tone),
      showIndicator: true,
    },
  ];
  const actions: ResearchHeaderAction[] = payload.command.actions.map((action) => ({
    id: action.id,
    label: action.label,
    kind: action.kind,
    title: action.detail,
    onClick: () => onAction(action),
  }));
  const meta: ResearchHeaderMeta[] = [
    {
      id: "cnn-date",
      label: <>CNN {payload.axes.market_behavior.latest_date || "-"}</>,
    },
    {
      id: "aaii-date",
      label: <>AAII {payload.axes.investor_survey.latest_date || "-"}</>,
    },
    {
      id: "no-score",
      label: "합성점수 없음",
    },
    {
      id: "no-trade",
      label: "매수·매도 신호 아님",
    },
    ...(payload.freshness.stale_count > 0
      ? [
          {
            id: "stale",
            label: <>stale {payload.freshness.stale_count} · 상세 근거 확인</>,
          },
        ]
      : []),
  ];

  return (
    <ResearchHeader
      actionFeedback={pendingActionLabel ? <>요청 전송 · {pendingActionLabel}</> : undefined}
      actions={actions}
      detail={payload.cross_read.confidence_note}
      eyebrow="MARKET PSYCHOLOGY · CROSS READ"
      facts={facts}
      kicker={payload.cross_read.status}
      meta={meta}
      summary={payload.cross_read.meaning}
      title={payload.summary.headline}
      titleId="sentiment-hero-title"
      transition={payload.summary.phase_label}
      variant="sentiment"
    />
  );
}

export default SentimentHero;
