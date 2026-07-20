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
- Inner candidate comparison requires shared chronological evaluation coverage. A hybrid with only a short recent macro history cannot beat M1 by being scored on fewer/easier dates.
- B0/B1 can win inner selection. In that case `selected_candidate` remains `None`, the raw `selected_configuration` records the baseline, and sufficient outer evidence resolves to `NO_EDGE` rather than inventing a model edge.
- Missing cycle/event tables degrade M2 to unavailable context while preserving the DB-only M1 path; provider fetching was not added to the UI or model service.
- Snapshot compatibility is now based on the completed-input fingerprint, not the raw maximum provider marker. A pending provider row can move the raw marker without invalidating or replacing the latest-good final snapshot.
- Immutable history and current are written in one transaction. `materialized_at` does not participate in identity, so retries remain idempotent.
- The Python bridge is the publication enforcement boundary: provisional numbers remain available only under `disclosure_probabilities`, while `NO_EDGE` carries no conditional numeric distribution or geometry to the React first surface.
- Fixed semantic axes make adjacent snapshots visually comparable. Outliers no longer rescale the entire map; their boundary marker and raw tooltip preserve the evidence.
- The observed trail and terminal distribution are different primitives: the former is an actual dated sequence, while the latter is a joint future-state region with no implied day-by-day route.
- Actual production-like evidence confirms the design is not forcing the requested shape: M1 can be the 5D inner candidate while all outer publication gates still resolve to `NO_EDGE`.
- A raw latest date and a final prediction basis are different fields. On 2026-07-20 the raw marker moved, but the canonical current remained 2026-07-17 until cutoff; the UI now states this explicitly.
- Legacy current rows may carry an as-of date derived from incomplete input. Only the one-time `session_status=LEGACY` transition may replace that row with an older completed-session V2 basis; subsequent V2 current rows retain the non-older rule.
