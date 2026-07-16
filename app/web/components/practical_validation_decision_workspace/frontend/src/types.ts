export type Tone = "positive" | "warning" | "danger" | "neutral"

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
      source_type: string
      selected: boolean
      eligible: boolean
    }>
  }
  candidate: {
    selection_source_id: string
    title: string
    source_type: string
    as_of: string
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
  }
  replay: { status: string; replay_id: string; completed: boolean }
  verdict: { tone: Tone; label: string; headline: string; detail: string }
  summary: Record<string, number>
  verified_findings: Array<{
    finding_id: string
    finding_kind: "verified"
    title: string
    detail: string
    category_id: string
  }>
  measured_cautions: Issue[]
  resolution_lanes: {
    resolve_now: Issue[]
    engineering_required: Issue[]
    final_review_handoff: Issue[]
  }
  category_disclosures: Array<{
    category_id: string
    title: string
    question: string
    outcome: string
    verified_items: string[]
    root_issue_ids: string[]
    technical_rows: Array<{
      row_id: string
      title: string
      status: string
      detail: string
    }>
  }>
  actions: {
    run_replay: { id: string; label: string; enabled: boolean }
    save_audit_only: { id: string; label: string; enabled: boolean }
    save_and_move: { id: string; label: string; enabled: boolean }
  }
}
