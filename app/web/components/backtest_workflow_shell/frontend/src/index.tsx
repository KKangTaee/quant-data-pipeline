import React, { useEffect } from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestWorkflowShell } from "./BacktestWorkflowShell"
import { WorkflowShell } from "./types"
import "./style.css"

type StreamlitArgs = {
  shell?: WorkflowShell
}

function App({ args }: { args: StreamlitArgs }) {
  useEffect(() => {
    const resize = () => Streamlit.setFrameHeight()
    const observer = new ResizeObserver(resize)
    observer.observe(document.documentElement)
    resize()
    return () => observer.disconnect()
  }, [args])

  return args.shell ? (
    <BacktestWorkflowShell shell={args.shell} />
  ) : (
    <div className="bt-workflow-empty">
      Backtest workflow 정보를 불러올 수 없습니다.
    </div>
  )
}

const Component = withStreamlitConnection(App)
createRoot(document.getElementById("root") as HTMLElement).render(<Component />)
