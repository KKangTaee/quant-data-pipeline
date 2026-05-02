# Phase 12 GTAA DBC vs PDBC vs No Commodity Analysis

## 질문

- `GTAA`에서 `DBC`를 쓸 때와 `PDBC`를 쓸 때
  ETF 자체 가격 흐름은 비슷해 보이는데,
  왜 전략 결과에서는 복리와 MDD 차이가 크게 나는가
- `DBC`
- `PDBC`
- `No Commodity Sleeve`

이 3가지를 기준으로 원인을 분석한다.

## 분석 기준

- 전략: `GTAA`
- 데이터 경로: DB-backed runtime
- 옵션:
  - `top = 3`
  - `option = month_end`
  - `Minimum Price = 5`
  - `Transaction Cost = 10 bps`
  - `Benchmark = SPY`
- 주 기본 비교:
  - 시작일 `2016-01-01`
  - 종료일 `2026-04-01`
  - `Signal Interval = 2` (현재 GTAA 기본값)

추가로 왜곡을 줄이기 위해 아래도 같이 본다.

- `Signal Interval = 1`
- 공통 시작점 `2016-08-31`

## 먼저 결론

핵심 결론은 4가지다.

1. `DBC`와 `PDBC` 자체는 매우 유사하게 움직인다.
2. 그런데 `GTAA`는 연속형 점수 전략이 아니라
   **top-3 + MA filter + interval anchor** 구조라서
   작은 ETF 차이가 전략 선택 차이로 크게 증폭된다.
3. 현재 `Signal Interval = 2` 비교에서는
   `PDBC`의 짧은 usable history 때문에
   **전략 시작일과 격월 리밸런싱 달력 자체가 바뀌는 구조적 차이**가 생긴다.
4. 현재 테스트 기준으로는
   - `DBC`는 `No Commodity Sleeve`보다 좋았고
   - `PDBC`는 `No Commodity Sleeve`보다도 약했다

즉 지금 결과는
“`DBC`와 `PDBC` ETF가 아주 다른 상품이어서”만이 아니라,
**현재 GTAA 구현이 시작점과 리밸런싱 anchor에 민감한 방식이라서**
차이가 더 크게 벌어진다고 보는 것이 맞다.

## ETF 자체는 얼마나 비슷한가

DB 가격 기준으로 `DBC`와 `PDBC`를 직접 비교하면
상당히 비슷하다.

- 공통 월말 구간: `2014-11-30` ~ `2026-03-31`
- 월말 가격 상관계수: `0.9996`
- 월말 수익률 상관계수: `0.9964`
- 공통 구간 누적수익률:
  - `DBC`: `+67.7%`
  - `PDBC`: `+65.2%`

쉬운 뜻:
- ETF 두 개만 떼어놓고 보면 거의 같은 방향으로 움직인다.
- 그래서 전략 결과가 크게 다른 이유는
  **ETF 자체 차이보다 전략의 선택 구조 때문**이라고 볼 수 있다.

## GTAA 전략이 차이를 키우는 이유

현재 GTAA는 아래 구조다.

1. 월말 기준 수익률 score 계산
   - `1M`
   - `3M`
   - `6M`
   - `12M`
   평균
2. 상위 `top 3` 선택
3. 선택 자산 중 `Close >= MA200`만 편입
4. 남는 자산 수만큼 equal weight
5. 빠진 비중은 현금
6. `interval(2)`면 첫 usable row를 기준으로 격월 cadence를 탄다

즉 이 전략은
- “비슷한 ETF를 넣어도 비슷한 결과가 나오는” 구조가 아니라
- **랭킹 경계에서 한 자리만 바뀌어도 포트폴리오가 달라지는 구조**다.

## 1차 결과: 현재 기본값 (`interval = 2`, `start = 2016-01-01`)

| Config | Strategy Start | End Balance | CAGR | MDD | Sharpe | Avg Turnover | Estimated Cost Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| `PDBC` | 2016-08-31 | 18,534.70 | 6.66% | -23.10% | 0.801 | 0.417 | 304.91 |
| `DBC` | 2016-01-29 | 22,804.43 | 8.45% | -13.86% | 1.224 | 0.454 | 417.19 |
| `No Commodity Sleeve` | 2016-01-29 | 21,777.30 | 7.96% | -17.50% | 1.159 | 0.433 | 388.52 |

### 여기서 가장 중요한 포인트

`PDBC`만 전략 시작일이 `2016-08-31`로 밀려 있다.

