# Phase 12 GTAA Commodity Alternative Candidate Analysis

## 질문

- `GTAA`에서 commodity sleeve 후보를 넓혀서 비교할 수 있는가
- `DBC`
- `PDBC`
- `No Commodity Sleeve`
- `CMDY`
- `BCI`
- `COMT`

이 6가지를 같은 GTAA 계약으로 비교해서:

1. 후보 ETF 기본 정보
2. 실제 DB 커버리지 확보 여부
3. 백테스트 기준 `CAGR`, `MDD`
4. 실전적으로 어떤 후보가 더 가능성이 있는지

를 정리한다.

## 이번 작업에서 실제로 한 것

1. 후보 ETF 공식 자료를 확인했다.
2. DB에 없는 후보는 targeted `Daily Market Update`로 backfill했다.
3. 같은 GTAA 계약에서 후보별 결과를 다시 돌렸다.
4. inception 차이 왜곡을 줄이기 위해 공통 시작점 비교도 했다.

## 후보 ETF 기본 정보

### `DBC`

- Invesco DB Commodity Index Tracking Fund
- Invesco 자료 기준 fund inception:
  - `2006-02-03`
- Invesco 2026 commodity digest 기준:
  - `Net Expense Ratio` 약 `0.84%`
- 특징:
  - 긴 역사
  - broad commodity exposure
  - 현재 프로젝트 GTAA에서 가장 오래 검증된 commodity sleeve

### `PDBC`

- Invesco Optimum Yield Diversified Commodity Strategy No K-1 ETF
- Invesco 자료 기준 inception:
  - `2014-11-07`
- Invesco 자료 기준:
  - `Net Expense Ratio` 약 `0.59%`
- 특징:
  - `No K-1`
  - 구조상 실무 편의성은 좋지만,
    현재 GTAA 안에서는 `DBC` 대체재처럼 동작하지 않았다

### `CMDY`

- iShares Bloomberg Roll Select Commodity Strategy ETF
- BlackRock fact sheet 기준 launch:
  - `2018-04-03`
- Expense Ratio:
  - `0.29%`
- Net Expense Ratio:
  - `0.28%`
- 특징:
  - broad commodity exposure
  - roll cost를 줄이려는 구조
  - `K-1` 없음

### `BCI`

- abrdn Bloomberg All Commodity Strategy K-1 Free ETF
- abrdn fact sheet 기준 inception:
  - `2017-03-30`
- Net Expense Ratio:
  - `0.26%`
- 특징:
  - Bloomberg Commodity Index TR 기반
  - `K-1 Free`
  - 비용은 후보 중 가장 낮은 편

### `COMT`

- iShares GSCI Commodity Dynamic Roll Strategy ETF
- BlackRock 자료 기준:
  - broad commodity exposure
  - enhanced roll selection
- Expense Ratio:
  - `0.49%`
- Net Expense Ratio:
  - `0.48%`
- 특징:
  - `K-1` 없음
  - broad commodity exposure
  - 현재 대안 후보 중에서는 GTAA 안에서 가장 무난한 편이었다

## DB 커버리지 확보

이번 비교 전에 targeted backfill을 실행했다.

- `CMDY`
  - daily market update success
  - DB latest: `2026-04-01`
  - row count: `2009`
- `BCI`
  - daily market update success
  - DB latest: `2026-04-01`
  - row count: `2263`
- `COMT`
  - daily market update success
  - DB latest: `2026-04-01`
  - row count: `2576`

즉 이번 비교는
“DB에 후보가 없어서 못 돌린 상태”가 아니라,
실제로 DB에 후보를 채운 뒤 비교한 결과다.

## 백테스트 계약

- 전략: `GTAA`
- 데이터 경로: DB-backed runtime
- 옵션:
  - `top = 3`
  - `option = month_end`
  - `Minimum Price = 5`
  - `Transaction Cost = 10 bps`
  - `Benchmark = SPY`

비교는 두 단계로 봤다.

1. 현재 실사용에 가까운 비교
   - 시작일 `2016-01-01`
   - 종료일 `2026-04-01`
   - `Signal Interval = 2`
   - `Signal Interval = 1`
2. 공통 시작점 비교
   - 시작일 `2020-01-31`
   - 후보 모두가 전략적으로 usable한 시점 이후

## 1차 결과: 현재 계약 그대로 비교

### `Signal Interval = 2`

