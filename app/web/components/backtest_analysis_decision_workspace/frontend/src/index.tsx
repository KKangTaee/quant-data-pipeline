import React, { useEffect } from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestAnalysisDecisionWorkspace } from "./BacktestAnalysisDecisionWorkspace"
import {
  BacktestAnalysisWorkspace,
  SingleSettingsWorkspace,
  WorkspaceSurface,
} from "./types"
import "./style.css"

type StreamlitArgs = {
  workspace?: BacktestAnalysisWorkspace | SingleSettingsWorkspace
  surface: WorkspaceSurface
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  useEffect(() => {
    const resize = () => Streamlit.setFrameHeight()
    const observer = new ResizeObserver(resize)
    observer.observe(document.documentElement)
    resize()
    return () => observer.disconnect()
  }, [args])

  return args.workspace ? (
    <BacktestAnalysisDecisionWorkspace
      workspace={args.workspace}
      surface={args.surface ?? "decision"}
    />
  ) : (
    <div className="bt1-empty">
      Backtest Analysis workspace payload를 읽을 수 없습니다.
    </div>
  )
}

const Component = withStreamlitConnection(App)
createRoot(document.getElementById("root") as HTMLElement).render(<Component />)
