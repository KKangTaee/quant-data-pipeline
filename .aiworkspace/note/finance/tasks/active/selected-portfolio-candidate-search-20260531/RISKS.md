# Risks

- Existing legacy selected decision registry has historical rows, but current Selected Portfolio Dashboard reads `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`; do not count legacy rows as dashboard-selected.
- Existing Practical Validation rows may be gate-passed for Final Review but still selected-route blocked by newer profile-aware policy.
- Browser QA can verify dashboard visibility after a selected V2 row exists; screenshots are generated artifacts and should not be committed unless explicitly requested.

## Closeout Risks

- The current dashboard source is V2, not the legacy final decision file. A candidate visible only in `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` is not considered dashboard-selected.
- No candidate should be manually appended until the selected-route gate reports `select_allowed=True`; otherwise the dashboard would display a row that the Final Review policy intentionally blocks.
- The most actionable next repair target is `EW Growth/Commodity 30 + GTAA Clean-6 70`, but it needs evidence work before selection: backtest realism packet, component role / weight rationale propagation, provider/look-through review, risk contribution/drop-one evidence, and stress/validation efficacy evidence.
