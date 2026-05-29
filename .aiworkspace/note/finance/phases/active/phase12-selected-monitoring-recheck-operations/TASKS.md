# Phase 12 Selected Monitoring / Recheck Operations Tasks

Status: Active
Created: 2026-05-29

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 12-0 | `phase12-board-open` | main-dev | Phase 12 official board, roadmap sync, task split | Complete |
| 12-1 | `selected-monitoring-source-map-v1` | `finance-task-intake` + `finance-backtest-web-workflow` | current Selected Dashboard / Final Review / runtime monitoring evidence source map and gap audit | Complete |
| 12-2 | `recheck-readiness-freshness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | DB market freshness, benchmark / component replay contract, missing / stale readiness policy | Complete |
| 12-3 | `selected-provider-evidence-staleness-contract-v1` | `finance-backtest-web-workflow` + `finance-db-pipeline` | provider holdings / exposure / operability freshness and coverage policy for selected portfolios | Complete |
| 12-4 | `recheck-comparison-review-signal-policy-v1` | `finance-backtest-web-workflow` | recheck baseline deterioration, review signal severity, failed / missing recheck handling | Complete |
| 12-5 | `allocation-drift-evidence-boundary-v1` | `finance-backtest-web-workflow` | optional actual allocation / drift evidence read-only boundary and alert preview | Complete |
| 12-6 | `decision-dossier-continuity-operations-v1` | `finance-backtest-web-workflow` | selected decision dossier / continuity / timeline operations evidence consistency | Complete |
| 12-7 | `phase12-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, storage boundary, phase closeout | Next |

## Next Target

`phase12-integrated-qa-closeout`

Goal:

- Phase 12 전체 변경이 compile / service contract / boundary / hygiene 검증을 통과하는지 확인한다.
- 새 JSONL registry, monitoring log 자동 저장, user memo / preset persistence가 추가되지 않았는지 확인한다.
- 완료된 12-1~12-6 결과를 phase closeout 기준으로 정리한다.

Out of scope:

- 새 JSONL registry
- monitoring log 자동 저장
- user memo / preset persistence
- broker order / live approval / auto rebalance
- account holdings 자동 연결
- UI direct provider / FRED / broker fetch
- full holdings / price history / macro series workflow JSONL 저장
