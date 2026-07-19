import { OBSERVATION_LABEL } from "./FuturesMacroWorkbench";
import type { HorizonCard, ProbabilityRow } from "./FuturesMacroWorkbench";

function ProbabilityBar({ row }: { row: ProbabilityRow }) {
  const value = Math.max(0, Math.min(1, row.value));
  const lift = Math.round(row.lift * 100);
  return (
    <div className="fm-workbench__probability-row">
      <span>{row.label}</span>
      <div className="fm-workbench__probability-track"><i style={{ width: `${Math.round(value * 100)}%` }} /></div>
      <strong>{Math.round(value * 100)}%</strong>
      <small>평소 {Math.round(row.baseline * 100)}% · {lift >= 0 ? "+" : ""}{lift}%p</small>
    </div>
  );
}

function PatternHorizonSection({ horizons }: { horizons: HorizonCard[] }) {
  return (
    <section className="fm-workbench__horizon-section" aria-labelledby="fm-horizon-title">
      <div className="fm-workbench__section-heading">
        <div><span>Probability path</span><h3 id="fm-horizon-title">현재와 다음 1주·1개월</h3></div>
        <small>현재는 관측 · 미래는 조건부 분포</small>
      </div>
      <div className="fm-workbench__horizon-grid">
        {horizons.map((item) => {
          const isObservation = item.kind === "observation";
          const probabilities = isObservation ? [] : item.probabilities;
          const hasPublishedDistribution = !isObservation && probabilities.length > 0;
          const statusClass = isObservation
            ? `observation-${item.observation_status.toLowerCase()}`
            : `estimate-${item.estimate_status.toLowerCase()}`;
          const statusLabel = isObservation
            ? OBSERVATION_LABEL[item.observation_status]
            : item.estimate_status;
          return (
            <article className={`fm-workbench__horizon-card ${statusClass}`} key={item.key}>
              <header>
                <div><span>{item.label}</span><strong>{item.title}</strong></div>
                <b>{statusLabel}</b>
              </header>
              <p>{item.summary}</p>
              {hasPublishedDistribution ? (
                <div className="fm-workbench__probabilities">
                  {probabilities.map((row) => <ProbabilityBar key={row.key} row={row} />)}
                </div>
              ) : (
                <div className="fm-workbench__no-edge">{item.edge_label || "방향 우위 미확인"}</div>
              )}
              <footer>
                {!isObservation && item.episode_count ? <span>독립 표본 {item.episode_count}개</span> : <span>확률이 아닌 현재 관측</span>}
                {item.status_reason ? <small>{item.status_reason}</small> : null}
              </footer>
            </article>
          );
        })}
      </div>
    </section>
  );
}

export default PatternHorizonSection;
