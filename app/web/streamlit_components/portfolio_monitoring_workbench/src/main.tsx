import React from "react";
import { createRoot } from "react-dom/client";
import PortfolioMonitoringWorkbench from "./PortfolioMonitoringWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <PortfolioMonitoringWorkbench />
  </React.StrictMode>,
);
