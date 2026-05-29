# Regime Split Validation V1 Notes

Status: Complete
Created: 2026-05-29
Completed: 2026-05-29

## Notes

- The task does not add a collector or schema; it consumes the existing macro loader.
- Missing macro history remains `NEEDS_INPUT` because current snapshot evidence is not enough for historical regime split.
- Official actual macro rows can support `PASS`; proxy / bridge rows downgrade source strength to `REVIEW`.
- Regime bucket returns are compact monthly return aggregates, not stored raw macro series or raw curve artifacts.
- The next task should decide how walk-forward / OOS / regime REVIEW or NEEDS_INPUT rows affect selected-route gate policy.
