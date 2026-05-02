# Phase 12 ETF Real-Money Hardening First Pass

## 목적

- `GTAA`
- `Risk Parity Trend`
- `Dual Momentum`

이 3개 ETF 전략을 단순 runnable prototype이 아니라,
실전 투자 판단에 더 가깝게 읽을 수 있는 first-pass surface로 끌어올린 구현 기록이다.

쉬운 뜻:
- 예전에는 "전략이 돌아간다"에 가까웠다.
- 지금은 "최소 가격 필터, 비용, benchmark를 같이 보고 해석한다"까지 올라왔다.

왜 필요한가:
- 실전에서는 수익률 숫자만 보면 안 된다.
- 너무 싼 자산을 자동으로 걸러내는지,
- 리밸런싱 비용을 반영하면 결과가 얼마나 달라지는지,
- benchmark 대비 어떤 결과인지
를 같이 봐야 한다.

## 이번에 구현된 범위

## 1. 공통 입력

ETF 전략 3종의 `Single Strategy` form에 아래 입력이 추가되었다.

- `Minimum Price`
- `Transaction Cost (bps)`
- `Benchmark Ticker`

추가 기본값 조정:
- `GTAA`의 기본 commodity sleeve는 이제 `DBC` 대신 `PDBC`를 사용한다.
- `GTAA`의 기본 `Signal Interval`은 이제 `1`이다.
- 이후 Phase 12 탐색 결과를 반영해,
  GTAA preset surface는 기본값과 상위 후보 3개만 남기도록 정리되었다.
  - `GTAA Universe`
  - `GTAA Universe (No Commodity + QUAL + USMV)`
  - `GTAA Universe (QQQ + XLE + IAU + TIP)`
  - `GTAA Universe (QQQ + QUAL + USMV + XLE + IAU)`
  - `GTAA Universe (U3 Commodity Candidate Base)`
  - `GTAA Universe (U1 Offensive Candidate Base)`
  - `GTAA Universe (U5 Smallcap Value Candidate Base)`

쉬운 뜻:
- GTAA를 기본 preset으로 돌릴 때,
  원자재 ETF 자리에 이제 `PDBC`가 들어간다.
- 그리고 기본 cadence는 이제 격월이 아니라 매월 신호(`interval = 1`)다.
- 그리고 사용자는 현재 UI에서
  기본 universe, 기존 비교 후보, 그리고 검증된 candidate-base preset을 바로 비교할 수 있다.
- 이제 같은 GTAA universe selector가 `Compare & Portfolio Builder`에도 들어가서,
  compare에서도 `Preset` / `Manual`을 고를 수 있고,
  현재는 `Advanced Inputs > Strategy-Specific Advanced Inputs` 안에서
  해당 전략 옵션과 함께 관리된다.

추가 설명:
- `U3 / U1 / U5` preset은 universe만 저장한 preset이다.
- 즉 preset을 선택해도 `top`, `interval`, `Score Horizons`가 자동으로 바뀌지는 않는다.
- 대신 caption에 현재까지 가장 잘 검증된 contract를 함께 표시한다.

왜 이렇게 했는가:
- 이번 변경은 성능 최적화 때문이 아니라,
  실전 운용 관점에서 더 무난한 기본값을 두기 위한 전략 기본 universe 조정이다.
- 사용자는 필요하면 manual ticker 입력으로 여전히 다른 구성을 직접 실험할 수 있다.

추가로 기존에 compare에만 노출되어 있던 일부 core parameter도 single form에 같이 정리했다.

- `Risk Parity Trend`
  - `Rebalance Interval`
  - `Volatility Window`
- `Dual Momentum`
  - `Top Assets`
  - `Rebalance Interval`

## 2. 투자 가능성 필터 first pass

전략 함수 레벨에서 `min_price`가 추가되었다.

- `finance.strategy.gtaa3`
- `finance.strategy.risk_parity_trend`
- `finance.strategy.dual_momentum`

현재 의미:
- `Close >= trend filter`
- 그리고 `Close >= Minimum Price`

를 동시에 만족해야 실제 투자 후보로 본다.

쉬운 뜻:
- 너무 낮은 가격의 ETF는 실전형 후보에서 제외한다.

현재 한계:
- volume / spread / AUM 같은 더 강한 investability는 아직 안 들어갔다.
- 이번 pass는 `가격 기반 최소 안전장치`까지만 구현됐다.

## 3. turnover / cost first pass

runtime post-process에서 ETF 전략 결과에 아래가 추가된다.

- `Gross Total Balance`
- `Gross Total Return`
- `Turnover`
- `Estimated Cost`
- `Cumulative Estimated Cost`
- `Net Total Balance`
- `Net Total Return`

그리고 결과 surface의 기본 `Total Balance`, `Total Return`은
이 first pass에서는 `net` 기준으로 다시 계산된다.

