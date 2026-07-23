import type {
  MarketSessionDay,
  MarketSessionPayload,
  MarketSessionPhase,
  PortfolioCurveRow,
  TodayPortfolio,
} from "./types";

export function marketPhaseTransition(
  previous: MarketSessionPhase | null,
  current: MarketSessionPhase,
): { id: "market_phase_changed"; phase: MarketSessionPhase } | null {
  if (previous == null || previous === current) return null;
  return { id: "market_phase_changed", phase: current };
}

export function displayPortfolio(portfolio: TodayPortfolio) {
  const live = portfolio.live;
  const usesLive = live.curve_point != null && live.metrics != null
    && (live.status === "LIVE_READY" || live.status === "LIVE_PARTIAL");
  const metrics = usesLive ? live.metrics! : portfolio.metrics;
  const coverageText = live.status === "LIVE_PARTIAL" && live.coverage.expected > 0
    ? `직접 종목 ${live.coverage.fresh}/${live.coverage.expected}개 장중 반영`
    : null;
  return {
    currentValue: metrics.current_value,
    latestObservationReturn: metrics.latest_observation_return,
    totalReturn: metrics.total_return,
    returnFromDate: metrics.return_from_date,
    returnToDate: metrics.return_to_date,
    contributors: usesLive ? live.contributors : portfolio.contributors,
    livePoint: usesLive ? live.curve_point : null,
    latestReturnLabel: usesLive ? "오늘 장중 수익률" : "최근 거래일 수익률",
    badge: usesLive ? "장중 임시" : live.status === "EOD_WAITING" ? "종가 반영 대기" : "확정 종가",
    coverageText,
    asOfUtc: usesLive ? live.as_of_utc : null,
  };
}

export type ChartPoint = PortfolioCurveRow & { timestamp: number };
export type ChartDomain = { minTime: number; maxTime: number; low: number; high: number };
export type ChartInsets = {
  width: number;
  height: number;
  left: number;
  right: number;
  top: number;
  bottom: number;
};

const DAY_MS = 86_400_000;

function zonedParts(nowMs: number, timeZone: string) {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone,
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
    hour: "2-digit",
    minute: "2-digit",
    hourCycle: "h23",
  }).formatToParts(new Date(nowMs));
  return Object.fromEntries(parts.map((part) => [part.type, part.value]));
}

function marketDateKey(nowMs: number): string {
  const parts = zonedParts(nowMs, "America/New_York");
  return `${parts.year}-${parts.month}-${parts.day}`;
}

function nextOpen(schedule: MarketSessionDay[], afterMs: number) {
  return schedule.find((row) => (
    row.open_at_utc != null
    && Date.parse(row.open_at_utc) > afterMs
  )) ?? null;
}

export function resolveMarketSession(
  payload: MarketSessionPayload,
  nowMs: number,
): {
  phase: MarketSessionPhase;
  today: MarketSessionDay | null;
  targetAtMs: number | null;
  nextTradingDay: MarketSessionDay | null;
} {
  if (payload.calendar_quality !== "CONFIRMED") {
    return {
      phase: "STALE",
      today: null,
      targetAtMs: null,
      nextTradingDay: null,
    };
  }
  const today = payload.schedule.find(
    (row) => row.trade_date === marketDateKey(nowMs),
  ) ?? null;
  if (today == null) {
    return {
      phase: "STALE",
      today: null,
      targetAtMs: null,
      nextTradingDay: null,
    };
  }
  const upcoming = nextOpen(payload.schedule, nowMs);
  if (today.day_kind !== "TRADING_DAY") {
    return {
      phase: today.day_kind,
      today,
      targetAtMs: upcoming?.open_at_utc
        ? Date.parse(upcoming.open_at_utc)
        : null,
      nextTradingDay: upcoming,
    };
  }
  const openMs = Date.parse(today.open_at_utc ?? "");
  const closeMs = Date.parse(today.close_at_utc ?? "");
  if (!Number.isFinite(openMs) || !Number.isFinite(closeMs)) {
    return {
      phase: "STALE",
      today,
      targetAtMs: null,
      nextTradingDay: upcoming,
    };
  }
  if (nowMs < openMs) {
    return {
      phase: "PRE_OPEN",
      today,
      targetAtMs: openMs,
      nextTradingDay: today,
    };
  }
  if (nowMs < closeMs) {
    return {
      phase: "OPEN",
      today,
      targetAtMs: closeMs,
      nextTradingDay: today,
    };
  }
  return {
    phase: "CLOSED",
    today,
    targetAtMs: upcoming?.open_at_utc
      ? Date.parse(upcoming.open_at_utc)
      : null,
    nextTradingDay: upcoming,
  };
}

export function formatCountdown(remainingMs: number): string {
  if (!Number.isFinite(remainingMs) || remainingMs <= 0) return "전환 중";
  const totalSeconds = Math.floor(remainingMs / 1000);
  const hours = Math.floor(totalSeconds / 3600);
  const minutes = Math.floor((totalSeconds % 3600) / 60);
  const seconds = totalSeconds % 60;
  const minuteSecond = `${minutes}분 ${String(seconds).padStart(2, "0")}초`;
  return hours > 0 ? `${hours}시간 ${minuteSecond}` : minuteSecond;
}

