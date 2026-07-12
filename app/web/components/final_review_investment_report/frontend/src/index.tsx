import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import {
  FinalDecisionActionModel,
  FinalReviewInvestmentReport,
  InvestmentReport,
} from "./FinalReviewInvestmentReport"
import "./style.css"

type StreamlitArgs = {
  report?: Record<string, unknown>
  decision_action?: Record<string, unknown>
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return (
    <FinalReviewInvestmentReport
      decisionAction={(args?.decision_action ?? {}) as FinalDecisionActionModel}
      report={(args?.report ?? {}) as InvestmentReport}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
