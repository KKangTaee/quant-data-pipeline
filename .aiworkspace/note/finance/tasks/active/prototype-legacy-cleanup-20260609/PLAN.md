# Prototype Legacy Cleanup / Removal Plan

Status: Active
Owner skill: finance-backtest-web-workflow
Started: 2026-06-09

## 이걸 하는 이유?

제품 방향 리서치 5순위로 남아 있던 legacy 정리 후보를 단순 archive demotion이 아니라 `Prototype Legacy Cleanup / Removal`로 실행한다.
Candidate Review, Portfolio Proposal, Pre-Live, old candidate packaging 흐름이 primary product에 남아 있으면 현재 정식 workflow가 다시 구 prototype 단계에 끌려갈 수 있다.

현재 정식 workflow는 아래로 고정한다.

```text
Backtest Analysis
  -> Practical Validation
  -> Final Review
  -> Operations > Portfolio Monitoring
```

## 작업 범위

- Backtest primary navigation / route helper / direct dispatch에서 legacy panel이 정식 단계처럼 열리는지 조사하고 정리한다.
- Overview / Operations / Reference / durable docs에서 old candidate / proposal copy가 현재 정식 workflow처럼 보이는 부분을 정리한다.
- Backtest Run History와 Candidate Library는 recovery 가치가 있으면 Operations archive / recovery로 유지한다.
- registry / saved JSONL은 삭제하거나 rewrite하지 않는다.
- generated run history, screenshots, temp artifact, `.DS_Store`는 stage하지 않는다.

## 1차 / 2차 / 3차

| 차수 | 목적 | 바뀔 화면 / 파일 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차 | Legacy inventory / 삭제 기준 수립 | active task docs, route / docs / Overview 조사 | 주요 legacy surface가 `DELETE_NOW`, `HIDE_FROM_PRIMARY`, `ARCHIVE_RECOVERY`, `KEEP_PRIMARY`, `DEFER_DELETE`로 분류됨 | 2차 코드 cleanup 대상 확정 |
| 2차 | Code / route / UI cleanup | `app/web/backtest_workflow_routes.py`, `app/web/pages/backtest.py`, `app/web/backtest_common.py`, Overview primary tabs/copy, related tests | Candidate Review / Portfolio Proposal / Pre-Live / old candidate packaging이 primary route나 Overview primary tab에서 보이지 않음 | 3차 docs sync / QA |
| 3차 | Docs / tests / QA / commit | durable docs, task/root logs, focused tests, Browser QA if needed | docs가 current workflow를 설명하고 focused checks가 통과하며 coherent commit 생성 | 다음 cleanup/refactor 후보는 deferred risk로 남김 |

## 5C 추가 차수

5B에서 route와 primary tab을 숨긴 뒤 남은 legacy module을 물리적으로 정리한다.

| 차수 | 목적 | 바뀔 화면 / 파일 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차 | Import graph / consumer audit | legacy Candidate / Proposal UI/helper, current Backtest result/history/compare/final-review consumers, runtime registry helpers | 대상 파일을 `DELETE_NOW`, `EXTRACT_CURRENT_HELPER`, `ARCHIVE_RECOVERY`, `KEEP_CURRENT`, `DEFER_DELETE`로 재분류 | 2차 current handoff extraction |
| 2차 | Current handoff helper extraction | `app/services/backtest_practical_validation_source.py`, `app/web/backtest_practical_validation_handoff.py`, current Backtest result/history/compare modules | current workflow가 legacy Candidate Review helper 없이 Practical Validation source handoff를 만든다 | 3차 physical cleanup |
| 3차 | Legacy UI/helper physical deletion | `app/web/backtest_candidate_review*.py`, `app/web/backtest_portfolio_proposal*.py`, `app/web/overview_dashboard_helpers.py` | 삭제 가능한 prototype UI/helper가 실제 삭제되고 Overview legacy snapshot helper가 제거된다 | 4차 docs/tests/commit |
| 4차 | Docs / tests / QA / commit | durable docs, task/root logs, focused tests, Browser QA | docs가 old workflow를 current처럼 설명하지 않고 coherent commit이 생성된다 | 남은 legacy runtime은 archive / recovery compatibility로만 유지 |

## 분류 기준

| Label | 기준 |
|---|---|
| `DELETE_NOW` | current workflow와 충돌하고, registry/saved 보존이나 recovery 가치가 없으며, 삭제해도 import/test 경계가 안전한 prototype surface |
| `HIDE_FROM_PRIMARY` | 파일/호환 helper는 당장 남기지만 navigation, primary route, Overview/Reference primary copy에서는 제거해야 하는 surface |
| `ARCHIVE_RECOVERY` | 과거 기록 복구, form restore, read-only inspection 가치가 있어 Operations archive / recovery로만 유지하는 surface |
| `KEEP_PRIMARY` | 현재 정식 workflow에 직접 필요한 screen, service, route, record chain |
| `DEFER_DELETE` | 삭제 가능성이 있지만 migration proof, registry consumer audit, or broader refactor가 필요한 surface |

## Out Of Scope

- registry / saved JSONL 삭제 또는 rewrite
- live approval, broker order, account sync, auto rebalance
- 새 strategy, 새 DB migration, provider fetch 추가
- Candidate Library / Run History의 historical record 자체 삭제
- legacy implementation file rename
- generated artifact cleanup commit

## Stop Condition

- primary product에서 prototype legacy workflow가 정식 단계처럼 보이지 않는다.
- 보존 surface는 Archive / Recovery read-only 의미가 분명하다.
- docs는 `Backtest Analysis -> Practical Validation -> Final Review -> Portfolio Monitoring`만 current workflow로 설명한다.
- focused tests / py_compile / diff checks가 가능한 범위에서 통과하고, 필요한 UI QA evidence가 남는다.
