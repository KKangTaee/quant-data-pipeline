import React from "react";
import { createRoot } from "react-dom/client";
import MarketContextValuation from "./MarketContextValuation";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode><MarketContextValuation /></React.StrictMode>,
);
