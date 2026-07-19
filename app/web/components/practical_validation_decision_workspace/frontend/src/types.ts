export type Tone = "positive" | "warning" | "danger" | "neutral"
export type WorkspaceSurface = "context" | "decision"

export type EvidenceExplanation = {
  display_title: string
  status_label: string
  what_was_checked: string
  result_summary: string
  meaning: string
  next_action: string
  evidence_state: string
  stage_owner: string
  technical_trace: {
    criterion: string
    status: string
    current: string
    evidence: string
    next_action: string
  }
}

export type WorkspaceIntent =
  | {
      action: "select_source"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
    }
  | {
      action: "select_profile_preset"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
      profile_id: string
    }
  | {
      action: "update_profile_answer"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
      question_id: string
      answer: string
    }
  | {
      action: "select_recheck_mode"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
      recheck_mode: string
    }
  | {
      action: "run_replay"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
    }
  | {
      action: "run_resolution_action"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
      root_issue_id: string
      action_id: string
    }
  | {
      action: "save_audit_only"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
    }
  | {
      action: "save_and_move"
      intent_id: string
      selection_source_id: string
      validation_result_id: string
    }

export type Issue = {
  root_issue_id: string
  title: string
  finding_kind: string
  resolution_class: string
  observed: string
  expected: string
  cause: string
  criticality: string
  terminal_state: string
  actionable_now: boolean
  action_id?: string | null
  action_label: string
  completion_criteria: string
  derived_checks: string[]
  measurement: Record<string, unknown>
  explanations: EvidenceExplanation[]
}

export type DecisionWorkspace = {
  schema_version: string
  selection_source_id: string
  validation_result_id: string
  state: string
  header: { question: string; detail: string }
  candidate_selector: {
    selected_source_id: string
    options: Array<{
      selection_source_id: string
      title: string
      source_type_label: string
      selected: boolean
      eligible: boolean
    }>
  }
  candidate: {
    selection_source_id: string
    title: string
    source_type_label: string
    as_of: string
    provenance: {
      period_label: string
      cagr_label: string
      mdd_label: string
      component_count: number
      data_trust_label: string
      warning_count: number
    }
  }
  profile: {
    profile_id: string
    profile_label: string
    options: Array<{
      profile_id: string
      label: string
      description: string
      selected: boolean
    }>
    questions: Array<{
      question_id: string
      label: string
      value: string
      options: Array<{ value: string; label: string }>
    }>
    threshold_summary: {
      rolling_window_months: number
      mdd_review_line: number
      one_way_cost_bps: number
    }
  }
  replay: {
    status: string
    replay_id: string
    completed: boolean
    mode: string
    mode_label: string
    mode_options: Array<{
      value: string
      label: string
      description: string
      recommended: boolean
      selected: boolean
    }>
    provenance: {
      visible: boolean
      mode_label: string
      requested_period_label: string
      actual_period_label: string
      latest_common_price_date: string
      coverage_status: string
      end_gap_days: number
      limiting_symbols: string[]
    }
  }
  record: {
    visible: boolean
    profile_label: string
    recheck_mode_label: string
    attempted_at: string
    replay_id: string
    validation_id: string
  }
  verdict: { tone: Tone; label: string; headline: string; detail: string }
  summary: Record<string, number>
  verified_findings: Array<{
    finding_id: string
    finding_kind: "verified"
    category_id: string
  } & EvidenceExplanation>
  validated_cautions: Issue[]
  measured_cautions: Issue[]
  resolution_lanes: {
    resolve_now: Issue[]
    engineering_required: Issue[]
    final_review_handoff: Issue[]
  }
  handoff_presentation: {
    state: "prospective" | "promoted"
    title: string
    detail: string
  }
  handoff_summary: {
    state: "prospective" | "promoted"
    title: string
    detail: string
    counts: {
      final_decision: number
      accepted_limit: number
      monitoring_transfer: number
    }
    items: Array<{
      root_issue_id: string
      handoff_kind: "final_decision" | "accepted_limit" | "monitoring_transfer"
      handoff_label: string
      title: string
      summary: string
      next_stage_action: string
    }>
  }
  category_disclosures: Array<{
    category_id: string
    title: string
    question: string
    outcome: string
    summary: {
      total_count: number
      verified_count: number
      review_count: number
      missing_count: number
      not_applicable_count: number
    }
    verified_items: string[]
    root_issue_ids: string[]
    explanations: EvidenceExplanation[]
  }>
  actions: {
    run_replay: { id: string; label: string; enabled: boolean }
    save_audit_only: { id: string; label: string; enabled: boolean }
    save_and_move: { id: string; label: string; enabled: boolean }
  }
}
