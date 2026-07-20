import assert from "node:assert/strict";
import test from "node:test";

import { buildPriceMomentumRange, priceMomentumRangeLabel } from "./priceMomentum.ts";

const series = [
  { date: "2025-07-20", price: 70, normalized_return_pct: -30 },
  { date: "2025-07-21", price: 80, normalized_return_pct: -20 },
  { date: "2026-01-21", price: 100, normalized_return_pct: 0 },
  { date: "2026-04-21", price: 90, normalized_return_pct: -10 },
  { date: "2026-06-21", price: 100, normalized_return_pct: 0 },
  { date: "2026-07-07", price: 110, normalized_return_pct: 10 },
  { date: "2026-07-21", price: 120, normalized_return_pct: 20 },
];

test("rebases each selected range to its first visible adjusted close", () => {
  const oneMonth = buildPriceMomentumRange(series, "1M");
  const threeMonths = buildPriceMomentumRange(series, "3M");
  const sixMonths = buildPriceMomentumRange(series, "6M");
  const oneYear = buildPriceMomentumRange(series, "1Y");

  assert.deepEqual(oneMonth.map((point) => point.returnPct), [0, 10, 20]);
  assert.deepEqual(threeMonths.map((point) => Number(point.returnPct.toFixed(2))), [0, 11.11, 22.22, 33.33]);
  assert.deepEqual(sixMonths.map((point) => point.returnPct), [0, -10, 0, 10, 20]);
  assert.deepEqual(oneYear.map((point) => point.returnPct), [0, 25, 12.5, 25, 37.5, 50]);
});

test("uses a rolling twelve-month window and exposes a dynamic readout label", () => {
  const oneYear = buildPriceMomentumRange(series, "1Y");

  assert.equal(oneYear[0].date, "2025-07-21");
  assert.equal(oneYear.at(-1)?.date, "2026-07-21");
  assert.equal(priceMomentumRangeLabel("1M"), "1M 수익률");
  assert.equal(priceMomentumRangeLabel("1Y"), "1Y 수익률");
});

test("clamps calendar-month cutoffs at month end", () => {
  const monthEndSeries = [
    { date: "2026-02-28", price: 100 },
    { date: "2026-03-03", price: 105 },
    { date: "2026-03-31", price: 110 },
  ];

  const oneMonth = buildPriceMomentumRange(monthEndSeries, "1M");

  assert.equal(oneMonth[0].date, "2026-02-28");
  assert.deepEqual(oneMonth.map((point) => point.returnPct), [0, 5, 10]);
});
