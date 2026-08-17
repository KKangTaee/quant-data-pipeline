import React from "react";
import { STUDIO_DESTINATIONS, studioDestination, type StudioView } from "./workbenchState";

type Props = {
  activeView: StudioView;
  managerName: string;
  periodLabel: string;
  isPreview: boolean;
  onViewChange: (view: StudioView) => void;
  managerControl: React.ReactNode;
  freshnessControl: React.ReactNode;
  children: React.ReactNode;
};

export function InstitutionalStudioShell({
  activeView,
  managerName,
  periodLabel,
  isPreview,
  onViewChange,
  managerControl,
  freshnessControl,
  children,
}: Props) {
  const activeDestination = studioDestination(activeView);

  return (
    <div className="ip-institutional-shell">
      <header className="ip-institutional-page-header">
        <div>
          <span className="ip-institutional-page-header__eyebrow">MARKET RESEARCH / INSTITUTIONAL HOLDINGS</span>
          <h1>기관 보유 분석</h1>
          <p>
            <strong>{managerName}</strong>
            <span>{periodLabel || "보고 분기 미수집"}</span>
            {isPreview ? <em>Preview</em> : null}
          </p>
        </div>
        <div className="ip-institutional-page-header__context">
          <span>현재 보기</span>
          <strong>{activeDestination.label}</strong>
        </div>
      </header>

      <section className="ip-institutional-controls" aria-label="기관과 데이터 기준 선택">
        {managerControl}
        {freshnessControl}
      </section>

      <nav className="ip-institutional-tabs" role="tablist" aria-label="기관 보유 분석 화면">
        {STUDIO_DESTINATIONS.map((item) => (
          <button
            key={item.id}
            type="button"
            role="tab"
            aria-selected={item.id === activeView}
            className={item.id === activeView ? "ip-institutional-tab--active" : ""}
            onClick={() => onViewChange(item.id)}
          >
            <strong>{item.label}</strong>
            <small>{item.description}</small>
          </button>
        ))}
      </nav>

      <section className="ip-institutional-canvas" role="tabpanel" aria-label={activeDestination.label}>
        {children}
      </section>
    </div>
  );
}
