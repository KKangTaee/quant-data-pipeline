# Phase Test Checklist Template

## 목적

- 이 checklist가 무엇을 확인하는 문서인지 짧게 적는다.
- 이번 checklist가 숫자 검증인지, UI 해석 검증인지, workflow 검증인지 먼저 적는다.

## 사용 방법

- 아래 항목은 사용자가 직접 `[ ]`를 `[x]`로 바꾸며 확인한다.
- 특별한 사유가 없으면, 모든 주요 체크 항목이 완료된 뒤 다음 major phase로 넘어간다.
- 일부 항목을 나중으로 미루면 그 이유를 문서나 handoff에 짧게 남긴다.

## 추천 실행 순서

1. 가장 핵심 UI 또는 workflow 확인
2. history / reload / compare 같은 연결 흐름 확인
3. 문서 / closeout / index 확인

## 1. 첫 번째 확인 영역

- 확인 위치:
  - 실제 UI 경로나 문서 경로를 적는다.
- 체크 항목:
  - [ ] 가장 먼저 보여야 하는 요소가 보이는지
  - [ ] 핵심 옵션 이름이 사용자가 이해할 수 있는 언어로 보이는지
  - [ ] 현재 선택이 무슨 뜻인지 설명이 같이 보이는지

## 2. 두 번째 확인 영역

- 확인 위치:
  - 실제 UI 경로나 문서 경로를 적는다.
- 체크 항목:
  - [ ] compare / history / load-into-form 같은 연결 흐름이 자연스러운지
  - [ ] 설정값 복원이나 meta surface가 기대대로 읽히는지

## 3. 세 번째 확인 영역

- 확인 위치:
  - 실제 UI 경로나 문서 경로를 적는다.
- 체크 항목:
  - [ ] interpretation / summary / report 문구가 읽기 쉬운지
  - [ ] operator가 다음 액션을 이해할 수 있는지

## 4. 문서와 closeout 확인

- 확인 문서:
  - 관련 phase TODO
  - completion summary
  - next phase preparation
  - roadmap / index
- 체크 항목:
  - [ ] phase 상태가 현재 구현 상태와 맞는지
  - [ ] 새 문서가 index에서 바로 찾히는지
  - [ ] 다음 단계로 넘어가기 위한 설명이 충분한지

## 한 줄 판단 기준

- 이번 checklist는
  “기능이 추가됐는가”보다,
  **사용자가 그 기능을 다시 찾아서 읽고 이해하고 검수할 수 있는가**
  를 확인하는 문서다.
