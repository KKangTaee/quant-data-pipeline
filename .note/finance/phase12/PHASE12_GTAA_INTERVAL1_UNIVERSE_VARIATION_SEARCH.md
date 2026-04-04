# Phase 12 GTAA Interval-1 Universe Variation Search

## 질문

- `Signal Interval = 1`로 고정했을 때
- 현재 `GTAA` universe를 조금씩 변형하면
- `CAGR`는 더 높고
- `MDD`는 더 낮은

더 실전적인 포트폴리오 계약을 찾을 수 있는가

## 이번 작업에서 실제로 한 것

1. 현재 `GTAA` universe를 기준으로 10개 변형 계약을 만들었다.
2. 새 후보 ETF 중 DB에 히스토리가 부족한 심볼은 targeted `Daily Market Update`로 backfill했다.
3. 같은 GTAA 계약에서 `Signal Interval = 1`로 10개 백테스트를 돌렸다.
4. 결과를 기준으로
   - 무엇이 실제로 좋아졌는지
   - GTAA에서 어떤 수정이 의미 있는지
   를 정리했다.

## 새로 추가해서 본 ETF

이번 search에서 새로 넣은 후보는 아래 4개다.

- `TIP`
  - inflation-linked bond / TIPS ETF
- `QUAL`
  - quality factor ETF
- `USMV`
  - minimum volatility ETF
- `VEA`
  - developed ex-US broad equity ETF

쉬운 뜻:
- `TIP`은 inflation / real-rate 방어 역할 후보
- `QUAL`은 quality equity sleeve 후보
- `USMV`는 drawdown 완화 후보
- `VEA`는 국제주식 노출 broaden 후보

## 데이터 수집

backfill 결과:

- `TIP`
  - success
  - row count `4086`
- `QUAL`
  - success
  - row count `3196`
- `USMV`
  - success
  - row count `3632`
- `VEA`
  - success
  - row count `4086`

즉 이번 search는
“후보가 DB에 없어서 못 돌린 상태”가 아니라,
실제로 DB를 채운 뒤 비교한 결과다.

## 테스트 계약

- 전략: `GTAA`
- 데이터 경로: DB-backed runtime
- `Signal Interval = 1`
- 시작일: `2016-01-01`
- 종료일: `2026-04-01`
- `top = 3`
- `option = month_end`
- `Minimum Price = 5`
- `Transaction Cost = 10 bps`
- `Benchmark = SPY`

## 10개 테스트 구성

1. `Current PDBC`
   - 현재 기본 GTAA universe
2. `DBC Base`
   - commodity sleeve만 `DBC`
3. `No Commodity`
   - commodity sleeve 제거
4. `DBC + TIP`
   - `DBC` base에 `TIP` 추가
5. `DBC + QUAL`
   - `DBC` base에 `QUAL` 추가
6. `DBC + USMV`
   - `DBC` base에 `USMV` 추가
7. `DBC + VEA`
   - `DBC` base에 `VEA` 추가
8. `DBC + TIP + QUAL`
   - `DBC` base에 `TIP`, `QUAL` 추가
9. `DBC + TIP + USMV`
   - `DBC` base에 `TIP`, `USMV` 추가
10. `DBC + QUAL + USMV`
   - `DBC` base에 `QUAL`, `USMV` 추가

## 결과 요약

