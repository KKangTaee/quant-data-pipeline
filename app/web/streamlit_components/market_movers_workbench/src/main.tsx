import React from "react";
import { createRoot } from "react-dom/client";
import MarketMoversWorkbench from "./MarketMoversWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <MarketMoversWorkbench />
  </React.StrictMode>,
);
