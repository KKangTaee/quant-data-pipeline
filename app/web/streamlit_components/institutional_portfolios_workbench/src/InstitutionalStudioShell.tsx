import React, { useEffect, useRef } from "react";
import { STUDIO_DESTINATIONS, studioDestination, type StudioView } from "./workbenchState";

type Props = {
  activeView: StudioView;
  managerName: string;
  periodLabel: string;
  isPreview: boolean;
  drawerOpen: boolean;
  onDrawerOpen: () => void;
  onDrawerClose: () => void;
  onViewChange: (view: StudioView) => void;
  railContent: React.ReactNode;
  headerMeta: React.ReactNode;
  children: React.ReactNode;
};

export function InstitutionalStudioShell({
  activeView,
  managerName,
  periodLabel,
  isPreview,
  drawerOpen,
  onDrawerOpen,
  onDrawerClose,
  onViewChange,
  railContent,
  headerMeta,
  children,
}: Props) {
  const menuButtonRef = useRef<HTMLButtonElement | null>(null);
  const activeDestination = studioDestination(activeView);

  useEffect(() => {
    if (!drawerOpen) {
      return undefined;
    }
    const handleKeyDown = (event: KeyboardEvent) => {
      if (event.key === "Escape") {
        onDrawerClose();
        window.setTimeout(() => menuButtonRef.current?.focus(), 0);
      }
    };
    window.addEventListener("keydown", handleKeyDown);
    return () => window.removeEventListener("keydown", handleKeyDown);
  }, [drawerOpen, onDrawerClose]);

  const selectView = (view: StudioView) => {
    onViewChange(view);
    onDrawerClose();
  };

  return (
    <div className={`ip-studio ${drawerOpen ? "ip-studio--drawer-open" : ""}`}>
      <div className="ip-studio-mobile-bar">
        <button
          ref={menuButtonRef}
          type="button"
          className="ip-studio-mobile-bar__menu"
          aria-expanded={drawerOpen}
          aria-controls="ip-institutional-studio-rail"
          onClick={onDrawerOpen}
        >
          <span aria-hidden="true">☰</span>
          리서치 메뉴
        </button>
        <button type="button" className="ip-studio-mobile-bar__current" onClick={onDrawerOpen}>
          <span>{activeDestination.shortLabel}</span>
          <strong>{managerName}</strong>
        </button>
        <span className={`ip-studio-mobile-bar__state ${isPreview ? "is-preview" : ""}`}>
          {isPreview ? "Preview" : periodLabel}
        </span>
      </div>

      <button
        type="button"
        className="ip-studio-scrim"
        aria-label="리서치 메뉴 닫기"
        tabIndex={drawerOpen ? 0 : -1}
        onClick={onDrawerClose}
      />

      <aside id="ip-institutional-studio-rail" className="ip-studio-rail" aria-label="Institutional research studio">
        <div className="ip-studio-rail__brand">
          <span>RESEARCH STUDIO</span>
          <strong>Institutional Holdings</strong>
          <p>저장된 SEC 13F를 맥락부터 종목까지 탐색합니다.</p>
        </div>
        <button type="button" className="ip-studio-rail__close" onClick={onDrawerClose}>
          닫기 <span aria-hidden="true">×</span>
        </button>

        <nav className="ip-studio-nav" aria-label="리서치 목적지">
          <span className="ip-studio-rail__label">탐색</span>
          {STUDIO_DESTINATIONS.map((item, index) => (
            <button
              key={item.id}
              type="button"
              className={item.id === activeView ? "ip-studio-nav__active" : ""}
              aria-current={item.id === activeView ? "page" : undefined}
              onClick={() => selectView(item.id)}
            >
              <em>{String(index + 1).padStart(2, "0")}</em>
              <span>
                <strong>{item.label}</strong>
                <small>{item.description}</small>
              </span>
            </button>
          ))}
        </nav>

        {railContent}
      </aside>

      <section className="ip-studio-canvas">
        <header className="ip-studio-header">
          <div>
            <span className="ip-studio-header__eyebrow">INSTITUTIONAL HOLDINGS / {activeDestination.shortLabel}</span>
            <h1>{activeDestination.label}</h1>
          </div>
          <div className="ip-studio-header__meta">{headerMeta}</div>
        </header>
        {children}
      </section>
    </div>
  );
}