이건 단순 표기 차이가 아니라,
**전략이 실제로 다른 달력으로 시작했다는 뜻**이다.

그리고 `interval = 2`에서는 이게 매우 중요하다.

- `DBC` 경로는 `2016-01`부터 격월 cadence
- `PDBC` 경로는 `2016-08`부터 격월 cadence

그래서 두 결과를 날짜 기준으로 직접 맞춰보면
공통 리밸런싱 날짜가 사실상 거의 없다.

- `DBC vs PDBC`
  - 공통 날짜 수: `1`
  - 즉 격월 anchor가 사실상 다른 전략처럼 동작한다

쉬운 뜻:
- 지금 `interval = 2` 비교는
  “같은 전략에서 commodity ETF만 바꾼 비교”라기보다
  **commodity ETF도 바뀌고 리밸런싱 달력도 같이 바뀐 비교**
  에 더 가깝다.

## 왜 `PDBC`만 시작이 늦어졌는가

현재 파이프라인 기준으로 `PDBC` 경로는
모든 전처리를 거친 뒤 첫 usable row가 `2016-08-31`이다.

이건 아래 요소가 겹친 결과로 보는 것이 자연스럽다.

- `PDBC`의 상대적으로 짧은 역사
- `MA200` warmup
- `12M` score warmup
- month-end 필터링
- 그 뒤 공통 날짜 intersection

즉 “ETF가 존재하기만 하면 바로 같은 시점부터 전략이 시작되는 것”이 아니다.

## 2차 결과: `interval = 1`로 cadence 차이를 줄여도 차이가 남는가

| Config | Strategy Start | End Balance | CAGR | MDD | Sharpe | Avg Turnover | Estimated Cost Total |
|---|---:|---:|---:|---:|---:|---:|---:|
| `PDBC` | 2016-08-31 | 17,898.18 | 6.28% | -26.20% | 0.580 | 0.325 | 478.85 |
| `DBC` | 2016-01-29 | 23,241.31 | 8.65% | -15.09% | 0.799 | 0.331 | 587.73 |
| `No Commodity Sleeve` | 2016-01-29 | 21,827.25 | 7.99% | -16.71% | 0.736 | 0.317 | 543.94 |

`interval = 1`에서는 월별로 날짜가 더 잘 맞기 때문에
`interval = 2`보다는 공정한 비교에 가깝다.

이 경우에도:

- `DBC vs PDBC`
  - 공통 날짜 수: `116`
  - 동일 보유 종목 수: `86`
  - 다른 보유 종목 수: `30`
  - 최종 잔고 차이: `+5,343` (`DBC` 우위)

즉 cadence 문제를 줄여도
**선택 종목 자체가 30번이나 달라졌고,
그 결과 차이도 여전히 크다.**

## 3차 결과: 공통 시작점으로 맞춘 뒤에도 차이가 남는가

공통 시작점을 `2016-08-31`로 맞추고 다시 돌리면:

### `interval = 2`

| Config | End Balance | CAGR | MDD | Sharpe | Avg Turnover |
|---|---:|---:|---:|---:|---:|
| `PDBC` | 18,534.70 | 6.66% | -23.10% | 0.801 | 0.417 |
| `DBC` | 22,385.83 | 8.79% | -19.43% | 1.089 | 0.406 |
| `No Commodity Sleeve` | 21,815.23 | 8.49% | -19.43% | 1.057 | 0.388 |

### `interval = 1`

| Config | End Balance | CAGR | MDD | Sharpe | Avg Turnover |
|---|---:|---:|---:|---:|---:|
| `PDBC` | 17,898.18 | 6.28% | -26.20% | 0.580 | 0.325 |
| `DBC` | 22,151.03 | 8.67% | -15.09% | 0.791 | 0.328 |
| `No Commodity Sleeve` | 20,844.16 | 7.98% | -16.71% | 0.727 | 0.313 |

이 결과는 중요하다.

쉬운 뜻:
- 시작일을 맞춰도 `DBC`가 여전히 더 좋다.
- 즉 차이의 전부가 “시작일 늦음” 때문은 아니다.
- **선택 종목 차이와 특정 국면에서 commodity sleeve가 어떤 방식으로 들어왔는지**
  가 실제로 성과 차이를 만든다.

## 어떤 국면에서 차이가 컸는가

현재 결과를 보면 `DBC`는 아래 구간에서 commodity sleeve 역할을 더 강하게 했다.

