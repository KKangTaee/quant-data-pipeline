import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestFactorReadinessPanel } from "./BacktestFactorReadinessPanel"
import "./style.css"

type Tone = "positive" | "warning" | "danger" | "neutral"

type ReadinessItem = {
  label?: string
  value?: string
  detail?: string
  tone?: Tone
}

type ReadinessCheck = {
  id?: string
  title?: string
  status?: string
  tone?: Tone
  summary?: string
  detail?: string
  metrics?: ReadinessItem[]
  issues?: ReadinessItem[]
}

type ReadinessAction = {
  label?: string
  detail?: string
  tone?: Tone
}

type StreamlitArgs = {
  status?: string
  tone?: Tone
  headline?: string
  summary?: string
  strategyLabel?: string
  runRecommended?: boolean
  checks?: ReadinessCheck[]
  actions?: ReadinessAction[]
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return (
    <BacktestFactorReadinessPanel
      status={args?.status ?? "-"}
      tone={args?.tone ?? "neutral"}
      headline={args?.headline ?? "-"}
      summary={args?.summary ?? ""}
      strategyLabel={args?.strategyLabel ?? ""}
      runRecommended={Boolean(args?.runRecommended)}
      checks={Array.isArray(args?.checks) ? args.checks : []}
      actions={Array.isArray(args?.actions) ? args.actions : []}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()

