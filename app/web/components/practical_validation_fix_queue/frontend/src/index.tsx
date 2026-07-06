import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { PracticalValidationFixQueue } from "./PracticalValidationFixQueue"
import "./style.css"

type Tone = "positive" | "warning" | "danger" | "neutral"

type FixItem = {
  label?: string
  status?: string
  statusLabel?: string
  displayLabel?: string
  issueTitle?: string
  currentProblem?: string
  completionCriteria?: string
  impactSummary?: string
  checkedEvidence?: string
  missingEvidence?: string
  actionLabel?: string
  whyItMatters?: string
  technicalLabel?: string
  fixLocation?: string
  fixAction?: string
  gateReason?: string
  tone?: Tone
}

type CoreGroup = {
  label?: string
  status?: string
  purpose?: string
  tone?: Tone
  modules?: string[]
}

type CriteriaCard = {
  label?: string
  displayLabel?: string
  issueTitle?: string
  status?: string
  statusLabel?: string
  technicalLabel?: string
  tone?: Tone
  explanation?: string
  evidence?: string
  currentProblem?: string
  completionCriteria?: string
  fixLocation?: string
  impactSummary?: string
  checkedEvidence?: string
  missingEvidence?: string
  actionLabel?: string
  whyItMatters?: string
  resolutionSurface?: string
}

type CriteriaGroup = {
  label?: string
  displayLabel?: string
  status?: string
  purpose?: string
  passedCriteria?: string[]
  remainingIssues?: string[]
  reviewCriteria?: string[]
  decisionSummary?: string
  tone?: Tone
  criteriaCards?: CriteriaCard[]
}

type StreamlitArgs = {
  statusLabel?: string
  tone?: Tone
  verdict?: string
  nextAction?: string
  canSaveAndMove?: boolean
  fixItems?: FixItem[]
  coreGroups?: CoreGroup[]
  criteriaGroups?: CriteriaGroup[]
  reviewCount?: number
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return (
    <PracticalValidationFixQueue
      statusLabel={args?.statusLabel ?? "-"}
      tone={args?.tone ?? "neutral"}
      verdict={args?.verdict ?? "-"}
      nextAction={args?.nextAction ?? ""}
      canSaveAndMove={Boolean(args?.canSaveAndMove)}
      fixItems={Array.isArray(args?.fixItems) ? args.fixItems : []}
      coreGroups={Array.isArray(args?.coreGroups) ? args.coreGroups : []}
      criteriaGroups={Array.isArray(args?.criteriaGroups) ? args.criteriaGroups : []}
      reviewCount={Number(args?.reviewCount ?? 0)}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