- `2018`
- `2021 ~ 2022`
- `2025 ~ 2026`

특히 `2021 ~ 2022`가 중요하다.

### `interval = 1` 기준 예시

`DBC`가 실제로 들어간 시점:

- `2021-02`
- `2021-04`
- `2021-05`
- `2021-06`
- `2021-07`
- `2021-09`
- `2021-10`
- `2021-11`
- `2021-12`
- `2022-01`
- `2022-02`
- `2022-03`
- `2022-04`
- `2022-05`
- `2022-06`
- `2022-07`
- `2022-08`

반면 `PDBC`는 같은 구간에서

- 비슷하게 들어간 달도 있지만
- 더 적게 들어가거나
- 어떤 달은 아예 빠진다

예를 들어:

- `2022-02-28`
  - `DBC`: `(DBC, GLD)`
  - `PDBC`: `(GLD,)`
- `2022-03-31`
  - `DBC`: `(DBC, GLD, VNQ)`
  - `PDBC`: `(GLD, VNQ)`
- `2022-06-30`
  - `DBC`: `(DBC,)`
  - `PDBC`: `()`
- `2022-07-29`
  - `DBC`: `(DBC,)`
  - `PDBC`: `()`
- `2022-08-31`
  - `DBC`: `(DBC,)`
  - `PDBC`: `()`

이건 굉장히 큰 차이다.

쉬운 뜻:
- 인플레이션/commodity 강세 구간에서
  `DBC`는 혼자라도 살아남아 포트폴리오를 지탱한 반면,
  `PDBC`는 그 자리를 충분히 대체하지 못한 달이 있었다.

## `No Commodity Sleeve`와 비교하면

현재 테스트 기준:

- `DBC`는 `No Commodity Sleeve`보다 좋다
- `PDBC`는 `No Commodity Sleeve`보다도 약하다

### `interval = 2`

- `DBC - No Commodity`
  - 최종 잔고 차이: `+1,027`
- `PDBC - No Commodity`
  - 공통 시작점으로 보면 `PDBC`가 더 약하다

### 공통 시작점 `2016-08-31`

- `DBC`는 여전히 `No Commodity Sleeve`보다 우위
- `PDBC`는 여전히 `No Commodity Sleeve`보다 약세

즉 현재 GTAA 계약에서는
**commodity sleeve를 넣는다면 DBC가 더 유의미했고,
PDBC는 대체재 역할을 제대로 못했다**고 읽는 편이 맞다.

## 왜 ETF 자체는 비슷한데 전략 결과는 이렇게 벌어지나

정리하면 원인은 3개다.

### 1. 시작점 / cadence anchor 차이

특히 `interval = 2`에서는
첫 usable row가 다르면 격월 달력이 통째로 달라진다.

이건 `DBC vs PDBC` 비교를
매우 불공정하게 만들 수 있다.

### 2. top-3 rank boundary 효과

ETF 두 개가 매우 비슷해도,
score가 top-3 경계에서 한 칸만 바뀌면
포트폴리오 편입 종목 전체가 달라질 수 있다.

### 3. MA filter + cash handling 증폭 효과

GTAA는 top-3를 뽑은 뒤
`Close >= MA200`을 통과한 자산만 편입하고,
나머지는 현금으로 둔다.

즉 commodity sleeve 하나가

- 편입되느냐
- 다른 자산을 밀어내느냐
- 통과 못해서 현금이 되느냐

가 결과를 크게 바꾼다.

## 현재 프로젝트 기준 권고

### 1. 지금 `PDBC vs DBC`를 공정하게 보려면

아래 둘 중 하나가 맞다.

- `interval = 1`로 먼저 비교
- 또는 공통 시작점 `2016-08-31` 이후로 맞춰서 비교

현재 `2016-01-01 + interval = 2` 비교는
ETF 비교이면서 동시에 cadence 비교이기도 하다.

### 2. 현재 GTAA 기본값을 무엇으로 둘지

현재 테스트 결과만 놓고 보면:

- 성과 관점: `DBC` 우위
- 세금/구조 편의 관점: `PDBC` 선호 가능
- pure strategy 결과만 보면:
  - `PDBC`는 아직 `DBC`의 대체재처럼 보이지 않는다

즉 현재 단계에선

- `PDBC`를 기본값으로 두되
- `DBC` 비교 preset을 유지하고
- 투자 판단은 둘을 나란히 보되
- 전략 성과 해석은 `DBC`를 더 강하게 참고

하는 것이 현실적이다.

