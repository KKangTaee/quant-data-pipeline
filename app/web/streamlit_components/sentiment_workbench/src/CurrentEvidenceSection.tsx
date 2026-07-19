import { displayValue, signedValue } from "./SentimentWorkbench";
import type { AaiiComparison, SentimentAxis } from "./SentimentWorkbench";

type SourceEvidenceProps = {
  axis: SentimentAxis;
  kind: "cnn" | "aaii";
  aaiiComparison: AaiiComparison[];
};

function SourceEvidenceBox({ axis, kind, aaiiComparison }: SourceEvidenceProps) {
  const balance = axis.component_balance;
  const responses = axis.responses;
  const bullishComparison = aaiiComparison.find((item) => item.key === "bullish");
  return (
    <article className={`sentiment-workbench__source-box sentiment-workbench__source-box--${kind}`}>
      <header>
        <div><span>{kind === "cnn" ? "CNN 시장 행동" : "AAII 투자자 설문"}</span><small>{axis.source}</small></div>
        <b>{axis.direction_label}</b>
      </header>
      {axis.available ? (
        <>
          <div className="sentiment-workbench__source-value">
            <strong>{displayValue(axis.current, kind === "aaii" ? "pp" : "")}</strong>
            <span>직전 대비 {signedValue(axis.change, kind === "aaii" ? "pp" : "p")}</span>
          </div>
          <small>기준 {axis.latest_date || "-"} · 직전 {axis.previous_date || "-"}</small>
        </>
      ) : <div className="sentiment-workbench__source-empty">관측값 없음 · 판정 보류</div>}
      <div className="sentiment-workbench__source-breakdown">
        {kind === "cnn" ? (
          <>
            <span>탐욕 <b>{balance?.greed_count ?? 0}</b></span>
            <span>중립 <b>{balance?.neutral_count ?? 0}</b></span>
            <span>공포 <b>{balance?.fear_count ?? 0}</b></span>
          </>
        ) : (
          <>
            <span>Bullish <b>{displayValue(responses?.bullish, "%")}</b></span>
            <span>Neutral <b>{displayValue(responses?.neutral, "%")}</b></span>
            <span>Bearish <b>{displayValue(responses?.bearish, "%")}</b></span>
          </>
        )}
      </div>
      <p>
        {kind === "cnn"
          ? axis.components_support
          : `Bullish 장기평균 대비 ${signedValue(bullishComparison?.difference_pp, "pp")} · ${axis.detail || ""}`}
      </p>
      <small>{axis.range?.sample_count ?? 0}개 관측 · {axis.range?.position_label || "자료 부족"}</small>
    </article>
  );
}

type Props = {
  axes: { market_behavior: SentimentAxis; investor_survey: SentimentAxis };
  aaiiComparison: AaiiComparison[];
};

function CurrentEvidenceSection({ axes, aaiiComparison }: Props) {
  return (
    <section className="sentiment-workbench__current-section" aria-labelledby="sentiment-current-title">
      <div className="sentiment-workbench__section-heading">
        <div><span>Current evidence</span><h3 id="sentiment-current-title">두 축의 현재 근거</h3></div>
        <small>행동과 인식을 같은 깊이로 비교</small>
      </div>
      <div className="sentiment-workbench__source-grid">
        <SourceEvidenceBox aaiiComparison={aaiiComparison} axis={axes.market_behavior} kind="cnn" />
        <SourceEvidenceBox aaiiComparison={aaiiComparison} axis={axes.investor_survey} kind="aaii" />
      </div>
    </section>
  );
}

export default CurrentEvidenceSection;
