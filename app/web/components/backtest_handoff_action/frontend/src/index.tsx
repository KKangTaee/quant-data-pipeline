import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestHandoffAction } from "./BacktestHandoffAction"
import "./style.css"

type StreamlitArgs = {
  statusLabel?: string
  tone?: "positive" | "warning" | "danger" | "neutral"
  summary?: string
  reasonTitle?: string
  reasons?: string[]
  entryCards?: Array<{
    label?: string
    value?: string
    detail?: string
    tone?: "positive" | "warning" | "danger" | "neutral"
  }>
  actionText?: string
  buttonLabel?: string
  disabled?: boolean
  reviewCount?: number
  blockerCount?: number
  boundaryText?: string
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return (
    <BacktestHandoffAction
      statusLabel={args?.statusLabel ?? "-"}
      tone={args?.tone ?? "neutral"}
      summary={args?.summary ?? "-"}
      reasonTitle={args?.reasonTitle ?? "상태"}
      reasons={Array.isArray(args?.reasons) ? args.reasons : []}
      entryCards={Array.isArray(args?.entryCards) ? args.entryCards : []}
      actionText={args?.actionText ?? "-"}
      buttonLabel={args?.buttonLabel ?? "Submit"}
      disabled={Boolean(args?.disabled)}
      reviewCount={Number(args?.reviewCount ?? 0)}
      blockerCount={Number(args?.blockerCount ?? 0)}
      boundaryText={args?.boundaryText ?? ""}
    />
  )
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
