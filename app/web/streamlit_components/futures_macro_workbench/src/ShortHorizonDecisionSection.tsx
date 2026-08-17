import type { ShortHorizonDecisionPayload } from "./FuturesMacroWorkbench";

function ShortHorizonDecisionSection({ decision }: { decision: ShortHorizonDecisionPayload }) {
  return (
    <section className="fm-workbench__decision" aria-labelledby="fm-decision-title">
      <div className="fm-workbench__section-heading">
        <div>
          <span>Short-horizon reading</span>
          <h3 id="fm-decision-title">단기 방향 판단 흐름</h3>
        </div>
      </div>
      <div className="fm-workbench__decision-steps">
        {decision.observation_cards.map((card, index) => (
          <article className={`observation-card observation-${card.key.toLowerCase()}`} key={card.key}>
            <b>{index + 1}</b>
            <div>
              <span>현재 관측 · {card.key}</span>
              <h4>{card.title}</h4>
              <p>{card.summary}</p>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default ShortHorizonDecisionSection;
