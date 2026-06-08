# Robustness Experiment Registry Plan

Status: Active
Created: 2026-06-08

## 이걸 하는 이유?

현재 Robustness Lab은 stress / rolling / sensitivity / overfit evidence를 compact board로 잘 보여주지만, 여러 실험을 하나의 `run-set` provenance로 묶는 계약은 약하다. 그래서 Practical Validation과 Final Review는 "이 후보 판단이 어떤 반복 실험 묶음에 근거했는가"를 명시적으로 추적하기 어렵다.

이번 작업은 새 전략 개발이나 성과 개선이 아니라, 기존 validation evidence를 `robustness_run_set_id`가 있는 compact 실험 묶음으로 읽게 만드는 작은 provenance layer다.

## Roadmap

| 차수 | 목적 | 바뀔 범위 | 완료 조건 | 다음 차수 연결 |
|---|---|---|---|---|
| 1차 | evidence 생성 위치를 확인하고 최소 schema를 정의한다 | task 문서, code audit | Robustness Lab / temporal / validation efficacy / realism evidence owner와 run-set schema가 문서화됨 | 2차 read model 구현 기준 |
| 2차 | compact Robustness Experiment Registry read model을 구현한다 | `app/services`, focused tests | 하나의 selected source / strategy family에 대해 run-set summary를 생성할 수 있음 | 3차 UI/evidence 소비 경로 |
| 3차 | Practical Validation / Final Review 연결, docs sync, QA, commit | web render, durable docs, tests | run-set id와 summary evidence가 PV/Final Review에서 읽히고 검증/commit 완료 | 후속 strategy-specific perturbation / broader suites |

## Scope

- 기존 Robustness Lab board를 보존한다.
- `robustness_run_set_id`가 있는 compact read model을 만든다.
- source id 또는 promotion contract reference, strategy family/key, frozen parameter set, experiment types, IS/OOS, walk-forward, regime, cost/slippage, parameter perturbation, NOT_RUN/REVIEW/BLOCKED evidence, artifact references, decision effect를 compact하게 담는다.
- Practical Validation result와 Final Review evidence packet / saved decision snapshot이 run-set summary를 읽을 수 있게 한다.
- full trade log, full holdings, full macro series, raw provider response는 workflow JSONL에 넣지 않고 reference만 남긴다.

## Out Of Scope

- 새 전략 개발.
- 전략 성과 개선.
- 대규모 Monte Carlo 또는 전체 전략군 batch runner.
- registry / saved JSONL rewrite.
- live approval, broker order, account sync, auto rebalance.
- 기존 `robustness-lab-v1` 삭제 또는 대체.

## Verification

- focused service contract tests.
- compile checks for touched modules.
- `git diff --check`.
- 가능한 범위에서 Browser QA.
- generated artifacts and local run history are left unstaged.
