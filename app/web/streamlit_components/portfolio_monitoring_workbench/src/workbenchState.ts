import type { DiagnosisDisplayGroup, DiagnosisDisplayGroupView, DiagnosisHistoryRow, DiagnosisProjection, DiagnosisRow, GroupMetrics, GroupSummary, ItemRow, MacroObservationProjection, MarketChartRow, RiskCalibrationProjection, SourceHealth } from "./contracts";

export type MonitoringSourceType = "direct_security" | "selected_strategy";
export type MonitoringKind = "stock" | "etf" | "strategy";
export type FundingMode = "fixed_notional" | "fixed_shares";

export type ItemDraft = {
  commandId: string;
  sourceType: MonitoringSourceType;
  selectedSourceRef: string;
  selectedLabel: string;
  selectedKind: MonitoringKind | null;
  requestedStartDate: string;
  fundingMode: FundingMode;
  notional: string;
  shares: string;
};

export type DraftValidationContext = {
  activeItems: Array<Pick<ItemRow, "source_ref" | "status">>;
  capacity: number;
  selectedReadiness: string | null;
};

export type ItemBuilderState = {
  drawerOpen: boolean;
  drawerStep: 1 | 2 | 3;
  catalogQuery: string;
  draft: ItemDraft;
};

export function createItemDraft(commandId: string): ItemDraft {
  return {
    commandId,
    sourceType: "direct_security",
    selectedSourceRef: "",
    selectedLabel: "",
    selectedKind: null,
    requestedStartDate: "",
    fundingMode: "fixed_notional",
    notional: "10000",
    shares: "",
  };
}

export function applySourceType(draft: ItemDraft, sourceType: MonitoringSourceType): ItemDraft {
  return {
    ...draft,
    sourceType,
    selectedSourceRef: "",
    selectedLabel: "",
    selectedKind: sourceType === "selected_strategy" ? "strategy" : null,
    fundingMode: sourceType === "selected_strategy" ? "fixed_notional" : draft.fundingMode,
    shares: sourceType === "selected_strategy" ? "" : draft.shares,
  };
}

export function availableFundingModes(sourceType: MonitoringSourceType): FundingMode[] {
  return sourceType === "selected_strategy"
    ? ["fixed_notional"]
    : ["fixed_notional", "fixed_shares"];
}

export function validateItemDraft(draft: ItemDraft, context: DraftValidationContext): string | null {
  const activeItems = context.activeItems.filter((item) => item.status !== "ended");
  if (activeItems.length >= context.capacity) {
    return `활성 항목은 최대 ${context.capacity}개까지 등록할 수 있습니다.`;
  }
  if (!draft.selectedSourceRef || !draft.selectedKind) {
    return "추적할 종목 또는 전략을 선택하세요.";
  }
  if (activeItems.some((item) => item.source_ref.toLocaleUpperCase() === draft.selectedSourceRef.toLocaleUpperCase())) {
    return "이미 이 포트폴리오에서 추적 중인 항목입니다.";
  }
  if (["MISSING_PRICE", "BLOCKED", "UNAVAILABLE"].includes(String(context.selectedReadiness || "").toLocaleUpperCase())) {
    return "요청일 이후 사용할 수 있는 시작 가격이 없어 등록할 수 없습니다.";
  }
  if (!draft.requestedStartDate) {
    return "추적 시작일을 선택하세요.";
  }
  if (draft.sourceType === "selected_strategy" && draft.fundingMode !== "fixed_notional") {
    return "백테스트 전략은 투자금 방식만 지원합니다.";
  }
  if (draft.fundingMode === "fixed_shares") {
    const shares = Number(draft.shares);
    if (!Number.isInteger(shares)) {
      return "수량은 소수점 없이 정수로 입력하세요.";
    }
    if (shares < 1) {
      return "수량은 1주 이상이어야 합니다.";
    }
  } else {
    const notional = Number(draft.notional);
    if (!Number.isFinite(notional) || notional <= 0) {
      return "투자금은 0보다 큰 금액이어야 합니다.";
    }
  }
  return null;
}

export function drawerPresentation(viewportWidth: number) {
  return viewportWidth <= 520 ? "full_width_sheet" : "side_drawer";
}

function recordValue(value: unknown): Record<string, unknown> | null {
  return value != null && typeof value === "object" && !Array.isArray(value)
    ? value as Record<string, unknown>
    : null;
}

