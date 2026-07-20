# Risks

- `known_at` proves when this application observed a value, not the provider's exact publication time.
- The first new capture can include old rolling-window observations; they are not PIT-available before that capture timestamp.
- Storing only changed rows would make replay more complex and lose positive evidence that a source response was observed unchanged; this design stores each normalized source view.
- Multiple manual refreshes can add repeated views. Expected volume is modest, but indexes and query plans must be verified.
- Source transaction code must not leave immutable history and canonical latest history out of sync.
- CNN component history cannot be backfilled from the current public response and must remain labeled as prospective capture-only.
- Loading full canonical history for charts must not change the 180-day range-context interpretation.
- A 24-hour automation cadence does not by itself prove an exact after-close execution time; actual UTC `observed_at` is authoritative.
- PIT history will initially be too short for credible 1W·1M validation. The UI must not convert early accumulation into unsupported probabilities.
- First live capture is complete, but each source still has only one chronological capture. This risk is active, so 1W·1M remain `UNAVAILABLE`.
- The 24-hour automation cadence is a collection interval, not a guaranteed after-close wall-clock schedule. For consistent daily interpretation, operate it after the US close when practical and use stored UTC `known_at` as authority.
- Legacy canonical history remains useful for descriptive charts but must never be treated as reconstructed publication-time history in the 4차 validation dataset.
- AAII workbook backfill is canonical descriptive history only. Its `1987-07-24` start must not be interpreted as application-known PIT history; immutable AAII truth still begins at `2026-07-20 09:17:45 UTC`.
- The official workbook uses a split `Reported` / `Date` header that pandas exposes as `Date`; parser tests cover both `Reported Date` and `Date` aliases.
- Latest desktop/420 interaction, hover, overflow, tab, and console QA remains a manual verification gap because Browser Use URL policy blocked localhost DOM access after the build.