### 3. `No Commodity Sleeve`도 항상 같이 볼 가치가 있다

왜냐하면 현재 결과에서

- `DBC`는 넣을 가치가 있었고
- `PDBC`는 오히려 빼는 편이 나았기 때문

즉 commodity sleeve를 무조건 넣는 것이 정답은 아니다.

## 다른 대안 후보

아래는 “지금 바로 교체 추천”이 아니라,
**후보로 추가 실험할 가치가 있는 broad commodity ETF**들이다.

### 1. `CMDY`

- 공식 페이지 기준:
  - broad basket commodity exposure
  - roll-selection 기반
  - K-1 없음
  - Expense Ratio `0.29%` / Net `0.28%`
  - Launch `2018-04-03`
  - 30-day median bid/ask spread `0.11%`
- 성격:
  - `PDBC`보다도 “K-1 없음 + broad commodity exposure” 관점에서 비교하기 쉬운 후보

### 2. `BCI`

- 공식 자료 기준:
  - Bloomberg Commodity Index Total Return 연동
  - K-1 free
  - Expense Ratio `0.26%`
  - Inception `2017-03-30`
  - Net assets 약 `$1.77B` (2025-12-31 기준 자료)
- 성격:
  - broad commodity beta를 더 단순하게 보고 싶을 때 비교 후보로 좋다

### 3. `COMT`

- 공식 페이지 기준:
  - broad commodity exposure
  - dynamic roll
  - K-1 없음
  - Expense Ratio `0.49%` / Net `0.48%`
- 성격:
  - `CMDY`보다 비용은 높지만,
    또 다른 broad commodity implementation으로 비교할 만하다

## 대안 ETF를 볼 때 체크할 것

다음 5가지는 꼭 같이 봐야 한다.

1. K-1 여부
2. broad commodity인지, sector 편향이 큰지
3. roll methodology
4. 수수료
5. 실제 GTAA top-3/MA200 구조 안에서 편입이 어떻게 달라지는지

즉 ETF 설명만 보고 고르면 안 되고,
**현재 GTAA 로직 안에 넣었을 때 어떤 달에 top-3로 들어오는지**
까지 봐야 한다.

## 최종 판단

현재 프로젝트/데이터/GTAA 구현 기준으로는:

- `DBC`와 `PDBC`는 ETF 자체로는 매우 비슷하다
- 하지만 GTAA 안에서는
  - 시작점 차이
  - 리밸런싱 anchor 차이
  - top-3 경계 효과
  - MA filter / cash 효과
  때문에 결과 차이가 크게 증폭된다
- 현재 테스트 결과는
  - `DBC` > `No Commodity Sleeve` > `PDBC`
  쪽에 가깝다

따라서 지금 단계의 가장 실무적인 해석은:

- `PDBC`를 세금/구조 편의 때문에 후보로 둘 수는 있다
- 하지만 **GTAA 성과상으로는 아직 `DBC`의 동일 대체재라고 보긴 어렵다**
- 공정한 비교를 위해서는
  - 공통 시작점
  - `interval = 1`
  - 동일 cost contract
  로 한 번 더 보는 것이 좋다

## Sources

- Invesco commodity lineup and current fee table:
  - https://www.invesco.com/us/en/solutions/invesco-etfs/commodity-investing.html
- Invesco commodity digest with DBC/PDBC common-inception performance context:
  - https://www.invesco.com/us-rest/contentdetail?contentId=e7b43972-ca85-4aad-9e44-9e3971ccc0ed&dnsName=us
- DBC product description:
  - https://www.invesco.com/us-rest/contentdetail?contentId=1fd207c649400410VgnVCM10000046f1bf0aRCRD&dnsName=us
- PDBC product / fact sheet:
  - https://www.invesco.com/us-rest/contentdetail?contentId=03b8588c0971b410VgnVCM100000c2f1bf0aRCRD
  - https://www.invesco.com/content/dam/invesco/us/en/product-documents/etf/fact-sheet/pdbc-invesco-optimum-yield-diversified-commodity-strategy-no-k-1-etf-fact-sheet.pdf
- CMDY official page:
  - https://www.blackrock.com/us/individual/products/292741/ishares-bloomberg-roll-select-commodity-strategy-etf-fund
- COMT official page:
  - https://www.blackrock.com/us/individual/products/270319/ishares-commodity-etf
- BCI fact sheet:
  - https://www.abrdn.com/docs?editionId=e08e3839-182a-450f-b524-301a91e9177a
