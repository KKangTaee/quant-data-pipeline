# Walk-forward Split Contract V1 Risks

Status: Complete
Created: 2026-05-29

## Risks

| Risk | Status | Mitigation |
| --- | --- | --- |
| Walk-forward row over-trusts proxy curves | Mitigated | Proxy source downgrades otherwise passing evidence to `REVIEW` |
| Missing benchmark is treated as acceptable | Mitigated | Missing benchmark curve returns `NEEDS_INPUT` |
| Short history produces misleading split evidence | Mitigated | Too few common months returns `NEEDS_INPUT` |
| Final Review route ignores temporal validation | Partially mitigated | Validation Efficacy route now reflects temporal row; dedicated selected-route policy refinement remains 10-5 |
| OOS / regime evidence still missing | Open | Handed off to 10-3 and 10-4 |