| Config | Strategy Start | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|---:|
| `DBC` | 2016-01-29 | 22,804.43 | 8.45% | -13.86% | 1.224 |
| `PDBC` | 2016-08-31 | 18,534.70 | 6.66% | -23.10% | 0.801 |
| `CMDY` | 2020-01-31 | 16,220.88 | 8.18% | -15.75% | 1.153 |
| `BCI` | 2019-01-31 | 17,249.60 | 7.92% | -16.18% | 1.190 |
| `COMT` | 2017-10-31 | 17,819.46 | 7.12% | -19.43% | 0.860 |
| `No Commodity Sleeve` | 2016-01-29 | 21,777.30 | 7.96% | -17.50% | 1.159 |

### 해석

- raw 결과만 보면 `DBC`가 가장 좋다.
- 대안 후보 중에서는:
  - `BCI`, `CMDY`가 상대적으로 괜찮아 보이지만
  - 공통 시작점이 아니므로 그대로 단정하면 안 된다.
- `PDBC`는 여전히 약하다.

### `Signal Interval = 1`

| Config | Strategy Start | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|---:|
| `DBC` | 2016-01-29 | 23,241.31 | 8.65% | -15.09% | 0.799 |
| `PDBC` | 2016-08-31 | 17,898.18 | 6.28% | -26.20% | 0.580 |
| `CMDY` | 2020-01-31 | 16,315.00 | 8.28% | -20.55% | 0.722 |
| `BCI` | 2019-01-31 | 16,422.30 | 7.19% | -22.03% | 0.654 |
| `COMT` | 2017-10-31 | 17,149.43 | 6.63% | -19.65% | 0.598 |
| `No Commodity Sleeve` | 2016-01-29 | 21,827.25 | 7.99% | -16.71% | 0.736 |

### 해석

- cadence 왜곡을 줄여도 `DBC`가 가장 좋다.
- 대안 후보 중에서는 `CMDY`가 CAGR은 가장 높지만,
  `MDD`와 Sharpe를 같이 보면 아주 강한 우위라고 보긴 어렵다.
- `PDBC`는 여전히 가장 약한 쪽이다.

## 2차 결과: 공통 시작점 `2020-01-31`로 맞춘 비교

이 비교가 더 공정하다.

이제 모든 후보가 같은 시작점에서 출발하므로,
“늦게 상장돼서 전략 시작이 늦었다”는 왜곡이 줄어든다.

### `Signal Interval = 2`

| Config | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|
| `DBC` | 18,075.39 | 10.10% | -13.86% | 1.369 |
| `PDBC` | 15,211.79 | 7.06% | -21.25% | 0.936 |
| `CMDY` | 16,220.88 | 8.18% | -15.75% | 1.153 |
| `BCI` | 15,983.67 | 7.92% | -16.18% | 1.121 |
| `COMT` | 16,150.36 | 8.11% | -16.03% | 1.125 |
| `No Commodity Sleeve` | 16,591.43 | 8.58% | -17.50% | 1.134 |

### `Signal Interval = 1`

| Config | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|
| `DBC` | 19,695.56 | 11.64% | -10.01% | 0.990 |
| `PDBC` | 15,989.70 | 7.93% | -26.05% | 0.687 |
| `CMDY` | 16,315.00 | 8.28% | -20.55% | 0.722 |
| `BCI` | 15,942.23 | 7.88% | -22.03% | 0.687 |
| `COMT` | 17,322.34 | 9.34% | -19.58% | 0.807 |
| `No Commodity Sleeve` | 18,657.06 | 10.67% | -15.88% | 0.907 |

## 공통 시작점 기준 핵심 해석

### 1. `DBC`는 여전히 가장 강하다

- `CAGR`
- `MDD`
- Sharpe

3개를 같이 봐도 `DBC`가 가장 좋다.

즉 현재 GTAA에서는
commodity sleeve를 유지한다면
`DBC`가 가장 전략 친화적으로 작동했다.

### 2. `PDBC`는 여전히 약하다

- `CAGR` 낮음
- `MDD` 더 나쁨
- Sharpe도 약함

즉 `PDBC`는 현재 GTAA 구조에서
`DBC` 대체재로 보긴 어렵다.

### 3. 대안 후보 중 가장 나은 건 `COMT`, 그 다음은 `CMDY`

공통 시작점 `interval = 1` 기준:

- `COMT`
  - End Balance `17,322`
  - CAGR `9.34%`
  - MDD `-19.58%`
- `CMDY`
  - End Balance `16,315`
  - CAGR `8.28%`
  - MDD `-20.55%`
- `BCI`
  - End Balance `15,942`
  - CAGR `7.88%`
  - MDD `-22.03%`

