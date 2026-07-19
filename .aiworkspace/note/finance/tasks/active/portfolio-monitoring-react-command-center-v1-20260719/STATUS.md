# Portfolio Monitoring React Command Center V1 Status

Status: 4차 Strength And Weakness Diagnosis Complete / 5차 Macro Risk Observation Next
Last Updated: 2026-07-19

## Current Position

- 전체 roadmap: `4/6차 구현 완료`
- current milestone: 4차 Task 14 evidence UI complete; 5차 Task 15 persisted macro context adapter next
- written design: approved by user
- detailed implementation plan: complete and self-reviewed
- implementation: started in inline execution mode

## Approved Decisions

- Overview / Market Context와 같은 React one-shell
- Portfolio-first Command Center
- Context Drawer item builder
- direct U.S. stock/ETF + Final Review monitoring candidate
- group maximum 10 items
- fixed notional and direct-security integer shares
- missing start price blocks registration
- pre-start/post-end capital remains cash
- deterministic layered diagnosis, probability only after calibration

## Next Action

1. Task 15 persisted macro snapshot adapter
2. Task 16 exposure-context match and confidence cap
3. Task 17 Macro Risk Observation UI / Operations handoff

## Deployment Boundary

- actual `finance_meta.monitoring_portfolio_*` tables are not migrated yet; the route opens the React recovery state with DB catalog access and mutation commands return explicit errors.
- the storage migration, default-group creation, rollback, and mutating Browser QA remain Task 21 closeout work; no table was created automatically in 1~3차.
- 4차 diagnosis React bundle is verified by contract tests; its populated visual Browser QA repeats after Task 21 because the recovery workspace intentionally has no active group.
