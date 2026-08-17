import type { MarketRepricingPayload } from "./FuturesMacroWorkbench";

function EvidenceList({ items, empty }: { items: string[]; empty: string }) {
  if (items.length === 0) {
    return <p className="fm-workbench__repricing-empty">{empty}</p>;
  }
  return <ul>{items.map((item) => <li key={item}>{item}</li>)}</ul>;
}

function MarketRepricingSection({ radar }: { radar: MarketRepricingPayload }) {
  const scenario = radar.conditional_scenario;
  return (
    <section className="fm-workbench__repricing" aria-labelledby="fm-repricing-title">
      <div className="fm-workbench__repricing-heading">
        <div>
          <span>Macro repricing</span>
          <h3 id="fm-repricing-title">시장 재가격화 해석</h3>
        </div>
        <b className={`status-${radar.status.toLowerCase()}`}>{radar.confidence_label}</b>
      </div>
      <div className="fm-workbench__repricing-headline">
        <strong>{radar.headline}</strong>
        <p>{radar.interpretation}</p>
      </div>
      <div className="fm-workbench__repricing-grid">
        <article>
          <span>유력한 해석</span>
          <EvidenceList
            items={radar.supporting_evidence}
            empty="현재 해석을 뒷받침하는 뚜렷한 핵심축이 없습니다."
          />
        </article>
        <article>
          <span>반대 근거</span>
          <EvidenceList
            items={radar.counter_evidence}
            empty="현재 관측에서 뚜렷한 반대 근거는 없습니다."
          />
        </article>
        <article className="fm-workbench__repricing-scenario">
          <span>조건부 시나리오</span>
          <p>{scenario.summary}</p>
          <dl>
            <div><dt>지속 조건</dt><dd>{scenario.continuation_condition}</dd></div>
            <div><dt>무효화 조건</dt><dd>{scenario.invalidation_condition}</dd></div>
          </dl>
          {scenario.sensitive_assets.length > 0 ? (
            <div className="fm-workbench__repricing-assets" aria-label="민감 영역">
              {scenario.sensitive_assets.map((item) => <small key={item}>{item}</small>)}
            </div>
          ) : null}
        </article>
      </div>
    </section>
  );
}

export default MarketRepricingSection;
