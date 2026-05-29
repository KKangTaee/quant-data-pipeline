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
| 11-4 | `component-role-weight-discipline-v1` | `finance-backtest-web-workflow` | component role, hedge / diversifier evidence, profile-aware weight discipline | Complete |
| 11-5 | `construction-risk-gate-policy-v1` | `finance-backtest-web-workflow` | selected-route policy treatment for construction risk gaps | Complete |
| 11-6 | `phase11-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Next |

## Immediate Next Task

`phase11-integrated-qa-closeout`

Goal:

- Phase 11 변경을 통합 검증하고 phase closeout 가능한 상태로 정리한다.
- service contract / boundary / hygiene check를 재실행한다.
- active phase docs와 root handoff log를 최종 상태로 맞춘다.
- 새 JSONL registry, user memo, preset, approval, order, auto rebalance behavior는 추가하지 않는다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- live trading signal generation
- full optimizer replacement
- raw holdings / return matrix artifact 저장
