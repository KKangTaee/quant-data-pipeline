import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { FinalReviewInvestmentReport, InvestmentReport } from "./FinalReviewInvestmentReport"
import "./style.css"

type StreamlitArgs = {
  report?: Record<string, unknown>
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return <FinalReviewInvestmentReport report={(args?.report ?? {}) as InvestmentReport} />
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
