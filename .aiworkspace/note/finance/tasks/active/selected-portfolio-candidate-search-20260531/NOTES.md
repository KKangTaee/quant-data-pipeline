# Notes

- User requested actual candidate discovery using existing DB, saved portfolio, and registry.
- Live approval, orders, auto rebalance, broker/account integration are explicitly out of scope.
- Existing worktree had unrelated modified / untracked generated artifacts before this task; do not revert or stage them.

## Result

- Final Review에 최종 선정 저장된 후보: 없음.
- Selected Portfolio Dashboard에 노출되는 후보: 없음.
- 사유: Practical Validation 또는 Final Review evidence route는 일부 후보에서 `READY_FOR_FINAL_DECISION`까지 도달했지만, Final Review selected-route gate가 요구하는 investability packet `select_allowed=True`를 만족한 후보가 없었다.

## Candidate Review

| Candidate | Source | Composition | Backtest / Replay | Practical Validation | Final Review selected-route result |
|---|---|---|---|---|---|
| GTAA Clean-6 AOR Top-2 1M/12M interval-2 MA150 | `PRACTICAL_VALIDATION_RESULTS` latest row | GTAA single component, 100% | saved validation score 8.6 | `READY_FOR_FINAL_REVIEW`; Final Review eligible | Blocked. `Risk Contribution` hard blocker and review-required groups remain: Backtest Realism, Component Role / Weight, Construction Risk, Data Coverage, Data Trust, Stress / Robustness, Validation Efficacy. |
| EW Growth/Commodity 30 + GTAA Clean-6 70 | `SAVED_PORTFOLIOS` | Equal Weight Growth/Commodity 4 30% + GTAA Clean-6 70% | replay CAGR 16.50%, MDD -10.26%, Sharpe 2.14; actual replay CAGR 15.71%, MDD -12.64%, Sharpe 1.91 | dry-run profiles all `READY_FOR_FINAL_REVIEW`; actual replay `PASS`, period coverage `PASS` | Blocked. `Backtest Realism` and `Component Role / Weight` hard blockers; construction, data coverage, provider, risk contribution, stress, validation efficacy still review-required. Strongest candidate to repair next because runtime replay and period coverage passed. |
| GTAA SPY Low-MDD 60 + EW Growth/Sector/Gold 40 | `SAVED_PORTFOLIOS` | GTAA SPY Low-MDD 60% + Equal Weight Growth/Sector/Gold 40% | replay CAGR 18.52%, MDD -10.04%, Sharpe 2.54; actual replay CAGR 17.50%, MDD -13.58%, Sharpe 2.61 | dry-run profiles `READY_FOR_FINAL_REVIEW`; actual replay `REVIEW`, period coverage `REVIEW` because aligned portfolio ended 2026-02-28 | Blocked. `Backtest Realism` and `Component Role / Weight` hard blockers; growth profile also blocks on validation efficacy due period coverage/runtime replay review. |
| Legacy current candidates / proposals | `CURRENT_CANDIDATE_REGISTRY`, `PORTFOLIO_PROPOSAL_REGISTRY` | 8 current candidates + 4 proposals | read-model evaluation only | not saved as new Practical Validation result | Blocked. None passed selected-route gate; repeated blockers include Risk Contribution, Backtest Realism, Construction Risk, Data Coverage, Provider / Look-through, Validation Efficacy. |

## Observations

- `FINAL_PORTFOLIO_SELECTION_DECISIONS.jsonl` has legacy selected rows, but the current Selected Portfolio Dashboard reads V2 only through `FINAL_PORTFOLIO_SELECTION_DECISIONS_V2.jsonl`.
- The saved mix prefill carries a `weight_reason`, but the Clean V2 saved-mix source conversion does not currently preserve that field into component metadata. This contributes to `Component Role / Weight` gate failures and should be treated as an evidence mapping gap, not manually overridden during candidate selection.
- Backtest realism blockers require compact net-cost / turnover / cost sensitivity / liquidity evidence at the source or mix level. Component contracts include some cost assumptions, but the current selected-route packet does not see enough aggregate evidence to allow selection.
