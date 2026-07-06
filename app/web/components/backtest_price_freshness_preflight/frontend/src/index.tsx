import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestPriceFreshnessPreflight } from "./BacktestPriceFreshnessPreflight"
import "./style.css"

type Tone = "positive" | "warning" | "danger" | "neutral"

type StreamlitArgs = {
  statusLabel?: string
  tone?: Tone
  headline?: string
  summary?: string
  detail?: string
  metricItems?: Array<{
    label?: string
    value?: string
    detail?: string
  }>
  issueRows?: Array<{
    label?: string
    value?: string
    detail?: string
    tone?: Tone
  }>
  nextAction?: string
  footnote?: string
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return (
    <BacktestPriceFreshnessPreflight
      statusLabel={args?.statusLabel ?? "-"}
      tone={args?.tone ?? "neutral"}
      headline={args?.headline ?? "-"}
      summary={args?.summary ?? ""}
      detail={args?.detail ?? ""}
      metricItems={Array.isArray(args?.metricItems) ? args.metricItems : []}
      issueRows={Array.isArray(args?.issueRows) ? args.issueRows : []}
      nextAction={args?.nextAction ?? ""}
      footnote={args?.footnote ?? ""}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
