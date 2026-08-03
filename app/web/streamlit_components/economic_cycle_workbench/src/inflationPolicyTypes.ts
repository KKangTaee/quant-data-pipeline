export type InflationPublicationStatus = "READY" | "LIMITED" | "NOT_AVAILABLE" | "FAILED";

export type InflationStateRow = {
  id: string;
  label: string;
  probability: number;
};

export type NextReleaseScenario = {
  mom_pct: number;
  publication_status: InflationPublicationStatus;
  reacceleration_delta?: number | null;
  hike_delta?: number | null;
  reason?: string | null;
};

export type ResistanceZone = {
  definition_id: string;
  owner: "AUTO" | "USER";
  owner_label: string;
  definition_name: string;
  instrument: string;
  zone_lower_pct: number;
  zone_upper_pct: number;
  buffer_pct: number;
  short_lookback_days?: number | null;
  long_lookback_days?: number | null;
  confirmation_profile: Record<string, unknown>;
  known_at?: string | null;
  saved_at?: string | null;
  algorithm_version: string;
  state?: string | null;
  zone_strength?: number | null;
  timeframes: number[];
  source: string;
  editable: boolean;
};

export type EquityStressPayload = {
  publication_status: InflationPublicationStatus;
  reason: string;
  as_of_at?: string | null;
  index_quantiles: Record<string, number>;
  eps_quantiles: Record<string, number>;
  multiple_quantiles: Record<string, number>;
  threshold_probabilities: Record<string, number>;
  target_decompositions: Record<string, Record<string, unknown>>;
  measured_next_year_eps_revision_pct?: number | null;
  user_ai_eps_uplift_pct: number;
  scenario_kind: string;
  current_index_level?: number | null;
  base_forward_eps?: number | null;
};

export type InflationPolicyPayload = {
  schema_version: "inflation_policy_v1";
  publication_status: InflationPublicationStatus;
  as_of_at?: string | null;
  model_version?: string | null;
  headline: {
    title: string;
    summary: string;
    is_historical: boolean;
    history_label: string;
    run_kind: string;
  };
  inflation: {
    publication_status: InflationPublicationStatus;
    reason: string;
    q4_quantiles_pct: Record<string, number>;
    state_probabilities: Record<string, number>;
    state_rows: InflationStateRow[];
    threshold_probabilities: Record<string, number>;
    next_release_scenarios: NextReleaseScenario[];
    state_definition: Record<string, unknown>;
  };
  policy: {
    publication_status: InflationPublicationStatus;
    reason: string;
    next_meeting_probabilities: Record<string, number>;
    net_move_probabilities: Record<string, number>;
    year_end_target_probabilities: Record<string, number>;
    committee_vote_prior: Record<string, number>;
    sep_net_move_prior: Record<string, number>;
  };
  rates: {
    publication_status: InflationPublicationStatus;
    reason: string;
    ten_year: Record<string, unknown>;
    instruments: Record<string, unknown>;
    driver_decomposition: Record<string, unknown>;
    inflation_confirmation: Record<string, unknown>;
    term_premium_status: InflationPublicationStatus;
    resistance_zones: ResistanceZone[];
  };
  reverse_scenario: Record<string, unknown> & {
    publication_status: InflationPublicationStatus;
    reason: string;
  };
  equity_stress: EquityStressPayload;
  recession: { publication_status: InflationPublicationStatus; reason: string };
  evidence: { items: Record<string, unknown>[]; details: Record<string, unknown> };
  freshness: Record<string, unknown>;
  warnings: string[];
  command_result?: Record<string, unknown> & {
    command_id?: InflationPolicyCommand["id"];
    publication_status?: InflationPublicationStatus;
    reason?: string;
  };
};

export type SaveCriterionPayload = {
  owner: "USER";
  definition_name: string;
  instrument: string;
  zone_lower_pct: number;
  zone_upper_pct: number;
  buffer_pct: number;
  short_lookback_days: 63 | 252 | 504;
  long_lookback_days: 63 | 252 | 504;
  confirmation_count: number;
  confirmation_window: number;
  require_breakeven_confirmation: boolean;
  exclude_term_premium_only: boolean;
  as_of_at?: string | null;
};

export type ReverseScenarioPayload = {
  instrument: string;
  zone_lower_pct: number;
  zone_upper_pct: number;
  buffer_pct: number;
  condition: "REACH" | "CONFIRMED" | "HOLD";
  hold_days: number;
  horizon_at: string;
  as_of_at?: string | null;
};

export type EquityScenarioPayload = {
  target_level: number;
  user_ai_eps_uplift_pct: number;
  as_of_at?: string | null;
};

export type InflationPolicyCommand =
  | { id: "save_yield_criterion"; nonce: string; payload: SaveCriterionPayload }
  | { id: "run_reverse_scenario"; nonce: string; payload: ReverseScenarioPayload }
  | { id: "run_equity_stress_scenario"; nonce: string; payload: EquityScenarioPayload };

export type InflationPolicyWorkbenchProps = {
  payload: InflationPolicyPayload;
  onCommand: (command: InflationPolicyCommand) => void;
};
