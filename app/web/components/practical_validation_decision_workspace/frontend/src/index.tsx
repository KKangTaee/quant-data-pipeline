import React, { useEffect } from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { PracticalValidationDecisionWorkspace } from "./PracticalValidationDecisionWorkspace"
import { DecisionWorkspace } from "./types"
import "./style.css"

type StreamlitArgs = {
  workspace?: DecisionWorkspace
  surface: "context" | "decision"
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  useEffect(() => {
    Streamlit.setFrameHeight()
  }, [args])
  if (!args.workspace) {
    return (
      <div className="pv2-empty">
        Practical Validation workspace payload를 읽을 수 없습니다.
      </div>
    )
  }
  return (
    <PracticalValidationDecisionWorkspace
      workspace={args.workspace}
      surface={args.surface ?? "decision"}
    />
  )
}

const Component = withStreamlitConnection(App)
createRoot(document.getElementById("root") as HTMLElement).render(<Component />)
Streamlit.setFrameHeight()