function stringValue(value: unknown, fallback = ""): string {
  return typeof value === "string" ? value : fallback;
}

export function normalizeItemBuilderState(
  value: unknown,
  fallbackCommandId: string,
): ItemBuilderState | null {
  const state = recordValue(value);
  const rawDraft = recordValue(state?.draft);
  if (!state || state.drawer_open !== true || !rawDraft) return null;

  const sourceType: MonitoringSourceType = rawDraft.source_type === "selected_strategy"
    ? "selected_strategy"
    : "direct_security";
  const selectedKind = ["stock", "etf", "strategy"].includes(String(rawDraft.selected_kind))
    ? rawDraft.selected_kind as MonitoringKind
    : null;
  const requestedFundingMode: FundingMode = rawDraft.funding_mode === "fixed_shares"
    ? "fixed_shares"
    : "fixed_notional";
  const fundingMode = sourceType === "selected_strategy" ? "fixed_notional" : requestedFundingMode;
  const rawStep = Number(state.drawer_step);
  const drawerStep = ([1, 2, 3].includes(rawStep) ? rawStep : 1) as 1 | 2 | 3;

  return {
    drawerOpen: true,
    drawerStep,
    catalogQuery: stringValue(state.catalog_query),
    draft: {
      commandId: stringValue(rawDraft.command_id, fallbackCommandId) || fallbackCommandId,
      sourceType,
      selectedSourceRef: stringValue(rawDraft.selected_source_ref),
      selectedLabel: stringValue(rawDraft.selected_label),
      selectedKind,
      requestedStartDate: stringValue(rawDraft.requested_start_date),
      fundingMode,
      notional: stringValue(rawDraft.notional, "10000"),
      shares: fundingMode === "fixed_shares" ? stringValue(rawDraft.shares) : "",
    },
  };
}

/** Stable identity prevents a Streamlit rerender from reapplying one recovery snapshot. */
export function itemBuilderRecoveryKey(state: ItemBuilderState | null): string | null {
  if (!state) return null;
  return JSON.stringify([
    state.drawerOpen,
    state.drawerStep,
    state.catalogQuery,
    state.draft.commandId,
    state.draft.sourceType,
    state.draft.selectedSourceRef,
    state.draft.selectedLabel,
    state.draft.selectedKind,
    state.draft.requestedStartDate,
    state.draft.fundingMode,
    state.draft.notional,
    state.draft.shares,
  ]);
}

export function buildCatalogSearchEvent(
  query: string,
  draft: ItemDraft,
  drawerStep: 1 | 2 | 3,
) {
  return {
    id: "search_catalog",
    query,
    source_type: draft.sourceType,
    requested_start_date: draft.requestedStartDate || undefined,
    item_builder_state: {
      drawer_open: true,
      drawer_step: drawerStep,
      catalog_query: query,
      draft: {
        command_id: draft.commandId,
        source_type: draft.sourceType,
        selected_source_ref: draft.selectedSourceRef,
        selected_label: draft.selectedLabel,
        selected_kind: draft.selectedKind,
        requested_start_date: draft.requestedStartDate,
        funding_mode: draft.fundingMode,
        notional: draft.notional,
        shares: draft.shares,
      },
    },
  };
}

export function buildAddItemPayload(draft: ItemDraft, portfolioGroupId: string) {
  return {
    command_id: draft.commandId,
    portfolio_group_id: portfolioGroupId,
    source_type: draft.sourceType,
    source_ref: draft.selectedSourceRef,
    instrument_kind: draft.selectedKind,
    requested_start_date: draft.requestedStartDate,
    funding_mode: draft.fundingMode,
    input_notional: draft.fundingMode === "fixed_notional" ? Number(draft.notional) : null,
    input_shares: draft.fundingMode === "fixed_shares" ? Number(draft.shares) : null,
  };
}

export type ChartPoint = {
  date: string;
  total: number | null;
  items: Record<string, number | null>;
};

export function selectActiveGroup(groups: GroupSummary[], requestedId: string | null | undefined) {
  const requested = groups.find((group) => group.portfolio_group_id === requestedId);
  return requested ?? groups.find((group) => group.selected) ?? groups.find((group) => group.is_default) ?? groups[0] ?? null;
}

export function selectItem(items: ItemRow[], requestedId: string | null | undefined) {
  const requested = items.find((item) => item.monitoring_item_id === requestedId);
  return requested ?? items.find((item) => item.status !== "ended") ?? items[0] ?? null;
}