쉬운 뜻:
- 기존 전략 곡선은 보존한다.
- 하지만 summary / chart는 비용 반영 후 기준으로 다시 본다.

현재 turnover 계산 방식:
- 현재 보유 비중과 다음 목표 비중 차이를 이용한 one-way turnover 근사
- `Rebalancing = False`인 행은 turnover를 `0`으로 본다

결과 표 읽는 법:
- `Turnover`
  - 그 날짜 리밸런싱에서 포트폴리오 비중이 얼마나 바뀌었는지에 대한 비율이다.
  - 예: `1.0`이면 포트폴리오를 거의 전부 다시 바꿨다는 뜻이고, `0.5`면 절반 정도를 갈아탔다는 뜻이다.
- `Gross Total Balance`
  - 비용을 빼기 전 전략 잔고다.
- `Total Balance`
  - 현재 first pass에서는 비용을 뺀 뒤 `net` 기준 잔고다.
  - 즉 `Gross Total Balance`보다 같거나 작게 보인다.
- `Estimated Cost`
  - 그 날짜 리밸런싱에서 turnover에 따라 추정한 비용 금액이다.
  - 단위는 퍼센트가 아니라 잔고와 같은 화폐 금액이다. 현재 프로젝트에서는 사실상 달러 금액으로 읽으면 된다.
- `Cumulative Estimated Cost`
  - 시작 시점부터 지금까지 누적된 예상 비용 금액이다.
  - 전략이 잦은 리밸런싱으로 얼마나 비용을 써왔는지 누적으로 보는 값이다.

현재 한계:
- exact trade blotter 수준은 아니다.
- slippage / spread / tax / market impact는 아직 포함되지 않았다.

## 4. benchmark overlay first pass

runtime은 결과 날짜 기준으로 benchmark ticker의 DB 종가를 `as-of`로 매핑해서
benchmark curve를 같이 만든다.

추가 산출물:
- `benchmark_chart_df`
- `benchmark_summary_df`

meta 추가 항목:
- `benchmark_available`
- `benchmark_end_balance`
- `net_excess_end_balance`

쉬운 뜻:
- 전략 날짜가 월말/격월이어도
- 같은 날짜 기준으로 benchmark를 비교할 수 있게 했다.

현재 한계:
- single ticker benchmark만 지원한다.
- composite benchmark나 factor benchmark는 아직 없다.

## 5. 결과 화면

`Single Strategy` 결과에 `Real-Money` 탭이 추가되었다.

여기서 볼 수 있는 것:
- `Minimum Price`
- `Transaction Cost`
- `Avg Turnover`
- `Estimated Cost Total`
- benchmark availability
- strategy net vs benchmark overlay
- cost detail preview
- 이후 shared real-money helper 보강으로
  benchmark-relative validation surface도 함께 읽을 수 있게 되었다.
  예:
  - `Validation Status`
  - strategy / benchmark max drawdown
  - rolling underperformance

`Compare`에서도 ETF 전략이 real-money hardening 정보를 유지한다.

- `Strategy Highlights`
  - `Min Price`
  - `Cost (bps)`
  - `Avg Turnover`
  - `Benchmark`
- `Focused Strategy`
  - `Real-Money Contract` 섹션

## 6. history / prefill / saved portfolio

다음 값이 history payload와 compare override에 같이 저장/복원된다.

- `min_price_filter`
- `transaction_cost_bps`
- `benchmark_ticker`

즉 아래 흐름에서 값이 유지된다.

- `Load Into Form`
- `Run Again`
- compare override
- saved portfolio compare context
- compare GTAA universe (`Preset` / `Manual`, selected tickers, preset name)

## 검증

compile:
- `finance/strategy.py`
- `finance/sample.py`
- `app/web/runtime/backtest.py`
- `app/web/runtime/history.py`
- `app/web/pages/backtest.py`

smoke:
- `run_gtaa_backtest_from_db(...)`
  - `real_money_hardening = True`
  - gross/net/cost columns 확인
  - benchmark overlay 생성 확인
- `run_risk_parity_trend_backtest_from_db(...)`
  - non-rebalance rows turnover `0` 확인
- `run_dual_momentum_backtest_from_db(...)`
  - real-money meta / cost / benchmark overlay 확인
- `_run_compare_strategy("GTAA", overrides=...)`
  - compare override가 runtime까지 내려가는 것 확인
- `_build_history_payload(...)`
  - min price / cost / benchmark가 payload에 포함되는 것 확인

## 이번 pass에서 일부러 안 한 것

- volume / spread / AUM 기반 investability
- rolling underperformance를 실제 전략 guardrail로 쓰는 것
- ETF strategy benchmark 선택지의 제품화
- transaction cost model 세분화
- strict annual family hardening

즉 이번 문서는
`ETF 전략군 real-money hardening first pass`
까지만 설명한다.
