# Notes

- Existing saved file `.aiworkspace/note/finance/saved/SELECTED_DASHBOARD_PORTFOLIOS.jsonl` is dirty in the worktree and must be preserved. Do not stage it unless explicitly requested.
- Current saved rows have `selected_decision_ids` only. New code must read them as default slots.
- Final Review selected rows include component `selection_history`, so current target assets and last rebalance can be shown without new DB writes.
- Next rebalance target cannot be known before the future rebalance date is run; show current target carry-forward and mark next target as recomputed at next rebalance.
- Runtime state now stores `strategy_slots` with selected decision id, start, latest-end mode, end, initial capital, and memo. It still writes `selected_decision_ids` for compatibility and derives effective slots for legacy rows.
- The dashboard portfolio is a user monitoring container, not a strategy definition or approval record. Final Review rows remain read-only source-of-truth.
- `전략 적용` only saves slot setup; `모니터 시나리오 실행` separately runs the selected component recheck in session state.
- Evidence hierarchy is now scenario-first: portfolio value / P&L / return / CAGR / MDD / benchmark spread / rebalance target appears before readiness / provider / preflight / audit detail.
- Streamlit renders all tab contents, so repeated disabled controls inside per-strategy tabs need explicit decision-scoped keys even when disabled.
