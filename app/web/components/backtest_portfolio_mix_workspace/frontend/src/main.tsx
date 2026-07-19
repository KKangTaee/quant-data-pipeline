import React, { useEffect } from "react"
import { createRoot } from "react-dom/client"
import { Streamlit, withStreamlitConnection } from "streamlit-component-lib"
import App, { PortfolioMixWorkspace } from "./App"
import "./styles.css"

function ConnectedApp({ args }: { args: { workspace?: PortfolioMixWorkspace } }) {
  useEffect(() => {
    const resize = () => Streamlit.setFrameHeight()
    const observer = new ResizeObserver(resize)
    observer.observe(document.documentElement)
    resize()
    return () => observer.disconnect()
  }, [args])

  return args.workspace ? <App workspace={args.workspace} /> : null
}

const Component = withStreamlitConnection(ConnectedApp)
createRoot(document.getElementById("root") as HTMLElement).render(<Component />)
