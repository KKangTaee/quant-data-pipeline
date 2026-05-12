# PHASE13_CAGR20_MDD25_HOLD_FREE_SEARCH

## 목적

사용자가 다음 조건을 만족하는 후보를 다시 탐색해달라고 요청했다.

- 기간: `2016-01-01 ~ 2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`
- 목표:
  - `promotion != hold`
  - `CAGR >= 20%`
  - `Maximum Drawdown >= -25%`

이번 탐색은 서브 에이전트 병렬 실행으로 진행했고, `Quality`, `Value`, `Quality + Value` strict annual family를 나눠서 검토했다.

## 결론

이번 탐색 범위에서는 **exact hit를 찾지 못했다.**

즉, 현재 practical UI-reproducible settings와 현재 승격 계약 기준으로는:

- `hold 아님`
- `CAGR 20% 이상`
- `MDD 25% 이내`

를 동시에 만족하는 strict annual 후보가 나오지 않았다.

## 가장 가까운 후보

가장 가까운 후보는 모두 `Value > Strict Annual` family에 몰렸다.

### 1. Best near-miss

- strategy: `Value > Strict Annual`
- factor set:
  - `book_to_market`
  - `earnings_yield`
  - `sales_yield`
  - `ocf_yield`
  - `operating_income_yield`
- `Universe Contract = Historical Dynamic PIT Universe`
- 기간: `2016-01-01 ~ 2026-04-01`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 10`
- `benchmark = SPY`
- `Trend Filter = on`
- `Market Regime = on`
- `Underperformance Guardrail = on`
- `Drawdown Guardrail = on`
- 결과:
  - `CAGR = 18.81%`
  - `MDD = -23.71%`
  - `promotion = hold`
  - `shortlist = hold`
  - `deployment = blocked`

이 후보는 `MDD` 기준은 만족하지만 `CAGR`가 `20%`에 약간 못 미친다.

### 2. Low-drawdown side reference

- strategy: `Value > Strict Annual`
- factor set:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `top_n = 9`
- 나머지 계약은 위와 동일
- 결과:
  - `CAGR = 15.84%`
  - `MDD = -17.42%`
  - `promotion = hold`

이 후보는 drawdown은 훨씬 좋지만 CAGR이 목표에서 더 멀다.

### 3. Additional nearby case

- strategy: `Value > Strict Annual`
- same factor set as #2
- `top_n = 7`
- 결과:
  - `CAGR = 15.24%`
  - `MDD = -19.57%`
  - `promotion = hold`

## 왜 계속 hold가 남는가

가장 유력한 후보를 메인 환경에서 직접 확인했을 때, `hold`의 핵심 원인은 다음으로 정리됐다.

- `validation_status = caution`
- `validation_policy_status = caution`

반면 아래 항목들은 정상으로 읽혔다.

- `benchmark_policy_status = normal`
- `liquidity_policy_status = normal`
- `guardrail_policy_status = normal`

즉 문제는 유동성이나 benchmark 자체보다, **rolling validation / validation policy** 쪽이다.

특히 exact-hit에 가장 가까웠던 low-drawdown 후보에서는:

- `rolling_underperformance_share = 36.6%`
- `rolling_underperformance_worst_excess_return = -39.4%`

가 확인됐고, 이 값들이 현재 validation / promotion 기준에서 `caution`을 만들어 `hold`를 유지했다.

## 해석

현재 strict annual family에서는 다음 trade-off가 계속 나타난다.

1. 수익을 더 높게 만들면 drawdown은 `-20% ~ -25%` 구간으로 남고, `hold`도 자주 남는다.
2. drawdown을 더 줄이면 CAGR이 `20%` 아래로 내려간다.
3. `hold`를 풀기 위해서는 단순 `benchmark`나 `top_n` 조정보다, validation / promotion 정책을 다시 해석해야 할 가능성이 크다.

## 실무적 결론

이번 조건은 현재 구현 범위 안에서 **매우 공격적인 목표**에 가깝다.

실무적으로 다음 두 방향 중 하나가 더 현실적이다.

1. `CAGR >= 20%`는 유지하고 `MDD` 목표를 조금 완화
2. `MDD <= 25%`는 유지하고 `CAGR` 목표를 `18%` 전후로 완화

현재 strict annual 범위 안에서는, 그 중간 지점으로 보이는 가장 현실적인 기준선이:

- `Value Strict Annual`
- `top_n = 10`
- default value factor set
- `CAGR 18.81%`
- `MDD -23.71%`

후보라고 볼 수 있다.
