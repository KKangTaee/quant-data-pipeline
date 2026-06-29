# Operations V2 Closeout 2026-06-08 Plan

## 이걸 하는 이유?

Operations Overview V2 1~4차에서 archive / development-history 노출 제거, Portfolio Monitoring Status summary, Evidence Health, priority review queue를 추가했다.
5차는 이 흐름을 전체 QA / 문서 / runbook 기준으로 닫고 다음 작업자가 어디서 이어가야 하는지 명확히 한다.

## Scope

- Validate `Operations > Operations Overview` through the app's normal top navigation path.
- Confirm the Operations Overview read model still exposes portfolio summary, evidence health, review queue, primary lanes, and disabled execution boundary.
- Document the direct `/operations` local routing modal as QA noise when it appears only on direct path entry.
- Update durable docs, runbook index, task manifests, and root handoff logs.

## Out Of Scope

- New Operations feature work.
- Portfolio Monitoring scenario execution UX changes.
- Provider DB detail fetch or ingestion collection.
- Registry / saved JSONL rewrite.
- Archive helper code deletion.
- Broker sync, order instruction, account sync, or auto rebalance.
