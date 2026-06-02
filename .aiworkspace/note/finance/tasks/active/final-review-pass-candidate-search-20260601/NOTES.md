# Notes

- Existing dirty generated/local files predate this task and must not be staged.
- Final Review selected-route ready is not live approval or broker/order readiness.
- `GRS Liquid Macro Top2` is the strongest current pass among the sweep because it has materially higher CAGR / Sharpe than GTAA while keeping MDD slightly better.
- Both GRS and GTAA still carry open review items such as cost / slippage sensitivity, liquidity / operability evidence, tax / account scope, and concentration-related WATCH rows. These are selected-route open reviews, not selected-route blockers under the current Final Review policy.
- Equal Weight's higher raw performance is not enough because the source still lacks measurable turnover / net cost proof and promotion net policy metadata; this remains the intended regression blocker.
- For the lower-MDD request, `GRS Macro Top1 MA200` is the cleanest "higher CAGR with lower MDD" candidate. It keeps the same liquid macro universe as the previous GRS Top2 candidate but selects only one asset each rebalance.
- If top=1 concentration is too aggressive, `GRS QQQ Gold Bonds Top2 MA150` is the lower-drawdown alternative: CAGR remains high at `12.94%`, MDD improves to `-8.81%`, Sharpe is `1.31`, and selected-route gate is ready.
- Final Decision V2 persistence was intentionally limited to fresh selected-route pass candidates. `GTAA Default Top3` was excluded after the fresh save run because its current Practical Validation / investability packet blocked selection.
- The dashboard saved portfolio is read-only monitoring state. It assigns the 4 selected decision rows to a user-visible portfolio but does not create live approval, orders, broker/account linkage, monitoring-log auto writes, or auto rebalance.
