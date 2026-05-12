# Value Strict Annual Strongest Current Candidate

## 목적

이 문서는 현재 코드 기준으로 `Value > Strict Annual` family에서
가장 강한 current candidate 하나를
링크 모음이 아니라 **전략 구성 자체** 중심으로 바로 읽기 쉽게 정리한 문서다.

즉 아래 질문에 바로 답하는 문서다.

- 어떤 전략인가
- 무엇을 어떻게 선택하는가
- 백테스트에서 어떤 값을 넣었는가
- 왜 strongest candidate로 보는가
- 무엇을 주의해서 읽어야 하는가

## 전략 한 줄 설명

`Historical Dynamic PIT Universe` 안에서
대표적인 `Value` factor 5개로 싼 종목을 매달 다시 골라 담고,
`Trend Filter`와 `Market Regime`는 끈 상태로
raw return edge를 가장 강하게 드러낸 strict annual value 전략이다.

쉽게 말하면:

- 싸게 보이는 종목들을 다시 순위화하고
- 상위 10개를 담고
- 매달 다시 갈아타는
- 공격형 `Value` strict annual 포트폴리오다.

## 전략 구성

### 1. 전략 family / variant

- family: `Value`
- variant: `Strict Annual`

### 2. Universe / 기간

- preset: `US Statement Coverage 100`
- `Universe Contract`: `Historical Dynamic PIT Universe`
- `Start Date`: `2016-01-01`
- `End Date`: `2026-04-01`
- `Timeframe`: `1d`
- `Option`: `month_end`

### 3. 포트폴리오 구성

- `Top N`: `10`
- `Rebalance Interval`: `1`

쉽게 말하면:

- 한 번 고를 때 10개를 담고
- 매달 다시 계산해서 교체한다.

### 4. Value factor 선택

이 후보는 아래 5개 factor를 사용한다.

- `book_to_market`
- `earnings_yield`
- `sales_yield`
- `ocf_yield`
- `operating_income_yield`

쉽게 말하면:

- 장부가 대비 싼가
- 이익 대비 싼가
- 매출 대비 싼가
- 영업현금흐름 대비 싼가
- 영업이익 대비 싼가

를 같이 보는 기본형 `Value` factor 묶음이다.

## 실전형 입력값

이 후보를 current practical contract 기준으로 다시 확인할 때 사용한 값은 아래와 같다.

- `Minimum Price`: `5.0`
- `Minimum History`: `12M`
- `Min Avg Dollar Volume 20D`: `5.0M`
- `Transaction Cost`: `10 bps`
- `Benchmark Contract`: `Ticker Benchmark`
- `Benchmark Ticker`: `SPY`
- `Min Benchmark Coverage`: `95%`
- `Min Net CAGR Spread`: `-2%`
- `Min Liquidity Clean Coverage`: `90%`
- `Max Underperformance Share`: `55%`
- `Min Worst Rolling Excess`: `-15%`
- `Max Strategy Drawdown`: `-35%`
- `Max Drawdown Gap vs Benchmark`: `8%`

쉽게 말하면:

- 너무 싼 종목은 빼고
- 최소 12개월 가격 이력이 있어야 하며
- 최근 20거래일 평균 거래대금이 너무 낮은 종목은 빼고
- 매매 비용은 0.10%로 가정한다.
- 그리고 benchmark / validation / liquidity / guardrail 승격 기준도 같이 켠 상태다.

중요:

- strict annual UI 기본값은 원래
  - `Minimum History = 0M`
  - `Min Avg Dollar Volume 20D = 0.0M`
  - underperformance / drawdown guardrail `off`
  쪽에 더 가깝다.
- 즉 위 strongest candidate는
  **기본 UI 상태를 그대로 돌린 값이 아니라**
  `Real-Money Contract`를 practical하게 맞춘 뒤 다시 돌린 결과다.
- 현재 UI에서는 `Preset = US Statement Coverage 100`과
  `Universe Contract = Historical Dynamic PIT Universe`를 같이 선택하면,
  selected preset `100`개가 그대로 dynamic candidate pool로 사용된다.
  즉 hidden `1000 -> 100` membership 확장을 따로 가정하지 않아도 된다.

