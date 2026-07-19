import React, { useEffect } from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { BacktestAnalysisResultWorkspace } from "./BacktestAnalysisResultWorkspace"
import { ResultWorkspace } from "./types"
import "./style.css"

type StreamlitArgs = {
  workspace?: ResultWorkspace
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
    <BacktestAnalysisResultWorkspace workspace={args.workspace} />
  ) : (
    <div className="bt1r-empty">결과 workspace payload를 읽을 수 없습니다.</div>
  )
}

const Component = withStreamlitConnection(App)
createRoot(document.getElementById("root") as HTMLElement).render(<Component />)
