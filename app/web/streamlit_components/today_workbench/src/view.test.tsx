import { renderToStaticMarkup } from "react-dom/server";
import { describe, expect, it } from "vitest";

import { TodayActionsView, TodayContextView } from "./TodayWorkbench";
import TodayPortfolioPanel from "./TodayPortfolioPanel";
import type { TodayPayload } from "./types";

const payload: TodayPayload = {
  schema_version: "today_home_v4",
  header: {
    as_of_date: "2026-07-22",
    source_count: 5,
    source_ready_count: 5,
    source_available_count: 5,
    status: "READY",
    status_label: "주요 자료 확인",
  },
  market: {
    status: "READY",
    tone: "neutral",
    headline: "저장 근거 확인",
    summary: "저장 자료입니다.",
    evidence: [],
    next_event: null,
    watch_items: [],
  },
  market_session: {
    schema_version: "market_session_v1",
    generated_at_utc: "2026-07-22T14:00:00Z",
    timezones: {
      market: "America/New_York",
      viewer: "Asia/Seoul",
    },
    calendar_quality: "CONFIRMED",
    warnings: [],
    schedule: [
      {
        trade_date: "2026-07-22",
        day_kind: "TRADING_DAY",
        holiday_label: null,
        open_at_utc: "2026-07-22T13:30:00Z",
        close_at_utc: "2026-07-22T20:00:00Z",
        is_early_close: false,
      },
    ],
  },
  portfolio: {
    status: "READY",
    name: "대표 포트폴리오",
    basis_date: "2026-07-22",
    summary: "저장 종가 기준",
    metrics: {
      current_value: 10000,
      latest_observation_return: 0.01,
      return_from_date: "2026-07-21",
      return_to_date: "2026-07-22",
      total_return: 0.05,
    },
    curve: [],
    curve_metadata: {
      interval: "daily",
      price_basis: "stored_close",
      aggregation: "none",
      intraday: false,
      observation_count: 0,
      start_date: null,
      end_date: null,
    },
    contributors: [],
    review_items: [],
    active_item_count: 1,
    live: {
      status: "INACTIVE",
      label: "확정 종가",
      as_of_utc: null,
      trade_date: null,
      coverage: { fresh: 0, expected: 0, fallback_symbols: [] },
      metrics: null,
      contributors: [],
      curve_point: null,
      message: "확정 종가 기준",
    },
  },
};

describe("Today split views", () => {
  it("keeps portfolio markup out of the context view", () => {
    const markup = renderToStaticMarkup(
      <TodayContextView
        payload={payload}
        onPhaseChange={() => undefined}
      />,
    );

    expect(markup).toContain("오늘의 시장 판단");
    expect(markup).not.toContain("REPRESENTATIVE PORTFOLIO");
  });

  it("keeps market and actions out of the portfolio view", () => {
    const markup = renderToStaticMarkup(
      <TodayPortfolioPanel
        portfolio={payload.portfolio}
        viewportWidth={960}
      />,
    );

    expect(markup).toContain("REPRESENTATIVE PORTFOLIO");
    expect(markup).not.toContain("오늘의 시장 판단");
    expect(markup).not.toContain("NEXT ACTION");
  });

  it("keeps navigation buttons in the actions view", () => {
    const markup = renderToStaticMarkup(
      <TodayActionsView onEvent={() => undefined} />,
    );

    expect(markup).toContain("시장 근거 자세히 보기");
    expect(markup).not.toContain("REPRESENTATIVE PORTFOLIO");
  });
});
