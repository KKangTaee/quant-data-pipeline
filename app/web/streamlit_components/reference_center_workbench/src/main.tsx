import React from "react";
import { createRoot } from "react-dom/client";
import ReferenceCenterWorkbench from "./ReferenceCenterWorkbench";


createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <ReferenceCenterWorkbench />
  </React.StrictMode>,
);
