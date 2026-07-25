# Overview Futures Macro Short-Horizon V1 Notes

Last Updated: 2026-07-24

## Confirmed Facts

- Original core futures preset had 16 symbols. `DX-Y.NYB` was later added for Economic Cycle, so current collection has 17.
- Current actual snapshot as of 2026-07-22 reports `standardized_count=17`, `symbol_count=17`, and pattern `available_family_count=6/6`.
- `SCORE_DEFINITIONS` direct member union has 15 symbols. `SI=F` and `DX-Y.NYB` are not family score inputs.
- Current 5D status is `NO_EDGE`: model Brier `0.5582115` versus best unconditional baseline `0.5566554`; coordinate median error `0.7602570` versus baseline `0.7441459`.
- Current actual family state contains a useful contradiction: risk-on 5D is negative and safe-haven 5D is also negative, so a simple defensive headline is incomplete.
- Repeated 1Y provider collection changed exactly 17 rows: one `2026-07-22` same-date row per symbol. Completed historical rows did not change.
- At 2026-07-23 09:56 KST / 2026-07-22 20:56 ET, those rows continued changing close/high/low/volume after the configured final cutoff. The old resolver therefore fingerprinted an in-progress provider bar as final.
- Nested outlook profiling showed the genuine changed-input path is model-bound: `_build_nested_horizon_outlook` and repeated analog configuration forecasts dominate, not the 1Y download or DB UPSERT.
- A 2026-07-24 live probe found 17/17 core symbols and 276 stored 5m bars per symbol inside the target 2026-07-23 session window; next-session bars starting 22:00 UTC were also present but excluded by the half-open end.
- The live final source reference is exactly `yfinance:5m:[2026-07-22T18:00:00-04:00,2026-07-23T17:00:00-04:00)`.

## Decisions

- Keep the fast three-step decision flow.
- Show four core directions and two confirmation signals instead of six equal rows.
- Keep internal model/status names; improve user-facing explanation.
- Preserve 20D backend evidence but remove future 20D and 2D path from the default surface.
- Do not alter family membership in this task.
- Separate routine overlap refresh from full bootstrap and add an unchanged-input fast path.
- Treat a same-date row as final only when its collection timestamp falls in the 17:15–18:00 ET settlement-stable gap; otherwise keep it pending until the provider date advances.
- Bump the pattern algorithm identity because completed-session semantics changed, and allow incompatible stored current versions to replace a newer-date legacy semantic row.
- Keep mutable Yahoo raw 1d fields and explicit completed-session `final_*` fields on the same stable row. Routine 1d UPSERT updates only raw fields; completed resolver/model input uses valid `yfinance_5m_session_aggregate_v1` values first.
- Require all 17 core symbols before writing any final value. Missing coverage and transaction errors preserve the prior latest-good snapshot rather than advancing a partial market state.
- Treat the 5m aggregate as an operational completed-session value, not an exchange official settlement.

## Visual Approval

- Visual companion session: `.superpowers/brainstorm/53349-1784762573/`
- Final approved mockup: `content/futures-macro-core-confirmation-v4.html`
- Visual artifacts remain generated/untracked and are not part of the spec commit.
