import React from "react";
import { createRoot } from "react-dom/client";
import SentimentWorkbench from "./SentimentWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <SentimentWorkbench />
  </React.StrictMode>,
);
