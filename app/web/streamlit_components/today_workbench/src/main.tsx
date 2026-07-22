import React from "react";
import { createRoot } from "react-dom/client";

import TodayWorkbench from "./TodayWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <TodayWorkbench />
  </React.StrictMode>,
);
