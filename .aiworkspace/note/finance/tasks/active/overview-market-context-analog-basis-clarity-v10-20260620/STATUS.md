# Status

Status: Complete

## Progress

- 2026-06-20: User approved implementation after guideline review.
- 2026-06-20: Started V10 task record for historical analog basis clarity and Macro comparison UX.
- 2026-06-20: Added service contract fields for requested / effective analog as-of alignment, basis warnings, limiting symbols, and symbol latest-date map.
- 2026-06-20: Updated Historical Analog UI to show selected date vs actual calculation date and redesigned Macro comparison funnel / condition group labels.
- 2026-06-20: Browser QA confirmed latest, selected 2026-06-18, 20D, and monthly paths.

## Result

- `latest` now clearly means the latest usable common DB price basis for the analog calculation.
- If selected date is later than usable common price coverage, the UI shows `선택 기준일과 실제 계산일이 다릅니다`, requested date, actual calculation date, limiting symbols, and the data-bound reason.
- Macro comparison now reads as broad sample -> GLD backdrop -> rate-pressure futures backdrop, with condition groups renamed in user language.

## Next

- Full PIT sector universe / historical sector membership remains a separate storage/read-path decision.
