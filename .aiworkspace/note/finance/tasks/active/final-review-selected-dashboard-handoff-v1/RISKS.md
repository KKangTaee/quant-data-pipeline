# Risks

- Local registries may be empty during Browser QA, so QA can only verify empty / no-selected handoff surfaces unless seeded test data is intentionally added. Generated screenshots are not staged.
- Handoff wording must not imply live approval, broker order, or auto rebalance.
- Handoff must not mutate Final Decision V2, selected monitoring log, registries, saved setup, or DB state.
