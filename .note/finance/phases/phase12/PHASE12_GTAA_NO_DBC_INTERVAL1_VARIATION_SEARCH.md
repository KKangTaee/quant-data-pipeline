# Phase 12 GTAA No-DBC Interval-1 Variation Search

## 질문

- `DBC`를 완전히 제외한 상태에서
- `GTAA` universe를 다른 심볼들로 수정하면
- 더 나은 `CAGR` / `MDD` 조합을 만들 수 있는가

이번 search는
`Signal Interval = 1`로 고정하고
`DBC` 없이 돌아가는 10개 변형을 비교한 결과다.

## 이번 작업에서 실제로 한 것

1. `DBC`를 제외한 GTAA 변형 10개를 구성했다.
2. 사용할 후보 ETF의 DB 커버리지를 확인했다.
3. 같은 GTAA 계약으로 10개 백테스트를 돌렸다.
4. 시작일 차이를 줄이기 위해 공통 시작점 `2020-01-31` 비교도 같이 봤다.

## 사용한 후보 축

- `PDBC`
- `COMT`
- `CMDY`
- `BCI`
- `No Commodity Sleeve`
- `QUAL`
- `USMV`

쉬운 뜻:
- `PDBC`, `COMT`, `CMDY`, `BCI`는 `DBC`를 대신할 commodity sleeve 후보
- `QUAL`, `USMV`는 commodity replacement가 아니라
  전체 GTAA universe를 더 실전형으로 만드는 개선 후보

## DB 커버리지 확인

이번 search에 사용한 심볼들은 모두 DB에서 usable 상태였다.

- `PDBC`
  - latest `2026-04-01`
- `COMT`
  - latest `2026-04-01`
- `CMDY`
  - latest `2026-04-01`
- `BCI`
  - latest `2026-04-01`
- `QUAL`
  - latest `2026-04-01`
- `USMV`
  - latest `2026-04-01`

즉 이번 비교는
데이터 부족 때문에 왜곡된 테스트가 아니다.

## 테스트 계약

- 전략: `GTAA`
- `Signal Interval = 1`
- `month_end`
- `top = 3`
- `Minimum Price = 5`
- `Transaction Cost = 10 bps`
- `Benchmark = SPY`

## 10개 테스트 구성

1. `PDBC Base`
2. `No Commodity`
3. `COMT Base`
4. `CMDY Base`
5. `BCI Base`
6. `PDBC + USMV`
7. `PDBC + QUAL + USMV`
8. `COMT + USMV`
9. `COMT + QUAL + USMV`
10. `No Commodity + QUAL + USMV`

## 1차 결과: 현재 전체 구간 기준

| Config | Universe Count | Strategy Start | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| `PDBC Base` | 12 | 2016-08-31 | 17,898.18 | 6.28% | -26.20% | 0.580 |
| `No Commodity` | 11 | 2016-01-29 | 21,827.25 | 7.99% | -16.71% | 0.736 |
| `COMT Base` | 12 | 2017-10-31 | 17,149.43 | 6.63% | -19.65% | 0.598 |
| `CMDY Base` | 12 | 2020-01-31 | 16,315.00 | 8.28% | -20.55% | 0.722 |
| `BCI Base` | 12 | 2019-01-31 | 16,422.30 | 7.19% | -22.03% | 0.654 |
| `PDBC + USMV` | 13 | 2016-08-31 | 18,447.69 | 6.61% | -27.56% | 0.622 |
| `PDBC + QUAL + USMV` | 14 | 2016-08-31 | 18,913.34 | 6.89% | -28.47% | 0.624 |
| `COMT + USMV` | 13 | 2017-10-31 | 17,640.66 | 6.99% | -21.21% | 0.642 |
| `COMT + QUAL + USMV` | 14 | 2017-10-31 | 19,320.66 | 8.16% | -16.98% | 0.711 |
| `No Commodity + QUAL + USMV` | 13 | 2016-01-29 | 23,307.68 | 8.69% | -16.17% | 0.795 |

## 먼저 보이는 결론

현재 전체 구간 기준으로도:

- `No Commodity + QUAL + USMV`
  가 가장 좋다
- `COMT + QUAL + USMV`
  가 그 다음으로 의미 있다
- `PDBC`는 추가 개선을 붙여도 여전히 약하다

하지만 이 결과는 후보 ETF inception 차이가 섞여 있으므로
공통 시작점 비교가 더 중요하다.

## 2차 결과: 공통 시작점 `2020-01-31`

| Config | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|
| `PDBC Base` | 15,989.70 | 7.93% | -26.05% | 0.687 |
| `No Commodity` | 18,657.06 | 10.67% | -15.88% | 0.907 |
| `COMT Base` | 17,322.34 | 9.34% | -19.58% | 0.807 |
| `CMDY Base` | 16,315.00 | 8.28% | -20.55% | 0.722 |
| `BCI Base` | 15,942.23 | 7.88% | -22.03% | 0.687 |
| `PDBC + USMV` | 16,091.97 | 8.04% | -27.63% | 0.693 |
| `PDBC + QUAL + USMV` | 16,760.28 | 8.76% | -28.47% | 0.726 |
| `COMT + USMV` | 17,433.01 | 9.46% | -21.21% | 0.812 |
| `COMT + QUAL + USMV` | 19,358.12 | 11.33% | -16.98% | 0.929 |
| `No Commodity + QUAL + USMV` | 19,955.19 | 11.88% | -16.17% | 0.977 |

## 공통 시작점 기준 핵심 결론

### 1. `DBC` 없이 가장 좋은 조합은 `No Commodity + QUAL + USMV`

- CAGR `11.88%`
- MDD `-16.17%`
- Sharpe `0.977`

