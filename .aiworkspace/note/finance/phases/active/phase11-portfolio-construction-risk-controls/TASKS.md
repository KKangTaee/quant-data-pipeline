# Phase 11 Portfolio Construction Risk Controls Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 11-0 | `phase11-board-open` | main-dev | Phase 11 official board, roadmap sync, task split | Complete |
| 11-1 | `construction-risk-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Practical Validation / Look-through / Robustness Lab / Final Review gate construction risk source map and gap audit | Complete |
| 11-2 | `concentration-overlap-exposure-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | component weight concentration, holdings overlap, asset / sector / theme exposure evidence contract | Complete |
| 11-3 | `correlation-risk-contribution-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | component return correlation, volatility contribution, drop-one dependency evidence contract | Complete |
| 11-4 | `component-role-weight-discipline-v1` | `finance-backtest-web-workflow` | component role, hedge / diversifier evidence, profile-aware weight discipline | Next |
| 11-5 | `construction-risk-gate-policy-v1` | `finance-backtest-web-workflow` | selected-route policy treatment for construction risk gaps | Planned |
| 11-6 | `phase11-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Planned |

## Immediate Next Task

`component-role-weight-discipline-v1`

Goal:

- component가 어떤 역할을 맡는지, hedge / diversifier / growth role이 evidence로 확인되는지 점검한다.
- validation profile 기준으로 max weight와 role concentration discipline을 compact row로 표시한다.
- role source가 없거나 weight discipline 근거가 부족하면 `PASS`가 아니라 `NEEDS_INPUT` 또는 `REVIEW`로 남긴다.
- component role metadata source를 먼저 확인하고, user memo / preset 성격의 새 저장 기능은 만들지 않는다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- live trading signal generation
- full optimizer replacement
- raw holdings / return matrix artifact 저장
