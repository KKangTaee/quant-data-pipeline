# Walk-forward / OOS Source Map V1 Status

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Completed

- Mapped current curve source hierarchy in Practical Validation.
- Mapped existing runtime rolling / OOS metadata.
- Confirmed Robustness Lab rolling evidence is present but currently portfolio-only.
- Confirmed Validation Efficacy Audit has no explicit temporal validation row yet.
- Confirmed Final Review gate can consume audit rows once temporal validation rows exist.
- Updated Phase 10 task board so 10-2 is next.

## Next

Start `walkforward-split-contract-v1`.

Initial implementation recommendation:

- Add a compact walk-forward / rolling temporal validation helper.
- Use existing normalized portfolio / benchmark curves.
- Require benchmark parity for relative PASS.
- Keep missing / short / proxy-only evidence as `NEEDS_INPUT` or `REVIEW`.
