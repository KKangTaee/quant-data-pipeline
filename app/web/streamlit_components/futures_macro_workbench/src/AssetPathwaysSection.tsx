import type { AssetPathwayPayload } from "./FuturesMacroWorkbench";

function AssetPathwaysSection({ pathways }: { pathways: AssetPathwayPayload[] }) {
  return (
    <section className="fm-workbench__asset-section" aria-labelledby="fm-asset-title">
      <div className="fm-workbench__section-heading">
        <div><span>Measured pathways</span><h3 id="fm-asset-title">자산별 확인 포인트</h3></div>
        <small>전체 체제의 보조 근거</small>
      </div>
      <div className="fm-workbench__asset-grid">
        {pathways.map((item) => (
          <article className={`estimate-${item.estimate_status.toLowerCase()}`} key={item.key}>
            <header><strong>{item.label}</strong><b>{item.estimate_status}</b></header>
            <div className="fm-workbench__asset-current">
              <span><small>1D</small>{item.current.one_day}</span>
              <span><small>5D</small>{item.current.five_day}</span>
              <span><small>20D</small>{item.current.twenty_day}</span>
            </div>
            <div className="fm-workbench__asset-outlook">
              <span>다음 5D <strong>{item.outlook.five_day}</strong></span>
              <span>다음 20D <strong>{item.outlook.twenty_day}</strong></span>
            </div>
            <p>{item.change_condition}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default AssetPathwaysSection;
