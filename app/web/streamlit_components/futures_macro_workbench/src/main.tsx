import React from "react";
import { createRoot } from "react-dom/client";
import FuturesMacroWorkbench from "./FuturesMacroWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <FuturesMacroWorkbench />
  </React.StrictMode>,
);
