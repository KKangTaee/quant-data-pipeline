# Phase 18 Current Chapter TODO

## 목표

- `Value`와 `Quality + Value` strict annual family에서
  Phase 17보다 더 큰 구조 변경을 실제 코드에 연결한다.
- 이번 챕터의 first slice는
  `Fill Rejected Slots With Next Ranked Names`
  contract다.

## 상태

- `in_progress`

## Workstream A. Larger Structural Redesign Kickoff

- [x] next major direction을 `larger structural redesign`로 고정
- [x] first slice를 `next-ranked eligible fill`로 선택
- [x] 기존 `partial cash retention` / `defensive sleeve` / `rank_tapered`와 해석 충돌 지점 정리

## Workstream B. First Implementation Slice

- [x] strict annual family 3종에 `rejected_slot_fill_enabled` contract 추가
- [x] single / compare / history / rerun surface 연결
- [x] interpretation / warning / selection-history field 보강
- [x] compile / import smoke 통과

## Workstream C. Representative Rerun First Pass

- [x] `Value` trend-on structural probe에 representative rerun 적용
- [x] `Quality + Value` strongest-point trend-on structural probe에 representative rerun 적용
- [x] actual rescue / anchor replacement / still-hold를 분리해서 기록
- [x] `Value` current practical anchor 근처(`+psr`, `+psr+pfcr`, `Top N 12~16`) follow-up second pass 수행

## 현재 판단

- `Value`
  - fill contract는 cash drag를 줄이고 validation을 개선하는 방향으로는 작동했다
  - 하지만 trend-on probe와 anchor-near second pass 모두 still `hold / blocked`였다
  - 즉 current practical anchor replacement나 gate rescue까지는 아니다
- `Quality + Value`
  - cash share와 `MDD`는 개선되지만
    still `hold / blocked`
  - blended strongest point를 교체하는 결과는 아니다

## 다음 active step

- [x] `Value`에서 fill contract를 current practical anchor 근처에 더 직접 적용하는 follow-up 수행
- [ ] `Quality + Value`에서 gate recovery까지 같이 볼 수 있는 second redesign lane 검토
- [ ] Phase 18 second slice 후보 우선순위 정리