export function partitionItemRows(items: ItemRow[]) {
  return {
    active: items.filter((item) => item.status !== "ended"),
    ended: items.filter((item) => item.status === "ended"),
  };
}

export function itemLifecycleLabel(item: Pick<ItemRow, "status">) {
  if (item.status === "ended") return "종료 기록";
  if (item.status === "data_review") return "확인 필요";
  return "활성 추적";
}

function finiteNumber(value: unknown): number | null {
  if (value == null || value === "") {
    return null;
  }
  const parsed = typeof value === "number" ? value : Number(value);
  return Number.isFinite(parsed) ? parsed : null;
}

export function buildGroupChartSeries(
  rows: Array<Record<string, string | number | null>>,
  itemIds: string[],
): ChartPoint[] {
  return rows
    .map((row) => ({
      date: String(row.date ?? ""),
      total: finiteNumber(row.total_value),
      items: Object.fromEntries(itemIds.map((itemId) => [itemId, finiteNumber(row[`item:${itemId}`])])),
    }))
    .filter((row) => row.date)
    .sort((left, right) => left.date.localeCompare(right.date));
}

export type ChartDateTick = {
  index: number;
  date: string;
};

/** Selects evenly spaced actual observations while always retaining the range ends. */
export function buildChartDateTicks(series: ChartPoint[], maxTicks: number): ChartDateTick[] {
  if (!series.length || maxTicks < 1) return [];
  const tickCount = Math.min(Math.max(Math.floor(maxTicks), 1), series.length);
  if (tickCount === 1) return [{ index: 0, date: series[0].date }];

  const indices = Array.from({ length: tickCount }, (_, position) => (
    Math.round((position * (series.length - 1)) / (tickCount - 1))
  ));
  return Array.from(new Set(indices)).map((index) => ({ index, date: series[index].date }));
}

export function nearestChartPointIndex(
  series: ChartPoint[],
  pointerX: number,
  plotLeft: number,
  plotRight: number,
): number | null {
  if (!series.length) return null;
  const validIndices = series
    .map((point, index) => point.total == null ? null : index)
    .filter((index): index is number => index != null);
  if (!validIndices.length) return null;

  const plotWidth = Math.max(plotRight - plotLeft, 1);
  const boundedX = Math.min(Math.max(pointerX, plotLeft), plotRight);
  const targetIndex = ((boundedX - plotLeft) / plotWidth) * Math.max(series.length - 1, 1);
  return validIndices.reduce((nearest, index) => (
    Math.abs(index - targetIndex) < Math.abs(nearest - targetIndex) ? index : nearest
  ));
}

export type MarketChartBounds = {
  minPrice: number;
  maxPrice: number;
  maxVolume: number;
};

export function buildMarketChartBounds(rows: MarketChartRow[]): MarketChartBounds | null {
  if (!rows.length) return null;
  const lows = rows.map((row) => row.low).filter(Number.isFinite);
  const highs = rows.map((row) => row.high).filter(Number.isFinite);
  if (!lows.length || !highs.length) return null;
  const volumes = rows
    .map((row) => row.volume)
    .filter((value): value is number => value != null && Number.isFinite(value) && value >= 0);
  return {
    minPrice: Math.min(...lows),
    maxPrice: Math.max(...highs),
    maxVolume: volumes.length ? Math.max(...volumes) : 0,
  };
}

export function nearestMarketChartRowIndex(
  rowCount: number,
  pointerX: number,
  plotLeft: number,
  plotRight: number,
): number | null {
  if (rowCount < 1) return null;
  const plotWidth = Math.max(plotRight - plotLeft, 1);
  const boundedX = Math.min(Math.max(pointerX, plotLeft), plotRight);
  const target = ((boundedX - plotLeft) / plotWidth) * Math.max(rowCount - 1, 0);
  return Math.min(Math.max(Math.round(target), 0), rowCount - 1);
}

export const MIN_MARKET_CHART_VISIBLE_ROWS = 15;

export type MarketChartViewport = {
  startIndex: number;
  endIndex: number;
};

function safeMarketChartRowCount(rowCount: number) {
  return Math.max(Math.floor(Number.isFinite(rowCount) ? rowCount : 0), 1);
}

