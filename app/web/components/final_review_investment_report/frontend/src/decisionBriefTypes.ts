export type Tone = "positive" | "warning" | "danger" | "neutral"

export type SeriesPoint = {
  date: string
  value: number
}

export type DecisionBriefSeries = {
  status: "measured" | "unmeasured"
  label: string
  source: string | null
  basis: "net_cost_applied" | "stored_curve_cost_unverified" | "benchmark"
  missing_reason: string | null
  points: SeriesPoint[]
}

export type DecisionBriefObservation = {
  observation_id: string
  root_issue_id: string | null
  title: string
  interpretation: string
  measured_value: number | string
  display_value: string
  threshold_or_comparator: number | string | null
  evidence_refs: string[]
  as_of: string | null
  primary_role?: "strength" | "weakness" | "monitoring"
}

export type MonitoringCondition = DecisionBriefObservation & {
  observation: string
  threshold: string
  cadence: string
  re_review_action: string
  primary_role: "monitoring"
}

export type CharacterProfileItem = {
  axis_id: string
  label: string
  measurement_status: "observed" | "evidence_missing"
  measured_value: number | null
  display_value: string
  unit: "percent" | "ratio_percent" | "bps" | "text"
  interpretation: string
  evidence_refs: string[]
  as_of: string | null
}

export type ReviewPressureItem = {
  axis_id: string
  label: string
  status: "within_limit" | "exceeds_limit" | "criterion_missing" | "evidence_missing"
  measured_value: number | null
  display_value: string
  criterion_value: number | null
  criterion_display: string | null
  comparison: "less_or_equal" | "absolute_less_or_equal" | "greater_or_equal" | null
  delta_value: number | null
  delta_display: string | null
  ratio_to_criterion: number | null
  summary: string
  evidence_refs: string[]
  as_of: string | null
}

export type DecisionOption = {
  route: string
  label: string
  tone: Tone
  recordable: boolean
  disabled_reason: string
  reason_placeholder: string
  button_label: string
}

export type DecisionBrief = {
  schema_version: "decision_brief_v1"
  candidate: {
    source_id: string
    validation_id: string
    title: string
    source_type: string
    as_of: string | null
  }
  eligibility: {
    eligible: boolean
    unresolved_actionable_count: number
    critical_engineering_count: number
    missing_contract_count: number
    pre_selection_unresolved_count: number
  }
  verdict: {
    route: string
    label: string
    tone: Tone
    headline: string
    thesis: string
  }
  evidence_confidence: {
    value: number
    label: string
    ready_checks: number
    total_checks: number
    basis: string
  }
  behavior_board: {
    period: {
      start: string | null
      end: string | null
      frequency: string
      requested_market_date?: string | null
      last_complete_rebalance_date?: string | null
      latest_valuation_date?: string | null
    }
    cumulative_series: DecisionBriefSeries
    benchmark_series: DecisionBriefSeries
    underwater_series: DecisionBriefSeries
    execution_observations: DecisionBriefObservation[]
  }
  character_profile: { items: CharacterProfileItem[] }
  review_pressure: { items: ReviewPressureItem[] }
  strengths: DecisionBriefObservation[]
  weaknesses: DecisionBriefObservation[]
  monitoring_conditions: MonitoringCondition[]
  decision_action: {
    suggested_route: string
    suggested_label: string
    reason_label: string
    reason_help: string
    options: DecisionOption[]
  }
  disclosures: {
    accepted_limits?: Array<Record<string, unknown>>
    source_gaps?: string[]
    provenance?: string[]
    unstructured_monitoring_triggers?: string[]
  }
  capabilities: {
    can_record_decision: boolean
    can_select_for_monitoring: boolean
    provider_fetch: false
    validation_rerun: false
    storage_append_in_react: false
  }
}

export type CandidateSelectorOption = {
  source_id: string
  validation_id: string
  title: string
  source_type: string
  eligible: boolean
  selected: boolean
}

export type CandidateSelectorModel = {
  schema_version: "decision_brief_candidate_selector_v1"
  options: CandidateSelectorOption[]
}

export type CandidateSelectionIntent = {
  action: "select_candidate"
  intent_id: string
  source_id: string
}

export type FinalDecisionIntent = {
  action: "record_final_decision"
  intent_id: string
  decision_route: string
  operator_reason: string
}

export type DecisionWorkspaceIntent = CandidateSelectionIntent | FinalDecisionIntent
