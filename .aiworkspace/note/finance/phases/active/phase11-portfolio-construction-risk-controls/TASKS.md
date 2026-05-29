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
| 11-5 | `construction-risk-gate-policy-v1` | `finance-backtest-web-workflow` | selected-route policy treatment for construction risk gaps | Next |
| 11-6 | `phase11-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Planned |

## Immediate Next Task

`construction-risk-gate-policy-v1`

Goal:

- Construction Risk / Risk Contribution / Component Role Weight audit route를 selected-route gate policy에 연결한다.
- `NEEDS_INPUT` / `BLOCKED`는 selected-route blocker로, `REVIEW`는 review-required 근거로 표시한다.
- row-level non-PASS criteria가 generic route 뒤에 숨지 않게 Final Review gate evidence에 병합한다.
- 새 JSONL registry, user memo, preset, approval, order, auto rebalance behavior는 추가하지 않는다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- broker order / live approval / auto rebalance
- live trading signal generation
- full optimizer replacement
- raw holdings / return matrix artifact 저장
