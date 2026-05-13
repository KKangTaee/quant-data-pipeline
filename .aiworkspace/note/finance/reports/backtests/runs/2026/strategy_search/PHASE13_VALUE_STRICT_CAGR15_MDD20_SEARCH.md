# PHASE13_VALUE_STRICT_CAGR15_MDD20_SEARCH

## 목적

사용자가 다음 조건을 만족하는 포트폴리오를 다시 탐색해달라고 요청했다.

- 기간: `2016-01-01 ~ 2026-04-01`
- `Universe Contract = Historical Dynamic PIT Universe`
- `top_n <= 10`
- 목표:
  - `CAGR >= 15%`
  - `Maximum Drawdown >= -20%`

직전 문맥상 `Quality`, `Value`, `Quality + Value` strict annual family를 모두 후보로 두고, 서브 에이전트 병렬 탐색 후 메인 환경에서 재검증하는 방식으로 진행했다.

## 기준선

같은 기간의 `SPY` 기준선은 메인 환경에서 직접 확인했다.

- `SPY`
  - `CAGR = 14.09%`
  - `MDD = -33.72%`

즉 이번 탐색은 단순히 수치 조건만 보는 것이 아니라, 실질적으로는 `SPY`보다도 나은 drawdown profile을 만들 수 있는지 함께 확인하는 의미를 가진다.

## 최종 발견 후보

### Best exact hit

- 전략 family: `Value`
- variant: `Strict Annual`
- preset: `US Statement Coverage 100`
- `Universe Contract = Historical Dynamic PIT Universe`
- 기간: `2016-01-01 ~ 2026-04-01`
- `option = month_end`
- `rebalance_interval = 1`
- `top_n = 9`
- value factors:
  - `earnings_yield`
  - `ocf_yield`
  - `operating_income_yield`
  - `fcf_yield`
- `Minimum Price = 5.0`
- `Minimum History = 12M`
- `Min Avg Dollar Volume 20D = 5.0M`
- `Transaction Cost = 10 bps`
- `Benchmark = SPY`
- `Trend Filter = on`
- `Market Regime = on`
- `Underperformance Guardrail = on`
- `Drawdown Guardrail = on`

### 메인 환경 재검증 결과

- `CAGR = 15.84%`
- `MDD = -17.42%`
- `promotion = hold`
- `shortlist = hold`
- `deployment = blocked`
- `validation = caution`
- `rolling = caution`
- `out_of_sample = normal`

## 근접 후보

- `top_n = 7`
  - 같은 factor / 같은 계약
  - `CAGR = 15.24%`
  - `MDD = -19.57%`
- `top_n = 10`
  - 같은 factor / 같은 계약
  - `CAGR = 14.61%`
  - `MDD = -15.16%`

즉 `top_n = 9`가 이번 탐색 범위에서 가장 깔끔하게:

- `CAGR >= 15%`
- `MDD >= -20%`

을 동시에 만족했다.

## 해석

이번 탐색의 핵심 결과는 두 가지다.

1. `Quality`와 `Quality + Value`보다 `Value Strict Annual`이 이 제약 조건에서 더 유리했다.
2. 숫자 목표는 맞출 수 있었지만, 현재 승격/검증 정책 기준으로는 여전히 `hold`가 남아 있다.

즉 이 후보는:

- 성과 조건으로는 합격
- 운영/승격 계약으로는 아직 보류

라고 읽는 것이 맞다.

## 실무적 의미

이 결과는 다음을 보여준다.

- `Value Strict Annual`은 long-window 조건에서도 방어적 drawdown과 준수한 CAGR을 동시에 만들 수 있다.
- 하지만 현재 validation/promotion contract는 여전히 보수적으로 작동하고 있어서, 성과 숫자가 좋다고 바로 `paper_probation` 이상으로 올라가지는 않는다.

따라서 다음 단계는 자연스럽게:

1. 이 후보를 기준으로 `hold`를 만드는 항목이 정확히 무엇인지 좁혀 보기
2. `top_n = 7 / 9 / 10` 주변에서 robustness를 추가 확인하기

로 이어진다.
