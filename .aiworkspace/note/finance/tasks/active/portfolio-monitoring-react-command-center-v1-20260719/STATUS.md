# Portfolio Monitoring React Command Center V1 Status

Status: 3차 React Portfolio Command Center Complete / 4차 Diagnosis Next
Last Updated: 2026-07-19

## Current Position

- 전체 roadmap: `3/6차 구현 완료`
- current milestone: 3차 Task 11 React page cutover complete; 4차 Task 12 exposure facts next
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

1. Task 12 normalized portfolio exposure facts
2. Task 13 deterministic behavior policy
3. Task 14 diagnosis priority/evidence React UI and 4차 gate

## Deployment Boundary

- actual `finance_meta.monitoring_portfolio_*` tables are not migrated yet; the route opens the React recovery state with DB catalog access and mutation commands return explicit errors.
- the storage migration, default-group creation, rollback, and mutating Browser QA remain Task 21 closeout work; no table was created automatically in 1~3차.
