import React, { useEffect } from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { DecisionBriefWorkspace } from "./DecisionBriefWorkspace"
import {
  CandidateSelectorModel,
  DecisionBrief,
  DecisionWorkspaceIntent,
} from "./decisionBriefTypes"
import "./style.css"

type StreamlitArgs = {
  decision_brief?: Record<string, unknown>
  candidate_selector?: Record<string, unknown>
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [args])

  return (
    <DecisionBriefWorkspace
      candidateSelector={(args?.candidate_selector ?? { options: [] }) as CandidateSelectorModel}
      decisionBrief={(args?.decision_brief ?? {}) as DecisionBrief}
      onIntent={(intent: DecisionWorkspaceIntent) => Streamlit.setComponentValue(intent)}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
