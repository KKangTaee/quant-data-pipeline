import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestPriceRefreshAction } from "./BacktestPriceRefreshAction"
import "./style.css"

type StreamlitArgs = {
  statusLabel?: string
  tone?: "positive" | "warning" | "danger" | "neutral"
  summary?: string
  detail?: string
  metricItems?: Array<{
    label?: string
    value?: string
    detail?: string
  }>
  actionText?: string
  buttonLabel?: string
  actionNote?: string
  disabled?: boolean
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return (
    <BacktestPriceRefreshAction
      statusLabel={args?.statusLabel ?? "-"}
      tone={args?.tone ?? "neutral"}
      summary={args?.summary ?? "-"}
      detail={args?.detail ?? ""}
      metricItems={Array.isArray(args?.metricItems) ? args.metricItems : []}
      actionText={args?.actionText ?? "-"}
      buttonLabel={args?.buttonLabel ?? "Submit"}
      actionNote={args?.actionNote ?? ""}
      disabled={Boolean(args?.disabled)}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
