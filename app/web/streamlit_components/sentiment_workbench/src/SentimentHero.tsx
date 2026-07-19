import type { SentimentAction, SentimentWorkbenchPayload } from "./SentimentWorkbench";

type Props = {
  payload: SentimentWorkbenchPayload;
  pendingActionLabel: string;
  onAction: (action: SentimentAction) => void;
};

function SentimentHero({ payload, pendingActionLabel, onAction }: Props) {
  return (
    <section className="sentiment-workbench__hero" aria-labelledby="sentiment-hero-title">
      <div className="sentiment-workbench__command-row">
        <div>
          <span className="sentiment-workbench__eyebrow">Market psychology · cross read</span>
          <small>CNN 시장 행동 × AAII 개인투자자 설문</small>
        </div>
        <div className="sentiment-workbench__actions" aria-label="시장 심리 자료 동작">
          {payload.command.actions.map((action) => (
            <button
              className={`sentiment-workbench__action sentiment-workbench__action--${action.kind}`}
              key={action.id}
              onClick={() => onAction(action)}
              title={action.detail}
              type="button"
            >
              {action.label}
            </button>
          ))}
          {pendingActionLabel ? (
            <span className="sentiment-workbench__action-feedback">요청 전송 · {pendingActionLabel}</span>
          ) : null}
        </div>
      </div>
      <div className="sentiment-workbench__hero-grid">
        <div className="sentiment-workbench__hero-copy">
          <span className="sentiment-workbench__kicker">{payload.cross_read.status}</span>
          <h2 className="sentiment-workbench__headline" id="sentiment-hero-title">{payload.summary.headline}</h2>
          <div className="sentiment-workbench__transition">{payload.summary.phase_label}</div>
          <p className="sentiment-workbench__summary-copy">{payload.cross_read.meaning}</p>
          {payload.cross_read.confidence_note ? <small>{payload.cross_read.confidence_note}</small> : null}
        </div>
        <aside className="sentiment-workbench__hero-side">
          <div><span>CNN 시장 행동</span><strong>{payload.axes.market_behavior.direction_label}</strong></div>
          <div><span>AAII 투자자 설문</span><strong>{payload.axes.investor_survey.direction_label}</strong></div>
        </aside>
      </div>
      <div className="sentiment-workbench__hero-meta">
        <span>CNN {payload.axes.market_behavior.latest_date || "-"}</span>
        <span>AAII {payload.axes.investor_survey.latest_date || "-"}</span>
        <span>합성점수 없음</span>
        <span>매수·매도 신호 아님</span>
        {payload.freshness.stale_count > 0 ? (
          <span>stale {payload.freshness.stale_count} · 상세 근거 확인</span>
        ) : null}
      </div>
    </section>
  );
}

export default SentimentHero;
