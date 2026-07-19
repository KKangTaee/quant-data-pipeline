import { describe, expect, it } from "vitest";
import type { GroupSummary, GroupValueResult } from "./contracts";
import {
  buildCommonBasisBanner,
  buildGroupChartSeries,
  formatMetric,
  selectActiveGroup,
  selectItem,
} from "./workbenchState";

const groups: GroupSummary[] = [
  {
    portfolio_group_id: "default",
    name: "기본 포트폴리오",
    is_default: true,
    selected: false,
    status: "active",
    version: 1,
    active_item_count: 1,
    history_item_count: 2,
  },
  {
    portfolio_group_id: "growth",
    name: "성장 전략",
    is_default: false,
    selected: true,
    status: "active",
    version: 2,
    active_item_count: 2,
    history_item_count: 2,
  },
];

const activeGroup = {
  status: "READY",
  basis_date: "2026-07-18",
  curve: [
    { date: "2026-07-01", total_value: 20000, "item:a": 10000, "item:b": null },
    { date: "2026-07-18", total_value: 21000, "item:a": 10500, "item:b": 10500 },
  ],
  metrics: {
    invested_capital: 20000,
    current_value: 21000,
    pnl: 1000,
    total_return: 0.05,
    mdd: -0.03,
    cagr: 1.91,
    observation_days: 17,
    short_window: true,
    total_contribution: 1000,
    downside_contribution: 0,
    contribution_by_item: { a: 500, b: 500 },
  },
  failures: {},
  item_rows: [
    { monitoring_item_id: "a", source_ref: "AAPL", status: "active", lane_status: "active", initial_capital: 10000, current_value: 10500, failure: null },
    { monitoring_item_id: "ended", source_ref: "OLD", status: "ended", lane_status: "ended", initial_capital: 10000, current_value: 9800, failure: null },
  ],
  active_item_count: 1,
  history_item_count: 2,
} satisfies GroupValueResult;

describe("portfolio monitoring workbench state", () => {
  it("resolves an explicit group, then server-selected group, then default", () => {
    expect(selectActiveGroup(groups, "default")?.portfolio_group_id).toBe("default");
    expect(selectActiveGroup(groups, "missing")?.portfolio_group_id).toBe("growth");
    expect(selectActiveGroup(groups.map((group) => ({ ...group, selected: false })), null)?.portfolio_group_id).toBe("default");
  });

  it("retains an ended item and resolves an explicit selection", () => {
    expect(selectItem(activeGroup.item_rows, "ended")?.source_ref).toBe("OLD");
    expect(selectItem(activeGroup.item_rows, null)?.source_ref).toBe("AAPL");
    expect(activeGroup.item_rows.map((item) => item.status)).toEqual(["active", "ended"]);
  });

  it("describes the common basis and partial state explicitly", () => {
    expect(buildCommonBasisBanner(activeGroup)).toContain("2026-07-18");
    expect(buildCommonBasisBanner({ ...activeGroup, status: "PARTIAL" })).toContain("일부 항목");
  });

  it("preserves chart gaps instead of converting missing item values to zero", () => {
    const series = buildGroupChartSeries(activeGroup.curve, ["a", "b"]);
    expect(series[0].items.b).toBeNull();
    expect(series[1].items.b).toBe(10500);
  });

  it("labels short-window CAGR in Korean", () => {
    expect(formatMetric(activeGroup.metrics.cagr, "cagr", activeGroup.metrics)).toBe("+191.00% · 17일 연환산");
    expect(formatMetric(activeGroup.metrics.current_value, "currency", activeGroup.metrics)).toBe("$21,000");
  });
});
