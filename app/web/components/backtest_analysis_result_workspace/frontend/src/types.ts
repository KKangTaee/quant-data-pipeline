export type WorkspaceAction = {
  id: string
  label: string
  enabled: boolean
}

export type ResultWorkspaceIntent = {
  action: "save_and_move"
  payload: {
    run_result_id: string
    current_configuration_fingerprint: string
  }
  nonce: string
}

export type DisplayMetric = {
  metric_id: string
  label: string
  value: unknown
  value_label: string
}

export type CurvePoint = {
  date: string
  value: number
  value_label: string
}

export type AllocationRow = {
  ticker: string
  weight: number | null
  weight_label: string
}

export type ResultWorkspace = {
  schema_version: string
  visible: boolean
  configuration_fingerprint: string
  lifecycle: {
    state: string
    display_label: string
    show_workspace: boolean
    result_available: boolean
    fingerprint_matches: boolean
    reference_only: boolean
    is_running: boolean
    error?: { kind: string; message: string } | null
  }
  identity: {
    run_result_id: string
    candidate_source_id: string
    validation_result_id: string
    strategy_name: string
    variant_name: string
    run_at: string
    period_label: string
  }
  performance_summary: DisplayMetric[]
  chart: {
    strategy_series: CurvePoint[]
    benchmark_series: CurvePoint[]
    markers: Array<CurvePoint & {
      marker_id: string
      label: string
      drawdown?: number
      drawdown_label?: string
    }>
    benchmark_missing_reason: string
  }
  holdings: {
    as_of: string
    target_as_of: string
    current_allocation: AllocationRow[]
    target_allocation: AllocationRow[]
    additions: string[]
    removals: string[]
    cash: number | null
    status: string
    explanation: string
    unavailable_reason: string
    evidence_status: string
    components?: Array<{
      component_id: string
      label: string
      weight: number | null
      target_allocation: AllocationRow[]
      status: string
    }>
  }
  technical_handoff_readiness: {
    state: string
    label: string
    can_handoff: boolean
    reasons: Array<{ root_issue_id: string; message: string }>
    action?: WorkspaceAction | null
  }
  level2_validation_questions: Array<{
    question_id: string
    root_issue_id: string
    lane: string
    lane_label: string
    status: string
    title: string
    summary: string
  }>
  evidence_groups: Array<{
    group_id: string
    label: string
    summary: string
    items: Array<{ label: string; value: string }>
  }>
  performance_rows: Array<{
    date: string
    balance: string
    period_return: string
    drawdown: string
    holding_count: number
    turnover: string
    cost: string
  }>
  holding_change_rows: Array<{
    date: string
    state: string
    current: string
    target: string
    additions: string
    removals: string
    cash: string
  }>
  technical_appendix: {
    row_count: number
    columns: string[]
    prepared_rows: Array<Record<string, unknown>>
    preview_limited: boolean
    meta_rows: Array<{ key: string; value: unknown }>
  }
  actions: Record<string, WorkspaceAction>
  boundaries: Record<string, boolean>
}
