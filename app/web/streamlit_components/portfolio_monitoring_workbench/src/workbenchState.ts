import type { GroupMetrics, GroupSummary, ItemRow } from "./contracts";

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
