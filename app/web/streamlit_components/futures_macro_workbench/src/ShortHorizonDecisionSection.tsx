import type { ShortHorizonDecisionPayload } from "./FuturesMacroWorkbench";

function ShortHorizonDecisionSection({ decision }: { decision: ShortHorizonDecisionPayload }) {
  const validation = decision.future_five_day_validation;
  return (
    <section className="fm-workbench__decision" aria-labelledby="fm-decision-title">
      <div className="fm-workbench__section-heading">
        <div>
          <span>Short-horizon reading</span>
          <h3 id="fm-decision-title">단기 방향 판단 흐름</h3>
        </div>
        <small aria-label="최근 1거래일, 최근 5거래일, 최근 20거래일 관측 범위">
          최근 관측과 향후 5거래일 검증을 구분합니다
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
        <article>
          <b>1</b>
          <div><span>관측</span><h4>{decision.one_day_shock.title}</h4><p>{decision.one_day_shock.summary}</p></div>
        </article>
        <article>
          <b>2</b>
          <div><span>판단</span><h4>{decision.five_day_direction.title}</h4><p>{decision.five_day_direction.summary}</p></div>
        </article>
        <article className={`estimate-${validation.status.toLowerCase()}`}>
          <b>3</b>
          <div>
            <span>향후 5거래일 · 검증 결론</span>
            <h4>{validation.title}</h4>
            <p>{validation.detail}</p>
            {validation.episode_count > 0 ? <small>독립 표본 {validation.episode_count}개</small> : null}
          </div>
        </article>
      </div>
    </section>
  );
}

export default ShortHorizonDecisionSection;
