# Phase 4 Strict Family Comparison Evaluation

> 참고:
> 이 문서는 strict family의 first-pass 비교 평가를 기록한 문서다.
> 이후 closeout 단계에서 `Value Snapshot (Strict Annual)`은
> historical share-count fallback과 value-factor refresh를 거치며
> `2016-01-29`부터 active하게 동작하도록 회복되었다.
> 최신 closeout 상태는
> `.note/finance/phase4/PHASE4_COVERAGE1000_AND_VALUE_STRICT_CLOSEOUT.md`
> 를 기준으로 보는 편이 정확하다.

## 목적

- `Quality Snapshot (Strict Annual)`과 `Value Snapshot (Strict Annual)`을
  현재 public strict annual family 기준으로 같은 조건에서 비교한다.
- strict annual family 안에서
  어떤 전략이 지금 더 primary public candidate에 가까운지 판단한다.

참고:
- 이후 strict annual quality 기본 factor set은
  coverage-first 방향으로 한 번 더 갱신되었다.
- 현재 public default benchmark는
  `.note/finance/phase4/PHASE4_STRICT_ANNUAL_QUALITY_FACTOR_SET_REFRESH_FIRST_PASS.md`
  를 함께 보는 편이 맞다.

## 비교 조건

- 기간:
  - `2016-01-01 ~ 2026-03-20`
- cadence:
  - `month_end`
- selection:
  - `top_n = 10`
- universe:
  - `US Statement Coverage 100`
  - `US Statement Coverage 300`

## 비교 결과

| Strategy | Universe | Elapsed | First Active | Active Rows | End Balance | CAGR | Sharpe | Max Drawdown |
| --- | --- | ---: | --- | ---: | ---: | ---: | ---: | ---: |
| Quality Snapshot (Strict Annual) | US Statement Coverage 100 | `3.321s` | `2016-01-29` | `124` | `79295.2` | `0.226587` | `1.121310` | `-0.388411` |
| Quality Snapshot (Strict Annual) | US Statement Coverage 300 | `9.264s` | `2016-01-29` | `124` | `73778.4` | `0.217893` | `1.135933` | `-0.357827` |
| Value Snapshot (Strict Annual) | US Statement Coverage 100 | `3.197s` | `2021-08-31` | `57` | `20228.2` | `0.071960` | `0.582769` | `-0.288070` |
| Value Snapshot (Strict Annual) | US Statement Coverage 300 | `9.080s` | `2021-08-31` | `57` | `20931.1` | `0.075578` | `0.562940` | `-0.277771` |

## 해석

### 1. 현재 strict annual family의 주력은 quality 쪽이다

- quality strict는 `2016-01-29`부터 바로 active하게 동작한다.
- `US Statement Coverage 100/300` 모두 `124` monthly row를 사용한다.
- value strict보다 activation이 훨씬 빠르고, 현재 성과/지표도 더 안정적으로 나온다.

### 2. value strict는 아직 secondary public candidate에 가깝다

- value strict는 현재 `2021-08-31`부터만 active하다.
- active row도 `57`개로 quality strict보다 짧다.
- 이는 valuation 계열이
  - statement shadow coverage
  - shares fallback
  - price matching
  영향을 더 많이 받기 때문이다.

### 3. runtime cost는 usable but still heavier 상태다

- strict annual fast path는 이미 raw statement rebuild 반복을 없앴다.
- 그래도 `Coverage 300`에서는 약 `9초` 수준이므로,
  compare나 repeated research에는 체감 비용이 남아 있다.

## 현재 판단

- `Quality Snapshot (Strict Annual)`:
  - strict annual family의 primary public candidate
- `Value Snapshot (Strict Annual)`:
  - secondary candidate
  - research/validation 성격이 더 강함

## 다음 의미

- broad vs strict 설명에서는
  `Quality Snapshot (Strict Annual)`을 strict annual 대표 전략으로 설명하는 편이 맞다.
- strict family 확장은
  `Quality -> Value -> Multi-Factor`
  순으로 가는 것이 자연스럽다.
