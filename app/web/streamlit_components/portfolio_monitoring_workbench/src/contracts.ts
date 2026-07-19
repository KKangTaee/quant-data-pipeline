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

export type DiagnosisRow = {
  rule_id: string;
  root_id?: string;
  policy_version: string;
  classification: "strength" | "weakness" | "data_gap" | string;
  severity: string;
  persistence: number;
  affected_weight: number;
  contribution: number | null;
  measured_fact: string;
  threshold: string;
  source_dates: string[];
  coverage: number;
  confidence: string;
  meaning: string;
  change_condition: string;
  next_check: string;
};

export type MacroObservationRow = {
  rule_id: string;
  root_id: string;
  state: "low" | "medium" | "high" | string;
  severity: string;
  affected_weight: number;
  matched_conditions: string[];
  current_observation: string;
  source_dates: string[];
  coverage: number;
  confidence: string;
  publication: string;
  change_condition: string;
  next_check: string;
};

export type MacroObservationProjection = {
  version: string;
  state: "low" | "medium" | "high" | string;
  rows: MacroObservationRow[];
  top_rows: MacroObservationRow[];
};

export type SourceHealth = {
  status: string;
  publication: string;
  coverage: number;
  as_of_dates: Record<string, string>;
  warnings: string[];
};

export type RiskCalibrationProjection = {
  publication_status: "SUPPRESSED" | "LIMITED" | "READY" | string;
  reasons: string[];
  probability?: number;
  horizon_sessions?: number;
  event_definition?: string;
  sample_size?: number;
  brier_score?: number;
  baseline_brier?: number;
  limitations?: string[];
};

export type DiagnosisHistoryRow = {
  as_of_date: string;
  observation_state: string;
  severity: string;
  confidence: string;
  resolved_at: string | null;
  outcome: string | null;
};

export type DiagnosisProjection = {
  policy_version: string;
  top_three: DiagnosisRow[];
  strengths: DiagnosisRow[];
  weaknesses: DiagnosisRow[];
  data_gaps: DiagnosisRow[];
  all_rows: DiagnosisRow[];
  coverage?: number;
};

export type PortfolioMonitoringWorkspace = {
  schema_version: "portfolio_monitoring_workspace_v1";
  generated_at: string;
  groups: GroupSummary[];
  active_group: GroupValueResult | null;
  catalog: { query: string; items: CatalogItem[] };
  commands: CommandProjection[];
  item_builder_state?: unknown;
  diagnosis: DiagnosisProjection;
  macro_observation: MacroObservationProjection;
  now_to_review: Array<Record<string, unknown>>;
  source_health: SourceHealth;
  risk_calibration: RiskCalibrationProjection;
  diagnosis_history: DiagnosisHistoryRow[];
  method: Record<string, string>;
  boundaries: Record<string, boolean | string | null>;
};

export type CommandProjection = {
  command_id: string;
  status: "idle" | "pending" | "success" | "error" | "succeeded" | "failed" | string;
  message?: string | null;
  target_id?: string | null;
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
