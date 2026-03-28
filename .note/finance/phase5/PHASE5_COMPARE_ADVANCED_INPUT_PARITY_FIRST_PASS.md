# Phase 5 Compare Advanced-Input Parity First Pass

## 목적

- compare 화면에서 strict factor 전략도 single 화면과 비슷한 수준의 strategy-specific 조절성을 갖게 한다.

## 이번 first pass에서 열린 입력

### Quality Snapshot (Strict Annual)

- preset
- `top_n`
- `rebalance_interval`
- quality factor set
- trend filter on/off
- trend filter window

### Value Snapshot (Strict Annual)

- preset
- `top_n`
- `rebalance_interval`
- value factor set
- trend filter on/off
- trend filter window

### Quality + Value Snapshot (Strict Annual)

- preset
- `top_n`
- `rebalance_interval`
- quality factor set
- value factor set
- trend filter on/off
- trend filter window

## 공통 입력과 분리 원칙

- compare 공통:
  - `timeframe`
  - `option`
- 전략별:
  - preset / universe
  - factor set
  - `top_n`
  - `rebalance_interval`
  - overlay input

## runtime 영향

- compare runner는 이제 strict factor 전략에서
  override된 `preset_name`, `tickers`, `universe_mode`를 실제 실행 입력으로 넘긴다.
- 즉 compare에서도
  `US Statement Coverage 100 / 300 / 500 / 1000 / Big Tech Strict Trial`
  같은 managed preset을 전략별로 다르게 줄 수 있다.

## 의도적 제한

- 이번 first pass는 preset 기반 compare parity에 집중한다
- compare에서 strict family manual ticker mode까지 바로 열지는 않았다
- 이유:
  - large-universe strict compare는 preset research가 더 흔한 사용 경로이기 때문이다

## 결론

- compare strict factor 전략은 이제
  single 화면 대비 부족했던 strategy-specific advanced input gap을 first-pass 수준에서 메웠다.
