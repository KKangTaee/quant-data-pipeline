import assert from "node:assert/strict";
import test from "node:test";

import { buildStockResearchHandoffEvent } from "./marketResearchHandoff.ts";

test("normalizes the selected symbol into the allow-listed handoff event", () => {
  assert.deepEqual(buildStockResearchHandoffEvent(" amd "), {
    id: "open_us_stock_research",
    symbol: "AMD",
  });
});
