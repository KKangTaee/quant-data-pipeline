# Walk-forward / OOS Source Map V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

| Risk | Impact | Mitigation |
| --- | --- | --- |
| Runtime OOS metadata and Practical Validation evidence diverge | Final Review may show inconsistent temporal validation | Build one service-level compact contract and reuse it where possible |
| Proxy curve evidence is over-trusted | DB price proxy can differ from actual strategy path | Carry curve source strength and avoid proxy-only PASS |
| Short history is over-interpreted | Split validation can be meaningless with too few observations | Map insufficient history to `NEEDS_INPUT` or `REVIEW` |
| Regime split becomes a current macro snapshot only | It will not answer whether strategy worked across regimes | Separate 10-4 historical regime split from current macro suitability |
| Storage sprawl returns | Raw split artifacts could bloat workflow JSONL | Store only compact audit rows in existing validation result payload |
