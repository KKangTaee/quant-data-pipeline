import type { PortfolioCurveRow } from "./types";

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
  const rawLow = Math.min(0, ...returns);
  const rawHigh = Math.max(0, ...returns);
  const padding = Math.max((rawHigh - rawLow) * 0.12, 0.005);
  const minTime = series[0].timestamp;
  const maxTime = series[series.length - 1].timestamp;
  return {
    minTime,
    maxTime: maxTime === minTime ? minTime + DAY_MS : maxTime,
    low: rawLow - padding,
    high: rawHigh + padding,
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