| Config | Universe Count | Strategy Start | End Balance | CAGR | MDD | Sharpe |
|---|---:|---:|---:|---:|---:|---:|
| `Current PDBC` | 12 | 2016-08-31 | 17,898.18 | 6.28% | -26.20% | 0.580 |
| `DBC Base` | 12 | 2016-01-29 | 23,241.31 | 8.65% | -15.09% | 0.799 |
| `No Commodity` | 11 | 2016-01-29 | 21,827.25 | 7.99% | -16.71% | 0.736 |
| `DBC + TIP` | 13 | 2016-01-29 | 23,867.58 | 8.94% | -15.09% | 0.822 |
| `DBC + QUAL` | 13 | 2016-01-29 | 23,474.80 | 8.76% | -17.07% | 0.801 |
| `DBC + USMV` | 13 | 2016-01-29 | 23,393.28 | 8.73% | -13.01% | 0.822 |
| `DBC + VEA` | 13 | 2016-01-29 | 23,299.97 | 8.68% | -15.09% | 0.782 |
| `DBC + TIP + QUAL` | 14 | 2016-01-29 | 24,107.35 | 9.05% | -17.07% | 0.824 |
| `DBC + TIP + USMV` | 14 | 2016-01-29 | 23,066.38 | 8.58% | -13.01% | 0.810 |
| `DBC + QUAL + USMV` | 14 | 2016-01-29 | 23,958.79 | 8.98% | -14.54% | 0.829 |

## 먼저 결론

현재 10개 비교 기준으로는 아래 3개가 중요하다.

1. `DBC Base`가 `Current PDBC`보다 훨씬 낫다.
2. `DBC + USMV`는 `DBC Base`보다
   - `CAGR`는 약간 더 높고
   - `MDD`는 더 낮다.
3. `DBC + QUAL + USMV`는 `DBC Base`보다
   - `CAGR`도 더 높고
   - `MDD`도 더 낮다.

즉 이번 search에서는
**`USMV` 추가가 가장 실질적인 개선 방향**으로 보였고,
그 다음은 `QUAL`을 함께 두는 조합이었다.

## 가장 의미 있는 결과 3개

### 1. `DBC + USMV`

- End Balance: `23,393.28`
- CAGR: `8.73%`
- MDD: `-13.01%`

기준인 `DBC Base`와 비교:

- `CAGR`
  - `8.65% -> 8.73%`
- `MDD`
  - `-15.09% -> -13.01%`

쉬운 뜻:
- 수익은 조금 더 좋고
- 낙폭은 꽤 줄었다
- 이번 search에서 가장 “실전형 개선”답게 보인 조합이다.

### 2. `DBC + QUAL + USMV`

- End Balance: `23,958.79`
- CAGR: `8.98%`
- MDD: `-14.54%`

`DBC Base`와 비교:

- `CAGR`
  - 더 높음
- `MDD`
  - 약간 더 좋음

쉬운 뜻:
- `USMV`만 추가했을 때보다 CAGR을 조금 더 끌어올리고 싶다면
  이 조합이 더 매력적이다.
- 대신 MDD 측면에선 `DBC + USMV`가 더 깔끔하다.

### 3. `DBC + TIP`

- End Balance: `23,867.58`
- CAGR: `8.94%`
- MDD: `-15.09%`

쉬운 뜻:
- 수익률은 좋아졌지만
- MDD는 사실상 개선이 없다.
- 그래서 “좋은 조합”으로 보이긴 해도
  `USMV`만큼 설득력 있지는 않다.

## 무엇이 별로였는가

### `Current PDBC`

- 여전히 가장 약한 축이다.
- 이번 search에서도 baseline으로 두기엔 부족하다.

### `DBC + QUAL`

- `CAGR`는 올라갔지만
- `MDD`가 더 나빠졌다.
- 즉 quality를 넣는다고 항상 더 실전형이 되는 건 아니다.

### `DBC + VEA`

- 거의 개선이 없었다.
- 현재 GTAA 구조에서는 `EFA`와의 역할 차이가 충분히 크게 나타나지 않았다.

## 왜 `USMV`가 좋아 보였는가

selection count를 보면 이유가 보인다.

### `DBC Base`

- `DBC` 편입 횟수: `29`

### `DBC + USMV`

- `USMV` 편입 횟수: `18`
- `DBC` 편입 횟수: `27`

쉬운 뜻:
- `USMV`가 단순히 리스트에만 있는 것이 아니라
  실제 top-3 안에 꽤 자주 들어왔다.
- 그리고 그 효과가
  낙폭 완화 쪽으로 연결된 것으로 보인다.

## `QUAL`은 어떻게 읽어야 하나

### `DBC + QUAL`

