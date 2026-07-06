import React from "react"
import { createRoot } from "react-dom/client"
import { withStreamlitConnection } from "streamlit-component-lib"
import { BacktestStrategyDetailPanel } from "./BacktestStrategyDetailPanel"
import "./style.css"

const ConnectedComponent = withStreamlitConnection(BacktestStrategyDetailPanel)

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ConnectedComponent />
  </React.StrictMode>,
)

