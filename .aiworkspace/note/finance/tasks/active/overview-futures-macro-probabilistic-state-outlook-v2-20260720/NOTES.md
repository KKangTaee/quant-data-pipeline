# Overview Futures Macro Probabilistic State Outlook V2 Notes

## Confirmed Decisions

- The product goal is a conditional future-state distribution, not a forced forecast line.
- Observed and predicted coordinates must use the same state function.
- Momentum-only remains a mandatory benchmark.
- Macro/event context is adopted only if it adds rolling-origin out-of-sample value.
- 5D and 20D may choose different candidates.
- `NO_EDGE` is a successful evaluated output.
- Current path/probability/coordinate statuses remain separate.
- Initial event context uses stored official schedules; consensus surprise direction is out of scope without a PIT source.

## Root-Cause Evidence

- Screenshot viewed on 2026-07-19 used an as-of 2026-07-17 stored snapshot.
- Current snapshot is as-of 2026-07-20 and was materialized at 2026-07-20 21:08:13 Asia/Seoul.
- New 2026-07-19 / 2026-07-20 session rows shifted every positional anchor by two rows.
- Rebuilding through the old cutoff reproduced the first screenshot coordinates.
- Appending future rows did not change the four checked historical 5D family features.
- The active forecast endpoint adds a historical forward cumulative-return delta to the current 5D state; it is not `S(t+h)`.

## Research Interpretation

- Cross-asset futures momentum already carries market-implied macro repricing.
- Direct macro data is most useful as a persistence/reversal context and event-risk condition.
- Slow macro levels should not dominate a 5D model.
- For 5D, price state, volatility, breadth, and event schedule are primary.
- For 20D, growth/inflation/policy/financial-condition context may have greater incremental value.
- Macro level and surprise are different. The repository has official event schedules but not a complete PIT consensus-surprise ledger.

## Design Boundary

- Do not implement a run/row/status diagnostics panel as the improvement.
- Do not change the Economic Cycle publication model.
- Do not show a hybrid adjustment just because macro data is available.
- Do not tune thresholds after reading the final actual outcome without recording a new candidate trial/version.
- Canonical observed trail defaults to 30 completed sessions while the separate regime ribbon retains up to 60 sessions.
- V1 compatibility helpers now derive coordinate paths and terminal regimes from same-state transitions; forward cumulative return z is no longer the visible terminal-state target.
