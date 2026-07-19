import React, { useEffect } from "react";
import { createRoot } from "react-dom/client";
import { ComponentProps, Streamlit, withStreamlitConnection } from "streamlit-component-lib";
import type { PortfolioMonitoringWorkspace } from "./contracts";

function PortfolioMonitoringSkeleton({ args }: ComponentProps) {
  const workspace = (args?.payload ?? null) as PortfolioMonitoringWorkspace | null;

  useEffect(() => {
    Streamlit.setFrameHeight();
  }, [workspace]);

  return (
    <main aria-label="Portfolio Monitoring">
      <span>{workspace?.schema_version ?? "portfolio_monitoring_workspace_v1"}</span>
    </main>
  );
}

const ConnectedPortfolioMonitoringSkeleton = withStreamlitConnection(PortfolioMonitoringSkeleton);

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ConnectedPortfolioMonitoringSkeleton />
  </React.StrictMode>,
);
