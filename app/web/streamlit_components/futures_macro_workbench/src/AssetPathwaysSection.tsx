import { OBSERVATION_LABEL } from "./FuturesMacroWorkbench";
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
          <article className={`observation-${item.observation_status.toLowerCase()}`} key={item.key}>
            <header><strong>{item.label}</strong><b>{OBSERVATION_LABEL[item.observation_status]}</b></header>
            <div className="fm-workbench__asset-current">
              <span><small>1D</small>{item.current.one_day}</span>
              <span><small>5D</small>{item.current.five_day}</span>
              <span><small>20D</small>{item.current.twenty_day}</span>
            </div>
            <div className="fm-workbench__asset-outlook">
              <span>
                <small>다음 5D</small>
                <strong>{item.outlook.five_day}</strong>
                <b className={`estimate-${item.outlook.five_day_status.toLowerCase()}`}>{item.outlook.five_day_status}</b>
              </span>
              <span>
                <small>다음 20D</small>
                <strong>{item.outlook.twenty_day}</strong>
                <b className={`estimate-${item.outlook.twenty_day_status.toLowerCase()}`}>{item.outlook.twenty_day_status}</b>
              </span>
            </div>
            <p>{item.change_condition}</p>
          </article>
        ))}
      </div>
    </section>
  );
}

export default AssetPathwaysSection;
