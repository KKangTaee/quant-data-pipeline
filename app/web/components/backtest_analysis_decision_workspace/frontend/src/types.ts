export type WorkspaceSurface = "context" | "settings" | "decision"

export type SettingsOption = {
  value: unknown
  label: string
}

export type SettingsField = {
  field_id: string
  payload_key: string
  label: string
  control:
    | "date"
    | "number"
    | "text"
    | "single_select"
    | "multi_select"
    | "segmented"
    | "toggle"
  value: unknown
  required: boolean
  help: string
  options?: SettingsOption[]
  min?: number
  max?: number
  step?: number
  advanced?: boolean
  wide?: boolean
  visible_when?: Record<string, unknown>
}

export type SettingsSection = {
  section_id: string
  title: string
  description: string
  fields: SettingsField[]
  disclosures: Array<Record<string, unknown>>
}

export type SingleSettingsWorkspace = {
  schema_version: string
  strategy_choice: string
  concrete_strategy_key: string
  draft_key: string
  profile: {
    display_name: string
    purpose_label: string
    maturity_label: string
    description: string
    selection_rule: string
    holding_rule: string
    risk_note: string
  }
  variant: {
    value: string | null
    options: SettingsOption[]
  }
  sections: SettingsSection[]
  evidence: {
    universe_summary: string
    universe_full_text: string
    technical_rows: Array<Record<string, unknown>>
  }
  action: WorkspaceAction
  validation_errors: Record<string, string>
}

export type WorkspaceAction = {
  id: string
  label: string
  enabled: boolean
}

export type WorkspaceIntent = {
  action:
    | "select_workspace_kind"
    | "select_strategy"
    | "select_mix_mode"
    | "save_mix"
    | "save_and_move"
  payload: Record<string, unknown>
  nonce: string
}

export type StrategyCatalogItem = {
  strategy_choice: string
  maturity: "production" | "development"
  variants: string[]
  level2_handoff_supported: boolean
}

export type BacktestAnalysisWorkspace = {
  schema_version: string
  workspace_id: string
  workspace_kind: "single_strategy" | "portfolio_mix"
  configuration_fingerprint: string
  run_result_id?: string | null
  candidate_source_id?: string | null
  workspace_phase: "selecting" | "configuring" | "result" | "error"
  result_freshness: "none" | "current" | "stale"
  handoff_state: "ready" | "blocked"
  strategy_maturity: "production" | "development"
  header: { question: string }
  current_work: { title: string; workspace_kind: string }
  strategy_catalog: Array<{
    group_id: string
    label: string
    items: StrategyCatalogItem[]
  }>
  configuration_summary: Record<string, unknown>
  saved_mixes: Array<Record<string, unknown>>
  mix?: {
    role_weight_rows: Array<{
      strategy_name: string
      role: string
      role_label: string
      weight_percent: number
      valid: boolean
    }>
    total_weight_percent: number
    saved_entry_mode: "new" | "saved"
  }
  decision: {
    headline: string
    summary: string
    reasons: Array<{ root_issue_id: string; message: string }>
    metrics: Array<{ metric_id: string; label: string; value: unknown }>
    result_available: boolean
  }
  error?: { kind: string; message: string } | null
  actions: Record<string, WorkspaceAction>
  boundaries: Record<string, boolean>
}
