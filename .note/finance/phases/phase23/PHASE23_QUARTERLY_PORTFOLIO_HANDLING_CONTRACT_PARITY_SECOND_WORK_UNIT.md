# Phase 23 Quarterly Portfolio Handling Contract Parity Second Work Unit

## 이 문서는 무엇인가

`Phase 23`의 두 번째 작업 단위 문서다.

이번 작업은 quarterly strict family가 annual strict처럼 `Portfolio Handling & Defensive Rules`를 UI, payload, compare, history 재진입 흐름에서 일관되게 다룰 수 있도록 만든 첫 구현 단위다.

## 쉽게 말하면

quarterly 전략은 이미 실행됐다.
하지만 지금까지는 `Trend Filter`나 `Market Regime` 이후 포트폴리오를 어떻게 처리할지 annual strict만큼 명시적으로 고르기 어려웠다.

이번 작업으로 quarterly에서도 아래 세 가지를 같은 방식으로 고르고 저장할 수 있게 했다.

- `Weighting Contract`
- `Rejected Slot Handling Contract`
- `Risk-Off Contract`

## 왜 필요한가

quarterly를 제품 기능으로 보려면 단순히 한 번 실행되는 것만으로 부족하다.

사용자가 quarterly 결과를 다시 열었을 때,
그 결과가 어떤 포트폴리오 처리 규칙으로 계산되었는지 알아야 한다.
또 compare나 saved replay로 이어질 때도 같은 규칙이 유지되어야 한다.

## 실제로 변경한 것

### 1. quarterly single strategy UI

아래 세 quarterly family에 `Portfolio Handling & Defensive Rules`를 추가했다.

- `Quality Snapshot (Strict Quarterly Prototype)`
- `Value Snapshot (Strict Quarterly Prototype)`
- `Quality + Value Snapshot (Strict Quarterly Prototype)`

각 화면에는 Phase 23 기준 안내도 추가했다.
이 안내는 quarterly가 지금 제품 기능화 중이지만 아직 투자 후보 승격이나 real-money promotion 단계는 아니라는 점을 먼저 보여준다.

### 2. quarterly payload

quarterly single strategy 실행 payload에 아래 값을 저장하게 했다.

- `weighting_mode`
- `rejected_slot_handling_mode`
- `rejected_slot_fill_enabled`
- `partial_cash_retention_enabled`
- `risk_off_mode`
- `defensive_tickers`

### 3. quarterly runtime

세 quarterly runner가 위 값을 직접 받을 수 있게 했다.

특히 `Value`와 `Quality + Value` quarterly runner도 이제 sample layer의 strict statement shadow 실행 경로로 해당 contract 값을 넘긴다.

### 4. compare / history 재진입

compare form에서도 quarterly 전략별로 같은 contract를 고를 수 있게 했다.

history의 `Load Into Form` 또는 compare prefill로 들어온 quarterly payload도
`Weighting`, `Rejected Slot Handling`, `Risk-Off`, `Defensive Tickers` 값을 다시 form에 복원한다.

## 이번 작업에서 일부러 하지 않은 것

아래 항목은 아직 이번 구현 단위에서 붙이지 않았다.

- quarterly real-money promotion 판단
- quarterly benchmark contract / liquidity promotion policy
- quarterly underperformance / drawdown guardrail UI
- quarterly 투자 후보 승격 판단

이유는 quarterly가 아직 productionization 중이기 때문이다.
먼저 portfolio handling contract를 재현 가능하게 만든 뒤,
그 다음에 real-money contract를 그대로 붙일지 별도 quarterly 기준으로 나눌지 판단하는 편이 안전하다.

## 기대 효과

- quarterly 결과의 계산 조건을 더 명확히 읽을 수 있다.
- compare에서 quarterly와 annual을 볼 때 overlay 이후 처리 규칙 차이가 덜 숨는다.
- history / load-into-form에서 quarterly 설정이 빠지는 위험이 줄어든다.
- Phase 23 다음 작업인 representative smoke validation의 확인 포인트가 더 분명해진다.

## 다음 확인할 것

- quarterly single strategy UI에서 `Portfolio Handling & Defensive Rules`가 자연스럽게 보이는지 확인한다.
- compare form에서 quarterly 전략을 선택했을 때 같은 contract 항목이 보이는지 확인한다.
- history run을 load했을 때 quarterly contract 값이 복원되는지 확인한다.
- representative quarterly smoke run으로 runtime이 실제 DB-backed 경로에서 깨지지 않는지 확인한다.

## 한 줄 정리

이번 작업으로 quarterly strict family는 처음으로 annual strict와 같은 portfolio handling contract 언어를 UI, payload, compare, history 재진입 흐름에 연결했다.
