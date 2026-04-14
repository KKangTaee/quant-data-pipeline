# Phase 18 Implementation-First Reprioritization

## 배경

- user decision 기준으로,
  지금은 deeper rerun / broad search를 계속 밀기보다
  **남아 있는 구현 항목을 먼저 정리한 뒤**
  다시 깊은 백테스트로 돌아가는 것이 더 자연스럽다.
- Phase 18 first slice(`next-ranked eligible fill`)는
  meaningful redesign lane임은 확인됐지만,
  current `Value` / `Quality + Value` anchor를 교체하는
  practical rescue로는 아직 고정되지 않았다.

즉 현재 phase의 운영 모드는
`backtest-first`가 아니라
**implementation-first**다.

## 이번 재정렬에서 고정한 원칙

1. broad deep backtest는 잠시 멈춘다
2. 새로운 구현 slice를 붙일 때는
   - compile / import smoke
   - minimal representative rerun
   정도만 수행한다
3. integrated deep rerun / larger search는
   implementation backlog가 어느 정도 닫힌 뒤 다시 연다

## 현재 implementation backlog

### 1. structural redesign main track

- second larger-redesign slice 후보를 좁힌다
- strict annual rejection-handling contract를
  operator가 읽기 쉽게 정리한다
  - survivor reweighting
  - partial cash retention
  - next-ranked fill
- 새 slice가 추가되면
  single / compare / history / prefill / interpretation surface를
  같이 맞춘다

### 2. candidate consolidation / operator bridge support track

- current strongest / near-miss candidate를
  compare -> weighted -> saved portfolio 흐름으로
  더 쉽게 연결할 수 있는지 본다
- 이 트랙은 immediate main track은 아니지만,
  구현을 먼저 해두면
  나중에 deeper rerun 결과를 정리하고 재현하기가 쉬워진다

## deep backtest를 다시 여는 시점

아래가 어느 정도 정리된 뒤 다시 여는 것이 맞다.

- larger structural redesign slice backlog가 더 구현되었는가
- operator-facing surface와 해석 문구가 current code와 맞는가
- strongest / near-miss candidate를 다시 읽을 context가 정리되었는가

그 뒤에는:

- integrated representative rerun
- broader rescue search
- family별 same-gate lower-MDD 검증

순으로 다시 돌아간다.

## immediate next step

- Phase 18 second slice 후보를
  **구현 관점에서 먼저 shortlist**
  한다
- 그 다음 실제 코드를 연결하고,
  마지막에 minimal validation만 붙인다

## 한 줄 결론

지금 Phase 18은
**깊은 백테스트를 더 밀어붙이는 단계가 아니라,
남아 있는 structural / operator 구현을 먼저 정리하는 단계**
로 읽는 것이 맞다.
