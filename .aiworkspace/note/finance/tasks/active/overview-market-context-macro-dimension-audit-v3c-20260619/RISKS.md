# Risks

Status: Complete
Last Updated: 2026-06-19

## Remaining Risks To Track

- Stored macro series coverage may be absent on another environment. The UI shows `UNAVAILABLE` or `AVAILABLE_REFERENCE` with preview count 0 without implying failure of the broad analog.
- Macro bucket preview can reduce anchor count conceptually, but this task must not apply those macro buckets as hard filters.
- Events and sentiment histories may be short or irregular. They should remain annotation / deferred context.
- Selected as-of replay still uses current universe / sector metadata plus DB prices through selected as-of, as documented in prior tasks.

## QA Risks To Check

- Browser QA confirmed `맥락 차원 상태` reads as product context, not a raw run/job diagnostics table.
- Browser QA confirmed used, reference, and deferred statuses were visible in latest, 20D, monthly, and selected-as-of mode.
- Browser QA checked the requested forbidden copy list; no forbidden prediction/recommendation/trade-signal wording was found in the checked body text.
