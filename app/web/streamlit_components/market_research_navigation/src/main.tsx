import React from "react";
import { createRoot } from "react-dom/client";
import MarketResearchNavigation from "./MarketResearchNavigation";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <MarketResearchNavigation />
  </React.StrictMode>,
);
