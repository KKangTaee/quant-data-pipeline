export type WorkflowStage = {
  stage_key: string
  level_label: string
  title: string
  english_title: string
  responsibility: string
  is_active: boolean
}

export type WorkflowShell = {
  schema_version: string
  headline: string
  description: string
  active_stage: string
  active_stage_index: number
  active_stage_context: WorkflowStage
  stages: WorkflowStage[]
}
