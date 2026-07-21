export type PriceMomentumRange = "1M" | "3M" | "6M" | "1Y";

export type PriceMomentumInput = {
  date?: unknown;
  price?: unknown;
};

export type PriceMomentumPoint = {
  date: string;
  price: number;
  returnPct: number;
};

function dateTimestamp(value: unknown) {
  const label = String(value || "");
  const timestamp = new Date(`${label}T00:00:00`).getTime();
  return Number.isNaN(timestamp) ? null : timestamp;
}

function subtractCalendarMonths(value: Date, months: number) {
  const cutoff = new Date(value);
  const originalDay = cutoff.getDate();
  cutoff.setDate(1);
  cutoff.setMonth(cutoff.getMonth() - months);
  const lastDayOfTargetMonth = new Date(
    cutoff.getFullYear(),
    cutoff.getMonth() + 1,
    0,
  ).getDate();
  cutoff.setDate(Math.min(originalDay, lastDayOfTargetMonth));
  return cutoff;
}

/** Rebase stored adjusted closes to the first valid trading day in the selected range. */
export function buildPriceMomentumRange(
  series: PriceMomentumInput[],
  range: PriceMomentumRange,
): PriceMomentumPoint[] {
  const valid = series
    .map((row) => ({
      date: String(row.date || ""),
      price: Number(row.price),
      timestamp: dateTimestamp(row.date),
    }))
    .filter((row) => row.timestamp !== null && Number.isFinite(row.price) && row.price > 0)
    .sort((left, right) => Number(left.timestamp) - Number(right.timestamp));
  if (!valid.length) return [];

  const latestDate = new Date(Number(valid[valid.length - 1].timestamp));
  const cutoff = subtractCalendarMonths(
    latestDate,
    range === "1Y" ? 12 : ({ "1M": 1, "3M": 3, "6M": 6 }[range]),
  );

  const selected = valid.filter((row) => Number(row.timestamp) >= cutoff.getTime());
  if (!selected.length) return [];
  const basePrice = selected[0].price;
  return selected.map((row) => ({
    date: row.date,
    price: row.price,
    returnPct: Number(((((row.price / basePrice) - 1) * 100)).toFixed(6)),
  }));
}

export function priceMomentumRangeLabel(range: PriceMomentumRange) {
  return `${range} 수익률`;
}
