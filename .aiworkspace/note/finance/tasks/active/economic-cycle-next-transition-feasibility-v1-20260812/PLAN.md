# Economic Cycle Next-Transition Feasibility V1

State: active
Last Updated: 2026-08-12

## 이걸 하는 이유?

사용자가 원하는 기능은 3·6개월 뒤 phase classification이 아니라 현재 정보로 다음
전환 목적지, 전환 임박도와 조건부 경로를 판단하는 기능이다. 기존 명세가 target을
잘못 고정했으므로 production 구현 전에 target을 바로잡고, 실제 PIT 전환 사건이
확률 학습과 검증에 충분한지 먼저 판정한다.

## Roadmap

1. 다음 confirmed phase와 전환 임박도 event 계약을 확정한다.
2. 모든 destination을 허용하는 전환 사건 추출과 표본 gate를 테스트 우선으로 만든다.
3. 실제 PIT panel에 적용해 GO / NO_GO_DATA를 결정한다.
4. GO면 별도 모델·UI task로, NO_GO_DATA면 공식 realtime data 확장 승인으로 넘긴다.

## Scope

- next-transition feasibility domain module과 tests
- 실제 DB를 변경하지 않는 PIT data audit
- 기존 research/spec/roadmap의 target과 결론 정렬

## Frozen Scope

- production DB schema와 refresh job
- Overview service/React UI
- current observed-state 계산
- 자산별 확인 포인트 계산·payload·디자인

## Stop Condition

표본 gate를 코드로 재현하고 실제 PIT 결과를 기록한 뒤, 결과에 따라 model/UI 착수
또는 data expansion 결정을 명확히 남기면 완료한다.
