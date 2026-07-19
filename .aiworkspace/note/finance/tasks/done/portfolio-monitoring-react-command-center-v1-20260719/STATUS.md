# Portfolio Monitoring React Command Center V1 Status

Status: Complete
Last Updated: 2026-07-19

## Current Position

- 전체 roadmap: `6/6차 구현·migration·QA 완료`
- current milestone: Task 21 durable docs, safe migration, responsive Browser QA, full regression complete
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

## Delivered

1. DB-backed group/item lifecycle와 default group exactly one
2. direct stock/ETF와 Final Review selected strategy catalog/valuation
3. Portfolio-first React one-shell, Context Drawer, common-basis KPI/item detail
4. deterministic exposure/behavior diagnosis와 macro risk observation
5. PIT diagnosis history, OOS calibration, fingerprint-safe probability gate
6. production schema migration, non-destructive legacy dry-run, 1440/760/420 Browser QA

## Deployment Boundary

- actual `finance_meta`에는 canonical five-table schema와 `monitoring_default` group 하나가 생성됐다. 사용자 item/command/diagnosis/calibration row는 만들지 않았다.
- actual legacy setup은 dry-run만 했고 source checksum `a2eadad5c7ea8d20beda955df953e3613d916b7c16c118123b859708d629f1dc`를 보존했다.
- 확률은 current config fingerprint의 `READY` calibration artifact가 없으므로 actual UI에서 `SUPPRESSED`다.
- 화면은 provider fetch, live approval, broker order, account sync, auto rebalance를 만들지 않는다.