- `QUAL` 편입 횟수: `34`

### `DBC + QUAL + USMV`

- `QUAL` 편입 횟수: `31`
- `USMV` 편입 횟수: `16`

즉 `QUAL`도 실제로 자주 선택된다.

하지만 이번 결과 기준으로는:

- `QUAL` 단독 추가
  - CAGR 개선
  - MDD 악화
- `QUAL + USMV` 조합
  - CAGR 개선
  - MDD도 개선

즉 `QUAL`은 혼자보다
**`USMV`와 같이 쓸 때 더 균형 잡힌 결과**를 만들었다고 읽는 것이 맞다.

## `TIP`은 생각보다 영향이 작았다

selection count를 보면:

- `DBC + TIP`
  - `TIP` 편입 횟수: `1`
- `DBC + TIP + QUAL`
  - `TIP` 편입 횟수: `1`

즉 `TIP`은 실제 편입이 거의 안 됐다.

쉬운 뜻:
- 이번 결과에서 `TIP`이 들어간 조합의 성과 개선은
  “TIP이 자주 활약해서”라기보다
  rank 경쟁 구조가 조금 바뀐 효과에 더 가깝다.

그래서 현재 기준으로는
`TIP`을 GTAA 핵심 개선축으로 보긴 어렵다.

## 이번 search 기준 추천 순서

### 가장 실전적으로 좋아 보이는 조합

1. `DBC + USMV`
   - 수익도 조금 개선
   - 낙폭이 더 확실히 개선
2. `DBC + QUAL + USMV`
   - 수익을 더 끌어올리면서도
   - 기본 `DBC`보다 MDD가 좋아짐
3. `DBC + TIP`
   - 수익 개선은 있으나
   - MDD 개선이 부족

### 그대로 유지해도 되는 것

- `DBC Base`
  - 여전히 강한 baseline

### 굳이 안 해도 되는 것

- `DBC + VEA`
- `DBC + QUAL` 단독
- `Current PDBC`

## GTAA에서 무엇을 수정하면 더 좋아질 가능성이 있는가

이번 결과 기준으로는 3가지가 보인다.

### 1. commodity sleeve는 `DBC` 쪽이 낫다

- 현재 GTAA에서는 `PDBC`보다 `DBC`가 낫다.
- 이건 여전히 가장 큰 차이 중 하나다.

### 2. low-vol equity sleeve를 추가하는 것이 유효하다

- `USMV` 추가는 실제로 의미 있었다.
- GTAA의 top-3 구조 안에서
  drawdown을 줄이는 방향으로 작동했다.

### 3. quality는 단독보다 low-vol과 같이 볼 가치가 있다

- `QUAL`만 넣으면 MDD가 악화될 수 있다.
- 하지만 `USMV`와 함께 넣으면 더 균형 잡힌 결과가 나왔다.

즉 현재 가장 현실적인 개선 방향은:

1. `PDBC -> DBC`
2. `USMV` 추가
3. 필요하면 `QUAL`도 같이 추가

## 다음 추천 작업

### A. UI preset 후보

다음 2개를 실제 preset 후보로 올려볼 가치가 있다.

- `GTAA Universe (DBC + USMV)`
- `GTAA Universe (DBC + QUAL + USMV)`

### B. 추가 확인

아래 둘을 한 번 더 보면 더 좋다.

1. `2020 이후`만 따로 잘라서 비교
2. `USMV`, `QUAL`이 실제로 들어온 달에
   무엇을 밀어내며 선택됐는지 상세 비교

## 최종 판단

현재 10개 테스트 기준으로:

- “그냥 현재 GTAA를 그대로 쓰는 것”보다
- `DBC`로 바꾸는 것이 먼저고,
- 그 다음엔 `USMV`를 추가한 쪽이
  가장 실전적으로 좋아 보인다.

이번 search의 핵심 결론은:

- **가장 균형 잡힌 개선 후보:** `DBC + USMV`
- **더 공격적으로 수익을 올리려는 개선 후보:** `DBC + QUAL + USMV`

이다.
