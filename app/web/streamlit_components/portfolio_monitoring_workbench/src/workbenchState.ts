import type { DiagnosisProjection, GroupMetrics, GroupSummary, ItemRow } from "./contracts";

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
  return {
    now: diagnosis.top_three.filter((row) => row.confidence !== "LOW").slice(0, 3),
    strengths: diagnosis.strengths,
    weaknesses: diagnosis.weaknesses,
    dataGaps: diagnosis.data_gaps,
    evidence: diagnosis.all_rows,
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
