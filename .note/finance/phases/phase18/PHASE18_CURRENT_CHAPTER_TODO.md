# Phase 18 Current Chapter TODO

## 목표

- `Value`와 `Quality + Value` strict annual family에서
  Phase 17보다 더 큰 구조 변경을 실제 코드에 연결한다.
- 지금은 broad deep backtest보다
  **구현 backlog를 먼저 정리하는 모드**다.
- deeper rerun / wider rescue search는
  remaining implementation slice가 더 닫힌 뒤 다시 연다.

## 상태

- `practical_closeout / manual_validation_pending`

## Workstream A. Implementation-First Reprioritization

- [x] next major direction을 `larger structural redesign`로 고정
- [x] first slice를 `next-ranked eligible fill`로 선택
- [x] 기존 `partial cash retention` / `defensive sleeve` / `rank_tapered`와 해석 충돌 지점 정리
- [x] current mode를 `implementation_first`로 재정렬
- [x] deeper rerun pause 원칙과 resume 조건을 phase 문서에 기록

## Workstream B. First Implementation Slice

- [x] strict annual family 3종에 `rejected_slot_fill_enabled` contract 추가
- [x] single / compare / history / rerun surface 연결
- [x] interpretation / warning / selection-history field 보강
- [x] compile / import smoke 통과

## Workstream C. Minimal Validation For First Slice

- [x] `Value` trend-on structural probe에 representative rerun 적용
- [x] `Quality + Value` strongest-point trend-on structural probe에 representative rerun 적용
- [x] actual rescue / anchor replacement / still-hold를 분리해서 기록
- [x] `Value` current practical anchor 근처(`+psr`, `+psr+pfcr`, `Top N 12~16`) follow-up second pass 수행

## Workstream D. Remaining Implementation Backlog Closeout Decision

- [x] Phase 18 second slice 후보 backlog를 current closeout 시점에 다시 검토
- [x] second slice는 current phase blocker가 아니라 future structural backlog로 defer
- [x] deep rerun 재개 조건은 "second slice 구현"이 아니라 Phase 21 integrated validation frame으로 재정리
- [x] next structural backlog는 Phase 21 validation 이후 다시 열지 판단하도록 정리

## Workstream E. Candidate Consolidation / Operator Bridge Support Decision

- [x] current strongest / near-miss candidate를 compare -> weighted -> saved 흐름으로 다시 읽는 gap inventory의 필요성을 재검토
- [x] operator bridge support 성격의 후속 작업은 Phase 20에서 실질적으로 다뤄졌음을 반영
- [x] main track을 방해하지 않는 범위의 bridge polish는 별도 closeout blocker로 보지 않기로 결정

## 현재 판단

- `Value`
  - fill contract는 redesign reference로는 유효하지만
    trend-on probe와 anchor-near second pass 모두 still `hold / blocked`였다
  - 즉 current practical anchor replacement나 gate rescue까지는 아니다
- `Quality + Value`
  - cash share와 `MDD`는 개선되지만
    still `hold / blocked`
  - blended strongest point를 교체하는 결과는 아니다
- 공통:
  - next-ranked fill first slice는 meaningful redesign evidence로는 남지만
    current anchor replacement까지는 아니다
  - remaining second-slice idea를 더 미는 것보다,
    지금까지 정리된 후보를 같은 frame에서 다시 검증하는 Phase 21이 더 우선이다

## 다음 active step

- [x] Phase 18 practical closeout 문서 작성
- [x] Phase 18 next-phase handoff 문서 작성
- [x] Phase 18 manual checklist 문서 작성
- [ ] Phase 21 integrated validation frame first pass 시작
