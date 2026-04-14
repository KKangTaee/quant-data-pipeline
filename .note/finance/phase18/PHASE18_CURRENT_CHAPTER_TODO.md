# Phase 18 Current Chapter TODO

## 목표

- `Value`와 `Quality + Value` strict annual family에서
  Phase 17보다 더 큰 구조 변경을 실제 코드에 연결한다.
- 지금은 broad deep backtest보다
  **구현 backlog를 먼저 정리하는 모드**다.
- deeper rerun / wider rescue search는
  remaining implementation slice가 더 닫힌 뒤 다시 연다.

## 상태

- `in_progress`

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

## Workstream D. Remaining Implementation Backlog

- [ ] Phase 18 second slice 후보 shortlist
- [ ] second slice 설계 문서 작성
- [ ] second slice 실제 코드 연결
- [ ] single / compare / history / prefill / interpretation sync
- [ ] minimal representative validation 수행

## Workstream E. Candidate Consolidation / Operator Bridge Support

- [ ] current strongest / near-miss candidate를 compare -> weighted -> saved 흐름으로 다시 읽을 때의 gap inventory 정리
- [ ] immediate bridge polish 후보 1개 선정
- [ ] main track을 방해하지 않는 범위에서 보조 구현 순서 정리

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
  - 지금은 더 깊은 rerun을 넓히기보다
    remaining implementation slice를 먼저 닫는 것이 맞다

## 다음 active step

- [ ] Phase 18 second slice 후보 우선순위 정리
- [ ] second slice를 구현 관점에서 먼저 설계
- [ ] deep rerun은 second slice 코드가 붙은 뒤 최소 범위로 재개
