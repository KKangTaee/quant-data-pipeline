# Phase 11 Portfolio Construction Risk Controls Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 11-0 | `phase11-board-open` | main-dev | Phase 11 official board, roadmap sync, task split | Complete |
| 11-1 | `construction-risk-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Practical Validation / Look-through / Robustness Lab / Final Review gate construction risk source map and gap audit | Complete |
| 11-2 | `concentration-overlap-exposure-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | component weight concentration, holdings overlap, asset / sector / theme exposure evidence contract | Next |
| 11-3 | `correlation-risk-contribution-contract-v1` | `finance-backtest-web-workflow` + `finance-strategy-implementation` | component return correlation, volatility contribution, drop-one dependency evidence contract | Planned |
| 11-4 | `component-role-weight-discipline-v1` | `finance-backtest-web-workflow` | component role, hedge / diversifier evidence, profile-aware weight discipline | Planned |
| 11-5 | `construction-risk-gate-policy-v1` | `finance-backtest-web-workflow` | selected-route policy treatment for construction risk gaps | Planned |
| 11-6 | `phase11-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Planned |

## Immediate Next Task

`concentration-overlap-exposure-contract-v1`

Goal:

- 기존 Practical Validation concentration diagnostic과 provider look-through board를 재사용해 read-only Construction Risk Audit의 concentration / overlap / exposure contract를 만든다.
- component max weight, top holding weight, top overlap weight, dominant asset bucket, unknown exposure, provider coverage를 한 contract로 묶는다.
- provider holdings / exposure가 없거나 partial이면 `PASS`가 아니라 `REVIEW` 또는 `NEEDS_INPUT`으로 남긴다.
- full holdings, raw provider response, user memo, preset 저장 없이 compact evidence만 사용한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- live trading signal generation
- full optimizer replacement
- raw holdings / return matrix artifact 저장
