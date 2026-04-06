# PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE

## 목적

Phase 13 탐색에서 가장 강했던 `Value` raw winner를, 사용자가 백테스트 UI에서 그대로 다시 넣어볼 수 있도록 입력값 중심으로 정리한다.

이번 문서는 다음 결과를 재현하기 위한 가이드다.

- 전략 family: `Value`
- variant: `Strict Annual`
- `CAGR = 29.89%`
- `MDD = -29.15%`
- `promotion = real_money_candidate`

중요한 점:

- 이 후보는 **가장 강한 raw winner**다.
- 다만 `MDD`가 여전히 깊기 때문에, “가장 균형 잡힌 후보”와는 다르다.
- 즉 이 문서는 “숫자가 가장 강했던 Value 후보를 다시 돌려보는 법”을 정리한 문서다.

## 이 전략을 한 줄로 설명하면

`Historical Dynamic PIT Universe` 안에서 `Value` factor가 높은 종목만 매달 다시 고르고, `trend filter`와 `market regime`을 일부러 끈 상태로 더 공격적으로 운영한 strict annual value 전략이다.

쉽게 말하면:

- 싼 주식(value)이 많이 모인 쪽을 고르고
- 매달 다시 순위를 매기고
- 위험 회피 장치를 일부 끄면서
- raw return을 최대한 살린 버전

## 백테스트에서 넣어야 하는 값

### 1. 전략 선택

- `Backtest`
- `Single Strategy`
- `Value`
- variant: `Strict Annual`

### 2. Universe / 기간

- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- `Start Date`: `2016-01-01`
- `End Date`: `2026-04-01`
- `Timeframe`: `1d`
- `Option`: `month_end`

## 3. 포트폴리오 구성

- `Top N`: `10`
- `Rebalance Interval`: `1`

쉽게 말하면:

- 한 번 고를 때 상위 10개를 담고
- 매달 다시 계산해서 갈아탄다

## 4. Value Factor 설정

아래 factor만 선택한다.

- `book_to_market`
- `earnings_yield`
- `sales_yield`
- `ocf_yield`
- `operating_income_yield`

이 조합은 Value strict annual의 `default value factors`와 같다.

쉽게 말하면:

- 장부가 대비 싼가
- 이익 대비 싼가
- 매출 대비 싼가
- 영업현금흐름 대비 싼가
- 영업이익 대비 싼가

를 같이 보는 조합이다.

## 5. 실전형 입력값

이 탐색 묶음에서 사용한 실전형 계약은 아래 기준이었다.

- `Minimum Price`: `5.0`
- `Minimum History`: `12M`
- `Min Avg Dollar Volume 20D`: `5.0M`
- `Transaction Cost`: `10 bps`

쉽게 말하면:

- 너무 싼 종목은 빼고
- 최소 12개월 가격 이력이 있어야 하고
- 하루 평균 거래대금이 너무 낮은 종목은 빼고
- 매매 비용은 0.10%로 가정한다

## 6. 리스크 / 실전형 오버레이

이 raw winner를 만들 때 핵심은 아래 두 개를 끈 것이다.

- `Trend Filter`: `off`
- `Market Regime`: `off`

나머지는 search contract 기준을 유지한다.

- `Benchmark Contract`: `Ticker Benchmark`
- `Benchmark Ticker`: `SPY`
- `Underperformance Guardrail`: `on`
- `Drawdown Guardrail`: `on`

쉽게 말하면:

- 추세 필터를 끄고
- 시장 전체 risk-off 판정도 끄고
- 대신 실전형 진단과 guardrail surface는 그대로 둔 상태다

이 조합이 왜 중요했냐면:

- `Trend Filter`와 `Market Regime`를 켜면 drawdown은 줄어들 수 있지만
- 이 raw winner에서는 오히려 return edge가 많이 약해졌다

## 7. 기대 결과

Phase 13 탐색 기록 기준 기대 결과는 아래다.

- `CAGR = 29.89%`
- `MDD = -29.15%`
- `promotion = real_money_candidate`

이 결과는 `SPY`보다 `CAGR`는 높지만, drawdown은 아직 깊은 편이다.

## 8. 이 전략을 어떻게 해석하면 좋은가

이 포트폴리오는 다음처럼 읽는 것이 맞다.

### 장점

- strict annual family 중 `Value`의 raw alpha가 가장 강하게 드러난 후보다
- `promotion = real_money_candidate`까지 올라간 rare case다
- `SPY`보다 수익률이 훨씬 높다

### 주의점

- `MDD = -29.15%`라서 low-drawdown 포트폴리오는 아니다
- 즉 “가장 안전한 전략”이 아니라 “가장 공격적으로 강했던 Value 후보”에 가깝다

## 9. 실무적으로 같이 봐야 하는 비교 후보

이 전략을 볼 때는 아래 후보도 같이 비교하는 게 좋다.

### strongest balanced near-miss

- family: `Value > Strict Annual`
- factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `month_end / interval 1 / top_n 9`
- `benchmark = SPY`
- `trend_filter = on`
- `market_regime = on`
- `underperformance_guardrail = on`
- `drawdown_guardrail = on`
- 결과:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - `promotion = hold`

이 후보는 raw winner보다 수익은 낮지만, drawdown은 훨씬 얕다.

즉:

- `29.89 / -29.15` 전략은 “가장 강한 공격형 Value 후보”
- `15.84 / -17.42` 전략은 “가장 균형 잡힌 Value near-miss”

로 읽으면 된다.

## 최종 메모

지금 사용자가 다시 돌려보려는 목적이

- “가장 강했던 Value 전략이 정확히 무엇이었는지 보기”

라면 이 문서의 설정대로 넣으면 된다.

반대로 목적이

- “실전형으로 더 안전한 후보를 고르기”

라면 이 전략 하나만 보지 말고, 위의 balanced near-miss와 같이 봐야 한다.