즉 대안 후보 순서는 현재 기준으로:

1. `COMT`
2. `CMDY`
3. `BCI`

에 가깝다.

### 4. 하지만 더 중요한 결론은 `No Commodity Sleeve`가 대안 후보들보다 강하다는 점이다

공통 시작점 기준:

- `No Commodity Sleeve`
  - `COMT`, `CMDY`, `BCI`, `PDBC`보다 좋다
- 즉 현재 GTAA에서는
  **`DBC`가 아니면 오히려 commodity sleeve를 빼는 편이 더 나았다**

이건 꽤 중요한 결론이다.

## 왜 이런 결과가 나왔는가

현재 GTAA는

1. top-3 score 선택
2. `MA200` filter
3. 통과 못 하면 cash

구조다.

즉 commodity ETF 후보는
ETF 자체 성격만 중요한 게 아니라:

- top-3 안에 얼마나 자주 들어오는지
- `MA200` 위에 얼마나 자주 남는지
- 다른 risk asset을 얼마나 밀어내는지

가 훨씬 중요하다.

이번 공통 시작점 비교에서 commodity sleeve 편입 빈도는 대략 이랬다.

### `interval = 1`

- `DBC`
  - 편입 `21`개월
- `COMT`
  - 편입 `18`개월
- `CMDY`
  - 편입 `17`개월
- `BCI`
  - 편입 `16`개월
- `PDBC`
  - 편입 `13`개월

쉬운 뜻:
- `DBC`는 commodity가 필요한 구간에서 더 자주 살아남았다.
- `PDBC`는 가장 덜 살아남았다.
- `COMT`와 `CMDY`는 중간 정도였다.

## 실무적으로 어떻게 읽는 것이 좋은가

### A. 성과 우선이면

- 지금 기준으로는 `DBC` 유지가 맞다.

### B. `DBC`를 구조/세무 이유로 피하고 싶다면

- 현재 GTAA 대체 후보로는
  - `COMT`
  - `CMDY`
  순서로 먼저 볼 가치가 있다.

### C. 하지만 현재 결과만 보면

- `COMT`
- `CMDY`
- `BCI`
- `PDBC`

모두 `DBC`를 이기지 못했고,
심지어 공통 시작점 기준으로는
**`No Commodity Sleeve`보다도 약했다.**

즉 지금 단계에서 가장 현실적인 권고는:

1. `DBC` 유지
2. `DBC`가 싫다면 `COMT`, `CMDY`를 추가 실험
3. 그래도 확신이 없으면 `No Commodity Sleeve`도 serious baseline으로 같이 두기

## 현재 기준 추천 순서

### 전략 결과만 기준

1. `DBC`
2. `No Commodity Sleeve`
3. `COMT`
4. `CMDY`
5. `BCI`
6. `PDBC`

### K-1 회피 / 구조 편의까지 감안한 후보 순서

1. `COMT`
2. `CMDY`
3. `BCI`
4. `PDBC`

단,
이건 어디까지나 `DBC`를 빼고 봤을 때의 순서다.

## 다음으로 해볼 가치가 있는 것

1. `COMT`와 `CMDY`를 preset으로 추가해서 UI 수준에서 비교 가능하게 만들기
2. `Signal Interval = 1`을 GTAA commodity sleeve 공정 비교 기본값으로 둘지 검토하기
3. 2021~2022 inflation regime만 따로 잘라서 sleeve contribution 분석하기
4. `No Commodity Sleeve`를 단순 비교용이 아니라 공식 baseline으로 승격할지 검토하기

## Sources

- Invesco commodity lineup / current fee table:
  - https://www.invesco.com/us/en/solutions/invesco-etfs/commodity-investing.html
- Invesco commodity digest January 2026:
  - https://www.invesco.com/us-rest/contentdetail?contentId=e7b43972-ca85-4aad-9e44-9e3971ccc0ed
- BlackRock CMDY official page:
  - https://www.blackrock.com/us/partner/products/292741/ishares-bloomberg-roll-select-commodity-strategy-etf
- BlackRock CMDY fact sheet:
  - https://www.blackrock.com/us/individual/literature/fact-sheet/cmdy-ishares-bloomberg-roll-select-commodity-strategy-etf-fund-fact-sheet-en-us.pdf
- BlackRock COMT official page:
  - https://www.blackrock.com/us/individual/products/270319/ishares-commodity-etf
- abrdn BCI fact sheet:
  - https://www.abrdn.com/docs?editionid=e08e3839-182a-450f-b524-301a91e9177a
