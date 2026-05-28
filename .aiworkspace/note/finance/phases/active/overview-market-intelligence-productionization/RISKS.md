# Overview Market Intelligence Productionization Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Earnings source remains unofficial | High | Keep source confidence visible, add official-source validation where practical, avoid overclaiming. |
| Full universe earnings scan is slow or rate-limited | High | Use bounded batches, low-frequency collection, cooldown, and progress display. |
| Event date changes create duplicate-looking rows | Medium | Add lifecycle interpretation and cleanup before broader collection. |
| UI becomes noisy | Medium | Keep operational density, use filters and diagnostics expanders. |
| Scope expands into recommendation engine | Medium | Keep market intelligence as context, not automatic candidate promotion. |
| Schema churn before behavior is clear | Medium | Start with read-model lifecycle interpretation; add columns only when persistence is needed. |
