# Risks

## 2026-05-31

- A stronger visual action panel must not imply live approval or order execution.
- If too much content is duplicated in cards and tables, the page may become longer without becoming clearer.
- Browser QA may reflect local empty / partial registry state; screenshots validate layout and no UI break, not investment correctness.
- Browser QA passed on desktop viewport for the new command center / lane cards / Decision Cockpit hierarchy.
- This pass intentionally does not redesign the deep Evidence Appendix tables. They remain in the older compact badge / dataframe style because they are secondary traceability surfaces.
- Mobile QA was not part of this pass. The CSS uses responsive grid collapse, but mobile-specific polish should be handled in a follow-up if needed.
- Existing Backtest code still contains broad `use_container_width` deprecation warnings. This task did not add new occurrences.
- Candidate-switching state leakage for `Source` / `Decision ID` was fixed by source-scoped widget keys. Browser QA only had one eligible candidate available locally, so the multi-candidate switch itself remains covered by code inspection rather than an interactive fixture.
- Official save is now selection-only. Existing historical non-select decision rows remain readable for compatibility, but the current UI no longer creates new hold / reject / re-review rows.
