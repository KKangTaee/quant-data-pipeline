# Strategy Promotion Contract Handoff Risks

Status: Active
Created: 2026-06-08

## Open Risks

| Risk | Impact | Mitigation |
|---|---|---|
| Contract becomes too broad for `backtest-dev` to fill | Strategy handoff may stall | Separate required fields from review/open follow-up fields and keep template structured. |
| Contract is mistaken for strategy approval | Product workflow could overstate readiness | Use `PROMOTE_READY`, `REVIEW_REQUIRED`, `BLOCKED`, `NOT_RUN` states and state that this is not live approval. |
| Risk-On Momentum 5D example reads like an approval | Deferred governance boundary could blur | Frame it as example evidence requirements only. |
| Helper can only check structure, not truth | False confidence if users treat it as approval | Name helper as contract completeness check and keep approval language out. |
| Existing dirty generated artifacts get committed | Local QA/run history noise enters repo | Stage only files created/modified for this task. |

## Follow-Up Constraints

- Future strategy implementation should run in `backtest-dev` or a strategy-specific implementation task.
- If Practical Validation UI/source payload changes are approved later, route through `finance-backtest-web-workflow`.
- If PIT/provenance fields need DB/schema changes, route through `finance-db-pipeline`.
