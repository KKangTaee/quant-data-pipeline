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
  gross_contributions: number;
  gross_withdrawals: number;
  net_contributions: number;
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

export type PositionEventRow = {
  root_event_id: string;
  current_event_id: string;
  position_event_id: string;
  status: "active" | "superseded" | "voided";
  position_effect: "initial_quantity_correction" | "buy" | "sell";
  trade_date: string;
  event_order: number;
  quantity: number | null;
  execution_price: number | null;
  reference_close: number | null;
  execution_price_source: "db_close_default" | "manual_override" | null;
  fee_usd: number;
  note: string;
  shares_after: number | null;
};

export type SelectedPositionProjection = {
  monitoring_item_id: string | null;
  eligible: boolean;
  reason: string | null;
  as_of_date: string | null;
  current_value: number | null;
  requested_start_date?: string | null;
  effective_start_date?: string | null;
  entry_close?: number | null;
  initial_capital?: number | null;
  effective_initial_shares: number | null;
  current_shares: number | null;
  gross_contributions: number;
  gross_withdrawals: number;
  pnl: number | null;
  total_return: number | null;
  event_rows: PositionEventRow[];
};

export type PositionTradeCloseProjection = {
  status: "IDLE" | "READY" | "MISSING" | string;
  monitoring_item_id: string | null;
  trade_date: string | null;
  reference_close: number | null;
  reason: string | null;
};

export type InitialPositionEntryProjection = {
  status: "IDLE" | "READY" | "MISSING" | string;
  monitoring_item_id: string | null;
  requested_start_date: string | null;
  effective_start_date: string | null;
  quantity: number | null;
  entry_close: number | null;
  initial_capital: number | null;
  reason: string | null;
};

export type PositionEditorRecoveryState = {
  open: true;
  mode: "record" | "replace" | "correction";
  position_effect: "buy" | "sell";
  trade_date: string;
  quantity: string;
  execution_price: string;
  price_mode: "awaiting_close" | "db_close_default" | "manual_override";
  fee_usd: string;
  note: string;
  root_event_id: string;
  expected_event_id: string;
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

export type MarketChartRow = {
  date: string;
  open: number;
  high: number;
  low: number;
  close: number;
  volume: number | null;
};

export type SelectedItemMarketChart = {
  status: "READY" | "UNSUPPORTED" | "MISSING" | "ERROR";
  monitoring_item_id: string | null;
  source_type: "direct_security" | "selected_strategy" | null;
  source_ref: string | null;
  instrument_kind: "stock" | "etf" | "strategy" | string | null;
  timeframe: "1d";
  max_rows: number;
  rows: MarketChartRow[];
  reason: string | null;
};

export type PriceRefreshRow = {
  symbol: string;
  latest_date: string | null;
  status: "current" | "stale" | "missing" | string;
};

export type PriceRefreshProjection = {
  status: "refresh_available" | "up_to_date" | "unavailable" | string;
  eligible: boolean;
  target_date: string | null;
  current_common_latest: string | null;
  symbols: string[];
  stale_symbols: string[];
  missing_symbols: string[];
  excluded_strategy_count: number;
  collection_start: string | null;
  collection_end: string | null;
  button_label: string;
  rows: PriceRefreshRow[];
  message: string;
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
  subject_ids?: string[];
  primary_metric?: number | null;
};

export type DiagnosisDisplayGroup = {
  group_id: string;
  family: string;
  section: "strength" | "weakness" | "data_gap";
  representative: DiagnosisRow;
  summary_fact: string;
  member_count: number;
  members: DiagnosisRow[];
};

export type DiagnosisDisplayGroupView = DiagnosisRow & DiagnosisDisplayGroup;

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
  display_groups?: DiagnosisDisplayGroup[];
  coverage?: number;
};

export type PortfolioMonitoringWorkspace = {
  schema_version: "portfolio_monitoring_workspace_v2";
  generated_at: string;
  groups: GroupSummary[];
  active_group: GroupValueResult | null;
  selected_position: SelectedPositionProjection;
  position_trade_close?: PositionTradeCloseProjection;
  initial_position_entry?: InitialPositionEntryProjection;
  position_editor_state?: PositionEditorRecoveryState | null;
  selected_item_market_chart?: SelectedItemMarketChart;
  price_refresh: PriceRefreshProjection;
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
  | { id: "end_item"; monitoring_item_id: string; requested_end_date: string; nonce: string }
  | { id: "reopen_item"; monitoring_item_id: string; nonce: string }
  | { id: "refresh_group_prices"; command_id: string; portfolio_group_id: string; nonce: string }
  | { id: "lookup_position_trade_close"; monitoring_item_id: string; trade_date: string; position_editor_state: PositionEditorRecoveryState; nonce: string }
  | { id: "lookup_initial_position_entry"; monitoring_item_id: string; requested_start_date: string; quantity: number; position_editor_state: PositionEditorRecoveryState; nonce: string }
  | { id: "correct_initial_quantity"; command_id: string; monitoring_item_id: string; requested_start_date: string; quantity: number; note: string; nonce: string }
  | { id: "record_position_trade"; command_id: string; monitoring_item_id: string; position_effect: "buy" | "sell"; trade_date: string; quantity: number; execution_price: number; fee_usd: number; note: string; nonce: string }
  | { id: "replace_position_trade"; command_id: string; monitoring_item_id: string; root_event_id: string; expected_event_id: string; position_effect: "buy" | "sell"; trade_date: string; quantity: number; execution_price: number; fee_usd: number; note: string; nonce: string }
  | { id: "void_position_trade"; command_id: string; monitoring_item_id: string; root_event_id: string; expected_event_id: string; nonce: string };

export type PortfolioMonitoringComponentValue = {
  event: PortfolioMonitoringEvent | null;
};