export function formatZonedClock(nowMs: number, timeZone: string): string {
  const parts = zonedParts(nowMs, timeZone);
  return `${parts.hour}:${parts.minute}`;
}

export function formatSessionHours(
  row: MarketSessionDay,
  timeZone: string,
): string {
  if (row.open_at_utc == null || row.close_at_utc == null) {
    return "일정 자료 부족";
  }
  const open = zonedParts(Date.parse(row.open_at_utc), timeZone);
  const close = zonedParts(Date.parse(row.close_at_utc), timeZone);
  return (
    `${open.month}.${open.day} ${open.hour}:${open.minute}`
    + `–${close.month}.${close.day} ${close.hour}:${close.minute}`
  );
}

export function signedMoneyText(value: number | null): string {
  if (value == null || !Number.isFinite(value)) return "—";
  const magnitude = new Intl.NumberFormat("en-US", {
    style: "currency",
    currency: "USD",
    maximumFractionDigits: 0,
  }).format(Math.abs(value));
  const sign = value > 0 ? "+" : value < 0 ? "-" : "";
  return `${sign}${magnitude}`;
}

function dateTimestamp(value: string): number {
  return Date.parse(`${value}T00:00:00Z`);
}

export function buildChartSeries(rows: PortfolioCurveRow[]): ChartPoint[] {
  return rows
    .map((row) => ({ ...row, timestamp: dateTimestamp(row.date) }))
    .filter((row) => (
      Number.isFinite(row.timestamp)
      && Number.isFinite(row.unit_value)
      && Number.isFinite(row.cumulative_return)
      && (row.total_value == null || Number.isFinite(row.total_value))
    ))
    .sort((left, right) => left.timestamp - right.timestamp);
}

export function buildDateTicks(series: ChartPoint[], maxTicks: number): ChartPoint[] {
  if (!series.length || maxTicks < 1) return [];
  const count = Math.min(Math.max(Math.floor(maxTicks), 1), series.length);
  if (count === 1) return [series[0]];
  const first = series[0];
  const last = series[series.length - 1];
  const selected = Array.from({ length: count }, (_, index) => {
    const target = first.timestamp + ((last.timestamp - first.timestamp) * index) / (count - 1);
    return series.reduce((nearest, row) => (
      Math.abs(row.timestamp - target) < Math.abs(nearest.timestamp - target)
        ? row
        : nearest
    ), first);
  });
  const unique = Array.from(new Map(selected.map((row) => [row.date, row])).values());
  if (unique.length === count) return unique;
  for (const row of series) {
    if (!unique.some((item) => item.date === row.date)) unique.push(row);
    if (unique.length === count) break;
  }
  return unique.sort((left, right) => left.timestamp - right.timestamp);
}

export function buildPercentTicks(domain: ChartDomain, maxTicks = 5): number[] {
  const count = Math.max(Math.floor(maxTicks), 2);
  const span = Math.max(domain.high - domain.low, 1e-9);
  const ticks = Array.from(
    { length: count },
    (_, index) => domain.low + (span * index) / (count - 1),
  );
  if (domain.low <= 0 && domain.high >= 0 && !ticks.some((value) => Math.abs(value) < 1e-12)) {
    const replaceIndex = ticks
      .map((value, index) => ({ distance: Math.abs(value), index }))
      .filter((item) => item.index > 0 && item.index < ticks.length - 1)
      .sort((left, right) => left.distance - right.distance)[0]?.index;
    if (replaceIndex != null) ticks[replaceIndex] = 0;
  }
  return ticks.sort((left, right) => left - right);
}

export function chartDomains(series: ChartPoint[]): ChartDomain {
  if (!series.length) {
    return { minTime: 0, maxTime: DAY_MS, low: -0.01, high: 0.01 };
  }
  const returns = series.map((row) => row.cumulative_return);
  const dataLow = Math.min(...returns);
  const dataHigh = Math.max(...returns);
  const rawLow = Math.min(0, dataLow);
  const rawHigh = Math.max(0, dataHigh);
  const padding = Math.max((rawHigh - rawLow) * 0.12, 0.005);
  const flatAtZero = dataLow === 0 && dataHigh === 0;
  const minTime = series[0].timestamp;
  const maxTime = series[series.length - 1].timestamp;
  return {
    minTime,
    maxTime: maxTime === minTime ? minTime + DAY_MS : maxTime,
    low: flatAtZero ? -padding : dataLow >= 0 ? 0 : rawLow - padding,
    high: flatAtZero ? padding : dataHigh <= 0 ? 0 : rawHigh + padding,
  };
}

export function pointCoordinates(
  point: ChartPoint,
  domain: ChartDomain,
  box: ChartInsets,
): { x: number; y: number } {
  const plotWidth = Math.max(box.width - box.left - box.right, 1);
  const plotHeight = Math.max(box.height - box.top - box.bottom, 1);
  const timeSpan = Math.max(domain.maxTime - domain.minTime, 1);
  const valueSpan = Math.max(domain.high - domain.low, 1e-9);
  return {
    x: box.left + ((point.timestamp - domain.minTime) / timeSpan) * plotWidth,
    y: box.top + ((domain.high - point.cumulative_return) / valueSpan) * plotHeight,
  };
}
