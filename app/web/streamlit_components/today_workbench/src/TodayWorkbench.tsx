import { useEffect, useRef, useState } from "react";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";

import TodayPortfolioChart from "./TodayPortfolioChart";
import {
  formatCountdown,
  displayPortfolio,
  formatSessionHours,
  formatZonedClock,
  resolveMarketSession,
  signedMoneyText,
} from "./presentation";
import type { EvidenceRow, TodayEventId, TodayPayload } from "./types";
import "./style.css";

type Props = Omit<ComponentProps, "args"> & { args: { payload?: TodayPayload } };

function moneyText(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "—";
  return new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(value);
}

function percentText(value: number | null) {
  if (value == null || !Number.isFinite(value)) return "—";
  return `${value > 0 ? "+" : ""}${(value * 100).toFixed(2)}%`;
}

function shortDate(value: string | null) {
  if (!value) return "-";
  const parts = value.slice(0, 10).split("-");
  return parts.length === 3 ? `${parts[1]}.${parts[2]}` : value;
}

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

function TodayWorkbench({ args, width }: Props) {
  const payload = args.payload;
  const rootRef = useRef<HTMLElement | null>(null);
  const [nowMs, setNowMs] = useState(() => Date.now());

  useEffect(() => {
    Streamlit.setFrameHeight();
    if (!rootRef.current || typeof ResizeObserver === "undefined") return;
    const observer = new ResizeObserver(() => Streamlit.setFrameHeight());
    observer.observe(rootRef.current);
    return () => observer.disconnect();
  }, [payload, width]);

  useEffect(() => {
    const timer = window.setInterval(() => setNowMs(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  if (!payload) {
    return <div className="today-component-empty">Today payload를 불러오지 못했습니다.</div>;
  }

  const emit = (id: TodayEventId) => Streamlit.setComponentValue({ event: { id } });
  const display = displayPortfolio(payload.portfolio);
  const recentTone = (display.latestObservationReturn ?? 0) < 0 ? "is-negative" : "is-positive";
  const totalTone = (display.totalReturn ?? 0) < 0 ? "is-negative" : "is-positive";
  const nextEvent = payload.market.next_event;
  const resolvedSession = resolveMarketSession(payload.market_session, nowMs);
  const phaseCopy = {
    PRE_OPEN: { label: "개장 전", countdown: "정규장 개장까지" },
    OPEN: { label: "장 진행 중", countdown: "정규장 마감까지" },
    CLOSED: { label: "정규장 마감", countdown: "다음 정규장 개장까지" },
    HOLIDAY: { label: "휴장", countdown: "다음 정규장 개장까지" },
    WEEKEND: { label: "휴장", countdown: "다음 정규장 개장까지" },
    STALE: { label: "일정 자료 부족", countdown: "새로고침 필요" },
  }[resolvedSession.phase];
  const displaySession = resolvedSession.today?.day_kind === "TRADING_DAY"
    ? resolvedSession.today
    : resolvedSession.nextTradingDay;
  const sessionNote = resolvedSession.phase === "HOLIDAY"
    ? resolvedSession.today?.holiday_label
    : resolvedSession.phase === "WEEKEND"
      ? "주말"
      : displaySession?.is_early_close
        ? "조기폐장"
        : payload.market_session.calendar_quality === "LIMITED"
          ? "일정 확인 필요"
          : null;
  const countdownText = resolvedSession.targetAtMs == null
    ? "새로고침 필요"
    : formatCountdown(resolvedSession.targetAtMs - nowMs);

  return (
    <main className="today-workbench" ref={rootRef}>
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

      <section className={`today-market-session phase-${resolvedSession.phase.toLowerCase()}`}>
        <div className="today-market-session-status">
          <span>미국 정규장</span>
          <strong>{phaseCopy.label}</strong>
          {sessionNote ? <b>{sessionNote}</b> : null}
        </div>
        <div className="today-market-session-clocks">
          <span>현재 시각</span>
          <strong>
            뉴욕 {formatZonedClock(nowMs, payload.market_session.timezones.market)}
            <i>·</i>
            한국 {formatZonedClock(nowMs, payload.market_session.timezones.viewer)}
          </strong>
        </div>
        <div className="today-market-session-hours">
          <span>{displaySession?.trade_date ?? "거래 일정"}</span>
          <strong>
            ET · {displaySession
              ? formatSessionHours(displaySession, payload.market_session.timezones.market)
              : "일정 자료 부족"}
          </strong>
          <small>
            KST · {displaySession
              ? formatSessionHours(displaySession, payload.market_session.timezones.viewer)
              : "일정 자료 부족"}
          </small>
        </div>
        <div className="today-market-session-countdown">
          <span>{phaseCopy.countdown}</span>
          <strong>{countdownText}</strong>
        </div>
      </section>

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

      <section className="today-portfolio-panel">
        <header className="today-portfolio-heading">
          <div>
            <span className="today-eyebrow">REPRESENTATIVE PORTFOLIO</span>
            <h2>{payload.portfolio.name}</h2>
            <p>{payload.portfolio.summary} · 기준 {payload.portfolio.basis_date ?? "-"}</p>
          </div>
          <b className={`today-portfolio-status status-${payload.portfolio.status.toLowerCase()}`}>{payload.portfolio.status === "READY" ? "정상 추적" : "확인 필요"}</b>
        </header>
        <div className="today-metrics" aria-live="polite">
          <article><span>현재 평가액</span><strong>{moneyText(display.currentValue)}</strong><small>{display.badge}{display.asOfUtc ? ` · ${formatZonedClock(Date.parse(display.asOfUtc), "America/New_York")} ET` : ` · ${payload.portfolio.basis_date ?? "-"}`}</small></article>
          <article><span>{display.latestReturnLabel}</span><strong className={recentTone}>{percentText(display.latestObservationReturn)}</strong><small>{shortDate(display.returnFromDate)} → {shortDate(display.returnToDate)}</small></article>
          <article><span>누적 수익률</span><strong className={totalTone}>{percentText(display.totalReturn)}</strong><small>{display.coverageText ?? "현금흐름 조정"}</small></article>
        </div>
        <TodayPortfolioChart
          rows={payload.portfolio.curve}
          metadata={payload.portfolio.curve_metadata}
          livePoint={display.livePoint}
          viewportWidth={width}
        />
        <div className="today-portfolio-detail-grid">
          <section className="today-contributor-section">
            <header className="today-detail-heading">
              <span>종목별 성과 기여</span>
              <small>기여 상위 2 · 하위 2</small>
            </header>
            <div className="today-contributor-grid">
              {display.contributors.length
                ? display.contributors.map((row) => {
                  const returnTone = row.total_return == null
                    ? "is-unavailable"
                    : row.total_return < 0 ? "is-negative" : "is-positive";
                  const contributionTone = row.tone === "negative"
                    ? "is-negative"
                    : "is-positive";
                  return (
                    <article
                      className="today-contributor-card"
                      key={`${row.symbol}-${row.contribution_value}`}
                    >
                      <strong className="today-contributor-symbol">{row.symbol}</strong>
                      <span className="today-contributor-return-label">종목 누적 수익률</span>
                      <b className={`today-contributor-return ${returnTone}`}>
                        {row.total_return == null
                          ? "수익률 자료 부족"
                          : percentText(row.total_return)}
                      </b>
                      <footer>
                        <span>포트폴리오 누적 기여</span>
                        <strong className={contributionTone}>
                          {signedMoneyText(row.contribution_value)}
                        </strong>
                      </footer>
                    </article>
                  );
                })
                : <small>기여 계산 자료가 없습니다.</small>}
            </div>
            <small className="today-contributor-note">
              종목 수익률은 입출금 영향을 조정한 누적 성과 · {display.badge}
            </small>
          </section>
          <section>
            <span>우선 확인</span>
            <div className="today-review-list">
              {payload.portfolio.review_items.length
                ? payload.portfolio.review_items.map((row) => <p key={`${row.severity}-${row.meaning}`}><b>{row.severity}</b>{row.meaning}</p>)
                : <small>현재 우선 확인 항목이 없습니다.</small>}
            </div>
          </section>
        </div>
      </section>

      <section className="today-action-section">
        <header className="today-section-heading"><div><span>NEXT ACTION</span><h2>다음 확인</h2></div></header>
        <div className="today-action-rail">
          <button type="button" onClick={() => emit("open_market_research")}>시장 근거 자세히 보기 <b>→</b></button>
          <button type="button" onClick={() => emit("open_stock_research")}>영향이 큰 종목 조사 <b>→</b></button>
          <button type="button" onClick={() => emit("open_portfolio_monitoring")}>포트폴리오 전체 점검 <b>→</b></button>
        </div>
      </section>
    </main>
  );
}

export default withStreamlitConnection(TodayWorkbench);
