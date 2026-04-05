# Phase 12 Strict Annual Underperformance Guardrail First Pass

## 1. 이번 작업이 무엇인지

이번 pass는 strict annual family에
`benchmark-relative trailing excess return` 기반의
optional guardrail을 실제 전략 규칙으로 연결한 작업이다.

대상 전략:
- `Quality Snapshot (Strict Annual)`
- `Value Snapshot (Strict Annual)`
- `Quality + Value Snapshot (Strict Annual)`

쉽게 말하면,
"benchmark 대비 최근 성과가 너무 나쁘면 그 rebalance에서는 무리하게 진입하지 않고 cash로 쉬게 할 수 있게 만들었다"
는 뜻이다.

중요한 점:
이 규칙은 기본값이 `OFF`다.
즉 current default behavior를 강제로 바꾸지 않고,
사용자가 실험 / 검증 / later promotion review를 위해 켤 수 있게 둔 first pass다.

## 2. 왜 이게 필요한가

validation surface second pass에서
rolling underperformance는 이미 read-only review signal로 보이고 있었다.

하지만 그 상태만으로는
"경고를 봤는데 실제 운용 규칙에는 반영되지 않는"
상태라서, 실전형 실험을 하려면 사용자가 직접 해석해서
별도 판단을 해야 했다.

이번 pass는 그중 하나를 명시적인 contract로 끌어와서,
strict annual family에서
"benchmark 대비 최근 상대성과가 너무 약할 때는 한 번 쉬는 것이 더 나은가"
를 실제 백테스트로 검증할 수 있게 만든 것이다.

## 3. 이번에 추가된 입력

single / compare의 annual strict block에 아래가 추가되었다.

- `Underperformance Guardrail`
  - 이 규칙을 켤지 말지
- `Guardrail Window (Months)`
  - 최근 몇 개월을 볼지
- `Worst Excess Threshold (%)`
  - benchmark 대비 trailing excess return이 어느 수준보다 더 나쁘면
    cash로 갈지

기본값:
- `Underperformance Guardrail = OFF`
- `Window = 12`
- `Threshold = -10%`

## 4. 실제 전략 규칙은 어떻게 동작하는가

guardrail이 켜져 있으면 rebalance 시점마다
아래를 본다.

1. 최근 `N`개월 동안 전략의 누적 수익률
2. 같은 기간 benchmark의 누적 수익률
3. 두 값의 차이 = trailing excess return

그리고 trailing excess return이
설정한 threshold보다 나쁘면
그 rebalance에서는 선택 종목에 진입하지 않고 cash를 유지한다.

예:
- window = `12M`
- threshold = `-10%`

이면
"최근 12개월 성과가 benchmark보다 10%p 이상 나쁘면 이번 rebalance는 쉬자"
로 읽으면 된다.

## 5. 결과에서 무엇을 볼 수 있는가

### Result Table

guardrail이 켜져 있으면 result row에 아래 진단 컬럼이 남는다.

- `Underperformance Guardrail State`
  - `warming_up`
  - `risk_on`
  - `risk_off`
  - `unknown`
- `Underperformance Guardrail Triggered`
- `Underperformance Guardrail Benchmark Close`
- `Underperformance Guardrail Strategy Return`
- `Underperformance Guardrail Benchmark Return`
- `Underperformance Guardrail Excess Return`
- `Underperformance Blocked Ticker`
- `Underperformance Blocked Count`

### Real-Money 탭

아래가 같이 보인다.

- `Guardrail`
- `Window`
- `Threshold`
- `Trigger Count`

즉 단순히 규칙을 켰다는 사실만이 아니라
"실제로 몇 번 발동했는가"까지 같이 읽을 수 있다.

### Compare / Execution Context

- `Strategy Highlights`
  - `Guardrail Triggers`
- `Execution Context`
  - guardrail contract
  - trigger summary

## 6. History / Prefill contract

guardrail 입력은 아래 경로에서도 복원된다.

- `History -> Load Into Form`
- compare prefill
- saved override payload

복원되는 값:
- `underperformance_guardrail_enabled`
- `underperformance_guardrail_window_months`
- `underperformance_guardrail_threshold`

즉 한 번 돌린 guardrail 실험을
나중에 다시 그대로 불러와 비교할 수 있다.

## 7. 이 규칙을 어떻게 읽어야 하는가

이 guardrail은
"실전형으로 보이게 만드는 UI 장식"
이 아니라,
실제로 selection 결과를 바꾸는 전략 규칙이다.

다만 아직은 first pass이므로,
이 규칙 하나를 켰다고 바로 real-money ready라고 보지는 않는 편이 맞다.

현재 위치는:
- validation surface보다 한 단계 더 실전적
- 하지만 stronger guardrail / richer benchmark / stronger investability까지 끝난 최종형은 아님

즉 지금은
"annual strict를 실제 운용 규칙처럼 더 엄격하게 실험할 수 있게 되었다"
정도로 읽는 것이 맞다.

## 8. 이번 작업의 경계

이번 pass에서 한 것:
- optional actual guardrail
- strict annual 3종 single / compare / history 연결
- result / real-money / compare / execution context 진단 추가

아직 안 한 것:
- multiple guardrail 조합
- richer benchmark selection contract
- stronger investability proxy
- guardrail이 promotion decision에 직접 자동 반영되는 stronger policy

## 9. 검증

- `py_compile`
  - `finance/sample.py`
  - `finance/strategy.py`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
- DB-backed smoke
  - annual strict run에서
    - guardrail columns 생성 확인
    - trigger count meta 생성 확인
    - guardrail input meta propagation 확인