쉬운 뜻:
- `DBC` 없이도 꽤 좋은 GTAA 계약은 만들 수 있다.
- 그런데 그 방향은
  “새 commodity ETF를 찾는 것”보다
  **commodity sleeve를 빼고 quality + low-vol sleeve를 넣는 것**
  에 더 가깝다.

### 2. commodity를 유지해야 한다면 `COMT + QUAL + USMV`가 가장 낫다

- CAGR `11.33%`
- MDD `-16.98%`

쉬운 뜻:
- `DBC`를 쓸 수 없지만 commodity exposure는 유지하고 싶다면
  현재 후보 중에서는 `COMT`가 가장 현실적이다.
- 그리고 `COMT` 단독보다
  `QUAL + USMV`를 같이 붙인 조합이 훨씬 낫다.

### 3. `PDBC`는 여전히 약하다

`PDBC` 개선 조합도 봤지만:

- `PDBC Base`
- `PDBC + USMV`
- `PDBC + QUAL + USMV`

모두 공통 시작점 기준으로
`No Commodity`보다 약했다.

즉 현재 GTAA 구조에서는
`PDBC`가 핵심 후보가 되긴 어렵다.

## 왜 `QUAL + USMV`가 잘 들었는가

selection count를 보면 이유가 드러난다.

### `No Commodity`

- `MTUM`: `32`
- `IWM`: `19`
- `IWN`: `20`
- `GLD`: `45`

### `No Commodity + QUAL + USMV`

- `QUAL`: `22`
- `USMV`: `5`
- `MTUM`: `30`
- `IWM`: `18`
- `IWN`: `19`
- `GLD`: `42`

쉬운 뜻:
- `QUAL`이 실제로 자주 top-3 안에 들어왔다.
- `USMV`는 횟수는 많지 않지만
  필요한 구간에서 들어오며 drawdown을 완화한 것으로 보인다.

### `COMT + QUAL + USMV`

- `QUAL`: `20`
- `USMV`: `4`
- `COMT`: `15`

즉 `COMT`를 완전히 대체하는 게 아니라
`QUAL`, `USMV`가 같이 들어오며
조합을 더 안정적으로 만든다.

## 이번 결과에서 무엇을 배울 수 있나

### A. `DBC`를 빼면 commodity 대체재만 찾는 건 충분하지 않다

현재 결과는:

- `COMT`
- `CMDY`
- `BCI`
- `PDBC`

중 무엇을 넣느냐보다,
**`QUAL + USMV`를 universe에 추가하느냐**
가 더 큰 차이를 만들었다.

### B. `No Commodity`가 계속 강한 baseline이다

공통 시작점 기준:

- `No Commodity`
  - `PDBC`, `COMT`, `CMDY`, `BCI` base보다 다 좋다

즉 `DBC`를 제거해야 한다면
먼저 serious baseline으로 봐야 하는 건
**`No Commodity` 자체**다.

### C. 그래도 commodity를 유지하고 싶다면 `COMT`

`COMT Base`는 완벽하지 않지만
현재 no-DBC commodity 후보 중에서는 가장 낫다.

그리고 실전형 개선 방향은:

- `COMT` 단독이 아니라
- `COMT + QUAL + USMV`

이다.

## 현재 기준 추천 순서

### `DBC` 없이 가장 실전적으로 좋아 보이는 순서

1. `No Commodity + QUAL + USMV`
2. `COMT + QUAL + USMV`
3. `No Commodity`
4. `COMT + USMV`
5. `COMT Base`
6. `CMDY Base`
7. `PDBC + QUAL + USMV`
8. `PDBC + USMV`
9. `PDBC Base`
10. `BCI Base`

## GTAA에서 무엇을 수정하면 더 좋아질 가능성이 있는가

이번 no-DBC search 기준으로는:

### 1. `PDBC` 중심 사고를 버리는 게 좋다

- `PDBC`를 살리려고 여러 조합을 붙여도
  결과가 충분히 좋아지지 않았다.

### 2. `QUAL + USMV` 추가가 더 중요하다

- commodity를 무엇으로 대체하느냐보다
  quality / low-vol sleeve를 universe에 추가하는 것이
  더 큰 개선으로 이어졌다.

### 3. commodity를 유지하려면 `COMT`를 우선 검토

- `DBC`를 못 쓰는 상황에서
  가장 실무적인 commodity replacement는 `COMT`
- 다만 단독보다
  `COMT + QUAL + USMV`
  조합이 훨씬 낫다.

## 가장 실무적인 권고

### 선택지 1. commodity를 빼도 된다면

- `GTAA Universe (No Commodity + QUAL + USMV)`

이게 현재 no-DBC 최고의 후보다.

### 선택지 2. commodity를 꼭 유지해야 한다면

- `GTAA Universe (COMT + QUAL + USMV)`

이게 현재 no-DBC commodity 유지 버전의 최선이다.

## 다음 추천 작업

1. preset 후보 추가
   - `GTAA Universe (No Commodity + QUAL + USMV)`
   - `GTAA Universe (COMT + QUAL + USMV)`
2. 2020 이후 inflation / post-rate-hike 구간만 따로 잘라 비교
3. `QUAL`, `USMV`가 어떤 달에 어떤 ETF를 밀어냈는지 상세 분석

## 최종 판단

이번 10개 search 기준으로:

- `DBC`를 제외하면
  단순 commodity 대체 ETF 찾기보다
  **universe 구조 자체를 quality + low-vol 쪽으로 보강하는 것**
  이 더 유효했다.

즉 현재 no-DBC GTAA의 가장 현실적인 개선 방향은:

1. `No Commodity + QUAL + USMV`
2. commodity를 유지해야 하면 `COMT + QUAL + USMV`

이다.