## Benchmark / Overlay / Guardrail

- `Benchmark Contract`: `Ticker Benchmark`
- `Benchmark Ticker`: `SPY`
- `Trend Filter`: `off`
- `Market Regime`: `off`
- `Underperformance Guardrail`: `on`
- `Drawdown Guardrail`: `on`

guardrail 세부값은 아래와 같다.

- `Underperformance Guardrail Window`: `12M`
- `Underperformance Worst Excess Threshold`: `-10%`
- `Drawdown Guardrail Window`: `12M`
- `Drawdown Guardrail Strategy DD Threshold`: `-35%`
- `Drawdown Guardrail Gap Threshold`: `8%`

핵심 포인트는 이거다.

- `Trend Filter`와 `Market Regime`를 끄면 더 공격적으로 간다
- 대신 real-money 해석에 필요한 benchmark / guardrail surface는 유지한다

즉:

- 실제 factor edge는 최대한 살리고
- 결과 해석은 실전형 기준으로 계속 읽는 조합이다.

즉 `guardrail on`은 단순한 체크만이 아니라,
위 `window / threshold`까지 포함한 계약이라고 보는 편이 맞다.

## 현재 strongest candidate로 보는 이유

current runtime refresh 기준으로 이 전략은:

- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`

까지 올라간다.

strict annual 3개 family를 같은 practical contract로 다시 돌렸을 때,
이 조합만 현재:

- `real_money_candidate`
- `paper_probation`
- `deployment != blocked`

를 동시에 만족했다.

## 기대 결과

current runtime refresh 기준 기대 결과는 아래다.

- `CAGR = 29.89%`
- `MDD = -29.15%`
- `Promotion = real_money_candidate`
- `Shortlist = paper_probation`
- `Deployment = review_required`
- `Validation = normal`
- `Validation Policy = normal`
- `Benchmark Policy = normal`
- `Liquidity Policy = normal`
- `Guardrail Policy = normal`
- `Rolling Review = watch`
- `Out-of-Sample Review = caution`

## 이 전략을 어떻게 해석하면 좋은가

### 장점

- strict annual family 중 현재 strongest exact candidate다
- `real_money_candidate / paper_probation`까지 올라간 rare case다
- `SPY` benchmark 기준으로도 수익률 edge가 강하다

### 주의점

- `MDD = -29.15%`라서 low-drawdown 전략은 아니다
- `Deployment = review_required`라서 바로 실전 투입 완료 상태로 읽으면 안 된다
- `Rolling Review = watch`, `Out-of-Sample Review = caution`이 남아 있어서
  최근/후반부 consistency는 더 보수적으로 읽어야 한다

## 어떤 상황에서 다시 보면 좋은가

이 문서는 특히 아래 목적일 때 바로 보면 된다.

- “지금 기준 strongest Value 포트폴리오가 정확히 무엇인지 보고 싶다”
- “Backtest UI에 무엇을 넣어야 하는지 한 장에서 보고 싶다”
- “왜 이 전략은 `paper_probation`까지 갔는지 이해하고 싶다”

반대로 목적이

- 더 방어적인 후보를 찾는 것
- `MDD`를 더 줄이는 것
- `Deployment`를 더 보수적으로 통과시키는 것

이라면 이 전략 하나만 보지 말고
balanced near-miss 문서도 같이 보는 게 맞다.

## 같이 보면 좋은 문서

- [VALUE_STRICT_ANNUAL.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/strategies/VALUE_STRICT_ANNUAL.md)
  - `Value` family 전체 허브
- [PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase13/PHASE13_VALUE_RAW_WINNER_BACKTEST_GUIDE.md)
  - strongest raw winner를 처음 정리한 재현 가이드
- [PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md](/Users/taeho/Project/quant-data-pipeline-worktrees/phase/.note/finance/reports/backtests/archive/legacy_phase/phase14/PHASE14_STRICT_ANNUAL_NONHOLD_CANDIDATE_REFRESH.md)
  - current runtime practical refresh 기준으로 family별 strongest candidate를 다시 고정한 문서
