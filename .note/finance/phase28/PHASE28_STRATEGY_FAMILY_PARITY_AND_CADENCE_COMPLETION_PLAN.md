# Phase 28 Strategy Family Parity And Cadence Completion Plan

## 이 문서는 무엇인가

이 문서는 Phase 28에서 전략 family별 사용성과 저장 / 재실행 흐름을 어떻게 맞출지 정리하는 계획 문서다.

Phase 28은 새 전략을 많이 추가하는 phase가 아니다.
이미 있는 annual strict, quarterly strict, price-only ETF 전략이 서로 다른 수준으로 만들어져 있을 때,
그 차이가 의도된 것인지 아직 덜 만든 것인지 사용자가 이해할 수 있게 만드는 phase다.

## 목적

- annual strict, quarterly strict, Global Relative Strength, GTAA 등 주요 전략 family의 지원 범위를 비교 가능하게 만든다.
- strategy별 cadence, data trust, history/replay, Real-Money/Guardrail 지원 차이를 화면과 문서에서 명확히 보여준다.
- Phase 29 후보 검토 workflow로 넘어가기 전에, 실행 / 저장 / 재실행의 의미가 strategy마다 흔들리지 않게 한다.

## 쉽게 말하면

지금은 어떤 전략은 Real-Money와 Guardrail이 잘 붙어 있고,
어떤 전략은 quarterly prototype이라 일부 기능만 붙어 있으며,
어떤 전략은 가격 기반 ETF 전략이라 재무제표 전략과 구조가 다르다.

Phase 28은 사용자가 이 차이를 "버그인가? 아직 미완성인가? 의도된 차이인가?"로 헷갈리지 않게 만드는 단계다.

## 왜 필요한가

- Phase 23에서 quarterly strict family를 제품 흐름으로 올렸다.
- Phase 24에서 Global Relative Strength 같은 신규 price-only ETF 전략을 추가했다.
- Phase 27에서 Data Trust Summary와 price_freshness라는 공통 trust-layer 개념이 생겼다.
- 이제 같은 Backtest 화면 안에서 전략마다 어떤 기능이 지원되는지, 어떤 기능은 나중에 맞출 대상인지 명확히 보여줘야 한다.

## 이 phase가 끝나면 좋은 점

- 사용자는 annual / quarterly / 신규 ETF 전략을 비교할 때 각 전략의 지원 범위를 바로 이해할 수 있다.
- history, load-into-form, run-again, saved replay에서 어떤 값이 복원되어야 하는지 확인하기 쉬워진다.
- Real-Money, Guardrail, Data Trust Summary가 strategy마다 어디까지 붙어 있는지 분명해진다.
- Phase 29에서 후보 검토 / 추천 workflow를 만들 때, 전략별 입력과 결과 계약이 덜 흔들린다.

## 이 phase에서 다루는 대상

- `Backtest > Single Strategy`
- `Backtest > Compare & Portfolio Builder`
- `Backtest > History`
- saved portfolio / replay로 이어지는 strategy override
- annual strict / quarterly strict / price-only ETF 전략의 capability 차이
- Phase 27에서 만든 Data Trust Summary / price_freshness 표현의 family별 확장 범위

## 현재 구현 우선순위

1. Strategy Capability Snapshot
   - 쉽게 말하면: 각 전략 카드에서 "이 전략은 지금 어디까지 지원되는가"를 표로 보여준다.
   - 왜 먼저 하는가: 사용자가 annual과 quarterly, GRS의 차이를 가장 먼저 헷갈리기 때문이다.
   - 기대 효과: 기능이 없는 것인지, 의도적으로 아직 보류한 것인지 화면에서 바로 알 수 있다.
2. history / load / replay parity 확인
   - 쉽게 말하면: 저장된 실행을 다시 열 때 중요한 설정값이 빠지지 않는지 확인한다.
   - 왜 필요한가: 좋은 결과를 다시 재현하지 못하면 후보 검토 workflow가 흔들린다.
   - 기대 효과: Phase 29 후보 검토에서 "이 결과를 다시 만들 수 있나"를 더 신뢰할 수 있다.
3. Real-Money / Guardrail parity 범위 결정
   - 쉽게 말하면: annual strict에 있는 실전 검증 옵션을 quarterly나 ETF 전략에도 똑같이 붙일지, 다르게 둘지 결정한다.
   - 왜 필요한가: 모든 전략에 같은 UI를 억지로 붙이면 오히려 잘못된 해석을 만들 수 있다.
   - 기대 효과: strategy 성격에 맞는 검증 surface를 만들 수 있다.

## 이 문서에서 자주 쓰는 용어

- `Strategy Family`: Quality, Value, Quality + Value, GTAA, Global Relative Strength처럼 전략을 묶어 보는 단위다.
- `Cadence`: 재무제표나 리밸런싱이 어떤 주기로 움직이는지 말한다. 예: annual, quarterly, monthly.
- `Parity`: 모든 전략을 똑같이 만든다는 뜻이 아니라, 사용자가 헷갈리지 않을 정도로 지원 범위와 차이를 맞춘다는 뜻이다.
- `Capability Snapshot`: 전략별로 현재 지원되는 기능과 아직 검토 대상인 기능을 보여주는 요약 표다.
- `Replay Parity`: 저장된 실행이나 포트폴리오를 다시 열었을 때 원래 설정이 빠지지 않고 복원되는 상태다.

## 이번 phase의 운영 원칙

- 새 전략 발굴보다 family별 일관성 확인을 우선한다.
- 모든 전략에 같은 옵션을 강제로 붙이지 않는다.
- 기능이 없는 경우에는 "없음"으로 숨기지 말고 "아직 annual 중심", "Phase 28 검토 대상"처럼 이유를 설명한다.
- 사용자가 명시적으로 투자 분석을 요청하지 않는 한 성과 좋은 후보 찾기로 넘어가지 않는다.

## 이번 phase의 주요 작업 단위

1. Strategy Capability Snapshot 첫 구현
   - Single Strategy와 Compare 전략 박스 안에 capability 표를 추가한다.
   - annual strict, quarterly prototype, Global Relative Strength의 차이를 먼저 보이게 한다.
2. History / Load / Replay 보존 확인
   - strategy별 핵심 payload와 meta가 history, load-into-form, run-again에서 유지되는지 확인한다.
   - 특히 quarterly cadence와 GRS score 설정을 중점적으로 본다.
3. Data Trust Summary 확장 범위 결정
   - Phase 27의 Data Trust Summary를 compare / saved replay / ETF 전략군에서 어디까지 공통화할지 정한다.
4. Real-Money / Guardrail parity 결정
   - annual strict, quarterly prototype, ETF 전략의 실전 검증 surface 차이를 표준화한다.

## 다음에 확인할 것

- `Backtest > Single Strategy`에서 strategy를 바꿨을 때 `Strategy Capability Snapshot`이 보이는지
- `Backtest > Compare & Portfolio Builder`에서 선택된 전략 박스마다 capability 표가 보이는지
- annual strict와 quarterly prototype의 Real-Money / Guardrail 차이가 화면에서 이해되는지
- Phase 28 다음 작업을 history / replay parity 쪽으로 이어갈지 확인

## 한 줄 정리

Phase 28은 전략을 더 많이 만드는 phase가 아니라,
이미 있는 전략들이 같은 제품 안에서 헷갈리지 않게 보이고 다시 실행되도록 맞추는 phase다.
