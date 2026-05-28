# Phase 8 Investability Data Evidence Expansion Tasks

Status: Active
Created: 2026-05-28

## Task Board

| Order | Task | Owner | Scope | Status |
| --- | --- | --- | --- | --- |
| 8-0 | `phase8-board-open` | main-dev | Phase 8 official board, roadmap sync, carry-forward mapping | Complete |
| 8-1 | `symbol-lifecycle-event-fields-v1` | `finance-db-pipeline` | lifecycle schema event fields, Form 25 / current listing row contract, loader/test/docs | Implementation complete |
| 8-2 | `historical-membership-source-review-v1` | main-dev + `finance-db-pipeline` | free / official source 후보 조사, source contract, ingestion feasibility | Pending |
| 8-3 | `symbol-action-ingestion-v1` | `finance-db-pipeline` | ticker change / merger / delisting action ingestion path | Pending |
| 8-4 | `historical-membership-ingestion-v1` | `finance-db-pipeline` | historical membership / computed snapshot evidence rows | Pending |
| 8-5 | `lifecycle-audit-scoring-v1` | `finance-backtest-web-workflow` | Data Coverage Audit evidence scoring refinement | Pending |
| 8-6 | `phase8-integrated-qa-closeout` | `finance-integration-review` + `finance-doc-sync` | compile, service contracts, docs, phase closeout | Pending |

## Previous Work Folded Into Phase 8

아래 task는 Phase 8 공식 오픈 전에 이미 완료됐지만 Phase 8의 선행 기반으로 본다.

- `historical-universe-survivorship-v1`
- `sec-form25-delisting-backfill-v1`
- `sec-form25-ingestion-ui-v1`

## Immediate Next Task

`historical-membership-source-review-v1`

Goal:

- 무료 / 공식 source 중 historical membership, ticker change, merger, delisting event를 안정적으로 얻을 수 있는 후보를 확인한다.
- source가 complete membership인지 event feed인지 current snapshot인지 구분한다.
- 구현 가능한 첫 ingestion slice를 정한다.

Out of scope:

- 새 JSONL registry
- user memo / preset persistence
- UI direct fetch
- live approval / broker order / auto rebalance
