# Overview Market Context Events Data Trust V1 Notes

## Intake Notes

- Worktree: `/Users/taeho/Project/quant-data-pipeline-worktrees/sub-dev`.
- Branch requested: `sub-dev`.
- Pre-existing dirty/generated files include `finance/.DS_Store` and many old `*-qa.png`; do not stage them.
- 1차 Market Context brief flow and 2차 refresh reflect work intentionally deferred CPI/Event coverage, Macro Calendar collection/ICS fallback verification, and Data Health exposure review.

## Discoveries

- Local DB coverage on 2026-06-12:
  - `2026-06-01` to `2026-07-31`, all event types: 46 rows before implementation probe, with 42 earnings, 2 FOMC, 2 GDP.
  - `MACRO_CPI` on `2026-06-10`: 0 rows.
  - `MACRO_CPI` on `2026-07-14`: 0 rows.
  - After read-model change, all-events default snapshot scans `2026-06-05` to `2026-08-11` and returns 61 rows: 4 official macro/FOMC rows and 57 provider-estimated earnings rows.
  - `build_market_events_snapshot(event_type="MACRO_CPI")` still returns `NO_EVENTS` because stored CPI rows are absent, not because the read model filters them out.
- Root cause:
  - The previous default event snapshot started at `today`, so just-past major releases could not appear.
  - `build_overview_macro_week_lane()` only considered rows with `Days Until >= 0`, so recent CPI would be omitted even if stored.
  - Event rows were date-sorted, allowing many earnings rows to compete with CPI/FOMC/GDP in context surfaces.
- Parser state:
  - Existing BLS HTML and ICS fixture paths already parsed full `Consumer Price Index`, `Producer Price Index`, and `Employment Situation` names.
  - This task added abbreviated `CPI` / `PPI` title coverage so fallback imports tolerate compact official titles.

## Decisions

- Keep event information context-only. It does not create trading signals, validation PASS/BLOCKER rows, Final Review decisions, or monitoring signals.
- Keep Market Context event output compact; full tables and collection status belong to Events/Data Health.
- Do not add a provider or schema. Missing CPI rows should be solved by existing Macro Calendar collection or BLS `.ics` import, then the read model will surface them.
