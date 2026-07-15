import React from "react";
import { createRoot } from "react-dom/client";
import InstitutionalPortfoliosWorkbench from "./InstitutionalPortfoliosWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <InstitutionalPortfoliosWorkbench />
  </React.StrictMode>,
);
