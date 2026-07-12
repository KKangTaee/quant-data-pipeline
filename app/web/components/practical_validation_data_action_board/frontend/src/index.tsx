import React from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import { DataActionBoard, PracticalValidationDataActionBoard } from "./PracticalValidationDataActionBoard"
import "./style.css"

type StreamlitArgs = {
  board?: Record<string, unknown>
}

type AppProps = {
  args: StreamlitArgs
}

function App({ args }: AppProps) {
  return <PracticalValidationDataActionBoard board={(args?.board ?? {}) as DataActionBoard} />
}

const ConnectedApp = withStreamlitConnection(App)
const root = createRoot(document.getElementById("root") as HTMLElement)
root.render(<ConnectedApp />)
Streamlit.setFrameHeight()
