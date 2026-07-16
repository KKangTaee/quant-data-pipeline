import React from "react";
import { createRoot } from "react-dom/client";
import EconomicCycleWorkbench from "./EconomicCycleWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <EconomicCycleWorkbench />
  </React.StrictMode>,
);
