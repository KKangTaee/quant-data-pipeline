# Risks

Status: Complete
Last Updated: 2026-06-18

## Open Risks

- Existing local generated/user files must remain unstaged: `finance/.DS_Store`, `.superpowers/`, `overview-market-context-next-checks-qa.png`.
- Full PIT sector leadership replay is not available from the existing DB/read path. The current implementation uses current universe / sector metadata with selected-as-of DB prices.
- For very early selected 기준일, analog can return 자료 부족 because enough history or forwardable historical anchor rows do not exist at or before that date.

## Deferred To 3차

- Macro-conditioned analog pilot.
- Rates / gold / futures / events / sentiment context combination.
- Any new storage/read path for PIT universe or sector metadata.