export function buildFullMarketChartViewport(rowCount: number): MarketChartViewport {
  const safeRowCount = safeMarketChartRowCount(rowCount);
  return { startIndex: 0, endIndex: safeRowCount - 1 };
}

export function normalizeMarketChartViewport(
  viewport: MarketChartViewport,
  rowCount: number,
  minimumVisible = MIN_MARKET_CHART_VISIBLE_ROWS,
): MarketChartViewport {
  const safeRowCount = safeMarketChartRowCount(rowCount);
  const minimumCount = Math.min(
    Math.max(Math.floor(Number.isFinite(minimumVisible) ? minimumVisible : 1), 1),
    safeRowCount,
  );
  const requestedStart = Number.isFinite(viewport.startIndex) ? Math.floor(viewport.startIndex) : 0;
  const requestedEnd = Number.isFinite(viewport.endIndex) ? Math.floor(viewport.endIndex) : requestedStart;
  const requestedCount = Math.max(requestedEnd - requestedStart + 1, minimumCount);
  const visibleCount = Math.min(requestedCount, safeRowCount);
  const startIndex = Math.min(Math.max(requestedStart, 0), safeRowCount - visibleCount);
  return { startIndex, endIndex: startIndex + visibleCount - 1 };
}

export function zoomMarketChartViewport(
  viewport: MarketChartViewport,
  rowCount: number,
  anchorRatio: number,
  direction: "in" | "out",
  minimumVisible = MIN_MARKET_CHART_VISIBLE_ROWS,
): MarketChartViewport {
  const normalized = normalizeMarketChartViewport(viewport, rowCount, minimumVisible);
  const safeRowCount = safeMarketChartRowCount(rowCount);
  const visibleCount = normalized.endIndex - normalized.startIndex + 1;
  const minimumCount = Math.min(
    Math.max(Math.floor(Number.isFinite(minimumVisible) ? minimumVisible : 1), 1),
    safeRowCount,
  );
  const targetCount = direction === "in"
    ? Math.max(minimumCount, Math.round(visibleCount * 0.8))
    : Math.min(safeRowCount, Math.round(visibleCount * 1.25));
  if (targetCount === visibleCount) return normalized;
  const ratio = Number.isFinite(anchorRatio) ? Math.min(Math.max(anchorRatio, 0), 1) : 0.5;
  const anchorIndex = normalized.startIndex + ratio * Math.max(visibleCount - 1, 0);
  const targetStart = Math.round(anchorIndex - ratio * Math.max(targetCount - 1, 0));
  return normalizeMarketChartViewport(
    { startIndex: targetStart, endIndex: targetStart + targetCount - 1 },
    safeRowCount,
    targetCount,
  );
}

export function panMarketChartViewport(
  viewport: MarketChartViewport,
  rowCount: number,
  deltaX: number,
  plotWidth: number,
): MarketChartViewport {
  const normalized = normalizeMarketChartViewport(viewport, rowCount);
  if (!Number.isFinite(deltaX) || !Number.isFinite(plotWidth) || plotWidth <= 0) return normalized;
  const visibleCount = normalized.endIndex - normalized.startIndex + 1;
  const rowDelta = Math.round((deltaX / plotWidth) * visibleCount);
  return normalizeMarketChartViewport({
    startIndex: normalized.startIndex - rowDelta,
    endIndex: normalized.endIndex - rowDelta,
  }, rowCount, visibleCount);
}

export type ChartTooltipBounds = {
  chartWidth: number;
  plotTop: number;
  plotBottom: number;
  tooltipWidth: number;
  tooltipHeight: number;
};

export function placeChartTooltip(
  pointX: number,
  pointY: number,
  bounds: ChartTooltipBounds,
) {
  const gap = 12;
  const useLeft = pointX + gap + bounds.tooltipWidth > bounds.chartWidth;
  const x = useLeft
    ? Math.max(8, pointX - gap - bounds.tooltipWidth)
    : pointX + gap;
  const maximumY = Math.max(bounds.plotTop, bounds.plotBottom - bounds.tooltipHeight);
  const y = Math.min(
    Math.max(pointY - bounds.tooltipHeight / 2, bounds.plotTop),
    maximumY,
  );
  return { x, y, side: useLeft ? "left" as const : "right" as const };
}

