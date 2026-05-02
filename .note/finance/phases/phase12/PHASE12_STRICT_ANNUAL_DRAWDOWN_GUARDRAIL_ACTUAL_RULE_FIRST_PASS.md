# Phase 12 Strict Annual Drawdown Guardrail Actual Rule First Pass

## 1. 이번 작업이 무엇인지

이번 pass는 strict annual family에
`drawdown-based optional actual guardrail`을
실제 전략 규칙으로 연결한 작업이다.

대상 전략:
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

쉽게 말하면,
"최근 전략 낙폭이 너무 깊거나 benchmark보다 낙폭이 지나치게 나빠지면,
그 rebalance에서는 무리하게 진입하지 않고 cash로 쉬게 할 수 있게 만들었다"
는 뜻이다.

중요한 점:
이 규칙은 기본값이 `OFF`다.
즉 current default behavior를 강제로 바꾸지 않고,
사용자가 실험 / 검증 / later promotion review를 위해 켤 수 있게 둔 first pass다.

## 2. 왜 이게 필요한가

이전 later pass에서 strict annual family는
`Portfolio Guardrail Policy`를 통해
전략 최대 낙폭과 benchmark 대비 drawdown gap을
승격 판단에 반영할 수 있게 되었다.

하지만 그 상태만으로는
"이 전략은 승격 후보로 조심해야 한다"는 해석만 있을 뿐,
실제 rebalance 규칙은 그대로였다.

이번 pass는 그중 일부를 actual execution rule로 끌어와서,
strict annual family에서
"최근 drawdown 상태가 너무 나쁠 때는 한 번 쉬는 것이 더 나은가"
를 실제 백테스트로 검증할 수 있게 만든 것이다.

## 3. 이번에 추가된 입력

single / compare의 annual strict block에 아래가 추가되었다.

- `Drawdown Guardrail`
  - 이 규칙을 켤지 말지
- `Drawdown Window (Months)`
  - 최근 몇 개월의 전략 / benchmark 낙폭을 볼지
- `Strategy DD Threshold (%)`
  - 전략 trailing drawdown이 어느 수준보다 더 깊으면 cash로 갈지
- `Drawdown Gap Threshold (%)`
  - 전략 drawdown이 benchmark보다 얼마나 더 나빠졌을 때 cash로 갈지

기본값:
- `Drawdown Guardrail = OFF`
- `Window = 12`
- `Strategy DD Threshold = -35%`
- `Drawdown Gap Threshold = 8%`

## 4. 실제 전략 규칙은 어떻게 동작하는가

guardrail이 켜져 있으면 rebalance 시점마다
아래를 본다.

1. 최근 `N`개월 동안 전략의 trailing max drawdown
2. 같은 기간 benchmark의 trailing max drawdown
3. 두 값의 차이 = drawdown gap

그리고 아래 중 하나라도 만족하면
그 rebalance에서는 선택 종목에 진입하지 않고 cash를 유지한다.

- 전략 trailing drawdown이 `Strategy DD Threshold`보다 더 깊다
- 전략 drawdown이 benchmark보다 `Drawdown Gap Threshold` 이상 더 나쁘다

예:
- window = `12M`
- strategy threshold = `-35%`
- gap threshold = `8%`

이면
"최근 12개월 기준 전략 drawdown이 -35%보다 깊거나,
benchmark보다 drawdown이 8%p 이상 더 나쁘면 이번 rebalance는 쉬자"
로 읽으면 된다.

## 5. 결과에서 무엇을 볼 수 있는가

### Result Table

guardrail이 켜져 있으면 result row에 아래 진단 컬럼이 남는다.

- `Drawdown Guardrail State`
  - `warming_up`
  - `risk_on`
  - `risk_off`
  - `unknown`
- `Drawdown Guardrail Triggered`
- `Drawdown Guardrail Benchmark Close`
- `Drawdown Guardrail Strategy Drawdown`
- `Drawdown Guardrail Benchmark Drawdown`
- `Drawdown Guardrail Gap`
- `Drawdown Blocked Ticker`
- `Drawdown Blocked Count`

### Real-Money 탭

아래가 같이 보인다.

- `Guardrail`
- `Window`
- `Strategy DD Threshold`
- `DD Gap Threshold`
- `Trigger Count`

즉 규칙이 켜져 있다는 사실뿐 아니라
"실제로 몇 번 발동했는가"까지 같이 읽을 수 있다.

### Compare / Execution Context

- `Strategy Highlights`
  - `DD Guardrail Triggers`
- `Execution Context`
  - drawdown guardrail contract
  - trigger summary

## 6. History / Prefill contract

guardrail 입력은 아래 경로에서도 복원된다.

- `History -> Load Into Form`
- compare prefill
- saved override payload

복원되는 값:
- `drawdown_guardrail_enabled`
- `drawdown_guardrail_window_months`
- `drawdown_guardrail_strategy_threshold`
- `drawdown_guardrail_gap_threshold`

즉 한 번 돌린 drawdown guardrail 실험을
나중에 다시 그대로 불러와 비교할 수 있다.

## 7. 이 규칙을 어떻게 읽어야 하는가

이 guardrail은
"실전형으로 보이게 만드는 UI 장식"
이 아니라,
실제로 selection 결과를 바꾸는 전략 규칙이다.

다만 아직은 first pass이므로,
이 규칙 하나를 켰다고 바로 real-money ready라고 보지는 않는 편이 맞다.

현재 위치는:
- promotion rule만 보강한 단계보다 한 단계 더 실전적
- 하지만 richer spread / AUM policy까지 끝난 최종형은 아님

즉 지금은
"annual strict를 drawdown 기준까지 포함해 더 보수적으로 실험할 수 있게 되었다"
정도로 읽는 것이 맞다.

## 8. 이번 작업의 경계

이번 pass에서 한 것:
- optional actual drawdown guardrail
- strict annual 3종 single / compare / history 연결
- result / real-money / compare / execution context 진단 추가

아직 안 한 것:
- richer spread / AUM policy
- multiple drawdown guardrail 조합
- 더 강한 liquidity / AUM / spread 기반 execution realism

## 9. 검증

- `py_compile`
  - `finance/strategy.py`
  - `finance/sample.py`
  - `app/web/runtime/backtest.py`
  - `app/web/runtime/history.py`
  - `app/web/pages/backtest.py`
- DB-backed smoke
  - strict annual quality / value / quality+value 경로에서
    drawdown guardrail columns 생성 확인
  - trigger count / trigger share meta 생성 확인
  - guardrail input meta propagation 확인
