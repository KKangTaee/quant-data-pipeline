# Risks

- A stronger visual action panel must not imply live approval or order execution.
- If too much content is duplicated in cards and tables, the page may become longer without becoming clearer.
- Browser QA may reflect local empty / partial registry state; screenshots validate layout and no UI break, not investment correctness.
# Risks

## 2026-05-31

- Browser QA passed on desktop viewport for the new command center / lane cards / Decision Cockpit hierarchy.
- This pass intentionally does not redesign the deep Evidence Appendix tables. They remain in the older compact badge / dataframe style because they are secondary traceability surfaces.
- Mobile QA was not part of this pass. The CSS uses responsive grid collapse, but mobile-specific polish should be handled in a follow-up if needed.
- Existing Backtest code still contains broad `use_container_width` deprecation warnings. This task did not add new occurrences.