export function buildCommonBasisBanner(group: { status: string; basis_date: string | null }) {
  if (!group.basis_date) {
    return "공통 평가 기준일을 계산할 수 없습니다.";
  }
  if (group.status === "PARTIAL") {
    return `일부 항목은 가치 계산이 제한되어 원금을 현금으로 유지했습니다. 공통 기준일 ${group.basis_date}`;
  }
  return `모든 활성 항목을 비교할 수 있는 공통 기준일 ${group.basis_date}`;
}

export function buildDiagnosisSections(diagnosis: DiagnosisProjection) {
  const view = (group: DiagnosisDisplayGroup): DiagnosisDisplayGroupView => ({
    ...group.representative,
    ...group,
  });
  const legacy = (
    row: DiagnosisRow,
    section: DiagnosisDisplayGroup["section"],
  ): DiagnosisDisplayGroupView => ({
    ...row,
    group_id: row.root_id ?? row.rule_id,
    family: row.rule_id.split(":", 1)[0],
    section,
    representative: row,
    summary_fact: row.measured_fact,
    member_count: 1,
    members: [row],
  });
  const serverGroups = diagnosis.display_groups;
  const legacyPayload = serverGroups === undefined;
  const groups = serverGroups === undefined
    ? [
      ...diagnosis.strengths.map((row) => legacy(row, "strength")),
      ...diagnosis.weaknesses.map((row) => legacy(row, "weakness")),
      ...diagnosis.data_gaps.map((row) => legacy(row, "data_gap")),
    ]
    : serverGroups.map(view);
  const weaknesses = groups.filter((group) => group.section === "weakness");
  return {
    now: (legacyPayload
      ? diagnosis.top_three.map((row) => legacy(row, "weakness"))
      : weaknesses
    ).filter((group) => group.confidence !== "LOW").slice(0, 3),
    strengths: groups.filter((group) => group.section === "strength"),
    weaknesses,
    dataGaps: groups.filter((group) => group.section === "data_gap"),
    evidence: diagnosis.all_rows,
  };
}

export function buildMacroObservationPresentation(
  observation: MacroObservationProjection,
  sourceHealth: SourceHealth,
) {
  const labels: Record<string, string> = { low: "낮음", medium: "중간", high: "높음" };
  return {
    stateLabel: labels[observation.state] ?? observation.state,
    sourceChip: `${sourceHealth.status} · coverage ${(sourceHealth.coverage * 100).toFixed(0)}%`,
    rows: observation.rows,
    topRows: observation.top_rows.filter((row) => row.confidence !== "LOW").slice(0, 3),
    staleWarning: sourceHealth.warnings.join(" · "),
    dates: sourceHealth.as_of_dates,
  };
}

export function buildRiskCalibrationPresentation(
  calibration: RiskCalibrationProjection,
  history: DiagnosisHistoryRow[],
) {
  if (calibration.publication_status !== "READY" || calibration.probability == null) {
    return {
      mode: "observation_only" as const,
      status: calibration.publication_status,
      reasons: calibration.reasons,
      history,
    };
  }
  return {
    mode: "qualified_probability" as const,
    status: calibration.publication_status,
    probability: calibration.probability,
    horizonSessions: calibration.horizon_sessions,
    eventDefinition: calibration.event_definition,
    qualification: `OOS ${calibration.sample_size ?? 0}개 · baseline 대비 Brier 검증`,
    score: `Brier ${(calibration.brier_score ?? 0).toFixed(3)} / baseline ${(calibration.baseline_brier ?? 0).toFixed(3)}`,
    limitations: calibration.limitations ?? [],
    history,
  };
}

function signedPercent(value: number) {
  const sign = value > 0 ? "+" : "";
  return `${sign}${(value * 100).toFixed(2)}%`;
}

export function formatMetric(
  value: number | null | undefined,
  kind: "currency" | "percent" | "cagr" | "number",
  metrics?: Pick<GroupMetrics, "short_window" | "observation_days">,
) {
  if (value == null || !Number.isFinite(value)) {
    return "-";
  }
  if (kind === "currency") {
    return new Intl.NumberFormat("en-US", {
      style: "currency",
      currency: "USD",
      maximumFractionDigits: 0,
    }).format(value);
  }
  if (kind === "percent" || kind === "cagr") {
    const label = signedPercent(value);
    return kind === "cagr" && metrics?.short_window
      ? `${label} · ${metrics.observation_days}일 연환산`
      : label;
  }
  return new Intl.NumberFormat("ko-KR", { maximumFractionDigits: 2 }).format(value);
}
