# Phase 13 Candidate Shortlist Contract First Pass

## 1. 이번 작업이 무엇인지

이번 pass는 Phase 12에서 이미 계산하고 있던
- `promotion_decision`
- `benchmark / liquidity / validation / guardrail` 상태

를 그대로 두고,
그 결과를 **실제 운용 shortlist 언어**로 다시 읽을 수 있게 만든 작업이다.

즉 이제 결과 화면에서는 단순히
- `real_money_candidate`
- `production_candidate`
- `hold`

만 보는 것이 아니라,
- `watchlist`
- `paper_probation`
- `small_capital_trial`
- `hold`

중 어디에 두는 것이 자연스러운지도 같이 볼 수 있다.

쉬운 뜻:

- Phase 12는 "이 전략이 실전형 후보인가"를 정리했다.
- Phase 13 first pass는 "그 후보를 실제 운용 리스트에서는 어떤 상태로 둘 것인가"를 정리한다.

## 2. 왜 이게 필요한가

`promotion_decision`만으로는 아직 운영 행동이 직접 보이지 않는다.

예를 들어:
- `real_money_candidate`라고 해도 바로 실제 돈을 넣는 것은 과하다
- `production_candidate`도 그냥 남겨두면 다음 행동이 모호하다

그래서 Phase 13에서는
백테스트 / validation 결과를
**운영 상태 language**로 다시 묶어주는 shortlist contract가 필요하다.

## 3. 이번 first pass에서 고정한 shortlist 상태

### `hold`

- 의미:
  아직 shortlist로 올리기 어렵다.
- 언제 쓰는가:
  `promotion_decision = hold`

### `watchlist`

- 의미:
  후보로는 남기지만,
  바로 probation으로 넘기기 전 추가 review가 더 필요하다.
- 언제 쓰는가:
  `promotion_decision = production_candidate`

### `paper_probation`

- 의미:
  실전형 후보로는 읽히지만,
  실제 자금 투입 전 종이계좌 / paper tracking으로 먼저 관찰하는 것이 맞다.
- 언제 쓰는가:
  `promotion_decision = real_money_candidate`
  이지만, 아직 더 보수적으로 보는 편이 맞는 경우

현재 first pass에서는 특히 아래가 여기에 해당한다.
- ETF 전략군
  - 이유: ETF second-pass backlog가 아직 남아 있기 때문
- annual strict라도
  - actual guardrail / benchmark contract 조건이 더 강하게 맞지 않은 경우

### `small_capital_trial`

- 의미:
  매우 작은 실제 자금으로 trial을 검토할 수 있는 상태다.
- 언제 쓰는가:
  현재 first pass에서는 **strict annual 계열 중에서도**
  아래 조건이 모두 맞는 경우만 여기에 올린다.
  - `promotion_decision = real_money_candidate`
  - `underperformance_guardrail_enabled = True`
  - `drawdown_guardrail_enabled = True`
  - `benchmark_available = True`
  - `universe_contract != static_managed_research`
  - `benchmark_contract = candidate_universe_equal_weight`

쉬운 뜻:

- `small_capital_trial`은 일부러 좁게 잡았다.
- first pass에서는 쉽게 실제 자금 trial로 올리지 않고,
  annual strict에서 guardrail과 benchmark contract가 더 강하게 맞는 경우에만 허용한다.

## 4. 실제 runtime에서 어떻게 계산되는가

runtime meta에는 아래가 추가된다.

- `strategy_family`
- `shortlist_family`
- `shortlist_status`
- `shortlist_next_step`
- `shortlist_rationale`

그리고 `promotion_decision`이 계산된 뒤,
그 값을 바탕으로 shortlist status가 이어서 계산된다.

즉 shortlist는 별도 임의 판단이 아니라,
이미 구현된 promotion / policy surface를
**운영 language로 재해석한 레이어**다.

## 5. UI에서 어디서 보이는가

### Single / Focused Strategy

`Real-Money Contract` 안에
`Candidate Shortlist` 섹션이 추가된다.

여기서:
- `Family`
- `Status`
- `Next Step`
- `Shortlist rationale`

를 같이 본다.

### Execution Context

아래 값이 같이 보인다.
- `Shortlist Status`
- `Shortlist Next Step`
- `Shortlist Family`

### Compare

`Strategy Highlights`에 아래가 추가된다.
- `Shortlist`
- `Shortlist Next`

또 compare meta 표에도
- `strategy_family`
- `shortlist_status`
- `shortlist_next_step`

가 같이 남는다.

## 6. 현재 범위와 의도적인 한계

이번 작업은 **first pass**다.

이번에 한 것:
- shortlist 상태 language 고정
- runtime meta 연결
- single / compare / execution context surface 연결

아직 안 한 것:
- shortlist를 별도 저장 object로 관리
- paper probation / small-capital trial 기록 workflow
- monthly review note surface
- manual override shortlist 상태

즉 지금은
"백테스트 결과를 shortlist 상태로 읽을 수 있게 만든 first pass"
로 보는 것이 맞다.

## 7. 검증

- `py_compile`
  - `app/web/runtime/backtest.py`
  - `app/web/pages/backtest.py`
- DB-backed smoke
  - strict annual sample run
  - GTAA sample run
- helper-level smoke
  - `hold`
  - `watchlist`
  - `paper_probation`
  - `small_capital_trial`
  상태가 각각 계산되는 것 확인
