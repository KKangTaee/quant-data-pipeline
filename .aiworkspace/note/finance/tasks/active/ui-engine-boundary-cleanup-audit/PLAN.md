# UI Engine Boundary Cleanup Audit Plan

Status: Complete
Created: 2026-05-27

## 이걸 하는 이유?

이 task는 Task 6~9 구현 전에 방향을 다시 고정하기 위한 audit 작업이다.
목표는 전체 코드를 전부 뜯어고치는 것이 아니라, 지금 남은 UI-engine 분리 부채가 어디에 있고 어떤 순서로 고치는 것이 안전한지 정리하는 것이다.

## Scope

포함한다.

- 현재 docs / code boundary 확인
- boundary lint 결과 기록
- service/runtime에서 web helper를 참조하는 지점 확인
- 큰 cleanup 후보 파일과 하위 task 방향 정리
- phase / task 문서 생성
- root handoff log / roadmap 갱신

포함하지 않는다.

- 코드 이동
- Streamlit UI 변경
- tests 추가 / 수정
- provider collection 구현
- runtime strategy 계산 변경

## Done Criteria

- `ui-engine-boundary-cleanup` phase 문서가 생성되어 있다.
- Task 6~9가 하위 단계 단위로 정리되어 있다.
- 현재 advisory import와 큰 파일 후보가 기록되어 있다.
- 이번 작업에서 브라우저 테스트가 필요한지 판단이 기록되어 있다.
