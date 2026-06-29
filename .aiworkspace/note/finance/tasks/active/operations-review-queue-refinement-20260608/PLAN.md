# Operations Review Queue Refinement 2026-06-08 Plan

## 이걸 하는 이유?

Operations Overview V2 1~3차에서 archive/development-history 노출 제거, portfolio-first summary, Evidence Health mini strip을 추가했다.
4차는 그 다음에 보이는 `Today's Operations Queue`를 실제 운영자가 "무엇부터 확인해야 하는지" 기준으로 재정렬한다.

## Scope

- Modify `app/web/operations_overview.py`.
- Add focused contracts in `tests/test_service_contracts.py`.
- Update durable finance docs and root handoff logs after implementation.

## User Flow

1. 사용자는 Operations Console에 들어온다.
2. Portfolio Monitoring Status와 Evidence Health를 먼저 본다.
3. Today's Operations Queue에서 priority / evidence / target / next action을 순서대로 본다.
4. 필요한 경우 Portfolio Monitoring 또는 System / Data Health로 이동한다.

## Implementation Steps

1. RED: action queue priority / evidence / boundary contract tests를 추가하고 실패를 확인한다.
2. GREEN: already-loaded portfolio summary, evidence health, run history status를 사용해 queue item을 score / sort한다.
3. Render: queue card에 priority, evidence, target, read-only boundary를 명확히 표시한다.
4. Docs: roadmap / project map / flow / task manifest / root logs를 4차 상태로 맞춘다.
5. QA: focused unittest, py_compile, diff check, Browser QA screenshot을 실행한다.

## Out Of Scope

- Provider DB detail evidence fetch.
- Portfolio Monitoring scenario execution UX 변경.
- Registry / saved JSONL rewrite.
- Archive helper code deletion.
- Broker sync, order instruction, auto rebalance.
