# Overview Macro Context Cockpit V1 Risks

## Closed / Controlled Risks

- Existing Overview file is large; keep changes small and avoid broad refactor.
- Snapshot schemas are dict / DataFrame oriented; tests should lock only the new cockpit contract and avoid overfitting UI details.
- Browser QA used local DB state and verified layout plus explicit stale / review states rather than pretending data is fresh.

## Remaining Follow-Up

- Cockpit V1 points to `Data Health`, but it does not yet provide a priority-ranked Ingestion action queue. That remains 2차.
- Breadth summary is a compact top-sector read, not a full heatmap or market breadth dashboard. That remains 3차.
