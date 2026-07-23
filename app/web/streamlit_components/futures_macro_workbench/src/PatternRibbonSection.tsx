import type { CSSProperties } from "react";
import type { RibbonPayload } from "./FuturesMacroWorkbench";

function PatternRibbonSection({ ribbon }: { ribbon: RibbonPayload }) {
  return (
    <section className="fm-workbench__ribbon-section" aria-labelledby="fm-ribbon-title">
      <div className="fm-workbench__section-heading">
        <div><span>Regime history</span><h3 id="fm-ribbon-title">최근 체제 이력</h3></div>
        <small>색은 체제 · 사선은 전환 상태</small>
      </div>
      {ribbon.items.length > 0 ? (
        <>
          <div className="fm-workbench__ribbon" style={{ "--ribbon-count": Math.max(1, ribbon.items.length) } as CSSProperties}>
            {ribbon.items.map((item) => (
              <span
                aria-label={`${item.date} · ${item.regime_label} · ${item.transition_label}`}
                className={`regime-${item.regime} transition-${item.transition}`}
                key={item.date}
                role="img"
                tabIndex={0}
                title={`${item.date} · ${item.regime_label} · ${item.transition_label}`}
              />
            ))}
          </div>
          <div className="fm-workbench__ribbon-legend" aria-label="최근 60거래일 체제 색상 범례">
            <small>과거 → 최근</small>
            <span className="legend-risk_seeking"><i />위험선호</span>
            <span className="legend-defensive"><i />방어</span>
            <span className="legend-inflation_rate_pressure"><i />물가·금리 부담</span>
            <span className="legend-mixed"><i />혼재</span>
            <span className="legend-transition"><i />전환 시도</span>
          </div>
        </>
      ) : <div className="fm-workbench__empty">표시할 체제 경로가 아직 없습니다.</div>}
    </section>
  );
}

export default PatternRibbonSection;
