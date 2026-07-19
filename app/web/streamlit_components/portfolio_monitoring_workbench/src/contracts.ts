export type GroupSummary = {
  portfolio_group_id: string;
  name: string;
  is_default: boolean;
  selected?: boolean;
  status: string;
  version: number;
  active_item_count: number;
  history_item_count: number;
};

export type GroupMetrics = {
  invested_capital: number;
  current_value: number;
  pnl: number;
  total_return: number | null;
  mdd: number | null;
  cagr: number | null;
  observation_days: number;
  short_window: boolean;
  total_contribution: number;
  downside_contribution: number;
  contribution_by_item: Record<string, number>;
};

export type ItemRow = {
  monitoring_item_id: string;
  source_ref: string;
  status: string;
  lane_status: string;
  initial_capital: number;
  current_value: number;
  failure: string | null;
};

export type GroupValueResult = {
  status: "READY" | "PARTIAL" | "EMPTY" | string;
  basis_date: string | null;
  curve: Array<Record<string, string | number | null>>;
  metrics: GroupMetrics;
  failures: Record<string, string>;
  item_rows: ItemRow[];
  active_item_count: number;
  history_item_count: number;
};

export type CatalogItem = {
  source_type: "direct_security" | "selected_strategy";
  source_ref: string;
  instrument_kind: "stock" | "etf" | "strategy";
  label: string;
  metadata: Record<string, unknown>;
  readiness: string;
};

export type PortfolioMonitoringWorkspace = {
  schema_version: "portfolio_monitoring_workspace_v1";
  generated_at: string;
  groups: GroupSummary[];
  active_group: GroupValueResult | null;
  catalog: { query: string; items: CatalogItem[] };
  commands: Array<Record<string, unknown>>;
  method: Record<string, string>;
  boundaries: Record<string, boolean>;
};

export type PortfolioMonitoringEvent =
  | { id: "create_group"; name: string; nonce: string }
  | { id: "rename_group"; portfolio_group_id: string; name: string; expected_version: number; nonce: string }
  | { id: "select_group"; portfolio_group_id: string; nonce: string }
  | { id: "select_item"; monitoring_item_id: string; nonce: string }
  | { id: "search_catalog"; query: string; source_type: "direct_security" | "selected_strategy"; nonce: string }
  | { id: "add_item"; payload: Record<string, unknown>; nonce: string }
  | { id: "end_item"; monitoring_item_id: string; requested_end_date: string; nonce: string };

export type PortfolioMonitoringComponentValue = {
  event: PortfolioMonitoringEvent | null;
};
