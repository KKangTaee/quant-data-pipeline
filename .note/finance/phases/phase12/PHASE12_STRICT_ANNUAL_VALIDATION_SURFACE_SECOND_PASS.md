# Phase 12 Strict Annual Validation Surface Second Pass

## 1. 이번 작업이 무엇인지

이번 pass는 strict annual family의 전략 규칙을 크게 바꾸는 작업이 아니다.

대신,
실전 판단에서 더 중요해지는
- benchmark 대비 drawdown
- rolling underperformance
- 현재 상태가 normal / watch / caution 중 어디인지
- 그리고 지금 run을 `real_money_candidate / production_candidate / hold` 중
  어느 쪽으로 읽는 편이 맞는지

를 결과 화면에서 바로 읽을 수 있게 만든
`validation surface` 보강 작업이다.

대상은 우선 strict annual family를 염두에 두고 진행했지만,
구현은 shared real-money helper에 들어가서
ETF 전략군에도 같은 진단 surface가 같이 붙는다.

## 2. 왜 이게 필요한가

first pass까지는 아래를 볼 수 있었다.
- minimum price
- turnover
- estimated cost
- benchmark end balance

이 정도면 "비용을 반영한 결과"는 읽을 수 있었지만,
"benchmark 대비 지금 상태가 괜찮은가"를 한 번 더 정리해서 보려면
사용자가 직접 숫자를 해석해야 했다.

실전 판단에서는 단순 수익률보다
- benchmark보다 더 깊게 깨지는지
- trailing window에서 benchmark를 자주 지는지
- 최근에도 계속 밀리고 있는지

를 같이 보는 편이 더 자연스럽다.

## 3. 이번에 추가된 진단 값

shared real-money runtime는 benchmark가 있을 때
아래 값을 추가로 계산한다.

- `validation_status`
  - `normal`
  - `watch`
  - `caution`
- `validation_window_label`
  - 현재 monthly contract 기준 `12M`
- `strategy_current_drawdown`
- `strategy_max_drawdown`
- `benchmark_current_drawdown`
- `benchmark_max_drawdown`
- `rolling_underperformance_share`
- `rolling_underperformance_current_streak`
- `rolling_underperformance_longest_streak`
- `rolling_underperformance_worst_excess_return`
- `rolling_underperformance_latest_excess_return`
- `validation_watch_signals`
- `promotion_decision`
- `promotion_rationale`
- `promotion_next_step`

## 4. 이 값들을 어떻게 읽으면 되는가

### `validation_status`

가장 요약된 신호다.

- `normal`
  - 현재 benchmark-relative 진단에서 큰 경고가 없다
- `watch`
  - 일부 drawdown / underperformance 신호가 있어서 추가 확인이 필요하다
- `caution`
  - 실전 승격 전에 다시 검토하는 편이 맞다

중요한 점:
이 값은 자동 매매 규칙이 아니라
`실전 검토용 상태 표시`다.

### `rolling_underperformance_share`

전체 rolling window 중 benchmark보다 뒤진 구간의 비율이다.

예:
- `20%`
  - trailing 12개월 창 대부분에서는 benchmark보다 크게 밀리지 않았다는 뜻
- `70%`
  - 많은 구간에서 benchmark를 계속 못 이겼다는 뜻

### `rolling_underperformance_current_streak`

최근 연속으로 몇 개 window를 benchmark보다 못 이겼는지 본다.

이 값이 크면
"지금도 계속 약한 상태가 이어지고 있다"
고 읽을 수 있다.

### `rolling_underperformance_worst_excess_return`

가장 나빴던 rolling window에서
benchmark 대비 얼마나 뒤졌는지 보여준다.

예:
- `-0.05`
  - 가장 나쁜 trailing 12개월 구간에서도 5%p 정도 뒤짐
- `-0.20`
  - 특정 trailing 12개월 구간에서 benchmark보다 20%p나 뒤진 적이 있음

### `strategy_max_drawdown` vs `benchmark_max_drawdown`

둘을 같이 봐야 한다.

전략 수익률이 좋아도
drawdown이 benchmark보다 너무 깊으면
실전에서는 버티기 어려울 수 있다.

### `promotion_decision`

이 값은 지금 run을 실전 승격 관점에서
어느 상태로 읽는 편이 맞는지 요약한 것이다.

- `real_money_candidate`
  - 현재 계약 기준에서는 실전형 후보로 읽을 수 있는 상태
- `production_candidate`
  - hardening은 되었지만, 아직 robustness / guardrail 검토가 더 필요
- `hold`
  - benchmark, validation, freshness 같은 핵심 review signal 때문에
    바로 승격하기보다 보류하는 편이 맞음

중요한 점:
이 값도 자동 투자 명령이 아니라
`현재 결과를 어떻게 해석할지` 돕는 review signal이다.

## 5. 경고 기준

현재 second pass는 아래를 watch signal로 본다.

- strategy drawdown이 benchmark보다 `5%p` 이상 더 나쁜 경우
- worst rolling excess가 `-10%` 이하인 경우
- current underperformance streak가 `3` 이상인 경우
- underperformance share가 `60%` 이상인 경우

이 중 일부가 겹치거나 더 심하면
`caution`으로 올린다.

즉 이 기준은
"실전 승격 전에 한 번 더 보자"
는 review signal이지,
자동으로 전략을 폐기하는 hard rule은 아니다.

## 6. UI에서 어디에 보이는가

### Single Strategy

`Real-Money` 탭에 아래가 추가된다.

- `Validation Status`
- `Strategy Max Drawdown`
- `Benchmark Max Drawdown`
- `Rolling Window`
- `Underperformance Share`
- `Current Underperf Streak`
- `Longest Underperf Streak`
- `Worst Rolling Excess`

그리고 watch/caution이면
짧은 안내 문구가 같이 나온다.

### Compare

focused strategy의 `Real-Money Contract` 섹션에서도
같은 값을 읽을 수 있다.

또 `Strategy Highlights`에는
- `Validation`
- `Promotion`
- `Worst Rolling Excess`

컬럼이 추가된다.

### Meta / Execution Context

`Execution Context`에도
- validation status
- strategy / benchmark max drawdown
- rolling underperformance 요약
- promotion decision / rationale / next step

이 같이 남는다.

## 7. 이번 작업의 경계

이번 pass는
`validation surface` 강화다.

이 문서 기준으로는 아직 안 한 것:
- richer benchmark contract
- stronger investability proxy
- multiple guardrail 조합 같은 stronger policy

즉 지금은
"실전 판단에 필요한 진단이 더 잘 보인다"
까지 왔고,
"진단을 바로 전략 규칙으로 연결한다"
까지는 이 문서 범위 밖이었다.

주의:
이후 Phase 12 later pass에서
`PHASE12_STRICT_ANNUAL_UNDERPERFORMANCE_GUARDRAIL_FIRST_PASS.md`
문서 기준으로
optional actual guardrail이 별도로 추가되었다.
즉 validation surface와 actual guardrail은
같은 것이 아니라 서로 다른 층으로 읽는 편이 맞다.

## 8. 검증

- `py_compile`
  - `app/web/pages/backtest.py`
  - `app/web/runtime/backtest.py`
- DB-backed annual strict smoke
  - validation status / rolling underperformance meta 생성 확인
- strict annual compare smoke
  - compare 경로에서도 같은 validation meta 유지 확인
