import type { ShortHorizonDecisionPayload } from "./FuturesMacroWorkbench";

function ShortHorizonDecisionSection({ decision }: { decision: ShortHorizonDecisionPayload }) {
  return (
    <section className="fm-workbench__decision" aria-labelledby="fm-decision-title">
      <div className="fm-workbench__section-heading">
        <div>
          <span>Short-horizon reading</span>
          <h3 id="fm-decision-title">단기 방향 판단 흐름</h3>
        </div>
        <small aria-label="최근 1거래일, 최근 5거래일, 최근 20거래일 관측 범위">
          1D 변화 → 5D 현재 방향 → 20D 배경 관계 순서로 읽습니다
        </small>
      </div>
      <div className="fm-workbench__window-rail">
        {decision.observation_windows.map((window) => (
          <div key={window.key}>
            <span>{window.label}</span>
            <strong>{window.role}</strong>
          </div>
        ))}
      </div>
      <div className="fm-workbench__decision-steps">
        {decision.observation_cards.map((card, index) => (
          <article className={`observation-card observation-${card.key.toLowerCase()}`} key={card.key}>
            <b>{index + 1}</b>
            <div>
              <span>현재 관측 · {card.key}</span>
              <h4>{card.title}</h4>
              <p>{card.summary}</p>
              <small>{card.detail}</small>
            </div>
          </article>
        ))}
      </div>
    </section>
  );
}

export default ShortHorizonDecisionSection;
