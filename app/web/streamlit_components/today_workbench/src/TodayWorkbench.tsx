import { useEffect, useRef } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";

import MarketSessionClock from "./MarketSessionClock";
import TodayPortfolioPanel from "./TodayPortfolioPanel";
import type {
  EvidenceRow,
  MarketSessionPhase,
  TodayEventId,
  TodayPayload,
  TodayPortfolioIslandPayload,
  TodayWorkbenchView,
} from "./types";
import "./style.css";

type Props = Omit<ComponentProps, "args"> & {
  args: {
    payload?: TodayPayload | TodayPortfolioIslandPayload;
    view?: TodayWorkbenchView;
  };
};

type ContextProps = {
  payload: TodayPayload;
  onPhaseChange: (phase: MarketSessionPhase) => void;
};

type ActionsProps = {
  onEvent: (id: TodayEventId) => void;
};

function EvidenceCard({ row }: { row: EvidenceRow }) {
  return (
    <article className="today-evidence-card">
      <header>
        <span>{row.label}</span>
        <b className={`today-signal signal-${row.signal_level}`}>{row.signal_label}</b>
      </header>
      <h3>{row.title}</h3>
      <p>{row.detail}</p>
      <footer>
        <strong>{row.risk_label}</strong>
        <span>{row.data_quality_label} · 기준 {row.as_of_date ?? "-"}</span>
      </footer>
    </article>
  );
}

export function TodayContextView({ payload, onPhaseChange }: ContextProps) {
  const nextEvent = payload.market.next_event;

  return (
    <>
      <section className="today-hero">
        <div>
          <span className="today-eyebrow">TODAY · MARKET &amp; PORTFOLIO</span>
          <h1>오늘의 시장 판단</h1>
          <p>{payload.market.headline}</p>
        </div>
        <aside>
          <span>{payload.header.as_of_date ?? "-"} 기준</span>
          <strong>{payload.header.status_label}</strong>
          <b>{payload.header.source_ready_count}/{payload.header.source_count} READY</b>
        </aside>
      </section>

      <MarketSessionClock
        marketSession={payload.market_session}
        onPhaseChange={onPhaseChange}
      />

      <section className="today-context-grid">
        <section className="today-panel">
          <header className="today-section-heading">
            <div><span>MARKET EVIDENCE</span><h2>판단 근거</h2></div>
            <small>저장 근거 {payload.market.evidence.length}개</small>
          </header>
          <div className="today-signal-legend" aria-label="신호 분류">
            <span className="signal-support">● 지지</span>
            <span className="signal-neutral">● 중립</span>
            <span className="signal-watch">● 주의</span>
            <span className="signal-limited">● 자료 제한</span>
          </div>
          <div className="today-evidence-grid">
            {payload.market.evidence.map((row) => <EvidenceCard key={row.key} row={row} />)}
          </div>
        </section>

        <section className="today-panel today-events-panel">
          <header className="today-section-heading">
            <div><span>NEXT CHECK</span><h2>다음 일정 · 주의</h2></div>
            <small>중요도 우선</small>
          </header>
          {nextEvent ? (
            <article className="today-event-card">
              <b>{nextEvent.date ?? "-"} · D-{nextEvent.days_until}</b>
              <h3>{nextEvent.title}</h3>
              <p>{nextEvent.type} · {nextEvent.importance}</p>
            </article>
          ) : <div className="today-compact-empty">예정된 주요 일정이 없습니다.</div>}
          <ul className="today-watch-list">
            {payload.market.watch_items.map((item) => <li key={item}>{item}</li>)}
          </ul>
        </section>
      </section>
    </>
  );
}

export function TodayActionsView({ onEvent }: ActionsProps) {
  return (
    <section className="today-action-section">
      <header className="today-section-heading">
        <div><span>NEXT ACTION</span><h2>다음 확인</h2></div>
      </header>
      <div className="today-action-rail">
        <button type="button" onClick={() => onEvent("open_market_research")}>
          시장 근거 자세히 보기 <b>→</b>
        </button>
        <button type="button" onClick={() => onEvent("open_stock_research")}>
          영향이 큰 종목 조사 <b>→</b>
        </button>
        <button type="button" onClick={() => onEvent("open_portfolio_monitoring")}>
          포트폴리오 전체 점검 <b>→</b>
        </button>
      </div>
    </section>
  );
}

function fullPayload(
  payload: TodayPayload | TodayPortfolioIslandPayload | undefined,
): TodayPayload | null {
  return payload?.schema_version === "today_home_v4" ? payload : null;
}

function TodayWorkbench({ args, width }: Props) {
  const payload = args.payload;
  const view = args.view ?? "full";
  const rootRef = useRef<HTMLElement | null>(null);

  useEffect(() => {
    Streamlit.setFrameHeight();
    if (!rootRef.current || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => Streamlit.setFrameHeight());
    observer.observe(rootRef.current);
    return () => observer.disconnect();
  }, [payload, view, width]);

  if (!payload) {
    return <div className="today-component-empty">Today payload를 불러오지 못했습니다.</div>;
  }

  const emit = (id: TodayEventId) => Streamlit.setComponentValue({ event: { id } });
  const emitPhaseChange = (phase: MarketSessionPhase) => {
    Streamlit.setComponentValue({ event: { id: "market_phase_changed", phase } });
  };
  const full = fullPayload(payload);
  const portfolio = payload.portfolio;

  if ((view === "context" || view === "actions" || view === "full") && !full) {
    return <div className="today-component-empty">Today 전체 payload가 필요합니다.</div>;
  }

  return (
    <main className={`today-workbench view-${view}`} ref={rootRef}>
      {(view === "context" || view === "full") && full
        ? <TodayContextView payload={full} onPhaseChange={emitPhaseChange} />
        : null}
      {(view === "portfolio" || view === "full")
        ? <TodayPortfolioPanel portfolio={portfolio} viewportWidth={width} />
        : null}
      {(view === "actions" || view === "full")
        ? <TodayActionsView onEvent={emit} />
        : null}
    </main>
  );
}

export default withStreamlitConnection(TodayWorkbench);
