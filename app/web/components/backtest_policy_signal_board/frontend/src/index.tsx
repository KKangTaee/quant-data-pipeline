import React from "react"
import { createRoot } from "react-dom/client"
import { withStreamlitConnection } from "streamlit-component-lib"
import { BacktestPolicySignalBoard } from "./BacktestPolicySignalBoard"
import "./style.css"

const ConnectedComponent = withStreamlitConnection(BacktestPolicySignalBoard)

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ConnectedComponent />
  </React.StrictMode>,
)
