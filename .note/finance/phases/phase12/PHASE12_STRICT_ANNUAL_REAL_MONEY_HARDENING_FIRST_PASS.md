# Phase 12 Strict Annual Real-Money Hardening First Pass

## 1. 이번 작업이 무엇인지

이번 pass는 ETF 전략군에 먼저 붙였던 real-money 계약을
`Strict Annual Family`에도 첫 단계로 연결한 작업이다.

대상 전략:
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

쉽게 말하면,
"annual strict 전략도 이제 단순 backtest 숫자만 보는 것이 아니라,
최소 가격, 거래 비용, benchmark를 같이 보고 해석할 수 있게 만들었다"
는 뜻이다.

## 2. 왜 이게 필요한가

annual strict family는 Phase 10부터 dynamic PIT 기준에서는 더 실전형에 가까운 validation surface를 갖고 있었지만,
실제 운용 판단에 필요한 계약은 아직 ETF 전략군보다 약했다.

특히 이전 상태에서는:
- 최저 가격 기준이 없었고
- turnover 기반 비용이 반영되지 않았고
- benchmark와 같은 날짜 기준 비교가 바로 안 됐다

그래서 전략 수익률은 볼 수 있어도,
"실제로 굴린다면 어떤 숫자로 읽어야 하는가"는 한 단계 더 해석이 필요했다.

## 3. 이번에 추가된 것

### 3-1. Single Strategy form

annual strict 3종 form의 `Advanced Inputs`에 아래가 추가되었다.

- `Minimum Price`
- `Transaction Cost (bps)`
- `Benchmark Ticker`

기본값은 ETF 전략군과 동일하다.
- `Minimum Price = 5.0`
- `Transaction Cost = 10.0 bps`
- `Benchmark Ticker = SPY`

### 3-2. Compare surface

`Compare & Portfolio Builder`의 annual strict block에도 같은 입력이 추가되었다.

즉 compare에서도:
- universe/preset
- factor 선택
- trend/regime overlay
- real-money 입력

을 한 전략 블록 안에서 같이 조절할 수 있다.

### 3-3. History / Prefill

annual strict run을 저장한 뒤
`Load Into Form`, `Run Again`, compare prefill로 다시 불러오면
아래 값도 복원된다.

- `min_price_filter`
- `transaction_cost_bps`
- `benchmark_ticker`

## 4. runtime에서 실제로 바뀐 계약

### 4-1. min price filter

annual strict 전략은 statement shadow factor로 ranking한 뒤
동일가중으로 top N을 보유한다.

이번 pass부터는 rebalance 시점에:
- 가격이 존재하고
- `Minimum Price` 이상인 종목만
후보로 남는다.

즉 min price는 단순 표시용이 아니라,
실제로 annual strict ranking candidate를 줄이는 investability filter로 작동한다.

### 4-2. turnover / transaction cost

ETF 전략군과 같은 turnover 추정 후처리를 annual strict 결과에도 적용한다.

결과 표에는 아래 컬럼이 추가된다.
- `Gross Total Balance`
- `Gross Total Return`
- `Turnover`
- `Estimated Cost`
- `Cumulative Estimated Cost`
- `Net Total Balance`
- `Net Total Return`

그리고 현재 summary/chart는 net 기준으로 다시 계산된다.

### 4-3. benchmark overlay

`Benchmark Ticker`의 DB 가격을 결과 날짜에 `as-of`로 맞춰
benchmark curve를 같이 만든다.

결과 bundle에는:
- `benchmark_chart_df`
- `benchmark_summary_df`

가 추가될 수 있고,
meta에는:
- `benchmark_available`
- `benchmark_end_balance`
- `net_excess_end_balance`

가 남는다.

## 5. 결과 화면에서 어떻게 읽히는가

single strategy 결과에서
`meta.real_money_hardening = True`면
기존과 같은 `Real-Money` 탭이 열린다.

즉 annual strict 3종도 이제 ETF 전략군처럼:
- gross vs net
- turnover / estimated cost
- benchmark availability
- strategy net vs benchmark

를 같은 방식으로 읽을 수 있다.

compare에서도 focused strategy가 annual strict면
`Real-Money Contract` 섹션이 같이 보인다.

## 6. 현재 범위와 아직 안 한 것

이번 작업은 `first pass`다.

이번에 한 것:
- minimum price
- turnover / cost
- single benchmark overlay
- single / compare / history contract 연결

이 문서 시점에서 아직 안 한 것:
- rolling underperformance guardrail
- richer benchmark contract
- stronger investability proxy
- quarterly family로의 같은 승격

즉 annual strict는 이제
"real-money candidate를 읽기 위한 첫 계약"
까지는 올라왔지만,
guardrail second pass는 이후 later pass에서 별도 구현되었다.

## 7. 검증

- `py_compile`
  - `app/web/pages/backtest.py`
  - `app/web/runtime/backtest.py`
  - `finance/sample.py`
  - `finance/strategy.py`
- DB-backed smoke
  - `Quality Snapshot (Strict Annual)`
  - `Value Snapshot (Strict Annual)`
  - `Quality + Value Snapshot (Strict Annual)`
- compare smoke
  - strict annual compare override에서
    `min_price_filter`
    `transaction_cost_bps`
    `benchmark_ticker`
    가 runtime까지 내려가는 것 확인
