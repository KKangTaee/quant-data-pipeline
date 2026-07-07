import React from "react";
import { createRoot } from "react-dom/client";
import EventsWorkbench from "./EventsWorkbench";

createRoot(document.getElementById("root") as HTMLElement).render(
  <React.StrictMode>
    <EventsWorkbench />
  </React.StrictMode>,
);
