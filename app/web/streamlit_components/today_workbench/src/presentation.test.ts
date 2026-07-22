import { describe, expect, it } from "vitest";

import {
  buildChartSeries,
  buildDateTicks,
  buildPercentTicks,
  chartDomains,
  displayPortfolio,
  formatCountdown,
  formatSessionHours,
  formatZonedClock,
  pointCoordinates,
  resolveMarketSession,
} from "./presentation";
import * as presentation from "./presentation";
import type { TodayPortfolio } from "./types";

const eodPortfolio: TodayPortfolio = {
  status: "READY",
  name: "Core",
  basis_date: "2026-07-21",
  summary: "저장 종가",
  metrics: {
    current_value: 1500,
    latest_observation_return: 0.02,
    return_from_date: "2026-07-18",
    return_to_date: "2026-07-21",
    total_return: 0.10,
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
  active_item_count: 2,
  live: {
    status: "INACTIVE",
    label: "확정 종가",
    as_of_utc: null,
    trade_date: null,
    coverage: { fresh: 0, expected: 0, fallback_symbols: [] },
    metrics: null,
    contributors: [],
    curve_point: null,
    message: "저장된 확정 종가 기준입니다.",
  },
};

describe("Today live portfolio presentation", () => {
  it("uses live values only when a live point exists", () => {
    const result = displayPortfolio({
      ...eodPortfolio,
      live: {
        ...eodPortfolio.live,
        status: "LIVE_READY",
        label: "장중 임시",
        as_of_utc: "2026-07-22T14:00:00Z",
        trade_date: "2026-07-22",
        coverage: { fresh: 2, expected: 2, fallback_symbols: [] },
        metrics: {
          current_value: 1575,
          latest_observation_return: 0.05,
          return_from_date: "2026-07-21",
          return_to_date: "2026-07-22",
          total_return: 0.155,
        },
        curve_point: {
          date: "2026-07-22T14:00:00Z",
          timestamp_utc: "2026-07-22T14:00:00Z",
          kind: "intraday",
          unit_value: 1.155,
          total_value: 1575,
          cumulative_return: 0.155,
        },
      },
    });

    expect(result.currentValue).toBe(1575);
    expect(result.latestReturnLabel).toBe("오늘 장중 수익률");
    expect(result.badge).toBe("장중 임시");
  });

  it("keeps EOD values when all quotes fail", () => {
    const result = displayPortfolio({
      ...eodPortfolio,
      live: { ...eodPortfolio.live, status: "LIVE_PARTIAL" },
    });

    expect(result.currentValue).toBe(1500);
    expect(result.livePoint).toBeNull();
  });

  it("shows coverage for partial quotes", () => {
    const result = displayPortfolio({
      ...eodPortfolio,
      live: {
        ...eodPortfolio.live,
        status: "LIVE_PARTIAL",
        coverage: { fresh: 1, expected: 2, fallback_symbols: ["QQQ"] },
      },
    });

    expect(result.coverageText).toBe("직접 종목 1/2개 장중 반영");
  });
});

describe("Today contributor currency presentation", () => {
  it("keeps explicit positive and negative contribution signs", () => {
    const signedMoneyText = Reflect.get(presentation, "signedMoneyText") as
      | ((value: number | null) => string)
      | undefined;

    expect(signedMoneyText?.(11915)).toBe("+$11,915");
    expect(signedMoneyText?.(-401)).toBe("-$401");
  });
});

describe("Today portfolio chart presentation", () => {
  it("uses elapsed calendar time for x coordinates", () => {
    const series = buildChartSeries([
      { date: "2026-07-18", unit_value: 1, total_value: 10000, cumulative_return: 0 },
      { date: "2026-07-21", unit_value: 1.06, total_value: 10600, cumulative_return: 0.06 },
      { date: "2026-07-22", unit_value: 1.07, total_value: 10700, cumulative_return: 0.07 },
    ]);
    const domain = chartDomains(series);
    const box = { width: 400, height: 200, left: 50, right: 20, top: 20, bottom: 30 };
    const saturday = pointCoordinates(series[0], domain, box);
    const monday = pointCoordinates(series[1], domain, box);
    const tuesday = pointCoordinates(series[2], domain, box);
    expect(monday.x - saturday.x).toBeCloseTo(3 * (tuesday.x - monday.x));
  });

  it("keeps responsive date ticks within the requested count", () => {
    const series = buildChartSeries(Array.from({ length: 9 }, (_, index) => ({
      date: `2026-07-${String(index + 10).padStart(2, "0")}`,
      unit_value: 1 + index / 100,
      total_value: 10000 + index * 100,
      cumulative_return: index / 100,
    })));
    expect(buildDateTicks(series, 5)).toHaveLength(5);
    expect(buildDateTicks(series, 3)).toHaveLength(3);
    expect(buildDateTicks(series, 3)[0].date).toBe(series[0].date);
    const mobileTicks = buildDateTicks(series, 3);
    expect(mobileTicks[mobileTicks.length - 1]?.date).toBe(series[series.length - 1]?.date);
  });

  it("includes zero in the percent domain and keeps a missing tooltip value", () => {
    const series = buildChartSeries([
      { date: "2026-07-18", unit_value: 0.98, total_value: null, cumulative_return: -0.02 },
      { date: "2026-07-21", unit_value: 1.03, total_value: 10300, cumulative_return: 0.03 },
    ]);
    const domain = chartDomains(series);
    expect(domain.low).toBeLessThanOrEqual(0);
    expect(domain.high).toBeGreaterThanOrEqual(0);
    expect(buildPercentTicks(domain, 5).some((value) => Math.abs(value) < 1e-12)).toBe(true);
    expect(series[0].total_value).toBeNull();
  });

  it("does not invent a negative axis range for an all-positive series", () => {
    const positive = buildChartSeries([
      { date: "2026-07-18", unit_value: 1.8, total_value: 18000, cumulative_return: 0.8 },
      { date: "2026-07-21", unit_value: 2.6, total_value: 26000, cumulative_return: 1.6 },
    ]);
    const negative = buildChartSeries([
      { date: "2026-07-18", unit_value: 0.9, total_value: 9000, cumulative_return: -0.1 },
      { date: "2026-07-21", unit_value: 0.7, total_value: 7000, cumulative_return: -0.3 },
    ]);

    expect(chartDomains(positive).low).toBe(0);
    expect(chartDomains(negative).high).toBe(0);
  });

  it("drops invalid dates and sorts the remaining observations", () => {
    const series = buildChartSeries([
      { date: "not-a-date", unit_value: 1, total_value: 100, cumulative_return: 0 },
      { date: "2026-07-21", unit_value: 1.03, total_value: 103, cumulative_return: 0.03 },
      { date: "2026-07-18", unit_value: 1, total_value: 100, cumulative_return: 0 },
    ]);
    expect(series.map((row) => row.date)).toEqual(["2026-07-18", "2026-07-21"]);
  });
});

const sessionPayload = {
  schema_version: "market_session_v1" as const,
  generated_at_utc: "2026-11-27T12:00:00+00:00",
  timezones: {
    market: "America/New_York" as const,
    viewer: "Asia/Seoul" as const,
  },
  calendar_quality: "CONFIRMED" as const,
  warnings: [],
  schedule: [
    {
      trade_date: "2026-11-27",
      day_kind: "TRADING_DAY" as const,
      holiday_label: null,
      open_at_utc: "2026-11-27T14:30:00+00:00",
      close_at_utc: "2026-11-27T18:00:00+00:00",
      is_early_close: true,
    },
    {
      trade_date: "2026-11-28",
      day_kind: "WEEKEND" as const,
      holiday_label: "주말",
      open_at_utc: null,
      close_at_utc: null,
      is_early_close: false,
    },
    {
      trade_date: "2026-11-29",
      day_kind: "WEEKEND" as const,
      holiday_label: "주말",
      open_at_utc: null,
      close_at_utc: null,
      is_early_close: false,
    },
    {
      trade_date: "2026-11-30",
      day_kind: "TRADING_DAY" as const,
      holiday_label: null,
      open_at_utc: "2026-11-30T14:30:00+00:00",
      close_at_utc: "2026-11-30T21:00:00+00:00",
      is_early_close: false,
    },
  ],
};

describe("Today U.S. regular-market phase", () => {
  it("switches exactly at open and early close boundaries", () => {
    expect(
      resolveMarketSession(
        sessionPayload,
        Date.parse("2026-11-27T14:29:59Z"),
      ).phase,
    ).toBe("PRE_OPEN");
    expect(
      resolveMarketSession(
        sessionPayload,
        Date.parse("2026-11-27T14:30:00Z"),
      ).phase,
    ).toBe("OPEN");
    expect(
      resolveMarketSession(
        sessionPayload,
        Date.parse("2026-11-27T18:00:00Z"),
      ).phase,
    ).toBe("CLOSED");
  });

  it("keeps weekend closed and targets the next trading-day open", () => {
    const resolved = resolveMarketSession(
      sessionPayload,
      Date.parse("2026-11-28T12:00:00Z"),
    );
    expect(resolved.phase).toBe("WEEKEND");
    expect(resolved.targetAtMs).toBe(Date.parse("2026-11-30T14:30:00Z"));
  });

  it("fails closed when the official calendar schedule is limited", () => {
    const resolved = resolveMarketSession(
      {
        ...sessionPayload,
        calendar_quality: "LIMITED",
        warnings: ["공식 조기폐장 일정 자료 부족"],
      },
      Date.parse("2026-11-27T15:00:00Z"),
    );

    expect(resolved).toEqual({
      phase: "STALE",
      today: null,
      targetAtMs: null,
      nextTradingDay: null,
    });
  });
});

describe("Today U.S. regular-market time copy", () => {
  it("formats clocks, countdown, and KST date crossing", () => {
    expect(
      formatCountdown(5 * 60 * 60 * 1000 + 18 * 60 * 1000 + 9 * 1000),
    ).toBe("5시간 18분 09초");
    expect(formatCountdown(-1)).toBe("전환 중");
    expect(
      formatZonedClock(
        Date.parse("2026-07-22T13:00:00Z"),
        "America/New_York",
      ),
    ).toBe("09:00");
    expect(
      formatZonedClock(
        Date.parse("2026-07-22T13:00:00Z"),
        "Asia/Seoul",
      ),
    ).toBe("22:00");
    expect(
      formatSessionHours(
        {
          trade_date: "2026-07-22",
          day_kind: "TRADING_DAY",
          holiday_label: null,
          open_at_utc: "2026-07-22T13:30:00Z",
          close_at_utc: "2026-07-22T20:00:00Z",
          is_early_close: false,
        },
        "Asia/Seoul",
      ),
    ).toBe("07.22 22:30–07.23 05:00");
  });
});
