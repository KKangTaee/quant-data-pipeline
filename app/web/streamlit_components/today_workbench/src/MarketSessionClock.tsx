import { useEffect, useRef, useState } from "react";

import {
  formatCountdown,
  formatSessionHours,
  formatZonedClock,
  resolveMarketSession,
} from "./presentation";
import type {
  MarketSessionPayload,
  MarketSessionPhase,
} from "./types";

type Props = {
  marketSession: MarketSessionPayload;
  onPhaseChange: (phase: MarketSessionPhase) => void;
};

export default function MarketSessionClock({ marketSession, onPhaseChange }: Props) {
  const [nowMs, setNowMs] = useState(() => Date.now());
  const phaseRef = useRef<MarketSessionPhase | null>(null);
  const resolvedSession = resolveMarketSession(marketSession, nowMs);

  useEffect(() => {
    const timer = window.setInterval(() => setNowMs(Date.now()), 1000);
    return () => window.clearInterval(timer);
  }, []);

  useEffect(() => {
    if (phaseRef.current == null) {
      phaseRef.current = resolvedSession.phase;
      return;
    }
    if (phaseRef.current !== resolvedSession.phase) {
      phaseRef.current = resolvedSession.phase;
      onPhaseChange(resolvedSession.phase);
    }
  }, [onPhaseChange, resolvedSession.phase]);

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
        : marketSession.calendar_quality === "LIMITED"
          ? "일정 확인 필요"
          : null;
  const countdownText = resolvedSession.targetAtMs == null
    ? "새로고침 필요"
    : formatCountdown(resolvedSession.targetAtMs - nowMs);

  return (
    <section className={`today-market-session phase-${resolvedSession.phase.toLowerCase()}`}>
      <div className="today-market-session-status">
        <span>미국 정규장</span>
        <strong>{phaseCopy.label}</strong>
        {sessionNote ? <b>{sessionNote}</b> : null}
      </div>
      <div className="today-market-session-clocks">
        <span>현재 시각</span>
        <strong>
          뉴욕 {formatZonedClock(nowMs, marketSession.timezones.market)}
          <i>·</i>
          한국 {formatZonedClock(nowMs, marketSession.timezones.viewer)}
        </strong>
      </div>
      <div className="today-market-session-hours">
        <span>{displaySession?.trade_date ?? "거래 일정"}</span>
        <strong>
          ET · {displaySession
            ? formatSessionHours(displaySession, marketSession.timezones.market)
            : "일정 자료 부족"}
        </strong>
        <small>
          KST · {displaySession
            ? formatSessionHours(displaySession, marketSession.timezones.viewer)
            : "일정 자료 부족"}
        </small>
      </div>
      <div className="today-market-session-countdown">
        <span>{phaseCopy.countdown}</span>
        <strong>{countdownText}</strong>
      </div>
    </section>
  );
}
