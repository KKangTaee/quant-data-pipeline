# Phase 8 Quarterly Family Scope And Compare Decision

## 결정 요약

- quarterly strict family는 이번 Phase 8 first pass에서 아래 3개로 정리한다.
  - `Quality Snapshot (Strict Quarterly Prototype)`
  - `Value Snapshot (Strict Quarterly Prototype)`
  - `Quality + Value Snapshot (Strict Quarterly Prototype)`
- 세 전략 모두 현재 해석은 `research-only`다.
- single strategy UI에는 모두 노출한다.
- compare surface에도 first pass로 모두 노출한다.

## 왜 이렇게 정리했는가

- Phase 7에서 quarterly data foundation과 PIT timing은 복구되었지만,
  product 관점에서는 여전히 quality만 열려 있었다.
- value와 quality+value가 빠진 상태에서는
  quarterly family를 annual strict family와 비교 가능한 전략군이라고 보기 어렵다.
- compare까지 같이 열어야
  annual vs quarterly,
  quality vs value vs quality+value
  비교 연구가 가능해진다.

## current exposure policy

### Single Strategy

- 3개 quarterly prototype 모두 노출
- 기본 preset:
  - `US Statement Coverage 100`
- preflight:
  - strict price freshness
  - quarterly statement shadow coverage preview
- overlays:
  - trend filter
  - market regime overlay

### Compare

- 3개 quarterly prototype 모두 compare selectable
- compare default preset:
  - `US Statement Coverage 100`
- compare advanced inputs:
  - preset
  - top N
  - rebalance interval
  - quality/value factor set
  - trend filter
  - market regime overlay

## naming policy

- annual strict public-candidate family와 혼동되지 않도록
  quarterly 쪽은 이름에 계속 `Strict Quarterly Prototype`을 유지한다.
- `Prototype` 라벨은 현재 기능 부족이 아니라
  promotion readiness가 아직 열리지 않았다는 의미다.

## research-only 의미

- 실행 가능하더라도 public default나 operator preset으로 승격된 상태는 아니다.
- coverage는 Phase 7 이후 크게 좋아졌지만,
  strategy-by-strategy로 active start와 factor availability가 다를 수 있다.
- 특히 manual ticker small universe에서는
  `AAPL/MSFT/GOOG` 기준 value / quality+value가 `2017-05-31`부터 active하게 열렸다.
- 반면 `US Statement Coverage 100` preset 기준으로는
  value / quality+value quarterly 둘 다 `2016-01-29`부터 active하다.

## 다음 판단 기준

- compare에서 반복적으로 안정적으로 돌아가는지
- history / prefill / interpretation이 충분히 읽히는지
- annual strict family와 비교했을 때 quarterly family가 distinct research value를 주는지
- 늦은 active start가 특정 universe에서 과도하게 자주 발생하는지
