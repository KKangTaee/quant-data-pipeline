# Plan

## Goal

최근 완료 작업 이후 Finance Console의 current 탭별 제품 내용, code ownership, durable docs, task / roadmap 상태를 진단하고 오래된 문서 표현과 누락된 flow 설명을 분리한다.

## 이걸 하는 이유?

최근 작업이 여러 surface를 바꾼 뒤 문서가 다시 오래된 `Workspace > Overview`, `Operations`, legacy tab, completed-task chronology 중심으로 흐를 수 있다. 실제 사용자가 보는 7개 top-level surface와 canonical docs가 다르게 읽히면 다음 개발자가 잘못된 owner나 오래된 경로를 따라가게 된다.

## Scope

- 1차: 진단. 실제 navigation, surface별 owner, durable docs, state manifest, stale terminology를 대조한다.
- 2차: 정리 계획. canonical doc role별로 고칠 것 / 유지할 것 / 제거할 것을 정한다.
- 3차: 승인된 범위의 문서 보강 / 정리 / 필요한 작은 code contract 보정.
- 4차: focused validation, generated artifact 제외, commit / handoff.

## Stop Condition

- 1차 진단 결과가 탭별로 정리되고, 수정 후보가 `must fix`, `candidate cleanup`, `intentional retained history`로 분리된다.
- 문서 편집은 1차 진단 후 범위가 확정될 때 진행한다.
