# Phase 28 Real-Money / Guardrail Parity Fifth Work Unit

## 무엇을 한 작업인가

Phase 28의 마지막 구현 단위로, 전략별 `Real-Money`와 `Guardrail` 지원 범위를 같은 언어로 보여주는 표를 추가했다.

쉽게 말하면:

- `annual strict`는 실전 검증 기능이 가장 많이 붙어 있는 기준 전략군이다.
- `quarterly prototype`은 아직 실전 승격 후보가 아니라 cadence / replay 검증 단계다.
- `Global Relative Strength`는 ETF 가격 기반 전략이라 ETF 운용 가능성 first pass만 본다.
- `GTAA`, `Risk Parity Trend`, `Dual Momentum`은 ETF 전략군용 Real-Money / Guardrail first pass를 본다.

## 왜 필요한가

Phase 28에서 사용자가 가장 헷갈릴 수 있는 지점은 다음 질문이다.

- “이 전략도 annual strict처럼 실전 검증이 다 붙은 건가?”
- “quarterly는 왜 Real-Money Contract가 없지?”
- “ETF 전략의 Real-Money는 재무제표 전략의 promotion과 같은 건가?”

정답은 “전략마다 성격이 다르므로 같은 UI를 강제로 붙이지 않는다”이다.
대신 화면에서 현재 지원 범위와 의도된 차이를 분명하게 보여준다.

## 이번 작업에서 바뀐 화면

- `Backtest > Compare & Portfolio Builder > Strategy Comparison`
  - `Real-Money / Guardrail` 탭을 추가했다.
  - compare에 들어간 전략별 실전 검증 범위와 저장 / replay 확인값을 함께 보여준다.
- `Backtest > History > Selected History Run`
  - `History Real-Money / Guardrail Scope` 표를 추가했다.
  - 선택한 저장 기록이 annual strict, quarterly prototype, ETF first pass 중 무엇인지 구분한다.
- `Backtest > Compare & Portfolio Builder > Saved Portfolios`
  - `Saved Portfolio Real-Money / Guardrail Scope` 표를 추가했다.
  - 저장 포트폴리오 안의 각 전략이 어떤 검증 범위로 다시 열리는지 확인한다.

## 이번 작업의 결론

Phase 28에서는 quarterly prototype에 annual strict와 같은 Real-Money / Guardrail 기능을 억지로 붙이지 않는다.

대신 다음 기준을 고정한다.

- annual strict: full strict equity Real-Money / Guardrail 기준 surface
- quarterly prototype: cadence / replay / portfolio handling 검증 단계
- GRS: ETF operability + cost / benchmark first pass, dedicated ETF guardrail은 아직 없음
- GTAA / Risk Parity / Dual Momentum: ETF Real-Money + ETF guardrail first pass
- Equal Weight: 실전 후보가 아니라 baseline

## 이 phase가 끝나면 좋은 점

- 사용자가 quarterly prototype을 annual strict 수준의 실전 검증 완료 전략으로 오해하지 않는다.
- ETF 전략의 Real-Money first pass와 strict equity promotion surface를 구분할 수 있다.
- compare, history, saved portfolio에서 같은 기준으로 Real-Money / Guardrail 범위를 확인할 수 있다.

## 다음에 확인할 것

- compare 결과의 `Real-Money / Guardrail` 탭이 보이는지
- quarterly prototype이 full Real-Money surface로 표시되지 않는지
- saved portfolio를 다시 열기 전에 strategy별 검증 범위가 이해되는지
- history record에서 annual / quarterly / ETF first pass 차이가 자연스럽게 읽히는지

## 한 줄 정리

Phase 28의 Real-Money / Guardrail parity는 모든 전략을 똑같이 만드는 작업이 아니라,
전략별 실전 검증 범위를 헷갈리지 않게 보여주는 작업이다.
