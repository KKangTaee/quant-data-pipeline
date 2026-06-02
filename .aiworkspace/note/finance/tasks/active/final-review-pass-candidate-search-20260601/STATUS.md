# Status

- 2026-06-01: Started. Scope is dry-run candidate search in main-dev without registry/saved persistence.
- 2026-06-01: Dry-run sweep completed for GRS, GTAA, Risk Parity, Dual Momentum, and Equal Weight regression candidates.
- 2026-06-01: Passing Final Review selected-route candidates found: `GRS Liquid Macro Top2` and `GTAA Default Top3`.
- 2026-06-01: Best candidate by current sweep is `GRS Liquid Macro Top2`: CAGR `13.31%`, MDD `-17.75%`, Sharpe `1.12`, replay PASS, selected-route preflight ready, Final Review selected gate ready.
- 2026-06-01: Lower-MDD follow-up found `GRS Macro Top1 MA200`: CAGR `18.03%`, MDD `-12.43%`, Sharpe `1.18`, replay PASS, selected-route preflight ready, Final Review selected gate ready. Main tradeoff is top=1 concentration.
- 2026-06-01: User approved durable dashboard exposure for passed candidates. Appended 4 fresh-selected GRS candidates to `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl` and created dashboard saved portfolio `Final Review 통과 후보 2026-06-01` with all 4 selected decision ids.
- 2026-06-01: Fresh GTAA Default Top3 re-run was not saved because Practical Validation returned `BLOCKED` and selected-route gate was not ready under the unchanged Final Review policy.
