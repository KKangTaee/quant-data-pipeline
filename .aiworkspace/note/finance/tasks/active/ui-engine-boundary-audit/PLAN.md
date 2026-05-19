# UI Engine Boundary Audit Plan

Status: Active
Created: 2026-05-19

## 이걸 하는 이유?

`ui-engine-boundary-foundation` phase의 첫 작업은 코드를 바로 옮기는 것이 아니라, 현재 코드 흐름을 충분히 읽고 안전한 분리 순서를 확정하는 것이다.

이 audit이 없으면 `app/services`를 만들더라도 UI, runtime, registry, validation 계산이 다시 섞일 수 있다.
따라서 첫 task는 어떤 파일이 어떤 책임을 갖고, 어떤 부분을 service로 옮길 수 있으며, 어떤 부분은 아직 건드리면 위험한지 정리한다.

## Scope

포함:

- Backtest Single Strategy flow
- Compare / Weighted Portfolio flow
- Practical Validation flow
- Selected Dashboard read model flow
- `app/web/runtime` adapter/helper boundary
- `finance/*` engine boundary

제외:

- 코드 이동
- UI 변경
- DB/schema 변경
- registry rewrite

## Deliverables

- `NOTES.md`: audit findings
- `RUNS.md`: commands and results
- `RISKS.md`: risk and mitigation
- `STATUS.md`: task state and next task recommendation

## Done Criteria

- first implementation task target is identified
- no-go files for first implementation are listed
- validation baseline is listed
- phase docs point to this task as first audit
