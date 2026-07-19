import { displayValue, signedValue } from "./SentimentWorkbench";
import type { SentimentWorkbenchPayload } from "./SentimentWorkbench";

type Props = {
  outlook: SentimentWorkbenchPayload["outlook"];
};

function SentimentOutlookSection({ outlook }: Props) {
  return (
    <section className="sentiment-workbench__outlook-section" aria-labelledby="sentiment-outlook-title">
      <div className="sentiment-workbench__section-heading">
        <div><span>Outlook</span><h3 id="sentiment-outlook-title">기간별 심리 경로</h3></div>
        <small>1W와 1M을 분리해 검증 상태부터 확인</small>
      </div>
      <div className="sentiment-workbench__outlook-grid">
        {outlook.horizons.map((horizon) => {
          const canPublish = horizon.status !== "UNAVAILABLE"
            && horizon.validation_evidence.length > 0
            && horizon.probabilities.length > 0;
          return (
            <article className="sentiment-workbench__outlook-card" data-horizon={horizon.key} key={horizon.key}>
              <header>
                <div><span>{horizon.key}</span><strong>{horizon.period_label}</strong></div>
                <b className={`sentiment-workbench__outlook-status sentiment-workbench__outlook-status--${horizon.status.toLowerCase()}`}>{horizon.status_label}</b>
              </header>
              {horizon.status === "UNAVAILABLE" || !canPublish ? (
                <div className="sentiment-workbench__outlook-unavailable">
                  <strong>검증 전 비공개</strong>
                  <p>{horizon.status_reason}</p>
                  <small>검증된 에피소드 표본과 기준선이 없으면 확률을 임의 생성하지 않습니다.</small>
                </div>
              ) : (
                <div className="sentiment-workbench__outlook-probabilities">
                  {horizon.probabilities.map((probability) => (
                    <div key={probability.key || probability.label}>
                      <span>{probability.label}</span>
                      <strong>{displayValue(probability.value, "%")}</strong>
                      <small>기준 대비 {signedValue(probability.difference_pp, "pp")}</small>
                    </div>
                  ))}
                  <small>검증 에피소드 {horizon.episode_count}개 · 기준선 {displayValue(horizon.baseline, "%")}</small>
                </div>
              )}
            </article>
          );
        })}
      </div>
      <p className="sentiment-workbench__outlook-summary">{outlook.summary}</p>
    </section>
  );
}

export default SentimentOutlookSection;
