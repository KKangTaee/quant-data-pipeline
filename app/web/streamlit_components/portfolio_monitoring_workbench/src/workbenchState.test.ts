import { describe, expect, it } from "vitest";
import type { GroupSummary, GroupValueResult } from "./contracts";
import {
  buildCommonBasisBanner,
  buildChartDateTicks,
  buildGroupChartSeries,
  formatMetric,
  applySourceType,
  availableFundingModes,
  createItemDraft,
  drawerPresentation,
  validateItemDraft,
  selectActiveGroup,
  selectItem,
  buildDiagnosisSections,
  buildMacroObservationPresentation,
  buildFullMarketChartViewport,
  buildMarketChartBounds,
  buildRiskCalibrationPresentation,
  buildCatalogSearchEvent,
  itemBuilderRecoveryKey,
  nearestChartPointIndex,
  nearestMarketChartRowIndex,
  normalizeMarketChartViewport,
  normalizeItemBuilderState,
  panMarketChartViewport,
  partitionItemRows,
  placeChartTooltip,
  itemLifecycleLabel,
  zoomMarketChartViewport,
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

  it("separates active tracking from ended history and uses lifecycle labels", () => {
    const sections = partitionItemRows(activeGroup.item_rows);

    expect(sections.active.map((item) => item.source_ref)).toEqual(["AAPL"]);
    expect(sections.ended.map((item) => item.source_ref)).toEqual(["OLD"]);
    expect(itemLifecycleLabel(sections.active[0])).toBe("활성 추적");
    expect(itemLifecycleLabel(sections.ended[0])).toBe("종료 기록");
    expect(itemLifecycleLabel({ ...sections.active[0], status: "data_review" })).toBe("확인 필요");
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

  it("builds unique date ticks from actual observations and preserves both ends", () => {
    const series = buildGroupChartSeries(
      Array.from({ length: 9 }, (_, index) => ({
        date: `2026-07-${String(index + 1).padStart(2, "0")}`,
        total_value: 10000 + index,
      })),
      [],
    );

    expect(buildChartDateTicks(series, 5).map((tick) => tick.index)).toEqual([0, 2, 4, 6, 8]);
    expect(buildChartDateTicks(series, 3).map((tick) => tick.index)).toEqual([0, 4, 8]);
    expect(buildChartDateTicks(series.slice(0, 2), 5).map((tick) => tick.index)).toEqual([0, 1]);
  });

  it("selects the nearest valid chart observation across the plot", () => {
    const series = buildGroupChartSeries([
      { date: "2026-07-01", total_value: 10000 },
      { date: "2026-07-02", total_value: null },
      { date: "2026-07-03", total_value: 12000 },
    ], []);

    expect(nearestChartPointIndex(series, 66, 66, 938)).toBe(0);
    expect(nearestChartPointIndex(series, 502, 66, 938)).toBe(0);
    expect(nearestChartPointIndex(series, 880, 66, 938)).toBe(2);
  });

  it("keeps the chart tooltip inside the visible chart bounds", () => {
    expect(placeChartTooltip(900, 20, {
      chartWidth: 960,
      plotTop: 22,
      plotBottom: 244,
      tooltipWidth: 142,
      tooltipHeight: 48,
    })).toEqual({ x: 746, y: 22, side: "left" });

    expect(placeChartTooltip(120, 240, {
      chartWidth: 960,
      plotTop: 22,
      plotBottom: 244,
      tooltipWidth: 142,
      tooltipHeight: 48,
    })).toEqual({ x: 132, y: 196, side: "right" });
  });

  it("labels short-window CAGR in Korean", () => {
    expect(formatMetric(activeGroup.metrics.cagr, "cagr", activeGroup.metrics)).toBe("+191.00% · 17일 연환산");
    expect(formatMetric(activeGroup.metrics.current_value, "currency", activeGroup.metrics)).toBe("$21,000");
  });
});

describe("selected item market chart", () => {
  const rows = [
    { date: "2026-07-16", open: 10, high: 12, low: 9, close: 11, volume: 100 },
    { date: "2026-07-17", open: 11, high: 13, low: 10, close: 12, volume: 200 },
    { date: "2026-07-18", open: 12, high: 12.5, low: 10.5, close: 11, volume: null },
  ];

  it("uses the full candle range and ignores missing volume", () => {
    expect(buildMarketChartBounds(rows)).toEqual({ minPrice: 9, maxPrice: 13, maxVolume: 200 });
  });

  it("selects the nearest candle across bounded plot coordinates", () => {
    expect(nearestMarketChartRowIndex(rows.length, 0, 10, 110)).toBe(0);
    expect(nearestMarketChartRowIndex(rows.length, 60, 10, 110)).toBe(1);
    expect(nearestMarketChartRowIndex(rows.length, 200, 10, 110)).toBe(2);
    expect(nearestMarketChartRowIndex(0, 60, 10, 110)).toBeNull();
  });

  it("builds and normalizes an inclusive market chart viewport", () => {
    expect(buildFullMarketChartViewport(120)).toEqual({ startIndex: 0, endIndex: 119 });
    expect(normalizeMarketChartViewport({ startIndex: -20, endIndex: 200 }, 120)).toEqual({
      startIndex: 0,
      endIndex: 119,
    });
    expect(buildFullMarketChartViewport(0)).toEqual({ startIndex: 0, endIndex: 0 });
  });

  it("zooms around left center and right pointer anchors", () => {
    const full = buildFullMarketChartViewport(120);
    expect(zoomMarketChartViewport(full, 120, 0, "in")).toEqual({ startIndex: 0, endIndex: 95 });
    expect(zoomMarketChartViewport(full, 120, 0.5, "in")).toEqual({ startIndex: 12, endIndex: 107 });
    expect(zoomMarketChartViewport(full, 120, 1, "in")).toEqual({ startIndex: 24, endIndex: 119 });
  });

  it("clamps repeated zoom to 15 rows and back to the full range", () => {
    let viewport = buildFullMarketChartViewport(120);
    for (let index = 0; index < 20; index += 1) {
      viewport = zoomMarketChartViewport(viewport, 120, 0.5, "in");
    }
    expect(viewport.endIndex - viewport.startIndex + 1).toBe(15);
    for (let index = 0; index < 20; index += 1) {
      viewport = zoomMarketChartViewport(viewport, 120, 0.5, "out");
    }
    expect(viewport).toEqual({ startIndex: 0, endIndex: 119 });
  });

  it("pans by visible-row distance and clamps both data edges", () => {
    const viewport = { startIndex: 40, endIndex: 69 };
    expect(panMarketChartViewport(viewport, 120, 100, 300)).toEqual({ startIndex: 30, endIndex: 59 });
    expect(panMarketChartViewport(viewport, 120, -100, 300)).toEqual({ startIndex: 50, endIndex: 79 });
    expect(panMarketChartViewport(viewport, 120, 10000, 300)).toEqual({ startIndex: 0, endIndex: 29 });
    expect(panMarketChartViewport(viewport, 120, -10000, 300)).toEqual({ startIndex: 90, endIndex: 119 });
    expect(panMarketChartViewport(buildFullMarketChartViewport(120), 120, 100, 300)).toEqual({
      startIndex: 0,
      endIndex: 119,
    });
  });
});

describe("item drawer contract", () => {
  it("switches direct and selected-strategy drafts without leaking share mode", () => {
    const direct = createItemDraft("command-1");
    expect(availableFundingModes(direct.sourceType)).toEqual(["fixed_notional", "fixed_shares"]);

    const strategy = applySourceType({ ...direct, fundingMode: "fixed_shares", shares: "3" }, "selected_strategy");
    expect(strategy.fundingMode).toBe("fixed_notional");
    expect(strategy.shares).toBe("");
    expect(availableFundingModes(strategy.sourceType)).toEqual(["fixed_notional"]);
  });

  it("accepts integer shares only", () => {
    const base = {
      ...createItemDraft("command-2"),
      selectedSourceRef: "AAPL",
      selectedKind: "stock" as const,
      requestedStartDate: "2026-07-20",
      fundingMode: "fixed_shares" as const,
    };
    expect(validateItemDraft({ ...base, shares: "3.5" }, { activeItems: [], capacity: 10, selectedReadiness: "READY" })).toContain("정수");
    expect(validateItemDraft({ ...base, shares: "0" }, { activeItems: [], capacity: 10, selectedReadiness: "READY" })).toContain("1주");
    expect(validateItemDraft({ ...base, shares: "3" }, { activeItems: [], capacity: 10, selectedReadiness: "READY" })).toBeNull();
  });

  it("disables review for missing price, duplicate source, and 10-of-10 capacity", () => {
    const draft = {
      ...createItemDraft("command-3"),
      selectedSourceRef: "AAPL",
      selectedKind: "stock" as const,
      requestedStartDate: "2026-07-20",
      notional: "10000",
    };
    expect(validateItemDraft(draft, { activeItems: [], capacity: 10, selectedReadiness: "MISSING_PRICE" })).toContain("가격");
    expect(validateItemDraft(draft, { activeItems: [{ source_ref: "AAPL", status: "active" }], capacity: 10, selectedReadiness: "READY" })).toContain("이미");
    expect(validateItemDraft(draft, { activeItems: Array.from({ length: 10 }, (_, index) => ({ source_ref: `S${index}`, status: "active" })), capacity: 10, selectedReadiness: "READY" })).toContain("10개");
  });

  it("uses a full-width sheet on mobile and preserves the command id", () => {
    const draft = createItemDraft("stable-command");
    expect(drawerPresentation(420)).toBe("full_width_sheet");
    expect(drawerPresentation(760)).toBe("side_drawer");
    expect(applySourceType(draft, "direct_security").commandId).toBe("stable-command");
  });

  it("identifies the same server recovery snapshot only once", () => {
    const recovered = normalizeItemBuilderState({
      drawer_open: true,
      drawer_step: 1,
      catalog_query: "equal",
      draft: {
        command_id: "command-recovery",
        source_type: "selected_strategy",
        selected_source_ref: "",
        selected_label: "",
        selected_kind: "strategy",
        requested_start_date: "",
        funding_mode: "fixed_notional",
        notional: "10000",
        shares: "",
      },
    }, "fallback-command");

    expect(itemBuilderRecoveryKey(recovered)).toBe(itemBuilderRecoveryKey({
      ...recovered!,
      draft: { ...recovered!.draft },
    }));
    expect(itemBuilderRecoveryKey({ ...recovered!, catalogQuery: "risk parity" }))
      .not.toBe(itemBuilderRecoveryKey(recovered));
  });

  it("restores the selected target, requested date, and review step after a server search", () => {
    const restored = normalizeItemBuilderState({
      drawer_open: true,
      drawer_step: 3,
      catalog_query: "AAPL",
      draft: {
        command_id: "command-recovered",
        source_type: "direct_security",
        selected_source_ref: "AAPL",
        selected_label: "Apple Inc.",
        selected_kind: "stock",
        requested_start_date: "2026-07-01",
        funding_mode: "fixed_shares",
        notional: "10000",
        shares: "5",
      },
    }, "fallback-command");

    expect(restored?.drawerStep).toBe(3);
    expect(restored?.catalogQuery).toBe("AAPL");
    expect(restored?.draft.commandId).toBe("command-recovered");
    expect(restored?.draft.requestedStartDate).toBe("2026-07-01");
    expect(restored?.draft.shares).toBe("5");
  });

  it("includes the current wizard state in catalog search events", () => {
    const draft = {
      ...createItemDraft("command-search"),
      selectedSourceRef: "AAPL",
      selectedLabel: "Apple Inc.",
      selectedKind: "stock" as const,
      requestedStartDate: "2026-07-01",
    };

    expect(buildCatalogSearchEvent("apple", draft, 2)).toMatchObject({
      id: "search_catalog",
      query: "apple",
      source_type: "direct_security",
      item_builder_state: {
        drawer_open: true,
        drawer_step: 2,
        catalog_query: "apple",
        draft: {
          command_id: "command-search",
          selected_source_ref: "AAPL",
          requested_start_date: "2026-07-01",
        },
      },
    });
  });
});

describe("diagnosis evidence contract", () => {
  it("keeps at most three first-read rows and preserves full evidence", () => {
    const row = {
      rule_id: "trend_break_200d:a", policy_version: "portfolio_monitoring_policy_v1",
      classification: "weakness" as const, severity: "HIGH", persistence: 20,
      affected_weight: 0.4, contribution: -120, measured_fact: "200D 아래 20거래일",
      threshold: "high 20거래일", source_dates: ["2026-07-18"], coverage: 0.95,
      confidence: "HIGH", meaning: "장기 추세 약화", change_condition: "200D 위 회복",
      next_check: "다음 종가",
    };
    const sections = buildDiagnosisSections({
      policy_version: "portfolio_monitoring_policy_v1",
      top_three: [row, { ...row, rule_id: "two" }, { ...row, rule_id: "three" }, { ...row, rule_id: "four" }],
      strengths: [{ ...row, rule_id: "strength", classification: "strength" as const }],
      weaknesses: [row], data_gaps: [], all_rows: [row],
    });

    expect(sections.now).toHaveLength(3);
    expect(sections.evidence[0].measured_fact).toContain("20거래일");
    expect(sections.evidence[0].threshold).toContain("high");
    expect(sections.evidence[0].change_condition).toContain("회복");
    expect(JSON.stringify(sections)).not.toMatch(/매수|매도|목표\s*비중/);
  });
});

describe("macro observation evidence contract", () => {
  it("keeps meaning before source health and never creates probability copy", () => {
    const presentation = buildMacroObservationPresentation(
      {
        state: "high", rows: [{
          rule_id: "macro_tech_risk_off", root_id: "sector:Technology", state: "high", severity: "MEDIUM",
          affected_weight: 0.5, matched_conditions: ["risk_on"], current_observation: "Technology 50% / risk-on -40",
          source_dates: ["2026-07-18"], coverage: 0.75, confidence: "MEDIUM", publication: "PROVISIONAL",
          change_condition: "risk-on > -20", next_check: "다음 snapshot",
        }], top_rows: [], version: "portfolio_monitoring_macro_context_v1",
      },
      { status: "LIMITED", publication: "PROVISIONAL", coverage: 0.75, as_of_dates: { futures_macro: "2026-07-18" }, warnings: ["stale source"] },
    );

    expect(presentation.stateLabel).toBe("높음");
    expect(presentation.sourceChip).toContain("LIMITED");
    expect(presentation.rows[0].change_condition).toContain("-20");
    expect(presentation.staleWarning).toContain("stale");
    expect(JSON.stringify(presentation)).not.toMatch(/확률|probability|매수|매도/);
  });
});

describe("risk calibration disclosure contract", () => {
  it("shows observation-only fallback unless probability is qualified", () => {
    const fallback = buildRiskCalibrationPresentation({ publication_status: "SUPPRESSED", reasons: ["표본 250개 미만"] }, []);
    expect(fallback.mode).toBe("observation_only");
    expect(JSON.stringify(fallback)).not.toContain("probability");

    const ready = buildRiskCalibrationPresentation({
      publication_status: "READY", probability: 0.27, horizon_sessions: 21,
      event_definition: "subsequent drawdown <= -10%", sample_size: 300,
      brier_score: 0.08, baseline_brier: 0.10, limitations: ["OOS only"], reasons: [],
    }, [{ as_of_date: "2026-07-01", observation_state: "medium", severity: "WATCH", confidence: "MEDIUM", resolved_at: "2026-07-18", outcome: "resolved" }]);
    expect(ready.mode).toBe("qualified_probability");
    expect(ready.qualification).toContain("300");
    expect(ready.score).toContain("0.080");
    expect(ready.history[0].resolved_at).toBe("2026-07-18");
    expect(JSON.stringify(ready)).not.toMatch(/기대수익|매수|매도/);
  });
});
